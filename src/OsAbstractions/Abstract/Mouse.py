""" abstract representation for a keyboard """

from abc import ABC, abstractmethod
from typing import Literal


class AbsMouse(ABC):
    @staticmethod
    @abstractmethod
    def set_pos(x: int, y: int):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_pos() -> (int, int):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def scroll(dx: int, dy: int):
        raise NotImplementedError

    buttons = Literal["left", "middle", "right"]

    @staticmethod
    @abstractmethod
    def press_button(button: buttons, down: bool):
        """
        on most os the mouse buttons are "just" keys,
        so you can press them with the keyboard class
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def is_pressed(button: buttons):
        raise NotImplementedError
