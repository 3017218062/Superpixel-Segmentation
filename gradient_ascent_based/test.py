from skimage import io, morphology, filters
from matplotlib import pyplot as plt

image = io.imread("../result/lena_SLIC_boundary.png", as_gray=True)
image = morphology.dilation(image)
io.imshow(image)
plt.show()

image  = morphology.erosion(image)
io.imshow(image)
plt.show()
