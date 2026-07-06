from collections import defaultdict

from atlas.platform.repository_objects import load_repository_objects


NAME = "opportunities"
HELP = "Show Engineering Opportunity repository objects."


LIFECYCLE_ORDER = [
    "captured",
    "reviewed",
    "accepted",
    "architected",
    "scheduled",
    "implemented",
    "closed",
]


def register(subparsers):
    parser = subparsers.add_parser(NAME, help=HELP)
    parser.set_defaults(func=run)


def print_opportunity(entity) -> None:
    print(f"- {entity.id}: {entity.title}")
    print(f"  Path: {entity.path}")
    print(f"  Capability: {entity.capability}")
    print(f"  Created: {entity.created}")
    print(f"  Source: {entity.source}")

    if entity.missing_fields:
        print(f"  Missing Fields: {', '.join(entity.missing_fields)}")


def run(args):
    entities, errors = load_repository_objects("engineering-opportunity")
    grouped = defaultdict(list)

    for entity in entities:
        grouped[entity.status].append(entity)

    print("Atlas Engineering Opportunities")
    print("===============================")
    print()

    print("Summary")
    print("-------")
    print(f"Total: {len(entities)}")
    print(f"Load Errors: {len(errors)}")
    print()

    for status in LIFECYCLE_ORDER:
        opportunities = grouped.get(status, [])

        print(status.title())
        print("-" * len(status))

        if not opportunities:
            print("- None")
        else:
            for entity in opportunities:
                print_opportunity(entity)

        print()

    extra_statuses = sorted(set(grouped) - set(LIFECYCLE_ORDER))
    for status in extra_statuses:
        print(status.title())
        print("-" * len(status))
        for entity in grouped[status]:
            print_opportunity(entity)
        print()

    if errors:
        print("Errors")
        print("------")
        for error in errors:
            print(f"- {error.path}: {error.message}")
