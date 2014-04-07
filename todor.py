#!/usr/bin/env python

import argparse
import sys

from todor.exceptions import RootAlreadyExists, RootNotFound, UnknownPrefix, AmbiguousPrefix
from todor.tasklist import TaskList

def _build_parser():
    parser = argparse.ArgumentParser()

    # ACTIONS
    ##########
    actions = parser.add_argument_group('Actions')

    # Initialise task file
    actions.add_argument('--init', dest='init', action='store_true')

    # Edit a task
    actions.add_argument('-e', '--edit', dest='edit', metavar='TASK HASH')

    # Complete a task
    actions.add_argument('-c', '--complete', dest='complete', metavar='TASK HASH')

    # Delete a task
    actions.add_argument('-rm', '--remove', dest='remove', metavar='TASK HASH')

    # OUTPUT OPTIONS
    #################
    output = parser.add_argument_group('Output Options')

    # Grep for a task
    output.add_argument('-g', '--grep', dest='grep', metavar='SEARCH TERM(S)', default='')

    # Detailed task listing
    output.add_argument('-l', '--long', dest='detailed', action='store_true')

    # Simple task listing
    output.add_argument('-s', '--simple', dest='simple', action='store_true')

    # List completed tasks
    output.add_argument('--completed', dest='kind', action='store_const', const='completed', default='tasks')

    return parser

def _main():
    args, text = _build_parser().parse_known_args()
    text = ' '.join(text).strip()

    try:
        if args.init:
            _create_root()
        else:
            task_list = TaskList()

            if args.complete:
                task_list.finish(args.complete)
                task_list.write()

            elif args.remove:
                task_list.remove(args.remove)
                task_list.write()

            elif args.edit:
                task_list.edit(args.edit, text)
                task_list.write()

            elif text:
                task_list.add(text)
                task_list.write()

            else:
                task_list.print_list(kind=args.kind, grep=args.grep, detailed=args.detailed, simple=args.simple)

    except RootNotFound:
        sys.stderr.write('Error: No task root could be found.\nTry using {0} --init first.\n'.format(sys.argv[0]))

    except RootAlreadyExists, e:
        sys.stderr.write('Error: The task root at {0} already exists!\n'.format(e.path))

    except UnknownPrefix, e:
        sys.stderr.write('Error: The prefix "{0}" does not match any tasks!\n'.format(e.prefix))

    except AmbiguousPrefix, e:
        sys.stderr.write('Error: The prefix "{0}" is ambiguous, it matches more than one task!\n'.format(e.prefix))

if __name__ == '__main__':
    _main()
