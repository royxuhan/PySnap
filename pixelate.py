from main import *
from PIL import Image

def open_image(path):
    newImage = Image.open(path)
    return newImage


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


file = "NH.png"
pixelate(file, "output.png", 1)
final = open_image("output.png")
final.show()