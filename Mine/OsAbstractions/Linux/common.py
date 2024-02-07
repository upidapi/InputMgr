from select import select

from Mine.Events import any_event, MouseEvent, KeyboardEvent
from Mine.OsAbstractions.Abstract import EventApi

# from evdev.ecodes import keys, KEY, SYN, REL, ABS, EV_KEY, EV_REL, EV_ABS, EV_SYN
from evdev import ecodes
import evdev


ALLOW_UNKNOWN_KEYCODES = False

# todo make into args
#   somehow make into args for the platform
#   instead of consts
#   probably by adding functions
#     eg:
#     def supress(),
#     def un_supress()
#     def set_device_paths()

DEVICE_PATHS = []
SUPPRESS = False


# https://python-evdev.readthedocs.io/en/latest/tutorial.html#reading-events-using-asyncio
# devices = [evdev.InputDevice(path) for path in evdev.list_devices()]


class LinuxEventApi(EventApi):
    _MODIFIER_MAP: dict[Key, Key] = {
        Key.alt.value.vk: Key.alt,
        Key.alt_l.value.vk: Key.alt,
        Key.alt_r.value.vk: Key.alt,
        Key.alt_gr.value.vk: Key.alt_gr,
        Key.shift.value.vk: Key.shift,
        Key.shift_l.value.vk: Key.shift,
        Key.shift_r.value.vk: Key.shift
    }

    # todo add typehint
    _devices = []
    _modifiers = set()
    @classmethod
    def _get_devices(cls, paths):
        """Attempts to load a readable keyboard device.

        :param paths: A list of paths.

        :return: a compatible device
        """
        devices = []
        for path in paths:
            # Open the device
            try:
                device = evdev.InputDevice(path)
            except OSError:

                continue

            devices.append(device)
            # # Does this device provide more handled event codes?
            # capabilities = next_dev.capabilities()
            # next_count = sum(
            #     len(codes)
            #     for event, codes in capabilities.items()
            #     if event in cls._EVENTS
            # )
            #
            # if next_count > count:
            #     dev = next_dev
            #     count = next_count
            # else:
            #     next_dev.close()

        if not devices:
            # todo prob change to "no devices found"
            #   since this includes mice etc
            raise OSError('no keyboard device available')

        return devices

    @classmethod
    def start_listening(cls) -> None:
        cls._devices = cls._get_devices(
            DEVICE_PATHS or evdev.list_devices()
        )
        # todo add support to supress individual devices
        if SUPPRESS:
            for device in cls._devices:
                device.grab()  # mine!

        cls._layout = LAYOUT
        cls._modifiers = set()

    @classmethod
    def stop_listening(cls) -> None:
        for device in cls._devices:
            device.close()

    @classmethod
    def _handle_modifyer_key(cls, event_code, event_val):
        is_press = event_val in (
            evdev.events.KeyEvent.key_down,
            evdev.events.KeyEvent.key_hold,
        )

        if event_code in cls._MODIFIER_MAP:
            modifier = cls._MODIFIER_MAP[event_code]
            if is_press:
                cls._modifiers.add(modifier)
            elif modifier in cls._modifiers:
                cls._modifiers.remove(modifier)


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
                evdev.events.KeyEvent.key_up: KeyboardEvent.KeyUp,
                evdev.events.KeyEvent.key_down: KeyboardEvent.KeyDown,
                evdev.events.KeyEvent.key_hold: KeyboardEvent.KeySend,
            }[event_val]

            vk = event_code

            cls._handle_modifyer_key(vk, event_val)

            try:
                # keycode = ecodes.keys[vk]
                key = cls._layout.for_vk(vk, cls._modifiers)

            except KeyError:
                if not ALLOW_UNKNOWN_KEYCODES:
                    raise TypeError(
                        f"unknown keycode detected {vk:=} {event:=}"
                    )
                keycode = vk


            return dc(
                raw=event,
                time_ms=time_ms,
                vk_code=vk
            )

    @classmethod
    def fetch_new_events(cls) -> None:
        """ called to add waiting events to the queue """
        r, w, x = select(cls._devices)
        for file_device in r:
            for raw_event in cls._devices[file_device].read():
                event = cls._convert_raw_event_to_event(raw_event)
                cls.dispatch_event(event)
