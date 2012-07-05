#=================================================================================================================================================
#=================================================================================================================================================
#	namingToolsLib - a part of cgmTools
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
__version__ = '0.1.03182012'

import maya.cmds as mc
import maya.mel as mel
from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.classes import NameFactory

from cgm.lib import *
from cgm.lib import (guiFactory,
                     dictionary,
                     search)
reload(NameFactory)
reload(search)
reload(dictionary)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# UI Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiUpdateAutoNamePreview(self):
	autoNameObject = mc.textField(self.AutoNameObjectField,q=True,text = True)
	if autoNameObject:
		newName = NameFactory.returnUniqueGeneratedName(autoNameObject,True)
		self.GeneratedNameField(e = True,label = ("Preview : '" + newName + "'"))
	else:
		self.GeneratedNameField(e = True,label = ('Name will preview here...'))
		

def uiNameLoadedAutoNameObject(self):
	autoNameObject = mc.textField(self.AutoNameObjectField,q=True,text = True)
	if autoNameObject:
		newName = NameFactory.doNameObject(autoNameObject,True)
		mc.textField(self.AutoNameObjectField,e = True,text = newName)
	else:
		guiFactory.warning('No current autoname object loaded!')
		
def uiNameLoadedAutoNameObjectChildren(self):
	autoNameObject = mc.textField(self.AutoNameObjectField,q=True,text = True)
	if autoNameObject:
		newNameList = NameFactory.doRenameHeir(autoNameObject,True)
		mc.textField(self.AutoNameObjectField,e = True,text = newNameList[0])

	else:
		guiFactory.warning('No current autoname object loaded!')
def uiLoadParentNameObject(self,parentNameObject):
	assert mc.objExists(parentNameObject) is True,"'%s' doesn't exist" % parentNameObject
	mc.select(cl=True)
	mc.select(parentNameObject)
	uiLoadAutoNameObject(self)

def uiLoadAutoNameObject(self):
	selected = []
	bufferList = []
	selected = (mc.ls (sl=True,flatten=True,shortNames=True))
	
	fieldToKeyDict = {'cgmName':self.NameTagField,
                      'cgmType':self.ObjectTypeTagField,
                      'cgmNameModifier':self.NameModifierTagField,
                      'cgmTypeModifier':self.ObjectTypeModifierTagField,
                      'cgmDirectionModifier':self.DirectionModifierTagField,
                      'cgmDirection':self.DirectionTagField,
                      'cgmPosition':self.PositionTagField,
	                  'cgmIterator':self.IteratorTagField}
	
	if selected:
		if len(selected) >= 2:
			guiFactory.warning('Only one object can be loaded')
		else:
			# Put the object in the field
			guiFactory.doLoadSingleObjectToTextField(self.AutoNameObjectField,'cgmVar_AutoNameObject')

			#Get the tag info for the object
			tagsDict = NameFactory.returnObjectGeneratedNameDict(selected[0])
			userAttrs = attributes.returnUserAttributes(selected[0])
			cgmAttrs = NameFactory.returnCGMOrder()
			usedAttrs = lists.returnMatchList(userAttrs,cgmAttrs)
			tagAttrs = tagsDict.keys()
			#Enable the tag fields
			for key in fieldToKeyDict.keys():
				mc.textField(fieldToKeyDict.get(key),edit=True,enable=True,
				             text = '',
				              bgc = dictionary.returnStateColor('normal'))
			
			for key in tagsDict.keys():
				currentField = fieldToKeyDict.get(key)

				
				buildSelectPopUp = {}
				buildLoadPopUp = {}
				#purge popup
				popUpBuffer =  currentField(q=True, popupMenuArray = True)
				if popUpBuffer:
					for item in popUpBuffer:
						mc.deleteUI (item)
				
				mc.textField(currentField,edit=True,text = tagsDict.get(key),
				             bgc = dictionary.returnStateColor('keyed'))
				
				# Set special color cases, if it's guessed or gotten upstream....
				if usedAttrs:
					if key not in usedAttrs:
						mc.textField(currentField,edit = True, bgc = dictionary.returnStateColor('reserved'))
					# if it's connected	
					elif (mc.connectionInfo ((selected[0]+'.'+key),isDestination=True)):
						driverObject = attributes.returnDriverObject(selected[0]+'.'+key)
						driverAttr = attributes.returnDriverAttribute(selected[0]+'.'+key)
						mc.textField(currentField,edit = True,
						             text = (driverAttr),
						             bgc = dictionary.returnStateColor('connected'))
						buildSelectPopUp['Select driver object'] = (driverObject)
						buildLoadPopUp['Load driver object'] = (driverObject)


				else:
					#Got it from a parent
					parentNameObjectRaw = search.returnTagUp(selected[0],key)
					if parentNameObjectRaw:
						if '|' in parentNameObjectRaw[1]:
							parentNameBuffer = parentNameObjectRaw[1].split('|')
							parentNameObject = parentNameBuffer[-1]
						else:
							parentNameObject = parentNameObjectRaw[1]
						mc.textField(currentField,edit = True,
					                 enable=True,
					                 text = parentNameObject,
					                 bgc = dictionary.returnStateColor('semiLocked'))
						buildSelectPopUp['Select parent name object'] = (parentNameObjectRaw[1])
						buildLoadPopUp['Load parent name object'] = (parentNameObjectRaw[1])
					else:
						mc.textField(currentField,edit = True,
					                 bgc = dictionary.returnStateColor('reserved'))
							
				if buildSelectPopUp or buildLoadPopUp:
					buffer = MelPopupMenu(currentField,button = 3)
				if buildSelectPopUp:		
					for key in buildSelectPopUp.keys():
						MelMenuItem(buffer ,
							        label = key,
							        c = ('%s%s%s' %("mc.select('",buildSelectPopUp.get(key),"')")))
				if buildLoadPopUp:		
					for key in buildLoadPopUp.keys():
						MelMenuItem(buffer ,
					                label = key,
					                c = lambda *a:uiLoadParentNameObject(self,buildLoadPopUp.get(key)))
						
						
			# if it's connected
			uiUpdateAutoNamePreview(self)
			
	else:
		#clear the field
		guiFactory.doLoadSingleObjectToTextField(self.AutoNameObjectField,'cgmVar_AutoNameObject')
		# update the fields
		for key in fieldToKeyDict.keys():
			mc.textField(fieldToKeyDict.get(key),edit=True,enable=False,
		                 text = '',
			             bgc = dictionary.returnStateColor('normal'))
			
		# Fix previewer
		uiUpdateAutoNamePreview(self)
		
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Tagging Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiClearTags(self):
	selected = mc.ls(sl=True)
	mc.select(cl=True)
	
	tagToKeyDict = {'Name':'cgmName',
                      'Type':'cgmType',
                      'NameModifier':'cgmNameModifier',
                      'TypeModifier':'cgmTypeModifier',
                      'DirectionModifier':'cgmDirectionModifier',
                      'Direction':'cgmDirection',
                      'Position':'cgmPosition',
	                  'Iterator':'cgmIterator'}
	
	tagShortHand = self.cgmMultiTagOptions(q=True,value = True)
	tagToUse = tagToKeyDict.get(tagShortHand)
	if tagToUse:
		success = []
		for obj in selected:
			try:
				attributes.doDeleteAttr(obj,tagToUse)
				success.append(obj)
			except:
				guiFactory.warning('%s failed to recieve info!' %obj)
		if success:		
			guiFactory.warning('%s%s%s%s' %("purged '", tagToUse, "' from ", ','.join(success)))

		else:
			guiFactory.warning('No info found to purge')
	else:
		guiFactory.warning('No tag info found to purge')

