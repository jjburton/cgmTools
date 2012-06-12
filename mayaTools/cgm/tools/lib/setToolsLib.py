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
    print self.refSetsDict
    print "# Object Sets found: "
    for o in self.objectSetsRaw:
        print "#    '%s'"%o
    
    print "# Loaded Sets: "  
    for o in self.objectSets:
        print "#    '%s'"%o  
        
    if self.ActiveObjectSetsOptionVar.value:
        print "# Active Sets: "
        for o in self.ActiveObjectSetsOptionVar.value:
            if o:
                print "#    '%s'"%o 
    if self.refSetsDict:
        print "# Refs and sets: "
        for o in self.refSetsDict.keys():
            print "#     '%s':'%s'"%(o,"','".join(self.refSetsDict.get(o)))            
    
    if self.ActiveRefsOptionVar.value:
        print "# Active Refs: "
        for o in self.ActiveRefsOptionVar.value:
            if o:
                print "#    '%s'"%o 
    guiFactory.doPrintReportEnd()


def updateObjectSets(self):
    self.objectSetsRaw = search.returnObjectSets()
    self.refPrefixes = []
    self.refSetsDict = {'From Scene':[]}
    self.sortedSets = []
    self.objectSets = []
    
    if self.objectSetsRaw:
        for o in self.objectSetsRaw:
            # Get our reference prefixes and sets sorted out
            buffer = search.returnReferencePrefix(o)
            if buffer:
                if buffer in self.refSetsDict.keys():
                    self.refSetsDict[buffer].append(o)
                else:
                    self.refSetsDict[buffer] = [o]
            else:
                self.refSetsDict['From Scene'].append(o)
                        
        if self.refSetsDict.keys():
            self.refPrefixes.extend( self.refSetsDict.keys() )
        
    if self.ActiveRefsOptionVar.value and self.objectSetsRaw:
        self.sortedSets = []
        for r in self.refSetsDict.keys():
            if r in self.ActiveRefsOptionVar.value:
                self.sortedSets.extend(self.refSetsDict.get(r))
                
        if self.sortedSets:
            self.objectSets = self.sortedSets
        else:
            self.objectSets = self.objectSetsRaw
            
    else:
        self.objectSets = self.objectSetsRaw
            
            
    #Get our sets ref info
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
        if '' in self.ActiveObjectSetsOptionVar.value:
            self.ActiveObjectSetsOptionVar.remove('')
        self.ActiveObjectSetsOptionVar.append(setName) 
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()

def setSetAsInactive(self,nameIndex):
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName): 
        self.ActiveObjectSetsOptionVar.remove(setName) 
            
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reset()

def setRefState(self,refIndex,value,reset = True):
    refName = self.refPrefixDict.get(refIndex)
    if refName in self.refPrefixes:
        if value:
            self.ActiveRefsOptionVar.append(refName)
        else:
            self.ActiveRefsOptionVar.remove(refName)
        if reset:
            self.reset()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%refName)
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
        if self.ActiveObjectSetsOptionVar.value:
            for o in self.ActiveObjectSetsOptionVar.value:
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
        if self.ActiveObjectSetsOptionVar.value:    
            for o in self.ActiveObjectSetsOptionVar.value:
                s = SetFactory(o)
                s.key()
                allObjectsList.extend(s.setList)                 
        else:
            guiFactory.warning("No active sets found")
            return  
    else:
        for o in self.objectSetsDict.keys():
            s = SetFactory(self.objectSetsDict.get(o))
            s.key()
            allObjectsList.extend(s.setList)             

    if allObjectsList:
        mc.select(allObjectsList)
    
def deleteMultiCurrentKeys(self):
    allObjectsList = []      
    
    if self.setMode:
        if self.ActiveObjectSetsOptionVar.value:    
            for o in self.ActiveObjectSetsOptionVar.value:
                s = SetFactory(o)
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
            
def setAllRefState(self,value):
    if self.activeRefsCBDict:
        for i in self.activeRefsCBDict.keys():
            tmp = self.activeRefsCBDict.get(i)
            mc.menuItem(tmp,edit = True,cb=value)
            setRefState(self,i,value,False)
        self.reset()
            
