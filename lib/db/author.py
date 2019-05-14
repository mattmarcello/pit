class Author:
    def __init__(self, name, email, time):
        self.name = name
        self.email = email
        self.time = time

    def to_s(self):
        return "%s <%s> %s" % (self.name, self.email, self.time)
