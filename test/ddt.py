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
            build([get_source_path(file) for file in args.files])
        run(args.executor, args.action, args.files)
    elif args.command == "build":
        build([file for file in args.files] if args.files else None)


def run(executor, action, relative_paths):
    print(f"\nSending {action} command to {executor} executor...")
    full_paths = get_full_paths_default_all(relative_paths, test_build_dir)
    getattr(executors[executor], action)(full_paths)


def build(relative_paths):
    print("\nBuilding JSON from YAML...")
    full_paths = get_full_paths_default_all(relative_paths, test_src_dir)

    if len(full_paths) == 0:
        print("No tests found.")

    schema_path = os.path.join(os.path.dirname(__file__), "testgen", "ddt.schema.json")
    validator = Draft202012Validator(json.load(open(schema_path)))

    for full_path in full_paths:
        try:
            with open(full_path, "r") as file:
                tests = safe_load(file)
                validator.validate(tests)
                build_test_json(full_path, tests)
                build_verify_json(full_path, tests)
        except FileNotFoundError as err:
            print_error(f"Could not find file {full_path}", err)
        except scanner.ScannerError as err:
            print_error(f"Could not load content from {full_path}", err)
        except ValidationError as err:
            print_error(f"Could not validate {full_path}", err)
        except Exception as err:
            print_error(f"Could not build {full_path}", err)


test_src_dir = os.path.join(os.path.dirname(__file__), "testgen", "src")
test_build_dir = os.path.join(os.path.dirname(__file__), "DDT_DATA")


def get_full_paths_default_all(rel_paths, base_dir):
    os.chdir(test_src_dir)
    rel_paths = rel_paths or glob.glob("./**/*.ddt.yml", recursive=True)
    return [
        os.path.normpath(os.path.join(base_dir, rel_path)) for rel_path in rel_paths
    ]


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


def get_source_path(destination_path):
    rel_dir = os.path.dirname(destination_path)
    basename = ".ddt.yml".join(
        os.path.basename(destination_path).rsplit(".test.json", 1)
    )
    return Path(test_src_dir, rel_dir, basename)


def get_destination_path(src_path, file_extension):
    full_build_dir = test_build_dir.join(os.path.dirname(src_path).split(test_src_dir))
    basename = file_extension.join(os.path.basename(src_path).rsplit(".ddt.yml", 1))
    return Path(full_build_dir, basename)


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
