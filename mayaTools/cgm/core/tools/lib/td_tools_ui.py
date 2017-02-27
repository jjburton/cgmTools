"""
------------------------------------------
td_ui_tools: cgm.core.tools.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
2.0 rewrite
================================================================
"""
__version__ = '0.1.02262017'

import maya.cmds as mc
import maya
import maya.mel as mel

from cgm.core import cgm_General as cgmGen
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.tools import meshTools
from cgm.core.lib import node_utils as NODES
from cgm.core.tools import attrTools as ATTRTOOLS

def uiSection_selection(parent = None):
    uiSelect = mc.menuItem(parent = parent, l='Select*', subMenu=True,tearOff = True)
    
    for s in ['selection','children','heirarchy','scene']:
        mc.menuItem(p=uiSelect, l=s,subMenu=True)

        mc.menuItem(l='Joints', subMenu = False,
                    c=cgmGen.Callback(MMCONTEXT.select,s,'joint'))
        mc.menuItem(l='Curves', subMenu = False,
                    c=cgmGen.Callback(MMCONTEXT.select,s,'nurbsCurve'))
        mc.menuItem(l='Mesh', subMenu = False,
                    c=cgmGen.Callback(MMCONTEXT.select,s,'mesh'))        
        mc.menuItem(l='Surface', subMenu = False,
                    c=cgmGen.Callback(MMCONTEXT.select,s,'nurbsSurface'))   
    
    return uiSelect


def uiSection_distance(parent = None, selection = None, pairSelected = True):
    _p = mc.menuItem(parent=parent, subMenu = True,tearOff = True,
                     en=pairSelected,
                     l = 'Distance')  

    if pairSelected:     
        _n = mc.menuItem(parent=_p, subMenu = True,
                         l = 'Near')
        _f = mc.menuItem(parent=_p, subMenu = True,
                         l = 'Far')

        mc.menuItem(parent=_n, 
                    l = 'Target',
                    c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Near Target',True,**{'mode':'closest','resMode':'object'}),                                                                      
                    )   
        mc.menuItem(parent=_n, 
                    l = 'Shape',
                    c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Near Shape',True,**{'mode':'closest','resMode':'shape'}),                                                                      
                    )               
        mc.menuItem(parent=_n, 
                    l = 'Surface Point',
                    c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Near point on surface',True,**{'mode':'closest','resMode':'pointOnSurface'}),                                                                      
                    )     
        mc.menuItem(parent=_n, 
                    l = 'Surface Loc',
                    c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Near point on surface',True,**{'mode':'closest','resMode':'pointOnSurfaceLoc'}),                                                                      
                    )               
        mc.menuItem(parent=_n,
                    l = 'Surface Nodes',
                    c = cgmGen.Callback(MMCONTEXT.func_process, DIST.create_closest_point_node, selection,'firstToEach','Create closest Point Node',True,**{}),                                                                      
                    )                 



        mc.menuItem(parent=_f, 
                    l = 'Target',
                    c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Far Target',True,**{'mode':'far','resMode':'object'}),                                                                      
                    )                  
        mc.menuItem(parent=_f, 
                    l = 'Shape',
                    c = cgmGen.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Far Shape',True,**{'mode':'far','resMode':'shape'}),                                                                      
                    )      
    return _p


    
def uiSection_joints(parent = None):
    uiJoints = mc.menuItem(parent = parent, l='Joints', subMenu=True, tearOff = True)

    _axis = mc.menuItem(l='Axis', subMenu = True)
    
    for ctxt in ['selection','children','heirarchy','scene']:
            mc.menuItem(p=_axis, l=ctxt,subMenu=True)
            mc.menuItem(l='Show',
                        c=cgmGen.Callback(MMCONTEXT.set_attrs,None,'displayLocalAxis',1,ctxt,'joint'))
        
            mc.menuItem(l='Hide',
                        c=cgmGen.Callback(MMCONTEXT.set_attrs,None,'displayLocalAxis',0,ctxt,'joint'))
            

    mc.menuItem(parent = uiJoints,
                l='cometJO',
                c=lambda *a: mel.eval('cometJointOrient'),
                ann="General Joint orientation tool\n by Michael Comet")   
    
    
    
    
def uiSection_sdk(parent = None):
    _str_func = 'uiSection_sdk'
    uiSDK = mc.menuItem(parent = parent, l='SDK', subMenu=True)
    
    mc.menuItem(parent = uiSDK,
                l='seShapeTaper',
                c=lambda *a: mel.eval('seShapeTaper'),)   
    
    
def uiSection_curves(parent):
    uiCurve = mc.menuItem(parent = parent, l='Curve', subMenu=True)
    mc.menuItem(parent=uiCurve,
                l = 'Describe',
                c = cgmGen.Callback(MMCONTEXT.func_context_all, CURVES.get_python_call, 'selection','shape'),                            
                )   
    mc.menuItem(parent=uiCurve,
                en=False,
                l = 'Mirror')      

