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
    def scroll(dx: float, dy: float):
        # might be int, int and not float, float
        raise NotImplementedError

    _buttons = Literal["left", "middle", "right", "forward", "back"]

    @staticmethod
    @abstractmethod
    def press_button(button: _buttons, down: bool):
        """
        on most os the mouse buttons are "just" keys,
        so you can press them with the keyboard class
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def is_pressed(button: _buttons):
        raise NotImplementedError
