#=================================================================================================================================================
#=================================================================================================================================================
#	tdToolsLib - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Library of functions for the cgmRiggingTools tool
#
# ARGUMENTS:
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

from cgm.lib.classes import DraggerContextFactory
reload(DraggerContextFactory)

from cgm.lib.zoo.zooPyMaya import skinWeights
from cgm.lib.cgmBaseMelUI import *
from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes.ControlFactory import *
from cgm.lib.classes.DraggerContextFactory import *

from cgm.lib.classes import NameFactory 


from cgm.lib import (guiFactory,
                     controlBuilder,
                     constraints,
                     curves,
                     dictionary,
                     search,
                     deformers,
                     modules,
                     logic,
                     rigging,
                     locators,
                     attributes,
                     batch,
                     distance,
                     position,
                     lists,
                     sdk,
                     skinning)

from cgm.tools.lib import locinatorLib,namingToolsLib

reload(curves)
reload(position)
reload(attributes)
reload(NameFactory)
reload(guiFactory)
reload(modules)
reload(controlBuilder)
"""

"""
def loadZooSkinPropagation( *a ):
    from zooPyMaya import refPropagation
    refPropagation.propagateWeightChangesToModel_confirm()

def uiSetSelfVariable(self,variable,value):
    print variable
    print value
    self.variable = value

def loadJTDDynamicParent():
    mel.eval('source JTDDynParentUI;')
    
def tempLoadSDKToGraphEditor():
    mel.eval('source jbGraphSetDrivenAttribute;')   

def loadGUIOnStart(self):
    selection = mc.ls(sl=True) or []
    try:
	if selection:
	    for obj in selection:
		if search.returnTagInfo(selection[0],'cgmObjectType') == 'textCurve':
		    if mc.optionVar( q='cgmVar_AutoloadTextObject' ):
			mc.select(selection[0])
			TextCurveObjectdoLoad(self)
			break
	    
	    if mc.optionVar( q='cgmVar_AutoloadAutoname' ):
		mc.select(selection[0])
		namingToolsLib.uiLoadAutoNameObject(self)
		    
	if selection:
	    mc.select(selection)
    except:
	pass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# SDK
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doSelectDrivenJoints(self):
    selection = mc.ls(sl=True) or []
    mc.select(cl=True)
    channelBoxName = search.returnMainChannelBoxName()

    # Get the attrs
    selectionAttrs = mc.channelBox(channelBoxName,q=True, sma=True)

    fullAttrs = []
    if selectionAttrs:
        for attr in selectionAttrs:
            fullAttrs.append(selection[0]+'.'+attr)
        for fullAttr in fullAttrs:
            drivenJoints = sdk.returnDrivenJoints(fullAttr)
            if drivenJoints:
                mc.select(drivenJoints)
            else:
                guiFactory.warning('No driven joints found')
    else:
        guiFactory.warning('No selection attributes found')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Mesh Click
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiUpdate_ClickMeshTargetField(self):
    if self.ClickMeshTargetOptionVar.value:
	print self.ClickMeshTargetOptionVar.value
	if len(self.ClickMeshTargetOptionVar.value) == 1:
	    self.ClickMeshTargetsField(edit=True, text = "%s"%(self.ClickMeshTargetOptionVar.value[0]))	    
	else:
	    self.ClickMeshTargetsField(edit=True, text = "'%s'"%"','".join(self.ClickMeshTargetOptionVar.value))
    else:
	self.ClickMeshTargetsField(edit=True, text = "")
	
def uiUpdate_ClickMeshClampField(self):
    if self.ClickMeshClampOptionVar.value:
	if len(self.ClickMeshTargetOptionVar.value) > 0:
	    self.ClickMeshClampIntField(edit=True, value =  self.ClickMeshClampOptionVar.value)    
	else:
	    self.ClickMeshClampIntField(edit=True, value = self.ClickMeshClampOptionVar.value)

def uiLoadClickMeshTargets(self):
    """ 
    Loads target objects and updates menus

    Keyword arguments:
    selectAttr(string) -- Name of an attr (False ignores)
    """   
    selection = mc.ls(sl=True) or []
    self.ClickMeshTargetOptionVar.clear()
    if not selection:
	self.ClickMeshTargetsField(edit=True, text = "")	
	guiFactory.warning("Nothing selected")
	return
    
    if selection:
	for o in selection:
	    if search.returnObjectType(o) == 'mesh':
		self.ClickMeshTargetOptionVar.append(o)
	    else:
		guiFactory.warning("'%s' is not a mesh object. Ignoring"%o)
		
    uiUpdate_ClickMeshTargetField(self)

	
