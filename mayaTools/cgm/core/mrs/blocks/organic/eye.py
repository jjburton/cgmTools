"""
------------------------------------------
cgm.core.mrs.blocks.organic.eye
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__MAYALOCAL = 'EYE'

# From Python =============================================================
import copy
import re
import pprint
import time
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
#r9Meta.cleanCache()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


import cgm.core.cgm_General as cgmGEN
from cgm.core.rigger import ModuleShapeCaster as mShapeCast

import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.assets as MRSASSETS
path_assets = cgmPATH.Path(MRSASSETS.__file__).up().asFriendly()

import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
#reload(MODULECONTROL)
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.lib.rigging_utils as CORERIG
from cgm.core.lib import snap_utils as SNAP
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.rig.joint_utils as JOINT
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.position_utils as POS
import cgm.core.lib.math_utils as MATH
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.locator_utils as LOC
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.shape_utils as SHAPES
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.ik_utils as IK
import cgm.core.cgm_RigMeta as cgmRIGMETA
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.string_utils as STR
import cgm.core.lib.surface_Utils as SURF
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.rig.general_utils as RIGGEN

#for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT:
#    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

DGETAVG = DIST.get_average_position
CRVPCT = CURVES.getPercentPointOnCurve
DPCTDIST = DIST.get_pos_by_linearPct
#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.10.31.2018'
__autoForm__ = False
__menuVisible__ = True
__faceBlock__ = True

#These are our base dimensions. In this case it is for human
__dimensions_by_type = {'box':[22,22,22],
                        'human':[15.2, 23.2, 19.7]}
d_build_profiles = {}

__l_rigBuildOrder__ = ['rig_dataBuffer',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_pupilIris',
                       'rig_lidSetup',
                       'rig_highlightSetup',
                       'rig_cleanUp']



d_wiring_define = {'msgLinks':[],
                   'msgLists':['defineStuff']}
d_wiring_skeleton = {'msgLinks':[],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull','eyeOrientHelper','rootHelper','noTransPrerigNull']}
d_wiring_form = {'msgLinks':['formNull','noTransFormNull'],
                 'msgLists':[]}
d_wiring_extraDags = {'msgLinks':['bbHelper'],
                      'msgLists':[]}

#>>>Profiles ==============================================================================================
d_build_profiles = {}


d_block_profiles = {
    'simpleEye':{'eyeType':'sphere',
                 'ikSetup':True,
                 'lidBuild':'none',
                 'baseDat':{'baseSize':[2.7,2.7,2.7]},
                 },
    'clam':{
    'eyeType':'sphere',
    'ikSetup':True,
    'lidBuild':'clam',
    'numLidUprJoints':1,
    'numLidLwrJoints':1,
    'baseDat':{'upr':[0,1,0],'lwr':[0,-1,0],'left':[1,0,0],'right':[-1,0,0],
               'baseSize':[2.7,2.7,2.7]},
       },
    'fullLid':{
    'eyeType':'sphere',
    'ikSetup':True,
    'lidBuild':'full',
    'numLidUprJoints':5,
    'numLidLwrJoints':5,
    'numConLids':3,
    'baseDat':{'upr':[0,1,0],'lwr':[0,-1,0],'left':[1,0,0],'right':[-1,0,0],
               'baseSize':[2.7,2.7,2.7]},
       }
}



#>>>Attrs =================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'baseAim',
                   'attachPoint',
                   'attachIndex',
                   'nameList',
                   'buildSDK',
                   'numSpacePivots',
                   'loftDegree',
                   'loftSplit',
                   'scaleSetup',
                   'visLabels',
                   'jointRadius',
                   'controlOffset',
                   'conDirectOffset',
                   'proxyDirect',
                   'moduleTarget',
                   'visProximityMode',                   
                   'scaleSetup']

d_attrsToMake = {'eyeType':'sphere:nonsphere',
                 'buildEyeOrb':'bool',
                 'ikSetup':'bool',
                 'paramMidUpr':'float',
                 'paramMidLwr':'float',
                 'ballSetup':'aim:fixed',
                 'pupilBuild':'none:shape:joint:blendshape',
                 'irisBuild':'none:shape:joint:blendshape',
                 'irisDepth':'float',
                 'lidAttach':'aimJoint:surfaceSlide',
                 'irisAttach':'parent:surfaceSlide',
                 'pupilAttach':'parent:surfaceSlide',
                 'lidBuild':'none:clam:full',
                 'lidType':'simple:full',
                 'lidDepth':'float',
                 'lidJointDepth':'float',
                 'lidClosed':'bool',
                 'lidFanUpr':'none:single',
                 'lidFanLwr':'none:single',
                 'prerigJointOrient':'bool',
                 'numConLids':'int',
                 'numLidUprJoints':'int',
                 'numLidUprShapers':'int',
                 'numLidLwrJoints':'int',
                 'numLidLwrShapers':'int',
                 'numLidSplit_u':'int',
                 'numLidSplit_v':'int',
                 'lidHandleOffset':'float',
                 'highlightSetup':'none:simple:sdk:surfaceSlide',

}

d_defaultSettings = {'version':__version__,
                     'proxyDirect':True,
                     'attachPoint':'end',
                     'side':'right',
                     'nameList':['eye','eyeOrb','pupil','iris','cornea'],
                     'loftDegree':'cubic',
                     'visLabels':True,
                     'paramMidUpr':.5,
                     'paramMidLwr':.5,
                     'pupilBuild':1,
                     'irisBuild':1,
                     'lidDepth':.108,
                     'baseSize':[2.7,2.7,2.7],
                     'numLidLwrShapers':3,
                     'numLidUprShapers':3,
                     'numLidSplit_u':10,
                     'numLidSplit_v':8,
                     'numConLids':1,
                     'jointRadius':1.0,
                     'prerigJointOrient':True,
                     'scaleSetup':False,
                     'numLidLwrShapers':5,
                     'numLidUprShapers':5,
                     #'baseSize':MATH.get_space_value(__dimensions[1]),
                     }

#=============================================================================================================
#>> AttrMask 
#=============================================================================================================
_d_attrStateOn = {0:['ikSetup'],
                  1:[],
                  2:[],
                  3:[],
                  4:[]}

_d_attrStateOff = {0:[],
                   1:[],
                   2:[],
                   3:[],
                   4:[]}


d_attrProfileMask = {'noLid':['numLidUprJoints','numLidUprShapers','numLidLwrJoints','numLidLwrShapers',
                              'loftDegree','loftSplit','lidBuild',
                              'paramMidUpr','paramMidLwr']}

for k in ['eyeSimple']:
    d_attrProfileMask[k] = d_attrProfileMask['noLid']
    
    
#=============================================================================================================
#>> Define
#=============================================================================================================
def uiBuilderMenu(self,parent = None):
    #uiMenu = mc.menuItem( parent = parent, l='Head:', subMenu=True)
    _short = self.p_nameShort
    
    mc.menuItem(en=False,divider=True,
                label = "Eye")
    
    mc.menuItem(ann = '[{0}] Snap state handles to surface'.format(_short),
                c = cgmGEN.Callback(uiFunc_snapStateHandles,self),
                label = "Snap state handles")
    
    mc.menuItem(ann = '[{0}] Snap selected objects to the surface'.format(_short),
                c = cgmGEN.Callback(uiFunc_snapSelectedToEye,self),
                label = "Snap Selected")
    mc.menuItem(ann = '[{0}] Aim prerig Handles down the chain'.format(_short),
                c = cgmGEN.Callback(uiFunc_aimPreHandles,self),
                label = "Aim Pre Handles")    
    mc.menuItem(en=True,divider = True,
                label = "Utilities")
    _sub = mc.menuItem(en=True,subMenu = True,tearOff=True,
                       label = "State Picker")
    
    #self.atUtils('uiStatePickerMenu',parent)
    
    #self.UTILS.uiBuilderMenu(self,parent)
    
    return

def uiFunc_snapStateHandles(self):
    _state = self.p_blockState
    
    if not self.blockState:
        ml_handles = self.msgList_get('defineSubHandles')
        uiFunc_snapSelectedToEye(self, ml_handles)

def uiFunc_snapSelectedToEye(self,ml=None):
    if not ml:
        ml = cgmMeta.asMeta(mc.ls(sl=1))
    
    if not ml:
        log.warning("Nothing Selected")
        return False
    
    mBBShape = self.getMessageAsMeta('bbHelper')
    if not mBBShape:
        log.warning("No eye surface found")
        return False
    
    for mObj in ml:
        try:mObj.p_position = DIST.get_closest_point(mObj.mNode, mBBShape.mNode)[0]
        except Exception,err:
            log.warning("Failed to snap: {0} | {1}".format(mObj.mNode,err))
            

def uiFunc_aimPreHandles(self,upr=1,lwr=1):
    _str_func = 'uiFunc_aimPreHandles'    
    
    _lidBuild = 'full'


    if _lidBuild == "full":
        _d_Lid = {'cgmName':'lid'}
        for d in 'upr','lwr':
            ml = self.prerigNull.msgList_get('{0}Drivers'.format(d))
            for i,mObj in enumerate(ml):
                if mObj == ml[-1]:
                    _target = ml[-2]
                    _axisAim = 'x-'
                else:
                    _target = ml[i+1]
                    _axisAim = 'x+'
            
                SNAP.aim_atPoint(mObj.mNode,
                                 _target.p_position,
                                 _axisAim, 'y+', 'vector',
                                 self.getAxisVector('y+'))
                
                #SNAP.go(mObj.shapeHelper.mNode, mObj.mNode,False)
                mObj.shapeHelper.p_orient = mObj.p_orient
                
                #SNAP.aim_atPoint(mObj.shapeHelper.mNode,
                #                _target.p_position,
                #                _axisAim, 'y+', 'vector',
                #                self.getAxisVector('y+'))
            
            
            
            
            """
            log.debug("|{0}| >>  lid {1}...".format(_str_func,d)+ '-'*20)
            d_dir = copy.copy(_d_Lid)
            d_dir['cgmPosition'] = d
            
            for side in ['inner','center','outer']:
                d_dir['cgmDirection'] = _side
                key = d+'Lid'+side.capitalize()        
                mHandles = mPrerigNull.msgList_get('{0}JointHelpers'.format(key))
                ml = []
                for mHandle in mHandles:
                    mJnt = create_jointFromHandle(mHandle,mRoot)
                    ml.append(mJnt)
                    mShape = mHandle.shapeHelper
                    mShape.connectChildNode(mJnt,'targetJoint')
                    
    
                mPrerigNull.msgList_connect('{0}Joints'.format(key),ml)
                ml_joints.extend(ml)            """

    
#=============================================================================================================
#>> Define
#=============================================================================================================
@cgmGEN.Timer
def define(self):
    _str_func = 'define'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.mNode
    _side = self.UTILS.get_side(self)
    
    ATTR.set_alias(_short,'sy','blockScale')    
    self.setAttrFlags(attrs=['sx','sz','sz'])
    self.doConnectOut('sy',['sx','sz'])    
    
    #ATTR.set_min(_short, 'loftSides', 3)
    ATTR.set_min(_short, 'loftSplit', 1)
    ATTR.set_min(_short, 'numLidLwrShapers', 3)
    ATTR.set_min(_short, 'numLidUprShapers', 3)
        
    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)
        defineNull = self.getMessage('defineNull')
        if defineNull:
            log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
            mc.delete(defineNull)
            
    #self.atUtils('define_set_baseSize')
    _size = self.atUtils('defineSize_get')
    
    _crv = CURVES.create_fromName(name='locatorForm',#'axis3d',#'arrowsAxis', 
                                  direction = 'z+', size = _size/4)
    SNAP.go(_crv,self.mNode,)
    CORERIG.override_color(_crv, 'white')        
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    mHandleFactory = self.asHandleFactory()
    self.addAttr('cgmColorLock',True,lock=True, hidden=True)
    mDefineNull = self.atUtils('stateNull_verify','define')
    
    mNoTransformNull = self.getMessageAsMeta('noTransDefineNull')
    if mNoTransformNull:
        mNoTransformNull.delete()
        
    mNoTransformNull = self.atUtils('noTransformNull_verify','define',mVisLink=self)
    ml_handles = []
    
    """
    #Rotate Group ==================================================================
    mRotateGroup = cgmMeta.validateObjArg(mDefineNull.doGroup(True,False,asMeta=True,typeModifier = 'rotate'),
                                          'cgmObject',setClass=True)
    mRotateGroup.p_parent = mDefineNull
    mRotateGroup.doConnectIn('rotate',"{0}.baseAim".format(_short))
    mRotateGroup.setAttrFlags()"""
    
    _size_width = self.baseSize[0]#...x width
    _size_base = _size_width * .25
    
    #Bounding sphere ==================================================================
    log.debug(cgmGEN.logString_msg(_str_func,'blockVolume...'))
    mBlockVolume = self.doCreateAt(setClass=1)

    mBlockVolume.doSnapTo(self)
    mBlockVolume.p_parent = mDefineNull    
    mBlockVolume.tz = -.5
    
    mBlockVolume.rename('blockVolume')
    
    #Mid driver ....
    log.debug(cgmGEN.logString_msg(_str_func,'midDriver...'))
    
    mMidDriver = mBlockVolume.doCreateAt(setClass=1)
    mMidDriver.rename('midDriver')
    mMidDriver.p_parent = mBlockVolume
    mMidDriver.dagLock()
    
    #Mid Group...
    log.debug(cgmGEN.logString_msg(_str_func,'midGroup...'))    
    mMidGroup = mMidDriver.doCreateAt(setClass=1)
    mMidGroup.rename('midGoup')
    mMidGroup.p_parent = mDefineNull
    mc.parentConstraint(mMidDriver.mNode, mMidGroup.mNode)
    mMidGroup.dagLock()
    self.connectChildNode(mMidGroup.mNode,'midDrivenDag','module')

    CORERIG.copy_pivot(mBlockVolume.mNode,self.mNode)
    
    
    #Create Pivot =====================================================================================
    """
    log.debug(cgmGEN.logString_msg(_str_func,'pivot...'))    
    
    crv = CURVES.create_fromName('sphere', size = _size_base/5)
    mHandleRoot = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
    mHandleFactory.color(mHandleRoot.mNode)

    #_shortHandle = mHandleRoot.mNode

    #ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
    mHandleRoot.doStore('cgmType','formHandle')
    mHandleRoot.rename('eyeRoot_formHandle')

    mHandleRoot.p_parent = mMidGroup
    mHandleRoot.resetAttrs()
    #mHandleRoot.doGroup(True,True,asMeta=True,typeModifier = 'center')

    self.connectChildNode(mHandleRoot.mNode,'rootHelper','module')
    ml_handles.append('rootHelper')"""
    
    #Create Pivot =====================================================================================
    log.debug(cgmGEN.logString_msg(_str_func,'pivot...'))
    _irisPosHelper = CURVES.create_fromName('sphere', size = _size_base/3)
    mShape = cgmMeta.validateObjArg(_irisPosHelper)

    mShape.doSnapTo(self.mNode)
    mShape.p_parent = mMidGroup

    mShape.tz = self.baseSizeZ
    mShape.rz = 90    
    

    mIrisPosHelper = self.doCreateAt(setClass=True)
    mIrisPosHelper.p_position = mShape.p_position
    
    CORERIG.shapeParent_in_place(mIrisPosHelper.mNode, mShape.mNode,False)
    
    
    
    mPupilTrackDriver = mIrisPosHelper.doCreateAt(setClass=1)
    mPupilTrackDriver.rename('eyeTrackDriver')
    
    mIrisPosHelper.p_parent = mDefineNull
    mIrisPosHelper.rename('irisPos_defineHandle')

    self.connectChildNode(mIrisPosHelper.mNode,'irisPosHelper','module')
    mHandleFactory.color(mIrisPosHelper.mNode,controlType='sub')
    
    ml_handles.append(mIrisPosHelper)    
    mPupilTrackDriver.p_parent = mIrisPosHelper#...parent our tracker to the orient handle    
    
    """
    #Orient helper =====================================================================================
    _orientHelper = CURVES.create_fromName('arrowSingle', size = _size_base)
    mShape = cgmMeta.validateObjArg(_orientHelper)


    mShape.doSnapTo(self.mNode)
    mShape.p_parent = mMidGroup

    mShape.tz = self.baseSizeZ
    mShape.rz = 90
    
    mPupilTrackDriver = self.doCreateAt(setClass=1)
    mPupilTrackDriver.rename('eyeTrackDriver')

    _crvLinear = CORERIG.create_at(create='curveLinear',
                                   l_pos=[mMidGroup.p_position,mShape.p_position])
    
    
    mOrientHelper = mMidGroup.doCreateAt(setClass=True)
    CORERIG.shapeParent_in_place(mOrientHelper.mNode, mShape.mNode,False)
    CORERIG.shapeParent_in_place(mOrientHelper.mNode, _crvLinear,False)
    
    mOrientHelper.p_parent = mMidGroup

    mOrientHelper.doStore('cgmType','formHandle')
    mOrientHelper.rename('eyeOrient_formHandle')

    self.connectChildNode(mOrientHelper.mNode,'eyeOrientHelper','module')
    mHandleFactory.color(mOrientHelper.mNode,controlType='sub')
    
    ml_handles.append(mOrientHelper)    
    mPupilTrackDriver.p_parent = mOrientHelper#...parent our tracker to the orient handle
    """

    #Bounding sphere ==================================================================
    #_bb_shape = CURVES.create_fromName('sphere', 1.0, baseSize=1.0)
    #_bb_shape = CORERIG.create_proxyGeo('sphere', [.5,.5,.5], 'z+',bakeScale=False)[0]
    _bb_shape = mc.sphere(axis=[0,0,1],ch=0,radius=.5,sections=6,spans=8)#[0]
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    for mShape in mBBShape.getShapes(asMeta=1):
        mShape.overrideEnabled = 1
        mShape.overrideDisplayType = 2
    mBBShape.doSnapTo(mMidDriver)
    mBBShape.p_parent = mMidDriver#mDefineNull    
    #mc.orientConstraint(mOrientHelper.mNode, mBBShape.mNode)
    #mBBShape.tz = -.5
    
    #CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
    #mHandleFactory.color(mBBShape.mNode,controlType='sub')
    CORERIG.colorControl(mBBShape.mNode,_side,controlType='sub',transparent = True)
    
    mBBShape.setAttrFlags()
    
    mBBShape.doStore('cgmName', self)
    mBBShape.doStore('cgmType','bbVisualize')
    mBBShape.doName()    
    
    self.connectChildNode(mBBShape.mNode,'bbHelper')
    
    str_meshShape = mBBShape.getShapes()[0]
    l_uIsos = SURF.get_dat(str_meshShape, uKnots=True)['uKnots']
    maxU = ATTR.get(str_meshShape,'maxValueU')
    l_use = []
    for i,k in enumerate(l_uIsos):
        if i in [5,6,7]:
            l_use.append(k)    
    #l_use.append(maxU * .95)
    ml_curves = []
    for i,k in enumerate(l_use):
        _crv = mc.duplicateCurve("{0}.{2}[{1}]".format(str_meshShape,k,'u'), ch = 1, rn = 0, local = 0)[0]
        mCrv = cgmMeta.validateObjArg(_crv, 'cgmObject',setClass=True)
        mCrv.p_parent = mNoTransformNull
        mHandleFactory.color(_crv)
        mCrv.rename("eye_knot_{0}_approx".format(i))
        #for mShape in mCrv.getShapes(asMeta=1):
            #mShape.overrideEnabled = 1
            #mShape.overrideDisplayType = 2
        mCrv.dagLock()
        
    #SurfaceTrackSphere ==========================================================
    log.debug(cgmGEN.logString_msg(_str_func,'surface...'))
    mSurface = mBBShape.doDuplicate(po=False)
    mSurface.rename('TrackSurface')
    mSurface.v=0
    
    self.connectChildNode(mSurface.mNode,'trackSurface')
        
        
    #Pupil/Iris =====================================================================
    log.debug(cgmGEN.logString_msg(_str_func,'Iris/pupil...'))
    
    b_irisShape = self.irisBuild
    b_pupilShape = self.pupilBuild
    
    if b_irisShape or b_pupilShape:
        
    
        mTrack = self.doCreateAt()
        mTrack.rename("pupilIris_surfaceDriver")
        mTrack.p_parent = mNoTransformNull
    
        _res = RIGCONSTRAINT.attach_toShape(mTrack.mNode,mSurface.mNode,'conParent',driver= mPupilTrackDriver)
        md = _res[-1]
        mFollicle = md['mFollicle']
        for k in ['mDriverLoc','mFollicle']:
            md[k].p_parent = mNoTransformNull
            md[k].v = False
            
        mDepth = mTrack.doCreateAt(setClass=1)
        mDepth.rename('irisDepth')
        mDepth.p_parent = mTrack
            
        ATTR.connect('{0}.irisDepth'.format(self.mNode), "{0}.tz".format(mDepth.mNode))
            
        for k in ['pupil','iris']:
            if k is 'pupil' and not b_pupilShape:
                continue
            if k is 'iris' and not b_irisShape:
                continue
            _shape = CURVES.create_fromName('circle', 1.0, baseSize=1.0)
            mHelper = cgmMeta.validateObjArg(_shape, 'cgmObject',setClass=True)
            mHelper.doSnapTo(self)
            mHandleFactory.color(mHelper.mNode,controlType='sub')
            ml_handles.append(mHelper)
            mHelper.rename("{0}_visualize".format(k))
            
            mHelper.p_parent = mDefineNull
            
            #if k == 'pupil':
            #    mHelper.tz = -.1
            #else:
            #    mHelper.tz = -.11
    
            mTransformedGroup = mHelper.doGroup(True,True,asMeta=True,
                                                typeModifier = 'driver',
                                                setClass='cgmObject')
            mc.parentConstraint(mDepth.mNode,mTransformedGroup.mNode)
            
            if k == 'pupil':
                _sizeUse = _size_width * .1
            else:
                _sizeUse = _size_width * .2
                
            mHelper.sx = _sizeUse        
            mHelper.sy = _sizeUse        
            
            #ATTR.connect('{0}.{1}Size'.format(self.mNode,k), "{0}.scaleY".format(mHelper.mNode))
            #ATTR.connect('{0}.{1}Size'.format(self.mNode,k), "{0}.scaleX".format(mHelper.mNode))
            
            self.connectChildNode(mHelper.mNode,'{0}Helper'.format(k))
            
            #mc.projectCurve(mBBShape.mNode, mHelper.mNode, ch=1, un=True)
            #mHelper.v = False
            #mHelper.template = True
            
            _surf = mc.planarSrf(mHelper.mNode,ch=1, d=3, ko=0, tol = .01, rn = 0, po = 0,
                                 name = "{0}_approx".format(k))
            mc.reverseSurface(_surf[0])
            mSurf = cgmMeta.validateObjArg(_surf[0], 'cgmObject',setClass=True)
            if k == 'iris':
                CORERIG.colorControl(mSurf.mNode,_side,'sub',transparent = True)
            else:
                CORERIG.colorControl(mSurf.mNode,_side,'main',transparent=True)
                
            mSurf.p_parent = mNoTransformNull
            mSurf.dagLock()
            #planarSrf -ch 1 -d 3 -ko 0 -tol 0.01 -rn 0 -po 0 "iris_visualizeShape";
            
            
            # projectCurve -ch true -rn false -un  true  -tol 0.01 "iris_visualizeShape" "clamLid__eyeBlock_bbVisualizeShape" ;
    
            #for mShape in mHelper.getShapes(asMeta=1):
                #mShape.overrideEnabled = 1
                #mShape.overrideDisplayType = 2        
        
        
        self.irisDepth = -_size_width * .04
        
    #...no connect scale
    self.doConnectOut('baseSize', "{0}.scale".format(mBlockVolume.mNode))

    #Lid stuff ======================================================================
    _sideMult = 1
    _axisOuter = 'x+'
    _axisInner = 'x-'
    
    if self.side == 1:
        _sideMult = -1
        _axisOuter = 'x-'
        _axisInner = 'x+'
        
    if self.lidBuild:
        _d = {#'aim':{'color':'yellowBright','defaults':{'tz':1}},
              'upr':{'color':'white','tagOnly':True,'arrow':False,
                     'vectorLine':False,'defaults':{'ty':1}},
              'lwr':{'color':'white','tagOnly':True,'arrow':False,
                     'vectorLine':False,'defaults':{'ty':-1}},
              'inner':{'color':'white','tagOnly':True,'arrow':False,
                       'vectorLine':False,'defaults':{'tx':1*_sideMult}},
              'outer':{'color':'white','tagOnly':True,'arrow':False,
                       'vectorLine':False,'defaults':{'tx':-1*_sideMult}},
              'uprEnd':{'color':'white','tagOnly':True,'arrowFollow':'upr','arrow':False,
                        'defaults':{'ty':1.5}},
              'lwrEnd':{'color':'white','tagOnly':True,'arrowFollow':'lwr','arrow':False,
                        'defaults':{'ty':-1.5}},
              'innerEnd':{'color':'white','tagOnly':True,'arrowFollow':'inner','arrow':False,
                          'defaults':{'tx':1.5*_sideMult}},
              'outerEnd':{'color':'white','tagOnly':True,'arrowFollow':'outer','arrow':False,
                          'defaults':{'tx':-1.5*_sideMult}},              
              }
    
        _l_order = ['upr','lwr','inner','outer',
                    'uprEnd','lwrEnd','innerEnd','outerEnd']
    
    
        md_res = self.UTILS.create_defineHandles(self, _l_order, _d, _size / 2)
        #self.UTILS.define_set_baseSize(self)
        
        md_handles = md_res['md_handles']
        ml_handlesSub = md_res['ml_handles']
        
        d_positions = {'inner':self.getPositionByAxisDistance(_axisOuter,_size*.75),
                       'outer':self.getPositionByAxisDistance(_axisInner,_size*.75),
                       'upr':self.getPositionByAxisDistance('y+',_size*.25),
                       'lwr':self.getPositionByAxisDistance('y-',_size*.25),
                       'innerEnd':self.getPositionByAxisDistance(_axisOuter,_size*.9),
                       'outerEnd':self.getPositionByAxisDistance(_axisInner,_size*.95),
                       'uprEnd':self.getPositionByAxisDistance('y+',_size*.8),
                       'lwrEnd':self.getPositionByAxisDistance('y-',_size*.8),                       
                       }
        
        for k,p in d_positions.iteritems():
            md_handles[k].p_position = p
            
            
        #md_handles['inner'].p_position = d_positions['inner']
        #md_handles['outer'].p_position = d_positions['outer']
        #md_handles['upr'].p_position = d_positions['upr']
        #md_handles['lwr'].p_position = d_positions['lwr']
        
        """
        _crvUpr = CORERIG.create_at(create='curve',l_pos = [d_positions['inner'],
                                                            d_positions['upr'],
                                                            d_positions['outer']])
        
        _crvLwr = CORERIG.create_at(create='curve',l_pos = [d_positions['inner'],
                                                            d_positions['lwr'],
                                                            d_positions['outer']])"""
        
        d_curveCreation = {'lidUpr':{'keys':['inner','upr','outer'],
                                   'rebuild':False},
                           'lidUprOutr':{'keys':['innerEnd','uprEnd','outerEnd'],
                                     'rebuild':False},
                           'lidLwr':{'keys':['inner','lwr','outer'],
                                   'rebuild':False},
                           'lidLwrOutr':{'keys':['innerEnd','lwrEnd','outerEnd'],
                                     'rebuild':False},                   
                           
                            }
        
        md_resCurves = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mNoTransformNull)
        self.msgList_connect('defineCurves',md_resCurves['ml_curves'])#Connect
        self.msgList_connect('defineSubHandles',ml_handlesSub)#Connect
        
        self.msgList_connect('defineHandles',ml_handles + ml_handlesSub)#Connect
        
        _size_depthHelper = _size_base/8
        
            
        for tag,mHandle in md_handles.iteritems():
            #print DIST.get_closest_point(mHandle.mNode, mBBShape.mNode,True)
            mHandle.doConnectIn('scaleX',"{0}.jointRadius".format( _short))
            mHandle.doConnectIn('scaleY',"{0}.jointRadius".format( _short))
            mHandle.doConnectIn('scaleZ',"{0}.jointRadius".format( _short))
            
            ATTR.set_lock(mHandle.mNode,'scale',True)
            
            if 'End' not in tag:
                #Lid Depth Vis....
                _depthHelp = CURVES.create_fromName('cylinder', size = [_size_depthHelper,_size_depthHelper,1])
                #mShape = cgmMeta.validateObjArg(_depthHelp)
                #mShape.doSnapTo(mHandle.mNode)
                
                CORERIG.shapeParent_in_place(mHandle.mNode,_depthHelp,False,True,True)
                self.doConnectOut('lidDepth', "{0}.scaleZ".format(mHandle.mNode))
                
                #mShape.p_parent = mDefineNull
                """
                
                mGroup = mShape.doGroup(True,True,asMeta=True,
                                        typeModifier = 'driven',
                                        setClass='cgmObject')
                mc.pointConstraint(mHandle.mNode, mGroup.mNode,maintainOffset = False)"""
                """
                mc.aimConstraint(mMidDriver.mNode, mHandle.mNode, maintainOffset = False,
                                 aimVector = [0,0,-1], upVector = [0,1,0], 
                                 worldUpObject = self.mNode,
                                 worldUpType = 'objectrotation', 
                                 worldUpVector = [0,1,0])"""
                SNAP.aim_atPoint(mHandle.mNode,mMidDriver.p_position,'z-',mode='vector', vectorUp=self.getAxisVector('y+'))
                ATTR.set_standardFlags(mHandle.mNode,['sz'])
            #else:
                #for a in 'sx','sy','sz':
                    #self.doConnectOut('lidDepth', "{0}.{1}".format(mHandle.mNode,a))
                    #ATTR.set_standardFlags(mHandle.mNode,[a])
                    
            elif cgmGEN.__mayaVersion__ >= 2018:
                mController = mHandle.controller_get()
                
                try:
                    ATTR.connect("{0}.visProximityMode".format(self.mNode),
                             "{0}.visibilityMode".format(mController.mNode))    
                except Exception,err:
                    log.error(err)

                self.msgList_append('defineStuff',mController)                
        
            if 'End' not in tag:
                mHandle.p_position = DIST.get_closest_point(mHandle.mNode, mBBShape.mNode)[0]
    
    #_dat = self.baseDat
    #self.baseSize = _dat['baseSize']
 


#=============================================================================================================
#>> Form
#=============================================================================================================
def formDelete(self):
    _str_func = 'formDelete'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    ml_defSubHandles = self.msgList_get('defineSubHandles')
    for mObj in ml_defSubHandles:
        mObj.template = False    
        mObj.v=1
        
    for mObj in self.msgList_get('defineCurves'):
        mObj.template=0
        mObj.v=1
        
    """
    for k in ['end','rp','up','aim']:
        mHandle = self.getMessageAsMeta("define{0}Helper".format(k.capitalize()))
        if mHandle:
            l_const = mHandle.getConstraintsTo()
            if l_const:
                log.debug("currentConstraints...")
                pos = mHandle.p_position
                
                for i,c in enumerate(l_const):
                    log.debug("    {0} : {1}".format(i,c))
                mc.delete(l_const)
                mHandle.p_position = pos
                
            mHandle.v = True
            mHandle.template = False
            
        mHandle = self.getMessageAsMeta("vector{0}Helper".format(k.capitalize()))
        if mHandle:
            mHandle.template=False"""
            
    try:self.defineLoftMesh.template = False
    except:pass
    self.bbHelper.v = True
    
@cgmGEN.Timer
def form(self):
    try:    
        _str_func = 'form'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        _short = self.p_nameShort
        _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
        
        #Initial checks ===============================================================================
        log.debug("|{0}| >> Initial checks...".format(_str_func)+ '-'*40)    
        _side = self.UTILS.get_side(self)
        _eyeType = self.getEnumValueString('eyeType')
                
        #if _eyeType not in ['sphere']:
        #    return log.error("|{0}| >> loft setup mode not done: {1}".format(_str_func,_loftSetup))
        
        #Create temple Null  ==================================================================================
        mFormNull = BLOCKUTILS.formNull_verify(self)    
        mHandleFactory = self.asHandleFactory()
        mNoTransformNull = self.atUtils('noTransformNull_verify','form')
        mTrackSurface = self.trackSurface
        
        #Meat ==============================================================================================
        if self.lidBuild:
            log.debug("|{0}| >> Lid setup...".format(_str_func)+ '-'*40)
            
            
            #Gather all our define dhandles and curves -----------------------------
            log.debug("|{0}| >> Get our define curves/handles...".format(_str_func)+ '-'*40)    
    
            md_handles = {}
            md_dCurves = {}
            d_defPos = {}


            ml_defineHandles = self.msgList_get('defineSubHandles')
            for mObj in ml_defineHandles:
                md_handles[mObj.handleTag] = mObj
                d_defPos[mObj.handleTag] = mObj.p_position
                mObj.v=0
                
            for mObj in self.msgList_get('defineCurves'):
                md_dCurves[mObj.handleTag] = mObj
                mObj.template=1
                mObj.v=0
            
            #
            d_pairs = {}
            d_creation = {}
            l_order = []
            d_curveCreation = {}
            ml_subHandles = []
            md_loftCreation = {}
            
            DGETAVG = DIST.get_average_position
            CRVPCT = CURVES.getPercentPointOnCurve
            
            log.debug("|{0}| >>  Need some special positions".format(_str_func))

            mVec = self.getAxisVector('z+')

            _offset = self.lidDepth#DIST.get_distance_between_points(d_defPos['inner'],d_defPos['upr']) * .25
            _size = self.atUtils('defineSize_get') / 8
            
            for tag in 'upr','lwr','outer','inner':
                d_defPos[tag+'Line'] = DIST.get_pos_by_vec_dist(d_defPos[tag],mVec,_offset)
                
                
            pEdgeInner = DGETAVG([d_defPos['innerLine'],d_defPos['innerEnd']])
            pEdgeOuter = DGETAVG([d_defPos['outerLine'],d_defPos['outerEnd']])
            pEdgeUpr = DGETAVG([d_defPos['uprLine'],d_defPos['uprEnd']])
            pEdgeLwr = DGETAVG([d_defPos['lwrLine'],d_defPos['lwrEnd']])
            
            d_defPos['innerEdge'] = pEdgeInner
            d_defPos['outerEdge'] = pEdgeOuter
            d_defPos['uprEdge'] = pEdgeUpr
            d_defPos['lwrEdge'] = pEdgeLwr
            
            
            log.debug("|{0}| >>  Lid setup...".format(_str_func))
            
            _d_toDo = {'upr':{'count':self.numLidUprShapers,
                              },
                       'lwr':{'count':self.numLidLwrShapers}}
            
            _d_posToSplit = {'upr':{'contact':['inner','upr','outer'],
                                    'line':['innerLine','uprLine','outerLine'],
                                    'edge':['innerEdge','uprEdge','outerEdge'],
                                    'orb':['innerEnd','uprEnd','outerEnd']},
                             'lwr':{'contact':['inner','lwr','outer'],
                                    'line':['innerLine','lwrLine','outerLine'],
                                    'edge':['innerEdge','lwrEdge','outerEdge'],
                                    'orb':['innerEnd','lwrEnd','outerEnd']}
                             }
            
            _d_pos = {}
            d_curveKeys = {}
            l_tags = ['upr','lwr']
            
            for tag in l_tags:
                d = _d_toDo[tag]
                d_curveKeys[tag] = {}
                for ii, crvToDo in enumerate(['contact','line','edge','orb']):
                    _tag = tag + STR.capFirst(crvToDo)
                    _cnt = d['count']
                    l_keys = _d_posToSplit[tag][crvToDo]
                    
                    #GEt main positions
                    l_pos = []
                    for t in l_keys:
                        l_pos.append(d_defPos[t])
                        
                        
                    #Get percentage list
                    l_v = MATH.get_splitValueList(points = _cnt)
                    
                    _crv = CORERIG.create_at(create='curve',l_pos= l_pos)
                    
                    if crvToDo in ['contact','line']:
                        _crvShape = TRANS.shapes_get(_crv)[0]
                        
                        _crv = mc.rebuildCurve(_crv,rpo=True,ch=1, spans=10)
                        _l_source = mc.ls("{0}.{1}[*]".format(_crvShape,'ep'),flatten=True,long=True)
                        
                        for ii,cv in enumerate(_l_source):
                            if crvToDo == 'contact':
                                pClose = DIST.get_closest_point(cv, mTrackSurface.mNode)[0]
                                POS.set(cv,pClose)
                                #LOC.create(position=pClose,name='contact_{0}'.format(ii))
                            else:
                                pMe = POS.get(cv)
                                datClose = DIST.get_closest_point_data(mTrackSurface.mNode, targetPoint=pMe)
                                pClose = datClose['position']
                                #_vec = MATH.get_vector_of_two_points(pSurf,pMe)
                                pprint.pprint(datClose)
                                newPos = DIST.get_pos_by_vec_dist(pClose,datClose['normalizedNormal'],_offset)
                                POS.set(cv,newPos)
                                
                            """
                            if offsetMode == 'fixed':
                                set_vectorOffset(c,_origin,distance,vector,mode=mode)
                            else:
                                pMe = POS.get(c)
                                _vec = MATHUTILS.get_vector_of_two_points(_origin,pMe)
                                d = get_distance_between_points(_origin,pMe)
                                newPos = get_pos_by_vec_dist(POS.get(c),_vec,d*factor)
                                POS.set(c,newPos) """                       

                    
                    
                    
                    l_keys = []
                    for i,v in enumerate(l_v):
                        _key = "{0}_{1}".format(_tag,i)
                        if tag != 'upr':
                            if v == l_v[0] or v == l_v[-1]:
                                continue
                        l_keys.append(_key)
                        
                        #Generate handle dat...
                        l_order.append(_key)
                        p = CRVPCT(_crv,v)

                                
                        _d_pos[_key] = p
                        d_creation[_key] = {'color':'yellowWhite','tagOnly':True,'arrow':False,'jointLabel':0,
                                            'vectorLine':False,'pos':p}
                    d_curveKeys[tag][crvToDo] = l_keys
                        
                    if tag != 'upr':
                        l_keys.insert(0,d_curveKeys['upr'][crvToDo] [0])
                        l_keys.append(d_curveKeys['upr'][crvToDo] [-1])
                    d_curveCreation[_tag] = {'keys':l_keys,
                                             'rebuild':1}
                    mc.delete(_crv)


            #LoftDeclarations....
            md_loftCreation['uprLid'] = {'keys':['uprContact','uprLine','uprEdge','uprOrb'],
                                         'rebuild':{'spansU':5,'spansV':5},
                                         'kws':{'noRebuild':1}}
            md_loftCreation['lwrLid'] = {'keys':['lwrContact','lwrLine','lwrEdge','lwrOrb'],
                                         'rebuild':{'spansU':5,'spansV':5},
                                         'kws':{'noRebuild':1}}
            md_loftCreation['uprLid']['keys'].reverse()
            
            md_loftCreation['attachLids'] = {'keys':md_loftCreation['uprLid']['keys'][:-1] + md_loftCreation['lwrLid']['keys'][1:],
                                             'rebuild':{'spansU':5,'spansV':5,
                                                        'rebuildType':1},
                                         'kws':{'noRebuild':1}
                                             }

            md_res = self.UTILS.create_defineHandles(self, l_order, d_creation, _size, 
                                                     mFormNull,statePlug = 'form')
            
            ml_subHandles.extend(md_res['ml_handles'])
            md_handles.update(md_res['md_handles'])
            
            
            #Setting up contact line tracking...
            for tag in l_tags:
                for i,key in enumerate(d_curveKeys[tag]['contact']):
                    mHandle = md_handles[key]
                    _trackKey = d_curveKeys[tag]['line'][i]
                    
                    

                    mHandle.p_position = DIST.get_closest_point(md_handles[_trackKey].mNode,
                                                                mTrackSurface.mNode)[0]
                    
                    
                    mTrackGroup = mHandle.doGroup(True,True,asMeta=True,
                                                  typeModifier = 'track',
                                                  setClass='cgmObject')                    
                    
                    _res = RIGCONSTRAINT.attach_toShape(mTrackGroup.mNode,mTrackSurface.mNode,
                                                        'conPoint',driver= md_handles[_trackKey])
                    md = _res[-1]
                    mFollicle = md['mFollicle']
                    for k in ['mDriverLoc','mFollicle']:
                        md[k].p_parent = mNoTransformNull
                        md[k].v = False
                        
                """
                for i,key in enumerate(d_curveKeys[tag]['edge']):
                    if key in [d_curveKeys[tag]['edge'][0],d_curveKeys[tag]['edge'][-1]] and tag == 'lwr':
                        continue
                    
                    mHandle = md_handles[key]
                    #pos  = DIST.get_closest_point(mHandle.mNode, mTrackSurface.mNode)[0]
                    pos = DIST.get_pos_by_vec_dist(mHandle.p_position,mVec,-_offset)
                    mHandle.p_position = pos
                    """
            
        
                
            md_res = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mNoTransformNull,'formCurve')
            md_resCurves = md_res['md_curves']
            
            for k,d in md_loftCreation.iteritems():
                ml_curves = [md_resCurves[k2] for k2 in d['keys']]
                for mObj in ml_curves:
                    mObj.v=False
                    
                _d = d.get('kws',{})
                if _side == 'left':
                    _d['noReverse'] = True
                
                mLoft = self.UTILS.create_simpleFormLoftMesh(self,
                                                             [mObj.mNode for mObj in ml_curves],
                                                             mFormNull,
                                                             polyType = 'faceLoft',
                                                             d_rebuild = d.get('rebuild',{}),
                                                             baseName = k,
                                                             transparent = False,
                                                             vDriver = "{0}.numLidSplit_v".format(_short),
                                                             uDriver = "{0}.numLidSplit_u".format(_short),
                                                             **d.get('kws',{}))
                if 'attach' in k:
                    mLoft.template =1
        
            
            
            for tag,mHandle in md_handles.iteritems():
                if cgmGEN.__mayaVersion__ >= 2018:
                    mController = mHandle.controller_get()
                    
                    try:
                        ATTR.connect("{0}.visProximityMode".format(self.mNode),
                                 "{0}.visibilityMode".format(mController.mNode))    
                    except Exception,err:
                        log.error(err)
    
                    self.msgList_append('formStuff',mController)                       
                    
                #Depth setup
                #_depthHelp = CURVES.create_fromName('cylinder', size = [_size,_size,1])
                #mShape = cgmMeta.validateObjArg(_depthHelp)
                #mShape.doSnapTo(mHandle.mNode)
                
                #CORERIG.shapeParent_in_place(mHandle.mNode,_depthHelp,False,True,True)
                #self.doConnectOut('lidDepth', "{0}.scaleZ".format(mHandle.mNode))
                
                #SNAP.aim_atPoint(mHandle.mNode,mEdgeDriver.p_position,'z-',mode='vector', vectorUp=self.getAxisVector('y+'))
                #ATTR.set_standardFlags(mHandle.mNode,['sz'])
            """       
    
            #Mirror indexing -------------------------------------
            log.debug("|{0}| >> Mirror Indexing...".format(_str_func)+'-'*40) 
            
            idx_ctr = 0
            idx_side = 0
            d = {}
            
            for tag,mHandle in md_handles.iteritems():
                if mHandle in ml_defineHandles:
                    continue
                
                mHandle._verifyMirrorable()
                _center = True
                for p1,p2 in d_pairs.iteritems():
                    if p1 == tag or p2 == tag:
                        _center = False
                        break
                if _center:
                    log.debug("|{0}| >>  Center: {1}".format(_str_func,tag))    
                    mHandle.mirrorSide = 0
                    mHandle.mirrorIndex = idx_ctr
                    idx_ctr +=1
                mHandle.mirrorAxis = "translateX,rotateY,rotateZ"
        
            #Self mirror wiring -------------------------------------------------------
            for k,m in d_pairs.iteritems():
                try:
                    md_handles[k].mirrorSide = 1
                    md_handles[m].mirrorSide = 2
                    md_handles[k].mirrorIndex = idx_side
                    md_handles[m].mirrorIndex = idx_side
                    md_handles[k].doStore('mirrorHandle',md_handles[m])
                    md_handles[m].doStore('mirrorHandle',md_handles[k])
                    idx_side +=1        
                except Exception,err:
                    log.error('Mirror error: {0}'.format(err))
            """
                
        
            self.msgList_connect('formHandles',ml_subHandles)#Connect
            self.msgList_connect('formCurves',md_res['ml_curves'])#Connect        
            return            
            
            
        

        """
        ml_defSubHandles = self.msgList_get('defineSubHandles')
        for mObj in ml_defSubHandles:
            mObj.template = True
            
        l_tags = ['upr','lwr','inner','outer',
                  'uprEnd','lwrEnd','innerEnd','outerEnd']
        md_handles = {}
        d_pos = {}
        for tag in l_tags:
            md_handles[tag] = self.getMessageAsMeta("define{0}Helper".format(STR.capFirst(tag)))
            d_pos[tag] = md_handles[tag].p_position
            
        
        #Build our curves =======================================================================
        #For this first pass we're just doing simple curve, will loop back when we do full lids
        log.debug("|{0}| >> Lid cuves...".format(_str_func)+ '-'*40)
        
        md_loftCurves = {}
        d_loftCurves = {'upr':[d_pos['inner'],
                               d_pos['upr'],
                               d_pos['outer']],
                        'lwr':[d_pos['inner'],
                               d_pos['lwr'],
                               d_pos['outer']],
                        'uprEnd':[d_pos['innerEnd'],
                                  d_pos['uprEnd'],
                                  d_pos['outerEnd']],
                        'lwrEnd':[d_pos['innerEnd'],
                                  d_pos['lwrEnd'],
                                  d_pos['outerEnd']]}


        for tag,l_pos in d_loftCurves.iteritems():
            _crv = CORERIG.create_at(create='curve',l_pos = l_pos)
            mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
            mCrv.p_parent = mFormNull
            mHandleFactory.color(mCrv.mNode)
            
            mCrv.rename('{0}_loftCurve'.format(tag))
            
            self.connectChildNode(mCrv, tag+'LidLoftCurve','block')
            md_loftCurves[tag]=mCrv
            
        self.UTILS.create_simpleFormLoftMesh(self,
                                                 [md_loftCurves['upr'].mNode,
                                                  md_loftCurves['uprEnd'].mNode],
                                                 mFormNull,
                                                 polyType = 'bezier',
                                                 baseName = 'uprLid')
        self.UTILS.create_simpleFormLoftMesh(self,
                                                 [md_loftCurves['lwr'].mNode,
                                                  md_loftCurves['lwrEnd'].mNode],
                                                 mFormNull,
                                                 polyType = 'bezier',
                                                 baseName = 'lwrLid')    
        
        log.debug(self.uprLidFormLoft)
        log.debug(self.lwrLidFormLoft)
        log.debug(self.uprLidLoftCurve)
        log.debug(self.lwrLidLoftCurve)"""
    
        
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerigDelete(self):
    try:self.moduleEyelid.delete()
    except:pass
    
def prerig(self):
    try:
        _str_func = 'prerig'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        self.blockState = 'prerig'
        _side = self.UTILS.get_side(self)
        
        self.atUtils('module_verify')
        mStateNull = self.UTILS.stateNull_verify(self,'prerig')
        mNoTransformNull = self.atUtils('noTransformNull_verify','prerig')
        
        #mRoot = self.getMessageAsMeta('rootHelper')
        mHandleFactory = self.asHandleFactory()
        mHandleFactory.setHandle(self)
        
        ml_handles = []
        md_crvDrivers = {}
        
        #Get base dat =============================================================================    
        _mVectorAim = MATH.get_obj_vector(self.mNode,asEuclid=True)
        mBBHelper = self.bbHelper
        _v_range = max(TRANS.bbSize_get(self.mNode)) *2
        _bb_axisBox = SNAPCALLS.get_axisBox_size(mBBHelper.mNode, _v_range, mark=False)
        _size_width = _bb_axisBox[0]#...x width
        
        if self.lidBuild:
            _size_base = _size_width * .25
            _size_sub = _size_base * .2            
        else:
            _size_base = _size_width * .25
            _size_sub = _size_base * .2
        
        _pos_bbCenter = POS.get_bb_center(mBBHelper.mNode)
    
        log.debug("{0} >> axisBox size: {1}".format(_str_func,_bb_axisBox))
        log.debug("{0} >> Center: {1}".format(_str_func,_pos_bbCenter))
    
        #for i,p in enumerate(_l_basePos):
            #LOC.create(position=p,name="{0}_loc".format(i))
    
    
    
        #mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self,'form') 
        mIrisPos = self.getMessageAsMeta('irisPosHelper')
        #mPupilPos = self.getMessageAsMeta('irisPosHelper')
        d_baseHandeKWS = {'mStateNull' : mStateNull,
                          'mNoTransformNull' : mNoTransformNull,
                          'jointSize': self.jointRadius}
        

    
        #Create Pivot =====================================================================================
        #loc = LOC.create(position=_pos_bbCenter,name="bbCenter_loc")
        #TRANS.parent_set(loc,mFormNull)
    
        crv = CURVES.create_fromName('sphere', size = _size_base)
        mHandleRoot = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
        mHandleFactory.color(mHandleRoot.mNode)
        
        mHandleRoot.doSnapTo(self)

        #_shortHandle = mHandleRoot.mNode
    
        #ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
        mHandleRoot.doStore('cgmName','eyeRoot')    
        mHandleRoot.doStore('cgmType','formHandle')
        mHandleRoot.doName()
    
        mHandleRoot.p_position = _pos_bbCenter
        mHandleRoot.p_parent = mStateNull
        mHandleRoot.doGroup(True,True,asMeta=True,typeModifier = 'center')
    
        self.connectChildNode(mHandleRoot.mNode,'rootHelper','module')
        
        #Iris/pupil helper =====================================================================================
        d_pupilIris = {'pupil':self.pupilBuild,
                       'iris':self.irisBuild}
        md_handles = {}
        md_shapes = {}
        reload(BLOCKSHAPES)
        for k,v in d_pupilIris.iteritems():
            if not v:
                continue
            
            log.debug("|{0}| >> {1} setup...".format(_str_func,k)+ '-'*40)
            
            _tag = k
            #------------------------------------------------------------
        
            _d_name = {'cgmName':_tag,
                       'cgmType':'jointHelper'}
        
            _d_kws = copy.copy(d_baseHandeKWS)
            _size_use = copy.copy(_size_sub)
            if k == 'iris':
                _size_use = _size_use * 2.0
                
            mShape, mDag = BLOCKSHAPES.create_face_handle(self,
                                                          self.p_position,
                                                          _tag ,None, 'center',
                                                          mDriver = mIrisPos,
                                                          mSurface = mBBHelper,#mLidLoft,
                                                          mAttachCrv = None,
                                                          mainShape='semiSphere',
                                                          #jointShape='sphere',
                                                          size= _size_sub,
                                                          mode='joint',
                                                          depthAttr= 'irisDepth',
                                                          offsetAttr='conDirectOffset',
                                                          controlType='sub',
                                                          plugDag= 'jointHelper',
                                                          plugShape= 'directShape',
                                                          attachToSurf=True,
                                                          #orientToDriver=True,
                                                          shapeToSurf=True,
                                                          nameDict= _d_name,
                                                          **d_baseHandeKWS)
            
            
            _bbSize = TRANS.bbSize_get(self.getMessageAsMeta('{0}Helper'.format(k)).mNode, True, 'max')
            TRANS.scaleLocal_set(mShape.mNode,_bbSize)
            mShape.sz = _bbSize * .5
            
            md_handles[k] = mDag
            md_shapes[k] = mShape
            
            #mShape.p_parent = mStateNull
            ml_handles.append(mShape)        
        
        #Orient helper =====================================================================================
        _orientHelper = CURVES.create_fromName('arrowSingle', size = _size_base)
        mShape = cgmMeta.validateObjArg(_orientHelper)
    
        mShape.doSnapTo(self.mNode)
        mShape.p_parent = self
    
        mShape.tz = DIST.get_distance_between_points(self.p_position,mIrisPos.p_position) - (_size_base)
        mShape.rz = 90
                
        
        _crvLinear = CORERIG.create_at(create='curveLinear',
                                       l_pos=[self.p_position,mShape.p_position])
        
        mShape.p_parent = mHandleRoot
        
        mOrientHelper = mHandleRoot.doCreateAt(setClass=True)
        CORERIG.shapeParent_in_place(mOrientHelper.mNode, mShape.mNode,False)
        CORERIG.shapeParent_in_place(mOrientHelper.mNode, _crvLinear,False)
        
        mOrientHelper.p_parent = mHandleRoot
    
        mOrientHelper.doStore('cgmName','eyeOrient')
        mOrientHelper.doStore('cgmType','formHandle')
        mOrientHelper.doName()
        
        self.connectChildNode(mOrientHelper.mNode,'eyeOrientHelper','module')
        mHandleFactory.color(mOrientHelper.mNode,controlType='sub')
        
        ml_handles.append(mOrientHelper)
        
        for k in ['pupil','iris']:
            if md_shapes.get(k):
                mOrientHelper.p_parent = md_shapes[k].p_parent
                break
        
        mAimGroup = mOrientHelper.doGroup(True,True,asMeta=True,typeModifier = 'aim',setClass='cgmObject')
        
        mc.aimConstraint(mIrisPos.mNode, mAimGroup.mNode, maintainOffset = False,
                         aimVector = [0,0,1], upVector = [0,1,0], 
                         worldUpObject = self.mNode,
                         worldUpType = 'objectrotation', 
                         worldUpVector = [0,1,0])
        
        if self.buildEyeOrb:
            pass
            """
                log.debug("|{0}| >> Eye orb setup...".format(_str_func))
    
                crv = CURVES.create_fromName('circle', size = [self.baseSizeX, self.baseSizeY, None])
                mHandleOrb = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
                mHandleFactory.color(mHandleOrb.mNode)
    
                #_shortHandle = mHandleRoot.mNode
                mHandleOrb.doSnapTo(self.mNode)
                mHandleOrb.p_parent = mStateNull
    
                #ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
                mHandleOrb.doStore('cgmName','eyeOrb')    
                mHandleOrb.doStore('cgmType','formHandle')
                mHandleOrb.doName()
    
                self.connectChildNode(mHandleOrb.mNode,'eyeOrbHelper','module')"""
    
        
        
        #Settings shape --------------------
        if self.ikSetup or self.buildEyeOrb:
            log.debug("|{0}| >> Settings/Orb setup ... ".format(_str_func)) 
            
            _size_bb = mHandleFactory.get_axisBox_size(self.getMessage('bbHelper'))
            _size = MATH.average(_size_bb)
            
            mSettingsShape = cgmMeta.validateObjArg(CURVES.create_fromName('gear',_size_base,
                                                                           'z+'),'cgmObject',setClass=True)
            
            mSettingsShape.doSnapTo(mHandleRoot.mNode)
            
            d_directions = {'left':'x+','right':'x-','center':'z+'}
            str_settingsDirections = d_directions.get(_side,'z+')
            
            mSettingsShape.p_position = self.getPositionByAxisDistance(str_settingsDirections,
                                                                        _size_bb[1] * .7)
            
            mSettingsShape.p_parent = mStateNull
            
            mSettingsShape.doStore('cgmName','settingsShape')
            mSettingsShape.doStore('cgmType','prerigHandle')
            mSettingsShape.doName()
            
            self.connectChildNode(mSettingsShape.mNode,'settingsHelper','block')
            mHandleFactory.color(mSettingsShape.mNode,controlType='sub')
            
            ml_handles.append(mSettingsShape)
        
        
              
        
        if self.lidBuild:
            def create_lidHandle(self,tag,pos,mJointTrack=None,trackAttr=None,visualConnection=True,controlShape='circle',shapeDirection='z+',multiplier=1):
                mHandle = cgmMeta.validateObjArg( CURVES.create_fromName(controlShape, size = _size_sub * multiplier,direction=shapeDirection), 
                                                  'cgmObject',setClass=1)
                mHandle.doSnapTo(self)
                
                
                vec = MATH.get_vector_of_two_points(mOrientHelper.p_position, pos)
                posResult = DIST.get_pos_by_vec_dist(pos,vec,self.lidDepth * 1.25)
                
                mHandle.p_position = posResult
                
                mHandle.p_parent = mStateNull
                mHandle.doStore('cgmName',tag)
                mHandle.doStore('cgmType','formHandle')
                mHandle.doName()
                
                mHandleFactory.color(mHandle.mNode,controlType='sub')
                
                self.connectChildNode(mHandle.mNode,'{0}LidHandle'.format(tag),'block')
                
                
                #joinHandle ------------------------------------------------
                mJointHandle = cgmMeta.validateObjArg( CURVES.create_fromName('jack',
                                                                              size = _size_sub*.75),
                                                       'cgmObject',
                                                       setClass=1)
                
                mJointHandle.doStore('cgmName',tag)    
                mJointHandle.doStore('cgmType','jointHelper')
                mJointHandle.doName()                
                
                mJointHandle.p_position = pos
                mJointHandle.p_parent = mStateNull
                
                
                mHandleFactory.color(mJointHandle.mNode,controlType='sub')
                mHandleFactory.addJointLabel(mJointHandle,tag)
                mHandle.connectChildNode(mJointHandle.mNode,'jointHelper','handle')
                
                mTrackGroup = mJointHandle.doGroup(True,True,
                                                   asMeta=True,
                                                   typeModifier = 'track',
                                                   setClass='cgmObject')
                
                if trackAttr and mJointTrack:
                    mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mJointTrack.mNode,turnOnPercentage=True))
                    
                    mPointOnCurve.doConnectIn('parameter',"{0}.{1}".format(self.mNode,trackAttr))
                    
                    mTrackLoc = mJointHandle.doLoc()
                    
                    mPointOnCurve.doConnectOut('position',"{0}.translate".format(mTrackLoc.mNode))
       
                    mTrackLoc.p_parent = mNoTransformNull
                    mTrackLoc.v=False
                    mc.pointConstraint(mTrackLoc.mNode,mTrackGroup.mNode)                    
                    
                    
                elif mJointTrack:
                    mLoc = mHandle.doLoc()
                    mLoc.v=False
                    mLoc.p_parent = mNoTransformNull
                    mc.pointConstraint(mHandle.mNode,mLoc.mNode)
                    
                    res = DIST.create_closest_point_node(mLoc.mNode,mJointTrack.mNode,True)
                    #mLoc = cgmMeta.asMeta(res[0])
                    mTrackLoc = cgmMeta.asMeta(res[0])
                    mTrackLoc.p_parent = mNoTransformNull
                    mTrackLoc.v=False
                    mc.pointConstraint(mTrackLoc.mNode,mTrackGroup.mNode)
                    
                    
                mAimGroup = mJointHandle.doGroup(True,True,
                                                 asMeta=True,
                                                 typeModifier = 'aim',
                                                 setClass='cgmObject')
                mc.aimConstraint(mLidRoot.mNode,
                                 mAimGroup.mNode,
                                 maintainOffset = False, weight = 1,
                                 aimVector = [0,0,-1],
                                 upVector = [0,1,0],
                                 worldUpVector = [0,1,0],
                                 worldUpObject = self.mNode,
                                 worldUpType = 'objectRotation' )                          
                    
                
                if visualConnection:
                    log.debug("|{0}| >> visualConnection ".format(_str_func, tag))
                    trackcrv,clusters = CORERIG.create_at([mLidRoot.mNode,
                                                           mJointHandle.mNode],#ml_handleJoints[1]],
                                                          'linearTrack',
                                                          baseName = '{0}_midTrack'.format(tag))
                
                    mTrackCrv = cgmMeta.asMeta(trackcrv)
                    mTrackCrv.p_parent = mNoTransformNull
                    mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')
                
                    for s in mTrackCrv.getShapes(asMeta=True):
                        s.overrideEnabled = 1
                        s.overrideDisplayType = 2
                
                return mHandle
                
            log.debug("|{0}| >> Lid setup...".format(_str_func)+ '-'*40)
            _lidBuild = self.getEnumValueString('lidBuild')
            mUprLid = self.getMessageAsMeta('uprContactFormCurve')
            mLwrLid = self.getMessageAsMeta('lwrContactFormCurve')
            
            log.debug("|{0}| >> EyeLid setup: {1}.".format(_str_func,_lidBuild))
            
            mModule_lids = self.atUtils('module_verify','eyelid','moduleEyelid')
            
            #Lid Root ---------------------------------------------------------
            crv = CURVES.create_fromName('jack', size = _size_sub)
            mLidRoot = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
            mHandleFactory.color(mLidRoot.mNode)
        
            #_shortHandle = mHandleRoot.mNode
        
            #ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
            mLidRoot.doStore('cgmName','lidRoot')    
            mLidRoot.doStore('cgmType','formHandle')
            mLidRoot.doName()
        
            mLidRoot.p_position = _pos_bbCenter
            mLidRoot.p_parent = mStateNull
            mLidRoot.doGroup(True,True,asMeta=True,typeModifier = 'center')
            
            mHandleFactory.addJointLabel(mLidRoot,'lidRoot')
            self.connectChildNode(mLidRoot.mNode,'lidRootHelper','block')
            ml_handles.append(mLidRoot)
            
            md_lidHandles = {}
            d_anchorDat = {}
            md_mirrorDat = {'center':[],
                            'left':[],
                            'right':[]}
            
            _d_mirrorKey = {'inner':'left',
                            'outer':'right'}            
            
            d_baseHandeKWS = {'mStateNull' : mStateNull,
                              'mNoTransformNull' : mNoTransformNull,
                              'jointSize': self.jointRadius}
            
            #Lid Handles ----------------------------------------------------------------------------
            _lidFanLwr = self.getEnumValueString('lidFanLwr')
            _lidFanUpr = self.getEnumValueString('lidFanUpr')
            mUprLidEdge = self.getMessageAsMeta('uprEdgeFormCurve')
            mLwrLidEdge = self.getMessageAsMeta('lwrEdgeFormCurve')
            
            if _lidFanUpr == 'single':
                log.debug("|{0}| >> Lid Fan Single...".format(_str_func)+ '-'*40)
                
                mUprFanHandle = create_lidHandle(self,'uprFanCenter',
                                              CURVES.getPercentPointOnCurve(mUprLidEdge.mNode,.5),
                                              mJointTrack=mUprLidEdge,
                                              trackAttr = 'paramMidUpr',
                                              controlShape='circle',
                                              multiplier=1,
                                              )
                
                mLwrFanHandle = create_lidHandle(self,'lwrFanCenter',
                                              CURVES.getPercentPointOnCurve(mLwrLidEdge.mNode,.5),
                                              mJointTrack=mLwrLidEdge,
                                              trackAttr = 'paramMidLwr',
                                              controlShape='circle',
                                              multiplier=1,
                                              )                
                ml_handles.extend([mUprFanHandle,mLwrFanHandle])
            
            
            
            #Lid Handles ----------------------------------------------------------------------------
            if _lidBuild == 'clam':
                d_handles = {'upr':CURVES.getPercentPointOnCurve(mUprLid.mNode,.5),
                             'lwr':CURVES.getPercentPointOnCurve(mLwrLid.mNode,.5)}
                
                mUprHandle = create_lidHandle(self,'upr',
                                              CURVES.getPercentPointOnCurve(mUprLid.mNode,.5),
                                              mJointTrack=mUprLid,
                                              trackAttr = 'paramMidUpr',
                                              controlShape='loftCircleHalfUp',
                                              multiplier=1.5,
                                              )
                
                mLwrHandle = create_lidHandle(self,'lwr',
                                              CURVES.getPercentPointOnCurve(mLwrLid.mNode,.5),
                                              mJointTrack=mLwrLid,                                              
                                              trackAttr = 'paramMidLwr',
                                              controlShape='loftCircleHalfDown',
                                              multiplier=1.5,
                                              )
                
                """
                import cgm.core.lib.locator_utils as LOC
                for tag,p in d_handles.iteritems():
                    mHandle,mJointHandle = create_lidHandle(self,tag,p,jointTrack = )
                    md_lidHandles[tag] = mHandle"""
                    
                ml_handles.extend([mLidRoot,mUprHandle,mLwrHandle])
            else:
                #We need to get our initial positions from split data from the line meet cruve and the peak?
                md_anchors = {}
                
                for tag in ['upr','lwr']:
                    mContact = self.getMessageAsMeta('{0}ContactFormCurve'.format(tag))
                    mLine = self.getMessageAsMeta('{0}LineFormCurve'.format(tag))
                    
                    if tag == 'upr':
                        _v = DIST.get_distance_between_points(CURVES.getMidPoint(mContact.mNode),
                                                                         CURVES.getMidPoint(mLine.mNode))
                        self.lidJointDepth = _v * -.5
                    
                    
                    _res_tmp = mc.loft([mCrv.mNode for mCrv in [mContact,mLine]],
                                       o = True, d = 1, po = 0, c = False,u=False, autoReverse=0,ch=True)
                    str_meshShape = TRANS.shapes_get(_res_tmp[0])[0]
                    
                    l_crvs = SURF.get_surfaceSplitCurves(str_meshShape,count= 1, cullStartEnd=False)
                    _l_split =  CURVES.getUSplitList(l_crvs[0],self.numConLids + 2,rebuild=0)
                    
                    d_split = MATH.get_evenSplitDict(_l_split)
                    d_anchorDat[tag] = {}
                    for t,l in d_split.iteritems():
                        d_anchorDat[tag][t] = l
                        #for i,p in enumerate(l):
                        #    LOC.create(position=p,name="{0}_{1}_{2}".format(tag,t,i))
                            
                    mc.delete(_res_tmp)
                    mc.delete(l_crvs)
                    """
                    mCrv = md_dCurves[tag+'_Peak']
                    #SURF.get_surfaceSplitCurves()
                    _l_split =  CURVES.getUSplitList(mCrv.mNode,self.numConLids + 2,rebuild=1)
                    
                    d_split = MATH.get_evenSplitDict(_l_split)
                    d_anchorDat[tag] = {}
                    for t,l in d_split.iteritems():
                        d_anchorDat[tag][t] = l
                        
                        #for i,p in enumerate(l):
                        #    LOC.create(position=p,name="{0}_{1}_{2}".format(tag,t,i))                
                    """
                
                
                #Lid Anchors....
                _d = {'cgmName':'lid',
                      'cgmType':'preAnchor'}
                
                mLidSurf = self.attachLidsFormLoft#self.bbHelper
                
                for section,sectionDat in d_anchorDat.iteritems():
                    md_anchors[section] = {}
                    
                    _base = 0
                    if section == 'lwr':
                        _base = 1
                    l_tags = ["{0}Lid".format(section)]
                    
                    for side,sideDat in sectionDat.iteritems():
                        if side == 'start':side='inner'
                        elif side =='end':side = 'outer'
                        
                        md_anchors[section][side] = {}
                        md_anchors[section][side]['tags'] = []
                        md_anchors[section][side]['ml'] = []
                        
                        d_tmp = md_anchors[section][side]
                        
                        b_more = False
                        if len(sideDat) > 2:
                            b_more = True
                            
                        if side == 'outer':
                            sideDat.reverse()
                            
                        if section == 'lwr' and len(sideDat)>1:
                            sideDat.pop(0)
                            
                        for i,p in enumerate(sideDat):
                            if side == 'center':
                                tag = ''.join(l_tags)
                            else:
                                if not i and section == 'upr':
                                    tag = 'lidCorner'
                                else:
                                    l_use = copy.copy(l_tags)
                                    if b_more:l_use.append("_{0}".format(i+_base))
                                    tag = ''.join(l_use)
                                
                            #LOC.create(position=p,name=tag)

                            _dUse = copy.copy(_d)
                            _dUse['cgmName'] = tag
                            _dUse['cgmDirection'] = _side
                            _dUse['cgmPosition'] = side
                            #reload(BLOCKSHAPES)
                            mAnchor = BLOCKSHAPES.create_face_anchor(self,p,
                                                                     mLidSurf,
                                                                     tag,
                                                                     None,
                                                                     _side,
                                                                     nameDict=_dUse,
                                                                     mStateNull=mStateNull,
                                                                     size= _size_sub/2)
                            #mAnchor.p_position = p
                            
                            #mAnchor.rotate = 0,0,0
                            d_tmp['tags'].append(tag)
                            d_tmp['ml'].append(mAnchor)
                            ml_handles.append(mAnchor)
                            
                            md_mirrorDat[_d_mirrorKey.get(side,side)].append(mAnchor)#...this will need to map eventually on the mirror call
                            
    
                
                #...get my anchors in lists...-----------------------------------------------------------------
                ml_uprLeft = copy.copy(md_anchors['upr']['inner']['ml'])
                ml_uprRight = md_anchors['upr']['outer']['ml']
                ml_lwrLeft = copy.copy(md_anchors['lwr']['inner']['ml'])
                ml_lwrRight = md_anchors['lwr']['outer']['ml']
                
                ml_uprLeft.reverse()
                ml_lwrLeft.reverse()
                    
                md_anchorsLists = {}
                
                if md_anchors['upr'].get('center'):
                    ml_uprCenter = md_anchors['upr']['center']['ml']
                    ml_lwrCenter = md_anchors['lwr']['center']['ml']
                    
                    md_anchorsLists['upr'] = ml_uprRight + ml_uprCenter + ml_uprLeft
                    md_anchorsLists['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrCenter + ml_lwrLeft + ml_uprLeft[-1:]
                                    
                else:
                    md_anchorsLists['upr'] = ml_uprRight + ml_uprLeft
                    md_anchorsLists['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrLeft + ml_uprLeft[-1:]
                
                #if _side == 'left':
                md_anchorsLists['upr'].reverse()
                md_anchorsLists['lwr'].reverse()
                    
                #...anchor | aim ----------------------------------------------------------------------------
                log.debug(cgmGEN.logString_msg('anchor | aim'))
                
                for tag,sectionDat in md_anchors.iteritems():
                    for side,sideDat in sectionDat.iteritems():
                        if side == 'center':
                            continue
                        
                        if side == 'inner':
                            if _side == 'right':
                                _aim = [-1,0,0]
                            else:
                                _aim = [1,0,0]
                        else:
                            if _side == 'right':
                                _aim = [1,0,0]
                            else:
                                _aim = [-1,0,0]
                                
                        for i,mDriver in enumerate(sideDat['ml']):
                            _mode = None
                            
                            if tag == 'upr' and not i:
                                _mode = 'simple'
    
                            if _mode == 'simple':
                                loc = LOC.create(position = DGETAVG([md_anchors['upr'][side]['ml'][1].p_position,
                                                                     md_anchors['lwr'][side]['ml'][0].p_position]))
                                
                                    
                                mc.delete(mc.aimConstraint(loc,
                                                           mDriver.mNode,
                                                           maintainOffset = False, weight = 1,
                                                           aimVector = _aim,
                                                           upVector = [0,1,0],
                                                           worldUpVector = [0,1,0],
                                                           worldUpObject = self.mNode,
                                                           worldUpType = 'objectRotation'))
                                
                                mc.delete(loc)
                            else:
                                try:_tar=sideDat[i+1].mNode
                                except:_tar=md_anchors[tag]['center']['ml'][0].mNode
    
                                mc.delete(mc.aimConstraint(_tar,
                                                 mDriver.mNode,
                                                 maintainOffset = False, weight = 1,
                                                 aimVector = _aim,
                                                 upVector = [0,1,0],
                                                 worldUpVector = [0,1,0],
                                                 worldUpObject = self.mNode,
                                                 worldUpType = 'objectRotation' ))                
                
                
                #...make our driver curves...---------------------------------------------------------------
                log.debug(cgmGEN.logString_msg('driver curves'))
                d_curveCreation = {}
                for section,sectionDat in md_anchorsLists.iteritems():
                    #for side,dat in sectionDat.iteritems():
                    d_curveCreation[section+'Driver'] = {'ml_handles': sectionDat,
                                                         'rebuild':0}
                    
                    #for i,mObj in enumerate(sectionDat):
                    #    LOC.create(position=mObj.p_position,name=section+'Driver'+'_'+str(i))
                    
                md_res = self.UTILS.create_defineCurve(self, d_curveCreation, {}, mNoTransformNull,'preCurve')
                md_resCurves = md_res['md_curves']
                ml_resCurves = md_res['ml_curves']
                
                
                #Make our Lid handles...-------------------------------------------------------------------------
                log.debug(cgmGEN.logString_sub('Handles'))
                md_prerigDags = {}
                md_jointHelpers = {}
                
                _d = {'cgmName':''}
                
                #...get our driverSetup
                for section,sectionDat in md_anchors.iteritems():
                    log.debug(cgmGEN.logString_sub(section))
                    
                    #md_handles[section] = {}
                    md_prerigDags[section] = {}
                    md_jointHelpers[section] = {}
                    mDriverCrv = md_resCurves[section+'Driver']
                    
                    if section == 'upr':
                        _mainShape = 'loftCircleHalfUp'
                    else:
                        _mainShape = 'loftCircleHalfDown'
                        
                    for side,dat in sectionDat.iteritems():
                        log.debug(cgmGEN.logString_msg(side))
                        
                        
                        #md_handles[section][side] = []
                        md_prerigDags[section][side] = []
                        md_jointHelpers[side] = []
                        
                        _ml_shapes = []
                        _ml_prerigDags = []
                        _ml_jointShapes = []
                        _ml_jointHelpers = []
                        
                        tag = section+'Lid'+STR.capFirst(side)
                        _ml_anchors = dat['ml']
                        
                        #reload(BLOCKSHAPES)
                        if side == 'center':
                            mAnchor = _ml_anchors[0]
                            p = mAnchor.p_position
                            d_use = mAnchor.getNameDict(ignore=['cgmType'])
                            
                            mShape, mDag = BLOCKSHAPES.create_face_handle(self,p,
                                                                          tag,
                                                                          None,
                                                                          _side,
                                                                          mDriver=mAnchor,
                                                                          size= self.lidDepth,
                                                                          
                                                                          mSurface=mLidSurf,#mLidLoft,
                                                                          #mAttachCrv=mDriverCrv,
                                                                          mainShape=_mainShape,
                                                                          jointShape='locatorForm',
                                                                          controlType='main',#_controlType,
                                                                          mode='handle',
                                                                          depthAttr = 'lidJointDepth',
                                                                          plugDag= 'preDag',
                                                                          plugShape= 'preShape',
                                                                          attachToSurf=True,
                                                                          orientToDriver = True,
                                                                          nameDict= d_use,**d_baseHandeKWS)
                            _ml_shapes.append(mShape)
                            _ml_prerigDags.append(mDag)                            
                            
    
                        
                        else:
                            #mCrv = md_resCurves.get(section+'Driver')
                            #if mCrv:
                            for i,mAnchor in enumerate(_ml_anchors):
                                _shapeUse = _mainShape
                                _controlType = 'main'
                                
                                if section == 'upr' and not i:
                                    if side == 'inner':
                                        if _side == 'right':
                                            _shapeUse = 'widePos'
                                        else:
                                            _shapeUse = 'wideNeg'
                                            
                                    else:
                                        if _side == 'right':
                                            _shapeUse = 'wideNeg'
                                        else:
                                            _shapeUse = 'widePos'
                                else:
                                    _controlType = 'sub'
                                    
                                        
                                p = mAnchor.p_position
                                d_use = mAnchor.getNameDict(ignore=['cgmType'])
                                
                                
    
                                mShape, mDag = BLOCKSHAPES.create_face_handle(self,p,
                                                                              tag,
                                                                              None,
                                                                              _side,
                                                                              mDriver=mAnchor,
                                                                              mSurface=mLidSurf,#mLidLoft,
                                                                              #mAttachCrv=mDriverCrv,
                                                                              mainShape=_shapeUse,
                                                                              jointShape='locatorForm',
                                                                              depthAttr = 'lidJointDepth',
                                                                              size= _size_sub,
                                                                              controlType=_controlType,
                                                                              mode='handle',
                                                                              plugDag= 'preDag',
                                                                              plugShape= 'preShape',
                                                                              attachToSurf=True,
                                                                              orientToDriver = True,
                                                                              nameDict= d_use,**d_baseHandeKWS)
                                
    
                                _ml_shapes.append(mShape)
                                _ml_prerigDags.append(mDag)                            
                                
                                
                                
      
                        mStateNull.msgList_connect('{0}PrerigShapes'.format(tag),_ml_shapes)
                        mStateNull.msgList_connect('{0}PrerigHandles'.format(tag),_ml_prerigDags)
                        md_mirrorDat[_d_mirrorKey.get(side,side)].extend(_ml_shapes + _ml_prerigDags)
                        md_prerigDags[section][side] = _ml_prerigDags
                        ml_handles.extend(_ml_shapes + _ml_prerigDags)
                
                
                #...get joint handles...-----------------------------------------------------------------
                ml_uprCenter = md_prerigDags['upr']['center']
                ml_uprLeft = copy.copy(md_prerigDags['upr']['inner'])
                ml_uprLeft.reverse()
                ml_uprRight = md_prerigDags['upr']['outer']
                
                ml_lwrCenter = md_prerigDags['lwr']['center']
                ml_lwrLeft = copy.copy(md_prerigDags['lwr']['inner'])
                ml_lwrLeft.reverse()
                
                ml_lwrRight = md_prerigDags['lwr']['outer']
                
                md_handleCrvDrivers = {}
                
                md_handleCrvDrivers['upr'] = ml_uprRight + ml_uprCenter + ml_uprLeft
                md_handleCrvDrivers['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrCenter + ml_lwrLeft + ml_uprLeft[-1:]
                
                #pprint.pprint(md_anchors)
                #pprint.pprint(d_anchorDat)
                #pprint.pprint(md_crvDrivers)
    
                #...make our driver curves...---------------------------------------------------------------
                log.debug(cgmGEN.logString_msg('driven curves'))
                d_curveCreation = {}
                for section,sectionDat in md_handleCrvDrivers.iteritems():
                    d_curveCreation[section+'Driven'] = {'ml_handles': sectionDat,
                                                         'rebuild':1}
                        
                md_res = self.UTILS.create_defineCurve(self, d_curveCreation, {}, mNoTransformNull,'preCurve')
                md_resCurves.update(md_res['md_curves'])
                ml_resCurves.extend(md_res['ml_curves'])
                
                #Joint handles =============================================================================
                log.debug(cgmGEN.logString_sub('joints'))
                
                d_lidDrivenDat = {}
                d_lidDriverDat = {}
                md_lidDrivers = {}
                
                #...get our spilt data ---------------------------------------------------------------------
                log.debug(cgmGEN.logString_msg('joints | split data'))
                
                for tag in 'upr','lwr':
                    mDriverCrv = md_resCurves[tag+'Driver']
                    mDrivenCrv = md_resCurves[tag+'Driven']
                    #_crv = CORERIG.create_at(create='curveLinear',
                    #                         l_pos=[mObj.p_position for mObj in md_handleCrvDrivers[tag]])
                    
                    _count = self.getMayaAttr('numLid'+tag.capitalize()+'Joints')
                    
                    
                    l_driverPos =  CURVES.getUSplitList(mDriverCrv.mNode,_count + 2,rebuild=0)
                    l_drivenPos = CURVES.getUSplitList(mDrivenCrv.mNode,_count + 2,rebuild=0)
                    
                    l_drivenPos.reverse()
                    l_driverPos.reverse()
                    
                    d_split_driven = MATH.get_evenSplitDict(l_drivenPos)
                    d_split_driver = MATH.get_evenSplitDict(l_driverPos)
                    
                    d_lidDrivenDat[tag] = {}
                    d_lidDriverDat[tag] = {}
                    
                    for t,l in d_split_driven.iteritems():
                        d_lidDrivenDat[tag][t] = l
                        
                        #for i,p in enumerate(l):
                            #LOC.create(position=p,name="{0}_{1}_{2}".format(tag,t,i))                    
                    
                    for t,l in d_split_driver.iteritems():
                        d_lidDriverDat[tag][t] = l
                    
    
                
                _d = {'cgmName':'lid',
                      'cgmType':'preAnchor'}
                
                _sizeDirect = _size_sub * .4
                
                md_lidJoints = {}
                for section,sectionDat in d_lidDrivenDat.iteritems():
                    mDriverCrv = md_resCurves[section+'Driver']
                    mDriverCrv.v = 0
                    
                    mDrivenCrv = md_resCurves[section+'Driven']
                    mDrivenCrv.v = 0
                    
                    md_lidJoints[section] = {}
                    md_lidDrivers[section] = {}
                    
                    #_d['cgmPosition'] = section
                    
                    _base = 0
                    if section == 'lwr':
                        _base = 1
                    
                    
                    for side,sideDat in sectionDat.iteritems():
                        driverDat = d_lidDriverDat[section][side]
                        
                        if side == 'start':side='inner'
                        elif side =='end':side = 'outer'
                        
                        #if side == 'start':side='inner'
                        #elif side =='end':side = 'outer'                        
                        
                        _ml_jointShapes = []
                        _ml_jointHelpers = []
                        _ml_lidDrivers = []
                        
                        md_lidJoints[section][side] = []
                        md_lidDrivers[section][side] = []
                        
                        l_bridge = md_lidJoints[section][side]
                        l_tags = ['{0}Lid'.format(section)]
                        
                        b_more = False
                        if len(sideDat) > 2:
                            b_more = True
                            
                        if side == 'outer':
                            sideDat.reverse()
                            driverDat.reverse()
                            
                        if section == 'lwr' and len(sideDat)>1:
                            sideDat.pop(0)
                            driverDat.pop(0)
                            
                        for i,p_driven in enumerate(sideDat):
                            p_driver = driverDat[i]
                            _dUse = copy.copy(_d)
                            
                            if side == 'center':
                                tag = ''.join(l_tags)
                            else:
                                if not i and section == 'upr':
                                    tag = 'lidCorner'
                                else:
                                    l_use = copy.copy(l_tags)
                                    if b_more:l_use.append("_{0}".format(i+_base))
                                    tag = ''.join(l_use)
                                    
                            log.debug(cgmGEN.logString_msg('tag | {0}'.format(tag)))
    
                            _dUse['cgmName'] = tag#'lid' #+ STR.capFirst(tag)
                            _dUse['cgmDirection'] = _side
                            _dUse['cgmPosition'] = side
                            
                            #Driver ...
                            mDriver = self.doCreateAt(setClass=1)#self.doLoc()#
                            mDriver.rename("{0}_{1}_{2}_{3}_driver".format(section, side,_dUse['cgmName'],i))
                            mDriver.p_position = p_driver
                            mDriver.p_parent = mNoTransformNull#mStateNull
                            
                            _res = RIGCONSTRAINT.attach_toShape(mDriver.mNode,mDriverCrv.mNode,'conPoint')
                            TRANS.parent_set(_res[0], mNoTransformNull.mNode)                        
                            
                            
                            mShape, mDag = BLOCKSHAPES.create_face_handle(self,
                                                                          p_driven,tag,None,_side,
                                                                          mDriver=mDriver,
                                                                          
                                                                          mSurface=mLidSurf,#mLidLoft,
                                                                          mAttachCrv = mDrivenCrv,
                                                                          mainShape='semiSphere',
                                                                          #jointShape='sphere',
                                                                          size= _sizeDirect,
                                                                          mode='joint',
                                                                          depthAttr='lidJointDepth',
                                                                          offsetAttr='conDirectOffset',
                                                                          controlType='sub',
                                                                          plugDag= 'jointHelper',
                                                                          plugShape= 'directShape',
                                                                          attachToSurf=True,
                                                                          #orientToDriver=True,
                                                                          nameDict= _dUse,**d_baseHandeKWS)
                            
                            #md_mirrorDat[side].append(mShape)
                            #md_mirrorDat[side].append(mDag)
                            
                            _ml_jointShapes.append(mShape)
                            _ml_jointHelpers.append(mDag)
                            _ml_lidDrivers.append(mDriver)
    
                        tag = section+'Lid'+STR.capFirst(side)
                        mStateNull.msgList_connect('{0}JointHelpers'.format(tag),_ml_jointHelpers)
                        mStateNull.msgList_connect('{0}JointShapes'.format(tag),_ml_jointShapes)
                        md_jointHelpers[section][side] = _ml_jointHelpers
                        ml_handles.extend(_ml_jointShapes)
                        ml_handles.extend(_ml_jointHelpers)
                        md_mirrorDat[_d_mirrorKey.get(side,side)].extend(_ml_jointShapes + _ml_jointHelpers)
                        md_lidDrivers[section][side] = _ml_lidDrivers
                        
                
                #Aim our lid drivers...------------------------------------------------------------------
                if self.prerigJointOrient:
                    log.debug(cgmGEN.logString_msg('aim lid drivers'))
        
                    for tag,sectionDat in md_lidDrivers.iteritems():
                        for side,sideDat in sectionDat.iteritems():
                            ml_check = md_anchorsLists[tag]
                            l_check = [mObj.mNode for mObj in ml_check]
                            
                            if side == 'outer':
                                if _side == 'right':
                                    _aim = [1,0,0]
                                else:
                                    _aim = [-1,0,0]                            
                            else:
                                if _side == 'right':
                                    _aim = [-1,0,0]
                                else:
                                    _aim = [1,0,0]
                                    
                            for i,mDriver in enumerate(sideDat):
                                _mode = None
                                
                                if tag == 'upr' and not i:
                                    _mode = 'simple'
                                if side == 'center':
                                    _mode = 'simple'
                                    
                                _closest = DIST.get_closestTarget(mDriver.mNode,l_check)
                                    
                                if _mode == 'simple':
                                    mc.orientConstraint(_closest, mDriver.mNode, maintainOffset = False)
                                else:
                                    if mDriver == sideDat[-1]:
                                        _tar = md_lidDrivers[tag]['center'][0].mNode
                                    else:
                                        _tar = sideDat[i+1].mNode
                                        
                                    mc.aimConstraint(_tar,
                                                     mDriver.mNode,
                                                     maintainOffset = False, weight = 1,
                                                     aimVector = _aim,
                                                     upVector = [0,0,1],
                                                     worldUpVector = [0,0,1],
                                                     worldUpObject = _closest,
                                                     worldUpType = 'objectRotation' )
                            
                
                #Driven Curve
                ml_uprCenter = md_jointHelpers['upr']['center']
                ml_uprLeft = copy.copy(md_jointHelpers['upr']['inner'])
                ml_uprLeft.reverse()
                ml_uprRight = md_jointHelpers['upr']['outer']
                
                ml_lwrCenter = md_jointHelpers['lwr']['center']
                ml_lwrLeft = copy.copy(md_jointHelpers['lwr']['inner'])
                ml_lwrLeft.reverse()
                
                ml_lwrRight = md_jointHelpers['lwr']['outer']
                
                md_crvDrivers = {}
                
                md_crvDrivers['upr'] = ml_uprRight + ml_uprCenter + ml_uprLeft
                md_crvDrivers['lwr'] = ml_uprRight[:1] + ml_lwrRight + ml_lwrCenter + ml_lwrLeft + ml_uprLeft[-1:]
                
                #pprint.pprint(md_anchors)
                #pprint.pprint(d_anchorDat)
                #pprint.pprint(md_crvDrivers)
                
                d_driven = {}
                #...make our driver curves...---------------------------------------------------------------
                log.debug(cgmGEN.logString_msg('driven curves'))
                for section,sectionDat in md_crvDrivers.iteritems():
                    #for side,dat in sectionDat.iteritems():
                    d_driven[section+'Result'] = {'ml_handles': sectionDat,
                                                  'rebuild':1}
                    
                        
                        
                md_res = self.UTILS.create_defineCurve(self, d_driven, {}, mNoTransformNull,'preCurve')
                md_resCurves.update(md_res['md_curves'])
                ml_resCurves.extend(md_res['ml_curves'])
                
                #Scale Setup -------------------------------------
                if self.scaleSetup:
                    log.debug(cgmGEN.logString_msg('Scale Pivot'))
                    mScalePivot = mHandleFactory.addScalePivotHelper(self)
                    ml_handles.append(mScalePivot)
                    
                    mScalePivot.p_position = self.midDrivenDag.p_position
                
                #Mirror setup --------------------------------
                log.debug(cgmGEN.logString_sub('mirror'))
                idx_ctr = 0
                idx_side = 0
                
                log.debug(cgmGEN.logString_msg('mirror | center'))
                for mHandle in md_mirrorDat['center']:
                    mHandle = cgmMeta.validateObjArg(mHandle,'cgmControl')
                    mHandle._verifyMirrorable()
                    mHandle.mirrorSide = 0
                    mHandle.mirrorIndex = idx_ctr
                    idx_ctr +=1
                    mHandle.mirrorAxis = "translateX,rotateY,rotateZ"
        
                log.debug(cgmGEN.logString_msg('mirror | sides'))
                    
                for i,mHandle in enumerate(md_mirrorDat['left']):
                    mLeft = cgmMeta.validateObjArg(mHandle,'cgmControl') 
                    mRight = cgmMeta.validateObjArg(md_mirrorDat['right'][i],'cgmControl')
        
                    for mObj in mLeft,mRight:
                        mObj._verifyMirrorable()
                        mObj.mirrorAxis = "translateX,rotateY,rotateZ"
                        mObj.mirrorIndex = idx_side
                    mLeft.mirrorSide = 1
                    mRight.mirrorSide = 2
                    mLeft.doStore('mirrorHandle',mRight)
                    mRight.doStore('mirrorHandle',mLeft)            
                    idx_side +=1                
             
                        
        # Connect -------------------------------------------------
        self.msgList_connect('prerigHandles', ml_handles)
        if md_crvDrivers:
            mStateNull.msgList_connect('uprDrivers', md_crvDrivers['upr'] )
            mStateNull.msgList_connect('lwrDrivers', md_crvDrivers['lwr'] )
        

        
        #Close out ===============================================================================================
        self.blockState = 'prerig'
        
        return
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        
#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def skeleton_check(self):
    return True

def skeleton_build(self, forceNew = True):
    _short = self.mNode
    _str_func = '[{0}] > skeleton_build'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func)) 
    
    _radius = self.atUtils('get_shapeOffset') * .25# or 1
    _side = self.atUtils('get_side')
    ml_joints = []
    
    mModule = self.atUtils('module_verify')
    
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError,"No rigNull connected"
    
    mPrerigNull = self.prerigNull
    if not mPrerigNull:
        raise ValueError,"No prerig null"
    
    #>> If skeletons there, delete -------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
    _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
    
    mEyeOrb = False
    
    _d_base = self.atBlockUtils('skeleton_getNameDictBase')
    _d_base['cgmType'] = 'skinJoint'    
    #pprint.pprint( _d_base )
    
    #..name --------------------------------------
    def name(mJnt,d):
        #mJnt.rename(NAMETOOLS.returnCombinedNameFromDict(d))
        for t,v in d.iteritems():
            log.debug("|{0}| >> {1} | {2}.".format(_str_func,t,v))            
            mJnt.doStore(t,v)
        mJnt.doName()
        
    #>> Eye ===================================================================================
    log.debug("|{0}| >> Eye...".format(_str_func))
    mRootHelper = self.getMessageAsMeta('rootHelper')
    mOrientHelper = self.getMessageAsMeta('eyeOrientHelper')
    
    p = mRootHelper.p_position
    
    #...create ---------------------------------------------------------------------------
    mEyeJoint = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
    mEyeJoint.parent = False
    self.copyAttrTo(_baseNameAttrs[0],mEyeJoint.mNode,'cgmName',driven='target')
    
    #...orient ----------------------------------------------------------------------------
    #cgmMeta.cgmObject().getAxisVector
    #CORERIG.match_orientation(mEyeJoint.mNode, mOrientHelper.mNode)
    p_aim = mOrientHelper.getPositionByAxisDistance('z+',10.0)
    SNAP.aim_atPoint(mEyeJoint.mNode,p_aim,'z+')
    JOINT.freezeOrientation(mEyeJoint.mNode)
    
    name(mEyeJoint,_d_base)
    ml_joints.append(mEyeJoint)
    
    mPrerigNull.connectChildNode(mEyeJoint.mNode,'eyeJoint')
    
    mRoot = mEyeJoint
    #>> Eye =================================================================================== 
    if self.buildEyeOrb:
        mEyeOrbJoint = mEyeJoint.doDuplicate()
        self.copyAttrTo(_baseNameAttrs[1],mEyeOrbJoint.mNode,'cgmName',driven='target')
        name(mEyeOrbJoint,_d_base)
        
        mEyeJoint.p_parent = mEyeOrbJoint
        ml_joints.insert(0,mEyeOrbJoint)
        mPrerigNull.connectChildNode(mEyeOrbJoint.mNode,'eyeOrbJoint')
        mRoot = mEyeOrbJoint

    #if len(ml_joints) > 1:
    #    ml_joints[0].getParent(asMeta=1).radius = ml_joints[-1].radius * 5
    
    #Pupil ======================================================================================
    str_pupilAttach = self.getEnumValueString('pupilAttach')
    str_irisAttach = self.getEnumValueString('irisAttach')

    
    for s in 'iris','pupil':
        str_build = self.getEnumValueString('{0}Build'.format(s))
        log.debug("|{0}| >> {2}: {1}.".format(_str_func,str_build, s))
        
        if str_build == 'joint':
            _d_hl = copy.copy(_d_base)
            _d_hl['cgmNameModifier'] = s        
            
            mHelper = mPrerigNull.getMessageAsMeta('{0}JointHelper'.format(s))
            if not mHelper:
                raise ValueError,"Missing Prerig handle: {0}. Rebuild prerig.".format(s)
            
            mJoint = mEyeJoint.doDuplicate()
            name(mJoint,_d_hl)
            
            mJoint.p_parent = mRoot
            
            mJoint.p_position = mHelper.p_position
            
            mPrerigNull.connectChildNode(mJoint.mNode,'{0}Joint'.format(s))        
            ml_joints.append(mJoint)
        
        
        
    #>> Highlight ===============================================================================
    if self.highlightSetup:
        _highlightSetup = self.getEnumValueString('highlightSetup')
        log.info("|{0}| >> highlight: {1}.".format(_str_func,_highlightSetup))
        
        _d_hl = copy.copy(_d_base)
        _d_hl['cgmNameModifier'] = 'highlight'        
        
        mHighlightJoint = mEyeJoint.doDuplicate()
        name(mHighlightJoint,_d_hl)
        
        mHighlightJoint.p_parent = mRoot
        mPrerigNull.connectChildNode(mHighlightJoint.mNode,'eyeHighlightJoint')        
        ml_joints.append(mHighlightJoint)
        
        if _highlightSetup == 'surfaceSlide':
            mHighlightJoint.doSnapTo(mHelper)
            
 
        
    if self.lidBuild:#=====================================================
        _lidBuild = self.getEnumValueString('lidBuild')
        log.debug("|{0}| >> EyeLid setup: {1}.".format(_str_func,_lidBuild))
        
        #'lidRootHelper'
        
        mLidsHelper = self.getMessageAsMeta('lidsHelper')
        _d_lids = copy.copy(_d_base)
        
        _d_lids['cgmNameModifier'] = 'lid'
        
        if _lidBuild == 'clam':
            for a in ['upr','lwr']:
                log.debug("|{0}| >> Creating lid joint: {1}.".format(_str_func,a))
                _a = '{0}LidHandle'.format(a)
                mHandle = self.getMessageAsMeta(_a)
                mJointHandle = mHandle.jointHelper
                
                mJoint = mJointHandle.doCreateAt('joint')
                mJoint.parent = mRoot
                
                mJoint.doStore('cgmName',a)
                name(mJoint,_d_lids)
                
                JOINT.freezeOrientation(mJoint.mNode)
                
                log.debug("|{0}| >> joint: {1} | {2}.".format(_str_func,mJoint,mJoint.parent))                
                ml_joints.append(mJoint)
                mPrerigNull.connectChildNode(mJoint.mNode,'{0}LidJoint'.format(a))
                
        elif _lidBuild == "full":
            _d_Lid = {'cgmName':'lid'}
            for d in 'upr','lwr':
                log.debug("|{0}| >>  lid {1}...".format(_str_func,d)+ '-'*20)
                d_dir = copy.copy(_d_Lid)
                d_dir['cgmPosition'] = d
                
    
                for side in ['inner','center','outer']:
                    d_dir['cgmDirection'] = _side
                    key = d+'Lid'+side.capitalize()        
                    mHandles = mPrerigNull.msgList_get('{0}JointHelpers'.format(key))
                    ml = []
                    for mHandle in mHandles:
                        mJnt = create_jointFromHandle(mHandle,mRoot)
                        ml.append(mJnt)
                        mShape = mHandle.shapeHelper
                        mShape.connectChildNode(mJnt,'targetJoint')

                    mPrerigNull.msgList_connect('{0}Joints'.format(key),ml)
                    ml_joints.extend(ml)
            else:
                log.error("Don't have setup for eyelidType: {0}".format(_lidBuild))
        
        if self.lidFanLwr or self.lidFanUpr:
            l_toDo = []
            if self.lidFanUpr:
                l_toDo.append('uprFanCenter')
            if self.lidFanLwr:
                l_toDo.append('lwrFanCenter')
                
            for a in l_toDo:
                log.debug("|{0}| >> Creating fan lid joint: {1}.".format(_str_func,a))
                _a = '{0}LidHandle'.format(a)
                
                mHandle = self.getMessageAsMeta(_a)
                mJointHandle = mHandle.jointHelper
                
                mJoint = mJointHandle.doCreateAt('joint')
                mJoint.parent = mRoot
                
                mJoint.doStore('cgmName',a)
                name(mJoint,_d_lids)
                
                JOINT.freezeOrientation(mJoint.mNode)
                
                log.debug("|{0}| >> joint: {1} | {2}.".format(_str_func,mJoint,mJoint.parent))                
                ml_joints.append(mJoint)
                mPrerigNull.connectChildNode(mJoint.mNode,'{0}LidJoint'.format(a))

            
    
    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    self.atBlockUtils('skeleton_connectToParent')

    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
    for mJnt in ml_joints:mJnt.rotateOrder = 5
        
    return ml_joints    

    return
    

    


#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {'head':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
@cgmGEN.Timer
def rig_prechecks(self):
    _str_func = 'rig_prechecks'
    log.debug(cgmGEN.logString_start(_str_func))

    
    mBlock = self.mBlock
    
    str_lidBuild = mBlock.getEnumValueString('lidBuild')
    if str_lidBuild not in ['none','clam','full']:
        self.l_precheckErrors.append("Lid setup not completed: {0}".format(str_lidBuild))
    
    

@cgmGEN.Timer
def rig_dataBuffer(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_dataBuffer'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mModule = self.mModule
    mRigNull = self.mRigNull
    mPrerigNull = mBlock.prerigNull
    ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
    mMasterNull = self.d_module['mMasterNull']
    
    mEyeFormHandle = mBlock.bbHelper
    
    self.mRootFormHandle = mEyeFormHandle
    ml_formHandles = [mEyeFormHandle]
    
    self.b_scaleSetup = mBlock.scaleSetup
    
    
    """
    self.str_lidBuild = False
    if mBlock.lidBuild:
        self.str_lidBuild  = mBlock.getEnumValueString('lidBuild')
        
    self.str_highlightSetup = False
    if mBlock.highlightSetup:
        self.str_highlightSetup = mBlock.getEnumValueString('highlightSetup')"""
    
    for k in ['lidBuild','highlightSetup',
              'ballSetup',
              'irisBuild','pupilBuild','ikSetup','buildSDK',
              'irisAttach','pupilAttach',
              'lidFanUpr','lidFanLwr','lidAttach']:
        self.__dict__['str_{0}'.format(k)] = ATTR.get_enumValueString(mBlock.mNode,k)    
        self.__dict__['v_{0}'.format(k)] = mBlock.getMayaAttr(k)
        
    #Logic checks ========================================================================
    self.b_needEyeOrb = False
    if not mBlock.buildEyeOrb and self.str_lidBuild:
        self.b_needEyeOrb = True
        
        
    #SurfaceSlide Eye ========================================================================
    b_eyeSlide = False
    for v in self.str_lidAttach, self.str_irisAttach, self.str_pupilAttach:
        if v == 'surfaceSlide':
            b_eyeSlide = True
            break
    self.b_eyeSlide = b_eyeSlide
    
    b_irisPupilSlide = False
    for v in self.str_irisAttach, self.str_pupilAttach:
        if v == 'surfaceSlide':
            b_irisPupilSlide = True
            break    
    self.b_irisPupilSlide = b_irisPupilSlide
    
    #Offset ============================================================================    
    str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
    
    if not mBlock.getMayaAttr('offsetMode'):
        log.debug("|{0}| >> default offsetMode...".format(_str_func))
        self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
    else:
        str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
        log.debug("|{0}| >> offsetMode: {1}".format(_str_func,str_offsetMode))
        
        l_sizes = []
        for mHandle in ml_formHandles:
            _size_sub = POS.get_bb_size(mHandle,True)
            l_sizes.append( MATH.average(_size_sub) * .1 )            
        self.v_offset = MATH.average(l_sizes)
    log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))    
    log.debug(cgmGEN._str_subLine)
    
    #Size =======================================================================================
    self.v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    self.f_sizeAvg = MATH.average(self.v_baseSize)
    
    log.debug("|{0}| >> size | self.v_baseSize: {1} | self.f_sizeAvg: {2}".format(_str_func,
                                                                                  self.v_baseSize,
                                                                                  self.f_sizeAvg ))
    #DynParents =============================================================================
    self.UTILS.get_dynParentTargetsDat(self)
    log.debug(cgmGEN._str_subLine)
    
    #rotateOrder =============================================================================
    _str_orientation = self.d_orientation['str']
    _l_orient = [_str_orientation[0],_str_orientation[1],_str_orientation[2]]
    self.ro_base = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
    self.ro_head = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    self.ro_headLookAt = "{0}{2}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
    log.debug("|{0}| >> rotateOrder | self.ro_base: {1}".format(_str_func,self.ro_base))
    log.debug("|{0}| >> rotateOrder | self.ro_head: {1}".format(_str_func,self.ro_head))
    log.debug("|{0}| >> rotateOrder | self.ro_headLookAt: {1}".format(_str_func,self.ro_headLookAt))
    log.debug(cgmGEN._str_subLine)
    
    #eyeLook =============================================================================
    reload(self.UTILS)
    self.mEyeLook = False
    
    if self.str_ballSetup != 'fixed':
        self.mEyeLook = self.UTILS.eyeLook_get(self,True)#autobuild...

    return True


def create_jointFromHandle(mHandle=None,mParent = False,cgmType='skinJoint'):
    mJnt = mHandle.doCreateAt('joint')
    mJnt.doCopyNameTagsFromObject(mHandle.mNode,ignore = ['cgmType'])
    mJnt.doStore('cgmType',cgmType)
    mJnt.doName()
    JOINT.freezeOrientation(mJnt.mNode)

    mJnt.p_parent = mParent
    try:ml_joints.append(mJnt)
    except:pass
    return mJnt

@cgmGEN.Timer
def create_lidRoot(mJnt,mEyeJoint,mBlock):
    mLidRoot = mEyeJoint.doDuplicate(po=True)
    mLidRoot.doStore('cgmName',mJnt.p_nameBase)
    mLidRoot.doStore('cgmType','lidRoot')
    mLidRoot.p_parent = False
    mLidRoot.doName()
    
    SNAP.aim(mLidRoot.mNode, mJnt.mNode, 'z+','y+','vector',
             mBlock.getAxisVector('y+'))
    JOINT.freezeOrientation(mLidRoot.mNode)
    mJnt.connectChildNode(mLidRoot.mNode,'lidRoot')    
    
    return mLidRoot

def rig_skeleton(self):
    def doSingleJoint(tag,mParent = None):
        log.debug("|{0}| >> gathering {1}...".format(_str_func,tag))            
        mJntSkin = mPrerigNull.getMessageAsMeta('{0}Joint'.format(tag))
    
        mJntRig = mJntSkin.getMessageAsMeta('rigJoint')
        mJntDriver = mJntSkin.getMessageAsMeta('driverJoint')
    
        if mParent is not None:
            mJntDriver.p_parent = mParent
    
        md_skinJoints[tag] = mJntSkin
        md_rigJoints[tag] = mJntRig
        md_driverJoints[tag] = mJntDriver
        md_handleShapes[tag] = mPrerigNull.getMessageAsMeta('{0}ShapeHelper'.format(tag))
    
    def mirrorConnect(tag1,tag2):
        md_rigJoints[tag1].doStore('mirrorControl',md_rigJoints[tag2])
        md_rigJoints[tag2].doStore('mirrorControl', md_rigJoints[tag1])
        
        md_driverJoints[tag1].doStore('mirrorControl',md_driverJoints[tag2])
        md_driverJoints[tag2].doStore('mirrorControl', md_driverJoints[tag1])
        
    def doSingleDriver(mJoint,tag,mRigJoint = None,):
        #print mJoint
        mDriver = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                          [mJoint],
                                                          'driver',
                                                          False,
                                                          singleMode = True,
                                                          cgmType='driver')[0]
        #print mDriver
        if mRigJoint:
            mRigJoint.doStore('driverJoint',mDriver)
        mJoint.doStore('driverJoint',mDriver)
        md_driverJoints[tag] = mDriver

    
    _short = self.d_block['shortName']
    
    _str_func = 'rig_skeleton'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mPrerigNull = mBlock.prerigNull
    
    ml_jointsToConnect = []
    ml_jointsToHide = []
    md_skinJoints = {}
    md_rigJoints = {}
    md_segJoints = {}
    md_driverJoints = {}
    md_handles = {}
    md_handleShapes = {}
    md_directShapes = {}
    md_directJoints = {}    
    ml_joints = mRigNull.msgList_get('moduleJoints')
    self.d_joints['ml_moduleJoints'] = ml_joints
    
    
    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'])
                                     #d_rotateOrders, d_preferredAngles)
    
    
    #Eye =================================================================================
    log.debug("|{0}| >> Eye...".format(_str_func)+'-'*40)
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                           ml_joints, 'rig',
                                                           self.mRigNull,
                                                           'rigJoints',
                                                           'rig',
                                                           cgmType = False,
                                                           blockNames=False)
    
    
    mEyeJoint = mPrerigNull.getMessageAsMeta('eyeJoint')
    mEyeRigJoint = mEyeJoint.getMessageAsMeta('rigJoint')
    log.debug(mEyeJoint)
    log.debug(mEyeRigJoint)
    mRigNull.connectChildNode(mEyeRigJoint,'directEye')
    
    mEyeBlend = False
    mEyeRoot = mEyeRigJoint
    ml_driversToMake = copy.copy(ml_joints)
    
    if self.str_ballSetup not in ['fixed']:
        #Fk Joint ...........
        mEyeFK = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,[mEyeJoint],
                                                         'fk', mRigNull,
                                                         'fkEye',
                                                         cgmType = False,
                                                         singleMode = True)[0]    
        mEyeFK.p_parent = mEyeRigJoint.p_parent
        
        ml_driversToMake.remove(mEyeJoint)    
        
        mEyeRoot = mEyeFK
    
        #IK setup ----------------------------------------------------------------------------------
        
        if mBlock.ikSetup:
            log.debug("|{0}| >> Eye IK...".format(_str_func))              
    
            mEyeIK = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,[mEyeJoint],
                                                             'ik', mRigNull,
                                                             'ikEye',
                                                             cgmType = False,
                                                             singleMode = True)[0]
            
            mEyeBlend = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,[mEyeJoint],
                                                                'blend', mRigNull,
                                                                'blendEye',
                                                                cgmType = False,
                                                                singleMode = True)[0]
            
            for mJnt in mEyeIK,mEyeBlend:
                mJnt.p_parent = mEyeRigJoint.p_parent
            
            mEyeRigJoint.p_parent = mEyeBlend
            
            #ml_jointsToConnect.extend([mEyeIK])
            ml_jointsToHide.append(mEyeBlend)    
        log.debug(cgmGEN._str_subLine)
    
    #Pupil  =====================================================================
    if self.str_pupilBuild == 'joint':
        log.debug("|{0}| >> Eye...".format(_str_func)+'-'*40)
        
        mPupilJoint = mPrerigNull.getMessageAsMeta('pupilJoint')
        mPupilRigJoint = mPupilJoint.getMessageAsMeta('rigJoint')
        
        mPupilDriver = mPupilJoint.getMessageAsMeta('driverJoint')
        
        log.debug(mPupilJoint)
        log.debug(mPupilRigJoint)

        mRigNull.connectChildNode(mPupilRigJoint,'directPupil')
        
        self.mPupilJoint = mPupilJoint
        self.mPupilRigJoint = mPupilRigJoint
        
        for mJnt in [mPupilRigJoint]:
            if mEyeBlend:
                mJnt.p_parent = mEyeBlend
            else:
                mJnt.p_parent = mEyeRoot
                
        ml_driversToMake.remove(mPupilJoint)
        
        doSingleDriver(mPupilJoint,'pupil',mPupilRigJoint)
        
    
                
    #Iris  =====================================================================
    if self.str_irisBuild == 'joint':
        log.debug("|{0}| >> Eye...".format(_str_func)+'-'*40)
        
        mIrisJoint = mPrerigNull.getMessageAsMeta('irisJoint')
        mIrisRigJoint = mIrisJoint.getMessageAsMeta('rigJoint')
        log.debug(mIrisJoint)
        log.debug(mIrisRigJoint)

        mRigNull.connectChildNode(mIrisRigJoint,'directIris')
        
        self.mIrisJoint = mIrisJoint
        self.mIrisRigJoint = mIrisRigJoint
        
        for mJnt in [mIrisRigJoint]:
            if mEyeBlend:
                mJnt.p_parent = mEyeBlend
            else:
                mJnt.p_parent = mEyeRoot

        ml_driversToMake.remove(mIrisJoint)    
        doSingleDriver(mIrisJoint,'iris',mIrisRigJoint)

    #EyeLid =====================================================================================
    log.debug("|{0}| >> Eye...".format(_str_func)+'-'*40)
    #reload(BLOCKUTILS)
    self.d_lidData = {}
    
    mHighlight = mBlock.prerigNull.getMessageAsMeta('eyeHighlightJoint')
    
    if mHighlight:
        mRigJoint = mHighlight.getMessageAsMeta('rigJoint')        
        ml_driversToMake.remove(mHighlight)
        doSingleDriver(mHighlight,'highlight',mRigJoint)
        
    
    if self.str_lidBuild == 'clam':

        #Need to make our lid roots and orient
        for tag in 'upr','lwr':
            log.debug("|{0}| >> {1}...".format(_str_func,tag))
            self.d_lidData[tag] = {}
            _d = self.d_lidData[tag]
            
            mLidSkin = mPrerigNull.getMessageAsMeta('{0}LidJoint'.format(tag))
            mLidRig = mLidSkin.getMessageAsMeta('rigJoint')
            _d['mSkin'] = mLidSkin
            _d['mRig'] = mLidRig
            #Lid Blend
            mLidBlend = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,[mLidRig],
                                                              'ik', mRigNull,
                                                              '{0}IKLid'.format(tag),
                                                              singleMode = True,
                                                              cgmType=False)[0]
            _d['mBlend'] = mLidBlend
            
            #if self.str_lidAttach == 'aimJoint':
            #Lid Root
            mLidRoot = mEyeJoint.doDuplicate(po=True)
            mLidRoot.doStore('cgmName','{0}lid_rootJoint'.format(tag))
            ATTR.delete(mLidRoot.mNode,'cgmType')
            mLidRoot.p_parent = False
            mLidRoot.doName()
            
            _d['mRoot'] = mLidRoot
            
            SNAP.aim(mLidRoot.mNode, mLidSkin.mNode, 'z+','y+','vector',
                     mBlock.getAxisVector('y+'))
            JOINT.freezeOrientation(mLidRoot.mNode)
            mLidBlend.p_parent = mLidRoot
            
            for mJnt in mLidBlend,mLidRoot:
                try:mJnt.drawStyle =2
                except:mJnt.radius = .00001
                    
            mLidRig.p_parent = mLidBlend
    else:
        log.debug("|{0}| >>  lid ".format(_str_func)+ '-'*20)
        

        ml_driverJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                  ml_driversToMake,
                                                                  None,
                                                                  self.mRigNull,
                                                                  'driverJoints',
                                                                  'driver',
                                                                  cgmType = 'driver',
                                                                  blockNames=False)        
        
        
        
        for d in 'upr','lwr':
            log.debug("|{0}| >>  lid {1}...".format(_str_func,d)+ '-'*5)
            #key = d+'Lid'+side.capitalize()       
            _k = 'lid'+d.capitalize()
            
            md_directShapes[_k] = {}
            md_directJoints[_k] = {}
            
            for _d in md_skinJoints,md_handles,md_handleShapes,md_rigJoints,md_segJoints:
                if not _d.get(_k):
                    _d[_k] = {}

            for side in ['inner','center','outer']:
                #key = 'Lid'+d.capitalize()+side.capitalize()
                key = d+'Lid'+STR.capFirst(side)
                ml = []
                ml_hide = []
                md_directShapes[_k][side] = mPrerigNull.msgList_get('{0}JointShapes'.format(key))
                
                ml_skin = mPrerigNull.msgList_get('{0}Joints'.format(key))
                ml_rig = []
                ml_driver = []
                
                for mJnt in ml_skin:
                    mRigJoint = mJnt.getMessageAsMeta('rigJoint')
                    ml_rig.append(mRigJoint)
                
                    mDriver = mJnt.getMessageAsMeta('driverJoint')
                    ml_driver.append(mDriver)
                    mDriver.p_parent = False
                    mRigJoint.doStore('driverJoint',mDriver)
                    
                    if self.str_lidAttach == 'aimJoint':
                        mLidRoot = create_lidRoot(mDriver,mEyeJoint,mBlock)
                        mDriver.p_parent = mLidRoot
                        ml_hide.append(mLidRoot)
                        
                    mRigJoint.p_parent = mDriver
                    ml_hide.append(mDriver)
                
                md_rigJoints[_k][side] = ml_rig
                md_skinJoints[_k][side] = ml_skin
                md_segJoints[_k][side] = ml_driver
                md_directJoints[_k][side] = ml_rig
                
                mHandles = mPrerigNull.msgList_get('{0}PrerigHandles'.format(key))
                mHelpers = mPrerigNull.msgList_get('{0}PrerigShapes'.format(key))
                
                for ii,mHandle in enumerate(mHandles):
                    mJnt = create_jointFromHandle(mHandle,False,'handle')
                    ml.append(mJnt)
                    
                    if d == 'upr' and side in ['inner','outer'] and ii == 0:
                        log.debug("|{0}| >>  influenceJoints for {1}...".format(_str_func,mHandle))
                        for k in 'upr','lwr':
                            mSub = create_jointFromHandle(mHandle,False,'{0}Influence'.format(k))
                            mSub.doStore('mClass','cgmObject')
                            mSub.p_parent = mJnt
                            mJnt.doStore('{0}Influence'.format(k),mSub)
                            ml_jointsToConnect.append(mSub)
                            ml_jointsToHide.append(mSub)
                
                ml_jointsToHide.extend(ml_hide)
                md_handles[_k][side] = ml
                md_handleShapes[_k][side] = mHelpers
                
            """
            for i,mObj in enumerate(md_directJoints[_k]['right']):
                mObj.doStore('mirrorControl',md_directJoints[_k]['left'][i])
                md_directJoints[_k]['left'][i].doStore('mirrorControl', mObj)
            
            for i,mObj in enumerate(md_handles[_k]['right']):
                mObj.doStore('mirrorControl',md_handles[_k]['left'][i])
                md_handles[_k]['left'][i].doStore('mirrorControl', mObj)
                """
            log.debug(cgmGEN._str_subLine)
            
    if mBlock.lidBuild:
        l_toDo = []
        if self.v_lidFanUpr:
            l_toDo.append('uprFanCenter')
        if self.v_lidFanLwr:
            l_toDo.append('lwrFanCenter')
            
        for tag in l_toDo:
            log.debug("|{0}| >> {1}...".format(_str_func,tag))

            self.d_lidData[tag] = {}
            _d = self.d_lidData[tag]
            
            mLidSkin = mPrerigNull.getMessageAsMeta('{0}LidJoint'.format(tag))
            mLidRig = mLidSkin.getMessageAsMeta('rigJoint')
            
            _d['mSkin'] = mLidSkin
            _d['mRig'] = mLidRig
            
            #if self.str_lidAttach == 'aimJoint':
            #Lid Root
            mLidRoot = mEyeJoint.doDuplicate(po=True)
            mLidRoot.doStore('cgmName','{0}Lid_rootJoint'.format(tag))
            ATTR.delete(mLidRoot.mNode,'cgmType')
            mLidRoot.p_parent = False
            mLidRoot.doName()
            
            _d['mRoot'] = mLidRoot
            
            SNAP.aim(mLidRoot.mNode, mLidSkin.mNode, 'z+','y+','vector',
                     mBlock.getAxisVector('y+'))
            JOINT.freezeOrientation(mLidRoot.mNode)
            
            for mJnt in [mLidRoot]:
                try:mJnt.drawStyle =2
                except:mJnt.radius = .00001
            mLidRig.p_parent = mLidRoot

    log.debug(cgmGEN._str_subLine)
    self.md_rigJoints = md_rigJoints
    self.md_skinJoints = md_skinJoints
    self.md_segJoints = md_segJoints
    self.md_handles = md_handles
    self.md_handleShapes = md_handleShapes
    self.md_driverJoints = md_driverJoints
    self.md_directShapes = md_directShapes
    self.md_directJoints = md_directJoints
    
    #...joint hide -----------------------------------------------------------------------------------
    for mJnt in ml_jointsToHide:
        try:mJnt.drawStyle =2
        except:mJnt.radius = .00001
            
    #...connect... 
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    return

#@cgmGEN.Timer
def rig_shapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
    
        mBlock = self.mBlock
        _baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'nameList')    
        mHandleFactory = mBlock.asHandleFactory()
        mRigNull = self.mRigNull
        mPrerigNull = mBlock.prerigNull
        mEyeDirect = mRigNull.getMessageAsMeta('directEye')
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        mSettings = None
        
        if mBlock.buildEyeOrb or mBlock.ikSetup or self.b_needEyeOrb:
            log.debug("|{0}| >> Settings needed...".format(_str_func))
            mSettingsHelper = mBlock.getMessageAsMeta('settingsHelper')
            if not mSettingsHelper:
                raise ValueError,"Settings helper should have been generated during prerig phase. Please go back"
            log.debug(mSettingsHelper)
            
            if mBlock.buildEyeOrb:
                log.debug("|{0}| >> EyeOrb Settings...".format(_str_func))
                mEyeOrbJoint = mPrerigNull.getMessageAsMeta('eyeOrbJoint')
                mEyeOrbRigJoint = mEyeOrbJoint.getMessageAsMeta('rigJoint')
                CORERIG.shapeParent_in_place(mEyeOrbRigJoint.mNode,mSettingsHelper.mNode,False)
                mSettings = mEyeOrbRigJoint
            elif self.b_needEyeOrb:
                mSettings = mEyeDirect.doCreateAt(setClass=True)
                CORERIG.shapeParent_in_place(mSettings.mNode,mSettingsHelper.mNode,False)
                
            else:
                mSettings = mSettingsHelper.doCreateAt()
                CORERIG.shapeParent_in_place(mSettings.mNode,mSettingsHelper.mNode,True)
                
            mSettings.doStore('mClass','cgmObject')
            #mSettings.doStore('cgmName','{0}_eyeRoot'.format(self.d_module['partName']))
            #mSettings.doName()
            mSettings.rename('{0}_eyeRoot'.format(self.d_module['partName']))
                
            mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
            mRigNull.connectChildNode(mSettings,'rigRoot','rigNull')#Connect
            
        
        if mBlock.scaleSetup:
            mRoot = mRigNull.getMessageAsMeta('rigRoot')
            if mBlock.getMessage('scalePivotHelper'):
                log.info("|{0}| >> Scale Pivot setup...".format(_str_func))
                p_scalePivot = mBlock.scalePivotHelper.p_position
                TRANS.scalePivot_set(mRoot.mNode, p_scalePivot)
                TRANS.rotatePivot_set(mRoot.mNode, p_scalePivot)
                
        
        mBallRoot = False
        
        log.debug("|{0}| >> ballRoot ...".format(_str_func))
        mBallControl = mBlock.rootHelper.doDuplicate(po=False)
        mc.makeIdentity(mBallControl.mNode, apply = True, t=0, r=0,s=1,n=0,pn=1)
        mBallControl.doStore('cgmName','ball')
        mBallControl.p_parent = mSettings
        mBallControl.doName()
        mBallRoot = mBallControl
        mRigNull.connectChildNode(mBallControl,'controlBall','rigNull')#Connect
            
        if self.str_ballSetup != 'fixed':
            #Logic ====================================================================================
            mFKEye = mRigNull.getMessageAsMeta('fkEye')
            mEyeOrientHelper = mBlock.eyeOrientHelper
            
            if mFKEye:
                log.debug("|{0}| >> FK eye...".format(_str_func))  
                log.debug(mFKEye)
                
                
                #_shape_fk = CURVES.create_fromName('sphere', size = [v*1.1 for v in self.v_baseSize])
                #SNAP.go(_shape_fk,mFKEye.mNode)
                #mHandleFactory.color(_shape_fk, controlType = 'main')
                CORERIG.shapeParent_in_place(mFKEye.mNode,mEyeOrientHelper.mNode,1)
                mHandleFactory.color(mFKEye.mNode, controlType = 'main')
                
                #mShape = mBlock.getMessageAsMeta('bbHelper').doDuplicate()
                mRigNull.connectChildNode(mFKEye.mNode,'controlFK','rigNull')#Connect
                
                if not mSettings:
                    mRigNull.connectChildNode(mFKEye,'settings','rigNull')#Connect
                    
                
            mIKEye = mRigNull.getMessageAsMeta('ikEye')
            if mIKEye:
                log.debug("|{0}| >> IK eye...".format(_str_func))  
                log.debug(mIKEye)
                
                if not self.b_eyeSlide:#IK direct shape... -------------------------------------------
                    CORERIG.shapeParent_in_place(mIKEye.mNode,mEyeOrientHelper.mNode,1)
                    mHandleFactory.color(mIKEye.mNode, controlType = 'sub')
                    
                    mRigNull.connectChildNode(mIKEye.mNode,'controlIKDirect','rigNull')#Connect
                
                
                #Create shape... -----------------------------------------------------------------------        
                log.debug("|{0}| >> Creating shape...".format(_str_func))
                mIKControl = cgmMeta.asMeta( CURVES.create_fromName('eye',
                                                                    direction = 'z+',
                                                                    size = self.f_sizeAvg * .5 ,
                                                                    absoluteSize=False),'cgmObject',setClass=True)
                mIKControl.doSnapTo(mBlock.mNode)
                pos = RIGGEN.get_planeIntersect(self.mEyeLook, mIKEye)
                #pos = mBlock.getPositionByAxisDistance('z+',
                #                                       self.f_sizeAvg * 4)
            
                mIKControl.p_position = pos
                mIKControl.p_orient = self.mEyeLook.p_orient
                
                if mIKEye.hasAttr('cgmDirection'):
                    mIKControl.doStore('cgmDirection',mIKEye.cgmDirection)
                mIKControl.doStore('cgmName',mIKEye.cgmName)
                
                mHandleFactory.color(mIKControl.mNode)
        
                mIKControl.doName()
                
                mIKControl.p_parent = self.mEyeLook
                mRigNull.connectChildNode(mIKControl,'controlIK','rigNull')#Connect
            
            
        
        mDirectEye = mRigNull.getMessageAsMeta('directEye')
        if mDirectEye:#Direct Eye =======================================================================
            log.debug("|{0}| >> direct eye...".format(_str_func))  
            log.debug(mDirectEye)
            
            trackcrv= CORERIG.create_at(l_pos=[mDirectEye.p_position,
                                               mBlock.getPositionByAxisDistance('z+',
                                               self.f_sizeAvg * 1.5)],#ml_handleJoints[1]],
                                        create='curveLinear',
                                        baseName = '{0}_eyeTrack'.format(self.d_module['partName']))
        
            
            CORERIG.shapeParent_in_place(mDirectEye,trackcrv,False)
            mHandleFactory = mBlock.asHandleFactory()
            mHandleFactory.color(mDirectEye.mNode, controlType = 'sub')
            
            if not mSettings:
                mRigNull.connectChildNode(mDirectEye,'settings','rigNull')#Connect
                
            #mDirectEye.p_parent = mBallRoot
            
            #for s in mDirectEye.getShapes(asMeta=True):
                #s.overrideEnabled = 1
                #s.overrideDisplayType = 2

        
        if self.str_pupilBuild in ['joint','surfaceSlide'] :
            log.debug("|{0}| >> Pupil ...".format(_str_func))
            mPupilRigJoint = self.mPupilRigJoint
            mShape = mPrerigNull.pupilDirectShape.doDuplicate(po=False)
            mHandleFactory.color(mShape.mNode, controlType = 'sub')
            
            #mShape.tz = mShape.tz + self.v_offset
            
            CORERIG.shapeParent_in_place(mPupilRigJoint.mNode, mShape.mNode,False)
            mRigNull.connectChildNode(mPupilRigJoint,'controlPupil','rigNull')#Connect

        if self.str_irisBuild in ['joint','surfaceSlide'] :
            log.debug("|{0}| >> Iris ...".format(_str_func))
            mIrisRigJoint = self.mIrisRigJoint
            mShape = mPrerigNull.irisDirectShape.doDuplicate(po=False)
            #mShape.tz = mShape.tz + self.v_offset
            mHandleFactory.color(mShape.mNode, controlType = 'sub')
            
            CORERIG.shapeParent_in_place(mIrisRigJoint.mNode, mShape.mNode,False)
            mRigNull.connectChildNode(mIrisRigJoint,'controlIris','rigNull')#Connect
            
        
        if self.b_irisPupilSlide:
            log.debug("|{0}| >> slideEye ...".format(_str_func))
            mSlideEyeHelper = mBlock.getMessageAsMeta('irisPosHelper')
            log.debug(mSettingsHelper)
            
            mSlideEye = mSlideEyeHelper.doDuplicate(po=False)
            
            mSlideEye.p_parent = False
            
            mSlideEye.doStore('mClass','cgmObject')
            #mSettings.doStore('cgmName','{0}_eyeRoot'.format(self.d_module['partName']))
            #mSettings.doName()
            mSlideEye.rename('{0}_slideEye'.format(self.d_module['partName']))
                
            mRigNull.connectChildNode(mSlideEye,'controlSlideEye','rigNull')#Connect
            
        
        mHighlight = mPrerigNull.getMessageAsMeta('eyeHighlightJoint')
        if mHighlight:#==============================================================================
            log.debug("|{0}| >> highlight ...".format(_str_func))
            mHighlightDirectJoint = mHighlight.getMessageAsMeta('rigJoint')
            
            mHighlightShape = cgmMeta.asMeta( CURVES.create_fromName('circle',
                                                                direction = 'z+',
                                                                size = mBlock.jointRadius ,
                                                                absoluteSize=False),'cgmObject',setClass=True)
            mHighlightShape.doSnapTo(mHighlightDirectJoint.mNode)
            
            
            if self.str_highlightSetup == 'joint':
                pos = mBlock.getPositionByAxisDistance('z+',
                                                       self.f_sizeAvg * .25 + mBlock.controlOffset)
            else:
                pos = mBlock.getPositionByAxisDistance('z+',
                                                       mBlock.controlOffset)
                
            mHighlightShape.p_position = pos
            mHandleFactory.color(mHighlightShape.mNode, controlType='sub')
            
            CORERIG.shapeParent_in_place(mHighlightDirectJoint.mNode,mHighlightShape.mNode,False)
            
            mRigNull.connectChildNode(mHighlightDirectJoint,'controlHighlight','rigNull')#Connect            
            
        
        if self.str_lidBuild:#Lid setup =======================================================================
            log.debug("|{0}| >> Lid setup: {1}".format(_str_func,self.str_lidBuild))
            if self.str_lidBuild == 'clam':
                for k in 'upr','lwr':
                    log.debug("|{0}| >> lid handle| {1}...".format(_str_func,k))                      
                    _key = '{0}LidHandle'.format(k)
                    mShapeSource = mBlock.getMessageAsMeta(_key)
                    mHandle = mShapeSource.doCreateAt('joint',setClass=True)
                    
                    try:mHandle.drawStyle =2
                    except:mHandle.radius = .00001
                    
                    CORERIG.shapeParent_in_place(mHandle.mNode,mShapeSource.mNode)
                    mHandle.doStore('cgmName','{0}Lid'.format(k),attrType='string')
                    _size = TRANS.bbSize_get(mHandle.mNode,True, mode ='max')
                    mHandleFactory.color(mHandle.mNode, controlType = 'main')
                    
                    if self.mModule.hasAttr('cgmDirection'):
                        mHandle.doStore('cgmDirection',self.mModule.cgmDirection)
                    
                    self.d_lidData[k]['mHandle'] = mHandle
                    mHandle.doName()
                    mRigNull.connectChildNode(mHandle,_key,'rigNull')#Connect
                    
                    log.debug("|{0}| >> lid direct| {1}...".format(_str_func,k))
                    mRig =  self.d_lidData[k]['mRig']
                    
                    _shape = CURVES.create_controlCurve(mRig.mNode, 'cube',
                                                        sizeMode= 'fixed',
                                                        size = _size)
                    mHandleFactory.color(_shape, controlType = 'sub')
                    CORERIG.shapeParent_in_place(mRig.mNode,_shape,False)
                    
            else:
                log.debug("|{0}| >> lid setup...".format(_str_func)+ '-'*40)

                
                #Handles ================================================================================
                log.debug("|{0}| >> Handles...".format(_str_func)+ '-'*80)
                for k in 'lidLwr','lidUpr':
                    log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
                    for side,ml in self.md_handles[k].iteritems():
                        log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                        for i,mHandle in enumerate(ml):
                            log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                            CORERIG.shapeParent_in_place(mHandle.mNode,
                                                         self.md_handleShapes[k][side][i].mNode)
                log.debug(cgmGEN._str_subLine)
                
                for k,d in self.md_directJoints.iteritems():
                    log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
                    for side,ml in d.iteritems():
                        log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                        for i,mHandle in enumerate(ml):
                            log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                            CORERIG.shapeParent_in_place(mHandle.mNode,
                                                         self.md_directShapes[k][side][i].mNode)
                            #ml_processed.append(mHandle)                

        if self.v_lidBuild:
            if mBlock.lidFanLwr or mBlock.lidFanUpr:
                l_toDo = []
                if mBlock.lidFanUpr:
                    l_toDo.append('uprFanCenter')
                if mBlock.lidFanLwr:
                    l_toDo.append('lwrFanCenter')
                    
                for k in l_toDo:
                    log.info("|{0}| >> lid fan handle| {1}...".format(_str_func,k))                      
                    _key = '{0}LidHandle'.format(k)
                    
                    mShapeSource = mBlock.getMessageAsMeta(_key)
                    mHandle = mShapeSource.doCreateAt('joint',setClass=True)
                    
                    try:mHandle.drawStyle =2
                    except:mHandle.radius = .00001
                    
                    CORERIG.shapeParent_in_place(mHandle.mNode,mShapeSource.mNode)
                    mHandle.doStore('cgmName','{0}Lid'.format(k),attrType='string')
                    
                    _size = TRANS.bbSize_get(mHandle.mNode,True, mode ='max')
                    
                    if self.mModule.hasAttr('cgmDirection'):
                        mHandle.doStore('cgmDirection',self.mModule.cgmDirection)
                    
                    self.d_lidData[k]['mHandle'] = mHandle
                    mHandle.doName()
                    mRigNull.connectChildNode(mHandle,_key,'rigNull')#Connect
                    
                    log.debug("|{0}| >> lid direct| {1}...".format(_str_func,k))
                    mRig =  self.d_lidData[k]['mRig']
                    
                    _shape = CURVES.create_controlCurve(mRig.mNode, 'cube',
                                                        sizeMode= 'fixed',
                                                        size = _size)
                    mHandleFactory.color(_shape, controlType = 'sub')
                    CORERIG.shapeParent_in_place(mRig.mNode,_shape,False)
                
 
        for mJnt in ml_rigJoints:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001                
        return
    except Exception,error:
        cgmGEN.cgmExceptCB(Exception,error,msg=vars())


@cgmGEN.Timer
def rig_controls(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_controls'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
      
        mRigNull = self.mRigNull
        mBlock = self.mBlock
        ml_controlsAll = []
        if self.mEyeLook:
            ml_controlsAll.append(self.mEyeLook)#we'll append to this list and connect them all at the end
        
        
        
        mRootParent = self.mDeformNull
        
        d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')
        
        mControlFK = mRigNull.getMessageAsMeta('fkEye')
        mControlIK = mRigNull.getMessageAsMeta('controlIK')
        mSettings = mRigNull.getMessageAsMeta('settings')
        mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
        mDirect = mRigNull.getMessageAsMeta('directEye')
        
        b_sdk=False
        if self.str_buildSDK in ['dag']:
            b_sdk = True
        
        # Drivers ==========================================================================================    
        if mBlock.ikSetup:
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
            
    
        #>> vis Drivers ==============================================================================	
        #mPlug_visSub = self.atBuilderUtils('build_visSub')
        
        mPlug_visSub = self.atBuilderUtils('build_visModuleMD','visSub')
        mPlug_visDirect = self.atBuilderUtils('build_visModuleMD','visDirect')

        # Connect to visModule ...
        ATTR.connect(self.mPlug_visModule.p_combinedShortName, 
                     "{0}.visibility".format(self.mDeformNull.mNode))
        
        """
        mPlug_visSub = cgmMeta.cgmAttr(mSettings,'visSub', value = True,
                                          attrType='bool', defaultValue = True,
                                          keyable = False,hidden = False)        
        mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True,
                                          attrType='bool', defaultValue = False,
                                          keyable = False,hidden = False)"""        
        
        #Settings ========================================================================================
        if mSettings:
            log.debug("|{0}| >> Found settings : {1}".format(_str_func, mSettings))
            
            _d = MODULECONTROL.register(mSettings,
                                        addDynParentGroup = False,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ")
            
            mSettings = _d['mObj']
            ml_controlsAll.append(mSettings)
            
        
            
        mControlBall = mRigNull.getMessageAsMeta('controlBall')
        #controlBall ================================================================================
        if mControlBall:
            log.debug("|{0}| >> Found ball : {1}".format(_str_func, mControlBall))
            
            _d = MODULECONTROL.register(mControlBall,
                                        addDynParentGroup = 0,
                                        #addSDKGroup=b_sdk,
                                        #addSDKGroup=True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ")
            
            mControlBall = _d['mObj']
            ml_controlsAll.append(mControlBall)
                
                
        if self.str_ballSetup != 'fixed':#==============================================================
            #FK ========================================================================================    
            log.debug("|{0}| >> Found fk : {1}".format(_str_func, mControlFK))
            
            _d = MODULECONTROL.register(mControlFK,
                                        addSDKGroup=b_sdk,                                    
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True)
            
            
            mControlFK = _d['mObj']
            mControlFK.addAttr('cgmControlDat','','string')
            mControlFK.cgmControlDat = {'tags':['fk']}
            
            ml_controlsAll.append(mControlFK)
            if mBlendJoint:
                self.atUtils('get_switchTarget', mControlFK, mBlendJoint)
                    
            #ik ========================================================================================
            if mControlIK:
                log.debug("|{0}| >> Found ik : {1}".format(_str_func, mControlIK))
                
                _d = MODULECONTROL.register(mControlIK,
                                            addDynParentGroup = True,
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = True,
                                            **d_controlSpaces)
                
                mControlIK = _d['mObj']
                ml_controlsAll.append(mControlIK)
                self.atUtils('get_switchTarget', mControlIK, mBlendJoint)
                
            
            
        mControlIKDirect = mRigNull.getMessageAsMeta('controlIKDirect')
        if mControlIKDirect:
            log.info("|{0}| >> Found ik direct : {1}".format(_str_func, mControlIKDirect))
            
            _d = MODULECONTROL.register(mControlIKDirect,
                                        addDynParentGroup = False,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True)
            
            #mControl= _d['mObj']
            ml_controlsAll.append( _d['mObj'])
            for mShape in _d['mObj'].getShapes(asMeta=True):
                ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))            
            
        #controlIKDirect
        
        #>> Direct Controls ==================================================================================
        log.debug("|{0}| >> Direct Eye controls...".format(_str_func))
        
        #ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        ml_controlsAll.extend([mDirect])
        
        for i,mObj in enumerate([mDirect]):
            d_buffer = MODULECONTROL.register(mObj,
                                              typeModifier='direct',
                                              mirrorSide= self.d_module['mirrorDirection'],
                                              mirrorAxis="translateX,rotateY,rotateZ",
                                              makeAimable = False)
    
            mObj = d_buffer['instance']
            ATTR.set_hidden(mObj.mNode,'radius',True)        
            if mObj.hasAttr('cgmIterator'):
                ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                
            for mShape in mObj.getShapes(asMeta=True):
                ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
        log.debug(cgmGEN._str_subLine)        

        
        if self.str_lidBuild:#Lid setup =======================================================================
            log.debug("|{0}| >> Lid setup: {1}".format(_str_func,self.str_lidBuild))
            
            cgmMeta.cgmAttr(mSettings.mNode,
                            'blink',attrType='float',
                            minValue=0,maxValue=1,
                            lock=False,keyable=True)
            cgmMeta.cgmAttr(mSettings.mNode,
                            'blinkHeight',attrType='float',
                            minValue=0,maxValue=1,
                            lock=False,keyable=True)            
            
            if self.str_lidBuild == 'clam':
                ml_handles = []
                for k in 'upr','lwr':
                    log.debug("|{0}| >> lid | {1}...".format(_str_func,k))
                    _key = '{0}LidHandle'.format(k)
                    mHandle = self.d_lidData[k]['mHandle']
                    mRig = self.d_lidData[k]['mRig']
                    
                    MODULECONTROL.register(mHandle,
                                           addSDKGroup=b_sdk,                                           
                                           mirrorSide= self.d_module['mirrorDirection'],
                                           mirrorAxis="translateX,rotateY,rotateZ")
                    
                    d_buffer = MODULECONTROL.register(mRig,
                                           typeModifier='direct',
                                           mirrorSide= self.d_module['mirrorDirection'],
                                           mirrorAxis="translateX,rotateY,rotateZ",
                                           makeAimable = False)
                    mObj = d_buffer['instance']
                    ATTR.set_hidden(mObj.mNode,'radius',True)        
                    if mObj.hasAttr('cgmIterator'):
                        ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                        
                    for mShape in mObj.getShapes(asMeta=True):
                        ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                        
                    ml_controlsAll.extend([mHandle,mRig])
                    mHandle.addAttr('cgmControlDat','','string')
                    mHandle.cgmControlDat = {'tags':['ik']}
                    ml_handles.append(mHandle)
                    
                mRigNull.msgList_connect('handleJoints',ml_handles)
                    
            else:
                #Handles ================================================================================
                log.debug("|{0}| >> Handles...".format(_str_func)+ '-'*80)
                ml_segmentHandles = []
                for k,d in self.md_handles.iteritems():
                    log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
                    for side,ml in d.iteritems():
                        log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                        for i,mHandle in enumerate(ml):
                            log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                            _d = MODULECONTROL.register(mHandle,
                                                        addSDKGroup=b_sdk,                                                        
                                                        mirrorSide= self.d_module['mirrorDirection'],
                                                        mirrorAxis="translateX,rotateY,rotateZ",
                                                        makeAimable = False)
                            
                            ml_controlsAll.append(_d['mObj'])
                            ml_segmentHandles.append(_d['mObj'])
                            """
                            if side == 'right':
                                mTarget = d['left'][i]
                                log.debug("|{0}| >> mirrorControl connect | {1} <<>> {2}".format(_str_func, mHandle.mNode, mTarget.mNode))
                                mHandle.doStore('mirrorControl',mTarget)
                                mTarget.doStore('mirrorControl',mHandle)"""
                                
                mRigNull.msgList_connect('handleJoints',ml_segmentHandles)
                
                #Direct ================================================================================
                log.debug("|{0}| >> Direct...".format(_str_func)+ '-'*80)
                _side = self.d_module['direction']
                
                for k,d in self.md_directJoints.iteritems():
                    log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
                    for side,ml in d.iteritems():
                        log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                        for i,mHandle in enumerate(ml):
                            log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                            
                            
                            _d = MODULECONTROL.register(mHandle,
                                                        typeModifier='direct',
                                           mirrorSide= self.d_module['mirrorDirection'],
                                                        mirrorAxis="translateX,rotateY,rotateZ",
                                                        makeAimable = False)                            
                            mObj = _d['mObj']
                        
                            ml_controlsAll.append(_d['mObj'])
                        
                            if mObj.hasAttr('cgmIterator'):
                                ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                            for mShape in mObj.getShapes(asMeta=True):
                                ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                
                
            
            if self.v_lidBuild:
                if mBlock.lidFanLwr or mBlock.lidFanUpr:
                    l_toDo = []
                    if mBlock.lidFanUpr:
                        l_toDo.append('uprFanCenter')
                    if mBlock.lidFanLwr:
                        l_toDo.append('lwrFanCenter')
                        
                    for k in l_toDo:
                        log.info("|{0}| >> lid fan handle| {1}...".format(_str_func,k))                      
                        _key = '{0}LidHandle'.format(k)
                        
                        mHandle = self.d_lidData[k]['mHandle']
                        mRig = self.d_lidData[k]['mRig']
                        
                        MODULECONTROL.register(mHandle,
                                               #addSDKGroup=b_sdk,                                           
                                               mirrorSide= self.d_module['mirrorDirection'],
                                               mirrorAxis="translateX,rotateY,rotateZ")
                        
                        d_buffer = MODULECONTROL.register(mRig,
                                               typeModifier='direct',
                                               mirrorSide= self.d_module['mirrorDirection'],
                                               mirrorAxis="translateX,rotateY,rotateZ",
                                               makeAimable = False)
                        
                        mObj = d_buffer['instance']
                        ATTR.set_hidden(mObj.mNode,'radius',True)        
                        if mObj.hasAttr('cgmIterator'):
                            ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                            
                        for mShape in mObj.getShapes(asMeta=True):
                            ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                            
                        ml_controlsAll.extend([mHandle,mRig])
                        mHandle.addAttr('cgmControlDat','','string')
                        mHandle.cgmControlDat = {'tags':['ik']}
                        #ml_handles.append(mHandle)              
                                
                                

        mPupil = mRigNull.getMessageAsMeta('controlPupil')
        #mPupil ================================================================================
        if mPupil:
            log.debug("|{0}| >> Found pupil : {1}".format(_str_func, mPupil))
            
            _d = MODULECONTROL.register(mPupil,
                                        addDynParentGroup = 0,
                                        addSDKGroup=b_sdk,
                                        #addSDKGroup=True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ")
            
            mPupil = _d['mObj']
            ml_controlsAll.append(mPupil)
            
        mIris = mRigNull.getMessageAsMeta('controlIris')
        #mIris ================================================================================
        if mIris:
            log.debug("|{0}| >> Found iris : {1}".format(_str_func, mIris))
            
            _d = MODULECONTROL.register(mIris,
                                        addDynParentGroup = 0,
                                        addSDKGroup=b_sdk,
                                        #addSDKGroup=True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ")
            
            mIris = _d['mObj']
            ml_controlsAll.append(mIris)        
            
            
        mControlSlideEye = mRigNull.getMessageAsMeta('controlSlideEye')
        #mControlSlideEye ================================================================================
        if mControlSlideEye:
            log.debug("|{0}| >> Found slideEye : {1}".format(_str_func, mControlSlideEye))
            
            _d = MODULECONTROL.register(mControlSlideEye,
                                        addDynParentGroup = 1,
                                        #addSDKGroup=True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ")
            
            mControlSlideEye = _d['mObj']
            ml_controlsAll.append(mControlSlideEye)
            
            ml_controlsAll.append( _d['mObj'])
            for mShape in _d['mObj'].getShapes(asMeta=True):
                ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))                        
            
            
        mControlHighlight = mRigNull.getMessageAsMeta('controlHighlight')
        #mControlHighlight ================================================================================
        if mControlHighlight:
            log.debug("|{0}| >> Found highlight : {1}".format(_str_func, mControlHighlight))
            
            _d = MODULECONTROL.register(mControlHighlight,
                                        addDynParentGroup = 1,
                                        #addSDKGroup=True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ")
            
            mControlHighlight = _d['mObj']
            ml_controlsAll.append(mControlHighlight)
            
            
        #Close out...
        mHandleFactory = mBlock.asHandleFactory()
        for mCtrl in ml_controlsAll:
            ATTR.set(mCtrl.mNode,'rotateOrder',self.ro_base)
            
            if mCtrl.hasAttr('radius'):
                ATTR.set(mCtrl.mNode,'radius',0)        
                ATTR.set_hidden(mCtrl.mNode,'radius',True)        
            
            ml_pivots = mCtrl.msgList_get('spacePivots')
            if ml_pivots:
                log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
                for mPivot in ml_pivots:
                    mHandleFactory.color(mPivot.mNode, controlType = 'sub')            

        mRigNull.msgList_connect('controlsFace',ml_controlsAll)
        mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        mRigNull.moduleSet.extend(ml_controlsAll)
        mRigNull.faceSet.extend(ml_controlsAll)
        
    except Exception,error:
        cgmGEN.cgmExceptCB(Exception,error,msg=vars())


@cgmGEN.Timer
def rig_frame(self):
    _short = self.d_block['shortName']
    _str_func = ' rig_rigFrame'
    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    if self.str_ballSetup == 'fixed':#===================================================================
        log.debug("|{0}| >> no setup".format(_str_func))            
        return True

    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mDeformNull
    mModule = self.mModule
    _str_rigNull = mRigNull.mNode
    
    mControlFK = mRigNull.getMessageAsMeta('fkEye')
    mJointFK = mControlFK
    mJointIK = mRigNull.getMessageAsMeta('ikEye')
    mControlIK = mRigNull.getMessageAsMeta('controlIK')
    mSettings = mRigNull.getMessageAsMeta('settings')
    mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
    mDirect = mRigNull.getMessageAsMeta('directEye')
    mRigRoot = mRigNull.getMessageAsMeta('rigRoot')
    mBallControl = mRigNull.getMessageAsMeta('controlBall')
    
    if mRigRoot:
        mRootParent = mRigRoot
    ml_joints = [mJointFK,mJointIK,mBlendJoint,mSettings,mDirect]
    
    #pprint.pprint(vars())
    
    log.debug("|{0}| >> Adding to attach driver...".format(_str_func))
    self.mDeformNull.p_parent = self.md_dynTargetsParent['attachDriver'].mNode    
    if mSettings:
        mSettings.masterGroup.p_parent = self.mDeformNull
    
    if mBallControl:
        mBallRoot = mBallControl
    else:
        mBallRoot = mSettings
        
    """
    #Mid IK trace ------------------------------------------------------
    log.debug("|{0}| >> eye track Crv".format(_str_func))
    trackcrv= CORERIG.create_at(l_pos=[mDirect.p_position,
                                       mBlock.getPositionByAxisDistance('z+',
                                       self.f_sizeAvg * 2)],#ml_handleJoints[1]],
                                create='curveLinear',
                                baseName = '{0}_eyeTrack'.format(self.d_module['partName']))

    
    mTrackCrv = mDirect.doCreateAt(setClass=True)
    CORERIG.shapeParent_in_place(mTrackCrv,trackcrv,False)
    mTrackCrv.p_parent = mSettings
    mHandleFactory = mBlock.asHandleFactory()
    mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')
    
    for s in mTrackCrv.getShapes(asMeta=True):
        s.overrideEnabled = 1
        s.overrideDisplayType = 2
    #mTrackCrv.doConnectIn('visibility',"{0}.v".format(mIKGroup.mNode))    
    mc.orientConstraint(mDirect.mNode,mTrackCrv.mNode)
    """


    if mBlock.ikSetup:
        mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK'
                                     )    
        #Aim setup ---------------------------------------------------------------
        log.debug("|{0}| >> Aim setup...".format(_str_func, mControlIK))    
        
        if not self.b_eyeSlide:#IK direct shape... -------------------------------------------
            mIKTarget = mJointIK.masterGroup
        else:
            mIKTarget = mJointIK
            
        mc.aimConstraint(mControlIK.mNode,
                         mIKTarget.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = self.d_orientation['vectorAim'],
                         upVector = self.d_orientation['vectorUp'],
                         worldUpVector = self.d_orientation['vectorUp'],
                         worldUpObject = mSettings.mNode,
                         worldUpType = 'objectRotation' )
        
        
        #>>> Setup a vis blend result
        mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
        mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
    
        NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                             mPlug_IKon.p_combinedName,
                                             mPlug_FKon.p_combinedName)
    
        #IK...
        mIKGroup = mSettings.doCreateAt()
        mIKGroup.doStore('cgmName',self.d_module['partName'])
        mIKGroup.doStore('cgmTypeModifier','ik')
        mIKGroup.doName()
        mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
    
        mIKGroup.parent = mBallRoot
        mControlIK.masterGroup.parent = mIKGroup
        mIKTarget.p_parent = mIKGroup
        
        #FK...
        FKGroup = mSettings.doCreateAt()
        FKGroup.doStore('cgmName',self.d_module['partName'])        
        FKGroup.doStore('cgmTypeModifier','FK')
        FKGroup.doName()
        mPlug_FKon.doConnectOut("{0}.visibility".format(FKGroup.mNode))
    
        FKGroup.parent = mBallRoot
        mControlFK.masterGroup.parent = FKGroup        
        
        
    #Setup blend ----------------------------------------------------------------------------------
    log.debug("|{0}| >> blend setup...".format(_str_func))
      
    if self.b_scaleSetup :
        log.debug("|{0}| >> scale blend chain setup...".format(_str_func))    
        
        if mBlock.ikSetup:
            RIGCONSTRAINT.blendChainsBy(mJointFK,mJointIK,mBlendJoint,
                                        driver = mPlug_FKIK.p_combinedName,
                                        l_constraints=['point','orient','scale'])
            
        for mJnt in ml_joints:
            mJnt.segmentScaleCompensate = False
            
            
    elif mBlock.ikSetup:
        #Setup blend ----------------------------------------------------------------------------------
        RIGCONSTRAINT.blendChainsBy(mJointFK,mJointIK,mBlendJoint,
                                    driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])

    if mBlendJoint:
        mBlendJoint.p_parent = mBallRoot
        
        
    if self.str_lidBuild in ['full']:
        log.debug("|{0}| >> lid setup...".format(_str_func)+ '-'*40)
        
        #Lid handles ------------------------------------------------------
        log.debug("|{0}| >> lid handles...".format(_str_func)+ '-'*20)
        
        log.debug("|{0}| >> sort handles".format(_str_func)+ '-'*20)
        mInnerCorner = self.md_handles['lidUpr']['inner'][0]
        mOuterCorner = self.md_handles['lidUpr']['outer'][0]
        mUprCenter = self.md_handles['lidUpr']['center'][0]
        mLwrCenter = self.md_handles['lidLwr']['center'][0]
        
        ml_uprInner = self.md_handles['lidUpr']['inner'][1:]
        ml_lwrInner = self.md_handles['lidLwr']['inner']
        
        for ml in ml_uprInner,ml_lwrInner:
            ml.reverse()
        
        ml_uprLid = self.md_handles['lidUpr']['outer'][1:] + ml_uprInner#self.md_handles['lidUpr']['inner'][1:]
        ml_lwrLid = self.md_handles['lidLwr']['outer'] + ml_lwrInner#self.md_handles['lidLwr']['inner']
        ml_uprChain = self.md_handles['lidUpr']['outer'][1:] + [mUprCenter] + ml_uprInner#self.md_handles['lidUpr']['inner'][1:]
        ml_lwrChain = self.md_handles['lidLwr']['outer'] + [mLwrCenter] + ml_lwrInner#self.md_handles['lidLwr']['inner']

            
        for mControl in mUprCenter,mLwrCenter,mOuterCorner,mInnerCorner:
            mControl.masterGroup.p_parent = mRootParent
        
        #side handles ---------------------------
        #First we're going to attach our handles to a surface to ge general placement. Then we're going to try
        d_lidSetup = {'upr':{'ml_chain':[mOuterCorner] + ml_uprChain + [mInnerCorner],
                               'mInfluences':[mOuterCorner,mUprCenter,mInnerCorner],
                               'mHandles':ml_uprLid},
                      'lwr':{'ml_chain':[mOuterCorner] + ml_lwrChain + [mInnerCorner],
                               'mInfluences':[mOuterCorner,mLwrCenter,mInnerCorner],
                               'mHandles':ml_lwrLid}}        
        """
        d_lidSetup = {'upr':{'ml_chain':[mOuterCorner] + ml_uprChain + [mInnerCorner],
                               'mInfluences':[mOuterCorner.uprInfluence,mUprCenter,mInnerCorner.uprInfluence],
                               'mHandles':ml_uprLid},
                      'lwr':{'ml_chain':[mOuterCorner] + ml_lwrChain + [mInnerCorner],
                               'mInfluences':[mOuterCorner.lwrInfluence,mLwrCenter,mInnerCorner.lwrInfluence],
                               'mHandles':ml_lwrLid}}"""
        
        for k,d in d_lidSetup.iteritems():
            #need our handle chain to make a ribbon
            ml_chain = d['ml_chain']
            mInfluences = d['mInfluences']
            l_surfaceReturn = IK.ribbon_createSurface([mJnt.mNode for mJnt in ml_chain],
                                            'z+')
            
            mControlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
            mControlSurface.addAttr('cgmName',"{0}HandlesFollow_lid".format(k),attrType='string',lock=True)    
            mControlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
            mControlSurface.doName()
            mControlSurface.p_parent = _str_rigNull
            
            
            log.debug("|{0}| >> Skinning surface: {1}".format(_str_func,mControlSurface))
            mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mObj.mNode for mObj in mInfluences],
                                                                  mControlSurface.mNode,
                                                                  tsb=True,nurbsSamples=4,
                                                                  maximumInfluences = 3,
                                                                  normalizeWeights = 1,dropoffRate=10.0),
                                                  'cgmNode',
                                                  setClass=True)
        
            mSkinCluster.doStore('cgmName', mControlSurface)
            mSkinCluster.doName()

            for mHandle in d['mHandles']:
                mHandle.masterGroup.p_parent = mRootParent#mFollowParent
                _resAttach = RIGCONSTRAINT.attach_toShape(mHandle.masterGroup.mNode,
                                                          mControlSurface.mNode,
                                                          'conPoint')
                TRANS.parent_set(_resAttach[0],_str_rigNull)
                
                
            
            for mObj in [mControlSurface]:
                mObj.overrideEnabled = 1
                cgmMeta.cgmAttr(_str_rigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(_str_rigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
                mObj.parent = mRigNull
                
                

            
            ml_lwrInner = self.md_handles['lidLwr']['inner']
            ml_lwrOuter = self.md_handles['lidLwr']['outer']
            d_lidAim = {'upr':{'inner':self.md_handles['lidUpr']['inner'][1:],
                               'outer':self.md_handles['lidUpr']['outer'][1:]},
                        'lwr':{'inner':self.md_handles['lidLwr']['inner'],
                               'outer':self.md_handles['lidLwr']['outer']}}
            
            
            for tag,sectionDat in d_lidAim.iteritems():
                for side,sideDat in sectionDat.iteritems():
                    if side == 'inner':
                        _aim = [-1,0,0]
                        mCorner = mInnerCorner
                        mInfluence = mInnerCorner.getMessageAsMeta('{0}Influence'.format(tag))
                        _tar=sideDat[0].mNode
                    else:
                        _aim = [1,0,0]
                        mCorner = mOuterCorner
                        mInfluence = mOuterCorner.getMessageAsMeta('{0}Influence'.format(tag))
                        
                        _tar=sideDat[0].mNode
                        
                    mAimGroup = mInfluence.doGroup(True,True,
                                                asMeta=True,
                                                typeModifier = 'aim',
                                                setClass='cgmObject')

                    mc.aimConstraint(_tar,
                                     mAimGroup.mNode,
                                     maintainOffset = 1, weight = 1,
                                     aimVector = _aim,
                                     upVector = [0,1,0],
                                     worldUpVector = [0,1,0],
                                     worldUpObject = mCorner.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )                    
                        
                    """for i,mJnt in enumerate(sideDat):
                        _mode = None
                        
                        if not i:
                            _tar = _corner
                        else:
                            _tar=sideDat[i-1].mNode
                            
                        mAimGroup = mJnt.doGroup(True,True,
                                                 asMeta=True,
                                                 typeModifier = 'aim',
                                                 setClass='cgmObject')

                        mc.aimConstraint(_tar,
                                         mAimGroup.mNode,
                                         maintainOffset = 1, weight = 1,
                                         aimVector = _aim,
                                         upVector = [0,1,0],
                                         worldUpVector = [0,1,0],
                                         worldUpObject = mJnt.masterGroup.mNode,
                                         worldUpType = 'objectRotation' )"""
        
        """
        #Lid Corner influences ------------------------------------------------------
        log.debug("|{0}| >> lid corner influences...".format(_str_func)+ '-'*20)
        for i,mHandle in enumerate([mOuterCorner,mInnerCorner]):
            mPlug_upr = cgmMeta.cgmAttr(mHandle,'twistUpper',value = 0,
                                          attrType='float',defaultValue = 0.0,keyable = True,hidden = False)
            mPlug_lwr = cgmMeta.cgmAttr(mHandle,'twistLower',value = 0,
                                          attrType='float',defaultValue = 0.0,keyable = True,hidden = False)
            
            if not i:
                _aim = [-1,0,0]
            else:
                _aim = [1,0,0]
                
            mUprInfluence = mHandle.uprInfluence
            mLwrInfluence = mHandle.lwrInfluence
            
            for ii,mInfl in enumerate([mUprInfluence,mLwrInfluence]):
                if not ii:
                    _tar = mUprCenter.mNode
                else:
                    _tar = mLwrCenter.mNode
                    
                mAimGroup = mInfl.doGroup(True,True,
                                         asMeta=True,
                                         typeModifier = 'aim',
                                         setClass='cgmObject')
                mc.aimConstraint(_tar,
                                 mAimGroup.mNode,
                                 maintainOffset = 1, weight = 1,
                                 aimVector = _aim,
                                 upVector = [0,1,0],
                                 worldUpVector = [0,1,0],
                                 worldUpObject = mHandle.mNode,
                                 worldUpType = 'objectRotation' )                    
                
            
            
            
            if not i:# ['outer']:# and k not in ['inner','outer']:
                mPlug_upr.doConnectOut("{0}.rz".format(mHandle.uprInfluence.mNode))                 
                mPlug_lwr.doConnectOut("{0}.rz".format(mHandle.lwrInfluence.mNode))                 
            else:  
                str_arg1 = "{0}.rz = -{1}".format(mHandle.uprInfluence.mNode,
                                                  mPlug_upr.p_combinedShortName)                
                str_arg2 = "{0}.rz = -{1}".format(mHandle.lwrInfluence.mNode,
                                                 mPlug_lwr.p_combinedShortName)
                for a in str_arg1,str_arg2:
                    NODEFACTORY.argsToNodes(a).doBuild()"""
        
    return

@cgmGEN.Timer
def rig_highlightSetup(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_highlightSetup'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)

    if self.str_highlightSetup is not 'none':
        log.debug("|{0}| >> No highlight setup...".format(_str_func))
        return True
    
    _short = self.d_block['shortName']    
    _lidSetup = self.str_lidBuild
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mSettings = mRigNull.settings
    mRootParent = self.mConstrainNull
    mModule = self.mModule
    _jointOrientation = self.d_orientation['str']
    _side = mBlock.atUtils('get_side')
    
    mRigRoot = mRigNull.getMessageAsMeta('rigRoot')
    mHighLight = mRigNull.getMessageAsMeta('controlHighlight')
    mControlFK = mRigNull.getMessageAsMeta('fkEye')
    mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
    
    mHighLight.masterGroup.p_parent = mRigRoot
    
    
    mPlug_highlight = cgmMeta.cgmAttr(mSettings,"highlight",attrType='bool',value = True, keyable=True,hidden=False)
    mPlug_highlight.doConnectOut('{0}.scale'.format(mHighLight.masterGroup.mNode))
    

    if  mBlock.highlightSetup:
        log.debug("|{0}| >> sdk highlight...".format(_str_func))
        
        mHighlightDriver = mBlock.prerigNull.getMessageAsMeta('eyeHighlightJoint').getMessageAsMeta('driverJoint')
        mHighlightDriver.p_parent = mHighLight.masterGroup
        
        _d_toDo = {'hl_xFollow':.25,
                   'hl_xOffset':-15,
                   'hl_yFollow':.15,
                   'hl_yOffset':10}
        
        for k,v in _d_toDo.iteritems():
            cgmMeta.cgmAttr(mHighlightDriver,k,attrType = 'float', value = v,
                            hidden = False,keyable=False)
            
        if mBlendJoint:
            mBlend = mBlendJoint
        else:
            mBlend = mControlFK
            
        #mSDK = mHighLight.sdkGroup
        
        for k in 'x','y':
            mPlug_mult = cgmMeta.cgmAttr(mHighlightDriver,"res_hlFollowMult",attrType='float',keyable=False,hidden=False)
            _arg1 = "{0} = {1}.rotate{2} * {3}.hl_{4}Follow".format(mPlug_mult.p_combinedShortName,
                                                                    mBlend.mNode,
                                                                    k.upper(),
                                                                    mHighlightDriver.mNode,
                                                                    k)
            _arg2 = "{0}.r{3} = {1} + {2}.hl_{3}Offset".format(mHighlightDriver.mNode,
                                                               mPlug_mult.p_combinedShortName,
                                                               mHighlightDriver.mNode,
                                                               k)
            
            for _arg in _arg1,_arg2:
                NODEFACTORY.argsToNodes(_arg).doBuild()    
    
    

def create_clamBlinkCurves(self, ml_uprSkinJoints = None, ml_lwrSkinJoints = None):
    _short = self.d_block['shortName']
    _str_func = 'create_clamBlinkCurves'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mConstrainNull    
    mSettings = mRigNull.settings
    
    
    ml_curves = []
    
    log.debug(mRigNull.uprLidCurve)
    log.debug(mRigNull.lwrLidCurve)
    log.debug(mSettings)
    
    mUprLidDriven = mRigNull.uprLidCurve
    mLwrLidDriven = mRigNull.lwrLidCurve
    
    mUprLidDriven.addAttr('cgmName','uprLid',lock=True)
    mLwrLidDriven.addAttr('cgmName','LwrLid',lock=True)
    
    md = {'upr':{'mDriven':mUprLidDriven},
          'lwr':{'mDriven':mLwrLidDriven}}
    
    for mObj in mUprLidDriven,mLwrLidDriven:
        mObj.p_parent = False
        mObj.addAttr('cgmTypeModifier','driven',lock=True)
        mObj.doName()
        ml_curves.append(mObj)
        
    
    for tag in ['upr','lwr']:
        log.debug("|{0}| >> {1} curve create...".format(_str_func,tag))
        
        _d = md[tag]
        
        mBlink = _d['mDriven'].doDuplicate(po = False)
        mBlink.addAttr('cgmTypeModifier','blink',lock=True)
        mBlink.doName()
        ml_curves.append(mBlink)
        _d['mBlink'] = mBlink
        
        mDriver = _d['mDriven'].doDuplicate(po = False)
        mDriver.addAttr('cgmTypeModifier','driver',lock=True)
        mDriver.doName()
        ml_curves.append(mDriver)
        _d['mDriver'] = mDriver
        
    
    #Smart Blink curve--------------------------------------------------------
    log.debug("|{0}| >> smart blink curve create...".format(_str_func))
    
    mSmartBlink = mUprLidDriven.doDuplicate(po=False)
    mSmartBlink.addAttr('cgmName','smartBlink',lock=True)    
    mSmartBlink.doName()
    ml_curves.append(mSmartBlink)
    
    md['mSmart'] = mSmartBlink
    
    #Wire--------------------------------------------------------
    _uprDriver = md['upr']['mDriver'].mNode
    _uprDriven = md['upr']['mDriven'].mNode
    _lwrDriver = md['lwr']['mDriver'].mNode
    _lwrDriven = md['lwr']['mDriven'].mNode
        
    log.debug("|{0}| >> wire deformers...".format(_str_func))    
    _l_return = mc.wire(_uprDriven,
                        w=_uprDriver, 
                        gw = False, en = 1, ce = 0, li =0)
    mUprWire = cgmMeta.cgmNode(_l_return[0])
    mUprWire.doStore('cgmName',_uprDriven)
    mUprWire.doName()
    
    _l_return = mc.wire(_lwrDriven,
                        w = _lwrDriver, 
                        gw = False, en = 1, ce = 0, li =0)
    mLwrWire = cgmMeta.cgmNode(_l_return[0])
    mLwrWire.doStore('cgmName',_lwrDriven,attrType = 'msg')
    mLwrWire.doName()
    
    #mUprWire.parent = mRigNull
    #mLwrWire.parent = mRigNull
    #.dropoffDistance[0] Need to set dropoff distance
    ATTR.set(mUprWire.mNode,'dropoffDistance[0]',50)
    ATTR.set(mLwrWire.mNode,'dropoffDistance[0]',50)
    
    
    #Skin our curves --------------------------------------------------------
    log.debug("|{0}| >> skin curves...".format(_str_func))
    if not ml_uprSkinJoints:
        ml_uprSkinJoints = [self.d_lidData['upr']['mHandle']]#ml_uprLidHandles
        
    if not ml_lwrSkinJoints:
        ml_lwrSkinJoints = [self.d_lidData['lwr']['mHandle']]#[ml_uprLidHandles[0]] + ml_lwrLidHandles + [ml_uprLidHandles[-1]]
    md_skinSetup = {'upr':{'ml_joints':ml_uprSkinJoints,'mi_crv':md['upr']['mDriver']},
                    'lwr':{'ml_joints':ml_lwrSkinJoints,'mi_crv':md['lwr']['mDriver']}}
    
    for k in md_skinSetup.keys():
        d_crv = md_skinSetup[k]
        str_crv = d_crv['mi_crv'].p_nameShort
        l_joints = [mi_obj.p_nameShort for mi_obj in d_crv['ml_joints']]
        log.debug(" %s | crv : %s | joints: %s"%(k,str_crv,l_joints))
        try:
            mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mi_obj.mNode for mi_obj in d_crv['ml_joints']],
                                                          d_crv['mi_crv'].mNode,
                                                          tsb=True,
                                                          maximumInfluences = 3,
                                                          normalizeWeights = 1,dropoffRate=2.5)[0])
        except Exception,error:raise StandardError,"skinCluster : %s"%(error)  	    
    
    
    
    #blendshape smart blink--------------------------------------------------------
    log.debug("|{0}| >> blendshape smart blink...".format(_str_func))
    
    _str_bsNode = mc.blendShape([_uprDriver,_lwrDriver],mSmartBlink.mNode)[0]
    mBsNode = cgmMeta.asMeta(_str_bsNode,'cgmNode',setClass=True)
    mBsNode.doStore('cgmName',mSmartBlink)
    mBsNode.doName()

    mPlug_height = cgmMeta.cgmAttr(mSettings,'blinkHeight',attrType = 'float', defaultValue=.1, minValue = 0, maxValue = 1)
    import cgm.lib.deformers as deformers
    l_bsAttrs = deformers.returnBlendShapeAttributes(mBsNode.mNode)
    log.debug(l_bsAttrs)
    d_return = NODEFACTORY.createSingleBlendNetwork([mSettings.mNode,'blinkHeight'],
                                              [mSettings.mNode,'blinkHeight_upr'],
                                              [mSettings.mNode,'blinkHeight_lwr'],
                                              keyable=True)	
    #Connect                                  
    d_return['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mBsNode.mNode,l_bsAttrs[0]))
    d_return['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mBsNode.mNode,l_bsAttrs[1]))
    
    #Build our blink match wire deformers--------------------------------------------------------
    log.debug("|{0}| >> Build our blink match wire deformers...".format(_str_func))
    
    mPlug_height.value = 0	    
    _l_return = mc.wire(md['lwr']['mBlink'].mNode, w = mSmartBlink.mNode, gw = False, en = 1, ce = 0, li =0)
    mi_lwrBlinkWire = cgmMeta.cgmNode(_l_return[0])
    mi_lwrBlinkWire.doStore('cgmName',_lwrDriven,attrType = 'msg')
    mi_lwrBlinkWire.addAttr('cgmTypeModifier','blink')	    
    mi_lwrBlinkWire.doName()
    mc.setAttr("%s.scale[0]"%mi_lwrBlinkWire.mNode,0)
    mc.setAttr("%s.dropoffDistance[0]"%mi_lwrBlinkWire.mNode,50)

    mPlug_height.value = 1
    _l_return = mc.wire(md['upr']['mBlink'].mNode, w = mSmartBlink.mNode, gw = False, en = 1, ce = 0, li =0)
    mi_uprBlinkWire = cgmMeta.cgmNode(_l_return[0])
    mi_uprBlinkWire.doStore('cgmName',_uprDriven,attrType = 'msg')
    mi_uprBlinkWire.addAttr('cgmTypeModifier','blink')	    
    mi_uprBlinkWire.doName()
    mc.setAttr("%s.scale[0]"%mi_uprBlinkWire.mNode,0)
    mc.setAttr("%s.dropoffDistance[0]"%mi_uprBlinkWire.mNode,50)

    mPlug_height.value = .1#back to default

    #mi_smartBlinkCrv.parent = mRigNull
    
    #blendshape upr/lwr --------------------------------------------------------------
    log.debug("|{0}| >> blendshape upr/lwr...".format(_str_func))
    
    mPlug_blink = cgmMeta.cgmAttr(mSettings,'blink',attrType = 'float', keyable=True, minValue=0, maxValue=1, defaultValue=0)
    d_blendshapeBlink = {'upr':{'mi_target':md['upr']['mBlink'],'mi_driven':md['upr']['mDriven']},
                         'lwr':{'mi_target':md['lwr']['mBlink'],'mi_driven':md['lwr']['mDriven']}}
    for k in d_blendshapeBlink.keys():
        d_buffer = d_blendshapeBlink[k]
        mi_target = d_buffer['mi_target']
        mi_driven = d_buffer['mi_driven']
        _str_bsNode = mc.blendShape(mi_target.mNode,mi_driven.mNode)[0]
        mi_bsNode = cgmMeta.asMeta(_str_bsNode,'cgmNode',setClass=True)
        mi_bsNode.doStore('cgmName',mi_driven)
        mi_bsNode.doName()
        l_bsAttrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
        mPlug_blink.doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[0]))    


    self.fnc_connect_toRigGutsVis( ml_curves )
    
    for mWire in mi_lwrBlinkWire,mi_uprBlinkWire,mLwrWire,mUprWire:
        ml_curves.append( cgmMeta.asMeta( ATTR.get_driver(mWire.mNode,'baseWire[0]',True)))
    
    
    for mCrv in ml_curves:
        if mCrv in [ md['upr']['mDriver'], md['lwr']['mDriver'],mSmartBlink]:
            mCrv.p_parent = mRigNull
        else:
            mCrv.p_parent = mSettings
        
    self.md_blinkCurves = md
    self.ml_blinkCurves = ml_curves    
    return md,ml_curves

@cgmGEN.Timer
def create_lidFollow(self):
    _short = self.d_block['shortName']
    _str_func = 'create_lidFollow'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)
    
    _str_orientation = self.d_orientation['str']
    
    mRigNull = self.mRigNull
    mEyeJoint = mRigNull.getMessageAsMeta('blendEye') or mRigNull.getMessageAsMeta('fkEye')
    mSettings = mRigNull.settings
    
    #mPlug_autoFollow = cgmMeta.cgmAttr(mSettings,"autoFollow",attrType = 'float', value = 1.0,
    #                                   hidden = False,keyable=True,maxValue=1.0,minValue=0)	    
    #self.mPlug_autoFollow = mPlug_autoFollow
    
    mPlug_followUpr = cgmMeta.cgmAttr(mSettings,"lidFollowUpr",attrType = 'float', value = 1.0,
                                       hidden = False,keyable=True,maxValue=1.0,minValue=0)	    
    mPlug_followLwr = cgmMeta.cgmAttr(mSettings,"lidFollowLwr",attrType = 'float', value = 1.0,
                                       hidden = False,keyable=True,maxValue=1.0,minValue=0)
    
    self.mPlug_followUpr = mPlug_followUpr
    self.mPlug_followLwr = mPlug_followLwr
    
    mZeroLoc = mEyeJoint.doCreateAt()
    mZeroLoc.addAttr('cgmName','zero')
    mZeroLoc.doName()
    
    mZeroLoc.p_parent = mSettings
    
    md_dat = {}
    
    log.debug("|{0}| >> create nodes...".format(_str_func))    
    for k in 'upr','lwr':
        log.debug("|{0}| >> {1}...".format(_str_func,k))            
        _d = self.d_lidData[k]
        #mRoot = _d['mRoot']
        mHandle = _d['mHandle']
        
        mDriven = mZeroLoc.doDuplicate(po=False)
        mDriven.cgmName = "{0}Driven".format(k)
        mDriven.doName()
        
        md_dat[k] = {'mDriven':mDriven}
        
        mClamp = cgmMeta.cgmNode(nodeType='clamp')
        mClamp.doStore('cgmName',self.d_module['partName'])
        mClamp.addAttr('cgmTypeModifier',k)
        mClamp.doName()
        md_dat[k]['mClamp'] = mClamp

        if k == 'lwr':
            mRemap = cgmMeta.cgmNode(nodeType='remapValue')
            mRemap.doStore('cgmName',self.d_module['partName'])
            mRemap.addAttr('cgmTypeModifier','lwr')
            mRemap.doName()
            md_dat[k]['mRemap'] = mRemap
            
    #Upr wiring --------------------------------------------------------------   
    log.debug("|{0}| >> upr wiring...".format(_str_func)+'-'*40)
    _uprClamp = md_dat['upr']['mClamp'].mNode
    _uprLoc = md_dat['upr']['mDriven'].mNode
    
    log.debug("|{0}| >> upr up...".format(_str_func))
    mPlug_driverUp = cgmMeta.cgmAttr(mEyeJoint.mNode,"r{0}".format(_str_orientation[2]))
    mPlug_uprUpLimit = cgmMeta.cgmAttr(mSettings,"uprUpLimit",attrType='float',
                                       value=-60,keyable=False,hidden=False)
    mPlug_uprDnLimit = cgmMeta.cgmAttr(mSettings,"uprDnLimit",attrType='float',
                                       value=50,keyable=False,hidden=False)
    mPlug_driverUp.doConnectOut("{0}.inputR".format(_uprClamp))
    mPlug_uprDnLimit.doConnectOut("{0}.maxR".format(_uprClamp))
    mPlug_uprUpLimit.doConnectOut("{0}.minR".format(_uprClamp))
    mc.connectAttr("{0}.outputR".format(_uprClamp),
                   "{0}.r{1}".format(_uprLoc,_str_orientation[2]))

    self.mPlug_uprUpLimit = mPlug_uprUpLimit#store
    self.mPlug_uprDnLimit = mPlug_uprDnLimit#store		        
    
    log.debug("|{0}| >> upr out...".format(_str_func))
    
    mPlug_driverSide = cgmMeta.cgmAttr(mEyeJoint.mNode,"r{0}".format(_str_orientation[1]))
    mPlug_leftLimit = cgmMeta.cgmAttr(mSettings,"uprLeftLimit",value=20,defaultValue=20,attrType='float',keyable=False,hidden=False)
    mPlug_rightLimit = cgmMeta.cgmAttr(mSettings,"uprRightLimit",value=-20,defaultValue=-20,attrType='float',keyable=False,hidden=False)

    mPlug_driverSide.doConnectOut("{0}.inputG".format(_uprClamp))
    mPlug_leftLimit.doConnectOut("{0}.maxG".format(_uprClamp))
    mPlug_rightLimit.doConnectOut("{0}.minG".format(_uprClamp))
    mc.connectAttr("{0}.outputG".format(_uprClamp),"{0}.r{1}".format(_uprLoc,_str_orientation[1]))

    self.mPlug_leftLimit = mPlug_leftLimit
    self.mPlug_rightLimit = mPlug_rightLimit#store
    
    #lwr wiring --------------------------------------------------------------   
    log.debug("|{0}| >> lwr wiring...".format(_str_func))
    _lwrClamp = md_dat['lwr']['mClamp'].mNode
    _lwrLoc = md_dat['lwr']['mDriven'].mNode
    _lwrRemap = md_dat['lwr']['mRemap'].mNode
    
    mPlug_lwrUpLimit = cgmMeta.cgmAttr(mSettings,"lwrUpLimit",attrType='float',
                                       value=-26,keyable=False,hidden=False)
    mPlug_lwrDnLimit = cgmMeta.cgmAttr(mSettings,"lwrDnLimit",attrType='float',
                                       value=35,keyable=False,hidden=False)
    mPlug_lwrDnStart = cgmMeta.cgmAttr(mSettings,"lwrDnStart",attrType='float',
                                       value=5,keyable=False,hidden=False)    
    mPlug_driverUp.doConnectOut("{0}.inputValue".format(_lwrRemap))
    mPlug_lwrDnStart.doConnectOut("{0}.inputMin".format(_lwrRemap))

    md_dat['lwr']['mRemap'].inputMax = 50
    mPlug_lwrDnLimit.doConnectOut("{0}.outputLimit".format(_lwrRemap))
    mPlug_lwrDnLimit.doConnectOut("{0}.inputMax".format(_lwrRemap))
    mPlug_lwrDnLimit.doConnectOut("{0}.outputMax".format(_lwrRemap))

    ATTR.connect("{0}.outValue".format(_lwrRemap),"{0}.inputR".format(_lwrClamp))

    mPlug_lwrDnLimit.doConnectOut("{0}.maxR".format(_lwrClamp))
    mPlug_lwrUpLimit.doConnectOut("{0}.minR".format(_lwrClamp))
    ATTR.connect("{0}.outputR".format(_lwrClamp),
                 "{0}.r{1}".format(_lwrLoc,_str_orientation[2]))
    #ATTR.connect("{0}.outputG".format(_lwrClamp),
    #             "{0}.r{1}".format(_lwrLoc,_str_orientation[1]))

    self.mPlug_lwrUpLimit = mPlug_lwrUpLimit#store
    self.mPlug_lwrDnLimit = mPlug_lwrDnLimit#store
    self.mPlug_lwrDnStart = mPlug_lwrDnStart#store
    
    #Lwr left/right
    
    mPlug_driverSide = cgmMeta.cgmAttr(mEyeJoint.mNode,"r{0}".format(_str_orientation[1]))
    mPlug_leftLwrLimit = cgmMeta.cgmAttr(mSettings,"lwrLeftLimit",value=20,defaultValue=20,attrType='float',keyable=False,hidden=False)
    mPlug_rightLwrLimit = cgmMeta.cgmAttr(mSettings,"lwrRightLimit",value=-20,defaultValue=-20,attrType='float',keyable=False,hidden=False)

    mPlug_driverSide.doConnectOut("{0}.inputG".format(_lwrClamp))
    mPlug_leftLwrLimit.doConnectOut("{0}.maxG".format(_lwrClamp))
    mPlug_rightLwrLimit.doConnectOut("{0}.minG".format(_lwrClamp))
    mc.connectAttr("{0}.outputG".format(_lwrClamp),"{0}.r{1}".format(_lwrLoc,_str_orientation[1]))

    self.mPlug_leftLwrLimit = mPlug_leftLwrLimit
    self.mPlug_rightLwrLimit = mPlug_rightLwrLimit#store    
    
    #Contraints --------------------------------------------------------------   
    log.debug("|{0}| >> Contraints...".format(_str_func))
    #d_autolidBlend = NODEFACTORY.createSingleBlendNetwork(mPlug_autoFollow,
    #                                                      [mSettings.mNode,'resultAutoFollowOff'],
    #                                                      [mSettings.mNode,'resultAutoFollowOn'],
    #                                                      hidden = True,keyable=False)    
    
    d_followAttrs = {'upr':mPlug_followUpr,
                     'lwr':mPlug_followLwr}
    for k in 'upr','lwr':
        log.debug("|{0}| >> {1}...".format(_str_func,k))            
        _d = self.d_lidData[k]
        d_autolidBlend = NODEFACTORY.createSingleBlendNetwork(d_followAttrs[k],
                                                              [mSettings.mNode,'resultAutoFollow{0}Off'.format(k.capitalize())],
                                                              [mSettings.mNode,'resultAutoFollow{0}On'.format(k.capitalize())],
                                                              hidden = True,keyable=False)           
        
        #mRoot = _d['mRoot']
        mHandle = _d['mHandle']
        
        _const = mc.parentConstraint([mZeroLoc.mNode,
                                      md_dat[k]['mDriven'].mNode],
                                     mHandle.masterGroup.mNode,
                                     maintainOffset = True)[0]
        
        l_weightTargets = mc.parentConstraint(_const,q=True,weightAliasList = True)
        d_autolidBlend['d_result1']['mi_plug'].doConnectOut('%s.%s' % (_const,l_weightTargets[1]))
        d_autolidBlend['d_result2']['mi_plug'].doConnectOut('%s.%s' % (_const,l_weightTargets[0]))    
    
    
@cgmGEN.Timer
def rig_pupilIris(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_pupilIris'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    
    self.mOrb = False
    
    if not self.b_eyeSlide:
        log.debug("|{0}| >> no build...".format(_str_func))
        return    

    _short = self.d_block['shortName']    
    _lidSetup = self.str_lidBuild
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mSettings = mRigNull.settings
    
    mBall = mRigNull.controlBall
    
    mRootParent = self.mConstrainNull
    mModule = self.mModule
    _jointOrientation = self.d_orientation['str']
    _side = mBlock.atUtils('get_side')
    

    log.debug("|{0}| >> surfaceSlide orb dup...".format(_str_func))
    mOrb = mBlock.bbHelper.doDuplicate(po=False)
    mOrb.dagLock(False)
    mOrb.rx = 90
    mOrb.p_parent = mBall
    mOrb.rename("{0}_orb".format(self.d_module['partName']))
    mOrb.template=1
    
    self.mOrb = mOrb
    
    #Setup Iris/pupil drivers -----------------------------------------------------------
    mDirect = mRigNull.getMessageAsMeta('directEye')
    mControlSlideEye = mRigNull.getMessageAsMeta('controlSlideEye')
    mControlBall = mRigNull.getMessageAsMeta('controlBall')

    mLoc = False
    
    for s in ['iris','pupil']:
        #controlIris
        if self.__dict__['str_{0}Attach'.format(s)] == 'surfaceSlide':
            log.info("|{0}| >> surfaceSlide {1}...".format(_str_func,s))
            mControl = mRigNull.getMessageAsMeta('control{0}'.format(STR.capFirst(s)))
            if mControl:
                
                if not mLoc:
                    
                    if self.str_ballSetup != 'fixed':#============================================
                        mControlSlideEye.masterGroup.p_parent = mDirect
                    else:
                        mControlSlideEye.masterGroup.p_parent = mSettings#mControlBall#mDirect
                                        
                    mDriver = mControl.doCreateAt()
                    
                    _res = RIGCONSTRAINT.attach_toShape(mDriver.mNode,mOrb.mNode,None,
                                                        driver= mControlSlideEye)
                
                    md = _res[-1]
                    mFollicle = md['mFollicle']
                    
                    mLoc = mControl.doLoc()
                    mLoc.p_parent =mFollicle
                    mLoc.resetAttrs()
                    mLoc.tz = - self.v_offset
                    
                    for k in ['mDriverLoc','mFollicle']:
                        md[k].p_parent = mRigNull
                        md[k].v = False
                    
                    mDriver.p_parent = mFollicle
                    
                    mc.aimConstraint(mLoc.mNode,
                                     mDriver.mNode,
                                     maintainOffset = True, weight = 1,
                                     aimVector = [0,0,-1],
                                     upVector = [0,1,0],
                                     worldUpVector = [0,1,0],
                                     worldUpObject = mControlSlideEye.mNode,
                                     worldUpType = 'objectRotation' )    
                    
                self.md_driverJoints[s].p_parent = mDriver
                
                    #mJoint.p_position = md['mFollicle'].p_position
                mc.parentConstraint(self.md_driverJoints[s].mNode,
                                    mControl.masterGroup.mNode,maintainOffset=0)
                
                mScaleGroup = mControl.doGroup(True,True,asMeta=True,typeModifier = 'scale')
                
                mScaleGroup.doConnectIn('scale','{0}.scale'.format(mControlSlideEye.mNode))

        
    
    
        
@cgmGEN.Timer
def rig_lidSetup(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_lidSetup'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)

    if not self.v_lidBuild:
        log.debug("|{0}| >> No lid setup...".format(_str_func))
        return True
    
    _short = self.d_block['shortName']    
    _lidSetup = self.str_lidBuild
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mSettings = mRigNull.settings
    mRootParent = self.mConstrainNull
    mModule = self.mModule
    _jointOrientation = self.d_orientation['str']
    _side = mBlock.atUtils('get_side')
    mControlBall = mRigNull.getMessageAsMeta('controlBall')
    
    
    mOrb = self.mOrb

    if mBlock.lidFanLwr or mBlock.lidFanUpr:
        l_toDo_fan = []
        if mBlock.lidFanUpr:
            l_toDo_fan.append('upr')
        if mBlock.lidFanLwr:
            l_toDo_fan.append('lwr')    


    if _lidSetup:
        log.debug("|{0}| >>  Lid setup ... ".format(_str_func)+'-'*40)
        
        mUprRoot = None
        mLwrRoot = None
        
        if _lidSetup == 'clam':
            log.debug("|{0}| >>  clam ... ".format(_str_func))
            #First we need to make our new curves
            for k in 'upr','lwr':
                _d = self.d_lidData[k]                
                l_tags = ['inner',k,'outer']
                l_pos = []
                for tag in l_tags:
                    if tag == k:
                        l_pos.append(_d['mRig'].p_position)
                    else:
                        mHandle = mBlock.getMessageAsMeta("define{0}Helper".format(tag.capitalize()))
                        l_pos.append(mHandle.p_position)
                
                _crv = CORERIG.create_at(create='curve',l_pos = l_pos)
                mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
                mRigNull.connectChildNode(mCrv, k+'LidCurve','module')
                
            
            create_clamBlinkCurves(self)
            
            for k in 'upr','lwr':
                _d = self.d_lidData[k]
                mBlend = _d['mBlend']
                mRig = _d['mRig']
                mHandle = _d['mHandle']
                
                
                mHandle.masterGroup.p_parent = mSettings
                mTarget = mRig.doLoc()
                
                if self.str_lidAttach == 'aimJoint' or l_toDo_fan:
                    mRoot = _d['mRoot']
                
                    if k == 'upr':
                        mUprRoot = mRoot
                    else:
                        mLwrRoot = mRoot
                    
                    mTarget = mRig.doLoc()
                    _res_attach = RIGCONSTRAINT.attach_toShape(mTarget.mNode,
                                                               self.md_blinkCurves[k]['mDriven'].mNode)
                    
                    
                    TRANS.parent_set(_res_attach[0], mRigNull.mNode)
                    _shape = self.md_blinkCurves[k]['mDriven'].getShapes()[0]
                    mPOCI = cgmMeta.asMeta(_res_attach[1])
                    _minU = ATTR.get(_shape,'minValue')
                    _maxU = ATTR.get(_shape,'maxValue')
                    _param = mPOCI.parameter
                    pct = MATH.get_normalized_parameter(_minU,_maxU,_param)
                    log.debug("|{0}| >>  min,max,param,pct | {1},{2},{3},{4} ".format(_str_func,
                                                                                      _minU,
                                                                                      _maxU,
                                                                                      _param,
                                                                                      pct))
                    mPOCI.turnOnPercentage = True
                    mPOCI.parameter = pct
    
                    mc.aimConstraint(mTarget.mNode,
                                     mRoot.mNode,
                                     maintainOffset = True, weight = 1,
                                     aimVector = self.d_orientation['vectorAim'],
                                     upVector = self.d_orientation['vectorUp'],
                                     worldUpVector = self.d_orientation['vectorUp'],
                                     worldUpObject = mHandle.mNode,
                                     skip = [self.d_orientation['str'][0]],
                                     worldUpType = 'objectRotation' )
                    
                    mRoot.p_parent = mSettings
                    
                    
                if self.str_lidAttach == 'surfaceSlide':
                    mDriver = mRig.masterGroup
                    #mDriver.p_parent = mSettings
                    
                    #mTrack = mJoint.doCreateAt()
                    #mTrack.p_parent = mRigNull                    
                    #mTrack.rename("{0}_surfaceDriver".format(mJoint.p_nameBase))
                    
                    _res = RIGCONSTRAINT.attach_toShape(mDriver.mNode,mOrb.mNode,None,
                                                        driver= mHandle)
                    
                    md = _res[-1]
                    mFollicle = md['mFollicle']
                    for k in ['mDriverLoc','mFollicle']:
                        md[k].p_parent = mRigNull
                        md[k].v = False
                    
                    #mJoint.p_position = md['mFollicle'].p_position
                    mc.parentConstraint(mFollicle.mNode,
                                        mDriver.mNode,maintainOffset=1)
                    
                
                
                
        else:
            log.debug("|{0}| >>  full ... ".format(_str_func))
            
            mRigRoot = mRigNull.getMessageAsMeta('rigRoot')

            mdD = self.md_driverJoints
        
            log.debug("|{0}| >> sort influences".format(_str_func))
            mLeftCorner = self.md_handles['lidUpr']['inner'][0]
            mRightCorner = self.md_handles['lidUpr']['outer'][0]
            mUprCenter = self.md_handles['lidUpr']['center'][0]
            mLwrCenter = self.md_handles['lidLwr']['center'][0]
            
            
            self.d_lidData['upr'] = {'mHandle' : mUprCenter}
            self.d_lidData['lwr'] = {'mHandle' : mLwrCenter}
            
            ml_uprLidInfluences = [mRightCorner.uprInfluence] + self.md_handles['lidUpr']['outer'][1:] + self.md_handles['lidUpr']['center']+ self.md_handles['lidUpr']['inner'][1:] + [mLeftCorner.uprInfluence]
            ml_lwrLidInfluences = [mRightCorner.lwrInfluence] + self.md_handles['lidLwr']['outer'] + self.md_handles['lidLwr']['center']+ self.md_handles['lidLwr']['inner'] + [mLeftCorner.lwrInfluence]
        
            log.debug("|{0}| >> sort driven".format(_str_func))
            dUpr =  self.md_rigJoints['lidUpr']
            dLwr =  self.md_rigJoints['lidLwr']
            _revUprLeft = copy.copy(dUpr['inner'])
            _revLwrLeft = copy.copy(dLwr['inner'])
            for l in _revLwrLeft,_revUprLeft:
                l.reverse()
        
            ml_uprRig = dUpr['outer'] + dUpr['center']+ _revUprLeft
            ml_lwrRig = dLwr['outer'] + dLwr['center']+ _revLwrLeft
            
            d_crvTargets = {'upr':ml_uprRig,
                            'lwr':[ml_uprRig[0]] + ml_lwrRig + [ml_uprRig[-1]]}
            
            
            d_plug_hugs = {}
            
            for k in 'upr','lwr':
                d_plug_hugs[k] = {}
                _k = k.capitalize()
                _crv = CORERIG.create_at(create='curve',l_pos = [mObj.p_position for mObj in d_crvTargets[k]])
                mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
                mRigNull.connectChildNode(mCrv, k+'LidCurve','module')
                
                mPlug_hug = cgmMeta.cgmAttr(mSettings.mNode,
                                             'hug{0}'.format(_k),
                                             attrType='float',
                                             lock=False,
                                             defaultValue = 1.0,
                                             value = 1.0,
                                             keyable=True)
    
                mPlug_hugOn = cgmMeta.cgmAttr(mSettings,'result_hug{0}On'.format(_k),attrType='float',
                                               defaultValue = 0,keyable = False,lock=True,
                                               hidden=1)
    
                mPlug_hugOff= cgmMeta.cgmAttr(mSettings,'result_hug{0}Off'.format(_k),attrType='float',
                                               defaultValue = 0,keyable = False,lock=True,
                                               hidden=1)                
    
                NODEFACTORY.createSingleBlendNetwork(mPlug_hug.p_combinedName,
                                                     mPlug_hugOn.p_combinedName,
                                                     mPlug_hugOff.p_combinedName)                
                d_plug_hugs[k]['on'] = mPlug_hugOn
                d_plug_hugs[k]['off'] = mPlug_hugOff
            
            
            create_clamBlinkCurves(self, ml_uprSkinJoints = ml_uprLidInfluences,
                                   ml_lwrSkinJoints = ml_lwrLidInfluences)

            for mJoint in ml_uprRig:
                mTarget = mJoint.doLoc()
                mDriver = mJoint.driverJoint

                
                _res_attach = RIGCONSTRAINT.attach_toShape(mTarget.mNode,
                                                           self.md_blinkCurves['upr']['mDriven'].mNode)
                
                
                
                TRANS.parent_set(_res_attach[0], mRigNull.mNode)
                _shape = self.md_blinkCurves['upr']['mDriven'].getShapes()[0]
                mPOCI = cgmMeta.asMeta(_res_attach[1])
                _minU = ATTR.get(_shape,'minValue')
                _maxU = ATTR.get(_shape,'maxValue')
                _param = mPOCI.parameter
                pct = MATH.get_normalized_parameter(_minU,_maxU,_param)
                log.debug("|{0}| >>  min,max,param,pct | {1},{2},{3},{4} ".format(_str_func,
                                                                                  _minU,
                                                                                  _maxU,
                                                                                  _param,
                                                                                  pct))
                mPOCI.turnOnPercentage = True
                mPOCI.parameter = pct
                
                mLidRoot = mDriver.getMessageAsMeta('lidRoot')
                
                if mDriver.cgmPosition == 'center':
                    mUprRoot = mLidRoot
                    
                if self.str_lidAttach == 'aimJoint':
                    
                    

                    
                    mc.aimConstraint(mTarget.mNode,
                                     mLidRoot.mNode,
                                     maintainOffset = True, weight = 1,
                                     aimVector = self.d_orientation['vectorAim'],
                                     upVector = self.d_orientation['vectorUp'],
                                     worldUpVector = self.d_orientation['vectorUp'],
                                     worldUpObject = mRigRoot.mNode,#mUprCenter.mNode,
                                     worldUpType = 'objectRotation' )
                    mLidRoot.p_parent = mSettings
                    
                else:
                    mDriver.p_parent = mSettings
                    
                    #mTrack = mJoint.doCreateAt()
                    #mTrack.p_parent = mRigNull                    
                    #mTrack.rename("{0}_surfaceDriver".format(mJoint.p_nameBase))
                    
                    _res = RIGCONSTRAINT.attach_toShape(mDriver.mNode,mOrb.mNode,None,
                                                        driver= mTarget)
                    
                    md = _res[-1]
                    mFollicle = md['mFollicle']
                    for k in ['mDriverLoc','mFollicle']:
                        md[k].p_parent = mRigNull
                        md[k].v = False
                    
                    #mJoint.p_position = md['mFollicle'].p_position
                    mc.parentConstraint(mFollicle.mNode,
                                       mDriver.mNode,maintainOffset=1)                     
                    
                    
                
                
                
                #Blend point --------------------------------------------------------------------
                _const = mc.parentConstraint([mDriver.mNode,mTarget.mNode],mJoint.masterGroup.mNode)[0]
                ATTR.set(_const,'interpType',2)
                
                targetWeights = mc.parentConstraint(_const,q=True, weightAliasList=True)
                


                #Connect                                  
                d_plug_hugs['upr']['on'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                d_plug_hugs['upr']['off'].doConnectOut('%s.%s' % (_const,targetWeights[1]))
                    
                    
                    
                
                #mHandle.masterGroup.p_parent = mSettings                
                
                
            for mJoint in ml_lwrRig:
             
                mTarget = mJoint.doLoc()
                mDriver = mJoint.driverJoint

                    
                _res_attach = RIGCONSTRAINT.attach_toShape(mTarget.mNode,
                                                           self.md_blinkCurves['lwr']['mDriven'].mNode)
                TRANS.parent_set(_res_attach[0], mRigNull.mNode)
                
                
                _shape = self.md_blinkCurves['lwr']['mDriven'].getShapes()[0]
                mPOCI = cgmMeta.asMeta(_res_attach[1])
                _minU = ATTR.get(_shape,'minValue')
                _maxU = ATTR.get(_shape,'maxValue')
                _param = mPOCI.parameter
                pct = MATH.get_normalized_parameter(_minU,_maxU,_param)
                log.debug("|{0}| >>  min,max,param,pct | {1},{2},{3},{4} ".format(_str_func,
                                                                                  _minU,
                                                                                  _maxU,
                                                                                  _param,
                                                                                  pct))
                mPOCI.turnOnPercentage = True
                mPOCI.parameter = pct
                
                mLidRoot = mDriver.getMessageAsMeta('lidRoot')
                
                if mDriver.cgmPosition == 'center':
                    mLwrRoot = mLidRoot
                
                if self.str_lidAttach == 'aimJoint':
                    

                    
                    mc.aimConstraint(mTarget.mNode,
                                     mLidRoot.mNode,
                                     maintainOffset = True, weight = 1,
                                     aimVector = self.d_orientation['vectorAim'],
                                     upVector = self.d_orientation['vectorUp'],
                                     worldUpVector = self.d_orientation['vectorUp'],
                                     worldUpObject = mRigRoot.mNode,#mUprCenter.mNode,
                                     worldUpType = 'objectRotation' )
                    mLidRoot.p_parent = mSettings
                    
                else:
                    mDriver.p_parent = mSettings
                    
                    #mTrack = mJoint.doCreateAt()
                    #mTrack.p_parent = mRigNull                    
                    #mTrack.rename("{0}_surfaceDriver".format(mJoint.p_nameBase))
                    
                    _res = RIGCONSTRAINT.attach_toShape(mDriver.mNode,mOrb.mNode,None,
                                                        driver= mTarget)
                    
                    md = _res[-1]
                    mFollicle = md['mFollicle']
                    for k in ['mDriverLoc','mFollicle']:
                        md[k].p_parent = mRigNull
                        md[k].v = False
                    
                    #mJoint.p_position = md['mFollicle'].p_position
                    mc.parentConstraint(mFollicle.mNode,
                                       mDriver.mNode,maintainOffset=1)  
                    
                
                #Blend point --------------------------------------------------------------------
                _const = mc.parentConstraint([mDriver.mNode,mTarget.mNode],mJoint.masterGroup.mNode)[0]
                ATTR.set(_const,'interpType',2)
                
                targetWeights = mc.parentConstraint(_const,q=True, weightAliasList=True)
                
                

                #Connect                                  
                d_plug_hugs['lwr']['on'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                d_plug_hugs['lwr']['off'].doConnectOut('%s.%s' % (_const,targetWeights[1]))          
            

            
            
            
            """
            mDeformNull = self.mDeformNull
            
            mdD = self.md_driverJoints

            log.debug("|{0}| >> sort influences".format(_str_func))
            mLeftCorner = self.md_handles['lidUpr']['inner'][0]
            mRightCorner = self.md_handles['lidUpr']['outer'][0]
            mUprCenter = self.md_handles['lidUpr']['center'][0]
            mLwrCenter = self.md_handles['lidLwr']['center'][0]        
            ml_uprLidInfluences = [mRightCorner.uprInfluence] + self.md_handles['lidUpr']['outer'][1:] + self.md_handles['lidUpr']['center']+ self.md_handles['lidUpr']['inner'][1:] + [mLeftCorner.uprInfluence]
            ml_lwrLidInfluences = [mRightCorner.lwrInfluence] + self.md_handles['lidLwr']['inner'] + self.md_handles['lidLwr']['center']+ self.md_handles['lidLwr']['inner'] + [mLeftCorner.lwrInfluence]
            
            log.debug("|{0}| >> sort driven".format(_str_func))
            dUpr =  self.md_rigJoints['lidUpr']
            dLwr =  self.md_rigJoints['lidLwr']
            _revUprLeft = copy.copy(dUpr['inner'])
            _revLwrLeft = copy.copy(dLwr['inner'])
            for l in _revLwrLeft,_revUprLeft:
                l.reverse()
                
            ml_uprRig = dUpr['outer'] + dUpr['center']+ _revUprLeft
            ml_lwrRig = dLwr['outer'] + dLwr['center']+ _revLwrLeft
        
            mMidDag = cgmMeta.cgmObject(name='midSealMarker')
            mMidDag.p_position = DIST.get_average_position([mUprCenter.p_position,
                                                            mLwrCenter.p_position])
            mMidDag.p_parent = mDeformNull
            
            d_lids = {'driven1':ml_uprRig,
                      'driven2':ml_lwrRig,
                      'influences1':ml_uprLidInfluences,
                      'influences2':ml_lwrLidInfluences,
                      'baseName':'lidRibbons',
                      'settingsControl':mSettings,
                      'baseName1' :"uprLid",
                      'baseName2':"lwrLid",
                      'extendEnds':False,
                      'sealDriver1':mLeftCorner,
                      'sealDriver2':mRightCorner,
                      'sealDriverMid':mMidDag,#mUprCenter
                      'sealSplit':False,
                      'sealName1' : 'inner',
                      'sealName2' : 'outer',                      
                      'specialMode':'noStartEnd',#'endsToInfluences',
                      'moduleInstance':mModule,
                      'msgDriver':'driverJoint'}    
            
            pprint.pprint(d_lids)
            
            #pprint.pprint(d_test)
            IK.ribbon_seal(**d_lids)
            
            #mc.parentConstraint(mLeftCorner.mNode, ml_uprRig[-1].masterGroup.mNode, maintainOffset = True)
            #mc.parentConstraint(mRightCorner.mNode, ml_uprRig[0].masterGroup.mNode, maintainOffset = True)
            
            for mObj in ml_uprRig + ml_lwrRig:
                mObj.driverJoint.p_parent = mDeformNull
                        """

        #Autofollow --------------------------------------------------------------------
        create_lidFollow(self)
        
        
        
        #Lid Fan Setup --------------------------------------------------------------------
        if l_toDo_fan:
            mDirectEye = mRigNull.getMessageAsMeta('directEye')
            
            for k in l_toDo_fan:
                _key = k + 'FanCenter'
                    
                mHandle = self.d_lidData[_key]['mHandle']
                mRig = self.d_lidData[_key]['mRig']
                
                
                                
                #if self.str_lidAttach == 'aimJoint':
                mRoot = self.d_lidData[_key]['mRoot']
                mHandle.masterGroup.p_parent = mRoot
                
                if k == 'upr':
                    mFollowRoot = mUprRoot
                else:
                    mFollowRoot = mLwrRoot
                    
                if not mFollowRoot:
                    log.debug("|{0}| >>  Creating follow Root".format(_str_func,_key))
                    mFollowEnd = mDirectEye.doDuplicate(po=True)
                    
                    mFollowEnd.doSnapTo(self.d_lidData[k]['mHandle'])
                    
                    mFollowRoot = create_lidRoot(mFollowEnd,mDirectEye,mBlock)
                    mFollowEnd.p_parent = mFollowRoot
                    
                    
                    mTarget = mFollowEnd.doLoc()
    
                        
                    _res_attach = RIGCONSTRAINT.attach_toShape(mTarget.mNode,
                                                               self.md_blinkCurves[k]['mDriven'].mNode)
                    
                    TRANS.parent_set(_res_attach[0], mRigNull.mNode)
                    
                    
                    _shape = self.md_blinkCurves[k]['mDriven'].getShapes()[0]
                    mPOCI = cgmMeta.asMeta(_res_attach[1])
                    _minU = ATTR.get(_shape,'minValue')
                    _maxU = ATTR.get(_shape,'maxValue')
                    _param = mPOCI.parameter
                    pct = MATH.get_normalized_parameter(_minU,_maxU,_param)
                    log.debug("|{0}| >>  min,max,param,pct | {1},{2},{3},{4} ".format(_str_func,
                                                                                      _minU,
                                                                                      _maxU,
                                                                                      _param,
                                                                                      pct))
                    mPOCI.turnOnPercentage = True
                    mPOCI.parameter = pct
                    
                    
                    #Need to make our diver that follows the blink curve and not just the handle =============
                    #self.d_lidData[k]['mHandle'].mNode

                    mTarget = self.d_lidData[k]['mHandle'].doCreateAt()
    
                        
                    _res_attach = RIGCONSTRAINT.attach_toShape(mTarget.mNode,
                                                               self.md_blinkCurves[k]['mDriven'].mNode)
                    TRANS.parent_set(_res_attach[0], mRigNull.mNode)
                    
                    
                    _shape = self.md_blinkCurves[k]['mDriven'].getShapes()[0]
                    mPOCI = cgmMeta.asMeta(_res_attach[1])
                    _minU = ATTR.get(_shape,'minValue')
                    _maxU = ATTR.get(_shape,'maxValue')
                    _param = mPOCI.parameter
                    pct = MATH.get_normalized_parameter(_minU,_maxU,_param)
                    log.debug("|{0}| >>  min,max,param,pct | {1},{2},{3},{4} ".format(_str_func,
                                                                                      _minU,
                                                                                      _maxU,
                                                                                      _param,
                                                                                      pct))
                    mPOCI.turnOnPercentage = True
                    mPOCI.parameter = pct
                    
                    #.... ------------------------------------------
                    
                    #self.d_lidData[k]['mHandle'].mNode

                    mc.aimConstraint(mTarget.mNode,
                                     mFollowRoot.mNode,
                                     maintainOffset = True, weight = 1,
                                     aimVector = self.d_orientation['vectorAim'],
                                     upVector = self.d_orientation['vectorUp'],
                                     worldUpVector = self.d_orientation['vectorUp'],
                                     worldUpObject = mRigRoot.mNode,#mUprCenter.mNode,
                                     worldUpType = 'objectRotation' )
                    
                    if mControlBall:
                        mFollowRoot.p_parent = mControlBall                    
                    else:
                        mFollowRoot.p_parent = mSettings                    
                    

                mRig.masterGroup.p_parent = mHandle
                
                if mControlBall:
                    mRoot.p_parent = mControlBall   
                else:
                    mRoot.p_parent = mSettings
                
                _out = "r{0}".format(self.d_orientation['str'][1])
                _up = "r{0}".format(self.d_orientation['str'][2])
                
                mPlug_followUp = cgmMeta.cgmAttr(mSettings,_key + "UpMult",attrType = 'float', value = .5,
                                                   hidden = False,keyable=True,minValue=0.01)	    
                mPlug_followOut = cgmMeta.cgmAttr(mSettings,_key + "OutMult",attrType = 'float', value = .5,
                                                  hidden = False,keyable=True,minValue=0.01)
                
                arg_up = "{0}.{1} = {2}.{1} * {3}".format(mRoot.mNode, _up,
                                                          mFollowRoot.mNode,
                                                          mPlug_followUp.p_combinedShortName)
                arg_out = "{0}.{1} = {2}.{1} * {3}".format(mRoot.mNode, _out,
                                                          mFollowRoot.mNode,
                                                          mPlug_followOut.p_combinedShortName)
                for a in arg_up,arg_out:
                    NODEFACTORY.argsToNodes(a).doBuild()
                        
                
                if self.str_lidAttach == 'surfaceSlide':
                    mDriver = mRig.masterGroup
                    mDriver.p_parent = mRoot
                    
                    mHandle.masterGroup.p_parent = mRoot#mSettings
                    
                    _res = RIGCONSTRAINT.attach_toShape(mDriver.mNode,mOrb.mNode,None,
                                                        driver= mHandle)
                    md = _res[-1]
                    mFollicle = md['mFollicle']
                    for k2 in ['mDriverLoc','mFollicle']:
                        md[k2].p_parent = mRigNull
                        md[k2].v = False
                
                    #mc.parentConstraint(mFollicle.mNode,
                    #                    mDriver.mNode,maintainOffset=1)
                    
                    #mRig.masterGroup.p_parent = mDriver
                    mDriver.p_parent = mSettings

                    mc.parentConstraint([md['mFollicle'].mNode],
                                        mDriver.mNode, maintainOffset = 1)                    
                    #Blend point --------------------------------------------------------------------
                    """_const = mc.parentConstraint([md['mFollicle'].mNode, mHandle.mNode],
                                                 mDriver.mNode, maintainOffset = 1)[0]
                    
                    ATTR.set(_const,'interpType',2)
                    
                    targetWeights = mc.parentConstraint(_const,q=True, weightAliasList=True)
                    
                    #Connect                                  
                    d_plug_hugs[k]['on'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    d_plug_hugs[k]['off'].doConnectOut('%s.%s' % (_const,targetWeights[1]))"""
                    
                    
                if self.str_lidAttach == 'surfaceSlideOLD':
                    mDriver = mRig.getMessageAsMeta('sourceJoint').driverJoint
                    mHandle.masterGroup.p_parent = mSettings
                    
                    _res = RIGCONSTRAINT.attach_toShape(mDriver.mNode,mOrb.mNode,None,
                                                        driver= mHandle)
                    md = _res[-1]
                    mFollicle = md['mFollicle']
                    for k2 in ['mDriverLoc','mFollicle']:
                        md[k2].p_parent = mRigNull
                        md[k2].v = False
                
                    #mc.parentConstraint(mFollicle.mNode,
                    #                    mDriver.mNode,maintainOffset=1)
                    
                    mRig.masterGroup.p_parent = mDriver
                    mDriver.p_parent = mSettings
    
                    #Blend point --------------------------------------------------------------------
                    mc.parentConstraint([md['mFollicle'].mNode],
                                        mDriver.mNode, maintainOffset = 1)                    
                    """
                    _const = mc.parentConstraint([md['mFollicle'].mNode, mHandle.mNode],
                                                 mDriver.mNode, maintainOffset = 1)[0]
                    
                    ATTR.set(_const,'interpType',2)
                    
                    targetWeights = mc.parentConstraint(_const,q=True, weightAliasList=True)
                    
                    
    
                    #Connect                                  
                    d_plug_hugs[k]['on'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    d_plug_hugs[k]['off'].doConnectOut('%s.%s' % (_const,targetWeights[1]))   """         

    
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_cleanUp'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    mControlFK = mRigNull.getMessageAsMeta('fkEye')
    mJointFK = mControlFK
    mJointIK = mRigNull.getMessageAsMeta('ikEye')
    mControlIK = mRigNull.getMessageAsMeta('controlIK')
    mSettings = mRigNull.getMessageAsMeta('settings')
    mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
    mDirect = mRigNull.getMessageAsMeta('directEye')    
    
    
    mAttachDriver = mRigNull.getMessageAsMeta('attachDriver')
    mAttachDriver.doStore('cgmAlias', '{0}_partDriver'.format(self.d_module['partName']))
    
    #if not self.mConstrainNull.hasAttr('cgmAlias'):
        #self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))    
    
    
    #>>  DynParentGroups - Register parents for various controls ============================================
    ml_baseDynParents = []
    ml_endDynParents = self.ml_dynParentsAbove + self.ml_dynEndParents# + [mRoot]
    ml_ikDynParents = []    
    

    #...ik controls ==================================================================================
    if mControlIK:
        log.debug("|{0}| >>  IK Handle ... ".format(_str_func))                
    
        ml_targetDynParents = [self.mEyeLook] + self.ml_dynParentsAbove + self.ml_dynEndParents
        
        ml_targetDynParents.append(self.md_dynTargetsParent['world'])
        ml_targetDynParents.extend(mControlIK.msgList_get('spacePivots',asMeta = True))
    
        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mControlIK,dynMode=0)
    
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
            
        log.debug("|{0}| >>  IK targets...".format(_str_func))
        #pprint.pprint(ml_targetDynParents)        
        
        log.debug(cgmGEN._str_subLine)
        
    if mBlock.highlightSetup:
        log.debug("|{0}| >> highlight...".format(_str_func))
        mHighLight = mRigNull.getMessageAsMeta('controlHighlight')
        mHighlightDriver = mBlock.prerigNull.getMessageAsMeta('eyeHighlightJoint').getMessageAsMeta('driverJoint')
                
        ml_targetDynParents = [mHighlightDriver] + self.ml_dynParentsAbove + self.ml_dynEndParents
        
        if mBlendJoint:
            ml_targetDynParents.insert(0, mBlendJoint)
        elif mControlFK:
            ml_targetDynParents.insert(0, mControlFK)
            

        mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mHighLight,dynMode=1)
        for mTar in ml_targetDynParents:
            mDynGroup.addDynParent(mTar)
        mDynGroup.rebuild()
        
        for mChild in mHighlightDriver.getChildren(asMeta=1):
            mChild.resetAttrs()

    #Settings =================================================================================
    log.debug("|{0}| >> Settings...".format(_str_func))
    mSettings.visDirect = 0
    
    mPlug_FKIK = cgmMeta.cgmAttr(mSettings,'FKIK')
    mPlug_FKIK.p_defaultValue = 1
    mPlug_FKIK.value = 1
        
    #Lock and hide =================================================================================
    if mBlendJoint:mBlendJoint.dagLock(True)
        
    ml_controls = mRigNull.msgList_get('controlsAll')
    self.UTILS.controls_lockDown(ml_controls)
    
    if not mBlock.scaleSetup:
        log.debug("|{0}| >> No scale".format(_str_func))
        ml_controlsToLock = copy.copy(ml_controls)
        for mCtrl in ml_controlsToLock:
            ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
    else:
        log.debug("|{0}| >>  scale setup...".format(_str_func))
        for mJnt in self.d_joints['ml_moduleJoints']:
            mJnt.segmentScaleCompensate = 0
        
        for mJnt in mSettings.getAllChildren():
            try:
                mJnt.segmentScaleCompensate = 0
            except:
                pass

        
        
    self.mDeformNull.dagLock(True)
    
    
    #Lid Defaults ===============================================================
    if self.v_lidBuild:
        mPlug_leftLimit = self.mPlug_leftLimit#store
        mPlug_rightLimit = self.mPlug_rightLimit#store
        mPlug_uprUpLimit = self.mPlug_uprUpLimit#store
        mPlug_uprDnLimit = self.mPlug_uprDnLimit#store	
        mPlug_lwrUpLimit = self.mPlug_lwrUpLimit#store
        mPlug_lwrDnLimit = self.mPlug_lwrDnLimit#store
        mPlug_lwrDnStart = self.mPlug_lwrDnStart#store		
    
        _l_defaults = [{"plug":self.mPlug_followLwr,'setting':1},
                       {"plug":self.mPlug_followUpr,'setting':1},
                       {"plug":mPlug_uprUpLimit,'setting':-30},
                       {"plug":mPlug_lwrDnLimit,'setting':15}]
    
        if self.d_module['mirrorDirection'] == 'Right':
            _l_defaults.extend([{"plug":mPlug_rightLimit,'setting':-30},
                                {"plug":mPlug_leftLimit,'setting':10}])
        else:
            _l_defaults.extend([{"plug":mPlug_rightLimit,'setting':-10},
                                {"plug":mPlug_leftLimit,'setting':30}])
        for d in _l_defaults:
            _value = d['setting'] 
            d['plug'].p_defaultValue = _value
            d['plug'].value = _value
    

    
    #Close out ===============================================================================================
    mRigNull.version = self.d_block['buildVersion']
    mBlock.blockState = 'rig'
    mBlock.UTILS.set_blockNullFormState(mBlock)
    self.UTILS.rigNodes_store(self)


def create_simpleMesh(self,  deleteHistory = True, cap=True):
    _str_func = 'create_simpleMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    
    mGroup = self.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    l_headGeo = mGroup.getChildren(asMeta=False)
    ml_headStuff = []
    for i,o in enumerate(l_headGeo):
        log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
        if ATTR.get(o,'v'):
            log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
            mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
            ml_headStuff.append(  mObj )
            mObj.p_parent = False
        

    if self.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))    
        ml_neckMesh = self.UTILS.create_simpleLoftMesh(self,deleteHistory,cap)
        ml_headStuff.extend(ml_neckMesh)
        
    _mesh = mc.polyUnite([mObj.mNode for mObj in ml_headStuff],ch=False)
    _mesh = mc.rename(_mesh,'{0}_0_geo'.format(self.p_nameBase))
    
    return cgmMeta.validateObjListArg(_mesh)

def asdfasdfasdf(self, forceNew = True, skin = False):
    """
    Build our proxyMesh
    """
    _short = self.d_block['shortName']
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHeadIK = mRigNull.headIK
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"

    #>> If proxyMesh there, delete --------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    if directProxy:
        log.debug("|{0}| >> directProxy... ".format(_str_func))
        _settings = self.mRigNull.settings.mNode
        
    
    mGroup = mBlock.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    l_headGeo = mGroup.getChildren(asMeta=False)
    l_vis = mc.ls(l_headGeo, visible = True)
    ml_headStuff = []
    
    for i,o in enumerate(l_vis):
        log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))
        
        mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
        ml_headStuff.append(  mObj )
        mObj.parent = ml_rigJoints[-1]
        
        ATTR.copy_to(ml_rigJoints[-1].mNode,'cgmName',mObj.mNode,driven = 'target')
        mObj.addAttr('cgmIterator',i)
        mObj.addAttr('cgmType','proxyGeo')
        mObj.doName()
        
        if directProxy:
            CORERIG.shapeParent_in_place(ml_rigJoints[-1].mNode,mObj.mNode,True,False)
            CORERIG.colorControl(ml_rigJoints[-1].mNode,_side,'main',directProxy=True)        
        
    if mBlock.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))


def build_proxyMesh(self, forceNew = True, puppetMeshMode = False):
    """
    Build our proxyMesh
    """
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self
    mModule = self.moduleTarget
    mRigNull = mModule.rigNull
    mDeformNull = mModule.deformNull
    mSettings = mRigNull.settings
    mRoot = mRigNull.getMessageAsMeta('rigRoot')
    if not mRoot:
        mRoot = mDeformNull
        
    mPuppet = self.atUtils('get_puppet')
    mMaster = mPuppet.masterControl    
    mPuppetSettings = mMaster.controlSettings
    str_partName = mModule.get_partNameBase()
    mPrerigNull = mBlock.prerigNull
    directProxy = mBlock.proxyDirect
    
    _side = BLOCKUTILS.get_side(self)
    ml_neckProxy = []
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"
    v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    
    #>> If proxyMesh there, delete --------------------------------------------------------------------------- 
    if puppetMeshMode:
        _bfr = mRigNull.msgList_get('puppetProxyMesh',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> puppetProxyMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr        
    else:
        _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
                _bfr2 = mRigNull.msgList_get('proxyJoints',asMeta=True)
                mc.delete([mObj.mNode for mObj in _bfr2])
                
            else:
                return _bfr
        
    #>> Eye ===================================================================================
    log.debug("|{0}| >> Eye...".format(_str_func))
    
    #if directProxy:
    #    log.debug("|{0}| >> directProxy... ".format(_str_func))
    #    _settings = self.mRigNull.settings.mNode
        
    mDirect = mRigNull.getMessageAsMeta('directEye')
    """
    mProxyEye = cgmMeta.validateObjArg(CORERIG.create_proxyGeo('sphere',
                                                               v_baseSize,ch=False)[0],
                                       'cgmObject',setClass=True)"""
    
    mOrb = mBlock.getMessageAsMeta('bbHelper')
    str_meshShape = mOrb.getShapes()[0]
    minU = ATTR.get(str_meshShape,'minValueU')
    maxU = ATTR.get(str_meshShape,'maxValueU')
    
    l_use = [MATH.average(minU,maxU),
             maxU * .6,
             maxU * .7]
    
    l_crvs = []
    l_delete = []
    for v in l_use:
        _crv = mc.duplicateCurve("{0}.u[{1}]".format(str_meshShape,v), ch = 0, rn = 0, local = 0)[0]
        l_crvs.append(_crv)
        l_delete.append(_crv)
        
    _r = 272
    md_helpers = {}
    ml_helpers = []
    b_noPupil = False
    
    for k in ['iris','pupil']:
        mHelper = mBlock.getMessageAsMeta('{0}Helper'.format(k))
        if not mHelper:
            continue
        mDup = mHelper.doDuplicate(po=False)
        mDup.dagLock(False)
        mDup.p_parent = False
        l_crvs.append(mDup.mNode)
        l_delete.append(mDup.mNode)
        md_helpers[k] =[mDup.mNode]
        mDup.rz = _r
        
        if k == 'iris' and not mBlock.getMessage('pupilHelper'):
            mDup2 = mHelper.doDuplicate(po=False)
            mDup2.rz = _r
            
            mDup2.dagLock(False)
            mDup2.p_parent = mDup
            pos_bb = TRANS.bbCenter_get(mDup2.mNode)
            mDup2.p_parent = False
            
            DIST.offsetShape_byVector(mDup2.mNode,origin= pos_bb,
                                      factor = -.99, offsetMode = 'vectorScale')             
            l_crvs.append(mDup2.mNode)
            l_delete.append(mDup2.mNode)
            
            md_helpers[k].append(mDup2)
            b_noPupil = True

        if k == 'pupil':
            mDup2 = mHelper.doDuplicate(po=False)
            mDup2.rz = _r
            
            mDup2.dagLock(False)
            mDup2.p_parent = mDup
            d = DIST.get_bb_size(mDup.mNode,mode='max')
            mDup2.tz = - d * .2
            pos_bb = TRANS.bbCenter_get(mDup2.mNode)
            
            mDup2.p_parent = False
            
            DIST.offsetShape_byVector(mDup2.mNode,origin= pos_bb,
                                      factor = -.8, offsetMode = 'vectorScale')            
            
            #for ep in mc.ls("{0}.ep[*]".format(mDup2.getShapes()[0]),flatten=True):
                #POS.set(ep,pos_bb)
                
            l_crvs.append(mDup2.mNode)
            l_delete.append(mDup2.mNode)
            
            md_helpers[k].append(mDup2)
        """
        _surf = mc.planarSrf(mHelper.mNode,ch=1, d=3, ko=0, tol = .01, rn = 0, po = 0,
                             name = "{0}_approx".format(k))
        mc.reverseSurface(_surf[0])
        mSurf = cgmMeta.validateObjArg(_surf[0], 'cgmObject',setClass=True)
        mSurf.p_parent = False
        if k == 'iris':
            CORERIG.colorControl(mSurf.mNode,_side,'sub',transparent = True)
        else:
            CORERIG.colorControl(mSurf.mNode,_side,'main',transparent=True)    """
    
    l_crvs.reverse()
    if b_noPupil:
        _mesh = BUILDERUTILS.create_loftMesh(l_crvs[1:], name="{0}_proxy".format(str_partName),
                                             uniform=True,
                                             degree=2,divisions=1,cap=False)        
    else:
        _mesh = BUILDERUTILS.create_loftMesh(l_crvs[2:], name="{0}_proxy".format(str_partName),
                                             uniform=True,
                                             degree=2,divisions=1,cap=False)
    #l_crvs.reverse()
    CORERIG.colorControl(_mesh,_side,'sub',transparent=False,proxy=True)
    l_combine = [_mesh]
    #Iris...------------------------------------------------------------------------
    if md_helpers.get('iris'):
        if b_noPupil:
            _meshIris = BUILDERUTILS.create_loftMesh(l_crvs[:2], name="{0}_proxyIris".format(str_partName),
                                                     uniform=0,
                                                     degree=1,divisions=5,cap=False)            
        else:
            _meshIris = BUILDERUTILS.create_loftMesh(l_crvs[1:3], name="{0}_proxyIris".format(str_partName),
                                                     uniform=0,
                                                     degree=1,divisions=5,cap=False)
        
        mc.polyNormal(_meshIris, normalMode = 0, userNormalMode=1,ch=0)
        CORERIG.colorControl(_meshIris,_side,'main',transparent=False,proxy=True)
        l_combine.append(_meshIris)
        
    #pupil ----------------------------------------------------------------------
    if md_helpers.get('pupil'):
        _meshPupil = BUILDERUTILS.create_loftMesh(l_crvs[:2], name="{0}_proxyPupil".format(str_partName),
                                                 uniform=1,
                                                 degree=1,divisions=5,cap=False)    
        mc.polyNormal(_meshPupil, normalMode = 0, userNormalMode=1,ch=0)
        CORERIG.colorControl(_meshPupil,'special','pupil',transparent=False,proxy=True)
        l_combine.append(_meshPupil)
    
    
    
    _mesh = mc.polyUnite(l_combine, ch=False )[0]
    mProxyEye = cgmMeta.validateObjArg(_mesh,'cgmObject',setClass=True)  
    mc.delete(l_delete)
    
    #mProxyEye.doSnapTo(mDirect)
    mProxyEye.p_parent = mDirect
    ml_proxy = [mProxyEye]
    ml_noFreeze = []
    
    
    if mBlock.lidBuild:
        
        str_lidBuild = mBlock.getEnumValueString('lidBuild')
        #>>Lid setup ================================================
        if str_lidBuild == 'clam':
            #Need to make our lid roots and orient
            for k in 'upr','lwr':
                log.debug("|{0}| >> {1}...".format(_str_func,k))
                _keyHandle = '{0}LidHandle'.format(k)
                
                mLidSkin = mPrerigNull.getMessageAsMeta('{0}LidJoint'.format(k))
                mRigJoint = mLidSkin.rigJoint
                
                mEndCurve = mBlock.getMessageAsMeta('{0}EdgeFormCurve'.format(k)).doDuplicate(po=False)
                mEndCurve.dagLock(False)
                mEndCurve.p_parent = False
                mEndCurve.p_parent = mDeformNull
                mEndCurve.v = False
                
                #mStartCurve = mRigNull.getMessageAsMeta(k+'LineFormCurve')#.doDuplicate(po=False)
                mStartCurve = mRigNull.getMessageAsMeta(k+'LidCurve')#.doDuplicate(po=False)
                
                """
                mHandle = mRigNull.getMessageAsMeta(_keyHandle)
                
                ml_uprSkinJoints = [self.d_lidData['upr']['mHandle']]#ml_uprLidHandles
                ml_lwrSkinJoints = [self.d_lidData['lwr']['mHandle']]#[ml_uprLidHandles[0]] + ml_lwrLidHandles + [ml_uprLidHandles[-1]]
                md_skinSetup = {'upr':{'ml_joints':ml_uprSkinJoints,'mi_crv':md['upr']['mDriver']},
                                'lwr':{'ml_joints':ml_lwrSkinJoints,'mi_crv':md['lwr']['mDriver']}}
                
                for k in md_skinSetup.keys():
                    d_crv = md_skinSetup[k]
                    str_crv = d_crv['mi_crv'].p_nameShort
                    l_joints = [mi_obj.p_nameShort for mi_obj in d_crv['ml_joints']]
                    log.debug(" %s | crv : %s | joints: %s"%(k,str_crv,l_joints))
                    try:
                        mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mi_obj.mNode for mi_obj in d_crv['ml_joints']],
                                                                      d_crv['mi_crv'].mNode,
                                                                      tsb=True,
                                                                      maximumInfluences = 3,
                                                                      normalizeWeights = 1,dropoffRate=2.5)[0])
                    except Exception,error:raise StandardError,"skinCluster : %s"%(error)  	                
                    """
                
                
                #Loft ------------------------------------------------
                _res_body = mc.loft([mStartCurve.mNode,mEndCurve.mNode], 
                                    o = True, d = 1, po = 3, c = False,autoReverse=False)
                mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
                _loftNode = _res_body[1]
                _inputs = mc.listHistory(mLoftSurface.mNode,pruneDagObjects=True)
                _rebuildNode = _inputs[0]            
                mLoftSurface = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
            
                #if polyType == 'bezier':
                mc.reverseSurface(mLoftSurface.mNode, direction=1,rpo=True)
            
                _d = {'keepCorners':False}#General}
            
    
            
                mLoftSurface.overrideEnabled = 1
                mLoftSurface.overrideDisplayType = 2
            
                mLoftSurface.p_parent = mModule
                mLoftSurface.resetAttrs()
            
                mLoftSurface.doStore('cgmName',"{0}_{1}Lid".format(str_partName,k),attrType='string')
                mLoftSurface.doStore('cgmType','proxy')
                mLoftSurface.doName()
                log.debug("|{0}| loft node: {1}".format(_str_func,_loftNode))             
    
                ml_proxy.append(mLoftSurface)
        else:
            log.debug("|{0}| >> ...".format(_str_func))
            ml_proxyJoints = []
            
            log.debug(cgmGEN.logString_sub(_str_func,'proxy joints'))        
            md_defineObjs = {}
            ml_formHandles = self.msgList_get('formHandles')
            for mObj in ml_formHandles:
                md_defineObjs[mObj.handleTag] = mObj
                
            _d_joints = {'upr':[],
                         'lwr':[]}
                
            for k,l in _d_joints.iteritems():
                _key = k+'Orb'
                for k2,mObj in md_defineObjs.iteritems():
                    if _key in k2:
                        mJoint = self.doCreateAt('joint')
                        mJoint.p_position = mObj.p_position
                        mJoint.p_parent = mRoot #mDeformNull
                        mJoint.v=False
                        mJoint.dagLock()
                        ml_proxyJoints.append(mJoint)
                        l.append(mJoint)
        
            mRigNull.msgList_connect('proxyJoints', ml_proxyJoints)        
            
            md_map = {}
            for k in 'upr','lwr','lidCorner':
                md_map[k] = []
                
                for mJnt in ml_rigJoints:
                    if '_{0}'.format(k) in mJnt.p_nameBase:
                        md_map[k].append(mJnt)        
            
            pprint.pprint(md_map)
            _d_mesh = {}
            for k in 'upr','lwr':
                mMesh = self.getMessageAsMeta('{0}LidFormLoft'.format(k))
                d_kws = {'mode':'default',
                         'uNumber':self.numLidSplit_u,
                         'vNumber':self.numLidSplit_v,
                         }
    
                        
                mMesh = RIGCREATE.get_meshFromNurbs(mMesh,**d_kws)    
                ml_proxy.append(mMesh)
                ml_noFreeze.append(mMesh)
                
                mc.skinCluster ([mJnt.mNode for mJnt in md_map[k] + md_map['lidCorner'] + _d_joints[k]],
                                mMesh.mNode,
                                tsb=True,
                                bm=0,
                                wd=0,
                                sm=0,
                                maximumInfluences = 4,
                                heatmapFalloff = 1.0,
                                dropoffRate=4,                            
                                normalizeWeights = 1)            

    for mProxy in ml_proxy:
        if mProxy not in ml_noFreeze:
            mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)

        #Vis connect -----------------------------------------------------------------------
        mProxy.overrideEnabled = 1
        ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(mProxy.mNode) )
        ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayType".format(mProxy.mNode) )
        for mShape in mProxy.getShapes(asMeta=1):
            str_shape = mShape.mNode
            mShape.overrideEnabled = 0
            #ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(str_shape) )
            ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayTypes".format(str_shape) )
            
    #if directProxy:
    #    for mObj in ml_rigJoints:
    #        for mShape in mObj.getShapes(asMeta=True):
                #mShape.overrideEnabled = 0
    #            mShape.overrideDisplayType = 0
    #            ATTR.connect("{0}.visDirect".format(_settings), "{0}.overrideVisibility".format(mShape.mNode))
        
        

    
    mRigNull.msgList_connect('proxyMesh', ml_proxy)




