def uiSection_shapes(parent = None, selection = None, pairSelected = True):
    _str_func = 'uiSection_shapes'    
    
    #>>>Shape ==============================================================================================
    uiShape = mc.menuItem(parent = parent, l='Shape', subMenu=True,tearOff = True)


    #---------------------------------------------------------------------------
    mc.menuItem(parent=uiShape,
                #en = pairSelected,
                l = 'shapeParent',
                #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.shapeParent_in_place, selection, 'lastFromRest','shapeParent'),
                rp = "W")   
    _d_combine = {'keepSource':False}
    mc.menuItem(parent=uiShape,
                #en = pairSelected,                
                l = 'Combine',
                #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                c = cgmGen.Callback(MMCONTEXT.func_enumrate_all_to_last, RIGGING.shapeParent_in_place, selection,'toFrom', **_d_combine),
                rp = "NW")
    mc.menuItem(parent=uiShape,
                #en = pairSelected,                
                l = 'Add',
                #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                c = cgmGen.Callback(MMCONTEXT.func_enumrate_all_to_last, RIGGING.shapeParent_in_place, selection,'toFrom', **{}),
                rp = "NW")      

    _d_replace = {'replaceShapes':True}                
    mc.menuItem(parent=uiShape,
                l = 'Replace',
                c = cgmGen.Callback(MMCONTEXT.func_process, RIGGING.shapeParent_in_place, selection,'lastFromRest', 'replaceShapes',**_d_replace),                                                        
                #c = cgmGen.Callback(MMCONTEXT.func_all_to_last, RIGGING.shapeParent_in_place, selection,'toFrom', **_d_replace),                            
                rp = "SW")                  

    mc.menuItem(parent=uiShape,
                l = 'Extract',
                c = cgmGen.Callback(MMCONTEXT.func_context_all, RIGGING.duplicate_shape, 'selection','shape'),                            
                rp = "SW")              
    #>Color -------------------------------------------------------------------------------------------------
    uiColorShape = mc.menuItem(parent = uiShape, l='Color*', subMenu=True)
    
    for ctxt in ['selection','children','heirarchy','scene']:
        uiContext = mc.menuItem(p=uiColorShape, l=ctxt,subMenu=True)    

        uiColorIndexShape = mc.menuItem(p=uiContext,l='Index', subMenu=True)
        _IndexKeys = SHARED._d_colorsByIndexSets.keys()
        
        for k1 in _IndexKeys:
            _keys2 = SHARED._d_colorsByIndexSets.get(k1,[])
            _sub = False
    
            mc.menuItem(parent=uiColorIndexShape,subMenu = True,
                        en = True,
                        l=k1)
    
            for k2 in _keys2:
                mc.menuItem(en = True,
                            l=k2,
                            c=cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_index[k2],ctxt,'shape'))                        
    
    
        uiRGBShape = mc.menuItem(parent = uiContext, l='RBG', subMenu=True)            
        _IndexKeys = SHARED._d_colorSetsRGB.keys()
        for k1 in _IndexKeys:
            _keys2 = SHARED._d_colorSetsRGB.get(k1,[])
            _sub = False
            if _keys2:_sub = True
    
            mc.menuItem(parent=uiRGBShape,subMenu = _sub,
                        en = True,
                        l=k1,
                        c=cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[k1],ctxt,'shape'))
    
            if _sub:
                mc.menuItem(en = True,
                            l=k1,
                            c=cgmGen.Callback(MMCONTEXT.color_override,k1,ctxt,'shape'))                    
                for k2 in _keys2:
                    _buffer = "{0}{1}".format(k1,k2)
                    mc.menuItem(en = True,
                                l=_buffer,
                                c=cgmGen.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[_buffer],ctxt,'shape'))              


def uiSection_mesh(parent):
    _str_func = 'uiSection_mesh'  
    
    uiMesh = mc.menuItem(parent = parent, l='Mesh', subMenu=True,tearOff = True)
    mc.menuItem(parent = uiMesh,
                l='cgmMeshTools',
                c=cgmGen.Callback(meshTools.run))                                 
        #c=lambda *a: meshTools.run())         
    mc.menuItem(parent = uiMesh,
                l='abSym',
                c=lambda *a: mel.eval('abSymMesh'),)
    
    
def uiSection_skin(parent):
    _str_func = 'uiSection_skin'  
    
    uiSkin = mc.menuItem(parent = parent, l='Skin', subMenu=True)
    mc.menuItem(parent = uiSkin,
                l='abWeight',
                c=lambda *a: mel.eval('abWeightLifter'),)         
    mc.menuItem(parent = uiSkin,
                l='ngSkin',
                en=False,
                c=lambda *a: mel.eval('cometJointOrient'),) 
    
def uiSection_attributes(parent):
    _str_func = 'uiSection_attributes'  
    
    uiAttr = mc.menuItem(parent = parent, l='attributes', subMenu=True, tearOff = True)
    mc.menuItem(parent = uiAttr,
                l='attrTools',
                c=cgmGen.Callback(ATTRTOOLS.ui))   
    
    
    _add = mc.menuItem(parent=uiAttr,subMenu=True,
                       l='Add',
                       rp='S') 
    _d_attrTypes = {"string":'E','float':'S','enum':'NE','vector':'SW','int':'W','bool':'NW','message':'SE'}
    for _t,_d in _d_attrTypes.iteritems():
        mc.menuItem(parent=_add,
                    l=_t,
                    c = cgmGen.Callback(ATTRTOOLS.uiPrompt_addAttr,_t,**{'autoLoadFail':True}),
                    rp=_d)      

    
def uiSection_nodes(parent):
    _str_func = 'uiSection_nodes'  
    
    uiNodes = mc.menuItem(parent = parent, l='Nodes', subMenu=True)

    _uic_nodes = mc.menuItem(parent = uiNodes,subMenu=True,
                             l='Create',
                             )               
    for n in SHARED._d_node_to_suffix.keys():
        mc.menuItem(parent = _uic_nodes,
                    l=n,
                    c=cgmGen.Callback(NODES.create,'NameMe',n),                   
                    )                  