def uiClickMeshToolLaunch(self):
    """ 
    Launches the ClickMesh tool

    Keyword arguments:
    selectAttr(string) -- Name of an attr (False ignores)
    """
    doMesh = []
    if not self.ClickMeshTargetOptionVar.value:
	raise StandardError("No suitable mesh found")
    else:
	for o in self.ClickMeshTargetOptionVar.value:
	    if not mc.objExists(o):
		guiFactory.warning("'%s' doesn't exist. Not included!"%o)
	    else:
		doMesh.append(o)
	    
    if not doMesh:
	raise StandardError("No suitable mesh found")
    
    
    
    self.ClickMeshTool = DraggerContextFactory.clickMesh( mesh = doMesh,
                                                          closestOnly = True,
                                                          dragStore=False,
                                                          clampIntersections = self.ClickMeshClampOptionVar.value)
    
    self.ClickMeshTool.setMode(self.ClickMeshTool.modes[self.ClickMeshModeOptionVar.value])
    self.ClickMeshTool.setCreate(self.ClickMeshTool.createModes[self.ClickMeshBuildOptionVar.value])  
    self.ClickMeshTool.setDragStoreMode(self.ClickMeshDragStoreOptionVar.value)  
    
def uiClickMesh_setDragStore(self,i):
    """ 
    Sets drag store mode

    Keyword arguments:
    selectAttr(string) -- Name of an attr (False ignores)
    """
    self.ClickMeshDragStoreOptionVar.set(i)
    
    if self.ClickMeshTool:
	self.ClickMeshTool.setDragStoreMode(bool(i))  
	
def uiClickMesh_changeMode(self,i):
    """ 
    Loads target objects and updates menus

    Keyword arguments:
    selectAttr(string) -- Name of an attr (False ignores)
    """   
    self.ClickMeshModeOptionVar.set(i)
    
    if self.ClickMeshTool:
	self.ClickMeshTool.setMode(self.ClickMeshTool.modes[self.ClickMeshModeOptionVar.value])

def uiClickMesh_changeCreateMode(self,i):
    """ 
    Loads target objects and updates menus

    Keyword arguments:
    selectAttr(string) -- Name of an attr (False ignores)
    """   
    self.ClickMeshBuildOptionVar.set(i)
    
    if self.ClickMeshTool:
	self.ClickMeshTool.setCreate(self.ClickMeshTool.createModes[self.ClickMeshBuildOptionVar.value])

def uiClickMesh_setClamp(self):
    """ 
    Loads target objects and updates menus

    Keyword arguments:
    selectAttr(string) -- Name of an attr (False ignores)
    """
    print "asdfasdfasdfasdfasdfasdf"
    buffer = self.ClickMeshClampIntField(q=True, value=True)
    
    if buffer >= 0:
	self.ClickMeshClampOptionVar.set(buffer)
	self.ClickMeshClampIntField(e=True, value=buffer)
	if self.ClickMeshTool:
	    self.ClickMeshTool.setClamp(buffer)
    else:
	self.ClickMeshClampIntField(e=True, value=self.ClickMeshClampOptionVar.value)
	guiFactory.warning("%s is an invalid value. Try again!"%buffer)
    
	
