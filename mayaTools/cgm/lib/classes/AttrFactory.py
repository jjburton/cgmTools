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
reload(guiFactory)
attrTypesDict = {'message':['message','msg','m'],
                 'double':['float','fl','f','doubleLinear','double'],
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
        
            
        #guiFactory.report("'%s.%s' >> '%s' >> is '%s'"%(self.obj.nameLong,self.attr,self.value,self.form))
        

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def updateData(self,*a, **kw):
        """ 
        Get's attr updated data       
        """     
        assert mc.objExists('%s.%s'%(self.obj.nameLong,self.attr)) is True, "'%s.%s' doesn't exist" %(self.obj.nameLong,self.attr)
        # Default attrs
        self.nameCombined = '%s.%s'%(self.obj.nameLong,self.attr)        
        self.minValue = False
        self.maxValue = False
        self.defaultValue = False
        self.nameNice = mc.attributeQuery(self.attr, node = self.obj.nameLong, niceName = True)
        self.nameLong = mc.attributeQuery(self.attr, node = self.obj.nameLong, longName = True)
        self.nameAlias = False
        if mc.aliasAttr(self.nameCombined,q=True):
            self.nameAlias = mc.aliasAttr(self.nameCombined,q=True)
        
        self.enum = False
        self.userAttrs = mc.listAttr(self.obj.nameLong, userDefined = True) or []
        
        #Check connections
        self.driverAttribute = attributes.returnDriverAttribute(self.nameCombined)
        self.drivenAttribute = attributes.returnDrivenAttribute(self.nameCombined)
        
        #Check if dynamic. As best I understand it, it's whether an attribute is user created or not
        self.dynamic = False        
        if self.nameLong in self.userAttrs:
            self.dynamic = True
            
        self.get(*a, **kw)
        
        #Check if numeric
        self.numeric = True
        if self.form in ['string','message','enum','bool']:
            self.numeric = False
        
        self.locked = mc.getAttr(self.nameCombined ,lock=True)
        self.keyable = mc.getAttr(self.nameCombined ,keyable=True)
        
        # So, if it's keyable, you have to use one attribute to read correctly, otherwise it's the other...awesome
        self.hidden = not mc.getAttr(self.nameCombined,channelBox=True)
        if self.keyable:
            self.hidden = mc.attributeQuery(self.attr, node = self.obj.nameLong, hidden=True)
        #if self.form not in ['string','message'] and self.attr in mc.listAttr(self.obj.nameLong, userDefined = True):

        if self.numeric and self.dynamic:
            if mc.attributeQuery(self.attr, node = self.obj.nameLong, minExists=True):
                try:
                    self.minValue =  mc.attributeQuery(self.attr, node = self.obj.nameLong, minimum=True)
                    #guiFactory.report("'%s.%s' minValue is %s" %(self.obj.nameLong,self.attr, self.minValue))
                except:
                    pass
                    
            if mc.attributeQuery(self.attr, node = self.obj.nameLong, maxExists=True):
                try:
                    self.maxValue =  mc.attributeQuery(self.attr, node = self.obj.nameLong, maximum=True)
                    #guiFactory.report("'%s.%s' maxValue is %s" %(self.obj.nameLong,self.attr, self.maxValue))
                except:
                    pass
                
            if type(mc.addAttr((self.obj.nameLong+'.'+self.attr),q=True,defaultValue = True)) is int or float:
                try:
                    self.defaultValue = mc.attributeQuery(self.attr, node = self.obj.nameLong, listDefault=True)
                    #guiFactory.report("'%s.%s' defaultValue is %s" %(self.obj.nameLong,self.attr, self.defaultValue))
                except:
                    pass
                
        if self.form == 'enum':
            self.enum = mc.addAttr((self.obj.nameLong+'.'+self.attr),q=True, en = True)
                
    
    def convert(self,attrType):
        """ 
        Converts an attribute type from one to another
        
        Keyword arguments:
        attrType(string)        
        """        
        try:
            attributes.convertAttrType(self.nameCombined,attrType)
            guiFactory.warning("'%s.%s' converted to '%s'"%(self.obj.nameLong,self.attr,attrType))
            
        except:
            guiFactory.warning("'%s.%s' failed to convert"%(self.obj.nameLong,self.attr))
            
            
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
            #guiFactory.report("'%s.%s' >> '%s'"%(self.obj.nameLong,self.attr,self.value))
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
            attributes.doDeleteAttr(self.obj.nameLong,self.attr)
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
            
            
            
    def setEnum(self,enumCommand):
        """ 
        Set the options for an enum attribute
        
        Keyword arguments:
        enumCommand(string) -- 'off:on', 'off=0:on=2', etc
        """   
        try:
            if self.form == 'enum':
                mc.addAttr ((self.obj.nameLong+'.'+self.attr), e = True, at=  'enum', en = enumCommand)
                guiFactory.report("'%s.%s' has been updated!"%(self.obj.nameLong,self.attr))
                
            else:
                guiFactory.warning("'%s.%s' is not an enum. Invalid call"%(self.obj.nameLong,self.attr))
            
        except:
            guiFactory.warning("'%s.%s' failed to change..."%(self.obj.nameLong,self.attr))
            
    def doStore(self,infoToStore,convertIfNecessary = True):
        """ 
        Set the options for an enum attribute
        
        Keyword arguments:
        enumCommand(string) -- 'off:on', 'off=0:on=2', etc
        """   
        try:
            if self.form == 'message':
                self.obj.store(self.attr,infoToStore)
            elif convertIfNecessary:
                self.convert('message')
                self.updateData()
                self.obj.store(self.attr,infoToStore)                
            
        except:
            guiFactory.warning("'%s.%s' failed to store '%s'"%(self.obj.nameLong,self.attr,infoToStore))
            
    def doDelete(self):
        """ 
        Set the options for an enum attribute
        
        Keyword arguments:
        enumCommand(string) -- 'off:on', 'off=0:on=2', etc
        """   
        try:
            mc.deleteAttr(self.nameCombined)            
            self.attr = False
        except:
            guiFactory.warning("'%s.%s' failed to store '%s'"%(self.obj.nameLong,self.attr,infoToStore))
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Set Options
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     
    def doDefault(self,value = None):
        if value is not None:
            try:
                mc.addAttr((self.obj.nameLong+'.'+self.attr),e=True,defaultValue = value)
                self.defaultValue = value
            except:
                guiFactory.warning("'%s.%s' failed to set a default value"%(self.obj.nameLong,self.attr))       
                
    def doMax(self,value = None):
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
                
                
    def doMin(self,value = None):
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
    
    def doLocked(self,arg = True):
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
                
    def doHidden(self,arg = True):
        if arg:
            if not self.hidden:
                if self.keyable:
                    self.doKeyable(False)
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,channelBox = False) 
                guiFactory.report("'%s.%s' hidden!"%(self.obj.nameLong,self.attr))
                self.hidden = True

                
        else:
            if self.hidden:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,channelBox = True)           
                guiFactory.report("'%s.%s' unhidden!"%(self.obj.nameLong,self.attr))
                self.hidden = False
                
                
    def doKeyable(self,arg = True):
        if arg:
            if not self.keyable:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,keyable = True) 
                guiFactory.report("'%s.%s' keyable!"%(self.obj.nameLong,self.attr))
                self.keyable = True
                self.hidden = False
                    
                
        else:
            if self.keyable:
                mc.setAttr((self.obj.nameLong+'.'+self.attr),e=True,keyable = False)           
                guiFactory.report("'%s.%s' unkeyable!"%(self.obj.nameLong,self.attr))
                self.keyable = False
                if not mc.getAttr(self.nameCombined,channelBox=True):
                    self.updateData()
                    self.doHidden(False)
                    
    def doAlias(self,arg):
        if arg:
            try:
                if arg != self.nameAlias:
                    if mc.aliasAttr(arg,self.nameCombined):
                        self.nameAlias = arg
                else:
                    guiFactory.report("'%s.%s' already has that alias!"%(self.obj.nameLong,self.attr,arg))
                    
            except:
                guiFactory.warning("'%s.%s' failed to set alias of '%s'!"%(self.obj.nameLong,self.attr,arg))
                    
        else:
            if self.nameAlias:
                self.attr = self.nameLong                
                mc.aliasAttr(self.nameCombined,remove=True)
                self.nameAlias = False
                self.updateData()
                
                
    def doNiceName(self,arg):
        if arg:
            try:
                mc.addAttr(self.nameCombined,edit = True, niceName = arg)
                self.nameNice = arg

            except:
                guiFactory.warning("'%s.%s' failed to set nice name of '%s'!"%(self.obj.nameLong,self.attr,arg))
                    

    def doRename(self,arg):
        assert type(arg) is str or unicode,"Must pass string argument into doRename"
        if arg:
            try:
                if arg != self.nameLong:
                    attributes.doRenameAttr(self.obj.nameLong,self.nameLong,arg)
                    self.attr = arg
                    self.updateData()
                    
                else:
                    guiFactory.report("'%s.%s' already has that nice name!"%(self.obj.nameLong,self.attr,arg))
                    
            except:
                guiFactory.warning("'%s.%s' failed to rename name of '%s'!"%(self.obj.nameLong,self.attr,arg))
                
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Connections and transfers
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>             
    def doConnectOut(self,target,*a, **kw):
        """ 
        Connect to a target
        
        Keyword arguments:
        *a, **kw
        """ 
        assert mc.objExists(target),"'%s' doesn't exist"%target
        
        if mc.ls(target,type = 'transform',long = True):
            #If the object has a transform
            if mc.objExists('%s.%s'%(target,self.attr)):
                #If it has a matching attribute
                try:
                    attributes.doConnectAttr(self.nameCombined,('%s.%s'%(target,self.attr)))
                except:
                    guiFactory.warning("'%s' failed to connect to '%s'!"%(self.nameCombined,target))
            else:
                print "Target object doesn't have this particular attribute"

        elif '.' in target:           
            try:
                attributes.doConnectAttr(self.nameCombined,target)
            except:
                guiFactory.warning("'%s' failed to connect to '%s'!"%(self.nameCombined,target))   
                
    def doConnectIn(self,source,*a, **kw):
        """ 
        Connect to a target
        
        Keyword arguments:
        *a, **kw
        """ 
        assert mc.objExists(source),"'%s' doesn't exist"%source
        
        if mc.ls(source,type = 'transform',long = True):
            #If the object has a transform
            if mc.objExists('%s.%s'%(source,self.attr)):
                #If it has a matching attribute
                try:
                    attributes.doConnectAttr(('%s.%s'%(source,self.attr)),self.nameCombined)
                except:
                    guiFactory.warning("'%s' failed to connect to '%s'!"%(source,self.nameCombined))
            else:
                print "Target object doesn't have this particular attribute"

        elif '.' in source:           
            try:
                attributes.doConnectAttr(source,self.nameCombined)
            except:
                guiFactory.warning("'%s' failed to connect to '%s'!"%(source,self.nameCombined))
                
    def doCopyTo(self,target,values = True, incomingConnections = False, outgoingConnections = False, keepSourceConnections = False):
        """ 
        Connect to a target
        
        Keyword arguments:
        *a, **kw
        """ 
        assert mc.objExists(target),"'%s' doesn't exist"%target
        assert mc.ls(target,type = 'transform',long = True),"'%s' Doesn't have a transform"%target
        
        if '.' in list(target):
            pass
        else:
            matchAttr = attributes.returnMatchAttrsDict(self.obj.nameLong,target,[self.nameLong])
        
            if not matchAttr:
                print "No match attr....making"
            
        
        attributes.copyAttrs(self.obj.nameLong,target,[self.nameLong], values, incomingConnections, outgoingConnections, keepSourceConnections)
        
        """except:
            guiFactory.warning("'%s' failed to copy to '%s'!"%(target,self.nameCombined))   """         
            
    def doTransferTo(self,target,deleteSelfWhenDone = False):
        """ 
        Connect to a target
        
        Keyword arguments:
        *a, **kw
        """ 
        assert mc.objExists(target),"'%s' doesn't exist"%target
        assert mc.ls(target,type = 'transform',long = True),"'%s' Doesn't have a transform"%target
        assert '.' not in list(target),"'%s' appears to be an attribute"%target
        
        target = AttrFactory(target,self.attr,self.form,self.value)
        
        attributes.copyAttrs(self.obj.nameLong,target.obj.nameLong,[target.attr])        
        
        if self.form == 'enum':
            target.setEnum(self.enum)
        if self.form == 'message':
            target.doStore(self.value)
        target.doHidden(self.hidden)
        target.doKeyable(self.keyable)        
        target.doLocked(self.locked)
        
        if deleteSelfWhenDone:
            self.doDelete()
        
        
        