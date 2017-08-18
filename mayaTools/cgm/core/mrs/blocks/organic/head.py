"""
------------------------------------------
cgm.core.mrs.blocks.simple.torso
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
from cgm.core.lib import snap_utils as SNAP
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.position_utils as POS
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.locator_utils as LOC
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
for m in DIST,POS,MATH,CONSTRAINT,LOC,BLOCKUTILS:
    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.08072017'
__autoTemplate__ = False


#>>>Attrs ----------------------------------------------------------------------------------------------------
_l_coreNames = ['head']

l_attrsStandard = ['side',
                   'position',
                   'proxyType',
                   'hasRootJoint',
                   'buildIK',
                   'baseNames',
                   'proxyShape',
                   #'customStartOrientation',
                   'moduleTarget',]

d_attrsToMake = {'proxyShape':'cube:sphere:cylinder'}

d_defaultSettings = {'version':__version__,
                     'baseSize':1,
                     'attachPoint':'base',
                     'buildIK':True,
                     'proxyShape':'cube',
                     'baseNames':['head'],#...our datList values
                     'proxyType':1}

#Skeletal stuff ------------------------------------------------------------------------------------------------
d_skeletonSetup = {'mode':'handle',
                   'targetsMode':'msg',
                   'targets':'jointHelper'}

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotationOrders = {'head':'yxz'}

#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode

#=============================================================================================================
#>> Template
#=============================================================================================================    
def templateDelete(self):
    return BLOCKUTILS.templateDelete(self,['orientHelper'])

is_template = BLOCKUTILS.is_template

  
def template(self):
    _str_func = 'template'
    
    _short = self.p_nameShort
    _size = self.baseSize
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
    
    log.info("|{0}| >> [{1}] | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))            

    #Create temple Null  ==================================================================================
    mTemplateNull = BLOCKUTILS.templateNull_verify(self)
    

    #Our main rigBlock shape =================================================================================
    #_crv = CURVES.create_controlCurve(self.mNode,shape='circleArrow',side = 'y+', sizeMode = 'fixed', size = _size * 14)
    #CORERIG.colorControl(_crv,_side,'main')
    #CORERIG.shapeParent_in_place(self.mNode,_crv,False)   
    #height = _size, width = _size
    
    #_shape = self.getEnumValueString('proxyShape')
    #_res = d_build[self.getEnumValueString('proxyShape')]()
    
    #SNAP.go(_res[0],self.mNode)
    
    mHandleFactory = self.asHandleFactory(self.mNode)
    mHandleFactory.rebuildSimple('cube', _size, shapeDirection = 'y+')
    pprint.pprint(vars())
    
    #TRANS.parent_set(_res[0],mTemplateNull.mNode)
    CORERIG.colorControl(self.mNode,_side,'main',transparent = True)
    
    return True

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def build_prerigMesh(self):
    _str_func = 'build_prerigMesh'    
    _shape = self.getEnumValueString('proxyShape')
    _size = self.baseSize
    
    if _shape == 'cube':
        _res = mc.polyCube(width=_size, height = _size)
    elif _shape == 'sphere':
        _res = mc.polySphere(radius = _size * .5)
    elif _shape == 'cylinder':
        _res = mc.polyCylinder(height = _size, radius = _size * .5)
    else:
        raise ValueError,"|{0}| >> Unknown shape: [{1}]".format(_str_func,_shape)
    return _res

def prerig(self):
    _str_func = 'prerig'
        
    _short = self.p_nameShort
    _size = self.baseSize
    _sizeSub = _size * .2
    
    #_baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    _side = 'center'
    
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
    
    log.info("|{0}| >> [{1}] | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     
        
    self._factory.module_verify()  
    
    #Create preRig Null  ==================================================================================
    mPrerigNull = BLOCKUTILS.prerigNull_verify(self)   
    
    #Joint Helper ==========================================================================================
    mJointHelper = self.asHandleFactory(self.mNode).addJointHelper(baseSize = _sizeSub)
    #mJointHelper.scale = 1,1,1    
    
    
    #Prerig Mesh ==========================================================================================
    _res = build_prerigMesh(self)
    mProxy = cgmMeta.validateObjArg(_res[0],'cgmObject',setClass=True)
    mProxy.doSnapTo(self.mNode)
    mProxy.parent = mPrerigNull
    
    CORERIG.colorControl(mProxy.mNode,_side,'main',transparent = True)
    for mShape in mProxy.getShapes(asMeta=1):
        mProxy.overrideEnabled = 1
        mShape.overrideDisplayType = 2   
    
    mProxy.scale = self.getScaleLossy()
    mProxy.parent = mPrerigNull
    
    pprint.pprint(vars())
    
    return True

def prerigDelete(self):
    return BLOCKUTILS.prerig_delete(self,templateHandles=True)

def is_prerig(self):
    return BLOCKUTILS.is_prerig(self,msgLinks=['moduleTarget','prerigNull'])


def build_skeleton(self):
    _short = self.mNode
    _str_func = '[{0}] > build_skeleton'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    
    ml_joints = self._factory.create_skeleton()
    
    self.moduleTarget.rigNull.msgList_connect('handleJoints',ml_joints)
    
    ml_joints[0]
    ml_skinJoints = []
    for i,i_jnt in enumerate(ml_joints):
        ml_skinJoints.append(i_jnt)		

        mDup = i_jnt.doDuplicate()#Duplicate
        mDup.addAttr('cgmNameModifier','scale',lock=True)#Tag
        #i_jnt.doName()#Rename
        mDup.doName()#Rename
        mDup.parent = i_jnt#Parent
        mDup.connectChildNode(i_jnt,'rootJoint','scaleJoint')#Connect
        #------------------------------------------------------------
        ml_skinJoints.append(mDup)#Append
        log.info("|{0}| >> Created scaleJoint: {1}".format(_str_func,mDup.mNode))  

    self.moduleTarget.rigNull.msgList_connect('skinJoints',ml_skinJoints) 
    return True

#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotationOrders = {'head':'yxz'}

def skeleton_pushSettings(self, ml_chain, d_rotateOrders = {}, d_limits = {} ):
    _short = self.mNode
    _str_func = '[{0}] > skeleton_pushSettings'.format(_short)
    
    #Orientation 
    #Direction
    
    return
    for mJnt in ml_chain:
        _key = mJnt.getMayaAttr('cgmName')
        _rotateOrderBuffer = d_rotationOrders.get(_key,False)
        if _rotateOrderBuffer:
            log.info("|{0}| >> found data on {1}:{2}".format(_str_func,_key,_rotateOrderBuffer))  
            

            #log.info("preferred angles(%s)>>> %s"%(i_jnt.cgmName,__d_preferredAngles__.get(i_jnt.cgmName)))
            for i,v in enumerate(_rotateOrderBuffer):	
                if self._go._direction.lower() == 'right':#negative value
                    i_jnt.__setattr__('preferredAngle%s'%self._go._jointOrientation[i].upper(),-v)				
                else:
                    i_jnt.__setattr__('preferredAngle%s'%self._go._jointOrientation[i].upper(),v)
    
    
#Rig build stuff goes through the rig build factory ------------------------------------------------------

def build_rigSkeleton(self):
    _short = self.mBlock.mNode
    _str_func = '[{0}] > build_rigSkeleton'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    
    log.info("|{0}| >> Chcking extra dat...".format(_str_func))  
    
    
    
    return
    ml_rigJoints = BLOCKUTILS.skeleton_buildRigChain(self.mBlock)
    
    ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(self.mBlock,'fk','fkJoints')
    
    if i_jnt.cgmName in __d_preferredAngles__.keys():
        #log.info("preferred angles(%s)>>> %s"%(i_jnt.cgmName,__d_preferredAngles__.get(i_jnt.cgmName)))
        for i,v in enumerate(__d_preferredAngles__.get(i_jnt.cgmName)):	
            if self._go._direction.lower() == 'right':#negative value
                i_jnt.__setattr__('preferredAngle%s'%self._go._jointOrientation[i].upper(),-v)				
            else:
                i_jnt.__setattr__('preferredAngle%s'%self._go._jointOrientation[i].upper(),v)
    
    
    if self.buildIK:
        log.info("|{0}| >> buildIK on. Building blend and IK chains...".format(_str_func))  
        ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(self,'blend','blendJoints')
        ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(self,'ik','ikJoints')
        
    
    return
    mi_go = self.d_kws['goInstance']
    #>>>Create joint chains
    #=============================================================    
    try:		
        ml_skinJoints = mi_go._ml_skinJoints
        ml_moduleJoints = mi_go._ml_moduleJoints
        ml_segmentHandleJoints = []

        #>>Rig chain  
        #=====================================================================	
        ml_rigJoints = mi_go.build_rigChain()
        l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
        ml_handleJoints = mi_go._mi_module.rig_getRigHandleJoints()

        ml_handleJoints[0].parent = False#Parent to world
        ml_handleJoints[-1].parent = False#Parent to world
    except Exception,error:raise Exception,"Create rig chain! | error: {0}".format(error)


    try:#Connection
        _str_subFunc = "Connection"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  

        #>>> Store em all to our instance
        mi_go._i_rigNull.connectChildNode(i_startJnt,'startAnchor','rigNull')
        mi_go._i_rigNull.connectChildNode(i_endJnt,'endAnchor','rigNull')	
        mi_go._i_rigNull.msgList_connect('anchorJoints',ml_anchors,'rigNull')
        mi_go._i_rigNull.msgList_connect('segmentJoints',ml_segmentJoints,'rigNull')	
        mi_go._i_rigNull.msgList_connect('influenceJoints',ml_influenceJoints,'rigNull')


        mi_go.get_report()

    except Exception,error:raise Exception,"Connect! | error: {0}".format(error)


    try:#Gut connect
        _str_subFunc = "Guts connect"	
        ml_jointsToConnect = [i_startJnt,i_endJnt]
        ml_jointsToConnect.extend(ml_rigJoints)
        ml_jointsToConnect.extend(ml_segmentJoints)    
        ml_jointsToConnect.extend(ml_influenceJoints)

        mi_go.connect_toRigGutsVis( ml_jointsToConnect )

    except Exception,error:raise Exception,"Guts connect! | error: {0}".format(error)
    return True
    
    
    

"""def rig(self):    
    if self.hasRootJoint:
        mJoint = self.doCreateAt('joint')
        mJoint.parent = self.moduleTarget.masterNull.skeletonGroup
        mJoint.connectParentNode(self,'module','rootJoint')
    raise NotImplementedError,"Not done."

def rigDelete(self):
    try:self.moduleTarget.masterControl.delete()
    except Exception,err:
        for a in err:
            print a
    return True

def is_rig(self):
    _str_func = 'is_rig'
    _l_missing = []

    _d_links = {'moduleTarget' : ['masterControl']}

    for plug,l_links in _d_links.iteritems():
        _mPlug = self.getMessage(plug,asMeta=True)
        if not _mPlug:
            _l_missing.append("{0} : {1}".format(plug,l_links))
            continue
        for l in l_links:
            if not _mPlug[0].getMessage(l):
                _l_missing.append(_mPlug[0].p_nameBase + '.' + l)


    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True"""


__l_rigBuildOrder__ = [build_rigSkeleton,
                       ]



















