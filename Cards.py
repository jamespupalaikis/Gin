import numpy as np
import random as rand
from copy import deepcopy

##############################################################################
suitdict = {1: 'C', 2: 'D', 3: 'H', 4: 'S'}
valuedict = {1:1,2:2,3:3,4:4,5:5, 6:6,7:7, 8:8, 9:9, 10:10, 11:10, 12:10,13:10}
carddict = {1:'A',2:'2',3:'3',4:'4',5:'5', 6:'6',7:'7', 8:'8', 9:'9', 
            10:'10', 11:'J', 12:'Q',13:'K'}

##############################################################################
def flatten(list_of_lists):
    if (len(list_of_lists) == 0):
        return list_of_lists
    if (isinstance(list_of_lists[0], list)):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


def lessthan(left,right):  
# comparison function returning if left is lower value than right 
# (by suit, then face value)

    if (left[0] == right[0]):
        if(left[1] == right[1]):
            print(left, right)
        assert (left[1] != right[1])
        return (left[1] < right[1])
    else:
        return (left[0] < right[0])



def sorthand(hand):
    if (len(hand) > 1):
        mid = len(hand) // 2
        left = hand[:mid]
        right = hand[mid:]

        # Recursive call on each half
        sorthand(left)
        sorthand(right)

        # Two iterators for traversing the two halves
        i = 0
        j = 0

        # Iterator for the main list
        k = 0

        while( i < len(left) and j < len(right)):
            if (lessthan(left[i] ,right[j])):
                # The value from the left half has been used
                hand[k] = left[i]
                # Move the iterator forward
                i += 1
            else:
                hand[k] = right[j]
                j += 1
            # Move to the next slot
            k += 1

            # For all the remaining values
        while( i < len(left)):
            hand[k] = left[i]
            i += 1
            k += 1

        while( j < len(right)):
            hand[k] = right[j]
            j += 1
            k += 1
##############################################################################
def getvalue(cards): 
    #takes a list of cards and returns the sum of their face values
    total = 0
    copy = deepcopy(cards)
    while(copy != []):
        new = copy.pop()
        total += valuedict[new[1]]
    return total

def isrun(cards):
    #returns whether contained cards contain a run
    if(len(cards) < 3):
        return False
    sorthand(cards)
    start = cards.pop(0)
    while(cards != []):
        next = cards.pop(0)
        if((start[0] == next[0]) and (next[1] == start[1] + 1)):
            start = next
        else:
            return False
    return True



def findrun(card, bin):
    # finds if a run can be made using the card, and the cards from the bin
    goods = list(filter(lambda x: x[0] == card[0] , bin))
    #filter to same suit
    goods = list(filter(lambda x:  x[1] > card[1] , goods))
    #filter out smaller cards 
    # (they should have been included in prev searches bc hand is sorted)
    while(goods != []):
        if(isrun([card] + goods)):
            runmade = [card] + goods
            return (runmade, list(filter(lambda x: x not in runmade, bin )))
        goods = goods[:-1]

    ass = [card] + bin
    sorthand(ass)
    return(( [] , ass))





def findset(card, bin):
    #same but for sets, return ([set created], [remaining bin])
    goods = list(filter(lambda x: x[1] == card[1] , bin))
    bin2 = list(filter(lambda x: x not in goods, bin))
    if(len(goods) >= 2):
        #print(f'foundset: {[card] + goods}, remaining: {bin2}')
        return ([card] + goods, bin2)
    else:
        ass = [card] + bin
        sorthand(ass)
        #print('setfind failed: ',([], ass) )
        return ([], ass)

def ismeld(bin):
    for card in bin:
        newbin = list(filter(lambda x: x != card ,bin))
        if(findrun(card, newbin) or (findset(card, newbin) )):
            return True
    return False


