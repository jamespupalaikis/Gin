import Cards as c
import PlayGame as p
import random as rand
from Cards import recurse
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