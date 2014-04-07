#!/usr/bin/env python

import argparse
import sys

from todor.exceptions import RootAlreadyExists, RootNotFound, UnknownPrefix, AmbiguousPrefix
from todor.helpers import _create_root
from todor.tasklist import TaskList

def _build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Initialise task list
    init = subparsers.add_parser('init')

    # Add a new task
    add = subparsers.add_parser('add')

    # Edit a task
    edit = subparsers.add_parser('edit')
    edit.add_argument('prefix')

    # Complete a task
    done = subparsers.add_parser('done')
    done.add_argument('prefix')

    # Delete a task
    rm = subparsers.add_parser('rm')
    rm.add_argument('prefix')

    # List tasks
    ls = subparsers.add_parser('ls')
    ls.add_argument('-g', '--grep', dest='grep', default='')
    ls.add_argument('-l', '--long', dest='long', action='store_true')
    ls.add_argument('-s', '--short', dest='short', action='store_true')
    ls.add_argument('-d', '--done', dest='kind', action='store_const', const='done', default='tasks')

    return parser

def _main():
    parser = _build_parser()
    args, text = parser.parse_known_args()
    text = ' '.join(text).strip()

    try:
        if args.command == 'init':
            _create_root()

        else:
            tl = TaskList()

            if args.command == 'add':
                tl.add(text)
                tl.write()

            elif args.command == 'edit':
                tl.edit(args.prefix, text)
                tl.write()

            elif args.command == 'done':
                tl.finish(args.prefix)
                tl.write()

            elif args.command == 'rm':
                tl.remove(args.prefix)
                tl.write()

            elif args.command == 'ls':
                tl.print_list(kind=args.kind, grep=args.grep, long=args.long, short=args.short)

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