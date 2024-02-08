import evdev

from Mine.OsAbstractions.Abstract.Keyboard import InvalidKeyException
from Mine.OsAbstractions.Abstract.StateMgr import AbsStateMgr
from Mine.OsAbstractions.Linux.common import LinuxKeyData, LinuxLayout, LinuxKeyEnum


class StateMgr(AbsStateMgr):
    MODIFIER_MAP: dict[LinuxKeyData, LinuxKeyData] = {
        LinuxKeyEnum.alt.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_l.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_r.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_gr.vk: LinuxKeyEnum.alt_gr,
        LinuxKeyEnum.shift.vk: LinuxKeyEnum.shift,
        LinuxKeyEnum.shift_l.vk: LinuxKeyEnum.shift,
        LinuxKeyEnum.shift_r.vk: LinuxKeyEnum.shift
    }
