#!/usr/bin/env python

import argparse
import hashlib
import os
import sys
from operator import itemgetter


class RootAlreadyExists(Exception):
    def __init__(self, path):
        super(RootAlreadyExists, self).__init__()
        self.path = path


class RootNotFound(Exception):
    pass


class UnknownPrefix(Exception):
    def __init(self, prefix):
        super(UnknownPrefix, self).__init__()
        self.prefix = prefix


class AmbiguousPrefix(Exception):
    def __init(self, prefix):
        super(AmbiguousPrefix, self).__init__()
        self.prefix = prefix

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

def _prefixes(ids):
    prefixes = {}
    for id in ids:
        id_len = len(id)

        for i in range(1, id_len + 1):
            # Finds an unused prefix, or a singular collision
            prefix = id[:i]
            if (not prefix in prefixes) or (prefixes[prefix] and prefix != prefixes[prefix]):
                break

        if prefix in prefixes:
            # If there is a collision
            other_id = prefixes[prefix]
            for j in range(i, id_len + 1):
                if other_id[:j] == id[:j]:
                    prefixes[id[:j]] = ''
                else:
                    prefixes[other_id[:j]] = other_id
                    prefixes[id[:j]] = id
                    break
        else:
            # No collision
            prefixes[prefix] = id

    prefixes = dict(zip(prefixes.values(), prefixes.keys()))
    if '' in prefixes:
        del prefixes['']

    return prefixes

def _task_from_taskline(taskline):
    text = taskline.strip()

    if text == '' or text.startswith('#'):
        return None

    return { 'id': _hash(text), 'text': text }

def _tasklines_from_tasks(tasks):
    tasklines = []

    for task in tasks:
        tasklines.append('{0}\n'.format(task['text']))

    return tasklines


class TaskList(object):
    def __init__(self):
        self.root = _get_root_path()
        self.tasks = {}
        self.completed = {}

        filemap = (('tasks', 'tasks'), ('completed', 'completed'))
        for kind, filename in filemap:
            path = os.path.join(self.root, filename)
            if os.path.exists(path):
                with open(path, 'r') as task_file:
                    task_lines = [tl.strip() for tl in task_file if tl]
                    tasks = map(_task_from_taskline, task_lines)
                    for task in tasks:
                        if task is not None:
                            getattr(self, kind)[task['id']] = task

    def __getitem__(self, prefix):
        matched = filter(lambda tid: tid.startswith(prefix), self.tasks.keys())
        if len(matched) == 1:
            return self.tasks[matched[0]]
        elif len(matched) == 0:
            raise UnknownPrefix(prefix)
        else:
            matched = filter(lambda tid: tid == prefix, self.tasks.keys())
            if len(matched) == 1:
                return self.tasks[matched[0]]
            else:
                raise AmbiguousPrefix(prefix)

    def add(self, text):
        task_id = _hash(text)
        self.tasks[task_id] = { 'id': task_id, 'text': text }

    def finish(self, prefix):
        task = self.tasks.pop(self[prefix]['id'])
        self.completed[task['id']] = task

    def remove(self, prefix):
        self.tasks.pop(self[prefix]['id'])

    def print_list(self,kind='tasks', grep='', detailed=False, simple=False):
        tasks = getattr(self, kind)
        label = 'prefix' if not detailed else 'id'

        if not detailed:
            for task_id, prefix in _prefixes(tasks).iteritems():
                tasks[task_id]['prefix'] = prefix

        label_length = max(map(lambda t: len(t[label]), tasks.values())) if tasks else 0

        for _, task in sorted(tasks.iteritems()):
            if grep.lower() in task['text'].lower():
                l = '{0} - '.format(task[label].ljust(label_length)) if not simple else ''
                print l + task['text']

    def write(self):
        filemap = (('tasks', 'tasks'), ('completed', 'completed'))
        for kind, filename in filemap:
            path = os.path.join(self.root, filename)
            tasks = sorted(getattr(self, kind).values(), key=itemgetter('id'))
            with open(path, 'w') as task_file:
                for taskline in _tasklines_from_tasks(tasks):
                    task_file.write(taskline)


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
                print 'edit', args.edit

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