def uiClickMesh_dropTool(self,):
    """ 
    Finalize the tool

    Keyword arguments:
    selectAttr(string) -- Name of an attr (False ignores)
    """
    assert self.ClickMeshTool, "There is no clickMesh tool active"
    if self.ClickMeshTool:
	self.ClickMeshTool.finalize()
	self.ClickMeshTool = False
	
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Attribute Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doDeformerKeyableAttributesConnect(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for connecting the animateable attributes of a deformer to another object
    ARGUMENTS:
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
        targetObjectsBuffer = mc.optionVar(q='cgmVar_TargetObjects')
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

    ARGUMENTS:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    selection = mc.ls(sl=True, flatten = True)
    if selection:
        if search.returnObjectType(selection[0]) is 'polyUnite':
            self.SourceObjectField(edit = True, text = selection[0])
            uniteNode = selection[0]
        else:
            buffer = deformers.returnPolyUniteNodeFromResultGeo(selection[0])
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

    ARGUMENTS:
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

    ARGUMENTS:
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
        targetObjectsBuffer = mc.optionVar(q='cgmVar_TargetObjects')
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
        return guiFactory.warning('Either selection meshes or target objects required')

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

    ARGUMENTS:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    selection = mc.ls(sl=True, flatten = True) or []
    if selection:
        poseBufferCandidate = selection[0]
        self.SourceObjectField(edit = True, text = poseBufferCandidate)

        #Check for a connected blendshape node
        blendShapeSearchBuffer = deformers.returnBlendShapeNodeFromPoseBuffer(poseBufferCandidate)
        if blendShapeSearchBuffer:
            guiFactory.doLoadMultipleObjectsToTextField(self.TargetObjectField,blendShapeSearchBuffer,'cgmVar_TargetObjects')
        else:
            return (guiFactory.warning('No connected blendShape node found'))
    else:
        return (guiFactory.warning('Please select a poseBuffer'))



def doCreatePoseBuffer(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for extracting blendshapes from an object that may have had the targets deleted

    ARGUMENTS:
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

    DoConnectCase = mc.optionVar(q='cgmVar_PoseBufferDoConnect') 
    TransferConnectionsCase = mc.optionVar(q='cgmVar_PoseBufferTransferConnections') 


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

    ARGUMENTS:
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
        #targetObjectsBuffer = mc.optionVar(q='cgmVar_TargetObjects')
        if ';' in targetObjectsBuffer:
            targetObjects = targetObjectsBuffer.split(';')
        else:
            targetObjects = [targetObjectsBuffer]

    RemoveMissingCase = mc.optionVar(q='cgmVar_PoseBufferDoRemoveMissing')
    DoConnectCase = mc.optionVar(q='cgmVar_PoseBufferDoConnect')
    TransferConnectionsCase = mc.optionVar(q='cgmVar_PoseBufferTransferConnections')


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

    ARGUMENTS:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Get our variables from the ui and optionVars
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # Check for selection, defaults to using that for targets
    sourceObject = mc.optionVar(q='cgmVar_SourceObject')
    #targetObjectsBuffer = self.TargetObjectField(query = True, text=True)
    targetObjectsBuffer = mc.optionVar(q='cgmVar_TargetObjects')
    if ';' in targetObjectsBuffer:
        targetObjects = targetObjectsBuffer.split(';')
    else:
        targetObjects = targetObjectsBuffer

    bakeInbetweensCase = mc.optionVar(q='cgmVar_BSBakeInbetweens')
    transferConnectionsCase = mc.optionVar(q='cgmVar_BSBakeTransferConnections')
    bakeCombineCase = mc.optionVar(q='cgmVar_BSBakeCombine')
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

    ARGUMENTS:
    ui(string) - ui window name under which our variables are stored.

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    sourceObject = mc.optionVar(q='cgmVar_SourceObject')
    bakeInbetweensCase = mc.optionVar(q='cgmVar_BSBakeInbetweens')
    transferConnectionsCase = mc.optionVar(q='cgmVar_BSBakeTransferConnections')
    bakeCombineCase = mc.optionVar(q='cgmVar_BSBakeCombine')
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

    ARGUMENTS:
    A selection or a set cgmVar_SourceObject

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    selection = mc.ls(sl=True,flatten=True) or []

    sourceObject = mc.optionVar(q='cgmVar_SourceObject')

    #see if we have selection stuff to work on
    if selection:
        # if the source object isn't loaded in the field, it tries to grab the last object selection
        if not sourceObject:
            sourceObject = selection[-1]
            targetObjects = selection[:-1]
        else:
            targetObjects = selection

    else:
        targetObjects = mc.optionVar(q='cgmVar_TargetObjects')


    if len(selection) >=1:

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
                guiFactory.warning('You need target objects selection or loaded to the target field')
        else:
            guiFactory.warning('You need a source object')
    else:
        guiFactory.warning('You need at least two objects')

    """
    selection = mc.ls(sl=True,flatten=True)
    if skinning.querySkinCluster(selection[0]):
        badVertices = skinning.returnExcessInfluenceVerts(selection[0],maxInfluences)
        returnProc(badVertices)

    elif sourceObject:
        badVertices = skinning.returnExcessInfluenceVerts(sourceObject,maxInfluences)
        returnProc(badVertices)

    else:
        guiFactory.warning('You need a source object or an object with a skin cluster selection.')
    """

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Skin Cluster Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doCopySkinningToVertFromSource():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    asdf

    ARGUMENTS:
    asdf

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    # Check for selection, defaults to using that for targets
    selection = mc.ls(sl=True,flatten=True) or []
    targetObjects = []

    if selection:
        for obj in selection:
            if search.returnObjectType(obj) == 'polyVertex':
                targetObjects.append(obj)
    else:
        targetObjectsBuffer = mc.optionVar(q='cgmVar_TargetObjects')

    sourceObject = mc.optionVar(q='cgmVar_SourceObject') 


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
            guiFactory.warning('You need target objects selection or loaded to the target field')
    else:
        guiFactory.warning('You need a source object')


def doTransferSkinning():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Transfers the skin weighting from one object to another

    ARGUMENTS:
    A selection or a set cgmVar_SourceObject

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    selection = mc.ls(sl=True,flatten=True) or []

    if selection:
        targetObjects = selection
    else:
        targetObjects = mc.optionVar(q='cgmVar_TargetObjects')

    sourceObject = mc.optionVar(q='cgmVar_SourceObject')

    if sourceObject:
        if targetObjects:
            for obj in targetObjects:

                skinWeights.transferSkinning( sourceObject, obj )

        else:
            guiFactory.warning('You need target objects selection or loaded to the target field')
    else:
        guiFactory.warning('You need a source object')

def doCopyWeightsFromFirstToOthers():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Transfers the skin weighting from one oomponent to another

    ARGUMENTS:
    A selection of vertices

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    sourceObject = mc.optionVar(q='cgmVar_SourceObject')
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
        guiFactory.warning('You need a source object selection or loaded')




def doSelectInfluenceJoints():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for selecting the influence objects from a mesh with a skinCluster

    ARGUMENTS:
    A selection or a set cgmVar_SourceObject

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Check for selection, defaults to using that for targets
    selection = mc.ls(sl=True,flatten=True) or []

    if selection:
        influenceList = []
        for obj in selection:
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

    ARGUMENTS:
    A selection or a set cgmVar_SourceObject

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


    sourceObject = mc.optionVar(q='cgmVar_SourceObject')
    maxInfluences = self.MaxVertsField(q=True,v=True)


    selection = mc.ls(sl=True,flatten=True) or []
    if skinning.querySkinCluster(selection[0]):
        badVertices = skinning.returnExcessInfluenceVerts(selection[0],maxInfluences)
        returnProc(badVertices)

    elif sourceObject:
        badVertices = skinning.returnExcessInfluenceVerts(sourceObject,maxInfluences)
        returnProc(badVertices)

    else:
        guiFactory.warning('You need a source object or an object with a skin cluster selection.')



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
def doMatchSnap():
    batch.doObjOnlyFunctionOnSelected(locinatorLib.doUpdateObj)
    

def doLayoutByRowsAndColumns(self):
    mc.optionVar(iv=('cgmVar_RowColumnCount',self.RowColumnIntField(q=True,v=True)))
    sortByName = mc.optionVar(q='cgmVar_OrderByName')
    columnNumber = mc.optionVar(q='cgmVar_RowColumnCount')
    bufferList = []
    selection = (mc.ls (sl=True,flatten=True)) or []
    mc.select(cl=True)
    if selection:
	targetObject = selection[-1]
    if sortByName:
        selection.sort()
    if len(selection) >=2:
        position.layoutByColumns(selection,columnNumber)
    else:
        guiFactory.warning('You must have at least two objects selected')
    mc.select(selection)

def doCGMNameToFloat():
    returnBuffer = []
    for obj in  mc.ls(sl=True):
        returnBuffer.append(modules.cgmTagToFloatAttr(obj,'cgmName',keyable = True))

    if returnBuffer:
	for i in returnBuffer:
	    if i:
		guiFactory.warning("'%s' created"%(i))

#>>> Aim Snap
def doAimSnapToOne():
    aimVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_ObjectAimAxis'))
    upVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_ObjectUpAxis'))
    worldUpVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_WorldUpAxis'))
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)
    if len(selection) >=2:
        for item in selection[:-1]:
            print ('on ' + item)
            bufferList.append(position.aimSnap(item,selection[-1],aimVector,upVector,worldUpVector))
        return bufferList
    else:
        guiFactory.warning('You must have at least two objects selected')

def doAimSnapOneToNext():
    aimVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_ObjectAimAxis'))
    upVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_ObjectUpAxis'))
    worldUpVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_WorldUpAxis'))
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)
    if len(selection) >=2:
        parsedList = lists.parseListToPairs(selection)
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
    aimVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_ObjectAimAxis'))
    upVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_ObjectUpAxis'))
    worldUpVector = dictionary.returnStringToVectors(mc.optionVar(q='cgmVar_WorldUpAxis'))

    aimMode = mc.optionVar(q='cgmVar_SurfaceSnapAimMode')

    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)
    
    if search.returnObjectType(selection[-1]) not in ['mesh','nurbsSurface','nurbsCurve']:
	guiFactory.warning("'%s' is not a mesh, nurbsSurface, or nurbsCurve"%selection[-1])
	return
    
    if len(selection) >=2:
        ### Counter start ###
        mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(selection),'Snapping...')
        nurbsCurveCase = False
        if search.returnObjectType(selection[-1]) == 'nurbsCurve':
            nurbsCurveCase = True
            nurbsCurveAimLoc = locators.locMeObject(selection[-1],True)
        for item in selection[:-1]:
            ### Counter Break ###
            if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                break
            mc.progressBar(mayaMainProgressBar, edit=True, status = ("Snapping '%s'"%item), step=1)

            ### Counter Break ###
            aimLoc = locators.locMeObject(item)
            bufferLoc = locators.locClosest([item],selection[-1])
	    if bufferLoc:
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
    
    
	    mc.delete([bufferLoc,aimLoc])
	    if nurbsCurveCase:
		mc.delete(nurbsCurveAimLoc)


        guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
	mc.select(selection)
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
	    o = ObjectFactory(item)
	    if o.mType == 'joint':
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
	    else:
		sizeList.append( max(distance.returnBoundingBoxSize(item))/divider )
        if self.sizeMode == 3:
            return ( sum(sizeList)/len(sizeList) )
        elif self.sizeMode == 5:
            return sizeList[0]
        else:
            return sizeList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>> Text Curve Objects Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def TextCurveObjectCreate(self):
    textCheck = mc.textField(self.textObjectTextField,q=True,text=True)
    self.textObjectFont = mc.optionVar( q='cgmVar_FontOption' )
    colorChoice = mc.optionVar(q='cgmVar_DefaultOverrideColor')

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
                curves.setColorByIndex(self.textCurrentObject,colorChoice)
        else:
            self.textCurrentObject = curves.createTextCurveObject(self.textObjectText,self.textObjectSize,None, font = self.textObjectFont)
            mc.textField(self.textCurrentObjectField,edit=True,text = self.textCurrentObject )
            curves.setColorByIndex(self.textCurrentObject,colorChoice)


