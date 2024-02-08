from Mine.ViritallKeys.VkEnum import KeyData


class AbsStateMgr:
    _pressed_keys = set()

    @classmethod
    def get_pressed_keys(cls):
        return cls._pressed_keys

    @classmethod
    def press_keys(cls, *keys: KeyData):
        cls._pressed_keys += set(keys)

    @classmethod
    def un_press_keys(cls, *keys: KeyData):
        cls._pressed_keys -= set(keys)
