""" abstract representation for a keyboard """

from abc import ABC, abstractmethod

from Mine.ViritallKeys.VkEnum import KeyData


class AbsKeyboard(ABC):
    class InvalidKeyException(Exception):
        """The exception raised when an invalid ``key`` parameter is passed to
        :meth:`AbsKeyboard.press`

        Its first argument is the ``key`` parameter.
        """
        pass

    class InvalidCharacterException(Exception):
        """The exception raised when an invalid character is encountered in
        the string passed to :meth:`Controller.key_data_to_vk_code`.

        Its first argument is the index of the character in the string, and the
        second the character.
        """
        pass

    @classmethod
    @abstractmethod
    def is_pressed(cls, vk_code: int) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def press(cls, vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def update_mapping(cls) -> None:
        """
        updates the internal keyboard key to vk_code mapping
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def key_data_to_vk_code(cls, key_data: KeyData) -> int:
        """
        converts some data to a keycode e.g. "NP_0" to the keycode for numpad 0
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def key_to_vk_code(cls, key: str) -> int:
        """
        converts a key from the keyboard e.g. "a", "#", "^" to a keycode
        """
        raise NotImplementedError
