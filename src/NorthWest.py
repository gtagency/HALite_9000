import BorderExpander as be
import hlt


def desirability(square):
    if square.production == 0:
        return 0
    if square.strength == 0:
        return 255
    return square.production / square.strength

def move_push(square, direction):
    not_mine = tuple(sq for sq in be.get_neighbors(game_map, square) if sq.owner != myID)
    if len(not_mine) == 0:
        return hlt.Move(square, direction)
    target = max(not_mine, key=desirability)
    return be.move_toward(game_map, square, target)

def get_move(square):
    if square.strength < 3 * square.production + 1:
        return hlt.Move(square, hlt.STILL)
    if not push_north_successful:
        return move_push(square, hlt.NORTH)
    else:
        return move_push(square, hlt.WEST)

def my_squares():
    return (s for s in game_map if s.owner == myID)


if __name__ == '__main__':
    myID, game_map = hlt.get_init()
    hlt.send_init("NorthWest")

    while True:
        game_map.get_frame()

        # total_production = sum(game_map.production[s.y][s.x] for s in my_squares())
        push_north_successful = True
        last_y = -1
        for sqr in my_squares():
            if sqr.y == last_y + 1:
                last_y += 1
            elif sqr.y > last_y + 1:
                push_north_successful = False
                break

        moves = [get_move(s) for s in my_squares()]
        hlt.send_frame(moves)
