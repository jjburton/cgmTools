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
import Red9.core.Red9_AnimationUtils as r9Anim
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
import cgm.core.rig.general_utils as RIGGEN
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

for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT,RIGGEN:
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
                       'rig_cleanUp']




d_wiring_skeleton = {'msgLinks':[],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull','noTransPrerigNull']}
d_wiring_template = {'msgLinks':['templateNull','noTransTemplateNull'],
                     }
d_wiring_extraDags = {'msgLinks':['bbHelper'],
                      'msgLists':[]}
#>>>Profiles ==============================================================================================
d_build_profiles = {}


d_block_profiles = {'default':{},
                    'eyebrow':{'baseSize':[17.6,7.2,8.4],
                               'browType':'full',
                               'profileOptions':{},
                               'paramStart':.2,
                                'paramMid':.5,
                                'paramEnd':.7,                               
                               },
                    }

#>>>Attrs =================================================================================================
l_attrsStandard = ['side',
                   'position',
                   'baseAim',
                   'baseDat',
                   'attachPoint',
                   'nameList',
                   'loftDegree',
                   'loftSplit',
                   'scaleSetup',
                   'moduleTarget',]

d_attrsToMake = {'browType':'full:side',
                 'paramStart':'float',
                 'paramMid':'float',
                 'paramEnd':'float',
                 'addBrowUpr':'bool',
                 'addTemple':'bool',
                 'addEyeSqueeze':'bool',
                 'browSetup':'ribbon:undefined',
                 'numHandlesBrow':'int',
                 'numJointsBrow':'int',
                 'profileOptions':'string',
}

d_defaultSettings = {'version':__version__,
                     'attachPoint':'end',
                     'side':'none',
                     'nameList':['brow','squeeze'],
                     'loftDegree':'cubic',
                     'paramStart':.2,
                     'paramMid':.5,
                     'paramEnd':1.0,
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
    
    #Attributes =========================================================
    ATTR.set_alias(_short,'sy','blockScale')    
    self.setAttrFlags(attrs=['sx','sz','sz'])
    self.doConnectOut('sy',['sx','sz'])

    ATTR.set_min(_short, 'loftSplit', 1)
    
    #Cleaning =========================================================        
    _shapes = self.getShapes()
    if _shapes:
        log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
        mc.delete(_shapes)
        defineNull = self.getMessage('defineNull')
        if defineNull:
            log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
            mc.delete(defineNull)
    
    ml_handles = []
    
    #rigBlock Handle ===========================================================
    log.debug("|{0}| >>  RigBlock Handle...".format(_str_func))            
    _size = MATH.average(self.baseSize[1:])
    _crv = CURVES.create_fromName(name='locatorForm',#'axis3d',#'arrowsAxis', 
                                  direction = 'z+', size = _size/4)
    SNAP.go(_crv,self.mNode,)
    CORERIG.override_color(_crv, 'white')        
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    mHandleFactory = self.asHandleFactory()
    self.addAttr('cgmColorLock',True,lock=True, hidden=True)
    mDefineNull = self.atUtils('stateNull_verify','define')
    
    #Bounding sphere ==================================================================
    _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
    mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
    mBBShape.p_parent = mDefineNull    
    mBBShape.tz = -.5
    mBBShape.ty = .5
    
    
    CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
    self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
    mHandleFactory.color(mBBShape.mNode,controlType='sub')
    mBBShape.setAttrFlags()
    
    mBBShape.doStore('cgmName', self)
    mBBShape.doStore('cgmType','bbVisualize')
    mBBShape.doName()    
    
    self.connectChildNode(mBBShape.mNode,'bbHelper')
    
    return

        
    
    self.msgList_connect('defineSubHandles',ml_handles)#Connect
    
    
 
 

#=============================================================================================================
#>> Template
#=============================================================================================================
def mirror_self(self,primeAxis = 'Left'):
    _str_func = 'mirror_self'
    _idx_state = self.getState(False)

    if _idx_state > 0:
        log.debug("|{0}| >> template...".format(_str_func)+ '-'*80)
        ml_mirrorHandles = self.msgList_get('templateHandles')
        r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                                     mode = '',primeAxis = primeAxis.capitalize() )
    if _idx_state > 1:
        log.debug("|{0}| >> prerig...".format(_str_func)+ '-'*80)        
        ml_mirrorHandles = self.msgList_get('prerigHandles')
        r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                                 mode = '',primeAxis = primeAxis.capitalize() )        
    

def mirror_template(self,primeAxis = 'Left'):
    _str_func = 'mirror_template'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    ml_mirrorHandles = self.msgList_get('templateHandles')
    
    r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                             mode = '',primeAxis = primeAxis.capitalize() )
    
def mirror_prerig(self,primeAxis = 'Left'):
    _str_func = 'mirror_template'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    ml_mirrorHandles = self.msgList_get('prerigHandles')
    
    r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                             mode = '',primeAxis = primeAxis.capitalize() )    

