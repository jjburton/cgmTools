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
__version__ = '0.1.03282012'

import maya.cmds as mc
import maya.mel as mel
from cgm.lib.classes import NameFactory
from cgm.lib.classes.AttrFactory import *


from cgm.lib import *
from cgm.lib import (guiFactory,
                     dictionary,
                     attributes,
                     search)
reload(attributes)
reload(search)
reload(dictionary)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# UI Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiUpdateAttrReport(self): 
    buildReport = []
    if self.activeAttr:
    
	if self.activeAttr.driverAttribute and self.activeAttr.form != 'message':
	    buildReport.append("'%s'>>Drives Me"%self.activeAttr.driverAttribute)
	    
	if self.activeAttr.drivenAttribute:
	    buildReport.append("Drives>>'%s'"%self.activeAttr.drivenAttribute)
	
	
	if self.activeAttr.numeric:
	    if len(list(str(self.activeAttr.value))) > 4 and type(self.activeAttr.value) is float:
		buildReport.append("Value=%f"%self.activeAttr.value)        
	    else:
		buildReport.append("Value=%s"%self.activeAttr.value)
	elif self.activeAttr.form == 'message':
	    buildReport.append("Message='%s'"%self.activeAttr.value)        
	else:
	    buildReport.append("Value=%s"%self.activeAttr.value)
	    
	
	self.AttrReportField(edit = True, label = ' | '.join(buildReport))

def uiUpdateCheckBox(self, commandAttr, valueAttr):   
    commandAttr(not valueAttr)
    uiSelectActiveAttr(self,self.activeAttr.attr)
    
def uiConvertLoadedAttr(self,mode,Active = True):    
    #>>> Variables
    if self.activeAttr and self.ConvertAttrTypeOptionVar.value:
	self.activeAttr.convert(mode)
	uiSelectActiveAttr(self,self.activeAttr.attr) 
	
def uiRenameAttr(self):    
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
    #>>> Variables
    varCheck = self.NiceNameField(q=True,text=True)
    if self.activeAttr:
        if varCheck:
            self.activeAttr.doNiceName(varCheck)             
        else:
            self.activeAttr.doNiceName(self.activeAttr.attr.capitalize())
            
        uiSelectActiveAttr(self,self.activeAttr.attr)  
        
def uiUpdateString(self):    
    #>>> Variables
    varCheck = self.StringField(q=True,text=True)
    if self.activeAttr:
        if varCheck:
            self.activeAttr.set(varCheck)             
        else:
            self.activeAttr.set('')
            
        uiSelectActiveAttr(self,self.activeAttr.attr) 
        
def uiUpdateMessage(self):    
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




def uiLoadSourceObject(self,selectAttr = False):
    selected = []
    bufferList = []
    #mc.select('test_bsNode')
    
    selected = (mc.ls (sl=True,flatten=True,shortNames=True))
    self.activeAttr = []
    if selected:
        if len(selected) >= 2:
            guiFactory.warning('Only one object can be loaded')
        else:
            # Put the object in the field
            guiFactory.doLoadSingleObjectToTextField(self.SourceObjectField,'cgmVar_AttributeSourceObject')
            
            # Get our attr menu
            uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu,selectAttr)


    else:
        #clear the field
        guiFactory.doLoadSingleObjectToTextField(self.SourceObjectField,'cgmVar_AttributeSourceObject')
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

