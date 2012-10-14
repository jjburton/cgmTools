#=================================================================================================================================================
#=================================================================================================================================================
#	Locator - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for the widgety magic of rigging
#
# ARGUMENTS:
# 	Maya
#   distance
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
# FUNCTION KEY:
#   1) locMe - creates locators at the pivots of every object selected - matching translation, rotation and rotation order
#   2) locMeObject (obj) - return name of locator created
#   3) setRotationOrderObj (obj, ro)
#   4) doSetLockHideKeyableAttr (obj,lock,visible,keyable,channels) - Pass an oject, True/False for locking it,
#       True/False for visible in channel box, and which channels you want locked in ('tx','ty',etc) form
#   5) groupMe() - Pass selection into it and return locators placed at the pivots of each object - matching translation, rotation and rotation order
#   6) groupMeObject(obj) - Pass object into it and return locators placed at the pivots of each object - matching translation, rotation and rotation order
#
# 3/4/2011 - added point, orient, parent snap functions as well as the list to heirarchy one
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.lib import guiFactory
from cgm.lib.classes import NameFactory
from cgm.lib import rigging
from cgm.lib import distance
from cgm.lib import search
from cgm.lib import geo
from cgm.lib import attributes
from cgm.lib import position

# Maya version check
mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Locator Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMe():
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass selection into it and return locators placed at the pivots of
	each object - matching translation, rotation and rotation order

	ARGUMENTS:
	Nothing

	RETURNS:
	returnBuffer(list) - list of locators
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	placeLoc = []
	placeLoc = (mc.ls (sl=True))
	returnBuffer = []
	for obj in placeLoc:
		buffer = locMeObject(obj)
		returnBuffer.append(buffer)
	return returnBuffer

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createLocFromObject(obj):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass  an object into it and get a named locator with stored info for updating it

	ARGUMENTS:
	obj(string)

	RETURNS:
	name(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	# make it
	nameBuffer = mc.spaceLocator()

	#store info
	attributes.storeInfo(nameBuffer[0],'cgmName',obj,False)
	attributes.storeInfo(nameBuffer[0],'cgmLocMode','fromObject',False)

	return ( NameFactory.doNameObject(nameBuffer[0]) )
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeCenter(objList,forceBBCenter = False):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass  an object into it and get a named locator with stored info for updating it

	ARGUMENTS:
	obj(string)

	RETURNS:
	name(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	# make it
	nameBuffer = mc.spaceLocator()

	#store info
	attributes.storeInfo(nameBuffer[0],'cgmSource',(','.join(objList)),False)
	attributes.storeInfo(nameBuffer[0],'cgmLocMode','selectCenter',False)
	attributes.storeInfo(nameBuffer[0],'cgmName',(str('_to_'.join(objList))),False)
	attributes.storeInfo(nameBuffer[0],'cgmTypeModifier','midPoint',False)

	posList = []

	for obj in objList:
		if mc.objExists(obj) == True:
			objInfo = returnInfoForLoc(obj,forceBBCenter)
			posList.append(objInfo['position'])

	objTrans = distance.returnAveragePointPosition(posList)

	mc.move (objTrans[0],objTrans[1],objTrans[2], nameBuffer[0])

	return ( NameFactory.doNameObject(nameBuffer[0]) )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doPositionLocator(locatorName,locInfo):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Position a locator with locator info generated from returnInfoForLoc

	ARGUMENTS:
	locatorName(string)
	locInfo(dict)

	RETURNS:
	success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if search.returnObjectType(locatorName) == 'locator':
		objTrans = locInfo['position']
		objRot = locInfo['rotation']
		correctRo = locInfo['rotationOrder']

		mc.move (objTrans[0],objTrans[1],objTrans[2], locatorName)
		mc.setAttr ((locatorName+'.rotateOrder'), correctRo)

		#Rotate
		if locInfo['objectType'] == 'polyFace':
			constBuffer = mc.normalConstraint((locInfo['createdFrom']),locatorName)
			mc.delete(constBuffer[0])
		else:
			mc.rotate (objRot[0], objRot[1], objRot[2], locatorName, ws=True)

		return True
	else:
		guiFactory.warning('Not a locator.')
		return False


def locClosest(objectList,targetObject):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Creates a locator on the surface of the last object in a selection set closest
	to each remaining object in the selection

	ARGUMENTS:
	objectList

	RETURNS:
	locatorList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	bufferList = []

	lastObjectType = search.returnObjectType(targetObject)
	
	#Get our source objects locators as sometimes the pivot has no correlation to the objects pivot - like a cv
	fromObjects = []
	for item in objectList:
		fromObjects.append(locMeObject(item))
	

	if lastObjectType == 'mesh':
		if mayaVersion >=2011:
			for item in fromObjects:
				bufferList.append( locMeClosestPointOnMesh(item, targetObject) )
		else:
			guiFactory.warning('Apologies, but in maya 2010 and below this only supports nurbsSurface target objects')
			return False
	elif lastObjectType == 'nurbsSurface':
		for item in fromObjects:
			bufferList.append( locMeClosestUVOnSurface(item, targetObject) )
	elif lastObjectType == 'nurbsCurve':
		if mayaVersion >=2011:
			for item in fromObjects:
				bufferList.append( locMeClosestPointOnCurve(item, targetObject) )
		else:
			guiFactory.warning('Apologies, but in maya 2010 and below this only supports nurbsSurface target objects')
			return False

	else:
		guiFactory.warning('Your target object must be a mesh, nurbsSurface, or nurbsCurve')
		return False

	for loc in fromObjects:
		mc.delete(loc)
		
	for loc in bufferList:
		cnt = bufferList.index(loc)
		storeList = []
		storeList = objectList
		storeList.append(targetObject)
		attributes.storeInfo(loc,'cgmName',('%s_to_%s'%(objectList[0],objectList[-1])),False)		
		attributes.storeInfo(loc,'cgmSource',(','.join(storeList)),False)
		attributes.storeInfo(loc,'cgmLocMode','closestPoint',False)
		attributes.storeInfo(loc,'cgmTypeModifier','closestPoint',False)
		bufferList[cnt] = NameFactory.doNameObject(loc)


	return bufferList[0]
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doUpdateLocator(locatorName,forceBBCenter = False):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Update a locator created with our nifty tool.

	ARGUMENTS:
	obj(string)

	RETURNS:
	name(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if search.returnObjectType(locatorName) == 'locator':
		locatorMode = search.returnTagInfo(locatorName,'cgmLocMode')
		if locatorMode == 'fromObject':
			obj = search.returnTagInfo(locatorName,'cgmName')
			if mc.objExists(obj) == True:
				"""get stuff to transfer"""
				locInfo = returnInfoForLoc(obj,forceBBCenter)
				doPositionLocator(locatorName,locInfo)
				return True
			else:
				guiFactory.warning ("The stored object doesn't exist")
				return False
			
		else:
			sourceObjects = search.returnTagInfo(locatorName,'cgmSource')
			targetObjectsBuffer = sourceObjects.split(',')
			targetObjects = []
			for obj in targetObjectsBuffer:
				if mc.objExists(obj):
					targetObjects.append(obj)
				else:
					guiFactory.warning  ('%s%s' % (obj, " not found, using any that are... "))
			if locatorMode == 'selectCenter':
				locBuffer = locMeCenter(targetObjects,forceBBCenter)
				position.moveParentSnap(locatorName,locBuffer)
				mc.delete(locBuffer)

			if locatorMode == 'closestPoint':
				locBuffer = locClosest(targetObjects[:-1],targetObjects[-1])
				position.moveParentSnap(locatorName,locBuffer)
				mc.delete(locBuffer)
				


	else:
		return False

	return locatorName
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeObject(obj,forceBBCenter = False):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass  an object into it and return locator placed at the pivots -
	matching translation, rotation and rotation order

	ARGUMENTS:
	obj(string)

	RETURNS:
	name(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	"""pass  an object into it and get locator placed at the pivots - matching translation, rotation and rotation order"""
	locatorName = createLocFromObject(obj)

	"""get stuff to transfer"""
	locInfo = returnInfoForLoc(obj,forceBBCenter)
	doPositionLocator(locatorName,locInfo)

	return locatorName
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeObjectStandAlone(obj):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass  an object into it and return locator placed at the pivots -
	matching translation, rotation and rotation order

	ARGUMENTS:
	obj(string)

	RETURNS:
	name(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	"""pass  an object into it and get locator placed at the pivots - matching translation, rotation and rotation order"""
	rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
	"""get stuff to transfer"""
	objTrans = mc.xform (obj, q=True, ws=True, sp=True)
	objRot = mc.xform (obj, q=True, ws=True, ro=True)
	objRoo = mc.xform (obj, q=True, roo=True )
	"""get rotation order"""
	correctRo = rotationOrderDictionary[objRoo]
	wantedName = (obj + '_loc')
	cnt = 1
	while mc.objExists(wantedName) == True:
		wantedName = ('%s%s%s%i' % (obj,'_','loc_',cnt))
		cnt +=1
	actualName = mc.spaceLocator (n= wantedName)

	""" account for multipleNamed things """
	if '|' in list(obj):
		locatorName = ('|'+actualName[0])
	else:
		locatorName = actualName[0]


	mc.move (objTrans[0],objTrans[1],objTrans[2], locatorName)
	mc.setAttr ((locatorName+'.rotateOrder'), correctRo)
	mc.rotate (objRot[0], objRot[1], objRot[2], locatorName, ws=True)

	return locatorName
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnInfoForLoc(obj,forceBBCenter = False):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Return info to create or update a locator.

	ARGUMENTS:
	obj(string)

	RETURNS:
	locInfo(dict)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	"""pass  an object into it and get locator placed at the pivots - matching translation, rotation and rotation order"""
	rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}

	"""get stuff to transfer"""
	objType = search.returnObjectType(obj)

	# vertex
	if objType == 'polyVertex':
		objTrans = mc.pointPosition(obj,w=True)
	elif objType == 'polyEdge':
		mc.select(cl=True)
		mc.select(obj)
		mel.eval("PolySelectConvert 3")
		edgeVerts = mc.ls(sl=True,fl=True)
		posList = []
		for vert in edgeVerts:
			posList.append(mc.pointPosition(vert,w=True))
		objTrans = distance.returnAveragePointPosition(posList)
		mc.select(cl=True)
	elif objType == 'polyFace':
		mc.select(cl=True)
		mc.select(obj)
		mel.eval("PolySelectConvert 3")
		edgeVerts = mc.ls(sl=True,fl=True)
		posList = []
		for vert in edgeVerts:
			posList.append(mc.pointPosition(vert,w=True))
		objTrans = distance.returnAveragePointPosition(posList)
		mc.select(cl=True)
	elif objType in ['surfaceCV','curveCV','editPoint','nurbsUV','curvePoint']:
		mc.select(cl=True)
		objTrans = mc.pointPosition (obj,w=True)
	else:
		if forceBBCenter == True:
			objTrans = distance.returnCenterPivotPosition(obj)
		else:
			objTrans = mc.xform (obj, q=True, ws=True, sp=True)

	objRot = mc.xform (obj, q=True, ws=True, ro=True)
	objRoo = mc.xform (obj, q=True, roo=True )

	"""get rotation order"""
	correctRo = rotationOrderDictionary[objRoo]


	locInfo = {}
	locInfo['createdFrom']=obj
	locInfo['objectType']=objType
	locInfo['position']=objTrans
	locInfo['rotation']=objRot
	locInfo['rotationOrder']=correctRo


	return locInfo
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def parentPivotLocMeObject(obj):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass  an object into it and return locator placed at the center of
	the bounding box of the object while matching other factors

	ARGUMENTS:
	obj(string)

	RETURNS:
	name(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	"""pass  an object into it and get locator placed at the pivots - matching translation, rotation and rotation order"""
	locBuffer = locMeObject(obj)

	""" see if there is a parent, if there is, copy the pivot of it, if not, set it to world center """
	parents = mc.listRelatives(obj,parent=True,fullPath=True)
	if parents != None:
		rigging.copyPivot(locBuffer,parents[0])
		return locBuffer
	else:
		worldCenterPivot = mc.spaceLocator()
		rigging.copyPivot(locBuffer,worldCenterPivot[0])
		mc.delete(worldCenterPivot)
		return locBuffer

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def centerPivotLocMeObject(obj):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass  an object into it and return locator placed at the center of
	the bounding box of the object while matching other factors

	ARGUMENTS:
	obj(string)

	RETURNS:
	name(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	"""pass  an object into it and get locator placed at the pivots - matching translation, rotation and rotation order"""
	rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}

	"""get stuff to transfer"""
	objTrans = distance.returnCenterPivotPosition(obj)
	objRot = mc.xform (obj, q=True, ws=True, ro=True)
	objRoo = mc.xform (obj, q=True, roo=True )

	"""get rotation order"""
	correctRo = rotationOrderDictionary[objRoo]
	wantedName = (obj + '_loc')
	cnt = 1
	while mc.objExists(wantedName) == True:
		wantedName = ('%s%s%s%i' % (obj,'_','loc_',cnt))
		cnt +=1
	actualName = mc.spaceLocator (n= wantedName)

	""" account for multipleNamed things """
	if '|' in list(obj):
		locatorName = ('|'+actualName[0])
	else:
		locatorName = actualName[0]


	mc.move (objTrans[0],objTrans[1],objTrans[2], locatorName)
	mc.setAttr ((locatorName+'.rotateOrder'), correctRo)
	mc.rotate (objRot[0], objRot[1], objRot[2], locatorName, ws=True)

	return locatorName
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def pointLocMeObj(obj):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass  an object into it and return locator placed at the pivot of the object

	ARGUMENTS:
	obj(string)

	RETURNS:
	name(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	"""return stuff to transfer"""
	objTrans = mc.xform (obj, q=True, ws=True, sp=True)

	wantedName = (obj + '_loc')
	actualName = mc.spaceLocator (n= wantedName)
	mc.move (objTrans[0],objTrans[1],objTrans[2], [actualName[0]])
	return actualName[0]
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeClosestPointOnCurve(obj, curve):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places a locator on the closest point on a curve to the target object

	ARGUMENTS:
	obj(string)
	curve(string)

	RETURNS:
	locatorName(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	locatorName = locMeObject(obj)
	objTrans = distance.returnClosestUPosition(obj,curve)

	mc.move (objTrans[0],objTrans[1],objTrans[2], locatorName)

	return locatorName

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLocPos(pos):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places a locator at a position in ws

	ARGUMENTS:
	pos(list)

	RETURNS:
	locatorName(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	locatorName = mc.spaceLocator(n='pos_loc')

	mc.move (pos[0],pos[1],pos[2], locatorName)

	return locatorName

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeClosestUVOnSurface(obj, surface, pivotOnSurfaceOnly = False):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locators on the cv's of a surface

	ARGUMENTS:
	curve(string)

	RETURNS:
	locList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	locBuffer = locMeObject(obj)
	pivotLoc = locMeObject(obj)

	controlSurface = mc.listRelatives(surface,shapes=True)

	""" make the closest point node """
	closestPointNode = mc.createNode ('closestPointOnSurface')
	""" to account for target objects in heirarchies """
	attributes.doConnectAttr((locBuffer+'.translate'),(closestPointNode+'.inPosition'))
	attributes.doConnectAttr((controlSurface[0]+'.worldSpace'),(closestPointNode+'.inputSurface'))

	""" make the pointOnSurfaceNode """
	pointOnSurfaceNode = mc.createNode ('pointOnSurfaceInfo')
	""" Connect the info node to the surface """
	attributes.doConnectAttr  ((controlSurface[0]+'.worldSpace'),(pointOnSurfaceNode+'.inputSurface'))
	""" Contect the pos group to the info node"""
	attributes.doConnectAttr ((pointOnSurfaceNode+'.position'),(pivotLoc+'.translate'))
	attributes.doConnectAttr ((closestPointNode+'.parameterU'),(pointOnSurfaceNode+'.parameterU'))
	attributes.doConnectAttr  ((closestPointNode+'.parameterV'),(pointOnSurfaceNode+'.parameterV'))

	if pivotOnSurfaceOnly != True:
		position.movePointSnap(locBuffer,pivotLoc)
	else:
		rigging.copyPivot(locBuffer,pivotLoc)


	mc.delete(closestPointNode)
	mc.delete(pointOnSurfaceNode)
	mc.delete(pivotLoc)

	#Rotate
	constBuffer = mc.normalConstraint(surface,locBuffer)
	mc.delete(constBuffer[0])

	return locBuffer

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeClosestPointOnMesh(obj, mesh):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locators on the closest point of a mesh to a target object

	ARGUMENTS:
	obj(string)
	mesh(string)

	RETURNS:
	locatorName(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	locatorName = locMeObject(obj)

	""" make the closest point node """
	closestPointNode = mc.createNode ('closestPointOnMesh')
	controlSurface = mc.listRelatives(mesh,shapes=True)

	""" to account for target objects in heirarchies """
	attributes.doConnectAttr((obj+'.translate'),(closestPointNode+'.inPosition'))
	attributes.doConnectAttr((controlSurface[0]+'.worldMesh'),(closestPointNode+'.inMesh'))
	attributes.doConnectAttr((controlSurface[0]+'.worldMatrix'),(closestPointNode+'.inputMatrix'))

	""" Contect the locator to the info node"""
	attributes.doConnectAttr ((closestPointNode+'.position'),(locatorName+'.translate'))


	faceIndex = mc.getAttr(closestPointNode+'.closestFaceIndex')
	face = ('%s%s%i%s' %(mesh,'.f[',faceIndex,']'))

	mc.delete(closestPointNode)
	#Rotate
	constBuffer = mc.normalConstraint(face,locatorName)
	mc.delete(constBuffer[0])

	return locatorName
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeCVOfCurve(curveCV):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locators on the cv's of a curve

	ARGUMENTS:
	curve(string)

	RETURNS:
	locList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if search.returnObjectType(curveCV) == 'curveCV':
		cvPos = mc.pointPosition (curveCV,w=True)
		wantedName = (curveCV + '_loc')
		actualName = mc.spaceLocator (n= wantedName)
		mc.move (cvPos[0],cvPos[1],cvPos[2], [actualName[0]])
		return actualName[0]
	else:
		guiFactory.warning  ('Not a curveCV')
		return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeCVOnCurve(curveCV):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locators on the cv's closest position on a curve

	ARGUMENTS:
	curve(string)

	RETURNS:
	locList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if search.returnObjectType(curveCV) == 'curveCV':
		cvPos = mc.pointPosition (curveCV,w=True)
		wantedName = (curveCV + '_loc')
		actualName = mc.spaceLocator (n= wantedName)
		mc.move (cvPos[0],cvPos[1],cvPos[2], [actualName[0]])
		splitBuffer = curveCV.split('.')
		uPos = distance.returnClosestUPosition (actualName[0],splitBuffer[0])
		mc.move (uPos[0],uPos[1],uPos[2], [actualName[0]])
		return actualName[0]
	else:
		guiFactory.warning  ('Not a curveCV')
		return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeCVsOfCurve(curve):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locators on the cv's of a curve

	ARGUMENTS:
	curve(string)

	RETURNS:
	locList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if mc.objExists (curve):
		locList = []
		cvList = []
		shapes = mc.listRelatives(curve,shapes=True,fullPath=True)
		for shape in shapes:
			cvList = (mc.ls ([shape+'.cv[*]'],flatten=True))		
			if cvList:
				mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(cvList))						
				for cv in cvList:
					if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
						break
					mc.progressBar(mayaMainProgressBar, edit=True, status = ("Procssing '%s'"%str(cv)), step=1)
	
					locList.append(locMeObject(cv))
					
				guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

	else:
		guiFactory.warning ('Curve does not exist')
		success = False
		return False
	
	if locList:
		return locList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeCVsOnCurve(curve):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locators on the cv's closest position on a curve

	ARGUMENTS:
	curve(string)

	RETURNS:
	locList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	locList = []
	if mc.objExists (curve):
		cvList = []
		shapes = mc.listRelatives(curve,shapes=True,fullPath=True)
		for shape in shapes:
			cvList = (mc.ls ([shape+'.cv[*]'],flatten=True))
			if cvList:
				mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(cvList))		
				for cv in cvList:
					if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
						break
					mc.progressBar(mayaMainProgressBar, edit=True, status = ("Procssing '%s'"%str(cv)), step=1)
	
					locList.append(locClosest([cv],curve))
					
				guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
			
	else:
		guiFactory.warning  ('Curve does not exist')
		return False
	
	if locList:
		return locList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeEditPoint(editPoint):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locators on the cv's of a curve

	ARGUMENTS:
	curve(string)

	RETURNS:
	locList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if search.returnObjectType(editPoint) == 'editPoint':
		pos = mc.pointPosition (editPoint,w=True)
		wantedName = (editPoint + '_loc')
		actualName = mc.spaceLocator (n= wantedName)
		mc.move (pos[0],pos[1],pos[2], [actualName[0]])
		return actualName[0]
	else:
		guiFactory.warning  ('Not an editPoint')
		return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeCvFromCvIndex(shape,cvIndex):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locators on the cv's closest position on a curve

	ARGUMENTS:
	curve(string)

	RETURNS:
	locList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	cv = ('%s%s%i%s'%(shape,'.cv[',cvIndex,']'))
	if mc.objExists(cv):
		cvPos = mc.pointPosition (cv,w=True)
		wantedName = (cv + 'loc')
		actualName = mc.spaceLocator (n= wantedName)
		mc.move (cvPos[0],cvPos[1],cvPos[2], [actualName[0]])
		uPos = distance.returnClosestUPosition (actualName[0],shape)
		mc.move (uPos[0],uPos[1],uPos[2], [actualName[0]])
		return actualName[0]
	else:
		guiFactory.warning  ('Shape does not exist')
		return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeSurfaceCV(cv):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Places locator on a cv of a surface

	ARGUMENTS:
	cv(string)
	cvIndex

	RETURNS:
	locList(list)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	cvPos = mc.pointPosition (cv,w=True)
	splitBuffer = cv.split('.')
	surface = splitBuffer[0]
	wantedName = (cv + 'loc')
	actualName = mc.spaceLocator (n= wantedName)
	mc.move (cvPos[0],cvPos[1],cvPos[2], [actualName[0]])
	return actualName[0]


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def locMeEdgeLoop(polyEdge):
	"""
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Creates a locator from an edgeloop

	ARGUMENTS:
	polyEdge(string)

	RETURNS:
	locatorName(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	# Get the loop
	if ':' in polyEdge:
		edges = mc.ls(polyEdge,flatten=True)
	elif ',' in polyEdge:
		edges = polyEdge
	else:
		edges = search.returnEdgeLoopFromEdge(polyEdge)

	mc.select(cl=True)
	mc.select(edges)

	mel.eval("PolySelectConvert 3")
	edgeVerts = mc.ls(sl=True,fl=True)
	postList = []
	for vert in edgeVerts:
		posList.append(mc.pointPosition(vert,w=True))
	objTrans = distance.returnAveragePointPosition(posList)
	mc.select(cl=True)

	# Make the loc
	locatorName = createLocFromObject(polyEdge)
	mc.move (objTrans[0],objTrans[1],objTrans[2], locatorName)

	# aim it
	posList = []
	for vtx in edgeVerts:
		posList.append( mc.pointPosition(vtx,w=True) )

	polyBuffer = geo.createPolyFromPosList(posList)

	constBuffer = mc.normalConstraint(polyBuffer,locatorName)
	mc.delete(constBuffer[0])
	mc.delete(polyBuffer)

	return locatorName


