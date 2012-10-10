#=================================================================================================================================================
#=================================================================================================================================================
#	setToolsLib - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2012 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1.06192012 - FIrst release version, documentation added
#
#=================================================================================================================================================
__version__ = '0.1.06192012'

import maya.cmds as mc
import maya.mel as mel
import subprocess
from cgm.lib.classes import SetFactory 
reload(SetFactory)

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
    """ 
    Generates a report for the objectSets as the tool sees them.    
    """    
    guiFactory.doPrintReportStart()
    print self.refSetsDict
    print "# %i Object Sets found: "%len(self.objectSetsRaw['all'])
    for o in self.objectSetsRaw['all']:
        print "#    '%s'"%o
    
    print "# Loaded Sets: "  
    if self.objectSets:
	for o in self.objectSets:
	    print "#    '%s'"%o  
    else:
	"No loaded sets. Check your hiding flags"
	
    print "# Qss Sets: "
    if self.qssSets:
	print "#     '%s'"%("','".join(self.qssSets))  
    else:
	print ("#     None")
		
    if self.ActiveObjectSetsOptionVar.value:
        print "# Active Sets: "
        for o in self.ActiveObjectSetsOptionVar.value:
            if o:
                print "#    '%s'"%o 
    if self.refSetsDict:
        print "# Refs and sets: "
        for r in self.refSetsDict.keys():
            print "#     '%s':'%s'"%(r,"','".join(self.refSetsDict.get(r)))           
    
    print "# Active Refs: "
    if self.ActiveRefsOptionVar.value:   
        for o in self.ActiveRefsOptionVar.value:
            if o:
                print ("#    '%s'"%o)
    else:
        print ("#    None")
                  
    print "# Active Types: "
    if self.ActiveTypesOptionVar.value:    
        for o in self.ActiveTypesOptionVar.value:
            if o:
                print "#    '%s'"%o 
    else:
        print "#    None"
	
    print "# Maya Sets: "
    if self.mayaSets:    
	for o in self.mayaSets:
	    if o:
		print "#    '%s'"%o 
    else:
	print "#    None"
                
    guiFactory.doPrintReportEnd()


