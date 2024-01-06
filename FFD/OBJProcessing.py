import vtk

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
