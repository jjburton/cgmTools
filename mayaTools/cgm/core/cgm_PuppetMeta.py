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
from cgm.core import cgm_General as cgmGeneral

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

# From cgm ==============================================================
#from cgm.lib.classes import NameFactory
#from cgm.core import cgm_Meta as cgmMeta
import cgm_Meta as cgmMeta
from cgm.core.lib import nameTools
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import PuppetFactory as pFactory
from cgm.core.rigger import MorpheusFactory as morphyF

from cgm.core.classes import NodeFactory as nodeF
from cgm.lib import (modules,
                     distance,
                     deformers,
                     controlBuilder,
                     attributes,
                     search,
                     curves)

cgmModuleTypes = ['cgmModule','cgmLimb','cgmEyeball','cgmEyelids']
l_faceModuleTypes = ['eyeball','eyelids']
########################################################################
class cgmPuppet(cgmMeta.cgmNode):
    """"""
    #----------------------------------------------------------------------
    #@cgmGeneral.Timer
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
	    try:
		if not self.__verify__(name,**kws):
		    #log.critical("'%s' failed to __verify__!"%name)
		    raise StandardError,"'%s' failed to verify!"%name
	    except StandardError,error:
		raise StandardError,"%s >>> verify fail | error : %s"%(_str_funcName,error) 

    #====================================================================================
    #@cgmGeneral.Timer    
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
    
    #@cgmGeneral.Timer
    def __verify__(self,name = None):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """             
	_str_funcName = "cgmPuppet.__verify__(%s)"%self.p_nameShort
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
	
        #============== 
	try:#Puppet Network Node ================================================================
	    log.debug(1)
	    self.addAttr('mClass', initialValue='cgmPuppet',lock=True)  
	    if name is not None and name:
		self.addAttr('cgmName',name, attrType='string', lock = True)
	    self.addAttr('cgmType','puppetNetwork')
	    self.addAttr('version',initialValue = 1.0, lock=True)  
	    self.addAttr('masterNull',attrType = 'messageSimple',lock=True)  
	    self.addAttr('masterControl',attrType = 'messageSimple',lock=True)  	
	    self.addAttr('moduleChildren',attrType = 'message',lock=True) 
	    self.addAttr('unifiedGeo',attrType = 'messageSimple',lock=True) 
	except StandardError,error:
	    raise StandardError,"%s >>> Puppet network |error : %s"%(_str_funcName,error)
	
	try:#Settings ============================================================================
	    log.debug(2)	
	    defaultFont = modules.returnSettingsData('defaultTextFont')
	    self.addAttr('font',attrType = 'string',initialValue=defaultFont,lock=True)   
	    self.addAttr('axisAim',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=2) 
	    self.addAttr('axisUp',enumName = 'x+:y+:z+:x-:y-:z-', attrType = 'enum',initialValue=1) 
	    self.addAttr('axisOut',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=0) 
	    self.addAttr('skinDepth',attrType = 'float',initialValue=.75,lock=True)   
	    
	    self.doName()
	    log.debug("Network good...")
	except StandardError,error:
	    raise StandardError,"%s >>> Settings |error : %s"%(_str_funcName,error)
		
        try:#MasterNull ===========================================================================
	    log.debug(4)	
	    if not self.getMessage('masterNull'):#If we don't have a masterNull, make one
		self.i_masterNull = cgmMasterNull(puppet = self)
		log.debug('Master created.')
	    else:
		log.debug('Master null exists. linking....')            
		self.i_masterNull = self.masterNull#Linking to instance for faster processing. Good idea?
		log.debug('self.i_masterNull: %s'%self.i_masterNull)
		self.i_masterNull.__verify__()
	    if self.i_masterNull.getShortName() != self.cgmName:
		self.masterNull.doName()
		if self.i_masterNull.getShortName() != self.cgmName:
		    log.warning("Master Null name still doesn't match what it should be.")
		    return False
	    attributes.doSetLockHideKeyableAttr(self.i_masterNull.mNode,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
	    log.debug("Master Null good...")
	except StandardError,error:
	    raise StandardError,"%s >>> MasterNull | error : %s"%(_str_funcName,error)	
	    
	try:#Quick select sets ================================================================
	    if not self.getMessage('puppetSet'):#
		i_selectSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
		i_selectSet.connectParentNode(self.mNode,'puppet','puppetSet')
	    
	    i_selectSet = self.puppetSet
	    cgmMeta.cgmAttr(self,'cgmName').doCopyTo(i_selectSet.mNode,connectTargetToSource =True)
	    i_selectSet.doName()	    
	    
	except StandardError,error:
	    raise StandardError,"%s >>> ObjectSet | error : %s"%(_str_funcName,error)
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Groups
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
	try:
	    log.debug(5)
	    for attr in 'deform','noTransform','geo','parts':
		grp = attributes.returnMessageObject(self.i_masterNull.mNode,attr+'Group')# Find the group
		Attr = 'i_' + attr+'Group'#Get a better attribute store string           
		if mc.objExists( grp ):
		    self.__dict__[Attr]  = r9Meta.MetaClass(grp)#initialize
		    log.debug("'%s' initialized as 'self.%s'"%(grp,Attr))
		else:#Make it
		    log.debug('Creating %s'%attr)                                    
		    self.__dict__[Attr]= cgmMeta.cgmObject(name=attr)#Create and initialize
		    self.__dict__[Attr].doName()
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
	except StandardError,error:
	    raise StandardError,"%s >>> groups |error : %s"%(_str_funcName,error)	
	    
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
	
	mc.rename(self.mNode,nameTools.returnCombinedNameFromDict(self.getNameDict()))
	    
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

    ##@r9General.Timer
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
    def getUnifiedGeo(self):
        return pFactory.getUnifiedGeo(self)
    
    def getModuleFromDict(self,*args,**kws):
	"""
	Pass a check dict of attributes and arguments. If that module is found, it returns it.
	checkDict = {'moduleType':'torso',etc}
	"""
	return pFactory.getModuleFromDict(self,*args,**kws)
    
    def getModules(self):
	"""
	Returns ordered modules. If you just need modules, they're always accessible via self.moduleChildren
	"""
	return pFactory.getModules(self)
    def gatherModules(self):
	"""
	Gathers all connected module children to the puppet
	"""
	return pFactory.gatherModules(self)
    def getState(self):
	"""
	Returns puppet state. That is the minimum state of it's modules
	"""
	return pFactory.getState(self) 
    
    def isCustomizable(self):
	return False 
    
    ##@r9General.Timer
    def _verifyMasterControl(self,**kws):
	""" 
	"""
	_str_funcName = "cgmPuppet._verifyMasterControl(%s)"%self.p_nameShort    
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
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
		kws['size'] = averageBBSize * 1.5
	    elif len(self.moduleChildren) == 1 and self.moduleChildren[0].getMessage('helper'):
		log.debug(">>> %s : Helper found.Sizing that."%_str_funcName)
		averageBBSize = distance.returnBoundingBoxSizeToAverage(self.moduleChildren[0].getMessage('helper'))		
		kws['size'] = averageBBSize * 1.5
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
	    nodeF.argsToNodes("%s.%sVis = if %s.%s > 0"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
	    nodeF.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
	
	#Geotype
	i_settings.addAttr('geoType',enumName = 'reg:proxy', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
	for i,attr in enumerate(['reg','proxy']):
	    nodeF.argsToNodes("%s.%sVis = if %s.geoType == %s:1 else 0"%(str_nodeShort,attr,str_nodeShort,i)).doBuild()    
	
	#Divider
	i_settings.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)
	
	#i_settings.addAttr('templateVis',attrType = 'float',lock=True,hidden = True)
	#i_settings.addAttr('templateLock',attrType = 'float',lock=True,hidden = True)	
	#i_settings.addAttr('templateStuff',enumName = 'off:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
	#nodeF.argsToNodes("%s.templateVis = if %s.templateStuff > 0"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()
	#nodeF.argsToNodes("%s.templateLock = if %s.templateStuff == 1:0 else 2"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()	
	

	#>>> Deform group
	#=====================================================================	
	if self.masterNull.getMessage('deformGroup'):
	    self.masterNull.deformGroup.parent = i_masterControl.mNode
	
	i_masterControl.addAttr('cgmAlias','world',lock = True)
	
	
	#>>> Skeleton Group
	#=====================================================================	
	if not self.masterNull.getMessage('skeletonGroup'):
	    #Make it and link it
	    i_grp = i_masterControl.doDuplicateTransform()
	    i_grp.doRemove('cgmName')
	    i_grp.addAttr('mClass','cgmObject',lock=True)	    
	    i_grp.addAttr('cgmTypeModifier','skeleton',lock=True)	 
	    i_grp.parent = i_masterControl.mNode
	    self.masterNull.connectChildNode(i_grp,'skeletonGroup','module')
	    
	    i_grp.doName()
	    
	self._i_skeletonGroup = self.masterNull.skeletonGroup	

	#Verify the connections
	self._i_skeletonGroup.overrideEnabled = 1             
	cgmMeta.cgmAttr(i_settings,'skeletonVis',lock=False).doConnectOut("%s.%s"%(self._i_skeletonGroup.mNode,'overrideVisibility'))    
	cgmMeta.cgmAttr(i_settings,'skeletonLock',lock=False).doConnectOut("%s.%s"%(self._i_skeletonGroup.mNode,'overrideDisplayType'))    
	    
	
	#>>>Connect some flags
	#=====================================================================
	i_geoGroup = self.masterNull.geoGroup
	i_geoGroup.overrideEnabled = 1		
	cgmMeta.cgmAttr(i_settings.mNode,'geoVis',lock=False).doConnectOut("%s.%s"%(i_geoGroup.mNode,'overrideVisibility'))
	cgmMeta.cgmAttr(i_settings.mNode,'geoLock',lock=False).doConnectOut("%s.%s"%(i_geoGroup.mNode,'overrideDisplayType'))    
	
	
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
    ##@r9General.Timer    
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

    ##@r9General.Timer    
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
		
    ##@r9General.Timer
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
    ##@r9General.Timer
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
	
    ##@r9General.Timer
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
    
    ##@r9General.Timer
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
    ##@r9General.Timer	    
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
	
    ##@r9General.Timer	
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
    
    ##@r9General.Timer
    def rebuildControlCurve(self, size = None,font = None,**kws):
	"""
	Rebuild the master control curve
	"""
	log.debug('>>> rebuildControlCurve')
	ml_shapes = cgmMeta.validateObjListArg( self.getShapes(),noneValid=True )
	self.color =  modules.returnSettingsData('colorMaster',True)
	
	#>>> Figure out the control size 	
	if size == None:#
	    if ml_shapes:
		absSize =  distance.returnAbsoluteSizeCurve(self.mNode)
		size = max(absSize)
	    else:size = 125
	#>>> Figure out font	
	if font == None:#
	    if kws and 'font' in kws.keys():font = kws.get('font')		
	    else:font = 'arial'
	#>>> Delete shapes
	if ml_shapes:
	    for s in ml_shapes:s.delete()	
		
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
    ##@r9General.Timer    
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
		
    ##@r9General.Timer
    def __verify__(self,*args,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
	_str_funcName = "cgmModuleBufferNode.__verify__(%s)"%(self.p_nameShort)
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)  
	
	cgmMeta.cgmBufferNode.__verify__(self,**kws)
	
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
        #self.addAttr('cgmTypeModifier',initialValue = bufferType,lock=True)
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

rigNullAttrs_toMake = {'version':'string',#Attributes to be initialzed for any module
                       'fk':'bool',
                       'ik':'bool',
                       'gutsLock':'int',
                       'gutsVis':'int',                       
                       'skinJoints':'message',
                       'dynSwitch':'messageSimple'}

templateNullAttrs_toMake = {'version':'string',
                            'gutsLock':'int',
                            'gutsVis':'int',
                            'controlsVis':'int',
                            'controlsLock':'int',
                            'root':'messageSimple',#The module root                            
                            'handles':'int',                            
                            'templateStarterData':'string',#this will be a json dict
                            'controlObjectTemplatePose':'string'}

class cgmModule(cgmMeta.cgmObject):
    ##@r9General.Timer
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
        log.debug("'%s' Checks out!"%self.getShortName())
	
    ##@r9General.Timer
    def initialize(self,**kws):
        """ 
        Initializes the various components a moduleNull for a character/asset.

        RETURNS:
        success(bool)
        """  
	_str_funcName = "cgmModule.initialize(%s)"%(self.p_nameShort)
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)  	
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
	    """
	    try: 		
		i_buffer = r9Meta.MetaClass(obj)
	    except StandardError,error:
		log.error("buffer failed ('%s') failed: %s"%(attr,error))		
		return False
	    
	    if not issubclass(type(i_buffer),cgmModuleBufferNode):
		return False	
	    #If we get here, link it
	    
	    self.__dict__[Attr] = i_buffer"""
           	
        return True # Experimetning, Don't know that we need to check this stuff as it's for changing info, not to be used in process

    ##@r9General.Timer
    def __verify__(self,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """
	_str_funcName = "cgmModule.__verify__(%s)"%(self.p_nameShort)
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)  	
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
        self.addAttr('deformNull',attrType='messageSimple',lock=True)	
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
	self.__verifyAttributesOn__(self.i_rigNull,rigNullAttrs_toMake)
	self.__verifyAttributesOn__(self.i_templateNull,templateNullAttrs_toMake)
	
	"""
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
		"""
	#Set Module Parent if we have that kw
	#=================		
	if self.kw_moduleParent:
	    self.doSetParentModule(self.kw_moduleParent)
	    	
        return True
    
    #@cgmGeneral.Timer
    def __verifyAttributesOn__(self,null,dictToUse):
        #Attrbute checking
        #=================
	log.debug(">>> %s.__verifyAttributesOn__ >> "%(self.p_nameShort) + "="*75)            	        	
	if type(dictToUse) is not dict:
	    raise StandardError,"Not a dict: %s"%null
	i_null = cgmMeta.validateObjArg(null)
	if not i_null:
	    raise StandardError,"Not a valid object: %s"%dictToUse	
	
        for attr in sorted(dictToUse.keys()):#See table just above cgmModule
	    try:
		log.debug("Checking '%s' on template Null"%attr)	
		if attr == 'rollJoints':
		    log.debug(self.kw_rollJoints)
		    if self.kw_rollJoints == 0:
			i_null.addAttr(attr,initialValue = self.kw_rollJoints, attrType = dictToUse[attr],lock = True )                
		    else:
			i_null.addAttr(attr,initialValue = self.kw_rollJoints, attrType = dictToUse[attr],lock = True )                		    	    
		elif attr == 'handles':
		    if self.kw_handles == 1:
			i_null.addAttr(attr,initialValue = self.kw_handles, attrType = dictToUse[attr],lock = True,min = 1 )                
		    else:
			i_null.addAttr(attr,initialValue = self.kw_handles, attrType = dictToUse[attr],lock = True,min = 1 )                
		elif attr == 'rollOverride':
		    i_null.addAttr(attr,initialValue = '{}', attrType = dictToUse[attr],lock = True )                                
		else:
		    i_null.addAttr(attr,attrType = dictToUse[attr],lock = True )   
	    except StandardError,error:
		log.error(">>> %s.%s >> failed: %s"%(self.p_nameShort,attr,error))     
		
    def __verifyObjectSet__(self):
	_str_funcName = "__verifyObjectSet__(%s)"%self.p_nameShort
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)		
	try:#Quick select sets ================================================================
	    if not self.rigNull.getMessage('moduleSet'):#
		i_selectSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
		i_selectSet.connectParentNode(self.rigNull.mNode,'rigNull','moduleSet')
	    
	    i_selectSet = self.rigNull.moduleSet
	    i_selectSet.doStore('cgmName',self.mNode)
	    i_selectSet.doName()
	    
	    if self.getMessage('modulePuppet'):
		self.modulePuppet.puppetSet.addObj(i_selectSet.mNode)
	    
	except StandardError,error:
	    raise StandardError,"%s >>> ObjectSet | error : %s"%(_str_funcName,error)
    
    def getModuleColors(self):
        direction = search.returnTagInfo(self.mNode,'cgmDirection')
        if not direction:
            return modules.returnSettingsData('colorCenter',True)
        else:
            return modules.returnSettingsData(('color'+direction.capitalize()),True)
    
    def getPartNameBase(self):
	return nameTools.returnRawGeneratedName(self.mNode, ignore = ['cgmType'])
    
    def getSettingsControl(self):
	"""
	Call to figure out a module's settings control
	"""
	_str_funcName = "getSettingsControl(%s)"%self.p_nameShort
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)  
	mi_rigNull = self.rigNull#Link
	try:
	    return mi_rigNull.settings#fastest check
	except:log.debug("%s >>> No settings connected. Probably not rigged, so let's check ..."%_str_funcName)
	if self.moduleType in l_faceModuleTypes:
	    log.debug("%s >>> Face module..."%_str_funcName)
	    try:return self.moduleParent.rigNull.settings#fastest check
	    except:log.debug("%s >>> No moduleParent settings connected..."%_str_funcName)	    
	    try:return self.modulePuppet.masterControl.controlSettings#fastest check
	    except:log.debug("%s >>> No masterControl settings found..."%_str_funcName)	    
	    
	log.error("%s >>> Unable to find settings control."%(_str_funcName))
	return False
    
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
    
    def doSkeletonize(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doSkeletonize)
        """
        return mFactory.doSkeletonize(self)
    def skeletonDelete(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.deleteSkeleton)
        """
        return mFactory.deleteSkeleton(self)
    
    #>>> Rig
    #===========================================================
    def doRig(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doRig)
        """
        return mFactory.doRig(self,*args,**kws)
    
    def isRigged(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isRigged)
        """
        return mFactory.isRigged(self,**kws)  
    
    def isRigConnected(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isRigConnected)
        """
        return mFactory.isRigConnected(self,**kws)  
    
    def rigConnect(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rigConnect)
        """
        return mFactory.rigConnect(self,**kws) 
    
    def rigDisconnect(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rigDisconnect)
        """
        return mFactory.rigDisconnect(self,**kws)  
    
    def rigDelete(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rigDisconnect)
        """
        return mFactory.rigDelete(self,**kws)     
    
    def rig_getReport(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rig_getReport)
        """
        return mFactory.rig_getReport(self)  
    
    def rig_getSkinJoints(self,asMeta = True):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rig_getSkinJoints)
        """
        return mFactory.rig_getSkinJoints(self,asMeta)  
    
    def rig_getHandleJoints(self,asMeta = True):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rig_getHandleJoints)
        """
        return mFactory.rig_getHandleJoints(self,asMeta)
    
    def rig_getRigHandleJoints(self,asMeta = True):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rig_getRigHandleJoints)
        """
        return mFactory.rig_getRigHandleJoints(self,asMeta)      
    
    def get_rollJointCountList(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.get_rollJointCountList)
        """
        return mFactory.get_rollJointCountList(self)     
    
    #>>> Animation
    #========================================================================
    def animKey(self,**kws):
	try:
	    buffer = self.rigNull.msgList_getMessage('controlsAll')
	    if buffer:
		mc.select(buffer)
		mc.setKeyframe(**kws)
		return True
	    return False
	except StandardError,error:
	    log.error("%s.animKey>> animKey fail | %s"%(self.getBaseName(),error))
	    return False
    def animSelect(self,**kws):
	try:
	    buffer = self.rigNull.msgList_getMessage('controlsAll')
	    if buffer:
		mc.select(buffer)
		return True
	    return False
	except StandardError,error:
	    log.error("%s.animSelect>> animSelect fail | %s"%(self.getBaseName(),error))
	    return False
	
    #>>> Module Children
    #========================================================================
    def getAllModuleChildren(self):
	return mFactory.getAllModuleChildren(self)
		
    def animKey_children(self,**kws):
	mFactory.animKey_children(self,**kws)

    def animSelect_children(self,**kws):
	mFactory.animSelect_children(self,**kws)

    def dynSwitch_children(self,arg):
	mFactory.dynSwitch_children(self,arg)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Limb stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
d_limb_rigNullAttrs_toMake = {'stretchy':'bool',
                              'bendy':'bool',
                              'twist':'bool'}

d_limb_templateNullAttrs_toMake = {'rollJoints':'int',#How many splits per segement
                                   'rollOverride':'string',#Override
                                   'curveDegree':'int',#Degree of the template curve, 0 for purely point to point curve
                                   'posObjects':'message',#Not 100% on this one
                                   'controlObjects':'message',#Controls for setting the template
                                   'curve':'messageSimple',#Module curve
                                   'orientHelpers':'messageSimple',#Orientation helper controls
                                   'orientRootHelper':'messageSimple',#Root orienation helper
                                   }

limbTypes = {'segment':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'finger':{'handles':5,'rollOverride':'{"0":1}','curveDegree':0,'rollJoints':0},
             'clavicle':{'handles':1,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'arm':{'handles':3,'rollOverride':'{}','curveDegree':0,'rollJoints':3},
             'leg':{'handles':4,'rollOverride':'{}','curveDegree':2,'rollJoints':3},
             'legSimple':{'handles':3,'rollOverride':'{}','curveDegree':2,'rollJoints':3}, 
             'armSimple':{'handles':3,'rollOverride':'{}','curveDegree':2,'rollJoints':3},                          
             'torso':{'handles':5,'rollOverride':'{"-1":0,"0":0}','curveDegree':2,'rollJoints':2},
             'tail':{'handles':5,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'head':{'handles':1,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'neckHead':{'handles':2,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'foot':{'handles':3,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'hand':{'handles':1,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'thumb':{'handles':4,'rollOverride':'{}','curveDegree':1,'rollJoints':0}                          
             }

class cgmLimb(cgmModule):
    #@cgmGeneral.Timer    
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
	    
	#>>> Attributes ...
	self.__verifyAttributesOn__(self.i_rigNull,d_limb_rigNullAttrs_toMake)
	self.__verifyAttributesOn__(self.i_templateNull,d_limb_templateNullAttrs_toMake)
	    
	settings = limbTypes[moduleType]
	if settings:
	    for attr in settings.keys():
		self.templateNull.addAttr(attr, value = settings[attr],lock = True) 
                                
        return True
    
#>>> Eyeball =====================================================================================================
d_eyeball_rigNullAttrs_toMake = {'irisControl':'bool',#Whether we should have a iris setup
                                 'pupilControl':'bool',#Whether we should have a pupil control
                                 }

d_eyeball_templateNullAttrs_toMake = {}

class cgmEyeball(cgmModule):
    #@cgmGeneral.Timer    
    def __init__(self,*args,**kws):
        """ 
        Intializes an eyeball master class handler
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
	_str_funcName = "cgmEyeball.__init__"    
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
	if kws:log.debug("%s >>> kws: %s"%(_str_funcName,str(kws)))         
	if args:log.debug("%s >>> args: %s"%(_str_funcName,str(args))) 
               
        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']
        super(cgmEyeball, self).__init__(*args,**kws) 

    def __verify__(self,**kws):
        cgmModule.__verify__(self,**kws)
	moduleType = kws.pop('mType','eyeball')	

        if self.moduleType != moduleType:
            log.debug("Changing type to '%s' type"%moduleType)
	self.moduleType = moduleType
	
	#>>> Attributes ...
	self.__verifyAttributesOn__(self.i_rigNull,d_eyeball_rigNullAttrs_toMake)
	self.__verifyAttributesOn__(self.i_templateNull,d_eyeball_templateNullAttrs_toMake)
	
	settings = {'handles': 1}
	if settings:
	    for attr in settings.keys():
		self.templateNull.addAttr(attr, value = settings[attr],lock = True)   
        return True

