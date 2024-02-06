import platform as _platform
from typing import Literal

from Mine.OsAbstractions.Abstract import AbsBackend


_system = _platform.system()


def _get_backend():
    if _system == 'Windows':
        from Windows import WindowsBackend

        return WindowsBackend

    elif _system == 'Linux':
        from Linux import LinuxBackend

        return LinuxBackend

    elif _system == 'Darwin':
        try:
            from Darwin import DarwinBackend

            return DarwinBackend

        except ImportError as e:
            # This can happen during setup if pyobj wasn't already installed
            raise e
    else:
        raise OSError(f"Unsupported platform \"{_system}\"")


_back_end: AbsBackend = _get_backend()


def get_backend() -> AbsBackend:
    return _back_end


def get_backend_type():
    return _system
