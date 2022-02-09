# events-example0.py
# Barebones timer, mouse, and keyboard events
import Cards as c
from tkinter import *

####################################
# customize these functions
####################################

def init(data):
    # load data.xyz as appropriate
    
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
    canvas.create_rectangle(x-40, y-60, x+40, y + 60, width = 2)
    if(suit == 0 and value == 0):
    #this will represent a card back instead (don't feel like writing a new fn)
        canvas.create_rectangle(x-35, y-55, x+35, y + 55, width = 8, outline = 'red', fill = 'light blue')
        canvas.create_text(x,y,text = 'fuck you fuck you', angle = 45)
    
    else:
        drawsuit(canvas, suit, x,y)
        canvas.create_text(x - 30, y - 50, text = c.carddict[value])
        canvas.create_text(x + 30, y + 50, text = c.carddict[value])
    








##############################################################################

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
    pass

def redrawAll(canvas, data):
    
    
    for i in range(1,12):
        drawCard(canvas, i%4 + 1,i,i*105, 600)
    drawCard(canvas, 0,0, 400, 400)
    pass


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