"Unified remote integration as a commandline cli"
from sys import path

from custom_components.unified_remote.cli.args import arg_handler
from custom_components.unified_remote.cli.connection import Connection
from custom_components.unified_remote.cli.remotes import Remotes

if __name__ == "__main__":
    # Set remotes.yaml directory location.
    absolute_path = path[0] + "/custom_components/unified_remote/cli/"
    # Fetch parsed arguments.
    args = arg_handler()
    # Do remote parsing.
    remotes = Remotes(absolute_path + "remotes.yml")
    # Get remote with name given on arguments
    remote = remotes.get_remote(args.remote_name)
    # Check if remote exists
    if remote is None:
        raise Exception(
            f'Remote "{args.remote_name}" doesn\'t exists. Check your remotes.yml file.'
        )
    # Get remote id
    remote_id = remote["id"]
    # Get remote action
    remote_action = args.remote_action
    # Check if action exists in remote controls
    if remote_action not in remote["controls"]:
        raise Exception(
            f"Action {remote_action} doesn't exists for remote {args.remote_name}"
        )

    # Peform a connection with host client
    conn = Connection()
    conn.connect(host=args.host, port=args.port)
    # Send a request with remote parameters
    conn.exe_remote(remote_id, remote_action)
