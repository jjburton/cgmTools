
import re

from zooPy.misc import removeDupes
from zooPy.names import camelCaseToNice

from triggered import Trigger
from control import getNiceName
from apiExtensions import asMObject, cleanShortName
from maya.cmds import *

import maya.cmds as cmd

import apiExtensions
import triggered
import rigUtils
import control

attrState = control.attrState
AXES = rigUtils.Axis.BASE_AXES


class ChangeSpaceCmd(unicode):
	'''
	contains a bunch of higher level tools to querying the space changing command string
	'''

	_THE_LINES = 'zooFlags;', 'zooUtils;', 'zooChangeSpace \"-attr parent %d\" %%%d;'

	@classmethod
	def Create( cls, parentIdx, parentConnectIdx ):
		return cls( '\n'.join( cls._THE_LINES ) % (parentIdx, parentConnectIdx) )
	@classmethod
	def IsChangeSpaceCmd( cls, theStr ):
		return '\nzooChangeSpace "' in theStr

	def getInterestingLine( self ):
		for line in self.split( '\n' ):
			if line.startswith( 'zooChangeSpace ' ):
				return line
	def getIndex( self ):
		interestingLine = self.getInterestingLine()
		indexStr = interestingLine.split( ' ' )[ -2 ].replace( '"', '' )

		return int( indexStr )
	def setIndex( self, index ):
		lines = self.split( '\n' )
		for n, line in enumerate( lines ):
			if line.startswith( 'zooChangeSpace ' ):
				toks = line.split( ' ' )
				toks[ -2 ] = '%d"' % index

				lines[ n ] = ' '.join( toks )

		return ChangeSpaceCmd( '\n'.join( lines ) )
	def getConnectToken( self ):
		interestingLine = self.getInterestingLine()
		lastToken = interestingLine.split( ' ' )[ -1 ].replace( ';', '' )

		return lastToken


def build( src, tgts, names=None, space=None, **kw ):
	'''
	'''
	if names is None:
		names = [ None for t in tgts ]

	conditions = []
	for tgt, name in zip( tgts, names ):
		cond = add( src, tgt, name, space, **kw )
		conditions.append( cond )

	return conditions


CONSTRAINT_TYPES = CONSTRAINT_PARENT, CONSTRAINT_POINT, CONSTRAINT_ORIENT = 'parentConstraint', 'pointConstraint', 'orientConstraint'
CONSTRAINT_CHANNELS = { CONSTRAINT_PARENT: (['t', 'r'], ['ct', 'cr']),
                        CONSTRAINT_POINT: (['t'], ['ct']),
                        CONSTRAINT_ORIENT: (['r'], ['cr']) }

NO_TRANSLATION = { 'skipTranslationAxes': ('x', 'y', 'z') }
NO_ROTATION = { 'skipRotationAxes': ('x', 'y', 'z') }

