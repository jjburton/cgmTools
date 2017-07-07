import maya.cmds as mc


from cgm.core.lib import transform_utils as TRANS
from cgm.core.lib import position_utils as POS

reload(TRANS)

reload(POS)


_root = 'node'
_euclid = False
#...gets...
TRANS.translate_get(_root,_euclid)
TRANS.position_get(_root,asEuclid = _euclid)
TRANS.rotate_get(_root,_euclid)
TRANS.eulerAngles_get(_root)
TRANS.orient_get(_root,_euclid)
TRANS.orient_get(_root,_euclid)
TRANS.orientObject_get(_root,_euclid)
TRANS.rotateAxis_get(_root,_euclid)
TRANS.worldMatrix_get(_root,_euclid)
TRANS.scaleLocal_get(_root,_euclid)
TRANS.scaleLossy_get(_root,_euclid)

#...sets...
_pos = [0,1,1]
_rot = [10,66,80]
_scale = [1,2,1]
_rot = TRANS.rotate_get('NotBatman_master_block1',True)
TRANS.translate_set(_root,_pos)
TRANS.position_set(_root,_pos)
TRANS.rotate_set(_root,_rot)
TRANS.eulerAngles_set(_root,_rot)
TRANS.orient_set(_root,_rot)
TRANS.orientObject_set(_root,_rot)
TRANS.rotateAxis_set(_root,_rot)
TRANS.scaleLocal_set(_root,_scale)



#...heirarchy
_rootRoot = 'group2'
TRANS.parent_get(_root)
TRANS.parent_set(_root,TRANS.parent_get(_root))
TRANS.parents_get(_root)
TRANS.children_get(_rootRoot)
TRANS.descendents_get(_rootRoot)
TRANS.is_childTo(_root,TRANS.parents_get(_root)[0])
TRANS.is_childTo(_root,None)
TRANS.is_parentTo(_rootRoot, _root)
TRANS.is_parentTo(_root, _rootRoot)

cgmMeta.cgmObject(_rootRoot).getListPathTo(_root)
TRANS.get_listPathTo(_rootRoot, _root,False)

cgmMeta.cgmObject(_root).getListPathTo(_rootRoot)
TRANS.get_listPathTo(_root, _rootRoot,False)

TRANS.is_parentTo(_root,TRANS.parents_get(_root)[0])


_root = 'NotBatman_master_block'
_root = 'NotBatman_master_block|curveShape2'
_root = 'NotBatman_master_block.cv[50]'
_root = 'NotBatman_master_block.ep[26]'
_root = 'NotBatman_master_block2'
TRANS.sibblings_get(_root,False)
TRANS.shapes_get(_root)
TRANS.get_rootList()

#...transform matrix stuff...
_v = [1,1,1]
TRANS.worldMatrix_get(_root,True)

TRANS.transformDirection(_root,_v)
TRANS.transformPoint(_root,_v)
TRANS.transformInverseDirection(_root,_v)
TRANS.transformInversePoint(_root,_v)
TRANS.euclidVector3Arg([0,0,0])


#...creation
TRANS.child_create(_root)
TRANS.parent_create(_root)
TRANS.group_me(_root)