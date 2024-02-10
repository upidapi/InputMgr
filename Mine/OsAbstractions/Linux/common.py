import errno
import functools
import os
import re
import subprocess

# from evdev.ecodes import keys, KEY, SYN, REL, ABS, EV_KEY, EV_REL, EV_ABS, EV_SYN
import evdev

from Mine.OsAbstractions.Linux import xorg_keysyms
from Mine.ViritallKeys.VkEnum import KeyData, VkEnum


class LinuxKeyData(KeyData):
    def __init__(self, x_name=None, **kwargs):
        super().__init__(**kwargs)
        self.x_name = x_name
        # self.kernel_name = kernel_name


def _k_from_name(x_name, kernel_name, **kwargs):
    """Creates a key from a name.

    :param str x_name: The X name.

    :param str kernel_name: The kernel name.

    :return: a key code
    """
    try:
        vk = getattr(evdev.ecodes, kernel_name)
    except AttributeError:
        vk = None
    return LinuxKeyData.from_vk(
        vk,
        x_name=x_name,
        # kernel_name=kernel_name,
        **kwargs,
    )


class LinuxKeyEnum(VkEnum, enum_item_type=LinuxKeyData):
    alt = _k_from_name('Alt_L', 'KEY_LEFTALT')
    alt_l = _k_from_name('Alt_L', 'KEY_LEFTALT')
    alt_r = _k_from_name('Alt_R', 'KEY_RIGHTALT')
    alt_gr = _k_from_name('Mode_switch', 'KEY_RIGHTALT')
    backspace = _k_from_name('BackSpace', 'KEY_BACKSPACE')
    caps_lock = _k_from_name('Caps_Lock', 'KEY_CAPSLOCK')
    cmd = _k_from_name('Super_L', 'KEY_LEFTMETA')
    cmd_l = _k_from_name('Super_L', 'KEY_LEFTMETA')
    cmd_r = _k_from_name('Super_R', 'KEY_RIGHTMETA')
    ctrl = _k_from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_l = _k_from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_r = _k_from_name('Control_R', 'KEY_RIGHTCTRL')
    delete = _k_from_name('Delete', 'KEY_DELETE')
    down = _k_from_name('Down', 'KEY_DOWN')
    end = _k_from_name('End', 'KEY_END')
    enter = _k_from_name('Return', 'KEY_ENTER')
    esc = _k_from_name('Escape', 'KEY_ESC')
    f1 = _k_from_name('F1', 'KEY_F1')
    f2 = _k_from_name('F2', 'KEY_F2')
    f3 = _k_from_name('F3', 'KEY_F3')
    f4 = _k_from_name('F4', 'KEY_F4')
    f5 = _k_from_name('F5', 'KEY_F5')
    f6 = _k_from_name('F6', 'KEY_F6')
    f7 = _k_from_name('F7', 'KEY_F7')
    f8 = _k_from_name('F8', 'KEY_F8')
    f9 = _k_from_name('F9', 'KEY_F9')
    f10 = _k_from_name('F10', 'KEY_F10')
    f11 = _k_from_name('F11', 'KEY_F11')
    f12 = _k_from_name('F12', 'KEY_F12')
    f13 = _k_from_name('F13', 'KEY_F13')
    f14 = _k_from_name('F14', 'KEY_F14')
    f15 = _k_from_name('F15', 'KEY_F15')
    f16 = _k_from_name('F16', 'KEY_F16')
    f17 = _k_from_name('F17', 'KEY_F17')
    f18 = _k_from_name('F18', 'KEY_F18')
    f19 = _k_from_name('F19', 'KEY_F19')
    f20 = _k_from_name('F20', 'KEY_F20')
    home = _k_from_name('Home', 'KEY_HOME')
    left = _k_from_name('Left', 'KEY_LEFT')
    page_down = _k_from_name('Page_Down', 'KEY_PAGEDOWN')
    page_up = _k_from_name('Page_Up', 'KEY_PAGEUP')
    right = _k_from_name('Right', 'KEY_RIGHT')
    shift = _k_from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_l = _k_from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_r = _k_from_name('Shift_R', 'KEY_RIGHTSHIFT')
    space = _k_from_name('space', 'KEY_SPACE', char=' ')
    tab = _k_from_name('Tab', 'KEY_TAB', char='\t')
    up = _k_from_name('Up', 'KEY_UP')

    media_play_pause = _k_from_name('Play', 'KEY_PLAYPAUSE')
    media_volume_mute = _k_from_name('Mute', 'KEY_MUTE')
    media_volume_down = _k_from_name('LowerVolume', 'KEY_VOLUMEDOWN')
    media_volume_up = _k_from_name('RaiseVolume', 'KEY_VOLUMEUP')
    media_previous = _k_from_name('Prev', 'KEY_PREVIOUSSONG')
    media_next = _k_from_name('Next', 'KEY_NEXTSONG')

    insert = _k_from_name('Insert', 'KEY_INSERT')
    menu = _k_from_name('Menu', 'KEY_MENU')
    num_lock = _k_from_name('Num_Lock', 'KEY_NUMLOCK')
    pause = _k_from_name('Pause', 'KEY_PAUSE')
    print_screen = _k_from_name('Print', 'KEY_SYSRQ')
    scroll_lock = _k_from_name('Scroll_Lock', 'KEY_SCROLLLOCK')


