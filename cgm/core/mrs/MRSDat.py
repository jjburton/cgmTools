"""
MRSDat
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
__MAYALOCAL = 'MRSDAT'


# From Python =============================================================
import copy
import os
import pprint
import getpass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

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
#from cgm.core.mrs import ShapeDat as SHAPEDAT
import cgm.core.mrs.RigBlocks as RIGBLOCKS
from cgm.core.classes import GuiFactory as CGMUI
mUI = CGMUI.mUI
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.search_utils as CORESEARCH

import cgm.core.lib.position_utils as POS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.locator_utils as LOC
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
import cgm.images.icons as cgmIcons
_path_imageFolder = PATHS.Path(cgmIcons.__file__).up().asFriendly()

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
        _str_func = 'BaseDat.startDir_get'
        log.debug(log_msg(_str_func,startDirMode))        
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
    #_dataFormat = 'json'
    
    '''
    Class to handle blockDat data. Replacing existing block dat which storing on the node is not ideal
    '''    
    
    def __init__(self, mBlock = None, filepath = None, dat = None, **kws):
        """

        """
        _str_func = 'data.__buffer__'
        log.debug(log_start(_str_func))
        super(BlockDat, self).__init__(filepath, **kws)
        self.mBlock = False
        self.structureMode = 'file'
        
        if dat:
            self.fillDat(dat)
            """
            self.test = {}
            self.test['test'] = {}
            self.test['test']['test'] = dat
            self.dat = self.test['test']['test'] """
        else:
            if mBlock:
                self.mBlock = cgmMeta.asMeta(mBlock)
            if self.mBlock:
                self.get()
        
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
            raise ValueError("Must have mBlock to save")
        
        startDir = self.startDir_get()
        _path = "{}.{}".format( os.path.normpath(os.path.join(startDir,self.mBlock.p_nameBase)), BlockDat._ext)
        
        if not os.path.exists(_path):
            raise ValueError("Invalid path: {}".format(_path))
        pprint.pprint(_path)
        
        self.read(_path)
        
        self.set()
        
        return        
        
    def write(self,*arg,**kws):
        _str_func = 'BlockDat.write'        
        log.debug(log_start(_str_func))
        
        if not self.mBlock and not self.dat:
            raise ValueError("Must have mBlock to save or dat")
        
        if self.mBlock:
            _name = self.mBlock.p_nameBase
        else:
            _name = self.dat['baseName']
        
        if self.dir_export:
            startDir = self.dir_export
        else:
            startDir = self.startDir_get(kws.get('startDirMode'))
            
        _path = "{}.{}".format( os.path.normpath(os.path.join(startDir,_name)), BlockDat._ext)
        
        pprint.pprint(_path)
        pprint.pprint(kws)
        BaseDat.write(self, filepath = _path, *arg,**kws)
        #self.write(_path)
        
        return

    def create(self, autoPush= True):
        return blockDat_createBlock(self, autoPush=autoPush)
    
    def __repr__(self):
        if self.dat:
            return "({} | {} | {} | {})".format(self.get_string(), self.__class__, self._ext, self._dataFormat)    
        if self.mBlock:
            return "({} | {} | {} | {})".format(self.mBlock.p_nameBase, self.__class__, self._ext, self._dataFormat)    
        return "({} | {} | {})".format(self.__class__, self._ext, self._dataFormat)
    
    
    def get_string(self):
        if not self.dat:
            return False
        return blockDat_getString(self)
        

def blockDat_getString(self):
    mDat = copy.deepcopy(self.dat)
    _blockType = mDat['blockType']
    _side = mDat.get('side')
    _nameOriginal = mDat['baseName']
    _res = [_nameOriginal,_blockType]
    """
    _d = {'blockType':_blockType,
          'autoForm':False,
          'side':_side,
          'baseSize':_size,#mDat['baseSize'],
          'blockProfile':mDat.get('blockProfile'),
          'buildProfile':mDat.get('buildProfile'),
          'blockParent': mDat.get('blockParent')}"""
    if _side not in [False,None,'none']:
        _res.insert(0,_side)
    
    return " | ".join(_res)

    
@cgmGEN.Wrap_exception
def blockDat_createBlock(self, autoPush = True, promptName = True):
    '''
    blockDat self
    '''
    _str_func = 'blockDat_createBlock'        
    log.debug(log_start(_str_func))
    
    if not self.dat:
        raise ValueError("must have dat")
    
    mDat = copy.deepcopy(self.dat)
    _blockType = mDat['blockType']
    _side = mDat.get('side')
    _nameOriginal = mDat['baseName']
    
    
    _size = mDat['baseDat'].get('baseSize') or mDat.get('baseSize') or "Fail"
    if _size == 'Fail':
        raise ValueError("No baseSize")
    
    
    
    
    _d = {'blockType':_blockType,
          'autoForm':False,
          'side':_side,
          'baseSize':_size,#mDat['baseSize'],
          'blockProfile':mDat.get('blockProfile'),
          'buildProfile':mDat.get('buildProfile'),
          'blockParent': CORESEARCH.find_from_string(mDat.get('blockParent'))}    
    
    
    #...prompt ------------------------------------------------------------------------------------------------------------------------------------------------
    if promptName:
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
            
            if mDat.get('blockPosition') and mDat['blockPosition'] != 'none':
                _d['cgmPosition'] = mDat.get('blockPosition')
                    
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
    
    for k,l in list(mDat.get('datLists',{}).items()):
        dTmp = {'enum':False}
        if k == 'loftList':
            dTmp['enum']  = BLOCKSHARE._d_attrsTo_make['loftShape']
            dTmp['mode'] = 'enum'
            
        ATTR.datList_connect(mNew.mNode, k,l, **dTmp)  
    

    l_nameList = mNew.datList_get('nameList')
    for i,n in enumerate(l_nameList):
        if _nameOriginal in n and _d.get('name'):
            l_nameList[i] = n.replace(_nameOriginal,_d['name'])
            
    mNew.datList_connect('nameList',l_nameList)
    pprint.pprint(l_nameList)                
    
    
    blockDat_load(mNew, mDat, redefine=False, autoPush=autoPush)
    #log.debug('here...')
    #blockDat_load(mNew)#...investigate why we need two...
    
    #mNew.p_blockParent = self.p_blockParent
    #self.connectChildNode(mMirror,'blockMirror','blockMirror')#Connect    
    pprint.pprint(_d)

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
                'blockPosition':self.getMayaAttr('position') or self.getMayaAttr('cgmPosition'),
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
        
        try:_gen['lenParents'] = len(self.getBlockParents())
        except:_gen['lenParents'] = 0        
            
        
        for k in list(_gen.keys()):
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
        
        for k,l in list(_d.items()):
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
            _res['shape'] = shapeDat_get(self)
        
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
        
@cgmGEN.Wrap_exception
def blockDat_load(self, blockDat = None,
                  baseDat = True,
                  useMirror = False,
                  move = True, 
                  settingsOnly = False,
                  autoPush = True,
                  currentOnly=False,
                  overrideMode = None,
                  shapeDat = True,
                  redefine=False, **kws):
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
        raise ValueError("|{0}| >> blockDat must be dict. type: {1} | blockDat: {2}".format(_str_func,type(blockDat),blockDat)) 

    _blockType = blockDat.get('blockType')
    if _blockType != self.blockType:
        raise ValueError("|{0}| >> blockTypes don't match. self: {1} | blockDat: {2}".format(_str_func,self.blockType,_blockType)) 

    self.sy = blockDat['blockScale']
    
    if baseDat:
        self.baseDat = blockDat['baseDat']
    
    #.>>>..Settings ====================================================================================
    log.debug("|{0}| >> Settings...".format(_str_func)+ '-'*80)
    _settings = blockDat.get('settings')
    _udFail = {}
    
    if not _settings:
        raise ValueError("|{0}| >> No settings data found".format(_str_func))
    
    for k,d in list(_settings.items()):
        log.info(log_sub(_str_func,k))
        for a,v in list(d.items()):
            _current = ATTR.get(_short,a)
            if _current != v:
                try:
                    if ATTR.get_type(_short,a) in ['message']:
                        log.debug("|{0}| >> settings '{1}' skipped. Not loading message data".format(_str_func,a))                     
                    else:
                        log.debug("|{0}| >> settings '{1}' mismatch. self: {2} | blockDat: {3}".format(_str_func,a,_current,v)) 
                        ATTR.set(_short,a,v)
                except Exception as err:
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
        except Exception as err:
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
    
    if shapeDat and blockDat.get('shape'):
        shapeDat_set(self,blockDat['shape'])
    
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
            for k,d in list(_d_warnings.items()):
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
            for i,mObj in list(md_match.items()):
                if not i_loop:log.info(cgmGEN.logString_msg(_str_func,"Handle: {0}".format(mObj)))
                
                _handleType = mObj.getMayaAttr('handleType')
                if _handleType == 'vector':
                    try:
                        mObj.p_orient = _orientsTempl[i]
                        continue
                    except Exception as err:
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
                                        except Exception as err:
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
                        
            for i,d_sub in list(_subShapers.items()):
                try:
                    ml_subs = ml_handles[int(i)].msgList_get('subShapers')
                    log.debug ("|{0}| >> subShapers: {1}".format(_str_func,i))
                    if not ml_subs:
                        raise ValueError("Failed to find subShaper: {0} | {1}".format(i,d_sub))
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
                                    except Exception as err:
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
                                except Exception as err:
                                    log.error(err)
                                    TRANS.scale_to_boundingBox_relative(mObj.mNode,_bb[ii],freeze=False)
                            else:
                                ATTR.set(mObj.mNode,'s',_s[ii])
                except Exception as err:
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
    
    if _mode_str not in list(_modeToState.keys()):
        raise ValueError("Unknown mode: {0}".format(_mode_str))
    
    _blockState_int = self.blockState
    
    if not _blockState_int >= _modeToState[_mode_str]:
        raise ValueError('[{0}] not {1} yet. State: {2}'.format(_short,_mode_str,_blockState_int))
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
                
                if not MATH.is_float_equivalent(sum(_rot),0.0):
                    _d['r'] = _rot
                if not MATH.is_float_equivalent(MATH.multiply(_scale), 1.0):
                    _d['s'] = _scale
                if not MATH.is_float_equivalent(sum(_trans),0.0):
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
                  'nameTags':[mObj.getMayaAttr('nameTag') or mObj.p_nameBase for mObj in ml_subShapers],                  
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
          'nameTags':[mObj.getMayaAttr('nameTag') or mObj.p_nameBase for mObj in ml_handles],
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




class BlockConfig(BaseDat):
    '''
    Class to handle blockDat data. Replacing existing block dat which storing on the node is not ideal
    '''    
    _ext = 'cgmBlockConfig'
    _startDir = ['cgmDat','mrs']
    _cleanDat = {'blockList':[],
                 'config':{},
                 'uiStrings':[],
                 'indices':[]}
    
    def __init__(self, ml_context = None, filepath = None, **kws):
        """

        """
        _str_func = 'BlockConfig.__buffer__'
        log.debug(log_start(_str_func))
        self.str_filepath = None
        self.dat = {}
        self.mBlockDat = []
                
        super(BlockConfig, self).__init__(filepath, **kws)
        
        

        if not filepath:
            if not ml_context and ml_context is not None:
                ml_context = BLOCKGEN.block_getFromSelected(True)
                if not ml_context:
                    md = BLOCKGEN.get_scene_block_heirarchy()
                    ml_context =  cgmGEN.walk_heirarchy_dict_to_list(md)                
                
            if ml_context:
                self.get(ml_context)
        
    def clear(self):
        _str_func = 'BlockConfig.clear'
        log.debug(log_start(_str_func))
        self.dat = copy.copy(BlockConfig._cleanDat)
        self.mBlockDat = []        
        
    def get(self, ml_context = []):
        _str_func = 'BlockConfig.get'
        log.debug(log_start(_str_func))
        
        self.dat = config_get(ml_context)
        self.mBlockDat = []
        
        for i,block in enumerate(self.dat['blockList']):
            #log.info(block)
            self.mBlockDat.append( BlockDat(dat= self.dat['config'][str(i)] ))
            
    def append(self, ml_context = []):
        _str_func = 'BlockConfig.append'
        log.debug(log_start(_str_func))        
        
        
        if not ml_context and ml_context is not None:
            ml_context = BLOCKGEN.block_getFromSelected(True)
            if not ml_context:
                raise ValueError("{} | Must have a context to append".format(_str_func))
        
        _newDat = config_get(ml_context)
        
        
        _oldIndices = self.dat.get('indices',[])
        if _oldIndices:
            _start = max(_oldIndices) + 1
        else:
            _start = 0
            
        for i,k in enumerate(_newDat['indices']):
            self.dat['blockList'].append(_newDat['blockList'][i])
            self.dat['config'][str(k+_start)] = _newDat['config'][str(k)]
            self.dat['uiStrings'].append(_newDat['uiStrings'][k])
            self.dat['indices'].append(k+_start)


            self.mBlockDat.append( BlockDat(dat= _newDat['config'][str(k)] ))

        return True
        #Get the current open list
        
    def remove(self, idx = None, ml_context = []):
        _str_func = 'BlockConfig.remove'
        log.debug(log_start(_str_func))
        
        if idx is None:
            raise ValueError("{} | Must have an index".format(_str_func))
        

        if idx not in self.dat['indices']:
            raise ValueError("{} | Invalid idx - {} | {}".format(_str_func, idx, self.dat['indices']))
        

        #try:self.mBlockDat.pop(idx)
        #except:
        #    raise ValueError,"{} | Invalid idx - {} | {}".format(_str_func, idx, self.dat['indices'])
        self.mBlockDat = []
        
        _baseDat = copy.deepcopy(self.dat)
        
        _newDat = copy.deepcopy(BlockConfig._cleanDat)
        pprint.pprint(_newDat)
        _i = 0
        
        for i,k in enumerate(_baseDat['indices']):
            if k == idx:
                continue
            
            _newDat['blockList'].append(_baseDat['blockList'][i])
            _newDat['config'][str(_i)] = _baseDat['config'][str(k)]
            _newDat['uiStrings'].append(_baseDat['uiStrings'][i])
            
            self.mBlockDat.append( BlockDat(dat= _baseDat['config'][str(k)] ))
            
            #self.dat['blockList'].append(_newDat['blockList'][i])
            #self.dat['config'][str(k+_start)] = _newDat['config'][str(k)]
            #self.dat['uiStrings'].append(_newDat['uiStrings'][k])
            #self.dat['indices'].append(k+_start)
            _i+=1

        _newDat['indices'] = list(range(len(_newDat['blockList'])))        

        self.dat = _newDat
        return True
        
    def set(self, mBlock = None):
        _str_func = 'BlockConfig.set'
        log.debug(log_start(_str_func))
    

    def read(self, filepath = None, *arg,**kws):
        BaseDat.read(self, filepath, *arg,**kws)
        
        self.mBlockDat = []
        
        for i,block in enumerate(self.dat['blockList']):
            #log.info(block)
            self.mBlockDat.append( BlockDat(dat= self.dat['config'][str(i)] ))
            
        if not self.dat.get('indices'):
            self.dat['indices'] = list(range(len(self.dat['blockList'])))        
        
        #self.str_filepath = filepath
        return True    
        
    
        
        
        
        

def config_get(ml_context = [], report = True):
    _str_func = 'config_get'        
    log.debug(log_start(_str_func))
    
    _sel = mc.ls(sl=1)
    #>> Find our block context -------------------------------------------------------------------
    if not ml_context:
        ml_context = BLOCKGEN.block_getFromSelected(True)
    if not ml_context:
        if _sel:mc.select(_sel)
        return log.error("No blocks selected")        
        #md = BLOCKGEN.get_scene_block_heirarchy()
        #ml_context =  cgmGEN.walk_heirarchy_dict_to_list(md)
        
    if log.level == 10:
        pprint.pprint(ml_context)
        
    _res = {'blockList':[],
            'config':{},
            'uiStrings':[],
            'indices':[]}
    
    ml,strings = BLOCKGEN.get_uiScollList_dat(showState=False,showProfile=False)
    
    d_order = {}
    #...want to get our list in order as we want
    for i,mBlock in enumerate(ml_context):
        _idx = ml.index(mBlock)
        d_order[_idx] = mBlock
        
    _keys = sorted(d_order)
    for i,k in enumerate(_keys):
        _res['blockList'].append(d_order[k].p_nameBase)
        _res['config'][str(i)] = blockDat_get(d_order[k],False)    
        _res['uiStrings'].append(strings[k])
        _res['indices'].append(i)
    
    if log.level == 10:
        pprint.pprint(_res)
    #...
    if _sel:mc.select(_sel)
    
    return _res

def blockConfig_create(self, idx = None, autoPush = True, promptName = False):
    '''
    blockDat self
    '''
    _str_func = 'blockDat_createBlock'        
    log.debug(log_start(_str_func))
    if not self.dat:
        raise ValueError("must have dat")
    mc.select(cl=1)

    if idx is not None:
        return blockDat_createBlock(self.mBlockDat[idx], autoPush, promptName)
        
    ml = []
    for i,block in enumerate(self.dat['blockList']):
        log.debug(cgmGEN.logString_sub(_str_func,block))
        
        ml.append( blockDat_createBlock(self.mBlockDat[i], autoPush, promptName) )
        
    return ml







#======================================================================================================================================================
#... UI stuff
#======================================================================================================================================================


d_blockDatOptions = {'General':['move','useMirror','autoPush','currentOnly','redefine']}
l_blockDatOptions = ['General','form','loft']


d_shapeDat_options = {"form":['formHandles'],
                      "loft":['loftHandles','loftShapes'],
                     }
d_blockDatOptions.update(d_shapeDat_options)

d_shapeDatShort = {'formHandles':'handles',
                   "loftHandles":'handles',
                   'loftShapes':'shapes'}
d_shapeDatLabels = {'formHandles':{'ann':"Setup expected qss sets", 'label':'form'},
                    'loftHandles':{'ann':"Wire for mirroring", 'label':'loft'},
                    'loftShapes':{'ann':"Connect bind joints to rig joints", 'label':'shapes'},}
__toolname__ ='BlockDat'
_padding = 5




def getSubMenu_recursive(key,mDict):
    #https://stackoverflow.com/questions/6004073/how-can-i-create-directories-recursively
    _split = k.split('.')[:-1]
    _keyUse = k.split('.')[-1]    
    sub_path = os.path.dirname(path)
    if not os.path.exists(sub_path):
        mkdir_recursive(sub_path)
        
    if not mDict.get(key):
        _sub = mUI.MelMenuItem( _parent, subMenu=True, l=sub, tearOff=True)
        md_menus[key]  = _sub        
        
class ui(CGMDAT.ui):
    _datTypes = ['cgmBlockConfig']
    
    def insert_init(self, *args, **kws):
        CGMDAT.ui.insert_init(self,*args,**kws)
        
        self.create_guiOptionVar('libraryDirMode',defaultValue = 'dev') 
        
    def build_menus(self):
        self.uiMenu_FileMenu = mUI.MelMenu(l='File', pmc = cgmGEN.Callback(self.buildMenu_file))
        self.uiMenu_library = mUI.MelMenu(l='Library', pmc = cgmGEN.Callback(self.buildMenu_library), pmo=True, tearOff=True)
        self.uiMenu_SetupMenu = mUI.MelMenu(l='Dev', pmc = cgmGEN.Callback(self.buildMenu_dev))
        
    def uiFunc_libraryDirMode(self,v):
        _str_func = 'uiFunc_libraryDirMode[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _path = CGMDAT.startDir_getBase(v)
        if _path:
            self.var_libraryDirMode.setValue(v)
            print(_path)
            self.buildMenu_library(True)#...force
            
    def buildMenu_library( self, force=True, *args, **kws):
        if self.uiMenu_library and force is not True:
            log.debug("No load...")
            return
        
        self.uiMenu_library.clear()
        
        _menu = self.uiMenu_library
        mUI.MelMenuItemDiv(self.uiMenu_library, l="Options")
        
        #Context ...---------------------------------------------------------------------------------
        _starDir = mUI.MelMenuItem(_menu, l="SearchDir",tearOff=True,
                                   subMenu = True)
        
        uiRC = mc.radioMenuItemCollection()
        
        #self._l_contextModes = ['self','below','root','scene']
        _d_ann = {'self':'Context is only of the active/sel block',
                  'below':'Context is active/sel block and below',
                  'root':'Context is active/sel root and below',
                  'scene':'Context is all blocks in the scene. Careful skippy!',}
        
        _on = self.var_libraryDirMode.value
        
        for i,item in enumerate(['workspace','dev']):
            if item == _on:_rb = True
            else:_rb = False
            mUI.MelMenuItem(_starDir,label=item,
                            collection = uiRC,
                            ann = _d_ann.get(item),
                            c = cgmGEN.Callback(self.uiFunc_libraryDirMode,item),                                  
                            rb = _rb)                
        mUI.MelMenuItemDiv(_menu, l="Found")
                
        
        if force:
            path = CGMDAT.startDir_getBase(_on)
            
            #if _on == 'dev':
            path = os.path.join(path, 'cgmDat','mrs')
            get_ext_options(True,path=path)
            
        _options, _categories = get_ext_options(extensions=self._datTypes)
        
        
        md_menus = {}
        for k in _categories.get(self._datTypes[0],[]):
            f = _options.get(k)
            #print("{} | {}".format(k,f))
            _useMenu = self.uiMenu_library
            if '.' in k:
                _split = k.split('.')[:-1]
                _keyUse = k.split('.')[-1]
                #pprint.pprint(_split)
                
                for i,sub in enumerate(_split):
                    _parentKey = '.'.join(_split[:i+1])
                    #print ("parentKey: {}".format(_parentKey))
                    
                    if not i:
                        _parent = self.uiMenu_library
                    if not md_menus.get(_parentKey):
                        _sub = mUI.MelMenuItem( _parent, subMenu=True, l=sub, tearOff=True)
                        md_menus[_parentKey]  = _sub
                    _parent = md_menus[_parentKey] 
                _useMenu = md_menus[_parentKey]                 
            else:
                _keyUse = k
            """
            if '.' in k:
                _split = k.split('.')[:-1]
                _keyUse = k.split('.')[-1]
                for i,sub in enumerate(_split):
                    _splitKey = '.'.join(_split[i:])
                    print _splitKey
                    if not i:
                        _parent = self.uiMenu_library
                    if not md_menus.get(_splitKey):
                        _sub = mUI.MelMenuItem( _parent, subMenu=True, l=sub, tearOff=True)
                        md_menus[_splitKey]  = _sub
                        
                    _parent = md_menus[_splitKey] 
                    _useMenu = md_menus[_splitKey] """
                            
            mUI.MelMenuItem(_useMenu, l=_keyUse,
                            c=cgmGEN.Callback(self.uiFunc_dat_load,**{'filepath':f}),
                            ann="{} | {}".format(_keyUse, f))                


        mUI.MelMenuItemDiv(self.uiMenu_library)
        mUI.MelMenuItem(self.uiMenu_library, l='Rebuild',
                        c=lambda *a: mc.evalDeferred(self.buildMenu_library,lp=True))
        log.info("Library menu rebuilt")
        return
    
    
        _d = copy.copy(self._d_modules)
        for b in _d[1]['blocks']:
            if _d[0][b].__dict__.get('__menuVisible__'):
                mUI.MelMenuItem(self.uiMenu_library, l=b,
                                c=cgmGEN.Callback(self.uiFunc_block_create,b),
                                ann="{0} : {1}".format(b, self.uiFunc_block_create))
                
                l_options = RIGBLOCKS.get_blockProfile_options(b)                
                if l_options:
                    for o in l_options:
                        mUI.MelMenuItem(self.uiMenu_library, l=o,
                                        c=cgmGEN.Callback(self.uiFunc_block_create,b,o),
                                        ann="{0} : {1}".format(b, self.uiFunc_block_create))

        
        for c in list(_d[1].keys()):
            #d_sections[c] = []
            if c == 'blocks':continue
            for b in _d[1][c]:
                if _d[0][b].__dict__.get('__menuVisible__'):
                    #d_sections[c].append( [b,cgmGEN.Callback(self.uiFunc_block_create,b)] )
                    l_options = RIGBLOCKS.get_blockProfile_options(b)
                    if l_options:
                        _sub = mUI.MelMenuItem( self.uiMenu_library, subMenu=True,l=b,tearOff=True)
                        l_options.sort()
                        for o in l_options:
                            _l = "{0}".format(o)
                            _c = cgmGEN.Callback(self.uiFunc_block_create,b,o)
                            mUI.MelMenuItem(_sub, l=_l,
                                            c=_c,
                                            ann="{0} : {1}".format(_l, _c)
                                            )
                    else:
                        mUI.MelMenuItem(self.uiMenu_library, l=b,
                                        c=cgmGEN.Callback(self.uiFunc_block_create,b,'default'),
                                        ann="{0} : {1}".format(b, self.uiFunc_block_create))


        mUI.MelMenuItemDiv(self.uiMenu_library)
        mUI.MelMenuItem(self.uiMenu_library, l='Rebuild',
                        c=lambda *a: mc.evalDeferred(self.buildMenu_library,lp=True))
        log.info("Library menu rebuilt")
        
    def build_bottomButtonRow(self,parent):
        
        mRow = mUI.MelHRowLayout(parent)
                    
        mUI.MelButton(mRow,
                      h=30,
                      en=False,
                      bgc = CGMUI.guiHeaderColor,
                      label='Fix')
                
        self.uiButton_row = mRow
        mRow.layout()
        
    def uiStatus_fileClear(self):
        self.uiStatus_top(edit=True,bgc = CORESHARE._d_gui_state_colors.get('help'),label = '' )
        self._loadedFile = ""
        
    def uiStatus_fileExplorer(self):
        if os.path.exists(self._loadedFile):
            os.startfile(PATHS.Path(self._loadedFile).up().asFriendly())
        
        return
        if self._loadedFile and os.path.exists(self._loadedFile):
            PATHS.Path(self._loadedFile).up().asFriendly()
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        #Declare form frames...------------------------------------------------------
        _MainForm = mUI.MelFormLayout(parent,ut='CGMUITemplate')#mUI.MelColumnLayout(ui_tabs)
        
        
        #self.uiStatus_topRow = mUI.MelHLayout(_MainForm,)
        """
        self.uiStatus_top = mUI.MelButton(_MainForm,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = CORESHARE._d_gui_state_colors.get('warning'),
                                         label = 'No Data',
                                         h=20)"""
        #>>>Objects Load Row ---------------------------------------------------------------------------------------
        _row_status = mUI.MelHSingleStretchLayout(_MainForm)
        mUI.MelSpacer(_row_status, w = 2)
        
        self.uiStatus_top = mUI.MelButton(_row_status,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = CORESHARE._d_gui_state_colors.get('warning'),
                                         label = 'No Data',
                                         h=20)
        mUI.MelIconButton(_row_status,
                          ann='Clear the loaded file link',
                          image=os.path.join(CGMUI._path_imageFolder,'clear.png') ,
                          w=25,h=25,
                          bgc = CGMUI.guiButtonColor,
                          c = lambda *a:self.uiStatus_fileClear())
        mUI.MelIconButton(_row_status,
                          ann='Open Dir',
                          image=os.path.join(CGMUI._path_imageFolder,'find_file.png') ,
                          w=25,h=25,
                          bgc = CGMUI.guiButtonColor,
                          c = lambda *a:self.uiStatus_fileExplorer())        
        
        _row_status.setStretchWidget(self.uiStatus_top)
        mUI.MelSpacer(_row_status, w = 2)
        _row_status.layout()        
        
        
        
        _inside = mUI.MelScrollLayout(_MainForm,ut='CGMUITemplate')
        

        
        #Top Section -----------
        self.uiSection_top = mUI.MelColumn(_inside ,useTemplate = 'cgmUISubTemplate',vis=True)         
        self.uiUpdate_top()
  
        #data frame...------------------------------------------------------
        try:self.var_shapeDat_dataFrameCollapse
        except:self.create_guiOptionVar('cgmDat_dataFrameCollapse',defaultValue = 0)
        mVar_frame = self.var_cgmDat_dataFrameCollapse
        
        _frame = mUI.MelFrameLayout(_inside,label = 'Data',vis=True,
                                    collapse=mVar_frame.value,
                                    collapsable=True,
                                    enable=True,
                                    #ann='Contextual MRS functionality',
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        self.uiFrame_data = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 

        mUI.MelLabel(self.uiFrame_data, label = "Select", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        

        #Progress bar... ----------------------------------------------------------------------------
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)


        _buttonRow = self.build_bottomButtonRow(_MainForm)
            
        """
        mUI.MelButton(_MainForm,
                            h=30,
                            bgc = CGMUI.guiHeaderColor,
                            label='Create')"""
        

        _row_cgm = CGMUI.add_cgmFooter(_MainForm)            

        #Form Layout--------------------------------------------------------------------
        _MainForm(edit = True,
                  af = [(_row_status,"top",0),
                        (_row_status,"left",0),
                        (_row_status,"right",0),                        
                        (_inside,"left",0),
                        (_inside,"right",0),
                        (self.uiButton_row,"left",0),
                        (self.uiButton_row,"right",0),                           
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_inside,"bottom",2,self.uiButton_row),
                        (self.uiButton_row,"bottom",2,_row_cgm),
                        (_inside,"top",0,_row_status),
                        ],
                  attachNone = [(self.uiButton_row,"top")])    

        
        
class uiBlockDat(ui):
    USE_Template = 'cgmUITemplate'
    TOOLNAME = "uiBlockDat"
    WINDOW_NAME = "{}UI".format(TOOLNAME)
    WINDOW_TITLE = 'BlockDat | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 400,350
    
    _datClass = BlockDat
    _datTypes = ['cgmBlockDat']
    
    
    
    def build_bottomButtonRow(self,parent):
        mRow = mUI.MelHLayout(parent,padding=4)
        
        
        mc.button(parent=mRow,
                  l = 'Create',
                  ut = 'cgmUITemplate',
                  c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiDat.create, self._dCB_reg['autoPush'].getValue())),
                  ann = 'Build with MRS')
        
        #mUI.MelSeparator(mRow,w=5)
        mc.button(parent=mRow,
                  l = 'Load',
                  ut = 'cgmUITemplate',
                  c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_set)),
                  ann = 'Build with MRS')                        
                
        self.uiButton_row = mRow
        mRow.layout()
        
    def uiUpdate_top(self):
        _str_func = 'uiUpdate_top[{0}]'.format(self.__class__.TOOLNAME)
        log.debug("|{0}| >>...".format(_str_func))
        self.uiSection_top.clear()
        
        mc.setParent(self.uiSection_top)
        _inside = self.uiSection_top
        self.uiStatus_blockString = mUI.MelLabel(_inside,label = '...')
        
        """        
        CGMUI.add_Header('Functions')
        mc.button(parent=_inside,
                  l = 'Create',
                  ut = 'cgmUITemplate',
                  c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiDat.create, self._dCB_reg['autoPush'].getValue())),
                  ann = 'Build with MRS')"""

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

        
        """
        _button = mc.button(parent=_inside,
                            l = 'Load',
                            ut = 'cgmUITemplate',
                            c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_set)),
                            ann = 'Build with MRS')"""                
        
    def uiStatus_refresh(self, string=None):
        CGMDAT.ui.uiStatus_refresh(self, string)
        if self.uiDat:
            _color = BLOCKSHARE.d_outlinerColors.get(self.uiDat.dat['blockType'])['main'] or SHARED._d_gui_state_colors.get('connected')#d_colors.get(mDat.get('side'),d_colors['center'])
            self.uiStatus_blockString(e=1, label = blockDat_getString(self.uiDat), bgc=_color)
        
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
            for k,cb in list(self._dCB_reg.items()):
                kws[k] = cb.getValue()
            pprint.pprint(kws)

        
        mc.undoInfo(openChunk=True)

        for mBlock in mBlocks:
            log.debug(log_sub(_str_func,mBlock.mNode))
            try:blockDat_load(mBlock, self.uiDat.dat, **kws)
            except Exception as err:
                log.error("{} | err: {}".format(mBlock.mNode, err))
                    
        mc.undoInfo(closeChunk=True)
        
        return
    

    
    
@cgmGEN.Wrap_exception
class uiBlockConfigDat(ui):
    USE_Template = 'cgmUITemplate'
    TOOLNAME = "uiBlockConfigDat"
    WINDOW_NAME = "BlockConfigUI"
    WINDOW_TITLE = 'BlockConfig | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = False
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 600,350
    
    _datClass = BlockConfig
    
    def post_init(self,*args,**kws):
        CGMDAT.ui.post_init(self,*args,**kws)
        if self.uiDat.dat:
            self.uiUpdate_data()
            
            
    def uiFunc_appendData(self,ml_context = []):
        _str_func = 'uiFunc_appendData[{0}]'.format(self.__class__.TOOLNAME)
        log.debug(log_start(_str_func))
        
        if self.uiDat.append(ml_context):
            self.uiUpdate_data()
            
        
    def uiFunc_dat_clear(self):
        _str_func = 'uiFunc_dat_clear[{0}]'.format(self.__class__.TOOLNAME)
        log.debug(log_start(_str_func))
        
        result = mc.confirmDialog(title="Clear Dat",
                                  message= "Clear Dat",
                                  button=['OK','Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        
        if result != 'OK':
            log.error("|{}| >> Cancelled.".format(_str_func))
            return False        
        
        self.uiDat.clear()
        self.uiUpdate_data()
        
            
    def uiFunc_removeData(self,idx=None):
        _str_func = 'uiFunc_removeData[{0}]'.format(self.__class__.TOOLNAME)
        log.debug(log_start(_str_func))
        try:_block = self.uiDat.dat['blockList'][idx]
        except:
            raise ValueError("{} | invalid idx: {}".format(_str_func,idx))
            
        result = mc.confirmDialog(title="Removing Dat| Dat {}".format(_block),
                                  message= "Remove: {}".format(_block),
                                  button=['OK','Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        
        if result != 'OK':
            log.error("|{}| >> Cancelled.".format(_str_func))
            return False        
        
        if idx is not None:
            self.uiDat.remove(idx)
            self.uiUpdate_data()            
            return
        
        ml_process = copy.deepcopy(self.uiDat.dat['blockList'])
        
        for i,a in enumerate(ml_process):
            if self._dCB_blocks[i].getValue():
                self.uiDat.remove(i)
        self.uiUpdate_data()
        
    
    def uiFunc_update(self,idx=None, mBlock = None):
        _str_func = 'uiFunc_update[{0}]'.format(self.__class__.TOOLNAME)
        log.debug(log_start(_str_func))
        
        if idx == None:
            raise ValueError("No known index")
        
        if not mBlock:
            mBlock = BLOCKGEN.block_getFromSelected()
            
        if not mBlock:
            return log.error("No block selected")
                
        
        result = mc.confirmDialog(title="Updating BlockConfig | Dat {}".format(idx),
                                  message= "DataSource: {}".format(mBlock.p_nameBase),
                                  button=['OK','Cancel'],
                                  defaultButton='OK',
                                  cancelButton='Cancel',
                                  dismissString='Cancel')
        
        if result != 'OK':
            log.error("|{}| >> Cancelled.".format(_str_func))
            return False
        
        #Buffer this so updating blocks doesn't break our parentage
        mParent = mBlock.p_blockParent
        if not mParent or mParent.blockType in ['master']:
            bfr_blockParent = self.uiDat.mBlockDat[idx].dat['blockParent']
        else:
            bfr_blockParent = False
            
        mBlockDat = BlockDat(mBlock)
        self.uiDat.mBlockDat[idx] = mBlockDat
        self.uiDat.dat['config'][str(idx)] = blockDat_get(mBlock, False)
        
        if bfr_blockParent:
            self.uiDat.mBlockDat[idx].dat['blockParent'] = bfr_blockParent
            self.uiDat.dat['config'][str(idx)]['blockParent'] = bfr_blockParent
        
            print((self.uiDat.mBlockDat[idx].dat['blockParent']))
            print((self.uiDat.dat['config'][str(idx)]['blockParent'])) 
            log.warning("|{}| >> Using bfr'd blockParent.".format(_str_func))
        
        
        return log.info("Replaced Block [{}] data with | [{}]".format(idx, mBlock))
        
        
            
    def uiUpdate_top(self):
        _str_func = 'uiUpdate_top[{0}]'.format(self.__class__.TOOLNAME)
        log.debug("|{0}| >>...".format(_str_func))
        self.uiSection_top.clear()
        
        mc.setParent(self.uiSection_top)
        _inside = self.uiSection_top

        
        
        """
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
                            ann = 'Build with MRS')                """
        
        
    def uiFunc_create(self,idx=None):
        if idx is not None:
            blockConfig_create(self.uiDat, idx)
            return
        for i,a in enumerate(self.uiDat.dat['blockList']):
            if self._dCB_blocks[i].getValue():
                blockConfig_create(self.uiDat, i)
                
    def uiFunc_setToggles(self,arg):
        for i,mCB in list(self._dCB_blocks.items()):
            mCB.setValue(arg)
                
    def uiFunc_dat_get(self):
        _str_func = 'uiFunc_dat_get[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        _sel = mc.ls(sl=1)
        
        ml_context = BLOCKGEN.block_getFromSelected(True)
        if not ml_context:
            md = BLOCKGEN.get_scene_block_heirarchy()
            ml_context =  cgmGEN.walk_heirarchy_dict_to_list(md)              
        if not ml_context:
            return log.error("No blocks selected")
        
        self.uiDat.get(ml_context)
        
        self.uiStatus_refresh(string = "Scene | Blocks: [{}]".format(len(self.uiDat.mBlockDat)))
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
            for k,cb in list(self._dCB_reg.items()):
                kws[k] = cb.getValue()
            pprint.pprint(kws)

        
        mc.undoInfo(openChunk=True)

        for mBlock in mBlocks:
            log.debug(log_sub(_str_func,mBlock.mNode))
            try:blockDat_load(mBlock, self.uiDat.dat, **kws)
            except Exception as err:
                log.error("{} | err: {}".format(mBlock.mNode, err))
                    
        mc.undoInfo(closeChunk=True)
        
        return
    
    def log_blockDat(self,idx = None):
        _d = self.uiDat.dat['config'][str(idx)]
        pprint.pprint(list(_d.keys()))
        
    def get_blockDatUI(self,idx=None):
        mUI = uiBlockDat()
        _dSource = self.uiDat.dat['config'][str(idx)]
        _d = {k:_dSource[k] for k in list(_dSource.keys())}
        
        mDat = BlockDat(dat = _d)
        
        mUI.uiDat = mDat
        mUI.uiStatus_refresh(  )
        
    def get_shapeDatUI(self,idx=None):
        mDat = self.uiDat.dat['config'][str(idx)].get('shape')
        if not mDat:
            return log.error("No shapeDat found")
        
        mUI = uiShapeDat()
        mUI.uiDat = mDat
        mUI.uiStatus_refresh(  )
        
    def uiUpdate_data(self):
        _str_func = 'uiUpdate_data[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
         
        self.uiFrame_data.clear()
        
        if not self.uiDat:
            return
        
        """
        mUI.MelLabel(self.uiFrame_data, label = "Select", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        
        for util in ['Select Source']:
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_dat,util),
                          ann="...",
                          label=util,
                          ut='cgmUITemplate',
                          h=20)"""
        
        self._dCB_blocks = {}
        
        _row = mUI.MelHLayout(self.uiFrame_data, h=30, padding=5 )
        mUI.MelButton(_row, label = 'All',ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_setToggles,1))
        mUI.MelButton(_row, label = 'None',ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_setToggles,0))
        mUI.MelSeparator(_row,w=10)
        mUI.MelButton(_row, label = 'Clear',ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_dat_clear))
        mUI.MelButton(_row, label = 'Add',ut='cgmUITemplate',
                      c = cgmGEN.Callback(self.uiFunc_appendData))
        #mUI.MelButton(_row, label = 'Remove',ut='cgmUITemplate',
        #              c = cgmGEN.Callback(self.uiFunc_removeData))
        _row.layout()
        
        
        for i,a in enumerate(self.uiDat.dat['blockList']):
            try:
                
                #...make our block list
                mDat = self.uiDat.mBlockDat[i]
                _type = mDat.dat['blockType']
                _side = mDat.dat.get('side','center')
                if _side in ['none','None']:
                    _side = 'center'
                if _side in [False,'none',None]:
                    _side = 'center'
                    
                cgmGEN._reloadMod(CORESHARE)
                d_color = CORESHARE._d_gui_direction_colors_use[_side]
                if MATH.is_even(i):
                    _ut = 'cgmUITemplate'
                    _header = d_color['base']
                else:
                    _ut = 'cgmUIHeaderTemplate'
                    _header = d_color['base2']
                _bgc = d_color['bgc']
                                        
                    
                #_colorSide = CORESHARE._d_gui_direction_colors_use.get(_side) or SHARED._d_gui_state_colors.get('warning')
                #_colorSub = CORESHARE._d_gui_direction_colors_use.get(_side) or SHARED._d_gui_state_colors.get('warning')
                #_colorDark = CORESHARE._d_gui_direction_colors_use.get(_side) or SHARED._d_gui_state_colors.get('warning')
                
                #pprint.pprint([mDat.dat['baseName'],_colorSide,_colorSub,_colorDark])
                #_color = BLOCKSHARE.d_outlinerColors.get(mDat.dat['blockType'])['main']#d_colors.get(mDat.get('side'),d_colors['center'])
                #_colorSub = BLOCKSHARE.d_outlinerColors.get(mDat.dat['blockType'])['sub']#d_colors.get(mDat.get('side'),d_colors['center'])
                
                
                #mUI.MelIconCheckBox(self.uiFrame_data,)
                _label = CORESTRINGS.stripWhiteSpaceStart(self.uiDat.dat['uiStrings'][i])#blockDat_getString(self.uiDat.mBlockDat[i])
                
                #Row...
                _row = mUI.MelHSingleStretchLayout(self.uiFrame_data, h=30, bgc=_header)            
    
                _icon = None
                try:
                    _icon = os.path.join(_path_imageFolder,'mrs','{}.png'.format(_type))
                except:pass
                #mc.iconTextButton( style='iconAndTextVertical', image1='cube.png', label='cube' )
                #continue
                
                mUI.MelSpacer(_row,w=10)
                            
                if _icon:
                    #mUI.MelIconButton
                    mUI.MelIconButton(_row,
                                      ann=_type,
                                      style='iconOnly',
                                      l=_label,
                                      image1 =_icon ,
                                      ua=True,
                                      #mw=5,
                                      scaleIcon=True,
                                      w=30,h=30,
                                      #bgc = d_color['base']
                                      )
                                      #olc=[float(v) for v in d_state_colors['form']],
                                      #olb=[float(v) for v in d_state_colors['form']]+[.5],
                                      #w=20,h=20,
                                      #c=cgmGEN.Callback(self.uiFunc_setBlockType,b))
                    """
                    mUI.MelImage(_row,
                                 w=10,
                                 h=10,
                                      image =_icon)
                                      #olc=[float(v) for v in d_state_colors['form']],
                                      #olb=[float(v) for v in d_state_colors['form']]+[.5],
                                      #w=20,h=20)"""
                mUI.MelLabel(_row,label = "[{}]".format(i))
                
                _lenParents = mDat.dat['lenParents'] 
                if _lenParents:
                    mUI.MelSpacer(_row,w=_lenParents * 10)
                
                
                _cb = mUI.MelCheckBox(_row,l=_label,
                                     #annotation = d_dat.get('ann',k),
                                     value = 1)
                self._dCB_blocks[i] = _cb
                _row.setStretchWidget(_cb)
                
                mDat = mDat.dat.get('shape')
    
                mUI.MelButton(_row, bgc=d_color['button'], label = 'BlockDat',
                              c = cgmGEN.Callback(self.get_blockDatUI,i))
                #mUI.MelButton(_row, bgc=_colorDark, label = 'Log',
                #              c = cgmGEN.Callback(self.log_blockDat,i))                
                mUI.MelButton(_row, bgc=d_color['button'], label = 'ShapeDat',en =bool(mDat),
                              c = cgmGEN.Callback(self.get_shapeDatUI,i))            
                mUI.MelButton(_row, bgc=d_color['button'], label = 'Create',
                              c = cgmGEN.Callback(self.uiFunc_create,i))
                mUI.MelButton(_row, bgc=d_color['button'], label = 'Update',
                              c = cgmGEN.Callback(self.uiFunc_update,i))
                mUI.MelButton(_row, bgc=d_color['button'], label = 'Remove',
                              ann="Remove this BlockDat",
                              c = cgmGEN.Callback(self.uiFunc_removeData,i))            
                mUI.MelSpacer(_row,w=10)
                
                _row.layout()
                
                mUI.MelSeparator(self.uiFrame_data,h=1)
            except Exception as err:
                log.error(err)
        
        mc.setParent(self.uiFrame_data)
        CGMUI.add_Header('Other')
        """
        mc.button(parent=self.uiFrame_data,
                  l = 'Create',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(self.uiFunc_create),
                  #c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiDat.create, self._dCB_reg['autoPush'].getValue())),
                  ann = 'Build with MRS')"""
        
        mUI.MelSpacer(self.uiFrame_data,h=30)
        mUI.MelLabel(self.uiFrame_data, label = "PPRINT", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        
        for a in list(self.uiDat.dat.keys()):
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_printDat,a),
                          ann="...",
                          label=a,
                          ut='cgmUITemplate',
                          h=20)
            
        mUI.MelButton(self.uiFrame_data,
                      c = cgmGEN.Callback(self.uiFunc_printDat,'all'),
                      ann="...",
                      label='all',
                      ut='cgmUITemplate',
                      h=20)
        
    def build_bottomButtonRow(self,parent):
        mRow = mUI.MelButton(parent,
                      l = 'Create',
                      c = cgmGEN.Callback(self.uiFunc_create),
                      bgc = CGMUI.guiHeaderColor,
                      en=True)
                
        self.uiButton_row = mRow
        
        
    def buildMenu_library2( self, force=True, *args, **kws):
        if self.uiMenu_library and force is not True:
            log.debug("No load...")
            return
        
        if force:
            get_ext_options(True)
            
        _options, _categories = get_ext_options()
        
        
        self.uiMenu_library.clear()
        md_menus = {}
        for k in _categories.get('cgmBlockConfig',[]):
            f = _options.get(k)
            print(("{} | {}".format(k,f)))
            _useMenu = self.uiMenu_library
            if '.' in k:
                _split = k.split('.')[:-1]
                for i,sub in enumerate(_split):
                    _splitKey = '.'.join(_split[i:])
                    
                    if not i:
                        _parent = self.uiMenu_library
                    if not md_menus.get(_splitKey):
                        _sub = mUI.MelMenuItem( _parent, subMenu=True, l=sub, tearOff=True)
                        md_menus[_splitKey]  = _sub
                    _parent = md_menus[_splitKey] 
                    _useMenu = md_menus[_splitKey] 
                            
            mUI.MelMenuItem(_useMenu, l=k,
                            c=cgmGEN.Callback(self.uiFunc_dat_load,**{'filepath':f}),
                            ann="{} | {}".format(k, f))                


        mUI.MelMenuItemDiv(self.uiMenu_library)
        mUI.MelMenuItem(self.uiMenu_library, l='Rebuild',
                        c=lambda *a: mc.evalDeferred(self.buildMenu_library,lp=True))
        log.info("Library menu rebuilt")
        return
    
    
        _d = copy.copy(self._d_modules)
        for b in _d[1]['blocks']:
            if _d[0][b].__dict__.get('__menuVisible__'):
                mUI.MelMenuItem(self.uiMenu_library, l=b,
                                c=cgmGEN.Callback(self.uiFunc_block_create,b),
                                ann="{0} : {1}".format(b, self.uiFunc_block_create))
                
                l_options = RIGBLOCKS.get_blockProfile_options(b)                
                if l_options:
                    for o in l_options:
                        mUI.MelMenuItem(self.uiMenu_library, l=o,
                                        c=cgmGEN.Callback(self.uiFunc_block_create,b,o),
                                        ann="{0} : {1}".format(b, self.uiFunc_block_create))

        
        for c in list(_d[1].keys()):
            #d_sections[c] = []
            if c == 'blocks':continue
            for b in _d[1][c]:
                if _d[0][b].__dict__.get('__menuVisible__'):
                    #d_sections[c].append( [b,cgmGEN.Callback(self.uiFunc_block_create,b)] )
                    l_options = RIGBLOCKS.get_blockProfile_options(b)
                    if l_options:
                        _sub = mUI.MelMenuItem( self.uiMenu_library, subMenu=True,l=b,tearOff=True)
                        l_options.sort()
                        for o in l_options:
                            _l = "{0}".format(o)
                            _c = cgmGEN.Callback(self.uiFunc_block_create,b,o)
                            mUI.MelMenuItem(_sub, l=_l,
                                            c=_c,
                                            ann="{0} : {1}".format(_l, _c)
                                            )
                    else:
                        mUI.MelMenuItem(self.uiMenu_library, l=b,
                                        c=cgmGEN.Callback(self.uiFunc_block_create,b,'default'),
                                        ann="{0} : {1}".format(b, self.uiFunc_block_create))


        mUI.MelMenuItemDiv(self.uiMenu_library)
        mUI.MelMenuItem(self.uiMenu_library, l='Rebuild',
                        c=lambda *a: mc.evalDeferred(self.buildMenu_library,lp=True))
        log.info("Library menu rebuilt")


