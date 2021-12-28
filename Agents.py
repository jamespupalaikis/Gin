import Cards as c
import PlayGame as p

#here we will create "agents" that will interface with the game class.
#TODO: edit PlayGamre file so that instead of "player" attributes being just hand objects, they are "agents"
# each "input" call will instead call a function of the agent object whose turn it is, which will then return a move


class agent:
    def __init__(self):
        self.hand = c.hand()
    def __repr__(self):
        #print(self.hand)
        return 'null agent object'

    def dealhand(self, deck):  # fills your hand from deck
        self.hand.starthand(deck)

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


class humanplayer(agent):
    def __init__(self, name = 'Human Guy' ):
        self.name = name
        self.hand = c.hand()
    def __repr__(self):
        return f'Human Player {self.name}'


    def initialmove(self): #the initial move of the game; options are "draw" or pass
        move = input('Enter "draw" to draw card, or "pass" to pass')
        return move

    def discard(self):
        move = (input('Enter the number card you want to discard (0 for first, etc. Type "k" to knock)'))
        return move

    def drawmove(self):
        move = input('Enter "1" to draw from face down deck, or "2" to draw from the discard deck')
        return move

