import pytest

import dataclasses
import datetime
import re

@dataclasses.dataclass
class Token:
    start: int
    end: int

@dataclasses.dataclass
class SUNIT(Token):
    scale: int
    unit: str

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

INDTFMT = "%Y/%m/%d"
TOKPATTS = {
    # No conflicts as of now. So order wouldn't have mattered anyway
    "LPAR": re.compile(r' *(?P<LPAR>\()'),
    "RPAR": re.compile(r' *(?P<RPAR>\))'),
    "OP": re.compile(r' *(?P<OP>\+|-)'),
    "SUNIT": re.compile(r' *(?P<SUNIT>(?P<_SCALE>\d+)(?P<_UNIT>w|d|h|m))'),
}

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

@pytest.mark.parametrize("scale,unit,expected", [
    (2, "w", datetime.timedelta(days=2*7)),
    (321, "d", datetime.timedelta(days=321)),
])
def test_sunit_to_timedelta(scale, unit, expected):
    assert sunit_to_timedelta(scale, unit) == expected
