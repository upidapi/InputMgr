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


class Up:
    def __init__(self, *vks: int):
        self.vks = set(vks)


class Down:
    def __init__(self, *vks: int):
        self.vks = set(vks)


press_seq_type: [Up, Down, int]


class Keyboard:
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
    def get_seq_class(cls, down):
        return Down if down else Up

    @classmethod
    def _to_press_seq(cls, key: KeyData, no_cleanup: bool = False):
        setup, vk, cleanup = cls._buttons_for_key(key)

        out: [Up, Down, int] = []
        for vk, press in setup:
            # this could theoretically block the wrong event since
            # we only get the vk
            out.append(
                cls.get_seq_class(press)(vk)
            )

        out.append(vk)

        if not no_cleanup:
            for vk, press in setup:
                out.append(
                    cls.get_seq_class(press)(vk)
                )

        return out


    @classmethod
    def _minify_press_seq(
            cls,
            press_seq: press_seq_type
    ):
        down = set()
        up = set()

        # full_seq = [j for i in press_seq for j in i]

        out = []
        for thing in press_seq:
            if isinstance(thing, int):
                out += Down(*(down - up))
                out += Up(*(up - down))

                down = set()
                up = set()

            elif isinstance(thing, Down):
                down += thing.vks

            elif isinstance(thing, Up):
                up += thing.vks

            else:
                raise TypeError(f"invalid press seq type {thing:=} {press_seq:=}")

        out += Down(*down)
        out += Up(*up)

        return out

    @classmethod
    def _exec_press_seq(cls, press_seq: press_seq_type):
        for thing in press_seq:
            if isinstance(thing, int):
                cls._queue_vk_press(thing, True)
                cls._queue_vk_press(thing, False)

            elif isinstance(thing, Down):
                for vk in thing.vks:
                    cls._queue_vk_press(vk, True)

            elif isinstance(thing, Up):
                for vk in thing.vks:
                    cls._queue_vk_press(vk, False)

            else:
                raise TypeError(f"invalid press seq type {thing}")

        _keyboard.send_queued_presses()

    conv_from_types = int | str | KeyData

    @classmethod
    def _to_key_data(cls, *inp: conv_from_types | (conv_from_types, ))\
            -> (KeyData | (KeyData, )):
        return (
            {cls._to_key_data(y) for y in x}  # preserve the set struct
            if isinstance(x, tuple) else
            cls._to_key_data(x)  # convert
            for x in inp
        )

    @classmethod
    def type(cls, *inp: conv_from_types | {conv_from_types}):


def _to_vk(inp: conv_from_types):
    # already a vk
    if isinstance(inp, int):
        return inp

    # convert keyboard keys to vk
    if isinstance(inp, str):
        return tuple(
            _keyboard.key_to_vk_code(char)
            for char in inp
        )

    # convert vk_data to vk
    # e.g. the thing in the enums
    if isinstance(inp, KeyData):
        if inp.os != _backend_type:
            raise TypeError(
                f"you can't use a vk from \"{inp.os}\" on your \"{_backend_type}\" system"
            )

        return _keyboard.key_data_to_vk_code(
            inp
        )


"""
"abc" => (a_code, b_code, c_code)
"ab", "cd" => (a_code, b_code, c_code, d_code)
{"abc"} => ({a_code, b_code, c_code})

KeyData("ESC") => [esc_code]

[
"""
def to_vk(*inp: conv_from_types | {conv_from_types}) -> [int | {int}]:
    # sets are assumed to be pressed together
    # tuples in order
    return [
        {_to_vk(y) for y in x}  # preserve the set struct
        if isinstance(x, set) else
        _to_vk(x)  # convert
        for x in inp
    ]


class Pressing:
    """
    usage:

    executes the code while pressing the keys

    with pressing("ab"):
        # code
    """

    def __init__(self, *keys: conv_from_types | {conv_from_types}):
        self._keys = keys

    def __enter__(self):
        pass


def _press_vk(down: bool, vk):
    inputs = INPUT(type=INPUT_KEYBOARD, value=INPUTUNION(ki=KEYBDINPUT(
        wVk=vk,
        wScan=0,
        dwFlags=KEY_DOWN_EVENT if down else KEY_UP_EVENT,
        time=0,
        dwExtraInfo=None
    )))
    ctypes.windll.user32.SendInput(1, ctypes.byref(inputs), ctypes.sizeof(inputs))

def _press_vks(down: bool, *vk: int | str):
    vks = compile_to_vks(*vk)
    for vk in vks:
        _press_vk(down, vk)

def press_keys(*vk: int | str):
    _press_vks(True, *vk)

def un_press_keys(*vk: int | str):
    _press_vks(False, *vk)

def click_keys(*vk: int | str):
    """
    clicks a list of keys in order before un-clicking al of them in the reverse

    @example
    # send an "a" with the "shift" and "alt" keys pressed

    click_keys("+!a")
    """
    # possibly start by un-pressing the key
    press_keys(True, *vk)
    un_press_keys(False, *vk[::-1])

def typewrite_keys(*vk: int | str):
    """
    clicks the keys, one by one

    @example
    # typewrite "hello"

    typewrite_keys("hello")
    """
    vks = compile_to_vks(*vk)
    for vk in vks:
        _press_vk(True, vk)
        _press_vk(False, vk)


