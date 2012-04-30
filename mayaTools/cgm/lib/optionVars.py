#=================================================================================================================================================
#=================================================================================================================================================
#	optionVars - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Tools for optionVars
#
# ARGUMENTS:
# 	Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2012 CG Monks - All Rights Reserved.
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel


def purgeOptionVar(varName):
    if mc.optionVar(exists = varName):    
        mc.optionVar( remove=varName )
        print "'%s' removed"%varName
        return True
    return False


def purgeCGM():
    optionVars = mc.optionVar(list=True)
    retList = []
    for var in optionVars:
        if 'cgm' in var:
            if purgeOptionVar(var):
                retList.append(var)
                
    if retList:
        return retList
    return False
    
