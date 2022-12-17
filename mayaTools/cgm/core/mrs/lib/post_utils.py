"""
------------------------------------------
cgm.core.mrs.lib.post_utils
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
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
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel    

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import cgm.core.cgm_General as cgmGEN
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
import cgm.core.rig.general_utils as CORERIGGEN
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core import cgm_RigMeta as cgmRigMeta
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.lib.string_utils as STRINGS
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.position_utils as POS
import cgm.core.rig.joint_utils as JOINT
import cgm.core.lib.search_utils as SEARCH
import cgm.core.rig.ik_utils as IK
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.lib.shapeCaster as SHAPECASTER
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.cgm_RigMeta as cgmRIGMETA
import cgm.core.lib.shared_data as CORESHARE

# From cgm ==============================================================
import cgm.core.cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = cgmGEN.get_releaseString()

log_start = cgmGEN.logString_start
log_sub = cgmGEN.logString_sub
log_msg = cgmGEN.logString_msg

def swimSettings_get(deformer = None,handle = None):
    d = {}
    mObj = cgmMeta.asMeta(deformer)
    d['node_t'] = mObj.translate
    d['node_r'] = mObj.rotate
    d['node_s'] = mObj.scale

    for a in mObj.getAttrs(ud=True):
        d[a] = ATTR.get(mObj.mNode,a)
        
    mHandle = cgmMeta.asMeta(handle)
    d['handle_t'] = mHandle.translate
    d['handle_r'] = mHandle.rotate
    d['handle_s'] = mHandle.scale

    pprint.pprint(d)
    return d

def swimSettings_set(deformer = None,handle = None, d=None):
    mObj = cgmMeta.asMeta(deformer)
    mObj.translate = d['node_t']
    mObj.rotate = d['node_r']
    mObj.scale = d['node_s']
    
    for a,v in d.iteritems(): 
        try:ATTR.set(mObj.mNode, a, v)
        except Exception,err:
            print("{} | {} | {}".format(a,v,err))
    mHandle = cgmMeta.asMeta(handle)
    mHandle.translate =  d['handle_t'] 
    mHandle.rotated = ['handle_r'] 
    mHandle.scaled = ['handle_s']  

    return d


def autoSwim(controlSurface = None, waveControl = None, deformer = 'wave', baseName = '', mModule = None, ml_joints = None, setupCycle = 1,cycleLength = 100, cycleOffset = -20, orient = 'zyx'):
    _str_func = 'autoSwim'
    log_start(_str_func)
    
    _nameTag = '{}autoSwim_{}'.format(baseName, deformer)
    
    mModule = cgmMeta.validateObjArg(mModule,mType='cgmRigModule')
    mRigNull = mModule.rigNull
    _str_rigNull = mRigNull.mNode
    
    mRoot = mRigNull.rigRoot
    if not ml_joints:
        ml_joints = mRigNull.msgList_get('segmentJoints')
        
    ml_blends = mRigNull.msgList_get('blendJoints')
    if not ml_blends:
        ml_blends = mRigNull.msgList_get('fkJoints')
    
    mTargetSurface = cgmMeta.validateObjArg(controlSurface,mayaType='nurbsSurface')
    
    if not waveControl:
        mSettings = ml_blends[0].doCreateAt()
        mSettings.doStore('cgmName',_nameTag)
        mSettings.doStore('cgmNameModifier','settings')
        
        mSettings.doName()
        
        mSettings.p_parent = ml_blends[0]
        
        
        mRigNull.connectChildNode(mSettings.mNode,'swimControl','rigNull')
        
        
        #Shape
        #bb_ik = POS.get_bb_size(mIKFormHandle.mNode,True,mode='maxFill')
        #bb_ik = [v * 1.5 for v in bb_ik]
    
        _ik_shape = CURVES.create_fromName('sphere', size = DIST.get_distance_between_points(ml_blends[0].p_position,
                                                                                             ml_blends[-1].p_position))
        SNAP.go(_ik_shape,mSettings.mNode)
        CORERIG.shapeParent_in_place(mSettings.mNode, _ik_shape, False)        
        
        
        #aim setup...
        
        mBaseOrientGroup = mSettings.doCreateAt()
        mBaseOrientGroup.rename('{}_orient'.format(_nameTag))
        mBaseOrientGroup.p_parent = mSettings
        
        ATTR.set(mBaseOrientGroup.mNode, 'rotateOrder', orient)
    
        mLocBase = mSettings.doCreateAt()
        mLocAim = mSettings.doCreateAt()
    
        mLocAim.doStore('cgmType','aimDriver')
        mLocBase.doStore('cgmType','baseDriver')
    
    
        for mObj in mLocBase,mLocAim:
            mObj.doStore('cgmName',mSettings.mNode)                        
            mObj.doName()
            mObj.p_parent = mSettings
                        
    
        mAimTarget = ml_blends[-1]
        """
                            _direction = self.d_module['direction'] or 'center'
                            if _direction.lower() == 'left':
                                v_aim = [0,0,1]
                            else:
                                v_aim = [0,0,-1]"""
    
        mc.aimConstraint(mAimTarget.mNode, mLocAim.mNode, maintainOffset = True,
                         aimVector = [0,0,1], upVector = [0,1,0], 
                         worldUpObject = mSettings.mNode,
                         worldUpType = 'objectrotation', 
                         worldUpVector = [0,1,0])#self.v_twistUp
    
    
        const = mc.orientConstraint([mLocAim.mNode,mLocBase.mNode],
                                    mBaseOrientGroup.mNode, maintainOffset = True)[0]
    
        d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mSettings.mNode,
                                                              'aim'],
                                                             [mSettings.mNode,'resRootFollow'],
                                                             [mSettings.mNode,'resFullFollow'],
                                                             keyable=True)
    
        targetWeights = mc.orientConstraint(const,q=True,
                                            weightAliasList=True,
                                            maintainOffset=True)
    
        #Connect                                  
        d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
        d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
        d_blendReturn['d_result1']['mi_plug'].p_hidden = True
        d_blendReturn['d_result2']['mi_plug'].p_hidden = True                                            

        
                
        
    else:
        mSettings = cgmMeta.validateObjArg(waveControl)
    
    
    #Duplicate our surface
    mSwimSurface = mTargetSurface.doDuplicate(po=False)
    #mSwimSurface.p_parent = False
    mSwimSurface.rename("{}_autoSwim_surface".format(baseName))
    
    #Make our deformer
    _buffer = mc.nonLinear (mSwimSurface.mNode, type = deformer, name = _nameTag)
    
    mDeformer = cgmMeta.asMeta(_buffer[0])
    mDeformerHandle = cgmMeta.asMeta(_buffer[1])
    mDeformerHandle.rename("{}_handle".format(_nameTag))
    mDeformer.rename("{}_deformer".format(_nameTag))
    
    mDeformerHandle.p_position = ml_joints[0].p_position
    mDeformerHandle.rx = 90
    mDeformerHandle.ry = 90
    
    mDeformer.dropoff = 1
    mDeformer.dropoffPosition = 1
    mDeformer.maxRadius = 2
    
    if not waveControl:#Parent under out settings
        mDeformerHandle.p_parent = mBaseOrientGroup
        
    else:
        mDeformerHandle.p_parent = ml_blends[0]
    
    #...blendshape
    blendshapeNode = mc.blendShape (mSwimSurface.mNode, mTargetSurface.mNode, name = '{}_bsNode'.format(_nameTag) )
    
    mRigNull.connectChildNode(mDeformerHandle.mNode,'swimHandle','rigNull')
    
    
    #...attributes =================================================================================================
    _settings = mSettings.mNode
    l_order = ['swim','speed','wavelength','amplitude','dropoff','dropoffPosition']
    d_attrs = {'swim':{'min':0,'max':1, 'dv':0,'target':"{0}.{1}".format(blendshapeNode[0],
                                                                        mSwimSurface.p_nameBase)},
               'speed':{'min':-100,'max':100,'dv':0,'v':1},
               'wavelength':{'min':0,'max':10,'dv':5,'v':5,'target':'deformer'},
               'amplitude':{'min':0,'max':10,'dv':0,'v':0,'target':'deformer'},
               'dropoff':{'min':0,'max':1,'dv':1,'v':1,'target':'deformer'},
               'dropoffPosition':{'min':0,'max':1,'dv':0,'v':0,'target':'deformer'},
               'minRadius':{'min':0,'max':10,'dv':10,'v':1,'target':'deformer'},
               'maxRadius':{'min':0,'max':10,'dv':10,'v':10,'target':'deformer'},
               'lowBound':{'min':-100,'max':100,'dv':-1,'v':-1,'target':'deformer'},
               'highBound':{'min':-100,'max':100,'dv':1,'v':1,'target':'deformer'},               
                 }
    
    if not setupCycle:
        d_attrs['offset'] = {'dv':0,'v':0,'target':'deformer'}
        l_order.append('offset')
        
        d_attrs.pop('speed')
        l_order.remove('speed')
        
    if deformer == 'wave':
        l_order.extend(['minRadius','maxRadius'])
    elif deformer == 'sine':
        l_order.extend(['lowBound','highBound'])
    
    for a in l_order:
        _d = d_attrs[a]
        _target = _d.get('target')
        
        if _target == 'deformer':
            if not mc.objExists('{}.{}'.format(mDeformer.mNode,a)):
                print("{} doesn't exist".format(a))
                continue
        
        _kws = {}
        for k in ['min','max','dv']:
            _v = _d.get(k)
            if _v is not None:
                if k == 'min':
                    _kws['minValue'] = _v
                elif k == 'max':
                    _kws['maxValue'] = _v
                elif k == 'dv':
                    _kws['defaultValue'] = _v
                    
        ATTR.add(_settings, a, 'float', value = _d.get('v',0), hidden = False, keyable = True, **_kws)
        
        if _target:
            if _target == 'deformer':
                ATTR.connect("{}.{}".format(_settings,a), "{}.{}".format(mDeformer.mNode,a))
            else:
                ATTR.connect("{}.{}".format(_settings,a), _target)
                
    mSettings.speed = 1
    mSettings.wavelength = 4
    mSettings.amplitude = .3
    mSettings.dropoff = 1
    mSettings.dropoffPosition = 1
    mSettings.minRadius = 0    
    mSettings.maxRadius = 2
    
    if setupCycle:
        import cgm
        reload(cgm.lib.nodes)
        cgm.lib.nodes.offsetCycleSpeedControlNodeSetup (mDeformer.mNode,(_settings+'.speed'),cycleLength,cycleOffset)
    
    pprint.pprint(vars())
    
    return
    if mModule:#if we have a module, connect vis
        for mObj in [mDeformerHandle]:
            mObj.overrideEnabled = 1
            cgmMeta.cgmAttr(_str_rigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(_str_rigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(mObj.mNode,'overrideDisplayType'))    
            #mObj.parent = mRigNull        
    


def skin_mesh(mMesh,ml_joints,**kws):
    try:
        _str_func = 'skin_mesh'
        log_start(_str_func)
        l_joints = [mObj.mNode for mObj in ml_joints]
        _mesh = mMesh.mNode
        """
        try:
            kws_heat = copy.copy(kws)
            _defaults = {'heatmapFalloff' : 1,
                         'maximumInfluences' : 2,
                         'normalizeWeights' : 1, 
                         'dropoffRate':7}
            for k,v in _defaults.iteritems():
                if kws_heat.get(k) is None:
                    kws_heat[k]=vars
                    
            skin = mc.skinCluster (l_joints,
                                   _mesh,
                                   tsb=True,
                                   bm=2,
                                   wd=0,
                                   **kws)
        except Exception,err:"""
        #log.warning("|{0}| >> heat map fail | {1}".format(_str_func,err))
        skin = mc.skinCluster (l_joints,
                               mMesh.mNode,
                               tsb=True,
                               bm=0,#0
                               maximumInfluences = 3,
                               wd=0,
                               normalizeWeights = 1,dropoffRate=5)
        """ """
        skin = mc.rename(skin,'{0}_skinCluster'.format(mMesh.p_nameBase))
        #mc.geomBind( skin, bindMethod=3, mi=3 )
        
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())

    

def backup(self,ml_handles = None):
    try:
        _str_func = 'segment_handles'
        log_start(_str_func)
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        _offset = self.v_offset
        _jointOrientation = self.d_orientation['str']
        
        if not ml_handles:
            raise ValueError,"{0} | ml_handles required".format(_str_func)        
      
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    
    


d_default = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:.25, 1:.5}},
           'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5}},
           'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':70, '-':-30,'ease':{0:.25, 1:.5}},}

def SDK_wip(ml = [], matchType = False, settings = None,
            d_attrs = d_default, skipLever = True, skipFKBase = []):
    _str_func = 'siblingSDK_wip'
    log.info(cgmGEN.logString_start(_str_func))
    
    if not ml:
        ml = cgmMeta.asMeta(sl=1)
    else:
        ml = cgmMeta.asMeta(ml)
    
    #mParent -----------------------------------------------------------------------------
    mParent = ml[0].moduleParent
    if not settings:
        mParentSettings = mParent.rigNull.settings
    else:
        mParentSettings = cgmMeta.asMeta(settings)
    #pprint.pprint([mParent,mParentSettings])
    _settings = mParentSettings.mNode

    #Siblings get ------------------------------------------------------------------------
    #mSiblings = mTarget.atUtils('siblings_get',excludeSelf=False, matchType = matchType)
    mSiblings = ml
    
    md = {}
    d_int = {}
    
    #Need to figure a way to get the order...
    for i,mSib in enumerate(mSiblings):
        log.info(cgmGEN.logString_start(_str_func, mSib.__repr__()))
        
        _d = {}
        
        
        if mSib.moduleType == 'handle':
            ml_fk = [mSib.rigNull.getMessageAsMeta('handle')]
        else:
            ml_fk = mSib.atUtils('controls_get','fk')
            
        if not ml_fk:
            log.warning('missing fk. Skippping...')
            continue
        
        
        if skipLever or skipFKBase:
            if i in skipFKBase:
                ml_fk = ml_fk[1:]
            elif skipLever and mSib.getMessage('rigBlock') and mSib.rigBlock.getMayaAttr('blockProfile') in ['finger']:
                ml_fk = ml_fk[1:]
            
        #if 'thumb' not in mSib.mNode:
        #    ml_fk = ml_fk[1:]
            
        
        
        _d['fk'] = ml_fk
        ml_sdk = []
        

        
        for ii,mFK in enumerate(ml_fk):
            mSDK = mFK.getMessageAsMeta('sdkGroup')
            if not mSDK:
                mSDK =  mFK.doGroup(True,True,asMeta=True,typeModifier = 'sdk')            
            ml_sdk.append(mSDK)
            
            if not d_int.get(ii):
                d_int[ii] = []
            
            d_int[ii].append(mSDK)
            
        _d['sdk'] = ml_sdk
        
        md[mSib] = _d
        
    #pprint.pprint(md)
    #pprint.pprint(d_int)
    #return
    
    for a,d in d_attrs.iteritems():
        log.info(cgmGEN.logString_sub(_str_func,a))
        for i,mSib in enumerate(mSiblings):
            log.info(cgmGEN.logString_sub(_str_func,mSib))  
            d_sib = copy.deepcopy(d)
            d_idx = d.get(i,{})
            if d_idx:
                _good = True
                for k in ['d','+d','-d','+','-']:
                    if not d_idx.get(k):
                        _good = False
                        break
                if _good:
                    log.info(cgmGEN.logString_msg(_str_func,"Found d_idx on mSib | {0}".format(d_idx))) 
                    d_use = copy.deepcopy(d_idx)
            else:d_use = copy.deepcopy(d_sib)
            
            d2 = md[mSib]
            str_part = mSib.getMayaAttr('cgmName') or mSib.get_partNameBase()
            
            #_aDriver = "{0}_{1}".format(a,i)
            _aDriver = "{0}_{1}".format(a,str_part)
            if not mParentSettings.hasAttr(_aDriver):
                ATTR.add(_settings, _aDriver, attrType='float', keyable = True)            
            
            log.info(cgmGEN.logString_msg(_str_func,"d_sib | {0}".format(d_sib))) 
            for ii,mSDK in enumerate(d2.get('sdk')):
                
                d_cnt = d_idx.get(ii,{}) 
                if d_cnt:
                    log.info(cgmGEN.logString_msg(_str_func,"Found d_cnt on mSib | {0}".format(d_cnt))) 
                    d_use = copy.deepcopy(d_cnt)
                else:d_use = copy.deepcopy(d_sib)
                
                log.info(cgmGEN.logString_msg(_str_func,"{0}| {1} | {2}".format(i,ii,d_use))) 
                
                if d_use.get('skip'):
                    continue                
                
                d_ease = d_use.get('ease',{})
                v_ease = d_ease.get(ii,None)
                
                l_rev = d_sib.get('reverse',[])
                
                if  issubclass( type(d_use['d']), dict):
                    d_do = d_use.get('d')
                else:
                    d_do = {d_use['d'] : d_use}
                    
                    
                for k,d3 in d_do.iteritems():
                    
                    if d3.get('skip'):
                        continue

                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, k),
                                         currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                         itt='linear',ott='linear',                                         
                                         driverValue = 0, value = 0)
                    
                    #+ ------------------------------------------------------------------
                    pos_v = d3.get('+')
                    pos_d = d_use.get('+d', 1.0)
                    if v_ease is not None:
                        pos_v = pos_v * v_ease
                    
                    if i in l_rev:
                        print("...rev pos")
                        pos_v*=-1
                    
                    ATTR.set_max("{0}.{1}".format(_settings, _aDriver),pos_d)
                    
                    if pos_v:
                        mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, k),
                                         currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                         itt='linear',ott='linear',                                         
                                         driverValue = pos_d, value = pos_v)
                    
                    
                    #- ----------------------------------------------------------
                    neg_v = d3.get('-')
                    neg_d = d_use.get('-d', -1.0)
                    if v_ease is not None:
                        neg_v = neg_v * v_ease                
                    
                    if i in l_rev:
                        print("...rev neg")                        
                        neg_v*=-1
                            
                    ATTR.set_min("{0}.{1}".format(_settings, _aDriver),neg_d)
                        
                    if neg_v:
                        mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, k),
                                         currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                         itt='linear',ott='linear',                                         
                                         driverValue = neg_d, value = neg_v)        
     



#bear...
d_toeClaws = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:.25, 1:.5, 3:0}},
              'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5, 3:0}},
              'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':85, '-':-50},
              'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
              #0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
              0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-20, '-':60}},#index
              1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':20}},#middle
              2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-20}},#ring
              3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':20, '-':-60}}}#pinky                
              }

d_attrs_toesLever = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:0.2, 1:.25, 1:.5, 3:0}},
                'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:0.2, 1:.25, 1:.5, 3:0}},
                'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':85, '-':-50,'ease':{0:.2,1:1,2:1,3:0}},
                'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                #0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
                0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25},
                   1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':50}},#index
                1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':5},
                   1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':10}},#middle
                2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10},
                   1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':-20}},#ring
                3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30},
                   1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':-60}}}#pinky                
                }

d_attrs_toes3Lever = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:0.2, 1:.25, 1:.5, 3:0}},
                      'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:0.2, 1:.25, 1:.5, 3:0}},
                      'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':85, '-':-50,'ease':{0:.2,1:1,2:1,3:0}},
                      'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                      #0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
                      0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25},
                         1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':50}},#index
                      1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':5},
                         1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':10}},#middle
                      2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30},
                         1:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':-60}}}#pinky                
                      }


d_fingers = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
             'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
             'roll':{
                 0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                 'd':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40},
             'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
             0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
             1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
             2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
             3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
             4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_fingersToon = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                 'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
                 'roll':{
                     0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                     'd':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40},
                 'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                 0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':60}},#thumb
                 1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
                 2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
                 3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
                 4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

#thumb in x 35, y -11.9
#thumb out -38, 21 -11
d_fingersFlat = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
             'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
             'roll':{
                 0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                 'd':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40},
             'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
             0:{0:{'d':{'ry':{'+':-11.9, '-':21},
                        'rz':{'+':-11},
                        'rx':{'+':35, '-':-38}},
                        '+d':10.0, '-d':-10.0}},#thumb
             1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
             2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
             3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
             4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky


d_otterPaw = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
                'roll':{
                    #0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                    'd':'rx', '+d':10.0, '-d':-10.0, '+':80, '-':-40},
                'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':0,
                0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-12, '-':30}},#thumb
                1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-4, '-':17}},#index
                2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':0, '-':1}},#middle
                3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':2, '-':-15}},#ring
                4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':3.2, '-':-40}}}}#pinky

d_fingersPaw = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
                'roll':{
                    #0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                    'd':'rx', '+d':10.0, '-d':-10.0, '+':80, '-':-40},
                'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':0,
                0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
                1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-25, '-':40}},#index
                2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
                3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':20, '-':-20}},#ring
                4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':30, '-':-30}}}}#pinky
d_pawSimple = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5, 1:.7}},
                'roll':{
                    #0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                    'd':'rx', '+d':10.0, '-d':-10.0, '+':80, '-':-40},
                'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':0,
                0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-25, '-':40}},#index
                1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
                2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':20, '-':-20}},#ring
                3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':30, '-':-30}}}}#pinky

d_pawFront= {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.5,}},
               'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5}},
               'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':120, '-':-40, 'ease':{1:.3,}},
               'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
               0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
               1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
               2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
               3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
               4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_dragonFront= {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.5,2:0}},
               'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5,2:0}},
               'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':90, '-':-40, 'ease':{1:.5,2:0}},
                       #0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':60, '-':-40, 'ease':{1:.5,2:0}}}},
               'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':0,
               0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-40, '-':25}},#thumb
               1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
               2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
               3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-30}}}}#pinky

d_catPaw = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.5,}},
            'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5}},
            'claw':{'d':'rx', '+d':10.0, '-d':-10.0, '+':20, '-':-120, 'ease':{0:0,}},            
            'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':120, '-':-40, 'ease':{1:0,}},
            'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
            0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':45}},#thumb
            1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
            2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
            3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
            4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_pawBack = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.5,}},
               'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.5}},
               'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':120, '-':-40, 'ease':{1:.3,}},
               'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
               0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':45}},#thumb
               1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
               2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
               3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':5, '-':-10}},#ring
               4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_attrs = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
           'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5}},
           'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':80, '-':-40,
                   0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10,'-':-40},
                      1:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10,'-':-10}}},     
            'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                      0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':40, '-':-25}},#thumb
                      1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':25}},#index
                      2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':1}},#middle
                      3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky



d_talons = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5,2:0}, 'reverse':[0]},
              'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5,2:0}, 'reverse':[0]},
              'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':100, '-':-40, 'ease':{1:.5, 2:.5,2:0}},
              'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':-0,
              0:{'skip':True},#thumb
              1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-20, '-':25}},#index
              2:{0:{'d':'ry', '+d':10.0, '-d':-10.0,'+':0, '-':0}},#middle
              3:{0:{'d':'ry',  '+d':10.0, '-d':-10.0, '+':20, '-':-25}},#ring
              4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_batToes = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5,2:0}, 'reverse':[0]},
             'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5,2:0}, 'reverse':[0]},
             'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':100, '-':-40, 'ease':{1:.8, 2:.5,2:0}},
             'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':-0,
             0:{'skip':True},#thumb
             1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-20, '-':25}},#index
             2:{0:{'d':'ry', '+d':10.0, '-d':-10.0,'+':0, '-':0}},#middle
             3:{0:{'d':'ry',  '+d':10.0, '-d':-10.0, '+':20, '-':-25}},#ring
             4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky


d_dragonFrontBak = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}},
                 'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5}},
                 'roll':{0:{0:{'d':'rx', '+d':10.0, '-d':-10.0, '+':10, '-':-40}},
                 'd':'rx', '+d':10.0, '-d':-10.0, '+':80, '-':-40},
                 'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':1,'-':-1,
                 0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-10, '-':10}},#inner
                 1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-20, '-':25}},#main
                 2:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':-5, '-':-10}},#mid
                 3:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':40, '-':-30}},#end
                 4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':10, '-':-30}}}}#pinky

d_tailFan7 = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':30, '-':-30, 'ease':{0:.25, 1:.5}, 'reverse':[0,1,2]},
              'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':50, '-':-50,'ease':{0:.25, 1:.5}, 'reverse':[0,1,2]},
              'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':100, '-':-40, 'ease':{0:.25, 1:.5, 2:.5}},
              'spread':{'d':'ry','+d':10.0, '-d':-10.0,'+':0,'-':-0,
              0:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':90, '-':-50}},
              1:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':60, '-':-30}},
              2:{0:{'d':'ry', '+d':10.0, '-d':-10.0,'+':30, '-':-20}},
              3:{'skip':True},#---middle
              4:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':30, '-':-20}},
              5:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':60, '-':-30}},
              6:{0:{'d':'ry', '+d':10.0, '-d':-10.0, '+':90, '-':-50}},
              
              }}#pinky


def siblingSDK_wip(mTarget = 'L_ring_limb_part',matchType = False,
                   d_attrs = d_default):
    _str_func = 'siblingSDK_wip'
    log.info(cgmGEN.logString_start(_str_func))
    
    if mTarget is None:
        mTarget = cgmMeta.asMeta(sl=1)
        if mTarget:mTarget = mTarget[0]
    else:
        mTarget = cgmMeta.asMeta(mTarget)
        
    #mParent -----------------------------------------------------------------------------
    mParent = mTarget.moduleParent
    mParentSettings = mParent.rigNull.settings
    
    #pprint.pprint([mParent,mParentSettings])
    _settings = mParentSettings.mNode

    #Siblings get ------------------------------------------------------------------------
    mSiblings = mTarget.atUtils('siblings_get',excludeSelf=False, matchType = matchType)
    md = {}
    #Need to figure a way to get the order...
    for i,mSib in enumerate(mSiblings):
        log.info(cgmGEN.logString_start(_str_func, mSib.__repr__()))
        
        _d = {}
        
        ml_fk = mSib.atUtils('controls_get','fk')
        if not ml_fk:
            log.warning('missing fk. Skippping...')
            continue
        
        
        if 'thumb' not in mSib.mNode:
            ml_fk = ml_fk[1:]
            
        
        
        _d['fk'] = ml_fk
        ml_sdk = []
        
        str_part = mSib.get_partNameBase()

        
        for mFK in ml_fk:
            mSDK = mFK.getMessageAsMeta('sdkGroup')
            if not mSDK:
                mSDK =  mFK.doGroup(True,True,asMeta=True,typeModifier = 'sdk')            
            ml_sdk.append(mSDK)
            
            

        for a,d in d_attrs.iteritems():
            log.info("{0} | ...".format(a))
            
            _aDriver = "{0}_{1}".format(a,i)
            #_aDriver = "{0}_{1}".format(str_part,a)
            if not mParentSettings.hasAttr(_aDriver):
                ATTR.add(_settings, _aDriver, attrType='float', keyable = True)
            
            
            for mSDK in ml_sdk:
                mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = 0, value = 0)
                
                #+ ------------------------------------------------------------------
                pos_v = d.get('+')
                pos_d = d.get('+d', 1.0)
                
                if pos_v:
                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = pos_d, value = pos_v)
                
                
                #- ----------------------------------------------------------
                neg_v = d.get('-')
                neg_d = d.get('-d', -1.0)
                    
                if neg_v:
                    mc.setDrivenKeyframe("{0}.{1}".format(mSDK.mNode, d['d']),
                                     currentDriver = "{0}.{1}".format(_settings, _aDriver),
                                     itt='linear',ott='linear',                                         
                                     driverValue = neg_d, value = neg_v)        
 
            
        _d['sdk'] = ml_sdk
        md[mSib] = _d
        

def dynParent_proxyControlAttributes(mDynParentGroups = None, test = 1):
    l_dynParentAttributes = ['space','orientTo','follow','scaleSpace']
    
    _str_func = 'dynParent_proxyControlAttributes'
    log.info(log_start(_str_func))
    if not mDynParentGroups:
        mDynParentGroups = r9Meta.getMetaNodes(mTypes = 'cgmDynParentGroup',nTypes=['transform'])
    else:
        mDynParentGroups = cgmMeta.validateObjListArg(mDynParentGroups,mType='cgmDynParentGroup')

    for mGroup in mDynParentGroups:
        mChild = mGroup.getMessageAsMeta('dynChild')
        if not mChild:
            log.info("Skip: {}".format(mGroup))
            continue
        
        log.info("Child: {}".format(mChild))
        _group = mGroup.mNode
        _child = mChild.mNode
        
        for a in l_dynParentAttributes:
            if mChild.hasAttr(a):
                log.info( a )
                
                ATTR.copy_to(_child, a, _group, a,convertToMatch = True,
                             values = True, inConnection= True,
                             outConnections = True, keepSourceConnections = True,
                             copySettings = True, driven = False)
                ATTR.delete(_child,a)
            
                #proxy it back
                mc.addAttr(_child, ln=a, proxy="{}.{}".format(_group,a))        
        log.info('>'*8 + " End Group: {}".format(mGroup) + '-'*50)
        
        

def settings_createRootHolder(mSettings = None):
    _str_func = 'settings_createRootHolder'
    log.info(log_start(_str_func))
    if not mSettings:
        mSettings = cgmMeta.asMeta(sl=1)
    else:
        mSettings = cgmMeta.validateObjListArg(mSettings)
        
        
    for mCtrl in mSettings:
        log.info(log_sub(mCtrl))
        
        #Create our curve...--------------------------------------------------------
        try:_string = mCtrl.cgmOwner.module.ribBlock.cgmName
        except:
            _string = mCtrl.p_nameBase
            
        _size = TRANS.bbSize_get(mCtrl.mNode,True,'max')
        mNew = cgmMeta.asMeta(CURVES.create_text(_string, _size))
        mNew.doSnapTo(mCtrl)
        
        mNew.rename('rootHolder_{}'.format(mCtrl.p_nameBase))
        
        
        #Prep...
        
        _orig = mCtrl.mNode
        _new = mNew.mNode
        
        
        #Move attrs...----------------------------------------------------------------------------
        for a in ['FKIK', 'visSub', 'visSub_out', 'visRoot', 'visRoot_out', 'visDirect', 'visDirect_out',  'result_FKon', 'result_IKon', 'blendParam']:
            if mCtrl.hasAttr(a):
                reload(ATTR)
                
                #Move
                ATTR.copy_to(_orig, a, _new, a,convertToMatch = True,
                             values = True, inConnection= True,
                             outConnections = True, keepSourceConnections = True,
                             copySettings = True, driven = False)
                ATTR.delete(_orig,a)
        
                #proxy it back
                if a in ['FKIK','visSub','visRoot','visDirect','blendParam']:
                    mc.addAttr(_orig, ln=a, proxy="{}.{}".format(_new,a))
                
        
        return mNew
        
def repair_rigJointWiring(nodes=None):
    _str_func = 'repair_rigJointWiring'
    log.info(log_start(_str_func))
    
    
    if not nodes:
        mNodes = cgmMeta.asMeta(sl=1)
    else:
        mNodes = cgmMeta.validateObjListArg(nodes)
        
    for mObj in mNodes:
        log.info(log_sub(_str_func,mObj))
        
        if not mObj.getMessage('rigJoint'):
            log.info(log_msg(_str_func,"Needs rigJoint"))
            mDrivers = mObj.getConstrainingObjects(asMeta=1)
            if mDrivers:
                ATTR.store_info(mObj.mNode, 'rigJoint',mDrivers[0])
                log.info(log_msg(_str_func,"Used: {}".format(mDrivers[0])))
            else:
                log.error(log_msg(_str_func,"No driver found"))
                
            
    

def settings_pullFromDeformation(mPuppets = None, test = 1):
    _str_func = 'settings_pullFromDeformation'
    log.info(log_start(_str_func))
    if not mPuppets:
        mPuppets = r9Meta.getMetaNodes(mTypes = 'cgmRigPuppet',nTypes=['transform','network'])
    else:
        mPuppets = cgmMeta.validateObjListArg(mPuppets,mType='cgmRigPuppet')



    for mPuppet in mPuppets:
        log.info(log_sub(mPuppet))
        mMasterSettings = mPuppet.masterControl.controlSettings
        mModules = mPuppet.atUtils('modules_getHeirarchal')
        
        log.info(log_msg("MasterSettings: {}".format(mMasterSettings)))
        
        
        
        for mModule in mModules:
            log.info(log_sub(mModule))
            _type = mModule.moduleType
            mRigNull = mModule.rigNull
            
            mSettings = mRigNull.getMessageAsMeta('settings')
            if mSettings:
                log.info(log_msg('Settings: {}'.format(mSettings)))
                
                mMasterGroup = mSettings.masterGroup

                                
                if test == 1:
                    mProxyCtrl = settings_createRootHolder(mSettings)
                    mProxyCtrl.p_parent = mMasterSettings
                else:
                    if 'cog' in mSettings.p_nameBase:
                        continue
                    if _type in ['eye']:
                        continue
                    
                    mMasterGroup.dagLock(0)
                    mMasterGroup.p_parent = False
                    
    log.info(log_msg("Test: {}".format(test)))
    
    return
    
    
    for mObj in cgmMeta.asMeta(mc.ls('*_settings_anim')):
        mRigNull = mObj.getMessageAsMeta('cgmOwner')
        if mRigNull:
            mRoot = mRigNull.getMessageAsMeta('rigRoot')
            if mRoot:
                mParent = mObj.getParent(asMeta=1)
                mParent.dagLock(0)
                mParent.p_parent = mRoot.dynParentGroup.p_parent    
    

#
def gather_worldStuff(groupTo = 'worldStuff',parent=True):
    ml = []
    for mObj in cgmMeta.asMeta(mc.ls('|*', type = 'transform')):
        if mObj.p_nameBase in ['cgmLightGroup','master','main','cgmRigBlocksGroup']:
            continue
        
        _type =  mObj.getMayaType()
        if _type in ['camera']:
            continue
        
        if mObj.isReferenced():
            continue
        
        print mObj
        print _type
        ml.append(mObj)
        
        
    if ml and parent:
        if not mc.objExists(groupTo):
            mGroup = cgmMeta.asMeta(mc.group(em=True))
            mGroup.rename(groupTo)
        else:
            mGroup = cgmMeta.asMeta(groupTo)
            
        for mObj in ml:
            log.info("Parenting to {0} | {1} | {2}".format(groupTo, mObj.p_nameShort, mObj.getMayaType()))
            mObj.p_parent = mGroup
    
    pprint.pprint(ml)
    return ml
        
def layers_getUnused(delete=False):
    ml = []
    for mObj in cgmMeta.asMeta(mc.ls(type = 'displayLayer')):
        if not mc.editDisplayLayerMembers(mObj.mNode, q=True):
            ml.append(mObj)
    
    if delete:
        for mObj in ml:
            if not mObj.isReferenced():
                log.info("Deleting  empty layer {0} ".format(mObj))
                mObj.delete()
        return True
    return ml

def shaders_getUnused(delete=False):
    ml = []
    for _type in ['lambert','blinn','phong','phongE']:
        for mObj in cgmMeta.asMeta(mc.ls(type = _type),noneValid=True) or []:
            if mObj in ml:
                continue
            log.info(cgmGEN.logString_sub("shaders_getUnused", mObj))
            
            if mObj.p_nameBase is '{0}1'.format(_type):
                log.info("default shader {0}".format(mObj))                
                continue
            
            try:
                for o in ATTR.get_driven("{0}.outColor".format(mObj.mNode),getNode=1):
                    if VALID.get_mayaType(o) == 'shadingEngine':
                        l = mc.sets(o, q=True) 
                        if not l:
                            log.info("Unused shader | {0}".format(mObj))
                            ml.append(mObj)
            except Exception,err:
                print err
            #if not mc.editDisplayLayerMembers(mObj.mNode, q=True):
                #ml.append(mObj)
    
    if delete:
        for mObj in ml:
            if not mObj.isReferenced():
                log.info("Deleting  empty layer | {0} ".format(mObj))
                mObj.delete()
        return True
    return ml


def refs_remove():
    for refFile in mc.file(query=True, reference=True):
        log.info("Removing | {0}".format(refFile))
        mc.file( refFile, removeReference=True )

def defJointFix(start='none', addDynJoint = False, skip = ['DEFJOINT']):
    '''
    
    '''
    import cgm.core.rig.constraint_utils as RIGCONSTRAINTS
    mRoot = cgmMeta.validateObjArg(start)
    ml = [mRoot]
        
    #Get our initial list...
    ml_allChildren = mRoot.getAllChildren(asMeta=1,type='joint')
    ml_allChildren.reverse()
        
    for mObj in ml_allChildren:
        _noGo = False
        if skip:
            for a in skip:
                if mObj.p_nameBase.count(a):
                    _noGo = True
                    continue
        
        if _noGo:
            continue
        mChildren = mObj.getChildren(asMeta=1,type='joint')
        if mChildren:
            mDriver = mObj.getConstrainingObjects(asMeta=1)
            if mDriver:
                mDriver = mDriver[0]
                print("Setup: {}".format(mObj.p_nameShort))
                l_constraints = mObj.getConstraintsTo()
                mc.delete(l_constraints)
                
                ml.append(mObj)
                
                #...get the non joint children as well
                mAllChildren = mObj.getChildren(asMeta=1)
                for mChild in mAllChildren:
                    mChild.p_parent = mRoot
                
                #...dup our joint
                mDup = mObj.doDuplicate()
                if '_sknJnt' in mObj.p_nameBase:
                    _baseName = mObj.p_nameBase.replace('_sknJnt','')
                else:
                    _baseName = mObj.p_nameBase
                    
                mDup.rename('{}_DEFJOINT'.format(_baseName))
                _parentTo = mDup
                
                #DynJoint
                if addDynJoint:
                    mDyn = mObj.doDuplicate()
                    mDyn.rename('{}_DynJoint'.format(_baseName))
                    
                    mDyn.p_parent = mDup
                    _parentTo = mDyn
                
                #...reparent
                for mChild in mAllChildren:
                    mChild.p_parent = _parentTo
                
                mObj.p_parent = _parentTo  
                
                #...reconnect
                RIGCONSTRAINTS.driven_connect(mDup.mNode, mDriver.mNode, 'noScale')
                RIGCONSTRAINTS.driven_connect(mObj.mNode, mDriver.mNode)

        if mObj not in ml:
            print("No setup: {}".format(mObj.p_nameShort))
            
    pprint.pprint(ml)
    print("Setup {} joints".format(len(ml)))
    
    
def dynJoints(start='none'):
    '''
    
    '''
    import cgm.core.rig.constraint_utils as RIGCONSTRAINTS
    mRoot = cgmMeta.validateObjArg(start)
    ml = [mRoot]
        
    #Get our initial list...
    ml_allChildren = mRoot.getAllChildren(asMeta=1,type='joint')
    ml_allChildren.reverse()
    for mObj in ml_allChildren:
        if mObj.p_nameShort.endswith('DEFJOINT'):
            mChildren = mObj.getChildren(asMeta=1,type='joint')
            if mChildren:
                #...get the non joint children as well
                mAllChildren = mObj.getChildren(asMeta=1)
                for mChild in mAllChildren:
                    mChild.p_parent = False                
                
                
                mDup = mObj.doDuplicate()
                mDup.rename('{}_DYN'.format(mObj.p_nameBase))
                mDup.p_parent = mObj
                
                mc.delete(mDup.getConstraintsTo())
                for a in ['tx','ty','tz','rx','ry','rz']:
                    ATTR.break_connection(mDup.mNode,a)
                
                #...reparent
                for mChild in mAllChildren:
                    mChild.p_parent = mDup
                
    
            if mObj not in ml:
                print("No setup: {}".format(mObj.p_nameShort))
            
    pprint.pprint(ml)
    print("Setup {} joints".format(len(ml)))
    
    
def setup_shapes(d_shapes = {}):
    _str_func = 'setup_shapes'
    log.info(log_start(_str_func))
    pprint.pprint(d_shapes)
    
    l_missing = []
    
    def process_obj(target, d):
        mObj = cgmMeta.validateObjArg(target,noneValid=True)
        if not mObj:
            l_missing.append("Obj: {}".format(target))
            return
        
        mExisting = mObj.getShapes(asMeta=1)[0]
        
        mTarget = cgmMeta.asMeta( CURVES.create_fromName(d.get('shape'),d.get('size')))
        mTarget.doSnapTo(mObj)
        
        _moveOffsetAim = d.get('moveOffsetAim')
        mTarget.p_parent = mObj
        mTarget.resetAttrs(['tx','ty','tz','rx','ry','rz'])
        
        if _moveOffsetAim:
            mTarget.tz = _moveOffsetAim
        
        _setAttr = d.get('setAttr',{})
        if _setAttr:
            for a,v in _setAttr.iteritems():
                print("{}|{}".format(a,v))
                mTarget.setMayaAttr(a,v)
        mTarget.p_parent = False
            
        CORERIG.override_color(mTarget.mNode, rgb = mExisting.overrideColorRGB)
        CORERIG.shapeParent_in_place(mObj.mNode,mTarget.mNode,False,True)        
        
        
    for o,d in d_shapes.iteritems():
        log.info("{} | {}".format(o,d))
        if d.get('mirror'):
            for side in ['L','R']:
                o_string = "{}_{}".format(side,o)
                mObj = cgmMeta.validateObjArg(o_string,noneValid=True)
                if not mObj:
                    l_missing.append("Obj: {}".format(o_string))
                    continue
                
                mExisting = mObj.getShapes(asMeta=1)[0]
                
                mTarget = cgmMeta.asMeta( CURVES.create_fromName(d.get('shape'),d.get('size')))
                mTarget.doSnapTo(mObj)
                
                _moveOffsetAim = d.get('moveOffsetAim')
                if _moveOffsetAim:
                    mTarget.p_parent = mObj
                    mTarget.tz = _moveOffsetAim
                    mTarget.p_parent = False
                    
                CORERIG.override_color(mTarget.mNode, rgb = mExisting.overrideColorRGB)
                CORERIG.shapeParent_in_place(mObj.mNode,mTarget.mNode,False,True)
        else:
            process_obj(o,d)
            """
            mObj = cgmMeta.validateObjArg(o_string,noneValid=True)
            if not mObj:
                l_missing.append("Obj: {}".format(o_string))
                continue
            
            mExisting = mObj.getShapes(asMeta=1)[0]
            
            mTarget = cgmMeta.asMeta( CURVES.create_fromName(d.get('shape'),d.get('size')))
            mTarget.doSnapTo(mObj)
            
            _moveOffsetAim = d.get('moveOffsetAim')
            if _moveOffsetAim:
                mTarget.p_parent = mObj
                mTarget.tz = _moveOffsetAim
                mTarget.p_parent = False
                
                
                
            CORERIG.override_color(mTarget.mNode, rgb = mExisting.overrideColorRGB)
            CORERIG.shapeParent_in_place(mObj.mNode,mTarget.mNode,False,True)"""
            

    if l_missing:
        print(cgmGEN._str_hardBreak)
        print("Missing the following controls: ")
        for o in l_missing:
            print(o)
            
    print(log_msg(_str_func,cgmGEN._str_hardBreak))
    
def setup_defaults(d_defaults = {}):
    _str_func = 'setup_defaults'
    log.info(log_start(_str_func))
    pprint.pprint(d_defaults)
    l_missing = []
    for o,d in d_defaults.iteritems():
        try:
            mObj = cgmMeta.validateObjArg(o,noneValid=True)
            if not mObj:
                l_missing.append("Control: {}".format(o))
                continue
            
            for a,v in d.iteritems():
                if not mObj.hasAttr(a):
                    l_missing.append("Attribute: {}".format(a))
                    continue
                if a == 'rotateOrder':
                    if VALID.valueArg(v):
                        _v = CORESHARE._d_rotateOrder_from_index(v)
                    else:_v = v
                    mc.xform(o,rotateOrder=_v,p=True)
                    
                    if mObj.hasAttr('defaultValues'):
                        _d = mObj.defaultValues
                        _dNew = {}
                        for a2 in 'XYZ':
                            _dNew['rotate{}'.format(a2)] = mObj.getMayaAttr('rotate{}'.format(a2))
                        _d.update(_dNew)
                        mObj.defaultValues = _d
                    
                try:ATTR.set_default(o,a,v)
                except Exception,err:log.error(err)
                ATTR.set(o,a,v)
        except Exception,err:
            pprint.pprint(vars())
            raise Exception,err
    if l_missing:
        print(cgmGEN._str_hardBreak)
        print("Missing the following controls: ")
        for o in l_missing:
            print(o)
    print(log_msg(_str_func,cgmGEN._str_hardBreak))
    
def setup_limits(d_limits = {}):
    _str_func = 'setup_limits'
    log.info(log_start(_str_func))    
    pprint.pprint(d_limits)
    
    l_missing = []
    for o,d in d_limits.iteritems():
        for side in ['L','R']:
            o_string = "{}_{}".format(side,o)
            mObj = cgmMeta.validateObjArg(o_string,noneValid=True)
            if not mObj:
                l_missing.append("Obj: {}".format(o_string))
                continue
            mc.transformLimits(o_string, **d)
    
    if l_missing:
        print(cgmGEN._str_hardBreak)
        print("Missing the following controls: ")
        for o in l_missing:
            print(o)
    print(log_msg(_str_func,cgmGEN._str_hardBreak))
    