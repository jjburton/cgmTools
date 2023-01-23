# 
#   -= ml_utilities.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 8, 2012-11-15
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_utilities.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_utilities
#     ml_utilities._showHelpCommand()
# From MEL, this looks like:
#     python("import ml_utilities;ml_utilities._showHelpCommand()");
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
# However, you can certainly call these functions if they seem useful in your own scripts.
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 8

import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya
from functools import partial
import shutil, os, re, sys

#declare some variables
websiteURL = 'http://morganloomis.com'
wikiURL = websiteURL+'/wiki/tools.html'


def _showHelpCommand(url):
    '''
    This just returns the maya command for launching a wiki page, since that gets called a few times
    '''
    return 'import maya.cmds;maya.cmds.showHelp("'+url+'",absolute=True)'


def main():
    '''
    This just launches the online help and serves as a placeholder for the default function for this script.
    '''
    mc.showHelp(wikiURL+'#ml_utilities', absolute=True)
    

def upToDateCheck(revision, prompt=True):
    '''
    This is a check that can be run by scripts that import ml_utilities to make sure they
    have the correct version.
    '''
    
    if not '__revision__' in locals():
        return
    
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


def constrain(source, destination, translate=True, rotate=True, scale=False):
    '''
    Constrain two objects, even if they have some locked attributes.
    '''
    
    transAttr = None
    rotAttr = None
    scaleAttr = None
    
    if translate:
        transAttr = mc.listAttr(destination, keyable=True, unlocked=True, string='translate*')
    if rotate:
        rotAttr = mc.listAttr(destination, keyable=True, unlocked=True, string='rotate*')
    if scale:
        scaleAttr = mc.listAttr(destination, keyable=True, unlocked=True, string='scale*')

    rotSkip = list()
    transSkip = list()

    for axis in ['x','y','z']:
        if transAttr and not 'translate'+axis.upper() in transAttr:
            transSkip.append(axis)
        if rotAttr and not 'rotate'+axis.upper() in rotAttr:
            rotSkip.append(axis)

    if not transSkip:
        transSkip = 'none'
    if not rotSkip:
        rotSkip = 'none'
    
    constraints = list()
    if rotAttr and transAttr and rotSkip == 'none' and transSkip == 'none':
        constraints.append(mc.parentConstraint(source, destination))
    else:
        if transAttr:
            constraints.append(mc.pointConstraint(source, destination, skip=transSkip))
        if rotAttr:
            constraints.append(mc.orientConstraint(source, destination, skip=rotSkip))
            
    return constraints


def createAnimLayer(nodes=None, name=None, namePrefix='', override=True):
    '''
    Create an animation layer, add nodes, and select it.
    '''
    
    #if there's no layer name, generate one
    if not name:
        if namePrefix:
            namePrefix+='_'
        if nodes:
            shortNodes = mc.ls(nodes, shortNames=True)
            shortNodes = [x.rpartition(':')[-1] for x in shortNodes]
            #if there's just one node, use it's name minus the namespace
            if len(shortNodes) == 1:
                name = namePrefix+shortNodes[0]
            else:
                #try to find the longest common substring 
                commonString = longestCommonSubstring(shortNodes)
                if commonString:
                    name = commonString
                elif ':' in nodes[0]:
                    #otherwise use the namespace if it has one
                    name = nodes[0].rpartition(':')[-1]
        if not name:
            if not namePrefix:
                namePrefix = 'ml_'
            name = namePrefix+'animLayer'
    
    layer = mc.animLayer(name, override=override)
    
    #add the nodes to the layer
    if nodes:
        sel = mc.ls(sl=True)
        mc.select(nodes)
        mc.animLayer(layer, edit=True, addSelectedObjects=True)
        if sel:
            mc.select(sel)
        else:
            mc.select(clear=True)
    
    #select the layer
    selectAnimLayer(layer)
    return layer
    

def selectAnimLayer(animLayer=None):
    '''
    Select only the specified animation layer
    '''
    #deselect all layers
    for each in mc.ls(type='animLayer'):
        mc.animLayer(each, edit=True, selected=False, preferred=False)
    if animLayer:
        mc.animLayer(animLayer, edit=True, selected=True, preferred=True)


def getSelectedAnimLayers():
    '''
    Return the names of the layers which are selected
    '''
    layers = list()
    for each in mc.ls(type='animLayer'):
        if mc.animLayer(each, query=True, selected=True):
            layers.append(each)
    return layers
    

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


