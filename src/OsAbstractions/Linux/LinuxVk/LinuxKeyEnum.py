import os
import re

import evdev

from src.AbsVkEnum import VkEnum
from src.OsAbstractions.Linux.LinuxVk import LinuxKeyData


def _k_from_name(kernel_name, x_name=None, **kwargs):
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


# https://manpages.ubuntu.com/manpages/jammy/man5/keymaps.5.html


class LinuxKeyEnum(VkEnum, enum_item_type=LinuxKeyData):
    """
    a map from name to vk, i.e. the state is ignored
    """
    # <editor-fold desc="Mouse">
    mouse_left = _k_from_name("BTN_LEFT")
    mouse_middle = _k_from_name("BTN_MIDDLE")
    mouse_right = _k_from_name("BTN_RIGHT")

    mouse_forward = _k_from_name("BTN_FORWARD")
    mouse_back = _k_from_name("BTN_BACK")
    # </editor-fold>

    # <editor-fold desc="Modifiers">
    # https://superuser.com/questions/428945/defining-keyboard-shortcuts-involving-the-fn-key
    # NOTE: the "fn" key is a hardware level modifier
    # so the key is never sent to the os
    # i.e. pressing fn + f1 makes the keyboard directly send f13
    # instead of sending f1 that the os interoperates as f13

    alt = alt_l = _k_from_name("KEY_LEFTALT", "Alt")

    # alt_r is just alt_gr
    alt_gr = alt_r = _k_from_name("KEY_RIGHTALT", "AltGr")

    caps_lock = _k_from_name("KEY_CAPSLOCK", "Caps_Lock")

    # windows / command / super key
    cmd_l = cmd = _k_from_name("KEY_LEFTMETA", "Super_L")
    cmd_r = _k_from_name("KEY_RIGHTMETA", "Super_R")

    # this is true on my layout, probably not the case for you
    ctrl = _k_from_name("KEY_LEFTCTRL", "Control")
    ctrl_l = _k_from_name("KEY_LEFTCTRL", "Control_L")
    ctrl_r = _k_from_name("KEY_RIGHTCTRL", "Control_R")

    # this is true on my layout, probably not the case for you
    shift = _k_from_name("KEY_LEFTSHIFT", "Shift")
    shift_l = _k_from_name("KEY_LEFTSHIFT", "Shift_L")
    shift_r = _k_from_name("KEY_RIGHTSHIFT", "Shift_R")
    # </editor-fold>

    backspace = _k_from_name("SW_MUTE_DEVICE", "Delete", char="\b")
    delete = _k_from_name("KEY_DELETE", "Remove")
    enter = _k_from_name("KEY_ENTER", "Return", char="\n")
    space = _k_from_name("KEY_SPACE", "space", char=' ')
    tab = _k_from_name("KEY_TAB", "Tab", char='\t')

    f1 = _k_from_name("KEY_F1", "F1")
    f2 = _k_from_name("KEY_F2", "F2")
    f3 = _k_from_name("KEY_F3", "F3")
    f4 = _k_from_name("KEY_F4", "F4")
    f5 = _k_from_name("KEY_F5", "F5")
    f6 = _k_from_name("KEY_F6", "F6")
    f7 = _k_from_name("KEY_F7", "F7")
    f8 = _k_from_name("KEY_F8", "F8")
    f9 = _k_from_name("KEY_F9", "F9")
    f10 = _k_from_name("KEY_F10", "F10")
    f11 = _k_from_name("KEY_F11", "F11")
    f12 = _k_from_name("KEY_F12", "F12")
    f13 = _k_from_name("KEY_F13", "F13")
    f14 = _k_from_name("KEY_F14", "F14")
    f15 = _k_from_name("KEY_F15", "F15")
    f16 = _k_from_name("KEY_F16", "F16")
    f17 = _k_from_name("KEY_F17", "F17")
    f18 = _k_from_name("KEY_F18", "F18")
    f19 = _k_from_name("KEY_F19", "F19")
    f20 = _k_from_name("KEY_F20", "F20")

    esc = _k_from_name("KEY_ESC", "Escape")
    home = _k_from_name("KEY_HOME", "Find")
    end = _k_from_name("KEY_END", "Select")
    page_down = _k_from_name("KEY_PAGEDOWN", "Next")
    page_up = _k_from_name("KEY_PAGEUP", "Prior")

    insert = _k_from_name("KEY_INSERT", "Insert")
    menu = _k_from_name("KEY_MENU", "Menu")
    pause = _k_from_name("KEY_PAUSE", "Pause")
    print_screen = _k_from_name("KEY_SYSRQ", "Compose")
    scroll_lock = _k_from_name("KEY_SCROLLLOCK", "Scroll_Lock")

    # arrow keys
    up = _k_from_name("KEY_UP", "Up")
    down = _k_from_name("KEY_DOWN", "Down")
    left = _k_from_name("KEY_LEFT", "Left")
    right = _k_from_name("KEY_RIGHT", "Right")

    # <editor-fold desc="Media keys">
    media_volume_mute = _k_from_name("KEY_MUTE", "Mute")
    media_volume_down = _k_from_name("KEY_VOLUMEDOWN", "LowerVolume")
    media_volume_up = _k_from_name("KEY_VOLUMEUP", "RaiseVolume")

    media_play_pause = _k_from_name("KEY_PLAYPAUSE", "Play")
    media_previous = _k_from_name("KEY_PREVIOUSSONG", "Prev")
    media_next = _k_from_name("KEY_NEXTSONG", "Next")
    # </editor-fold>

    # <editor-fold desc="Numpad keys">
    num_lock = _k_from_name("KEY_NUMLOCK", "Num_Lock")

    kp_div = _k_from_name("KEY_KPSLASH", "KP_Divide")
    kp_mul = _k_from_name("KEY_KPASTERISK", "KP_Multiply")
    kp_minus = _k_from_name("KEY_KPMINUS", "KP_Subtract")
    kp_plus = _k_from_name("KEY_KPPLUS", "KP_Add")
    kp_dot = _k_from_name("KEY_KPDOT", "KP_Comma")
    kp_enter = _k_from_name("KEY_KPENTER", "KP_Enter")

    # for i in range(11):
    #     print(f"kp_{i} = _k_from_name("KEY_KP{i}", "KEY_KP{i}")")
    kp_0 = _k_from_name("KEY_KP0", "KP_0")
    kp_1 = _k_from_name("KEY_KP1", "KP_1")
    kp_2 = _k_from_name("KEY_KP2", "KP_2")
    kp_3 = _k_from_name("KEY_KP3", "KP_3")
    kp_4 = _k_from_name("KEY_KP4", "KP_4")
    kp_5 = _k_from_name("KEY_KP5", "KP_5")
    kp_6 = _k_from_name("KEY_KP6", "KP_6")
    kp_7 = _k_from_name("KEY_KP7", "KP_7")
    kp_8 = _k_from_name("KEY_KP8", "KP_8")
    kp_9 = _k_from_name("KEY_KP9", "KP_9")
    # </editor-fold>


