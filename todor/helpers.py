import hashlib
import os
import re
from operator import itemgetter

from .exceptions import RootAlreadyExists, RootNotFound, UnknownPrefix, AmbiguousPrefix

FOLDER_NAME = '.todor'

def _create_root():
    root_path = os.path.join(os.getcwd(), FOLDER_NAME)

    if os.path.exists(root_path):
        raise RootAlreadyExists(root_path)

    os.mkdir(root_path)
    open(os.path.join(root_path, 'tasks'), 'a').close()
    open(os.path.join(root_path, 'completed'), 'a').close()

def _get_root_path():
    dir_path = os.getcwd()

    while(not os.path.exists(os.path.join(dir_path, FOLDER_NAME))):
        new_path = os.path.dirname(dir_path)
        if new_path == dir_path:
            raise RootNotFound

        dir_path = os.path.dirname(dir_path)

    return os.path.join(dir_path, FOLDER_NAME)

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