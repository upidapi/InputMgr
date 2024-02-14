import os

from Mine.OsAbstractions import AbsBackend

from Mine.OsAbstractions.Linux.EventApi import LinuxEventApi
from Mine.OsAbstractions.Linux.Keyboard import LinuxKeyboard
from Mine.OsAbstractions.Linux.Mouse import LinuxMouse


# avoid security on debug
if not __debug__:
    if os.geteuid() != 0:
        # this is due to that the following requires root:
        #   dumpkeys: a util for getting the keyboard layout
        #   taking global input
        #   (possibly) creating synthetic inputs
        raise Exception("you need root privileges to run this script")


class LinuxBackend(AbsBackend):
    EventApi = LinuxEventApi
    Mouse = LinuxMouse
    Keyboard = LinuxKeyboard
