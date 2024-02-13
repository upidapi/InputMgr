import errno
import functools
import os
import re
import subprocess

# from evdev.ecodes import keys, KEY, SYN, REL, ABS, EV_KEY, EV_REL, EV_ABS, EV_SYN
import evdev

from Mine.OsAbstractions.Linux import xorg_keysyms
from Mine.OsAbstractions.Linux.xorg_keysyms import unicode_char_to_name, name_to_symbolic_key
from Mine.ViritallKeys.VkEnum import KeyData, VkEnum


class LinuxKeyData(KeyData):
    def __init__(self, x_name=None, **kwargs):
        super().__init__(**kwargs)

        # x_name doesn't seam to have any reason behind the name
        # it looks like it's basically only an id / name tag
        self.x_name = x_name
        # self.kernel_name = kernel_name

    def _calc_is_dead(self):
        try:
            name = unicode_char_to_name(self.combining)
            symbolic_key = name_to_symbolic_key(name)

            if symbolic_key:
                return True
            else:
                return False
        except KeyError:
            pass


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
    # <editor-fold desc="Mouse">
    mouse_left = _k_from_name('BTN_LEFT', 'BTN_LEFT')
    mouse_middle = _k_from_name('BTN_MIDDLE', 'BTN_MIDDLE')
    mouse_right = _k_from_name('BTN_RIGHT', 'BTN_RIGHT')

    mouse_forward = _k_from_name('BTN_FORWARD', 'BTN_FORWARD')
    mouse_back = _k_from_name('BTN_BACK', 'BTN_BACK')
    # </editor-fold>

    # <editor-fold desc="Modifiers">
    alt = _k_from_name('Alt_L', 'KEY_LEFTALT')
    alt_l = _k_from_name('Alt_L', 'KEY_LEFTALT')

    # alt_r is just alt_gr
    alt_r = _k_from_name('Alt_R', 'KEY_RIGHTALT')
    alt_gr = _k_from_name('Mode_switch', 'KEY_RIGHTALT')

    caps_lock = _k_from_name('Caps_Lock', 'KEY_CAPSLOCK')

    # windows / command / super key
    cmd = _k_from_name('Super_L', 'KEY_LEFTMETA')
    cmd_l = _k_from_name('Super_L', 'KEY_LEFTMETA')
    cmd_r = _k_from_name('Super_R', 'KEY_RIGHTMETA')

    ctrl = _k_from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_l = _k_from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_r = _k_from_name('Control_R', 'KEY_RIGHTCTRL')

    shift = _k_from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_l = _k_from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_r = _k_from_name('Shift_R', 'KEY_RIGHTSHIFT')
    # </editor-fold>

    backspace = _k_from_name('BackSpace', 'KEY_BACKSPACE')
    delete = _k_from_name('Delete', 'KEY_DELETE')
    enter = _k_from_name('Return', 'KEY_ENTER', char="\n")
    space = _k_from_name('space', 'KEY_SPACE', char=' ')
    tab = _k_from_name('Tab', 'KEY_TAB', char='\t')

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

    esc = _k_from_name('Escape', 'KEY_ESC')
    home = _k_from_name('Home', 'KEY_HOME')
    end = _k_from_name('End', 'KEY_END')
    page_down = _k_from_name('Page_Down', 'KEY_PAGEDOWN')
    page_up = _k_from_name('Page_Up', 'KEY_PAGEUP')

    insert = _k_from_name('Insert', 'KEY_INSERT')
    menu = _k_from_name('Menu', 'KEY_MENU')
    pause = _k_from_name('Pause', 'KEY_PAUSE')
    print_screen = _k_from_name('Print', 'KEY_SYSRQ')
    scroll_lock = _k_from_name('Scroll_Lock', 'KEY_SCROLLLOCK')

    # arrow keys
    up = _k_from_name('Up', 'KEY_UP')
    down = _k_from_name('Down', 'KEY_DOWN')
    left = _k_from_name('Left', 'KEY_LEFT')
    right = _k_from_name('Right', 'KEY_RIGHT')

    # <editor-fold desc="Media keys">
    media_volume_mute = _k_from_name('Mute', 'KEY_MUTE')
    media_volume_down = _k_from_name('LowerVolume', 'KEY_VOLUMEDOWN')
    media_volume_up = _k_from_name('RaiseVolume', 'KEY_VOLUMEUP')

    media_play_pause = _k_from_name('Play', 'KEY_PLAYPAUSE')
    media_previous = _k_from_name('Prev', 'KEY_PREVIOUSSONG')
    media_next = _k_from_name('Next', 'KEY_NEXTSONG')
    # </editor-fold>

    # <editor-fold desc="Numpad keys">
    # todo add keypad/numpad keys
    num_lock = _k_from_name('Num_Lock', 'KEY_NUMLOCK')
    # </editor-fold>