def doSetCurveColorByIndex(colorIndex):
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    if selection:
        for obj in selection:
            curves.setColorByIndex(obj,colorIndex)

    else:
        guiFactory.warning('You must select something.')


def TextCurveObjectdoLoad(self):
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    if selection:
        if len(selection) >= 2:
            guiFactory.warning('Only one cgmTextCurve can be loaded')
        else:
            if search.returnTagInfo(selection[0],'cgmObjectType') != 'textCurve':
                guiFactory.warning('selection object is not a cgmTextCurve object')
            else:
                mc.textField(self.textCurrentObjectField,edit=True,ut = 'cgmUILockedTemplate', text = selection[0],editable = False )
                TextCurveObjectLoadUI(self)
    else:
        guiFactory.warning('You must select something.')


def TextCurveObjectLoadUI(self):
    textCurveObject = mc.textField(self.textCurrentObjectField ,q=True,text=True)
    objAttrs = attributes.returnUserAttrsToDict(textCurveObject)
    mc.textField(self.textObjectTextField,e=True,text=(objAttrs['cgmObjectText']))
    mc.floatField(self.textObjectSizeField,e=True,value=(float(objAttrs['cgmObjectSize'])))


def TextCurveObjectdoUpdate(self):
    #Get variables
    self.renameObjectOnUpdate = mc.optionVar(q='cgmVar_RenameOnUpdate')
    self.textObjectFont =  mc.optionVar(q='cgmVar_FontOption')
    self.changeFontOnUpdate = mc.optionVar(q='cgmVar_ChangeFontOnUpdate')
    textCurveObject = mc.textField(self.textCurrentObjectField ,q=True,text=True)
    selection = mc.ls(sl=True)
    
    #>>> Doing the stuff
    if selection:
	mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(selection))			
        for obj in selection:
            updatedObjects = []
	    
            #Progress bar
	    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		    break
	    mc.progressBar(mayaMainProgressBar, edit=True, status = ("Checking '%s'"%obj), step=1)
            
            # If the object is a text curve object, we have stuff to do
            if search.returnTagInfo(obj,'cgmObjectType') == 'textCurve':
                self.textObjectText = mc.textField(self.textObjectTextField,q=True,text=True)				
                
                #If the object selection is the loaded object, we need to grab the info there.
                if obj == textCurveObject:
                    # Get our variables
                    self.textObjectText = mc.textField(self.textObjectTextField,q=True,text=True)
                    self.textObjectSize = mc.floatField(self.textObjectSizeField,q=True,value=True)
        
                    # Store the data on on the object
                    attributes.storeInfo(obj,'cgmObjectText',self.textObjectText)
                    attributes.storeInfo(obj,'cgmObjectSize',self.textObjectSize)
                    
                    
                    if self.renameObjectOnUpdate:
                        attributes.storeInfo(obj,'cgmName',self.textObjectText)
                        obj = NameFactory.doNameObject(obj)                    
                 
                if self.changeFontOnUpdate:
                    attributes.storeInfo(obj,'cgmObjectFont',self.textObjectFont) 
                buffer = curves.updateTextCurveObject(obj)	
                  
                updatedObjects.append(buffer)
                guiFactory.warning("'%s' updated"%buffer)
		
	guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

        if updatedObjects:
            mc.select(buffer)
            TextCurveObjectdoLoad(self)
	    if mc.optionVar( q='cgmVar_AutoloadAutoname' ):
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
                textCurveObject = NameFactory.doNameObject(textCurveObject)

            # Put our updated object info
            mc.textField(self.textCurrentObjectField,edit=True,ut = 'cgmUILockedTemplate', text = textCurveObject,editable = False )

            TextCurveObjectLoadUI(self)
            namingToolsLib.uiLoadAutoNameObject(self)                        
            guiFactory.warning("'%s' updated"%textCurveObject)


    else:
        TextCurveObjectLoadUI(self)        
        guiFactory.warning('No textCurveObject loaded or selected')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>Curve Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doCreateOneOfEachCurve(self):
    bufferList = []
    mc.select(cl=True)
    colorChoice = mc.optionVar(q='cgmVar_DefaultOverrideColor')
    creationSize = mc.floatField(self.textObjectSizeField,q=True,value=True)
    self.uiCurveAxis = mc.optionVar(q='cgmVar_ObjectAimAxis')
    
    #Info
    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(self.curveOptionList))		    
    for option in self.curveOptionList:
	if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		break
	mc.progressBar(mayaMainProgressBar, edit=True, status = ("Procssing '%s'"%option), step=1)
	
	buffer = curves.createControlCurve(option,creationSize,self.uiCurveAxis )
	attributes.storeInfo(buffer,'cgmName',option)	
	buffer = NameFactory.doNameObject(buffer)
	curves.setColorByIndex(buffer,colorChoice)
	bufferList.append(buffer)
	
    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
    mc.select(bufferList)
    
