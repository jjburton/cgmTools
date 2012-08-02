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
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel
import subprocess

from cgm.lib.cgmBaseMelUI import *
from cgm.lib.classes.SetFactory import *
from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes import NameFactory
from cgm.rigger import PuppetFactory
from cgm.lib.classes import AttrFactory
from cgm.rigger.lib import functions
reload(AttrFactory)
reload(NameFactory)
reload(PuppetFactory)

from cgm.rigger.PuppetFactory import *
from cgm.rigger.lib.Limb.module import *


from cgm.lib import (search,guiFactory,lists,modules)
reload(search)
reload(guiFactory)

"""

"""
def verifyPuppet(self):
    try:
	self.Puppet.verify()
	self.Puppet.getModules()
	updateUIPuppet(self)
	self.updateModulesUI()	
	updateHelpUI(self)	
    except:
        guiFactory.warning("'%s' failed to verify"%self.Puppet.nameBase)
	
	
def initializePuppet(self):
    try:
	self.Puppet.initialize()
	updateUIPuppet(self)
	self.updateModulesUI()
	updateHelpUI(self)	
    except:
        guiFactory.warning("'%s' failed to initialize"%self.Puppet.nameBase)
	
def deletePuppet(self):
    try:
	self.Puppet.delete()
	self.Puppet = False
	updateUIPuppet(self)
	self.updateModulesUI()
	updateHelpUI(self)
    except:
        self.Puppet = False	
        guiFactory.warning("'%s' failed to delete"%self.Puppet.nameBase)
	
def doPuppetCreate(self):
    #mel.eval('python("cgmTmp = PuppetFactory();cgmPuppet.__dict__[cgmTmp.nameBase] = cgmTmp")')	    
    self.Puppet = PuppetFactory()
    self.PuppetBridge[self.Puppet.PuppetNull.nameBase] = self.Puppet #Store it to the bridge
    
    updateUIPuppet(self)
    self.updateModulesUI()
    """
    except:
        self.Puppet = False
        guiFactory.warning("Failed to create puppet. Check the woodshop.")"""
	
def activatePuppet(self,name):
    try:
	if name in self.PuppetBridge.keys(): # if the puppet is instanced to our bridge, just link it up
	    self.Puppet = self.PuppetBridge[name]
	else:
	    self.Puppet = PuppetFactory(name)
	    self.PuppetBridge[self.Puppet.PuppetNull.nameBase] = self.Puppet #Store it to the bridge
	    
	
    except:
        self.Puppet = False
        guiFactory.warning("'%s' failed to activate"%name)
    
    updateUIPuppet(self)
    self.updateModulesUI()	
    
def updateUIPuppet(self):
    if not self.Puppet:
        self.MasterPuppetTF(edit=True, text = '') 
	
	for uiItem in self.UI_StateRows['define']:
	    uiItem(edit = True, vis = False)	
	
	for k in self.puppetStateButtonsDict.keys():
	    self.puppetStateButtonsDict[k](edit = True, en=False)
	
	updatePuppetUIReport(self) 
	self.updateModulesUI()
        return
    
    self.MasterPuppetTF(edit=True, text = self.Puppet.nameBase)
    
    self.puppetStateButtonsDict[0](edit=True,en=True)
    
    for uiItem in self.UI_StateRows['define']:
	uiItem(edit = True, vis = True)
	
    self.PuppetModeOptionVar.set(self.Puppet.optionPuppetMode.value)
    self.PuppetAimOptionVar.set(self.Puppet.optionAimAxis.value)
    self.PuppetUpOptionVar.set(self.Puppet.optionUpAxis.value)
    self.PuppetOutOptionVar.set(self.Puppet.optionOutAxis.value)
    
    mc.radioCollection(self.PuppetModeCollection ,edit=True,sl= (self.PuppetModeCollectionChoices[ self.Puppet.optionPuppetMode.value ]))
    
    updatePuppetUIReport(self) 
    self.updateModulesUI()
    
def activeAndUpdatePuppet(self, name = ''):
    activatePuppet(self,name)
    updateUIPuppet(self)
    self.updateModulesUI()
     

