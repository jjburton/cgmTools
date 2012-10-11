#=================================================================================================================================================
#=================================================================================================================================================
#	attrToolsLib - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Library of functions for the attributeTool
#
# ARGUMENTS:
#   Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
#=================================================================================================================================================
__version__ = '0.1.07022012'

import maya.cmds as mc
import maya.mel as mel
from cgm.lib.classes import NameFactory
from cgm.lib.classes import AttrFactory
from cgm.lib.classes import ObjectFactory
reload(AttrFactory)
reload(ObjectFactory)

from cgm.lib.classes.AttrFactory import *
from cgm.lib.classes.ObjectFactory import *
from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.lib import (guiFactory,
                     dictionary,
                     attributes,
                     search)
reload(attributes)
reload(search)
reload(dictionary)
reload(guiFactory)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Info processing
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiToggleOptionCB(self,optionVar):
    """ 
    Toggles hide mode
    """ 
    optionVar.toggle()
    uiUpdateSourceObjectData(self)


def uiTransferAttributes(self):
    """ 
    Update the loaded source object cata from the optionVar
    """     
    attrs = self.ManageAttrList.getSelectedItems()
    targets = search.returnSelected()
    guiFactory.report("Source object is '%s'"%self.SourceObject.nameShort)

    if not self.SourceObject:
	return guiFactory.warning("No source")
    if not attrs:
	guiFactory.warning("No selected attrs.Doing all loaded!")
	attrs = self.loadAttrs
    if not targets:
	return guiFactory.warning("No selected targets")

    if attrs and self.SourceObject and targets:
	for a in attrs:
	    aInstance = AttrFactory(self.SourceObject.nameLong,a)	    
	    if self.CopyAttrModeOptionVar.value == 0:
		#Connect mode
		for target in targets:
		    aInstance.doConnectOut(target)
	    elif self.CopyAttrModeOptionVar.value == 1:
		#Copy mode
		print 'Copy Mode'
		for target in targets:
		    aInstance.doCopyTo(target,
		                       convertToMatch = self.TransferConvertStateOptionVar.value,
		                       copyAttrSettings = self.CopyAttrOptionsOptionVar.value, 		                       
		                       values = self.TransferValueOptionVar.value,
		                       incomingConnections = self.TransferIncomingOptionVar.value,
		                       outgoingConnections = self.TransferOutgoingOptionVar.value,
		                       keepSourceConnections = self.TransferKeepSourceOptionVar.value,
		                       connectSourceToTarget = self.TransferDriveSourceStateOptionVar.value,
		                       )

	    elif self.CopyAttrModeOptionVar.value == 2:
		if aInstance.dynamic:
		    #Transfer
		    guiFactory.report("On target '%s'"%targets[0])
		    aInstance.doTransferTo(targets[0])
		    if len(targets) > 1:
			guiFactory.warning("Only one target allowed in this mode.Ignorming -'%s'"%("','".join(targets[1:])))
		else:
		    guiFactory.warning("'%s' isn't dynamic. Can't transfer"%(aInstance.nameCombined))
		    

			
    uiUpdateSourceObjectData(self)
    uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu)

    for a in attrs:
	try:
	    self.ManageAttrList.selectItems(attrs)
	except:
	    pass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Info processing
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def updateLoadAttrs(self):
    self.loadAttrs = []

    if self.SourceObject and self.SourceObject.update(self.SourceObject.nameLong):
	if self.HideNonstandardOptionVar.value:
	    self.loadAttrs.extend(self.SourceObject.transformAttrs)
	    self.loadAttrs.extend(self.SourceObject.userAttrs)
	    self.loadAttrs.extend(self.SourceObject.keyableAttrs)
	    
	    self.loadAttrs = lists.returnListNoDuplicates(self.loadAttrs)
	else:
	    self.loadAttrs.extend( mc.listAttr(self.SourceObject.nameLong) )
	
	if self.HideTransformsOptionVar.value:
	    for a in self.SourceObject.transformAttrs:
		if a in self.loadAttrs:
		    self.loadAttrs.remove(a)
		    
	if self.HideUserDefinedOptionVar.value:
	    for a in self.SourceObject.userAttrs:
		if a in self.loadAttrs:
		    self.loadAttrs.remove(a)	
		    
	if self.HideParentAttrsOptionVar.value:
	    for a in self.loadAttrs:
		if (mc.attributeQuery(a, node = self.SourceObject.nameLong, listChildren=True)) is not None:
		    self.loadAttrs.remove(a)
		    
	if self.HideCGMAttrsOptionVar.value:
	    buffer = []
	    for a in self.loadAttrs:
		if 'cgm' not in a:
		    buffer.append(a)
	    if buffer:
		self.loadAttrs = buffer
	    
    if self.loadAttrs:	    
	return True
	
    return False

