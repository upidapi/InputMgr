from src.Events import KeyboardEvent, MouseEvent
from src.Main.EventQueue import EventQueue


def print_event(
        event,

        mouse_move=False,
        mouse_click=True,
        mouse_unclick=True,
        mouse_scroll=True,

        keyboard_keydown=True,
        keyboard_keyup=True,
        keyboard_key_send=True,
):

    # print(type(event))

    string_event = str(type(event)).split(".")[-1][:-2] + ": "
    padded_event = string_event.ljust(10)

    if isinstance(event, KeyboardEvent.event_types):
        if any((keyboard_keydown, keyboard_keyup, keyboard_key_send)):
            safe_char = event.key_data.char or ''

            f_char = f"\"{safe_char}\"{' ' * (1 - len(safe_char))}"

            vk = str(event.key_data.vk).ljust(4)

            end_part = \
                f' \"{event.chars}\"' \
                if isinstance(event, KeyboardEvent.KeySend) else \
                ''
            print(f"{padded_event}{vk:<3} {f_char} {end_part}")
        return

    if isinstance(event, MouseEvent.event_types):
        if isinstance(event, MouseEvent.Move):
            if mouse_move:
                print(f"{padded_event}{event.pos}")
            return

        if isinstance(event, MouseEvent.Scroll):
            if mouse_scroll:
                print(f"{padded_event}{event.pos} {event.dy=} {event.dx=}")
            return

        if isinstance(event, MouseEvent.Click | MouseEvent.UnClick):
            if any((mouse_click, mouse_unclick)):
                print(f"{padded_event}{event.pos} {event.button}")
            return


async def print_events(
        mouse_move=False,
        mouse_click=True,
        mouse_unclick=True,
        mouse_scroll=True,

        keyboard_keydown=True,
        keyboard_keyup=True,
        keyboard_key_send=True,
):
    with EventQueue() as es:
        async for event in es:
            print_event(
                event,

                mouse_move,
                mouse_click,
                mouse_unclick,
                mouse_scroll,

                keyboard_keydown,
                keyboard_keyup,
                keyboard_key_send,
            )

