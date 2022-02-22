import Cards as c
import random as rand
from Cards import recurse


from scipy.special import softmax


import torch
import numpy as np
#this will create "agents" that will interface with the game class.

# each "input" call will instead call a function of the agent object whose 
# turn it is, which will then return a move
import copy

class agent:
    def __init__(self, name = 'none'):
        self.name = name
        self.hand = c.hand()
        self.melds = []
        self.deadwood = (100,[])
        self.hold = [] #hold a card drawn from faceup pile so it cant be discarded

    def __repr__(self):

        return 'null agent object'

    def dealhand(self, deck):  # fills your hand from deck
        self.hand.starthand(deck)
    
    def identify(self):#is this a real human?
        return False

    def updatemelds(self, cards = None):#updates the meld and deadwood info
        if(cards is None):
            cards = self.gethand()
        deadval, [melds, dead] = recurse(cards)
        self.deadwood = (deadval, dead)
        self.melds = melds

    def meldslist(self):
        flatlist=[element for sublist in self.melds for element in sublist]
        return flatlist

    def printhand(self):
        print(self.hand)

    def sorthand(self):
        self.hand.sort()

    def gethand(self):
        return self.hand.gethand()

    def cardcount(self):
        return self.hand.cardcount()
    def getcard(self, index):
        return self.hand.getcard(index)
    def deadvals(self):
        return [c.valuedict[card[1]] for card in self.deadwood[1]]

    def singlearray(self, c):
        #returns a sparsely populated 52 len array with a 1 for a single card
        a = np.zeros((4,13))
        a[c[0] -1][c[1] - 1] = 1
        '''index = 0
        index += (c[0] - 1) * 13
        index += c[1]
        index -= 1
        a[index] = 1
        return a #this is a little hamfisted, maybe clean up later'''
        return a

    def gethighdeadcard(self):
        cards = self.deadwood[1] 
        highest = (0, None)
        for card in cards:
            v = c.valuedict[card[1]]
            if (v > highest[0]):
                highest = (v, card)
        return highest[1]
                
            
    def readarray(self, array, val = 1):
        assert(len(array) == 4)
        assert(len(array[0] == 13))
        
        cards = []
        for i in range(4):
            for j in range(13):
                if(array[i][j] == val):
                    cards.append((i+1, j+1))
        
        return cards
        
    def getarraymaxes(self, array):
        assert(len(array) == 4)
        assert(len(array[0] == 13))
        
        max = 0.0
        cards = []
        
        
    def canknock(self):
        self.updatemelds(self.hand.gethand() + self.hold)
        deadwood = self.deadwood[1]
        deadvals = [c.valuedict[card[1]] for card in deadwood]
        deadvals.sort()
        
            
        if (len(deadvals) == 0):
            return True
        elif (len(deadvals) == 1):
            return True
        elif (sum(deadvals[:-1]) <= 10):
            return True
        return False



###############################
class textplayer(agent):
    def __init__(self, name = 'Human Text Guy' ):
        agent.__init__(self, name)
    def __repr__(self):
        return f'Human Player {self.name}'


    def initialmove(self, discarddeck): 
        #the initial move of the game; options are "draw" or pass
        move = input('Enter "draw" to draw card, or "pass" to pass')
        return move

    def discardmove(self,discarddeck):
        move = (input('Enter the number card you want to discard (0 for first, etc. Type "k" to knock)'))
        return move

    def drawmove(self, discarddeck):
        move = input('Enter "1" to draw from face down deck, or "2" to draw from the discard deck')
        return move

#####################################################################
###TODO: Interface with the tkinter event system: move to the Gin.py file? 



class human(agent):
    def __init__(self, name = 'Human' ):
        agent.__init__(self, name)
        
    def __repr__(self):
        return f'{self.name}'
    
    def identify(self):
        return True

    def initialmove(self, event): 
        #the initial move of the game; options are "draw" or pass
        if(event == 1):
            move = 'draw'
        
        if(event == 2):
            move = 'pass'
            
        return move

    def discardmove(self,event):
        #move = (input('Enter the number card you want to discard (0 for first, etc. Type "k" to knock)'))
        
        if(event in range(11)):
            move = str(event)
        elif(event == 'k'):
            move = 'k'
        #if(self.hold != []):
        #    self.hand.addto(self.hold.pop())
        #    self.hold = []
        
        return move

    def drawmove(self, event):
        # = input('Enter "1" to draw from face down deck, or "2" to draw from the discard deck')
        if(event == 1):
            move = '2'
        if(event == 2):
            move = '1'
            
        return move






########################################################################3


