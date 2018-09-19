try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
from PIL import Image
import cv2
import random
from cascade import *

def init(data):
    data.image = ""
    data.mode = "start"
    data.pixelateFactor = 5

    data.imageFly = PhotoImage(file="images/iron.png")
    # bouncing image variables
    for x in range(data.width):
        data.imageLeft = random.randint(0, x)
    for y in range(data.height):
        data.imageTop = random.randint(0, y)
    data.imageSize = 50
    data.imageSpeed = 10
    data.headingRight = True
    data.headingDown = True

###### filters ######

# Open an Image
def open_image(path):
    newImage = Image.open(path)
    return newImage

# Save image
def save_image(image, path):
    image.save(path, 'png')


# Create a new image with the given size
def create_image(i, j):
    image = Image.new("RGB", (i, j), "white")
    return image


# Get the pixel from the given image
def get_pixel(image, i, j):
    # Inside image bounds?
    width, height = image.size
    if i > width or j > height:
        return None

  # Get Pixel
    pixel = image.getpixel((i, j))
    return pixel

# Create a Grayscale version of the image
def convert_grayscale(image):
    # Get size
    width, height = image.size

    # Create new Image and a Pixel Map
    new = create_image(width, height)
    pixels = new.load()

  # Transform to grayscale
    for i in range(width):
        for j in range(height):
        # Get Pixel
            pixel = get_pixel(image, i, j)

            # Get R, G, B values (This are int from 0 to 255)
            red =   pixel[0]
            green = pixel[1]
            blue =  pixel[2]

            # Transform to grayscale
            gray = (red * 0.299) + (green * 0.587) + (blue * 0.114)

            # Set Pixel in new image
            pixels[i, j] = (int(gray), int(gray), int(gray))

    # Return new image
    return new


# Create a Half-tone version of the image
def convert_halftoning(image):
    # Get size
    width, height = image.size

    # Create new Image and a Pixel Map
    new = create_image(width, height)
    pixels = new.load()

    # Transform to half tones
    for i in range(0, width, 2):
        for j in range(0, height, 2):
            # Get Pixels
            try:
                p1 = get_pixel(image, i, j)
                p2 = get_pixel(image, i, j + 1)
                p3 = get_pixel(image, i + 1, j)
                p4 = get_pixel(image, i + 1, j + 1)
            except IndexError:
                continue

            # Transform to grayscale
            gray1 = (p1[0] * 0.299) + (p1[1] * 0.587) + (p1[2] * 0.114)
            gray2 = (p2[0] * 0.299) + (p2[1] * 0.587) + (p2[2] * 0.114)
            gray3 = (p3[0] * 0.299) + (p3[1] * 0.587) + (p3[2] * 0.114)
            gray4 = (p4[0] * 0.299) + (p4[1] * 0.587) + (p4[2] * 0.114)

            # Saturation Percentage
            sat = (gray1 + gray2 + gray3 + gray4) / 4

            # Draw white/black depending on saturation
            if sat > 223:
                pixels[i, j]         = (255, 255, 255) # White
                pixels[i, j + 1]     = (255, 255, 255) # White
                pixels[i + 1, j]     = (255, 255, 255) # White
                pixels[i + 1, j + 1] = (255, 255, 255) # White
            elif sat > 159:
                try:
                    pixels[i, j]         = (255, 255, 255) # White
                    pixels[i, j + 1]     = (0, 0, 0)       # Black
                    pixels[i + 1, j]     = (255, 255, 255) # White
                    pixels[i + 1, j + 1] = (255, 255, 255) # White
                except IndexError:
                    continue
            elif sat > 95:
                pixels[i, j]         = (255, 255, 255) # White
                pixels[i, j + 1]     = (0, 0, 0)       # Black
                pixels[i + 1, j]     = (0, 0, 0)       # Black
                pixels[i + 1, j + 1] = (255, 255, 255) # White
            elif sat > 32:
                pixels[i, j]         = (0, 0, 0)       # Black
                pixels[i, j + 1]     = (255, 255, 255) # White
                pixels[i + 1, j]     = (0, 0, 0)       # Black
                pixels[i + 1, j + 1] = (0, 0, 0)       # Black
            else:
                pixels[i, j]         = (0, 0, 0)       # Black
                pixels[i, j + 1]     = (0, 0, 0)       # Black
                pixels[i + 1, j]     = (0, 0, 0)       # Black
                pixels[i + 1, j + 1] = (0, 0, 0)       # Black

    # Return new image
    return new


# Return color value depending on quadrant and saturation
def get_saturation(value, quadrant):
    if value > 223:
        return 255
    elif value > 159:
        if quadrant != 1:
            return 255
        return 0

    elif value > 95:
        if quadrant == 0 or quadrant == 3:
            return 255
        return 0

    elif value > 32:
        if quadrant == 1:
            return 255
        return 0

    else:
        return 0


