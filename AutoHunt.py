#Name: David Pinero-Jacome
#Andrew ID: dpineroj
#utoHunt - Word Hunt Checker and Visualizer
#29.8.25
from cmu_graphics import *

def onAppStart(app):
    app.rows, app.cols = 4, 4
    app.gridMargin =50
    app.cellSize = min((app.width - 2 * app.gridMargin) // app.cols,
                        (app.height - 200) // app.rows)
    app.gridLeft = (app.width - app.cellSize * app.cols) // 2
    app.gridTop = 100
    app.currentCell = 0
    app.gridSize = app.rows * app.cols
    app.grid = [['' for _ in range(app.cols)] for _ in range(app.rows)]
 

    app.mode = 'input'

    app.stepsPerSecond = 10
    app.preCountdownSteps = 0 #time buffer
    app.countdown = 3 #before word visualization starts

    #https://boardgames.stackexchange.com/questions/38366/latest-collins-scrabble-words-list-in-text-file
    wordList = loadWords('words.txt') 
    app.treeRoot = buildTree(wordList)
    app.validWordGroups = []
    app.validWords = []
    app.currentWordIndex = 0
    app.wordStep = 0
    app.segmentDelaySteps = 0
    app.wordDelaySteps = 0

def game_onResize(app):
    app.cellSize = min((app.width - 2 * app.gridMargin) // app.cols,
                        (app.height - 200) // app.rows)
    app.gridLeft = (app.width - app.cellSize * app.cols) // 2

    
#https://stackoverflow.com/questions/30969687/use-python-to-open-a-file-in-read-mode
def loadWords(path): 
    with open(path, 'r') as f:
        words = [line.strip().upper() for line in f if len(line.strip()) > 2 \
                 and line.strip().isalpha()]
    return words

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
                size = int(app.cellSize * 0.4)
                drawLabel(letter, x + app.cellSize / 2, y + app.cellSize / 2,
                          size = size, bold = True)
def start_redrawAll(app):
    drawLabel('AUTOHUNT', app.width // 2, 160, size = 36, bold = True)
    drawLabel('automically solve word hunt puzzles', app.width // 2, 200, size = 18)
    drawLabel('press space to begin', app.width // 2, 260, size = 20)

def start_onKeyPress(app, key):
    if key == 'space':
        setActiveScreen('game')


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
                app.mode = 'preCountdown' #time buffer before countdown

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
            app.mode = 'animate'
            app.stepsPerSecond = 2 #0.5s per step
    if app.mode == 'animate':
        if app.currentWordIndex >= len(app.validWords):
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

def game_redrawAll(app):
    titleSize = int(app.height * 0.09)
    drawLabel("AUTOHUNT", app.width // 2, 50, size = titleSize, bold = True)
    drawGrid(app)

    if app.mode == 'countdown':
        countdownSize = int(app.cellSize * 0.3)
        drawLabel(app.countdown, app.width // 2, app.height // 1.05, 
                  size = countdownSize)

    if app.mode == 'animate' and app.currentWordIndex < len(app.validWords):
        word, path = app.validWords[app.currentWordIndex]
        drawWordPath(app, path, app.wordStep)
        wordSize = int(app.cellSize * 0.3)
        drawLabel(f"{word}", app.width // 2, 
                  app.gridTop + app.cellSize * app.rows + 30, 
                  size = wordSize, bold = True)

def drawWordPath(app, path, step):
    for i in range(step):
        if i < len(path) - 1:
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            x1 = app.gridLeft + c1 * app.cellSize + app.cellSize // 2
            y1 = app.gridTop + r1 * app.cellSize + app.cellSize // 2
            x2 = app.gridLeft + c2 * app.cellSize + app.cellSize // 2
            y2 = app.gridTop + r2 * app.cellSize + app.cellSize // 2
            drawLine(x1, y1, x2, y2, fill = 'red', lineWidth = 4)
    
def groupLongestWordLength(group):
    if len(group) == 0:
        return 0
    return len(group[0][0])

def findAllWords(app):
    #reset the word list and tracking sets
    app.validWords = []
    app.foundWords = set()
    app.validWordGroups = []

    #begin backtracking from each grid cell
    for row in range(app.rows):
        for col in range(app.cols):
            backtrack(app, row, col, app.treeRoot, [], set(), "")
    
    #sort each group by word length (longest to shortest)
    for group in app.validWordGroups:
        group.sort(key = wordLength, reverse = True)

    app.validWordGroups = [group for group in app.validWordGroups if len(group) > 0]
    app.validWordGroups.sort(key=groupLongestWordLength, reverse=True)
    app.validWords = [pair for group in app.validWordGroups for pair in group]

    print("==== FOUND WORDS ====")
    for word, path in app.validWords:
        print(word)

def wordLength(pair):
    return len(pair[0])


def backtrack(app, row, col, node, path, visited, wordsSoFar):
    if not (0 <= row < app.rows and 0 <= col < app.cols):
        return
    if (row, col) in visited:
        return
    
    letter = app.grid[row][col]
    if not letter or letter not in node.children:
        return
    
    node = node.children[letter]
    wordsSoFar += letter
    path.append((row, col))
    visited.add((row, col))


# Add current full word if it's valid and not already found
    if node.isWord:
        # Remove from any previous group if already found
        for group in app.validWordGroups:
            group[:] = [pair for pair in group if pair[0] != wordsSoFar]

        # Create a new group starting with this word
        app.validWordGroups.append([(wordsSoFar, path[:])])
        app.foundWords.add(wordsSoFar)

        # Now walk backward and check all shorter prefixes
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
                for group in app.validWordGroups[:-1]:
                    group[:] = [pair for pair in group if pair[0] != prefixWord]
                app.validWordGroups[-1].append((prefixWord, prefixPath))
                app.foundWords.add(prefixWord)
    
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if not (dr == 0 and dc == 0):
                backtrack(app, row + dr, col + dc, node, path,
                          visited, wordsSoFar)
    
    path.pop()
    visited.remove((row, col))

#replicated tree structure from cmu module
class TreeNode:
    def __init__(self):
        self.children = dict()
        self.isWord = False

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

