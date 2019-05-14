from hashlib import sha1
from collections import namedtuple
import struct
from pathlib import Path

from lib.lockfile import Lockfile
from lib._index.entry import Entry
from lib._index.checksum import Checksum


class Index:
    Entry = Entry
    Checksum = Checksum

    HEADER_SIZE = 12
    HEADER_FORMAT = "> 4s 2I"
    SIGNATURE = b"DIRC"
    VERSION = 2

    ENTRY_FORMAT = lambda l: "> 10I 20s h %dsx" % l
    ENTRY_BLOCK = 8
    ENTRY_MIN_SIZE = 64

    def __init__(self, pathname):
        self.entries = {}
        self.keys = set()
        self.parents = {}
        self.lockfile = Lockfile(Path(pathname))
        self.pathname = pathname

    def clear(self):
        self.entries = {}
        self.parents = {}
        self.keys = set()
        self.changed = False

    def add(self, pathname, oid, stat):
        entry = Entry.create(pathname, oid, stat)

        self.discard_conflicts(entry)

        self.store_entry(entry)
        self.changed = True

    def write_updates(self):

        if not self.changed:
            return self.lockfile.rollback()

        writer = Checksum(self.lockfile)

        header = struct.pack(Index.HEADER_FORMAT, b"DIRC", 2, len(self.entries))
        writer.write(header)

        self.each_entry(lambda entry: writer.write(entry.to_s()))

        writer.write_checksum()

        self.lockfile.commit()

        self.changed = False

    def begin_write(self):
        self.digest = sha1()

    def each_entry(self, cb):
        for key in sorted(self.keys):
            entry = self.entries[key]
            cb(entry)

    def get_entries(self):
        entries = []
        for key in sorted(self.keys):
            entries.append(self.entries[key])
        return entries

    def load_for_update(self):
        self.lockfile.hold_for_update()
        self.load()

    def load(self):
        self.clear()

        f = self.open_index_file()

        if f:

            reader = Checksum(f)
            count = self.read_header(reader)
            self.read_entries(reader, count)
            reader.verify_checksum()
            f.close()

    def open_index_file(self):
        try:
            return open(self.pathname, "rb")
        except FileNotFoundError:
            return None

    def read_header(self, reader):
        data = reader.read(Index.HEADER_SIZE)
        signature, version, count = struct.unpack(Index.HEADER_FORMAT, data)

        if not signature == Index.SIGNATURE:
            raise (
                Invalid(
                    "Signature: expected %s but found %s" % (Index.SIGNATURE, signature)
                )
            )

        if not version == Index.VERSION:
            raise (
                Invalid("Version: expected %s but found %s" % (Index.VERSION, version))
            )

        return count

    def read_entries(self, reader, count):
        for _ in range(count):
            entry = reader.read(Index.ENTRY_MIN_SIZE)
            while not bytearray(entry)[-1] == 0:
                entry = entry + reader.read(Index.ENTRY_BLOCK)

            self.store_entry(Entry.parse(entry))

    def store_entry(self, entry):
        self.keys.add(entry.key())
        self.entries[entry.key()] = entry

        for dirname in entry.parent_directories():
            n = dirname.name.encode("utf-8")

            s = self.parents.get(n, set())

            s.add(entry.path)

            self.parents[n] = s

    def discard_conflicts(self, entry):
        for parent in entry.parent_directories():
            self.remove_entry(parent.name.encode("utf-"))

        x = self.parents.get(entry.path, set())

        for child in self.parents.get(entry.path, set()).copy():
            self.remove_entry(child)

    def remove_entry(self, pathname):
        entry = self.entries.get(pathname)

        if entry:
            self.keys.remove(entry.key())
            del self.entries[entry.key()]

            for parent in entry.parent_directories():

                k = parent.name.encode("utf-8")

                self.parents[k].remove(entry.path)

                if len(self.parents[k]) == 0:
                    del self.parents[k]

    def release_lock(self):
        self.lockfile.rollback()

