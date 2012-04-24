#=================================================================================================================================================
#=================================================================================================================================================
#	objectFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for finding stuff
#
# REQUIRES:
# 	Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#   0.11 - 04/04/2011 - added cvListSimplifier
#
# FUNCTION KEY:
#   1) ????
#   2) ????
#   3) ????
#
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel
from cgm.lib.classes import NameFactory

from cgm.lib import (lists,
                     optionVars,
                     search,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)

optionVarTypeDict = {'int':['int','i','integer',1,0],
                     'float':['f','float','fl',1.0,0.0],
                     'string':['string','str','s']}

class OptionVarFactory():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Assertions to verify:
    1) An object knows what it is

    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    def __init__(self,varName,varType = 'int'):
        #Default to creation of a var as an int value of 0
        ### input check   
        self.name = ''
        self.form = ''
        self.value = ''
        
        self.check(varName,varType)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    def check(self,varName,varType):
        #If it doesn't exist, make it. If it does, fill out the data
        if not mc.optionVar(exists = varName):
            for option in optionVarTypeDict.keys():
                if varType in optionVarTypeDict.get(option):
                    self.name = varName
                    self.form = option
                    self.create(self.form)
                    self.value = mc.optionVar(q=self.name)
                    return
            if not self.form:
                return guiFactory.warning("'%s' is not a valid variable type"%varType)  
        
        else:
            self.name = varName
            self.value = mc.optionVar(q=varName)
            typeReturn = type(self.value)
            if typeReturn is list:
                if type(self.value[0]) is unicode:
                    self.form = 'string'
                else:
                    typeBuffer = str(type(self.value[0]))
            else:
                typeBuffer = str(typeReturn)
            
            self.getStringType(typeBuffer)


    def create(self,doType):
        print "making '%s'"%self.form
            
        if doType == 'int':
            mc.optionVar(iv=(self.name,0))
        elif doType == 'float':
            mc.optionVar(fv=(self.name,0))
        elif doType == 'string':
            mc.optionVar(sv=(self.name,''))
            

    def getStringType(self,typeBuffer):
        if typeBuffer is int:
            self.form = 'int'
        elif typeBuffer is float:
            self.form = 'float'
        elif typeBuffer is unicode:
            self.form = 'string'
        else:
            self.form = typeBuffer
  
    def purge(self):
        try:
            mc.optionVar(remove = self.name)
            self.name = ''
            self.form = ''
            self.value = ''
            
        except:
            guiFactory.warning("'%s' doesn't exist"%(self.name))
            
            
    def add(self,value):
        pass
        

    
