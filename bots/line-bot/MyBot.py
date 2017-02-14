import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random


myID, game_map = hlt.get_init()
hlt.send_init("MarcBot")
i = 0
while True:
    game_map.get_frame()
    moves = []
    for mine in (p for p in game_map if p.owner == myID):
        if i % 20 == 0:
            moves.append(Move(mine, NORTH))
    i += 1
    #moves = [Move(square, random.choice((NORTH, EAST, SOUTH, WEST, STILL))) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
