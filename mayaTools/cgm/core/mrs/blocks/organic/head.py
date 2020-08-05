"""
------------------------------------------
cgm.core.mrs.blocks.simple.torso
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__MAYALOCAL = 'HEAD'

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
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta


import cgm.core.cgm_General as cgmGEN
from cgm.core.rigger import ModuleShapeCaster as mShapeCast

import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.cgmPy.path_Utils as cgmPATH
import cgm.core.mrs.assets as MRSASSETS
path_assets = cgmPATH.Path(MRSASSETS.__file__).up().asFriendly()

import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
#reload(MODULECONTROL)
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.lib.rigging_utils as CORERIG
from cgm.core.lib import snap_utils as SNAP
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.rig.joint_utils as JOINT
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.position_utils as POS
import cgm.core.lib.math_utils as MATH
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.lib.constraint_utils as CONSTRAINT
import cgm.core.mrs.lib.rigShapes_utils as RIGSHAPES
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES
import cgm.core.lib.locator_utils as LOC
import cgm.core.lib.list_utils as LISTS
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.shape_utils as SHAPES
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.rig.ik_utils as IK
import cgm.core.cgm_RigMeta as cgmRIGMETA
import cgm.core.mrs.lib.post_utils as MRSPOST
#for m in DIST,POS,MATH,IK,CONSTRAINT,LOC,BLOCKUTILS,RIGSHAPES,BUILDERUTILS,CORERIG,RAYS,JOINT,RIGCONSTRAINT:
#    #reload(m)
    
# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = '1.04302019'
__autoForm__ = False
__dimensions = __baseSize__ = [15.2, 23.2, 19.7]
__menuVisible__ = True

#These are our base dimensions. In this case it is for human
__dimensions_by_type = {'box':[22,22,22],
                        'human':[15.2, 23.2, 19.7]}

__l_rigBuildOrder__ = ['rig_dataBuffer',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_segments',                       
                       'rig_cleanUp']

d_wiring_skeleton = {'msgLinks':[],
                     'msgLists':['moduleJoints','skinJoints']}
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull'],
                   'msgLists':['prerigHandles']}
d_wiring_form = {'msgLinks':['formNull','noTransFormNull'],
                     'msgLists':['formHandles']}

_d_attrStateOn = {0:[],
                  1:['headRotate'],
                  2:['headAim'],
                  3:[],
                  4:[]}

_d_attrStateOff = {0:[],
                   1:[],
                   2:[],
                   3:[],
                   4:[]}

#=============================================================================================================
#>> AttrMask 
#=============================================================================================================
_d_attrStateOn = {0:[],
                  1:['hasJoint'],
                  2:['rotPivotPlace','basicShape'],
                  3:[],
                  4:[]}

d_attrProfileMask = {'box':['loftDegree','loftList','loftSetup','loftShape','loftSides','loftSplit',
                            'neckBuild','neckControls','neckDirection','neckIK',
                            'neckJoints','neckShapers','neckSubShapers',
                            'proxyGeoRoot','ribbonAim','ribbonConnectBy','ribbonParam',
                            'segmentMidIKControl',]}

for k in ['simple']:
    d_attrProfileMask[k] = d_attrProfileMask['box']

#=============================================================================================================
#>> Profiles 
#=============================================================================================================
d_build_profiles = {
    'unityLow':{'default':{'neckJoints':1,
                           'neckControls':1,
                           'neckBuild':True},
                'headNeck':{'neckJoints':1,
                         'neckControls':1}
                   },
    'unityMed':{'default':{'neckJoints':1},
               },
    'unityHigh':{'default':{'neckJoints':3,
                          'neckControls':1},
               },    
    'feature':{'default':{'numJoints':9,
                          'neckControls':5}
               }
}

d_block_profiles = {
    'box':{'neckShapers':2,
           'cgmName':'head',           
           'neckBuild':False,
           'baseAim':[0,-1,0],
           'baseUp':[0,0,-1],
           'baseSize':[22,22,22],
           'loftShape':'square',
           'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'end':[0,-1,0]},           
           },
    'simple':{'neckShapers':3,
              'cgmName':'head',              
              'neckBuild':False,
              'baseSize':[15.2, 23.2, 19.7],
              'loftShape':'wideUp',
              'neckDirection':'vertical',
              'proxyType':'geo',
              'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'end':[0,-1,0]},
               },
    'neck short':{'neckShapers':3,
                  'cgmName':'head',                  
                  'neckControls':1,
                  'neckShapers':2,
                  'neckBuild':True,
                  'neckIK':'ribbon',                  
                  'baseSize':[15.2, 23.2, 19.7],
                  'loftShape':'wideUp',
                  'neckDirection':'vertical',
                  'proxyType':'geo',
                  'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'end':[0,-1,0]},
                   },
    'neck long':{'neckShapers':4,
                 'neckControls':3,
                 'cgmName':'head',
                 'neckShapers':2,
                 'neckJoints':5,
                 'neckIK':'ribbon',
                 'neckBuild':True,
                 'baseSize':[15.2, 23.2, 19.7],
                 'loftShape':'wideUp',
                 'neckDirection':'vertical',
                 'proxyType':'geo',
                 'baseDat':{'rp':[0,0,-1],'up':[0,0,-1],'end':[0,-1,0]},
                  },}

#=============================================================================================================
#>>>Attrs 
#=============================================================================================================
l_attrsStandard = ['side',
                   'position',
                   #'baseUp',
                   #'baseAim',
                   #'hasRootJoint',
                   'attachPoint',
                   'attachIndex',
                   'nameList',
                   'loftSides',
                   'loftDegree',
                   'loftSplit',
                   'loftShape',
                   'loftList',
                   'ribbonParam',
                   #'ikSetup',
                   #'ikBase',
                   #'buildProfile',
                   'ikOrientToWorld',
                   'numSpacePivots',
                   'scaleSetup',
                   #'offsetMode',
                   'proxyDirect',
                   'proxyGeoRoot',
                   'spaceSwitch_direct',                   
                   'settingsDirection',
                   'visRotatePlane',
                   'visProximityMode',
                   'visLabels',
                   'moduleTarget',]

d_attrsToMake = {'visMeasure':'bool',
                 'proxyShape':'cube:sphere:cylinder',
                 'proxyType':'base:geo',
                 'headAim':'bool',
                 'headRotate':'double3',
                 'loftSetup':'default:loftList',
                 
                 'squashMeasure' : 'none:arcLength:pointDist',
                 'squash' : 'none:simple:single:both',
                 'squashExtraControl' : 'bool',
                 'squashFactorMax':'float',
                 'squashFactorMin':'float',
                 'neckSize':'double3',
             
                 'ribbonAim': 'none:stable:stableBlend',
                 'ribbonConnectBy': 'constraint:matrix',
                 'segmentMidIKControl':'bool',
                 'neckDirection':'vertical:horizontal',
                 'neckBuild':'bool',
                 'neckControls':'int',
                 'neckShapers':'int',
                 'neckSubShapers':'int',
                 'neckJoints':'int',
                 'blockProfile':'string',#':'.join(d_block_profiles.keys()),
                 #'blockProfile':':'.join(d_block_profiles.keys()),
                 'neckIK':BLOCKSHARE._d_attrsTo_make.get('ikSetup')#we wanna match this one
                 }

d_defaultSettings = {'version':__version__,
                     'baseSize':MATH.get_space_value(__dimensions[1]),
                     'headAim':True,
                     'neckBuild':True,
                     'neckControls': 1,
                     'neckShapers':0,
                     'neckSubShapers':2,
                     'attachPoint':'end',
                     'loftSides': 10,
                     'loftSplit':1,
                     'loftDegree':'linear',
                     'neckJoints':3,
                     'proxyDirect':True,
                     'attachPoint':'end',
                     'neckIK':'ribbon',
                     'ribbonParam':'blend',
                     'visLabels':True,
                     'squashMeasure':'arcLength',
                     'squash':'simple',
                     'squashFactorMax':1.0,
                     'squashFactorMin':1.0,
                     
                     'segmentMidIKControl':True,
                     'squash':'both',
                     'squashExtraControl':True,
                     'ribbonAim':'stable',
                     'ikOrientToWorld':True,
                     'proxyShape':'cube',
                     'proxyGeoRoot':1,
                     'loftList':['wideUp','circle'],
                     'nameList':['neck','head'],#...our datList values
                     'proxyType':'geo'}

#Skeletal stuff ------------------------------------------------------------------------------------------------
d_skeletonSetup = {'mode':'curveCast',
                   'targetsMode':'prerigHandles',
                   'helperUp':'z-',
                   'countAttr':'neckJoints',
                   'targets':'jointHelper'}

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotationOrders = {'head':'yxz'}

_l_hiddenAttrs = ['neckSize']

#=============================================================================================================
#>> UI
#=============================================================================================================
def headGeo_getGroup(self,select=False):
    _str_func = 'get_headGeoGroup'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)    
    mGroup = self.getMessageAsMeta('headGeoGroup')
    log.debug(mGroup)
    if select:
        mc.select(mGroup.mNode)
    return mGroup

def headGeo_lock(self,arg=None):
    _str_func = 'headGeo_selectable'    
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))    
    mGroup = headGeo_getGroup(self)
    if mGroup:
        if arg is None:
            arg = not mGroup.overrideEnabled
        mGroup.overrideEnabled = arg

def headGeo_add(self,arg = None):
    _str_func = 'headGeo_add'
    if not arg:
        arg = mc.ls(sl=1)
    ml_stuff = cgmMeta.validateObjListArg(arg)
    if not ml_stuff:
        return log.error("|{0}| add | Nothing selected and no arg offered ".format(self.p_nameShort))
    mProxyGeoGrp = headGeo_getGroup(self)
    ml_proxies = []
    _side = self.UTILS.get_side(self)
    mHandleFactory = self.asHandleFactory()
    for mObj in ml_stuff:
        mProxy = mObj.doDuplicate(po=False)
        mProxy = cgmMeta.validateObjArg(mProxy,'cgmObject',setClass=True)
        ml_proxies.append(mProxy)
        #TRANS.scale_to_boundingBox(mProxy.mNode,_bb_axisBox)
        mHandleFactory.color(mProxy.mNode,_side,'sub',transparent=True)
        
        mProxy.p_parent = mProxyGeoGrp
        self.msgList_append('headMeshProxy',mProxy,'block')
        
        mProxy.rename("{0}_proxyGeo".format(mProxy.p_nameBase))

def headGeo_remove(self,arg = None):
    _str_func = 'headGeo_remove'
    if not arg:
        arg = mc.ls(sl=1)
    ml_stuff = cgmMeta.validateObjListArg(arg)
    if not ml_stuff:
        return log.error("|{0}| remove | Nothing selected and no arg offered ".format(self.p_nameShort))
    mProxyGeoGrp = headGeo_getGroup(self)
    ml_proxies = []
    _side = self.UTILS.get_side(self)
    
    for mObj in ml_stuff:
        mObj.p_parent = False
        self.msgList_remove('headMeshProxy',mObj)
        mObj.rename(mObj.p_nameBase.replace('proxyGeo','geo'))
        mObj.overrideEnabled = 0
        for mShape in mObj.getShapes(asMeta=1):
            mShape.overrideEnabled = 0
        
def headGeo_replace(self,arg = None):
    _str_func = 'get_headGeoGroup'
    
    if not arg:
        arg = mc.ls(sl=1)
    ml_stuff = cgmMeta.validateObjListArg(arg)
    if not ml_stuff:
        return log.error("|{0}| add | Nothing selected and no arg offered ".format(self.p_nameShort))
    
    mProxyGeoGrp = headGeo_getGroup(self)    
    #Clean
    ml_current = self.msgList_get('headMeshProxy')
    for mObj in ml_current:
        if mObj not in ml_stuff:
            mObj.p_parent = False
        
    try:self.msgList_purge('headMeshProxy')
    except:pass
    
    headGeo_add(self,ml_stuff)
    

def uiBuilderMenu(self,parent = None):
    #uiMenu = mc.menuItem( parent = parent, l='Head:', subMenu=True)
    _short = self.p_nameShort
    
    mc.menuItem(en=False,
                label = "Head Geo")    
    mc.menuItem(ann = '[{0}] Report Head geo group'.format(_short),
                c = cgmGEN.Callback(headGeo_getGroup,self),
                label = "Report Group")
    mc.menuItem(ann = '[{0}] Add selected to head geo proxy group'.format(_short),
                c = cgmGEN.Callback(headGeo_add,self),
                label = "Add selected")
    mc.menuItem(ann = '[{0}] REPLACE existing geo with selected'.format(_short),
                c = cgmGEN.Callback(headGeo_replace,self),
                label = "Replace with selected")
    mc.menuItem(ann = '[{0}]Remove selected to head geo proxy group'.format(_short),
                c = cgmGEN.Callback(headGeo_remove,self),
                label = "Remove selected")        
    mc.menuItem(ann = '[{0}] Select Geo Group'.format(_short),
                c = cgmGEN.Callback(headGeo_getGroup,self,True),
                label = "Select Group")
    
    mc.menuItem(ann = '[{0}] Head Geo Lock'.format(_short),
                c = cgmGEN.Callback(headGeo_lock,self,None),
                label = "Toggle Lock")

    
    """
    mc.menuItem(uiMenu,
                ann = '[{0}] Recreate the base shape and push values to baseSize attr'.format(_short),                                                    
                c = cgmGEN.Callback(resize_masterShape,self),
                label = "Resize")"""

#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    try:
        _str_func = 'define'    
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        _short = self.mNode
        
        for a in 'baseAim','baseSize','baseUp':
            if ATTR.has_attr(_short,a):
                ATTR.set_hidden(_short,a,True)            
        
        ATTR.set_min(_short, 'neckControls', 1)
        ATTR.set_min(_short, 'loftSides', 3)
        ATTR.set_min(_short, 'loftSplit', 1)
        ATTR.set_min(_short, 'neckShapers', 2)
        
        ATTR.set_alias(_short,'sy','blockScale')    
        self.setAttrFlags(attrs=['sx','sz','sz'])
        self.doConnectOut('sy',['sx','sz'])            
        
        for a in _l_hiddenAttrs:
            if ATTR.has_attr(_short,a):
                ATTR.set_hidden(_short,a,True)        
        
        _shapes = self.getShapes()
        if _shapes:
            log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
            mc.delete(_shapes)
            defineNull = self.getMessage('defineNull')
            if defineNull:
                log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
                mc.delete(defineNull)
            self.verify()
            
        
        _size = self.atUtils('defineSize_get')
        #_sizeSub = _size / 2.0
        log.debug("|{0}| >>  Size: {1}".format(_str_func,_size))
        """
        _crv = CURVES.create_fromName(name='locatorForm',
                                      direction = 'z+', size = _size * 2.0)
    
        SNAP.go(_crv,self.mNode,)
        CORERIG.override_color(_crv, 'white')
        CORERIG.shapeParent_in_place(self.mNode,_crv,False)
        self.addAttr('cgmColorLock',True,lock=True,visible=False)"""
        
        mHandleFactory = self.asHandleFactory()        
        mDefineNull = self.atUtils('stateNull_verify','define')
        
        
        """
        #Rotate Group ==================================================================
        mRotateGroup = cgmMeta.validateObjArg(mDefineNull.doGroup(True,False,asMeta=True,typeModifier = 'rotate'),
                                              'cgmObject',setClass=True)
        mRotateGroup.p_parent = mDefineNull
        mRotateGroup.doConnectIn('rotate',"{0}.baseAim".format(_short))
        mRotateGroup.setAttrFlags()
        """
        #Bounding box ==================================================================
        _bb_shape = CURVES.create_controlCurve(self.mNode,'cubeOpen', size = 1.0, sizeMode='fixed')
        mBBShape = cgmMeta.validateObjArg(_bb_shape, 'cgmObject',setClass=True)
        mBBShape.p_parent = mDefineNull    
        #mBBShape.ty = .5
        
        #CORERIG.copy_pivot(mBBShape.mNode,self.mNode)
        mBBShape.scale = self.baseSize
        #self.doConnectOut('baseSize', "{0}.scale".format(mBBShape.mNode))
        mHandleFactory.color(mBBShape.mNode,controlType='sub')
        #mBBShape.setAttrFlags(['scale'])
        
        mBBShape.doStore('cgmName', self)
        mBBShape.doStore('cgmType','bbVisualize')
        mBBShape.doName()    
        
        self.connectChildNode(mBBShape.mNode,'bbHelper')
        
        #Aim Controls ==================================================================
        _d = {'aim':{'color':'yellowBright','defaults':{'tz':2}},
              'end':{'color':'white','name':'neckBase','defaults':{'ty':-1}},
              'start':{'color':'white','name':'neckEnd','defaults':{},'noLock':['translate']},
              'up':{'color':'greenBright','name':'neckUp','defaults':{'tz':-1}},
              'rp':{'color':'redBright','name':'neckRP','defaults':{'tz':-2},'parentTag':'end'}}
        
        for k,d in _d.iteritems():
            d['vectorLine'] = False
    
        _l_order = ['aim','end','start','up','rp']
        
        _baseDat = self.baseDat or {}
        
        _resDefine = self.UTILS.create_defineHandles(self, _l_order, _d, _size,
                                                     rotVecControl=True,
                                                     blockUpVector = _baseDat.get('up',[0,1,0]),
                                                     startScale=True,)
                                                     #vectorScaleAttr='neckSize')
        self.UTILS.define_set_baseSize(self)
        
        md_vector = _resDefine['md_vector']
        md_handles = _resDefine['md_handles']
    
                
        #Rotate Plane ======================================================================
        mRotatePlane = self.UTILS.create_define_rotatePlane(self, md_handles,md_vector,mStartParent = md_handles['start'])
        
        #Neck Build Group ======================================================================
        mNeckGroup = mDefineNull.doCreateAt('null',setClass='cgmObject')
        mNeckGroup.p_parent = mDefineNull
        mNeckGroup.rename('neck_ull')
        mNeckGroup.doConnectIn('visibility',"{0}.neckBuild".format(self.mNode))
    
        md_handles['end'].p_parent = mNeckGroup
        md_handles['start'].p_parent = mNeckGroup
        md_handles['rp'].p_parent = mNeckGroup        
        self.defineLoftMesh.p_parent = mNeckGroup
        self.defineLoftMesh.resetAttrs()
        mRotatePlane.p_parent = mNeckGroup
        
        _end = md_handles['end'].mNode
        self.doConnectIn('neckSizeX',"{0}.width".format(_end))
        self.doConnectIn('neckSizeY',"{0}.height".format(_end))
        self.doConnectIn('neckSizeZ',"{0}.length".format(_end))
        
        self.UTILS.rootShape_update(self)        
        _dat = self.baseDat
        _dat['baseSize'] = self.baseSize
        self.baseDat = _dat        
        
        self.msgList_append('defineHandles', mBBShape)
        
        return    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

    
    
    
#=============================================================================================================
#>> Form
#=============================================================================================================    
#def formDelete(self):
#    return BLOCKUTILS.formDelete(self,['orientHelper'])

#is_form = BLOCKUTILS.is_form
def formDelete(self):
    try:
        _str_func = 'formDelete'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        for k in ['end','start','rp','up','aim']:
            mHandle = self.getMessageAsMeta("define{0}Helper".format(k.capitalize()))
            if mHandle:
                mHandle.v = True
                mHandle.template = False
                if k in ['rp','up']:
                    continue                
                l_const = mHandle.getConstraintsTo()
                if l_const:
                    log.debug("currentConstraints...")
                    pos = mHandle.p_position
                    for i,c in enumerate(l_const):
                        log.debug("    {0} : {1}".format(i,c))
                        if k in ['start','end']:
                            if mc.ls(c,type=['aimConstraint']):
                                pass
                            else:
                                mc.delete(c)
                        else:
                            mc.delete(c)
                    mHandle.p_position = pos
                    
                if k == 'end':
                    _end = mHandle.mNode
                    self.doConnectIn('neckSizeX',"{0}.width".format(_end))
                    self.doConnectIn('neckSizeY',"{0}.height".format(_end))
                    self.doConnectIn('neckSizeZ',"{0}.length".format(_end))
                    """
                    _end = mHandle.mNode
                    _neckSize = []
                    for a in 'width','height','length':
                        _neckSize.append(ATTR.get(_end,a))
                    self.neckSize = _neckSize
                    _dat = self.baseDat
                    _dat['baseSize'] = self.baseSize
                    self.baseDat = _dat"""

                
            mHandle = self.getMessageAsMeta("vector{0}Helper".format(k.capitalize()))
            if mHandle:
                mHandle.template=False
                
        
        try:self.defineLoftMesh.v = True
        except:pass
        self.bbHelper.v = True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
  
def form(self):
    try:
        _str_func = 'form'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
        _proxyType = self.proxyType
        
        #Initial checks ===============================================================================
        log.debug("|{0}| >> Initial checks...".format(_str_func)+ '-'*40)
        
        _short = self.p_nameShort
        _side = self.UTILS.get_side(self)
            

        
        _ikSetup = self.getEnumValueString('ikSetup')
        _loftSetup = self.getEnumValueString('loftSetup')
                
        for a in 'XYZ':ATTR.break_connection(self.mNode,'neckSize'+a)
        
        #Get base dat =============================================================================
        log.debug("|{0}| >> Base dat...".format(_str_func)+ '-'*40)
        md_vectorHandles = {}
        md_defineHandles = {}
        
        #Form our vectors and gather the helpers
        md_defineHandles,md_vectorHandles = self.UTILS.define_getHandles(self)
        """
        for k in ['end','rp','up','aim']:
            mHandle = self.getMessageAsMeta("vector{0}Helper".format(k.capitalize()))    
            if mHandle:
                log.debug("define vector: {0} | {1}".format(k,mHandle))            
                mHandle.template=True
                md_vectorHandles[k] = mHandle
                
            mHandle = self.getMessageAsMeta("define{0}Helper".format(k.capitalize()))    
            if mHandle:
                log.debug("define handle: {0} | {1}".format(k,mHandle))                        
                md_defineHandles[k] = mHandle
                if k in ['end','aim']:
                    mHandle.template = True"""
        
        #_l_basePosRaw = self.datList_get('basePos') or [(0,0,0)]
        if self.neckBuild:
            _l_basePos = [md_defineHandles['start'].p_position]
        else:
            _l_basePos = [self.p_position]
            

        
        #Create temple Null  ==================================================================================
        mFormNull = BLOCKUTILS.formNull_verify(self)
        mNoTransformNull = BLOCKUTILS.noTransformNull_verify(self,'form')
        
        mLoc = self.doLoc()
        SNAP.aim_atPoint(mLoc.mNode, md_defineHandles['aim'].p_position, vectorUp=self.getAxisVector('y+'))
        _mVectorAim = MATH.get_obj_vector(mLoc.mNode,
                                          asEuclid=True)
        mLoc.delete()
        log.debug("vectorAim: {0}".format(_mVectorAim))
    
        pos_self = self.p_position
        pos_aim = DIST.get_pos_by_vec_dist(pos_self, _mVectorAim, 5)        
        
        
        #Our main head handle =================================================================================
        mBBHelper = self.bbHelper
        
        mHeadHandle = mBBHelper.doCreateAt(setClass=True)
        self.copyAttrTo(_baseNameAttrs[-1],mHeadHandle.mNode,'cgmName',driven='target')    
        mHeadHandle.doStore('cgmType','blockHelper')
        mHeadHandle.doName()
        
        mHeadHandle.p_parent = mFormNull
        mHandleFactory = self.asHandleFactory(mHeadHandle.mNode, rigBlock = self.mNode)
        
        CORERIG.shapeParent_in_place(mHeadHandle.mNode, mBBHelper.mNode, True, True)
        
        CORERIG.colorControl(mHeadHandle.mNode,_side,'main',transparent = True) 
        mBBHelper.v = False
        #self.defineNull.template=True        
        _bb_axisBox = SNAPCALLS.get_axisBox_size(mBBHelper.mNode)
        v_baseSize = _bb_axisBox #SNAPCALLS.get_axisBox_size(mBBHelper.mNode)
        #v_baseSize = DIST.get_bb_size(mBBHelper.mNode)

        
        
        #Orient Helper ==============================================================================
        mOrientCurve = mHandleFactory.addOrientHelper(baseSize = v_baseSize[0] * .7,
                                                      shapeDirection = 'z+',
                                                      setAttrs = {'rz':90,
                                                                  'tz': v_baseSize[2] * .8})
        self.copyAttrTo(_baseNameAttrs[-1],mOrientCurve.mNode,'cgmName',driven='target')
        mOrientCurve.doName()    
        CORERIG.colorControl(mOrientCurve.mNode,_side,'sub')
        
        """
        SNAP.aim_atPoint(obj=mOrientCurve.mNode, position = pos_aim,
                         aimAxis="z+", upAxis="y+", 
                         mode='vector', vectorUp= self.getAxisVector('y+'))"""
        
        mOrientCurve.setAttrFlags(['rz','translate','scale','v'])
        

        
        self.connectChildNode(mOrientCurve.mNode,'orientHelper')
        
        
        mAimTrans = md_defineHandles['aim'].doCreateAt(setClass = True)
        mAimTrans.p_parent = mOrientCurve.mNode                
        
        
        #Proxies ==============================================================================
        ml_proxies = []        
        log.debug("|{0}| >> Geo proxyType...".format(_str_func,))     
        
        if _proxyType == 0:
            _res = build_prerigMesh(self)
            mProxy = cgmMeta.validateObjArg(_res[0],'cgmObject',setClass=True)
            mProxy.doSnapTo(self.mNode)       
            TRANS.scale_to_boundingBox(mProxy.mNode, _bb_axisBox)
            
            ml_proxies.append(mProxy)
            
            #mProxy.scale = self.getScaleLossy() 
            CORERIG.colorControl(mProxy.mNode,_side,'main',transparent = True)  
            
            for mShape in mProxy.getShapes(asMeta=1):
                mShape.overrideEnabled = 1
                mShape.overrideDisplayType = 2  
                
            mProxy.parent = mHeadHandle
            mGroup = mProxy.doGroup(True, asMeta = True, typeModifier = 'rotateGroup')
            ATTR.connect(self.mNode + '.headRotate', mGroup.mNode + '.rotate')
            
        elif _proxyType == 1:
            log.debug("|{0}| >> Geo proxyType. Pushing dimensions...".format(_str_func))     
            #self.scaleX = __dimensions[0] / __dimensions[1]
            #self.scaleZ = __dimensions[2] / __dimensions[1]        
            
            mFile = os.path.join(path_assets, 'headSimple_01.obj')
            _res = cgmOS.import_file(mFile,'HEADIMPORT')
            
            mGeoProxies = mHeadHandle.doCreateAt()
            mGeoProxies.rename("proxyGeo")
            mGeoProxies.parent = mHeadHandle
            #mGeoProxies.parent = mFormNull
            
            #_bb = DIST.get_bb_size(self.mNode,True)
            
            ATTR.connect(self.mNode + '.headRotate', mGeoProxies.mNode + '.rotate')
            mGeoProxies.connectParentNode(self, 'rigBlock','headGeoGroup') 
            
            for i,o in enumerate(_res):
                mProxy = cgmMeta.validateObjArg(o,'cgmObject',setClass=True)
                ml_proxies.append(mProxy)
                TRANS.scale_to_boundingBox(mProxy.mNode,_bb_axisBox)
                #TRANS.scale_to_boundingBox(mProxy.mNode,[1,1,1])
                mProxy.doSnapTo(mHeadHandle.mNode)                
                
                #CORERIG.colorControl(mProxy.mNode,_side,'main',transparent = True)
                mHandleFactory.color(mProxy.mNode,_side,'sub',transparent=True)
                
                mProxy.parent = mGeoProxies
                mProxy.rename('head_{0}'.format(i))
                
                #for mShape in mProxy.getShapes(asMeta=1):
                    #mShape.overrideEnabled = 1
                    #mShape.overrideDisplayType = 2                  
                
            NODEFACTORY.build_conditionNetworkFromGroup(mGeoProxies.mNode,'headGeo',self.mNode)
            ATTR.set_keyable(self.mNode,'headGeo',False)
            #mGeoProxies.scale = self.baseSize
            mGeoProxies.overrideEnabled = 1
            mGeoProxies.overrideDisplayType = 2         
            #self.doConnectOut('baseSize', "{0}.scale".format(mGeoProxies.mNode))
            #mc.parentConstraint([mHeadHandle.mNode],mGeoProxies.mNode,maintainOffset = True)
            
            
        else:
            raise NotImplementedError,"|{0}| >> Unknown proxyType: [{1}:{2}]".format(_str_func,
                                                                                     _proxyType,
                                                                                     ATTR.get_enumValueString(self.mNode,'proxyType'))
        
        self.msgList_connect('headMeshProxy',ml_proxies,'block')#Connect
        
        
        #Neck ==================================================================================================
        if not self.neckBuild:
            self.msgList_connect('formHandles',[mHeadHandle.mNode])
            #...just so we have something here. Replaced if we have a neck        
        else:
            log.debug("|{0}| >> Neck ...".format(_str_func)+ '-'*60)
            self.defineLoftMesh.v = False
            
            int_handles = self.neckShapers
            _loftShape = self.getEnumValueString('loftShape')
            #if _loftSetup == 'loftList':
            self.UTILS.verify_loftList(self,int_handles)                    
            
            #Get base dat =============================================================================
            log.debug("|{0}| >> neck Base dat...".format(_str_func)+ '-'*40)
            mRootUpHelper = self.vectorUpHelper
            mRootRpHelper = self.vectorRpHelper
            
            mDefineStartObj = self.defineStartHelper
            mDefineEndObj = self.defineEndHelper
            mDefineUpObj = self.defineUpHelper
            
            """
            mLoc = mRootRpHelper.doLoc()
            SNAP.aim_atPoint(mLoc.mNode, md_defineHandles['end'].p_position, vectorUp=mRootRpHelper.getAxisVector('y+'))
            _mVectorAim = MATH.get_obj_vector(mLoc.mNode,asEuclid=True) #self.vectorEndHelper.mNode
            mLoc.delete()"""
            
            _mVectorAim = MATH.get_vector_of_two_points(mDefineStartObj.p_position,
                                                        mDefineEndObj.p_position, True)
            
            _mVectorUp = MATH.get_obj_vector(mRootUpHelper.mNode,asEuclid=True)

        
            mDefineLoftMesh = self.defineLoftMesh
            _v_range = DIST.get_distance_between_points(mDefineStartObj.p_position,
                                                        mDefineEndObj.p_position)
            #_bb_axisBox = SNAPCALLS.get_axisBox_size(mDefineLoftMesh.mNode, _v_range, mark=False)
            _size_width = mDefineEndObj.width#...x width
            _size_height = mDefineEndObj.height#
            log.debug("|{0}| >> Generating more pos dat | bbHelper: {1} | range: {2}".format(_str_func,
                                                                                             mDefineLoftMesh.p_nameShort,
                                                                                             _v_range))
            _end = DIST.get_pos_by_vec_dist(_l_basePos[0], _mVectorAim, _v_range)
            _size_length = DIST.get_distance_between_points(mDefineStartObj.p_position, _end)
            _size_handle = _size_width * 1.25
            _size_loft = MATH.get_greatest(_size_width,_size_height)
            
            #self.baseSize = [_size_width,_size_height,_size_length]
            _l_basePos.append(_end)
            log.debug("|{0}| >> baseSize: {1}".format(_str_func, self.baseSize))
            
            for i,p in enumerate(_l_basePos):
                LOC.create(position=p)
            
            for mHandle in mDefineEndObj,mDefineStartObj:
                mHandle.v=False
            
            
            #Get base dat =============================================================================        
            log.debug("|{0}| >> Building neck...".format(_str_func)) 
            _b_lever = False
            md_handles = {}
            ml_handles = []
            md_loftHandles = {}
            ml_loftHandles = []
            
            _loftShapeBase = self.getEnumValueString('loftShape')
            _loftShape = 'loft' + _loftShapeBase[0].capitalize() + ''.join(_loftShapeBase[1:])
            _loftSetup = self.getEnumValueString('loftSetup')
            
            cgmGEN.func_snapShot(vars())
            
            _l_basePos.reverse()
            _l_mainParents = [mFormNull, mHeadHandle]
            
                
            md_handles,ml_handles,ml_shapers,ml_handles_chain = self.UTILS.form_segment(
                self,
                aShapers = 'neckShapers',aSubShapers = 'neckSubShapers',
                loftShape=_loftShape,l_basePos = _l_basePos, baseSize=_size_handle,
                orientHelperPlug='orientNeckHelper',
                sizeWidth = _size_width, sizeLoft=_size_loft,side = _side,
                mFormNull = mFormNull,mNoTransformNull = mNoTransformNull,
                mDefineEndObj=None)
            
            
            self.UTILS.form_shapeHandlesToDefineMesh(self,ml_handles_chain)

            #>>> Connections ====================================================================================
            self.msgList_connect('formHandles',[mHeadHandle]+[mObj.mNode for mObj in ml_handles_chain])
        
            #>>Loft Mesh =========================================================================================
            if self.neckShapers:
                targets = [mObj.loftCurve.mNode for mObj in ml_shapers]
                self.msgList_connect('shaperHandles',[mObj.mNode for mObj in ml_shapers])
            else:
                targets = [mObj.loftCurve.mNode for mObj in ml_handles_chain]
                
        
            mNeckSurf = self.atUtils('create_prerigLoftMesh',
                                     targets,
                                     mFormNull,
                                     'neckControls',                     
                                     'loftSplit',
                                     polyType='bezier',
                                     baseName = self.cgmName )
            mHandleFactory.color(mNeckSurf.mNode,_side,'sub',transparent=True)
            

            mNoTransformNull.v = False
        
            #End setup======================================================================================

        
            #Aim end handle -----------------------------------------------------------------------------------
            SNAP.aim_atPoint(md_handles['end'].mNode, position=_l_basePos[0], 
                             aimAxis="z-", mode='vector', vectorUp=_mVectorUp)
            
            SNAP.aim_atPoint(md_handles['start'].mNode, position=_l_basePos[-1], 
                             aimAxis="z+", mode='vector', vectorUp=_mVectorUp)
            
            #Constrain the define end to the end of the form handles
            mc.pointConstraint(md_handles['start'].mNode,mDefineEndObj.mNode,maintainOffset=False)            
            mc.pointConstraint(md_handles['end'].mNode,mDefineStartObj.mNode,maintainOffset=False)
           
           
            self.UTILS.form_shapeHandlesToDefineMesh(self,ml_handles_chain)
               
               
                
            #self.msgList_connect('formHandles',[mHeadHandle.mNode] + ml_handles)#...just so we have something here. Replaced if we have a neck        
                
            """
            BLOCKUTILS.create_formLoftMesh(self,targets,mBaseLoftCurve,
                                               mFormNull,'neckControls',
                                               baseName = _l_baseNames[1])"""
            
            """
            #Base Orient Helper ----------------------------------------------------------------------------------
            mHandleFactory = self.asHandleFactory(mBaseCurve.mNode)
        
            mBaseOrientCurve = mHandleFactory.addOrientHelper(baseSize = _size_width,
                                                              shapeDirection = 'z-',
                                                              setAttrs = {#'rz':90,
                                                                          'ty':_size_width * .25,
                                                                          'tz':- _size_width})
        
            self.copyAttrTo(_baseNameAttrs[1],mOrientCurve.mNode,'cgmName',driven='target')
            mBaseOrientCurve.doName()    
            mBaseOrientCurve.p_parent = mBaseLoftCurve.parent
            #mBaseOrientCurve.resetAttrs()
            mBaseOrientCurve.setAttrFlags(['rz','rx','translate','scale','v'])
        
            CORERIG.colorControl(mBaseOrientCurve.mNode,_side,'sub')          
            mc.select(cl=True)    """
            
        #Aim this last so we don't shear our head geo
        """
        SNAP.aim_atPoint(obj=mHeadHandle.mNode, position = pos_aim,
                         aimAxis="z+", upAxis="y+", 
                         mode='vector', vectorUp= self.getAxisVector('y+'))"""
  
        mc.pointConstraint(mAimTrans.mNode,
                           md_defineHandles['aim'].mNode,
                           maintainOffset = True)        
        
        self.blockState = 'form'#...buffer
        
        return True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,msg=vars())


#=============================================================================================================
#>> Prerig
#=============================================================================================================
def build_prerigMesh(self):
    _str_func = 'build_prerigMesh'    
    _shape = self.getEnumValueString('proxyShape')
    _size = self.baseSize
    
    if _shape == 'cube':
        _res = mc.polyCube(width=_size[0], height = _size[1], depth = _size[2])
    elif _shape == 'sphere':
        _res = mc.polySphere(radius = MATH.average(_size) * .5)
    elif _shape == 'cylinder':
        _res = mc.polyCylinder(height = MATH.average(_size), radius = MATH.average(_size) * .5)
    else:
        raise ValueError,"|{0}| >> Unknown shape: [{1}]".format(_str_func,_shape)
    return _res

def prerig(self):
    try:
        #Buffer some data
        _str_func = 'prerig'
        _short = self.p_nameShort
        _side = self.atUtils('get_side')
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        
        _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
        

        #Initial validation ================================================================================
        log.debug("|{0}| >> Initial checks...".format(_str_func)+ '-'*40)
        
        self.atUtils('module_verify')
        mPrerigNull = BLOCKUTILS.prerigNull_verify(self)   
        #mNoTransformNull = self.atUtils('noTransformNull_verify')
        mNoTransformNull = self.UTILS.noTransformNull_verify(self,'prerig')
        ml_formHandles = self.msgList_get('formHandles')
        _sizeSub = self.atUtils('get_shapeOffset')*2#_size * .2
        
        #>>New handles =====================================================================================
        mHandleFactory = self.asHandleFactory(self.mNode)   

        #Settings Helper ====================================================================
        mBBHelper = self.bbHelper
        _bb_axisBox = SNAPCALLS.get_axisBox_size(mBBHelper.mNode)
        
        pos = mBBHelper.getPositionByAxisDistance('z+', _bb_axisBox[1] * .75)
        vector = mBBHelper.getAxisVector('y+')
        
        newPos = DIST.get_pos_by_vec_dist(pos,vector, _bb_axisBox[1] * .5)
    
        settings = CURVES.create_fromName('gear', _bb_axisBox[1]/5,'x+')
        
        mSettingsShape = cgmMeta.validateObjArg(settings,'cgmObject')
        mSettings = cgmMeta.validateObjArg(self.doCreateAt(),'cgmObject',setClass=True)
        
        mSettings.p_position = newPos
        mSettingsShape.p_position = newPos
        mSettings.p_parent = mPrerigNull
        
        ATTR.copy_to(self.mNode,'cgmName',mSettings.mNode,driven='target')
        #mSettings.doStore('cgmName','head')
        mSettings.doStore('cgmType','shapeHelper')
        mSettings.doName()
        #CORERIG.colorControl(mSettings.mNode,_side,'sub')
        
        SNAP.aim_atPoint(mSettingsShape.mNode,
                         self.p_position,
                         aimAxis='z+',
                         mode = 'vector',
                         vectorUp= self.getAxisVector('y+'))
        
        CORERIG.shapeParent_in_place(mSettings.mNode, mSettingsShape.mNode,False)
        mHandleFactory.color(mSettings.mNode,controlType='sub')
        
        self.connectChildNode(mSettings,'settingsHelper','block')#Connect
        
        
        if not self.neckBuild:
            #Joint Helper ======================================================================================
            mJointHelper = mHandleFactory.addJointHelper(baseSize = _sizeSub,
                                                         loftHelper = False,
                                                         baseShape='axis3d')
            ATTR.set_standardFlags(mJointHelper.mNode, attrs=['sx', 'sy', 'sz'], 
                                  lock=False, visible=True,keyable=False)
            
            self.msgList_connect('jointHelpers',[mJointHelper])#mJointHelper.mNode
            self.msgList_connect('prerigHandles',[mJointHelper])#self.mNode
            
            mHandleFactory.addJointLabel(mJointHelper,'head')
            
            
    
        else:#NECK build ==========================================================================================
            int_neckControls = self.neckControls + 1
            ml_formHandles_neck = ml_formHandles[1:]
            ml_noParent = []
            
            mStartHandle = ml_formHandles_neck[0]#...changed
            mEndHandle = ml_formHandles_neck[-1]    
            mOrientHelper = self.orientHelper
            mOrientNeckHelper = self.orientNeckHelper
            
            _ikEnd = False
            ml_handles = []
            ml_jointHandles = []        
            _vec_root_up = mOrientNeckHelper.getAxisVector('y+')
        
            #Initial logic=========================================================================================
            log.debug("|{0}| >> Initial Logic...".format(_str_func)+'-'*40) 
        
            _pos_start = mStartHandle.p_position
            _pos_end = mEndHandle.p_position 
            _vec = MATH.get_vector_of_two_points(_pos_start, _pos_end)
    
            _offsetDist = DIST.get_distance_between_points(_pos_start,_pos_end) / int_neckControls#(int_neckControls - 1.0)
        
            _mVectorAim = MATH.get_vector_of_two_points(_pos_start, _pos_end,asEuclid=True)
            _mVectorUp = MATH.get_obj_vector(mOrientNeckHelper.mNode,'y+',asEuclid=True)
            
            _worldUpVector = [_mVectorUp.x,_mVectorUp.y,_mVectorUp.z]
            
            #Sub handles... ------------------------------------------------------------------------------------
            log.debug("|{0}| >> PreRig Handle creation...".format(_str_func)+'-'*40)
            ml_aimGroups = []
            _nameDict = self.getNameDict(ignore=['cgmName','cgmType'])
            #_nameDict['cgmType'] = 'blockHandle'
            
            mDefineEndObj = self.defineEndHelper    
            _size_width = mDefineEndObj.width#...x width
            _sizeUse = _size_width/ 3.0 #self.atUtils('get_shapeOffset')
            
            """
            #Track curve ============================================================================
            log.debug("|{0}| >> TrackCrv...".format(_str_func)+'-'*40) 
            
            _trackCurve = mc.curve(d=1,p=[mObj.p_position for mObj in ml_formHandles])
            mTrackCurve = cgmMeta.validateObjArg(_trackCurve,'cgmObject')
            mTrackCurve.rename(self.cgmName + 'prerigTrack_crv')
            mTrackCurve.parent = mNoTransformNull
            
            
            #mPrerigNull.connectChildNode('prerigTrackCurve',mTrackCurve.mNode,)
            
            l_clusters = []
            #_l_clusterParents = [mStartHandle,mEndHandle]
            for i,cv in enumerate(mTrackCurve.getComponents('cv')):
                _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(ml_formHandles[i].p_nameBase,i))
                #_res = mc.cluster(cv)
                TRANS.parent_set( _res[1], ml_formHandles[i].getMessage('loftCurve')[0])
                l_clusters.append(_res)
                ATTR.set(_res[1],'visibility',False)
            
            #pprint.pprint(l_clusters)
            mc.rebuildCurve(mTrackCurve.mNode, d=3, keepControlPoints=False,ch=1,n="reparamRebuild")        
            """
            #Track curve ============================================================================
            log.debug("|{0}| >> TrackCrv...".format(_str_func)+'-'*40) 
        
            _trackCurve = mc.curve(d=1,p=[mObj.p_position for mObj in ml_formHandles_neck])
            mTrackCurve = cgmMeta.validateObjArg(_trackCurve,'cgmObject')
            mTrackCurve.rename(self.cgmName + 'prerigTrack_crv')
            mTrackCurve.parent = mNoTransformNull
        
        
            #mPrerigNull.connectChildNode('prerigTrackCurve',mTrackCurve.mNode,)
        
            l_clusters = []
            #_l_clusterParents = [mStartHandle,mEndHandle]
            for i,cv in enumerate(mTrackCurve.getComponents('cv')):
                _res = mc.cluster(cv, n = 'test_{0}_{1}_pre_cluster'.format(ml_formHandles_neck[i].p_nameBase,i))
                #_res = mc.cluster(cv)
                TRANS.parent_set( _res[1], ml_formHandles_neck[i].getMessage('loftCurve')[0])
                l_clusters.append(_res)
                ATTR.set(_res[1],'visibility',False)
        
            #pprint.pprint(l_clusters)
        
            mc.rebuildCurve(mTrackCurve.mNode, d=3, keepControlPoints=False,ch=1,n="reparamRebuild")
            
            #....split
            _l_pos = CURVES.returnSplitCurveList(mTrackCurve.mNode,self.neckControls + 1,markPoints = False)
            #_l_pos = [ DIST.get_pos_by_vec_dist(_pos_start, _vec, (_offsetDist * i)) for i in range(self.numControls-1)] + [_pos_end]
        
            #_sizeUse = self.atUtils('get_shapeOffset')
            mDefineEndObj = self.defineEndHelper    
            _size_width = mDefineEndObj.width#...x width        
            _sizeUse1 = _size_width/ 3.0 #self.atUtils('get_shapeOffset')
            _sizeUse2 = self.atUtils('get_shapeOffset') * 2
            _sizeUse = min([_sizeUse1,_sizeUse2])
            _len_set = len(_l_pos)
            
            for i,p in enumerate(_l_pos): #i,mFormHandle in enumerate(ml_formHandles_neck):
                log.debug("|{0}| >> prerig handle cnt: {1}".format(_str_func,i))
                #_HandleSnapTo = mFormHandle.mNode
                #mFormHandle = ml_formHandles_neck[i]
                #_HandleSnapTo = mFormHandle.mNode
                _last = False
                if p == _l_pos[-1]:
                    _last = True
                    crv = CURVES.create_fromName('axis3d', size = _sizeUse * 2.0)
                    mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
                    mHandle.addAttr('cgmColorLock',True,lock=True,hidden=True)
                    self.connectChildNode(mHandle.mNode,'ikOrientHandle')
                else:
                    crv = CURVES.create_fromName('cubeOpen', size = _sizeUse)
                    mHandle = cgmMeta.validateObjArg(crv, 'cgmObject', setClass=True)
                    
                _short = mHandle.mNode
                mHandle.p_position = p
                
                if _last:
                    mHandle.doStore('cgmName','{0}'.format(_l_baseNames[-1]))
                    ml_formHandles[0].connectChildNode(mHandle.mNode,'prerigHandle')
                    #SNAP.aim_atPoint(mHandle.mNode,_l_pos[i-1], aimAxis='z-',mode = 'vector',vectorUp=_worldUpVector)
                    
                else:
                    if _len_set > 2:
                        mHandle.doStore('cgmName','{0}_{1}'.format(_l_baseNames[0],i))
                    else:
                        mHandle.doStore('cgmName','{0}'.format(_l_baseNames[0]))
                    #ml_formHandles_neck[i].connectChildNode(mHandle.mNode,'prerigHandle')
                    SNAP.aim_atPoint(mHandle.mNode,_l_pos[i+1], mode = 'vector',vectorUp=_worldUpVector)
                    
                
                #try:ATTR.copy_to(self.mNode,_baseNameAttrs[i],_short, 'cgmName', driven='target')
                #except:mHandle.doStore('cgmName','NeedAnotherNameAttr')
                mHandle.doStore('cgmType','preHandle')
                for k,v in _nameDict.iteritems():
                    if v:
                        ATTR.copy_to(self.mNode,k,_short, k, driven='target')
                mHandle.doName()
                ml_handles.append(mHandle)
                
                #mHandle.doSnapTo(_HandleSnapTo)
                
                mGroup = mHandle.doGroup(True,True,asMeta=True,typeModifier = 'master',setClass='cgmObject')
                mGroup.p_parent = mPrerigNull
                
                
                _res_attach = RIGCONSTRAINT.attach_toShape(mGroup.mNode, mTrackCurve.mNode, 'conPoint')
                TRANS.parent_set(_res_attach[0], mNoTransformNull.mNode)
            
            
                mHandleFactory = self.asHandleFactory(mHandle.mNode)
                
                #Convert to loft curve setup ----------------------------------------------------
                ml_jointHandles.append(mHandleFactory.addJointHelper(baseSize = _sizeUse))
                mHandleFactory.color(mHandle.mNode,controlType='sub')
                
                
            self.msgList_connect('prerigHandles', ml_handles)
            
            #ml_handles[0].connectChildNode(mOrientHelper.mNode,'orientHelper')      
            
            #This breaks the naming
            #self.UTILS.prerigHandles_getNameDat(self,True)
                                     
            #Joint placer loft....
            log.debug("|{0}| >> Joint placers...".format(_str_func)+'-'*40)        
            for i,mObj in enumerate(ml_handles[:-1]):
                mLoft = mObj.jointHelper.loftCurve
                mAimGroup = mLoft.doGroup(True,True,asMeta=True)
                mc.aimConstraint(ml_handles[i+1].masterGroup.mNode,
                                 mAimGroup.mNode,
                                 maintainOffset = True, weight = 1,
                                 aimVector = [0,0,1],
                                 upVector = [0,1,0],
                                 worldUpVector = [0,1,0],
                                 worldUpObject = mObj.masterGroup.mNode,
                                 worldUpType = 'objectRotation' )          
            targets = [mObj.jointHelper.loftCurve.mNode for mObj in ml_handles]
            
            #Name Handles...
            log.debug("|{0}| >> name handles...".format(_str_func)+'-'*40)                
            for mHandle in ml_handles:
                mHandleFactory.addJointLabel(mHandle,mHandle.cgmName)
            
            self.msgList_connect('jointHelpers',[mObj.jointHelper.mNode for mObj in ml_handles])
            self.atUtils('create_jointLoft',
                         targets,
                         mPrerigNull,
                         baseCount = self.neckJoints * self.neckControls,
                         baseName = self.cgmName,
                         simpleMode = True)
            
            
            for t in targets:
                ATTR.set(t,'v',0)
            
            #Point Contrain the rpHandle -------------------------------------------------------------------------
            mVectorRP = self.getMessageAsMeta('vectorRpHelper')
            str_vectorRP = mVectorRP.mNode
            ATTR.set_lock(str_vectorRP,'translate',False)
            
            mc.pointConstraint([ml_jointHandles[0].mNode], str_vectorRP,maintainOffset=False)
            ATTR.set_lock(str_vectorRP,'translate',True)            
            
            
            #cgmGEN.func_snapShot(vars())
            #Neck ==================================================================================================
            mNoTransformNull.v = False
        
        self.blockState = 'prerig'#...buffer
        return True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

        
def prerigDelete(self):
    if self.getMessage('formLoftMesh'):
        mFormLoft = self.getMessage('formLoftMesh',asMeta=True)[0]
        for s in mFormLoft.getShapes(asMeta=True):
            s.overrideDisplayType = 2     
    if self.getMessage('noTransformNull'):
        mc.delete(self.getMessage('noTransformNull'))
        
    
    if self.neckBuild:
        #vectorRP ----------------------------------------------
        mVectorRP = self.getMessageAsMeta('vectorRpHelper')
        str_vectorRP = mVectorRP.mNode
        ATTR.set_lock(str_vectorRP,'translate',False)
        mVectorRP.resetAttrs(['tx','ty','tz'])
        ATTR.set_lock(str_vectorRP,'translate',True)        
        
    return BLOCKUTILS.prerig_delete(self,formHandles=True)

#def is_prerig(self):
#    return BLOCKUTILS.is_prerig(self,msgLinks=['moduleTarget','prerigNull'])
#def is_prerig(self):return True

def skeleton_check(self):
    return True

def skeleton_build(self, forceNew = True):
    try:
        _short = self.mNode
        _str_func = '[{0}] > skeleton_build'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func)) 
        
        _radius = self.atUtils('get_shapeOffset')
        mModule = self.atUtils('module_verify')
        
        ml_joints = []
    
        mRigNull = mModule.rigNull
        if not mRigNull:
            raise ValueError,"No rigNull connected"
        
        ml_formHandles = self.msgList_get('formHandles',asMeta = True)
        if not ml_formHandles:
            raise ValueError,"No formHandles connected"    
        
        ml_prerigHandles = self.msgList_get('prerigHandles',asMeta = True)
        if not ml_prerigHandles:
            raise ValueError,"No prerigHandles connected"
        
        #>> If skeletons there, delete -------------------------------------------------------------------------- 
        _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> Joints detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr
    
        _baseNameAttrs = ATTR.datList_getAttrs(self.mNode,'nameList')
        _l_baseNames = ATTR.datList_get(self.mNode, 'nameList')
        _l_namesToUse = self.atUtils('skeleton_getNameDicts',False, self.neckJoints +1,
                                     iterName = _l_baseNames[0])     
        
        #>> Head ===================================================================================
        log.debug("|{0}| >> Head...".format(_str_func))
        if self.neckBuild:
            p = POS.get( ml_prerigHandles[-1].jointHelper.mNode )        
        else:
            p = POS.get( self.jointHelper.mNode )
        mHeadHelper = self.orientHelper
        
        #...create ---------------------------------------------------------------------------
        mHead_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
        mHead_jnt.parent = False
        #self.copyAttrTo(_baseNameAttrs[-1],mHead_jnt.mNode,'cgmName',driven='target')
        
        #...orient ----------------------------------------------------------------------------
        #cgmMeta.cgmObject().getAxisVector
        #CORERIG.match_orientation(mHead_jnt.mNode, mHeadHelper.mNode)
        if self.neckBuild:
            """
            mVec_up = self.atUtils('prerig_get_upVector')
            
            TRANS.aim_atPoint(mHead_jnt.mNode,
                              ml_prerigHandles[-2].p_position,
                              'y-', 'z+', 'vector',
                              vectorUp=mVec_up)"""
            mHead_jnt.p_orient = ml_prerigHandles[-1].p_orient
            
        else:
            p_orientAxis = mHeadHelper.getPositionByAxisDistance('z+', 100)
            
            TRANS.aim_atPoint(mHead_jnt.mNode,
                              p_orientAxis,
                              'y-', 'z+', 'vector',
                              vectorUp=mHeadHelper.getAxisVector('y+'))
        """
        TRANS.aim_atPoint(mHead_jnt.mNode,
                          p_orientAxis,
                          'z+', 'y+', 'vector',
                          vectorUp=mHeadHelper.getAxisVector('y+'))    
        """
        #LOC.create(position=p_orientAxis)
        
        JOINT.freezeOrientation(mHead_jnt.mNode)
        
        #...name ----------------------------------------------------------------------------
        #mHead_jnt.doName()
        #mHead_jnt.rename(_l_namesToUse[-1])
        for k,v in _l_namesToUse[-1].iteritems():
            mHead_jnt.doStore(k,v)
        mHead_jnt.doName()
        
        if self.neckBuild:#...Neck =====================================================================
            if self.neckJoints == 0:
                log.warning("|{0}| >> Neck build on, no neckJoints. Setting to 1".format(_str_func))                
                self.neckJoints = 1
            log.debug("|{0}| >> neckBuild...".format(_str_func))
            if len(ml_prerigHandles) == 2 and self.neckJoints == 1:
                log.debug("|{0}| >> Single neck joint...".format(_str_func))
                p = POS.get( ml_prerigHandles[0].jointHelper.mNode )
                
                mBaseHelper = self.orientNeckHelper
                
                #...create ---------------------------------------------------------------------------
                mNeck_jnt = cgmMeta.cgmObject(mc.joint (p=(p[0],p[1],p[2])))
                
                #self.copyAttrTo(_baseNameAttrs[0],mNeck_jnt.mNode,'cgmName',driven='target')
                
                #...orient ----------------------------------------------------------------------------
                #cgmMeta.cgmObject().getAxisVector
                mVec_up = self.atUtils('prerig_get_upVector')
                
                TRANS.aim_atPoint(mNeck_jnt.mNode,
                                  mHead_jnt.p_position,
                                  'z+', 'y+', 'vector',
                                  vectorUp=mVec_up)#mHeadHelper.getAxisVector('z-'))
                JOINT.freezeOrientation(mNeck_jnt.mNode)
                
                #mNeck_jnt.doName()
                
                mHead_jnt.p_parent = mNeck_jnt
                ml_joints.append(mNeck_jnt)
                
                #mNeck_jnt.rename(_l_namesToUse[0])
                for k,v in _l_namesToUse[0].iteritems():
                    mNeck_jnt.doStore(k,v)
                mNeck_jnt.doName()
            else:
                log.debug("|{0}| >> Multiple neck joint...".format(_str_func))
                
                _d = self.atBlockUtils('skeleton_getCreateDict', self.neckJoints +1)
                
                
                mVec_up = self.atUtils('prerig_get_upVector')
                
                ml_joints = JOINT.build_chain(_d['positions'][:-1], parent=True, worldUpAxis= mVec_up)
                
                for i,mJnt in enumerate(ml_joints):
                    #mJnt.rename(_l_namesToUse[i])
                    for k,v in _l_namesToUse[i].iteritems():
                        mJnt.doStore(k,v)
                    mJnt.doName()                
                
                #self.copyAttrTo(_baseNameAttrs[0],ml_joints[0].mNode,'cgmName',driven='target')
                
            mHead_jnt.p_parent = ml_joints[-1]
            ml_joints[0].parent = False
        else:
            mHead_jnt.parent = False
            #mHead_jnt.rename(_l_namesToUse[-1])
            
        ml_joints.append(mHead_jnt)
        
        for mJnt in ml_joints:
            mJnt.displayLocalAxis = 1
            mJnt.radius = _radius
        #if len(ml_joints) > 1:
            #mHead_jnt.radius = ml_joints[-1].radius * 3
    
        mRigNull.msgList_connect('moduleJoints', ml_joints)
        self.msgList_connect('moduleJoints', ml_joints)
        self.atBlockUtils('skeleton_connectToParent')
        for mJnt in ml_joints:mJnt.rotateOrder = 5
        
        return ml_joints
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {'head':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------

def rig_prechecks(self):
    try:
        _str_func = 'rig_prechecks'
        log.debug(cgmGEN.logString_start(_str_func))
        
        mBlock = self.mBlock
        
        #if mBlock.neckControls > 1:
            #self.l_precheckErrors.append("Don't have support for more than one neckControl yet. Found: {0}".format(mBlock.neckControls))
        
        if mBlock.segmentMidIKControl and mBlock.neckJoints < 2:
            mBlock.segmentMidIKControl = False
            self.l_precheckWarnings.append("Must have more than one neck joint with segmentMidIKControl, turning off")    
        if mBlock.neckJoints < mBlock.neckControls-1:
            self.l_precheckErrors.append("Neck control count must be equal or less than neck joint count")
            
        if mBlock.getEnumValueString('squashMeasure') == 'pointDist':
            self.l_precheckWarnings.append('pointDist squashMeasure mode not recommended')
            
        if mBlock.neckIK not in [0,3]:
            self.l_precheckErrors.append("Haven't setup neck mode: {0}".format(ATTR.get_enumValueString(mBlock.mNode,'neckIK')))
            
        #Checking our data points
        ml_pre = mBlock.msgList_get('prerigHandles')
        if mBlock.neckBuild and len(ml_pre) != mBlock.neckControls +1:
            self.l_precheckErrors.append('Not enough preHandles for the neckControls count. | neckControls: {0} | prerig: {1} | Excpected: {2}'.format(mBlock.neckControls,len(ml_pre),mBlock.neckControls+1))
            
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

@cgmGEN.Timer
def rig_dataBuffer(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_dataBuffer'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        mBlock = self.mBlock
        mModule = self.mModule
        mRigNull = self.mRigNull
        mPrerigNull = mBlock.prerigNull
        ml_formHandles = mBlock.msgList_get('formHandles')
        ml_handleJoints = mPrerigNull.msgList_get('handleJoints')
        mMasterNull = self.d_module['mMasterNull']
        
        self.mHandleFactory = mBlock.asHandleFactory()
        self.mRootFormHandle = ml_formHandles[0]
        
        #Vector ====================================================================================
        self.mVec_up = mBlock.atUtils('prerig_get_upVector')
        log.debug("|{0}| >> self.mVec_up: {1} ".format(_str_func,self.mVec_up))
        
        #Offset ============================================================================
        self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
        """
        str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
        if not mBlock.offsetMode:
            log.debug("|{0}| >> default offsetMode...".format(_str_func))
        else:
            str_offsetMode = ATTR.get_enumValueString(mBlock.mNode,'offsetMode')
            log.debug("|{0}| >> offsetMode: {1}".format(_str_func,str_offsetMode))
            
            l_sizes = []
            for mHandle in ml_formHandles:
                #_size_sub = SNAPCALLS.get_axisBox_size(mHandle)
                #l_sizes.append( MATH.average(_size_sub[1],_size_sub[2]) * .1 )
                _size_sub = POS.get_bb_size(mHandle,True)
                l_sizes.append( MATH.average(_size_sub) * .1 )            
            self.v_offset = MATH.average(l_sizes)
            #_size_midHandle = SNAPCALLS.get_axisBox_size(ml_formHandles[self.int_handleMidIdx])
            #self.v_offset = MATH.average(_size_midHandle[1],_size_midHandle[2]) * .1
            
            """
            
        log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))    
        log.debug(cgmGEN._str_subLine)
        
        self.str_neckDirection =  mBlock.getEnumValueString('neckDirection')
        log.debug("|{0}| >> self.str_neckDirection: {1}".format(_str_func,self.str_neckDirection))    
    
        
        #Squash stretch logic  =================================================================================
        log.debug("|{0}| >> Squash stretch..".format(_str_func))
        self.b_scaleSetup = mBlock.scaleSetup
        
        self.b_squashSetup = False
        
        self.d_squashStretch = {}
        self.d_squashStretchIK = {}
        
        _squashStretch = None
        if mBlock.squash:
            _squashStretch =  mBlock.getEnumValueString('squash')
            self.b_squashSetup = True
        self.d_squashStretch['squashStretch'] = _squashStretch
        
        _squashMeasure = None
        if mBlock.squashMeasure:
            _squashMeasure =  mBlock.getEnumValueString('squashMeasure')    
        self.d_squashStretch['squashStretchMain'] = _squashMeasure    
    
        _driverSetup = None
        if mBlock.ribbonAim:
            _driverSetup =  mBlock.getEnumValueString('ribbonAim')
        self.d_squashStretch['driverSetup'] = _driverSetup
    
        self.d_squashStretch['additiveScaleEnds'] = mBlock.scaleSetup
        self.d_squashStretch['extraSquashControl'] = mBlock.squashExtraControl
        self.d_squashStretch['squashFactorMax'] = mBlock.squashFactorMax
        self.d_squashStretch['squashFactorMin'] = mBlock.squashFactorMin
        
        log.debug("|{0}| >> self.d_squashStretch..".format(_str_func))    
        #pprint.pprint(self.d_squashStretch)
        
        #Check for mid control and even handle count to see if w need an extra curve
        if mBlock.segmentMidIKControl:
            if MATH.is_even(mBlock.neckControls):
                self.d_squashStretchIK['sectionSpans'] = 2
                
        if self.d_squashStretchIK:
            log.debug("|{0}| >> self.d_squashStretchIK..".format(_str_func))    
            #pprint.pprint(self.d_squashStretchIK)
        
        
        if not self.b_scaleSetup:
            pass
        
        log.debug("|{0}| >> self.b_scaleSetup: {1}".format(_str_func,self.b_scaleSetup))
        log.debug("|{0}| >> self.b_squashSetup: {1}".format(_str_func,self.b_squashSetup))
        
        log.debug(cgmGEN._str_subLine)
        
        #segintbaseindex =============================================================================
        str_ikBase = ATTR.get_enumValueString(mBlock.mNode,'ikBase')
        log.debug("|{0}| >> IK Base: {1}".format(_str_func,str_ikBase))    
        self.int_segBaseIdx = 0
        if str_ikBase in ['hips']:
            self.int_segBaseIdx = 1
        log.debug("|{0}| >> self.int_segBaseIdx: {1}".format(_str_func,self.int_segBaseIdx))
        
        log.debug(cgmGEN._str_subLine)
    
        #DynParents =============================================================================
        self.UTILS.get_dynParentTargetsDat(self)
        
        #rotateOrder =============================================================================
        _str_orientation = self.d_orientation['str']
        _l_orient = [_str_orientation[0],_str_orientation[1],_str_orientation[2]]
        self.ro_base = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
        self.ro_head = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
        self.ro_headLookAt = "{0}{2}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
        log.debug("|{0}| >> rotateOrder | self.ro_base: {1}".format(_str_func,self.ro_base))
        log.debug("|{0}| >> rotateOrder | self.ro_head: {1}".format(_str_func,self.ro_head))
        log.debug("|{0}| >> rotateOrder | self.ro_headLookAt: {1}".format(_str_func,self.ro_headLookAt))
    
        log.debug(cgmGEN._str_subLine)
        
        #mainRot axis =============================================================================
        """For twist stuff"""
        #_mainAxis = ATTR.get_enumValueString(mBlock.mNode,'mainRotAxis')
        #_axis = ['aim','up','out']
        #if _mainAxis == 'up':
        #    _upAxis = 'out'
        #else:
        #    _upAxis = 'up'
        
        self.v_twistUp = self.d_orientation.get('vector{0}'.format('Out'))
        log.debug("|{0}| >> twistUp | self.v_twistUp: {1}".format(_str_func,self.v_twistUp))        
    
        return True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


@cgmGEN.Timer
def rig_skeleton(self):
    try:
        _short = self.d_block['shortName']
        
        _str_func = 'rig_skeleton'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
            
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        ml_jointsToConnect = []
        ml_jointsToHide = []
        ml_joints = mRigNull.msgList_get('moduleJoints')
        self.d_joints['ml_moduleJoints'] = ml_joints
        ml_formHandles = mBlock.msgList_get('formHandles')
        
        BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'])
                                         #d_rotateOrders, d_preferredAngles)
        
        log.debug("|{0}| >> Head...".format(_str_func))  
        
        #ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock, ml_joints, 'rig', self.mRigNull,'rigJoints',blockNames=False)
        ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                               ml_joints, None ,
                                                               mRigNull,'rigJoints',
                                                               blockNames=False,
                                                               cgmType = 'rigJoint',
                                                               connectToSource = 'rig')    
        
        
        if self.mBlock.headAim:
            log.debug("|{0}| >> Head IK...".format(_str_func))              
            ml_fkHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'fk', self.mRigNull, 'fkHeadJoint', singleMode = True)
            
            ml_blendHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'blend', self.mRigNull, 'blendHeadJoint', singleMode = True)
            ml_aimHeadJoints = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_rigJoints[-1], 'aim', self.mRigNull, 'aimHeadJoint', singleMode = True)
            ml_jointsToConnect.extend(ml_fkHeadJoints + ml_aimHeadJoints)
            ml_jointsToHide.extend(ml_blendHeadJoints)
        
        #...Neck ---------------------------------------------------------------------------------------
        if self.mBlock.neckBuild:
            ml_segmentHandles = False
            
            log.debug("|{0}| >> Neck Build".format(_str_func))
            
            #mOrientHelper = ml_formHandles[1].orientHelper
            mOrientHelper =mBlock.orientHelper
            
            vec_chainUp = self.mVec_up

            
            #return mOrientHelper.getAxisVector('y+')
            ml_fkJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'fk',
                                                               'fkJoints',
                                                               mOrientHelper=mOrientHelper)
            self.ml_fkJoints = ml_fkJoints
            
            #ml_fkJoints[-1].doSnapTo(position=False,rotation=True)
            #JOINT.freezeOrientation(ml_fkJoints[-1].mNode)
            ml_jointsToHide.extend(ml_fkJoints)
            
            ml_parentJoints = ml_fkJoints
    
            if self.mBlock.neckIK:
                log.debug("|{0}| >> buildIK on. Building blend and IK chains...".format(_str_func))  
                ml_blendJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'blend','blendJoints')
                ml_ikJoints = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'ik','ikJoints')
                ml_jointsToConnect.extend(ml_ikJoints)
                ml_jointsToHide.extend(ml_blendJoints)
                ml_parentJoints = ml_blendJoints
                for i,mJnt in enumerate(ml_ikJoints):
                    if mJnt not in [ml_ikJoints[0],ml_ikJoints[-1]]:
                        mJnt.preferredAngle = mJnt.jointOrient
                        
                
                if mBlock.segmentMidIKControl:
                    log.debug("|{0}| >> Creating ik mid control...".format(_str_func))  
                    #Lever...
                    mMidIK = ml_rigJoints[0].doDuplicate(po=True)
                    mMidIK.cgmName = 'neck_segMid'
                    mMidIK.p_parent = False
                    mMidIK.doName()
                
                    mMidIK.p_position =POS.get_curveMidPointFromDagList([mObj.mNode for mObj in ml_rigJoints])
                    
                    
                    # DIST.get_average_position([ml_rigJoints[self.int_segBaseIdx].p_position,
                                       #                            ml_rigJoints[-1].p_position])
                
                    SNAP.aim(mMidIK.mNode, ml_rigJoints[-1].mNode, 'z+','y+','vector',
                             vec_chainUp)
                             #mBlock.rootUpHelper.getAxisVector('y+'))
                    JOINT.freezeOrientation(mMidIK.mNode)
                    mRigNull.connectChildNode(mMidIK,'controlSegMidIK','rigNull')
                    
                    
                if mBlock.neckIK and mBlock.neckControls > 1 :#...ribbon/spline
                    log.debug("|{0}| >> IK Drivers...".format(_str_func))            
                    ml_ribbonIKDrivers = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,ml_ikJoints, None, mRigNull,'ribbonIKDrivers', cgmType = 'ribbonIKDriver', indices=[0,-1])
                    for i,mJnt in enumerate(ml_ribbonIKDrivers):
                        mJnt.parent = False
                        mTar = ml_parentJoints[0]
                        if i == 0:
                            mTar = ml_parentJoints[0]
                        else:
                            mTar = ml_parentJoints[-1]
                        mJnt.doCopyNameTagsFromObject(mTar.mNode,ignore=['cgmType'])
                        mJnt.doName()
                    ml_jointsToConnect.extend(ml_ribbonIKDrivers)
                    
            if mBlock.neckJoints > mBlock.neckControls:
                log.debug("|{0}| >> Handles...".format(_str_func))            
                ml_segmentHandles = BLOCKUTILS.skeleton_buildHandleChain(mBlock,'handle',
                                                                         'handleJoints',
                                                                         clearType=True)
                for i,mObj in enumerate(ml_segmentHandles):
                    if i:
                        mObj.p_parent = ml_segmentHandles[i-1]
                        
                JOINT.orientChain(ml_segmentHandles,
                                  worldUpAxis=vec_chainUp)
                for i,mJnt in enumerate(ml_segmentHandles):
                    mJnt.parent = ml_parentJoints[i]
                
                log.debug("|{0}| >> segment necessary...".format(_str_func))
                ml_segmentChain = BLOCKUTILS.skeleton_buildDuplicateChain(mBlock,
                                                                          ml_joints,
                                                                          None, mRigNull,
                                                                          'segmentJoints',
                                                                          cgmType = 'segJnt')
                JOINT.orientChain(ml_segmentChain,
                                  worldUpAxis=vec_chainUp)
                
                
                for i,mJnt in enumerate(ml_rigJoints):
                    if mJnt != ml_rigJoints[-1]:
                        mJnt.parent = ml_segmentChain[i]
                        mJnt.connectChildNode(ml_segmentChain[i],'driverJoint','sourceJoint')#Connect
                    else:
                        mJnt.p_parent = False
                        
                ml_jointsToHide.extend(ml_segmentChain)
            else:
                for i,mJnt in enumerate(ml_rigJoints):
                    mJnt.p_parent = ml_parentJoints[i]
                
            """
            if mBlock.neckControls > 2 and ml_segmentHandles:
                log.debug("|{0}| >> IK Drivers...".format(_str_func))            
                ml_baseIKDrivers = BLOCKUTILS.skeleton_buildDuplicateChain(ml_segmentHandles,
                                                                           None, mRigNull,
                                                                           'baseIKDrivers',
                                                                           cgmType = 'baseIKDriver', indices=[0,-1])
                for mJnt in ml_baseIKDrivers:
                    mJnt.parent = False
                ml_jointsToConnect.extend(ml_baseIKDrivers)"""
                
                
        #...joint hide -----------------------------------------------------------------------------------
        for mJnt in ml_jointsToHide:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001
                
        #...connect... 
        self.fnc_connect_toRigGutsVis( ml_jointsToConnect )        
        
        return
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

#@cgmGEN.Timer
def rig_shapes(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_shapes'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        ml_prerigHandles = self.mBlock.atBlockUtils('prerig_getHandleTargets')
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        mHeadHelper = ml_prerigHandles[-1]
        mBlock = self.mBlock
        _baseNameAttrs = ATTR.datList_getAttrs(mBlock.mNode,'nameList')    
        ml_formHandles = mBlock.msgList_get('formHandles')
        mHandleFactory = mBlock.asHandleFactory()
        mRigNull = self.mRigNull
        
        #l_toBuild = ['segmentFK_Loli','segmentIK']
        #mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
        
        #Get our base size from the block
        _jointOrientation = self.d_orientation['str']
        
        _size = DIST.get_bb_size(ml_formHandles[0].mNode,True,True)
        _side = BLOCKUTILS.get_side(self.mBlock)
        _short_module = self.mModule.mNode
        ml_joints = self.d_joints['ml_moduleJoints']
        _offset = self.v_offset
        
        #Logic ====================================================================================
    
        
        #Head=============================================================================================
        if mBlock.headAim:
            log.debug("|{0}| >> Head aim...".format(_str_func))  
            
            _ikPos =DIST.get_pos_by_vec_dist(ml_prerigHandles[-1].p_position,
                                             MATH.get_obj_vector(ml_rigJoints[-1].mNode,'y-'),
                                             _size * 1.5)
            
            ikCurve = CURVES.create_fromName('sphere2',_size/3)
            textCrv = CURVES.create_text('head',_size/4)
            CORERIG.shapeParent_in_place(ikCurve,textCrv,False)
            
            mLookAt = cgmMeta.validateObjArg(ikCurve,'cgmObject',setClass=True)
            mLookAt.p_position = _ikPos
            
            ATTR.copy_to(_short_module,'cgmName',mLookAt.mNode,driven='target')
            #mIK.doStore('cgmName','head')
            mLookAt.doStore('cgmTypeModifier','lookAt')
            mLookAt.doName()
            
            CORERIG.colorControl(mLookAt.mNode,_side,'main')
            
            self.mRigNull.connectChildNode(mLookAt,'lookAt','rigNull')#Connect
        
        
        #Head control....-------------------------------------------------------------------------------
        if not mBlock.neckBuild:
            b_FKIKhead = False
            if mBlock.neckControls > 1 and mBlock.neckBuild: 
                log.debug("|{0}| >> FK/IK head necessary...".format(_str_func))          
                b_FKIKhead = True            
            
            

            
            #IK ----------------------------------------------------------------------------------
            mIK = ml_rigJoints[-1].doCreateAt()
            #CORERIG.shapeParent_in_place(mIK,l_lolis,False)
            CORERIG.shapeParent_in_place(mIK,ml_formHandles[0].mNode,True)
            mIK = cgmMeta.validateObjArg(mIK,'cgmObject',setClass=True)
            
            mBlock.copyAttrTo(_baseNameAttrs[-1],mIK.mNode,'cgmName',driven='target')
            
            #ATTR.copy_to(_short_module,'cgmName',mIK.mNode,driven='target')
            #mIK.doStore('cgmName','head')
            if b_FKIKhead:mIK.doStore('cgmTypeModifier','ik')
            mIK.doName()    
            CORERIG.colorControl(mIK.mNode,_side,'main')
            self.mRigNull.connectChildNode(mIK,'headIK','rigNull')#Connect
            self.mRigNull.connectChildNode(mIK,'controlIK','rigNull')#Connect
            
            self.mRigNull.connectChildNode(mIK,'settings','rigNull')#Connect
            
            
            """                
                if b_FKIKhead:
                    l_lolis = []
                    l_starts = []
                    for axis in ['x+','z-','x-']:
                        pos = mHeadHelper.getPositionByAxisDistance(axis, _size * .75)
                        ball = CURVES.create_fromName('sphere',_size/10)
                        mBall = cgmMeta.cgmObject(ball)
                        mBall.p_position = pos
                        mc.select(cl=True)
                        p_end = DIST.get_closest_point(mHeadHelper.mNode, ball)[0]
                        p_start = mHeadHelper.getPositionByAxisDistance(axis, _size * .25)
                        l_starts.append(p_start)
                        line = mc.curve (d=1, ep = [p_start,p_end], os=True)
                        l_lolis.extend([ball,line])
                        
                    mFK = ml_fkJoints[-1]
                    CORERIG.shapeParent_in_place(mFK,l_lolis,False)
                    mFK.doStore('cgmTypeModifier','fk')
                    mFK.doName()
                    
                    CORERIG.colorControl(mFK.mNode,_side,'main')
                    
                    self.mRigNull.connectChildNode(mFK,'headFK','rigNull')#Connect
                else:
                    self.mRigNull.connectChildNode(mIK,'settings','rigNull')#Connect
                    """
            
                
        else:
            mHeadTar = ml_rigJoints[-1]
            #mFKHead = ml_rigJoints[-1].doCreateAt()
            
            #CORERIG.shapeParent_in_place(mFKHead,ml_formHandles[0].mNode,True)
            #mFKHead = cgmMeta.validateObjArg(mFKHead,'cgmObject',setClass=True)
            #mFKHead.doCopyNameTagsFromObject(mHeadTar.mNode,
            #                                ignore=['cgmType','cgmTypeModifier'])        
            #mFKHead.doStore('cgmTypeModifier','fk')
            #mFKHead.doName()

            #Fix fk.... ---------------------------------------------------------------------------
            CORERIG.shapeParent_in_place(ml_fkJoints[-1].mNode,ml_formHandles[0].mNode,True)            
            mFKHead = ml_fkJoints[-1]                        
            mFKHead.doCopyNameTagsFromObject(mHeadTar.mNode,
                                             ignore=['cgmType','cgmTypeModifier'])
            mFKHead.doStore('cgmTypeModifier','fk')
            mFKHead.doName()
                                             
            mHandleFactory.color(mFKHead.mNode,controlType='main')
            

            
            if mBlock.neckIK:
                ml_blendJoints = mRigNull.msgList_get('blendJoints')
                mIKHead = mBlock.ikOrientHandle.doCreateAt(setClass=True)
                mIKHead.doCopyNameTagsFromObject(mFKHead.mNode)
                mIKHead.doStore('cgmTypeModifier','ik')
                mIKHead.doName()
                
                CORERIG.shapeParent_in_place(mIKHead.mNode, mFKHead.mNode)                            
                
                #mIKHead = mFKHead.doDuplicate(po=False)
                #mIKHead.doStore('cgmTypeModifier','ik')
                #mIKHead.doName()
                #mIKHead.p_parent = False
                
                #match orient
                #CORERIG.match_orientation(mIKHead.mNode, mBlock.ikOrientHandle.mNode)
                mIKHeadDriver = mFKHead.doCreateAt(setClass=True)
                mIKHeadDriver.doStore('cgmType','ikHeadDriver')
                mIKHeadDriver.p_parent = mIKHead.mNode
                mIKHeadDriver.doName()
                mIKHead.connectChildNode(mIKHeadDriver,'driver','control')#Connect
                
                
                self.mRigNull.connectChildNode(mIKHead,'controlIK','rigNull')#Connect
                self.mRigNull.connectChildNode(mIKHead,'headIK','rigNull')#Connect
                
 
                
                #Base IK...---------------------------------------------------------------------------------
                log.debug("|{0}| >> baseIK...".format(_str_func))
                ml_ikJoints = mRigNull.msgList_get('ikJoints')
                #mIK_formHandle = self.mRootFormHandle
                #bb_ik = mHandleFactory.get_axisBox_size(mIK_formHandle.mNode)
                #_ik_shape = CURVES.create_fromName('sphere', size = bb_ik)
            
                _ik_shape = self.atBuilderUtils('shapes_fromCast',
                                                targets = [ mObj for mObj in ml_rigJoints[:1]],
                                                offset = _offset,
                                                mode = 'castHandle')[0].mNode
            
                mIKBaseShape = cgmMeta.validateObjArg(_ik_shape, 'cgmObject',setClass=True)
            
                mIKBaseCrv = ml_ikJoints[0].doCreateAt()
                mIKBaseCrv.doCopyNameTagsFromObject(ml_fkJoints[0].mNode,ignore=['cgmType'])
                CORERIG.shapeParent_in_place(mIKBaseCrv.mNode, mIKBaseShape.mNode, False)                            
            
                mIKBaseCrv.doStore('cgmTypeModifier','ikBase')
                mIKBaseCrv.doName()
            
                mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main',transparent=True)
            
                mHandleFactory.color(mIKBaseCrv.mNode, controlType = 'main')        
                self.mRigNull.connectChildNode(mIKBaseCrv,'controlIKBase','rigNull')#Connect                    
    
            self.mRigNull.connectChildNode(mFKHead,'headFK','rigNull')#Connect
            
                    
            
            """
            if b_FKIKhead:
                l_lolis = []
                l_starts = []
                for axis in ['x+','z-','x-']:
                    pos = mHeadHelper.getPositionByAxisDistance(axis, _size * .75)
                    ball = CURVES.create_fromName('sphere',_size/10)
                    mBall = cgmMeta.cgmObject(ball)
                    mBall.p_position = pos
                    mc.select(cl=True)
                    p_end = DIST.get_closest_point(mHeadHelper.mNode, ball)[0]
                    p_start = mHeadHelper.getPositionByAxisDistance(axis, _size * .25)
                    l_starts.append(p_start)
                    line = mc.curve (d=1, ep = [p_start,p_end], os=True)
                    l_lolis.extend([ball,line])
                    
                mFK = ml_fkJoints[-1]
                CORERIG.shapeParent_in_place(mFK,l_lolis,False)
                mFK.doStore('cgmTypeModifier','fk')
                mFK.doName()
                
                CORERIG.colorControl(mFK.mNode,_side,'main')
                
                self.mRigNull.connectChildNode(mFK,'headFK','rigNull')#Connect        
                 """
            
            #Settings =================================================================================
            mShape = mBlock.getMessageAsMeta('settingsHelper')
            mSettings = mShape.doDuplicate(po=False)
            mSettings.p_parent = False
            ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
            #mSettings.doStore('cgmName','head')
            mSettings.doStore('cgmTypeModifier','settings')
            mSettings.doName()
            #CORERIG.colorControl(mSettings.mNode,_side,'sub')            
            """
            pos = mHeadHelper.getPositionByAxisDistance('z+', _size * .75)
            
            mTar = ml_rigJoints[-1]
            
            vector = mHeadHelper.getAxisVector('y+')
            newPos = DIST.get_pos_by_vec_dist(pos,vector,_size * .5)
        
            settings = CURVES.create_fromName('gear',_size/5,'x+')
            mSettingsShape = cgmMeta.validateObjArg(settings,'cgmObject')
            mSettings = cgmMeta.validateObjArg(mTar.doCreateAt(),'cgmObject',setClass=True)
            
            mSettings.p_position = newPos
            mSettingsShape.p_position = newPos
        
            ATTR.copy_to(_short_module,'cgmName',mSettings.mNode,driven='target')
            #mSettings.doStore('cgmName','head')
            mSettings.doStore('cgmTypeModifier','settings')
            mSettings.doName()
            #CORERIG.colorControl(mSettings.mNode,_side,'sub')
            
            SNAP.aim_atPoint(mSettingsShape.mNode,
                             mTar.p_position,
                             aimAxis=_jointOrientation[0]+'+',
                             mode = 'vector',
                             vectorUp= mTar.getAxisVector(_jointOrientation[0]+'-'))
            
            CORERIG.shapeParent_in_place(mSettings.mNode, mSettingsShape.mNode,False)"""
            mHandleFactory.color(mSettings.mNode,controlType='sub')
            
            self.mRigNull.connectChildNode(mSettings,'settings','rigNull')#Connect
            
            #Neck ================================================================================
            log.debug("|{0}| >> Neck...".format(_str_func))
            #Root -------------------------------------------------------------------------------------------
            #Grab form handle root - use for sizing, make ball
            mNeckBaseHandle = self.mBlock.msgList_get('formHandles')[1]
            size_neck = DIST.get_bb_size(mNeckBaseHandle.mNode,True,True) /2
    
            mRoot = ml_joints[0].doCreateAt()
            mRootCrv = cgmMeta.validateObjArg(CURVES.create_fromName('locatorForm', size_neck),
                                              'cgmObject',setClass=True)
            mRootCrv.doSnapTo(ml_joints[0])
    
            #SNAP.go(mRootCrv.mNode, ml_joints[0].mNode,position=False)
    
            CORERIG.shapeParent_in_place(mRoot.mNode,mRootCrv.mNode, False)
    
            ATTR.copy_to(_short_module,'cgmName',mRoot.mNode,driven='target')
            mRoot.doStore('cgmTypeModifier','root')
            mRoot.doName()
    
            CORERIG.colorControl(mRoot.mNode,_side,'sub')
            self.mRigNull.connectChildNode(mRoot,'rigRoot','rigNull')#Connect
    
            #controlSegMidIK =============================================================================
            if mRigNull.getMessage('controlSegMidIK'):
                log.debug("|{0}| >> controlSegMidIK...".format(_str_func))            
                mControlSegMidIK = mRigNull.getMessage('controlSegMidIK',asMeta=1)[0]
                
                ml_shapes = self.atBuilderUtils('shapes_fromCast',
                                                targets = mControlSegMidIK,
                                                offset = _offset,
                                                mode = 'simpleCast')#'simpleCast  limbSegmentHandle
                
                CORERIG.shapeParent_in_place(mControlSegMidIK.mNode, ml_shapes[0].mNode,False)
                
                mControlSegMidIK.doStore('cgmTypeModifier','ik')
                mControlSegMidIK.doStore('cgmType','handle')
                mControlSegMidIK.doName()            
        
                mHandleFactory.color(mControlSegMidIK.mNode, controlType = 'sub')
            
    
            #FK/Ik =======================================================================================    
            ml_fkShapes = self.atBuilderUtils('shapes_fromCast', mode = 'frameHandle')#frameHandle
    
            mHandleFactory.color(ml_fkShapes[0].mNode, controlType = 'main')        
            CORERIG.shapeParent_in_place(ml_fkJoints[0].mNode, ml_fkShapes[0].mNode, True, replaceShapes=True)
    
            for i,mShape in enumerate(ml_fkJoints[:-1]):
                mShape = ml_fkShapes[i]
                mHandleFactory.color(mShape.mNode, controlType = 'main')        
                CORERIG.shapeParent_in_place(ml_fkJoints[i].mNode, mShape.mNode, True, replaceShapes=True)
                mShape.delete()
                
        
            for mShape in ml_fkShapes:
                try:mShape.delete()
                except:pass
                
        #Direct Controls =============================================================================
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
            
        RIGSHAPES.direct(self,ml_rigJoints)
        
        """        
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        
        _size_direct = DIST.get_bb_size(ml_formHandles[-1].mNode,True,True)
        
        d_direct = {'size':_size_direct/2}
            
        ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                              ml_rigJoints,
                                              mode ='direct',**d_direct)
        
        for i,mCrv in enumerate(ml_directShapes):
            CORERIG.colorControl(mCrv.mNode,_side,'sub')
            CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
            for mShape in ml_rigJoints[i].getShapes(asMeta=True):
                mShape.doName()"""
    
        for mJnt in ml_rigJoints:
            try:
                mJnt.drawStyle =2
            except:
                mJnt.radius = .00001    
        
    
        #Handles ===========================================================================================
        ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
    
        if ml_handleJoints:
            log.debug("|{0}| >> Found Handle joints...".format(_str_func))
            #l_uValues = MATH.get_splitValueList(.01,.99, len(ml_handleJoints))
            ml_handleShapes = self.atBuilderUtils('shapes_fromCast',
                                                  targets = ml_handleJoints,
                                                  offset = _offset,
                                                  mode = 'limbSegmentHandle')#'segmentHandle') limbSegmentHandle limbSegmentHandleBack
    
    
            for i,mCrv in enumerate(ml_handleShapes):
                log.debug("|{0}| >> Shape: {1} | Handle: {2}".format(_str_func,mCrv.mNode,ml_handleJoints[i].mNode ))                
                mHandleFactory.color(mCrv.mNode, controlType = 'sub')            
                CORERIG.shapeParent_in_place(ml_handleJoints[i].mNode, 
                                             mCrv.mNode, False,
                                             replaceShapes=True)
    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        



@cgmGEN.Timer
def rig_controls(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_controls'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
      
        mRigNull = self.mRigNull
        mBlock = self.mBlock
        ml_controlsAll = []#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
        mSettings = mRigNull.settings
        
        mHeadFK = mRigNull.getMessageAsMeta('headFK')
        mHeadIK = mRigNull.getMessageAsMeta('headIK')
        
        d_controlSpaces = self.atBuilderUtils('get_controlSpaceSetupDict')    
        
        
        # Drivers ==========================================================================================    
        if self.mBlock.neckBuild:
            if self.mBlock.neckIK:
                mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',minValue=0,maxValue=1,lock=False,keyable=True)
        
            #>> vis Drivers ==============================================================================	
            mPlug_visSub = self.atBuilderUtils('build_visModuleMD','visSub')
            mPlug_visRoot = self.atBuilderUtils('build_visModuleMD','visRoot')


        mPlug_visDirect = self.atBuilderUtils('build_visModuleMD','visDirect')

        # Connect to visModule ...
        ATTR.connect(self.mPlug_visModule.p_combinedShortName, 
                     "{0}.visibility".format(self.mDeformNull.mNode))

        
        if self.mBlock.headAim:        
            mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',
                                        minValue=0,maxValue=1,
                                        lock=False,keyable=True)
            
            
        #>> Neck build ======================================================================================
        if self.mBlock.neckBuild:
            log.debug("|{0}| >> Neck...".format(_str_func))
            
            #Root -------------------------------------------------------------------------------------------
            if not mRigNull.getMessage('rigRoot'):
                raise ValueError,"No rigRoot found"
            
            mRoot = mRigNull.rigRoot
            log.debug("|{0}| >> Found rigRoot : {1}".format(_str_func, mRoot))
            
            
            _d = MODULECONTROL.register(mRoot,
                                        addDynParentGroup = True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True)
            
            mRoot = _d['mObj']
            mRoot.masterGroup.parent = mRootParent
            mRootParent = mRoot#Change parent going forward...
            ml_controlsAll.append(mRoot)
            
            for mShape in mRoot.getShapes(asMeta=True):
                ATTR.connect(mPlug_visRoot.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                
            
            #FK controls -------------------------------------------------------------------------------------
            log.debug("|{0}| >> FK Controls...".format(_str_func))
            ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
            ml_parentJoints = ml_fkJoints            
            ml_blendJoints = mRigNull.msgList_get('blendJoints')
            if ml_blendJoints:
                ml_parentJoints = ml_blendJoints
            
            ml_fkJoints[0].parent = mRoot
            ml_controlsAll.extend(ml_fkJoints)
            
            if self.d_module['mirrorDirection'] == 'Centre':
                _fkMirrorAxis = 'translateY,translateZ,rotateY,rotateZ'
            else:
                _fkMirrorAxis = 'translateY,translateZ'
            
            for i,mObj in enumerate(ml_fkJoints):
                d_buffer = MODULECONTROL.register(mObj,
                                                  mirrorSide= self.d_module['mirrorDirection'],
                                                  mirrorAxis=_fkMirrorAxis,
                                                  makeAimable = True)
        
                mObj = d_buffer['mObj']
                #mObj.axisAim = "%s+"%self._go._jointOrientation[0]
                #mObj.axisUp= "%s+"%self._go._jointOrientation[1]	
                #mObj.axisOut= "%s+"%self._go._jointOrientation[2]
                #try:i_obj.drawStyle = 2#Stick joint draw style	    
                #except:self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
                ATTR.set_hidden(mObj.mNode,'radius',True)
                
                
            
            mControlBaseIK = mRigNull.getMessageAsMeta('controlIKBase')
            if mControlBaseIK:
                mControlBaseIK = mRigNull.controlIKBase
                log.debug("|{0}| >> Found controlBaseIK : {1}".format(_str_func, mControlBaseIK))
                
                _d = MODULECONTROL.register(mControlBaseIK,
                                            addDynParentGroup = True, 
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = True,
                                            **d_controlSpaces)
                                            
                
                mControlBaseIK = _d['mObj']
                mControlBaseIK.masterGroup.parent = mRootParent
                ml_controlsAll.append(mControlBaseIK)
                
                #Register our snapToTarget -------------------------------------------------------------
                self.atUtils('get_switchTarget', mControlBaseIK,ml_parentJoints[0])
    
                
                
            mControlSegMidIK = False
            
            #controlSegMidIK =============================================================================
            if mRigNull.getMessage('controlSegMidIK'):
                mControlSegMidIK = mRigNull.controlSegMidIK
                log.debug("|{0}| >> found controlSegMidIK: {1}".format(_str_func,mControlSegMidIK))
                
                _d = MODULECONTROL.register(mControlSegMidIK,
                                            addDynParentGroup = True, 
                                            mirrorSide= self.d_module['mirrorDirection'],
                                            mirrorAxis="translateX,rotateY,rotateZ",
                                            makeAimable = True,
                                            **d_controlSpaces)
                
                
                mControlSegMidIK = _d['mObj']
                mControlSegMidIK.masterGroup.parent = mRootParent
                ml_controlsAll.append(mControlSegMidIK)
            
                #Register our snapToTarget -------------------------------------------------------------
                self.atUtils('get_switchTarget', mControlSegMidIK,ml_parentJoints[ MATH.get_midIndex(len(ml_parentJoints))])        
    
    
        #ikHead ========================================================================================
        if mHeadIK:
            log.debug("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
            
            _d = MODULECONTROL.register(mHeadIK,
                                        addDynParentGroup = True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
            
            mHeadIK = _d['mObj']
            mHeadIK.masterGroup.parent = mRootParent
            ml_controlsAll.append(mHeadIK)
            
            if mBlock.neckBuild:
                self.atUtils('get_switchTarget', mHeadIK, ml_parentJoints[-1])
        
        
        #>> headLookAt ========================================================================================
        mHeadLookAt = False
        if mRigNull.getMessage('lookAt'):
            mHeadLookAt = mRigNull.lookAt
            log.debug("|{0}| >> Found lookAt : {1}".format(_str_func, mHeadLookAt))
            MODULECONTROL.register(mHeadLookAt,
                                   typeModifier='lookAt',
                                   addDynParentGroup = True, 
                                   mirrorSide= self.d_module['mirrorDirection'],
                                   mirrorAxis="translateX,rotateY,rotateZ",
                                   makeAimable = False,
                                   **d_controlSpaces)
            mHeadLookAt.masterGroup.parent = mRootParent
            ml_controlsAll.append(mHeadLookAt)
            
            if mHeadIK:
                mHeadLookAt.doStore('controlIK', mHeadIK)
            if mHeadFK:
                mHeadLookAt.doStore('controlFK', mHeadFK)
                
            #int_mid = MATH.get_midIndex(len(ml_blend))
    
            
        
        #>> settings ========================================================================================
        if mHeadFK:
            _d = MODULECONTROL.register(mHeadFK,
                                        addDynParentGroup = True,
                                        mirrorSide= self.d_module['mirrorDirection'],
                                        mirrorAxis="translateX,rotateY,rotateZ",
                                        makeAimable = True,
                                        **d_controlSpaces)
            
            mHeadFK = _d['mObj']
            mHeadFK.masterGroup.parent = mRootParent
            ml_controlsAll.append(mHeadFK)
            
            if mBlock.neckBuild:
                self.atUtils('get_switchTarget', mHeadFK, ml_parentJoints[-1])            
            
            
            #Settings...
            mSettings = mRigNull.settings
            log.debug("|{0}| >> Found settings : {1}".format(_str_func, mSettings))
            
            MODULECONTROL.register(mSettings,
                                   mirrorSide= self.d_module['mirrorDirection'],
                                   )
            
            mSettings.masterGroup.parent = ml_parentJoints[-1]
            ml_controlsAll.append(mSettings)
        
        #>> handleJoints ========================================================================================
        ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
        if ml_handleJoints:
            log.debug("|{0}| >> Found Handle Joints...".format(_str_func))
            
            ml_controlsAll.extend(ml_handleJoints)
            
            for i,mObj in enumerate(ml_handleJoints):
                d_buffer = MODULECONTROL.register(mObj,
                                                  mirrorSide= self.d_module['mirrorDirection'],
                                                  mirrorAxis="translateX,rotateY,rotateZ",
                                                  makeAimable = False)
        
                mObj = d_buffer['mObj']
                ATTR.set_hidden(mObj.mNode,'radius',True)
                
                for mShape in mObj.getShapes(asMeta=True):
                    ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
            
                
        #>> Direct Controls ========================================================================================
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        ml_controlsAll.extend(ml_rigJoints)
        
        for i,mObj in enumerate(ml_rigJoints):
            d_buffer = MODULECONTROL.register(mObj,
                                              typeModifier='direct',
                                              mirrorSide= self.d_module['mirrorDirection'],
                                              mirrorAxis="translateX,rotateY,rotateZ",
                                              makeAimable = False)
            mObj = d_buffer['mObj']
            ATTR.set_hidden(mObj.mNode,'radius',True)        
            if mObj.hasAttr('cgmIterator'):
                ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                
            for mShape in mObj.getShapes(asMeta=True):
                ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                    
                
        #ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        #self.atBuilderUtils('check_nameMatches', ml_controlsAll)
        
        mHandleFactory = mBlock.asHandleFactory()
        for mCtrl in ml_controlsAll:
            ATTR.set(mCtrl.mNode,'rotateOrder',self.ro_base)
            
            if mCtrl.hasAttr('radius'):
                ATTR.set(mCtrl.mNode,'radius',0)        
            
            ml_pivots = mCtrl.msgList_get('spacePivots')
            if ml_pivots:
                log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
                for mPivot in ml_pivots:
                    mHandleFactory.color(mPivot.mNode, controlType = 'sub')            
                    ml_controlsAll.append(mPivot)
        
        if mHeadIK:
            ATTR.set(mHeadIK.mNode,'rotateOrder',self.ro_head)
        if mHeadLookAt:
            ATTR.set(mHeadLookAt.mNode,'rotateOrder',self.ro_headLookAt)
            
        
        mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        mRigNull.moduleSet.extend(ml_controlsAll)

        return 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)        

    try:#>>>> IK Segments =============================================================================	 
        for i_obj in ml_shapes_segmentIK:
            d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='segIK',
                                                       mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",	                                               
                                                       setRotateOrder=2)       
            i_obj = d_buffer['instance']
            i_obj.masterGroup.parent = mi_go._i_deformNull.mNode
            mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)	    

        mi_go._i_rigNull.msgList_connect('segmentHandles',ml_shapes_segmentIK,'rigNull')
        ml_controlsAll.extend(ml_shapes_segmentIK)	
    except Exception,error:raise Exception,"IK Segments! | error: {0}".format(error)


@cgmGEN.Timer
def rig_segments(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_neckSegment'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))    
        
        if not self.mBlock.neckBuild:
            log.debug("|{0}| >> No neck build optioned".format(_str_func))                      
            return True
        
        log.debug("|{0}| >> ...".format(_str_func))  
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mDeformNull
        mModule = self.mModule
        mRoot = mRigNull.rigRoot
        
        ml_segJoints = mRigNull.msgList_get('segmentJoints')
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        #ml_rigJoints[0].parent = ml_blendJoints[0]
        #ml_rigJoints[-1].parent = mHeadFK
        ml_handleJoints = mRigNull.msgList_get('handleJoints')
        
        
        if not ml_segJoints:
            log.debug("|{0}| >> No segment joints. No segment setup necessary.".format(_str_func))
            return True    
        
        for mJnt in ml_segJoints:
            mJnt.drawStyle = 2
            ATTR.set(mJnt.mNode,'radius',0)    
        
        #>> Ribbon setup ========================================================================================
        log.debug("|{0}| >> Ribbon setup...".format(_str_func))    
        
        ml_influences = copy.copy(ml_handleJoints)
        
        _settingsControl = None
        if mBlock.squashExtraControl:
            _settingsControl = mRigNull.settings.mNode
        
        _extraSquashControl = mBlock.squashExtraControl
               
        res_segScale = self.UTILS.get_blockScale(self,'segMeasure')
        mPlug_masterScale = res_segScale[0]
        mMasterCurve = res_segScale[1]
        
        mSegMidIK = mRigNull.getMessageAsMeta('controlSegMidIK')
        if mSegMidIK and mBlock.neckControls == 1:
            log.debug("|{0}| >> seg mid IK control found...".format(_str_func))
            ml_influences.append(mSegMidIK)
        
        _d = {'jointList':[mObj.mNode for mObj in ml_segJoints],
              'baseName':'{0}_rigRibbon'.format(self.d_module['partName']),
              'connectBy':'constraint',
              'extendEnds':True,
              'masterScalePlug':mPlug_masterScale,
              'paramaterization':mBlock.getEnumValueString('ribbonParam'),          
              'influences':ml_influences,
              'settingsControl':_settingsControl,
              'attachEndsToInfluences':False,
              'moduleInstance':mModule}
        
        if mSegMidIK:
            _d['sectionSpans'] = 2
            
        _d.update(self.d_squashStretch)
        res_ribbon = IK.ribbon(**_d)
        
        ml_surfaces = res_ribbon['mlSurfaces']
        
        mMasterCurve.p_parent = mRoot    
        
        ml_segJoints[0].parent = mRoot
        
        if self.b_squashSetup:
            for mJnt in ml_segJoints:
                mJnt.segmentScaleCompensate = False
                if mJnt == ml_segJoints[0]:
                    continue
                mJnt.p_parent = ml_segJoints[0].p_parent    
        
        return
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
    #>> Ribbon setup ========================================================================================
    log.debug("|{0}| >> Ribbon setup...".format(_str_func))
    #reload(IK)
    #mSurf = IK.ribbon([mObj.mNode for mObj in ml_rigJoints], baseName = mBlock.cgmName, connectBy='constraint', msgDriver='masterGroup', moduleInstance = mModule)
    mSurf = IK.ribbon([mObj.mNode for mObj in ml_segJoints],
                      baseName = mBlock.cgmName,
                      driverSetup='stable',
                      connectBy='constraint',
                      moduleInstance = mModule)

    mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_handleJoints],
                                                          mSurf.mNode,
                                                          tsb=True,
                                                          maximumInfluences = 2,
                                                          normalizeWeights = 1,dropoffRate=2.5),
                                          'cgmNode',
                                          setClass=True)

    mSkinCluster.doStore('cgmName', mSurf)
    mSkinCluster.doName()    

    cgmGEN.func_snapShot(vars())
    
    ml_segJoints[0].parent = mRoot
    
    
    """
    #>> Neck build ======================================================================================
    if mBlock.neckJoints > 1:
        
        if mBlock.neckControls == 1:
            log.debug("|{0}| >> Simple neck segment...".format(_str_func))
            ml_segmentJoints[0].parent = ml_blendJoints[0] #ml_handleJoints[0]
            ml_segmentJoints[-1].parent = mHeadIK # ml_handleJoints[-1]
            RIGCONSTRAINT.setup_linearSegment(ml_segmentJoints)
            
        else:
            log.debug("|{0}| >> Neck segment...".format(_str_func))    """
            



@cgmGEN.Timer
def rig_frame(self):
    try:
        _short = self.d_block['shortName']
        _str_func = ' rig_rigFrame'
        
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))    
    
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mRootParent = self.mDeformNull
        mModule = self.mModule
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        ml_fkJoints = mRigNull.msgList_get('fkJoints')
        ml_parentJoints = ml_fkJoints
        
        ml_handleJoints = self.mRigNull.msgList_get('handleJoints')
        ml_baseIKDrivers = self.mRigNull.msgList_get('baseIKDrivers')
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        ml_segBlendTargets = copy.copy(ml_blendJoints)
        mSegMidIK = mRigNull.getMessageAsMeta('controlSegMidIK')
        
        
        mHeadFK = False
        
        mHeadFK = mRigNull.getMessageAsMeta('headFK')
        mHeadIK = mRigNull.getMessageAsMeta('headIK')
        if mHeadIK and mBlock.neckBuild:
            log.debug("|{0}| >> Found headIK : {1}".format(_str_func, mHeadIK))
            mTopHandleDriver = mHeadIK.driver
        elif mHeadFK:
            mTopDriver = mHeadFK
            mTopHandleDriver = mHeadFK
        else:
            mTopDriver = mHeadIK
            mTopHandleDriver = mHeadIK
            
            
        _ikNeck = mBlock.getEnumValueString('neckIK')
        
        if ml_blendJoints:
            mHeadStuffParent = ml_blendJoints[-1]
            mAimParent = ml_blendJoints[-1]
            mTopTwistDriver = ml_blendJoints[-1]
            ml_parentJoints = ml_blendJoints
        else:
            mHeadStuffParent = mHeadFK
            mAimParent = mHeadFK
            mTopTwistDriver = mHeadFK
            #mAimParent = self.mDeformNull
            
        #Tmp parent till logic worked out
        ml_rigJoints[-1].masterGroup.parent = mTopHandleDriver
        
        #>> headFK ========================================================================================
        """We use the ik head sometimes."""
        
        if mBlock.headAim:
            log.debug("|{0}| >> HeadAim setup...".format(_str_func))
            mSettings = mRigNull.settings
            
            mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
            
            mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
            mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
            mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
            mTopHandleDriver = mHeadBlendJoint
            mHeadLookAt = mRigNull.lookAt
            
            if ml_handleJoints:
                mTopDriver = ml_handleJoints[-1].doCreateAt()
            else:
                mTopDriver = mHeadFKJoint.doCreateAt()#ml_fkJoints[-1]
                
            mTopDriver.p_parent = mHeadBlendJoint
            if ml_segBlendTargets:
                ml_segBlendTargets[-1] = mTopDriver#...insert into here our new twist driver
            
            mHeadLookAt.doStore('drivenBlend', mHeadBlendJoint)
            mHeadLookAt.doStore('drivenAim', mHeadAimJoint)
            
            self.atUtils('get_switchTarget', mHeadLookAt, mHeadBlendJoint)
            
            mHeadLookAt.doStore('fkMatch', mTopDriver)
            mHeadLookAt.doStore('ikMatch', mHeadBlendJoint)
            mTopTwistDriver = mHeadBlendJoint
            if mBlock.scaleSetup:
                for mJnt in mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint:
                    mJnt.segmentScaleCompensate = False
            
            
            ATTR.connect(mPlug_aim.p_combinedShortName, "{0}.v".format(mHeadLookAt.mNode))
            
            #Setup Aim Main -------------------------------------------------------------------------------------
            mc.aimConstraint(mHeadLookAt.mNode,
                             mHeadAimJoint.mNode,
                             maintainOffset = False, weight = 1,
                             aimVector = self.d_orientation['vectorUpNeg'],
                             upVector = self.d_orientation['vectorAim'],
                             worldUpVector = self.d_orientation['vectorUp'],
                             worldUpObject = mHeadLookAt.mNode,#mHeadIK.mNode,#mHeadIK.masterGroup.mNode
                             worldUpType = 'objectRotation' )
            
            #Setup Aim back on head -------------------------------------------------------------------------------------
            _str_orientation = self.d_orientation['str']
            mc.aimConstraint(mHeadStuffParent.mNode,
                             mHeadLookAt.mNode,
                             maintainOffset = False, weight = 1,
                             aimVector = self.d_orientation['vectorAimNeg'],
                             upVector = self.d_orientation['vectorUp'],
                             worldUpVector = self.d_orientation['vectorAim'],
                             skip = _str_orientation[0],
                             worldUpObject = mHeadStuffParent.mNode,#mHeadIK.masterGroup.mNode,#mHeadIK.mNode,#mHeadIK.masterGroup.mNode
                             worldUpType = 'objectRotation' )
            
            ATTR.set_alias(mHeadLookAt.mNode,'r{0}'.format(_str_orientation[0]),'tilt')
            mHeadLookAt.setAttrFlags(attrs=['r{0}'.format(v) for v in _str_orientation[1:]])
            
            #Setup blend ----------------------------------------------------------------------------------
            RIGCONSTRAINT.blendChainsBy(mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint,
                                        driver = mPlug_aim.p_combinedName,l_constraints=['orient'])
            
            #Parent pass ---------------------------------------------------------------------------------
            mHeadLookAt.masterGroup.parent = mHeadStuffParent#mHeadIK.masterGroup
            #mSettings.masterGroup.parent = mHeadIK
            
            for mObj in mHeadFKJoint,mHeadAimJoint,mHeadBlendJoint:
                mObj.p_parent = mHeadStuffParent
            
            #mHeadIK.parent = mHeadBlendJoint.mNode
            """
            mHeadFK_aimFollowGroup = mHeadFK.doGroup(True,True,True,'aimFollow')
            mc.orientConstraint(mHeadBlendJoint.mNode,
                                mHeadFK_aimFollowGroup.mNode,
                                maintainOffset = False)"""
            
            #Trace crv ---------------------------------------------------------------------------------
            log.debug("|{0}| >> head look at track Crv".format(_str_func))
            trackcrv,clusters = CORERIG.create_at([mHeadLookAt.mNode,
                                                   mHeadAimJoint.mNode],#ml_handleJoints[1]],
                                                  'linearTrack',
                                                  baseName = '{0}_headAimTrack'.format(self.d_module['partName']))
        
            mTrackCrv = cgmMeta.asMeta(trackcrv)
            mTrackCrv.p_parent = self.mModule
            mHandleFactory = mBlock.asHandleFactory()
            mHandleFactory.color(mTrackCrv.mNode, controlType = 'sub')
        
            for s in mTrackCrv.getShapes(asMeta=True):
                s.overrideEnabled = 1
                s.overrideDisplayType = 2
            mTrackCrv.doConnectIn('visibility',mPlug_aim.p_combinedShortName)
            
            #Parent the direct control to the 
            if ml_rigJoints[-1].getMessage('masterGroup'):
                ml_rigJoints[-1].masterGroup.parent = mTopHandleDriver
            else:
                ml_rigJoints[-1].parent = mTopHandleDriver        
        else:
            log.debug("|{0}| >> NO Head IK setup...".format(_str_func))    
            #Parent the direct control to the 
            if ml_blendJoints:
                mTopHandleDriver = ml_blendJoints[-1]
                
            if ml_rigJoints[-1].getMessage('masterGroup'):
                ml_rigJoints[-1].masterGroup.parent = mTopHandleDriver
            else:
                ml_rigJoints[-1].parent = mTopHandleDriver    
    
            
        #>> Neck build ======================================================================================
        if mBlock.neckBuild:
            log.debug("|{0}| >> Neck...".format(_str_func))
            
            mHeadFK.masterGroup.p_parent = ml_fkJoints[-2]
            
            if not mRigNull.getMessage('rigRoot'):
                raise ValueError,"No rigRoot found"
            
            mRoot = mRigNull.rigRoot
            mSettings = mRigNull.settings
            
            if self.mBlock.neckIK:
                log.debug("|{0}| >> Neck IK...".format(_str_func))
                ml_ikJoints = mRigNull.msgList_get('ikJoints')
                ml_blendJoints = mRigNull.msgList_get('blendJoints')
                ml_handleParents = ml_fkJoints
                if ml_blendJoints:
                    log.debug("|{0}| >> Handles parent: blend".format(_str_func))
                    ml_handleParents = ml_blendJoints            
                
                mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',attrType='float',lock=False,keyable=True)
                
                #>>> Setup a vis blend result
                mPlug_FKon = cgmMeta.cgmAttr(mSettings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
                mPlug_IKon = cgmMeta.cgmAttr(mSettings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            
                NODEFACTORY.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,
                                                     mPlug_IKon.p_combinedName,
                                                     mPlug_FKon.p_combinedName)
                  
                mPlug_FKon.doConnectOut("{0}.visibility".format(ml_fkJoints[0].masterGroup.mNode))
                
                log.debug("|{0}| >> Neck IK | IK group...".format(_str_func))
                
                mIKGroup = mRoot.doCreateAt()
                mIKGroup.doStore('cgmTypeModifier','ik')
                mIKGroup.doName()
        
                mPlug_IKon.doConnectOut("{0}.visibility".format(mIKGroup.mNode))
                mIKGroup.parent = mRoot
                #mIKControl.masterGroup.parent = mIKGroup            
                mIKGroup.dagLock(True)
                mHeadIK.masterGroup.p_parent = mIKGroup
                
                """
                # Create head position driver ------------------------------------------------
                mHeadDriver = mHeadIK.doCreateAt()
                mHeadDriver.rename('headBlendDriver')
                mHeadDriver.parent = mRoot
                
                mHeadIKDriver = mHeadIK.doCreateAt()
                mHeadIKDriver.rename('headIKDriver')
                mHeadIKDriver.parent = mRoot
                
                mHeadFKDriver = mHeadIK.doCreateAt()
                mHeadFKDriver.rename('headFKDriver')
                mHeadFKDriver.parent = ml_fkJoints[-1]
                
                mHeadIK.connectChildNode(mHeadDriver.mNode, 'blendDriver')
                
                RIGCONSTRAINT.blendChainsBy(mHeadFKDriver.mNode,
                                            mHeadIKDriver.mNode,
                                            mHeadDriver.mNode,
                                            driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])            
                
                """
                
                mIKBaseControl = mRigNull.controlIKBase
                mIKBaseControl.masterGroup.p_parent = mIKGroup
                
                # Neck controls --------------------------------------------------------------
                if mBlock.neckControls == 1:
                    log.debug("|{0}| >> Neck IK | Single Control...".format(_str_func))
                    mc.pointConstraint(mHeadIK.mNode,
                                       ml_ikJoints[-1].mNode,
                                       maintainOffset = True)
                    
                    
                    mc.orientConstraint(mHeadIK.mNode,ml_ikJoints[-1].mNode, maintainOffset = True)
                    
                    #ml_ikJoints[0].parent = mIKGroup            
                    if mIKBaseControl:
                        mc.pointConstraint(mIKBaseControl.mNode,ml_ikJoints[0].mNode,maintainOffset=False)
                        mc.orientConstraint(mIKBaseControl.mNode,ml_ikJoints[0].mNode,maintainOffset=False)
                        
                        mNeckAim = mIKBaseControl.doCreateAt()
                        mNeckAim.parent = mIKGroup            
                        mNeckAim.doStore('cgmName','neckAim')                        
                        mNeckAim.doStore('cgmTypeModifier','back')
                        mNeckAim.doStore('cgmType','aimer')
                        mNeckAim.doStore('cgmAlias','neckAim')
                        
                        mNeckAim.doName()
                        
                        mIKBaseControl.connectChildNode(mNeckAim,'aimDriver','source')#Connect
                        
                        mc.aimConstraint(mHeadIK.mNode,
                                         mNeckAim.mNode,
                                         maintainOffset = True, weight = 1,
                                         aimVector = self.d_orientation['vectorAim'],
                                         upVector = self.d_orientation['vectorUp'],
                                         worldUpVector = self.d_orientation['vectorOut'],
                                         worldUpObject = mRoot.mNode,
                                         worldUpType = 'objectRotation' )
                        
                        
                    else:
                        mc.aimConstraint(mHeadIK.mNode,
                                         ml_ikJoints[0].mNode,
                                         maintainOffset = True, weight = 1,
                                         aimVector = self.d_orientation['vectorAim'],
                                         upVector = self.d_orientation['vectorUp'],
                                         worldUpVector = self.d_orientation['vectorOut'],
                                         worldUpObject = mIKBaseControl.mNode,
                                         worldUpType = 'objectRotation' )
                        
                        
                        
                    if mBlock.neckJoints < 2:
                        ml_rigJoints[0].masterGroup.p_parent = ml_handleParents[0]
                        
                    if mSegMidIK:
                        log.debug("|{0}| >> seg mid IK control found | single neck control".format(_str_func))
                        mSegMidIK.masterGroup.parent = mRoot
                        #mc.pointConstraint([mObj.mNode for mObj in ml_handleJoints], mSegMidIK.masterGroup.mNode,maintainOffset = True )
                        
                        
                        ml_midTrackJoints = copy.copy(ml_handleJoints)
                        ml_midTrackJoints.insert(1,mSegMidIK)
        
                        d_mid = {'jointList':[mJnt.mNode for mJnt in ml_midTrackJoints],
                                 'ribbonJoints':[mObj.mNode for mObj in ml_rigJoints],
                                 'baseName' :self.d_module['partName'] + '_midRibbon',
                                 'driverSetup':None,
                                 'squashStretch':None,
                                 'msgDriver':'masterGroup',
                                 'specialMode':'noStartEnd',
                                 'paramaterization':'floating',
                                 'connectBy':'constraint',
                                 'influences':ml_handleJoints,
                                 'moduleInstance' : mModule}
                        #reload(IK)
                        l_midSurfReturn = IK.ribbon(**d_mid)
                    
                if ml_handleJoints:                    
                    log.debug("|{0}| >> Neck IK | handleJoints...".format(_str_func))
                    for i,mHandle in enumerate(ml_handleJoints):
                        log.debug("|{0}| >> Neck IK | mHandle {1} | {2}".format(_str_func, i, mHandle))                    
                        mHandle.masterGroup.parent = ml_handleParents[i]
                        s_rootTarget = False
                        s_targetForward = False
                        s_targetBack = False
                        mMasterGroup = mHandle.masterGroup
                        b_first = False
                        b_last = False
                        if mHandle == ml_handleJoints[0]:
                            log.debug("|{0}| >> First handle: {1}".format(_str_func,mHandle))
                            if len(ml_handleJoints) <=2:
                                s_targetForward = ml_handleParents[-1].mNode
                            else:
                                s_targetForward = ml_handleJoints[i+1].getMessage('masterGroup')[0]
                                
                            s_rootTarget = mRoot.mNode
                            b_first = True
                
                        elif mHandle == ml_handleJoints[-1]:
                            log.debug("|{0}| >> Last handle: {1}".format(_str_func,mHandle))
                            s_rootTarget = ml_handleParents[i].mNode                
                            s_targetBack = ml_handleJoints[i-1].getMessage('masterGroup')[0]
                            b_last = True
                        else:
                            log.debug("|{0}| >> Reg handle: {1}".format(_str_func,mHandle))            
                            s_targetForward = ml_handleJoints[i+1].getMessage('masterGroup')[0]
                            s_targetBack = ml_handleJoints[i-1].getMessage('masterGroup')[0]
                

                        
                        if b_last and mBlock.headAim:
                            if s_targetBack:
                                mAimBack = mHandle.doCreateAt()
                                mAimBack.parent = mMasterGroup            
                                mAimBack.doStore('cgmTypeModifier','back')
                                mAimBack.doStore('cgmType','aimer')
                                mAimBack.doName()
                    
                                _const=mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                                        aimVector = [0,0,-1], upVector = [1,0,0],
                                                        worldUpObject = mTopTwistDriver.mNode,
                                                        worldUpType = 'objectRotation', worldUpVector = [1,0,0])            
                                s_targetBack = mAimBack.mNode
                    
                            s_targetForward = mTopTwistDriver.mNode
                    


                        else:


                            #Decompose matrix for parent...
                            mUpDecomp = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
                            mUpDecomp.doStore('cgmName',ml_handleParents[i])                
                            mUpDecomp.addAttr('cgmType','aimMatrix',attrType='string',lock=True)
                            mUpDecomp.doName()
                            
                            
                            ATTR.connect("%s.worldMatrix"%(ml_handleParents[i].mNode),"%s.%s"%(mUpDecomp.mNode,'inputMatrix'))                            
                
                            if s_targetForward:
                                mAimForward = mHandle.doCreateAt()
                                mAimForward.parent = mMasterGroup            
                                mAimForward.doStore('cgmTypeModifier','forward')
                                mAimForward.doStore('cgmType','aimer')
                                mAimForward.doName()
                    
                                _const=mc.aimConstraint(s_targetForward, mAimForward.mNode, maintainOffset = True, #skip = 'z',
                                                        aimVector = [0,0,1], upVector = [1,0,0], worldUpObject = ml_handleParents[i].mNode,
                                                        worldUpType = 'vector', worldUpVector = [0,0,0])            
                                s_targetForward = mAimForward.mNode
                                ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                 
                    
                            else:
                                s_targetForward = ml_handleParents[i].mNode
                    
                            if s_targetBack:
                                mAimBack = mHandle.doCreateAt()
                                mAimBack.parent = mMasterGroup                        
                                mAimBack.doStore('cgmTypeModifier','back')
                                mAimBack.doStore('cgmType','aimer')
                                mAimBack.doName()
                    
                                _const = mc.aimConstraint(s_targetBack, mAimBack.mNode, maintainOffset = True, #skip = 'z',
                                                          aimVector = [0,0,-1], upVector = [1,0,0], worldUpObject = ml_handleParents[i].mNode,
                                                          worldUpType = 'vector', worldUpVector = [0,0,0])  
                                s_targetBack = mAimBack.mNode
                                ATTR.connect("%s.%s"%(mUpDecomp.mNode,"outputRotate"),"%s.%s"%(_const[0],"upVector"))                                     
                            else:
                                s_targetBack = s_rootTarget
                                #ml_handleParents[i].mNode
                
                        #pprint.pprint([s_targetForward,s_targetBack])
                        mAimGroup = mHandle.doGroup(True,asMeta=True,typeModifier = 'aim')
                
                        mHandle.parent = False
                
                        if b_first:
                            const = mc.orientConstraint([s_targetBack, s_targetForward], mAimGroup.mNode, maintainOffset = True)[0]
                        else:
                            const = mc.orientConstraint([s_targetForward, s_targetBack], mAimGroup.mNode, maintainOffset = True)[0]
                
                
                        d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mHandle.mNode,'followRoot'],
                                                                             [mHandle.mNode,'resultRootFollow'],
                                                                             [mHandle.mNode,'resultAimFollow'],
                                                                             keyable=True)
                        targetWeights = mc.orientConstraint(const,q=True, weightAliasList=True,maintainOffset=True)
                
                        #Connect                                  
                        d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                        d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                        d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                        d_blendReturn['d_result2']['mi_plug'].p_hidden = True
                
                        mHandle.parent = mAimGroup#...parent back                
                    
                    
                    #Defaults ---------------------------------------------------------------------
                    for mHandle in ml_handleJoints:
                        if mHandle in [ml_handleJoints[0],ml_handleJoints[-1]]:
                            mHandle.followRoot = 0
                            ATTR.set_default(mHandle.mNode,'followRoot',0)
                        else:
                            mHandle.followRoot = .5
                            ATTR.set_default(mHandle.mNode,'followRoot',.5)
                            
                if mBlock.neckControls > 1:
                    #Ribbon or Spline =============================================================
                    log.debug("|{0}| >> Neck IK | ikType: {1}".format(_str_func,_ikNeck))
                    
                    if not mRigNull.getMessage('rigRoot'):
                        raise ValueError,"No rigRoot found"
                    if not mRigNull.getMessage('controlIK'):
                        raise ValueError,"No controlIK found"            
                
                    mIKControl = mRigNull.controlIK
                    mSettings = mRigNull.settings
                    ml_ikJoints = mRigNull.msgList_get('ikJoints')
                    mPlug_FKIK = cgmMeta.cgmAttr(mSettings.mNode,'FKIK',
                                                 attrType='float',
                                                 lock=False,
                                                 keyable=True)
                    _jointOrientation = self.d_orientation['str']
                
                    mStart = ml_ikJoints[0]
                    mEnd = ml_ikJoints[-1]
                    _start = ml_ikJoints[0].mNode
                    _end = ml_ikJoints[-1].mNode
                    
                    
                    mIKBaseControl = False
                    if mRigNull.getMessage('controlIKBase'):
                        mIKBaseControl = mRigNull.controlIKBase
            
                        mIKBaseControl.masterGroup.parent = mIKGroup
                        
                        
                    if mIKBaseControl:
                        mBaseOrientGroup = cgmMeta.validateObjArg(mIKBaseControl.doGroup(True,False,asMeta=True,typeModifier = 'aim'),'cgmObject',setClass=True)
                        ATTR.set(mBaseOrientGroup.mNode, 'rotateOrder', _jointOrientation)
                    
                        mLocBase = mIKBaseControl.doCreateAt()
                        mLocAim = mIKBaseControl.doCreateAt()
                        
                    
                        mLocAim.doStore('cgmType','aimDriver')
                        mLocBase = mIKBaseControl.doCreateAt()
                        mLocBase.doStore('cgmType','baseDriver')
                        
                        
                        for mObj in mLocBase,mLocAim:
                            mObj.doStore('cgmName',mIKBaseControl.mNode)                        
                            mObj.doName()
                    
                        mLocAim.p_parent = mIKBaseControl.dynParentGroup
                
                        mAimTarget = mIKControl
                        """
                        _direction = self.d_module['direction'] or 'center'
                        if _direction.lower() == 'left':
                            v_aim = [0,0,1]
                        else:
                            v_aim = [0,0,-1]"""
                
                        mc.aimConstraint(mAimTarget.mNode, mLocAim.mNode, maintainOffset = True,
                                         aimVector = [0,0,1], upVector = [0,1,0], 
                                         worldUpObject = mIKBaseControl.dynParentGroup.mNode,
                                         worldUpType = 'objectrotation', 
                                         worldUpVector = self.v_twistUp)
                    
                    
                        mLocBase.p_parent = mIKBaseControl.dynParentGroup
                    
                    
                        const = mc.orientConstraint([mLocAim.mNode,mLocBase.mNode],
                                                    mBaseOrientGroup.mNode, maintainOffset = True)[0]
                    
                        d_blendReturn = NODEFACTORY.createSingleBlendNetwork([mIKBaseControl.mNode,
                                                                              'aim'],
                                                                             [mIKControl.mNode,'resRootFollow'],
                                                                             [mIKControl.mNode,'resFullFollow'],
                                                                             keyable=True)
                    
                        targetWeights = mc.orientConstraint(const,q=True,
                                                            weightAliasList=True,
                                                            maintainOffset=True)
                    
                        #Connect                                  
                        d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[0]))
                        d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (const,targetWeights[1]))
                        d_blendReturn['d_result1']['mi_plug'].p_hidden = True
                        d_blendReturn['d_result2']['mi_plug'].p_hidden = True                                            
                        ATTR.set_default(mIKBaseControl.mNode, 'aim', 1.0)
                        #mIKBaseControl.extendIK = 0.0
                        mIKBaseControl.p_parent = mBaseOrientGroup
            
                    else:#Spin Group#========================================================================
                        log.debug("|{0}| >> spin setup...".format(_str_func))
            
                        #Make a spin group
                        mSpinGroup = mStart.doGroup(False,False,asMeta=True)
                        mSpinGroup.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])	
                        mSpinGroup.addAttr('cgmName','{0}NoFlipSpin'.format(self.d_module['partName']))
                        mSpinGroup.doName()
            
                        mSpinGroup.parent = mRoot
            
                        mSpinGroup.doGroup(True,True,typeModifier='zero')
            
                        #Setup arg
                        mPlug_spin = cgmMeta.cgmAttr(mIKControl,'spin',attrType='float',keyable=True, defaultValue = 0, hidden = False)
                        mPlug_spin.doConnectOut("%s.r%s"%(mSpinGroup.mNode,_jointOrientation[0]))
            
                        mSpinGroup.dagLock(True)
            
                    if _ikNeck == 'rp':
                        log.debug("|{0}| >> rp setup...".format(_str_func,_ikNeck))
            
                        #Build the IK ---------------------------------------------------------------------
                        _d_ik= {'globalScaleAttr':mPlug_globalScale.p_combinedName,
                                'stretch':'translate',
                                'lockMid':False,
                                'rpHandle':True,
                                'nameSuffix':'noFlip',
                                'controlObject':mIKControl.mNode,
                                'moduleInstance':self.mModule.mNode}
            
                        d_ikReturn = IK.handle(_start,_end,**_d_ik)
            
                        #Get our no flip position-------------------------------------------------------------------------
                        log.debug("|{0}| >> no flip dat...".format(_str_func))
            
                        _side = mBlock.atUtils('get_side')
                        _dist_ik_noFlip = DIST.get_distance_between_points(mStart.p_position,
                                                                           mEnd.p_position)
                        if _side == 'left':#if right, rotate the pivots
                            pos_noFlipOffset = mStart.getPositionByAxisDistance(_jointOrientation[2]+'-',_dist_ik_noFlip)
                        else:
                            pos_noFlipOffset = mStart.getPositionByAxisDistance(_jointOrientation[2]+'+',_dist_ik_noFlip)
            
                        #No flip -------------------------------------------------------------------------
                        log.debug("|{0}| >> no flip setup...".format(_str_func))
            
                        mIKHandle = d_ikReturn['mHandle']
                        ml_distHandlesNF = d_ikReturn['ml_distHandles']
                        mRPHandleNF = d_ikReturn['mRPHandle']
            
                        #No Flip RP handle -------------------------------------------------------------------
                        mRPHandleNF.p_position = pos_noFlipOffset
            
                        mRPHandleNF.doCopyNameTagsFromObject(self.mModule.mNode, ignore = ['cgmName','cgmType'])
                        mRPHandleNF.addAttr('cgmName','{0}PoleVector'.format(self.d_module['partName']), attrType = 'string')
                        mRPHandleNF.addAttr('cgmTypeModifier','noFlip')
                        mRPHandleNF.doName()
            
                        if mIKBaseControl:
                            mRPHandleNF.parent = mIKBaseControl.mNode
                        else:
                            mRPHandleNF.parent = mSpinGroup.mNode
            
                        #>>>Parent IK handles -----------------------------------------------------------------
                        log.debug("|{0}| >> parent ik dat...".format(_str_func,_ikNeck))
            
                        mIKHandle.parent = mIKControl.mNode#handle to control	
                        for mObj in ml_distHandlesNF[:-1]:
                            mObj.parent = mRoot
                        ml_distHandlesNF[-1].parent = mIKControl.mNode#handle to control
            
                        #>>> Fix our ik_handle twist at the end of all of the parenting
                        IK.handle_fixTwist(mIKHandle,_jointOrientation[0])#Fix the twist
            
                        mc.parentConstraint([mIKControl.mNode], ml_ikJoints[-1].mNode, maintainOffset = True)
            
                        if mIKBaseControl:
                            ml_ikJoints[0].parent = mRigNull.controlIKBase
            
                        if mIKBaseControl:
                            mc.pointConstraint(mIKBaseControl.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
            
                    elif _ikNeck == 'spline':# ==============================================================
                        log.debug("|{0}| >> spline setup...".format(_str_func))
                        ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                        if not ml_ribbonIkHandles:
                            raise ValueError,"No ribbon IKDriversFound"
            
                        log.debug("|{0}| >> ribbon ik handles...".format(_str_func))
            
                        if mIKBaseControl:
                            ml_ribbonIkHandles[0].parent = mIKBaseControl
                        else:
                            ml_ribbonIkHandles[0].parent = mSpinGroup
            
                        ml_ribbonIkHandles[-1].parent = mIKControl
            
                        mc.aimConstraint(mIKControl.mNode,
                                         ml_ribbonIkHandles[0].mNode,
                                         maintainOffset = True, weight = 1,
                                         aimVector = self.d_orientation['vectorAim'],
                                         upVector = self.d_orientation['vectorUp'],
                                         worldUpVector = self.d_orientation['vectorOut'],
                                         worldUpObject = mSpinGroup.mNode,
                                         worldUpType = 'objectRotation' )
            
            
                        res_spline = IK.spline([mObj.mNode for mObj in ml_ikJoints],
                                               orientation = _jointOrientation,
                                               moduleInstance = self.mModule)
                        mSplineCurve = res_spline['mSplineCurve']
                        log.debug("|{0}| >> spline curve...".format(_str_func))
            
            
                        #...ribbon skinCluster ---------------------------------------------------------------------
                        log.debug("|{0}| >> ribbon skinCluster...".format(_str_func))                
                        mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_ribbonIkHandles],
                                                                              mSplineCurve.mNode,
                                                                              tsb=True,
                                                                              maximumInfluences = 2,
                                                                              normalizeWeights = 1,dropoffRate=2.5),
                                                              'cgmNode',
                                                              setClass=True)
            
                        mSkinCluster.doStore('cgmName', mSplineCurve)
                        mSkinCluster.doName()    
                        cgmGEN.func_snapShot(vars())
            
            
                    elif _ikNeck == 'ribbon':#==============================================================
                        log.debug("|{0}| >> ribbon setup...".format(_str_func))
                        ml_ribbonIkHandles = mRigNull.msgList_get('ribbonIKDrivers')
                        if not ml_ribbonIkHandles:
                            raise ValueError,"No ribbon IKDriversFound"
                        ml_skinDrivers = copy.copy(ml_ribbonIkHandles)
                        max_influences = 2
                        
                        #Aim our ribbon handle -----------------------------------------
                        if mIKBaseControl:
                            mEndRibbonTarget =  mIKBaseControl
                        else:
                            mEndRibbonTarget = mRoot
                            
                        mc.aimConstraint(mEndRibbonTarget.mNode,
                                         ml_ribbonIkHandles[-1].mNode,
                                         maintainOffset = True, weight = 1,
                                         aimVector = self.d_orientation['vectorAimNeg'],
                                         upVector = self.d_orientation['vectorUp'],
                                         worldUpVector = self.d_orientation['vectorOut'],
                                         worldUpObject = mIKControl.mNode,
                                         worldUpType = 'objectRotation' )
                        #....
            
    
                        mSegMidIK = mRigNull.getMessageAsMeta('controlSegMidIK')
                        
            
            
                        if mSegMidIK:
                            log.debug("|{0}| >> seg mid IK control found...".format(_str_func))
                            mSegMidIK.masterGroup.parent = mIKGroup
                            ml_skinDrivers.append(mSegMidIK)
                            max_influences+=1
            
                            ml_midTrackJoints = copy.copy(ml_ribbonIkHandles)
                            ml_midTrackJoints.insert(1,mSegMidIK)
            
                            d_mid = {'jointList':[mJnt.mNode for mJnt in ml_midTrackJoints],
                                     'ribbonJoints':[mObj.mNode for mObj in ml_rigJoints[self.int_segBaseIdx:]],
                                     'baseName' :self.d_module['partName'] + '_midRibbon',
                                     'driverSetup':None,
                                     'squashStretch':None,
                                     'msgDriver':'masterGroup',
                                     'specialMode':'noStartEnd',
                                     'paramaterization':'floating',
                                     'connectBy':'constraint',
                                     'influences':ml_ribbonIkHandles,
                                     'moduleInstance' : mModule}
                            #reload(IK)
                            l_midSurfReturn = IK.ribbon(**d_mid)
            
            
            
                        log.debug("|{0}| >> ribbon ik handles...".format(_str_func))
            
                        if mIKBaseControl:
                            ml_ribbonIkHandles[0].parent = mIKBaseControl
                        else:
                            ml_ribbonIkHandles[0].parent = mSpinGroup
                            mc.aimConstraint(mIKControl.mNode,
                                             ml_ribbonIkHandles[0].mNode,
                                             maintainOffset = True, weight = 1,
                                             aimVector = self.d_orientation['vectorAim'],
                                             upVector = self.d_orientation['vectorUp'],
                                             worldUpVector = self.d_orientation['vectorOut'],
                                             worldUpObject = mSpinGroup.mNode,
                                             worldUpType = 'objectRotation' )                    
                            
                        
                        ml_ribbonIkHandles[-1].parent = mIKControl
            
            
                        if not  mRigNull.msgList_get('segmentJoints') and ml_handleJoints:
                            ml_skinDrivers.extend(ml_handleJoints)
            
                        if not len(ml_skinDrivers):
                            raise ValueError,"No skin drivers for ribbon found!"
                        d_ik = {'jointList':[mObj.mNode for mObj in ml_ikJoints],
                                'baseName' : self.d_module['partName'] + '_ikRibbon',
                                'driverSetup':'stable',
                                'squashStretch':None,
                                'connectBy':'constraint',
                                'squashStretchMain':'arcLength',
                                'paramaterization':mBlock.getEnumValueString('ribbonParam'),
                                #masterScalePlug:mPlug_masterScale,
                                'settingsControl': mSettings.mNode,
                                'extraSquashControl':True,
                                'influences':ml_skinDrivers,
                                'moduleInstance' : self.mModule}
            
                        #if str_ikBase == 'hips':
                            #d_ik['attachEndsToInfluences'] = True
            
                        #if mBlock.neckControls == mBlock.numJoints:
                            #d_ik['paramaterization'] = 'fixed'
            
            
                        d_ik.update(self.d_squashStretchIK)
                        res_ribbon = IK.ribbon(**d_ik)
            
                        const = ml_ikJoints[-1].getConstraintsTo(asMeta=True)
                        for mConst in const:
                            mConst.delete()
                        mc.parentConstraint([mIKControl.mNode], ml_ikJoints[-1].mNode, maintainOffset = True)
            
                        """
                            #...ribbon skinCluster ---------------------------------------------------------------------
                            log.debug("|{0}| >> ribbon skinCluster...".format(_str_func))
            
            
            
                            mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mHandle.mNode for mHandle in ml_skinDrivers],
                                                                                  mSurf.mNode,
                                                                                  tsb=True,
                                                                                  maximumInfluences = max_influences,
                                                                                  normalizeWeights = 1,dropoffRate=10),
                                                                  'cgmNode',
                                                                  setClass=True)
            
                            mSkinCluster.doStore('cgmName', mSurf)
                            mSkinCluster.doName()    
            
                            #Tighten the weights...
                            #reload(CORESKIN)
                            CORESKIN.surface_tightenEnds(mSurf.mNode, ml_ribbonIkHandles[0].mNode,
                                                         ml_ribbonIkHandles[-1].mNode, blendLength=5)"""
            
                    else:
                        raise ValueError,"Not implemented {0} ik setup".format(_ikNeck)                    
                    
    
    
    
                
                
                #Parent --------------------------------------------------            
                ml_blendJoints[0].parent = mRoot
                ml_ikJoints[0].parent = mRigNull.controlIKBase
                
                    
                    
                #Setup blend ----------------------------------------------------------------------------------
                log.debug("|{0}| >> blend setup...".format(_str_func))                
                
                if self.b_scaleSetup:
                    log.debug("|{0}| >> scale blend chain setup...".format(_str_func))                
                    RIGCONSTRAINT.blendChainsBy(ml_fkJoints,ml_ikJoints,ml_blendJoints,
                                                driver = mPlug_FKIK.p_combinedName,
                                                l_constraints=['point','orient','scale'])
            
            
                    #Scale setup for ik joints                
                    ml_ikScaleTargets = [mHeadIK]
            
                    if mIKBaseControl:
                        mc.scaleConstraint(mIKBaseControl.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
                        ml_ikScaleTargets.append(mIKBaseControl)
                    else:
                        mc.scaleConstraint(mRoot.mNode, ml_ikJoints[0].mNode,maintainOffset=True)
                        ml_ikScaleTargets.append(mRoot)
            
                    mc.scaleConstraint(mHeadIK.mNode, ml_ikJoints[-1].mNode,maintainOffset=True)
            
                    _targets = [mHandle.mNode for mHandle in ml_ikScaleTargets]
            
                    #Scale setup for mid set IK
                    if mSegMidIK:
                        mMasterGroup = mSegMidIK.masterGroup
                        _vList = DIST.get_normalizedWeightsByDistance(mMasterGroup.mNode,_targets)
                        _scale = mc.scaleConstraint(_targets,mMasterGroup.mNode,maintainOffset = True)#Point contraint loc to the object
                        CONSTRAINT.set_weightsByDistance(_scale[0],_vList)                
                        ml_ikScaleTargets.append(mSegMidIK)
                        _targets = [mHandle.mNode for mHandle in ml_ikScaleTargets]
            
                    for mJnt in ml_ikJoints[1:-1]:
                        _vList = DIST.get_normalizedWeightsByDistance(mJnt.mNode,_targets)
                        _scale = mc.scaleConstraint(_targets,mJnt.mNode,maintainOffset = True)#Point contraint loc to the object
                        CONSTRAINT.set_weightsByDistance(_scale[0],_vList)
            
                    for mJnt in ml_ikJoints[1:]:
                        mJnt.p_parent = mIKGroup
                        mJnt.segmentScaleCompensate = False
            
                    for mJnt in ml_blendJoints:
                        mJnt.segmentScaleCompensate = False
                        if mJnt == ml_blendJoints[0]:
                            continue
                        mJnt.p_parent = ml_blendJoints[0].p_parent
                        
                else:
                    RIGCONSTRAINT.blendChainsBy(ml_fkJoints,ml_ikJoints,ml_blendJoints,
                                                driver = mPlug_FKIK.p_combinedName,
                                                l_constraints=['point','orient'])                
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

    
def rig_cleanUp(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_cleanUp'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        mSettings = mRigNull.settings
        b_ikOrientToWorld = mBlock.ikOrientToWorld
        
        mRoot = mRigNull.getMessageAsMeta('rigRoot')
        if mRoot and not mRoot.hasAttr('cgmAlias'):
            mRoot.addAttr('cgmAlias','root')    
        
        mMasterControl= self.d_module['mMasterControl']
        mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
        mMasterNull = self.d_module['mMasterNull']
        mModuleParent = self.d_module['mModuleParent']
        mPlug_globalScale = self.d_module['mPlug_globalScale']
        ml_blendJoints = mRigNull.msgList_get('blendJoints')
        ml_fkJoints =  mRigNull.msgList_get('fkJoints')
        mAttachDriver = mRigNull.getMessageAsMeta('attachDriver')
        mAttachDriver.doStore('cgmAlias', '{0}_partDriver'.format(self.d_module['partName']))
        
        #if not self.mConstrainNull.hasAttr('cgmAlias'):
            #self.mConstrainNull.addAttr('cgmAlias','{0}_rootNull'.format(self.d_module['partName']))    
        
        #>>  Parent and constraining joints and rig parts =======================================================
        #if mSettings != mHeadIK:
            #mSettings.masterGroup.parent = mHeadIK
        
        #>>  DynParentGroups - Register parents for various controls ============================================
        ml_baseDynParents = []
        ml_endDynParents = self.ml_dynParentsAbove + self.ml_dynEndParents# + [mRoot]
        ml_ikDynParents = []    
        """
        #...head -----------------------------------------------------------------------------------
        ml_baseHeadDynParents = []
        
        #ml_headDynParents = [ml_controlsFK[0]]
        if mModuleParent:
            mi_parentRigNull = mModuleParent.rigNull
            if mi_parentRigNull.getMessage('controlIK'):
                ml_baseHeadDynParents.append( mi_parentRigNull.controlIK )	    
            if mi_parentRigNull.getMessage('controlIKBase'):
                ml_baseHeadDynParents.append( mi_parentRigNull.controlIKBase )
            if mi_parentRigNull.getMessage('rigRoot'):
                ml_baseHeadDynParents.append( mi_parentRigNull.rigRoot )
            ml_parentRigJoints =  mi_parentRigNull.msgList_get('rigJoints')
            if ml_parentRigJoints:
                ml_used = []
                for mJnt in ml_parentRigJoints:
                    if mJnt in ml_used:continue
                    if mJnt in [ml_parentRigJoints[0],ml_parentRigJoints[-1]]:
                        ml_baseHeadDynParents.append( mJnt.masterGroup)
                        ml_used.append(mJnt)
                        
        ml_baseHeadDynParents.append(mMasterNull.puppetSpaceObjectsGroup)"""
        
        #...Root controls ================================================================================
        ml_targetDynParents = []
        if mRoot:
            log.debug("|{0}| >>  Root: {1}".format(_str_func,mRoot))                
            #mParent = mRoot.getParent(asMeta=True)
            ml_targetDynParents = [self.md_dynTargetsParent['attachDriver']]
        
            if not mRoot.hasAttr('cgmAlias'):
                mRoot.addAttr('cgmAlias','{0}_root'.format(self.d_module['partName']))
        
            #if not mParent.hasAttr('cgmAlias'):
            #    mParent.addAttr('cgmAlias',self.d_module['partName'] + 'base')
            #ml_targetDynParents.append(mParent)    
            
            ml_targetDynParents.extend(ml_endDynParents)
        
            mDynGroup = mRoot.dynParentGroup
            #mDynGroup.dynMode = 2
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            #mDynGroup.dynFollow.p_parent = self.mDeformNull   
            
        """
        #...fk head ==================================================================================
        mHeadFK = mRigNull.getMessageAsMeta('headFK')
        if mHeadFK:
            log.debug("|{0}| >>  FK Head ... ".format(_str_func))                


            ml_targetDynParents = ml_baseDynParents + [self.md_dynTargetsParent['attachDriver']] + ml_endDynParents
            
            ml_targetDynParents.append(self.md_dynTargetsParent['world'])
            ml_targetDynParents.extend(mHeadFK.msgList_get('spacePivots',asMeta = True))
            
            mAim = mHeadFK.getMessageAsMeta('aimDriver')
            if mAim:
                ml_targetDynParents.insert(0,mAim)
                
            if ml_blendJoints:
                ml_targetDynParents.insert(0,ml_blendJoints[-1])
            else:
                ml_targetDynParents.insert(0,ml_fkJoints[-1])
                
            
            mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mHeadFK,dynMode=2)
            #mDynGroup.dynMode = 2
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            mDynGroup.dynFollow.p_parent = self.mDeformNull"""
            
        #...ik controls ==================================================================================
        log.debug("|{0}| >>  IK Handles ... ".format(_str_func))                
        
        ml_ikControls = []
        mControlIK = mRigNull.getMessage('controlIK')
        
        if mControlIK:
            ml_ikControls.append(mRigNull.controlIK)
            
        mControlIKBase = mRigNull.getMessageAsMeta('controlIKBase')
        if mControlIKBase:
            ml_ikControls.append(mRigNull.controlIKBase)
            
        for mHandle in ml_ikControls:
            log.debug("|{0}| >>  IK Handle: {1}".format(_str_func,mHandle))
            if b_ikOrientToWorld and mHandle != mControlIKBase:BUILDERUTILS.control_convertToWorldIK(mHandle)
            
            ml_targetDynParents = ml_baseDynParents + [self.md_dynTargetsParent['attachDriver']] + ml_endDynParents
            
            ml_targetDynParents.append(self.md_dynTargetsParent['world'])
            ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
            
            if mHandle == mControlIKBase:
                mAim = mHandle.getMessageAsMeta('aimDriver')
                if mAim:
                    ml_targetDynParents.insert(0,mAim)
        
            mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mHandle,dynMode=2)
            #mDynGroup.dynMode = 2
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            mDynGroup.dynFollow.p_parent = self.mDeformNull
            
        if ml_targetDynParents:
            log.debug("|{0}| >>  IK targets...".format(_str_func))
            #pprint.pprint(ml_targetDynParents)        
        
            log.debug(cgmGEN._str_subLine)
                  
        
        if mRigNull.getMessage('controlIKMid'):
            log.debug("|{0}| >>  IK Mid Handle ... ".format(_str_func))                
            mHandle = mRigNull.controlIKMid
            
            if b_ikOrientToWorld:BUILDERUTILS.control_convertToWorldIK(mHandle)
            
            mParent = mHandle.masterGroup.getParent(asMeta=True)
            ml_targetDynParents = []
        
            if not mParent.hasAttr('cgmAlias'):
                mParent.addAttr('cgmAlias','midIKBase')
            
            mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
            if mPivotResultDriver:
                mPivotResultDriver = mPivotResultDriver[0]
            ml_targetDynParents = [mPivotResultDriver,mControlIK,mParent]
            
            ml_targetDynParents.extend(ml_baseDynParents + ml_endDynParents)
            #ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
        
            mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mHandle,dynMode=0)
            #mDynGroup.dynMode = 2
        
            for mTar in ml_targetDynParents:
                mDynGroup.addDynParent(mTar)
            mDynGroup.rebuild()
            #mDynGroup.dynFollow.p_parent = self.mConstrainNull
            
            log.debug("|{0}| >>  IK Mid targets...".format(_str_func,mRoot))
            #pprint.pprint(ml_targetDynParents)                
            log.debug(cgmGEN._str_subLine)        
        
        
        """
        #Head -------------------------------------------------------------------------------------------
        ml_headDynParents = []
      
        ml_headDynParents.extend(mHeadIK.msgList_get('spacePivots',asMeta = True))
        ml_headDynParents.extend(ml_endDynParents)
        
        mBlendDriver =  mHeadIK.getMessage('blendDriver',asMeta=True)
        if mBlendDriver:
            mBlendDriver = mBlendDriver[0]
            ml_headDynParents.insert(0, mBlendDriver)  
            mBlendDriver.addAttr('cgmAlias','neckDriver')
        #pprint.pprint(ml_headDynParents)
    
        #Add our parents
        mDynGroup = mHeadIK.dynParentGroup
        log.debug("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
        mDynGroup.dynMode = 2
    
        for o in ml_headDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
    
        mDynGroup.dynFollow.parent = mMasterDeformGroup
        """
        
        #...headLookat ---------------------------------------------------------------------------------------
        if mBlock.headAim:
            log.debug("|{0}| >> HeadAim setup...".format(_str_func))
            
            mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
            
            #mHeadFKJoint = mRigNull.getMessage('fkHeadJoint', asMeta=True)[0]
            #mHeadAimJoint = mRigNull.getMessage('aimHeadJoint', asMeta=True)[0]
            #mHeadBlendJoint = mRigNull.getMessage('blendHeadJoint', asMeta=True)[0]
            #mHeadFKDynParentGroup = mHeadIK.dynParentGroup
            
            mHeadLookAt = mRigNull.lookAt        
            mHeadLookAt.setAttrFlags(attrs='v')
            
            if b_ikOrientToWorld:BUILDERUTILS.control_convertToWorldIK(mHeadLookAt)
            
            #...dynParentGroup...
            ml_headLookAtDynParents = []
            ml_headLookAtDynParents.extend(mHeadLookAt.msgList_get('spacePivots',asMeta = True))
            ml_headLookAtDynParents.extend(ml_endDynParents)    
            
            if ml_blendJoints:
                ml_headLookAtDynParents.insert(0, ml_blendJoints[-1])
                if not ml_blendJoints[-1].hasAttr('cgmAlias'):
                    ml_blendJoints[-1].addAttr('cgmAlias','blendHead')        
            #mHeadIK.masterGroup.addAttr('cgmAlias','headRoot')
            #Add our parents...
            mDynGroup = mHeadLookAt.dynParentGroup
            log.debug("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
        
            for o in ml_headLookAtDynParents:
                mDynGroup.addDynParent(o)
            mDynGroup.rebuild()
            
        #...rigJoints =================================================================================
        
        if mBlock.spaceSwitch_direct:
            log.debug("|{0}| >>  Direct...".format(_str_func))                
            for i,mObj in enumerate(mRigNull.msgList_get('rigJoints')):
                log.debug("|{0}| >>  Direct: {1}".format(_str_func,mObj))                        
                ml_targetDynParents = copy.copy(ml_baseDynParents)
                ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta=True) or [])
        
                mParent = mObj.masterGroup.getParent(asMeta=True)
                if not mParent.hasAttr('cgmAlias'):
                    mParent.addAttr('cgmAlias','{0}_rig{1}_base'.format(mObj.cgmName,i))
                ml_targetDynParents.insert(0,mParent)
        
                ml_targetDynParents.extend(ml_endDynParents)
        
                mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mObj.mNode,dynMode=0)
                #mDynGroup.dynMode = 2
        
                for mTar in ml_targetDynParents:
                    mDynGroup.addDynParent(mTar)
        
                mDynGroup.rebuild()
        
                #mDynGroup.dynFollow.p_parent = mRoot
                
        #...fk controls ============================================================================================
        log.debug("|{0}| >>  FK...".format(_str_func)+'-'*80)                
        ml_fkJoints = self.mRigNull.msgList_get('fkJoints')
        if ml_fkJoints:
            for i,mObj in enumerate([ml_fkJoints[0],ml_fkJoints[-1]]):
                if not mObj.getMessage('masterGroup'):
                    log.debug("|{0}| >>  Lacks masterGroup: {1}".format(_str_func,mObj))            
                    continue
                log.debug("|{0}| >>  FK: {1}".format(_str_func,mObj))
                ml_targetDynParents = copy.copy(ml_baseDynParents)
                ml_targetDynParents.append(self.md_dynTargetsParent['attachDriver'])
                
                mParent = mObj.masterGroup.getParent(asMeta=True)
                if mParent and mParent.hasAttr('cgmAlias'):
                    mParent.addAttr('cgmAlias','{0}_base'.format(mObj.p_nameBase))
                _mode = 2
                if i == 0:
                    ml_targetDynParents.append(mParent)
                    #_mode = 2            
                else:
                    ml_targetDynParents.insert(0,mParent)
                    #_mode = 1
                
                ml_targetDynParents.extend(ml_endDynParents)
                ml_targetDynParents.extend(mObj.msgList_get('spacePivots',asMeta = True))
            
                mDynGroup = cgmRIGMETA.cgmDynParentGroup(dynChild=mObj.mNode, dynMode=_mode)# dynParents=ml_targetDynParents)
                #mDynGroup.dynMode = 2
            
                for mTar in ml_targetDynParents:
                    mDynGroup.addDynParent(mTar)
                mDynGroup.rebuild()
        
                if _mode == 2:
                    mDynGroup.dynFollow.p_parent = mRoot    
                
                log.debug("|{0}| >>  FK targets: {1}...".format(_str_func,mObj))
                #pprint.pprint(ml_targetDynParents)                
                log.debug(cgmGEN._str_subLine)    
            
        #Settings =================================================================================
        log.debug("|{0}| >> Settings...".format(_str_func))
        mSettings.visRoot = 0
        mSettings.visDirect = 0
        
        ml_handleJoints = mRigNull.msgList_get('handleJoints')
        if ml_handleJoints:
            ATTR.set_default(ml_handleJoints[0].mNode, 'followRoot', .5)
            ml_handleJoints[0].followRoot = .5
            
            
        #Lock and hide =================================================================================
        ml_blendJoints = mRigNull.msgList_get('blendJoints',asMeta=True)
        for mJnt in ml_blendJoints:
            mJnt.dagLock(True)
            
        ml_controls = mRigNull.msgList_get('controlsAll')
        self.UTILS.controls_lockDown(ml_controls)
            
    
        
        if not mBlock.scaleSetup:
            log.debug("|{0}| >> No scale".format(_str_func))
            ml_controlsToLock = copy.copy(ml_controls)
            if self.b_squashSetup:
                ml_handles = self.mRigNull.msgList_get('handleJoints')
                for mHandle in ml_handles:
                    ml_controlsToLock.remove(mHandle)
                if self.__dict__.has_key('md_roll'):
                    for i in self.md_roll.keys():
                        mControlMid = mRigNull.getMessageAsMeta('controlSegMidIK_{0}'.format(i))
                        if mControlMid:
                            ml_controlsToLock.remove(mControlMid)
        
        
            for mCtrl in ml_controlsToLock:
                ATTR.set_standardFlags(mCtrl.mNode, ['scale'])
        else:
            log.debug("|{0}| >>  scale setup...".format(_str_func))
            
            
        self.mDeformNull.dagLock(True)
    
        
        #>>  Attribute defaults =================================================================================
        
        mRigNull.version = self.d_block['buildVersion']
        mBlock.blockState = 'rig'
        
        mBlock.template = True
        mBlock.noTransFormNull.template=True
        mBlock.UTILS.set_blockNullFormState(mBlock)
        self.UTILS.rigNodes_store(self)
    
    #>>  Parent and constraining joints and rig parts =======================================================

    #>>  DynParentGroups - Register parents for various controls ============================================
    #>>  Lock and hide ======================================================================================
    #>>  Attribute defaults =================================================================================
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        
    
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
        log.debug("|{0}| >> Missing...".format(_str_func))  
        for l in _l_missing:
            log.debug("|{0}| >> {1}".format(_str_func,l))  
        return False
    return True"""

def create_simpleMesh(self, deleteHistory = True, cap=True, skin = False, parent=False):
    try:
        _str_func = 'create_simpleMesh'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        #pprint.pprint(vars())
        if skin:
            mModuleTarget = self.getMessage('moduleTarget',asMeta=True)
            if not mModuleTarget:
                return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
            mModuleTarget = mModuleTarget[0]
            ml_moduleJoints = mModuleTarget.rigNull.msgList_get('moduleJoints')
            if not ml_moduleJoints:
                return log.error("|{0}| >> Must have moduleJoints for skining mode".format(_str_func))        
        
        #>> Head ===================================================================================
        log.debug("|{0}| >> Head...".format(_str_func))
        
        mGroup = self.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
        l_headGeo = mGroup.getChildren(asMeta=False)
        ml_headStuff = []
        for i,o in enumerate(l_headGeo):
            log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
            if ATTR.get(o,'v'):
                log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
                mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
                ml_headStuff.append(  mObj )
                mObj.p_parent = False
                if parent:
                    mObj.p_parent = parent
                    #if skin:mObj.doCopyPivot(parent)
                if skin:
                    mc.skinCluster ([ ml_moduleJoints[-1].mNode],
                                    mObj.mNode,
                                    tsb=True,
                                    bm=1,
                                    maximumInfluences = 3,
                                    normalizeWeights = 1, dropoffRate=10)
    
        if self.neckBuild:#...Neck =====================================================================
            log.debug("|{0}| >> neckBuild...".format(_str_func))    
            ml_neckMesh = self.UTILS.create_simpleLoftMesh(self,None,None,
                                                           deleteHistory=deleteHistory,
                                                           cap=cap,
                                                           flipUV=True, #WHY??!!!!
                                                           loftMode='evenCubic')
            
            
            ml_headStuff.extend(ml_neckMesh)
            if parent:
                for mObj in ml_neckMesh:
                    mObj.p_parent = parent
                    #if skin:mObj.doCopyPivot(parent)
            
            if skin:
                for mMesh in ml_neckMesh:
                    MRSPOST.skin_mesh(mMesh,ml_moduleJoints)
                    """
                    mc.skinCluster ([mJnt.mNode for mJnt in ml_moduleJoints],
                                    mMesh.mNode,
                                    tsb=True,
                                    bm=1,
                                    maximumInfluences = 3,
                                    normalizeWeights = 1, dropoffRate=2)"""
        if skin:
            _res = mc.polyUniteSkinned([mObj.mNode for mObj in ml_headStuff],ch=False,objectPivot=True)
            _mesh = mc.rename(_res[0],'{0}_0_geo'.format(self.p_nameBase))
            mc.rename(_res[1],'{0}_skinCluster'.format(_mesh))
            mMesh = cgmMeta.asMeta(_mesh)
            if parent:
                mMesh.dagLock(False)
                mMesh.p_parent = parent
            
        elif deleteHistory != False:
            _mesh = mc.polyUnite([mObj.mNode for mObj in ml_headStuff],ch=False)
            _mesh = mc.rename(_mesh,'{0}_0_geo'.format(self.p_nameBase))
            CORERIG.color_mesh(_mesh,'puppetmesh')        
        else:
            return
        
        for mObj in ml_headStuff:
            try:mObj.delete()
            except:pass
        
        return cgmMeta.validateObjListArg(_mesh)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

def asdfasdfasdf(self, forceNew = True, skin = False):
    """
    Build our proxyMesh
    """
    _short = self.d_block['shortName']
    _str_func = 'build_proxyMesh'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    log.debug("{0}".format(self))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHeadIK = mRigNull.headIK
    mSettings = mRigNull.settings
    mPuppetSettings = self.d_module['mMasterControl'].controlSettings
    
    ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
    if not ml_rigJoints:
        raise ValueError,"No rigJoints connected"

    #>> If proxyMesh there, delete --------------------------------------------------------------------------- 
    _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
        
    #>> Head ===================================================================================
    log.debug("|{0}| >> Head...".format(_str_func))
    if directProxy:
        log.debug("|{0}| >> directProxy... ".format(_str_func))
        _settings = self.mRigNull.settings.mNode
        
    
    mGroup = mBlock.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
    l_headGeo = mGroup.getChildren(asMeta=False)
    l_vis = mc.ls(l_headGeo, visible = True)
    ml_headStuff = []
    
    for i,o in enumerate(l_vis):
        log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))
        
        mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
        ml_headStuff.append(  mObj )
        mObj.parent = ml_rigJoints[-1]
        
        ATTR.copy_to(ml_rigJoints[-1].mNode,'cgmName',mObj.mNode,driven = 'target')
        mObj.addAttr('cgmIterator',i)
        mObj.addAttr('cgmType','proxyGeo')
        mObj.doName()
        
        if directProxy:
            CORERIG.shapeParent_in_place(ml_rigJoints[-1].mNode,mObj.mNode,True,False)
            CORERIG.colorControl(ml_rigJoints[-1].mNode,_side,'main',directProxy=True)        
        
    if mBlock.neckBuild:#...Neck =====================================================================
        log.debug("|{0}| >> neckBuild...".format(_str_func))


