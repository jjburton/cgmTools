# 
#   -= ml_utilities.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 2, 2011-05-04
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_utilities.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_utilities
#     ml_utilities.help()
# From MEL, this looks like:
#     python("import ml_utilities;ml_utilities.help()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# ml_utilities isn't a stand alone tool, but rather it's a collection of support functions
# that are required by several of the tools in this library. The individual tools will tell
# you if this script is required.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# ml_utilities isn't a stand alone tool, and so it isn't meant to be used directly.
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 2

import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya
from functools import partial
import shutil, os, re

def help():
    '''
    This just launches the online help and serves as a placeholder for the default function for this script.
    '''
    mc.showHelp('http://morganloomis.com/wiki/tools.html#ml_utilities', absolute=True)


def upToDateCheck(revision, prompt=True):
    '''
    This is a check that can be run by scripts that import ml_utilities to make sure they
    have the correct version.
    '''
    if revision > __revision__:
        if prompt and mc.optionVar(query='ml_utilities_revision') < revision:
            result = mc.confirmDialog( title='Module Out of Date', 
                        message='Your version of ml_utilities may be out of date for this tool. Without the latest file you may encounter errors.',
                        button=['Download Latest Revision','Ignore', "Don't Ask Again"], 
                        defaultButton='Download Latest Revision', cancelButton='Ignore', dismissString='Ignore' )
            
            if result == 'Download Latest Revision':
                mc.showHelp('http://morganloomis.com/download/ml_utilities.py', absolute=True)
            elif result == "Don't Ask Again":
                mc.optionVar(intValue=('ml_utilities_revision', revision))
        return False
    return True


def createHotkey(command, name, description=''):
    '''
    Open up the hotkey editor to create a hotkey from the specified command
    '''
    
    mm.eval('hotkeyEditor')
    mc.textScrollList('HotkeyEditorCategoryTextScrollList', edit=True, selectItem='User')
    mm.eval('hotkeyEditorCategoryTextScrollListSelect')
    mm.eval('hotkeyEditorCreateCommand')

    mc.textField('HotkeyEditorNameField', edit=True, text=name)
    mc.textField('HotkeyEditorDescriptionField', edit=True, text=description)
    mc.scrollField('HotkeyEditorCommandField', edit=True, text=command)


def createShelfButton(command, label, name=None, description='', 
                       image='render_useBackground', #this default image is a "!"
                       labelColor=(1, 0.5, 0), 
                       labelBackgroundColor=(0, 0, 0, 0.5), 
                       backgroundColor=None
                       ):
    '''
    Create a shelf button for the command on the current shelf
    '''
    #some good default icons:
    #menuIconConstraints - !
    #render_useBackground - circle
    #render_volumeShader - black dot
    #menuIconShow - eye
    
    gShelfTopLevel = mm.eval('$temp=$gShelfTopLevel')
    if not mc.tabLayout(gShelfTopLevel, exists=True):
        OpenMaya.MGlobal.displayWarning('Shelf not visbile.')
        return

    if not name:
        name = label
        
    shelfTab = mc.shelfTabLayout(gShelfTopLevel, query=True, selectTab=True)
    shelfTab = gShelfTopLevel+'|'+shelfTab
    
    #add additional args depending on what version of maya we're in
    kwargs = dict()
    if mm.eval('getApplicationVersionAsFloat') >= 2009:
        kwargs['commandRepeatable'] = True
    if mm.eval('getApplicationVersionAsFloat') >= 2011:
        kwargs['overlayLabelColor'] = labelColor
        kwargs['overlayLabelBackColor'] = labelBackgroundColor
        if backgroundColor:
            kwargs['enableBackground'] = bool(backgroundColor)
            kwargs['backgroundColor'] = backgroundColor
        image+='.png'
    else:
        image+='.xpm'

    return mc.shelfButton(parent=shelfTab, label=name, command=command,
                          imageOverlayLabel=label, image=image, annotation=description, 
                          width=32, height=32, align='center', **kwargs)


def deselectChannels():
    '''
    Deselect selected channels in the channelBox
    by clearing selection and then re-selecting
    '''
    
    if not getSelectedChannels():
        return
    sel = mc.ls(sl=True)
    mc.select(clear=True)
    mc.evalDeferred(partial(mc.select,sel))


def formLayoutGrid(form, controls, offset=1):
    '''
    Controls should be a list of lists, and this will arrange them in a grid
    '''

    kwargs = {'edit':True, 'attachPosition':list()}
    rowInc = 100/len(controls)
    colInc = 100/len(controls[0])
    position = {'left':0,'right':100,'top':0,'bottom':100}
    
    for r,row in enumerate(controls):
        position['top'] = r*rowInc
        position['bottom'] = (r+1)*rowInc
        for c,ctrl in enumerate(row):
            position['left'] = c*colInc
            position['right'] = (c+1)*colInc
            for k in position.keys():
                kwargs['attachPosition'].append((ctrl, k, offset, position[k]))

    mc.formLayout(form, **kwargs)


