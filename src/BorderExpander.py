import hlt


def log(file, data):
    with open("logs/" + file, 'w') as f:
        f.write(data)


def move_toward(game_map, s0, s1):
    # shift position of s1 to wrap around board edges
    s1 = closest_dist_version(game_map, s0, s1)

    if abs(s1.y-s0.y) >= abs(s1.x-s0.x):
        if s1.y >= s0.y:
            return hlt.Move(s0, hlt.SOUTH)
        else:
            return hlt.Move(s0, hlt.NORTH)
    else:
        if s1.x >= s0.x:
            return hlt.Move(s0, hlt.EAST)
        else:
            return hlt.Move(s0, hlt.WEST)

def can_take(s0, s1):
    return s1.owner != myID and s0.strength > s1.strength

def manhattan_dist(s0, s1):
    return abs(s1.y - s0.y) + abs(s1.x - s0.x)

def closest_dist_version(game_map, s0, s1):
    out_y = s1.y
    out_x = s1.x
    if s1.y > s0.y + game_map.height/2:
        out_y -= game_map.height
    elif s1.y < s0.y - game_map.height/2:
        out_y += game_map.height
    if s1.x > s0.x + game_map.width/2:
        out_x -= game_map.width
    elif s1.x < s0.x - game_map.width/2:
        out_x += game_map.width
    return hlt.Square(out_x, out_y, None, None, None)

def get_neighbors(game_map, square):
    for dx, dy in ((1,0), (0,1), (-1,0), (0,-1)):
        y = (square.y + dy) % game_map.height
        x = (square.x + dx) % game_map.width
        yield game_map.contents[y][x]

def get_new_border():
    out = set()
    for square in filter(lambda s: s.owner == myID, game_map):
        for possible_border in filter(lambda s: s.owner != myID, get_neighbors(game_map, square)):
            out.add(possible_border)
    return tuple(out)

def expansion_target(square):
    return min(border_list, key=lambda sq: manhattan_dist(square, closest_dist_version(game_map, square, sq)))

def get_move(square):
    if square.strength < 3 * square.production + 1:
        return hlt.Move(square, hlt.STILL)

    target = expansion_target(square)
    if target not in get_neighbors(game_map, square) or can_take(square, target):
        return move_toward(game_map, square, target)
    else:
        return hlt.Move(square, hlt.STILL)

if __name__ == '__main__':
    myID, game_map = hlt.get_init()
    hlt.send_init("BorderExpander")

    while True:
        game_map.get_frame()
        border_list = get_new_border()
        moves = [get_move(s) for s in game_map if s.owner == myID]
        hlt.send_frame(moves)

