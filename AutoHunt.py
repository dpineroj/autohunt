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
    #create 4x4 empty letter grid
    app.grid = [['' for _ in range(app.cols)] for _ in range(app.rows)]
    app.currentCell = 0
    app.gridSize = app.rows * app.cols
    app.mode = 'input'

    app.stepsPerSecond = 10
    app.preCountdownSteps = 0 #time buffer
    app.countdown = 3 #before word visualization starts

    #temp word set to test with
    app.wordSet = {'CAR', 'CARD', 'CARS', 'SCAR', 'ARC', 'RACE', 'ACE', 'CASE'}



def drawGrid(app):
    for row in range(app.rows):
        for col in range(app.cols):
            x = app.gridLeft + col * app.cellSize
            y = app.gridTop + row * app.cellSize
            #draw cell border
            drawRect(x, y, app.cellSize, app.cellSize, fill = None, 
                     border = 'black', borderWidth = 2)
            
            letter = app.grid[row][col] #draw letter if cell is filled
            if letter:
                drawLabel(letter, x + app.cellSize / 2, y + app.cellSize / 2,
                          size = 36, bold = True)

def onKeyPress(app, key):
    if app.mode == 'input':
        if key == 'backspace' and app.currentCell > 0:
            app.currentCell -= 1
            row, col = getGridPosition(app, app.currentCell)
            app.grid[row][col] = ''

        elif len(key) == 1 and key.isalpha() and app.currentCell < app.gridSize:
            row, col = getGridPosition(app, app.currentCell)
            app.grid[row][col] = key.upper()
            app.currentCell += 1

            if app.currentCell == app.gridSize:
                app.mode = 'preCountdown' #time buffer before countdown

def onStep(app):
    if app.mode == 'preCountdown': #delay 0.5s befire countdown
        app.preCountdownSteps += 1
        if app.preCountdownSteps >= 5:
            app.mode = 'countdown'
            app.stepsPerSecond = 1 
    elif app.mode == 'countdown':
        app.countdown -= 1
        if app.countdown == 0:
            findAllWords(app)
            app.mode = 'animate'


#convert linear index to (row, col) coordinates
def getGridPosition(app, index):
    return index // app.cols, index % app.cols

def redrawAll(app):
    drawLabel("Auto Hunt Beta", app.width // 2, 20, size = 20)
    drawGrid(app)

    if app.mode == 'countdown':
        drawLabel(app.countdown, app.width // 2, app.height // 1.05, 
                  size = 24)

def findAllWords(app):
    app.validWords = []
    for row in range(app.rows):
        for col in range(app.cols):
            visited = set()
            backtrack(app, row, col, '', visited)

def backtrack(app, row, col, path, visited):
    if not (0 <= row < app.rows and 0 <= col < app.cols):
        return
    if (row, col) in visited:
        return

    path += app.grid[row][col]
    visited = visited | {(row, col)}
    if len(path) > 1 and path in app.wordSet:
        app.validWords.append((path, visited | {(row, col)})) 

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr != 0 or dc != 0:
                backtrack(app, row + dr, col + dc, path, visited)

runApp(width = 500, height = 500)




