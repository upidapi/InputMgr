import errno
import functools
import os
import re
import subprocess

from src.OsAbstractions.Linux.LinuxVk import xorg_keysyms, LinuxKeyEnum, LinuxKeyData

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
        # this uses names to find the keys
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

        # things with "incorrect" names
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
        if __debug__:
            # for debug when you don't have root
            data_path = os.path.join(
                os.path.dirname(__file__),
                "ExampleLayoutData.txt"
            )

            with open(data_path) as f:
                raw_data = f.read()
        else:
            raw_data = subprocess.check_output(
                ['dumpkeys', '--full-table', '--keys-only']
            ).decode('utf-8')

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
