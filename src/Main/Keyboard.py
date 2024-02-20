from src.AbsVkEnum import KeyData
from src.Main import TypeWriter
from src.OsAbstractions import get_backend, get_backend_type

_backend_type = get_backend_type()

_backend = get_backend()
_keyboard = _backend.Keyboard
_event_api = _backend.EventApi


class Keyboard:
    @classmethod
    def is_pressed(cls, key: KeyData):
        return _keyboard.key_pressed(key)

    typewrite = TypeWriter.typewrite

    # todo add helpers for keybindings
    #   binding them to functions
    #   recording keybindings

    # todo add a wait func
    #   waits for specific hotkey

    # todo add a record functionality
    #   record sequences
    #       record for n sec
    #       record until stop_record is called
    #       record n presses
    #   replay

    # todo add a reverse keycode presses to char
    #   so a unicode seq of presses
    #   (ctrl, shift, u, a, 2, 1, enter) => "\ua21"
    #   (shift, a) => "A"
    #   (¨, ¨) => "¨"
    #   (¨, " ") => "¨"

    # todo add a word listener
    #   listens for a word
    #   calls a callback when detected

    # todo add a word replacer
    #   listens for a word and replaces it with
    #   the determined word
