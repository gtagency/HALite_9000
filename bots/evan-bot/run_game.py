import os
import random
import sys

size1 = int(random.uniform(25, 60))
size2 = random.choice((size1, int(size1 * random.uniform(0.8, 1.2))))

if len(sys.argv) < 2:
    print("Specify at least one python file")
    exit()

program_names = sys.argv[1:]

cmdstr = ' '.join([
    os.path.join(os.curdir, "halite"),
    '-d',
    '"%d %d"' % (size1, size2),
    ' '.join(['"python3 %s"' % pn for pn in program_names])
])

# print(cmdstr)
os.system(cmdstr)
