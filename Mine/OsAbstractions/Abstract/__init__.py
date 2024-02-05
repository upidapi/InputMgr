import platform as _platform
from typing import Type

from Mine.OsAbstractions.Abstract.EventApi import EventApi


class Backend:
    def __init__(
            self,
            event_stack,
            mouse_controller,
            keyboard_controller
    ):
        # todo add types
        self.event_api: Type[EventApi] = event_stack
        self.mouse_controller = mouse_controller
        self.keyboard_controller = keyboard_controller


def _get_backend():
    _system = _platform.system()
    if _system == 'Windows':
        from Windows.mouse import WindowsMouse
        from Windows.keyboard import WindowsKeyboard
        from Windows.common import WindowsEventApi

        return Backend(
            WindowsEventApi,
            WindowsMouse,
            WindowsKeyboard,
        )

    elif _system == 'Linux':
        from Linux.mouse import LinuxMouse
        from Linux.keyboard import LinuxKeyboard
        from Linux.common import LinuxEventApi

        return Backend(
            LinuxEventApi,
            LinuxMouse,
            LinuxKeyboard,
        )

    elif _system == 'Darwin':
        try:
            from Darwin.mouse import DarwinMouse
            from Darwin.keyboard import DarwinKeyboard
            from Darwin.common import DarwinEventApi

            return Backend(
                DarwinEventApi,
                DarwinMouse,
                DarwinKeyboard,
            )
        except ImportError as e:
            # This can happen during setup if pyobj wasn't already installed
            raise e
    else:
        raise OSError(f"Unsupported platform \"{_system}\"")


_back_end: Backend = _get_backend()


def get_backend():
    return _back_end
