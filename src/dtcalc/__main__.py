import argparse

from dtcalc.lexeval import lexeval

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-dtfmt", default="%Y/%m/%d")
    parser.add_argument("--out-dtfmt", default="%w weeks, %d days, %H hours, %M minutes")
    parser.add_argument("input")

    args = parser.parse_args()
    try:
        result = lexeval(args.input, args.in_dtfmt, args.out_dtfmt)
        print(result)
    except Exception as expt:
        print(f"Error: {expt.args[0]}")
