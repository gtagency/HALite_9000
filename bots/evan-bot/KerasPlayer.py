import random
import sys
import os
import hlt
import numpy as np
import time

# copied from http://stackoverflow.com/q/11130156
class suppress_stdout_stderr(object):
    def __init__(self):
        self.null_fds =  [os.open(os.devnull,os.O_RDWR) for x in range(2)]
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        os.dup2(self.null_fds[0],1)
        os.dup2(self.null_fds[1],2)

    def __exit__(self, *_):
        os.dup2(self.save_fds[0],1)
        os.dup2(self.save_fds[1],2)
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])

with suppress_stdout_stderr():
    from keras.models import model_from_json



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Pass in JSON model filename, HDF5 weights filename, and lookout distance")
        exit()

    keras_model_json_filename = sys.argv[1]
    keras_model_weights_filename = sys.argv[2]
    lookout_dist = int(sys.argv[3])
    input_size = pow((2 * lookout_dist) + 1, 2) * 3

    with suppress_stdout_stderr():
        with open(keras_model_json_filename) as f:
            model = model_from_json(f.read())
        model.load_weights(keras_model_weights_filename)

    data_in = ""
    while data_in != "end":
        data_in = str(input())
        x = np.array(data_in.split(',')).reshape((1, input_size))
        y = model.predict(x, batch_size=1, verbose=0)
        move_code = np.random.choice(tuple(range(5)), p=y)
        with open('log2.txt', 'w') as f: f.write(data_in + " " + str(move_code))
        print("$" + move_code)