def updatePuppetName(self):
    """ 
    Sets string value of a loaded attr in the modify menu
    """  
    #>>> Variables
    varCheck = self.MasterPuppetTF(q=True,text=True)
    if self.Puppet:
        if varCheck:
            try:
		oldName = self.Puppet.nameBase
                self.Puppet.doRenamePuppet(varCheck)
		self.PuppetBridge.pop(oldName)
		self.PuppetBridge[varCheck] = self.Puppet
            except:		
                pass
			
def updatePuppetUIReport(self):
    buildReport = []
	    
    if not self.Puppet:
	self.puppetReport(edit=True, label = '...')
	return
    state = self.Puppet.getState()
    #build master report
    if state == 0:
	if not self.Puppet.geo:
	    buildReport.append('No geo defined')
	else:
	    buildReport.append('%i geo items'%len(self.Puppet.geo))
	
	if not self.Puppet.ModulesBuffer.bufferList:
	    buildReport.append('0 modules')
	else:
	    buildReport.append('%i modules'%len(self.Puppet.ModulesBuffer.bufferList))
	    
	if not self.Puppet.templateSizeObjects:
	    buildReport.append('No size template')
    elif state == 1:
	buildReport.append('Template mode!')
    elif state == 2:
	buildReport.append('Deform mode!')
    elif state == 3:
	buildReport.append('Rig mode!')
    else:
	buildReport.append('No idea what state this is')
    

    if buildReport:
	    self.puppetReport(edit = True, label = ' | '.join(buildReport))
	    
    updateHelpUI(self)
	    
	    
def updateHelpUI(self):
    buildReport = []
	    
    if not self.Puppet:
	self.helpInfo(edit=True, label = 'Try adding a Puppet')
			    
    #Initial State help
    state = self.Puppet.getState()
    
    if state == 0:
	if not self.Puppet.geo:
	    self.helpInfo(edit=True, label = 'Need some geo')
	    return
	    
	if not self.Puppet.templateSizeObjects:
	    self.helpInfo(edit=True, label = 'Add a size template')
	    return
	
	if not self.Puppet.modules:
	    self.helpInfo(edit=True, label = 'Need at least one module')
	    return
	
    elif state == 1:
	self.helpInfo(edit=True, label = 'Template mode!')
	
    elif state == 2:
	self.helpInfo(edit=True, label = 'Deform mode!')
	
    elif state == 3:
	self.helpInfo(edit=True, label = 'Rig mode!')
	
    else:
	self.helpInfo(edit=True, label = 'No idea what state this is...')
	
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Define
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doAddGeo(self):
    self.Puppet.addGeo()
    updatePuppetUIReport(self)
    
def setPuppetBaseMode(self,i):
    if self.Puppet:
	self.Puppet.optionPuppetMode.set(i)
    self.PuppetModeOptionVar.set(i)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Axis
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def setPuppetAxisAim(self,i):
    if self.Puppet:
	self.Puppet.doSetAimAxis(i)
	updatePuppetAxisMenus(self)
    
def setPuppetAxisUp(self,i):
    if self.Puppet:
	self.Puppet.doSetUpAxis(i)
	updatePuppetAxisMenus(self)
    
def setPuppetAxisOut(self,i):
    if self.Puppet:
	self.Puppet.doSetOutAxis(i)
	updatePuppetAxisMenus(self)
    
def updatePuppetAxisMenus(self):
    if self.Puppet:
	self.PuppetAimOptionVar.set(self.Puppet.optionAimAxis.value)
	self.PuppetUpOptionVar.set(self.Puppet.optionUpAxis.value)
	self.PuppetOutOptionVar.set(self.Puppet.optionOutAxis.value)    
	mc.radioCollection(self.AimAxisCollection ,edit=True,sl= (self.AimAxisCollectionChoices[ (self.PuppetAimOptionVar.value) ]))
	mc.radioCollection(self.UpAxisCollection ,edit=True,sl= (self.UpAxisCollectionChoices[ (self.PuppetUpOptionVar.value) ]))
	mc.radioCollection(self.OutAxisCollection ,edit=True,sl= (self.OutAxisCollectionChoices[ (self.PuppetOutOptionVar.value) ]))

def doSetAxisAndUpdateModule(self,function,instance,index):
    function(instance,index)
    self.updateModulesUI()
    
