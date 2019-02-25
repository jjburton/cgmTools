"""
------------------------------------------
cgm.core.mrs.blocks.simple.handle
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import time
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
import Red9.core.Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.cgm_General as cgmGEN

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.math_utils as MATH

import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.transform_utils as TRANS
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.list_utils as LISTS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.lib.locator_utils as LOC
import cgm.core.lib.string_utils as STR
#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.02.202019'
__autoTemplate__ = False
__component__ = False
__menuVisible__ = True
__baseSize__ = 10,10,10
__l_rigBuildOrder__ = []
__blockFrame__ = True

#>>>Profiles ===================================================================================================
d_build_profiles = {'unityLow':{'default':{}},
                    'unityMed':{'default':{}},
                    'unityHigh':{'default':{}},
                    'feature':{'default':{}}}
d_block_profiles = {}

#>>>Attrs ========================================================================================================
l_attrsStandard = [
'side',
'position',
'attachPoint',
#'baseDat',
'blockProfile',
'moduleTarget']

d_attrsToMake = {
'definePose':'wide:relax',
'numFinger':'int',
'numThumbInner':'int',
'numThumbOuter':'int'}

d_defaultSettings = {
'version':__version__,
'definePose':'wide',
'numFinger':4,
'numThumbOuter':0,
'numThumbInner':1}
#'baseDat':{'lever':[0,0,-1],'aim':[0,0,1],'up':[0,1,0],'end':[0,0,1]},}

d_wiring_prerig = {}
d_wiring_template = {}
d_wiring_define = {'msgLinks':['noTransDefineNull'],
                     }
#=============================================================================================================
#>> Define
#=============================================================================================================
def mirror_self(self,primeAxis = 'Left'):
    _str_func = 'mirror_self'
    _idx_state = self.getState(False)
    
    log.debug("|{0}| >> define...".format(_str_func)+ '-'*80)
    ml_mirrorHandles = self.msgList_get('defineSubHandles')
    r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                             mode = '',primeAxis = primeAxis.capitalize() )    
    """
    if _idx_state > 0:
        log.debug("|{0}| >> template...".format(_str_func)+ '-'*80)
        ml_mirrorHandles = self.msgList_get('templateHandles')
        r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                                     mode = '',primeAxis = primeAxis.capitalize() )
    
    if _idx_state > 1:
        log.debug("|{0}| >> prerig...".format(_str_func)+ '-'*80)        
        ml_mirrorHandles = self.msgList_get('prerigHandles') + self.msgList_get('jointHandles')
        r9Anim.MirrorHierarchy().makeSymmetrical([mObj.mNode for mObj in ml_mirrorHandles],
                                                 mode = '',primeAxis = primeAxis.capitalize() )
        """

def templateDelete(self):pass

def define(self):
    try:
        _str_func = 'define'
        _short = self.mNode
        log.debug(cgmGEN.logString_start(_str_func))
        
        #Attributes =========================================================
        log.debug(cgmGEN.logString_sub(_str_func,'attributes'))
        self.addAttr('isMegaBlock',True,lock=True,hidden=True)
        #self.doStore('isMegaBlock',True)
        ATTR.set_alias(_short,'sy','blockScale')    
        self.setAttrFlags(attrs=['sx','sz','sz'])
        self.doConnectOut('sy',['sx','sz'])
        _str_pose = self.getEnumValueString('definePose')
        
        
        #ATTR.set_min(_short, 'loftSplit', 1)
        #ATTR.set_min(_short, 'paramUprStart', 0.0)
        #ATTR.set_min(_short, 'paramLwrStart', 0.0)
        
        
        #Buffer our values...
        #_str_faceType = self.getEnumValueString('faceType')
        #_str_muzzleSetup = self.getEnumValueString('muzzleSetup')
        #_str_noseSetup = self.getEnumValueString('noseSetup')
        #_str_uprJawSetup = self.getEnumValueString('uprJawSetup')    
        #_str_lipsSetup = self.getEnumValueString('lipsSetup')
        #_str_teethSetup = self.getEnumValueString('teethSetup')
        #_str_cheekSetup = self.getEnumValueString('cheekSetup')
        #_str_tongueSetup = self.getEnumValueString('tongueSetup')
        
    
        #Cleaning =========================================================        
        _shapes = self.getShapes()
        if _shapes:
            log.debug(cgmGEN.logString_msg(_str_func,'Removing old shapes'))
            mc.delete(_shapes)
            defineNull = self.getMessage('defineNull')
            if defineNull:
                log.debug(cgmGEN.logString_msg(_str_func,'Removing old defineNull'))
                mc.delete(defineNull)
        ml_handles = []

        mNoTransformNull = self.getMessageAsMeta('noTransDefineNull')
        if mNoTransformNull:
            mNoTransformNull.delete()

        
        #rigBlock Handle ===========================================================
        log.debug(cgmGEN.logString_sub(_str_func,'RigBlock Handle'))
        
        _size = MATH.average(self.baseSize[1:])
        _crv = CURVES.create_fromName(name='locatorForm',#'axis3d',#'arrowsAxis', 
                                      direction = 'z+', size = _size/4)
        SNAP.go(_crv,self.mNode,)
        CORERIG.override_color(_crv, 'white')        
        CORERIG.shapeParent_in_place(self.mNode,_crv,False)
        mHandleFactory = self.asHandleFactory()
        self.addAttr('cgmColorLock',True,lock=True, hidden=True)
        mDefineNull = self.atUtils('stateNull_verify','define')
        mNoTransformNull = self.atUtils('noTransformNull_verify','define')
        
        #Bounding sphere ==================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'bbVisualize'))        
        _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
        mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
        mBBShape.p_parent = mDefineNull    
        mBBShape.tz = .5
        #mBBShape.ty = .5
        
        CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
        mHandleFactory.color(mBBShape.mNode,controlType='sub')
        mBBShape.setAttrFlags()
        
        mBBShape.doStore('cgmName', self)
        mBBShape.doStore('cgmType','bbVisualize')
        mBBShape.doName()    
        
        self.connectChildNode(mBBShape.mNode,'bbHelper')
        self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
        
        
        #Make our handles creation data =======================================================
        d_pairs = {}
        d_creation = {}
        l_order = []
        d_curves = {}
        d_curveCreation = {}
        d_toParent = {}
        
        log.debug(cgmGEN.logString_sub(_str_func,'handle data'))        
        
        
        _d_pairs = {'tipInner':'tipOuter',
                    #'thumbTipInner':'thumbTipOuter',
                    'thumbBaseInner':'thumbBaseOuter',
                    'thumbMidInner':'thumbMidOuter',
                    'thumbTipInner':'thumbTipOuter',
                    'midInner':'midOuter',
                    'baseInner':'baseOuter'
                    }
        
        d_pairs.update(_d_pairs)
        
        _d_scaleSpace = {
            'wide':{'tipInner':[.6,0,.8],
                    'tipOuter':[-.6,0,.8],
                    'tipMid':[0,0,1],
                    'baseInner':[.4,0,-.95],
                    'baseOuter':[-.4,0,-.95],
                    'baseMid':[0,0,-.95],
                    'midInner':[.5,0,0],
                    'midOuter':[-.5,0,0],
                    'midMid':[0,.2,0],
                    'thumbTipInner':[1,-.25,0],
                    'thumbBaseInner':[.5,-.1,-.95],
                    'thumbTipOuter':[-1,-.25,0],
                    'thumbBaseOuter':[-.5,-.1,-.95],                    
                    #'rollInner':[.4,0,.5],
                    #'rollOuter':[-.4,0,.5],
                    #'rollMid':[0,.2,.5],
                    },
            }
    
        _d = {#'thumbTipInner':{'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0},
              #'thumbBaseInner':{'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0},
              }
        
        for k in ['tip','base','mid']:
            _d['{0}Inner'.format(k)] = {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Outer'.format(k)] = {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Mid'.format(k)] = {'color':'yellow','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
        
        for k in ['roll']:
            _d['{0}Inner'.format(k)] = {'color':'blueWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Outer'.format(k)] = {'color':'redWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Mid'.format(k)] = {'color':'yellowWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            
            
            
        for k in ['thumbBase','thumbTip']:
            _d['{0}Inner'.format(k)] = {'color':'blueBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Outer'.format(k)] = {'color':'redBright','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            
        for k in ['thumbMid']:
            _d['{0}Inner'.format(k)] = {'color':'blueWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
            _d['{0}Outer'.format(k)] = {'color':'redWhite','tagOnly':1,'arrow':0,'jointLabel':1,'vectorLine':0}
        
        
        
        for k,d in _d.iteritems():
            _v = _d_scaleSpace[_str_pose].get(k)
            if _v is not None:
                d['scaleSpace'] = _v
        
        d_creation.update(_d)
        l_order.extend(_d.keys())
        """
        l_order.extend(['tipInner','tipOuter','tipMid',
                        'baseInner','baseOuter','baseMid',
                        'midInner','midOuter','midMid',
                        'rollInner','rollOuter','rollMid',                        
                        'thumbTipInner','thumbBaseInner',
                        ])"""
        
        _d_curveCreation = {
            'tipLine':{'keys':['tipInner','tipMid','tipOuter'],'rebuild':1},
            'baseLine':{'keys':['baseInner','baseMid','baseOuter'],'rebuild':1},
            'midLine':{'keys':['midInner','midMid','midOuter'],'rebuild':1},
            'rollLine':{'keys':['rollInner','rollMid','rollOuter'],'rebuild':1},
            'outerLine':{'keys':['baseOuter','midOuter','rollOuter','tipOuter'],'rebuild':0},
            'innerLine':{'keys':['baseInner','midInner','rollInner','tipInner'],'rebuild':0},
            'innerThumbLine':{'keys':['thumbBaseInner','thumbMidInner','thumbTipInner'],'rebuild':0},
            'outerThumbLine':{'keys':['thumbBaseOuter','thumbMidOuter','thumbTipOuter'],'rebuild':0},
        }
        
        d_curveCreation.update(_d_curveCreation)
        #pprint.pprint(vars())
        
        
        #make em...============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'Make handles'))        
        
        #self,l_order,d_definitions,baseSize,mParentNull = None, mScaleSpace = None, rotVecControl = False,blockUpVector = [0,1,0]
        md_res = self.UTILS.create_defineHandles(self, l_order, d_creation, _size/2, mDefineNull, mBBShape)
    
        md_handles = md_res['md_handles']
        ml_handles = md_res['ml_handles']
        
        
        for k,p in d_toParent.iteritems():
            md_handles[k].p_parent = md_handles[p]
            
        
        
        #Setup our handle aims/contraints =========================================================== 
        log.debug(cgmGEN.logString_sub(_str_func,'Position rolls'))                
        for t in ['Inner','Outer','Mid']:
            #Initial pos
            k = 'roll'+t
            mHandle = md_handles['roll'+t]
            #log.debug(mHandle)                
            
            mStart = md_handles['mid'+t]
            mEnd = md_handles['tip'+t]
            pos=  DIST.get_average_position([mStart.p_position,
                                             mEnd.p_position])
            mHandle.p_position = pos
            mGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'driver')
            mc.parentConstraint([mStart.mNode,mEnd.mNode],mGroup.mNode,maintainOffset=True)
            mAimGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'aim')
            mc.aimConstraint(mEnd.mNode, mAimGroup.mNode, maintainOffset = False,
                             aimVector = [0,0,1], upVector = [0,1,0], 
                             worldUpObject = self.mNode,
                             worldUpType = 'objectrotation', 
                             worldUpVector = [0,1,1])
            
        log.debug(cgmGEN.logString_sub(_str_func,'thumbMids'))                
        for t in ['Inner','Outer']:
            #Initial pos
            mHandle = md_handles['thumbMid'+t]
            #log.debug(mHandle)                
            
            mStart = md_handles['thumbBase'+t]
            mEnd = md_handles['thumbTip'+t]
            pos=  DIST.get_average_position([mStart.p_position,
                                             mEnd.p_position])
            mHandle.p_position = pos
            mGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'driver')
            mc.parentConstraint([mStart.mNode,mEnd.mNode],mGroup.mNode,maintainOffset=True)
            mAimGroup = mHandle.doGroup(True,True, asMeta=True,typeModifier = 'aim')
            
            if t == 'Inner':
                _aimUp = [1,0,0]
            else:
                _aimUp = [-1,0,0]
            mc.aimConstraint(mEnd.mNode, mAimGroup.mNode, maintainOffset = False,
                             aimVector = [0,0,1], upVector = [0,1,0], 
                             worldUpObject = self.mNode,
                             worldUpType = 'objectrotation', 
                             worldUpVector = _aimUp)
            
        log.debug(cgmGEN.logString_sub(_str_func,'mid mid'))
        mMidMid = md_handles['midMid']
        mGroup = mMidMid.doGroup(True,True, asMeta=True,typeModifier = 'driver')
        mc.parentConstraint([md_handles['midInner'].mNode,
                             md_handles['midOuter'].mNode],mGroup.mNode,maintainOffset=True)
        
        
            
        #Curves =================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'curves'))        
        md_resCurves = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mNoTransformNull)
        md_curves = md_resCurves['md_curves']
        
        ATTR.set(md_curves['innerLine'].mNode,'v',False)
        ATTR.set(md_curves['outerLine'].mNode,'v',False)
        
        for k in ['tipLine','rollLine','baseLine','midLine']:
            md_curves[k].template = True
        
        #...vis ===================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'inner thumb vis setup'))                
        for k in 'thumbBaseInner','thumbMidInner','thumbTipInner':
            ATTR.connect("{0}.numThumbInner".format(_short), "{0}.visibility".format(md_handles[k].mNode))
            ATTR.set_standardFlags(md_handles[k].mNode,['v'])
        ATTR.connect("{0}.numThumbInner".format(_short),
                     "{0}.visibility".format(md_curves['innerThumbLine'].mNode))
        ATTR.set_standardFlags(md_curves['innerThumbLine'].mNode,['v'])
        
        log.debug(cgmGEN.logString_sub(_str_func,'outer thumb vis setup'))                
        for k in 'thumbBaseOuter','thumbMidOuter','thumbTipOuter':
            ATTR.connect("{0}.numThumbOuter".format(_short), "{0}.visibility".format(md_handles[k].mNode))
            ATTR.set_standardFlags(md_handles[k].mNode,['v'])
        ATTR.connect("{0}.numThumbOuter".format(_short),
                     "{0}.visibility".format(md_curves['outerThumbLine'].mNode))
        ATTR.set_standardFlags(md_curves['outerThumbLine'].mNode,['v'])        

        #mirror============================================================
        log.debug(cgmGEN.logString_sub(_str_func,'Mirror'))        
        
        idx_ctr = 0
        idx_side = 0
        d = {}
        
        for tag,mHandle in md_handles.iteritems():
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
            md_handles[k].mirrorSide = 1
            md_handles[m].mirrorSide = 2
            md_handles[k].mirrorIndex = idx_side
            md_handles[m].mirrorIndex = idx_side
            md_handles[k].doStore('mirrorHandle',md_handles[m])
            md_handles[m].doStore('mirrorHandle',md_handles[k])
            idx_side +=1
    
        #Curves -------------------------------------------------------------------------
        self.msgList_connect('defineHandles',ml_handles)#Connect    
        self.msgList_connect('defineSubHandles',ml_handles)#Connect
        self.msgList_connect('defineCurves',md_resCurves['ml_curves'])#Connect
        
        
        #Verify our drivers
        verify_drivers(self)
        
        
        return        
        
 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        




def uiBuilderMenu(self,parent = None):
    #uiMenu = mc.menuItem( parent = parent, l='Head:', subMenu=True)
    _short = self.p_nameShort
    
    mc.menuItem(en=False,
                label = "Hand")
    
    mc.menuItem(ann = '[{0}] Build Drivers for our subs to attach to'.format(_short),
                c = cgmGEN.Callback(verify_drivers,self),
                label = "Verify Drivers")
    
    mc.menuItem(en=False,
                label = "----Sub")    
    mc.menuItem(ann = '[{0}] Verify sub blocks'.format(_short),
                c = cgmGEN.Callback(verify_subBlocks,self),
                label = "Verify")
    
    mc.menuItem(ann = '[{0}] Snap sub blocks'.format(_short),
                c = cgmGEN.Callback(sub_connect,self,'snap'),
                label = "Snap")
    mc.menuItem(ann = '[{0}] Attach sub blocks'.format(_short),
                c = cgmGEN.Callback(sub_connect,self,'attach'),
                label = "Attach")
    mc.menuItem(ann = '[{0}] Detach sub blocks'.format(_short),
                c = cgmGEN.Callback(sub_connect,self,'attach'),
                label = "Detach")    
    
    return
    mc.menuItem(ann = '[{0}] Report Head geo group'.format(_short),
                c = cgmGEN.Callback(headGeo_getGroup,self),
                label = "Report Group")
    mc.menuItem(ann = '[{0}] Add selected to head geo proxy group'.format(_short),
                c = cgmGEN.Callback(headGeo_add,self),
                label = "Add selected")
    mc.menuItem(ann = '[{0}] REPLACE existing geo with selected'.format(_short),
                c = cgmGEN.Callback(headGeo_replace,self),
                label = "Replace with selected")
    mc.menuItem(ann = '[{0}]Remove selected to head geo proxy group'.format(_short),
                c = cgmGEN.Callback(headGeo_remove,self),
                label = "Remove selected")        
    mc.menuItem(ann = '[{0}] Select Geo Group'.format(_short),
                c = cgmGEN.Callback(headGeo_getGroup,self,True),
                label = "Select Group")
    
    
    mc.menuItem(ann = '[{0}] Head Geo Lock'.format(_short),
                c = cgmGEN.Callback(headGeo_lock,self,None),
                label = "Toggle Lock")

_l_finger = ['index','middle','ring','pinky']

def get_nameOptions(self,mode = 'finger',count = None):
    _str_func = 'verify_subBlocks'
    _short = self.mNode
    log.debug(cgmGEN.logString_start(_str_func))
    
    if mode == 'finger':
        if count is None:
            int_fingers = self.numFinger
        else:
            int_fingers = count
            
        if int_fingers:
            if int_fingers < len(_l_finger):
                if int_fingers in [1,4]:
                    return _l_finger[:int_fingers]
                elif int_fingers == 2:
                    return [_l_finger[0],_l_finger[-1]]
                else:
                    return [_l_finger[0],_l_finger[1],_l_finger[-1]]
                    
            else:
                _l_use = copy.copy(_l_finger)
                for i in range(int_fingers-len(_l_finger)):
                    _l_use.append('finger_{0}'.format(i+1))
                return _l_use
            return _l_finger
    else:
        if count is None:
            int_count = self.numbThumbInner
        else:
            int_count = count
                   
        if int_count > 1:
            return ["{0}_{1}".format(mode,i) for i in range(int_count)]
        return ['thumb']
    
def verify_drivers(self,forceNew=True):
    try:
        _str_func = 'verify_drivers'
        _short = self.mNode
        log.debug(cgmGEN.logString_start(_str_func))
        
        md_curves = {}
        md_uValues = {}
        md_baseDrivers = {}
        md_driverLists = {}
        md_baseDriverLists ={}
        reload(CURVES)
        
        mNoTransformNull = self.getMessageAsMeta('noTransDefineNull')
        
        #Thumbs ---------------------------------------------------------------------
        log.debug(cgmGEN.logString_sub(_str_func,'thumb'))
        for a in 'thumbInner','thumbOuter':
            sAttr = 'num'+STR.capFirst(a)
            v = self.getMayaAttr(sAttr)
            if v:
                
                if v>1:
                    log.error("Only one thumb supported per side currently.")
                    ATTR.set(_short,sAttr,1)
                    
                ml_check= self.msgList_get('finger{0}Curves')
                _build = True
                if ml_check:
                    if forceNew or len(ml_check) != int_fingers:
                        log.warning(cgmGEN.logString_msg(_str_func,'Not enough data points. Rebuilding: {0}'.format(a)))
                        _build = True
                    else:
                        log.debug(cgmGEN.logString_msg(_str_func,'good dat'))                    
                        _build = False
                        
                if _build:
                    log.debug(cgmGEN.logString_msg(_str_func,'building: {0}'.format(a)))
                    
                
        
        
        
        
        #Fingers ------------------------------------------------------------------------------
        int_fingers = self.numFinger
        
        if int_fingers:
            log.debug(cgmGEN.logString_sub(_str_func,'fingers'))
            
            ml_check= self.msgList_get('finger{0}Curves')
            _build = True
            if ml_check:
                if forceNew or len(ml_check) != int_fingers:
                    log.warning(cgmGEN.logString_msg(_str_func,'Not enough data points. Rebuilding'))
                    _build = True
                else:
                    log.debug(cgmGEN.logString_msg(_str_func,'good dat'))                    
                    _build = False
            
            if _build:
                l_fingerTags = ['base','mid','roll','tip']
                md_handles = {}
                md_baseTags = {}
                md_driverTags = {}
                
                log.debug(cgmGEN.logString_msg(_str_func,'finger Group...'))        
                mFingerGroup = self.getMessageAsMeta('fingerNoTrans')
                if mFingerGroup:
                    mc.delete(mFingerGroup.getChildren())
                else:
                    mFingerGroup =mNoTransformNull.doCreateAt(setClass=True)
                    mFingerGroup.rename('fingerStuff')
                    mFingerGroup.p_parent = mNoTransformNull
                    self.connectChildNode(mFingerGroup, 'fingerNoTrans','block')
                
                log.debug(cgmGEN.logString_msg(_str_func,'Gather dat...'))
                for k in l_fingerTags:
                    mCurve = self.getMessageAsMeta("{0}LineDefineCurve".format(k))
                    if not mCurve:
                        log.debug(cgmGEN.logString_msg(_str_func,'Missing Curve: {0}'.format(k)))
                    else:
                        md_curves[k] = mCurve
                        
                log.debug(cgmGEN.logString_msg(_str_func,'uValues'))
                if int_fingers == 1:
                    ml_uValues = [.5]
                elif int_fingers == 2:
                    ml_uValues = [0.0,1.0]
                elif int_fingers == 3:
                    ml_uValues = [0.0,.5, 1.0]
                else:
                    ml_uValues = CURVES.getUSplitList(md_curves['base'].mNode,int_fingers,False,returnU=True)
                    ml_uValues = MATH.normalizeList(ml_uValues)
                pprint.pprint(ml_uValues)
                
                log.debug(cgmGEN.logString_msg(_str_func,'param attributes'))
                ATTR.datList_connect(self.mNode,'pFingerStart',ml_uValues)
                l_paramStart = ATTR.datList_getAttrs(self.mNode, 'pFingerStart')
                ATTR.datList_connect(self.mNode,'pFingerEnd',ml_uValues)
                l_paramEnd = ATTR.datList_getAttrs(self.mNode, 'pFingerEnd')
                
                for a in l_paramStart + l_paramEnd:
                    ATTR.set_lock(_short,a,False)
                    ATTR.set_min(_short,a,0.0)
                    ATTR.set_max(_short,a,1.0)
                    
                    
                    
                
                log.debug(cgmGEN.logString_msg(_str_func,'base drivers...'))
                md_rollFix = {}
                
                for k in l_fingerTags:
                    md_baseDrivers[k] = {}
                    ml = []
                    ml_tags = []
                    
                    for i,v in enumerate(ml_uValues):
                        if not md_baseTags.get(i):md_baseTags[i] = []
                        if not md_rollFix.get(i):md_rollFix[i] = {}
                        
                        log.debug(cgmGEN.logString_msg(_str_func,'Driver {0} | {1}...'.format(k,i)))        
                        tag = "base_{0}_{1}".format(k,i)
                        mLoc = cgmMeta.asMeta(self.doCreateAt(setClass=True))
                        #mLoc = self.doLoc(fastMode=True)#cgmMeta.asMeta(self.doCreateAt('locator'))
                        mLoc.doStore('baseTag',tag)
                        mCrv = md_curves[k]
                        
                        self.connectChildNode(mLoc, '{0}_{1}_fingerBaseDriver'.format(k,i),'block')
                        mLoc.rename("{0}_{1}_baseDriver".format(k,i))
                        mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,
                                                                                     turnOnPercentage=True))
                        
                        if k == 'tip':
                            log.debug(cgmGEN.logString_msg(_str_func,'end! {0} | {1}...'.format(k,i)))        
                            mPointOnCurve.doConnectIn('parameter',"{0}.{1}".format(self.mNode,l_paramEnd[i]))
                        elif k == 'roll':
                            """
                            md_rollFix[i]['mPoci'] = mPointOnCurve
                            md_rollFix[i]['mCrv'] = mCrv"""
                            NODEFACTORY.argsToNodes("{0} = {1} >< {2}".format(
                                "{0}.parameter".format(mPointOnCurve.mNode),
                                "{0}.{1}".format(_short,l_paramStart[i]),
                                "{0}.{1}".format(_short,l_paramEnd[i]),
                                )).doBuild()
                            
                        else:
                            mPointOnCurve.doConnectIn('parameter',"{0}.{1}".format(self.mNode,l_paramStart[i]))
                            
                        mPointOnCurve.doConnectOut('position',"{0}.translate".format(mLoc.mNode))
                        mPointOnCurve.rename('{0}_{1}_fingerBaseDriver_poci'.format(k,i))
                        mLoc.p_parent = mFingerGroup
                        
                        md_baseDrivers[k][i] = mLoc
                        ml.append(mLoc)
                        md_handles[tag] = mLoc
                        if k!= 'base':
                            ml_tags.append(tag)
                            md_baseTags[i].append(tag)
                        
                    self.msgList_connect('finger{0}BaseDrivers'.format(k.capitalize()), ml)
                    md_baseDriverLists[k] = ml
                    
                #Do our roll fixes =================================================================
                """
                for i,v in enumerate(ml_uValues):
                    mLoc = cgmMeta.asMeta(self.doCreateAt(setClass=True))
                    mLoc.rename("{0}_{1}_rollParamDriver".format(k,i))
                    mLoc.p_parent = mFingerGroup
                    mc.pointConstraint([md_baseDrivers['mid'][i].mNode,
                                        md_baseDrivers['tip'][i].mNode],mLoc.mNode,maintainOffset = False)
                    
                    _node = mc.createNode ('nearestPointOnCurve')
                    _node = mc.rename('roll{0}_{1}_npoc'.format(k,i))
                    mc.connectAttr ((mLoc.mNode+'.translate'),(_node+'.inPosition'))
                    mc.connectAttr ((md_rollFix[i]['mCrv'].getShapes()[0]+'.worldSpace'),(_node+'.inputCurve'))
                
                    md_rollFix[i]['mPoci'].doConnectIn('parameter',"{0}.parameter".format(_node))
                    md_rollFix[i]['mPoci'].turnOnPercentage = 0"""
                    
                #Basecurves
                log.debug(cgmGEN.logString_msg(_str_func,'Base Curves...'))
                d_curveCreation = {}
                for i,l in md_baseTags.iteritems():
                    d_curveCreation["fBase_{0}".format(i)] = {'keys':l,'rebuild':1}
                
                
                #d_curveCreation.update(_d_curveCreation)
                md_resCurves = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mFingerGroup)
                md_curves = md_resCurves['md_curves']
                ml_curves = md_resCurves['ml_curves']
                for mCrv in ml_curves:
                    mCrv.inheritsTransform=0
                    mCrv.v=False
                    #mCrv.p_parent = mFingerGroup
                    
                
                #Final drivers ------------------------------------------------------------
                log.debug(cgmGEN.logString_sub(_str_func,'final drivers'))
                
                log.debug(cgmGEN.logString_msg(_str_func,'splits'))
                l_splits = [.4,.8]
                
                log.debug(cgmGEN.logString_msg(_str_func,'param attributes'))
                ATTR.datList_connect(self.mNode,'paramSplit',l_splits)
                l_paramSplit = ATTR.datList_getAttrs(self.mNode, 'paramSplit')
                for a in l_paramSplit:
                    ATTR.set_lock(_short,a,False)
                    ATTR.set_min(_short,a,0.05)
                    ATTR.set_max(_short,a,.95)
                    
                
                for i in md_baseTags.keys():
                    log.debug(cgmGEN.logString_sub(_str_func,'subSplit {0}'.format(mCrv)))
                    mCrv = md_curves["fBase_{0}".format(i)]
                    if not md_driverTags.get(i):md_driverTags[i] = []
                    ml = []
                    l=[]
                    l_tags = copy.copy(md_baseTags[i])
                    l_tags.pop(1)
                    _end = l_tags.pop(-1)
                    
                    for ii,a in enumerate(l_paramSplit):
                        log.debug(cgmGEN.logString_msg(_str_func,'paramSplit {0}|{1}'.format(i,a)))                        
                        tag = "finger_{0}_{1}".format(i,ii)
                        mLoc = cgmMeta.asMeta(self.doCreateAt(setClass=True))
                        #mLoc = self.doLoc(fastMode=True)#cgmMeta.asMeta(self.doCreateAt('locator'))
                        
                        #self.connectChildNode(mLoc, '{0}_{1}_fingerDriver'.format(i,ii+2),'block')
                        mLoc.rename("finger{0}_{1}_driver".format(i,ii))
                        mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,
                                                                                     turnOnPercentage=True))
                        
                        mPointOnCurve.doConnectIn('parameter',"{0}.{1}".format(self.mNode,a))
                        mPointOnCurve.doConnectOut('position',"{0}.translate".format(mLoc.mNode))
                        mPointOnCurve.rename('fingerDriver_{0}_{1}_poci'.format(i,ii+2))
                        mLoc.p_parent = mFingerGroup
                        
                        #md[k][i] = mLoc
                        ml.append(mLoc)
                        md_handles[tag] = mLoc
                        l_tags.append(tag)
                    
                    l_tags.append(_end)
                    l_tags.insert(0,md_baseDrivers['base'][i].baseTag)
                    md_driverTags[i] = l_tags
                    
                    
                    self.msgList_connect('finger{0}Drivers'.format(i), [md_handles[tag] for tag in l_tags])
                    
                #NewCurves
                log.debug(cgmGEN.logString_msg(_str_func,'Driver Curves...'))
                d_curveCreation = {}
                l_curveKeys = []
                for i,l in md_driverTags.iteritems():
                    key = "finger_{0}".format(i)
                    d_curveCreation[key] = {'keys':l,'rebuild':0}
                    l_curveKeys.append(key)
                
                #d_curveCreation.update(_d_curveCreation)
                md_resCurves = self.UTILS.create_defineCurve(self, d_curveCreation, md_handles, mFingerGroup)
                md_curves = md_resCurves['md_curves']
                ml_curves = md_resCurves['ml_curves']
                for mCrv in ml_curves:
                    mCrv.inheritsTransform=0
                    #mCrv.v=False                    
  
                    #self.msgList_connect('finger{0}Drivers'.format(k.capitalize()), ml)
                    #md_driverLists[k] = ml
                ml_mainCurves = ml_curves
                    
                #Visualization =================================================================
                log.debug(cgmGEN.logString_sub(_str_func,'Visualization...'))
                
                log.debug(cgmGEN.logString_msg(_str_func,'param scale'))
                l_scales = [1.0 for v in range(len(md_baseTags.keys()))]
                
                ATTR.datList_connect(self.mNode,'scaleX',l_scales)
                l_scaleX = ATTR.datList_getAttrs(self.mNode, 'scaleX')
                
                ATTR.datList_connect(self.mNode,'scaleY',l_scales)
                l_scaleY = ATTR.datList_getAttrs(self.mNode, 'scaleY')                
                
                ATTR.datList_connect(self.mNode,'scaleTaper',l_scales)                
                l_scaleTaper = ATTR.datList_getAttrs(self.mNode, 'scaleTaper')
                
                for a in l_scaleTaper + l_scaleX + l_scaleY:
                    ATTR.set_lock(_short,a,False)
                    ATTR.set_min(_short,a,.1)
                    
                for a in l_scaleY:
                    ATTR.set(_short,a,1.25)                    
                
                for i,k in enumerate(l_curveKeys):
                    mCrv = md_curves[k]
                    mBaseHandle = md_baseDrivers['base'][i]
                    _crv = CURVES.create_fromName(name='loftSquircle',
                                                  direction = 'z+', size = 1.0)
                    mProfile = cgmMeta.asMeta(_crv)
                    mProfile.doSnapTo(self.mNode)
                    mProfile.p_position = mBaseHandle.p_position
                    mProfile.v=False
                    
                    #extrude -ch true -rn false -po 0 -et 2 -ucp 1 -fpt 0 -upn 1 -rotation 0 -scale 1 -rsp 1 "baseInner_defineHandle_crv" "finger_0_defineCurve" ;
                    
                    _res = mc.extrude(mProfile.mNode,[mCrv.mNode],ucp=0,fixedPath=False,extrudeType=2,ch=True)
                    mSurface = cgmMeta.asMeta(_res[0])
                    mExtrude = cgmMeta.asMeta(_res[1])
                    
                    mProfile.rename("finger_{0}_profile".format(i))
                    mSurface.rename("finger_{0}_surf".format(i))
                    mExtrude.rename("finger_{0}_extrude".format(i))
                    
                    
                    mProfile.p_parent = mBaseHandle#mFingerGroup#mBaseHandle
                    mSurface.p_parent = mFingerGroup
                    
                    self.asHandleFactory().color(mSurface.mNode,transparent=True)
                    #CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = True)
                    
                    mExtrude.doConnectIn('scale',"{0}.{1}".format(_short,l_scaleTaper[i]))
                    #for a in 'XYZ':
                    mProfile.doConnectIn('scaleX',"{0}.{1}".format(_short,l_scaleX[i]))
                    mProfile.doConnectIn('scaleY',"{0}.{1}".format(_short,l_scaleY[i]))
                
                    mSurface.inheritsTransform = 0
                    mSurface.overrideEnabled = 1
                    mSurface.overrideDisplayType = 2
                    for s in mSurface.getShapes(asMeta=True):
                        s.overrideEnabled = 1
                        s.overrideDisplayType = 2
                        
                self.msgList_connect('finger{0}Curves'.format(i), ml_mainCurves)
                    
                
                    

                #cgmGEN.func_snapShot(vars())
                
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
    
def verify_subBlocks(self,forceNew=True):
    try:
        _str_func = 'verify_subBlocks'
        _short = self.mNode
        log.debug(cgmGEN.logString_start(_str_func))
        
        md_curves = {}
        md_uValues = {}
        md_drivers = {}
        md_driverLists ={}
        reload(CURVES)
        mNoTransformNull = self.getMessage('noTransDefineNull')
        
        #Fingers ------------------------------------------------------------------------------
        log.debug(cgmGEN.logString_msg(_str_func,'checking previous'))
        int_fingers = self.numFinger
        
        ml_fingerBlocks = self.msgList_get('fingerBlocks')
        if ml_fingerBlocks:
            if forceNew or len(ml_fingerBlocks) != int_fingers:
                for mBlock in ml_fingerBlocks:
                    mBlock.delete()
                    
        if int_fingers:
            log.debug(cgmGEN.logString_sub(_str_func,'fingers'))
            l_fingerTags = ['base','tip','mid','roll']
            
            log.debug(cgmGEN.logString_msg(_str_func,'finger Group...'))        
            mFingerGroup = self.getMessageAsMeta('fingerNoTrans')
            if mFingerGroup:
                mc.delete(mFingerGroup.getChildren())
            else:
                mFingerGroup =self.doCreateAt(setClass=True)
                mFingerGroup.rename('fingerStuff')
                mFingerGroup.p_parent = mNoTransformNull
                self.connectChildNode(mFingerGroup, 'fingerNoTrans','block')
            
            log.debug(cgmGEN.logString_msg(_str_func,'Gather dat...'))
            for k in l_fingerTags:
                mCurve = self.getMessageAsMeta("{0}LineDefineCurve".format(k))
                if not mCurve:
                    log.debug(cgmGEN.logString_msg(_str_func,'Missing Curve: {0}'.format(k)))
                else:
                    md_curves[k] = mCurve
                    
            log.debug(cgmGEN.logString_msg(_str_func,'uValues'))
            if int_fingers == 1:
                ml_uValues = [.5]
            elif int_fingers == 2:
                ml_uValues = [0.0,1.0]
            elif int_fingers == 3:
                ml_uValues = [0.0,.5, 1.0]
            else:
                ml_uValues = CURVES.getUSplitList(md_curves['base'].mNode,int_fingers,False,returnU=True)
                ml_uValues = MATH.normalizeList(ml_uValues)
            pprint.pprint(ml_uValues)
            
            log.debug(cgmGEN.logString_msg(_str_func,'param attributes'))
            ATTR.datList_connect(self.mNode,'paramFinger',ml_uValues)
            l_param = ATTR.datList_getAttrs(self.mNode, 'paramFinger')
            for a in l_param:
                ATTR.set_lock(_short,a,False)
                ATTR.set_min(_short,a,0.0)
                ATTR.set_max(_short,a,1.0)
            
            
            log.debug(cgmGEN.logString_msg(_str_func,'drivers...'))            
            for k in l_fingerTags:
                md_drivers[k] = {}
                ml = []
                for i,v in enumerate(ml_uValues):
                    log.debug(cgmGEN.logString_msg(_str_func,'Driver {0} | {1}...'.format(k,i)))        
                    
                    mLoc = cgmMeta.asMeta(self.doCreateAt(setClass=True))#self.doLoc(fastMode=True)#cgmMeta.asMeta(self.doCreateAt('locator'))
                    mCrv = md_curves[k]
                    
                    self.connectChildNode(mLoc, '{0}_{1}_fingerDriver'.format(k,i),'block')
                    mLoc.rename("{0}_{1}_driver".format(k,i))
                    mPointOnCurve = cgmMeta.asMeta(CURVES.create_pointOnInfoNode(mCrv.mNode,
                                                                                 turnOnPercentage=True))
                    
                    mPointOnCurve.doConnectIn('parameter',"{0}.{1}".format(self.mNode,l_param[i]))
                    mPointOnCurve.doConnectOut('position',"{0}.translate".format(mLoc.mNode))
                    mPointOnCurve.rename('{0}_{1}_fingerDriver_poci'.format(k,i))
                    mLoc.p_parent = mFingerGroup
                    
                    md_drivers[k][i] = mLoc
                    ml.append(mLoc)
                self.msgList_connect('finger{0}Drivers'.format(k.capitalize()), ml)
                md_driverLists[k] = ml
                
            pprint.pprint(md_curves)        
            pprint.pprint(md_drivers)
            
            
            log.debug(cgmGEN.logString_msg(_str_func,'scale...'))
            if int_fingers > 1:
                l_pos = [mObj.p_position for mObj in md_driverLists['mid']]                
                _width = DIST.get_distance_between_points(l_pos[0],l_pos[-1])/int_fingers
            else:
                _width = self.baseSize[2]/4
            
            log.debug(cgmGEN.logString_sub(_str_func,'fingers'))
            ml_fingerBlocks = []
            l_names = get_nameOptions(self,'finger',int_fingers)
            for i in range(int_fingers):
                _name = l_names[i]
                log.debug(cgmGEN.logString_msg(_str_func,'Finger {0} | {1}...'.format(i,_name)))
                length = DIST.get_distance_between_points(md_drivers['tip'][i].p_position,
                                                          md_drivers['mid'][i].p_position)
                
                mc.select(cl=True)
                mSub = cgmMeta.createMetaNode('cgmRigBlock',blockType='limb',
                                              name=_name,
                                              blockProfile='finger',baseSize = [_width,_width,length])
                ml_fingerBlocks.append(mSub)
                
                """
                mc.pointConstraint(md_drivers['mid'][i].mNode,
                                    mSub.mNode,
                                    maintainOffset = False)
                mc.orientConstraint(self.mNode,
                                   mSub.mNode,
                                   maintainOffset = False)                

                mSub.p_position = md_drivers['mid'][i].p_position
                for t in ['end','lever']:
                    mDefineHandle = mSub.getMessageAsMeta("define{0}Helper".format(t.capitalize()))
                    if t == 'end':
                        mDefineHandle.p_position = md_drivers['tip'][i].p_position
                        _tar = md_drivers['tip'][i]
                    else:
                        mDefineHandle.p_position = md_drivers['base'][i].p_position
                        _tar = md_drivers['base'][i]
                    
                    mc.pointConstraint(_tar.mNode,
                                        mDefineHandle.mNode,
                                        maintainOffset = False)
                    mDefineHandle.template=True
                    
                    
                print i"""
            
            self.msgList_connect('fingerBlocks',ml_fingerBlocks)
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
    
    
def sub_connect(self,mode='snap',forceNew=True):
    try:
        _str_func = 'sub_connect'
        _short = self.mNode
        log.debug(cgmGEN.logString_start(_str_func))
        
        md_drivers = {}

        mNoTransformNull = self.getMessage('noTransDefineNull')
        
        #Fingers ------------------------------------------------------------------------------
        int_fingers = self.numFinger
        
        ml_fingerBlocks = self.msgList_get('fingerBlocks')
        if ml_fingerBlocks:
            log.debug(cgmGEN.logString_sub(_str_func,'fingerBlocks'))            
            if not ml_fingerBlocks:
                log.warning("No finger blocks found")
                #if forceNew or len(ml_fingerBlocks) != int_fingers:
                    #for mBlock in ml_fingerBlocks:
                        #mBlock.delete()
            else:
                ml_midDrivers = self.msgList_get('fingerMidDrivers')
                ml_tipDrivers = self.msgList_get('fingerTipDrivers')
                ml_baseDrivers = self.msgList_get('fingerBaseDrivers')
                
                for i,mSub in enumerate(ml_fingerBlocks):
                    log.debug(cgmGEN.logString_msg(_str_func,'Finger {0} | {1}...'.format(i,mSub)))
                    
                    log.debug(cgmGEN.logString_msg(_str_func,'define...'))
                    mSub.p_position = ml_midDrivers[i].p_position
                    if mode == 'attach':
                        mc.pointConstraint(ml_midDrivers[i].mNode,
                                            mSub.mNode,
                                            maintainOffset = False)
                        mc.orientConstraint(self.mNode,
                                           mSub.mNode,
                                           maintainOffset = False)              
    
                    for t in ['end','lever']:
                        mDefineHandle = mSub.getMessageAsMeta("define{0}Helper".format(t.capitalize()))
                        if t == 'end':
                            mDefineHandle.p_position = ml_tipDrivers[i].p_position
                            _tar = ml_tipDrivers[i]
                        else:
                            mDefineHandle.p_position = ml_baseDrivers[i].p_position
                            _tar = ml_baseDrivers[i]
                            
                        if mode == 'attach':
                            mAttachGroup = mDefineHandle.getMessageAsMeta('attachGroup')
                            if not mAttachGroup:
                                mAttachGroup = mDefineHandle.doGroup(True,True, asMeta=True,
                                                                     typeModifier = 'attach')
                                
                        
                            mc.pointConstraint(_tar.mNode,
                                                mAttachGroup.mNode,
                                                maintainOffset = False)
                        mDefineHandle.template=True
                    
                    #Template....
                    log.debug(cgmGEN.logString_msg(_str_func,'template...'))
                    
            
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
        
def sub_detach(self):
    try:
        _str_func = 'sub_detach'
        _short = self.mNode
        log.debug(cgmGEN.logString_start(_str_func))
        
        md_drivers = {}

        mNoTransformNull = self.getMessage('noTransDefineNull')
        
        #Fingers ------------------------------------------------------------------------------
        ml_fingerBlocks = self.msgList_get('fingerBlocks')
        if ml_fingerBlocks:
            log.debug(cgmGEN.logString_sub(_str_func,'fingerBlocks'))            
            if not ml_fingerBlocks:
                log.warning("No finger blocks found")
            else:
                for i,mSub in enumerate(ml_fingerBlocks):
                    log.debug(cgmGEN.logString_msg(_str_func,'Finger {0} | {1}...'.format(i,mSub)))
                    l_const = mSub.getConstraintsTo()
                    if l_const:mc.delete(l_const)

                    for t in ['end','lever']:
                        mDefineHandle = mSub.getMessageAsMeta("define{0}Helper".format(t.capitalize()))
                        mAttachGroup = mDefineHandle.getMessageAsMeta('attachGroup')
                        if mAttachGroup:
                            l_const = mAttachGroup.getConstraintsTo()
                            if l_const:mc.delete(l_const)                                
                                
                        mDefineHandle.template=False            
            
    except Exception,err:
        cgmGEN.cgmException(Exception,err)
    








