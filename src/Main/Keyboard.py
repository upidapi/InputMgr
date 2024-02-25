from typing import Callable

from src.AbsVkEnum import KeyData
from src.Events import KeyboardEvent, any_event
from src.Main import TypeWriter
from src.Main.EventQueue import EventQueue, EventDistributor
from src.OsAbstractions import get_backend, get_backend_type

_backend_type = get_backend_type()

_backend = get_backend()
_keyboard = _backend.Keyboard
_event_api = _backend.EventApi
_mouse = _backend.Mouse


class Hotkey:
    def __init__(
            self,
            press,
            along_with: set[int] = None,
            exclusive: bool = True,
            ignore_mouse: bool = True
    ):
        self.press: int = press
        self.along_with: set[int] = along_with or set()
        self.exclusive: bool = exclusive
        self.ignore_mouse: bool = ignore_mouse

    def __hash__(self):
        return hash((
            self.press,
            sorted(list(self.along_with)),
            self.exclusive,
            self.ignore_mouse
        ))


class Keyboard:
    @classmethod
    def is_pressed(cls, *keys: KeyData):
        return all(
            _keyboard.key_pressed(key.vk)
            for key in keys
        )

    typewrite = TypeWriter.typewrite

    @staticmethod
    async def wait_for_text_typed(text):
        """
        waits for a specific string to be typed (for example aaAAaa33)
        and return when that happens
        """
        cur_progress = 0

        with EventQueue() as eq:
            async for event in eq:

                if not isinstance(event, KeyboardEvent.KeySend):
                    continue

                for char in event.chars:
                    if text[cur_progress] != char:
                        cur_progress = 0
                        continue

                    cur_progress += 1

                    if cur_progress == len(text):
                        return

    # # {(func, text): progress}
    # _text_type_binds: dict = {}
    #
    # @classmethod
    # def _listening_for_text_callback(cls, event: any_event):
    #     if not isinstance(event, KeyboardEvent.KeySend):
    #         return
    #
    #     for char in event.chars:
    #         for (func, text), progress in cls._text_type_binds.items():
    #             if text[progress] != char:
    #                 progress = 0
    #             else:
    #                 progress += 1
    #
    #                 if progress == len(text):
    #                     func()
    #                     progress = 0
    #
    #             cls._text_type_binds[(func, text)] = progress
    #
    # @classmethod
    # def bind_to_text_typed(cls, func, text):
    #     cls._text_type_binds[(func, text)] = 0
    #     if len(cls._text_type_binds) == 1:
    #         EventDistributor.add_callback(
    #             cls._listening_for_text_callback
    #         )
    #
    # @classmethod
    # def un_bind_to_text_typed(cls, func, text):
    #     try:
    #         del cls._text_type_binds[(func, text)]
    #     except KeyError:
    #         raise TypeError("there is no func bound to that text")
    #
    #     if len(cls._text_type_binds) == 0:
    #         EventDistributor.remove_callback(
    #             cls._listening_for_text_callback
    #         )
    #
    # # text: func
    # idk = {}
    #
    # @classmethod
    # def add_text_replace(cls, text, replacement):
    #     def wrapper():
    #         cls.typewrite("\b" * len(text) + replacement)
    #
    #     cls.idk[text] = wrapper
    #     cls.bind_to_text_typed(wrapper, text)
    #
    # @classmethod
    # def remove_text_replace(cls, text):
    #     wrapper = cls.idk[text]
    #     cls.un_bind_to_text_typed(wrapper, text)

    # {text: (replace, progress)}
    _text_type_binds: dict = {}

    @classmethod
    def _listening_for_text_callback(cls, event: any_event):
        if not isinstance(event, KeyboardEvent.KeySend):
            return

        for char in event.chars:
            to_replace = []

            for text, (replace, progress) in cls._text_type_binds.items():
                if text[progress] != char:
                    progress = 0
                else:
                    progress += 1

                    if progress == len(text):
                        to_replace.append((text, replace))

                cls._text_type_binds[text] = (replace, progress)

            if to_replace:
                text, replace = min(to_replace, key=lambda x: len(x[0]))
                cls.typewrite("\b" * len(text) + replace)

                for text, (replace, progress) in cls._text_type_binds.items():
                    cls._text_type_binds[text] = (replace, 0)

    @classmethod
    def add_text_replacement(cls, text, replacement):
        if cls._text_type_binds[text]:
            raise TypeError(f"a replacement already exist for \"{text}\"")

        cls._text_type_binds[text] = (replacement, 0)
        if len(cls._text_type_binds) == 1:
            EventDistributor.add_callback(
                cls._listening_for_text_callback
            )

    @classmethod
    def remove_text_replacement(cls, text):
        try:
            del cls._text_type_binds[text]
        except KeyError:
            raise TypeError("there is no func bound to that text")

        if len(cls._text_type_binds) == 0:
            EventDistributor.remove_callback(
                cls._listening_for_text_callback
            )

    @staticmethod
    async def wait_for_hotkey(hotkey: Hotkey):
        with EventQueue() as eq:
            async for event in eq:
                if not isinstance(event, KeyboardEvent.KeyDown):
                    continue

                if event.vk != hotkey.press:
                    continue

                pressed = _keyboard.get_pressed_keys()
                if hotkey.ignore_mouse:
                    pressed -= _mouse.button_vks

                if hotkey.exclusive:
                    if pressed == hotkey.along_with:
                        break
                elif pressed.issuperset(hotkey.along_with):
                    break

    _hotkey_binds = {}

    @classmethod
    def bind_to_hotkey(
            cls,
            func: Callable[[], None],
            hotkey: Hotkey,
    ):
        def wrapper(event):
            if not isinstance(event, KeyboardEvent.KeyDown):
                return

            if event.vk != hotkey.press:
                return

            pressed = _keyboard.get_pressed_keys()
            if hotkey.ignore_mouse:
                pressed -= _mouse.button_vks

            if hotkey.exclusive:
                if pressed == hotkey.along_with:
                    func()
            elif pressed.issuperset(hotkey.along_with):
                func()

        cls._hotkey_binds[(func, hotkey)] = wrapper
        EventDistributor.add_callback(wrapper)

    @classmethod
    def unbind_hotkey(
            cls,
            func: Callable[[], None],
            hotkey: Hotkey,
    ):
        try:
            wrapper = cls._hotkey_binds[(func, hotkey)]
        except KeyError:
            raise TypeError("no func bound to said hotkey")

        EventDistributor.remove_callback(wrapper)
