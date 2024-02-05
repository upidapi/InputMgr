import time
from typing import Callable

from Mine.OsAbstractions.Abstract import get_backend

_event_api = get_backend().event_api


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

            while True:
                while True:
                    if break_cond():
                        raise StopIteration

                    _event_api.fetch_new_events()

                    if _event_api.event_queue:
                        break

                    time.sleep(0.001)

                yield _event_api.event_queue.pop(0)
        except KeyboardInterrupt:
            _event_api.stop_listening()

            raise KeyboardInterrupt

