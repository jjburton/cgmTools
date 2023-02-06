# 
#   -= ml_worldBake.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 10, 2012-11-15
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_worldBake.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_worldBake
#     ml_worldBake.ui()
# From MEL, this looks like:
#     python("import ml_worldBake;ml_worldBake.ui()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
#  
# Temporarily bake animation to locators in world (or custom) space.
# Use  this tool to preserve the worldspace position of animation when you need to make
# positional changes to an object's parent.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#  
# Run the tool, select the objects, then press the "To Locators" button.
# When you're ready to bake back, select the locators and press the 
# "From Locators" button. Checking "Bake on Ones" will bake every frame,
# otherwise the keytimes will be derived from the original animation.
#      ________________
# - -/__ UI Options __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# [Bake Selection To Locators] : Bake selected object to locators specified space.
# [Bake Selected Locators Back To Objects] : Bake from selected locators back to their source objects.
# [Bake Selected] : Bake from the first selected object directly to the second.
# [Bake Selected With Offset] : Bake from the first selected object directly to the second, maintaining offset.
#      __________________
# - -/__ Requirements __/- - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# This script requires the ml_utilities module, which can be downloaded here:
# 	http://morganloomis.com/wiki/tools.html#ml_utilities
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 10

import maya.cmds as mc
from maya import OpenMaya

try:
    from . import ml_utilities as utl
    utl.upToDateCheck(8)
