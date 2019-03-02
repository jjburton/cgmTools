"""
name_utils
Josh Burton 
www.cgmonks.com

"""
# From Python =============================================================
import copy
import re
import pprint

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
import cgm.core.lib.list_utils as LISTS
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
        _surface = mc.listRelatives(mesh,shapes=True,fullPath = True)[0]
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
    

def createFollicleOnMesh(targetSurface, name = 'follicle'):
    """
    Creates named follicle node on a mesh
    
    Keywords
    mesh -- mesh to attach to
    name -- base name to use ('follicle' default)
    
    Returns
    [follicleNode,follicleTransform]
    """
    
    if SEARCH.is_shape(targetSurface):
        l_shapes = [targetSurface]
    else:
        l_shapes = mc.listRelatives(targetSurface, s=True,fullPath = True)
    if not l_shapes:
        raise ValueError,"Must have shapes to check."


    _shape = l_shapes[0]
    log.info("_shape: {0}".format(_shape))
    _type = VALID.get_mayaType(_shape)    
    
    #objType = search.returnObjectType(mesh)
    #assert objType in ['mesh','nurbsSurface'],("'%s' isn't a mesh"%mesh)
        
    follicleNode = create((name),'follicle')
    
    """ make the closest point node """
    #closestPointNode = createNamedNode((targetObj+'_to_'+mesh),'closestPointOnMesh')
    #controlSurface = mc.listRelatives(_shape,shapes=True)[0]
    follicleTransform = mc.listRelatives(follicleNode,p=True,fullPath = True)[0]
    
    attributes.doConnectAttr((_shape+'.worldMatrix[0]'),(follicleNode+'.inputWorldMatrix'))#surface to follicle node 
    
    if _type == 'mesh': 
        attributes.doConnectAttr((_shape+'.outMesh'),(follicleNode+'.inputMesh'))    #surface mesh to follicle input mesh
    else:
        attributes.doConnectAttr((_shape+'.local'),(follicleNode+'.inputSurface'))    #surface mesh to follicle input mesh
        
    attributes.doConnectAttr((follicleNode+'.outTranslate'),(follicleTransform+'.translate'))
    attributes.doConnectAttr((follicleNode+'.outRotate'),(follicleTransform+'.rotate'))    
    
    attributes.doSetLockHideKeyableAttr(follicleTransform)
    
    return [follicleNode,follicleTransform]



d_function_to_Operator = {'==':0,'!=':1,'>':2,'>=':3,'<':4,'<=':5,#condition
                          '*':1,'/':2,'^':3,#md
                          '+':1,'-':2,'><':3}#pma

d_operator_to_NodeType = {'clamp':['clamp('],
                          'setRange':['setRange('],
                          'condition':[' == ',' != ',' > ',' < ',' >= ',' <= '],
                          'multiplyDivide':[' * ',' / ',' ^ '],
                          'plusMinusAverage':[' + ',' - ',' >< ']}#>< we're using for average

d_node_to_input = {'multiplyDivide':{'in':['input1','input2'],
                                     'out':'output'},
                   'plusMinusAverage':{'in':['input1'],
                                       'out':'output'}}

