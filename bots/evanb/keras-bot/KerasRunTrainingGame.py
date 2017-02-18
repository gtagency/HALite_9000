import os
import random
import sys

def abs_from_file(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

def abs_from_parent(path):
    return abs_from_file(os.path.join(os.pardir, path))

size1 = int(random.uniform(25, 60))
size2 = random.choice((size1, int(size1 * random.uniform(0.8, 1.2))))

if len(sys.argv) < 2:
    print("Specify at least one python file")
    exit()

program_names = sys.argv[1:]

cmdstr = ' '.join([
    abs_from_parent("halite"),
    '-q',
    '-t',
    '-d', '"%d %d"' % (size1, size2),
    ' '.join(['"python3 %s"' % abs_from_parent(pn) for pn in program_names])
])

# print(cmdstr)
os.chdir('logs')
os.system(cmdstr)
