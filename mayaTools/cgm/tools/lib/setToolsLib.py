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

from cgm.lib import (search,guiFactory,lists)
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
    self.refPrefixes = []        
    
    if self.objectSets:
        for o in self.objectSets:
            buffer = search.returnReferencePrefix(o)
            if buffer:
                self.refPrefixes.append(buffer)
        if self.refPrefixes:
            self.refPrefixes = lists.returnListNoDuplicates(self.refPrefixes)
    
        print ("Prefixes are: '%s'"%self.refPrefixes)
            
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Individual Set Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def selectSetObjects(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.select()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()
        

def addSelected(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.doStoreSelected()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()


def removeSelected(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.doRemoveSelected()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()
        

def keySet(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.key()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()
    
    
def deleteCurrentSetKey(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.deleteCurrentKey()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()
    

def purgeSet(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.purge()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()


def setSetAsActive(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        if '' in self.activeObjectSetsOptionVar.value:
            self.activeObjectSetsOptionVar.remove('')
        self.activeObjectSetsOptionVar.append(setName) 
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()

def setSetAsInactive(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName): 
        self.activeObjectSetsOptionVar.remove(setName) 
            
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()

def createSet(self):
    b = SetFactory('Set')
    b.doStoreSelected()
    self.reset()
    
def deleteSet(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex) 
    if mc.objExists(setName):
        mc.delete(setName)
        self.reset()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()
    
def copySet(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex) 
    if mc.objExists(setName):
        s = SetFactory(self.objectSetsDict.get(nameIndex))
        s.copy()
        self.reset()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()
    
def toggleQssState(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.isQss(not s.qssState)
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()
    
def updateSetName(self,setTextField,nameIndex):
    # get the field
    setName = self.objectSetsDict.get(nameIndex)
    if not mc.objExists(setName):
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()
        return

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
# Multi Set Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
def setAllSetsAsActive(self):
    if self.activeSetsCBDict:
        for i,s in enumerate(self.activeSetsCBDict.keys()):
            tmp = self.activeSetsCBDict.get(s)          
            mc.checkBox(tmp, edit = True,
                        value = True)
            setSetAsActive(self,i)

def setAllSetsAsInactive(self):
    if self.activeSetsCBDict:
        for i,s in enumerate(self.activeSetsCBDict.keys()):
            tmp = self.activeSetsCBDict.get(s)                        
            mc.checkBox(tmp, edit = True,
                        value = False)
            setSetAsInactive(self,i)

def selectMultiSets(self):
    allObjectsList = []            
    if self.setMode:
        if self.activeObjectSetsOptionVar.value:
            for o in self.activeObjectSetsOptionVar.value:
                s = SetFactory(o)
                allObjectsList.extend(s.setList)     
        else:
            guiFactory.warning("No active sets found")
            return
            
    else:
        for i in self.objectSetsDict.keys():
            tmp = SetFactory(self.objectSetsDict.get(i))
            allObjectsList.extend(tmp.setList)

    if allObjectsList:
        mc.select(allObjectsList)
            
def keyMultiSets(self):
    allObjectsList = []   
    
    if self.setMode:
        if self.activeObjectSetsOptionVar.value:    
            for i in self.objectSetsDict.keys():
                s = SetFactory(self.objectSetsDict.get(i))
                s.key()
                allObjectsList.extend(s.setList)                 
        else:
            guiFactory.warning("No active sets found")
            return  
    else:
        for i in self.objectSetsDict.keys():
            s = SetFactory(self.objectSetsDict.get(i))
            s.key()
            allObjectsList.extend(s.setList)             

    if allObjectsList:
        mc.select(allObjectsList)
    
def deleteMultiCurrentKeys(self):
    allObjectsList = []      
    
    if self.setMode:
        if self.activeObjectSetsOptionVar.value:    
            for i in self.objectSetsDict.keys():
                s = SetFactory(self.objectSetsDict.get(i))
                s.deleteCurrentKey()
                allObjectsList.extend(s.setList)                
        else:
            guiFactory.warning("No active sets found")
            return  
    else:
        for i in self.objectSetsDict.keys():
            s = SetFactory(self.objectSetsDict.get(i))
            s.deleteCurrentKey()
            allObjectsList.extend(s.setList) 
            
    if allObjectsList:
        mc.select(allObjectsList)    
            
            
    