def frameRange(start=None, end=None):
    '''
    Returns the frame range based on the highlighted timeslider,
    or otherwise the playback range.
    '''
    
    if not start and not end:
        gPlayBackSlider = mm.eval('$temp=$gPlayBackSlider')
        if mc.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
            frameRange = mc.timeControl(gPlayBackSlider, query=True, rangeArray=True)
            return frameRange
        else:
            start = mc.playbackOptions(query=True, min=True)
            end = mc.playbackOptions(query=True, max=True)
    
    return start,end  


def getChannelFromAnimCurve(curve):
    '''
    Finding the channel associated with a curve has gotten really complicated since animation layers.
    This is a recursive function which walks connections from a curve until an animated channel is found.
    '''

    #we need to save the attribute for later.
    attr = ''
    if '.' in curve:
        curve, attr = curve.split('.')
        
    nodeType = mc.nodeType(curve)
    if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
        source = mc.listConnections(curve+'.output', source=False, plugs=True)
        if not source and nodeType=='animBlendNodeAdditiveRotation':
            #if we haven't found a connection from .output, then it may be a node that uses outputX, outputY, etc.
            #get the proper attribute by using the last letter of the input attribute, which should be X, Y, etc.
            source = mc.listConnections(curve+'.output'+attr[-1], source=False, plugs=True)
        if source:
            nodeType = mc.nodeType(source[0])
            if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
                return getChannelFromAnimCurve(source[0])
            return source[0]


def getCurrentCamera():
    '''
    Returns the camera that you're currently looking through
    '''
    
    panel = mc.getPanel(withFocus=True)
    camShape = mc.modelEditor(panel, query=True, camera=True)

    if not camShape:
        return False
    
    if mc.nodeType(camShape) == 'transform':
        return camShape
    elif mc.nodeType(camShape) == 'camera':
        return mc.listRelatives(camShape, parent=True)[0]


def getNamespace(node):
    '''Returns the namespace of a node with simple string parsing'''
    
    namespace = ''
    
    if node and ':' in node:
        namespace = node.partition(':')[0]
        namespace+=':'
    return namespace


def getSelectedChannels():
    '''
    Return channels that are selected in the channelbox
    '''
    
    if not mc.ls(sl=True):
        return
    gChannelBoxName = mm.eval('$temp=$gChannelBoxName')
    sma = mc.channelBox(gChannelBoxName, query=True, sma=True)
    ssa = mc.channelBox(gChannelBoxName, query=True, ssa=True)
    sha = mc.channelBox(gChannelBoxName, query=True, sha=True)
                
    channels = list()
    if sma:
        channels.extend(sma)
    if ssa:
        channels.extend(ssa)
    if sha:
        channels.extend(sha)

    return channels


def renderShelfIcon(name='tmp', width=32, height=32):
    '''
    This renders a shelf-sized icon and hopefully places it in your icon directory
    '''
    imageName=name

    #getCamera
    cam = getCurrentCamera()
    
    #save these values for resetting
    currentRenderer = mc.getAttr('defaultRenderGlobals.currentRenderer')
    imageFormat = mc.getAttr('defaultRenderGlobals.imageFormat')

    mc.setAttr('defaultRenderGlobals.currentRenderer', 'mayaSoftware', type='string')

    mayaVersion = mm.eval('getApplicationVersionAsFloat')
    
    imageFormat = 50 #XPM
    if mayaVersion >= 2011:
        imageFormat = 32 #PNG

    mc.setAttr('defaultRenderGlobals.imageFormat', imageFormat)
    mc.setAttr('defaultRenderGlobals.imfkey', 'xpm', type='string')
    #here's the imageName
    mc.setAttr('defaultRenderGlobals.imageFilePrefix', imageName, type='string')

    mc.setAttr(cam+'.backgroundColor', 0.8,0.8,0.8, type='double3')
    #need to reset this afterward
    
    image = mc.render(cam, xresolution=width, yresolution=height)
    base = os.path.basename(image)

    #here we attempt to move the rendered icon to a more generalized icon location
    #we want the default user icon directory, so match up a directory in the icon invironment path
    appDir = os.environ['MAYA_APP_DIR']
    for each in os.environ['XBMLANGPATH'].split(':'):
        #on some linux systems each path ends with %B, for some reason
        iconPath = each.replace('%B','')
        if iconPath.startswith(appDir) and os.path.exists(iconPath):
            newPath = os.path.abspath(iconPath)
            newPath = '/'.join((newPath, base))
            image = shutil.move(image, newPath)
            image = newPath
            break
            
    #reset
    mc.setAttr('defaultRenderGlobals.currentRenderer', currentRenderer, type='string')
    mc.setAttr('defaultRenderGlobals.imageFormat', imageFormat)
    
    return image


