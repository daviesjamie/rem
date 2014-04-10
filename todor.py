#!/usr/bin/env python

import argparse
import sys

from todor.tasklist import TaskList
from todor.utils import RootAlreadyExists, RootNotFound, UnknownPrefix, AmbiguousPrefix, create_root, temp_edit

def _build_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Initialise task list
    init = subparsers.add_parser('init')

    # Add a new task
    add = subparsers.add_parser('add')
    add.add_argument('-f', '--file', dest='file', nargs='?', const='TEMPORARY_EDIT_FILE')

    # Edit a task
    edit = subparsers.add_parser('edit')
    edit.add_argument('prefix')

    # Complete a task
    done = subparsers.add_parser('done')
    done.add_argument('prefixes', nargs='+')

    # Delete a task
    rm = subparsers.add_parser('rm')
    rm.add_argument('prefixes', nargs='+')

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
            create_root()

        else:
            tl = TaskList()

            if args.command == 'add':
                if args.file:
                    if args.file == 'TEMPORARY_EDIT_FILE':
                        template = []
                        template.append("")
                        template.append("# Enter your todo tasks here.")
                        template.append("# Each line will be treated as a separate task.")
                        template.append("# Lines starting with a # will be ignored.")
                        template.append("#")
                        template.append("# Todor, todor? TODOR!")

                        tasklines = temp_edit("\n".join(template)).splitlines()

                        for taskline in tasklines:
                            tl.add(taskline)
                else:
                    tl.add(text)

                tl.write()

            elif args.command == 'edit':
                tl.edit(args.prefix, text)
                tl.write()

            elif args.command == 'done':
                for prefix in args.prefixes:
                    tl.finish(prefix)
                tl.write()

            elif args.command == 'rm':
                for prefix in args.prefixes:
                    tl.remove(prefix)
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
