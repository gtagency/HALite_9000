import sys
import numpy as np
import hlt
import itertools

LOOKOUT_DIST = 2
INPUT_SIZE = (((2 * LOOKOUT_DIST) + 1) ** 2) * 3
HIDDEN_LAYER_SIZES = (40,20)

# float encoding parameters
FLOAT_BITS_EXP = 3
FLOAT_BITS_SIGNIFICAND = 20
FLOAT_BITS = 1 + FLOAT_BITS_EXP + FLOAT_BITS_SIGNIFICAND

N_WEIGHTS = INPUT_SIZE*HIDDEN_LAYER_SIZES[0] \
        + sum(HIDDEN_LAYER_SIZES[i-1]*HIDDEN_LAYER_SIZES[i]
              for i in range(1, len(HIDDEN_LAYER_SIZES))) \
        + 5*HIDDEN_LAYER_SIZES[-1]
N_BIASES = sum(HIDDEN_LAYER_SIZES) + 5
N_GENOME_BITS = (N_WEIGHTS + N_BIASES) * FLOAT_BITS


def binary_to_custom_float(bitvec):
    sign = -1.0 if bitvec[0] == '1' else 1.0
    i = 1 + FLOAT_BITS_EXP
    exponent = int(bitvec[1:i], 2) - (2 ** (FLOAT_BITS_EXP-1))
    significand = sum(1/2**i for i, x in enumerate(bitvec[i:], 1) if x == '1')
    return sign * 2**exponent * (1 + significand)


def get_context(square):
    ownership = []
    production = []
    strength = []
    r_y = tuple(range(square.y - LOOKOUT_DIST, square.y + LOOKOUT_DIST + 1))
    r_x = tuple(range(square.x - LOOKOUT_DIST, square.x + LOOKOUT_DIST + 1))
    for y, x in itertools.product(r_y, r_x):
        visible_square = game_map.contents[y % game_map.height][x % game_map.width]
        production.append(visible_square.production)
        strength.append(visible_square.strength)
        if visible_square.owner == myID:
            ownership.append(1)
        elif visible_square.owner == 0:
            ownership.append(0)
        else:
            ownership.append(-1)
    return list(itertools.chain(ownership, production, strength))


def sigmoid(X):
    return 1 / (1 + np.exp(-X))


def softmax(y):
    y2 = np.exp(y)
    y3 = y2 / sum(y2.flat)   # for some reason, normalizing twice gets
    return y3 / sum(y3.flat) # rid of all rounding errors


def feed_forward(X, w_list, b_list):
    X2 = np.array(X)
    for l in range(len(HIDDEN_LAYER_SIZES)):
        X2 = sigmoid(np.matmul(X2, w_list[l]) + b_list[l])

    y = []
    for i in range(X2.shape[0]):
        raw_out = np.matmul(X2[i], w_list[-1]) + b_list[-1]
        y.append(softmax(raw_out))
    return y


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Must pass in player name and genome")
        exit()
    if len(sys.argv[2]) != N_GENOME_BITS:
        print("Genome must be %d bits" % N_GENOME_BITS)
        exit()

    hlt_player_id = sys.argv[1]
    genome = sys.argv[2]

    i = 0
    w_layers = []
    prev_layer_size = INPUT_SIZE
    for layer_size in itertools.chain(HIDDEN_LAYER_SIZES, [5]):
        w = []
        for m in range(prev_layer_size):
            r = []
            for n in range(layer_size):
                # print("layer %d, prev_index %d, current_index %d, i = %d / %d"
                #       % (len(w_layers), m, n, i, N_GENOME_BITS))
                r.append(binary_to_custom_float(genome[i:i+FLOAT_BITS]))
                i += FLOAT_BITS
            w.append(r)
        W = np.array(w)
        # if (len(W.flat) != 5):
        #     print("Shape of layer: " + str(W.shape))
        w_layers.append(W)
        prev_layer_size = layer_size

    b_layers = []
    for layer_size in itertools.chain(HIDDEN_LAYER_SIZES, [5]):
        b = []
        for n in range(layer_size):
            b.append(binary_to_custom_float(genome[i:i+FLOAT_BITS]))
            i += FLOAT_BITS
        B = np.array(b).reshape((1, layer_size))
        b_layers.append(B)


    #play halite
    myID, game_map = hlt.get_init()
    hlt.send_init(hlt_player_id)

    while True:
        game_map.get_frame()

        x = []
        my_squares = []
        for s in game_map:
            if s.owner == myID:
                my_squares.append(s)
                x.append(get_context(s))
        X = np.array(x)
        move_probabilities = feed_forward(X, w_layers, b_layers)

        moves = []
        for square, prob_vec in zip(my_squares, move_probabilities):
            flat = tuple(prob_vec.flat)
            # if len(flat) != 5:
            #     print("caught len(flat) == " + str(len(flat)))
            #     print(prob_vec.shape)
            move_code = np.random.choice(tuple(range(5)), p=flat)
            moves.append(hlt.Move(square, move_code))

        hlt.send_frame(moves)