def uiSelectActiveAttr(self,attr):  
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
	#Converion Row
	self.AttrConvertRow(e=True, vis = True)
	indexAttr = False
	
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
    self.KeyableAttrCB(edit=True, value = self.activeAttr.keyable, en = True,
                       cc = lambda *a:uiUpdateCheckBox(self, self.activeAttr.doKeyable,self.activeAttr.keyable))
    
    self.HiddenAttrCB(edit=True, value = self.activeAttr.hidden, en = True,
                      cc = lambda *a:uiUpdateCheckBox(self,self.activeAttr.doHidden, self.activeAttr.hidden))

    self.LockedAttrCB(edit=True, value = self.activeAttr.locked, en = True,
                      cc = lambda *a:uiUpdateCheckBox(self,self.activeAttr.doLocked, self.activeAttr.locked)) 

    self.NameField(edit=True, en=True, text = self.activeAttr.nameLong)
    
    if self.activeAttr.dynamic:
    	self.NiceNameField(edit=True, en=True, text = self.activeAttr.nameNice)
    else:
	self.NiceNameField(edit=True, en=False, text = '')  
	
    if self.activeAttr.nameAlias:
	self.AliasField(edit=True, en=True, text = self.activeAttr.nameAlias)
    else:
	self.AliasField(edit=True, en=True, text = '')  
    
    
    #>>> Numbers
    if self.activeAttr.form in ['long','float','double','doubleLinear','doubleAngle'] and self.activeAttr.dynamic:
        self.EditDigitSettingsRow(edit = True, vis = True)
        minBuffer = self.activeAttr.minValue
        maxBuffer = self.activeAttr.maxValue
        defaultValue = self.activeAttr.defaultValue
        if minBuffer is not False:
            self.MinField(e=True, text = str(minBuffer))
        else:
            self.MinField(e=True, text = '')
            
        if maxBuffer is not False:
            self.MaxField(e=True, text = str(maxBuffer))
        else:
            self.MaxField(e=True, text = '')
            
        if defaultValue is not False:
            self.DefaultField(e=True, text = str(defaultValue))
        else:
            self.DefaultField(e=True, text = '')
            
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
    if self.activeAttr.form  == 'enum': 
        self.EditEnumRow(e=True, vis = True)
        self.EnumField(edit = True,enable = True, text = self.activeAttr.enum,
                       cc = lambda *a:uiUpdateEnum(self))
    else:
        self.EditEnumRow(e=True, vis = False)



def uiDeleteAttr(self,menu):
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
        attributes.deleteAttr(sourceObject,attrToDelete)
        guiFactory.warning("'%s.%s' removed"%(sourceObject,attrToDelete))
    except:
        guiFactory.warning("'%s.%s' failed to delete"%(sourceObject,attrToDelete))

    #Update the attr menu    
    uiUpdateObjectAttrMenu(self,menu)


def uiUpdateObjectAttrMenu(self,menu,selectAttr = False):			
    def uiAttrUpdate(item):
        uiSelectActiveAttr(self,item)

    sourceObject =  mc.optionVar( q = 'cgmVar_AttributeSourceObject')

    if mc.objExists(sourceObject):
        # Get the attributes list
        menu.clear()
        attrs = mc.listAttr(sourceObject,keyable=True)
        regAttrs = mc.listAttr(sourceObject)
        userAttrs = mc.listAttr(sourceObject,userDefined = True) or []
        lockedAttrs = mc.listAttr(sourceObject,locked = True) or []
        for attr in 'translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ','v':
            if attr in regAttrs:
                attrs.append(attr)

        if userAttrs:
            attrs.extend( userAttrs )

        if lockedAttrs:
            attrs.extend( lockedAttrs )

        attrs = lists.returnListNoDuplicates(attrs)
        attrs.sort()	    
	    
        if attrs:
            for a in attrs:
                if a in ['attributeAliasList']:
		    attrs.remove(a)
		else:
                    menu.append(a)
            uiSelectActiveAttr(self,attrs[-1])
        else:
            menu.clear()
        #Select if we can
        if selectAttr in attrs:            
            index = attrs.index(selectAttr)
            self.ObjectAttributesOptionMenu.selectByIdx(index ) 
            uiSelectActiveAttr(self,attr)
        else:
            uiSelectActiveAttr(self,attrs[0])
        menu(edit=True,cc = uiAttrUpdate)

    else:
        menu.clear()
  


def doAddAttributesToSelected(self):    
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
                elif attrType == 'vector':
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