def uiUpdateSourceObjectData(self):
    """ 
    Update the loaded source object cata from the optionVar
    """     
    try:
	if updateLoadAttrs(self):

	    uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu)

	    self.ManageAttrList.clear()
	    if self.SourceObject:
		for a in self.loadAttrs:
		    self.ManageAttrList.append(a)

	else:
	    self.SourceObject = False
	    self.loadAttrs = []
	    guiFactory.warning("Failed to get attrs!")

    except:
	guiFactory.warning("Failed to update loaded!")



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Basic UI
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiLoadSourceObject(self,selectAttr = False):
    """ 
    Loads a source object and updates menus

    Keyword arguments:
    selectAttr(string) -- Name of an attr (False ignores)
    """   
    selected = search.returnSelected()

    self.activeAttr = []
    if selected:
	if '.' in selected[-1]:
	    targetBuffer = selected[-1].split('.')
	    self.SourceObjectOptionVar.set(targetBuffer[0])
	    self.SourceObject = ObjectFactory(targetBuffer[0])
	    
	    if len(targetBuffer) == 2:
		selectAttr = targetBuffer[-1]
	else:
	    self.SourceObjectOptionVar.set(selected[0])
	    self.SourceObject = ObjectFactory(selected[0])	    
	    
		
	# Put the object in the field
	self.SourceObject.getAttrs()
	self.SourceObjectField(e=True, text = self.SourceObjectOptionVar.value )	    
	self.ManagerSourceObjectField(e=True, text = self.SourceObjectOptionVar.value )	    

	# Get our attr menu
	uiUpdateSourceObjectData(self)	
	uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu,selectAttr)

    else:
	#clear the field
	guiFactory.doLoadSingleObjectToTextField(self.SourceObjectField, self.SourceObjectOptionVar.name)
	self.ManagerSourceObjectField(e=True, text = '' )	    
	self.SourceObjectOptionVar.set('')	
	self.SourceObject = False
	self.loadAttrs = []	

	uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu,selectAttr)

	self.ConvertAttrTypeOptionVar.set(0)

	#clear the menu items
	self.AttrReportField(edit = True, label = '...')

	self.KeyableAttrCB(edit=True, en = False,v=0)
	self.HiddenAttrCB(edit=True, en = False,v=0)
	self.LockedAttrCB(edit=True, en = False,v=0) 
	self.NameField(edit=True, en=False, text = '')
	self.NiceNameField(edit=True, en=False, text = '')
	self.AliasField(edit=True, en=False, text = '')        

	self.EditStringRow(e = True, vis = False)   
	self.EditEnumRow(e=True, vis = False)
	self.EditMessageRow(e=True, vis = False)
	self.AttrConvertRow(e=True, vis = False)

	self.DeleteAttrButton(e = True, en = False)

	#Clear the menus
	self.EditDigitSettingsRow(edit = True, vis = False)

	self.ManageAttrList.clear()

