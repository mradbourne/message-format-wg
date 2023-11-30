import glob, os, json
import yaml

# with open('testgen/config.yml', 'r') as yaml_file:
#     configuration = yaml.safe_load(yaml_file)

# with open('testgen/config.json', 'w') as json_file:
#     json.dump(configuration, json_file)


# output = json.dumps(json.load(open('testgen/config.json')), indent=2)
# print(output)
def main():
    test_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "testgen", "src")
    )
    os.chdir(test_dir)
    for test_file in glob.glob("./**/*.test.yml", recursive=True):
        build_json(test_file)


def build_json(file):
    with open(file, "r") as yaml_file:
        test_dict = yaml.safe_load(yaml_file)
        print(type(configuration))


if __name__ == "__main__":
    main()
