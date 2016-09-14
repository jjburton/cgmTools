#=================================================================================================================================================
#=================================================================================================================================================
#	guiFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Tool to make standard guis for our tools
#
# ARGUMENTS:
#   Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1.12042011 - First version
#	0.1.12072011 - Added progress tracking
#
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel


from cgm.core.lib.zoo.baseMelUI import *
from cgm.lib import dictionary
from cgm.lib import optionVars

mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

# Maya version check
if mayaVersion >= 2011:
    currentGenUI = True
else:
    currentGenUI = False
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Define our Colors
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def setBGColorState(textFieldToChange, newState):
    mc.textField(textFieldToChange,edit = True, bgc = dictionary.returnStateColor(newState))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Define our Templates
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def initializeTemplates():
    guiBackgroundColor = [.45,.45,.45]
    guiTextFieldColor = [.4,.4,.4]    
    guiHeaderColor = [.25,.25,.25]
    guiSubMenuColor = [.65,.65,.65]
    guiButtonColor = [.35,.35,.35]
    guiHelpBackgroundColor = [0.8, 0.8, 0.8]
    guiHelpBackgroundReservedColor = [0.411765 , 0.411765 , 0.411765]
    guiHelpBackgroundLockedColor = [0.837, 0.399528, 0.01674]

    if mc.uiTemplate( 'cgmUITemplate', exists=True ):
        mc.deleteUI( 'cgmUITemplate', uiTemplate=True )
    mc.uiTemplate('cgmUITemplate')
    mc.separator(dt='cgmUITemplate', height = 10, style = 'none')
    mc.button(dt = 'cgmUITemplate', height = 15, backgroundColor = guiButtonColor,align = 'center')
    mc.window(dt = 'cgmUITemplate', backgroundColor = guiBackgroundColor)
    mc.optionMenu(dt='cgmUITemplate',backgroundColor = guiButtonColor)
    mc.optionMenuGrp(dt ='cgmUITemplate', backgroundColor = guiButtonColor)
    mc.textField(dt = 'cgmUITemplate',backgroundColor = [1,1,1],h=20)
    mc.formLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor)    
    mc.textScrollList(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 
    mc.frameLayout(dt='cgmUITemplate', backgroundColor = guiBackgroundColor) 

    # Define our header template
    if mc.uiTemplate( 'cgmUIHeaderTemplate', exists=True ):
        mc.deleteUI( 'cgmUIHeaderTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIHeaderTemplate')
    mc.text(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.separator(dt='cgmUIHeaderTemplate', height = 5, style = 'none',backgroundColor = guiHeaderColor)
    mc.formLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)    
    mc.rowLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.rowColumnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)
    mc.columnLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor)  
    mc.textScrollList(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 
    mc.frameLayout(dt='cgmUIHeaderTemplate', backgroundColor = guiHeaderColor) 

    # Define our sub template
    if mc.uiTemplate( 'cgmUISubTemplate', exists=True ):
        mc.deleteUI( 'cgmUISubTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUISubTemplate')
    mc.formLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.text(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.separator(dt='cgmUISubTemplate', height = 2, style = 'none', backgroundColor = guiSubMenuColor)
    mc.rowLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.rowColumnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.columnLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.scrollLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor)
    mc.textField(dt = 'cgmUISubTemplate',backgroundColor = [1,1,1],h=20)
    mc.textScrollList(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 
    mc.frameLayout(dt='cgmUISubTemplate', backgroundColor = guiSubMenuColor) 


    # Define our instructional template
    if mc.uiTemplate( 'cgmUIInstructionsTemplate', exists=True ):
        mc.deleteUI( 'cgmUIInstructionsTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIInstructionsTemplate')
    mc.text(dt = 'cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.formLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
    mc.rowLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.rowColumnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)
    mc.columnLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor)    
    mc.textField(dt = 'cgmUIInstructionsTemplate',backgroundColor = [1,1,1],h=20)
    mc.textScrollList(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 
    mc.frameLayout(dt='cgmUIInstructionsTemplate', backgroundColor = guiHelpBackgroundColor) 

    # Define our Reserved
    if mc.uiTemplate( 'cgmUIReservedTemplate', exists=True ):
        mc.deleteUI( 'cgmUIReservedTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUIReservedTemplate')
    mc.textField(dt = 'cgmUIReservedTemplate', backgroundColor = guiTextFieldColor,h=20)
    mc.formLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)    
    mc.rowLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
    mc.rowColumnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)
    mc.columnLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor)  
    mc.frameLayout(dt='cgmUIReservedTemplate', backgroundColor = guiButtonColor) 

    # Define our Locked
    if mc.uiTemplate( 'cgmUILockedTemplate', exists=True ):
        mc.deleteUI( 'cgmUILockedTemplate', uiTemplate=True )
    mc.uiTemplate('cgmUILockedTemplate')
    mc.textField(dt = 'cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor, h=20)
    mc.frameLayout(dt='cgmUILockedTemplate', backgroundColor = guiHelpBackgroundLockedColor) 

def resetGuiInstanceOptionVars(optionVarHolder,commandToRun = False):
    if optionVarHolder:
        purgeOptionVars(optionVarHolder)
    if commandToRun:    
        commandToRun()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Standard functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def forceSelectUpdate():
    selection = mc.ls(sl=True, flatten = True, long = True) or []
    transforms = mc.ls(type='transform') or []
    mc.select(cl=True)
    
    if transforms:
        for t in transforms:
            if t not in selection:
                print "Selecting '%s'"%t
                mc.select(t)
                break
        if selection:
            mc.select(selection)

def warning(message):
    try:
        mc.warning(message)
    except:
        if "'" in list(message):
            mel.eval('%s%s%s' %("$messageVar =  '", message,"'"))
        else:
            mel.eval('%s%s%s' %('$messageVar =  "', message,'"'))
            
        mel.eval('warning $messageVar')
        
def showAbout(uiWin):
    window = mc.window( title="About", iconName='About', widthHeight=(200, 55),backgroundColor = guiBackgroundColor )
    mc.columnLayout( adjustableColumn=True )
    mc.text(label=uiWin.toolName, ut = 'cgmUIHeaderTemplate')
    mc.separator(ut='cgmUIHeaderTemplate')
    mc.separator(ut='cgmUITemplate')
    mc.separator(ut='cgmUITemplate')
    mc.separator(ut='cgmUITemplate')
    mc.text(label='')
    mc.button(label='Visit Website', ut = 'cgmUITemplate', command=('import webbrowser;webbrowser.open("http://www.cgmonks.com")') )
    mc.button(label='Close', ut = 'cgmUITemplate', command=('mc.deleteUI(\"' + window + '\", window=True)') )
    mc.setParent( '..' )
    mc.showWindow( window )

def toggleModeState(OptionSelection,OptionList,OptionVarName,ListOfContainers,forceInt = False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Toggle for turning off and on the visbility of a list of containers

    ARGUMENTS:
    optionSelection(string) - this should point to the variable holding a (bool) value
    optionList(list) - the option selection must be in the optionList

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    visOn = OptionList.index(OptionSelection)
    if forceInt:
        mc.optionVar(iv=(OptionVarName,int(visOn)))
    else:
        mc.optionVar(sv=(OptionVarName,OptionSelection))

    cnt = 0
    for Container in ListOfContainers:
        if cnt == visOn:
            #Container(e=True,vis=True)
            setUIObjectVisibility(Container,True)
        else:
            #Container(e=True,vis=False)
            setUIObjectVisibility(Container,False)
        cnt+=1

def toggleOptionVarState(OptionSelection,OptionList,OptionVarName,forceInt = False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Toggle for turning off and on the visbility of a list of containers

    ARGUMENTS:
    optionSelection(string) - this should point to the variable holding a (bool) value
    optionList(list) - the option selection must be in the optionList

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    cnt = OptionList.index(OptionSelection)

    if forceInt:
        mc.optionVar(iv=(OptionVarName,int(cnt)))
    else:
        mc.optionVar(sv=(OptionVarName,OptionSelection))

def toggleMenuShowState(stateToggle, listOfItems):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Toggle for turning off and on the visibility of a menu section

    ARGUMENTS:
    stateToggle(string) - this should point to the variable holding a (bool) value
    listOfItems(list) - list of menu item names to change

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if stateToggle:
        newState = False
    else:
        newState = True

    for item in listOfItems:
        uiType = mc.objectTypeUI(item)
        if uiType == 'staticText':
            mc.text(item, edit = True, visible = newState)
        elif uiType == 'separator':
            mc.separator(item, edit = True, visible = newState)
        elif uiType == 'rowLayout':
            mc.rowLayout(item, edit = True, visible = newState)
        elif uiType == 'rowColumnLayout':
            mc.rowColumnLayout(item, edit = True, visible = newState)
        elif uiType == 'columnLayout':
            mc.columnLayout(item, edit = True, visible = newState)
        elif uiType == 'formLayout':
            mc.formLayout(item, edit = True, visible = newState)
            #print ('%s%s%s%s%s%s%s' % ('"python(mc.',uiType,"('",item,"', edit = True, visible = ",newState,'))"'))
            #mel.eval(('%s%s%s%s%s%s%s' % ('"python(mc.',uiType,"('",item,"', edit = True, visible = ",newState,'))"')))
            #mc.separator(item, edit = True, visible = newState)
        else:
            warning('%s%s%s' %('No idea what ', item, ' is'))
    return newState

def setUIObjectVisibility(item, visState):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Toggle for turning off and on the visibility of a menu section

    ARGUMENTS:
    stateToggle(string) - this should point to the variable holding a (bool) value
    listOfItems(list) - list of menu item names to change

    RETURNS:
    locatorName(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    uiType = mc.objectTypeUI(item)

    if uiType == 'staticText':
        mc.text(item, edit = True, visible = visState)
    elif uiType == 'separator':
        mc.separator(item, edit = True, visible = visState)
    elif uiType == 'rowLayout':
        mc.rowLayout(item, edit = True, visible = visState)
    elif uiType == 'rowColumnLayout':
        mc.rowColumnLayout(item, edit = True, visible = visState)
    elif uiType == 'columnLayout':
        mc.columnLayout(item, edit = True, visible = visState)
    elif uiType == 'formLayout':
        mc.formLayout(item, edit = True, visible = visState)
        #print ('%s%s%s%s%s%s%s' % ('"python(mc.',uiType,"('",item,"', edit = True, visible = ",visState,'))"'))
        #mel.eval(('%s%s%s%s%s%s%s' % ('"python(mc.',uiType,"('",item,"', edit = True, visible = ",visState,'))"')))
        #mc.separator(item, edit = True, visible = visState)
    else:
        warning('%s%s%s' %('No idea what ', item, ' is'))



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Load to fields
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doLoadSingleObjectToTextField(textFieldObject,variableToSet = False):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True,shortNames=True))
    buffer = textFieldObject(q=True,text = True )
    if selected:
        if len(selected) >= 2:
            warning('Only one object can be loaded')
        else:
            textFieldObject(edit=True,ut = 'cgmUILockedTemplate', text = selected[0],editable = False )
            if variableToSet:
                mc.optionVar(sv=(variableToSet,selected[0]))
    else:
        if buffer:
            textFieldObject(edit=True,text = '')
            if variableToSet:
                mc.optionVar(remove = variableToSet)
            warning('Object removed!')
        else:
            warning('You must select something.')


def doLoadMultipleObjectsToTextField(textFieldObject,objectsToLoad = False, variableToSet = False):
    if not objectsToLoad:
        objectsToLoad = (mc.ls (sl=True,flatten=True,shortNames=True))

    if objectsToLoad:
        textFieldObject(edit=True,ut = 'cgmUILockedTemplate', text = ';'.join(objectsToLoad),editable = False )
        if variableToSet:
            mc.optionVar(clearArray = variableToSet)
            for item in objectsToLoad:
                mc.optionVar(sva=(variableToSet,item))
    else:
        textFieldObject(edit=True,text = '')
        if variableToSet:
            mc.optionVar(clearArray = variableToSet)
        warning('You must select something.')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Standard functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def lineSplitter(text, size):
    lineList = []
    wordsList = text.split(' ')
    baseCnt = 0
    cnt = 0
    max = len(wordsList)
    while cnt < max:
        buffer = ' '.join(wordsList[baseCnt:cnt + 1])
        if len(buffer) < size:
            cnt+=1
        else:
            baseCnt = cnt+1
            cnt = baseCnt
            lineList.append(buffer)
    if baseCnt < max:
        lineList.append(' '.join(wordsList[baseCnt:]))
    return lineList


#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Buttons
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doButton2(parent, labelText, commandText = 'guiFactory.warning("Fix this")',annotationText = '',*a,**kw):
    if currentGenUI:
        return 	MelButton(parent,l=labelText,ut = 'cgmUITemplate',
                                 c= commandText,
                                 height = 20,
                                 align = 'center',
                                 annotation = annotationText,*a,**kw)
    else:
        return MelButton(parent,l=labelText, backgroundColor = [.75,.75,.75],
                         c= commandText,
                         height = 20,
                         align = 'center',
                         annotation = annotationText,*a,**kw)


def doButton(labelText, commandText = 'guiFactory.warning("Fix this")'):
    if currentGenUI:
        return mc.button(label= labelText, ut = 'cgmUITemplate', command=commandText )
    else:
        return mc.button(label= labelText, backgroundColor = [.75,.75,.75],command=commandText )

def doLoadToFieldButton(commandText = 'guiFactory.warning("Fix this")'):
    if currentGenUI:
        return mc.button(label='<<<', ut = 'cgmUITemplate', width = 50, recomputeSize = False, command=commandText )
    else:
        return mc.button(label='<<<', backgroundColor = [.75,.75,.75], width = 50, command=commandText )

def doReturnFontFromDialog(currentFont):
    fontChoice = mc.fontDialog()
    if fontChoice:
        return fontChoice
    else:
        warning("No font selected. You're stuck with " + currentFont)
        return currentFont

def doToggleIntOptionVariable(variable):
    varState = mc.optionVar( q= variable )
    mc.optionVar( iv=(variable, not varState))

def purgeOptionVars(varHolder):
    """
    Typically self.optionVars
    """
    sceneOptionVars = mc.optionVar(list=True)
    if varHolder:
        for var in varHolder:
            if var in sceneOptionVars:
                optionVars.purgeOptionVar(var)

def appendOptionVarList(self,varName):
    if varName not in self.optionVars:
        self.optionVars.append(varName)

def doCheckBox(self,parent,optionVarName,*a,**kw):
    appendOptionVarList(self,'cgmVar_KeyingTarget')	
    if not mc.optionVar( ex=optionVarName ):
        mc.optionVar( iv=(optionVarName, 0) )         

    return MelCheckBox(parent,
                       v = mc.optionVar(q=optionVarName),
                       onCommand = lambda *a: mc.optionVar(iv=(optionVarName,1)),
                       offCommand = lambda *a: mc.optionVar(iv=(optionVarName,0)),
                       *a,**kw)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Text and line breaks
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def header(text, align = 'center',overrideUpper =False):
    if not overrideUpper:
        text = text.upper()
    if currentGenUI:
        return mc.text(text, al = align, ut = 'cgmUIHeaderTemplate')
    else:
        return mc.text(('%s%s%s' %('>>> ',text,' <<<')), al = align)

def headerBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUIHeaderTemplate')
    else:
        return mc.separator(style='double')

def lineBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUITemplate')
    else:
        return mc.separator(ut='cgmUITemplate')

def lineSubBreak(vis=True):
    if currentGenUI:
        return mc.separator(ut='cgmUISubTemplate',vis=vis)
    else:
        return mc.separator(style='single',vis=vis)

def sectionBreak():
    if currentGenUI:
        return mc.separator(ut='cgmUISubTemplate')
    else:
        return mc.separator(style='single')

def instructions(text, align = 'center', vis = False, maxLineLength = 35):
    # yay, accounting for word wrap...
    if currentGenUI:
        buffer = mc.text(text, ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True, visible = vis)
        return [buffer]
    else:
        instructions = []
        textLines = lineSplitter(text, maxLineLength)
        instructions.append(mc.separator(style='single', visible = vis))
        for line in textLines:
            instructions.append(mc.text(line, h = 15, al = align, visible = vis))
        instructions.append(mc.separator(style='single', visible = vis))

        return instructions

def oldVersionInstructions(text, align = 'center'):
    # yay, accounting for word wrap...
    if currentGenUI:
        return [mc.text(text, ut = 'cgmUIInstructionsTemplate',al = 'center', ww = True, visible = False)]
    else:
        instructions = []
        textLines = lineSplitter(text, 35)
        instructions.append(mc.text(label = '>>> Warning <<<', visible = False))
        for line in textLines:
            instructions.append(mc.text(line, al = align, visible = False))
        instructions.append(mc.separator(style='single', visible = False))

        return instructions

def textBlock(text, align = 'center'):
    # yay, accounting for word wrap...
    if currentGenUI:
        return [mc.text(text,al = 'center', ww = True, visible = True)]
    else:
        textBlock = []
        textLines = lineSplitter(text, 50)
        textBlock.append(mc.separator(style = 'single', visible = True))
        for line in textLines:
            textBlock.append(mc.text(line, al = align, visible = True))
        textBlock.append(mc.separator(style = 'single', visible = True))
        return textBlock


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Progress Tracking
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doProgressWindow(winName='Progress Window',statusMessage = 'Progress...',startingProgress = 0, interruptableState = True):
    return  mc.progressWindow(title= winName,
                              progress=startingProgress,
                              status= statusMessage,
                              isInterruptable=interruptableState )

def doUpdateProgressWindow(statusMessage,stepInterval,stepRange,reportItem=False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tools to do a maya progress window. This function and doEndMayaProgressBar are a part of a set.

    ARGUMENTS:
    statusMessage(string) - starting status message
    stepInterval(int)
    stepRange(int)
    reportItem(string/bool) - If you want a percentage to be shown, put False(default - False)

    RETURNS:
    mayaMainProgressBar(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """

    maxRange = int(stepRange)
    percent = (float(stepInterval)/maxRange)
    progressAmount = int(percent * 100)

    # Check if the dialog has been cancelled
    if mc.progressWindow(query=True, isCancelled=True ) :
        if reportItem != False:
            warning('%s%s' %('Stopped at ',str(reportItem)))
            return 'break'
        else:
            warning('%s%s%s' %('Stopped at ',str(progressAmount),'%'))
            return 'break'

    # Check if end condition has been reached
    if mc.progressWindow( query=True, progress=True ) >= 100 :
        return 'break'

    if reportItem != False:
        mc.progressWindow(edit=True, progress=progressAmount, status=(statusMessage+  str(reportItem)) )
    else:
        mc.progressWindow(edit=True, progress=progressAmount, status=(statusMessage+ `stepInterval` ) )

def doCloseProgressWindow():
    mc.progressWindow(endProgress=1)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doStartMayaProgressBar(stepMaxValue = 100, statusMessage = 'Calculating....',interruptableState = True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tools to do a maya progress bar. This function and doEndMayaProgressBar are a part of a set. Example
    usage:

    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(int(number))
    for n in range(int(number)):
    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
    break
    mc.progressBar(mayaMainProgressBar, edit=True, status = (n), step=1)

    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

    ARGUMENTS:
    stepMaxValue(int) - max number of steps (defualt -  100)
    statusMessage(string) - starting status message
    interruptableState(bool) - is it interuptible or not (default - True)

    RETURNS:
    mayaMainProgressBar(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mayaMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
    mc.progressBar( mayaMainProgressBar,
                    edit=True,
                    beginProgress=True,
                    isInterruptable=interruptableState,
                    status=statusMessage,
                    maxValue= stepMaxValue )
    return mayaMainProgressBar

def doEndMayaProgressBar(mayaMainProgressBar):
    mc.progressBar(mayaMainProgressBar, edit=True, endProgress=True)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doProgressBar(winName,trackedList,statusMessage):
    mc.progressBar()


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Reporting
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def report(message):
    print ("# Report: %s #"%message)
    
def doPrintReportStart(label = False):
    if label and type(label) is str:
        start = '#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> '
        end = ' - start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        print "%s%s%s"%(start,label,end)
        
    else:
        print '#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'

def doPrintReportBreak():
    print '#---------------------------------------------------------------------------'

def doPrintReportEnd(label = False):
    print '#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> End >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'





"""
class cgmBridge:pass   

def classBridge_Puppet():
    try:
        mel.eval('python("cgmPuppet")')
    except:
        report("Creating puppet class bridge...")
        mel.eval('python("from cgm.lib import guiFactory;cgmPuppet = guiFactory.cgmBridge();")')	

def classBridge_Puppet2():
    try:
        cgmPuppet
    except:
        cgmPuppet = cgmBridge()
"""        
def testBridge():
    #from cgm.lib.classes import Bridge 
    globals()['cgmBridge'] = BridgeCGM()
    print cgmBridge.__dict__.keys()
    print 'cgmBridge' in globals()
    cgmBridge.__dict__['test'] = 1
    print cgmBridge.__dict__.keys()


    