def curveControlCreate(self):
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)
    colorChoice = mc.optionVar(q='cgmVar_DefaultOverrideColor')

    #Info
    self.uiCurveName = self.uiCurveNameField(q=True,text=True)
    curveChoice = self.shapeOptions(q=True,sl=True)
    shapeOption =  self.curveOptionList[curveChoice-1]
    self.uiCurveAxis = mc.optionVar(q='cgmVar_ObjectAimAxis')
    self.sizeMode = mc.optionVar( q='cgmVar_SizeMode' )
    makeVisControl =  self.MakeVisControlCB(q=True, value=True)
    makeSettingsControl =  self.MakeSettingsControlCB(q=True, value=True)
    makeRigGroups = self.MakeGroupsCB(q=True, value=True)
    
    

    if self.MakeMasterControlCB(q=True, value=True):
        if selection:
            size = max(distance.returnBoundingBoxSize(selection))
	else:
	    size = self.textObjectSizeField(q=True,value=True)
	    
	if self.uiCurveName:
	    bufferList = controlBuilder.createMasterControl(self.uiCurveName,size,self.textObjectFont,makeVisControl,makeSettingsControl,makeRigGroups)
	else:
	    bufferList = controlBuilder.createMasterControl('char',size,self.textObjectFont,makeVisControl,makeSettingsControl,makeRigGroups)
	
	self.MakeMasterControlCB(e=True, value=False)

    else:
        if selection:
            sizeReturn = returnObjectSizesForCreation(self,selection)
            #['Object','1/2 object','Average','Input Size','First Object']
            mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(selection))		
            for item in selection:
                if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                    break
                mc.progressBar(mayaMainProgressBar, edit=True, status = ("Creating curve for '%s'"%item), step=1)

                if self.sizeMode in [0,1,2]:
                    creationSize = sizeReturn[selection.index(item)]
                else:
                    creationSize = sizeReturn
		
		print shapeOption
		print creationSize
		print self.uiCurveAxis
                buffer = curves.createControlCurve(shapeOption,creationSize,self.uiCurveAxis )
		print "buffer is '%s'"%buffer
                attributes.storeInfo(buffer,'cgmName',item)
		attributes.storeInfo(buffer,'cgmSource',item)
                buffer = NameFactory.doNameObject(buffer)
                if self.forceBoundingBoxState == True:
		    guiFactory.warning("Forced Bounding box on")
                    locBuffer = locators.locMeObject(item, self.forceBoundingBoxState)
                    position.moveParentSnap(buffer,locBuffer)
                    mc.delete(locBuffer)
                else:
                    position.moveParentSnap(buffer,item)

                curves.setColorByIndex(buffer,colorChoice)
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
            buffer = NameFactory.doNameObject(buffer)
            curves.setColorByIndex(buffer,colorChoice)
	    bufferList.append(buffer)
	    
    if bufferList:
	if  mc.optionVar( q='cgmVar_AutoloadAutoname' ):
	    mc.select(bufferList[-1])
	    namingToolsLib.uiLoadAutoNameObject(self)  
	mc.select(bufferList)	    

