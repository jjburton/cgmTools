#=================================================================================================================================================
#=================================================================================================================================================
#	bufferToolsLib - a part of cgmTools
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
from cgm.lib.classes.BufferFactory import *
from cgm.lib.classes.OptionVarFactory import *
from cgm.lib.classes.ObjectFactory import *

from cgm.lib import (search,guiFactory)
reload(search)
reload(guiFactory)

"""

"""
def updateObjectBuffers(self):
    self.objectBuffers = search.returnObjectBuffers()

def selectBufferObjects(objectBufferName):
    tmp = BufferFactory(objectBufferName)
    tmp.select()

def addSelected(objectBufferName):
    tmp = BufferFactory(objectBufferName)
    tmp.doStoreSelected()

def removeSelected(objectBufferName):
    tmp = BufferFactory(objectBufferName)
    tmp.doRemoveSelected()

def keyBuffer(objectBufferName):
    tmp = BufferFactory(objectBufferName)
    tmp.key()  

def purgeBuffer(objectBufferName):
    tmp = BufferFactory(objectBufferName)
    tmp.purge()  

def setBufferAsActive(optionVar,bufferName):
    tmp = OptionVarFactory(optionVar,'string')
    if '' in tmp.value:
        tmp.remove('')
    tmp.append(bufferName) 

def setBufferAsInactive(optionVar,bufferName):
    tmp = OptionVarFactory(optionVar,'string')
    tmp.remove(bufferName) 

def createBuffer(self):
    b = BufferFactory('Buffer')
    b.doStoreSelected()
    self.reset()


def updateBufferName(self,bufferTextField,bufferName):
	newName = mc.textField(bufferTextField,q=True,text = True)
	
	assert mc.objExists(bufferName) is True,"'%s' doesn't exist.Try updating the tool."%bufferObject

	if bufferName and newName:
		b = ObjectFactory(bufferName)
		b.store('cgmName', newName)
		b.doName()
		mc.textField(bufferTextField,e = True,text = b.nameBase)
		#Reset
		guiFactory.resetGuiInstanceOptionVars(self.optionVars,bufferTools.run)

	else:
		guiFactory.warning("There's a problem with the name input.")


