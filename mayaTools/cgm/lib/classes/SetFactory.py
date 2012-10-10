#=================================================================================================================================================
#=================================================================================================================================================
#	objectFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for finding stuff
#
# ARGUMENTS:
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
from cgm.lib import attributes
from cgm.lib import dictionary
from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes.AttrFactory import *

from cgm.lib.classes import NameFactory

from cgm.lib.ml import (ml_resetChannels)

reload(ml_resetChannels)

setTypes = dictionary.setTypes

class SetFactory(object):
    """ 
    Set Class handler
    
    """
    def __init__(self,setName,setType = False,qssState = False):
        """ 
        Intializes an set factory class handler
        
        Keyword arguments:
        setName(string) -- name for the set
        
        """
        ### input check           
        self.setType = ''
        self.setList = []
        self.qssState = qssState
        self.refPrefix = None
        self.refState = False
        
        if mc.objExists(setName):
            self.baseName = search.findRawTagInfo(setName,'cgmName')
            self.setType = search.returnTagInfo(setName,'cgmType') or ''
            self.storeNameStrings(setName)
            self.updateData()
            self.isRef()
            
        else:
            self.baseName = setName
            self.create(setType)
            self.refState = False

    def storeNameStrings(self,obj):
        """ Store the base, short and long names of an object to instance."""
        set = mc.ls(obj,long=True)
        self.nameLong = set[0]
        set = mc.ls(obj,shortNames=True)        
        self.nameShort = set[0]
        if '|' in set[0]:
            splitBuffer = set[0].split('|')
            self.nameLongBase = splitBuffer[-1]
            return
        self.nameLongBase = self.nameShort  
        
    def create(self,setType):
        """ Creates a set object honoring our quick select set options """ 
        set = mc.sets(em=True)
            
        attributes.storeInfo(set,'cgmName',self.baseName)
        if setType:
            self.setType = setType
            if setType in setTypes.keys():
                doType = setTypes.get(setType)
            else:
                doType = setType
            attributes.storeInfo(set,'cgmType',setType)
            
        set = NameFactory.doNameObject(set,True)
        self.storeNameStrings(set)
        
        if self.qssState:
            self.isQss(self.qssState)        
        
    def isQss(self,arg = True):
        if arg:
            if mc.sets(self.nameLong,q=True,text=True)!= 'gCharacterSet':
                mc.sets(self.nameLong, edit = True, text = 'gCharacterSet')
                guiFactory.warning("'%s' is now a qss"%(self.nameShort))
                self.qssState = True
                
        else:
            if mc.sets(self.nameLong,q=True,text=True)== 'gCharacterSet':
                mc.sets(self.nameLong, edit = True, text = '')            
                guiFactory.warning("'%s' is no longer a qss"%(self.nameShort)) 
                self.qssState = False
                
    def isRef(self):
        if mc.referenceQuery(self.nameLong, isNodeReferenced=True):
            self.refState = True
            self.refPrefix = search.returnReferencePrefix(self.nameLong)
            return
        self.refState = False
        self.refPrefix = None

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def updateData(self,*a,**kw):
        """ 
        Updates the stored data
        
        Stores basic data, qss state and type
        
        """
        self.setList = mc.sets(self.nameLong, q = True)
        if not self.setList:
            self.setList = []
            
        if mc.sets(self.nameLong,q=True,text=True)== 'gCharacterSet':
            self.qssState = True
        else:
            self.qssState = False
            
        self.parents = mc.listSets(o=self.nameLong)
        
        #If it's a maya set
	self.mayaSetState = False
	for check in ['defaultCreaseDataSet',
                          'defaultObjectSet',
                          'defaultLightSet',
                          'initialParticleSE',
                          'initialShadingGroup',
                          'tweakSet']:
		if check in self.nameLong and not self.qssState:
			self.mayaSetState = True
        
        
        typeBuffer = search.returnTagInfo(self.nameLong,'cgmType')
        if typeBuffer:
            for t in setTypes.keys():
                if setTypes.get(t) == typeBuffer:
                    self.setType = t
            if not self.setType:
                self.setType = typeBuffer
            
            
                      
    def store(self,info,*a,**kw):
        """ 
        Store information to a set in maya via case specific attribute.
        
        Keyword arguments:
        info(string) -- must be an object in the scene
        
        """
        assert mc.objExists(info) is True, "'%s' doesn't exist"%info
        if info == self.nameShort:
            return False
        
        if info in self.setList:
            guiFactory.warning("'%s' is already stored on '%s'"%(info,self.nameLong))    
            return
        
        try:
            mc.sets(info,add = self.nameLong)
            self.setList.append(info)
        except:
            guiFactory.warning("'%s' failed to add to '%s'"%(info,self.nameLong))    
            
        
        
    def doStoreSelected(self): 
        """ Store selected objects """
        # First look for attributes in the channel box
        SelectCheck = False
        
        channelBoxCheck = search.returnSelectedAttributesFromChannelBox()
        if channelBoxCheck:
            SelectCheck = True
            for item in channelBoxCheck:
                self.store(item)
            return
        
        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.store(item)
                SelectCheck = True                
            except:
                guiFactory.warning("Couldn't store '%s'"%(item))   
                
        if not SelectCheck:
            guiFactory.warning("No selection found")   
            
        
        
    def remove(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        if info not in self.setList:
            guiFactory.warning("'%s' isn't already stored '%s'"%(info,self.nameLong))    
            return
        
        try:
            mc.sets(info,rm = self.nameLong)    
            guiFactory.warning("'%s' removed!"%(info))  
            self.updateData()
            
        except:
            guiFactory.warning("'%s' failed to remove from '%s'"%(info,self.nameLong))    
            
        
    def doRemoveSelected(self): 
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
                guiFactory.warning("Couldn't remove '%s'"%(item)) 
                
        if not SelectCheck:
            guiFactory.warning("No selection found")   
                    
    def purge(self):
        """ Purge all set memebers from a set """
        
        try:
            mc.sets( clear = self.nameLong)
            self.setList = []
            guiFactory.report("'%s' purged!"%(self.nameLong))     
        except:
            guiFactory.warning("'%s' failed to purge"%(self.nameLong)) 
        
    def copy(self):
        """ Purge all set memebers from a set """
        
        try:
            buffer = mc.sets(name = ('%s_Copy'%self.nameShort), copy = self.nameLong)
            guiFactory.report("'%s' duplicated!"%(self.nameLong))
	    
	    for attr in dictionary.cgmNameTags:
		if mc.objExists("%s.%s"%(self.nameLong,attr)):
		    attributes.doCopyAttr(self.nameLong,attr,buffer)
		
	    return buffer
        except:
            guiFactory.warning("'%s' failed to copy"%(self.nameLong)) 
            
    def select(self):
        """ 
        Select set members or connected objects
        """ 
        if self.setList:
            mc.select(self.setList)
            return
        
        guiFactory.warning("'%s' has no data"%(self.nameShort))  
        return False
    
    def selectSelf(self):
        """ 
        Select set members or connected objects
        """ 
        mc.select(self.nameLong,noExpand=True)
    
    def key(self,*a,**kw):
        """ Select the seted objects """        
        if self.setList:
            mc.select(self.setList)
            mc.setKeyframe(*a,**kw)
            return True
        
        guiFactory.warning("'%s' has no data"%(self.nameShort))  
        return False
    
    def reset(self,*a,**kw):
        """ Reset the set objects """        
        if self.setList:
            mc.select(self.setList)
            ml_resetChannels.resetChannels()        
            return True
        
        guiFactory.warning("'%s' has no data"%(self.nameShort))  
        return False
    
    def deleteKey(self,*a,**kw):
        """ Select the seted objects """        
        if self.setList:
            mc.select(self.setList)
            mc.cutKey(*a,**kw)
            return True
        
        guiFactory.warning("'%s' has no data"%(self.nameShort))  
        return False   
    
    def deleteCurrentKey(self,*a,**kw):
        """ Select the seted objects """        
        if self.setList:
            mc.select(self.setList)
            mel.eval('timeSliderClearKey;')
            return True
        
        guiFactory.warning("'%s' has no data"%(self.nameShort))  
        return False
    
    def doName(self,sceneUnique=False):
        """
        Function for naming a maya instanced object using the cgm.NameFactory class.
        
        Keyword arguments:
        sceneUnique(bool) -- Whether to run a full scene dictionary check or the faster just objExists check (default False)
        
        """   
	assert not self.refState, "Cannot change the name of a referenced set"
	assert not self.mayaSetState, "Cannot change name of a maya default set"
	
        buffer = NameFactory.doNameObject(self.nameLong,sceneUnique)
        self.storeNameStrings(buffer)
        return buffer
        
            
    def doSetType(self,setType = None):
        """ Set a set's type """
	assert not self.refState, "Cannot change the type of a referenced set"
	assert not self.mayaSetState, "Cannot change type of a maya default set"

	
        if setType is not None:
            doSetType = setType
            if setType in setTypes.keys():
                doSetType = setTypes.get(setType)

            if attributes.storeInfo(self.nameLong,'cgmType',doSetType,True):
                self.doName()
                guiFactory.warning("'%s' renamed!"%(self.nameShort))  
                return self.nameShort
            else:               
                guiFactory.warning("'%s' failed to store info"%(self.nameShort))  
                return False
        else:
            attributes.doDeleteAttr(self.nameShort,'cgmType')
            self.doName()
            guiFactory.warning("'%s' renamed!"%(self.nameShort))  
            return self.nameShort
    


        

    