def createShelfButton(command, label='', name=None, description='', 
                       image=None, #the default image is a circle
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
        OpenMaya.MGlobal.displayWarning('Shelf not visible.')
        return

    if not name:
        name = label
    
    if not image:
        image = getIcon(name)
    if not image:
        image = 'render_useBackground'
        
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
            for k in list(position.keys()):
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
    

def getChannelFromAnimCurve(curve, plugs=True):
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
        source = mc.listConnections(curve+'.output', source=False, plugs=plugs)
        if not source and nodeType=='animBlendNodeAdditiveRotation':
            #if we haven't found a connection from .output, then it may be a node that uses outputX, outputY, etc.
            #get the proper attribute by using the last letter of the input attribute, which should be X, Y, etc.
            #if we're not returning plugs, then we wont have an attr suffix to use, so just use X.
            attrSuffix = 'X'
            if plugs:
                attrSuffix = attr[-1]
                
            source = mc.listConnections(curve+'.output'+attrSuffix, source=False, plugs=plugs)
        if source:
            nodeType = mc.nodeType(source[0])
            if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
                return getChannelFromAnimCurve(source[0], plugs=plugs)
            return source[0]


def getCurrentCamera():
    '''
    Returns the camera that you're currently looking through.
    If the current highlighted panel isn't a modelPanel, 
    '''
    
    panel = mc.getPanel(withFocus=True)
    
    if mc.getPanel(typeOf=panel) != 'modelPanel':
        #just get the first visible model panel we find, hopefully the correct one.
        for p in mc.getPanel(visiblePanels=True):
            if mc.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                mc.setFocus(panel)
                break
    
    if mc.getPanel(typeOf=panel) != 'modelPanel':
        OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
        return False
    
    camShape = mc.modelEditor(panel, query=True, camera=True)

    if not camShape:
        return False
    
    if mc.nodeType(camShape) == 'transform':
        return camShape
    elif mc.nodeType(camShape) == 'camera':
        return mc.listRelatives(camShape, parent=True)[0]


def getFrameRate():
    '''
    Return an int of the current frame rate
    '''
    currentUnit = mc.currentUnit(query=True, time=True)
    if currentUnit == 'film':
        return 24
    if currentUnit == 'show':
        return 48
    if currentUnit == 'pal':
        return 25
    if currentUnit == 'ntsc':
        return 30
    if currentUnit == 'palf':
        return 50
    if currentUnit == 'ntscf':
        return 60
    if 'fps' in currentUnit:
        return int(currentUnit.substitute('fps',''))
    
    return 1


def getHoldTangentType():
    '''
    Returns the best in and out tangent type for creating a hold with the current tangent settings.
    '''
    tangentType = mc.keyTangent(query=True, g=True, ott=True)[0]
    
    if tangentType=='linear':
        return 'linear','linear'
    if tangentType=='step':
        return 'linear','step'
    if tangentType == 'plateau' or tangentType == 'spline' or mm.eval('getApplicationVersionAsFloat') < 2012:
        return 'plateau','plateau'
    return 'auto','auto'


def getIcon(name):
    '''
    Check if an icon name exists, and return with proper extension.
    Otherwise return standard warning icon.
    '''
    
    ext = '.png'
    if mm.eval('getApplicationVersionAsFloat') < 2011:
        ext = '.xpm'
    
    if not name.endswith('.png') and not name.endswith('.xpm'):
        name+=ext
    
    for each in os.environ['XBMLANGPATH'].split(':'):
        #on some linux systems each path ends with %B, for some reason
        iconPath = os.path.abspath(each.replace('%B',''))
        iconPath = os.path.join(iconPath,name)
        if os.path.exists(iconPath):        
            return name
    
    return None
    return 'menuIconConstraints'+ext


def getIconPath():
    '''
    Find the icon path
    '''
    
    appDir = os.environ['MAYA_APP_DIR']
    for each in os.environ['XBMLANGPATH'].split(':'):
        #on some linux systems each path ends with %B, for some reason
        iconPath = each.replace('%B','')
        if iconPath.startswith(appDir):
            iconPath = os.path.abspath(iconPath)
            if os.path.exists(iconPath):
                return iconPath

    
def getNamespace(node):
    '''Returns the namespace of a node with simple string parsing. Now supports nested namespaces.'''
    
    namespace = ''
    
    if node and mc.objExists(node):
        shortName = mc.ls(node, shortNames=True)[0]
        if ':' in shortName:
            namespace = shortName.rpartition(':')[0]
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


def listAnimCurves(objOrAttrs):
    '''
    This lists connections to all types of animNodes
    '''
    
    animNodes = list()
    
    tl = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTL')
    ta = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTA')
    tu = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTU')
    
    if tl:
        animNodes.extend(tl)
    if ta:
        animNodes.extend(ta)
    if tu:
        animNodes.extend(tu)
    
    return animNodes
    
    
def longestCommonSubstring(data):
    '''
    Returns the longest string that is present in the list of strings.
    '''
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr):
                    find = data[0][i:i+j]
                    if len(data) < 1 and len(find) < 1:
                        continue
                    found = True
                    for k in range(len(data)):
                        if find not in data[k]:
                            found = False
                    if found:
                        substr = data[0][i:i+j]
    return substr


