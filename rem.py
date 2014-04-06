#!/usr/bin/env python

import argparse
import hashlib
import os
import sys


class RootAlreadyExists(Exception):
    def __init__(self, path):
        super(RootAlreadyExists, self).__init__()
        self.path = path


class RootNotFound(Exception):
    pass


def _create_root():
    root_path = os.path.join(os.getcwd(), '.rem')

    if os.path.exists(root_path):
        raise RootAlreadyExists(root_path)

    os.mkdir(root_path)
    open(os.path.join(root_path, 'tasks'), 'a').close()
    open(os.path.join(root_path, 'completed'), 'a').close()

def _get_root_path():
    dir_path = os.getcwd()

    while(not os.path.exists(os.path.join(dir_path, '.rem'))):
        new_path = os.path.dirname(dir_path)
        if new_path == dir_path:
            raise RootNotFound

        dir_path = os.path.dirname(dir_path)

    return os.path.join(dir_path, '.rem')

def _hash(text):
    return hashlib.sha1(text).hexdigest()

def _task_from_taskline(taskline):
    text = taskline.strip()

    if text.startswith('#'):
        return None

    text = taskline.strip()
    return { 'id': _hash(text), 'text': text }


class TaskList(object):
    def __init__(self):
        self.root = _get_root_path()
        self.tasks = {}
        self.done = {}

        filemap = (('tasks', 'tasks'), ('completed', 'completed'))
        for kind, filename in filemap:
            path = os.path.join(self.root, filename)
            if os.path.exists(path):
                with open(path, 'r') as task_file:
                    task_lines = [tl.strip() for tl in task_file if tl]
                    tasks = map(_task_from_taskline, task_lines)
                    for task in tasks:
                        if task is not None:
                            getattr(self, kind)[task['id']] = task['text']

    def print_list(self,kind='tasks', grep=None, detailed=False, simple=False):
        tasks = getattr(self, kind)

        for id, task in tasks.iteritems():
            print id, task


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
    output.add_argument('-g', '--grep', dest='grep', metavar='SEARCH TERM(S)')

    # Detailed task listing
    output.add_argument('-l', '--long', dest='detailed', action='store_true')

    # Simple task listing
    output.add_argument('-s', '--simple', dest='simple', action='store_true')

    # List completed tasks
    output.add_argument('--completed', dest='kind', action='store_const', const='completed', default='tasks')

    return parser

def _main():
    args, text = _build_parser().parse_known_args()

    try:
        if args.init:
            _create_root()
        else:
            task_list = TaskList()

            if args.complete:
                print 'complete', args.complete
            elif args.remove:
                print 'remove', args.remove
            elif args.edit:
                print 'edit', args.edit
            elif text:
                print 'new', text
            else:
                task_list.print_list(kind=args.kind)

    except RootNotFound:
        sys.stderr.write('Error: No task root could be found.\nTry using {0} --init first.\n'.format(sys.argv[0]))

    except RootAlreadyExists, e:
        sys.stderr.write('Error: The task root at {0} already exists!\n'.format(e.path))

if __name__ == '__main__':
    _main()
