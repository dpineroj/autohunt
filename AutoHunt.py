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
    app.validWords = []
    app.currentWordIndex = 0
    app.wordStep = 0
    app.segmentDelaySteps = 0
    app.wordDelaySteps = 0

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
                print('all letters entered')
                app.mode = 'preCountdown' #time buffer before countdown

def onStep(app):
    print(f"mode = {app.mode}")
    if app.mode == 'preCountdown': #delay 0.5s befire countdown
        app.preCountdownSteps += 1
        if app.preCountdownSteps >= 5:
            app.mode = 'countdown'
            app.stepsPerSecond = 1 
    elif app.mode == 'countdown':
        app.countdown -= 1
        print(f"countdown now: {app.countdown}")
        if app.countdown == 0:
            print("countdown complete")
            findAllWords(app)
            print("valid words and paths")
            for word, path in app.validWords:
                print(f"{word}: {path}")
            app.mode = 'animate'
            print(f"Found {len(app.validWords)} words")
            app.stepsPerSecond = 2 #0.5s per step
    if app.mode == 'animate':
        print(f"IN ANIMATE MODE - index: {app.currentWordIndex}, total: {len(app.validWords)}")
        if app.currentWordIndex >= len(app.validWords):
            print('no more words - switching to done mode')
            app.mode = 'done'
            return
        
        word, path = app.validWords[app.currentWordIndex]

        if app.wordStep < len(path) - 1:
            app.segmentDelaySteps += 1
            if app.segmentDelaySteps >= 1:
                app.wordStep += 1
                app.segmentDelaySteps = 0
        else:
            app.wordDelaySteps += 1
            if app.wordDelaySteps >= 2:
                app.currentWordIndex += 1
                app.wordStep = 0
                app.wordDelaySteps = 0
                app.segmentDelaySteps = 0



#convert linear index to (row, col) coordinates
def getGridPosition(app, index):
    return index // app.cols, index % app.cols

def redrawAll(app):
    drawLabel(f"mode: {app.mode}", 250, 480)
    drawLabel("Auto Hunt Beta", app.width // 2, 20, size = 20)
    drawGrid(app)

    if app.mode == 'countdown':
        drawLabel(app.countdown, app.width // 2, app.height // 1.05, 
                  size = 24)

    if app.mode == 'animate' and app.currentWordIndex < len(app.validWords):
        word, path = app.validWords[app.currentWordIndex]
        drawWordPath(app, path, app.wordStep)

def drawWordPath(app, path, step):
    print(f"drawing word step {step} of path {path}")
    for i in range(step):
        if i < len(path) - 1:
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            x1 = app.gridLeft + c1 * app.cellSize + app.cellSize // 2
            y1 = app.gridTop + r1 * app.cellSize + app.cellSize // 2
            x2 = app.gridLeft + c2 * app.cellSize + app.cellSize // 2
            y2 = app.gridTop + r2 * app.cellSize + app.cellSize // 2
            print(f"drawing line from {path[i]} to {path[i + 1]}")
            drawLine(x1, y1, x2, y2, fill = 'red', lineWidth = 4)

def findAllWords(app):
    app.validWords = []
    seenWords = set()
    for row in range(app.rows):
        for col in range(app.cols):
            visited = set()
            backtrack(app, row, col, '', [], visited, seenWords)
    print(f"done search: {len(app.validWords)} valid words found ")

def backtrack(app, row, col, wordsSoFar, path, visited, seenWords):
    if not (0 <= row < app.rows and 0 <= col < app.cols):
        return
    if (row, col) in visited:
        return
    
    letter = app.grid[row][col]
    if not letter:
        return
    wordsSoFar += letter
    path.append((row, col))
    visited.add((row, col))

    if len(wordsSoFar) > 1 and wordsSoFar in app.wordSet:
        if wordsSoFar not in seenWords:
            app.validWords.append((wordsSoFar, path.copy()))
            seenWords.add(wordsSoFar)
    
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if not (dr == 0 and dc == 0):
                backtrack(app, row + dr, col + dc, wordsSoFar, path, visited, seenWords)
    
    path.pop()
    visited.remove((row, col))


runApp(width = 500, height = 500)




