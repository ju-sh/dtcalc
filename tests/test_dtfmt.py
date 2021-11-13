import calendar
import re

import pytest

import dtcalc.dtfmt

@pytest.mark.parametrize("lst,name,expected", [
    (calendar.month_abbr[1:], "monabbr",
     '(?P<monabbr>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'),
])
def test_list_to_patt(lst, name, expected):
    assert dtcalc.dtfmt.list_to_patt(lst, name) == expected

@pytest.mark.parametrize("fmt,expected", [
    ("%Y %m   %d",
     re.compile(' *(?P<DTIME>(?P<Y>\\d\\d\\d\\d) (?P<m>1[0-2]|0[1-9]|[1-9])   (?P<d>3[0-1]|[1-2]\\d|0[1-9]|[1-9]| [1-9]))')),
])
def test_get_pattern(fmt, expected):
    assert dtcalc.dtfmt.get_pattern(fmt) == expected
