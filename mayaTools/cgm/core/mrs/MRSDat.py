"""
skinDat
Josh Burton 
www.cgmonks.com

Core skinning data handler for cgm going forward.

Storing joint positions and vert positions so at some point can implement a method
to apply a skin without a reference object in scene if geo or joint counts don't match

Currently only regular skin clusters are storing...

Features...
- Skin data gather
- Read/write skin data to a readable config file
- Apply skinning data to geo of different vert count
- 

Thanks to Alex Widener for some ideas on how to set things up.

"""
__MAYALOCAL = 'CGMPROJECT'


# From Python =============================================================
import copy
import os
import pprint
import getpass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
#import maya.OpenMaya as OM
#import maya.OpenMayaAnim as OMA

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import Red9.core.Red9_CoreUtils as r9Core

import Red9.packages.configobj as configobj
import Red9.startup.setup as r9Setup    

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_Dat as CGMDAT
from cgm.core.cgmPy import validateArgs as cgmValid
import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.lib.path_utils as COREPATHS
import cgm.core.lib.math_utils as COREMATH
import cgm.core.lib.string_utils as CORESTRINGS
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.tools.lib.project_utils as PU
import cgm.core.lib.mayaSettings_utils as MAYASET
import cgm.core.mrs.lib.scene_utils as SCENEUTILS
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.mrs.lib import general_utils as BLOCKGEN

mUI = cgmUI.mUI

from cgm.core import cgm_General as cgmGEN
log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start

__version__ = cgmGEN.__RELEASESTRING
_colorGood = CORESHARE._d_colors_to_RGB['greenWhite']
_colorBad = CORESHARE._d_colors_to_RGB['redWhite']
_l_unknownMask = ['mClassGrp','cgmDirection','baseSizeX','baseSizeZ','mClass']

class BaseDat(CGMDAT.data):
    def startDir_get(self):
        _str_func = 'BaseDat.startDir_get'
        log.debug(log_start(_str_func))  
        startDir = CGMDAT.startDir_getBase(self.structureMode)
                
        if len(self._startDir)>1:
            _path = os.path.join(startDir, os.path.join(*self._startDir))                    
        else:
            _path = os.path.join(startDir, self._startDir[0])        
        
        return _path        

class BlockDat(BaseDat):
    _ext = 'cgmBlockDat'
    _startDir = ['cgmDat','mrs']
    
    '''
    Class to handle blockDat data. Replacing existing block dat which storing on the node is not ideal
    '''    
    
    def __init__(self, mBlock = None, filepath = None, **kws):
        """

        """
        _str_func = 'data.__buffer__'
        log.debug(log_start(_str_func))
        
        super(BlockDat, self).__init__(filepath, **kws)
        self.mBlock = cgmMeta.asMeta(mBlock)
        self.structureMode = 'file'
        
    def get(self, mBlock = None):
        _str_func = 'data.get'
        log.debug(log_start(_str_func))
        
        mBlock = self.mBlock
        self.dat = blockDat_get(mBlock)
        
        
    def set(self, mBlock = None, **kws):
        _str_func = 'data.set'
        log.debug(log_start(_str_func))
        
        mBlock = self.mBlock        
        blockDat_load(mBlock, self.dat, **kws)
        
    def load(self):
        _str_func = 'BlockDat.load'        
        log.debug(log_start(_str_func))
        
        if not self.mBlock:
            raise ValueError,"Must have mBlock to save"
        
        startDir = self.startDir_get()
        _path = "{}.{}".format( os.path.normpath(os.path.join(startDir,self.mBlock.p_nameBase)), BlockDat._ext)
        
        if not os.path.exists(_path):
            raise ValueError,"Invalid path: {}".format(_path)
        pprint.pprint(_path)
        
        self.read(_path)
        
        self.set()
        
        return        
        
    def save(self,mode=None):
        _str_func = 'BlockDat.save'        
        log.debug(log_start(_str_func))
        
        if not self.mBlock:
            raise ValueError,"Must have mBlock to save"
        
        startDir = self.startDir_get()
        _path = "{}.{}".format( os.path.normpath(os.path.join(startDir,self.mBlock.p_nameBase)), BlockDat._ext)
        
        pprint.pprint(_path)
        
        self.write(_path)
        
        return
        if not os.path.exists(startDir):
            CGMDAT.CGMOS.mkdir_recursive(startDir)
        
        if not mode:
            pass

