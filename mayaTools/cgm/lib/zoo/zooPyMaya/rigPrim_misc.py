
from baseRigPrimitive import *
from skeletonPart_arbitraryChain import ArbitraryChain


class ControlHierarchy(PrimaryRigPart):
	__version__ = 0

	#part doesn't have a CONTROL_NAMES list because parts are dynamic - use indices to refer to controls
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'ArbitraryChain' ), )

	def _build( self, part, controlShape=DEFAULT_SHAPE_DESC, spaceSwitchTranslation=False, parents=(), rigOrphans=False, **kw ):
		joints = list( part ) + (part.getOrphanJoints() if rigOrphans else [])
		return controlChain( self, joints, controlShape, spaceSwitchTranslation, parents, rigOrphans, **kw ), ()


class WeaponControlHierarchy(PrimaryRigPart):
	__version__ = 0
	SKELETON_PRIM_ASSOC = ( SkeletonPart.GetNamedSubclass( 'WeaponRoot' ), )

	def _build( self, part, controlShape=DEFAULT_SHAPE_DESC, spaceSwitchTranslation=True, parents=(), **kw ):
		return controlChain( self, part.selfAndOrphans(), controlShape, spaceSwitchTranslation, parents, True, **kw ), ()


def controlChain( rigPart, joints, controlShape=DEFAULT_SHAPE_DESC, spaceSwitchTranslation=False, parents=(), rigOrphans=False, **kw ):
	scale = kw[ 'scale' ]

	#discover parent nodes
	namespace = ''
	try:
		namespace = getNamespaceFromReferencing( joints[ 0 ] )
	except IndexError: pass

	parents = tuple( '%s%s' % (namespace, p) for p in parents )

	### DETERMINE THE PART'S PARENT CONTROL AND THE ROOT CONTROL ###
	parentControl, rootControl = getParentAndRootControl( joints[ 0 ] )

	ctrls = []
	prevParent = parentControl

	for item in joints:
		ctrl = buildControl( '%s_ctrl' % item, item, PivotModeDesc.BASE, controlShape, size=AUTO_SIZE )
		ctrlSpace = getNodeParent( ctrl )

		#do parenting
		parent( ctrlSpace, prevParent )

		#stuff objects into appropriate variables
		prevParent = ctrl
		ctrls.append( ctrl )

		#lock un-needed axes
		if not spaceSwitchTranslation:
			attrState( ctrl, 't', *LOCK_HIDE )

	#setup space switching
	buildKwargs = {} if spaceSwitchTranslation else spaceSwitching.NO_TRANSLATION
	for n, (ctrl, j) in enumerate( zip( ctrls, joints ) ):
		buildDefaultSpaceSwitching( j, ctrl, parents, reverseHierarchy=False, **buildKwargs )

	createLineOfActionMenu( joints, ctrls )

	return ctrls


#end
