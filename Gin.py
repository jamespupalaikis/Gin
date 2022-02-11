# events-example0.py
# Barebones timer, mouse, and keyboard events
import Cards as c
from tkinter import *
import numpy.random as rand

####################################
# customize these functions
####################################

def init(data):
    # load data.xyz as appropriate
    data.ass = 0
    
    data.s, data.v = rand.randint(1,5),rand.randint(1,14)
    
    data.disp = 'menu'
    # what to display
    
    data.log = '' 
    # display the last turn made
    
    data.cardmenulist = [[rand.randint(1,5), rand.randint(1,14), rand.randint(5,22), rand.randint(100,1200), 0] ] 
    # cards falling in the menu
    
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
def drawCard(canvas, suit, value, x,y):
    #card size will be 70*120, centered at x,y
    #as usual suit 1-4, value 1-13
    canvas.create_rectangle(x-40, y-60, x+40, y + 60, width = 2, fill = 'white')
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
    
    if(y <655 and y > 545 ):
        zone = x // 105
        if(zone > 10):
            return -1
        return zone
    
    
    return -1

###############DRAWING########################################################
def drawMenu(canvas, data):
    #canvas.create_rectangle()
    for card in data.cardmenulist:
        drawCard(canvas, card[0], card[1], card[3], card[4])
    
    canvas.create_rectangle(data.width//2 - 190, data.height//2 - 60, data.width//2 + 190, data.height//2 + 60, fill = 'yellow')
    canvas.create_text(data.width//2, data.height//2 - 220, text = 'Gin Rummy',font="Arial 80 bold", fill = 'green')
    canvas.create_text(data.width//2, data.height//2 - 120, text = 'By James Pupalaikis',font="Arial 33 bold", fill = 'blue')
    canvas.create_text(data.width//2, data.height//2, text = 'Play Now',font="Arial 55 bold", fill = 'red')
    

def drawBoard(canvas,data):
    for i in range(1,12):
        # my hand
        drawCard(canvas, i%4 + 1,i,i*105, 600)
        
    for i in range(1,12):
        # their hand 
        drawCard(canvas, 0,0,i*105, 100)
    
    # faceup pile
    drawCard(canvas,data.s, data.v , 400, 400)
    
    #facedown pile
    drawCard(canvas, 0,0,800,400)
    
    #logger
    canvas.create_text(200,200,text=data.ass)
    
    #last turn
    canvas.create_text(1000, 300, text = 'Last Turn: ', font = 'Arial 21 bold')

############################################################################

def mousePressed(event, data):
    if(data.disp == 'menu'):
        if(event.x >data.width//2 - 190 and event.x <data.width//2 + 190 ):
            if(event.y >data.height//2 - 60 and event.y <data.height//2 + 60):
                data.disp = 'board'
    data.ass = cardClicker(event.x - 52, event.y)
    
    
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
    if(data.disp == 'menu'):
        draw = rand.randint(10)
        if (draw == 2):
            #items will take form [suit, value, speed, xloc, yloc]
            data.cardmenulist.append([rand.randint(1,5), rand.randint(1,14), rand.randint(5,22), rand.randint(100,1200), 0])
        for carditem in data.cardmenulist:
            carditem[4]+= carditem[2]
            if(carditem[4] >= 1500):
                data.cardmenulist.remove(carditem)
            
            
    pass

def redrawAll(canvas, data):
    canvas.create_rectangle(0,0,1300,800,fill = 'light blue')
    if(data.disp == 'menu'):
        drawMenu(canvas, data)
    if(data.disp != 'menu'):
        drawBoard(canvas, data)

##############
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
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