def minimizeRotationCurves(obj):
    '''
    Sets rotation animation to the value closest to zero.
    '''
    
    rotateCurves = mc.keyframe(obj, attribute=('rotateX','rotateY', 'rotateZ'), query=True, name=True)
    
    if not rotateCurves or len(rotateCurves) < 3:
        return
    
    keyTimes = mc.keyframe(rotateCurves, query=True, timeChange=True)
    tempFrame = sorted(keyTimes)[0] - 1
    
    #set a temp frame
    mc.setKeyframe(rotateCurves, time=(tempFrame,), value=0)
    
    #euler filter
    mc.filterCurve(rotateCurves)
    
    #delete temp key
    mc.cutKey(rotateCurves, time=(tempFrame,))
    

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
    newPath = getIconPath()
    newPath = os.path.join(newPath, base)
    shutil.move(image, newPath)
    image = newPath
            
    #reset
    mc.setAttr('defaultRenderGlobals.currentRenderer', currentRenderer, type='string')
    mc.setAttr('defaultRenderGlobals.imageFormat', imageFormat)
    
    return image
    
    
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
        self.button = mc.draggerContext(self.draggerContext, query=True, button=True)
        #dragString
        
        # This makes it so the script editor doesn't get spammed by a cycle in the puppet
        mc.cycleCheck(evaluation=False)
        
        # This turns off the undo queue until we're done dragging, so we can undo it.
        mc.undoInfo(openChunk=True)
        
    def drag(self, *args):
        '''
        This is what is actually run during the drag, updating the coordinates and calling the 
        placeholder drag functions depending on which button is pressed.
        '''
        
        self.dragPoint = mc.draggerContext(self.draggerContext, query=True, dragPoint=True)
        
        #if this doesn't work, try getmodifier
        self.modifier = mc.draggerContext(self.draggerContext, query=True, modifier=True)
        
        self.x = ((self.dragPoint[0] - self.anchorPoint[0]) * self.multiplier) + self.defaultValue
        self.y = ((self.dragPoint[1] - self.anchorPoint[1]) * self.multiplier) + self.defaultValue
        
        if self.minValue is not None and self.x < self.minValue:
            self.x = self.minValue
        if self.maxValue is not None and self.x > self.maxValue:
            self.x = self.maxValue
        
        #dragString
        if self.modifier == 'control':
            if self.button == 1:
                self.dragControlLeft(*args)
            elif self.button == 2:
                self.dragControlMiddle(*args)
        elif self.modifier == 'shift':
            if self.button == 1:
                self.dragShiftLeft(*args)
            elif self.button == 2:
                self.dragShiftMiddle(*args)
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
        
    def dragLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
        
    def dragControlLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragControlMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
        
    def dragShiftLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragShiftMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
    
    #no drag right, because that is monopolized by the right click menu
    #no alt drag, because that is used for the camera
    
    def setTool(self):
        mc.setToolTo(self.draggerContext)


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