def optimize(nodeTypes='multiplyDivide'):
    _str_func = 'optimize'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)
    
    _nodeTypes = VALID.listArg(nodeTypes)
    d_modeToNodes = {}
    d_modeToPlugs = {}
    l_oldNodes = []
    
    for t in _nodeTypes:
        if t in ['plusMinusAverage']:
            raise ValueError,"Don't handle type: {0}".format(t)
        nodes = mc.ls(type=t)
        l_oldNodes.extend(nodes)
        for n in nodes:
            _mode = ATTR.get(n,'operation')
            _operator = ATTR.get_enumValueString(n,'operation')
            #d_operator_to_NodeType[t][_mode]
            
            if not d_modeToNodes.get(_mode):
                d_modeToNodes[_mode] = []
            d_modeToNodes[_mode].append(n)
            
            d_plugs = {}
            d_plugValues = {}
            for i,inPlug in enumerate(d_node_to_input[t]['in']):
                d_plugs[i] = ATTR.get_children(n,inPlug) or []
                for p in d_plugs[i]:
                    c = ATTR.get_driver(n,p,False,skipConversionNodes=True)
                    if c:
                        d_plugValues[p] = c
                    else:
                        d_plugValues[p] = ATTR.get(n,p)
                    
            l_outs = ATTR.get_children(n,d_node_to_input[t]['out']) or []
            for p in l_outs:
                d_plugValues[p] = ATTR.get_driven(n,p,False,skipConversionNodes=True)
            
            #pprint.pprint(d_modeToNodes)
            #pprint.pprint(d_plugs)
            #print l_outs
            #print cgmGeneral._str_subLine
            #pprint.pprint(d_plugValues)
            
            for i in range(len(l_outs)):
                _out = d_plugValues[l_outs[i]]
                if _out:
                    d_set = {'out':_out, 'in':[]}
                    log.debug("|{0}| >> Output found on: {1} ".format(_str_func,_out))
                    _keys = d_plugs.keys()
                    _keys.sort()
                    for k in _keys:
                        d_set['in'].append(d_plugValues[  d_plugs[k][i] ])
                        #d_set['in'].append(d_plugs[k][i])
                    #pprint.pprint(d_set)
                    
                    if not d_modeToPlugs.get(_mode):
                        d_modeToPlugs[_mode] = []
                    d_modeToPlugs[_mode].append(d_set)
                    
            #    if VALID.stringArg()



    l_inPlugs = ['input1','input2']
    l_outplugs = [u'output']
    l_new = []
    _cnt = 0
        
    for operator,d_sets in d_modeToPlugs.iteritems():
        if operator == 1:
            for nodeSet in d_sets:
                newNode = mc.createNode('multDoubleLinear')
                newNode = mc.rename(newNode,'optimize_{0}_mdNode'.format(_cnt))
                _cnt+=1
                l_new.append(newNode)
                
                _ins = d_set['in']
                _outs = d_set['out']
                
                for iii,inPlug in enumerate(_ins):
                    if mc.objExists(inPlug):
                        ATTR.connect(inPlug, "{0}.{1}".format(newNode, l_inPlugs[iii]))
                    else:
                        ATTR.set(newNode,l_inPlugs[iii], inPlug)
                    
                for out in _outs:
                    ATTR.connect("{0}.output".format(newNode), out)
                    
        #pprint.pprint(d_setsSorted)
        print len(d_sets)
        #print len(d_setsSorted)    
    
    
    
    """
    
    l_inPlugs = {0: [u'input1X', u'input1Y', u'input1Z'],
               1: [u'input2X', u'input2Y', u'input2Z']}
    l_outplugs = [u'outputX', u'outputY', u'outputZ']
    
    for operator,d_sets in d_modeToPlugs.iteritems():
        d_setsSorted = LISTS. get_chunks(d_sets,3)
        for nodeSet in d_setsSorted:
            newNode = mc.createNode('multiplyDivide')
            newNode = mc.rename(newNode,'optimize_{0}_mdNode'.format(_cnt))
            _cnt+=1
            l_new.append(newNode)
            ATTR.set(newNode,'operation',operator)
            
            for i,d_set in enumerate(nodeSet):
                _ins = d_set['in']
                _outs = d_set['out']
                
                for iii,inPlug in enumerate(_ins):
                    if mc.objExists(inPlug):
                        ATTR.connect(inPlug, "{0}.{1}".format(newNode, l_inPlugs[iii][i]))
                    else:
                        ATTR.set(newNode,l_inPlugs[iii][i], inPlug)
                    
                for out in _outs:
                    ATTR.connect("{0}.{1}".format(newNode, l_outplugs[i]), out)
                    
        #pprint.pprint(d_setsSorted)
        print len(d_sets)
        print len(d_setsSorted)
        """
    mc.delete(l_oldNodes)
    return len(l_new)
    
    

    
def renderer_clean(check='Mayatomr',clean=False):
    """
    Hattip: https://forums.autodesk.com/t5/maya-shading-lighting-and/maya-2017-scene-error-warning-about-mental-ray-nodes/td-p/6627874
    """
    d_rendererNodes = {'turtle':['TurtleRenderOptions',
                                 'TurtleUIOptions',
                                 'TurtleBakeLayerManager',
                                 'TurtleDefaultBakeLayer']}
    _str_func = 'renderer_clean'
    log.debug("|{0}| >> [{1}] | clean: {2}...".format(_str_func,check,clean))
    
    if check in ['Mayatomr']:
        l = mc.ls(type='unknown')
        log.debug("|{0}| >> unknown nodes: {1}".format(_str_func,len(l)))
        
        for n in l:
            try:
                _test = mc.unknownNode(n, q=True,p=1)
                if _test == check:
                    log.debug("|{0}| >> matches: {1}".format(_str_func,n))
                    if clean:
                        mc.delete(n)
            except:pass
            
        if check in mc.unknownPlugin(q=1,list=1):
            log.debug("|{0}| >> Found: {1}".format(_str_func,check))
            if clean:
                log.debug("|{0}| >> Removing: {1}".format(_str_func,check))
                mc.unknownPlugin(check,remove=1)
    else:
        l = d_rendererNodes.get(check.lower())
        for n in l:
            if mc.objExists(n):
                log.debug("|{0}| >> matches: {1}".format(_str_func,n))
                if clean:
                    try:mc.delete(n)
                    except Exception,err:
                        log.debug("|{0}| >> Failed: {1} | {2}".format(_str_func,n,err))
        """
        for n in mc.ls():
            if 'turtle' in n.lower():
                for n in l:
                    try:
                        _test = mc.unknownNode(n, q=True,p=1)
                        if _test == check:
                            log.debug("|{0}| >> matches: {1}".format(_str_func,n))
                            if clean:
                                mc.delete(n)"""
                
    
    

    
    
    