class randombot(agent):
    def __init__(self, name = "Randy Bot"):
        agent.__init__(self, name)

    def __repr__(self):
        return self.name

    def initialmove(self, discarddeck):
        moves = ['draw', 'pass']
        r = rand.randint(0,1)
        return moves[r]
    def drawmove(self, discarddeck):
        return str(rand.randint(1,2))
    def discardmove(self,discarddeck):
        moves = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'k']
        r = rand.randint(0,10)
        return moves[r]



#########################################################################



class betterrandom(agent):
    def __init__(self, name = "Robby Bot"):
        agent.__init__(self, name)

    def __repr__(self):
        return self.name

    def initialmove(self, discarddeck):
        #check whether the card matches value of held cards
        for card in self.hand.gethand():
            if(card[1] == discarddeck.peek()[1]):#check for same face value
                return "draw"
        return "pass"

        return
    def discardmove(self,discarddeck):
        #discard a random deadwood that is not part of a meld
        self.updatemelds(self.gethand() + self.hold)
        deadv = self.deadvals()
        deadv.sort()
        dead = sum(deadv[:-1])
        if(dead <= 10 ):
            return 'k'
        #TODO: this bot can still discard the most recently drawn card
        
        
        new = copy.copy(self.deadwood[1])
        
        if(self.hold != []):
            try:
                new.remove(self.hold[0])
            except:
                pass
            self.hand.addto(self.hold.pop())
            self.hold = []
            
        card = rand.choice(new)
        return str(self.hand.findcard(card))


    def drawmove(self, discarddeck):
        #similar to initialmove, check if faceup card matches held values
        top = discarddeck.peek()
        move = '1'
        for card in self.hand.gethand():
            if(card[1] == top[1]):#check for same face value
                move =  '2'
            if((top[0], top[1] + 1) in self.hand.gethand()):
                if(((top[0], top[1] + 2) in self.hand.gethand()) or 
                   ((top[0], top[1] -1) in self.hand.gethand()) ):
                    move =  '2'
            elif(((top[0], top[1] - 1) in self.hand.gethand()) and 
                 ((top[0], top[1] - 2) in self.hand.gethand()) ):
                move =  '2'
        roll = rand.randint(0,10)
        if(roll == 5):
            move = '1'
        return move

##########################################################################

class simpletree(agent):
    def __init__(self, name = "Sammy Bot"):
        agent.__init__(self, name)

    def __repr__(self):
        return self.name

    def initialmove(self, discarddeck):
        return
    def discardmove(self):
        return
    def drawmove(self):
        return

##############################################################################


