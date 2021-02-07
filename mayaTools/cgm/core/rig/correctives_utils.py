"""
------------------------------------------
cgm.core.rig.correctives_utils
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
import maya.mel as mel    

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import cgm.core.cgm_General as cgmGEN
#from cgm.core.rigger import ModuleShapeCaster as mShapeCast
#import cgm.core.cgmPy.os_Utils as cgmOS
#import cgm.core.cgmPy.path_Utils as cgmPATH
#import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
#import cgm.core.rig.general_utils as CORERIGGEN
#import cgm.core.lib.math_utils as MATH
#import cgm.core.lib.transform_utils as TRANS
#import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
#import cgm.core.tools.lib.snap_calls as SNAPCALLS
#import cgm.core.classes.NodeFactory as NODEFACTORY
#from cgm.core import cgm_RigMeta as cgmRigMeta
#import cgm.core.lib.list_utils as LISTS
#import cgm.core.lib.nameTools as NAMETOOLS
import cgm.core.lib.locator_utils as LOC
#import cgm.core.rig.create_utils as RIGCREATE
#import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rayCaster as RAYS
##import cgm.core.lib.rigging_utils as CORERIG
#import cgm.core.lib.curve_Utils as CURVES
#import cgm.core.rig.constraint_utils as RIGCONSTRAINT
#import cgm.core.lib.constraint_utils as CONSTRAINT
#import cgm.core.lib.position_utils as POS
#import cgm.core.rig.joint_utils as JOINT
#import cgm.core.lib.search_utils as SEARCH
#import cgm.core.rig.ik_utils as IK
#import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
#import cgm.core.lib.shapeCaster as SHAPECASTER
from cgm.core.cgmPy import validateArgs as VALID
#import cgm.core.cgm_RigMeta as cgmRIGMETA


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
log_start = cgmGEN.logString_start
log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub

class handler(object):
    baseName = None
    mJoint = None
    mReader = None
    mDriven = None
    maxValue = 1
    _plug_reader = None
    
    def __init__(self,
                 joint = None,
                 readerName = 'forward'
                 ):
        _str_func = 'handler.__init__'
        
        log.debug(log_start(_str_func))
        
        _sel = mc.ls(sl=1)
        if _sel:
            if not joint:
                joint = _sel[0]
                
        if readerName and self._plug_reader != readerName:
            log.warn("New reader name!")
            
        if joint:
            self.joint_verify(joint)
            
    def driven_verify(self, obj, attr):
        _str_func = 'handler.driven_verify'
        log.debug(log_start(_str_func))
        
        if mc.objExists('{0}.{1}'.format(obj,attr)):
            mDriven = cgmMeta.cgmAttr(obj,attr)

        else:
            mDriven = cgmMeta.cgmAttr(obj,attr, 'float', minValue=0, maxValue=self.maxValue)
        
        mDriven.p_hidden = False
        
        self.mDriven = mDriven
        return mDriven        
    
    def get_readerString(self, readerName):
        return '{0}Reader'.format(readerName)
        
    def joint_verify(self, joint = None, readerName = None):
        _str_func = 'handler.joint_verify'
        log.debug(log_start(_str_func))
        
        mJoint = cgmMeta.validateObjArg(joint,noneValid=True, mayaType='joint')
        
        if not mJoint:
            raise ValueError,log_msg(_str_func,"Not a valid joint")
        
        self.mJoint = mJoint
        
        if readerName:
            _string = self.get_readerString(readerName)
            mReader = mJoint.getMessageAsMeta(_string)
            if mReader:
                self.mReader = mReader
                self._plug_reader = _string
        
        
        return mJoint
    
    def report(self):
        _str_func = 'handler.report'
        log.debug(log_start(_str_func))
        
        pprint.pprint ({'mJoint':self.mJoint,
                        'mReader':self.mReader,
                        'mDriven':self.mDriven})
    
        
    def reader_verify(self, readerName= 'forward',
                      parent = False):
        _str_func = 'handler.reader_verify'
        log.debug(log_start(_str_func))
        
        _plug_reader = '{0}Reader'.format(readerName)
        mJoint = self.mJoint
        
        _nameBase = '{0}_{1}'.format(mJoint.p_nameBase, _plug_reader)
        
        mReader = mJoint.getMessageAsMeta(_plug_reader)
        if not mReader:
            log.debug(log_msg(_str_func,"Making mReader"))
            mReader = mJoint.doDuplicate(po=True,ic=False)
            mReader.p_parent = parent
            mReader.rename(_nameBase)
            mJoint.connectChildNode(mReader,_plug_reader,'source')
        elif parent:
            mReader.p_parent = parent
        
        
        self.mReader = mReader
        return mReader
    
    def reader_set(self):
        _str_func = 'handler.reader_set'
        log.debug(log_start(_str_func))
        
        self.mReader.p_orient = self.mJoint.p_orient
        
        
    def reader_setup(self,mode = 'alignMatrix',
                     drivenBy = 'group'):
        '''
        alignMatrix | r&d by Charles Wardlaw. Just proceduralized CGM pals's work.
        '''
        
        _str_func = 'handler.reader_setup'
        log.debug(log_start(_str_func))
        
        mReader = self.mReader
        mJoint = self.mJoint
        mDriven = self.mDriven
        
        # Vector Products =====================================================
        l_todo = [{'name':'extract_source', 'type':'vectorProduct'},
                  {'name':'extract_reader', 'type':'vectorProduct'},
                  {'name':'vectorProduct', 'type':'vectorProduct'},
                  {'name':'remap', 'type':'remapValue'}]
        md = {}
        
        for d in l_todo:
            _name = d['name']
            _type = d['type']
            
            log.debug(log_sub(_str_func, _name))
            mNode = cgmMeta.cgmNode(nodeType= _type)
            mNode.rename("{0}_{1}".format(mReader.p_nameBase, _name))
            
            md[_name] = mNode
            
            if _name in  ['extract_source','extract_reader']:
                mNode.input1Z = 1
                mNode.input2Z = 1
                mNode.operation = 3 #...vector matrix product
                
                if _name == 'extract_source':
                    mJoint.doConnectOut('worldMatrix[0]', "{0}.matrix".format(mNode.mNode))        
                    mNode.normalizeOutput = 1
                else:
                    mReader.doConnectOut('worldMatrix[0]', "{0}.matrix".format(mNode.mNode))        
                    mNode.normalizeOutput = 1
                    
            elif _name == 'vectorProduct':
                mNode.operation = 1#dot product
                md['extract_source'].doConnectOut('output', "{0}.input1".format(mNode.mNode))    
                md['extract_reader'].doConnectOut('output', "{0}.input2".format(mNode.mNode))    
                
            else:
                md['vectorProduct'].doConnectOut('outputX', "{0}.inputValue".format(mNode.mNode))    
            
        if self.mDriven:
            mDriven.doConnectIn("{0}.outValue".format(md['remap'].mNode))        
        
        
d_layouts = {'upDown':{'names':['up','dn'],
                       'directions':['y+','y-'],
                       'offset':-.3,},
             'outs':{'names':['out','in'],
                       'directions':['x+','x-'],
                       'offset':-.3,}             
             }


def layout_getPoints(dag = None,
                     #axisAim = 'z+',
                     #axisUp = 'y+',
                     castMesh = None,
                     orient = 'zyx',
                     layout = 'upDown',
                     offset = -.3,
                     loc = False,
                     name = 'posX'):
    _str_func = 'layout_getPoints'
    log.debug(log_start(_str_func))
    
    _d = d_layouts.get(layout)
    if not _d:
        raise ValueError,log_msg(_str_func,"Unknown layout: {0}".format(layout))
    mDag= cgmMeta.validateObjArg(dag,default_mType='cgmObject')
    
    _mode = _d.get('mode','default')
    _res = {}
    if _mode == 'default':
        _names = _d['names']
        _directions = _d['directions']
        _offset = _d.get('offset',offset)
        for i,n in enumerate(_names):
            log.debug(log_sub(_str_func,n))
            
            #pos = RAYS.get_cast_pos(mDag.mNode,_directions[i],shapes = castMesh)
            #_res[n] = pos
            
            
            _cast = RAYS.cast(mesh = castMesh, obj = mDag.mNode, axis = _directions[i],
                              maxDistance = 10000, firstHit = True,
                              offsetMode = 'normal', offsetDistance = _offset,
                              locDat=0)           
            pprint.pprint(_cast)
            _res[n] = _cast['near']
            
        
    else:
        raise ValueError,log_msg(_str_func,"Unknown mode: {0}".format(_mode))
        
    pprint.pprint(_res)
    
    if loc:
        for n,p in _res.iteritems():
            LOC.create(position=p,name='{0}_loc'.format(n))
    
    return _res

    

def reader_verify(joint = None,
                  #axisAim = 'z+',
                  #axisUp = 'y+',
                  target = None,
                  parent = None,
                  driven = None,
                  name = 'posX'):
    _str_func = 'reader_verify'
    log.debug(log_start(_str_func))
    
    
    mJoint = cgmMeta.validateObjArg(joint,mayaType='joint')
    #mAxis = VALID.simpleAxis(axisAim)
    mTarget = cgmMeta.validateObjArg(target,noneValid=True)
    mDriven = cgmMeta.validateAttrArg(driven)
    
    # Reader ============================================================
    _plug_reader = '{0}Reader'.format(name)
    _nameBase = '{0}_{1}'.format(mJoint.p_nameBase, _plug_reader)
    
    mReader = mJoint.getMessageAsMeta(_plug_reader)
    if not mReader:
        log.debug(log_msg(_str_func,"Making mReader"))
        mReader = mJoint.doDuplicate(po=True,ic=False)
        mReader.p_parent = False
        mReader.rename(_nameBase)
        mJoint.connectChildNode(mReader,_plug_reader,'source')
        
        
    # Vector Products =====================================================
    l_todo = [{'name':'extract_source', 'type':'vectorProduct'},
              {'name':'extract_reader', 'type':'vectorProduct'},
              {'name':'vectorProduct', 'type':'vectorProduct'},
              {'name':'remap', 'type':'remapValue'}]
    md = {}
    
    for d in l_todo:
        _name = d['name']
        _type = d['type']
        
        log.debug(log_sub(_str_func, _name))
        mNode = cgmMeta.cgmNode(nodeType= _type)
        mNode.rename("{0}_{1}".format(_nameBase, _name))
        
        md[_name] = mNode
        
        if _name in  ['extract_source','extract_reader']:
            mNode.input1Z = 1
            mNode.input2Z = 1
            mNode.operation = 3 #...vector matrix product
            
            if _name == 'extract_source':
                mJoint.doConnectOut('worldMatrix[0]', "{0}.matrix".format(mNode.mNode))        
                mNode.normalizeOutput = 1
            else:
                mReader.doConnectOut('worldMatrix[0]', "{0}.matrix".format(mNode.mNode))        
                mNode.normalizeOutput = 1
                
        elif _name == 'vectorProduct':
            mNode.operation = 1#dot product
            md['extract_source'].doConnectOut('output', "{0}.input1".format(mNode.mNode))    
            md['extract_reader'].doConnectOut('output', "{0}.input2".format(mNode.mNode))    
            
        else:
            md['vectorProduct'].doConnectOut('outputX', "{0}.inputValue".format(mNode.mNode))    
        
    if mDriven:
        mDriven['mPlug'].doConnectIn("{0}.outValue".format(md['remap'].mNode))
        
    pprint.pprint(md)
        
        
        
        
        
    
    




d_default = {'twist':{'d':'rz', '+d':10.0, '-d':-10.0, '+':50, '-':-50, 'ease':{0:.25, 1:.5}},
           'side':{'d':'ry', '+d':10.0, '-d':-10.0, '+':25, '-':-25,'ease':{0:.25, 1:.5}},
           'roll':{'d':'rx', '+d':10.0, '-d':-10.0, '+':70, '-':-30,'ease':{0:.25, 1:.5}},}

def SDK_wip(ml = [], matchType = False,
            d_attrs = d_default, skipLever = True, skipFKBase = []):
    _str_func = 'siblingSDK_wip'
    log.info(cgmGEN.logString_start(_str_func))
    
    if not ml:
        ml = cgmMeta.asMeta(sl=1)
    else:
        ml = cgmMeta.asMeta(ml)
    
    #mParent -----------------------------------------------------------------------------
    mParent = ml[0].moduleParent
    mParentSettings = mParent.rigNull.settings
    
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
