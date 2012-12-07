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

from cgm.core import cgmMeta
reload(cgmMeta)
from cgm.core.cgmMeta import *

from cgm.lib import (modules)

import random
import re
import copy
import time

#Initial settings to setup
#==============    
initLists = ['modules','rootModules','orderedModules','orderedParentModules','nodes']
initDicts = ['Module','moduleParents','moduleChildren','moduleStates']
initStores = []

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
        
        start = time.clock()
              
        #Need a simple return of
        puppets = simplePuppetReturn()
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Finding the network node and name info from the provided information
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>          
        ##If a node is provided, check if it's a cgmPuppet
        ##If a name is provided, see if there's a puppet with that name, 
        ##If nothing is provided, just make one
        if name is not None:
            if puppets:##If we have puppets, check em
                log.debug("Found the following puppets: '%s'"%"','".join(puppets))
                for p in puppets:
                    if attributes.doGetAttr(p,'cgmName') == name:
                        log.info("Puppet tagged '%s' exists. Checking '%s'..."%(name,p))
                        puppet = p
                        name = attributes.doGetAttr(p,'cgmName')
                        break
        else:
            if args and args[0] and mc.objExists(args[0]):
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
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Verify or Initialize
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>           
        log.info("Puppet is '%s'"%name)
        super(cgmPuppet, self).__init__(node = puppet, name = name,**kws)  
        self.doStore('cgmName',name,True)
            
        #>>> Puppet Network Initialization Procedure ==================       
        if self.refState or initializeOnly:
            log.info("'%s' Initializing only..."%name)
            if not self.initialize():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%name)
                return          
        else:
            if not self.verify():
                log.critical("'%s' failed to verify!"%name)
                return  
            
        log.info("'%s' Checks out!"%name)
        log.info('Time taken =  %0.3f' % (time.clock()-start))
        
        
    def __bindData__(self):
        #Default to creation of a var as an int value of 0
        ### input check   
        pass     
        #self.addAttr('masterNull',type='messageSimple')        
        #self.addAttr('puppetGroup',type='messageSimple')
        #self.addAttr('modulesGroup',type='messageSimple')
        #self.addAttr('noTransformGroup',type='messageSimple')
        #self.addAttr('geoGroup',type='messageSimple')
        
    #====================================================================================
    def initialize(self):
        """ 
        Initializes the various components a masterNull for a character/asset.
        
        RETURNS:
        success(bool)
        """  
        #>>>Setup variables
        for l in initLists:
            self.__dict__[l+'_list'] = []
        for d in initDicts:
            self.__dict__[d+'_dict'] = {}
        for o in initStores:
            self.__dict__[o+'_stored_'] = False  
            
        #Puppet Network Node
        #==============
        if self.mClass != 'cgmPuppet':
            return False    
        
        #>>>Master null
        if self.masterNull:
            self.PuppetNull = cgmObject(self.masterNull[0])
            log.info("'%s' initialized as master null"%self.masterNull[0])
        else:
            log.error("MasterNull missing. Go back to unreferenced file")
            return False
        
        #>>>Info Nulls
        ## Initialize the info nodes
        for attr in 'settings','geo','parts':
            if attr in  self.__dict__.keys():
                try:
                    Attr = attr[0].capitalize() + attr[1:]#Get a better attribute store string, capitalize doesn't maintain mixed case 'noTransform'                  
                    self.__dict__[Attr] = cgmMetaNode( self.__getattribute__(attr)[0] )
                    log.info("'%s' initialized as %s info null"%(self.__getattribute__(attr)[0],attr))                    
                except:
                    log.error("'%s' info node failed. Please verify puppet."%attr)                    
                    return False
        
                self.optionPuppetMode = AttrFactory(self.SettingsInfoNull,'optionPuppetTemplateMode','int',initialValue = 0)      
        
        self.optionAimAxis= cgmAttr(self.Settings,'axisAim') 
        self.optionUpAxis= cgmAttr(self.Settings,'axisUp') 
        self.optionOutAxis= cgmAttr(self.Settings,'axisOut')  
        
        
        #>>>Groups 
        ## Initialize the info nodes
        for attr in 'partsGroup','noTransformGroup','geoGroup':
            if attr in self.PuppetNull.__dict__.keys():
                try:
                    Attr = str(attr[0].capitalize() + attr[1:])#Get a better attribute store string
                    self.__dict__[Attr] = cgmObject( self.PuppetNull.__getattribute__(attr)[0] )
                    log.info("'%s' initialized to 'self.%s'"%(self.PuppetNull.__getattribute__(attr)[0],Attr))                    
                except:
                    log.error("'%s' info node failed. Please verify puppet."%attr)                    
                    return False

                
        return True
    
    def verify(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """ 
        #>>>Setup variables
        for l in initLists:
            self.__dict__['list_'+l] = []
        for d in initDicts:
            self.__dict__['dict_'+d] = {}
        for o in initStores:
            self.__dict__['stored_'+o] = False  
            
        #Puppet Network Node
        #==============    
        if attributes.doGetAttr(self.mNode,'mClass') != 'cgmPuppet':
            log.error("'%s' is not a puppet. It's mClass is '%s'"%(self.mNode, attributes.doGetAttr(self.mNode,'mClass')))
            return False
        self.doName() #See if it's named properly. Need to loop back after scene stuff is querying properly
        
        self.doStore('cgmType','puppetNetwork')
        self.addAttr('version',initialValue = 1.0, lock=True)  
        self.addAttr('masterNull',attrType = 'msg')  
        self.addAttr('settings',attrType = 'msg')  
        self.addAttr('geo',attrType = 'msg')  
        self.addAttr('parts',attrType = 'msg')  

        self.doName()
        self.getAttrs()
        log.debug("Network good...")

        
        #MasterNull
        #==============   
        if mc.objExists(attributes.returnMessageObject(self.mNode,'masterNull')):#If we don't have a masterNull, make one
            log.info('Master null exists. Initializing')
            self.PuppetNull = cgmMasterNull(self.masterNull[0])
        else:
            self.PuppetNull = cgmMasterNull(puppet = self)
            self.doStore('masterNull',self.PuppetNull.mNode)               
            log.info('Master created.')            
                     
        if self.PuppetNull.mNode != self.cgmName:
            self.PuppetNull.doName(False)
        
        attributes.doSetLockHideKeyableAttr(self.PuppetNull.mNode,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        log.debug("Master Null good...")
        
    
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Info Nodes
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>             
        
        #Settings
        #==============
        if mc.objExists( attributes.returnMessageObject(self.mNode,'settings') ):
            log.info("Initializing '%s'"%self.settings[0])                                    
            self.Settings  = cgmInfoNode( attributes.returnMessageObject(self.mNode,'settings'))#Initialize if exists           
        else:
            log.info('Creating settings')                                    
            self.Settings = cgmInfoNode(puppet = self, infoType = 'settings')#Create and initialize
            self.doStore('settings',self.Settings.mNode)
        
        defaultFont = modules.returnSettingsData('defaultTextFont')
        self.Settings.doStore('font',defaultFont)
        
        cgmAttr(self.Settings,'puppetType','int',initialValue=0,lock=True)   
        cgmAttr(self.Settings,'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=2) 
        cgmAttr(self.Settings,'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=1) 
        cgmAttr(self.Settings,'axisOut','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=0) 
        
        
        #Geo
        #==============
        if mc.objExists( attributes.returnMessageObject(self.mNode,'geo') ):
            log.info("Initializing '%s'"%self.geo[0])                                    
            self.Geo  = cgmInfoNode( attributes.returnMessageObject(self.mNode,'geo'), infoType = 'geo')#Initialize if exists           
        else:
            log.info('Creating geo')                                    
            self.Geo = cgmInfoNode(puppet = self, infoType = 'geo')#Create and initialize
            self.doStore('geo',self.Geo.mNode)
            
        #Parts
        #==============
        if mc.objExists( attributes.returnMessageObject(self.mNode,'parts') ):
            log.info("Initializing '%s'"%self.parts[0])                                    
            self.Parts  = cgmInfoNode( attributes.returnMessageObject(self.mNode,'parts'), infoType = 'parts')#Initialize if exists           
        else:
            log.info('Creating parts')                                    
            self.Parts = cgmInfoNode(puppet = self, infoType = 'parts')#Create and initialize
            self.doStore('parts',self.Parts.mNode)   
            
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Groups
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
        for attr in 'noTransform','geo','parts':
            grp = attributes.returnMessageObject(self.PuppetNull.mNode,attr+'Group')# Find the group
            Attr = str(attr[0].capitalize() + attr[1:]+'Group')#Get a better attribute store string           
            if mc.objExists( grp ):
                #If exists, initialize it
                try:     
                    self.__dict__[Attr]  = cgmObject(grp)#Initialize if exists           
                    log.info("'%s' initialized to 'self.%s'"%(grp,Attr))                    
                except:
                    log.error("'%s' group failed. Please verify puppet."%attr)                    
                    return False   
                
            else:#Make it
                log.info('Creating %s'%attr)                                    
                self.__dict__[Attr]= cgmObject(name=attr)#Create and initialize
                self.__dict__[Attr].doName()
                self.PuppetNull.doStore(attr+'Group', self.__dict__[Attr].mNode) 
                log.info("'%s' initialized to 'self.%s'"%(grp,Attr))                    
                
           
            # Few Case things
            #==============            
            if attr == 'geo':
                self.__dict__[Attr].doParent(self.NoTransformGroup)
            else:    
                self.__dict__[Attr].doParent(self.PuppetNull)
        
            attributes.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode )
        
        return True
            
    def changeName(self,name = ''):
        if name == self.cgmName:
            log.error("Puppet already named '%s'"%self.cgmName)
            return
        if name != '' and type(name) is str:
            log.warn("Changing name from '%s' to '%s'"%(self.cgmName,name))
            self.doStore('cgmName',name)
            self.verify()
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Puppet Utilities
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>             
    def tracePuppet(self):
        pass #Do this later.Trace a puppet to be able to fully delete everything.
        #self.nodes_list.append()
            
    def delete(self):
        """
        Delete the Puppet
        """
        mc.delete(self.PuppetNull.mNode)
        mc.delete(self.mNode)        
        del(self.PuppetNull)
        del(self)
        
    def getState(self):
        """
        Return a Puppet's state
        
        Returns:
        state/False -- (int)/(bool)
        """
        checkList = []
        if self.getModuleStates() is False:
            return False
        for k in self.moduleStates.keys():
            checkList.append(self.moduleStates[k])
        return min(checkList) 
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Module Utilities
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>       
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Special objects
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>           
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
        cgmAttr(self,'cgmName',initialValue = '')
        cgmAttr(self,'cgmType',initialValue = 'ignore')
        cgmAttr(self,'cgmModuleType',value = 'master')   
        cgmAttr(self,'partsGroup',attrType = 'msg')   
        cgmAttr(self,'noTransformGroup',attrType = 'msg')   
        cgmAttr(self,'geoGroup',attrType = 'msg')   
        
        
        
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
        
        cgmAttr(self,'cgmName',initialValue = '')
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
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        
def simplePuppetReturn():
    catch = mc.ls(type='network')
    returnList = []
    if catch:
        for o in catch:
            if attributes.doGetAttr(o,'mClass') == 'cgmPuppet':
                returnList.append(o)
    return returnList
          