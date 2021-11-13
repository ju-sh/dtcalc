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
