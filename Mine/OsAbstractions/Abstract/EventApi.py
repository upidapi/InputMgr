from abc import ABC, abstractmethod

from Mine.Events import any_event, KeyboardEvent


class EventApi(ABC):
    # used to block events that where created programmatically
    _blocked_events = set()
    event_queue = []
    # store the current state of the keyboard
    # vk_code: is_down
    _key_states = {}

    # maybe
    # todo add a check to make sure that you've started listening before
    #   using meth::fetch_new_events

    @classmethod
    def dispatch_event_block(cls, event: any_event) -> None:
        """ makes it so that the next event that is dispatched with the {}"""

        # todo: add some warning for if a event stys blocked for too long
        #   since that would mean that the programmatically generated user
        #   input failed.
        cls._blocked_events.add(event)

    @classmethod
    def dispatch_event(cls, event: any_event) -> None:
        """ helper function to add a new event to the event stack """

        # check if event is blocked
        for blocked_event in cls._blocked_events:
            if event == blocked_event:
                cls._blocked_events.remove(blocked_event)
                return

        if isinstance(event, KeyboardEvent.KeySend):
            if not cls._key_states[event.key]:
                # pycharm incorrectly assumes that "time" "raw" "vk_code" isn't
                # a part of KeyDown since it only checks the parent for attrs
                # but not the parent's parent
                # noinspection PyArgumentList
                cls.event_queue.append(
                    KeyboardEvent.KeyDown(
                        time=event.time,
                        raw=event.raw,
                        vk_code=event.vk_code
                    )
                )

            cls._key_states[event.key] = True

        if isinstance(event, KeyboardEvent.KeyUp):
            cls._key_states[event.key] = False

        cls.event_queue.append(event)

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
