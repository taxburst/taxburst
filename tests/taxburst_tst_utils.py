import os.path

example_dir = os.path.join(os.path.dirname(__file__), "../examples")


def get_example_filepath(filename):
    return os.path.abspath(os.path.join(example_dir, filename))
