# import dataclasses
# from dataclasses import dataclass
#
#
# @dataclass
# class Move:
#     end_time: int
#     from_place: str
#     to_place: str
#     start_time: int = dataclasses.field(compare=False)
#
#
# @dataclass
# class MoveByTrain(Move):
#     ticket_id: str
#
#
# @dataclass
# class MoveByCar(Move):
#     car_id: str
#
#
# @dataclass
# class MoveOnFoot(Move):
#     pass
#
#
# MoveOnFoot(
#     start_time=0,
#     end_time=2,
#     from_place="a",
#     to_place="b"
# )
#
# # def move_duration(moves: List[Move]):  # Accepts all kinds of moves
# #     return sum(m.end_time - m.start_time for m in moves)
from Test.test2 import MouseEvent

MouseEvent.Move(
    time_ms=10,
    raw=1,
    pos=(100, 100),
    delta=(-1, -1),
)