#=====================================================================================================================
#...ShapeDat
#=====================================================================================================================
class ShapeDat(BaseDat):
    '''
    Class to handle blockShape data.
    '''    
    _ext = 'cgmShapeDat'
    _startDir = ['cgmDat','mrs','shapeDat']
    
    def __init__(self, mBlock = None, filepath = None, **kws):
        """

        """
        _str_func = 'data.__buffer__'
        log.debug(log_start(_str_func))
        super(ShapeDat, self).__init__(filepath, **kws)
        
        self.str_filepath = None
        self.dat = {}
        self.mBlock = mBlock
        
    def get(self, mBlock = None):
        _str_func = 'data.get'
        log.debug(log_start(_str_func))
        if not mBlock:
            mBlock = self.mBlock
        self.dat = shapeDat_get(mBlock)    
    
    def set(self, mBlock = None, data = None, settings=True, formHandles=True, loftHandles=True, loftShapes=True, loftHandleMode='world', shapeMode='ws', loops=2):
        _str_func = 'data.set'
        log.debug(log_start(_str_func))
        
        mBlock = self.mBlock
        if not data:
            data = self.dat
            
        dat_set(mBlock, data, settings, formHandles,loftHandles,loftShapes,loftHandleMode,shapeMode,loops)
        
    def load(self):
        _str_func = 'data.load'        
        log.debug(log_start(_str_func))
        
        if not self.mBlock:
            raise ValueError("Must have mBlock to save")
        
        startDir = self.startDir_get()
        _path = "{}.{}".format( os.path.normpath(os.path.join(startDir,self.mBlock.p_nameBase)), data._ext)
        
        if not os.path.exists(_path):
            raise ValueError("Invalid path: {}".format(_path))
        pprint.pprint(_path)
        
        self.read(_path)
        self.set()
        
        return        
        
    def write(self,*arg,**kws):
        _str_func = 'data.save'        
        log.debug(log_start(_str_func))
        
        if not self.mBlock:
            raise ValueError("Must have mBlock to save")
        
        if self.dir_export:
            startDir = self.dir_export
        else:
            startDir = self.startDir_get()
        
        _path = "{}.{}".format( os.path.normpath(os.path.join(startDir,
                                                              self.mBlock.atUtils('get_partName'))),
                                ShapeDat._ext)
        pprint.pprint(_path)
        
        BaseDat.write(self,_path, *arg,**kws)
        return
        if not os.path.exists(startDir):
            CGMDAT.CGMOS.mkdir_recursive(startDir)
        
        if not mode:
            pass
        

