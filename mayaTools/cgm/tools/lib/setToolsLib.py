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
    guiFactory.doPrintReportStart()
    tmp = OptionVarFactory('cgmVar_activeObjectSets','string')    
    print "# Object Sets found: "
    for o in self.objectSets:
        print "#    '%s'"%o
    if tmp.value:
        print "# Active Sets: "
        for o in tmp.value:
            if o:
                print "#    '%s'"%o        
    guiFactory.doPrintReportEnd()


def updateObjectSets(self):
    self.objectSets = search.returnObjectSets()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Individual Set Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def selectSetObjects(self,nameIndex):
    tmp = SetFactory(self.objectSetsDict.get(nameIndex))
    tmp.select()

def addSelected(self,nameIndex):
    tmp = SetFactory(self.objectSetsDict.get(nameIndex))
    tmp.doStoreSelected()

def removeSelected(self,nameIndex):
    tmp = SetFactory(self.objectSetsDict.get(nameIndex))
    tmp.doRemoveSelected()

def keySet(self,nameIndex):
    tmp = SetFactory(self.objectSetsDict.get(nameIndex))
    tmp.key() 
    
def deleteCurrentSetKey(self,nameIndex):
    tmp = SetFactory(self.objectSetsDict.get(nameIndex))
    time = search.returnTimelineInfo()
    tmp.deleteCurrentKey()  

def purgeSet(self,nameIndex):
    tmp = SetFactory(self.objectSetsDict.get(nameIndex))
    tmp.purge()  

def setSetAsActive(self,optionVar,nameIndex):
    tmp = OptionVarFactory(optionVar,'string')
    if '' in tmp.value:
        tmp.remove('')
    tmp.append(self.objectSetsDict.get(nameIndex)) 

def setSetAsInactive(self,optionVar,nameIndex):
    tmp = OptionVarFactory(optionVar,'string')
    tmp.remove(self.objectSetsDict.get(nameIndex)) 

def createSet(self):
    b = SetFactory('Set')
    b.doStoreSelected()
    self.reset()
    
def deleteSet(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)  
    mc.delete(setName)
    self.reset()
    
def copySet(self,nameIndex):
    tmp = SetFactory(self.objectSetsDict.get(nameIndex))
    tmp.copy()
    self.reset()
    
def toggleQssState(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    Set = SetFactory(setName)
    Set.isQss(not Set.qssState)
    
def updateSetName(self,setTextField,nameIndex):
    # get the field
    setName = self.objectSetsDict.get(nameIndex)
    assert mc.objExists(setName) is True,"'%s' doesn't exist.Try updating the tool."%bufferObject

    newName = mc.textField(setTextField,q=True,text = True)

    if setName and newName:
        #Name it
        attributes.storeInfo(setName,'cgmName',newName)
        buffer = NameFactory.doNameObject(setName)
        #Update...field
        mc.textField(setTextField,e = True,text = buffer)
        #...dict...
        self.objectSetsDict[nameIndex] = buffer
        #...optionVar...
        tmp = OptionVarFactory('cgmVar_activeObjectSets','string')
        if setName in tmp.value:
            guiFactory.report("Set was an active set. Setting new name '%s' as active"%buffer)
            tmp.remove(setName)
            tmp.append(buffer) 
        

    else:
        guiFactory.warning("There's a problem with the name input.")
        
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# All Set Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
def selectAll(self):
    allObjectsList = []
    for i in self.objectSetsDict.keys():
        tmp = SetFactory(self.objectSetsDict.get(i))
        allObjectsList.extend(tmp.setList)
    
    mc.select(allObjectsList)
    
def setAllSetsAsActive(self):
    if self.activeSetsCBDict:
        for i,s in enumerate(self.activeSetsCBDict.keys()):
            tmp = self.activeSetsCBDict.get(s)          
            mc.checkBox(tmp, edit = True,
                        value = True)
            setSetAsActive(self,'cgmVar_activeObjectSets',i)

def setAllSetsAsInactive(self):
    if self.activeSetsCBDict:
        for i,s in enumerate(self.activeSetsCBDict.keys()):
            tmp = self.activeSetsCBDict.get(s)                        
            mc.checkBox(tmp, edit = True,
                        value = False)
            setSetAsInactive(self,'cgmVar_activeObjectSets',i)
            
def keyAll(self):
    allObjectsList = []
    for i in self.objectSetsDict.keys():
        tmp = SetFactory(self.objectSetsDict.get(i))
        tmp.key()
    
def deleteAllCurrentKeys(self):
    allObjectsList = []
    for i in self.objectSetsDict.keys():
        tmp = SetFactory(self.objectSetsDict.get(i))
        tmp.deleteCurrentKey()
    
    selectAll(self)