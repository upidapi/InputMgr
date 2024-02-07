import time
from select import select
import errno
import functools
import os
import re
import subprocess


from Mine.Events import any_event, MouseEvent, KeyboardEvent
from Mine.OsAbstractions.Abstract import EventApi

# from evdev.ecodes import keys, KEY, SYN, REL, ABS, EV_KEY, EV_REL, EV_ABS, EV_SYN
from evdev import ecodes
import evdev

from Mine.OsAbstractions.Linux import xorg_keysyms
from Mine.ViritallKeys.VkEnum import KeyData, VkEnum

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

class Layout(object):
    """
    A description of the keyboard layout.
    """
    #: A regular expression to parse keycodes in the dumpkeys output
    #:
    #: The groups are: keycode number, key names.
    KEYCODE_RE = re.compile(
        r"keycode\s+(\d+)\s+=(.*)")

    class Key(object):
        """ A key in a keyboard layout. """

        def __init__(self, normal, shifted, alt, alt_shifted):
            self._normal: LinuxKeyData = normal
            self._shifted: LinuxKeyData = shifted
            self._alt: LinuxKeyData = alt
            self._alt_shifted: LinuxKeyData = alt_shifted

        def __str__(self):
            return (
                f'<'
                f'normal: \"{self.normal}\", '
                f'shifted: \"{self.shifted}\", '
                f'alternative: \"{self.alt}\", '
                f'shifted alternative: \"{self.alt_shifted}\">'
            )

        __repr__ = __str__

        def _to_list(self):
            return [self.normal, self.shifted, self.alt, self.alt_shifted]

        def __iter__(self):
            return iter(self._to_list())

        def __getitem__(self, i):
            return self._to_list()[i]

        @property
        def normal(self):
            """ The normal key. """
            return self._normal

        @property
        def shifted(self):
            """ The shifted key. """
            return self._shifted

        @property
        def alt(self):
            """ The alternative key. """
            return self._alt

        @property
        def alt_shifted(self):
            """ The shifted alternative key. """
            return self._alt_shifted

    def __init__(self):
        self._vk_table = self._load()
        self._char_table = {}

        for vk, keys in self._vk_table.items():
            for key, modifier_keys in (
                    (keys.normal, set()),
                    (keys.shifted, {LinuxKeyEnum.shift}),
                    (keys.alt, {LinuxKeyEnum.alt_gr}),
                    (keys.alt_shifted, {LinuxKeyEnum.shift, LinuxKeyEnum.alt_gr}),
            ):
                key: KeyData

                if key is None:
                    continue

                if key.char is None:
                    continue

                self._char_table[key.char] = (
                    vk, modifier_keys
                )

    def for_vk(self, vk, modifiers):
        """Reads a key for a virtual key code and modifier state.

        :param int vk: The virtual key code.

        :param set modifiers: A set of modifiers.

        :return: a mapped key

        :raises KeyError: if ``vk`` is an unknown key
        """

        full_key = self._vk_table[vk]

        if LinuxKeyEnum.shift in modifiers:
            if LinuxKeyEnum.alt_gr in modifiers:
                return full_key.alt_shifted

            return full_key.shifted

        if LinuxKeyEnum.alt_gr in modifiers:
            return full_key.alt

        return full_key.normal

    def for_char(self, char):
        """Reads a virtual key code and modifier state for a character.

        :param str char: The character.

        :return: the tuple ``(vk, modifiers)``

        :raises KeyError: if ``vk`` is an unknown key
        """
        return self._char_table[char]

    @staticmethod
    def _parse(vk, name):
        """
        Parses a single key from the ``dumpkeys`` output.

        :param int vk: The key code.

        :param str name: The key name.

        :return: a key representation
        """
        try:
            # First try special keys...
            for key in LinuxKeyEnum:
                if key.value._x_name == name:
                    return key
        except StopIteration:
            # ...then characters...
            try:
                _, char = xorg_keysyms.SYMBOLS[name.lstrip('+')]
                if char:
                    return KeyData.from_char(char, vk=vk)
            except KeyError:
                pass

            # ...and finally special dumpkeys names
            try:
                return KeyData.from_char(
                    {
                        'one': '1',
                        'two': '2',
                        'three': '3',
                        'four': '4',
                        'five': '5',
                        'six': '6',
                        'seven': '7',
                        'eight': '8',
                        'nine': '9',
                        'zero': '0'
                    }[name])

            except KeyError:
                pass

    @functools.lru_cache()
    def _load(self):
        """
        Loads the keyboard layout.

        For simplicity, we call out to the ``dumpkeys`` binary. In the future,
        we may want to implement this ourselves.
        """
        result = {}

        raw_data = subprocess.check_output(
            ['dumpkeys', '--full-table', '--keys-only']
        ).decode('utf-8')

        key_data = self.KEYCODE_RE.findall(raw_data)

        for keycode, names in key_data:

            vk = int(keycode)
            keys = tuple(
                self._parse(vk, name)
                for name in names.split()[:4]
            )

            # if we don't find any keys, skip it
            if all(key is None for key in keys):
                continue

            result[vk] = self.Key(*keys)

        return result


