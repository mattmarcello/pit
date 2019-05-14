import zlib
from sys import argv

script, filename = argv

f = open(filename, 'r')

data = f.read()

f.close()

print(zlib.decompress(data))


