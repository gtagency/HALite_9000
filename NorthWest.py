import hlt
import random

def log(file, data):
    with open("logs/" + file, 'w') as f:
        f.write(data)

myID, game_map = hlt.get_init()
hlt.send_init("NorthWest")

log('production_map.txt', str(game_map.production).replace('), (', '\n'))

def get_move(square):
    movecode = hlt.STILL
    if square.strength > 7 * square.production:
        movecode = random.choice((hlt.NORTH, hlt.WEST))

    return hlt.Move(square, movecode)

game_map.get_frame()
#log("turn0.txt", str(game_map.contents))
moves = [get_move(s) for s in game_map if s.owner == myID]
hlt.send_frame(moves)

while True:
    game_map.get_frame()
    moves = [get_move(s) for s in game_map if s.owner == myID]
    hlt.send_frame(moves)