class IsolateViews():
    '''
    Isolates selection with nothing selected for all viewports
    This speeds up any process that causes the viewport to refresh,
    such as baking or changing time. 
    '''
    
    def __enter__(self):
    
        self.sel = mc.ls(sl=True)
        self.modelPanels = mc.getPanel(type='modelPanel')
        self.isolate(True)
        
        mc.select(clear=True)
        
        #save and turn off settings that might print to the script editor
        self.resetCycleCheck = mc.cycleCheck(query=True, evaluation=True)
        mc.cycleCheck(evaluation=False)
        
        self.resetAutoKey = mc.autoKeyframe(query=True, state=True)
        mc.autoKeyframe(state=False)
        
    
    def __exit__(self, *args):
            
        #reset settings
        mc.cycleCheck(evaluation=self.resetCycleCheck)
        mc.autoKeyframe(state=self.resetAutoKey)
        
        if self.sel:
            mc.select(self.sel)
            
        self.isolate(False)
        
    
    def isolate(self, state):
    
        mc.select(clear=True)
        for each in self.modelPanels:
            mc.isolateSelect(each, state=state)


class UndoChunk():
    '''
    In versions of maya before 2011, python doesn't always undo properly, so in 
    some cases we have to manage the undo queue ourselves.
    '''
    
    def __enter__(self):
        '''open the undo chunk'''
        if mm.eval('getApplicationVersionAsFloat') < 2011:
            mc.undoInfo(openChunk=True)
            
    def __exit__(self, *args):
        '''close the undo chunk'''
        if mm.eval('getApplicationVersionAsFloat') < 2011:
            mc.undoInfo(closeChunk=True)


class MlUi():
    '''
    Window template for consistency
    '''

    def __init__(self, name, title, width=400, height=200, info=''):
    
        self.name = name
        self.title = title
        self.width = width
        self.height = height
        self.info = info

    def __enter__(self):
        '''
        Initialize the UI
        '''
        if mc.window(self.name, exists=True):
            mc.deleteUI(self.name)

        mc.window(self.name, title='ml :: '+self.title, iconName=self.title, width=self.width, height=self.height)

        self.form = mc.formLayout()
        self.column = mc.columnLayout(adj=True)

        mc.rowLayout( numberOfColumns=2, columnWidth2=(34, self.width-34), adjustableColumn=2, 
                    columnAlign2=('right','left'),
                    columnAttach=[(1, 'both', 0), (2, 'both', 8)] )

        mc.text(label=' _ _ |\n| | | |')
        mc.popupMenu(button=1)
        mc.menuItem(label='Help', command=('import maya.cmds;maya.cmds.showHelp("http://morganloomis.com/wiki/tools.html#'+self.name+'",absolute=True)'))
        mc.text(label=self.info)
        mc.setParent('..')
        mc.separator(height=8, style='single')
        return self
    
    
    def __exit__(self, *args):
        '''
        Finalize the UI
        '''
        
        mc.setParent(self.form)

        frame = mc.frameLayout(labelVisible=False)
        mc.helpLine()
        
        mc.formLayout( self.form, edit=True,
                     attachForm=((self.column, 'top', 0), (self.column, 'left', 0),
                                 (self.column, 'right', 0), (frame, 'left', 0),
                                 (frame, 'bottom', 0), (frame, 'right', 0)),
                     attachNone=((self.column, 'bottom'), (frame, 'top')) )

        mc.showWindow(self.name)
        mc.window(self.name, edit=True, width=self.width, height=self.height)

        
    def buttonWithPopup(self, label=None, command=None, annotation='', shelfLabel='ml', shelfIcon='render_useBackground'):
        '''
        Create a button and attach a popup menu to a control with options to create a shelf button or a hotkey.
        The argCommand should return a kwargs dictionary that can be used as args for the main command.
        '''
        
        if not shelfLabel:
            shelfLabel = label
            
        button = mc.button(label=label, command=command, annotation=annotation+' Or right click for more options.')
        
        mc.popupMenu()
        self.shelfMenuItem(command=command, annotation=annotation, shelfLabel=shelfLabel, shelfIcon=shelfIcon)
        self.hotkeyMenuItem(command=command, annotation=annotation)
        return button


    def shelfMenuItem(self, command=None, annotation='', shelfLabel='ml', shelfIcon='menuIconConstraints', menuLabel='Create Shelf Button'):
        '''
        This creates a menuItem that can be attached to a control to create a shelf menu with the given command
        '''
        pythonCommand = 'import '+self.name+';'+self.name+'.'+command.__name__+'()'
        
        mc.menuItem(label=menuLabel,
                    command='import ml_utilities;ml_utilities.createShelfButton(\"'+pythonCommand+'\", \"'+shelfLabel+'\", \"'+self.name+'\", description=\"'+annotation+'\", image=\"'+shelfIcon+'\")',
                    enableCommandRepeat=True,
                    image=shelfIcon)

    
    def hotkeyMenuItem(self, command=None, annotation='', menuLabel='Create Hotkey'):
        '''
        This creates a menuItem that can be attached to a control to create a hotkey with the given command
        '''
        melCommand = 'python(\\\"import '+self.name+';'+self.name+'.'+command.__name__+'()'+'\\\");'
        mc.menuItem(label=menuLabel,
                    command='import ml_utilities;ml_utilities.createHotkey(\"'+melCommand+'\", \"'+self.name+'\", description=\"'+annotation+'\")',
                    enableCommandRepeat=True,
                    image='commandButton')


