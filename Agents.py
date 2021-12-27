import cards as c
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


class humanplayer(agent):
    def __init__(self, name ):
        self.name = name
        self.hand = c.hand()
    def __repr__:
        return f'Human Player {self.name}'

    def printhand(self):
        print(self.hand)

