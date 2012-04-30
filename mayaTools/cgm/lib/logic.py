#=================================================================================================================================================
#=================================================================================================================================================
#	logic - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for list stuff
# 
# ARGUMENTS:
# 	rigging
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#=================================================================================================================================================

import maya.cmds as mc

from cgm.lib import (locators,
                     distance,
                     rigging,
                     dictionary,
                     guiFactory)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Logic
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class axisFactory():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    

    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    def __init__(self,input):
        self.axisString = ''
        self.axisVector = ''
        
        shortStringsDict = {'x':'x+','y':'y+','z':'z+'}
        stringToVectorDict = {'x+':[1,0,0],'x-':[-1,0,0],'y+':[0,1,0],'y-':[0,-1,0],'z+':[0,0,1],'z-':[0,0,-1]}
        vectorToStringDict = {'[1,0,0]':'x+','[-1,0,0]':'x-','[0,1,0]':'y+','[0,-1,0]':'y-','[0,0,1]':'z+','[0,0,-1]':'z-'}
        
        if input in shortStringsDict.keys():
            self.axisString = shortStringsDict.get(input)
            self.axisVector = stringToVectorDict.get(self.axisString)
            
        elif input in stringToVectorDict.keys():
            self.axisVector = stringToVectorDict.get(input)
            self.axisString = input
            
        elif str(input) in vectorToStringDict.keys():
            self.axisString = vectorToStringDict.get(str(input))
            self.axisVector = stringToVectorDict.get(self.axisString)
            
        elif ' ' in list(str(input)):
            splitBuffer = str(input).split(' ')
            newVectorString =  ''.join(splitBuffer)
            self.axisString = vectorToStringDict.get(newVectorString)
            self.axisVector = stringToVectorDict.get(self.axisString)
            
        else:
            print input
            print str(input)
            self.axisString = False
            self.axisVector = False
            guiFactory.warning("'%s' not recognized"%input)
            

            

        
        
        
def returnLocalUp(aimVector):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a local aim direction

    ARGUMENTS:
    aimVector(string) = '[1,0,0]'

    RETURNS:
    direction(list) - [0,0,0]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    localUpReturn = {'[1,0,0]':[0,1,0],'[-1,0,0]':[0,-1,0],'[0,1,0]':[0,0,1],'[0,-1,0]':[0,0,-1],'[0,0,1]':[0,1,0],'[0,0,-1]':[0,-1,0]}
    joinBuffer = ','.join(map(str,aimVector))
    buffer =   ('%s%s%s' % ("[",joinBuffer,"]"))
    return localUpReturn.get(buffer)

def returnLocalAimDirection(rootObj,aimObj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a local aim direction

    ARGUMENTS:
    rootObj(string)
    aimObj(string)

    RETURNS:
    direction(list) - [0,0,0]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    directionalLocArray = []
    locGroups = []
    directions = ['+x','-x','+y','-y','+z','-z']
    returnDirections = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]
    distanceBuffer = distance.returnDistanceBetweenObjects(rootObj,aimObj)

    #distanceValues = distanceBuffer /2
    cnt = 0
    for direction in directions:
        locBuffer = locators.locMeObject(rootObj)
        locBuffer = mc.rename(locBuffer,(locBuffer+'_'+str(cnt)))
        locGroups.append(rigging.groupMeObject(locBuffer))
        directionBuffer = list(direction)
        if directionBuffer[0] == '-':
            mc.setAttr((locBuffer+'.t'+directionBuffer[1]), -1)
        else:
            mc.setAttr((locBuffer+'.t'+directionBuffer[1]), 1)
        directionalLocArray.append(locBuffer)
        cnt+=1
    closestLoc = distance.returnClosestObject(aimObj, directionalLocArray)
    matchIndex = directionalLocArray.index(closestLoc)

    for grp in locGroups:
        mc.delete(grp)

    return returnDirections[matchIndex]


def returnLinearDirection(rootObj,aimObj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a linear direction

    ARGUMENTS:
    rootObj(string)
    aimObj(string)

    RETURNS:
    direction(string) - 'x,y,z,-x,-y,-z'
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #make locators in case we're using something like joints
    axis = {0:'x',1:'y',2:'z'}
    rootPos = mc.xform (rootObj,q=True, ws=True, rp=True)
    aimPos = mc.xform (aimObj,q=True, ws=True, rp=True)

    rawDifferenceList = [(aimPos[0]-rootPos[0]),(aimPos[1]-rootPos[1]),(aimPos[2]-rootPos[2])]
    absDifferenceList = [abs(rawDifferenceList[0]),abs(rawDifferenceList[1]),abs(rawDifferenceList[2])]

    biggestNumberIndex = absDifferenceList.index(max(absDifferenceList))
    direction = axis.get(biggestNumberIndex)
    if rawDifferenceList[biggestNumberIndex] < 0:
        return ('%s%s' %('-',direction))
    else:
        return (direction)


def returnHorizontalOrVertical(objList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns if a set of objects is laid out vertically or horizontally

    ARGUMENTS:
    objList(list)

    RETURNS:
    direction(string) - horizontal/vertical
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #make locators in case we're using something like joints
    locList = []
    for obj in objList:
        locList.append(locators.locMeObject(obj))
    box = distance.returnBoundingBoxSize(locList)

    maxIndex = box.index(max(box))
    if maxIndex == 1:
        generalDirection = 'vertical'
    else:
        generalDirection = 'horizontal'

    #delete our locators
    for loc in locList:
        mc.delete(loc)
    return generalDirection
