import maya.cmds as mc
import maya.mel as mel
from cgm.lib.classes import NameFactory

from cgm.lib.ml import (ml_resetChannels)
reload(ml_resetChannels)

import copy

from cgm.lib import (lists,
                     search,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)

reload(attributes)

#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
from Red9.core import Red9_Meta as r9Meta
reload(r9Meta)
from Red9.core.Red9_Meta import *

r9Meta.registerMClassInheritanceMapping()    
#=========================================================================

#Mark, any thoughts on where to store important defaults
drawingOverrideAttrsDict = {'overrideEnabled':0,
                            'overrideDisplayType':0,
                            'overrideLevelOfDetail':0,
                            'overrideShading':1,
                            'overrideTexturing':1,
                            'overridePlayback':1,
                            'overrideVisibility':1}

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmMeta - MetaClass factory for figuring out what to do with what's passed to it
#=========================================================================    
class testClass(MetaClass):
    def __bindData__(self):              
        self.addAttr('testing',2.0)
        self.addAttr('testString','asdf')

    def __init__(self,*args,**kws):
        super(testClass, self).__init__(*args,**kws)

                    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmMeta - MetaClass factory for figuring out what to do with what's passed to it
#=========================================================================    
class cgmMeta(object):
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
        if mc.ls(node,type='transform'):
            log.info("'%s' Appears to be a transform, initializing as cgmObject"%node)
            return cgmObject(name = name, node = node)          
        else:
            log.info("Appears to be a '%s'. Initializing as cgmNode"%objectType)  
            return cgmNode(name = name, node = node)    
          
        return False
            
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmNode - subclass to Red9.MetaClass
#=========================================================================    
class cgmNode(MetaClass):#Should we do this?    
    def __init__(self,node = None, name = None,nodeType = 'network',*args,**kws):
        """ 
        Utilizing Red 9's MetaClass. Intialized a node in cgm's system.
        """
        log.debug("In cgmNode.__init__ Node is '%s'"%node)
        log.debug("In cgmNode.__init__ Name is '%s'"%name) 
	
	if node == None:
	    catch = cgmMeta(nodeType = nodeType)
	    node = catch.mNode	
	    
        super(cgmNode, self).__init__(node=node, name = name, nodeType = nodeType)
	self.UNMANAGED.extend(['referencePrefix'])
	self.__dict__['__name__'] = self.mNode
            
    def __setattr__(self, attr, value):
        #Overloading until the functionality is what we need. For now, just handling locking
	attrBuffer = '%s.%s'%(self.mNode,attr)
	#Lock handling
	wasLocked = False
	if (mc.objExists(attrBuffer)) == True:
	    attrType = mc.getAttr(attrBuffer,type=True)
	    if mc.getAttr(attrBuffer,lock=True) == True:
		wasLocked = True
                mc.setAttr(attrBuffer,lock=False)
		
	MetaClass.__setattr__(self,attr,value)
	
	if wasLocked == True:
	    mc.setAttr(attrBuffer,lock=True)

    def addAttr(self, attr,value = None, attrType = False,enum = False,initialValue = None,lock = None,keyable = None, hidden = None,**kws):
        if attr not in self.UNMANAGED and not attr=='UNMANAGED':
	    if self.hasAttr(attr):#Quick create check for initial value
		initialCreate = False
	    else:
		initialCreate = True
		
	    #If type is double3, handle with out own setup as Red's doesn't have it
	    #==============    
	    #if attributes.validateRequestedAttrType(attrType) == 'double3':
		#cgmAttr(self.mNode, attrName = attr, value = value, attrType = attrType, enum = enum, initialValue = initialValue, lock=lock,keyable=keyable,hidden = hidden)
		#object.__setattr__(self, attr, value)		
	    MetaClass.addAttr(self,attr,value)		

	    if initialValue is not None and initialCreate:
		self.__setattr__(attr,initialValue)
		
	    #Easy carry for flag handling - until implemented
	    #==============  
	    cgmAttr(self.mNode, attrName = attr, attrType = attrType, lock=lock,keyable=keyable,hidden = hidden)
		
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
    def update(self,obj):
        """ Update the instance with current maya info. For example, if another function outside the class has changed it. """ 
        assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
        super(cgmNode, self).__init__(node = obj) #Forces a reinitialization        
        	
    def getCGMNameTags(self):
        """
        Get the cgm name tags of an object.
        """
        self.cgm = {}
        for tag in NameFactory.cgmNameTags:
            self.cgm[tag] = search.findRawTagInfo(self.mNode,tag)
        return self.cgm    
        
    def getAttrs(self):
        """ Stores the dictionary of userAttrs of an object."""
        self.userAttrsDict = attributes.returnUserAttrsToDict(self.mNode) or {}
        self.userAttrs = mc.listAttr(self.mNode, userDefined = True) or []
        self.attrs = mc.listAttr(self.mNode) or []
        self.keyableAttrs = mc.listAttr(self.mNode, keyable = True) or []

        self.transformAttrs = []
        for attr in 'translate','translateX','translateY','translateZ','rotate','rotateX','rotateY','rotateZ','scaleX','scale','scaleY','scaleZ','visibility','rotateOrder':
            if mc.objExists(self.mNode+'.'+attr):
                self.transformAttrs.append(attr)
		
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
    
    def doName(self,sceneUnique=False,nameChildren=False):
        """
        Function for naming a maya instanced object using the cgm.NameFactory class.

        Keyword arguments:
        sceneUnique(bool) -- Whether to run a full scene dictionary check or the faster just objExists check (default False)

        """       
        if self.isReferenced():
            log.error("'%s' is referenced. Cannot change name"%self.mNode)
            return

        if nameChildren:
            NameFactory.doRenameHeir(self.mNode,sceneUnique)
	    self.update(self.mNode)

        else:
            NameFactory.doNameObject(self.mNode,sceneUnique)
	    self.update(self.mNode)
	    
    #=========================================================================                   
    # Attribute Functions
    #=========================================================================                   
    def doStore(self,attr,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        attributes.storeInfo(self.mNode,attr,info,*a,**kw)

    def doRemove(self,attr):
        """ Removes an attr from the maya object instanced. """
        if self.isReferenced():
            return log.warning("'%s' is referenced. Cannot delete attrs"%self.mNode)    	
        try:
            attributes.doDeleteAttr(self.mNode,attr)
        except:
            log.warning("'%s.%s' not found"%(self.mNode,attr))
             
    def copyNameTagsFromObject(self,target,ignore=[False]):
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
            if tag not in ignore and targetCGM[tag] is not None or False:
                attributes.doCopyAttr(target,tag,
                                      self.mNode,connectTargetToSource=True)
                didSomething = True
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
	if node == None:
	    catch = cgmMeta(name = name, nodeType = 'transform')
	    node = catch.mNode

        super(cgmObject, self).__init__(node=node, name = name)
        
        if len(mc.ls(self.mNode,type = 'transform',long = True)) == 0:
            log.error("'%s' has no transform"%self.mNode)
            raise StandardError, "The class was designed to work with objects with transforms"
                
    def __bindData__(self):pass
        #self.addAttr('test',2)
    #=========================================================================      
    # Get Info
    #========================================================================= 
    def getTransformAttrs(self):
	self.transformAttrs = []
	for attr in 'translate','translateX','translateY','translateZ','rotate','rotateX','rotateY','rotateZ','scaleX','scale','scaleY','scaleZ','visibility','rotateOrder':
	    if mc.objExists(self.mNode+'.'+attr):
		self.transformAttrs.append(attr)
	return self.transformAttrs
    
    def getFamily(self):
        """ Get the parent, child and shapes of the object."""
        self.parent = self.getParent()
        self.children = self.getChildren()
        self.shapes = self.getShapes()
        return {'parent':self.parent,'children':self.children,'shapes':self.shapes}
        
    def getParent(self):
        return search.returnParentObject(self.mNode) or False
    
    def getChildren(self):
        return search.returnChildrenObjects(self.mNode) or []
    
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
    def copyRotateOrder(self,targetObject):
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

    def copyPivot(self,sourceObject):
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
        assert mc.ls(self.mNode,type='transform'),"'%s' has no transform"%self.mNode	
        rigging.groupMeObject(self.mNode,True,maintain)    

    def doParent(self,parent = False):
        """
        Function for parenting a maya instanced object while maintaining a correct object instance.

        Keyword arguments:
        parent(string) -- Target parent
        """
        if parent == self.parent:
            return True
        
        if parent: #if we have a target parent
            try:
                #If we have an Object Factory instance, link it
                parent = parent.mNode
                log.debug("Parent is an instance")
            except:
                #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
                assert mc.objExists(parent) is True, "'%s' - parent object doesn't exist" %parent    
            
            log.debug("Parent is '%s'"%parent)
            try:
                mc.parent(self.mNode,parent)
            except:
                log.debug("'%s' already has target as parent"%self.mNode)
                return False
            
        else:#If not, do so to world
            rigging.doParentToWorld(self.mNode)
            log.debug("'%s' parented to world"%self.mNode)                        
            
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
# cgmAttr - separate class
#=========================================================================    
class cgmAttr(object):
    """ 
    Initializes a maya attribute as a class obj
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
        try:
            #If we have an Object Factory instance, link it
            objName.mNode
            self.obj = objName
        except:
            #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
            assert mc.objExists(objName) is True, "'%s' doesn't exist" %objName
            catch = cgmNode(objName)
            self.obj = catch
        
        self.form = attributes.validateRequestedAttrType(attrType)
        self.attr = attrName
        self.children = False
        initialCreate = False
        
        # If it exists we need to check the type. 
        if mc.objExists('%s.%s'%(self.obj.mNode,attrName)):
            log.debug("'%s.%s' exists"%(self.obj.mNode,attrName))
            currentType = mc.getAttr('%s.%s'%(self.obj.mNode,attrName),type=True)
            log.debug("Current type is '%s'"%currentType)
            if not attributes.validateAttrTypeMatch(attrType,currentType) and self.form is not False:
                if self.obj.isReferenced():
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
                  
    def __call__(self):
        return self.get()
    
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
        self.enumCommand = False
        
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
            self.enumCommand = standardFlagsBuffer.get('enum')
                
    
    def doConvert(self,attrType):
        """ 
        Converts an attribute type from one to another while preserving as much data as possible.
        
        Keyword arguments:
        attrType(string)        
        """
        self.updateData()
        if self.obj.isReferenced():
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
                        cInstance = cgmAttr(self.obj.mNode,c)                        
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
                if value != self.value:
                    self.doStore(value)
            elif value != self.value:
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
                if self.enumCommand != enumCommand:
                    mc.addAttr ((self.obj.mNode+'.'+self.attr), e = True, at=  'enum', en = enumCommand)
                    self.enumCommand = enumCommand
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

        if self.form == 'message':
            self.obj.doStore(self.attr,infoToStore)
            self.value = infoToStore
        elif convertIfNecessary:
            self.doConvert('message')
            self.updateData()
            self.obj.doStore(self.attr,infoToStore)                
            self.value = infoToStore
            
        #except:
          #  log.error("'%s.%s' failed to store '%s'"%(self.obj.mNode,self.attr,infoToStore))
            
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
                        cInstance = cgmAttr(self.obj.mNode,c)                        
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
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
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
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
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
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
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
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
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
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
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
                    cInstance = cgmAttr(self.obj.mNode,c)                                            
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
    def __init__(self,setName = None,setType = False,qssState = None,**kws):
        """ 
        Intializes an set factory class handler
        
        Keyword arguments:
        setName(string) -- name for the set
        
        """
        ### input check  
	if setName is not None and mc.objExists(setName):
	    assert search.returnObjectType(setName) == 'objectSet',"Not an object set"    
	    super(cgmObjectSet, self).__init__(node = setName)  
	else:
	    super(cgmObjectSet, self).__init__(node = setName,nodeType = 'objectSet')
	    
        log.debug("In cgmObjectSet.__init__ setName is '%s'"%setName)
        log.debug("In cgmObjectSet.__init__ setType is '%s'"%setType) 
        log.debug("In cgmObjectSet.__init__ qssState is '%s'"%qssState) 
	
	self.UNMANAGED.extend(['objectSetType','qssState','mayaSetState'])
	
	#Maya Set?
	#==============
	self.mayaSetState = False
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
	    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #Qss
    #==============    
    def isQss(self):
	if mc.sets(self.mNode,q=True,text=True)== 'gCharacterSet':
	    self.qssState = True
	    return True
	else:
	    self.qssState = False
	    return False
		
    def makeQss(self,arg):
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
    def isSetType(self):
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
        """ Set a set's type """
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

    objectSetType = property(isSetType, doSetType)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def setList(self):
	return mc.sets(self.mNode, q = True) or []
    
    def doesContain(self,obj):
	assert mc.objExists(obj),"'%s' doesn't exist"%obj
        buffer = mc.ls(obj,shortNames=True)        
        
	for o in self.setList():
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
        assert mc.objExists(info) is True, "'%s' doesn't exist"%info
        if info == self.mNode:
            return False
        
        if info in self.setList():
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
        if self.setList():
            mc.select(self.setList())
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
        if self.setList():
            mc.select(self.setList())
            mc.setKeyframe(*a,**kw)
            return True
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
    
    def reset(self,*a,**kw):
        """ Reset the set objects """        
        if self.setList():
            mc.select(self.setList())
            ml_resetChannels.resetChannels()        
            return True
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False
    
    def deleteKey(self,*a,**kw):
        """ Select the seted objects """        
        if self.setList():
            mc.select(self.setList())
            mc.cutKey(*a,**kw)
            return True
        
        log.warning("'%s' has no data"%(self.mNode))  
        return False   
    
    def deleteCurrentKey(self,*a,**kw):
        """ Select the seted objects """        
        if self.setList():
            mc.select(self.setList())
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
                self.initialStore(value)
		
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
		
class cgmOptionVar2(object):
    """ 
    OptionVar Class handler
    
    """
    def __init__(self,varName,varType = None,value = None, defaultValue = None):
        """ 
        Intializes an optionVar class handler
        
        Keyword arguments:
        varName(string) -- name for the optionVar
        varType(string) -- 'int','float','string' (default 'int')
        value() -- will attempt to set the optionVar with the value
        defaultValue() -- will ONLY use if the optionVar doesn't exist
        
        """
        #Default to creation of a var as an int value of 0
        ### input check   
        self.name = varName
        self.form = ''
        self.value = ''
        
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
                self.form = requestVarType
                self.create(self.form)
                if defaultValue is not None:
                    self.initialStore(defaultValue)
                elif value is not None:
                    self.initialStore(value)
                    
                self.value = mc.optionVar(q=self.name)
                
            else:
                guiFactory.warning("'%s' is not a valid variable type"%varType)
            
        else:               
            self.update(varType)
            
            #Attempt to set a value on call
            if value is not None:           
                self.initialStore(value)
            
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
                    self.set(value)
                        
    def returnVarTypeFromCall(self, varTypeCheck):    
        for option in optionVarTypeDict.keys():
            if varTypeCheck in optionVarTypeDict.get(option):
                return option
        return 'int'
    
    def update(self,varType = None):
        """ 
        Update the data in case some other process has changed on optionVar
        """
        dataBuffer = mc.optionVar(q=self.name)   
        
        requestVarType = self.returnVarTypeFromCall(varType)
        
        if not mc.optionVar(exists = self.name):
            if requestVarType:
                self.form = requestVarType
                self.create(self.form)
                self.value = mc.optionVar(q=self.name)
                return
            else:
                return guiFactory.warning("'%s' is not a valid variable type"%varType)  
        
        else:
            #If it exists, first check for data buffer
            typeBuffer = search.returnDataType(dataBuffer) or False
            if not typeBuffer:
                print'changing to int!'
                typeBuffer = 'int'
            
            if varType is not None:    
                if typeBuffer == requestVarType:
                    self.form = typeBuffer
                    self.value = dataBuffer
                    return                
                else:
                    self.form = requestVarType
                    self.create(self.form)
                    self.value = mc.optionVar(q=self.name)
                    return  
            else:
                self.form = typeBuffer
                self.value = mc.optionVar(q=self.name)
                return                  
            

    def create(self,doType):
        """ 
        Makes an optionVar.
        """
        print "Creating '%s' as '%s'"%(self.name,self.form)
            
        if doType == 'int':
            mc.optionVar(iv=(self.name,0))
        elif doType == 'float':
            mc.optionVar(fv=(self.name,0))
        elif doType == 'string':
            mc.optionVar(sv=(self.name,''))

  
    def purge(self):
        """ 
        Purge an optionVar from maya
        """
        try:
            mc.optionVar(remove = self.name)
            self.name = ''
            self.form = ''
            self.value = ''
            
        except:
            guiFactory.warning("'%s' doesn't exist"%(self.name))
            
    def clear(self):
        """
        Clear the data from an option var
        """
        doName = self.name
        doType = self.form
        self.purge()
        self.__init__(doName,doType)
            
            
    def set(self,value):
        if self.form == 'int':
            try:
                mc.optionVar(iv = (self.name,value))
                self.value = value
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'float':
            try:
                mc.optionVar(fv = (self.name,value))
                self.value = value
                
            except:
                guiFactory.report("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'string':
            try:
                mc.optionVar(sv = (self.name,str(value)))
                self.value = value
                
            except:
                guiFactory.report("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
    def append(self,value): 
        if type(self.value) is list:
            if value in self.value:
                return guiFactory.warning("'%s' already added"%(value))

        if self.form == 'int':
            try:
                mc.optionVar(iva = (self.name,int(value)))
                self.update(self.form)
                guiFactory.report("'%s' added to '%s'"%(value,self.name))
                
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'float':
            try:
                mc.optionVar(fva = (self.name,value))
                self.update(self.form)
                guiFactory.report("'%s' added to '%s'"%(value,self.name))
                
            except:
                guiFactory.report("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'string':
            try:
                mc.optionVar(sva = (self.name,str(value)))
                for i in "",'':
                    if i in self.value:
                        self.remove(i)

                self.update(self.form)
                guiFactory.report("'%s' added to '%s'"%(value,self.name))
                             
                
            except:
                guiFactory.report("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))

            

    def remove(self,value):
        if value in self.value:
            try:         
                i = self.value.index(value)
                mc.optionVar(removeFromArray = (self.name,i))
                self.update(self.form)
                guiFactory.report("'%s' removed from '%s'"%(value,self.name))
            except:
                guiFactory.report("'%s' failed to remove '%s'"%(value,self.name))
        else:
            guiFactory.report("'%s' wasn't found in '%s'"%(value,self.name))
            

                            
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
        assert self.form == 'int',"'%s' not an int type var"%(self.name)
        
        mc.optionVar(iv = (self.name,not self.value))
        self.value = not self.value
        guiFactory.report("'%s':%s"%(self.name,self.value))
        
        
        
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
            guiFactory.warning("'%s' is empty!"%self.name)
            
            
    def existCheck(self):
        """
        Attempts to select the items of a optionVar buffer
        """
        bufferList = self.value
        existsList = []
        if bufferList:
            for item in bufferList:
                if mc.objExists(item):
                        existsList.append(item)
                        
        mc.optionVar(clearArray = self.name)
        if existsList:
            existsList = lists.returnListNoDuplicates(existsList)
            self.extend(existsList)
                
                        
                        
        

    