def build_proxyMesh(self, forceNew = True, puppetMeshMode = False):
    """
    Build our proxyMesh
    """
    try:
        _short = self.p_nameShort
        _str_func = '[{0}] > build_proxyMesh'.format(_short)
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
    
        _start = time.clock()
        mBlock = self
        mModule = self.moduleTarget
        mRigNull = mModule.rigNull
        mSettings = mRigNull.settings
        mPuppet = self.atUtils('get_puppet')
        mMaster = mPuppet.masterControl
        mPuppetSettings = mMaster.controlSettings
        str_partName = mModule.get_partNameBase()
        directProxy = mBlock.proxyDirect        
        
        directProxy = mBlock.proxyDirect
        
        _side = BLOCKUTILS.get_side(self)
        ml_neckProxy = []
        
        ml_rigJoints = mRigNull.msgList_get('rigJoints',asMeta = True)
        if not ml_rigJoints:
            raise ValueError,"No rigJoints connected"
        
        #>> If proxyMesh there, delete ---------------------------------------------------------------------- 
        if puppetMeshMode:
            _bfr = mRigNull.msgList_get('puppetProxyMesh',asMeta=True)
            if _bfr:
                log.debug("|{0}| >> puppetProxyMesh detected...".format(_str_func))            
                if forceNew:
                    log.debug("|{0}| >> force new...".format(_str_func))                            
                    mc.delete([mObj.mNode for mObj in _bfr])
                else:
                    return _bfr        
        else:
            _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
            if _bfr:
                log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
                if forceNew:
                    log.debug("|{0}| >> force new...".format(_str_func))                            
                    mc.delete([mObj.mNode for mObj in _bfr])
                else:
                    return _bfr
            
        #>> Head ===================================================================================
        log.debug("|{0}| >> Head...".format(_str_func))
        if directProxy:
            log.debug("|{0}| >> directProxy... ".format(_str_func))
            _settings = mRigNull.settings.mNode
            
        if directProxy:
            for mJnt in ml_rigJoints:
                for shape in mJnt.getShapes():
                    mc.delete(shape)
        
        mGroup = mBlock.msgList_get('headMeshProxy')[0].getParent(asMeta=True)
        
        l_headGeo = mGroup.getChildren(asMeta=False)
        #l_vis = mc.ls(l_headGeo, visible = True)
        ml_segProxy = []
        ml_headStuff = []
        _extendToStart = True
        _ballBase = False
        _ballMode = False
        if mBlock.proxyGeoRoot:
            _ballMode = mBlock.getEnumValueString('proxyGeoRoot')
            _ballBase=True        
        if puppetMeshMode:
            log.debug("|{0}| >> puppetMesh setup... ".format(_str_func))
            ml_moduleJoints = mRigNull.msgList_get('moduleJoints')
            
            if mBlock.neckBuild:
                if mBlock.neckJoints == 1:
                    mProxy = ml_moduleJoints[0].doCreateAt(setClass=True)
                    mPrerigProxy = mBlock.getMessage('prerigLoftMesh',asMeta=True)[0]
                    mPrerigProxyDup = mPrerigProxy.doDuplicate(po=False)
                    CORERIG.shapeParent_in_place(mProxy.mNode, mPrerigProxyDup.mNode,False,True)
                    ATTR.copy_to(ml_moduleJoints[0].mNode,'cgmName',mProxy.mNode,driven = 'target')
                    mProxy.addAttr('cgmType','proxyPuppetGeo')
                    mProxy.doName()
                    mProxy.parent = ml_moduleJoints[0]
                    ml_segProxy = [mProxy]
    
                    
                else:
                    # Create ---------------------------------------------------------------------------
                    _extendToStart = True
                    _ballBase = False
                    _ballMode = False
                    if mBlock.proxyGeoRoot:
                        _ballMode = mBlock.getEnumValueString('proxyGeoRoot')
                        _ballBase=True
    
                    ml_neckProxy = cgmMeta.validateObjListArg(BLOCKUTILS.mesh_proxyCreate(self,
                                                                                          ml_rigJoints,
                                                                                          ballBase = _ballBase,
                                                                                          ballMode = _ballMode,
                                                                                          extendToStart=_extendToStart),
                                                              'cgmObject')                
                    
                    
                    log.debug("|{0}| >> created: {1}".format(_str_func,ml_neckProxy))
                    
                    for i,mGeo in enumerate(ml_neckProxy):
                        mGeo.parent = ml_moduleJoints[i]
                        mGeo.doStore('cgmName',str_partName)
                        mGeo.addAttr('cgmIterator',i+1)
                        mGeo.addAttr('cgmType','proxyPuppetGeo')
                        mGeo.doName()
                        ml_segProxy.append(mGeo)
            
            for i,o in enumerate(l_headGeo):
                log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
                if ATTR.get(o,'v'):
                    log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
                    mGeo = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
                    mGeo.parent = ml_moduleJoints[-1]
                    mGeo.doStore('cgmName',str_partName)
                    mGeo.addAttr('cgmTypeModifier','end')
                    mGeo.addAttr('cgmType','proxyPuppetGeo')
                    mGeo.doName()
                    ml_segProxy.append( mGeo )
                    
            for mGeo in ml_segProxy:
                CORERIG.color_mesh(mGeo.mNode,'puppetmesh')
                
            mRigNull.msgList_connect('puppetProxyMesh', ml_segProxy)
            return ml_segProxy    
        
        
        
        
        for i,o in enumerate(l_headGeo):
            log.debug("|{0}| >> geo: {1}...".format(_str_func,o))                    
            if ATTR.get(o,'v'):
                log.debug("|{0}| >> visible head: {1}...".format(_str_func,o))            
                mObj = cgmMeta.validateObjArg(mc.duplicate(o, po=False, ic = False)[0])
                ml_headStuff.append(  mObj )
                mObj.p_parent = False
                mObj.parent = ml_rigJoints[-1]
                
                ATTR.copy_to(ml_rigJoints[-1].mNode,'cgmName',mObj.mNode,driven = 'target')
                mObj.addAttr('cgmIterator',i)
                mObj.addAttr('cgmType','proxyGeo')
                mObj.doName()
                
                if directProxy:
                    CORERIG.shapeParent_in_place(ml_rigJoints[-1].mNode,mObj.mNode,True,False)
                    CORERIG.colorControl(ml_rigJoints[-1].mNode,_side,'main',directProxy=True)        
            
        if mBlock.neckBuild:#...Neck =====================================================
            log.debug("|{0}| >> neckBuild...".format(_str_func))
            
            ml_neckProxy = cgmMeta.validateObjListArg(self.atUtils('mesh_proxyCreate', ml_rigJoints[:-1],
                                                                   ballBase = _ballBase,
                                                                   ballMode = _ballMode,
                                                                   extendToStart=_extendToStart),
                                                             'cgmObject')             
            log.debug("|{0}| >> created: {1}".format(_str_func,ml_neckProxy))
    
            for i,mGeo in enumerate(ml_neckProxy):
                mGeo.parent = ml_rigJoints[i]
                ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mGeo.mNode,driven = 'target')
                mGeo.addAttr('cgmIterator',i+1)
                mGeo.addAttr('cgmType','proxyGeo')
                mGeo.doName()
    
                if directProxy:
                    CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mGeo.mNode,True,False)
                    CORERIG.colorControl(ml_rigJoints[i].mNode,_side,'main',directProxy=True)        
            
            
            # Create ---------------------------------------------------------------------------
            if mBlock.neckJoints == 1:
                
                pass
                """
                mProxy = ml_rigJoints[0].doCreateAt(setClass=True)
                mPrerigProxy = mBlock.getMessage('prerigLoftMesh',asMeta=True)[0]
                CORERIG.shapeParent_in_place(mProxy.mNode, mPrerigProxy.mNode)
                
                ATTR.copy_to(ml_rigJoints[0].mNode,'cgmName',mProxy.mNode,driven = 'target')
                mProxy.addAttr('cgmType','proxyGeo')
                mProxy.doName()
                mProxy.parent = ml_rigJoints[0]
                ml_neckProxy = [mProxy]
                #mc.polyNormal(mProxy.mNode,setUserNormal = True)
                
                if directProxy:
                    CORERIG.shapeParent_in_place(ml_rigJoints[0].mNode,mProxy.mNode,True,False)
                    CORERIG.colorControl(ml_rigJoints[0].mNode,_side,'main',directProxy=True)            
                """
     
        
        for mProxy in ml_neckProxy + ml_headStuff:
            CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
            mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)
    
            #Vis connect -----------------------------------------------------------------------
            mProxy.overrideEnabled = 1
            ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(mProxy.mNode) )
            ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayType".format(mProxy.mNode) )
            for mShape in mProxy.getShapes(asMeta=1):
                str_shape = mShape.mNode
                mShape.overrideEnabled = 0
                #ATTR.connect("{0}.proxyVis".format(mPuppetSettings.mNode),"{0}.visibility".format(str_shape) )
                ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayTypes".format(str_shape) )
                
        if directProxy:
            for mObj in ml_rigJoints:
                for mShape in mObj.getShapes(asMeta=True):
                    #mShape.overrideEnabled = 0
                    mShape.overrideDisplayType = 0
                    ATTR.connect("{0}.visDirect".format(_settings), "{0}.overrideVisibility".format(mShape.mNode))
            
        mRigNull.msgList_connect('proxyMesh', ml_neckProxy + ml_headStuff)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
    

