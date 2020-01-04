from tool.imageTool import *
from collections import Counter
import math


class Cluster(object):
    ID = 0
    l, a, b, x, y = 0, 0, 0, 0, 0

    def __init__(self, l, a, b, x, y, ID=0):
        self.l = l
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        self.ID = ID

    def update(self, l, a, b, x, y):
        self.l = l
        self.a = a
        self.b = b
        self.x = x
        self.y = y

    def __str__(self):
        return "{},{}:{} {} {} ".format(self.x, self.y, self.l, self.a, self.b)


class SLIC():
    def __init__(self, image, k, iterNumber=3):
        """
        - Initialize the image and its properties.
        - Set the length of super pixels.
        - Create label and distance with height and width.
            - label: Used to record which super pixel the current point belongs to.
            - distance: Used to record the shortest distance between the current point and the center of the super pixel.
        - Define a array saving the cluster information.
        """
        self.image = image
        self.height, self.width = self.image.shape[:2]
        self.superPixelLength = math.sqrt(self.height * self.width / k)
        self.label = np.zeros((self.height, self.width), dtype="int")
        self.distance = np.zeros((self.height, self.width), dtype="int")
        self.distance[:, :] = 1e9
        self.clusters = []
        self.clusterNumber = 0
        self.iterNumber = iterNumber
        self.boundary = color.rgb2lab(np.zeros(self.image.shape))

    def run(self):
        self.__clusterInit()
        self.__clusterMove()
        for i in range(self.iterNumber):
            self.__labelChoose()
            self.__clusterUpdate()
        self.__connect()
        self.__enforceConnect2()
        self.__imageSplit()

    def __clusterInit(self):
        """
        - Split the image according to superPixelLength.
        - Add all super pixels to clusters array.
        """
        print("Initializing...")
        for i in range(int(self.height / self.superPixelLength)):
            for j in range(int(self.width / self.superPixelLength)):
                self.clusterNumber += 1
                x = int(self.superPixelLength * (i + 0.5))
                y = int(self.superPixelLength * (j + 0.5))
                l, a, b = image[x][y]
                self.clusters.append(Cluster(l, a, b, x, y, self.clusterNumber))

    def __clusterMove(self):
        """
        - Define gradientCalculate function.
        - Change clusters' center according to smallest gredient.
        """

        def gradientCalculate(self, x, y):
            gradient = 0
            for i in range(3):
                gradient += math.fabs(self.image[x][y + 1][i] - self.image[x][y - 1][i]) + math.fabs(
                    self.image[x + 1][y][i] - self.image[x - 1][y][i])

            return gradient / 2

        print("Moving...")
        for index in range(self.clusterNumber):
            cluster = self.clusters[index]
            x, y = cluster.x, cluster.y
            minGradient = gradientCalculate(self, x, y)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == dy == 0:
                        continue
                    _x = cluster.x + dx
                    _y = cluster.y + dy
                    currentGradient = gradientCalculate(self, _x, _y)
                    if currentGradient < minGradient:
                        minGradient = currentGradient
                        x, y = _x, _y
            currentPixel = self.image[x][y]
            self.clusters[index].update(currentPixel[0], currentPixel[1], currentPixel[2], x, y)

    def __labelChoose(self):
        """
        - Define the distCalculate function.
        - Choose the nearest cluster's center for every point.
        - Update every cluster's center after choosing.
        """

        def distCalculate(point, clusterCenter, Nc=10, Ns=self.superPixelLength):
            Dc2 = (point.l - clusterCenter.l) ** 2 + (point.a - clusterCenter.a) ** 2 + (point.b - clusterCenter.b) ** 2
            Ds2 = (point.x - clusterCenter.x) ** 2 + (point.y - clusterCenter.y) ** 2
            D = Dc2 * (Ns ** 2) + Ds2 * (Nc ** 2)
            return D

        print("Clustering...")
        h, w = self.height - 1, self.width - 1
        for index in range(self.clusterNumber):
            clusterCenter = self.clusters[index]
            for i in range(int(clusterCenter.x - self.superPixelLength), int(clusterCenter.x + self.superPixelLength)):
                if i < 0 or i > h: continue
                for j in range(int(clusterCenter.y - self.superPixelLength),
                               int(clusterCenter.y + self.superPixelLength)):
                    if j < 0 or j > w: continue
                    currentPixel = self.image[i][j]
                    D = distCalculate(Cluster(currentPixel[0], currentPixel[1], currentPixel[2], i, j), clusterCenter)
                    if D < self.distance[i][j]:
                        self.label[i][j], self.distance[i][j] = clusterCenter.ID, D

    def __clusterUpdate(self):
        """
        - Calculate the average of every cluster.
        - Use average to replace center.
        """
        print("Updating...")
        X, Y, num = [0] * self.clusterNumber, [0] * self.clusterNumber, [0] * self.clusterNumber
        for i in range(self.height):
            for j in range(self.width):
                k = self.label[i][j] - 1
                X[k] += i
                Y[k] += j
                num[k] += 1

        for index in range(self.clusterNumber):
            x, y = X[index] // num[index], Y[index] // num[index]
            currentPixel = self.image[x][y]
            self.clusters[index].update(currentPixel[0], currentPixel[1], currentPixel[2], x, y)

    def __enforceConnect(self):
        """
        - Count the label.
        - Initialize the threshold.
        - Merge small block into right block.
        """
        labels = Counter(self.label.reshape(-1))
        threshold = (self.superPixelLength ** 2) / 4
        while True:
            stop = 1
            for i in range(self.height):
                for j in range(self.width):
                    if labels[self.label[i][j]] < threshold and j + 1 < self.width:
                        self.label[i][j] += 1
                        stop = 0
            if stop: break

    def __connect(self):
        label = self.label
        height, width = self.height, self.width

        cnt = 0
        vis = np.zeros(label.shape)
        dx = [-1, 1, 0, 0]
        dy = [0, 0, 1, -1]

        for i in range(height):
            for j in range(width):
                if not vis[i][j]:
                    cnt += 1
                    Q = [(i, j)]
                    while len(Q):
                        x, y = Q.pop(0)
                        vis[x][y] = cnt
                        for k in range(4):
                            xx = x + dx[k]
                            yy = y + dy[k]
                            if 0 <= xx and xx < width and 0 <= yy and yy < height  and vis[xx][yy] != cnt:
                                vis[xx][yy] = cnt
                                Q.append((xx, yy))
        self.label = vis

    def __enforceConnect2(self):
        N = self.clusterNumber + 1
        label = self.label
        threshold = self.superPixelLength ** 2 / 4

        count = np.zeros(N)
        height, width = self.height, self.width
        for i in range(height):
            for j in range(width):
                count[label[i][j]] += 1
        p = np.arange(N)

        def find(x):
            if p[x] == x:
                return x
            else:
                p[x] = find(p[x])
                return p[x]

        def union(i, j):
            x = find(i)
            y = find(j)
            if x != y:
                p[x] = y
                count[x] += count[y]
                print(x,y)

        for i in range(height - 1):
            for j in range(width - 1):
                x = find(label[i][j])
                if count[x] < threshold:
                    y = find(label[i][j + 1])
                    z = find(label[i + 1][j])
                    if x != y:
                        union(x, y)
                    elif x != z:
                        union(x, z)
        for i in range(height):
            for j in range(width):
                label[i][j] = find(label[i][j])
        self.label = label

    def __imageSplit(self):
        """
        - Draw the boundary of super pixels.
            - Depending on the surrounding super pixels.
            - Because pixels are traversed by rows and columns, we only need to look at the right and bottom.
            - Determine whether there is a divided boundary around to refine the boundary.
        - Draw all super pixel blocks.
        """
        print("Spliting...")
        for i in range(self.height):
            up = i - 1 if i - 1 > -1 else i
            down = i + 1 if i + 1 < self.height else i
            for j in range(self.width):
                left = j - 1 if j - 1 > -1 else j
                right = j + 1 if j + 1 < self.width else j
                k = self.label[i][j]
                # if not (k == self.label[i][left] == self.label[i][right] == self.label[up][j] == self.label[down][j]):
                #     self.image[i][j] = np.asarray([100, 0, 0])
                #     continue
                # if not k == self.label[i][right] == self.label[down][j]:
                #     self.image[i][j] = np.asarray([100, 0, 0])
                #     continue
                if (k != self.label[i][right] and self.image[i][left][0] != 100) or (
                        k != self.label[down][j] and self.image[up][j][0] != 100):
                    self.image[i][j] = np.asarray([100, 0, 0])
                    continue
                cluster = self.clusters[k - 1]
                self.image[i][j] = np.asarray([cluster.l, cluster.a, cluster.b])

    def imageSave(self, filename):
        newImage = (color.lab2rgb(self.image) * 255).astype(np.uint8)
        io.imsave(filename, newImage)

    def boundarySave(self, filename):
        newImage = (color.lab2rgb(self.boundary) * 255).astype(np.uint8)
        io.imsave(filename, newImage)


if __name__ == "__main__":
    image = imageLoad()
    slic = SLIC(image, k=400, iterNumber=5)
    slic.run()
    slic.imageSave("../result/cloth_SLIC.png")
    # slic.boundarySave("../result/cloth_SLIC_boundary.png")
