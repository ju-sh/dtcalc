import dataclasses
import datetime
import re

import dtcalc.dtfmt

@dataclasses.dataclass
class Token:
    start: int
    end: int

@dataclasses.dataclass
class SUNIT(Token):
    value: datetime.timedelta

@dataclasses.dataclass
class DTIME(Token):
    value: datetime.datetime

@dataclasses.dataclass
class OP(Token):
    value: str

@dataclasses.dataclass
class LPAR(Token):
    pass

@dataclasses.dataclass
class RPAR(Token):
    pass

def sunit_to_timedelta(scale: int, unit: str) -> datetime.timedelta:
    if unit == "w":
        return datetime.timedelta(weeks=scale)
    if unit == "d":
        return datetime.timedelta(days=scale)
    if unit == "h":
        return datetime.timedelta(hours=scale)
    if unit == "m":
        return datetime.timedelta(minutes=scale)
    if unit == "s":
        return datetime.timedelta(seconds=scale)
    raise ValueError
