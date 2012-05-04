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
        if mc.objExists(bufferName):
            self.rootName = search.findRawTagInfo(bufferName,'cgmName')
            self.bufferType = search.findRawTagInfo(bufferName,'cgmType')
        ### input check   
        self.rootName = bufferName
        self.bufferType = ''
        
        self.create()
        
        
    def create(self):
        buffer = mc.group(em=True)
        attributes.storeInfo(buffer,'cgmName',self.rootName)
        attributes.storeInfo(buffer,'cgmType','objectBuffer')
        self.name = NameFactory.doNameObject(buffer)
        
    def store(self,attr,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        attributes.storeInfo(self.nameLong,attr,info,*a,**kw)        
        
    def select(self):
        if self.value:
            for item in self.value:
                print item
    


        

    
