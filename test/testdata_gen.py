import glob
import os
import json
from pathlib import Path
from yaml import safe_load, scanner
from jsonschema import Draft202012Validator, ValidationError

JSON_INDENT = 2


def main():
    test_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "testgen", "src")
    )
    os.chdir(test_dir)
    test_files = glob.glob("./**/*.ddt.yml", recursive=True)

    if len(test_files) == 0:
        print("No tests found.")

    schema_path = os.path.join(os.path.dirname(__file__), "testgen", "ddt.schema.json")
    validator = Draft202012Validator(json.load(open(schema_path)))

    for src_path in test_files:
        with open(src_path, "r") as file:
            try:
                tests = safe_load(file)
                validator.validate(tests)
                build_test_json(src_path, tests)
                build_verify_json(src_path, tests)
            except scanner.ScannerError as err:
                print_error(f"Could not load {src_path}", err)
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


if __name__ == "__main__":
    main()
