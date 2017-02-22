import random

import hlt


def log(file, data):
    with open("logs/" + file, 'w') as f:
        f.write(data)

def weighted_choice(choices):
    total = sum(w for c, w in choices)
    # log("total.txt", str(total))
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        upto += w
        if upto >= r:
            return c
    # log("error.txt", str(upto))
    assert False, "Shouldn't get here"

def get_map_2D_indices(index):
    return (index // game_map.width, index % game_map.width)

def get_direction(index_current, index_target):
    y0, x0 = get_map_2D_indices(index_current)
    y1, x1 = get_map_2D_indices(index_target)
    if abs(y1-y0) >= abs(x1-x0):
        if y1 >= y0:
            movecode = hlt.SOUTH
        else:
            movecode = hlt.NORTH
    else:
        if x1 >= x0:
            movecode = hlt.EAST
        else:
            movecode = hlt.WEST
    return movecode

def get_1D(index):
    y, x = get_map_2D_indices(index)
    return game_map.contents[y][x]

def get_move(square, index):
    movecode = hlt.STILL
    if square.strength > 5 * square.production:
        target_index = weighted_choice(tuple(filter(
            lambda iw: get_1D(iw[0]).owner != myID,
            production_1D
        )))
        movecode = get_direction(index, target_index)
    return hlt.Move(square, movecode)


if __name__ == '__main__':
    myID, game_map = hlt.get_init()
    hlt.send_init("ProductionSampler")

    production_1D = []
    for row in game_map.production:
        production_1D += row
    production_1D = tuple(enumerate(production_1D))

    while True:
        game_map.get_frame()
        moves = [get_move(s, i) for i, s in enumerate(game_map) if s.owner == myID]
        hlt.send_frame(moves)

