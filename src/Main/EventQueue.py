import asyncio
import atexit
import inspect
from typing import Callable, Awaitable

from src.Events import any_event
from src.OsAbstractions import get_backend

_event_api = get_backend().EventApi


class EventDistributor:
    # _running_sub_stacks = set()
    _event_callbacks = set()

    running = False

    @classmethod
    async def run_event_distributor(cls):
        if cls.running:
            raise TypeError(
                "event conveyor already running cant start it again"
            )

        cls.running = True

        # some added safety for debugging
        _event_api.start_listening()

        print("started")

        while True:
            if not cls._event_callbacks:
                _event_api.stop_listening()
                cls.running = False
                break

            for event in _event_api.event_queue:
                for callback in cls._event_callbacks:
                    callback(event)
            _event_api.event_queue = []

            _event_api.fetch_new_events()

            await asyncio.sleep(0.001)

    # add a with poling rate

    @classmethod
    def add_callback(cls, callback: Callable[[any_event], None]):
        cls._event_callbacks.add(callback)

        if not cls.running:
            asyncio.create_task(
                cls.run_event_distributor()
            )

    @classmethod
    def remove_callback(cls, callback: Callable[[any_event], None]):
        cls._event_callbacks.remove(callback)

        if not cls._event_callbacks:
            cls.running = False

# class EventDistributor:
#     _event_callbacks = set()
#
#     @classmethod
#     async def _run_event_distributor(cls):
#         _event_api.start_listening()
#
#         while True:
#             for event in _event_api.event_queue:
#                 for callback in cls._event_callbacks:
#                     callback(event)
#             _event_api.event_queue = []
#
#             _event_api.fetch_new_events()
#
#             await asyncio.sleep(0.001)
#
#     # add a with poling rate
#
#     @classmethod
#     def add_callback(cls, callback: Callable[[any_event], None]):
#         if callback in cls._event_callbacks:
#             raise ValueError(
#                 f"callback: {callback} is already a registered function"
#             )
#
#         cls._event_callbacks.add(callback)
#
#     @classmethod
#     def remove_callback(cls, callback: Callable[[any_event], None]):
#         try:
#             cls._event_callbacks.remove(callback)
#         except KeyError:
#             raise ValueError(
#                 f"cannot remove {callback} since is not registered"
#             )
#
#     asyncio.create_task(
#         _run_event_distributor()
#     )


# incase we run into some kind of error make sure
# that the listener is stopped
@atexit.register
def _event_listening_cleanup():
    print("cleaning evnet_listener up due to exception")

    _event_api.stop_listening()


class EventQueue:
    """
    a queue of all events

    avents are added to it when detected by the event handlers
    removed when read
    """
    def __init__(
            self,
            # event_distributor: EventDistributor = None
    ):
        # self._event_distributor = event_distributor or EventDistributor()
        self._in_with = False
        self._running = False
        self.queued_events = []

    def add_event(self, event: any_event):
        self.queued_events.append(event)

    def stop(self):
        self._running = False

    def __enter__(self):
        self._in_with = True

        EventDistributor.add_callback(self.add_event)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._in_with = False

        if exc_type is None:
            EventDistributor.add_callback(self.add_event)
            return

        if exc_type is StopIteration:
            EventDistributor.remove_callback(self.add_event)
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
            raise TypeError(
                "event conveyor already running cant start it again"
            )

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

    async def supply_events(
            self,
            handler: Callable[[any_event], Awaitable[None] | None]
    ):
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

            # noinspection PyAsyncCall
            asyncio.create_task(wrapper())

        else:
            with self as eq:
                async for event in eq:
                    handler(event)
