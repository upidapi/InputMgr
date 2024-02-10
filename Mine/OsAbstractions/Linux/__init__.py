from Mine.OsAbstractions import AbsBackend

from Mine.OsAbstractions.Linux.EventApi import LinuxEventApi
from Mine.OsAbstractions.Linux.keyboard import LinuxKeyboard


class LinuxBackend(AbsBackend):
    event_api = LinuxEventApi
    mouse_controller = None
    keyboard_controller = LinuxKeyboard