# these are special since they affect the resulting char when pressed
# they also don't count to dead chars (ignored):
# pressing dead, dead => non-dead version of dead
# pressing dead, mod, dead => non-dead version of dead
# pressing dead, mod, mod, dead => non-dead version of dead
# pressing dead, non-mod, dead => dead + non-mod
LINUX_VK_MODIFIER_MAP: dict[int, LinuxKeyData] = {
    LinuxKeyEnum.alt.vk: LinuxKeyEnum.alt,
    LinuxKeyEnum.alt_l.vk: LinuxKeyEnum.alt,

    LinuxKeyEnum.alt_gr.vk: LinuxKeyEnum.alt_gr,

    LinuxKeyEnum.shift.vk: LinuxKeyEnum.shift,
    LinuxKeyEnum.shift_l.vk: LinuxKeyEnum.shift,
    LinuxKeyEnum.shift_r.vk: LinuxKeyEnum.shift,

    LinuxKeyEnum.ctrl.vk: LinuxKeyEnum.ctrl,
    LinuxKeyEnum.ctrl_l.vk: LinuxKeyEnum.ctrl,
    LinuxKeyEnum.ctrl_r.vk: LinuxKeyEnum.ctrl,

    # todo add more modifiers (like meta, fn)
    #  search up a list of all modifiers on xorg
    LinuxKeyEnum.caps_lock.vk: LinuxKeyEnum.caps_lock,
    LinuxKeyEnum.num_lock.vk: LinuxKeyEnum.num_lock,
}


