#=================================================================================================================================================
#=================================================================================================================================================
#	objectFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for finding stuff
#
# REQUIRES:
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

from cgm.lib import (lists,
                     search,
                     autoname,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)


class ObjectFactory():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Assertions to verify:
    1) An object knows what it is

    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    def __init__(self,obj):
        ### input check
        assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
        self.cgmName = ''
        self.cgmNameModifier = ''
        self.cgmPosition = ''
        self.cgmDirectionModifier = ''
        self.cgmDirection = ''
        self.cgmIterator = ''
        self.cgmTypeModifier = ''
        self.cgmType  = ''
        self.parent = False
        self.children = False
        self.type = ''
        
        self.userAttrs = {}
        
        self.update(obj)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def getCGMNameTags(self):
        self.cgmName = search.findRawTagInfo(self.nameLong,'cgmName')
        self.cgmNameModifier =  search.findRawTagInfo(self.nameLong,'cgmNameModifier')
        self.cgmPosition =  search.findRawTagInfo(self.nameLong,'cgmPosition')
        self.cgmDirectionModifier =  search.findRawTagInfo(self.nameLong,'cgmDirectionModifier')
        self.cgmDirection =  search.findRawTagInfo(self.nameLong,'cgmDirection')
        self.cgmIterator =  search.findRawTagInfo(self.nameLong,'cgmIterator')
        self.cgmTypeModifier =  search.findRawTagInfo(self.nameLong,'cgmTypeModifier')
        self.cgmType  =  search.findRawTagInfo(self.nameLong,'cgmType')
                
    def getUserAttrs(self):
        self.userAttrs = attributes.returnUserAttrsToDict(self.nameLong)
        
    def getType(self):
        self.type = search.returnObjectType(self.nameLong)
        
    def getFamily(self):
        self.parent = search.returnParentObject(self.nameLong)
        self.children = search.returnChildrenObjects(self.nameLong)
        self.shapes = mc.listRelatives(self.nameLong,shapes=True)
        
    def storeNameStrings(self,obj):
        buffer = mc.ls(obj,long=True)
        self.nameLong = buffer[0]
        buffer = mc.ls(obj,shortNames=True)        
        self.nameShort = buffer[0]
        if '|' in buffer[0]:
            splitBuffer = buffer[0].split('|')
            self.nameBase = splitBuffer[-1]
        else:
            self.nameBase = self.nameShort
        
    def name(self):
        buffer = autoname.doNameObject(self.nameLong)
        if buffer:
            self.update(buffer)
            
    def doName(self):
        buffer = autoname.doNameObject(self.nameLong)
        if buffer:
            self.update(buffer)
            
    def doParent(self,p):
        buffer = rigging.doParentReturnName(self.nameLong,p)
        self.update(  buffer)  
        
    def store(self,attr,info,*a,**kw):
        attributes.storeInfo(self.nameLong,attr,info,*a,**kw)

    def doGroup(self,maintain=False):
        group = rigging.groupMeObject(self.nameLong,True,maintain) 
        groupLong = mc.ls(group,long =True)
        self.update(groupLong[0]+'|'+self.nameBase)  
        
    def deleteAttr(self,attr):
        try:
            attributes.deleteAttr(self.nameLong,attr)
        except:
            guiFactory.warning("'%s.%s' not found"%(self.nameLong,attr))
        
    def update(self,obj):
        self.storeNameStrings(obj) 
        self.getType()
        self.getFamily()
        self.getCGMNameTags()
        self.getUserAttrs()        

