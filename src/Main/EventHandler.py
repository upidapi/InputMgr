import asyncio
import atexit
import inspect
import time
from typing import Callable, Awaitable

from src.Events import KeyboardEvent, MouseEvent, any_event

from src.Main.Mouse import Mouse
from src.Main.Keyboard import Keyboard
from src.OsAbstractions import get_backend
from src.OsAbstractions.Abstract.Keyboard import Down, LiteralVk

_event_api = get_backend().EventApi


class _EventDistributor:
    _running_sub_stacks = set()
    running = False

    @classmethod
    async def run_event_distributor(cls):
        if cls.running:
            raise TypeError("event conveyor already running cant start it again")

        cls.running = True

        # some added safety for debugging
        _event_api.start_listening()

        print("started")

        while True:
            if not cls._running_sub_stacks:
                _event_api.stop_listening()
                cls.running = False
                break

            for eq in cls._running_sub_stacks:
                eq.queued_events += _event_api.event_queue
                _event_api.event_queue = []

            _event_api.fetch_new_events()

            await asyncio.sleep(0.001)

    # add a with poling rate

    @classmethod
    def add_sub_stack(cls, sub_stack):
        need_start = not cls._running_sub_stacks

        cls._running_sub_stacks.add(sub_stack)

        if need_start:
            cls.run_event_distributor()

    @classmethod
    def remove_sub_stack(cls, sub_stack):
        cls._running_sub_stacks.remove(sub_stack)


# incase we run into some kind of error make sure
# that the listener is stopped
@atexit.register
def _event_listening_cleanup():
    if not _EventDistributor.running:
        return

    print("cleaning evnet_listener up due to exception")

    _event_api.stop_listening()


class EventQueue:
    """
    a queue of all events

    avents are added to it when detected by the event handlers
    removed when read
    """
    def __init__(self):
        self._in_with = False
        self._running = False
        self.queued_events = []

    def stop(self):
        self._running = False

    def __enter__(self):
        self._in_with = True

        _EventDistributor.add_sub_stack(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._in_with = False

        if exc_type is None:
            _EventDistributor.remove_sub_stack(self)
            return

        if exc_type is StopIteration:
            _EventDistributor.remove_sub_stack(self)
            return True  # supress exception

    async def __aiter__(self):
        """
        Gets the next event, forever. If there's no events queued. Then it
        waits for an event before yielding.

        # ------------------example------------------
        # this would print all keyboard keydown events

        with EventStack() as eq:
            for event in eq:
                if isinstance(event, KeyboardEvent.KeyDown):
                    event.print_event()
        """

        if not self._in_with:
            raise TypeError("not in protective with statement")

        if self._running:
            raise TypeError("event conveyor already running cant start it again")

        self._running = True

        while True:
            while True:
                if not self._running:
                    raise StopIteration  # todo or maybe StopAsyncIteration

                if self.queued_events:
                    break

                await asyncio.sleep(0.001)

            yield self.queued_events.pop(0)

    # add a with poling rate

    async def supply_events(self, handler: Callable[[any_event], Awaitable[None] | None]):
        """
        a decorator that makes the supplied func receive
        all events

        ------------example------------
        # prints all events

        eq = EventStack()
        @eq.supply_events
        async def handle_event(event)
            print_event(event)

        # to stop it either call eq.stop()
        # or raise StopIteration (from inside the handler)
        """
        is_async = inspect.iscoroutinefunction(handler)

        if is_async:
            async def wrapper():
                with self as _eq:
                    async for _event in _eq:
                        await handler(_event)

            asyncio.create_task(wrapper())

        else:
            with self as eq:
                async for event in eq:
                    handler(event)


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


async def print_events(
        mouse_move=False,
        mouse_click=True,
        mouse_unclick=True,
        mouse_scroll=True,

        keyboard_keydown=True,
        keyboard_keyup=True,
        keyboard_key_send=True,
):
    with EventQueue() as eq:
        async for event in eq:
            print_event(
                event,

                mouse_move,
                mouse_click,
                mouse_unclick,
                mouse_scroll,

                keyboard_keydown,
                keyboard_keyup,
                keyboard_key_send,
            )


async def wait_for_text_typed(text):
    """
    waits for a specific string to be typed (for example aaAAaa33)
    and return when that happens
    """
    cur_progress = 0

    with EventQueue() as eq:
        async for event in eq:

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
    records user inputs

    --------example--------
    # records until "a" is typed
    # then waits for 1 sec before playing the recording
    async def main():
        Recorder.record()

        await EventHelper.wait_for_text_typed("a")

        recording = Recorder.stop_recording()

        await asyncio.sleep(1)

        await Recorder.play(recording)

    asyncio.run(main())
    """

    # int corresponds to seconds sleep
    data: list[dict] = []

    eq: EventQueue | None = None

    @classmethod
    def _handle_event(cls, event):
        # we ignore key-send events sice they're not really
        # user inputs and only a helper for handling them
        if isinstance(event, KeyboardEvent.KeySend):
            return

        cls.data.append(event)
        return

    @classmethod
    def record(cls):
        """
        starts recording user inputs
        """
        cls.eq = EventQueue()

        async def record():
            with cls.eq:
                async for event in cls.eq:
                    cls._handle_event(event)

        # will finish eventually
        asyncio.create_task(record())

    @classmethod
    def stop_recording(cls):
        """
        stops the current recording and returns the recording

        can be replayed with Recorder.play(recording)
        """
        if cls.eq is None:
            raise TypeError("cant stop it since recorder not running")

        cls.eq.stop()

        data = cls.data
        cls.data = []
        return data

    @classmethod
    async def play(cls, data: [any_event]):
        """
        replays a recording (returned from stop_recording)
        with the timings preserved
        """
        if not data:
            return

        start = time.time_ns() / 10 ** 6
        initial_time = data[0].time_ms
        start_delta = start + initial_time

        for event in data:
            event: any_event
            to_exec = event.time_ms + start_delta - time.time_ns() / 10 ** 6

            if to_exec > 0:
                await asyncio.sleep(to_exec * 1000)

            if isinstance(event, KeyboardEvent.KeyDown | KeyboardEvent.KeyUp):
                dc = Down if isinstance(event, KeyboardEvent.KeyDown) else Down
                Keyboard.typewrite(
                    dc(
                        LiteralVk(
                            event.key_data
                        )
                    )
                )

            elif isinstance(event, MouseEvent.Move):
                Mouse.set_pos(*event.pos)

            elif isinstance(event, MouseEvent.Click | MouseEvent.UnClick):
                down = isinstance(event, MouseEvent.Click)

                Mouse.press_button(event.button, down)

            elif isinstance(event, MouseEvent.Scroll):
                # todo make sure that the scroll(dx, dy) == event for it (.dx, .dy)
                Mouse.scroll(event.dx, event.dy)

            else:
                raise TypeError(f"invalid event type for playback: {event}")
