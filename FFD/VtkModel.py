import vtk
from FFD import objReader, FFD
import numpy as np
from time import time
from OBJProcessing import resizePolyData, applyColorsToPoints, extractColorsFromFile


class VtkModel(object):
    # 初始化参数
    # render: 指定vtk场景的渲染器对象，默认值为None
    # irender: 指定vtk渲染窗口的交互器对象，默认值为None
    # filename: 指定要加载的3D模型的文件名，默认为“bunny.obj”
    # resize: 控制加载的模型的缩放比例，默认值为1
    # color: 控制是否为模型启用颜色，默认值为False
    # r: 用于控制画布中球体的半径大小，默认值为0.01
    # x1,y1,z1: 控制物体的初始尺寸，用于在创建模型时设置其大小
    def __init__(self, render=None, irender=None, filename="bunny.obj", resize=1, color=False, r=0.01, x1=4, y1=4,
                 z1=4):
        self.render = render
        self.irender = irender
        self.filename = filename
        self.resize = resize
        self.r = r
        self.color = color
        self.x1 = x1
        self.y1 = y1
        self.z1 = z1

        # 设置背景颜色
        self.render.SetBackground(237, 237, 237)
        # 交互方式
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.irender.SetInteractorStyle(style)

        # 初始化绘图
        self.load_obj()
        self.drawface()

        # 根据文件中物体的大小，自动设置球体的半径
        self.r = (self.ffd.maxX - self.ffd.minX) * self.r
        # 绘制点和线，添加监听器
        self.drawpoints()
        self.drawlines()
        self.add_points_ob()

    # 将控制点的索引值i，j，k转化为坐标系中的坐标x，y，z，由FFD算法自动生成能恰好包住物体的长方体
    def ijk_to_xyz(self, i, j, k):
        x, y, z = self.ffd.controlPointsPosition[i][j][k]
        return x, y, z

    # 找出第i，j，k号球所有邻居球体的索引值，并判断是否越界
    def neighbor(self, i, j, k):
        n = []
        if i > 0:
            n.append((i - 1, j, k))
        if i < self.x1:
            n.append((i + 1, j, k))
        if j > 0:
            n.append((i, j - 1, k))
        if j < self.y1:
            n.append((i, j + 1, k))
        if k > 0:
            n.append((i, j, k - 1))
        if k < self.z1:
            n.append((i, j, k + 1))
        return n

    # 加载obj格式文件
    def load_obj(self):
        self.reader = vtk.vtkOBJReader()
        self.reader.SetFileName(self.filename)
        self.reader.Update()
        self.data = self.reader.GetOutput()

    # def color(self):
    #     if self.COLORED:
    #         return
    #     else:
    #         self.data.GetPointData().SetScalars(self.data_color.GetPointData().GetScalars())
    #         self.COLORED = True
    #     mapper = vtk.vtkPolyDataMapper()
    #     mapper.SetInputData(self.data)
    #     try:
    #         self.ren.RemoveActor(self.actor)
    #         self.actor = vtk.vtkActor()
    #         self.actor.SetMapper(mapper)
    #         self.ren.AddActor(self.actor)
    #     except:
    #         pass

    # 调整尺寸，对PolyData进行减采样，对Triangle类型有效
    # def adjust_size(self, resize):
    #     self.data = resizePolyData(self.data, resize)
    #     self.data_color = resizePolyData(self.data_color, resize)
    #
    #     self.points = self.data.GetPoints()
    #     vertices = [self.points.GetPoint(i) for i in range(self.points.GetNumberOfPoints())]
    #     self.ffd = FFD(pointNumX=self.x1 + 1, pointNumY=self.y1 + 1, pointNumZ=self.z1 + 1, objFile=self.filename,
    #                    points=vertices)
    #     self.ffd.initFFD()
    #     mapper = vtk.vtkPolyDataMapper()
    #     mapper.SetInputData(self.data)
    #     self.render.RemoveActor(self.actor)
    #     self.actor = vtk.vtkActor()
    #     self.actor.SetMapper(mapper)
    #     self.render.AddActor(self.actor)

    # 绘制人脸并选择是否上色和控制缩放比例
    def drawface(self, resize=1.0, color=False):
        self.data_color = vtk.vtkPolyData()
        self.data_color.DeepCopy(self.data)
        self.data_color = applyColorsToPoints(self.data_color, extractColorsFromFile(self.filename))
        self.colored = False

        if color:
            self.color()

        if resize != 1:
            self.data = resizePolyData(self.data, resize)
            self.data_color = resizePolyData(self.data_color, resize)

        self.points = self.data.GetPoints()
        vertices = [self.points.GetPoint(i) for i in range(self.points.GetNumberOfPoints())]
        self.ffd = FFD(pointNumX=self.x1 + 1, pointNumY=self.y1 + 1, pointNumZ=self.z1 + 1, objFile=self.filename,
                       points=vertices)
        self.ffd.initFFD()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.data)

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.render.AddActor(self.actor)

    # 绘制每个控制点对应的球体
    def drawpoints(self):
        # 初始化列表，存放i*j*k个球体
        self.slist = [[[0 for zlist in range(self.z1 + 1)] for ylist in range(self.y1 + 1)] for xlist in
                      range(self.x1 + 1)]

        """
        首先定义球体widget，选择渲染窗口交互器，再将索引值转换为坐标值，
        最后将所有球体的坐标保存在列表slist中。
        """
        for i, j, k in ((xlist, ylist, zlist) for xlist in range(self.x1 + 1) for ylist in range(self.y1 + 1) for zlist
                        in range(self.z1 + 1)):
            swidget = vtk.vtkSphereWidget()
            swidget.SetInteractor(self.irender)
            x, y, z = self.ijk_to_xyz(i, j, k)
            swidget.SetCenter(x, y, z)
            swidget.SetRadius(self.r)
            # swidget.GetSphereProperty().SetColor(0, 1.0, 0)
            swidget.SetRepresentationToSurface()
            swidget.On()
            self.slist[i][j][k] = swidget

    # 绘制连接控制点之间的线段
    def drawlines(self):
        # 初始化source_list，datamapper_list和actor_list，由于每个球体最多对应6个邻接球，则列表为6*i*j*k维
        self.source_list = [
            [[[vtk.vtkLineSource() for n in range(6)] for c in range(self.z1 + 1)] for b in range(self.y1 + 1)] for a in
            range(self.x1 + 1)]
        self.datamapper_list = [
            [[[vtk.vtkPolyDataMapper() for n in range(6)] for c in range(self.z1 + 1)] for b in range(self.y1 + 1)] for
            a in range(self.x1 + 1)]
        self.actor_list = [
            [[[vtk.vtkActor() for n in range(6)] for c in range(self.z1 + 1)] for b in range(self.y1 + 1)] for a in
            range(self.x1 + 1)]
        # 初始化球的坐标列表sposition，根据球体的数目可知列表为i*j*k维
        self.sposition = [[[0 for c in range(self.z1 + 1)] for b in range(self.y1 + 1)] for a in range(self.x1 + 1)]

        for i, j, k in ((xlist, ylist, zlist) for xlist in range(self.x1 + 1) for ylist in range(self.y1 + 1) for zlist
                        in range(self.z1 + 1)):
            # 获取球心的坐标
            x1, y1, z1 = self.slist[i][j][k].GetCenter()
            self.sposition[i][j][k] = [x1, y1, z1]
            n = self.neighbor(i, j, k)
            index = 0
            for (ni, nj, nk) in n:
                x2, y2, z2 = self.slist[ni][nj][nk].GetCenter()
                # 设置起点与终点
                self.source_list[i][j][k][index].SetPoint1(x1, y1, z1)
                self.source_list[i][j][k][index].SetPoint2(x2, y2, z2)

                self.datamapper_list[i][j][k][index].SetInputConnection(
                    self.source_list[i][j][k][index].GetOutputPort())
                self.actor_list[i][j][k][index].SetMapper(self.datamapper_list[i][j][k][index])
                self.actor_list[i][j][k][index].GetMapper().ScalarVisibilityOff()
                self.actor_list[i][j][k][index].GetProperty().SetColor(0, 1.0, 0)
                self.render.AddActor(self.actor_list[i][j][k][index])
                index += 1

    # 在每一个球体控制点上添加Observer观测用户，并利用回调函数sphere_callback进行交互
    def add_points_ob(self):
        for i, j, k in ((xlist, ylist, zlist) for xlist in range(self.x1 + 1) for ylist in range(self.y1 + 1) for zlist
                        in range(self.z1 + 1)):
            self.slist[i][j][k].AddObserver("InteractionEvent", self.sphere_callback)

    # 定义回调函数sphere_callback，其功能有：检查控制点是否移动，并更新连线
    def sphere_callback(self, obj, event):
        self._sphere_callback()

    # 更新模型中每个控制点对应的球体的位置
    def sphere_qt(self, ijk, xyz):
        i, j, k = ijk
        self.slist[i][j][k].SetCenter(xyz)
        self._sphere_callback()

    def _sphere_callback(self):
        for i, j, k in ((xlist, ylist, zlist) for xlist in range(self.x1 + 1) for ylist in range(self.y1 + 1) for zlist
                        in range(self.z1 + 1)):
            # 得到球体之前的位置
            xi, yi, zi = self.sposition[i][j][k]
            # 得到球体现在的位置
            xj, yj, zj = self.slist[i][j][k].GetCenter()

            # 对经过移动的球体进行计算操作
            if xj != xi or yj != yi or zj != zi:
                print("Before Position:", xi, yi, zi)
                print("New Position:", xj, yj, zj)
                print(i, j, k)
                self.ffd.cacheUpdate((i, j, k), np.array([xj, yj, zj]))
                self.sposition[i][j][k]=[xj, yj, zj]
                # 重新计算位置改变的球体的坐标
                n = self.neighbor(i, j, k)
                count = 0
                for (ni, nj, nk) in n:
                    # 对于这个移动过的球体i的邻居j 获取球心的位置
                    xk, yk, zk = self.slist[ni][nj][nk].GetCenter()
                    # 设置新位置与邻接球体的起点和终点
                    self.source_list[i][j][k][count].SetPoint1(xj, yj, zj)
                    self.source_list[i][j][k][count].SetPoint2(xk, yk, zk)
                    self.datamapper_list[i][j][k][count].SetInputConnection(
                        self.source_list[i][j][k][count].GetOutputPort())
                    # 删去原有线段，生成新的线段
                    nei_of_nei = self.neighbor(ni, nj, nk).index((i, j, k))
                    self.render.RemoveActor(self.actor_list[ni][nj][nk][nei_of_nei])
                    self.actor_list[i][j][k][count].SetMapper(self.datamapper_list[i][j][k][count])
                    self.actor_list[i][j][k][count].GetMapper().ScalarVisibilityOff()
                    self.actor_list[i][j][k][count].GetProperty().SetColor(0, 1.0, 0)
                    self.render.AddActor(self.actor_list[i][j][k][count])
                    count += 1

        print("Use FFD and calculate: ")
        # 更新球体控制点
        self.ffd.updateControlPoint()
        self.points = self.data.GetPoints()

        t = time()
        for a, b, c in self.ffd.cache.keys():
            for a1, b1, c1 in ((a1, b1, c1) for a1 in range(-2, 2) for b1 in range(-2, 2) for c1 in range(-2, 2)):
                if 0 <= a + a1 < self.ffd.controlPointNumX and 0 <= b + b1 < self.ffd.controlPointNumY and 0 <= c + c1 < self.ffd.controlPointNumZ:
                    for (index, x, y, z) in self.ffd.objectPoints[(a + a1, b + b1, c + c1)]:
                        temp = self.ffd.T_local([x, y, z])
                        self.points.SetPoint(index, tuple([x + temp[0], y + temp[1], z + temp[2]]))
        print(time() - t)

        # 构造mapper
        self.ffd.cacheReset()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.data)
        # 删去原始人脸
        self.render.RemoveActor(self.actor)
        # 更新人脸
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.render.AddActor(self.actor)
        print("FFD finished.")


if __name__ == "__main__":
    render = vtk.vtkRenderer()
    irender = vtk.vtkRenderWindowInteractor()
    renderwindow = vtk.vtkRenderWindow()

    renderwindow.AddRenderer(render)
    irender.SetRenderWindow(renderwindow)

    VtkModel(render=render, irender=irender)

    irender.Initialize()
    renderwindow.Render()
    irender.Start()
