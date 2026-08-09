from cmu_graphics import *
from PIL import Image  
import random, string

def onAppStart(app):
    #-------------------------#
    # General Grid Setup
    #-------------------------#
    app.rows, app.cols = 4, 4
    app.gridMargin = 50
    app.cellSpacing = 8
    app.cellSize = min((app.width - 2 * app.gridMargin) // app.cols,
                       (app.height - 200) // app.rows)
    app.gridLeft = (app.width - app.cellSize * app.cols) // 2
    app.gridTop = 100
    app.gridSize = app.rows * app.cols
    app.grid = [['' for _ in range(app.cols)] for _ in range(app.rows)]
    app.currentCell = 0

    #-------------------------#
    # App Mode & Speed
    #-------------------------#
    app.mode = 'input'
    app.stepsPerSecond = 10
    app.preCountdownSteps = 0  # time buffer before animation
    app.countdown = 3          # before word visualization starts

    #-------------------------#
    # Load Word Tree
    #-------------------------#
    wordList = loadWords('words.txt')  # text file from:
    #https://boardgames.stackexchange.com/questions/38366/latest-collins-scrabble-words-list-in-text-file
    app.treeRoot = buildTree(wordList)
    app.validWordGroups = []  # groups of longest-to-shortest words by path
    app.validWords = []       # flat list of words in animation order
    app.currentWordIndex = 0
    app.wordStep = 0
    app.segmentDelaySteps = 0
    app.wordDelaySteps = 0

    #-------------------------#
    # Images
    #-------------------------#
    
    app.tile = CMUImage(Image.open('wooden-tile.png')) #resource doc

    #-------------------------#
    # Mini Grid (Start Screen)
    #-------------------------#
    app.miniGrid = generateRandomGrid(4, 4)
    app.miniCellSize = app.cellSize * 0.5
    app.miniGridTop = app.height * 0.38
    app.miniGridLeft = (app.width - 
                        (app.miniCellSize * 4 + 3 * app.cellSpacing)) / 2
    app.miniWordIndex = 0
    app.miniWordPath = []
    app.miniValidWords = []

    #-------------------------#
    # Arrow Button Setup
    #-------------------------#
    app.arrowButtonSize = app.miniCellSize * 0.8
    arrowSpacing = app.arrowButtonSize * 3
    centerX = app.width / 2
    app.arrowY = app.miniGridTop - app.arrowButtonSize * 1.2
    leftX = centerX - arrowSpacing / 2 - app.arrowButtonSize / 2
    rightX = centerX + arrowSpacing / 2 - app.arrowButtonSize / 2
    app.leftArrow = Button(leftX, app.arrowY, app.arrowButtonSize, 
                           app.arrowButtonSize, fill = None, 
                           fun = handleLeftArrow)
    app.rightArrow = Button(rightX, app.arrowY, app.arrowButtonSize, 
                            app.arrowButtonSize, fill = None, 
                            fun = handleRightArrow) #28.7.25 lecture

    #-------------------------#
    # Mini Word Animation
    #-------------------------#
    app.miniStep = 0
    app.miniSegmentDelaySteps = 0
    app.animateMiniWord = True

    #-------------------------#
    # Game Info & Game Over
    #-------------------------#
    app.wordsFound = 0
    app.timeLeft = 60
    app.timerActive = False
    app.gameOver = False
    app.infoBarY = 10
    app.mainMenuButton = Button(0, 0, 0, 0, fill = 'gainsboro', 
                                fun = goToMainMenu)
    app.newBoardButton = Button(0, 0, 0, 0, fill = 'lightGreen', 
                                fun = restartGame)

    #-------------------------#
    # Dynamic Resizing + Mini Word Search Setup 
    #-------------------------#
    game_onResize(app)
    findWordsForMiniGrid(app)
    start_onResize(app)
    resizeMiniComponents(app)

def startFunction(app):
    setActiveScreen('game')

def setBackground(app):
    #always load full-size background image (1920x1080)
    fullBG = Image.open('pattern-tiled-1920x1080.jpg').convert('RGB')
    #had issues loading image, learned method: 
    #https://www.geeksforgeeks.org/python/python-pil-image-convert-method/ 

    #crop box centered around the window
    bgWidth, bgHeight = fullBG.size
    cropWidth, cropHeight = app.width, app.height

    #bounds
    cropWidth = min(cropWidth, bgWidth)
    cropHeight = min(cropHeight, bgHeight)

    left = (bgWidth - cropWidth) // 2
    top = (bgHeight - cropHeight) // 2
    right = left + cropWidth
    bottom = top + cropHeight
    #https://www.geeksforgeeks.org/python/python-pil-image-crop-method/
    cropped = fullBG.crop((left, top, right, bottom))
    app.AutoHuntBG = CMUImage(cropped)

#AI helped with logic to resize start screen so it fits any window (X)
def resizeMiniComponents(app):
    # ==== Mini grid sizing ====
    maxCellSizeW = app.width * 0.08
    maxCellSizeH = app.height * 0.08
    app.miniCellSize = min(maxCellSizeW, maxCellSizeH)

    app.cellSpacing = app.miniCellSize * 0.15  # spacing tied to cell size

    totalGridWidth = 4 * app.miniCellSize + 3 * app.cellSpacing
    app.miniGridLeft = (app.width - totalGridWidth) / 2
    app.miniGridTop = app.height * 0.38  

    # ==== Arrow buttons ====
    app.arrowButtonSize = app.miniCellSize * 0.7
    arrowSpacing = app.arrowButtonSize * 3.5  # distance between centers

    centerX = app.width / 2

    arrowY = app.miniGridTop - app.arrowButtonSize * 1.45

    #everything below is AI
    app.leftArrow.x = centerX - arrowSpacing / 2 - app.arrowButtonSize / 2
    app.leftArrow.y = arrowY 
    app.leftArrow.w = app.arrowButtonSize
    app.leftArrow.h = app.arrowButtonSize

    app.rightArrow.x = centerX + arrowSpacing / 2 - app.arrowButtonSize / 2
    app.rightArrow.y = arrowY
    app.rightArrow.w = app.arrowButtonSize
    app.rightArrow.h = app.arrowButtonSize

    # ==== Word display Box ====
    app.wordBoxW = app.arrowButtonSize * 2.4
    app.wordBoxH = app.arrowButtonSize * 0.8
    app.wordBoxX = (app.width - app.wordBoxW) / 2
    app.wordBoxY = app.miniGridTop - app.arrowButtonSize * 1.4 


def start_onResize(app):
    setBackground(app)
    app.buttonW = app.width * 0.3
    app.buttonH = app.height * 0.07
    app.buttonX = (app.width - app.buttonW) / 2
    app.buttonY = app.height * 0.85
    app.automateButton = Button(app.buttonX, app.buttonY,
                                app.buttonW, app.buttonH,
                                fill = 'goldenrod', fun =startFunction)
    resizeMiniComponents(app)

def generateRandomGrid(rows, cols):
    return [[random.choice(string.ascii_uppercase) for _ in range(cols)] \
             for _ in range(rows)]


def game_onResize(app):
    app.cellSize = min((app.width - 2 * app.gridMargin) // app.cols,
                        (app.height - 200) // app.rows)
    app.gridLeft = (app.width - app.cellSize * app.cols) // 2

    buttonW = app.width * 0.25
    buttonH = app.height * 0.06
    spacing = app.height * 0.02

    # Button logic for game over
    app.mainMenuButton.x = (app.width - buttonW) / 2
    app.mainMenuButton.y = app.height / 2 + 50
    app.mainMenuButton.w = buttonW
    app.mainMenuButton.h = buttonH

    app.newBoardButton.x = app.mainMenuButton.x
    app.newBoardButton.y = app.mainMenuButton.y + buttonH + spacing
    app.newBoardButton.w = buttonW
    app.newBoardButton.h = buttonH

    setBackground(app)


#https://stackoverflow.com/questions/30969687/use-python-to-open-a-file-in-read-mode
def loadWords(path): #learned how to open text file from ^^^^
    with open(path, 'r') as f:
        words = [line.strip().upper() for line in f if len(line.strip()) > 2 \
                 and line.strip().isalpha()]
    return words

def drawRoundedGridBackground(left, top, rows, cols, cellSize, spacing, 
                               radius = 20, fillColor = rgb(68, 87, 59), 
                               borderColor = 'lightGreen', borderWidth = 4):
    # Total grid dimensions 
    gridWidth = cols * cellSize + (cols - 1) * spacing
    gridHeight = rows * cellSize + (rows - 1) * spacing

    # Outer background bounds 
    bgLeft = left - spacing - borderWidth
    bgTop = top - spacing - borderWidth
    bgWidth = gridWidth + 2 * spacing + 2 * borderWidth
    bgHeight = gridHeight + 2 * spacing + 2 * borderWidth

    outerRadius = radius + borderWidth

    # === Draw Border Layer ===
    drawRect(bgLeft + outerRadius, bgTop, bgWidth - 2 * outerRadius, 
             bgHeight, fill = borderColor)
    drawRect(bgLeft, bgTop + outerRadius, bgWidth, 
             bgHeight - 2 * outerRadius, fill = borderColor)

    drawCircle(bgLeft + outerRadius, bgTop + outerRadius, outerRadius, 
               fill = borderColor)
    drawCircle(bgLeft + bgWidth - outerRadius, bgTop + outerRadius, 
               outerRadius, fill = borderColor)
    drawCircle(bgLeft + outerRadius, bgTop + bgHeight - outerRadius, 
               outerRadius, fill = borderColor)
    drawCircle(bgLeft + bgWidth - outerRadius, bgTop + bgHeight - outerRadius, 
               outerRadius, fill = borderColor)

    # === Draw Inner Grid Background ===
    innerLeft = bgLeft + borderWidth
    innerTop = bgTop + borderWidth
    innerWidth = bgWidth - 2 * borderWidth
    innerHeight = bgHeight - 2 * borderWidth

    drawRect(innerLeft + radius, innerTop, innerWidth - 2 * radius, 
             innerHeight, fill = fillColor)
    drawRect(innerLeft, innerTop + radius, innerWidth, 
             innerHeight - 2 * radius, fill = fillColor)

    drawCircle(innerLeft + radius, innerTop + radius, 
               radius, fill = fillColor)
    drawCircle(innerLeft + innerWidth - radius, innerTop + radius, 
               radius, fill = fillColor)
    drawCircle(innerLeft + radius, innerTop + innerHeight - radius, 
               radius, fill = fillColor)
    drawCircle(innerLeft + innerWidth - radius, 
               innerTop + innerHeight - radius, radius, fill = fillColor)


def drawGrid(app):
    drawRoundedGridBackground(app.gridLeft, app.gridTop,
                          app.rows, app.cols,
                          app.cellSize, app.cellSpacing)
    for row in range(app.rows):
        for col in range(app.cols):
            x = app.gridLeft + col * (app.cellSize + app.cellSpacing)
            y = app.gridTop + row * (app.cellSize + app.cellSpacing)
            drawRect(x, y, app.cellSize, app.cellSize, 
                     fill = 'darkOliveGreen', border = None)
            drawImage(app.tile, x, y, width = app.cellSize,
                       height = app.cellSize)

            letter = app.grid[row][col] #draw letter if cell is filled
            if letter:
                size = int(app.cellSize * 0.4)
                drawLabel(letter, x + app.cellSize / 2, y + app.cellSize / 2,
                          size = size, bold = True)

def start_redrawAll(app):
    drawImage(app.AutoHuntBG, 0, 0) #background image

    titleSize = int(app.height * 0.1)
    subtitleSize = int(app.height * 0.025)

    drawLabel('AUTOHUNT', app.width // 2, app.height * 0.15,
              size = titleSize, font = 'monospace', 
              bold = True, fill = rgb(34, 61, 36))

    drawLabel('complete the grid to hunt all possible words', 
              app.width // 2, app.height * 0.22, 
              size = subtitleSize, fill = rgb(34, 61, 36))


    drawRect(0, app.height * 0.95, app.width, app.height, 
             fill = rgb(50, 50, 50))
    size = app.height * 0.08
    drawLabel("LET'S PLAY WORD HUNT!", app.width // 2, app. height * 0.97, 
              size = int(size * 0.3), fill = 'gainsboro', bold = True)
    
    drawMiniGrid(app)
    app.automateButton.draw()
    drawMiniWordPath(app)
    drawMiniWordDisplay(app)
    app.leftArrow.draw() 
    app.rightArrow.draw() 

def drawMiniWordDisplay(app):
    if app.miniWordIndex < len(app.miniValidWords):
        word, _ = app.miniValidWords[app.miniWordIndex]
        x = app.wordBoxX
        y = app.wordBoxY
        w = app.wordBoxW
        h = app.wordBoxH
        r = h / 2  # rounded radius

        drawRect(x + r, y, w - 2 * r, h, fill = 'lightGreen')
        drawCircle(x + r, y + h / 2, r, fill = 'lightGreen')
        drawCircle(x + w - r, y + h / 2, r, fill = 'lightGreen')

        drawLabel(word, x + w / 2, y + h / 2,
                  size = int(h * 0.4), fill = 'black', font = 'arial', 
                  bold = True)


def drawMiniWordPath(app):
    if app.miniWordIndex < len(app.miniValidWords):
        _, path = app.miniValidWords[app.miniWordIndex]
        for i in range(min(app.miniStep, len(path) - 1)):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            x1 = app.miniGridLeft + c1 * (app.miniCellSize + app.cellSpacing) \
            + app.miniCellSize / 2
            y1 = app.miniGridTop + r1 * (app.miniCellSize + app.cellSpacing) \
            + app.miniCellSize / 2
            x2 = app.miniGridLeft + c2 * (app.miniCellSize + app.cellSpacing) \
            + app.miniCellSize / 2
            y2 = app.miniGridTop + r2 * (app.miniCellSize + app.cellSpacing) \
            + app.miniCellSize / 2
            drawLine(x1, y1, x2, y2, fill = 'red', lineWidth = 2)

    
def start_onMousePress(app, mx, my):
    app.automateButton.respondToPress(app, mx, my)
    app.leftArrow.respondToPress(app, mx, my)
    app.rightArrow.respondToPress(app, mx, my)

def game_onMousePress(app, mx, my):
    if app.mode == 'gameOver':
        app.mainMenuButton.respondToPress(app, mx, my)
        app.newBoardButton.respondToPress(app, mx, my)

def goToMainMenu(app):
    onAppStart(app)  #resets 
    setActiveScreen('start')  #go to start screen


def restartGame(app):
    onAppStart(app)
    setActiveScreen('game')

def handleRightArrow(app):
    if app.miniWordIndex < len(app.miniValidWords) - 1:
        app.miniWordIndex += 1
        app.miniStep = 0
        app.miniSegmentDelaySteps = 0
        app.animateMiniWord = True  # <--- START animating

def handleLeftArrow(app):
    if app.miniWordIndex > 0:
        app.miniWordIndex -= 1
        app.miniStep = 0
        app.miniSegmentDelaySteps = 0
        app.animateMiniWord = True 

def drawMiniGrid(app):
    drawRoundedGridBackground(app.miniGridLeft, app.miniGridTop,
                          app.rows, app.cols,
                          app.miniCellSize, app.cellSpacing,
                          radius = 10)
    for row in range(app.rows):
        for col in range(app.cols):
            x = app.miniGridLeft + col * (app.miniCellSize + app.cellSpacing)
            y = app.miniGridTop + row * (app.miniCellSize + app.cellSpacing)
            drawImage(app.tile, x, y, width = app.miniCellSize, 
                      height = app.miniCellSize)
            letter = app.miniGrid[row][col]
            if letter:
                size = int(app.miniCellSize * 0.4)
                drawLabel(letter, x + app.miniCellSize / 2, 
                          y + app.miniCellSize / 2,
                          size = size, bold = True)

def game_onKeyPress(app, key):
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
                app.mode = 'preCountdown' 

def start_onStep(app):
    if app.animateMiniWord and app.miniWordIndex < len(app.miniValidWords):
        _, path = app.miniValidWords[app.miniWordIndex]
        if app.miniStep < len(path) - 1:
            app.miniSegmentDelaySteps += 1
            if app.miniSegmentDelaySteps >= 1:
                app.miniStep += 1
                app.miniSegmentDelaySteps = 0

def game_onStep(app):
    if app.mode == 'preCountdown': #delay 0.5s befire countdown
        app.preCountdownSteps += 1
        if app.preCountdownSteps >= 5:
            app.mode = 'countdown'
            app.stepsPerSecond = 1 
    elif app.mode == 'countdown':
        app.countdown -= 1
        if app.countdown == 0:
            findAllWords(app)

            if len(app.validWords) == 0:
                app.mode = 'gameOver'
                app.timerActive = False
                return

            app.mode = 'animate'
            app.stepsPerSecond = 2  # 0.5s per step
            app.timerActive = True
            app.timerTicks = 0

    elif app.mode == 'animate':
         # Timer countdown
        if app.timerActive:
            app.timerTicks += 1
            if app.timerTicks % app.stepsPerSecond == 0:
                app.timeLeft -= 1
                if app.timeLeft <= 0:
                    app.mode = 'gameOver'
                    app.timerActive = False
                    return

        if app.currentWordIndex >= len(app.validWords):
            app.mode = 'gameOver'
            app.timerActive = False
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
                app.wordsFound += 1

#convert linear index to (row, col) coordinates
def getGridPosition(app, index):
    return index // app.cols, index % app.cols

def game_redrawAll(app):
    #backgrond image
    drawImage(app.AutoHuntBG, 0, 0)

    #info bar background
    barWidth = app.width * 0.3
    barHeight = 50
    barX = (app.width - barWidth) / 2
    barY = app.infoBarY
    drawRect(barX, barY, barWidth, barHeight, fill = 'white', border = None, 
             borderWidth = 2)
    
    # Dimensions setup for pretty display (rounded rectangle)
    pillWidth = barHeight * 1.2
    pillHeight = barHeight * 0.45
    pillX = barX - 5
    pillY = barY + (barHeight - pillHeight) / 2
    radius = pillHeight / 2  

    shrink = 10  # pixels to remove from the middle
    drawRect(pillX + radius + shrink / 2, pillY, 
             pillWidth - 2 * radius - shrink, 
             pillHeight, fill = 'goldenrod')


    nudge = -10 # adjust as needed 

    # Left cap
    drawOval(pillX + radius - nudge, pillY + radius, pillHeight, 
             pillHeight, fill = 'goldenrod')
    # Right cap
    drawOval(pillX + pillWidth - radius + nudge, pillY + radius, pillHeight, 
             pillHeight, fill ='goldenrod')
    drawLabel(f"WORDS:{app.wordsFound}", barX + barWidth * 0.28, 
              barY + barHeight / 2,
            size = 30, fill = 'black', align = 'left', bold = True,
            font = 'monospace')

    drawRect(0, app.height * 0.95, app.width, app.height, 
             fill = rgb(50, 50, 50))

    drawGrid(app)

        # === Timer background below info bar ===
    timerWidth = app.width * 0.05
    timerHeight = 25
    timerX = (app.width + barWidth) / 2 - timerWidth 
    timerY = barY + barHeight   

    drawRect(timerX, timerY, timerWidth, timerHeight, 
             fill = 'black', opacity = 30)

    
    minutes = app.timeLeft // 60
    seconds = app.timeLeft % 60
    timeText = f"{minutes}:{seconds:02}"

    drawLabel(timeText, timerX + timerWidth / 2, timerY + timerHeight / 2,
            size = 10, fill = 'white', bold = True, font = 'monospace')

    if app.mode == 'countdown':
        drawRect(0, 0, app.width, app.height, fill = 'black', 
                 opacity = 20)
        size = int(app.height * 0.2)
        drawLabel(str(app.countdown), app.width // 2, app.height // 2,
                  size = size, fill = 'white', bold = True, font = 'monospace')

    if app.mode == 'animate' and app.currentWordIndex < len(app.validWords):
        word, path = app.validWords[app.currentWordIndex]
        drawWordPath(app, path, app.wordStep)
        wordSize = int(app.height * 0.025) 
        drawLabel(f"{word}", app.width // 2,
                app.height * 0.97, 
                size = wordSize, fill = 'gainsboro', bold = True)
    
    if app.mode == 'gameOver':
        drawRect(0, 0, app.width, app.height, fill = 'black', opacity = 80)
        drawLabel("Words Hunted", app.width // 2, app.height // 2,
                  size = 40, fill = 'white', bold = True)

        # Draw Main Menu button
        drawRect(app.mainMenuButton.x, app.mainMenuButton.y,
                 app.mainMenuButton.w, app.mainMenuButton.h,
                 fill = app.mainMenuButton.fill, border = 'white', 
                 borderWidth = 2)
        drawLabel("main menu", app.mainMenuButton.x + app.mainMenuButton.w / 2,
                  app.mainMenuButton.y + app.mainMenuButton.h / 2,
                  size = 20, fill = 'black', bold = True)

        # Draw New Board button
        drawRect(app.newBoardButton.x, app.newBoardButton.y,
                 app.newBoardButton.w, app.newBoardButton.h,
                 fill = app.newBoardButton.fill, border = 'white',
                   borderWidth = 2)
        drawLabel("new board", app.newBoardButton.x + app.newBoardButton.w / 2,
                  app.newBoardButton.y + app.newBoardButton.h / 2,
                  size = 20, fill = 'black', bold = True)


#AI used to help fix lines not being centered when drawing path
def getGameCellCenter(app, row, col):
    x = app.gridLeft + col * (app.cellSize + app.cellSpacing) + app.cellSize / 2
    y = app.gridTop + row * (app.cellSize + app.cellSpacing) + app.cellSize / 2
    return x, y

def drawWordPath(app, path, step):
    for i in range(step):
        if i < len(path) - 1:
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            x1, y1 = getGameCellCenter(app, r1, c1)
            x2, y2 = getGameCellCenter(app, r2, c2)

            drawLine(x1, y1, x2, y2, fill = 'red', lineWidth = 4, 
                     opacity = 75)
    
def groupLongestWordLength(group):
    if len(group) == 0:
        return 0
    return len(group[0][0])

#help from AI to recycle backtrack function 
def findWordsForMiniGrid(app):
    validGroups = []
    foundWords = set()
    for row in range(app.rows):
        for col in range(app.cols):
            backtrack(app, row, col, app.treeRoot, [], set(), "",
                      app.miniGrid, validGroups, foundWords)

    for group in validGroups:
        group.sort(key = wordLength, reverse = True)

    validGroups = [g for g in validGroups if len(g) > 0]
    #https://docs.python.org/3/howto/sorting.html
    validGroups.sort(key = groupLongestWordLength, reverse = True)
    app.miniValidWords = [pair for g in validGroups for pair in g]

def findAllWords(app):
    #reset the word list and tracking sets
    app.validWords = []
    app.foundWords = set()
    app.validWordGroups = []

    #begin backtracking from each grid cell
    for row in range(app.rows):
        for col in range(app.cols):
            backtrack(app, row, col, app.treeRoot, [], set(), "",
                      app.grid, app.validWordGroups, app.foundWords)
    
    #sort each group by word length (longest to shortest)
    for group in app.validWordGroups:
        group.sort(key = wordLength, reverse = True)

    app.validWordGroups = [group for group in app.validWordGroups if len(group) > 0]
    app.validWordGroups.sort(key = groupLongestWordLength, reverse = True)
    app.validWords = [pair for group in app.validWordGroups for pair in group]

def wordLength(pair):
    return len(pair[0])

#the holy grail
def backtrack(app, row, col, node, path, visited, wordsSoFar, grid, 
              validGroups, foundWords):
    if not (0 <= row < app.rows and 0 <= col < app.cols): #check bounds
        return
    if (row, col) in visited:
        return
    
    letter = grid[row][col]
    if not letter or letter not in node.children:
        return
    
    #valid next letter found, continue down tree and path
    node = node.children[letter]
    wordsSoFar += letter
    path.append((row, col))
    visited.add((row, col))


    # add current full word if it's valid and not already found
    if node.isWord:
        # Remove from any previous group if already found
        for group in validGroups:
            group[:] = [pair for pair in group if pair[0] != wordsSoFar]

        # create a new group starting with this word
        validGroups.append([(wordsSoFar, path[:])])
        foundWords.add(wordsSoFar)

        # walk backward and check all shorter prefixes
        for i in range(len(path) - 1, 0, -1):
            prefixPath = path[:i]
            prefixWord = wordsSoFar[:i]
            prefixNode = app.treeRoot
            valid = True
            for letter in prefixWord:
                if letter in prefixNode.children:
                    prefixNode = prefixNode.children[letter]
                else:
                    valid = False
                    break
            if valid and prefixNode.isWord:
                # Remove prefix from earlier groups
                for group in validGroups[:-1]:
                    group[:] = [pair for pair in group if pair[0] != prefixWord]
                validGroups[-1].append((prefixWord, prefixPath))
                foundWords.add(prefixWord)
    #check all other directions
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if not (dr == 0 and dc == 0):
                backtrack(app, row + dr, col + dc, node, path, visited,
                          wordsSoFar, grid, validGroups, foundWords)
    #backtrack
    path.pop()
    visited.remove((row, col))

#button class derived from 28.7.25 lecture
class Button:
    def __init__(self, x, y, w, h, fill, fun):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.fill = fill
        self.fun = fun

    def respondToPress(self, app, mx, my):
        if self.isPressed(mx, my):
            self.fun(app)

    def isPressed(self, mx, my):
        return self.x <= mx <= self.x + self.w and \
        self.y <= my <= self.y + self.h

    def draw(self):
        #check if its left or right arrow button
        if self.fun in [handleLeftArrow, handleRightArrow]:
            cx = self.x + self.w / 2
            cy = self.y + self.h / 2
            #draw arrows
            arrow = '<' if self.fun == handleLeftArrow else '>'
            drawCircle(cx, cy, self.h * 0.3, fill = 'black', opacity = 30)
            drawLabel(arrow, cx, cy, size = int(self.h * 0.3), bold = True,
                    fill = 'white', font = 'monospace', opacity = 20)
        #chec if its automate button
        elif self.fun == startFunction:
            radius = min(self.h / 2, self.w / 2)
            if self.w < 2 * radius: #no draw if width too small
                return
            
            #rounded rectangle
            drawRect(self.x + radius, self.y, self.w - 2 * radius, 
                     self.h, fill = self.fill)
            drawCircle(self.x + radius, self.y + self.h / 2, radius, 
                       fill = self.fill)
            drawCircle(self.x + self.w - radius, self.y + self.h / 2, radius, 
                       fill = self.fill)
            drawLabel('automate', self.x + self.w / 2, self.y + self.h / 2,
                    size = int(self.h * 0.45), bold = True, 
                    fill = 'black', font = 'monospace')


#replicated tree structure from cmu module, with a little more:
#https://www.aleksandrhovhannisyan.com/blog/python-trie-data-structure/
class TreeNode: #node in prefix tree for storing words
    def __init__(self):
        self.children = dict() #characters to child treeNodes
        self.isWord = False #true if path to node forms valid word

def buildTree(wordList):
    root = TreeNode()
    for word in wordList:
        node = root
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TreeNode()
            node = node.children[letter]
        node.isWord = True
    return root

def main():
    runAppWithScreens(initialScreen = 'start', width = 600, height = 600)
main()

