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
        
        if mc.objExists(bufferName):
            self.baseName = search.findRawTagInfo(bufferName,'cgmName')
            self.bufferType = search.findRawTagInfo(bufferName,'cgmType')
            self.storeNameStrings(bufferName)
            userAttrs = mc.listAttr(self.nameLong,ud=True)
            for attr in userAttrs:
                if 'item_' in attr:
                    a = AttrFactory(bufferName,attr)
                    data = a.getMessage()
                    if data:
                        self.bufferList.append(data)
            
        else:
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
        buffer = mc.group(em=True)
        attributes.storeInfo(buffer,'cgmName',self.baseName)
        attributes.storeInfo(buffer,'cgmType','objectBuffer')
        buffer = NameFactory.doNameObject(buffer,True)
        storeNameStrings(buffer)
        
    def returnNextAvailableCnt(self):
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
    def store(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        if info in self.bufferList:
            guiFactory.warning("'%s' is already stored on '%s'"%(info,self.nameLong))    
            return
        
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
    
        attributes.storeInfo(self.nameLong,('item_'+str(cnt)),info,*a,**kw)
        self.bufferList.append(info)
        
        
    def remove(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        if info not in self.bufferList:
            guiFactory.warning("'%s' isn't already stored '%s'"%(info,self.nameLong))    
            return
        
        userAttrs = attributes.returnUserAttrsToDict(self.nameLong)
        countList = []
        for key in userAttrs.keys():
            if item == attributes.getInfo:
                pass
        
    def purge(self):
        userAttrs = attributes.returnUserAttrsToDict(self.nameLong)
        for attr in userAttrs.keys():
            if 'item_' in attr:
                attributes.deleteAttr(self.nameLong,attr)
                guiFactory.warning("Deleted: '%s.%s'"%(self.nameLong,attr))    
                
        self.bufferList = []
        
    def doStoreSelected(self): 
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.store(item)
            except:
                guiFactory.warning("Couldn't store '%s'"%(item))    
                
        
    def select(self):
        if self.bufferList:
            for item in self.bufferList:
                print item
    


        

    
