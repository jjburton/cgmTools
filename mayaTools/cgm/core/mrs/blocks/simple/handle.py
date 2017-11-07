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


import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.11062017'
__autoTemplate__ = False
__blockBit__ = True

#>>>Attrs ----------------------------------------------------------------------------------------------------
l_attrsStandard = ['side',
                   'position',
                   'hasRootJoint',
                   'hasJoint',
                   'basicShape',
                   'pivotLeft',
                   'pivotRight',
                   'pivotCenter',
                   'pivotForward',
                   'pivotBack',
                   'moduleTarget']

d_attrsToMake = {'puppetName':'string',
                 'shapeDirection':":".join(CORESHARE._l_axis_by_string),
                 'targetJoint':'messageSimple',
                 'rootJoint':'messageSimple'}

d_defaultSettings = {'version':__version__,
                     'hasRootJoint':False,
                     'hasJoint':True,
                     'baseSize':10,#cm
                     'basicShape':5,
                     'pivotLeft':True,
                     'pivotRight':True,
                     'pivotCenter':True,
                     'pivotForward':True,
                     'pivotBack':True,
                     'shapeDirection':2,
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
    self._factory.puppet_verify()    
    pass

def prerigDelete(self):
    try:self.moduleTarget.masterNull.delete()
    except Exception,err:
        for a in err:
            print a
    return True   

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
    return True
#=============================================================================================================
#>> rig
#=============================================================================================================
def rig(self):
    #
    self.moduleTarget._verifyMasterControl(size = DIST.get_size_byShapes(self,'max'))
    
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
            






 








