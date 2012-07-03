import maya.cmds as mc
import maya.mel as mel

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.ObjectFactory import *

from cgm.lib import guiFactory
from cgm.lib import search
from cgm.tools.lib import animToolsLib
from cgm.tools.lib import tdToolsLib
from cgm.tools.lib import locinatorLib
from cgm.lib import locators

import cgmToolbox

reload(locinatorLib)
reload(tdToolsLib)

def run():
	cgmSnapMM = snapMarkingMenu()
	
class snapMarkingMenu(BaseMelWindow):
	_DEFAULT_MENU_PARENT = 'viewPanes'
	
	def __init__(self):	
		"""
		Initializes the pop up menu class call
		"""
		self.optionVars = []
		self.toolName = 'cgm.snapMM'
		IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
		mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')	
		surfaceSnapAimModeVar = OptionVarFactory('cgmVar_SurfaceSnapAimMode', 'int')	
		UpdateRotateOrderOnTagVar = OptionVarFactory('cgmVar_TaggingUpdateRO', 'int')	
		self.LocinatorUpdateObjectsBufferOptionVar = OptionVarFactory('cgmVar_LocinatorUpdateObjectsBuffer',defaultValue = [''])
		
		self.LocinatorUpdateObjectsOptionVar = OptionVarFactory('cgmVar_SnapMMUpdateMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.LocinatorUpdateObjectsOptionVar.name)
		
		self.SnapModeOptionVar = OptionVarFactory('cgmVar_SnapMMMatchMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.SnapModeOptionVar.name)
				
		
		panel = mc.getPanel(up = True)
		sel = search.selectCheck()
		
		IsClickedOptionVar.set(0)
		mmActionOptionVar.set(0)
		
		if mc.popupMenu('cgmMM',ex = True):
			mc.deleteUI('cgmMM')
			
		if panel:
			if mc.control(panel, ex = True):
				mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = 'viewPanes',
					         pmc = lambda *a: self.createUI('cgmMM'))
	
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
		
		self.LocinatorUpdateObjectsBufferOptionVar = OptionVarFactory('cgmVar_LocinatorUpdateObjectsBuffer',defaultValue = [''])
		IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
		mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')
		
		sel = search.selectCheck()
		selPair = search.checkSelectionLength(2)
		
		IsClickedOptionVar.set(1)
		
		mc.menu(parent,e = True, deleteAllItems = True)
		MelMenuItem(parent,
		            en = selPair,
		            l = 'Point Snap',
		            c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
		            rp = 'NW')		            
		MelMenuItem(parent,
		            en = selPair,
		            l = 'Parent Snap',
		            c = lambda *a:buttonAction(tdToolsLib.doParentSnap()),
		            rp = 'N')	
		MelMenuItem(parent,
		            en = selPair,
		            l = 'Orient Snap',
		            c = lambda *a:buttonAction(tdToolsLib.doOrientSnap()),
		            rp = 'NE')	
		
		MelMenuItem(parent,
		            en = selPair,
		            l = 'Surface Snap',
		            c = lambda *a:buttonAction(tdToolsLib.doSnapClosestPointToSurface(False)),
		            rp = 'W')
		
		if self.LocinatorUpdateObjectsOptionVar.value:
			ShowMatch = False
			if self.LocinatorUpdateObjectsBufferOptionVar.value:
				ShowMatch = True
			MelMenuItem(parent,
				        en = ShowMatch,
				        l = 'Buffer Snap',
				        c = lambda *a:buttonAction(locinatorLib.doUpdateLoc(self,True)),
				        rp = 'S')					
		else:
			ShowMatch = search.matchObjectCheck()			
			MelMenuItem(parent,
				        en = ShowMatch,
				        l = 'Match Snap',
				        c = lambda *a:buttonAction(locinatorLib.doUpdateSelectedObjects(self)),
				        rp = 'S')	
			
		
		MelMenuItem(parent,
		            en = 0,
		            l = 'Mirror',
		            c = lambda *a:buttonAction(locinatorLib.doUpdateObj(self,True)),
		            rp = 'SW')			
		
		MelMenuItemDiv(parent)
		MelMenuItem(parent,l = 'Loc Me',
	                c = lambda *a: buttonAction(locinatorLib.doLocMe(self)))
		MelMenuItem(parent, l = 'Tag Loc to Object',en = selPair,
	                c = lambda *a: buttonAction(locinatorLib.doTagObjects(self)))
		# Update Mode
		UpdateMenu = MelMenuItem(parent, l='Update Mode', subMenu=True)
		UpdateMenuCollection = MelRadioMenuCollection()

		if self.LocinatorUpdateObjectsOptionVar.value == 0:
			slMode = True
			bufferMode = False
		else:
			slMode = False
			bufferMode = True

		UpdateMenuCollection.createButton(UpdateMenu,l='Selected',
				                             c=lambda *a: self.LocinatorUpdateObjectsOptionVar.set(0),
				                             rb=slMode )
		UpdateMenuCollection.createButton(UpdateMenu,l='Buffer',
				                             c=lambda *a:self.LocinatorUpdateObjectsOptionVar.set(1),
				                             rb=bufferMode )
		#>>>Match Mode
		self.MatchModeOptions = ['parent','point','orient']
		
		self.MatchModeCollection = MelRadioMenuCollection()
		self.MatchModeCollectionChoices = []
					
		MatchModeMenu = MelMenuItem( parent, l='Match Mode', subMenu=True)
		self.matchMode = self.SnapModeOptionVar.value
		for c,item in enumerate(self.MatchModeOptions):
			if self.matchMode == c:
				rbValue = True
			else:
				rbValue = False
			self.MatchModeCollectionChoices.append(self.MatchModeCollection.createButton(MatchModeMenu,label=item,
			                                                                             rb = rbValue,
			                                                                             command = Callback(self.SnapModeOptionVar.set,c)))
		#>>> Define
		DefineMenu = MelMenuItem( parent, l='Buffer', subMenu=True)
		MelMenuItem( DefineMenu, l="Define",
		             c= lambda *a: locinatorLib.defineObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		MelMenuItem( DefineMenu, l="Add Selected",
		             c= lambda *a: locinatorLib.addSelectedToObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		MelMenuItem( DefineMenu, l="Remove Selected",
		             c= lambda *a: locinatorLib.removeSelectedFromObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		MelMenuItemDiv( DefineMenu )
		MelMenuItem( DefineMenu, l="Select Members",
				     c= lambda *a: locinatorLib.selectObjBufferMembers(self.LocinatorUpdateObjectsBufferOptionVar))
		MelMenuItem( DefineMenu, l="Clear",
		             c= lambda *a: locinatorLib.clearObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
				
		
		
		
		
		MelMenuItemDiv(parent)		
		MelMenuItem(parent, l = 'Locinator',
	                c = lambda *a: buttonAction(cgmToolbox.loadLocinator()))
		MelMenuItem(parent, l = 'cgm.animTools',
	                c = lambda *a: buttonAction(cgmToolbox.loadAnimTools()))
		MelMenuItem(parent, l = 'cgm.tdTools',
	                c = lambda *a: buttonAction(cgmToolbox.loadTDTools()))
		MelMenuItem(parent, l = 'cgm.attrTools',
	                c = lambda *a: buttonAction(cgmToolbox.loadAttrTools()))
		

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
