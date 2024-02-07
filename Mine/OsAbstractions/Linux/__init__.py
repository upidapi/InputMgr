from Mine.OsAbstractions import AbsBackend as _AbsBackend

from Mine.OsAbstractions.Linux.common import LinuxEventApi as _LinuxEventApi


class LinuxBackend(_AbsBackend):
    event_api = _LinuxEventApi
    mouse_controller = None
    keyboard_controller = None