def shapeDat_set(mBlock,data,
                 settings = True,
                 formHandles = True,
                 loftHandles = True,
                 loftShapes=True,
                 loftHandleMode = 'world',
                 shapeMode = 'ws',
                 loops=2,
                 **kws):
    _str_func = 'shapeDat_set'
    log.debug(log_start(_str_func))
    
    _str_block = mBlock.mNode
    ml_handles = None
    
    #Logic checks....
    b_dataAddLever = False
    b_targetAddLever = False
    l_skips = []
    _dataForward = 0
    _dataSkip = 0
    
    if mBlock.hasAttr('addLeverBase'):
        if data['base'].get('addLeverBase') not in ['none']:
            print("data has addLeverBase")
            b_dataAddLever = True
        else:
            print("data has no addLeverBase")
            
        if mBlock.hasAttr('addLeverBase') and mBlock.addLeverBase:
            print("mBlock has addLeverBase")
            b_targetAddLever = True        
        else:
            print("mBlock has no addLeverBase")
            
        if not b_targetAddLever and b_dataAddLever:
            print("Target doesn't, data does. dataSkip 1 [0]")
            _dataSkip = 1
                
        if  b_targetAddLever and not b_dataAddLever:
            print("Target does, data doesn't. Pull data forward")
            _dataForward = -1
            if 0 not in l_skips:
                l_skips.append(0)        
        
    
    #First part of block reset to get/load data------------------------------------------------------
    pos = mBlock.p_position
    orient = mBlock.p_orient
    scale = mBlock.blockScale
    
    mBlock.p_position = 0,0,0
    mBlock.p_orient = 0,0,0
    mBlock.blockScale = 1.0

    def get_loftShapes(ml_handles):
        _res = {}
        
        for i,mObj in enumerate(ml_handles):
            _res[i] = {'mLoft': mObj.getMessageAsMeta('loftCurve'),
                       'mSubShapers':mObj.msgList_get('subShapers'),
                       }

    
        return _res
        
    def get_handles(ml_handles):
        if ml_handles:
            log.info("Found...")
            return ml_handles
        
        ml_handles = mBlock.msgList_get('formHandles')
        return ml_handles
    
    if settings:
        log.info(log_sub(_str_func,'Settings...'))
        
        for a,v in list(data['settings'].items()):
            try:
                #if a in l_enumLists:
                #    ATTR.datList_connect(_str_block,a,v,enum=1)
                if a in l_datLists:
                    dTmp = {'enum':False}
                    if a == 'loftList':
                        dTmp['enum']  = BLOCKSHARE._d_attrsTo_make['loftShape']
                        dTmp['mode'] = 'enum'
                        
                    ATTR.datList_connect(_str_block, a,v, **dTmp)                     
                    
                else:
                    ATTR.set(_str_block, a, v)
            except Exception as err:
                log.error("{} | {} | {}".format(a,v,err))

        if mBlock.blockState < 1:
            mBlock.p_blockState = 1
            
        
        
    #Form Handles and shapes -----------------------------------------------------------    
    if formHandles: 
        log.info(log_sub(_str_func,'FormHandles...'))
        ml_handles = get_handles(ml_handles)
        
        if mBlock in ml_handles:
            raise ValueError("mBlock cannot be in handles")
        
        pprint.pprint(ml_handles)
        
        dat_form = data['handles']['form']

            
        for ii in range(len(ml_handles)+1):#...since the end affects the mids we need to lop through
            for i, mObj in enumerate(ml_handles):
                if i in l_skips:
                    continue
                
                try:dat_form[i]
                except:
                    log.debug(log_msg(_str_func, 'No data on: {}'.format(i)))
                    continue
                    
                try:
                    
                    if _dataForward:
                        i = i-1
                    if _dataSkip:
                        i = i+1
                        
                    #mObj.translate = dat_form[i]['trans']
                    #mObj.rotate = dat_form[i]['rot']
                    mObj.p_position = dat_form[i]['pos']
                    mObj.p_orient = dat_form[i]['orient']
                    
                    mObj.scaleX = dat_form[i]['scale'][0]
                    mObj.scaleY = dat_form[i]['scale'][1]
                    try:mObj.scaleZ = dat_form[i]['scale'][2]
                    except:pass
                except:
                    log.debug(log_msg(_str_func, 'No data on: {}'.format(i)))
                    
                
    
    if ml_handles and ml_handles[-1].getMessage('pivotHelper'):
        log.info(log_msg(_str_func,'pivot Helper'))
        
        mPivotHelper = ml_handles[-1].pivotHelper
        dat_pivot = data.get('pivotHelper')
        if dat_pivot:
            dat_pivot = dat_pivot[0]
            log.info(log_msg(_str_func,'setting pivotHelper'))
            pprint.pprint(dat_pivot)
            mPivotHelper.p_position = dat_pivot['pos']
            
            mPivotHelper.p_orient = dat_pivot['orient']
            
            mPivotHelper.scaleX = dat_pivot['scale'][0]
            mPivotHelper.scaleY = dat_pivot['scale'][1]
            try:mPivotHelper.scaleZ = dat_pivot['scale'][2]
            except:pass
            
            shapes_set(mPivotHelper, dat_pivot['shapes'],'ws')
        
            
        
        dat_pivotTop = data.get('pivotTopHelper')            
        mTopLoft = mPivotHelper.getMessageAsMeta('topLoft')
        if mTopLoft and dat_pivotTop:
            dat_pivotTop = dat_pivotTop[0]            
            log.info(log_msg(_str_func,'setting pivotTopHelper'))
            pprint.pprint(dat_pivotTop)
            
            mTopLoft.p_position = dat_pivotTop['pos']
            mTopLoft.p_orient = dat_pivotTop['orient']
            
            mTopLoft.scaleX = dat_pivotTop['scale'][0]
            mTopLoft.scaleY = dat_pivotTop['scale'][1]
            try:mTopLoft.scaleZ = dat_pivotTop['scale'][2]
            except:pass
            
            shapes_set(mTopLoft, dat_pivotTop['shapes'],'ws')                
            
    
    #loft handles and shapes -----------------------------------------------------------
    if loftHandles or loftShapes:
        log.info(log_sub(_str_func,'loftHandles...'))
        if not ml_handles:
            ml_handles = get_handles(ml_handles)
            
            
            
        dat_loft = data['handles']['loft']
        dat_shapes = data['handles']['loftShapes']
        
        dat_sub = data['handles']['sub']
        dat_subShapes = data['handles']['subShapes']
        dat_subRel = data['handles']['subRelative']
        

        md_loftShapes = get_loftShapes(ml_handles)
        
        
        for i,mObj in enumerate(ml_handles):
            if i in l_skips:
                continue
            
                    
            _mLoft = md_loftShapes[i].get('mLoft')
            _mSubShapers = md_loftShapes[i].get('mSubShapers',[])
            
            
            if _dataForward:
                i = i-1
            if _dataSkip:
                i = i+1
                
            if _mLoft:
                if loftHandles:
                    for iii in range(loops):
                        if loftHandleMode == 'local':
                            _mLoft.translate = dat_loft[i]['trans']
                            _mLoft.rotate = dat_loft[i]['rot']                        
                        else:
                            _mLoft.p_position = dat_loft[i]['pos']
                            _mLoft.p_orient = dat_loft[i]['orient']       
                            
                        _mLoft.scale = dat_loft[i]['scale']
                            
                    #mObj.p_position = dat_loft[i]['pos']
                    
                if loftShapes:
                    log.info(log_sub(_str_func,'loft loftShape {}...'.format(i)))
                    #for iii in range(loops):
                    shapes_set(_mLoft, dat_shapes[i],shapeMode)                    
            
            
            if _mSubShapers:
                if loftHandles:
                    _datLast = None
                    for iii in range(loops):
                        for ii,mObj in enumerate(_mSubShapers):
                            if loftHandles:
                                try:
                                    _datTmp = dat_sub[i][ii]
                                    _datLast = _datTmp
                                except:
                                    log.warning("Missing sub dat: {} | using last".format(ii))
                                    _datTmp = _datLast
                                    
                                try:
                                    if loftHandleMode == 'local':
                                        mObj.translate = _datTmp['trans']
                                        mObj.rotate = _datTmp['rot']                        
                                    else:
                                        mObj.p_position = _datTmp['pos']
                                        mObj.p_orient = _datTmp['orient']                    
                                        
                                    #mObj.p_position = _datTmp['pos']
                                    mObj.scale = _datTmp['scale']
                                except Exception as err:
                                    pprint.pprint(_datTmp)
                                    log.error("loft handle loop: {} | i: {} | ii:{} | err: {}".format(iii,i,ii,err))
                        
                        
                        #Relative set
                        try:
                            relativePointDat_setFromObjs([mObj.mNode for mObj in _mSubShapers],
                                                         ml_handles[i].mNode,
                                                         ml_handles[i+1].mNode,
                                                         dat_subRel[i] ) 
                        except Exception as err:
                            log.error("loft handle loop: {} | i: {} | ii:{} | err: {}".format(iii,i,ii,err))
                            
                    

                if loftShapes:
                    log.info(log_sub(_str_func,'sub loftShapes...'))
                    for iii in range(loops):
                        for ii,mObj in enumerate(_mSubShapers):
                            try:
                                shapes_set(mObj, dat_subShapes[i][ii],shapeMode)
                            except Exception as err:
                                log.error("loft shape loop: {} | i: {} | ii:{} | err: {}".format(iii,i,ii,err))
    #if loftShapes:
    #    log.info(log_sub(_str_func,'loftShapes...'))
        
    #Restore our block...-----------------------------------------------------------------
    mBlock.p_position = pos
    mBlock.p_orient = orient         
    mBlock.blockScale = scale         
            
