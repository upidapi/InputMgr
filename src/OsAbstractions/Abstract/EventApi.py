from abc import ABC, abstractmethod

from src.Events import any_event, KeyboardEvent


class EventApi(ABC):
    # used to block events that where created programmatically
    _blocked_events: set[any_event] = set()
    event_queue = []
    # store the current state of the keyboard
    # vk_code: is_down
    # _key_states = {}

    # is the EventApi inited and listening
    _active = False

    # maybe
    # todo add a check to make sure that you've started listening before
    #   using meth::fetch_new_events

    def __init__(self):
        raise TypeError("you are not ment to make instances of this class")

    @classmethod
    def dispatch_event_block(cls, event: any_event) -> None:
        """ makes it so that the next event that is dispatched with the {}"""

        # todo: add some warning for if a event stys blocked for too long
        #   since that would mean that the programmatically generated user
        #   input (probably) failed.
        cls._blocked_events.add(event)

    @classmethod
    def _is_event_blocked(cls, event: any_event) -> bool:
        # check if event is blocked
        for blocked_event in cls._blocked_events:
            if event.__class__ == blocked_event.__class__:
                if isinstance(event, KeyboardEvent.event_types):
                    # When dispatching blocks for keyboards
                    # we block a specific key/button.
                    # So don't compare the full thing since the
                    # state is impossible to calculate.
                    if event.key_data.vk == blocked_event.key_data.vk:
                        return True

                if event == blocked_event:
                    # todo make it so that a block sent at eg ms 100
                    #  only can block events after that
                    cls._blocked_events.remove(blocked_event)
                    return True

        return False

    @classmethod
    def dispatch_event(cls, *event: any_event) -> None:
        """ helper function to add a new event to the event stack """

        # this logic was written for windows
        # if isinstance(event, KeyboardEvent.KeySend):
        #     if not cls._key_states.get(event.key_data, False):
        #         cls.event_queue.append(
        #             KeyboardEvent.KeyDown(
        #                 time_ms=event.time_ms,
        #                 raw=event.raw,
        #                 key_data=event.key_data
        #             )
        #         )
        #
        #     cls._key_states[event.key_data] = True
        #
        # if isinstance(event, KeyboardEvent.KeyUp):
        #     cls._key_states[event.key_data] = False

        cls.event_queue += event

    @classmethod
    def clear_blocked_events(cls):
        cls._blocked_events = set()

    @classmethod
    def clear_queued_events(cls):
        cls.event_queue = []

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
