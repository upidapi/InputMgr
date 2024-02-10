from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from Mine.Events._BaseEvent import _BaseEvent


@dataclass
class _BaseMouseEvent(_BaseEvent):
    # pos of the mouse
    pos: (int, int)


@dataclass
class _Move(_BaseMouseEvent):
    # mouse move since last event
    delta: (int, int)


_button_type = Literal["left", "middle", "right", "forward", "backward"]


@dataclass
class _Click(_BaseMouseEvent):
    button: _button_type


@dataclass
class _UnClick(_BaseMouseEvent):
    button: _button_type


@dataclass
class _Scroll(_BaseMouseEvent):
    # todo possibly use a dx, dy format to be able to handle
    #   variable size scrolls along with sideways scrolls
    direction: Literal["up", "down"]


_event_types = _Move | _Click | _UnClick | _Scroll

dict.update()

# @staticmethod
# def parse_raw_event(event: RawMouseEvent) -> [event_types]:
#     general_args = {
#         "time": event.time,
#         "pos": event.position,
#         "injected": event.injected,
#         "raw": event,
#     }
#
#     if event.message in [HookConstants.side_button_down, HookConstants.side_button_up]:
#         button: MouseEvent.button_type
#         if event.data == 0x20000:
#             button = "forward"
#         elif event.data == 0x10000:
#             button = "backward"
#         else:
#             raise TypeError(f"invalid {event.data:=}")
#
#         if event.message == HookConstants.side_button_down:
#             return [MouseEvent.Click(
#                 **general_args,
#                 button=button
#             )]
#
#         elif event.message == HookConstants.side_button_up:
#             return [MouseEvent.UnClick(
#                 **general_args,
#                 button=button
#             )]
#
#         else:
#             raise TypeError(f"invalid {event.message:=}")
#
#     if event.data:
#         direction: Literal["up", "down"]
#
#         if event.data == 0x780000:
#             direction = "up"
#         elif event.data == -0x780000:
#             direction = "down"
#         else:
#             raise TypeError(f"event.Wheel is not 1 or -1 ({event.wheel_direction:=})")
#
#         return [MouseEvent.Scroll(
#             **general_args,
#             direction=direction
#         )]
#
#     if event.message == HookConstants.WM_MOUSEMOVE:
#         return [MouseEvent.Move(
#             **general_args,
#         )]
#
#     button: Literal["left", "middle", "right"]
#     action: Literal["up", "down"]
#
#     try:
#         button, action = {
#             HookConstants.WM_LBUTTONDOWN: ("left", "down"),
#             HookConstants.WM_LBUTTONUP: ("left", "up"),
#             HookConstants.WM_MBUTTONDOWN: ("middle", "down"),
#             HookConstants.WM_MBUTTONUP: ("middle", "up"),
#             HookConstants.WM_RBUTTONDOWN: ("right", "down"),
#             HookConstants.WM_RBUTTONUP: ("right", "up"),
#         }[event.message]
#     except IndexError:
#         raise TypeError(f"invalid event message, {event.__dict__:=}")
#
#     if action == "down":
#         return [MouseEvent.Click(
#             **general_args,
#             button=button
#         )]
#
#     if action == "up":
#         return [MouseEvent.UnClick(
#             **general_args,
#             button=button
#         )]
#
#     raise TypeError(f"invalid event signature, {event.__dict__:=}")

# we have to do this to make dataclasses work (in pycharm)
class MouseEvent:
    event_types = _event_types
    button_type = _button_type

    Move = _Move
    Click = _Click
    UnClick = _UnClick
    Scroll = _Scroll
