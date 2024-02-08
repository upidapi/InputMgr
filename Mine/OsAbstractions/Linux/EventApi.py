import time

from select import select

import evdev
from evdev import ecodes

from Mine.Events import KeyboardEvent, any_event
from Mine.OsAbstractions.Abstract import EventApi
from Mine.OsAbstractions.Linux.StateMgr import StateMgr
from Mine.OsAbstractions.Linux.common import LinuxKeyEnum, LinuxKeyData, LinuxLayout


DEVICE_PATHS = []
SUPPRESS = False


# ALLOW_UNKNOWN_KEYCODES = False

# todo make into args
#   somehow make into args for the platform
#   instead of consts
#   probably by adding functions
#     eg:
#     def supress(),
#     def un_supress()
#     def set_device_paths()


class LinuxEventApi(EventApi):
    # todo add typehint
    _devices: [evdev.InputDevice] = []
    _pressed_keys: set[LinuxKeyData] = set()

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

    @classmethod
    def stop_listening(cls) -> None:
        for device in cls._devices:
            device.close()

    @classmethod
    def get_pressed_keys(cls):
        return cls._pressed_keys

    @classmethod
    def _get_pressed_modifier_keys(cls):
        """
        gets a set of all active modifier keys

        if none of these keys are pressed then
        """
        modifier_keys = set()
        for key in cls._pressed_keys:
            if key in StateMgr.MODIFIER_MAP:
                modifier_keys.add(key)

        return modifier_keys

    @classmethod
    def _get_active_modifiers(cls) -> set[LinuxKeyData]:
        """
        returns a set of modifier keys that would equate to
        the current modifier state

        so if shift_l, shift_r, ctrl_r are pressed
        => shift, ctrl
        """
        modifier_keys = {None}
        for key in cls._pressed_keys:
            modifier_keys.add(
                StateMgr.MODIFIER_MAP.get(
                    key, None
                )
            )

        modifier_keys.remove(None)
        return modifier_keys

    @classmethod
    def _handle_key_side_effects(cls, event_code, event_val):
        is_press = event_val in (
            evdev.events.KeyEvent.key_down,
            evdev.events.KeyEvent.key_hold,
        )

        if is_press:
            StateMgr.press_keys(event_code)
        else:
            StateMgr.un_press_keys(event_code)

    @classmethod
    def _convert_raw_keyboard_event(
            cls,
            event_val,
            vk,
            time_ms,
            raw_event
    ) -> KeyboardEvent:
        dc = {
            evdev.events.KeyEvent.key_up: KeyboardEvent.KeyUp,
            evdev.events.KeyEvent.key_down: KeyboardEvent.KeyDown,
            evdev.events.KeyEvent.key_hold: KeyboardEvent.KeySend,
        }[event_val]

        cls._handle_key_side_effects(vk, event_val)

        modifier_keys = cls._get_active_modifiers()
        key: LinuxKeyData
        try:
            # keycode = ecodes.keys[vk]
            key = LinuxLayout.for_vk(
                vk,
                modifier_keys
            )

        except KeyError:
            for key_opt in LinuxKeyEnum:
                if key_opt.value.vk == vk:
                    # todo remove this
                    # noinspection PyTypeChecker
                    key = key_opt
                    break
            else:
                key = LinuxKeyData.from_vk(vk)

            # if not ALLOW_UNKNOWN_KEYCODES:
            #     raise TypeError(
            #         f"unknown keycode detected {vk:=} {raw_event:=}"
            #     )
            # keycode = vk

        return dc(
            raw=raw_event,
            time_ms=time_ms,
            key=key
        )

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
        # todo "or might me touch"
        if event_type == ecodes.EV_ABS:
            # todo implement
            return None

        # todo implement scroll
        #  https://stackoverflow.com/questions/15882665/how-to-read-out-scroll-wheel-info-from-dev-input-mice

        # keyboard/click event
        if event_type == ecodes.EV_KEY:
            return cls._convert_raw_keyboard_event(
                event_val,
                event_code,
                time_ms,
                event
            )

    @classmethod
    def fetch_new_events(cls) -> None:
        """ called to add waiting events to the queue """
        r, w, x = select(cls._devices)
        for file_device in r:
            for raw_event in cls._devices[file_device].read():
                event = cls._convert_raw_event_to_event(raw_event)
                cls.dispatch_event(event)


if __name__ == '__main__':
    try:
        LinuxEventApi.start_listening()
        while True:
            LinuxEventApi.fetch_new_events()
            time.sleep(0.01)
    except BaseException as e:
        LinuxEventApi.stop_listening()
        raise e
