"""
------------------------------------------
toolbox: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__version__ = '0.1.08172017'

import webbrowser

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc
import maya
import maya.mel as mel

from cgm.core import cgm_General as cgmGen
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
reload(MMCONTEXT)
from cgm.core.lib import shared_data as SHARED
from cgm.core.tools import locinator as LOCINATOR
import cgm.core.lib.locator_utils as LOC
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.tools.lib.snap_calls as SNAPCALLS
from cgm.core.tools import meshTools as MESHTOOLS
import cgm.core.lib.distance_utils as DIST
from cgm.core.lib import node_utils as NODES
from cgm.core.tools import attrTools as ATTRTOOLS
from cgm.core.tools import dynParentTool as DYNPARENTTOOL
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.rig.joint_utils as JOINTS
import cgm.core.tools.locinator as LOCINATOR
import cgm.core.lib.arrange_utils as ARRANGE
import cgm.core.lib.rigging_utils as RIGGING
import cgm.core.classes.GuiFactory as cgmUI
import cgm.core.tools.lib.annotations as TOOLANNO
import cgm.core.lib.transform_utils as TRANS
import cgm.core.tools.transformTools as TT
reload(MESHTOOLS)
reload(TT)
reload(TOOLANNO)
reload(cgmUI)
reload(SNAPCALLS)
mUI = cgmUI.mUI

_2016 = False
if cgmGen.__mayaVersion__ >=2016:
    _2016 = True

def uiFunc_createOneOfEach():
    var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)        
    CURVES.create_oneOfEach(var_createSizeValue.value)

def uiFunc_createCurve():
    reload(CURVES)
    var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
    var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
    var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
    var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
    var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
    var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25)        
    CURVES.create_controlCurve(mc.ls(sl=True),
                               var_curveCreateType.value,
                               var_defaultCreateColor.value,
                               var_createSizeMode.value,
                               var_createSizeValue.value,
                               var_createSizeMulti.value,
                               SHARED._l_axis_by_string[var_createAimAxis.value])
def uiSetupOptionVars_curveCreation(self):
    self.var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
    self.var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
    self.var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
    self.var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
    self.var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
    self.var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25) 
    

def uiFunc_distanceMeastureToField(self):
    _res = DIST.get_distance_between_targets()
    if not _res:
        raise ValueError,"Found no distance data."
    
    self.uiFF_distance.setValue(_res)
    
def uiFunc_vectorMeasureToField(self):
    _res = DIST.get_vector_between_targets()
    
    if not _res:
        raise ValueError,"Found no vector data."
    
    self.uiFF_vecX.setValue(_res[0][0])
    self.uiFF_vecY.setValue(_res[0][1])
    self.uiFF_vecZ.setValue(_res[0][2])
    

#>>

def buildRow_parent(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Parent:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )      

    mc.button(parent=_row,
              l='Ordered',
              ut = 'cgmUITemplate',
              ann = "Parent in selection order",    
              c = lambda *a:TRANS.parent_orderedTargets())                                             

    mc.button(parent=_row,
              l='Reverse Ordered',
              ut = 'cgmUITemplate',
              ann = "Parent in reverse selection order",                                                                                                                       
              c = lambda *a:TRANS.parent_orderedTargets(reverse=True))                                             

    _row.layout()   
    

def buildColumn_transform(self,parent):
    _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    
    
    
    
    
    
    
    