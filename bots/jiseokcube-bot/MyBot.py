import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random, math

myID, game_map = hlt.get_init()
hlt.send_init("jiseokcube2")

def assign_move(square):
    enemyNeighbor = False
    for direction, neighbor in enumerate(game_map.neighbors(square)):
        if neighbor.owner != myID and neighbor.strength < square.strength:
            enemyNeighbor = True
            return Move(square, direction)
    
    myNeighbors = []
    for direction, neighbor in enumerate(game_map.neighbors(square)):
        if neighbor.owner == myID:
            myNeighbors.append(direction)
    
    if len(myNeighbors) == 0:
        return Move(square, random.choice((NORTH, EAST, SOUTH, WEST)))
    elif enemyNeighbor or square.strength < 5 * square.production or len(myNeighbors) == 1:
        return Move(square, STILL)
    elif not enemyNeighbor and (myNeighbors[0] + myNeighbors[1]) % 2 == 1:
        return Move(square, random.choice(myNeighbors[:2]))
    return Move(square, STILL)

while True:
    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
