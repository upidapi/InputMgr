from dataclasses import dataclass


def dict_p_print(a: dict, indent=0):
    inside = ""

    for key, val in a.items():
        inside += f"{'    ' * (indent + 1)}{key}: {val} \n"

    return (
        f"{{\n"
        f"{inside}"
        f"{'    ' * indent}}}"
    )


@dataclass
class _BaseEvent:
    time: int
    raw: any

    def print_event(self):
        x = {
            "event_type": type(self),
            "event_dict": dict_p_print(self.__dict__, 1),
            "raw_event_type": type(self.raw),
            "raw_event_dict": dict_p_print(self.raw.__dict__, 1),
        }

        print(dict_p_print(x))