l_dataAttrs = ['blockType','addLeverBase', 'addLeverEnd','cgmName']
l_enumLists = ['loftList']
l_datLists = ['numSubShapers']

def shapeDat_get(mBlock=None):
    _str_func = 'shapeDat_get'
    log.debug(log_start(_str_func))
    
    _str_block = mBlock.mNode
    
    #Check state. must be form state
    if mBlock.blockState < 1:
        raise ValueError("Must be in form state")
    
    _type = mBlock.blockType
    _supported = ['limb','segment','handle','head']
    if _type not in _supported:
        return log.error("{} type not supported. | Supported: {}".format(_type,_supported))
    
    #First part of block reset to get/load data------------------------------------------------------
    pos = mBlock.p_position
    orient = mBlock.p_orient
    scale = mBlock.blockScale
    
    #prep.... ------------------------------------------------------------------------------    
    mBlock.p_position = 0,0,0
    mBlock.p_orient = 0,0,0
    mBlock.blockScale = 1.0

    try:
        
        def get_attr(obj,a,d = {}):
            try:
                if a in l_enumLists:
                    if ATTR.datList_exists(_str_block,a):
                        _d[a] = ATTR.datList_get(_str_block,a,enum=1)
                elif a in l_datLists:
                    if ATTR.datList_exists(_str_block,a):
                        _d[a] = ATTR.datList_get(_str_block,a)                
                elif ATTR.get_type(obj, a) == 'enum':
                    d[a] = ATTR.get_enumValueString(_str_block, a)
                else:
                    d[a] = ATTR.get(_str_block, a)
            except:pass        
        
        #Form count
        _res = {}
        
        #Settings ... ---------------------------------------------------------------------------
        _d = {}
        _res['settings'] = _d
        
        for a in ['loftSetup','loftShape','numShapers','numSubShapers','shapersAim','shapeDirection','loftList']:
            get_attr(_str_block,a,_d)
        
                
        #Dat ... ---------------------------------------------------------------------------
        _d = {}
        _res['base'] = _d
        
        for a in l_dataAttrs:
            get_attr(_str_block,a,_d)
        
        _d['source']= mBlock.p_nameBase
        _d['type'] = _d.pop('cgmName','none')
                
        #FormHandles ... ---------------------------------------------------------------------------
        _d = {}
        _d['form'] = []
        _d['loft'] = []
        _d['loftShapes'] = []
        
        _d['sub'] = []
        _d['subShapes'] = []    
        _d['subRelative'] = []    
        
        _res['handles'] = _d
        
        ml_handles = mBlock.msgList_get('formHandles')
        #pprint.pprint(ml_handles)
        
        _res['base']['shapers'] = len(ml_handles)
        _res['base']['subs'] = []
        _num_subs = _res['base']['subs']
        
        
        def getCVS(mObj):
            _obj = mObj.mNode
            _res = {}
            
            _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)
    
            for i,s in enumerate(_l_shapes_source):
                _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
                for i,ep in enumerate(_l_ep_source):
                    _pos = POS.get(ep,space='os')
                
        def get(mObj,shapes=False):
            d = {'pos':mObj.p_position,
                 'orient':mObj.p_orient,
                 'rot':mObj.rotate,
                 'trans':mObj.translate,
                 'scale':mObj.scale}
            
            if shapes:
                d['shapes'] = shapes_get(mObj,'ws')
                
            return d
        
        for i, mObj in enumerate(ml_handles):
            _d['form'].append( get(mObj))
            _l_shapes = []
            _l_loft = []
            
            mLoftCurve = mObj.getMessageAsMeta('loftCurve')
            
            ml_loft = []
            
            #LoftCurve.....--------------------------------------------------------
            if mLoftCurve:
                _d['loft'].append(get(mLoftCurve))
                _d['loftShapes'].append(shapes_get(mLoftCurve,'all'))
            else:
                _d['loft'].append(False)
                _d['loftShapes'].append(False)            
            
            #sub..--------------------------------------------------------
            ml_subShapers = mObj.msgList_get('subShapers')
            #If subShapes, process them
            if ml_subShapers:
                l_subShapes = []
                l_sub = []
                for ii,mObj in enumerate(ml_subShapers):
                    l_subShapes.append( shapes_get(mObj,'all'))
                    l_sub.append( get(mObj))
                
                _d['subRelative'].append( relativePointDat_getFromObjs([mObj.mNode for mObj in ml_subShapers],
                                                               ml_handles[i].mNode,ml_handles[i+1].mNode) )
                _d['subShapes'].append( l_subShapes )
                _d['sub'].append( l_sub )
                _num_subs.append(len(ml_subShapers))
            else:
                _d['sub'].append(False)
                _d['subShapes'].append(False)               
                _d['subRelative'].append(False)               
                _num_subs.append(0)
        
            if mObj.getMessage('pivotHelper'):
                mPivotHelper = mObj.pivotHelper
                _res['pivotHelper'] = [ get(mPivotHelper,shapes=True)]
                    
                
                mTopLoft = mPivotHelper.getMessageAsMeta('topLoft')
                if mTopLoft:
                    _res['pivotTopHelper'] = [ get(mTopLoft,shapes=True)]
    
        
    
        #pprint.pprint(_res)
        
        #Restore our block...-----------------------------------------------------------------
        #mBlock.p_position = pos
        #mBlock.p_orient = orient      
        return _res
    finally:
        #Restore our block...-----------------------------------------------------------------
        mBlock.p_position = pos
        mBlock.p_orient = orient         
        mBlock.blockScale = scale             
    
