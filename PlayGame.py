import Cards as c
from Cards import meldeval


mydeck = c.deck()

print(mydeck.peek())


class Gin:
    def __init__(self):
        self.maindeck = c.deck(shuffle = True)
        self.discarddeck = c.deck(empty = True)
        self.player1 = c.hand(maindeck)
        self.player2 = c.hand(maindeck)
        self.state = 'deal'#gives the gamestate

    def discard(self, player):
        print()

    def dealphase(self, first, index = 0): #first will pass the hand of the player BEING DEALT TO. Index is a 0, unless the previous player has passed
        self.discarddeck.add(self.maindeck)
        print(f'Discard Deck: {self.discarddeck.peek()}')
        while(True):
            move = input('Enter "draw" to draw card, or "pass" to pass')
            if(move == 'draw'):
                #draw card
                #run discard
                #change gamestate to active




        return