"""

plain   keycode 108 = Down            
        shift   keycode 108 = Down            
        altgr   keycode 108 = Down            
        shift   altgr   keycode 108 = VoidSymbol      
        control keycode 108 = Down            
        shift   control keycode 108 = Down            
        altgr   control keycode 108 = Down            
        shift   altgr   control keycode 108 = VoidSymbol      
        alt     keycode 108 = Down            
        shift   alt     keycode 108 = VoidSymbol      
        altgr   alt     keycode 108 = VoidSymbol      
        shift   altgr   alt     keycode 108 = VoidSymbol      
        control alt     keycode 108 = Down            

plain   keycode 109 = Next            
        shift   keycode 109 = Scroll_Forward  
        altgr   keycode 109 = Next            
        shift   altgr   keycode 109 = VoidSymbol      
        control keycode 109 = Next            
        shift   control keycode 109 = Next            
        altgr   control keycode 109 = Next            
        shift   altgr   control keycode 109 = VoidSymbol      
        alt     keycode 109 = Next            
        shift   alt     keycode 109 = VoidSymbol      
        altgr   alt     keycode 109 = VoidSymbol      
        shift   altgr   alt     keycode 109 = VoidSymbol      
        control alt     keycode 109 = Next            

plain   keycode 110 = Insert          
        shift   keycode 110 = Insert          
        altgr   keycode 110 = Insert          
        shift   altgr   keycode 110 = VoidSymbol      
        control keycode 110 = Insert          
        shift   control keycode 110 = Insert          
        altgr   control keycode 110 = Insert          
        shift   altgr   control keycode 110 = VoidSymbol      
        alt     keycode 110 = Insert          
        shift   alt     keycode 110 = VoidSymbol      
        altgr   alt     keycode 110 = VoidSymbol      
        shift   altgr   alt     keycode 110 = VoidSymbol      
        control alt     keycode 110 = Insert            
"""

"""
dumpkeys -S 8 --keys-only

plain   
        shift   
        altgr   
        shift   altgr   
        control 
        shift   control 
        altgr   control 
        shift   altgr   control 
        alt     
        shift   alt     
        altgr   alt     
        shift   altgr   alt     
        control alt     

plain   
        shift   
        altgr   
        shift   altgr   
        control 
        shift   control 
        altgr   control 
        shift   altgr   control 
        alt     
        shift   alt     
        altgr   alt     
        shift   altgr   alt     
        control alt     

plain   
        shift   
        altgr   
        shift   altgr   
        control 
        shift   control 
        altgr   control 
        shift   altgr   control 
        alt     
        shift   alt     
        altgr   alt     
        shift   altgr   alt     
        control alt     

"""


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

    _vk_table: dict[int, Key] = {}
    _char_table: dict[str, tuple[int, set[LinuxKeyData]]] = {}

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
            return LinuxKeyData.from_char(char, vk=vk)

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
                mapped_name, vk=vk
            )

    @classmethod
    @functools.lru_cache()
    def _load_vk_table(cls):
        """
        Loads the keyboard layout.

        For simplicity, we call out to the ``dumpkeys`` binary. In the future,
        we may want to implement this ourselves.
        """
        # for debug when you don't have root
        data_path = os.path.join(
            os.path.dirname(__file__),
            "ExampleData.txt"
        )
        with open(data_path) as f:
            raw_data = f.read()

        # raw_data = subprocess.check_output(
        #     ['dumpkeys', '--full-table', '--keys-only']
        # ).decode('utf-8')

        key_data = cls.KEYCODE_RE.findall(raw_data)

        for keycode, names in key_data[::-1]:

            vk = int(keycode)
            keys = tuple(
                cls._parse_raw_key(vk, name)
                # todo possibly add the other 4 things too
                for name in names.split()[:4]
            )

            # if we don't find any keys, skip it
            if all(key is None for key in keys):
                continue

            cls._vk_table[vk] = cls.Key(*keys)

    @classmethod
    def load_char_table(cls):
        cls._load_vk_table()

        for vk, keys in cls._vk_table.items():
            for key, modifier_keys in (
                    (keys.normal, set()),
                    (keys.shifted, {LinuxKeyEnum.shift}),
                    (keys.alt, {LinuxKeyEnum.alt_gr}),
                    (keys.alt_shifted, {LinuxKeyEnum.shift, LinuxKeyEnum.alt_gr}),
            )[::-1]:
                key: LinuxKeyData

                if key is None:
                    continue

                if key.char is None:
                    continue

                cls._char_table[key.char] = (
                    vk, modifier_keys
                )

        # print(cls._char_table)

    @classmethod
    def for_vk(cls, vk, modifiers: set[LinuxKeyData]):
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
    def for_char(cls, char: str) -> tuple[int, set[LinuxKeyData]]:
        """Reads a virtual key code and modifier state for a character.

        :param str char: The character.

        :return: the tuple ``(vk, modifiers)``

        :raises KeyError: if ``vk`` is an unknown key
        """
        return cls._char_table[char]

    @classmethod
    def char_in_layout(cls, char: str) -> bool:
        return char in cls._char_table


def _init_layout():
    try:
        #: The keyboard layout.
        LinuxLayout.load_char_table()
    except subprocess.CalledProcessError as e:
        # todo i think the 1 should be a 0
        #   (id for root is 0)
        raise ImportError('failed to load keyboard layout: "' + str(e) + (
            '"; please make sure you are root' if os.getuid() != 1 else '"'))
    except OSError as e:
        raise ImportError({
            errno.ENOENT: 'the binary dumpkeys is not installed'}.get(
            e.args[0],
            str(e)))


_init_layout()
