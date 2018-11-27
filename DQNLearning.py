import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.autograd as autograd

import random
import logging
from Net import DQN
from ReplayBuffer import ReplayBuffer

LEARNING_RATE = 0.001
REPLAY_SIZE = 3000
GAMMA = 0.80
UPDATE_FREQ = 30

class DQNAgent():
    def __init__(self, input_size,
                output_size, batch_size = 32):
        self.input_size = input_size
        self.output_size = output_size
        
        ##DQN network
        self.model = DQN(input_size, output_size)
        self.optimizer = torch.optim.RMSprop(self.model.parameters())

        self.param_update_counter = 0
        self.target_model = DQN(input_size, output_size)        

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
        fraction  = min(float(step) / 100, 1.0)
        return 1.0 + fraction * -0.9

    ##Epsilon greddy selection
    ##Explore using random, or exploit the model
    def select_epsilon_greedy(self, state, step):
        rand = random.random()
        epsilon_threashold = self.get_epsilon_threshold(step)
        if rand > epsilon_threashold:
            logging.debug("[IA] Taking model advice")
            tensor = torch.FloatTensor([state])
            return self.model(tensor)
        else:
            logging.debug("[IA] Taking random advice")
            ##Return random values for actions QTable
            return torch.FloatTensor([[random.random() for _ in range(self.output_size)]])

    ##Process the input data
    def process(self, state):
        # print("Got data %s of len %d and expecting %d"%(state, len(state), self.input_size))
        if (len(state) != self.input_size):
            raise ValueError("Bad input data")

        ##Increase current step
        self.counter += 1

        ##Retrieve Q values for actions
        actions = self.select_epsilon_greedy(state, self.counter)

        # logging.info("[DQN] e-greedy actions: %s"%(actions))

        ##Return data on possible actions
        return actions

    ##User taken action
    ##Based on the return of process
    def action_taken(self, state, action):
        ##Saving data
        if self.last_data != None:
            raise ValueError("Missing a next state call !")
        if action >= 20:
            raise ValueError("Bad action value !")
        self.last_data = (state, action)

    def next_state(self, new_state):
        state, action = self.last_data
        data_to_save = (state, action, new_state)
        self.scheduled_data.append(data_to_save)
        self.last_data = None

    ##Reward fed by the user
    ##Reward all actions taken since last reward
    ##Reward is every half turn (ghost scream, innocents, etc.)
    def reward(self, rew, end_game):
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

    def train(self):
        ##Train every 4 steps and if bath size is OK
        if not (self.replay_buffer.can_sample_batch(self.batch_size) and self.counter % 4 == 0):
            return
        state_batch, act_batch, rew_batch, nstate_batch, d_batch = self.replay_buffer.get_batch(self.batch_size)
        state_batch = torch.from_numpy(state_batch)
        act_batch = torch.from_numpy(act_batch).long()
        rew_batch = torch.from_numpy(rew_batch).view(self.batch_size, 1)
        nstate_batch = torch.from_numpy(nstate_batch)
        d_batch = torch.from_numpy(1 - d_batch).type(torch.FloatTensor).view(self.batch_size, 1)

        q_values = self.model(state_batch)

        print(q_values)
        print(act_batch)

        ## Get the taken action for each state (action is the index of the QValue taken from the table)
        current_Q_Values = q_values.gather(1, act_batch.unsqueeze(1))

        ## Compute best action for next state
        next_max_q = self.target_model(nstate_batch).detach().max(1)[0].view(self.batch_size, 1)

        ## If the state was the end of the game don't take in consideration the next Q value
        ## Set them to 0
        next_Q_values = d_batch * next_max_q

        ## Compute the target
        target_Q_values = rew_batch + (GAMMA * next_Q_values)

        ## Compute error
        bellman_error = target_Q_values - current_Q_Values
        clipped_bellman_error = bellman_error.clamp(-1, 1)

        d_error = clipped_bellman_error * -1.0

        ## Init optimizer
        self.optimizer.zero_grad()
        current_Q_Values.backward(d_error.data)

        ## Optimize params
        self.optimizer.step()
        self.param_update_counter += 1

        ## Update target model
        if self.param_update_counter % UPDATE_FREQ == 0:
            self.target_model.load_state_dict(self.model.state_dict())


    ##Reset step
    def reset(self):
        logging.debug("[DQN] Reset step counter")
        self.counter = 0