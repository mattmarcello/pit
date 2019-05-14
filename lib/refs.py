import os
from pathlib import Path

from lib.lockfile import Lockfile


class Refs:
    class LockDenied(Exception):
        pass

    def __init__(self, pathname):
        self.pathname = pathname

    def read_head(self):
        """TODO: add error handling"""
        if os.path.isfile(self.__head_path()):
            with open(self.__head_path(), "r") as f:
                return f.read().strip()

    def update_head(self, oid):
        lockfile = Lockfile(Path(self.__head_path()), use_bytes=False)

        lockfile.hold_for_update():
        lockfile.write(oid)
        lockfile.write("\n")
        lockfile.commit()

    def __head_path(self):
        return os.path.join(self.pathname, "HEAD")
