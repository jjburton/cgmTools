#=================================================================================================================================================
#=================================================================================================================================================
#	cgmLocinator - a part of cgmTools
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
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tool Commands
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocMe(self):
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
    self.forceBoundingBoxState = mc.optionVar( q='cgmVarForceBoundingBoxState' )

    if selected:
	mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(selected))		
	
	for item in selected:
	    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		    break
	    mc.progressBar(mayaMainProgressBar, edit=True, status = ("Procssing '%s'"%item), step=1)

	    
	    locBuffer = locators.locMeObject(item, self.forceBoundingBoxState)
	    if '.' not in list(item):
		attributes.storeInfo(item,'cgmMatchObject',locBuffer)
	    bufferList.append(locBuffer)
	    
	guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

    if bufferList:
        mc.select(bufferList)

    if len(bufferList) > 0:
        print ('%s%s' % (" The following locators have been created - ", bufferList))
    else:
        return (mc.spaceLocator(name = 'worldCenter_loc'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doPurgeCGMAttrs(self):
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

    REQUIRES:
    Active Selection

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = []
    selected = (mc.ls (sl=True,flatten=True))
    mc.select(cl=True)
    self.forceBoundingBoxState = mc.optionVar( q='cgmVarForceBoundingBoxState' )

    print selected 

    if len(selected) >=2:
        buffer = (locators.locMeCenter(selected,self.forceBoundingBoxState))
    elif len(selected) == 1:
        buffer =(locators.locMeCenter(selected,True))
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
def queryCanUpdate(objectToUpdate):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Checks if an object is updatable

    REQUIRES:
    objectToUpdate(string)

    RETURNS:
    ifcanUpdate(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if search.returnObjectType(objectToUpdate) == 'locator':
        if search.returnTagInfo(objectToUpdate,'cgmLocMode'):
            return True
        else:
            return False
    else:
        matchObject = search.returnTagInfo(objectToUpdate,'cgmMatchObject')
        if mc.objExists(matchObject):
            return True
        else:
            return False


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
        buffer = locators.locClosest(selected[:-1],selected[-1])
        mc.select(buffer)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doUpdateLoc(self, forceCurrentFrameOnly = False ):
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
    self.currentFrameOnly = mc.optionVar( q='cgmCurrentFrameOnly' )
    self.forceEveryFrame = mc.optionVar( q='cgmVarForceEveryFrame' )
    self.forceBoundingBoxState = mc.optionVar( q='cgmVarForceBoundingBoxState' )

    if not len(selected):
        guiFactory.warning('Nothing Selected')
        return 

    toUpdate = []
    # First see if we have any updateable objects
    for item in selected:
        if queryCanUpdate(item):
            toUpdate.append(item)


    if len(toUpdate) >= 1:
        if self.currentFrameOnly or forceCurrentFrameOnly:
            for item in toUpdate:
                if search.returnObjectType(item) == 'locator':
                    if locators.doUpdateLocator(item,self.forceBoundingBoxState):
                        guiFactory.warning('%s%s' % (item, " updated..."))
                    else:
                        guiFactory.warning('%s%s' % (item, " could not be updated..."))
                else:
                    matchObject = search.returnTagInfo(item,'cgmMatchObject')
                    if mc.objExists(matchObject):
                        position.moveParentSnap(item,matchObject)
                        print ('%s%s' % (item, " updated..."))
                    else:
                        guiFactory.warning('%s%s' % (item, " has no match object"))
        else:
            self.startFrame = self.startFrameField(q=True,value=True)
            self.endFrame = self.endFrameField(q=True,value=True)
            initialFramePosition = mc.currentTime(q=True)


            if self.forceEveryFrame== True:
                for item in toUpdate:
                    #Then delete the key clear any key frames in the region to be able to cleanly put new ones on keys only mode
                    mc.cutKey(item,animation = 'objects', time=(self.startFrame,self.endFrame + 1))

                mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(range(self.startFrame,self.endFrame + 1)),"On '%s'"%item)
                #guiFactory.doProgressWindow()
                maxRange = self.endFrame + 1

                for f in range(self.startFrame,self.endFrame + 1):
		    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
			    break
		    mc.progressBar(mayaMainProgressBar, edit=True, status = ("On frame %i for '%s'"%(f,"','".join(toUpdate))), step=1)                    
                    """
                    if guiFactory.doUpdateProgressWindow('On f',f,maxRange,f) == 'break':
                        break
                    """
                    mc.currentTime(f)
                    for item in toUpdate:
                        if search.returnObjectType(item) == 'locator':
                            locators.doUpdateLocator(item,self.forceBoundingBoxState)
                        else:
                            if queryCanUpdate(item):
				matchObject = search.returnTagInfo(item,'cgmMatchObject')
				if mc.objExists(matchObject):
				    position.moveParentSnap(item,matchObject)
                            else:
                                break
                        mc.setKeyframe(item,time = f,at=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ'])

		guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

                #guiFactory.doCloseProgressWindow()
                #Put the time line back where it was
                mc.currentTime(initialFramePosition)

            else:

                guiFactory.doProgressWindow()
                itemCnt = 0

                for item in toUpdate:
		    print item
                    if guiFactory.doUpdateProgressWindow('On ',itemCnt,(len(toUpdate)),item) == 'break':
                        break
		    
		    # If our object is a locator that's created from muliple sources, we need to check each object for keyframes

                    if search.returnObjectType(item) == 'locator':
			sourceObjectBuffer = search.returnTagInfo(item,'cgmSource')
			if ',' in sourceObjectBuffer:
			    keyFrames = []
			    matchObjects = returnLocatorSources(item)
			    for o in matchObjects:
				keyFrames.extend(search.returnListOfKeyIndices(o))
			    keyFrames = lists.returnListNoDuplicates(keyFrames)
			else:
			    matchObject = returnLocatorSource(item)
			    keyFrames = search.returnListOfKeyIndices(matchObject)

                    else:
                        matchObject = search.returnTagInfo(item,'cgmMatchObject')
			keyFrames = search.returnListOfKeyIndices(matchObject)
			
                    maxRange = len(keyFrames)
                    #Start our frame counter
                    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(maxRange)

                    #first clear any key frames in the region to be able to cleanly put new ones on keys only mode
                    mc.cutKey(item,animation = 'objects', time=(self.startFrame,self.endFrame + 1))

                    maxRange = len(keyFrames)
                    for f in keyFrames:
                        if f >= self.startFrame and f <= self.endFrame:
                            #Update our progress bar
                            if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                                break
                            mc.progressBar(mayaMainProgressBar, edit=True, status = ('%s%i' % ('Copying f',f)), step=1)

                            mc.currentTime(f)
                            if search.returnObjectType(item) == 'locator':
				print 'updating...'
                                locators.doUpdateLocator(item,self.forceBoundingBoxState)
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
        guiFactory.warning('No updateable object selected')
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
    returnList = []
    if len(selected)<=1:
        for item in selected:
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

    REQUIRES:
    Selected Curve

    RETURNS:
    locList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    selected = lists.returnSelectedToList()
    selected = (mc.ls (sl=True,flatten=True))
    badObjects = []
    returnList = []

    if len(selected)<=1:
        for item in selected:
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

    REQUIRES:
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