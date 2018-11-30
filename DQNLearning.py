import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.autograd as autograd

import random
import logging
from Net import DQN
from ReplayBuffer import ReplayBuffer

LEARNING_RATE = 0.000025
ALPHA = 0.95
EPS = 0.01
REPLAY_SIZE = 1000000
GAMMA = 0.99
UPDATE_FREQ = 5000
START_LEARNING = 50000
LEARNING_FREQ = 16

class DQNAgent():
    def __init__(self, input_size,
                output_size, name = "NoName", batch_size = 32):
        self.name = name

        self.input_size = input_size
        self.output_size = output_size
        
        ##DQN network
        self.model = DQN(input_size, output_size)
        self.load_params()

        self.target_model = DQN(input_size, output_size)
        self.target_model.load_state_dict(self.model.state_dict())

        self.optimizer = torch.optim.RMSprop(self.model.parameters(), lr=LEARNING_RATE,
                            alpha=ALPHA, eps=EPS)

        self.param_update_counter = 0

        #Trainin vars
        self.batch_size = batch_size
        self.replay_buffer = ReplayBuffer(REPLAY_SIZE, self.input_size)

        ##Used for e-greedy policy
        self.counter = -1

        ##Saved data
        self.last_data = None
        self.scheduled_data = []

    ##Return the threshold for the e-greedy algorithm
    ##depending on the current step of the learning
    def get_epsilon_threshold(self, step):
        fraction  = min(float(step) / 1000000, 1.0)
        return 1.0 + fraction * (0.1 - 1.0)

    ##Epsilon greddy selection
    ##Explore using random, or exploit the model
    def select_epsilon_greedy(self, state, step):
        rand = random.random()
        epsilon_threashold = self.get_epsilon_threshold(step)
        if step > START_LEARNING and rand > epsilon_threashold:
            logging.debug("[IA] Taking model advice")
            tensor = torch.Tensor([state])
            return self.model(tensor)
        else:
            logging.debug("[IA] Taking random advice")
            ##Return random values for actions QTable
            return torch.Tensor([[random.random() for _ in range(self.output_size)]])

    ##Process the input data
    def process(self, state):
        # print("Got data %s of len %d and expecting %d"%(state, len(state), self.input_size))
        if (len(state) != self.input_size):
            raise ValueError("Bad input data")

        ##Increase current step
        self.counter += 1

        ##Retrieve Q values for actions
        actions = self.select_epsilon_greedy(state, self.counter)

        ##Return data on possible actions
        return actions

    ##User taken action
    ##Based on the return of process
    def action_taken(self, state, action):
        ##Saving data
        if self.last_data != None:
            raise ValueError("Missing a next state call !")
        if action not in [i for i in range(self.output_size)]:
            raise ValueError("Bad action value !")
        self.last_data = (state, action)

    ##Return true if we are waiting a next state
    def awaitingNextState(self):
        return self.last_data != None

    ## Fetch the last data and add it next state
    ## Add the result in the scheduled queue
    ## to await the reward
    def next_state(self, new_state):
        state, action = self.last_data
        data_to_save = (state, action, new_state)
        self.scheduled_data.append(data_to_save)
        self.last_data = None

    ##Reward fed by the user
    ##Reward all actions taken since last reward
    ##Reward is every half turn (ghost scream, innocents, etc.)
    def reward(self, rew, end_game):
        logging.debug("[IA] Applying reward of %d to %s"%(rew, self.scheduled_data))
        rew = max(-1.0, min(rew, 1.0))
        ##Iterating over scheduled data to append reward
        for scheduled_data in self.scheduled_data:
            state, action, new_state = scheduled_data
            ##Apply end_game only if this is the last state stored (end can only be notified at the end of the tour)
            self.replay_buffer.store(state, action, rew, new_state, end_game if scheduled_data == self.scheduled_data[-1] else False)
        ##Clear all data from tour
        self.scheduled_data.clear()

        ##Trigger train
        self.train()

    #CF Algorithm 1 from paper http://web.stanford.edu/class/psych209/Readings/MnihEtAlHassibis15NatureControlDeepRL.pdf
    def train(self):
        ##Train every 4 steps and if bath size is OK
        if not (self.counter > START_LEARNING and
                self.counter % LEARNING_FREQ == 0 and
                self.replay_buffer.can_sample_batch(self.batch_size)):
            return
        state_batch, act_batch, rew_batch, nstate_batch, d_batch = self.replay_buffer.get_batch(self.batch_size)
        state_batch = torch.from_numpy(state_batch)
        act_batch = torch.from_numpy(act_batch).long()
        rew_batch = torch.from_numpy(rew_batch).view(self.batch_size, 1)
        nstate_batch = torch.from_numpy(nstate_batch)
        d_batch = torch.from_numpy(1 - d_batch).type(torch.Tensor).view(self.batch_size, 1)

        q_values = self.model(state_batch)

        ## Get the taken action for each state (action is the index of the QValue taken from the table)
        current_Q_Values = q_values.gather(1, act_batch.unsqueeze(1))

        ## Compute best Q value for next state
        next_max_q = self.target_model(nstate_batch).detach().max(1)[0].view(self.batch_size, -1)

        ## If the state was the end of the game don't take in consideration the next Q value
        ## as it doesn't exist
        ## Set them to 0
        next_Q_values = d_batch * next_max_q

        ## Add the reward to the potential future reward
        target_Q_values = rew_batch + (GAMMA * next_Q_values)

        #based on https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
        loss = F.smooth_l1_loss(current_Q_Values, target_Q_values)

        ## Init optimizer
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.model.parameters():
            param.grad.data.clamp(-1, 1)

        ## Optimize params
        self.optimizer.step()
        self.param_update_counter += 1

        if self.counter % 500 == 0:
            logging.info("Step %d"%(self.counter))
        ## Update target model
        if self.param_update_counter % UPDATE_FREQ == 0:
            logging.info("Step %d - Updating target model"%(self.counter))
            self.target_model.load_state_dict(self.model.state_dict())
            self.save_params()

    ##Reset step
    def reset(self):
        logging.debug("[DQN] Reset step counter")
        self.counter = 0

    def save_params(self):
        try:
            logging.info("Saving model params to ./saved_params_" + self.name)
            torch.save(self.model, "./saved_params_" + self.name)
            torch.save(self.target_model, "./target_saved_params_" + self.name)
        except Exception as e:
            logging.critical("Error: " + str(e))

    def load_params(self):
        try:
            logging.info("Fetching previous trained model")
            self.model = torch.load("./saved_params_" + self.name)
            logging.info("Previous model loaded with success. Weights:")
            for param in self.model.parameters():
                logging.info(param.data)
        except:
            logging.info("Couldn't load model. Starting from scratch")

    def __del__(self):
        self.save_params()