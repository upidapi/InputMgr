import time
from typing import Callable

from Mine.Events import KeyboardEvent, MouseEvent
from Mine.OsAbstractions import get_backend

_event_api = get_backend().EventApi


class EventStack:
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
            _event_api.start_listening()

            print("started")

            while True:
                while True:
                    if break_cond():
                        raise StopIteration

                    if _event_api.event_queue:
                        break

                    _event_api.fetch_new_events()

                    time.sleep(0.001)

                yield _event_api.event_queue.pop(0)
        except BaseException as e:
            print("stopping")

            _event_api.stop_listening()
            raise e


def print_event(
        event,

        mouse_move=False,
        mouse_click=True,
        mouse_unclick=True,
        mouse_scroll=True,

        keyboard_keydown=True,
        keyboard_keyup=True,
        keyboard_key_send=True,
):

    # print(type(event))

    string_event = str(type(event)).split(".")[-1][:-2] + ": "
    padded_event = string_event.ljust(10)

    if isinstance(event, KeyboardEvent.event_types):
        if any((keyboard_keydown, keyboard_keyup, keyboard_key_send)):
            f_char = event.key_data.char or ''
            vk = str(event.key_data.vk).ljust(4)

            print(f"{padded_event}{vk} \"{f_char}\"")
        return

    if isinstance(event, MouseEvent.event_types):
        if isinstance(event, MouseEvent.Move):
            if mouse_move:
                print(f"{padded_event}{event.pos}")
            return

        if isinstance(event, MouseEvent.Scroll):
            if mouse_scroll:
                print(f"{padded_event}{event.pos} {event.dy=} {event.dx=}")
            return

        if isinstance(event, MouseEvent.Click | MouseEvent.UnClick):
            if any((mouse_click, mouse_unclick)):
                print(f"{padded_event}{event.pos} {event.button}")
            return


def print_events():
    for event in EventStack.get_conveyor():
        print_event(event)
