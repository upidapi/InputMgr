import os
from typing import Type

from Mine.OsAbstractions.Abstract import AbsMouse

LinuxMouse: Type[AbsMouse]

# check if users is using xorg
if os.environ.get('DISPLAY'):
    from Mine.OsAbstractions.Linux.Mouse.XorgMouse import LinuxXLibMouse

    LinuxMouse = LinuxXLibMouse
else:
    raise TypeError("could not find proper LinuxMouse, (we've only got support for xorg)")

"""
# struct

- top



event handler

state mgr



- core


"""