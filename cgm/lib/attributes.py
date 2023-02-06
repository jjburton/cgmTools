#=================================================================================================================================================
#=================================================================================================================================================
#	attribute - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with attributes
# 
# ARGUMENTS:
# 	Maya
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - cgmonks.info@gmail.com
#	https://github.com/jjburton/cgmTools/wiki
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
#   
#=================================================================================================================================================

import maya.cmds as mc
from cgm.lib import guiFactory,dictionary,settings,lists

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()

#>>>Debug chunk===================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=================================================================

attrTypesDict = {'message':('message','msg'),
		 'double':('float','fl','f','doubleLinear','doubleAngle','double','d'),
		 'string':('string','s','str'),
		 'long':('long','int','i','integer'),
		 'bool':('bool','b','boolean'),
		 'enum':('enum','options','e'),
		 'double3':('vector','vec','v','double3','d3'),
		 'multi':('multi','m')}

attrCompatibilityDict = {'message':('message'),
			 'double':('float','doubleLinear','doubleAngle','double'),
			 'string':('string'),
			 'long':('long','integer'),
			 'bool':('bool',),
			 'enum':('enum'),
			 'double3':('vector','double3'),
			 'multi':('multi')}

dataConversionDict = {'long':int,
		      'string':str,
		      'double':float} 

d_attrCategoryLists = {'transform':('translateX','translateY','translateZ',
				    'rotateX','rotateY','rotateZ',
				    'scaleX','scaleY','scaleZ','visibility'),
		       'joint':('rotateOrder','rotateAxisX','rotateAxisY','rotateAxisZ',
				'inheritsTransform','drawStyle','radius',
				'jointTypeX','jointTypeY','jointTypeZ',
				'stiffnessX','stiffnessY','stiffnessZ',
				'preferredAngleX','preferredAngleY','preferredAngleZ',
				'jointOrientX','jointOrientY','jointOrientZ','segmentScaleCompensate','showManipDefault',
				'displayHandle','displayLocalAxis','selectHandleX','selectHandleY','selectHandleZ'),
		       'objectDisplayAttrs':('visibility','template','lodVisibility'),
		       'curveShapeAttrs':('intermediateObject','dispCV','dispEP','dispHull','dispGeometry'),
		       'locatorShape':('localPositionX','localPositionY','localPositionZ',
				       'localScaleX','localScaleY','localScaleZ'),
		       'overrideAttrs':('overrideEnabled','overrideDisplayType',
					'overrideLevelOfDetail','overrideShading',
					'overrideTexturing','overridePlayback',
					'overrideVisibility','overrideColor')}
def validateAttrArg(arg):
	"""
	Validate an attr arg to usable info
	"""
	try:
		if type(arg) in [list,tuple] and len(arg) == 2:
			obj = arg[0]
			attr = arg[1]
			combined = "%s.%s"%(arg[0],arg[1])
			if not mc.objExists(combined):
				raise Exception("validateAttrArg>>>obj doesn't exist: %s"%combined)
		elif mc.objExists(arg) and '.' in arg:
			obj = arg.split('.')[0]
			attr = '.'.join(arg.split('.')[1:])
			combined = arg
		else:
			raise Exception("validateAttrArg>>>Bad attr arg: %s"%arg)

		return {'obj':obj ,'attr':attr ,'combined':combined}
	except Exception as error:
		log.error("validateAttrArg>>Failure")
		raise Exception(error)

def returnCompatibleAttrs(sourceObj,sourceAttr,target,*a, **kw):
	""" 
	Returns compatible attributes

	Keyword arguments:
	attrType1(string)  
	attrType1(string)  
	"""
	assert mc.objExists('%s.%s'%(sourceObj,sourceAttr)) is True,"returnCompatibleAttrs error. '%s.%s' doesn't exist."%(sourceObj,sourceAttr)
	assert mc.objExists(target) is True,"'%s' doesn't exist."%(target)

	sourceType = validateRequestedAttrType( mc.getAttr((sourceObj+'.'+sourceAttr),type=True) )
	if sourceType:
		returnBuffer = []
		bufferDict = returnObjectsAttributeByTypeDict(target,attrTypesDict.get(sourceType),*a, **kw) or {}
		for key in list(bufferDict.keys()):
			returnBuffer.extend(bufferDict.get(key))
		if returnBuffer:    
			return returnBuffer
	return False




def validateRequestedAttrType(attrType):
	""" 
	Returns if an attr type is valid or not

	Keyword arguments:
	attrType(string)        
	"""          
	aType = False
	for option in list(attrTypesDict.keys()):
		if attrType in attrTypesDict.get(option): 
			aType = option
			break

	return aType

def validateAttrTypeMatch(attrType1,attrType2):
	""" 
	Returns if attr types match

	Keyword arguments:
	attrType1(string)  
	attrType1(string)  
	"""
	if attrType1 == attrType2:
		return True

	for option in list(attrTypesDict.keys()):
		if attrType1 in attrTypesDict.get(option) and attrType2 in attrTypesDict.get(option): 
			return True
	return False

def doAddAttr(obj,attrName,attrType,*a, **kw):
	""" 
	Adds an attr if you don't care to know the specific commands for each type

	Keyword arguments:
	obj(string) -- must exist in scene
	attrName(string) -- attribute name
	attrType(string) -- must be valid type. Type 'print attrTypesDict' for search dict  
	"""          
	#assert mc.objExists(obj) is True,"'%s' doesn't exists!. Can't add attribute"%obj
	assert mc.objExists('%s.%s'%(obj,attrName)) is not True,"'%s.%s' already exists. "%(obj,attrName)

	attrTypeReturn = validateRequestedAttrType(attrType)
	assert attrTypeReturn is not False,"'%s' is not a valid attribute type for creation."%attrType

	if attrTypeReturn == 'string':
		return addStringAttributeToObj(obj,attrName,*a, **kw)
	elif attrTypeReturn == 'double':
		return addFloatAttributeToObject(obj,attrName,*a, **kw)
	elif attrTypeReturn == 'string':
		return addStringAttributeToObj(obj,attrName,*a, **kw)
	elif attrTypeReturn == 'long':
		return addIntegerAttributeToObj(obj,attrName,*a, **kw) 
	elif attrTypeReturn == 'double3':
		return addVectorAttributeToObj(obj,attrName,*a, **kw)
	elif attrTypeReturn == 'enum':
		return addEnumAttrToObj(obj,attrName,*a, **kw)
	elif attrTypeReturn == 'bool':
		return addBoolAttrToObject(obj,attrName,*a, **kw)
	elif attrTypeReturn == 'message':
		return addMessageAttributeToObj(obj,attrName,*a, **kw)
	else:
		return False

def returnStandardAttrFlags(obj,attr): 
	""" 
	Returns a diciontary of locked,keyable,locked states of an attribute. If
	the attribute is numeric, it grabs the typical flags for that.

	Keyword arguments:
	obj(string) -- must exist in scene
	attr(string) -- name for an attribute    
	"""    
	nameCombined = "%s.%s"%(obj,attr)
	assert mc.objExists(nameCombined) is True,"'%s' doesn't exist!"%(nameCombined)

	objAttrs = mc.listAttr(obj, userDefined = True) or []
	dataDict = {'type':mc.getAttr(nameCombined,type=True),
		    'locked':mc.getAttr(nameCombined ,lock=True),
		'keyable':mc.getAttr(nameCombined ,keyable=True)}

	# So, if it's keyable, you have to use one attribute to read correctly, otherwise it's the other...awesome
	dynamic = False
	if attr in objAttrs:
		dynamic = True
	dataDict['dynamic'] = dynamic


	hidden = not mc.getAttr(nameCombined,channelBox=True)

	if dataDict.get('keyable'):
		hidden = mc.attributeQuery(attr, node = obj, hidden=True)
	dataDict['hidden'] = hidden

	enumData = False
	if dataDict.get('type') == 'enum' and dynamic == True:
		dataDict['enum'] = mc.addAttr(nameCombined,q=True, en = True)

	numeric = True
	if dataDict.get('type') in ['string','message','enum','bool']:
		numeric = False
	dataDict['numeric'] = numeric

	if dynamic:
		dataDict['readable']=mc.addAttr(nameCombined,q=True,r=True)
		dataDict['writable']=mc.addAttr(nameCombined,q=True,w=True)
		dataDict['storable']=mc.addAttr(nameCombined,q=True,s=True)
		dataDict['usedAsColor']=mc.addAttr(nameCombined,q=True,usedAsColor = True)        

	return dataDict

def returnNumericAttrSettingsDict(obj,attr): 
	""" 
	Returns a diciontary of max,min,ranges,softs and default settings of an attribute

	Keyword arguments:
	obj(string) -- must exist in scene
	attr(string) -- name for an attribute    

	Return:
	dataDict(dict)
	"""    
	nameCombined = "%s.%s"%(obj,attr)
	assert mc.objExists(nameCombined) is True,"'%s' doesn't exist!"%(nameCombined)

	objAttrs = mc.listAttr(obj, userDefined = True) or []

	dynamic = False
	if attr in objAttrs:
		dynamic = True

	numeric = True
	attrType = mc.getAttr(nameCombined,type=True)    
	if attrType in ['string','message','enum','bool']:
		numeric = False

	dataDict = {}    
	# Return numeric data    
	if not numeric or not dynamic or mc.attributeQuery(attr, node = obj, listChildren=True):
		return False
	else:
		dataDict['min'] = False                    
		if mc.attributeQuery(attr, node = obj, minExists=True):
			try:
				minValue =  mc.attributeQuery(attr, node = obj, minimum=True)
				if minValue is not False:
					dataDict['min'] = minValue[0]
			except:
				dataDict['min'] = False
				log.warning("'%s.%s' failed to query min value" %(obj,attr))

		dataDict['max'] = False                
		if mc.attributeQuery(attr, node = obj, maxExists=True):
			try:
				maxValue =  mc.attributeQuery(attr, node = obj, maximum=True)
				if maxValue is not False:
					dataDict['max']  = maxValue[0]                    
			except:
				dataDict['max']  = False
				log.warning("'%s.%s' failed to query max value" %(obj,attr))

		dataDict['default'] = False             
		if type(mc.addAttr(nameCombined,q=True,defaultValue = True)) is int or float:
			try:
				defaultValue = mc.attributeQuery(attr, node = obj, listDefault=True)
				if defaultValue is not False:
					dataDict['default'] = defaultValue[0]  
			except:
				dataDict['default'] = False
				log.warning("'%s.%s' failed to query default value" %(obj,attr))

		#>>> Soft values
		dataDict['softMax']  = False
		try:
			softMaxValue =  mc.attributeQuery(attr, node = obj, softMax=True)
			if softMaxValue is not False:
				dataDict['softMax'] = softMaxValue[0]                  
		except:
			dataDict['softMax']  = False

		dataDict['softMin']  = False
		try:
			softMinValue =  mc.attributeQuery(attr, node = obj, softMin=True)
			if softMinValue is not False:
				dataDict['softMin']  = softMinValue[0]                  
		except:
			dataDict['softMin']  = False

		#>>> Range
		try:
			dataDict['range'] =  mc.attributeQuery(attr, node = obj, range=True)
		except:
			dataDict['range'] = False

		try:
			dataDict['softRange'] =  mc.attributeQuery(attr, node = obj, softRange=True)
		except:
			dataDict['softRange'] = False 

		return dataDict


