import struct
from lib.entry import Entry
from pathlib import Path


class Tree:

    mode = "100644"

    @classmethod
    def build(cls, entries):

        print("tree entries", entries)

        root = cls()

        for entry in entries:
            print("root", root.entries)
            root.add_entry(entry.parent_directories(), entry)

        return root

    def __init__(self):
        self.entries = {}
        self.mode = 0o4000

    def add_entry(self, parents, entry):
        if len(parents) == 0:
            self.entries[entry.basename()] = entry
        else:
            if self.entries.get(parents[0].name):
                tree = self.entries[parents[0].name]
            else:
                tree = Tree()
                self.entries[Path(parents[0].name)] = tree
            tree.add_entry(parents[1:], entry)

    def traverse(self, cb):
        for name, entry in self.entries.items():
            if type(entry) == Tree:
                entry.traverse(cb)
        cb(self)

    def type(self):
        return "tree"


    def to_s(self):
        def format_entry(name_entry):
            name, entry = name_entry
            print("entry", entry)
            print("name", name)
            print("entry.oid", entry.oid)
            mode = oct(entry.mode)[2:]
            s = struct.pack(
                "%ds%dsx20s" % (len(mode) + 1, len(name.as_posix())),
                (mode + " ").encode("utf-8"),
                name.as_posix().encode("utf-8"),
                entry.oid if type(entry.oid) == bytes else bytes.fromhex(entry.oid), # TODO: must fix this smell
            )

            return s


        print("this my tree",  b"".join(list((map(format_entry, self.entries.items())))))
        return b"".join(list((map(format_entry, self.entries.items()))))