def uiSelectActiveAttr(self,attr):  
    """ 
    All the processes for when an attribut is selected

    Keyword arguments:
    attr(string) -- Name of an attr 
    """   
    #>>> Variables
    sourceObject =  mc.optionVar( q = 'cgmVar_AttributeSourceObject')
    attrType = mc.getAttr((sourceObject+'.'+attr),type=True)

    self.activeAttr = AttrFactory(sourceObject,attr)

    typeToTypesDict = {'numeric':['long','double','doubleAngle','doubleLinear'],
                       'string':['string'],
                       'message':['message']}

    fieldToTypeDict = {'min':self.MinField,
                       'max':self.MaxField,
                       'default':self.DefaultField,
                       'string':self.StringField,
                       'message':self.MessageField,
                       'enum':self.EnumField}

    if self.activeAttr.dynamic:
	self.DeleteAttrButton(e = True, en=True)
	indexAttr = False
	
	#Converion Row
	if self.activeAttr.parent or self.activeAttr.children:
	    self.AttrConvertRow(e=True, vis = False)
	else:
	    self.AttrConvertRow(e=True, vis = True)
	
	for option in attrTypesDict.keys():
	    if self.activeAttr.form in attrTypesDict.get(option): 
		indexAttr = option
		if indexAttr == 'long':
		    indexAttr = 'int'
		elif indexAttr == 'double':
		    indexAttr = 'float'
		break

	if indexAttr in self.attrConvertTypes:
	    self.ConvertAttrTypeOptionVar.set(0)	    
	    mc.radioCollection(self.ConvertAttrTypeRadioCollection ,edit=True,sl= (self.ConvertAttrTypeRadioCollectionChoices[ self.attrConvertTypes.index(indexAttr) ]))
	    self.ConvertAttrTypeOptionVar.set(1)


    else:
	self.DeleteAttrButton(e = True, en=False)
	self.AttrConvertRow(e=True, vis = False)

    uiUpdateAttrReport(self)

    #>>> Basics
    # Get our states
    keyableState = self.activeAttr.keyable
    hiddenState = self.activeAttr.hidden
    lockedState = self.activeAttr.locked
    if self.activeAttr.children:
	cKeyable = []
	cHidden = []
	cLocked = []
	for c in self.activeAttr.children:
	    buffer = attributes.returnStandardAttrFlags(self.activeAttr.obj.nameLong,c)
	    cKeyable.append(buffer.get('keyable'))
	    cHidden.append(buffer.get('hidden'))
	    cLocked.append(buffer.get('locked'))
	keyableState = sum(cKeyable)
	hiddenState = sum(cHidden)
	lockedState = sum(cLocked)
	    
    
    self.KeyableAttrCB(edit=True, value = keyableState, en = True,
                       cc = lambda *a:uiUpdateCheckBox(self, self.activeAttr.doKeyable,keyableState))

    self.HiddenAttrCB(edit=True, value = hiddenState, en = True,
                      cc = lambda *a:uiUpdateCheckBox(self,self.activeAttr.doHidden, hiddenState))

    self.LockedAttrCB(edit=True, value = lockedState, en = True,
                      cc = lambda *a:uiUpdateCheckBox(self,self.activeAttr.doLocked, lockedState)) 

    self.NameField(edit=True, en=True, text = self.activeAttr.nameLong)

    if self.activeAttr.dynamic:
	self.NiceNameField(edit=True, en=True, bgc = dictionary.returnStateColor('normal'), text = self.activeAttr.nameNice)
    else:
	self.NiceNameField(edit=True, en=False, text = '')  

    if self.activeAttr.nameAlias:
	self.AliasField(edit=True, en=True,
	                bgc = dictionary.returnStateColor('normal'), text = self.activeAttr.nameAlias)
    else:
	self.AliasField(edit=True, en=True,
	                bgc = dictionary.returnStateColor('normal'), text = '')  


    #>>> Numbers
    if self.activeAttr.numeric and self.activeAttr.dynamic and not self.activeAttr.children:
	self.EditDigitSettingsRow(edit = True, vis = True)
	minBuffer = self.activeAttr.minValue
	maxBuffer = self.activeAttr.maxValue
	defaultValue = self.activeAttr.defaultValue
	if self.activeAttr.minValue is not False:
	    self.MinField(e=True, text = str(self.activeAttr.minValue))
	else:
	    self.MinField(e=True, text = '')

	if self.activeAttr.maxValue is not False:
	    self.MaxField(e=True, text = str(self.activeAttr.maxValue))
	else:
	    self.MaxField(e=True, text = '')

	if self.activeAttr.defaultValue is not False:
	    self.DefaultField(e=True, text = str(self.activeAttr.defaultValue))
	else:
	    self.DefaultField(e=True, text = '')
	    
	if self.activeAttr.softMinValue is not False:
	    self.SoftMinField(e=True, text = str(self.activeAttr.softMinValue))
	else:
	    self.SoftMinField(e=True, text = '')

	if self.activeAttr.softMaxValue is not False:
	    self.SoftMaxField(e=True, text = str(self.activeAttr.softMaxValue))
	else:
	    self.SoftMaxField(e=True, text = '')
    else:
	self.EditDigitSettingsRow(edit = True, vis = False)

    #>>> String
    if self.activeAttr.form  == 'string':
	self.EditStringRow(e = True, vis = True)        
	self.StringField(edit = True,enable = True, text = self.activeAttr.value, 
	                 cc = lambda *a:uiUpdateString(self))      
    else:
	self.EditStringRow(e = True, vis = False)


    #>>> String  
    if self.activeAttr.form  == 'message':
	self.EditMessageRow(e=True, vis = True)
	self.MessageField(edit = True,enable = False, text = self.activeAttr.value)
	uiUpdateMessage
    else:
	self.EditMessageRow(e=True, vis = False)


    #>>> Enum
    if self.activeAttr.form  == 'enum' and self.activeAttr.dynamic: 
	self.EditEnumRow(e=True, vis = True)
	self.EnumField(edit = True,enable = True, text = self.activeAttr.enum,
	               cc = lambda *a:uiUpdateEnum(self))
    else:
	self.EditEnumRow(e=True, vis = False)


