import Cards as c
import PlayGame as p
import random as rand
from Cards import recurse
import BuildModel as mod

import numpy as np
#here we will create "agents" that will interface with the game class.
#TODO: edit PlayGamre file so that instead of "player" attributes being just hand objects, they are "agents"
# each "input" call will instead call a function of the agent object whose turn it is, which will then return a move


class agent:
    def __init__(self, name = 'none'):
        self.name = name
        self.hand = c.hand()
        self.melds = []
        self.deadwood = (100,[])

    def __repr__(self):
        #print(self.hand)
        return 'null agent object'

    def dealhand(self, deck):  # fills your hand from deck
        self.hand.starthand(deck)

    def updatemelds(self):#updates the meld and deadwood info
        deadval, [melds, dead] = recurse(self.gethand())
        self.deadwood = (deadval, dead)
        self.melds = melds



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


class textplayer(agent):
    def __init__(self, name = 'Human Text Guy' ):
        agent.__init__(self, name)
    def __repr__(self):
        return f'Human Player {self.name}'


    def initialmove(self, discarddeck): #the initial move of the game; options are "draw" or pass
        move = input('Enter "draw" to draw card, or "pass" to pass')
        return move

    def discard(self):
        move = (input('Enter the number card you want to discard (0 for first, etc. Type "k" to knock)'))
        return move

    def drawmove(self, discarddeck):
        move = input('Enter "1" to draw from face down deck, or "2" to draw from the discard deck')
        return move

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
    def discard(self):
        moves = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'k']
        r = rand.randint(0,11)
        return moves[r]



class betterrandom(agent):
    def __init__(self, name = "Robby Bot"):
        agent.__init__(self, name)

    def __repr__(self):
        return self.name

    def initialmove(self, discarddeck):#check whether the card matches value of held cards
        for card in self.hand.gethand():
            if(card[1] == discarddeck.peek()[1]):#check for same face value
                return "draw"
        return "pass"

        return
    def discard(self):#discard a random deadwood that is not part of a meld
        self.updatemelds()
        deadv = self.deadvals()
        deadv.sort()
        dead = sum(deadv[:-1])
        if(dead <= 10 ):
            return 'k'
        card = rand.choice(self.deadwood[1])
        return str(self.hand.findcard(card))

        return
    def drawmove(self, discarddeck):#similar to initialmove, check if faceup card matches held values
        for card in self.hand.gethand():
            if(card[1] == discarddeck.peek()[1]):#check for same face value
                return '2'
        return '1'



class simpletree(agent):
    def __init__(self, name = "Sammy Bot"):
        agent.__init__(self, name)

    def __repr__(self):
        return self.name

    def initialmove(self, discarddeck):#check whether the card creates any runs, or matches the value of any held cards
        return
    def discard(self):#discard the highest value deadwood card that there is no value match for
        return
    def drawmove(self):#similar to initialmove, check if faceup card creates runs or matches value
        return

#########################################################################################################################


class qlearner(agent):
    def __init__(self,models,  name = 'GLaDOS'):
        agent.__init__(self, name)

        self.startnet = mod.StartNet()
        self.startnet.load_state_dict(torch.load(models[0]))
        self.drawnet = mod.DrawNet()
        self.drawnet.load_state_dict(torch.load(models[1]))
        self.discardnet = mod.DiscardNet()
        self.discardnet.load_state_dict(torch.load(models[2]))
        self.state = (np.zeros((4,13)),np.zeros((4,13)))#store as 2 2D lists: hand list of 4 suits * 13 cards, and discard list of same
        self.first = (False, np.zeros((104)), -1)#bool for if first move was made, 52 len array for hand, and sparse 52 array for the faceup card(all zeros except 1)
        self.turns = ([],[],[],[],[]) #turns will store a drawboardstate, a draw move (-1 or 1),, a discard boardstate, a set of discard weights, and a discard move for a given turn

    def dealhand(self, deck):  # fills your hand from deck and updates the gamestate
        self.hand.starthand(deck)
        for drawn in self.hand.gethand():
            self.state[0][drawn[0] - 1][drawn[1] - 1] = 1#update hand state

    def savestate_afterdraw(self, drawn, drawdeck = -1):#updates self.state after a draw ( remove from discard if thats where it was drawn from
        assert(self.state[0][drawn[0] - 1][drawn[1] - 1] == 0) #shouldnt be in hand before
        self.state[0][drawn[0] - 1][drawn[1] - 1] = 1 #set hand value to 1
        '''if(discard == -1):#drawn from discardpile
            assert(self.state[1][drawn[0] - 1][drawn[1] - 1] == 1)
            self.state[1][drawn[0] - 1][drawn[1] - 1] = 0#set discarddeck value to 0'''

    #ADD TO TURN LOG


    def savestate_discard(self, discarded, probs):#updates self.state after a discard (update hand, add to discard)
        assert(self.state[0][discarded[0] - 1][discarded[1] - 1] == 1)#should be in hand before
        self.state[0][discarded[0] - 1][discarded[1] - 1] = 0 #remove from hand state
        '''assert (self.state[1][discarded[1] - 1][discarded[1] - 1] == 0)#shouldnt be in discard before
        self.state[1][discarded[0] - 1][discarded[1] - 1] = 1  # add to discard state'''



    #ADD TO TURN LOG


    def singlearray(self, c):#returns a sparsely populated 52 len array with a 1 for a single card
        a = np.zeros((52))
        index = 0
        index += (c[0] - 1) * 13
        index += c[1]
        index -= 1
        a[index] = 1
        return a #this is a little hamfisted, maybe clean up later


    def initialmove(self, discarddeck):#check whether the card creates any runs, or matches the value of any held cards
        top = discarddeck.peek()
        toparr = self.singlearray(top)
        brdstate = np.append(self.state[0].flatten(), toparr, 0)#boardstate to add to self.first
        input = torch.tensor(brdstate).astype(float)
        move = self.startnet(input)[0].item()
        self.first[0] = True
        self.first[1] = brdstate
        if(move < 0):
            self.first[2] = -1

            return 'pass'
        else:
            self.first[2] = 1
            #DO NOT add to hand state, just do it at the beginning of the discard

            return 'draw'

    def drawmove(self,discarddeck):
        top = discarddeck.peek()
        toparr = self.singlearray(top)
        brdstate = np.append(self.state[0].flatten(), discarddeck.array(), 0)#boardstate minus top card
        brdstate2 = np.append(brdstate, toparr, 0)#boardstate to add to log
        input = torch.tensor(brdstate).astype(float)
        move = self.drawnet(input)[0].item()
        self.turns[0].append(brdstate2)
        if (move < 0):#draw from discard pile
            # ADD TO LOG
            self.turns[1].append(-1)
            #DO NOT add to hand state, just do it at the beginning of the discard
            return 2
        else:#draw from facedown pile
            # ADD TO LOG
            self.turns[1].append(1)
            return 1
        return

    def discard(self):
        last = self.gethand()[-1]
        assert (self.state[0][last[0] - 1][last[1] - 1] == 0)  # shouldnt be in hand before
        self.state[0][last[0] - 1][last[1] - 1] = 1  # set hand value to 1
        #log last card drawn as in hand
        ########################
        #build input:
        brdstate = np.append(self.state[0].flatten(), discarddeck.array(top = True), 0)#boardstate WITH top card
        


        return
