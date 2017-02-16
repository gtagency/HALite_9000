import multiprocessing
import subprocess
import time
import random
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD

lookout_dist = 3
n_games = 20
batch_size = 30
n_simulations = 50
n_epochs = 10
"""
input format: (2n+1)^2 inputs for each of ownership, production, and strength
"""

def run_training_game(i, json_file, weights_file):
    print("starting training game %d" % i)
    name0 = "keras%d_0" % i
    name1 = "keras%d_1" % i
    retval = subprocess.run(["python3", "run_training_game.py",
                             "KerasPlayerHltWrapper.py %s %s %s %d" % (name0, json_file, weights_file, lookout_dist),
                             "KerasPlayerHltWrapper.py %s %s %s %d" % (name1, json_file, weights_file, lookout_dist),
                             "BorderExpander.py"
                            ],
                            stdout=subprocess.PIPE)
    print("finished training game %d" % i)
    lines = retval.stdout.decode('utf-8').split('\n')
    # print("returned lines: " + str(lines))

    res0, res1 = lines[4:6]
    # print(res0)
    # print(res1)
    pos0 = res0.split()[1]
    pos1 = res1.split()[1]
    winner = name0 if pos0 < pos1 else name1
    loser = name1 if pos0 < pos1 else name0

    X = []
    Y = []
    with open("train/"+winner+'.txt', 'r') as win_file:
        for line in win_file.readlines():
            x = []
            ownership, production, strength, move = line.split('|')
            for s in (ownership, production, strength):
                for c in s.split(','):
                    x.append(int(c))
            # print(x)
            X.append(x)
            y = [0.] * 5
            y[int(move)] = 1.
            # print(y)
            Y.append(y)

    with open("train/"+loser+'.txt', 'r') as lose_file:
        for line in lose_file.readlines():
            x = []
            ownership, production, strength, move = line.split('|')
            for s in (ownership, production, strength):
                for c in s.split(','):
                    x.append(int(c))
            # print(x)
            X.append(x)
            y = [0.25] * 5
            y[int(move)] = 0.
            # print(y)
            Y.append(y)

    return np.array(X), np.array(Y)


def get_game_data(x):
    time.sleep(4.0 * x)
    weights_file = "model/weights_%d.h5" % x
    json_file = "model/model_%d.json" % x
    with open(json_file, 'w') as f:
        f.write(model.to_json())
    model.save_weights(weights_file)
    return run_training_game(x, json_file, weights_file)


if __name__ == '__main__':
    input_size = pow((2 * lookout_dist) + 1, 2) * 3

    model = Sequential()
    model.add(Dense(32, input_shape=(input_size,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))

    model.add(Dense(32))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))

    # model.add(Dense(16))
    # model.add(Activation('relu'))
    # model.add(Dropout(0.2))

    model.add(Dense(5))
    model.add(Activation('softmax'))

    model.compile(loss='mean_squared_error',
                  optimizer=SGD(lr=0.01),
                  metrics=['accuracy'])

    pool = multiprocessing.Pool(processes=n_games)

    for epoch in range(n_simulations):
        XY_list = pool.map(get_game_data, range(n_games))

        X = np.vstack(test_xy[0] for test_xy in XY_list)
        Y = np.vstack(test_xy[1] for test_xy in XY_list)
        X_train, X_test = np.vsplit(X, (int(X.shape[0] * 0.9),))
        Y_train, Y_test = np.vsplit(Y, (int(Y.shape[0] * 0.9),))

        history = model.fit(X_train, Y_train,
                            batch_size=batch_size, nb_epoch=n_epochs,
                            verbose=1, validation_data=(X_test, Y_test))

        score = model.evaluate(X_test, Y_test, verbose=0)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])
