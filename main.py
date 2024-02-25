import pexpect

# https://github.com/x2es/bt-dualboot
# to make it work on windows and linux without repairing

from src import Keyboard, Hotkey

# the macro keys are 183, 184, 185, 186


class BthConnectHotkey:
    HP_BTH_ADDR = "AC:80:0A:2E:81:6A"
    HOTKEY = Hotkey(183)

    def __init__(self):
        self.bth_ctl_instance = pexpect.spawn(
            "bluetoothctl", echo=False
        )

        Keyboard.bind_to_hotkey(self._connect_bth, BthConnectHotkey.HOTKEY)

    def _connect_bth(self):
        print("Connecting to bluetooth headphones...")
        self.bth_ctl_instance.send(
            f"connect {BthConnectHotkey.HP_BTH_ADDR}\n"
        )


class SwitchFocusHotkey:
    # deps: alsa-utils

    HOTKEY = Hotkey(184)

    def __init__(self):
        self.bth_ctl_instance = pexpect.spawn(
            "bluetoothctl", echo=False
        )

        Keyboard.bind_to_hotkey(self._connect_bth, BthConnectHotkey.HOTKEY)

    def _connect_bth(self):
        print("Connecting to bluetooth headphones...")
        self.bth_ctl_instance.send(
            f"connect {BthConnectHotkey.HP_BTH_ADDR}\n"
        )


BthConnectHotkey()
