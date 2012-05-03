#=================================================================================================================================================
#=================================================================================================================================================
#	tdToolsLib - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Library of functions for the cgmRiggingTools tool
#
# ARGUMENTS:
#   Maya
#
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1.12072011 - First version
#	0.1.12132011 - master control maker implemented, snap move tools added
#	0.1.12272011 - split out library from tool
#
#=================================================================================================================================================
__version__ = '0.1.12032011'

import maya.cmds as mc
import maya.mel as mel
import subprocess

from cgm.lib.cgmBaseMelUI import *
from cgm.lib.ml import (ml_breakdownDragger,
                        ml_resetChannels,
                        ml_deleteKey,
                        ml_setKey,
                        ml_hold,
                        ml_arcTracer,
                        ml_convertRotationOrder,
                        ml_copyAnim)

reload(ml_arcTracer)
"""

"""
def ml_breakdownDraggerCall():
    ml_breakdownDragger.drag()
    
def ml_resetChannelsCall():
    ml_resetChannels.resetChannels()

def ml_deleteKeyCall():
    ml_deleteKey.ui()
    
def ml_setKeyCall():
    ml_setKey.ui()
    
def ml_holdCall():
    ml_hold.ui()
    
def ml_arcTracerCall():
    ml_arcTracer.ui()
    
def ml_copyAnimCall():
    ml_copyAnim.ui()

def ml_convertRotationOrderCall():
    ml_convertRotationOrder.ui()