def templateDelete(self):
    _str_func = 'templateDelete'
    log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    ml_defSubHandles = self.msgList_get('defineSubHandles')
    for mObj in ml_defSubHandles:
        mObj.template = False    
            
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
        #_side = self.UTILS.get_side(self)
        #_eyeType = self.getEnumValueString('eyeType')
                
        #if _eyeType not in ['sphere']:
        #    return log.error("|{0}| >> loft setup mode not done: {1}".format(_str_func,_loftSetup))
        
        
        #Create temple Null  ==================================================================================
        mTemplateNull = BLOCKUTILS.templateNull_verify(self)
        mNoTransformNull = self.atUtils('noTransformNull_verify','template')
        
        mHandleFactory = self.asHandleFactory()
        
        self.bbHelper.v = False
        _size = MATH.average(self.baseSize[1:])
        
        d_handleTags = {}
        md_loftCurves = {}
        md_curves = []
        
        #Brow Handles  ==================================================================================
        log.debug("|{0}| >> Brow Handles...".format(_str_func)+ '-'*40)
        
        """
        _sideMult = 1
        _axisOuter = 'x+'
        _axisInner = 'x-'
        
        if self.side == 1:
            _sideMult = -1
            _axisOuter = 'x-'
            _axisInner = 'x+'
            """
        
        if self.browType == 0:#Full brow
            log.debug("|{0}| >>  Full Brow...".format(_str_func))            
            _d_pairs = {'browLeft':'browRight',
                        'browMidLeft':'browMidRight',
                        'browMidLeftUp':'browMidRightUp',                        
                        'browLeftUp':'browRightUp'}
            
            _d = {#'aim':{'color':'yellowBright','defaults':{'tz':1}},
                  'browCenter':{'color':'yellowBright','tagOnly':True,'arrow':False,
                                'vectorLine':False,'defaults':{}},
                  'browLeft':{'color':'blue','tagOnly':True,'arrow':False,'jointLabel':False,
                              'vectorLine':False,'defaults':{'tx':2}},
                  'browRight':{'color':'red','tagOnly':True,'arrow':False,'jointLabel':False,
                               'vectorLine':False,'defaults':{'tx':-2}},
                  'browMidLeft':{'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':False,
                              'vectorLine':False,'defaults':{'tx':1}},
                  'browMidRight':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':False,
                               'vectorLine':False,'defaults':{'tx':-1}},
                  'templeLeft':{'color':'blueSky','tagOnly':True,'arrow':False,'jointLabel':False,
                              'vectorLine':False,'defaults':{'tx':2,'tz':-1}},
                  'templeRight':{'color':'redWhite','tagOnly':True,'arrow':False,'jointLabel':False,
                               'vectorLine':False,'defaults':{'tx':-2,'tz':-1}},
                  'browCenterUp':{'color':'yellowBright','tagOnly':True,'parentTag':'browCenter',
                                  'jointLabel':False,
                                   'defaults':{'ty':2.0}},
                  'browLeftUp':{'color':'blueSky','tagOnly':True,'parentTag':'browLeft','jointLabel':False,
                              'defaults':{'tx':2,'ty':2}},
                  'browRightUp':{'color':'redWhite','tagOnly':True,'parentTag':'browRight','jointLabel':False,
                              'defaults':{'tx':-2,'ty':2}},
                  'browMidLeftUp':{'color':'blueSky','tagOnly':True,'parentTag':'browMidLeft','jointLabel':False,
                                'defaults':{'tx':1,'ty':2}},
                  'browMidRightUp':{'color':'redWhite','tagOnly':True,'parentTag':'browMidRight','jointLabel':False,
                                 'defaults':{'tx':-1,'ty':2}},                  
                  'templeLeftUp':{'color':'blueSky','tagOnly':True,'parentTag':'templeLeft','jointLabel':False,
                                 'defaults':{'tx':2,'ty':2,'tz':-1}},
                  'templeRightUp':{'color':'redWhite','tagOnly':True,'parentTag':'templeRight','jointLabel':False,
                                    'defaults':{'tx':-2,'ty':2,'tz':-1}},              
                  }        

            _l_order = ['browCenter','browLeft','browRight','browMidLeft','browMidRight',
                        'browCenterUp','browLeftUp','browRightUp','browMidLeftUp','browMidRightUp']
                        
            #if self.addTemple:
            _l_order.extend(['templeLeft','templeRight','templeLeftUp','templeRightUp'])
            _d_pairs['templeLeft']='templeRight'
            _d_pairs['templeLeftUp']='templeRightUp'
            
            md_res = self.UTILS.create_defineHandles(self, _l_order, _d, _size / 5, mTemplateNull)
        
            md_handles = md_res['md_handles']
            ml_handles = md_res['ml_handles']
            
            idx_ctr = 0
            idx_side = 0
            
            for mHandle in ml_handles:
                mHandle._verifyMirrorable()
                _str_handle = mHandle.p_nameBase
                if 'Center' in _str_handle:
                    mHandle.mirrorSide = 0
                    mHandle.mirrorIndex = idx_ctr
                    idx_ctr +=1
                mHandle.mirrorAxis = "translateX,rotateY,rotateZ"
    
            #Self mirror wiring -------------------------------------------------------
            for k,m in _d_pairs.iteritems():
                md_handles[k].mirrorSide = 1
                md_handles[m].mirrorSide = 2
                md_handles[k].mirrorIndex = idx_side
                md_handles[m].mirrorIndex = idx_side
                md_handles[k].doStore('mirrorHandle',md_handles[m])
                md_handles[m].doStore('mirrorHandle',md_handles[k])
                idx_side +=1
            
            
            """
            d_positions = {'inner':self.getPositionByAxisDistance(_axisOuter,_size*.5),
                           'outer':self.getPositionByAxisDistance(_axisInner,_size*.5),
                           'upr':self.getPositionByAxisDistance('y+',_size*.25),
                           'lwr':self.getPositionByAxisDistance('y-',_size*.25),
                           }
            md_handles['inner'].p_position = d_positions['inner']
            md_handles['outer'].p_position = d_positions['outer']
            md_handles['upr'].p_position = d_positions['upr']
            md_handles['lwr'].p_position = d_positions['lwr']
            
            
            _crvUpr = CORERIG.create_at(create='curve',l_pos = [d_positions['inner'],
                                                                d_positions['upr'],
                                                                d_positions['outer']])
            
            _crvLwr = CORERIG.create_at(create='curve',l_pos = [d_positions['inner'],
                                                                d_positions['lwr'],
                                                                d_positions['outer']])"""        
        
            
            #Get our curve handles -----------------------------------------------
            d_handleTags = {}
            d_handleTags['browLine'] = ['templeRight','browRight','browMidRight','browCenter',
                                       'browMidLeft','browLeft','templeLeft']
            
            d_handleTags['browUpr'] = ['templeRightUp','browRightUp','browMidRightUp',
                                       'browCenterUp','browMidLeftUp','browLeftUp',
                                       'templeLeftUp']
            
            d_handleTags['browLeft'] = ['browCenter','browMidLeft','browLeft','templeLeft']
            d_handleTags['browRight'] = ['browCenter','browMidRight','browRight','templeRight']
        
        self.msgList_connect('templateHandles',ml_handles)#Connect
        
        
        #Track curve --------------------------------------------------------------------------
        log.debug("|{0}| >> TrackCrvs...".format(_str_func)+'-'*40) 
        
        for tag,l_tags in d_handleTags.iteritems():
            log.debug("|{0}| >>  curve: {1}...".format(_str_func,tag))            
            
            l_pos = []
            for k in l_tags:
                l_pos.append(md_handles[k].p_position)
            
            _crv = mc.curve(d=1,p=l_pos)
            #CORERIG.create_at(create='curve',l_pos = l_pos)
            mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
            mCrv.p_parent = mNoTransformNull
            mHandleFactory.color(mCrv.mNode)
            mCrv.rename('{0}_loftCurve'.format(tag))            
            mCrv.v=False
            md_loftCurves[tag] = mCrv
            
            self.connectChildNode(mCrv, tag+'loftCurve','block')
            
            
            l_clusters = []
            for i,cv in enumerate(mCrv.getComponents('cv')):
                _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(md_handles[l_tags[i]].p_nameBase,i))
                TRANS.parent_set( _res[1], md_handles[l_tags[i]].mNode)
                l_clusters.append(_res)
                ATTR.set(_res[1],'visibility',False)
        
            #pprint.pprint(l_clusters)
            mc.rebuildCurve(mCrv.mNode, d=3, keepControlPoints=False,ch=1,s=8,
                            n="{0}_reparamRebuild".format(md_handles[l_tags[i]].p_nameBase))
            
        #Build our brow loft --------------------------------------------------------------------------
        log.debug("|{0}| >> Loft...".format(_str_func)+'-'*40) 
        self.UTILS.create_simpleTemplateLoftMesh(self,
                                                 [md_loftCurves['browLine'].mNode,
                                                  md_loftCurves['browUpr'].mNode],
                                                 mTemplateNull,
                                                 polyType = 'bezier',
                                                 baseName = 'brow')
        
        #Build our brow loft --------------------------------------------------------------------------
        log.debug("|{0}| >> Visualize brow...".format(_str_func)+'-'*40)
        md_directCurves = {}
        for tag in ['browLeft','browRight']:
            mCrv = md_loftCurves[tag]
            ml_temp = []
            for k in ['start','mid','end']:
                mLoc = cgmMeta.asMeta(self.doCreateAt())
                mJointLabel = mHandleFactory.addJointLabel(mLoc,k)
                
                self.connectChildNode(mLoc, tag+k.capitalize()+'templateHelper','block')
                
                mLoc.rename("{0}_{1}_templateHelper".format(tag,k))
                
                mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,
                                                                             turnOnPercentage=True))
                
                mPointOnCurve.doConnectIn('parameter',"{0}.{1}".format(self.mNode,"param{0}".format(k.capitalize())))
            
            
                mPointOnCurve.doConnectOut('position',"{0}.translate".format(mLoc.mNode))
            
                mLoc.p_parent = mNoTransformNull
                ml_temp.append(mLoc)
                #mLoc.v=False
                #mc.pointConstraint(mTrackLoc.mNode,mTrackGroup.mNode)
                
            #Joint curves......
            _crv = mc.curve(d=1,p=[mObj.p_position for mObj in ml_temp])
            
            #CORERIG.create_at(create='curve',l_pos = l_pos)
            mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
            mCrv.p_parent = mNoTransformNull
            mHandleFactory.color(mCrv.mNode)
            mCrv.rename('{0}_jointCurve'.format(tag))            
            mCrv.v=False
            md_loftCurves[tag] = mCrv
        
            self.connectChildNode(mCrv, tag+'JointCurve','block')
        
            l_clusters = []
            for i,cv in enumerate(mCrv.getComponents('cv')):
                _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(ml_temp[i].p_nameBase,i))
                TRANS.parent_set( _res[1], ml_temp[i].mNode)
                l_clusters.append(_res)
                ATTR.set(_res[1],'visibility',False)
                
            mc.rebuildCurve(mCrv.mNode, d=3, keepControlPoints=False,ch=1,s=8,
                            n="reparamRebuild")
        
        

        
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerigDelete(self):
    try:self.moduleEyelid.delete()
    except:pass
    
    self.noTransTemplateNull.v=True
    