def controller_getDat(self):
    _str_func = 'controller_getDat'
    log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
    mRigNull = self.rigNull
    
    def checkList(l):
        ml = []
        for o in l:
            if mRigNull.getMessage(o):
                log.debug("|{0}| >>  Message found: {1} ".format(_str_func,o))                
                mObj = mRigNull.getMessage(o,asMeta=True)[0]
                if mObj not in ml:ml.append(mObj)
            elif mRigNull.msgList_exists(o):
                log.debug("|{0}| >>  msgList found: {1} ".format(_str_func,o))                
                _msgList = mRigNull.msgList_get(o)
                for mObj in _msgList:
                    if mObj not in ml:ml.append(mObj)
        return ml
    
    md = {}

    #Root...
    md['root'] =  checkList(['cog','rigRoot','limbRoot'])

    md['settings'] =  checkList(['mSettings','settings'])
    
    #Direct...
    md['direct'] = mRigNull.msgList_get('rigJoints')
    
    md['pivots'] = checkList(['pivot{0}'.format(n.capitalize()) for n in BLOCKSHARE._l_pivotOrder])
    
    #FK...
    md['fk'] = checkList(['leverFK','fkJoints','controlsFK','controlFK'])
    
    md['noHide'] = md['root'] + md['settings']
    
    #IK...
    md['ik'] = checkList(['leverFK',
                          'controlIKBase',
                          'controlIKMid','controlSegMidIK',
                          'controlBallRotation','leverIK',
                          'controlIKBall','controlIKBallHinge','controlIKToe',
                          'controlIKEnd','controlIK'])
    #seg...
    md['segmentHandles'] = mRigNull.msgList_get('handleJoints')
        
        
    return md




















