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
from cgm.core.lib import rigging_utils as CORERIG
reload(CORERIG)
from cgm.core.lib import snap_utils as SNAP
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.position_utils as POS
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.lib.locator_utils as LOC
for m in DIST,POS,MATH,CONSTRAINT,LOC:
    reload(m)
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = 'alpha.07032017'
__autoTemplate__ = False


#>>>Attrs ----------------------------------------------------------------------------------------------------
_l_coreNames = ['pelvis','spine','sternum',]

l_attrsStandard = ['side',
                   'position',
                   'proxyType',
                   'hasRootJoint',
                   'buildIK',
                   'loftShape',
                   'loftSplit',
                   'loftSides',
                   'loftDegree',
                   'numberControls',
                   'baseNames',
                   'numberJoints',
                   'customStartOrientation',
                   'moduleTarget',]

#d_attrsToMake = {'puppetName':'string'}

d_defaultSettings = {'version':__version__,
                     'baseSize':1,
                     'attachPoint':'base',
                     'buildIK':True,
                     'numberControls':3,
                     'loftSides':3,
                     'loftSplit':4,
                     'loftDegree':'cubic',
                     'loftShape':'square',
                     'numberJoints':4,
                     'baseNames':['pelvis','spine','shoulders'],#...our datList values
                     'proxyType':1}

#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    _short = self.mNode
    #ATTR.set(_short,'translate',[0,0,0])
    #ATTR.set(_short,'rotate',[0,0,0])
    #ATTR.set_standardFlags(self.mNode,attrs=['translate','rotate','sx','sz'])
    #for a in ['x','z']:
        #ATTR.connect("{0}.sy".format(_short),"{0}.s{1}".format(_short,a))
    #ATTR.set_alias(_short,'sy','blockScale')

#=============================================================================================================
#>> Template
#=============================================================================================================    
def templateDelete(self):
    _str_func = 'templateDelete'    
    log.info("|{0}| >> ...".format(_str_func))                            
    for link in ['orientHelper','loftCurve']:
        if self.getMessage(link):
            log.info("|{0}| >> deleting link: {1}".format(_str_func,link))                        
            mc.delete(self.getMessage(link))
    return True

def is_template(self):
    if not self.getMessage('templateNull'):
        return False
    return True

