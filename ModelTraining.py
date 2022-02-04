#This will be an (eventually) headless implementation of PlayGame that plays games between a NN Qlearning AI and a given computer adversary
#It will allow for training between each game based on a recorded game log of  moves made.
import numpy as np

import Cards as c
from Cards import recurse
import Agents as a
import numpy.random as rand
import BuildModel as mod

#######

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose
from sklearn.utils import shuffle
import matplotlib.pyplot as plt




#################################

def unison_shuffled_copies(a, b):
    rng_state = rand.get_state()
    rand.shuffle(a)
    rand.set_state(rng_state)
    rand.shuffle(b)
    
#################################

class TrainGame: #this will run a single game, return a result (reward/score), and a set of moves made throughout the game
    def __init__(self, qlearner,player2 ):
        startplayer = rand.randint(1,2)
        self.knocker = (None,None) #FIRST Player is knocker
        self.winner = None
        self.maindeck = c.deck(shuffled = True)
        self.discarddeck = c.deck(empty = True)
        self.learner = qlearner
        self.player2 = player2
        # (gamescore,[starting move, [boardstates...], [draw action made:-1 or 1...], [(discard action state, index of discard action made),...])
        # NOTE: the first draw action is associated with the SECOND boardstate if the AI goes first, as the first real draw is a different network
        #self.learnstate = (0, [],[],[])
        ####################################

        self.learner.dealhand(self.maindeck)
        self.player2.dealhand(self.maindeck)
        self.learner.sorthand()
        self.player2.sorthand()
        self.start = self.learner
        if (startplayer == 2):
            self.start = self.player2


        self.learner.updatemelds()
        self.player2.updatemelds()





    def playgame(self):
        self.dealphase(self.start)
        points = self.getwinner()
        return points,self.learner.first, self.learner.turns

    def interpret(self, card):  # will return a translated card value
        a, b = card
        a = c.suitdict[a]
        b = c.carddict[b]
        return (a, b)


    def interpretmelds(self, mylist):
        new = []
        for meld in mylist:
            newmeld = []
            for card in meld:
                newmeld.append(self.interpret(card))
            new.append(newmeld)
        return new


    def getwinner(self):
        self.learner.updatemelds()
        self.player2.updatemelds()
        p1 = self.learner.deadwood[0]
        p2 = self.player2.deadwood[0]
        self.learner.hold = []
        self.player2.hold = []
        if (p1 < p2):
            points = p2 - p1
            if (self.knocker[0] == self.player2):
                print(f'Undercut by {self.learner.name}!')
                points += 25
            if (p1 == 0):
                if (self.learner.cardcount() == 11):
                    print(f"Big Gin by {self.learner.name}!")
                    points += 31
                else:
                    print(f'{self.learner.name} got gin!')
                    points += 25


        elif (p2 < p1):
            points = -1 * (p1 - p2)
            if (self.knocker[0] == self.learner):
                print(f'Undercut by {self.player2.name}!')
                points -= 25
            if (p2 == 0):
                if (self.player2.cardcount() == 11):
                    print(f"Big Gin by {self.player2.name}!")
                    points -= 31
                else:
                    print(f'{self.player2.name} got gin!')
                    points -= 25

        else:  # A push
            if((self.knocker[1] is None) == False):
                print(f'An undercut by {self.knocker[1].name}')
                if(self.knocker[1] == self.learner):
                    points = 25
                else:
                    points = -25
            else:
                
                return 0

        return points




    def knock(self, player):
        deadwood = player.deadwood[1]
        deadvals = [c.valuedict[card[1]] for card in deadwood]
        deadvals.sort()
        print('dead: ', deadvals)
        print('melds: ', player.melds)
        if (len(deadvals) == 0):
            if (player == self.learner):
                self.knocker = (self.learner, self.player2)
            else:
                self.knocker = (self.player2, self.learner)
            return True
        elif (len(deadvals) == 1):
            if (player == self.learner):
                self.knocker = (self.learner, self.player2)
            else:
                self.knocker = (self.player2, self.learner)
            return True
        elif (sum(deadvals[:-1]) <= 10):
            if (player == self.learner):
                self.knocker = (self.learner, self.player2)
            else:
                self.knocker = (self.player2, self.learner)
            return True
        return False


    def discard(self, player):
        if (self.discarddeck.cardcount() > 0):
            print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        player.printhand()
        while (True):
            # discardindex = (input('Enter the number card you want to discard (0 for first, etc. Type "k" to knock)'))#ADD OPTION TO KNOCK\
            discardindex = player.discardmove(self.discarddeck)
            try:
                discardindex = int(discardindex)
            except:
                if (discardindex != 'k'):
                    print('Enter a number! (or k)')

            if (isinstance(discardindex, str)):
                
                tryknock = self.knock(player)
                if (tryknock == True):  # knock accepted
                    print('knock accepted')
                    print(player.deadwood)
                    player.hand.discardto(player.gethighdeadcard(), self.discarddeck)
                    print(player.deadwood)
                    return
                print("You can't knock right now!!!!")

                # print('ass', type(discardindex))
            
            elif ((discardindex > (player.cardcount() - 1)) or (discardindex < 0)):
                print('Not a valid number!')
            elif (discardindex >= 0 and (discardindex < player.cardcount())):
                dcard = player.getcard(discardindex)
                print(f'discarded {self.interpret(dcard)}')
                player.hand.discardto(dcard, self.discarddeck)  # TODO: implement this at agent level
                player.sorthand()
                #player.updatemelds()

                #print(
                #    f"Current Melds: {self.interpretmelds(player.melds)}")  # recurse() gives (deadwoodvalue, [[melds], [deadwood']])
                print(f"Deadwood value: {player.deadwood[0]}")
                return
            elif (discardindex == 'quit'):
                assert (True == False)
            print('Enter a valid input!')


    def dealphase(self, first,
                  index=0):  # first will pass the hand of the player BEING DEALT TO. Index is a 0, unless the previous player has passed
        if (first == self.learner):
            other = self.player2
            self.state = 'p1deal'
        else:
            other = self.learner
            self.state = 'p2deal'
        # other will be the player that is not drawing
        if (index == 0):
            self.discarddeck.add(self.maindeck.deal())
        print(f"{first.name}'s Turn Now")
        print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        first.printhand()
        while (True):

            # move = input('Enter "draw" to draw card, or "pass" to pass')
            move = first.initialmove(self.discarddeck)
            if (move == 'draw'):
                first.hand.drawfrom(self.discarddeck)
                self.discard(first)
                if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                    return
                self.discarddeck.add(self.maindeck.deal())
                # self.state = 'play'
                print('playing turns normally now')
                print('###################################################################################')
                self.playTurn(other)
                return
                # initiate turn function for other player
            elif (move == 'pass'):
                if (index == 1):
                    print('playing turns normally now')
                    print('###################################################################################')
                    self.playTurn(other)
                    return
                elif (index == 0):
                    self.dealphase(other, index=1)
                    return

            elif (move == 'quit'):
                print('ABORTING')
                assert (False == True)

            else:
                print('enter a valid input!')


    def playTurn(self, player):
        if (player == self.learner):
            other = self.player2
            me = "Player 1"
            state = 'p1turn'
        else:
            other = self.learner
            me = "Player 2"
            self.state = 'p2turn'

        print(f"{player.name}'s Turn Now")
        print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        player.printhand()

        while (True):
            # move = input('Enter "1" to draw from face down deck, or "2" to draw from the discard deck')
            move = player.drawmove(self.discarddeck)
            if (move == '1'):
                try:
                    top = (self.maindeck.peek())
                except:
                    print('Everyone sucks, no more cards')
                    return
                print(f'You drew: {self.interpret(self.maindeck.peek())}')
                player.hand.drawfrom(self.maindeck)
                self.discard(player)
                if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                    return
                print('###################################################################################')
                self.playTurn(other)
                return
            elif (move == '2'):
                #player.hand.drawfrom(self.discarddeck)
                player.hold.append(self.discarddeck.deal())#add it to hold so it cant be discarded
                self.discard(player)
                if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                    return
                print('###################################################################################')
                self.playTurn(other)
                return
                # initiate turn function for other player

            else:
                print('enter a valid move!')


