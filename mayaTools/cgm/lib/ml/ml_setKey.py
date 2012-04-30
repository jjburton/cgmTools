# 
#   -= ml_setKey.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 5, 2012-03-26
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_setKey.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_setKey
#     ml_setKey.ui()
# From MEL, this looks like:
#     python("import ml_setKey;ml_setKey.ui()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# This is a more robust tool for setting keyframes in Maya, including
# setting keys on selected channels, keyed channels, and several other options.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Run the tool, select the options, and press the Set Key button.
# Alternately, set the options and press the "Create Hotkey" button to
# turn the current functionality into a hotkey.
#      ________________
# - -/__ UI Options __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# [] Selected Channels : Only key channels that are selected in the Channel Box
# [] Visible in Graph Editor : Only key curves visible in Graph Editor
# [] Key Only Keyed Channels : Only set keys on channels that are already keyed
# [] Delete Sub-Frames : Delete sub-frame keys surrounding the current frame
# [] Insert Key : Insert key (preserve tangents)
# [] Key Shapes : Set keyframes on shapes
# [] Key Shapes : Set keyframes on shapes
# [Set Key] : Run the command.
#  : Right-click for more options
#      __________________
# - -/__ Requirements __/- - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# This script requires the ml_utilities module, which can be downloaded here:
# 	http://morganloomis.com/wiki/tools.html#ml_utilities
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 5

import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya

try:
    import ml_utilities as utl
    utl.upToDateCheck(2)
