from networking import *
import os
import sys
import numpy as np

myID, gameMap = getInit()

with open(os.devnull) as stderr:
    from keras.models import load_model
    from keras import backend as K
    import keras.objectives
    import keras.activations

def pointwise_softmax(x):
    return K.map_fn(lambda y: K.softmax(y), x)

def custom_objective(y_true, y_pred):
    return keras.objectives.categorical_crossentropy(y_true, y_pred)

keras.activations.pointwise_softmax = pointwise_softmax
keras.objectives.custom_objective = custom_objective

model = load_model("model.h5")

model.predict(np.random.randn(1, 20, 20, 4)).shape # make sure model is compiled during init

def stack_to_input(stack):
    return stack.transpose(1,2,0)

def frame_to_stack(frame):
    game_map = np.array([[(x.owner, x.production, x.strength) for x in row] for row in frame.contents])
    return np.array([(game_map[:, :, 0] == myID),  # 0 : owner is me
                      ((game_map[:, :, 0] != 0) & (game_map[:, :, 0] != myID)),  # 1 : owner is enemy
                      game_map[:, :, 1]/20,  # 2 : production
                      game_map[:, :, 2]/255,  # 3 : strength
                      ]).astype(np.float32)

sendInit('ardapekis')
while True:
    stack = frame_to_stack(getFrame())
    positions = np.transpose(np.nonzero(stack[0]))
    pred = model.predict(np.expand_dims(stack_to_input(stack),0))
    output = [pred[0,x,y].argmax() for (x,y) in positions]
    sendFrame([Move(Location(positions[i][1],positions[i][0]), output[i]) for i in range(len(positions))])
