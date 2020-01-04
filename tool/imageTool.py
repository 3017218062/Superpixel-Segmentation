import numpy as np
from skimage import io, color, util, morphology


def imageLoad():
    image = io.imread(r"../image/cloth.jpg")
    image = color.rgb2lab(image)
    return image


def imageSave(image, imageName="lena.png"):
    io.imsave(r"../result/%s" % imageName, color.lab2rgb(image))

# if __name__ == "__main__":
#     print(imageLoad())