def curveControlConnect(self):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Connects a curve control from the tdTools gui

    ARGUMENTS:
    self(class)

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    def updateTransform(curve,sourceObject):
	childrenToWorld = []	
	children = mc.listRelatives(curve,children=True,type = 'transform')
	if children:
	    for c in children:
		childrenToWorld.append(rigging.doParentToWorld(c))
	transform = rigging.groupMeObject(sourceObject,False,False)
	attributes.copyUserAttrs(curve,transform)
	buffer = curves.parentShapeInPlace(transform,curve)
	mc.delete(curve)
	if childrenToWorld:
	    for c in childrenToWorld:
		rigging.doParentReturnName(c,transform)
	return transform
    
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    
    if not selection:
	guiFactory.warning("Nothing is selection")
	return
    
    #>>> Variables
    #ConnectionTypes = ['Constrain','Direct','Shape Parent','Parent','Child']
    ConnectBy = self.ConnectionTypes[ mc.optionVar(q='cgmVar_ControlConnectionType') ]
    ConstraintMode = self.ConstraintTypes[ mc.optionVar(q='cgmVar_ControlConstraintType') ]
    
    ScaleState = self.ScaleConstraintCB(q=True,v=True)
    RotateOrderState = self.controlCurveRotateOrderCB(q=True,v=True)
    ExtraGroupState = self.CurveControlExtraGroupCB(q=True,v=True)
    LockNHideState = self.CurveControlLockNHideCB(q=True,v=True)
    
    HeirarchyState = self.CurveControlHeirarchyCB(q=True,v=True)
    HeirarchyMode = self.HeirBuildTypes[ mc.optionVar(q='cgmVar_HeirBuildType') ]
    
    # First loop to get info
    parentConstraintTargets = {}
    controlInstances = {}
    for cnt,o in enumerate(selection):
	obj = ObjectFactory(o)
	obj.store('cgmType','controlAnim')
	obj.doName()	
	selection[cnt] = obj.nameBase
	obj.getAttrs()
	
	if 'cgmSource' in obj.userAttrsDict.keys():
	    source = ObjectFactory(obj.userAttrsDict.get('cgmSource'))	
	    
	    buffer = updateTransform(obj.nameShort,source.nameShort)
	    obj.update(buffer)
	    obj.doName()

	    
	    if mc.objExists(source.parent):
		curveParentObj = search.returnObjectsConnectedToObj(source.parent,True)	
		
		if HeirarchyState and HeirarchyMode == 'match':
		    if curveParentObj:
			buffer = rigging.doParentReturnName(obj.nameLong,curveParentObj[0])
			obj.update(buffer)
		else:
		    parentConstraintTargets[obj.nameBase] = source.parent
	else:
	    return guiFactory.warning("'%s' has no source"%obj.nameBase)	    
			
    
    # Loop to connect stuff
    for cnt,o in enumerate(selection):
	obj = ControlFactory(o,RotateOrderState,True)
	obj.getAttrs()
	
	if 'cgmSource' in obj.userAttrsDict.keys():
	    source = ObjectFactory(obj.userAttrsDict.get('cgmSource'))    
	    
	    if ConnectBy == 'ShapeParent':
		curves.parentShapeInPlace(source.nameLong,obj.nameLong)
		mc.delete(obj.nameLong)
		
	    elif ConnectBy == 'ChildOf':
		rigging.doParentReturnName(obj.nameLong,source.nameLong)
		mc.select(selection)

	    elif ConnectBy == 'Parent':
		rigging.doParentReturnName(source.nameLong,obj.nameLong)
		mc.select(selection)

	    elif ConnectBy == 'Constrain':
		groupBuffer = rigging.groupMeObject(obj.nameLong,True,True)
		obj.update(obj.nameBase)
		
		if HeirarchyState and HeirarchyMode == 'maintain' :
		    if obj.nameBase in parentConstraintTargets.keys():
			constraints.parent(parentConstraintTargets.get(obj.nameBase),groupBuffer,maintainOffset = True)
			if ScaleState:
			    pass
			    #buffer = constraints.scale(parentConstraintTargets.get(obj.nameBase),groupBuffer,maintainOffset = False)   
			    #rigging.copyPivot(buffer[0],parentConstraintTargets.get(obj.nameBase))
			
		if ExtraGroupState:
		    ConstraintGroup = ObjectFactory(rigging.groupMeObject(obj.nameLong,True,True) )
		    ConstraintGroup.store('cgmTypeModifier','constraint')
		    
		if RotateOrderState:
		    mc.connectAttr(obj.RotateOrderControl.nameCombined,(groupBuffer+'.rotateOrder'))
		    mc.connectAttr(obj.RotateOrderControl.nameCombined,(source.nameShort+'.rotateOrder'))
		    if ExtraGroupState:
			mc.connectAttr(obj.RotateOrderControl.nameCombined,(ConstraintGroup.nameLong+'.rotateOrder'))
			
		if ExtraGroupState:	
		    NameFactory.doNameObject(ConstraintGroup.nameLong)
		    obj.update(obj.nameBase)
				
		if ConstraintMode == 'parent':
		    constraints.parent(obj.nameLong,source.nameLong,maintainOffset = False)
		    
		    #mc.parentConstraint(obj.nameLong,source.nameLong,maintainOffset = False)
		elif ConstraintMode == 'point':
		    constraints.point(obj.nameLong,source.nameLong,maintainOffset = False)
		    if LockNHideState:
			attributes.doSetLockHideKeyableAttr(obj.nameLong,channels = ['rx','ry','rz'])
		elif ConstraintMode == 'orient':
		    mc.orientConstraint(obj.nameLong,source.nameLong,maintainOffset = False)
		    if LockNHideState:
			attributes.doSetLockHideKeyableAttr(obj.nameLong,channels = ['tx','ty','tz'])
		elif ConstraintMode == 'point/orient':
		    constraints.point(obj.nameLong,source.nameLong,maintainOffset = False)		    
		    constraints.orient(obj.nameLong,source.nameLong,maintainOffset = False)
		
		if ScaleState:
		    attributes.doConnectAttr((obj.nameLong+'.s'),(source.nameLong+'.s'))
		    #buffer = constraints.scale(obj.nameLong,source.nameLong,maintainOffset = False)
		    #rigging.copyPivot(buffer[0],parentConstraintTargets.get(obj.nameBase))
		
		if LockNHideState:
		    attributes.doSetLockHideKeyableAttr(obj.nameLong,channels = ['v'])
		    if not ScaleState:
			attributes.doSetLockHideKeyableAttr(obj.nameLong,channels = ['sx','sy','sz'])		    

		obj.store('cgmDrivenObject',source.nameLong)
		obj.remove('cgmSource')
		
		
	    else:
		guiFactory.warning('Got to the end!')
		

	else:
	    guiFactory.warning("'%s' has no source"%obj.nameBase)

    

    
