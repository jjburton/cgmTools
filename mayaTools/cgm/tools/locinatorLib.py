#=================================================================================================================================================
#=================================================================================================================================================
#	cgmLocinator - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#   Tool for making locators and other stuffs
# 
# REQUIRES:
#   Maya
#   distance
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.joshburton.com
# 	Copyright 2011 Josh Burton - All Rights Reserved.
# 
# CHANGELOG:
#	0.1.11292011 - First version
#	0.1.12012011 - Closest object working, update selected, just loc selected working
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


from cgm.lib import rigging
from cgm.lib import attributes
from cgm.lib import locators
from cgm.lib import search
from cgm.lib import lists
from cgm.lib import batch
from cgm.lib import autoname
from cgm.lib import guiFactory
from cgm.lib import modules
from cgm.lib import position

reload(attributes)
reload(lists)
reload(batch)
reload(rigging)
reload(search)
reload(autoname)
reload(guiFactory)
reload(modules)
reload(locators)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tool Commands
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def doLocMe(ui):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function to create a locator from a seleciton
    
    REQUIRES:
    ui(activeUI)
    Active Selection
    
    RETURNS:
    locList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    ui.forceBoundingBoxState = mc.optionVar( q='cgmVarForceBoundingBoxState' )

    for item in selected:
	locBuffer = locators.locMeObject(item, ui.forceBoundingBoxState)
	if '.' not in list(item):
	    attributes.storeInfo(item,'cgmMatchObject',locBuffer)
	bufferList.append(locBuffer)
	
    if len(bufferList) > 0:
	print ('%s%s' % (" The following locators have been created - ", bufferList))
    else:
	return (mc.spaceLocator(name = 'worldCenter_loc'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doPurgecgmAttrs(ui):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a locator at the center of of a selection of objects
    
    REQUIRES:
    Active Selection
    
    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    
    if len(selected) >=1:
	for item in selected:
	    modules.purgecgmAttrsFromObject(item)
    else:
	guiFactory.warning('Something must be selected')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>	

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocCenter(ui):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a locator at the center of of a selection of objects
    
    REQUIRES:
    Active Selection
    
    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    ui.forceBoundingBoxState = mc.optionVar( q='cgmVarForceBoundingBoxState' )

    if len(selected) >=2:
	return (locators.locMeCenter(selected,ui.forceBoundingBoxState))
    if len(selected) == 1:
	return (locators.locMeCenter(selected,True))
    else:
	return (mc.spaceLocator(name = 'worldCenter_loc'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>	
def doTagObjects(ui):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tag objects with a single locator in a selection, if more than one locator exists,
    it uses the first one in the selection list.
    
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
    
    typeList = []
    taggingLoc = False
    for obj in selected:
	if 'locator' not in typeList:
	    objType = search.returnObjectType(obj)
	    typeList.append(objType)
	    if objType == 'locator':
		taggingLoc = obj
	else:
	    print 'You have more than one locator'
    
    if taggingLoc:
	for obj in selected:
	    if obj is not taggingLoc:
		attributes.storeInfo(obj,'cgmMatchObject',taggingLoc)
		print ('%s%s' % (obj, " tagged and released...")) 
    
    else:
	guiFactory.warning('No locator in selection, you need one')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocClosest():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a locator on the surface of the last object in a selection set closest
    to each remaining object in the selection
    
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
    else:
	return locators.locClosest(selected)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doUpdateLoc(ui, forceCurrentFrameOnly = False ):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Updates selected locator or object connected to a match locator's position and rotation
    
    REQUIRES:
    ui
    Active Selection
    
    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    ui.currentFrameOnly = mc.optionVar( q='cgmCurrentFrameOnly' )
    ui.forceEveryFrame = mc.optionVar( q='cgmVarForceEveryFrame' )
    ui.forceBoundingBoxState = mc.optionVar( q='cgmVarForceBoundingBoxState' )

    if len(selected) >= 1:
	if ui.currentFrameOnly or forceCurrentFrameOnly:
	    for item in selected:
		if search.returnObjectType(item) == 'locator':
		    if locators.doUpdateLocator(item,ui.forceBoundingBoxState):
			print ('%s%s' % (item, " updated..."))
		    else:
			print ('%s%s' % (item, " could not be updated..."))
		else:
		    matchObject = search.returnTagInfo(item,'cgmMatchObject')
		    if mc.objExists(matchObject):
			position.moveParentSnap(item,matchObject)
			print ('%s%s' % (item, " updated..."))
	else:
	    ui.startFrame = ui.startFrameField(q=True,value=True)
	    ui.endFrame = ui.endFrameField(q=True,value=True)
	    initialFramePosition = mc.currentTime(q=True)
	    if ui.forceEveryFrame== True:
		print 'every frame'

		for item in selected:
		    #first clear any key frames in the region to be able to cleanly put new ones on keys only mode
		    mc.cutKey(item,animation = 'objects', time=(ui.startFrame,ui.endFrame + 1))
		
		guiFactory.doProgressWindow()
		maxRange = ui.endFrame + 1
		
		for f in range(ui.startFrame,ui.endFrame + 1):
		    if guiFactory.doUpdateProgressWindow('On f',f,maxRange,f) == 'break':
			break
		    mc.currentTime(f)
		    for item in selected:
			
			if search.returnObjectType(item) == 'locator':
				locators.doUpdateLocator(item,ui.forceBoundingBoxState)
			else:
			    matchObject = search.returnTagInfo(item,'cgmMatchObject')
			    if mc.objExists(matchObject):
				position.moveParentSnap(item,matchObject)
				
			mc.setKeyframe(item,time = f,at=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ'])
			
			
		guiFactory.doCloseProgressWindow()
		#Put the time line back where it was
		mc.currentTime(initialFramePosition)
		
	    else:
		guiFactory.doProgressWindow()
		itemCnt = 0
		print 'here'
		for item in selected:
		    if guiFactory.doUpdateProgressWindow('On ',itemCnt,(len(selected)),item) == 'break':
			break
		
		    if search.returnObjectType(item) == 'locator':
			matchObject = returnLocatorSource(item)
		    else:
			matchObject = search.returnTagInfo(item,'cgmMatchObject')
			
		    keyFrames = search.returnListOfKeyIndices(matchObject)
		    maxRange = len(keyFrames)
		    #Start our frame counter
		    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(maxRange)
		    
		    #first clear any key frames in the region to be able to cleanly put new ones on keys only mode
		    mc.cutKey(item,animation = 'objects', time=(ui.startFrame,ui.endFrame + 1))
		    
		    maxRange = len(keyFrames)
		    for f in keyFrames:
			if f >= ui.startFrame and f <= ui.endFrame:
			    #Update our progress bar
			    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
				    break
			    mc.progressBar(mayaMainProgressBar, edit=True, status = ('%s%i' % ('Copying f',f)), step=1)
			    			    
			    mc.currentTime(f)
			    if search.returnObjectType(item) == 'locator':
				locators.doUpdateLocator(item,ui.forceBoundingBoxState)
			    else:
				if mc.objExists(matchObject):
				    position.moveParentSnap(item,matchObject)
				else:
				    return False
				
			    mc.setKeyframe(item,time = f,at=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ'])
			    #Close our progress bar
			    
		    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
		    itemCnt += 1
		    
		guiFactory.doCloseProgressWindow() 
		#Put the time line back where it was	
		mc.currentTime(initialFramePosition)
    else:
	guiFactory.warning('Nothing selected')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocCVsOfObject():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Places locators on the cv's of a curve
    
    REQUIRES:
    Selected Curve
    
    RETURNS:
    locList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = lists.returnSelectedToList()
    selected = (mc.ls (sl=True,flatten=True))
    badObjects = []
    if len(selected)<=1:
	for item in selected:
	    if search.returnObjectType(item) == 'nurbsCurve':
		locators.locMeCVsOfCurve(item)
	    else:
		badObjects.append(item)
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
    
    REQUIRES:
    Selected Curve
    
    RETURNS:
    locList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = lists.returnSelectedToList()
    selected = (mc.ls (sl=True,flatten=True))
    badObjects = []
    if len(selected)<=1:
	for item in selected:
	    if search.returnObjectType(item) == 'nurbsCurve':
		locators.locMeCVsOnCurve(item)
	    else:
		badObjects.append(item)
		
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
    
    REQUIRES:
    locatorName(string)
    
    RETURNS:
    obj(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if search.returnObjectType(locatorName) == 'locator':
        sourceObjectBuffer = search.returnTagInfo(locatorName,'cgmSource')
        if sourceObjectBuffer:
	    if ',' in list(sourceObjectBuffer):
		sourceObjects = sourceObjectBuffer.split(',')
		return sourceObjects[-1]
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
    