def shapes_get(mObj, mode = 'os'):
    _str_func = 'shapes_get'
    log.debug(log_start(_str_func))
        
    _obj = mObj.mNode
    _res = {}
    _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)

    for i,s in enumerate(_l_shapes_source):
        _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
        
        #Object Space
        if mode in ['os','all']:
            if not _res.get('os'):
                _res['os'] = []
                
            _d = []
            _res['os'].append(_d)
            for i,ep in enumerate(_l_ep_source):
                _d.append(POS.get(ep,space='os'))
        
        #WorldSpace
        if mode in ['ws','all']:
            if not _res.get('ws'):
                _res['ws'] = []        
            _d = []
            _res['ws'].append(_d)
            for i,ep in enumerate(_l_ep_source):
                _d.append(POS.get(ep,space='ws'))        
            
    #pprint.pprint(_res)
    return _res

def shapes_set(mObj, dat, mode = 'os'):
    _str_func = 'shapes_set'
    log.debug(log_start(_str_func))
    
    _dat = dat[mode]
    _obj = mObj.mNode
    _l_shapes_source = mc.listRelatives(_obj,shapes=True,fullPath=True)
    
    if len(_l_shapes_source) != len(_dat):
        raise ValueError("Len of source shape ({0}) != dat ({1})".format(len(_l_shapes_source),len(_dat))) 
    
    for i,s in enumerate(_l_shapes_source):
        _l_ep_source = mc.ls("{0}.cv[*]".format(s),flatten = True)
        _l_pos = _dat[i]
        
        if len(_l_ep_source) != len(_l_pos):
            raise ValueError("Len of source shape {} | ({}) != dat ({})".format(i,len(_l_ep_source),len(_l_pos)))         
        
        for ii,ep in enumerate(_l_ep_source):
            POS.set(ep, _l_pos[ii],space=mode)  
            

