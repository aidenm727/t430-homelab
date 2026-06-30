import argparse

from .commands import docs, doctor, explain, impact, missing, next, open, state, validate


COMMANDS = [
    state,
    doctor,
    next,
    docs,
    explain,
    impact,
    missing,
    open,
    validate,
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

if __name__ == "__main__":
    main()