def template(self):
    _str_func = 'template'
    
    _short = self.p_nameShort
    _size = self.baseSize
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
    
    log.info("|{0}| >> [{1}] | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))            

    #Create temple Null  ==================================================================================
    if not self.getMessage('templateNull'):
        str_templateNull = CORERIG.create_at(self.mNode)
        templateNull = cgmMeta.validateObjArg(str_templateNull, mType = 'cgmObject',setClass = True)
        templateNull.connectParentNode(self, 'rigBlock','templateNull') 
        templateNull.doStore('cgmName', self.mNode)
        templateNull.doStore('cgmType','templateNull')
        templateNull.doName()
        templateNull.p_parent = self
        templateNull.setAttrFlags()
    else:
        templateNull = self.templateNull
        
    #Our main rigBlock shape =================================================================================
    #_crv = CURVES.create_controlCurve(self.mNode,shape='circleArrow',side = 'y+', sizeMode = 'fixed', size = _size * 14)
    #CORERIG.colorControl(_crv,_side,'main')
    #CORERIG.shapeParent_in_place(self.mNode,_crv,False)    
    mHandleFactory = self.asHandleFactory(self.mNode)
    mHandleFactory.rebuildAsLoftTarget(self.getEnumValueString('loftShape'), _size, shapeDirection = 'y+')
    mBaseLoftCurve = self.loftCurve
    mBaseLoftCurve.p_parent = templateNull
    
    
    #Orientation helper ======================================================================================
    """orientHelper = CURVES.create_controlCurve(self.mNode,'circleArrow1',  direction= 'y+', sizeMode = 'fixed', size = _size * 2.4)
    mOrientCurve = cgmMeta.validateObjArg(_orientHelper, mType = 'cgmObject',setClass=True)
    
    #self.copyAttrTo(_baseNameAttrs[-1],mTopCurve.mNode,'cgmName')
    #mOrientCurve.doStore(self.mNode,'cgmName')
    self.copyAttrTo(_baseNameAttrs[1],mOrientCurve.mNode,'cgmName',driven='target')
    mOrientCurve.doStore('cgmType','orientHandle')
    mOrientCurve.doName()    
    
    mOrientCurve.p_parent = self
    """
    mOrientCurve = mHandleFactory.addOrientHelper(baseSize = _size, setAttrs = {'tz': - _size * .8})
    self.copyAttrTo(_baseNameAttrs[1],mOrientCurve.mNode,'cgmName',driven='target')
    mOrientCurve.doName()    
    mOrientCurve.setAttrFlags(['rz','rx','translate','scale','v'])
    mOrientCurve.p_parent = templateNull
    CORERIG.colorControl(mOrientCurve.mNode,_side,'sub')
    #mOrientCurve.connectParentNode(self.mNode,'handle','orientHelper')
    
    #Create attatch points ----------------------------------------------------------------------------------

    #Create joint template ----------------------------------------------------------------------------------

    #>>> Top curve ==========================================================================================
    mTopCurve = mHandleFactory.buildBaseShape(self.getEnumValueString('loftShape'), _size, shapeDirection = 'y+')
    mTopCurve.p_parent = templateNull
    mTopCurve.translate = 0,_size*3,0        
    
    self.copyAttrTo(_baseNameAttrs[-1],mTopCurve.mNode,'cgmName',driven='target')
    mTopCurve.doStore('cgmType','blockHandle')
    mTopCurve.doName()
    
    #Convert to loft curve setup ----------------------------------------------------
    mHandleFactory = self.asHandleFactory(mTopCurve.mNode)
    mHandleFactory.rebuildAsLoftTarget(self.getEnumValueString('loftShape'), _size, shapeDirection = 'y+')
    
    mc.makeIdentity(mTopCurve.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned

    mTopCurve.setAttrFlags(['rotate','tx','tz'])
    mc.transformLimits(mTopCurve.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
    mTopLoftCurve = mTopCurve.loftCurve
    
    CORERIG.colorControl(mTopCurve.mNode,_side,'main',transparent = True)
    
    #>>Loft Mesh ==================================================================================================
    targets = [mBaseLoftCurve.mNode, mTopLoftCurve.mNode]
    _res_body = mc.loft(targets, o = True, d = 3, po = 1 )
    mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
    _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)
    _tessellate = _inputs[0]
    
    _d = {'format':2,#General
          'polygonType':1,#'quads',
          'uNumber': 1 + self.numberControls}
    
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)    
        
    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 1
    _arg = "{0}.numberOfControlsOut = {1} + 1".format(mBaseLoftCurve.p_nameShort,
                                                      self.getMayaAttrString('numberControls','short'))
                                                      
    NODEFACTORY.argsToNodes(_arg).doBuild()
    
    ATTR.connect("{0}.numberOfControlsOut".format(mBaseLoftCurve.mNode), "{0}.uNumber".format(_tessellate))
    
    ATTR.connect("{0}.loftSides".format(self.mNode), "{0}.vNumber".format(_tessellate))
    
    mLoft.p_parent = templateNull
    mLoft.resetAttrs()
    
    mLoft.doStore('cgmName',self.mNode)
    mLoft.doStore('cgmType','controlsApprox')
    mLoft.doName()
    
    #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
    #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;

    mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
    #Color our stuff...
    CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = True)
    
    mLoft.inheritsTransform = 0
    for s in mLoft.getShapes(asMeta=True):
        s.overrideDisplayType = 1
        
    self.msgList_connect('templateHandles',[mTopCurve.mNode])
    
    return True
