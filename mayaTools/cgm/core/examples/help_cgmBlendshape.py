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
cgm.core._reload()#...this is the core reloader

#==============================================================================================
#>> cgmMeta.cgmBlendshape
#==============================================================================================
import maya.cmds as mc

#You MUST have the demo file to work though this exercise though you could probably glean the gist without it with your own  setup

#>>Starting off =========================================================================
bs1 = cgmMeta.cgmBlendShape('pSphere1_bsNode')#...let's initialize our blendshape

#>>bsShape Functions =========================================================================
#We're referring to the shapes that drive a blendshape nodeds base object here and the functions relating to them
#Doing this first will make the blendshape wide functions make more sense on the queries and what not.

bs1.bsShape_add('base1_add')#...we're gonna add a new shape to our node. Since no index is specified, it just chooses the next available
bs1.bsShape_add('base1_add', 8)#...let's  specify an index
#...hmm, our add throws an error because that name is taken. let's fix it
bs1.bsShape_nameWeightAlias('HeyThere',8)#...nice!
bs1.bsShape_add('base1_tween', 0, weight = .5)#...we're gonna add a new inbetween shape by it's geo, index, and weight

#Replace functions...
#...replacing is not something easily done in basic maya calls
bs1.bsShape_replace('base1_replace','base1_target')#...replace with a "from to"" call. 
#...Note - the inbetween is intact as is the driver connection
bs1.bsShape_replace('base1_replace',0)#...indice calls also work for most calls
bs1.bsShape_replace('base1_target',0)

#Indexing...
#An index for use with working with blendshapes needs to have an index and weight in order to know what you're working with
bs1.bsShape_index('base1_target')#...this will return a list of the indices and weights which this target affects in [[index,weight],...] format
bs1.bsShape_index('base1_add')#...this will return a list of the indices and weights which this target affects in [[index,weight],...] format

#Query...
bs1.bsShape_getTargetArgs('base1_target')#...this returns data for a target in the format excpected by mc.blendshape for easier use in nested list format

#>>Blendshape node wide functions =========================================================================
bs1.get_targetWeightsDict()#...this is a handy call for just getting the data on a blendshape in {index:{weight:{data}}} format
bs1.get_indices()#...get the indices in use on the blendshape from the api in a list format
bs1.get_shapes()#...get our blendshape shapes that drive our blendshape
bs1.get_baseObjects()#...get the base shapes of the blendshape or the object(s) the blendshape is driving
bs1.get_weight_attrs()#...get the attributes on the bsNode which drive our indices

#arg validation ...
bs1.bsShape_validateShapeArg()#...no target specified, error
bs1.bsShape_validateShapeArg(0)#...more than one entry, error
bs1.bsShape_validateShapeArg(0, .5)#...there we go
bs1.bsShape_validateShapeArg('base1_target')


#>>message Treatment =========================================================================
#We have made several changes to r9's stuff in how we do messages, it is however compatible with r9's stuff

#==============================================================================================