########################################################################################################################




def manipfirst(obj, points):#takes the first move training object(given its first element is True) and puts it into trainable form
    assert(obj[0] == True)
    status, state, move = obj
    #ADD PENALTY HERE
    return state, points*move/129

def manipdraw(obj, points,manip , turnpenalty = 0.965): #takes the first 2 elements of the returned data(the draw elements) and puts it into trainable form
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


def manipdiscard(obj, points, manip, turnpenalty = 0.99): #takes the last 3 elements of the returned data(the discard elements) and puts into trainable form
    state, baseprobs, choiceindex = obj
    assert(len(baseprobs) == len(choiceindex))
    state.reverse()
    baseprobs.reverse()
    choiceindex.reverse()
    mult =1.0
    for i in range(len(baseprobs)):
        probs = baseprobs[i]
        overflow = 70 #spread from the max 129 points you want in the label adjustment
        val = (points+129)/(258 - 2*overflow)
        val *= mult
        val = max(val, 0)
        val = min(val, 1)
        if(manip == True):
            probs[choiceindex[i]] = val
        #mult *= turnpenalty

    return state, baseprobs


class customData(Dataset):
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

def trainmodel(dataloader, model, loss_fn, optimizer):
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
        if (batch % 1 == 0):
            loss, current = loss.item(), batch * len(x)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
    except:#CHECK WHY THIS HAPPENS
        pass

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")


def savemodels(models, saveto):

    startnet, drawnet, discnet = models
    startloc, drawloc, discloc = saveto
    torch.save(startnet.state_dict(), startloc)
    torch.save(drawnet.state_dict(), drawloc)
    torch.save(discnet.state_dict(), discloc)
    print('All Models Saved')


