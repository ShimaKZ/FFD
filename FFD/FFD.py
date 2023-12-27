import numpy as np
import copy
class objReader(object):
    "Load a .obj file"
    def __init__(self, filename):
        self.vertices=[]
        self.faces=[]
        self.tmp=[]
        for line in open(filename,"r"):
            if line.startswith("#"):
                continue
            values=line.split()
            if not values:
                continue
            if(values[0]=='v'):
                v=[float(x) for x in values[1:4]]
                t=[float(x) for x in values[4:]]
                self.vertices.append(v)
                self.tmp.append(t)
            elif(values[0]=='f'):
                self.faces.append([int(x) for x in values[1:4]])


class FFD(object):
    "handler of FFD algorithm"
    def __init__(self,pointNumX,pointNumY,pointNumZ,objFile,points):
        self.controlPointNumX=pointNumX
        self.controlPointNumY=pointNumY
        self.controlPointNumZ=pointNumZ
        # Number of control points of each dimension
        self.objFile=objFile
        self.initialPoints=points
        self.B=[lambda x:(1 - x) ** 3 / 6,
                lambda x:(3 * x ** 3 - 6 * x ** 2 + 4) / 6,
                lambda x: (-3 * x ** 3 + 3 * x ** 2 + 3 * x + 1) / 6,
                lambda x:x ** 3 / 6
               ]
    def initFFD(self):
        tmpPoints=copy.deepcopy(self,initialPoints)
        [self.minX,self.minY,self.minZ,self.maxX,self.maxY,self.maxZ]=[tmpPoints[0][0],tmpPoints[0][1],tmpPoints[0][2],tmpPoints[0][0],tmpPoints[0][1],tmpPoints[0][2]]
        for points in tmpPoints:
            self.minX=min(self.minX,points[0])
            self.maxX=max(self.maxX,points[0])
            self.minY=min(self.minY,points[1])
            self.maxY=max(self.maxY,points[1])
            self.minZ=min(self.minZ,points[2])
            self.maxZ=max(self.maxZ,points[2])
        del tmptmpPoints
        self.spaceX=(self.maxX-self.minX)/(self.controlPointNumX-1)
        self.spaceY=(self.maxY-self.minY)/(self.controlPointNumY-1)
        self.spaceZ=(self.maxZ-self.minZ)/(self.controlPointNumZ-1)
        # The space between the nearest control points of each dimension
        self.controlPointsOffset=[[[np.array([0.,0.,0.])for z in range(self.controlPointNumZ)]for y in range(self.controlPointNumY)] for x in range(self.controlPointNumX)]
        self.controlPointsPosition=[[[np.array([self.minX + x * self.spaceX,self.minY + y * self.spaceY, self.minZ + z * self.spaceZ]) for z in range(self.controlPointNumZ)]for y in range(self.controlPointNumY)] for x in range(self.controlPointNumX)]
        self.objectPoints = {}

        for x in range(self.controlPointNumX):
            for y in range(self.controlPointNumY):
                for z in range(self.controlPointNumZ):
                    self.objectPoints[(x, y, z)] = set()
        for index in range(len(self.initialPoints)):
            [x,y,z]=self.initialPoints[index]
            i = int((x - self.minX) / self.spaceX)
            j = int((y - self.minY) / self.spaceY)
            k = int((z - self.minZ) / self.spaceZ)
            self.objectPoints[i,j,k].add((index,x,y,z))
    def T_local(self, objectPoint):
        [x,y,z]=objectPoint
        [posX,posY,posZ]=[(x - self.minX) / self.spaceX,(y - self.minY) / self.spaceY,(z - self.minZ) / self.spaceZ]
        [i,j,k]=[int(posX)-1,int(posY)-1,int(posZ)-1]
        [u,v,w]=[posX-(i+1),posY-(j+1),posZ-(k+1)]
        res = np.array([0., 0., 0.])
        for l in range(4):
            if i+l>=0 and i+l<self.controlPointNumX:
                for m in range(4):
                    if j+m>=0 and j+m<self.controlPointNumY:
                        for n in range(4):
                            if k+n>=0 and k+n<self.controlPointNumZ:
                                res+=self.B[l](u) * self.B[m](v) * self.B[n](w) * self.controlPointsOffset [i + l][j + m][k + n]
        return res
    def cacheReset(self):
        del self.cache
        self.cache={}
    def cacheUpdate(self,id,position):
        self.cache[id]=position
    def updateControlPoint(self):
        
        for (u, v, w), newPosition in self.cache.items():
            self.controlPointsOffset [u][v][w] = newPosition - self.controlPointsPosition [u][v][w]