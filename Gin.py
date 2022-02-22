# events-example0.py
# Barebones timer, mouse, and keyboard events
import Cards as c
from tkinter import *
import numpy.random as rand
import BuildModel as mod
import torch
import Gameplay as game

import Agents as agents

from time import sleep
####################################
# customize these functions
####################################
#TODO
#TODO
#TODO
# need to implement turn log
# need to prettify knock button
# need to fix the sleep timer so that it sleeps while the proper turn instructions are shown
# polish win screen/add replay button
# add option to type name at beginning, label the players maybe

#AMBITIOUS GOALS: 
# implement animations (this might be a disaster)
# implement full games
# implement difficulty settings


########################

def init(data):
    # load data.xyz as appropriate

    
    data.winner = [None, 0]
    #stores winner and score
    
    data.showall = False
    #whether to display opponent cards
    
    
    data.s, data.v = rand.randint(1,5),rand.randint(1,14)
    
    data.disp = 'menu'
    # what to display
    
    data.log = [-1, (0,0)] 
    # display the last turn made
    
    data.cardmenulist = [[rand.randint(1,5), rand.randint(1,14), rand.randint(5,22), rand.randint(100,1200), 0] ] 
    # cards falling in the menu
    
    loadfrom = ["models/trainingmodels/start_b3.pth",
              "models/trainingmodels/draw_b3.pth",
              "models/trainingmodels/discard_b3.pth"]
    
    startnet = mod.StartNet()
    startnet.load_state_dict(torch.load(loadfrom[0]))
    drawnet = mod.DrawNet()
    drawnet.load_state_dict(torch.load(loadfrom[1]))
    discardnet = mod.DiscardNet()
    discardnet.load_state_dict(torch.load(loadfrom[2]))
    data.models = [startnet, drawnet, discardnet]

    
    data.mode = None
    
    data.startpass = True #True until a pass is given, then False
    
    data.diff = 0
    #difficulty; 0 for easy, 1 for normal
    
    
    pass

##############################################################################
def drawsuit(canvas,suit,x,y):
    if(suit == 1): #club
        r = 7
        canvas.create_oval(x-r,y-r -11, x+r,y+r-11 , fill = 'black')
        canvas.create_oval(x-r - 6,y-r , x+r - 6,y+r , fill = 'black')
        canvas.create_oval(x-r + 6,y-r , x+r + 6,y+r , fill = 'black')
        canvas.create_line(x,y,x,y + 14, width = 4)
        
    if(suit == 2): #diamond
        canvas.create_polygon(x - 10, y , x,y+20, x + 10, y ,x,y-20, fill = 'red')
        
    if(suit == 3): #heart
        r = 8
        canvas.create_polygon(x - 16, y , x,y+20, x + 16, y , fill = 'red')
        canvas.create_oval(x-r + 7,y-r-1 , x+r + 7,y+r-1 , fill = 'red', outline = 'red')
        canvas.create_oval(x-r - 7,y-r-1 , x+r - 7,y+r-1 , fill = 'red', outline = 'red')
        
    if(suit == 4): #spade
        r = 8
        canvas.create_polygon(x - 16, y+3 , x,y-20 +3, x + 16, y+3 , fill = 'black')
        canvas.create_oval(x-r + 7,y-r+3 , x+r + 7,y+r+3 , fill = 'black', outline = 'black')
        canvas.create_oval(x-r - 7,y-r+3 , x+r - 7,y+r+3 , fill = 'black', outline = 'black')
        canvas.create_line(x,y,x,y + 18, width = 4)




