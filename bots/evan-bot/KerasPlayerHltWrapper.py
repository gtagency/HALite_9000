import sys
import pexpect
import hlt
import time
from itertools import product, chain



def assign_move(square):
    ownership = []
    production = []
    strength = []
    r_y = range(square.y - lookout_dist, square.y + lookout_dist + 1)
    r_x = range(square.x - lookout_dist, square.x + lookout_dist + 1)
    for y, x in product(r_y, r_x):
        square = game_map.contents[y % game_map.height][x % game_map.width]
        production.append(square.production)
        strength.append(square.strength)
        if square.owner == myID:
            ownership.append(1)
        elif square.owner == 0:
            ownership.append(0)
        else:
            ownership.append(-1)
    child.sendline(','.join(str(x) for x in chain(ownership, strength, production)))
    child.expect('$.*')
    with open("log.txt", 'w') as f: f.write(child.before)
    # move_code = int(str(child.after[1:]))
    return hlt.Move(square, 0)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Pass in player ID, JSON model filename, HDF5 weights filename, and lookout distance")
        exit()

    hlt_player_id = sys.argv[1]
    lookout_dist = int(sys.argv[4])
    cmds = ['python3', 'KerasPlayer.py'] + sys.argv[2:]
    child = pexpect.spawn(' '.join(cmds))

    # for i in range(10):
    #     x_str = ','.join([str(i)]*27)
    #     child.sendline(x_str)
    #     child.expect('hi')
    #     y_str = str(child.after)
    #     print(y_str)
    #
    # child.close()

    myID, game_map = hlt.get_init()
    time.sleep(1)
    hlt.send_init(hlt_player_id)

    while True:
        game_map.get_frame()
        moves = [assign_move(s) for s in game_map if s.owner == myID]
        hlt.send_frame(moves)
