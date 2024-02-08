""" abstract representation for a keyboard """
from abc import ABC, abstractmethod

from Mine.ViritallKeys.VkEnum import KeyData


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


class AbsKeyboard(ABC):
    # @classmethod
    # @abstractmethod
    # def is_pressed(cls, vk_code: int) -> bool:
    #     raise NotImplementedError

    @classmethod
    @abstractmethod
    def queue_press(cls, vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def send_queued_presses(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def update_mapping(cls) -> None:
        """
        updates the internal keyboard key to vk_code mapping
        """
        raise NotImplementedError

    # @classmethod
    # @abstractmethod
    # def key_data_to_vk_code(cls, key_data: KeyData) -> int:
    #     """
    #     converts some data to a keycode e.g. "NP_0" to the keycode for numpad 0
    #     """
    #     raise NotImplementedError
    #
    # @classmethod
    # @abstractmethod
    # def key_to_vk_code(cls, key: str) -> int:
    #     """
    #     converts a key from the keyboard e.g. "a", "#", "^" to a keycode
    #     """
    #     raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_buttons_for_key(cls, key: KeyData)\
            -> (int, set[int], set[int]):
        """
        gets the buttons that needs to be pressed to get a specific KeyData

        if it has a "vk" it simply sends it

        otherwise it uses the "char" to find what modifiers
        and key that needs to be pressed

        :return: vk, setup, cleanup
        """

    @classmethod
    @abstractmethod
    def get_key_data_from_vk(cls, vk: int) -> KeyData:
        """
        converts a vk into a KeyData obj
        """

    @classmethod
    @abstractmethod
    def get_key_data_from_char(cls, char: str) -> KeyData:
        """
        converts a vk into a KeyData obj
        """
