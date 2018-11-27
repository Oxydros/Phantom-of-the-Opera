import random
import numpy as np
import logging

## Based on https://github.com/transedward/pytorch-dqn/blob/master/utils/replay_buffer.py
class ReplayBuffer(object):

    def __init__(self, size, state_dim):
        self.max_size = size
        self.next_id = 0
        self.buffer_size = 0
        self.state_dim = state_dim

        self.states = None
        self.next_states = None
        self.actions = None
        self.reward = None
        self.done = None

    ## Return true if there is enough data
    ## to be sample for a batch of batch_size
    def can_sample_batch(self, batch_size):
        return batch_size + 1 <= self.buffer_size

    ## Return a batch of random data
    ## of size batch_size
    def get_batch(self, batch_size):
        assert self.can_sample_batch(batch_size)
        ## Generate random ids
        idxs = [random.randint(0, self.buffer_size - 1) for i in range(batch_size)]
        logging.info("[ReplayBuffer] Selected random batch : %s"%(idxs))

        ## Generate batch given the random ids
        state_batch = self.states[idxs]
        next_state_batch = self.next_states[idxs]
        action_batch = self.actions[idxs]
        reward_batch = self.reward[idxs]
        done_batch = np.array([1.0 if self.done[i] else 0.0 for i in idxs], dtype=np.float32)
        return state_batch, action_batch, reward_batch, next_state_batch, done_batch

    def store(self, state, action, reward, next_state, done):
        if self.states is None:
            self.states = np.empty([self.max_size] + [self.state_dim], dtype=np.float32)
            self.next_states = np.empty([self.max_size] + [self.state_dim], dtype=np.float32)
            self.actions = np.empty([self.max_size], dtype=np.int32)
            self.reward = np.empty([self.max_size], dtype=np.float32)
            self.done = np.empty([self.max_size], dtype=np.bool)

        self.states[self.next_id] = state
        self.actions[self.next_id] = action
        self.reward[self.next_id] = reward
        self.next_states[self.next_id] = next_state
        self.done[self.next_id] = done

        self.next_id = (self.next_id + 1) % self.max_size
        self.buffer_size = min(self.max_size, self.buffer_size + 1)