#>>> Eyelids =====================================================================================================
d_eyelids_rigNullAttrs_toMake = {}
d_eyelids_templateNullAttrs_toMake = {}

class cgmEyelids(cgmModule):
    #@cgmGeneral.Timer    
    def __init__(self,*args,**kws):
	""" 
	Intializes an eyelids master class handler
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
	_str_funcName = "cgmEyelids.__init__"    
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
	if kws:log.debug("%s >>> kws: %s"%(_str_funcName,str(kws)))         
	if args:log.debug("%s >>> args: %s"%(_str_funcName,str(args))) 
	       
	if 'name' not in kws.keys() and 'mType' in kws.keys():
	    kws['name'] = kws['mType']
	super(cgmEyelids, self).__init__(*args,**kws) 

    def __verify__(self,**kws):
	cgmModule.__verify__(self,**kws)
	moduleType = kws.pop('mType','eyelids')	

	if self.moduleType != moduleType:
	    log.debug("Changing type to '%s' type"%moduleType)
	self.moduleType = moduleType
	
	#>>> Attributes ...
	self.__verifyAttributesOn__(self.i_rigNull,d_eyelids_rigNullAttrs_toMake)
	self.__verifyAttributesOn__(self.i_templateNull,d_eyelids_templateNullAttrs_toMake)
	
	settings = {'handles': 5}
	if settings:
	    for attr in settings.keys():
		self.templateNull.addAttr(attr, value = settings[attr],lock = True)   
	return True

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Rig Blocks
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
d_rigBlockAttrs_toMake = {'version':'string',#Attributes to be initialzed for any module
                          'buildAs':'string',
                          'autoMirror':'bool',
                          'direction':'left:right:center',
                          'position':'none:front:back:upper:lower:forward',
                          'moduleTarget':'messageSimple',
                          'blockMirror':'messageSimple'}

class cgmRigBlock(cgmMeta.cgmObject):
    ##@r9General.Timer
    def __init__(self,*args,**kws):
	""" 
	The root of the idea of cgmRigBlock is to be a sizing mechanism and build options for
	our modular rigger.
	
	Args:
	node = existing module in scene
	name = treated as a base name

	"""
	_str_funcName = "cgmRigBlock.__init__"    
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
	if kws:log.debug("%s >>> kws: %s"%(_str_funcName,str(kws)))         
	if args:log.debug("%s >>> args: %s"%(_str_funcName,str(args)))    
		
	#>>Verify or Initialize
	super(cgmRigBlock, self).__init__(*args,**kws) 

	#Keywords - need to set after the super call
	#==============         
	__doVerify__ = kws.get('doVerify') or False
	
	
	self.kw_name= kws.get('name') or False        
	self.kw_moduleParent = kws.get('moduleParent') or False
	self.kw_forceNew = kws.get('forceNew') or False
	self.kw_initializeOnly = kws.get('initializeOnly') or False  
	self.kw_callNameTags = {'cgmPosition':kws.get('position') or False, 
                                'cgmDirection':kws.get('direction') or False, 
                                'cgmDirectionModifier':kws.get('directionModifier') or False,
                                'cgmNameModifier':kws.get('nameModifier') or False}
	
	#>>> Initialization Procedure ================== 
	if not self.isReferenced():
	    if self.__justCreatedState__ or __doVerify__:	    
		if not self.__verify__(**kws):
		    log.critical("'%s' failed to verify!"%self.mNode)
		    raise StandardError,"'%s' failed to verify!"%self.mNode 
		return
	log.debug("'%s' Checks out!"%self.getShortName())
	
    ##@r9General.Timer
    def __verify__(self,**kws):
	""""""
	""" 
	Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

	RETURNS:
	success(bool)
	"""
	_str_funcName = "cgmRigBlock.__verify__"    
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
	
	#>>> Block transform ==================                   
	self.addAttr('mClass', initialValue='cgmRigBlock',lock=True) 
	self.addAttr('cgmType',value = 'rigHelper',lock=True)	
	
	if self.kw_name:#If we have a name, store it
	    self.addAttr('cgmName',self.kw_name,attrType='string',lock=True)
	elif 'buildAs' in kws.keys():
	    self.addAttr('cgmName',kws['buildAs'],attrType='string',lock=True)	    

	#Store tags from init call
	#==============  
	for k in self.kw_callNameTags.keys():
	    if self.kw_callNameTags.get(k):
		log.debug(k + " : " + str(self.kw_callNameTags.get(k)))                
		self.addAttr(k,value = self.kw_callNameTags.get(k),lock = True)
		log.debug(str(self.getNameDict()))
		log.debug(self.__dict__[k])


	#Attrbute checking
	#=================
	self.verifyAttrDict(d_rigBlockAttrs_toMake,keyable = False, hidden = False)
	log.debug("%s.__verify__ >>> kw_callNameTags: %s"%(self.p_nameShort,self.kw_callNameTags))	    	
	d_enumToCGMTag = {'cgmDirection':'direction','cgmPosition':'position'}
	for k in d_enumToCGMTag.keys():
	    log.debug("%s.__verify__ >>> trying to set key: %s"%(self.p_nameShort,k))	    
	    if k in self.kw_callNameTags.keys():
		log.debug("%s.__verify__ >>> trying to set key: %s | data: %s"%(self.p_nameShort,k,self.kw_callNameTags.get(k)))
		try:self.__setattr__(d_enumToCGMTag.get(k),self.kw_callNameTags.get(k))
		except StandardError,error: log.error("%s.__verify__ >>> Failed to set key: %s | data: %s | error: %s"%(self.p_nameShort,k,self.kw_callNameTags.get(k),error))
	
	self.doName()   
	
	return True
    
    def __verifyModule__(self):
	""" 
	Verify
	"""
	_str_funcName = "cgmRigBlock.__verifyModule__"    
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)
	
	#First see if we have a module
	if not self.getMessage('mi_module'):
	    log.debug(">>> %s >>> No module found. Building... "%(_str_funcName))
	    self.__buildModule__()
	return True
	    
    def __buildModule__(self):
	"""
	General Module build before expected pass to individual blocks for specialization
	"""
	_str_funcName = "cgmRigBlock.__buildModule__(%s)"%self.p_nameShort   
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)
	
	#>>> Gather basic info for module build
	d_kws = {}
	d_kws['name'] = self.cgmName
	#Direction
	str_direction = self.getEnumValueString('direction')
	if str_direction in ['left','right']:
	    d_kws['direction'] = str_direction
	#Position
	str_position = self.getEnumValueString('position')	    
	if str_position != 'none':
	    d_kws['position'] = str_position
	    
	log.debug(">>> %s >>> kws..."%(_str_funcName)) 
	for k in d_kws.keys():
	    log.debug("%s : %s"%(k,d_kws.get(k)))
	self._d_buildKWS = d_kws    
	
	#>>>Initial module build in 
	log.debug(">>> %s >>> passing..."%(_str_funcName))
    
    #@cgmGeneral.Timer
    def __buildSimplePuppet__(self):
	"""
	Build a simple puppet for itself
	"""
	_str_funcName = "cgmRigBlock.__buildSimplePuppet__(%s)"%self.p_nameShort   
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)
	mi_module = self.moduleTarget
	if not mi_module:
	    try:
		log.debug(">>> %s >>> Has no module, creating")
		mi_module = self.__buildModule__()
	    except StandardError,error:
		raise StandardError, ">>> %s>>> module build failed. error: %s"%(_str_funcName,error)
	if mi_module.getMessage('modulePuppet'):
	    log.debug(">>> %s >>> already has a puppet. Aborting"%_str_funcName)
	    return False
	
	log.debug(">>> %s >>> Building puppet..."%(_str_funcName))
	mi_puppet = cgmPuppet(name = mi_module.getNameAlias())
	mi_puppet.connectModule(mi_module)	
	if mi_module.getMessage('moduleMirror'):
	    mi_puppet.connectModule(mi_module.moduleMirror)
	mi_puppet.gatherModules()#Gather any modules in the chain
	return mi_puppet
	
	
	    
	    
    def __updateSizeData__(self):
	"""For overload"""
	pass
    
class cgmEyeballBlock(cgmRigBlock):
    d_attrsToMake = {'buildIris':'bool',
                     'buildPupil':'bool',
                     'buildLids':'bool',
                     'uprLidJoints':'int',
                     'lwrLidJoints':'int',
                     'pupilHelper':'messageSimple',
                     'irisHelper':'messageSimple',
                     'uprLidHelper':'messageSimple',
                     'lwrLidHelper':'messageSimple',
                     'moduleEyelids':'messageSimple'} 
    d_defaultSettings = {'buildIris':True,'buildPupil':True,'buildLids':True,
                         'uprLidJoints':5,'lwrLidJoints':5}
    d_helperSettings = {'iris':{'plug':'irisHelper','check':'buildIris'},
                        'pupil':{'plug':'pupilHelper','check':'buildIris'}}

    #@cgmGeneral.Timer    
    def __init__(self,*args,**kws):
        """ 
        """
	_str_funcName = "cgmEyeballBlock.__init__"  
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)
        if kws:log.debug("kws: %s"%str(kws))         
        if args:log.debug("args: %s"%str(args))  
               
        if 'name' not in kws.keys():
            kws['name'] = 'eye'  
        super(cgmEyeballBlock, self).__init__(*args,**kws) 

    #@cgmGeneral.Timer
    def __verify__(self,**kws):
	_str_funcName = "cgmEyeballBlock.__verify__(%s)"%self.p_nameShort    
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
        cgmRigBlock.__verify__(self,**kws)
	
	if self.isReferenced():
	    raise StandardError,"%s >>> is referenced. Cannot verify"%_str_funcName

	#>>> Attributes ..
	self.addAttr('buildAs','cgmEyeball',lock=True)
	self.verifyAttrDict(cgmEyeballBlock.d_attrsToMake,keyable = False, hidden = False)
	for attr in cgmEyeballBlock.d_defaultSettings.keys():
	    try:self.addAttr(attr, value = cgmEyeballBlock.d_defaultSettings[attr], defaultValue = cgmEyeballBlock.d_defaultSettings[attr])
	    except StandardError,error: raise StandardError,"%s.__verify__ >>> Failed to set value on: %s | data: %s | error: %s"%(self.p_nameShort,attr,cgmEyeballBlock.d_defaultSettings[attr],error)
	if not self.getShapes():
	    self.__rebuildShapes__()
	    
	self.doName()        
        return True

    #@cgmGeneral.Timer
    def __rebuildShapes__(self,size = None):
	_str_funcName = "cgmEyeballBlock.__rebuildShapes__(%s)"%self.p_nameShort   
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
	if self.isReferenced():
	    raise StandardError,"%s >>> is referenced. Cannot verify"%_str_funcName
	
	l_shapes = self.getShapes()
	if l_shapes:
	    mc.delete(l_shapes)
	    
	ml_shapes = cgmMeta.validateObjListArg( self.getShapes(),noneValid=True )
	self.color = getSettingsColors( self.getAttr('cgmDirection') )
	
	#>>> Figure out the control size 	
	if size is None:#
	    if l_shapes:
		absSize =  distance.returnAbsoluteSizeCurve(self.mNode)
		size = max(absSize)
	    else:size = 10
	    
	#>>> Delete shapes
	if l_shapes:
	    log.debug("%s >>> deleting: %s"%(_str_funcName,l_shapes))	    
	    mc.delete(ml_shapes)
	
	#>>> Build the eyeorb
	l_curveShapes = []
	l_curveShapes.append(mc.curve( d = 3,p = [[-1.9562614856650922e-17, 0.27234375536457955, 0.42078583109797302], [3.6231144545942155e-17, 0.44419562780377575, 0.2927550836423139], [1.2335702099837762e-16, 0.55293025498339243, -0.0036181380792718819], [1.4968222251671369e-16, 0.38920758821246809, -0.39338278937226923], [8.8443099225711831e-17, -0.0024142895734145229, -0.55331090087007562], [-2.4468224144040798e-17, -0.39262563725601413, -0.38997137672626969], [-1.2297164287833005e-16, -0.55294077490394233, 0.0012071651865769651], [-1.6080353342952326e-16, -0.44037303463385957, 0.29661659753593533], [-1.3886669551328167e-16, -0.27181045164087791, 0.42314656824251157]],k = (1.0, 1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.0, 7.0)))
	l_curveShapes.append(mc.curve( d = 3,p = [[0.27234375536457939, 1.734683000445787e-16, 0.42078583109797307], [0.44419562780377558, 1.2740478502632556e-16, 0.29275508364231401], [0.55293025498339232, -1.3852290198695529e-18, -0.0036181380792717592], [0.38920758821246809, -1.5060930340872423e-16, -0.39338278937226911], [-0.0024142895734143997, -2.1183887958462436e-16, -0.55331090087007562], [-0.3926256372560139, -1.4930322064116459e-16, -0.3899713767262698], [-0.55294077490394222, 4.6217148477624099e-19, 0.0012071651865768424], [-0.44037303463385952, 1.2888319214868455e-16, 0.29661659753593522], [-0.27117872614283267, 1.7437212447837615e-16, 0.42314656824251151]],k = (1.0, 1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.0, 7.0)))
	l_curveShapes.append(mc.curve( d = 3,p = [[9.7144514654701197e-17, -0.27151128700632393, 0.4226944232293004], [0.071575100224478827, -0.27101472617476752, 0.42269442322930045], [0.21517305056594385, -0.2111533666759117, 0.4226944232293004], [0.30072197725858107, 0.00196779544506197, 0.42269442322930029], [0.21167818985563105, 0.21394895499628236, 0.42269442322930018], [-0.0013130587947546969, 0.30092899899893094, 0.42269442322930012], [-0.21353716294939432, 0.21209359123764582, 0.42269442322930018], [-0.30072769872395522, -0.0006565404922469105, 0.42269442322930029], [-0.21332222008560683, -0.2130230418667757, 0.4226944232293004], [-0.069207355235434434, -0.27162900941733881, 0.42269442322930045], [1.1410775855283418e-16, -0.27151128700632399, 0.4226944232293004]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
	l_curveShapes.append(mc.curve( d = 3,p = [[0.0, -0.49825526937946768, 2.2126978888235788e-16], [0.131348759885549, -0.49734402162391972, 3.0084413217208814e-16], [0.39486795357586341, -0.38749135902787507, 2.3439409455508664e-16], [0.55186033493999953, 0.0036111369820883686, -2.1843820862340872e-18], [0.38845447152927703, 0.39262159367483379, -2.3749738105919298e-16], [-0.002409617923089843, 0.552240244276892, -3.3405093821679339e-16], [-0.39186590664792353, 0.38921678211230448, -2.3543780552354256e-16], [-0.55187083450450314, -0.0012048293219408162, 7.2880303374564086e-19], [-0.39147146111426462, -0.39092243375831293, 2.3646955671973833e-16], [-0.12700366826764278, -0.49847130390333205, 3.0152602688544059e-16], [3.1129555427347658e-17, -0.49825526937946774, 2.2126978888235788e-16]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
	str_orb = curves.combineCurves(l_curveShapes)	
	
	curves.parentShapeInPlace(self.mNode,str_orb)#parent shape in place	
	curves.setCurveColorByName(self.mNode,self.color[0])#Set the color	    	
	mc.delete(str_orb)	
	
	#>>>Build the Iris and pupil
	l_buildOrder = ['pupil','iris','uprLid','lwrLid']
	d_buildCurves = {'pupil':mc.circle(normalZ = 1,radius = .09)[0],
	                 'iris':mc.circle(normalZ = 1,radius = .18)[0],
	                 'uprLid': mc.curve( d = 7,p = [[-0.44983530883670614, -0.071322594849904483, 0.36447022867017792], [-0.41829822121153859, -0.076896548997831424, 0.36029350648460373], [-0.37965007473058976, -0.068979541432776223, 0.38851433033177529], [-0.30723268320699781, 0.069290384212930434, 0.47810854649572376], [-0.17722744036745491, 0.18746372246544851, 0.59390774699001958], [0.10824468618298072, 0.21321584685485462, 0.584725411742131], [0.3298348785746214, 0.15455892134311355, 0.47446094679578343], [0.45662395681608442, 0.0061289393759054178, 0.32035084692498095], [0.45876148344130957, -0.081023121388213326, 0.25124022530758361]],k = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0)),
	                 'lwrLid':mc.curve( d = 7,p = [[-0.45053674825700091, -0.073162071798690526, 0.36480978291355348], [-0.42304044071766306, -0.067231612899713564, 0.3610575914584816], [-0.39997680161862192, -0.077368790745462476, 0.38742660957006148], [-0.27603943705561623, -0.19069469101646774, 0.4998691161966955], [-0.14516156462612845, -0.2266921348862958, 0.57038517412610701], [0.10764440316710838, -0.24084200820627188, 0.55850510170499423], [0.32024605633174202, -0.20780685290092293, 0.4559870301884088], [0.43357025439741831, -0.10483423978152118, 0.28188913131160498], [0.46005845201487922, -0.083167671103495877, 0.24918293340572251]],k = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0)),
	                 }
	ml_curves = []
	md_curves = {}
	for k in l_buildOrder:
	    str_return = d_buildCurves.get(k)
	    mi_obj = cgmMeta.cgmObject(str_return,setClass=True)#instance
	    mi_obj.addAttr('cgmName',k)#tag
	    mi_obj.addAttr('cgmType',value = 'rigHelper',lock=True)		    
	    curves.setCurveColorByName(mi_obj.mNode,self.color[0])#Set the color	    			
	    ml_curves.append(mi_obj)#append
	    md_curves[k] = mi_obj
	    mi_obj.doName()#Name	

	    if k in ['uprLid','lwrLid']:
		mi_obj.doCopyPivot(self)
		
	    self.connectChildNode(mi_obj,'%sHelper'%k,'mi_block')
	        
	#Second pass on doing parenting and some lock work
	for k in md_curves.keys():
	    mi_obj = md_curves.get(k)
	    if k == 'pupil':
		mi_obj.parent = md_curves.get('iris')		
	    else:
		mi_obj.parent = self.mNode#parent to inherit names
	    if k in ['iris','pupil']:
		mi_obj.tz = .46
		mc.makeIdentity(mi_obj.mNode,apply=True,t=1,r=1,s=1,n=0)
		
	    cgmMeta.cgmAttr(mi_obj,'sx').doConnectIn("%s.scaleY"%mi_obj.mNode)
	    attributes.doSetLockHideKeyableAttr(mi_obj.mNode,lock=True,visible=False,keyable=False,channels=['tx','ty','rx','ry','rz','sx','sz','v'])
		 	
	#Connect in our scales so we're scaling the eye one one channel
	cgmMeta.cgmAttr(self,'sx').doConnectIn("%s.scaleY"%self.mNode)
	cgmMeta.cgmAttr(self,'sz').doConnectIn("%s.scaleY"%self.mNode)
	for a in ['sx','sz','rotate','v']:
	    cgmMeta.cgmAttr(self,a,keyable=False,lock=True,hidden=True)
	
	#attributes.doSetLockHideKeyableAttr(self.mNode,lock=True,visible=False,keyable=False,channels=['tx','ty','rx','ry','rz','sx','sz','v'])
    def __mirrorBuild__(self):
	cgmRigBlock.__buildModule__(self)
	_str_funcName = "cgmEyeballBlock.__buildMirror__(%s)"%self.p_nameShort   
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)	
	try:
	    try:#Mirror curves =====================================================================
		if not self.getMessage('blockMirror'):
		    mi_dup = self.doDuplicate(False)
		    l_pivot = mc.xform(self.mNode,q=True, sp = True,ws=True)
		    for a in ['lwrLid','uprLid']:
			mc.scale( -1,1,1,self.getMessageInstance("%sHelper"%a).getComponents('cv'),pivot = l_pivot ,  r=True)
		self.connectChildNode(mi_dup,"blockMirror","blockMirror")
		
		mi_dup.direction = not self.direction
		mi_dup.cgmDirection = mi_dup.getEnumValueString('direction')
		mi_dup.doName()
			
	    except StandardError,error:raise StandardError,"Failed to mirror mirror shapes | error: %s "%(error)
	    try:#Find our shapes =====================================================================
		l_shapes = ['iris','pupil','uprLid','lwrLid']
		ml_crvs = [mi_dup]
		l_children = mi_dup.getAllChildren(True)
		for c in l_children:
		    i_c = cgmMeta.cgmNode(c)
		    for shape in l_shapes:
			if i_c.getAttr('cgmName') == shape:
			    mi_dup.connectChildNode(i_c,'%sHelper'%shape,'mi_block')
			    ml_crvs.append(i_c)
	    except StandardError,error:raise StandardError,"Failed to mirror mirror shapes | error: %s "%(error)
	    try:#Color =====================================================================
		__color = getSettingsColors( mi_dup.getAttr('cgmDirection') )
		for mCrv in ml_crvs:
		    curves.setCurveColorByName(mCrv.mNode,__color[0])#Set the color	    
	    except StandardError,error:raise StandardError,"Color mirror| error: %s "%(error)
	    
	    self.__mirrorPush__()
	    return mi_dup
	except StandardError,error:raise StandardError,"%s >> | error: %s "%(_str_funcName,error)
	
    def __mirrorPush__(self):
	cgmRigBlock.__buildModule__(self)
	_str_funcName = "cgmEyeballBlock.__pushToMirror__(%s)"%self.p_nameShort   
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)
	try:
	    if not self.getMessage('blockMirror'):
		log.warning("%s >> no blockMirror found"%_str_funcName)
		return False
	    mi_mirror = self.blockMirror
	    
	    mi_mirror.tx = -self.tx
	    mi_mirror.ty = self.ty
	    mi_mirror.sy = self.sy
	    
	except StandardError,error:raise StandardError,"%s >> | error: %s "%(_str_funcName,error)
 
	
    def __buildModule__(self):
	cgmRigBlock.__buildModule__(self)
	_str_funcName = "cgmEyeballBlock.__buildModule__(%s)"%self.p_nameShort   
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)
	try:
	    bfr_name = self._d_buildKWS.get('name') or None
	    bfr_position = self._d_buildKWS.get('position') or None
	    bfr_direction = self._d_buildKWS.get('direction') or None
	    
	    try:#Eyeball module
		#===================================================================
		i_module = cgmEyeball(name = bfr_name,
		                      position = bfr_position,
		                      direction = bfr_direction)
		self.connectChildNode(i_module,"moduleTarget","helper")
	    except StandardError,error:raise StandardError,"Failed to build eyeball module | error: %s "%(error)
	    try:#Eyelids module
		#===================================================================
		i_eyelidsModule = cgmEyelids(name = 'eyelids',
		                           position = bfr_position,
		                           direction = bfr_direction)
		i_eyelidsModule.doSetParentModule(i_module)
		self.connectChildNode(i_eyelidsModule,"moduleEyelids","helper")
		
	    except StandardError,error:raise StandardError,"Failed to build eyelids module | error: %s "%(error)
	    try:#Mirror ============================================================
		if self.autoMirror:
		    log.info("%s >> mirror mode"%(_str_funcName))
		    if not self.getMessage('blockMirror'):
			mi_mirror = self.__mirrorBuild__()
		    else:
			mi_mirror = self.blockMirror
			bfr_mirrorDirection = mi_mirror.cgmDirection
		    
		    try:#Eyeball module
			#===================================================================
			i_moduleMirror = cgmEyeball(name = bfr_name,
			                            position = bfr_position,
			                            direction = bfr_mirrorDirection)
			i_module.connectChildNode(i_moduleMirror,"moduleMirror","moduleMirror")
			mi_mirror.connectChildNode(i_moduleMirror,"moduleTarget","helper")		    
		    except StandardError,error:raise StandardError,"Failed to mirror eyeball module | error: %s "%(error)
		    try:#Eyelids module
			#===================================================================
			i_eyelidsModuleMirror = cgmEyelids(name = 'eyelids',
			                                   position = bfr_position,
			                                   direction = bfr_mirrorDirection)
			i_eyelidsModuleMirror.doSetParentModule(i_moduleMirror)
			mi_mirror.connectChildNode(i_eyelidsModuleMirror,"moduleEyelids","helper")
		    except StandardError,error:raise StandardError,"Failed to mirror eyelids module | error: %s "%(error)
	    except StandardError,error:raise StandardError,"failed to mirror | error: %s "%(error)
	    
	    self.__storeNames__()
	    
	    #Size it
	    self.__updateSizeData__()
	    
	    #>>>Let's do our manual sizing
	    return i_module
	except StandardError,error:raise StandardError,"%s >>>  error: %s "%(_str_funcName,error)
    
    def __storeNames__(self):
	#Store our names
	_str_funcName = "cgmEyeballBlock.__storeNames__(%s)"%self.p_nameShort   	
	if not self.getMessage("moduleTarget"):
	    raise StandardError," %s >>> No Module!"%(_str_funcName)
	
	l_names= ['eyeball']
	if self.buildIris:l_names.append('iris')
	if self.buildPupil:l_names.append('pupil')
	self.moduleTarget.coreNames.value = l_names
	try:#Mirror ============================================================
	    if self.autoMirror:
		self.moduleTarget.moduleMirror.coreNames.value = l_names
	except StandardError,error:raise StandardError,"%s >>>  mirror error: %s "%(_str_funcName,error)

	return True
    
    def __updateSizeData__(self):
	"""For overload"""
	_str_funcName = "cgmEyeballBlock.__updateSizeData__(%s)"%self.p_nameShort   
	log.debug(">>> %s >>> "%(_str_funcName) + "="*75)
	if not self.getMessage('moduleTarget'):
	    raise StandardError,">>> %s >>> No module found "%(_str_funcName)
	
	i_module = self.mi_module#Lilnk
	l_pos = [self.getPosition()]
	d_helpercheck = cgmEyeballBlock.d_helperSettings#Link
	
	"""
	for k in d_helpercheck.keys():
	    try:
		if self.getAttr(d_helpercheck[k].get('check')) and self.getMessage(d_helpercheck[k].get('plug')):
		    l_pos.append(self.getMessageInstance(d_helpercheck[k].get('plug')).getPosition())
	    except StandardError,error:
		log.error(">>> %s >>> helper check failed: %s | error: %s"%(_str_funcName,k,error))	
	"""
	##ml_helpers = self.msgList_get('ml_helpers')#Get our helpers
	"""
	if self.buildPupil:
	    try:l_pos.append(self.pupilHelper.getPosition())
	    except StandardError,error:raise StandardError,"%s >>> Missing Pupil helper | error: %s "%(_str_funcName,error)
	if self.buildIris:
	    try:l_pos.append(self.irisHelper.getPosition())
	    except StandardError,error:raise StandardError,"%s >>> Missing Iris helper | error: %s "%(_str_funcName,error)
	
	log.info("%s >>> l_pos: %s"%(_str_funcName,l_pos))		

	#Push handles
	i_module.templateNull.handles = len(l_pos)
	
	i_module.doSize(sizeMode = 'manual',
	                 posList = l_pos)
	"""
	return True
	
		
	
	    
#Minor Utilities
def getSettingsColors(arg = None):
    try:
	return modules.returnSettingsData(('color'+arg.capitalize()),True)
    except:
	return modules.returnSettingsData('colorCenter',True)

	
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
r9Meta.registerMClassInheritanceMapping()
#=========================================================================