class LinuxKeyData(KeyData):
    def __init__(self, x_name, kernel_name, **kwargs):
        super().__init__(**kwargs)
        self.x_name = x_name
        self.kernel_name = kernel_name


def k_from_name(x_name, kernel_name, **kwargs):
    """Creates a key from a name.

    :param str x_name: The X name.

    :param str kernel_name: The kernel name.

    :return: a key code
    """
    try:
        vk = getattr(evdev.ecodes, kernel_name)
    except AttributeError:
        vk = None
    return KeyData.from_vk(
        vk,
        data={
            "x_name": x_name,
            "kernel_name": kernel_name,
        },
        **kwargs,
    )


class LinuxKeyEnum(VkEnum, enum_item_type=LinuxKeyData):
    alt = k_from_name('Alt_L', 'KEY_LEFTALT')
    alt_l = k_from_name('Alt_L', 'KEY_LEFTALT')
    alt_r = k_from_name('Alt_R', 'KEY_RIGHTALT')
    alt_gr = k_from_name('Mode_switch', 'KEY_RIGHTALT')
    backspace = k_from_name('BackSpace', 'KEY_BACKSPACE')
    caps_lock = k_from_name('Caps_Lock', 'KEY_CAPSLOCK')
    cmd = k_from_name('Super_L', 'KEY_LEFTMETA')
    cmd_l = k_from_name('Super_L', 'KEY_LEFTMETA')
    cmd_r = k_from_name('Super_R', 'KEY_RIGHTMETA')
    ctrl = k_from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_l = k_from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_r = k_from_name('Control_R', 'KEY_RIGHTCTRL')
    delete = k_from_name('Delete', 'KEY_DELETE')
    down = k_from_name('Down', 'KEY_DOWN')
    end = k_from_name('End', 'KEY_END')
    enter = k_from_name('Return', 'KEY_ENTER')
    esc = k_from_name('Escape', 'KEY_ESC')
    f1 = k_from_name('F1', 'KEY_F1')
    f2 = k_from_name('F2', 'KEY_F2')
    f3 = k_from_name('F3', 'KEY_F3')
    f4 = k_from_name('F4', 'KEY_F4')
    f5 = k_from_name('F5', 'KEY_F5')
    f6 = k_from_name('F6', 'KEY_F6')
    f7 = k_from_name('F7', 'KEY_F7')
    f8 = k_from_name('F8', 'KEY_F8')
    f9 = k_from_name('F9', 'KEY_F9')
    f10 = k_from_name('F10', 'KEY_F10')
    f11 = k_from_name('F11', 'KEY_F11')
    f12 = k_from_name('F12', 'KEY_F12')
    f13 = k_from_name('F13', 'KEY_F13')
    f14 = k_from_name('F14', 'KEY_F14')
    f15 = k_from_name('F15', 'KEY_F15')
    f16 = k_from_name('F16', 'KEY_F16')
    f17 = k_from_name('F17', 'KEY_F17')
    f18 = k_from_name('F18', 'KEY_F18')
    f19 = k_from_name('F19', 'KEY_F19')
    f20 = k_from_name('F20', 'KEY_F20')
    home = k_from_name('Home', 'KEY_HOME')
    left = k_from_name('Left', 'KEY_LEFT')
    page_down = k_from_name('Page_Down', 'KEY_PAGEDOWN')
    page_up = k_from_name('Page_Up', 'KEY_PAGEUP')
    right = k_from_name('Right', 'KEY_RIGHT')
    shift = k_from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_l = k_from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_r = k_from_name('Shift_R', 'KEY_RIGHTSHIFT')
    space = k_from_name('space', 'KEY_SPACE', char=' ')
    tab = k_from_name('Tab', 'KEY_TAB', char='\t')
    up = k_from_name('Up', 'KEY_UP')

    media_play_pause = k_from_name('Play', 'KEY_PLAYPAUSE')
    media_volume_mute = k_from_name('Mute', 'KEY_MUTE')
    media_volume_down = k_from_name('LowerVolume', 'KEY_VOLUMEDOWN')
    media_volume_up = k_from_name('RaiseVolume', 'KEY_VOLUMEUP')
    media_previous = k_from_name('Prev', 'KEY_PREVIOUSSONG')
    media_next = k_from_name('Next', 'KEY_NEXTSONG')

    insert = k_from_name('Insert', 'KEY_INSERT')
    menu = k_from_name('Menu', 'KEY_MENU')
    num_lock = k_from_name('Num_Lock', 'KEY_NUMLOCK')
    pause = k_from_name('Pause', 'KEY_PAUSE')
    print_screen = k_from_name('Print', 'KEY_SYSRQ')
    scroll_lock = k_from_name('Scroll_Lock', 'KEY_SCROLLLOCK')


