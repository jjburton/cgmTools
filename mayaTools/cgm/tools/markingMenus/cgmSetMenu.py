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

reload(setToolsLib)


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
		IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int',0)
		mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int',0)			
			
		panel = mc.getPanel(up = True)
		if panel:
			# Attempt at fixing a bug of some tools not working when the pop up parent isn't 'viewPanes'
			if 'MayaWindow' in mc.panel(panel,q = True,ctl = True):
				panel = 'viewPanes'
			
		sel = search.selectCheck()
		
		IsClickedOptionVar.set(0)
		mmActionOptionVar.set(0)
		
		if mc.popupMenu('cgmMM',ex = True):
			mc.deleteUI('cgmMM')
			
		if panel:
			if mc.control(panel, ex = True):
				try:
					mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = panel,
						         pmc = lambda *a: self.createUI('cgmMM'))
				except:
					pass		

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
		
		IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
		mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')
		
		self.ActiveObjectSetsOptionVar = OptionVarFactory('cgmVar_activeObjectSets','string')
		self.ActiveRefsOptionVar = OptionVarFactory('cgmVar_activeRefs','string')
		self.ActiveTypesOptionVar = OptionVarFactory('cgmVar_activeTypes','string')
			
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
		if self.ActiveObjectSetsOptionVar.value:
			activeCheck = True
				
		IsClickedOptionVar.set(1)
		
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
				    c = lambda *a: setTools.run())
		MelMenuItemDiv(parent)
		
		self.objectSetsDict = {}
		self.activeSetsCBDict = {}
		for i,b in enumerate(self.objectSets):
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


		MelMenuItemDiv(parent)	
		MelMenuItem(parent, l="Reset",
	                 c=lambda *a: guiFactory.resetGuiInstanceOptionVars(self.optionVars))
			
		
	
		
def killUI():
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')
	
	if mc.popupMenu('cgmMM',ex = True):
		mc.deleteUI('cgmMM')

			
	IsClickedOptionVar.set(0)
	mmActionOptionVar.set(0)	