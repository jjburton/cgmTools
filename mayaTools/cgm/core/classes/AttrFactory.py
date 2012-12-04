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
import copy
from cgm.lib.classes import NameFactory
from cgm.core.cgmMeta import *

from cgm.lib import (search,
                     attributes,
                     dictionary,
                     guiFactory)
reload(attributes)
reload(guiFactory)
attrTypesDict = {'message':['message','msg','m'],
                 'double':['float','fl','f','doubleLinear','doubleAngle','double','d'],
                 'string':['string','s','str'],
                 'long':['long','int','i','integer'],
                 'bool':['bool','b','boolean'],
                 'enum':['enum','options','e'],
                 'double3':['vector','vec','v','double3','d3']}
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class AttrFactory():
    """ 
    Initialized a maya attribute as a class obj
    """
    def __init__(self,objName,attrName,attrType = False,value = None,enum = False,initialValue = None,lock = None,keyable = None, hidden = None, *a, **kw):
        """ 
        Asserts object's existance and that it has a transform. Then initializes. If 
        an existing attribute name on an object is called and the attribute type is different,it converts it. All functions
        ignore locks on attributes and will act when called regardless of target settings
        
        
        Keyword arguments:
        obj(string) -- must exist in scene or an cgmObject instance
        attrName(string) -- name for an attribute to initialize
        attrType(string) -- must be valid attribute type. If AttrFactory is imported, you can type 'print attrTypesDict'
        enum(string) -- default enum list to set on call or recall
        value() -- set value on call
        initialValue() -- only set on creation
        
        *a, **kw
        
        """
        ### input check
        try:
            #If we have an Object Factory instance, link it
            objName.mNode
            self.obj = objName
        except:
            #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
            assert mc.objExists(objName) is True, "'%s' doesn't exist" %objName
            self.obj = cgmObject(objName)
        
        self.form = attributes.validateRequestedAttrType(attrType)
        self.attr = attrName
        self.children = False
        initialCreate = False
        
        # If it exists we need to check the type. 
        if mc.objExists('%s.%s'%(self.obj.mNode,attrName)):
            currentType = mc.getAttr('%s.%s'%(self.obj.mNode,attrName),type=True)
            if not attributes.validateAttrTypeMatch(attrType,currentType) and self.form is not False:
                if self.obj.refState:
                    log.error("'%s' is referenced. cannot convert '%s' to '%s'!"%(self.obj.mNode,attrName,attrType))                   
                self.doConvert(attrType)             
                
            else:
                self.attr = attrName
                self.form = currentType
                
        else:
            try:
                if self.form == False:
                    self.form = 'string'
                    attributes.addStringAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                elif self.form == 'double':
                    attributes.addFloatAttributeToObject(self.obj.mNode,attrName,*a, **kw)
                elif self.form == 'string':
                    attributes.addStringAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                elif self.form == 'long':
                    attributes.addIntegerAttributeToObj(self.obj.mNode,attrName,*a, **kw) 
                elif self.form == 'double3':
                    attributes.addVectorAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                elif self.form == 'enum':
                    attributes.addEnumAttrToObj(self.obj.mNode,attrName,*a, **kw)
                elif self.form == 'bool':
                    attributes.addBoolAttrToObject(self.obj.mNode,attrName,*a, **kw)
                elif self.form == 'message':
                    attributes.addMessageAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                else:
                    log.error("'%s' is an unknown form to this class"%(self.form))
                
                initialCreate = True
                
            except:
                log.error("'%s.%s' failed to add"%(self.obj.mNode,attrName))
         
        self.updateData(*a, **kw)
            
        if enum:
            try:
                self.setEnum(enum)
            except:
                log.error("Failed to set enum value of '%s'"%enum)        

        if initialValue is not None and initialCreate:
            self.set(initialValue)
          
        elif value is not None:
            self.set(value)
        
        if type(keyable) is bool:
            self.doKeyable(keyable)   
            
        if type(hidden) is bool:
            self.doHidden(hidden)
            
        if type(lock) is bool:
            self.doLocked(lock)
                  

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def updateData(self,*a, **kw):
        """ 
        Get's attr updated data       
        """     
        assert mc.objExists('%s.%s'%(self.obj.mNode,self.attr)) is True, "'%s.%s' doesn't exist" %(self.obj.mNode,self.attr)
        # Default attrs
        self.nameCombined = '%s.%s'%(self.obj.mNode,self.attr)        
        self.minValue = False
        self.maxValue = False
        self.defaultValue = False
        self.nameNice = mc.attributeQuery(self.attr, node = self.obj.mNode, niceName = True)
        self.nameLong = mc.attributeQuery(self.attr, node = self.obj.mNode, longName = True)
        self.nameAlias = False
        if mc.aliasAttr(self.nameCombined,q=True):
            self.nameAlias = mc.aliasAttr(self.nameCombined,q=True)
            
        self.get(*a, **kw)
        
        #>>> Parent Stuff
        pBuffer = mc.attributeQuery(self.attr, node = self.obj.mNode, listParent=True)
        if pBuffer is None:
            self.parent = False
        else:
            self.parent = pBuffer[0]
        self.children = mc.attributeQuery(self.attr, node = self.obj.mNode, listChildren=True)
        if self.children is None:
            self.children = False        
        self.siblings = mc.attributeQuery(self.attr, node = self.obj.mNode, listSiblings=True)
        if self.siblings is None:
            self.siblings = False    
        self.enum = False
        
        self.userAttrs = mc.listAttr(self.obj.mNode, userDefined = True) or []
        
        standardFlagsBuffer = attributes.returnStandardAttrFlags(self.obj.mNode,self.nameLong)
        standardDataBuffer = attributes.returnAttributeDataDict(self.obj.mNode,self.nameLong)
        
        #Check connections
        self.driver = attributes.returnDriverAttribute(self.nameCombined,False)
        self.driven = attributes.returnDrivenAttribute(self.nameCombined,False)
        
        self.numeric = standardFlagsBuffer.get('numeric')
        self.dynamic = standardFlagsBuffer.get('dynamic')
            
        self.locked = standardFlagsBuffer.get('locked')
        self.keyable = standardFlagsBuffer.get('keyable')
        self.hidden = standardFlagsBuffer.get('hidden')
         
        
        if self.dynamic:
            self.readable = standardFlagsBuffer.get('readable')
            self.writable = standardFlagsBuffer.get('writable')
            self.storable = standardFlagsBuffer.get('storable')
            self.usedAsColor = standardFlagsBuffer.get('usedAsColor')   
            
        #>>> Numeric 
        if self.numeric:
            bufferDict = attributes.returnNumericAttrSettingsDict(self.obj.mNode,self.nameLong)
            if bufferDict:
                self.maxValue = bufferDict.get('max')
                self.minValue = bufferDict.get('min')
                self.defaultValue = bufferDict.get('default')
                self.softMaxValue = bufferDict.get('softMax')
                self.softMinValue = bufferDict.get('softMin')
                self.rangeValue = bufferDict.get('range')
                self.softRangeValue = bufferDict.get('softRange')
            else:
                self.maxValue = False
                self.minValue = False
                self.defaultValue = False
                self.softMaxValue = False
                self.softMinValue = False
                self.rangeValue = False
                self.softRangeValue = False               
                           
        if self.form == 'enum':
            self.enum = standardFlagsBuffer.get('enum')
                
    
    def doConvert(self,attrType):
        """ 
        Converts an attribute type from one to another while preserving as much data as possible.
        
        Keyword arguments:
        attrType(string)        
        """
        self.updateData()
        if self.obj.refState:
            log.error("'%s' is referenced. cannot convert '%s' to '%s'!"%(self.obj.mNode,self.attr,attrType))                           

        if self.children:
            log.error("'%s' has children, can't convert"%self.nameCombined)
        keyable = copy.copy(self.keyable)
        hidden =  copy.copy(self.hidden)
        locked =  copy.copy(self.locked)
        storedNumeric = False
        if self.numeric and not self.children:
            storedNumeric = True
            minimum =  copy.copy(self.minValue)
            maximum =  copy.copy(self.maxValue)
            default =  copy.copy(self.defaultValue)
            softMin =  copy.copy(self.softMinValue)
            softMax =  copy.copy(self.softMaxValue)
        
        attributes.doConvertAttrType(self.nameCombined,attrType)
        self.updateData()
        
        #>>> Reset variables
        self.doHidden(hidden)
        self.doKeyable(keyable)        
        self.doLocked(locked)

        if self.numeric and not self.children and storedNumeric:
            if softMin is not False or int(softMin) !=0 :
                self.doSoftMin(softMin)
            if softMax is not False or int(softMax) !=0 :
                self.doSoftMax(softMax)            
            if minimum is not False:
                self.doMin(minimum)
            if maximum is not False:
                self.doMax(maximum)
            if default is not False:
                self.doDefault(default)
            
        log.info("'%s.%s' converted to '%s'"%(self.obj.mNode,self.attr,attrType))
            
    
    def set(self,value,*a, **kw):
        """ 
        Set attr value based on attr type
        
        Keyword arguments:
        value(varied)   
        *a, **kw
        """
        try:
            if self.children:
                log.info("'%s' has children, running set command on '%s'"%(self.nameCombined,"','".join(self.children)))
                
                for i,c in enumerate(self.children):
                    try:
                        cInstance = AttrFactory(self.obj.mNode,c)                        
                        if type(value) is list and len(self.children) == len(value): #if we have the same length of values in our list as we have children, use them
                            attributes.doSetAttr(cInstance.obj.mNode,cInstance.attr, value[i], *a, **kw)
                            cInstance.value = value[i]
                            self.value = value
                        else:    
                            attributes.doSetAttr(cInstance.obj.mNode,cInstance.attr, value, *a, **kw)
                            self.value = value
                    except:
                        log.debug("'%s' failed to set"%c)
                        
            elif self.form == 'message':
                if value:
                    self.doStore(value)
            else:
                attributes.doSetAttr(self.obj.mNode,self.attr, value, *a, **kw)
                self.value = value
        
        except:
            log.error("'%s.%s' failed to set '%s'"%(self.obj.mNode,self.attr,value))
        
        
    def get(self,*a, **kw):
        """ 
        Get and store attribute value based on attr type
        
        Keyword arguments:
        *a, **kw
        """     
        try:
            if self.form == 'message':
                self.value = attributes.returnMessageObject(self.obj.mNode,self.attr)
            else:
                self.value =  attributes.doGetAttr(self.obj.mNode,self.attr)
            return self.value
        except:
            log.info("'%s.%s' failed to get"%(self.obj.mNode,self.attr))
            
            
    def getMessage(self,*a, **kw):
        """ 
        Get and store attribute value as if they were messages. Used for bufferFactory to use a connected
        attribute as a poor man's attribute message function
        
        Keyword arguments:
        *a, **kw
        """   
        try:
            if self.form == 'message':
                self.value = attributes.returnMessageObject(self.obj.mNode,self.attr)
                if search.returnObjectType(self.value) == 'reference':
                    if attributes.repairMessageToReferencedTarget(self.obj.mNode,self.attr,*a,**kw):
                        self.value = attributes.returnMessageObject(self.obj.mNode,self.attr)                        
            else:
                self.value = attributes.returnDriverAttribute("%s.%s"%(self.obj.mNode,self.attr))

            log.info("'%s.%s' >Message> '%s'"%(self.obj.mNode,self.attr,self.value))
            return self.value
            
        except:
            log.error("'%s.%s' failed to get"%(self.obj.mNode,self.attr))
            
            
            
    def setEnum(self,enumCommand):
        """ 
        Set the options for an enum attribute
        
        Keyword arguments:
        enumCommand(string) -- 'off:on', 'off=0:on=2', etc
        """   
        try:
            if self.form == 'enum':
                mc.addAttr ((self.obj.mNode+'.'+self.attr), e = True, at=  'enum', en = enumCommand)
                self.enum = enumCommand
                log.info("'%s.%s' has been updated!"%(self.obj.mNode,self.attr))
                
            else:
                log.warning("'%s.%s' is not an enum. Invalid call"%(self.obj.mNode,self.attr))
        except:
            log.error("'%s.%s' failed to change..."%(self.obj.mNode,self.attr))
            
    def doStore(self,infoToStore,convertIfNecessary = True):
        """ 
        Store information to an object. If the info exits as an object, it stores as a message node. Otherwise there are
        other storing methods.
        
        Keyword arguments:
        infoToStore(string) -- string of information to store
        convertIfNecessary(bool) -- whether to convert the attribute if it needs to to store it. Default (True)
        """   
        assert self.children is False,"This attribute has children. Can't store."
        try:
            if self.form == 'message':
                self.obj.store(self.attr,infoToStore)
                self.value = infoToStore
            elif convertIfNecessary:
                self.doConvert('message')
                self.updateData()
                self.obj.store(self.attr,infoToStore)                
                self.value = infoToStore
            
        except:
            log.error("'%s.%s' failed to store '%s'"%(self.obj.mNode,self.attr,infoToStore))
            
    def doDelete(self):
        """ 
        Deletes an attribute
        """   
        try:
            attributes.doDeleteAttr(self.obj.mNode,self.attr)
            log.warning("'%s.%s' deleted"%(self.obj.mNode,self.attr))
            self.value = None
            return self.value
        
        except:
            log.error("'%s.%s' failed to delete"%(self.obj.mNode,self.attr))  
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Set Options
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>                       
    def doDefault(self,value = None):
        """ 
        Set default settings of an attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """   
        if self.numeric: 
            if value is not None:
                if self.children:
                    log.warning("'%s' has children, running set command on '%s'"%(self.nameCombined,"','".join(self.children)))
                    for c in self.children:
                        cInstance = AttrFactory(self.obj.mNode,c)                        
                        try:
                            mc.addAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,defaultValue = value)
                            cInstance.defaultValue = value                                                        
                        except:
                            log.warning("'%s' failed to set a default value"%cInstance.nameCombined)                
                    self.defaultValue = value                            
                
                else:     
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,defaultValue = value)
                        self.defaultValue = value
                    except:
                        log.warning("'%s.%s' failed to set a default value"%(self.obj.mNode,self.attr))       
                
    def doMax(self,value = None):
        """ 
        Set max value for a numeric attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        if self.numeric and not self.children: 
            if value is False:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasMaxValue = value)
                    self.maxValue = value
                    log.warning("'%s.%s' had it's max value cleared"%(self.obj.mNode,self.attr))                     
                except:
                    log.error("'%s.%s' failed to clear a max value"%(self.obj.mNode,self.attr))  
            
            elif value is not None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,maxValue = value)
                    self.maxValue = value
                except:
                    log.error("'%s.%s' failed to set a max value"%(self.obj.mNode,self.attr))
                
                
    def doMin(self,value = None):
        """ 
        Set min value for a numeric attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        if self.numeric and not self.children: 
            if value is False:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasMinValue = value)
                    self.minValue = value
                    log.warning("'%s.%s' had it's min value cleared"%(self.obj.mNode,self.attr))                     
                except:
                    log.error("'%s.%s' failed to clear a min value"%(self.obj.mNode,self.attr))
            
            
            elif value is not None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,minValue = value)
                    self.minValue = value
                except:
                    log.warning("'%s.%s' failed to set a default value"%(self.obj.mNode,self.attr))
                    
    def doSoftMax(self,value = None):
        """ 
        Set soft max value for a numeric attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        if self.numeric and not self.children: 
            if value is False:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasSoftMaxValue = 0)
                    self.softMaxValue = value
                    log.warning("'%s.%s' had it's soft max value cleared"%(self.obj.mNode,self.attr))                     
                except:
                    log.error("'%s.%s' failed to clear a soft max value"%(self.obj.mNode,self.attr))  
            
            elif value is not None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,softMaxValue = value)
                    self.softMaxValue = value
                except:
                    log.error("'%s.%s' failed to set a soft max value"%(self.obj.mNode,self.attr))
                    
    def doSoftMin(self,value = None):
        """ 
        Set soft min value for a numeric attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        if self.numeric and not self.children: 
            if value is False:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasSoftMinValue = 0)
                    self.softMinValue = value
                    log.warning("'%s.%s' had it's soft max value cleared"%(self.obj.mNode,self.attr))                     
                except:
                    log.error("'%s.%s' failed to clear a soft max value"%(self.obj.mNode,self.attr))  
            
            elif value is not None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,softMinValue = value)
                    self.softMinValue = value
                except:
                    log.error("'%s.%s' failed to set a soft max value"%(self.obj.mNode,self.attr))
        
    def doLocked(self,arg = True):
        """ 
        Set lock state of an attribute
        
        Keyword arguments:
        arg(bool)
        """ 
        assert type(arg) is bool, "doLocked arg must be a bool!"
        if arg:
            if self.children:
                log.info("'%s' has children, running set command on '%s'"%(self.nameCombined,"','".join(self.children)))
                for c in self.children:
                    cInstance = AttrFactory(self.obj.mNode,c)                                            
                    if not cInstance.locked:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,lock = True) 
                        log.warning("'%s.%s' locked!"%(cInstance.obj.mNode,cInstance.attr))
                        cInstance.locked = True
                self.updateData()  
                
            elif not self.locked:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,lock = True) 
                log.warning("'%s.%s' locked!"%(self.obj.mNode,self.attr))
                self.locked = True
                
        else:
            if self.children:
                log.warning("'%s' has children, running set command on '%s'"%(self.nameCombined,"','".join(self.children)))
                for c in self.children:
                    cInstance = AttrFactory(self.obj.mNode,c)                                            
                    if cInstance.locked:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,lock = False) 
                        log.warning("'%s.%s' unlocked!"%(cInstance.obj.mNode,cInstance.attr))
                        cInstance.locked = False
                self.updateData()  
                
            elif self.locked:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,lock = False)           
                log.warning("'%s.%s' unlocked!"%(self.obj.mNode,self.attr))
                self.locked = False
                
    def doHidden(self,arg = True):
        """ 
        Set hidden state of an attribute
        
        Keyword arguments:
        arg(bool)
        """ 
        assert type(arg) is bool, "doLocked arg must be a bool!"        
        if arg:
            if self.children:
                log.warning("'%s' has children, running set command on '%s'"%(self.nameCombined,"','".join(self.children)))
                for c in self.children:
                    cInstance = AttrFactory(self.obj.mNode,c)                                            
                    if not cInstance.hidden:
                        if cInstance.keyable:
                            cInstance.doKeyable(False)
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,channelBox = False) 
                        log.info("'%s.%s' hidden!"%(cInstance.obj.mNode,cInstance.attr))
                        cInstance.hidden = False
                
            elif not self.hidden:
                if self.keyable:
                    self.doKeyable(False)
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,channelBox = False) 
                log.info("'%s.%s' hidden!"%(self.obj.mNode,self.attr))
                self.hidden = True

                
        else:
            if self.children:
                log.warning("'%s' has children, running set command on '%s'"%(self.nameCombined,"','".join(self.children)))
                for c in self.children:
                    cInstance = AttrFactory(self.obj.mNode,c)                                            
                    if cInstance.hidden:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,channelBox = True) 
                        log.info("'%s.%s' unhidden!"%(cInstance.obj.mNode,cInstance.attr))
                        cInstance.hidden = False
                
            elif self.hidden:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,channelBox = True)           
                log.info("'%s.%s' unhidden!"%(self.obj.mNode,self.attr))
                self.hidden = False
                
                
    def doKeyable(self,arg = True):
        """ 
        Set keyable state of an attribute
        
        Keyword arguments:
        arg(bool)
        """         
        assert type(arg) is bool, "doLocked arg must be a bool!"        
        if arg:
            if self.children:
                log.warning("'%s' has children, running set command on '%s'"%(self.nameCombined,"','".join(self.children)))
                for c in self.children:
                    cInstance = AttrFactory(self.obj.mNode,c)                                            
                    if not cInstance.keyable:
                        mc.setAttr(cInstance.nameCombined,e=True,keyable = True) 
                        log.info("'%s.%s' keyable!"%(cInstance.obj.mNode,cInstance.attr))
                        cInstance.keyable = True
                        cInstance.hidden = False

                
            elif not self.keyable:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,keyable = True) 
                log.info("'%s.%s' keyable!"%(self.obj.mNode,self.attr))
                self.keyable = True
                self.hidden = False
                    
                
        else:
            if self.children:
                log.warning("'%s' has children, running set command on '%s'"%(self.nameCombined,"','".join(self.children)))
                for c in self.children:
                    cInstance = AttrFactory(self.obj.mNode,c)                                            
                    if cInstance.keyable:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,keyable = False) 
                        log.info("'%s.%s' unkeyable!"%(cInstance.obj.mNode,cInstance.attr))
                        cInstance.keyable = False
                        if not mc.getAttr(cInstance.nameCombined,channelBox=True):
                            cInstance.updateData()
                            cInstance.doHidden(False)                
                
            elif self.keyable:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,keyable = False)           
                log.info("'%s.%s' unkeyable!"%(self.obj.mNode,self.attr))
                self.keyable = False
                if not mc.getAttr(self.nameCombined,channelBox=True):
                    self.updateData()
                    self.doHidden(False)
                    
    def doAlias(self,arg):
        """ 
        Set the alias of an attribute
        
        Keyword arguments:
        arg(string) -- name you want to use as an alias
        """     
        assert type(arg) is str or unicode,"Must pass string argument into doAlias"                
        if arg:
            try:
                if arg != self.nameAlias:
                    if mc.aliasAttr(arg,self.nameCombined):
                        self.nameAlias = arg
                else:
                    log.info("'%s.%s' already has that alias!"%(self.obj.mNode,self.attr,arg))
                    
            except:
                log.warning("'%s.%s' failed to set alias of '%s'!"%(self.obj.mNode,self.attr,arg))
                    
        else:
            if self.nameAlias:
                self.attr = self.nameLong                
                mc.aliasAttr(self.nameCombined,remove=True)
                self.nameAlias = False
                self.updateData()
                
                
    def doNiceName(self,arg):
        """ 
        Set the nice name of an attribute
        
        Keyword arguments:
        arg(string) -- name you want to use as a nice name
        """    
        assert type(arg) is str or unicode,"Must pass string argument into doNiceName"        
        if arg:
            try:
                mc.addAttr(self.nameCombined,edit = True, niceName = arg)
                self.nameNice = arg

            except:
                log.warning("'%s.%s' failed to set nice name of '%s'!"%(self.obj.mNode,self.attr,arg))
                    

    def doRename(self,arg):
        """ 
        Rename an attribute as something else
        
        Keyword arguments:
        arg(string) -- name you want to use as a nice name
        """            
        assert type(arg) is str or unicode,"Must pass string argument into doRename"
        if arg:
            try:
                if arg != self.nameLong:
                    attributes.doRenameAttr(self.obj.mNode,self.nameLong,arg)
                    self.attr = arg
                    self.updateData()
                    
                else:
                    log.info("'%s.%s' already has that nice name!"%(self.obj.mNode,self.attr,arg))
                    
            except:
                log.warning("'%s.%s' failed to rename name of '%s'!"%(self.obj.mNode,self.attr,arg))
                
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Connections and transfers
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def returnCompatibleFromTarget(self,target,*a, **kw):
        """ 
        Attempts to make a connection from instanced attribute to a target
        
        Keyword arguments:
        target(string) - object or attribute to connect to
        *a, **kw
        """ 
        assert mc.objExists(target),"'%s' doesn't exist"%target
        
        return attributes.returnCompatibleAttrs(self.obj.mNode,self.nameLong,target,*a, **kw)
        
            
    
    def doConnectOut(self,target,*a, **kw):
        """ 
        Attempts to make a connection from instanced attribute to a target
        
        Keyword arguments:
        target(string) - object or attribute to connect to
        *a, **kw
        """ 
        assert mc.objExists(target),"'%s' doesn't exist"%target
        
        if '.' in target:           
            try:
                attributes.doConnectAttr(self.nameCombined,target)
            except:
                log.warning("'%s' failed to connect to '%s'!"%(self.nameCombined,target))  
                
        else:
            #If the object has a transform
            matchAttr = attributes.returnMatchNameAttrsDict(self.obj.mNode,target,[self.nameLong]) or []
            if matchAttr:
                #If it has a matching attribute
                try:
                    attributes.doConnectAttr(self.nameCombined,('%s.%s'%(target,matchAttr.get(self.nameLong))))
                except:
                    log.warning("'%s' failed to connect to '%s'!"%(self.nameCombined,target))
            else:
                print "Target object doesn't have this particular attribute"

 
                
    def doConnectIn(self,source,*a, **kw):
        """ 
        Attempts to make a connection from a source to our instanced attribute
        
        Keyword arguments:
        source(string) - object or attribute to connect to
        *a, **kw
        """ 
        assert mc.objExists(source),"'%s' doesn't exist"%source
               
        if '.' in source:           
            try:
                attributes.doConnectAttr(source,self.nameCombined)
            except:
                log.warning("'%s' failed to connect to '%s'!"%(source,self.nameCombined))  
                
        else:
            #If the object has a transform
            matchAttr = attributes.returnMatchNameAttrsDict(self.obj.mNode,source,[self.nameLong]) or []
            if matchAttr:
                #If it has a matching attribute
                try:
                    attributes.doConnectAttr(('%s.%s'%(source,matchAttr.get(self.nameLong))),self.nameCombined)
                except:
                    log.warning("'%s' failed to connect to '%s'!"%(source,self.nameCombined))
            else:
                print "Source object doesn't have this particular attribute"
                
    def doCopyTo(self,target, targetAttrName = None,  debug = True,*a,**kw):
        """                                     
        Replacement for Maya's since maya's can't handle shapes....blrgh...
        Copy attributes from one object to another as well as other options. If the attribute already
        exists, it'll copy the values. If it doesn't, it'll make it. If it needs to convert, it can.
        It will not make toast.
    
        Keywords:
        toObject(string) - obj to copy to
        targetAttrName(string) -- name of the attr to copy to . Default is None which will create an 
                          attribute oft the fromAttr name on the toObject if it doesn't exist
        convertToMatch(bool) -- whether to convert if necessary.default True        
        values(bool) -- copy values. default True
        incomingConnections(bool) -- default False
        outGoingConnections(bool) -- default False
        keepSourceConnections(bool)-- keeps connections on source. default True
        copyAttrSettings(bool) -- copy the attribute state of the fromAttr (keyable,lock,hidden). default True
        connectSourceToTarget(bool) useful for moving attribute controls to another object. default False
        
        RETURNS:
        success(bool)
        """
        assert mc.objExists(target),"'%s' doesn't exist"%target
        assert mc.ls(target,long=True) != [self.obj.mNode], "Can't transfer to self!"
        functionName = 'doCopyTo'
        
        convertToMatch = kw.pop('convertToMatch',True)
        values = kw.pop('values',True)
        incomingConnections = kw.pop('incomingConnections',False)
        outgoingConnections = kw.pop('outgoingConnections',False)
        keepSourceConnections = kw.pop('keepSourceConnections',True)
        copyAttrSettings = kw.pop('copyAttrSettings',True)
        connectSourceToTarget = kw.pop('connectSourceToTarget',False)
        connectTargetToSource = kw.pop('connectTargetToSource',False)  
        
        if debug:
            guiFactory.doPrintReportStart(functionName)
            log.info("AttrFactory instance: '%s'"%self.nameCombined)
            log.info("convertToMatch: '%s'"%convertToMatch)
            log.info("targetAttrName: '%s'"%targetAttrName)
            log.info("incomingConnections: '%s'"%incomingConnections)
            log.info("outgoingConnections: '%s'"%outgoingConnections)
            log.info("keepSourceConnections: '%s'"%keepSourceConnections)
            log.info("copyAttrSettings: '%s'"%copyAttrSettings)
            log.info("connectSourceToTarget: '%s'"%connectSourceToTarget)
            log.info("keepSourceConnections: '%s'"%keepSourceConnections)
            log.info("connectTargetToSource: '%s'"%connectTargetToSource)
            guiFactory.doPrintReportBreak()
            

                
        copyTest = [values,incomingConnections,outgoingConnections,keepSourceConnections,connectSourceToTarget,copyAttrSettings]
        
        if sum(copyTest) < 1:
            log.warning("You must have at least one option for copying selected. Otherwise, you're looking for the 'doDuplicate' function.")            
            return False

        if '.' in list(target):
            targetBuffer = target.split('.')
            if len(targetBuffer) == 2:
                attributes.doCopyAttr(self.obj.mNode,
                                      self.nameLong,
                                      targetBuffer[0],
                                      targetBuffer[1],
                                      convertToMatch = convertToMatch,
                                      values=values, incomingConnections = incomingConnections,
                                      outgoingConnections=outgoingConnections, keepSourceConnections = keepSourceConnections,
                                      copyAttrSettings = copyAttrSettings, connectSourceToTarget = connectSourceToTarget)               

            else:
                log.warning("Yeah, not sure what to do with this. Need an attribute call with only one '.'")
        else:
            attributes.doCopyAttr(self.obj.mNode,
                                  self.nameLong,
                                  target,
                                  targetAttrName,
                                  convertToMatch = convertToMatch,
                                  values=values, incomingConnections = incomingConnections,
                                  outgoingConnections=outgoingConnections, keepSourceConnections = keepSourceConnections,
                                  copyAttrSettings = copyAttrSettings, connectSourceToTarget = connectSourceToTarget)                                                 
        if debug:
            guiFactory.doPrintReportEnd(functionName)        
        #except:
        #    log.warning("'%s' failed to copy to '%s'!"%(target,self.nameCombined))          
            
    def doTransferTo(self,target):
        """ 
        Transfer an instanced attribute to a target with all settings and connections intact
        
        Keyword arguments:
        target(string) -- object to transfer it to
        *a, **kw
        """ 
        assert mc.objExists(target),"'%s' doesn't exist"%target
        assert mc.ls(target,type = 'transform',long = True),"'%s' Doesn't have a transform"%target
        assert self.obj.transform is not False,"'%s' Doesn't have a transform. Transferring this attribute is probably a bad idea. Might we suggest doCopyTo along with a connect to source option"%self.obj.mNode        
        assert mc.ls(target,long=True) != [self.obj.mNode], "Can't transfer to self!"
        assert '.' not in list(target),"'%s' appears to be an attribute. Can't transfer to an attribute."%target
        assert self.dynamic is True,"'%s' is not a dynamic attribute."%self.nameCombined
        
        #mc.copyAttr(self.obj.mNode,self.target.obj.mNode,attribute = [self.target.attr],v = True,ic=True,oc=True,keepSourceConnections=True)
        attributes.doCopyAttr(self.obj.mNode,
                              self.nameLong,
                              target,
                              self.nameLong,
                              convertToMatch = True,
                              values = True, incomingConnections = True,
                              outgoingConnections = True, keepSourceConnections = False,
                              copyAttrSettings = True, connectSourceToTarget = False)
        self.doDelete()

            

        
        