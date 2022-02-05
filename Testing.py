import Cards as c
import ModelTraining as m
import Agents as a
import BuildModel as mod
import torch
import numpy as np
import matplotlib.pyplot as plt
import numpy.random as rand
from scipy.special import softmax

#import torchsummary

mydick = c.deck(empty = True)
mydick.add((1,1))
mydick.add((4,13))
#print (mydick.array(top = True))

def get_output_shape(model, image_dim):
    return model(torch.rand(*(image_dim)).unsqueeze(0)).data.shape

'''p1 = a.qlearner(["models/trainingmodels/start_init.pth","models/trainingmodels/draw_init.pth","models/trainingmodels/discard_init.pth"]  )
p2 = a.betterrandom('Bobby')
game = m.TrainGame(p1,p2)
vals = game.playgame()
print(vals[0])
x = 0
for i in vals[2][0]:
    x += 1
    print(x)
    print(i)
x = 0
for i in vals[2][1]:
    x += 1
    print(x)
    print(i)
x = 0
for i in vals[2][2]:
    x += 1
    print(x)
    print(i)
x = 0
for i in vals[2][3]:
    x += 1
    print(x)
    print(i)
x = 0
for i in vals[2][4]:
    x += 1
    print(x)
    print(i)'''

from sklearn.utils import shuffle

load = "models/trainingmodels/draw_0.pth"
dn = mod.DrawNet()
dn.load_state_dict(torch.load(load))
#print(get_output_shape(dn, (2,4,13)))
brd = np.zeros((3,4,13))
brd2 = brd
for i in range(rand.randint(0,22)):
    brd2[rand.randint(0,2)][rand.randint(0,3)][rand.randint(0,12)] = 1
    
    
def unison_shuffled_copies(a, b):
    rng_state = rand.get_state()
    rand.shuffle(a)
    rand.set_state(rng_state)
    rand.shuffle(b)
    


input = torch.tensor(brd2).float().unsqueeze(0)
print(input)
print(dn(input)[0].item())
#print(a)
f = [[1,2],[2,3],[3,4]]
g = [['a','b'],['b','c'],['c','d']]
unison_shuffled_copies(f, g)
print(f, g)

#print(softmax(brd2.flatten()))




