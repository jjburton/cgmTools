import maya.cmds as mc
import maya.mel as mel

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core import cgm_PuppetMeta as cgmPM

from cgm.lib import guiFactory
from cgm.lib import (lists,search)
from cgm.tools.lib import animToolsLib
from cgm.tools.lib import tdToolsLib
from cgm.tools.lib import locinatorLib
reload(animToolsLib)
from cgm.lib import locators


import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def run():
    try:
	cgmSetKeyMM = puppetKeyMarkingMenu()
    except:
	mel.eval('performSetKeyframeArgList 1 {"0", "animationList"};')

class puppetKeyMarkingMenu(BaseMelWindow):
    _DEFAULT_MENU_PARENT = 'viewPanes'

    def __init__(self):	
	"""
	Initializes the pop up menu class call
	"""
	self.optionVars = []
	IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked', value = 0)
	mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction',value = 0)			

	panel = mc.getPanel(up = True)
	if panel:
	    # Attempt at fixing a bug of some tools not working when the pop up parent isn't 'viewPanes'
	    if 'MayaWindow' in mc.panel(panel,q = True,ctl = True):
		panel = 'viewPanes'

	sel = search.selectCheck()
	
	#>>>> Clock set
	#====================================================================
	self.clockStartVar = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyClockStart', defaultValue = 0.0)	
	self.clockStartVar.value = time.clock()
	log.debug("cgmPuppetKey.clockStart: %s"%self.clockStartVar.value)
	
	IsClickedOptionVar.value = 0
	mmActionOptionVar.value = 0

	if mc.popupMenu('cgmMM',ex = True):
	    mc.deleteUI('cgmMM')

	if panel:
	    if mc.control(panel, ex = True):
		try:
		    mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = panel,
		                 pmc = lambda *a: self.createUI('cgmMM'))
		except:
		    log.warning('Exception on set key marking menu')
		    mel.eval('performSetKeyframeArgList 1 {"0", "animationList"};')		

    def setupVariables(self):
	self.KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
	guiFactory.appendOptionVarList(self,self.KeyTypeOptionVar.name)

	self.KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)
	guiFactory.appendOptionVarList(self,self.KeyModeOptionVar.name)	

	self.mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction')
	
	self.BuildModuleOptionVar = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyBuildModule', defaultValue = 1)
	guiFactory.appendOptionVarList(self,self.BuildModuleOptionVar.name)	
	
	self.BuildPuppetOptionVar = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyBuildPuppet', defaultValue = 1)
	guiFactory.appendOptionVarList(self,self.BuildPuppetOptionVar.name)	
	
	self.ResetModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)		
	guiFactory.appendOptionVarList(self,self.ResetModeOptionVar.name)
	

    def createUI(self,parent):
	"""
	Create the UI
	"""		
	def buttonAction(command):
	    """
	    execute a command and let the menu know not do do the default button action but just kill the ui
	    """			
	    self.mmActionOptionVar.value=1			
	    command
	    killUI()	

	def aimObjects(self):
	    for i_obj in self.ml_objList[1:]:
		if i_obj.hasAttr('mClass') and i_obj.mClass == 'cgmControl':
		    if i_obj._isAimable():
			i_obj.doAim(self.i_target)
		   
	time_buildMenuStart =  time.clock()
	self.setupVariables()#Setup our optionVars

	IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked',value = 0)
	IsClickedOptionVar.value = 1
	

	#>>>> Sel check
	#====================================================================
	selected = mc.ls(sl=True) or []
	self.ml_objList = cgmMeta.validateObjListArg(selected,cgmMeta.cgmObject,True)
	log.debug("ml_objList: %s"%self.ml_objList)
	self.ml_modules = []
	if selected:selCheck = True
	else:selCheck = False

	#>>>> Aim check
	#====================================================================
	b_aimable = False
	self.i_target = False
	if len(self.ml_objList)>=2:
	    for i_obj in self.ml_objList[1:]:
		if i_obj.hasAttr('mClass') and i_obj.mClass == 'cgmControl':
		    if i_obj._isAimable():
			b_aimable = True
			self.i_target = self.ml_objList[0]
			break

	#ShowMatch = search.matchObjectCheck()

	#>>>> Build Menu
	#====================================================================		
	mc.menu(parent,e = True, deleteAllItems = True)
	MelMenuItem(parent,
	            en = selCheck,
	            l = 'Reset Selected',
	            c = lambda *a:buttonAction(animToolsLib.ml_resetChannelsCall(transformsOnly = self.ResetModeOptionVar.value)),
	            rp = 'N')  

	MelMenuItem(parent,
	            en = b_aimable,
	            l = 'Aim',
	            c = lambda *a:buttonAction(aimObjects(self)),
	            rp = 'E')     		

	MelMenuItem(parent,
	            en = selCheck,
	            l = 'dragBreakdown',
	            c = lambda *a:buttonAction(animToolsLib.ml_breakdownDraggerCall()),
	            rp = 'S')
	
	MelMenuItem(parent,
	            en = selCheck,
	            l = 'deleteKey',
	            c = lambda *a:deleteKey(),
	            rp = 'SW')	

	if self.ml_objList:
	    for i_o in self.ml_objList:
		#>>> Space switching							
		if i_o.getMessage('dynParentGroup'):
		    i_dynParent = cgmMeta.validateObjArg(i_o.getMessage('dynParentGroup')[0],cgmRigMeta.cgmDynParentGroup,True)
		    if i_dynParent:
			MelMenuItem(parent,l=">> %s <<"%i_o.getShortName(),en = False)
			for a in cgmRigMeta.d_DynParentGroupModeAttrs[i_dynParent.dynMode]:
			    if i_o.hasAttr(a):
				tmpMenu = MelMenuItem( parent, l="Change %s"%a, subMenu=True)
				v = mc.getAttr("%s.%s"%(i_o.mNode,a))
				for i,o in enumerate(cgmMeta.cgmAttr(i_o.mNode,a).p_enum):
				    if i == v:b_enable = False
				    else:b_enable = True
				    MelMenuItem(tmpMenu,l = "%s"%o,en = b_enable,
				                c = Callback(i_dynParent.doSwitchSpace,a,i))								
			MelMenuItemDiv(parent)

		#>>> Module
		buffer = i_o.getMessage('module')
		try:
		    self.ml_modules.append(i_o.rigNull.module)
		except StandardError,error:
		    log.info("Failed to append module for: %s | %s"%(i_o.getShortName(),error))

	#>>> Module
	if self.BuildModuleOptionVar.value and self.ml_modules:
	    self.ml_modules = lists.returnListNoDuplicates(self.ml_modules)
	    for i_module in self.ml_modules:
		MelMenuItem(parent,l=">> %s<< "%i_module.getBaseName(),en = False)
		try:#To build dynswitch
		    i_switch = i_module.rigNull.dynSwitch
		    for a in i_switch.l_dynSwitchAlias:
			MelMenuItem( parent, l="switch>> %s"%a,
			             c = Callback(i_switch.go,a))						
		except StandardError,error:
		    log.info("Failed to build dynSwitch for: %s | %s"%(i_o.getShortName(),error))	
		try:#module basic menu
		    if i_module.rigNull.getMessage('controlsAll'):
			MelMenuItem( parent, l="Key",
			             c = Callback(i_module.animKey))
			#MelMenuItem( parent, l="Select",
				#c = Callback(buttonAction(i_module.animSelect)))							
			MelMenuItem( parent, l="Select",
			             c = Callback(i_module.animSelect))									
		except StandardError,error:
		    log.info("Failed to build basic module menu for: %s | %s"%(i_o.getShortName(),error))					

		MelMenuItemDiv(parent)						


	#>>> Options menus
	#================================================================================
	MelMenuItem(parent,l = ">> Options <<",en = False)
	
	#>>> Build Type
	BuildMenu = MelMenuItem( parent, l='Build Menus', subMenu=True)
	#BuildMenuCollection = MelRadioMenuCollection()
	b_buildModule = self.BuildModuleOptionVar.value
	MelMenuItem(BuildMenu,l=' Module ',
	            c= Callback(self.toggleVarAndReset,self.BuildModuleOptionVar),
	            cb= self.BuildModuleOptionVar.value )	
	MelMenuItem(BuildMenu,l=' Puppet ',
	            c= Callback(self.toggleVarAndReset,self.BuildPuppetOptionVar),
	            cb= self.BuildPuppetOptionVar.value )		
	
	
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


	#>>> Reset Mode
	ResetMenu = MelMenuItem( parent, l='Reset Mode', subMenu=True)
	ResetMenuCollection = MelRadioMenuCollection()

	if self.ResetModeOptionVar.value == 0:
	    regModeOption = True
	    cbModeOption = False
	else:
	    regModeOption = False
	    cbModeOption = True

	ResetMenuCollection.createButton(ResetMenu,l=' Default ',
	                                 c= Callback(self.toggleVarAndReset,self.ResetModeOptionVar),
	                                 rb= regModeOption )
	ResetMenuCollection.createButton(ResetMenu,l=' Transform Attrs ',
	                                 c= Callback(self.toggleVarAndReset,self.ResetModeOptionVar),
	                                 rb= cbModeOption )			

	#MelMenuItemDiv(parent)
	"""
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
		"""
	#MelMenuItem(parent,l = "-"*20,en = False)
	MelMenuItemDiv(parent)							
	MelMenuItem(parent, l="Reset",
	            c=lambda *a: guiFactory.resetGuiInstanceOptionVars(self.optionVars))
	
	f_time = time.clock()-time_buildMenuStart
	log.info('build menu took: %0.3f seconds  ' % (f_time) + '<'*10)  
	
    def toggleVarAndReset(self, optionVar):
	try:
	    self.mmActionOptionVar.value=1						
	    optionVar.toggle()
	    log.info("PuppetKey.toggleVarAndReset>>> %s : %s"%(optionVar.name,optionVar.value))
	except StandardError,error:
	    log.error(error)
	    print "MM change var and reset failed!"