def uiCopyTags(self):
	selected = mc.ls(sl=True)
	if len(selected) >= 2:
		for obj in selected[1:]:
			print obj
			attributes.copyNameTagAttrs(selected[0],obj)
	else:
		guiFactory.warning('Need at least two objects.')
	
def uiSwapTags(self):
	selected = mc.ls(sl=True)
	if len(selected) == 2:
		attributes.swapNameTagAttrs(selected[0],selected[1])
	else:
		guiFactory.warning('Two and only two objects selected please.')	
	

def uiMultiTagObjects(self):
	selected = mc.ls(sl=True)
	mc.select(cl=True)
	
	
	tagToKeyDict = {'Name':'cgmName',
                      'Type':'cgmType',
                      'NameModifier':'cgmNameModifier',
                      'TypeModifier':'cgmTypeModifier',
                      'DirectionModifier':'cgmDirectionModifier',
                      'Direction':'cgmDirection',
                      'Position':'cgmPosition',
	                  'Iterator':'cgmIterator'}
	
	tagShortHand = self.cgmMultiTagOptions(q=True,value = True)
	tagToUse = tagToKeyDict.get(tagShortHand)
	infoToStore = self.multiTagInfoField (q=True, text = True)
	if tagToUse:
		if infoToStore:
			success = []
			for obj in selected:
				try:
					attributes.storeInfo(obj,tagToUse, infoToStore,True)
					success.append(obj)
				except:
					guiFactory.warning('%s failed to recieve info!' %obj)
			if success:		
				guiFactory.warning('%s%s%s%s' %("Stored '", infoToStore, "' to ", ','.join(success)))

		else:
			guiFactory.warning('No info found to store')
	else:
		guiFactory.warning('No tag info found to store')
	

	
