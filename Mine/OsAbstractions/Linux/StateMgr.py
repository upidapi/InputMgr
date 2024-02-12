import evdev

from Mine.OsAbstractions.Abstract.Keyboard import InvalidKeyException
from Mine.OsAbstractions.Abstract.StateMgr import AbsStateMgr
from Mine.OsAbstractions.Linux.common import LinuxKeyData, LinuxLayout, LinuxKeyEnum


class LinuxStateMgr(AbsStateMgr):
    MODIFIER_MAP: dict[LinuxKeyData, LinuxKeyData] = {
        LinuxKeyEnum.alt: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_l: LinuxKeyEnum.alt,
        # todo this is probably wrong
        #   not the comment out but the original
        # LinuxKeyEnum.alt_r: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_gr: LinuxKeyEnum.alt_gr,
        LinuxKeyEnum.shift: LinuxKeyEnum.shift,
        LinuxKeyEnum.shift_l: LinuxKeyEnum.shift,
        LinuxKeyEnum.shift_r: LinuxKeyEnum.shift,
        # todo add more modifiers
        LinuxKeyEnum.ctrl: LinuxKeyEnum.ctrl,
    }
