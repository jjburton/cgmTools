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


# From cgm ==============================================================
from cgm.lib.classes import NameFactory
reload(NameFactory)

from cgm.lib.ml import (ml_resetChannels)
reload(ml_resetChannels)

from cgm.lib import (lists,
                     search,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)

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

#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================
      
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
                log.info("Created a transform")
	    elif nodeType == 'optionVar':
		return cgmOptionVar(varName=name,*args,**kws)
            elif nodeType != 'network':
                log.info("Trying to make a node of this type '%s'"%nodeType)
                node = mc.createNode(nodeType)
            else:
                log.info("Make default node")
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
            log.info("Appears to be a '%s'"%mClass)
            log.error("Specialized processing not implemented, initializing as...") 
	    
        objectType = search.returnObjectType(node)
	if objectType == 'objectSet':
            log.info("'%s' Appears to be an objectSet, initializing as cgmObjectSet"%node)	    
	    return cgmObjectSet(node,*args,**kws)
        elif mc.ls(node,type='transform'):
            log.info("'%s' Appears to be a transform, initializing as cgmObject"%node)
            return cgmObject(name = name, node = node)          
        else:
            log.info("Appears to be a '%s'. Initializing as cgmNode"%objectType)  
            return cgmNode(name = name, node = node)    
          
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
	
    def __init__(self,node = None, name = None,nodeType = 'network',*args,**kws):	
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
	        
        super(cgmNode, self).__init__(node=node, name = name, nodeType = nodeType)
	self.update()
	self.__dict__['__name__'] = self.getShortName()
            
	    
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
	    log.info("sending cgmNode.__setMessageAttr__ to MetaClass...")
	    r9Meta.MetaClass.__setMessageAttr__(self,attr,value,**kws)
	elif type(value) is list:
	    log.info("Multi message mode from cgmNode!")
	    attributes.storeObjectsToMessage(value,self.mNode,attr)
	else:
	    attributes.storeObjectToMessage(value,self.mNode,attr)
	    
    def getMessage(self,attr,longNames = True):
	if mc.getAttr('%s.%s' % (self.mNode,attr),type=True)  == 'message':
	    return attributes.returnMessageData(self.mNode,attr,longNames)
	return False
	
    def addAttr(self, attr,value = None, attrType = None,enumName = None,initialValue = None,lock = None,keyable = None, hidden = None,*args,**kws):
        if attr not in self.UNMANAGED and not attr=='UNMANAGED':
	    #enum special handling
	    #valueCarry = None #Special handling for enum and value at the same time
	    #if enum is not None:
		#valueCarry = value
		#value = enum	    
	    
	    if self.hasAttr(attr):#Quick create check for initial value
		initialCreate = False
	    else:
		initialCreate = True
		
		if value is None and initialValue is not None:#If no value and initial value, use it
		    value = initialValue
		    	    
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
		log.warning("'%s.%s' Value was not properly set during creation, setting"%(self.mNode,attr))
		self.__setattr__(attr,value)
		#cgmAttr(self, attrName = attr, value=value)
	    
	    #if valueCarry is not None:
		#self.__setattr__(attr,valueCarry)
		
	    #if initialValue is not None and initialCreate:
		#log.info("In mNode.addAttr, setting initialValue of '%s'"%str(initialValue)) 
		#self.__setattr__(attr,initialValue)
	    
	    #if value and attrType is not 'enum':#Want to be able to really set attr on addAttr call if attr exists
		#self.__setattr__(attr,value)
	    
	    #Easy carry for flag handling - until implemented
	    #==============  
	    if keyable or lock or hidden:
		cgmAttr(self, attrName = attr, lock=lock,keyable=keyable,hidden = hidden)
		
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
    def update(self):
        """ Update the instance with current maya info. For example, if another function outside the class has changed it. """ 
        assert mc.objExists(self.mNode) is True, "'%s' doesn't exist" %obj
	if self.hasAttr('mNodeID'):#experiment
	    log.info("setting mNodeID to '%s'"%self.getShortName())
	    log.info(self.mNodeID)
	    attributes.doSetAttr(self.mNode,'mNodeID',self.getShortName())
	
    def getCGMNameTags(self):
        """
        Get the cgm name tags of an object.
        """
        self.cgm = {}
        for tag in NameFactory.cgmNameTags:
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
	return NameFactory.returnObjectGeneratedNameDict(self.mNode) or {}    
		
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
        return search.returnObjectType(self.mNode)
    
    def getShortName(self):
        buffer = mc.ls(self.mNode,shortNames=True)        
        return buffer[0]
    def getLongName(self):
        buffer = mc.ls(self.mNode,l=True)        
        return buffer[0]    
    
    def doName(self,sceneUnique=False,nameChildren=False):
        """
        Function for naming a maya instanced object using the cgm.NameFactory class.

        Keyword arguments:
        sceneUnique(bool) -- Whether to run a full scene dictionary check or the faster just objExists check (default False)

        """   
	log.debug("Before doName = " + self.mNode)
	log.debug('Name dict: %s"'%self.getNameDict())
        if self.isReferenced():
            log.error("'%s' is referenced. Cannot change name"%self.mNode)
            return False

        if nameChildren:
            NameFactory.doRenameHeir(self.mNode,sceneUnique)
	    self.update()

        else:
            NameFactory.doNameObject(self.mNode,sceneUnique)
	    self.update()
	log.debug("After doName = " + self.mNode)
	
	    
    #=========================================================================                   
    # Attribute Functions
    #=========================================================================                   
    def doStore(self,attr,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        attributes.storeInfo(self.mNode,attr,info,*a,**kw)
	object.__setattr__(self, attr, info)
	#self.update()

    def doRemove(self,attr):
        """ Removes an attr from the maya object instanced. """
        if self.isReferenced():
            return log.warning("'%s' is referenced. Cannot delete attrs"%self.mNode)    	
        try:
            attributes.doDeleteAttr(self.mNode,attr)
        except:
            log.warning("'%s.%s' not found"%(self.mNode,attr))
	    
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
        if self.isReferenced():
            return log.warning("'%s' is referenced. Cannot change name architecture"%self.mNode)   
	
        if tag not in NameFactory.cgmNameTags:
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
             
    def doCopyNameTagsFromObject(self,target,ignore=[False]):
        """
        Get name tags from a target object (connected)
        
        Keywords
        ignore(list) - tags to ignore
        
        Returns
        success(bool)
        """
        assert mc.objExists(target),"Target doesn't exist"
        targetCGM = NameFactory.returnObjectGeneratedNameDict(target,ignore = ignore)
        didSomething = False
        
        for tag in targetCGM.keys():
	    log.info("..."+tag)
            if tag not in ignore and targetCGM[tag] is not None or False:
                attributes.doCopyAttr(target,tag,
                                      self.mNode,connectTargetToSource=False)
                didSomething = True
	#self.update()
        return didSomething
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmObject - sublass to cgmNode
#=========================================================================        
class cgmObject(cgmNode):                  
    def __init__(self,node = None, name = 'null',*args,**kws):
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
        
        if len(mc.ls(self.mNode,type = 'transform',long = True)) == 0:
            log.error("'%s' has no transform"%self.mNode)
            raise StandardError, "The class was designed to work with objects with transforms"
                
    def __bindData__(self):pass
        #self.addAttr('test',2)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #parent
    #==============    
    def getParent(self):
        return search.returnParentObject(self.mNode) or False
		
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
	
		
    parent = property(getParent, doParent)
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
    
    def getAllParents(self):
        return search.returnAllParents(self.mNode) or False
    
    def getChildren(self):
        return search.returnChildrenObjects(self.mNode) or []
    
    def getAllChildren(self):
        return search.returnAllChildrenObjects(self.mNode) or []    
    
    def getShapes(self):
        return mc.listRelatives(self.mNode,shapes=True) or []

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

    def doGroup(self,maintain=False):
        """
        Grouping function for a maya instanced object.

        Keyword arguments:
        maintain(bool) -- whether to parent the maya object in place or not (default False)

        """
        return rigging.groupMeObject(self.mNode,True,maintain)    
                     
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
		    log.info('Found match')
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
            log.info("'%s' is already stored on '%s'"%(info,self.mNode))    
            return
        try:
            mc.sets(info,add = self.mNode)
            log.info("'%s' added to '%s'!"%(info,self.mNode))  	    
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
            ml_resetChannels.resetChannels()        
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
                log.info('Changing to int!')
                typeBuffer = 'int'
            
            if varType is not None:    
                if typeBuffer == requestVarType:
		    log.info("Checks out")
                    return                
                else:
		    log.warning("Converting optionVar type...")
                    self.create(requestVarType)
		    if dataBuffer is not None:
			log.info("Attempting to set with: %s"%dataBuffer)
			self.value = dataBuffer
			log.info("Value : %s"%self.value)
                    return  

    def create(self,doType):
        """ 
        Makes an optionVar.
        """
        log.info( "Creating '%s' as '%s'"%(self.name,doType) )
            
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
                log.info("'%s' added to '%s'"%(value,self.name))
                
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
        log.info("'%s':%s"%(self.name,self.value))
        
        
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
class cgmBuffer(cgmNode):
    def __init__(self,node = None, name = None,nodeType = 'network',*args,**kws):
        """ 
        Intializes an set factory class handler
        
        Keyword arguments:
        setName(string) -- name for the set
        
        """
        ### input check  
	super(cgmBuffer, self).__init__(node = node,name = name,nodeType = nodeType) 
        log.debug("In cgmBuffer.__init__ node is '%s'"%node)
	
        self.bufferList = []
        self.bufferDict = {}	
	
	self.updateData()
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #value
    #==============    
    def getValue(self):
	return self.bufferDict
		
    def setValue(self,value):
	self.purge()#wipe it to reset it
	if type(value) is list or type(value) is tuple:
	    for i in value:
		self.store(i)
	else:
	   self.store(value) 
	    
    value = property(getValue, setValue)#get,set
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def returnNextAvailableCnt(self):
        """ Get's the next available item number """        
        userAttrs = self.getUserAttrsAsDict()
        countList = []
        for key in userAttrs.keys():
            if 'item_' in key:
                splitBuffer = key.split('item_')
                countList.append(int(splitBuffer[-1]))
        cnt = 0
        cntBreak = 0
        while cnt in countList and cntBreak < 500:
            cnt+=1
            cntBreak += 1
        return cnt
        
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def updateData(self,*a,**kw):
        """ Updates the stored data """
        self.bufferList = []
        self.bufferDict = {}
	
        for attr in self.getUserAttrs():
            if 'item_' in attr:
                a = cgmAttr(self.mNode,attr)
                data = a.getMessage()
                if data:
                    self.bufferList.append(data)
                    self.bufferDict[attr] = data
                    
    def rebuild(self,*a,**kw):
        """ Rebuilds the buffer data cleanly """ 
	listCopy = copy.copy(self.bufferList)
	self.value = listCopy
	self.updateData()
                    
    def store(self,info,*a,**kw):
        """ 
        Store information to an object in maya via case specific attribute.
        
        Keyword arguments:
        info(string) -- must be an object in the scene
        
        """
        if not mc.objExists(info):
	    log.warning("'%s' doesn't exist"%info)
	    return
        
        if info in self.bufferList:
            log.info("'%s' is already stored on '%s'"%(info,self.mNode))    
            return
        
        cnt = self.returnNextAvailableCnt()    
        attributes.storeInfo(self.mNode,('item_'+str(cnt)),info,*a,**kw)
        self.bufferList.append(info)
        self.bufferDict['item_'+str(cnt)] = info
        
    def doStoreSelected(self): 
        """ Store elected objects """
        # First look for attributes in the channel box
        channelBoxCheck = search.returnSelectedAttributesFromChannelBox()
        if channelBoxCheck:
            for item in channelBoxCheck:
                self.store(item)
            return
        
        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.store(item)
            except:
                log.warning("Couldn't store '%s'"%(item))     
        
    def remove(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        if info not in self.bufferList:
            guiFactory.warning("'%s' isn't already stored '%s'"%(info,self.mNode))    
            return
        
        for key in self.bufferDict.keys():
            if self.bufferDict.get(key) == info:
                attributes.doDeleteAttr(self.mNode,key)
                self.bufferList.remove(info)
                self.bufferDict.pop(key)
                
        log.warning("'%s' removed!"%(info))  
                
        self.updateData()
        
    def doRemoveSelected(self): 
        """ Store elected objects """
        # First look for attributes in the channel box
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
        
        userAttrs = mc.listAttr(self.mNode,userDefined = True) or []
        for attr in userAttrs:
            if 'item_' in attr:
                attributes.doDeleteAttr(self.mNode,attr)
                log.warning("Deleted: '%s.%s'"%(self.mNode,attr))  
                
        self.bufferList = []
        self.bufferDict = {}        
         
    def select(self):
        """ 
        Select the buffered objects. Need to work out nested searching better
        only goes through two nexts now
        """        
        if self.bufferList:
            selectList = []
            # Need to dig down through the items
            for item in self.bufferList:
                if search.returnTagInfo(item,'cgmType') == 'objectBuffer':
                    tmpFactory = cgmBuffer(item)
                    selectList.extend(tmpFactory.bufferList)
                    
                    for item in tmpFactory.bufferList:
                        if search.returnTagInfo(item,'cgmType') == 'objectBuffer':
                            subTmpFactory = cgmBuffer(item)   
                            selectList.extend(subTmpFactory.bufferList)
                            
                else:
                    selectList.append(item)
                    
            mc.select(selectList)
            return
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
    
    def key(self,*a,**kw):
        """ Select the buffered objects """        
        if self.bufferList:
            mc.select(self.bufferList)
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
    
    def __init__(self,objName,attrName,attrType = False,value = None,enum = False,initialValue = None,lock = None,keyable = None, hidden = None, *a, **kw):
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
        try:
            #If we have an Object Factory instance, link it
            objName.mNode
            self.obj = objName
        except:
            #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
            assert mc.objExists(objName) is True, "'%s' doesn't exist" %objName
            self.obj = cgmNode(objName)
	    
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
		log.info("'%s' exists. creating as message."%value)
		self.attrType = 'message'		
	    else:
		dataReturn = search.returnDataType(value)
		log.info("Trying to create attr of type '%s'"%dataReturn)
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
                
            except:
                log.error("'%s.%s' failed to add"%(self.obj.mNode,attrName))
                     
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
		log.info("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
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
    
    #>>> Property - p_nameLong ================== 
    def getEnum(self):
	return mc.attributeQuery(self.attr, node = self.obj.mNode, longName = True) or False	
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
                log.info("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
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
	return mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, hidden=True)
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
                    if not cInstance.hidden:
                        if cInstance.keyable:
                            cInstance.doKeyable(False)
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,channelBox = False) 
                        log.info("'%s.%s' hidden!"%(cInstance.obj.mNode,cInstance.attr))
                
            elif not self.p_hidden:
                if self.p_keyable:
                    self.doKeyable(False)
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,channelBox = False) 
                log.info("'%s.%s' hidden!"%(self.obj.mNode,self.attr))
   
        else:
            if self.getChildren():
                log.warning("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if cInstance.hidden:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,channelBox = True) 
                        log.info("'%s.%s' unhidden!"%(cInstance.obj.mNode,cInstance.attr))
                
            elif self.p_hidden:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,channelBox = True)           
                log.info("'%s.%s' unhidden!"%(self.obj.mNode,self.attr))
		
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
	KeyableTypes = ['long','float','bool','enum','double3']  
        assert type(arg) is bool, "doKeyable arg must be a bool!" 
	
	if self.attrType not in KeyableTypes:
	    log.warning("'%s' not a keyable attrType"%self.attrType)
	    return False
	
        if arg:
            if self.getChildren():
                log.warning("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if not cInstance.keyable:
                        mc.setAttr(cInstance.nameCombined,e=True,keyable = True) 
                        log.info("'%s.%s' keyable!"%(cInstance.obj.mNode,cInstance.attr))
                        cInstance.p_hidden = False
                
            elif not self.p_keyable:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,keyable = True) 
                log.info("'%s.%s' keyable!"%(self.obj.mNode,self.attr))
                self.p_hidden = False
                    
                
        else:
            if self.getChildren():
                log.warning("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                for c in self.getChildren():
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
                    if cInstance.keyable:
                        mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,keyable = False) 
                        log.info("'%s.%s' unkeyable!"%(cInstance.obj.mNode,cInstance.attr))
                        if not mc.getAttr(cInstance.nameCombined,channelBox=True):
                            cInstance.doHidden(False)                
                
            elif self.p_keyable:
                mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,keyable = False)           
                log.info("'%s.%s' unkeyable!"%(self.obj.mNode,self.attr))
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
                else:
                    log.info("'%s.%s' already has that alias!"%(self.obj.mNode,self.attr,arg))
                    
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
                log.error("'%s.%s' failed to set nice name of '%s'!"%(self.obj.mNode,self.attr,arg))
                    
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
	    log.warn("'%s' is not a numberic attribute"%self.p_combinedName)
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
	    log.warn("'%s' is not a numberic attribute"%self.p_combinedName)
	    return False

	minValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, minimum=True)
	try:
	    if minValue is not False:
		return minValue[0]
	    return False
	except:
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
	    log.warn("'%s' is not a numberic attribute"%self.p_combinedName)	    
	    return False
		    
    p_minValue = property (getMinValue,doMin)
    
    #>>> Property - p_softMin ==================  
    def getSoftMin(self):
	if not self.isNumeric():
	    log.warn("'%s' is not a numberic attribute"%self.p_combinedName)
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
		log.warn("'%s' is not a numberic attribute"%self.p_combinedName)	    
		return False
    p_softMin = property (getSoftMin,doSoftMin)
    
    #>>> Property - p_softMax ==================  
    def getSoftMax(self):
	if not self.isNumeric():
	    log.warn("'%s' is not a numberic attribute"%self.p_combinedName)
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
		log.warn("'%s' is not a numberic attribute"%self.p_combinedName)	    
		return False
    p_softMax = property (getSoftMax,doSoftMax)
    
    #>>> Property - p_maxValue ==================         
    def getMaxValue(self):
	if not self.isNumeric():
	    log.warn("'%s' is not a numberic attribute"%self.p_combinedName)
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
	    log.error("'%s' is not a numberic attribute"%self.p_combinedName)	    
	    return False
		    
    p_maxValue = property (getMaxValue,doMax)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Queries ==================  
    def isDynamic(self):
	if self.attr in mc.listAttr(self.obj.mNode, userDefined = True):
	    return True
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

            log.info("'%s.%s' >Message> '%s'"%(self.obj.mNode,self.attr,self.value))
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
        
	guiFactory.doPrintReportStart(functionName)
	log.info("AttrFactory instance: '%s'"%self.p_combinedName)
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
        assert self.obj.transform is not False,"'%s' Doesn't have a transform. Transferring this attribute is probably a bad idea. Might we suggest doCopyTo along with a connect to source option"%self.obj.mNode        
        assert mc.ls(target,long=True) != [self.obj.mNode], "Can't transfer to self!"
        assert '.' not in list(target),"'%s' appears to be an attribute. Can't transfer to an attribute."%target
        assert self.isDynamic() is True,"'%s' is not a dynamic attribute."%self.p_combinedName
        
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
	
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in
#r9Meta.registerMClassNodeMapping(nodeTypes = ['network','transform','objectSet'])#What node types to look for
