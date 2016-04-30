"""
os_Utils
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
# From Python =============================================================
import re
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.OpenMaya as OM

class Point(OM.MPoint, object):
    '''
    Subclass of MPoint, use a nicer str() and repr()
    
    acknowledgement:
    NateH - http://forums.cgsociety.org/archive/index.php?t-904223.html
    
    '''
    def __init__(self, x=0, y=0, z=0):
        #allow point to take a single tuple, or 3 floats, or wrap an existing MVector
        if isinstance(x, OM.MPoint) or isinstance(x, OM.MVector):
            super(Point, self).__init__(x)
            return

        if isinstance(x, tuple) or isinstance(x, list):
            super(Point, self).__init__(x[0], x[1], x[2])
        else:
            OM.MPoint.__init__(self, x, y, z)

    def __str__(self):
        return '(%g, %g, %g)'%(self.x, self.y, self.z)
    def __repr__(self):
        return '<<MPoint (%g, %g, %g)>>'%(self.x, self.y, self.z)

    def asTuple(self):
        return (self.x, self.y, self.z)
    
    
def mObjectArray_get_list(mArray = None):
    result = []

    for i in xrange(mArray.length()):
        objFn = OM.MFnDagNode( mArray[i])
        result.append( objFn.fullPathName() )
        
    return result

def mObject_getNameString(mObject = None):
    result = []
    
    objFn = OM.MFnDagNode( mObject )
    return objFn.fullPathName()


   