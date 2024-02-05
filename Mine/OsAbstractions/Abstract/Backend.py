from typing import Type

from Mine.OsAbstractions import EventApi


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

