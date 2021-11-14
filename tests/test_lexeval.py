import datetime
import re

import pytest

from dtcalc.lexeval import (next_tok, evaluate, infix_to_postfix,
                            eval_postfix, lexer, sunit_to_td, lexeval, LexError)
import dtcalc.tokens as tokens
import dtcalc.dtfmt

@pytest.fixture
def TOKPATTS():
    return  {
        "LPAR": re.compile(r' *(?P<LPAR>\()'),
        "RPAR": re.compile(r' *(?P<RPAR>\))'),
        "OP": re.compile(r' *(?P<OP>\+|-)'),
        "SUNIT": re.compile(r' *(?P<SUNIT>(?P<_SCALE>\d+)(?P<_UNIT>w|d|h|m))'),
        #"DTIME": dtcalc.dtfmt.get_pattern(INDTFMT),
    }

class TestSunitToTD:
    @pytest.mark.parametrize("scale,unit,expected", [
        (2, "w", datetime.timedelta(days=2*7)),
        (321, "d", datetime.timedelta(days=321)),
        (20, "h", datetime.timedelta(hours=20)),
        (31, "m", datetime.timedelta(minutes=31)),
        (21, "s", datetime.timedelta(seconds=21)),
    ])
    def test_valid(self, scale, unit, expected):
        assert sunit_to_td(scale, unit) == expected

    def test_invalid(self):
        with pytest.raises(ValueError):
            sunit_to_td(1, "ab")

class TestTokpatts:
    # Match object's end() gives end + 1
    @pytest.mark.parametrize("inp,start,end,scale,unit", [
        (" 3d  ", 0, 3, "3", "d"),
        ("432w  ", 0, 4, "432", "w"),
    ])
    def test_sunit(self, TOKPATTS, inp, start, end, scale, unit):
        mobj = TOKPATTS["SUNIT"].match(inp)
        mdict = mobj.groupdict()
        assert mobj.start() == start
        assert mobj.end() == end
        assert mdict["_SCALE"] == scale
        assert mdict["_UNIT"] == unit

    @pytest.mark.parametrize("inp,start,end,indtfmt,dtstr", [
        (" 2021/11/15 ", 0, 11, "%Y/%m/%d", "2021/11/15"),
    ])
    # Just consider %Y/%m/%d format for now
    def test_dtime(self, TOKPATTS, inp, start, end, indtfmt, dtstr):
        TOKPATTS["DTIME"] = dtcalc.dtfmt.get_pattern(indtfmt)
        mobj = TOKPATTS["DTIME"].match(inp)
        assert mobj.start() == start
        assert mobj.end() == end
        assert mobj["DTIME"] == dtstr

    @pytest.mark.parametrize("inp,toktype,start,end,expected", [
        ("   +", "OP", 0, 4, "+"),
        ("  - ", "OP", 0, 3, "-"),
        ("   ( ", "LPAR", 0, 4, "("),
        ("  ) ", "RPAR", 0, 3, ")"),
    ])
    def test_others(self, TOKPATTS, inp, toktype, start, end, expected):
        mobj = TOKPATTS[toktype].match(inp)
        assert mobj.start() == start
        assert mobj.end() == end
        assert mobj[toktype] == expected

class TestNextTok:
    @pytest.mark.parametrize("inp,indtfmt,expected", [
        # XXX: try different date formats
        (" 2021/11/13 ", "%Y/%m/%d", (tokens.DTIME(0, 11, datetime.datetime(2021, 11, 13)), 11)),
        (" 2d ad", "%Y/%m/%d", (tokens.SUNIT(0, 3, datetime.timedelta(days=2)), 3)),
        (" 32w ad", "%Y/%m/%d", (tokens.SUNIT(0, 4, datetime.timedelta(weeks=32)), 4)),
        (" + ", "%Y/%m/%d", (tokens.OP(0, 2, "+"), 2)),
        ("- ", "%Y/%m/%d", (tokens.OP(0, 1, "-"), 1)),
        (" (d ad", "%Y/%m/%d", (tokens.LPAR(0, 2), 2)),
        (" ) d ad", "%Y/%m/%d", (tokens.RPAR(0, 2), 2)),
    ])
    def test_valid(self, TOKPATTS, inp, indtfmt, expected):
        TOKPATTS["DTIME"] = dtcalc.dtfmt.get_pattern(indtfmt)
        assert next_tok(inp, TOKPATTS, indtfmt) == expected

    def test_invalid(self, TOKPATTS):
        inp = "aaaa"
        with pytest.raises(LexError):
            next_tok(inp, TOKPATTS, "%Y/%m/%d")