def create_handle(self,tag,pos,mJointTrack=None,
                  trackAttr=None,visualConnection=True,
                  nameEnd = 'BrowHandle'):
    mHandle = cgmMeta.validateObjArg( CURVES.create_fromName('circle', size = _size_sub), 
                                      'cgmObject',setClass=1)
    mHandle.doSnapTo(self)

    mHandle.p_position = pos

    mHandle.p_parent = mStateNull
    mHandle.doStore('cgmName',tag)
    mHandle.doStore('cgmType','templateHandle')
    mHandle.doName()

    mHandleFactory.color(mHandle.mNode,controlType='sub')

    self.connectChildNode(mHandle.mNode,'{0}nameEnd'.format(tag),'block')

    return mHandle

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

def prerig(self):
    try:
        _str_func = 'prerig'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        self.blockState = 'prerig'
        _side = self.UTILS.get_side(self)
        
        self.atUtils('module_verify')
        mStateNull = self.UTILS.stateNull_verify(self,'prerig')
        mNoTransformNull = self.atUtils('noTransformNull_verify','prerig')
        self.noTransTemplateNull.v=False
        
        #mRoot = self.getMessageAsMeta('rootHelper')
        mHandleFactory = self.asHandleFactory()
        
        ml_handles = []
        md_handles = {'brow':{'center':[],
                              'left':[],
                              'right':[]}}
        md_jointHandles = {'brow':{'center':[],
                              'left':[],
                              'right':[]}}
        #Get base dat =============================================================================    
        mBBHelper = self.bbHelper
        mBrowLoft = self.getMessageAsMeta('browTemplateLoft')
        
        _size = MATH.average(self.baseSize[1:])
        _size_base = _size * .25
        _size_sub = _size_base * .5
        
        idx_ctr = 0
        idx_side = 0
        
        def create_handle(mHelper, mSurface, tag, k, side, controlType = 'main', aimGroup = 1,nameDict = None):
            mHandle = cgmMeta.validateObjArg( CURVES.create_fromName('squareRounded', size = _size_sub), 
                                              'cgmControl',setClass=1)
            mHandle._verifyMirrorable()
            
            mHandle.doSnapTo(self)
            mHandle.p_parent = mStateNull
            
            if nameDict:
                RIGGEN.store_and_name(mHandle,nameDict)
            else:
                mHandle.doStore('cgmName',tag)
                mHandle.doStore('cgmType','prerigHandle')
                mHandle.doName()
                
                
            _key = tag
            if k:
                _key = _key+k.capitalize()
            mMasterGroup = mHandle.doGroup(True,True,
                                           asMeta=True,
                                           typeModifier = 'master',
                                           setClass='cgmObject')
        
            mc.pointConstraint(mHelper.mNode,mMasterGroup.mNode,maintainOffset=False)
        
            mHandleFactory.color(mHandle.mNode,side = side, controlType=controlType)
            mStateNull.connectChildNode(mHandle, _key+'prerigHelper','block')
        
            mc.normalConstraint(mSurface.mNode, mMasterGroup.mNode,
                                aimVector = [0,0,1], upVector = [0,1,0],
                                worldUpObject = self.mNode,
                                worldUpType = 'objectrotation', 
                                worldUpVector = [0,1,0])
        
            if aimGroup:
                mHandle.doGroup(True,True,
                                asMeta=True,
                                typeModifier = 'aim',
                                setClass='cgmObject')
        
        
            mHandle.tz = _size_sub
            
            return mHandle
        
        def create_jointHelper(mPos, mSurface, tag, k, side, nameDict=None, aimGroup = 1):
            
            mHandle = cgmMeta.validateObjArg( CURVES.create_fromName('axis3d', size = _size_sub * .5), 
                                              'cgmControl',setClass=1)
            mHandle._verifyMirrorable()
            
            mHandle.doSnapTo(self)
            mHandle.p_parent = mStateNull
            if nameDict:
                RIGGEN.store_and_name(mHandle,nameDict)
                _dCopy = copy.copy(nameDict)
                _dCopy.pop('cgmType')
                mJointLabel = mHandleFactory.addJointLabel(mHandle,NAMETOOLS.returnCombinedNameFromDict(_dCopy))
                
            else:
                mHandle.doStore('cgmName',tag)
                mHandle.doStore('cgmType','jointHelper')
                mHandle.doName()
            
            _key = tag
            if k:
                _key = "{0}_{1}".format(tag,k)
            
            
            
            mMasterGroup = mHandle.doGroup(True,True,
                                           asMeta=True,
                                           typeModifier = 'master',
                                           setClass='cgmObject')
    
            mc.pointConstraint(mPos.mNode,mMasterGroup.mNode,maintainOffset=False)
    
            #mHandleFactory.color(mHandle.mNode,side = side, controlType='sub')
            mStateNull.connectChildNode(mHandle, _key+'prerigHelper','block')
    
            mc.normalConstraint(mSurface.mNode, mMasterGroup.mNode,
                                aimVector = [0,0,1], upVector = [0,1,0],
                                worldUpObject = self.mNode,
                                worldUpType = 'objectrotation', 
                                worldUpVector = [0,1,0])
    
            if aimGroup:
                mHandle.doGroup(True,True,
                                asMeta=True,
                                typeModifier = 'aim',
                                setClass='cgmObject')
    

            return mHandle        
        
        #Handles =====================================================================================
        log.debug("|{0}| >> Brow Handles..".format(_str_func)+'-'*40)
        
        _d = {'cgmName':'browCenter',
              'cgmType':'handleHelper'}
        
        mBrowCenterDefine = self.defineBrowcenterHelper
        md_handles['browCenter'] = [create_handle(mBrowCenterDefine,mBrowLoft,
                                                  'browCenter',None,'center',nameDict = _d)]
        md_handles['brow']['center'].append(md_handles['browCenter'])
        md_handles['browCenter'][0].mirrorIndex = idx_ctr
        idx_ctr +=1
        mStateNull.msgList_connect('browCenterPrerigHandles',md_handles['browCenter'])
        
        _d_nameHandleSwap = {'start':'inner',
                             'end':'outer'}
        for tag in ['browLeft','browRight']:
            _d['cgmName'] = tag
        
            for k in ['start','mid','end']:
                _d['cgmNameModifier'] = _d_nameHandleSwap.get(k,k)
                
                if 'Left' in tag:
                    _side = 'left'
                elif 'Right' in tag:
                    _side = 'right'
                else:
                    _side = 'center'
                
                if _side in ['left','right']:
                    _d['cgmDirection'] = _side
                    
                if k == 'mid':
                    _control = 'sub'
                else:
                    _control = 'main'
                    
                mTemplateHelper = self.getMessageAsMeta(tag+k.capitalize()+'templateHelper')
                
                mHandle = create_handle(mTemplateHelper,mBrowLoft,tag,k,_side,controlType = _control,nameDict = _d)
                md_handles['brow'][_side].append(mHandle)
                ml_handles.append(mHandle)
            mStateNull.msgList_connect('{0}PrerigHandles'.format(tag),md_handles['brow'][_side])


        #Joint helpers ------------------------
        log.debug("|{0}| >> Joint helpers..".format(_str_func)+'-'*40)
        _d = {'cgmName':'brow',
              'cgmDirection':'center',
              'cgmType':'jointHelper'}        
        
        mFullCurve = self.getMessageAsMeta('browLineloftCurve')
        md_jointHandles['browCenter'] = [create_jointHelper(mBrowCenterDefine,mBrowLoft,'center',None,
                                                            'center',nameDict=_d)]
        md_jointHandles['brow']['center'].append(md_jointHandles['browCenter'])
        md_jointHandles['browCenter'][0].mirrorIndex = idx_ctr
        idx_ctr +=1
        mStateNull.msgList_connect('browCenterJointHandles',md_jointHandles['browCenter'])
        

        for tag in ['browLeft','browRight']:
            mCrv = self.getMessageAsMeta("{0}JointCurve".format(tag))
            if 'Left' in tag:
                _side = 'left'
            elif 'Right' in tag:
                _side = 'right'
            else:
                _side = 'center'            
            
            if _side in ['left','right']:
                _d['cgmDirection'] = _side
                
            _factor = 100/(self.numJointsBrow-1)
            
            for i in range(self.numJointsBrow):
                log.debug("|{0}| >>  Joint Handle: {1}|{2}...".format(_str_func,tag,i))            
                _d['cgmIterator'] = i
                
                mLoc = cgmMeta.asMeta(self.doCreateAt())
                mLoc.rename("{0}_{1}_jointTrackHelper".format(tag,i))
            
                #self.connectChildNode(mLoc, tag+k.capitalize()+'templateHelper','block')
                mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,
                                                                             turnOnPercentage=True))
            
                mPointOnCurve.parameter = (_factor * i)/100.0
                mPointOnCurve.doConnectOut('position',"{0}.translate".format(mLoc.mNode))
            
                mLoc.p_parent = mNoTransformNull
                
            
                res = DIST.create_closest_point_node(mLoc.mNode,mFullCurve.mNode,True)
                #mLoc = cgmMeta.asMeta(res[0])
                mTrackLoc = cgmMeta.asMeta(res[0])
                mTrackLoc.p_parent = mNoTransformNull
                mTrackLoc.v=False
                
                mHandle = create_jointHelper(mTrackLoc,mBrowLoft,tag,i,_side,nameDict=_d)
                md_jointHandles['brow'][_side].append(mHandle)
                ml_handles.append(mHandle)
                
            
        
        #Aim pass ------------------------------------------------------------------------
        for side in ['left','right']:
            #Handles -------
            ml = md_handles['brow'][side]
            for i,mObj in enumerate(ml):
                mObj.mirrorIndex = idx_side + i
                mObj.mirrorAxis = "translateX,rotateY,rotateZ"
                
                if side == 'left':
                    _aim = [-1,0,0]
                    mObj.mirrorSide = 1                    
                else:
                    _aim = [1,0,0]
                    mObj.mirrorSide = 2
                    
                _up = [0,0,1]
                _worldUp = [0,0,1]
                
                if i == 0:
                    mAimGroup = mObj.aimGroup
                    mc.aimConstraint(md_handles['browCenter'][0].masterGroup.mNode,
                                     mAimGroup.mNode,
                                     maintainOffset = False, weight = 1,
                                     aimVector = _aim,
                                     upVector = _up,
                                     worldUpVector = _worldUp,
                                     worldUpObject = mObj.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )                                
                else:

                    mAimGroup = mObj.aimGroup
                    mc.aimConstraint(ml[i-1].masterGroup.mNode,
                                     mAimGroup.mNode,
                                     maintainOffset = False, weight = 1,
                                     aimVector = _aim,
                                     upVector = _up,
                                     worldUpVector = _worldUp,
                                     worldUpObject = mObj.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )
                    
            mStateNull.msgList_connect('brow{0}PrerigHandles'.format(side.capitalize()), ml)
            
        idx_side = idx_side + i + 1
        log.info(idx_side)
        
        for side in ['left','right']:
            #Joint Helpers ----------------
            ml = md_jointHandles['brow'][side]
            for i,mObj in enumerate(ml):
                if side == 'left':
                    _aim = [1,0,0]
                    mObj.mirrorSide = 1
                else:
                    _aim = [-1,0,0]
                    mObj.mirrorSide = 2
                    
                mObj.mirrorIndex = idx_side + i
                mObj.mirrorAxis = "translateX,rotateY,rotateZ"
                _up = [0,0,1]
                _worldUp = [0,0,1]
                if mObj == ml[-1]:
                    _vAim = [_aim[0]*-1,_aim[1],_aim[2]]
                    mAimGroup = mObj.aimGroup
                    mc.aimConstraint(ml[i-1].masterGroup.mNode,
                                     mAimGroup.mNode,
                                     maintainOffset = False, weight = 1,
                                     aimVector = _vAim,
                                     upVector = _up,
                                     worldUpVector = _worldUp,
                                     worldUpObject = mObj.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )                    
                else:
                    mAimGroup = mObj.aimGroup
                    mc.aimConstraint(ml[i+1].masterGroup.mNode,
                                     mAimGroup.mNode,
                                     maintainOffset = False, weight = 1,
                                     aimVector = _aim,
                                     upVector = _up,
                                     worldUpVector = _worldUp,
                                     worldUpObject = mObj.masterGroup.mNode,
                                     worldUpType = 'objectRotation' )
                    
            mStateNull.msgList_connect('brow{0}JointHandles'.format(side.capitalize()), ml)
        
        #Mirror setup --------------------------------
        """
        for mHandle in ml_handles:
            mHandle._verifyMirrorable()
            _str_handle = mHandle.p_nameBase
            if 'Center' in _str_handle:
                mHandle.mirrorSide = 0
                mHandle.mirrorIndex = idx_ctr
                idx_ctr +=1
            mHandle.mirrorAxis = "translateX,rotateY,rotateZ"
    
        #Self mirror wiring -------------------------------------------------------
        for k,m in _d_pairs.iteritems():
            md_handles[k].mirrorSide = 1
            md_handles[m].mirrorSide = 2
            md_handles[k].mirrorIndex = idx_side
            md_handles[m].mirrorIndex = idx_side
            md_handles[k].doStore('mirrorHandle',md_handles[m])
            md_handles[m].doStore('mirrorHandle',md_handles[k])
            idx_side +=1        """
        
        #Close out ======================================================================================
        self.msgList_connect('prerigHandles', ml_handles)
        
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
    
    mRoot = self.UTILS.skeleton_getAttachJoint(self)
    
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

    
    if self.browType == 0:#Full brow
        log.debug("|{0}| >>  Full Brow...".format(_str_func))
        
        #ml_left = mPrerigNull.msgList_get('browLeftJointHandles')
        #ml_right = mPrerigNull.msgList_get('browRightJointHandles')
        #ml_center = mPrerigNull.msgList_get('browCenterJointHandles')
        
        for tag in 'left','right','center':
            ml_base = mPrerigNull.msgList_get('brow{0}JointHandles'.format(tag.capitalize()))
            ml_new = []
            for mObj in ml_base:
                mJnt = mObj.doCreateAt('joint')
                mJnt.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                mJnt.doStore('cgmType','skinJoint')
                mJnt.doName()
                ml_new.append(mJnt)
                ml_joints.append(mJnt)
                JOINT.freezeOrientation(mJnt.mNode)
                
                mJnt.p_parent = mRoot
                
            mPrerigNull.msgList_connect('brow{0}Joints'.format(tag.capitalize()), ml_new)
            
                
    #>> ===========================================================================
    mRigNull.msgList_connect('moduleJoints', ml_joints)
    self.msgList_connect('moduleJoints', ml_joints)
    #self.atBlockUtils('skeleton_connectToParent')

    for mJnt in ml_joints:
        mJnt.displayLocalAxis = 1
        mJnt.radius = _radius
    for mJnt in ml_joints:mJnt.rotateOrder = 5
        
    return ml_joints    
    
    #...orient ----------------------------------------------------------------------------
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

