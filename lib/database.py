import zlib
from hashlib import sha1
from os import path, rename
import os
from random import shuffle
import struct

from lib.db.author import Author
from lib.db.blob import Blob
from lib.db.commit import Commit
from lib.db.tree import Tree


class Database:
    Author = Author
    Blob = Blob
    Commit = Commit
    Tree = Tree

    @classmethod
    def temp_chars(cls):
        return list(
            map(
                chr,
                list(range(ord("a"), ord("z") + 1)) + list(range(ord("A"), ord("B"))),
            )
        ) + list(range(0, 10))

    def __init__(self, pathname):
        self.pathname = pathname

    def store(self, obj):

        string = obj.to_s()

        content = struct.pack(
            "%ds %dsx %ds" % (len(obj.type()) + 1, len(str(len(string))), len(string)),
            (obj.type() + " ").encode("utf-8"),
            str(len(string)).encode("utf-8"),
            string,
        )

        obj.oid = sha1(content).hexdigest()

        self.write_object(obj.oid, content)

    def write_object(self, oid, content):

        object_path = os.path.join(self.pathname, oid[0:2], oid[2:40])

        if os.path.isfile(object_path):
            return

        dirname = os.path.dirname(object_path)
        temp_path = path.join(dirname, self.generate_temp_name())

        try:
            f = open(temp_path, "wb")
        except IOError:
            os.makedirs(dirname)
            f = open(temp_path, "wb")

        data = zlib.compress(content, 1)

        f.write(data)

        f.close()

        rename(temp_path, object_path)

    def generate_temp_name(self):
        temp_chars = self.temp_chars()
        shuffle(temp_chars)
        f = "".join(map(str, temp_chars[0:7]))
        return "tmp_objc_%s" % (f)
