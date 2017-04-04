import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move

myID, game_map = hlt.get_init()
hlt.send_init("prabhav-bot")


def heuristic(square):
    if square.owner == 0 and square.strength > 0:
        return square.production / square.strength
    else:
        return sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))


"""def best_border(square):
    best_direction = NORTH
    temp_score = -1
    for d in (NORTH, EAST, SOUTH, WEST):
        current = square
        distance = 0
        while current.owner == myID and current != game_map.get_target(square, (d + 2) % 4):
            distance += 1
            current = game_map.get_target(current, d)
        neighbor_in_direction = game_map.get_target(current, (d + 2) % 4)
        temp_tuple = border_attack(neighbor_in_direction)
        my_score = temp_tuple[3]/distance
        if my_score > temp_score:
            temp_score = my_score
            best_direction = d
    return best_direction"""


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


def border_attack(square):
    border = False
    best_neighbor_direction = NORTH
    best_neighbor_score = -1
    for direction, neighbor in enumerate(game_map.neighbors(square)):
        if neighbor.owner != myID:
            border = True
            tmp_neighbor_score = heuristic(neighbor)
            if tmp_neighbor_score > best_neighbor_score:
                best_neighbor_score = tmp_neighbor_score
                best_neighbor_direction = direction
    if border and game_map.get_target(square, best_neighbor_direction).strength < square.strength:
        return True, Move(square, best_neighbor_direction), best_neighbor_direction, best_neighbor_score
    else:
        return False, border, best_neighbor_direction, best_neighbor_score


def assign_move(square):
    temp_tuple = border_attack(square)
    if temp_tuple[0]:
        return [temp_tuple[1]]
    if temp_tuple[1]:
        my_temp_moves = []
        temp_neighbor = square
        temp_direction = STILL
        temp_strength = -1
        for direction, neighbor in enumerate(game_map.neighbors(square)):
            if neighbor.owner == myID:
                temp_tuple_neighbor = border_attack(neighbor)
                if temp_tuple_neighbor[0]:
                    my_temp_moves.append(temp_tuple_neighbor[1])
                elif temp_tuple_neighbor[1]:
                    attack_square_enemy_together = neighbor.strength + square.strength > game_map.get_target(square, temp_tuple[2]).strength
                    attack_neighbor_enemy_together = neighbor.strength + square.strength > game_map.get_target(neighbor, temp_tuple_neighbor[2]).strength
                    if attack_square_enemy_together and (
                                not attack_neighbor_enemy_together or temp_tuple[3] > temp_tuple_neighbor[3]):
                        if temp_strength == -1 or neighbor.strength < temp_strength:
                            temp_neighbor = neighbor
                            temp_strength = neighbor.strength
                            temp_direction = direction
        if temp_strength != -1:
            my_temp_moves.extend([Move(square, STILL), Move(temp_neighbor, (temp_direction + 2) % 4)])
            return my_temp_moves
    if square.strength < 5 * square.production:
        return [Move(square, STILL)]
    if not temp_tuple[1]:
        return [Move(square, nearest_border(square))]
    else:
        return [Move(square, STILL)]

while True:
    game_map.get_frame()
    moves = []
    squares_moves = {}
    for tile in game_map:
        if tile.owner == myID:
            my_moves = assign_move(tile)
            if len(my_moves) > 1:
                for a in my_moves:
                    for move in moves:
                        if a.square == move.square:
                            squares_moves[game_map.get_target(move.square, move.direction)].remove(move)
                            moves.remove(move)
                for my_move in my_moves:
                    moves.append(my_move)
                    squares_moves_key = game_map.get_target(my_move.square, my_move.direction)
                    if squares_moves_key not in squares_moves:
                        squares_moves[squares_moves_key] = [my_move]
                    else:
                        squares_moves[squares_moves_key].append(my_move)
            else:
                if not any(my_moves[0].square == move.square for move in moves):
                    moves.extend(my_moves)
                    squares_moves_key = game_map.get_target(my_moves[0].square, my_moves[0].direction)
                    if squares_moves_key not in squares_moves:
                        squares_moves[squares_moves_key] = [my_moves[0]]
                    else:
                        squares_moves[squares_moves_key].append(my_moves[0])

    for key in squares_moves:
        strength_list = sorted((x for x in squares_moves[key] if x.direction != STILL), key=lambda t: t.square.strength)
        if sum(x.square.strength for x in strength_list) > 255:
            if key.owner != myID:
                for j in range(len(strength_list) - 1):
                    moves.remove(strength_list[j])
                    moves.append(Move(strength_list[j].square, STILL))
            else:
                for j in range(1, len(strength_list)):
                    moves.remove(strength_list[j])
                    moves.append(Move(strength_list[j].square, STILL))
    hlt.send_frame(moves)