class KeySelection(object):
    '''
    
    '''
    
    def __init__(self, *args):
    
        #if args are passed in, this has been called from and out of date script. Warn and fail.
        if args:
            print('')
            print("Because of an update to ml_utilities, the tool you're trying to run is deprecated and needs to be updated as well.")
            print("Please visit http://morganloomis.com/downloads and download the latest version of this tool.")
            OpenMaya.MGlobal.displayError('Tool out of date. See script editor for details.')
            return
        
        self.shortestTime = getFrameRate()/6000.0
        
        #node variables
        self.nodeSelection = mc.ls(sl=True)
        self._nodes = list()
        self._curves = list()
        self._channels = list()
        
        #time variables 
        self.currentTime = mc.currentTime(query=True)
        self._time = None
        self._timeRangeStart = None
        self._timeRangeEnd = None
        
        #keyframe command variables
        self.selected = False
        
        #other housekeeping
        self._curvesCulled = False
        
    @property
    def curves(self):
        '''
        The keySelections's animation curve list.
        '''
        
        # if self._curves is False or None, then it has been initialized and curves haven't been found.
        if self._curves == []:
            
            #find anim curves connected to channels or nodes
            for each in (self._channels, self._nodes):
                if not each:
                    continue
                # this will only return time based keyframes, not driven keys
                self._curves = mc.keyframe(each, time=(':',), query=True, name=True)
                    
                if self._curves:
                    self._curvesCulled = False
                    break
            if not self._curves:
                self._curves = False
                
        # need to remove curves which are unkeyable
        # supposedly referenced keys are keyable in 2013, I'll need to test that and update
        if self._curves and not self._curvesCulled:
            remove = list()
            for c in self._curves:
                if mc.referenceQuery(c, isNodeReferenced=True):
                    remove.append(c)
                else:
                    plug = mc.listConnections('.'.join((c,'output')), source=False, plugs=True)[0]
                    if not mc.getAttr(plug, keyable=True) and not mc.getAttr(plug, settable=True):
                        remove.append(c)
            if remove:
                for r in remove:
                    self._curves.remove(r)
            self._curvesCulled = True
        
        return self._curves
    
    @property
    def channels(self):
        '''
        The keySelection's channels list.
        '''
        
        if not self._channels:
        
            if self._curves:
                for c in self._curves:
                    self._channels.append(getChannelFromAnimCurve(c))
            elif self._nodes:
                for obj in self._nodes:
                    keyable = mc.listAttr(obj, keyable=True, unlocked=True, hasData=True, settable=True)
                    if keyable:
                        for attr in keyable:
                            self._channels.append('.'.join((obj, attr)))
                         
        return self._channels
            
    @property
    def nodes(self):
        '''
        The keySelection's node list.
        '''
        
        if not self._nodes:
            
            if self._curves:
                self._nodes = list()
                for c in self._curves:
                    n = getChannelFromAnimCurve(c, plugs=False)
                    if not n in self._nodes:
                        self._nodes.append(n)
            elif self._channels:
                for each in self._channels:
                    n = each.split('.')[0]
                    if not n in self._nodes:
                        self._nodes.append(n)
                        
        return self._nodes
    
    @property
    def args(self):
        '''
        This will return channels, curves or nodes in instances where we don't care which.
        It wont waste time converting from one to the other.
        '''
        if self._channels:
            return self._channels
        if self._curves:
            return self._curves
        if self._nodes:
            return self._nodes
        return None
    
    @property
    def time(self):
        '''
        The keySelection's time, formatted for maya's various keyframe command arguments.
        '''
        if self._time:
            if isinstance(self._time, list):
                return tuple(self._time)
            elif isinstance(self._time, float) or isinstance(self._time, int):
                return (self._time,)
            return self._time
        elif self._timeRangeStart and self._timeRangeEnd:
            return (self._timeRangeStart,self._timeRangeEnd)
        elif self._timeRangeStart:
            return (str(self._timeRangeStart)+':',)
        elif self._timeRangeEnd:
            return (':'+str(self._timeRangeEnd),)
        elif self.selected:
            #if keys are selected, get their times
            timeList = self.keyframe(query=True, timeChange=True)
            return tuple(set(timeList))
        return (':',)
    
    
    @property
    def times(self):
        '''
        This returns an expanded list of times, which is synced with the curve list.
        '''
        timeList = list()
        theTime = self.time
        for c in self.curves:
            curveTime = tuple(mc.keyframe(c, time=(theTime,), query=True, timeChange=True))
            if len(curveTime) == 1:
                curveTime = (curveTime[0],)
            timeList.append(curveTime)
        return timeList
        
    
    @property
    def initialized(self):
        '''
        Basically just tells if the object has been sucessfully initialized.
        '''
        return bool(self.args)
    
    
    def selectedObjects(self):
        '''
        Initializes the keySelection object with selected objects.
        Returns True if successful.
        '''
        
        if not self.nodeSelection:
            return False
        
        self._nodes = self.nodeSelection
        return True


    def selectedChannels(self):
        '''
        Initializes the keySelection object with selected channels.
        Returns True if successful.
        '''
        
        chanBoxChan = getSelectedChannels()
        
        if not chanBoxChan:
            return False
        
        #channels may be on shapes, include shapes in the list
        nodes = self.nodeSelection
        shapes = mc.listRelatives(self.nodeSelection, shapes=True, path=True)
        if shapes:
            nodes.extend(shapes)
            nodes = list(set(nodes))
        
        for obj in nodes:
            for attr in chanBoxChan:
                if mc.attributeQuery(attr, node=obj, exists=True):
                    self._channels.append('.'.join((obj,attr)))
        
        if not self._channels:
            return False
        
        return True
    
    
    def selectedLayers(self, includeLayerWeight=True):
        '''
        This affects keys on all layers that the node belongs to.
        If includeLayerWeight, the keys on the layer's weight attribute will be affected also.
        '''
        layers = getSelectedAnimLayers()
        curves = list()
        for layer in layers:
            layerCurves = mc.animLayer(layer, query=True, animCurves=True)
            if layerCurves:
                curves.extend(layerCurves)
            if includeLayerWeight:
                weightCurve = mc.keyframe(layer+'.weight', query=True, name=True)
                if weightCurve:
                    curves.append(weightCurve[0])
        self._curves = curves
        #we only want to use curves, since nodes or channels wont accurately represent all layers
        self._nodes = None
        self._channels = None
    
    
    def visibleInGraphEditor(self):
        '''
        Initializes the keySelection object with curves visibile in graph editor.
        Returns True if successful.
        '''
        
        
        if not 'graphEditor1' in mc.getPanel(visiblePanels=True):
            return False

        graphVis = mc.selectionConnection('graphEditor1FromOutliner', query=True, obj=True)
        
        if not graphVis:
            return False
        
        for each in graphVis:
            try:
                self._curves.extend(mc.keyframe(each, query=True, name=True))
            except Exception:
                pass
                
        
        if not self._curves:
            return False
            
        return True
        
        
    def selectedKeys(self):
        '''
        Initializes the keySelection object with selected keyframes.
        Returns True if successful.
        '''
        
        selectedCurves = mc.keyframe(query=True, name=True, selected=True)
        
        if not selectedCurves:
            return False
        self._curves = selectedCurves
        self.selected = True
        return True
        

    def keyedChannels(self, includeShapes=False):
        '''
        Initializes the keySelection object with keyed channels.
        Returns True if successful.
        '''
        
        
        if not self.nodeSelection:
            return False
        
        self._nodes = self.nodeSelection
        if includeShapes:
            shapes = mc.listRelatives(self.nodeSelection, shapes=True)
            if shapes:
                self._nodes.extend(shapes)
        
        #since self.curves is a property, it is actually finding curves from self._nodes
        if not self.curves:
            #if we don't find curves, reset nodes and fail
            self._nodes = None
            return False
            
        return True

    
    def keyedInHierarchy(self, includeRoot=True):
        '''
        Initializes the keySelection object with all the animation curves in the hierarchy.
        Returns True if successful.
        '''
        
        if not self.nodeSelection:
            return False
        
        objs = mc.ls(self.nodeSelection, long=True)
        tops = list()
        namespaces = list()
        for obj in objs:
            namespace = getNamespace(obj)
            if namespace in namespaces:
                #we've already done this one
                continue
            
            hier = obj.split('|')
            if not namespace:
                #if there's no namespace, just grab the top of the hierarchy
                if len(hier) > 1:
                    tops.append(hier[1])
                else:
                    tops.append(obj)
            
            else:
                #otherwise look through the hierarchy until you find the first node with the same namespace
                namespaces.append(namespace)
                for each in hier:
                    if namespace in each:
                        tops.append(each)
                        break
        
        if not tops:
            #if we haven't been sucessful, we're done
            return False
        
        nodes = mc.listRelatives(tops, pa=True, type='transform', ad=True)
        if not nodes:
            nodes = list()
            
        if includeRoot:
            nodes.extend(tops)
        
        if not nodes:
            return False
        
        #now that we've determined the hierarchy, lets find keyed nodes
        #for node in nodes:
        # this will only return time based keyframes, not driven keys
        self._curves = mc.keyframe(nodes, time=(':',), query=True, name=True)
        
        #nodes or channels can be acessed by the node or channel property
        if not self._curves:
            return False
        
        return True
    
    
    def scene(self):
        '''
        Initializes the keySelection object with all animation curves in the scene.
        Returns True if successful.
        '''
        
        tl = mc.ls(type='animCurveTL')
        ta = mc.ls(type='animCurveTA')
        tu = mc.ls(type='animCurveTU')
        
        if tl:
            self._curves.extend(tl)
        if ta:
            self._curves.extend(ta)
        if tu:
            self._curves.extend(tu)
            
        if not self._curves:
            return False
        
        return True

    
    def selectedFrameRange(self):
        '''
        Sets the keySelection time to the selected frame range, returns false if frame range not selected.
        '''
        
        gPlayBackSlider = mm.eval('$temp=$gPlayBackSlider')
        if mc.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
            self._timeRangeStart, self._timeRangeEnd = mc.timeControl(gPlayBackSlider, query=True, rangeArray=True)
            return True
        return False
        
        
    def frameRange(self):
        '''
        Sets the keySelection time to the selected frame range, or the current frame range.
        '''
        #this is selected range in the time slider
        self._timeRangeStart, self._timeRangeEnd = frameRange()
        

    def toEnd(self, includeCurrent=False):
        '''
        Sets the keySelection time to the range from the current frame to the last frame.
        Option to include the current frame.
        '''
        
        t = self.currentTime
        if not includeCurrent:
            t+=self.shortestTime
        self._timeRangeStart = t
        

    def fromBeginning(self, includeCurrent=False):
        '''
        Sets the keySelection time to the range from the first frame to the current frame.
        Option to include the current frame.
        '''
        
        t = self.currentTime        
        if not includeCurrent:
            t-=self.shortestTime
        self._timeRangeEnd = t
        

    def keyRange(self):
        '''
        Sets the keySelection time range to the range of keys in the keySelection.
        '''
        
        keyTimes = self.getSortedKeyTimes()
        
        if not keyTimes or keyTimes[0] == keyTimes[-1]:
            return
        
        self._timeRangeStart = keyTimes[0]
        self._timeRangeEnd = keyTimes[-1]


    def currentFrame(self):
        '''
        Sets the keySelection time to the current frame.
        '''
        self._time = self.currentTime
        
        
    def previousKey(self):
        '''
        Sets the keySelection time to the previous key from the current frame.
        '''
        self._time = self.findKeyframe(which='previous')
    
    
    def nextKey(self):
        '''
        Sets the keySelection time to the next key from the current frame.
        '''
        self._time = self.findKeyframe(which='next')
    
    
    def setKeyframe(self, deleteSubFrames=False, **kwargs):
        '''
        Wrapper for the setKeyframe command. Curve and time arguments will be provided based on 
        how this object was intitialized, otherwise usage is the same as maya's setKeyframe command.
        Option to delete sub-frames after keying.
        '''
        
        if not 'time' in kwargs:
            #still not sure about how I want to do this, but we need a discrete time.
            #if time is a string set to current time
            if isinstance(self.time, tuple) and (isinstance(self.time[0], str) or len(self.time)>1):
                kwargs['time'] = mc.currentTime(query=True)
            else:
                kwargs['time'] = self.time
        
        if 'insert' in kwargs and kwargs['insert'] == True:
            #setKeyframe fails if insert option is used but there's no keyframes on the channels.
            #key any curves with insert, then key everything again without it
            
            if self.curves:
                mc.setKeyframe(self.curves, **kwargs)
            kwargs['insert'] = False
        
        #want to try setting keys on nodes first, since certain setKeyframe arguments wont work
        #as expected with channels
        if self._nodes:
            mc.setKeyframe(self.nodes, **kwargs)
            self._curves = mc.keyframe(self.nodes, query=True, name=True)
        else:
            mc.setKeyframe(self.channels, **kwargs)
            self._curves = mc.keyframe(self.channels, query=True, name=True)
        
        #there's a new selection of curves, so reset the member variables
        self._channels = list()
        self._nodes = list()
        self._time = kwargs['time']
        
        if deleteSubFrames:
            #remove nearby sub-frames
            #this breaks at higher frame ranges because maya doesn't keep enough digits
            #this value is also different for different frame rates
            if self.currentTime % 1 == 0 and -9999 < self.currentTime < 9999:
                #the distance that keys can be is independent of frame rate, so we have to convert based on the frame rate.
                tol = self.shortestTime
                self.cutKey(time=(self.currentTime+tol, self.currentTime+0.5))
                self.cutKey(time=(self.currentTime-0.5, self.currentTime-tol))        
        
    
    def keyframe(self,**kwargs):
        '''
        Wrapper for the keyframe command. Curve and time arguments will be provided based on 
        how this object was intitialized, otherwise usage is the same as maya's keyframe command.
        '''
        if self.selected:
            #it's important that selection test first, becuase it's called by the time property
            kwargs['sl'] = True
        elif not 'time' in kwargs:
            kwargs['time'] = self.time
        
        return mc.keyframe(self.curves, **kwargs)
        
        
    def cutKey(self, includeSubFrames=False, **kwargs):
        '''
        Wrapper for the cutKey command. Curve and time arguments will be provided based on 
        how this object was intitialized, otherwise usage is the same as maya's cutKey command.
        Option to delete sub-frames.
        '''
        
        if not 'includeUpperBound' in kwargs:
            kwargs['includeUpperBound'] = False
            
        if self.selected:
            mc.cutKey(sl=True, **kwargs)
            return
        
        if not 'time' in kwargs:
            if includeSubFrames:
                kwargs['time'] = (round(self.time[0])-0.5, round(self.time[-1])+0.5)
            else:
                kwargs['time'] = self.time
        mc.cutKey(self.curves, **kwargs)
        
        
        
    def copyKey(self, **kwargs):
        '''
        
        '''
        
        if not 'includeUpperBound' in kwargs:
            kwargs['includeUpperBound'] = False
            
        if self.selected:
            mc.copyKey(sl=True, **kwargs)
            return
        
        if not 'time' in kwargs:
            kwargs['time'] = self.time
            
        mc.copyKey(self.args, **kwargs)
        
        
    def pasteKey(self, option='replaceCompletely', **kwargs):
        '''
        
        '''
        mc.pasteKey(self.args, option=option, **kwargs)
        
        
    def selectKey(self,**kwargs):
        '''
        Wrapper for maya's selectKey command.
        '''
        
        if not 'time' in kwargs:
            kwargs['time'] = self.time
        mc.selectKey(self.curves, **kwargs)
    
    
    def moveKey(self, frames):
        '''
        A wrapper for keyframe -edit -timeChange
        '''
        
        if not frames:
            return
        
        self.keyframe(edit=True, relative=True, timeChange=frames)
