import datetime

import pytest

import dtcalc.tokens

@pytest.mark.parametrize("scale,unit,expected", [
    (2, "w", datetime.timedelta(days=2*7)),
    (321, "d", datetime.timedelta(days=321)),
])
def test_sunit_to_timedelta(scale, unit, expected):
    assert dtcalc.tokens.sunit_to_timedelta(scale, unit) == expected
