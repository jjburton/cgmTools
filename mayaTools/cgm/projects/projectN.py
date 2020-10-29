import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_RigMeta as RIGMETA
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.rigger.lib import rig_Utils as rUtils
#reload(rUtils)
from cgm.core.classes import NodeFactory as NodeF
import cgm.core.lib.distance_utils as DIST
from cgm.core import cgm_General as cgmGEN

import maya.cmds as mc
import pprint

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


"""
mc.delete(mc.ls(type='positionMarker'))
mBlock.moduleTarget.rigNull.msgList_get('moduleJoints')
mBlock.atUtils('skeletonized_query')
l_startSnap = [[-0.00018139342393015353, 7.605513570170998, -66.5626329131333], [-0.00018139342392977642, 10.684854532060829, -59.775072715719574], [-0.00018139342392956887, 12.379601233577182, -51.42832399692508], [0.5210297752251732, 15.19091061410884, -40.06570333283602]]
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    for i,p in enumerate(l_startSnap):
        POS.set("{0}.cv[{1}]".format(mObj.mNode,i), p)

mc.ls(sl=1)
mWheel = cgmMeta.asMeta('socket_wheel')
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    mObj.doSnapTo(mWheel)
    
cgmMeta.asMeta(sl=1)[0].dagLock(False)
l_sl = []    
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    l_sl.append(mObj.mNode)
    mPath = cgmMeta.asMeta(mc.listConnections(mObj.mNode, type='motionPath')[0])
    l_sl.append(mPath.mNode)
mc.select(l_sl)

mc.listConnections('outro_stuff_rework|exit_p2c1|exit_p2c1Shape->|orientationMarker94|orientationMarkerShape94')
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    print mc.listConnections(mObj.getShapes()[0],type='positionMarker')

l_startSnap = [[-0.00018139342393015353, 7.605513570170998, -66.5626329131333], [-0.00018139342392977642, 10.684854532060829, -59.775072715719574], [-0.00018139342392956887, 12.379601233577182, -51.42832399692508], [0.5210297752251732, 15.19091061410884, -40.06570333283602]]
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    for i,p in enumerate(l_startSnap):
        POS.set("{0}.cv[{1}]".format(mObj.mNode,i), p)
cgmGEN.__mayaVersion__
reload(ATTR)
#Snap pivot 1 to match targets...
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    mMatch = mObj.getMessageAsMeta('cgmMatchTarget')
    ml_space = mObj.msgList_get('spacePivots')
    print mMatch
    print ml_space
    mc.parentConstraint([mMatch.mNode],ml_space[0].mNode,maintainOffset = False)
    
#Snap  
for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    ml_space = mObj.msgList_get('spacePivots')
    mc.parentConstraint(['holdem_sockets:startScoket'],ml_space[1].mNode,maintainOffset = False) 
    
for mObj in cgmMeta.asMeta(sl=1):
    print mObj

for mObj in cgmMeta.asMeta(mc.ls(sl=1)):
    print mObj
    
    
mLoc = cgmMeta.asMeta(mc.spaceLocator()[0])
mLoc2 = cgmMeta.asMeta(mc.spaceLocator()[0])

mLoc.doConnectOut('ty',"{0}.ty".format(mLoc2.mNode))
mLoc.doConnectIn('tx',"{0}.tx".format(mLoc2.mNode))



"""

def cards_outSnap(nodes = None):
    if not nodes:
        mNodes = cgmMeta.asMeta(sl=1)
    else:
        
        mNodes = cgmMeta.asMeta(nodes)
        
    _current = mc.currentTime(q=True)

    for mObj in mNodes:
        mc.currentTime(_current)        
        mObj.doSnapTo('holdem_sockets:socket_wheel')
        mObj.scaleY = .5
        
        mc.setKeyframe(mObj.mNode)
        
        mc.currentTime(_current+1)
        mObj.doSnapTo('holdem_sockets:startScoket')
        mObj.scaleY = .25
        mc.setKeyframe(mObj.mNode)
        
    _current = mc.currentTime(q=True)

