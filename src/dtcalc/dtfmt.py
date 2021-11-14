"""
Functions to handle different datetime formats.
"""

from typing import Sequence
import calendar
import datetime
import re


def list_to_patt(lst: Sequence[str], name: str) -> str:
    """
    Create a regex pattern in string form capable of matching each element
    in a list.

    Beware of having empty string in lst!

    Arguments:
      lst: list of strings for which a regex pattern is to be determined.
      name: name to be given to the output group pattern.

    Returns:
      regex pattern in string form that can match each element in lst.
    """
    # longer strings need to be matched first
    lst = sorted(lst, key=len, reverse=True)
    patt = "|".join(re.escape(elem) for elem in lst)
    patt = f"(?P<{name}>{patt})"
    return patt


PATT_DICT = {
    # Source of most of this dict: _strptime.py of cpython
    # https://github.com/python/cpython/blob/main/Lib/_strptime.py

    # The " [1-9]" part of the regex is to make %c from ANSI C work

    # 01-31 (day of month)
    'd': r"(?P<d>3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9])",

    # 000000-999999 (microseconds)
    'f': r"(?P<f>[0-9]{1,6})",

    # 00-24 (hour: 24 hour clock)
    'H': r"(?P<H>2[0-3]|[0-1]\d|\d)",

    # 00-12 (hour: 12 hour clock)
    'I': r"(?P<I>1[0-2]|0[1-9]|[1-9])",

    'G': r"(?P<G>\d\d\d\d)",

    # 001-366 (day of year)
    'j': (r"(?P<j>36[0-6]|3[0-5]\d|[1-2]\d\d|0[1-9]\d|00[1-9]"
          r"|[1-9]\d|0[1-9]|[1-9])"),

    # (01-12) month
    'm': r"(?P<m>1[0-2]|0[1-9]|[1-9])",

    # (00-59) minute
    'M': r"(?P<M>[0-5]\d|\d)",

    # (00-59) second
    'S': r"(?P<S>6[0-1]|[0-5]\d|\d)",

    # (00-53) week of year with Sunday as first day of week
    'U': r"(?P<U>5[0-3]|[0-4]\d|\d)",

    'w': r"(?P<w>[0-6])",
    'u': r"(?P<u>[1-7])",
    'V': r"(?P<V>5[0-3]|0[1-9]|[1-4]\d|\d)",
    'y': r"(?P<y>\d\d)",
    'Y': r"(?P<Y>\d\d\d\d)",
    'z': r"(?P<z>[+-]\d\d:?[0-5]\d(:?[0-5]\d(\.\d{1,6})?)?|(?-i:Z))",

    # Tuesday
    'A': list_to_patt(calendar.day_name[:7], 'A'),

    # Tue
    'a': list_to_patt(calendar.day_abbr[:7], 'a'),

    # January
    'B': list_to_patt(calendar.month_name[1:13], 'B'),

    # Jan
    'b': list_to_patt(calendar.month_abbr[1:13], 'b'),

    # AM (en_US locale)
    'p': r"(?P<p>AM|PM|am|pm)",

    # %
    '%': "%",

    # 'Z': self.__seqToRE((tz for tz_names in self.locale_time.timezone
    #                             for tz in tz_names),
    #                     'Z'),
}


def get_pattern(fmt: str) -> re.Pattern:
    """
    Accept a POSIX date command style format string and return corresponding
    compiled regex pattern.

    Arguments:
      fmt: format string in the style accepted by date command in POSIX.

    Returns:
      Pattern object that can match the given format.
    """
    out_patt = ""
    while "%" in fmt:
        idx = fmt.index("%")  # a ValueError can't happen here
        out_patt += fmt[:idx]
        try:
            patt = PATT_DICT[fmt[idx+1]]
        except KeyError as kerr:
            msg = f"Unknown format specifier: {fmt[idx+1]!r}"
            raise ValueError(msg) from kerr
        except IndexError as inderr:
            raise ValueError("Lone '%' found") from inderr
        out_patt += patt
        fmt = fmt[idx+2:]
    out_patt = f" *(?P<DTIME>{out_patt})"
    return re.compile(out_patt)


def fmt_td(tdobj: datetime.timedelta) -> str:
    """
    Format a timedelta object into a string.
    Use w,d,h,m units.

    Arguments:
      tdobj: timedelta object to be formatted into string.

    Returns:
      String representation of tdobj using w,d,h,m units.
    """
    # https://gist.github.com/thatalextaylor/7408395
    out_str = ""
    seconds_float = tdobj.total_seconds()
    if seconds_float < 0:
        out_str += "-"
        seconds_float = -seconds_float
    seconds = int(seconds_float)
    weeks = seconds // 604800  # 60*60*24*7
    seconds %= 604800
    days = seconds // 86400  # 60*60*24
    seconds %= 86400
    hours = seconds // 3600  # 60*60
    seconds %= 3600
    minutes = seconds // 60  # 60
    seconds %= 60

    if weeks > 0:
        out_str += f"{weeks} weeks, "
    if days > 0:
        out_str += f"{days} days, "
    if hours > 0:
        out_str += f"{hours} hours, "
    if minutes > 0:
        out_str += f"{minutes} minutes, "
    # Remaining seconds are ignored for now
    return out_str[:-2]