class qlearner(agent):
    def __init__(self,models,  name = 'GLaDOS'):
        agent.__init__(self, name)
        self.startnet, self.drawnet, self.discardnet = models
        self.state = [np.zeros((4,13)),np.zeros((4,13))]
        #store as 2 2D lists:hand list of 4 suits*13 cards,and discardlist of same
        self.first = [False, np.zeros((104)), -1]
        #bool for if first move was made, 52 len array for hand, 
        #and sparse 52 array for the faceup card(all zeros except 1)
        self.turns = ([],[],[],[],[]) #turns will store a drawboardstate, a 
        #draw move (-1 or 1),, a discard boardstate, a set of discard weights, 
        # and a discard move for a given turn

    def getmodels(self):
        return self.startnet, self.drawnet, self.discardnet

    def dealhand(self, deck):  # fills your hand from deck and updates the gamestate
        self.hand.starthand(deck)
        for drawn in self.hand.gethand():
            self.state[0][drawn[0] - 1][drawn[1] - 1] = 1#update hand state

  




    def initialmove(self, discarddeck):
        top = discarddeck.peek()
        toparr = self.singlearray(top)
        brdstate = np.zeros((2,4,13))

        brdstate[0] = self.state[0]
        brdstate[1] = toparr
        input = torch.tensor(brdstate).float().unsqueeze(0)
        move = self.startnet(input)[0].item()
        self.first[0] = True
        self.first[1] = brdstate
        if(move < 0):
            self.first[2] = -1

            return 'pass'
        else:
            self.first[2] = 1
            #DO NOT add to hand state, 
            # just do it at the beginning of the discard

            return 'draw'

    def drawmove(self,discarddeck):
        top = discarddeck.peek()
        toparr = self.singlearray(top)
        brd = np.zeros((3,4,13))
        brd[0] = self.state[0]
        brd[1] = discarddeck.array()
        brd[2] = toparr

        input = torch.tensor(brd).float().unsqueeze(0)
        move = self.drawnet(input)[0].item()
        print(f'learned draw move: {move}')
        self.turns[0].append(brd)
        if (move < 0.500001):#draw from discard pile
            # ADD TO LOG
            self.turns[1].append(-1)
            #DO NOT add to hand state, 
            # just do it at the beginning of the discard
            return '2'
        else:#draw from facedown pile
            # ADD TO LOG
            self.turns[1].append(1)
            return '1'
        return

    def discardmove(self,discarddeck):
        if(self.hold == []):
            last = self.hand.gethand()[-1]
        else:
            last = self.hold[0]
            
        assert (self.state[0][last[0] - 1][last[1] - 1] == 0)  
        # shouldnt be in hand before
        self.state[0][last[0] - 1][last[1] - 1] = 1  
        # set hand value to 1
        #log last card drawn as in hand
        ########################
        # LOOK FOR KNOCK!!!
        self.updatemelds(self.hand.gethand() + self.hold)
        deadv = self.deadvals()
        deadv.sort()
        dead = sum(deadv[:-1])
        if (dead <= 10):
            return 'k'

        #build input:
        brd = np.zeros((2,4,13))
        brd[0] = self.state[0]
        brd[1] = discarddeck.array(top = True)

        self.turns[2].append(brd)
        input = torch.tensor(brd).float().unsqueeze(0)
        probs = self.discardnet(input).tolist()[0]#add this to log
        #print('probs', np.array(probs).reshape(4,13))
        self.turns[3].append(probs)
        enum = list(enumerate(probs))
        enum.sort(key = lambda x: x[1], reverse=True)
        for ind, cardoption in enum:
            translatedcard = self.hand.translatearray(ind)
            if(translatedcard != last):
                if(self.hand.isinhand(translatedcard)):
                    cardindex = ind #store this in log
                    self.turns[4].append(ind)
    
                    self.state[0][translatedcard[0]-1][translatedcard[1]-1] = 0  
                    #remove the card from hand
                    if(self.hold != []):
                        self.hand.addto(self.hold.pop())
                        self.hold = []
                    return self.hand.findcard(translatedcard)


        return


#################################################################################################################3

