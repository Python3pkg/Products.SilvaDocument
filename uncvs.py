import os

def remove(a, b, c):
    if b.endswith('CVS'):
        os.system('rm -rf %s' % b)

os.path.walk('.', remove, None)
