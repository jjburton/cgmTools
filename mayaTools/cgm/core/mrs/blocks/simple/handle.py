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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
r9Meta.cleanCache()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.rig.joint_utils as JOINTS

import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.11062017'
__autoTemplate__ = True
__component__ = True
__menuVisible__ = True

#>>>Attrs ----------------------------------------------------------------------------------------------------
l_attrsStandard = ['side',
                   'position',
                   'hasRootJoint',
                   'hasJoint',
                   'basicShape',
                   'addAim',
                   'addPivotLeft',
                   'addPivotRight',
                   'addPivotCenter',
                   'addPivotFront',
                   'addPivotBack',
                   'moduleTarget']

d_attrsToMake = {'shapeDirection':":".join(CORESHARE._l_axis_by_string),
                 'axisAim':":".join(CORESHARE._l_axis_by_string),
                 'axisUp':":".join(CORESHARE._l_axis_by_string),                 
                 'targetJoint':'messageSimple',
                 'rootJoint':'messageSimple'}

d_defaultSettings = {'version':__version__,
                     'hasRootJoint':False,
                     'hasJoint':True,
                     'baseSize':10,#cm
                     'basicShape':5,
                     'addAim':True,
                     'addPivotLeft':True,
                     'addPivotRight':True,
                     'addPivotCenter':True,
                     'addPivotFront':True,
                     'addPivotBack':True,
                     'shapeDirection':2,
                     'axisAim':2,
                     'axisUp':4,
                     
                     'attachPoint':'end',
                     'proxyType':1}


#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    self.translate = 0,0,0
    self.rotate = 0,0,0
    #self.setAttrFlags(attrs=['translate','rotate','sx','sz'])
    #self.doConnectOut('sy',['sx','sz'])
    #ATTR.set_alias(_short,'sy','blockScale')
    
#=============================================================================================================
#>> Template
#=============================================================================================================
def template(self):
    _crv = CURVES.create_controlCurve(self.mNode, shape=self.getEnumValueString('basicShape'),
                                      direction = self.getEnumValueString('shapeDirection'),
                                      sizeMode = 'fixed', size = self.baseSize)
    CORERIG.shapeParent_in_place(self.mNode,_crv,False)
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
        
    CORERIG.colorControl(self.mNode,_side,'main',transparent = False) 
    
    self.msgList_connect('templateHandles',[self.mNode])

    return True

def templateDelete(self):
    return BLOCKUTILS.templateDelete(self)

