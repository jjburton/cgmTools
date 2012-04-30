# 
#   -= ml_copyAnim.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 1, 2012-03-14
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_copyAnim.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_copyAnim
#     ml_copyAnim.ui()
# From MEL, this looks like:
#     python("import ml_copyAnim;ml_copyAnim.ui()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Copy animation curves either completely or in part from one node or hierarchy to another.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Select the source and destination node (or top node) and press the button to either copy
# the selected node only, or the whole hierarchy underneath. Highlight the timeline if you
# want to copy just that part of the animation.
#      ________________
# - -/__ UI Options __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# [Copy Single] : Copy animation from one object to another.
# [Copy Hierarchy] : Uses name matching to copy animation across.
#      __________________
# - -/__ Requirements __/- - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# This script requires the ml_utilities module, which can be downloaded here:
# 	http://morganloomis.com/wiki/tools.html#ml_utilities
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 1

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
    
def ui():
    '''
    user interface for ml_copyAnim
    '''

    with utl.MlUi('ml_copyAnim', 'Copy Animation', width=400, height=120, info='''Copy animation across single nodes, or hierarchies based on name.
Highlight the timeline to copy just that part of the animation.''') as win:

        win.buttonWithPopup(label='Copy Single', command=copySingle, annotation='Copy animation from one object to another.', shelfLabel='cpAn', shelfIcon='defaultTwoStackedLayout')
        win.buttonWithPopup(label='Copy Hierarchy', command=copyHierarchy, annotation='Uses name matching to copy animation across.', shelfLabel='cpAn', shelfIcon='defaultTwoStackedLayout')


def _getStartAndEnd():
    
    gPlayBackSlider = mm.eval('$temp=$gPlayBackSlider')
    if mc.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
        start, end = mc.timeControl(gPlayBackSlider, query=True, rangeArray=True)
        return start, end-1
    return None, None


def copySingle(source=None, destination=None, pasteMethod='replace', offset=0):
    '''
    Copy animation from a source node and paste it to a destination node
    '''
    start, end = _getStartAndEnd()
     
    if not source and not destination:
        sel = mc.ls(sl=True)
        
        if len(sel) != 2:
            OpenMaya.MGlobal.displayWarning('Please select exactly 2 objects.')
            return
        
        source = sel[0]
        destination = sel[1]
        
    copyAnimation(source=source, destination=destination, pasteMethod=pasteMethod, offset=offset, start=start, end=end)


def copyHierarchy(sourceTop=None, destinationTop=None, pasteMethod='replace', offset=0, addToLayer=False):
    '''
    Copy animation from a source hierarchy and paste it to a destination hierarchy.
    '''
    start, end = _getStartAndEnd()
    
    if not sourceTop and not destinationTop:
        sel = mc.ls(sl=True)
        
        if len(sel) != 2:
            OpenMaya.MGlobal.displayWarning('Please select exactly 2 objects.')
            return
            
        sourceTop = sel[0]
        destinationTop = sel[1]
    
    #get keyed objects below source
    nodes = mc.listRelatives(sourceTop, pa=True, ad=True)
    keyed = list()
    
    for node in nodes:
        # this will only return time based keyframes, not driven keys
        if mc.keyframe(node, time=(':',), query=True, keyframeCount=True):
            keyed.append(node)
    
    if not keyed:
        return
    
    #get a list of all nodes under the destination
    destNames = [x.partition(':')[-1] for x in mc.listRelatives(destinationTop, ad=True)]
    destNS = destinationTop.partition(':')[0]
    
    layer = None
    if addToLayer:
        layer = mc.animLayer('myLayer')
    
    for node in keyed:
        nodeName = mc.ls(node, shortNames=True)[0]
        nodeName = nodeName.partition(':')[-1]
        
        if nodeName in destNames:
            destNode = mc.ls(destNS+':'+nodeName)
            if not destNode:
                print 'Cannot find destination node: '+destNS+':'+nodeName
                continue
            if len(destNode) > 1:
                print 'Two or more destination nodes have the same name: '+destNS+':'+nodeName
                continue
            
            copyAnimation(source=node, destination=destNode[0], pasteMethod=pasteMethod, offset=offset, start=start, end=end, layer=layer)
    

def copyAnimation(source=None, destination=None, pasteMethod='replace', offset=0, start=None, end=None, layer=None):
    '''
    Actually do the copy and paste from one node to another. If start and end frame is specified,
    set a temporary key before copying, and delete it afterward.
    '''
    
    if pasteMethod=='replaceCompletely' or not start or not end:
        mc.copyKey(source)
        mc.pasteKey(destination, option=pasteMethod, timeOffset=offset)
    else:
        
        #need to do this per animation curve, unfortunately, to make sure we're not adding or removing too many keys
        animCurves = mc.keyframe(source, query=True, name=True)
        if not animCurves:
            return
        
        #story cut keytimes as 2 separate lists means we only have to run 2 cutkey commands, rather than looping through each
        cutStart = list()
        cutEnd = list()
        for curve in animCurves:
        
            #does it have keyframes on the start and end frames?
            startKey = mc.keyframe(curve, time=(start,), query=True, timeChange=True)
            endKey = mc.keyframe(curve, time=(end,), query=True, timeChange=True)

            #if it doesn't set a temporary key for start and end
            #and store the curve name in the appropriate list
            if not startKey:
                mc.setKeyframe(curve, time=(start,), insert=True)
                cutStart.append(curve)
            if not endKey: 
                mc.setKeyframe(curve, time=(end,), insert=True)
                cutEnd.append(curve)
            
        mc.copyKey(source, time=(start,end))
        mc.pasteKey(destination, option=pasteMethod, time=(start,end), copies=1, connect=0, timeOffset=offset)

        #if we set temporary source keys, delete them now
        if cutStart:
            mc.cutKey(cutStart, time=(start,))
        if cutEnd:
            mc.cutKey(cutEnd, time=(end,))


if __name__ == '__main__': ui()


#      ______________________
# - -/__ Revision History __/- - - - - - - - - - - - - - - - - - - - - - - -
#
# Revision 1: 2012-03-14 : First publish.