def returnAttributeDataDict(obj,attr,value = True,incoming = True, outGoing = True):
	""" 
	Returns a diciontary of parent,children,sibling of an attribute or False if nothing found   

	Keyword arguments:
	obj(string) -- must exist in scene
	attr(string) -- name for an attribute    
	"""       
	assert mc.objExists("%s.%s"%(obj,attr)) is True,"'%s.%s' doesn't exist!"%(obj,attr)

	returnDict = {}
	if value:
		returnDict['value'] = doGetAttr(obj,attr)
	if incoming:
		returnDict['incoming'] = returnDriverAttribute('%s.%s'%(obj,attr),False)
	if outGoing:
		returnDict['outGoing'] = returnDrivenAttribute('%s.%s'%(obj,attr),False)

	return returnDict

def returnAttrFamilyDict(obj,attr):
	""" 
	Returns a diciontary of parent,children,sibling of an attribute or False if nothing found   

	Keyword arguments:
	obj(string) -- must exist in scene
	attr(string) -- name for an attribute    
	"""       
	assert mc.objExists("%s.%s"%(obj,attr)) is True,"'%s.%s' doesn't exist!"%(obj,attr)

	returnDict = {}
	buffer = mc.attributeQuery(attr, node = obj, listParent=True)
	if buffer is not None:
		returnDict['parent'] = buffer[0]
	buffer= mc.attributeQuery(attr, node = obj, listChildren=True)
	if buffer is not None:
		returnDict['children'] = buffer
	buffer= mc.attributeQuery(attr, node = obj, listSiblings=True)
	if buffer is not None:
		returnDict['siblings'] = buffer

	if returnDict:
		return returnDict
	return False


def returnAttrListFromStringInput (stringInput1,stringInput2 = None):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Takes an list of string variables to add to an object as string
	attributes. Skips it if it exists.

	ARGUMENTS:
	stringInput(string/stringList)

	RETURNS:
	[obj,attr]
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if '.' in list(stringInput1):
		buffer = stringInput1.split('.')
		assert mc.objExists(buffer[0]) is True,"'%s' doesn't exsit"%buffer[0]
		assert len(buffer) == 2, "'%s' has too many .'s"%stringInput1
		obj = buffer [0]
		attr = buffer[1]
		return [obj,attr]
	elif len(stringInput1) == 2:
		assert mc.objExists(stringInput1[0]) is True,"'%s' doesn't exsit"%stringInput1[0]
		obj = stringInput1 [0]
		attr = stringInput1[1]
		return [obj,attr]
	elif stringInput2 !=None:
		assert mc.objExists(stringInput1) is True,"'%s' doesn't exsit"%stringInput1
		return [stringInput1,stringInput2]

	else:
		return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Storing fuctions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def storeInfo(obj,infoType,info,overideMessageCheck = False,leaveUnlocked = False):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Stores autoname stuff to an object where the variable name is the
	infoType and the info is the info stored
	-If info is object, it connects the attribute as a message to that object
	-If info is attribute, connected to attribute
	-Otherwise, stored as string

	ARGUMENTS:
	obj(string) - object to add our tag to
	infoType(string) - cgmName, cgmType, etc
	info(string) - info to store, object to connect to, attribute to connect to
	overideMessageCheck(bool) = default -False - whether to overide the objExists check

	RETURNS:
	True/False
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	typeDictionary = dictionary.initializeDictionary(typesDictionaryFile)
	namesDictionary = dictionary.initializeDictionary(namesDictionaryFile)
	settingsDictionary = dictionary.initializeDictionary(settingsDictionaryFile)
	attrTypes = returnObjectsAttributeTypes(obj)    
	goodToGo = False
	infoData = 0

	#Figure out the data type
	#==============      
	if type(info) is list:
		for o in info:
			if mc.objExists(o) and not overideMessageCheck:
				infoData = 'multiMessage'
				log.debug('Multi message mode!')
				break
	elif mc.objExists(info) and not overideMessageCheck and not '.' in list(info):#attribute check
		infoData = 'message'

	elif mc.objExists(info) and '.' in list(info):
		if '[' not in info:
			infoData = 'attribute'
		else:
			infoData = 'string'

	#Force leave  unlocked to be on in the case of referenced objects.
	if mc.referenceQuery(obj, isNodeReferenced=True):
		leaveUnlocked = True

	if infoType in settingsDictionary:
		infoTypeName = settingsDictionary.get(infoType)
		goodToGo = True
		# Checks to see if the type exists in the library
		if infoType == 'cgmType':
			if info in typeDictionary:
				goodToGo = True
			else:
				goodToGo = True
	else:
		infoTypeName = infoType
		goodToGo = True

	attributeBuffer = ('%s%s%s' % (obj,'.',infoTypeName))
	""" lock check """
	wasLocked = False
	if (mc.objExists(attributeBuffer)) == True:
		if mc.getAttr(attributeBuffer,lock=True) == True:
			wasLocked = True
			mc.setAttr(attributeBuffer,lock=False)

	if goodToGo == True:
		if infoData == 'message':
			storeObjectToMessage(info,obj,infoType)
			if leaveUnlocked != True:
				mc.setAttr(('%s%s%s' % (obj,'.',infoType)),lock=True)
		elif infoData == 'multiMessage':
			storeObjectsToMessage(info,obj,infoType)#Multi message!
		else:
			""" 
            if we get this far and it's a message node we're trying
            to store other data to we need to delete it
            """
			if mc.objExists(attributeBuffer) and mc.attributeQuery (infoTypeName,node=obj,msg=True):
				doDeleteAttr(obj,infoTypeName)
			"""
            Make our new string attribute if it doesn't exist
            """
			if mc.objExists(attributeBuffer) == False:
				addStringAttributeToObj(obj,infoTypeName)
				if leaveUnlocked != True:
					mc.setAttr(attributeBuffer,lock=True)
			"""
            set the data
            """
			if infoData == 'attribute':
				infoAttrType = mc.getAttr(info,type=True)
				if mc.objExists(obj+'.'+infoType):
					objAttrType = mc.getAttr((obj+'.'+infoType),type=True)
					if infoAttrType != objAttrType:
						doConvertAttrType((obj+'.'+infoType),infoAttrType)


				doConnectAttr(info,attributeBuffer)

				if leaveUnlocked != True:
					mc.setAttr(attributeBuffer,lock=True)
			else:
				doSetStringAttr(attributeBuffer,info)
				if leaveUnlocked != True:
					mc.setAttr(attributeBuffer,lock=True)
		return True
	else:
		return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Set/Copy/Delete Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doGetAttr(obj,attr,*a, **kw):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Replacement for getAttr which get's message objects as well as parses double3 type 
	attributes to a list

	ARGUMENTS:
	obj(string)
	attr(string)

	RETURNS:
	attrInfo(varies)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	try:
		if not mc.objExists(obj+'.'+attr):
			return False
		else:
			if "[" in attr:
				log.debug("Indexed attr")
				return mc.listConnections(obj+'.'+attr)

			attrType = mc.getAttr((obj+'.'+attr),type=True)
			if attrType in ['TdataCompound']:
				return mc.listConnections(obj+'.'+attr)		
			objAttributes =(mc.listAttr (obj))
			messageBuffer = []
			messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
			if messageQuery == True:
				query = (mc.listConnections(obj+'.'+attr))
				if not query == None:
					return query[0]
				else:
					return False        
			elif attrType == 'double3':
				childrenAttrs = mc.attributeQuery(attr, node =obj, listChildren = True)
				dataBuffer = []
				for childAttr in childrenAttrs:
					dataBuffer.append(mc.getAttr(obj+'.'+childAttr))
				return dataBuffer
			elif attrType == 'double':
				parentAttr = mc.attributeQuery(attr, node =obj, listParent = True)
				return mc.getAttr("%s.%s"%(obj,attr),*a, **kw)
			else:
				return mc.getAttr("%s.%s"%(obj,attr),*a, **kw)
	except Exception as error:
		raise Exception("doGetError Fail! | obj:'{0}' | attr:'{1}' | {2}".format(obj,attr,error))






#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def doConnectAttr(fromAttr,toAttr,forceLock = False,transferConnection=False):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Replacement for setAttr which will unlock a locked node it's given
	to force a setting of the values. Also has a lock when done overide.
	In addition has transfer connections ability for buffer nodes.

	ARGUMENTS:
	attribute(string) - 'obj.attribute'
	value() - depends on the attribute type
	forceLock(bool) = False(default)
	transferConnection(bool) - (False) - whether you wante to transfer the existing connection to or not
	                                    useful for buffer connections
	RETURNS:
	nothin
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert fromAttr != toAttr,"Cannot connect an attriubute to itself. The world might blow up!"

	wasLocked = False
	if (mc.objExists(toAttr)) == True:
		if mc.getAttr(toAttr,lock=True) == True:
			wasLocked = True
			mc.setAttr(toAttr,lock=False)
		bufferConnection = returnDriverAttribute(toAttr)
		attrBuffer = returnObjAttrSplit(toAttr)
		if not attrBuffer:
			return False
		doBreakConnection(attrBuffer[0],attrBuffer[1])
		mc.connectAttr(fromAttr,toAttr)     

	if transferConnection == True:
		if bufferConnection != False:
			mc.connectAttr(bufferConnection,toAttr)

	if wasLocked == True or forceLock == True:
		mc.setAttr(toAttr,lock=True)

def isKeyed(arg):
	"""passes to validateAttrArg for validation. Returns if obj attr is keyed"""
	d_valid = validateAttrArg(arg)
	if mc.keyframe(d_valid['combined'], query=True):return True
	return False

