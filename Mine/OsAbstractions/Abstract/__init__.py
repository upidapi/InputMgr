import platform as _platform
from typing import Type

from Mine.OsAbstractions.Abstract.Events.AbsEventStack import AbsEventStack


class Backend:
    def __init__(
            self,
            event_stack,
            mouse_controller,
            keyboard_controller
    ):
        self.event_stack: Type[AbsEventStack] = event_stack
        self.mouse_controller = mouse_controller
        self.keyboard_controller = keyboard_controller


def get_backend():
    _system = _platform.system()
    if _system == 'Windows':
        from Windows.mouse import WindowsMouse as Mouse
        from Windows.keyboard import WindowsKeyboard as Keyboard
        from Windows.vk import WindowsVk as Vk

    elif _system == 'Linux':
        from Linux.mouse import LinuxMouse as Mouse
        from Linux.keyboard import LinuxKeyboard as Keyboard
        from Linux.vk import LinuxVk as Vk

    elif _system == 'Darwin':
        try:
            from Darwin.mouse import DarwinMouse as Mouse
            from Darwin.keyboard import DarwinKeyboard as Keyboard
            from Darwin.vk import DarwinVk as Vk

        except ImportError as e:
            # This can happen during setup if pyobj wasn't already installed
            raise e
    else:
        raise OSError(f"Unsupported platform \"{_system}\"")