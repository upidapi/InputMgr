from select import select

import evdev

from Mine.Events import KeyboardEvent, any_event, MouseEvent
from Mine.OsAbstractions.Abstract import EventApi
from Mine.OsAbstractions.Linux.StateMgr import LinuxStateMgr
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

class LinuxInputEvent:
    def __init__(self, event: evdev.InputEvent):
        #: Time in seconds since epoch at which event occurred.
        self.time_ms = event.timestamp() * 1000

        self.type = event.type

        self.code = event.code

        self.value = event.value

    def __str__(self):
        return \
            (f"{self.__class__.__name__}("
             f"time: {self.time_ms} "
             f"type: {self.type}, "
             f"code: {self.code}, "
             f"val: {self.value})")

    __repr__ = __str__


class LinuxEventApi(EventApi):
    _devices: dict[str, evdev.InputDevice] = {}
    _pressed_keys: set[LinuxKeyData] = set()

    @classmethod
    def _get_devices(cls, paths):
        """Attempts to load a readable keyboard device.

        :param paths: A list of paths.

        :return: a compatible device
        """
        # originally this had some try/catching for os errors
        # and just ignored them
        # if problems occur we might have to re add it
        devices = map(evdev.InputDevice, paths)
        devices = {dev.fd: dev for dev in devices}

        if not devices:
            raise OSError('no devices found')

        return devices

    @classmethod
    def start_listening(cls) -> None:
        cls._devices = cls._get_devices(
            DEVICE_PATHS or evdev.list_devices()
        )
        # todo add support to supress individual devices
        if SUPPRESS:
            for device in cls._devices.values():
                device.grab()  # mine!

    @classmethod
    def stop_listening(cls) -> None:
        for device in cls._devices.values():
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
            if key in LinuxStateMgr.MODIFIER_MAP:
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
                LinuxStateMgr.MODIFIER_MAP.get(
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
            LinuxStateMgr.press_keys(event_code)
        else:
            LinuxStateMgr.un_press_keys(event_code)

    @classmethod
    def _convert_raw_keyboard_event(cls, event: LinuxInputEvent) -> KeyboardEvent:
        # dataclass

        # key up
        if event.value == 0:
            dc = KeyboardEvent.KeyUp

        # key down
        elif event.value == 1:
            dc = KeyboardEvent.KeyDown

        # key send
        elif event.value == 2:
            dc = KeyboardEvent.KeySend

        else:
            raise TypeError(f"event value not 0, 1, or 2: {event}")

        vk = event.code
        cls._handle_key_side_effects(vk, event.value)

        modifier_keys = cls._get_active_modifiers()
        key: LinuxKeyData
        try:
            # todo check if this is right
            #   they dont do the same thing
            # keycode = ecodes.keys[vk]
            key = LinuxLayout.for_vk(
                vk,
                modifier_keys
            )

        except KeyError:
            for key_opt in LinuxKeyEnum:
                if key_opt.vk == vk:
                    key = key_opt
                    break
            else:
                # if not ALLOW_UNKNOWN_KEYCODES:
                #     raise TypeError(
                #         f"unknown keycode detected {vk:=} {raw_event:=}"
                #     )

                key = LinuxKeyData.from_vk(vk)

        return dc(
            raw=event,
            time_ms=event.time_ms,
            key_data=key
        )

    # todo get initial pos
    # todo get the actual pos
    #   the pos isn't exposed to evdev, since its too low level
    #   so we have to get it another way, for example xlib
    # x, y
    _mouse_pos = (0, 0)

    @classmethod
    def _convert_mouse_move_event(cls, event: LinuxInputEvent) -> MouseEvent.event_types | None:
        dx, dy = 0, 0

        # dx move
        if event.code == 0:
            # val = pixels moved
            # val < 0: move left
            # val > 0: move right
            dx = event.value

        # dy move
        if event.code == 1:
            # val = pixels moved
            # val < 0: move up
            # val > 0: move down
            dy = event.value

        cls._mouse_pos = (
            cls._mouse_pos[0] + dx,
            cls._mouse_pos[1] + dy,
        )

        return MouseEvent.Move(
            time_ms=event.time_ms,
            raw=event,
            pos=cls._mouse_pos,
            delta=(dx, dy)
        )

    @classmethod
    def _convert_scroll_event(cls, event: LinuxInputEvent):
        # todo add support for sideways scroll

        # scroll direction
        if event.code == 8:
            # val = 1: scroll up
            # val = -1: scroll down
            return

        # scroll amount
        if event.code == 11:
            # val = scroll amount
            # val > 0: scroll up
            # val < 0: scroll down
            return MouseEvent.Scroll(
                time_ms=event.time_ms,
                raw=event,
                pos=cls._mouse_pos,
                dy=-event.value,
            )

    @classmethod
    def _convert_raw_event_to_event(cls, event: evdev.InputEvent) -> any_event | None:
        event = LinuxInputEvent(event)

        # sync event
        if event.type == 0:
            # no real purpose (probably)
            return

        # rel event
        # mouse move, scroll
        if event.type == 2:
            if event.code in (0, 1):
                return cls._convert_mouse_move_event(event)

            if event.code in (8, 11):
                return cls._convert_scroll_event(event)

            print("unknown scroll: ", event)

            return

        # print(event)

        # "button" event
        # like a keyboard or button press
        if event.type == 1:
            # keycode = event.code
            # characters are typed on "key down" and "key send"

            if event.value in (0, 1, 2):
                return cls._convert_raw_keyboard_event(event)

            print("unknown button: ", event)

        # idk
        if event.type == 4:
            # sent right before a "key down" or "key up" event

            # the code seams to always be
            # event.code = 4

            # the val seams to correspond with the vk
            # it's always the same for the same button
            #     ive tried restarting the program
            #     not checked:
            #         restart computer
            #         another keyboard
            #         another layout

            # if you want to compare
            # specs
            #     arch
            #     swedish (nordic) layout
            #     key-cron keyboad
            # examples
            #     q => val = 458772
            #     w => val = 458778
            #     e => val = 458760
            #     r => val = 458773
            #     t => val = 458775

            if event.code == 4:
                return

            print("unknown idk event: ", event)
            return

        # lock keys
        # e.g. caps_lock, num_lock etc
        if event.type == 17:
            # val = 1: on
            # val = 0: off

            # code = 0: num_lock
            # code = 1: caps_lock
            # there's probably more that I don't know about

            # when switching on
            # sent when the "key down" is sent

            # when switching off
            # sent when the "key up" is sent

            if event.value in (0, 1) and event.code in (0, 1):
                return

            print("unknown lock key: ", event)

        print("unknown event: ", event)

        return

    @classmethod
    def fetch_new_events(cls) -> None:
        """ called to add waiting events to the queue """
        r, w, x = select(cls._devices, [], [])

        for file_device in r:
            for raw_event in cls._devices[file_device].read():
                event = cls._convert_raw_event_to_event(raw_event)

                if event is None:
                    continue

                # print(raw_event)
                # print(event)
                cls.dispatch_event(event)