class LinuxLayout:
    """
    A description of the keyboard layout.
    """
    #: A regular expression to parse keycodes in the dumpkeys output
    #:
    #: The groups are: keycode number, key names.
    KEYCODE_RE = re.compile(
        r"keycode\s+(\d+)\s+=(.*)")

    class Key:
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

    _vk_table: dict[int, Key]
    _char_table: dict[str, (Key, set[Key])]

    @staticmethod
    def _parse_raw_key(vk, name):
        """
        Parses a single key from the ``dumpkeys`` output.

        :param int vk: The key code.

        :param str name: The key name.

        :return: a key representation
        """
        # First try special keys...
        for key in LinuxKeyEnum:
            key: LinuxKeyData
            if key.x_name == name:
                return key

        # ...then characters...
        _, char = xorg_keysyms.SYMBOLS.get(
            name.lstrip('+'),
            (None, None)
        )

        if char:
            return KeyData.from_char(char, vk=vk)

        mapped_name = {
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
            }.get(name, None)

        if mapped_name:
            return LinuxKeyData.from_char(
                mapped_name
            )

    @classmethod
    @functools.lru_cache()
    def _load_vk_table(cls):
        """
        Loads the keyboard layout.

        For simplicity, we call out to the ``dumpkeys`` binary. In the future,
        we may want to implement this ourselves.
        """
        result = {}
        data_path = os.path.join(
            os.path.dirname(__file__),
            "ExampleData.txt"
        )

        # todo get running ths as root working
        # raw_data = subprocess.check_output(
        #     ['dumpkeys', '--full-table', '--keys-only']
        # ).decode('utf-8')
        with open(data_path) as f:
            raw_data = f.read()

        key_data = cls.KEYCODE_RE.findall(raw_data)

        for keycode, names in key_data:

            vk = int(keycode)
            keys = tuple(
                cls._parse_raw_key(vk, name)
                # todo possibly add the other 4 things too
                for name in names.split()[:4]
            )

            # if we don't find any keys, skip it
            if all(key is None for key in keys):
                continue

            result[vk] = cls.Key(*keys)

        return result

    @classmethod
    def load_char_table(cls):
        cls._vk_table = cls._load_vk_table()
        cls._char_table = {}

        for vk, keys in cls._vk_table.items():
            for key, modifier_keys in (
                    (keys.normal, set()),
                    (keys.shifted, {LinuxKeyEnum.shift}),
                    (keys.alt, {LinuxKeyEnum.alt_gr}),
                    (keys.alt_shifted, {LinuxKeyEnum.shift, LinuxKeyEnum.alt_gr}),
            ):
                key: LinuxKeyData

                if key is None:
                    continue

                if key.char is None:
                    continue

                cls._char_table[key.char] = (
                    vk, modifier_keys
                )

    @classmethod
    def for_vk(cls, vk, modifiers):
        """Reads a key for a virtual key code and modifier state.

        :param int vk: The virtual key code.

        :param set modifiers: A set of modifiers.

        :return: a mapped key

        :raises KeyError: if ``vk`` is an unknown key
        """

        full_key = cls._vk_table[vk]

        if LinuxKeyEnum.shift in modifiers:
            if LinuxKeyEnum.alt_gr in modifiers:
                return full_key.alt_shifted

            return full_key.shifted

        if LinuxKeyEnum.alt_gr in modifiers:
            return full_key.alt

        return full_key.normal

    @classmethod
    def for_char(cls, char: str) -> (Key, set[Key]):
        """Reads a virtual key code and modifier state for a character.

        :param str char: The character.

        :return: the tuple ``(vk, modifiers)``

        :raises KeyError: if ``vk`` is an unknown key
        """
        return cls._char_table[char]


def _init_layout():
    try:
        #: The keyboard layout.
        LinuxLayout.load_char_table()
    except subprocess.CalledProcessError as e:
        raise ImportError('failed to load keyboard layout: "' + str(e) + (
            '"; please make sure you are root' if os.getuid() != 1 else '"'))
    except OSError as e:
        raise ImportError({
            errno.ENOENT: 'the binary dumpkeys is not installed'}.get(
            e.args[0],
            str(e)))


_init_layout()


print("finish")