def recurse(bin, melds = [], bestscore = 1000, bestgroup = [[],[]] ,index = 0):
    #recurse() gives (deadwoodvalue, [[melds], [deadwood']])
    #print("STARTING!", f"BIN IS {bin}")
    if ((ismeld(bin) == False) or (index >= len(bin))): #(index >= len(bin)):

        val = getvalue(bin)
        #print(f'index: {index}, bin: {bin}, score: {val}')
        if(val < bestscore):
            bestscore = val
            bestgroup = [melds, bin]
        return bestscore, bestgroup

    sorthand(bin)
    #print(len(bin), index)
    card = bin[index]
    #print('1', bin)
    binmin = bin[:index] + bin[index + 1:]
    #print('2', binmin)
    newmeld, newbin = findrun(card, binmin)
    newmeld2, newbin2 = findset(card, binmin)


    if newmeld == []:
        group1 = recurse( bin, melds, bestscore, bestgroup, index + 1)
        #print(1, group1)
    else:
        group1 = recurse( newbin,melds + [newmeld], bestscore, bestgroup, 0)
        if(group1 is None):
           
            pass

    if newmeld2 == []:
        group2 = recurse( bin, melds,bestscore, bestgroup, index + 1)
    else:
        group2 = recurse( newbin2,melds + [newmeld2], bestscore, bestgroup, 0)
        if (group2 is None):
            pass
    score1, grouped1 = group1
    score2, grouped2 = group2

    if(score1 <= score2):
        return score1,grouped1
    else:
        return score2, grouped2

def meldeval(hand):
    melds =recurse(hand)[1][0]
    flat = flatten(melds)
    deadwood = list(filter(lambda x:x not in flat, hand))
    return melds, deadwood
#############################################################################

class deck:
    def __init__(self, shuffled = True, empty = False):
        self.deck = []
        if(empty == False):
            for suit in range(1,5):
                for val in range(1,14):
                    self.deck.append((suit, val))

            if(shuffled == True):
                rand.shuffle(self.deck)
    #def

    def __repr__(self):
        rep = 'Deck: '
        for card in self.deck:
            (a,b) = card
            rep+= str((suitdict[a], carddict[b])) + ', '
        return rep[:-2]

    def cardcount(self):
        return(len(self.deck))

    def deal(self):
        top = self.deck.pop(0)
        #print('card removed')
        return top

    def peek(self):
        assert((self.deck) != [])
        top = self.deck[0]
        return top

    def add(self, card):#add to the top of the deck
        self.deck = [card] + self.deck
        #print('card added')

    def array(self, top = False):
        #return an 52 len array of 1 for the cards that are in the deck minus 
        # the top card if top = false (for backend use only)
        
        arr = np.zeros((4,13))
        for card in self.deck[1:]:
            arr[card[0] - 1][card[1] -1] = 1
        if((top == True) and len(self.deck) > 0):
            top = self.deck[0]
            arr[top[0] - 1][top[1] - 1] = 1

        return arr





class hand:
    def __init__(self):
        self.cards = []


    def __repr__(self):
        rep = 'Hand: '
        for card in self.cards:
            (a, b) = card
            rep += str((suitdict[a], carddict[b])) + ', '
        return rep[:-2]

    def starthand(self, deck):
        self.cards = [] 
        #clear current hand
        while (len(self.cards) != 10):
            self.cards.append(deck.deal())
        assert (len(self.cards) == 10)


    def drawfrom(self, deck):
        self.cards.append(deck.deal())

    def discardto(self,card,deck):
        #takes a card index (from 0) and discards it into specified deck
        self.cards = list(filter(lambda x: x != card,self.cards))
        deck.add(card)

    def sort(self):
        sorthand(self.cards)

    def cardcount(self):
        return len(self.cards)


    def findcard(self, card):
        return self.cards.index(card)


    def getcard(self, index):

        assert(index >= 0)
        assert(index < len(self.cards))
        return self.cards[index]
    def gethand(self):
        return self.cards

    def isinhand(self, card):#check if card is in hand
        for c in self.cards:
            if (c == card):
                return True
        return False

    def translatearray(self, arrayindex): 
        #translates a 0-51 array index to a card value
        suit = arrayindex//13 + 1
        face = arrayindex%13 + 1
        return (suit, face)
    
    def addto(self, card):
        self.cards.append(card)


##############################################################################