# Create a dithered version of the image
def convert_dithering(image):
    # Get size
    width, height = image.size

    # Create new Image and a Pixel Map
    new = create_image(width, height)
    pixels = new.load()

    # Transform to half tones
    for i in range(0, width, 2):
        for j in range(0, height, 2):
        # Get Pixels
            try:
                p1 = get_pixel(image, i, j)
                p2 = get_pixel(image, i, j + 1)
                p3 = get_pixel(image, i + 1, j)
                p4 = get_pixel(image, i + 1, j + 1)
            except IndexError:
                continue

            # Color Saturation by RGB channel
            red   = (p1[0] + p2[0] + p3[0] + p4[0]) / 4
            green = (p1[1] + p2[1] + p3[1] + p4[1]) / 4
            blue  = (p1[2] + p2[2] + p3[2] + p4[2]) / 4

            # Results by channel
            r = [0, 0, 0, 0]
            g = [0, 0, 0, 0]
            b = [0, 0, 0, 0]

            # Get Quadrant Color
            for x in range(0, 4):
                r[x] = get_saturation(red, x)
                g[x] = get_saturation(green, x)
                b[x] = get_saturation(blue, x)

            # Set Dithered Colors
            pixels[i, j]         = (r[0], g[0], b[0])
            pixels[i, j + 1]     = (r[1], g[1], b[1])
            pixels[i + 1, j]     = (r[2], g[2], b[2])
            pixels[i + 1, j + 1] = (r[3], g[3], b[3])

    # Return new image
    return new


# Create a Primary Colors version of the image
def convert_primary(image):
    # Get size
    width, height = image.size

    # Create new Image and a Pixel Map
    new = create_image(width, height)
    pixels = new.load()

    # Transform to primary
    for i in range(width):
        for j in range(height):
            # Get Pixel
            pixel = get_pixel(image, i, j)

            # Get R, G, B values (This are int from 0 to 255)
            red =   pixel[0]
            green = pixel[1]
            blue =  pixel[2]

            # Transform to primary
            if red > 127:
                red = 255
            else:
                red = 0
            if green > 127:
                green = 255
            else:
                green = 0
            if blue > 127:
                blue = 255
            else:
                blue = 0

            # Set Pixel in new image
            pixels[i, j] = (int(red), int(green), int(blue))

    # Return new image
    return new


##### cartoonizer #####

num_down = 2     # number of downsampling steps
num_bilateral = 7  # number of bilateral filtering steps

def cartoonize(image):
    img_rgb = cv2.imread(image)

    # downsample image using Gaussian pyramid
    img_color = img_rgb

    for _ in range(num_down):
        try:
            img_color = cv2.pyrDown(img_color)
        except:
            img_color = cv2.pyrUp(img_color)

    # repeatedly apply small bilateral filter instead of
    # applying one large filter
    for _ in range(num_bilateral):
        img_color = cv2.bilateralFilter(img_color, d=9,
                                        sigmaColor=9,
                                        sigmaSpace=7)

    # upsample image to original size
    for _ in range(num_down):
        img_color = cv2.pyrUp(img_color)

    # convert to grayscale and apply median blur
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)

    # detect and enhance edges
    img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                     cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY,
                                     blockSize=9,
                                     C=3)

    # convert back to color, bit-AND with color image
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
    try:
        img_cartoon = cv2.bitwise_and(img_color, img_edge)
    except:
        img_cartoon = cv2.bitwise_and(img_color, img_color, img_edge)
    return img_cartoon


# display
# cv2.imshow("cartoon", img_cartoon)
# cv2.imwrite('outputCa.png', img_cartoon)

cv2.waitKey(0)
cv2.destroyAllWindows()

##### pixelate #####

def pixelate(input_file_path, output_file_path, pixel_size):
    image = Image.open(input_file_path)
    image = image.resize(
        (image.size[0] // pixel_size, image.size[1] // pixel_size),
        Image.NEAREST
    )
    image = image.resize(
        (image.size[0] * pixel_size, image.size[1] * pixel_size),
        Image.NEAREST
    )
    image.save(output_file_path)


#####


####################################
# mode dispatcher (stolen from 112 website)
####################################

def mousePressed(event, data):
    if (data.mode == "start"):        startMousePressed(event, data)
    elif (data.mode == "filter"):   filterMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "start"):        startKeyPressed(event, data)
    elif (data.mode == "filter"):   filterKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "start"):        startTimerFired(data)
    elif (data.mode == "filter"):   filterTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "start"):        startRedrawAll(canvas, data)
    elif (data.mode == "filter"):   filterRedrawAll(canvas, data)

####################################
# start mode
####################################

def startMousePressed(event, data):
    pass

def startKeyPressed(event, data):
    if event.keysym == "u" or event.keysym == "U":
        data.image = input("What's the image called?")
        img = open_image(data.image)
        img.show()
    if event.keysym == "y":
        data.mode = "filter"
    if event.keysym == "t":
        cascade()
    if event.keysym == "s":
        pass