def doCreateCurveFromObjects():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a curve from a selection of objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    curveName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)

    if len(selection)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    try:
        return curves.curveFromObjList(selection)
    except:
        guiFactory.warning('Houston, we have a problem')

def uiSetGuessOrientation(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Guess an objects orientation

    ARGUMENTS:
    Active Selection

    RETURNS:
    curveName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    aimFromObject = []
    aimToObject = []
    # set world regardless of selection
    worldUp = mc.upAxis(q=True,axis=True)		
    worldAxis = logic.axisFactory(worldUp)	
    if worldAxis:
        index = self.axisOptions.index(worldAxis.axisString)
        mc.optionVar( sv=('cgmVar_WorldUpAxis', worldAxis.axisString) )
        menuItems = self.WorldUpCollection.getItems()
        menuItems[index](edit = True,rb = True)	
        print("worldUp set to '%s'"%worldAxis.axisString)	

    if selection:
        aimAxis = []
        upAxis = []	
        child = mc.listRelatives(selection[0],children = True, type = 'transform',path = True)
        parent = mc.listRelatives(selection[0],parent = True, type = 'transform',path = True)
        if parent:
            aimFromObject = parent[0]
            aimToObject = selection[0]
        elif child:
            aimFromObject = selection[0]
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
            mc.optionVar( sv=('cgmVar_ObjectAimAxis', aimAxis.axisString) )
            menuItems = self.ObjectAimCollection.getItems()
            menuItems[index](edit = True,rb = True)
            guiFactory.warning("aim set to '%s'"%aimAxis.axisString)

        if upAxis:
            index = self.axisOptions.index(upAxis.axisString)
            mc.optionVar( sv=('cgmVar_ObjectUpAxis', upAxis.axisString) )
            menuItems = self.ObjectUpCollection.getItems()
            menuItems[index](edit = True, rb = True)
            guiFactory.warning("up set to '%s'"%upAxis.axisString)			
    else:
        guiFactory.warning("No objects selection. Setting defaults of 'z+' aim, 'y+' up")
        aimIndex = self.axisOptions.index('z+')
        mc.optionVar( sv=('cgmVar_ObjectAimAxis', 'z+') )
        menuItems = self.ObjectAimCollection.getItems()
        menuItems[aimIndex](edit = True,rb = True)	

        upIndex = self.axisOptions.index('y+')
        mc.optionVar( sv=('cgmVar_ObjectUpAxis', 'y+') )
        menuItems = self.ObjectUpCollection.getItems()
        menuItems[upIndex](edit = True,rb = True)
    
    if selection:
        mc.select(selection)


def doShapeParent():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)

    if len(selection)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    for obj in selection[1:]:
        try:
            curves.parentShape(obj,selection[0])
        except:
            guiFactory.warning(obj + ' failed')

