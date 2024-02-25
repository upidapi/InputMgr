from src.Events import KeyboardEvents, MouseEvents, any_event

from src.Main.EventPrinting import print_event, print_events
from src.Main.EventQueue import EventQueue, EventDistributor
from src.Main.Keyboard import Keyboard, Hotkey
from src.Main.Mouse import Mouse
from src.Main.Recorder import Recorder

from src.OsAbstractions.Linux.LinuxVk import LinuxKeyEnum


# we need to make the user explicitly select a vkEnum
# so that the ide can correctly infer the typehints
class Vk:
    Linux = LinuxKeyEnum
