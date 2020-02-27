from remotes import Remotes
from connection import Connection
from args import arg_handler
from sys import path

if __name__ == "__main__":
    # Fetching absolute path where this file is located
    absolute_path = path[0] + "/"
    args = arg_handler()
    remotes = Remotes(absolute_path + "remotes.yml")
    remote = remotes.get_remote(args.remote_name)
    remote_id = remote['id']
    remote_action = args.remote_action
    if not remote_action in remote['controls']:
        raise Exception(f"Action {remote_action} doesn't exists for remote {args.remote_name}")

    conn = Connection(host=args.host, port=args.port)
    conn.exe_remote(remote_id, remote_action)
    pass