class Dragger(object):

    def __init__(self,
                name = 'mlDraggerContext',
                title = 'Dragger',
                defaultValue=0,
                minValue=None,
                maxValue=None,
                multiplier=0.01,
                cursor='hand'
                ):
        
        self.multiplier = multiplier
        self.defaultValue = defaultValue
        self.minValue = minValue
        self.maxValue = maxValue
        self.cycleCheck = mc.cycleCheck(query=True, evaluation=True)
        
        self.draggerContext = name
        if not mc.draggerContext(self.draggerContext, exists=True):
            self.draggerContext = mc.draggerContext(self.draggerContext)
                                                    
        mc.draggerContext(self.draggerContext, edit=True,
                        pressCommand=self.press, 
                        dragCommand=self.drag,
                        releaseCommand=self.release,
                        cursor=cursor,
                        drawString=title,
                        undoMode='all'
                        )
                                                    
    
    def press(self, *args):
        '''
        Be careful overwriting the press method in child classes, because of the undoInfo openChunk
        '''
        
        self.anchorPoint = mc.draggerContext(self.draggerContext, query=True, anchorPoint=True)
        self.modifier = mc.draggerContext(self.draggerContext, query=True, modifier=True)
        self.button = mc.draggerContext(self.draggerContext, query=True, button=True)
        #dragString
        
        # This makes it so the script editor doesn't get spammed by a cycle in the puppet
        mc.cycleCheck(evaluation=False)
        
        # This turns off the undo queue until we're done dragging, so we can undo it.
        mc.undoInfo(openChunk=True)
        
    def drag(self, *args):
        
        self.dragPoint = mc.draggerContext(self.draggerContext, query=True, dragPoint=True)
        
        self.x = ((self.dragPoint[0] - self.anchorPoint[0]) * self.multiplier) + self.defaultValue
        self.y = ((self.dragPoint[1] - self.anchorPoint[1]) * self.multiplier) + self.defaultValue
        
        if self.minValue is not None and self.x < self.minValue:
            self.x = self.minValue
        if self.maxValue is not None and self.x > self.maxValue:
            self.x = self.maxValue
        
        #dragString
        if self.modifier == 'control':
            if self.button == 1:
                self.dragControlLeft()
            elif self.button == 2:
                self.dragControlMiddle()
        elif self.modifier == 'shift':
            if self.button == 1:
                self.dragShiftLeft()
            elif self.button == 2:
                self.dragShiftMiddle()
        else:
            if self.button == 1:
                self.dragLeft()
            elif self.button == 2:
                self.dragMiddle()
        
        mc.refresh()
    
    def release(self, *args):
        '''
        Be careful overwriting the release method in child classes. Not closing the undo chunk leaves maya in a sorry state.
        '''
        # close undo chunk and turn cycle check back on
        mc.undoInfo(closeChunk=True)
        mc.cycleCheck(evaluation=self.cycleCheck)
        mm.eval('SelectTool')
    
    def drawString(self, message):
        '''
        Creates a string message at the position of the pointer.
        '''
        mc.draggerContext(self.draggerContext, edit=True, drawString=message)
        
    def dragLeft(self):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragMiddle(self):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
        
    def dragControlLeft(self):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragControlMiddle(self):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
        
    def dragShiftLeft(self):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragShiftMiddle(self):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
    
    #no drag right, because that is monopolized by the right click menu
    #no alt drag, because that is used for the camera
    
    def setTool(self):
        mc.setToolTo(self.draggerContext)
