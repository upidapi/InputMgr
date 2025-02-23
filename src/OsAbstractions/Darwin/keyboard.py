from src.AbsVkEnum import KeyData
from src.OsAbstractions.Abstract import AbsKeyboard


class DarwinKeyboard(AbsKeyboard):
    @staticmethod
    def press(vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @classmethod
    def update_mapping(cls) -> None:
        raise NotImplementedError

    @staticmethod
    def key_data_to_vk_code(key_data: KeyData) -> int:
        raise NotImplementedError
