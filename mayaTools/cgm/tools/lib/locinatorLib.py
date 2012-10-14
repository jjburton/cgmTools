#=================================================================================================================================================
#=================================================================================================================================================
#	cgmLocinator - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Tool for making locators and other stuffs
#
# ARGUMENTS:
#   Maya
#   distance
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1.11292011 - First version
#	0.1.12012011 - Closest object working, update selection, just loc selection working
#	0.1.12022011 - Got most things working now except for the stuff in time, tabs added, honoring postion option now
#	0.1.12032011 - Made hide info hideable, work on templates. Update locator over time working. Adding match tab
#	0.1.12062011 - Rewrite to work with maya 2010 and below, pushing most things through guiFactory now
#	0.1.12082011 - Reworked some progress bar stuff and added a purge cgm attrs tool to keep stuff clean for pipelines
#	0.1.12112011 - Simplified gui, cleaned up a few things
#
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel
import subprocess

from cgm.lib.classes import NameFactory
from cgm.lib.classes import ObjectFactory
reload(ObjectFactory)
from cgm.lib.classes import OptionVarFactory
reload(OptionVarFactory)


from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes.OptionVarFactory import *

from cgm.lib import rigging
from cgm.lib import attributes
from cgm.lib import locators
from cgm.lib import search
from cgm.lib import lists
from cgm.lib import batch
from cgm.lib import guiFactory
from cgm.lib import modules
from cgm.lib import position

reload(attributes)
reload(lists)
reload(batch)
reload(rigging)
reload(search)
reload(NameFactory)
reload(guiFactory)
reload(modules)
reload(locators)

matchModeKeyingDict = {0:['translateX','translateY','translateZ','rotateX','rotateY','rotateZ'],
                       1:['translateX','translateY','translateZ'],
                       2:['rotateX','rotateY','rotateZ']}

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# GUI
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def setGUITimeRangeToCurrent(self):
    timelineInfo = search.returnTimelineInfo()
    self.startFrameField(edit=True,value=(timelineInfo["rangeStart"]))
    self.endFrameField(edit=True,value=(timelineInfo["rangeEnd"]))

def setGUITimeRangeToScene(self):
    timelineInfo = search.returnTimelineInfo()
    self.startFrameField(edit=True,value=(timelineInfo["sceneStart"]))
    self.endFrameField(edit=True,value=(timelineInfo["sceneEnd"]))