def updateObjectSets(self):
    """ 
    Gets sccene set objects, and sorts the data in to the class as varaibles
    """  
    self.objectSetsRaw = search.returnObjectSets()
    
    self.refPrefixes = self.objectSetsRaw['referenced'].keys()
    self.refSetsDict = self.objectSetsRaw['referenced'] or {}
    self.setTypesDict = self.objectSetsRaw['cgmTypes'] or {}
    self.setGroups = self.objectSetsRaw['objectSetGroups'] or []
    #Set Group stuff
    self.setGroupName = False
    
    for s in self.setGroups:
	if s in self.refSetsDict.get('From Scene'):
	    self.setGroupName = s
	    self.setsGroup = SetFactory(s)
	    break
    
    self.mayaSets = self.objectSetsRaw['maya'] or []
    self.qssSets = self.objectSetsRaw['qss'] or []
	
    self.sortedSets = []
    self.objectSets = []
    self.activeSets = []
    
    #Sort sets we want to actually load
    self.sortedSets = []
    
    #Sort for activeRefs
    tmpActiveRefSets = []
    if self.ActiveRefsOptionVar.value:
	for r in self.ActiveRefsOptionVar.value:
	    #If value, let's add or subtract based on if our set refs are found
	    if self.refSetsDict.get(r):
		tmpActiveRefSets.extend(self.refSetsDict.get(r))
			   
    #Sort for active types  
    tmpActiveTypeSets = []
    if self.setTypesDict.keys() and self.ActiveTypesOptionVar.value:
	for t in self.setTypesDict.keys():
	    if t in self.ActiveTypesOptionVar.value and self.setTypesDict.get(t):	    
		tmpActiveTypeSets.extend(self.setTypesDict.get(t))

    if tmpActiveTypeSets and tmpActiveRefSets:
	self.sortedSets = lists.returnMatchList(tmpActiveTypeSets,tmpActiveRefSets)
    elif tmpActiveTypeSets:
	self.sortedSets = tmpActiveTypeSets
    else:
	self.sortedSets = tmpActiveRefSets
	
	
    #Next step, hiding. First get our cull lists
    if self.sortedSets:
        self.objectSets = self.sortedSets
    else:
        self.objectSets = self.objectSetsRaw['all']
	
    # Start pulling out stuff by making a list we can iterate through as culling from a list you're iterating through doesn't work
    bufferList = copy.copy(self.objectSets)
    
    # Hide Set groups
    if mc.optionVar(q='cgmVar_HideSetGroups'):
        for s in self.setGroups:
	    try:self.objectSets.remove(s)
	    except:pass
	    
                
    # Hide animLayer Sets
    if mc.optionVar(q='cgmVar_HideAnimLayerSets'):
        for s in bufferList:
            if search.returnObjectType(s) == 'animLayer':
		try:self.objectSets.remove(s)
		except:pass

                
    # Hide Maya Sets
    if mc.optionVar(q='cgmVar_HideMayaSets'):
	for s in self.mayaSets:
	    try:self.objectSets.remove(s)
	    except:pass
	    
	    
    # Hide non qss Sets
    #print self.qssSets
    #print self.objectSets
    if mc.optionVar(q='cgmVar_HideNonQss'):
	#print "sorting for qss"
	for s in bufferList:
	    if s not in self.qssSets and s not in self.setGroups:
		try:self.objectSets.remove(s)
		except:pass 
    
    
    #Refresh our active lists    
    if self.ActiveObjectSetsOptionVar.value:
	for o in self.objectSets:
	    if o in self.ActiveObjectSetsOptionVar.value:
		self.activeSets.append(o) 
       
    self.setInstances = {}
    self.setInstancesFastIndex = {}
	
    #If we have object sets to load, we're gonna initialize em
    if self.objectSets:
	#Counter build
	mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(self.objectSetsRaw),"Getting Set info")
	
        for i,o in enumerate(self.objectSets):
	    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
		break
	    mc.progressBar(mayaMainProgressBar, edit=True, status = ("On set %s"%(o)), step=1)                    	
	    
	    self.setInstances[i] = SetFactory(o) #Store the instance so we only have to do it once
	    sInstance = self.setInstances[i] #Simple link to keep the code cleaner
	    
	    self.setInstancesFastIndex[o] = i #Store name to index for fast lookup of index on the fly
	    	    
	guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

    # Set Group creation if they don't have em
    if mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ) and not self.setGroupName:
        initializeSetGroup(self)
        
    if mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ):
        doGroupLocal(self)
                    
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Individual Set Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doSelectSetObjects(self,nameIndex):
    """ 
    Selectes the objects of an indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    try:
	self.setInstances[nameIndex].select()
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()
        

def doAddSelected(self,nameIndex):
    """ 
    Adds selected objects to an indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """
    try:
	self.setInstances[nameIndex].doStoreSelected()
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()
	


def doRemoveSelected(self,nameIndex):
    """ 
    Removes selected objects to an indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    try:
	self.setInstances[nameIndex].doRemoveSelected()
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()
        

def doKeySet(self,nameIndex):
    """ 
    Keys the objects of an indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """      
    try:
        if self.KeyTypeOptionVar.value:
            self.setInstances[nameIndex].key(breakdown = True)
        else:
            self.setInstances[nameIndex].key()	
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()
    
        
def doResetSet(self,nameIndex):
    """ 
    Reset the objects of an indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    
    Note - the reset funtion utilizes Morgan Loomis' ml_resetChannels function
    """   
    try:
	self.setInstances[nameIndex].reset()
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()
	
    
def doDeleteCurrentSetKey(self,nameIndex):
    """ 
    Delete the current frame keys from the objects of an indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """       
    try:
	self.setInstances[nameIndex].deleteCurrentKey()
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()
	

