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


LINUX_MODIFIER_MAP: dict[LinuxKeyData, LinuxKeyData] = {
    LinuxKeyEnum.alt: LinuxKeyEnum.alt,
    LinuxKeyEnum.alt_l: LinuxKeyEnum.alt,

    LinuxKeyEnum.alt_gr: LinuxKeyEnum.alt_gr,

    LinuxKeyEnum.shift: LinuxKeyEnum.shift,
    LinuxKeyEnum.shift_l: LinuxKeyEnum.shift,
    LinuxKeyEnum.shift_r: LinuxKeyEnum.shift,

    # todo add more modifiers
    LinuxKeyEnum.ctrl: LinuxKeyEnum.ctrl,
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


def _helper():
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

        if x_name == kernel_name or x_name is None:
            inp = input(f"x_name for {vk} {kernel_name}")
            if inp:
                x_name = inp

        args = [f"\"{kernel_name}\""]
        if x_name:
            args.append(f"\"{x_name}\"")
        args += rest_args

        out.append(f"    {name} = _k_from_name({', '.join(args)})")

        if full_line.endswith("\n"):
            out.append("")

    print("\n".join(out))


if __name__ == '__main__':
    _helper()