def uiUpdateObjectAttrMenu(self,menu,selectAttr = False):
    """ 
    Updates the attribute menu of a loaded object in the modify section

    Keyword arguments:
    menu(string) -- Menu name
    selectAttr(string) -- Name of an attr (False ignores)
    """ 
    def uiAttrUpdate(item):
	uiSelectActiveAttr(self,item)

    menu.clear()
    attrs=[]
    for a in self.loadAttrs:
	if a not in ['attributeAliasList']:
	    attrs.append(a)

    if attrs:
	if self.SortModifyOptionVar.value:
	    attrs.sort()    
	# Get the attributes list
	if attrs:
	    for a in attrs:
		menu.append(a)
	    uiSelectActiveAttr(self,attrs[-1])
	else:
	    menu.clear()
	#Select if we can
	if selectAttr in attrs:            
	    index = attrs.index(selectAttr)
	    self.ObjectAttributesOptionMenu.selectByIdx(index ) 
	    uiSelectActiveAttr(self,selectAttr)
	else:
	    uiSelectActiveAttr(self,attrs[0])
	menu(edit=True,cc = uiAttrUpdate)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Attribute Creation Section
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doAddAttributesToSelected(self): 
    """ 
    Adds attributes to selected objects
    """  
    #>>> Variables
    varCheck = mc.textField(self.AttrNamesTextField,q=True,text=True)
    selected = mc.ls(sl=True,shortNames = True)
    attrType = mc.optionVar(q='cgmVar_AttrCreateType')

    ### Asserts and verifies
    if not varCheck:
	guiFactory.warning("Variable name field is empty")
	return
    if not selected:
	guiFactory.warning("Variable name field is empty")
	return
    for obj in selected:
	assert mc.objExists(obj) is True,"'%s' doesn't exist"%obj


    #>>> Stuff to do
    ### Split a multi list
    if ';' in varCheck:
	attrsToAdd = varCheck.split(';')
    else:
	attrsToAdd = [varCheck]

    returnDict = {}
    if attrType == 'message':
	if len(selected) == 1:
	    objAttrBuffer = []
	    #Just gonna add a message attr
	    for attr in attrsToAdd: 
		if attributes.addMessageAttributeToObj(selected[0],attr):
		    objAttrBuffer.append(attr)
	    returnDict[obj] = objAttrBuffer
	else:
	    #if our number of names is equal to our number of selected items minus the last which we will add to
	    if len(selected[0:-1]) == len(attrsToAdd):
		#Just gonna add a message attr
		for obj in selected[:-1]: 
		    objAttrBuffer = []
		    cnt=selected.index(obj)
		    if attributes.storeObjectToMessage(obj,selected[-1],attrsToAdd[cnt]):
			objAttrBuffer.append(attrsToAdd[cnt])
		returnDict[selected[-1]] = objAttrBuffer

	    else:
		objAttrBuffer = []
		for obj in selected: 
		    objAttrBuffer = []	    
		    #Just gonna add a message attr
		    for attr in attrsToAdd: 
			if attributes.addMessageAttributeToObj(obj,attr):
			    objAttrBuffer.append(attr)
		    returnDict[obj] = objAttrBuffer

    else:
	for obj in selected:
	    objAttrBuffer = []
	    for attr in attrsToAdd:
		if attrType == 'string':
		    if attributes.addStringAttributeToObj(obj,attr):
			objAttrBuffer.append(attr)
		elif attrType == 'double3':
		    if attributes.addVectorAttributeToObj(obj,attr):
			objAttrBuffer.append(attr)
		elif attrType == 'int':
		    if attributes.addIntegerAttributeToObj(obj,attr):
			objAttrBuffer.append(attr)
		elif attrType == 'bool':
		    if attributes.addBoolAttrToObject(obj,attr):
			objAttrBuffer.append(attr)
		elif attrType == 'enum':
		    if attributes.addEnumAttrToObj(obj,attr):
			objAttrBuffer.append(attr)
		elif attrType == 'float':
		    if attributes.addFloatAttributeToObject(obj,attr):
			objAttrBuffer.append(attr)

	    returnDict[obj] = objAttrBuffer

    mc.select(cl=True)
    mc.select(selected[-1])


    uiLoadSourceObject(self,objAttrBuffer[-1])
    uiSelectActiveAttr(self,objAttrBuffer[-1])

    mc.select(selected)
    return returnDict


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modify Menu Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiUpdateAttrReport(self): 
    """ 
    Updates the attr report for the modify section
    """     
    buildReport = []
    connectReport = []
    self.ConnectedPopUpMenu.clear()
    
    if self.activeAttr:
	#>>> Connect Report
	if self.activeAttr.driver and self.activeAttr.form != 'message':
	    connectReport.append("'%s'>>Drives Me"%self.activeAttr.driver)
	    buffer = attributes.returnObjAttrSplit(self.activeAttr.driver)
	    MelMenuItem(self.ConnectedPopUpMenu ,
		    label = 'Select Driver',
		    c = Callback(mc.select,buffer[0]))	    
	    MelMenuItem(self.ConnectedPopUpMenu ,
		    label = 'Load Driver',
		    c = lambda *a: uiLoadAttrFromSub(self,self.activeAttr.driver ))		
	    MelMenuItem(self.ConnectedPopUpMenu ,
	            label = "Break from '%s'"%self.activeAttr.driver,
	            c = Callback(uiBreakConnection,self,self.activeAttr.nameCombined))
	    
	if self.activeAttr.driven:
	    if len(self.activeAttr.driven)<2:
		connectReport.append("Drives>>'%s'"%"','".join(self.activeAttr.driven))
	    else:
		connectReport.append("Drives>>[ %i ] attributes"%len(self.activeAttr.driven))		
	    MelMenuItem(self.ConnectedPopUpMenu,l='Driven:',en=False)
	    if len(self.activeAttr.driven)>1:
		MelMenuItem(self.ConnectedPopUpMenu ,
		        label = "Select All Connections",
		        c = Callback(mc.select,self.activeAttr.driven))	    
	    MelMenuItemDiv(self.ConnectedPopUpMenu)
	    for c in self.activeAttr.driven:
		buffer = attributes.returnObjAttrSplit(c)
		MelMenuItem(self.ConnectedPopUpMenu ,
		        label = "Select '%s'"%buffer[0],
		        c = Callback(mc.select,buffer[0]))
		MelMenuItem(self.ConnectedPopUpMenu ,
		        label = "Load Connection",
		        c = Callback(uiLoadAttrFromSub,self,c))		
		MelMenuItem(self.ConnectedPopUpMenu ,
		        label = "Break to '%s'"%c,
		        c = Callback(uiBreakConnection,self,c))	
		MelMenuItemDiv(self.ConnectedPopUpMenu)
		
	if connectReport:
	    self.ConnectionReportRow(e = True, vis = True)
	    self.ConnectionReportField(edit = True, label = ' | '.join(connectReport),vis=True)
	    
	    
	else:
	    self.ConnectionReportRow(e = True, vis = False)
	    self.ConnectionReportField(edit = True, label = '')	  
	    
	#>>> Other report
	if self.activeAttr.parent:
	    buildReport.append("Parent='%s'"%self.activeAttr.parent)
	if self.activeAttr.children:
	    buildReport.append("Children='%s'"%(',').join(self.activeAttr.children))
	    
	if self.activeAttr.numeric and self.activeAttr.children is False:
	    if len(list(str(self.activeAttr.value))) > 4 and type(self.activeAttr.value) is float:
		buildReport.append("Value=%f"%self.activeAttr.value)        
	    else:
		buildReport.append("Value=%s"%self.activeAttr.value)
		
	elif self.activeAttr.form == 'message':
	    buildReport.append("Message='%s'"%self.activeAttr.value)        
	elif self.activeAttr.children is False:
	    buildReport.append("Value=%s"%self.activeAttr.value)

	if buildReport:
	    self.AttrReportField(edit = True, label = ' | '.join(buildReport))
	
  
	
	

