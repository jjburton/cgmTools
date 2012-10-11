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
from cgm.lib.classes import NameFactory

from cgm.lib import (lists,
                     search,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)

drawingOverrideAttrsDict = {'overrideEnabled':0,
                            'overrideDisplayType':0,
                            'overrideLevelOfDetail':0,
                            'overrideShading':1,
                            'overrideTexturing':1,
                            'overridePlayback':1,
                            'overrideVisibility':1}
class ObjectFactory():
    """ 
    Initialized a maya object as a class obj
    """
    def __init__(self,obj=''):
        """ 
        Asserts objects existance and that it has a transform. Then initializes. 

        Keyword arguments:
        obj(string)        

        """
        ### input check
        if not mc.objExists(obj):
            buffer = mc.group(empty=True)
            if len(list(obj)) < 1:
                obj = buffer
            obj = mc.rename(buffer,obj)
            guiFactory.warning("'%s' created as a null." %obj)

        self.parent = False
        self.children = False
        self.refState = False
        self.cgm = {}
        self.mType = ''
        self.transform = False

        self.update(obj)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def isRef(self):
        """
        Get ref state of the object
        """	
        if mc.referenceQuery(self.nameLong, isNodeReferenced=True):
            self.refState = True
            self.refPrefix = search.returnReferencePrefix(self.nameShort)
            return
        self.refState = False
        self.refPrefix = None

    def getCGMNameTags(self):
        """
        Get the cgm name tags of an object.
        """
        self.cgm = {}
        for tag in NameFactory.cgmNameTags:
            self.cgm[tag] = search.findRawTagInfo(self.nameLong,tag)
            
    def getNameTagsFromObject(self,target,ignore=[False]):
        """
        Get name tags from a target object (connected)
        
        Keywords
        ignore(list) - tags to ignore
        
        Returns
        success(bool)
        """
        targetCGM = NameFactory.returnObjectGeneratedNameDict(target,ignore = ignore)
        didSomething = False
        
        for tag in targetCGM.keys():
            if tag not in ignore and targetCGM[tag] is not None or False:
                attributes.doCopyAttr(target,tag,
                                      self.nameLong,connectTargetToSource=True)
                didSomething = True
        return didSomething

    def getAttrs(self):
        """ Stores the dictionary of userAttrs of an object."""
        self.userAttrsDict = attributes.returnUserAttrsToDict(self.nameLong) or {}
        self.userAttrs = mc.listAttr(self.nameLong, userDefined = True) or []
        self.attrs = mc.listAttr(self.nameLong) or []
        self.keyableAttrs = mc.listAttr(self.nameLong, keyable = True) or []

        self.transformAttrs = []
        for attr in 'translate','translateX','translateY','translateZ','rotate','rotateX','rotateY','rotateZ','scaleX','scale','scaleY','scaleZ','visibility','rotateOrder':
            if mc.objExists(self.nameLong+'.'+attr):
                self.transformAttrs.append(attr)

    def getType(self):
        """ get the type of the object """
        self.mType = search.returnObjectType(self.nameLong)

    def getFamily(self):
        """ Get the parent, child and shapes of the object."""
        self.parent = search.returnParentObject(self.nameLong) or False
        self.children = search.returnChildrenObjects(self.nameLong) or []
        self.shapes = mc.listRelatives(self.nameLong,shapes=True) or []

    def getTransforms(self):
        """ Get transform information of the object. """
        self.rotateOrder = mc.getAttr(self.nameLong + '.rotateOrder')

    def getMatchObject(self):
        """ Get match object of the object. """
        matchObject = search.returnTagInfo(self.nameLong,'cgmMatchObject')

        if mc.objExists(matchObject):
            return matchObject
        return False

    def storeNameStrings(self,obj):
        """ Store the base, short and long names of an object to instance."""
        buffer = mc.ls(obj,long=True)
        self.nameLong = buffer[0]
        buffer = mc.ls(obj,shortNames=True)        
        self.nameShort = buffer[0]
        if '|' in buffer[0]:
            splitBuffer = buffer[0].split('|')
            self.nameBase = splitBuffer[-1]
            return
        self.nameBase = self.nameShort

    def update(self,obj):
        """ Update the instance with current maya info. For example, if another function outside the class has changed it. """ 
        assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj

        try:
            self.transform = mc.ls(obj,type = 'transform',long = True) or False
            self.storeNameStrings(obj) 
            self.getType()
            self.getFamily()
            self.getCGMNameTags()
            #self.getAttrs() 
            self.isRef()

            self.transformAttrs = []
            for attr in 'translate','translateX','translateY','translateZ','rotate','rotateX','rotateY','rotateZ','scaleX','scale','scaleY','scaleZ','visibility','rotateOrder':
                if mc.objExists(self.nameLong+'.'+attr):
                    self.transformAttrs.append(attr)

            return True
        except:
            return False

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Attribute Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        
    def store(self,attr,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        attributes.storeInfo(self.nameLong,attr,info,*a,**kw)

    def remove(self,attr):
        """ Removes an attr from the maya object instanced. """
        if self.refState:
            return guiFactory.warning("'%s' is referenced. Cannot delete attrs"%self.nameShort)    	
        try:
            attributes.doDeleteAttr(self.nameLong,attr)
        except:
            guiFactory.warning("'%s.%s' not found"%(self.nameLong,attr))


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Rigging Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    def copyRotateOrder(self,targetObject):
        """ 
        Copy the rotate order from a target object to the current instanced maya object.
        """
        try:
            #If we have an Object Factory instance, link it
            targetObject.nameShort
            targetObject = targetObject.nameShort
        except:	
            assert mc.objExists(targetObject) is True, "'%s' - target object doesn't exist" %targetObject    
        assert self.transform ,"'%s' has no transform"%obj	
        assert mc.ls(targetObject,type = 'transform'),"'%s' has no transform"%targetObject
        buffer = mc.getAttr(targetObject + '.rotateOrder')
        attributes.doSetAttr(self.nameLong, 'rotateOrder',buffer) 

    def copyPivot(self,sourceObject):
        """ Copy the pivot from a source object to the current instanced maya object. """
        try:
            #If we have an Object Factory instance, link it
            sourceObject.nameShort
            sourceObject = sourceObject.nameShort
        except:
            #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
            assert mc.objExists(sourceObject) is True, "'%s' - source object doesn't exist" %sourceObject

        assert self.transform ,"'%s' has no transform"%obj		
        assert mc.ls(sourceObject,type = 'transform'),"'%s' has no transform"%sourceObject
        rigging.copyPivot(self.nameLong,sourceObject)

    def doGroup(self,maintain=False):
        """
        Grouping function for a maya instanced object.

        Keyword arguments:
        maintain(bool) -- whether to parent the maya object in place or not (default False)

        """
        assert mc.ls(self.nameLong,type='transform'),"'%s' has no transform"%self.nameLong	

        group = rigging.groupMeObject(self.nameLong,True,maintain) 
        groupLong = mc.ls(group,long=True)
        self.update(groupLong[0]+'|'+self.nameBase)  
        return groupLong[0]

    def doName(self,sceneUnique=False,nameChildren=False):
        """
        Function for naming a maya instanced object using the cgm.NameFactory class.

        Keyword arguments:
        sceneUnique(bool) -- Whether to run a full scene dictionary check or the faster just objExists check (default False)

        """       
        if self.refState:
            return guiFactory.warning("'%s' is referenced. Cannot change name"%self.nameShort)

        if nameChildren:
            buffer = NameFactory.doRenameHeir(self.nameLong,sceneUnique)
            if buffer:
                self.update(buffer[0])

        else:
            buffer = NameFactory.doNameObject(self.nameLong,sceneUnique)
            if buffer:
                self.update(buffer)   	    


    def doParent(self,p = False):
        """
        Function for parenting a maya instanced object while maintaining a correct object instance.

        Keyword arguments:
        p(string) -- Whether to run a full scene dictionary check or the faster just objExists check

        """ 
        assert self.transform,"'%s' has no transform"%obj	
        
        if p: #if we have a target parent
            try:
                #If we have an Object Factory instance, link it
                p.nameShort
                p = p.nameShort
            except:
                #If it fails, check that the object name exists and if so, initialize a new Object Factory instance
                assert mc.objExists(p) is True, "'%s' - parent object doesn't exist" %p     

            buffer = rigging.doParentReturnName(self.nameLong,p)
            
        else:#If not, do so to world
            buffer = rigging.doParentToWorld(self.nameLong)
            
        self.update(buffer)

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
            assert mc.objExists('%s.%s'%(self.nameLong,a)),"'%s.%s' doesn't exist"%(self.nameLong,a)

        if attrs is None or False:
            for a in drawingOverrideAttrsDict:
                attributes.doSetAttr(self.nameLong,a,drawingOverrideAttrsDict[a])

        if type(attrs) is dict:
            for a in attrs.keys():
                if a in drawingOverrideAttrsDict:
                    try:
                        attributes.doSetAttr(self.nameLong,a,attrs[a])
                    except:
                        raise AttributeError, "There was a problem setting '%s.%s' to %s"%(self.nameBase,a,drawingOverrideAttrsDict[a])
                else:
                    guiFactory.warning("'%s.%s' doesn't exist"%(self.nameBase,a))
                    
        if type(attrs) is list:
            for a in attrs:
                if a in drawingOverrideAttrsDict:
                    try:
                        attributes.doSetAttr(self.nameLong,a,drawingOverrideAttrsDict[a])
                    except:
                        raise AttributeError, "There was a problem setting '%s.%s' to %s"%(self.nameBase,a,drawingOverrideAttrsDict[a])
                else:
                    guiFactory.warning("'%s.%s' doesn't exist"%(self.nameBase,a))       
                    
                    
        if pushToShapes:
            raise NotImplementedError,"This feature isn't done yet"
        