def isConnected(arg):
	"""passes to validateAttrArg for validation. Returns if obj attr is keyed"""
	d_valid = validateAttrArg(arg)
	if mc.connectionInfo(d_valid['combined'], isDestination=True):return True
	return False

def doSetAttr(obj, attribute, value, forceLock = False, *a, **kw):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Replacement for setAttr which will unlock a locked node it's given
	to force a setting of the values. It will also break connections to
	set a value. Also has a lock when done overide

	ARGUMENTS:
	obj(string)
	attribute(string)
	value() - depends on the attribute type
	forceLock(bool) = False(default)

	RETURNS:
	nothin
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrBuffer = '%s.%s'%(obj,attribute)
	wasLocked = False

	if (mc.objExists(attrBuffer)) == True:
		try:
			attrType = mc.getAttr(attrBuffer,type=True)
			attrType = validateRequestedAttrType(attrType)
			if mc.getAttr(attrBuffer,lock=True) == True:
				wasLocked = True
				mc.setAttr(attrBuffer,lock=False)

			if not isKeyed([obj,attribute]):
				if doBreakConnection(obj,attribute):
					log.warning("'%s' connection broken"%(attrBuffer))

			if validateRequestedAttrType(attrType) == 'long':
				mc.setAttr(attrBuffer,int(float(value)), *a, **kw)
			elif validateRequestedAttrType(attrType) == 'string':
				mc.setAttr(attrBuffer,str(value),type = 'string', *a, **kw)
			elif validateRequestedAttrType(attrType) == 'double':
				mc.setAttr(attrBuffer,float(value), *a, **kw)
			else:
				mc.setAttr(attrBuffer,value, *a, **kw)

			if wasLocked == True or forceLock == True:
				mc.setAttr(attrBuffer,lock=True)
			log.debug("'%s' set to '%s'"%(attrBuffer,value))
		except Exception as error:
			log.error(error)
			log.warning("Failed to set '%s' with '%s'"%(attrBuffer,value))

def doMultiSetAttr(objList, attribute, value, forceLock = False, *a, **kw):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pushes doSetAttr to a list of objects

	ARGUMENTS:
	objList(list)
	attribute(string)
	value() - depends on the attribute type
	forceLock(bool) = False(default)

	RETURNS:
	Success
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	for obj in objList:
		attrBuffer = '%s.%s'%(obj,attribute)
		if (mc.objExists(attrBuffer)):
			doSetAttr(obj,attribute,value,forceLock,**kw)
		else:
			log.warning("'%s' doesn't exist! Skipping..."%attrBuffer)

def setAttrsFromDict(obj, attrs = None, pushToShapes = False):
	"""
	Function for changing drawing override settings on on object

	Keyword arguments:
	attrs -- default will set all override attributes to default settings
	(dict) - pass a dict in and it will attempt to set the key to it's indexed value ('attr':1}
	(list) - if a name is provided and that attr is an override attr, it'll reset only that one
	"""
	# First make sure the drawing override attributes exist on our instanced object
	log.info("THIS FUNCTION ISN'T DONE!")
	#Get what to act on
	targets = [obj]
	if pushToShapes:
		buffer = mc.listRelatives(self.mNode,shapes=True,fullPath=fullPath) or []
		if buffer:	
			targets.extend(buffer)

	for t in targets:
		if issubclass(attrs,dict):
			for a in list(attrs.keys()):
				try:
					attributes.doSetAttr(t,a,attrs[a])
				except Exception as error:
					raise Exception("There was a problem setting '%s.%s' to %s"%(obj,a,attrs[a]))


def doSetStringAttr(attribute,value,forceLock = False):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Replacement for setAttr which will unlock a locked node it's given
	to force a setting of the values. Also has a lock when done overide

	ARGUMENTS:
	attribute(string) - 'obj.attribute'
	value() - depends on the attribute type
	forceLock(bool) = False(default)

	RETURNS:
	nothin
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	wasLocked = False
	if (mc.objExists(attribute)) == True:
		if mc.getAttr(attribute,lock=True) == True:
			wasLocked = True
			doBreakConnection(attribute)
			mc.setAttr(attribute,lock=False)
			mc.setAttr(attribute,value, type='string')
		else:
			doBreakConnection(attribute)
			mc.setAttr(attribute,value, type='string')

	if wasLocked == True or forceLock == True:
		mc.setAttr(attribute,lock=True)

def doRenameAttr(obj,oldAttrName,newAttrName,forceLock = False):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Replacement for setAttr which will unlock a locked node it's given
	to force a setting of the values. Also has a lock when done overide

	ARGUMENTS:
	attribute(string) - 'obj.attribute'
	value() - depends on the attribute type
	forceLock(bool) = False(default)

	RETURNS:
	nothin
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	wasLocked = False
	combinedBuffer = '%s.%s'%(obj,oldAttrName)
	if (mc.objExists(combinedBuffer)) == True:
		if mc.getAttr(combinedBuffer,lock=True) == True:
			wasLocked = True
			mc.setAttr(combinedBuffer,lock=False)
			mc.renameAttr(combinedBuffer,newAttrName)
		else:
			mc.renameAttr(combinedBuffer,newAttrName)

	if wasLocked == True or forceLock == True:
		newBuffer = '%s.%s'%(obj,newAttrName)
		mc.setAttr(newBuffer,lock=True)

def doConvertAttrType(targetAttrName,attrType):
	""" 
	Attempts to convert an existing attrType from one type to another. 
	Enum's are stored to strings as 'option1;option2'.
	Strings with a ';' will split to enum options on conversion.

	Keyword arguments:
	targetAttrName(string) -- name for an existing attribute name
	attrType(string) -- desired attribute type

	"""    
	assert mc.objExists(targetAttrName) is True,"'%s' doesn't exist!"%targetAttrName

	aType = False
	for option in list(attrTypesDict.keys()):
		if attrType in attrTypesDict.get(option): 
			aType = option
			break

	assert aType is not False,"'%s' is not a valid attribute type!"%attrType


	#>>> Get data
	targetLock = False
	if mc.getAttr((targetAttrName),lock = True) == True:
		targetLock = True
		mc.setAttr(targetAttrName,lock = False)

	targetType = mc.getAttr(targetAttrName,type=True)

	buffer = targetAttrName.split('.')
	targetObj = buffer[0]
	targetAttr = buffer[-1]


	#>>> Do the stuff
	if aType != targetType:
		# get data connection and data to transfer after we make our new attr
		# see if it's a message attribute to copy    
		connection = ''
		if mc.attributeQuery (targetAttr,node=targetObj,msg=True):
			dataBuffer = (returnMessageObject(targetObj,targetAttr))
		else:
			connection = returnDriverAttribute(targetAttrName)            
			dataBuffer = mc.getAttr(targetAttrName)

		if targetType == 'enum':           
			dataBuffer = mc.addAttr((targetObj+'.'+targetAttr),q=True, en = True)


		doDeleteAttr(targetObj,targetAttr)

		"""if it doesn't exist, make it"""
		if aType == 'string':
			mc.addAttr (targetObj, ln = targetAttr,  dt = aType )

		elif aType == 'enum':
			enumStuff  = 'off:on'
			if dataBuffer:
				if type(dataBuffer) is str or type(dataBuffer) is str:
					enumStuff = dataBuffer
			mc.addAttr (targetObj, ln = targetAttr, at=  'enum', en = enumStuff)

		elif aType == 'double3':
			mc.addAttr (targetObj, ln=targetAttr, at= 'double3')
			mc.addAttr (targetObj, ln=(targetAttr+'X'),p=targetAttr , at= 'double')
			mc.addAttr (targetObj, ln=(targetAttr+'Y'),p=targetAttr , at= 'double')
			mc.addAttr (targetObj, ln=(targetAttr+'Z'),p=targetAttr , at= 'double')
		else:
			mc.addAttr (targetObj, ln = targetAttr,  at = aType )

		if connection:
			try:
				doConnectAttr(connection,targetAttrName)
			except:
				log.warning("Couldn't connect '%s' to the '%s'"%(connection,targetAttrName))

		elif dataBuffer is not None:
			if mc.objExists(dataBuffer) and aType == 'message':
				storeObjectToMessage(dataBuffer,targetObj,targetAttr)
			else:
				try:
					if aType == 'long':
						mc.setAttr(targetAttrName,int(float(dataBuffer)))
					elif aType == 'string':
						mc.setAttr(targetAttrName,str(dataBuffer),type = aType)
					elif aType == 'double':
						mc.setAttr(targetAttrName,float(dataBuffer))   
					else:
						mc.setAttr(targetAttrName,dataBuffer,type = aType)
				except:
					log.warning("Couldn't add '%s' to the '%s'"%(dataBuffer,targetAttrName))


		if targetLock:
			mc.setAttr(targetAttrName,lock = True)