class LinuxEventApi(EventApi):
    _MODIFIER_MAP: dict[LinuxKeyEnum, LinuxKeyEnum] = {
        LinuxKeyEnum.alt.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_l.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_r.vk: LinuxKeyEnum.alt,
        LinuxKeyEnum.alt_gr.vk: LinuxKeyEnum.alt_gr,
        LinuxKeyEnum.shift.vk: LinuxKeyEnum.shift,
        LinuxKeyEnum.shift_l.vk: LinuxKeyEnum.shift,
        LinuxKeyEnum.shift_r.vk: LinuxKeyEnum.shift
    }

    # todo add typehint
    _devices = []
    _pressed_keys = set()
    _layout: Layout

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

    @classmethod
    def stop_listening(cls) -> None:
        for device in cls._devices:
            device.close()

    @classmethod
    def _get_modifier_keys(cls):
        modifier_keys = {None}
        for key in cls._pressed_keys:
            modifier_keys.add(
                cls._MODIFIER_MAP.get(
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
            cls._pressed_keys.add(event_code)
        elif event_code in cls._pressed_keys:
            cls._pressed_keys.remove(event_code)

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

        modifier_keys = cls._get_modifier_keys()
        key: LinuxKeyData
        try:
            # keycode = ecodes.keys[vk]
            key = cls._layout.for_vk(
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


try:
    #: The keyboard layout.
    LAYOUT = Layout()
except subprocess.CalledProcessError as e:
    raise ImportError('failed to load keyboard layout: "' + str(e) + (
        '"; please make sure you are root' if os.getuid() != 1 else '"'))
except OSError as e:
    raise ImportError({
        errno.ENOENT: 'the binary dumpkeys is not installed'}.get(
        e.args[0],
        str(e)))

if __name__ == '__main__':
    try:
        LinuxEventApi.start_listening()
        while True:
            LinuxEventApi.fetch_new_events()
            time.sleep(0.01)
    except BaseException as e:
        LinuxEventApi.stop_listening()
        raise e