def add( src, tgt,
         name=None,
         space=None,
         maintainOffset=True,
         nodeWithParentAttr=None,
         skipTranslationAxes=(),
         skipRotationAxes=(),
         constraintType=CONSTRAINT_PARENT ):

	global AXES
	AXES = list( AXES )

	if space is None:
		space = listRelatives( src, p=True, pa=True )[ 0 ]

	if nodeWithParentAttr is None:
		nodeWithParentAttr = src

	if not name:
		name = getNiceName( tgt )
		if name is None:
			name = camelCaseToNice( str( tgt ) )


	#if there is an existing constraint, check to see if the target already exists in its target list - if it does, return the condition used it uses
	attrState( space, ('t', 'r'), lock=False )
	existingConstraint = findConstraint( src )
	if existingConstraint:
		constraintType = nodeType( existingConstraint )
		constraintFunc = getattr( cmd, constraintType )
		targetsOnConstraint = constraintFunc( existingConstraint, q=True, tl=True )
		if tgt in targetsOnConstraint:
			idx = targetsOnConstraint.index( tgt )
			aliases = constraintFunc( existingConstraint, q=True, weightAliasList=True )
			cons = listConnections( '%s.%s' % (existingConstraint, aliases[ idx ]), type='condition', d=False )

			return cons[ 0 ]


	#when skip axes are specified maya doesn't handle things properly - so make sure
	#ALL transform channels are connected, and remove unwanted channels at the end...
	preT, preR = getAttr( '%s.t' % space )[0], getAttr( '%s.r' % space )[0]
	if existingConstraint:
		chans = CONSTRAINT_CHANNELS[ constraintType ]
		for channel, constraintAttr in zip( *chans ):
			for axis in AXES:
				spaceAttr = '%s.%s%s' %( space, channel, axis)
				conAttr = '%s.%s%s' % (existingConstraint, constraintAttr, axis)
				if not isConnected( conAttr, spaceAttr ):
					connectAttr( conAttr, spaceAttr )


	#get the names for the parents from the parent enum attribute
	cmdOptionKw = { 'mo': True } if maintainOffset else {}
	if objExists( '%s.parent' % nodeWithParentAttr ):
		srcs, names = getSpaceTargetsNames( src )
		addAttr( '%s.parent' % nodeWithParentAttr, e=True, enumName=':'.join( names + [name] ) )

		#if we're building a pointConstraint instead of a parent constraint AND we already
		#have spaces on the object, we need to turn the -mo flag off regardless of what the
		#user set it to, as the pointConstraint maintain offset has different behaviour to
		#the parent constraint
		if constraintType in ( CONSTRAINT_POINT, CONSTRAINT_ORIENT ):
			cmdOptionKw = {}
	else:
		addAttr( nodeWithParentAttr, ln='parent', at="enum", en=name )
		setAttr( '%s.parent' % nodeWithParentAttr, keyable=True )


	#now build the constraint
	constraintFunction = getattr( cmd, constraintType )
	constraint = constraintFunction( tgt, space, **cmdOptionKw )[ 0 ]


	weightAliasList = constraintFunction( constraint, q=True, weightAliasList=True )
	targetCount = len( weightAliasList )
	constraintAttr = weightAliasList[ -1 ]
	condition = shadingNode( 'condition', asUtility=True )
	condition = rename( condition, '%s_to_space_%s#' % (cleanShortName( src ), cleanShortName( tgt )) )

	setAttr( '%s.secondTerm' % condition, targetCount-1 )
	setAttr( '%s.colorIfTrue' % condition, 1, 1, 1 )
	setAttr( '%s.colorIfFalse' % condition, 0, 0, 0 )
	connectAttr( '%s.parent' % nodeWithParentAttr, '%s.firstTerm' % condition )
	connectAttr( '%s.outColorR' % condition, '%s.%s' % (constraint, constraintAttr) )


	#find out what symbol to use to find the parent attribute
	parentAttrIdx = 0
	if not apiExtensions.cmpNodes( space, src ):
		srcTrigger = triggered.Trigger( src )
		parentAttrIdx = srcTrigger.connect( nodeWithParentAttr )


	#add the zooObjMenu commands to the object for easy space switching
	Trigger.CreateMenu( src,
	                    "parent to %s" % name,
	                    ChangeSpaceCmd.Create( targetCount-1, parentAttrIdx ) )


	#when skip axes are specified maya doesn't handle things properly - so make sure
	#ALL transform channels are connected, and remove unwanted channels at the end...
	for axis, value in zip( AXES, preT ):
		if axis in skipTranslationAxes:
			attr = '%s.t%s' % (space, axis)
			delete( attr, icn=True )
			setAttr( attr, value )

	for axis, value in zip( AXES, preR ):
		if axis in skipRotationAxes:
			attr = '%s.r%s' % (space, axis)
			delete( attr, icn=True )
			setAttr( attr, value )


	#make the space node non-keyable and lock visibility
	attrState( space, [ 't', 'r', 's' ], lock=True )
	attrState( space, 'v', *control.HIDE )


	return condition


