"""
------------------------------------------
cgm.core.mrs.blocks.organic.eye
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
reload(MODULECONTROL)
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
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.ik_utils as IK
import cgm.core.cgm_RigMeta as cgmRIGMETA
import cgm.core.lib.nameTools as NAMETOOLS

for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT:
    reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.10.31.2018'
__autoTemplate__ = False
__menuVisible__ = True
__faceBlock__ = True

#These are our base dimensions. In this case it is for human
__dimensions_by_type = {'box':[22,22,22],
                        'human':[15.2, 23.2, 19.7]}

__l_rigBuildOrder__ = ['rig_dataBuffer',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_lidSetup',
                       'rig_cleanUp']




d_wiring_skeleton = {'msgLinks':[],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull','eyeOrientHelper','rootHelper','noTransPrerigNull']}
d_wiring_template = {'msgLinks':['templateNull'],
                     }
d_wiring_extraDags = {'msgLinks':['bbHelper'],
                      'msgLists':[]}
#>>>Profiles ==============================================================================================
d_build_profiles = {}


d_block_profiles = {'default':{},
                    'eye':{'baseSize':[2.7,2.7,2.7],
                           'eyeType':'sphere',
                           'ikSetup':True,
                           'setupLid':'none',
                           },
                    'eyeClamLid':{
                        'baseSize':[2.7,2.7,2.7],
                        'eyeType':'sphere',
                        'ikSetup':True,
                        'setupLid':'clam',
                        'numLidUpr':1,
                        'numLidLwr':1,
                        'baseDat':{'upr':[0,1,0],'lwr':[0,-1,0],'left':[1,0,0],'right':[-1,0,0]},
                           }}



#>>>Attrs =================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'baseAim',
                   'baseDat',
                   'attachPoint',
                   'nameList',
                   'numSpacePivots',
                   'loftDegree',
                   'loftSplit',
                   'scaleSetup',
                   'proxyDirect',
                   'moduleTarget',]

d_attrsToMake = {'eyeType':'sphere:nonsphere',
                 'hasEyeOrb':'bool',
                 'ikSetup':'bool',
                 'paramMidUpr':'float',
                 'paramMidLwr':'float',
                 'setupPupil':'none:joint:blendshape',
                 'setupIris':'none:joint:blendshape',
                 'setupLid':'none:clam:full',
                 'numLidUpr':'int',
                 'numLidLwr':'int',
                 
                 
}

d_defaultSettings = {'version':__version__,
                     'proxyDirect':True,
                     'attachPoint':'end',
                     'side':'right',
                     'nameList':['eye','eyeOrb','pupil','iris','cornea'],
                     'loftDegree':'cubic',
                     'paramMidUpr':.5,
                     'paramMidLwr':.5,
                     #'baseSize':MATH.get_space_value(__dimensions[1]),
                     }

#=============================================================================================================
#>> Define
#=============================================================================================================
@cgmGEN.Timer
def define(self):
    _str_func = 'define'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    _short = self.mNode
    
    ATTR.set_alias(_short,'sy','blockScale')    
    self.setAttrFlags(attrs=['sx','sz','sz'])
    self.doConnectOut('sy',['sx','sz'])    
    
    #ATTR.set_min(_short, 'loftSides', 3)
    ATTR.set_min(_short, 'loftSplit', 1)
    
    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)
        defineNull = self.getMessage('defineNull')
        if defineNull:
            log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
            mc.delete(defineNull)
    
    _size = MATH.average(self.baseSize[1:])
    _crv = CURVES.create_fromName(name='locatorForm',#'axis3d',#'arrowsAxis', 
                                  direction = 'z+', size = _size/4)
    SNAP.go(_crv,self.mNode,)
    CORERIG.override_color(_crv, 'white')        
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    mHandleFactory = self.asHandleFactory()
    self.addAttr('cgmColorLock',True,lock=True, hidden=True)
    mDefineNull = self.atUtils('stateNull_verify','define')
    
    #Rotate Group ==================================================================
    mRotateGroup = cgmMeta.validateObjArg(mDefineNull.doGroup(True,False,asMeta=True,typeModifier = 'rotate'),
                                          'cgmObject',setClass=True)
    mRotateGroup.p_parent = mDefineNull
    mRotateGroup.doConnectIn('rotate',"{0}.baseAim".format(_short))
    mRotateGroup.setAttrFlags()
    
    #Bounding sphere ==================================================================
    _bb_shape = CURVES.create_controlCurve(self.mNode,'sphere', size = 1.0, sizeMode='fixed')
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    mBBShape.p_parent = mDefineNull    
    mBBShape.tz = -.5
    
    CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
    self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
    mHandleFactory.color(mBBShape.mNode,controlType='sub')
    mBBShape.setAttrFlags()
    
    mBBShape.doStore('cgmName', self)
    mBBShape.doStore('cgmType','bbVisualize')
    mBBShape.doName()    
    
    self.connectChildNode(mBBShape.mNode,'bbHelper')
    _sideMult = 1
    _axisOuter = 'x+'
    _axisInner = 'x-'
    
    if self.side == 1:
        _sideMult = -1
        _axisOuter = 'x-'
        _axisInner = 'x+'
        
    if self.setupLid:
        _d = {#'aim':{'color':'yellowBright','defaults':{'tz':1}},
              'upr':{'color':'blueSky','tagOnly':True,'arrow':False,
                     'vectorLine':False,'defaults':{'ty':1}},
              'lwr':{'color':'blueSky','tagOnly':True,'arrow':False,
                     'vectorLine':False,'defaults':{'ty':-1}},
              'inner':{'color':'blueSky','tagOnly':True,'arrow':False,
                       'vectorLine':False,'defaults':{'tx':1*_sideMult}},
              'outer':{'color':'blueSky','tagOnly':True,'arrow':False,
                       'vectorLine':False,'defaults':{'tx':-1*_sideMult}},
              'uprEnd':{'color':'blue','tagOnly':True,'parentTag':'upr',
                        'defaults':{'ty':1.5}},
              'lwrEnd':{'color':'blue','tagOnly':True,'parentTag':'lwr',
                        'defaults':{'ty':-1.5}},
              'innerEnd':{'color':'blue','tagOnly':True,'parentTag':'inner',
                          'defaults':{'tx':1.5*_sideMult}},
              'outerEnd':{'color':'blue','tagOnly':True,'parentTag':'outer',
                          'defaults':{'tx':-1.5*_sideMult}},              
              }
    
        _l_order = ['upr','lwr','inner','outer',
                    'uprEnd','lwrEnd','innerEnd','outerEnd']
    
    
        md_res = self.UTILS.create_defineHandles(self, _l_order, _d, _size / 5)
        #self.UTILS.define_set_baseSize(self)
        
        md_handles = md_res['md_handles']
        ml_handles = md_res['ml_handles']
        
        d_positions = {'inner':self.getPositionByAxisDistance(_axisOuter,_size*.5),
                       'outer':self.getPositionByAxisDistance(_axisInner,_size*.5),
                       'upr':self.getPositionByAxisDistance('y+',_size*.25),
                       'lwr':self.getPositionByAxisDistance('y-',_size*.25),
                       }
        md_handles['inner'].p_position = d_positions['inner']
        md_handles['outer'].p_position = d_positions['outer']
        md_handles['upr'].p_position = d_positions['upr']
        md_handles['lwr'].p_position = d_positions['lwr']
        
        """
        _crvUpr = CORERIG.create_at(create='curve',l_pos = [d_positions['inner'],
                                                            d_positions['upr'],
                                                            d_positions['outer']])
        
        _crvLwr = CORERIG.create_at(create='curve',l_pos = [d_positions['inner'],
                                                            d_positions['lwr'],
                                                            d_positions['outer']])"""
        
    
        self.msgList_connect('defineSubHandles',ml_handles)#Connect
    
    
 
 

#=============================================================================================================
#>> Template
#=============================================================================================================
def templateDelete(self):
    _str_func = 'templateDelete'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    ml_defSubHandles = self.msgList_get('defineSubHandles')
    for mObj in ml_defSubHandles:
        mObj.template = False    
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
def template(self):
    try:    
        _str_func = 'template'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        _short = self.p_nameShort
        _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
        
        #Initial checks ===============================================================================
        log.debug("|{0}| >> Initial checks...".format(_str_func)+ '-'*40)    
        _side = self.UTILS.get_side(self)
        _eyeType = self.getEnumValueString('eyeType')
                
        if _eyeType not in ['sphere']:
            return log.error("|{0}| >> loft setup mode not done: {1}".format(_str_func,_loftSetup))
        
        #Create temple Null  ==================================================================================
        mTemplateNull = BLOCKUTILS.templateNull_verify(self)    
        mHandleFactory = self.asHandleFactory()
        
        #Meat ==============================================================================================
        if self.setupLid:
            log.debug("|{0}| >> Lid setup...".format(_str_func)+ '-'*40)
            
            ml_defSubHandles = self.msgList_get('defineSubHandles')
            for mObj in ml_defSubHandles:
                mObj.template = True
                
            l_tags = ['upr','lwr','inner','outer',
                      'uprEnd','lwrEnd','innerEnd','outerEnd']
            md_handles = {}
            d_pos = {}
            for tag in l_tags:
                md_handles[tag] = self.getMessageAsMeta("define{0}Helper".format(tag.capitalize()))
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
            
            
            """
            _crvUpr = CORERIG.create_at(create='curve',l_pos = [d_pos['inner'],
                                                                d_pos['upr'],
                                                                d_pos['outer']])
                    
            _crvLwr = CORERIG.create_at(create='curve',l_pos = [d_pos['inner'],
                                                                d_pos['lwr'],
                                                                d_pos['outer']])
            
            _crvUprEnd = CORERIG.create_at(create='curve',l_pos = [d_pos['innerEnd'],
                                                                   d_pos['uprEnd'],
                                                                   d_pos['outerEnd']])
                            
            _crvLwrEnd = CORERIG.create_at(create='curve',l_pos = [d_pos['innerEnd'],
                                                                   d_pos['lwrEnd'],
                                                                   d_pos['outerEnd']])
            
            
            mUpr = cgmMeta.asMeta(_crvUpr,setClass=True)
            mLwr = cgmMeta.asMeta(_crvLwr,setClass=True)
            mUprEnd = cgmMeta.asMeta(_crvUprEnd,setClass=True)
            mLwrEnd = cgmMeta.asMeta(_crvLwrEnd,setClass=True)
            """

            
            for tag,l_pos in d_loftCurves.iteritems():
                _crv = CORERIG.create_at(create='curve',l_pos = l_pos)
                mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
                mCrv.p_parent = mTemplateNull
                mHandleFactory.color(mCrv.mNode)
                
                mCrv.rename('{0}_loftCurve'.format(tag))
                
                self.connectChildNode(mCrv, tag+'LidLoftCurve','block')
                md_loftCurves[tag]=mCrv
                
            self.UTILS.create_simpleTemplateLoftMesh(self,
                                                     [md_loftCurves['upr'].mNode,
                                                      md_loftCurves['uprEnd'].mNode],
                                                     mTemplateNull,
                                                     polyType = 'bezier',
                                                     baseName = 'uprLid')
            self.UTILS.create_simpleTemplateLoftMesh(self,
                                                     [md_loftCurves['lwr'].mNode,
                                                      md_loftCurves['lwrEnd'].mNode],
                                                     mTemplateNull,
                                                     polyType = 'bezier',
                                                     baseName = 'lwrLid')    
            
            log.debug(self.uprLidTemplateLoft)
            log.debug(self.lwrLidTemplateLoft)
            log.debug(self.uprLidLoftCurve)
            log.debug(self.lwrLidLoftCurve)
    
        
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
        
        ml_handles = []
        
        #Get base dat =============================================================================    
        _mVectorAim = MATH.get_obj_vector(self.mNode,asEuclid=True)
        mBBHelper = self.bbHelper
        _v_range = max(TRANS.bbSize_get(self.mNode)) *2
        _bb_axisBox = SNAPCALLS.get_axisBox_size(mBBHelper.mNode, _v_range, mark=False)
        _size_width = _bb_axisBox[0]#...x width
        _size_base = _size_width * .25
        _size_sub = _size_base * .5
        
        _pos_bbCenter = POS.get_bb_center(mBBHelper.mNode)
    
        log.debug("{0} >> axisBox size: {1}".format(_str_func,_bb_axisBox))
        log.debug("{0} >> Center: {1}".format(_str_func,_pos_bbCenter))
    
        #for i,p in enumerate(_l_basePos):
            #LOC.create(position=p,name="{0}_loc".format(i))
    
    
    
        #mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self,'template') 
    
    
        #Create Pivot =====================================================================================
        #loc = LOC.create(position=_pos_bbCenter,name="bbCenter_loc")
        #TRANS.parent_set(loc,mTemplateNull)
    
        crv = CURVES.create_fromName('sphere', size = _size_base)
        mHandleRoot = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
        mHandleFactory.color(mHandleRoot.mNode)
    
        #_shortHandle = mHandleRoot.mNode
    
        #ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
        mHandleRoot.doStore('cgmName','eyeRoot')    
        mHandleRoot.doStore('cgmType','templateHandle')
        mHandleRoot.doName()
    
        mHandleRoot.p_position = _pos_bbCenter
        mHandleRoot.p_parent = mStateNull
        mHandleRoot.doGroup(True,True,asMeta=True,typeModifier = 'center')
    
        self.connectChildNode(mHandleRoot.mNode,'rootHelper','module')
    
        #Orient helper =====================================================================================
        _orientHelper = CURVES.create_fromName('arrowSingle', size = _size_base)
        mShape = cgmMeta.validateObjArg(_orientHelper)
    
    
        mShape.doSnapTo(self.mNode)
        mShape.p_parent = mHandleRoot
    
        mShape.tz = self.baseSizeZ
        mShape.rz = 90
    
        _crvLinear = CORERIG.create_at(create='curveLinear',
                                       l_pos=[mHandleRoot.p_position,mShape.p_position])
        
        
        mOrientHelper = mHandleRoot.doCreateAt(setClass=True)
        CORERIG.shapeParent_in_place(mOrientHelper.mNode, mShape.mNode,False)
        CORERIG.shapeParent_in_place(mOrientHelper.mNode, _crvLinear,False)
        
        mOrientHelper.p_parent = mHandleRoot
    
        mOrientHelper.doStore('cgmName','eyeOrient')
        mOrientHelper.doStore('cgmType','templateHandle')
        mOrientHelper.doName()
    
        self.connectChildNode(mOrientHelper.mNode,'eyeOrientHelper','module')
        mHandleFactory.color(mOrientHelper.mNode,controlType='sub')
        
        ml_handles.append(mOrientHelper)
    
        if self.hasEyeOrb:
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
                mHandleOrb.doStore('cgmType','templateHandle')
                mHandleOrb.doName()
    
                self.connectChildNode(mHandleOrb.mNode,'eyeOrbHelper','module')"""
    
    
        
        #Settings shape --------------------
        if self.ikSetup or self.hasEyeOrb:
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
        
        if self.setupLid:
            def create_lidHandle(self,tag,pos,mJointTrack=None,trackAttr=None,visualConnection=True):
                mHandle = cgmMeta.validateObjArg( CURVES.create_fromName('circle', size = _size_sub), 
                                                  'cgmObject',setClass=1)
                mHandle.doSnapTo(self)
                
                mHandle.p_position = pos
                
                mHandle.p_parent = mStateNull
                mHandle.doStore('cgmName',tag)
                mHandle.doStore('cgmType','templateHandle')
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
            _setupLid = self.getEnumValueString('setupLid')
            mUprLid = self.getMessageAsMeta('uprLidLoftCurve')
            mLwrLid = self.getMessageAsMeta('lwrLidLoftCurve')
            
            log.debug("|{0}| >> EyeLid setup: {1}.".format(_str_func,_setupLid))
            
            mModule_lids = self.atUtils('module_verify','eyelid','moduleEyelid')
            
            #Lid Root ---------------------------------------------------------
            crv = CURVES.create_fromName('jack', size = _size_sub)
            mLidRoot = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
            mHandleFactory.color(mLidRoot.mNode)
        
            #_shortHandle = mHandleRoot.mNode
        
            #ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
            mLidRoot.doStore('cgmName','lidRoot')    
            mLidRoot.doStore('cgmType','templateHandle')
            mLidRoot.doName()
        
            mLidRoot.p_position = _pos_bbCenter
            mLidRoot.p_parent = mStateNull
            mLidRoot.doGroup(True,True,asMeta=True,typeModifier = 'center')
            
            mHandleFactory.addJointLabel(mLidRoot,'lidRoot')
            self.connectChildNode(mLidRoot.mNode,'lidRootHelper','block')
            ml_handles.append(mLidRoot)
            
            md_lidHandles = {}
            
            #Lid Handles
            if _setupLid == 'clam':
                d_handles = {'upr':CURVES.getPercentPointOnCurve(mUprLid.mNode,.5),
                             'lwr':CURVES.getPercentPointOnCurve(mLwrLid.mNode,.5)}
                
                mUprHandle = create_lidHandle(self,'upr',
                                              CURVES.getPercentPointOnCurve(mUprLid.mNode,.5),
                                              mJointTrack=mUprLid,
                                              trackAttr = 'paramMidUpr',
                                              )
                
                mLwrHandle = create_lidHandle(self,'lwr',
                                              CURVES.getPercentPointOnCurve(mLwrLid.mNode,.5),
                                              mJointTrack=mLwrLid,                                              
                                              trackAttr = 'paramMidLwr',
                                              )
                
                
                
                
                
                
                """
                import cgm.core.lib.locator_utils as LOC
                for tag,p in d_handles.iteritems():
                    mHandle,mJointHandle = create_lidHandle(self,tag,p,jointTrack = )
                    md_lidHandles[tag] = mHandle"""
                    
                ml_handles.extend([mLidRoot,mUprHandle,mLwrHandle])
        
        
        self.msgList_connect('prerigHandles', ml_handles)
        
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
    pprint.pprint( _d_base )
    
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
    if self.hasEyeOrb:
        mEyeOrbJoint = mEyeJoint.doDuplicate()
        self.copyAttrTo(_baseNameAttrs[1],mEyeOrbJoint.mNode,'cgmName',driven='target')
        name(mEyeOrbJoint,_d_base)
        
        mEyeJoint.p_parent = mEyeOrbJoint
        ml_joints.insert(0,mEyeOrbJoint)
        mPrerigNull.connectChildNode(mEyeOrbJoint.mNode,'eyeOrbJoint')
        mRoot = mEyeOrbJoint

    if len(ml_joints) > 1:
        ml_joints[0].getParent(asMeta=1).radius = ml_joints[-1].radius * 5
        
    if self.setupLid:#=====================================================
        _setupLid = self.getEnumValueString('setupLid')
        log.debug("|{0}| >> EyeLid setup: {1}.".format(_str_func,_setupLid))
        
        #'lidRootHelper'
        
        mLidsHelper = self.getMessageAsMeta('lidsHelper')
        _d_lids = copy.copy(_d_base)
        
        _d_lids['cgmNameModifier'] = 'lid'
        
        if _setupLid == 'clam':
            
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

        else:
            log.error("Don't have setup for eyelidType: {0}".format(_setupLid))
            
    
    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    self.atBlockUtils('skeleton_connectToParent')

    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
    for mJnt in ml_joints:mJnt.rotateOrder = 5
        
    return ml_joints    

    return
    

    
    
    
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    p = POS.get( ml_prerigHandles[-1].jointHelper.mNode )
    mHeadHelper = ml_templateHandles[0].orientHelper
    
    #...create ---------------------------------------------------------------------------
    mHead_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
    mHead_jnt.parent = False
    #self.copyAttrTo(_baseNameAttrs[-1],mHead_jnt.mNode,'cgmName',driven='target')
    
    #...orient ----------------------------------------------------------------------------
    #cgmMeta.cgmObject().getAxisVector
    CORERIG.match_orientation(mHead_jnt.mNode, mHeadHelper.mNode)
    JOINT.freezeOrientation(mHead_jnt.mNode)
    
    #...name ----------------------------------------------------------------------------
    #mHead_jnt.doName()
    #mHead_jnt.rename(_l_namesToUse[-1])
    for k,v in _l_namesToUse[-1].iteritems():
        mHead_jnt.doStore(k,v)
    mHead_jnt.doName()
    
    if self.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))
        if len(ml_prerigHandles) == 2 and self.neckJoints == 1:
            log.debug("|{0}| >> Single neck joint...".format(_str_func))
            p = POS.get( ml_prerigHandles[0].jointHelper.mNode )
            
            mBaseHelper = ml_prerigHandles[0].orientHelper
            
            #...create ---------------------------------------------------------------------------
            mNeck_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
            
            #self.copyAttrTo(_baseNameAttrs[0],mNeck_jnt.mNode,'cgmName',driven='target')
            
            #...orient ----------------------------------------------------------------------------
            #cgmMeta.cgmObject().getAxisVector
            TRANS.aim_atPoint(mNeck_jnt.mNode,
                              mHead_jnt.p_position,
                              'z+', 'y+', 'vector',
                              vectorUp=mHeadHelper.getAxisVector('z-'))
            JOINT.freezeOrientation(mNeck_jnt.mNode)
            
            #mNeck_jnt.doName()
            
            mHead_jnt.p_parent = mNeck_jnt
            ml_joints.append(mNeck_jnt)
            
            #mNeck_jnt.rename(_l_namesToUse[0])
            for k,v in _l_namesToUse[0].iteritems():
                mNeck_jnt.doStore(k,v)
            mNeck_jnt.doName()
        else:
            log.debug("|{0}| >> Multiple neck joint...".format(_str_func))
            
            _d = self.atBlockUtils('skeleton_getCreateDict', self.neckJoints +1)
            
            mOrientHelper = ml_prerigHandles[0].orientHelper
            
            ml_joints = JOINT.build_chain(_d['positions'][:-1], parent=True, worldUpAxis= mOrientHelper.getAxisVector('z-'))
            
            for i,mJnt in enumerate(ml_joints):
                #mJnt.rename(_l_namesToUse[i])
                for k,v in _l_namesToUse[i].iteritems():
                    mJnt.doStore(k,v)
                mJnt.doName()                
            
            #self.copyAttrTo(_baseNameAttrs[0],ml_joints[0].mNode,'cgmName',driven='target')
            
        mHead_jnt.p_parent = ml_joints[-1]
        ml_joints[0].parent = False
    else:
        mHead_jnt.parent = False
        #mHead_jnt.rename(_l_namesToUse[-1])
        
    ml_joints.append(mHead_jnt)
    
    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
    if len(ml_joints) > 1:
        mHead_jnt.radius = ml_joints[-1].radius * 5

    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    self.atBlockUtils('skeleton_connectToParent')
    
    return ml_joints


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
    
    str_lidSetup = mBlock.getEnumValueString('setupLid')
    if str_lidSetup not in ['clam','none']:
        self.l_precheckErrors.append("Lid setup not completed: {0}".format(str_lidSetup))
    
    

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
    
    mEyeTemplateHandle = mBlock.bbHelper
    
    self.mRootTemplateHandle = mEyeTemplateHandle
    ml_templateHandles = [mEyeTemplateHandle]
    
    self.b_scaleSetup = mBlock.scaleSetup
    
    self.str_lidSetup = False
    if mBlock.setupLid:
        self.str_lidSetup  = mBlock.getEnumValueString('setupLid')
        
    #Logic checks ========================================================================
    self.b_needEyeOrb = False
    if not mBlock.hasEyeOrb and self.str_lidSetup:
        self.b_needEyeOrb = True
    
    #Offset ============================================================================    
    str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
    
    if not mBlock.getMayaAttr('offsetMode'):
        log.debug("|{0}| >> default offsetMode...".format(_str_func))
        self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
    else:
        str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
        log.debug("|{0}| >> offsetMode: {1}".format(_str_func,str_offsetMode))
        
        l_sizes = []
        for mHandle in ml_templateHandles:
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
    self.mEyeLook = self.UTILS.eyeLook_get(self,True)#autobuild...

    return True