#         self.copyKey()
#         self.pasteKey(timeOffset=frames)
        
        
    def scaleKey(self, timePivot=0, **kwargs):
        '''
        Wrapper for maya's scaleKey command.
        '''
        
        if not 'time' in kwargs:
            kwargs['time'] = self.time
        
        if timePivot == 'current':
            timePivot = self.currentTime
            
        mc.scaleKey(self.curves, timePivot=timePivot, **kwargs)
    
    
    def tangentType(self, **kwargs):
        '''
        Wrapper for maya's tangentType command.
        '''
        if not 'time' in kwargs:
            kwargs['time'] = self.time
        mc.tangentType(self.curves, **kwargs)
    
    def keyTangent(self, **kwargs):
        '''
        Wrapper for maya's keyTangent command.
        '''
        if not 'time' in kwargs:
            kwargs['time'] = self.time
        mc.keyTangent(self.curves, **kwargs)
    
    
    def findKeyframe(self, which='next', loop=False, roundFrame=False, **kwargs):
        '''
        This is similar to maya's findKeyframe, but operates on the keySelection and has options
        for rounding and looping.
        '''
        
        if which != 'next' and which != 'previous' and which != 'first' and which != 'last':
            return
        
        if not roundFrame:
            if not loop or which == 'first' or which == 'last':
                #if there's not special options, just use default maya command for speed
                return mc.findKeyframe(self.args, which=which, **kwargs)
        
        keyTimes = self.getSortedKeyTimes()
        
        #if we don't find any, we're done
        if not keyTimes:
            return
                
        tolerence = 0.0
        if roundFrame:
            tolerence = 0.5
        
        if which == 'previous':
            findTime = keyTimes[-1]
            for x in reversed(keyTimes):
                if self.currentTime - x > tolerence:
                    findTime=x
                    break
        elif which == 'next':
            findTime = keyTimes[0]
            for x in keyTimes:
                if x - self.currentTime > tolerence:
                    findTime=x
                    break        
        elif which == 'first':
            findTime = keyTimes[0]
        elif which == 'last':
            findTime = keyTimes[-1]
            
        if roundFrame:
            #round to nearest frame, if that option is selected
            findTime = round(findTime)
        
        return findTime
        
        
    def getSortedKeyTimes(self):
        '''
        Returns a list of the key times in order without duplicates.
        '''
        
        keyTimes = self.keyframe(query=True, timeChange=True)
        if not keyTimes:
            return
        return sorted(list(set(keyTimes)))
        


