import argparse

from atlas.commands import doctor, state


COMMANDS = [
    state,
    doctor,
]


def build_parser():
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Atlas reduces engineering friction while increasing engineering understanding.",
    )

    subparsers = parser.add_subparsers(dest="command")

    for command in COMMANDS:
        command.register(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)