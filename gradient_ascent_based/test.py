from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage import io
import matplotlib.pyplot as plt

image = io.imread(r"../image/lena.png")
segments = slic(image, n_segments=900, max_iter=5, enforce_connectivity=True)
plt.imshow(mark_boundaries(image, segments, color=(0, 0, 0)))
plt.show()
