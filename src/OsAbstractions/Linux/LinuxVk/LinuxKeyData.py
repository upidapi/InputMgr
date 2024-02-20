from src.AbsVkEnum import KeyData
from src.OsAbstractions.Linux.LinuxVk.xorg_keysyms import unicode_char_to_name, name_to_symbolic_key


class LinuxKeyData(KeyData):
    def __init__(self, x_name=None, **kwargs):
        super().__init__(**kwargs)

        # x_name is the name dumpkeys has for a key
        self.x_name = x_name

    def _calc_is_dead(self):
        try:
            name = unicode_char_to_name(self.combining)
            symbolic_key = name_to_symbolic_key(name)

            if symbolic_key:
                return True
            else:
                return False
        except KeyError:
            pass