def uiUpdateCheckBox(self, commandAttr, valueAttr):   
    """ 
    Updates a checkbox and exectures a command

    Keyword arguments:
    commandAttr(instanced command) 
    valueAttr(instanced attr)
    """     
    commandAttr(not valueAttr)
    uiSelectActiveAttr(self,self.activeAttr.attr)

def uiConvertLoadedAttr(self,mode,Active = True):  
    """ 
    Converts a loaded attribute type

    Keyword arguments:
    mode(string) -- mode to convert to
    """     
    #>>> Variables
    if self.activeAttr and self.ConvertAttrTypeOptionVar.value:
	self.activeAttr.doConvert(mode)
	uiSelectActiveAttr(self,self.activeAttr.attr) 

def uiRenameAttr(self):   
    """ 
    Renames a loaded attr in the modify menu
    """     
    #>>> Variables
    varCheck = self.NameField(q=True,text=True)
    if self.activeAttr:
	if varCheck:
	    self.activeAttr.doRename(varCheck)
	    mc.select(self.activeAttr.obj.nameLong)
	    uiLoadSourceObject(self,varCheck)	    
	    uiSelectActiveAttr(self,varCheck)
	else:
	    uiSelectActiveAttr(self,self.activeAttr.attr)  

def uiUpdateAlias(self):   
    """ 
    Updates the alias a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.AliasField(q=True,text=True)
    if self.activeAttr:
	if varCheck:
	    self.activeAttr.doAlias(varCheck) 
	    uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu,selectAttr = varCheck)
	    uiSelectActiveAttr(self,varCheck)	    
	else:
	    self.activeAttr.doAlias(False)
	    uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu,selectAttr = self.activeAttr.attr)
	    uiSelectActiveAttr(self,self.activeAttr.attr)	    

	uiSelectActiveAttr(self,self.activeAttr.nameLong)  

def uiUpdateNiceName(self):  
    """ 
    Update nice name of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.NiceNameField(q=True,text=True)
    if self.activeAttr:
	if varCheck:
	    self.activeAttr.doNiceName(varCheck)             
	else:
	    self.activeAttr.doNiceName(self.activeAttr.attr.capitalize())

	uiSelectActiveAttr(self,self.activeAttr.attr)  

