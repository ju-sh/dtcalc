import calendar
import datetime
import re

def list_to_patt(lst: 'List[str]', name: str) -> str:
    """
    Beware of having empty string in lst!
    """
    # longer strings need to be matched first
    lst.sort(key=len, reverse=True)
    patt = "|".join(re.escape(elem) for elem in lst)
    patt = f"(?P<{name}>{patt})"
    return patt

PATT_DICT = {
    # Source of most of this dict: _strptime.py of cpython
    # The " [1-9]" part of the regex is to make %c from ANSI C work
    'd': r"(?P<d>3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9])",
    'f': r"(?P<f>[0-9]{1,6})",
    'H': r"(?P<H>2[0-3]|[0-1]\d|\d)",
    'I': r"(?P<I>1[0-2]|0[1-9]|[1-9])",
    'G': r"(?P<G>\d\d\d\d)",
    'j': r"(?P<j>36[0-6]|3[0-5]\d|[1-2]\d\d|0[1-9]\d|00[1-9]|[1-9]\d|0[1-9]|[1-9])",
    'm': r"(?P<m>1[0-2]|0[1-9]|[1-9])",
    'M': r"(?P<M>[0-5]\d|\d)",
    'S': r"(?P<S>6[0-1]|[0-5]\d|\d)",
    'U': r"(?P<U>5[0-3]|[0-4]\d|\d)",
    'w': r"(?P<w>[0-6])",
    'u': r"(?P<u>[1-7])",
    'V': r"(?P<V>5[0-3]|0[1-9]|[1-4]\d|\d)",
    'y': r"(?P<y>\d\d)",
    'Y': r"(?P<Y>\d\d\d\d)",
    'z': r"(?P<z>[+-]\d\d:?[0-5]\d(:?[0-5]\d(\.\d{1,6})?)?|(?-i:Z))",
    'A': list_to_patt(calendar.day_name[:7], 'A'),
    'a': list_to_patt(calendar.day_abbr[:7], 'a'),
    'B': list_to_patt(calendar.month_name[1:13], 'B'),
    'b': list_to_patt(calendar.month_abbr[1:13], 'b'),
    'p': r"(?P<p>AM|PM)",  # XXX: add lowercase am pm
    '%': "%",

#    'Z': self.__seqToRE((tz for tz_names in self.locale_time.timezone
#                                for tz in tz_names),
#                        'Z'),
}

def get_pattern(fmt: str) -> str :
    """
    Accept a unix date style format string and return corresponding compiled
    regex pattern.
    """
    fmt_len = len(fmt)
    #rv = "^"
    rv = ""
    fmtdict = {}
    while "%" in fmt:
        idx = fmt.index("%")  # a ValueError can't happen here
        rv += fmt[:idx]
        if idx >= fmt_len:
            raise ValueError("Lone '%' found")
        try:
            patt = PATT_DICT[fmt[idx+1]]
            fmtdict[fmt[idx+1]] = None
        except KeyError:
            raise ValueError(f"Unknown format specifier: {fmt[idx+1]!r}")
        rv += patt
        fmt = fmt[idx+2:]
    rv = f" *(?P<DTIME>{rv})"
    patt = re.compile(rv)
    return patt
