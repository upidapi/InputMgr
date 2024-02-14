from Mine.AbsVkEnum import KeyData
from Mine.OsAbstractions.Abstract import AbsKeyboard


class WindowsKeyboard(AbsKeyboard):
    @staticmethod
    def press(vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @classmethod
    def update_mapping(cls) -> None:
        raise NotImplementedError

    @staticmethod
    def key_data_to_vk_code(key_data: KeyData) -> int:
        raise NotImplementedError
