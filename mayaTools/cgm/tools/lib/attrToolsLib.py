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
def uiUpdateCheckBox(self, commandAttr, valueAttr):   
    commandAttr(not valueAttr)
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
            self.activeAttr.isMin(False)             
        elif type(varCheck) is float or int:
            try:
                self.activeAttr.isMin(float(varCheck))
            except:
                guiFactory.report("'%s.%s' failed to set min. Probably not a dynamic attribute" %(self.activeAttr.obj.nameLong,self.activeAttr.attr))
                
        else:
            self.activeAttr.isMin(False)
            
        uiSelectActiveAttr(self,self.activeAttr.attr)
        
def uiUpdateMaxValue(self):    
    #>>> Variables
    varCheck = self.MaxField(q=True,text=True)
    print varCheck
    if self.activeAttr:
        if type(varCheck)is unicode and len(varCheck) < 1:
            self.activeAttr.isMax(False)           
        elif type(varCheck) is float or int:
            try:
                self.activeAttr.isMax(float(varCheck))
            except:
                guiFactory.report("'%s.%s' failed to set min. Probably not a dynamic attribute" %(self.activeAttr.obj.nameLong,self.activeAttr.attr))
                
        else:
            self.activeAttr.isMax(False)
            
        uiSelectActiveAttr(self,self.activeAttr.attr)

        
def uiUpdateDefaultValue(self):    
    #>>> Variables
    varCheck = self.DefaultField(q=True,text=True)

    if self.activeAttr:
        if type(varCheck)is unicode and len(varCheck) < 1:
            self.activeAttr.isDefault(False)        
        elif type(varCheck) is float or int:
            try:
                self.activeAttr.isDefault(float(varCheck))
            except:
                guiFactory.report("'%s.%s' failed to set min. Probably not a dynamic attribute" %(self.activeAttr.obj.nameLong,self.activeAttr.attr))
                
        else:
            self.activeAttr.isDefault(False)
            
        uiSelectActiveAttr(self,self.activeAttr.attr)   




def uiLoadSourceObject(self,selectAttr = False):
    selected = []
    bufferList = []
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
        
        #clear the menu items
        self.KeyableAttrCB(edit=True, en = False)
        self.HiddenAttrCB(edit=True, en = False)
        self.LockedAttrCB(edit=True, en = False) 
        
        self.EditStringRow(e = True, vis = False)   
        self.EditEnumRow(e=True, vis = False)
        self.EditMessageRow(e=True, vis = False)
        
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
    else:
        self.DeleteAttrButton(e = True, en=False)
        
        
    #>>> Basics     
    self.KeyableAttrCB(edit=True, value = self.activeAttr.keyable, en = True,
                       cc = lambda *a:uiUpdateCheckBox(self, self.activeAttr.isKeyable,self.activeAttr.keyable))
    
    self.HiddenAttrCB(edit=True, value = self.activeAttr.hidden, en = True,
                      cc = lambda *a:uiUpdateCheckBox(self,self.activeAttr.isHidden, self.activeAttr.hidden))

    self.LockedAttrCB(edit=True, value = self.activeAttr.locked, en = True,
                      cc = lambda *a:uiUpdateCheckBox(self,self.activeAttr.isLocked, self.activeAttr.locked)) 

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
        
    if self.activeAttr.form  == 'message':
        self.EditMessageRow(e=True, vis = True)
        self.MessageField(edit = True,enable = False, text = self.activeAttr.value)
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
        userAttrs = mc.listAttr(sourceObject,userDefined = True)
        lockedAttrs = mc.listAttr(sourceObject,locked = True)
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
            print ("single mode")
            objAttrBuffer = []
            #Just gonna add a message attr
            for attr in attrsToAdd: 
                if attributes.addMessageAttributeToObj(selected[0],attr):
                    objAttrBuffer.append(attr)
            returnDict[obj] = objAttrBuffer
        else:
            #if our number of names is equal to our number of selected items minus the last which we will add to
            if len(selected[0:-1]) == len(attrsToAdd):
                print('message mode')
                #Just gonna add a message attr
                for obj in selected[:-1]: 
                    objAttrBuffer = []
                    cnt=selected.index(obj)
                    if attributes.storeObjectToMessage(obj,selected[-1],attrsToAdd[cnt]):
                        objAttrBuffer.append(attrsToAdd[cnt])
                        print objAttrBuffer
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

    print returnDict

    uiLoadSourceObject(self,objAttrBuffer[-1])

    mc.select(selected)
    print returnDict
    return returnDict



