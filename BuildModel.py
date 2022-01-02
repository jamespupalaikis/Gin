import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose

import matplotlib.pyplot as plt


import numpy as np

#############################
# ## In this file, the model(s) will be build and instantiated with a single generic training example.
# There will be 3 neural networks comprising this model:
# The Start network: Will handle ONLY the first draw/pass move. It will take in a hand(52 binary) plus the faceup card (52 binary)
    # and will pass back a number that will be - for pass, + for draw
    # it will be reinforced with the final reward score(+ for win, - for loss) multiplied by some TBD reward penalty * the sign of the decision made
    #NOTE: this may be way more stable because its a cleaner subset of moves used, or way less stable because the data will be much sparser
    #Hell, maybe I will make this a simple decision tree, as there technically is a "correct" move if youre not tracking opponent strategy

#The "draw" network: Will handle decision of which pile to draw from on a normal turn. It will take 52+52+52 array of "gamestate" and pass back a float
    #again, - for discard, + for main (maybe reverse?)
    #a gamestate will be an array of binaries for which cards in hand (first 52), which cards in discard(next 52) minus the one on top
    #plus 52 more for the faceup card
    #it will be reinforced with the (game score)/129 *  the sign of decision made (+1, -1), * the reward penalty

#the last, (probably most complex) network will be the "discard" network, which will handle decisions on which card to discard after a draw
    #it will  take a 104 binary gamestate in, and return (SUBJECT TO CHANGE):
    #a 52 *card* array, containing a ranking of each card. Decision is made based on card/(sum all cards) probability
    #ALternate training protocol:
        #reinforced by the returned value(I.E. Eval the boardstate again) but replace the chosen card with (score+129)/258
        #NOTE: this may reinforce too many incorrect moves unintentionally
        #NOTE: You will have to adjust the learning rate based on the reward penalty I think, or else you cannot implement it
    #NOTE; learning rate will need to be quite small given the stochastic nature of games and luck-dependent gamescores

#info will be passed in at the end of a game in the following form:
#(gamescore,[starting move, [boardstates...], [draw action made:-1 or 1...], [(discard action state, index of discard action made),...])
#NOTE: the first draw action is associated with the SECOND boardstate, as the first real draw is a different network


#IDEA: implement embedding layer to "semantically" encode information about runs, sets, and general suit information for each card location
#embedding would allow you to keep separate the entry pipelines from the discard pile, your hand, your opponent's hand, and then fork them back together


class StartNet(nn.Module):
    def __init__(self):
        super(StartNet, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(52 + 52, 64),
            nn.ReLU(),
            nn.Linear(64,64),
            nn.ReLU(),
            nn.Linear(64,1)

        )

    def forward(self,x):
        #x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

class DrawNet(nn.Module):
    def __init__(self):
        super(DrawNet, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(52+52 + 52, 128),
            nn.ReLU(),
            nn.Linear(128,128),
            nn.ReLU(),
            nn.Linear(128,1)
        )

    def forward(self,x):
        #x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

class DiscardNet(nn.Module):
    def __init__(self):
        super(DiscardNet, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(52 + 52 , 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 52)
        )

    def forward(self,x):
        #x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


if (__name__ == "__main__"):
    startnet =  StartNet()
    torch.save(startnet.state_dict(), "models/trainingmodels/start_init.pth")
    print("Saved PyTorch Model State to models/trainingmodels/start_init.pth")

    drawnet =  DrawNet()
    torch.save(drawnet.state_dict(), "models/trainingmodels/draw_init.pth")
    print("Saved PyTorch Model State to models/trainingmodels/draw_init.pth")

    discardnet =  DiscardNet()
    torch.save(discardnet.state_dict(), "models/trainingmodels/discard_init.pth")
    print("Saved PyTorch Model State to models/trainingmodels/discard_init.pth")
#x = np.ndarray*[[0 for i in range(104)]]
#x = torch.tensor(np.expand_dims(np.append(np.zeros((52,1)),(np.zeros((52,1))), 0), -1) )
    x = torch.tensor((np.append(np.zeros((52,) ),(np.zeros((52,))), 0)) )
    print(x.shape)
#x = torch.tensor(x)
    pred = startnet(x.float())
    print(pred)
    print(pred[0].item())