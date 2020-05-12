#=================================================================================================================================================
#=================================================================================================================================================
#	cgm.bufferTools - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Tool for making locators and other stuffs
#
# ARGUMENTS:
#   Maya
#   distance
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
#=================================================================================================================================================
__version__ = '0.1.06042012'

from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.classes.OptionVarFactory import *

import maya.mel as mel
import maya.cmds as mc

from cgm.tools.lib import (bufferToolsLib)
from cgm.lib import (search,guiFactory)

from cgm.lib import guiFactory

#reload(bufferToolsLib)
#reload(guiFactory)


def run():
	cgmBufferToolsWin = bufferToolsClass()
	#cgmBufferToolsWin(edit = True, resizeToFitChildren = True)

class bufferToolsClass(BaseMelWindow):
	from  cgm.lib import guiFactory
	guiFactory.initializeTemplates()
	USE_Template = 'cgmUITemplate'
	
	WINDOW_NAME = 'cgmBufferToolsWindow'
	WINDOW_TITLE = 'cgm.bufferTools'
	DEFAULT_SIZE = 265, 200
	DEFAULT_MENU = None
	RETAIN = True
	MIN_BUTTON = True
	MAX_BUTTON = False
	FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created

	def __init__( self):		
		self.toolName = 'cgm.bufferTools'
		self.description = 'This is a series of tools for working with cgm Buffers'
		self.author = 'Josh Burton'
		self.owner = 'CG Monks'
		self.website = 'www.cgmonks.com'
		self.version =  __version__ 
		self.optionVars = []
		
		self.activeObjectBuffersOptionVar = OptionVarFactory('cgmVar_activeObjectBuffers','string')
		guiFactory.appendOptionVarList(self,'cgmVar_activeObjectBuffers')		

		self.showHelp = False
		self.helpBlurbs = []
		self.oldGenBlurbs = []
		
		self.objectBuffers = []
		bufferToolsLib.updateObjectBuffers(self)

		#Menu
		self.setupVariables
		self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)
		self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)
		
		self.ShowHelpOption = mc.optionVar( q='cgmVar_AnimToolsShowHelp' )
		
		#GUI
		self.Main_buildLayout(self)

		self.show()

	def setupVariables():
		if not mc.optionVar( ex='cgmVar_ForceBoundingBoxState' ):
			mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 0) )
		if not mc.optionVar( ex='cgmVar_ForceEveryFrame' ):
			mc.optionVar( iv=('cgmVar_ForceEveryFrame', 0) )
		if not mc.optionVar( ex='cgmVar_bufferToolsShowHelp' ):
			mc.optionVar( iv=('cgmVar_bufferToolsShowHelp', 0) )
		if not mc.optionVar( ex='cgmVar_CurrentFrameOnly' ):
			mc.optionVar( iv=('cgmVar_CurrentFrameOnly', 0) )
		if not mc.optionVar( ex='cgmVar_bufferToolsShowHelp' ):
			mc.optionVar( iv=('cgmVar_bufferToolsShowHelp', 0) )
		
		
		guiFactory.appendOptionVarList(self,'cgmVar_bufferToolsShowHelp')
		
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Menus
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildOptionsMenu( self, *a ):
		self.UI_OptionsMenu.clear()

		# Placement Menu
		PlacementMenu = MelMenuItem( self.UI_OptionsMenu, l='Placement', subMenu=True)
		PlacementMenuCollection = MelRadioMenuCollection()

		if mc.optionVar( q='cgmVar_ForceBoundingBoxState' ) == 0:
			cgmOption = False
			pivotOption = True
		else:
			cgmOption = True
			pivotOption = False

		PlacementMenuCollection.createButton(PlacementMenu,l='Bounding Box Center',
				                             c=lambda *a: mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 1)),
				                             rb=cgmOption )
		PlacementMenuCollection.createButton(PlacementMenu,l='Pivot',
				                             c=lambda *a: mc.optionVar( iv=('cgmVar_ForceBoundingBoxState', 0)),
				                             rb=pivotOption )
		
		# Tagging options
		AutoloadMenu = MelMenuItem( self.UI_OptionsMenu, l='Tagging', subMenu=True)
		if not mc.optionVar( ex='cgmVar_TaggingUpdateRO' ):
			mc.optionVar( iv=('cgmVar_TaggingUpdateRO', 1) )
		guiFactory.appendOptionVarList(self,'cgmVar_TaggingUpdateRO')	
	  
		RenameOnUpdateState = mc.optionVar( q='cgmVar_TaggingUpdateRO' )
		MelMenuItem( AutoloadMenu, l="Update Rotation Order",
	                 cb= mc.optionVar( q='cgmVar_TaggingUpdateRO' ),
	                 c= lambda *a: guiFactory.doToggleIntOptionVariable('cgmVar_TaggingUpdateRO'))
		

		MelMenuItemDiv( self.UI_OptionsMenu )
		MelMenuItem( self.UI_OptionsMenu, l="Reset",
			         c=lambda *a: self.reset())
	def reset(self):
		guiFactory.resetGuiInstanceOptionVars(self.optionVars,run)

	def buildHelpMenu( self, *a ):
		self.UI_HelpMenu.clear()
		MelMenuItem( self.UI_HelpMenu, l="Show Help",
				     cb=self.ShowHelpOption,
				     c= lambda *a: self.do_showHelpToggle())
		MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
				     c=lambda *a: self.printHelp() )

		MelMenuItemDiv( self.UI_HelpMenu )
		MelMenuItem( self.UI_HelpMenu, l="About",
				     c=lambda *a: self.showAbout() )

	def do_showHelpToggle( self):
		guiFactory.toggleMenuShowState(self.ShowHelpOption,self.helpBlurbs)
		mc.optionVar( iv=('cgmVar_bufferToolsShowHelp', not self.ShowHelpOption))
		self.ShowHelpOption = mc.optionVar( q='cgmVar_bufferToolsShowHelp' )

	def do_showTimeSubMenuToggleOn( self):
		guiFactory.toggleMenuShowState(1,self.timeSubMenu)
		mc.optionVar( iv=('cgmVar_CurrentFrameOnly', 1))

	def do_showTimeSubMenuToggleOff( self):
		guiFactory.toggleMenuShowState(0,self.timeSubMenu)
		mc.optionVar( iv=('cgmVar_CurrentFrameOnly', 0))


	def showAbout(self):
		window = mc.window( title="About", iconName='About', ut = 'cgmUITemplate',resizeToFitChildren=True )
		mc.columnLayout( adjustableColumn=True )
		guiFactory.header(self.toolName,overrideUpper = True)
		mc.text(label='>>>A Part of the cgmTools Collection<<<', ut = 'cgmUIInstructionsTemplate')
		guiFactory.headerBreak()
		guiFactory.lineBreak()
		descriptionBlock = guiFactory.textBlock(self.description)

		guiFactory.lineBreak()
		mc.text(label=('%s%s' %('Written by: ',self.author)))
		mc.text(label=('%s%s%s' %('Copyright ',self.owner,', 2011')))
		guiFactory.lineBreak()
		mc.text(label='Version: %s' % self.version)
		mc.text(label='')
		guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/bufferTools/")')
		guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
		mc.setParent( '..' )
		mc.showWindow( window )

	def printHelp(self):
		import bufferToolsLib
		help(bufferToolsLib)

	def do_everyFrameToggle( self):
		EveryFrameOption = mc.optionVar( q='cgmVar_ForceEveryFrame' )
		guiFactory.toggleMenuShowState(EveryFrameOption,self.timeSubMenu)
		mc.optionVar( iv=('cgmVar_ForceEveryFrame', not EveryFrameOption))



	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	# Layouts
	#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	def buildPlaceHolder(self,parent):
		self.containerName = MelColumnLayout(parent,ut='cgmUISubTemplate')
		return self.containerName
	
	def Main_buildLayout(self,parent):
		MainForm = MelFormLayout(parent)

		#>>>  Snap Section
		BufferHeader = guiFactory.header('Buffers')
		HelpInfo = MelLabel(MainForm,
		                    l = " Set buffer options: Set active, select, change name,add,remove,key,purge",
		                    ut = 'cgmUIInstructionsTemplate',
		                    al = 'center',
		                    ww = True,vis = self.ShowHelpOption)
		self.helpBlurbs.extend([HelpInfo])
		
		BufferListScroll = MelScrollLayout(MainForm,cr = 1, ut = 'cgmUISubTemplate')
		BufferMasterForm = MelFormLayout(BufferListScroll)
		BufferListColumn = MelColumnLayout(BufferMasterForm, adj = True, rowSpacing = 3)
		
		for i,b in enumerate(self.objectBuffers):
			tmpSetRow = MelFormLayout(BufferListColumn,height = 20)
			
			#Get check box state
			activeState = False
			if b in self.activeObjectBuffersOptionVar.value:
				activeState = True
			
			tmpActive = MelCheckBox(tmpSetRow,
			                        annotation = 'Set buffer set as active',
			                        value = activeState,
			                        onCommand =  "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.setBufferAsActive('cgmVar_activeObjectBuffers','",b,"')"),
			                        offCommand = "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.setBufferAsInactive('cgmVar_activeObjectBuffers','",b,"')"))
			tmpSel = guiFactory.doButton2(tmpSetRow,
			                              's->',
										  "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.selectBufferObjects('",b,"')"),
			                              'Select the buffer objects')
			
			tmpName = MelTextField(tmpSetRow, w = 100,ut = 'cgmUIReservedTemplate', text = b)
			bField = "%s"%tmpName
			bName = "%s"%b
			tmpName(edit = True,
			        ec = lambda *a:bufferToolsLib.updateBufferName(self,bField,bName))
			
			"""
			tmpName(edit = True,
			        ec = "%s%s%s%s%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.updateBufferName('",self,"','",tmpName,"','",b,"')"))
			"""
			tmpAdd = guiFactory.doButton2(tmpSetRow,
			                               '+',
										   "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.addSelected('",b,"')"),
			                               'Add selected  to the buffer')
			tmpRem= guiFactory.doButton2(tmpSetRow,
			                             '-',
										 "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.removeSelected('",b,"')"),
			                             'Remove selected  to the buffer')
			tmpKey = guiFactory.doButton2(tmpSetRow,
			                              'k',
										  "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.keyBuffer('",b,"')"),
			                              'Key buffer')
			tmpPurge = guiFactory.doButton2(tmpSetRow,
			                                'p',
											"%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.purgeBuffer('",b,"')"),
			                                'Purge buffer')	
			mc.formLayout(tmpSetRow, edit = True,
			              af = [(tmpActive, "left", 2),
			                    (tmpPurge,"right",0)],
			              ac = [(tmpSel,"left",0,tmpActive),
			                    (tmpName,"left",2,tmpSel),
			                    (tmpName,"right",2,tmpAdd),
			                    (tmpAdd,"right",2,tmpRem),
			                    (tmpRem,"right",2,tmpKey),
			                    (tmpKey,"right",2,tmpPurge)])
			
			MelSpacer(tmpSetRow, w = 2)
		
		
		
			
		
		NewBufferRow = guiFactory.doButton2(MainForm,
		                                    'Create Buffer',
		                                    lambda *a:bufferToolsLib.createBuffer(self),
		                                    'Create new buffer from selected buffer')	
			
		BufferMasterForm(edit = True,
		                 af = [(BufferListColumn,"top",0),
		                       (BufferListColumn,"left",0),
		                       (BufferListColumn,"right",0),
		                       (BufferListColumn,"bottom",0)])
		                 
		MainForm(edit = True,
		         af = [(BufferHeader,"top",0),
		               (BufferHeader,"left",0),
		               (BufferHeader,"right",0),
		               (HelpInfo,"left",0),
		               (HelpInfo,"right",0),
		               (BufferListScroll,"left",0),
		               (BufferListScroll,"right",0),
		               (NewBufferRow,"left",4),
		               (NewBufferRow,"right",4),
		               (NewBufferRow,"bottom",4)],
		         ac = [(HelpInfo,"top",0,BufferHeader),
		               (BufferListScroll,"top",0,HelpInfo),
		               (BufferListScroll,"bottom",0,NewBufferRow)],
		         attachNone = [(NewBufferRow,"top")])


		"""
			formLayout -e
				-af $opts "top" 0
				-af $opts "left" 0
				-af $opts "right" 0
		
				-ac $labelForm "top" 0 $opts
				-af $labelForm "left" 0
				-af $labelForm "right" 0
		
				-ac $list "top" 0 $labelForm
				-af $list "left" 0
				-af $list "right" 0
				-ac $list "bottom" 2 $newset
		
				-af $newset "left" 0
				-af $newset "right" 0
				-ac $newset "bottom" 2 $image
		
				-af $image "left" 0
				-af $image "right" 0
				-af $image "bottom" 0
				$master;
		
			formLayout -e
				-af $allsel "left" 0
		
				-ac $alllbl "left" 0 $allsel
				-ac $alllbl "right" 0 $alladd
		
				-ac $alladd "right" 0 $allrem
		
				-ac $allrem "right" 0 $alldel
		
				-af $alldel "right" 42
				$labelForm;
		
			formLayout -e
				-af $setList "top" 0
				-af $setList "left" 0
				-af $setList "right" 0
				-af $setList "bottom" 0
				$qssMaster;		
				
			"""
		
		


		
	def MainBackup_buildLayout(self,parent):
		BufferLayout = MelColumnLayout(parent)

		#>>>  Snap Section
		guiFactory.header('Buffers')
		guiFactory.lineSubBreak()
		
		bufferScroll = MelScrollLayout(BufferLayout,cr = 1)
		for i,b in enumerate(self.objectBuffers):
			self.b = MelHSingleStretchLayout(bufferScroll,h = 20)
			
			MelSpacer(self.b, w = 2)
			"""
			
			lambda *a:bufferToolsLib.selectBufferObjects(self.objectBuffers[i]),
			"%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.selectBufferObjects('",b,"')"),
			
			"""
			guiFactory.doButton2(self.b,
			                     'Sel',
			                     "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.selectBufferObjects('",b,"')"),
			                     'Select the buffer objects')
			tmp = MelTextField(self.b, w = 100,ut = 'cgmUIReservedTemplate', text = b, editable = False)
			self.b.setStretchWidget(tmp)
			guiFactory.doButton2(self.b,
			                     '+',
			                     "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.addSelected('",b,"')"),
			                     'Add selected  to the buffer')
			guiFactory.doButton2(self.b,
			                     '-',
			                     "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.removeSelected('",b,"')"),
			                     'Remove selected  to the buffer')
			guiFactory.doButton2(self.b,
			                     'k',
			                     "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.keyBuffer('",b,"')"),
			                     'Key buffer')
			guiFactory.doButton2(self.b,
			                     'p',
			                     "%s%s%s"%("from cgm.tools.lib import bufferToolsLib;bufferToolsLib.purgeBuffer('",b,"')"),
			                     'Purge buffer')			
			
			MelSpacer(self.b, w = 2)
			self.b.layout()
			
		mc.setParent(BufferLayout)
		guiFactory.lineSubBreak()
			
		guiFactory.lineBreak()
		guiFactory.doButton2(BufferLayout,
	                         'Create Buffer',
	                         lambda *a:bufferToolsLib.createBuffer(self),
	                         'Create new buffer from selected buffer')	
		


		"""
		for b in self.objectBuffers:
			self.b = MelFormLayout(BufferLayout,height = 20)
			tmpSel = guiFactory.doButton2(self.b,
			                              'Sel',
			                              lambda *a:bufferToolsLib.selectBufferObjects(b),
			                              'Select the buffer objects')
			tmpName = MelTextField(self.b, w = 100,ut = 'cgmUIReservedTemplate', text = b, editable = False)
			
			tmpAdd = guiFactory.doButton2(self.b,
			                               '+',
			                               lambda *a:bufferToolsLib.addSelected(b),
			                               'Add selected  to the buffer')
			tmpRem= guiFactory.doButton2(self.b,
			                             '-',
			                             lambda *a:bufferToolsLib.removeSelected(b),
			                             'Remove selected  to the buffer')
			tmpKey = guiFactory.doButton2(self.b,
			                              'k',
			                              lambda *a:bufferToolsLib.keyBuffer(b),
			                              'Key buffer')
			tmpPurge = guiFactory.doButton2(self.b,
			                                'p',
			                                lambda *a:bufferToolsLib.purgeBuffer(b),
			                                'Purge buffer')	
			mc.formLayout(self.b, edit = True,
			              af = [tmpSel, "left", 0],
			              ac = [tmpName,"left",0,tmpSel],
			              ac = [tmpName,"right",0,tmpAdd],
			              ac = [tmpAdd,"right",0,tmpRem],
			              ac = [tmpRem,"right",0,tmpKey],
			              ac = [tmpKey,"right",0,tmpPurge],
			              af = [tmpPurge,"right",0])
			
			
		
		"""
		"""
		for( $set in $sets ) {
			string $isPrevious = ( $zooSetMenuPreviousSet == $set ) ? "boldLabelFont":"smallPlainLabelFont";
			int $hideState = 0;
			int $isPostCommand = 0;
			string $hideLabel = ( $hideState ) ? ">":"h";
			string $unhideLabel = ( $hideState ) ? "u":"<";
			string $postLabel = ( $isPostCommand ) ? "pc>":"-o-";

			if( `objExists ( $set +".zooSetMenuHidden" )` ) $hideState = `getAttr ( $set +".zooSetMenuHidden" )`;
			else addAttr -ln zooSetMenuHidden -k 0 -h 1 -at bool $set;

			if( `objExists ( $set +".postCommandString" )` ) $isPostCommand = 1;

			string $rowName = `formLayout`;
				string $sel = `button -height 20 -label $buttonLabel -c ( "{zooSetSelector `zooSetNameFromRowName "+ $rowName +"`; zooSetPreviousSet `zooSetNameFromRowName "+ $rowName +"`;}" )`;
				string $name = `nameField -height 20 -o $set`;
				string $add = `button -height 20 -label "+" -align center -c ( "sets -add `zooSetNameFromRowName "+ $rowName +"` `ls -sl`" )`;
				string $rem = `button -height 20 -label "-" -align center -c ( "sets -rm `zooSetNameFromRowName "+ $rowName +"` `ls -sl`" )`;
				string $del = `button -height 20 -label "del" -align center -c ( "{delete `zooSetNameFromRowName "+ $rowName +"`; zooSetMenuWindowFunctions delete "+ $rowName +" none;}" )`;
				string $pc = `button -height 20 -label $postLabel -align center -c ( "zooSetMenuPostFunctions window `zooSetNameFromRowName "+ $rowName +"`;" )`;
			setParent ..;

			formLayout -e
				-af $sel "left" 0

				-ac $name "left" 0 $sel
				-ac $name "right" 0 $add

				-ac $add "right" 0 $rem

				-ac $rem "right" 0 $del

				-ac $del "right" 0 $pc

				-af $pc "right" 0
				$rowName;
			}		
		"""