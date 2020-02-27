from yaml import load, dump, FullLoader


def yaml_load(path: str):
    with open(path, "r") as file:
        data = load(file, Loader=FullLoader)
        return data

# debugging
if __name__ == "__main__":
    print(yaml_load("remotes.yml"))
