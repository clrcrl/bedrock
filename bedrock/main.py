import os
import sys

import argparse

from bedrock.core_configure import configure
from bedrock.core_generate import generate


def parse_args(args):

    p = argparse.ArgumentParser(
        prog="bedrock: build your redshift cluster on solid ground",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Select one of these sub-commands and you can find more help from there.",
    )

    base_subparser = argparse.ArgumentParser(add_help=False)

    base_subparser.add_argument("--host", type=str, required=True)

    base_subparser.add_argument("--port", type=int, required=True)

    base_subparser.add_argument("--dbname", type=str, required=True)

    base_subparser.add_argument("--user", type=str, required=True)

    base_subparser.add_argument("--password", type=str, required=True)

    subs = p.add_subparsers(title="Available sub-commands", dest="command")

    generate_sub = subs.add_parser(
        "generate", parents=[base_subparser], help="Generate a YAML spec for a database"
    )

    configure_sub = subs.add_parser(
        "configure",
        parents=[base_subparser],
        help="Configure a database to match a YAML spec",
    )

    configure_sub.add_argument("--spec", type=str, required=True)

    configure_sub.add_argument("--live", dest="live", action="store_true")

    configure_sub.add_argument("--check", dest="live", action="store_false")

    configure_sub.set_defaults(live=False)

    if len(args) == 0:
        p.print_help()
        sys.exit(1)
        return

    parsed = p.parse_args(args)
    return parsed


def handle(args):
    parsed = parse_args(args)
    if parsed.command == "generate":
        generate(parsed.host, parsed.port, parsed.user, parsed.password, parsed.dbname)

    if parsed.command == "configure":
        configure(
            parsed.spec,
            parsed.host,
            parsed.port,
            parsed.user,
            parsed.password,
            parsed.dbname,
            parsed.live,
        )


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    handle(args)


if __name__ == "__main__":
    main()
