import asyncio
import time
from typing import Callable

from src.Events import KeyboardEvent, MouseEvent
from src.OsAbstractions import get_backend
from src.OsAbstractions.Abstract.Keyboard import Up, Down

_event_api = get_backend().EventApi


class EventStack:
    running = False

    @classmethod
    async def get_conveyor(cls):
        """
        Gets the next event, forever. If there's no events queued. Then it
        waits for an event before yielding.

        # ------------------example------------------
        # this would print all keyboard keydown events

        for event in EventHandler.get_conveyor():
            if isinstance(event, KeyboardEvent.KeyDown):
                event.print_event()
        """

        if cls.running:
            raise TypeError("event conveyor already running cant start it again")

        cls.running = True

        try:
            _event_api.start_listening()

            print("started")

            while True:
                while True:
                    if not cls.running:
                        raise StopIteration

                    if _event_api.event_queue:
                        break

                    _event_api.fetch_new_events()

                    await asyncio.sleep(0.001)

                yield _event_api.event_queue.pop(0)
        except BaseException as e:
            print("stopping")

            _event_api.stop_listening()
            raise e

    # add a with poling rate

    # add a sub event stack that isn't a singleton

    @classmethod
    def stop_conveyor(cls):
        if not cls.running:
            raise TypeError("event conveyor is stopped cant stop it again")

        cls.running = False


class EventHandler:
    @classmethod
    def get_conveyor(cls, break_cond: Callable[[], bool] = lambda: False):
        """
        Gets the next event, forever. If there's no events queued. Then it
        waits for an event before yielding.

        # ------------------example------------------
        # this would print all keyboard keydown events

        for event in EventHandler.get_conveyor():
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

    @classmethod
    def print_event(
            cls,
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

    @classmethod
    def print_events(cls):
        for event in cls.get_conveyor():
            cls.print_event(event)

    @classmethod
    def wait_for_text_typed(cls, text):
        cur_progress = 0
        for event in cls.get_conveyor():
            if not isinstance(event, KeyboardEvent.KeySend):
                continue

            for char in event.chars:
                if text[cur_progress] != char:
                    cur_progress = 0
                    continue

                cur_progress += 1

                if cur_progress == len(text):
                    return

    # todo switch to a async event stack


class Recorder:
    """
    records events until stop is called
    """

    # int corresponds to seconds sleep
    data: list[Up | Down, int] = []

    @classmethod
    async def start(cls):
        async for event in EventStack.get_conveyor():
            if not isinstance(event, KeyboardEvent.KeyDown | KeyboardEvent.KeyUp):
                continue

            dc = Up if KeyboardEvent.KeyUp else Down

            cls.data.append(
                dc(
                    event.key_data.vk
                )
            )

    @classmethod
    def stop(cls):
        EventStack.stop_conveyor()