def doCopyAxisFromParent(self,moduleInstance):
    """
    Self should be a module instance
    """
    parent = moduleInstance.msgModuleParent.get()
    if not parent:
	functions.copyAxisOptions(moduleInstance,self.Puppet)
	guiFactory.report("Copied axis settings for '%s' from '%s'"%(moduleInstance.nameBase,self.Puppet.nameBase))	
    else:
	guiFactory.warning("Not implemented")
    self.updateModulesUI()	
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def addModule(self,moduleType):
    if self.Puppet:
	self.Puppet.createModule(moduleType.lower())
	updateUIPuppet(self)
	self.updateModulesUI()
	

def doRemoveModule(self,nameIndex):
    """ 
    Duplicate an indexed object set and reload the gui

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    moduleName = self.Puppet.ModulesBuffer.bufferList[nameIndex]
    if mc.objExists(moduleName):
	self.Puppet.removeModule(moduleName)
	updatePuppetUIReport(self)	
	self.updateModulesUI()	
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%moduleName)
	self.updateModulesUI()
	
def doDeleteModule(self,nameIndex):
    """ 
    Duplicate an indexed object set and reload the gui

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    moduleName = self.Puppet.ModulesBuffer.bufferList[nameIndex]
    if mc.objExists(moduleName):
	self.Puppet.deleteModule(moduleName)
	updatePuppetUIReport(self)	
	self.updateModulesUI()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%moduleName)
	self.updateModulesUI()

def doBuildSizeTemplate(self):
    self.Puppet.verifyTemplateSizeObject(True)
    updatePuppetUIReport(self)
	
def uiUpdateBaseName(self,index):  
    """ 
    Sets the default value of a loaded attr in the modify menu
    """  
    #>>> Variables
    if self.moduleBaseNameFields[index]:
	varCheck = self.moduleBaseNameFields[index](q=True,text=True)
	if varCheck != self.Puppet.Module[index].nameBase:    
	    #Rename it
	    moduleName = self.Puppet.ModulesBuffer.bufferList[index]
	    self.Puppet.changeModuleCGMTag(moduleName,'cgmName',varCheck)	    
	    uiModuleUpdateFrameLabel(self,index)
	else:
	    guiFactory.report("'%s' is already the baseName" %varCheck)
    else:
	guiFactory.warning("No connected field found. Try reloading the GUI")
	
def uiModuleUpdateFrameLabel(self,index):
    buffer = ["'%s'"%self.Puppet.ModulesBuffer.bufferList[index]]
    if not self.Puppet.Module[index].moduleParent:
	buffer.append( "Root")
    buffer.append("typ: %s"%self.Puppet.Module[index].afModuleType.value)
    buffer.append("state: %s"%self.Puppet.Module[index].getState())
    
    
    color = dictionary.guiDirectionColors['center']
    if self.Puppet.Module[index].ModuleNull.cgm['cgmDirection'] in dictionary.guiDirectionColors.keys():
	color = dictionary.guiDirectionColors[ self.Puppet.Module[index].ModuleNull.cgm['cgmDirection'] ]
    
    self.moduleFrames[index](edit=True,l=' | '.join(buffer),
                             bgc = color)


def uiModuleUpdateIntAttrFromField(self,fieldsDict,attrClassInstanceName,index):  
    """ 
    Sets the default value of a loaded attr in the modify menu
    """  
    #>>> Variables
    if fieldsDict[index]:
	varCheck = fieldsDict[index](q=True,value=True)
	if varCheck != self.Puppet.Module[index].__dict__[attrClassInstanceName].value:    
	    self.Puppet.Module[index].__dict__[attrClassInstanceName].set(varCheck)
	else:
	    guiFactory.report("'%s' is already the value" %varCheck)
    else:
	guiFactory.warning("No connected field found. Try reloading the GUI")
	
	
def uiModuleToggleBool(self,attrClassInstanceName,index):  
    """ 
    Sets the default value of a loaded attr in the modify menu
    """  
    #>>> Variables
    if self.Puppet.Module[index] and attrClassInstanceName in self.Puppet.Module[index].__dict__.keys():
	self.Puppet.Module[index].__dict__[attrClassInstanceName].set( not self.Puppet.Module[index].__dict__[attrClassInstanceName].value )
    else:
	guiFactory.warning("No idea what this is. Try reloading the GUI")
		