def uiUpdateString(self):   
    """ 
    Sets string value of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.StringField(q=True,text=True)
    if self.activeAttr:
	if varCheck:
	    self.activeAttr.set(varCheck)             
	else:
	    self.activeAttr.set('')

	uiSelectActiveAttr(self,self.activeAttr.attr) 

def uiUpdateMessage(self):   
    """ 
    Sets the message value of a loaded attr in the modify menu
    """  
    #>>> Variables
    selection = mc.ls(sl=True,flatten=True,long=True) or []
    if self.activeAttr:
	if selection:
	    self.activeAttr.doStore(selection[0])             
	else:
	    self.activeAttr.doStore('')
	    guiFactory.warning("'%s.%s' failed to store"%(self.activeAttr.obj.nameLong,self.activeAttr.attr))

	uiSelectActiveAttr(self,self.activeAttr.attr) 

def uiUpdateEnum(self):  
    """ 
    Updates enum options of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.EnumField(q=True,text=True)
    if self.activeAttr:
	if varCheck:
	    try:
		self.activeAttr.setEnum(varCheck)
	    except:
		guiFactory.warning("'%s.%s' failed to change. Check your command." %(self.activeAttr.obj.nameLong,self.activeAttr.attr))
	else:
	    self.activeAttr.set('')

	uiSelectActiveAttr(self,self.activeAttr.attr) 

def uiUpdateMinValue(self):  
    """ 
    Sets min value of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.MinField(q=True,text=True)
    if self.activeAttr:
	if type(varCheck)is unicode and len(varCheck) < 1:
	    self.activeAttr.doMin(False)             
	elif type(varCheck) is float or int:
	    try:
		self.activeAttr.doMin(float(varCheck))
	    except:
		guiFactory.report("'%s.%s' failed to set min. Probably not a dynamic attribute" %(self.activeAttr.obj.nameLong,self.activeAttr.attr))

	else:
	    self.activeAttr.doMin(False)

	uiSelectActiveAttr(self,self.activeAttr.attr)

def uiUpdateMaxValue(self):  
    """ 
    Sets max value of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.MaxField(q=True,text=True)
    if self.activeAttr:
	if type(varCheck)is unicode and len(varCheck) < 1:
	    self.activeAttr.doMax(False)           
	elif type(varCheck) is float or int:
	    try:
		self.activeAttr.doMax(float(varCheck))
	    except:
		guiFactory.report("'%s.%s' failed to set min. Probably not a dynamic attribute" %(self.activeAttr.obj.nameLong,self.activeAttr.attr))

	else:
	    self.activeAttr.doMax(False)

	uiSelectActiveAttr(self,self.activeAttr.attr)


