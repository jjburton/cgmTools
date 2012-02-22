#=================================================================================================================================================
#=================================================================================================================================================
#	geo - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with attributes
# 
# REQUIRES:
# 	Maya
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.joshburton.com
# 	Copyright 2011 Josh Burton - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
#   
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel

import re


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Create Tools 
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     
def createPolyFromPosList(posList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a poly from position list
    
    REQUIRES:
    posList(string) - list of positions
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    polyBuffer = mc.polyCreateFacet(p = posList,hole = False)
    newFaceVerts = (mc.ls ([polyBuffer[0]+'.vtx[*]'],flatten=True))
    for vert in newFaceVerts:
        cnt = newFaceVerts.index(vert)
        pos = posList[cnt]
        mc.xform(vert,t = [pos[0],pos[1],pos[2]],ws=True)
    return polyBuffer[0]