def uiModuleOptionMenuSet(self,OptionMenuDictInstance,MenuSourceList,tag,index):  
    """ 
    Sets the default value of a loaded attr in the modify menu
    """  
    #>>> Variables
    dataIndex =  OptionMenuDictInstance[index](q=True, select=True) -1
    data = MenuSourceList[dataIndex]
    if self.Puppet.Module[index]:
	print data
	if data:
	    moduleName = self.Puppet.ModulesBuffer.bufferList[index]	    
	    self.Puppet.changeModuleCGMTag(moduleName,tag,data)	    
	    uiModuleUpdateFrameLabel(self,index)	    
    else:
	guiFactory.warning("No module found. Try reloading the GUI")




	    
def uiForceModuleUpdateUI(self):  
    self.updateModulesUI()	    
    updatePuppetUIReport(self)
    updateHelpUI(self)













def printReport(self):
    """ 
    Generates a report for the objectSets as the tool sees them.    
    """    
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

    print "# Active Refs: "
    if self.ActiveRefsOptionVar.value:   
        for o in self.ActiveRefsOptionVar.value:
            if o:
                print "#    '%s'"%o
    else:
        print "#    None"



    print "# Active Types: "
    if self.ActiveTypesOptionVar.value:    
        for o in self.ActiveTypesOptionVar.value:
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
    self.refPrefixes = []
    self.refSetsDict = {'From Scene':[]}
    self.setTypesDict = {}
    for t in self.setTypes:
        self.setTypesDict[t] = []
    self.sortedSets = []
    self.objectSets = []
    self.setGroupName = False
    self.setGroups = []
    self.activeSets = []

    if self.objectSetsRaw:
        for o in self.objectSetsRaw:
            sInstance = SetFactory(o)
            # if it's an object set group, add it to our list
            if sInstance.setType == 'objectSetGroup':
                self.setGroups.append(sInstance.nameShort)

            # Get our reference prefixes and sets sorted out
            if sInstance.refState:
                if sInstance.refPrefix in self.refSetsDict.keys():
                    self.refSetsDict[sInstance.refPrefix].append(o)
                else:
                    self.refSetsDict[sInstance.refPrefix] = [o]
            else:
                self.refSetsDict['From Scene'].append(o)
                # See if we have a scene set group and if so, initialize
                if sInstance.setType == 'objectSetGroup':
                    self.setsGroup = SetFactory(o)
                    self.setGroupName = self.setsGroup.nameShort

            # Get our type tags, if none assign 'NONE'
            if sInstance.setType:
                if sInstance.setType in self.setTypesDict.keys():
                    self.setTypesDict[sInstance.setType].append(o)
                else:
                    self.setTypesDict['NONE'].append(o)     
            else:
                self.setTypesDict['NONE'].append(o)


        if self.refSetsDict.keys():
            self.refPrefixes.extend( self.refSetsDict.keys() )


        self.sortedSets = []

        #Sort for activeRefs
        tmpActiveRefSets = []
        if self.refSetsDict.keys() and self.ActiveRefsOptionVar.value:
            for r in self.refSetsDict.keys():
                #If value, let's add or subtract based on if our set refs are found
                if r in self.ActiveRefsOptionVar.value and self.refSetsDict.get(r):
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

    if self.sortedSets:
        self.objectSets = self.sortedSets
    else:
        self.objectSets = self.objectSetsRaw

    if self.ActiveObjectSetsOptionVar.value:
        loadedActiveBuffer = []
        for o in self.objectSets:
            if o in self.ActiveObjectSetsOptionVar.value:
                self.activeSets.append(o)

    # Set Group creation if they don't have em
    if mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ) and not self.setGroupName:
        initializeSetGroup(self)

    if mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ):
        doGroupLocal(self)

    # Hide Set groups
    if mc.optionVar(q='cgmVar_HideSetGroups'):
        for s in self.setGroups:
            if s in self.objectSets:
                self.objectSets.remove(s)

    # Hide animLayer Sets
    if mc.optionVar(q='cgmVar_HideAnimLayerSets'):
        for s in self.setGroups:
            if s in self.objectSets and search.returnObjectType(s) == 'animLayer':
                self.objectSets.remove(s)

    # Hide Maya Sets
    if mc.optionVar(q='cgmVar_HideMayaSets'):
        for s in ['defaultCreaseDataSet',
                  'defaultObjectSet',
                  'defaultLightSet',
                  'initialParticleSE',
                  'initialShadingGroup']:
            if s in self.objectSets:
                self.objectSets.remove(s)

        for s in self.objectSets:
            if 'tweakSet' in s:
                self.objectSets.remove(s)




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Individual Set Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doSelectSetObjects(self,nameIndex):
    """ 
    Selectes the objects of an indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.select()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()


def doAddSelected(self,nameIndex):
    """ 
    Adds selected objects to an indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.doStoreSelected()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()


