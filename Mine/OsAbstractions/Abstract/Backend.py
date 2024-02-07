from typing import Type

from Mine.OsAbstractions.Abstract.EventApi import EventApi
from Mine.OsAbstractions.Abstract.Mouse import AbsMouse
from Mine.OsAbstractions.Abstract.Keyboard import AbsKeyboard


class AbsBackend:
    event_api: Type[EventApi]
    mouse_controller: Type[AbsMouse]
    keyboard_controller: Type[AbsKeyboard]

