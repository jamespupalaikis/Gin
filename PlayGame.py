import Cards as c
from Cards import recurse


mydeck = c.deck()

print(mydeck.peek())


class Gin:
    def __init__(self):
        self.maindeck = c.deck(shuffled = True)
        self.discarddeck = c.deck(empty = True)
        self.player1 = c.hand(self.maindeck)
        self.player2 = c.hand(self.maindeck)
        self.state = 'deal'#gives the gamestate
        self.player1.sort()
        self.player2.sort()

    def interpret(self, card):#will return a translated card value
        a,b = card
        a = c.suitdict[a]
        b = c.carddict[b]
        return (a,b)

    def interpretmelds(self, mylist):
        new = []
        for meld in mylist:
            newmeld = []
            for card in meld:
                newmeld.append(self.interpret(card))
            new.append(newmeld)
        return new


    def discard(self, player):
        if(self.discarddeck.cardcount() > 0):
            print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        print(player)
        while(True):
            discardindex = int(input('Enter the number card you want to discard (0 for first, etc)'))#ADD OPTION TO KNOCK\
            #print('ass', type(discardindex))
            if((discardindex > player.cardcount()) or (discardindex < 0)):
                print('Not a valid number!')
            if(discardindex >= 0 and (discardindex < player.cardcount())):
                player.discardto(player.getcard(discardindex), self.discarddeck)
                player.sort()
                eval = recurse(player.gethand())
                print(f"Current Melds: {self.interpretmelds(eval[1][0])}")
                print(f"Deadwood value: {eval[0]}")
                return
            if(discardindex == 'quit'):
                assert(True == False)
            print('Enter a valid input!')


    def dealphase(self, first, index = 0): #first will pass the hand of the player BEING DEALT TO. Index is a 0, unless the previous player has passed
        if(first == self.player1):
            other = self.player2
            me = "Player 1"
        else:
            other = self.player1
            me = "Player 2"
        #other will be the player that is not drawing
        if(index == 0):
            self.discarddeck.add(self.maindeck.deal())
        print(f"{me}'s Turn Now")
        print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        print(first)
        while(True):

            move = input('Enter "draw" to draw card, or "pass" to pass')
            if(move == 'draw'):
                first.drawfrom(self.discarddeck)
                self.discard(first)
                self.discarddeck.add(self.maindeck.deal())
                self.state = 'play'
                print('playing turns normally now')
                self.playTurn(other)
                return
                #initiate turn function for other player
            elif(move == 'pass'):
                if(index == 1):
                    print('playing turns normally now')
                    self.playTurn(other)
                    return
                elif(index == 0):
                    self.dealphase(other, index = 1)
                    return

            elif(move == 'quit'):
                print('ABORTING')
                assert(False == True)

            else:
                print('enter a valid input!')


    def playTurn(self, player):
        if (player == self.player1):
            other = self.player2
            me = "Player 1"
        else:
            other = self.player1
            me = "Player 2"

        print(f"{me}'s Turn Now")
        print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        print(player)
        while (True):
            move = input('Enter "1" to draw from face down deck, or "2" to draw from the discard deck')
            if (move == '1'):
                print(f'You drew: {self.interpret(self.maindeck.peek())}')
                player.drawfrom(self.maindeck)
                self.discard(player)
                self.playTurn(other)
                return
            elif (move == '2'):
                player.drawfrom(self.discarddeck)
                self.discard(player)
                self.playTurn(other)
                return
                # initiate turn function for other player
                return
            else:
                print('enter a valid move!')

game = Gin()
game.dealphase(game.player1)