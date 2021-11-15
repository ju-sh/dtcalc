"""
Token classes.
"""

import dataclasses
import datetime


@dataclasses.dataclass
class Token:
    """
    Base class of all tokens.
    Not meant to be instantiated directly.
    (Still, not marking it an abstract class.)

    Attributes:
      start: starting index of token in input string.
      end: one more than the last index of token in input string.
    """
    start: int
    end: int

@dataclasses.dataclass
class SUNIT(Token):
    """
    Represents a datetime offset value.

    Stands for 'scaled unit'.
    Results from combination of an integer ('scale') and a 'unit'.
    Value would end up being a datetime.timedelta.

    Attributes:
      value: resultant datetime offset.
    """
    value: datetime.timedelta

@dataclasses.dataclass
class DTIME(Token):
    """
    Represents a datetime value.

    Attributes:
      value: datetime.datetime object
    """
    value: datetime.datetime

@dataclasses.dataclass
class OP(Token):
    """
    Represents a valid operator.

    Attributes:
      value: operator as string.
    """
    value: str

@dataclasses.dataclass
class LPAR(Token):
    """
    Represents left parenthesis.
    """

@dataclasses.dataclass
class RPAR(Token):
    """
    Represents right parenthesis.
    """