def doPurgeSet(self,nameIndex):
    """ 
    Purge the objects of an indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """    
    try:
	self.setInstances[nameIndex].purge()
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()
	

def doCreateSet(self):
    """ 
    Create a set and reload the gui
    """
    b = SetFactory('Set')
    b.isQss(True)
    b.doStoreSelected()
    self.reload()
    
def doDeleteSet(self,nameIndex):
    """ 
    Delete an indexed object set and reload the gui
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """   	
    setName = self.setInstances[nameIndex].nameLong
    print self.setInstances[nameIndex].mayaSetState 
    print self.setInstances[nameIndex].refState 
    if mc.objExists(setName):
	if not self.setInstances[nameIndex].mayaSetState and not self.setInstances[nameIndex].refState:
	    mc.delete(setName)
	    self.reload()
	else:
	    guiFactory.warning("'%s' is a referenced or a maya set. Cannot delete!"%setName)	    
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()
    
def doCopySet(self,nameIndex):
    """ 
    Duplicate an indexed object set and reload the gui
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    try:
	buffer = self.setInstances[nameIndex].copy()
	print buffer
        self.reload()	
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()    
	
    
def doToggleQssState(self,nameIndex):
    """ 
    Toggle the qss state of a indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """ 
    try:
	self.setInstances[nameIndex].isQss(not s.qssState)
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()

def doSetType(self,setName,typeName):
    """ 
    Set the type an indexed object set
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    typeName(string) -- name of a type (preferabbly indexed to our base typeName dictionary)
    """ 
    try:
        if typeName == 'NONE':
            self.setInstances[nameIndex].doSetType()            
        else:
            self.setInstances[nameIndex].doSetType(typeName)	    
    except:
        guiFactory.warning("Set not found.Reloading Gui")
        self.reload()    
        
    
def doUpdateSetName(self,setTextField,nameIndex):
    """ 
    Updates the name of an indexed object set, and updates the gui
    
    Keyword arguments:
    setTextField(string) - name of the text field to update
    nameIndex(int) -- index of an objectSet dictionary
    """ 
    # get the field
    setName = self.setInstances[nameIndex].nameShort
    if not mc.objExists(setName):
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()
        return

    newName = mc.textField(setTextField,q=True,text = True)

    if setName and newName:
	if setName == newName:
	    guiFactory.warning("'%s' already is named what was input."%newName)	    
	else:
	    #Name it
	    attributes.storeInfo(setName,'cgmName',newName)
	    self.setInstances[nameIndex].doName()	
	    buffer = self.setInstances[nameIndex].nameShort
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
# Marking Menu stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Gui stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doSetSetAsActive(self,nameIndex):
    """ 
    Activates active state of an indexed object set, and updates the gui
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """ 
    setName = self.setInstances[nameIndex].nameShort
    if mc.objExists(setName):
        self.ActiveObjectSetsOptionVar.append(setName) 
        self.activeSets.append(setName)
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()

def doSetSetAsInactive(self,nameIndex):
    """ 
    Deactivates active state of an indexed object set, and updates the gui
    
    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """ 
    setName = self.setInstances[nameIndex].nameShort
    if mc.objExists(setName): 
        self.ActiveObjectSetsOptionVar.remove(setName) 
        self.activeSets.remove(setName)
            
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()

def doSetRefState(self,refIndex,value,reset = True):
    """ 
    Establish the ref state of an indexed rererence name, and updates the gui
    
    Keyword arguments:
    refIndex(int) -- index of an refPrefix dictionary
    value(bool) -- state of the ref
    reset(bool) -- whether to reset the gui on success
    
    """ 
    refName = self.refPrefixDict.get(refIndex)
    if refName in self.refPrefixes:
        if value:
            self.ActiveRefsOptionVar.append(refName)
        else:
            self.ActiveRefsOptionVar.remove(refName)
        if reset:
            self.reload()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%refName)
        self.reload()
        
def doSetTypeState(self,typeIndex,value,reset = True):
    """ 
    Establish the type state of an indexed type name, and updates the gui
    
    Keyword arguments:
    typeIndex(int) -- index of an typeDict dictionary
    value(bool) -- state of the ref
    reset(bool) -- whether to reset the gui on success
    """ 
    
    typeName = self.typeDict.get(typeIndex)
    if typeName in self.setTypes:
        if value:
            self.ActiveTypesOptionVar.append(typeName)
        else:
            self.ActiveTypesOptionVar.remove(typeName)
        if reset:
            self.reload()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%typeName)
        self.reload()
        
def guiDoSetType(self,nameIndex,typeName):
    """ Function for the gui call, root function is above """
    try:
	self.setInstances[nameIndex].doSetType(typeName)
	self.reload()
    except:
        guiFactory.warning("Set '%s' doesn't exist.Reloading Gui"%nameIndex)
        self.reload()
	
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Set Group Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def initializeSetGroup(self):
    """ 
    Initializes local set group
    """ 
    # Set Group creation if they don't have em
    if not self.setGroupName or not mc.objExists(self.setGroupName):
        self.setsGroup = SetFactory('Scene','objectSetGroup')
        self.setGroupName = self.setsGroup.nameShort
        if not mc.optionVar( q='cgmVar_HideSetGroups' ):
            self.objectSets.append(self.setsGroup.nameShort)   

def doSetMaintainLocalSetGroup(self):
    """ 
    Initializes maintain local set group mode, creates local set group if it
    doesn't exist, and adds stray sets of they're local
    """     
    self.MaintainLocalSetGroupOptionVar.toggle()
    
    if self.MaintainLocalSetGroupOptionVar.value:
        doGroupLocal(self)
        
        self.reload()
        
def doSetHideSetGroups(self):
    """ 
    Toggles hide set group mode
    """ 
    self.HideSetGroupOptionVar.toggle()
    self.reload()
    
def uiToggleOptionCB(self,optionVar):
    """ 
    Toggles hide set group mode
    """ 
    optionVar.toggle()
    self.reload()
    
def doGroupLocal(self):
    """ 
    Groups local stray object sets
    """ 
    if not self.setGroupName or mc.objExists(self.setGroupName)!=True:
	initializeSetGroup(self)
	guiFactory.report("'%s' created!"%self.setGroupName)	
	
    buffer = self.refSetsDict.get('From Scene')
    for s in buffer:
	if s in self.setInstancesFastIndex.keys():
	    index = self.setInstancesFastIndex[s] 
	    sInstance = self.setInstances[index]
	else:
	    sInstance = SetFactory(s)
	    
	if not sInstance.parents and not sInstance.refState and not sInstance.mayaSetState and s != self.setGroupName:
	    self.setsGroup.store(s)
	    guiFactory.report("'%s' grouped to '%s'!"%(sInstance.nameShort,self.setsGroup.nameShort))	
    guiFactory.report("Local group function complete.")
	    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Multi Set Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def doMultiSetType(self,setMode,typeName):
    """ 
    Sets the type for mutliple sets(active/loaded depending on mode)
    
    Keyword arguments:
    setMode(int) -- loaded/active state
    typeName(string) -- name of typeName
    """ 
    
    if setMode:
        if self.ActiveObjectSetsOptionVar.value:
            for s in self.ActiveObjectSetsOptionVar.value:
		print "Setting Type on %s"%s		
                if s in self.objectSets:
		    index = self.setInstancesFastIndex[s]
		    bufferName = self.setInstances[index].nameShort #store old name
		    self.setInstances[index].doSetType(typeName) #change type
		    self.ActiveObjectSetsOptionVar.remove(bufferName) #remove old name from active list
		    self.ActiveObjectSetsOptionVar.append(self.setInstances[index].nameShort) #add the ndw
		    
	    self.reload()		    
	    
        else:
            guiFactory.warning("No active sets found")
            return
            
    else:
        for s in self.objectSets:
	    index = self.setInstancesFastIndex[s]
	    bufferName = self.setInstances[index].nameShort #store old name
	    self.setInstances[index].doSetType(typeName) #change type
	    self.ActiveObjectSetsOptionVar.remove(bufferName) #remove old name from active list
	    self.ActiveObjectSetsOptionVar.append(self.setInstances[index].nameShort) #add the ndw
	    
	self.reload()		        

def doSetAllSetsAsActive(self):
    """ 
    Activates the active state for mutliple sets
    """ 
    if self.activeSetsCBDict:
        for i in self.activeSetsCBDict.keys(): # for each key
            if self.setInstances[i].nameShort in self.objectSets: #if that indexed set is in our loaded sets
                tmp = self.activeSetsCBDict.get(i) #get the checkbox
                mc.checkBox(tmp, edit = True,
                            value = True)
                doSetSetAsActive(self,i)#set as active

def doSetAllSetsAsInactive(self):
    """ 
    Deactivates the active state for mutliple sets
    """   
    if self.activeSetsCBDict:
        for i in self.activeSetsCBDict.keys(): # for each key
            if self.setInstances[i].nameShort in self.objectSets: #if that indexed set is in our loaded sets
                tmp = self.activeSetsCBDict.get(i) #get the checkbox
                mc.checkBox(tmp, edit = True,
                            value = False)
                doSetSetAsInactive(self,i)#set as active

def doSelectMultiSets(self,setMode):
    """ 
    Selects mutliple sets(active/loaded depending on mode)
    
    Keyword arguments:
    setMode(int) -- loaded/active state
    """ 
    allObjectsList = []    
    try:
	if setMode:
	    if self.ActiveObjectSetsOptionVar.value:
		for s in self.ActiveObjectSetsOptionVar.value:
		    if s in self.objectSets:
			index = self.setInstancesFastIndex[s]	    
			allObjectsList.extend(self.setInstances[index].setList)     
	    else:
		guiFactory.warning("No active sets found")
		return
		
	else:
	    for s in self.objectSets:
		index = self.setInstancesFastIndex[s]	    
		allObjectsList.extend(self.setInstances[index].setList) 
    except:
        guiFactory.warning("Some sets don't exist.Reloading Gui")
        self.reload()	

    if allObjectsList:
        mc.select(allObjectsList)
            
def doKeyMultiSets(self,setMode):
    """ 
    Key mutliple sets(active/loaded depending on mode)
    
    Keyword arguments:
    setMode(int) -- loaded/active state
    """ 
    allObjectsList = []   
    try:
	if setMode:
	    if self.ActiveObjectSetsOptionVar.value:    
		for o in self.ActiveObjectSetsOptionVar.value:
		    if o in self.objectSets:
			index = self.setInstancesFastIndex[o]	    	    
			sInstance = self.setInstances[index]
			
			if self.KeyTypeOptionVar.value:
			    sInstance.key(breakdown = True)
			else:
			    sInstance.key()
			allObjectsList.extend(sInstance.setList)                 
	    else:
		guiFactory.warning("No active sets found")
		return  
	else:
	    for s in self.objectSets:
		index = self.setInstancesFastIndex[s]	    	    
		sInstance = self.setInstances[index]
		
		if self.KeyTypeOptionVar.value:
		    sInstance.key(breakdown = True)
		else:
		    sInstance.key()
		allObjectsList.extend(sInstance.setList)             
    
	if allObjectsList:
	    mc.select(allObjectsList)
    except:
	guiFactory.warning("Some sets don't exist.Reloading Gui")
	self.reload()	    
    
def doDeleteMultiCurrentKeys(self,setMode):
    """ 
    Delete the curret key of mutliple sets(active/loaded depending on mode)
    
    Keyword arguments:
    setMode(int) -- loaded/active state
    """     
    allObjectsList = []      
    try:
	if setMode:
	    if self.ActiveObjectSetsOptionVar.value:    
		for o in self.ActiveObjectSetsOptionVar.value:
		    if o in self.objectSets:
			index = self.setInstancesFastIndex[o]	    	    
			sInstance = self.setInstances[index]
			
			sInstance.deleteCurrentKey()
			allObjectsList.extend(sInstance.setList)                
	    else:
		guiFactory.warning("No active sets found")
		return  
	else:
	    for s in self.objectSets:
		index = self.setInstancesFastIndex[s]	    	    
		sInstance = self.setInstances[index]
		sInstance.deleteCurrentKey()
		allObjectsList.extend(sInstance.setList) 
		
	if allObjectsList:
	    mc.select(allObjectsList) 
	
    except:
	guiFactory.warning("Some sets don't exist.Reloading Gui")
	self.reload()	 
        
def doResetMultiSets(self,setMode):
    """ 
    Reset the objects of mutliple sets(active/loaded depending on mode)
    
    Keyword arguments:
    setMode(int) -- loaded/active state
    """     
    allObjectsList = []   
    try:
	if setMode:
	    if self.ActiveObjectSetsOptionVar.value:    
		for o in self.ActiveObjectSetsOptionVar.value:
		    if o in self.objectSets:
			index = self.setInstancesFastIndex[o]	    	    
			sInstance = self.setInstances[index]
			sInstance.reset()
			allObjectsList.extend(sInstance.setList)                 
	    else:
		guiFactory.warning("No active sets found")
		return  
	else:
	    for s in self.objectSets:
		index = self.setInstancesFastIndex[s]	    	    
		sInstance.reset()
		allObjectsList.extend(sInstance.setList)             
    
	if allObjectsList:
	    mc.select(allObjectsList)
    except:
	guiFactory.warning("Some sets don't exist.Reloading Gui")
	self.reload()	 
               
def doSetAllRefState(self,value):
    """ 
    Toggle the ref state of mutliple refs
    
    Keyword arguments:
    value(int) -- on or off
    """     
    if self.activeRefsCBDict:
        for i in self.activeRefsCBDict.keys():
            tmp = self.activeRefsCBDict.get(i)
            mc.menuItem(tmp,edit = True,cb=value)
            doSetRefState(self,i,value,False)
        self.reload()
        
def doSetAllTypeState(self,value):
    """ 
    Set the the loaded type state of mutliple types
    
    Keyword arguments:
    value(int) -- on or off
    """  
    if self.activeTypesCBDict:
        for i in self.activeTypesCBDict.keys():
            tmp = self.activeTypesCBDict.get(i)
            mc.menuItem(tmp,edit = True,cb=value)
            doSetTypeState(self,i,value,False)
        self.reload()
        
def doMultiSetQss(self,qssState):
    """ 
    Sets the type for mutliple sets(active/loaded depending on mode)
    
    Keyword arguments:
    setMode(int) -- loaded/active state
    typeName(string) -- name of typeName
    """ 
    
    if self.SetToolsModeOptionVar.value:
        if self.ActiveObjectSetsOptionVar.value:
            for s in self.ActiveObjectSetsOptionVar.value:
                if s in self.objectSets:
		    index = self.setInstancesFastIndex[s]
		    self.setInstances[index].isQss(qssState) #change type
	    self.reload()		    
	    
        else:
            guiFactory.warning("No active sets found")
            return
            
    else:
        for s in self.objectSets:
	    index = self.setInstancesFastIndex[s]
	    self.setInstances[index].isQss(qssState) #change type
	self.reload()	   
