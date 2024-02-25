import unicodedata
from typing import Self

from src.AbsVkEnum import KeyData
from src.OsAbstractions.Linux.LinuxVk.xorg_keysyms import is_dead


class LinuxKeyData(KeyData):
    def __init__(self, x_name=None, caps_lock_able=False, **kwargs):
        super().__init__(**kwargs)

        # x_name is the name dumpkeys has for a key
        self.x_name = x_name

        # todo take the caps lock into account
        # flag for if the key is affected by caps lock
        self.caps_lock_able = caps_lock_able

        self.is_dead = self._calc_is_dead()

    def _calc_is_dead(self):
        try:
            return is_dead(self.char)
        except KeyError:
            return False
