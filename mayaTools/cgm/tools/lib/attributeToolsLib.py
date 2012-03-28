#=================================================================================================================================================
#=================================================================================================================================================
#	attributeToolsLib - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#   Library of functions for the attributeTool
#
# REQUIRES:
#   Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
#=================================================================================================================================================
__version__ = '0.1.03282012'

import maya.cmds as mc
import maya.mel as mel

from cgm.lib.cgmBaseMelUI import *

from cgm.lib import *
from cgm.lib import (guiFactory,
                     dictionary,
                     attributes,
                     autoname,
                     search)
reload(attributes)
reload(search)
reload(dictionary)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# UI Stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def uiLoadSourceObject(self):
    selected = []
    bufferList = []
    selected = (mc.ls (sl=True,flatten=True,shortNames=True))

    if selected:
	if len(selected) >= 2:
	    guiFactory.warning('Only one object can be loaded')
	else:
	    # Put the object in the field
	    guiFactory.doLoadSingleObjectToTextField(self.SourceObjectField,'cgmVarAttributeSourceObject')
	    # Get our attr menu
	    uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu)


    else:
	#clear the field
	guiFactory.doLoadSingleObjectToTextField(self.SourceObjectField,'cgmVarAttributeSourceObject')
	uiUpdateObjectAttrMenu(self,self.ObjectAttributesOptionMenu)
	"""
		# update the fields
		for key in fieldToKeyDict.keys():
			mc.textField(fieldToKeyDict.get(key),edit=True,enable=False,
		                 text = '',
			             bgc = dictionary.returnStateColor('normal'))
		"""


 

def uiUpdateObjectAttrMenu(self,menu):
    def uiAttrUpdate(item):
	attrType = mc.getAttr((sourceObject + '.'+item),type=True)
	print item
	guiFactory.warning ("'%s' is of the type: '%s'"%(item,attrType)  ) 

	
    sourceObject =  mc.optionVar( q = 'cgmVarAttributeSourceObject')
    menu(edit=True,cc = uiAttrUpdate)
    
    if mc.objExists(sourceObject):
	# Get the attributes list
	menu.clear()
	attrs = mc.listAttr(sourceObject,keyable=True)
	userAttrs = mc.listAttr(sourceObject,userDefined = True)
	lockedAttrs = mc.listAttr(sourceObject,locked = True)
	if userAttrs:
	    attrs.extend( userAttrs )

	if lockedAttrs:
	    attrs.extend( lockedAttrs )

	attrs = lists.returnListNoDuplicates(attrs)
	attrs.sort()
	if attrs:
	    for a in attrs:
		menu.append(a)
	else:
	    menu.clear()
    else:
	menu.clear()