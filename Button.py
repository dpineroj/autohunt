from cmu_graphics import *


class Button:
    def __init__(self, x, y, w, h, color, fun):
        self.x = x
        self. y= y
        self. w = w
        self.h = h
        self.color = color
        self.fun = fun

    def respondToPress(self, app, mx, my):
        if self.isPressed(mx, my):
            self.fun(app)

    def isPressed(self, mx, my):
        left = self.x
        top = self.y
        right = left + self.w
        bottom = top + self.h
        return left <= mx <= right and top <= my <= bottom

    def draw(self):
        drawRect(self.x, self.y, self.w, self.h, fill = self.color)

def onAppStart(app):
    app.buttonList = [Button(200, 200, 150, 150, 'red', startFunction)]
    

def onMousePress(app, mx, my):
    for button in app.buttonList:
        button.respondToPress(app, mx, my)


def startFunction(app):
    for button in app.buttonList:
        button.color = 'purple'


def redrawAll(app):
    for i in range(len(app.buttonList)):
        app.buttonList[i].draw()




runApp(width = 600, height = 600)