def uiUpdateDefaultValue(self):  
    """ 
    Sets the default value of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.DefaultField(q=True,text=True)

    if self.activeAttr:
	if type(varCheck)is unicode and len(varCheck) < 1:
	    self.activeAttr.doDefault(False)        
	elif type(varCheck) is float or int:
	    try:
		self.activeAttr.doDefault(float(varCheck))
	    except:
		guiFactory.report("'%s.%s' failed to set min. Probably not a dynamic attribute" %(self.activeAttr.obj.nameLong,self.activeAttr.attr))

	else:
	    self.activeAttr.doDefault(False)

	uiSelectActiveAttr(self,self.activeAttr.attr) 
	
def uiUpdateSoftMaxValue(self):  
    """ 
    Sets min value of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.SoftMaxField(q=True,text=True)
    if self.activeAttr:
	if type(varCheck)is unicode and len(varCheck) < 1:
	    self.activeAttr.doSoftMax(0)             
	elif type(varCheck) is float or int:
	    try:
		self.activeAttr.doSoftMax(float(varCheck))
	    except:
		guiFactory.report("'%s.%s' failed to set min. Probably not a dynamic attribute" %(self.activeAttr.obj.nameLong,self.activeAttr.attr))

	else:
	    self.activeAttr.doSoftMax(False)

	uiSelectActiveAttr(self,self.activeAttr.attr)
	
