import time
from typing import Self

from Mine.Events import KeyboardEvent
from Mine.OsAbstractions import get_backend, get_backend_type
from Mine.OsAbstractions.Abstract.Keyboard import StateData, Down, Up, base_conv_from_types
from Mine.ViritallKeys.VkEnum import KeyData

_backend_type = get_backend_type()

_backend = get_backend()
_keyboard = _backend.Keyboard
_event_api = _backend.EventApi

ASSUME_NO_STATE_CHANGE = False


class _Up:
    def __init__(self, *vks: int, no_optimise=False):
        self.vks = set(vks)
        self.no_optimise = no_optimise

    def __repr__(self):
        return f"{type(self).__name__}({self.vks})"


class _Down:
    def __init__(self, *vks: int, no_optimise=False):
        self.vks = set(vk for vk in vks)
        self.no_optimise = no_optimise

    def __repr__(self):
        return f"{type(self).__name__}({self.vks})"


press_seq_type = tuple[_Up | _Down | int, ...]


# class Pressed:
#     def __init__(self, pressed: (base_conv_from_types,), do: base_conv_from_types | Up | Down):
#         self.pressed = pressed
#         self.do = do


class _StateData:
    def __init__(
            self,
            do: tuple[int | _Up | _Down | Self, ...],
            need_pressed: set[int] = None,
            need_unpressed: set[int] = None
    ):
        self.do = do
        self.need_pressed = need_pressed or set()
        self.need_unpressed = need_unpressed or set()

    def __repr__(self):
        return f"{type(self).__name__}({self.need_pressed} {self.do} {self.need_unpressed})"


# todo possibly add a Literal class
#   that works like type_literal but only for a part

all_conv_from_types = base_conv_from_types | Up | Down | StateData


