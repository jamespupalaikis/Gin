#This program handles the cycle of running a batch of games, saving the 
# agent turn lists after each game, shuffling full batches training data, 
#and then training the networks. Gameplay.py has a playgame_trainreturn
#function that will play a game and return the score

import numpy as np
import numpy.random as rand

import Agents as a
import BuildModel as mod
from Gameplay import Game

import torch
from torch.utils.data import DataLoader, Dataset


###############################################################################

def unison_shuffled_copies(a, b):
    '''Shuffles two lists (data and labels) in the same way'''
    rng_state = rand.get_state()
    rand.shuffle(a)
    rand.set_state(rng_state)
    rand.shuffle(b)

#################################

# GLOBALS
# This determines whether to print progress/loss stuff while training 
output = False
###############################################################################




def manip_first(obj, points):
    '''takes the first move training object(given its first element is True) 
    and puts it into trainable form (described in readme.md)'''
    assert(obj[0] == True)
    status, state, move = obj
    #ADD PENALTY HERE
    return state, points*move/129

def manip_draw(obj, points,manip , turnpenalty = 0.965): 
    '''takes the first 2 elements of the returned data(the draw elements) 
     and puts it into trainable form (described in readme.md)'''
    state, move = obj
    assert(len(state) == len(move))
    state.reverse()
    move.reverse()
    mult = 1.0
    
    for i in range(len(move)):
        if(manip == True):
            label = 0.5
            label += (points*mult *move[i])/(129 * 2)
        
            move[i] = label
        else:
            move[i] = max(move[i], 0)
        mult *= turnpenalty
    print('training move vals', move)
    return state, move


def manip_discard(obj, points, manip, turnpenalty = 0.99): 
    '''takes the last 3 elements of the returned data(the discard elements) 
    and puts into trainable form (described in readme.md)'''
    state, baseprobs, choiceindex = obj
    assert(len(baseprobs) == len(choiceindex))
    state.reverse()
    baseprobs.reverse()
    choiceindex.reverse()
    mult =1.0
    for i in range(len(baseprobs)):
        probs = baseprobs[i]
        overflow = 70 
        #spread from the max 129 points you want in the label adjustment
        val = (points+129)/(258 - 2*overflow)
        val *= mult
        val = max(val, 0)
        val = min(val, 1)
        if(manip == True):
            probs[choiceindex[i]] = val
        #mult *= turnpenalty

    return state, baseprobs


class customData(Dataset):
    '''Dataloader for pytorch model'''
    def __init__(self,x,y):
        x = np.array(x)
        y = np.array(y)
        self.X = torch.FloatTensor(x)
        self.y = torch.FloatTensor(y)
        # self.X = torch.LongTensor(x)
        # self.y = torch.LongTensor(y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, index):
        xdat = self.X[index]
        ydat = self.y[index]
        return (xdat, ydat)

def train_model(dataloader, model, loss_fn, optimizer):
    '''Given a dataloader, a model and training params, will train the model'''
    size = len(dataloader.dataset)
    model.train()
    for batch, (x,y) in enumerate(dataloader):
        x,y = x.to(device), y.to(device)

        # compute error
        pred = model(x)
        if((pred.size() != y.size())):
            y = y.reshape(tuple(pred.size()))
        loss = loss_fn(pred, y)
        #print('loss: ', loss)
        #backpropogate
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    try:
        if (batch % 10 == 0):
            loss, current = loss.item(), batch * len(x)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
    except:#CHECK WHY THIS HAPPENS
        pass

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")


def save_models(models, saveto):
    '''Saves the models (duh)'''
    startnet, drawnet, discnet = models
    startloc, drawloc, discloc = saveto
    torch.save(startnet.state_dict(), startloc)
    torch.save(drawnet.state_dict(), drawloc)
    torch.save(discnet.state_dict(), discloc)
    print('All Models Saved')


