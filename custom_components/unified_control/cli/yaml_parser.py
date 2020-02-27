from yaml import load, dump, FullLoader


def yaml_load(path: str):
    with open(path, "r") as file:
        data = load(file, Loader=FullLoader)
        return data