d_preferredAngles = {}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
@cgmGEN.Timer
def rig_prechecks(self):
    _str_func = 'rig_prechecks'
    log.debug(cgmGEN.logString_start(_str_func))
    
    mBlock = self.mBlock
    
    str_browSetup = mBlock.getEnumValueString('browSetup')
    if str_browSetup not in ['ribbon']:
        self.l_precheckErrors.append("Brow setup not completed: {0}".format(str_browSetup))
    
    str_browType = mBlock.getEnumValueString('browType')
    if str_browType not in ['full']:
        self.l_precheckErrors.append("Brow setup not completed: {0}".format(str_browType))
                
    if mBlock.scaleSetup:
        self.l_precheckErrors.append("Scale setup not complete")

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
    self.mPrerigNull = mPrerigNull
    ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
    mMasterNull = self.d_module['mMasterNull']
    
    mEyeTemplateHandle = mBlock.bbHelper
    
    self.mRootTemplateHandle = mEyeTemplateHandle
    ml_templateHandles = [mEyeTemplateHandle]
    
    self.b_scaleSetup = mBlock.scaleSetup
    
    self.str_browSetup = False
    if mBlock.browSetup:
        self.str_browSetup  = mBlock.getEnumValueString('browSetup')
        
    #Logic checks ========================================================================

    
    #Offset ============================================================================ 
    self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
    """
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
        self.v_offset = MATH.average(l_sizes)"""
    log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))    
    log.debug(cgmGEN._str_subLine)
    
    #Size =======================================================================================
    self.v_baseSize = [mBlock.blockScale * v for v in mBlock.baseSize]
    self.f_sizeAvg = MATH.average(self.v_baseSize)
    log.debug("|{0}| >> size | self.v_baseSize: {1} | self.f_sizeAvg: {2}".format(_str_func,
                                                                                  self.v_baseSize,
                                                                                  self.f_sizeAvg ))
    
    #Settings =============================================================================
    mModuleParent =  self.d_module['mModuleParent']
    if mModuleParent:
        mSettings = mModuleParent.rigNull.settings
    else:
        log.debug("|{0}| >>  using puppet...".format(_str_func))
        mSettings = self.d_module['mMasterControl'].controlVis

    log.debug("|{0}| >> mSettings | self.mSettings: {1}".format(_str_func,mSettings))
    self.mSettings = mSettings
    
    log.debug("|{0}| >> self.mPlug_visSub_moduleParent: {1}".format(_str_func,
                                                                    self.mPlug_visSub_moduleParent))
    log.debug("|{0}| >> self.mPlug_visDirect_moduleParent: {1}".format(_str_func,
                                                                       self.mPlug_visDirect_moduleParent))
    
    #DynParents =============================================================================
    #self.UTILS.get_dynParentTargetsDat(self)
    #log.debug(cgmGEN._str_subLine)
    
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
    
    
    BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'],
                                     self.d_module['mirrorDirection'])
                                     #d_rotateOrders, d_preferredAngles)
    
    
    #Rig Joints =================================================================================
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                           ml_joints,
                                                           'rig',
                                                           self.mRigNull,
                                                           'rigJoints',
                                                           'rig',
                                                           cgmType = False,
                                                           blockNames=False)
    
    ml_segmentJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_joints, None,
                                                               mRigNull,'segmentJoints','seg',
                                                               cgmType = 'segJnt')    
    ml_jointsToHide.extend(ml_segmentJoints)        
    
    #Brow joints ================================================================================
    log.debug("|{0}| >> Brow Joints...".format(_str_func)+ '-'*40)
    
    #Need to sort our joint lists:
    md_skinJoints = {'brow':{}}
    md_rigJoints = {'brow':{}}
    md_segJoints = {'brow':{}}
    
    for k in ['center','left','right']:
        log.debug("|{0}| >> {1}...".format(_str_func,k))        
        ml_skin = self.mPrerigNull.msgList_get('brow{0}Joints'.format(k.capitalize()))
        md_skinJoints['brow'][k] = ml_skin
        ml_rig = []
        ml_seg = []
        
        for mJnt in ml_skin:
            mRigJoint = mJnt.getMessageAsMeta('rigJoint')
            ml_rig.append(mRigJoint)
            
            mSegJoint = mJnt.getMessageAsMeta('segJoint')
            ml_seg.append(mSegJoint)
            mSegJoint.p_parent = False
            
            mRigJoint.p_parent = mSegJoint
            
        md_rigJoints['brow'][k] = ml_rig
        md_segJoints['brow'][k] = ml_seg
        
    """
    for i,mJnt in enumerate(ml_rigJoints):
        mJnt.parent = ml_segmentJoints[i]
        mJnt.connectChildNode(ml_segmentJoints[i],'driverJoint','sourceJoint')#Connect
    ml_jointsToHide.extend(ml_segmentJoints)        
        """
    log.debug(cgmGEN._str_subLine)
    
    #Brow joints ================================================================================
    log.debug("|{0}| >> Brow Handles...".format(_str_func)+ '-'*40)    
    mBrowCurve = mBlock.getMessageAsMeta('browLineloftCurve')
    _BrowCurve = mBrowCurve.getShapes()[0]
    md_handles = {'brow':{}}
    md_handleShapes = {'brow':{}}
    
    for k in ['center','left','right']:
        log.debug("|{0}| >> {1}...".format(_str_func,k))        
        ml_helpers = self.mPrerigNull.msgList_get('brow{0}PrerigHandles'.format(k.capitalize()))    
        ml_new = []
        for mHandle in ml_helpers:
            mJnt = mHandle.doCreateAt('joint')
            mJnt.doCopyNameTagsFromObject(mHandle.mNode,ignore = ['cgmType'])
            #mJnt.doStore('cgmType','dag')
            mJnt.doName()
            ml_new.append(mJnt)
            ml_joints.append(mJnt)
            JOINT.freezeOrientation(mJnt.mNode)
            mJnt.p_parent = False
            mJnt.p_position = mHandle.masterGroup.p_position
            #DIST.get_closest_point(mHandle.mNode,_BrowCurve,True)[0]

        md_handles['brow'][k] = ml_new
        md_handleShapes['brow'][k] = ml_helpers
        
        ml_jointsToHide.extend(ml_new)
    log.debug(cgmGEN._str_subLine)
    
    self.md_rigJoints = md_rigJoints
    self.md_skinJoints = md_skinJoints
    self.md_segJoints = md_segJoints
    self.md_handles = md_handles
    self.md_handleShapes = md_handleShapes
    
    #...joint hide -----------------------------------------------------------------------------------
    for mJnt in ml_jointsToHide:
        try:mJnt.drawStyle =2
        except:mJnt.radius = .00001
            
    #...connect... 
    self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
    return