def doShapeParentInPlace():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)

    if len(selection)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    for obj in selection[1:]:
        curves.parentShapeInPlace(obj,selection[0])
	
def doReplaceCurveShapes():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)

    if len(selection)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False
    
    originalShapes = mc.listRelatives (selection[-1], f= True,shapes=True)
    if originalShapes:
	colorIndex = mc.getAttr(originalShapes[0]+'.overrideColor') 
	 
    for obj in selection[:-1]:
	curves.parentShapeInPlace(selection[-1],obj)
	
    if originalShapes:
	for shape in originalShapes:
	    try:
		mc.delete(shape)
	    except:
		guiFactory.warning("'%s' failed to delete"%shape)
    
    #recolor
    if colorIndex:
	curves.setColorByIndex(selection[-1],colorIndex)
	
    mc.delete(selection[:-1])

def doCurveToPython():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Parents the shapefrom the first object to all other objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    if selection:
        for obj in selection:
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

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True)
    if selection:
        goodObjects = []
        for obj in selection:
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

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    for obj in selection:
        objType = search.returnObjectType(obj)
        print (">>> '" + obj + "' == " + objType)
    print 'done'

def doReportSelectionCount():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reports the number of selection items

    ARGUMENTS:
    Active Selection

    RETURNS:
    int(number)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    count = len(mc.ls(sl=True,flatten=True))
    guiFactory.warning('There are %i items selection.' % count)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Group stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def zeroGroupMe():
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    if selection:
        for obj in selection:
            rigging.zeroTransformMeObject(obj)

    else:
        guiFactory.warning('You must select something.')

def makeTransformHere():
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    if selection:
        for obj in selection:
            rigging.groupMeObject(obj,False)

    else:
        guiFactory.warning('You must select something.')

def doGroupMeInPlace():
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    if selection:
        for obj in selection:
            rigging.groupMeObject(obj,True,True)

    else:
        guiFactory.warning('You must select something.')
def doCopyPivot():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copies the pivot from the first object to all other objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)

    if len(selection)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    for obj in selection[1:]:
        try:
            rigging.copyPivot(obj,selection[0])
        except:
            guiFactory.warning(obj + ' failed')
	    
def doParentSelected():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copies the pivot from the first object to all other objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls (sl=True,flatten=True) or []
    mc.select(cl=True)

    if len(selection)<2:
        guiFactory.warning('You must have at least two objects selected')
        return False

    try:
	rigging.parentListToHeirarchy(selection)
	mc.select(selection)
    except:
	guiFactory.warning('Failed to parent selected')
	    