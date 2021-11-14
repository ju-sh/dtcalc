"""
Lex and evaluate input.
"""

from typing import Tuple, Union, List
import dataclasses
import datetime
import re

#from dtcalc.consts import TOKPATTS, INDTFMT
import dtcalc.tokens as tokens
import dtcalc.dtfmt


@dataclasses.dataclass
class LexError(Exception):
    src: str
    pos: int

def sunit_to_td(scale: int, unit: str) -> datetime.timedelta:
    """
    Accept an tokens.SUNIT object and calculate equivalent datetime.timedelta object.

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

# XXX: remove pos arg as it's always 0, and expand LexError
def next_tok(inp: str, TOKPATTS, INDTFMT: str, pos: int = 0) -> Tuple[tokens.Token, int]:
    """
    Get next token by matching the regex patterns of the valid tokens.

    Returns:
      tokens.Token object corresponding to matched token.
      Index of next character in inp to be processed.

    Raises:
      LexError: When next token is invalid.
    """
    for toktype in TOKPATTS:
        mobj = TOKPATTS[toktype].match(inp, pos)
        if mobj is not None:
            # leading white space would be included, yeah
            start = mobj.start()
            end = mobj.end()
            if toktype == "LPAR":
                return tokens.LPAR(start, end), end
            if toktype == "RPAR":
                return tokens.RPAR(start, end), end
            if toktype == "OP":
                return tokens.OP(start, end, mobj["OP"]), end
            if toktype == "SUNIT":
                scale = int(mobj["_SCALE"])
                unit = mobj["_UNIT"]
                tdval = sunit_to_td(scale, unit)
                return tokens.SUNIT(start, end, tdval), end
            #elif toktype == "DTIME":
            dtval = datetime.datetime.strptime(mobj["DTIME"], INDTFMT)
            return tokens.DTIME(start, end, dtval), end
    raise LexError(inp, pos)

def evaluate(op: tokens.OP, fst: tokens.Token, snd: tokens.Token) -> tokens.Token:
    if op.value == "+":
        if isinstance(fst, tokens.DTIME):
            if isinstance(snd, tokens.DTIME):  # D,D,+
                raise ValueError("Can't add two dates!")
            # elif isinstance(snd, tokens.SUNIT):
            else:  # D,S,+
                return tokens.DTIME(-1, -1, fst.value + snd.value)
        #elif isinstance(fst, tokens.SUNIT):
        else:
            if isinstance(snd, tokens.DTIME):  # S,D,+
                #tdval = sunit_to_td(fst)
                return tokens.DTIME(-1, -1, snd.value + fst.value)
            #elif isinstance(snd, tokens.SUNIT):
            else:  # S,S,+
                return tokens.SUNIT(-1, -1, fst.value + snd.value) 
    #elif op.value == "-":
    else:
        if isinstance(fst, tokens.DTIME):
            if isinstance(snd, tokens.DTIME):  # D,D,-
                return tokens.SUNIT(-1, -1, fst.value - snd.value)
            # elif isinstance(snd, tokens.SUNIT):
            else:  # D,S,-
                return tokens.DTIME(-1, -1, fst.value - snd.value)

        #elif isinstance(fst, tokens.SUNIT):
        else:
            if isinstance(snd, tokens.DTIME):  # S,D,-
                raise ValueError("Can't negate a lone datetime!")
            #elif isinstance(snd, tokens.SUNIT):
            else:  # S,S,-
                return tokens.SUNIT(-1, -1, fst.value - snd.value) 
            
def lexer(inp: str, TOKPATTS, INDTFMT: str) -> List[tokens.Token]:
    """
    Perform lexical analysis (tokenization).
    Accept an input string and produce a list of tokens

    Arguments:
      inp: input string
    Returns:
      List of tokens.Token objects in infix form.
    """
    rv = []
    while inp:
        tok, pos = next_tok(inp, TOKPATTS, INDTFMT)
        rv.append(tok)
        inp = inp[pos:].strip()
    return rv
    
def infix_to_postfix(toks: List[tokens.Token]) -> List[tokens.Token]:
    """
    Convert tokens from infix to postfix form. 

    Arguments:
      toks: list of tokens in infix form.
    Returns:
      list of tokens in postfix form.
    """
    toks.append(tokens.RPAR(-1,-1))
    post = []
    stack = [tokens.LPAR(-1, -1)]
    for tok in toks:
        if isinstance(tok, tokens.LPAR):
            stack.append(tok)
        elif isinstance(tok, tokens.DTIME) or isinstance(tok, tokens.SUNIT):
            post.append(tok)
        elif isinstance(tok, tokens.OP):
            try:
                # Both operators have same precedence currently
                while isinstance(stack[-1], tokens.OP):
                    stok = stack.pop()
                    post.append(stok)
                stack.append(tok)
            except IndexError:
                raise ValueError("Malformed input!")
        #elif isinstance(tok, tokens.RPAR):
        else:
            try:
                while not isinstance(stack[-1], tokens.LPAR):
                    stok = stack.pop()
                    post.append(stok)
                stack.pop()  # pop the tokens.LPAR
            except IndexError:
                raise ValueError("Unmatched parenthesis!")
    # stack should be empty at this point
    if stack:
        raise ValueError("Unmatched parenthesis!")
    return post

def eval_postfix(toks: List[tokens.Token]) -> Union[tokens.DTIME,
                                                    tokens.SUNIT]:
    stack = []
    for tok in toks:
        if isinstance(tok, tokens.SUNIT) or isinstance(tok, tokens.DTIME):
            stack.append(tok)
        #elif isinstance(tok, tokens.OP):
        else:
            snd = stack.pop()
            fst = stack.pop()
            val = evaluate(tok, fst, snd)
            stack.append(val)
    return stack[-1]
            
def lexeval(inp: str, in_dtfmt: str, out_dtfmt: str) -> str:
    """
    Driver function for performing input evaluation.

    Arguments:
      inp: input string
      in_dtfmt: input date format
      out_dtfmt: output date format

    Returns:
      String representation of resultant datetime or timedelta
    """

    TOKPATTS = {
        # No conflicts as of now. So order shouldn't matter
        "LPAR": re.compile(r' *(?P<LPAR>\()'),
        "RPAR": re.compile(r' *(?P<RPAR>\))'),
        "OP": re.compile(r' *(?P<OP>\+|-)'),
        "SUNIT": re.compile(r' *(?P<SUNIT>(?P<_SCALE>\d+)(?P<_UNIT>w|d|h|m))'),
        "DTIME": dtcalc.dtfmt.get_pattern(in_dtfmt),
    }


    infix_toks = lexer(inp, TOKPATTS, in_dtfmt)
    postfix_toks = infix_to_postfix(infix_toks)
    result = eval_postfix(postfix_toks)
    if isinstance(result, tokens.DTIME):
        res_str = result.value.strftime(out_dtfmt)
    #elif isinstance(result, tokens.SUNIT):
    else:
        res_str = dtcalc.dtfmt.fmt_td(result.value)
    return res_str
