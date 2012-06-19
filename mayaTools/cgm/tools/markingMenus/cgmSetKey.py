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
reload(animToolsLib)
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

	def createUI(self,parent):
		"""
		Create the UI
		"""		
		IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked')
		self.mmActionOptionVar = OptionVarFactory('cgmVar_mmAction')
		
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
			
		
	
		
def killUI():
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction')
	sel = search.selectCheck()
	
	if mc.popupMenu('cgmMM',ex = True):
		mc.deleteUI('cgmMM')

	if sel:
		if not mmActionOptionVar.value:
			print mmActionOptionVar.value
			mel.eval('performSetKeyframeArgList 1 {"0", "animationList"};')
			
"""
if (`popupMenu -exists tempMM`) { deleteUI tempMM; }
"""
	
	
"""

global proc cgmSetkeyKillUI () {
	global int $zooIsClicked;
	if( `popupMenu -ex tempMM` ) {
		deleteUI tempMM;
		if ( !$zooIsClicked ) performSetKeyframeArgList 1 {"0", "animationList"};
		}

	$zooIsClicked = 0;
	}



global proc cgmSetkeyCreateUI( string $parent, int $keyCommands ) {
	global int $zooIsClicked;
	string $selObjs[] = `ls -sl`;
	float $factor = `optionVar -ex zooCopycatFactor`? `optionVar -q zooCopycatFactor`: 0.1;
	int $smooth = `optionVar -ex zooSetkeySmooth`? `optionVar -q zooSetkeySmooth`: 0;
	float $curSpeed = `zooPlaySpeed -1 $smooth`;
	int $sel = `size $selObjs`;

	if( $keyCommands ) {
		zooKeyCommands "" "";
		zooKeyCommandsPopupMenu $parent;
		menuItem -d 1;
		}
	else menu -e -dai $parent;
	setParent -m $parent;

	$zooIsClicked = 1;
	menuItem -en $sel -l "push key forward" -c( "zooSetkeyPush fwd;" ) -rp E;
	menuItem -en $sel -l "push key backward" -c( "zooSetkeyPush bak;" ) -rp W;

	menuItem -en $sel -l "pull from forward key" -c( "zooCopycat right 1.0;" ) -rp NE;
	menuItem -en $sel -l "pull from previous key" -c( "zooCopycat left 1.0;" ) -rp NW;

	menuItem -en $sel -l "copycat value toward next" -c( "zooCopycat right "+ $factor +";" ) -rp SE;
	menuItem -en $sel -l "copycat value toward prev" -c( "zooCopycat left "+ $factor +";" ) -rp SW;

	menuItem -en $sel -l "copycat adjacent" -c( "zooCopycat left "+ $factor +"; zooCopycat right "+ $factor +";" ) -rp N;
	
	//menuItem -en $sel -l "dragBreakdown" -c( python("from cgm.tools.lib import animToolsLib;animToolsLib.ml_breakdownDraggerCall()")) -rp "S";
	menuItem -en $sel -l "dragBreakdown" -c(python("from cgm.tools.lib import animToolsLib;animToolsLib.ml_breakdownDraggerCall()")) -rp "S";

	menuItem -en $sel -l "copycat (breakdown) factor" -sm 1;
		menuItem -l "nudge by 2%" -cb( $factor == 0.02 ) -c( "optionVar -fv zooCopycatFactor 0.02;" );
		menuItem -l "nudge by 5%" -cb( $factor == 0.05 ) -c( "optionVar -fv zooCopycatFactor 0.05;" );
		menuItem -l "nudge by 10%" -cb( $factor == 0.1 ) -c( "optionVar -fv zooCopycatFactor 0.1;" );
		menuItem -l "nudge by 25%" -cb( $factor == 0.25 ) -c( "optionVar -fv zooCopycatFactor 0.25;" );
		menuItem -l "nudge by 50%" -cb( $factor == 0.5 ) -c( "optionVar -fv zooCopycatFactor 0.5;" );
	setParent -m ..;
	menuItem -d 1;
	menuItem -en 1 -l "autoTangent" -c( "autoTangent;" );
		menuItem -en 1 -l "tweenMachine" -c( "tweenMachine;" );

	menuItem -d 1;

	menuItem -en $sel -l "select all static keys" -c( "zooSelectStaticKeys static 1;" );
	menuItem -en $sel -l "select outer static keys" -c( "zooSelectStaticKeys outer 1;" );
	menuItem -en $sel -l "select inner static keys" -c( "zooSelectStaticKeys inner 1;" );
	menuItem -en $sel -l "select non static keys" -c( "zooSelectStaticKeys static 1; selectKey -tgl -k `ls -sl`;" );
	menuItem -d 1;

	menuItem -l "play on..." -sm 1;
		menuItem -l "ones" -cb( $curSpeed==1 ) -c( "zooPlaySpeed 1 "+ $smooth +";" );
		menuItem -l "twos" -cb( $curSpeed==0.5 ) -c( "zooPlaySpeed 0.5 "+ $smooth +";" );
		menuItem -l "threes" -cb( $curSpeed==0.33 ) -c( "zooPlaySpeed 0.33 "+ $smooth +";" );
		menuItem -l "fours" -cb( $curSpeed==0.25 ) -c( "zooPlaySpeed 0.25 "+ $smooth +";" );
		menuItem -d 1;
		menuItem -l "smooth (no frame holds)" -cb $smooth -c(($smooth? "optionVar -rm zooSetkeySmooth;": "optionVar -iv zooSetkeySmooth 1;") +"zooPlaySpeed "+ $curSpeed +" "+ (!$smooth));
	setParent -m ..;
	menuItem -l "open keyCommands" -c "source zooKeyCommandsWin;";
	}






global proc cgmSetkeyKillUI () {
	global int $zooIsClicked;
	if( `popupMenu -ex tempMM` ) {
		deleteUI tempMM;
		if ( !$zooIsClicked ) performSetKeyframeArgList 1 {"0", "animationList"};
		}

	$zooIsClicked = 0;
	}

"""