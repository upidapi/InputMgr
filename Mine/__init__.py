from Mine.Main.EventStack import EventStack

from Mine.Main.Keyboard import Keyboard
from Mine.Main.Mouse import Mouse

from Events import MouseEvent, KeyboardEvent

from Mine.OsAbstractions.Linux.LinuxVk import LinuxKeyEnum


# separate into a class for typehints
class Vk:
    Linux = LinuxKeyEnum
