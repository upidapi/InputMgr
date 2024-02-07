import enum
import errno
import functools
import os
import re
import subprocess

import evdev

from Mine.OsAbstractions.Abstract import AbsKeyboard, KeyCode
from Mine.OsAbstractions.Linux import xorg_keysyms
from Mine.OsAbstractions.Linux.common import LinuxEventApi
from Mine.ViritallKeys.VkEnum import KeyData


class LinuxKeyCode(KeyCode):
    def __init__(self, x_name, kernel_name, **kwargs):
        super().__init__(**kwargs)
        self._x_name = x_name
        self._kernel_name = kernel_name


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
    return LinuxKeyCode.from_vk(
        vk, _x_name=x_name, _kernel_name=kernel_name, **kwargs)


class Key(enum.Enum):
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
            self._normal = normal
            self._shifted = shifted
            self._alt = alt
            self._alt_shifted = alt_shifted

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
                    (keys.shifted, {Key.shift}),
                    (keys.alt, {Key.alt_gr}),
                    (keys.alt_shifted, {Key.shift, Key.alt_gr}),
            ):

                if key is None:
                    continue

                char = key.value.char if isinstance(key, Key) else key.char

                if char is None:
                    continue

                self._char_table[char] = (
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

        if Key.shift in modifiers:
            if Key.alt_gr in modifiers:
                return full_key.alt_shifted

            return full_key.shifted

        if Key.alt_gr in modifiers:
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
            for key in Key:
                if key.value._x_name == name:
                    return key
        except StopIteration:
            # ...then characters...
            try:
                _, char = xorg_keysyms.SYMBOLS[name.lstrip('+')]
                if char:
                    return KeyCode.from_char(char, vk=vk)
            except KeyError:
                pass

            # ...and finally special dumpkeys names
            try:
                return KeyCode.from_char(
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


class LinuxKeyboard(AbsKeyboard):
    @classmethod
    def is_pressed(cls, vk_code: int) -> bool:
        raise NotImplementedError

    @classmethod
    def press(cls, vk_code: int, down: bool) -> None:
        raise NotImplementedError

    @classmethod
    def update_mapping(cls) -> None:
        """
        updates the internal keyboard key to vk_code mapping
        """
        raise NotImplementedError

    @classmethod
    def key_data_to_vk_code(cls, key_data: KeyData) -> int:
        """
        converts some data to a keycode e.g. "NP_0" to the keycode for numpad 0
        """
        raise NotImplementedError

    @classmethod
    def key_to_vk_code(cls, key_data: str) -> int:
        """
        converts a key from the keyboard e.g. "a", "#", "^" to a keycode
        """
        raise NotImplementedError


class ListenerMixin(object):
    """A mixin for *uinput* event listeners.

    Subclasses should set a value for :attr:`_EVENTS` and implement
    :meth:`_handle`.
    """
    #: The events for which to listen
    _EVENTS = tuple()

    def __init__(self):
        self._dev = self._device(
            DEVICE_PATHS or evdev.list_devices()
        )
        if SUPPRESS:
            self._dev.grab()

        self._layout = LAYOUT
        self._modifiers = set()

    def _run(self):
        for event in self._dev.read_loop():
            if event.type in self._EVENTS:
                self._handle(event)

    def _stop_platform(self):
        self._dev.close()

    def _device(self, paths):
        """Attempts to load a readable keyboard device.

        :param paths: A list of paths.

        :return: a compatible device
        """
        dev, count = None, 0
        for path in paths:
            # Open the device
            try:
                next_dev = evdev.InputDevice(path)
            except OSError:
                continue

            # Does this device provide more handled event codes?
            capabilities = next_dev.capabilities()
            next_count = sum(
                len(codes)
                for event, codes in capabilities.items()
                if event in self._EVENTS)
            if next_count > count:
                dev = next_dev
                count = next_count
            else:
                next_dev.close()

        if dev is None:
            raise OSError('no keyboard device available')
        else:
            return dev

    _EVENTS = (
        evdev.ecodes.EV_KEY,)

    #: A
    _MODIFIERS = {
        Key.alt.value.vk: Key.alt,
        Key.alt_l.value.vk: Key.alt,
        Key.alt_r.value.vk: Key.alt,
        Key.alt_gr.value.vk: Key.alt_gr,
        Key.shift.value.vk: Key.shift,
        Key.shift_l.value.vk: Key.shift,
        Key.shift_r.value.vk: Key.shift}

    def _handle(self, event):
        """
        Handles a single event.

        This method should call one of the registered event callbacks.

        :param event: The event.
        """
        is_press = event.value in (KeyEvent.key_down, KeyEvent.key_hold)
        vk = event.code

        # Update the modifier state
        if vk in self._MODIFIERS:
            modifier = self._MODIFIERS[vk]
            if is_press:
                self._modifiers.add(modifier)
            elif modifier in self._modifiers:
                self._modifiers.remove(modifier)

        # Attempt to map the virtual key code to a key
        try:
            key = self._layout.for_vk(vk, self._modifiers)
        except KeyError:
            try:
                key = next(
                    key
                    for key in Key
                    if key.value.vk == vk)
            except StopIteration:
                key = KeyCode.from_vk(vk)

        if is_press:
            self.on_press(key)
        else:
            self.on_release(key)


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