def doRemoveSelected(self,nameIndex):
    """ 
    Removes selected objects to an indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.doRemoveSelected()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()


def doKeySet(self,nameIndex):
    """ 
    Keys the objects of an indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """      
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        if self.KeyTypeOptionVar.value:
            s.key(breakdown = True)
        else:
            s.key()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()

def doResetSet(self,nameIndex):
    """ 
    Reset the objects of an indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary

    Note - the reset funtion utilizes Morgan Loomis' ml_resetChannels function
    """   
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.reset()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()

def doDeleteCurrentSetKey(self,nameIndex):
    """ 
    Delete the current frame keys from the objects of an indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """       
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.deleteCurrentKey()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()


def doPurgeSet(self,nameIndex):
    """ 
    Purge the objects of an indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """    
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.purge()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
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
    setName = self.objectSetsDict.get(nameIndex) 
    if mc.objExists(setName):
        mc.delete(setName)
        self.reload()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()

def doCopySet(self,nameIndex):
    """ 
    Duplicate an indexed object set and reload the gui

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """  
    setName = self.objectSetsDict.get(nameIndex) 
    if mc.objExists(setName):
        s = SetFactory(self.objectSetsDict.get(nameIndex))
        s.copy()
        self.reload()
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()

def doToggleQssState(self,nameIndex):
    """ 
    Toggle the qss state of a indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    """ 
    setName = self.objectSetsDict.get(nameIndex)
    if mc.objExists(setName):
        s = SetFactory(setName)
        s.isQss(not s.qssState)
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()

def doSetType(self,setName,typeName):
    """ 
    Set the type an indexed object set

    Keyword arguments:
    nameIndex(int) -- index of an objectSet dictionary
    typeName(string) -- name of a type (preferabbly indexed to our base typeName dictionary)
    """ 
    if mc.objExists(setName):
        s = SetFactory(setName)
        if typeName == 'NONE':
            s.doSetType()            
        else:
            s.doSetType(typeName)
    else:
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()


def doUpdateSetName(self,setTextField,nameIndex):
    """ 
    Updates the name of an indexed object set, and updates the gui

    Keyword arguments:
    setTextField(string) - name of the text field to update
    nameIndex(int) -- index of an objectSet dictionary
    """ 
    # get the field
    setName = self.objectSetsDict.get(nameIndex)
    if not mc.objExists(setName):
        guiFactory.warning("'%s' doesn't exist.Reloading Gui"%setName)
        self.reload()
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
    setName = self.objectSetsDict.get(nameIndex)
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
    setName = self.objectSetsDict.get(nameIndex)
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
    setName = self.objectSetsDict.get(nameIndex)
    doSetType(self,setName,typeName)
    self.reload()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Set Group Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
def initializeSetGroup(self):
    """ 
    Initializes local set group
    """ 
    # Set Group creation if they don't have em
    if not self.setGroupName:
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
        if not self.setGroupName:
            initializeSetGroup(self)
        buffer = self.refSetsDict.get('From Scene')
        for s in buffer:
            sInstance = SetFactory(s)
            if not sInstance.parents:
                self.setsGroup.store(s)

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
    if not self.setGroupName:
        initializeSetGroup(self)
    buffer = self.refSetsDict.get('From Scene')
    for s in buffer:
        sInstance = SetFactory(s)
        if not sInstance.parents:
            self.setsGroup.store(s)


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
                if s in self.objectSets and s in self.refSetsDict.get('From Scene'):
                    doSetType(self,s,typeName)
            self.reload()

        else:
            guiFactory.warning("No active sets found")
            return

    else:
        for s in self.objectSets:
            if s in self.refSetsDict.get('From Scene'):
                doSetType(self,s,typeName)      
        self.reload()



def doSetAllSetsAsActive(self):
    """ 
    Activates the active state for mutliple sets
    """ 
    if self.activeSetsCBDict:
        for i,s in enumerate(self.activeSetsCBDict.keys()):
            if self.objectSetsDict.get(i) in self.objectSets:
                tmp = self.activeSetsCBDict.get(s)          
                mc.checkBox(tmp, edit = True,
                            value = True)
                doSetSetAsActive(self,i)

def doSetAllSetsAsInactive(self):
    """ 
    Deactivates the active state for mutliple sets
    """     
    if self.activeSetsCBDict:
        for i,s in enumerate(self.activeSetsCBDict.keys()):
            if self.objectSetsDict.get(i) in self.objectSets:
                tmp = self.activeSetsCBDict.get(s)                        
                mc.checkBox(tmp, edit = True,
                            value = False)
                doSetSetAsInactive(self,i)

def doSelectMultiSets(self,setMode):
    """ 
    Selects mutliple sets(active/loaded depending on mode)

    Keyword arguments:
    setMode(int) -- loaded/active state
    """ 
    allObjectsList = []            
    if setMode:
        if self.ActiveObjectSetsOptionVar.value:
            for o in self.ActiveObjectSetsOptionVar.value:
                if o in self.objectSets:
                    s = SetFactory(o)
                    allObjectsList.extend(s.setList)     
        else:
            guiFactory.warning("No active sets found")
            return

    else:
        for s in self.objectSets:
            sInstance = SetFactory(s)
            allObjectsList.extend(sInstance.setList) 

    if allObjectsList:
        mc.select(allObjectsList)

def doKeyMultiSets(self,setMode):
    """ 
    Key mutliple sets(active/loaded depending on mode)

    Keyword arguments:
    setMode(int) -- loaded/active state
    """ 
    allObjectsList = []   

    if setMode:
        if self.ActiveObjectSetsOptionVar.value:    
            for o in self.ActiveObjectSetsOptionVar.value:
                if o in self.objectSets:
                    sInstance = SetFactory(o)
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
            sInstance = SetFactory(s)
            if self.KeyTypeOptionVar.value:
                sInstance.key(breakdown = True)
            else:
                sInstance.key()
            allObjectsList.extend(sInstance.setList)             

    if allObjectsList:
        mc.select(allObjectsList)

def doDeleteMultiCurrentKeys(self,setMode):
    """ 
    Delete the curret key of mutliple sets(active/loaded depending on mode)

    Keyword arguments:
    setMode(int) -- loaded/active state
    """     
    allObjectsList = []      

    if setMode:
        if self.ActiveObjectSetsOptionVar.value:    
            for o in self.ActiveObjectSetsOptionVar.value:
                if o in self.objectSets:
                    sInstance = SetFactory(o)
                    sInstance.deleteCurrentKey()
                    allObjectsList.extend(sInstance.setList)                
        else:
            guiFactory.warning("No active sets found")
            return  
    else:
        for s in self.objectSets:
            sInstance = SetFactory(s)
            sInstance.deleteCurrentKey()
            allObjectsList.extend(sInstance.setList) 

    if allObjectsList:
        mc.select(allObjectsList) 

def doResetMultiSets(self,setMode):
    """ 
    Reset the objects of mutliple sets(active/loaded depending on mode)

    Keyword arguments:
    setMode(int) -- loaded/active state
    """     
    allObjectsList = []   

    if setMode:
        if self.ActiveObjectSetsOptionVar.value:    
            for o in self.ActiveObjectSetsOptionVar.value:
                if o in self.objectSets:
                    s = SetFactory(o)
                    s.reset()
                    allObjectsList.extend(s.setList)                 
        else:
            guiFactory.warning("No active sets found")
            return  
    else:
        for s in self.objectSets:
            sInstance = SetFactory(s)
            sInstance.reset()
            allObjectsList.extend(sInstance.setList)             

    if allObjectsList:
        mc.select(allObjectsList)

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

