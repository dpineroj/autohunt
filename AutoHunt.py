#David Pinero-Jacome (dpineroj)
#24.7.25
from cmu_graphics import *

def onAppStart(app):
    app.rows, app.cols = 4, 4
    app.cellSize = 100
    app.gridLeft = 50
    app.gridTop = 50
    app.grid = [['' for _ in range(app.cols)] for _ in range(app.rows)]

def drawGrid(app):
    for row in range(app.rows):
        for col in range(app.cols):
            x = app.gridLeft + col * app.cellSize
            y = app.gridTop + row * app.cellSize
            drawRect(x, y, app.cellSize, app.cellSize, fill=None, border='black', borderWidth=2)

def redrawAll(app):
    drawLabel("Auto Hunt Beta", app.width//2, 20, size=20)
    drawGrid(app)

runApp(width=500, height=500)






cmu_graphics.run()
