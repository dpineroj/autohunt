from cmu_graphics import *
from PIL import Image

# This demos using images stored locally rather than on the web.
# It's the same as the scaling demo, but it uses a local image.

# This is different from the version in the CMU Graphics docs
# because this version explicitly loads a PIL image, which then lets us use
# PIL image methods, even those that create new PIL images,
# such as Image.resize() used here.

# Also, importantly:
#   * PIL includes an Image class and cmu_graphics includes an Image class.
#   * These are different classes!
#   * Be sure to import PIL after cmu_graphics so Image is PIL's Image class!

def loadPilImage(path):
    # Loads a PIL image (not a CMU image!) from a url:
    return Image.open(path)

def onAppStart(app):
    # 1. Load a PIL image from a local path:
    path = 'greatPitch.gif'
    pilImage1 = loadPilImage(path)

    # 2. Create a new PIL image that is half-sized:
    imageWidth, imageHeight = pilImage1.size
    pilImage2 = pilImage1.resize((imageWidth//2, imageHeight//2))

    # 3. Convert from PIL images to CMU images before drawing:
    app.cmuImage1 = CMUImage(pilImage1)
    app.cmuImage2 = CMUImage(pilImage2)

def redrawAll(app):
    drawImage(app.cmuImage1, 200, app.height/2, align='center')
    drawImage(app.cmuImage2, 500, app.height/2, align='center')

def main():
    runApp(width=700, height=600)

main()