def TrainCycle(player1, models, opponent, train = (True, True, True), batches = (1,1,1), learning = (0.001, 0.00005, 0.00005), cyclelength = 1 , manip = True):
    fulldraw_x, fulldraw_y, fulldiscard_x, fulldiscard_y, fullfirst_x, fullfirst_y = [],[],[],[],[],[]
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
        game = TrainGame(p1, p2)
        points, firstvals, turnvals = game.playgame()
        
        fullpoints.append(points)
        
        print(f'GameScore: {points}')
        startnet, drawnet, discnet = p1.getmodels()
        
        #######################################################
        if(firstvals[0] == True):
            runfirst = True
            first_x, first_y = manipfirst(firstvals, points)
            #fullfirst_x += first_x.tolist()
            fullfirst_x += [first_x]
            fullfirst_y.append( first_y)
     
        draw_x, draw_y = manipdraw(turnvals[:2], points, manip)
        discard_x, discard_y = manipdiscard(turnvals[2:], points, manip)
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
            startoptimizer = torch.optim.Adam(startnet.parameters(), lr=learnstart)
            # loss_fn = torch.nn.CrossEntropyLoss()
            startloss_fn = torch.nn.MSELoss()
            startmodel = startnet
            for t in range(startepochs):
                print('epoch ', t + 1, ' out of ', startepochs, ' Startnet')
    
                trainmodel(first_data, startmodel, startloss_fn, startoptimizer)
    
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
    
            trainmodel(draw_data, drawmodel, drawloss_fn, drawoptimizer)
            # (acc, loss) = test(test_dataloader, model, loss_fn)
        
    print('#' * 25)
#################################################################################################################
    if(train[2] == True):
        discepochs = 32
        discoptimizer = torch.optim.Adam(discnet.parameters(), lr=learndisc)
        #loss_fn = torch.nn.BCELoss()
        #discloss_fn = torch.nn.MSELoss()
        discloss_fn = torch.nn.CrossEntropyLoss()
        discmodel = discnet
        for t in range(discepochs):
            print('epoch ', t + 1, ' out of ', discepochs, ' Discardnet')
    
            trainmodel(discard_data, discmodel, discloss_fn, discoptimizer)
            # (acc, loss) = test(test_dataloader, model, loss_fn)
    
        # RETURN vals and labels, to assemble back together and train on
    return points

def n_cycles(cycles, cyclelength , loadfrom, saveto, player1 = a.qlearner, opponent = a.betterrandom(),  interval = 4, fromsave= False, addtopoints = True , manip = True):
    backup = ["models/trainingmodels/start_backup.pth", "models/trainingmodels/draw_backup.pth",
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
        pts.append(TrainCycle(player1, models, opponent, cyclelength=cyclelength, batches = (1,8,8), manip = manip))
        if((i+1)%interval == 0):
            savemodels(models, backup)
    savemodels(models, saveto)
    if(addtopoints == True):
        p = np.genfromtxt('pointslist.csv').tolist()
        p += pts
        np.savetxt('pointslist.csv', p)
    print(pts)





     
if (__name__ == "__main__"):

    bench1_1 = ["models/trainingmodels/start_b1.pth","models/trainingmodels/draw_b1.pth","models/trainingmodels/discard_b1.pth"]#draw network slightly stabilized
    #strong, stable-ish, needs more high-epoch training. May be getting interference from discard deck, may want to work that into rewards
    bench2 = ["models/trainingmodels/start_b2.pth","models/trainingmodels/draw_b2.pth","models/trainingmodels/discard_b2.pth"]
    bench3 = ["models/trainingmodels/start_b3.pth","models/trainingmodels/draw_b3.pth","models/trainingmodels/discard_b3.pth"]
    #even more stable, some perfect games even
    aa = ["models/trainingmodels/start_init.pth","models/trainingmodels/draw_init.pth","models/trainingmodels/discard_init.pth"]
    bb = ["models/trainingmodels/start_0.pth", "models/trainingmodels/draw_0.pth", "models/trainingmodels/discard_0.pth"]
    cc = ["models/trainingmodels/start_1.pth","models/trainingmodels/draw_1.pth","models/trainingmodels/discard_1.pth"]
    dd = ["models/trainingmodels/start_2.pth","models/trainingmodels/draw_2.pth","models/trainingmodels/discard_2.pth"] 
    qq = ["models/trainingmodels/startq.pth","models/trainingmodels/drawq.pth","models/trainingmodels/discardq.pth"] 
    #n_cycles(5  ,15  ,cc, dd, player1 = a.forcetrainer, opponent=a.betterrandom(),addtopoints= False, manip = False)#, fromsave= True)
    n_cycles(1,1,dd,bench3 , player1 = a.qlearner, opponent=a.betterrandom(),addtopoints= False)#, fromsave= True)

