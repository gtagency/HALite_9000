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

def manhattan_dist(s0, s1):
    s1 = closest_dist_version(s0, s1)
    return abs(s1.y - s0.y) + abs(s1.x - s0.x)

def closest_dist_version(s0, s1):
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

def get_neighbors(square):
    out = []
    for dx, dy in ((1,0), (0,1), (-1,0), (0,-1)):
        y = (square.y + dy) % game_map.height
        x = (square.x + dx) % game_map.width
        s = game_map.contents[y][x]
        if s.owner != myID:
            out.append(s)
    return out

def get_new_border():
    out = []
    for square in filter(lambda s: s.owner == myID, game_map):
        for s in get_neighbors(square):
            out.append(s)
    return out

def desirability(square, target):
    dist_factor = pow(manhattan_dist(square, target), 0.5)
    production_factor = target.production / max(1, target.strength)
    return production_factor / dist_factor

def get_move(square):
    if square.strength < 5 * square.production + 1:
        return hlt.Move(square, hlt.STILL)

    def desirability_key(target):
        return desirability(square, target)

    neighbors = get_neighbors(square)
    if len(neighbors) > 0:
        target = max(neighbors, key=desirability_key)
        if can_take(square, target):
            return move_toward(square, target)
        else:
            return hlt.Move(square, hlt.STILL)
    else:
        target = max(border_list, key=desirability_key)
        return move_toward(square, target)



if __name__ == '__main__':
    myID, game_map = hlt.get_init()
    hlt.send_init("BorderExpander")

    while True:
        game_map.get_frame()
        border_list = get_new_border()
        moves = [get_move(s) for s in game_map if s.owner == myID]
        hlt.send_frame(moves)

