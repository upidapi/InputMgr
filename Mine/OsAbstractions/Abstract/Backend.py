from typing import Type

from Mine.OsAbstractions.Abstract import EventApi, AbsMouse, AbsKeyboard


class AbsBackend:
    def __init__(
            self,
            event_stack,
            mouse_controller,
            keyboard_controller
    ):
        self.event_api: Type[EventApi] = event_stack
        self.mouse_controller: Type[AbsMouse] = mouse_controller
        self.keyboard_controller: Type[AbsKeyboard] = keyboard_controller

