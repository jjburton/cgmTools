#=========================================================================      
#Pupper requirements- We force the update on the Red9 internal registry  
# Puppet - network node
# >>
#=========================================================================         
from Red9.core import Red9_Meta as r9Meta
reload(r9Meta)
from Red9.core.Red9_Meta import *
r9Meta.registerMClassInheritanceMapping()    
#========================================================================

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.lib.classes import NameFactory
from cgm.lib.classes import AttrFactory
reload(AttrFactory)
from cgm.core.classes.AttrFactory import *

from cgm.core import cgmMeta
reload(cgmMeta)
from cgm.core.cgmMeta import *

from cgm.lib import (modules)

import random
import re
import copy
########################################################################
class cgmPuppet(cgmMetaNode):
    """"""
    #----------------------------------------------------------------------
    def __init__(self,*args,**kws):
        """Constructor"""
        #>>>Keyword args
        name = kws.pop('name',None)
        puppet = kws.pop('puppet',None)
        initializeOnly = kws.pop('initializeOnly',False)
        
        #characterType = kws.pop('characterType','')
        
        #Need a simple return of
        puppets = simplePuppetReturn()
        
        #>>> Fining the network node and name info from the provided information ==================                
        ##If a node is provided, check if it's a cgmPuppet
        ##If a name is provided, see if there's a puppet with that name, 
        ##If nothing is provided, just make one
        if name is not None:
            if puppets:##If we have puppets, check em
                for p in puppets:
                    if attributes.doGetAttr(p,'cgmName') == name:
                        log.info("Puppet tagged '%s' exists. Checking '%s'..."%(name,p))
                        puppet = p
                        name = attributes.doGetAttr(p,'cgmName')
                        break
        else:
            if args[0] and mc.objExists(args[0]):
                ##If we're here, there's a node named our master null.
                ##We need to get the network from that.
                log.info("Trying to find network from '%s'"%args[0])
                tmp = cgmMetaNode(args[0])
                if attributes.doGetAttr(tmp.mNode,'mClass') == 'cgmPuppet':#If it's a puppet network
                    puppet = args[0]
                else:
                    puppet = tmp.puppet[0]#If its a root
                name = tmp.cgmName
        
        if not name:
            name = search.returnRandomName()  
            
        super(cgmPuppet, self).__init__(node = puppet, name = name,**kws)  
            
        #>>> Puppet Network Initialization Procedure ==================       
        if self.refState or initializeOnly:
            log.info("'%s' Initializing only..."%name)
            raise NotImplementedError
            if not self.initialize():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%name)
                return     
            
        else:
            if not self.verify():
                log.critical("'%s' failed to verify!"%name)
                return      
            
        self.doStore('cgmName',name,True)
        
    def __bindData__(self):
        #Default to creation of a var as an int value of 0
        ### input check   
        pass     
        #self.addAttr('masterNull',type='messageSimple')        
        #self.addAttr('puppetGroup',type='messageSimple')
        #self.addAttr('modulesGroup',type='messageSimple')
        #self.addAttr('noTransformGroup',type='messageSimple')
        #self.addAttr('geoGroup',type='messageSimple')
        
    #==================================================================
    def verify(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """ 
        #>>> Puppet Network Node =====================================        
        if self.mClass != 'cgmPuppet':
            log.error("'%s' is not a puppet. It's mClass is '%s'"%(name,self.mClass))
        self.doName() #See if it's named properly. Need to loop back after scene stuff is querying properly
        
        self.doStore('cgmType','puppetNetwork')
        AttrFactory(self,'version',initialValue = 1.0)  
        AttrFactory(self,'masterNull',attrType = 'msg')  
        AttrFactory(self,'settings',attrType = 'msg')  
        AttrFactory(self,'geo',attrType = 'msg')  
        AttrFactory(self,'parts',attrType = 'msg')  

        self.doName()
        self.getAttrs()
        log.debug("Network good...")
        
        #>>> Nulls ==================================================     
        if self.masterNull and mc.objExists(self.masterNull[0]):#If we don't have a masterNull, make one
            log.info('Master null exists. Initializig')
            self.PuppetNull = cgmMasterNull(self.masterNull[0])
        else:
            log.info('Master created.')            
            self.PuppetNull = cgmMasterNull(puppet = self)
            self.doStore('masterNull',self.PuppetNull.mNode)               
                     
        if self.PuppetNull.mNode != self.cgmName:
            self.PuppetNull.doName(False)
        
        attributes.doSetLockHideKeyableAttr(self.PuppetNull.mNode,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        log.debug("Master Null good...")
        
        #>>> Info Nulls ==============================================
        
        #>> Settings 
        if 'settings' in self.__dict__.keys() and self.settings:
            log.info("Initializing '%s'"%self.settings[0])                                    
            self.Settings  = cgmInfoNode( attributes.returnMessageObject(self.mNode,'settings'))#Initialize if exists           
        else:
            log.info('Creating settings')                                    
            self.Settings = cgmInfoNode(puppet = self, infoType = 'settings')#Create and initialize
            self.doStore('settings',self.Settings.mNode)
        
        defaultFont = modules.returnSettingsData('defaultTextFont')
        self.Settings.doStore('font',defaultFont)
                
        AttrFactory(self.Settings,'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=2) 
        AttrFactory(self.Settings,'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=1) 
        AttrFactory(self.Settings,'axisOut','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=0)         
        
        #>> Geo
        if 'geo' in self.__dict__.keys() and self.geo:
            log.info("Initializing '%s'"%self.geo[0])                                    
            self.Geo  = cgmInfoNode( attributes.returnMessageObject(self.mNode,'geo'), infoType = 'geo')#Initialize if exists           
        else:
            log.info('Creating geo')                                    
            self.Geo = cgmInfoNode(puppet = self, infoType = 'geo')#Create and initialize
            self.doStore('geo',self.Geo.mNode)
            
        #>> Parts
        if 'parts' in self.__dict__.keys() and self.parts:
            log.info("Initializing '%s'"%self.parts[0])                                    
            self.Parts  = cgmInfoNode( attributes.returnMessageObject(self.mNode,'parts'), infoType = 'parts')#Initialize if exists           
        else:
            log.info('Creating parts')                                    
            self.Parts = cgmInfoNode(puppet = self, infoType = 'parts')#Create and initialize
            self.doStore('parts',self.Parts.mNode)   
        
        #>>> Groups  ==============================================
        created = False        
        self.msgNoTransformGroup = AttrFactory(self.PuppetNull,'noTransformGroup','message')
        if not self.msgNoTransformGroup.get():
            self.NoTransformGroup = ObjectFactory(mc.group(empty=True))
            self.msgNoTransformGroup.doStore(self.NoTransformGroup.nameShort)
            created = True
        else:
            self.NoTransformGroup = ObjectFactory(self.msgNoTransformGroup.get())
            
        self.NoTransformGroup.store('cgmName','noTransform')   
        self.NoTransformGroup.store('cgmType','group')
        
        self.NoTransformGroup.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.NoTransformGroup.doName(False)
            
        self.msgNoTransformGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.NoTransformGroup.nameShort)
         
            
        #Checks our geo container null
        created = False        
        self.msgGeoGroup = AttrFactory(self.PuppetNull,'geoGroup','message')
        if not self.msgGeoGroup.get():
            self.GeoGroup = ObjectFactory(mc.group(empty=True))
            self.msgGeoGroup.doStore(self.GeoGroup.nameShort)            
            created = True
        else:
            self.GeoGroup = ObjectFactory(self.msgGeoGroup.get())
            
        self.GeoGroup.store('cgmName','geo')   
        self.GeoGroup.store('cgmType','group')
        
        self.GeoGroup.doParent(self.msgNoTransformGroup.get())
        
        if created:
            self.GeoGroup.doName(False)
            
        self.msgGeoGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.GeoGroup.nameShort)        
        
            
        return True
            
    def changeName(self,name = ''):
        if name == self.cgmName:
            log.error("Puppet already named '%s'"%self.cgmName)
            return
        if name != '' and type(name) is str:
            log.warn("Changing name from '%s' to '%s'"%(self.cgmName,name))
            self.doStore('cgmName',name)
            self.verify()
            
            
class cgmMasterNull(cgmObject):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, *args,**kws):
        """Constructor"""
        #>>>Keyword args
        puppet = kws.pop('puppet',False)
        super(cgmMasterNull, self).__init__(*args,**kws)
        
        if puppet:
            self.doStore('cgmName',puppet.mNode+'.cgmName')
            self.doStore('puppet',puppet.mNode)
            
        self.verify()
        
    def verify(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """ 
        AttrFactory(self,'cgmName',initialValue = '')
        AttrFactory(self,'cgmType',initialValue = 'ignore')
        AttrFactory(self,'cgmModuleType',value = 'master')   
        
        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()
        
class cgmInfoNode(cgmMetaNode):
    """"""
    def __init__(self, *args,**kws):
        """Constructor"""
        puppet = kws.pop('puppet',False)#to pass a puppet instance in        
        infoType = kws.pop('infoType','settings')
        
        #>>>Keyword args
        super(cgmInfoNode, self).__init__(*args,**kws)
        
        if puppet:
            self.doStore('cgmName',puppet.mNode+'.cgmName')
        
        AttrFactory(self,'cgmName',initialValue = '')
        self.doStore('cgmTypeModifier',infoType)
        self.doStore('cgmType','info')     
        
        self.verify()
        
    def verify(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """ 
        
        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()

        
        
        
        
        
        
def simplePuppetReturn():
    catch = mc.ls(type='network')
    returnList = []
    if catch:
        for o in catch:
            if attributes.doGetAttr(o,'mClass') == 'cgmPuppet':
                returnList.append(o)
    return returnList
          