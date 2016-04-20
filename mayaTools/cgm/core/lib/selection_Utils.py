"""
------------------------------------------
rayCaster: cgm.core.lib.rayCaster
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

ACKNOWLEDGEMENTS:
   Samaneh Momtazmand -- r&d for casting with surfaces
================================================================
"""
import maya.cmds as mc
import copy
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OM
from cgm.core.cgmPy import validateArgs as cgmValid

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
