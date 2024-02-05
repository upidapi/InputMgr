""" abstract representation for a keyboard """

from abc import ABC, abstractmethod

from Mine.ViritallKeys.VkEnum import KeyData


class AbsKeyboard(ABC):
    @staticmethod
    @abstractmethod
    def press(vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def update_mapping() -> None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def key_data_to_vk_code(key_data: KeyData) -> int:
        raise NotImplementedError
