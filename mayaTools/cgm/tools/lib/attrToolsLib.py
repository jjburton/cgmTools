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
def uiLoadSourceObject(self,selectAttr = False):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True,shortNames=True))

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

def uiSelectActiveAttr(self,attr):  
    #>>> Variables
    sourceObject =  mc.optionVar( q = 'cgmVar_AttributeSourceObject')
    attrType = mc.getAttr((sourceObject+'.'+attr),type=True)
    print attrType
    
    
    typeToTypesDict = {'numeric':['long','double','doubleAngle','doubleLinear'],
                       'string':['string'],
                       'message':['message']}
    
    fieldToTypeDict = {'min':self.MinField,
                       'max':self.MaxField,
                       'default':self.DefaultField,
                       'string':self.StringField,
                       'message':self.MessageField,
                       'enum':self.EnumField}
    
    #>>> Basics
    #keyableState = mc.getAttr((sourceObject+'.'+attr),keyable=True)
    #hiddenState =  mc.getAttr((sourceObject+'.'+attr),cb=True)
    lockedState =  mc.getAttr((sourceObject+'.'+attr), lock=True)
    keyableState = mc.attributeQuery(attr, node = sourceObject, keyable=True)
    hiddenState =  mc.attributeQuery(attr, node = sourceObject, hidden=True)
    
    if mc.attributeQuery(attr, node = sourceObject, minExists=True):
        minValue =  mc.attributeQuery(attr, node = sourceObject, minimum=True)
        print 'min'
        print minValue
        
    if mc.attributeQuery(attr, node = sourceObject, maxExists=True):
        maxValue =  mc.attributeQuery(attr, node = sourceObject, maximum=True)
        print 'max'
        print maxValue
    
    defaultValue = mc.addAttr((sourceObject+'.'+attr),q=True,defaultValue = True)
    print 'defaultValue'
    print defaultValue
    

    self.KeyableAttrCB(edit=True, value = keyableState)
    if not hiddenState and not keyableState:
        self.HiddenAttrCB(edit=True, value = 1)
    else:
        self.HiddenAttrCB(edit=True, value = 0)
    self.LockedAttrCB(edit=True, value = lockedState) 

    #>>> String
    if attrType == 'string':
        currentString = mc.getAttr((sourceObject+'.'+attr))
        self.StringField(edit = True,enable = True, text = currentString)
        
    elif attrType == 'message':
        currentObject = attributes.returnMessageObject(sourceObject,attr)
        self.MessageField(edit = True,enable = True, text = currentObject)
        
    elif attrType == 'enum':
        currentString = mc.getAttr((sourceObject+'.'+attr),asString = True)
        options = mc.attributeQuery(attr, node = sourceObject, listEnum=True)
        optionList = options[0].split(':')
        for o in optionList:
            print o
        
        self.EnumField(edit = True,enable = True, text = (';'.join(optionList)))







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
        for attr in 'translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ','visibility':
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



