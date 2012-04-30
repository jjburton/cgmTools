# 
#   -= ml_deleteKey.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 3, 2012-04-14
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_deleteKey.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_deleteKey
#     ml_deleteKey.ui()
# From MEL, this looks like:
#     python("import ml_deleteKey;ml_deleteKey.ui()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# This is a more robust tool for deleting keyframes in Maya, including
# deleting keys on selected channels, current frame, or visible in graph editor.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Run the tool, select the options, and press the Delete Key button.
# Alternately, set the options and right click the button to create
# a hotkey or shelf button. The options all work together, they are evaluated
# in the order listed in the UI. For example, if all options are checked, it 
# will first look for selected keys to delete. If no keys are selected, it 
# will check if the channel box is highlighted. And so on.
#      ________________
# - -/__ UI Options __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# [] Selected Keys : Delete the keys selected in the graph editor.
# [] Selected Channels : Delete all the keys on selected channels. (Unless overridden above)
# [] Visible in Graph Editor : Only delete keys that are visible in the graph editor. (Unless overridden above)
# [] Current Frame : Delete the keys on the current frame. (Unless overridden above)
# [] Delete Sub-Frames : Delete sub-frame keys surrounding the current frame.
# [Delete Key] : Run the command.
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
__revision__ = 3


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
    
hotkey = {'d':'deleteKey(deleteSubFrames=True, selectedChannels=True, visibleInGraphEditor=True)'}


def ui():
    '''
    User interface for ml_deleteKey
    '''

    with utl.MlUi('ml_deleteKey', 'deleteKey', width=400, height=220, info='''Press Delete Key to delete keyframes using the selected settings.
Right click the button to create a hotkey or shelf button with the current settings.
Options are evaluated in top to bottom order.''') as win:
    
        mc.checkBoxGrp('ml_deleteKey_selectedKey_checkBox', label='Selected Keys', annotation='Delete the keys selected in the graph editor.')
        mc.checkBoxGrp('ml_deleteKey_chanBox_checkBox', label='Selected Channels', annotation='Delete all the keys on selected channels. (Unless overridden above)')
        mc.checkBoxGrp('ml_deleteKey_graphVis_checkBox', label='Visible in Graph Editor', annotation='Only delete keys that are visible in the graph editor. (Unless overridden above)')
        mc.checkBoxGrp('ml_deleteKey_currentFrame_checkBox', label='Current Frame', annotation='Delete the keys on the current frame. (Unless overridden above)')
        mc.checkBoxGrp('ml_deleteKey_subFrames_checkBox', label='Delete Sub-Frames', annotation='Delete sub-frame keys surrounding the current frame.')

        mc.button(label='Delete Key', command=_deleteKeyButton, annotation='Run the command.')
        
        mc.popupMenu()
        mc.menuItem(label='Create Shelf Button', command=_shelfButtonCallback)
        mc.menuItem(label='Create Hotkey', command=_hotkeyCallback)
        

def _uiArgs():

    selected = mc.checkBoxGrp('ml_deleteKey_selectedKey_checkBox', query=True, value1=True)
    chanBox = mc.checkBoxGrp('ml_deleteKey_chanBox_checkBox', query=True, value1=True)
    graphVis = mc.checkBoxGrp('ml_deleteKey_graphVis_checkBox', query=True, value1=True)
    current = mc.checkBoxGrp('ml_deleteKey_currentFrame_checkBox', query=True, value1=True)
    subFrames = mc.checkBoxGrp('ml_deleteKey_subFrames_checkBox', query=True, value1=True)

    kwargs = dict()
    if selected:
        kwargs['selectedKeys'] = True
    if chanBox:
        kwargs['selectedChannels'] = True
    if graphVis:
        kwargs['visibleInGraphEditor'] = True
    if current:
        kwargs['currentFrame'] = True
    if subFrames:
        kwargs['deleteSubFrames'] = True
    
    return kwargs