def train_cycle(player1, models, opponent, train = (True, True, True),
               batches = (1,1,1), learning = (0.001, 0.00005, 0.00005),
               cyclelength = 1 , manip = True):
    '''Runs a cycle of {cyclelength} games,shuffles the turns, and trains model'''
    l = ([],[],[],[],[],[])
    fulldraw_x,fulldraw_y,fulldiscard_x,fulldiscard_y,fullfirst_x,fullfirst_y=l
    batchstart, batchdraw, batchdisc = batches
    learnstart, learndraw, learndisc = learning
    fullpoints = []
    runfirst = False
    for i in range(cyclelength):
        print('*%*%#' * 30)
        print(' ')
        print(f'On Subcycle {i + 1}')
        print('')
        p1 = player1(models)
        p2 = opponent
        mygame = Game(p1, p2, output=output)
        points, firstvals, turnvals = mygame.playgame_trainreturn()
        
        fullpoints.append(points)
        
        print(f'GameScore: {points}')
        startnet, drawnet, discnet = p1.getmodels()
        
        #######################################################
        if(firstvals[0] == True):
            runfirst = True
            first_x, first_y = manip_first(firstvals, points)
            #fullfirst_x += first_x.tolist()
            fullfirst_x += [first_x]
            fullfirst_y.append( first_y)
     
        draw_x, draw_y = manip_draw(turnvals[:2], points, manip)
        discard_x, discard_y = manip_discard(turnvals[2:], points, manip)
        fulldraw_x += draw_x
        fulldraw_y += draw_y
        fulldiscard_x += discard_x
        fulldiscard_y += discard_y
        
    
    unison_shuffled_copies(fulldraw_x,fulldraw_y )
    unison_shuffled_copies(fulldiscard_x,fulldiscard_y )
    
    ###########################################
    
    

    trans_draw = customData(fulldraw_x, fulldraw_y)
    trans_disc = customData(fulldiscard_x, fulldiscard_y)


    draw_data = DataLoader(trans_draw, batch_size=batchdraw)
    discard_data = DataLoader(trans_disc, batch_size=batchdisc)
    
    drawnet = drawnet.to(device)
    discnet = discnet.to(device)
    
    
    if(runfirst == True):
        unison_shuffled_copies(fullfirst_x,fullfirst_y )
        trans_first = customData(fullfirst_x, fullfirst_y)
        first_data = DataLoader(trans_first, batch_size=batchstart)
        startnet = startnet.to(device)
    
    ###################################################
    if(train[0] == True):
        if(runfirst == True):
            startepochs = 10
            startoptimizer=torch.optim.Adam(startnet.parameters(),lr=learnstart)
            # loss_fn = torch.nn.CrossEntropyLoss()
            startloss_fn = torch.nn.MSELoss()
            startmodel = startnet
            for t in range(startepochs):
                print('epoch ', t + 1, ' out of ', startepochs, ' Startnet')
    
                train_model(first_data,startmodel,startloss_fn, startoptimizer)
    
                #(acc, loss) = test(test_dataloader, model, loss_fn)
    print('#' * 25)
    #######################################################
    if(train[1] == True):
        drawepochs = 32
        drawoptimizer =  torch.optim.Adam(drawnet.parameters(), lr=learndraw)
        #loss_fn = torch.nn.CrossEntropyLoss()
        drawloss_fn =  torch.nn.BCELoss()
        drawmodel = drawnet
        for t in range(drawepochs):
            print('epoch ', t + 1, ' out of ', drawepochs, ' Drawnet')
    
            train_model(draw_data, drawmodel, drawloss_fn, drawoptimizer)
            # (acc, loss) = test(test_dataloader, model, loss_fn)
        
    print('#' * 25)
