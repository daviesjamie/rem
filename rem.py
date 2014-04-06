import argparse
import sys

def _build_parser():
    parser = argparse.ArgumentParser()

    # ACTIONS
    actions = parser.add_argument_group('Actions')

    # Edit a task
    actions.add_argument('-e', '--edit', dest='edit', metavar='TASK')

    # Complete a task
    actions.add_argument('-c', '--complete', dest='complete', metavar='TASK')

    # Delete a task
    actions.add_argument('-d', '--delete', '-rm', dest='delete', metavar='TASK')


    # OUTPUT OPTIONS
    output = parser.add_argument_group('Output Options')

    # Grep for a task
    output.add_argument('-g', '--grep', dest='grep', metavar='SEARCH TERM(S)')

    # Detailed task listing
    output.add_argument('-l', '--long', dest='detailed', action='store_true')

    # Simple task listing
    output.add_argument('-s', '--simple', dest='simple', action='store_true')

    # List completed tasks
    output.add_argument('--completed', dest='completed', action='store_true')


    return parser


def main():
    args, text = _build_parser().parse_known_args()
    print args
    print text


if __name__ == '__main__':
    main()
