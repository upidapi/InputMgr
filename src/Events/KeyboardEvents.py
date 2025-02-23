from dataclasses import dataclass

from src.AbsVkEnum import KeyData
from src.Events._BaseEvent import _BaseEvent


# _key_states = {}
#
# @staticmethod
# def parse_raw_event(event: RawKeyboardEvent) -> [event_types]:
#     general_args = {
#         "time": event.time,
#
#         "raw": event,
#
#         "vk_code": event.vk_code,
#         "unicode": event.unicode,
#
#         "is_extended": bool(event.is_extended()),
#         "is_injected": bool(event.is_injected()),
#         "is_alt": bool(event.is_alt()),
#         "is_transition": bool(event.is_transition()),
#     }
#
#     if event.message in [HookConstants.WM_KEYDOWN, HookConstants.WM_SYSKEYDOWN]:
#         key_state = KeyboardEvent._key_states.get(event.vk_code)
#         KeyboardEvent._key_states[event.vk_code] = "down"
#
#         return [
#             KeyboardEvent.KeySend(**general_args),
#             *(
#                 []
#                 if key_state == "down" else
#                 [KeyboardEvent.KeyDown(**general_args)]
#             )
#         ]
#
#     elif event.message in [HookConstants.WM_KEYUP, HookConstants.WM_SYSKEYUP]:
#         KeyboardEvent._key_states[event.vk_code] = "up"
#
#         return [KeyboardEvent.KeyUp(**general_args)]
#
#     else:
#         raise TypeError(
#             f"invalid message type "
#             f"{event.message:=}, "
#             f"message_name={HookConstants.msg_to_name(event.message)}"
#         )


@dataclass(frozen=True)
class _BaseKeyboardEvent(_BaseEvent):
    key_data: KeyData


@dataclass(frozen=True)
class KeySend(_BaseKeyboardEvent):
    """
    This will happen when a key is pressed. But keeps being sent
    if it is continued to be held down.

    Good for text input, bad for detecting when a key is pressed
    """

    # the actual char the press results in
    # for example if you press a dead key once noting happens
    # but if you press it again it gets typed

    # ¨ => ""
    # ¨ + ¨ => ¨ (linux)
    # ¨ + ¨ => ¨¨ (windows)
    chars: str


@dataclass(frozen=True)
class KeyDown(_BaseKeyboardEvent):
    """
    Called when a key is pressed
    """


@dataclass(frozen=True)
class KeyUp(_BaseKeyboardEvent):
    """
    Called when a key is unpressed
    """


# we have to do this to make dataclasses work (in pycharm)
class KeyboardEvent:
    KeySend = KeySend
    KeyDown = KeyDown
    KeyUp = KeyUp

    event_types = KeyDown | KeyUp | KeySend
