from typing import Literal
import unicodedata

import evdev

from src.OsAbstractions.Abstract import AbsKeyboard
from src.OsAbstractions.Abstract.Keyboard import InvalidKeyException, StateData
from src.OsAbstractions.Linux.LinuxVk import LinuxKeyData, LinuxLayout, LinuxKeyEnum
from src.OsAbstractions.Linux.LinuxVk.LinuxKeyEnum import LINUX_MODIFIER_MAP


class LinuxKeyboard(AbsKeyboard):
    _pressed_keys = set()

    @classmethod
    def get_pressed_keys(cls) -> set[LinuxKeyData]:
        return cls._pressed_keys

    @classmethod
    def key_pressed(cls, key: LinuxKeyData) -> bool:
        return key in cls._pressed_keys

    @classmethod
    def add_pressed_keys(cls, *keys: LinuxKeyData):
        cls._pressed_keys.update(keys)

    @classmethod
    def remove_pressed_keys(cls, *keys: LinuxKeyData):
        cls._pressed_keys -= set(keys)

    _dev = evdev.UInput()

    @classmethod
    def queue_press(cls, vk: int, is_press: bool) -> None:
        """Queues a virtual key event.

        This method does not perform ``SYN``.

        :param int vk: The virtual key.

        :param bool is_press: Whether this is a press event.
        """
        cls._dev.write(evdev.ecodes.EV_KEY, vk, int(is_press))

    @classmethod
    def send_queued_presses(cls):
        cls._dev.syn()

    @classmethod
    def update_mapping(cls) -> None:
        """
        updates the internal keyboard key to vk_code mapping
        """
        raise NotImplementedError

    @classmethod
    def get_key_data_from_vk(cls, vk: int):
        return LinuxKeyData.from_vk(vk)

    @classmethod
    def get_key_data_from_char(cls, char: str) -> LinuxKeyData:
        vk, mod = LinuxLayout.for_char(char)
        # print(char, vk, mod, LinuxLayout.for_vk(vk, mod))
        # print(
        #     vk, mod,
        #     LinuxLayout._vk_table[vk],
        #     LinuxKeyEnum.alt_gr,
        #     LinuxLayout.for_vk(vk, {LinuxKeyEnum.alt_gr}),
        #     LinuxLayout.for_vk(vk, mod),
        # )

        return LinuxLayout.for_vk(vk, mod)

    @classmethod
    def get_vk_from_key_data(cls, key_data: LinuxKeyData) -> int:
        if key_data.vk is not None:
            return key_data.vk
        elif key_data.char is not None:
            return LinuxLayout.for_char(key_data.char)[0]
        else:
            raise InvalidKeyException(key_data)

    @classmethod
    def _get_req_mod_state(cls, raw_required_modifiers) \
            -> tuple[set[int], set[int]]:
        required_modifiers: set[int] = {x.vk for x in raw_required_modifiers}

        need_pressed = set()
        need_unpressed = set()

        # todo possibly move this to StateMgr
        rev_multidict: dict[int, set[int]] = {}
        for key, value in LINUX_MODIFIER_MAP.items():
            if value.vk in rev_multidict.keys():
                rev_multidict[value.vk].add(key.vk)
            else:
                rev_multidict[value.vk] = {key.vk}

        for generic_key, keys in rev_multidict.items():
            # this assumes the mod key is always the base form
            # so shift_l and not shift_r
            if generic_key in required_modifiers:
                need_pressed.add(generic_key)
            else:
                need_unpressed.update(keys)

        return need_pressed | required_modifiers, need_unpressed

    @classmethod
    def _calc_buttons_for_layout_char(cls, char: str) -> StateData:

        vk, raw_required_modifiers = LinuxLayout.for_char(char)

        key_data = LinuxLayout.for_vk(vk, raw_required_modifiers)

        need_pressed, need_unpressed = cls._get_req_mod_state(
            raw_required_modifiers
        )

        # if the char is a dead key then we have to press it
        # twice for it to show up
        return StateData(
            do=(vk, ) * (2 if key_data.is_dead else 1),
            need_pressed=need_pressed,
            need_unpressed=need_unpressed
        )

    @classmethod
    def _calc_buttons_for_unicode_char(cls, char: str) -> StateData:
        # consists of the chars: 0-9, a-f
        unicode_hex = hex(ord(char))[2:]

        do: list[int] = [
            LinuxLayout.for_char(char)[0]
            for char in f"u{unicode_hex}"
        ]

        do.append(LinuxKeyEnum.enter.vk)

        need_pressed, need_unpressed = cls._get_req_mod_state(
            {LinuxKeyEnum.shift, LinuxKeyEnum.ctrl}
        )

        return StateData(
            do=tuple(do),
            need_pressed=need_pressed,
            need_unpressed=need_unpressed,  # | {LinuxKeyEnum.ctrl},
        )

    @classmethod
    def calc_buttons_for_char(cls, char: str) -> StateData:
        """
        gets the buttons that needs to be pressed to get a specific char
        """
        if len(char) != 1:
            raise TypeError(f"len of char must be 1 {char=}")

        if LinuxLayout.char_in_layout(char):
            return cls._calc_buttons_for_layout_char(char)
        else:
            return cls._calc_buttons_for_unicode_char(char)

    _key_press_buffer_type: Literal["none", "unicode", "dead"] = "none"
    _key_press_buffer_data: [LinuxKeyData] = []

    @classmethod
    def clear_key_press_buffer(cls):
        """
        resets the saved press state

        so if you've pressed calc_resulting_chars_for_button("¨") and call this
        if you then press calc_resulting_chars_for_button("¨") again nothing happens
        you have to press it another time for it to become "¨¨" (windows)
        """
        cls._key_press_buffer_data = []
        cls._key_press_buffer_type = "none"

    @classmethod
    def calc_resulting_chars_for_button(cls, key_data: LinuxKeyData) -> str:
        """
        Calcs the resulting char for a button.
        A char might be a combination of several presses and held
        down buttons.

        button presses are possibly buffered if they affect the following
        pressed

        for example
        "¨" doesn't result in a character but changes the following one
        "¨" + "¨" => "¨"  (linux)
        "¨" + "o" => "ö"  (linux)

        one press can result in multiple characters like
        "¨" + "¨" => "¨¨"  (windows)
        """

        if cls._key_press_buffer_type == "none":
            if key_data.is_dead:
                cls._key_press_buffer_type = "dead"
                cls._key_press_buffer_data = []

                return ""

            # unicode
            if key_data == LinuxLayout.for_char("u"):
                need_pressed, need_unpressed = cls._get_req_mod_state(
                    {LinuxKeyEnum.shift, LinuxKeyEnum.ctrl}
                )

                # all correct keys pressed
                if not need_pressed and not need_unpressed:
                    cls._key_press_buffer_type = "unicode"
                    cls._key_press_buffer_data = []

            return key_data.char or ""

        if cls._key_press_buffer_type == "dead":
            combine_data: LinuxKeyData = cls._key_press_buffer_data[0]

            cls.clear_key_press_buffer()

            if key_data == LinuxKeyEnum.space:
                # dead + space => dead

                return combine_data.char or ""

            # try to combine
            combined = unicodedata.normalize(
                "NFC",
                key_data.char or "" + combine_data.combining or ""
            )

            if len(combined) != len(key_data.char or "") + len(combine_data.char or ""):
                # chars combined, return the combined version
                return combined

            # thy didn't return raw parts
            return combine_data.char or "" + key_data.char or ""

        if cls._key_press_buffer_type == "unicode":
            # find out what terminates a unicode char

            # convert to base form (@ => 2, A => a, etc)
            base_form = LinuxLayout.for_vk(key_data.vk, set())
            try:
                # can it represent hex?
                int(base_form.char, 16)

            except ValueError:
                # non valid hex char terminate unicode seq
                out = ""
                for button in cls._key_press_buffer_data:
                    out += button.char

                cls.clear_key_press_buffer()

                # probably handle enter differently since i don't think it
                # results in a \n char
                return chr(int(out, 16)) + cls.calc_resulting_chars_for_button(key_data)

            cls._key_press_buffer_data.append(base_form)
            return ""

        raise TypeError(f"cls._key_press_buffer_type has a invalid value \"{cls._key_press_buffer_type}\"")