import os

class Entry:

    REGULAR_MODE = "100644"
    EXECUTABLE_MODE = "100755"
    DIRECTORY_MODE = "40000"

    def __init__(self, name, oid, path):
        self.name = name
        self.oid = oid
        self.path = path

    def mode(self):
        return (
            Entry.EXECUTABLE_MODE
            if os.access(self.path, os.X_OK)
            else Entry.REGULAR_MODE
        )
