from Mine.OsAbstractions import get_backend, get_backend_type
from Mine.ViritallKeys.VkEnum import KeyData

_keyboard = get_backend().keyboard_controller
_backend_type = get_backend_type()

class Keyboard:
    @staticmethod
    def press_key(cls, vk_code):


conv_from_types = int | str | KeyData


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


