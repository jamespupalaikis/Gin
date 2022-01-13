import Cards as c
import ModelTraining as m
import Agents as a
import BuildModel as mod
import torch
import numpy as np
import matplotlib.pyplot as plt

mydick = c.deck(empty = True)
mydick.add((1,1))
mydick.add((4,13))
#print (mydick.array(top = True))

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




plt.plot([-29, -51, 55, 34, -31, 56, -7, 43, 70, 8, 64, 33, -17, 48, -12, -16, 27, 31, 41, -33, 35, 37, 3, -32, -18, -30, -30, -1, 55, 41, 69, -3, 27, -15, 13, -29, 33, 58, -6, 58, 29, -16, 29, 36, -31, 81, -15, 55, -9, 22, 65, -14, 54, 31, 32, 40, -3, 31, -11, 2, -26, 1, -7, 36, 36, 46, 27, 38, 50, -4, 43, -6, 41, 27, 27, -5, -3, -1, 36, 50, 44, -8, 57, -11, -44, -11, -7, 42, -29, 26, 29, -10, 34, 62, -14, 58, 49, 31, 29, -19] )
plt.show()
#print(a)