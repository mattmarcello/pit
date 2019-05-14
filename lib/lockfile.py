from pathlib import Path
from os import rename


class Lockfile:
    class MissingParent(Exception):
        pass

    class NoPermission(Exception):
        pass

    class StaleLock(Exception):
        pass

    class LockDenied(Exception):
        pass

    def __init__(self, path, use_bytes=True):

        self.use_bytes = use_bytes
        self.lock = None
        self.file_path = path
        self.lock_path = path.with_suffix(".lock")

    def hold_for_update(self):
        try:
            if not self.lock:
                self.lock = (
                    open(self.lock_path, "xb+")
                    if self.use_bytes
                    else open(self.lock_path, "x+")
                )
            return True
        except FileExistsError:
            raise Lockfile.LockDenied("Unable to create '%s': File exists." % self.lock_path )
        except FileNotFoundError as e:
            raise (Lockfile.MissingParent(str(e)))
        except IOError as e:
            raise (Lockfile.NoPermission(str(e)))

    def write(self, string):
        self.__raise_on_stale_lock()

        self.lock.write(string)

    def commit(self):
        self.__raise_on_stale_lock()

        rename(self.lock_path, self.file_path)
        self.lock.close()
        self.lock = None

    def rollback(self):
        self.__raise_on_stale_lock()
        Path.unlink(self.lock_path)
        self.lock.close()
        self.lock = None;



    def __raise_on_stale_lock(self):
        if not self.lock:
            raise Lockfile.StaleLock("Not holding on file: %s" % self.lock_path)

    
