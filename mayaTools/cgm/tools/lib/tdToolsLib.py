#=================================================================================================================================================
#=================================================================================================================================================
#	tdToolsLib - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Library of functions for the cgmRiggingTools tool
#
# REQUIRES:
#   Maya
#
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1.12072011 - First version
#	0.1.12132011 - master control maker implemented, snap move tools added
#	0.1.12272011 - split out library from tool
#
#=================================================================================================================================================
__version__ = '0.1.12032011'

import maya.cmds as mc
import maya.mel as mel
import subprocess

from cgm.lib.zoo.zooPyMaya import skinWeights
from cgm.lib.cgmBaseMelUI import *


from cgm.lib import (guiFactory,
                     objectFactory,
                     controlBuilder,
                     curves,
                     dictionary,
                     autoname,
                     search,
                     deformers,
                     logic,
                     rigging,
                     locators,
                     attributes,
                     batch,
                     distance,
                     position,
                     lists,
                     skinning)

from cgm.tools.lib import locinatorLib,namingToolsLib

reload(curves)
reload(position)
"""

"""
def uiSetSelfVariable(self,variable,value):
    print variable
    print value
    self.variable = value



def loadGUIOnStart(self):
    selected = mc.ls(sl=True)
    if selected:
        for obj in selected:
            if search.returnTagInfo(selected[0],'cgmObjectType') == 'textCurve':
                mc.select(selected[0])
                doLoadTexCurveObject(self)
                break
            
        mc.select(selected[0])
        namingToolsLib.uiLoadAutoNameObject(self)
	
        mc.select(selected)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# SDK
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doSelectDrivenJoints(self):
    selected = mc.ls(sl=True)
    mc.select(cl=True)
    channelBoxName = search.returnMainChannelBoxName()

    # Get the attrs
    selectedAttrs = mc.channelBox(channelBoxName,q=True, sma=True)

    fullAttrs = []
    if selectedAttrs:
        for attr in selectedAttrs:
            fullAttrs.append(selected[0]+'.'+attr)
        for fullAttr in fullAttrs:
            drivenJoints = sdk.returnDrivenJoints(fullAttr)
            if drivenJoints:
                mc.select(drivenJoints)
            else:
                guiFactory.warning('No driven joints found')
    else:
        guiFactory.warning('No selected attributes found')


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Attribute Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doDeformerKeyableAttributesConnect(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for connecting the animateable attributes of a deformer to another object
    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    sourceObject = self.SourceObjectField(q=True, text = True)
    if not search.returnObjectType(sourceObject) in ['nonLinear']:
        return (guiFactory.warning('No deformer object loaded loaded'))

    targetObjects = mc.ls(sl=True, flatten = True)
    if not targetObjects:
        targetObjectsBuffer = mc.optionVar(q='cgmVarTargetObjects')
        if ';' in targetObjectsBuffer:
            targetObjects = targetObjectsBuffer.split(';')
        else:
            targetObjects = targetObjectsBuffer

    baseName = self.BaseNameField(query=True, text =True)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Make the attributes and connect em
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    attributes.copyKeyableAttrs(sourceObject,targetObjects[0],connectAttrs=True)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Deformer Utility Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLoadPolyUnite(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    loads a polyUnite node to our source and selects the source shapes

    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    selectBuffer = mc.ls(sl=True, flatten = True)
    if selectBuffer:
        if search.returnObjectType(selectBuffer[0]) is 'polyUnite':
            self.SourceObjectField(edit = True, text = selectBuffer[0])
            uniteNode = selectBuffer[0]
        else:
            buffer = deformers.returnPolyUniteNodeFromResultGeo(selectBuffer[0])
            if buffer:
                self.SourceObjectField(edit = True, text = buffer)
                uniteNode = buffer
            else:
                return (guiFactory.warning('No poly unite node found'))
    else:
        return (guiFactory.warning('Please select a polyUnite Node or a polyUnite resulting geo'))


    if uniteNode:
        sourceShapesBuffer = deformers.returnPolyUniteSourceShapes(uniteNode)
        print sourceShapesBuffer
        selectList = []

        uniteGeoBuffer = mc.listRelatives( (deformers.returnPolyUniteResultGeoShape(uniteNode)), parent = True)
        uniteGeo = uniteGeoBuffer[0]
        print uniteGeo

        for obj in sourceShapesBuffer:
            if search.returnObjectType(obj) in ['blendShape','wrap','skinCluster']:
                objects = deformers.returnBaseObjectsFromDeformer(obj)
                for o in objects:
                    if o != uniteGeo:
                        selectList.append(o)
            else:
                selectList.append(obj)

        mc.select(cl=True)
        print selectList
        mc.select (selectList)
    else:
        return (guiFactory.warning('No polyUnite found'))

def doDeletePolyUniteNode(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for extracting blendshapes from an object that may have had the targets deleted

    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    sourceObject = self.SourceObjectField(q=True, text = True)
    print sourceObject
    if search.returnObjectType(sourceObject) == 'polyUnite':
        deformers.removePolyUniteNode(sourceObject)
    else:
        return (guiFactory.warning('No polyUnite loaded'))


def doBuildPolyUnite(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for extracting blendshapes from an object that may have had the targets deleted

    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    targetObjects = mc.ls(sl=True, flatten = True)
    if not targetObjects:
        targetObjectsBuffer = mc.optionVar(q='cgmVarTargetObjects')
        if ';' in targetObjectsBuffer:
            targetObjects = targetObjectsBuffer.split(';')
        else:
            targetObjects = targetObjectsBuffer

    baseName = self.BaseNameField(query=True, text = True)
    print baseName

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Variable data checks
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #Do we have targets
    if not targetObjects:
        return guiFactory.warning('Either selected meshes or target objects required')

    #Check for mesh object types
    for obj in targetObjects:
        if not search.returnObjectType(obj) == 'mesh':
            return (guiFactory.warning('%s is not a mesh object' %obj))


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Function
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if not baseName:
        baseName = 'UnifiedGeo'
    buffer = deformers.polyUniteGeo(targetObjects,name=baseName)

    self.SourceObjectField(edit = True, text = buffer[1])

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Blendshape Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLoadBlendShapePoseBuffer(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    loads a blendShape poseBuffer node to our source and selects the source shapes

    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    selectBuffer = mc.ls(sl=True, flatten = True)
    if selectBuffer:
        poseBufferCandidate = selectBuffer[0]
        self.SourceObjectField(edit = True, text = poseBufferCandidate)

        #Check for a connected blendshape node
        blendShapeSearchBuffer = deformers.returnBlendShapeNodeFromPoseBuffer(poseBufferCandidate)
        if blendShapeSearchBuffer:
            guiFactory.doLoadMultipleObjectsToTextField(self.TargetObjectField,blendShapeSearchBuffer,'cgmVarTargetObjects')
        else:
            return (guiFactory.warning('No connected blendShape node found'))
    else:
        return (guiFactory.warning('Please select a poseBuffer'))



def doCreatePoseBuffer(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for extracting blendshapes from an object that may have had the targets deleted

    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    sourceObject = self.SourceObjectField(q=True, text = True)


    baseName = self.BaseNameField(query=True, text =True)

    DoConnectCase = mc.optionVar(q='cgmVarPoseBufferDoConnect') 
    TransferConnectionsCase = mc.optionVar(q='cgmVarPoseBufferTransferConnections') 


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Variable data checks
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 

    #Check for blendShape object types
    if not search.returnObjectType(sourceObject) == 'blendShape':
        return (guiFactory.warning('%s is not a blendShape node' %sourceObject))

    if not baseName:
        baseName = 'Posebuffer'
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Function
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    buffer = deformers.blendShapeNodeToPoseBuffer(baseName,sourceObject,doConnect = DoConnectCase, transferConnections = TransferConnectionsCase)

    if DoConnectCase:
        deformers.connectBlendShapeNodeToPoseBuffer(sourceObject,buffer[0])


    self.TargetObjectField(edit = True, text = buffer[0])

def doUpdatePoseBuffer(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for extracting blendshapes from an object that may have had the targets deleted

    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    sourceObject = self.SourceObjectField(q=True, text = True)

    targetObjects = mc.ls(sl=True, flatten = True)
    if not targetObjects:
        targetObjectsBuffer = self.TargetObjectField(q=True,text=True)
        #targetObjectsBuffer = mc.optionVar(q='cgmVarTargetObjects')
        if ';' in targetObjectsBuffer:
            targetObjects = targetObjectsBuffer.split(';')
        else:
            targetObjects = [targetObjectsBuffer]

    RemoveMissingCase = mc.optionVar(q='cgmVarPoseBufferDoRemoveMissing')
    DoConnectCase = mc.optionVar(q='cgmVarPoseBufferDoConnect')
    TransferConnectionsCase = mc.optionVar(q='cgmVarPoseBufferTransferConnections')


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Variable data checks
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #Do we have targets
    if not targetObjects:
        return guiFactory.warning('We need a blendshape node')

    #Check for blendShape object types
    for obj in targetObjects:
        if not search.returnObjectType(obj) == 'blendShape':
            return (guiFactory.warning('%s is not a blendShape node' %obj))

    poseBuffer = sourceObject
    """
    print sourceObject
    if search.returnObjectType(sourceObject) == 'polyUnite':
	deformers.removePolyUniteNode(sourceObject)
    else:
	return (guiFactory.warning('No polyUnite loaded'))
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Function
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    buffer = deformers.updateBlendShapeNodeToPoseBuffer(poseBuffer,targetObjects[0],DoConnectCase,TransferConnectionsCase,RemoveMissingCase)

    if DoConnectCase:
        deformers.connectBlendShapeNodeToPoseBuffer(targetObjects[0],poseBuffer)

def doBakeBlendShapeTargetsToTargetsFromSource(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for extracting blendshapes from an object that may have had the targets deleted

    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # Check for selection, defaults to using that for targets
    sourceObject = mc.optionVar(q='cgmVarSourceObject')
    #targetObjectsBuffer = self.TargetObjectField(query = True, text=True)
    targetObjectsBuffer = mc.optionVar(q='cgmVarTargetObjects')
    if ';' in targetObjectsBuffer:
        targetObjects = targetObjectsBuffer.split(';')
    else:
        targetObjects = targetObjectsBuffer

    bakeInbetweensCase = mc.optionVar(q='cgmVarBSBakeInbetweens')
    transferConnectionsCase = mc.optionVar(q='cgmVarBSBakeTransferConnections')
    bakeCombineCase = mc.optionVar(q='cgmVarBSBakeCombine')
    combineTermsString = self.BlendShapeCombineTermsField(query=True,text=True)

    baseName = self.BaseNameField(query=True, text =True)

    blendShapeNodes = deformers.returnObjectDeformers(sourceObject,'blendShape')
    blendShapeNode = blendShapeNodes[0]


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Function
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if sourceObject:
        if len(blendShapeNodes) >= 1:
            if not baseName:
                baseName = False
            #>>> If we have target objects
            if targetObjects:
                #>>> if we're combining sides
                if bakeCombineCase:
                    if combineTermsString:
                        combineTerms = combineTermsString.split(';')
                        print combineTerms
                        #>>> Check for combineTerms length
                        if len(combineTerms)==2:
                            for targetObj in targetObjects:
                                deformers.bakeCombinedBlendShapeNodeToTargetObject(targetObj,sourceObject, blendShapeNode,
                                                                                   baseName, directions=combineTerms)
                        else:
                            guiFactory.warning("Not enough combine terms")
                    else:
                        guiFactory.warning("Need a combine string. For example 'left,right'")

                else:
                    """
		    bakeBlendShapeNodeToTargetObject(targetObject,sourceObject, blendShapeNode, baseNameToUse = False, stripPrefix = False,ignoreInbetweens = False, ignoreTargets = False, transferConnections = True)
		    """
                    for targetObj in targetObjects:
                        print 'source...'
                        print sourceObject
                        print 'target objects...'
                        print targetObjects
                        print 'bakeCase...'
                        print bakeInbetweensCase
                        print 'transfer...'
                        print transferConnectionsCase
                        print 'combineCase'
                        print bakeCombineCase
                        print 'combineTerms'
                        print combineTermsString
                        print 'bsNodes...'
                        print blendShapeNode
                        print 'basename...'
                        print baseName
                        deformers.bakeBlendShapeNodeToTargetObject(targetObj,sourceObject, blendShapeNode, baseNameToUse = baseName,
                                                                   stripPrefix = False, ignoreInbetweens = (not bakeInbetweensCase),
                                                                   ignoreTargets = False,transferConnections = transferConnectionsCase)
            else:
                guiFactory.warning('Need at least one target object')
        else:
            guiFactory.warning('Source object needs a blendShape node')
    else:
        guiFactory.warning('Need a source object')


def doBakeBlendShapeTargetsFromSource(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for extracting blendshapes from an object that may have had the targets deleted

    REQUIRES:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    sourceObject = mc.optionVar(q='cgmVarSourceObject')
    bakeInbetweensCase = mc.optionVar(q='cgmVarBSBakeInbetweens')
    transferConnectionsCase = mc.optionVar(q='cgmVarBSBakeTransferConnections')
    bakeCombineCase = mc.optionVar(q='cgmVarBSBakeCombine')
    combineTermsString = self.BlendShapeCombineTermsField(query=True,text=True)

    baseName = self.BaseNameField(query=True, text =True)

    blendShapeNodes = deformers.returnObjectDeformers(sourceObject,'blendShape')
    blendShapeNode = blendShapeNodes[0]
    print sourceObject
    print bakeInbetweensCase
    print transferConnectionsCase
    print bakeCombineCase
    print combineTermsString
    print blendShapeNodes
    print baseName

    if sourceObject:
        if len(blendShapeNodes) >= 1:
            if not baseName:
                baseName = False
            #>>> if we're combining sides
            if bakeCombineCase:
                if combineTermsString:
                    combineTerms = combineTermsString.split(',')
                    #>>> Check for combineTerms length
                    if len(combineTerms)==2:
                        deformers.bakeCombinedBlendShapeNode(sourceObject, blendShapeNode,
                                                             baseNameToUse = baseName, directions=combineTerms)
                    else:
                        guiFactory.warning("Not enough combine terms")
                else:
                    guiFactory.warning("Need a combine string. For example 'left,right'")

            else:
                deformers.bakeBlendShapeNode(sourceObject, blendShapeNode, baseNameToUse = baseName,
                                             stripPrefix = False, ignoreInbetweens = (not bakeInbetweensCase),
                                             ignoreTargets = [])

        else:
            guiFactory.warning('Source object needs a blendShape node')
    else:
        guiFactory.warning('Need a source object')


def doShrinkWrapToSource():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for finding vertices that are over X influences

    REQUIRES:
    A selection or a set cgmVarSourceObject

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    selected = mc.ls(sl=True,flatten=True)

    sourceObject = mc.optionVar(q='cgmVarSourceObject')

    #see if we have selected stuff to work on
    if selected:
        # if the source object isn't loaded in the field, it tries to grab the last object selected
        if not sourceObject:
            sourceObject = selected[-1]
            targetObjects = selected[:-1]
        else:
            targetObjects = selected

    else:
        targetObjects = mc.optionVar(q='cgmVarTargetObjects')


    if len(selected) >=1:

        if sourceObject:
            sourceType = search.returnObjectType(sourceObject)

            if targetObjects:
                itemCnt = 0

                for obj in targetObjects:
                    targetType = search.returnObjectType(obj)

                    # Type check to get our Components to move
                    if targetType == 'mesh':
                        componentsToMove = (mc.ls ([obj+'.vtx[*]'],flatten=True))

                    elif targetType == 'polyVertex':
                        componentsToMove = [obj]

                    elif targetType in ['polyEdge','polyFace']:
                        mc.select(cl=True)
                        mc.select(obj)

                        mel.eval("PolySelectConvert 3")
                        componentsToMove = mc.ls(sl=True,fl=True)

                    elif targetType in ['nurbsCurve','nurbsSurface']:
                        componentsToMove = []
                        shapes = mc.listRelatives(obj,shapes=True,fullPath=True)
                        if shapes:
                            for shape in shapes:
                                componentsToMove.extend(mc.ls ([shape+'.cv[*]'],flatten=True))
                        else:
                            componentsToMove = (mc.ls ([obj+'.cv[*]'],flatten=True))


                    elif targetType == 'shape':
                        componentsToMove = (mc.ls ([obj+'.cv[*]'],flatten=True))

                    elif targetType == 'surfaceCV':
                        componentsToMove = [obj]

                    else:
                        componentsToMove = [obj]

                    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(componentsToMove),'Shrinkwraping...')
                    # Let's move it
                    for c in componentsToMove:
                        if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                            break
                        mc.progressBar(mayaMainProgressBar, edit=True, status = ("wrapping '%s'"%c), step=1)

                        if sourceType in ['mesh','nurbsSurface','nurbsCurve']:
                            pos = distance.returnWorldSpacePosition(c)
                            targetLoc = mc.spaceLocator()
                            mc.move (pos[0],pos[1],pos[2], targetLoc[0])

                            closestLoc = locators.locClosest([targetLoc[0]],sourceObject)
                            position.movePointSnap(c,closestLoc)
                            mc.delete([targetLoc[0],closestLoc])

                        else:
                            guiFactory.warning('The source object must be a poly,nurbs curve or nurbs surface')

                    itemCnt += 1
                    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

            else:
                guiFactory.warning('You need target objects selected or loaded to the target field')
        else:
            guiFactory.warning('You need a source object')
    else:
        guiFactory.warning('You need at least two objects')

    """
    selected = mc.ls(sl=True,flatten=True)
    if skinning.querySkinCluster(selected[0]):
        badVertices = skinning.returnExcessInfluenceVerts(selected[0],maxInfluences)
        returnProc(badVertices)

    elif sourceObject:
        badVertices = skinning.returnExcessInfluenceVerts(sourceObject,maxInfluences)
        returnProc(badVertices)

    else:
        guiFactory.warning('You need a source object or an object with a skin cluster selected.')
    """

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Skin Cluster Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doCopySkinningToVertFromSource():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    asdf

    REQUIRES:
    asdf

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    # Check for selection, defaults to using that for targets
    selected = mc.ls(sl=True,flatten=True)
    targetObjects = []

    if selected:
        for obj in selected:
            if search.returnObjectType(obj) == 'polyVertex':
                targetObjects.append(obj)
    else:
        targetObjectsBuffer = mc.optionVar(q='cgmVarTargetObjects')

    sourceObject = mc.optionVar(q='cgmVarSourceObject') 


    if sourceObject: 
        if targetObjects:  
            mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(targetObjects),'Vert Weight Copying...')
            stepInterval = 1
            for obj in targetObjects:
                if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                    break
                skinning.copyWeightsByClosestVerticeFromVert(sourceObject, obj)
                stepInterval +=1

                mc.progressBar(mayaMainProgressBar, edit=True, status = ("Copying '%s'"%obj), step=1)

            guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

        else:
            guiFactory.warning('You need target objects selected or loaded to the target field')
    else:
        guiFactory.warning('You need a source object')


def doTransferSkinning():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Transfers the skin weighting from one object to another

    REQUIRES:
    A selection or a set cgmVarSourceObject

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    selected = mc.ls(sl=True,flatten=True)

    if selected:
        targetObjects = selected
    else:
        targetObjects = mc.optionVar(q='cgmVarTargetObjects')

    sourceObject = mc.optionVar(q='cgmVarSourceObject')

    if sourceObject:
        if targetObjects:
            for obj in targetObjects:

                skinWeights.transferSkinning( sourceObject, obj )

        else:
            guiFactory.warning('You need target objects selected or loaded to the target field')
    else:
        guiFactory.warning('You need a source object')

def doCopyWeightsFromFirstToOthers():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Transfers the skin weighting from one oomponent to another

    REQUIRES:
    A selection of vertices

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    sourceObject = mc.optionVar(q='cgmVarSourceObject')
    sourceObjectCheck = False
    if mc.objExists(sourceObject):
        if search.returnObjectType(sourceObject) == 'polyVertex':
            buffer = mc.ls(sl=True,flatten=True)
            targetObjects = buffer
            sourceObjectCheck = True

    if not sourceObjectCheck:
        buffer = mc.ls(sl=True,flatten=True)
        sourceObject = buffer[0]
        targetObjects = buffer[1:]


    if sourceObject:
        if targetObjects:
            mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(targetObjects),'Vert Weight Copying...')

            stepInterval = 1

            for obj in targetObjects:
                if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                    break
                mc.progressBar(mayaMainProgressBar, edit=True, status = ("copying '%s'"%obj), step=1)

                if search.returnObjectType(obj)=='polyVertex':
                    #progress
                    guiFactory.doUpdateProgressWindow(('On %s' %obj),stepInterval,len(targetObjects),True)

                    #function
                    skinning.copySkinWeightBetweenVertices( sourceObject, obj )

                    stepInterval += 1

                elif search.returnObjectType(obj)=='polyEdge':
                    #progress

                    #function
                    mel.eval("PolySelectConvert 3")
                    edgeVerts = mc.ls(sl=True,fl=True)
                    edgeVerts = lists.returnListNoDuplicates(edgeVerts)
                    for v in edgeVerts:
                        skinning.copySkinWeightBetweenVertices( sourceObject, v )

                    stepInterval += 1
                else:
                    guiFactory.warning("%s isn't a transferable component" %obj)

            guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

        else:
            guiFactory.warning('You need target objects selected')
    else:
        guiFactory.warning('You need a source object selected or loaded')




def doSelectInfluenceJoints():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for selecting the influence objects from a mesh with a skinCluster

    REQUIRES:
    A selection or a set cgmVarSourceObject

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    selected = mc.ls(sl=True,flatten=True)

    if selected:
        influenceList = []
        for obj in selected:
            skinCluster = skinning.querySkinCluster(obj)
            if skinCluster:
                influenceList.extend(skinning.queryInfluences(skinCluster))
            else:
                guiFactory.warning('%s has no skinCluster' %obj)
        mc.select(cl=True)
        if influenceList:
            mc.select(influenceList)
        else:
            guiFactory.warning('No Influences found')
    else:
        guiFactory.warning('Must have something selected')


def doReturnExcessInfluenceVerts(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for finding vertices that are over X influences

    REQUIRES:
    A selection or a set cgmVarSourceObject

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    def returnProc(badVertices):
        if len(badVertices)>0:
            mc.select(badVertices, replace=True)
            print (guiFactory.doPrintReportStart())
            print ('%s%i%s%i%s' % ('There are ',(len(badVertices)),' verts are over the max influence (',maxInfluences,'):'))
            print badVertices
            print (guiFactory.doPrintReportEnd())
        else:
            guiFactory.warning('No verts over max influence')


    sourceObject = mc.optionVar(q='cgmVarSourceObject')
    maxInfluences = self.MaxVertsField(q=True,v=True)


    selected = mc.ls(sl=True,flatten=True)
    if skinning.querySkinCluster(selected[0]):
        badVertices = skinning.returnExcessInfluenceVerts(selected[0],maxInfluences)
        returnProc(badVertices)

    elif sourceObject:
        badVertices = skinning.returnExcessInfluenceVerts(sourceObject,maxInfluences)
        returnProc(badVertices)

    else:
        guiFactory.warning('You need a source object or an object with a skin cluster selected.')



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tool Commands
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>> moveSnap
def doParentSnap():
    batch.doObjToTargetFunctionOnSelected(position.moveParentSnap)
def doPointSnap():
    batch.doObjToTargetFunctionOnSelected(position.movePointSnap)
def doOrientSnap():
    batch.doObjToTargetFunctionOnSelected(position.moveOrientSnap)

def doLayoutByRowsAndColumns(self):
    mc.optionVar(iv=('cgmVarRowColumnCount',self.RowColumnIntField(q=True,v=True)))
    sortByName = mc.optionVar(q='cgmVarOrderByName')
    columnNumber = mc.optionVar(q='cgmVarRowColumnCount')
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    if selected:
	targetObject = selected[-1]
    if sortByName:
        selected.sort()
    if len(selected) >=2:
        position.layoutByColumns(selected,columnNumber)
    else:
        guiFactory.warning('You must have at least two objects selected')
    mc.select(selected)

def doCGMNameToFloat():
    returnBuffer = []
    for obj in  mc.ls(sl=True):
        returnBuffer.append(modules.cgmTagToFloatAttr(obj,'cgmName'))
    return returnBuffer

#>>> Aim Snap
def doAimSnapToOne():
    aimVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarObjectAimAxis'))
    upVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarObjectUpAxis'))
    worldUpVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarWorldUpAxis'))
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    if len(selected) >=2:
        for item in selected[:-1]:
            print ('on ' + item)
            bufferList.append(position.aimSnap(item,selected[-1],aimVector,upVector,worldUpVector))
        return bufferList
    else:
        guiFactory.warning('You must have at least two objects selected')

def doAimSnapOneToNext():
    aimVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarObjectAimAxis'))
    upVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarObjectUpAxis'))
    worldUpVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarWorldUpAxis'))
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    if len(selected) >=2:
        parsedList = lists.parseListToPairs(selected)
        print parsedList
        for pair in parsedList:
            print ('on ' + pair[0])
            bufferList.append(position.aimSnap(pair[0],pair[1],aimVector,upVector,worldUpVector))
        return bufferList
    else:
        guiFactory.warning('You must have at least two objects selected')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Position
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doSnapClosestPointToSurface(aim=True):
    #mode 0 - normal, 1 - where it was
    aimVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarObjectAimAxis'))
    upVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarObjectUpAxis'))
    worldUpVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVarWorldUpAxis'))

    aimMode = mc.optionVar(q='cgmVarSurfaceSnapAimMode')

    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    if len(selected) >=2:
        ### Counter start ###
        mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(selected),'Snapping...')
        itemCnt = 0
        ### Counter start ###
        nurbsCurveCase = False
        if search.returnObjectType(selected[-1]) == 'nurbsCurve':
            nurbsCurveCase ==True
            nurbsCurveAimLoc = locators.locMeObject(selected[-1],True)
        for item in selected[:-1]:
            ### Counter Break ###
            if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                break
            mc.progressBar(mayaMainProgressBar, edit=True, status = ("Snapping '%s'"%item), step=1)

            ### Counter Break ###
            aimLoc = locators.locMeObject(item)
            bufferLoc = locators.locClosest([item],selected[-1])
            position.movePointSnap(item,bufferLoc)
            if aim:
                if aimMode:
                    if nurbsCurveCase:
                        position.aimSnap(item,nurbsCurveAimLoc,aimVector,upVector,worldUpVector)
                    else:
                        position.aimSnap(item,aimLoc,aimVector,upVector,worldUpVector)
                else:
                    if nurbsCurveCase:
                        mc.move(5, 0, 0,bufferLoc,os=True, r=True)
                        position.aimSnap(item,bufferLoc,aimVector,upVector,worldUpVector)
                    else:
                        position.aimSnap(item,aimLoc,aimVector,upVector,worldUpVector)


            itemCnt += 1
            mc.delete([bufferLoc,aimLoc])
            if nurbsCurveCase:
                mc.delete(nurbsCurveAimLoc)


        guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
        return bufferList
    else:
        guiFactory.warning('You must have at least two objects selected')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Curve Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#['Object','1.25 x size', '1/2 Object size','Average','Input Size','First Object']
def returnObjectSizesForCreation(self,objList):
    if self.sizeMode == 4:
        return ( mc.floatField(self.textObjectSizeField,q=True,value=True) )
    else:
	if self.sizeMode == 1:
	    divider = .9
	elif self.sizeMode == 2:
	    divider = 2
	else:
	    divider = 1
        sizeList = []
        for item in objList:
            child = mc.listRelatives(item,children = True, type = 'transform',path = True)
            if child:
                sizeBuffer = (distance.returnDistanceBetweenObjects(item,child)/divider)
                if sizeBuffer <= 0:
                    parent = mc.listRelatives(item,parent = True, type = 'transform')
                    sizeList.append( (distance.returnDistanceBetweenObjects(parent,item)/divider) )
                else:
                    sizeList.append( (distance.returnDistanceBetweenObjects(item,child)/divider) )
            else:
                objSize = distance.returnBoundingBoxSize(item)
                sizeAverage = max(objSize)
                if sizeAverage <= 0:
                    parent = mc.listRelatives(item,parent = True, type = 'transform', path = True)
                    sizeList.append( (distance.returnDistanceBetweenObjects(parent,item)/divider))
                else:
                    sizeList.append( sizeAverage/divider )
        if self.sizeMode == 3:
            return ( sum(sizeList)/len(sizeList) )
        elif self.sizeMode == 5:
            return sizeList[0]
        else:
            return sizeList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>> Text Curve Objects Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doCreateTextCurveObject(self):
    textCheck = mc.textField(self.textObjectTextField,q=True,text=True)
    self.textObjectFont = mc.optionVar( q='cgmVarFontOption' )
    colorChoice = mc.optionVar(q='cgmVarDefaultOverrideColor')

    if textCheck:
        self.textObjectText = self.textObjectTextField(q=True,text=True)
        self.textObjectSize = mc.floatField(self.textObjectSizeField,q=True,value=True)
        textObjectsToMake = []
        print self.textObjectText
        if ';' in self.textObjectText:
            textObjectsToMake = self.textObjectText.split(';')
        print textObjectsToMake
        if len(textObjectsToMake):
            for word in textObjectsToMake:
                self.textCurrentObject = curves.createTextCurveObject(word,self.textObjectSize,None, font = self.textObjectFont)
                mc.textField(self.textCurrentObjectField,edit=True,text = self.textCurrentObject )
                curves.setCurveColorByIndex(self.textCurrentObject,colorChoice)
        else:
            self.textCurrentObject = curves.createTextCurveObject(self.textObjectText,self.textObjectSize,None, font = self.textObjectFont)
            mc.textField(self.textCurrentObjectField,edit=True,text = self.textCurrentObject )
            curves.setCurveColorByIndex(self.textCurrentObject,colorChoice)


def doSetCurveColorByIndex(colorIndex):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    if selected:
        for obj in selected:
            curves.setCurveColorByIndex(obj,colorIndex)

    else:
        guiFactory.warning('You must select something.')


def doLoadTexCurveObject(self):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    if selected:
        if len(selected) >= 2:
            guiFactory.warning('Only one cgmTextCurve can be loaded')
        else:
            if search.returnTagInfo(selected[0],'cgmObjectType') != 'textCurve':
                guiFactory.warning('Selected object is not a cgmTextCurve object')
            else:
                mc.textField(self.textCurrentObjectField,edit=True,ut = 'cgmUILockedTemplate', text = selected[0],editable = False )
                uiLoadTextCurveObject(self)
    else:
        guiFactory.warning('You must select something.')


def uiLoadTextCurveObject(self):
    textCurveObject = mc.textField(self.textCurrentObjectField ,q=True,text=True)
    objAttrs = attributes.returnUserAttrsToDict(textCurveObject)
    mc.textField(self.textObjectTextField,e=True,text=(objAttrs['cgmObjectText']))
    mc.floatField(self.textObjectSizeField,e=True,value=(float(objAttrs['cgmObjectSize'])))


def doUpdateTextCurveObject(self):
    #Get variables
    self.renameObjectOnUpdate = mc.optionVar(q='cgmVarRenameOnUpdate')
    self.textObjectFont =  mc.optionVar(q='cgmVarFontOption')
    self.changeFontOnUpdate = mc.optionVar(q='cgmVarChangeFontOnUpdate')
    textCurveObject = mc.textField(self.textCurrentObjectField ,q=True,text=True)
    selected = mc.ls(sl=True)
    
    #>>> Doing the stuff
    if selected:
	mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(selected))			
        for obj in selected:
            updatedObjects = []
	    
            #Progress bar
	    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		    break
	    mc.progressBar(mayaMainProgressBar, edit=True, status = ("Checking '%s'"%obj), step=1)
            
            # If the object is a text curve object, we have stuff to do
            if search.returnTagInfo(obj,'cgmObjectType') == 'textCurve':
                self.textObjectText = mc.textField(self.textObjectTextField,q=True,text=True)				
                
                #If the object selected is the loaded object, we need to grab the info there.
                if obj == textCurveObject:
                    # Get our variables
                    self.textObjectText = mc.textField(self.textObjectTextField,q=True,text=True)
                    self.textObjectSize = mc.floatField(self.textObjectSizeField,q=True,value=True)
        
                    # Store the data on on the object
                    attributes.storeInfo(obj,'cgmObjectText',self.textObjectText)
                    attributes.storeInfo(obj,'cgmObjectSize',self.textObjectSize)
                    
                    
                    if self.renameObjectOnUpdate:
                        attributes.storeInfo(obj,'cgmName',self.textObjectText)
                        obj = autoname.doNameObject(obj)                    
                 
                if self.changeFontOnUpdate:
                    attributes.storeInfo(obj,'cgmObjectFont',self.textObjectFont) 
                buffer = curves.updateTextCurveObject(obj)	
                  
                updatedObjects.append(buffer)
                guiFactory.warning("'%s' updated"%buffer)
		
	guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

        if updatedObjects:
            mc.select(buffer)
            doLoadTexCurveObject(self)
            namingToolsLib.uiLoadAutoNameObject(self)            
            mc.select(updatedObjects)
            return

    elif textCurveObject:
        if mc.objExists(textCurveObject) and search.returnTagInfo(textCurveObject,'cgmObjectType') == 'textCurve':
            # Get our variables
            self.textObjectText = mc.textField(self.textObjectTextField,q=True,text=True)
            self.textObjectSize = mc.floatField(self.textObjectSizeField,q=True,value=True)

            # Store the data on on the object
            attributes.storeInfo(textCurveObject,'cgmObjectText',self.textObjectText)
            attributes.storeInfo(textCurveObject,'cgmObjectSize',self.textObjectSize)
            if self.changeFontOnUpdate:
                print 'YESSSSS'                
                attributes.storeInfo(textCurveObject,'cgmObjectFont',self.textObjectFont)

            textCurveObject = curves.updateTextCurveObject(textCurveObject)

            if self.renameObjectOnUpdate:
                attributes.storeInfo(textCurveObject,'cgmName',self.textObjectText)
                textCurveObject = autoname.doNameObject(textCurveObject)

            # Put our updated object info
            mc.textField(self.textCurrentObjectField,edit=True,ut = 'cgmUILockedTemplate', text = textCurveObject,editable = False )

            uiLoadTextCurveObject(self)
            namingToolsLib.uiLoadAutoNameObject(self)                        
            guiFactory.warning("'%s' updated"%textCurveObject)


    else:
        uiLoadTextCurveObject(self)        
        guiFactory.warning('No textCurveObject loaded or selected')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>Curve Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doCreateOneOfEachCurve(self):
    bufferList = []
    mc.select(cl=True)
    colorChoice = mc.optionVar(q='cgmVarDefaultOverrideColor')
    creationSize = mc.floatField(self.textObjectSizeField,q=True,value=True)
    self.uiCurveAxis = mc.optionVar(q='cgmVarObjectAimAxis')
    
    #Info
    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(self.curveOptionList))		    
    for option in self.curveOptionList:
	if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		break
	mc.progressBar(mayaMainProgressBar, edit=True, status = ("Procssing '%s'"%option), step=1)
	
	buffer = curves.createControlCurve(option,creationSize,self.uiCurveAxis )
	attributes.storeInfo(buffer,'cgmName',option)	
	buffer = autoname.doNameObject(buffer)
	curves.setCurveColorByIndex(buffer,colorChoice)
	bufferList.append(buffer)
	
    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
    mc.select(bufferList)
    
def doCurveControlCreate(self):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    colorChoice = mc.optionVar(q='cgmVarDefaultOverrideColor')

    #Info
    self.uiCurveName = self.uiCurveNameField(q=True,text=True)
    curveChoice = self.shapeOptions(q=True,sl=True)
    shapeOption =  self.curveOptionList[curveChoice-1]
    self.uiCurveAxis = mc.optionVar(q='cgmVarObjectAimAxis')
    self.sizeMode = mc.optionVar( q='cgmVarSizeMode' )
    makeVisControl =  self.MakeVisControlCB(q=True, value=True)
    makeSettingsControl =  self.MakeSettingsControlCB(q=True, value=True)

    if self.MakeMasterControlCB(q=True, value=True):
        if selected:
            size = max(distance.returnBoundingBoxSize(selected))
            if self.uiCurveName:
                bufferList.append( controlBuilder.createMasterControl(self.uiCurveName,size,self.textObjectFont,makeSettingsControl,makeVisControl))
            else:
                bufferList.append( controlBuilder.createMasterControl('char',size,self.textObjectFont,makeSettingsControlControl,makeVisControl))

        else:
            guiFactory.warning('Pick something for size reference')
    else:
        if selected:
            sizeReturn = returnObjectSizesForCreation(self,selected)
            #['Object','1/2 object','Average','Input Size','First Object']
            mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(selected))		
            for item in selected:
                if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                    break
                mc.progressBar(mayaMainProgressBar, edit=True, status = ("Creating curve for '%s'"%item), step=1)


                if self.sizeMode in [0,1,2]:
                    creationSize = sizeReturn[selected.index(item)]
                else:
                    creationSize = sizeReturn
                buffer = curves.createControlCurve(shapeOption,creationSize,self.uiCurveAxis )
                attributes.storeInfo(buffer,'cgmName',item)
		attributes.storeInfo(buffer,'cgmSource',item)
                buffer = autoname.doNameObject(buffer)

                if self.forceBoundingBoxState == True:
                    locBuffer = locators.locMeObject(item, self.forceBoundingBoxState)
                    position.moveParentSnap(buffer,locBuffer)
                    mc.delete(locBuffer)
                else:
                    position.moveParentSnap(buffer,item)

                curves.setCurveColorByIndex(buffer,colorChoice)
		bufferList.append(buffer)
            guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
	    
        else:
            print shapeOption
            print self.uiCurveAxis
            buffer = curves.createControlCurve(shapeOption,1,self.uiCurveAxis )
            print buffer
            print self.uiCurveName
            if self.uiCurveName:
                attributes.storeInfo(buffer,'cgmName',self.uiCurveName)
            else:
                attributes.storeInfo(buffer,'cgmName',shapeOption)
            buffer = autoname.doNameObject(buffer)
            curves.setCurveColorByIndex(buffer,colorChoice)
	    bufferList.append(buffer)
	    
    if bufferList:
	mc.select(bufferList[-1])
	namingToolsLib.uiLoadAutoNameObject(self)            
	mc.select(bufferList)	    

def doCurveControlConnect(self):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    
    if not selected:
	guiFactory.warning("Nothing is selected")
	return
    
    #>>> Variables
    #ConnectionTypes = ['Constrain','Direct','Shape Parent','Parent','Child']
    ConnectBy = self.ConnectionTypes[ mc.optionVar(q='cgmControlConnectionType') ]
    ConstraintMode = self.ConnectionTypes[ mc.optionVar(q='cgmControlConstraintType') ]
    
    ScaleConstraintState = self.ScaleConstraintCB(q=True,v=True)
    RotateOrderState = self.controlCurveRotateOrderCB(q=True,v=True)
    ExtraGroupState = self.CurveControlExtraGroupCB(q=True,v=True)
    HeirarchyState = self.CurveControlHeirarchyCB(q=True,v=True)
    
    for obj in selected:
	obj = objectFactory.go(obj)
	if 'cgmSource' in obj.userAttrs.keys():
	    source = objectFactory.go(obj.userAttrs.get('cgmSource'))
	    guiFactory.warning("'%s' is the source"%source.nameBase)
	    
	    if ConnectBy == 'ShapeParent':
		curves.parentShapeInPlace(source.nameLong,obj.nameLong)
		mc.delete(obj.nameLong)
		
	    elif ConnectBy == 'ChildOf':
		guiFactory.warning('CHILD MODE!')
		rigging.doParentReturnName(obj.nameLong,source.nameLong)
		
	    elif ConnectBy == 'ParentTo':
		guiFactory.warning('PARENT MODE!')
		rigging.doParentReturnName(source.nameLong,obj.nameLong)
		
	    elif ConnectBy == 'Constraint':
		groupBuffer = rigging.groupMeObject(obj.nameLong,True,True)
		obj.update(obj.nameBase)
		ConstraintGroup = rigging.groupMeObject(obj.nameLong,True,True)
		obj.update(obj.nameBase)
		
		mc.parentConstraint(obj.nameLong,source.nameLong,maintainOffset = False)
		#attributes.doConnectAttr(obj.nameLong + '.t',source.nameLong + '.t')
		#attributes.doConnectAttr(obj.nameLong + '.r',source.nameLong + '.r')
		
		
	    else:
		guiFactory.warning('Got to the end!')
	    #groupBuffer = rigging.groupMeObject(obj.nameLong)
	    #obj.update(obj.nameBase)
	    
	else:
	    guiFactory.warning("'%s' has no source"%obj.nameBase)

    

    
def doCreateCurveFromObjects():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a curve from a selection of objects

    REQUIRES:
    Active Selection

    RETURNS:
    curveName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)

    if len(selected)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    try:
        return curves.curveFromObjList(selected)
    except:
        guiFactory.warning('Houston, we have a problem')

def uiSetGuessOrientation(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Guess an objects orientation

    REQUIRES:
    Active Selection

    RETURNS:
    curveName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    aimFromObject = []
    aimToObject = []
    # set world regardless of selection
    worldUp = mc.upAxis(q=True,axis=True)		
    worldAxis = logic.axisFactory(worldUp)	
    if worldAxis:
        index = self.axisOptions.index(worldAxis.axisString)
        mc.optionVar( sv=('cgmVarWorldUpAxis', worldAxis.axisString) )
        menuItems = self.WorldUpCollection.getItems()
        menuItems[index](edit = True,rb = True)	
        print("worldUp set to '%s'"%worldAxis.axisString)	


    if selected:
        aimAxis = []
        upAxis = []	
        child = mc.listRelatives(selected[0],children = True, type = 'transform',path = True)
        parent = mc.listRelatives(selected[0],parent = True, type = 'transform',path = True)
        if parent:
            aimFromObject = parent[0]
            aimToObject = selected[0]
        elif child:
            aimFromObject = selected[0]
            aimToObject = child[0]			

        if aimFromObject and aimToObject:
            aim = logic.returnLocalAimDirection(aimFromObject,aimToObject)
            up = logic.returnLocalUp(aim)	
            aimAxis = logic.axisFactory(aim)
            upAxis = logic.axisFactory(up)

        else:
            aimAxis = logic.axisFactory('z+')
            upAxis = logic.axisFactory('y+')			

        if aimAxis:
            index = self.axisOptions.index(aimAxis.axisString)
            mc.optionVar( sv=('cgmVarObjectAimAxis', aimAxis.axisString) )
            menuItems = self.ObjectAimCollection.getItems()
            menuItems[index](edit = True,rb = True)
            guiFactory.warning("aim set to '%s'"%aimAxis.axisString)

        if upAxis:
            index = self.axisOptions.index(upAxis.axisString)
            mc.optionVar( sv=('cgmVarObjectUpAxis', upAxis.axisString) )
            menuItems = self.ObjectUpCollection.getItems()
            menuItems[index](edit = True, rb = True)
            guiFactory.warning("up set to '%s'"%upAxis.axisString)			
    else:
        guiFactory.warning("No objects selected. Setting defaults of 'z+' aim, 'y+' up")
        aimIndex = self.axisOptions.index('z+')
        mc.optionVar( sv=('cgmVarObjectAimAxis', 'z+') )
        menuItems = self.ObjectAimCollection.getItems()
        menuItems[aimIndex](edit = True,rb = True)	

        upIndex = self.axisOptions.index('y+')
        mc.optionVar( sv=('cgmVarObjectUpAxis', 'y+') )
        menuItems = self.ObjectUpCollection.getItems()
        menuItems[upIndex](edit = True,rb = True)
    
    if selected:
        mc.select(selected)


def doShapeParent():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    REQUIRES:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)

    if len(selected)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    for obj in selected[1:]:
        try:
            curves.parentShape(obj,selected[0])
        except:
            guiFactory.warning(obj + ' failed')

def doShapeParentInPlace():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    REQUIRES:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)

    if len(selected)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    for obj in selected[1:]:
        curves.parentShapeInPlace(obj,selected[0])
	
def doReplaceCurveShapes():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    REQUIRES:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)

    if len(selected)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False
    
    originalShapes = mc.listRelatives (selected[-1], f= True,shapes=True)
    
    for obj in selected[:-1]:
	curves.parentShapeInPlace(selected[-1],obj)
	
    if originalShapes:
	for shape in originalShapes:
	    try:
		mc.delete(shape)
	    except:
		guiFactory.warning("'%s' failed to delete"%shape)
    


def doCurveToPython():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    REQUIRES:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    if selected:
        for obj in selected:
            if search.returnObjectType(obj) in ['nurbsCurve','shape']:
                curves.curveToPython(obj)
            else:
                guiFactory.warning(obj + ' is not a curve or shape. Moving on...')

    else:
        guiFactory.warning('You must select something.')

def doCombineCurves():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Combines curves on the first curves transform

    REQUIRES:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    if selected:
        goodObjects = []
        for obj in selected:
            if search.returnObjectType(obj) in ['nurbsCurve','shape']:
                goodObjects.append(obj)
            else:
                guiFactory.warning(obj + ' is not a curve or shape. Moving on...')
        if len(goodObjects) >=2:
            curves.combineCurves(goodObjects)
        else:
            guiFactory.warning('You need at least two curves.')

    else:
        guiFactory.warning('You must select something.')

def doReportObjectType():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    REQUIRES:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    for obj in selected:
        objType = search.returnObjectType(obj)
        print (">>> '" + obj + "' == " + objType)
    print 'done'

def doReportSelectionCount():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reports the number of selected items

    REQUIRES:
    Active Selection

    RETURNS:
    int(number)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    count = len(mc.ls(sl=True,flatten=True))
    guiFactory.warning('There are %i items selected.' % count)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Group stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def zeroGroupMe():
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    if selected:
        for obj in selected:
            rigging.zeroTransformMeObject(obj)

    else:
        guiFactory.warning('You must select something.')

def makeTransformHere():
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    if selected:
        for obj in selected:
            rigging.groupMeObject(obj,False)

    else:
        guiFactory.warning('You must select something.')

def doGroupMeInPlace():
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    if selected:
        for obj in selected:
            rigging.groupMeObject(obj,True,True)

    else:
        guiFactory.warning('You must select something.')
def doCopyPivot():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copies the pivot from the first object to all other objects

    REQUIRES:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)

    if len(selected)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    for obj in selected[1:]:
        try:
            rigging.copyPivot(obj,selected[0])
        except:
            guiFactory.warning(obj + ' failed')