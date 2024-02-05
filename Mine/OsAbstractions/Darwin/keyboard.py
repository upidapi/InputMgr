from Mine.OsAbstractions.Abstract import AbsKeyboard
from Mine.ViritallKeys.VkEnum import KeyData


class DarwinKeyboard(AbsKeyboard):
    @staticmethod
    def press(vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @staticmethod
    def update_mapping() -> None:
        raise NotImplementedError

    @staticmethod
    def key_data_to_vk_code(key_data: KeyData) -> int:
        raise NotImplementedError