##############################################################################
    if(train[2] == True):
        discepochs = 32
        discoptimizer = torch.optim.Adam(discnet.parameters(), lr=learndisc)
        #loss_fn = torch.nn.BCELoss()
        #discloss_fn = torch.nn.MSELoss()
        discloss_fn = torch.nn.CrossEntropyLoss()
        discmodel = discnet
        for t in range(discepochs):
            print('epoch ', t + 1, ' out of ', discepochs, ' Discardnet')
    
            train_model(discard_data, discmodel, discloss_fn, discoptimizer)
            # (acc, loss) = test(test_dataloader, model, loss_fn)
    
        # RETURN vals and labels, to assemble back together and train on
    return points

def n_cycles(cycles, cyclelength , loadfrom, saveto, player1 = a.qlearner, 
             opponent = a.betterrandom(),  interval = 4, fromsave= False, 
             addtopoints = True , manip = True):
    
    '''As titled, runs n cycles of {cyclelength} games each, shuffled within 
    each cycle. '''
    
    
    backup = ["models/trainingmodels/start_backup.pth", 
              "models/trainingmodels/draw_backup.pth",
              "models/trainingmodels/discard_backup.pth"]
    if(fromsave == True):
        loadfrom = backup
    startnet = mod.StartNet()
    startnet.load_state_dict(torch.load(loadfrom[0]))
    drawnet = mod.DrawNet()
    drawnet.load_state_dict(torch.load(loadfrom[1]))
    discardnet = mod.DiscardNet()
    discardnet.load_state_dict(torch.load(loadfrom[2]))
    models = [startnet, drawnet, discardnet]
    pts = []
    for i in range(cycles):
        
        
        print(f'cycle: {i + 1} out of {cycles}')
        print(' ')
        print(' ')
        print('#*'*60)
        print(' ')
        print(' ')
        pts.append(train_cycle(player1, models, opponent, 
                              cyclelength=cyclelength, 
                              batches = (1,8,8), 
                              manip = manip))
        
        if((i+1)%interval == 0):
            save_models(models, backup)
    save_models(models, saveto)
    if(addtopoints == True):
        p = np.genfromtxt('pointslist.csv').tolist()
        p += pts
        np.savetxt('pointslist.csv', p)
    print(pts)





     
if (__name__ == "__main__"):

    bench1_1 = ["models/trainingmodels/start_b1.pth",
                "models/trainingmodels/draw_b1.pth",
                "models/trainingmodels/discard_b1.pth"]
    # draw network slightly stabilized
    # strong, stable-ish, needs more high-epoch training. 
    # May be getting interference from discard deck, may want to work that into rewards
    bench2 = ["models/trainingmodels/start_b2.pth",
              "models/trainingmodels/draw_b2.pth",
              "models/trainingmodels/discard_b2.pth"]
    
    bench3 = ["models/trainingmodels/start_b3.pth",
              "models/trainingmodels/draw_b3.pth",
              "models/trainingmodels/discard_b3.pth"]
    #even more stable, some perfect games even
    
    bench4 = ["models/trainingmodels/start_b4.pth",
              "models/trainingmodels/draw_b4.pth",
              "models/trainingmodels/discard_b4.pth"]

    aa = ["models/trainingmodels/start_init.pth",
          "models/trainingmodels/draw_init.pth",
          "models/trainingmodels/discard_init.pth"]
    
    bb = ["models/trainingmodels/start_0.pth", 
          "models/trainingmodels/draw_0.pth", 
          "models/trainingmodels/discard_0.pth"]
    
    cc = ["models/trainingmodels/start_1.pth",
          "models/trainingmodels/draw_1.pth",
          "models/trainingmodels/discard_1.pth"]
     
    dd = ["models/trainingmodels/start_2.pth",
          "models/trainingmodels/draw_2.pth",
          "models/trainingmodels/discard_2.pth"] 
    
    qq = ["models/trainingmodels/startq.pth",
          "models/trainingmodels/drawq.pth",
          "models/trainingmodels/discardq.pth"] 

    n_cycles(1  ,10  ,aa  , aa, player1 = a.qlearner, opponent=a.betterrandom(),addtopoints= True, manip = True)#, fromsave= True)



# TODO: scores list not being updated properly
#BUG" TODO undercut/final scoring being calculated incorrectly