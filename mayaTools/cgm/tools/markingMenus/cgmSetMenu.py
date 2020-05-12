import maya.cmds as mc
import maya.mel as mel

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes.SetFactory import *


from cgm.lib import guiFactory
from cgm.lib import search
from cgm.tools.lib import setToolsLib
from cgm.tools import setTools

import cgmToolbox

#reload(setToolsLib)


def run():
	try:
		cgmSetToolsMM = setToolsMarkingMenu()
	except:
		pass
	
class setToolsMarkingMenu(BaseMelWindow):
	_DEFAULT_MENU_PARENT = 'viewPanes'
	
	def __init__(self):	
		"""
		Initializes the pop up menu class call
		"""
		self.optionVars = []		
		self.IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked','int',0)
		self.mmActionOptionVar = OptionVarFactory('cgmVar_mmAction','int',0)
		
		self.setupVariables()
		
		panel = mc.getPanel(up = True)
		if panel:
			# Attempt at fixing a bug of some tools not working when the pop up parent isn't 'viewPanes'
			if 'MayaWindow' in mc.panel(panel,q = True,ctl = True):
				panel = 'viewPanes'
			
		sel = search.selectCheck()
		
		self.IsClickedOptionVar.set(0)
		self.mmActionOptionVar.set(0)
		
		if mc.popupMenu('cgmMM',ex = True):
			mc.deleteUI('cgmMM')
			
		if panel:
			if mc.control(panel, ex = True):
				try:
					mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = panel,
						         pmc = lambda *a: self.createUI('cgmMM'))
				except:
					guiFactory.warning('cgm.setMenu failed!')		

	def createUI(self,parent):
		"""
		Create the UI
		"""		
		
		def buttonAction(command):
			"""
			execute a command and let the menu know not do do the default button action but just kill the ui
			"""			
			killUI()
			command
			mmActionOptionVar.set(1)
		
		
		self.setTypes = ['NONE',
		                 'animation',
		                 'layout',
		                 'modeling',
		                 'td',
		                 'fx',
		                 'lighting']
		self.setModes = ['<<< All Loaded Sets >>>','<<< Active Sets >>>']

		setToolsLib.updateObjectSets(self)	

		loadedCheck = False
		if self.objectSets:
			loadedCheck = True
		
		activeCheck = False
		if self.activeSets:
			activeCheck = True
				
		self.IsClickedOptionVar.set(1)
		
		mc.menu(parent,e = True, deleteAllItems = True)
		MelMenuItem(parent,
		            en = loadedCheck,
		            l = 'Select Loaded',
		            c = Callback(setToolsLib.doSelectMultiSets,self,0),
		            rp = 'N')            
		
		MelMenuItem(parent,
		            en = activeCheck,
		            l = 'Select Active',
		            c = Callback(setToolsLib.doSelectMultiSets,self,1),
		            rp = 'S')
		
		MelMenuItem(parent,
		            en = loadedCheck,
		            l = 'Key Loaded',
		            c = Callback(setToolsLib.doKeyMultiSets,self,0),
		            rp = 'NE')            
		
		MelMenuItem(parent,
		            en = activeCheck,
		            l = 'Key Active',
		            c = Callback(setToolsLib.doKeyMultiSets,self,1),
		            rp = 'SE')
		
		MelMenuItem(parent,
		            en = loadedCheck,
		            l = 'Delete Key (Loaded)',
		            c = Callback(setToolsLib.doDeleteMultiCurrentKeys,self,0),
		            rp = 'NW')            
		
		MelMenuItem(parent,
		            en = activeCheck,
		            l = 'Delete Key (Active)',
		            c = Callback(setToolsLib.doDeleteMultiCurrentKeys,self,1),
		            rp = 'SW')
		
		
		MelMenuItemDiv(parent)
		
		MelMenuItem(parent,l = 'Show Gui',
				    c = lambda *a: self.reset())
		
		#>>> Keying Options
		KeyMenu = MelMenuItem( parent, l='Key type', subMenu=True)
		KeyMenuCollection = MelRadioMenuCollection()
	
		if self.KeyTypeOptionVar.value == 0:
			regKeyOption = True
			bdKeyOption = False
		else:
			regKeyOption = False
			bdKeyOption = True
	
		KeyMenuCollection.createButton(KeyMenu,l=' Reg ',
		                               c= Callback(self.toggleVarAndReset,self.KeyTypeOptionVar),
		                               rb= regKeyOption )
		KeyMenuCollection.createButton(KeyMenu,l=' Breakdown ',
		                               c= Callback(self.toggleVarAndReset,self.KeyTypeOptionVar),
		                               rb= bdKeyOption )


		#Ref menu	
		self.refPrefixDict = {}	
		self.activeRefsCBDict = {}
				
		if self.refPrefixes and len(self.refPrefixes) > 1:
		
			refMenu = MelMenuItem( parent, l='Load Refs:', subMenu=True)
			
				
			MelMenuItem( refMenu, l = 'All',
			             c = Callback(setToolsLib.doSetAllRefState,self,True))				
			MelMenuItemDiv( refMenu )

			
			for i,n in enumerate(self.refPrefixes):
				self.refPrefixDict[i] = n
				
				activeState = False
				
				if self.ActiveRefsOptionVar.value:
					if n in self.ActiveRefsOptionVar.value:
						activeState = True	
							
				tmp = MelMenuItem( refMenu, l = n,
				                   cb = activeState,
				                   c = Callback(setToolsLib.doSetRefState,self,i,not activeState))	
				
				self.activeRefsCBDict[i] = tmp
				
			MelMenuItemDiv( refMenu )
			MelMenuItem( refMenu, l = 'Clear',
			             c = Callback(setToolsLib.doSetAllRefState,self,False))	
			

			
		#Types menu	
		self.typeDict = {}	
		self.activeTypesCBDict = {}
					
		if self.setTypes:
		
			typeMenu = MelMenuItem( parent, l='Load Types: ', subMenu=True)
			
				
			MelMenuItem( typeMenu, l = 'All',
		                 c = Callback(setToolsLib.doSetAllTypeState,self,True))				
			MelMenuItemDiv( typeMenu )

			
			for i,n in enumerate(self.setTypes):
				self.typeDict[i] = n
				
				activeState = False
				
				if self.ActiveTypesOptionVar.value:
					if n in self.ActiveTypesOptionVar.value:
						activeState = True	
							
				tmp = MelMenuItem( typeMenu, l = n,
			                       cb = activeState,
			                       c = Callback(setToolsLib.doSetTypeState,self,i,not activeState))	
				
				self.activeTypesCBDict[i] = tmp
				
			MelMenuItemDiv( typeMenu )
			MelMenuItem( typeMenu, l = 'Clear',
		                 c = Callback(setToolsLib.doSetAllTypeState,self,False))	
		
		#>>> Autohide Options
		HidingMenu = MelMenuItem( parent, l='Auto Hide', subMenu=True)
		
		#guiFactory.appendOptionVarList(self,'cgmVar_MaintainLocalSetGroup')			
		MelMenuItem( HidingMenu, l="Anim Layer Sets",
	                 cb= self.HideAnimLayerSetsOptionVar.value,
	                 c= lambda *a: setToolsLib.uiToggleOptionCB(self,self.HideAnimLayerSetsOptionVar))
		
		MelMenuItem( HidingMenu, l="Maya Sets",
	                 cb= self.HideMayaSetsOptionVar.value,
	                 c= lambda *a: setToolsLib.uiToggleOptionCB(self,self.HideMayaSetsOptionVar))
		
		MelMenuItem( HidingMenu, l="Non Qss Sets",
	                 cb= self.HideNonQssOptionVar.value,
	                 c= lambda *a: setToolsLib.uiToggleOptionCB(self,self.HideNonQssOptionVar))
		
		MelMenuItem( HidingMenu, l="Set Groups",
	                 cb= self.HideSetGroupOptionVar.value,
	                 c= lambda *a: setToolsLib.uiToggleOptionCB(self,self.HideSetGroupOptionVar))
	

		MelMenuItemDiv(parent)
		
		self.objectSetsDict = {}
		self.activeSetsCBDict = {}
		
		maxSets = 10
		
		for i,b in enumerate(self.objectSets[:maxSets]):
			#Store the info to a dict
			self.objectSetsDict[i] = b
			sInstance = SetFactory(b)
			
			#Get check box state
			activeState = False
			if b in self.ActiveObjectSetsOptionVar.value:
				activeState = True
				
			tmpActive = MelMenuItem(parent,
			                        l = b,
		                            annotation = 'Toggle active state and select',
		                            cb = activeState,
			                        c = Callback(setToolsLib.doSelectSetObjects,self,i)
			                        )
			self.activeSetsCBDict[i] = tmpActive	
			
		if len(self.objectSets) >= maxSets:
			MelMenuItem(parent,l = 'More sets...see menu',
			            )			


		MelMenuItemDiv(parent)	
		MelMenuItem(parent, l="Reset",
	                 c=lambda *a: self.reset())
		
	def setupVariables(self):
		self.ActiveObjectSetsOptionVar = OptionVarFactory('cgmVar_activeObjectSets',defaultValue = [''])
		self.ActiveRefsOptionVar = OptionVarFactory('cgmVar_activeRefs',defaultValue = [''])
		self.ActiveTypesOptionVar = OptionVarFactory('cgmVar_activeTypes',defaultValue = [''])
		self.KeyTypeOptionVar = OptionVarFactory('cgmVar_KeyType', defaultValue = 0)
		
		self.HideSetGroupOptionVar = OptionVarFactory('cgmVar_HideSetGroups', defaultValue = 1)
		self.HideNonQssOptionVar = OptionVarFactory('cgmVar_HideNonQss', defaultValue = 1)		
		self.HideAnimLayerSetsOptionVar = OptionVarFactory('cgmVar_HideAnimLayerSets', defaultValue = 1)
		self.HideMayaSetsOptionVar = OptionVarFactory('cgmVar_HideMayaSets', defaultValue = 1)
		
		guiFactory.appendOptionVarList(self,self.ActiveObjectSetsOptionVar.name)
		guiFactory.appendOptionVarList(self,self.ActiveRefsOptionVar.name)
		guiFactory.appendOptionVarList(self,self.ActiveTypesOptionVar.name)
		guiFactory.appendOptionVarList(self,self.KeyTypeOptionVar.name)
		
		guiFactory.appendOptionVarList(self,self.HideSetGroupOptionVar.name)
		guiFactory.appendOptionVarList(self,self.HideNonQssOptionVar.name)		
		guiFactory.appendOptionVarList(self,self.HideAnimLayerSetsOptionVar.name)
		guiFactory.appendOptionVarList(self,self.HideMayaSetsOptionVar.name)		
		
	def reset(self):
		guiFactory.purgeOptionVars(self.optionVars)
		setTools.run()
		
	def reload(self):
		setTools.run()
		
	def toggleVarAndReset(self, optionVar):
		try:
			optionVar.toggle()
			self.reload()
		except:
			print "MM change var and reset failed!"
		
			
		
	
		
def killUI():
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')
	
	if mc.popupMenu('cgmMM',ex = True):
		mc.deleteUI('cgmMM')

			
	IsClickedOptionVar.set(0)
	mmActionOptionVar.set(0)	