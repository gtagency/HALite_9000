import hlt


def log(file, data):
    with open("logs/" + file, 'w') as f:
        f.write(data)

def my_squares():
    return (s for s in game_map if s.owner == myID)

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

def next_square(game_map, move):
    if move.direction == hlt.STILL:
        x, y = move.square.x, move.square.y
    elif move.direction == hlt.NORTH:
        x, y = move.square.x, (move.square.y - 1) % game_map.height
    elif move.direction == hlt.SOUTH:
        x, y = move.square.x, (move.square.y + 1) % game_map.height
    elif move.direction == hlt.WEST:
        x, y = (move.square.x - 1) % game_map.width, move.square.y
    else: #EAST
        x, y = (move.square.x + 1) % game_map.width, move.square.y
    return game_map.contents[y][x]

def avoid_collides(moves):
    # squares = tuple(m.square for m in moves)
    targets = list(next_square(game_map, m) for m in moves)
    resolved_targets = set()
    for i in range(len(moves)):
        if (targets.count(targets[i]) > 1 and targets[i] not in resolved_targets
                and targets[i] in my_squares()):
            involved_moves = list(moves[j] for j in range(len(moves)) if targets[i] == targets[j])
            # involved_targets = tuple(targets[j] for j in range(len(moves)) if targets[i] == targets[j])
            for index in range(len(involved_moves)):
                if sum(m.square.strength for m in involved_moves) <= 255:
                    break
                original_index = moves.index(involved_moves[index])
                if involved_moves[index].direction != hlt.STILL:
                    moves[original_index] = hlt.Move(
                            involved_moves[index].square, hlt.STILL
                    )
                resolved_targets.add(targets[original_index])


def get_move(square):
    if square.strength <= 5 * square.production:
        return hlt.Move(square, hlt.STILL)

    target = expansion_target(square)
    if target not in get_neighbors(game_map, square) or can_take(square, target):
        return move_toward(game_map, square, target)
    else:
        return hlt.Move(square, hlt.STILL)

if __name__ == '__main__':
    myID, game_map = hlt.get_init()
    hlt.send_init("BorderExpander2")

    while True:
        game_map.get_frame()
        border_list = get_new_border()
        moves = [get_move(s) for s in game_map if s.owner == myID]
        move = avoid_collides(moves)
        hlt.send_frame(moves)

