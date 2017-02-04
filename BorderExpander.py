import hlt
import random

def log(file, data):
    with open("logs/" + file, 'w') as f:
        f.write(data)

def move_toward(s0, s1):
    if abs(s1.y-s0.y) >= abs(s1.x-s0.x):
        if s1.y >= s0.y:
            movecode = hlt.SOUTH
        else:
            movecode = hlt.NORTH
    else:
        if s1.x >= s0.x:
            movecode = hlt.EAST
        else:
            movecode = hlt.WEST
    return hlt.Move(s0, movecode)

def can_take(s0, s1):
    return s1.owner != myID and s0.strength > s1.strength

def desirability(square):
    if square.strength == 0:
        return 255
    return square.production / square.strength

def get_all_manhattan(square, dist):
    out = set()
    for n in range(-dist, dist+1):
        x = (square.x + n) % game_map.width
        y1 = (square.y + dist - abs(n)) % game_map.height
        y2 = (square.y - dist + abs(n)) % game_map.height
        out.add(game_map.contents[y1][x])
        out.add(game_map.contents[y2][x])
        log("manhattan.txt", ", ".join(str((s.y, s.x)) for s in out))
    return tuple(out)

def expansion_target(square):
    dist = 0
    found = []
    while not found:
        dist += 1
        found = [
            sq for sq in get_all_manhattan(square, dist) if sq.owner != myID
        ]
    return max(found, key=desirability), dist

def get_move(square):
    if square.strength < 5 * square.production:
        return hlt.Move(square, hlt.STILL)

    target, dist = expansion_target(square)
    if dist > 1 or can_take(square, target):
        return move_toward(square, target)
    else:
        return hlt.Move(square, hlt.STILL)


myID, game_map = hlt.get_init()
hlt.send_init("BorderExpander")

while True:
    game_map.get_frame()
    moves = [get_move(s) for s in game_map if s.owner == myID]
    hlt.send_frame(moves)

