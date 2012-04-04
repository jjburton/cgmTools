
import sys
import skeletonBuilder
import baseRigPrimitive

from zooPy.path import Path
from skeletonBuilder import *
from baseRigPrimitive import *

RIG_PART_SCRIPT_PREFIX = 'rigPrim_'


### !!! DO NOT IMPORT RIG SCRIPTS BELOW THIS LINE !!! ###

def _iterRigPartScripts():
	for f in Path( __file__ ).up().files():
		if f.hasExtension( 'py' ):
			if f.name().startswith( RIG_PART_SCRIPT_PREFIX ):
				yield f

def _importRigPrimitiveScripts():
	for f in _iterRigPartScripts():
		__import__( f.name(), globals() )

_importRigPrimitiveScripts()

def _setupSkeletonPartRigMethods():
	'''
	sets up the rig method associations on the skeleton parts.  This is a list on each skeleton part containing
	the rigging methods that are compatible with that skeleton part
	'''

	_rigMethodDict = {}
	for cls in RigPart.GetSubclasses():
		try:
			assoc = cls.SKELETON_PRIM_ASSOC
		except AttributeError: continue

		if assoc is None:
			continue

		for partCls in assoc:
			if partCls is None:
				continue

			try:
				_rigMethodDict[ partCls ].append( (cls.PRIORITY, cls) )
			except KeyError:
				_rigMethodDict[ partCls ] = [ (cls.PRIORITY, cls) ]

	for partCls, rigTypes in _rigMethodDict.iteritems():
		rigTypes.sort()
		rigTypes = [ rigType for priority, rigType in rigTypes ]
		partCls.RigTypes = rigTypes

_setupSkeletonPartRigMethods()


#end