except ImportError:
    result = mc.confirmDialog( title='Module Not Found', 
                message='This tool requires the ml_utilities module. Once downloaded you will need to restart Maya.', 
                button=['Download Module','Cancel'], 
                defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel' )
    
    if result == 'Download Module':
        mc.showHelp('http://morganloomis.com/download/ml_utilities.py',absolute=True)
    
def ui():
    '''
    User interface for world bake
    '''

    with utl.MlUi('ml_worldBake', 'World Bake', width=400, height=175, info='''Select objects, bake to locators in world, camera, or custom space.
When you're ready to bake back, select locators
and bake "from locators" to re-apply your animation.''') as win:

        mc.checkBoxGrp('ml_worldBake_bakeOnOnes_checkBox',label='Bake on Ones', 
                       annotation='Bake every frame. If deselected, the tool will preserve keytimes.')
        
        tabs = mc.tabLayout()
        tab1 = mc.columnLayout(adj=True)
        mc.radioButtonGrp('ml_worldBake_space_radioButton', label='Bake To Space', numberOfRadioButtons=3,
                          labelArray3=('World','Camera','Last Selected'), select=1,
                          annotation='The locators will be parented to world, the current camera, or the last selection.')
        mc.checkBoxGrp('ml_worldBake_constrain_checkBox',label='Maintain Constraints', 
                       annotation='Constrain source nodes to the created locators, after baking.')
        
        win.ButtonWithPopup(label='Bake Selection To Locators', command=toLocators, annotation='Bake selected object to locators specified space.',
            readUI_toArgs={'bakeOnOnes':'ml_worldBake_bakeOnOnes_checkBox',
                           'spaceInt':'ml_worldBake_space_radioButton', 
                           'constrainSource':'ml_worldBake_constrain_checkBox'}, 
            name=win.name)#this last arg is temp..
        mc.setParent('..')
        
        tab2 = mc.columnLayout(adj=True)
        win.ButtonWithPopup(label='Bake Selected Locators Back To Objects', command=fromLocators, annotation='Bake from selected locators back to their source objects.',
            readUI_toArgs={'bakeOnOnes':'ml_worldBake_bakeOnOnes_checkBox'}, name=win.name)#this last arg is temp..
        mc.setParent('..')
        
        tab3 = mc.columnLayout(adj=True)
        mc.checkBoxGrp('ml_worldBake_maintainOffset_checkBox',label='Maintain Offset', 
                       annotation='Maintain the offset between nodes, rather than snapping.')
        win.ButtonWithPopup(label='Bake Selected', command=matchBake, annotation='Bake from the first selected object directly to the second.',
            readUI_toArgs={'bakeOnOnes':'ml_worldBake_bakeOnOnes_checkBox',
                           'maintainOffset':'ml_worldBake_maintainOffset_checkBox'}, name=win.name)#this last arg is temp..
        
        mc.tabLayout( tabs, edit=True, tabLabel=((tab1, 'Bake To Locators'), (tab2, 'Bake From Locators'), (tab3, 'Bake Selection')) )        
#        win.ButtonWithPopup(label='Bake Selected With Offset', command=matchBake, annotation='Bake from the first selected object directly to the second, maintaining offset.',
#            readUI_toArgs={'bakeOnOnes':'ml_worldBake_bakeOnOnes_checkBox'}, name=win.name)#this last arg is temp..


 
def toLocators(bakeOnOnes=False, space='world', spaceInt=None, constrainSource=False):
    '''
    Creates locators, and bakes their position to selection.
    Creates connections to the source objects, so they can 
    be found later to bake back.
    '''
    
    if spaceInt and 0 <= spaceInt <= 2:
        space = ['world', 'camera', 'last'][spaceInt]
    
    sel = mc.ls(sl=True)
    parent = None
    if space == 'camera':
        parent = utl.getCurrentCamera()
    elif space == 'last':
        parent = sel[-1]
        sel = sel[:-1]
    
    mc.select(sel)
    matchBakeLocators(parent=parent, bakeOnOnes=bakeOnOnes, constrainSource=constrainSource)


def fromLocators(bakeOnOnes=False):
    '''
    Traces connections from selected locators to their source nodes, and 
    bakes their position back.
    Arguments:
        bakeOnOnes :: Bool :: Preserve the original keytimes from the locator.
    '''
    #get neccesary nodes
    objs = mc.ls(sl=True)
    if not objs:
        OpenMaya.MGlobal.displayWarning('Select a previously baked locator.')
        return
    
    source = list()
    destination = list()
    
    for src in objs:
        try:
            dest = mc.listConnections(src+'.ml_bakeSource',destination=False)[0]
            if dest:
                source.append(src)
                destination.append(dest)
            
        except Exception:
            pass
    
    if not destination:
        OpenMaya.MGlobal.displayWarning('Select a previously baked locator.')
        return
    
    #delete constraints on destination nodes
    for each in destination:
        constraints = mc.listConnections(each, source=True, destination=False, type='constraint')
        if constraints:
            try:
                mc.delete(constraints)
            except Exception:
                pass
    
    matchBake(source, destination, bakeOnOnes=bakeOnOnes)
    
    for each in source:
        mc.delete(each)


def matchBakeLocators(parent=None, bakeOnOnes=False, constrainSource=False):

    #get neccesary nodes
    objs = mc.ls(sl=True)
    if not objs:
        OpenMaya.MGlobal.displayWarning('Select an Object')
        return
    
    locs = list()
    cutIndex = dict()
    noKeys = list()
    noKeysLoc = list()
    
    for obj in objs:
        
        
        name = mc.ls(obj, shortNames=True)[0]
        if ':' in name:
            name = obj.rpartition(':')[-1]
        
        locator = mc.spaceLocator(name='worldBake_'+name+'_#')[0]
        mc.setAttr(locator+'.rotateOrder', 3)
        
        
        mc.addAttr(locator, longName='ml_bakeSource', attributeType='message')
        mc.connectAttr('.'.join((obj,'message')), '.'.join((locator,'ml_bakeSource')))
        mc.addAttr(locator, longName='ml_bakeSourceName', dataType='string')
        mc.setAttr('.'.join((locator,'ml_bakeSourceName')), name, type='string')
        
        if parent:
            locator = mc.parent(locator, parent)[0]
        
        locs.append(locator)
        
        #should look through all trans and rot
        if not mc.keyframe(obj, query=True, name=True):
            noKeys.append(obj)  
            noKeysLoc.append(locator)

    matchBake(objs, locs, bakeOnOnes=bakeOnOnes)
    
    if not bakeOnOnes and noKeys:
        matchBake(noKeys, noKeysLoc, bakeOnOnes=True)
    
    if constrainSource:
        mc.cutKey(objs)
        for loc, obj in zip(locs, objs):
            mc.parentConstraint(loc, obj)
    

def matchBake(source=None, destination=None, bakeOnOnes=False, maintainOffset=False):

    if not source and not destination:
        sel = mc.ls(sl=True)
        if len(sel) != 2:
            OpenMaya.MGlobal.displayWarning('Select exactly 2 objects')
            return
        source = [sel[0]]
        destination = [sel[1]]

    #save for reset:
    resetTime = mc.currentTime(query=True)
    
    #frame range
    start, end = utl.frameRange()
    
    attributes = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ']
    
    duplicates = dict()
    keytimes = dict()
    constraint = list()
    itt = dict()
    ott = dict()
    #initialize allKeyTimes with start and end frames, since they may not be keyed
    allKeyTimes = [start,end]
    for s,d in zip(source,destination):
    
        #duplicate the destination
        dup = mc.duplicate(d, name='temp#', parentOnly=True)[0]
        for a in attributes:
            mc.setAttr(dup+'.'+a, lock=False, keyable=True)
        
        constraint.append(mc.parentConstraint(s, dup, maintainOffset=maintainOffset))
        
        #cut keys on destination
        mc.cutKey(d, attribute=attributes, time=(start,end))

        #set up our data dictionaries
        duplicates[d] = dup
        keytimes[d] = dict()
        itt[d] = dict()
        ott[d] = dict()
        
        #if we're baking on ones, we don't need keytimes
        if not bakeOnOnes:
            for a in attributes:
                currKeytimes = mc.keyframe(s, attribute=a, time=(start,end), query=True, timeChange=True)
                if not currKeytimes:
                    continue
                
                keytimes[d][a] = currKeytimes
                allKeyTimes.extend(currKeytimes)
                
                itt[d][a] = mc.keyTangent(s, attribute=a, time=(start,end), query=True, inTangentType=True)
                ott[d][a] = mc.keyTangent(s, attribute=a, time=(start,end), query=True, outTangentType=True)
                
                #change fixed tangents to spline, because we can't set fixed tangents
                for i, each in enumerate(itt[d][a]):
                    if each == 'fixed':
                        itt[d][a][i] = 'spline'
                        
                for i, each in enumerate(ott[d][a]):
                    if each == 'fixed':
                        ott[d][a][i] = 'spline'
                #in the future, save tangent in and out values
                
                
                #add the start and end frames and tangents if they're not keyed
                if not start in keytimes[d][a]:
                    keytimes[d][a].insert(0,start)
                    itt[d][a].insert(0,'spline')
                    ott[d][a].insert(0,'spline')
                if not end in keytimes[d][a]:
                    keytimes[d][a].append(end)
                    itt[d][a].append('spline')
                    ott[d][a].append('spline')
                #reverse these, because we want to pop but start from the beginning
                itt[d][a].reverse()
                ott[d][a].reverse()
    
    if bakeOnOnes:
        allKeyTimes = list(range(int(start), int(end)+1))
    else:
        allKeyTimes = list(set(allKeyTimes))
        allKeyTimes.sort()
    
    with utl.UndoChunk():
        with utl.IsolateViews():
            for frame in allKeyTimes:
                #cycle through all the frames
                mc.currentTime(frame, edit=True)
                for d in destination:
                    for a in attributes:
                        if bakeOnOnes:
                            mc.setKeyframe(d, attribute=a, time=frame, 
                                           value=mc.getAttr(duplicates[d]+'.'+a),
                                           itt='spline',
                                           ott='spline')
                        elif a in keytimes[d] and frame in keytimes[d][a]:
                            #tangent types line up with keytimes
                            mc.setKeyframe(d, attribute=a, time=frame, 
                                           value=mc.getAttr(duplicates[d]+'.'+a), 
                                           itt=itt[d][a].pop(), 
                                           ott=ott[d][a].pop()
                                           )
        #reset time and selection
        mc.currentTime(resetTime, edit=True)
        mc.select(destination, replace=True)
    
    mc.delete(list(duplicates.values()))
    mc.filterCurve(mc.listConnections(destination,type='animCurve'))
    if bakeOnOnes:
        mc.keyTangent(destination, attribute=attributes, itt='spline', ott='spline')


if __name__ == '__main__':
    #matchBakeLocators(constrainSource=True)
    ui()

#      ______________________
# - -/__ Revision History __/- - - - - - - - - - - - - - - - - - - - - - - - 
#
# Revision 1: : First publish
#
# Revision 6: : Updated to use ml_utilities. Changed from direct constraint to constrained duplicate node.
#
# Revision 7: 2011-05-13 : fixed a bug with transferring certain types of tangents.
#
# Revision 8: 2011-05-14 : fixed error baking things with transforms locked or hidden
#
# Revision 9: 2012-06-13 : fixing duplicate name bug, adding more error checking.
#
# Revision 10: 2012-11-15 : Converting UI to tabs, adding camera and explicit options.
