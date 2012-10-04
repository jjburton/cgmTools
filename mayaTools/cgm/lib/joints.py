#=================================================================================================================================================
#=================================================================================================================================================
#	joints - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with joints
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
#   0.11 = 4/2/2011 - added documentation for all the scripts written during River Monsters gig
#=================================================================================================================================================

import maya.cmds as mc

from cgm.lib import rigging
from cgm.lib import locators
from cgm.lib import names
from cgm.lib import search
from cgm.lib import distance
from cgm.lib import attributes
from cgm.lib import nodes
from cgm.lib import lists
from cgm.lib.classes import NameFactory 
from cgm.lib import curves

def connectJointScalingBlendToMasterScale(mainDriverAttribute,jointList):
        import attributes
        import nodes
        for joint in jointList:
                # Get driver
                jointDriver = attributes.returnDriverObject(joint+'.scale')
                if jointDriver:
                        mdNode = nodes.createNamedNode((joint + '_mdNode'),'multiplyDivide')
                        mc.setAttr((mdNode + '.operation'),1)

                        attributes.doConnectAttr((jointDriver+'.scale'),(mdNode + '.input1'))
                        attributes.doConnectAttr((mainDriverAttribute),(mdNode+'.input2'))
                        attributes.doConnectAttr((mdNode+'.output'),(joint+'.scale'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Naming Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def renameJointChainList (jointList, startJointName, interiorJointRootName):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Script to rename a joint chain list

        ARGUMENTS:
        jointList(list) - list of joints in order
        startJointName(string) - what you want the root named
        interiorJointRootName(string) - what you want the iterative name to be

        RETURNS:
        newJoints(list)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        newJointList = []
        jntBuffer = mc.rename (jointList[0],startJointName)
        newJointList.append (jntBuffer)
        cnt = 1
        for jnt in jointList[1:-1]:
                jntBuffer = mc.rename (jnt,('%s%s%02i' % (interiorJointRootName,'_',cnt)))
                newJointList.append (jntBuffer)
                cnt += 1
        jntBuffer = mc.rename (jointList[-1], (interiorJointRootName+'_end'))
        newJointList.append (jntBuffer)
        return newJointList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utility Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def toggleJntLocalAxisDisplay (jnt):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Toggles the display of a joint's local axis

        ARGUMENTS:
        jnt(string) - the joint you wanna mess with

        RETURNS:
        Nada
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        displayAttr = (jnt+'.displayLocalAxis')
        if (mc.getAttr (displayAttr)) == 0:
                mc.setAttr (displayAttr,1)
        else:
                mc.setAttr (displayAttr,0)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def setRotationOrderOnJoint (jnt, ro):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Set's the rotation order on a joint

        ARGUMENTS:
        jnt(string) - the joint to be fixed
        ro(string) - the rotation order you'd like used

        RETURNS:
        Success(True/False)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        #Checks for success rotation order
        successRO = 'True'
        rotationOrderOptions = ['xyz','yzx','zxy','xzy','yxz','zyx']
        if not ro in rotationOrderOptions:
                print (ro + ' is not a success rotation order. Expected one of the following:')
                print rotationOrderOptions
                successRO = 'False'
        else:  
                mc.joint (jnt, e=True, rotationOrder= ro)
        return successRO

# #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def orientJoint (jointToOrient, orientation = 'xyz', up = 'none'):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Orients a joint

        ARGUMENTS:
        jointToOrient(string) - Joint to orient.
        orientation(string) - how you want it oriented
        up(string) - what's the joint's up vector

        RETURNS:
        Success(True/False)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        success = True
        orientationOptions = ['xyz','yzx','zxy','xzy','yxz','zyx','none']
        secondaryAxisOptions = ['xup','xdown','yup','ydown','zup','zdown','none']
        if not orientation in orientationOptions:
                print (orientation + ' is not an acceptable orientation. Expected one of the following:')
                print orientationOptions
                return False
        if not up in secondaryAxisOptions:
                print (up + ' is not an acceptable second axis. Expected one of the following:')
                return False
        else:
                childJoint = mc.listRelatives(jointToOrient, type="joint", c=True)
                if childJoint != None:
                        if len(childJoint) > 0:
                                mc.makeIdentity(jointToOrient,apply=True,r = True)
                                mc.joint (jointToOrient, e=True, orientJoint= orientation, secondaryAxisOrient= up)

                else:
                        #Child joint. Use the same rotation as the parent.
                        parentJoint = mc.listRelatives(jointToOrient, type="joint", p=True) 		
                        if parentJoint != None :
                                if len(parentJoint) > 0:
                                        mc.delete(mc.orientConstraint(parentJoint[0], jointToOrient, w=1, o=(0,0,0)))
                                        freezeJointOrientation(jointToOrient)
        return success

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def freezeJointOrientation(jointToOrient):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        ACKNOWLEDGE:
        Jose Antonio Martin Martin - JoseAntonioMartinMartin@gmail.com

        DESCRIPTION:
        Freezes the joint orientation.

        ARGUMENTS:
        jointToOrient(string - Joint to orient.

        RETURNS:
        Nothing
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        mc.joint(jointToOrient, e=True, zeroScaleOrient=True)
        mc.makeIdentity(jointToOrient, apply=True, t=0, r=1, s=0, n=0)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def orientJointChain (jointList, orientation, up):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Orients a chain of joints with the appropriate inputs

        ARGUMENTS:
        jointList(list) - list of joints
        orientation(string) - your chosen orienation for the joints
        up(string) - what should be considered up for the joints

        RETURNS:
        Nothing
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """    
        for jointToOrient in jointList:
                orientJoint (jointToOrient, orientation, up)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def setGoodJointRadius(jointList,multiplier):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Guesses a good joint radius value and uses the multiplier to tweak it

        ARGUMENTS:
        jointList(list) - list of locators
        multiplier(float/integer) - just what it sounds like

        RETURNS:
        None
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        avDist = (distance.returnDistanceBetweenObjects (jointList[0],jointList[-1])/6)
        for jnt in jointList:
                mc.setAttr ((jnt+'.radi'),(avDist*multiplier))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Duplication Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def duplicateChainInPlace(jointList):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        asdf

        ARGUMENTS:
        asdf(list) - list of the objects you want joints created at

        RETURNS:
        asdf
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        dupJointsBuffer = mc.duplicate(jointList,po=True,rc=True)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def duplicateJoint (joint):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        asdf

        ARGUMENTS:
        asdf(list) - list of the objects you want joints created at

        RETURNS:
        asdf
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        mc.duplicate (joint, parentOnly=True)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Joint Curve Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createJointsFromCurve(curve, name, divideSpans = 0):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Creates joint chain from a curve

        ARGUMENTS:
        curve(string) - the curve
        name(string) - name you want it iterate on
        divideSpans(int) - number of roll joints you want, 0 is default

        RETURNS:
        jointList(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        cnt = 0
        jointChain = []
        print divideSpans
        if mc.objExists (curve):
                locs = locators.locMeCVsOnCurve(curve)
                jointPositions = []
                #>>> Divide stuff
                if divideSpans > 0:
                        """ if we're gonna divide stuff, we need to get our pairs"""
                        pairs = lists.parseListToPairs(locs)
                        for pair in pairs:
                                """ make a new curve"""
                                pairCurve = (curves.curveFromObjList(pair))
                                """rebuild it our division number """
                                print pairCurve
                                mc.rebuildCurve (pairCurve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=(divideSpans+1), d=1, tol=0.001)
                                """ get the locs for the pair curve and record the postions"""
                                pairLocs = locators.locMeCVsOnCurve(pairCurve)
                                if divideSpans == 1:
                                        """  rebuilding curves for only two segments doesn't work right so we wanna just grab the cvs we want"""
                                        firstMidLastPairLocs = lists.returnFirstMidLastList(pairLocs)
                                        for loc in firstMidLastPairLocs:
                                                jointPositions.append(distance.returnClosestUPosition (loc,curve)) 
                                        for loc in pairLocs:
                                                mc.delete(loc)
                                else:
                                        for loc in pairLocs:
                                                jointPositions.append(distance.returnClosestUPosition (loc,curve))
                                                mc.delete(loc)
                                mc.delete(pairCurve)
                else:
                        for loc in locs:
                                """ get our positions via locators and distance nodes """
                                jointPositions.append(distance.returnClosestUPosition (loc,curve))
                """ Remove the duplicate positions"""
                print jointPositions
                jointPositions = lists.returnPosListNoDuplicates(jointPositions)
                print jointPositions 
                #>>> Actually making the joints
                for pos in jointPositions:
                        currentJnt = ('%s%s%i' % (name,'_',cnt))
                        """Inserts our new joint, names it and positions it"""
                        mc.joint (p=(pos[0],pos[1],pos[2]),n=currentJnt)
                        """Sets the radius of the joint and adds it to our return joint list"""
                        jointChain.append (currentJnt)
                        cnt+=1

                for loc in locs:
                        mc.delete(loc)
                success = True
                return jointChain
        else:
                print ('Curve does not exist')
                success = False
                return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def createJointsFromCurveBAK (curve, name):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Creates joint chain from a curve

        ARGUMENTS:
        curve(string) - the curve
        name(string) - name you want it iterate on

        RETURNS:
        jointList(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        # need to rebuild curve?
        cnt = 0
        cvList = (mc.ls ([curve+'.cv[*]'],flatten=True))
        jointChain = []
        if mc.objExists (curve):
                for cv in cvList:
                        jointPos = mc.pointPosition (cv,world=True)
                        """Inserts our new joint, names it and positions it"""
                        currentJnt = ('%s%s%i' % (name,'_',cnt))
                        jointChain.append(mc.joint (p=(jointPos[0],jointPos[1],jointPos[2]),n=currentJnt))
                        """Sets the radius of the joint and adds it to our return joint list"""
                        #jointChain.append (currentJnt)
                        cnt+=1
                        success = True
                return jointChain
        else:
                print ('Curve does not exist')
                success = False
                return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def createCurveFromJoints (startJoint):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Creates a curve from a chain of joints

        ARGUMENTS:
        startJoint(string) - root of the chain you wanna curv...iate

        RETURNS:
        curve(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        """ return chain joints"""
        heirarchyJoints = []
        heirarchyJoints.append (startJoint)
        childrenJoints = search.returnChildrenJoints (startJoint)
        for joint in childrenJoints:
                heirarchyJoints.append(joint)
        """ return positional data for curve creation """
        posList = []
        for jnt in heirarchyJoints:
                posList.append(distance.returnWorldSpacePosition(jnt))
        """ make curve """
        crvName = mc.curve (d=1, p = posList , os=True, n=(startJoint+'_crv'))
        return crvName
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Joint Chain Creation Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createJointsFromPosListName (jointPositions,name = 'joint'):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Draws joints from input parameters

        ARGUMENTS:
        jointPositions(list) - an list of vector positions
        name(string) - name you want it iterate on
        suffix(string) - the suffix you'd like used

        RETURNS:
        jointList(list)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        j= 0
        listOfJoints = []
        for pos in jointPositions:        
                jointName = '%s%s%02i' % (name,'_',j,)
                mc.joint (p = (pos[0], pos[1], pos[2]), n=jointName) 
                #adds the name of the joint to our joint list
                listOfJoints.append (jointName)
                j += 1
        return listOfJoints
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def createJointsFromTemplateObjects(objectList):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        asdf

        ARGUMENTS:
        asdf

        RETURNS:
        asdf
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        cleanNamesList = []
        objectPositionList = []
        for obj in objectList:
                tempPos = mc.xform (obj,q=True, ws=True, rp=True)
                nameBuffer = NameFactory.returnUniqueGeneratedName(obj,'cgmType')
                objectPositionList.append (tempPos)
                cleanNamesList.append (nameBuffer)
        jointListBuffer=[]
        j = 0
        for pos in objectPositionList:
                print pos[0]
                jointListBuffer.append(mc.joint(p = (pos[0], pos[1], pos[2]), n=j))
                #listOfJoints.append (joint)
                j+=1
        return jointListBuffer
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createJointsFromPosListNameIterate (jointPositions, name, suffix):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Draws joints from input parameters

        ARGUMENTS:
        jointPositions(list) - an list of vector positions
        name(string) - name you want it iterate on
        suffix(string) - the suffix you'd like used

        RETURNS:
        jointList(list)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        j= 0
        listOfJoints = []
        for pos in jointPositions:        
                jointName = '%s%s%02i%s%s' % (name,'_',j,'_',suffix)
                mc.joint (p = (pos[0], pos[1], pos[2]), n=jointName) 
                #adds the name of the joint to our joint list
                listOfJoints.append (jointName)
                j += 1
        return listOfJoints
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 

def createJointsFromPosListNameWithNameList (jointPositions, nameList, suffix):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Draws joints from input parameters

        ARGUMENTS:
        jointPositions(list) - a list of transform positions
        nameListlist) - list of names you'd like the joints named as
        suffix(string) - the suffix you'd like used

        RETURNS:
        jointList(list)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        j= 0
        listOfJoints = []
        for pos in jointPositions:        
                jointName = '%s%s%s' % (nameList[j],'_',suffix)
                mc.joint (p = (pos[0], pos[1], pos[2]), n=jointName) 
                listOfJoints.append (jointName)
                j += 1
        return listOfJoints
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def createJointsFromObjPositions (objList, suffix):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Draws joints from object positions

        ARGUMENTS:
        objList(list) - list of the objects you want joints created at
        suffix(string) - the suffix you'd like for the joints

        RETURNS:
        jointList(list)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        cleanNamesList = []
        jointPositions = []
        for obj in objList:
                tempPos = mc.xform (obj,q=True, ws=True, rp=True)
                nameBuffer = names.stripSuffixObj (obj)
                jointPositions.append (tempPos)
                cleanNamesList.append (nameBuffer)
        listOfJoints = createJointsFromPosListNameWithNameList (jointPositions, cleanNamesList, suffix)
        return listOfJoints
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def createJointsFromObjects (objects, name, suffix):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Created joints from a locator list

        ARGUMENTS:
        objects(list) - list of objects
        name(string) - name of the joints
        suffix(string) - suffix for the joints

        RETURNS:
        jointList(list)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        l = 0
        objectPositionList = []
        for obj in objects:
                tempPos = mc.xform (obj,q=True, ws=True, rp=True)
                objectPositionList.append (tempPos)
                l += 1
        listOfJoints = createJointsFromPosListNameIterate (objectPositionList, name, suffix)
        return listOfJoints
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Surface Joint Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def createJointChainsFromNurbsSurface (name,surface,chainMode=0,directionMode=0,reverse=False):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Created joint chains from a lofted surface

        ARGUMENTS:
        name(string) - your root name for the joints	
        surface(string) - the lofted surface to be used
        chainMode -   0 - mid only
                      1 - ends only
                      2 - mid and ends only
                      3 - odds only
                      4 - evens only
                      5 - all except start and end anchors
                      6 - all
          directionMode - 0 - with surface flow
                          1 - against the grain 
          reverse(bool) - True/False - if you want to reverse the joint flow

        RETURNS:
        jointChainsList(nested list)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        mc.select(cl=True)
        """ Makes a series of joints chains on a nurbs surface with the input direciton mode of 1 or 2 as well as a True/False reverse option"""
        cvList = (mc.ls ([surface+'.cv[*][*]'],flatten=True))
        #>>>>>Figuring out which direction to make our chains from
        cvListFirstTerm = []
        cvListSecondTerm = []
        firstTermCharacterSearchList = []
        secondTermCharacterSearchList = []
        for cv in cvList:
                cvBuffer = search.returnCVCoordsToList(cv)
                cvListFirstTerm.append(cvBuffer[0])
                cvListSecondTerm.append(cvBuffer[1])
        #Clean up our lists of cv parts -----------Great info for other places
        cleanFirstTermCVList = lists.returnListNoDuplicates(cvListFirstTerm)
        cleanSecondTermCVList = lists.returnListNoDuplicates(cvListSecondTerm)
        #pick some chain positions to make chains from
        chainToMakeBuffer=[]
        chainsToMakeBuffer=[]
        cnt=0
        """ direction mode stuff """
        if directionMode == 0:
                """ pop out the second and second to last items cause we don't want joints on those extra cv's"""
                cleanSecondTermCVList.remove(cleanSecondTermCVList[1])
                cleanSecondTermCVList.remove(cleanSecondTermCVList[-2])
                for firstTerm in cleanFirstTermCVList:
                        for secondTerm in cleanSecondTermCVList:
                                chainToMakeBuffer.append ('%s%s%i%s%i%s' % (surface,'.cv[',int(firstTerm),'][',int(secondTerm),']'))
                        chainsToMakeBuffer.append (chainToMakeBuffer)
                        chainToMakeBuffer=[]
        if directionMode == 1:
                cleanFirstTermCVList.remove(cleanFirstTermCVList[1])
                cleanFirstTermCVList.remove(cleanFirstTermCVList[-2])
                for secondTerm in cleanSecondTermCVList:
                        for firstTerm in cleanFirstTermCVList:
                                chainToMakeBuffer.append ('%s%s%i%s%i%s' % (surface,'.cv[',int(firstTerm),'][',int(secondTerm),']'))
                        chainsToMakeBuffer.append (chainToMakeBuffer)
                        chainToMakeBuffer=[]
        """ reverse mode stuff """
        if reverse == True:
                for chain in chainsToMakeBuffer:
                        chain.reverse()
        """ accounts for chainMode """
        chainBuffer = lists.cvListSimplifier(chainsToMakeBuffer,chainMode)
        chainsToMakeBuffer = chainBuffer
        """ making the joints """
        jntCnt=0
        chainCnt=1                                         
        jointChainBuffer = []
        jointChainsBuffer = []
        for chain in chainsToMakeBuffer:
                for cv in chain:
                        jointPos = mc.pointPosition (cv,world=True)
                        """Inserts our new joint, names it and positions it"""
                        currentJnt = ('%s%s%i%s%i' % (name,'_',chainCnt,'_',jntCnt))
                        mc.joint (p=(jointPos[0],jointPos[1],jointPos[2]),n=currentJnt)
                        """adds it to our return joint list"""
                        jointChainBuffer.append (currentJnt)
                        jntCnt+=1
                jointChainsBuffer.append (jointChainBuffer)
                chainCnt +=1
                jntCnt = 0
                jointChainBuffer = []
                mc.select (clear=True)
        """ fix the joint sizes """
        for chain in jointChainsBuffer:
                setGoodJointRadius (chain,.5)
        mc.select(cl=True)
        return jointChainsBuffer

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def addSqashStretchToSurfaceChainByAttr(attributeHolder,jointChain,jointOrient):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Add squash and stretch to a joint chain that's been attached to a surface

        ARGUMENTS:
        attributeHolder(string) - what you wanna connect the squashStretch attributes to
        jointChain(list) - the joint chain to be processed (list of joints in chain)	
        jointOrient(string) - the joint orientation you want - ['xyz','yzx','zxy','xzy','yxz','zyx','none']

        RETURNS:
        None
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        #return our scale directions
        """ return our up channel """
        directionBuffer = list(jointOrient)
        direction = directionBuffer[0]
        aimDirection = direction.capitalize()
        """ and our other two """
        scale1Buffer = directionBuffer[1]
        scaleDirection1 = scale1Buffer.capitalize()
        scale2Buffer = directionBuffer[2]
        scaleDirection2 = scale2Buffer.capitalize()
        jointScaleAttrs=[]
        scaleNodes=[]
        sqrtNodes=[]
        sqStrchValueNodes=[]
        """ add our attributes"""
        for jnt in jointChain[0:-1]:
                jntScaleAttribute = attributes.addFloatAttributeToObject (attributeHolder,jnt)
                jointScaleAttrs.append(jntScaleAttribute)
        cnt=0
        for jnt in jointChain[0:-1]:
                """ breaks the connecton first to the extra scale channels and store the connection """
                worldScale1Attr = attributes.doBreakConnection((jnt+'.scale'+scaleDirection1))
                worldScale2Attr = attributes.doBreakConnection((jnt+'.scale'+scaleDirection2))


                #create the master scale node
                scaleValueBuffer = (nodes.createNamedNode((jnt+'_scaleValue'),'multiplyDivide'))
                """set to division mode"""
                mc.setAttr((scaleValueBuffer+'.operation'),2) 
                """connect the scale of the aim direction to our node"""
                mc.connectAttr(((jnt+'.scale'+aimDirection)),(scaleValueBuffer+'.input1X'))
                """ connect the aim stretch of the joint """
                mc.connectAttr(worldScale1Attr,(scaleValueBuffer+'.input2X'))


                #created the sqrt node
                sqrtNodesBuffer = (nodes.createNamedNode((jnt+'_sqrt'),'multiplyDivide'))
                """set to power"""
                mc.setAttr((sqrtNodesBuffer+'.operation'),3)
                """connect our scale node output"""
                mc.connectAttr((scaleValueBuffer+'.outputX'),(sqrtNodesBuffer+'.input1X'))
                """makes the power a square root"""
                mc.setAttr((sqrtNodesBuffer+'.input2X'),.5) 


                #create the invScale node
                invScaleBuffer = (nodes.createNamedNode((jnt+'_invScale'),'multiplyDivide'))
                """set to division mode"""
                mc.setAttr((invScaleBuffer+'.operation'),2) 
                """set the division factor"""
                mc.setAttr((invScaleBuffer+'.input1X'),1)
                """connect our sqrt output to the invScale node"""
                mc.connectAttr((sqrtNodesBuffer+'.outputX'),(invScaleBuffer+'.input2X'))


                #create pow scale node
                sqStrValueBuffer = (nodes.createNamedNode((jnt+'_sqStValue'),'multiplyDivide'))
                """set to power"""
                mc.setAttr((sqStrValueBuffer+'.operation'),3)
                """connect scale"""
                mc.connectAttr((invScaleBuffer+'.outputX'),(sqStrValueBuffer+'.input1X'))
                """connect cache"""
                mc.connectAttr(jointScaleAttrs[cnt],(sqStrValueBuffer+'.input2X'))
                sqStrchValueNodes.append(sqStrValueBuffer)
                sqrtNodes.append(sqrtNodesBuffer)
                scaleNodes.append(invScaleBuffer)


                #create the worldScale multiplier node
                worldScaleMDBuffer = (nodes.createNamedNode((jnt+'_invScaleWS'),'multiplyDivide'))
                """set to multiply mode"""
                mc.setAttr((worldScaleMDBuffer+'.operation'),1) 
                """set the division factor"""
                mc.setAttr((worldScaleMDBuffer+'.input1X'),1)
                """connect our sqrt output to the invScale node"""
                mc.connectAttr((sqStrValueBuffer+'.outputX'),(worldScaleMDBuffer+'.input1X'))
                """connect our world scale """
                mc.connectAttr(worldScale1Attr,(worldScaleMDBuffer+'.input2X'))


                #connect the scale out puts to the two other channels
                """reconnects stuff"""
                mc.connectAttr((worldScaleMDBuffer+'.outputX'),(jnt+'.scale'+scaleDirection1))
                mc.connectAttr((worldScaleMDBuffer+'.outputX'),(jnt+'.scale'+scaleDirection2))
                cnt+=1

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addSqashStretchToSurfaceChainByAnimCrv(attributeHolder,jointChain,jointOrient):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Add squash and stretch to a joint chain that's been attached to a surface

        ARGUMENTS:
        attributeHolder(string) - what you wanna connec the squashStretch attributes to
        jointChain(list) - the joint chain to be processed (list of joints in chain)	
        jointOrient(string) - the joint orientation you want - ['xyz','yzx','zxy','xzy','yxz','zyx','none']

        RETURNS:
        None
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        #return our scale directions
        """ return our up channel """
        directionBuffer = list(jointOrient)
        direction = directionBuffer[0]
        aimDirection = direction.capitalize()
        """ and our other two """
        scale1Buffer = directionBuffer[1]
        scaleDirection1 = scale1Buffer.capitalize()
        scale2Buffer = directionBuffer[2]
        scaleDirection2 = scale2Buffer.capitalize()
        """ make our attribute and declare some variables """
        if not mc.objExists ((attributeHolder+'.sqshStrch')):
                sqshStrchAttribute = attributes.addFloatAttributeToObject (attributeHolder,'sqshStrch')
        else:
                sqshStrchAttribute = (attributeHolder+'.sqshStrch')
        cnt=1
        frameCacheNodes=[]
        scaleNodes=[]
        sqrtNodes=[]
        sqStrchValueNodes=[]
        """ set our keyframes on our curve"""
        for jnt in range(len(jointChain)-1):
                mc.setKeyframe (attributeHolder,sqshStrchAttribute, time = cnt, value = 1)
                """ making the frame cache nodes """
                frameCacheNodes.append(nodes.createNamedNode(jointChain[jnt],'frameCache'))
                cnt+=1
        """ connect it """
        for cacheNode  in frameCacheNodes:
                mc.connectAttr((sqshStrchAttribute),(cacheNode+'.stream'))
        cnt=1
        """ set the vary time """
        for cacheNode in frameCacheNodes:
                mc.setAttr((cacheNode+'.varyTime'),cnt)
                cnt+=1
        """ create scale node """
        cnt=0
        for jnt in jointChain[0:-1]:
                """ breaks the connecton first to the extra scale channels and store the connection """
                worldScale1Attr = attributes.doBreakConnection((jnt+'.scale'+scaleDirection1))
                worldScale2Attr = attributes.doBreakConnection((jnt+'.scale'+scaleDirection2))


                #create the master scale node
                scaleValueBuffer = (nodes.createNamedNode((jnt+'_scaleValue'),'multiplyDivide'))
                """set to division mode"""
                mc.setAttr((scaleValueBuffer+'.operation'),2) 
                """connect the scale of the aim direction to our node"""
                mc.connectAttr(((jnt+'.scale'+aimDirection)),(scaleValueBuffer+'.input1X'))
                """ connect the aim stretch of the joint """
                mc.connectAttr(worldScale1Attr,(scaleValueBuffer+'.input2X'))


                #created the sqrt node
                sqrtNodesBuffer = (nodes.createNamedNode((jnt+'_sqrt'),'multiplyDivide'))
                """set to power"""
                mc.setAttr((sqrtNodesBuffer+'.operation'),3)
                """connect our scale node output"""
                mc.connectAttr((scaleValueBuffer+'.outputX'),(sqrtNodesBuffer+'.input1X'))
                """makes the power a square root"""
                mc.setAttr((sqrtNodesBuffer+'.input2X'),.5) 


                #create the invScale node
                invScaleBuffer = (nodes.createNamedNode((jnt+'_invScale'),'multiplyDivide'))
                """set to division mode"""
                mc.setAttr((invScaleBuffer+'.operation'),2) 
                """set the division factor"""
                mc.setAttr((invScaleBuffer+'.input1X'),1)
                """connect our sqrt output to the invScale node"""
                mc.connectAttr((sqrtNodesBuffer+'.outputX'),(invScaleBuffer+'.input2X'))


                #create pow scale node
                sqStrValueBuffer = (nodes.createNamedNode((jnt+'_sqStValue'),'multiplyDivide'))
                """set to power"""
                mc.setAttr((sqStrValueBuffer+'.operation'),3)
                """connect scale"""
                mc.connectAttr((invScaleBuffer+'.outputX'),(sqStrValueBuffer+'.input1X'))
                """connect cache"""
                mc.connectAttr((frameCacheNodes[cnt]+'.varying'),(sqStrValueBuffer+'.input2X'))
                sqStrchValueNodes.append(sqStrValueBuffer)
                sqrtNodes.append(sqrtNodesBuffer)
                scaleNodes.append(invScaleBuffer)


                #create the worldScale multiplier node
                worldScaleMDBuffer = (nodes.createNamedNode((jnt+'_invScaleWS'),'multiplyDivide'))
                """set to multiply mode"""
                mc.setAttr((worldScaleMDBuffer+'.operation'),1) 
                """set the division factor"""
                mc.setAttr((worldScaleMDBuffer+'.input1X'),1)
                """connect our sqrt output to the invScale node"""
                mc.connectAttr((sqStrValueBuffer+'.outputX'),(worldScaleMDBuffer+'.input1X'))
                """connect our world scale """
                mc.connectAttr(worldScale1Attr,(worldScaleMDBuffer+'.input2X'))


                #connect the scale out puts to the two other channels
                """reconnects stuff"""
                mc.connectAttr((worldScaleMDBuffer+'.outputX'),(jnt+'.scale'+scaleDirection1))
                mc.connectAttr((worldScaleMDBuffer+'.outputX'),(jnt+'.scale'+scaleDirection2))
                cnt+=1

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def attachJointChainToSurface(jointChain,surface,jointOrient,jointUp,squashStretch=False):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Attaches joint chain to a surface

        ARGUMENTS:
        jointChain - List of joints	
        surface - the lofted surface to be used
        jointOrient - the joint orientation you want - ['xyz','yzx','zxy','xzy','yxz','zyx','none']
        jointUp - which direction should be up ['xup','xdown','yup','ydown','zup','zdown','none']
        squashStretch - False - no squash/stretch
                        'attr' - sttribute controlled squash/stretch
                        'animCrv' - animation curve controlled squash/stretch

        RETURNS:
        returnList[0] - rig groups
        returnList[1] - master scale attribute
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        rigGroups = []
        returnList =[]
        mc.select(cl=True)
        uvList = []
        """ Make our groups to follow the surface and drive out """
        posGroups = []
        upGroups = []
        cnt = 0
        for jnt in jointChain:
                #temp axis toggle
                #toggleJntLocalAxisDisplay (jnt)
                posGroups.append (mc.group (n= ('%s%s' % (jnt,'_Pos_grp')), w=True, empty=True))
                upGroups.append (mc.group (n= ('%s%s' % (jnt,'_Up_grp')), w=True, empty=True))
                mc.parent (upGroups[cnt],posGroups[cnt])
                uvList.append (distance.returnClosestUV (jnt,surface))
                print jnt
                print uvList[cnt]
                cnt +=1
        """ orient chain"""
        orientJointChain (jointChain,jointOrient,jointUp)
        mc.select(cl=True)
        """ Make our position info nodes"""
        posInfoNodes = []
        cnt = 0
        uvBuffer = []
        for grp in posGroups:
                node = mc.createNode ('pointOnSurfaceInfo',name= (grp+'_posInfoNode'))
                posInfoNodes.append (node)
                """ pick our cv """
                uvBuffer = (uvList[cnt])
                """ Connect the info node to the surface """
                surfaceShape = mc.listRelatives(surface,shapes=True)
                mc.connectAttr ((surfaceShape[0]+'.worldSpace'),(posInfoNodes[cnt]+'.inputSurface'))
                """ Contect the pos group to the info node"""
                mc.connectAttr ((posInfoNodes[cnt]+'.position'),(grp+'.translate'))
                """ Connect the U tangent attribute to the child of our first group """
                mc.connectAttr ((posInfoNodes[cnt]+'.tangentU'),(upGroups[cnt]+'.translate'))
                mc.setAttr ((posInfoNodes[cnt]+'.parameterU'),uvBuffer[0])
                mc.setAttr ((posInfoNodes[cnt]+'.parameterV'),uvBuffer[1])
                cnt += 1
                cvBuffer = []
        """ Make our measure nodes to keep joint position """    
        posPairsList = lists.parseListToPairs (posInfoNodes)
        posDistConnections = []
        poseDistNameList = []
        for pair in posPairsList:
                distanceInfoBuffer = distance.createDistanceNodeBetweenPosInfoNodes (pair[0],pair[1])
                posDistConnections.append(distanceInfoBuffer[2])
                poseDistNameList.append(distanceInfoBuffer[0])
        """ connect the distances to our stretch translation channels on our joints """
        """ return our up channel """
        directionBuffer = list(jointOrient)
        direction = directionBuffer[0]
        directionCap = direction.capitalize()
        """ and our other two """
        worldScale1Buffer = directionBuffer[1]
        worldScale1 = worldScale1Buffer.capitalize()
        worldScale2Buffer = directionBuffer[2]
        worldScale2 = worldScale2Buffer.capitalize()

        cnt = 0
        jointLengths = []
        mdNodes = []
        """ need to make our master scale connector"""
        scaleHolderGrp= (surface+'_scaleHolder_grp')
        masterScaleAttrBuffer = (scaleHolderGrp+'.worldScale')
        if mc.objExists (scaleHolderGrp):
                pass
        else:
                mc.group (n= scaleHolderGrp, w=True, empty=True)
                mc.addAttr (scaleHolderGrp, ln = 'worldScale',  at = 'float', hidden=False )
                mc.setAttr(masterScaleAttrBuffer,1)
        """ return our default lengths and store them,then run them through an md node to return our scale values """
        for jnt in jointChain[0:-1]:
                lengthBuffer = mc.getAttr (posDistConnections[cnt])
                jointLengths.append (lengthBuffer)
                mc.addAttr (scaleHolderGrp, ln = (jnt),  at = 'float')
                jntAttrBuffer = (scaleHolderGrp+'.'+jnt)
                mc.setAttr (jntAttrBuffer,jointLengths[cnt])
                mdNodeBuffer = nodes.createNamedNode ((jnt+'_jntScale'), 'multiplyDivide')
                mdNodes.append(mdNodeBuffer)
                mc.setAttr ((mdNodeBuffer+'.operation'),2)
                mc.connectAttr((posDistConnections[cnt]),(mdNodeBuffer+'.input1X'))
                mc.connectAttr((jntAttrBuffer),(mdNodeBuffer+'.input2X'))
                print 'worldScale1'
                print 'worldsScale2'
                mc.connectAttr(masterScaleAttrBuffer,(jnt+'.scale'+worldScale1))
                mc.connectAttr(masterScaleAttrBuffer,(jnt+'.scale'+worldScale2))
                mc.connectAttr((mdNodeBuffer+'.output.outputX'),(jnt+'.scale'+directionCap))
                cnt+=1
        """Clean up stuff """
        if mc.objExists ('surfacePosFollowStuff_grp'):
                cleanupGrp = 'surfacePosFollowStuff_grp'
        else:
                cleanupGrp = mc.group (n= 'surfacePosFollowStuff_grp', w=True, empty=True)
        for grp in posGroups:
                mc.parent (grp, cleanupGrp)
        """ clean up measure stuff """
        if mc.objExists (surface+'_measureStuff_grp'):
                distCleanupGrp = (surface+'_measureStuff_grp')
        else:
                distCleanupGrp = mc.group (n= (surface+'_measureStuff_grp'), w=True, empty=True)
                mc.parent (distCleanupGrp,cleanupGrp)
        for dist in poseDistNameList:
                mc.parent (dist, distCleanupGrp)
                mc.setAttr ((dist+'.v'),0)
        rigGroups.append (distCleanupGrp)
        rigGroups.append (scaleHolderGrp)


        """ make some IK effectors and connect everything up"""
        effectorList = []
        cnt = (len(jointChain) - 1)
        firstTermCount = 0
        secondTermCount = 1
        while cnt > 0:
                effector = mc.ikHandle (name = (jointChain[firstTermCount]+'_ikHandle') , startJoint=jointChain[firstTermCount], endEffector = jointChain[secondTermCount], setupForRPsolver = True, solver = 'ikRPsolver', enableHandles=True )
                """ if it's the not the last effector, do this """
                if cnt > 1:
                        mc.parent (effector[0],posGroups[secondTermCount])
                """ if it is, parent it to the last controlJoint """
                if cnt == 1:
                        mc.parent (effector[0],posGroups[secondTermCount])
                effectorList.append (effector[0])
                cnt-=1
                firstTermCount += 1
                secondTermCount += 1
                if cnt == 0:
                        break
        """ let's make some  pole vector constraints"""
        #----------->>>>> Need to find a good way of "discovering" correct twist for the effectors
        cnt = 0
        """ Connect first joint to surface """
        mc.connectAttr ((posGroups[0]+'.translate'),(jointChain[0]+'.translate'))
        for effector in effectorList:
                poleVector = mc.poleVectorConstraint (upGroups[cnt],effector,name = (effector+'_pvConst'))
                cnt+=1
        """ Fix the last joint's scale by pullint it from the previous one"""
        mc.connectAttr ((jointChain[-2]+'.scaleX'),(jointChain[-1]+'.scaleX'))
        mc.connectAttr ((jointChain[-2]+'.scaleY'),(jointChain[-1]+'.scaleY'))
        mc.connectAttr ((jointChain[-2]+'.scaleZ'),(jointChain[-1]+'.scaleZ'))
        """ fix the twist"""
        fixOptions = [0,90,180,-90,-180]
        orientationBuffer = list(jointOrient)
        aimChannel = orientationBuffer[0]
        effectorCnt = 0
        for joint in jointChain[0:-1]:
                loopCnt = 0
                optionCnt = 0
                while (mc.getAttr(joint+'.r'+aimChannel)) != 0:
                        print ('no match for %s' %joint)
                        print fixOptions[optionCnt]
                        mc.setAttr((effectorList[effectorCnt]+'.twist'),fixOptions[optionCnt])
                        optionCnt += 1
                        if optionCnt == 4:
                                break
                effectorCnt += 1

        # Squash stretch option
        if not squashStretch == False:
                if mc.objExists (surface+'_squashStretch_info'):
                        squashStretchGrp = (surface+'_squashStretch_info')
                else:
                        squashStretchGrp = mc.group (n= (surface+'_squashStretch_info'), w=True, empty=True)
                attributes.doSetLockHideKeyableAttr(squashStretchGrp,True,False,False,('tx','ty','tz','rx','ry','rz','sx','sy','sz','v'))
                if squashStretch == 'attr':
                        addSqashStretchToSurfaceChainByAttr(squashStretchGrp,jointChain,jointOrient)
                elif squashStretch == 'animCrv':
                        addSqashStretchToSurfaceChainByAnimCrv(squashStretchGrp,jointChain,jointOrient)
        """ Clean up stuff for return """
        returnList.append (rigGroups)
        returnList.append (masterScaleAttrBuffer)
        return returnList
        """return all our data together to return"""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def loftSurfaceFromJointList(jointList,outChannel):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        ACKNOWLEDMENT:
        This is a modification of the brilliant technique I got from Matt's blog - 
        http://td-matt.blogspot.com/2011/01/spine-control-rig.html?showComment=1297462382914#c3066380136039163369

        DESCRIPTION:
        Lofts a surface from a joint list

        ARGUMENTS:
        jointList(list) - list of the joints you want to loft from
        outChannel(string)['x','y','z - the the extrude out direction

        RETURNS:
        surface(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """

        """ return a good length for out loft curves """
        length = (distance.returnDistanceBetweenObjects (jointList[0], jointList[-1])/2)
        loftCurveList = []
        crvPosBuffer = []
        crvPosBuffer.append ([0,0,0])
        if outChannel == 'x':
                crvPosBuffer.append ([length,0,0])
        elif outChannel == 'y':
                crvPosBuffer.append ([0,length,0])
        elif outChannel == 'z':
                crvPosBuffer.append ([0,0,length])
        crvPosBuffer.reverse ()
        """ for each joint, make a loft curve and snap it to the joint it goes with """
        for jnt in jointList:
                crvBuffer = mc.curve (d=1, p = crvPosBuffer , os=True, n=(jnt+'_tmpCrv'))
                mc.xform (crvBuffer, cp = True)
                posBuffer = distance.returnWorldSpacePosition (jnt)
                cnstBuffer = mc.parentConstraint ([jnt], [crvBuffer], maintainOffset = False)
                mc.delete (cnstBuffer)
                loftCurveList.append (crvBuffer)
        controlSurface = mc.loft (loftCurveList, reverseSurfaceNormals = True, ch = False, uniform = True, degree = 3)
        """ deletes our loft curve list"""
        for crv in loftCurveList:
                mc.delete (crv)

        return controlSurface

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def makeJointControlSurface(startJoint,controlJointList,outChannel,name):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        ACKNOWLEDMENT:
        This is a modification of the brilliant technique I got from Matt's blog - 
        http://td-matt.blogspot.com/2011/01/spine-control-rig.html?showComment=1297462382914#c3066380136039163369

        DESCRIPTION:
        Makes a ricgmon surface for ricgmon rigging and sets things up for it

        ARGUMENTS:
        startJoint - first joint of the heirarchy to work with
        controlJointList - seperate joints that will have the surface skinned to it (instead of using clusters)
        outChannel - x/y/z - which direction is out from the joint. In a traditional sense, it would most likely be x with a z aim and y up world
        name - what we're rigging here (spine, uprArm, etc)

        RETURNS:
        groupName(
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        """ Makes a ricgmon surface for ricgmon rigging """
        heirarchyJoints = []
        heirarchyJoints.append (startJoint)
        childrenBuffer = []
        controlJointGroups = []
        """ Makes some transform groups for our groups"""
        for cntrl in controlJointList:
                controlJointGroups.append (groupMeObject (cntrl))
                """ Get joint list """
        for jnt in (mc.listRelatives (startJoint, ad = True, type = 'joint')):
                childrenBuffer.append (jnt)
        childrenBuffer.reverse ()
        heirarchyJoints += childrenBuffer
        """ return a good length for out loft curves """
        length = (distance.returnDistanceBetweenObjects (heirarchyJoints[0], heirarchyJoints[-1])/2)
        loftCurveList = []
        crvPosBuffer = []
        crvPosBuffer.append ([0,0,0])
        if outChannel == 'x':
                crvPosBuffer.append ([length,0,0])
        elif outChannel == 'y':
                crvPosBuffer.append ([0,length,0])
        elif outChannel == 'z':
                crvPosBuffer.append ([0,0,length])
        crvPosBuffer.reverse ()
        """ for each joint, make a loft curve and snap it to the joint it goes with """
        for jnt in heirarchyJoints:
                crvBuffer = mc.curve (d=1, p = crvPosBuffer , os=True, n=(jnt+'_tmpCrv'))
                mc.xform (crvBuffer, cp = True)
                posBuffer = distance.returnWorldSpacePosition (jnt)
                cnstBuffer = mc.parentConstraint ([jnt], [crvBuffer], maintainOffset = False)
                mc.delete (cnstBuffer)
                loftCurveList.append (crvBuffer)
        controlSurface = mc.loft (loftCurveList, reverseSurfaceNormals = True, ch = False, uniform = True, degree = 3, n = (name+'_surf') )
        """ deletes our loft curve list"""
        for crv in loftCurveList:
                mc.delete (crv)
        cvList = (mc.ls ([controlSurface[0]+'.cv[*]'],flatten=True))
        """ Time to set skin our surface to our control joints """
        surfaceSkinCluster = mc.skinCluster (controlJointList,controlSurface,tsb=True, n=(controlSurface[0]+'_skinCluster') )
        """ Make our groups to follow the surface and drive out """
        posGroups = []
        upGroups = []
        cnt = 0
        for jnt in heirarchyJoints:
                posGroups.append (mc.group (n= ('%s%s' % (jnt,'_Pos_grp')), w=True, empty=True))
                upGroups.append (mc.group (n= ('%s%s' % (jnt,'_Up_grp')), w=True, empty=True))
                mc.parent (upGroups[cnt],posGroups[cnt])
                cnt +=1
        """ Make our v values for our position info groups"""
        vValues = []
        vValues.append (.5)
        cnt = 0
        for item in heirarchyJoints[1:-1]:
                vValues.append (cnt + 1)
                cnt += 1
        """ Make our position info nodes"""
        posInfoNodes = []
        cnt = 0
        for grp in posGroups[0:-1]:
                node = mc.createNode ('pointOnSurfaceInfo',name= (grp+'_posInfoNode'))
                posInfoNodes.append (node)
                """ Connect the info node to the surface """                  
                mc.connectAttr ((controlSurface[0]+'Shape.worldSpace'),(posInfoNodes[cnt]+'.inputSurface'))
                """ Contect the pos group to the info node"""
                mc.connectAttr ((posInfoNodes[cnt]+'.position'),(grp+'.translate'))
                """ Connect the U tangent attribute to the child of our first group """
                mc.connectAttr ((posInfoNodes[cnt]+'.tangentU'),(upGroups[cnt]+'.translate'))
                mc.setAttr ((posInfoNodes[cnt]+'.parameterU'),.5)
                mc.setAttr ((posInfoNodes[cnt]+'.parameterV'),(vValues[cnt]))
                cnt += 1
        """ make some IK effectors and connect everything up"""
        effectorList = []
        cnt = (len(heirarchyJoints) - 1)
        firstTermCount = 0
        secondTermCount = 1
        while cnt > 0:
                effector = mc.ikHandle (name = (heirarchyJoints[firstTermCount]+'_ikHandle') , startJoint=heirarchyJoints[firstTermCount], endEffector = heirarchyJoints[secondTermCount], setupForRPsolver = True, solver = 'ikRPsolver', enableHandles=True )
                """ if it's the not the last effector, do this """
                if cnt > 1:
                        mc.parent (effector[0],posGroups[secondTermCount])
                """ if it is, parent it to the last controlJoint """
                if cnt == 1:
                        pass
                        mc.parent (effector[0],controlJointList[len(controlJointList)-1])
                effectorList.append (effector[0])
                cnt-=1
                firstTermCount += 1
                secondTermCount += 1
                if cnt == 0:
                        break
        """ let's make some  pole vector constraints"""
        print effectorList
        cnt = 1
        for effector in effectorList:
                #print ('Constrain '+effector+' to '+ upGroups[cnt])
                poleVector = mc.poleVectorConstraint (upGroups[cnt],effector,name = (effector+'_pvConst'))
                """ fix the twist"""
                if (len(effectorList) - cnt) == 0:
                        mc.setAttr ((effector+'.twist'),-180)
                else:
                        mc.setAttr ((effector+'.twist'),-90)
                cnt+=1
        """ need to find the closest posGroup to our mid control"""
        midSnapPointObject = distance.returnClosestObject (controlJointList[int(len(controlJointList)/2)], heirarchyJoints)
        midGrpObject = distance.returnClosestObject (controlJointList[int(len(controlJointList)/2)], posGroups)
        midControlJointGrpObject = distance.returnClosestObject (controlJointList[int(len(controlJointList)/2)], controlJointGroups)
        """ setup inter-control constraints, 3 locator setup """
        constraintPointLocBuffer = locMeObject(midSnapPointObject)
        constraintPointLoc = mc.rename (constraintPointLocBuffer,('gut_ctrl_grp_point'))
        constraintAimLocBuffer = mc.duplicate (constraintPointLoc)
        constraintAimLoc = mc.rename (constraintAimLocBuffer,('gut_ctrl_grp_aimAt'))
        mc.move (1,0,0,constraintAimLoc,r=True,os=True,wd=True)
        constraintUpLocBuffer = mc.duplicate (constraintPointLoc)
        constraintUpLoc = mc.rename (constraintUpLocBuffer,('gut_ctrl_grp_up'))
        mc.move (0,0,1,constraintUpLoc,r=True,os=True,wd=True)
        mc.pointConstraint (constraintPointLoc, midControlJointGrpObject, maintainOffset = True)
        mc.aimConstraint (constraintAimLoc,midGrpObject,aimVector = [0,1,0],upVector = [0,0,1], worldUpObject = constraintUpLoc, maintainOffset = True )
        """ constrain the locators for follow along support! """
        constraintLocs = [constraintPointLoc,constraintAimLoc,constraintUpLoc]
        for loc in constraintLocs:
                mc.parentConstraint (controlJointList[0], controlJointList[len(controlJointList)-1], loc, maintainOffset = True)

        """return all our data together to return"""
        return controlJointGroups
        #print (controlJointList[int(len(controlJointList)/2))
        #print (mc.listRelatives ((controlJointList[int(len(controlJointList)/2)), parent=True))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def makeJointControlSurfaceFish(startJoint,controlJointList,outChannel,name):
        """ Makes a ricgmon surface for ricgmon rigging """
        heirarchyJoints = []
        heirarchyJoints.append (startJoint)
        childrenBuffer = []
        controlJointGroups = []
        """ Makes some transform groups for our groups"""
        for cntrl in controlJointList:
                controlJointGroups.append (groupMeObject (cntrl,True))
                """ Get joint list """
        for jnt in (mc.listRelatives (startJoint, ad = True, type = 'joint')):
                childrenBuffer.append (jnt)
        childrenBuffer.reverse ()
        heirarchyJoints += childrenBuffer
        """ return a good length for out loft curves """
        length = (distance.returnDistanceBetweenObjects (heirarchyJoints[0], heirarchyJoints[-1])/2)
        loftCurveList = []
        crvPosBuffer = []
        crvPosBuffer.append ([0,0,0])
        if outChannel == 'x':
                crvPosBuffer.append ([length,0,0])
        elif outChannel == 'y':
                crvPosBuffer.append ([0,length,0])
        elif outChannel == 'z':
                crvPosBuffer.append ([0,0,length])
        crvPosBuffer.reverse ()
        """ for each joint, make a loft curve and snap it to the joint it goes with """
        for jnt in heirarchyJoints:
                crvBuffer = mc.curve (d=1, p = crvPosBuffer , os=True, n=(jnt+'_tmpCrv'))
                mc.xform (crvBuffer, cp = True)
                posBuffer = distance.returnWorldSpacePosition (jnt)
                cnstBuffer = mc.parentConstraint ([jnt], [crvBuffer], maintainOffset = False)
                mc.delete (cnstBuffer)
                loftCurveList.append (crvBuffer)
        controlSurface = mc.loft (loftCurveList, reverseSurfaceNormals = True, ch = False, uniform = True, degree = 3, n = (name+'_surf') )
        """ deletes our loft curve list"""
        for crv in loftCurveList:
                mc.delete (crv)
        cvList = (mc.ls ([controlSurface[0]+'.cv[*]'],flatten=True))
        """ Time to set skin our surface to our control joints """
        surfaceSkinCluster = mc.skinCluster (controlJointList,controlSurface,tsb=True, n=(controlSurface[0]+'_skinCluster'))
        """ Make our groups to follow the surface and drive out """
        posGroups = []
        upGroups = []
        cnt = 0
        for jnt in heirarchyJoints:
                posGroups.append (mc.group (n= ('%s%s' % (jnt,'_Pos_grp')), w=True, empty=True))
                upGroups.append (mc.group (n= ('%s%s' % (jnt,'_Up_grp')), w=True, empty=True))
                mc.parent (upGroups[cnt],posGroups[cnt])
                cnt +=1
        """ Make our v values for our position info groups"""
        vValues = []
        vValues.append (.5)
        cnt = 0
        for item in heirarchyJoints[1:-1]:
                vValues.append (cnt + 1)
                cnt += 1
        """ Make our position info nodes"""
        posInfoNodes = []
        cnt = 0
        for grp in posGroups[0:-1]:
                node = mc.createNode ('pointOnSurfaceInfo',name= (grp+'_posInfoNode'))
                posInfoNodes.append (node)
                """ Connect the info node to the surface """                  
                mc.connectAttr ((controlSurface[0]+'Shape.worldSpace'),(posInfoNodes[cnt]+'.inputSurface'))
                """ Contect the pos group to the info node"""
                mc.connectAttr ((posInfoNodes[cnt]+'.position'),(grp+'.translate'))
                """ Connect the U tangent attribute to the child of our first group """
                mc.connectAttr ((posInfoNodes[cnt]+'.tangentU'),(upGroups[cnt]+'.translate'))
                mc.setAttr ((posInfoNodes[cnt]+'.parameterU'),.5)
                mc.setAttr ((posInfoNodes[cnt]+'.parameterV'),(vValues[cnt]))
                cnt += 1
        """ make some IK effectors and connect everything up"""
        effectorList = []
        cnt = (len(heirarchyJoints) - 1)
        firstTermCount = 0
        secondTermCount = 1
        while cnt > 0:
                effector = mc.ikHandle (name = (heirarchyJoints[firstTermCount]+'_ikHandle') , startJoint=heirarchyJoints[firstTermCount], endEffector = heirarchyJoints[secondTermCount], setupForRPsolver = True, solver = 'ikRPsolver', enableHandles=True )
                """ if it's the not the last effector, do this """
                if cnt > 1:
                        mc.parent (effector[0],posGroups[secondTermCount])
                """ if it is, parent it to the last controlJoint """
                if cnt == 1:
                        pass
                        mc.parent (effector[0],controlJointList[len(controlJointList)-1])
                effectorList.append (effector[0])
                cnt-=1
                firstTermCount += 1
                secondTermCount += 1
                if cnt == 0:
                        break
        """ let's make some  pole vector constraints"""
        #----------->>>>> Need to find a good way of "discovering" correct twist for the effectors
        cnt = 0
        for effector in effectorList:
                #print ('Constrain '+effector+' to '+ upGroups[cnt])
                poleVector = mc.poleVectorConstraint (upGroups[cnt],effector,name = (effector+'_pvConst'))
                """ fix the twist"""
                if (len(effectorList) - cnt) == 0:
                        mc.setAttr ((effector+'.twist'),180)
                elif cnt == 0:
                        mc.setAttr ((effector+'.twist'),-90)            
                else:
                        mc.setAttr ((effector+'.twist'),-90)
                cnt+=1
        #
        """return all our data together to return"""
        return controlJointGroups


def insertRollJointsSegment (start, end, number):
        #props for this function go to John Doublestein who
        #was the author in mel, I simply translated to python
        #www.johndoublestein.com
        cnt=1
        i=0
        rollChain = []
        """checks to see if 'end' is child of 'start'"""
        checkChild = mc.listRelatives (start, c= True,type= 'joint' )
        if end == checkChild[0]:
                """If it exists, get's the radius"""
                if mc.objExists (start+'.radi'):
                        radius = mc.getAttr (start+'.radi')

                """Creates curve between two joints to be recreated and from which our new positions will come"""
                startPos = mc.xform (start,q=True, ws=True, rp=True)
                endPos = mc.xform (end,q=True, ws=True, rp=True)
                crvName = mc.curve (d=1, p = [(startPos[0], startPos[1], startPos[2]),(endPos[0], endPos[1], endPos[2])], k= [0,1], n=(start+'_to_'+end+'_crv'))

                mc.rebuildCurve (crvName, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=(number+1), d=1, tol=0.001)
                mc.parent (crvName, start)

                currentJoint = start
                """While loop making joints for every cv except the last"""
                while mc.objExists ('%s%s%i%s' % (crvName,'.cv[',cnt,']')):
                        jointPos = mc.pointPosition ('%s%s%i%s' % (crvName,'.cv[',cnt,']'),l=True)
                        """Checks for non '1' scales"""
                        if mc.getAttr(currentJoint+'.scale')[0] != (1, 1, 1):        
                                mc.setAttr ('%s%s' % (currentJoint,'.sx'),1) 
                                mc.setAttr ('%s%s' % (currentJoint,'.sy'),1)         
                                mc.setAttr ('%s%s' % (currentJoint,'.sz'),1)     
                                print (currentJoint +' had scale value other that 1. Fixed.')
                        """Inserts our new joint, names it and positions it"""
                        catchName = mc.insertJoint (currentJoint)
                        newName = mc.rename (catchName,('%s%s%i' % (start,'_Roll_',i)))
                        mc.joint (newName, e=True,co=True,p=(jointPos[0],jointPos[1],jointPos[2]))
                        """Sets the radius of the joint and adds it to our return joint list"""
                        if mc.objExists (newName):
                                mc.setAttr ((newName+'.radi'), radius)
                                currentJoint = ('%s%s%i' % (start,'_Roll_',i))
                                rollChain.append (currentJoint)
                        cnt+=1
                        if (cnt == number+1):
                                break
                        i+=1
                #mc.delete ('tempRollCrv')
                success = True
        else:
                print ('There can be no joints between your start and end')
                success = False
        return rollChain