"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basis of working with RigBlocks
================================================================
"""
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.mrs import RigBlocks as RBLOCKS
#reload(RBLOCKS)
#==============================================================================================
#>> cgmMeta.cgmObject
#==============================================================================================
from cgm.core import cgm_Meta as cgmMeta
import maya.cmds as mc
import copy


#>>Box ====================================================================================
#First we're gonna make some objects to deal with, say 5
#For now you need the template file...

_root = 'box_root_crv'

#First let's familiarize ourselves with the basic factory functions...
b1 = RBLOCKS.factory()#...give you an empty factory
b1.set_rigBlock(_root)#...sets the active control

b1 = RBLOCKS.factory(_root)#...this will initialize our block factory

b1.verify()#...check the rigBlock 

#>>Quereies
#...you can query any rig block type
b1.get_attrCreateDict('box')
b1.get_skeletonCreateDict('box')


#>> Puppet stuff
b1.module_verify()#...verify we have a module
b1.puppet_verify()#...verify we have a puppet


#>> States
b1.skeletonize(True)# True being rebuild. If you change joint count setting for example

#>> Geo
b1.create_mesh('simple')
b1.create_mesh('jointProxy')


