class Commit:
    def __init__(self, parent, tree, author, message):
        self.parent = parent
        self.tree = tree
        self.author = author
        self.message = message

    def type(self):
        return "commit"

    def to_s(self):
        return "\n".join(
            filter(
                None.__ne__,
                [
                    "tree %s" % (self.tree),
                    "parent %s" % (self.parent) if self.parent is not None else None,
                    "author %s" % (self.author.to_s()),
                    "committer %s" % (self.author.to_s()),
                    "",
                    self.message,
                ],
            )
        ).encode("utf-8")
