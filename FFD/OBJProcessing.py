import vtk

def resizePolyData(data, resize):
    """
    通过减少顶点数量来简化 polydata

    参数:
        data (vtkPolyData): 需要被简化的 polydata
        resize (float): 目标缩减比例（从 0.0 到 1.0)

    返回:
    vtkPolyData: 简化后的 polydata。

    """

    if not (0 <= resize <= 1):
        raise ValueError("Resize value must be between 0 and 1")

    polyDataDecimate = vtk.vtkDecimatePro()
    polyDataDecimate.SetInputData(data)
    polyDataDecimate.SetTargetReduction(1-resize)
    polyDataDecimate.PreserveTopologyOff()
    polyDataDecimate.SplittingOn()
    polyDataDecimate.BoundaryVertexDeletionOn()
    polyDataDecimate.SetMaximumError(vtk.VTK_DOUBLE_MAX)
    polyDataDecimate.Update()
    return polyDataDecimate.GetOutput()


def extractColorsFromFile(filename):
    """
    从给定文件中提取颜色信息

    参数:
        filename (str): 包含颜色数据的文件。

    返回:
        list of tuple: 一个包含 RGB 颜色元组的列表。
    """
    extractedColors = []
    with open(filename, "r") as file:
        for line in file:
            lineParts = line.strip().split(" ")
            if lineParts[0] == "v" and len(lineParts) == 7:
                red, green, blue = (int(float(colorComponent) * 255) for colorComponent in lineParts[4:7])
                extractedColors.append((red, green, blue))

    return extractedColors

def applyColorsToPoints(polydata, pointColors=[]):
    """
    将 RGB 颜色应用到 VTK polydata 对象的点上

    参数:
        polydata (vtkPolyData): 要着色的 VTK polydata。
        pointColors (list of tuple): 颜色元组 (R, G, B) 的列表。

    返回:
        vtkPolyData: 已着色的 polydata。
    """
    colorArray = vtk.vtkUnsignedCharArray()
    colorArray.SetNumberOfComponents(3)
    colorArray.SetName("PointColors")

    for color in pointColors:
        red, green, blue = color
        colorArray.InsertNextTuple3(red, green, blue)

    polydata.GetPointData().SetScalars(colorArray)
    polydata.Modified()

    return polydata
