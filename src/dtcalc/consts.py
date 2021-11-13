import re

import dtcalc.dtfmt

INDTFMT = "%Y/%m/%d"

TOKPATTS = {
    # No conflicts as of now. So order wouldn't have mattered anyway
    "LPAR": re.compile(r' *(?P<LPAR>\()'),
    "RPAR": re.compile(r' *(?P<RPAR>\))'),
    "OP": re.compile(r' *(?P<OP>\+|-)'),
    "SUNIT": re.compile(r' *(?P<SUNIT>(?P<_SCALE>\d+)(?P<_UNIT>w|d|h|m))'),
    "DTIME": dtcalc.dtfmt.get_pattern(INDTFMT),
}


