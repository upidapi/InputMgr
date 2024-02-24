""" abstract representation for a keyboard """
from abc import ABC, abstractmethod
from typing import Self

from src.AbsVkEnum import KeyData


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
    """
    Note: this is evaluated lazily so only the key
    that are explicitly mentioned to be needed are
    actually pressed and unpressed

    StateData((1), {2}, {})
    StateData((1), {}, {})
    =>
    Down(2), 1, 1, Up(2),

    setting the need_pressed and need_unpressed doesn't
    guarantee that the key is pressed without anything elseasdlasöidjflkasjdflökasjdflökjasdölfkjasöldkfjalöskdjfölkasjdfölkasjdölfkjaöslkjdfasfldkö
    """
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


class LiteralVk:
    """
    converts everything into just the vk part

    types the vk(s) directly corresponding to the input

    so it totally ignores state
        LiteralVk("A") == LiteralVk("a")
        # on the nordic layout
        LiteralVk("3") == LiteralVk("#") == LiteralVk("£")

    it also won't fix the state for a specific char so:
        LiteralVk("a") might come out as "A", if shift is pressed

    """

    def __init__(self, *data: base_conv_from_types):
        self.data = data


all_conv_from_types = base_conv_from_types | Up | Down | StateData | LiteralVk


class AbsKeyboard(ABC):
    @classmethod
    @abstractmethod
    def get_pressed_keys(cls) -> set[int]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def key_pressed(cls, key: int) -> bool:
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

    @classmethod
    def clear_key_press_buffer(cls):
        """
        resets the saved press state

        so if you've pressed calc_resulting_chars_for_button("¨") and call this
        if you then press calc_resulting_chars_for_button("¨") again nothing happens
        you have to press it another time for it to become "¨¨" (windows)
        """

    @classmethod
    def calc_resulting_chars_for_button(
            cls,
            key_data: KeyData,
    ) -> str:
        """
        Calcs the resulting char for a button.
        A char might be a combination of several presses and held
        down buttons.

        button presses are possibly buffered if they affect the following
        pressed

        for example
        "¨" doesn't result in a character but changes the following one
        "¨" + "¨" => "¨"  (linux)
        "¨" + "o" => "ö"  (linux)

        one press can result in multiple characters like
        "¨" + "¨" => "¨¨"  (windows)

        this works using the KeySend events
        """