def getSelfOptionVars(self):
    try:
	if self.toolName == 'cgm.locinator':
	    self.bakeMode = mc.optionVar( q='cgmVar_LocinatorBakeState' )
	    self.forceEveryFrame = mc.optionVar( q='cgmVar_LocinatorKeyingMode' )
	    self.keyingTargetState = mc.optionVar( q='cgmVar_LocinatorKeyingTarget' )
	    self.matchMode = mc.optionVar(q='cgmVar_LocinatorMatchMode')
	elif self.toolName == 'cgm.animTools':
	    self.bakeMode = mc.optionVar( q='cgmVar_AnimToolsBakeState' )
	    self.forceEveryFrame = mc.optionVar( q='cgmVar_AnimToolsKeyingMode' )
	    self.keyingTargetState = mc.optionVar( q='cgmVar_AnimToolsKeyingTarget' )
	    self.matchMode = mc.optionVar(q='cgmVar_AnimToolsMatchMode')	
	elif self.toolName == 'cgm.snapMM':
	    self.bakeMode = 0
	    self.forceEveryFrame = 0
	    self.keyingTargetState = 0
	    self.matchMode = mc.optionVar(q='cgmVar_SnapMMMatchMode')	    
	    
	    
    except:
	guiFactory.warning("'%s' failed - locinatorLib.getSelfOptionVars"%self.toolName)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tool Commands
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocMe(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function to create a locator from a seleciton

    ARGUMENTS:
    ui(activeUI)
    Active Selection

    RETURNS:
    locList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = mc.ls(sl=True,flatten=True) or []
    mc.select(cl=True)
    self.forceBoundingBoxState = mc.optionVar( q='cgmVar_ForceBoundingBoxState' )

    if not selection:
	return mc.spaceLocator(name = 'worldCenter_loc')

    retLocators = []

    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(selection))		

    for item in selection:
	if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
	    break
	mc.progressBar(mayaMainProgressBar, edit=True, status = ("Procssing '%s'"%item), step=1)

	loc = locators.locMeObject(item, self.forceBoundingBoxState)
	if '.' not in list(item):
	    attributes.storeInfo(item,'cgmMatchObject',loc)
	retLocators.append(loc)

    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

    if retLocators:
	mc.select(retLocators)

    print 'The following locators have been created - %s' % ','.join(retLocators)
    return retLocators
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doPurgeCGMAttrs(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a locator at the center of of a selection of objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selection = []
    selection = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)

    if len(selection) >=1:
	for item in selection:
	    modules.purgeCGMAttrsFromObject(item)
    else:
	guiFactory.warning('Something must be selected')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocCenter(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a locator at the center of of a selection of objects

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selection = []
    selection = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    self.forceBoundingBoxState = mc.optionVar( q='cgmVar_ForceBoundingBoxState' )

    print selection 

    if len(selection) >=2:
	buffer = (locators.locMeCenter(selection,self.forceBoundingBoxState))
    elif len(selection) == 1:
	buffer =(locators.locMeCenter(selection,True))
    else:
	return (mc.spaceLocator(name = 'worldCenter_loc'))

    if buffer:
	mc.select(buffer)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doTagObjects(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tag objects with a single locator in a selection, if more than one locator exists,
    it uses the first one in the selection list. It uses the first object in the list
    as a rotateOrder source if update rotate order is on.

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    selection = (mc.ls (sl=True,flatten=True)) or []
    mc.select(cl=True)
    self.updateMatchRotateOrder = mc.optionVar(q='cgmVar_TaggingUpdateRO')

    if len(selection)<2:
	guiFactory.warning('You must have at least two objects selected')
	return False

    typeList = []
    taggingLoc = False
    for obj in selection:
	if 'locator' not in typeList:
	    objType = search.returnObjectType(obj)
	    typeList.append(objType)
	    if objType == 'locator':
		taggingLoc = obj
		selection.remove(obj)
		break
	else:
	    print 'You have more than one locator'

    if taggingLoc:
	for obj in selection:
	    attributes.storeInfo(obj,'cgmMatchObject',taggingLoc)
	    print ('%s%s' % (obj, " tagged and released..."))

	if self.updateMatchRotateOrder:
	    loc = ObjectFactory(taggingLoc)
	    loc.copyRotateOrder(selection[0])
	    guiFactory.warning("'%s's rotate order updated to match '%s'"%(loc.nameLong,selection[0]))

	selection.append(taggingLoc)
	mc.select(selection)

    else:
	guiFactory.warning('No locator in selection, you need one')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def queryCanUpdate(objectToUpdate):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Checks if an object is updatable

    ARGUMENTS:
    objectToUpdate(string)

    RETURNS:
    ifcanUpdate(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if search.returnObjectType(objectToUpdate) == 'locator':
	if search.returnTagInfo(objectToUpdate,'cgmLocMode'):
	    return True
	else:
	    matchObject = search.returnTagInfo(objectToUpdate,'cgmMatchObject')
	    if mc.objExists(matchObject):
		return True
	    else:
		return False
    else:
	matchObject = search.returnTagInfo(objectToUpdate,'cgmMatchObject')
	if mc.objExists(matchObject):
	    return True
	else:
	    return False


def doLocClosest(self):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a locator on the surface of the last object in a selection set closest
    to each remaining object in the selection

    ARGUMENTS:
    Active Selection

    RETURNS:
    locatorList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    if self.LocinatorUpdateObjectsOptionVar.value:
	selection = self.LocinatorUpdateObjectsBufferOptionVar.value
    else:
	selection = (mc.ls (sl=True,flatten=True)) or []

    mc.select(cl=True)

    if len(selection)<2:
	guiFactory.warning('You must have at least two objects selected')
	return False
    else:
	buffer = locators.locClosest(selection[:-1],selection[-1])
	mc.select(buffer)

def doUpdateObj(self,obj):
    matchObject = search.returnTagInfo(obj,'cgmMatchObject')

    if mc.objExists(matchObject):
	try:
	    if self.matchMode == 0:
		position.moveParentSnap(obj,matchObject)
	    elif self.matchMode == 1:
		position.movePointSnap(obj,matchObject)
	    elif self.matchMode == 2:
		position.moveOrientSnap(obj,matchObject)
	    return True
	except:
	    return False

def doConstrainToUpdateObject(self,obj):
    matchObject = search.returnTagInfo(obj,'cgmMatchObject')

    if mc.objExists(matchObject):

	try:
	    if self.matchMode == 0:
		buffer =  mc.parentConstraint(matchObject,obj, maintainOffset=False)
	    elif self.matchMode == 1:
		buffer = mc.pointConstraint(matchObject,obj,  maintainOffset=False)
	    elif self.matchMode == 2:
		buffer = mc.orientConstraint(matchObject,obj,   maintainOffset=False)

	    return buffer
	except:
	    return False

def doUpdateSelectedObjects(self):
    selection = mc.ls(sl=True,type = 'transform') or []
    if selection:
	for obj in selection:
	    matchObject = search.returnTagInfo(obj,'cgmMatchObject')

	    if mc.objExists(matchObject):
		try:
		    if self.matchMode == 0:
			position.moveParentSnap(obj,matchObject)
		    elif self.matchMode == 1:
			position.movePointSnap(obj,matchObject)
		    elif self.matchMode == 2:
			position.moveOrientSnap(obj,matchObject)
		except:
		    guiFactory.warning("'%s' has no match object"%obj)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doUpdateLoc(self, forceCurrentFrameOnly = False ):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Updates selection locator or object connected to a match locator's position and rotation

    ARGUMENTS:
    ui
    Active Selection

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []

    if self.LocinatorUpdateObjectsOptionVar.value:
	self.LocinatorUpdateObjectsBufferOptionVar = OptionVarFactory(self.LocinatorUpdateObjectsBufferOptionVar.name)
	
	preSelectBuffer = mc.ls(sl=True,flatten=True,long=True) or []
	mc.select(cl=True)
	self.LocinatorUpdateObjectsBufferOptionVar.select()
	selection =  mc.ls(sl=True,flatten=True,long=True) or []

    else:
	selection = (mc.ls (sl=True,flatten=True)) or []

    if not selection:
	if self.LocinatorUpdateObjectsOptionVar.value:
	    guiFactory.warning('Buffer is empty')
	    return 
	else:
	    guiFactory.warning('Nothing selected')
	    return 

    getSelfOptionVars(self)
    self.forceBoundingBoxState = mc.optionVar( q='cgmVar_ForceBoundingBoxState' )
    getSelfOptionVars(self)

    objectsToUpdate = {}
    
    # First see if we have any updateable objects
    for item in selection:
	matchObject = search.returnTagInfo(item,'cgmMatchObject')
	if mc.objExists(matchObject):
	    objectsToUpdate[item] = matchObject
	    
	elif search.returnObjectType(item) == 'locator':
	    if search.returnTagInfo(item,'cgmLocMode'): 
		objectsToUpdate[item] = False

    print "Self bake mode is '%s'"%self.bakeMode
    print "Force Every Frame mode is '%s'"%self.forceEveryFrame
    
    if objectsToUpdate:
	if not self.bakeMode:
	    #Single frame update
	    for item in objectsToUpdate.keys():
		if objectsToUpdate[item]:
		    if doUpdateObj(self,item):
			print ("'%s' updated..."%item)
		    else:
			guiFactory.warning('%s%s' % (item, " has no match object"))
		else:	
		    if locators.doUpdateLocator(item,self.forceBoundingBoxState):
			guiFactory.warning("'%s' updated..."%item)
		    else:
			guiFactory.warning('%s%s' % (item, " could not be updated..."))
	    

	    mc.select(objectsToUpdate.keys())

	else:
	    #Multi frame update
	    self.startFrame = self.startFrameField(q=True,value=True)
	    self.endFrame = self.endFrameField(q=True,value=True)
	    initialFramePosition = mc.currentTime(q=True)

	    constraintList = []
	    itemBaseAttrs = {}

	    if self.forceEveryFrame== True:
		for item in objectsToUpdate.keys():
		    #Then delete the key clear any key frames in the region to be able to cleanly put new ones on keys only mode
		    mc.cutKey(item,animation = 'objects', time=(self.startFrame,self.endFrame + 1),at= matchModeKeyingDict.get(self.matchMode))

		mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(range(self.startFrame,self.endFrame + 1)),"On '%s'"%item)
		maxRange = self.endFrame + 1
		#First set up our constraints for non locator objects
		for item in objectsToUpdate.keys():
		    if objectsToUpdate[item]:
			#Grab an attr buffer to see if a blendParent pops up
			itemBaseAttrs[item] = mc.listAttr(item, userDefined = True)
			#Then set up the constraint
			constraintList.append( doConstrainToUpdateObject(self,item) )

		for f in range(self.startFrame,self.endFrame + 1):
		    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
			break
		    mc.progressBar(mayaMainProgressBar, edit=True, status = ("On frame %i for '%s'"%(f,"','".join(objectsToUpdate))), step=1)                    

		    mc.currentTime(f)
		    for item in objectsToUpdate.keys():
			if not objectsToUpdate[item]:#locators are stored with false matchObjects
			    locators.doUpdateLocator(item,self.forceBoundingBoxState)
			else:
			    doUpdateObj(self,item)
			    
			mc.setKeyframe(item,time = f,at= matchModeKeyingDict.get(self.matchMode))
			

			#See if we got a new blendParent pop up we need to set to 1
			compareAttrList = mc.listAttr(item, userDefined = True)
			missingList = lists.returnMissingList( itemBaseAttrs.get(item) ,compareAttrList)
			if missingList:
			    for i in missingList:
				if 'blendParent' in i:
				    attributes.doSetAttr(item,i,1)	
				    mc.setKeyframe(item,time = f,at= matchModeKeyingDict.get(self.matchMode))


		guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

		if constraintList:
		    for o in constraintList:
			try:
			    mc.delete(o)
			except:
			    pass
		#guiFactory.doCloseProgressWindow()
		#Put the time line back where it was
		mc.currentTime(initialFramePosition)
		mc.select(objectsToUpdate.keys())

	    else:
		guiFactory.doProgressWindow()

		for itemCnt,item in enumerate(objectsToUpdate.keys()):
		    if guiFactory.doUpdateProgressWindow('On ',itemCnt,(len(objectsToUpdate)),item) == 'break':
			break

		    # If our object is a locator that's created from muliple sources, we need to check each object for keyframes

		    if search.returnObjectType(item) == 'locator':
			# If we're using the source object
			if not self.keyingTargetState:
			    sourceObjectBuffer = search.returnTagInfo(item,'cgmSource')
			    if sourceObjectBuffer and ',' in sourceObjectBuffer:
				keyFrames = []
				matchObjects = returnLocatorSources(item)
				for o in matchObjects:
				    keyFrames.extend(search.returnListOfKeyIndices(o))
				keyFrames = lists.returnListNoDuplicates(keyFrames)
			    else:
				matchObject = returnLocatorSource(item)
				keyFrames = search.returnListOfKeyIndices(matchObject)
			# if we're using the object's keys
			else:
			    matchObject = search.returnTagInfo(item,'cgmMatchObject')
			    keyFrames = search.returnListOfKeyIndices(item)

		    else:
			matchObject = search.returnTagInfo(item,'cgmMatchObject')
			if not self.keyingTargetState:
			    keyFrames = search.returnListOfKeyIndices(matchObject)
			else:
			    keyFrames = search.returnListOfKeyIndices(item)

			#Grab an attr buffer to see if a blendParent pops up
			itemBaseAttrs[item] = mc.listAttr(item, userDefined = True)
			#Then set up the constraint
			constraintList.append( doConstrainToUpdateObject(self,item) )


		    guiFactory.warning("'%s' has keys of %s"%(item,keyFrames))

		    maxRange = len(keyFrames)
		    #Start our frame counter
		    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(maxRange)

		    #first clear any key frames in the region to be able to cleanly put new ones on keys only mode
		    mc.cutKey(item,animation = 'objects', time=(self.startFrame,self.endFrame + 1),at= matchModeKeyingDict.get(self.matchMode))

		    maxRange = len(keyFrames)
		    for f in keyFrames:
			if f >= self.startFrame and f <= self.endFrame:
			    #Update our progress bar
			    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
				break
			    mc.progressBar(mayaMainProgressBar, edit=True, status = ('%s%i' % ('Copying f',f)), step=1)

			    mc.currentTime(f)
			    
			    if search.returnObjectType(item) == 'locator' and not objectsToUpdate[item]:
				locators.doUpdateLocator(item,self.forceBoundingBoxState)
			    else:
				doUpdateObj(self,item)
				
			    mc.setKeyframe(item,time = f,at= matchModeKeyingDict.get(self.matchMode))

			    #See if we got a new blendParent pop up we need to set to 1
			    compareAttrList = mc.listAttr(item, userDefined = True)
			    missingList = lists.returnMissingList( itemBaseAttrs.get(item) ,compareAttrList)
			    if missingList:
				for i in missingList:
				    if 'blendParent' in i:
					attributes.doSetAttr(item,i,1)	
					mc.setKeyframe(item,time = f,at= matchModeKeyingDict.get(self.matchMode))

			    #Close our progress bar

		    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

		if constraintList:
		    for o in constraintList:
			try:
			    mc.delete(o)
			except:
			    pass


		guiFactory.doCloseProgressWindow()
		#Put the time line back where it was

		mc.currentTime(initialFramePosition)
		mc.select(objectsToUpdate.keys())

	if self.LocinatorUpdateObjectsOptionVar.value and preSelectBuffer:
	    mc.select(preSelectBuffer)

    else:
	guiFactory.warning('No updateable object selected')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocCVsOfObject():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Places locators on the cv's of a curve

    ARGUMENTS:
    selection Curve

    RETURNS:
    locList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selection = (mc.ls (sl=True,flatten=True))  or []
    badObjects = []
    returnList = []
    if len(selection)<=1:
	for item in selection:
	    if search.returnObjectType(item) == 'nurbsCurve':
		returnList.extend( locators.locMeCVsOfCurve(item) )
	    else:
		badObjects.append(item)
	if returnList:
	    mc.select(returnList)

	if badObjects:
	    mc.warning ('%s%s' % (" The following objects aren't curves - ", badObjects))
	    return False
	else:
	    return True
    else:
	guiFactory.warning('Select at least one curve.')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocCVsOnObject():
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Places locators on the cv's closest position on a curve

    ARGUMENTS:
    selection Curve

    RETURNS:
    locList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selection = (mc.ls (sl=True,flatten=True)) or []
    badObjects = []
    returnList = []

    if len(selection)<=1:
	for item in selection:
	    if search.returnObjectType(item) == 'nurbsCurve':
		returnList.extend( locators.locMeCVsOnCurve(item) )
	    else:
		badObjects.append(item)

	if returnList:
	    mc.select(returnList)

	if badObjects:
	    mc.warning ('%s%s' % (" The following objects aren't curves - ", badObjects))
	    return False
	else:
	    return True
    else:
	guiFactory.warning('Select at least one curve.')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnLocatorSource(locatorName):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a locator's source

    ARGUMENTS:
    locatorName(string)

    RETURNS:
    obj(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if search.returnObjectType(locatorName) == 'locator':
	sourceObjectBuffer = search.returnTagInfo(locatorName,'cgmSource')
	if sourceObjectBuffer:
	    print sourceObjectBuffer
	    if ',' in list(sourceObjectBuffer):
		sourceObjectsBuffer = sourceObjectBuffer.split(',')
		return sourceObjectsBuffer[-1]
	    else:
		return sourceObjectBuffer

	sourceObject = search.returnTagInfo(locatorName,'cgmName')

	if sourceObject and mc.objExists(sourceObject):
	    if '.' in list(sourceObject):
		splitBuffer = sourceObject.split('.')
		return splitBuffer[0]
	    else:
		return sourceObject
	else:
	    print "Doesn't have a source stored"
	    return False

    else:
	return False

def returnLocatorSources(locatorName):
    sourceObjectBuffer = search.returnTagInfo(locatorName,'cgmSource')
    if sourceObjectBuffer:
	if ',' in list(sourceObjectBuffer):
	    sourceObjectsBuffer = sourceObjectBuffer.split(',')
	    sourceObjects = []
	    for o in sourceObjectsBuffer:
		if '.' in o:
		    splitBuffer = o.split('.')
		    sourceObjects.append(splitBuffer[0])
		else:
		    sourceObjects.append(o)
	    return lists.returnListNoDuplicates(sourceObjects)
	else:
	    return sourceObjectBuffer

	sourceObject = search.returnTagInfo(locatorName,'cgmName')

	if sourceObject and mc.objExists(sourceObject):
	    if '.' in list(sourceObject):
		splitBuffer = sourceObject.split('.')
		return splitBuffer[0]
	    else:
		return sourceObject
	else:
	    print "Doesn't have a source stored"
	    return False
    else:
	return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Buffer Tools - using optionVar
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def defineObjBuffer(bufferOptionVar):
    selection = mc.ls(sl=True, flatten = True) or []
    bufferOptionVar = OptionVarFactory(bufferOptionVar.name)
    
    bufferOptionVar.clear()

    if selection:
	for o in selection:
	    if queryCanUpdate(o):
		bufferOptionVar.append(o)
	    else:
		guiFactory.report("'%s' can't be updated. Not added to buffer"%o)
    else:
	guiFactory.warning("Nothing selected")

def addSelectedToObjBuffer(bufferOptionVar):
    selection = mc.ls(sl=True, flatten = True) or []
    bufferOptionVar = OptionVarFactory(bufferOptionVar.name)

    if selection:
	for o in selection:
	    if queryCanUpdate(o):
		bufferOptionVar.append(o)
	    else:
		guiFactory.report("'%s' can't be updated. Not added to buffer"%o)
    else:
	guiFactory.warning("Nothing selected")

def removeSelectedFromObjBuffer(bufferOptionVar):
    selection = mc.ls(sl=True, flatten = True) or []
    bufferOptionVar = OptionVarFactory(bufferOptionVar.name)

    if selection:
	for o in selection:
	    if queryCanUpdate(o):
		try:
		    bufferOptionVar.remove(o)
		except StandardError:
		    pass
	    else:
		guiFactory.report("'%s' can't be updated. Not added to buffer"%o)
    else:
	guiFactory.warning("Nothing selected")

def selectObjBufferMembers(bufferOptionVar):
    bufferOptionVar = OptionVarFactory(bufferOptionVar.name)

    if bufferOptionVar.value:
	bufferOptionVar.select()
    else:
	guiFactory.warning("Nothing selected")
	
def clearObjBuffer(bufferOptionVar):
    bufferOptionVar = OptionVarFactory(bufferOptionVar.name)

    if bufferOptionVar.value:
	bufferOptionVar.clear()
    else:
	guiFactory.warning("Nothing selected")
