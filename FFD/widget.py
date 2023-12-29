import sys
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
                             QApplication, QInputDialog, QMessageBox, QMainWindow, QAction, QFileDialog)
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from VtkModel import VtkModel
import gc


class widget(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'FFD'
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 800
        self.filename = "bunny.obj"
        self.initUI()
        self.initializeVTK()
        self.showAll()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 主垂直布局
        mainLayout = QVBoxLayout(self)

        # 水平布局用于放置按钮
        buttonLayout = QHBoxLayout()

        # 创建具有不同功能的五个按钮
        button1 = QPushButton('Load', self)
        button1.clicked.connect(self.loadFunction)

        button2 = QPushButton('Save', self)
        button2.clicked.connect(self.saveFunction)

        button3 = QPushButton('SelectDot', self)
        button3.clicked.connect(self.selectDotFunction)

        button4 = QPushButton('Reset', self)
        button4.clicked.connect(self.resetFunction)

        button5 = QPushButton('Quit', self)
        button5.clicked.connect(self.quitFunction)

        # 将按钮添加到水平布局中
        for button in [button1, button2, button3, button4, button5]:
            buttonLayout.addWidget(button)

        # 将水平布局添加到主垂直布局中
        mainLayout.addLayout(buttonLayout)

        # 创建并添加 QVTKRenderWindowInteractor
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        mainLayout.addWidget(self.vtkWidget)

    def initializeVTK(self, dots=5):
        """ VTK 渲染器和渲染窗口初始化 """
        self.render = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.render)
        self.irender = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.dots = dots
        self.dot_xyz = [None, None, None]

        self.model = VtkModel(render=self.render, irender=self.irender,
                              filename=self.filename, x1=dots - 1, y1=dots - 1, z1=dots - 1)

    def showAll(self):
        self.irender.Initialize()
        self.show()

    def loadFunction(self):
        """ 导入 .obj 文件"""
        # 打开文件选择对话框，并设置过滤器仅显示 OBJ 文件
        filename, ok = QFileDialog.getOpenFileName(self, 'Load .OBJ', '', 'OBJ Files (*.obj)')

        # 检查用户是否选择了文件并确认了选择
        if not ok or not filename:
            print("No file selected or loading canceled.")
            return

        # 更新 filename 属性
        self.filename = filename

        # 重新初始化 VTK 渲染窗口以加载新文件
        try:
            self.initializeVTK()
            self.showAll()
            print("Successfully loaded:", self.filename)
        except Exception as e:
            # 在出现错误时打印错误信息
            print("Error loading file:", e)

    def saveFunction(self):
        """ 保存 .obj 文件"""
        # 打开文件保存对话框
        filename, ok = QFileDialog.getSaveFileName(self, 'Save .OBJ', '', 'OBJ Files (*.obj)')

        # 如果用户选择了文件，则继续
        if ok and filename:
            try:
                # 使用 with 语句自动管理文件资源
                with open(filename, 'w') as file:
                    # 提取顶点数据和颜色数据
                    vertices = self.model.data.GetPoints()
                    colors = self.model.data.GetPointData().GetScalars()

                    # 写入顶点信息
                    for i in range(vertices.GetNumberOfPoints()):
                        x, y, z = vertices.GetPoint(i)
                        color_string = ''
                        if colors and i < colors.GetNumberOfTuples():
                            r, g, b = colors.GetTuple3(i)
                            color_string = f" {r / 255:.3f} {g / 255:.3f} {b / 255:.3f}"
                        file.write(f"v {x} {y} {z}{color_string}\n")

                    # 写入面信息
                    for i in range(self.model.data.GetNumberOfCells()):
                        cell = self.model.data.GetCell(i)
                        face = ' '.join([str(cell.GetPointId(j) + 1) for j in range(cell.GetNumberOfPoints())])
                        file.write(f"f {face}\n")

                print(f"OBJ file saved: {filename}")
            except Exception as e:
                print(f"Failed to save OBJ file: {e}")
        else:
            print("Save operation cancelled.")

    def selectDotFunction(self):
        """ 选择控制点功能槽函数 """
        self.dot_xyz = []
        prompts = [("X", "leftmost", "rightmost"), ("Y", "most far away from you", "closest initially"),
                   ("Z", "bottom", "top")]

        for axis, start, end in prompts:
            value, ok = QInputDialog.getInt(self, f"Select Dot {axis}",
                                            f"0 is the {start}, {self.dots - 1} is the {end}:", 0, 0, self.dots - 1, 1)
            if ok:
                self.dot_xyz.append(value)
            else:
                print(f"Selection for Dot {axis} canceled.")
                return

        # 检查是否所有控制点都已选择
        if len(self.dot_xyz) == 3:
            print(f"Selected control dot coordinates: {self.dot_xyz}")
        else:
            print("Control dot selection incomplete.")

    def resetFunction(self):
        """ 重置功能槽函数 """
        self.initializeVTK()
        self.showAll()

    def quitFunction(self):
        """ 退出功能槽函数 """
        sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ffd = widget()
    ffd.show()
    ffd.irender.Initialize()
    sys.exit(app.exec_())
