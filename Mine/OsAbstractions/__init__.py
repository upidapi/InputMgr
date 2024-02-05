import platform as _platform

from Mine.OsAbstractions.Abstract import Backend


def _get_backend():
    _system = _platform.system()
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


_back_end: Backend = _get_backend()


def get_backend():
    return _back_end
