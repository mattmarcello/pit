from time import sleep
from pathlib import Path
import struct
import os

# from lib.index import Index

ENTRY_FORMAT = lambda l: "> 10I 20s h %dsx" % l
ENTRY_BLOCK = 8

REGULAR_MODE = 0o100644
EXECUTABLE_MODE = 0o100755
MAX_PATH_SIZE = 0xFFF

entry_fields = (
    "ctime",
    "ctime_nsec",
    "mtime",
    "mtime_nsec",
    "dev",
    "ino",
    "mode",
    "uid",
    "gid",
    "size",
    "oid",
    "flags",
    "path",
)


class Entry:
    def __init__(
        self,
        ctime,
        ctime_nsec,
        mtime,
        mtime_nsec,
        dev,
        ino,
        mode,
        uid,
        gid,
        size,
        oid,
        flags,
        path,
    ):
        self.ctime = ctime
        self.ctime_nsec = ctime_nsec
        self.mtime = mtime
        self.mtime_nsec = mtime_nsec
        self.dev = dev
        self.ino = ino
        self.mode = mode
        self.uid = uid
        self.gid = gid
        self.size = size
        self.oid = oid
        self.flags = flags
        self.path = path

    @classmethod
    def create(cls, pathname, oid, stat):
        def get_decimal(n):
            return int(str(n % 1)[2:11])

        def get_relevant_bytes(n):
            big_endian_long = struct.pack("> Q", n)
            relevant_bytes = big_endian_long[4:]
            return struct.unpack("> I", relevant_bytes)[0]

        path = pathname.as_posix().encode("utf-8")
        mode = (
            EXECUTABLE_MODE if os.access(pathname.as_posix(), os.X_OK) else REGULAR_MODE
        )
        flags = min([len(path), MAX_PATH_SIZE])

        """TODO: rounding is a bit of a hack here"""

        return cls(
            get_relevant_bytes(int(stat.st_ctime)),
            get_relevant_bytes(get_decimal(round(stat.st_ctime % 1, 9))),
            int(stat.st_mtime),
            get_relevant_bytes(get_decimal(round(stat.st_mtime % 1, 9))),
            get_relevant_bytes(stat.st_dev),
            get_relevant_bytes(stat.st_ino),
            get_relevant_bytes(mode),
            get_relevant_bytes(stat.st_uid),
            get_relevant_bytes(stat.st_gid),
            get_relevant_bytes(stat.st_size),
            bytes.fromhex(oid),
            flags,
            path,
        )

    @classmethod
    def parse(cls, data):
        unpacked = None
        i = 0
        while not unpacked:
            try:
                fmt = ENTRY_FORMAT(i)
                unpacked = struct.unpack(fmt, data)
            except:
                """TODO: string is padded to multiple of 8 dis bad"""
                i += 1

        unpacked_with_stripped_name = unpacked[:-1] + (unpacked[-1][: unpacked[-2]],)

        return cls(*unpacked_with_stripped_name)

    def key(self):
        return self.path

    def to_s(self):

        string = struct.pack(
            ENTRY_FORMAT(len(self.path)),
            self.ctime,
            self.ctime_nsec,
            self.mtime,
            self.mtime_nsec,
            self.dev,
            self.ino,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.oid,
            self.flags,
            self.path,
        )

        """ pad with null bytes until string is mult of 8"""
        while len(string) % ENTRY_BLOCK != 0:
            string += b"\0"

        return string

    def parent_directories(self):
        return list(reversed(list(Path(self.path.decode("utf-8")).parents.__iter__())))[
            1:
        ]

    def basename(self):
        b = Path(self.path.decode("utf-8")).name
        return Path(b)