except ImportError:
    result = mc.confirmDialog( title='Module Not Found', 
                message='This tool requires the ml_utilities module. Once downloaded you will need to restart Maya.', 
                button=['Download Module','Cancel'], 
                defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel' )
    
    if result == 'Download Module':
        mc.showHelp('http://morganloomis.com/download/ml_utilities.py',absolute=True)
    
hotkey = {'S':'setKey(deleteSubFrames=True, insert=True, selectedChannels=True, visibleInGraphEditor=True, keyKeyed=True, keyShapes=True)'}


def ui():
    '''
    User interface for ml_setKey
    '''

    with utl.MlUi('ml_setKey', 'SetKey', width=400, height=220, info='''Press Set Key to set a keyframe with the current checkbox settings.
Right click the button to create a hotkey or shelf button 
with the currently selected settings.''') as win:
    
        mc.checkBoxGrp('ml_setKey_chanBox_checkBox', label='Selected Channels', annotation='Only key channels that are selected in the Channel Box')
        mc.checkBoxGrp('ml_setKey_graphVis_checkBox', label='Visible in Graph Editor', annotation='Only key curves visible in Graph Editor')
        mc.checkBoxGrp('ml_setKey_keyKeyed_checkBox', label='Key Only Keyed Channels', annotation='Only set keys on channels that are already keyed')
        mc.checkBoxGrp('ml_setKey_subFrames_checkBox', label='Delete Sub-Frames', annotation='Delete sub-frame keys surrounding the current frame')
        mc.checkBoxGrp('ml_setKey_insert_checkBox', label='Insert Key', annotation='Insert key (preserve tangents)')
        mc.checkBoxGrp('ml_setKey_shapes_checkBox', label='Key Shapes', annotation='Set keyframes on shapes')
        #mc.checkBoxGrp('ml_setKey_clamp_checkBox', label='Key Shapes', annotation='Set keyframes on shapes')

        mc.button(label='Set Key', command=_setKeyButton, annotation='Run the command.')
        
        mc.popupMenu()
        mc.menuItem(label='Create Shelf Button', command=_shelfButtonCallback)
        mc.menuItem(label='Create Hotkey', command=_hotkeyCallback)
        

def _uiArgs():

    chanBox = mc.checkBoxGrp('ml_setKey_chanBox_checkBox', query=True, value1=True)
    graphVis = mc.checkBoxGrp('ml_setKey_graphVis_checkBox', query=True, value1=True)
    subFrames = mc.checkBoxGrp('ml_setKey_subFrames_checkBox', query=True, value1=True)
    insert = mc.checkBoxGrp('ml_setKey_insert_checkBox', query=True, value1=True)
    keyKeyed = mc.checkBoxGrp('ml_setKey_keyKeyed_checkBox', query=True, value1=True)
    keyShapes = mc.checkBoxGrp('ml_setKey_shapes_checkBox', query=True, value1=True)

    kwargs = dict()
    if chanBox:
        kwargs['selectedChannels'] = True
    if graphVis:
        kwargs['visibleInGraphEditor'] = True
    if subFrames:
        kwargs['deleteSubFrames'] = True
    if insert:
        kwargs['insert'] = True
    if keyKeyed:
        kwargs['keyKeyed'] = True
    if keyShapes:
        kwargs['keyShapes'] = True
    
    return kwargs


def _setKeyButton(*args):
    '''called from the UI button, simply runs the command with the current settings.'''
    kwargs = _uiArgs()
    setKey(**kwargs)
    
    
def _buildCommand(*args):

    args = str()
    kwargs = _uiArgs()
    if kwargs:
        for k in kwargs.keys():
            args = args+k+'='+str(kwargs[k])+', '
        args = args[:-2]

    return 'import ml_setKey;ml_setKey.setKey('+args+')'


def _shelfButtonCallback(*args):

    description = 'Sets keys with the following options:'
    for k in _uiArgs().keys():
        description=description+' '+k
        
    utl.createShelfButton( _buildCommand(), "key", 'ml_setKey', description=description)


def _hotkeyCallback(*args):

    name = 'ml_setKey'
    description = 'Sets keys with the following options:'
    for k in _uiArgs().keys():
        name=name+'_'+k
        description=description+' '+k
        
    utl.createHotkey('python("'+_buildCommand()+'");', name, description=description)


def setKey(deleteSubFrames=False, insert=False, selectedChannels=False, visibleInGraphEditor=False, keyKeyed=False, keyShapes=False):
    '''
    The main function arguments:
    
        deleteSubFrames:        Delete sub-frame keys surrounding the current frame
        insert:                 Insert key (preserve tangents)
        selectedChannels:       Only key channels that are selected in the Channel Box
        visibleInGraphEditor:   Only key curves visible in Graph Editor
        keyKeyed:               Only set keys on channels that are already keyed
        keyShapes:              Set keyframes on shapes as well as transforms
    '''
    
    sel = mc.ls(sl=True)
    if not sel:
        return

    channels = list()
    
    doInsert = False
    
    if selectedChannels:
        chanBoxChan = utl.getSelectedChannels()
        if chanBoxChan:
            for obj in sel:
                for attr in chanBoxChan:
                    #shapes don't work here? because the channel doesn't exist on the selected object.
                    if mc.attributeQuery(attr, node=obj, exists=True):
                        channels.append('.'.join((obj,attr)))
    
    if channels:
        #this is an interface thing, I like to deselect channels if channels were selected
        utl.deselectChannels()
        
    if visibleInGraphEditor and not channels:
        #then visible in graph editor
        
        #first check if graph editor open
        if 'graphEditor1' in mc.getPanel(visiblePanels=True):
            graphVis = mc.selectionConnection('graphEditor1FromOutliner', query=True, obj=True)
            if graphVis:
                curves = mc.keyframe(graphVis, query=True, name=True)
                if curves:
                    for c in curves:
                        chan = utl.getChannelFromAnimCurve(c)
                        if chan:
                            channels.append(chan)
                    if channels:
                        doInsert = insert
                
    if keyKeyed and not channels:
        #otherwise try keyed channels.
        curves = mc.keyframe(sel, query=True, name=True)
        if curves:
            for c in curves:
                chan = utl.getChannelFromAnimCurve(c)
                if chan:
                    channels.append(chan)
            if channels:
                doInsert = insert
    
    
    if not channels:
        #otherwise just all the selected nodes, flatten the keyable channels.
        for each in sel:
            if doInsert!=insert and mc.keyframe(each, query=True, eval=True):
                #if there's keyframe values, we can can still insert
                doInsert=insert
                
            attrs = mc.listAttr(each, keyable=True, settable=True)
            if attrs:
                channels.extend(['.'.join((each,attr)) for attr in attrs])
                
    
    if not channels:
        OpenMaya.MGlobal.displayWarning('No channels specified.')
        return
    
    #if the user has middle-mouse dragged, we don't want to insert
    #test this by comparing the current attribute value with the evaluated animation curve
    #also check if there's n
    if doInsert:
        for each in channels:
            curveValue = mc.keyframe(each, query=True, eval=True)
            if not curveValue:
                doInsert=False
                break
            if round(mc.getAttr(each),3) != round(curveValue[0],3):
                doInsert=False
                break
        
    
    #this is a special arg, which creates keys on the attributes determined so far
    mc.setKeyframe(channels, insert=doInsert, shape=keyShapes)
    
    #remove nearby sub-frames
    #this breaks at higher frame ranges because maya doesn't keep enough digits
    #this value is also different for different frame rates
    time = mc.currentTime(query=True)
    if deleteSubFrames and time % 1 == 0 and -9999 < time < 9999:
        #the distance that keys can be is independent of frame rate, so we have to convert based on the frame rate.
        tol = getFrameRate()/6000.0
        mc.cutKey(channels, time=(time+tol,time+0.5))
        mc.cutKey(channels, time=(time-0.5,time-tol))
        

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
    
    
if __name__ == '__main__': ui()

#      ______________________
# - -/__ Revision History __/- - - - - - - - - - - - - - - - - - - - - - - -
#
# Revision 4: 2012-03-11 : Added revision notes, updated to use ml_utilities, fixed a bug where tangents weren't being preserved, and fixed middle-mouse dragging.
#
# Revision 5: 2012-03-26 : Updated delete sub-frame option to work with other frame rates
