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
import cgm.images as cgmImages
mImagesPath = PATHS.Path(cgmImages.__path__[0])

mUI = cgmUI.mUI

__version__ = cgmGEN.__RELEASESTRING
_colorGood = CORESHARE._d_colors_to_RGB['greenWhite']
_colorBad = CORESHARE._d_colors_to_RGB['redWhite']

from cgm.core import cgm_General as cgmGEN
log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start


class data(object):
    '''
    Class to handle blockDat data. Replacing existing block dat which storing on the node is not ideal
    '''    
    
    def __init__(self, mBlock = None, filepath = None, **kws):
        """

        """
        _str_func = 'data.__buffer__'
        log.debug(log_start(_str_func))
        
        self.str_filepath = None
        self.data = {}
        self.mBlock = None
        
        
    def get(self, mBlock = None):
        _str_func = 'data.get'
        log.debug(log_start(_str_func))
        
        
        
        
    
    
    def set(self, mBlock = None):
        _str_func = 'data.set'
        log.debug(log_start(_str_func))
        

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
    _d = {#"name":_short, 
          "blockType":self.blockType,
          "blockState":self.getEnumValueString('blockState'),
          "baseName":self.getMayaAttr('cgmName'), 
          'position':self.p_position,
          'baseSize':self.getState(False),
          'orient':self.p_orient,
          'scale':self.scale,
          'blockScale':ATTR.get(_short,'blockScale'),
          "version":self.version, 
          "ud":{}
          }   
    
    
    #Get attr sets...--------------------------------------------------------------------------
    _d = self.mBlock.atUtils('uiQuery_getStateAttrDict',0,0)
    
    self._d_attrFields = {}
    
    _short = mBlock.mNode
    
    _keys = _d.keys()
    _keys.sort()
    l_order =['define','profile','basic','name',
              'form','proxySurface','prerig',
              'skeleton',
              'rig','squashStretch']
    l_order.reverse()
    
    for k in l_order:
        if k in _keys:
            _keys.remove(k)
            _keys.insert(0,k)
            
    l_end = ['data','wiring','advanced']
    for k in l_end:
        if k in _keys:
            _keys.remove(k)
            _keys.append(k)
    
    
    
    """
    if self.getShapes():
        _d["size"] = POS.get_axisBox_size(self.mNode,False),
    else:
        _d['size'] = self.baseSize"""
    
        
    if self.getMessage('orientHelper'):
        _d['rootOrientHelper'] = self.orientHelper.rotate
    """
    _d['define'] = blockDat_getControlDat(self,'define',report)#self.getBlockDat_formControls()
    
    if _blockState_int >= 1:
        _d['form'] = blockDat_getControlDat(self,'form',report)#self.getBlockDat_formControls()

    if _blockState_int >= 2:
        _d['prerig'] = blockDat_getControlDat(self,'prerig',report)#self.getBlockDat_prerigControls() 

    for a in self.getAttrs(ud=True):
        if a not in _l_udMask:
            try:
                _type = ATTR.get_type(_short,a)
                if _type in ['message']:
                    continue
                elif _type == 'enum':
                    _d['ud'][a] = ATTR.get_enumValueString(_short,a)                    
                else:
                    _d['ud'][a] = ATTR.get(_short,a)
            except Exception,err:
                log.error("Failed to query attr: {0} | type: {1} | err: {2}".format(a,_type,err))
    
    _d['ud']['baseSize'] = baseSize_get(self)
    """
    if report:
        pprint.pprint(_d)
        #cgmGEN.walk_dat(_d,'[{0}] blockDat'.format(self.p_nameShort))
    return _d