@cgmGEN.Timer
def rig_shapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
    
        mBlock = self.mBlock
        #_baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'nameList')    
        mHandleFactory = mBlock.asHandleFactory()
        mRigNull = self.mRigNull
        mPrerigNull = self.mPrerigNull
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        
        #Brow center ================================================================================
        mBrowCenter = self.md_handles['brow']['center'][0].doCreateAt()
        mBrowCenterShape = self.md_handleShapes['brow']['center'][0].doDuplicate(po=False)
        mBrowCenterShape.scale = [1.5,1.5,1.5]
        
        mBrowCenter.doStore('cgmName','browMain')
        mBrowCenter.doName()
        
        CORERIG.shapeParent_in_place(mBrowCenter.mNode,
                                     mBrowCenterShape.mNode,False)
        
        mRigNull.connectChildNode(mBrowCenter,'browMain','rigNull')#Connect
        
        
        #Handles ================================================================================
        log.debug("|{0}| >> Handles...".format(_str_func)+ '-'*80)
        for k,d in self.md_handles.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            for side,ml in d.iteritems():
                log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                for i,mHandle in enumerate(ml):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    CORERIG.shapeParent_in_place(mHandle.mNode,
                                                 self.md_handleShapes[k][side][i].mNode)
                    
                    if side == 'center':
                        mHandleFactory.color(mHandle.mNode,side='center',controlType='sub')
                        
                    
        #Direct ================================================================================
        log.debug("|{0}| >> Direct...".format(_str_func)+ '-'*80)
        for k,d in self.md_rigJoints.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            for side,ml in d.iteritems():
                log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                for i,mHandle in enumerate(ml):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    crv = CURVES.create_fromName(name='cube',
                                                 direction = 'z+',
                                                 size = mHandle.radius*2)
                    SNAP.go(crv,mHandle.mNode)
                    mHandleFactory.color(crv,side=side,controlType='sub')
                    CORERIG.shapeParent_in_place(mHandle.mNode,
                                                 crv,keepSource=False)
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
        ml_controlsAll = []#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
        ml_segmentHandles = []
        
        #mPlug_visSub = self.atBuilderUtils('build_visSub')
        mPlug_visDirect = self.mPlug_visDirect_moduleParent
        mPlug_visSub = self.mPlug_visSub_moduleParent
        
        """
        cgmMeta.cgmAttr(self.mSettings,'visDirect_{0}'.format(self.d_module['partName']),
                                          value = True,
                                          attrType='bool',
                                          defaultValue = False,
                                          keyable = False,hidden = False)"""        
        
        
        
        
        mBrowMain = mRigNull.browMain
        _d = MODULECONTROL.register(mBrowMain,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = False)
        ml_controlsAll.append(_d['mObj'])
        ml_segmentHandles.append(_d['mObj'])
        
        #Handles ================================================================================
        log.debug("|{0}| >> Handles...".format(_str_func)+ '-'*80)
        for k,d in self.md_handles.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            for side,ml in d.iteritems():
                log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                for i,mHandle in enumerate(ml):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    _d = MODULECONTROL.register(mHandle,
                                                mirrorSide= side,
                                                mirrorAxis="translateX,rotateY,rotateZ",
                                                makeAimable = False)
                    
                    ml_controlsAll.append(_d['mObj'])
                    ml_segmentHandles.append(_d['mObj'])
                    
        #Direct ================================================================================
        log.debug("|{0}| >> Direct...".format(_str_func)+ '-'*80)
        for k,d in self.md_rigJoints.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
            for side,ml in d.iteritems():
                log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
                for i,mHandle in enumerate(ml):
                    log.debug("|{0}| >> {1}...".format(_str_func,mHandle))
                    _d = MODULECONTROL.register(mHandle,
                                                typeModifier='direct',
                                                mirrorSide= side,
                                                mirrorAxis="translateX,rotateY,rotateZ",
                                                makeAimable = False)
                    
                    mObj = _d['mObj']
                    
                    ml_controlsAll.append(_d['mObj'])
                    
                    ATTR.set_hidden(mObj.mNode,'radius',True)        
                    if mObj.hasAttr('cgmIterator'):
                        ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                
                    for mShape in mObj.getShapes(asMeta=True):
                        ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))                    

       
        

            
        #Close out...
        mHandleFactory = mBlock.asHandleFactory()
        for mCtrl in ml_controlsAll:
            ATTR.set(mCtrl.mNode,'rotateOrder',self.ro_base)
            
            if mCtrl.hasAttr('radius'):
                ATTR.set(mCtrl.mNode,'radius',0)        
            
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
        mRigNull.msgList_connect('handleJoints',ml_segmentHandles,'rigNull')        
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
    
    
    mBrowMain = mRigNull.browMain
    mBrowMain.masterGroup.p_parent = self.mDeformNull
    
    #Parenting ============================================================================
    log.debug("|{0}| >>Parenting...".format(_str_func)+ '-'*80)
    
    for k,d in self.md_handles.iteritems():
        log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
        for side,ml in d.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
            for i,mHandle in enumerate(ml):
                mHandle.masterGroup.p_parent = self.mDeformNull
                
    for k,d in self.md_segJoints.iteritems():
        log.debug("|{0}| >> {1}...".format(_str_func,k)+ '-'*40)
        for side,ml in d.iteritems():
            log.debug("|{0}| >> {1}...".format(_str_func,side)+ '-'*10)
            for i,mHandle in enumerate(ml):
                mHandle.p_parent = self.mDeformNull
        
    
    #Brow Ribbon ============================================================================
    log.debug("|{0}| >> Brow ribbon...".format(_str_func)+ '-'*80)
    
    md_seg = self.md_segJoints
    md_brow = md_seg['brow']
    ml_right = copy.copy(md_brow['right'])
    ml_center = md_brow['center']
    ml_left = md_brow['left']
    ml_right.reverse()
    
    ml_ribbonJoints = ml_right + ml_center + ml_left
    
    md_handles = self.md_handles
    md_brow = md_handles['brow']
    ml_rightHandles = copy.copy(md_brow['right'])
    ml_centerHandles = md_brow['center']
    ml_leftHandles = md_brow['left']
    ml_rightHandles.reverse()    
    
    
    ml_skinDrivers = ml_rightHandles + ml_centerHandles + ml_leftHandles
    
    d_ik = {'jointList':[mObj.mNode for mObj in ml_ribbonJoints],
            'baseName' : self.d_module['partName'] + '_ikRibbon',
            'orientation':'xyz',
            'loftAxis' : 'z',
            'tightenWeights':False,
            'driverSetup':'stableBlend',
            'squashStretch':None,
            'connectBy':'constraint',
            'squashStretchMain':'arcLength',
            'paramaterization':'fixed',#mBlock.getEnumValueString('ribbonParam'),
            #masterScalePlug:mPlug_masterScale,
            #'settingsControl': mSettings.mNode,
            'extraSquashControl':True,
            'influences':ml_skinDrivers,
            'moduleInstance' : self.mModule}    
    
    
    res_ribbon = IK.ribbon(**d_ik)
    
    #Setup some constraints============================================================================
    md_brow['center'][0].masterGroup.p_parent = mBrowMain
    
    mc.pointConstraint([md_brow['left'][0].mNode, md_brow['right'][0].mNode],
                       md_brow['center'][0].masterGroup.mNode,
                       maintainOffset=True)
    
    
    for side in ['left','right']:
        ml = md_brow[side]
        ml[0].masterGroup.p_parent = mBrowMain
        mc.pointConstraint([ml[0].mNode, ml[-1].mNode],
                           ml[1].masterGroup.mNode,
                           maintainOffset=True)
        
        
        
    pprint.pprint(vars())

    return


