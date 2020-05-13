import maya.cmds as mc
import maya.mel as mel

#from cgm.lib.zoo.zooPyMaya.baseMelUI import *
#from cgm.lib.classes.cgmMeta.cgmOptionVar import *
#from cgm.lib.classes.ObjectFactory import *
import cgm.core.cgm_Meta as cgmMeta
import cgm.core.lib.zoo.baseMelUI as mUI

from cgm.lib import guiFactory
from cgm.lib import search
from cgm.tools.lib import animToolsLib
from cgm.tools.lib import tdToolsLib
from cgm.tools.lib import locinatorLib
from cgm.lib import locators
from cgm.core.classes import DraggerContextFactory as cgmDrag
#reload(cgmDrag)
import cgmToolbox
#reload(cgmToolbox)
#reload(locinatorLib)
#reload(tdToolsLib)

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def run():
	cgmSnapMM = snapMarkingMenu()
	
class snapMarkingMenu(mUI.BaseMelWindow):
	
	def __init__(self):	
		"""
		Initializes the pop up menu class call
		"""
		self._str_MM = 'snapMarkingMenu'
		self.optionVars = []
		self.toolName = 'cgm.snapMM'
		IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked', 'int')
		mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction', 'int')	
		surfaceSnapAimModeVar = cgmMeta.cgmOptionVar('cgmVar_SurfaceSnapAimMode', 'int')	
		UpdateRotateOrderOnTagVar = cgmMeta.cgmOptionVar('cgmVar_TaggingUpdateRO', 'int')	
		self.LocinatorUpdateObjectsBufferOptionVar = cgmMeta.cgmOptionVar('cgmVar_LocinatorUpdateObjectsBuffer',defaultValue = [''])
		
		self.LocinatorUpdateObjectsOptionVar = cgmMeta.cgmOptionVar('cgmVar_SnapMMUpdateMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.LocinatorUpdateObjectsOptionVar.name)
		
		self.SnapModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_SnapMatchMode',defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.SnapModeOptionVar.name)
						
		IsClickedOptionVar.setValue(0)
		mmActionOptionVar.setValue(0)
		
		#if mc.popupMenu('cgmMM',ex = True):
			#mc.deleteUI('cgmMM')#...deleting ui elements seems to be hard crashing maya 2017
			
		
		_p = mc.getPanel(up = True)
		if _p is None:
			log.error("No panel detected...")
			return 
		if _p:
			log.info("{0} panel under pointer {1}...".format(self._str_MM, _p))                    
			_parentPanel = mc.panel(_p,q = True,ctl = True)
			log.info("{0} panel under pointer {1} | parent: {2}...".format(self._str_MM, _p,_parentPanel))
			if 'MayaWindow' in _parentPanel:
				_p = 'viewPanes' 
		if not mc.control(_p, ex = True):
			raise ValueError,"{0} doesn't exist!".format(_p)
			#_p = panel
		if not mc.popupMenu('cgmMM',ex = True):
			mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = _p,
			             pmc = lambda *a: self.createUI('cgmMM'), postMenuCommandOnce = True)
		else:
			mc.popupMenu('cgmMM', edit = True, ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = _p,
			              pmc = lambda *a: self.createUI('cgmMM'), postMenuCommandOnce = True)
	
	def createUI(self,parent):
		"""
		Create the UI
		"""		
		def buttonAction(command):
			"""
			execute a command and let the menu know not do do the default button action but just kill the ui
			"""			
			killUI()
			mmActionOptionVar.value = 1			
			command
			
		
		self.LocinatorUpdateObjectsBufferOptionVar = cgmMeta.cgmOptionVar('cgmVar_LocinatorUpdateObjectsBuffer',defaultValue = [''])
		IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked', 'int')
		mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction', 'int')
		
		self.SnapModeOptionVar.update()#Check if another tool has changed this setting
		
		_sel = mc.ls(sl=True)
		selPair = search.checkSelectionLength(2)
		_selecCheck = len(_sel)
		IsClickedOptionVar.value = 1
		
		mc.menu(parent,e = True, deleteAllItems = True)
		mUI.MelMenuItem(parent,
		            en = selPair,
		            l = 'Point Snap',
		            c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
		            rp = 'NW')		            
		mUI.MelMenuItem(parent,
		            en = selPair,
		            l = 'Parent Snap',
		            c = lambda *a:buttonAction(tdToolsLib.doParentSnap()),
		            rp = 'N')	
		mUI.MelMenuItem(parent,
		            en = selPair,
		            l = 'Orient Snap',
		            c = lambda *a:buttonAction(tdToolsLib.doOrientSnap()),
		            rp = 'NE')	
		
		mUI.MelMenuItem(parent,
		            en = selPair,
		            l = 'Surface Snap',
		            c = lambda *a:buttonAction(tdToolsLib.doSnapClosestPointToSurface(False)),
		            rp = 'W')
		
		if self.LocinatorUpdateObjectsOptionVar.value:
			ShowMatch = False
			if self.LocinatorUpdateObjectsBufferOptionVar.value:
				ShowMatch = True
			mUI.MelMenuItem(parent,
				        en = ShowMatch,
				        l = 'Buffer Snap',
				        c = lambda *a:buttonAction(locinatorLib.doUpdateLoc(self,True)),
				        rp = 'S')					
		else:
			ShowMatch = search.matchObjectCheck()			
			mUI.MelMenuItem(parent,
				        en = ShowMatch,
				        l = 'Match Snap',
				        c = lambda *a:buttonAction(locinatorLib.doUpdateSelectedObjects(self)),
				        rp = 'S')	
			
		mUI.MelMenuItem(parent,
	                en = _selecCheck,
	                l = 'RayCast',
	                #c = mUI.Callback(buttonAction,raySnap_start(_sel)),		            
	                c = lambda *a:buttonAction(raySnap_start(_sel)),
	                rp = 'SW')				
		mUI.MelMenuItem(parent,
		            en = 0,
		            l = 'Mirror',
		            c = lambda *a:buttonAction(locinatorLib.doUpdateObj(self,True)),
		            rp = 'SE')			
		
		mUI.MelMenuItemDiv(parent)
		mUI.MelMenuItem(parent,l = 'Loc Me',
	                c = lambda *a: buttonAction(locinatorLib.doLocMe(self)))
		mUI.MelMenuItem(parent, l = 'Tag Loc to Object',en = selPair,
	                c = lambda *a: buttonAction(locinatorLib.doTagObjects(self)))
		# Update Mode
		UpdateMenu = mUI.MelMenuItem(parent, l='Update Mode', subMenu=True)
		UpdateMenuCollection = mUI.MelRadioMenuCollection()

		if self.LocinatorUpdateObjectsOptionVar.value == 0:
			slMode = True
			bufferMode = False
		else:
			slMode = False
			bufferMode = True

		UpdateMenuCollection.createButton(UpdateMenu,l='Selected',
				                             c=lambda *a: self.LocinatorUpdateObjectsOptionVar.setValue(0),
				                             rb=slMode )
		UpdateMenuCollection.createButton(UpdateMenu,l='Buffer',
				                             c=lambda *a:self.LocinatorUpdateObjectsOptionVar.setValue(1),
				                             rb=bufferMode )
		#>>>Match Mode
		self.MatchModeOptions = ['parent','point','orient']
		
		self.MatchModeCollection = mUI.MelRadioMenuCollection()
		self.MatchModeCollectionChoices = []
					
		MatchModeMenu = mUI.MelMenuItem( parent, l='Match Mode', subMenu=True)
		self.matchMode = self.SnapModeOptionVar.value
		for c,item in enumerate(self.MatchModeOptions):
			if self.matchMode == c:
				rbValue = True
			else:
				rbValue = False
			self.MatchModeCollectionChoices.append(self.MatchModeCollection.createButton(MatchModeMenu,label=item,
			                                                                             rb = rbValue,
			                                                                             command = mUI.Callback(self.SnapModeOptionVar.setValue,c)))
		#>>> Define
		DefineMenu = mUI.MelMenuItem( parent, l='Buffer', subMenu=True)
		mUI.MelMenuItem( DefineMenu, l="Define",
		             c= lambda *a: locinatorLib.defineObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		mUI.MelMenuItem( DefineMenu, l="Add Selected",
		             c= lambda *a: locinatorLib.addSelectedToObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		mUI.MelMenuItem( DefineMenu, l="Remove Selected",
		             c= lambda *a: locinatorLib.removeSelectedFromObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
		
		mUI.MelMenuItemDiv( DefineMenu )
		mUI.MelMenuItem( DefineMenu, l="Select Members",
				     c= lambda *a: locinatorLib.selectObjBufferMembers(self.LocinatorUpdateObjectsBufferOptionVar))
		mUI.MelMenuItem( DefineMenu, l="Clear",
		             c= lambda *a: locinatorLib.clearObjBuffer(self.LocinatorUpdateObjectsBufferOptionVar))
				
		try:#>>> Sym Axis....
			_str_section = 'Ray Cast menu'
		
			uiMenu_rayCast = mUI.MelMenuItem( parent, l='Ray Cast Mode', subMenu=True)
			var_RayCastMode = cgmMeta.cgmOptionVar('cgmVar_SnapMenuRayCastMode', defaultValue=0)
			
			self.uiRC_RayCast = mUI.MelRadioMenuCollection()
			self.uiOptions_RayCast = []		
			_v = var_RayCastMode.value
			_modes = cgmDrag._clickMesh_modes
			for i,item in enumerate(_modes):
				if i == _v:
					_rb = True
				else:_rb = False
				self.uiOptions_RayCast.append(self.uiRC_RayCast.createButton(uiMenu_rayCast,label=item,
				                                                             c = mUI.Callback(var_RayCastMode.setValue,i),
				                                                             rb = _rb))   
		except Exception,err:
			log.error("{0} failed to load. err: {1}".format(_str_section,err))		
		
		
		
		mUI.MelMenuItemDiv(parent)		
		mUI.MelMenuItem(parent, l = 'Locinator',
	                c = lambda *a: buttonAction(cgmToolbox.loadLocinator()))
		mUI.MelMenuItem(parent, l = 'cgm.animTools',
	                c = lambda *a: buttonAction(cgmToolbox.loadAnimTools()))
		mUI.MelMenuItem(parent, l = 'cgm.tdTools',
	                c = lambda *a: buttonAction(cgmToolbox.loadTDTools()))
		mUI.MelMenuItem(parent, l = 'cgm.attrTools',
	                c = lambda *a: buttonAction(cgmToolbox.loadAttrTools()))
		mUI.MelMenuItem(parent, l = 'reload cgm.core',
	                c = lambda *a: buttonAction(cgmToolbox.reload_cgmCore()))	


		mUI.MelMenuItemDiv(parent)	
		
		mUI.MelMenuItem( parent, l="Docs",
	                     c='import webbrowser;webbrowser.open("http://www.cgmonks.com/tools/maya-tools/cgmmmsnap");')	
		
		mUI.MelMenuItem(parent, l="Reset",
	                 c=lambda *a: guiFactory.resetGuiInstanceOptionVars(self.optionVars))
			
		
	
		
def killUI():
	IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked', 'int')
	mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction', 'int')
	
	if mc.popupMenu('cgmMM',ex = True):
		mc.deleteUI('cgmMM')
		
	IsClickedOptionVar.setValue(0)
	mmActionOptionVar.setValue(0)	
	
	
def raySnap_start(targets = []):
	_toSnap = targets
	log.info("raySnap_start | targets: {0}".format(_toSnap))
	if not _toSnap:
		raise ValueError,"raySnap_start >> Must have targets!"

	var_RayCastMode = cgmMeta.cgmOptionVar('cgmVar_SnapMenuRayCastMode', defaultValue=0)
	log.info("mode: {0}".format(var_RayCastMode.value))
	
	cgmDrag.clickMesh( mode = var_RayCastMode.value,
	                   mesh = None,
	                   closestOnly = True,
	                   create = 'locator',
	                   dragStore = False,
	                   toSnap = _toSnap,
	                   timeDelay = .25,
	                   )

	log.warning("raySnap_start >>> ClickMesh initialized")
