from typing import Type

from src.OsAbstractions.Abstract.EventApi import EventApi
from src.OsAbstractions.Abstract.Mouse import AbsMouse
from src.OsAbstractions.Abstract.Keyboard import AbsKeyboard


class AbsBackend:
    EventApi: Type[EventApi]
    Mouse: Type[AbsMouse]
    Keyboard: Type[AbsKeyboard]
