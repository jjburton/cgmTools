#=================================================================================================================================================
#=================================================================================================================================================
#	cgm.setTools - a part of cgmTools
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
__version__ = '0.1.12072012'

from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.SetFactory import *

import maya.mel as mel
import maya.cmds as mc

from cgm.tools.lib import (setToolsLib)
from cgm.lib import (search,guiFactory)

from cgm.lib import guiFactory

#reload(setToolsLib)
#reload(guiFactory)

#>>>Debug chunk===================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=================================================================

def run():
    cgmSetToolsWin = setToolsClass()

class setToolsClass(BaseMelWindow):
    from  cgm.lib import guiFactory
    guiFactory.initializeTemplates()
    USE_Template = 'cgmUITemplate'

    WINDOW_NAME = 'cgmSetToolsWindow'
    WINDOW_TITLE = 'cgm.setTools - %s'%__version__
    DEFAULT_SIZE = 275, 400
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = False  #always resets the size of the window when its re-created

    def __init__( self):		
        self.toolName = 'cgm.setTools'
        self.description = 'This is a series of tools for working with cgm Sets'
        self.author = 'Josh Burton'
        self.owner = 'CG Monks'
        self.website = 'www.cgmonks.com'
        self.version =  __version__ 
        self.optionVars = []
        self.dockCnt = 'cgmSetToolsDock'			


        self.setTypes = ['NONE',
                         'animation',
                         'layout',
                         'modeling',
                         'td',
                         'fx',
                         'lighting']
        self.setModes = ['<<< All Loaded Sets >>>','<<< Active Sets >>>']

        self.showHelp = False
        self.helpBlurbs = []
        self.oldGenBlurbs = []

        self.objectSets = []

        #Menu
        self.setupVariables()
        self.setMode = self.SetToolsModeOptionVar.value		
        setToolsLib.updateObjectSets(self)

        self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)
        self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)

        self.ShowHelpOption = mc.optionVar( q='cgmVar_AnimToolsShowHelp' )

        #GUI

        self.Main_buildLayout(self)

        #====================
        # Show and Dock
        #====================
        #Maya2011 QT docking - from Red9's examples
        try:
            #'Maya2011 dock delete'
            if mc.dockControl(self.dockCnt, exists=True):
                mc.deleteUI(self.dockCnt, control=True)  
        except StandardError,error:
            raise StandardError(error)

        if self.dockOptionVar.value:
            try:
                allowedAreas = ['right', 'left']
                mc.dockControl(self.dockCnt, area='right', label=self.WINDOW_TITLE, content=self.WINDOW_NAME, floating=False, allowedArea=allowedAreas, width=300)
            except:
                #Dock failed, opening standard Window	
                self.show()
        else:self.show()

    def setupVariables(self):
        self.dockOptionVar = OptionVarFactory('cgmVar_AttrToolsBoxDock', defaultValue = 1)
        guiFactory.appendOptionVarList(self,self.dockOptionVar.name)	

        self.ActiveObjectSetsOptionVar = OptionVarFactory('cgmVar_activeObjectSets',defaultValue = [''])
        self.ActiveRefsOptionVar = OptionVarFactory('cgmVar_activeRefs',defaultValue = [''])
        self.ActiveTypesOptionVar = OptionVarFactory('cgmVar_activeTypes',defaultValue = [''])
        self.SetToolsModeOptionVar = OptionVarFactory('cgmVar_setToolsMode', defaultValue = 0)
        self.KeyTypeOptionVar = OptionVarFactory('cgmVar_KeyType', defaultValue = 0)
        self.ShowHelpOptionVar = OptionVarFactory('cgmVar_setToolsShowHelp', defaultValue = 0)
        self.MaintainLocalSetGroupOptionVar = OptionVarFactory('cgmVar_MaintainLocalSetGroup', defaultValue = 0)
        self.HideSetGroupOptionVar = OptionVarFactory('cgmVar_HideSetGroups', defaultValue = 1)
        self.HideNonQssOptionVar = OptionVarFactory('cgmVar_HideNonQss', defaultValue = 1)		
        self.HideAnimLayerSetsOptionVar = OptionVarFactory('cgmVar_HideAnimLayerSets', defaultValue = 1)
        self.HideMayaSetsOptionVar = OptionVarFactory('cgmVar_HideMayaSets', defaultValue = 1)


        guiFactory.appendOptionVarList(self,self.ActiveObjectSetsOptionVar.name)
        guiFactory.appendOptionVarList(self,self.ActiveRefsOptionVar.name)
        guiFactory.appendOptionVarList(self,self.ActiveTypesOptionVar.name)
        guiFactory.appendOptionVarList(self,self.SetToolsModeOptionVar.name)
        guiFactory.appendOptionVarList(self,self.ShowHelpOptionVar.name)
        guiFactory.appendOptionVarList(self,self.KeyTypeOptionVar.name)
        guiFactory.appendOptionVarList(self,self.HideSetGroupOptionVar.name)
        guiFactory.appendOptionVarList(self,self.HideNonQssOptionVar.name)		
        guiFactory.appendOptionVarList(self,self.MaintainLocalSetGroupOptionVar.name)
        guiFactory.appendOptionVarList(self,self.HideAnimLayerSetsOptionVar.name)
        guiFactory.appendOptionVarList(self,self.HideMayaSetsOptionVar.name)


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Menus
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildOptionsMenu( self, *a ):
        self.UI_OptionsMenu.clear()


        #Ref menu	
        self.refPrefixDict = {}	
        self.activeRefsCBDict = {}

        if self.refPrefixes and len(self.refPrefixes) > 1:

            refMenu = MelMenuItem( self.UI_OptionsMenu, l='Load Refs:', subMenu=True)


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

            typeMenu = MelMenuItem( self.UI_OptionsMenu, l='Load Types: ', subMenu=True)


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

        #>>> Grouping Options
        GroupingMenu = MelMenuItem( self.UI_OptionsMenu, l='Grouping', subMenu=True)

        #guiFactory.appendOptionVarList(self,'cgmVar_MaintainLocalSetGroup')	
        MelMenuItem( GroupingMenu, l="Group Local",
                     c= lambda *a: setToolsLib.doGroupLocal(self))

        MelMenuItem( GroupingMenu, l="Maintain Local Set Group",
                     cb= mc.optionVar( q='cgmVar_MaintainLocalSetGroup' ),
                     c= lambda *a: setToolsLib.doSetMaintainLocalSetGroup(self))


        #>>> Autohide Options
        HidingMenu = MelMenuItem( self.UI_OptionsMenu, l='Auto Hide', subMenu=True)

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

        #>>> Keying Options
        KeyMenu = MelMenuItem( self.UI_OptionsMenu, l='Key type', subMenu=True)
        KeyMenuCollection = MelRadioMenuCollection()

        if self.KeyTypeOptionVar.value == 0:
            regKeyOption = True
            bdKeyOption = False
        else:
            regKeyOption = False
            bdKeyOption = True

        KeyMenuCollection.createButton(KeyMenu,l=' Reg ',
                                       c=lambda *a:self.KeyTypeOptionVar.set(0),
                                       rb= regKeyOption )
        KeyMenuCollection.createButton(KeyMenu,l=' Breakdown ',
                                       c=lambda *a:self.KeyTypeOptionVar.set(1),
                                       rb= bdKeyOption )


        #>>> Reset Options		
        MelMenuItemDiv( self.UI_OptionsMenu )
        MelMenuItem( self.UI_OptionsMenu, l="Reload",
                     c=lambda *a: self.reload())		
        MelMenuItem( self.UI_OptionsMenu, l="Reset",
                     c=lambda *a: self.reset())

    def reset(self):	
        Callback(guiFactory.resetGuiInstanceOptionVars(self.optionVars,run))

    def reload(self):	
        run()

    def buildHelpMenu( self, *a ):
        self.UI_HelpMenu.clear()
        MelMenuItem( self.UI_HelpMenu, l="Show Help",
                     cb=self.ShowHelpOption,
                     c= lambda *a: self.do_showHelpToggle())

        MelMenuItem( self.UI_HelpMenu, l="Print Set Report",
                     c=lambda *a: self.printReport() )
        MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
                     c=lambda *a: self.printHelp() )

        MelMenuItemDiv( self.UI_HelpMenu )
        MelMenuItem( self.UI_HelpMenu, l="About",
                     c=lambda *a: self.showAbout() )

    def do_showHelpToggle( self):
        guiFactory.toggleMenuShowState(self.ShowHelpOption,self.helpBlurbs)
        mc.optionVar( iv=('cgmVar_setToolsShowHelp', not self.ShowHelpOption))
        self.ShowHelpOption = mc.optionVar( q='cgmVar_setToolsShowHelp' )


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
        guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/setTools/")')
        guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
        mc.setParent( '..' )
        mc.showWindow( window )

    def printHelp(self):
        help(setToolsLib)

    def printReport(self):
        setToolsLib.printReport(self)


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Layouts
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    def Main_buildLayout(self,parent):
        def modeSet( item ):
            i =  self.setModes.index(item)
            self.SetToolsModeOptionVar.set( i )
            self.setMode = i

        MainForm = MelFormLayout(parent)

        #>>>  Snap Section
        SetHeader = guiFactory.header('Sets')
        HelpInfo = MelLabel(MainForm,
                            l = " Set buffer options: Set active, select, change name,add,remove,key,purge",
                            ut = 'cgmUIInstructionsTemplate',
                            al = 'center',
                            ww = True,vis = self.ShowHelpOption)
        self.helpBlurbs.extend([HelpInfo])


        #>>>  All Sets menu
        AllSetsRow = MelFormLayout(MainForm,height = 20)
        activeState = True
        i = 1
        if self.objectSets:
            for b in self.objectSets:
                if b not in self.ActiveObjectSetsOptionVar.value:
                    activeState = False
        else:
            activeState = False

        tmpActive = MelCheckBox(AllSetsRow,
                                annotation = 'Sets all sets active',
                                value = activeState,
                                onCommand =  Callback(setToolsLib.doSetAllSetsAsActive,self),
                                offCommand = Callback(setToolsLib.doSetAllSetsAsInactive,self))

        tmpSel = guiFactory.doButton2(AllSetsRow,
                                      ' s ',
                                      lambda *a:setToolsLib.doSelectMultiSets(self,self.SetToolsModeOptionVar.value),
                                      'Select All Loaded/Active Sets')

        # Mode toggle box
        self.SetModeOptionMenu = MelOptionMenu(AllSetsRow,
                                               cc = modeSet)
        for m in self.setModes:
            self.SetModeOptionMenu.append(m)

        self.SetModeOptionMenu.selectByIdx(self.setMode,False)

        tmpKey = guiFactory.doButton2(AllSetsRow,
                                      ' k ',
                                      lambda *a:setToolsLib.doKeyMultiSets(self,self.SetToolsModeOptionVar.value),
                                      'Key All Sets')
        tmpDeleteKey = guiFactory.doButton2(AllSetsRow,
                                            ' d ',
                                            lambda *a:setToolsLib.doDeleteMultiCurrentKeys(self,self.SetToolsModeOptionVar.value),
                                            'Delete All Set Keys')	
        tmpReset = guiFactory.doButton2(AllSetsRow,
                                        ' r ',
                                        lambda *a:setToolsLib.doResetMultiSets(self,self.SetToolsModeOptionVar.value),		                                
                                        'Reset All Set Keys')	

        mc.formLayout(AllSetsRow, edit = True,
                      af = [(tmpActive, "left", 10),
                            (tmpReset,"right",10)],
                      ac = [(tmpSel,"left",0,tmpActive),
                            (self.SetModeOptionMenu,"left",4,tmpSel),
                            (self.SetModeOptionMenu,"right",4,tmpKey),
                            (tmpKey,"right",2,tmpDeleteKey),
                            (tmpDeleteKey,"right",2,tmpReset)
                            ])

        #>>> Sets building section
        allPopUpMenu = MelPopupMenu(self.SetModeOptionMenu ,button = 3)

        allCategoryMenu = MelMenuItem(allPopUpMenu,
                                      label = 'Make Type:',
                                      sm = True)

        multiMakeQssMenu = MelMenuItem(allPopUpMenu,
                                       label = 'Make Qss',
                                       c = Callback(setToolsLib.doMultiSetQss,self,True))
        multiMakeNotQssMenu = MelMenuItem(allPopUpMenu,
                                          label = 'Clear Qss State',
                                          c = Callback(setToolsLib.doMultiSetQss,self,False))		
        #Mulit set type
        for n in self.setTypes:
            MelMenuItem(allCategoryMenu,
                        label = n,
                        c = Callback(setToolsLib.doMultiSetType,self,self.SetToolsModeOptionVar.value,n))


        #>>> Sets building section
        SetListScroll = MelScrollLayout(MainForm,cr = 1, ut = 'cgmUISubTemplate')
        SetMasterForm = MelFormLayout(SetListScroll)
        SetListColumn = MelColumnLayout(SetMasterForm, adj = True, rowSpacing = 3)

        self.objectSetsDict = {}
        self.activeSetsCBDict = {}

        for b in self.objectSets:
            #Store the info to a dict
            try:
                i = self.setInstancesFastIndex[b] # get the index
                sInstance = self.setInstances[i] # fast link to the instance
            except:
                raise StandardError("'%s' failed to query an active instance"%b)

            #see if the no no fields are enabled
            enabledMenuLogic = True
            if sInstance.mayaSetState or sInstance.refState:				
                enabledMenuLogic = False


            tmpSetRow = MelFormLayout(SetListColumn,height = 20)

            #Get check box state
            activeState = False
            if sInstance.nameShort in self.ActiveObjectSetsOptionVar.value:
                activeState = True
            tmpActive = MelCheckBox(tmpSetRow,
                                    annotation = 'make set as active',
                                    value = activeState,
                                    onCommand =  Callback(setToolsLib.doSetSetAsActive,self,i),
                                    offCommand = Callback(setToolsLib.doSetSetAsInactive,self,i))

            self.activeSetsCBDict[i] = tmpActive

            tmpSel = guiFactory.doButton2(tmpSetRow,
                                          ' s ',
                                          Callback(setToolsLib.doSelectSetObjects,self,i),
                                          'Select the set objects')


            tmpName = MelTextField(tmpSetRow, w = 100,ut = 'cgmUIReservedTemplate', text = sInstance.nameShort,
                                   editable = enabledMenuLogic)

            tmpName(edit = True,
                    ec = Callback(setToolsLib.doUpdateSetName,self,tmpName,i)	)


            tmpAdd = guiFactory.doButton2(tmpSetRow,
                                          '+',
                                          Callback(setToolsLib.doAddSelected,self,i),
                                          'Add selected  to the set',
                                          en = not sInstance.refState)
            tmpRem= guiFactory.doButton2(tmpSetRow,
                                         '-',
                                         Callback(setToolsLib.doRemoveSelected,self,i),
                                         'Remove selected  to the set',
                                         en = not sInstance.refState)
            tmpKey = guiFactory.doButton2(tmpSetRow,
                                          'k',
                                          Callback(setToolsLib.doKeySet,self,i),			                              
                                          'Key set')
            tmpDeleteKey = guiFactory.doButton2(tmpSetRow,
                                                'd',
                                                Callback(setToolsLib.doDeleteCurrentSetKey,self,i),			                              			                                
                                                'delete set key')	

            tmpReset = guiFactory.doButton2(tmpSetRow,
                                            'r',
                                            Callback(setToolsLib.doResetSet,self,i),			                              			                                
                                            'Reset Set')
            mc.formLayout(tmpSetRow, edit = True,
                          af = [(tmpActive, "left", 4),
                                (tmpReset,"right",2)],
                          ac = [(tmpSel,"left",0,tmpActive),
                                (tmpName,"left",2,tmpSel),
                                (tmpName,"right",4,tmpAdd),
                                (tmpAdd,"right",2,tmpRem),
                                (tmpRem,"right",2,tmpKey),
                                (tmpKey,"right",2,tmpDeleteKey),
                                (tmpDeleteKey,"right",2,tmpReset)
                                ])

            MelSpacer(tmpSetRow, w = 2)

            #Build pop up for text field
            popUpMenu = MelPopupMenu(tmpName,button = 3)
            MelMenuItem(popUpMenu,
                        label = "<<<%s>>>"%b,
                        enable = False)

            if not enabledMenuLogic:
                if sInstance.mayaSetState:
                    MelMenuItem(popUpMenu,
                                label = "<Maya Default Set>",
                                enable = False)				
                if sInstance.refState:
                    MelMenuItem(popUpMenu,
                                label = "<Referenced>",
                                enable = False)		

            qssState = sInstance.qssState
            qssMenu = MelMenuItem(popUpMenu,
                                  label = 'Qss',
                                  cb = qssState,
                                  en = enabledMenuLogic,
                                  c = Callback(self.setInstances[i].isQss,not qssState))

            categoryMenu = MelMenuItem(popUpMenu,
                                       label = 'Make Type:',
                                       sm = True,
                                       en = enabledMenuLogic)

            for n in self.setTypes:
                MelMenuItem(categoryMenu,
                            label = n,
                            c = Callback(setToolsLib.guiDoSetType,self,i,n))


            MelMenuItem(popUpMenu ,
                        label = 'Copy Set',
                        c = Callback(setToolsLib.doCopySet,self,i))

            MelMenuItem(popUpMenu ,
                        label = 'Purge',
                        en = enabledMenuLogic,
                        c = Callback(setToolsLib.doPurgeSet,self,i))

            MelMenuItemDiv(popUpMenu)
            MelMenuItem(popUpMenu ,
                        label = 'Delete',
                        en = enabledMenuLogic,
                        c = Callback(setToolsLib.doDeleteSet,self,i))	



        NewSetRow = guiFactory.doButton2(MainForm,
                                         'Create Set',
                                         lambda *a:setToolsLib.doCreateSet(self),
                                         'Create new buffer from selected buffer')	

        SetMasterForm(edit = True,
                      af = [(SetListColumn,"top",0),
                            (SetListColumn,"left",0),
                            (SetListColumn,"right",0),
                            (SetListColumn,"bottom",0)])

        MainForm(edit = True,
                 af = [(SetHeader,"top",0),
                       (SetHeader,"left",0),
                       (SetHeader,"right",0),
                       (HelpInfo,"left",0),
                       (HelpInfo,"right",0),
                       (AllSetsRow,"left",0),
                       (AllSetsRow,"right",0),
                       (SetListScroll,"left",0),
                       (SetListScroll,"right",0),
                       (NewSetRow,"left",4),
                       (NewSetRow,"right",4),
                       (NewSetRow,"bottom",4)],
                 ac = [(HelpInfo,"top",0,SetHeader),
                       (AllSetsRow,"top",2,HelpInfo),
                       (SetListScroll,"top",2,AllSetsRow),
                       (SetListScroll,"bottom",0,NewSetRow)],
                 attachNone = [(NewSetRow,"top")])	

