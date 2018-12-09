import torch
import torch.nn as nn
import torch.nn.functional as F


class DQN(nn.Module):

    def __init__(self, input_size, nbr_actions):
        super(DQN, self).__init__()
        
        ##First layer, feed our input
        self.fc1 = nn.Linear(input_size, 256)
        ##Hidden layer
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        ##Output layer
        self.fc4 = nn.Linear(64, nbr_actions)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.fc4(x)