"""
dtcalc CLI interface
"""

import argparse

from dtcalc.lexeval import lexeval, LexError

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-dtfmt", default="%Y/%m/%d")
    parser.add_argument("--out-dtfmt", default="%Y/%m/%d")
    parser.add_argument("input", nargs="+")

    args = parser.parse_args()
    try:
        result = lexeval(args.input, args.in_dtfmt, args.out_dtfmt)
        print(result)
    except (ValueError, LexError):
        print("Error: Malformed input")