def returnMatchNameAttrsDict(fromObject,toObject,attributes=[True],directMatchOnly = False,*a, **kw ):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Tries to find match attrs regardless of name alias or what not in dict form.

	ARGUMENTS:
	fromObject(string) - obj with attrs
	toObject(string) - obj to check
	attrsToCopy(list) - list of attr names to copy, if [True] is used, it will do all of them
	directMatchOnly(bool) =- whether to check longNames (ignores alias'). Default is the wider search (False)

	If attriubtes is set to default ([True]), you can pass keywords and arguments into a listAttr call for the 
	search parameters


	RETURNS:
	matchAttrs(dict) = {sourceAttr:targetAttr, }
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	matchAttrs = {}
	if attributes[0] is True:
		attributes = mc.listAttr(fromObject, *a, **kw) or []

	if attributes:
		for attr in attributes:
			if mc.objExists('%s.%s'%(fromObject, attr) ):
				if directMatchOnly:
					if mc.objExists('%s.%s'%(toObject, attr) ):
						matchAttrs[attr] = attr                        
				else:
					try:
						buffer = mc.attributeQuery(attr,node=fromObject,longName=True) or ''                    
						if mc.objExists('%s.%s'%(toObject, buffer) ):
							matchAttrs[attr] = buffer
					except:
						log.warning("'%s' failed to query a long name to check"%attr)
		if matchAttrs:
			return matchAttrs
		else:
			return False
	return False


def doCopyAttr(fromObject,fromAttr, toObject, toAttr = None, *a,**kw):
	"""                                     
	DESCRIPTION:
	Replacement for Maya's since maya's can't handle shapes....blrgh...
	Copy attributes from one object to another as well as other options. If the attribute already
	exists, it'll copy the values. If it doesn't, it'll make it. If it needs to convert, it can.
	It will not make toast.

	Keywords:
	fromObject(string) - obj with attrs
	fromAttr(string) - source attribute
	toObject(string) - obj to copy to
	toAttr(string) -- name of the attr to copy to . Default is None which will create an 
	                  attribute of the fromAttr name on the toObject if it doesn't exist
	convertToMatch(bool) -- whether to automatically convert attribute if they need to be. Default True                  
	values(bool) -- copy values. default True
	inputConnections(bool) -- default False
	outGoingConnections(bool) -- default False
	keepSourceConnections(bool)-- keeps connections on source. default True
	copyAttrSettings(bool) -- copy the attribute state of the fromAttr (keyable,lock,hidden). default True
	connectSourceToTarget(bool) --useful for moving attribute controls to another object. default False
	connectTargetToSource(bool) --useful for moving attribute controls to another object. default False

	RETURNS:
	success(bool)
	"""
	#>>>Keyword args
	convertToMatch = kw.pop('convertToMatch',True)
	values = kw.pop('values',True)
	inputConnections = kw.pop('inputConnections',False)
	outgoingConnections = kw.pop('outgoingConnections',False)
	keepSourceConnections = kw.pop('keepSourceConnections',True)
	copyAttrSettings = kw.pop('copyAttrSettings',True)
	connectSourceToTarget = kw.pop('connectSourceToTarget',False)
	connectTargetToSource = kw.pop('connectTargetToSource',False) 

	if not mc.objExists('%s.%s'%(fromObject,fromAttr)):
		log.debug("doCopyAttr error. Source '%s.%s' doesn't exist"%(fromObject,fromAttr))
		return False
	assert mc.objExists(toObject) is True,"Target '%s' doesn't exist"%toObject

	# Gather info   
	sourceFlags = returnStandardAttrFlags(fromObject,fromAttr)
	sourceType = sourceFlags.get('type')

	if values and not validateRequestedAttrType(sourceType):
		log.warning("'%s.%s' is a '%s' and not valid for copying."%(fromObject,fromAttr,sourceType))             
		return False

	sourceLock = sourceFlags.get('locked')
	sourceKeyable = sourceFlags.get('keyable')
	sourceHidden = sourceFlags.get('hidden')
	sourceDynamic = sourceFlags.get('dynamic')
	sourceNumeric = sourceFlags.get('numeric')
	if sourceNumeric:
		sourceNumericFlags = returnNumericAttrSettingsDict(fromObject,fromAttr)
		if sourceNumericFlags:
			sourceDefault = sourceNumericFlags.get('default')
			sourceMax = sourceNumericFlags.get('max')
			sourceMin = sourceNumericFlags.get('min')
			sourceSoftMax = sourceNumericFlags.get('softMax')
			sourceSoftMin = sourceNumericFlags.get('softMin')

	sourceEnum = False
	if sourceType == 'enum':
		sourceEnum = sourceFlags.get('enum')

	goodToGo = True
	targetExisted = False
	relockSource = False

	#Let's check on the target attr
	if toAttr is not None:
		#If an attr is specified
		if mc.objExists('%s.%s'%(toObject,toAttr)):
			#If it exists, verify the types match and get standard flags
			targetExisted = True
			targetFlags = returnStandardAttrFlags(toObject,toAttr)
			targetType = targetFlags.get('type')
			targetLock = targetFlags.get('locked')
			targetKeyable = targetFlags.get('keyable')
			targetHidden = targetFlags.get('hidden')
			targetDynamic = targetFlags.get('dynamic')   
			if not validateRequestedAttrType(targetType):
				log.warning("'%s.%s' is a '%s' and may not copy correctly."%(toObject,toAttr,sourceType))             

			if not validateAttrTypeMatch(targetType,sourceType):
				#If it doesn't match, covert
				if sourceDynamic and convertToMatch:
					log.warning("'%s.%s' must be converted. It's type is not '%s'"%(toObject,toAttr,targetType))              
					if targetLock:
						mc.setAttr('%s.%s'%(toObject,toAttr),lock = False)
						relockSource = True
					doConvertAttrType(('%s.%s'%(toObject,toAttr)),sourceType)
				else:
					goodToGo = False


		elif doAddAttr(toObject,toAttr,sourceType):
			#If it doesn't exist, make it
			log.debug("'%s.%s' created!"%(toObject,toAttr))            
		else:
			return False

	else:
		#If no attr is specified (None), we first look to see if our target has an attr called what our source is
		matchAttrs = returnMatchNameAttrsDict(fromObject,toObject,[fromAttr])
		if matchAttrs:
			targetFlags = returnStandardAttrFlags(toObject,matchAttrs.get(fromAttr))
			targetType = targetFlags.get('type')
			targetLock = targetFlags.get('locked')
			targetKeyable = targetFlags.get('keyable')
			targetHidden = targetFlags.get('hidden')
			targetDynamic = targetFlags.get('dynamic')  

			if not targetType:
				log.warning("'%s.%s' has no type."%(toObject,toAttr))             
				return False    

			if not validateAttrTypeMatch(targetType,sourceType):
				if sourceDynamic and convertToMatch:
					toAttr = fromAttr                    
					#f the match attr doesnt' type as well, convert
					log.debug("Match is '%s', needs to be '%s'"%(targetType,sourceType))  
					if targetLock:
						mc.setAttr('%s.%s'%(toObject,toAttr),lock = False)
						relockSource = True                        
					doConvertAttrType(('%s.%s'%(toObject,toAttr)),sourceType)
				else:
					goodToGo = False
					toAttr = matchAttrs.get(fromAttr)
			else:
				#Otherwise, good to go
				toAttr = matchAttrs.get(fromAttr)                   

		elif doAddAttr(toObject,fromAttr,sourceType):
			toAttr = fromAttr
			log.debug("'%s.%s' created!"%(toObject,fromAttr))   

	if not goodToGo:
		log.warning("'%s.%s' may not copy well to '%s.%s'. Source type is '%s', target type is '%s'. Conversion mode is off"%(fromObject,fromAttr,toObject,toAttr,sourceType,targetType))

	#Let's get our data    
	dataDict = returnAttributeDataDict(fromObject,fromAttr)

	if values:
		if sourceType == 'message' and dataDict.get('value'):
			storeInfo(toObject,toAttr,dataDict.get('value'))
		else:
			doSetAttr(toObject,toAttr,dataDict.get('value'))

	if inputConnections and not connectSourceToTarget:
		buffer = dataDict['incoming']
		if buffer:
			try:
				doConnectAttr(buffer,('%s.%s'%(toObject,toAttr)))
				if not keepSourceConnections:
					doBreakConnection('%s.%s'%(fromObject,fromAttr))
			except:
				if sourceType != 'message':
					log.warning("Inbound fail - '%s.%s' failed to connect to '%s"%(fromObject,fromAttr,buffer))

	if outgoingConnections and not connectSourceToTarget:
		if dataDict['outGoing']:
			for connection in dataDict['outGoing']:
				try:
					doConnectAttr(('%s.%s'%(toObject,toAttr)),connection)

				except:
					log.warning("Outbound fail - '%s' failed to connect to '%s.%s'"%(connection,toObject,toAttr))

	if copyAttrSettings:
		if sourceEnum:
			mc.addAttr (('%s.%s'%(toObject,toAttr)), e = True, at=  'enum', en = sourceEnum)
		if sourceNumeric and sourceNumericFlags:
			if sourceDefault:
				mc.addAttr((toObject+'.'+toAttr),e=True,dv = sourceDefault)
			if sourceMax:
				mc.addAttr((toObject+'.'+toAttr),e=True,maxValue = sourceMax)                
			if sourceMin:
				mc.addAttr((toObject+'.'+toAttr),e=True,minValue = sourceMin)                
			if sourceSoftMax:
				mc.addAttr((toObject+'.'+toAttr),e=True,softMaxValue = sourceSoftMax)                
			if sourceSoftMin:
				mc.addAttr((toObject+'.'+toAttr),e=True,softMinValue = sourceSoftMin)                

		mc.setAttr(('%s.%s'%(toObject,toAttr)),e=True,channelBox = not sourceHidden)
		mc.setAttr(('%s.%s'%(toObject,toAttr)),e=True,keyable = sourceKeyable)
		mc.setAttr(('%s.%s'%(toObject,toAttr)),e=True,lock = sourceLock)


	if connectSourceToTarget:
		try:            
			doConnectAttr(('%s.%s'%(toObject,toAttr)),('%s.%s'%(fromObject,fromAttr)))
		except:
			log.warning("Connect to target fail - '%s.%s' failed to connect to '%s.%s'"%(fromObject,fromAttr,toObject,toAttr))

	elif connectTargetToSource:
		try:            
			doConnectAttr(('%s.%s'%(fromObject,fromAttr)),('%s.%s'%(toObject,toAttr)))
		except:
			log.warning("Connect to source fail - '%s.%s' failed to connect to '%s.%s'"%(fromObject,fromAttr,toObject,toAttr))

	if relockSource:
		mc.setAttr('%s.%s'%(toObject,toAttr),lock = True)

	return True



def copyKeyableAttrs(fromObject,toObject,attrsToCopy=[True],connectAttrs = False):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Copy attributes from one object to another. If the attribute already
	exists, it'll copy the values. If it doesn't, it'll make it.

	ARGUMENTS:
	fromObject(string) - obj with attrs
	toObject(string) - obj to copy to
	attrsToCopy(list) - list of attr names to copy, if [True] is used, it will do all of them

	RETURNS:
	success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrDict = {}
	keyableAttrs =(mc.listAttr (fromObject, keyable=True))
	matchAttrs = []
	lockAttrs = {}
	if keyableAttrs == None:
		return False
	else:
		if attrsToCopy[0] == 1:
			matchAttrs = keyableAttrs
		else:
			for attr in attrsToCopy:
				if attr in keyableAttrs:
					matchAttrs.append(attr)
	""" Get the attribute types of those the source object"""
	attrTypes = returnObjectsAttributeTypes(fromObject)

	print ('The following attrirbues will be created and copied')
	print(matchAttrs)
	#>>> The creation of attributes part
	if len(matchAttrs)>0:
		for attr in matchAttrs:
			""" see if it was locked, unlock it and store that it was locked """
			if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
				lockAttrs[attr] = True
				mc.setAttr((fromObject+'.'+attr),lock=False)
			"""if it doesn't exist, make it"""
			if mc.objExists(toObject+'.'+attr) is not True:
				attrType = (attrTypes.get(attr))

				if attrType == 'string':
					mc.addAttr (toObject, ln = attr,  dt =attrType )
				elif attrType == 'enum':
					enumStuff = mc.attributeQuery(attr, node=fromObject, listEnum=True)
					mc.addAttr (toObject, ln=attr, at= 'enum', en=enumStuff[0])
				elif attrType == 'double3':
					mc.addAttr (toObject, ln=attr, at= 'double3')
					mc.addAttr (toObject, ln=(attr+'X'),p=attr , at= 'double')
					mc.addAttr (toObject, ln=(attr+'Y'),p=attr , at= 'double')
					mc.addAttr (toObject, ln=(attr+'Z'),p=attr , at= 'double')
				else:
					mc.addAttr (toObject, ln = attr,  at =attrType )
		""" copy values """
		mc.copyAttr(fromObject,toObject,attribute=matchAttrs,v=True,ic=True)

		""" relock """
		for attr in list(lockAttrs.keys()):
			mc.setAttr((fromObject+'.'+attr),lock=True)
			mc.setAttr((toObject+'.'+attr),lock=True)


		""" Make it keyable """    
		for attr in matchAttrs:
			mc.setAttr((toObject+'.'+attr),keyable=True)

		if connectAttrs:
			for attr in matchAttrs:
				doConnectAttr((toObject+'.'+attr),(fromObject+'.'+attr))

		return True

	else:
		return False


def copyUserAttrs(fromObject,toObject,attrsToCopy=[True]):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Copy attributes from one object to another. If the attribute already
	exists, it'll copy the values. If it doesn't, it'll make it.

	ARGUMENTS:
	fromObject(string) - obj with attrs
	toObject(string) - obj to copy to
	attrsToCopy(list) - list of attr names to copy, if [True] is used, it will do all of them

	RETURNS:
	success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrDict = {}
	userAttrs =(mc.listAttr (fromObject, userDefined=True))
	matchAttrs = []
	lockAttrs = {}
	if userAttrs == None:
		return False
	else:
		if attrsToCopy[0] == 1:
			matchAttrs = userAttrs
		else:
			for attr in attrsToCopy:
				if attr in userAttrs:
					matchAttrs.append(attr)
	""" Get the attribute types of those the source object"""
	attrTypes = returnObjectsAttributeTypes(fromObject)

	#>>> The creation of attributes part
	messageAttrs = {}
	if len(matchAttrs)>0:
		for attr in matchAttrs:
			# see if it's a message attribute to copy  
			if mc.attributeQuery (attr,node=fromObject,msg=True):
				messageAttrs[attr] = (returnMessageObject(fromObject,attr))

			""" see if it was locked, unlock it and store that it was locked """
			if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
				lockAttrs[attr] = True
				mc.setAttr((fromObject+'.'+attr),lock=False)

			"""if it doesn't exist, make it"""
			if mc.objExists(toObject+'.'+attr) is not True:
				attrType = (attrTypes.get(attr))
				if attrType == 'string':
					mc.addAttr (toObject, ln = attr,  dt =attrType )
				elif attrType == 'enum':
					enumStuff = mc.attributeQuery(attr, node=fromObject, listEnum=True)
					mc.addAttr (toObject, ln=attr, at= 'enum', en=enumStuff[0])
				elif attrType == 'double3':
					mc.addAttr (toObject, ln=attr, at= 'double3')
					mc.addAttr (toObject, ln=(attr+'X'),p=attr , at= 'double')
					mc.addAttr (toObject, ln=(attr+'Y'),p=attr , at= 'double')
					mc.addAttr (toObject, ln=(attr+'Z'),p=attr , at= 'double')
				else:
					mc.addAttr (toObject, ln = attr,  at =attrType )
		""" copy values """
		mc.copyAttr(fromObject,toObject,attribute=matchAttrs,v=True,ic=True,oc=True,keepSourceConnections=True)

		if messageAttrs:
			for a in list(messageAttrs.keys()):
				storeInfo(toObject,a,messageAttrs.get(a))

		""" relock """
		for attr in list(lockAttrs.keys()):
			mc.setAttr((fromObject+'.'+attr),lock=True)
			mc.setAttr((toObject+'.'+attr),lock=True)
		return True
	else:
		return False

def copyNameTagAttrs(fromObject,toObject):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Copy cgmTag attrs from one object to another. 

	ARGUMENTS:
	fromObject(string) - obj with attrs
	toObject(string) - obj to copy to

	RETURNS:
	success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	lockAttrs = {}
	attrsToCopy = ['cgmName','cgmType','cgmDirection','cgmPosition','cgmNameModifier','cgmTypeModifier','cgmDirectionModifier']
	tagsDict = returnUserAttrsToDict(fromObject)

	#>>> The creation of attributes part
	if len(list(tagsDict.keys()))>0:
		for attr in list(tagsDict.keys()):

			"""if it doesn't exist, store  it"""
			if mc.objExists(fromObject+'.'+attr) and attr in attrsToCopy:
				""" see if it was locked, unlock it and store that it was locked """  
				if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
					lockAttrs[attr] = True

				storeInfo(toObject,attr,tagsDict.get(attr))


		""" relock """
		for attr in list(lockAttrs.keys()):
			mc.setAttr((fromObject+'.'+attr),lock=True)
			mc.setAttr((toObject+'.'+attr),lock=True)
		return True
	else:
		return False

def swapNameTagAttrs(object1,object2):
	"""                                     
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Swap cgmNameTag attrs from one object to another. 

	ARGUMENTS:
	fromObject(string) - 
	toObject(string) - 

	RETURNS:
	None
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	object1LockAttrs = {}
	object2LockAttrs = {}

	attrsToCopy = ['cgmName','cgmType','cgmDirection','cgmPosition','cgmNameModifier','cgmTypeModifier','cgmDirectionModifier']
	object1TagsDict = returnUserAttrsToDict(object1)
	object2TagsDict = returnUserAttrsToDict(object2)

	object1TagTypesDict = returnObjectsAttributeTypes(object1,userDefined = True)
	object2TagTypesDict = returnObjectsAttributeTypes(object2,userDefined = True)

	#>>> execution stuff
	if object1TagsDict and object2TagsDict:
		#>>> Object 1
		for attr in list(object1TagsDict.keys()):
			"""if it doesn't exist, store  it"""
			if mc.objExists(object1+'.'+attr) and attr in attrsToCopy:
				""" see if it was locked, unlock it and store that it was locked """  
				if mc.getAttr((object1+'.'+attr),lock=True) == True:
					object1LockAttrs[attr] = True

				doDeleteAttr(object1,attr) 
		#Copy object 2's tags to object 1            
		for attr in list(object2TagsDict.keys()):
			if object2TagTypesDict.get(attr) == 'message':
				storeInfo(object1,attr,object2TagsDict.get(attr))
			else:
				storeInfo(object1,attr,object2TagsDict.get(attr),True)

		#>>> Object 2
		for attr in list(object2TagsDict.keys()):
			"""if it doesn't exist, store  it"""
			if mc.objExists(object2+'.'+attr) and attr in attrsToCopy:
				""" see if it was locked, unlock it and store that it was locked """  
				if mc.getAttr((object2+'.'+attr),lock=True) == True:
					object2LockAttrs[attr] = True

				doDeleteAttr(object2,attr) 

		#Copy object 1's tags to object 2                      
		for attr in list(object1TagsDict.keys()):
			if object1TagTypesDict.get(attr) == 'message':
				storeInfo(object2,attr,object1TagsDict.get(attr))
			else:
				storeInfo(object2,attr,object1TagsDict.get(attr),True)

	else:
		log.warning("Selected objects don't have cgmTags to swap")





def doSetOverrideSettings(obj,enabled=True,displayType=1,levelOfDetail = 0,overrideShading=1,overrideTexturing=1,overridePlayback=1,overrideVisible=1):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Sets drawing override settings on an object or it's shapes

	ARGUMENTS:
	obj(string) - the object we'd like to startfrom
	enabled(bool) - whether to enable the override or not
	displayType(int) - (1)
	            Modes - 0 - Normal
	                    1 - Template
	                    2 - Reference

	levelOfDetail(int) -(0)
	            Modes - 0 - Full
	                    1 - Bounding Box
	overrideShading(bool) - (1)
	overrideTexturing(bool) - (1)
	overridePlayback(bool) - (1)
	overrideVisible(bool) - (1)

	RETURNS:
	Nothin
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	shapes = mc.listRelatives(obj,shapes = True)
	if len(shapes) > 0:
		for shape in shapes:
			doSetAttr(shape, 'overrideEnabled', enabled)
			doSetAttr(shape, 'overrideDisplayType', displayType)
			doSetAttr(shape, 'overrideLevelOfDetail', levelOfDetail)
			doSetAttr(shape, 'overrideShading', overrideShading)
			doSetAttr(shape, 'overrideTexturing', overrideTexturing)
			doSetAttr(shape, 'overridePlayback', overridePlayback)
			doSetAttr(shape, 'overrideVisible', overrideVisible)
	else:
		doSetAttr(obj, 'overrideEnabled', enabled)
		doSetAttr(obj, 'overrideDisplayType', displayType)
		doSetAttr(obj, 'overrideLevelOfDetail', levelOfDetail)
		doSetAttr(obj, 'overrideShading', overrideShading)
		doSetAttr(obj, 'overrideTexturing', overrideTexturing)
		doSetAttr(obj, 'overridePlayback', overridePlayback)
		doSetAttr(obj, 'overrideVisible', overrideVisible)

def doToggleTemplateDisplayMode(obj):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Toggles the template disply mode of an object

	ARGUMENTS:
	obj(string) - the object we'd like to startfrom

	RETURNS:
	Nothin
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	shapes = mc.listRelatives(obj,shapes = True)  

	if len(shapes) > 0:
		for shape in shapes:
			currentState = doGetAttr(shape,'template')
			doSetAttr(shape, 'template', not currentState)

	else:
		currentState = doGetAttr(obj,'template')
		doSetAttr(obj,'template', not currentState)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doDeleteAttr(obj,attr):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Deletes and attribute if it exists. Even if it's locked

	ARGUMENTS:
	attr(string) - the attribute to delete

	RETURNS:
	True/False depending if it found anything to destroy
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrBuffer = (obj+'.'+attr)
	if mc.objExists(attrBuffer) and not mc.attributeQuery(attr, node = obj, listParent=True):
		try:
			mc.setAttr(attrBuffer,lock=False)
		except:pass            
		try:
			doBreakConnection(attrBuffer)
		except:pass

		mc.deleteAttr(attrBuffer)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Joint Related
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def setRotationOrderObj (obj, ro):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an object and rotation order (xyz,xzy,etc) into it and it will
	set the object to that rotation order

	ARGUMENTS:
	obj(string) - object
	ro(string) - rotation order 
	                        xyz,yzx,zxy,xzy,yxz,zyx,none

	RETURNS:
	success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	""" pass an object and rotation order (xyz,xzy,etc) into it and it will set the object to that rotation order """
	validRO = True
	rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
	if not ro in rotationOrderDictionary:
		print((ro + ' is not a valid rotation order. Expected one of the following:'))
		print(rotationOrderDictionary)
		validRO = False
	else:  
		correctRo = rotationOrderDictionary[ro]        
		mc.setAttr ((obj+'.rotateOrder'), correctRo)
	return validRO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utility Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doSetLockHideKeyableAttr (obj,lock=True,visible=False,keyable=False,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an oject, True/False for locking it, True/False for visible in
	channel box, and which channels you want locked in ('tx','ty',etc) form

	ARGUMENTS:
	obj(string)
	lock(bool)
	visible(bool)
	keyable(bool)
	channels(list) - (tx,ty,vis,whatever)

	RETURNS:
	None
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	lockOptions = ('tx','ty','tz','rx','ry','rz','sx','sy','sz','v')
	for channel in channels:
		if channel in lockOptions:        
			mc.setAttr ((obj+'.'+channel),lock=lock, keyable=keyable, channelBox=visible)                   
		else:
			print((channel + ' is not a valid option. Skipping.'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Connections Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doBreakConnection(obj,attr=None):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Breaks a connection on an attribute if there is one

	ARGUMENTS:
	obj(string) - 
	attr(string) - the attribute to break the connection on

	RETURNS:
	source buffer or False
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if '.' in obj:
		attrBuffer = returnObjAttrSplit(obj)
		if attrBuffer:
			obj = attrBuffer[0]
			attr = attrBuffer[1]
		else:
			return False

	assert mc.objExists('%s.%s'%(obj,attr)) is True,"'%s.%s' doesn't exist"%(obj,attr)

	attrBuffer = '%s.%s'%(obj,attr)

	family = {}
	source = []

	if (mc.connectionInfo (attrBuffer,isDestination=True)):             
		#Get the driven for a vector connection
		sourceBuffer = mc.listConnections (attrBuffer, scn = False, d = False, s = True, plugs = True)
		if not sourceBuffer:
			#Parent mode
			family = returnAttrFamilyDict(obj,attr)           
			sourceBuffer = mc.connectionInfo (attrBuffer,sourceFromDestination=True)
		else:
			sourceBuffer = sourceBuffer[0]

		if not sourceBuffer:
			return log.warning("No source for '%s.%s' found!"%(obj,attr))
		try:
			log.debug('sourceBuffer: {0}'.format(sourceBuffer))
			drivenAttr = '%s.%s'%(obj,attr)
			if family and family.get('parent'):
				log.debug('family: {0}'.format(family))
				drivenAttr = '%s.%s'%(obj,family.get('parent'))

			log.debug ("Breaking '%s' to '%s'"%(sourceBuffer,drivenAttr))

			#>>>See if stuff is locked
			drivenLock = False
			if mc.getAttr(drivenAttr,lock=True):
				drivenLock = True
				mc.setAttr(drivenAttr,lock=False)
			sourceLock = False    
			if mc.getAttr(sourceBuffer,lock=True):
				sourceLock = True
				mc.setAttr(sourceBuffer,lock=False)

			mc.disconnectAttr (sourceBuffer,drivenAttr)


			if drivenLock:
				mc.setAttr(drivenAttr,lock=True)

			if sourceLock:
				mc.setAttr(sourceBuffer,lock=True)

			return sourceBuffer
		except Exception as err:
			raise Exception("doBreakConnection fail | {0}".format(err))
	else:
		return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnDriverAttribute(attribute,skipConversionNodes = False,longNames = True):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Returns the driverAttribute of an attribute if there is one

	ARGUMENTS:
	attribute(string)

	RETURNS:
	Success - driverAttribute(string)
	Failure - False
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if (mc.connectionInfo (attribute,isDestination=True)) == True:
		sourceBuffer = mc.listConnections (attribute, scn = skipConversionNodes, d = False, s = True, plugs = True)
		if not sourceBuffer:
			sourceBuffer = [mc.connectionInfo (attribute,sourceFromDestination=True)]   
		if sourceBuffer:
			if longNames:		    
				return str(mc.ls(sourceBuffer[0],l=True)[0])#cast to longNames!
			else:
				return str(mc.ls(sourceBuffer[0],shortNames=True)[0])#cast to shortnames!		    
		return False
	return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDriverObject(attribute,skipConversionNodes = False,longNames = True):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Returns the driver of an attribute if there is one

	ARGUMENTS:
	attribute(string)

	RETURNS:
	Success - driverObj(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	objectBuffer =  mc.listConnections (attribute, scn = skipConversionNodes, d = False, s = True, plugs = False)
	if not objectBuffer:
		return False
	if longNames:		    
		return str(mc.ls(objectBuffer[0],l=True)[0])#cast to longNames!
	else:
		return str(mc.ls(objectBuffer[0],shortNames=True)[0])#cast to shortnames!
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDrivenAttribute(attribute,skipConversionNodes = False,longNames = True):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Returns the drivenAttribute of an attribute if there is one

	ARGUMENTS:
	attribute(string)

	RETURNS:
	Success - drivenAttribute(string)
	Failure - False
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	if (mc.connectionInfo (attribute,isSource=True)) == True:
		destinationBuffer = mc.listConnections (attribute, scn = skipConversionNodes, s = False, d = True, plugs = True)
		if not destinationBuffer:
			destinationBuffer = mc.connectionInfo (attribute,destinationFromSource=True) 
		if destinationBuffer:
			returnList = []
			for lnk in destinationBuffer:
				if longNames:		    
					returnList.append(str(mc.ls(lnk,l=True)[0]))#cast to longNames!
				else:
					returnList.append(str(mc.ls(lnk,shortNames=True)[0]))#cast to shortnames!		    
			return returnList
		return False
	return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDrivenObject(attribute,skipConversionNodes = True,longNames = True):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Returns the driven object of an attribute if there is one

	ARGUMENTS:
	attribute(string)

	RETURNS:
	Success - drivenObj(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	objectBuffer =  mc.listConnections (attribute, scn = skipConversionNodes, s = False, d = True, plugs = False)
	if not objectBuffer:
		return False
	if attribute in objectBuffer:
		objectBuffer.remove(attribute)

	returnList = []
	for lnk in objectBuffer:
		if longNames:		    
			returnList.append(str(mc.ls(lnk,l=True)[0]))#cast to longNames!
		else:
			returnList.append(str(mc.ls(lnk,shortNames=True)[0]))#cast to shortnames!	
	return returnList    



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectsAttributeTypes(obj,*a, **kw ):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an object into it with user attributes and it will return a dictionary attribute's data types

	ARGUMENTS:
	obj(string) - obj with attrs
	any arguments for the mc.listAttr command

	RETURNS:
	attrDict(Dictionary) - dictionary in terms of {[attrName : type],[etc][etc]}
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert mc.objExists(obj) is True, "'%s' doesn't exist"%obj
	attrs =(mc.listAttr (obj,*a, **kw ))
	attrDict = {}
	if not attrs == None:   
		for attr in attrs:
			try:
				attrDict[attr] = (mc.getAttr((obj+'.'+attr),type=True))
			except:
				pass
		return attrDict
	else:
		return False

def returnObjectsAttributeByTypeDict(obj,typeCheck = [],*a, **kw ):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an object into it with  it will return a dictionary of attribute names by type keys

	ARGUMENTS:
	obj(string) - obj with attrs
	typeCheck(list) == list of attribute types to look for. default [] will query all
	any arguments for the mc.listAttr command

	RETURNS:
	attrDict(Dictionary) - dictionary in terms of {[type : attr1,attr2],[etc][etc]}
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert mc.objExists(obj) is True, "'%s' doesn't exist"%obj

	attrs =(mc.listAttr (obj,*a, **kw ))
	typeDict = {}    
	if typeCheck:
		for check in typeCheck:
			typeDict[check] = []

	if not attrs == None:   
		for attr in attrs:
			try:               
				typeBuffer = mc.getAttr((obj+'.'+attr),type=True) or None
				if typeCheck:
					if typeBuffer and typeBuffer in list(typeDict.keys()):
						typeDict[typeBuffer].append(attr)
				else:
					if typeBuffer and typeBuffer in list(typeDict.keys()):
						typeDict[typeBuffer].append(attr)
					elif typeBuffer:
						typeDict[typeBuffer] = [attr]                    
			except:
				pass
	if typeDict: 
		for key in list(typeDict.keys()):
			if typeDict.get(key):
				return typeDict
	return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnUserAttributes(obj,*a,**kw):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Returns user created attributes of an object

	ARGUMENTS:
	obj(string) - obj to check

	RETURNS:
	messageList - nested list in terms of [[attrName, target],[etc][etc]]
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	buffer = mc.listAttr(obj,ud=True) or []
	if len(buffer) > 0:
		return buffer
	else:
		return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnMessageObject(storageObject, messageAttr):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Returns the object linked to the message attribute

	ARGUMENTS:
	storageObject(string) - object holding the message attr
	messageAttr(string) - name of the message attr

	RETURNS:
	messageObject(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrBuffer = (storageObject+'.'+messageAttr)
	if mc.objExists(attrBuffer) == True:
		if mc.addAttr(attrBuffer,q=True,m=True):
			log.warning("'%s' is a multi message attr. Use returnMessageData"%attrBuffer)
			return False
		messageObject = (mc.listConnections (attrBuffer))
		if messageObject != None:
			if mc.objExists(messageObject[0]) and not mc.objectType(messageObject[0])=='reference':
				return messageObject[0]
			else:#Try to repair it
				return repairMessageToReferencedTarget(storageObject,messageAttr)
		else:
			return False
	else:
		return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnMessageData(storageObject, messageAttr,longNames=True):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Better message date return

	ARGUMENTS:
	storageObject(string) - object holding the message attr
	messageAttr(string) - name of the message attr

	RETURNS:
	messageObject(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrBuffer = (storageObject+'.'+messageAttr)
	if mc.objExists(attrBuffer) == True:
		msgLinks=mc.listConnections(attrBuffer,destination=True,source=True) #CHANGE : Source=True		
		returnList = []
		if msgLinks:
			for msg in msgLinks:
				if longNames:
					returnList.append(str(mc.ls(msg,l=True)[0]))#cast to longNames!
				else:
					returnList.append(str(mc.ls(msg,shortNames=True)[0]))#cast to shortNames!    
			return returnList 
		else:
			return False
	else:
		return False    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjAttrSplit(attr):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Simple attribute string splitter

	ARGUMENTS:
	attr(string) - obj with message attrs

	RETURNS:
	returnBuffer(list) -- [obj,attr]
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert mc.objExists(attr) is True,"'%s' doesn't exist!"
	returnBuffer = []

	if '.' in list(attr):
		splitBuffer = attr.split('.')
		if len(splitBuffer) >= 2:
			returnBuffer = [splitBuffer[0],'.'.join(splitBuffer[1:])]

		if returnBuffer:
			return returnBuffer
	return False  

def returnMessageObjs(obj):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an object into it with messages, it will return a list of the objects

	ARGUMENTS:
	obj(string) - obj with message attrs

	RETURNS:
	messageObject(string)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	objList = []
	objAttributes =(mc.listAttr (obj, userDefined=True))
	if not objAttributes == None:
		for attr in objAttributes:                    
			messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
			if messageQuery == True:
				query = (mc.listConnections(obj+'.'+attr))
				if not query == None:
					objList.append (query[0])
		return objList
	else:
		return False  
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnMessageAttrs(obj):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an object into it with messages, it will return a nested list in terms of [[attrName, target],[etc][etc]]

	ARGUMENTS:
	obj(string) - obj with message attrs

	RETURNS:
	messageList(Dictionary) - dictionary in terms of {[attrName : target],[etc][etc]}
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	messageList = {}
	objAttributes =(mc.listAttr (obj, userDefined=True))
	if not objAttributes == None:
		for attr in objAttributes:                    
			messageBuffer = []
			messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
			if messageQuery == True:
				query = (mc.listConnections(obj+'.'+attr))
				if not query == None:
					messageList[attr] = (query[0])
		return messageList
	else:
		return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def repairMessageToReferencedTarget(obj,attr):
	"""
	To be repairable, there must have been a message connection both directions.

	Assertions - 
	1) Target Attribute must be a message attribute
	2) Target is connected to a reference node

	Returns -
	Success(bool)

	"""
	targetAttr = "%s.%s"%(obj,attr)
	assert mc.attributeQuery (attr,node=obj,msg=True), "'%s' isn't a message attribute. Aborted"%targetAttr

	objTest = mc.listConnections(targetAttr, p=1)
	assert mc.objectType(objTest[0]) == 'reference',"'%s' isn't returning a reference. Aborted"%targetAttr 

	ref = objTest[0].split('RN.')[0] #Get to the ref
	log.info("Reference connection found, attempting to fix...")

	messageConnectionsOut =  mc.listConnections("%s.message"%(obj), p=1)
	if messageConnectionsOut and ref:
		for plug in messageConnectionsOut:
			if ref in plug:
				log.info("Checking '%s'"%plug)                
				matchObj = plug.split('.')[0]#Just get to the object
				doConnectAttr("%s.message"%matchObj,targetAttr)
				log.info("'%s' restored to '%s'"%(targetAttr,matchObj))

				if len(messageConnectionsOut)>1:#fix to first, report other possibles
					log.warning("Found more than one possible connection. Candidates are:'%s'"%"','".join(messageConnectionsOut))
					return False
				return matchObj
	log.warning("No message connections and reference found")
	return False

def returnMessageAttrsAsList(obj):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an object into it with messages, it will return a nested list in terms of [[attrName, target],[etc][etc]]

	ARGUMENTS:
	obj(string) - obj with message attrs

	RETURNS:
	messageList - nested list in terms of [[attrName, target],[etc][etc]]
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	messageList = []
	objAttributes =(mc.listAttr (obj, userDefined=True))
	if not objAttributes == None:
		for attr in objAttributes:                    
			messageBuffer = []
			messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
			if messageQuery == True:
				query = (mc.listConnections(obj+'.'+attr))
				if not query == None:
					messageBuffer.append (attr)
					messageBuffer.append (query[0])
					messageList.append (messageBuffer)
		return messageList
	else:
		return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnUserAttrsToDict(obj):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an object into it with user attributes and it will return a dictionary of the data back

	ARGUMENTS:
	obj(string) - obj with attrs

	RETURNS:
	attrDict(Dictionary) - dictionary in terms of {[attrName : target],[etc][etc]}
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrDict = {}
	objAttributes =(mc.listAttr (obj, userDefined=True)) or []
	attrTypes = returnObjectsAttributeTypes(obj,userDefined = True)

	if objAttributes:
		for attr in objAttributes:                    
			messageBuffer = []
			messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
			attrType = attrTypes.get(attr)
			if messageQuery == True:
				query = returnMessageData(obj,attr)
				attrDict[attr] = (query)
			elif attrType == 'double3':
				childrenAttrs = mc.attributeQuery(attr, node =obj, listChildren = True)
				dataBuffer = []
				for childAttr in childrenAttrs:
					dataBuffer.append(mc.getAttr(obj+'.'+childAttr))
				attrDict[attr] = dataBuffer
			elif attrType == 'double':
				parentAttr = mc.attributeQuery(attr, node =obj, listParent = True)
				if parentAttr:
					if parentAttr[0] not in objAttributes:
						attrDict[attr] = (mc.getAttr((obj+'.'+attr)))
					else:
						attrDict[attr] = (mc.getAttr((obj+'.'+attr)))                    
				else:
					attrDict[attr] = (mc.getAttr((obj+'.'+attr)))                    
			else:
				if attrType != 'attributeAlias':
					buffer = mc.getAttr(obj+'.'+attr)
					if buffer is not None:
						attrDict[attr] = (buffer)

		return attrDict
	else:
		return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnUserAttrsToList(obj):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Pass an object into it with user attributes and it will return a dictionary of the data back

	ARGUMENTS:
	obj(string) - obj with attrs

	RETURNS:
	attrsList(list) - nested list in terms of [[attrName : target],[etc][etc]]
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	returnList = []
	bufferDict = returnUserAttrsToDict(obj)
	if bufferDict:
		for key in list(bufferDict.keys()):
			buffer = []
			buffer.append(key)
			buffer.append(bufferDict.get(key))
			returnList.append(buffer)
		return returnList
	return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Creation Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addRotateOrderAttr (obj,name):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Add a rotate order attr

	ARGUMENTS:
	obj(string) - object to add attributes to
	attrList(list) - list of attributes to add

	RETURNS:
	NA
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	try:
		mc.addAttr(obj, ln=name, at = 'enum',en = 'xyz:yzx:zxy:xzy:yxz:zyx')
		mc.setAttr((obj+'.'+name),e = True, keyable = True )
		return ("%s.%s"%(obj,name))
	except Exception as error:
		log.error("addRotateOrderAttr>>Failure! '%s' failed to add '%s'"%(obj,name))
		raise Exception(error)       

def addPickAxisAttr(obj,name):
	""" 
	Add an axis picker attr

	ARGUMENTS:
	obj(string) - object to add attributes to
	name(string) - name of the attr to make
	"""
	try:
		mc.addAttr(obj, ln=name, at = 'enum',en = 'x+:y+:z+:x-:y-:z-')
		mc.setAttr((obj+'.'+name),e = True, keyable = True )
		return ("%s.%s"%(obj,name))
	except:
		log.warning("'%s' failed to add '%s'"%(obj,name))

def addAttributesToObj (obj, attributeTypesDict):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Takes an list of string variables to add to an object as string
	attributes. Skips it if it exists.

	ARGUMENTS:
	obj(string) - object to add attributes to
	attrList(list) - list of attributes to add

	RETURNS:
	NA
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	"""sort the keys"""
	sortedAttributes = dictionary.returnDictionarySortedToList(attributeTypesDict,True)

	""" make em"""
	for set in sortedAttributes:
		attr = set[0]
		attrType = set[1]
		attrCache = (obj+'.'+attr)
		if not mc.objExists (attrCache):
			if attrType == 'string':
				mc.addAttr (obj, ln = attr,  dt =attrType )
			elif attrType == 'double3':
				mc.addAttr (obj, ln=attr, at= 'double3')
				mc.addAttr (obj, ln=(attr+'X'),p=attr , at= 'double')
				mc.addAttr (obj, ln=(attr+'Y'),p=attr , at= 'double')
				mc.addAttr (obj, ln=(attr+'Z'),p=attr , at= 'double')
			else:
				mc.addAttr (obj, ln = attr,  at =attrType )

		else:
			print(('"' + attrCache + '" exists, moving on'))


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addStringAttributeToObj (obj,attr,*a, **kw ):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a string attribute to an object, passing forward commands


	ARGUMENTS:
	obj(string)
	attr(string)

	RETURNS:
	Success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""    
	assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

	try: 
		mc.addAttr (obj, ln = attr, dt = 'string',*a, **kw)
		return ("%s.%s"%(obj,attr))
	except:
		log.warning("'%s' failed to add '%s'"%(obj,attr))
		return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addIntegerAttributeToObj (obj,attr,*a, **kw ):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a integer attribute to an object, passing forward commands


	ARGUMENTS:
	obj(string)
	attr(string)

	RETURNS:
	Success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""   
	assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

	try: 
		mc.addAttr (obj, ln = attr, at = 'long',*a, **kw)
		return ("%s.%s"%(obj,attr))
	except:
		log.warning("'%s' failed to add '%s'"%(obj,attr))
		return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addMessageAttributeToObj (obj,attr,*a, **kw ):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a integer attribute to an object, passing forward commands


	ARGUMENTS:
	obj(string)
	attr(string)

	RETURNS:
	Success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""    
	assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

	try: 
		mc.addAttr (obj, ln = attr, at = 'message',*a, **kw )
		return ("%s.%s"%(obj,attr))
	except:
		log.warning("'%s' failed to add '%s'"%(obj,attr))
		return False   
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addVectorAttributeToObj (obj,attr,*a, **kw):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a vector attribute to an object, passing forward commands

	ARGUMENTS:
	obj(string)
	attr(string)

	RETURNS:
	Success(bool)
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""    
	try: 
		mc.addAttr (obj, ln=attr, at= 'double3',*a, **kw)
		mc.addAttr (obj, ln=(attr+'X'),p=attr , at= 'double',*a, **kw)
		mc.addAttr (obj, ln=(attr+'Y'),p=attr , at= 'double',*a, **kw)
		mc.addAttr (obj, ln=(attr+'Z'),p=attr , at= 'double',*a, **kw)       
		return ("%s.%s"%(obj,attr))

	except:
		log.warning("'%s' failed to add '%s'"%(obj,attr))
		return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addStringAttributesToObj (obj, attrList):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Takes an list of string variables to add to an object as string attributes. Skips it if it exists.
	Input -obj, attrList(list).

	ARGUMENTS:
	obj(string) - object to add attributes to
	attrList(list) - list of attributes to add

	RETURNS:
	NA
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	for attr in attrList:        
		attrCache = (obj+'.'+attr)
		if not mc.objExists (attrCache):
			mc.addAttr (obj, ln = attr,  dt = 'string')
			return ("%s.%s"%(obj,attr))            
		else:
			print(('"' + attrCache + '" exists, moving on'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addFloatAttributeToObject (obj, attr,*a, **kw):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a float attribute to an object

	ARGUMENTS:
	obj(string) - object to add attribute to
	attr(string) - attribute name to add
	minValue(int/float) - minimum value
	maxValue(int/float) - maximum value
	default(int/float) - default value

	RETURNS:
	Attribute full name (string) - ex obj.attribute
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

	try: 
		mc.addAttr (obj, ln = attr, at = 'float',*a, **kw)
		return ("%s.%s"%(obj,attr))
	except Exception as error:
		log.error("addFloatAttributeToObject>>Failure! '%s' failed to add '%s'"%(obj,attr))
		raise Exception(error)  
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addEnumAttrToObj (obj,attr,optionList=['off','on'],*a, **kw):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a enum attribute to an object

	ARGUMENTS:
	obj(string) - object to add attribute to
	attrName(list)
	optionList(list)
	default(int/float) - default value

	RETURNS:
	Attribute full name (string) - ex obj.attribute
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

	try: 
		mc.addAttr (obj,ln = attr, at = 'enum', en=('%s' %(':'.join(optionList))),*a, **kw)
		mc.setAttr ((obj+'.'+attr),e=True,keyable=True)
		return ("%s.%s"%(obj,attr))
	except:
		log.warning("'%s' failed to add '%s'"%(obj,attr))
		return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addFloatAttrsToObj (obj,attrList, *a, **kw):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a float attribute to an object

	ARGUMENTS:
	obj(string) - object to add attribute to
	attrList(list) - attribute name to add
	minValue(int/float) - minimum value
	maxValue(int/float) - maximum value
	default(int/float) - default value

	RETURNS:
	Attribute full name (string) - ex obj.attribute
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrsCache=[]
	for attr in attrList:
		attrCache = addFloatAttributeToObject (obj, attr, *a, **kw)
		attrsCache.append(attrCache)
	return attrsCache
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addBoolAttrToObject(obj, attr, *a, **kw):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a section break for an attribute list

	ARGUMENTS:
	obj(string) - object to add attribute to
	attr(string) - name for the section break

	RETURNS:
	Success
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

	try: 
		mc.addAttr (obj, ln = attr,  at = 'bool',*a, **kw)
		mc.setAttr ((obj+'.'+attr), edit = True, channelBox = True)

		return True
	except:
		log.warning("'%s' failed to add '%s'"%(obj,attr))
		return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addSectionBreakAttrToObj(obj, attr):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds a section break for an attribute list

	ARGUMENTS:
	obj(string) - object to add attribute to
	attr(string) - name for the section break

	RETURNS:
	Nothing
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrCache = (obj+'.'+attr)
	if not mc.objExists (attrCache):
		mc.addAttr (obj, ln = attr,  at = 'bool')
		mc.setAttr (attrCache, lock = True, channelBox = True)
	else:
		print(('"' + attrCache + '" exists, moving on'))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Message Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def storeObjNameToMessage (obj, storageObj):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds the obj name as a message attribute to the storage object

	ARGUMENTS:
	obj(string) - object to store
	storageObject(string) - object to store the info to

	RETURNS:
	Nothing
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	attrCache = ('%s%s%s' % (storageObj,'.',obj))
	if  mc.objExists (attrCache):  
		print((attrCache+' already exists'))
	else:
		mc.addAttr (storageObj, ln=obj, at= 'message')
		mc.connectAttr ((obj+".message"),(storageObj+'.'+ obj))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def storeObjectToMessage (obj, storageObj, messageName):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds the obj name as a message attribute to the storage object with
	a custom message attribute name

	ARGUMENTS:
	obj(string) - object to store
	storageObject(string) - object to store the info to
	messageName(string) - message name to store it as

	RETURNS:
	Success
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert mc.objExists(obj) is True,"'%s' doesn't exist"%(obj)
	assert mc.objExists(storageObj) is True,"'%s' doesn't exist"%(storageObj)

	attrCache = (storageObj+'.'+messageName)
	objLong = mc.ls(obj,long=True)
	if len(objLong)>1:
		log.warning("Can't find long name for storage, found '%s'"%objLong)
		return False 
	objLong = objLong[0]

	storageLong = mc.ls(storageObj,long=True)
	if len(storageLong)>1:
		log.warning("Can't find long name for storage, found '%s'"%storageLong)
		return False
	storageLong = storageLong[0]

	try:
		if  mc.objExists (attrCache):
			if mc.attributeQuery (messageName,node=storageObj,msg=True) and not mc.addAttr(attrCache,q=True,m=True):
				if returnMessageObject(storageObj,messageName) != obj:
					log.debug(attrCache+' already exists. Adding to existing message node.')
					doBreakConnection(attrCache)
					#mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),force=True)
					doConnectAttr((obj+".message"),(storageObj+'.'+ messageName))
					return True 
				else:
					log.debug("'%s' already stored to '%s.%s'"%(obj,storageObj,messageName))
			else:
				connections = returnDrivenAttribute(attrCache)
				if connections:
					for c in connections:
						doBreakConnection(c)

				log.debug("'%s' already exists. Not a message attr, converting."%attrCache)
				doDeleteAttr(storageObj,messageName)

				buffer = mc.addAttr (storageObj, ln=messageName, at= 'message')                
				#mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),force=True)
				doConnectAttr((obj+".message"),(storageObj+'.'+ messageName))                

				return True
		else:
			mc.addAttr (storageObj, ln=messageName, at= 'message')
			#mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName))
			doConnectAttr((obj+".message"),(storageObj+'.'+ messageName))	    
			return True
	except Exception as error:
		log.warning(error)
		return False

def storeObjectsToMessage (objects, storageObj, messageName):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds the obj name as a mulit message attribute to the storage object with
	a custom message attribute name. Reminder - multi message attrs are invisible

	ARGUMENTS:
	objects(list) - object to store
	storageObject(string) - object to store the info to
	messageName(string) - message name to store it as

	RETURNS:
	Success
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	for obj in objects:
		assert mc.objExists(obj) is True,"'%s' doesn't exist"%(obj)
	assert mc.objExists(storageObj) is True,"'%s' doesn't exist"%(storageObj)
	attrCache = (storageObj+'.'+messageName)
	objects = lists.returnListNoDuplicates(objects)
	try:
		if mc.objExists (attrCache):
			log.debug(attrCache+' already exists. Adding to existing message node.')                
			doDeleteAttr(storageObj,messageName)
			mc.addAttr (storageObj, ln=messageName, at= 'message',m=True,im=False) 
			for obj in objects:
				mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),nextAvailable=True)
			mc.setAttr(attrCache,lock=True)
			return True                       
		else:
			mc.addAttr(storageObj, ln=messageName, at= 'message',m=True,im=False) 
			for obj in objects:
				mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),nextAvailable=True)
			mc.setAttr(attrCache,lock=True)
			return True 
	except:
		log.error("Storing '%s' to '%s.%s' failed!"%(objects,storageObj,messageName))
		return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def storeObjListNameToMessage (objList, storageObj):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	DESCRIPTION:
	Adds the obj names as  message attributes to the storage object

	ARGUMENTS:
	objList(string) - object to store
	storageObj(string) - object to store the info to

	RETURNS:
	Nothing
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	for obj in objList:
		storeObjNameToMessage (obj, storageObj)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def queryIfMessage(obj,attr):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	log.warning('!'*50)
	log.warning("Please get rid of 'attributes.queryIfMessage' in your code")
	log.warning('!'*50)    
	if mc.objExists(obj+'.'+attr) != False:
		try:
			messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
			if messageQuery == True:
				return True
		except:
			return False
	else:
		return False



def reorderAttributes(obj,attrs,direction = 0):
	""" 
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	Acknowledgement:
	Thank you to - http://www.the-area.com/forum/autodesk-maya/mel/how-can-we-reorder-an-attribute-in-the-channel-box/

	DESCRIPTION:
	Reorders attributes on an object

	ARGUMENTS:
	obj(string) - obj with message attrs
	attrs(list) must be attributes on the object
	direction(int) - 0 is is negative (up on the channelbox), 1 is positive (up on the channelbox)

	RETURNS:
	>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	"""
	assert direction in [0,1],"Direction must be 0 for negative, or 1 for positive movement"
	for attr in attrs:
		assert mc.objExists(obj+'.'+attr) is True, "reorderAttributes error. '%s.%s' doesn't exist. Swing and a miss..."%(obj,atr)

	userAttrs = mc.listAttr(obj,userDefined = True)

	attrsToMove = []
	for attr in userAttrs:
		if not mc.attributeQuery(attr, node = obj,listParent = True):
			attrsToMove.append(attr)

	lists.reorderListInPlace(attrsToMove,attrs,direction)

	#To reorder, we need delete and undo in the order we want
	for attr in attrsToMove:
		try:
			attrBuffer = '%s.%s'%(obj,attr)
			lockState = False
			if mc.getAttr(attrBuffer,lock=True) == True:
				lockState = True
				mc.setAttr(attrBuffer,lock=False)

			mc.deleteAttr('%s.%s'%(obj,attr))

			mc.undo()

			if lockState:
				mc.setAttr(attrBuffer,lock=True)

		except:
			log.warning("'%s' Failed to reorder"%attr)

