# Heuristics to consider -
# * 5?
# heuristic returns 0 if...
# heuristic only cheks if sqaure.owner is 0, not if neighbors are 0 or enemies

import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move

myID, game_map = hlt.get_init()
hlt.send_init("TutorialBot")


# The best neighbor to occupy would be the one with highest production and lowest strength, therefore we take ratio of
# production/strength. However this is applicable only if the owner is none/0 and strength != 0. If owner is enemy, we
# find how string the enemy is (that is strength of all it's neighbors), it makes sense to attack the strongest enemy
# even though we may not completely destroy it but we will weaken the strongest, and not weaken the weakest. However we
# return 0 if there are no enemies around us and strength is 0
def heuristic(square):
    if square.owner == 0 and square.strength > 0:
        return square.production / square.strength
    else:
        # return total potential damage caused by overkill when attacking this square
        return sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))


# Move piece in direction of nearest border
def nearest_border(square):
    direction = NORTH
    max_distance = min(game_map.width, game_map.height) / 2
    for d in (NORTH, EAST, SOUTH, WEST):
        distance = 0
        current = square
        while current.owner == myID and distance < max_distance:
            distance += 1
            current = game_map.get_target(current, d)
        if distance < max_distance:
            direction = d
            max_distance = distance
    return direction


def assign_move(square):
    border = False
    best_neighbor_direction = NORTH
    best_neighbor_score = -1
    # enumerate returns tuples of count and value, count here is 'direction'
    for direction, neighbor in enumerate(game_map.neighbors(square)):
        if neighbor.owner != myID:
            # This means that the square is at the border of the territory controlled by our bot as there is at least
            # one neighbor that we don't control
            border = True
            tmp_neighbor_score = heuristic(neighbor)
            if tmp_neighbor_score > best_neighbor_score:
                best_neighbor_score = tmp_neighbor_score
                best_neighbor_direction = direction
    if border and game_map.get_target(square, best_neighbor_direction).strength < square.strength:
        return Move(square, best_neighbor_direction)
    # To ensure we fully utilize the strength we can obtain from a position, pieces only move once their strength equals
    # the tile's production times some arbitrary value = 5 here. This also ensures that pieces with 0 strength don't
    # move.
    if square.strength < 5 * square.production:
        return Move(square, STILL)
    # Move randomly in a specific area if not at the border
    if not border:
        return Move(square, nearest_border(square))
    # A square which is at the border, can't defeat it's neighbor, but has strength > 5 *
    return Move(square, STILL)


while True:

    game_map.get_frame()
    moves = [assign_move(square) for square in game_map if square.owner == myID]
    hlt.send_frame(moves)
