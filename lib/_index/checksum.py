from hashlib import sha1


class Checksum:
    class EndOfFile(Exception):
        pass

    class Invalid(Exception):
        pass

    CHECKSUM_SIZE = 20

    def __init__(self, f):
        self.file = f
        self.digest = sha1()

    def read(self, size):

        data = self.file.read(size)

        if not len(data) == size:
            raise EndOfFile()

        self.digest.update(data)

        return data

    def write(self, data):
        self.file.write(data)
        self.digest.update(data)

    def write_checksum(self):
        self.file.write(self.digest.digest())

    def verify_checksum(self):

        s = self.file.read(Checksum.CHECKSUM_SIZE)

        if not s == self.digest.digest():
            raise Checksum.Invalid("Checksum does not match value stored on disk")

