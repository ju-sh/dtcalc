import calendar
import datetime
import re

import pytest

import dtcalc.dtfmt


@pytest.mark.parametrize("lst,name,expected", [
    (calendar.month_abbr[1:], "monabbr",
     '(?P<monabbr>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'),
])
def test_list_to_patt(lst, name, expected):
    assert dtcalc.dtfmt.list_to_patt(lst, name) == expected


class TestGetPattern:
    @pytest.mark.parametrize("fmt,expected", [
        ("%Y %m   %d",
         re.compile(' *(?P<DTIME>(?P<Y>\\d\\d\\d\\d) (?P<m>1[0-2]|0[1-9]|'
                    '[1-9])   (?P<d>3[0-1]|[1-2]\\d|0[1-9]|[1-9]| [1-9]))')),
    ])
    def test_valid(self, fmt, expected):
        assert dtcalc.dtfmt.get_pattern(fmt) == expected

    @pytest.mark.parametrize("fmt", [
        ("%Y %m %  %d"),
        ("%Y %m %"),
        ("%Y %m %!  %d"),
    ])
    def test_invalid(self, fmt):
        with pytest.raises(ValueError):
            dtcalc.dtfmt.get_pattern(fmt)


@pytest.mark.parametrize("tdobj,expected", [
    (datetime.timedelta(days=1), "1 days"),
    (datetime.timedelta(days=-1), "-1 days"),
    (datetime.timedelta(weeks=2, days=-5), "1 weeks, 2 days"),
    (datetime.timedelta(hours=2, minutes=-1), "1 hours, 59 minutes"),
])
def test_fmt_td(tdobj, expected):
    assert dtcalc.dtfmt.fmt_td(tdobj) == expected