class MlUi():
    '''
    Window template for consistency
    '''

    def __init__(self, name, title, width=400, height=200, info='', menu=True, module=None):
    
        self.name = name
        self.title = title
        self.width = width
        self.height = height
        self.info = info
        self.menu = menu
        
        self.module = module
        if not module or module == '__main__':
            self.module = self.name

        #look for icon
        self.icon = getIcon(name)
        

    def __enter__(self):
        '''
        Initialize the UI
        '''
        if mc.window(self.name, exists=True):
            mc.deleteUI(self.name)

        mc.window(self.name, title='ml :: '+self.title, iconName=self.title, width=self.width, height=self.height, menuBar=self.menu)
        
        
        if self.menu:
            self.createMenu()
        
        self.form = mc.formLayout()
        self.column = mc.columnLayout(adj=True)

        
        mc.rowLayout( numberOfColumns=2, columnWidth2=(34, self.width-34), adjustableColumn=2, 
                    columnAlign2=('right','left'),
                    columnAttach=[(1, 'both', 0), (2, 'both', 8)] )

        #if we can find an icon, use that, otherwise do the text version
        if self.icon:
            mc.iconTextStaticLabel(style='iconOnly', image1=self.icon)
        else:
            mc.text(label=' _ _ |\n| | | |')
            
        if not self.menu:
            mc.popupMenu(button=1)
            mc.menuItem(label='Help', command=(_showHelpCommand(wikiURL+'#'+self.name)))
        
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

        
    def createMenu(self, *args):
        '''
        Create the main menu for the UI
        '''
        
        #generate shelf label by removing ml_
        shelfLabel = self.name.replace('ml_','')
        module = self.module
        if not module:
            module = self.name
            
        #if icon exists, use that
        argString = ''
        if not self.icon:
            argString = ', label="'+shelfLabel+'"'
        
        mc.menu(label='Tools')
        mc.menuItem(label='Add to shelf', 
            command='import ml_utilities;ml_utilities.createShelfButton("import '+module+';'+module+'.ui()", name="'+self.name+'", description="Open the UI for '+self.name+'."'+argString+')')
        if not self.icon:
            mc.menuItem(label='Get Icon',
                command=(_showHelpCommand(websiteURL+'/wp-content/files/'+self.name+'.png')))
        mc.menuItem(label='Get More Tools!', 
            command=(_showHelpCommand(websiteURL+'/downloads')))
        mc.setParent( '..', menu=True )

        mc.menu(label='Help')
        mc.menuItem(label='About', command=self.about)
        mc.menuItem(label='Documentation', command=(_showHelpCommand(wikiURL+'#'+self.name)))
        mc.menuItem(label='Python Command Documentation', command=(_showHelpCommand(wikiURL+'#\%5B\%5B'+self.name+'\%20Python\%20Documentation\%5D\%5D')))
        mc.menuItem(label='Submit a Bug or Request', command=(_showHelpCommand(websiteURL+'/downloads/feedback-and-bug-reports/?1ex_field1='+self.name)))
        
        mc.setParent( '..', menu=True )
       
       
    def about(self, *args):
        '''
        This pops up a window which shows the revision number of the current script.
        '''
        
        text='by Morgan Loomis\n\n'
        try:
            __import__(self.module)
            module = sys.modules[self.module]
            text = text+'Revision: '+str(module.__revision__)+'\n'
        except Exception:
            pass
        try:
            text = text+'ml_utilities Rev: '+str(__revision__)+'\n'
        except Exception:
            pass
        
        mc.confirmDialog(title=self.name, message=text, button='Close')
    
    
    def buttonWithPopup(self, label=None, command=None, annotation='', shelfLabel='', shelfIcon='render_useBackground', readUI_toArgs=dict()):
        '''
        Create a button and attach a popup menu to a control with options to create a shelf button or a hotkey.
        The argCommand should return a kwargs dictionary that can be used as args for the main command.
        '''
        
        if self.icon:
            shelfIcon = self.icon
        
        if annotation and not annotation.endswith('.'):
            annotation+='.'
        
        button = mc.button(label=label, command=command, annotation=annotation+' Or right click for more options.')
        
        mc.popupMenu()
        self.shelfMenuItem(command=command, annotation=annotation, shelfLabel=shelfLabel, shelfIcon=shelfIcon)
        self.hotkeyMenuItem(command=command, annotation=annotation)
        return button
        

    def shelfMenuItem(self, command=None, annotation='', shelfLabel='', shelfIcon='menuIconConstraints', menuLabel='Create Shelf Button'):
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
    
    
    class ButtonWithPopup():
        
        def __init__(self, label=None, name=None, command=None, annotation='', shelfLabel='', shelfIcon='render_useBackground', readUI_toArgs=dict(), **kwargs):
            '''
            The fancy part of this object is the readUI_toArgs argument.
            '''
            
            self.uiArgDict = readUI_toArgs
            self.name = name
            self.command = command
            self.kwargs = kwargs
            
            self.annotation = annotation
            self.shelfLabel = shelfLabel
            self.shelfIcon = shelfIcon

            if annotation and not annotation.endswith('.'):
                annotation+='.'

            button = mc.button(label=label, command=self.runCommand, annotation=annotation+' Or right click for more options.')

            mc.popupMenu()
            mc.menuItem(label='Create Shelf Button', command=self.createShelfButton, image=shelfIcon)

            mc.menuItem(label='Create Hotkey',
                        command=self.createHotkey, image='commandButton') 

        
        def readUI(self):
            '''
            This reads the UI elements and turns them into arguments saved in a kwargs style member variable
            '''
            
            if self.uiArgDict:
                #this is some fanciness to read the values of UI elements and generate or run the resulting command
                #keys represent the argument names, the values are UI elements
                
                for k in list(self.uiArgDict.keys()):
                    
                    uiType = mc.objectTypeUI(self.uiArgDict[k])
                    value = None
                    if uiType == 'rowGroupLayout':
                        controls = mc.layout(self.uiArgDict[k], query=True, childArray=True)
                        if 'check1' in controls:
                            value = mc.checkBoxGrp(self.uiArgDict[k], query=True, value1=True)
                        elif 'radio1' in controls:
                            #this will be a 1 based index, we want to return formatted button name?
                            value = mc.radioButtonGrp(self.uiArgDict[k], query=True, select=True)-1
                        elif 'slider' in controls:
                            try:
                                value = mc.floatSliderGrp(self.uiArgDict[k], query=True, value=True)
                                continue
                            except Exception:
                                pass
                            try:
                                value = mc.intSliderGrp(self.uiArgDict[k], query=True, value=True)
                                continue
                            except Exception:
                                pass
                        elif 'field1' in controls:
                            value = mc.floatFieldGrp(self.uiArgDict[k], query=True, value1=True)
                    else:
                        OpenMaya.MGlobal.displayWarning('Cannot read '+uiType+' UI element: '+self.uiArgDict[k])
                        continue
                    
                    self.kwargs[k] = value
        
        
        def runCommand(self, *args):
            '''
            This compiles the kwargs and runs the command directly
            '''
            self.readUI()
            self.command(**self.kwargs)
            

        def stringCommand(self):
            '''
            This takes the command
            '''
            
            cmd = 'import '+self.name+';'+self.name+'.'+self.command.__name__+'('
            
            comma = False
            for k,v in list(self.kwargs.items()):
                
                value = v
                if isinstance(v, str):
                    value = "'"+value+"'"
                elif v is True:
                    value = 'True'
                elif v is False:
                    value = 'False'
                elif not v:
                    value = 'None'
                
                if comma:
                    cmd+=', '
                cmd = cmd+k+'='+value
                
                comma = True
                
            cmd+=')'
            
            return cmd


        def createShelfButton(self,*args):
            '''
            Builds the command and creates a shelf button out of it
            '''
            self.readUI()
            pythonCommand = self.stringCommand()
            createShelfButton(pythonCommand, self.shelfLabel, self.name, description=self.annotation, image=self.shelfIcon)


        def createHotkey(self, annotation='', menuLabel='Create Hotkey'):
            '''
            Builds the command and prompts to create a hotkey.
            '''
            
            self.readUI()
            pythonCommand = self.stringCommand()
            melCommand = 'python("'+pythonCommand+'");'
            createHotkey(melCommand, self.name, description=self.annotation)

    
