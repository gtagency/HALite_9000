import sys
import numpy as np
import time
from keras.models import model_from_json



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Pass in JSON model filename, HDF5 weights filename, and lookout distance")
        exit()

    keras_model_json_filename = sys.argv[1]
    keras_model_weights_filename = sys.argv[2]
    lookout_dist = int(sys.argv[3])
    input_size = pow((2 * lookout_dist) + 1, 2) * 3

    with open(keras_model_json_filename) as f:
        model = model_from_json(f.read())
    model.load_weights(keras_model_weights_filename)

    # with open('log_player.txt', 'w') as f:
    #     f.write("starting log\n")
        # print("test")
    data_in = ""
    while data_in != "end":
        raw = input()
        data_in = tuple(int(x) for x in raw.split(','))
        # f.write(str(len(data_in)) + '\n')
        # f.write(str(data_in) + '\n')
        x = np.array(data_in).reshape((1, input_size))
        y = model.predict(x, batch_size=1, verbose=0)
        # f.write(str(y) + '\n')
        total = sum(y.flat)
        move_code = np.random.choice(tuple(range(5)), p=tuple(a/total for a in y.flat))
        # f.write(str(move_code) + '\n')
        print("result: %d" % move_code)


