# From: https://academy.cs.cmu.edu/cpcs-docs/screens

from cmu_graphics import *

def onAppStart(app):
    # The model is shared between all screens
    app.score = 0
    app.highScore = 0
    app.fill = 'blue'
    app.x = 200
    app.y = 200
    app.r = 50

def distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

############################################################
# Start Screen
############################################################

def start_redrawAll(app):
    drawLabel('Welcome!', 200, 160, size=24, bold=True)
    # Note: we can access app.highScore (and all app variables) from any screen
    drawLabel(f'High Score: {app.highScore}', 200, 200, size=24)
    drawLabel('Press space to begin!', 200, 240, size=16)

def start_onKeyPress(app, key):
    if key == 'space':
        setActiveScreen('game')

############################################################
# Game Screen
############################################################

def game_onScreenActivate(app):
    # Every time we switch to the game screen, reset the score
    app.score = 0

def game_onMousePress(app, mouseX, mouseY):
    if distance(mouseX, mouseY, app.x, app.y) <= app.r:
        app.score += 1

def game_redrawAll(app):
    drawLabel('Press the circle to increase your score!', 200, 40, size=20)
    drawLabel('Press r to return to the start screen', 200, 60, size=16)
    drawLabel(f'Score: {app.score}', 200, 130, size=16)
    drawCircle(app.x, app.y, app.r, fill = app.fill)

def game_onKeyPress(app, key):
    if key == 'r':
        app.highScore = max(app.highScore, app.score)
        setActiveScreen('start')

############################################################
# Main
############################################################

def main():
    runAppWithScreens(initialScreen='start')

main()