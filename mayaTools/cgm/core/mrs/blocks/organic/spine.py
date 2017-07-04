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
#>> Block data
#=============================================================================================================
__version__ = 'alpha.07032017'
__autoTemplate__ = False

_l_coreNames = ['pelvis','spine','sternum',]

l_attrsStandard = ['direction',
                   'position',
                   'proxyType',
                   'hasRootJoint',
                   'buildIK',
                   'numberControls',
                   'coreNames',
                   'numberJoints',
                   'customStartOrientation',
                   'moduleTarget',]

#d_attrsToMake = {'puppetName':'string'}

d_defaultSettings = {'version':__version__,
                     'baseSize':1,
                     'attachPoint':'base',
                     'buildIK':True,
                     'numberControls':3,
                     'numberJoints':4,
                     'coreNames':['pelvis','spine','sternum','shoulders'],
                     #'basicShape':'cube',
                     'proxyType':1}


#=============================================================================================================
#>> Template
#=============================================================================================================
def template(self):
    #Let's generate some names
    
    
    
    """
    # Create attach points	
		attachBase            = Transform(name=self.name+"_attachToBase")
		attachBase.parent     = self._attach
		
		attachEnd             = Transform(name=self.name+"_attachToEnd")
		attachEnd.parent      = self._attach
		
		self.attachPoints     = [ attachBase, attachEnd ]

		size = self.size

		# create joint template
		base        = Joint(name=self.name+"_hip_tmp", forceCreate=True)
		end         = Joint(name=self.name+"_shoulder_tmp", init_position = Vector3(0,size*10,0), forceCreate=True)
		
		base.radius = size
		end.radius  = size

		base.LockTransform(translate=False, rotate=False)

		self.templatePositions = [base, end]

		# create start orientation curve
		baseOrientCurve                 = ControlCurve( name=self.name+"_baseOrient_crv", curveShape=CurveShape.SPHERE, size=size*.5 )
		baseOrientCurve.color           = Color.BLUE

		animOrientCurve                 = ControlCurve( name=self.name+"_animOrient_crv", curveShape=CurveShape.ARROW, size=size )
		animOrientCurve.cvs             = [x.position + Vector3(0,0,size) for x in animOrientCurve.cvs] # offset CVs so pivot is at base
		animOrientCurve.color           = Color.BLUE
		
		animOrientCurveUp               = ControlCurve( name=self.name+"_animOrientUp_crv", curveShape=CurveShape.ARROW, size=size )
		animOrientCurveUp.cvs           = [x.position + Vector3(0,0,size) for x in animOrientCurveUp.cvs] # offset CVs so pivot is at base
		animOrientCurveUp.color         = Color.GREEN
		animOrientCurveUp.eulerAngles   = Vector3(-90,0,0)
		
		animOrientCurve.parent          = baseOrientCurve
		animOrientCurveUp.parent        = baseOrientCurve

		animOrientCurve.localPosition   = Vector3(0,0,0)
		animOrientCurveUp.localPosition = Vector3(0,0,0)

		baseOrientCurve.parent = base
		baseOrientCurve.localPosition   = Vector3(0,0,0)
		baseOrientCurve.eulerAngles     = Vector3(0,0,0)

		baseOrientCurve.ConnectAttrIn('v', self.GetAttrString('customStartOrientation'))
		#animOrientCurveUp.ConnectAttrIn('v', self.GetAttrString('customStartOrientation'))

		animOrientCurve.LockTransform()
		animOrientCurveUp.LockTransform()
		baseOrientCurve.LockTransform(rotate=False)

		# create orientation curve
		orientCurve       = ControlCurve( name=self.name+"_orientation_crv", curveShape=CurveShape.ARROW, size=.2 )
		orientCurve.cvs   = [x.position + Vector3(0,0,.2) for x in orientCurve.cvs] # offset CVs so pivot is at base
		orientCurve.color = rigOptions['colors']['main'][self.side]

		self.templateOrientation = [orientCurve, baseOrientCurve]

		# scale orientation curve with end translation
		orientCurve.ConnectAttrIn("sx", end.GetAttrString("ty"))
		orientCurve.ConnectAttrIn("sy", end.GetAttrString("ty"))
		orientCurve.ConnectAttrIn("sz", end.GetAttrString("ty"))

		orientCurve.LockTransform()

		# parent
		base.parent        = self._template
		end.parent         = base
		
		end.LockTransform(translate=False)
		end.LockAttribute('tx')
		end.LockAttribute('tz')

		orientCurve.parent = base
    """

    return True

def templateDelete(self):
    pass#...handled in generic callmc.delete(self.getShapes())

def is_template(self):
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





            






 








