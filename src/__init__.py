from src.Main.EventHandler import EventQueue

from src.Main.Mouse import Mouse

from src.Events import MouseEvent, KeyboardEvent

from src.OsAbstractions.Linux.LinuxVk import LinuxKeyEnum


# we need to make the user explicitly select a vkEnum
# so that the ide can correctly infer the typehints
class Vk:
    Linux = LinuxKeyEnum