class Keyboard:
    @classmethod
    def _dispatch_block(cls, vk: int, press: bool):
        event_class = KeyboardEvent.KeyDown if press else KeyboardEvent.KeyUp

        # btw blocking a KeyData blocks that button,
        # so we actually get all data we need
        key = KeyData.from_vk(vk)

        _event_api.dispatch_event_block(
            event_class(
                time.time_ns() / 10 ** 6,
                "synthetic event",
                key,
            )
        )

    @classmethod
    def _queue_vk_press(cls, vk: int, down: bool):
        cls._dispatch_block(vk, down)
        _keyboard.queue_press(vk, down)

    @classmethod
    def _get_seq_class(cls, down):
        return _Down if down else _Up

    @classmethod
    def _exec_press_seq(cls, press_seq: press_seq_type):
        for thing in press_seq:
            if isinstance(thing, int):
                cls._queue_vk_press(thing, True)
                cls._queue_vk_press(thing, False)

            elif isinstance(thing, _Down):
                for vk in thing.vks:
                    cls._queue_vk_press(vk, True)

            elif isinstance(thing, _Up):
                for vk in thing.vks:
                    cls._queue_vk_press(vk, False)

            else:
                raise TypeError(f"invalid press seq type {thing}")

        _keyboard.send_queued_presses()

    @classmethod
    def _state_part_to_press_seq(
            cls,
            *state_data: _StateData,
            cur_pressed=None
    ) -> list[_Up | _Down | int]:

        out: list[_Up | _Down | int] = []

        last_pressed = cur_pressed or _keyboard.get_pressed_keys()

        for state in state_data:
            out += [
                _Up(*((last_pressed - state.need_pressed) & state.need_unpressed)),
                _Down(*(state.need_pressed - last_pressed)),
            ]

            for x in state.do:
                if isinstance(x, _StateData):
                    out += cls._state_part_to_press_seq(
                        x,
                        cur_pressed=last_pressed
                    )
                else:
                    out.append(x)

            # we're "lazy", so we don't unpressed the keys that we don't have to
            not_unpressed = last_pressed - state.need_pressed - state.need_unpressed

            # but we have to remember that we didn't un press them
            last_pressed = {*state.need_pressed, *not_unpressed}

        need_pressed = cur_pressed or _keyboard.get_pressed_keys()

        out += [
            _Down(*(need_pressed - last_pressed)),
            _Up(*(last_pressed - need_pressed)),
        ]

        clean_out = []
        for thing in out:
            if isinstance(thing, _Up | _Down):
                if not thing.vks:
                    continue
            clean_out.append(thing)

        return clean_out

    @classmethod
    def _state_to_press_seq(cls, *state_data: _StateData):
        dirty_press_seq = cls._state_part_to_press_seq(*state_data)

        clean_press_seq = []
        for thing in dirty_press_seq:
            if isinstance(thing, _Up | _Down):
                if not thing.vks:
                    continue
            clean_press_seq.append(thing)

        return tuple(clean_press_seq)

    @classmethod
    def _compile_to_state_data(cls, *inp: all_conv_from_types) -> tuple[_StateData, ...]:
        out: list[_StateData] = []

        for part in inp:
            if isinstance(part, KeyData):
                out.append(_StateData((part.vk,)))

            elif isinstance(part, str):
                for char in part:
                    out += cls._compile_to_state_data(
                        _keyboard.calc_buttons_for_char(
                            char
                        )
                    )

            elif isinstance(part, int):
                out.append(
                    _StateData((part,))
                )

            elif isinstance(part, StateData):
                out.append(
                    _StateData(
                        do=cls._compile_to_state_data(*part.do),
                        need_pressed=part.need_pressed,
                        need_unpressed=part.need_unpressed,
                    )
                )

            elif isinstance(part, Down | Up):
                dc = _Down if isinstance(part, Down) else _Up

                out = []
                for data in part.data:
                    if isinstance(data, StateData):
                        raise TypeError("you cant use StateData in a Down/Up")

                    elif isinstance(data, str):
                        for char in data:
                            sd = cls._compile_to_state_data(char)[0]

                            # noinspection PyTypeChecker
                            # sd.do is always an int
                            sd.do = dc(sd.do)
                            out.append(sd)

                    elif isinstance(data, int):
                        out.append(
                            _StateData(
                                (dc(data),)
                            )
                        )

                    else:
                        raise TypeError(f"invalid type in the seq {type(data)=} {data=}")

                return tuple(out)

            else:
                raise TypeError(f"invalid type in the seq {type(part)=} {part=}")

        return tuple(out)

    @classmethod
    def _remove_modifiers(cls, *inp: all_conv_from_types) -> tuple[all_conv_from_types, ...]:
        """
        converts all "all_conv_from_types" so that all str and
        KeyData become just int (vks)
        """

        out = []

        for part in inp:
            if isinstance(part, int):
                out.append(part)

            if isinstance(part, str):
                out += [
                    _keyboard.get_vk_from_key_data(
                        _keyboard.get_key_data_from_char(
                            char
                        ))
                    for char in part
                ]

            if isinstance(part, KeyData):
                out += [
                    _keyboard.get_vk_from_key_data(
                        part
                    )
                ]

            elif isinstance(part, Up):
                out.append(
                    Up(
                        *cls._remove_modifiers(
                            *part.data
                        )
                    ))

            elif isinstance(part, Down):
                out.append(
                    Up(
                        *cls._remove_modifiers(
                            *part.data
                        )
                    )
                )

            elif isinstance(part, StateData):
                out.append(
                    StateData(
                        (
                            *cls._remove_modifiers(
                                *part.do
                            ),
                        ),
                        need_pressed=part.need_pressed,
                        need_unpressed=part.need_unpressed
                    )
                )
        return tuple(out)

    # todo handle caps-lock

    @classmethod
    def type(cls, *inp: all_conv_from_types):
        """
        types a sequence of things

        for each part in inp
            the following are cases for the type of the part

        int (vk):
            press and un pres said button (vk)

        str (text)
            press buttons in a way that archives the desired text

        KeyData
            if it has .char type that (see "str")
            if it has .vk type that (see "int")

        Up / Down
            if the inside is a vk
                then simply press/un press that vk

            if the inside is a char
                 then all modifiers are correctly pressed and cleaned up
                 but the actual vk that corresponds to the char
                    is simply pressed/un pressed

            Note:
                the char that is "permanently" pressed/unpressed
                is not taken into consideration when calculating the
                keys required to be pressed/unpressed to get a specific char

                i.e.
                type(Down(LinuxVk.shift), "a") => "A"

        Pressed(pressed, do)
            executes {do}
            while the keys in {pressed} are pressed
            afterward un presses those keys

            Note:
                if Up(a) is used inside {do}
                and {pressed} has {a} in it
                then {a} will be unpressed in the cleanup

                i.e.
                if Up(a) in {do}
                and {a} in {pressed}
                then {a} will be unpressed when "Pressed" finished
        """
        state_seq = cls._compile_to_state_data(*inp)
        press_seq = cls._state_to_press_seq(*state_seq)
        cls._exec_press_seq(press_seq)

    @classmethod
    def type_literal_keys(cls, *inp: all_conv_from_types):
        """
        types the vk(s) directly corresponding to the input

        so it totally ignores state
            type_literal_keys("A") == type_literal_keys("a")
            # on the nordic layout
            type_literal_keys("3") == type_literal_keys("#") == type_literal_keys("£")

        it also won't fix the state for a specific char so:
            type_literal_keys("a") might come out as "A", if shift is pressed
        """

        literal_inp = cls._remove_modifiers(*inp)
        cls.type(literal_inp)

    @classmethod
    def is_pressed(cls, key: KeyData):
        return _keyboard.key_pressed(key)
