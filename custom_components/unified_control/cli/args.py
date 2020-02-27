from argparse import ArgumentParser


def arg_handler():
    # Tool information
    parser = ArgumentParser()

    # Client host options
    host = parser.add_argument_group(title="Client host Parameters [optional]")
    host.add_argument('--host', '-c', action = 'store', dest = 'host',
                        required= False, help = "Default will be localhost", default="localhost")
    host.add_argument('--port', '-p', action = 'store', dest = 'port',
                        required= False, help = "Default will be 9510", default="9510")
    # Remote Option
    remote = parser.add_argument_group(title='Remote Parameters') 
    remote.add_argument('remote_id', metavar="Remote-ID", help='Ex.: \"Unified.Netflix\"')
    remote.add_argument('remote_action', metavar="Remote-Action", help='Ex.: \"play_pause\"')

    return parser.parse_args()
