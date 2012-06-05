#=================================================================================================================================================
#=================================================================================================================================================
#	bufferToolsLib - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Library of functions for the cgmRiggingTools tool
#
# ARGUMENTS:
#   Maya
#
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1.12072011 - First version
#	0.1.12132011 - master control maker implemented, snap move tools added
#	0.1.12272011 - split out library from tool
#
#=================================================================================================================================================
__version__ = '0.1.12032011'

import maya.cmds as mc
import maya.mel as mel
import subprocess

from cgm.lib.cgmBaseMelUI import *
from cgm.lib.classes.SetFactory import *
from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes import NameFactory

from cgm.lib import (search,guiFactory)
reload(search)
reload(guiFactory)

"""

"""
def printReport(self):
    print self.objectSets 

def updateObjectSets(self):
    self.objectSets = search.returnObjectSets()

def selectSetObjects(objectSetName):
    tmp = SetFactory(objectSetName)
    tmp.select()

def addSelected(objectSetName):
    tmp = SetFactory(objectSetName)
    tmp.doStoreSelected()

def removeSelected(objectSetName):
    tmp = SetFactory(objectSetName)
    tmp.doRemoveSelected()

def keySet(objectSetName):
    tmp = SetFactory(objectSetName)
    tmp.key()  

def purgeSet(objectSetName):
    tmp = SetFactory(objectSetName)
    tmp.purge()  

def setSetAsActive(optionVar,setName):
    tmp = OptionVarFactory(optionVar,'string')
    if '' in tmp.value:
        tmp.remove('')
    tmp.append(setName) 

def setSetAsInactive(optionVar,setName):
    tmp = OptionVarFactory(optionVar,'string')
    tmp.remove(setName) 

def createSet(self):
    b = SetFactory('Set')
    b.doStoreSelected()
    self.reset()

def setEditSet(self,name):
    self.editSet = name

"""
def updateSetName(self,setTextField,setName):
    # get the field
    assert mc.objExists(setName) is True,"'%s' doesn't exist.Try updating the tool."%bufferObject

    
    newName = mc.textField(setTextField,q=True,text = True)

    if setName and newName:
        attributes.storeInfo(setName,'cgmName',newName)
        buffer = NameFactory.doNameObject(setName)
        if buffer:
            mc.textField(setTextField,e = True,text = buffer)
            updateObjectSets(self)
            guiFactory.resetGuiInstanceOptionVars(self.optionVars,run)

    else:
        guiFactory.warning("There's a problem with the name input.")"""