class SkipUndo():
    '''
    Skips adding the encapsulated commands to the undo queue, so that you 
    cannot undo them.
    '''
    
    def __enter__(self):
        '''
        Turn off undo
        '''
        mc.undoInfo(stateWithoutFlush=False)
        
    def __exit__(self,*args):
        '''
        Turn on undo
        '''
        mc.undoInfo(stateWithoutFlush=True)
        
        
class UndoChunk():
    '''
    In versions of maya before 2011, python doesn't always undo properly, so in 
    some cases we have to manage the undo queue ourselves.
    '''
    
    def __init__(self, force=False):
        self.force = force
        
    def __enter__(self):
        '''open the undo chunk'''
        if self.force or mm.eval('getApplicationVersionAsFloat') < 2011:
            self.force = True
            mc.undoInfo(openChunk=True)
            
    def __exit__(self, *args):
        '''close the undo chunk'''
        if self.force:
            mc.undoInfo(closeChunk=True)
    

if __name__ == '__main__':
    
    option='next'
    roundFrame=False
    selected=False
    searchHierarchy=False
    
    sel = mc.ls(sl=True)
    currentTime = mc.currentTime(query=True)
    time = currentTime
    
    keySel = KeySelection()
    
    if searchHierarchy:
        #if we're looking through the hierarchy, 
        keySel.getKeyedFromHierarchy()
        
    else:
        #create the keySelection object.
        #all the heavy lifting is done in ml_utilities.
        if selected and keySel.selectedKeys():
            pass
        if keySel.visibleInGraphEditor():
            pass
        if keySel.selectedObjects():
            pass
    
    time = keySel.findKeyframe(which=option, roundFrame=roundFrame, loop=True)    
        
    #finally, set the time without adding to the undo queue
    with SkipUndo():
        mc.currentTime(time, edit=True)
    


#      ______________________
# - -/__ Revision History __/- - - - - - - - - - - - - - - - - - - - - - - - 
#
# Revision 1: : First publish
#
# Revision 2: 2011-05-04 : Fixed error in frameRange.
#
# Revision 3: 2012-05-31 : Adding Menu and Icon update to UI, adding KeyframeSelection object, and a few random utility functions.
#
# Revision 4: 2012-06-01 : Fixing bug with UI icons
#
# Revision 5: 2012-07-23 : Expanding and bug fixing Keyselection, added SkipUndo, minor bug fixes.
#
# Revision 6: 2012-07-23 : KeySelection bug fix
#
# Revision 7: 2012-08-07 : Minor bug with Keyselection, adding functions.
#
# Revision 8: 2012-11-06 : Backwards incompatable update to KeySelection, and several new functions.