"""





    #...........................................
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
	mBaseVisualCurve       = ControlCurve( name=self.name+"_orientation_crv", curveShape=CurveShape.ARROW, size=.2 )
	mBaseVisualCurve.cvs   = [x.position + Vector3(0,0,.2) for x in mBaseVisualCurve.cvs] # offset CVs so pivot is at base
	mBaseVisualCurve.color = rigOptions['colors']['main'][self.side]

	self.templateOrientation = [mBaseVisualCurve, baseOrientCurve]

	# scale orientation curve with end translation
	mBaseVisualCurve.ConnectAttrIn("sx", end.GetAttrString("ty"))
	mBaseVisualCurve.ConnectAttrIn("sy", end.GetAttrString("ty"))
	mBaseVisualCurve.ConnectAttrIn("sz", end.GetAttrString("ty"))

	mBaseVisualCurve.LockTransform()

	# parent
	base.parent        = self._template
	end.parent         = base

	end.LockTransform(translate=False)
	end.LockAttribute('tx')
	end.LockAttribute('tz')

	mBaseVisualCurve.parent = base"""



#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    _str_func = 'prerig'
    
    _short = self.p_nameShort
    _size = self.baseSize
    _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'baseNames')
    
    _side = 'center'
    if self.getMayaAttr('side'):
        _side = self.getEnumValueString('side')
    
    log.info("|{0}| >> [{1}] | baseSize: {2} | side: {3}".format(_str_func,_short,_size, _side))     
        
    self._factory.module_verify()  
    
    if self.numberControls<3:
        raise ValueError,"You really need more than 3 handles for a spine. Perhaps another block type."
    
    #Create preRig Null  ==================================================================================
    if not self.getMessage('prerigNull'):
        str_prerigNull = CORERIG.create_at(self.mNode)
        mPrerigNull = cgmMeta.validateObjArg(str_prerigNull, mType = 'cgmObject',setClass = True)
        mPrerigNull.connectParentNode(self, 'rigBlock','prerigNull') 
        mPrerigNull.doStore('cgmName', self.mNode)
        mPrerigNull.doStore('cgmType','prerigNull')
        mPrerigNull.doName()
        mPrerigNull.p_parent = self
        mPrerigNull.setAttrFlags()
    else:
        mPrerigNull = self.prerigNull    
    
    
    ml_templateHandles = self.msgList_get('templateHandles')
    
    
    #>>New handles ==================================================================================================
    mHandleFactory = self.asHandleFactory(self.mNode)   
    _vec_root_up = self.getAxisVector('z-')
    
    #Get positions
    #DIST.get_pos_by_axis_dist(obj, axis)
    mEndHandle = ml_templateHandles[-1]
    _pos_me = self.p_position
    _pos_end = mEndHandle.p_position
    
    _vec = MATH.get_vector_of_two_points(_pos_me, _pos_end)
    _offsetDist = DIST.get_distance_between_points(_pos_me,_pos_end) / self.numberControls
    _l_pos = [ DIST.get_pos_by_vec_dist(_pos_me, _vec, (_offsetDist * i)) for i in range(self.numberControls)] + [_pos_end]
    
    ml_handles = []
    for i,p in enumerate(_l_pos[1:-1]):
        mHandle = mHandleFactory.buildBaseShape(self.getEnumValueString('loftShape'), _size, shapeDirection = 'y+')
        ml_handles.append(mHandle)
        mHandle.p_position = p
        SNAP.aim_atPoint(mHandle.mNode,_l_pos[i+1], 'y+','z-', vectorUp = _vec_root_up)
        
        self.copyAttrTo(_baseNameAttrs[1],mHandle.mNode,'cgmName',driven='target')
        mHandle.doStore('cgmType','blockHandle')
        mHandle.doStore('cgmIterator',i)
        mHandle.doName()
        
        mHandle.p_parent = mPrerigNull
        mGroup = mHandle.doGroup(True,True,asMeta=True)
        _vList = DIST.get_normalizedWeightsByDistance(mGroup.mNode,[self.mNode,mEndHandle.mNode])
        _point = mc.pointConstraint([self.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
        _scale = mc.scaleConstraint([self.mNode,mEndHandle.mNode],mGroup.mNode,maintainOffset = False)#Point contraint loc to the object
        
        for c in _point,_scale:
            CONSTRAINT.set_weightsByDistance(c[0],_vList)
        
        #Convert to loft curve setup ----------------------------------------------------
        mHandleFactory = self.asHandleFactory(mHandle.mNode)
        
        mc.makeIdentity(mHandle.mNode,a=True, s = True)#...must freeze scale once we're back parented and positioned
        
        mHandleFactory.rebuildAsLoftTarget(self.getEnumValueString('loftShape'), _size, shapeDirection = 'y+')
    
        #mTopCurve.setAttrFlags(['rotate','tx','tz'])
        #mc.transformLimits(mTopCurve.mNode,  tz = [-.25,.25], etz = [1,1], ty = [.1,1], ety = [1,0])
        #mTopLoftCurve = mTopCurve.loftCurve
        
        CORERIG.colorControl(mHandle.mNode,_side,'sub',transparent = True)        
        #LOC.create(position = p)
        
    ml_handles.insert(0,self)
    ml_handles.append(mEndHandle)
    
    #>>Loft Mesh ==================================================================================================
    targets = [mObj.loftCurve.mNode for mObj in ml_handles]
    
    _res_body = mc.loft(targets, o = True, d = 3, po = 1 )
    mLoft = cgmMeta.validateObjArg(_res_body[0],'cgmObject',setClass= True)
    _inputs = mc.listHistory(mLoft.mNode,pruneDagObjects=True)
    _tessellate = _inputs[0]
    _loft = _inputs[1]
    log.info("|{0}| loft inputs: {1}".format(_str_func,_inputs)) 
    _d = {'format':2,#General
          'polygonType':1,#'quads',
          'uNumber': 1 + len(ml_handles)}
    
    for a,v in _d.iteritems():
        ATTR.set(_tessellate,a,v)    
        
    mLoft.overrideEnabled = 1
    mLoft.overrideDisplayType = 2
    
    mLoft.p_parent = mPrerigNull
    mLoft.resetAttrs()
    
    mLoft.doStore('cgmName',self.mNode)
    mLoft.doStore('cgmType','shapeApprox')
    mLoft.doName()
    
    #mc.polySetToFaceNormal(mLoft.mNode,setUserNormal = True)
    #polyNormal -normalMode 0 -userNormalMode 1 -ch 1 spine_block_controlsApproxShape;

    mc.polyNormal(mLoft.mNode, normalMode = 0, userNormalMode = 1, ch=1)
    
    #Color our stuff...
    CORERIG.colorControl(mLoft.mNode,_side,'main',transparent = False)
    
    mLoft.inheritsTransform = 0
    for s in mLoft.getShapes(asMeta=True):
        s.overrideDisplayType = 2    
        
    #...wire some controls
    _arg = "{0}.out_vSplit = {1} + {2} + 1".format(targets[0],
                                                  self.getMayaAttrString('numberControls','short'),
                                                  self.getMayaAttrString('loftSplit'))

    NODEFACTORY.argsToNodes(_arg).doBuild()
    #rg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)
    _arg = "{0}.out_degree = if {1} == 0:1 else 3".format(targets[0],
                                                          self.getMayaAttrString('loftDegree','short'))
  
    NODEFACTORY.argsToNodes(_arg).doBuild()    

    ATTR.connect("{0}.out_vSplit".format(targets[0]), "{0}.uNumber".format(_tessellate))
    ATTR.connect("{0}.loftSides".format(self.mNode), "{0}.vNumber".format(_tessellate)) 
    
    ATTR.connect("{0}.out_degree".format(targets[0]), "{0}.degree".format(_loft))    
    #ATTR.copy_to(_loft,'degree',self.mNode,'loftDegree',driven = 'source')
    #>>Joint placers ==================================================================================================
    
def prerigDelete(self):
    self.moduleTarget.delete()
    self.prerigNull.delete()
    return True   

def is_prerig(self):
    _str_func = 'is_prerig'
    _l_missing = []

    _d_links = {self : ['moduleTarget','prerigNull']}

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
"""def rig(self):    
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
    return True"""





















