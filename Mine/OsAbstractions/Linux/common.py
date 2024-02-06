from select import select

from Mine.Events import any_event, MouseEvent, KeyboardEvent
from Mine.OsAbstractions.Abstract import EventApi

# from evdev.ecodes import keys, KEY, SYN, REL, ABS, EV_KEY, EV_REL, EV_ABS, EV_SYN
from evdev import ecodes
import evdev


ALLOW_UNKNOWN_KEYCODES = False


# https://python-evdev.readthedocs.io/en/latest/tutorial.html#reading-events-using-asyncio
# devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

class LinuxEventApi(EventApi):
    # todo add typehint
    _devices: [] = []

    @classmethod
    def start_listening(cls) -> None:
        """ a startup method that will be called when the EventStack is started """
        raise NotImplementedError

    @classmethod
    def stop_listening(cls) -> None:
        """ a cleanup method that will be called when the EventStack is stopped """
        raise NotImplementedError

    @classmethod
    def _convert_raw_event_to_event(cls, event) -> any_event:
        # magic
        # https://github.com/gvalkov/python-evdev/blob/8c8014f78ceea2585a9092aedea5c4f528ec7ee8/evdev/events.py#L77

        # event: KeyEvent | RelEvent | AbsEvent | SynEvent = categorize(event)
        # event -> (sec, usec, type, code, val)
        time_ms = event[0] + event[1] / 1000000.0
        event_type = event[2]
        event_code = event[3]
        event_val = event[4]

        # todo remove (it's for debug)
        print(event)
        if event_type in (ecodes.EV_REL, ecodes.EV_SYN):
            # ignore
            return None

        # mouse event
        # todo or might me touch
        if event_type == ecodes.EV_ABS:
            # todo implement
            return None

        # todo implement scroll
        #  https://stackoverflow.com/questions/15882665/how-to-read-out-scroll-wheel-info-from-dev-input-mice

        # keyboard/click event
        if event_type == ecodes.EV_KEY:
            dc = {
                0: KeyboardEvent.KeyUp,
                1: KeyboardEvent.KeyDown,
                2: KeyboardEvent.KeySend,
            }[event_val]

            try:
                keycode = ecodes.keys[event_code]
            except KeyError:
                if not ALLOW_UNKNOWN_KEYCODES:
                    raise TypeError(
                        f"unknown keycode detected {event_code:=} {event:=}"
                    )
                keycode = event_code

            return dc(
                raw=event,
                time_ms=time_ms,
                vk_code=keycode
            )

    @classmethod
    def fetch_new_events(cls) -> None:
        """ called to add waiting events to the queue """
        r, w, x = select(cls._devices)
        for file_device in r:
            for raw_event in cls._devices[file_device].read():
                event = cls._convert_raw_event_to_event(raw_event)
                cls.dispatch_event(event)
