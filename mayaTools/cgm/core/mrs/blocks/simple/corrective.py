"""
------------------------------------------
cgm.core.mrs.blocks.simple.corrective
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__MAYALOCAL = 'CORRECTIVE'

# From Python =============================================================
import copy
import re
import time
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
#r9Meta.cleanCache()#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.cgm_General as cgmGEN

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import rigging_utils as CORERIG
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.math_utils as MATH

import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.rig.create_utils as RIGCREATE
import cgm.core.rig.constraint_utils as RIGCONSTRAINT
import cgm.core.mrs.lib.blockShapes_utils as BLOCKSHAPES
#reload(BLOCKSHAPES)
import cgm.core.lib.transform_utils as TRANS
import cgm.core.cgmPy.validateArgs as VALID
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.list_utils as LISTS
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.mrs.lib.ModuleControlFactory as MODULECONTROL
#reload(MODULECONTROL)
import cgm.core.mrs.lib.block_utils as BLOCKUTILS
import cgm.core.mrs.lib.builder_utils as BUILDERUTILS
import cgm.core.mrs.lib.rigShapes_utils as RIGSHAPES
from cgm.core.mrs.lib import general_utils as BLOCKGEN
from cgm.core.lib import nameTools as CORENAMES
import cgm.core.rig.correctives_utils as CORRECTIVES

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI
#reload(RIGSHAPES)


log_start = cgmGEN.logString_start
log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub

#=============================================================================================================
#>> Block Settings
#=============================================================================================================
__version__ = cgmGEN.__RELEASE
__autoForm__ = False
__component__ = True
__menuVisible__ = True
__baseSize__ = 1,1,1
__blockHelper__ = True

__l_rigBuildOrder__ = ['rig_dataBuffer',
                       'rig_skeleton',
                       'rig_shapes',
                       'rig_controls',
                       'rig_frame',
                       'rig_cleanUp']

#=============================================================================================================
#>> Profiles 
#=============================================================================================================

d_build_profiles = {'unityLow':{'default':{}},
                    'unityMed':{'default':{}},
                    'unityHigh':{'default':{}},
                    'feature':{'default':{}}}


d_attrStateMask = {'define':['readerDriver','readerParent',
                             'correctiveLayout','readerKey','readerType'],
                   'form':['loftList','basicShape','proxyShape','proxyType','shapersAim'],
                   'prerig':[],
                   'skeleton':['hasJoint'],
                   'proxySurface':['proxy'],
                   'rig':['rotPivotPlace','scaleSetup'],
                   'vis':[]}

d_block_profiles = {
    'hingeSimple':{
    'basicShape':'cube',
    'correctiveLayout':['upDown'],
    'readerKey':['posFwd'],
    'readerType':['alignMatrix'],
    'cgmName':'hinge'},}


#=============================================================================================================
#>> Attrs 
#=============================================================================================================
l_correctiveLayouts = BLOCKSHARE.l_correctiveLayouts#['upDown','outs','hipRight','hipLeft', 'shoulderRight','shoulderLeft']
l_readerPlugs = BLOCKSHARE.l_readerPlugs# ['posFwd','negFwd','posSide','negSide','posTwist','negTwist']
l_readerTypes = BLOCKSHARE.l_readerTypes# ['none','alignMatrix']

l_attrsStandard = ['side',
                   'position',
                   'hasJoint',
                   'basicShape',
                   'attachPoint',
                   'attachIndex',
                   'blockState_BUFFER',
                   'buildSDK',
                   'proxy',
                   'proxyType',
                   'blockProfile',
                   'visLabels',
                   'jointRadius',
                   'scaleSetup',                   
                   'visProximityMode',
                   'shapeDirection',
                   'meshBuild',                   
                   'moduleTarget']

d_attrsToMake = {'parentToDriver':'bool',
                 'correctiveLayout':"enumDatList",
                 'readerKey':'enumDatList',
                 'readerType':"enumDatList",
                 'readerKeyOverride':'string',
                 'readerDriver':'messageSimple',
                 'readerParent':'messageSimple',
                 'proxyShape':'cube:sphere:cylinder:cone:torus'}

d_defaultSettings = {'version':__version__,
                     'hasJoint':True,
                     'basicShape':0,
                     'shapeDirection':2,
                     'buildSDK':1,
                     'attachPoint':'closest',
                     'visLabels':True,
                     'jointRadius':.1,
                     'correctiveLayout':['upDown'],
                     'readerKey':['posFwd'],
                     'readerType':['alignMatrix'],                     
                     'meshBuild':False,
                     'proxyType':1}

#=============================================================================================================
#>> Wiring 
#=============================================================================================================
d_wiring_prerig = {'msgLinks':['moduleTarget','prerigNull']}
d_wiring_form = {}
    
    
_bak = {'msgLinks':['formNull'],
        #'msgLists':['formStuff'],
        'optional':['formStuff']}
d_wiring_define = {'msgLinks':['defineNull'],
                   'msgLists':['defineStuff'],
                   'optional':['defineStuff']}


#=============================================================================================================
#>> UI
#=============================================================================================================
   
def uiBuilderMenu(self,parent = None):
    #uiMenu = mc.menuItem( parent = parent, l='Head:', subMenu=True)
    _short = self.p_nameShort
    
    mUI.MelMenuItem(parent, ann = '[{0}] Set Driver'.format(_short),
                c = cgmGEN.Callback(driver_set,self),
                label = "Set Driver")
    mUI.MelMenuItem(parent, ann = '[{0}] Clear Driver'.format(_short),
                c = cgmGEN.Callback(driver_clear,self),
                label = "Clear Driver")
    
    mUI.MelMenuItem(parent, ann = '[{0}] Set Reader Parent'.format(_short),
                c = cgmGEN.Callback(readerParent_set,self),
                label = "Set Reader Parent")
    
    mUI.MelMenuItem(parent, en=True,divider = True,
                label = "Utilities")
    
    mLayout = mUI.MelMenuItem(parent, en=True,subMenu = True,tearOff=True,
                       label = "Add Layout:")
    for a in l_correctiveLayouts:
        mUI.MelMenuItem(mLayout, ann = '[{0}] Add layout: {1}'.format(_short,a),
                    c = cgmGEN.Callback(layout_add,self,a),
                    label = a)
    
    mReaders = mUI.MelMenuItem(parent, en=True,subMenu = True,tearOff=True,
                       label = "Add Reader:")
    for a in l_readerPlugs + ['custom']:
        mUI.MelMenuItem(mReaders, ann = '[{0}] Add Reader: {1}'.format(_short,a),
                    c = cgmGEN.Callback(reader_add,self,a),
                    label = a)        
        
    
    """
    mc.menuItem(en=False,divider=True,
                label = "Handle Geo")
    
    mc.menuItem(ann = '[{0}] Report proxy geo group'.format(_short),
                c = cgmGEN.Callback(proxyGeo_getGroup,self),
                label = "Report Group")
    mc.menuItem(ann = '[{0}] Add selected to proxy geo proxy group'.format(_short),
                c = cgmGEN.Callback(proxyGeo_add,self),
                label = "Add selected")
    mc.menuItem(ann = '[{0}] REPLACE existing geo with selected'.format(_short),
                c = cgmGEN.Callback(proxyGeo_replace,self),
                label = "Replace with selected")
    mc.menuItem(ann = '[{0}]Remove selected to proxy geo proxy group'.format(_short),
                c = cgmGEN.Callback(proxyGeo_remove,self),
                label = "Remove selected")        
    mc.menuItem(ann = '[{0}] Select Geo Group'.format(_short),
                c = cgmGEN.Callback(proxyGeo_getGroup,self,True),
                label = "Select Group")
    
    mc.menuItem(en=True,divider = True,
                label = "Utilities")
    _sub = mc.menuItem(en=True,subMenu = True,tearOff=True,
                       label = "State Picker")
    """
    
    #self.UTILS.uiBuilderMenu(self,parent)
    
    return

def readerParent_set(self,target = None):
    _str_func = 'readerParent_set'
    log.debug(log_start(_str_func))
    _sel = mc.ls(sl=1)
    if target == None and _sel:
        target = _sel[0]
    
    mTarget = cgmMeta.validateObjArg(target,noneValid=True)        
    self.readerParent = mTarget


def driver_set(self,target = None):
    _str_func = 'set_driver'
    log.debug(log_start(_str_func))
    _sel = mc.ls(sl=1)
    if target == None and _sel:
        target = _sel[0]
    
    ATTR.set_standardFlags(self.mNode, ['translate','rotate'],False,True,True)
    
    if not target:
        return log.warning(log_msg(_str_func,'No target offered'))
    
    mTargetParent = BLOCKGEN.block_getFromSelected()
    print mTargetParent
    mTarget = cgmMeta.validateObjArg(target,noneValid=True)        
    
    l_constraints = self.getConstraintsTo()
    if l_constraints:
        mc.delete(l_constraints)
        
    self.doSnapTo(mTarget)
    mc.parentConstraint(mTarget.mNode, self.mNode, maintainOffset = True)
    
    self.dagLock(True)
    
    self.readerDriver = mTarget
    
    if not self.p_blockParent and mTargetParent:
        self.p_blockParent = mTargetParent
        self.jointRadius = mTargetParent.jointRadius
        
    ATTR.set_standardFlags(self.mNode, ['sx','sz'])
    
    #Name... ---------------------------------------
    self.side = mTargetParent.side
    
    str_name = "{0}_{1}".format(CORENAMES.get_combinedNameDict(mTarget.mNode,
                                                               ignore = ['cgmType','cgmDirection']),self.blockProfile)
    self.doStore('cgmName',str_name)
    self.doName()

def driver_clear(self):
    l_constraints = self.getConstraintsTo()
    if l_constraints:
        mc.delete(l_constraints)
        
    self.dagLock(False)
    ATTR.set_standardFlags(self.mNode, ['sx','sz'])
    
def layout_add(self,lType = None):
    _str_func = 'layout_add'
    log.debug(log_start(_str_func))
    
    _short = self.p_nameShort
    
    i = ATTR.get_nextAvailableSequentialAttrIndex(_short,'correctiveLayout')
    str_attr = "correctiveLayout_{0}".format(i)
    self.addAttr(str_attr,initialValue = lType, attrType = 'enum', enumName= ":".join(l_correctiveLayouts), keyable = False)
    
def reader_add(self,rType = None):
    _str_func = 'reader_add'
    log.debug(log_start(_str_func))
    
    _short = self.p_nameShort
    
    i = ATTR.get_nextAvailableSequentialAttrIndex(_short,'readerKey')
    str_attr = "readerKey_{0}".format(i)
    
    if rType == 'custom':
        self.addAttr(str_attr,initialValue = 'changeMe', attrType = 'string', keyable=True)
    else:
        self.addAttr(str_attr,initialValue = rType, attrType = 'enum', enumName= ":".join(l_readerPlugs), keyable = False)
    
    self.addAttr(str_attr,initialValue = 1, attrType = 'enum', enumName= ":".join(l_readerTypes), keyable = False)    
    
    #print rType
    #print str_attr

#=============================================================================================================
#>> Define
#=============================================================================================================
def define(self):
    try:
        _str_func = 'define'
        _short = self.mNode
        
        for a in 'baseAim','baseSize','baseUp':
            if ATTR.has_attr(_short,a):
                ATTR.set_hidden(_short,a,True)    

        ATTR.set_alias(_short,'sy','blockScale')    
        self.setAttrFlags(attrs=['sx','sz','sz'])
        self.doConnectOut('sy',['sx','sz'])    
    
        _shapes = self.getShapes()
        if _shapes:
            log.debug("|{0}| >>  Removing old shapes...".format(_str_func))        
            mc.delete(_shapes)
            mDefineNull = self.getMessageAsMeta('defineNull')
            if mDefineNull:
                log.debug("|{0}| >>  Removing old defineNull...".format(_str_func))
                mDefineNull.delete()
    
        _size = self.atUtils('defineSize_get')
    
        #_sizeSub = _size / 2.0
        log.debug("|{0}| >>  Size: {1}".format(_str_func,_size))        
        _crv = CURVES.create_fromName(name='locatorForm',
                                      direction = 'z+', size = _size * .5)
    
        SNAP.go(_crv,self.mNode,)
        CORERIG.override_color(_crv, 'white')
        CORERIG.shapeParent_in_place(self.mNode,_crv,False)
        self.addAttr('cgmColorLock',True,lock=True,hidden=True)    
        mDefineNull = self.atUtils('stateNull_verify','define')
        md_handles = {}
        
       
        #self.UTILS.controller_walkChain(self,_resDefine['ml_handles'],'define')
            
        self.UTILS.rootShape_update(self, 'jack', 8.0)        

        for tag,mHandle in md_handles.iteritems():
            if cgmGEN.__mayaVersion__ >= 2018:
                mController = cgmMeta.controller_get(mHandle)
                
                try:
                    ATTR.connect("{0}.visProximityMode".format(self.mNode),
                             "{0}.visibilityMode".format(mHandle.mNode))    
                except Exception,err:
                    log.error(err)
                self.msgList_append('defineStuff',mController)
                
        BLOCKSHAPES.addJointRadiusVisualizer(self, mDefineNull)
        

    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

#=============================================================================================================
#>> Form
#=============================================================================================================
def formDelete(self):
    try:
        _str_func = 'formDelete'
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
            
        mNoTransformNull = self.getMessageAsMeta('noTransFormNull')
        if mNoTransformNull:
            mNoTransformNull.delete()
        
        
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


def layout_build(self, layout = None, key = None, castMesh = None):
    _str_func = 'layout_build'
    log.debug(log_start(_str_func))
    


def make_handle(self,):
    log.debug("|{0}| >> Shapers ...".format(_str_func)+ '-'*60)
    
    
    if _shape in ['cube']:
        _shapeDirection = 'z+'
    elif _shape in ['semiSphere']:
        _shapeDirection = 'y+'
    
    if _shape in ['circle','square']:
        _size = [v for v in self.baseSize[:-1]] + [None]
        _shapeDirection = 'y+'
    elif _shape in ['pyramid','semiSphere','sphere']:
        _size =  [_size_width,_size_height,_size_length]
    else:
        _size =  [_size_width,_size_length,_size_height]

    _crv = CURVES.create_controlCurve(self.mNode, shape=_shape,
                                      direction = _shapeDirection,
                                      bakeScale=False,
                                      sizeMode = 'fixed', size =_size)

    mHandle = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
    mHandle.p_parent = mFormNull
    _pos_mid = DIST.get_average_position(_l_basePos)
    if _shape in ['pyramid','semiSphere','circle','square']:
        mHandle.p_position = _l_basePos[0]
    else:
        mHandle.p_position = _pos_mid
        
    #if _shape in ['circle']:
    #    SNAP.aim_atPoint(mHandle.mNode, _l_basePos[-1], "z+",'y-','vector', _mVectorUp)
    #else:
    SNAP.aim_atPoint(mHandle.mNode, _l_basePos[-1],"y",'z-','vector', vectorUp=_mVectorUp)

    mHandle.doStore('cgmNameModifier','main')
    mHandle.doStore('cgmType','handle')
    mHandleFactory.copyBlockNameTags(mHandle)


    CORERIG.colorControl(mHandle.mNode,_side,'main',transparent = False) 

    mHandleFactory.setHandle(mHandle)

    #self.msgList_connect('formHandles',[mHandle.mNode])

    #Proxy geo ==================================================================================
    #reload(CORERIG)
    _proxy = CORERIG.create_proxyGeo(_proxyShape, [_size_width,_size_length,_size_height], 'y+',bakeScale=False)
    mProxy = cgmMeta.validateObjArg(_proxy[0], mType = 'cgmObject',setClass=True)
    
    mProxy.doSnapTo(mHandle.mNode)
    if _shape in ['pyramid','semiSphere','circle','square']:
        mProxy.p_position = _pos_mid
    #mProxy.p_position = _pos_mid
    #NAP.aim_atPoint(mHandle.mNode, _l_basePos[-1], "y",'z-','vector', _mVectorUp)
    
    #SNAPCALLS.snap(mProxy.mNode,mHandle.mNode, objPivot='boundingBox',objMode='y-',targetPivot='boundingBox',targetMode='y-')

    if mHandle.hasAttr('cgmName'):
        ATTR.copy_to(mHandle.mNode,'cgmName',mProxy.mNode,driven='target')        
    mProxy.doStore('cgmType','proxyHelper')
    self.msgList_connect('proxyMeshGeo',[mProxy])
    
    mProxy.doName()    

    mProxy.p_parent = mGeoGroup


    #CORERIG.colorControl(mProxy.mNode,_side,'sub',transparent=True)
    mHandleFactory.color(mProxy.mNode,_side,'sub',transparent=True)

    mProxy.connectParentNode(mHandle.mNode,'handle','proxyHelper')        
    mProxy.connectParentNode(self.mNode,'proxyHelper')        
    mProxy.connectParentNode(self.mNode,'handle','proxyHelper')        
    
    self.msgList_connect('formHandles',[mHandle.mNode,mProxy.mNode])

    attr = 'proxy'
    self.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
    NODEFACTORY.argsToNodes("%s.%sVis = if %s.%s > 0"%(_short,attr,_short,attr)).doBuild()
    NODEFACTORY.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(_short,attr,_short,attr)).doBuild()
            
            
    _baseDat = self.baseDat
    try:_baseDat['aHidden']
    except:_baseDat['aHidden']=[]
    
    for a in 'Vis','Lock':
        ATTR.set_hidden(_short,"{0}{1}".format(attr,a),True)
        ATTR.set_lock(_short,"{0}{1}".format(attr,a),True)
        _baseDat['aHidden'].append("{0}{1}".format(attr,a))
    self.baseDat = _baseDat
    #mProxy.resetAttrs()
    
    mGeoGroup.overrideEnabled = 1
    ATTR.connect("{0}.proxyVis".format(_short),"{0}.visibility".format(mGeoGroup.mNode) )
    ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayType".format(mGeoGroup.mNode) )        
    for mShape in mProxy.getShapes(asMeta=1):
        str_shape = mShape.mNode
        mShape.overrideEnabled = 0
        ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayTypes".format(str_shape) )
        ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayType".format(str_shape) )
        

    
def form(self):
    _str_func = 'form'
    log.info(log_start(_str_func))
    pass

#=============================================================================================================
#>> Prerig
#=============================================================================================================
def prerig(self):
    _str_func = 'prerig'
    log.info(log_start(_str_func))    
    #self._factory.puppet_verify()
    _side = self.atUtils('get_side')
    #Get some data...
    l_delete = []
    
    mStateNull = BLOCKUTILS.stateNull_verify(self,'prerig')
    self.atUtils('module_verify')
    
    mBlockParent = self.p_blockParent
    if not mBlockParent:
        raise ValueError,log_msg(_str_func, "must have mBlockParent")
    
    mDriver = self.getMessageAsMeta('readerDriver')
    if not mDriver:
        raise ValueError,log_msg(_str_func, "must have mDriver")
        
    _shape = self.getEnumValueString('basicShape')    
    _shapeDirection = self.getEnumValueString('shapeDirection')
    _proxyShape = self.getEnumValueString('proxyShape')
    _mVectorUp = MATH.get_obj_vector(mDriver.mNode,'y+',asEuclid=True)    
    
    mCastMesh = mBlockParent.atUtils('get_castMesh',True)
    _mesh = mCastMesh.mNode
    l_delete.append(_mesh)
    
    _baseSize = self.jointRadius
    _controlSize = _baseSize * .75
    _jointSize = _baseSize * .25
    
    mHandleFactory = self.asHandleFactory()
    
    # Process...===================================================================================
    _l_layouts = self.datList_get('correctiveLayout',enum=True)
    for i,l in enumerate(_l_layouts):
        log.info(log_msg(_str_func,l))
        
        _d = {'dag':mDriver.mNode,
              'layout':l,
              'castMesh':_mesh,
              "loc":0}
        
        #mStateNull.addAttr('dagHandles_{0}'.format(i), attrType = 'message')
        ml_dags = []
        ml_shapes = []
        _res = CORRECTIVES.layout_getPoints(**_d)
        
        for n,p in _res.iteritems():
            mDagHelper = cgmMeta.validateObjArg( CURVES.create_fromName('axis3d', size = _jointSize,
                                                                        bakeScale=1), 
                                              'cgmControl',setClass=1)
            
            #if jointShape in ['axis3d']:
            mDagHelper.addAttr('cgmColorLock',True,lock=True,hidden=True)            
            #else:
            #    color(self, mDagHelper.mNode,side = side, controlType='sub')
                
            mDagHelper._verifyMirrorable()
            mDagHelper.p_position = p
            mDagHelper.p_orient = mDriver.p_orient
            mDagHelper.p_parent = mStateNull
            ml_dags.append(mDagHelper)
            
            mDagHelper.doStore('cgmName',n)            
            mDagHelper.doStore('cgmNameModifier',l)
            mDagHelper.doStore('cgmType','dag')
            mHandleFactory.copyBlockNameTags(mDagHelper)      
            #mDagHelper.doName()
        
            """
            mMasterGroup = mDagHelper.doGroup(True,True,
                                           asMeta=True,
                                           typeModifier = 'master',
                                           setClass='cgmObject')"""
        
        
            #mStateNull.connectChildNode(mDagHelper, _key+STR.capFirst(plugDag),'block')            

            
            #Control Shape --------------------------------------------------------------------
            
            if _shape in ['cube']:
                _shapeDirection = 'z+'
            elif _shape in ['semiSphere']:
                _shapeDirection = 'y+'
            
            if _shape in ['circle','square']:
                _size = [_controlSize,_controlSize,None]
                _shapeDirection = 'y+'
            elif _shape in ['pyramid','semiSphere','sphere']:
                _size =  [_controlSize,_controlSize,_controlSize]
            else:
                _size =  [_controlSize,_controlSize,_controlSize]
        
            _crv = CURVES.create_controlCurve(self.mNode, shape=_shape,
                                              direction = _shapeDirection,
                                              bakeScale=False,
                                              sizeMode = 'fixed', size =_size)
        
            mShapeHandle = cgmMeta.validateObjArg(_crv,'cgmObject',setClass=True)
            mShapeHandle.p_parent = mStateNull
            ml_shapes.append(mShapeHandle)

            mShapeHandle.doSnapTo(mDagHelper)
                
            
            mShapeHandle.doStore('cgmName',n)            
            mShapeHandle.doStore('cgmNameModifier',l)
            mShapeHandle.doStore('cgmType','handle')
            mHandleFactory.copyBlockNameTags(mShapeHandle)
        
        
            CORERIG.colorControl(mShapeHandle.mNode,_side,'sub',transparent = False) 
            mHandleFactory.setHandle(mShapeHandle)
        
            #self.msgList_connect('formShapeHandles',[mShapeHandle.mNode])
            
            
            mDagHelper.doStore('shapeHelper',mShapeHandle)
            mShapeHandle.doStore('dagHelper',mDagHelper)
            
            
            #mShapeHandle.doSnapTo()
            
        
            """
            #Proxy geo ==================================================================================
            #reload(CORERIG)
            _proxy = CORERIG.create_proxyGeo(_proxyShape, [_size_width,_size_length,_size_height], 'y+',bakeScale=False)
            mProxy = cgmMeta.validateObjArg(_proxy[0], mType = 'cgmObject',setClass=True)
            
            mProxy.doSnapTo(mShapeHandle.mNode)
            if _shape in ['pyramid','semiSphere','circle','square']:
                mProxy.p_position = _pos_mid
            #mProxy.p_position = _pos_mid
            #NAP.aim_atPoint(mShapeHandle.mNode, _l_basePos[-1], "y",'z-','vector', _mVectorUp)
            
            #SNAPCALLS.snap(mProxy.mNode,mShapeHandle.mNode, objPivot='boundingBox',objMode='y-',targetPivot='boundingBox',targetMode='y-')
        
            if mShapeHandle.hasAttr('cgmName'):
                ATTR.copy_to(mShapeHandle.mNode,'cgmName',mProxy.mNode,driven='target')        
            mProxy.doStore('cgmType','proxyHelper')
            self.msgList_connect('proxyMeshGeo',[mProxy])
            
            mProxy.doName()    
        
            mProxy.p_parent = mGeoGroup
        
        
            #CORERIG.colorControl(mProxy.mNode,_side,'sub',transparent=True)
            mHandleFactory.color(mProxy.mNode,_side,'sub',transparent=True)
        
            mProxy.connectParentNode(mShapeHandle.mNode,'handle','proxyHelper')        
            mProxy.connectParentNode(self.mNode,'proxyHelper')        
            mProxy.connectParentNode(self.mNode,'handle','proxyHelper')        
            
            self.msgList_connect('formShapeHandles',[mShapeHandle.mNode,mProxy.mNode])
        
            attr = 'proxy'
            self.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
            NODEFACTORY.argsToNodes("%s.%sVis = if %s.%s > 0"%(_short,attr,_short,attr)).doBuild()
            NODEFACTORY.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(_short,attr,_short,attr)).doBuild()
                    
                    
            _baseDat = self.baseDat
            try:_baseDat['aHidden']
            except:_baseDat['aHidden']=[]
            
            for a in 'Vis','Lock':
                ATTR.set_hidden(_short,"{0}{1}".format(attr,a),True)
                ATTR.set_lock(_short,"{0}{1}".format(attr,a),True)
                _baseDat['aHidden'].append("{0}{1}".format(attr,a))
            self.baseDat = _baseDat
            #mProxy.resetAttrs()
            
            mGeoGroup.overrideEnabled = 1
            ATTR.connect("{0}.proxyVis".format(_short),"{0}.visibility".format(mGeoGroup.mNode) )
            ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayType".format(mGeoGroup.mNode) )        
            for mShape in mProxy.getShapes(asMeta=1):
                str_shape = mShape.mNode
                mShape.overrideEnabled = 0
                ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayTypes".format(str_shape) )
                ATTR.connect("{0}.proxyLock".format(_short),"{0}.overrideDisplayType".format(str_shape) )            
            
            
                """        
        ATTR.set_message(mStateNull.mNode, 'handleDags_{0}'.format(i), [mObj.mNode for mObj in ml_dags], simple =True, multi=True)
        ATTR.set_message(mStateNull.mNode, 'handleShapes_{0}'.format(i), [mObj.mNode for mObj in ml_shapes], simple =True, multi=True)
                
        
        #mStateNull.__dict__['dagHandles_{0}'.format(i)] = ml_dags
        
    
    #Get our list of layouts...

    
    
    mc.delete(l_delete)    



def prerigDelete(self):
    return True


#=============================================================================================================
#>> rig
#=============================================================================================================
def rigDelete(self):
    return 
            
def is_rig(self):
    try:
        _str_func = 'is_rig'
        _l_missing = []
        
        _d_links = {'moduleTarget' : ['constrainNull']}
        
        for plug,l_links in _d_links.iteritems():
            _mPlug = self.getMessage(plug,asMeta=True)
            if not _mPlug:
                _l_missing.append("{0} : {1}".format(plug,l_links))
                continue
            for l in l_links:
                if not _mPlug[0].getMessage(l):
                    _l_missing.append(plug + '.' + l)
    
        if _l_missing:
            log.info("|{0}| >> Missing...".format(_str_func))  
            for l in _l_missing:
                log.info("|{0}| >> {1}".format(_str_func,l))  
            return False
        return True
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


#=============================================================================================================
#>> Skeleton
#=============================================================================================================
def skeleton_build(self, forceNew = True):
    _short = self.mNode
    _str_func = '[{0}] > skeleton_build'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func)) 
    
    _radius = self.jointRadius / 2
    ml_joints = []
    
    mModule = self.moduleTarget
    if not mModule:
        raise ValueError,"No moduleTarget connected"
    
    mRigNull = mModule.rigNull
    if not mRigNull:
        raise ValueError,"No rigNull connected"
    
    #Find our parent joint --------------------------------------
    mParentModule = self.p_blockParent.moduleTarget
    l_targetJoints = mParentModule.rigNull.msgList_get('moduleJoints',asMeta = False, cull = True)
    if not l_targetJoints:
        raise ValueError,"mParentModule has no module joints."    
    
    _closestJoint = DIST.get_closestTarget(self.mNode, l_targetJoints)
    mParentJoint = cgmMeta.asMeta(_closestJoint)

    #>> If skeletons there, delete ------------------------------------------------------------------------ 
    _bfr = mRigNull.msgList_get('moduleJoints',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> Joints detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
    
    # Process...===================================================================================
    _l_layouts = self.datList_get('correctiveLayout',enum=True)
    ml_joints = []
    for i,l in enumerate(_l_layouts):
        log.info(log_msg(_str_func,l))
        
        for mDag in self.prerigNull.getMessageAsMeta('handleDags_{0}'.format(i)):
            mJoint = mDag.doCreateAt('joint')
            mJoint.doCopyNameTagsFromObject(mDag.mNode,ignore = ['cgmType'])
            mJoint.doStore('cgmType','skinJoint')
            mJoint.doName()
            
            mJoint.p_parent = mParentJoint
            
            JOINTS.freezeOrientation(mJoint)
            
            mDag.doStore('joint',mJoint)
            mJoint.rotateOrder = 5
            mJoint.displayLocalAxis = 1
            mJoint.radius = _radius 
            
            ml_joints.append(mJoint)
    
        

    mRigNull.msgList_connect('moduleJoints', ml_joints) 
 
    
    return ml_joints

        
def skeleton_check(self):
    if self.getMessage('moduleTarget'):
        if self.moduleTarget.getMessage('rigNull'):
            if self.moduleTarget.rigNull.msgList_get('moduleJoints'):
                return True
    return False

def skeletonDelete(self):
    if is_skeletonized(self):
        log.warning("MUST ACCOUNT FOR CHILD JOINTS")
        mc.delete(self.getMessage('rootJoint'))
    return True
            

#=============================================================================================================
#>> rig
#=============================================================================================================
#NOTE - self here is a rig Factory....

d_preferredAngles = {'head':[0,-10, 10]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
d_rotateOrders = {'head':'yxz'}

#Rig build stuff goes through the rig build factory ------------------------------------------------------
@cgmGEN.Timer
def rig_dataBuffer(self):
    try:
        _short = self.d_block['shortName']
        _str_func = 'rig_dataBuffer'
        log.debug("|{0}| >> ...".format(_str_func)+cgmGEN._str_hardBreak)
        log.debug(self)
        
        mBlock = self.mBlock
        mModule = self.mModule
        mRigNull = self.mRigNull
        mPrerigNull = mBlock.prerigNull
        
        
        #mMasterNull = self.d_module['mMasterNull']
        
        
        #Settings Parent
        self.mSettingsParent = None
        mModuleParent =  self.d_module['mModuleParent']
        if mModuleParent:
            mSettings = mModuleParent.rigNull.settings
        else:
            log.debug("|{0}| >>  using puppet...".format(_str_func))
            mSettings = self.d_module['mMasterControl'].controlVis
            self.mSettingsParent = mSettings
            
        log.debug(cgmGEN._str_subLine)
            
        #  data ======================================================================================
        log.debug(log_sub(_str_func,'data'))
        md_layouts = {}
        
        _l_layouts = mBlock.datList_get('correctiveLayout',enum=True)
        
        for i,l in enumerate(_l_layouts):
            log.info(log_msg(_str_func,l))
            md_layouts["{0}_{1}".format(l,i)] = {}
            _d = md_layouts["{0}_{1}".format(l,i)]
            _d['key'] = l
            _d['dags'] = []
            _d['shapes'] = []
            
            for mDag in mPrerigNull.getMessageAsMeta('handleDags_{0}'.format(i)):
                _d['dags'].append(mDag)
                _d['shapes'].append(mDag.shapeHelper)
                
        self.md_layouts = md_layouts
        pprint.pprint(md_layouts)
        
        
        #...
        md_readers = {}
        _l_keys = mBlock.datList_get('readerKey',enum=True)
        
        for i,l in enumerate(_l_keys):
            log.info(log_msg(_str_func,l))
            md_readers["{0}_{1}".format(l,i)] = {}
            _d = md_readers["{0}_{1}".format(l,i)]
            
            _d['type'] = mBlock.getEnumValueString('readerType_{0}'.format(i))
                
        self.md_readers = md_readers
        pprint.pprint(md_readers)        
        
        #Find our parent joint --------------------------------------
        l_targetJoints = mModuleParent.rigNull.msgList_get('moduleJoints',asMeta = False, cull = True)
        if not l_targetJoints:
            raise ValueError,"mParentModule has no module joints."    
        
        _closestJoint = DIST.get_closestTarget(mBlock.readerDriver.mNode, l_targetJoints)
        self.mReaderDriver =  cgmMeta.asMeta(_closestJoint)
        
        _closestJoint = DIST.get_closestTarget(mBlock.readerParent.mNode, l_targetJoints)
        self.mReaderParent =  cgmMeta.asMeta(_closestJoint)        
        

        #Offset ============================================================================    
        self.v_offset = self.mPuppet.atUtils('get_shapeOffset')
        log.debug("|{0}| >> self.v_offset: {1}".format(_str_func,self.v_offset))

        self.d_blockNameDict = mBlock.atUtils('get_baseNameDict')
        
        """
        #DynParents =============================================================================
        self.UTILS.get_dynParentTargetsDat(self)
        
        
        #rotateOrder =============================================================================
        _str_orientation = self.d_orientation['str']
        
        self.rotateOrder = "{0}{1}{2}".format(_str_orientation[1],_str_orientation[2],_str_orientation[0])
        self.rotateOrderIK = "{2}{0}{1}".format(_str_orientation[0],_str_orientation[1],_str_orientation[2])
        
        log.debug("|{0}| >> rotateOrder | self.rotateOrder: {1}".format(_str_func,self.rotateOrder))
        log.debug("|{0}| >> rotateOrder | self.rotateOrderIK: {1}".format(_str_func,self.rotateOrderIK))
    
        log.debug(cgmGEN._str_subLine)
        """
        log.debug(cgmGEN._str_subLine)    
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        


def rig_skeleton(self):
    _short = self.d_block['shortName']
    
    _str_func = '[{0}] > rig_skeleton'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
        
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    #ml_jointsToConnect = []
    #ml_jointsToHide = []
    ml_joints = mRigNull.msgList_get('moduleJoints')

    self.d_joints['ml_moduleJoints'] = ml_joints
    #BLOCKUTILS.skeleton_pushSettings(ml_joints, self.d_orientation['str'], self.d_module['mirrorDirection'],
    #                                 d_rotateOrders, d_preferredAngles)
    
    for mJnt in ml_joints:
        mJnt.segmentScaleCompensate = 0
        
    ml_rigJoints = BLOCKUTILS.skeleton_buildDuplicateChain(self,ml_joints, 'rig', self.mRigNull,'rigJoints','rigJoint')
    
    for mJnt in ml_rigJoints:
        mJnt.p_parent = False

    
    #...joint hide -----------------------------------------------------------------------------------
    """
    for mJnt in ml_jointsToHide:
        try:
            mJnt.drawStyle =2
        except:
            mJnt.radius = .00001"""
            
    #...connect... 
    #self.fnc_connect_toRigGutsVis( ml_jointsToConnect )
    
    #BUILDERUTILS.joints_connectToParent(self)
    log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    return

def rig_shapes(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_shapes'.format(_short)
    log.debug(log_start(_str_func))
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    
    #Get our base size from the block
    _side = BLOCKUTILS.get_side(self.mBlock)
    _short_module = self.mModule.mNode
    _offset = self.v_offset
    
    #pprint.pprint(vars())
    
    
    log.debug(log_sub(_str_func,"Layouts"))

    
    for k,d in self.md_layouts.iteritems():
        log.debug(log_sub(_str_func,k))
        
        self.md_layouts[k]['handles'] = []
        l = self.md_layouts[k]['handles']
        for i,mDag in enumerate(d['dags']):
            
            mHandle = mDag.doCreateAt()
            CORERIG.shapeParent_in_place(mHandle.mNode, d['shapes'][i].mNode)
            
            mHandle.doCopyNameTagsFromObject(mDag.mNode,ignore = ['cgmType'])
            mHandle.doName()
            
            l.append(mHandle)
        
        
    #...
    log.debug(log_sub(_str_func,"Readers"))
    if self.mReaderDriver and self.mReaderParent:
        _size_reader = DIST.get_distance_between_points(self.mReaderDriver.p_position,
                                                        self.mReaderParent.p_position)/4
        for k,d in self.md_readers.iteritems():
            log.debug(log_sub(_str_func,k))
            
            mShape = cgmMeta.validateObjArg( CURVES.create_fromName('pyramid', size = [_size_reader,_size_reader,_size_reader*2],
                                                                        bakeScale=1), 
                                              'cgmControl',setClass=1)
            
            mReader = self.mReaderDriver.doCreateAt(setClass=True)
            
            mShape.doSnapTo(mReader)
            
            mShape.p_position = mReader.getPositionByAxisDistance('{0}+'.format(self.d_orientation['str'][0]), _size_reader)
            CORERIG.shapeParent_in_place(mReader.mNode, mShape.mNode, False)
            
            mReader.doStore('cgmName', "{0}_{1}".format(k,self.mReaderDriver.p_nameBase))
            mReader.doName()
            
            d['handle'] = mReader
            CORERIG.colorControl(mReader.mNode,_side,'sub')
            
            
            
        
    
    """
    #Direct Controls =============================================================================
    log.info("|{0}| >> Direct controls...".format(_str_func))      
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    
    if len(ml_rigJoints) < 3:
        d_direct = {'size':_size/3}
    else:
        d_direct = {'size':None}
        
    ml_directShapes = self.atBuilderUtils('shapes_fromCast',
                                          ml_rigJoints,
                                          mode ='direct',**d_direct)
                                                                                                                                                            #offset = 3

    for i,mCrv in enumerate(ml_directShapes):
        CORERIG.colorControl(mCrv.mNode,_side,'sub')
        CORERIG.shapeParent_in_place(ml_rigJoints[i].mNode,mCrv.mNode, False, replaceShapes=True)
        for mShape in ml_rigJoints[i].getShapes(asMeta=True):
            mShape.doName()
            
    
    for mJnt in ml_rigJoints:
        try:
            mJnt.drawStyle =2
        except:
            mJnt.radius = .00001"""

        


    
def rig_controls(self):
    try:
        _short = self.d_block['shortName']
        _str_func = '[{0}] > rig_controls'.format(_short)
        log.info("|{0}| >> ...".format(_str_func))  
        _start = time.clock()
      
        mBlock = self.mBlock
        mRigNull = self.mRigNull
        ml_controlsAll = []#we'll append to this list and connect them all at the end
        mRootParent = self.mDeformNull
        mSettings = mRigNull.settings
        
            
        mHandle = mRigNull.handle
        
        # Drivers ==============================================================================================    
        #>> vis Drivers ================================================================================================	
        mPlug_visSub = self.atBuilderUtils('build_visModuleMD','visSub')
        mPlug_visDirect = self.atBuilderUtils('build_visModuleMD','visDirect')
        self.atBuilderUtils('build_visModuleProxy')#...proxyVis wiring

        # Connect to visModule ...
        ATTR.connect(self.mPlug_visModule.p_combinedShortName, 
                     "{0}.visibility".format(self.mDeformNull.mNode))        
        

            

        #mHandle ========================================================================================
        log.info("|{0}| >> Found handle : {1}".format(_str_func, mHandle))
        d_space = {'addDynParentGroup':True}
        if mBlock.numSpacePivots:
            d_space['addSpacePivots'] = mBlock.numSpacePivots
            
        _d = MODULECONTROL.register(mHandle,
                                    addConstraintGroup=False,
                                    addSDKGroup = mBlock.buildSDK,
                                    mirrorSide= self.d_module['mirrorDirection'],
                                    mirrorAxis="translateX,rotateY,rotateZ",
                                    makeAimable = True,**d_space)
        
        mHandle = _d['mObj']
        mHandle.masterGroup.parent = mRootParent
        ml_controlsAll.append(mHandle)            
        
        #>> settings ========================================================================================
        if mSettings.mNode != mHandle.mNode:
            log.info("|{0}| >> Settings setup : {1}".format(_str_func, mSettings))        
            MODULECONTROL.register(mSettings)
            mSettings.masterGroup.parent = mHandle
            ml_controlsAll.append(mSettings)
            
            
        #Settings Parent ==================================================================================
        if self.mSettingsParent:
            str_attr = "snapPoint_{0}".format(self.d_module['partName'])

            #Build the network
            self.mSettingsParent.addAttr(str_attr,enumName = 'off:lock:on',
                                         defaultValue = 2, value = 0,
                                         attrType = 'enum',keyable = False,
                                         hidden = False)
            str_objName = mHandle.mNode
            str_driver = self.mSettingsParent.mNode
            mHandle.overrideEnabled = 1
            d_ret = NODEFACTORY.argsToNodes("%s.overrideVisibility = if %s.%s > 0"%(str_objName,str_driver,str_attr)).doBuild()
            log.debug(d_ret)
            d_ret = NODEFACTORY.argsToNodes("%s.overrideDisplayType = if %s.%s == 2:0 else 2"%(str_objName,str_driver,str_attr)).doBuild()
            
            for shape in mc.listRelatives(mHandle.mNode,shapes=True,fullPath=True):
                log.debug(shape)
                mc.connectAttr("%s.overrideVisibility"%str_objName,"%s.overrideVisibility"%shape,force=True)
                mc.connectAttr("%s.overrideDisplayType"%str_objName,"%s.overrideDisplayType"%shape,force=True)            
            
    
        #>> Direct Controls ================================================================================
        ml_rigJoints = self.mRigNull.msgList_get('rigJoints')
        ml_controlsAll.extend(ml_rigJoints)
        
        for i,mObj in enumerate(ml_rigJoints):
            d_buffer = MODULECONTROL.register(mObj,
                                              typeModifier='direct',
                                              addDynParentGroup = True,                                          
                                              mirrorSide= self.d_module['mirrorDirection'],
                                              mirrorAxis="translateX,rotateY,rotateZ",
                                              makeAimable = False)
    
            mObj = d_buffer['instance']
            ATTR.set_hidden(mObj.mNode,'radius',True)        
            if mObj.hasAttr('cgmIterator'):
                ATTR.set_hidden(mObj.mNode,'cgmIterator',True)        
                
            for mShape in mObj.getShapes(asMeta=True):
                ATTR.connect(mPlug_visDirect.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
    
    
        # Pivots =================================================================================================
        if mBlock.getMessage('pivotHelper'):
            log.info("|{0}| >> Pivot helper found".format(_str_func))
            for a in 'center','front','back','left','right':#This order matters
                str_a = 'pivot' + a.capitalize()
                if mRigNull.getMessage(str_a):
                    log.info("|{0}| >> Found: {1}".format(_str_func,str_a))
                    
                    mPivot = mRigNull.getMessage(str_a,asMeta=True)[0]
                    
                    d_buffer = MODULECONTROL.register(mPivot,
                                                      typeModifier='pivot',
                                                      mirrorSide= self.d_module['mirrorDirection'],
                                                      mirrorAxis="translateX,rotateY,rotateZ",
                                                      makeAimable = False)
                    
                    mPivot = d_buffer['instance']
                    for mShape in mPivot.getShapes(asMeta=True):
                        ATTR.connect(mPlug_visSub.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))                
                    
                    
                    ml_controlsAll.append(mPivot)
            
        
        #>> headLookAt ========================================================================================
        if mRigNull.getMessage('lookAtHandle'):
            mLookAtHandle = mRigNull.lookAtHandle
            log.info("|{0}| >> Found lookAtHandle : {1}".format(_str_func, mLookAtHandle))
            MODULECONTROL.register(mLookAtHandle,
                                   typeModifier='lookAt',
                                   addSpacePivots = 1,
                                   addDynParentGroup = True,
                                   addConstraintGroup=False,
                                   mirrorSide= self.d_module['mirrorDirection'],
                                   mirrorAxis="translateX,rotateY,rotateZ",
                                   makeAimable = False)
            mLookAtHandle.masterGroup.parent = mRootParent
            ml_controlsAll.append(mLookAtHandle)
    
        mHandleFactory = mBlock.asHandleFactory()
        for mCtrl in ml_controlsAll:            
            if mCtrl.hasAttr('radius'):
                ATTR.set(mCtrl.mNode,'radius',0)        
            
            ml_pivots = mCtrl.msgList_get('spacePivots')
            if ml_pivots:
                log.debug("|{0}| >> Coloring spacePivots for: {1}".format(_str_func,mCtrl))
                for mPivot in ml_pivots:
                    mHandleFactory.color(mPivot.mNode, controlType = 'sub')            
                    ml_controlsAll.append(mPivot)    
    
    
            for mShape in mCtrl.getShapes(asMeta=True):
                if not ATTR.get_driver(mShape.mNode,'overrideVisibility'):
                    ATTR.connect(self.mPlug_visModule.p_combinedShortName, "{0}.overrideVisibility".format(mShape.mNode))
                        
        #Connections =======================================================================================
        #ml_controlsAll = self.atBuilderUtils('register_mirrorIndices', ml_controlsAll)
        mRigNull.msgList_connect('controlsAll',ml_controlsAll)
        mRigNull.moduleSet.extend(ml_controlsAll)
        
        log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))                
        
        
        
        return 
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def rig_frame(self):
    try:
        _short = self.d_block['shortName']
        _str_func = '[{0}] > rig_rigFrame'.format(_short)
        log.info("|{0}| >> ...".format(_str_func))  
        _start = time.clock()
        
        mBlock = self.mBlock
        ml_formHandles = mBlock.msgList_get('formHandles')
        mMainHandle = self.mRootFormHandle#ml_formHandles[0]    
        mRigNull = self.mRigNull
        mHandle = mRigNull.handle        
        log.info("|{0}| >> Found mHandle : {1}".format(_str_func, mHandle))
        
        #Changing targets - these change based on how the setup rolls through
        mDirectDriver = mHandle
        mAimDriver = mHandle
        mRootParent = self.mDeformNull
        
        if mBlock.parentToDriver:
            #This was causing issues with toe setup , need to resolve...
            log.debug("|{0}| >> Parent to driver".format(_str_func))
            #raise ValueError,"This was causing issues with toe setup , need to resolve..."
            self.mDeformNull.p_parent = self.md_dynTargetsParent['attachDriver'].mNode        
        
        #Pivot Setup ========================================================================================
        if mBlock.getMessage('pivotHelper'):
            log.info("|{0}| >> Pivot setup...".format(_str_func))
            
            mPivotResultDriver = mHandle.doCreateAt()
            mPivotResultDriver.addAttr('cgmName','pivotResult')
            mPivotResultDriver.addAttr('cgmType','driver')
            mPivotResultDriver.doName()
            
            mPivotResultDriver.addAttr('cgmAlias', 'PivotResult')
            
            mDirectDriver = mPivotResultDriver
            mAimDriver = mPivotResultDriver
            mRigNull.connectChildNode(mPivotResultDriver,'pivotResultDriver','rigNull')#Connect    
     
            mBlock.atBlockUtils('pivots_setup', mControl = mHandle, mRigNull = mRigNull, pivotResult = mPivotResultDriver, rollSetup = 'default',
                                front = 'front', back = 'back')#front, back to clear the toe, heel defaults
            
    
        #Aim ========================================================================================
        if mBlock.addAim:
            log.info("|{0}| >> Aim setup...".format(_str_func))
            mSettings = mRigNull.settings
            
            mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
            
            mAimFKJoint = mRigNull.getMessage('aimFKJoint', asMeta=True)[0]
            mAimIKJoint = mRigNull.getMessage('aimIKJoint', asMeta=True)[0]
            mAimBlendJoint = mRigNull.getMessage('aimBlendJoint', asMeta=True)[0]
            
            mDirectDriver = mAimBlendJoint
            mAimLookAt = mRigNull.lookAtHandle
            
            ATTR.connect(mPlug_aim.p_combinedShortName, "{0}.v".format(mAimLookAt.mNode))
            
            #Setup Aim -------------------------------------------------------------------------------------
            mc.aimConstraint(mAimLookAt.mNode,
                             mAimIKJoint.mNode,
                             maintainOffset = False, weight = 1,
                             aimVector = self.d_orientation['vectorAim'],
                             upVector = self.d_orientation['vectorUp'],
                             worldUpVector = self.d_orientation['vectorUp'],
                             worldUpObject = mAimDriver.mNode,
                             worldUpType = 'objectRotation' )
    
            #Setup blend ----------------------------------------------------------------------------------
            RIGCONSTRAINT.blendChainsBy(mAimFKJoint,mAimIKJoint,mAimBlendJoint,
                                        driver = mPlug_aim.p_combinedName,l_constraints=['orient'])
            
            #Parent pass ---------------------------------------------------------------------------------
            mAimLookAt.masterGroup.parent = mAimDriver
            
            for mObj in mAimFKJoint,mAimIKJoint,mAimBlendJoint:
                mObj.parent = mAimDriver
    
        else:
            log.info("|{0}| >> NO Head IK setup...".format(_str_func))    
        
    
        #Direct  ===================================================================================
        ml_rigJoints = mRigNull.msgList_get('rigJoints')
        
        #Parent the direct control to the 
        if ml_rigJoints[0].getMessage('masterGroup'):
            ml_rigJoints[0].masterGroup.parent = mDirectDriver
        else:
            ml_rigJoints[0].parent = mDirectDriver
            
        log.info("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f"%(time.clock()-_start)))
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
def rig_cleanUp(self):
    _short = self.d_block['shortName']
    _str_func = '[{0}] > rig_cleanUp'.format(_short)
    log.info("|{0}| >> ...".format(_str_func))  
    _start = time.clock()
    
    mBlock = self.mBlock
    mRigNull = self.mRigNull
    mHandle = mRigNull.handle            
    mSettings = mRigNull.settings
    
    
    mMasterControl= self.d_module['mMasterControl']
    mMasterDeformGroup= self.d_module['mMasterDeformGroup']    
    mMasterNull = self.d_module['mMasterNull']
    mModuleParent = self.d_module['mModuleParent']
    mPlug_globalScale = self.d_module['mPlug_globalScale']
    
    
    #>>  Parent and constraining joints and rig parts =======================================================
    #>>>> mSettings.masterGroup.parent = mHandle
    
    #>>  DynParentGroups - Register parents for various controls ============================================
    #>>  DynParentGroups - Register parents for various controls ============================================
    ml_baseDynParents = []
    ml_endDynParents = self.ml_dynParentsAbove + self.ml_dynEndParents# + [mRoot]
    ml_ikDynParents = []
    
    
    #...Handle -----------------------------------------------------------------------------------   
    ml_targetDynParents = copy.copy(ml_baseDynParents)
    ml_targetDynParents.append(self.md_dynTargetsParent['attachDriver'])
    ml_targetDynParents.extend(ml_endDynParents)
    
    ml_targetDynParents.append(self.md_dynTargetsParent['world'])
    
    mRoot = mRigNull.getMessageAsMeta('rigRoot')
    if mRoot:
        mDynGroup = mRoot.getMessageAsMeta('dynParentGroup')
        mDynGroup.dynMode = 0
        for o in ml_targetDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
        
        ml_targetDynParents.insert(0,mRoot)
    
    #...don't add space pivots till here    
    ml_targetDynParents.extend(mHandle.msgList_get('spacePivots',asMeta = True))
    
    #Add our parents
    mDynGroup = mHandle.getMessageAsMeta('dynParentGroup')
    if mDynGroup:
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
        mDynGroup.dynMode = 0
    
        for o in ml_targetDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
    else:
        mc.parentConstraint(self.md_dynTargetsParent['attachDriver'].mNode,
                            mHandle.masterGroup.mNode,maintainOffset = True)
        mc.scaleConstraint(self.md_dynTargetsParent['attachDriver'].mNode,
                            mHandle.masterGroup.mNode,maintainOffset = True)
    #mDynGroup.dynFollow.parent = mMasterDeformGroup
    
    
    #Direct ---------------------------------------------------------------------------------------------
    if mBlock.spaceSwitch_direct:
        for mControl in mRigNull.msgList_get('rigJoints'):
            _short_direct = mControl.p_nameBase
            if mControl.getMessage('dynParentGroup'):
                log.info("|{0}| >> Direct control: {1}".format(_str_func,_short_direct))
                ml_directHandleDynParents = copy.copy(ml_baseDynParents)
                ml_directHandleDynParents.extend(ml_endDynParents)
                
                mDriver = mControl.masterGroup.getParent(asMeta=True)
                if mDriver:
                    ml_directHandleDynParents.insert(0, mDriver)
                    if not mDriver.hasAttr('cgmAlias'):
                        mDriver.addAttr('cgmAlias',_short_direct + '_driver')
                    
                mDynGroup = mControl.dynParentGroup
                log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
                mDynGroup.dynMode = 0
            
                for o in ml_directHandleDynParents:
                    mDynGroup.addDynParent(o)
                mDynGroup.rebuild()        

    
    #...look at ------------------------------------------------------------------------------------------
    if mRigNull.getMessage('lookAtHandle'):
        log.info("|{0}| >> LookAt setup...".format(_str_func))
        
        mPlug_aim = cgmMeta.cgmAttr(mSettings.mNode,'blend_aim',attrType='float',lock=False,keyable=True)
        

        mHeadLookAt = mRigNull.lookAtHandle        
        mHeadLookAt.setAttrFlags(attrs='v')
        
        #...dynParentGroup...
        ml_headLookAtDynParents = copy.copy(ml_baseDynParents)
        ml_headLookAtDynParents.extend(mHeadLookAt.msgList_get('spacePivots',asMeta = True))
        ml_headLookAtDynParents.extend(ml_baseDynParents_end)
        
        ml_headLookAtDynParents.insert(0, mHandle)
        
        
        mPivotResultDriver = mRigNull.getMessage('pivotResultDriver',asMeta=True)
        if mPivotResultDriver:
            ml_headLookAtDynParents.insert(0, mPivotResultDriver)

            
        #mHandle.masterGroup.addAttr('cgmAlias','headRoot')
        
        #Add our parents...
        mDynGroup = mHeadLookAt.dynParentGroup
        log.info("|{0}| >> dynParentSetup : {1}".format(_str_func,mDynGroup))  
    
        for o in ml_headLookAtDynParents:
            mDynGroup.addDynParent(o)
        mDynGroup.rebuild()
        

    #>>  Lock and hide ======================================================================================
    mHandle.visDirect = 0
    
    #>>  Attribute defaults =================================================================================
    
    mRigNull.version = self.d_block['buildVersion']
    mBlock.blockState = 'rig'
    mBlock.UTILS.set_blockNullFormState(mBlock)
    self.UTILS.rigNodes_store(self)




def create_simpleMesh(self, deleteHistory = True, cap=True, skin = False, parent=False):
    try:
        _str_func = 'create_simpleMesh'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
        log.debug("{0}".format(self))
        
        if self.blockProfile in ['snapPoint']:
            return True
            
        
        if skin:
            mModuleTarget = self.getMessage('moduleTarget',asMeta=True)
            if not mModuleTarget:
                return log.error("|{0}| >> Must have moduleTarget for skining mode".format(_str_func))
            mModuleTarget = mModuleTarget[0]
            ml_moduleJoints = mModuleTarget.rigNull.msgList_get('moduleJoints')
            if not ml_moduleJoints:
                return log.error("|{0}| >> Must have moduleJoints for skining mode".format(_str_func))        
        
        
        
        ml_geo = self.msgList_get('proxyMeshGeo')
        ml_proxy = []
        mMeshCheck = self.getMessageAsMeta('proxyHelper')
        
        if ml_geo:
            log.debug("|{0}| >> ml_geo...".format(_str_func))
            
            str_setup = self.getEnumValueString('proxyShape')
            if str_setup in ['shapers']:
                d_kws = {}
                mMesh = self.UTILS.create_simpleLoftMesh(self,divisions=5)[0]
                ml_proxy = [mMesh]
                
            for i,mGeo in enumerate(ml_geo):
                if mGeo == mMeshCheck:
                    print 'nope...'
                    continue
                log.debug("|{0}| >> proxyMesh creation from: {1}".format(_str_func,mGeo))
                if mGeo.getMayaType() == 'nurbsSurface':
                    d_kws = {'mode':'general',
                             'uNumber':self.loftSplit,
                             'vNumber':self.loftSides,
                             }
                    mMesh = RIGCREATE.get_meshFromNurbs(self.proxyHelper,**d_kws)
                else:
                    mMesh = mGeo.doDuplicate(po=False)
                    mMesh.p_parent = False
                    
                ml_proxy.append(mMesh)            
            """
            for i,mGeo in enumerate(ml_geo):
                log.debug("|{0}| >> proxyMesh creation from: {1}".format(_str_func,mGeo))                        
                if mGeo.getMayaType() == 'nurbsSurface':
                    mMesh = RIGCREATE.get_meshFromNurbs(self.proxyHelper,
                                                        mode = 'general',
                                                        uNumber = self.loftSplit, vNumber=self.loftSides)
                else:
                    mMesh = mGeo.doDuplicate(po=False)
                    #mMesh.p_parent = False
                    #mDup = mBlock.proxyHelper.doDuplicate(po=False)
                mMesh.rename("{0}_{1}_mesh".format(self.p_nameBase,i))
                #mDup.inheritsTransform = True
                ml_proxy.append(mMesh)        """
        
            for mGeo in ml_proxy:
                CORERIG.color_mesh(mGeo.mNode,'puppetmesh')
            #mDup = self.proxyHelper.doDuplicate(po=False)
            
            if len(ml_proxy) > 1:
                _mesh = mc.polyUnite([mObj.mNode for mObj in ml_proxy], ch=False )[0]
                mMesh = cgmMeta.asMeta(_mesh)
                for mObj in ml_proxy[1:]:
                    try:mObj.delete()
                    except:pass
                ml_proxy = [mMesh]
 
            for i,mMesh in enumerate(ml_proxy):
                if parent and skin:
                    mMesh.p_parent=parent
                
                if skin:
                    mc.skinCluster ([mJnt.mNode for mJnt in ml_moduleJoints],
                                    mMesh.mNode,
                                    tsb=True,
                                    bm=1,
                                    maximumInfluences = 3,
                                    normalizeWeights = 1, dropoffRate=10)            
                mMesh.rename('{0}_{1}_puppetmesh_geo'.format(self.p_nameBase,i))
        return ml_proxy
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err,localDat=vars())        

def build_proxyMesh(self, forceNew = True, puppetMeshMode = False,**kws):
    """
    Build our proxyMesh
    """
    _short = self.p_nameShort
    _str_func = '[{0}] > build_proxyMesh'.format(_short)
    log.debug("|{0}| >> ...".format(_str_func))  
    _start = time.clock()

    mBlock = self
    
    if self.blockProfile in ['snapPoint']:
        log.debug("|{0}| >> snapPoint".format(_str_func))  
        
        return True
    
    if not mBlock.meshBuild:
        log.error("|{0}| >> meshBuild off".format(_str_func))                        
        return False
    
    mModule = self.moduleTarget    
    
    mRigNull = mModule.rigNull
    mSettings = mRigNull.settings
    mPuppet = self.atUtils('get_puppet')
    mMaster = mPuppet.masterControl
    mPuppetSettings = mMaster.controlSettings
    str_partName = mModule.get_partNameBase()
    mHandle = mRigNull.handle
    
    
    #>> If proxyMesh there, delete ----------------------------------------------------------------------------------- 
    if puppetMeshMode:
        _bfr = mRigNull.msgList_get('puppetProxyMesh',asMeta=True)
        if _bfr:
            log.debug("|{0}| >> puppetProxyMesh detected...".format(_str_func))            
            if forceNew:
                log.debug("|{0}| >> force new...".format(_str_func))                            
                mc.delete([mObj.mNode for mObj in _bfr])
            else:
                return _bfr        
            
    _bfr = mRigNull.msgList_get('proxyMesh',asMeta=True)
    if _bfr:
        log.debug("|{0}| >> proxyMesh detected...".format(_str_func))            
        if forceNew:
            log.debug("|{0}| >> force new...".format(_str_func))                            
            mc.delete([mObj.mNode for mObj in _bfr])
        else:
            return _bfr
    
    if not self.proxyType:
        log.info("No proxyType set")                            
        return False
        
    #>> Build bbProxy -----------------------------------------------------------------------------
    mMeshCheck = mBlock.getMessageAsMeta('proxyHelper')
    ml_geo = mBlock.msgList_get('proxyMeshGeo')
    #if not ml_geo and mMeshCheck:
        #ml_geo = [mMeshCheck]
            
    ml_proxy = []
    ml_rigJoints = mRigNull.msgList_get('rigJoints')
    str_setup = self.getEnumValueString('proxyShape')
    if str_setup == 'shapers':
        d_kws = {}
        mMesh = self.UTILS.create_simpleLoftMesh(self,divisions=5)[0]
        ml_proxy = [mMesh]
        
    if ml_geo:
        for i,mGeo in enumerate(ml_geo):
            #if mGeo == mMeshCheck:
            #    continue
            log.debug("|{0}| >> proxyMesh creation from: {1}".format(_str_func,mGeo))                        
            if mGeo.getMayaType() == 'nurbsSurface':
                mMesh = RIGCREATE.get_meshFromNurbs(mGeo,
                                                    mode = 'general',
                                                    uNumber = mBlock.loftSplit, vNumber=mBlock.loftSides)
            else:
                mMesh = mGeo.doDuplicate(po=False)
                #mMesh.p_parent = False
                #mDup = mBlock.proxyHelper.doDuplicate(po=False)
            ml_proxy.append(mMesh)
    else:
        log.debug("|{0}| >> no ml_geo".format(_str_func))                                
        
    for i,mMesh in enumerate(ml_proxy):
        log.debug("|{0}| >> proxyMesh: {1}".format(_str_func,mMesh))                                
        mMesh.p_parent = ml_rigJoints[0]
        mMesh.rename("{0}_{1}_mesh".format(mBlock.p_nameBase,i))
    #mDup.inheritsTransform = True
    
    
    #Connect to setup ------------------------------------------------------------------------------------
    _side = BLOCKUTILS.get_side(self)
    
    if puppetMeshMode:
        log.debug("|{0}| >> puppetMesh setup... ".format(_str_func))
        ml_moduleJoints = mRigNull.msgList_get('moduleJoints')
    
        for i,mGeo in enumerate(ml_proxy):
            log.debug("|{0}| >> geo: {1}...".format(_str_func,mGeo))
            CORERIG.color_mesh(mGeo.mNode,'puppetmesh')
            
            mc.makeIdentity(mGeo.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)
            
            mGeo.p_parent = ml_moduleJoints[0]

        mRigNull.msgList_connect('puppetProxyMesh', ml_proxy)
        return ml_proxy    
    
    
    for mProxy in ml_proxy:
        CORERIG.colorControl(mProxy.mNode,_side,'main',transparent=False,proxy=True)
        mc.makeIdentity(mProxy.mNode, apply = True, t=1, r=1,s=1,n=0,pn=1)
        
        

        #Vis connect -----------------------------------------------------------------------
        mProxy.overrideEnabled = 1
        ATTR.connect("{0}.proxyVis_out".format(mRigNull.mNode),"{0}.visibility".format(mProxy.mNode) )
        ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayType".format(mProxy.mNode) )        
        for mShape in mProxy.getShapes(asMeta=1):
            str_shape = mShape.mNode
            mShape.overrideEnabled = 0
            ATTR.connect("{0}.proxyLock".format(mPuppetSettings.mNode),"{0}.overrideDisplayTypes".format(str_shape) )
        
    mRigNull.msgList_connect('proxyMesh', ml_proxy)







 








