from dataclasses import dataclass

from Mine.Events._BaseEvent import _BaseEvent
from Mine.ViritallKeys.VkEnum import KeyData


class KeyboardEvent:
    @dataclass
    class _BaseKeyboardEvent(_BaseEvent):
        raw: any
        key_data: KeyData
        char: str

    @dataclass
    class KeySend(_BaseKeyboardEvent):
        """
        This will happen when a key is pressed. But keeps being sent
        if it is continued to be held down.

        Good for text input, bad for detecting when a key is pressed
        """
        pass

    @dataclass
    class KeyDown(_BaseKeyboardEvent):
        """
        Called when a key is pressed
        """
        pass

    @dataclass
    class KeyUp(_BaseKeyboardEvent):
        """
        Called when a key is unpressed
        """
        pass

    event_types = KeyDown | KeyUp | KeySend

    _key_states = {}

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

