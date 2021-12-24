import Cards as c
from Cards import recurse


mydeck = c.deck()

print(mydeck.peek())


class Gin:
    def __init__(self, startplayer = 1):
        self.knocker = (None,None) #FIRST Player is KNOCKER not necessarily winner, other is ther
        self.winner = None
        self.maindeck = c.deck(shuffled = True)
        self.discarddeck = c.deck(empty = True)
        self.player1 = c.hand(self.maindeck)
        self.player2 = c.hand(self.maindeck)
        self.state = 'deal'#gives the gamestate
        self.player1.sort()
        self.player2.sort()
        start = self.player1
        if(startplayer == 2):
            start = self.player2
        self.dealphase(start)

        #points for player 1
        points = self.getwinner()
        self.win(points)


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

    def getwinner(self):
        p1 = recurse(self.player1.gethand())[0]#points for player 1
        p2 = recurse(self.player2.gethand())[0]#... player 2
        if(p1<p2):
            self.winner = self.player1
            points = p2 - p1
            if(self.knocker[0] == self.player2):
                print('Undercut by Player 1!')
                points += 25
            if(p1 == 0):
                if(self.player1.cardcount() == 11):
                    print("Big Gin by Player 1!")
                    points += 31
                else:
                    print('Player 1 got gin!')
                    points += 25


        elif(p2<p1):
            self.winner = self.player2
            points = p1 - p2
            if (self.knocker[0] == self.player1):
                print('Undercut by Player 2!')
                points += 25
            if (p2 == 0):
                if (self.player2.cardcount() == 11):
                    print("Big Gin by Player 2!")
                    points += 31
                else:
                    print('Player 2 got gin!')
                    points += 25

        else:#A push
            self.winner = self.knocker[1]
            print("An undercut! winner is the guy who wasnt the knocker! bad code lol")
            points = 25

        return points

    def win(self, points):
        if(self.winner == self.player1):
            p = "Player 1"
        else:
            p = "Player 2"

        print("Congrats " + p + f"!!! You won {points} points!" )


    def knock(self, player):
        tally = recurse(player.gethand())
        deadwood = tally[1][1]
        deadvals = [c.valuedict[card[1]] for card in deadwood]
        deadvals.sort()
        if(len(deadvals) == 0 ):
            if (player == self.player1):
                self.knocker = (self.player1, self.player2)
            else:
                self.knocker = (self.player2, self.player1)
        elif(len(deadvals) == 1):
            if (player == self.player1):
                self.knocker = (self.player1, self.player2)
            else:
                self.knocker = (self.player2, self.player1)
        elif(sum(deadvals[:-1]) <= 10):
            if(player == self.player1):
                self.knocker = (self.player1, self.player2)
            else:
                self.knocker = (self.player2, self.player1)
            return True
        return False



    def discard(self, player):
        if(self.discarddeck.cardcount() > 0):
            print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        print(player)
        while(True):
            discardindex = (input('Enter the number card you want to discard (0 for first, etc. Type "k" to knock)'))#ADD OPTION TO KNOCK\

            try:
                discardindex = int(discardindex)
            except:
                if(discardindex != 'k'):
                    print('Enter a number! (or k)')

            if(isinstance(discardindex, str)):
                tryknock = self.knock(player)
                if(tryknock == True):#knock accepted
                    return
                print("You can't knock right now!!!!")


                #print('ass', type(discardindex))
            elif((discardindex > player.cardcount()) or (discardindex < 0)):
                    print('Not a valid number!')
            elif(discardindex >= 0 and (discardindex < player.cardcount())):
                    player.discardto(player.getcard(discardindex), self.discarddeck)
                    player.sort()
                    eval = recurse(player.gethand())
                    print(f"Current Melds: {self.interpretmelds(eval[1][0])}")
                    print(f"Deadwood value: {eval[0]}")
                    return
            elif(discardindex == 'quit'):
                    assert(True == False)
            print('Enter a valid input!')


    def dealphase(self, first, index = 0): #first will pass the hand of the player BEING DEALT TO. Index is a 0, unless the previous player has passed
        if(first == self.player1):
            other = self.player2
            me = "Player 1"
            self.state = 'p1deal'
        else:
            other = self.player1
            me = "Player 2"
            self.state = 'p2deal'
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
                if((self.knocker[0] is None) == False): #gotta put after discard to check for a knock
                    return
                self.discarddeck.add(self.maindeck.deal())
                #self.state = 'play'
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
            state = 'p1turn'
        else:
            other = self.player1
            me = "Player 2"
            self.state = 'p2turn'

        print(f"{me}'s Turn Now")
        print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        print(player)
        while (True):
            move = input('Enter "1" to draw from face down deck, or "2" to draw from the discard deck')
            if (move == '1'):
                print(f'You drew: {self.interpret(self.maindeck.peek())}')
                player.drawfrom(self.maindeck)
                self.discard(player)
                if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                    return
                self.playTurn(other)
                return
            elif (move == '2'):
                player.drawfrom(self.discarddeck)
                self.discard(player)
                if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                    return
                self.playTurn(other)
                return
                # initiate turn function for other player

            else:
                print('enter a valid move!')

game = Gin()
