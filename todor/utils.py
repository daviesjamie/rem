import hashlib
import os
import re
import subprocess
import tempfile
from operator import itemgetter

FOLDER_NAME = '.todor'

def create_root():
    root_path = os.path.join(os.getcwd(), FOLDER_NAME)

    if os.path.exists(root_path):
        raise RootAlreadyExists(root_path)

    os.mkdir(root_path)
    open(os.path.join(root_path, 'tasks'), 'a').close()
    open(os.path.join(root_path, 'done'), 'a').close()

def get_root_path():
    dir_path = os.getcwd()

    while(not os.path.exists(os.path.join(dir_path, FOLDER_NAME))):
        new_path = os.path.dirname(dir_path)
        if new_path == dir_path:
            raise RootNotFound

        dir_path = os.path.dirname(dir_path)

    return os.path.join(dir_path, FOLDER_NAME)

def get_system_editor():
    #editor = 'vi'
    #return (os.environ.get('VISUAL') or os.environ.get('EDITOR') or editor)
    return 'vim'

def hash(text):
    return hashlib.sha1(text).hexdigest()

def prefixes(ids):
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

def task_from_taskline(taskline):
    text = taskline.strip()

    if text == '' or text.startswith('#'):
        return None

    return { 'id': hash(text), 'text': text }

def tasklines_from_tasks(tasks):
    tasklines = []

    for task in tasks:
        tasklines.append('{0}\n'.format(task['text']))

    return tasklines

def temp_edit(text):
    (fd, name) = tempfile.mkstemp(prefix="todor-editor-", suffix=".txt", text=True)

    try:
        f = os.fdopen(fd, 'w')
        f.write(text)
        f.close()

        editor = get_system_editor()
        subprocess.check_call('{0} "{1}"'.format(editor, name), shell=True)

        f = open(name)
        t = f.read()
        f.close()
    finally:
        os.unlink(name)

    return t


class RootAlreadyExists(Exception):
    def __init__(self, path):
        super(RootAlreadyExists, self).__init__()
        self.path = path


class RootNotFound(Exception):
    pass


class UnknownPrefix(Exception):
   def __init__(self, prefix):
        super(UnknownPrefix, self).__init__()
        self.prefix = prefix


class AmbiguousPrefix(Exception):
    def __init__(self, prefix):
        super(AmbiguousPrefix, self).__init__()
        self.prefix = prefix
