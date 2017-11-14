"""
------------------------------------------
cgm.core.mrs.blocks.simple.master
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
import cgm.core.cgm_General as cgmGEN
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as RIG
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
reload(ATTR)
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.math_utils as MATH
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.06142017'
__autoTemplate__ = True
__menuVisible__ = True
__baseSize__ = 10,10,10

#>>>Attrs ----------------------------------------------------------------------------------------------------
l_attrsStandard = ['hasRootJoint','moduleTarget','baseSize']

d_attrsToMake = {'puppetName':'string',
                 'rootJoint':'messageSimple'}

d_defaultSettings = {'version':__version__,
                     'puppetName':'NotBatman',
                     'hasRootJoint':True, 
                     'attachPoint':'end'}


#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    self.translate = 0,0,0
    self.rotate = 0,0,0
    self.setAttrFlags(attrs=['translate','rotate','sx','sz'])
    self.doConnectOut('sy',['sx','sz'])
    ATTR.set_alias(_short,'sy','blockScale')
    
#=============================================================================================================
#>> Template
#=============================================================================================================
def template(self):
    _size = MATH.average(self.baseSize) * 1.5
    _crv = CURVES.create_controlCurve(self.mNode,shape='squareOpen',direction = 'y+', sizeMode = 'fixed', size = _size)
    CORERIG.colorControl(_crv,'center','main',transparent = False) 
    
    mCrv = cgmMeta.validateObjArg(_crv,'cgmObject')
    l_offsetCrvs = []
    for shape in mCrv.getShapes():
        offsetShape = mc.offsetCurve(shape, distance = 1, ch=False )[0]
        CORERIG.colorControl(offsetShape,'center','sub',transparent = False) 
        l_offsetCrvs.append(offsetShape)
        
    for s in [_crv] + l_offsetCrvs:
        RIG.shapeParent_in_place(self.mNode,s,False)
        
    #RIG.shapeParent_in_place(self.mNode,_crv,False)
    
    
    return True

def templateDelete(self):
    self.setAttrFlags(attrs=['translate','rotate','sx','sz'], lock = False)
    
    pass#...handled in generic callmc.delete(self.getShapes())

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
    self.moduleTarget._verifyMasterControl(size = DIST.get_bb_size(self.mNode,True,'max') * 1.5)
    
    if self.hasRootJoint:
        if not is_skeletonized(self):
            build_skeleton(self)
            
        mJoint = self.getMessage('rootJoint', asMeta = True)[0]
        log.info(mJoint)
        mJoint.p_parent = self.moduleTarget.masterNull.skeletonGroup
    self.template = 1

def rigDelete(self):
    self.template = 0
    try:self.moduleTarget.masterControl.delete()
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
        raise Exception,err
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
def build_skeleton(self):
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
            






 