def doStep(data):
    # modified from the Bouncing and Pausing Square Demo
    # move vertically
    if (data.headingRight == True):
        if (data.imageLeft + data.imageSize > data.width):
            data.headingRight = False
        else:
            data.imageLeft += data.imageSpeed
    else:
        if (data.imageLeft < 0):
            data.headingRight = True
        else:
            data.imageLeft -= data.imageSpeed

    # move horizontally
    if (data.headingDown == True):
        if (data.imageTop + data.imageSize > data.height):
            data.headingDown = False
        else:
            data.imageTop += data.imageSpeed
    else:
        if (data.imageTop < 0):
            data.headingDown = True
        else:
            data.imageTop -= data.imageSpeed

def startTimerFired(data):
    doStep(data)

def mousePressed(event, data):
    # use event.x and event.y
    pass

def startRedrawAll(canvas, data):
    canvas.create_rectangle(0,0,data.width,data.height,fill="gold")
    canvas.create_image(data.imageLeft, data.imageTop, anchor=NW,image=data.imageFly)
    canvas.create_text(data.width//2, data.height//3, text="SnapDat!", font="Helvetica 48 bold", fill="black")
    canvas.create_text(data.width//2, data.height//3+80, text="Better than Photoshop (...and Snapchat)", font="Helvetica 12", fill="#4885ed")
    canvas.create_text(data.width//2, data.height//3+120, text="Turn on your camera? ('t') (We don't sell your data unlike Facebook)", font="Helvetica 12 bold", fill="#db3236")
    canvas.create_text(data.width//2, data.height//3+170, text="Please upload your image ('u')", font="Helvetica 12 bold", fill="#4885ed")
    canvas.create_text(data.width//2, data.height//3+220, text="Your image: %s" %data.image, font="Helvetica 12 bold", fill="#3cba54")
    canvas.create_text(data.width//2, data.height//3+270, text="Is this your image?", font="Helvetica 12 bold", fill="#4885ed")
    canvas.create_text(data.width//2, data.height//3+320, text="Press ('y') for awesome stuff!", font="Helvetica 12 bold", fill="#db3236")

####################################
# filter mode
####################################

def filterMousePressed(event, data):
    pass

def filterKeyPressed(event, data):
    if event.keysym == 'a' or event.keysym == "A":
        original = open_image(data.image)
        new = convert_grayscale(original)
        new.show()
        save_image(new, 'SnapPix_gray.png')
    elif event.keysym == 'b' or event.keysym == "B":
        original = open_image(data.image)
        new = convert_halftoning(original)
        new.show()
        save_image(new, 'SnapPix_half.png')
    elif event.keysym == 'c' or event.keysym == "C":
        original = open_image(data.image)
        new = convert_dithering(original)
        new.show()
        save_image(new, 'SnapPix_dither.png')
    elif event.keysym == 'd' or event.keysym == "D":
        original = open_image(data.image)
        new = convert_primary(original)
        new.show()
        save_image(new, 'SnapPix_primary.png')
    elif event.keysym == 'e' or event.keysym == "E":
        img_cartoon = cartoonize(data.image)
        cv2.imshow("cartoon", img_cartoon)
        cv2.imwrite('SnapPix_cartoon.png', img_cartoon)
    elif event.keysym == 'f' or event.keysym == "F":
        file = data.image
        # img = open_image(file)
        data.pixelateFactor = input("What's your Pixelate Factor?")
        pixelate(file, "SnapPix_pixel.png", int(data.pixelateFactor))
        final = open_image("SnapPix_pixel.png")
        final.show()


def filterTimerFired(data):
    pass

def filterRedrawAll(canvas, data):
    # draw all the text and background
    canvas.create_rectangle(0,0,data.width,data.height,fill="black")
    canvas.create_text(data.width//2, data.height*(1/6)-60, text="Convert your image to Grayscale! ('A')", font="Helvetica 24 bold", fill="Snow3")
    canvas.create_text(data.width//2, data.height*(2/6)-60, text="Convert your image to Halftoning! ('B')", font="Helvetica 24 bold", fill="AntiqueWhite2")
    canvas.create_text(data.width//2, data.height*(3/6)-60, text="Convert your image to Dithering! ('C')", font="Helvetica 24 bold", fill="#f4c20d")
    canvas.create_text(data.width//2, data.height*(4/6)-60, text="Convert your image to Primary! ('D')", font="Helvetica 24 bold", fill="#3cba54")
    canvas.create_text(data.width//2, data.height*(5/6)-60, text="Convert your image to Cartoon! ('E')", font="Helvetica 24 bold", fill="#db3236")
    canvas.create_text(data.width//2, data.height*(6/6)-60, text="Convert your image to Pixel Art! ('F')", font="Helvetica 24 bold", fill="#4885ed")

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
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
    root = Tk()
    init(data)
    # create the root and the canvas
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

run(800, 800)
