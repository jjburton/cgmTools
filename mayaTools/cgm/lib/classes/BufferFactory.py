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
from cgm.lib.classes import NameFactory

class BufferFactory(OptionVarFactory):
    """ 
    Buffer Class handler
    
    """
    def __init__(self,bufferName):
        """ 
        Intializes an buffer factory class handler
        
        Keyword arguments:
        varName(string) -- name for the optionVar
        varType(string) -- 'int','float','string' (default 'int')
        
        """
        ### input check           
        self.rootName = bufferName
        self.bufferType = ''
        self.bufferList = []
        
        if mc.objExists(bufferName):
            self.rootName = search.findRawTagInfo(bufferName,'cgmName')
            self.bufferType = search.findRawTagInfo(bufferName,'cgmType')
            self.name = bufferName
            userAttrs = attributes.returnUserAttrsToDict(self.name)
            for key in userAttrs.keys():
                if 'item_' in key:
                    data = userAttrs.get(key)
                    if data:
                        self.bufferList.append(data)
            
        else:
            self.create()

        
        
    def create(self):
        buffer = mc.group(em=True)
        attributes.storeInfo(buffer,'cgmName',self.rootName)
        attributes.storeInfo(buffer,'cgmType','objectBuffer')
        self.name = NameFactory.doNameObject(buffer,True)
        
    def returnNextAvailableCnt(self):
        userAttrs = attributes.returnUserAttrsToDict(self.name)
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
        
    def store(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        if info in self.bufferList:
            guiFactory.warning("'%s' is already stored on '%s'"%(info,self.name))    
            return
        
        userAttrs = attributes.returnUserAttrsToDict(self.name)
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
    
        attributes.storeInfo(self.name,('item_'+str(cnt)),info,*a,**kw)
        self.bufferList.append(info)
        
    def purge(self):
        userAttrs = attributes.returnUserAttrsToDict(self.name)
        for attr in userAttrs.keys():
            if 'item_' in attr:
                attributes.deleteAttr(self.name,attr)
                guiFactory.warning("Deleted: '%s.%s'"%(self.name,attr))    
                
                
    def doStoreSelected(self): 
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.store(item)
            except:
                guiFactory.warning("Couldn't store '%s'"%(item))    
                
        
    def select(self):
        if self.value:
            for item in self.value:
                print item
    


        

    
