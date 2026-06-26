NAME = "state"
HELP = "Show current engineering state."


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def run(args):
    print("Atlas Engineering Toolkit")
    print()
    print("Engineering State")
    print()
    print("Status: OK")
    print()
    print("Command implementation coming next.")