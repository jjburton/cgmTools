#=================================================================================================================================================
#=================================================================================================================================================
#	objectFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for finding stuff
#
# Keyword arguments:
# 	Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#   0.11 - 04/04/2011 - added cvListSimplifier
#
# FUNCTION KEY:
#   1) ????
#   2) ????
#   3) ????
#
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel
from cgm.lib.classes import NameFactory
from cgm.lib.classes.ObjectFactory import *
from cgm.lib import (search,
                     attributes,
                     dictionary,
                     guiFactory)
reload(attributes)
attrTypesDict = {'message':['message','msg','m'],
                 'double':['float','fl','f','doubleLinear'],
                 'string':['string','s','str'],
                 'long':['long','int','i','integer'],
                 'bool':['bool','b','boolean'],
                 'enum':['enum','options','e'],
                 'vector':['vector','vec','v']}

class AttrFactory():
    """ 
    Initialized a maya object as a class obj
    """
    def __init__(self,objName,attrName,attrType = False,value = None,*a, **kw):
        """ 
        Asserts object's existance and that it has a transform. Then initializes. If 
        an existing attribute name on an object is called and the attribute type is different,
        
        
        Keyword arguments:
        obj(string)        
        
        """
        ### input check
        assert mc.objExists(objName) is True, "'%s' doesn't exist" %objName
        self.form = self.validateRequestedAttrType(attrType)
        self.attr = attrName
        
        self.obj = ObjectFactory(objName)
        
        # If it exists we need to check the type. 
        if mc.objExists('%s.%s'%(self.obj.nameLong,attrName)):
            currentType = mc.getAttr('%s.%s'%(self.obj.nameLong,attrName),type=True)
            if attrType != currentType and self.form is not False:            
                self.convert(attrType)
            else:
                self.attr = attrName
                self.form = currentType
        else:
            try:
                if self.form == False:
                    self.form = 'string'
                    attributes.addStringAttributeToObj(self.obj.nameLong,attrName,*a, **kw)
                elif self.form == 'double':
                    attributes.addFloatAttributeToObject(self.obj.nameLong,attrName,*a, **kw)
                elif self.form == 'string':
                    attributes.addStringAttributeToObj(self.obj.nameLong,attrName,*a, **kw)
                elif self.form == 'long':
                    attributes.addIntegerAttributeToObj(self.obj.nameLong,attrName,*a, **kw) 
                elif self.form == 'vector':
                    attributes.addVectorAttributeToObj(self.obj.nameLong,attrName,*a, **kw)
                elif self.form == 'enum':
                    attributes.addEnumAttrToObj(self.obj.nameLong,attrName,*a, **kw)
                elif self.form == 'bool':
                    attributes.addBoolAttrToObject(self.obj.nameLong,attrName,*a, **kw)
                elif self.form == 'enum':
                    attributes.addEnumAttrToObj(self.obj.nameLong,attrName,*a, **kw)
                elif self.form == 'message':
                    attributes.addMessageAttributeToObj(self.obj.nameLong,attrName,*a, **kw)
            except:
                guiFactory.warning("'%s.%s' failed to add",(self.obj.nameLong,attrName))
                
        if value is not None:
            self.set(value)
        
        self.updateData(*a, **kw)


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def updateData(self,*a, **kw):
        """ 
        Get's attr updated data       
        """     
        assert mc.objExists('%s.%s'%(self.obj.nameLong,self.attr)) is True, "'%s.%s' doesn't exist" %(self.obj.nameLong,self.attr)
        
        self.get(*a, **kw)
        
        self.locked = attributes.doGetAttr(self.obj.nameLong,self.attr,lock=True)
        self.keyable = mc.attributeQuery(self.attr, node = self.obj.nameLong, keyable=True)
        self.hidden = mc.attributeQuery(self.attr, node = self.obj.nameLong, hidden=True)
        
        if self.form not in ['string','message']:
            self.minValue = False
            if mc.attributeQuery(self.attr, node = self.obj.nameLong, minExists=True):
                self.minValue =  mc.attributeQuery(self.attr, node = self.obj.nameLong, minimum=True)
                guiFactory.report("'%s.%s' minValue is %s" %(self.obj.nameLong,self.attr, self.minValue))
                
            self.maxValue = False
            if mc.attributeQuery(self.attr, node = self.obj.nameLong, maxExists=True):
                self.maxValue =  mc.attributeQuery(self.attr, node = self.obj.nameLong, maximum=True)
                guiFactory.report("'%s.%s' maxValue is %s" %(self.obj.nameLong,self.attr, self.maxValue))
                
            self.defaultValue = False
            if mc.addAttr((self.obj.nameLong+'.'+self.attr),q=True,defaultValue = True):
                self.defaultValue = mc.addAttr((self.obj.nameLong+'.'+self.attr),q=True,defaultValue = True)
                guiFactory.report("'%s.%s' defaultValue is %s" %(self.obj.nameLong,self.attr, self.defaultValue))
    
    def convert(self,attrType):
        """ 
        Converts an attribute type from one to another
        
        Keyword arguments:
        attrType(string)        
        """        
        #try:
        attributes.convertAttrType('%s.%s'%(self.obj.nameLong,self.attr),attrType)
            
        #except:
        #guiFactory.warning("'%s.%s' failed to convert"%(self.obj.nameLong,self.attr))
            
            
    def validateRequestedAttrType(self,attrType):
        """ 
        Returns if an attr type is valid or not
        
        Keyword arguments:
        attrType(string)        
        """          
        aType = False
        for option in attrTypesDict.keys():
            if attrType in attrTypesDict.get(option): 
                aType = option
                break
            
        return aType
    
    def set(self,value,*a, **kw):
        """ 
        Set attr value based on attr type
        
        Keyword arguments:
        value(varied)   
        *a, **kw
        """
        try:
            attributes.doSetAttr(self.obj.nameLong,self.attr, value, *a, **kw)
        
        except:
            guiFactory.warning("'%s.%s' failed to set '%s'"%(self.obj.nameLong,self.attr,value))
        
        
    def get(self,*a, **kw):
        """ 
        Get and store attribute value based on attr type
        
        Keyword arguments:
        *a, **kw
        """     
        try:
            if self.form == 'message':
                self.value = attributes.returnMessageObject(self.obj.nameLong,self.attr)
            else:
                self.value =  attributes.doGetAttr(self.obj.nameLong,self.attr,*a, **kw)
            guiFactory.report("'%s.%s' >> '%s'"%(self.obj.nameLong,self.attr,self.value))
            return self.value
        except:
            guiFactory.warning("'%s.%s' failed to get"%(self.obj.nameLong,self.attr))
            
    def delete(self,*a, **kw):
        """ 
        Deletes an attribute
        
        Keyword arguments:
        *a, **kw
        """ 
        try:
            attributes.deleteAttr(self.obj.nameLong,self.attr)
            guiFactory.warning("'%s.%s' deleted"%(self.obj.nameLong,self.attr))
            self.value = None
            return self.value
        
        except:
            guiFactory.warning("'%s.%s' failed to delete"%(self.obj.nameLong,self.attr))   
            
    def getMessage(self,*a, **kw):
        """ 
        Get and store attribute value as if they were messages. Used for bufferFactory to use a connected
        attribute as a poor man's attribute message function
        
        Keyword arguments:
        *a, **kw
        """   
        try:
            if self.form == 'message':
                self.value = attributes.returnMessageObject(self.obj.nameLong,self.attr)
            else:
                self.value = attributes.returnDriverAttribute("%s.%s"%(self.obj.nameLong,self.attr))

            guiFactory.report("'%s.%s' >Message> '%s'"%(self.obj.nameLong,self.attr,self.value))
            return self.value
            
        except:
            guiFactory.warning("'%s.%s' failed to get"%(self.obj.nameLong,self.attr))
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Set Options
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     
    def isDefault(self,value = None):
        if value is not None:
            try:
                mc.addAttr((self.obj.nameLong+'.'+self.attr),e=True,defaultValue = value)
                self.defaultValue = value
            except:
                guiFactory.warning("'%s.%s' failed to set a default value"%(self.obj.nameLong,self.attr))       
                
    def isMax(self,value = None):
        if value is False:
            try:
                mc.addAttr((self.obj.nameLong+'.'+self.attr),e=True,hasMaxValue = value)
                self.maxValue = value
                guiFactory.warning("'%s.%s' had it's max value cleared"%(self.obj.nameLong,self.attr))                     
            except:
                guiFactory.warning("'%s.%s' failed to clear a max value"%(self.obj.nameLong,self.attr))  
        
        elif value is not None:
            try:
                mc.addAttr((self.obj.nameLong+'.'+self.attr),e=True,maxValue = value)
                self.maxValue = value
            except:
                guiFactory.warning("'%s.%s' failed to set a max value"%(self.obj.nameLong,self.attr))
                
                
    def isMin(self,value = None):
        if value is False:
            try:
                mc.addAttr((self.obj.nameLong+'.'+self.attr),e=True,hasMinValue = value)
                self.minValue = value
                guiFactory.warning("'%s.%s' had it's min value cleared"%(self.obj.nameLong,self.attr))                     
            except:
                guiFactory.warning("'%s.%s' failed to clear a min value"%(self.obj.nameLong,self.attr))
        
        
        elif value is not None:
            try:
                mc.addAttr((self.obj.nameLong+'.'+self.attr),e=True,minValue = value)
                self.minValue = value
            except:
                guiFactory.warning("'%s.%s' failed to set a default value"%(self.obj.nameLong,self.attr))
    
    def isLocked(self,arg = True):
        if arg:
            if not self.locked:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,lock = True) 
                guiFactory.report("'%s.%s' locked!"%(self.obj.nameLong,self.attr))
                self.locked = True
                
        else:
            if self.locked:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,lock = False)           
                guiFactory.report("'%s.%s' unlocked!"%(self.obj.nameLong,self.attr))
                self.locked = False
                
    def isHidden(self,arg = True):
        if arg:
            if not self.hidden:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,channelBox = False) 
                guiFactory.report("'%s.%s' hidden!"%(self.obj.nameLong,self.attr))
                self.hidden = True

                
        else:
            if self.hidden:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,channelBox = True)           
                guiFactory.report("'%s.%s' unhidden!"%(self.obj.nameLong,self.attr))
                self.hidden = False
                
                
    def isKeyable(self,arg = True):
        if arg:
            if not self.keyable:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,keyable = True) 
                guiFactory.report("'%s.%s' keyable!"%(self.obj.nameLong,self.attr))
                self.keyable = True
                if self.hidden:
                    self.hidden = False
                
        else:
            if self.keyable:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,keyable = False)           
                guiFactory.report("'%s.%s' unkeyable!"%(self.obj.nameLong,self.attr))
                self.keyable = False
                if not self.hidden:
                    mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,channelBox = True) 
                    
            
            
            
        