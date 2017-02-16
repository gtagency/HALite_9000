import sys
import pexpect
import hlt
import time
from itertools import product, chain


class LabeledContext:
    def __init__(self):
        self.ownership = []
        self.production = []
        self.strength = []
        self.move = 0

    def as_string(self):
        return (','.join(str(x) for x in self.ownership) + '|'
              + ','.join(str(x) for x in self.production) + '|'
              + ','.join(str(x) for x in self.strength) + '|'
              + str(self.move))

def assign_move(square):
    ownership = []
    production = []
    strength = []
    r_y = tuple(range(square.y - lookout_dist, square.y + lookout_dist + 1))
    r_x = tuple(range(square.x - lookout_dist, square.x + lookout_dist + 1))
    for y, x in product(r_y, r_x):
        visible_square = game_map.contents[y % game_map.height][x % game_map.width]
        production.append(visible_square.production)
        strength.append(visible_square.strength)
        if visible_square.owner == myID:
            ownership.append(1)
        elif visible_square.owner == 0:
            ownership.append(0)
        else:
            ownership.append(-1)

    try:
        child.sendline(','.join(str(x) for x in chain(ownership, strength, production)))
        child.expect('result: .*', timeout=1.1)
        move_code = int(str(child.after)[10])
        # with open("log_wrapper.txt", 'a') as f:
        #     f.write(str(move_code) + '\n')

        lc = LabeledContext()
        lc.ownership = ownership
        lc.strength = strength
        lc.production = production
        lc.move = move_code

        return hlt.Move(square, move_code), lc
    except:
        print(child.before)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Pass in player ID, JSON model filename, HDF5 weights filename, and lookout distance")
        exit()

    hlt_player_id = sys.argv[1]
    lookout_dist = int(sys.argv[4])
    cmds = ['python3', 'KerasPlayer.py'] + sys.argv[2:]
    child = pexpect.spawn(' '.join(cmds))

    myID, game_map = hlt.get_init()
    time.sleep(1.0)
    hlt.send_init(hlt_player_id)

    train_data_file = "train/%s.txt" % hlt_player_id
    open(train_data_file, 'w').close()

    while True:
        game_map.get_frame()
        moves = []
        data = []
        for s in game_map:
            if s.owner == myID:
                move, labeled_context = assign_move(s)
                moves.append(move)
                data.append(labeled_context)
        hlt.send_frame(moves)

        with open(train_data_file, 'a') as f:
            f.writelines(d.as_string()+'\n' for d in data)