def blockDat_get(self,report = True):
    _str_func = 'blockDat_get'        
    log.debug(log_start(_str_func))
    
    
    _l_udMask = ['blockDat','attributeAliasList','blockState','mClass','mClassGrp','mNodeID','version']
    #_ml_controls = self.getControls(True,True)
    _ml_controls = []
    _short = self.p_nameShort
    _blockState_int = self.blockState
    
    #self.baseSize = baseSize_get(self)
    #Trying to keep un assertable data out that won't match between two otherwise matching RigBlocks
    _res = {}
    
    _l_ud = self.getAttrs(ud=True)
    
    _gen = {#"name":_short, 
          "blockType":self.blockType,
          "blockState":self.getEnumValueString('blockState'),
          "baseName":self.getMayaAttr('cgmName'), 
          'position':self.p_position,
          'baseSize':self.getState(False),
          'orient':self.p_orient,
          'scale':self.scale,
          'blockScale':ATTR.get(_short,'blockScale'),
          'baseSize':self.atUtils('baseSize_get'),
          "version":self.version,
          }   
    
    for k in _gen.keys():
        try:_l_ud.remove(k)
        except:pass
        
    if self.getMessage('orientHelper'):
        _gen['rootOrientHelper'] = self.orientHelper.rotate    
    
    #_res['general'] = _gen
    _res = _gen
    #Get attr sets...--------------------------------------------------------------------------
    _d = self.atUtils('uiQuery_getStateAttrDict',0,0)
    
    _short = self.mNode
    
    _dSettings = {}
    
    def getBlockAttr(a,d):
        if self.hasAttr(a):
            try:_l_ud.remove(a)
            except:pass            
            _type = ATTR.get_type(_short,a)
            if _type in ['message']:
                return
            elif _type == 'enum':
                d[a] = ATTR.get_enumValueString(_short,a)                    
            else:
                d[a] = ATTR.get(_short,a)            
    
    for k,l in _d.iteritems():
        _dTmp = {}
        for a in l:
            getBlockAttr(a,_dTmp)             

        if _dTmp:
            _dSettings[k] = _dTmp
        
    d_unkown = {}
    for a in _l_ud:
        if a in _l_unknownMask:
            continue
        getBlockAttr(a,d_unkown)             
        
    if d_unkown:
        _dSettings['unknown'] = d_unkown
    _res['settings'] = _dSettings
    
    
    #...control data
    _res['define'] = self.atUtils('blockDat_getControlDat','define',report)#self.getBlockDat_formControls()
    
    if _blockState_int >= 1:
        _res['form'] = self.atUtils('blockDat_getControlDat','form',report)#self.getBlockDat_formControls()

    if _blockState_int >= 2:
        _res['prerig'] = self.atUtils('blockDat_getControlDat','prerig',report)#self.getBlockDat_prerigControls()     
    
    
    if report:
        pprint.pprint(_res)
    return _res


