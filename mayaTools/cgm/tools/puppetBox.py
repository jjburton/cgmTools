#=================================================================================================================================================
#=================================================================================================================================================
#	cgm.puppetBox - a part of cgmTools
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
__version__ = '0.1.07052012'

from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.lib.classes.OptionVarFactory import *
from cgm.rigger.PuppetFactory import *
from cgm.rigger import ModuleFactory
from cgm.rigger.lib import functions
#reload(functions)

import maya.mel as mel
import maya.cmds as mc

from cgm.tools.lib import puppetBoxLib
from cgm.lib import (search,
                     guiFactory,
                     modules,
                     dictionary)


#reload(puppetBoxLib)
#reload(dictionary)
#reload(guiFactory)
#reload(modules)

def run():
    cgmPuppetBoxWin = puppetBoxClass()

class puppetBoxClass(BaseMelWindow):
    from  cgm.lib import guiFactory
    guiFactory.initializeTemplates()
    USE_Template = 'cgmUITemplate'

    WINDOW_NAME = 'cgmPuppetBoxWindow'
    WINDOW_TITLE = 'cgm.puppetBox - %s'%__version__
    DEFAULT_SIZE = 250, 400
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = False  #always resets the size of the window when its re-created
    global cgmPuppet

    def __init__( self):		
        self.toolName = 'cgm.puppetBox'
        self.description = 'This is a series of tools for working with cgm Sets'
        self.author = 'Josh Burton'
        self.owner = 'CG Monks'
        self.website = 'www.cgmonks.com'
        self.dockCnt = 'cgmPuppetBoxDoc'			
        self.version =  __version__ 
        self.optionVars = []
        self.scenePuppets = []
        self.Puppet = False
        self.PuppetBridge = {}
        self.puppetStateOptions = ['define']
        self.puppetStateOptions.extend(ModuleFactory.moduleStates)
        #self.addModules = ['Spine','Leg','Arm','Limb','Finger','Foot','Neck','Head','Spine']
        self.addModules = ['Segment']
        self.moduleFrames = {}
        self.moduleBaseNameFields = {}
        self.moduleHandleFields = {}
        self.moduleRollFields = {}
        self.moduleCurveFields = {}
        self.moduleStiffIndexFields = {}

        self.moduleDirectionMenus = {}
        self.modulePositionMenus = {}

        self.moduleDirections = ['none','left','right']
        self.modulePositions = ['none','front','rear','forward','back','top','bottom']



        self.setModes = ['<<< All Loaded Sets >>>','<<< Active Sets >>>']
        self.scenePuppets = modules.returnPuppetObjects()
        self.UI_StateRows = {'define':[],'template':[],'skeleton':[],'rig':[]}

        self.showHelp = False
        self.helpBlurbs = []
        self.oldGenBlurbs = []

        #Menu
        self.setupVariables()

        self.UI_PuppetMenu = MelMenu( l='Puppet', pmc=self.buildPuppetMenu)
        self.UI_AddModulesMenu = MelMenu( l='Add', pmc=self.buildAddModulesMenu)
        self.UI_OptionsMenu = MelMenu( l='Options', pmc=self.buildOptionsMenu)		
        self.UI_HelpMenu = MelMenu( l='Help', pmc=self.buildHelpMenu)

        self.ShowHelpOption = mc.optionVar( q='cgmVar_AnimToolsShowHelp' )

        #GUI

        self.Main_buildLayout(self)

        if self.Puppet:
            puppetBoxLib.updateUIPuppet(self)


        if self.scenePuppets:
            puppetBoxLib.activatePuppet(self,self.scenePuppets[0])

        #====================
        # Show and Dock
        #====================
        #Maya2011 QT docking - from Red9's examples
        try:
            #'Maya2011 dock delete'
            if mc.dockControl(self.dockCnt, exists=True):
                mc.deleteUI(self.dockCnt, control=True)  
        except:
            pass

        if self.dockOptionVar.value:
            try:
                allowedAreas = ['right', 'left']
                mc.dockControl(self.dockCnt, area='right', label=self.WINDOW_TITLE, content=self.WINDOW_NAME, floating=False, allowedArea=allowedAreas, width=400)
            except:
                #Dock failed, opening standard Window	
                self.show()
        else:self.show()


    def setupVariables(self):
        self.PuppetModeOptionVar = OptionVarFactory('cgmVar_PuppetCreateMode',defaultValue = 0)
        guiFactory.appendOptionVarList(self,self.PuppetModeOptionVar.name)

        self.PuppetAimOptionVar = OptionVarFactory('cgmVar_PuppetAimAxis',defaultValue = 2)
        guiFactory.appendOptionVarList(self,self.PuppetAimOptionVar.name)		
        self.PuppetUpOptionVar = OptionVarFactory('cgmVar_PuppetUpAxis',defaultValue = 1)
        guiFactory.appendOptionVarList(self,self.PuppetUpOptionVar.name)	
        self.PuppetOutOptionVar = OptionVarFactory('cgmVar_PuppetOutAxis',defaultValue = 0)
        guiFactory.appendOptionVarList(self,self.PuppetOutOptionVar.name)			

        self.ActiveObjectSetsOptionVar = OptionVarFactory('cgmVar_activeObjectSets',defaultValue = [''])
        self.ActiveRefsOptionVar = OptionVarFactory('cgmVar_activeRefs',defaultValue = [''])
        self.ActiveTypesOptionVar = OptionVarFactory('cgmVar_activeTypes',defaultValue = [''])
        self.SetToolsModeOptionVar = OptionVarFactory('cgmVar_puppetBoxMode', defaultValue = 0)
        self.KeyTypeOptionVar = OptionVarFactory('cgmVar_KeyType', defaultValue = 0)
        self.ShowHelpOptionVar = OptionVarFactory('cgmVar_puppetBoxShowHelp', defaultValue = 0)
        self.MaintainLocalSetGroupOptionVar = OptionVarFactory('cgmVar_MaintainLocalSetGroup', defaultValue = 1)
        self.HideSetGroupOptionVar = OptionVarFactory('cgmVar_HideSetGroups', defaultValue = 1)
        self.HideAnimLayerSetsOptionVar = OptionVarFactory('cgmVar_HideAnimLayerSets', defaultValue = 1)
        self.HideMayaSetsOptionVar = OptionVarFactory('cgmVar_HideMayaSets', defaultValue = 1)
        
        self.dockOptionVar = OptionVarFactory('cgmVar_PuppetBoxDock', defaultValue = 1)
        
        guiFactory.appendOptionVarList(self,self.ActiveObjectSetsOptionVar.name)
        guiFactory.appendOptionVarList(self,self.ActiveRefsOptionVar.name)
        guiFactory.appendOptionVarList(self,self.ActiveTypesOptionVar.name)
        guiFactory.appendOptionVarList(self,self.SetToolsModeOptionVar.name)
        guiFactory.appendOptionVarList(self,self.ShowHelpOptionVar.name)
        guiFactory.appendOptionVarList(self,self.KeyTypeOptionVar.name)
        guiFactory.appendOptionVarList(self,self.HideSetGroupOptionVar.name)
        guiFactory.appendOptionVarList(self,self.MaintainLocalSetGroupOptionVar.name)
        guiFactory.appendOptionVarList(self,self.HideAnimLayerSetsOptionVar.name)
        guiFactory.appendOptionVarList(self,self.HideMayaSetsOptionVar.name)
        guiFactory.appendOptionVarList(self,self.dockOptionVar.name)        

        self.DebugModeOptionVar = OptionVarFactory('cgmVar_PuppetBoxDebug',defaultValue=0)
        guiFactory.appendOptionVarList(self,self.DebugModeOptionVar.name)		

    def updateModulesUI(self):
        def optionMenuSet(item):
            print item
            #puppetBoxLib.uiModuleSetCGMTag(self,tag,item,index)
            """
			i =  self.setModes.index(item)
			self.SetToolsModeOptionVar.set( i )
			self.setMode = i"""

        #deleteExisting
        self.ModuleListColumn.clear()

        if self.Puppet:			
            for i,b in enumerate(self.Puppet.ModulesBuffer.bufferList):
                # NEED to get colors
                #Build label for Frame
                self.moduleFrames[i] = MelFrameLayout(self.ModuleListColumn,l='',
                                                      collapse=True,
                                                      collapsable=True,
                                                      marginHeight=0,
                                                      marginWidth=0,
                                                      bgc = dictionary.guiDirectionColors['center'])
                puppetBoxLib.uiModuleUpdateFrameLabel(self,i)


                #Build Naming Row
                tmpNameRow = MelFormLayout(self.moduleFrames[i], h=25,
                                           )
                tmpNameLabel = MelLabel(tmpNameRow,l='base:',align='right')

                self.moduleBaseNameFields[i] = MelTextField(tmpNameRow,text=self.Puppet.Module[i].nameBase or '',
                                                            ec = Callback(puppetBoxLib.uiUpdateBaseName,self,i),
                                                            w=50,
                                                            h=20)

                tmpDirLabel = MelLabel(tmpNameRow,l='dir:',align='right')								
                self.moduleDirectionMenus[i] = MelOptionMenu(tmpNameRow, cc = Callback(puppetBoxLib.uiModuleOptionMenuSet,self,self.moduleDirectionMenus,self.moduleDirections,'cgmDirection',i))

                for cnt,o in enumerate(self.moduleDirections):
                    self.moduleDirectionMenus[i].append(o)
                    if o == self.Puppet.Module[i].ModuleNull.cgm['cgmDirection']:
                        self.moduleDirectionMenus[i](edit = True, select = cnt + 1)

                tmpPosLabel = MelLabel(tmpNameRow,l='pos:',align='right')
                self.modulePositionMenus[i] = MelOptionMenu(tmpNameRow,
                                                            cc = Callback(puppetBoxLib.uiModuleOptionMenuSet,self,self.modulePositionMenus,self.modulePositions,'cgmPosition',i))
                for cnt,o in enumerate(self.modulePositions):
                    self.modulePositionMenus[i].append(o)
                    if o == self.Puppet.Module[i].ModuleNull.cgm['cgmPosition']:
                        self.modulePositionMenus[i](edit = True, select = cnt + 1)					

                mc.formLayout(tmpNameRow, edit = True,
                              af = [(tmpNameLabel, "left", 10),
                                    (self.modulePositionMenus[i],"right",10)],
                              ac = [(self.moduleBaseNameFields[i],"left",5,tmpNameLabel),
                                    (self.moduleBaseNameFields[i],"right",5,tmpDirLabel),
                                    (tmpDirLabel,"right",5,self.moduleDirectionMenus[i]),
                                    (self.moduleDirectionMenus[i],"right",5,tmpPosLabel),
                                    (tmpPosLabel,"right",5,self.modulePositionMenus[i] ),
                                    ])
                #>>>>>>>>>>>>>>>>>>>>>

                if self.Puppet.Module[i].moduleClass == 'Limb':

                    #Build Int Settings Row
                    tmpIntRow = MelHSingleStretchLayout(self.moduleFrames[i], h=25,
                                                        )
                    tmpIntRow.setStretchWidget(MelSpacer(tmpIntRow,w=5))

                    MelLabel(tmpIntRow,l='Handles:')
                    self.moduleHandleFields[i] = MelIntField(tmpIntRow,
                                                             v = self.Puppet.Module[i].optionHandles.value,
                                                             bgc = dictionary.returnStateColor('normal'),
                                                             ec = Callback(puppetBoxLib.uiModuleUpdateIntAttrFromField,self,self.moduleHandleFields,'optionHandles',i),
                                                             h = 20, w = 35)
                    MelLabel(tmpIntRow,l='Roll:')
                    self.moduleRollFields[i] = MelIntField(tmpIntRow,
                                                           v = self.Puppet.Module[i].optionRollJoints.value,					                                       
                                                           bgc = dictionary.returnStateColor('normal'),
                                                           ec = Callback(puppetBoxLib.uiModuleUpdateIntAttrFromField,self,self.moduleRollFields,'optionRollJoints',i),
                                                           h = 20, w = 35)
                    MelLabel(tmpIntRow,l='Stiff Index:')
                    self.moduleStiffIndexFields[i] = MelIntField(tmpIntRow,
                                                                 v = self.Puppet.Module[i].optionStiffIndex.value,					                                             
                                                                 bgc = dictionary.returnStateColor('normal'),
                                                                 ec = Callback(puppetBoxLib.uiModuleUpdateIntAttrFromField,self,self.moduleStiffIndexFields,'optionStiffIndex',i),
                                                                 h = 20, w = 35)	
                    MelLabel(tmpIntRow,l='Curve:')
                    self.moduleCurveFields[i] = MelIntField(tmpIntRow,
                                                            v = self.Puppet.Module[i].optionCurveDegree.value,					                                        
                                                            bgc = dictionary.returnStateColor('normal'),
                                                            ec = Callback(puppetBoxLib.uiModuleUpdateIntAttrFromField,self,self.moduleCurveFields,'optionCurveDegree',i),
                                                            h = 20, w = 35)


                    MelSpacer(tmpIntRow,w=10)

                    tmpIntRow.layout()



                #PopUp Menu!
                popUpMenu = MelPopupMenu(self.moduleFrames[i],button = 3)

                MelMenuItem(popUpMenu,
                            label = "cls: %s"%self.Puppet.Module[i].moduleClass,
                            enable = False)
                #Parent/MIrror				
                MelMenuItem(popUpMenu,
                            label = "Set Parent>",
                            enable = False)
                MelMenuItem(popUpMenu,
                            label = "Set Mirror>",
                            enable = False)	

                if self.Puppet.Module[i].moduleClass == 'Limb':
                    MelMenuItem(popUpMenu,
                                label = 'FK',
                                cb = self.Puppet.Module[i].optionFK.value,
                                c = Callback(puppetBoxLib.uiModuleToggleBool,self,'optionFK',i))
                    MelMenuItem(popUpMenu,
                                label = 'IK',
                                cb = self.Puppet.Module[i].optionIK.value,
                                c = Callback(puppetBoxLib.uiModuleToggleBool,self,'optionIK',i))
                    MelMenuItem(popUpMenu,
                                label = 'Stretchy',
                                cb = self.Puppet.Module[i].optionStretchy.value,
                                c = Callback(puppetBoxLib.uiModuleToggleBool,self,'optionStretchy',i))
                    MelMenuItem(popUpMenu,
                                label = 'Bendy',
                                cb = self.Puppet.Module[i].optionBendy.value,
                                c = Callback(puppetBoxLib.uiModuleToggleBool,self,'optionBendy',i))

                MelMenuItemDiv(popUpMenu)

                # Object Aim Menu
                ObjectAimMenu = MelMenuItem(popUpMenu, l='Aim:', subMenu=True)
                self.ObjectAimCollection = MelRadioMenuCollection()

                for index,axis in enumerate(dictionary.axisDirectionsByString):
                    if self.Puppet.Module[i].optionAimAxis.get() == index:
                        checkState = True
                    else:
                        checkState = False
                    self.ObjectAimCollection.createButton(ObjectAimMenu,l=axis,
                                                          c= Callback(puppetBoxLib.doSetAxisAndUpdateModule,self,functions.doSetAimAxis,self.Puppet.Module[i],index),
                                                          rb = checkState)
                ObjectUpMenu = MelMenuItem(popUpMenu, l='Up:', subMenu=True)
                self.ObjectUpCollection = MelRadioMenuCollection()

                for index,axis in enumerate(dictionary.axisDirectionsByString):
                    if self.Puppet.Module[i].optionUpAxis.get() == index:
                        checkState = True
                    else:
                        checkState = False
                    self.ObjectUpCollection.createButton(ObjectUpMenu,l=axis,
                                                         c= Callback(puppetBoxLib.doSetAxisAndUpdateModule,self,functions.doSetUpAxis,self.Puppet.Module[i],index),
                                                         rb = checkState)
                ObjectOutMenu = MelMenuItem(popUpMenu, l='Out:', subMenu=True)
                self.ObjectOutCollection = MelRadioMenuCollection()

                for index,axis in enumerate(dictionary.axisDirectionsByString):
                    if self.Puppet.Module[i].optionOutAxis.get() == index:
                        checkState = True
                    else:
                        checkState = False
                    self.ObjectOutCollection.createButton(ObjectOutMenu,l=axis,
                                                          c= Callback(puppetBoxLib.doSetAxisAndUpdateModule,self,functions.doSetOutAxis,self.Puppet.Module[i],index),
                                                          rb = checkState)


                ObjectOutMenu = MelMenuItem(popUpMenu, l='Copy from Parent', 
                                            c= Callback(puppetBoxLib.doCopyAxisFromParent,self,self.Puppet.Module[i]))

                MelMenuItemDiv(popUpMenu)



                MelMenuItem(popUpMenu ,
                            label = 'Remove',
                            c = Callback(puppetBoxLib.doRemoveModule,self,i))

                MelMenuItem(popUpMenu ,
                            label = 'Delete',
                            c = Callback(puppetBoxLib.doDeleteModule,self,i))


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Menus
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def buildPuppetMenu( self, *a ):
        self.UI_PuppetMenu.clear()

        #>>> Puppet Options	
        MelMenuItem( self.UI_PuppetMenu, l="New",
                     c=lambda *a:puppetBoxLib.doPuppetCreate(self))

        #Build load menu
        self.scenePuppets = modules.returnPuppetObjects()		
        loadMenu = MelMenuItem( self.UI_PuppetMenu, l='Pick Puppet:', subMenu=True)

        if self.scenePuppets:
            for i,m in enumerate(self.scenePuppets):
                MelMenuItem( loadMenu, l="%s"%m,
                             c= Callback(puppetBoxLib.activatePuppet,self,m))		
        else:
            MelMenuItem( loadMenu, l="None found")

        if self.Puppet:
            MelMenuItemDiv( self.UI_PuppetMenu )	
            MelMenuItem( self.UI_PuppetMenu, l="Initialize",
                         c=lambda *a:puppetBoxLib.initializePuppet(self))
            if not self.Puppet.refState:
                MelMenuItem( self.UI_PuppetMenu, l="Verify",
                             c=lambda *a:puppetBoxLib.verifyPuppet(self))	
                MelMenuItem( self.UI_PuppetMenu, l="Delete",
                             c=lambda *a:puppetBoxLib.deletePuppet(self))	
        #>>> Reset Options		
        MelMenuItemDiv( self.UI_PuppetMenu )
        MelMenuItem( self.UI_PuppetMenu, l="Reload",
                     c=lambda *a: self.reload())		
        MelMenuItem( self.UI_PuppetMenu, l="Reset",
                     c=lambda *a: self.reset())

    def buildAddModulesMenu( self, *a ):
        self.UI_AddModulesMenu.clear()
        for i,m in enumerate(self.addModules):
            MelMenuItem( self.UI_AddModulesMenu, l="%s"%m,
                         c=lambda *a:puppetBoxLib.addModule(self,m))

        MelMenuItemDiv( self.UI_AddModulesMenu )

    def buildOptionsMenu( self, *a ):
        self.UI_OptionsMenu.clear()
        MelMenuItem( self.UI_OptionsMenu, l="Force module menu reload",
                     c=lambda *a:puppetBoxLib.uiForceModuleUpdateUI(self))		


    def reset(self):	
        Callback(guiFactory.resetGuiInstanceOptionVars(self.optionVars,run))

    def reload(self):	
        run()


    def buildHelpMenu( self, *a ):
        self.UI_HelpMenu.clear()
        MelMenuItem( self.UI_HelpMenu, l="Show Help",
                     cb=self.ShowHelpOptionVar.value,
                     c= lambda *a: self.do_showHelpToggle())

        MelMenuItem( self.UI_HelpMenu, l="Print Set Report",
                     c=lambda *a: self.printReport() )
        MelMenuItem( self.UI_HelpMenu, l="Print Tools Help",
                     c=lambda *a: self.printHelp() )

        MelMenuItemDiv( self.UI_HelpMenu )
        MelMenuItem( self.UI_HelpMenu, l="About",
                     c=lambda *a: self.showAbout() )
        MelMenuItem( self.UI_HelpMenu, l="Debug",
                     cb=self.DebugModeOptionVar.value,
                     c= lambda *a: self.DebugModeOptionVar.toggle())			

    def do_showHelpToggle( self):
        guiFactory.toggleMenuShowState(self.ShowHelpOptionVar.value,self.helpBlurbs)
        self.ShowHelpOptionVar.toggle()


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
        guiFactory.doButton('Visit Tool Webpage', 'import webbrowser;webbrowser.open(" http://www.cgmonks.com/tools/maya-tools/puppetBox/")')
        guiFactory.doButton('Close', 'import maya.cmds as mc;mc.deleteUI(\"' + window + '\", window=True)')
        mc.setParent( '..' )
        mc.showWindow( window )

    def printHelp(self):
        help(puppetBoxLib)

    def printReport(self):
        puppetBoxLib.printReport(self)


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Layouts
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    def Main_buildLayout(self,parent):
        def modeSet( item ):
            i =  self.setModes.index(item)
            self.SetToolsModeOptionVar.set( i )
            self.setMode = i

        MainForm = MelFormLayout(parent)
        TopSection = MelColumnLayout(MainForm)	
        SetHeader = guiFactory.header('Puppet')

        #>>>  Top Section
        #Report
        self.puppetReport = MelLabel(TopSection,
                                     bgc = dictionary.returnStateColor('help'),
                                     align = 'center',
                                     label = '...',
                                     h=20)
        MelSeparator(TopSection,ut='cgmUITemplate',h=5)

        #Edit name and state mode buttons
        MasterPuppetRow = MelHSingleStretchLayout(TopSection,padding = 5)
        MelSpacer(MasterPuppetRow,w=5)
        self.MasterPuppetTF = MelTextField(MasterPuppetRow,
                                           bgc = [1,1,1],
                                           ec = lambda *a:puppetBoxLib.updatePuppetName(self))
        MasterPuppetRow.setStretchWidget(self.MasterPuppetTF)

        self.puppetStateButtonsDict = {}
        for i,s in enumerate(self.puppetStateOptions):
            self.puppetStateButtonsDict[i] = guiFactory.doButton2(MasterPuppetRow,s.capitalize(),
                                                                  "print '%s'"%s,
                                                                  enable = False)
        MelSpacer(MasterPuppetRow,w=20)

        MasterPuppetRow.layout()
        #MelSeparator(TopSection,ut='cgmUITemplate',h=2)

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Define State Rows
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>		
        #Initial State Mode Row
        self.PuppetModeCollection = MelRadioCollection()
        self.PuppetModeCollectionChoices = []			

        self.InitialStateModeRow = MelHSingleStretchLayout(TopSection,padding = 2,vis=False)	
        MelSpacer(self.InitialStateModeRow,w=5)				
        MelLabel(self.InitialStateModeRow,l='Template Modes')
        Spacer = MelSeparator(self.InitialStateModeRow,w=10)						
        for i,item in enumerate(CharacterTypes):
            self.PuppetModeCollectionChoices.append(self.PuppetModeCollection.createButton(self.InitialStateModeRow,label=item,
                                                                                           onCommand = Callback(puppetBoxLib.setPuppetBaseMode,self,i)))
            MelSpacer(self.InitialStateModeRow,w=3)
        self.InitialStateModeRow.setStretchWidget( Spacer )
        MelSpacer(self.InitialStateModeRow,w=2)		
        self.InitialStateModeRow.layout()	

        mc.radioCollection(self.PuppetModeCollection ,edit=True,sl= (self.PuppetModeCollectionChoices[ (self.PuppetModeOptionVar.value) ]))
        self.UI_StateRows['define'].append(self.InitialStateModeRow)


        self.AxisFrame = MelFrameLayout(TopSection,label = 'Axis',vis=False,
                                        collapse=True,
                                        collapsable=True,
                                        ut = 'cgmUIHeaderTemplate')
        self.UI_StateRows['define'].append(self.AxisFrame)
        MelSeparator(TopSection,style='none',h=5)						

        #Aim Axis Mode Row
        self.AimAxisCollection = MelRadioCollection()
        self.AimAxisCollectionChoices = []			

        self.AimAxisRow = MelHSingleStretchLayout(self.AxisFrame,padding = 2,vis=False)	
        MelSpacer(self.AimAxisRow,w=5)				
        MelLabel(self.AimAxisRow,l='Aim ')
        Spacer = MelSeparator(self.AimAxisRow,w=10)						
        for i,item in enumerate(axisDirectionsByString):
            self.AimAxisCollectionChoices.append(self.AimAxisCollection.createButton(self.AimAxisRow,label=item,
                                                                                     onCommand = Callback(puppetBoxLib.setPuppetAxisAim,self,i)))
            MelSpacer(self.AimAxisRow,w=3)
        self.AimAxisRow.setStretchWidget( Spacer )
        MelSpacer(self.AimAxisRow,w=2)		
        self.AimAxisRow.layout()	


        #Up Axis Mode Row
        self.UpAxisCollection = MelRadioCollection()
        self.UpAxisCollectionChoices = []			

        self.UpAxisRow = MelHSingleStretchLayout(self.AxisFrame,padding = 2,vis=False)	
        MelSpacer(self.UpAxisRow,w=5)				
        MelLabel(self.UpAxisRow,l='Up ')
        Spacer = MelSeparator(self.UpAxisRow,w=10)						
        for i,item in enumerate(axisDirectionsByString):
            self.UpAxisCollectionChoices.append(self.UpAxisCollection.createButton(self.UpAxisRow,label=item,
                                                                                   onCommand = Callback(puppetBoxLib.setPuppetAxisUp,self,i)))
            MelSpacer(self.UpAxisRow,w=3)
        self.UpAxisRow.setStretchWidget( Spacer )
        MelSpacer(self.UpAxisRow,w=2)		
        self.UpAxisRow.layout()	


        #Out Axis Mode Row
        self.OutAxisCollection = MelRadioCollection()
        self.OutAxisCollectionChoices = []			

        self.OutAxisRow = MelHSingleStretchLayout(self.AxisFrame,padding = 2,vis=False)	
        MelSpacer(self.OutAxisRow,w=5)				
        MelLabel(self.OutAxisRow,l='Out ')
        Spacer = MelSeparator(self.OutAxisRow,w=10)	
        for i,item in enumerate(axisDirectionsByString):
            self.OutAxisCollectionChoices.append(self.OutAxisCollection.createButton(self.OutAxisRow,label=item,
                                                                                     onCommand = Callback(puppetBoxLib.setPuppetAxisOut,self,i)))
            MelSpacer(self.OutAxisRow,w=3)
        self.OutAxisRow.setStretchWidget( Spacer )
        MelSpacer(self.OutAxisRow,w=2)		
        self.OutAxisRow.layout()	

        #Set toggles on menu
        mc.radioCollection(self.AimAxisCollection ,edit=True,sl= (self.AimAxisCollectionChoices[ (self.PuppetAimOptionVar.value) ]))		
        mc.radioCollection(self.UpAxisCollection ,edit=True,sl= (self.UpAxisCollectionChoices[ (self.PuppetUpOptionVar.value) ]))		
        mc.radioCollection(self.OutAxisCollection ,edit=True,sl= (self.OutAxisCollectionChoices[ (self.PuppetOutOptionVar.value) ]))


        #Initial State Button Row
        self.InitialStateButtonRow = MelHLayout(TopSection, h = 20,vis=False,padding = 5)
        guiFactory.doButton2(self.InitialStateButtonRow,'Add Geo',
                             lambda *a:puppetBoxLib.doAddGeo(self))
        guiFactory.doButton2(self.InitialStateButtonRow,'Build Size Template',
                             lambda *a:puppetBoxLib.doBuildSizeTemplate(self))

        self.InitialStateButtonRow.layout()
        self.UI_StateRows['define'].append(self.InitialStateButtonRow)

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Multi Module
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        #>>>  All Sets menu
        AllModulesRow = MelFormLayout(MainForm,height = 20)
        activeState = True
        i = 1

        tmpActive = MelCheckBox(AllModulesRow,
                                annotation = 'Sets all sets active',
                                value = activeState,
                                onCommand =  Callback(puppetBoxLib.doSetAllSetsAsActive,self),
                                offCommand = Callback(puppetBoxLib.doSetAllSetsAsInactive,self))

        tmpSel = guiFactory.doButton2(AllModulesRow,
                                      ' s ',
                                      'Select All Loaded/Active Sets')

        # Mode toggle box
        self.ModuleModeOptionMenu = MelOptionMenu(AllModulesRow,
                                                  cc = modeSet)


        tmpKey = guiFactory.doButton2(AllModulesRow,
                                      ' k ',
                                      'Key All Sets')
        tmpDeleteKey = guiFactory.doButton2(AllModulesRow,
                                            ' d ',
                                            'Delete All Set Keys')	
        tmpReset = guiFactory.doButton2(AllModulesRow,
                                        ' r ',
                                        'Reset All Set Keys')	

        mc.formLayout(AllModulesRow, edit = True,
                      af = [(tmpActive, "left", 10),
                            (tmpReset,"right",10)],
                      ac = [(tmpSel,"left",0,tmpActive),
                            (self.ModuleModeOptionMenu,"left",4,tmpSel),
                            (self.ModuleModeOptionMenu,"right",4,tmpKey),
                            (tmpKey,"right",2,tmpDeleteKey),
                            (tmpDeleteKey,"right",2,tmpReset)
                            ])

        #>>> Sets building section
        allPopUpMenu = MelPopupMenu(self.ModuleModeOptionMenu ,button = 3)

        allCategoryMenu = MelMenuItem(allPopUpMenu,
                                      label = 'Make Type:',
                                      sm = True)




        #>>> Sets building section
        ModuleListScroll = MelScrollLayout(MainForm,cr = 1, ut = 'cgmUISubTemplate')
        ModuleMasterForm = MelFormLayout(ModuleListScroll)
        self.ModuleListColumn = MelColumnLayout(ModuleMasterForm,ut = 'cgmUIInstructionsTemplate', adj = True, rowSpacing = 2)



        self.helpInfo = MelLabel(MainForm,
                                 h=20,
                                 l = "Add a Puppet",
                                 ut = 'cgmUIInstructionsTemplate',
                                 al = 'center',
                                 ww = True,vis = self.ShowHelpOptionVar.value)
        self.helpBlurbs.extend([self.helpInfo ])

        VerifyRow = guiFactory.doButton2(MainForm,
                                         'Check Puppet',
                                         'Create new buffer from selected buffer')	

        ModuleMasterForm(edit = True,
                         af = [(self.ModuleListColumn,"top",0),
                               (self.ModuleListColumn,"left",0),
                               (self.ModuleListColumn,"right",0),
                               (self.ModuleListColumn,"bottom",0)])


        MainForm(edit = True,
                 af = [(TopSection,"top",0),	
                       (TopSection,"left",0),
                       (TopSection,"right",0),		               
                       (AllModulesRow,"left",0),
                       (AllModulesRow,"right",0),
                       (ModuleListScroll,"left",0),
                       (ModuleListScroll,"right",0),
                       (ModuleListScroll,"left",0),
                       (ModuleListScroll,"right",0),				       
                       (self.helpInfo,"left",8),
                       (self.helpInfo,"right",8),
                       (VerifyRow,"left",4),
                       (VerifyRow,"right",4),		               
                       (VerifyRow,"bottom",4)],
                 ac = [(AllModulesRow,"top",2,TopSection),
                       (ModuleListScroll,"top",2,AllModulesRow),
                       (ModuleListScroll,"bottom",0,self.helpInfo),
                       (self.helpInfo,"bottom",0,VerifyRow)],
                 attachNone = [(VerifyRow,"top")])	

