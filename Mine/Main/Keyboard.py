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


class Pressed:
    def __init__(self, pressed: (base_conv_from_types,), do: base_conv_from_types | Up | Down):
        self.pressed = pressed
        self.do = do


all_conv_from_types = base_conv_from_types | Up | Down | Pressed


class Keyboard:
    @classmethod
    def _dispatch_block(cls, vk: int, press: bool):
        event_class = KeyboardEvent.KeyDown if press else KeyboardEvent.KeyUp

        # btw blocking a KeyData blocks that button,
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
        """
        prevents excessive (and unnecessary) modifier presses
        so
            _minify_press_seq(
                _Down(5), 10, _Up(5), _Down(5), 12, _Up(5), _Down(5), 11, _Up(5)
            ) == (_Down(5), 10, 12, 11, _Up(5))

        if a _Up or _Down instance is marked as no_optimise
            then it won't be collapsed
        """
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
    def _to_press_seq(cls, *inp: all_conv_from_types) -> press_seq_type:
        out = []

        for part in inp:
            if isinstance(part, KeyData):
                out.append(part)
            elif isinstance(part, str):
                out += [
                    _keyboard.get_key_data_from_char(char)
                    for char in part
                ]
            elif isinstance(part, int):
                out.append(
                    _keyboard.get_key_data_from_vk(
                        part
                    )
                )
            elif isinstance(part, Pressed):
                out += cls._to_press_seq(Down(part.pressed))
                out.append(cls._to_press_seq(part.do))
                out += cls._to_press_seq(Up(part.pressed[::-1]))

            elif isinstance(part, Up):
                for data in part.data:
                    out += [
                        _Up(instruction, no_optimise=True)
                        if isinstance(instruction, int) else instruction
                        for instruction in cls._to_press_seq(data)
                    ]
            elif isinstance(part, Down):
                for data in part.data:
                    out += [
                        _Down(instruction, no_optimise=True)
                        if isinstance(instruction, int) else instruction
                        for instruction in cls._to_press_seq(data)
                    ]

        return tuple(out)

    # todo handle dead keys

    @classmethod
    def _remove_modifiers(cls, *inp: all_conv_from_types) -> press_seq_type:
        """
        converts all "all_conv_from_types" so that all str and
        KeyData become just int (vks)
        """

        out = []

        for part in inp:
            if isinstance(part, int):
                out.append(part)

            if isinstance(part, str):
                out += [
                    _keyboard.get_vk_from_key_data(
                        _keyboard.get_key_data_from_char(
                            char
                        ))
                    for char in part
                ]

            if isinstance(part, KeyData):
                out += [
                    _keyboard.get_vk_from_key_data(
                        part
                    )
                ]

            elif isinstance(part, Up):
                return Up(
                    cls._remove_modifiers(
                        *part.data
                    )
                )

            elif isinstance(part, Down):
                return Up(
                    cls._remove_modifiers(
                        *part.data
                    )
                )

            elif isinstance(part, Pressed):
                out += cls._remove_modifiers(Down(part.pressed))
                out.append(cls._remove_modifiers(part.do))
                out += cls._remove_modifiers(Up(part.pressed[::-1]))

        return out

    @classmethod
    def type(cls, *inp: all_conv_from_types):
        """
        types a sequence of things

        for each part in inp
            the following are cases for the type of the part

        int (vk):
            press and un pres said button (vk)

        str (text)
            press buttons in a way that archives the desired text

        KeyData
            if it has .char type that (see "str")
            if it has .vk type that (see "int")

        Up / Down
            if the inside is a vk
                then simply press/un press that vk

            if the inside is a char
                 then all modifiers are correctly pressed and cleaned up
                 but the actual vk that corresponds to the char
                    is simply pressed/un pressed

            Note:
                the char that is "permanently" pressed/unpressed
                is not taken into consideration when calculating the
                keys required to be pressed/unpressed to get a specific char

                i.e.
                type(Down(Vk.shift), "a") => "A"

        Pressed(pressed, do)
            executes {do}
            while the keys in {pressed} are pressed
            afterward un presses those keys

            Note:
                if Up(a) is used inside {do}
                and {pressed} has {a} in it
                then {a} will be unpressed in the cleanup

                i.e.
                if Up(a) in {do}
                and {a} in {pressed}
                then {a} will be unpressed when "Pressed" finished
        """
        press_seq = cls._key_data_to_press_seq(*inp)
        optimised_press_seq = cls._minify_press_seq(press_seq)
        cls._exec_press_seq(optimised_press_seq)

    @classmethod
    def type_literal_keys(cls, *inp: all_conv_from_types):
        """
        types the vk(s) directly corresponding to the input

        so it totally ignores state
            type_literal_keys("A") == type_literal_keys("a")
            # on the nordic layout
            type_literal_keys("3") == type_literal_keys("#") == type_literal_keys("£")

        it also won't fix the state for a specific char so:
            type_literal_keys("a") might come out as "A", if shift is pressed
        """

        literal_inp = cls._remove_modifiers(*inp)
        cls.type(literal_inp)
