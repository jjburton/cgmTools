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
#from cgm.lib.classes import NameFactory
from cgm.core.lib import nameTools
reload(nameTools)
from cgm.core.rigger import ModuleFactory as mFactory
reload(mFactory)
from cgm.core.rigger import PuppetFactory as pFactory
reload(pFactory)
from cgm.core.rigger import MorpheusFactory as morphyF
reload(morphyF)
from cgm.core import cgm_Meta as cgmMeta
reload(cgmMeta)
from cgm.core import cgm_Meta as cgmMeta

from cgm.core.classes import NodeFactory as nodeF
reload(nodeF)
from cgm.lib import (modules,
                     distance,
                     deformers,
                     controlBuilder,
                     attributes,
                     search,
                     curves)

cgmModuleTypes = ['cgmModule','cgmLimb']
########################################################################
class cgmPuppet(cgmMeta.cgmNode):
    """"""
    #----------------------------------------------------------------------
    #@r9General.Timer
    def __init__(self, node = None, name = None, initializeOnly = False, doVerify = False, *args,**kws):
        log.debug(">>> cgmPuppet.__init__")
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
	
        """Constructor"""
        #>>>Keyword args
        puppet = kws.pop('puppet',None)

        #Need a simple return of
        puppets = pFactory.simplePuppetReturn()
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Finding the network node and name info from the provided information
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>          
        ##If a node is provided, check if it's a cgmPuppet
        ##If a name is provided, see if there's a puppet with that name, 
        ##If nothing is provided, just make one
        if node is None and name is None and args:
            log.debug("Checking '%s'"%args[0])
            node = args[0]

        if puppets:#If we have puppets, check em
            log.debug("Found the following puppets: '%s'"%"','".join(puppets))            
            if name is not None or node is not None:    
                if node is not None and node in puppets:
                    puppet = node
                    name = attributes.doGetAttr(node,'cgmName')
                else:
                    for p in puppets:
                        if attributes.doGetAttr(p,'cgmName') in [node,name]:
                            log.debug("Puppet tagged '%s' exists. Checking '%s'..."%(attributes.doGetAttr(p,'cgmName'),p))
                            puppet = p
                            name = attributes.doGetAttr(p,'cgmName')
                            break

        if not name:
            log.warning("No puppet name found")
            name = search.returnRandomName()  

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Verify or Initialize
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>           
        log.debug("Puppet is '%s'"%name)
	if puppet is None:puppetCreatedState = True
	else:puppetCreatedState = False
        super(cgmPuppet, self).__init__(node = puppet, name = name) 
	self.UNMANAGED.extend(['__justCreatedState__','i_masterNull'])	
	
	self.__justCreatedState__ = puppetCreatedState
	
        #>>> Puppet Network Initialization Procedure ==================       
        if self.isReferenced() or initializeOnly:
            log.debug("'%s' Initializing only..."%name)
            if not self.initialize():
                #log.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%name)
                raise StandardError,"'%s' failed to initialize. Please go back to the non referenced file to repair!"%name
	elif self.__justCreatedState__ or doVerify:
	    log.debug("Verifying...")
            if not self.__verify__(name,**kws):
                #log.critical("'%s' failed to __verify__!"%name)
                raise StandardError,"'%s' failed to verify!"%name

    #====================================================================================
    def initialize(self):
        """ 
        Initializes the various components a masterNull for a character/asset.

        RETURNS:
        success(bool)
        """  
        #Puppet Network Node
        #==============
	if not issubclass(type(self),cgmPuppet):
            log.error("'%s' is not a puppet. It's mClass is '%s'"%(self.mNode, attributes.doGetAttr(self.mNode,'mClass')))
            return False
	
        return True
    
    #@r9General.Timer
    def __verify__(self,name = None):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """             
        #Puppet Network Node
        #============== 
	log.debug(1)
        self.addAttr('mClass', initialValue='cgmPuppet',lock=True)  
        if name is not None and name:
	    self.addAttr('cgmName',name, attrType='string', lock = True)
        
        self.addAttr('cgmType','puppetNetwork')
        self.addAttr('version',initialValue = 1.0, lock=True)  
        self.addAttr('masterNull',attrType = 'messageSimple',lock=True)  
        self.addAttr('masterControl',attrType = 'messageSimple',lock=True)  	
        self.addAttr('moduleChildren',attrType = 'message',lock=True) 
	
	#Settings
	#==============
	log.debug(2)	
	defaultFont = modules.returnSettingsData('defaultTextFont')
	self.addAttr('font',attrType = 'string',initialValue=defaultFont,lock=True)   
	self.addAttr('axisAim',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=2) 
	self.addAttr('axisUp',enumName = 'x+:y+:z+:x-:y-:z-', attrType = 'enum',initialValue=1) 
	self.addAttr('axisOut',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=0) 
	self.addAttr('skinDepth',attrType = 'float',initialValue=2,lock=True)   
	
        self.doName()
        log.debug("Network good...")

        #MasterNull
        #==============   
	log.debug(3)	
        if not mc.objExists(attributes.returnMessageObject(self.mNode,'masterNull')):#If we don't have a masterNull, make one
            self.i_masterNull = cgmMasterNull(puppet = self)
            log.debug('Master created.')
        else:
            log.debug('Master null exists. linking....')            
            self.i_masterNull = self.masterNull#Linking to instance for faster processing. Good idea?
	    log.debug('self.i_masterNull: %s'%self.i_masterNull)
	    self.i_masterNull.__verify__()
	    #self.masterNull.__verify__()
        if self.i_masterNull.getShortName() != self.cgmName:
            self.masterNull.doName()
            if self.i_masterNull.getShortName() != self.cgmName:
                log.warning("Master Null name still doesn't match what it should be.")
                return False
        attributes.doSetLockHideKeyableAttr(self.i_masterNull.mNode,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        log.debug("Master Null good...")
	        
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Groups
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
	log.debug(4)
        for attr in 'deform','noTransform','geo','parts':
            grp = attributes.returnMessageObject(self.i_masterNull.mNode,attr+'Group')# Find the group
            Attr = 'i_' + attr+'Group'#Get a better attribute store string           
            if mc.objExists( grp ):
                #If exists, initialize it
                #self.__dict__[Attr]  = self.i_masterNull.__dict__[attr+'Group']#link it, can't link it
                self.__dict__[Attr]  = r9Meta.MetaClass(grp)#initialize
                log.debug("'%s' initialized as 'self.%s'"%(grp,Attr))
                #except:
                    #log.error("'%s' group failed. Please __verify__ puppet."%attr)                    
                    #return False   

            else:#Make it
                log.debug('Creating %s'%attr)                                    
                self.__dict__[Attr]= cgmMeta.cgmObject(name=attr)#Create and initialize
                self.__dict__[Attr].doName()
                #self.i_masterNull.connectChildNode(self.__dict__[Attr].mNode, attr+'Group','puppet') #Connect the child to the holder
		self.__dict__[Attr].connectParentNode(self.i_masterNull.mNode,'puppet', attr+'Group')
                log.debug("Initialized as 'self.%s'"%(Attr))                    
		self.__dict__[Attr].__verify__()
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
            self.__verify__()

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Puppet Utilities
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>             
    def tracePuppet(self):
        pass #Do this later.Trace a puppet to be able to fully delete everything.
        #self.nodes_list.append()
        raise NotImplementedError

    def doName(self,sceneUnique=False,nameChildren=False,**kws):
        """
	Cause puppets are stupid
        """
	#if not self.getTransform() and self.__justCreatedState__:
	    #log.error("Naming just created nodes, causes recursive issues. Name after creation")
	    #return False
	if self.isReferenced():
	    log.error("'%s' is referenced. Cannot change name"%self.mNode)
	    return False
	
	self.rename(nameTools.returnCombinedNameFromDict(self.getNameDict()))
	    
    def delete(self):
        """
        Delete the Puppet
        """
        mc.delete(self.masterNull.mNode)
        del(self)

    def addModule(self,mClass = 'cgmModule',**kws):
        """
        Create and connect a new module
        
        moduleType(string) - type of module to create
	
	p = cgmPM.cgmPuppet(name='Morpheus')
	p.addModule(mClass = 'cgmLimb',mType = 'torso')
	p.addModule(mClass = 'cgmLimb',mType = 'neck', moduleParent = 'spine_part')
	p.addModule(mClass = 'cgmLimb',mType = 'head', moduleParent = 'neck_part')
	p.addModule(mClass = 'cgmLimb',mType = 'arm',direction = 'left', moduleParent = 'spine_part')
        """   
        if mClass == 'cgmModule':
            tmpModule = cgmModule(**kws)   
        elif mClass == 'cgmLimb':
            tmpModule = cgmLimb(**kws)
        else:
            log.warning("'%s' is not a known module type. Cannot initialize"%mClass)
            return False
        
        self.connectModule(tmpModule)
	return tmpModule

    #@r9General.Timer
    def connectModule(self,module,force = True,**kws):
        """
        Connects a module to a puppet

        module(string)
        """
        #See if it's connected
        #If exists, connect
        #Get instance
        #==============	
        buffer = copy.copy(self.getMessage('moduleChildren')) or []#Buffer till we have have append functionality	
	self.i_masterNull = self.masterNull
	
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
            log.debug("Current children: %s"%self.getMessage('moduleChildren'))
            log.debug("Adding '%s'!"%module.getShortName())    

            buffer.append(module.mNode)
	    self.__setMessageAttr__('moduleChildren',buffer) #Going to manually maintaining these so we can use simpleMessage attr  parents
	    module.modulePuppet = self.mNode
            #del self.moduleChildren
            #self.connectChildren(buffer,'moduleChildren','modulePuppet',force=force)#Connect	    
            #module.__setMessageAttr__('modulePuppet',self.mNode)#Connect puppet to 

        #module.parent = self.i_partsGroup.mNode
        module.doParent(self.masterNull.partsGroup.mNode)

        return True
    
    def getGeo(self):
        return pFactory.getGeo(self)
    
    def getModuleFromDict(self,checkDict):
	"""
	Pass a check dict of attrsibutes and arguments. If that module is found, it returns it.
	checkDict = {'moduleType':'torso',etc}
	"""
	return pFactory.getModuleFromDict(self,checkDict)
    
    def getModules(self):
	"""
	Returns ordered modules. If you just need modules, they're always accessible via self.moduleChildren
	"""
	return pFactory.getModuleFromDict(self)
    
    def getState(self):
	"""
	Returns puppet state. That is the minimum state of it's modules
	"""
	return pFactory.getState(self) 
    
    def isCustomizable(self):
	return False 
    
    @r9General.Timer
    def _verifyMasterControl(self,**kws):
	""" 
	"""    
	# Master Curve
	#==================================================================
	masterControl = attributes.returnMessageObject(self.mNode,'masterControl')
	if mc.objExists( masterControl ):
	    #If exists, initialize it
	    log.debug('masterControl exists')                                    	    
	    i_masterControl = self.masterControl
	else:#Make it
	    log.debug('Creating masterControl')  
	    #Get size
	    if self.getGeo():
		averageBBSize = distance.returnBoundingBoxSizeToAverage(self.masterNull.geoGroup.mNode)
		log.debug("averageBBSize: %s"%averageBBSize)
		kws['size'] = 100 #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO - replace when we have full character
	    elif 'size' not in kws.keys():kws['size'] = 50
	    log.debug("kws['size']: %s"%kws['size'])
	    i_masterControl = cgmMasterControl(puppet = self,**kws)#Create and initialize
	    #self.masterControl = self.i_masterControl.mNode
	    log.debug('Verifying')
	    i_masterControl.__verify__()
	i_masterControl.parent = self.masterNull.mNode
	i_masterControl.doName()
	"""    
	except StandardError,error:
	    log.error("_verifyMasterControl>> masterControl fail! "%error)
	    raise StandardError,error """
	
	# Vis setup
	# Setup the vis network
	#====================================================================
	try:
	    if not i_masterControl.hasAttr('controlVis') or not i_masterControl.getMessage('controlVis'):
		log.error("This is an old master control or the vis control has been deleted. rebuild")
	    else:
		iVis = i_masterControl.controlVis
		visControls = 'left','right','sub','main'
		visArg = [{'result':[iVis,'leftSubControls_out'],'drivers':[[iVis,'left'],[iVis,'subControls'],[iVis,'controls']]},
		          {'result':[iVis,'rightSubControls_out'],'drivers':[[iVis,'right'],[iVis,'subControls'],[iVis,'controls']]},
		          {'result':[iVis,'subControls_out'],'drivers':[[iVis,'subControls'],[iVis,'controls']]},		      
		          {'result':[iVis,'leftControls_out'],'drivers':[[iVis,'left'],[iVis,'controls']]},
		          {'result':[iVis,'rightControls_out'],'drivers':[[iVis,'right'],[iVis,'controls']]}
		           ]
		nodeF.build_mdNetwork(visArg)
	except StandardError,error:
	    log.error("_verifyMasterControl>> visNetwork fail! "%error)
	    raise StandardError,error 	
	log.debug("Verified: '%s'"%self.cgmName)  
	
	# Settings setup
	# Setup the settings network
	#====================================================================	
	i_settings = i_masterControl.controlSettings
	str_nodeShort = str(i_settings.getShortName())
	#Skeleton/geo settings
	for attr in ['skeleton','geo',]:
	    i_settings.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
	    nodeF.argsToNodes("if %s.%s > 0; %s.%sVis"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
	    nodeF.argsToNodes("if %s.%s == 2:0 else 2; %s.%sLock"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
	
	#Geotype
	i_settings.addAttr('geoType',enumName = 'reg:proxy', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
	for i,attr in enumerate(['reg','proxy']):
	    nodeF.argsToNodes("if %s.geoType == %s:1 else 0; %s.%sVis"%(str_nodeShort,i,str_nodeShort,attr)).doBuild()    
	
	#Divider
	i_settings.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)

	#>>> Deform group
	#=====================================================================	
	if self.masterNull.getMessage('deformGroup'):
	    self.masterNull.deformGroup.parent = i_masterControl.mNode
	    
	return True
    
class cgmMorpheusPuppet(cgmPuppet):
    pass
    """
    def __init__(self, node = None, name = None, initializeOnly = False, *args,**kws):
	cgmPuppet.__init__(self, node = node, name = name, initializeOnly = initializeOnly, *args,**kws)
        """	
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Special objects
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
class cgmMasterNull(cgmMeta.cgmObject):
    """"""
    #----------------------------------------------------------------------
    #@r9General.Timer    
    def __init__(self,node = None, name = 'Master',doVerify = False, *args,**kws):
        """Constructor"""
        #>>>Keyword args
	if mc.objExists(name) and node is None:
	    node = name
	    
	log.debug("node: '%s'"%node)
	log.debug("name: '%s'"%name)	
        super(cgmMasterNull, self).__init__(node=node, name = name)
	        
        if not self.isReferenced():   
	    if self.__justCreatedState__ or doVerify:
		if not self.__verify__(**kws):
		    raise StandardError,"Failed!"

    #@r9General.Timer    
    def __verify__(self,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
        puppet = kws.pop('puppet',False)
        if puppet and not self.isReferenced():
            log.debug("Puppet provided!")
            log.debug(puppet.cgmName)
            log.debug(puppet.mNode)
            self.doStore('cgmName',puppet.mNode+'.cgmName')
            self.addAttr('puppet',attrType = 'messageSimple')
            if not self.connectParentNode(puppet,'puppet','masterNull'):
                raise StandardError,"Failed to connect masterNull to puppet network!"
	    
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
    def __init__(self,node = None, name = None, doVerify = False, *args,**kws):
        """Constructor"""
        log.debug(">>> cgmInfoNode.__init__")
        if kws:log.debug("kws: %s"%kws)
        
        puppet = kws.pop('puppet',False)#to pass a puppet instance in 
        infoType = kws.pop('infoType','')

        #>>>Keyword args
        super(cgmInfoNode, self).__init__(node=node, name = name,*args,**kws)

        log.debug("puppet :%s"%puppet)
        if puppet:
            self.doStore('cgmName',puppet.mNode+'.cgmName')
            self.connectParentNode(puppet, 'puppet',infoType)               

        self.addAttr('cgmName', attrType = 'string', initialValue = '',lock=True)
        if infoType == '':
            if self.hasAttr('cgmTypeModifier'):
                infoType = self.cgmTypeModifier
            else:
                infoType = 'settings'

        self.addAttr('cgmTypeModifier',infoType,lock=True)
        self.addAttr('cgmType','info',lock=True)
        
        if not self.isReferenced():
	    if self.__justCreatedState__ or doVerify:
		if not self.__verify__():
		    raise StandardError,"Failed!"
		
    #@r9General.Timer
    def __verify__(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
        log.debug(">"*10 + " cgmInfoNode.verify.... " + "<"*10)
        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()  
        return True
        

    def __bindData__(self):
        pass
    
class cgmMorpheusMakerNetwork(cgmMeta.cgmNode):
    """"""
    def __init__(self,*args,**kws):
        """Constructor"""
        log.debug(">>> cgmMorpheusMakerNetwork.__init__")
	if kws:log.debug("kws: %s"%str(kws))
	if args:log.debug("args: %s"%str(args))
	doVerify = kws.get('doVerify') or False
	
        #>>>Keyword args
        super(cgmMorpheusMakerNetwork, self).__init__(*args,**kws)
	if not 'initializeOnly' in kws.keys():initializeOnly = False
	else:initializeOnly = kws.get('initializeOnly')
	log.debug("initOnly: '%s'"%initializeOnly)
	
        if self.isReferenced() or initializeOnly: 
	    log.debug("'%s' initialized!"%self.mNode)
	elif self.__justCreatedState__ or doVerify:
	    if not self.__verify__():
		raise StandardError,"Failed!"

    def __bindData__(self):
        pass
    #@r9General.Timer
    def __verify__(self):
        """ 
        """ 
	self.addAttr('mClass','cgmMorpheusMakerNetwork',attrType='string',lock=True)
	self.addAttr('cgmType','customizationNetwork',attrType='string',lock=True)
	
	self.addAttr('meshClass',initialValue = 'm1',attrType='string',lock=True)
	self.addAttr('version',initialValue = 0.0,attrType='float',lock=True)
	
	self.addAttr('masterNull',attrType='messageSimple',lock=True)
	self.addAttr('masterControl',attrType='messageSimple',lock=True)
	
	self.addAttr('mPuppet',attrType='messageSimple',lock=True)
	

	#>>> Necessary attributes
	#===============================================================
	#> Curves and joints
        self.addAttr('controlCurves',attrType = 'message')
        self.addAttr('leftJoints',attrType = 'message',lock=True)
        self.addAttr('rightJoints',attrType = 'message',lock=True)	
        self.addAttr('leftRoots',attrType = 'message',lock=True)
        self.addAttr('rightRoots',attrType = 'message',lock=True)
        self.addAttr('jointList',attrType = 'message',lock=True)
	
	#>>> Geo =======================================================
        self.addAttr('baseBodyGeo',attrType = 'messageSimple',lock=True)
	#>>> Bridges
        self.addAttr('bridgeMainGeo',attrType = 'messageSimple',lock=True)
        self.addAttr('bridgeFaceGeo',attrType = 'messageSimple',lock=True)	
	self.addAttr('bridgeBodyGeo',attrType = 'messageSimple',lock=True)	
	
	#>>> Nodes =====================================================
        self.addAttr('bodyBlendshapeNodes',attrType = 'messageSimple',lock=True)
        self.addAttr('faceBlendshapeNodes',attrType = 'messageSimple',lock=True)
        self.addAttr('bridgeMainBlendshapeNode',attrType = 'messageSimple',lock=True)
        self.addAttr('bridgeFaceBlendshapeNode',attrType = 'messageSimple',lock=True)
	self.addAttr('bridgeBodyBlendshapeNode',attrType = 'messageSimple',lock=True)
	
        #self.addAttr('skinCluster',attrType = 'messageSimple',lock=True)
	
	#>>> Controls ==================================================
        self.addAttr('controlsLeft',attrType = 'message',lock=True)
        self.addAttr('controlsRight',attrType = 'message',lock=True)
        self.addAttr('controlsCenter',attrType = 'message',lock=True)
	
	#>>> Object Sets ===============================================
        self.addAttr('objSetAll',attrType = 'messageSimple',lock=True)
        self.addAttr('objSetLeft',attrType = 'messageSimple',lock=True)
        self.addAttr('objSetRight',attrType = 'messageSimple',lock=True)
	
	#>>> Watch groups
        self.addAttr('autoPickerWatchGroups',attrType = 'message',lock=True)#These groups will setup pickers for all sub groups of them	
	
        self.doName()
	
	#MasterNull
	#==============   
	if not mc.objExists(attributes.returnMessageObject(self.mNode,'masterNull')):#If we don't have a masterNull, make one
	    self.i_masterNull = cgmMeta.cgmObject()
	    self.addAttr('masterNull',self.i_masterNull.mNode,attrType = 'messageSimple',lock=True)
	    log.debug('Master created.')
	else:
	    log.debug('Master null exists. linking....')            
	    self.i_masterNull = self.masterNull#Linking to instance for faster processing. Good idea?

	self.i_masterNull.doStore('cgmName', self.mNode + '.cgmName')	
	#self.masterNull.addAttr('cgmName',self.cgmName,attrType = 'string',lock=True)
	self.i_masterNull.doName()
	attributes.doSetLockHideKeyableAttr(self.i_masterNull.mNode,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
	log.debug("Master Null good...")
	
	# Groups
	#======================================================================
	l_baseGroups = ['noTransform','geo','customGeo','hairGeo',
	                'clothesGeo','baseGeo','bsGeo']
	l_geoGroups = ['customGeo','bsGeo','baseGeo']
	l_customGeoGroups = ['clothesGeo','hairGeo','earGeo','eyeballGeo','eyebrowGeo']
	l_earGeoGroups = ['left_earGeo','right_earGeo']
	l_eyeGeoGroups = ['left_eyeGeo','right_eyeGeo']	
	l_bsTargetGroups = ['faceTargets','bodyTargets']
	l_bsFaceTargets = ['mouthTargets','noseTargets','browTargets','fullFaceTargets']
	l_bsBodyTargets = ['torsoTargets','fullBodyTargets',
	                   'left_armTargets','right_armTargets','left_handTargets','right_handTargets',
	                   'left_legTargets','right_legTargets']
	l_autoPickerWatchAttrs = ['left_earGeo','right_earGeo','left_eyeGeo','right_eyeGeo']
	l_autoPickerWatchGroups = []
	for attr in l_baseGroups + l_customGeoGroups+ l_bsTargetGroups + l_bsBodyTargets + l_bsFaceTargets + l_earGeoGroups + l_eyeGeoGroups:
	    log.debug('On attr: %s'%attr)
	    self.i_masterNull.addAttr(attr+'Group',attrType = 'messageSimple', lock = True)
	    grp = attributes.returnMessageObject(self.masterNull.mNode,attr+'Group')# Find the group
	    Attr = 'i_' + attr+'Group'#Get a better attribute store string           
	    if mc.objExists( grp ):
		#If exists, initialize it
		self.__dict__[Attr]  = r9Meta.MetaClass(grp)#initialize
		log.debug("'%s' initialized as 'self.%s'"%(grp,Attr))
		log.debug(self.__dict__[Attr].mNode)

	    else:#Make it
		log.debug('Creating %s'%attr)                                    
		self.__dict__[Attr]= cgmMeta.cgmObject(name=attr)#Create and initialize
		self.__dict__[Attr].doName()
		#self.i_masterNull.connectChildNode(self.__dict__[Attr].mNode, attr+'Group','puppet') #Connect the child to the holder
		self.__dict__[Attr].connectParentNode(self.i_masterNull.mNode,'puppet', attr+'Group')
		
		log.debug("Initialized as 'self.%s'"%(Attr))         
		
	    #>>> Special data parsing to get things named how we want
	    if 'left' in attr and not self.__dict__[Attr].hasAttr('cgmDirection'):
		buffer = self.__dict__[Attr].cgmName
		buffer = buffer.split('left_')
		self.__dict__[Attr].doStore('cgmName',''.join(buffer[1:]),overideMessageCheck = True)		
		self.__dict__[Attr].doStore('cgmDirection','left')
	    if 'right' in attr and not self.__dict__[Attr].hasAttr('cgmDirection'):
		buffer = self.__dict__[Attr].cgmName
		buffer = buffer.split('right_')
		self.__dict__[Attr].doStore('cgmName',''.join(buffer[1:]),overideMessageCheck = True)		
		self.__dict__[Attr].doStore('cgmDirection','right')
		
	    if 'Targets' in attr and not self.__dict__[Attr].hasAttr('cgmTypeModifier'):
		buffer = self.__dict__[Attr].cgmName
		buffer = buffer.split('Targets')
		self.__dict__[Attr].doStore('cgmName',''.join(buffer[0]),overideMessageCheck = True)		
		self.__dict__[Attr].doStore('cgmTypeModifier','targets',overideMessageCheck = True)
		self.__dict__[Attr].doName()
		
	    if 'Geo' in attr and not self.__dict__[Attr].hasAttr('cgmTypeModifier'):
		buffer = self.__dict__[Attr].cgmName
		buffer = buffer.split('Geo')
		self.__dict__[Attr].doStore('cgmName',''.join(buffer[0]),overideMessageCheck = True)		
		self.__dict__[Attr].doStore('cgmTypeModifier','geo',overideMessageCheck = True)
		self.__dict__[Attr].doName()
		
	    # Few Case things
	    #==============            
	    if attr == 'geo':
		self.__dict__[Attr].doParent(self.i_noTransformGroup)
	    elif attr in l_geoGroups:
		self.__dict__[Attr].doParent(self.i_geoGroup)	
	    elif attr in l_customGeoGroups:
		self.__dict__[Attr].doParent(self.i_customGeoGroup)
	    elif attr in l_earGeoGroups:
		self.__dict__[Attr].doParent(self.i_earGeoGroup)
	    elif attr in l_eyeGeoGroups:
		self.__dict__[Attr].doParent(self.i_eyeballGeoGroup)	    
	    elif attr in l_bsTargetGroups:
		self.__dict__[Attr].doParent(self.i_bsGeoGroup)
	    elif attr in l_bsFaceTargets:
		self.__dict__[Attr].doParent(self.i_faceTargetsGroup)
	    elif attr in l_bsBodyTargets:
		self.__dict__[Attr].doParent(self.i_bodyTargetsGroup)	    
	    else:    
		self.__dict__[Attr].doParent(self.i_masterNull)
		
	    if attr in l_autoPickerWatchAttrs:#append to our list to store
		l_autoPickerWatchGroups.append(self.__dict__[Attr].mNode)

	    attributes.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode )
	
	self.autoPickerWatchGroups = l_autoPickerWatchGroups#store them
	# Master Curve
	#==================================================================
	masterControl = attributes.returnMessageObject(self.mNode,'masterControl')
	if mc.objExists( masterControl ):
	    #If exists, initialize it
	    self.i_masterControl = self.masterControl
	    self.i_masterControl.mClass = 'cgmMasterControl'

	else:#Make it
	    log.debug('Creating masterControl')                                    
	    self.i_masterControl = cgmMasterControl(puppet = self)#Create and initialize
	    #self.masterControl = self.i_masterControl.mNode
	    self.i_masterControl.__verify__()
	self.i_masterControl.parent = self.i_masterNull.mNode
	self.i_masterControl.doName()
	
	# Vis setup
	# Setup the vis network
	#====================================================================
	#self.i_masterControl.controlVis.addAttr('controls',attrType = 'bool',keyable = False, locked = True)
	if not self.i_masterControl.hasAttr('controlVis') or not self.i_masterControl.getMessage('controlVis'):
	    log.error("This is an old master control or the vis control has been deleted. rebuild")
	else:
	    iVis = self.i_masterControl.controlVis
	    visControls = 'left','right','sub','main'
	    visArg = [{'result':[iVis,'leftSubControls_out'],'drivers':[[iVis,'left'],[iVis,'subControls'],[iVis,'controls']]},
		      {'result':[iVis,'rightSubControls_out'],'drivers':[[iVis,'right'],[iVis,'subControls'],[iVis,'controls']]},
		      {'result':[iVis,'subControls_out'],'drivers':[[iVis,'subControls'],[iVis,'controls']]},		      
		      {'result':[iVis,'leftControls_out'],'drivers':[[iVis,'left'],[iVis,'controls']]},
		      {'result':[iVis,'rightControls_out'],'drivers':[[iVis,'right'],[iVis,'controls']]}
		       ]
	    
	    nodeF.build_mdNetwork(visArg)
	
	log.debug("Verified: '%s'"%self.cgmName)
        return True
        
    def doChangeName(self,name = ''):
	log.debug(">>> cgmMorpheusMakerNetwork.doChangeName")
	log.debug("name: '%s'"%name)	
        if name == self.cgmName:
            log.error("Network already named '%s'"%self.cgmName)
            return
        if name != '':
	    name = str(name)
            log.warning("Changing name from '%s' to '%s'"%(self.cgmName,name))
	    self.cgmName = name
            #self.doStore('cgmName',name,overideMessageCheck = True)
            self.__verify__()
	    self.masterControl.rebuildControlCurve()
	    
    def isCustomizable(self):
	"""
	TODO:
	Checks if an asset is good to go or not
	1) Check for controls
	2) Check for geo
	--skinned?
	--blendshaped?
	"""
	log.debug(">>> cgmMorpheusMakerNetwork.doChangeName")	
	controlsLeft = self.getMessage('controlsLeft')
	if not controlsLeft:
	    log.warning("No left controls. Aborting check.")
	    return False
	
	controlsRight = self.getMessage('controlsRight')	
	if not controlsRight:
	    log.warning("No right controls. Aborting check.")
	    return False
	
	if len(controlsLeft) != len(controlsRight):
	    log.warning("Control lengths don't match. Left: %i, Right: %i "%(len(controlsLeft),len(controlsRight)))
	    return False	    
	
	#Geo
	baseBodyGeo = self.getMessage('baseBodyGeo')
	if not baseBodyGeo:
	    log.warning("No base geo. Aborting check.")
	    return False
	
	#Skincluster
	#skinCluster = self.getMessage('skinCluster')
	if not deformers.returnObjectDeformers(baseBodyGeo[0],'skinCluster'):
	    log.warning("No skinCluster. Aborting check.")
	    return False
	
	#>>> Blendshape nodes
	if not deformers.returnObjectDeformers(baseBodyGeo[0],'blendShape'):
	    log.warning("No body blendshape node. Aborting check.")
	    return False
	"""
	if not self.getMessage('faceBlendshapeNodes'):
	    log.warning("No face blendshape node. Aborting check.")
	    return False"""		
	
	return True
    
    def verifyPuppet(self):
	"""
	Verify a Morpheus Puppet, creates one if not exists, otherwise make sure it's intact
	"""
	if not self.hasAttr('mPuppet'):
	    self.__verify__()
	    
	self.mPuppet = cgmMorpheusPuppet(name = str(self.cgmName),doVerify=True).mNode
        morphyF.verifyMorpheusNodeStructure(self.mPuppet)
	return True
	
    def verify_customizationData(self): 
	return morphyF.verify_customizationData(self)
    
    def setState(self,state,**kws):
	if self.verifyPuppet():
	    return morphyF.setState(self,state,**kws)
	return False
	
    def updateTemplate(self,**kws):
	return morphyF.updateTemplate(self,saveTemplatePose = True,**kws)  
	
    #@r9General.Timer
    def doUpdate_pickerGroups(self):
	"""
	Update the groups that are stored to self.autoPickerWatchGroups. By that, we mean
	setup a condition node network for each child of that group
	"""
	pickerGroups = self.getMessage('autoPickerWatchGroups')
	if not pickerGroups:
	    log.warning("No autoPickerWatchGroups detected")
	    return False
	log.debug( pickerGroups )
	#nodeF.build_conditionNetworkFromGroup('group1',controlObject = 'settings')
	i_settingsControl = self.masterControl.controlSettings
	settingsControl = i_settingsControl.getShortName()
	
	log.debug( i_settingsControl.mNode )
	for i_grp in self.autoPickerWatchGroups:
	    shortName = i_grp.getShortName()
	    log.debug(shortName)
	    #Let's get basic info for a good attr name
	    d = nameTools.returnObjectGeneratedNameDict(shortName,ignore=['cgmTypeModifier','cgmType'])
	    n = nameTools.returnCombinedNameFromDict(d)
	    nodeF.build_conditionNetworkFromGroup(shortName, chooseAttr = n, controlObject = settingsControl)
    
    #@r9General.Timer
    def doUpdateBlendshapeNode(self,blendshapeAttr):
	""" 
	Update a blendshape node by it checking it's source folder
	""" 
	log.debug(">>> cgmMorpheusMakerNetwork.doUpdateBlendshapeNode")
	log.debug("blendshapeAttr: '%s'"%blendshapeAttr)	
	
	# Get our base info
	#==================	        
	targetGeoGroup = self.masterNull.getMessage(blendshapeAttr)[0]#Targets group
	if not targetGeoGroup:
	    log.warning("No group found")
	    return False
	
	bsTargetObjects = search.returnAllChildrenObjects(targetGeoGroup,True)
	if not bsTargetObjects:
	    log.error("No geo group found")
	    return False
	
	baseGeo = self.getMessage('baseBodyGeo')[0]
	if not bsTargetObjects:
	    log.error("No geo found")
	    return False	
	
	#See if we have a blendshape node
    
	bsNode = deformers.buildBlendShapeNode(baseGeo,bsTargetObjects,'tmp')
	
	i_bsNode = cgmMeta.cgmNode(bsNode)
	i_bsNode.addAttr('cgmName','body',attrType='string',lock=True)    
	i_bsNode.addAttr('mClass','cgmNode',attrType='string',lock=True)
	i_bsNode.doName()
	p.bodyBlendshapeNodes = i_bsNode.mNode  

    def delete(self):
        """
        Delete the Puppet
        """
        if self.getMessage('mPuppet'):self.mPuppet.delete()
        mc.delete(self.masterNull.mNode)
	#mc.delete(self.mNode)
        del(self)
	
class cgmMasterControl(cgmMeta.cgmObject):
    """
    Make a master control curve
    """
    #@r9General.Timer	    
    def __init__(self,*args,**kws):
        """Constructor"""				
        #>>>Keyword args
        super(cgmMasterControl, self).__init__(*args,**kws)
	
        log.debug(">>> cgmMasterControl.__init__")
	if kws:log.debug("kws: %s"%str(kws))
	if args:log.debug("args: %s"%str(args)) 	
	doVerify = kws.get('doVerify') or False
	
        if not self.isReferenced():
	    if self.__justCreatedState__ or doVerify:
		if not self.__verify__(*args,**kws):
		    raise StandardError,"Failed!"	
	
    #@r9General.Timer	
    def __verify__(self,*args,**kws):
        puppet = kws.pop('puppet',False)
        if puppet and not self.isReferenced():
            log.debug("Puppet provided!")
            log.debug(puppet.cgmName)
            log.debug(puppet.mNode)
            self.doStore('cgmName',puppet.mNode+'.cgmName')
            self.addAttr('puppet',attrType = 'messageSimple')
            self.connectParentNode(puppet,'puppet','masterControl') 	
	
	#Check for shapes, if not, build
	self.color =  modules.returnSettingsData('colorMaster',True)

	#>>> Attributes
	if kws and 'name' in kws.keys():
	    self.addAttr('cgmName', kws.get('name'), attrType = 'string')
	    
	self.addAttr('cgmType','controlMaster',attrType = 'string')
	self.addAttr('axisAim',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=2, keyable = False, hidden=True)
	self.addAttr('axisUp',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=1, keyable = False, hidden=True)
	self.addAttr('axisOut',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=0, keyable = False, hidden=True)
	self.addAttr('setRO',attrType = 'enum', enumName= 'xyz:yzx:zxy:xzy:yxz:zyx',initialValue=0, keyable = True, hidden=False)
	attributes.doConnectAttr('%s.setRO'%self.mNode,'%s.rotateOrder'%self.mNode,True)

	self.addAttr('controlVis', attrType = 'messageSimple',lock=True)
	self.addAttr('visControl', attrType = 'bool',keyable = False,initialValue= 1)
	
	self.addAttr('controlSettings', attrType = 'messageSimple',lock=True)
	self.addAttr('settingsControl', attrType = 'bool',keyable = False,initialValue= 1)
	
	#Connect and Lock the scale stuff
	attributes.doConnectAttr(('%s.scaleY'%self.mNode),('%s.scaleX'%self.mNode),True)
	attributes.doConnectAttr(('%s.scaleY'%self.mNode),('%s.scaleZ'%self.mNode),True)
	cgmMeta.cgmAttr(self,'scaleX',lock=True,hidden=True)
	cgmMeta.cgmAttr(self,'scaleZ',lock=True,hidden=True)
	yAttr = cgmMeta.cgmAttr(self,'scaleY')
	yAttr.p_nameAlias = 'masterScale'
	
	#=====================================================================
	#>>> Curves!
	#=====================================================================
	#>>> Master curves
	if not self.getShapes() or len(self.getShapes())<3:
	    log.debug("Need to build shapes")
	    self.rebuildControlCurve(**kws)
	    
	#======================
	#>>> Sub controls
	visControl = attributes.returnMessageObject(self.mNode,'controlVis')
	if not mc.objExists( visControl ):
	    log.debug('Creating visControl')
	    buffer = controlBuilder.childControlMaker(self.mNode, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 135, controls = ['controlVisibility'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
	    i_c = cgmMeta.cgmObject(buffer.get('controlVisibility'))
	    i_c.addAttr('mClass','cgmObject')
	    i_c.doName()	
	    curves.setCurveColorByName(i_c.mNode,self.color[0])#Set the color
	    self.controlVis = i_c.mNode #Link it
	    
	    attributes.doConnectAttr(('%s.visControl'%self.mNode),('%s.v'%i_c.mNode),True)
	
	    #Vis control attrs
	    self.controlVis.addAttr('controls', attrType = 'bool',keyable = False,initialValue= 1)
	    self.controlVis.addAttr('subControls', attrType = 'bool',keyable = False,initialValue= 1)
	    #>>> Settings Control
	    settingsControl = attributes.returnMessageObject(self.mNode,'controlSettings')
	    
	    if not mc.objExists( settingsControl ):
		log.debug('Creating settingsControl')
		buffer = controlBuilder.childControlMaker(self.mNode, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 225, controls = ['controlSettings'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
		i_c = cgmMeta.cgmObject(buffer.get('controlSettings'))
		i_c.addAttr('mClass','cgmObject')
		i_c.doName()	
		curves.setCurveColorByName(i_c.mNode,self.color[0])#Set the color	    
		self.controlSettings = i_c.mNode #Link it	
		
		attributes.doConnectAttr(('%s.settingsControl'%self.mNode),('%s.v'%i_c.mNode),True)
	self.doName()
	
	
	return True
    
    #@r9General.Timer
    def rebuildControlCurve(self, size = None,font = None,**kws):
	"""
	Rebuild the master control curve
	"""
	log.debug('>>> rebuildControlCurve')
	shapes = self.getShapes()
	self.color =  modules.returnSettingsData('colorMaster',True)
	
	#>>> Figure out the control size 	
	if size == None:#
	    if shapes:
		absSize =  distance.returnAbsoluteSizeCurve(self.mNode)
		size = max(absSize)		
	    else:size = 125
	#>>> Figure out font	
	if font == None:#
	    if kws and 'font' in kws.keys():font = kws.get('font')		
	    else:font = 'arial'
	#>>> Delete shapes
	if shapes:
	    for s in shapes:mc.delete(s)	
		
	#>>> Build the new
	i_o = cgmMeta.cgmObject( curves.createControlCurve('masterAnim',size))#Create and initialize
	curves.setCurveColorByName( i_o.mNode,self.color[0] )
	curves.setCurveColorByName( i_o.getShapes()[1],self.color[1] )
	
	#>>> Build the text curve if cgmName exists
	if self.hasAttr('cgmName'):
	    rootShapes = i_o.getShapes()#Get the shapes
	    nameScaleBuffer = distance.returnAbsoluteSizeCurve(rootShapes[1])#Get the scale
	    nameScale = max(nameScaleBuffer) * .8#Get the new scale
	    masterText = curves.createTextCurveObject(self.cgmName,size=nameScale,font=font)
	    curves.setCurveColorByName(masterText,self.color[0])#Set the color
	    mc.setAttr((masterText+'.rx'), -90)#Rotate the curve
	    curves.parentShapeInPlace(self.mNode,masterText)#Shape parent it
	    mc.delete(masterText)
	    
	#>>>Shape parent it
	curves.parentShapeInPlace(self.mNode,i_o.mNode)
	mc.delete(i_o.mNode)
	
	self.doName()    
	
class cgmModuleBufferNode(cgmMeta.cgmBufferNode):
    """"""
    #@r9General.Timer    
    def __init__(self,node = None, name = None ,initializeOnly = False,*args,**kws):
	#DO NOT PUT A DEFAULT NAME IN THE DEFINITION...RECURSIVE HELL
        log.debug(">>> cgmModuleBufferNode.__init__")
        if kws:log.debug("kws: %s"%kws)    
        
        """Constructor"""
        module = kws.get('module') or False
        bufferType = kws.get('bufferType') or ''
	doVerify = kws.get('doVerify') or False
	
        #>>> Keyword args
        super(cgmModuleBufferNode, self).__init__(node=node, name = name,*args,**kws)
        log.debug(">"*10 + " cgmModuleBufferNode.init.... " + "<"*10)
        log.debug(args)
        log.debug(kws)        
        
        if not self.isReferenced(): 
	    if self.__justCreatedState__ or doVerify:	    
		if not self.__verify__(**kws):
		    raise StandardError,"Failed!"
    #@r9General.Timer
    def __verify__(self,*args,**kws):
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
                bufferType = 'cgmBuffer'   
                
        #>>> Attr check    
        self.addAttr('cgmName', attrType = 'string', initialValue = '',lock=True)
        self.addAttr('cgmTypeModifier',initialValue = bufferType,lock=True)
        self.addAttr('cgmType','cgmBuffer',lock=True)
        self.addAttr('module',attrType = 'messageSimple')

        #>>> Module stuff   
        if module:
            try:
                module = module.mNode
            except:
                module = module
            self.connectParentNode(module,'module',bufferType) 
            
        if self.getMessage('module'):
            self.doStore('cgmName',self.getMessage('module',False)[0],overideMessageCheck = True)#not long name
	    #self.doStore('cgmName',self.getMessage('module',False)[0],overideMessageCheck = True)#not long name
        self.doName()       
        #self.doName(**kws)  
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
                       'twist':'bool',
                       'gutsLock':'int',
                       'gutsVis':'int',                       
                       'skinJoints':'message'}

templateNullAttrs_toMake = {'version':'float',
                            'gutsLock':'int',
                            'gutsVis':'int',
                            'controlsVis':'int',
                            'controlsLock':'int',
                            'handles':'int',                            
                            'rollJoints':'int',#How many splits per segement
                            'rollOverride':'string',#Override
                            #'stiffIndex':'int',#Stiff index has to do with which segments to not split, maybe make it an argument
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
    #@r9General.Timer
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
        log.debug(">>> cgmModule.__init__")
        if kws:log.debug("kws: %s"%str(kws))         
        if args:log.debug("args: %s"%str(args))            

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
	doVerify = kws.get('doVerify') or False
        self.kw_name= kws.get('name') or False        
        self.kw_moduleParent = kws.get('moduleParent') or False
        self.kw_forceNew = kws.get('forceNew') or False
        self.kw_initializeOnly = kws.get('initializeOnly') or False  
        self.kw_handles = kws.get('handles') or 1 # can't have 0 handles  
        self.kw_rollJoints = kws.get('rollJoints') or 0 # can't have 0 handles  


        self.kw_callNameTags = {'cgmPosition':kws.get('position') or False, 
                                'cgmDirection':kws.get('direction') or False, 
                                'cgmDirectionModifier':kws.get('directionModifier') or False,
                                'cgmNameModifier':kws.get('nameModifier') or False}

        #>>> Initialization Procedure ================== 
	if not self.isReferenced():
	    if self.__justCreatedState__ or doVerify:	    
		if not self.__verify__(**kws):
		    log.critical("'%s' failed to verify!"%self.mNode)
		    raise StandardError,"'%s' failed to verify!"%self.mNode 
		return
	    
	log.debug("'%s' Initializing only..."%self.mNode)
	if not self.initialize():
	    log.critical("'%s' failed to initialize. Please go back to the non referenced file to repair!"%self.mNode)
	    raise StandardError,"'%s' failed to initialize!"%self.mNode
    
	
	
	"""#Old>>>
        if self.isReferenced() or self.kw_initializeOnly:
            log.debug("'%s' Initializing only..."%self.mNode)
            if not self.initialize():
                log.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%self.mNode)
                return          
        else:
	    if self.__justCreatedState__ or doVerify:	    
		if not self.__verify__(**kws):
		    log.critical("'%s' failed to verify!"%self.kw_name)
		    raise StandardError,"'%s' failed to verify!"%self.kw_name  
	"""
        log.debug("'%s' Checks out!"%self.getShortName())

    def __bindData__(self,**kws):        
        #Variables
        #==============   
        log.debug("In bind data")
        #self.addAttr('mClass', initialValue='cgmModule',lock=True) 
        #self.addAttr('cgmType',value = 'module',lock=True)
	
    #@r9General.Timer
    def initialize(self,**kws):
        """ 
        Initializes the various components a moduleNull for a character/asset.

        RETURNS:
        success(bool)
        """  
        #Puppet Network Node
        #==============
	if not issubclass(type(self),cgmModule):
            log.error("'%s' is cgmModule"%(self.mNode))
            return False
	
        for attr in moduleBuffers_toMake:
	    log.debug("checking: %s"%attr)
            Attr = 'i_' + attr#Get a better attribute store string   
	    obj = attributes.returnMessageObject(self.mNode,attr)# Find the object
	    if not obj:return False
	    try: 		
		i_buffer = r9Meta.MetaClass(obj)
	    except StandardError,error:
		log.error("buffer failed ('%s') failed: %s"%(attr,error))		
		return False
	    
	    if not issubclass(type(i_buffer),cgmModuleBufferNode):
		return False	
	    #If we get here, link it
	    
	    self.__dict__[Attr] = i_buffer
           	
        return True # Experimetning, Don't know that we need to check this stuff as it's for changing info, not to be used in process

    #@r9General.Timer
    def __verify__(self,**kws):
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
	    self.addAttr('cgmName',self.kw_name,attrType='string',lock=True)
	elif 'mType' in kws.keys():
	    self.addAttr('cgmName',kws['mType'],attrType='string',lock=True)	    
        
        if attributes.doGetAttr(self.mNode,'cgmType') != 'module':
            log.error("'%s' is not a module. It's mClass is '%s'"%(self.mNode, attributes.doGetAttr(self.mNode,'mClass')))
            return False

        #Store tags from init call
        #==============  
        for k in self.kw_callNameTags.keys():
            if self.kw_callNameTags.get(k):
                log.debug(k + " : " + str(self.kw_callNameTags.get(k)))                
                self.addAttr(k,value = self.kw_callNameTags.get(k),lock = True)
                log.debug(str(self.getNameDict()))
                log.debug(self.__dict__[k])
            #elif k in self.parentTagDict.keys():
                #   self.store(k,'%s.%s'%(self.msgModuleParent.value,k))
        self.doName()        

        #Attributes
        #==============  
        self.addAttr('moduleType',initialValue = 'segment',lock=True)

        self.addAttr('moduleParent',attrType='messageSimple')#Changed to message for now till Mark decides if we can use single
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
            log.debug(attr)
            grp = attributes.returnMessageObject(self.mNode,attr+'Null')# Find the group
            Attr = 'i_' + attr+'Null'#Get a better attribute store string           
            if mc.objExists( grp ):
                #If exists, initialize it
                try:     
                    self.__dict__[Attr] = r9Meta.MetaClass(grp)#Initialize if exists  
                    log.debug("'%s' initialized to 'self.%s'"%(grp,Attr))                    
                except:
                    log.error("'%s' group failed. Please verify puppet."%attr)                    
                    return False   

            else:#Make it
                log.debug('Creating %s'%attr)                                    
                self.__dict__[Attr]= cgmMeta.cgmObject(name=attr)#Create and initialize
		self.__dict__[Attr].connectParentNode(self.mNode,'module', attr+'Null')                
                self.__dict__[Attr].addAttr('cgmType',attr+'Null',lock=True)
                log.debug("'%s' initialized to 'self.%s'"%(grp,Attr))                    

            self.__dict__[Attr].doParent(self.mNode)
            self.__dict__[Attr].doName()

            attributes.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode )

        for attr in moduleBuffers_toMake:
            log.debug(attr)
            obj = attributes.returnMessageObject(self.mNode,attr)# Find the object
            Attr = 'i_' + attr#Get a better attribute store string           
            if mc.objExists( obj ):
                #If exists, initialize it
                try:     
                    self.__dict__[Attr]  = r9Meta.MetaClass(obj)#Initialize if exists  
                    log.debug("'%s' initialized to 'self.%s'"%(obj,Attr))                    
                except:
                    log.error("'%s' null failed. Please verify modules."%attr)                    
                    return False               
            else:#Make it
                log.debug('Creating %s'%attr)                                    
                self.__dict__[Attr]= cgmModuleBufferNode(module = self, name = attr, bufferType = attr, overideMessageCheck = True)#Create and initialize
                log.debug("'%s' initialized to 'self.%s'"%(attr,Attr))  
		
	    self.__dict__[Attr].__verify__()
	    
        #Attrbute checking
        #=================
        for attr in sorted(rigNullAttrs_toMake.keys()):#See table just above cgmModule
            log.debug("Checking '%s' on rig Null"%attr)
            self.i_rigNull.addAttr(attr,attrType = rigNullAttrs_toMake[attr],lock = True )

        for attr in sorted(templateNullAttrs_toMake.keys()):#See table just above cgmModule
            log.debug("Checking '%s' on template Null"%attr)	
            if attr == 'rollJoints':
                log.debug(self.kw_rollJoints)
                if self.kw_rollJoints == 0:
                    self.i_templateNull.addAttr(attr,initialValue = self.kw_rollJoints, attrType = templateNullAttrs_toMake[attr],lock = True )                
                else:
                    self.i_templateNull.addAttr(attr,value = self.kw_rollJoints, attrType = templateNullAttrs_toMake[attr],lock = True )                		    	    
            elif attr == 'handles':
                if self.kw_handles == 1:
                    self.i_templateNull.addAttr(attr,initialValue = self.kw_handles, attrType = templateNullAttrs_toMake[attr],lock = True,min = 1 )                
                else:
                    self.i_templateNull.addAttr(attr,value = self.kw_handles, attrType = templateNullAttrs_toMake[attr],lock = True,min = 1 )                
            elif attr == 'rollOverride':
                self.i_templateNull.addAttr(attr,initialValue = '{}', attrType = templateNullAttrs_toMake[attr],lock = True )                                
            else:
                self.i_templateNull.addAttr(attr,attrType = templateNullAttrs_toMake[attr],lock = True )        

	#Set Module Parent if we have that kw
	#=================		
	if self.kw_moduleParent:
	    self.doSetParentModule(self.kw_moduleParent)
        return True
    
    def getModuleColors(self):
        direction = search.returnTagInfo(self.mNode,'cgmDirection')
        if not direction:
            return modules.returnSettingsData('colorCenter',True)
        else:
            return modules.returnSettingsData(('color'+direction.capitalize()),True)
    
    def getPartNameBase(self):
	return nameTools.returnRawGeneratedName(self.mNode, ignore = ['cgmType'])
	
    
    def doSetParentModule(self,moduleParent,force = False):
        """
        Set a module parent of a module

        module(string)
        """
        mFactory.doSetParentModule(self,moduleParent,force)

    def getGeneratedCoreNames(self):
        return mFactory.getGeneratedCoreNames(self)
    
    def isModule(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isModule)
        """
        return mFactory.isModule(self)
    #>>> States
    #===========================================================
    def getState(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.getState)
        """
        return mFactory.getState(self)
    
    def setState(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.setState)
        """
        return mFactory.setState(self,*args,**kws)	
    
    #>>> Sizing
    #===========================================================
    def doSize(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doSize)
        """
        return mFactory.doSize(self,*args,**kws)
    def isSized(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isSized)
        """
        return mFactory.isSized(self,**kws)  
    
    #>>> Templates
    #===========================================================    
    def isTemplated(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isTemplated)
        """
        return mFactory.isTemplated(self)
    
    def doTemplate(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doTemplate)
        """
        return mFactory.doTemplate(self,*args,**kws)
    
    def deleteTemplate(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.deleteTemplate)
        """
        return mFactory.deleteTemplate(self) 
    
    def storeTemplatePose(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.storePose_templateSettings)
        """
        return mFactory.storePose_templateSettings(self)   
    
    def loadTemplatePose(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.readPose_templateSettings)
        """
        return mFactory.readPose_templateSettings(self)   
    
    #>>> Skeletonize
    #===========================================================  
    def isSkeletonized(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isSkeletonized)
        """
        return mFactory.isSkeletonized(self)
    
    def doSkeletonized(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doSkeletonized)
        """
        return mFactory.doSkeletonized(self)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Limb stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
limbTypes = {'segment':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'finger':{'handles':5,'rollOverride':'{"0":1}','curveDegree':0,'rollJoints':0},
             'clavicle':{'handles':1,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'arm':{'handles':3,'rollOverride':'{}','curveDegree':0,'rollJoints':3},
             'leg':{'handles':3,'rollOverride':'{}','curveDegree':2,'rollJoints':3},
             'torso':{'handles':5,'rollOverride':'{"-1":0,"0":0}','curveDegree':2,'rollJoints':2},
             'tail':{'handles':5,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'head':{'handles':1,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'neckHead':{'handles':4,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'foot':{'handles':3,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'hand':{'handles':0,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'thumb':{'handles':4,'rollOverride':'{}','curveDegree':1,'rollJoints':0}                          
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
        log.debug(">>> cgmLimb.__init__")
        if kws:log.debug("kws: %s"%str(kws))         
        if args:log.debug("args: %s"%str(args))  
        
        start = time.clock()	
        
        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']
            
        super(cgmLimb, self).__init__(*args,**kws) 


    def __verify__(self,**kws):
        cgmModule.__verify__(self,**kws)
	#super(cgmLimb,self).__verify(**kws)
	log.debug('here')
        if 'mType' not in kws.keys() and self.moduleType in limbTypes.keys():
            log.debug("'%s' type checks out."%self.moduleType)	    
            moduleType = self.moduleType
	elif 'mType' in kws.keys():
	    moduleType = kws['mType']
        elif 'name' in kws.keys():
            moduleType = kws['name']
        else:
            moduleType = kws.pop('mType','segment')	

        if not moduleType in limbTypes.keys():
            log.debug("'%s' type is unknown. Using segment type"%moduleType)
            moduleType = 'segment'

        if self.moduleType != moduleType:
            log.debug("Changing type to '%s' type"%moduleType)
            self.moduleType = moduleType
            settings = limbTypes[moduleType]
            if settings:
                for attr in settings.keys():
                    self.templateNull.addAttr(attr, value = settings[attr],lock = True) 
                    
        else:
            self.moduleType = moduleType
            settings = limbTypes[moduleType] 
            if settings:
                for attr in settings.keys():
                    self.templateNull.addAttr(attr, initialValue = settings[attr],lock = True)             
        return True



#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
r9Meta.registerMClassInheritanceMapping()
#=========================================================================