class forcetrainer(agent):
    # takes on decision tree based behaviour, logs moves, 
    # and aggressively trains decisions nns with it
    # will use this to mold the nns initially into a stable state
    def __init__(self, models, name='Trainer', behavior = betterrandom):
        agent.__init__(self, name)


        self.startnet, self.drawnet, self.discardnet = models
        self.state = [np.zeros((4,13)),np.zeros((4,13))]
        #store as 2 2D lists:hand list of 4 suits*13 cards, 
        # and discard list of same
        self.first = [False, np.zeros((104)), -1]
        #bool for if first move was made, 52 len array for hand, 
        # and sparse 52 array for the faceup card(all zeros except 1)
        self.turns = ([],[],[],[],[]) 
        #turns will store a drawboardstate, a draw move (-1 or 1),
        # a discard boardstate, a set of discard weights, 
        # and a discard move for a given turn
    
    def getmodels(self):
        return self.startnet, self.drawnet, self.discardnet


    def dealhand(self, deck):  
        # fills your hand from deck and updates the gamestate
        self.hand.starthand(deck)
        for drawn in self.hand.gethand():
            self.state[0][drawn[0] - 1][drawn[1] - 1] = 1#update hand state

    def analyzehand(self):
        hand = self.hand.gethand()
        pairs = [0]*13
        protected = []
        for card in hand:
            if(pairs[card[1] - 1] == 0):
                pairs[card[1] - 1] = -1
            elif(pairs[card[1] - 1] == -1):
                pairs[card[1] - 1] =1
            
            if(((card[0],card[1]-1) in hand) or ((card[0],card[1]+1) in hand)):
                protected.append(card)
        
        for i in range(len(pairs)):
            if(pairs[i] == -1):
                pairs[i] = 0
        
        return pairs, protected
        
        
                

    def initialmove(self, discarddeck):
        top = discarddeck.peek()
        toparr = self.singlearray(top)
        brdstate = np.zeros((2, 4, 13))
        brdstate[0] = self.state[0]
        brdstate[1] = toparr
        move = 'pass'
        for card in self.hand.gethand():
            if(card[1] == discarddeck.peek()[1]):#check for same face value
                move = "draw"


        self.first[0] = True
        self.first[1] = brdstate
        if(move == 'pass'):
            self.first[2] = -1

            return 'pass'
        else:
            self.first[2] = 1
            #DO NOT add to hand state, 
            # just do it at the beginning of the discard

            return 'draw'


    def drawmove(self,discarddeck):
        top = discarddeck.peek()
        toparr = self.singlearray(top)
        brd = np.zeros((3, 4, 13))
        brd[0] = self.state[0]
        brd[1] = discarddeck.array()
        brd[2] = toparr

        move = '1'
        val = 1
        if(top[1] <= 7):
            val -= 0.05
            if(top[1] <= 5 ):
                val -= 0.05
                if(top[1] <= 3):
                    val -= 0.1
                    if(top[1] == 1):
                        val -= 0.1
                        
        for card in self.hand.gethand():
            if(card[1] == top[1]):#check for same face value
                move =  '2'
                val -=   .4
                
        
        if((top[0], top[1] + 1) in self.hand.gethand()):
            val -= .3
            if(((top[0], top[1] + 2) in self.hand.gethand()) ):
                val -= 0.7
                move = '2'
            if((top[0], top[1] -1) in self.hand.gethand()):
                val -= 0.7
                move = '2'
                
        elif(((top[0], top[1] - 1) in self.hand.gethand())  ):
            val -= 0.3
            if((top[0], top[1] - 2) in self.hand.gethand()): 
                val -= 0.7
                move = '2'
            
            
        roll = rand.randint(0,30)
        if(roll == 5):
            move = '1'
            val = 0
            
        val = min(val, 1)
        #move = self.drawnet(input)[0].item()
        self.turns[0].append(brd)
        if (move== '2'):#draw from discard pile
            # ADD TO LOG
            self.turns[1].append(max(val, 0))
            
            #DO NOT add to hand boardstate,
            # just do it at the beginning of the discard
            return '2'
        
        else:#draw from facedown pile
            # ADD TO LOG
            self.turns[1].append(min(val, 1))
            return '1'


    def discardmove(self,discarddeck):
        if(self.hold == []):
            last = self.hand.gethand()[-1]
        else:
            last = self.hold[0]
        assert (self.state[0][last[0] - 1][last[1] - 1] == 0)  
        # shouldnt be in hand before
        self.state[0][last[0] - 1][last[1] - 1] = 1  
        # now set hand value to 1
        self.updatemelds(self.hand.gethand() + self.hold)
        deadv = self.deadvals()
        deadv.sort()
        dead = sum(deadv[:-1])
        if (dead <= 10):
            return 'k'
    ################TODO: make this more sophisticated
    
    
    
        
        viables = copy.copy(self.deadwood[1])
        if(self.hold != []):
            try:
                viables.remove(self.hold[0])
            except:
                pass
            self.hand.addto(self.hold.pop())
            self.hold = []
        secondary = []
        # move =  str(self.hand.findcard(card))
        #probs = self.singlearray(card).flatten()
        pairs, protected = self.analyzehand()
        
        for car in viables:
            if(pairs[car[0] - 1] == 1):
                viables.remove(car)
                if(car not in protected):
                    secondary.append(car)
            elif(car in protected):
                viables.remove(car)
                secondary.append(car)
        
        if(viables != []):
            card = rand.choice(viables)
        
        elif(secondary != []):
            card = rand.choice(secondary)
        
        else: 
            card = rand.choice(self.deadwood[1])
        
        probs = np.ones((4,13))
        for i in range(len(pairs)):
            if(pairs[i] == 1):
                for j in range(4):
                    probs[j][i] -= 0.22
        for car in protected:
            probs[car[0] - 1][car[1]-1] -= 0.22
        
        for i in range(4):
            for j in range(13):
                if(j <9):
                    probs[i][j] -= (.13/10)*(10-j + 1)
                    
            
            
        
        for car in self.meldslist():
            probs[car[0] - 1][car[1]-1] = 0
            
        probs = softmax(probs.flatten(), axis = -1).reshape(4,13)
        for car in self.meldslist():
            probs[car[0] - 1][car[1]-1] = 0
        
        probs = probs.flatten()
        #probs = softmax(probs)
    ###########################
        #build input:
        brd = np.zeros((2, 4, 13))
        brd[0] = self.state[0]
        brd[1] = discarddeck.array(top=True)
        self.turns[2].append(brd)


        #print('probs', probs)
        self.turns[3].append(probs)
        enum = list(enumerate(probs))
        enum.sort(key = lambda x: x[1], reverse=True)
        for ind, cardoption in enum:
            translatedcard = self.hand.translatearray(ind)
            if(self.hand.isinhand(translatedcard)):
                cardindex = ind #store this in log
                self.turns[4].append(ind)

                self.state[0][translatedcard[0] - 1][translatedcard[1] - 1] = 0  
                #remove the card from hand
                
                return self.hand.findcard(translatedcard)


        return