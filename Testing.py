import Cards as c
import ModelTraining as m
import Agents as a
import BuildModel as b


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


a = [1,1,1,1,1]
a.reverse()
penalty = 0.99
mult = 1
labels = []
for i in range(len(a)):
    a[i] *= mult
    mult *= penalty

print(a[2:])