import maya.cmds as mc
import maya.mel as mel

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.lib.classes.OptionVarFactory import *
from cgm.lib import guiFactory
from cgm.tools.lib import animToolsLib
from cgm.tools.lib import tdToolsLib

def run():
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')	
	panel = mc.getPanel(up = True)
	sel = guiFactory.selectCheck()
	
	IsClickedOptionVar.set(0)
	mmActionOptionVar.set(0)
	
	if mc.popupMenu('cgmMM',ex = True):
		mc.deleteUI('cgmMM')
	print panel
	if panel:
		if mc.control(panel, ex = True):
			mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = panel,
				         pmc = lambda *a: createUI('cgmMM'))
			return

	if sel:
		pass
		             

def createUI(parent):
	def buttonAction(command):
		killUI()
		command
		mmActionOptionVar.set(1)

		
	print 'Buildling mm'	
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')
	
	sel = guiFactory.selectCheck()
	
	IsClickedOptionVar.set(1)
	
	mc.menu(parent,e = True, deleteAllItems = True)
	
	mc.setParent(parent,m=True)
	
	mc.menuItem(en = sel,
                l = 'Point Snap',
                c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                rp = 'NW')
	mc.menuItem(en = sel,
                l = 'Parent Snap',
                c = lambda *a:buttonAction(tdToolsLib.doParentSnap()),
                rp = 'N')
	mc.menuItem(en = sel,
                l = 'Orient Snap',
                c = lambda *a:buttonAction(tdToolsLib.doOrientSnap()),
                rp = 'NE')
	
	mc.setParent('..',m=True)
	mc.menuItem(d = 1)	
	mc.menuItem(l = 'Locinator',
                c = lambda *a: buttonAction(mel.eval('autoTangent')))

	
def killUI():
	print "killing SetKey mm"
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')
	print IsClickedOptionVar.value
	print mmActionOptionVar.value
	
	sel = guiFactory.selectCheck()
	
	if mc.popupMenu('cgmMM',ex = True):
		mc.deleteUI('cgmMM')
	
	print '>>>'
	print sel	
	if sel:
		if not mmActionOptionVar.value:
			pass
			#mel.eval('performSetKeyframeArgList 1 {"0", "animationList"};')
			
	IsClickedOptionVar.set(0)
	mmActionOptionVar.set(0)
	
