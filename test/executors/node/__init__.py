import os

executor_root = os.path.join(os.path.dirname(__file__))


def init():
    os.system(f"cd {executor_root} && npm install")


def test():
    os.system(f"cd {executor_root} && npm test")