class TestEvaluate:
    @pytest.mark.parametrize("op,fst,snd,expected",[
        (tokens.OP(-1,-1,"+"),
         tokens.DTIME(-1,-1,datetime.datetime(2021,11,10)),
         tokens.SUNIT(-1, -1, datetime.timedelta(days=3)),
         tokens.DTIME(start=-1, end=-1, value=datetime.datetime(2021, 11, 13, 0, 0))),

        (tokens.OP(-1,-1,"+"),
         tokens.SUNIT(-1, -1, datetime.timedelta(days=3)),
         tokens.DTIME(-1,-1,datetime.datetime(2021,11,10)),
         tokens.DTIME(start=-1, end=-1, value=datetime.datetime(2021, 11, 13, 0, 0))),

        (tokens.OP(-1,-1,"+"),
         tokens.SUNIT(-1, -1, datetime.timedelta(days=3)),
         tokens.SUNIT(-1, -1, datetime.timedelta(weeks=2)),
         tokens.SUNIT(-1, -1, datetime.timedelta(days=17))),

        (tokens.OP(-1,-1,"-"),
         tokens.DTIME(-1,-1,datetime.datetime(2021,11,10)),
         tokens.DTIME(-1,-1,datetime.datetime(2021,11,11)),
         tokens.SUNIT(-1, -1, datetime.timedelta(days=-1))),

        (tokens.OP(-1,-1,"-"),
         tokens.DTIME(-1,-1,datetime.datetime(2021,11,10)),
         tokens.SUNIT(-1, -1, datetime.timedelta(days=10)),
         tokens.DTIME(-1,-1,datetime.datetime(2021,10,31))),
    ])
    def test_valid(self, op, fst, snd, expected):
        assert evaluate(op, fst, snd) == expected

    @pytest.mark.parametrize("op,fst,snd",[
        (tokens.OP(-1, -1, "+"),
         tokens.DTIME(-1, -1, datetime.datetime(2021,11,10)),
         tokens.DTIME(-1, -1, datetime.datetime(2021,11,10))),

        (tokens.OP(-1,-1,"-"),
         tokens.SUNIT(-1, -1, datetime.timedelta(days=3)),
         tokens.DTIME(-1,-1,datetime.datetime(2021,11,10))),
    ])
    def test_invalid(self, op, fst, snd):
        with pytest.raises(ValueError):
            evaluate(op, fst, snd)

class TestInfixToPostfix:
    @pytest.mark.parametrize("toks,expected",[
        # infix_to_postfix(lexer("2021/09/21 +( 2d - 3w)")),
        ([tokens.DTIME(start=0, end=10, value=datetime.datetime(2021, 9, 21, 0, 0)),
          tokens.OP(start=0, end=1, value='+'), tokens.LPAR(start=0, end=1),
          tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=2)),
          tokens.OP(start=0, end=1, value='-'),
          tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=21)),
          tokens.RPAR(start=0, end=1)],
         [tokens.DTIME(start=0, end=10, value=datetime.datetime(2021, 9, 21, 0, 0)),
          tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=2)),
          tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=21)),
          tokens.OP(start=0, end=1, value='-'), tokens.OP(start=0, end=1, value='+')]),
    ])
    def test_valid(self, toks, expected):
        assert infix_to_postfix(toks) == expected

    @pytest.mark.parametrize("toks",[
         # "2d + (3w "
        ([tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=2)),
          tokens.OP(start=0, end=1, value='+'), tokens.LPAR(start=0, end=1),
          tokens.SUNIT(start=0, end=2, value=datetime.timedelta(weeks=3))]),

         # "2d) + 3w "
        ([tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=2)),
          tokens.RPAR(start=0, end=2),
          tokens.OP(start=0, end=1, value='+'),
          tokens.SUNIT(start=0, end=2, value=datetime.timedelta(weeks=3))]),
    ])
    def test_invalid(self, toks):
        with pytest.raises(ValueError):
            infix_to_postfix(toks)

@pytest.mark.parametrize("toks,expected",[
    ([tokens.DTIME(start=0, end=10, value=datetime.datetime(2021, 9, 21, 0, 0)),
      tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=2)),
      tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=21)),
      tokens.OP(start=0, end=1, value='-'), tokens.OP(start=0, end=1, value='+')],
      tokens.DTIME(start=-1, end=-1, value=datetime.datetime(2021, 9, 2, 0, 0))),
])
def test_eval_postfix(toks, expected):
    assert eval_postfix(toks) == expected

@pytest.mark.parametrize("inp,indtfmt,expected",[
    ("2021/09/21 +( 2d - 3w)", "%Y/%m/%d",

     [tokens.DTIME(start=0, end=10, value=datetime.datetime(2021, 9, 21, 0, 0)),
      tokens.OP(start=0, end=1, value='+'), tokens.LPAR(start=0, end=1),
      tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=2)),
      tokens.OP(start=0, end=1, value='-'),
      tokens.SUNIT(start=0, end=2, value=datetime.timedelta(days=21)),
      tokens.RPAR(start=0, end=1)]),
])
def test_lexer(TOKPATTS, inp, indtfmt, expected):
    TOKPATTS["DTIME"] = dtcalc.dtfmt.get_pattern(indtfmt)
    assert lexer(inp, TOKPATTS, indtfmt) == expected

@pytest.mark.parametrize("inp,in_dtfmt,out_dtfmt,expected",[
    ("2021/11/09 +  2d", "%Y/%m/%d", "%Y/%m/%d", "2021/11/11"),  # datetime.datetime(2021, 11, 11))
    ("2021/11/09 -  2021/11/10", "%Y/%m/%d", "%Y/%m/%d", "-1 days"),  # datetime.datetime(2021, 11, 11)),
])
def test_lexeval(inp, in_dtfmt, out_dtfmt, expected):
    assert lexeval(inp, in_dtfmt, out_dtfmt) == expected