def relativePointDat_getFromObjs(targets, start,end, vUp = [0,0,-1]):
    """
    pTar - point of the target
    pStart - Start point
    pEnd - endPoint
    dBase - base distance start to end
    pCrv - closest point on crv
    dCrv - distance to point on crv
    vCrv - vector from crv to point
    vUp - vector up (not using this yet)
    
    """
    _str_func = 'relativePointDat_getFromObj'
    log.debug(log_start(_str_func))
    _res = {'tar':[]}
    
    ml_targets = cgmMeta.validateObjListArg(targets)
    mStart = cgmMeta.validateObjArg(start)
    mEnd = cgmMeta.validateObjArg(end)
    
    
    #p1, p2, pTar
    _res['pStart'] = mStart.p_position
    _pEnd = mEnd.p_position
    
    
    #distance between p1 p2
    _res['dBase'] = DIST.get_distance_between_points(_res['pStart'],_pEnd)
    _res['vBase'] = MATH.get_vector_of_two_points(_res['pStart'],_pEnd)
    _res['vUp'] = vUp
    
    #closest point on linear curve between those
    _crv = CORERIG.create_at(l_pos=[_res['pStart'],_pEnd],create='curveLinear')
    
    for mObj in ml_targets:
        _dObj = {}
        _p = mObj.p_position
        _r = DIST.get_closest_point(_p, _crv, loc=False)
        _close = _r[0]
        _d2 = _r[1]
        #_d2 = DIST.get_distance_between_points(_close, _res['pTar'])
        _vecCrv = MATH.get_vector_of_two_points(_close, _p)
        
        #get dist from start to closest
        _dObj['dClose'] = DIST.get_distance_between_points(_res['pStart'],_close)
        
        _dObj['dCrv'] = _d2
        _dObj['vCrv'] = _vecCrv
        
        _res['tar'].append(_dObj)
    
    mc.delete(_crv)
    
    for k in ['pStart']:
        _res.pop(k)
        
    #pprint.pprint(_res)

    return _res


