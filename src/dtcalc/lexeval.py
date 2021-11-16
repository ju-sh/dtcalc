"""
Lex and evaluate input.
"""

from typing import Tuple, Union, List, Dict, Optional
import dataclasses
import datetime
import re

from dtcalc import tokens
import dtcalc.dtfmt


@dataclasses.dataclass
class LexError(Exception):
    """
    Exception to be raised when lexer fails.

    Input string is not explicitly stored as there is only one input.

    Attributes:
      pos: start index of first unrecognized token.
    """
    pos: int


def sunit_to_td(scale: int, unit: str) -> datetime.timedelta:
    """
    Accept an tokens.SUNIT object and calculate equivalent
    datetime.timedelta object.

    Arguments:
      scale: integer by which unit is scaled.
      unit: time unit

    Returns:
      Equivalent datetime.timedelta object.

    Raises:
      ValueError: When unit is invalid.
    """
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
    raise ValueError("Invalid unit!")


def next_tok(inp: str, tokpatts, indtfmt: str,
             pos: int) -> Tuple[tokens.Token, int]:
    """
    Get next token by matching the regex patterns of the valid tokens.

    Returns:
      tokens.Token object corresponding to matched token.
      Index of next character in inp to be processed.

    Raises:
      LexError: When next token is invalid.
    """
    tok: Optional[tokens.Token] = None
    for toktype in tokpatts:
        mobj = tokpatts[toktype].match(inp, pos)
        if mobj is not None:
            # leading white space would be included, yeah
            start = mobj.start()
            end = mobj.end()

            if toktype == "DTIME":
                dtval = datetime.datetime.strptime(mobj["DTIME"], indtfmt)
                tok, npos = tokens.DTIME(start, end, dtval), end
            elif toktype == "SUNIT":
                scale = int(mobj["_SCALE"])
                unit = mobj["_UNIT"]
                tdval = sunit_to_td(scale, unit)
                tok, npos = tokens.SUNIT(start, end, tdval), end
            elif toktype == "SPECIAL":
                valstr = mobj["SPECIAL"]
                cur_dt = datetime.datetime.now()
                if valstr == "today":
                    tokval = datetime.datetime(cur_dt.year, cur_dt.month,
                                               cur_dt.day)
                    tok = tokens.DTIME(start, end, tokval)
                elif valstr == "now":
                    tok = tokens.DTIME(start, end, cur_dt)
                npos = end
            elif toktype == "OP":
                tok, npos = tokens.OP(start, end, mobj["OP"]), end
            elif toktype == "LPAR":
                tok, npos = tokens.LPAR(start, end), end
            elif toktype == "RPAR":
                tok, npos = tokens.RPAR(start, end), end
    if tok is None:
        raise LexError(pos)
    return tok, npos


def evaluate(oprtr: tokens.OP, fst: tokens.Token,
             snd: tokens.Token) -> Union[tokens.DTIME, tokens.SUNIT]:
    """
    Perform operation using given operator and operands and return result.
    For use during postfix expression evaluation.

    Arguments:
      oprtr: operator
      fst: first operand
      snd: second operand

    Returns:
      Value of 'fst oprtr snd'

    Raises:
      ValueError: when oprtr is not a valid OP token
    """
    res: Union[tokens.DTIME, tokens.SUNIT]
    if oprtr.value == "+":
        if isinstance(fst, tokens.DTIME):
            if isinstance(snd, tokens.DTIME):  # D,D,+
                raise ValueError("Can't add two dates!")
            if isinstance(snd, tokens.SUNIT):
                res = tokens.DTIME(-1, -1, fst.value + snd.value)
        elif isinstance(fst, tokens.SUNIT):
            if isinstance(snd, tokens.DTIME):  # S,D,+
                res = tokens.DTIME(-1, -1, snd.value + fst.value)
            elif isinstance(snd, tokens.SUNIT):  # S,S,+
                res = tokens.SUNIT(-1, -1, fst.value + snd.value)
    elif oprtr.value == "-":
        if isinstance(fst, tokens.DTIME):
            if isinstance(snd, tokens.DTIME):  # D,D,-
                res = tokens.SUNIT(-1, -1, fst.value - snd.value)
            elif isinstance(snd, tokens.SUNIT):  # D,S,-
                res = tokens.DTIME(-1, -1, fst.value - snd.value)

        elif isinstance(fst, tokens.SUNIT):
            if isinstance(snd, tokens.DTIME):  # S,D,-
                raise ValueError("Can't negate a lone datetime!")
            if isinstance(snd, tokens.SUNIT):  # S,S,-
                res = tokens.SUNIT(-1, -1, fst.value - snd.value)
    else:
        raise ValueError(f"Unknown operator: {oprtr.value}")
    return res


