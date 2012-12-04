import maya.cmds as mc
import maya.mel as mel
from cgm.lib.classes import NameFactory

from cgm.lib import (lists,
                     search,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)

#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
from cgm.lib.Red9.core import Red9_Meta as r9Meta
reload(r9Meta)
from cgm.lib.Red9.core.Red9_Meta import *

r9Meta.registerMClassInheritanceMapping()    
print '============================================='  
r9Meta.printSubClassRegistry()  
print '============================================='  
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

class cgmMetaClass(MetaClass):#Should we do this?
    def __init__(self,*args,**kws):
        """ 
        Utilizing Red 9's MetaClass. Intialized a node in cgm's system.
        """
        MetaClass.__init__(self, *args,**kws)
        
        self.update(self.mNode)
         
                    
    #=========================================================================      
    # Get Info
    #========================================================================= 
    def update(self,obj):
        """ Update the instance with current maya info. For example, if another function outside the class has changed it. """ 
        assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
        MetaClass.__init__(self, node=obj) #Is this a good idea?
        
        self.getRefState()

    def getRefState(self):
        """
        Get ref state of the object
        """	
        if mc.referenceQuery(self.mNode, isNodeReferenced=True):
            self.refState = True
            self.refPrefix = search.returnReferencePrefix(self.mNode)
            return [self.refState,self.refPrefix]
        self.refState = False
        self.refPrefix = None
        return {'referenced':self.refState,'prefix':self.refPrefix}
    
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

    def getMayaType(self):
        """ get the type of the object """
        return search.returnObjectType(self.mNode)
    
    def doName(self,sceneUnique=False,nameChildren=False):
        """
        Function for naming a maya instanced object using the cgm.NameFactory class.

        Keyword arguments:
        sceneUnique(bool) -- Whether to run a full scene dictionary check or the faster just objExists check (default False)

        """       
        if self.refState:
            log.error("'%s' is referenced. Cannot change name"%self.mNode)
            return

        if nameChildren:
            buffer = NameFactory.doRenameHeir(self.mNode,sceneUnique)
            if buffer:
                self.update(buffer[0])

        else:
            buffer = NameFactory.doNameObject(self.mNode,sceneUnique)
            if buffer:
                self.update(buffer) 
    #=========================================================================                   
    # Attribute Functions
    #=========================================================================                   
    def doStore(self,attr,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        attributes.storeInfo(self.mNode,attr,info,*a,**kw)

    def doRemove(self,attr):
        """ Removes an attr from the maya object instanced. """
        if self.refState:
            return guiFactory.warning("'%s' is referenced. Cannot delete attrs"%self.mNode)    	
        try:
            attributes.doDeleteAttr(self.mNode,attr)
        except:
            guiFactory.warning("'%s.%s' not found"%(self.mNode,attr))
            
            
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
    

class cgmObject(cgmMetaClass):
    def __init__(self,obj='', autoCreate = True):
        """ 
        Utilizing Red 9's MetaClass. Intialized a object in cgm's system. If no object is passed it 
        creates an empty transform

        Keyword arguments:
        obj(string)        
        autoCreate(bool) - whether to create a transforum if need be
        """
        ### input check

        if not mc.objExists(obj):
            if autoCreate:#If the object doesn't exist, create a transform
                buffer = mc.group(empty=True)
                if len(list(obj)) < 1:
                    obj = buffer            
                obj = mc.rename(buffer,obj)
                log.info("'%s' created as a null." %obj)
            else:#Fails
                log.error("No object specified and no auto create option set")
            
        cgmMetaClass.__init__(self, node=obj) 
        
        if len(mc.ls(self.mNode,type = 'transform',long = True)) == 0:
            log.error("'%s' has no transform"%self.mNode)  
        self.update(self.mNode)#Get intial info
        
    #=========================================================================      
    # Get Info
    #=========================================================================                   
    def update(self,obj):
        """ Update the instance with current maya info. For example, if another function outside the class has changed it. """ 
        assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
        cgmMetaClass.update(self,obj=obj)
        
        try:
            self.getFamily()
            self.transformAttrs = []
            for attr in 'translate','translateX','translateY','translateZ','rotate','rotateX','rotateY','rotateZ','scaleX','scale','scaleY','scaleZ','visibility','rotateOrder':
                if mc.objExists(self.nameLong+'.'+attr):
                    self.transformAttrs.append(attr)
            return True
        except:
            log.debug("Failed to update '%s'"%self.mNode)
            return False
        
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
        assert self.transform ,"'%s' has no transform"%obj	
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
        if parent: #if we have a target parent
            try:
                #If we have an Object Factory instance, link it
                parent = parent.mNode
                log.debug("Parent is an instance")
            except:
                #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
                assert mc.objExists(parent) is True, "'%s' - parent object doesn't exist" %parent    
            
            log.info("Parent is '%s'"%parent)
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
                    if a in drawingOverrideAttrsDict:
                        try:
                            attributes.doSetAttr(t,a,attrs[a])
                        except:
                            raise AttributeError, "There was a problem setting '%s.%s' to %s"%(self.mNode,a,drawingOverrideAttrsDict[a])
                    else:
                        guiFactory.warning("'%s.%s' doesn't exist"%(t,a))
                        
            if type(attrs) is list:
                for a in attrs:
                    if a in drawingOverrideAttrsDict:
                        try:
                            attributes.doSetAttr(self.mNode,a,drawingOverrideAttrsDict[a])
                        except:
                            raise AttributeError, "There was a problem setting '%s.%s' to %s"%(self.mNode,a,drawingOverrideAttrsDict[a])
                    else:
                        guiFactory.warning("'%s.%s' doesn't exist"%(t,a))       
                        
                            
