import time
from typing import Literal, Tuple

import evdev

from Mine.Events import KeyboardEvent
from Mine.OsAbstractions import get_backend, get_backend_type
from Mine.ViritallKeys.VkEnum import KeyData

_backend_type = get_backend_type()

_backend = get_backend()
_keyboard = _backend.keyboard_controller
_event_api = _backend.event_api
_state_mgr = _backend.state_mgr


ASSUME_NO_STATE_CHANGE = False


# todo make the program actually respect the no_optimise flag
#   if it has it then that event needs to happen
#   probably implement by checking if it's a click or if it has
#   the no_optimise flag in _minify_press_seq
class _Up:
    def __init__(self, *vks: int, no_optimise=False):
        self.vks = set(vks)
        self.no_optimise = no_optimise


class _Down:
    def __init__(self, *vks: int, no_optimise=False):
        self.vks = set(vk for vk in vks)
        self.no_optimise = no_optimise


press_seq_type: [_Up, _Down, int]
base_conv_from_types = int | str | KeyData


# exposed to the user
class Up:
    def __init__(self, *data: base_conv_from_types):
        self.data = data


class Down:
    def __init__(self, *data: base_conv_from_types):
        self.data = data


# todo make this both take a list of keys that have to be active
#   and a action to do while that is true
class Pressed:
    def __init__(self, pressed: (base_conv_from_types, ), do: base_conv_from_types | Up | Down):
        self.pressed = pressed
        self.do = do


all_conv_from_types = base_conv_from_types | Up | Down | Pressed


class Keyboard:
    @classmethod
    def _dispatch_block(cls, vk: int, press: bool):
        event_class = KeyboardEvent.KeyDown if press else KeyboardEvent.KeyUp

        # btw blocking a KeyData blocks that button
        # so we actually get all data we need
        key = KeyData.from_vk(vk)

        _event_api.dispatch_event_block(
            event_class(
                time.time_ns() / 10 ** 6,
                "synthetic event",
                key,
            )
        )

    @classmethod
    def _queue_vk_press(cls, vk: int, down: bool):
        cls._dispatch_block(vk, down)
        _keyboard.queue_press(vk, down)

    @classmethod
    def _get_seq_class(cls, down):
        return _Down if down else _Up

    @classmethod
    def _buttons_for_key(cls, key: KeyData):
        pressed_keys = _state_mgr.get_pressed_keys()
        vk, need_pressed, need_unpressed = _keyboard.calc_buttons_for_key(key)

        # assume that no events are sent between now and the last
        # event fetch
        # if an event did occur then there's a chance that the
        # mod key state changed which could lead to incorrect chars
        # being pressed
        if ASSUME_NO_STATE_CHANGE:
            to_press = need_pressed - pressed_keys
            to_un_press = pressed_keys | need_unpressed
        else:
            to_press = need_pressed
            to_un_press = need_unpressed

        setup: set[(int, bool)] = set(
            (key, True)
            for key in to_press
        ) | set(
            (key, False)
            for key in to_un_press
        )

        cleanup: set[(int, bool)] = set(
            (key_vk, not pressed) for key_vk, pressed in setup
        )

        return setup, vk, cleanup

    @classmethod
    def _key_data_to_press_seq(cls, key: KeyData):
        setup, vk, cleanup = cls._buttons_for_key(key)

        out: [_Up, _Down, int] = []
        for vk, press in setup:
            # this could theoretically block the wrong event since
            # we only get the vk
            out.append(
                cls._get_seq_class(press)(vk)
            )

        out.append(vk)

        for vk, press in setup:
            out.append(
                cls._get_seq_class(press)(vk)
            )

        return tuple(out)

    @classmethod
    def _exec_press_seq(cls, press_seq: press_seq_type):
        for thing in press_seq:
            if isinstance(thing, int):
                cls._queue_vk_press(thing, True)
                cls._queue_vk_press(thing, False)

            elif isinstance(thing, _Down):
                for vk in thing.vks:
                    cls._queue_vk_press(vk, True)

            elif isinstance(thing, _Up):
                for vk in thing.vks:
                    cls._queue_vk_press(vk, False)

            else:
                raise TypeError(f"invalid press seq type {thing}")

        _keyboard.send_queued_presses()

    @classmethod
    def _minify_press_seq(
            cls,
            press_seq: press_seq_type
    ) -> press_seq_type:
        down = set()
        up = set()

        # full_seq = [j for i in press_seq for j in i]

        out = []
        for thing in press_seq:
            if isinstance(thing, int) or \
                    isinstance(thing, _Down | _Up) and thing.no_optimise:
                out += _Down(*(down - up))
                out += _Up(*(up - down))

                out.append(thing)
                # if isinstance(thing, int):
                # elif isinstance(thing, _Down):
                #     out.append(_Down)

                down = set()
                up = set()

            elif isinstance(thing, _Down):
                down += thing.vks

            elif isinstance(thing, _Up):
                up += thing.vks

            else:
                raise TypeError(f"invalid press seq type {thing:=} {press_seq:=}")

        out += _Down(*down)
        out += _Up(*up)

        return out

    @classmethod
    def _to_press_seq(cls, *inp: all_conv_from_types) -> (press_seq_type, ):
        # todo handle (Up | Down)(str)
        out = []

        for x in inp:
            if isinstance(x, KeyData):
                out.append(x)
            elif isinstance(x, str):
                out += [
                    _keyboard.get_key_data_from_char(char)
                    for char in x
                ]
            elif isinstance(x, int):
                out.append(
                    _keyboard.get_key_data_from_vk(
                        x
                    )
                )
            elif isinstance(x, Pressed):
                out += cls._to_press_seq(Down(x.pressed))
                out.append(cls._to_press_seq(x.do))
                out += cls._to_press_seq(Up(x.pressed[::-1]))

            elif isinstance(x, Up):
                out += [
                    _Up(cls._to_press_seq(data), no_optimise=True)
                    for data in x.data
                ]
            elif isinstance(x, Down):
                out += [
                    _Down(cls._to_press_seq(data), no_optimise=True)
                    for data in x.data
                ]

        return tuple(out)

    @classmethod
    def type(cls, *inp: all_conv_from_types):
        """
        types a sequence of things

        int (vk):
            press and un pres said button (vk)

        str (text)
            press buttons in a way that archives the desired text

        """
        press_seq = cls._key_data_to_press_seq(*inp)
        optimised_press_seq = cls._minify_press_seq(press_seq)
        cls._exec_press_seq(optimised_press_seq)
