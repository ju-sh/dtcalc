import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-dtfmt", default="%Y/%m/%d")
    parser.add_argument("--out-dtfmt", default="%Y %d %H %M %S")
    parser.add_argument("input")

    args = parser.parse_args()
    print(args)
