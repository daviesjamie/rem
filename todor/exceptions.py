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

