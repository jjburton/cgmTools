
import apiExtensions

from maya.cmds import *
from zooPy.misc import removeDupes


def resetAttrs( obj, skipVisibility=True ):
	'''
	simply resets all keyable attributes on a given object to its default value
	great for running on a large selection such as all character controls...
	'''

	#obj = apiExtensions.asMObject( obj )
	attrs = listAttr( obj, k=True, s=True, m=True ) or []
	if skipVisibility:
		if 'visibility' in attrs:
			attrs.remove( 'visibility' )

	if not attrs:
		return

	selAttrs = channelBox( 'mainChannelBox', q=True, sma=True ) or channelBox( 'mainChannelBox', q=True, sha=True )

	for attr in attrs:

		#if there are selected attributes AND the current attribute isn't in the list of selected attributes, skip it...
		if selAttrs:
			attrShortName = attributeQuery( attr, n=obj, shortName=True )
			if attrShortName not in selAttrs:
				continue

		default = 0

		try:
			default = attributeQuery( attr, n=obj, listDefault=True )[ 0 ]
		except RuntimeError: pass

		attrpath = '%s.%s' % (obj, attr)
		if not getAttr( attrpath, settable=True ):
			continue

		#need to catch because maya will let the default value lie outside an attribute's
		#valid range (ie maya will let you creat an attrib with a default of 0, min 5, max 10)
		try:
			setAttr( attrpath, default )
		except RuntimeError: pass


def resetAttrsForSelection():
	for obj in ls( sl=True ) or []:
		resetAttrs( obj )


#end