def relativePointDat_setFromObjs(targets, start, end, d = {}):
    """
    pTar - point of the target
    pStart - Start point
    pEnd - endPoint
    dBase - base distance start to end
    pCrv - closest point on crv
    dCrv - distance to point on crv
    vCrv - vector from crv to point
    vUp - vector up (not using this yet)
    
    """
    _str_func = 'relativePointDat_setFromObjs'
    log.debug(log_start(_str_func))
    _res = {}
    
    ml_targets = cgmMeta.validateObjListArg(targets)
    mStart = cgmMeta.validateObjArg(start)
    mEnd = cgmMeta.validateObjArg(end)
    
    l_tarDat = d.get('tar',[])
    if len(ml_targets) < len(l_tarDat):
        raise ValueError("must have same number of targets as data")
    
    _pStart = mStart.p_position
    _pEnd = mEnd.p_position    
    
    #Get factor -------------------------------------------------------------
    _dCurrent = DIST.get_distance_between_points(_pStart,_pEnd)
    _fac = _dCurrent / d['dBase'] 
    
    
    #transform vector ------------------------------------------------------
    
    vCurrent = MATH.get_vector_of_two_points(_pStart,_pEnd,True)
    vOffset =   MATH.dotproduct(MATH.Vector3(d['vBase'][0],d['vBase'][1],d['vBase'][2]), vCurrent)
    
    #vOffset =   MATH.Vector3(d['vBase'][0],d['vBase'][1],d['vBase'][2]) - vCurrent
    
    for i,mTarget in enumerate(ml_targets):
        dUse = l_tarDat[i] 
        vNew =  MATH.Vector3(dUse['vCrv'][0],dUse['vCrv'][1],dUse['vCrv'][2] ) * (vOffset)
        
        
        #Get relative closest point - start > vector * dClose * factor
        _close = DIST.get_pos_by_vec_dist(_pStart, vCurrent, dUse['dClose'] * _fac)
        #LOC.create(position=_close,name="close")
        
        _new = DIST.get_pos_by_vec_dist(_close, vNew, dUse['dCrv'] * _fac)
        
        
        mTarget.p_position = _new
    
    
    
    #pprint.pprint(vars())

    return _res