def blockDat_load(self, blockDat = None,
                  useMirror = False,
                  settingsOnly = False,
                  autoPush = True,
                  currentOnly=False,
                  overrideMode = None,
                  redefine=False):
    """
    redefine - When duplicating, sometimes we need to redfine after data load
    """
    try:
        _short = self.p_nameShort        
        _str_func = 'blockDat_load'
        log.debug(cgmGEN.logString_start(_str_func))
        _d_warnings = {}
    
        if blockDat is None:
            log.debug("|{0}| >> No blockDat passed. Checking self...".format(_str_func))    
            blockDat = self.blockDat
    
        if not issubclass(type(blockDat),dict):
            raise ValueError,"|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat) 
    
        _blockType = blockDat.get('blockType')
        if _blockType != self.blockType:
            raise ValueError,"|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType) 
    
        self.blockScale = blockDat['blockScale']
        
        #.>>>..Settings ====================================================================================
        log.debug("|{0}| >> Settings...".format(_str_func)+ '-'*80)
        _settings = blockDat.get('settings')
        _udFail = {}
        
        if not _settings:
            raise ValueError,"|{0}| >> No settings data found".format(_str_func)
        
        for k,d in _settings.iteritems():
            log.info(log_sub(_str_func,k))
            for a,v in d.iteritems():
                _current = ATTR.get(_short,a)
                if _current != v:
                    try:
                        if ATTR.get_type(_short,a) in ['message']:
                            log.debug("|{0}| >> settings '{1}' skipped. Not loading message data".format(_str_func,a))                     
                        else:
                            log.debug("|{0}| >> settings '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                            ATTR.set(_short,a,v)
                    except Exception,err:
                        _udFail[a] = v
                        log.error("|{0}| >> settings '{1}' failed to change. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                        #r9Meta.printMetaCacheRegistry()                
                        for arg in err.args:
                            log.error(arg)                      
    
        if _udFail:
            log.warning(cgmGEN.logString_sub(_str_func,'Settings Fails'))
            pprint.pprint(_udFail)
            
        if settingsOnly:
            log.warning(cgmGEN.logString_msg(_str_func,'settings only'))
            return
        
        #>>State ====================================================================================
        log.debug("|{0}| >> State".format(_str_func) + '-'*80)
        _stateArgs = BLOCKGEN.validate_stateArg(blockDat.get('blockState'))
        _target_state_idx = _stateArgs[0]
        _target_state = _stateArgs[1]
        
        _current_state = self.getState()
        _onlyState = False
        _current_state_idx = self.getState(False)
        
        if currentOnly:
            log.debug("|{0}| >> Current only mode: {1}".format(_str_func,_current_state))
            return blockDat_load_state(self,_current_state,blockDat)

            
        elif _target_state != _current_state:
            log.debug("|{0}| >> States don't match. self: {1} | blockDat: {2}".format(_str_func,_current_state,_target_state)) 
            #self.p_blockState = _state
            
        mMirror = False
        if useMirror:
            if self.getMessage('blockMirror'):
                mMirror = self.blockMirror
            log.debug("|{0}| >> UseMirror. BlockMirror Found: {1}".format(_str_func,mMirror))
            
    
        #>>Controls ====================================================================================
        def setAttr(node,attr,value):
            try:ATTR.set(node,attr,value)
            except Exception,err:
                log.warning("|{0}| >> Failed to set: {1} | attr:{2} | value:{3} | err: {4}".format(_str_func,
                                                                                                   node,
                                                                                                   attr,value))
        log.debug("|{0}| >> Block main controls".format(_str_func)+ '-'*80)
        _pos = blockDat.get('position')
        _orients = blockDat.get('orient')
        _scale = blockDat.get('scale')
        _orientHelper = blockDat.get('rootOrientHelper')
        
        self.p_position = blockDat.get('position')
        self.p_orient = blockDat.get('orient')
        
        #else:
            #for ii,v in enumerate(_scale):
                #_a = 's'+'xyz'[ii]
                #if not self.isAttrConnected(_a) and not(ATTR.is_locked(_short,a)):
                #setAttr(_short,_a,v)
            
        #>>Define Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'define'))
        
        if redefine:
            changeState(self,'define',forceNew=True)
            changeState(self,'define',forceNew=True)            
            _current_state_idx = 0
            _current_state = 'define'
        
        if blockDat.get('blockScale'):
            self.blockScale = blockDat['blockScale']
            
            
        if mMirror == 'cat':
            log.debug("|{0}| >> mMirror define pull...".format(_str_func))            
            controls_mirror(mMirror,self,define=True)
        else:
            blockDat_load_state(self,'define',blockDat,_d_warnings,overrideMode=overrideMode)
        
        #>>Form Controls ====================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'form'))
        
        if _target_state_idx >= 1:
            log.debug("|{0}| >> form dat....".format(_str_func))
            if autoPush:
                if _current_state_idx < 1:
                    log.debug("|{0}| >> Pushing to form....".format(_str_func))
                    self.p_blockState = 1
            else:
                return log.warning(cgmGEN.logString_msg(_str_func,"Autopush off. Can't go to: {0}".format(_target_state)))
            
            log.debug(cgmGEN.logString_msg(_str_func,'form push'))
            
        if mMirror:
            log.debug("|{0}| >> mMirror form pull...".format(_str_func))            
            self.UTILS.controls_mirror(mMirror,self,form=True,prerig=False)
        
        else:
            if _orientHelper:
                mOrientHelper = self.getMessageAsMeta('orientHelper')
                if mOrientHelper:
                    _ctrl = mOrientHelper.mNode
                    for ii,v in enumerate(_orientHelper):
                        _a = 'r'+'xyz'[ii]
                        setAttr(_ctrl,_a,v)
                else:
                    _d_warnings['form']=["Missing orient Helper. Data found."]
                
            blockDat_load_state(self,'form',blockDat,_d_warnings,overrideMode=overrideMode)
           
        #Prerig ==============================================================================================
        log.debug(cgmGEN.logString_sub(_str_func,'prerig'))
        
        if _target_state_idx >= 2:
            log.debug("|{0}| >> prerig dat....".format(_str_func))
            if _current_state_idx < 2:
                if not autoPush:
                    return log.warning(cgmGEN.logString_msg(_str_func,"Autopush off. Can't go to: {1}".format(_target_state)))
                else:
                    log.debug("|{0}| >> Pushing to prerig....".format(_str_func))
                    self.p_blockState = 2

        if mMirror:
            log.debug("|{0}| >> mMirror prerig pull...".format(_str_func))            
            self.UTILS.controls_mirror(mMirror,self,form=False,prerig=True)
        else:
            blockDat_load_state(self,'prerig',blockDat,_d_warnings,overrideMode,overrideMode)
            
        if _d_warnings:
            try:
                for k,d in _d_warnings.iteritems():
                    for i,w in enumerate(d):
                        if i == 0:log.warning(cgmGEN.logString_sub(_str_func,"{0} | Warnings".format(k)))
                        log.warning(w)
            except:pass
        return

    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def blockDat_load_state(self,state = None,
                        blockDat = None,
                        d_warnings = None,
                        overrideMode = None,
                        mainHandleNormalizeScale = False):
    _str_func = 'blockDat_load_state'
    log.debug(cgmGEN.logString_start(_str_func))
    
    _noScale = False
    _scaleMode = None
        
    if overrideMode:
        if overrideMode == 'update':
            if state not in ['form',1]:
                _noScale = True
                mainHandleNormalizeScale = False
            else:
                mainHandleNormalizeScale = True
                _scaleMode = 'bb'
        elif overrideMode == 'useLoft':
            if state in ['form',1]:
                _scaleMode = 'useLoft'
                
    if state  in ['prerig', 2]:
        _noScale = True
    
    #pprint.pprint([mainHandleNormalizeScale,_noScale,_scaleMode])    
    
    if not blockDat:
        log.debug(cgmGEN.logString_msg(_str_func,"No blockDat, using self"))
        blockDat = self.blockDat

    d_state = blockDat.get(state,False)
    if not d_state:
        log.error(cgmGEN.logString_msg(_str_func,"No {0} data found in blockDat".format(state)))
        return False
    
    ml_handles = self.atUtils('controls_get',**{state:True})
    
    if d_warnings:
        if not d_warnings.get(state):
            d_warnings[state] =  []
        _l_warnings = d_warnings[state]
    else:
        _l_warnings = []

    if not ml_handles:
        log.error("|{0}| >> No {1} handles found".format(_str_func,state))
    else:
        log.debug(cgmGEN.logString_sub(_str_func,"processing {0}".format(state)))        
        _posTempl = d_state.get('positions')
        _orientsTempl = d_state.get('orients')
        _scaleTempl = d_state.get('scales')
        _bbTempl = d_state.get('bb')
        _jointHelpers = d_state.get('jointHelpers')
        _loftCurves = d_state.get('loftCurves',{})
        _subShapers = d_state.get('subShapers',{})
        _len_posTempl = len(_posTempl)
        _jointHelpersPre = {}
        if state == 'prerig':
            _jointHelpersPre = d_state.get('jointHelpers')
            
        md_match = {}
        for i,mHandle in enumerate(ml_handles):
            md_match[i] = mHandle
            
        if len(ml_handles) > _len_posTempl:
            msg = "|{0}| >> {3} handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}. Attempting to match".format(_str_func,len( ml_handles),_len_posTempl,state)
            log.warning(msg)
            
            _names = d_state['names']
            for i,name in enumerate(_names):
                for mHandle in ml_handles:
                    if mHandle.p_nameShort == name:
                        md_match[i] = mHandle
                if not md_match.get(i):
                    log.warning(cgmGEN.logString_msg(_str_func, "Couldn't find: {0} | {1}".format(i,name)))
                    
                                            
            
            """
            msg = "|{0}| >> {3} handle dat doesn't match. Cannot load. self: {1} | blockDat: {2}".format(_str_func,len( ml_handles),_len_posTempl,state)
            if d_warnings:
                _l_warnings.append(msg)
            else:
                log.warning(msg)"""
            
        #pprint.pprint(md_match)
        
        for i_loop in range(3):
            log.debug(cgmGEN.logString_sub(_str_func,"Loop: {0}".format(i_loop)))
            for i,mObj in md_match.iteritems():
                if not i_loop:log.info(cgmGEN.logString_msg(_str_func,"Handle: {0}".format(mObj)))
                
                _handleType = mObj.getMayaAttr('handleType')
                if _handleType == 'vector':
                    try:
                        mObj.p_orient = _orientsTempl[i]
                        continue
                    except Exception,err:
                        _l_warnings.append('{0}...'.format(mObj.p_nameShort))
                        _l_warnings.append('Couldnt set vector handle orient | {0}'.format(err))
                
                if i > _len_posTempl-1:
                    _l_warnings.append("No data for: {0}".format(mObj))
                    continue
                
                mObj.p_position = _posTempl[i]
                if not ATTR.is_locked(mObj.mNode,'rotate'):
                    mObj.p_orient = _orientsTempl[i]
                    
                _tmp_short = mObj.mNode
                _d_loft = _loftCurves.get(str(i))
                
                if _noScale != True:
                    _cgmType = mObj.getMayaAttr('cgmType')
                    if _scaleMode == 'useLoft' and  _cgmType in ['blockHandle','formHandle']:
                        _bb = _d_loft.get('bb')
                        _size = MATH.average(_bb) * .75
                        #_size = DIST.get_arcLen(mObj.getMessage('loftCurve')[0]) / 2.0
                        #DIST.scale_to_axisSize(_tmp_short,[_bb[0],_bb[1],_size])
                        mc.scale(_size,_size,_size, _tmp_short, absolute = True)
                        
                    elif mainHandleNormalizeScale and _cgmType in ['blockHandle','formHandle']:
                        _average = MATH.average(_bbTempl[i])
                        mc.scale(_average,_average,_average, _tmp_short, absolute = True)
                        
                        #TRANS.scale_to_boundingBox(_tmp_short,[_bbTempl[i][0],
                        #                                       _average,
                        #                                       _bbTempl[i][2]],freeze=False)
                    else:
                        _noBB = False
                        _normalizeUp = False
                        if _cgmType in ['pivotHelper']:
                            if  mObj.getMayaAttr('cgmName') not in ['base','top']:
                                _noBB = True
                            else:
                                _normalizeUp = True
                                
                        if _scaleMode == 'bb' and _noBB != True:
                            TRANS.scale_to_boundingBox_relative(_tmp_short,_bbTempl[i],freeze=False)
                        else:
                            for ii,v in enumerate(_scaleTempl[i]):
                                _a = 's'+'xyz'[ii]
                                if not mObj.isAttrConnected(_a):
                                    ATTR.set(_tmp_short,_a,v)
                                else:
                                    log.debug("|{0}| >> connected scale: {1}".format(_str_func,_a))
                        if _normalizeUp:
                            mObj.sy = 1
                            
                #Secondary stuff
                if _jointHelpers and _jointHelpers.get(i):
                    mObj.jointHelper.translate = _jointHelpers[i]
                
                if _d_loft:
                    if i_loop:
                        log.debug("|{0}| >> _d_loft: {1}".format(_str_func,_d_loft))
                    
                        mLoftCurve = mObj.getMessageAsMeta('loftCurve')
                        if mLoftCurve:
                            _rot = _d_loft.get('r')
                            _s = _d_loft.get('s')
                            _t = _d_loft.get('t')
                            _bb = _d_loft.get('bb')
                            _ab = _d_loft.get('ab')
                            _p = _d_loft.get('p')
                            if _rot:
                                ATTR.set(mLoftCurve.mNode,'rotate',_rot)
                                
                            if _noScale != True:
                                if _s != None:
                                    if _scaleMode in ['bb','useLoft']:
                                        try:DIST.scale_to_axisSize(mLoftCurve.mNode,_ab,skip=2)
                                        except Exception,err:
                                            log.error(err)
                                            TRANS.scale_to_boundingBox_relative(mLoftCurve.mNode,_bb,freeze=False)
                                    else:
                                        ATTR.set(mLoftCurve.mNode,'scale',_s)
                                    
                            if _p:
                                mLoftCurve.p_position = _p
                            #if _t:
                                #ATTR.set(mLoftCurve.mNode,'translate',_t)
                            
                if _jointHelpersPre and _jointHelpersPre.get(i):
                    mObj.jointHelper.translate = _jointHelpersPre[i]                    
                        
            for i,d_sub in _subShapers.iteritems():
                try:
                    ml_subs = ml_handles[int(i)].msgList_get('subShapers')
                    log.debug ("|{0}| >> subShapers: {1}".format(_str_func,i))
                    if not ml_subs:
                        raise ValueError,"Failed to find subShaper: {0} | {1}".format(i,d_sub)
                    _t = d_sub.get('t')
                    _r = d_sub.get('r')
                    _s = d_sub.get('s')
                    _p = d_sub.get('p')
                    _bb = d_sub.get('bb')
                    _ab = d_sub.get('ab')
                    
                    _len_p = len(_p)
                    for ii,mObj in enumerate(ml_subs):
                        if ii > _len_p-1:
                            _l_warnings.append("No data for sub {0} on {1}".format(ii,mObj))
                            #mObj.p_position = _p[ii-1]
                            #ATTR.set(mObj.mNode,'t',_t[ii])
                            ATTR.set(mObj.mNode,'r',_r[ii-1])
                            
                            if _noScale != True:
                                if _scaleMode in ['bb','useLoft']:
                                    try:DIST.scale_to_axisSize(mObj.mNode,_ab[ii-1],skip=2)
                                    except Exception,err:
                                        log.error(err)                                
                                        TRANS.scale_to_boundingBox_relative(mObj.mNode,_bb[ii-1],freeze=False)
                                else:
                                    ATTR.set(mObj.mNode,'s',_s[ii-1])
                            
                            continue                            
                        mObj.p_position = _p[ii]
                        #ATTR.set(mObj.mNode,'t',_t[ii])
                        ATTR.set(mObj.mNode,'r',_r[ii])
                        
                        if _noScale != True:
                            if _scaleMode in ['bb','useLoft']:
                                try:DIST.scale_to_axisSize(mObj.mNode,_ab[ii],skip=2)
                                except Exception,err:
                                    log.error(err)
                                    TRANS.scale_to_boundingBox_relative(mObj.mNode,_bb[ii],freeze=False)
                            else:
                                ATTR.set(mObj.mNode,'s',_s[ii])
                except Exception,err:
                    log.error(cgmGEN.logString_msg(_str_func,"subShapers: {0} | {1}".format(i,err)))
                    pprint.pprint(d_sub)