_linux_enum_text_data = """    
    # <editor-fold desc="Mouse">
    mouse_left = _k_from_name("BTN_LEFT")
    mouse_middle = _k_from_name("BTN_MIDDLE")
    mouse_right = _k_from_name("BTN_RIGHT")

    mouse_forward = _k_from_name("BTN_FORWARD")
    mouse_back = _k_from_name("BTN_BACK")
    # </editor-fold>

    # <editor-fold desc="Modifiers">
    alt = _k_from_name("KEY_LEFTALT", "Alt_L")
    alt_l = _k_from_name("KEY_LEFTALT", "Alt_L")

    # alt_r is just alt_gr
    alt_r = _k_from_name("KEY_RIGHTALT", "Alt_R")
    alt_gr = _k_from_name("KEY_RIGHTALT", "Mode_switch")

    caps_lock = _k_from_name("KEY_CAPSLOCK", "Caps_Lock")

    # windows / command / super key
    cmd = _k_from_name("KEY_LEFTMETA", "Super_L")
    cmd_l = _k_from_name("KEY_LEFTMETA", "Super_L")
    cmd_r = _k_from_name("KEY_RIGHTMETA", "Super_R")

    ctrl = _k_from_name("KEY_LEFTCTRL", "Control_L")
    ctrl_l = _k_from_name("KEY_LEFTCTRL", "Control_L")
    ctrl_r = _k_from_name("KEY_RIGHTCTRL", "Control_R")

    shift = _k_from_name("KEY_LEFTSHIFT", "Shift_L")
    shift_l = _k_from_name("KEY_LEFTSHIFT", "Shift_L")
    shift_r = _k_from_name("KEY_RIGHTSHIFT", "Shift_R")
    # </editor-fold>

    backspace = _k_from_name("KEY_BACKSPACE", "BackSpace")
    delete = _k_from_name("KEY_DELETE", "Delete")
    enter = _k_from_name("KEY_ENTER", "Return", char="\n")
    space = _k_from_name("KEY_SPACE", "space", char=' ')
    tab = _k_from_name("KEY_TAB", "Tab", char='\t')

    f1 = _k_from_name("KEY_F1", "F1")
    f2 = _k_from_name("KEY_F2", "F2")
    f3 = _k_from_name("KEY_F3", "F3")
    f4 = _k_from_name("KEY_F4", "F4")
    f5 = _k_from_name("KEY_F5", "F5")
    f6 = _k_from_name("KEY_F6", "F6")
    f7 = _k_from_name("KEY_F7", "F7")
    f8 = _k_from_name("KEY_F8", "F8")
    f9 = _k_from_name("KEY_F9", "F9")
    f10 = _k_from_name("KEY_F10", "F10")
    f11 = _k_from_name("KEY_F11", "F11")
    f12 = _k_from_name("KEY_F12", "F12")
    f13 = _k_from_name("KEY_F13", "F13")
    f14 = _k_from_name("KEY_F14", "F14")
    f15 = _k_from_name("KEY_F15", "F15")
    f16 = _k_from_name("KEY_F16", "F16")
    f17 = _k_from_name("KEY_F17", "F17")
    f18 = _k_from_name("KEY_F18", "F18")
    f19 = _k_from_name("KEY_F19", "F19")
    f20 = _k_from_name("KEY_F20", "F20")

    esc = _k_from_name("KEY_ESC", "Escape")
    home = _k_from_name("KEY_HOME", "Home")
    end = _k_from_name("KEY_END", "End")
    page_down = _k_from_name("KEY_PAGEDOWN", "Page_Down")
    page_up = _k_from_name("KEY_PAGEUP", "Page_Up")

    insert = _k_from_name("KEY_INSERT", "Insert")
    menu = _k_from_name("KEY_MENU", "Menu")
    pause = _k_from_name("KEY_PAUSE", "Pause")
    print_screen = _k_from_name("KEY_SYSRQ", "Print")
    scroll_lock = _k_from_name("KEY_SCROLLLOCK", "Scroll_Lock")

    # arrow keys
    up = _k_from_name("KEY_UP", "Up")
    down = _k_from_name("KEY_DOWN", "Down")
    left = _k_from_name("KEY_LEFT", "Left")
    right = _k_from_name("KEY_RIGHT", "Right")

    # <editor-fold desc="Media keys">
    media_volume_mute = _k_from_name("KEY_MUTE", "Mute")
    media_volume_down = _k_from_name("KEY_VOLUMEDOWN", "LowerVolume")
    media_volume_up = _k_from_name("KEY_VOLUMEUP", "RaiseVolume")

    media_play_pause = _k_from_name("KEY_PLAYPAUSE", "Play")
    media_previous = _k_from_name("KEY_PREVIOUSSONG", "Prev")
    media_next = _k_from_name("KEY_NEXTSONG", "Next")
    # </editor-fold>

    # <editor-fold desc="Numpad keys">
    num_lock = _k_from_name("KEY_NUMLOCK", "Num_Lock")

    kp_div = _k_from_name("KEY_KPSLASH", "KP_Divide")
    kp_mul = _k_from_name("KEY_KPASTERISK", "KP_Multiply")
    kp_minus = _k_from_name("KEY_KPMINUS", "KP_Subtract")
    kp_plus = _k_from_name("KEY_KPPLUS", "KP_Add")
    kp_dot = _k_from_name("KEY_KPDOT", "KP_Comma")
    kp_enter = _k_from_name("KEY_KPENTER", "KP_Enter")

    # for i in range(11):
    #     print(f"kp_{i} = _k_from_name("KEY_KP{i}", "KEY_KP{i}")")
    kp_0 = _k_from_name("KEY_KP0", "KP_0")
    kp_1 = _k_from_name("KEY_KP1", "KP_1")
    kp_2 = _k_from_name("KEY_KP2", "KP_2")
    kp_3 = _k_from_name("KEY_KP3", "KP_3")
    kp_4 = _k_from_name("KEY_KP4", "KP_4")
    kp_5 = _k_from_name("KEY_KP5", "KP_5")
    kp_6 = _k_from_name("KEY_KP6", "KP_6")
    kp_7 = _k_from_name("KEY_KP7", "KP_7")
    kp_8 = _k_from_name("KEY_KP8", "KP_8")
    kp_9 = _k_from_name("KEY_KP9", "KP_9")
    # </editor-fold>
"""


