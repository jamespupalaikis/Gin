#This will be an (eventually) headless implementation of PlayGame that plays games between a NN Qlearning AI and a given computer adversary
#It will allow for training between each game based on a recorded game log of  moves made.


import Cards as c
from Cards import recurse
import Agents as a
import random as rand

class LogGame: #this will run a single game, return a result (reward/score), and a set of moves made throughout the game
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
        start = self.learner
        if (startplayer == 2):
            start = self.player2

        self.dealphase(start)

        #points for player 1
        points = self.getwinner()
        #result = self.win(points)



    #def interpret(self, card):#will return a translated card value
    #    a,b = card
    #    a = c.suitdict[a]
    #    b = c.carddict[b]
    #    return (a,b)

    #def interpretmelds(self, mylist):
    #    new = []
    #    for meld in mylist:
    #        newmeld = []
    #        for card in meld:
    #            newmeld.append(self.interpret(card))
    #        new.append(newmeld)
    #    return new

    def getwinner(self):
        p1 = recurse(self.learner.gethand())[0]#points for player 1
        p2 = recurse(self.player2.gethand())[0]#... player 2
        if(p1<p2):
            #self.winner = self.learner
            points = p2 - p1
            if(self.knocker[0] == self.player2):
                #('Undercut by Player 1!')
                points += 15
            if(p1 == 0):
                if(self.learner.cardcount() == 11):
                    #("Big Gin by Player 1!")
                    points += 31
                else:
                    #print('Player 1 got gin!')
                    points += 25


        elif(p2<p1):
            #self.winner = self.player2
            points = p1 - p2
            if (self.knocker[0] == self.learner):
                #print('Undercut by Player 2!')
                points -= 15
            if (p2 == 0):
                if (self.player2.cardcount() == 11):
                    #print("Big Gin by Player 2!")
                    points -= 31
                else:
                    #print('Player 2 got gin!')
                    points -= 25

        else:#A push
            #self.winner = self.knocker[1]
            #print("An undercut! winner is the guy who wasnt the knocker! bad code lol")
            if(self.knocker == self.learner):
                points = 15
            else:
                points = -15


        return points

    #def win(self, points):
    #    if(self.winner == self.learner):
    #        p = "Player 1"
    #    else:
    #        p = "Player 2"
    #
    #    print("Congrats " + p + f"!!! You won {points} points!" )


    def knock(self, player):
        player.updatemelds()
        #tally = recurse(player.gethand())
        deadwood = player.deadwood[1]
        deadvals = [c.valuedict[card[1]] for card in deadwood]
        deadvals.sort()
        if(len(deadvals) == 0 ):
            if (player == self.learner):
                self.knocker = (self.learner, self.player2)
            else:
                self.knocker = (self.player2, self.learner)
        elif(len(deadvals) == 1):
            if (player == self.learner):
                self.knocker = (self.learner, self.player2)
            else:
                self.knocker = (self.player2, self.learner)
        elif(sum(deadvals[:-1]) <= 10):
            if(player == self.learner):
                self.knocker = (self.learner, self.player2)
            else:
                self.knocker = (self.player2, self.learner)
            return True
        return False



    def discard(self, player):
        if(self.discarddeck.cardcount() > 0):
            print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        player.printhand()
        while(True):
            #discardindex = (input('Enter the number card you want to discard (0 for first, etc. Type "k" to knock)'))#ADD OPTION TO KNOCK\
            discardindex = player.discard()
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
                    dcard = player.getcard(discardindex)
                    print(f'discarded {self.interpret(dcard)}')
                    player.hand.discardto(dcard, self.discarddeck)#TODO: implement this at agent level
                    player.sorthand()
                    player.updatemelds()

                    print(f"Current Melds: {self.interpretmelds(player.melds)}")#recurse() gives (deadwoodvalue, [[melds], [deadwood']])
                    print(f"Deadwood value: {player.deadwood[0]}")
                    return
            elif(discardindex == 'quit'):
                    assert(True == False)
            print('Enter a valid input!')


    def dealphase(self, first, index = 0): #first will pass the hand of the player BEING DEALT TO. Index is a 0, unless the previous player has passed
        if(first == self.learner):
            other = self.player2
        else:
            other = self.learner

        if(index == 0):
            self.discarddeck.add(self.maindeck.deal())
        while(True):
            move = first.initialmove(self.discarddeck)
            if(move == 'draw'):
                first.hand.drawfrom(self.discarddeck)
                self.discard(first)
                if((self.knocker[0] is None) == False): #gotta put after discard to check for a knock
                    return
                self.discarddeck.add(self.maindeck.deal())
                #self.state = 'play'
                print('playing turns normally now')
                print('###################################################################################')
                self.playTurn(other)
                return
                #initiate turn function for other player
            elif(move == 'pass'):
                if(index == 1):
                    print('playing turns normally now')
                    print('###################################################################################')
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
        if (player == self.learner):
            other = self.player2
            me = "Player 1"
            state = 'p1turn'
        else:
            other = self.learner
            me = "Player 2"
            self.state = 'p2turn'

        print(f"{me}'s Turn Now")
        print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        player.printhand()
        while (True):
            #move = input('Enter "1" to draw from face down deck, or "2" to draw from the discard deck')
            move = player.drawmove(self.discarddeck)
            if (move == '1'):
                print(f'You drew: {self.interpret(self.maindeck.peek())}')
                player.hand.drawfrom(self.maindeck)
                self.discard(player)
                if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                    return
                print('###################################################################################')
                self.playTurn(other)
                return
            elif (move == '2'):
                player.hand.drawfrom(self.discarddeck)
                self.discard(player)
                if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                    return
                print('###################################################################################')
                self.playTurn(other)
                return
                # initiate turn function for other player

            else:
                print('enter a valid move!')

