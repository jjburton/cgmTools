"""
------------------------------------------
selection_Utils: cgm.core.lib.selection_Utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

ACKNOWLEDGEMENTS:
   
================================================================
"""
import maya.cmds as mc
import copy
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OM
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.lib import search

def get_filtered(mode = 'transform'):
    """
    Create a new mesh by adding,subtracting etc the positional info of one mesh to another

    :parameters:
        sourceObj(str): The mesh we're using to change our target
        target(str): Mesh to be modified itself or by duplication

    :returns
        mesh(str) -- which has been modified

    """
    _str_funcName = 'get_filtered'
    _modes = ['transform']
    _m = cgmValid.kw_fromList(mode, _modes, indexCallable=True, calledFrom=_str_funcName)
    
    _res = []
    if _m == 'transform':
        _sel = mc.ls(sl=True)
        for s in _sel:
            _t = search.get_transform(s)
            if _t not in _res:
                _res.append(_t)
                
    return  _res
    

def get_softSelectionItems():
    """
    Acknowledgements: 
    http://forums.cgsociety.org/archive/index.php?t-1065459.html
    """
    selection = OM.MSelectionList()
    softSelection = OM.MRichSelection()
    OM.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)
    
    dagPath = OM.MDagPath()
    component = OM.MObject()
    
    iter = OM.MItSelectionList( selection,OM.MFn.kMeshVertComponent )
    elements = []
    while not iter.isDone(): 
        iter.getDagPath( dagPath, component )
        dagPath.pop()
        node = dagPath.fullPathName()
        fnComp = OM.MFnSingleIndexedComponent(component) 
        
        for i in range(fnComp.elementCount()):
            elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
        iter.next()
    return elements

def get_softSelectionWeights():
    """
    https://groups.google.com/forum/#!topic/python_inside_maya/q1JlddKybyM
    """
    #Grab the soft selection
    selection = OM.MSelectionList()
    softSelection = OM.MRichSelection()
    OM.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)
    
    dagPath = OM.MDagPath()
    component = OM.MObject()
    
    # Filter Defeats the purpose of the else statement
    iter = OM.MItSelectionList( selection,OM.MFn.kMeshVertComponent )
    elements, weights = [], []
    while not iter.isDone(): 
        iter.getDagPath( dagPath, component )
        dagPath.pop() #Grab the parent of the shape node
        node = dagPath.fullPathName()
        fnComp = OM.MFnSingleIndexedComponent(component)   
        getWeight = lambda i: fnComp.weight(i).influence() if fnComp.hasWeights() else 1.0
        
        for i in range(fnComp.elementCount()):
            elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
            weights.append(getWeight(i)) 
        iter.next()
        
    return elements, weights

def get_sorted_softSelectionWeights():
    """
    https://groups.google.com/forum/#!topic/python_inside_maya/q1JlddKybyM
    """
    #Grab the soft selection
    selection = OM.MSelectionList()
    softSelection = OM.MRichSelection()
    OM.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)
    
    dagPath = OM.MDagPath()
    component = OM.MObject()
    
    # Filter Defeats the purpose of the else statement
    iter = OM.MItSelectionList( selection,OM.MFn.kMeshVertComponent )
    elements, weights = [], []
    d_objects = {}
    while not iter.isDone(): 
        iter.getDagPath( dagPath, component )
        dagPath.pop() #Grab the parent of the shape node
        node = dagPath.fullPathName()
        if not d_objects.get(node,False):
            d_objects[node] = {}
        
        _d = d_objects[node]
        fnComp = OM.MFnSingleIndexedComponent(component)   
        getWeight = lambda i: fnComp.weight(i).influence() if fnComp.hasWeights() else 1.0
        
        for i in range(fnComp.elementCount()):
            elements.append('%s.vtx[%i]' % (node, fnComp.element(i)))
            _path = '%s.vtx[%i]' % (node, fnComp.element(i))
            _d[int(_path.split('[')[-1].split(']')[0])] = getWeight(i)
            weights.append(getWeight(i)) 
        iter.next()
        
    return d_objects
