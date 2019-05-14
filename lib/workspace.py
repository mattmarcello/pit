import pathspec

from os import walk, path
import os
import codecs
from pathlib import Path


class Dir:
    @classmethod
    def entries(cls, path):
        return os.listdir(path)


class Workspace:
    class MissingFile(Exception):
        pass

    class NoPermission(Exception):
        pass

    IGNORE = [".", "..", ".git"]

    SPEC = pathspec.PathSpec(map(pathspec.patterns.GitWildMatchPattern, IGNORE))

    def __init__(self, pathname):
        self.pathname = pathname

    def list_files(self, pathname=None):

        blacklist_predicate = lambda f: not Workspace.SPEC.match_file(f)

        path = pathname or self.pathname

        if os.path.isdir(path):
            paths = []
            for (root, dirnames, filenames) in walk(path):
                fs = list(map(lambda path: os.path.join(root, path), filenames))
                filtered_fs = list(filter(blacklist_predicate, fs))
                paths.extend(filtered_fs)
            return paths
        elif os.path.exists(path):
            return [path]

        else:
            raise (Workspace.MissingFile("pathspec %s did not match any files" % path))

    def read_file(self, path):
        try:
            f = codecs.open(os.path.join(self.pathname, path), "r", "latin-1")
            return f.read()
        except PermissionError:
            raise Workspace.NoPermission("open('%s'): Permission Denied" % path)

    def stat_file(self, path):
        try:
            return os.stat(os.path.join(self.pathname, path))
        except PermissionError:
            raise Workspace.NoPermission("stat('%s'): Permission Denied" % path)
