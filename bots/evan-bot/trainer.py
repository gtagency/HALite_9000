import multiprocessing
import subprocess
import time
import random
from keras.models import Sequential, model_from_json
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop

lookout_dist = 1
"""
input format: (2n+1)^2 inputs for each of ownership, strength, and production
"""

def run_training_game(i, json_file, weights_file):
    print("starting %d" % i)
    retval = subprocess.run(["python3", "run_game.py",
                             "KerasPlayerHltWrapper.py %d %s %s %d" % (0, json_file, weights_file, lookout_dist),
                             "KerasPlayerHltWrapper.py %d %s %s %d" % (1, json_file, weights_file, lookout_dist),
                             ],
                            stdout=subprocess.PIPE)
    print("finished %d" % i)
    return retval.stdout.decode('utf-8')


if __name__ == '__main__':
    input_size = pow((2 * lookout_dist) + 1, 2) * 3

    model = Sequential()
    model.add(Dense(64, input_shape=(input_size,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))

    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))

    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))

    model.add(Dense(5))
    model.add(Activation('softmax'))

    model.compile(loss='mean_squared_error',
                  optimizer=RMSprop(lr=0.001),
                  metrics=['accuracy'])

    weights_file = "weights.h5"
    json_file = "model.json"
    with open(json_file, 'w') as f:
        f.write(model.to_json())
    model.save_weights(weights_file)

    #model2 = model_from_json(json)

    print(run_training_game(0, json_file, weights_file))
