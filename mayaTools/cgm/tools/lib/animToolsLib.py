#=================================================================================================================================================
#=================================================================================================================================================
#	animToolsLib - a part of cgmToolbox
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Library of functions for the cgmAnimTools
#
# ARGUMENTS:
#   Maya
#
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Unless another author's tool, Copyright 2011 CG Monks - All Rights Reserved.
#
#
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel
import subprocess

from cgm.core.lib.zoo.baseMelUI import *
from cgm.lib.ml import (ml_breakdownDragger,
                        ml_resetChannels,
                        ml_deleteKey,
                        ml_setKey,
                        ml_hold,
                        ml_stopwatch,
                        ml_arcTracer,
                        ml_convertRotationOrder,
                        ml_copyAnim)

reload(ml_arcTracer)
reload(ml_resetChannels)
"""

"""
def ml_breakdownDraggerCall():
    ml_breakdownDragger.drag()
    
def ml_resetChannelsCall(transformsOnly = False):
    ml_resetChannels.main(transformsOnly = transformsOnly)
    
def ml_resetChannelsCallMod(transformsOnly = False):
    ml_resetChannels.resetChannelsMod(transformOnly)
    
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
    
def ml_stopwatchCall():
    ml_stopwatch.ui()