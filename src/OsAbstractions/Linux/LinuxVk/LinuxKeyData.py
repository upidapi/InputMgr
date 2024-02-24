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

    def join(self, key: Self):
        """
        joins self (a dead char)
        with another

        self: dead char
        self: dead char or normal char

        join(^, a) => â
        join(^, ^) => ^
        join(^, " ") => ^
        join(a, a) => ValueError("cant put normal char on another")
        join(a, ^) => ValueError("cant put normal char on another")
        """
        if not self.is_dead:
            ValueError("cant put normal char on char")

        if self.char is None:
            ValueError("self needs to have a char to combine")

        if key.char is None:
            ValueError("key needs to have a char to combine")

        if key.char in (self.char, " "):
            # combine with self or space returns the non-dead
            # version of it

            return self.get_resulting_char()

        combined = unicodedata.normalize(
            "NFC",
            self.char + key.char
        )

        if len(combined) != len(self.char) + len(key.char):
            # chars combined, return the combined version
            return combined

        # if they don't successfully combine,
        # then they combine to make nothing
        return ""
