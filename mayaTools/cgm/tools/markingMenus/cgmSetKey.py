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

#reload(locinatorLib)
#reload(tdToolsLib)
#reload(animToolsLib)
def run():
	try:
		cgmSetKeyMM = setKeyMarkingMenu()
	except:
		mel.eval('performSetKeyframeArgList 1 {"0", "animationList"};')
	
class setKeyMarkingMenu(BaseMelWindow):
	_DEFAULT_MENU_PARENT = 'viewPanes'
	
	def __init__(self):	
		"""
		Initializes the pop up menu class call
		"""
		self.optionVars = []
		IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 0)
		mmActionOptionVar = OptionVarFactory('cgmVar_mmAction',0)			
		
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
					guiFactory.warning('Exception on set key marking menu')
					mel.eval('performSetKeyframeArgList 1 {"0", "animationList"};')		
					
	def setupVariables(self):
		self.KeyTypeOptionVar = OptionVarFactory('cgmVar_KeyType', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.KeyTypeOptionVar.name)
		
		self.KeyModeOptionVar = OptionVarFactory('cgmVar_KeyMode', defaultValue = 0)
		guiFactory.appendOptionVarList(self,self.KeyModeOptionVar.name)	
		
		self.mmActionOptionVar = OptionVarFactory('cgmVar_mmAction')
		

	def createUI(self,parent):
		"""
		Create the UI
		"""		
		IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked',value = 0)
		self.setupVariables()
		
		def buttonAction(command):
			"""
			execute a command and let the menu know not do do the default button action but just kill the ui
			"""			
			self.mmActionOptionVar.set(1)			
			command
			killUI()
			
		sel = search.selectCheck()
		selPair = search.checkSelectionLength(2)
		ShowMatch = search.matchObjectCheck()
		
		IsClickedOptionVar.set(1)
		
		mc.menu(parent,e = True, deleteAllItems = True)
		MelMenuItem(parent,
		            en = sel,
		            l = 'Reset Selected',
		            c = lambda *a:buttonAction(animToolsLib.ml_resetChannelsCall()),
		            rp = 'N')            
		
		MelMenuItem(parent,
		            en = sel,
		            l = 'dragBreakdown',
		            c = lambda *a:buttonAction(animToolsLib.ml_breakdownDraggerCall()),
		            rp = 'S')
		
	
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
		
		#>>> Keying Mode
		KeyMenu = MelMenuItem( parent, l='Key Mode', subMenu=True)
		KeyMenuCollection = MelRadioMenuCollection()
	
		if self.KeyModeOptionVar.value == 0:
			regModeOption = True
			cbModeOption = False
		else:
			regModeOption = False
			cbModeOption = True
	
		KeyMenuCollection.createButton(KeyMenu,l=' Default ',
		                               c= Callback(self.toggleVarAndReset,self.KeyModeOptionVar),
		                               rb= regModeOption )
		KeyMenuCollection.createButton(KeyMenu,l=' Channelbox ',
		                               c= Callback(self.toggleVarAndReset,self.KeyModeOptionVar),
		                               rb= cbModeOption )		
		
		MelMenuItemDiv(parent)
		MelMenuItem(parent,l = 'autoTangent',
				    c = lambda *a: buttonAction(mel.eval('autoTangent')))
		MelMenuItem(parent,l = 'tweenMachine',
				    c = lambda *a: buttonAction(mel.eval('tweenMachine')))	
		MelMenuItem(parent, l = 'cgm.animTools',
	                c = lambda *a: buttonAction(cgmToolbox.loadAnimTools()))	
		MelMenuItemDiv(parent)
		MelMenuItem(parent,l = 'ml Set Key',
			        c = lambda *a: buttonAction(animToolsLib.ml_setKeyCall()))
		MelMenuItem(parent,l = 'ml Hold',
			        c = lambda *a: buttonAction(animToolsLib.ml_holdCall()))
		MelMenuItem(parent,l = 'ml Delete Key',
			        c = lambda *a: buttonAction(animToolsLib.ml_deleteKeyCall()))
		MelMenuItem(parent,l = 'ml Arc Tracer',
			        c = lambda *a: buttonAction(animToolsLib.ml_arcTracerCall()))

		MelMenuItemDiv(parent)	
		MelMenuItem(parent, l="Reset",
	                 c=lambda *a: guiFactory.resetGuiInstanceOptionVars(self.optionVars))
			
	def toggleVarAndReset(self, optionVar):
		try:
			optionVar.toggle()
			self.reload()
		except:
			print "MM change var and reset failed!"
	
		
def killUI():
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction')
	
	sel = search.selectCheck()
	
	if mc.popupMenu('cgmMM',ex = True):
		mc.deleteUI('cgmMM')

	if sel:
		if not mmActionOptionVar.value:
			setKey()
			
def setKey():
	KeyTypeOptionVar = OptionVarFactory('cgmVar_KeyType', defaultValue = 0)
	KeyModeOptionVar = OptionVarFactory('cgmVar_KeyMode', defaultValue = 0)	
	
	if not KeyModeOptionVar.value:#This is default maya keying mode
		selection = mc.ls(sl=True) or []
		if not selection:
			return guiFactory.warning('Nothing selected!')
			
		if not KeyTypeOptionVar.value:
			mc.setKeyframe(selection)
		else:
			mc.setKeyframe(breakdown = True)
	else:#Let's check the channel box for objects
		print 'cb mode'
		selection = search.returnSelectedAttributesFromChannelBox(False) or []
		if not selection:
			selection = mc.ls(sl=True) or []
			if not selection:
				return guiFactory.warning('Nothing selected!')
		
		if not KeyTypeOptionVar.value:
			mc.setKeyframe(selection)
		else:
			mc.setKeyframe(selection,breakdown = True)		

