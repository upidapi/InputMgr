from typing import Type

from Mine.OsAbstractions.Abstract.EventApi import EventApi
from Mine.OsAbstractions.Abstract.Mouse import AbsMouse
from Mine.OsAbstractions.Abstract.Keyboard import AbsKeyboard


class AbsBackend:
    EventApi: Type[EventApi]
    Mouse: Type[AbsMouse]
    Keyboard: Type[AbsKeyboard]