def _get_x_vk_to_x_code():
    """
    Loads the keyboard layout.

    For simplicity, we call out to the ``dumpkeys`` binary. In the future,
    we may want to implement this ourselves.
    """

    data_path = os.path.join(
        os.path.dirname(__file__),
        "ExampleLayoutData.txt"
    )

    with open(data_path) as f:
        raw_data = f.read()

    keycode_re = re.compile(
        r"keycode\s+(\d+)\s+=(.*)")

    key_data = keycode_re.findall(raw_data)

    out = {}
    for keycode, names in key_data[::-1]:
        vk = int(keycode)

        out[vk] = names

    return out


def _helper():
    vk_to_names = _get_x_vk_to_x_code()

    out = []

    for full_line in _linux_enum_text_data.split("\n    "):
        line = full_line.strip()  # remove tab

        # line = repr(line)[1:-1].replace("//", "/")

        full_line = f"    {full_line}"

        if len(line) == 0:
            out.append(line)
            continue

        if line[0] in ("#", "\n", " "):
            out.append(full_line)
            continue

        line = (
            line
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )

        name, the_rest = line.split(" = ", 1)
        args = the_rest[len("_k_from_name("):-1].split(", ")

        kernel_name = args[0][1:-1]
        vk = getattr(evdev.ecodes, kernel_name)

        if len(args) == 1:
            x_name = None
        else:
            x_name = args[1][1:-1]

        rest_args = args[2:]

        # if x_name == kernel_name or x_name is None:
        #     inp = input(f"x_name for {vk} {kernel_name}")
        #     if inp:
        #         x_name = inp

        # convert kernel_name to to x_name
        possible_names = vk_to_names.get(vk, None)
        possible_names = [
            name for name in possible_names.split()
            if name != "VoidSymbol"
        ]

        while True:
            print()
            print()
            print("".join(f"{i}: {name}   " for i, name in enumerate(possible_names)))
            inp = input(f"x_name for {vk} {kernel_name}")
            if not inp:
                break

            if inp in [str(i) for i in range(len(possible_names))]:
                x_name = possible_names[int(inp)]
                break

            print("invalid choice")

        args = [f"\"{kernel_name}\""]
        if x_name:
            args.append(f"\"{x_name}\"")
        args += rest_args

        out.append(f"    {name} = _k_from_name({', '.join(args)})")

        if full_line.endswith("\n"):
            out.append("")

    print("\n".join(out))


def _vk_to_rest(vks):
    vk_to_names = _get_x_vk_to_x_code()

    rev_multidict: dict[int, set[int]] = {}
    for key, value in evdev.ecodes.ecodes.items():
        if value in rev_multidict.keys():
            rev_multidict[value].add(key)
        else:
            rev_multidict[value] = {key}

    out = []
    for vk in vks:
        # kernel_name = rev.get(vk)
        x_name = None

        possible_x_names = vk_to_names.get(vk, None)
        possible_x_names = [
            name for name in possible_x_names.split()
            if name != "VoidSymbol"
        ]

        while True:
            print()
            print()
            print("".join(f"{i}: {name}   " for i, name in enumerate(possible_x_names)))
            inp = input(f"x_name for {vk}")
            if not inp:
                break

            if inp in [str(i) for i in range(len(possible_x_names))]:
                x_name = possible_x_names[int(inp)]
                break

            print("invalid choice")

        possible_kernel_names = [*rev_multidict.get(vk, set())]

        kernel_name = None

        while True:
            print()
            print()
            print("".join(f"{i}: {name}   " for i, name in enumerate(possible_kernel_names)))
            inp = input(f"kernel_name for {vk} {x_name}")
            if not inp:
                break

            if inp in [str(i) for i in range(len(possible_kernel_names))]:
                kernel_name = possible_kernel_names[int(inp)]
                break

            print("invalid choice")

        part = []
        if kernel_name is not None:
            part.append(kernel_name)
        if x_name is not None:
            part.append(x_name)

        out.append(tuple(part))

    for line in out:
        print(", ".join([f"\"{line}\"" for line in line]))


if __name__ == '__main__':
    _vk_to_rest([
        14,
        111,
        102,
        107,
        109,
        104,
        99,
    ])
