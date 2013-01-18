"""
------------------------------------------
cgm_PuppetMeta: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is the core MetaClass structure for cgm's modular rigger.
================================================================
"""
import maya.cmds as mc

import random
import re
import copy
import time

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

# From cgm ==============================================================
from cgm.lib.classes import NameFactory
from cgm.core.rigger import ModuleFactory as mFactory
reload(mFactory)
from cgm.core.rigger import PuppetFactory as pFactory
reload(pFactory)

from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (modules,attributes,search)

cgmModuleTypes = ['cgmModule','cgmLimb']
########################################################################
class cgmPuppet(cgmMeta.cgmNode):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, node = None, name = None, initializeOnly = False, *args,**kws):
        log.info(">>> cgmPuppet.__init__")
        if kws:log.info("kws: %s"%str(kws))
        if args:log.info("args: %s"%str(args))
        
        """Constructor"""
        #>>>Keyword args
        puppet = kws.pop('puppet',None)

        start = time.clock()

        #Need a simple return of
        puppets = pFactory.simplePuppetReturn()

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Finding the network node and name info from the provided information
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>          
        ##If a node is provided, check if it's a cgmPuppet
        ##If a name is provided, see if there's a puppet with that name, 
        ##If nothing is provided, just make one
        if node is None and name is None and args:
            log.info("Checking '%s'"%args[0])
            node = args[0]

        if puppets:#If we have puppets, check em
            log.info("Found the following puppets: '%s'"%"','".join(puppets))            
            if name is not None or node is not None:    
                if node is not None and node in puppets:
                    puppet = node
                    name = attributes.doGetAttr(node,'cgmName')
                else:
                    for p in puppets:
                        if attributes.doGetAttr(p,'cgmName') in [node,name]:
                            log.info("Puppet tagged '%s' exists. Checking '%s'..."%(attributes.doGetAttr(p,'cgmName'),p))
                            puppet = p
                            name = attributes.doGetAttr(p,'cgmName')
                            break

        """
        if puppet == None:#If we still don't have a puppet
            if args and args[0]:
                log.info("Checking args")
                if mc.objExists(args[0]):
                    ##If we're here, there's a node named our master null.
                    ##We need to get the network from that.
                    log.info("Trying to find network from '%s'"%args[0])
                    tmp = r9Meta.MetaClass(args[0])
                    if attributes.doGetAttr(tmp.mNode,'mClass') == 'cgmPuppet':#If it's a puppet network
                        puppet = args[0]
                    else:
                        puppet = tmp.puppet.mNode#If its a root
                    name = tmp.cgmName
                else:
                    log.info("Not Puppet object found, creating '%s'"%args[0])
                    puppet = None
                    name = args[0]   
                    """

        if not name:
            log.warning("No puppet name found")
            name = search.returnRandomName()  

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Verify or Initialize
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>           
        log.info("Puppet is '%s'"%name)
        super(cgmPuppet, self).__init__(node = puppet, name = name) 

        #>>> Puppet Network Initialization Procedure ==================       
        if self.isReferenced() or initializeOnly:
            log.info("'%s' Initializing only..."%name)
            if not self.initialize():
                #log.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%name)
                raise StandardError,"'%s' failed to initialize. Please go back to the non referenced file to repair!"%name
        else:
            if not self.verify(name):
                #log.critical("'%s' failed to verify!"%name)
                raise StandardError,"'%s' failed to verify!"%name

        log.info("'%s' Checks out!"%name)
        log.info('Time taken =  %0.3f' % (time.clock()-start))


    #====================================================================================
    def initialize(self,name = ''):
        """ 
        Initializes the various components a masterNull for a character/asset.

        RETURNS:
        success(bool)
        """  
        #Puppet Network Node
        #==============
        if self.mClass != 'cgmPuppet':
            return False  
        
        return True

        #>>>Master null
        if self.getMessage('masterNull'):
            self.i_masterNull = self.masterNull#link it
            log.info("'%s' initialized as master null"%self.masterNull.mNode)
        else:
            log.error("MasterNull missing. Go back to unreferenced file")
            return False
        #>>>Info Nulls
        ## Initialize the info nodes
        for attr in 'settings','geo':
            if attr in  self.__dict__.keys():
                try:
                    Attr = 'i_'+ attr
                    buffer = self.getMessage(attr)[0]                    
                    self.__dict__[Attr] = cgmMeta.cgmMetaFactory( buffer )
                    log.info("'%s' initialized as self.%s"%(buffer,Attr))                    
                except:
                    log.error("'%s' info node failed. Please verify puppet."%attr)                    
                    return False

        #>>>Groups 
        ## Initialize the info nodes
        for attr in 'deformGroup','partsGroup','noTransformGroup','geoGroup':
            if attr in self.i_masterNull.__dict__.keys():
                try:
                    Attr = 'i_'+ attr
                    buffer = self.i_masterNull.getMessage(attr)[0]                                        
                    self.__dict__[Attr] = cgmMeta.cgmMetaFactory( buffer )
                    log.info("'%s' initialized as 'self.%s'"%(buffer,Attr))                    
                except:
                    log.error("'%s' info node failed. Please verify puppet."%attr)                    
                    return False


        return True

    def verify(self,name = ''):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """             
        #Puppet Network Node
        #============== 
        self.addAttr('mClass', initialValue='cgmPuppet',lock=True)  
        self.doStore('cgmName',name,True)
        
        if attributes.doGetAttr(self.mNode,'mClass') != 'cgmPuppet':
            log.error("'%s' is not a puppet. It's mClass is '%s'"%(self.mNode, attributes.doGetAttr(self.mNode,'mClass')))
            return False
        self.doName() #See if it's named properly. Need to loop back after scene stuff is querying properly

        self.addAttr('cgmType','puppetNetwork')
        self.addAttr('version',initialValue = 1.0, lock=True)  
        self.addAttr('masterNull',attrType = 'messageSimple',lock=True)  
        self.addAttr('settings',attrType = 'messageSimple',lock=True)  
        self.addAttr('geo',attrType = 'messageSimple',lock=True)  
        self.addAttr('moduleChildren',attrType = 'message',lock=True)  

        self.doName()
        self.getAttrs()
        log.debug("Network good...")

        #MasterNull
        #==============   
        if not mc.objExists(attributes.returnMessageObject(self.mNode,'masterNull')):#If we don't have a masterNull, make one
            self.i_masterNull = cgmMasterNull(puppet = self)
            #self.connectChild(self.i_masterNull.mNode, 'masterNull','puppet')               
            log.info('Master created.')
        else:
            log.info('Master null exists. linking....')            
            self.i_masterNull = self.masterNull#Linking to instance for faster processing. Good idea?

        if self.i_masterNull.getShortName() != self.cgmName:
            self.i_masterNull.doName(False)
            if self.i_masterNull.getShortName() != self.cgmName:
                log.warning("Master Null name still doesn't match what it should be.")
                return False
        attributes.doSetLockHideKeyableAttr(self.masterNull.mNode,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        log.debug("Master Null good...")

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Info Nodes
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>             

        #Settings
        #==============
        if not mc.objExists( attributes.returnMessageObject(self.mNode,'settings') ):
            log.info('Creating settings')                                    
            self.i_settings = cgmInfoNode(puppet = self, infoType = 'settings')#Create and initialize
        else:
            log.info('settings infoNode exists. linking....')                        
            self.i_settings = self.settings #Linking to instance for faster processing. Good idea?

        defaultFont = modules.returnSettingsData('defaultTextFont')

        self.i_settings.addAttr('font',attrType = 'string',initialValue=defaultFont,lock=True)   
        self.i_settings.addAttr('puppetType',attrType = 'int',initialValue=0,lock=True)
        self.i_settings.addAttr('axisAim',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=2) 
        self.i_settings.addAttr('axisUp',enumName = 'x+:y+:z+:x-:y-:z-', attrType = 'enum',initialValue=1) 
        self.i_settings.addAttr('axisOut',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=0) 

        #Geo
        #==============
        if mc.objExists( attributes.returnMessageObject(self.mNode,'geo') ):
            log.info('geo infoNode exists. linking....')                        
            self.i_geo  = self.geo #Linking to instance for faster processing. Good idea?         
        else:
            log.info('Creating geo')                                    
            self.i_geo = cgmInfoNode(puppet = self, infoType = 'geo')#Create and initialize

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Groups
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
        for attr in 'deform','noTransform','geo','parts':
            grp = attributes.returnMessageObject(self.i_masterNull.mNode,attr+'Group')# Find the group
            Attr = 'i_' + attr+'Group'#Get a better attribute store string           
            if mc.objExists( grp ):
                #If exists, initialize it
                #self.__dict__[Attr]  = self.i_masterNull.__dict__[attr+'Group']#link it, can't link it
                self.__dict__[Attr]  = r9Meta.MetaClass(grp)#initialize
                log.info("'%s' initialized as 'self.%s'"%(grp,Attr))
                log.info(self.__dict__[Attr].mNode)
                #except:
                    #log.error("'%s' group failed. Please verify puppet."%attr)                    
                    #return False   

            else:#Make it
                log.info('Creating %s'%attr)                                    
                self.__dict__[Attr]= cgmMeta.cgmObject(name=attr)#Create and initialize
                self.__dict__[Attr].doName()
                self.i_masterNull.connectChild(self.__dict__[Attr].mNode, attr+'Group','puppet') #Connect the child to the holder
                log.info("Initialized as 'self.%s'"%(Attr))                    

            # Few Case things
            #==============            
            if attr == 'geo':
                self.__dict__[Attr].doParent(self.i_noTransformGroup)
            else:    
                self.__dict__[Attr].doParent(self.i_masterNull)

            attributes.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode )

        return True

    def changeName(self,name = ''):
        if name == self.cgmName:
            log.error("Puppet already named '%s'"%self.cgmName)
            return
        if name != '' and type(name) is str:
            log.warn("Changing name from '%s' to '%s'"%(self.cgmName,name))
            self.cgmName = name
            self.verify()

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Puppet Utilities
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>             
    def tracePuppet(self):
        pass #Do this later.Trace a puppet to be able to fully delete everything.
        #self.nodes_list.append()
        raise NotImplementedError

    def delete(self):
        """
        Delete the Puppet
        """
        mc.delete(self.i_masterNull.mNode)
        mc.delete(self.i_geo.mNode)
        mc.delete(self.i_parts.mNode)
        mc.delete(self.i_settings.mNode)
        del(self)

    def addModule(self,mClass = 'cgmModule',**kws):
        """
        Create and connect a new module
        
        moduleType(string) - type of module to create
        """   
        if mClass == 'cgmModule':
            tmpModule = cgmModule(**kws)   
        elif mClass == 'cgmLimb':
            tmpModule = cgmLimb(**kws)
        else:
            log.warning("'%s' is not a known module type. Cannot initialize"%mClass)
            return False
        
        self.connectModule(tmpModule)

    @r9General.Timer
    def connectModule(self,module,force = True,**kws):
        """
        Connects a module to a puppet

        module(string)
        """
        #See if it's connected
        #If exists, connect
        #Get instance
        #==============	
        buffer = copy.copy(self.moduleChildren) or []#Buffer till we have have append functionality	

        try:
            module.mNode#see if we have an instance
            if module.mNode in buffer and force != True:
                log.warning("'%s' already connnected to '%s'"%(module.getShortName(),self.i_masterNull.getShortName()))
                return False 	    
        except:
            if mc.objExists(module):
                if mc.ls(module,long=True)[0] in buffer and force != True:
                    log.warning("'%s' already connnected to '%s'"%(module,self.i_masterNull.getShortName()))
                    return False

                module = r9Meta.MetaClass(module)#initialize

            else:
                log.warning("'%s' doesn't exist"%module)#if it doesn't initialize, nothing is there		
                return False	

        #Logic checks
        #==============	
        if not module.hasAttr('mClass'):
            log.warning("'%s' lacks an mClass attr"%module.mNode)	    
            return False

        elif module.mClass not in cgmModuleTypes:
            log.warning("'%s' is not a recognized module type"%module.mClass)
            return False

        #Connect
        #==============	
        else:
            log.info("Current children: %s"%buffer)
            log.info("Adding '%s'!"%module.getShortName())    

            buffer.append(module.mNode)
            del self.moduleChildren
            self.connectChildren(buffer,'moduleChildren','moduleParent',force=force)#Connect
            module.__setMessageAttr__('modulePuppet',self.mNode)#Connect puppet to 

        #module.parent = self.i_partsGroup.mNode
        module.doParent(self.i_partsGroup.mNode)

        return True
    def getGeo(self):
        return pFactory.getGeo(self)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Special objects
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>           
class cgmMasterNull(cgmMeta.cgmObject):
    """"""
    #----------------------------------------------------------------------
    def __init__(self,node = None, name = 'master',*args,**kws):
        """Constructor"""
        #>>>Keyword args
        puppet = kws.pop('puppet',False)

        super(cgmMasterNull, self).__init__(node=node, name = name)

        if puppet and not self.isReferenced():
            log.info("Puppet provided!")
            log.info(puppet.cgmName)
            log.info(puppet.mNode)
            self.doStore('cgmName',puppet.mNode+'.cgmName')
            self.addAttr('puppet',attrType = 'messageSimple')
            self.connectParent(puppet, 'masterNull','puppet') 
        
        if not self.isReferenced():   
            if not self.verify():
                raise StandardError,"Failed!"

    def verify(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
        self.addAttr('mClass',value = 'cgmMasterNull',lock=True)
        self.addAttr('cgmName',initialValue = '',lock=True)
        self.addAttr('cgmType',initialValue = 'ignore',lock=True)
        self.addAttr('cgmModuleType',value = 'master',lock=True)   
        self.addAttr('partsGroup',attrType = 'messageSimple',lock=True)   
        self.addAttr('deformGroup',attrType = 'messageSimple',lock=True)   	
        self.addAttr('noTransformGroup',attrType = 'messageSimple',lock=True)   
        self.addAttr('geoGroup',attrType = 'messageSimple',lock=True)   
        
        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()
        return True

    def __bindData__(self):
        pass

class cgmInfoNode(cgmMeta.cgmNode):
    """"""
    def __init__(self,node = None, name = 'info', *args,**kws):
        """Constructor"""
        log.info(">>> cgmInfoNode.__init__")
        if kws:log.info("kws: %s"%kws)
        
        puppet = kws.pop('puppet',False)#to pass a puppet instance in 
        infoType = kws.pop('infoType','')

        #>>>Keyword args
        super(cgmInfoNode, self).__init__(node=node, name = name,*args,**kws)

        log.info("puppet :%s"%puppet)
        if puppet:
            self.doStore('cgmName',puppet.mNode+'.cgmName')
            self.connectParent(puppet, infoType, 'puppet')               

        self.addAttr('cgmName', attrType = 'string', initialValue = '',lock=True)
        if infoType == '':
            if self.hasAttr('cgmTypeModifier'):
                infoType = self.cgmTypeModifier
            else:
                infoType = 'settings'

        self.addAttr('cgmTypeModifier',infoType,lock=True)
        self.addAttr('cgmType','info',lock=True)
        
        if not self.isReferenced():   
            if not self.verify():
                raise StandardError,"Failed!"

    def verify(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
        log.info(">"*10 + " cgmInfoNode.verify.... " + "<"*10)
        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()  
        return True
        

    def __bindData__(self):
        pass
    
class cgmModuleBufferNode(cgmMeta.cgmBufferNode):
    """"""
    def __init__(self,node = None, name = 'buffer',initializeOnly = False,*args,**kws):
        log.info(">>> cgmModuleBufferNode.__init__")
        if kws:log.info("kws: %s"%kws)    
        
        """Constructor"""
        module = kws.get('module') or False
        bufferType = kws.get('bufferType') or ''

        #>>> Keyword args
        super(cgmModuleBufferNode, self).__init__(node=node, name = name,*args,**kws)
        log.debug(">"*10 + " cgmModuleBufferNode.init.... " + "<"*10)
        log.debug(args)
        log.debug(kws)        
        
        if not self.isReferenced():   
            if not self.verify(**kws):
                raise StandardError,"Failed!"

    def verify(self,*args,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
        module = kws.get('module') or False
        bufferType = kws.get('bufferType') or ''
               
        #>>> Buffer type set    
        if bufferType == '':
            if self.hasAttr('cgmTypeModifier'):
                bufferType = self.cgmTypeModifier
            else:
                bufferType = 'buffer'   
                
        #>>> Attr check    
        self.addAttr('cgmName', attrType = 'string', initialValue = '',lock=True)
        self.addAttr('cgmTypeModifier',initialValue = bufferType,lock=True)
        self.addAttr('cgmType','buffer',lock=True)
        self.addAttr('module',attrType = 'messageSimple')

        #>>> Module stuff   
        if module:
            try:
                module = module.mNode
            except:
                module = module
            self.connectParent(module, bufferType, 'module') 
            
        if self.getMessage('module'):
            self.doStore('cgmName',self.getMessage('module',False)[0],overideMessageCheck = True)#not long name
            #self.doStore('cgmName',self.getMessage('module',False)[0],overideMessageCheck = True)#not long name
              
        self.doName(**kws)  
        return True

    def __bindData__(self):
        pass
    


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# MODULE Base class
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
"""
InfoNullsNames = ['settings',
                  'setupOptions',
                  'templatePosObjects',
                  'visibilityOptions',
                  'templateControlObjects',
                  'coreNames',
                  'templateStarterData',
                  'templateControlObjectsData',
                  'skinJoints',
                  'rotateOrders']"""

moduleStates = ['define','template','deform','rig']

initLists = []
initDicts = ['infoNulls','parentTagDict']
initStores = ['ModuleNull','refState']
initNones = ['refPrefix','moduleClass']

defaultSettings = {'partType':'none'}

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
moduleNulls_toMake = 'rig','template' #These will be created and connected to a module and parented under them    
moduleBuffers_toMake = ['coreNames']

rigNullAttrs_toMake = {'version':'float',#Attributes to be initialzed for any module
                       'fk':'bool',
                       'ik':'bool',
                       'stretchy':'bool',
                       'bendy':'bool',
                       'handles':'int',
                       'skinJoints':'message'}

templateNullAttrs_toMake = {'version':'float',
                            'rollJoints':'int',#How many splits per segement
                            'stiffIndex':'int',#Stiff index has to do with which segments to not split, maybe make it an argument
                            'curveDegree':'int',#Degree of the template curve, 0 for purely point to point curve
                            'posObjects':'message',#Not 100% on this one
                            'controlObjects':'message',#Controls for setting the template
                            'root':'messageSimple',#The module root
                            'curve':'messageSimple',#Module curve
                            'orientHelpers':'messageSimple',#Orientation helper controls
                            'orientRootHelper':'messageSimple',#Root orienation helper
                            'templateStarterData':'string',#this will be a json dict
                            'controlObjectTemplatePose':'string'}

class cgmModule(cgmMeta.cgmObject):
    def __init__(self,*args,**kws):
        """ 
        Intializes an module master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored

        Naming and template tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        """
        log.info(">>> cgmModule.__init__")
        if kws:log.info("kws: %s"%str(kws))         
        if args:log.info("args: %s"%str(args))            
        
        start = time.clock()

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Figure out the node
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>          
        ##If a node is provided, use it
        ##If a name is provided, see if there's node for it
        ##If nothing is provided, just make one     


        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Verify or Initialize
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
        
        super(cgmModule, self).__init__(*args,**kws) 

        #Keywords - need to set after the super call
        #==============         
        self.kw_name= kws.get('name') or self.cgmName or False        
        self.kw_moduleParent = kws.get('moduleParent') or False
        #self.kw_position = kws.get('position') or False
        #self.kw_direction = kws.get('direction') or False
        #self.kw_directionModifier = kws.get('directionModifier') or False
        #self.kw_nameModifier = kws.get('nameModifier') or False
        self.kw_forceNew = kws.get('forceNew') or False
        self.kw_initializeOnly = kws.get('initializeOnly') or False  
        self.kw_handles = kws.get('handles') or 1 # can't have 0 handles  
        self.kw_rollJoints = kws.get('rollJoints') or 0 # can't have 0 handles  


        self.kw_callNameTags = {'cgmPosition':kws.get('position') or False, 
                                'cgmDirection':kws.get('direction') or False, 
                                'cgmDirectionModifier':kws.get('directionModifier') or False,
                                'cgmNameModifier':kws.get('nameModifier') or False}

        #>>> Initialization Procedure ==================   
        if self.isReferenced() or self.kw_initializeOnly:
            log.info("'%s' Initializing only..."%self.kw_name)
            if not self.initialize():
                log.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%self.kw_name)
                return          
        else:
            if not self.verify(**kws):
                log.critical("'%s' failed to verify!"%self.kw_name)
                return  

        log.info("'%s' Checks out!"%self.getShortName())
        log.info('Time taken =  %0.3f' % (time.clock()-start))


    def __bindData__(self,**kws):        
        #Variables
        #==============   
        log.info("In bind data")
        #self.addAttr('mClass', initialValue='cgmModule',lock=True) 
        #self.addAttr('cgmType',value = 'module',lock=True)

    def initialize(self,**kws):
        """ 
        Initializes the various components a moduleNull for a character/asset.

        RETURNS:
        success(bool)
        """  
        #Puppet Network Node
        #==============
        if self.cgmType != 'module':
            log.warning("cgmType not '%s'"%self.cgmType)
            return False    
        return True # Experimetning, Don't know that we need to check this stuff as it's for changing info, not to be used in process
        for attr in moduleNulls_toMake:
            attr = attr + 'Null'
            if attr in self.__dict__.keys():
                try:
                    Attr = 'i_' + attr+'Null'#Get a better attribute store string   
                    buffer = self.getMessage(attr)[0]
                    log.info(Attr)
                    log.info(buffer)
                    self.__dict__[Attr] = r9Meta.MetaClass( buffer )
                    log.info("'%s' initialized as self.%s"%(buffer))
                except:    
                    log.error("'%s' null failed. Please verify puppet."%attr)                    
                    return False
                
        for attr in moduleBuffers_toMake:
            if attr in self.__dict__.keys():
                try:
                    Attr = 'i_' + attr#Get a better attribute store string
                    buffer = self.getMessage(attr)[0]                    
                    self.__dict__[Attr] = r9Meta.MetaClass( buffer)
                    log.info("'%s' initialized as self.%s"%(buffer))  
                except:    
                    log.error("'%s' info node failed. Please verify puppet."%attr)                    
                    return False

        return True


    def verify(self,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """
        #>>> Module Null ==================                   
        self.addAttr('mClass', initialValue='cgmModule',lock=True) 
        self.addAttr('cgmType',value = 'module',lock=True)
        
        if self.kw_name:#If we have a name, store it
            self.doStore('cgmName',self.kw_name,True)        
        
        if attributes.doGetAttr(self.mNode,'cgmType') != 'module':
            log.error("'%s' is not a module. It's mClass is '%s'"%(self.mNode, attributes.doGetAttr(self.mNode,'mClass')))
            return False

        #Store tags from init call
        #==============  
        for k in self.kw_callNameTags.keys():
            if self.kw_callNameTags.get(k):
                log.info(k + " : " + str(self.kw_callNameTags.get(k)))                
                self.addAttr(k,value = self.kw_callNameTags.get(k),lock = True)
                log.info(str(self.getNameDict()))
                log.info(self.__dict__[k])
            #elif k in self.parentTagDict.keys():
                #   self.store(k,'%s.%s'%(self.msgModuleParent.value,k))
        self.doName()        

        #Attributes
        #==============  
        self.addAttr('moduleType',initialValue = 'segment',lock=True)

        self.addAttr('moduleParent',attrType='message')#Changed to message for now till Mark decides if we can use single
        self.addAttr('modulePuppet',attrType='messageSimple')
        self.addAttr('moduleChildren',attrType='message')

        stateDict = {'templateState':0,'rigState':0,'skeletonState':0} #Initial dict
        self.addAttr('moduleStates',attrType = 'string', initialValue=stateDict, lock = True)

        self.addAttr('rigNull',attrType='messageSimple',lock=True)
        self.addAttr('templateNull',attrType='messageSimple',lock=True)
        self.addAttr('coreNames',attrType='messageSimple',lock=True)

        log.debug("Module null good...")

        #>>> Rig/Template Nulls ==================   

        #Initialization
        #==============      
        for attr in moduleNulls_toMake:
            log.info(attr)
            grp = attributes.returnMessageObject(self.mNode,attr+'Null')# Find the group
            Attr = 'i_' + attr+'Null'#Get a better attribute store string           
            if mc.objExists( grp ):
                #If exists, initialize it
                try:     
                    self.__dict__[Attr]  = r9Meta.MetaClass(grp)#Initialize if exists  
                    log.info("'%s' initialized to 'self.%s'"%(grp,Attr))                    
                except:
                    log.error("'%s' group failed. Please verify puppet."%attr)                    
                    return False   

            else:#Make it
                log.info('Creating %s'%attr)                                    
                self.__dict__[Attr]= cgmMeta.cgmObject(name=attr)#Create and initialize
                self.connectChild(self.__dict__[Attr].mNode, attr+'Null','module') #Connect the child to the holder                
                self.__dict__[Attr].addAttr('cgmType',attr+'Null',lock=True)
                log.info("'%s' initialized to 'self.%s'"%(grp,Attr))                    

            self.__dict__[Attr].doParent(self.mNode)
            self.__dict__[Attr].doName()

            attributes.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode )
        """    
        if not mc.objExists( attributes.returnMessageObject(self.mNode,'settings') ):
            log.info('Creating settings')                                    
            self.i_settings = cgmInfoNode(puppet = self, infoType = 'settings')#Create and initialize
        else:
            log.info('settings infoNode exists. linking....')                        
            self.i_settings = self.settings #Linking to instance for faster processing. Good idea?   
        """
        for attr in moduleBuffers_toMake:
            log.info(attr)
            obj = attributes.returnMessageObject(self.mNode,attr)# Find the object
            Attr = 'i_' + attr#Get a better attribute store string           
            if mc.objExists( obj ):
                #If exists, initialize it
                try:     
                    self.__dict__[Attr]  = r9Meta.MetaClass(obj)#Initialize if exists  
                    log.info("'%s' initialized to 'self.%s'"%(obj,Attr))                    
                except:
                    log.error("'%s' null failed. Please verify modules."%attr)                    
                    return False               
            else:#Make it
                log.info('Creating %s'%attr)                                    
                self.__dict__[Attr]= cgmModuleBufferNode(module = self, bufferType = attr, overideMessageCheck = True)#Create and initialize
                #self.connectChild(self.__dict__[Attr].mNode, attr,'module') #Connect the child to the holder                
                #self.__dict__[Attr].addAttr('cgmName',attr+'Null',lock=True)
                log.info("'%s' initialized to 'self.%s'"%(attr,Attr))    
                
        #Attrbute checking
        #=================
        for attr in rigNullAttrs_toMake.keys():#See table just above cgmModule
            log.info("Checking '%s' on rig Null"%attr)
            if attr == 'handles':
                if self.kw_handles == 1:
                    self.i_rigNull.addAttr(attr,initialValue = self.kw_handles, attrType = rigNullAttrs_toMake[attr],lock = True )                
                else:
                    self.i_rigNull.addAttr(attr,value = self.kw_handles, attrType = rigNullAttrs_toMake[attr],lock = True )                

                log.info('handles case, setting min')
                a = cgmMeta.cgmAttr(self.i_rigNull.mNode,'handles')
                log.info(self.kw_handles)                
                log.info(self.i_rigNull.handles)                
                a.doMin(1)#Make this check that the value is not below the min when set
            else:
                self.i_rigNull.addAttr(attr,attrType = rigNullAttrs_toMake[attr],lock = True )

        for attr in templateNullAttrs_toMake.keys():#See table just above cgmModule
            log.info("Checking '%s' on template Null"%attr)	
            if attr == 'rollJoints':
                log.info(self.kw_rollJoints)
                if self.kw_rollJoints == 0:
                    self.i_templateNull.addAttr(attr,initialValue = self.kw_rollJoints, attrType = templateNullAttrs_toMake[attr],lock = True )                
                else:
                    self.i_templateNull.addAttr(attr,value = self.kw_rollJoints, attrType = templateNullAttrs_toMake[attr],lock = True )                		    	    
            else:
                self.i_templateNull.addAttr(attr,attrType = templateNullAttrs_toMake[attr],lock = True )        

        return True
    
    def getModuleColors(self):
        direction = search.returnTagInfo(self.mNode,'cgmDirection')
        if not direction:
            return modules.returnSettingsData('colorCenter',True)
        else:
            return modules.returnSettingsData(('color'+direction.capitalize()),True)
        
    def doSetParentModule(self,moduleParent,force = False,):
        """
        Set a module parent of a module

        module(string)
        """
        mFactory.doSetParentModule(self,moduleParent,force)

    def getGeneratedCoreNames(self):
        return mFactory.getGeneratedCoreNames(self)
    def doSize(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doSize)
        """
        return mFactory.doSize(self,**kws)
    def isSized(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isSized)
        """
        return mFactory.isSized(self,**kws)       
    def isTemplated(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isTemplated)
        """
        return mFactory.isTemplated(self)
    def isSkeletonized(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isSkeletonized)
        """
        return mFactory.isSkeletonized(self)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Limb stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
