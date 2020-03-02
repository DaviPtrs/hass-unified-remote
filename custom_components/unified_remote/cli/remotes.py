"Define and parse remote definitions"
from custom_components.unified_remote.cli.yaml_parser import yaml_load


class Remotes:
    """This class convert remotes description from a yaml file to a list of remotes.
    \nEach remote is represented by a dictionary, containing keys named by \"name\",
    \"id\", \"[type]\" and \"controls\".
    """

    def __init__(self, yaml_path="remotes.yml"):
        yaml_data = yaml_load(yaml_path)
        self.__types = None
        self.__remotes = None
        if yaml_data is None:
            raise FileNotFoundError()
        else:
            self.__types = self.__type_parser(yaml_data)
            self.__remotes = self.__remote_parser(yaml_data)

    def __type_parser(self, yaml_data: dict):
        """Return all types declared in yaml file."""

        types = yaml_data.get("types")
        if types is None:
            types = dict()
        return types

    def __remote_validator(self, remote: dict):
        """Check if remote has an id, and if it has a type or a control list."""

        assert "id" in remote.keys()
        assert "type" in remote.keys() or remote["controls"] != []

    def get_remote(self, name):
        """Return remote by name"""

        return self.__remotes.get(name)

    def __append_remote_type(self, remotes):
        """Append to remote control list, all controls declarated on his type, if it has a type."""

        if remotes is None:
            raise Exception(
                "None remotes was parsed, please check your remotes.yml file"
            )
        for name, remote in remotes.items():
            # If there's no control list declared, then create an empty list to it.
            if "controls" not in remote.keys():
                remote["controls"] = list()
            remote_type = remote.get("type")
            # If and get chain to access control list of a remote type.
            if remote_type is not None:
                type_params = self.__types.get(remote_type)
                if type_params is not None:
                    type_controls = type_params.get("controls")
                    if type_controls is not None:
                        # Appending...
                        for control in type_controls:
                            remote["controls"].append(control)
            try:
                # Validates remote after control parsing.
                self.__remote_validator(remote)
            except AssertionError:
                # Customizing AssertionError message to be logged after.
                raise AssertionError(f'Invalid parsing for remote "{name}"')

    def __remote_parser(self, yaml_data: dict):
        """Fetch declared remotes then parse all the data to properly remote structure."""

        yaml_remotes = yaml_data.get("remotes")
        self.__append_remote_type(yaml_remotes)
        return yaml_remotes
