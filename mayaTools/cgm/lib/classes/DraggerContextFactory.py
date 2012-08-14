import maya.cmds as mc
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
from zooPyMaya import apiExtensions

from cgm.lib import (locators,
                     guiFactory)
import os


    
def pressPoint():
    LocatePoint()
    

class ContextualPick(object):
    def __init__(self,name = 'cgmDraggerContext', *a,**kw):
        """ 
        Initializes a draggerContext object for use with other tools
        
        Arguments:
        undoMode --
        projection --
        plane --
        space --
        cursor
        drag -- Whether to enable drag mode
        """
        undoMode = kw.pop('undoMode','step')
        projection = kw.pop('projection','plane')
        plane = kw.pop('plane',[1,0,0])
        self.space = kw.pop('space','world')
        cursor = kw.pop('cursor','crossHair')
        drag = kw.pop('drag',False)
        
        if mc.draggerContext(name,query=True,exists=True): # if it exists, delete it
            mc.deleteUI(name)    
        
        self.name = name
        
        imageFilePath = ('cgmDefault.png')
        mc.draggerContext( self.name,  image1 = imageFilePath,
                           undoMode = undoMode, projection = projection, space = self.space,
                           initialize = self.initialPress,
                           pressCommand = self.press,
                           *a,**kw )
        
        if projection == 'plane': mc.draggerContext(self.name,e=True, plane = plane)# if our projection is 'plane', set the plane
        if drag:mc.draggerContext(self.name,e=True, dragCommand = self.drag)# If drag mode, turn it on

        self.setTool()
        
    def finalize(self):
        mc.setToolTo('selectSuperContext')
        mc.selectMode(object=True)
        
    def press(self):
        self.anchorPoint = mc.draggerContext(self.name, query=True, anchorPoint=True)
        self.modifier = mc.draggerContext(self.name, query=True, modifier=True)
        self.button = mc.draggerContext(self.name, query=True, button=True)
        self.returnList.append(self.anchorPoint)
        
        guiFactory.report("Position is %s in '%s' space"%(self.anchorPoint,self.space))
        
    def drag(self):
        self.dragPoint = mc.draggerContext(self.name, query=True, dragPoint=True)
        self.button = mc.draggerContext( self.name, query=True, button=True)
        self.modifier = mc.draggerContext( self.name, query=True, modifier=True)
        
        self.returnList.append(self.dragPoint)

    def initialPress(self):
        self.returnList = []
        mc.warning("Select the first point")
         
    def dropTool(self):
        mc.setToolTo('selectSuperContext')        
        mc.selectMode(object=True) 
        return self.returnList
        
    def setTool(self):
        mc.setToolTo(self.name)
        
class LocatePoint(ContextualPick):
    '''Creates the tool and manages the data'''

    def __init__(self,drag = False, plane = [0,1,0], *a,**kw
                 ):
        
        ContextualPick.__init__(self, drag = drag, plane = plane, *a,**kw )
        
    
    def press(self):
        ContextualPick.press(self)
        self.returnList.append(self.anchorPoint)
        nameBuffer = mc.spaceLocator()
        mc.move (self.anchorPoint[0],self.anchorPoint[1],self.anchorPoint[2], nameBuffer[0]) 
        return self.anchorPoint
        
    def release(self):pass
    
    def drag(self):    
        ContextualPick.drag(self)        
        print ("Drag: " + str(self.dragPoint) + "  Button is " + str(self.button) + "  Modifier is " + self.modifier + "\n")
        nameBuffer = mc.spaceLocator()
        mc.move (self.dragPoint[0],self.dragPoint[1],self.dragPoint[2], nameBuffer[0])           


class Testing(ContextualPick):
    '''Creates the tool and manages the data'''

    def __init__(self,drag = False,space = 'screen',projection = 'viewPlane', *a,**kw
                 ):
        
        ContextualPick.__init__(self, drag = drag, space = space, projection = projection, *a,**kw )
        
    
    def press(self):
        ContextualPick.press(self)
        self.returnList.append(self.anchorPoint)
        print ("Press: " + str(self.anchorPoint) + "  Button is " + str(self.button) + "  Modifier is " + self.modifier + "\n")

        return self.anchorPoint
        
    def release(self):pass
    
    def drag(self):    
        ContextualPick.drag(self)        
        print ("Drag: " + str(self.dragPoint) + "  Button is " + str(self.button) + "  Modifier is " + self.modifier + "\n")

def screenToWorld(startX,startY):
    maya3DViewHandle = OpenMayaUI.M3dView()
    activeView = maya3DViewHandle.active3dView()
    vertexMPoint = OpenMaya.MPoint()
    vertexMVector = OpenMaya.MVector()

    #activeView.worldToView(vertexMPoint, xPosShortPtr, yPosShortPtr,vecDirDoublePtr )
    activeView.viewToWorld(startX, startY, vertexMPoint, vertexMVector )
    pos = vertexMPoint.get()
    vec = vertexMVector.get()
    
    posUtil = OpenMaya.MScriptUtil()
    vecUtil = OpenMaya.MScriptUtil()
    
    posTranslate = posUtil.asDouble3Ptr(vertexMPoint)
    vecTranslate = vecUtil.asDoublePtr(vertexMVector)
    
    
    return pos,vec
        
        
        

"""
- Captured a mouse click event within a Context command
- Ran a MGlobal::selectFromScreen on the mouse coords generated by the event
- Used M3dView::active3dView().viewToWorld to convert 2D screen coords to 3D world coords
This returns source and direction vectors
- ran a MFnMesh.closestIntersection() using my vectors
- Grabbed the hitPoint generated by this method to get final 3D pos (remember to use MDistance::internalToUI() )
"""
"""
def worldToScreen(x,y,z):
    import maya.OpenMayaUI as OpenMayaUI
    import maya.OpenMaya as OpenMaya
    maya3DViewHandle = OpenMayaUI.M3dView()
    activeView = maya3DViewHandle.active3dView()
    vertexMPoint = OpenMaya.MPoint(x,y,z)
    
    # Build utilities. maya crashes if you don't in 2011...
    xUtil = OpenMaya.MScriptUtil()
    yUtil = OpenMaya.MScriptUtil()
    vecUtil = OpenMaya.MScriptUtil()
    
    xPosShortPtr = xUtil.asShortPtr()
    yPosShortPtr = yUtil.asShortPtr()
    vecDirDoublePtr = vecUtil.asDouble3Ptr()
    
    #activeView.worldToView(vertexMPoint, xPosShortPtr, yPosShortPtr,vecDirDoublePtr )
    activeView.worldToView(vertexMPoint, xPosShortPtr, yPosShortPtr,vecDirDoublePtr )
    xPos = xUtil.getShort(xPosShortPtr)
    yPos = yUtil.getShort(yPosShortPtr)
    vec = vecUtil.getDouble(yPosShortPtr)
    
    return xPos,yPos,vec
    
worldToScreen(1,0,0)



import maya.OpenMaya as om
import maya.OpenMayaUI as omui

3dView.viewToWorld(24,38)

m3d = omui.M3dView()
omui.M3dView.getM3dViewFromModelPanel('modelPanel4', m3d)
msX = om.MScriptUtil()
msY = om.MScriptUtil()
xPtr = msX.asShortPtr()
yPtr = msY.asShortPtr()"""