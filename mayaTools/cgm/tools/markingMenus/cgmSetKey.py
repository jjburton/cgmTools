import maya.cmds as mc
import maya.mel as mel

from cgm.lib.zoo.zooPyMaya.baseMelUI import *

from cgm.lib.classes.OptionVarFactory import *
from cgm.lib import guiFactory
from cgm.tools.lib import animToolsLib

reload(animToolsLib)
def run():
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')	
	panel = mc.getPanel(up = True)
	sel = guiFactory.selectCheck()
	
	IsClickedOptionVar.set(0)
	mmActionOptionVar.set(0)
	
	if mc.popupMenu('tempMM',ex = True):
		mc.deleteUI('tempMM')
	print panel
	if panel:
		if mc.control(panel, ex = True):
			mc.popupMenu('tempMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = 'viewPanes',
				         pmc = lambda *a: createUI('tempMM'))
			return
		             

def createUI(parent):
	def buttonAction(command):
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
                l = 'Reset Selected',
                c = lambda *a:buttonAction(animToolsLib.ml_resetChannelsCall()),
                rp = 'N')
	
	mc.menuItem(en = sel,
                l = 'dragBreakdown',
                c = lambda *a:buttonAction(animToolsLib.ml_breakdownDraggerCall()),
                rp = 'S')
	
	mc.setParent('..',m=True)
	mc.menuItem(d = 1)	
	mc.menuItem(l = 'autoTangent',
                c = lambda *a: buttonAction(mel.eval('autoTangent')))
	mc.menuItem(l = 'tweenMachine',
                c = lambda *a: buttonAction(mel.eval('tweenMachine')))
	
	mc.menuItem(d = 1)
	mc.menuItem(l = 'ml Set Key',
                c = lambda *a: buttonAction(animToolsLib.ml_setKeyCall()))
	mc.menuItem(l = 'ml Hold',
                c = lambda *a: buttonAction(animToolsLib.ml_holdCall()))
	mc.menuItem(l = 'ml Delete Key',
                c = lambda *a: buttonAction(animToolsLib.ml_deleteKeyCall()))

def killUI():
	print "killing SetKey mm"
	IsClickedOptionVar = OptionVarFactory('cgmVar_IsClicked', 'int')
	mmActionOptionVar = OptionVarFactory('cgmVar_mmAction', 'int')
	print IsClickedOptionVar.value
	print mmActionOptionVar.value
	
	sel = guiFactory.selectCheck()
	
	if mc.popupMenu('tempMM',ex = True):
		mc.deleteUI('tempMM')
	
	print '>>>'
	print sel	
	if sel:
		if not mmActionOptionVar.value:
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