def killUI():
    IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked')
    mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction')

    sel = search.selectCheck()
    
    #>>> Timer stuff
    #=============================================================================
    var_clockStart = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyClockStart', defaultValue = 0.0)    
    f_seconds = time.clock()-var_clockStart.value
    log.debug(">"*10  + '   cgmPuppetKey =  %0.3f seconds  ' % (f_seconds) + '<'*10)    
    
    #>>>Delete our gui and default behavior
    if mc.popupMenu('cgmMM',ex = True):
	mc.deleteUI('cgmMM')
    if sel and f_seconds <= .5 and not mmActionOptionVar.value:
	setKey()

def setKey():
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	

    if not KeyModeOptionVar.value:#This is default maya keying mode
	selection = mc.ls(sl=True) or []
	if not selection:
	    return log.warning('cgmPuppetKey.setKey>>> Nothing selected!')

	if not KeyTypeOptionVar.value:
	    mc.setKeyframe(selection)
	else:
	    mc.setKeyframe(breakdown = True)
    else:#Let's check the channel box for objects
	selection = search.returnSelectedAttributesFromChannelBox(False) or []
	if not selection:
	    selection = mc.ls(sl=True) or []
	    if not selection:
		return log.warning('cgmPuppetKey.setKey>>> Nothing selected!')

	if not KeyTypeOptionVar.value:
	    mc.setKeyframe(selection)
	else:
	    mc.setKeyframe(selection,breakdown = True)	
	    
def deleteKey():
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	

    if not KeyModeOptionVar.value:#This is default maya keying mode
	selection = mc.ls(sl=True) or []
	if not selection:
	    return log.warning('cgmPuppetKey.deleteKey>>> Nothing selected!')

	if not KeyTypeOptionVar.value:
	    mc.cutKey(selection)	    
	else:
	    mc.cutKey(selection)	    
    else:#Let's check the channel box for objects
	selection = search.returnSelectedAttributesFromChannelBox(False) or []
	if not selection:
	    selection = mc.ls(sl=True) or []
	    if not selection:
		return log.warning('cgmPuppetKey.deleteKey>>> Nothing selected!')

	if not KeyTypeOptionVar.value:
	    mc.cutKey(selection)	    
	else:
	    mc.cutKey(selection,breakdown = True)	
