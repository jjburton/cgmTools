"""
name_utils
Josh Burton 
www.cgmonks.com

"""
# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.lib import search_utils as SEARCH
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import attribute_utils as ATTR
reload(SHARED)

#CANNOT IMPORT: DIST, LOC

from cgm.lib import attributes

#>>> Utilities
#===================================================================
def add_follicle(mesh, name = 'follicle'):
    """
    Creates named follicle node on a mesh
    
    :parameters:
        mesh(str): Surface to attach to
        name(str): base name for the follicle

    :returns
        [newNode, newTransform]
    """   
    _str_func = "add_follicle"
    
    _node= create(name,'follicle')
    
    if SEARCH.is_shape(mesh):
        _surface = mesh
    else:
        _surface = mc.listRelatives(mesh,shapes=True)[0]
    _type = VALID.get_mayaType(_surface)
    _trans = SEARCH.get_transform(_node)
    
    attributes.doConnectAttr((_surface+'.worldMatrix[0]'),(_node+'.inputWorldMatrix'))#surface to follicle node 
    if _type == 'mesh': 
        attributes.doConnectAttr((_surface+'.outMesh'),(_node+'.inputMesh'))    #surface mesh to follicle input mesh
    else:
        attributes.doConnectAttr((_surface+'.local'),(_node+'.inputSurface'))    #surface mesh to follicle input mesh
        
    attributes.doConnectAttr((_node+'.outTranslate'),(_trans+'.translate'))
    attributes.doConnectAttr((_node+'.outRotate'),(_trans+'.rotate'))    
    
    #ATTR.set_message(_node,'follTrans',_trans)
    #ATTR.set_message(_trans,'follNode',_node)
    
    attributes.doSetLockHideKeyableAttr(_trans)
        
    return [_node,_trans]    
    
    """follicleNode = createNamedNode((name),'follicle')
        
    #closestPointNode = createNamedNode((targetObj+'_to_'+mesh),'closestPointOnMesh')
    controlSurface = mc.listRelatives(mesh,shapes=True)[0]
    follicleTransform = mc.listRelatives(follicleNode,p=True)[0]
    
    attributes.doConnectAttr((controlSurface+'.worldMatrix[0]'),(follicleNode+'.inputWorldMatrix'))#surface to follicle node 
    if objType == 'mesh': 
        attributes.doConnectAttr((controlSurface+'.outMesh'),(follicleNode+'.inputMesh'))    #surface mesh to follicle input mesh
    else:
        attributes.doConnectAttr((controlSurface+'.local'),(follicleNode+'.inputSurface'))    #surface mesh to follicle input mesh
        
    attributes.doConnectAttr((follicleNode+'.outTranslate'),(follicleTransform+'.translate'))
    attributes.doConnectAttr((follicleNode+'.outRotate'),(follicleTransform+'.rotate'))    
    
    attributes.doSetLockHideKeyableAttr(follicleTransform)
    
    return [follicleNode,follicleTransform] """
    
def create(name = None, nodeType = None):
    """
    Create a named node
    
    :parameters:
        name(str): base name
        nodeType(str): 
            follicle

    :returns
        [newNode, newTransform]
    """   
    _str_func = "create"
    
    if name is None:
        name = 'i_should_have_given_a_name'
    _suffix = SHARED._d_node_to_suffix.get(nodeType,False)
    if _suffix == False:
        raise ValueError,"Update cgm.core.lib.shared_data._d_node_to_suffix with nodeType: {0}".format(nodeType)
    
    _l_utilityNodes = ['plusMinusAverage','condition']
    
    if nodeType in _l_utilityNodes:
        return mc.shadingNode (nodeType,name= (name+'_'+_suffix), asUtility=True)
    else:
        return mc.createNode (nodeType,name= (name+'_'+_suffix),)
    

def createFollicleOnMesh(mesh, name = 'follicle'):
    """
    Creates named follicle node on a mesh
    
    Keywords
    mesh -- mesh to attach to
    name -- base name to use ('follicle' default)
    
    Returns
    [follicleNode,follicleTransform]
    """
    assert mc.objExists(mesh),"'%s' doesn't exist!"%mesh
    #objType = search.returnObjectType(mesh)
    #assert objType in ['mesh','nurbsSurface'],("'%s' isn't a mesh"%mesh)
        
    follicleNode = createNamedNode((name),'follicle')
    
    """ make the closest point node """
    #closestPointNode = createNamedNode((targetObj+'_to_'+mesh),'closestPointOnMesh')
    controlSurface = mc.listRelatives(mesh,shapes=True)[0]
    follicleTransform = mc.listRelatives(follicleNode,p=True)[0]
    
    attributes.doConnectAttr((controlSurface+'.worldMatrix[0]'),(follicleNode+'.inputWorldMatrix'))#surface to follicle node 
    if objType == 'mesh': 
        attributes.doConnectAttr((controlSurface+'.outMesh'),(follicleNode+'.inputMesh'))    #surface mesh to follicle input mesh
    else:
        attributes.doConnectAttr((controlSurface+'.local'),(follicleNode+'.inputSurface'))    #surface mesh to follicle input mesh
        
    attributes.doConnectAttr((follicleNode+'.outTranslate'),(follicleTransform+'.translate'))
    attributes.doConnectAttr((follicleNode+'.outRotate'),(follicleTransform+'.rotate'))    
    
    attributes.doSetLockHideKeyableAttr(follicleTransform)
    
    return [follicleNode,follicleTransform]

