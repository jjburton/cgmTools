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
from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes.AttrFactory import *

from cgm.lib.classes import NameFactory


class BufferFactory(object):
    """ 
    Buffer Class handler
    
    """
    def __init__(self,bufferName):
        """ 
        Intializes an buffer factory class handler
        
        Keyword arguments:
        bufferName(string) -- name for the buffer
        
        """
        ### input check           
        self.bufferType = ''
        self.bufferList = []
        self.bufferDict = {}
        
        if mc.objExists(bufferName):
            self.baseName = search.findRawTagInfo(bufferName,'cgmName')
            self.storeNameStrings(bufferName)
            self.updateData()
            
        else:
            self.baseName = bufferName
            self.create()

    def storeNameStrings(self,obj):
        """ Store the base, short and long names of an object to instance."""
        buffer = mc.ls(obj,long=True)
        self.nameLong = buffer[0]
        buffer = mc.ls(obj,shortNames=True)        
        self.nameShort = buffer[0]
        if '|' in buffer[0]:
            splitBuffer = buffer[0].split('|')
            self.nameLongBase = splitBuffer[-1]
            return
        self.nameLongBase = self.nameShort  
        
    def create(self):
        """ Creates a cgm buffer object """        
        buffer = mc.group(em=True)
        attributes.storeInfo(buffer,'cgmName',self.baseName)
        buffer = NameFactory.doNameObject(buffer,True)
        self.storeNameStrings(buffer)
        
    def returnNextAvailableCnt(self):
        """ Get's the next available item number """        
        userAttrs = attributes.returnUserAttrsToDict(self.nameLong)
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
        userAttrs = mc.listAttr(self.nameLong,ud=True) or []
        for attr in userAttrs:
            if 'item_' in attr:
                a = AttrFactory(self.nameLong,attr)
                data = a.getMessage()
                if data:
                    self.bufferList.append(data)
                    self.bufferDict[attr] = data
                    
    def rebuild(self,*a,**kw):
        """ Rebuilds the buffer data cleanly """        
        if self.bufferDict:
            #make a copy list            
            buffer = []
            for item in self.bufferList:
                buffer.append(item)
                
            #purge our existing stuff
            self.purge()
            
            #add our stuff    
            for item in buffer:
                try:
                    self.store(item)
                except:
                    guiFactory.warning("'%s' failed. Probably doesn't exist"%(info))    
            # Update data        
            self.updateData()
                    
    def store(self,info,*a,**kw):
        """ 
        Store information to an object in maya via case specific attribute.
        
        Keyword arguments:
        info(string) -- must be an object in the scene
        
        """
        assert mc.objExists(info) is True, "'%s' doesn't exist"%info
        
        if info in self.bufferList:
            guiFactory.warning("'%s' is already stored on '%s'"%(info,self.nameLong))    
            return
        
        userAttrs = attributes.returnUserAttrsToDict(self.nameLong) or {}
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
    
        attributes.storeInfo(self.nameLong,('item_'+str(cnt)),info,*a,**kw)
        guiFactory.warning("'%s' stored on '%s'"%(info,self.nameLong))            
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
                guiFactory.warning("Couldn't store '%s'"%(item))     
        
    def remove(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        if info not in self.bufferList:
            guiFactory.warning("'%s' isn't already stored '%s'"%(info,self.nameLong))    
            return
        
        for key in self.bufferDict.keys():
            if self.bufferDict.get(key) == info:
                attributes.doDeleteAttr(self.nameLong,key)
                self.bufferList.remove(info)
                self.bufferDict.pop(key)
                
        guiFactory.warning("'%s' removed!"%(info))  
                
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
                guiFactory.warning("Couldn't remove '%s'"%(item)) 
                
    def purge(self):
        """ Purge all buffer attributes from an object """
        
        userAttrs = mc.listAttr(self.nameLong,userDefined = True) or []
        for attr in userAttrs:
            if 'item_' in attr:
                attributes.doDeleteAttr(self.nameLong,attr)
                guiFactory.warning("Deleted: '%s.%s'"%(self.nameLong,attr))  
                
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
                    tmpFactory = BufferFactory(item)
                    selectList.extend(tmpFactory.bufferList)
                    
                    for item in tmpFactory.bufferList:
                        if search.returnTagInfo(item,'cgmType') == 'objectBuffer':
                            subTmpFactory = BufferFactory(item)   
                            selectList.extend(subTmpFactory.bufferList)
                            
                else:
                    selectList.append(item)
                    
            mc.select(selectList)
            return
        
        guiFactory.warning("'%s' has no data"%(self.nameShort))  
        return False
    
    def key(self,*a,**kw):
        """ Select the buffered objects """        
        if self.bufferList:
            mc.select(self.bufferList)
            mc.setKeyframe(*a,**kw)
            return True
        
        guiFactory.warning("'%s' has no data"%(self.nameShort))  
        return False
    


        

    
