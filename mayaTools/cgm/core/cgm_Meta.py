"""
------------------------------------------
cgm_Meta: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is the Core of the MetaNode implementation of the systems.
It is uses Mark Jackson (Red 9)'s as a base.
================================================================
"""

import maya.cmds as mc
import maya.mel as mel
import copy

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General


# From cgm ==============================================================
#from cgm.lib.classes import NameFactory as OLD_Name
#reload(OLD_Name)
from cgm.core.lib import nameTools
reload(nameTools)
from cgm.lib.ml import (ml_resetChannels)
reload(ml_resetChannels)

from cgm.lib import (lists,
                     search,
                     attributes,
                     distance,
                     constraints,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory,
                     locators)

reload(attributes)
reload(search)

# Shared Defaults ========================================================
drawingOverrideAttrsDict = {'overrideEnabled':0,
                            'overrideDisplayType':0,
                            'overrideLevelOfDetail':0,
                            'overrideShading':1,
                            'overrideTexturing':1,
                            'overridePlayback':1,
                            'overrideVisibility':1}
l_componentTypes = ['polyVertex','curveCV','surfaceCV','polyEdge','editPoint','isoparm','polyFace','polyUV','curvePoint','surfacePatch','nurbsUV']
l_cgmNameTags = ['cgmName','cgmNameModifier','cgmPosition','cgmDirection','cgmDirectionModifier','cgmIterator','cgmType','cgmTypeModifier']

