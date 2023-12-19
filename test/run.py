import sys

sys.dont_write_bytecode = True

import argparse
from pathlib import Path
from executors import executors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("executor", choices=executors.keys())
    parser.add_argument("action", choices=["init", "test"])
    args = parser.parse_args()
    getattr(executors[args.executor], args.action)()


if __name__ == "__main__":
    main()
