import sys

sys.dont_write_bytecode = True

import argparse
import glob
import os
import json
from pathlib import Path
from yaml import safe_load, scanner
from jsonschema import Draft202012Validator, ValidationError
from executors import executors

JSON_INDENT = 2


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command")
    build_parser = subparser.add_parser("build")
    run_parser = subparser.add_parser("run")

    build_parser.add_argument(
        "-f", "--files", nargs="+", required=False, help="Source files to build"
    )

    run_parser.add_argument("executor", choices=executors.keys())
    run_parser.add_argument("action", choices=["init", "test"])
    run_parser.add_argument("-b", "--build", action=argparse.BooleanOptionalAction)
    run_parser.add_argument(
        "-f", "--files", nargs="+", required=False, help="Test files to run"
    )

    args = parser.parse_args()

    if args.command == "run":
        if args.build:
            build(args.files)
        run(args.executor, args.action, args.files)
    elif args.command == "build":
        build(args.files)


def run(executor, action, files):
    print(f"\nSending {action} command to {executor} executor...")
    test_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "DDT_DATA"))
    os.chdir(test_dir)
    test_files = (
        [os.path.join(test_dir, file) for file in files]
        if files
        else glob.glob("./**/*.ddt.yml", recursive=True)
    )
    getattr(executors[executor], action)(test_files)


def build(files):
    print("\nBuilding JSON from YAML...")
    test_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "testgen", "src")
    )
    os.chdir(test_dir)
    test_files = files or glob.glob("./**/*.ddt.yml", recursive=True)

    if len(test_files) == 0:
        print("No tests found.")

    schema_path = os.path.join(os.path.dirname(__file__), "testgen", "ddt.schema.json")
    validator = Draft202012Validator(json.load(open(schema_path)))

    for src_path in test_files:
        try:
            with open(os.path.join(test_dir, src_path), "r") as file:
                tests = safe_load(file)
                validator.validate(tests)
                build_test_json(src_path, tests)
                build_verify_json(src_path, tests)
        except FileNotFoundError as err:
            print_error(f"Could not find file {src_path}", err)
        except scanner.ScannerError as err:
            print_error(f"Could not load content from {src_path}", err)
        except ValidationError as err:
            print_error(f"Could not validate {src_path}", err)
        except Exception as err:
            print_error(f"Could not build {src_path}", err)


def print_error(user_message, err):
    err_str = f"{type(err).__name__}: {err.args}"
    print(f"{user_message}:\n", err_str, "\n")


def build_test_json(src_path, tests):
    destination = get_destination_path(src_path, ".test.json")
    build_json(
        tests,
        destination,
        scenario_fields=["scenario", "description"],
        test_fields=["label", "description", "locale", "pattern", "inputs"],
    )


def build_verify_json(src_path, tests):
    destination = get_destination_path(src_path, ".verify.json")
    build_json(
        tests,
        destination,
        scenario_fields=["scenario"],
        test_fields=["label", "verify"],
    )


def get_destination_path(src_path, file_extension):
    rel_dir = os.path.dirname(src_path)
    basename = file_extension.join(os.path.basename(src_path).rsplit(".ddt.yml", 1))
    return Path(os.path.dirname(__file__), "DDT_DATA", rel_dir, basename)


def build_json(tests, destination_path, scenario_fields, test_fields):
    output = {sf: tests.get(sf) for sf in scenario_fields if tests.get(sf) != None}
    verifications = [
        {tf: test.get(tf) for tf in test_fields if test.get(tf) != None}
        for test in tests["tests"]
    ]
    output["verifications"] = verifications

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with open(destination_path, "w") as json_file:
        json.dump(output, json_file, indent=JSON_INDENT)

    print(f"Written {destination_path}")


if __name__ == "__main__":
    main()
