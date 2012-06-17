# 
#   -= ml_resetChannels.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 4, 2011-01-06
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_resetChannels.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_resetChannels
#     ml_resetChannels.resetChannels()
# From MEL, this looks like:
#     python("import ml_resetChannels;ml_resetChannels.resetChannels()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Sets the selected channels in the channel box to their default values,
# or if no channels are selected, resets all keyable channels.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Select channels in the channel box, and run the command directly, as
# a hotkey or shelf button.
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 4

import maya.cmds as mc
import maya.mel as mm

def resetChannels():
    '''
    Resets selected channels in the channel box to default, or if nothing's
    selected, resets all keyable channels to default.
    '''
    gChannelBoxName = mm.eval('$temp=$gChannelBoxName')
    
    sel = mc.ls(sl=True)
    if not sel:
        return
    
    chans = mc.channelBox(gChannelBoxName, query=True, sma=True)
    
    for obj in sel:
        #Check if object is an attribute, Morgan, this is the section I added
        if '.' in obj:
            splitBuffer = obj.split('.')
            if splitBuffer and mc.attributeQuery (splitBuffer[-1], node = ''.join(splitBuffer[:-1]), exists = True ):
                attrs = [splitBuffer[-1]]
                obj = ''.join(splitBuffer[:-1])
        
        else:
            attrs = chans
            if not chans:
                attrs = mc.listAttr(obj, keyable=True, unlocked=True)
        
        for attr in attrs:
            try:
                default = mc.attributeQuery(attr, listDefault=True, node=obj)[0]
                mc.setAttr(obj+'.'+attr, default)
            except StandardError:
                pass
                
    _deselectChannels()
    
def _getSelectedChannels():
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


def _deselectChannels():
    '''
    Deselect selected channels in the channelBox,
    by clearing selection and then re-selecting
    '''
    
    if not _getSelectedChannels():
        return
    from functools import partial
    sel = mc.ls(sl=True)
    mc.select(clear=True)
    mc.evalDeferred(partial(mc.select,sel))