class config(object):
    '''
    Class to handle skin data. Utilizes red9.packages.ConfigObj for storage format. Storing what might be an excess of info
    to make it more useful down the road for applying skinning data to meshes that don't have the same vert counts or joint counts.
    
    :param sourchMesh: Mesh to export data from
    :param targetMesh: Mesh to import data to
    :param filepath: File to read on call or via self.read() call to browse to one
    
    '''    

    #_geoToComponent = {'mesh':'vtx'}
    
    
    def __init__(self, project = None, filepath = None, **kws):
        """

        """        
        self.str_filepath = None
        self.assetDat = []
        
        #self.d_env = {}#cgmGEN.get_mayaEnviornmentDict()
        #self.d_env['file'] = mc.file(q = True, sn = True)
        
        for k,d in PU._dataConfigToStored.iteritems():
            log.debug("initialze: {0}".format(k))
            self.__dict__[d] = {}
        
        if not self.d_project.get('name') and project:
            self.d_project['name'] = project
            
        if filepath is not None:
            try:self.read(filepath)
            except Exception,err:log.error("data Filepath failed to read | {0}".format(err))

    def write(self, filepath = None, update = False):
        '''
        Write the Data ConfigObj to file
        '''
        _str_func = 'data.write'
        log.debug("|{0}| >>...".format(_str_func))
        
        if update:
            filepath = self.str_filepath
            
        filepath = self.validateFilepath(filepath)
        if not filepath:
            log.warning('Invalid path: {0}'.format(filepath))
            
            return False
        log.warning('Write to: {0}'.format(filepath))
            
        ConfigObj = configobj.ConfigObj(indent_type='\t')
        ConfigObj['configType']= 'cgmProject'
        
        for k,d in PU._dataConfigToStored.iteritems():
            _dat = self.__dict__.get(d,None)
            if _dat:
                log.debug("Dat: {0}".format(k))
                #pprint.pprint(self.__dict__[d])
                #print (self.__dict__[d])
                ConfigObj[k] = _dat
                log.debug("...")
        
        ConfigObj['assetDat'] = self.assetDat
        
        log.debug('....')
        ConfigObj.filename = filepath
        ConfigObj.write()
        
        #if update:
        self.str_filepath = filepath
        log.warning('Complete')
        return True
        
    def read(self, filepath = None, report = False):
        '''
        Read the Data ConfigObj from file and report the data if so desired.
        ''' 
        _str_func = 'data.read'
        log.debug("|{0}| >>...".format(_str_func))
        
        mPath = self.validateFilepath(filepath, fileMode = 1)
        
        if not mPath or not mPath.exists():            
            raise ValueError('Given filepath doesnt not exist : %s' % filepath)   
        
        _config = configobj.ConfigObj(mPath.asFriendly())
        #if _config.get('configType') != 'cgmSkinConfig':
            #raise ValueError,"This isn't a cgmSkinConfig config | {0}".format(filepath)
                
        for k in PU._dataConfigToStored.keys():
            log.debug("Checking...{0}".format(k))
            
            if _config.has_key(k):
                _d = _config[k]
                if issubclass(type(_d),dict):
                    self.__dict__[PU._dataConfigToStored[k]] = {}
                    for _k,_item in _d.iteritems():
                        log.debug("{0} | {1}".format(_k,_item))
                        self.__dict__[PU._dataConfigToStored[k]][_k] = decodeString(_item)                    
                else:
                    self.__dict__[PU._dataConfigToStored[k]]  = _d
                #_v = decodeString(_config[k])
                #log.debug("{0} | {1}".format(type(_v),_v))
                #self.__dict__[PU._dataConfigToStored[k]] = _v
            else:
                log.debug("Config file missing section {0}".format(k))
        
        self.assetDat = decodeString(_config.get('assetDat',[]))
            
        if report:self.log_self()
        self.str_filepath = str(mPath)
        
        return True
    
    def log_self(self):
        #_d = copy.copy(self.__dict__)
        #print (_d)
        pprint.pprint(self.__dict__)
        
    
def decodeString(val):
    '''
    From configObj the return is a string, we want to encode
    it back to it's original state so we pass it through this
    '''
    try:
        # configobj section handler to push back to native dict
        try:
            from Red9.packages.configobj import Section
            if issubclass(type(val), Section):
                return val.dict()
        except:
            log.debug('failed to convert configObj section %s' % val)
        
        if cgmValid.isListArg(val):
            return [decodeString(v) for v in val]
        
        if not issubclass(type(val), str) and not type(val) == unicode:
            # log.debug('Val : %s : is not a string / unicode' % val)
            # log.debug('ValType : %s > left undecoded' % type(val))
            return val
        if val == 'False' or val == 'True' or val == 'None':
            # log.debug('Decoded as type(bool)')
            return eval(val)
        elif val == '[]':
            # log.debug('Decoded as type(empty list)')
            return eval(val)
        elif val == '()':
            # log.debug('Decoded as type(empty tuple)')
            return eval(val)
        elif val == '{}':
            # log.debug('Decoded as type(empty dict)')
            return eval(val)
        elif (val[0] == '[' and val[-1] == ']'):
            # log.debug('Decoded as type(list)')
            return eval(val)
        elif (val[0] == '(' and val[-1] == ')'):
            # log.debug('Decoded as type(tuple)')
            return eval(val)
        elif (val[0] == '{' and val[-1] == '}'):
            # log.debug('Decoded as type(dict)')
            return eval(val)
        try:
            encoded = int(val)
            # log.debug('Decoded as type(int)')
            return encoded
        except:
            pass
        try:
            encoded = float(val)
            # log.debug('Decoded as type(float)')
            return encoded
        except:
            pass
    except:
        return
    # log.debug('Decoded as type(string)')
    return val
    