def lexer(inp: str, tokpatts: Dict[str, re.Pattern],
          indtfmt: str) -> List[tokens.Token]:
    """
    Perform lexical analysis (tokenization).
    Accept an input string and produce a list of tokens

    Arguments:
      inp: input string
    Returns:
      List of tokens.Token objects in infix form.
    """
    toks = []
    pos = 0
    inplen = len(inp)
    while pos < inplen:
        if inp[pos].isspace():
            pos += 1
        else:
            tok, pos = next_tok(inp, tokpatts, indtfmt, pos)
            toks.append(tok)
    return toks


def infix_to_postfix(toks: List[tokens.Token]) -> List[tokens.Token]:
    """
    Convert tokens from infix to postfix form.

    Probably a form of operator-precedence parsing.
    https://en.wikipedia.org/wiki/Operator-precedence_parser
    https://en.wikipedia.org/wiki/Shunting-yard_algorithm

    Arguments:
      toks: list of tokens in infix form. Obtained as result of lexing.
    Returns:
      list of tokens in postfix form.
    """
    toks.append(tokens.RPAR(-1, -1))

    # type is Union[OP, DTIME, SUNIT] actually
    post: List[tokens.Token] = []

    stack: List[tokens.Token] = [tokens.LPAR(-1, -1)]

    for tok in toks:
        if isinstance(tok, tokens.LPAR):
            stack.append(tok)
        elif isinstance(tok, (tokens.DTIME, tokens.SUNIT)):
            post.append(tok)
        elif isinstance(tok, tokens.OP):
            try:
                # Both operators have same precedence currently
                while isinstance(stack[-1], tokens.OP):
                    stok = stack.pop()
                    post.append(stok)
                stack.append(tok)
            except IndexError as inderr:
                raise ValueError("Malformed input!") from inderr
        # elif isinstance(tok, tokens.RPAR):
        else:
            try:
                while not isinstance(stack[-1], tokens.LPAR):
                    stok = stack.pop()
                    post.append(stok)
                stack.pop()  # pop the tokens.LPAR
            except IndexError as inderr:
                raise ValueError("Unmatched parenthesis!") from inderr
    # stack should be empty at this point
    if stack:
        raise ValueError("Unmatched parenthesis!")
    return post


def eval_postfix(toks: List[tokens.Token]) -> Union[tokens.DTIME,
                                                    tokens.SUNIT]:
    """
    Evaluate using a stack a list of tokens arranged in postfix
    notation order.

    Arguments:
      toks: a postfix expression of tokens stored as list.

    Returns:
      Value of the postfix expression after evaluation.
    """
    # stack consists only of value in postfix evaluation
    stack: List[Union[tokens.DTIME, tokens.SUNIT]] = []
    for tok in toks:
        if isinstance(tok, (tokens.SUNIT, tokens.DTIME)):
            stack.append(tok)
        elif isinstance(tok, tokens.OP):
            snd = stack.pop()
            fst = stack.pop()
            val = evaluate(tok, fst, snd)
            stack.append(val)
    if len(stack) != 1:
        raise ValueError("Malformed input!")
    return stack[-1]


def lexeval(inp_lst: List[str], in_dtfmt: str, out_dtfmt: str) -> str:
    """
    Driver function for performing input evaluation.

    Arguments:
      inp: input string
      in_dtfmt: input date format
      out_dtfmt: output date format

    Returns:
      String representation of resultant datetime or timedelta
    """

    tokpatts = {
        # No conflicts as of now. So order shouldn't matter
        "LPAR": re.compile(r' *(?P<LPAR>\()'),
        "RPAR": re.compile(r' *(?P<RPAR>\))'),
        "OP": re.compile(r' *(?P<OP>\+|-)'),
        "SUNIT": re.compile(r' *(?P<SUNIT>(?P<_SCALE>\d+)(?P<_UNIT>w|d|h|m))'),
        "SPECIAL": re.compile(r' *(?P<SPECIAL>today|now)'),
        "DTIME": dtcalc.dtfmt.get_pattern(in_dtfmt),
    }

    inp = ' '.join(inp_lst)
    infix_toks = lexer(inp, tokpatts, in_dtfmt)
    postfix_toks = infix_to_postfix(infix_toks)
    result = eval_postfix(postfix_toks)
    if isinstance(result, tokens.DTIME):
        res_str = result.value.strftime(out_dtfmt)
    # elif isinstance(result, tokens.SUNIT):
    else:
        res_str = dtcalc.dtfmt.fmt_td(result.value)
    return res_str