def relativePointDat_get(point, pStart,pEnd):
    _str_func = 'relativePointDat_get'
    log.debug(log_start(_str_func))
    
    _res = {}
    
    
    
    
    return _res



d_shapeDat_options = {"form":['formHandles'],
                      "loft":['loftHandles','loftShapes'],
                     }
d_shapeDatShort = {'formHandles':'handles',
                   "loftHandles":'handles',
                   'loftShapes':'shapes'}
d_shapeDatLabels = {'formHandles':{'ann':"Setup expected qss sets", 'label':'form'},
                    'loftHandles':{'ann':"Wire for mirroring", 'label':'loft'},
                    'loftShapes':{'ann':"Connect bind joints to rig joints", 'label':'shapes'},}
         
class uiShapeDat(ui):
    USE_Template = 'cgmUITemplate'
    TOOLNAME = "uiShapeDat"
    WINDOW_NAME = "ShapeDatUI"
    WINDOW_TITLE = 'ShapeDat | {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = False
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 300,400
    
    _datClass = ShapeDat
    _datTypes = ['cgmShapeDat']
    
    #def insert_init(self,*args,**kws):
    #    self._loadedFile = ""
    #    self.dat = None
    
    #def __init__(self):
    #    super(ui, self).__init__()
    #    self.dat = None
        
        
    #def build_menus(self):
    #    self.uiMenu_FileMenu = mUI.MelMenu(l='File', pmc = cgmGEN.Callback(self.buildMenu_file))
    #    self.uiMenu_SetupMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_setup))

    def buildMenu_setup(self):pass
    
    
    def uiStatus_refresh(self,string = None):
        _str_func = 'uiStatus_refresh[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))
        
        if not self.uiDat.dat:
            self.uiStatus_top(edit=True,bgc = SHARED._d_gui_state_colors.get('help'),label = 'No Data')
            #self.uiStatus_bottom(edit=True,bgc = SHARED._d_gui_state_colors.get('warning'),label = 'No Data')
            
            self.uiData_base(edit=True,vis=0)
            self.uiData_base.clear()
            
        else:
            self.uiData_base.clear()
            
            _base = self.uiDat.dat['base']
            if not string:
                string = "Source: {}".format(_base['source'])
            self.uiStatus_top(edit=True,bgc = SHARED._d_gui_state_colors.get('connected'),label = string)
            
            self.uiData_base(edit=True,vis=True)
            
            mUI.MelLabel(self.uiData_base, label = "Base", h = 13, 
                         ut='cgmUIHeaderTemplate',align = 'center')
            
            for a in ['type','blockType','shapers','subs']:
                mUI.MelLabel(self.uiData_base, label = "{} : {}".format(a,self.uiDat.dat['base'].get(a)),
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
        
        #sDat = dat_get(mBlock)
        #self.uiDat.dat = sDat
        
        self.uiDat.mBlock = mBlock
        self.uiDat.get()        
        
        self.uiStatus_refresh(string = "Scene: '{}'".format(mBlock.p_nameBase))
        if _sel:mc.select(_sel)
        
    def uiFunc_dat_set(self,mBlocks = None,**kws):
        _str_func = 'uiFunc_dat_set[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))        
        
        if not mBlocks:
            mBlocks = BLOCKGEN.block_getFromSelected(multi=True)
            
        if not mBlocks:
            return log.error("No blocks selected")
        
        if not self.uiDat.dat:
            return log.error("No dat loaded")
            
        
        if not kws:
            kws = {}
            for k,cb in list(self._dCB_reg.items()):
                kws[k] = cb.getValue()
            
            pprint.pprint(kws)
        
        
        
        mc.undoInfo(openChunk=True)

        
        for mBlock in mBlocks:
            log.info(log_sub(_str_func,mBlock.mNode))
            try:shapeDat_set(mBlock, self.uiDat.dat, **kws)
            except Exception as err:
                log.error("{} | err: {}".format(mBlock.mNode, err))
                    
        mc.undoInfo(closeChunk=True)
        
        return
        for d in ['form','loft']:
            l = d_shapeDat_options[d]
            mUI.MelLabel(_inside, label = '{0}'.format(d.upper()), h = 13, 
                         ut='cgmUIHeaderTemplate',align = 'center')
            for k in l:
                d_dat = d_shapeDatLabels.get(k,{})
                
        for d,l in list(MRSBATCH.d_mrsPost_calls.items()):
            for k in l:# _l_post_order:
                log.debug("|{0}| >> {1}...".format(_str_func,k)+'-'*20)
                
                #self._dCB_reg[k].getValue():#self.__dict__['cgmVar_mrsPostProcess_{0}'.format(k)].getValue():
                l_join.insert(2,"'{0}' : {1} ,".format(k,int(self._dCB_reg[k].getValue())))        
        
    
    def uiFunc_dat(self,mode='Select Source'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.uiDat.dat:
            return log.error("No dat loaded selected")
        
        if mode == 'Select Source':
            mc.select(self.uiDat.dat['base']['source'])
    
    def uiFunc_printDat(self,mode='all'):
        _str_func = 'uiFunc_print[{0}]'.format(self.__class__.TOOLNAME)            
        log.debug("|{0}| >>...".format(_str_func))  
        
        if not self.uiDat.dat:
            return log.error("No dat loaded selected")    
        
        sDat = self.uiDat.dat
        
        print((log_sub(_str_func,mode)))
        if mode == 'all':
            pprint.pprint(self.uiDat.dat)
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
        _MainForm = mUI.MelFormLayout(parent,ut='cgmUITemplate')#mUI.MelColumnLayout(ui_tabs)
        _inside = mUI.MelScrollLayout(_MainForm)
        """
        #SetHeader = cgmUI.add_Header('{0}'.format(_strBlock))
        self.uiStatus_top = mUI.MelButton(_inside,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = SHARED._d_gui_state_colors.get('warning'),
                                         label = 'No Data',
                                         h=20)                
        """
        #>>>Objects Load Row ---------------------------------------------------------------------------------------
        _row_status = mUI.MelHSingleStretchLayout(_inside)
        mUI.MelSpacer(_row_status, w = 2)
        
        self.uiStatus_top = mUI.MelButton(_row_status,
                                         vis=True,
                                         c = lambda *a:mc.evalDeferred(cgmGEN.Callback(self.uiFunc_dat_get)),
                                         bgc = CORESHARE._d_gui_state_colors.get('help'),
                                         label = 'No Data',
                                         h=20)
        mUI.MelIconButton(_row_status,
                          ann='Clear the loaded file link',
                          image=os.path.join(CGMUI._path_imageFolder,'clear.png') ,
                          w=25,h=25,
                          bgc = CGMUI.guiButtonColor,
                          c = lambda *a:self.uiStatus_fileClear())
        mUI.MelIconButton(_row_status,
                          ann='Open Dir',
                          image=os.path.join(CGMUI._path_imageFolder,'find_file.png') ,
                          w=25,h=25,
                          bgc = CGMUI.guiButtonColor,
                          c = lambda *a:self.uiStatus_fileExplorer())        
        
        _row_status.setStretchWidget(self.uiStatus_top)
        mUI.MelSpacer(_row_status, w = 2)
        _row_status.layout()                
        

  
        self.uiPB_test=None
        self.uiPB_test = mc.progressBar(vis=False)

        
    
        
        
                
        #checkboxes frame...------------------------------------------------------------
        self._dCB_reg = {}
        for d in ['form','loft']:
            l = d_shapeDat_options[d]
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
                            ut = 'cgmUITemplate',
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
                                    useTemplate = 'cgmUIHeaderTemplate',
                                    expandCommand = lambda:mVar_frame.setValue(0),
                                    collapseCommand = lambda:mVar_frame.setValue(1)
                                    )	
        self.uiFrame_data = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
        
        
        self.uiData_base = mUI.MelColumn(self.uiFrame_data ,useTemplate = 'cgmUISubTemplate',vis=False) 

        mUI.MelLabel(self.uiFrame_data, label = "Select", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        
        for util in ['Select Source']:
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_dat,util),
                          ann="...",
                          label=util,
                          ut='cgmUITemplate',
                          h=20)                            
        
        
        
        
        mUI.MelLabel(self.uiFrame_data, label = "PPRINT", h = 13, 
                     ut='cgmUIHeaderTemplate',align = 'center')
        
        for a in ['settings','base','formHandles','loftHandles','sub','subShapes','subRelative','all']:
            mUI.MelButton(self.uiFrame_data,
                          c = cgmGEN.Callback(self.uiFunc_printDat,a),
                          ann="...",
                          label=a,
                          ut='cgmUITemplate',
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

        
global DAT_OPTIONS
DAT_OPTIONS = None

#def get_modules_dict(update=False):
#    return get_modules_dat(update)[0]

#@cgmGEN.Timer
def get_ext_options(update = False,debug=None, path= None, skipRoot = True, extensions = ['cgmBlockConfig','cgmBlockDat','cgmShapeDat']):
    """
    Data gather for available blocks.

    :parameters:

    :returns
        _d_modules, _d_categories, _l_unbuildable
        _d_modules(dict) - keys to modules
        _d_categories(dict) - categories to list of entries
        _l_unbuildable(list) - list of unbuildable modules
        
    
    """
    _str_func = 'get_ext_options'    
    global DAT_OPTIONS

    if DAT_OPTIONS and not update:
        log.debug("|{0}| >> passing buffer...".format(_str_func))          
        return DAT_OPTIONS
    
    
    DAT_OPTIONS = CGMDAT.get_ext_options(update,debug,path,skipRoot,extensions)