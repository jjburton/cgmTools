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
    def __init__(self,objName,attrName,attrType,value = None,*a, **kw):
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
            if attrType != currentType:            
                self.convert(attrType)
            else:
                self.attr = attrName
        else:
            try:
                if self.form == 'double':
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


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def convert(self,attrType):
        #try:
        attributes.convertAttrType('%s.%s'%(self.obj.nameLong,self.attr),attrType)
            
        #except:
        #guiFactory.warning("'%s.%s' failed to convert"%(self.obj.nameLong,self.attr))
            
            
    def validateRequestedAttrType(self,attrType):
        aType = False
        for option in attrTypesDict.keys():
            if attrType in attrTypesDict.get(option): 
                aType = option
                break
            
        assert aType is not False,"'%s' is not a valid attribute type!"%attrType
        return aType
    
    def set(self,value,*a, **kw):
        try:
            attrBuffer = '%s.%s'%(self.obj.nameLong,self.attr)
            if self.form == 'long':
                mc.setAttr(attrBuffer,int(float(value)),*a, **kw)
            elif self.form == 'string':
                mc.setAttr(attrBuffer,str(value),type = 'string',*a, **kw)
            elif self.form == 'double':
                mc.setAttr(attrBuffer,float(value),*a, **kw)
            elif self.form == 'message':
                buffer = attributes.storeObjectToMessage(value,self.obj.nameLong,self.attr)
                if not buffer:
                    guiFactory.warning("'%s.%s' failed to add '%s'. Guessing it doesn't exist"%(self.obj.nameLong,self.attr,value))                    
            else:
                mc.setAttr(attrBuffer,value,type = self.form,*a, **kw)        
    
            mc.setAttr('%s.%s'%(self.obj.nameLong,self.attr),*a, **kw)
        except:
            guiFactory.warning("'%s.%s' failed to set '%s'"%(self.obj.nameLong,self.attr,value))
        
    def get(self,*a, **kw):
        try:
            if self.form == 'message':
                self.value = attributes.returnMessageObject(self.obj.nameLong,self.attr)
            else:
                self.value =  mc.getAttr('%s.%s'%(self.obj.nameLong,self.attr),*a, **kw)
            guiFactory.warning("'%s.%s' >> '%s'"%(self.obj.nameLong,self.attr,self.value))
        except:
            guiFactory.warning("'%s.%s' failed to get"%(self.obj.nameLong,self.attr))
            
        