##############################################################################
def drawCard(canvas, suit, value, x,y, outline = 'black'):
    #card size will be 70*120, centered at x,y
    #as usual suit 1-4, value 1-13
    canvas.create_rectangle(x-40, y-60, x+40, y + 60, width = 2, fill = 'white', outline = outline)
    if(suit == 0 and value == 0):
    #this will represent a card back instead (don't feel like writing a new fn)
        canvas.create_rectangle(x-35, y-55, x+35, y + 55, width = 8, outline = 'red', fill = 'light green')
        canvas.create_oval(x-31,y-31,x+31,y+31, fill = 'dark green', outline = 'green')
        canvas.create_text(x,y,text = '$', font = 'arial 30', fill = 'yellow')
        canvas.create_text(x - 20, y - 40, text = '$', font = 'arial 15', fill = 'yellow')
        canvas.create_text(x + 20, y + 40, text = '$', font = 'arial 15', fill = 'yellow')
        canvas.create_text(x + 20, y - 40, text = '$', font = 'arial 15', fill = 'yellow')
        canvas.create_text(x - 20, y + 40, text = '$', font = 'arial 15', fill = 'yellow')
        #canvas.create_text(x,y,text = 'fuck you fuck you', angle = 55)
        
        
    
    else:
        drawsuit(canvas, suit, x,y)
        canvas.create_text(x - 30, y - 50, text = c.carddict[value])
        canvas.create_text(x + 30, y + 50, text = c.carddict[value])
    
##############################################################################
def cardClicker(x,y):
    # Interpret clicking on cards in hand for discard
    zone = -1
    if(y > 340 and y < 460):
        if(x > 300 and x < 350):
            zone = 'k'
    else:
        x -= 52
        if(y <655 and y > 545 ):
            zone = x // 105
            if(zone > 10):
                return -1

    return zone 
    
    
    return -1


def translateLog(data):
    base = data.log
    deck = ['facedown deck', 'faceup deck'][data.log[0] - 1]
    v = c.carddict[data.log[1][1]]
    s = ['clubs', 'diamonds', 'hearts', 'spades'][data.log[1][0] -1]
    card = v + ' of ' + s
    return f'Drew from {deck}, and then discarded {card}'

