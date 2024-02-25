from src.AbsVkEnum import KeyData
from src.OsAbstractions.Windows.Base import KEYBDINPUT, MapVirtualKey, VkKeyScan


class WinKeyData(KeyData):
    def __init__(self, scan=None, flags=None, **kwargs):
        super().__init__(**kwargs)

        self.scan = scan
        self.flags = flags

    def parameters(self, is_press):
        """
        The parameters to pass to ``SendInput`` to generate this key.

        :param bool is_press: Whether to generate a press event.

        :return: all arguments to pass to ``SendInput`` for this key

        :rtype: dict

        :raise ValueError: if this key is a unicode character that cannot be
        represented by a single UTF-16 value
        """
        if self.vk:
            vk = self.vk
            scan = self.scan \
                or MapVirtualKey(vk, MapVirtualKey.MAPVK_VK_TO_VSC)
            flags = 0
        elif ord(self.char) > 0xFFFF:
            raise ValueError
        else:
            res = VkKeyScan(self.char)

            # can it be represented by a scancode?
            if (res >> 8) & 0xFF == 0:
                # send scancode
                vk = res & 0xFF
                scan = self.scan \
                    or MapVirtualKey(vk, MapVirtualKey.MAPVK_VK_TO_VSC)
                flags = 0

            else:
                # send unicode
                vk = 0
                scan = ord(self.char)
                flags = KEYBDINPUT.UNICODE

        state_flags = (
            KEYBDINPUT.KEYUP
            if not is_press else
            0
        )

        return dict(
            dwFlags=(self.flags or 0) | flags | state_flags,
            wVk=vk,
            wScan=scan
        )

    @classmethod
    def _from_ext(cls, vk, **kwargs):
        """Creates an extended key code.

        :param vk: The virtual key code.

        :param kwargs: Any other parameters to pass.

        :return: a key code
        """
        return cls.from_vk(vk, flags=KEYBDINPUT.EXTENDEDKEY, **kwargs)


