"""
skinDat
Josh Burton 
www.cgmonastery.com

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
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.lib.transform_utils as TRANS
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import distance_utils as DIST

import cgm.core.mrs.RigBlocks as RIGBLOCKS
from cgm.core.classes import GuiFactory as CGMUI
mUI = CGMUI.mUI

from cgm.core import cgm_General as cgmGEN
log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start

__version__ = cgmGEN.__RELEASESTRING
_colorGood = CORESHARE._d_colors_to_RGB['greenWhite']
_colorBad = CORESHARE._d_colors_to_RGB['redWhite']
_l_unknownMask = ['mClassGrp','cgmDirection','baseSizeX','baseSizeZ','mClass']


_l_datLists = ['numSubShapers','rollCount','loftList','nameList']

class BaseDat(CGMDAT.data):
    def startDir_get(self,startDirMode=None):
        if startDirMode == None:
            startDir = CGMDAT.startDir_getBase(self.structureMode)
        else:
            startDir = CGMDAT.startDir_getBase(startDirMode)
        
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
        self.mBlock = False
        
        if mBlock:
            self.mBlock = cgmMeta.asMeta(mBlock)
        if self.mBlock:
            self.get()
        self.structureMode = 'file'
        
    def get(self, mBlock = None, report = False):
        _str_func = 'data.get'
        log.debug(log_start(_str_func))
        
        mBlock = self.mBlock
        self.dat = blockDat_get(mBlock,report)
        
        
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
        
    def create(self, autoPush= True):
        return blockDat_createBlock(self, autoPush=autoPush)
        
def blockDat_createBlock(self, autoPush = True):
    '''
    blockDat self
    '''
    _str_func = 'blockDat_createBlock'        
    log.debug(log_start(_str_func))
    
    if not self.dat:
        raise ValueError,"must have dat"
    
    mDat = copy.deepcopy(self.dat)
    _blockType = mDat['blockType']
    _side = mDat.get('side')
    _nameOriginal = mDat['baseName']
    
    
    _size = mDat['baseDat'].get('baseSize') or mDat.get('baseSize') or "Fail"
    if _size == 'Fail':
        raise ValueError,"No baseSize"
    
    
    _d = {'blockType':_blockType,
          'autoForm':False,
          'side':_side,
          'baseSize':_size,#mDat['baseSize'],
          'blockProfile':mDat.get('blockProfile'),
          'buildProfile':mDat.get('buildProfile'),
          'blockParent': mDat.get('blockParent')}    
    
    
    #...prompt ------------------------------------------------------------------------------------------------------------------------------------------------
    _title = 'New name for block'.format(_blockType)
    result = mc.promptDialog(title=_title,
                             message='Current: {0} | type: {1} | build: {2} | block:{3} '.format(_nameOriginal,_blockType,_d.get('blockProfile'),_d.get('buildProfile')),
                             button=['OK', 'Cancel'],
                             text = _nameOriginal,
                             defaultButton='OK',
                             cancelButton='Cancel',
                             dismissString='Cancel')
    if result == 'OK':
        _v =  mc.promptDialog(query=True, text=True)
        _d['name'] =  _v
        _d['cgmName'] = _v
        mDat['settings']['name']['cgmName'] = _v
        
    else:
        log.error("Creation cancelled")
        return False    
    
    
    pprint.pprint(_d)
    #pprint.pprint(mDat['settings']['name'])
    
    #...Create ------------------------------------------------------------------------------------------------------------------------------------------------
    log.debug("|{}| >> Creating  block. | file: {} ".format(_str_func, self.str_filepath))
    
    mNew = cgmMeta.createMetaNode('cgmRigBlock',
                                  **_d)
    
    
    #mNew.doSnapTo(self.mBlock)
    
    
    #blockDat['ud']['cgmName'] = _v
    
    """
    if _d['blockType'] in ['finger','thumb']:
        log.debug("|{0}| >> Clearing nameList".format(_str_func))
        for a in blockDat['ud'].iteritems():
            if 'nameList' in a:
                blockDat['ud'].remove(a)
        blockDat['ud']['nameList_0'] = _v            
        """
    ###mNew.blockDat = blockDat
    
    for k,l in mDat.get('datLists',{}).iteritems():
        dTmp = {'enum':False}
        if k == 'loftList':
            dTmp['enum']  = BLOCKSHARE._d_attrsTo_make['loftShape']
            dTmp['mode'] = 'enum'
            
        ATTR.datList_connect(mNew.mNode, k,l, **dTmp)  
    

    l_nameList = mNew.datList_get('nameList')
    for i,n in enumerate(l_nameList):
        if _nameOriginal in n:
            l_nameList[i] = n.replace(_nameOriginal,_d['name'])
            
    mNew.datList_connect('nameList',l_nameList)
    pprint.pprint(l_nameList)                
    
    
    blockDat_load(mNew, mDat, redefine=False, autoPush=autoPush)
    #log.debug('here...')
    #blockDat_load(mNew)#...investigate why we need two...
    
    #mNew.p_blockParent = self.p_blockParent
    #self.connectChildNode(mMirror,'blockMirror','blockMirror')#Connect    

    return mNew    
        
    
def blockDat_get(self,report = True):
    _str_func = 'blockDat_get'        
    log.debug(log_start(_str_func))
    
    #First part of block reset to get/load data------------------------------------------------------
    pos = self.p_position
    orient = self.p_orient
    scale = self.blockScale

    try:
        _l_udMask = ['blockDat','attributeAliasList','blockState','mClass','mClassGrp','mNodeID','version']
        _ml_controls = []
        _short = self.p_nameShort
        _blockState_int = self.blockState
        
        _res = {}
        
        _l_ud = self.getAttrs(ud=True)
        
        _gen = {#"name":_short, 
              "blockType":self.blockType,
              "blockState":self.getEnumValueString('blockState'),
              'blockProfile':self.blockProfile,
              "buildProfile":self.getMayaAttr('buildProfile'),
              "shapeProfile":self.getMayaAttr('shapeProfile'),                     
              "baseName":self.getMayaAttr('cgmName'), 
              'position':self.p_position,
              'orient':self.p_orient,
              'scale':self.scale,
              'side': self.getEnumValueString('side') if self.hasAttr('side') else False,
              'blockScale':ATTR.get(_short,'blockScale'),
              'baseSize':self.atUtils('baseSize_get'),
              "version":self.version,
              'baseDat':self.baseDat,
              }
        
        #set prep.... ------------------------------------------------------------------------------    
        self.p_position = 0,0,0
        self.p_orient = 0,0,0
        self.blockScale = 1.0
        #...        
        
        try:_gen['blockParent'] = self.getMessage('blockParent')[0]
        except:_gen['blockParent'] = False
            
        
        for k in _gen.keys():
            try:_l_ud.remove(k)
            except:pass
            
        if self.getMessage('orientHelper'):
            _gen['rootOrientHelper'] = self.orientHelper.rotate    
            
        _res = _gen
            
        #...let's get our datLists -------------------------------------------------------------------------------
        d_dat = {}
        
        for a in _l_datLists:
            if ATTR.datList_exists(_short,a):
                d_dat[a] = ATTR.datList_get(_short,a,enum=True)
                
                for s2 in ATTR.datList_getAttrs(_short,a):
                    try:_l_ud.remove(s2)
                    except:pass
                try:_l_ud.remove(a)
                except:pass
        
        _res['datLists'] = d_dat
        
        
        #_res['general'] = _gen
        #Get attr sets...--------------------------------------------------------------------------
        _d = self.atUtils('uiQuery_getStateAttrDict',0,0)
        
        _short = self.mNode
        
        _dSettings = {}
        
        def getBlockAttr(a,d):
            if a not in _l_ud:
                return
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
        _res['define'] = blockDat_getControlDat(self,'define',report)#self.getBlockDat_formControls()
        
        if _blockState_int >= 1:
            _res['form'] = blockDat_getControlDat(self,'form',report)#self.getBlockDat_formControls()
        
        if _blockState_int >= 2:
            _res['prerig'] = blockDat_getControlDat(self,'prerig',report)#self.getBlockDat_prerigControls()     
        

        if report:
            pprint.pprint(_res)
        
        return _res
    finally:
        #Restore our block...-----------------------------------------------------------------
        self.p_position = pos
        self.p_orient = orient         
        self.blockScale = scale             
        

def blockDat_load(self, blockDat = None,
                  baseDat = True,
                  useMirror = False,
                  move = True, 
                  settingsOnly = False,
                  autoPush = True,
                  currentOnly=False,
                  overrideMode = None,
                  redefine=False):
    """
    redefine - When duplicating, sometimes we need to redfine after data load
    """
    #First part of block reset to get/load data------------------------------------------------------
    #pos = self.p_position
    #orient = self.p_orient
    #scale = self.blockScale
    def reposition(self,blockDat,posBase,orientBase,scaleBase):
        if move:
            self.p_position = blockDat.get('position')
            self.p_orient = blockDat.get('orient')
            
        
        else:
            self.p_position = posBase
            self.p_orient = orientBase            
            #self.blockScale = scaleBase
            
        try:
            self.sy = blockDat['blockScale']
        except:
            self.sy = scaleBase
        """
        if blockDat.get('blockScale'):
            self.blockScale = blockDat['blockScale']
        else:
            self.blockScale = scaleBase"""
        
        pprint.pprint([self.blockScale, blockDat.get('blockScale'), posBase, orientBase, scaleBase])
        
    _short = self.p_nameShort        
    _str_func = 'blockDat_load'
    log.debug(cgmGEN.logString_start(_str_func))
    _d_warnings = {}

    if blockDat is None:
        log.warn("|{0}| >> No blockDat passed. Checking self...".format(_str_func))    
        blockDat = self.blockDat

    if not issubclass(type(blockDat),dict):
        raise ValueError,"|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat) 

    _blockType = blockDat.get('blockType')
    if _blockType != self.blockType:
        raise ValueError,"|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType) 

    self.sy = blockDat['blockScale']
    
    if baseDat:
        self.baseDat = blockDat['baseDat']
    
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
    
    
    log.debug("|{0}| >> Block main controls".format(_str_func)+ '-'*80)
    _pos = blockDat.get('position')
    _orient = blockDat.get('orient')
    _scale = blockDat.get('scale')
    _orientHelper = blockDat.get('rootOrientHelper')
    
    _posBase = self.p_position
    _orientBase= self.p_orient
    _scaleBase = self.blockScale
    
    self.p_position = 0,0,0
    self.p_orient = 0,0,0            
    self.blockScale = 1.0    
    
    if currentOnly:
        log.debug("|{0}| >> Current only mode: {1}".format(_str_func,_current_state))
        _res =  blockDat_load_state(self,_current_state,blockDat)
        reposition(self,blockDat,_posBase,_orientBase,_scaleBase)
        return _res 
        
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

        
    #moving this to later
    #self.p_position = blockDat.get('position')
    #self.p_orient = blockDat.get('orient')
    
    #else:
        #for ii,v in enumerate(_scale):
            #_a = 's'+'xyz'[ii]
            #if not self.isAttrConnected(_a) and not(ATTR.is_locked(_short,a)):
            #setAttr(_short,_a,v)
        
    #>>Define Controls ====================================================================================
    log.debug(cgmGEN.logString_sub(_str_func,'define'))
    
    if redefine:
        self.UTILS.changeState(self,'define',forceNew=True)
        self.UTILS.changeState(self,'define',forceNew=True)            
        _current_state_idx = 0
        _current_state = 'define'
    

    if mMirror == 'cat':
        log.debug("|{0}| >> mMirror define pull...".format(_str_func))            
        self.UTILS.controls_mirror(mMirror,self,define=True)
    else:
        blockDat_load_state(self,'define',blockDat,_d_warnings,overrideMode=overrideMode)
        
    if _target_state == 'define':
        reposition(self, blockDat, _posBase, _orientBase, _scaleBase)
        return log.info( cgmGEN.logString_sub(_str_func,'{} completed at define.'.format(self)) )
    
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
        
    if _target_state == 'form':
        reposition(self, blockDat, _posBase, _orientBase, _scaleBase)
        return log.info( cgmGEN.logString_sub(_str_func,'{} completed at form.'.format(self)) )
        
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
        
    
    #Move setup. Either back to where we were to using blockDat 
    reposition(self,blockDat,_posBase,_orientBase,_scaleBase)
        
             
    if _d_warnings:
        try:
            for k,d in _d_warnings.iteritems():
                for i,w in enumerate(d):
                    if i == 0:log.warning(cgmGEN.logString_sub(_str_func,"{0} | Warnings".format(k)))
                    log.warning(w)
        except:pass
    return
    
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
                
                for ii,v in enumerate(_scaleTempl[i]):
                    _a = 's'+'xyz'[ii]
                    if not mObj.isAttrConnected(_a):
                        ATTR.set(_tmp_short,_a,v)
                    else:
                        log.debug("|{0}| >> connected scale: {1}".format(_str_func,_a))                
                
                            
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
                    

def blockDat_getControlDat(self,mode = 'define',report = True):
    _short = self.p_nameShort        
    _str_func = 'blockDat_getControlDat'
    log.debug("|{0}| >>  ".format(_str_func)+ '='*80)
    log.debug("|{0}| {1}".format(_str_func,self))
    
    _mode_int,_mode_str = BLOCKGEN.validate_stateArg(mode)
    
    _modeToState = {'define':0,
                    'form':1,
                    'prerig':2}
    
    if _mode_str not in _modeToState.keys():
        raise ValueError,"Unknown mode: {0}".format(_mode_str)
    
    _blockState_int = self.blockState
    
    if not _blockState_int >= _modeToState[_mode_str]:
        raise ValueError,'[{0}] not {1} yet. State: {2}'.format(_short,_mode_str,_blockState_int)
        #_ml_formHandles = self.msgList_get('formHandles',asMeta = True)
    
    _d_controls = {'define':False,'form':False,'prerig':False}
    _d_controls[_mode_str] = True
    ml_handles = self.UTILS.controls_get(self, **_d_controls)
    #pprint.pprint(vars())
    
    #if _blockState_int == 2:
    #   for plug in ['m'] 
    
    if not ml_handles:
        log.debug('[{0}] No form or prerig handles found'.format(_short))
        return False

    _ml_controls = ml_handles

    _l_orientHelpers = []
    _l_jointHelpers = []
    _d_orientHelpers = {}
    _d_jointHelpers = {}
    _d_loftCurves = {}
    _d_subShapers = {}
    
    for i,mObj in enumerate(ml_handles):
        _str_short = mObj.mNode
        log.debug("|{0}| >>  {1} | {2}".format(_str_func,i,mObj.mNode))
        if mObj.getMessage('orientHelper'):
            _d_orientHelpers[str(i)] = mObj.orientHelper.rotate

        if mObj.getMessage('jointHelper'):
            _d_jointHelpers[str(i)] = mObj.jointHelper.translate
            
        mLoftCurve = mObj.getMessageAsMeta('loftCurve')
        if mLoftCurve:
            log.debug("|{0}| >>  loftcurve: {1}".format(_str_func,mLoftCurve)+'-'*20)
            if mLoftCurve.v:
                _d = {}
                _rot = mLoftCurve.rotate
                _orient = mLoftCurve.p_orient
                _trans = mLoftCurve.translate
                _scale = mLoftCurve.scale
                _p = mLoftCurve.p_position
                
                _d['bb'] = TRANS.bbSize_get(mLoftCurve.mNode)
                _d['ab'] = DIST.get_axisSize(mLoftCurve.mNode)
                
                if not COREMATH.is_float_equivalent(sum(_rot),0.0):
                    _d['r'] = _rot
                if not COREMATH.is_float_equivalent(COREMATH.multiply(_scale), 1.0):
                    _d['s'] = _scale
                if not COREMATH.is_float_equivalent(sum(_trans),0.0):
                    _d['t'] = _trans
                    
                _d['p'] = _p
                if _d:
                    _d_loftCurves[str(i)] = _d
                    log.debug("|{0}| >>  d: {1}".format(_str_func,_d))
        
        ml_subShapers = mObj.msgList_get('subShapers')
        if ml_subShapers:
            _d = {}
            log.debug("|{0}| >>  subShapers...".format(_str_func))
            _d = {'p':[mObj.p_position for mObj in ml_subShapers],
                  'o':[mObj.p_orient for mObj in ml_subShapers],
                  'r':[mObj.rotate for mObj in ml_subShapers],
                  't':[mObj.translate for mObj in ml_subShapers],
                  's':[mObj.scale for mObj in ml_subShapers],
                  'ab':[DIST.get_axisSize(mObj.mNode) for mObj in ml_subShapers],                             
                  'bb':[TRANS.bbSize_get(mObj.mNode) for mObj in ml_subShapers]}            
            if _d:
                _d_subShapers[str(i)] = _d            
        
        log.debug(cgmGEN._str_subLine)    


        #else:
            #_l_jointHelpers.append(False)
    _d = {'positions':[mObj.p_position for mObj in ml_handles],
          'orients':[mObj.p_orient for mObj in ml_handles],
          'scales':[mObj.scale for mObj in ml_handles],
          'names':[mObj.p_nameBase for mObj in ml_handles],
          'bb':[TRANS.bbSize_get(mObj.mNode) for mObj in ml_handles]}
    
    if _d_orientHelpers:
        _d['orientHelpers'] =_d_jointHelpers
        
    if _d_jointHelpers:
        _d['jointHelpers'] =_d_jointHelpers
        
    if _d_loftCurves:
        _d['loftCurves'] =_d_loftCurves
    
    if _d_subShapers:
        _d['subShapers'] =_d_subShapers
        
    #if self.getMessage('orientHelper'):
    #    _d['rootOrientHelper'] = self.orientHelper.rotate

    if report:cgmGEN.walk_dat(_d,'[{0}] form blockDat'.format(self.p_nameShort))
    return _d


#======================================================================================================================================================
#... UI stuff
#======================================================================================================================================================


d_blockDatOptions = {'General':['move','useMirror','autoPush','currentOnly','redefine']}
l_blockDatOptions = ['General']

d_shapeDat_options = {"form":['formHandles'],
                      "loft":['loftHandles','loftShapes'],
                     }
d_shapeDatShort = {'formHandles':'handles',
                   "loftHandles":'handles',
                   'loftShapes':'shapes'}
d_shapeDatLabels = {'formHandles':{'ann':"Setup expected qss sets", 'label':'form'},
                    'loftHandles':{'ann':"Wire for mirroring", 'label':'loft'},
                    'loftShapes':{'ann':"Connect bind joints to rig joints", 'label':'shapes'},}
__toolname__ ='BlockDat'
_padding = 5

class uiBlockDat(CGMDAT.ui):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = "{}UI".format(__toolname__)
    WINDOW_TITLE = 'BlockDat | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 400,350
    
    _datClass = BlockDat
   
    def uiUpdate_top(self):
        _str_func = 'uiUpdate_top[{0}]'.format(self.__class__.TOOLNAME)
        log.debug("|{0}| >>...".format(_str_func))
        self.uiSection_top.clear()
        
        mc.setParent(self.uiSection_top)
        _inside = self.uiSection_top
        CGMUI.add_Header('Functions')
        mc.button(parent=_inside,
                  l = 'Create',
                  ut = 'cgmUITemplate',
                  c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiDat.create, self._dCB_reg['autoPush'].getValue())),
                  ann = 'Build with MRS')

        #checkboxes frame...------------------------------------------------------------
        self._dCB_reg = {}
        for d in l_blockDatOptions:
            l = d_blockDatOptions[d]
            mUI.MelLabel(_inside, label = '{0}'.format(d.upper()), h = 13, 
                         ut='cgmUIHeaderTemplate',align = 'center')
            #mc.setParent(_inside)
            #cgmUI.add_Header(d)
            for k in l:
                d_dat = d_shapeDatLabels.get(k,{})
                
                _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
                mUI.MelSpacer(_row,w=10)    
                
                mUI.MelLabel(_row, label = '{0}:'.format( d_dat.get('label',k) ))
                _row.setStretchWidget(mUI.MelSeparator(_row))
    
                _plug = 'cgmVar_blockDat_' + k#d_shapeDatShort.get(k,k)
                try:self.__dict__[_plug]
                except:
                    log.debug("{0}:{1}".format(_plug,1))
                    self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 0)
        
                l = k
                _buffer = k#d_shapeDatShort.get(k)
                if _buffer:l = _buffer
                _cb = mUI.MelCheckBox(_row,
                                      #annotation = d_dat.get('ann',k),
                                      value = self.__dict__[_plug].value,
                                      onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                      offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
                self._dCB_reg[k] = _cb
                mUI.MelSpacer(_row,w=10)    
                
                _row.layout()

        
        
        _button = mc.button(parent=_inside,
                            l = 'Load',
                            ut = 'cgmUITemplate',
                            c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_set)),
                            ann = 'Build with MRS')                
        
        
               
    def uiFunc_dat_get(self):
        _str_func = 'uiFunc_dat_get[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _sel = mc.ls(sl=1)
        
        mBlock = BLOCKGEN.block_getFromSelected()
        if not mBlock:
            return log.error("No blocks selected")
        
        
        self.uiDat.mBlock = mBlock
        self.uiDat.get()
        
        self.uiStatus_refresh(string = "Scene: '{}'".format(mBlock.p_nameBase))
        if _sel:mc.select(_sel)        
        
        return
    
    def uiFunc_dat_set(self,mBlocks = None,**kws):
        _str_func = 'uiFunc_dat_set[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))        
        
        if not mBlocks:
            mBlocks = BLOCKGEN.block_getFromSelected(multi=True)
            
        if not mBlocks:
            return log.error("No blocks selected")
        
        if not self.uiDat:
            return log.error("No dat loaded")
            
        
        if not kws:
            kws = {}
            for k,cb in self._dCB_reg.iteritems():
                kws[k] = cb.getValue()
            pprint.pprint(kws)

        
        mc.undoInfo(openChunk=True)

        for mBlock in mBlocks:
            log.info(log_sub(_str_func,mBlock.mNode))
            try:blockDat_load(mBlock, self.uiDat.dat, **kws)
            except Exception,err:
                log.error("{} | err: {}".format(mBlock.mNode, err))
                    
        mc.undoInfo(closeChunk=True)
        
        return    

class ui2(CGMUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = "BlockDatUI"
    WINDOW_TITLE = 'BlockDat | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 300,400
    
    def insert_init(self,*args,**kws):
        self._loadedFile = ""
        self.dat = None
        
    def build_menus(self):
        self.uiMenu_FileMenu = mUI.MelMenu(l='File', pmc = cgmGEN.Callback(self.buildMenu_file))
        self.uiMenu_SetupMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_setup))

    def buildMenu_file(self):
        self.uiMenu_FileMenu.clear()                      

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_actions,self)))

        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Save As",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_save_as_actions,self)))
        
        mUI.MelMenuItem( self.uiMenu_FileMenu, l="Load",)
                        # c = lambda *a:mc.evalDeferred(cgmGEN.Callback(uiFunc_load_actions,self)))
    def buildMenu_setup(self):pass
    
    
    def uiStatus_refresh(self):
        _str_func = 'uiStatus_refresh[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not self.dat:
            self.uiStatus_top(edit=True,bgc = SHARED._d_gui_state_colors.get('warning'),label = 'No Data')
            #self.uiStatus_bottom(edit=True,bgc = SHARED._d_gui_state_colors.get('warning'),label = 'No Data')
            
            self.uiData_base(edit=True,vis=0)
            self.uiData_base.clear()
            
        else:
            self.uiData_base.clear()
            
            _base = self.dat['base']
            _str = "Source: {}".format(_base['source'])
            self.uiStatus_top(edit=True,bgc = SHARED._d_gui_state_colors.get('connected'),label = _str)
            
            self.uiData_base(edit=True,vis=True)
            
            mUI.MelLabel(self.uiData_base, label = "Base", h = 13, 
                         ut='CGMUIHeaderTemplate',align = 'center')
            
            for a in ['type','blockType','shapers','subs']:
                mUI.MelLabel(self.uiData_base, label = "{} : {}".format(a,self.dat['base'].get(a)),
                             bgc = SHARED._d_gui_state_colors.get('help'))                
            
            
            #_str = "blockType: {}".format(_base.get('blockType','No blockType'))
            #self.uiStatus_bottom(edit=True,bgc = SHARED._d_gui_state_colors.get('connected'),label = _str)            
                
    def uiFunc_dat_get(self):
        _str_func = 'uiFunc_dat_get[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        _sel = mc.ls(sl=1)
        
        mBlock = BLOCKGEN.block_getFromSelected()
        if not mBlock:
            return log.error("No blocks selected")
        
        sDat = dat_get(mBlock)
        self.dat = sDat
        
        self.uiStatus_refresh()
        if _sel:mc.select(_sel)
        
    def uiFunc_dat_set(self,mBlocks = None,**kws):
        _str_func = 'uiFunc_dat_set[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))        
        
        if not mBlocks:
            mBlocks = BLOCKGEN.block_getFromSelected(multi=True)
            
        if not mBlocks:
            return log.error("No blocks selected")
        
        if not self.dat:
            return log.error("No dat loaded")
            
        
        if not kws:
            kws = {}
            for k,cb in self._dCB_reg.iteritems():
                kws[k] = cb.getValue()
            
            pprint.pprint(kws)

        mc.undoInfo(openChunk=True)

        
        for mBlock in mBlocks:
            log.info(log_sub(_str_func,mBlock.mNode))
            try:dat_set(mBlock, self.dat, **kws)
            except Exception,err:
                log.error("{} | err: {}".format(mBlock.mNode, err))
                    
        mc.undoInfo(closeChunk=True)
        
        return
        for d in ['form','loft']:
            l = d_shapeDat_options[d]
            mUI.MelLabel(_inside, label = '{0}'.format(d.upper()), h = 13, 
                         ut='CGMUIHeaderTemplate',align = 'center')
            for k in l:
                d_dat = d_shapeDatLabels.get(k,{})
                
        for d,l in MRSBATCH.d_mrsPost_calls.iteritems():
            for k in l:# _l_post_order:
                log.debug("|{0}| >> {1}...".format(_str_func,k)+'-'*20)
                
                #self._dCB_reg[k].getValue():#self.__dict__['cgmVar_mrsPostProcess_{0}'.format(k)].getValue():
                l_join.insert(2,"'{0}' : {1} ,".format(k,int(self._dCB_reg[k].getValue())))        
        
    
    def uiFunc_dat(self,mode='Select Source'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.dat:
            return log.error("No dat loaded selected")
        
        if mode == 'Select Source':
            mc.select(self.dat['base']['source'])
    
    def uiFunc_printDat(self,mode='all'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.dat:
            return log.error("No dat loaded selected")    
        
        sDat = self.dat
        
        print(log_sub(_str_func,mode))
        if mode == 'all':
            pprint.pprint(self.dat)
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        elif mode == 'base':
            pprint.pprint(sDat['base'])
        elif mode == 'settings':
            pprint.pprint(sDat['settings'])
        elif mode == 'formHandles':
            pprint.pprint(sDat['handles']['form'])        
        elif mode == 'loftHandles':
            pprint.pprint(sDat['handles']['loft'])  
        elif mode == 'sub':
            pprint.pprint(sDat['handles']['sub'])
        elif mode == 'subShapes':
            pprint.pprint(sDat['handles']['subShapes'])
        elif mode == 'subRelative':
            pprint.pprint(sDat['handles']['subRelative'])            
            
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        #Declare form frames...------------------------------------------------------
        _MainForm = mUI.MelFormLayout(parent,ut='CGMUITemplate')#mUI.MelColumnLayout(ui_tabs)
        _inside = mUI.MelScrollLayout(_MainForm)

        #SetHeader = CGMUI.add_Header('{0}'.format(_strBlock))
        self.uiStatus_top = mUI.MelButton(_inside,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = SHARED._d_gui_state_colors.get('warning'),
                                         label = 'No Data',
                                         h=20)                
        
        
        
        #mc.setParent(_MainForm)
        """
        self.uiStatus_bottom = mUI.MelButton(_MainForm,
                                             bgc=SHARED._d_gui_state_colors.get('warning'),
                                             #c=lambda *a:self.uiFunc_updateStatus(),
                                             ann="...",
                                             label='...',
                                             h=20)"""
  
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        
    
        
        
                
        #checkboxes frame...------------------------------------------------------------
        self._dCB_reg = {}
        for d in ['form','loft']:
            l = d_shapeDat_options[d]
            mUI.MelLabel(_inside, label = '{0}'.format(d.upper()), h = 13, 
                         ut='CGMUIHeaderTemplate',align = 'center')
            #mc.setParent(_inside)
            #CGMUI.add_Header(d)
            for k in l:
                d_dat = d_shapeDatLabels.get(k,{})
                
                _row = mUI.MelHSingleStretchLayout(_inside,ut='CGMUISubTemplate',padding = 5)
                mUI.MelSpacer(_row,w=10)    
                
                mUI.MelLabel(_row, label = '{0}:'.format( d_dat.get('label',k) ))
                _row.setStretchWidget(mUI.MelSeparator(_row))
    
                _plug = 'cgmVar_shapeDat_' + k#d_shapeDatShort.get(k,k)
                try:self.__dict__[_plug]
                except:
                    log.debug("{0}:{1}".format(_plug,1))
                    self.__dict__[_plug] = cgmMeta.cgmOptionVar(_plug, defaultValue = 1)
        
                l = k
                _buffer = k#d_shapeDatShort.get(k)
                if _buffer:l = _buffer
                _cb = mUI.MelCheckBox(_row,
                                      #annotation = d_dat.get('ann',k),
                                      value = self.__dict__[_plug].value,
                                      onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                                      offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
                self._dCB_reg[k] = _cb
                mUI.MelSpacer(_row,w=10)    
                
                _row.layout()

        
        
        _button = mc.button(parent=_inside,
                            l = 'Load',
                            ut = 'CGMUITemplate',
                            c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_set)),
                            ann = 'Build with MRS')        
        
        #data frame...------------------------------------------------------
        try:self.var_shapeDat_dataFrameCollapse
        except:self.create_guiOptionVar('shapeDat_dataFrameCollapse',defaultValue = 0)
        mVar_frame = self.var_shapeDat_dataFrameCollapse
        
        _frame = mUI.MelFrameLayout(_inside,label = 'Data',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    #ann='Contextual MRS functionality',
                                    useTemplate = 'CGMUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        self.uiFrame_data = mUI.MelColumnLayout(_frame,useTemplate = 'CGMUISubTemplate') 
        
        
        self.uiData_base = mUI.MelColumn(self.uiFrame_data ,useTemplate = 'CGMUISubTemplate',vis=False) 

        mUI.MelLabel(self.uiFrame_data, label = "Select", h = 13, 
                     ut='CGMUIHeaderTemplate',align = 'center')
        
        for util in ['Select Source']:
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_dat,util),
                          ann="...",
                          label=util,
                          ut='CGMUITemplate',
                          h=20)                            
        
        
        
        
        mUI.MelLabel(self.uiFrame_data, label = "PPRINT", h = 13, 
                     ut='CGMUIHeaderTemplate',align = 'center')
        
        for a in ['settings','base','formHandles','loftHandles','sub','subShapes','subRelative','all']:
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_printDat,a),
                          ann="...",
                          label=a,
                          ut='CGMUITemplate',
                          h=20)                    
        

        _row_cgm = CGMUI.add_cgmFooter(_MainForm)            

        #Form Layout--------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_inside,"top",0),
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",0,_row_cgm),
                        #(_button,"bottom",0,_row_cgm),
                        #(self.uiPB_test,"bottom",0,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])    
    

        self.uiFunc_dat_get()
        
       
   




