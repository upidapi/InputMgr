from Mine.Main.EventStack import EventStack

from Mine.Main.Keyboard import Keyboard
from Mine.Main.Mouse import Mouse

from Events import MouseEvent, KeyboardEvent

from Mine.OsAbstractions.Linux.LinuxVk import LinuxKeyEnum


# we need to make the user explicitly select a vkEnum
# so that the ide can correctly infer the typehints
class Vk:
    Linux = LinuxKeyEnum
