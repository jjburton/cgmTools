"""
------------------------------------------
Builder: cgm.core.mrs.helpers
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : http://www.cgmonastery.com
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

from cgm.core.mrs.lib import rigFrame_utils as RIGFRAME
import cgm.core.lib.string_utils as CORESTRINGS

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


def buildFrame_helpers(self,parent,changeCommand = ''):
    
    try:self.var_rayCastMode
    except:self.create_guiOptionVar('rayCastMode',defaultValue = 0)
    
    try:self.var_rayCastOffsetMode
    except:self.create_guiOptionVar('rayCastOffsetMode',defaultValue = 0)
    
    try:self.var_rayCastOffsetDist
    except:self.create_guiOptionVar('rayCastOffsetDist',defaultValue = 1.0)
        

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
    except:self.create_guiOptionVar('helperCreateMode',defaultValue = 0)
    
    uiRC = mUI.MelRadioCollection()
    _on = self.var_helperCreateMode.value

    _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row1,w=5)

    mUI.MelLabel(_row1,l='Create Mode')
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = self.var_helperCreateMode.value

    for i,item in enumerate(['simple','raycast']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_helperCreateMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)
        
    
    self.uiIF_helperCount = mUI.MelIntField(_row1, min = 1)
    
    mUI.MelButton(_row1, label='Create', ut='cgmUITemplate')
    
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

    