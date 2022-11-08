"""
------------------------------------------
Builder: cgm.core.mrs.helpers
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'HELPERS'

import random
import re
import copy
import time
import pprint
import os
import subprocess, os
import sys

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim
import Red9.core.Red9_CoreUtils as r9Core

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc


# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.lib.transform_utils as TRANS

from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as RIGMETA
from cgm.core import cgm_PuppetMeta as PUPPETMETA
from cgm.core.classes import GuiFactory as CGMUI
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import NodeFactory as NODEFAC
from cgm.core.cgmPy import path_Utils as PATH
from cgm.core.mrs import RigBlocks as RIGBLOCKS
from cgm.core.lib import shared_data as SHARED
from cgm.core.mrs.lib import builder_utils as BUILDERUTILS
from cgm.core.mrs.lib import block_utils as BLOCKUTILS
from cgm.core.mrs.lib import blockShapes_utils as BLOCKSHAPES
from cgm.core.mrs.lib import ModuleControlFactory as MODULECONTROLFACTORY
from cgm.core.mrs.lib import ModuleShapeCaster as MODULESHAPECASTER
from cgm.core.rig import ik_utils as IK
import cgm.core.tools.lib.snap_calls as SNAPCALLS
import cgm.core.classes.DraggerContextFactory as dragFactory
from cgm.core.mrs.lib import rigFrame_utils as RIGFRAME
import cgm.core.lib.string_utils as CORESTRINGS
import cgm.core.classes.DraggerContextFactory as DRAGGER

from cgm.core.mrs.lib import general_utils as BLOCKGEN
import cgm.core.tools.lib.tool_chunks as UICHUNKS
import cgm.core.tools.toolbox as TOOLBOX
import cgm.core.mrs.lib.shared_dat as BLOCKSHARE
import cgm.core.tools.markingMenus.lib.contextual_utils as CONTEXT
import cgm.core.tools.snapTools as SNAPTOOLS
import cgm.core.lib.list_utils as LISTS
from cgm.core.lib import nameTools as NAMETOOLS
import cgm.core.mrs.lib.rigShapes_utils as RIGSHAPES
import cgm.core.mrs.lib.post_utils as MRSPOST


# Factory 
#=====================================================================================================
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

d_state_colors = {'define':[1,.3,.3],
                  'form':[1,.5,0],
                  'prerig':[1,.9,0],
                  'skeleton':[0,.7,.7],
                  'rig':[.310,1,0],
                  'default':[.3,.2,.5],
                  }

d_uiStateSubColors = {}
for k,color in d_state_colors.iteritems():
    d_uiStateSubColors[k] = [v *.95 for v in color ]
    
#Generate our ui colors
d_uiStateUIColors = {}

for k,color in d_state_colors.iteritems():
    _d = {}
    d_uiStateUIColors[k] = _d
    _d['base'] = [v *.95 for v in color ]
    _d['light'] = [ MATH.Clamp(v*2.0,None,1.0) for v in color ]
    _d['bgc'] = [ v * .8 for v in _d['base'] ]
    _d['button'] = [v *.6 for v in _d['bgc'] ]

#>>> Root settings =============================================================
__version__ =  cgmGEN.__RELEASESTRING
_sidePadding = 25

        
def uiFunc_helper_initialize(self):
    _str_func = 'uiFunc_helper_initialize[{0}]'.format(self.__class__.TOOLNAME)
    log.info("|{0}| >>...".format(_str_func))
    
    
    if self.ml_helpers:
        #print.pprint(self.ml_helpers)
        self.mButton_helpersBuild(edit=True, en=True)
        for mObj in self.ml_helpers:
            try:mObj.delete()
            except:
                try:mc.delete(mObj)
                except:
                    pass
                
    d_make = {'count':self.uiIF_helperCount.getValue(),
              'mode':self.var_helperCreateMode.getValue(),
              'baseSize' : [self.uifloat_baseSizeX.getValue() or 1,
                        self.uifloat_baseSizeY.getValue() or 1,
                        self.uifloat_baseSizeZ.getValue() or 1],              
              }
    #d_make = {}
    pprint.pprint(d_make)
    log.info( createBlockHelper(self, **d_make) )
    

def uiFunc_helper_build(self):
    _str_func = 'uiFunc_helper_build[{0}]'.format(self.__class__.TOOLNAME)
    log.info("|{0}| >>...".format(_str_func))
    
    def returnFail():
        return log.error("No helpers found. Reinitialize.")
    
    if not self.ml_helpers:
        return returnFail()
    
    ml_helpers = []
    for mObj in self.ml_helpers:
        if mObj.mNode:
            mObj.mNode
            ml_helpers.append(mObj)
        else:
            return returnFail()

    self.uiFunc_create(count = len(ml_helpers))
    
    if len(self.ml_blocksMade) != len(ml_helpers):
        return log.error("Didn't make enough blocks")
    
    pprint.pprint(ml_helpers)
    
    for i,mObj in enumerate(ml_helpers):
        mBlock = self.ml_blocksMade[i]
        reload(SNAPCALLS)
        
        
        _shapeDirection = self.d_blockCreate.get('shapeDirection','y+')
        #print (_shapeDirection)
        
        if _shapeDirection.count('+'):
            _shapeDirection= _shapeDirection.replace('+','-')
        else:
            _shapeDirection= _shapeDirection.replace('-','+')
                
        #print (_shapeDirection)
        
        if mBlock.blockType == 'head':
            mBlock.p_position = mObj.p_position
        else:
            SNAPCALLS.snap(mBlock.mNode, mObj.mNode, objPivot='rp', targetPivot='castNear',targetMode= _shapeDirection)
        
        
    
    
        
class HelperDag(object):
    def __init__(self,mUI = None):
        if not mc.objExists('mrsHelpers'):
            mDag = cgmMeta.cgmObject(name='mrsHelpers')
        else:
            mDag = cgmMeta.cgmObject('mrsHelpers')
        mDag.dagLock()
        
        self.mUI = mUI
        self.mDag = mDag
        
        mDag.addAttr('helpers', initialValue=[], attrType='message')
        self.ml_helpers = mDag.getMessageAsMeta('helpers')
        
    def dat_get(self):
        _str_func = 'dat_get[{0}]'.format(self.__class__)                    
        if not self.mUI:
            return ( log.error("No UI on HelperDag"))
        
        log.info("|{0}| >>...".format(_str_func))
        
            
    

    
    
def buildFrame_helpers(self,parent,changeCommand = ''):
    """
    try:self.var_rayCastMode
    except:self.create_guiOptionVar('rayCastMode',defaultValue = 0)
    
    try:self.var_rayCastOffsetMode
    except:self.create_guiOptionVar('rayCastOffsetMode',defaultValue = 0)
    
    try:self.var_rayCastOffsetDist
    except:self.create_guiOptionVar('rayCastOffsetDist',defaultValue = 1.0)"""
    self.ml_helpers = []
    
    self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
    self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
    self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
    #self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)    
    
    try:self.var_helpersFrameCollapse
    except:self.create_guiOptionVar('helpersFrameCollapse',defaultValue = 0)
    
    mVar_frame = self.var_helpersFrameCollapse
    
    _frame = mUI.MelFrameLayout(parent,label = 'Helpers',vis=True,
                                collapse=mVar_frame.value,
                                collapsable=True,
                                enable=True,
                                useTemplate = 'cgmUIHeaderTemplate',
                                expandCommand = lambda:mVar_frame.setValue(0),
                                collapseCommand = lambda:mVar_frame.setValue(1)
                                )	
    
    _inside = mUI.MelColumnLayout(_frame,useTemplate = 'cgmUISubTemplate') 
    
    #Create Mode =========================================================================
    
    try:self.var_helperCreateMode
    except:self.create_guiOptionVar('helperCreateMode',defaultValue = 'simple')
    
    uiRC = mUI.MelRadioCollection()
    _on = self.var_helperCreateMode.value

    _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row1,w=5)

    mUI.MelLabel(_row1,l='Create Mode')
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = self.var_helperCreateMode.value

    for i,item in enumerate(['simple','raycast']):
        if item == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_helperCreateMode.setValue,item))

        mUI.MelSpacer(_row1,w=2)
        
    mUI.MelLabel(_row1, label = 'Count')
    self.uiIF_helperCount = mUI.MelIntField(_row1, min = 1)

    mUI.MelLabel(_row1, label = ' || ')
    
    self.mButton_helpersInitialize = mUI.MelButton(_row1, label='Initialize', ut='cgmUITemplate',
                                                   c = lambda *a:uiFunc_helper_initialize(self))
    self.mButton_helpersBuild = mUI.MelButton(_row1, label='Build', ut='cgmUITemplate', en=True,
                                              c = lambda *a:uiFunc_helper_build(self))
    
    mUI.MelSpacer(_row1,w=2)    

    _row1.layout()     
    
    #Raycast =============================================================================
    mc.setParent(_inside)
    CGMUI.add_Header('Raycast')
    
    #>>>Cast Mode  -------------------------------------------------------------------------------------
    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastMode.value

    _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row1,w=5)

    mUI.MelLabel(_row1,l='Cast')
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastMode.value

    for i,item in enumerate(['close','mid','far','all','x','y','z']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_rayCastMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)    

    _row1.layout() 

    #>>>offset Mode  -------------------------------------------------------------------------------------
    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastOffsetMode.value        

    _row_offset = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_offset,w=5)                              
    mUI.MelLabel(_row_offset,l='Offset')
    _row_offset.setStretchWidget( mUI.MelSeparator(_row_offset) )  

    for i,item in enumerate(['None','Distance','snapCast']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row_offset,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_rayCastOffsetMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)   

    cgmUI.add_Button(_row_offset,'Set Offset',
                     lambda *a:self.var_rayCastOffsetDist.uiPrompt_value('Set offset distance'),
                     'Set the the rayCast offset distance by ui prompt') 
    mUI.MelSpacer(_row_offset,w=5)                              
    
    _row_offset.layout()

    
def createBlockHelper(self = None, count= 1, mode = 'simple', baseSize = [1,1,1], name = 'block'):
    _str_func = 'uiFunc_createHelper'
    log.info("|{}| >>... {} | {} | {}".format(_str_func, count, mode,baseSize))
    
    self.ml_helpers = []
    
    if mode == 'simple':
        for i in range(count):
            #mSphere = cgmMeta.asMeta(mc.polySphere(radius=1, name='block_{}_helper'.format(i), ch=False)[0])
            #mHelper = cgmMeta.asMeta(mc.polyCube(depth=baseSize[0], height=baseSize[1], width=baseSize[2], name='block_{}_helper'.format(i), ch=False)[0])
            mHelper = cgmMeta.asMeta(mc.polyCube(depth=1, height=1, width=1, name='block_{}_helper'.format(i), ch=False)[0])
            
            mHelper.scale = baseSize
            
            self.ml_helpers.append(mHelper)

    elif mode == 'raycast':
        #reload(SNAPCALLS)
        #mHelper = cgmMeta.asMeta(mc.polySphere(radius=1, name='ref_helper', ch=False)[0])
        #mHelper.select()
        mCaster = helpers_raycast(self, None,'duplicate',False,toCreate = ['{}_{}_helper'.format(name, i) for i in range(count)])
        #mHelper.delete()
        #pprint.pprint(mCaster.l_created)
        #self._l_toDuplicate
        
        """
        return helperRayCaster(mode = 'midPoint',
                               mesh = geo,
                               create = 'locator',
                               toCreate = ['block_{}_helper'.format(i) for i in range(count)])"""          
        
        
    print (self.ml_helpers)
    print self.mDag
    if self.ml_helpers:
        self.mButton_helpersBuild(edit=True, en=True)
        self.mDag.helpers = self.ml_helpers
        

    
def helpers_raycast(self = None, targets = [], create = None, drag = False, snap=True, aim=False, toCreate=[], kwsOnly = False):
    '''
    self = data storage
    '''
    reload(dragFactory)
    class helperRayCaster(dragFactory.clickMesh):
        """Sublass to get the functs we need in there"""
        def __init__(self,mStorage = None,**kws):
            if kws:log.info("kws: %s"%str(kws))

            super(helperRayCaster, self).__init__(**kws)
            self.mStorage = mStorage
            log.info("Please place '%s'"%self.l_toCreate[0])
        
        def press_pre_insert(self):
            mSphere = cgmMeta.asMeta(mc.polySphere(radius=1, name='ref_helper', ch=False)[0])
            mSphere.p_position = 10000,10000,10000
            self._l_toDuplicate = [mSphere.mNode]
            pprint.pprint(self.l_mesh)
            
        def press_post_insert(self):
            log.info('here')
            if self.mode != 'midPoint':
                return
            try:_obj = self._createModeBuffer[-1]
            except:
                return
            
            try:
                _x = RAYS.get_dist_from_cast_axis(_obj,'x')
                _z = RAYS.get_dist_from_cast_axis(_obj,'z')
                _y = MATH.average(_x,_z)
                _box = [_x,_y,_z]
                TRANS.scale_to_boundingBox( _obj, _box)
            except:
                pass
            
        
        def release(self):
            if len(self.l_return)< len(self.l_toCreate)-1:#If we have a prompt left
                log.info("Please place '%s'"%self.l_toCreate[len(self.l_return)+1])            
            dragFactory.clickMesh.release(self)
            mc.delete(self._l_toDuplicate)


        def finalize(self):
            log.info("returnList: %s"% self.l_return)
            log.info("createdList: %s"% self.l_created)  
            self.mStorage.ml_helpers = cgmMeta.asMeta( self.l_created )
            
            buffer = [] #self.mStorage.templateNull.templateStarterData
            log.info("starting data: %s"% buffer)

            #Make sure we have enough points
            #==============  
            '''
            handles = self.mStorage.templateNull.handles
            if len(self.l_return) < handles:
                log.warning("Creating curve to get enough points")                
                curve = CURVES.curveFromPosList(self.l_return)
                mc.rebuildCurve (curve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0,s=(handles-1), d=1, tol=0.001)
                self.l_return = curves.returnCVsPosList(curve)#Get the pos of the cv's
                mc.delete(curve)'''

            #Store info
            #==============
            '''
            for i,p in enumerate(self.l_return):
                buffer.append(p)#need to ensure it's storing properly
                #log.info('[%s,%s]'%(buffer[i],p))'''

            #Store locs
            #==============  
            '''
            log.info("finish data: %s"% buffer)
            self.mStorage.templateNull.__setattr__('templateStarterData',buffer,lock=True)
            #self.mStorage.templateNull.templateStarterData = buffer#store it
            log.info("'%s' sized!"%self._str_moduleName)'''
            dragFactory.clickMesh.finalize(self)
                        
            

    _str_func = 'helpers_raycast'
    _toSnap = False
    _toAim = False
    if not targets:
        targets = mc.ls(sl=True)
        
    if snap:
        if not create or create == 'duplicate':
            #targets = mc.ls(sl=True)#...to use g to do again?...    
            _toSnap = targets

            log.debug("|{0}| | targets: {1}".format(_str_func,_toSnap))
            if not _toSnap:
                #if create == 'duplicate':
                #    log.error("|{0}| >> Must have targets to duplicate!".format(_str_func))
                #return
                pass
    
    if aim:
        _toAim = targets

    var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
    var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
    var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0)
    var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])
    var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0) 
    var_objDefaultAimAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultAimAxis', defaultValue = 2)
    var_objDefaultUpAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultUpAxis', defaultValue = 1)      
    var_objDefaultOutAxis = cgmMeta.cgmOptionVar('cgmVar_objDefaultOutAxis', defaultValue = 0)      
    var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)
    var_aimMode = cgmMeta.cgmOptionVar('cgmVar_aimMode',defaultValue='world')
    
    _rayCastMode = var_rayCastMode.value
    _rayCastOffsetMode = var_rayCastOffsetMode.value
    _rayCastTargetsBuffer = var_rayCastTargetsBuffer.value
    _rayCastOrientMode = var_rayCastOrientMode.value
    _objDefaultAimAxis = var_objDefaultAimAxis.value
    _objDefaultUpAxis = var_objDefaultUpAxis.value
    _objDefaultOutAxis = var_objDefaultOutAxis.value
    _rayCastDragInterval = var_rayCastDragInterval.value
    
    log.debug("|{0}| >> Mode: {1}".format(_str_func,_rayCastMode))
    log.debug("|{0}| >> offsetMode: {1}".format(_str_func,_rayCastOffsetMode))
    
    kws = {'mode':'surface', 'mesh':None,'closestOnly':True, 'create':'locator','dragStore':False,'orientMode':None,
           'objAimAxis':SHARED._l_axis_by_string[_objDefaultAimAxis], 'objUpAxis':SHARED._l_axis_by_string[_objDefaultUpAxis],'objOutAxis':SHARED._l_axis_by_string[_objDefaultOutAxis],
           'aimMode':var_aimMode.value,'mStorage':self,
           'timeDelay':.1, 'offsetMode':None, 'dragInterval':_rayCastDragInterval, 'offsetDistance':var_rayCastOffsetDist.value}#var_rayCastOffsetDist.value
    
    if _rayCastTargetsBuffer:
        log.warning("|{0}| >> Casting at buffer {1}".format(_str_func,_rayCastMode))
        kws['mesh'] = _rayCastTargetsBuffer
        
    if _toSnap:
        kws['toSnap'] = _toSnap
    elif create:
        kws['create'] = create

    if _toAim:
        kws['toAim'] = _toAim
        
    if _rayCastOrientMode == 1:
        kws['orientMode'] = 'normal'
    
    if toCreate:
        kws['toCreate'] = toCreate
        
    if create == 'duplicate':
        kws['toDuplicate'] = _toSnap        
        if _toSnap:
            kws['toSnap'] = False
        #else:
        #    log.error("|{0}| >> Must have target with duplicate mode!".format(_str_func))
        #    cgmGEN.log_info_dict(kws,"RayCast args")        
        #    return
        
    if drag:
        kws['dragStore'] = drag
    
    if _rayCastMode == 1:
        kws['mode'] = 'midPoint'
    elif _rayCastMode == 2:
        kws['mode'] = 'far'
    elif _rayCastMode == 3:
        kws['mode'] = 'surface'
        kws['closestOnly'] = False
    elif _rayCastMode == 4:
        kws['mode'] = 'planeX'
    elif _rayCastMode == 5:
        kws['mode'] = 'planeY'   
    elif _rayCastMode == 6:
        kws['mode'] = 'planeZ'        
    elif _rayCastMode != 0:
        log.warning("|{0}| >> Unknown rayCast mode: {1}!".format(_str_func,_rayCastMode))
        
    if _rayCastOffsetMode == 1:
        kws['offsetMode'] = 'distance'
    elif _rayCastOffsetMode == 2:
        kws['offsetMode'] = 'snapCast'
    elif _rayCastOffsetMode != 0:
        log.warning("|{0}| >> Unknown rayCast offset mode: {1}!".format(_str_func,_rayCastOffsetMode))
    cgmGEN.log_info_dict(kws,"RayCast args")
    
    #pprint.pprint(kws)
    if kwsOnly:
        return kws
    return helperRayCaster(**kws)
    #return DRAGGER.clickMesh(**kws)