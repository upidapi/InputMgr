""" abstract representation for a keyboard """

from abc import ABC, abstractmethod

from Mine.ViritallKeys.VkEnum import KeyData


class AbsKeyboard(ABC):
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

    @staticmethod
    @abstractmethod
    def button_up(vk_code: int):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def button_down(vk_code: int):
        raise NotImplementedError