limbTypes = {'segment':{'handles':3,'stiffIndex':0,'curveDegree':1,'rollJoints':3},
             'finger':{'handles':5,'stiffIndex':1,'curveDegree':0,'rollJoints':0},
             'clavicle':{'handles':1,'stiffIndex':0,'curveDegree':0,'rollJoints':0},
             'arm':{'handles':3,'stiffIndex':0,'curveDegree':0,'rollJoints':3},
             'leg':{'handles':3,'stiffIndex':0,'curveDegree':0,'rollJoints':3},
             'torso':{'handles':5,'stiffIndex':-1,'curveDegree':1,'rollJoints':2},
             'tail':{'handles':5,'stiffIndex':0,'curveDegree':1,'rollJoints':3},
             'head':{'handles':1,'stiffIndex':0,'curveDegree':0,'rollJoints':0},
             'neckHead':{'handles':4,'stiffIndex':-1,'curveDegree':1,'rollJoints':3},
             'foot':{'handles':3,'stiffIndex':0,'curveDegree':0,'rollJoints':0}
             }  
class cgmLimb(cgmModule):
    def __init__(self,*args,**kws):
        """ 
        Intializes an module master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored
        
        mType(string) -- must be in cgm_PuppetMeta.limbTypes.keys()
        Naming and template tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        """
        log.info(">>> cgmLimb.__init__")
        if kws:log.info("kws: %s"%str(kws))         
        if args:log.info("args: %s"%str(args))  
        
        start = time.clock()	
        
        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']
            
        super(cgmLimb, self).__init__(*args,**kws) 


    def verify(self,**kws):
        cgmModule.verify(self,**kws)

        if 'mType' not in kws.keys() and self.moduleType in limbTypes.keys():
            log.info("'%s' type checks out."%self.moduleType)	    
            moduleType = self.moduleType
        elif 'name' in kws.keys():
            moduleType = kws['name']
        else:
            moduleType = kws.pop('mType','segment')	

        if not moduleType in limbTypes.keys():
            log.info("'%s' type is unknown. Using segment type"%moduleType)
            moduleType = 'segment'

        if self.moduleType != moduleType:
            log.info("Changing type to '%s' type"%moduleType)
            self.moduleType = moduleType
            settings = limbTypes[moduleType] 
            self.rigNull.addAttr('handles', value = settings['handles'],lock = True) 
            self.templateNull.addAttr('rollJoints', value = settings['rollJoints'],lock = True) 
            self.templateNull.addAttr('curveDegree', value = settings['curveDegree'],lock = True) 
            self.templateNull.addAttr('stiffIndex', value = settings['stiffIndex'],lock = True) 	    

        else:
            self.moduleType = moduleType
            settings = limbTypes[moduleType] 
            self.rigNull.addAttr('handles', initialValue = settings['handles'],lock = True) 
            self.templateNull.addAttr('rollJoints', initialValue = settings['rollJoints'],lock = True) 
            self.templateNull.addAttr('curveDegree', initialValue = settings['curveDegree'],lock = True) 
            self.templateNull.addAttr('stiffIndex', initialValue = settings['stiffIndex'],lock = True) 

        return True



#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
r9Meta.registerMClassInheritanceMapping()
#=========================================================================
