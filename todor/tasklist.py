import os
import re
from operator import itemgetter

from util import UnknownPrefix, AmbiguousPrefix
from util import get_root_path, hash, prefixes, task_from_taskline, tasklines_from_tasks


class TaskList(object):
    def __init__(self):
        self.root = get_root_path()
        self.tasks = {}
        self.done = {}

        filemap = (('tasks', 'tasks'), ('done', 'done'))
        for kind, filename in filemap:
            path = os.path.join(self.root, filename)
            if os.path.exists(path):
                with open(path, 'r') as task_file:
                    task_lines = [tl.strip() for tl in task_file if tl]
                    tasks = map(task_from_taskline, task_lines)
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
        task = task_from_taskline(text)
        if task:
            self.tasks[task['id']] = task

    def edit(self, prefix, text):
        task = self[prefix]

        if text.startswith('s/') or text.startswith('/'):
            text = re.sub('^s?/', '', text).rstrip('/')
            find, _, repl = text.partition('/')
            text = re.sub(find, repl, task['text'])

        task['text'] = text

    def finish(self, prefix):
        task = self.tasks.pop(self[prefix]['id'])
        self.done[task['id']] = task

    def remove(self, prefix):
        self.tasks.pop(self[prefix]['id'])

    def print_list(self,kind='tasks', grep='', long=False, short=False):
        tasks = getattr(self, kind)
        label = 'prefix' if not long else 'id'

        if not long:
            for task_id, prefix in prefixes(tasks).iteritems():
                tasks[task_id]['prefix'] = prefix

        label_length = max(map(lambda t: len(t[label]), tasks.values())) if tasks else 0

        for _, task in sorted(tasks.iteritems()):
            if grep.lower() in task['text'].lower():
                l = '{0} - '.format(task[label].rjust(label_length)) if not short else ''
                print l + task['text']

    def write(self):
        filemap = (('tasks', 'tasks'), ('done', 'done'))
        for kind, filename in filemap:
            path = os.path.join(self.root, filename)
            tasks = sorted(getattr(self, kind).values(), key=itemgetter('id'))
            with open(path, 'w') as task_file:
                for taskline in tasklines_from_tasks(tasks):
                    task_file.write(taskline)
