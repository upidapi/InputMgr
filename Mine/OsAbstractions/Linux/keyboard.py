from Mine.OsAbstractions.Abstract import AbsKeyboard
from Mine.OsAbstractions.Linux.common import LinuxEventApi
from Mine.ViritallKeys.VkEnum import KeyData


class LinuxKeyboard(AbsKeyboard):
    @classmethod
    def is_pressed(cls, vk_code: int) -> bool:
        raise NotImplementedError

    @classmethod
    def press(cls, vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @classmethod
    def update_mapping(cls) -> None:
        """
        updates the internal keyboard key to vk_code mapping
        """
        raise NotImplementedError

    @classmethod
    def key_data_to_vk_code(cls, key_data: KeyData) -> int:
        """
        converts some data to a keycode e.g. "NP_0" to the keycode for numpad 0
        """
        raise NotImplementedError

    @classmethod
    def key_to_vk_code(cls, key_data: str) -> int:
        """
        converts a key from the keyboard e.g. "a", "#", "^" to a keycode
        """
        raise NotImplementedError
