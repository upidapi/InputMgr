import asyncio
import contextlib
import time
from typing import Callable

from src.Events import KeyboardEvent, MouseEvent
from src.OsAbstractions import get_backend
from src.OsAbstractions.Abstract.Keyboard import Up, Down

_event_api = get_backend().EventApi


class EventDistributor:
    running_sub_stacks = set()

    @classmethod
    async def run_event_distributor(cls):
        """
        Gets the next event, forever. If there's no events queued. Then it
        waits for an event before yielding.

        # ------------------example------------------
        # this would print all keyboard keydown events

        for event in EventHandler.get_conveyor():
            if isinstance(event, KeyboardEvent.KeyDown):
                event.print_event()
        """

        if cls.running_sub_stacks:
            raise TypeError("event conveyor already running cant start it again")

        cls.running = True

        # some added safety for debugging
        try:
            _event_api.start_listening()

            print("started")

            while True:
                if not cls.running_sub_stacks:
                    _event_api.stop_listening()

                for es in cls.running_sub_stacks:
                    es._queued_events += _event_api.event_queue
                    _event_api.event_queue = []

                _event_api.fetch_new_events()

                await asyncio.sleep(0.001)

        except BaseException as e:
            print("stopping")

            _event_api.stop_listening()
            raise e

    # add a with poling rate

    # add a sub event stack that isn't a singleton

    @classmethod
    def add_sub_stack(cls, sub_stack):
        need_start = not cls.running_sub_stacks

        cls.running_sub_stacks.add(sub_stack)

        if need_start:
            cls.run_event_distributor()

    @classmethod
    def remove_sub_stack(cls, sub_stack):
        cls.running_sub_stacks.remove(sub_stack)


class EventStack:
    def __init__(self):
        self._in_with = False
        self._running = False
        self._queued_events = []

    def __enter__(self):
        self._in_with = True

        EventDistributor.add_sub_stack(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._in_with = False

        if exc_type is None:
            EventDistributor.remove_sub_stack(self)
            return

        _event_api.stop_listening()
        raise exc_type(exc_val)

    async def __aiter__(self):
        """
        Gets the next event, forever. If there's no events queued. Then it
        waits for an event before yielding.

        # ------------------example------------------
        # this would print all keyboard keydown events

        for event in EventHandler.get_conveyor():
            if isinstance(event, KeyboardEvent.KeyDown):
                event.print_event()

        btw don't use break to exit the loop
        you need to use self.stop_conveyor() to stop the loop
        """

        if not self._in_with:
            raise TypeError("not in protective with statement")

        if self._running:
            raise TypeError("event conveyor already running cant start it again")

        self._running = True

        while True:
            while True:
                if self._queued_events:
                    break

                await asyncio.sleep(0.001)

            yield self._queued_events.pop(0)

    # add a with poling rate

    # add a sub event stack that isn't a singleton
    def stop(self):
        self._running = False

    # @classmethod
    # def add_handler(cls, handler):
    #     with cls() as es:
    #         async for event in es:
    #             handler(event)


class EventHandler:
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
        with EventStack() as es:
            async for event in es:
                cls.print_event(event)

    @classmethod
    def wait_for_text_typed(cls, text):
        cur_progress = 0

        with EventStack() as es:
            async for event in es:

                if not isinstance(event, KeyboardEvent.KeySend):
                    continue

                for char in event.chars:
                    if text[cur_progress] != char:
                        cur_progress = 0
                        continue

                    cur_progress += 1

                    if cur_progress == len(text):
                        return


class Recorder:
    """
    records events until stop is called
    """

    # int corresponds to seconds sleep
    data: list[Up | Down | int] = []

    es: EventStack | None = None

    @classmethod
    def _handle_event(cls, event):
        if not isinstance(event, KeyboardEvent.KeyDown | KeyboardEvent.KeyUp):
            return

        dc = Up if KeyboardEvent.KeyUp else Down

        cls.data.append(
            dc(
                event.key_data.vk
            )
        )

    @classmethod
    async def start(cls):
        with EventStack() as es:
            cls.es = es
            async for event in es:
                cls._handle_event(event)

    @classmethod
    def stop(cls):
        if cls.es is None:
            raise TypeError("cant stop it since recorder not running")

        cls.es.stop()

        data = cls.data
        cls.data = []
        return data
