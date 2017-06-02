"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basis of cgmMeta.cgmBlendshape
================================================================
"""
from cgm.core import cgm_Meta as cgmMeta
#cgm.core._reload()#...this is the core reloader

#==============================================================================================
#>> cgmMeta.cgmBlendshape
#==============================================================================================
import maya.cmds as mc

#You MUST have the demo file to work though this exercise though you could probably glean the gist without it with your own  setup

#>>Starting off =========================================================================
bs1 = cgmMeta.cgmBlendShape('pSphere1_bsNode')#...let's initialize our blendshape
bs1._MFN #...here you'll find the api blendshape deformer call should you be inclined to use it

#>>bsShape Functions =========================================================================
#We're referring to the shapes that drive a blendshape nodeds base object here and the functions relating to them
#Doing this first will make the blendshape wide functions make more sense on the queries and what not.

bs1.bsShape_add('base1_add')#...we're gonna add a new shape to our node. Since no index is specified, it just chooses the next available
bs1.bsShape_add('base1_add', 8)#...let's  specify an index
#...hmm, our add throws an error because that name is taken. let's fix it
bs1.bsShape_nameWeightAlias('HeyThere',8)#...nice!
bs1.bsShape_add('base1_tween', 0, weight = .5)#...we're gonna add a new inbetween shape by it's geo, index, and weight
#==============================================================================================

#Replace functions...
#...replacing is not something easily done in basic maya calls
bs1.bsShape_replace('base1_replace','base1_target')#...replace with a "from to"" call. 
bs1.bsShape_replace('base1_target','base1_replace')#...and back

#...Note - the inbetween is intact as is the driver connection
bs1.bsShape_replace('base1_replace',0)#...indice calls also work for most calls
bs1.bsShape_replace('base1_target',0)
#==============================================================================================

#Indexing...
#An index for use with working with blendshapes needs to have an index and weight in order to know what you're working with
bs1.bsShape_index('base1_target')#...this will return a list of the indices and weights which this target affects in [[index,weight],...] format
bs1.bsShape_index('base1_add')#...this will return a list of the indices and weights which this target affects in [[index,weight],...] format
#==============================================================================================

#Query...
bs1.bsShape_getTargetArgs('base1_target')#...this returns data for a target in the format excpected by mc.blendshape for easier use in nested list format
bs1.is_bsShape('base1_target')#...yup
bs1.is_bsShape('bakeTo')#...nope
#==============================================================================================

#>>Blendshape node wide functions =========================================================================
bs1.get_targetWeightsDict()#...this is a handy call for just getting the data on a blendshape in {index:{weight:{data}}} format
bs1.get_indices()#...get the indices in use on the blendshape from the api in a list format
bs1.bsShapes_get()#...get our blendshape shapes that drive our blendshape
bs1.get_baseObjects()#...get the base shapes of the blendshape or the object(s) the blendshape is driving
bs1.get_weight_attrs()#...get the attributes on the bsNode which drive our indices
bs1.bsShapes_get()#...get our shapes
#==============================================================================================

#>>Arg validation =========================================================================
bs1.bsShape_validateShapeArg()#...no target specified, error
bs1.bsShape_validateShapeArg(0)#...more than one entry, error
bs1.bsShape_validateShapeArg(0, .5)#...there we go
bs1.bsShape_validateShapeArg('base1_target')
#==============================================================================================

#Generating geo...
#Sometimes you wanna extract shapes from a blendShape node. Let's try some of that
bs1.bsShape_createGeoFromIndex(0)#...will create the a new piece of geo matching the 1.0 weight at 1.0
bs1.bsShape_createGeoFromIndex(0,.5)#...will get you the inbetween
bs1.bsShape_createGeoFromIndex(3)#...will get you squat because nothing is there
bs1.bsShape_createGeoFromIndex(0, multiplier = 2.0)#...you can also generate factored targets
bs1.bsShape_createGeoFromIndex(0, multiplier = .5)#...


bs1.bsShapes_delete()#...delete all the targets for your blendshape.
#...ah geeze I didn't mean to do that. No worries!
bs1.bsShapes_restore()#...rebuilds the targets and plugs them back in
#==============================================================================================

#To come...
#Shape adding/subtracting etc
#Baking to target etc.
 
#==============================================================================================
