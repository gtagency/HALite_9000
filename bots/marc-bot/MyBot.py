import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random
from util import PQueue



me, game_map = hlt.get_init()
hlt.send_init("MarcBot")
i = 0
direct = {(0, -1) : NORTH, (1, 0) : EAST,
        (0, 1) : SOUTH, (-1, 0) : WEST,
        (0, 0) : STILL}

directions = [NORTH, EAST, SOUTH, WEST]


def get_path(path, start, end, game_map):
    actions = []
    while end != start:
        d = hlt.opposite_cardinal(path[end])
        actions.append(path[end])
        end = game_map.get_target(end, d)
    return actions[::-1]


def search(game_map, start, end):
    queue = PQueue()
    queue.add((0, start, None, 0))
    visited = set()
    path = {}
    path[start] = None
    def heuristic(state):
        return game_map.get_distance(state, end)
    while queue.len() > 0:
        estimated, current, action, true = queue.pop()

        if current not in visited:
            path[current] = action
            visited.add(current)
            if current == end:
                return true, path
            n = [(game_map.get_target(current, d), d) for d in directions]
            
            # ns = [(dist + grid[r][c], (r, c), d) for  in n]
            for state, action in n:
                if state not in visited:
                    queue.add((true + state.strength + heuristic(state), state,
                            action, true + state.strength))
    
def kernel(current, game_map, function = lambda x : x.strength):
    accumulator = 0
    for d in directions:
        s = game_map.get_target(current, d)
        accumulator += function(s) 
    return accumulator

    
while True:
    game_map.get_frame()
    moves = []
    best = max((sq for sq in game_map if sq.owner != me), key = lambda x : x.production)
    for sq in game_map:
        if sq.strength < 150:
            d = random.choice(directions)
            dest = game_map.get_target(sq, d) 
            if dest not in mine and dest.strength < sq.strength:
                moves.append(Move(sq, d))
            # if dest in mine and dest.strength > 0:
                # moves.append(Move(sq, d))
                # mine.remove(dest)
            # elif dest.strength < sq.strength:
                # moves.append(Move(sq, d))
        else:
            pass
             # dist, path = search(game_map, sq, best)
             # if len(path) > 0:
                # d = get_path(path, sq, best, game_map)[0]
                # moves.append(Move(sq, d))  

    hlt.send_frame(moves)
