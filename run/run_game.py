import os
import random

size1 = int(random.uniform(25, 60))
size2 = random.choice((size1, int(size1 * random.uniform(0.8, 1.2))))

path_to_files = os.path.join(os.curdir, '..', 'src')
program_names = [fn for fn in os.listdir(path_to_files)
                 if fn[-3:] == '.py' and fn != 'hlt.py']

cmdstr = ' '.join([
    os.path.join(os.curdir, "halite"),
    '-d',
    '"%d %d"' % (size1, size2),
    ' '.join(['"python3 %s"' % os.path.join(path_to_files, pn) for pn in program_names])
])

print(cmdstr)
os.system(cmdstr)
