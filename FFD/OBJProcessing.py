import vtk

def resizePolyData(data, resize):
    """
    Simplify the poly data by reducing the number of vertices.

    Args:
        data (vtkPolyData): The polydata to be simplified.
        resize (float): The target reduction proportion (0.0 to 1.0).
    
    Returns:
        vtkPolyData: The simplified polydata.
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
    """Extracts color information from a given file.

    Args:
        filename (str): the file containing color data.

    Returns:
        list of tuple: A list of RGB color tuples.
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
    """Apply RGB colors to the points in a VTK polydata object.

    Args: 
        polydata (vtkPolyData): The VTK polydata to color.
        pointColors (list of tuple): List of color tuples (R, G, B).

    Returns:
        vtkPolyData: The colored polydata.
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
