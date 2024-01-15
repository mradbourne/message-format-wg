# Data-driven tests

A conformance test suite for parsing and formatting messages sufficient to ensure implementations can validate conformance to the specification(s) provided.

All operations are performed using the `ddt.py` CLI, which can be found in this directory.

## Setup

Navigate to the test directory:

```bash
cd test/
```

Install `ddt.py` CLI dependencies:

```bash
pip install -r requirements.txt
```

## Test executors

This test framework includes the platform-specific test executors that can run the same test files as long as these files conform to the [DDT schema](./testgen/ddt.schema.json).

### Running tests with an existing executor

Use the following command where 'node' is the name of the executor:

```bash
python ddt.py run node test
```

To build and run with a single command, add the `-b`/`--build` flag:

```bash
python ddt.py run node test -b
```

To run a subset of tests, use the `-f`/`--files` flag:

```bash
python ddt.py run node test -f syntax/whitespace.test.json
```

### Creating and registering a new executor

The framework is extendable with new executors.

#### Creating

Each new executor is placed in the `executors/` directory. It takes the form of a directory with an `__init__.py` file that contains two functions, `init` and `test`.

The `init` function should set up the executor, including any dependency installation and build steps.

The `test` function runs tests within the executor. The function provides a `test_paths` parameter, which is a list of test files to run.

For example:

```python
# executors/node/__init__.py
def init():
    os.system(f"cd {executor_root} && npm install")


def test(test_paths):
    os.system(f"cd {executor_root} && npm test -- {' '.join(test_paths)}")
```

#### Registering

Each new executor needs to be added to the list in `executors/__init__.py`. The name given to the executor in this list is what should be passed to the `python ddt.py run` command when you run the tests. For example:

```python
# executors/__init__.py
from . import foo, bar

executors = {
    "fooexecutor": foo,
    "barexecutor": bar,
}
```

This file includes the 'foo' and 'bar' executors. To run tests with the 'foo' executor, use the following command:

```bash
python ddt.py run fooexecutor test
```
