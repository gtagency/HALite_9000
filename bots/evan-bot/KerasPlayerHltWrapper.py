import sys
import pexpect
import hlt
import time
from itertools import product, chain


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
        with open("log_wrapper.txt", 'a') as f:
            f.write(str(move_code) + '\n')
        return hlt.Move(square, move_code)
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
    time.sleep(0.5)
    hlt.send_init(hlt_player_id)

    # with open("log_wrapper.txt", 'w') as f:
    #     f.write("start log\n")

    while True:
        game_map.get_frame()
        moves = [assign_move(s) for s in game_map if s.owner == myID]
        # with open("log_wrapper_moves.txt", 'w') as f:
        #     f.writelines(str(m.direction == hlt.STILL) for m in moves)
        hlt.send_frame(moves)
