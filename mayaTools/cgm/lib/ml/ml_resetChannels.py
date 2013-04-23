# 
#   -= ml_resetChannels.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 6, 2013-04-23
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_resetChannels.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_resetChannels
#     ml_resetChannels.main()
# From MEL, this looks like:
#     python("import ml_resetChannels;ml_resetChannels.main()");
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
# Run command line to use the transformsOnly flag, in order to only
# reset transform attributes.
#      __________________
# - -/__ Requirements __/- - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# This script requires the ml_utilities module, which can be downloaded here:
# 	http://morganloomis.com/wiki/tools.html#ml_utilities
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 6

import maya.cmds as mc
import maya.mel as mm

try:
    import ml_utilities as utl
    utl.upToDateCheck(8)
except ImportError:
    result = mc.confirmDialog( title='Module Not Found', 
                message='This tool requires the ml_utilities module. Once downloaded you will need to restart Maya.', 
                button=['Download Module','Cancel'], 
                defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel' )
    
    if result == 'Download Module':
        mc.showHelp('http://morganloomis.com/download/ml_utilities.py',absolute=True)
    
def main(selectedChannels=True, transformsOnly=False):
    '''
    Resets selected channels in the channel box to default, or if nothing's
    selected, resets all keyable channels to default.
    '''
    gChannelBoxName = mm.eval('$temp=$gChannelBoxName')
    
    sel = mc.ls(sl=True)
    if not sel:
        return
    
    chans = None
    if selectedChannels:
        chans = mc.channelBox(gChannelBoxName, query=True, sma=True)
    
    testList = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ',
                'tx','ty','yz','rx','ry','rz','sx','sy','sz']
    for obj in sel:
        attrs = chans
        if not chans:
            attrs = mc.listAttr(obj, keyable=True, unlocked=True)
        if transformsOnly:
            attrs = [x for x in attrs if x in testList]
        if attrs:
            for attr in attrs:
                try:
                    default = mc.attributeQuery(attr, listDefault=True, node=obj)[0]
                    mc.setAttr(obj+'.'+attr, default)
                except StandardError:
                    pass
                
    utl.deselectChannels()

if __name__ == '__main__':
    main(transformsOnly=True)
    
#      ______________________
# - -/__ Revision History __/- - - - - - - - - - - - - - - - - - - - - - - -
#
# Revision 5: 2012-05-27 : Added revision notes, updated to use ml_utilities, changed primary function to main() for consistency
#
# Revision 6: 2013-04-23 : added transformsOnly and selected flags to support cgMonks