def _deleteKeyButton(*args):
    '''called from the UI button, simply runs the command with the current settings.'''
    deleteKey(**_uiArgs())
    
    
def _buildCommand(*args):
    '''Constructs a command from the current settings that can be passed to hotkey or shelf button.'''
    
    args = str()
    kwargs = _uiArgs()
    if kwargs:
        for k in kwargs.keys():
            args = args+k+'='+str(kwargs[k])+', '
        args = args[:-2]

    return 'import ml_deleteKey;ml_deleteKey.deleteKey('+args+')'


def _shelfButtonCallback(*args):

    description = 'Sets keys with the following options:'
    for k in _uiArgs().keys():
        description=description+' '+k
        
    utl.createShelfButton( _buildCommand(), "del", 'ml_deleteKey', description=description)


def _hotkeyCallback(*args):

    name = 'ml_deleteKey'
    description = 'Sets keys with the following options:'
    for k in _uiArgs().keys():
        name=name+'_'+k
        description=description+' '+k
        
    utl.createHotkey('python("'+_buildCommand()+'");', name, description=description)


def deleteKey(deleteSubFrames=False, selectedKeys=False, selectedChannels=False, visibleInGraphEditor=False, currentFrame=False):
    '''
    The main function arguments:
    
        selectedKeys:           Delete the keys selected in the graph editor
        selectedChannels:       Delete all the keys on selected channels
        visibleInGraphEditor:   Only delete keys that are visible in the graph editor
        currentFrame:           Delete the keys on the current frame
        deleteSubFrames:        Delete sub-frame keys surrounding the current frame
    '''
    
    sel = mc.ls(sl=True)
    if not sel:
        return

    channels = list()
    
    if selectedKeys and mc.keyframe(query=True, selected=True):
        #if selected keys (and keys are selected) just cut them
        mc.cutKey(includeUpperBound=False, sl=True, clear=True)
        return
    
    chanBoxChan = utl.getSelectedChannels()
    if selectedChannels and chanBoxChan:
        #if channel box (and channels are selected)
        curves = list()
        for obj in sel:
            for chan in chanBoxChan:
                temp = mc.listConnections('.'.join((obj,chan)), source=True, destination=False, type='animCurve')
                if temp:
                    curves.append(temp[0])
        if curves:
            mc.cutKey(curves, includeUpperBound=False, clear=True)
            utl.deselectChannels()
            return
    
    #past this point the options accumulate
    
    args = list()
    #animCurves = list()
    if visibleInGraphEditor and 'graphEditor1' in mc.getPanel(visiblePanels=True):
        #if visible in graph editor and graph editor is open
        graphVis = mc.selectionConnection('graphEditor1FromOutliner', query=True, obj=True)
        if graphVis:
            #animCurves = mc.keyframe(graphVis, query=True, name=True)
            args.append(mc.keyframe(graphVis, query=True, name=True))
    
    kwargs = {'includeUpperBound':False, 'clear':True}
    if currentFrame:
        if not args:
            args = sel
        time = (mc.currentTime(query=True))
        #include sub-frames in the time
        if deleteSubFrames and time % 1 == 0 and -9999 < time < 9999:
            kwargs['time'] = (time-0.5,time+0.5)
        else:
            kwargs['time'] = (time,)
    
    if not args and (selectedKeys or selectedChannels or visibleInGraphEditor or currentFrame):
        #if there were any arguments, but tool hasn't found any curves, don't do anything
        return
    
    mc.cutKey(*args, **kwargs)


if __name__ == '__main__': ui()


#      ______________________
# - -/__ Revision History __/- - - - - - - - - - - - - - - - - - - - - - - -
#
# Revision 1: 2012-03-29 : First publish.
#
# Revision 2: 2012-03-29 : Fixing bugs, published first version too quickly!

#
# Revision 3: 2012-04-14 : minor bug fix