@cgmGEN.Timer
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
    

    #Settings =================================================================================
    #log.debug("|{0}| >> Settings...".format(_str_func))
    #mSettings.visDirect = 0
    
    #mPlug_FKIK = cgmMeta.cgmAttr(mSettings,'FKIK')
    #mPlug_FKIK.p_defaultValue = 1
    #mPlug_FKIK.value = 1
        
    #Lock and hide =================================================================================
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
    m#Settings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    mPrerigNull = mBlock.prerigNull
    #directProxy = mBlock.proxyDirect
    
    _side = BLOCKUTILS.get_side(self.mBlock)
    
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
        
    ml_proxy = []
    ml_curves = []
    #Brow -------------
    mUprCurve = mBlock.getMessageAsMeta('browUprloftCurve')
    mUprUse = mUprCurve.doDuplicate(po=False)
    mUprUse.p_parent = mRigNull.constrainNull
    mUprCurve.v=False
    ml_curves.append(mUprUse)
    md_rigJoints = {'brow':{}}
    for k in ['center','left','right']:
        log.debug("|{0}| >> {1}...".format(_str_func,k))        
        ml_skin = mPrerigNull.msgList_get('brow{0}Joints'.format(k.capitalize()))
        ml_rig = []
        for mJnt in ml_skin:
            mRigJoint = mJnt.getMessageAsMeta('rigJoint')
            ml_rig.append(mRigJoint)        
        md_rigJoints['brow'][k] = ml_rig
        
    ml_right = copy.copy(md_rigJoints['brow']['right'])
    ml_right.reverse()
    ml_followJoints = ml_right + md_rigJoints['brow']['center'] + md_rigJoints['brow']['left']

    
    _crv = mc.curve(d=1,p=[mObj.p_position for mObj in ml_followJoints])
    mCrv = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
    mCrv.p_parent = mRigNull
    mCrv.rename('{0}_proxyBrowCurve'.format(self.d_module['partName']))            
    mCrv.v=False
    ml_curves.append(mCrv)

    l_clusters = []
    for i,cv in enumerate(mCrv.getComponents('cv')):
        _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(self.d_module['partName'],i))
        TRANS.parent_set( _res[1],ml_followJoints[i].mNode)
        l_clusters.append(_res)
        ATTR.set(_res[1],'visibility',False)

    #pprint.pprint(l_clusters)
    mc.rebuildCurve(mCrv.mNode, d=3, keepControlPoints=False,ch=1,s=8,
                    n="{0}_reparamRebuild".format(self.d_module['partName']))    

    #Loft ------------------------------------------------
    _res_body = mc.loft([mCrv.mNode,mUprUse.mNode], 
                        o = True, d = 1, po = 3, c = False,ch=True,autoReverse=False)
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

    mLoftSurface.doStore('cgmName',"{0}_{1}brow".format(self.d_module['partName'],k),attrType='string')
    mLoftSurface.doStore('cgmType','proxy')
    mLoftSurface.doName()
    log.info("|{0}| loft node: {1}".format(_str_func,_loftNode))             



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
        
        

    
    mRigNull.msgList_connect('proxyMesh', ml_proxy + ml_curves)




















