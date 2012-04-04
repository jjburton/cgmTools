
from zooPy.vectors import *
from zooPy.path import Path
from zooPy import names

import time
import datetime


TOOL_NAME = 'weightSaver'
TOOL_VERSION = 2
DEFAULT_PATH = Path('%TEMP%/temp_skin.weights')
TOL = 0.25
EXTENSION = 'weights'

_MAX_RECURSE = 35


class SkinWeightException(Exception): pass
class NoVertFound(Exception): pass


class VertSkinWeight(Vector):
	'''
	extends Vector to store a vert's joint list, weightlist and id
	'''

	#can be used to store a dictionary so mesh names can be substituted at restore time when restoring by id
	MESH_NAME_REMAP_DICT = None

	#can be used to store a dictionary so joint names can be substituted at restore time
	JOINT_NAME_REMAP_DICT = None

	def __str__( self ):
		return '<%0.3f, %0.3f, %0.3f> %s' % (self[ 0 ], self[ 1 ], self[ 2 ], ', '.join( '%s: %0.2f' % d for d in zip( self.joints, self.weights ) ))
	__repr__ = __str__
	def populate( self, meshName, vertIdx, jointList, weightList ):
		self.idx = vertIdx
		self.weights = tuple( weightList )  #convert to tuple to protect it from changing accidentally...

		self.__mesh = meshName
		self.__joints = tuple( jointList )
	@property
	def mesh( self ):
		'''
		If a MESH_NAME_REMAP Mapping object is present, the mesh name is re-mapped accordingly,
		otherwise the stored mesh name is returned.
		'''
		if self.MESH_NAME_REMAP_DICT is None:
			return self.__mesh

		return self.MESH_NAME_REMAP_DICT.get( self.__mesh, self.__mesh )
	@property
	def joints( self ):
		'''
		Returns the list of joints the vert is skinned to.  If a JOINT_NAME_REMAP Mapping object is
		present, names are re-mapped accordingly.
		'''
		jointRemap = self.JOINT_NAME_REMAP_DICT
		if jointRemap is None:
			return self.__joints

		joints = [ jointRemap.get( j, j ) for j in self.__joints ]

		if len( joints ) != set( joints ):
			joints, self.weights = regatherWeights( joints, self.weights )

		return joints
	def getVertName( self ):
		return '%s.%d' % (self.mesh, self.idx)


class MayaVertSkinWeight(VertSkinWeight):
	'''
	NOTE: this class needs to be defined in this file otherwise weight files saved from maya will be
	unavailable to external tools like modelpipeline because the maya scripts are invisible outside
	of maya.  When unpickling objects - python needs to know what module to find the object's class
	in, so if that module is unavailable, a pickleException is raised when loading the file.
	'''
	def getVertName( self ):
		return '%s.vtx[%d]' % (self.mesh, self.idx)


class WeightSaveData(tuple):
	def __init__( self, data ):
		self.miscData, self.joints, self.jointHierarchies, self.weightData = data
	def getUsedJoints( self ):
		allJoints = set()
		for jData in self.weightData:
			allJoints |= set( jData.joints )

		return allJoints
	def getUsedMeshes( self ):
		allMeshes = set()
		for d in self.weightData:
			allMeshes.add( d.mesh )

		return allMeshes


def getUsedJoints( filepath ):
	return WeightSaveData( filepath.unpickle() ).getUsedJoints()


def regatherWeights( actualJointNames, weightList ):
	'''
	re-gathers weights.  when joints are re-mapped (when the original joint can't be found) there is
	the potential for joints to be present multiple times in the jointList - in this case, weights
	need to be summed for the duplicate joints otherwise maya doesn't weight the vert properly (dupes
	just get ignored)
	'''
	new = {}
	[ new.setdefault(j, 0) for j in actualJointNames ]
	for j, w in zip( actualJointNames, weightList ):
		new[ j ] += w

	return new.keys(), new.values()


#end