#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================
from cgm.lib.classes import NameFactory as Old_Name#   TMP<<<<<<<<<<<<<<<<<<<<<<<<

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmMeta - MetaClass factory for figuring out what to do with what's passed to it
#=========================================================================    
class cgmMetaFactory(object):
    def __new__(self, node = None, name = None, nodeType = 'transform',*args,**kws):
        '''
        Idea here is if a MayaNode is passed in and has the mClass attr
        we pass that into the super(__new__) such that an object of that class
        is then instantiated and returned.
        '''	
        doName = None
        objectFlags = ['cgmObject','object','obj','transform']
            
        if not node and name: 
            node = name
        if not node and nodeType:
            node = True # Yes, make the sucker
 
        #If the node doesn't exists, make one 
        #==============           
        if node and not mc.objExists(node):#If we have a node and it exists, we'll initialize. Otherwise, we need to figure out what to make
            if nodeType in objectFlags:
                node = mc.createNode('transform')
                log.debug("Created a transform")
	    elif nodeType == 'optionVar':
		return cgmOptionVar(varName=name,*args,**kws)
            elif nodeType != 'network':
                log.debug("Trying to make a node of this type '%s'"%nodeType)
                node = mc.createNode(nodeType)
            else:
                log.debug("Make default node")
                node = mc.createNode('network')
	    
        if name and node != name and node != True:
            node = mc.rename(node, name)
            
        log.debug("In MetaFactory.__new__ Node is '%s'"%node)
        log.debug("In MetaFactory.__new__ Name is '%s'"%name) 
        log.debug("In MetaFactory.__new__ nodeType is '%s'"%nodeType)   
        
        #Process what to do with it
        #==============             
        mClass = attributes.doGetAttr(node,'mClass')
        if mClass:
            log.debug("Appears to be a '%s'"%mClass)
            log.debug("Specialized processing not implemented, initializing as...") 
	    
        objType = search.returnObjectType(node)
	if objType == 'objectSet':
            log.debug("'%s' Appears to be an objectSet, initializing as cgmObjectSet"%node)	    
	    return cgmObjectSet(node,*args,**kws)
        elif mc.ls(node,type='transform'):
            log.debug("'%s' Appears to be a transform, initializing as cgmObject"%node)
            return cgmObject(name = name, node = node,**kws)          
        else:
            log.debug("Appears to be a '%s'. Initializing as cgmNode"%objType)  
            return cgmNode(name = name, node = node,**kws)    
          
        return False
            
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmNode - subclass to Red9.MetaClass
#=========================================================================    
class cgmNode(r9Meta.MetaClass):#Should we do this? 
    def __bind__(self):
	"""
	Setup before maya object initialization
	"""
	self.referencePrefix = False
    def __init__(self,node = None, name = None,nodeType = 'network',setClass = False, *args,**kws):	
        """ 
        Utilizing Red 9's MetaClass. Intialized a node in cgm's system.
        """
        log.debug("In cgmNode.__init__ Node is '%s'"%node)
        log.debug("In cgmNode.__init__ Name is '%s'"%name) 
	
	#if node == None:
	    #log.info("Creating node of type '%s'"%nodeType)
	    #catch = cgmMeta(name = name, nodeType = nodeType,*args,**kws)
	    #node = catch.mNode
	    #log.info(node)
	if node is None or name is not None and mc.objExists(name):
	    createdState = True
	else:createdState = False
	
	#ComponentMode
	if node is not None and search.returnObjectType(node) in l_componentTypes:
	    componentMode = True
	    component = node.split('.')[-1]
	else:
	    componentMode = False
	    component = False
	
	super(cgmNode, self).__init__(node=node, name = name, nodeType = nodeType)
	self.UNMANAGED.extend(['__justCreatedState__','__componentMode__','__component__'])	
	self.__dict__['__justCreatedState__'] = createdState
	self.__dict__['__componentMode__'] = componentMode
	self.__dict__['__component__'] = component
	if setClass:
	    self.addAttr('mClass','cgmNode',lock=True)
	
	self.update()
        
    def __verify__(self):
	pass#For overload
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #parent
    #==============    
    def getParent(self):
	return search.returnParentObject(self.mNode) or False
    
    def getParent_asMObject(self):
	pBuffer = search.returnParentObject(self.mNode) or False
	if not pBuffer:
	    return False
        return r9Meta.MetaClass(pBuffer)
				
    parent = property(getParent)
    
    def __getattributeBACK__(self, attr, longNames = True, ignoreOverload = True):
	"""Overload just on message attributes
	longnames currently only for my overload.
	"""
	try:
	    mNode=object.__getattribute__(self, "_mNode")
	    if mc.objExists(mNode):
		if mc.attributeQuery(attr, exists=True, node=mNode):
		    if mc.getAttr('%s.%s' % (mNode,attr),type=True)  == 'message' and not ignoreOverload:
			return attributes.returnMessageData(self.mNode,attr,longNames)
		    else:
			return r9Meta.MetaClass.__getattribute__(self,attr)
		else:
		    return object.__getattribute__(self, attr)
	    return object.__getattribute__(self, attr)
	except StandardError,error:
	    raise StandardError(error)
	    
    def __setMessageAttr__(self,attr,value, force = True, ignoreOverload = False,**kws):
	"""Overload for our own purposes to allow multiple connections"""
	log.debug("In cgmNode.__setMessageAttr__...")
	if ignoreOverload:#just use Mark's
	    log.debug("sending cgmNode.__setMessageAttr__ to MetaClass...")
	    r9Meta.MetaClass.__setMessageAttr__(self,attr,value,**kws)
	elif type(value) is list:
	    log.debug("Multi message mode from cgmNode: '%s.%s"%(self.getShortName(),attr))
	    attributes.storeObjectsToMessage(value,self.mNode,attr)
	else:
	    attributes.storeObjectToMessage(value,self.mNode,attr)
	    
    def __setattr__(self,attr,value, force = True, lock = None, **kws):
	"""Overload for our own purposes to allow multiple connections"""
	log.debug("In cgmNode.__setattr__...")
	if lock is None:
	    try:
		if self.attrIsLocked(attr):
		    lock = True	    
	    except:pass
	try:r9Meta.MetaClass.__setattr__(self,attr,value,**kws)
	except StandardError,error:
	    raise StandardError, "%s.__setattr__: %s"%(self.getShortName(),error)
	if lock is not None and not self.isReferenced():
	    mc.setAttr(('%s.%s'%(self.mNode,attr)),lock=lock)	  
	    
    def getMessage(self,attr,longNames = True):
	"""
	This maybe odd to some, but we treat traditional nodes as regular message connections. However, sometimes, you want a message like connection
	to an attribute. To do this, we devised a method of creating a compaptble attr on the object to recieve the message, 
	connecting the attribute you want to connect to that attribute and then when you call an attribute as getMessage, if it is not a message attr
	it tries to trace back that connection to an attribute.
	"""
	if mc.objExists('%s.%s' % (self.mNode,attr)) and mc.getAttr('%s.%s' % (self.mNode,attr),type=True)  == 'message':
	    return attributes.returnMessageData(self.mNode,attr,longNames) or []
	elif mc.objExists('%s.%s' % (self.mNode,attr)):
	    return cgmAttr(self,attr).getMessage()
	return []
    
    def getMessageInstance(self,attr):
	"""
	This is for when you need to build a attr name in 
	"""
	buffer = self.getMessage(attr)
	if len(buffer) == 1:
	    return validateObjArg(self.getMessage(attr)) or False
	else:
	    return validateObjListArg(self.getMessage(attr)) or False	    
    
    def getComponent(self):
	"""
	Replacement mNode call for component mode
	"""
	if self.__componentMode__ and self.__component__:
	    buffer = '%s.%s'%(self.mNode,self.__component__)
	    if mc.objExists(buffer):return buffer
	    else:log.warning("Component no longer exists: %s"%self.__component__)
	    return self.mNode
	return self.mNode
    
    def isComponent(self):
	"""
	Returns if what is stored is a component
	"""
	if self.__componentMode__ and self.__component__:
	    buffer = '%s.%s'%(self.mNode,self.__component__)
	    if mc.objExists(buffer):return True
	    else:log.warning("Component no longer exists: %s"%self.__component__)
	    return False
	return False 
    
    def isAttrKeyed(self,attr):
	"""
	Returns if attribute is keyed
	"""	
	return attributes.isKeyed([self.mNode,attr])
    def isAttrConnected(self,attr):
	"""
	Returns if attribute is connected
	"""		
	return attributes.isConnected([self.mNode,attr])
    
    def getComponents(self,arg = False):
	"""
	@arg
	pass an arg through an mc.ls flatten call
	"""
	if arg:
	    try:return mc.ls(['%s.%s[*]'%(self.mNode,arg)],flatten=True)
	    except StandardError,error:
		log.error(error)
		return False
	else:
	    try:
		objType = self.getMayaType()
		if objType in ['mesh','polyVertex','polyEdge','polyFace','nurbsCurve',
			       'nurbsSurface','shape','surfaceCV']:
		    if objType == 'mesh':
			return mc.ls([self.mNode+'.vtx[*]'],flatten=True)
		    elif objType == 'polyVertex':
			return self.getComponent()
		    elif objType in ['polyEdge','polyFace']:
			mc.select(cl=True)
			mc.select(self.mNode)
			mel.eval("PolySelectConvert 3")
			return mc.ls(sl=True,fl=True)
		    elif objType in ['nurbsCurve','nurbsSurface']:
			l_components = []
			shapes = mc.listRelatives(self.mNode,shapes=True,fullPath=True)
			if shapes:
			    for shape in shapes:
				l_components.extend(mc.ls ([shape+'.ep[*]'],flatten=True))
			    return l_components
			else:
			    return mc.ls([self.mNode+'.ep[*]'],flatten=True)
		    elif objType == 'shape':
			return mc.ls ([self.mNode+'.ep[*]'],flatten=True)
		    elif objType == 'surfaceCV':
			return self.getComponent()
		    else:
			return self.getComponent()
		return False 
	    except StandardError,error:
		log.warning("getComponents: %s"%error)	
		return False
	    
    def connectChildNode(self, node, attr, connectBack = None, srcAttr=None, force=True):
        """
        Fast method of connecting a node to the mNode via a message attr link. This call
        generates a NONE-MULTI message on both sides of the connection and is designed 
        for simple parent child relationships.
        
        NOTE: this call by default manages the attr to only ONE CHILD to
        avoid this use cleanCurrent=False
        @param node: Maya node to connect to this mNode
        @param attr: Name for the message attribute  
        @param srcAttr: If given this becomes the attr on the child node which connects it 
                        to self.mNode. If NOT given this attr is set to self.mNodeID
        @param cleanCurrent: Disconnect and clean any currently connected nodes to this attr.
                        Note this is operating on the mNode side of the connection, removing
                        any currently connected nodes to this attr prior to making the new ones
        @param force: Maya's default connectAttr 'force' flag, if the srcAttr is already connected 
                        to another node force the connection to the new attr
        TODO: do we move the cleanCurrent to the end so that if the connect fails you're not left 
        with a half run setup?
	
	Usage Example:
        from cgm.core import cgm_Meta as cgmMeta
	cgmO = cgmObject()
	cgm02 = cgmObject()
	cgmO.connectChildNode(cgm02.mNode,'childNode','parentNode')
        """
        #make sure we have the attr on the mNode, if we already have a MULIT-message
        #should we throw a warning here???
        #self.addAttr(attr, attrType='messageSimple')
        try:
	    if issubclass(type(node), r9Meta.MetaClass):
		#if not srcAttr:
		    #srcAttr=node.message
		node=node.mNode    	    
            if not srcAttr:          
                srcAttr=self.message  #attr on the nodes source side for the child connection         
	    """
            if r9Meta.isMetaNode(node):
                if not issubclass(type(node), r9Meta.MetaClass): #allows you to pass in an metaClass
                    r9Meta.MetaClass(node).addAttr(srcAttr,attrType='messageSimple')
                else:
                    node.addAttr(srcAttr,attrType='messageSimple')
                    node=node.mNode 
            elif not mc.attributeQuery(srcAttr, exists=True, node=node):
                mc.addAttr(node,longName=srcAttr, at='message', m=False)  
		"""
            #if not self.isChildNode(node, attr, srcAttr): 
	    #mc.connectAttr('%s.%s' % (self.mNode,attr),'%s.%s' % (node,srcAttr), f=force)
	    attributes.storeObjectToMessage(node,self.mNode,attr)
	    if connectBack is not None:attributes.storeObjectToMessage(self.mNode,node,connectBack)		
        except StandardError,error:
            log.warning("connectChildNode: %s"%error)
	    raise StandardError,error
	    
    def connectParentNode(self, node, attr, connectBack = None, srcAttr=None):
        """
	Replacing Mark's connect Parent with our own which connects to .message connections.
	
        Fast method of connecting message links to the mNode as parents
        @param node: Maya nodes to connect to this mNode
        @param attr: Name for the message attribute on self to connec to the parent
	
        @param srcAttr: If given this becomes the attr on the node which connects it 
                        to the parent. If NOT given the connection attr is the parent.message
        """
        #log.info(connectBack)
        if issubclass(type(node), r9Meta.MetaClass):
            #if not srcAttr:
                #srcAttr=node.message
            node=node.mNode        
        try:
            #if connectBack and not mc.attributeQuery(connectBack, exists=True, node=node):
                #add to parent node
                #mc.addAttr(node,longName=connectBack, at='message', m=False)
	    attributes.storeObjectToMessage(node,self.mNode,attr)
	    if connectBack is not None:attributes.storeObjectToMessage(self.mNode,node,connectBack)
	    #attributes.storeObjectToMessage(node,self.mNode,attr)
	    
	    #if srcAttr:attributes.storeObjectToMessage(node,self.mNode,srcAttr)
	    return True
	    
        except StandardError,error:
                log.warning("connectParentNode: %s"%error)
		
    def connectChildrenNodes(self, nodes, attr, connectBack = None, force=True):
        """
	Replacement connector using .msg connections
        """
	if type(nodes) not in [list,tuple]:nodes=[nodes]
	nodesToDo = []
	for node in nodes:
	    if issubclass(type(node), r9Meta.MetaClass):
		nodesToDo.append(node.mNode) 
	    elif mc.objExists(node):
		nodesToDo.append(node) 
	    else:
		log.warning("connectChildrenNodes can't add: '%s'"%node)
		
	attributes.storeObjectsToMessage(nodesToDo,self.mNode,attr)
	for node in nodesToDo:
	    try:
		if connectBack is not None:attributes.storeObjectToMessage(self.mNode,node,connectBack)		
	    except StandardError,error:
		log.warning("connectChildrenNodes: %s"%error)
	    
    def addAttr(self, attr,value = None, attrType = None,enumName = None,initialValue = None,lock = None,keyable = None, hidden = None,*args,**kws):
        if attr not in self.UNMANAGED and not attr=='UNMANAGED':
	    #enum special handling
	    #valueCarry = None #Special handling for enum and value at the same time
	    #if enum is not None:
		#valueCarry = value
		#value = enum	    
	    if mc.objExists("%s.%s"%(self.mNode,attr)):#Quick create check for initial value
		initialCreate = False
		if self.isReferenced():
		    log.warning('This is a referenced node, cannot add attr: %s.%s'%(self.getShortName(),attr))
		    return False		
	    else:
		initialCreate = True
		if value is None and initialValue is not None:#If no value and initial value, use it
		    value = initialValue
		    	    
	    validatedAttrType = attributes.validateRequestedAttrType(attrType)
	    if attrType is not None and validatedAttrType in ['string','float','long'] and mc.objExists("%s.%s"%(self.mNode,attr)):
		currentType = mc.getAttr('%s.%s'%(self.mNode,attr),type=True)
		if currentType != validatedAttrType:
		    log.info("cgmNode.addAttr >> %s != %s : %s.%s. Converting."%(validatedAttrType,currentType,self.getShortName(),attr))
		    cgmAttr(self, attrName = attr, attrType=validatedAttrType)
		    	    
	    #If type is double3, handle with out own setup as Red's doesn't have it
	    #==============    
	    #if attributes.validateRequestedAttrType(attrType) == 'double3':
		#cgmAttr(self.mNode, attrName = attr, value = value, attrType = attrType, enum = enum, initialValue = initialValue, lock=lock,keyable=keyable,hidden = hidden)
		#object.__setattr__(self, attr, value)	

	    #Catch for no value flags
	    #DataTypeDefaults={'string': "",
	                      #'int': 0,
	                      #'bool': False,
	                      #'float': 0,
	                      #'float3': [0,0,0],
	                      #'double3':[0,0,0],
	                      #'enum': "off:on",
	                      #'message':''} 
	    
	    #if value is None and attrType is not None:
		#value = DataTypeDefaults.get(attrType)
	    if enumName is None and attrType is 'enum':
		enumName = "off:on"
	    log.debug("In mNode.addAttr attr is '%s'"%attr)
	    log.debug("In mNode.addAttr attrType is '%s'"%str(attrType))	    
	    log.debug("In mNode.addAttr value is '%s'"%str(value)) 		
	    #if valueCarry is not None:log.debug("In mNode.addAttr valueCarry is '%s'"%str(valueCarry)) 		
	    
	    #Pass to Red9
	    #MetaClass.addAttr(self,attr=attr,value=value,attrType = attrType,*args,**kws)
	    if attrType == 'enum':
		r9Meta.MetaClass.addAttr(self,attr,value=value,attrType = attrType,enumName = enumName, *args,**kws)
	    else:
		r9Meta.MetaClass.addAttr(self,attr,value=value,attrType = attrType, *args,**kws)	
		
	    if value is not None and r9Meta.MetaClass.__getattribute__(self,attr) != value: 
		log.debug("'%s.%s' Value (%s) was not properly set during creation to: %s"%(self.getShortName(),attr,r9Meta.MetaClass.__getattribute__(self,attr),value))
		if attributes.isConnected([self.mNode,attr]):
		    attributes.doBreakConnection(self.mNode,attr)
		self.__setattr__(attr,value,**kws)
		#attributes.doSetAttr(self.mNode,attr,value)
		#cgmAttr(self, attrName = attr, value=value)#Swictched back to cgmAttr to deal with connected attrs
		    
	    #if valueCarry is not None:
		#self.__setattr__(attr,valueCarry)
		
	    #if initialValue is not None and initialCreate:
		#log.info("In mNode.addAttr, setting initialValue of '%s'"%str(initialValue)) 
		#self.__setattr__(attr,initialValue)
	    
	    #if value and attrType is not 'enum':#Want to be able to really set attr on addAttr call if attr exists
		#self.__setattr__(attr,value)
	    
	    #Easy carry for flag handling - until implemented
	    #==============  
	    if keyable is not None or hidden is not None:
		cgmAttr(self, attrName = attr, keyable=keyable,hidden = hidden)
	    if lock is not None:
		mc.setAttr(('%s.%s'%(self.mNode,attr)),lock=lock)	
		
            return True
        return False
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #Reference Prefix
    #==============    
    def getReferencePrefix(self):
	return search.returnReferencePrefix(self.mNode)
    
    referencePrefix = property(getReferencePrefix)
    
    #=========================================================================      
    # Get Info
    #========================================================================= 
    def returnNextAvailableAttrCnt(self,attr = None):
	if attr in [None,False,True]:
	    log.warning("cgmNode.returnNextAvailableAttrCnt>>> bad attr arg: '%s'"%attr)
	    return False
        """ Get's the next available item number """        
        userAttrs = self.getUserAttrsAsDict()
        countList = []
        for key in userAttrs.keys():
            if attr in key:
                splitBuffer = key.split(attr)
                countList.append(int(splitBuffer[-1]))
	for i in range(500):
	    if i not in countList:
		return i
        return False
    
    def update(self):
        """ Update the instance with current maya info. For example, if another function outside the class has changed it. """ 
        assert mc.objExists(self.mNode) is True, "'%s' doesn't exist" %obj
	if self.hasAttr('mNodeID') and not self.isReferenced():#experiment
	    log.debug(self.mNodeID)
	    attributes.doSetAttr(self.mNode,'mNodeID',self.getShortName())
	self.__dict__['__name__'] = self.getShortName()
	
    def getCGMNameTags(self):
        """
        Get the cgm name tags of an object.
        """
        self.cgm = {}
        for tag in l_cgmNameTags:
            self.cgm[tag] = search.findRawTagInfo(self.mNode,tag)
        return self.cgm    
        
    def getAttrs(self,**kws):
        return mc.listAttr(self.mNode,**kws) or []
	
    def getKeyableAttrs(self):
	return mc.listAttr(self.mNode, keyable = True) or []
	
    def getUserAttrs(self):
	return mc.listAttr(self.mNode, userDefined = True) or []
	
    def getUserAttrsAsDict(self):
	return attributes.returnUserAttrsToDict(self.mNode) or {}
    
    def getNameDict(self):
	return nameTools.returnObjectGeneratedNameDict(self.mNode) or {}  
    
    def getNameAlias(self):
	if self.hasAttr('cgmAlias'):
	    return self.cgmAlias
	buffer =  nameTools.returnRawGeneratedName(self.mNode, ignore = ['cgmType'])
	if buffer:return buffer
	else:return self.getBaseName()
	
    def getTransform(self):
	"""Find the transform of the object"""
	buffer = mc.ls(self.mNode, type = 'transform') or False
	if buffer:
	    return buffer[0]
	else:
	    buffer = mc.listRelatives(self.mNode,parent=True,type='transform') or False
	if buffer:
	    return buffer[0]
	return False
	
    def getMayaType(self):
        """ get the type of the object """
        return search.returnObjectType(self.getComponent())
    
    def getMayaAttr(self,attr,**kws):
        """ get the type of the object """
        return attributes.doGetAttr(self.mNode,attr,**kws)  
    
    def getAttr(self,attr):
        """ Get the attribute. As an add on to Marks. I don't want errors if it doesn't have the attr, I just want None. """
        try: return self.__getattribute__(attr)
	except: return None    
    
    def getShortName(self):
        buffer = mc.ls(self.mNode,shortNames=True)        
        return buffer[0]
    
    def getBaseName(self):
        buffer = self.mNode     
        return buffer.split('|')[-1].split(':')[-1] 
    
    def getLongName(self):
        buffer = mc.ls(self.mNode,l=True)        
        return buffer[0]  
    
    def isTransform(self):
        buffer = mc.ls(self.mNode,type = 'transform',long = True)
	if buffer and buffer[0]==self.getLongName():
	    return True
        return False
    
    def compareAttrs(self,target,**kws):
        """ compare the attributes of one object to another """
	if not mc.objExists(target):
	    raise StandardError,"Target doesn't exist! | %s"%target
	l_targetAttrs = mc.listAttr(target,**kws)
	for a in mc.listAttr(self.mNode,**kws):
	    try:
		#log.info("Checking %s"%a)
		selfBuffer = attributes.doGetAttr(self.mNode,a)
		targetBuffer = attributes.doGetAttr(target,a)
		if a in l_targetAttrs and selfBuffer != targetBuffer:
		    log.debug("%s.%s : %s != %s.%s : %s"%(self.getShortName(),a,selfBuffer,target,a,targetBuffer))
	    except StandardError,error:
		log.debug(error)	
		log.warning("'%s.%s'couldn't query"%(self.mNode,a))
	return True
	    
    #@r9General.Timer
    def doName(self,sceneUnique=False,nameChildren=False,fastIterate = True,**kws):
        """
        Function for naming a maya instanced object using the cgm.NameFactory class.

        Keyword arguments:
        sceneUnique(bool) -- Whether to run a full scene dictionary check or the faster just objExists check (default False)

        """
	#if not self.getTransform() and self.__justCreatedState__:
	    #log.error("Naming just created nodes, causes recursive issues. Name after creation")
	    #return False
	if sceneUnique:
	    log.error("Remove this cgmNode.doName sceneUnique call")
	if self.isReferenced():
	    log.error("'%s' is referenced. Cannot change name"%self.mNode)
	    return False	
	
	#Name it
	NameFactory(self).doName(nameChildren = nameChildren,fastIterate=fastIterate,**kws)
	log.debug("Named: '%s'"%self.getShortName())
		
	
    def doNameOLD(self,sceneUnique=False,nameChildren=False,**kws):
        """
        Function for naming a maya instanced object using the cgm.NameFactory class.

        Keyword arguments:
        sceneUnique(bool) -- Whether to run a full scene dictionary check or the faster just objExists check (default False)

        """  
	def doNameChildren(self):
	    if not len(mc.ls(self.mNode,type = 'transform',long = True)) == 0:
		childrenObjects = search.returnAllChildrenObjects(self.mNode,True) or []
		i_children = []
		for c in childrenObjects:
		    i_c =  r9Meta.MetaClass(c)
		    mc.rename(i_c.mNode,rename('xxx'))
		    i_children.append(i_c )
		for i_c in i_children:
		    name = Old_Name.returnUniqueGeneratedName(i_c.mNode,sceneUnique =sceneUnique,**kws)
		    mc.rename(i_c.mNode,name)  		    
	    
	log.debug('Name dict: %s"'%self.getNameDict())
        if self.isReferenced():
            log.error("'%s' is referenced. Cannot change name"%self.mNode)
            return False

	name = Old_Name.returnUniqueGeneratedName(self.mNode,sceneUnique = sceneUnique,**kws)
	currentShortName = self.getShortName()
	
	if currentShortName == name:
	    log.debug("'%s' is already named correctly."%currentShortName)
	    if nameChildren:
		doNameChildren(self)
	    return currentShortName
	else:
	    mc.rename(self.mNode,name)
	    shapes = mc.listRelatives(self.mNode,shapes=True,fullPath=True)
	    if shapes:
		for shape in shapes:
		    if not mc.referenceQuery(shape, isNodeReferenced=True):
			i_shape = r9Meta.MetaClass(shape)
			name = Old_Name.returnUniqueGeneratedName(i_shape.mNode,sceneUnique =sceneUnique,**kws)
			mc.rename(i_shape.mNode,name)  
	    if nameChildren:
		doNameChildren(self)
		
	    return self.getShortName()
	
    def getChildrenNodes(self, walk=True, mAttrs=None):
	"""Overload to push a conflicting command to a name we want as getChildren is used for cgmObjects to get dag children"""
	return r9Meta.MetaClass.getChildren(self, walk, mAttrs)
    
    #@r9General.Timer
    def getSiblings(self):
	"""Function to get siblings of an object"""
	l_siblings = []
	if not self.getTransform():
	    #See if there are more maya nodes of the same type
	    objType = mc.objectType(self.mNode)
	    l_buffer = mc.ls(type = objType)
	    log.debug("typeCheck: '%s'"%objType)
	    log.debug("l_buffer: %s"%l_buffer)
	    if l_buffer:
		for o in l_buffer:
		    if str(o) != self.getLongName():
			l_siblings.append(o)
			log.debug("Sibling found: '%s'"%o)
		return l_siblings
	elif self.getMayaType() == 'shape':
	    for s in mc.listRelatives(self.parent,shapes = True,fullPath = True):
		if str(s) != self.getLongName():#str() for stupid unicode return
		    l_siblings.append(s)
		    log.debug("Shape Sibling found: '%s'"%s)
	    return l_siblings
	elif self.parent:
	    #i_p = cgmObject(self.parent)#Initialize the parent
	    for c in search.returnChildrenObjects(self.parent,True):
		if c != self.getLongName():
		    l_siblings.append(c)
		    log.debug("Sibling found: '%s'"%c)
	else:#We have a root transform
	    l_rootTransforms = search.returnRootTransforms() or []
	    typeBuffer = self.getMayaType()
	    for c in l_rootTransforms:
		if c != self.getShortName() and search.returnObjectType(c) == typeBuffer:
		    l_siblings.append(c)
	log.debug(l_siblings)
	return l_siblings   
    
    #=========================================================================                   
    # Attribute Functions
    #=========================================================================                   
    def doStore(self,attr,info,overideMessageCheck = False,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        attributes.storeInfo(self.mNode,attr,info,overideMessageCheck = overideMessageCheck,*a,**kw)
	object.__setattr__(self, attr, info)
	#self.update()

    def doRemove(self,attr):
        """ Removes an attr from the maya object instanced. """
        if self.isReferenced():
            return log.warning("'%s' is referenced. Cannot delete attrs"%self.mNode)    	
        try:
            attributes.doDeleteAttr(self.mNode,attr)
	except StandardError,error:
	    log.error(error)	
            log.warning("'%s.%s' not found"%(self.mNode,attr))	    
	    return False
	    
    def doChangeNameTag(self,tag,value = False,sceneUnique=False,nameChildren=False,**kw):
	"""
	For changing a tag and renaming in one go
	@ Tag(string)
	Must be a cgm naming tag
	@ Value(string)
	what to change it to
	@ sceneUnique(bool)
	@ nameChildren(bool)
	"""
	try:
	    if self.isReferenced():
		return log.warning("'%s' is referenced. Cannot change name architecture"%self.mNode)   
	    
	    if tag not in l_cgmNameTags:
		log.debug("'%s' is not a valid cgm name tag."%(tag))         
		return False
	    
	    if value in [None,False,'None','none']:
		log.debug("Removing '%s.%s'"%(self.getShortName(),tag))            
		self.doRemove(tag)
		self.doName(sceneUnique,nameChildren)            
		return True
		
	    elif tag in self.__dict__.keys() and self.__dict__[tag] == value:
		log.debug("'%s.%s' already has base name of '%s'."%(self.getShortName(),tag,value))
		return False
	    else:
		self.doStore(tag,value,True,**kw)
		self.doName(sceneUnique,nameChildren)            
		return True
	except StandardError,error:
	    log.error(error)	
	    return False
	
    def doCopyNameTagsFromObject(self,target,ignore=[False]):
        """
        Get name tags from a target object (connected)
        
        Keywords
        ignore(list) - tags to ignore
        
        Returns
        success(bool)
        """
	if type(ignore) not in [list,tuple]:ignore = [ignore]
	try:
	    log.debug(">>> cgmNode.doCopyNametagsFromObject")
	    assert mc.objExists(target),"Target doesn't exist"
	    targetCGM = nameTools.returnObjectGeneratedNameDict(target,ignore = ignore)
	    didSomething = False
	    
	    for tag in targetCGM.keys():
		log.debug("..."+tag)
		if tag not in ignore and targetCGM[tag] is not None or False:
		    attributes.doCopyAttr(target,tag,
			                  self.mNode,connectTargetToSource=False)
		    didSomething = True
	    #self.update()
	    return didSomething
	except StandardError,error:
	    log.error(error)	
	    return False
	
    def returnPositionOutPlug(self):
	"""
	Finds out plug of a node for connection to a distance node for example
	"""
	try:
	    l_elibiblePlugs = ['worldPosition','position'] 
	    d_plugTypes= {'worldPosition':'worldPosition[0]','position':'position'}
	    for attr in l_elibiblePlugs:
		if self.hasAttr(attr):
		    return "%s.%s"%(self.mNode,d_plugTypes.get(attr))
	    return False
	except StandardError,error:
	    log.error("returnPositionOutPlug>> Failed. error: %s"%error)	    
	    raise StandardError,error 
	
    def getPosition(self,worldSpace = True):
	try:
	    if self.isComponent():
		log.debug("Component position mode")
		objType = self.getMayaType()	    
		if objType in ['polyVertex','polyUV','surfaceCV','curveCV','editPoint','nurbsUV','curvePoint']:
		    if worldSpace:return mc.pointPosition(self.getComponent(),world = True)
		    return mc.pointPosition(self.getComponent(),local = True)
		elif objType in ['polyFace','polyEdge']:
			mc.select(cl=True)
			mc.select(self.getComponent())
			mel.eval("PolySelectConvert 3")
			verts = mc.ls(sl=True,fl=True)
			posList = []
			for vert in verts:
			    if worldSpace:posList.append( mc.pointPosition(vert,world = True) )
			    else:posList.append( mc.pointPosition(vert,local = True) )			    
			pos = distance.returnAveragePointPosition(posList)
			mc.select(cl=True)
			return pos
		else:
		    raise NotImplementedError,"Don't know how to position '%s's componentType: %s"%(self.getShortName,objType)
		
	    else:
		#if kws and 'ws' in kws.keys():ws = kws.pop('ws')
		log.debug('Standard self.getPosition()')
		if worldSpace:return mc.xform(self.mNode, q=True, ws=True, rp=True)    
		return mc.xform(self.mNode, q=True, os=True, t=True) 
	except StandardError,error:
	    log.error("cgmNode.getPosition: %s"%error)	
	    return False
	
    def doLoc(self,forceBBCenter = False,nameLink = False):
        """
        Create a locator from an object

        Keyword arguments:
        forceBBCenter(bool) -- whether to force a bounding box center (default False)
	nameLink(bool) -- whether to copy name tags or link the object to cgmName
        """
	buffer = False
	if self.isComponent():
	    buffer =  locators.locMeObject(self.getComponent(),forceBBCenter = forceBBCenter)
	elif self.isTransform():
	    buffer = locators.locMeObject(self.mNode,forceBBCenter = forceBBCenter)
	if not buffer:
	    return False
	i_loc = cgmObject(buffer,setClass=True)
	if nameLink:
	    i_loc.connectChildNode(self,'cgmName')
	else:
	    i_loc.doCopyNameTagsFromObject(self.mNode,ignore=['cgmType'])
	i_loc.doName()
	return i_loc
    
    def doDuplicate(self,parentOnly = True, incomingConnections = True):
        """
        Return a duplicated object instance

        Keyword arguments:
        incomingConnections(bool) -- whether to do incoming connections (default True)
        """
	if self.isComponent():
	    log.warning("doDuplicate fail. Cannot duplicate components")
	    raise StandardError,"doDuplicate fail. Cannot duplicate component: '%s'"%self.getShortName()
	
	buffer = mc.duplicate(self.mNode,po=parentOnly,ic=incomingConnections)[0]
	log.debug("doDuplicate>> buffer: %s"%buffer)
	i_obj = r9Meta.MetaClass(buffer)
	mc.rename(i_obj.mNode, self.getShortName()+'_DUPLICATE')
	log.debug("doDuplicate>> i_obj: %s"%i_obj)	
	return i_obj
	
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmObject - sublass to cgmNode
#=========================================================================        
class cgmObject(cgmNode):                  
    def __init__(self,node = None, name = 'null',setClass = False,*args,**kws):
        """ 
        Utilizing Red 9's MetaClass. Intialized a object in cgm's system. If no object is passed it 
        creates an empty transform

        Keyword arguments:
        obj(string)     
        autoCreate(bool) - whether to create a transforum if need be
        """
        ### input check
	#if node == None:
	    #catch = cgmMeta(name = name, nodeType = 'transform')
	    #node = catch.mNode

        super(cgmObject, self).__init__(node = node, name = name,nodeType = 'transform')
        
        if not self.isTransform():
            log.error("'%s' has no transform"%self.mNode)
            raise StandardError, "The class was designed to work with objects with transforms"
	if setClass:
	    self.addAttr('mClass','cgmObject',lock=True)
	    
    def __bindData__(self):pass
        #self.addAttr('test',2)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #parent
    #==============    
    #def getParent(self):
        #return search.returnParentObject(self.mNode) or False
		
    def doParent(self,target = False):
        """
        Function for parenting a maya instanced object while maintaining a correct object instance.

        Keyword arguments:
        parent(string) -- Target parent
        """
        if target == self.getParent():
            return True
	log.debug("Parenting '%s' to '%s'"%(self.mNode,target))

        if target: #if we have a target parent
            try:
                #If we have an Object Factory instance, link it
                self.parent = target.mNode
                log.debug("Parent is an instance")   		
            except:
                #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
                assert mc.objExists(target) is True, "'%s' - parent object doesn't exist" %target    
            
            log.debug("Parent is '%s'"%target)
            try: 		
                mc.parent(self.mNode,target)
            except:
                log.debug("'%s' already has target as parent"%self.mNode)
                return False
	
        else:#If not, do so to world
            rigging.doParentToWorld(self.mNode)
            log.debug("'%s' parented to world"%self.mNode) 
	
		
    parent = property(cgmNode.getParent, doParent)
    #=========================================================================      
    # Get Info
    #========================================================================= 	
    def getTransformAttrs(self):
	self.transformAttrs = []
	for attr in 'translate','translateX','translateY','translateZ','rotate','rotateX','rotateY','rotateZ','scaleX','scale','scaleY','scaleZ','visibility','rotateOrder':
	    if mc.objExists(self.mNode+'.'+attr):
		self.transformAttrs.append(attr)
	return self.transformAttrs
    
    def getFamilyDict(self):
        """ Get the parent, child and shapes of the object."""
        return {'parent':self.parent,'children':self.children,'shapes':self.shapes} or {}
    
    def getAllParents(self,fullPath = False):
        return search.returnAllParents(self.mNode,not fullPath) or []
    
    def getChildren(self,fullPath=False):
        return search.returnChildrenObjects(self.mNode,fullPath) or []
    
    def getAllChildren(self,fullPath = False):
        return search.returnAllChildrenObjects(self.mNode,fullPath) or []    
    
    def getShapes(self):
        return mc.listRelatives(self.mNode,shapes=True) or []
    
    def isChildOf(self,obj):
	try:
	    i_obj = validateObjArg(obj,noneValid=False)
	    for o in self.getAllParents(True):
		if i_obj.mNode == r9Meta.MetaClass(o).mNode:
		    return True
	    return False
	except StandardError,error:
	    log.error("isChildOf>> error: %s"%error)	    
	    log.error("isChildOf>> Failed. self: '%s' | obj: '%s'"%(self.mNode,obj))
	    raise StandardError,error 
    
    def isParentOf(self,obj):
	try:
	    i_obj = validateObjArg(obj,noneValid=False)
	    for o in self.getAllChildren(True):
		if i_obj.mNode == r9Meta.MetaClass(o).mNode:
		    return True
	    return False
	except StandardError,error:
	    log.error("isParentOf>> error: %s"%error)
	    log.error("isParentOf>> Failed. self: '%s' | obj: '%s'"%(self.mNode,obj))
	    raise StandardError,error 
	
    def returnPositionOutPlug(self,autoLoc=True):
	try:
	    if self.getMayaType() == 'locator':
		return cgmNode(mc.listRelatives(self.mNode,shapes=True)[0]).returnPositionOutPlug()	    
	    else:
		buffer = cgmNode.returnPositionOutPlug(self)
		if not buffer and autoLoc:
		    #See if we have one
		    if self.getMessage('positionLoc'):
			i_loc = cgmObject(self.getMessage('positionLoc')[0])		    
		    else:
			i_loc = self.doLoc()
			i_loc.parent = self.mNode
			self.connectChildNode(i_loc,'positionLoc','owner')
		    return cgmNode(mc.listRelatives(i_loc.mNode,shapes=True)[0]).returnPositionOutPlug()	    		    
		else:return buffer
	except StandardError,error:
	    log.error("returnPositionOutPlug(cgmObject overload)>> error: %s"%error)
	    raise StandardError,error 
	
    def getListPathTo(self,obj):
	try:
	    i_obj = validateObjArg(obj,cgmObject,noneValid=False)
	    log.debug("getListPathTo>>> target object: %s" %i_obj)
	    l_path = []
	    if self.isParentOf(i_obj):
		l_parents = i_obj.getAllParents(True)
		self_index = l_parents.index(self.mNode)
		l_parents = l_parents[:self_index+1]
		l_parents.reverse()
		log.info(l_parents)
		#l_path.append(self.getShortName())
		for o in l_parents:
		    i_o = cgmObject(o)
		    l_path.append(i_o.getShortName())		    
		    if i_obj.mNode == i_o.mNode:
			break	
		l_path.append(i_obj.getShortName())
			
	    elif self.isChildOf(obj):
		l_parents = self.getAllParents(True)
		#l_parents.reverse()
		l_path.append(self.getShortName())
		for o in l_parents:
		    i_o = cgmObject(o)
		    l_path.append(i_o.getShortName())		    
		    if i_obj.mNode == i_o.mNode:
			break	
	    else:
		return False
	    return l_path
	except StandardError,error:
	    log.error("getListPathTo>> error: %s"%error)	    
	    log.error("getListPathTo>> Failed. self: '%s' | obj: '%s'"%(self.mNode,obj))
	    raise StandardError,error 
    
    def getMatchObject(self):
        """ Get match object of the object. """
        matchObject = search.returnTagInfo(self.mNode,'cgmMatchObject')
        if mc.objExists(matchObject):
            log.debug("Match object found")
            return matchObject
        return False

    #=========================================================================  
    # Rigging Functions
    #=========================================================================  
    def doCopyRotateOrder(self,targetObject):
        """ 
        Copy the rotate order from a target object to the current instanced maya object.
        """
        try:
            #If we have an Object Factory instance, link it
            targetObject.mNode
            targetObject = targetObject.mNode
            log.debug("Target is an instance")            
        except:	
            log.debug("Target is not an instance")
            assert mc.objExists(targetObject) is True, "'%s' - target object doesn't exist" %targetObject    
        assert mc.ls(targetObject,type = 'transform'),"'%s' has no transform"%targetObject
        buffer = mc.getAttr(targetObject + '.rotateOrder')
        attributes.doSetAttr(self.mNode, 'rotateOrder', buffer) 

    def doCopyPivot(self,sourceObject):
        """ Copy the pivot from a source object to the current instanced maya object. """
        try:
            #If we have an Object Factory instance, link it
            sourceObject.mNode
            sourceObject = sourceObject.mNode
            log.debug("Source is an instance")                        
        except:
            #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
            assert mc.objExists(sourceObject) is True, "'%s' - source object doesn't exist" %sourceObject

        assert mc.ls(sourceObject,type = 'transform'),"'%s' has no transform"%sourceObject
        rigging.copyPivot(self.mNode,sourceObject)


    def doCopyTransform(self,sourceObject):
        """ Copy the pivot from a source object to the current instanced maya object. """
        try:
            #If we have an Object Factory instance, link it
            sourceObject.mNode
            sourceObject = sourceObject.mNode
            log.debug("Source is an instance")                        
        except:
            #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
            assert mc.objExists(sourceObject) is True, "'%s' - source object doesn't exist" %sourceObject

        assert mc.ls(sourceObject,type = 'transform'),"'%s' has no transform"%sourceObject
	objRot = mc.xform (sourceObject, q=True, ws=True, ro=True)
	self.doCopyPivot(sourceObject)
	self.rotateAxis = objRot
	
    def doGroup(self,maintain=False):
        """
        Grouping function for a maya instanced object.

        Keyword arguments:
        maintain(bool) -- whether to parent the maya object in place or not (default False)

        """
        return rigging.groupMeObject(self.mNode,True,maintain)   
    
    def doZeroGroup(self,connect=True):
        """
        Zero Grouping function for a maya instanced object.

        Keyword arguments:
        maintain(bool) -- whether to parent the maya object in place or not (default False)
        """
	i_group = validateObjArg(self.doGroup(True), cgmObject)
	i_group.addAttr('cgmTypeModifier','zero')
	if connect:self.connectChildNode(i_group,'zeroGroup','cgmName')
	i_group.doName()	
	return i_group
    
    def doDuplicateTransform(self,copyAttrs = False):
        """
        Duplicates an objects tranform

        Keyword arguments:
        copyAttrs(bool) -- whether to copy attrs to the new transform (default False)

        """
	try:
	    i_obj = cgmObject( rigging.groupMeObject(self.mNode,parent = False),setClass=True  ) 
	    if copyAttrs:
		for attr in self.getUserAttrs():
		    cgmAttr(self,attr).doCopyTo(i_obj.mNode,attr,connectSourceToTarget = False)	    
		self.addAttr('cgmType','null',lock=True)
		i_obj.doName()
	    elif i_obj.hasAttr('cgmName'):
		i_obj.doRemove('cgmName')
		mc.rename(i_obj.mNode, self.getShortName()+'_Transform')
	    return i_obj
	except StandardError,error:
	    log.error("doDuplicateTransform fail! | %s"%error) 
	    raise StandardError
	
    def duplicateTransform(self,copyAttrs = False):
	DeprecationWarning,"duplicateTransform is now doDuplicateTransform"
	return self.doDuplicateTransform(copyAttrs)
    
    def doAddChild(self,child = False):
        """
        Function for adding a child

        Keyword arguments:
        child(string) -- Target child
        """
	if not mc.objExists(child):
	    log.warning("Specified child '%s' doesn't exist"%child)
	    return False
	
        if child in self.getChildren():
            return True
        
        if child: #if we have a target child
            log.debug("Child is '%s'"%child)
            try:
                mc.parent(child,self.mNode)
            except:
                log.debug("'%s' already has target as child"%self.mNode)
                return False
             
    def setDrawingOverrideSettings(self, attrs = None, pushToShapes = False):
        """
        Function for changing drawing override settings on on object

        Keyword arguments:
        attrs -- default will set all override attributes to default settings
                 (dict) - pass a dict in and it will attempt to set the key to it's indexed value ('attr':1}
                 (list) - if a name is provided and that attr is an override attr, it'll reset only that one
        """
        # First make sure the drawing override attributes exist on our instanced object
        for a in drawingOverrideAttrsDict:
            assert mc.objExists('%s.%s'%(self.mNode,a)),"'%s.%s' doesn't exist"%(self.mNode,a)

        #Get what to act on
        targets = [self.mNode]
        if pushToShapes:
            shapes = self.getShapes()
            if shapes:
                targets.extend(shapes)
        
        for t in targets:
            #Get to business
            if attrs is None or False:
                for a in drawingOverrideAttrsDict:
                    attributes.doSetAttr(t,a,drawingOverrideAttrsDict[a])
    
            if type(attrs) is dict:
                for a in attrs.keys():
		    try:
			attributes.doSetAttr(t,a,attrs[a])
		    except:
			raise AttributeError, "There was a problem setting '%s.%s' to %s"%(self.mNode,a,drawingOverrideAttrsDict[a])

                        
            if type(attrs) is list:
                for a in attrs:
                    if a in drawingOverrideAttrsDict:
                        try:
                            attributes.doSetAttr(self.mNode,a,drawingOverrideAttrsDict[a])
                        except:
                            raise AttributeError, "There was a problem setting '%s.%s' to %s"%(self.mNode,a,drawingOverrideAttrsDict[a])
                    else:
                        log.warning("'%s.%s' doesn't exist"%(t,a))      
    #>>> Constraints
    #==============================================================
    def getConstraintsTo(self):	
	return constraints.returnObjectConstraints(self.mNode)

    def getConstraintsFrom(self):
	return constraints.returnObjectDrivenConstraints(self.mNode)
    
    def isConstrainedBy(self,obj):
	l_constraints = self.getConstraintsTo()
	if not l_constraints:
	    return False
	else:
	    try:
		#If we have an Object Factory instance, link it
		obj.mNode
		i_obj = obj
	    except:
		#If it fails, check that the object name exists and if so, initialize a new Object Factory instance
		assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
		i_obj = cgmNode(obj)
	    log.debug("obj: %s"%i_obj.getShortName())
	    log.debug("l_constraints: %s"%l_constraints)
	    #for i_c in [r9Meta.MetaClass(c) for c in l_constraints]:
	    returnList = []
	    for c in l_constraints:
		targets = constraints.returnConstraintTargets(c)
		log.debug("%s : %s"%(cgmNode(c).getShortName(),targets))
		if i_obj.getShortName() in targets:
		    returnList.append(c)
	    if returnList:return returnList	
	return False
    
	
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmObjectSet - subclass to cgmNode
#=========================================================================  
class cgmControl(cgmObject): 
    def __init__(self,node = None, name = 'null',setClass = False,*args,**kws):
	""" 
	Class for control specific functions
    
	Keyword arguments:
	obj(string)     
	autoCreate(bool) - whether to create a transforum if need be
	"""
	try: super(cgmControl, self).__init__(node = node, name = name,nodeType = 'transform')
	except StandardError,error:
	    raise StandardError, "cgmControl.__init__ fail! | %s"%error
	if setClass:
	    self.addAttr('mClass','cgmControl',lock=True)
	    
    #>>> Module stuff
    #========================================================================
    def _hasModule(self):
	try:
	    if self.getAttr('module'):
		return True
	    return False
	except StandardError,error:
	    log.error("%s._hasModule>> _hasModule fail | %s"%(self.getShortName(),error))	    
	    return False
	
    def _hasSwitch(self):
	try:
	    if self.module.rigNull.dynSwitch:
		return True
	    return False
	except StandardError,error:
	    log.error("%s._hasSwitch>> _hasSwitch fail | %s"%(self.getShortName(),error))
	    return False	
    
    #>>> Aim stuff
    #========================================================================
    def _isAimable(self):
	try:
	    if self.hasAttr('axisAim') and self.hasAttr('axisUp'):
		return self._verifyAimable()
	    return False
	except StandardError,error:
	    log.error("cgmControl._verifyAimable>> _verifyAimable fail | %s"%error)
	    return False
	
	if self.axisAim == self.axisUp or self.axisAim == self.axisOut or self.axisUp == self.axisOut:
	    log.error("cgmControl._verifyAimable>> Axis settings cannot be the same")	    
	    return False
	return True

    def _verifyAimable(self):
	try:
	    self.addAttr('axisAim', attrType='enum',enumName = 'x+:y+:z+:x-:y-:z-',initialValue=2, keyable = True, lock = False, hidden = True) 
	    self.addAttr('axisUp', attrType='enum',enumName = 'x+:y+:z+:x-:y-:z-',initialValue=1, keyable = True, lock = False, hidden = True) 
	    self.addAttr('axisOut', attrType='enum', enumName = 'x+:y+:z+:x-:y-:z-',initialValue=0, keyable = True, lock = False, hidden = True) 
	    return True
	except StandardError,error:
	    raise StandardError, "cgmControl._verifyAimable fail! | %s"%error	
	
    def doAim(self,target = None):
	try:
	    if not self._isAimable():
		log.warning("Not an aimable control: '%s'"%self.getShortName())
		return False
	    i_target = validateObjArg(target,cgmObject,noneValid=True)
	    if not i_target:
		log.warning("Invalid aim target : '%s'"%target)
		return False	    
	    
	    l_enums = mc.attributeQuery('axisAim', node=self.mNode, listEnum=True)[0].split(':')
	    
	    aimVector = dictionary.stringToVectorDict.get("%s"%l_enums[self.axisAim])
	    upVector = dictionary.stringToVectorDict.get("%s"%l_enums[self.axisUp])
	    outVector = dictionary.stringToVectorDict.get("%s"%l_enums[self.axisOut])
	    
	    log.debug("aimVector: %s"%aimVector)
	    log.debug("upVector: %s"%upVector)
	    log.debug("outVector: %s"%outVector)
	    aimConstraintBuffer = mc.aimConstraint(i_target.mNode,self.mNode,maintainOffset = False, weight = 1, aimVector = aimVector, upVector = upVector, worldUpType = 'scene' )
	    mc.delete(aimConstraintBuffer)
	except StandardError,error:
	    raise StandardError, "%s.doAim fail! | %s"%(self.getShortName(),error)
	    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmObjectSet - subclass to cgmNode
#=========================================================================  
setTypes = {'animation':'animSet',
            'layout':'layoutSet',
            'modeling':'modelingSet',
            'td':'tdSet',
            'fx':'fxSet',
            'lighting':'lightingSet'}

class cgmObjectSet(cgmNode):
    """ 
    Maya Object Set Class handler
    """ 	
    def __init__(self,setName = None,setType = False,qssState = None,value = None,**kws):
        """ 
        Intializes an set factory class handler
        
        Keyword arguments:
        setName(string) -- name for the set
        
        """
        ### input check  
	if setName is not None:
	    if mc.objExists(setName):
		assert search.returnObjectType(setName) == 'objectSet',"Not an object set"    
		super(cgmObjectSet, self).__init__(node = setName)  
	    else:
		super(cgmObjectSet, self).__init__(node = None,name = setName,nodeType = 'objectSet')
	else:
	    super(cgmObjectSet, self).__init__(node = setName,nodeType = 'objectSet')
	    
        log.debug("In cgmObjectSet.__init__ setName is '%s'"%setName)
        log.debug("In cgmObjectSet.__init__ setType is '%s'"%setType) 
        log.debug("In cgmObjectSet.__init__ qssState is '%s'"%qssState) 
	
	self.UNMANAGED.extend(['objectSetType','qssState','mayaSetState'])
	self.mayaSetState = False
	
	#Maya Set?
	#==============
	for check in ['defaultCreaseDataSet',
                          'defaultObjectSet',
                          'defaultLightSet',
                          'initialParticleSE',
                          'initialShadingGroup',
                          'tweakSet']:
		if check in self.mNode and not self.qssState:
			self.mayaSetState = True
			
	#Set on call options
	#==============
	if setType:
	    self.doSetType(setType)
	    
	if qssState is not None:
	    self.makeQss(qssState)
	    
	#Attempt to set a value on call
	if value is not None:           
	    self.value = value	
	    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #Qss
    #==============    
    def isQss(self):
	"""
	Returns if an object set is a qss set or not
	"""
	if mc.sets(self.mNode,q=True,text=True)== 'gCharacterSet':
	    return True
	else:
	    return False
		
    def makeQss(self,arg):
	"""
	Makes an object set a qss set (if possible)
	"""
	assert not self.mayaSetState,"'%s' is a maya set and may not be changed to a qss"%(self.mNode)  
	
        if arg:
            if mc.sets(self.mNode,q=True,text=True)!= 'gCharacterSet':
                mc.sets(self.mNode, edit = True, text = 'gCharacterSet')
                log.warning("'%s' is now a qss"%(self.mNode))
                self.qssState = True
		return True
                
        else:
            if mc.sets(self.mNode,q=True,text=True)== 'gCharacterSet':
                mc.sets(self.mNode, edit = True, text = '')            
                log.warning("'%s' is no longer a qss"%(self.mNode)) 
                self.qssState = False	
		return False
		
    qssState = property(isQss, makeQss)
    
    
    #ObjectSet Type
    #==============  
    def getSetType(self):
	"""
	Returns the objectSet type as defined by CG Monks
	"""
	buffer = search.returnTagInfo(self.mNode,'cgmType')
	if buffer:
	    for k in setTypes.keys():
		if buffer == setTypes[k]:
		    log.debug('Found match')
		    return k
	    else:
		return buffer
	else:return False
    
    def doSetType(self,setType = None):
        """
	Set a an objectSet's type
	"""
	assert type(setType) is str, "Set type must be a string command. '%s'"%setType
	assert not self.isReferenced(), "Cannot change the type of a referenced set"
	assert not self.mayaSetState, "Cannot change type of a maya default set"

        if setType is not None:
            doSetType = setType
            if setType in setTypes.keys():
                doSetType = setTypes.get(setType)
	    if search.returnTagInfo(self.mNode,'cgmType') != doSetType:
		if attributes.storeInfo(self.mNode,'cgmType',doSetType,True):
		    self.doName()
		    log.warning("'%s' renamed!"%(self.mNode))  
		    return self.mNode
		else:               
		    log.warning("'%s' failed to store info"%(self.mNode))  
		    return False
        else:
            attributes.doDeleteAttr(self.mNode,'cgmType')
            self.doName()
            log.warning("'%s' renamed!"%(self.mNode))  
            return self.mNode

    objectSetType = property(getSetType, doSetType)
    
    #Value
    #==============  
    def getList(self):
	return mc.sets(self.mNode, q = True) or []    
    
    def doSetList(self, objectList = []):
	"""
	Reset the list with the objects provided
	"""
	self.purge()
	if type(objectList) is list:
	    for o in objectList:
		self.addObj(o)
	else:
	    self.addObj(objectList)
	    
	return self.getList()
    def deleteSet(self):
	if not self.isReferenced():
	    del(self)	    
    
    value = property(getList, doSetList, deleteSet)
	
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def doesContain(self,obj):
	assert mc.objExists(obj),"'%s' doesn't exist"%obj
        buffer = mc.ls(obj,shortNames=True)        
	for o in self.getList():
	    if str(o) ==  buffer[0]:
		return True
	return False
		
    def getParents(self):
        """ 
        Updates the stored data
        
        Stores basic data, qss state and type
        
        """
        return mc.listSets(o=self.mNode) or False
                                  
    def addObj(self,info,*a,**kw):
        """ 
        Store information to a set in maya via case specific attribute.
        
        Keyword arguments:
        info(string) -- must be an object in the scene
        
        """
        if not mc.objExists(info):
	    log.warning("'%s' doesn't exist"%info)
	    return False
        if info == self.mNode:
            return False
        
        if info in self.getList():
            log.debug("'%s' is already stored on '%s'"%(info,self.mNode))    
            return
        try:
            mc.sets(info,add = self.mNode)
            log.debug("'%s' added to '%s'!"%(info,self.mNode))  	    
        except:
            log.warning("'%s' failed to add to '%s'"%(info,self.mNode))    
            
    def addSelected(self): 
        """ Store selected objects """
        # First look for attributes in the channel box
        SelectCheck = False
        
        channelBoxCheck = search.returnSelectedAttributesFromChannelBox()
        if channelBoxCheck:
            SelectCheck = True
            for item in channelBoxCheck:
                self.add(item)
            return
        
        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
	#log.info("Storing : %s"%toStore)
        for item in toStore:
	    self.add(item)
	    SelectCheck = True 

        if not SelectCheck:
            log.warning("No selection found")   
            
    def removeObj(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        buffer = mc.ls(info,shortNames=True)   
	info = buffer[0]
	
        if not self.doesContain(info):
            log.warning("'%s' isn't already stored '%s'"%(info,self.mNode))    
            return
        try:
            mc.sets(info,rm = self.mNode)    
            log.warning("'%s' removed from '%s'!"%(info,self.mNode))  
            
        except:
            log.warning("'%s' failed to remove from '%s'"%(info,self.mNode))    
            
    def removeSelected(self): 
        """ Store elected objects """
        SelectCheck = False
        
        # First look for attributes in the channel box
        channelBoxCheck = search.returnSelectedAttributesFromChannelBox()
        if channelBoxCheck:
            SelectCheck = True                            
            for item in channelBoxCheck:
                self.remove(item)
            return
        
        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.remove(item)
                SelectCheck = True                                
            except:
                log.warning("Couldn't remove '%s'"%(item)) 
                
        if not SelectCheck:
            log.warning("No selection found")   
                    
    def purge(self):
        """ Purge all set memebers from a set """
        try:
            mc.sets( clear = self.mNode)
            log.warning("'%s' purged!"%(self.mNode))     
        except:
            log.warning("'%s' failed to purge"%(self.mNode)) 
        
    def copy(self):
        """ Duplicate a set """
        try:
            buffer = mc.sets(name = ('%s_Copy'%self.mNode), copy = self.mNode)
            log.warning("'%s' duplicated!"%(self.mNode))
	    
	    for attr in dictionary.cgmNameTags:
		if mc.objExists("%s.%s"%(self.mNode,attr)):
		    attributes.doCopyAttr(self.mNode,attr,buffer)
		
	    return buffer
        except:
            log.warning("'%s' failed to copy"%(self.mNode)) 
            
    def select(self):
        """ 
        Select set members or connected objects
        """ 
        if self.getList():
            mc.select(self.getList())
            return
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
    
    def selectSelf(self):
        """ 
        Select set members or connected objects
        """ 
        mc.select(self.mNode,noExpand=True)
    
    def key(self,*a,**kw):
        """ Select the seted objects """        
        if self.getList():
            mc.select(self.getList())
            mc.setKeyframe(*a,**kw)
            return True
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
    
    def reset(self):
        """ Reset the set objects """        
        if self.getList():
            mc.select(self.getList())
            ml_resetChannels.main()        
            return True
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
    
    def deleteKey(self,*a,**kw):
        """ Select the seted objects """        
        if self.getList():
            mc.select(self.getList())
            mc.cutKey(*a,**kw)
            return True
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False   
    
    def deleteCurrentKey(self):
        """ Select the seted objects """        
        if self.getList():
            mc.select(self.getList())
            mel.eval('timeSliderClearKey;')
            return True
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
                    
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmOptionVar - class wrapper for optionVariables in Maya
#=========================================================================
optionVarTypeDict = {'int':['int','i','integer',1,0],
                             'float':['f','float','fl',1.0,0.0],
                             'string':['string','str','s']}  
class cgmOptionVar(object):  
    """ 
    OptionVar Class handler
    
    """
    def __init__(self,varName = None,varType = None,value = None, defaultValue = None):
        """ 
        Intializes an optionVar class handler
        
        Keyword arguments:
        varName(string) -- name for the optionVar
        varType(string) -- 'int','float','string' (default 'int')
        value() -- will attempt to set the optionVar with the value
        defaultValue() -- will ONLY use if the optionVar doesn't exist
        
        """
        #Default to creation of a var as an int value of 0
	if varName is None:
	    raise StandardError,"You must have a optionVar name on call even if it's creating one"
        ### input check
        self.name = varName
        
        #>>> If it doesn't exist, create, else update
        if not mc.optionVar(exists = self.name):
            if varType is not None:
                requestVarType = self.returnVarTypeFromCall(varType)
            elif defaultValue is not None:
                requestVarType = search.returnDataType(defaultValue)                
            elif value is not None:
                requestVarType = search.returnDataType(value)
            else:
                requestVarType = 'int'
                
            if requestVarType:
                self.create(requestVarType)
                if defaultValue is not None:
                    self.initialStore(defaultValue)
                elif value is not None:
                    self.initialStore(value)
                                    
            else:
                log.warning("'%s' is not a valid variable type"%varType)
            
        else:               
            self.update(varType)
            
            #Attempt to set a value on call
            if value is not None:           
                self.value = value
		
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #value
    #==============    
    def getValue(self):
	if mc.optionVar(exists = self.name):
	    return mc.optionVar(q=self.name)
	else:
	    log.debug("'%s' no longer exists as an option var!"%self.name)
	    raise StandardError, "'%s' no longer exists as an option var!"%self.name
		
    def setValue(self,value):
	if type(value) is list or type(value) is tuple:
	    self.__init__(self.name,self.varType,value = value[0])#Reinitialize
	    for v in value[1:]:
		self.append(v)
	else:
	    if self.varType == 'int':
		try:
		    mc.optionVar(iv = (self.name,int(float(value))))
		except:
		    log.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))
		
	    elif self.varType == 'float':
		try:
		    mc.optionVar(fv = (self.name,float(value)))
		    
		except:
		    log.info("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))
		
	    elif self.varType == 'string':
		try:
		    mc.optionVar(sv = (self.name,str(value)))
		except:
		    log.info("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))
	object.__setattr__(self, self.name, value)
	
	    
    def purge(self):
        """ 
        Purge an optionVar from maya
        """
        try:
            mc.optionVar(remove = self.name)     
        except:
            log.warning("'%s' doesn't exist"%(self.name))
	    
    value = property(getValue, setValue, purge)#get,set,del
    
    #varType
    #==============    
    def getType(self):
	dataBuffer = mc.optionVar(q=self.name)                                         
        typeBuffer = search.returnDataType(dataBuffer) or False
	if not typeBuffer:
	    log.warning("I don't know what this is!")
	    return False
	return typeBuffer

    
    def setType(self,varType = None):
	if not mc.optionVar(exists = self.name):
	    if varType is not None:
		requestVarType = self.returnVarTypeFromCall(varType)             
	    else:
		log.info("Not sure what '%s' is, making as int"%varType)
		requestVarType = 'int'
		
	    if requestVarType:
		self.create(requestVarType)	    
	    else:
		log.warning("'%s' is not a valid variable type"%varType) 
	else:
	    self.update(varType)
    
    varType = property(getType, setType)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    def initialStore(self,value):
        if type(value) is list:
            self.extend(value)
        else:
            if type(self.value) is list:
                self.append(value)                            
            else:
                if value != self.value:
                    self.setValue(value)
                        
    def returnVarTypeFromCall(self, varTypeCheck):    
        for option in optionVarTypeDict.keys():
            if varTypeCheck in optionVarTypeDict.get(option):
                return option
        return 'int'
    
    def update(self,varType = None):
        """ 
        Update the data in case some other process has changed on optionVar
        """
        dataBuffer = self.value 
        requestVarType = self.returnVarTypeFromCall(varType)
	                                            
        if not mc.optionVar(exists = self.name):
            if requestVarType:
                self.create(self.form)
                return
            else:
                return log.warning("'%s' is not a valid variable type"%varType)  
        
        else:
            #If it exists, first check for data buffer
            typeBuffer = search.returnDataType(dataBuffer) or False
            if not typeBuffer:
                log.debug('Changing to int!')
                typeBuffer = 'int'
            
            if varType is not None:    
                if typeBuffer == requestVarType:
		    log.debug("Checks out")
                    return                
                else:
		    log.warning("Converting optionVar type...")
                    self.create(requestVarType)
		    if dataBuffer is not None:
			log.debug("Attempting to set with: %s"%dataBuffer)
			self.value = dataBuffer
			log.debug("Value : %s"%self.value)
                    return  

    def create(self,doType):
        """ 
        Makes an optionVar.
        """
        log.debug( "Creating '%s' as '%s'"%(self.name,doType) )
            
        if doType == 'int':
            mc.optionVar(iv=(self.name,0))
        elif doType == 'float':
            mc.optionVar(fv=(self.name,0))
        elif doType == 'string':
            mc.optionVar(sv=(self.name,''))
              
    def clear(self):
        """
        Clear the data from an option var
        """
        doName = self.name
        doType = self.varType
        self.purge()
        self.__init__(doName,doType)
            
    def append(self,value): 
        if type(self.value) is list or type(self.value) is tuple:
            if value in self.value:
                return log.warning("'%s' already added"%(value))

        if self.varType == 'int':
            try:
                mc.optionVar(iva = (self.name,int(value)))
                log.debug("'%s' added to '%s'"%(value,self.name))
                
            except:
                log.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))
            
        elif self.varType == 'float':
            try:
                mc.optionVar(fva = (self.name,float(value)))
                log.info("'%s' added to '%s'"%(value,self.name))
                
            except:
                log.info("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))
            
        elif self.varType == 'string':
            try:
                mc.optionVar(sva = (self.name,str(value)))
                for i in "",'':
                    if i in self.value:
                        self.remove(i)

                log.info("'%s' added to '%s'"%(value,self.name))           
                
            except:
                log.info("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))

    def remove(self,value):
        if value in self.value:
            try:         
                i = self.value.index(value)
                mc.optionVar(removeFromArray = (self.name,i))
                self.update(self.form)
                log.info("'%s' removed from '%s'"%(value,self.name))
            except:
                log.info("'%s' failed to remove '%s'"%(value,self.name))
        else:
            log.info("'%s' wasn't found in '%s'"%(value,self.name))
            
                            
    def extend(self,valuesList):
        assert type(valuesList) is list,"'%s' not a list"%(valuesList)
        
        for v in valuesList:
            if type(self.value) is list:
                if v not in self.value:
                    self.append(v)
            else:
                if v != self.value:
                    self.append(v)
    
    def toggle(self):
        """
        Toggles an int type variable
        """
        assert self.varType == 'int',"'%s' not an int type var"%(self.name)
        
        self.value = not self.value
        log.debug("'%s':%s"%(self.name,self.value))
        
        
    def select(self):
        """
        Attempts to select the items of a optionVar buffer
        """
        selectList = []
        if self.value:
            for item in self.value:
                if mc.objExists(item):
                    if '.' in item:
                        buffer = mc.ls(item,o=True)
                        if mc.objExists(buffer[0]):
                            selectList.append(buffer[0])
                    else:
                        selectList.append(item)
                
        if selectList:
            mc.select(selectList)
        else:
            log.warning("'%s' is empty!"%self.name)
             
    def existCheck(self):
        """
        Removes non existing items
        """
        for item in self.value:
	    if not mc.objExists(item):
		self.remove(item)
		log.warning("'%s' removed from '%s'"%(item,self.name))
			
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmBuffer - replacement for a multimessage attribute. Stores a list to object
#=========================================================================
class cgmBufferNode(cgmNode):
    def __init__(self,node = None, name = None, value = None, nodeType = 'network', overideMessageCheck = False,**kws):
        """ 
	Replacement for a multimessage attribute when you want to be able to link to an attr
	
        Keyword arguments:
        setName(string) -- name for the set
        
        To Do:
	Add extend,append, replace, remove functions
        """
        ### input check  
        log.debug("In cgmBuffer.__init__ node is '%s'"%node)

	super(cgmBufferNode, self).__init__(node = node,name = name,nodeType = nodeType) 
	self.UNMANAGED.extend(['l_buffer','d_buffer','value','d_indexToAttr','_kw_overrideMessageCheck'])
	self._kw_overrideMessageCheck = overideMessageCheck
	self.__verify__()
        if not self.isReferenced():	    
	    if not self.__verify__():
		raise StandardError,"cgmBufferNode.__init__>> failed to verify : '%s'!"%self.getShortName()
	    if value is not None:
		self.value = value	
		
	self.updateData()
	    	
    def __verify__(self,**kws):
	log.debug("cgmBufferNode>>> in %s.__verify__()"%self.getShortName())
	self.addAttr('messageOverride',initialValue = self._kw_overrideMessageCheck,attrType = 'bool',lock=True)
	return True   
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #value
    #==============    
    def getValue(self):
	return self.l_buffer
    
    @r9General.Timer   
    def setValue(self,value):
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False
	self.purge()#wipe it to reset it
	if type(value) is list or type(value) is tuple:
	    for i in value:
		self.store(i,overideMessageCheck = self.messageOverride)
	else:
	    self.store(value,overideMessageCheck = self.messageOverride) 
	    
    value = property(getValue, setValue)#get,set
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     
    def returnNextAvailableCnt(self):
        """ Get's the next available item number """        
        return self.returnNextAvailableAttrCnt('item_')
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def updateData(self,*a,**kw):
        """ Updates the stored data """
        self.l_buffer = []
        self.d_buffer = {}
	self.d_indexToAttr = {}
	l_itemAttrs = []
	d_indexToAttr = {}
        for attr in self.getUserAttrs():
            if 'item_' in attr:
		index = int(attr.split('item_')[-1])
		dataBuffer = attributes.doGetAttr(self.mNode,attr)
		data = dataBuffer
		self.d_buffer[attr] = data
		self.d_indexToAttr[index] = attr
		self.l_buffer.append(data)
		
	#verify data order
	for key in self.d_indexToAttr.keys():
	    self.l_buffer[key] = self.d_buffer[self.d_indexToAttr[key]]
                    
    def rebuild(self,*a,**kw):
        """ Rebuilds the buffer data cleanly """ 
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False	
	listCopy = copy.copy(self.l_buffer)
	self.value = listCopy
	self.updateData()
                    
    def store(self,info,index = None,allowDuplicates = True,*a,**kw):
        """ 
        Store information to an object in maya via case specific attribute.
        
        Keyword arguments:
        info(string) -- must be an object in the scene
        
        """
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False
	
        if not mc.objExists(info) and self.messageOverride != True:
	    log.warning("'%s' doesn't exist"%info)
	    return
        
        if not allowDuplicates and info in self.l_buffer:
            log.debug("'%s' is already stored on '%s'"%(info,self.mNode))    
            return
        

	if index is not None and index < len(self.l_buffer):
	    cnt = index
	else:
	    cnt = self.returnNextAvailableCnt()
	if self.messageOverride:
	    cgmAttr(self.mNode,('item_'+str(cnt)),value = info,lock=True)	    
	else:
	    attributes.storeInfo(self.mNode,('item_'+str(cnt)),info,overideMessageCheck = self.messageOverride)	    
        
        #attributes.storeInfo(self.mNode,('item_'+str(cnt)),info,overideMessageCheck = self.messageOverride)
	self.updateData()
        #self.l_buffer.append(info)
        #self.d_buffer['item_'+str(cnt)] = info
        
    def doStoreSelected(self): 
        """ Store elected objects """
        # First look for attributes in the channel box
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False
	
        channelBoxCheck = search.returnSelectedAttributesFromChannelBox()
        if channelBoxCheck:
            for item in channelBoxCheck:
                self.store(item,overideMessageCheck = self.messageOverride)
            return
        
        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.store(item,overideMessageCheck = self.messageOverride)
            except:
                log.warning("Couldn't store '%s'"%(item))     
        
    def remove(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False
	
        if info not in self.l_buffer:
            guiFactory.warning("'%s' isn't already stored '%s'"%(info,self.mNode))    
            return
        
        for key in self.d_buffer.keys():
            if self.d_buffer.get(key) == info:
                attributes.doDeleteAttr(self.mNode,key)
                self.l_buffer.remove(info)
                self.d_buffer.pop(key)
                
        log.warning("'%s' removed!"%(info))  
                
        self.updateData()
        
    def doRemoveSelected(self): 
        """ Store elected objects """
        # First look for attributes in the channel box
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False
	
        channelBoxCheck = search.returnSelectedAttributesFromChannelBox()
        if channelBoxCheck:
            for item in channelBoxCheck:
                self.remove(item)
            return
        
        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.remove(item)
            except:
                log.warning("Couldn't remove '%s'"%(item)) 
                
    def purge(self):
        """ Purge all buffer attributes from an object """
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False
	
        userAttrs = mc.listAttr(self.mNode,userDefined = True) or []
        for attr in userAttrs:
            if 'item_' in attr:
                attributes.doDeleteAttr(self.mNode,attr)
                log.debug("Deleted: '%s.%s'"%(self.mNode,attr))  
                
        self.l_buffer = []
        self.d_buffer = {}        
         
    def select(self):
        """ 
        Select the buffered objects. Need to work out nested searching better
        only goes through two nexts now
        """        
        if self.l_buffer:
            selectList = []
            # Need to dig down through the items
            for item in self.l_buffer:
                if search.returnTagInfo(item,'cgmType') == 'objectBuffer':
                    tmpFactory = cgmBuffer(item)
                    selectList.extend(tmpFactory.l_buffer)
                    
                    for item in tmpFactory.l_buffer:
                        if search.returnTagInfo(item,'cgmType') == 'objectBuffer':
                            subTmpFactory = cgmBuffer(item)   
                            selectList.extend(subTmpFactory.l_buffer)
                            
                else:
                    selectList.append(item)
                    
            mc.select(selectList)
            return
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
    
    def key(self,*a,**kw):
        """ Select the buffered objects """        
        if self.l_buffer:
            mc.select(self.l_buffer)
            mc.setKeyframe(*a,**kw)
            return True
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmAttr - separate class
#=========================================================================    
class cgmAttr(object):
    """ 
    Initializes a maya attribute as a class obj. 9/10 times, you can just use a cgmNode with innate attr handling
    """
    attrTypesDict = {'message':['message','msg','m'],
                     'double':['float','fl','f','doubleLinear','doubleAngle','double','d'],
                     'string':['string','s','str'],
                     'long':['long','int','i','integer'],
                     'bool':['bool','b','boolean'],
                     'enum':['enum','options','e'],
                     'double3':['vector','vec','v','double3','d3']}    
    
    def __init__(self,objName,attrName,attrType = False,value = None,enum = False,initialValue = None,lock = None,keyable = None, hidden = None, minValue = None, maxValue = None, defaultValue = None,*a, **kw):
        """ 
        Asserts object's existance then initializes. If 
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
        #>>> Initialization ==================   
	if issubclass(type(objName),r9Meta.MetaClass):
	    self.obj = objName
	else:
            assert mc.objExists(objName) is True, "'%s' doesn't exist" %objName
            self.obj = cgmNode(objName)	    
	
	if attrType:attrType = attributes.validateRequestedAttrType(attrType)
	#value/attr type logic check
	#==============  
	if enum is not False:
	    self.attrType = attrType = 'enum'
	elif value and attrType is False:
	    if type(value) is list:
		for o in value:
		    if mc.objExists(o):
			self.attrType = 'message'		
			log.warning('Multi message mode!')
			break
		    self.attrType = 'double3'#Need better detection here for json and what not
	    elif mc.objExists(value):
		log.debug("'%s' exists. creating as message."%value)
		self.attrType = 'message'		
	    else:
		dataReturn = search.returnDataType(value)
		log.debug("Trying to create attr of type '%s'"%dataReturn)
		self.attrType = attributes.validateRequestedAttrType(dataReturn)
	else:
	    self.attrType = attributes.validateRequestedAttrType(attrType)
	    
        self.attr = attrName
        initialCreate = False
        
        # If it exists we need to check the type. 
        if mc.objExists('%s.%s'%(self.obj.mNode,attrName)):
            log.debug("'%s.%s' exists"%(self.obj.mNode,attrName))
            currentType = mc.getAttr('%s.%s'%(self.obj.mNode,attrName),type=True)
            log.debug("Current type is '%s'"%currentType)
            if not attributes.validateAttrTypeMatch(self.attrType,currentType) and self.attrType is not False:
                if self.obj.isReferenced():
                    log.error("'%s' is referenced. cannot convert '%s' to '%s'!"%(self.obj.mNode,attrName,attrType))                   
                self.doConvert(self.attrType)             
                
            else:
                self.attr = attrName
                self.attrType = currentType
                
        else:
            try:
                if self.attrType == False:
                    self.attrType = 'string'
                    attributes.addStringAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                elif self.attrType == 'double':
                    attributes.addFloatAttributeToObject(self.obj.mNode,attrName,*a, **kw)
                elif self.attrType == 'string':
                    attributes.addStringAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                elif self.attrType == 'long':
                    attributes.addIntegerAttributeToObj(self.obj.mNode,attrName,*a, **kw) 
                elif self.attrType == 'double3':
                    attributes.addVectorAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                elif self.attrType == 'enum':
                    attributes.addEnumAttrToObj(self.obj.mNode,attrName,*a, **kw)
                elif self.attrType == 'bool':
                    attributes.addBoolAttrToObject(self.obj.mNode,attrName,*a, **kw)
                elif self.attrType == 'message':
                    attributes.addMessageAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                else:
                    log.error("'%s' is an unknown form to this class"%(self.attrType))
                
                initialCreate = True
                
	    except StandardError,error:
		log.error("addAttr>>Failure! '%s' failed to add '%s' | type: '%s'"%(self.obj.mNode,attrName,self.attrType))
		raise StandardError,error                  
                     
        if enum:
            try:
                self.setEnum(enum)
            except:
                log.error("Failed to set enum value of '%s'"%enum)        

        if initialValue is not None and initialCreate:
            self.set(initialValue)
          
        elif value is not None:
            self.set(value)
	    
	if minValue is not None:
	    try:
		self.p_minValue = minValue
	    except:
		log.error("addAttr>>minValue on call Failure! %s"%minValue)
		
	if maxValue is not None:
	    try:
		self.p_maxValue = maxValue
	    except:
		log.error("addAttr>>minValue on call Failure! %s"%maxValue)
		
	if defaultValue is not None:
	    try:
		self.p_defaultValue = defaultValue
	    except:
		log.error("addAttr>>minValue on call Failure! %s"%defaultValue)
		
        if type(keyable) is bool:
            self.doKeyable(keyable)   
            
        if type(hidden) is bool:
            self.doHidden(hidden)
            
        if type(lock) is bool:
            self.doLocked(lock)
	    
	log.debug("'%s' initialized. Value: '%s'"%(self.p_combinedName,self.value))
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #value
    #==============    
    def set(self,value,*a, **kw):
        """ 
        Set attr value based on attr type
        
        Keyword arguments:
        value(varied)   
        *a, **kw
        """
	if self.obj.hasAttr(self.attr):
	    if self.attrType == 'message':
		self.doStore(value)	    
	    elif self.getChildren():
		log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
		for i,c in enumerate(self.getChildren()):
		    try:
			cInstance = cgmAttr(self.obj.mNode,c)                        
			if type(value) is list and len(self.getChildren()) == len(value): #if we have the same length of values in our list as we have children, use them
			    cInstance.value = value[i]
			else:    
			    attributes.doSetAttr(cInstance.obj.mNode,cInstance.attr, value, *a, **kw)
		    except:
			log.debug("'%s' failed to set"%c)	
	    else:
		attributes.doSetAttr(self.obj.mNode,self.attr, value, *a, **kw)
		    
	object.__setattr__(self, self.attr, self.value)
        
        
    def get(self,*a, **kw):
        """ 
        Get and store attribute value based on attr type
        
        Keyword arguments:
        *a, **kw
        """    
	try:
	    if self.attrType == 'message':
		return attributes.returnMessageData(self.obj.mNode,self.attr)
	    else:
		return attributes.doGetAttr(self.obj.mNode,self.attr)
        except:
            log.error("'%s.%s' failed to get"%(self.obj.mNode,self.attr))
	    
    def doDelete(self):
        """ 
        Deletes an attribute
        """   
        try:
            attributes.doDeleteAttr(self.obj.mNode,self.attr)
            log.warning("'%s.%s' deleted"%(self.obj.mNode,self.attr))
	    del(self)
        
        except:
            log.error("'%s.%s' failed to delete"%(self.obj.mNode,self.attr))  
	      
    value = property(get, set, doDelete)#get,set,del
    
    #>>> Property - p_combinedName ==================             
    def isCombinedName(self):
	return '%s.%s'%(self.obj.mNode,self.attr)  
    p_combinedName = property(isCombinedName)
    
    def isCombinedShortName(self):
	return '%s.%s'%(self.obj.getShortName(),self.attr)  
    p_combinedShortName = property(isCombinedShortName) 
    
    #>>> Property - p_nameLong ================== 
    def getEnum(self):
	#attributeQuery(attr, node=self.mNode, listEnum=True)[0].split(':')
	return mc.attributeQuery(self.attr, node = self.obj.mNode, listEnum=True)[0].split(':') or False	
    def setEnum(self,enumCommand):
        """ 
        Set the options for an enum attribute
        
        Keyword arguments:
        enumCommand(string) -- 'off:on', 'off=0:on=2', etc
        """   
        try:
            if self.attrType == 'enum':
                if self.p_enum != enumCommand:
                    mc.addAttr ((self.obj.mNode+'.'+self.attr), e = True, at=  'enum', en = enumCommand)
                    log.info("'%s.%s' has been updated!"%(self.obj.mNode,self.attr))
                
            else:
                log.warning("'%s.%s' is not an enum. Invalid call"%(self.obj.mNode,self.attr))
        except:
            log.error("'%s.%s' failed to change..."%(self.obj.mNode,self.attr))
    
    p_enum = property (getEnum,setEnum)
    
    #==========================================  
    # Basic flag properties
    #==========================================   
    #>>> Property - p_locked ==================    
    def isLocked(self):
	return mc.getAttr(self.p_combinedName, lock=True)
    
    def doLocked(self,arg = True):
        """ 
        Set lock state of an attribute
        
        Keyword arguments:
        arg(bool)
        """ 
        assert type(arg) is bool, "doLocked arg must be a bool!"
        if arg:
            if self.getChildren():
                log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if not cInstance.p_locked:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,lock = True) 
                        log.debug("'%s.%s' locked!"%(cInstance.obj.mNode,cInstance.attr))
                
            elif not self.p_locked:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,lock = True) 
                log.debug("'%s.%s' locked!"%(self.obj.mNode,self.attr))
                
        else:
            if self.getChildren():
                log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if cInstance.p_locked:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,lock = False) 
                        log.debug("'%s.%s' unlocked!"%(cInstance.obj.mNode,cInstance.attr))
                
            elif self.p_locked:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,lock = False)           
                log.debug("'%s.%s' unlocked!"%(self.obj.mNode,self.attr))
		
    p_locked = property (isLocked,doLocked)
    
    #>>> Property - p_hidden ================== 
    def isHidden(self):
	hidden = not mc.getAttr(self.p_combinedName,channelBox=True)
	if self.p_keyable:
	    hidden = mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, hidden=True)	
	return hidden
    def doHidden(self,arg = True):
        """ 
        Set hidden state of an attribute
        
        Keyword arguments:
        arg(bool)
        """ 
        assert type(arg) is bool, "doHidden arg must be a bool!"        
        if arg:
            if self.getChildren():
                log.warning("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if not cInstance.p_hidden:
                        if cInstance.p_keyable:
                            cInstance.doKeyable(False)
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,channelBox = False) 
                        log.debug("'%s.%s' hidden!"%(cInstance.obj.mNode,cInstance.attr))
                
            elif not self.p_hidden:
                if self.p_keyable:
                    self.doKeyable(False)
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,channelBox = False) 
                log.debug("'%s.%s' hidden!"%(self.obj.mNode,self.attr))
   
        else:
            if self.getChildren():
                log.warning("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if cInstance.p_hidden:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,channelBox = True) 
                        log.debug("'%s.%s' unhidden!"%(cInstance.obj.mNode,cInstance.attr))
                
            elif self.p_hidden:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,channelBox = True)           
                log.debug("'%s.%s' unhidden!"%(self.obj.mNode,self.attr))
		
    p_hidden = property (isHidden,doHidden) 
    
    #>>> Property - p_locked ==================
    def isKeyable(self):
	return mc.getAttr(self.p_combinedName,keyable=True)
    def doKeyable(self,arg = True):
        """ 
        Set keyable state of an attribute
        
        Keyword arguments:
        arg(bool)
        """         
	KeyableTypes = ['long','float','bool','double','enum','double3','doubleAngle','doubleLinear']  
        assert type(arg) is bool, "doKeyable arg must be a bool!" 
	
	if self.attrType not in KeyableTypes:
	    log.warning("'%s' not a keyable attrType"%self.attrType)
	    return False
	
        if arg:
            if self.getChildren():
                log.warning("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if not cInstance.p_keyable:
                        mc.setAttr(cInstance.nameCombined,e=True,keyable = True) 
                        log.debug("'%s.%s' keyable!"%(cInstance.obj.mNode,cInstance.attr))
                        cInstance.p_hidden = False
                
            elif not self.p_keyable:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,keyable = True) 
                log.debug("'%s.%s' keyable!"%(self.obj.mNode,self.attr))
                self.p_hidden = False
                    
                
        else:
            if self.getChildren():
                log.warning("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if cInstance.p_keyable:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,keyable = False) 
                        log.debug("'%s.%s' unkeyable!"%(cInstance.obj.mNode,cInstance.attr))
                        if not mc.getAttr(cInstance.nameCombined,channelBox=True):
                            cInstance.doHidden(False)                
                
            elif self.p_keyable:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,keyable = False)           
                log.debug("'%s.%s' unkeyable!"%(self.obj.mNode,self.attr))
                if not mc.getAttr(self.p_combinedName,channelBox=True):
                    self.doHidden(False)    
    p_keyable = property (isKeyable,doKeyable) 

    #==========================================    
    # Name flag properties
    #==========================================       
    #>>> Property - p_nameAlias ===============
    def getAlias(self):
	if mc.aliasAttr(self.p_combinedName,q=True):
	    return mc.aliasAttr(self.p_combinedName,q=True) 
	return None
    
    def doAlias(self,arg):
        """ 
        Set the alias of an attribute
        
        Keyword arguments:
        arg(string) -- name you want to use as an alias
        """     
        assert type(arg) is str or unicode,"Must pass string argument into doAlias"                
        if arg:
            try:
		if arg != self.p_nameAlias:
		    return mc.aliasAttr(arg,self.p_combinedName)
		else:log.debug("'%s.%s' already has that alias!"%(self.obj.getShortName(),self.attr))
            except:
                log.warning("'%s.%s' failed to set alias of '%s'!"%(self.obj.mNode,self.attr,arg))
                    
        else:
            if self.p_nameAlias:
                self.attr = self.p_nameLong                
                mc.aliasAttr(self.p_combinedName,remove=True)
		
    p_nameAlias = property (getAlias,doAlias)
                
    #>>> Property - p_nameNice ================== 
    def getNiceName(self):
	return mc.attributeQuery(self.attr, node = self.obj.mNode, niceName = True) or False
    def doNiceName(self,arg):
        """ 
        Set the nice name of an attribute
        
        Keyword arguments:
        arg(string) -- name you want to use as a nice name
        """    
        assert type(arg) is str or unicode,"Must pass string argument into doNiceName"        
        if arg:
            try:
                mc.addAttr(self.p_combinedName,edit = True, niceName = arg)
            except:
                log.error("'%s.%s' failed to set nice name of '%s'!"%(self.obj.mNode,self.p_nameLong,arg))
                    
    p_nameNice = property (getNiceName,doNiceName)
    
    #>>> Property - p_nameLong ================== 
    def getNameLong(self):
	return mc.attributeQuery(self.attr, node = self.obj.mNode, longName = True) or False	
    def doRename(self,arg):
        """ 
        Rename an attribute as something else
        
        Keyword arguments:
        arg(string) -- name you want to use as a nice name
        """            
        assert type(arg) is str or unicode,"Must pass string argument into doRename"
        if arg:
            try:
                if arg != self.p_nameLong:
                    attributes.doRenameAttr(self.obj.mNode,self.p_nameLong,arg)
                    self.attr = arg                    
                else:
                    log.info("'%s.%s' already has that nice name!"%(self.obj.mNode,self.attr,arg))
                    
            except:
                log.error("'%s.%s' failed to rename name of '%s'!"%(self.obj.mNode,self.attr,arg))
    
    p_nameLong = property (getNameLong,doRename)
    
    #================================================    
    # Numeric properties
    #================================================    
    #>>> Property - p_defaultValue ==================  
    def getDefault(self):
	if not self.isNumeric():
	    log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
	    return False
	try:
	    defaultValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, listDefault=True)
	    if defaultValue is not False:
		return defaultValue[0]
	    return False
	except:
	    log.error("'%s' failed to query default value" %self.p_combinedName)
	    return False
    
    def doDefault(self,value = None):
        """ 
        Set default settings of an attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """   
        if self.isNumeric(): 
            if value is not None:
                if self.getChildren():
                    log.warning("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                    for c in self.getChildren():
                        cInstance = cgmAttr(self.obj.mNode,c)                        
                        try:
                            mc.addAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,defaultValue = value)
                        except:
                            log.warning("'%s' failed to set a default value"%cInstance.nameCombined)                
                
                else:     
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,defaultValue = value)
                    except:
                        log.error("'%s.%s' failed to set a default value"%(self.obj.mNode,self.attr))     
			
    p_defaultValue = property (getDefault,doDefault)
    
    
    #>>> Property - p_minValue ==================       
    def getMinValue(self):
	if not self.isNumeric():
	    log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
	    return False

	try:
	    minValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, minimum=True)	    
	    if minValue is not False:
		return minValue[0]
	    return False
	except StandardError,error:
	    log.error(error)
	    log.error("'%s' failed to query min value" %self.p_combinedName)
	    return False
	
    def doMin(self,value = None):
        """ 
        Set min value for a numeric attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        if self.isNumeric() and not self.getChildren(): 
            if value is False or None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasMinValue = False)
                    log.warning("'%s.%s' had it's min value cleared"%(self.obj.mNode,self.attr))                     
                except:
                    log.error("'%s.%s' failed to clear a min value"%(self.obj.mNode,self.attr))
            
            elif value is not None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,minValue = value)
                except:
                    log.error("'%s.%s' failed to set a default value"%(self.obj.mNode,self.attr))
	    if self.value < value:
		self.value = value
		log.warning("Value changed due to new min. Value is now %s"%value)
	else:
	    log.debug("'%s' is not a numeric attribute"%self.p_combinedName)	    
	    return False
		    
    p_minValue = property (getMinValue,doMin)
    
    #>>> Property - p_softMin ==================  
    def getSoftMin(self):
	if not self.isNumeric():
	    log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
	    return False
	try:
	    minValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, softMin=True)
	    if minValue is not False:
		return minValue[0]
	    return False
	except:
	    return False
	
    def doSoftMin(self,value = None):
        """ 
        Set soft min value for a numeric attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        if self.isNumeric() and not self.getChildren(): 
            if value is False:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasSoftMinValue = 0)
                    log.warning("'%s.%s' had it's soft max value cleared"%(self.obj.mNode,self.attr))                     
                except:
                    log.error("'%s.%s' failed to clear a soft max value"%(self.obj.mNode,self.attr))  
            elif value is not None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,softMinValue = value)
                except:
                    log.error("'%s.%s' failed to set a soft max value"%(self.obj.mNode,self.attr))
	    else:
		log.debug("'%s' is not a numeric attribute"%self.p_combinedName)	    
		return False
    p_softMin = property (getSoftMin,doSoftMin)
    
    #>>> Property - p_softMax ==================  
    def getSoftMax(self):
	if not self.isNumeric():
	    log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
	    return False
	try:
	    maxValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, softMax=True)
	    if maxValue is not False:
		return maxValue[0]
	    return False
	except:
	    return False
	
    def doSoftMax(self,value = None):
        """ 
        Set soft max value for a numeric attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        if self.isNumeric() and not self.getChildren(): 
            if value is False:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasSoftMaxValue = 0)
                    log.warning("'%s.%s' had it's soft max value cleared"%(self.obj.mNode,self.attr))                     
                except:
                    log.error("'%s.%s' failed to clear a soft max value"%(self.obj.mNode,self.attr))  
            elif value is not None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,softMaxValue = value)
                except:
                    log.error("'%s.%s' failed to set a soft max value"%(self.obj.mNode,self.attr))
	    else:
		log.debug("'%s' is not a numeric attribute"%self.p_combinedName)	    
		return False
    p_softMax = property (getSoftMax,doSoftMax)
    
    #>>> Property - p_maxValue ==================         
    def getMaxValue(self):
	if not self.isNumeric():
	    log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
	    return False
	try:
	    maxValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, maximum=True)
	    if maxValue is not False:
		return maxValue[0]
	    return False
	except:
	    log.error("'%s' failed to query max value" %self.p_combinedName)
	    return False
	
    def doMax(self,value = None):
        """ 
        Set max value for a numeric attribute
        
        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        if self.isNumeric() and not self.getChildren(): 
            if value is False or None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasMaxValue = False)
                    log.warning("'%s.%s' had it's max value cleared"%(self.obj.mNode,self.attr))                     
                except:
                    log.error("'%s.%s' failed to clear a max value"%(self.obj.mNode,self.attr))
            elif value is not None:
                try:
                    mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,maxValue = value)
                except:
                    log.error("'%s.%s' failed to set a default value"%(self.obj.mNode,self.attr))
	    if self.value > value:
		self.value = value
		log.warning("Value changed due to new max. Value is now %s"%value)
	else:
	    log.error("'%s' is not a numeric attribute"%self.p_combinedName)	    
	    return False
		    
    p_maxValue = property (getMaxValue,doMax)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Queries ==================  
    def isDynamic(self):
	if self.attr in mc.listAttr(self.obj.mNode, userDefined = True):
	    return True
	log.error("%s.isDynamic: False"%self.p_combinedShortName)
	return False
    def isNumeric(self):
	if mc.getAttr(self.p_combinedName,type=True) in ['string','message','enum','bool']:
	    return False
	return True
    def isReadable(self):
	if not self.isDynamic():
	    log.warning("'%s' is not a dynamic attribute. 'readable' not relevant"%self.p_combinedName)	    	    	    
	    return False
	return mc.addAttr(self.p_combinedName,q=True,r=True) or False
    def isWritable(self):
	if not self.isDynamic():
	    log.warning("'%s' is not a dynamic attribute. 'writable' not relevant"%self.p_combinedName)	    	    
	    return False
	return mc.addAttr(self.p_combinedName,q=True,w=True) or False
    def isStorable(self):
	if not self.isDynamic():
	    log.warning("'%s' is not a dynamic attribute. 'storable' not relevant"%self.p_combinedName)	    	    
	    return False
	return mc.addAttr(self.p_combinedName,q=True,s=True) or False    
    def isUsedAsColor(self):
	if not self.isDynamic():
	    log.warning("'%s' is not a dynamic attribute. 'usedAsColor' not relevant"%self.p_combinedName)	    
	    return False
	return mc.addAttr(self.p_combinedName,q=True,usedAsColor=True) or False  
    
    def isUserDefined(self):
	if self.p_nameLong in mc.listAttr(self.obj.mNode, userDefined = True):
	    return True
	return False
    
    def getRange(self):
	if not self.isNumeric():
	    log.warning("'%s' is not a numeric attribute. 'range' not relevant"%self.p_combinedName)	    
	    return False
	return mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, range=True) or False    
    
    def getSoftRange(self):
	if not self.isNumeric():
	    log.warning("'%s' is not a numeric attribute. 'range' not relevant"%self.p_combinedName)	    
	    return False
	return mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, softRange=True) or False     
    
    #>>> Family ==================  
    def getChildren(self):
	return mc.attributeQuery(self.attr, node = self.obj.mNode, listChildren=True) or []
    def getParent(self):
	return mc.attributeQuery(self.attr, node = self.obj.mNode, listParent=True) or []
    def getSiblings(self):
	return mc.attributeQuery(self.attr, node = self.obj.mNode, listSiblings=True) or []
    
    #>>> Connections ==================  
    def getDriven(self,obj=False,skipConversionNodes = False):
	"""returns attr by default"""
	if obj:
	    return attributes.returnDrivenObject(self.p_combinedName,skipConversionNodes)
	return attributes.returnDrivenAttribute(self.p_combinedName,skipConversionNodes) or None
    def getDriver(self,obj=False,skipConversionNodes = False):
	"""returns attr by default"""
	if obj:
	    return attributes.returnDriverObject(self.p_combinedName,skipConversionNodes) or None	    
	return attributes.returnDriverAttribute(self.p_combinedName,skipConversionNodes) or None
	                              
    def doConvert(self,attrType):
        """ 
        Converts an attribute type from one to another while preserving as much data as possible.
        
        Keyword arguments:
        attrType(string)        
        """
        if self.obj.isReferenced():
            log.error("'%s' is referenced. cannot convert '%s' to '%s'!"%(self.obj.mNode,self.attr,attrType))                           

        if self.getChildren():
            log.error("'%s' has children, can't convert"%self.p_combinedName)
        keyable = copy.copy(self.p_keyable)
        hidden =  copy.copy(self.p_hidden)
        locked =  copy.copy(self.p_locked)
        storedNumeric = False
        if self.isNumeric() and not self.getChildren():
            storedNumeric = True
            minimum =  copy.copy(self.p_minValue)
            maximum =  copy.copy(self.p_maxValue)
            default =  copy.copy(self.p_defaultValue)
            softMin =  copy.copy(self.p_softMin)
            softMax =  copy.copy(self.p_softMax)
        
        attributes.doConvertAttrType(self.p_combinedName,attrType)
        
        #>>> Reset variables
        self.doHidden(hidden)
        self.doKeyable(keyable)        
        self.doLocked(locked)

        if self.isNumeric() and not self.getChildren() and storedNumeric:
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
        
        self.attrType = mc.getAttr(self.p_combinedName,type=True)    
        log.info("'%s.%s' converted to '%s'"%(self.obj.mNode,self.attr,attrType))
                        
    def isMulti(self):
	return mc.addAttr("%s.%s"%(self.obj.mNode,self.attr),q=True,m=True)
    def isIndexMatters(self):
	return mc.addAttr("%s.%s"%(self.obj.mNode,self.attr),q=True,im=True)
    
    def getMessage(self,*a, **kw):
        """ 
        Get and store attribute value as if they were messages. Used for bufferFactory to use a connected
        attribute as a poor man's attribute message function
        
        Keyword arguments:
        *a, **kw
        """   
        try:
            if self.attrType == 'message':
                return attributes.returnMessageObject(self.obj.mNode,self.attr)
                if search.returnObjectType(self.value) == 'reference':
                    if attributes.repairMessageToReferencedTarget(self.obj.mNode,self.attr,*a,**kw):
                        return attributes.returnMessageObject(self.obj.mNode,self.attr)                        
            else:
                return attributes.returnDriverAttribute("%s.%s"%(self.obj.mNode,self.attr))

            log.debug("'%s.%s' >Message> '%s'"%(self.obj.mNode,self.attr,self.value))
            return self.value
            
        except:
            log.error("'%s.%s' failed to get"%(self.obj.mNode,self.attr))
               
            
    def doStore(self,infoToStore,convertIfNecessary = True):
        """ 
        Store information to an object. If the info exits as an object, it stores as a message node. Otherwise there are
        other storing methods.
        
        Keyword arguments:
        infoToStore(string) -- string of information to store
        convertIfNecessary(bool) -- whether to convert the attribute if it needs to to store it. Default (True)
        """   
        if self.attrType == 'message':
            self.obj.doStore(self.attr,infoToStore)
        elif convertIfNecessary:
            self.doConvert('message')
            self.obj.doStore(self.attr,infoToStore)                
            
        #except:
          #  log.error("'%s.%s' failed to store '%s'"%(self.obj.mNode,self.attr,infoToStore))
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Set Options
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>                                                        

                
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
        
        return attributes.returnCompatibleAttrs(self.obj.mNode,self.p_nameLong,target,*a, **kw)
         
    
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
                attributes.doConnectAttr(self.p_combinedName,target)
            except:
                log.warning("'%s' failed to connect to '%s'!"%(self.p_combinedName,target))  
                
        else:
            #If the object has a transform
            matchAttr = attributes.returnMatchNameAttrsDict(self.obj.mNode,target,[self.p_nameLong]) or []
            if matchAttr:
                #If it has a matching attribute
                try:
                    attributes.doConnectAttr(self.p_combinedName,('%s.%s'%(target,matchAttr.get(self.p_nameLong))))
                except:
                    log.warning("'%s' failed to connect to '%s'!"%(self.p_combinedName,target))
            else:
                print "Target object doesn't have this particular attribute"

 
                
    def doConnectIn(self,source,childIndex = False,*a, **kw):
        """ 
        Attempts to make a connection from a source to our instanced attribute
        
        Keyword arguments:
        source(string) - object or attribute to connect to
        *a, **kw
        """ 
        assert mc.objExists(source),"'%s' doesn't exist"%source
               
        if '.' in source:           
            try:
                attributes.doConnectAttr(source,self.p_combinedName)
            except:
                log.warning("'%s' failed to connect to '%s'!"%(source,self.p_combinedName))  
                
        else:
            #If the object has a transform
            matchAttr = attributes.returnMatchNameAttrsDict(self.obj.mNode,source,[self.p_nameLong]) or []
            if matchAttr:
                #If it has a matching attribute
                try:
                    attributes.doConnectAttr(('%s.%s'%(source,matchAttr.get(self.p_nameLong))),self.p_combinedName)
                except:
                    log.warning("'%s' failed to connect to '%s'!"%(source,self.p_combinedName))
            else:
                print "Source object doesn't have this particular attribute"
                
    def doCopyTo(self,target, targetAttrName = None, *a,**kw):
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
        
	log.debug("AttrFactory instance: '%s'"%self.p_combinedName)
	log.debug("convertToMatch: '%s'"%convertToMatch)
	log.debug("targetAttrName: '%s'"%targetAttrName)
	log.debug("incomingConnections: '%s'"%incomingConnections)
	log.debug("outgoingConnections: '%s'"%outgoingConnections)
	log.debug("keepSourceConnections: '%s'"%keepSourceConnections)
	log.debug("copyAttrSettings: '%s'"%copyAttrSettings)
	log.debug("connectSourceToTarget: '%s'"%connectSourceToTarget)
	log.debug("keepSourceConnections: '%s'"%keepSourceConnections)
	log.debug("connectTargetToSource: '%s'"%connectTargetToSource)
            
        copyTest = [values,incomingConnections,outgoingConnections,keepSourceConnections,connectSourceToTarget,copyAttrSettings]
        
        if sum(copyTest) < 1:
            log.warning("You must have at least one option for copying selected. Otherwise, you're looking for the 'doDuplicate' function.")            
            return False

        if '.' in list(target):
            targetBuffer = target.split('.')
            if len(targetBuffer) == 2:
                attributes.doCopyAttr(self.obj.mNode,
                                      self.p_nameLong,
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
                                  self.p_nameLong,
                                  target,
                                  targetAttrName,
                                  convertToMatch = convertToMatch,
                                  values=values, incomingConnections = incomingConnections,
                                  outgoingConnections=outgoingConnections, keepSourceConnections = keepSourceConnections,
                                  copyAttrSettings = copyAttrSettings, connectSourceToTarget = connectSourceToTarget)                                                      
        #except:
        #    log.warning("'%s' failed to copy to '%s'!"%(target,self.p_combinedName))          
            
    def doTransferTo(self,target):
        """ 
        Transfer an instanced attribute to a target with all settings and connections intact
        
        Keyword arguments:
        target(string) -- object to transfer it to
        *a, **kw
        """ 
        assert mc.objExists(target),"'%s' doesn't exist"%target
        assert mc.ls(target,type = 'transform',long = True),"'%s' Doesn't have a transform"%target
        assert self.obj.isTransform() is not False,"'%s' Doesn't have a transform. Transferring this attribute is probably a bad idea. Might we suggest doCopyTo along with a connect to source option"%self.obj.mNode        
        assert mc.ls(target,long=True) != [self.obj.mNode], "Can't transfer to self!"
        assert '.' not in list(target),"'%s' appears to be an attribute. Can't transfer to an attribute."%target
        assert self.isDynamic() is True,"'%s' is not a dynamic attribute."%self.p_combinedShortName
        
        #mc.copyAttr(self.obj.mNode,self.target.obj.mNode,attribute = [self.target.attr],v = True,ic=True,oc=True,keepSourceConnections=True)
        attributes.doCopyAttr(self.obj.mNode,
                              self.p_nameLong,
                              target,
                              self.p_nameLong,
                              convertToMatch = True,
                              values = True, incomingConnections = True,
                              outgoingConnections = True, keepSourceConnections = False,
                              copyAttrSettings = True, connectSourceToTarget = False)
        self.doDelete()

class NameFactory(object):
    """ 
    New Name Factory. Finds a 
    """
    def __init__(self,node,doName = False):
        """ 
        """
        if issubclass(type(node),cgmNode):
            self.i_node = node
        elif mc.objExists(node):
            self.i_node = cgmNode(node)
        else:
            raise StandardError,"NameFactory.go >> node doesn't exist: '%s'"%node
        log.debug("self.i_node: '%s'"%self.i_node)
        #Initial Data        
	self.i_nameParents = []
	self.i_nameChildren = []
	self.i_nameSiblings = []
        
    def isNameLinked(self,node = None):   
	if node is None:
	    i_node = self.i_node
	elif issubclass(type(node),cgmNode):
	    i_node = node
	elif mc.objExists(node):
	    i_node = cgmNode(node)
	else:
	    raise StandardError,"NameFactory.isNameLinked >> node doesn't exist: '%s'"%node
	
        if i_node.hasAttr('cgmName') and i_node.getMessage('cgmName'):
            return True
        return False
    
    #@r9General.Timer
    def getMatchedParents(self, node = None):  
	if node is None:
	    i_node = self.i_node
	elif issubclass(type(node),cgmNode):
	    i_node = node
	elif mc.objExists(node):
	    i_node = cgmNode(node)
	else:
	    raise StandardError,"NameFactory.getMatchedParents >> node doesn't exist: '%s'"%node
	
        parents = search.returnAllParents(i_node.mNode)
        self.i_nameParents = []
        if parents:
            #parents.reverse()
            d_nameDict = i_node.getNameDict()
            for p in parents :
                i_p = cgmNode(p)
                if i_p.getNameDict() == d_nameDict:
                    self.i_nameParents.append(i_p)
                    log.debug("Name parent found: '%s'"%i_p.mNode)
		else:break
        return self.i_nameParents
    
    def getMatchedChildren(self, node = None):  
	if node is None:
	    i_node = self.i_node
	elif issubclass(type(node),cgmNode):
	    i_node = node
	elif mc.objExists(node):
	    i_node = cgmNode(node)
	else:
	    raise StandardError,"NameFactory.getMatchedChildren >> node doesn't exist: '%s'"%node
	
        #>>> Count our matched name children range
        children = mc.listRelatives (i_node.mNode, allDescendents=True,type='transform',fullPath=True)
        self.i_nameChildren = []        
        if children:
            #children.reverse()
            d_nameDict = i_node.getNameDict()            
            for c in children :
                i_c = cgmNode(c)
                if i_c.getNameDict() == d_nameDict:
                    self.i_nameChildren.append(i_c)
                    log.debug("Name child found: '%s'"%i_c.mNode)
		else:break
        return self.i_nameChildren
    
    def getMatchedSiblings(self, node = None):
	if node is None:
	    i_node = self.i_node
	elif issubclass(type(node),cgmNode):
	    i_node = node
	elif mc.objExists(node):
	    i_node = cgmNode(node)
	else:
	    raise StandardError,"NameFactory.getMatchedSiblings >> node doesn't exist: '%s'"%node
	
        self.i_nameSiblings = []
        d_nameDict = i_node.getNameDict()        
        for s in i_node.getSiblings():                    
            i_c = cgmNode(s)
            if i_c.getNameDict() == d_nameDict and i_c.mNode != i_node.mNode:
                self.i_nameSiblings.append(i_c)
                log.debug("Name sibling found: '%s'"%i_c.mNode)                

        return self.i_nameSiblings
    
    #@r9General.Timer    
    def getFastIterator(self, node = None):
	"""
	Fast iterate finder
	"""
	if node is None:i_node = self.i_node
	elif issubclass(type(node),cgmNode):i_node = node
	elif mc.objExists(node):i_node = cgmNode(node)
	else:raise StandardError,"NameFactory.getBaseIterator >> node doesn't exist: '%s'"%node
		
        self.int_fastIterator = 0
        #If we have an assigned iterator, start with that
	d_nameDict = i_node.getNameDict()	
        if i_node.getMayaAttr('cgmIterator') is not False:
            return int(i_node.getMayaAttr('cgmIterator'))
			      
	self.d_nameCandidate = d_nameDict
	self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)  
	
	#Now that we have a start, we're gonna see if that name is taken by a sibling or not
	def getNewNameCandidate(self):
	    self.int_fastIterator+=1#add one
	    log.debug("Counting in getBaseIterator: %s"%self.int_fastIterator)				
	    self.d_nameCandidate['cgmIterator'] = str(self.int_fastIterator)
	    self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
	    log.debug("Checking: '%s'"%self.bufferName)
	    return self.bufferName
	
	mc.rename(i_node.mNode,self.bufferName)#Name it
	log.debug("Checking: '%s'"%self.bufferName)
	if self.bufferName != i_node.getShortName():
	    self.int_fastIterator = 1
	    self.d_nameCandidate['cgmIterator'] = str(self.int_fastIterator)
	    self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
	    mc.rename(i_node.mNode,self.bufferName)#Name it
	    while self.bufferName != i_node.getShortName() and self.int_fastIterator <100:
		getNewNameCandidate(self)	
		mc.rename(i_node.mNode,self.bufferName)#Name it
	
	log.debug("fastIterator: %s"%self.int_fastIterator)
        return self.int_fastIterator
    
    #@r9General.Timer    
    def getBaseIterator(self, node = None):
	if node is None:
	    i_node = self.i_node
	elif issubclass(type(node),cgmNode):
	    i_node = node
	elif mc.objExists(node):
	    i_node = cgmNode(node)
	else:
	    raise StandardError,"NameFactory.getBaseIterator >> node doesn't exist: '%s'"%node
	
        self.int_baseIterator = 0
        #If we have an assigned iterator, start with that
	d_nameDict = i_node.getNameDict()
        if 'cgmIterator' in d_nameDict.keys():
            return int(d_nameDict.get('cgmIterator'))
	    
	#Gather info
	i_nameParents = self.getMatchedParents(i_node)
	i_nameChildren = self.getMatchedChildren(i_node)
	i_nameSiblings = self.getMatchedSiblings(i_node)
	
        if i_nameParents:#If we have parents 
            self.int_baseIterator =  len(i_nameParents) + 1
        elif i_nameChildren or i_nameSiblings:#If we have children, we can't be 0
            self.int_baseIterator = 1
	    
	#Now that we have a start, we're gonna see if that name is taken by a sibling or not
        if i_nameSiblings:#check siblings
	    def getNewNameCandidate(self):
		self.int_baseIterator+=1#add one
		log.debug("Counting in getBaseIterator: %s"%self.int_baseIterator)				
		self.d_nameCandidate['cgmIterator'] = str(self.int_baseIterator)
		self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
		log.debug("Checking: '%s'"%self.bufferName)
		return self.bufferName	    
	    
	    self.d_nameCandidate = i_node.getNameDict()
	    if self.int_baseIterator:
		self.d_nameCandidate['cgmIterator'] = str(self.int_baseIterator)
	    self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
	    
            l_siblingShortNames = [i_s.getBaseName() for i_s in i_nameSiblings]
            log.debug("Checking sibblings: %s"%l_siblingShortNames)
	    log.debug("Checking: '%s'"%self.bufferName)	    
            while self.bufferName in l_siblingShortNames and self.int_baseIterator <100:
                getNewNameCandidate(self)	
	
	log.debug("baseIterator: %s"%self.int_baseIterator)
        return self.int_baseIterator
    
    #@r9General.Timer    
    def getIterator(self,node = None):
        """
        """
	if node is None:
	    i_node = self.i_node
	elif issubclass(type(node),cgmNode):
	    i_node = node
	elif mc.objExists(node):
	    i_node = cgmNode(node)
	else:
	    raise StandardError,"NameFactory.getIterator >> node doesn't exist: '%s'"%node
	    
        self.int_iterator = 0
        
        def getNewNameCandidate(self):
            self.int_iterator+=1#add one
	    log.debug("Counting in getIterator: %s"%self.int_iterator)	    
            self.d_nameCandidate['cgmIterator'] = str(self.int_iterator)
            self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
            return self.bufferName
            
        if 'cgmIterator' in i_node.getNameDict().keys():
            return int(self.objGeneratedNameDict.get('cgmIterator'))
        
        #Gather info
        i_nameParents = self.getMatchedParents(node = i_node)
        i_nameChildren = self.getMatchedChildren(node = i_node)
        i_nameSiblings = self.getMatchedSiblings(node = i_node)
        
        if i_nameParents:#If we have parents 
            self.int_iterator = self.getBaseIterator(i_nameParents[-1]) + len(i_nameParents)
	else:
	    self.int_iterator = self.getBaseIterator(node = i_node)
            
        #Now that we have a start, we're gonna see if that name is taken by a sibling or not
        self.d_nameCandidate = i_node.getNameDict()
        if self.int_iterator:
            self.d_nameCandidate['cgmIterator'] = str(self.int_iterator)
        self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
        
        log.debug("bufferName: '%s'"%self.bufferName)
        if not mc.objExists(self.bufferName):
            log.debug('Good name candidate')
            return self.int_iterator
        else:#if there is only one
            for obj in mc.ls(self.bufferName):
                i_bufferName = cgmNode(obj)
                if i_node.mNode == i_bufferName.mNode:
                    log.debug("I'm me! : %s"%self.int_iterator)
                    return self.int_iterator
                
        if i_nameSiblings:#check siblings
            l_siblingShortNames = [i_s.getBaseName() for i_s in i_nameSiblings]
            log.debug("Checking sibblings: %s"%l_siblingShortNames)
            while self.bufferName in l_siblingShortNames and self.int_iterator <100:
                getNewNameCandidate(self)
            """
            for i_s in i_nameSiblings:
                if i_node.getShortName() == self.bufferName:
                    log.debug("I'm me! : %s"%self.int_iterator)
                    return self.int_iterator                    
                elif i_s.getShortName() == self.bufferName:
                    log.debug("Sibling has this")
                    getNewNameCandidate(self)
                else:
                    getNewNameCandidate(self)                    
            """
        log.debug("getIterator: %s"%self.int_iterator)
        return self.int_iterator
    
    #@r9General.Timer
    def returnUniqueGeneratedName(self, ignore='none',node = None,fastIterate = True, **kws):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Returns a generated name with iteration for heirarchy objects with the same tag info
    
        ARGUMENTS:
        ignore(string) - default is 'none', only culls out cgmtags that are 
                         generated via returnCGMOrder() function
    
        RETURNS:
        name(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
	if node is None:i_node = self.i_node
	elif issubclass(type(node),cgmNode):i_node = node
	elif mc.objExists(node):i_node = cgmNode(node)
	else:raise StandardError,"NameFactory.getIterator >> node doesn't exist: '%s'"%node
	
        if type(ignore) is not list:ignore = [ignore]
        log.debug("ignore: %s"%ignore)
        
        #>>> Dictionary driven order first build
        d_updatedNamesDict = nameTools.returnObjectGeneratedNameDict(i_node.mNode,ignore)
        
        if 'cgmName' not in d_updatedNamesDict.keys() and search.returnObjectType(i_node.mNode) !='group' and 'cgmName' not in ignore:
            i_node.addAttr('cgmName',i_node.getShortName(),attrType = 'string',lock = True)
            #d_updatedNamesDict = nameTools.returnObjectGeneratedNameDict(i_node.mNode,ignore)
	    d_updatedNamesDict['cgmName'] = i_node.getShortName()
	    
        if fastIterate:  
	    iterator = self.getFastIterator(node = i_node)
	else:
	    iterator = self.getIterator(node = i_node)  
	    
	if iterator:
	    d_updatedNamesDict['cgmIterator'] = str(iterator)
                
        log.debug(nameTools.returnCombinedNameFromDict(d_updatedNamesDict))
        return nameTools.returnCombinedNameFromDict(d_updatedNamesDict)
    
    #@r9General.Timer
    def doNameObject(self,node = None,fastIterate = True, **kws):
	if node is None:i_node = self.i_node
	elif issubclass(type(node),cgmNode):i_node = node
	elif mc.objExists(node):i_node = cgmNode(node)
	else:raise StandardError,"NameFactory.doNameObject >> node doesn't exist: '%s'"%node
	log.debug("Naming: '%s'"%i_node.getShortName())
        nameCandidate = self.returnUniqueGeneratedName(node = i_node, fastIterate=fastIterate,**kws)
	log.debug("nameCandidate: %s"%nameCandidate)
	mc.rename(i_node.mNode,nameCandidate)
        #i_node.rename(nameCandidate)
	
        str_baseName = i_node.getBaseName()
        if  str_baseName != nameCandidate:
            log.warning("'%s' not named to: '%s'"%(str_baseName,nameCandidate))
            
        return str_baseName
    
    #@r9General.Timer    
    def doName(self,fastIterate = True,nameChildren=False,nameShapes = False,node = None,**kws):
	if node is None:i_node = self.i_node
	elif issubclass(type(node),cgmNode):i_node = node
	elif mc.objExists(node):i_node = cgmNode(node)
	else:raise StandardError,"NameFactory.doName >> node doesn't exist: '%s'"%node
	
	#Try naming object
	try:self.doNameObject(node = i_node,fastIterate=fastIterate,**kws)
	except StandardError,error:
	    raise StandardError,"NameFactory.doName.doNameObject failed: '%s'|%s"%(i_node.mNode,error)
	
	i_rootObject = i_node
	
	if nameShapes:
	    shapes = mc.listRelatives(i_rootObject.mNode,shapes=True,fullPath=True) or []
	    if shapes:
		l_iShapes = []
		for s in shapes:
		    if not mc.referenceQuery(s, isNodeReferenced=True):
			l_iShapes.append(cgmNode(s))
		for i_s in l_iShapes:
		    log.debug("on shape: '%s'"%i_s.mNode)
		    try:self.doNameObject(node = i_s, fastIterate=fastIterate,**kws)
		    except StandardError,error:
			raise StandardError,"NameFactory.doName.doNameObject child ('%s') failed: %s"%i_node.getShortName(),error
			
	#Then the children
	if nameChildren:#Initialize them all so we don't lose them
	    l_iChildren = []
	    for o in mc.listRelatives(i_rootObject.mNode, allDescendents = True,type='transform',fullPath=True) or []:
		l_iChildren.append(cgmNode(o))
	    
	    if l_iChildren:
		l_iChildren.reverse()
		for i_c in l_iChildren:
		    log.debug("on child: '%s'"%i_c.mNode)		    
		    try:self.doNameObject(node = i_c,fastIterate=fastIterate,**kws)
		    except StandardError,error:
			raise StandardError,"NameFactory.doName.doNameObject child ('%s') failed: %s"%i_node.getShortName(),error




#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================  
def getMetaNodesInitializeOnly(mTypes = ['cgmPuppet','cgmMorpheusPuppet','cgmMorpheusMakerNetwork'],dataType = ''):
    """
    Meant to be a faster get command than Mark's for nodes we only want initializeOnly mode
    """
    """
    checkList = r9Meta.getMetaNodes(mAttrs = 'mClass', mTypes=mTypes,dataType = '')
    returnList = []
    for o in checkList:
	i_o = False
	try:i_o = r9Meta.MetaClass(o,initializeOnly = True)
	except:log.warning("'%s' can't take initializeOnly kw"%o)
	if i_o and i_o.hasAttr('mClass') and i_o.mClass in mTypes:
	    if dataType == 'metaClass':
		returnList.append(i_o)
	    else:
		returnList.append(i_o.mNode)
    """
    checkList = mc.ls(type='network')
    returnList = []
    for o in checkList:
	if attributes.doGetAttr(o,'mClass') in mTypes:
	    returnList.append(o)
    return returnList

#=========================================================================      
# Argument validation
#=========================================================================  
#@r9General.Timer
def validateObjArg(arg = None,mType = None, noneValid = False, default_mType = cgmNode):
    """
    validate an objArg to be able to get instance of the object
    
    arg -- obj or instance
    mType -- if not None, make sure instance is this type
    noneValid -- whether none is a valid arg
    default_mType -- type to intialize as for default
    """
    try:
	i_arg = False
	argType = type(arg)
	if argType in [list,tuple]:#make sure it's not a list
	    if len(arg) ==1:
		arg = arg[0]
	    else:
		raise StandardError,"validateObjArg>>> arg cannot be list or tuple: %s"%arg	
	if not noneValid:
	    if arg in [None,False]:
		raise StandardError,"validateObjArg>>> arg cannot be None"
	else:
	    if arg in [None,False]:
		if arg not in [None,False]:log.warning("validateObjArg>>> arg fail: %s"%arg)
		return False
	log.debug("validateObjArg>>> arg: %s"%arg)
	if issubclass(argType,r9Meta.MetaClass):#we have an instance already
	    i_arg = arg
	elif not mc.objExists(arg):
	    if noneValid: return False
	    else:
		raise StandardError,"validateObjArg>>> Doesn't exist: %s"%arg	
	    
	elif mType is not None:
	    log.debug("validateObjArg>>> mType arg: '%s'"%mType)
	    if i_arg:
		i_autoInstance = i_arg
	    else:
		i_autoInstance = r9Meta.MetaClass(arg)
	    if type(mType) in [unicode,str]:
		log.debug("validateObjArg>>> string mType: '%s'"%mType)
		if i_autoInstance.getAttr('mClass') == mType:
		    return i_autoInstance
		else:
		    raise StandardError,"validateObjArg>>> '%s' Not correct mType: mType:%s != %s"%(i_autoInstance.mNode,type(i_autoInstance),mType)			    
	    else:
		log.debug("validateObjArg>>> class mType: '%s'"%mType)		
		if issubclass(type(i_autoInstance),mType):#if it's a subclass of our mType, good to go
		    return i_autoInstance
		#elif i_autoInstance.hasAttr('mClass') and i_autoInstance.mClass != str(mType).split('.')[-1]:
		    #raise StandardError,"validateObjArg>>> '%s' Not correct mType: mType:%s != %s"%(i_autoInstance.mNode,type(i_autoInstance),mType)	
	    log.debug("validateObjArg>>> Initializing as mType: %s"%mType)	
	    i_arg =  mType(arg)
	else:
	    log.debug("validateObjArg>>> Initializing as defaultType: %s"%default_mType)
	    i_arg = default_mType(arg)
	
	return i_arg
    except StandardError,error:
	log.error("validateObjArg>>Failure! arg: %s | mType: %s"%(arg,mType))
	raise StandardError,error    
    
def validateObjListArg(l_args = None,mType = None, noneValid = False, default_mType = cgmNode):
    try:
	if type(l_args) not in [list,tuple]:l_args = [l_args]
	returnList = []
	for arg in l_args:
	    buffer = validateObjArg(arg,mType,noneValid,default_mType)
	    if buffer:returnList.append(buffer)
	return returnList
    except StandardError,error:
	log.error("validateObjListArg>>Failure! l_args: %s | mType: %s"%(l_args,mType))
	raise StandardError,error    

def validateAttrArg(arg,defaultType = 'float',noneValid = False,**kws):
    """
    Validate an attr arg to usable info
    Arg should be sting 'obj.attr' or ['obj','attr'] format.

    """
    try:
	if type(arg) in [list,tuple] and len(arg) == 2:
	    obj = arg[0]
	    attr = arg[1]
	    combined = "%s.%s"%(arg[0],arg[1])
	elif '.' in arg:
	    obj = arg.split('.')[0]
	    attr = '.'.join(arg.split('.')[1:])
	    combined = arg
	else:
	    raise StandardError,"validateAttrArg>>>Bad attr arg: %s"%arg
	
	if not mc.objExists(obj):
	    raise StandardError,"validateAttrArg>>>obj doesn't exist: %s"%obj
	    
	if not mc.objExists(combined):
	    if noneValid:
		return False
	    else:
		log.debug("validateAttrArg>>> '%s'doesn't exist, creating attr (%s)!"%(combined,defaultType))
		if kws:log.debug("kws: %s"%kws)
		i_plug = cgmAttr(obj,attr,attrType=defaultType,**kws)
	else:
	    i_plug = cgmAttr(obj,attr,**kws)	    
	
	return {'obj':obj ,'attr':attr ,'combined':combined,'mi_plug':i_plug}
    except StandardError,error:
	if noneValid:
	    return False
	else:
	    log.error("validateAttrArg>>Failure! arg: %s"%arg)
	    raise StandardError,error
    
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in
#r9Meta.registerMClassNodeMapping(nodeTypes = ['network','transform','objectSet'])#What node types to look for