def is_template(self):
    if self.getShapes():
        return True
    return False

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    #self._factory.puppet_verify()
    _str_func = 'prerig'
    _short = self.p_nameShort
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    _l_baseNames = ATTR.datList_get(self.mNode, 'baseNames')
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')

    self._factory.module_verify()  
    ml_templateHandles = self.msgList_get('templateHandles')
    
    #Create preRig Null  ==================================================================================
    mPrerigNull = BLOCKUTILS.prerigNull_verify(self)       
    
    if self.hasJoint:
        _size = DIST.get_bb_size(self.mNode,True,True)
        _sizeSub = _size * .2   
    
        log.info("|{0}| >> [{1}]  Has joint| baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     
    
        #Joint Helper ==========================================================================================
        mJointHelper = self.asHandleFactory(self.mNode).addJointHelper(baseSize = _sizeSub, loftHelper = False, lockChannels = ['scale'])
        ATTR.set_standardFlags(mJointHelper.mNode, attrs=['sx', 'sy', 'sz'], 
                               lock=False, visible=True,keyable=False)
    
        self.msgList_connect('jointHelpers',[mJointHelper.mNode])
        self.msgList_connect('prerigHandles',[self.mNode])
        
    #Pivot Helpers ==========================================================================================
    ml_pivots = []
    mPivotRootHandle = False
    self_pos = self.p_position
    self_upVector = self.getAxisVector('y+')
    for a in ['addPivotBack','addPivotFront','addPivotLeft','addPivotRight','addPivotCenter']:
        d_pivotDirections = {'back':'z-',
                             'front':'z+',
                             'left':'x+',
                             'right':'x-'}

        if self.getAttr(a):
            _strPivot = a.split('addPivot')[-1]
            _strPivot = _strPivot[0].lower() + _strPivot[1:]
            log.info("|{0}| >> Adding addPivot helper: {1}".format(_str_func,_strPivot))
            
            if _strPivot == 'center':
                pivot = CURVES.create_controlCurve(self.mNode, shape='circle',
                                                   direction = 'y+',
                                                   sizeMode = 'fixed',
                                                   size = _sizeSub)
                mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                mPivot.addAttr('cgmName',_strPivot)
                ml_pivots.append(mPivot)
            else:
                mAxis = VALID.simpleAxis(d_pivotDirections[_strPivot])
                _inverse = mAxis.inverse.p_string
                pivot = CURVES.create_controlCurve(self.mNode, shape='hinge',
                                                   direction = _inverse,
                                                   sizeMode = 'fixed', size = _sizeSub)
                mPivot = cgmMeta.validateObjArg(pivot,'cgmObject',setClass=True)
                mPivot.addAttr('cgmName',_strPivot)
                
                mPivot.p_position = DIST.get_pos_by_axis_dist(_short,mAxis.p_string, _size/2)
                SNAP.aim_atPoint(mPivot.mNode,self_pos, _inverse, 'y+', mode='vector', vectorUp = self_upVector)
            
                ml_pivots.append(mPivot)
        
                if not mPivotRootHandle:
                    pivotHandle = CURVES.create_controlCurve(self.mNode, shape='squareOpen',
                                                             direction = 'y+',
                                                             sizeMode = 'fixed', size = _size * 1.25)
                    mPivotRootHandle = cgmMeta.validateObjArg(pivotHandle,'cgmObject',setClass=True)
                    mPivotRootHandle.addAttr('cgmName','base')
                    mPivotRootHandle.addAttr('cgmType','pivotHelper')            
                    mPivotRootHandle.doName()
                    
                    CORERIG.colorControl(mPivotRootHandle.mNode,_side,'sub',transparent = False) 
                    
                    mPivotRootHandle.parent = mPrerigNull
                    self.connectChildNode(mPivotRootHandle,'pivotHelper','block')#Connect    
                    
    for mPivot in ml_pivots:
        mPivot.addAttr('cgmType','pivotHelper')            
        mPivot.doName()
        
        CORERIG.colorControl(mPivot.mNode,_side,'sub',transparent = False) 
        mPivot.parent = mPivotRootHandle
        mPivotRootHandle.connectChildNode(mPivot,'pivot'+ mPivot.cgmName.capitalize(),'handle')#Connect    



def prerigDelete(self):
    #if self.getMessage('templateLoftMesh'):
    #    mTemplateLoft = self.getMessage('templateLoftMesh',asMeta=True)[0]
    #    for s in mTemplateLoft.getShapes(asMeta=True):
    #        s.overrideDisplayType = 2     
    
    if self.getMessage('noTransformNull'):
        mc.delete(self.getMessage('noTransformNull'))
    return BLOCKUTILS.prerig_delete(self,templateHandles=True)

def is_prerig(self):
    return BLOCKUTILS.is_prerig(self,msgLinks=['moduleTarget','prerigNull'])

"""
def is_prerig(self):
    _str_func = 'is_prerig'
    _l_missing = []
    
    _d_links = {self : ['moduleTarget']}
    
    for plug,l_links in _d_links.iteritems():
        for l in l_links:
            if not plug.getMessage(l):
                _l_missing.append(plug.p_nameBase + '.' + l)
                
    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True"""
#=============================================================================================================
#>> rig
#=============================================================================================================
def rig(self):
    #
    self.moduleTarget._verifyMasterControl(size = DIST.get_bb_size(self,True,True))
    
    if self.hasRootJoint:
        if not is_skeletonized(self):
            skeletonize(self)
            
        mJoint = self.getMessage('rootJoint', asMeta = True)[0]
        log.info(mJoint)
        mJoint.p_parent = self.moduleTarget.masterNull.skeletonGroup  

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
                _l_missing.append(plug.p_nameBase + '.' + l)

    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True

#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def build_skeleton(self, forceNew = True):
    _short = self.mNode
    _str_func = '[{0}] > build_skeleton'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func)) 
    
    if not self.hasJoint:
        return True
    
    _radius = 1
    ml_joints = []
    
    mModule = self.moduleTarget
    if not mModule:
        raise ValueError,"No moduleTarget connected"
    
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError,"No rigNull connected"
    
    ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
    if not ml_prerigHandles:
        raise ValueError,"No prerigHandles connected"
    
    #>> If skeletons there, delete ----------------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        
    mJoint = self.jointHelper.doCreateAt('joint')
    JOINTS.freezeOrientation(mJoint)
    
    #mJoint.connectParentNode(self,'module','rootJoint')
    
    self.copyAttrTo('cgmName',mJoint.mNode,'cgmName',driven='target')
    #mJoint.doStore('cgmTypeModifier','root')
    mJoint.doName()
    
    mRigNull.msgList_connect('moduleJoints', [mJoint])
    return mJoint.mNode        
    

def skeletonize(self):
    #    
    if is_skeletonized(self):
        return True
    
    if self.hasRootJoint:
        mJoint = self.doCreateAt('joint')
        mJoint.connectParentNode(self,'module','rootJoint')
        self.copyAttrTo('puppetName',mJoint.mNode,'cgmName',driven='target')
        mJoint.doStore('cgmTypeModifier','root')
        mJoint.doName()
        return mJoint.mNode
        #self.msgList_connect('modul')
        
def is_skeletonized(self):
    if self.hasRootJoint:
        if not self.getMessage('rootJoint'):
            return False
    return True

def skeletonDelete(self):
    if is_skeletonized(self):
        log.warning("MUST ACCOUNT FOR CHILD JOINTS")
        mc.delete(self.getMessage('rootJoint'))
    return True
            






 