def uiUpdateAutoNameTag(self,tag):
	fieldToKeyDict = {'cgmName':self.NameTagField,
                      'cgmType':self.ObjectTypeTagField,
                      'cgmNameModifier':self.NameModifierTagField,
                      'cgmTypeModifier':self.ObjectTypeModifierTagField,
                      'cgmDirectionModifier':self.DirectionModifierTagField,
                      'cgmDirection':self.DirectionTagField,
                      'cgmPosition':self.PositionTagField,
	                  'cgmIterator':self.IteratorTagField}
	
	autoNameObject = mc.textField(self.AutoNameObjectField,q=True,text = True)
	#>>> See if our object exists
	if not mc.objExists(autoNameObject):
		guiFactory.warning("'%s' doesn't seem to exist. It may have been renamed or delete. Load a new object please" %autoNameObject)
		return
	
	tagField = fieldToKeyDict.get(tag)
	if autoNameObject:
		infoToStore = mc.textField(tagField, q = True, text = True)
		if infoToStore:
			attributes.storeInfo(autoNameObject,tag, infoToStore,True)
			guiFactory.setBGColorState(tagField,'keyed')
						
			guiFactory.warning("Stored '%s' to object" %infoToStore)
			
			
		else:
			attributes.doDeleteAttr(autoNameObject,tag)
			guiFactory.setBGColorState(tagField,'normal')
			guiFactory.warning('%s purged' %tag)
			
			#refresh load to guess
			mc.select(autoNameObject)
			uiLoadAutoNameObject(self)
			
	else:
		guiFactory.setBGColorState(tagField,'normal')
		guiFactory.warning('You must select something.')
	
	uiUpdateAutoNamePreview(self)
	
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Naming functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiGetObjectInfo(self):
	selected = mc.ls(sl=True,long=True)
	from cgm.lib.classes import NameFactory
	reload(NameFactory)
	
	for obj in selected:
		obj = NameFactory.NameFactory(obj)
		obj.reportInfo()
			
		
def uiReturnIterator(self):
	selected = mc.ls(sl=True)
	from cgm.lib.classes import NameFactory
	reload(NameFactory)
	
	for obj in selected:
		print (NameFactory.returnIterateNumber(obj))
			
def uiReturnFastName(self):
	selected = mc.ls(sl=True)
	from cgm.lib.classes import NameFactory
	reload(NameFactory)
	
	for obj in selected:
		print (NameFactory.returnObjectGeneratedNameDict(obj))
			
def uiReturnSceneUniqueName(self):
	selected = mc.ls(sl=True)
	from cgm.lib.classes import NameFactory
	reload(NameFactory)
	
	for obj in selected:
		print (NameFactory.returnUniqueGeneratedName(obj,True))
			
def uiNameObject(self,sceneUnique):
	selected = mc.ls(sl=True,flatten=True,long=True)
	newNames = []
	
	if not selected:
		guiFactory.warning('Must have something selected')
		return
		
	elif len(selected) > 1:
		tmpGroup = mc.group(em=True)
		cnt = 1
		
		for o in selected:
			attributes.storeInfo(tmpGroup,('name'+str(cnt)),o)
			cnt += 1
		toNameAttrs = attributes.returnUserAttributes(tmpGroup)
		
		mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(toNameAttrs),'Naming...')
		for attr in toNameAttrs:
			if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
				break

			objectToName = (attributes.returnMessageObject(tmpGroup,attr))
			mc.progressBar(mayaMainProgressBar, edit=True, status = ("Naming '%s'"%objectToName), step=1)

			try:
				buffer =  NameFactory.doNameObject( objectToName,sceneUnique )
			except:
				guiFactory.warning("'%s' failed"%objectToName)


			if buffer:
				newNames.append(buffer)
				
		guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
		mc.delete(tmpGroup)
		
		
	else:
		NameFactory.doNameObject(selected[0],sceneUnique)
	
	if newNames:
		print ("The following were named: %s" %','.join(newNames))
		
	

def doUpdateObjectName(self):
	selected = mc.ls(sl=True)
	
	for obj in selected:
		try:
			NameFactory.doUpdateName(obj)
		except:
			guiFactory.warning('Error on naming attempt')
			
def doNameHeirarchy(self,sceneUnique=False,fastIterate=True):
	selected = mc.ls(sl=True)
	
	if not selected:
		guiFactory.warning('Must have something selected')
		return
	
	for obj in selected:
		try:
			NameFactory.doRenameHeir(obj,sceneUnique,fastIterate)
		except:
			guiFactory.warning('Error on naming attempt')		
		



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Hame Heirarchy Nav
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiAutoNameWalkUp(self):
	autoNameObject = mc.textField(self.AutoNameObjectField,q=True,text = True)
	if autoNameObject:
		parent = search.returnParentObject(autoNameObject,False)
		if parent:
			mc.textField(self.AutoNameObjectField,e=True,text = parent)
			mc.select(parent)
			uiUpdateAutoNamePreview(self)
			uiLoadAutoNameObject(self)
		else:
			guiFactory.warning('No parent found!')
	else:
		guiFactory.warning('No current autoname object loaded!')
		
def uiAutoNameWalkDown(self):
	autoNameObject = mc.textField(self.AutoNameObjectField,q=True,text = True)
	if autoNameObject:
		children = search.returnChildrenObjects(autoNameObject)
		print children
		if children:
			mc.textField(self.AutoNameObjectField,e=True,text = children[0])
			mc.select(children[0])
			uiUpdateAutoNamePreview(self)
			uiLoadAutoNameObject(self)
		else:
			guiFactory.warning('No children found!')
	else:
		guiFactory.warning('No current autoname object loaded!')