from keras.layers import Dense, Flatten, Conv2D, Permute, Conv2DTranspose
from keras.models import Sequential
from keras.models import model_from_json
from keras.optimizers import Adam
from rl.agents.dqn import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy

from atari_processor import AtariProcessor
from constants import *


def load_model(filename='models/model_raw_images.'):
    model_json = open(filename + 'json', 'r')
    loaded_model_json = model_json.read()
    model_json.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(filename + 'h5')
    print("Loaded model from disk")
    return loaded_model


def get_cnn_model(input_shape=INPUT_SHAPE_CNN, nb_actions=2):
    model = Sequential()
    model.add(Permute((2, 3, 1), input_shape=input_shape))
    model.add(Conv2D(32, (8, 8), strides=(4, 4), activation='relu'))
    model.add(Conv2D(64, (4, 4), strides=(2, 2), activation='relu'))
    model.add(Conv2D(64, (3, 3), strides=(1, 1), activation='relu'))
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dense(nb_actions, activation='linear'))
    return model


def get_agent_from_model(model, nb_actions, input_shape):
    memory = SequentialMemory(limit=50000, window_length=WINDOW_LENGTH)
    processor = AtariProcessor(input_shape=input_shape, preprocess_images=PREPROCESS)
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05,
                                  nb_steps=1000000)
    dqn = DQNAgent(model=model, nb_actions=nb_actions, policy=policy, memory=memory, processor=processor,
                   nb_steps_warmup=50000, gamma=.99, target_model_update=10000, train_interval=4, delta_clip=1.)
    dqn.compile(Adam(lr=.00025), metrics=['mae'])
    return dqn


def adapt_model_to_alife(model, input_shape=(3, 3)):
    complete_model = Sequential()
    complete_model.add(Conv2DTranspose(4, (SHRUNKEN_SHAPE[0], SHRUNKEN_SHAPE[1] - input_shape[0] + 1)
                                       , input_shape=(1,)+input_shape, padding='valid'))
    complete_model.add(Permute((3, 1, 2)))
    complete_model.add(model)
    return model