###############DRAWING########################################################
def drawMenu(canvas, data):
    #canvas.create_rectangle()
    for card in data.cardmenulist:
        drawCard(canvas, card[0], card[1], card[3], card[4])
    
    canvas.create_rectangle(data.width//2 - 190, data.height//2 + 60, data.width//2 + 190, data.height//2 + 180, fill = 'yellow')
    canvas.create_text(data.width//2, data.height//2 - 220, text = 'Gin Rummy',font="Arial 80 bold", fill = 'green')
    canvas.create_text(data.width//2, data.height//2 - 100, text = 'Select Difficulty',font="Arial 33 bold", fill = 'blue')
    canvas.create_text(data.width//2 - 100, data.height//2 , text = 'Easy',font="Arial 23 bold", fill = 'black')
    canvas.create_text(data.width//2 + 100, data.height//2 , text = 'Normal',font="Arial 23 bold", fill = 'black')
    canvas.create_text(data.width//2, data.height//2 + 120, text = 'Play Now',font="Arial 55 bold", fill = 'blue')
    
    
    
    
    if(data.diff == 0):
        canvas.create_polygon(data.width//2 - 150, data.height//2,
                              data.width//2 - 180, data.height//2 - 30,
                              data.width//2 - 180, data.height//2 + 30,
                              fill = 'red')
    elif(data.diff == 1):
        canvas.create_polygon(data.width//2 + 45, data.height//2,
                              data.width//2 + 15, data.height//2 - 30,
                              data.width//2 + 15, data.height//2 + 30,
                              fill = 'red')
    

def drawBoard(canvas,data):
    myhand = data.players[0].gethand()
    for i in range(len(myhand)): 
        # my hand
        card = myhand[i]
        drawCard(canvas, card[0],card[1],(i+1)*105, 600)
    for card in data.players[0].hold:
        drawCard(canvas, card[0], card[1], (10 + 1)*105, 600, 'red')
        
        
        
    theirhand = data.players[1].gethand()
    for i in range(len(theirhand)):
        # their hand 
        if(data.showall == False):
            drawCard(canvas, 0,0,(i + 1)*105, 100)
        else:
            card = theirhand[i]
            drawCard(canvas, card[0],card[1],(i+1)*105, 100)
            
    # faceup pile
    up = data.game.discarddeck.peek()
    drawCard(canvas, up[0], up[1] , 400, 400)
    
    #facedown pile
    drawCard(canvas, 0,0,800,400)
    
    #Knock Button
    canvas.create_rectangle(300, 340, 350, 460, fill = 'red')
    canvas.create_rectangle(310, 360,340, 440, fill = 'orange' )
    canvas.create_text(325, 400, text = 'Knock', angle = 90, font = 'arial 16 bold')
    
    #logger

    
    #last turn
    canvas.create_text(1000, 300, text = "Opponent's 'Last Turn: ", font = 'Arial 14 bold')
    if(data.log[0] != -1):
        canvas.create_text(1000, 330, text = translateLog(data), font = 'Arial 14')
    
    #checkbutton for show all cards
    canvas.create_rectangle(50, 200, 75, 225, fill = 'beige')
    canvas.create_text(80,212, text = 'Show all cards', font = 'arial 14', anchor=W)
    if(data.showall == True):
        canvas.create_text(65,212, text = '✓', fill = 'green', font = 'arial 18')
        
        
    
def drawDirections(canvas, data):
    # create text for turn instructions
    if(data.mode == 'p1start'):
        text = 'Your turn now; Click the faceup card to draw, or facedown deck to pass'
    
    elif(data.mode == 'p2start'):
        text = 'Player 2 is choosing...'
        
    elif(data.mode == 'p1draw'):
        text = 'Click the deck that you want to draw from'
    
    elif(data.mode == 'p2draw'):
        text = 'Player 2 drawing now...'
    
    elif(data.mode == 'p1discard'):
        text = 'Click the card that you want to discard'
        
    elif(data.mode == 'p2discard'):
        text = 'Player 2 discarding now...'
        
    elif(data.mode == 'null'):
        text = 'null flag'
    
    
    
    else:
        text = 'You should not be seeing this!'
        
    canvas.create_text(50,300, anchor = W, text = text, font = 'Arial 14 bold')
    
def drawWin(canvas, data):
    for card in data.cardmenulist:
        drawCard(canvas, card[0], card[1], card[3], card[4])
    txt = f'{data.winner[0]} is the winner with a score of {data.winner[1]}!!!'
    canvas.create_text(data.width//2, data.height//2 , text = txt,
                       font="Arial 33 bold", fill = 'blue')

############################################################################
# MOUSE FUNCTIONS
def mouseMenu(event, data):
    x,y= event.x, event.y
    # Test

    
    if(y > data.height//2- 30  and y <  data.height//2 + 30 ):
        if(x > data.width//2 - 100- 50 and x < data.width//2 - 100 + 50  ):
            data.diff = 0
        elif( x > data.width//2 + 100- 60  and x < data.width//2 + 100 +  60  ):
            data.diff = 1
    
    
    if(x >data.width//2 - 190 and x <data.width//2 + 190 ):
        if(y >data.height//2 + 60 and y <data.height//2 + 180):
            #########_Start a game_##########
            if(data.diff == 0):
                p2 = agents.randombot('Computer')
            elif(data.diff == 1):
                p2 = agents.qlearner(data.models, 'Computer')
            data.players = [agents.human(), p2]
            
            data.game = game.Game(data.players[0], data.players[1], output = 'False')
            #print(data.game.start, data.game.start.identify())
            data.game.discarddeck.add(data.game.maindeck.deal())
            
            if(data.game.start.identify() == True):
                # Human player start
                data.mode = 'p1start'
            
            elif(data.game.start.identify() == False):
                 #computer player start
                 data.mode = 'p2start'
                 
            else:
                data.mode = 'null'
                
                
            data.disp = 'board'


def drawcheck(event, data):
    #checks mouse move and makes sure agent is only called if within proper bounds
    #It will execute the move, and set the mode to the proper following state
    x,y = event.x, event.y
    if(x > 360 and x < 440):#faceup file
        if(y > 340 and y < 460):
            if(data.mode == 'p1start'):
                data.game.dealphase(data.players[0], 1)
                data.mode = 'p1discard'

            
            elif(data.mode == 'p1draw'):
                data.game.playTurn(data.players[0], 1)
                data.mode = 'p1discard'
    
    if(x > 760 and x < 840):#facedown/pass
        if(y > 340 and y < 460):
            if(data.mode == 'p1start'):
                dealmove = data.game.dealphase(data.players[0], 2)
                #have global check to see if pass has been made to determin move
                #FOLLOWING IS TEMPORARY 
                #TODO: FIX
                if(dealmove == 0): # draw
                    data.mode = 'p1discard'
                
                elif(dealmove == 1): # pass
                    if(data.startpass == True):
                        data.startpass = False
                        data.mode = 'p2start'
                        otherStart( data)
                    else:
                        data.mode = 'p2draw'
                        otherDraw(data)
                    
                
            
            elif(data.mode == 'p1draw'):
                data.game.playTurn(data.players[0], 2)
                data.mode = 'p1discard'
                
def discardCheck(event, data):
    x,y = event.x, event.y
    zone = cardClicker(x,y)
    if(zone == 'k'):
        print('tried knocking')
        check = data.players[0].canknock()
        print(check)
        if(check == True):
            print('knock success')
            res = data.game.discard(data.players[0], zone)
            if(res == 1):
                win(data)
            
    elif(zone != -1):
        
        #print(zone, 'apple ap')
        #print(data.players[0].gethand())
        res = data.game.discard(data.players[0], zone)
        if(res == 1):
            win(data)
        else:
            data.mode = 'p2draw' 
            otherDraw(data)
        
        
        
def mouseButtons(event, data): #checks/unchecks buttons on main board
# 50, 200, 75, 225
    x,y = event.x, event.y
    if(y > 200 and y < 225):
        if(x > 50 and x < 75):
            data.showall = not (data.showall)
            
            
####OTher Player Functions#################################

def otherStart(data):
    #sleep(5)
    move = data.game.dealphase(data.players[1])
    if(move == 0): # draw
        #sleep(5)
        discmove = data.game.discard(data.players[1]) 
        if(discmove == 1):
            win( data)
        else:
            data.mode = 'p1start'
        #data.log = data.game.log
    
    elif(move == 1):# pass
        if(data.startpass == True):
            data.startpass = False
            data.mode = 'p1start'
        else:
            data.mode = 'p1draw'
        
        
def otherDraw(data):
    data.game.playTurn(data.players[1])
    sleep(2)
    discmove = data.game.discard(data.players[1])
    if(discmove == 1):
        win(data)
    
    else:
        data.mode = 'p1draw'
    data.log = data.game.log
###################################################################    

def win( data):
    data.disp = 'win'
    points = data.game.getwinner()
    if(points > 0):
        winner = [data.players[0], points]
    else:
        winner = [data.players[1], -points]
    data.winner = winner
    print('asshole')
    
    
    
    
    
############################################################################
def mousePressed(event, data):
    if(data.disp == 'menu'):
        mouseMenu(event, data)
            
    if(data.disp == 'board'):
        mouseButtons(event, data)
        if(data.mode == 'p1start' or data.mode == 'p1draw'):
            #print('drawcheck')
            drawcheck(event, data)
            #print(data.mode)
        if(data.mode == 'p1discard'):
            #print('runningdisccheckrn')
            discardCheck(event, data)
    
       

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
    if(data.disp in ['menu', 'win']):
        draw = rand.randint(10)
        if (draw == 2):
            #items will take form [suit, value, speed, xloc, yloc]
            data.cardmenulist.append([rand.randint(1,5), rand.randint(1,14),
                                      rand.randint(5,22), rand.randint(100,1200), 0])
        for carditem in data.cardmenulist:
            carditem[4]+= carditem[2]
            if(carditem[4] >= 1500):
                data.cardmenulist.remove(carditem)
            
            
    pass

def redrawAll(canvas, data):
    canvas.create_rectangle(0,0,1300,800,fill = 'light blue')
    if(data.disp == 'menu'):
        drawMenu(canvas, data)
    if(data.disp == 'board'):
        drawBoard(canvas, data)
        drawDirections(canvas, data)
    if(data.disp == 'win'):
        drawWin(canvas, data)
        

##############
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        #print('mpwrapper')
        mousePressed(event, data)
        
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1300, 800)