def removeSpace( src, tgt ):
	'''
	removes a target (or space) from a "space switching" object
	'''

	tgts, names = getSpaceTargetsNames( src )
	tgt_mobject = asMObject( tgt )

	name = None
	for index, (aTgt, aName) in enumerate( zip( tgts, names ) ):
		aTgt = asMObject( aTgt )
		if aTgt == tgt_mobject:
			name = aName
			break

	if name is None:
		raise AttributeError( "no such target" )

	delete = False
	if len( tgts ) == 1:
		delete = True

	constraint = findConstraint( src )

	parentAttrOn = findSpaceAttrNode( src )
	space = findSpace( src )

	srcTrigger = Trigger( src )
	cmds = srcTrigger.iterMenus()

	if delete:
		delete( constraint )
		deleteAttr( '%s.parent' % src )
	else:
		constraintType = nodeType( constraint )
		constraintFunc = getattr( cmd, constraintType )
		constraintFunc( tgt, constraint, rm=True )

	for slot, cmdName, cmdStr in srcTrigger.iterMenus():
		if cmdName == ( "parent to %s" % name ):
			srcTrigger.removeMenu( slot )

		#rebuild the parent attribute
		newNames = names[:]
		newNames.pop( index )
		addAttr( '%s.parent' % parentAttrOn, e=True, enumName=':'.join( newNames ) )

	#now we need to update the indicies in the right click command - all targets that were beyond the one we
	#just removed need to have their indices decremented
	for slot, cmdName, cmdStr in srcTrigger.iterMenus():
		if not cmdName.startswith( 'parent to ' ):
			continue

		cmdStrObj = ChangeSpaceCmd( cmdStr )
		cmdIndex = cmdStrObj.getIndex()
		if cmdIndex < index:
			continue

		cmdStrObj = cmdStrObj.setIndex( cmdIndex-1 )
		srcTrigger.setMenuCmd( slot, cmdStrObj )


def getSpaceName( src, theTgt ):
	'''
	will return the user specified name given to a particular target object
	'''
	tgts, names = getSpaceTargetsNames( src )
	for tgt, name in zip( tgts, names ):
		if tgt == theTgt:
			return name


def getSpaceTargetsNames( src ):
	'''
	this procedure returns a 2-tuple: a list of all targets, and a list of user
	specified names - for the right click menus
	'''
	constraint = findConstraint( src )
	if constraint is None:
		return [], []

	space = findSpace( src, constraint )
	if space is None:
		return [], []

	constraintType = nodeType( constraint )
	constraintFunc = getattr( cmd, constraintType )

	targetsOnConstraint = constraintFunc( constraint, q=True, tl=True )
	trigger = Trigger( src )

	SPECIAL_STRING = 'parent to '
	LEN_SPECIAL_STRING = len( SPECIAL_STRING )

	tgts, names = [], []
	for slotIdx, slotName, slotCmd in trigger.iterMenus():
		if slotName.startswith( SPECIAL_STRING ):
			names.append( slotName[ LEN_SPECIAL_STRING: ] )

			cmdStrObj = ChangeSpaceCmd( slotCmd )
			cmdIndex = cmdStrObj.getIndex()
			tgts.append( targetsOnConstraint[ cmdIndex ] )

	return tgts, names


def findSpace( obj, constraint=None ):
	'''
	will return the node being used as the "space node" for any given space switching object
	'''
	if constraint is None:
		constraint = findConstraint( obj )
		if constraint is None:
			return None

	cAttr = '%s.constraintParentInverseMatrix' % constraint
	spaces = listConnections( cAttr, type='transform', d=False )
	if spaces:
		future = ls( listHistory( cAttr, f=True ), type='transform' )
		if future:
			return future[ -1 ]


def findConstraint( obj ):
	'''
	will return the name of the constraint node thats controlling the "space node" for any given
	space switching object
	'''
	parentAttrOn = findSpaceAttrNode( obj )
	if parentAttrOn is None:
		return None

	pAttr = '%s.parent' % parentAttrOn
	if not objExists( pAttr ):
		return None

	conditions = listConnections( pAttr, type='condition', s=False ) or []
	for condition in conditions:
		constraints = listConnections( '%s.outColorR' % condition, type='constraint', s=False )
		if constraints:
			return constraints[ 0 ]

	return None


def findSpaceAttrNode( obj ):
	'''
	returns the node that contains the parent attribute for the space switch
	'''
	parentAttrOn = "";
	trigger = Trigger( obj )

	for slotIdx, slotName, slotCmd in trigger.iterMenus():
		if slotName.startswith( 'parent to ' ):
			cmdStrObj = ChangeSpaceCmd( slotCmd )
			connectToken = cmdStrObj.getConnectToken()

			return trigger.resolve( connectToken )


#end
