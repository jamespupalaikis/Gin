# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 13:44:19 2022

@author: James
"""

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



class Game: 
# this will run a single game, return a result (reward/score), 
# and a set of moves made throughout the game
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
        self.other = self.player2
        if (startplayer == 2):
            self.start = self.player2
            self.other = self.learner

        self.learner.updatemelds()
        self.player2.updatemelds()





    def playgame_trainreturn(self):
        run = True
        self.discarddeck.add(self.maindeck.deal())
        res = self.dealphase(self.start)
        if(res == 0):
            
            turns = (self.other, self.start)
            
            disc = self.discard(self.start)#check discard for knock
            if(disc == 1):
                run = False
            
        print('#'*82)
        if(res == 1):#if the first player passes, return 1 and give other player turn
            res2 = self.dealphase(self.other)
            
            if(res2 == 0):#if p2 drew, discard and check for knock
                disc = self.discard(self.other)
                if(disc == 1):
                    run = False
                    
            print('#'*82)
            turns = (self.start, self.other)
            
            # this block determines turn order after
            
        if(self.discarddeck.cardcount() == 0):
            self.discarddeck.add(self.maindeck.deal())
            
        while(run == True):
        
            self.playTurn(turns[0])
            res = self.discard(turns[0])
            print('#'*82)
            # result of discard can be 2 options: 
            # a 0 indicates a normal turn, and will continue normally
            # a 1 passed will indicate a knock, or that cards are all out. 
            # in this case, break from the loop and get the winner
            # maybe remove the "knocker" global var?  can just process it here
            if(res == 1):
                break
            self.playTurn(turns[1])
            res = self.discard(turns[1])
            print('#'*82)
            if(res == 1):
                break
        
        # outside loop, knocker has been established already. Get the winner and go home
        

        points = self.getwinner()
        return points,self.learner.first, self.learner.turns
    # above line could possibly be moved to a "training game" function. This
    # could allow for the game class and the training file to be separated, 
    # and the game function being multipurposed for use with the gameplay interface
            

    def interpret(self, card):  # will return a translated card value
        s, v = card
        s = c.suitdict[s]
        v = c.carddict[v]
        return (s, v)


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
                    return 1
                
                print("You can't knock right now!!!!")


            
            elif ((discardindex > (player.cardcount() - 1)) or (discardindex < 0)):
                print('Not a valid number!')
            elif (discardindex >= 0 and (discardindex < player.cardcount())):
                dcard = player.getcard(discardindex)
                print(f'discarded {self.interpret(dcard)}')
                player.hand.discardto(dcard, self.discarddeck)  # TODO: implement this at agent level
                player.sorthand() 


            
                print(f"Deadwood value: {player.deadwood[0]}")
                return 0
            
            elif (discardindex == 'quit'):
                assert (True == False)
                
            print('Enter a valid input!')


    def dealphase(self, first):  
        # first will pass the hand of the player BEING DEALT TO. Index is a 0, unless the previous player has passed
        if (first == self.learner):
            other = self.player2

        else:
            other = self.learner
        # other will be the player that is not drawing
        
     
        print(f"{first.name}'s Turn Now")
        print(f'Discard Deck Faceup Card: {self.interpret(self.discarddeck.peek())}')
        first.printhand()
        while (True):

            # move = input('Enter "draw" to draw card, or "pass" to pass')
            move = first.initialmove(self.discarddeck)
            if (move == 'draw'):
                first.hand.drawfrom(self.discarddeck)
                
                
                # self.state = 'play'
                print('playing turns normally now')

                return 0
                # initiate turn function for other player
            elif (move == 'pass'):
                return 1

            elif (move == 'quit'):
                print('ABORTING')
                assert (False == True)

            else:
                print('enter a valid input!')


    def playTurn(self, player):
        if (player == self.learner):
            other = self.player2

        else:
            other = self.learner


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
                #self.discard(player)
                #if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                #    return

                return
            
            elif (move == '2'):
                #player.hand.drawfrom(self.discarddeck)
                player.hold.append(self.discarddeck.deal())#add it to hold so it cant be discarded
                #self.discard(player)
                #if ((self.knocker[0] is None) == False):  # gotta put after discard to check for a knock
                #    return

                return
                # initiate turn function for other player

            else:
                print('enter a valid move!')