from src.AbsVkEnum import KeyData
from src.OsAbstractions.Linux.LinuxVk.xorg_keysyms import is_dead


class LinuxKeyData(KeyData):
    def __init__(self, x_name=None, **kwargs):
        super().__init__(**kwargs)

        # x_name is the name dumpkeys has for a key
        self.x_name = x_name

    def _calc_is_dead(self):
        try:
            return is_dead(self.char)
        except KeyError:
            return False
