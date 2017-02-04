import hlt

def log(file, data):
    with open("logs/" + file, 'w') as f:
        f.write(data)


def move_toward(s0, s1):
    # shift position of s1 to wrap around board edges
    s1 = closest_dist_version(s0, s1)

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

def desirability(square):
    if square.strength == 0:
        return 255
    return square.production / square.strength

def manhattan_dist(s0, s1):
    return abs(s1.y - s0.y) + abs(s1.x - s0.x)

def closest_dist_version(s0, s1):
    offset_x = (0, game_map.width, -game_map.width)
    offset_y = (0, game_map.height, -game_map.height)
    versions = []
    for dx in offset_x:
        for dy in offset_y:
            versions.append(hlt.Square(s1.x+dx, s1.y+dy, None, None, None))
    return min(versions, key=lambda x: manhattan_dist(s0, x))

def get_neighbors(square):
    dirs = ((1,0), (0,1), (-1,0), (0,-1))
    for dx, dy in dirs:
        y = (square.y + dy) % game_map.width
        x = (square.x + dx) % game_map.height
        yield game_map.contents[y][x]

def get_new_border():
    out = set()
    for square in filter(lambda s: s.owner == myID, game_map):
        for possible_border in filter(lambda s: s.owner != myID, get_neighbors(square)):
            out.add(possible_border)
    return tuple(out)

def expansion_target(square):
    return min(border_list, key=lambda sq: manhattan_dist(square, closest_dist_version(square, sq)))

def get_move(square):
    if square.strength < 3 * square.production + 1:
        return hlt.Move(square, hlt.STILL)

    target = expansion_target(square)
    if target not in get_neighbors(square) or can_take(square, target):
        return move_toward(square, target)
    else:
        return hlt.Move(square, hlt.STILL)


myID, game_map = hlt.get_init()
hlt.send_init("BorderExpander")

while True:
    game_map.get_frame()
    border_list = get_new_border()
    moves = [get_move(s) for s in game_map if s.owner == myID]
    hlt.send_frame(moves)