def uiUpdateSoftMinValue(self):  
    """ 
    Sets min value of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.SoftMinField(q=True,text=True)
    if self.activeAttr:
	if type(varCheck)is unicode and len(varCheck) < 1:
	    self.activeAttr.doSoftMin(0)             
	elif type(varCheck) is float or int:
	    try:
		self.activeAttr.doSoftMin(float(varCheck))
	    except:
		guiFactory.report("'%s.%s' failed to set min. Probably not a dynamic attribute" %(self.activeAttr.obj.nameLong,self.activeAttr.attr))

	else:
	    self.activeAttr.doSoftMin(False)

	uiSelectActiveAttr(self,self.activeAttr.attr)
	
def uiDeleteAttr(self,menu):
    """ 
    Deletes a loaded attr in the modify menu
    """  
    #>>> Variables and assertations
    sourceObject =  mc.optionVar( q = 'cgmVar_AttributeSourceObject')
    assert mc.objExists(sourceObject) is True, "'%s' doesn't exist."%sourceObject

    #>>> Get info
    buffer =  menu.getMenuItems()
    attrList = []
    for item in buffer:
	attrList.append( mc.menuItem(item,q=True,label=True))
    cnt =  menu.getSelectedIdx()
    attrToDelete = attrList[cnt]

    #>>>Function
    try:
	attributes.doDeleteAttr(sourceObject,attrToDelete)
	guiFactory.warning("'%s.%s' removed"%(sourceObject,attrToDelete))
    except:
	guiFactory.warning("'%s.%s' failed to delete"%(sourceObject,attrToDelete))

    #Update the attr menu    
    updateLoadAttrs(self)
    uiUpdateObjectAttrMenu(self,menu)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Manage attributes functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiReorderAttributes(self,direction):
    """ 
    Reorder attributes from an active attribute selection

    Keyword arguments:
    direction(int) -- 0 is negative, 1 is positive
    """     
    attrsToMove = self.ManageAttrList.getSelectedItems()
    
    if attrsToMove and self.SourceObjectOptionVar.value:
	checkedAttrs = []
	for attr in attrsToMove:
	    #Check for parents
	    bufferDict = attributes.returnAttrFamilyDict(self.SourceObject.nameLong,attr)
	    flagDict = attributes.returnStandardAttrFlags(self.SourceObject.nameLong,attr)
	    if flagDict.get('dynamic'):
		if bufferDict and 'parent' in bufferDict.keys():
		    checkedAttrs.append(bufferDict.get('parent'))
		else:
		    checkedAttrs.append(attr)
	    checkedAttrs = lists.returnListNoDuplicates(checkedAttrs)
	
	if checkedAttrs:    
	    attributes.reorderAttributes(self.SourceObject.nameLong,checkedAttrs,direction)
	else:
	    guiFactory.warning("No dynamic attributes selected")

	uiUpdateSourceObjectData(self)

	self.ManageAttrList.selectItems(attrsToMove)
    else:
	guiFactory.warning('No attributes selected.')

def uiManageAttrsKeyable(self):
    """ 
    Makes an active attribute selection keyable
    """     
    attrs = self.ManageAttrList.getSelectedItems()

    if attrs and self.SourceObjectOptionVar.value:
	for a in attrs:
	    aInstance = AttrFactory(self.SourceObject.nameLong,a)
	    aInstance.doKeyable(True)

	uiUpdateSourceObjectData(self)

	self.ManageAttrList.selectItems(attrs)
    else:
	guiFactory.warning('No attributes selected.')

def uiManageAttrsUnkeyable(self):
    """ 
    Makes an active attribute selection unkeyable
    """     
    attrs = self.ManageAttrList.getSelectedItems()

    if attrs and self.SourceObjectOptionVar.value:
	for a in attrs:
	    aInstance = AttrFactory(self.SourceObject.nameLong,a)
	    aInstance.doKeyable(False)

	uiUpdateSourceObjectData(self)

	self.ManageAttrList.selectItems(attrs)
    else:
	guiFactory.warning('No attributes selected.')

def uiManageAttrsHide(self):
    """ 
    Makes an active attribute selection hidden
    """     
    attrs = self.ManageAttrList.getSelectedItems()

    if attrs and self.SourceObjectOptionVar.value:
	for a in attrs:
	    aInstance = AttrFactory(self.SourceObject.nameLong,a)
	    aInstance.doHidden(True)

	uiUpdateSourceObjectData(self)

	self.ManageAttrList.selectItems(attrs)
    else:
	guiFactory.warning('No attributes selected.')

def uiManageAttrsUnhide(self):
    """ 
    Makes an active attribute selection unhidden
    """     
    attrs = self.ManageAttrList.getSelectedItems()

    if attrs and self.SourceObjectOptionVar.value:
	for a in attrs:
	    aInstance = AttrFactory(self.SourceObject.nameLong,a)
	    aInstance.doHidden(False)

	uiUpdateSourceObjectData(self)

	self.ManageAttrList.selectItems(attrs)
    else:
	guiFactory.warning('No attributes selected.')

def uiManageAttrsLocked(self):
    """ 
    Makes an active attribute selection locked
    """     
    attrs = self.ManageAttrList.getSelectedItems()

    if attrs and self.SourceObjectOptionVar.value:
	for a in attrs:
	    aInstance = AttrFactory(self.SourceObject.nameLong,a)
	    aInstance.doLocked(True)

	uiUpdateSourceObjectData(self)

	self.ManageAttrList.selectItems(attrs)
    else:
	guiFactory.warning('No attributes selected.')

def uiManageAttrsUnlocked(self):
    """ 
    Makes an active attribute selection unlocked
    """     
    attrs = self.ManageAttrList.getSelectedItems()

    if attrs and self.SourceObjectOptionVar.value:
	for a in attrs:
	    aInstance = AttrFactory(self.SourceObject.nameLong,a)
	    aInstance.doLocked(False)

	uiUpdateSourceObjectData(self)

	self.ManageAttrList.selectItems(attrs)
    else:
	guiFactory.warning('No attributes selected.')


def uiManageAttrsDelete(self):
    """ 
    Makes an active attribute selection no more...deleted
    """     
    attrs = self.ManageAttrList.getSelectedItems()

    if attrs and self.SourceObjectOptionVar.value:
	for a in attrs:
	    aInstance = AttrFactory(self.SourceObject.nameLong,a)
	    aInstance.doDelete()

	uiUpdateSourceObjectData(self)

    else:
	guiFactory.warning('No attributes selected.')
	
def uiBreakConnection(self,attribute):
    """ 
    Breaks a connection in a submenu
    """     
    attributes.doBreakConnection(attribute)
    buffer = attributes.returnObjAttrSplit(attribute)
    if buffer:
	uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu,buffer[1])
	
def uiLoadAttrFromSub(self,attribute):
    """ 
    Load an attribute from a submenu
    """     
    mc.select(attribute)
    #buffer = attributes.returnObjAttrSplit(attribute)    
    uiLoadSourceObject(self)