@cgmGEN.Timer
def rig_skeleton(self):
    _short = self.d_block['shortName']
    
    _str_func = 'rig_skeleton'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mPrerigNull = mBlock.prerigNull
    
    ml_jointsToConnect = []
    ml_jointsToHide = []
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
    
    if mBlock.ikSetup:
        log.debug("|{0}| >> Eye IK...".format(_str_func))              
        mEyeFK = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,[mEyeJoint],
                                                         'fk', mRigNull,
                                                         'fkEye',
                                                         cgmType = False,
                                                         singleMode = True)[0]
        
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
        
        for mJnt in mEyeFK,mEyeIK,mEyeBlend:
            mJnt.p_parent = mEyeRigJoint.p_parent
        
        mEyeRigJoint.p_parent = mEyeBlend
        
        ml_jointsToConnect.extend([mEyeIK])
        ml_jointsToHide.append(mEyeBlend)    
    log.debug(cgmGEN._str_subLine)
    
    #EyeLid =====================================================================================
    log.debug("|{0}| >> Eye...".format(_str_func)+'-'*40)
    reload(BLOCKUTILS)
    if self.str_lidSetup == 'clam':
        self.d_lidData = {}
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
            
            #ml_jointsToHide.extend([mLidBlend])
            #ml_jointsToConnect.extend([mLidRoot])
            
            mLidRig.p_parent = mLidBlend
            
        pprint.pprint(self.d_lidData)
    log.debug(cgmGEN._str_subLine)
    
    
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
        
        if mBlock.hasEyeOrb or mBlock.ikSetup or self.b_needEyeOrb:
            log.debug("|{0}| >> Settings needed...".format(_str_func))
            mSettingsHelper = mBlock.getMessageAsMeta('settingsHelper')
            if not mSettingsHelper:
                raise ValueError,"Settings helper should have been generated during prerig phase. Please go back"
            log.debug(mSettingsHelper)
            
            if mBlock.hasEyeOrb:
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
            mSettings.doStore('cgmName','eyeRoot')
            mSettings.doName()
                
            mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
        
        
        #Logic ====================================================================================
        mFKEye = mRigNull.getMessageAsMeta('fkEye')
        if mFKEye:
            log.debug("|{0}| >> FK eye...".format(_str_func))  
            log.debug(mFKEye)
            
            _shape_fk = CURVES.create_fromName('sphere', size = [v*1.1 for v in self.v_baseSize])
            SNAP.go(_shape_fk,mFKEye.mNode)
            mHandleFactory.color(_shape_fk, controlType = 'main')
            CORERIG.shapeParent_in_place(mFKEye.mNode,_shape_fk,False)
            
            #mShape = mBlock.getMessageAsMeta('bbHelper').doDuplicate()
            mRigNull.connectChildNode(mFKEye.mNode,'controlFK','rigNull')#Connect
            
        
        mIKEye = mRigNull.getMessageAsMeta('ikEye')
        if mIKEye:
            log.debug("|{0}| >> IK eye...".format(_str_func))  
            log.debug(mIKEye)
            
            #Create shape... -----------------------------------------------------------------------        
            log.debug("|{0}| >> Creating shape...".format(_str_func))
            mIKControl = cgmMeta.asMeta( CURVES.create_fromName('eye',
                                                                direction = 'z+',
                                                                size = self.f_sizeAvg * .5 ,
                                                                absoluteSize=False),'cgmObject',setClass=True)
            mIKControl.doSnapTo(mBlock.mNode)
            pos = mBlock.getPositionByAxisDistance('z+',
                                                   self.f_sizeAvg * 4)
        
            mIKControl.p_position = pos
        
            
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
            
            #for s in mDirectEye.getShapes(asMeta=True):
                #s.overrideEnabled = 1
                #s.overrideDisplayType = 2
                
        if self.str_lidSetup:#Lid setup =======================================================================
            log.debug("|{0}| >> Lid setup: {1}".format(_str_func,self.str_lidSetup))
            if self.str_lidSetup == 'clam':
                for k in 'upr','lwr':
                    log.debug("|{0}| >> lid handle| {1}...".format(_str_func,k))                      
                    _key = '{0}LidHandle'.format(k)
                    mShapeSource = mBlock.getMessageAsMeta(_key)
                    mHandle = mShapeSource.doCreateAt('joint',setClass=True)
                    
                    try:mHandle.drawStyle =2
                    except:mHandle.radius = .00001
                    
                    CORERIG.shapeParent_in_place(mHandle.mNode,mShapeSource.mNode)
                    mHandle.doStore('cgmName','{0}Lid'.format(k),attrType='string')
                    
                    if self.mModule.hasAttr('cgmDirection'):
                        mHandle.doStore('cgmDirection',self.mModule.cgmDirection)
                    
                    self.d_lidData[k]['mHandle'] = mHandle
                    mHandle.doName()
                    mRigNull.connectChildNode(mHandle,_key,'rigNull')#Connect
                    
                    log.debug("|{0}| >> lid direct| {1}...".format(_str_func,k))
                    mRig =  self.d_lidData[k]['mRig']
                    
                    _shape = CURVES.create_controlCurve(mRig.mNode, 'cube',
                                                        sizeMode= 'fixed',
                                                        size = mRig.radius)
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
        ml_controlsAll = [self.mEyeLook]#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
        
        d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')
        
        mControlFK = mRigNull.getMessageAsMeta('fkEye')
        mControlIK = mRigNull.getMessageAsMeta('controlIK')
        mSettings = mRigNull.getMessageAsMeta('settings')
        mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
        mDirect = mRigNull.getMessageAsMeta('directEye')
        
        # Drivers ==========================================================================================    
        if mBlock.ikSetup:
            mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
            
    
        #>> vis Drivers ==============================================================================	
        mPlug_visSub = self.atBuilderUtils('build_visSub')
        mPlug_visDirect = cgmMeta.cgmAttr(mSettings,'visDirect', value = True,
                                          attrType='bool', defaultValue = False,
                                          keyable = False,hidden = False)
        
        #Settings ========================================================================================
        if mSettings:
            log.debug("|{0}| >> Found settings : {1}".format(_str_func, mSettings))
            
            _d = MODULECONTROL.register(mSettings,
                                        addDynParentGroup = False,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ")
            
            mSettings = _d['mObj']
            ml_controlsAll.append(mSettings)
            
        
        
        #FK ========================================================================================    
        log.debug("|{0}| >> Found fk : {1}".format(_str_func, mControlFK))
        
        _d = MODULECONTROL.register(mControlFK,
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

        
        if self.str_lidSetup:#Lid setup =======================================================================
            log.debug("|{0}| >> Lid setup: {1}".format(_str_func,self.str_lidSetup))
            
            cgmMeta.cgmAttr(mSettings.mNode,
                            'blink',attrType='float',
                            minValue=0,maxValue=1,
                            lock=False,keyable=True)
            cgmMeta.cgmAttr(mSettings.mNode,
                            'blinkHeight',attrType='float',
                            minValue=0,maxValue=1,
                            lock=False,keyable=True)            
            
            if self.str_lidSetup == 'clam':
                ml_handles = []
                for k in 'upr','lwr':
                    log.debug("|{0}| >> lid | {1}...".format(_str_func,k))
                    _key = '{0}LidHandle'.format(k)
                    mHandle = self.d_lidData[k]['mHandle']
                    mRig = self.d_lidData[k]['mRig']
                    
                    MODULECONTROL.register(mHandle,
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
        """
        if mHeadIK:
            ATTR.set(mHeadIK.mNode,'rotateOrder',self.ro_head)
        if mHeadLookAt:
            ATTR.set(mHeadLookAt.mNode,'rotateOrder',self.ro_headLookAt)
            """
        
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

    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mRootParent = self.mDeformNull
    mModule = self.mModule
    
    mControlFK = mRigNull.getMessageAsMeta('fkEye')
    mJointFK = mControlFK
    mJointIK = mRigNull.getMessageAsMeta('ikEye')
    mControlIK = mRigNull.getMessageAsMeta('controlIK')
    mSettings = mRigNull.getMessageAsMeta('settings')
    mBlendJoint = mRigNull.getMessageAsMeta('blendEye')
    mDirect = mRigNull.getMessageAsMeta('directEye')
    
    ml_joints = [mJointFK,mJointIK,mBlendJoint,mSettings,mDirect]
    
    pprint.pprint(vars())
    
    log.debug("|{0}| >> Adding to attach driver...".format(_str_func))
    self.mDeformNull.p_parent = self.md_dynTargetsParent['attachDriver'].mNode    
    if mSettings:
        mSettings.masterGroup.p_parent = self.mDeformNull
        
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
        mc.aimConstraint(mControlIK.mNode,
                         mJointIK.mNode,
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
    
        mIKGroup.parent = mSettings
        mControlIK.masterGroup.parent = mIKGroup
        mJointIK.p_parent = mIKGroup
        
        #FK...
        FKGroup = mSettings.doCreateAt()
        FKGroup.doStore('cgmName',self.d_module['partName'])        
        FKGroup.doStore('cgmTypeModifier','FK')
        FKGroup.doName()
        mPlug_FKon.doConnectOut("{0}.visibility".format(FKGroup.mNode))
    
        FKGroup.parent = mSettings
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
            
            
    else:
        #Setup blend ----------------------------------------------------------------------------------
        RIGCONSTRAINT.blendChainsBy(mJointFK,mJointIK,mBlendJoint,
                                    driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])
    
    
    mBlendJoint.p_parent = mSettings


    
    return


    

def create_clamBlinkCurves(self):
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
        mCrv.p_parent = mRigNull
        
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
    
    mPlug_autoFollow = cgmMeta.cgmAttr(mSettings,"autoFollow",attrType = 'float', value = 1.0,
                                       hidden = False,keyable=True,maxValue=1.0,minValue=0)	    
    self.mPlug_autoFollow = mPlug_autoFollow    
    
    mZeroLoc = mEyeJoint.doCreateAt()
    mZeroLoc.addAttr('cgmName','zero')
    mZeroLoc.doName()
    
    mZeroLoc.p_parent = mSettings
    
    md_dat = {}
    
    log.debug("|{0}| >> create nodes...".format(_str_func))    
    for k in 'upr','lwr':
        log.debug("|{0}| >> {1}...".format(_str_func,k))            
        _d = self.d_lidData[k]
        mRoot = _d['mRoot']
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
    ATTR.connect("{0}.outputG".format(_lwrClamp),
                 "{0}.r{1}".format(_lwrLoc,_str_orientation[1]))

    self.mPlug_lwrUpLimit = mPlug_lwrUpLimit#store
    self.mPlug_lwrDnLimit = mPlug_lwrDnLimit#store
    self.mPlug_lwrDnStart = mPlug_lwrDnStart#store
    
    #Contraints --------------------------------------------------------------   
    log.debug("|{0}| >> Contraints...".format(_str_func))
    d_autolidBlend = NODEFACTORY.createSingleBlendNetwork(mPlug_autoFollow,
                                                          [mSettings.mNode,'resultAutoFollowOff'],
                                                          [mSettings.mNode,'resultAutoFollowOn'],
                                                          hidden = True,keyable=False)    
    
    for k in 'upr','lwr':
        log.debug("|{0}| >> {1}...".format(_str_func,k))            
        _d = self.d_lidData[k]
        mRoot = _d['mRoot']
        mHandle = _d['mHandle']
        
        _const = mc.parentConstraint([mZeroLoc.mNode,
                                      md_dat[k]['mDriven'].mNode],
                                     mHandle.masterGroup.mNode,
                                     maintainOffset = True)[0]
        
        l_weightTargets = mc.parentConstraint(_const,q=True,weightAliasList = True)
        d_autolidBlend['d_result1']['mi_plug'].doConnectOut('%s.%s' % (_const,l_weightTargets[1]))
        d_autolidBlend['d_result2']['mi_plug'].doConnectOut('%s.%s' % (_const,l_weightTargets[0]))    
    
    
    
@cgmGEN.Timer
def rig_lidSetup(self):
    _short = self.d_block['shortName']
    _str_func = 'rig_lidSetup'
    log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    log.debug(self)

    if not self.str_lidSetup:
        log.debug("|{0}| >> No lid setup...".format(_str_func))
        return True
    
    _short = self.d_block['shortName']    
    _lidSetup = self.str_lidSetup
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mSettings = mRigNull.settings
    mRootParent = self.mConstrainNull
    mModule = self.mModule
    _jointOrientation = self.d_orientation['str']
    _side = mBlock.atUtils('get_side')

    
    if _lidSetup:
        log.debug("|{0}| >>  Lid setup ... ".format(_str_func)+'-'*40)
        
        
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
                mRoot = _d['mRoot']
                mBlend = _d['mBlend']
                mRig = _d['mRig']
                mHandle = _d['mHandle']
                
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
                                 worldUpType = 'objectRotation' )
                
                mRoot.p_parent = mSettings
                mHandle.masterGroup.p_parent = mSettings
        
        
        #Autofollow --------------------------------------------------------------------
        create_lidFollow(self)

    
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
        pprint.pprint(ml_targetDynParents)        
        
        log.debug(cgmGEN._str_subLine)


    #Settings =================================================================================
    log.debug("|{0}| >> Settings...".format(_str_func))
    mSettings.visDirect = 0
    
    mPlug_FKIK = cgmMeta.cgmAttr(mSettings,'FKIK')
    mPlug_FKIK.p_defaultValue = 1
    mPlug_FKIK.value = 1
        
    #Lock and hide =================================================================================
    mBlendJoint.dagLock(True)
        
    ml_controls = mRigNull.msgList_get('controlsAll')
    self.UTILS.controls_lockDown(ml_controls)
    
    if not mBlock.scaleSetup:
        log.debug("|{0}| >> No scale".format(_str_func))
        ml_controlsToLock = copy.copy(ml_controls)
        for mCtrl in ml_controlsToLock:
            ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
    else:
        log.debug("|{0}| >>  scale setup...".format(_str_func))
        
        
    self.mDeformNull.dagLock(True)
    
    
    #Lid Defaults ===============================================================
    if self.str_lidSetup:
        mPlug_autoFollow = self.mPlug_autoFollow
        mPlug_leftLimit = self.mPlug_leftLimit#store
        mPlug_rightLimit = self.mPlug_rightLimit#store
        mPlug_uprUpLimit = self.mPlug_uprUpLimit#store
        mPlug_uprDnLimit = self.mPlug_uprDnLimit#store	
        mPlug_lwrUpLimit = self.mPlug_lwrUpLimit#store
        mPlug_lwrDnLimit = self.mPlug_lwrDnLimit#store
        mPlug_lwrDnStart = self.mPlug_lwrDnStart#store		
    
        _l_defaults = [{"plug":mPlug_autoFollow,'setting':1},
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
    mBlock.UTILS.set_blockNullTemplateState(mBlock)
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
    _short = self.d_block['shortName']
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    mPrerigNull = mBlock.prerigNull
    directProxy = mBlock.proxyDirect
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    ml_neckProxy = []
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"
    self.v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    
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
            else:
                return _bfr
        
    #>> Eye ===================================================================================
    log.debug("|{0}| >> Eye...".format(_str_func))
    
    #if directProxy:
    #    log.debug("|{0}| >> directProxy... ".format(_str_func))
    #    _settings = self.mRigNull.settings.mNode
        
    mDirect = mRigNull.getMessageAsMeta('directEye')
    
    mProxyEye = cgmMeta.validateObjArg(CORERIG.create_proxyGeo('sphere',
                                                               self.v_baseSize,ch=False)[0],
                                       'cgmObject',setClass=True)
    
    mProxyEye.doSnapTo(mDirect)
    mProxyEye.p_parent = mDirect
    
    ml_proxy = [mProxyEye]
    
    str_lidSetup = mBlock.getEnumValueString('setupLid')
    #>>Lid setup ================================================
    if str_lidSetup == 'clam':
        #Need to make our lid roots and orient
        for k in 'upr','lwr':
            log.debug("|{0}| >> {1}...".format(_str_func,k))
            _keyHandle = '{0}LidHandle'.format(k)
            
            mLidSkin = mPrerigNull.getMessageAsMeta('{0}LidJoint'.format(k))
            mRigJoint = mLidSkin.rigJoint
            
            mEndCurve = mBlock.getMessageAsMeta('{0}EndLidLoftCurve'.format(k)).doDuplicate(po=False)
            mEndCurve.p_parent = False
            mEndCurve.p_parent = self.mDeformNull
            mEndCurve.v = False
            
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
        
            mLoftSurface.p_parent = self.mModule
            mLoftSurface.resetAttrs()
        
            mLoftSurface.doStore('cgmName',"{0}_{1}Lid".format(self.d_module['partName'],k),attrType='string')
            mLoftSurface.doStore('cgmType','proxy')
            mLoftSurface.doName()
            log.debug("|{0}| loft node: {1}".format(_str_func,_loftNode))             
            
            
            
            #mLoft = mBlock.getMessageAsMeta('{0}LidTemplateLoft'.format(tag))
            #mMesh = mLoft.doDuplicate(po=False, ic=False)
            #mDag = mRigJoint.doCreateAt(setClass='cgmObject')
            #CORERIG.shapeParent_in_place(mDag.mNode, mMesh.mNode,False)
            #mDag.p_parent = mRigJoint
            ml_proxy.append(mLoftSurface)
    
    

    for mProxy in ml_proxy:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
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




















