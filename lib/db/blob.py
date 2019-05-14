class Blob:
    def __init__(self, data):
        self.data = data

    def type(self):
        return "blob"

    def to_s(self):
        return self.data.encode("utf-8")
