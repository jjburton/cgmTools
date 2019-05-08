"""
------------------------------------------
cgm.core.mrs.blocks.simple.doodad
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
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as RIG
from cgm.core.lib import snap_utils as SNAP

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.06272017'
__autoForm__ = True
__menuVisible__ = False

#>>>Attrs ----------------------------------------------------------------------------------------------------
l_attrsStandard = ['side','position',
                   'proxyType','hasRootJoint',
                   'moduleTarget','basicShape']

d_defaultSettings = {'version':__version__,
                     'baseSize':1,
                     'attachPoint':'end',
                     'basicShape':'cube',
                     'side':'right',
                     'proxyType':1}


#=============================================================================================================
#>> Form
#=============================================================================================================
def form(self):
    _crv = CURVES.create_controlCurve(self.mNode, shape=self.getEnumValueString('basicShape'), 
                                      direction = 'z+', sizeMode = 'fixed', size = self.baseSize)
    RIG.shapeParent_in_place(self.mNode,_crv,False)
    return True

def formDelete(self):
    pass#...handled in generic callmc.delete(self.getShapes())

def is_form(self):
    if self.getShapes():
        return True
    return False

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    self._factory.module_verify()    
    

def prerigDelete(self):
    try:self.moduleTarget.delete()
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
    if self.hasRootJoint:
        mJoint = self.doCreateAt('joint')
        mJoint.parent = self.moduleTarget.masterNull.skeletonGroup
        mJoint.connectParentNode(self,'module','rootJoint')
    raise NotImplementedError,"Not done."

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
                _l_missing.append(_mPlug[0].p_nameBase + '.' + l)
                

    if _l_missing:
        log.info("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.info("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True





            






 








