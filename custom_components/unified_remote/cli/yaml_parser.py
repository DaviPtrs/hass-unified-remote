"Load yaml files"
from yaml import FullLoader, load


def yaml_load(path: str):
    """Reads yaml file in path and return it content in string form."""

    with open(path, "r") as file:
        data = load(file, Loader=FullLoader)
        return data
