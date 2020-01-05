# SLIC

## 算法实现

### RGB转LAB

公式:

![](../resource/gradient_ascent_based/SLIC/rgb2lab1.gif)

![](../resource/gradient_ascent_based/SLIC/L.gif)

![](../resource/gradient_ascent_based/SLIC/a.gif)

![](../resource/gradient_ascent_based/SLIC/b.gif)

我们可以使用skimage.color.rgb2lab()来实现这个操作。

### 初始化聚类中心

- 首先，我们设置超像素或者说聚类的数量K。

- 然后按照等大小将图片分为K个超像素块。

    ![](../resource/gradient_ascent_based/SLIC/S.gif)

- 初始化聚类中心，用一个名为Cluster的数组保存它们。

    ![](../resource/gradient_ascent_based/SLIC/initial.png)

- 我们需要名为Distance和Label的两个数组，分别用来保存当前点和最近的聚类中心的距离和最近的聚类中心的标签。

### 迭代聚类

对于每次迭代，我们选取点周围2Sx2S的区域：

- 计算Distance数组。(每个点与它们最近的聚类中心的距离)

    ![](../resource/gradient_ascent_based/SLIC/dc.gif)

    ![](../resource/gradient_ascent_based/SLIC/ds.gif)

    ![](../resource/gradient_ascent_based/SLIC/d.gif)
    
    - m(Nc)是Lab空间中的最大颜色距离，设置为10。
    
    - s(Ns)是Lab空间中的最大空间距离，设置为superPixelLength。

- 选择Label数组。(每个点最近的聚类中心的标签)

- 更新聚类中心。(使用每个聚类的几何中心)

## 注意

### 为什么要将rgb转为lab？

- 它不仅是一种与设备无关的颜色模型，而且是一种基于生理特性的颜色模型。LAB颜色模型由三个元素组成，一个是亮度（L），A和B是两个颜色通道。A包括从深绿色（低亮度值）到灰色（中等亮度值）到亮粉色（高亮度值）的颜色；B是从亮蓝色（低亮度值）到灰色（中等亮度值）到黄色（高亮度值）。因此，这种颜色在混合后会产生鲜艳的颜色，LAB模式定义了最多的颜色。

- LAB模式的分割效果优于RGB模式下的分割效果。

### 为什么要选择2Sx2S的区域？

- 缩小了超像素的搜索区域。

- 使SLIC的复杂度无关与超像素的数量。

## 算法优化

### 选择梯度

它可以避免在边缘定位超像素，并且减少用噪声代替超像素的机会。

在每个点的3x3的区域中：

- 分别计算附近8个点的梯度。

    ![](../resource/gradient_ascent_based/SLIC/dx.gif)
    
    ![](../resource/gradient_ascent_based/SLIC/dy.gif)
    
    ![](../resource/gradient_ascent_based/SLIC/g.gif)

- 选择梯度最小的点为新的聚类中心。

### 合并小块

由于聚类过程的特点，并不能保证每个类在XY空间都是连续的。

首先，使用BFS找出每个连接的块。

时间复杂度为O(mn)，其中n和m分别为图像的长度和宽度。

然后，当块的大小小于预设阈值时，使用并行搜索集合并连接小块。

- 计算所有连通图。

- 初始化阈值。

- 将小块合并到附近的块中。

### 绘制边界

显然，在四个方向上具有不同标签的点是边界点。

由于数组的遍历方法，我们只需要查看右方或下方的点。

此外，如果左边或上面有标记，我们可以跳过这个点。

## 结果

分割后的超像素:

![](../result/lena_SLIC_pixel.png)

分割后的图片:

![](../result/lena_SLIC_image.png)