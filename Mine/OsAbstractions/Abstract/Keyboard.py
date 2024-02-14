""" abstract representation for a keyboard """
from abc import ABC, abstractmethod
from typing import Self

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


base_conv_from_types = int | str | KeyData


# exposed to the user
class Up:
    def __init__(self, *data: base_conv_from_types):
        self.data = data


class Down:
    def __init__(self, *data: base_conv_from_types):
        self.data = data


class StateData:
    def __init__(
            self,
            do: tuple[base_conv_from_types | Up | Down | Self, ...],
            need_pressed: set[int] = None,
            need_unpressed: set[int] = None
    ):
        # note:
        # if a keys is in both need_pressed and need_unpressed
        # then it's guaranteed to have been released before pressed

        self.do = do
        self.need_pressed = need_pressed or set()
        self.need_unpressed = need_unpressed or set()


class AbsKeyboard(ABC):
    @classmethod
    @abstractmethod
    def get_pressed_keys(cls) -> set[KeyData]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def key_pressed(cls, key: KeyData) -> bool:
        raise NotImplementedError

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

    # todo handle unicode keys
    @classmethod
    @abstractmethod
    def calc_buttons_for_char(cls, char: str) -> StateData:
        """
        gets the buttons that needs to be pressed to get a specific KeyData

        sometimes multiple buttons are needed
            e.g. dead chars
            unicode chars

        returns in the following format
            a tuple of data_tuples where each data_tuple is one button press
            the data_tuple is in the form of (vk, setup, cleanup)

        :return: ((vk, setup, cleanup), ...)
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

    @classmethod
    @abstractmethod
    def get_vk_from_key_data(cls, key_data: KeyData) -> int:
        """
        converts a vk into a KeyData obj
        """

    # @classmethod
    # @abstractmethod
    # def get_char_from_key_data(cls, key_data: KeyData) -> str:
    #     """
    #     converts a vk into a KeyData obj
    #     """
