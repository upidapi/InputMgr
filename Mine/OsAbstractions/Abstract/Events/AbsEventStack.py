import time
from typing import Callable
from abc import ABC, abstractmethod

from Mine.OsAbstractions.Abstract.Events.KeyboardEvents import KeyboardEvent
from Mine.OsAbstractions.Abstract.Events.MouseEvents import MouseEvent


class AbsEventStack(ABC):
    all_events = KeyboardEvent.event_types | MouseEvent.event_types

    queued_events = []
    # store the current state of the keyboard
    # vk_code: is_down
    _key_states = {}

    @classmethod
    def _dispatch_event(cls, event: all_events) -> None:
        """ helper function to add a new event to the event stack """
        if isinstance(event, KeyboardEvent.KeySend):
            if not cls._key_states[event.key]:
                # pycharm incorrectly assumes that "time" "raw" "vk_code" isn't
                # a part of KeyDown since it only checks the parent for attrs
                # but not the parent's parent
                # noinspection PyArgumentList
                cls.queued_events.append(
                    KeyboardEvent.KeyDown(
                        time=event.time,
                        raw=event.raw,
                        vk_code=event.vk_code
                    )
                )

            cls._key_states[event.key] = True

        if isinstance(event, KeyboardEvent.KeyUp):
            cls._key_states[event.key] = False

        cls.queued_events.append(event)

    @classmethod
    @abstractmethod
    def fetch_new_events(cls) -> None:
        """ called to add waiting events to the queue """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def start_listening(cls) -> None:
        """ a startup method that will be called when the EventStack is started """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def stop_listening(cls) -> None:
        """ a cleanup method that will be called when the EventStack is stopped """
        raise NotImplementedError

    @classmethod
    def get_conveyor(cls, break_cond: Callable[[], bool] = lambda: False):
        """
        Gets the next event, forever. If there's no events queued. Then it
        waits for an event before yielding.

        # ------------------example------------------
        # this would print all keyboard keydown events

        es = EventStack()

        for event in es.get_conveyor():
            if isinstance(event, KeyboardEvent.KeyDown):
                event.print_event()
        """
        try:
            while True:
                while True:
                    if break_cond():
                        raise StopIteration

                    cls.fetch_new_events()

                    if cls.queued_events:
                        break

                    time.sleep(0.001)

                yield cls.queued_events.pop(0)
        except KeyboardInterrupt:
            cls.stop_listening()

            raise KeyboardInterrupt


# class EventStack(ABC):
#     all_events = KeyboardEvent.event_types | MouseEvent.event_types
#
#     def __init__(self):
#         # temp
#         # should be based on the os
#         self.event_handler = AbsEventHandler()
#
#     def __del__(self):
#         self.event_handler.stop_listening()
#         print("cleaned upp event stack")
#
