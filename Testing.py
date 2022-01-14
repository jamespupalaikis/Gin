import Cards as c
import ModelTraining as m
import Agents as a
import BuildModel as mod
import torch
import numpy as np
import matplotlib.pyplot as plt

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




dn = mod.DiscardNet()
#print(get_output_shape(dn, (2,4,13)))
brd = np.zeros((2,4,13))
input = torch.tensor(brd).float().unsqueeze(0)
print(dn(input))
#print(a)