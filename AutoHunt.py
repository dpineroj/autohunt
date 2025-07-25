#Name: David Pinero-Jacome
#Andrew ID: dpineroj
#Section: D, Summer 2025
#Term Project: AutoHunt - Word Hunt Checker and Visualizer
#24.8.25


from cmu_graphics import *

def onAppStart(app):
    app.rows, app.cols = 4, 4
    app.cellSize = 100
    app.gridLeft = 50
    app.gridTop = 50
    app.grid = [['' for _ in range(app.cols)] for _ in range(app.rows)]
    app.currentCell = 0
    app.gridSize = app.rows * app.cols

def drawGrid(app):
    for row in range(app.rows):
        for col in range(app.cols):
            x = app.gridLeft + col * app.cellSize
            y = app.gridTop + row * app.cellSize
            drawRect(x, y, app.cellSize, app.cellSize, fill = None, 
                     border = 'black', borderWidth = 2)
            letter = app.grid[row][col]
            if letter:
                drawLabel(letter, x + app.cellSize / 2, y + app.cellSize / 2,
                          size = 36, bold = True)

def onKeyPress(app, key):
    if key == 'backspace' and app.currentCell > 0:
        app.currentCell -= 1
        row = app.currentCell // app.cols
        col = app.currentCell % app.cols
        app.grid[row][col] = ''

    if len(key) == 1 and key.isalpha() and app.currentCell < app.gridSize:
        row = app.currentCell // app.cols
        col = app.currentCell % app.cols
        app.grid[row][col] = key.upper()
        app.currentCell += 1


def redrawAll(app):
    drawLabel("Auto Hunt Beta", app.width // 2, 20, size = 20)
    drawGrid(app)

runApp(width = 500, height = 500)




