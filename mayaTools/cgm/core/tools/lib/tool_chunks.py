"""
------------------------------------------
tool_chunks: cgm.core.tools.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__version__ = '0.1.11222017'

import webbrowser
import copy

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc
import maya
import maya.mel as mel

import Red9

from cgm.lib.zoo.zooPyMaya import xferAnimUI

from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import rigging_utils as RIGGING
import cgm.core.rig.constraint_utils as RIGCONSTRAINTS
#reload(RIGGING)
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.lib.rayCaster as RAYS
import cgm.core.lib.locator_utils as LOC
from cgm.core.tools import meshTools
reload(meshTools)
from cgm.core.lib import node_utils as NODES
import cgm.core.lib.sdk_utils as SDK
reload(SDK)
import cgm.core.tools.lib.tool_calls as TOOLCALLS
reload(TOOLCALLS)
import cgm.core.classes.GuiFactory as cgmUI
import cgm.projects.CGM as CGMPROJECTS
from cgm.core.tools import attrTools as ATTRTOOLS
reload(ATTRTOOLS)

from cgm.core.tools import locinator as LOCINATOR
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI
import cgm.core.tools.lib.annotations as TOOLANNO
import cgm.core.tools.updateTool as CGMUPDATE
reload(CGMUPDATE)
from cgm.core.lib import attribute_utils as ATTRS
from cgm.core.classes import HotkeyFactory as HKEY
from cgm.core.tools.lib import snap_calls as UISNAPCALLS
reload(UISNAPCALLS)
import cgm.core.lib.arrange_utils as ARRANGE
import cgm.core.tools.lightLoomLite as LIGHTLOOMLITE
reload(LIGHTLOOMLITE)
import cgm.core.rig.joint_utils as JOINTS
from cgm.core.lib.ml_tools import (ml_breakdownDragger,
                                   ml_breakdown,
                                   ml_resetChannels,
                                   ml_deleteKey,
                                   ml_setKey,
                                   ml_hold,
                                   ml_stopwatch,
                                   ml_arcTracer,
                                   ml_convertRotationOrder,
                                   ml_copyAnim)


_2016 = False
if cgmGEN.__mayaVersion__ >=2016:
    _2016 = True
    
def uiSection_help(parent):
    _str_func = 'uiSection_help'  
    
    mc.menuItem(parent = parent,
                    l='Check for updates',
                    ann = "Check your local cgm branch for updates...",
                    c=lambda *a: mc.evalDeferred(CGMUPDATE.checkBranch,lp=True))
    mc.menuItem(parent = parent,
                l='cgmUpdateTool',
                ann = "Get Tool Updates",
                c=lambda *a: mc.evalDeferred(TOOLCALLS.cgmUpdateTool,lp=True))
    
    mc.menuItem(parent = parent,
                l='CGM Docs',
                ann = "Find help for various tools",
                c=lambda *a: webbrowser.open("http://docs.cgmonks.com"))  
    
    mc.menuItem(parent = parent,
                l='Report issue',
                ann = "Load a browser page to report a bug",
                c=lambda *a: webbrowser.open("https://github.com/jjburton/cgmTools/issues/new"))    
    mc.menuItem(parent = parent,
                l='Get Builds',
                ann = "Get the latest builds of cgmTools from bitBucket",
                c=lambda *a: webbrowser.open("https://github.com/jjburton/cgmTools")) 
    _vids = mc.menuItem(parent = parent,subMenu = True,
                        l='Videos')
    
    mc.menuItem(parent = _vids,
                l='cgm',
                ann = "CG Monks Vimeo Channel",
                c=lambda *a: webbrowser.open("http://vimeo.com/cgmonks"))     
    mc.menuItem(parent = _vids,
                l='Red9',
                ann = "Red 9 Vimeo Channel",
                c=lambda *a: webbrowser.open("http://vimeo.com/user9491246"))    
   
    mc.menuItem(parent = parent,
                l='Coding questions',
                ann = "Get help on stack overflow for your coding questions",
                c=lambda *a: webbrowser.open("http://stackoverflow.com"))          
    mc.menuItem(parent = parent,
                l='Enviornment Info',
                ann = "Get your maya/os enviorment info. Useful for bug reporting to tool makers",
                c=lambda *a: cgmGEN.report_enviornment())
        
def uiSection_selection(parent = None):
    uiSelect = mc.menuItem(parent = parent, l='Select*', subMenu=True,tearOff = True)
    
    for s in ['selection','children','heirarchy','scene']:
        mc.menuItem(p=uiSelect, l=s,
                    ann = "Select all items matching specifiec type in  {0}".format(s),                    
                    subMenu=True)

        mc.menuItem(l='Joints', subMenu = False,
                    ann = "Select all joints in {0}".format(s),
                    c=cgmGEN.Callback(MMCONTEXT.select,s,'joint'))
        mc.menuItem(l='Curves', subMenu = False,
                    ann = "Select all curves in {0}".format(s),                    
                    c=cgmGEN.Callback(MMCONTEXT.select,s,'nurbsCurve'))
        mc.menuItem(l='Mesh', subMenu = False,
                    ann = "Select all mesh in {0}".format(s),                    
                    c=cgmGEN.Callback(MMCONTEXT.select,s,'mesh'))        
        mc.menuItem(l='Surface', subMenu = False,
                    ann = "Select all surfaces in {0}".format(s),                    
                    c=cgmGEN.Callback(MMCONTEXT.select,s,'nurbsSurface'))   
    
    return uiSelect

def uiSection_arrange(parent = None, selection = None, pairSelected = True):
    #>>Arrange ----------------------------------------------------------------------------------------
    _arrange= mc.menuItem(parent=parent,subMenu = True,
                          l = 'Arrange',
                          ann = "Ordered layout of selected items")    
    
    mc.menuItem(parent=_arrange,
              l = 'Linear[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('linearEven'))
    mc.menuItem(parent=_arrange,
                l = 'Linear[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('linearSpaced'))
    
    #mUI.MelMenuItemDiv(_arrange)        

    mc.menuItem(parent=_arrange,
              l = 'Curve[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubic'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicEven'))
    mc.menuItem(parent=_arrange,
              l = 'Arc[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicArc'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicArcEven'))
    mc.menuItem(parent=_arrange,
              l = 'Arc[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced','curve':'cubicArc'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicArcSpaced'))    
    
    #mUI.MelMenuItemDiv(_arrange)        
    mc.menuItem(parent=_arrange,
              l = '2[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicRebuild','spans':2}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild2Even'))
    mc.menuItem(parent=_arrange,
              l = '2[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'spaced','curve':'cubicRebuild','spans':2}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild2Spaced'))
    mc.menuItem(parent=_arrange,
              l = '3[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicRebuild','spans':2}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild3Even'))
    mc.menuItem(parent=_arrange,
              l = '3[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine', **{'mode':'even','curve':'cubicRebuild','spans':3}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild3Spaced'))    

def uiSection_distance(parent = None, selection = None, pairSelected = True):
    _p = mc.menuItem(parent=parent, subMenu = True,tearOff = True,
                     ann = 'Get info on distance',
                     l = 'Distance')  

    #if pairSelected:     
    _n = mc.menuItem(parent=_p, subMenu = True,
                     l = 'Near')
    _f = mc.menuItem(parent=_p, subMenu = True,
                     l = 'Far')

    mc.menuItem(parent=_n, 
                l = 'Target',
                ann = "Find nearest target in from:to selection list",
                c = cgmGEN.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Near Target',True,**{'mode':'closest','resMode':'object'}),                                                                      
                )   
    mc.menuItem(parent=_n, 
                l = 'Shape',
                ann = "Find nearest shape in  from:to selection list",                    
                c = cgmGEN.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Near Shape',True,**{'mode':'closest','resMode':'shape'}),                                                                      
                )               
    mc.menuItem(parent=_n, 
                l = 'Surface Point',
                ann = "Find nearest surface point in from:to selection list",                    
                c = cgmGEN.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Near point on surface',True,**{'mode':'closest','resMode':'pointOnSurface'}),                                                                      
                )     
    mc.menuItem(parent=_n, 
                l = 'Surface Loc',
                ann = "Find nearest surface point in from:to selection list. And loc it.",                                        
                c = cgmGEN.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Near point on surface',True,**{'mode':'closest','resMode':'pointOnSurfaceLoc'}),                                                                      
                )               
    mc.menuItem(parent=_n,
                l = 'Surface Nodes',
                ann = "Create nearest surface point nodes in from:to selection list",                                        
                c = cgmGEN.Callback(MMCONTEXT.func_process, DIST.create_closest_point_node, selection,'firstToEach','Create closest Point Node',True,**{}),                                                                      
                )                 



    mc.menuItem(parent=_f, 
                l = 'Target',
                ann = "Find furthest taregt in from:to selection list",                                        
                c = cgmGEN.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Far Target',True,**{'mode':'far','resMode':'object'}),                                                                      
                )                  
    mc.menuItem(parent=_f, 
                l = 'Shape',
                ann = "Find furthest shape in from:to selection list",                                        
                c = cgmGEN.Callback(MMCONTEXT.func_process, DIST.get_by_dist, selection,'firstToRest','Far Shape',True,**{'mode':'far','resMode':'shape'}),                                                                      
                )      
    return _p


    
def uiSection_joints(parent = None):
    uiJoints = mc.menuItem(parent = parent, l='Joints', subMenu=True, tearOff = True)

    _axis = mc.menuItem(l='Axis', subMenu = True)
    
    for ctxt in ['selection','children','heirarchy','scene']:
            mc.menuItem(p=_axis, l=ctxt,subMenu=True)
            mc.menuItem(l='Show',
                        ann = "Show axis for all joints in {0}".format(ctxt),                        
                        c=cgmGEN.Callback(MMCONTEXT.set_attrs,None,'displayLocalAxis',1,ctxt,'joint'))
        
            mc.menuItem(l='Hide',
                        ann = "Hide axis for all joints in {0}".format(ctxt),                                                
                        c=cgmGEN.Callback(MMCONTEXT.set_attrs,None,'displayLocalAxis',0,ctxt,'joint'))
            
    mc.menuItem(parent = uiJoints,
                l='cgmJointTools',
                c=lambda *a: TOOLCALLS.jointTools(),
                ann="Our joint tools")
    mc.menuItem(parent = uiJoints,
                l='cometJO',
                c=lambda *a: mel.eval('cometJointOrient'),
                ann="General Joint orientation tool  by Michael Comet")
    mc.menuItem(parent=uiJoints, 
                l = 'Freeze Orient',
                ann = "Freeze the joint orientation",                                        
                c = cgmGEN.Callback(MMCONTEXT.func_process, None, JOINTS.freezeOrientation, 'each','FreezeOrientation',True,**{}),                                                                      
                )    
    
    
    
def uiSection_sdk(parent = None):
    _str_func = 'uiSection_sdk'
    uiSDK = mc.menuItem(parent = parent, l='SDK',tearOff =True,
                        ann = "Functions and tools for dealing with SDKs",                                                                                                                          
                        subMenu=True)
    
    mc.menuItem(parent = uiSDK,
                l='Get Driven',
                ann = "Get driven objects from a sdk driver",                                                        
                c=lambda *a:SDK.get_driven(None,getPlug=False))
    mc.menuItem(parent = uiSDK,
                l='Get Driven Plugs',
                ann = "Get driven plugs from a sdk driver",                                                        
                c=lambda *a:SDK.get_driven(None,getPlug=True))
    mc.menuItem(parent = uiSDK,
                l='Get Driver',
                ann = "Get driver objects from a sdk driver",                                                        
                c=lambda *a:SDK.get_driver(None,getPlug=False))
    mc.menuItem(parent = uiSDK,
                l='Get Driver Plugs',
                ann = "Get driver plugs from a sdk driver",                                                        
                c=lambda *a:SDK.get_driver(None,getPlug=True))
    
    
    mc.menuItem(parent = uiSDK,
                l='seShapeTaper',
                ann = "Fantastic blendtaper like tool for sdk poses by our pal - Scott Englert",                                                        
                c=lambda *a: mel.eval('seShapeTaper'),)   
    
    
def uiSection_curves(parent, selection = None):
    uiCurve = mc.menuItem(parent = parent, l='Curve',
                          ann = "Functions and tools for dealing with curves",                                                                                                  
                          subMenu=True)
    
    mc.menuItem(parent=uiCurve,
                l = 'Describe',
                ann = "Generate pythonic recreation calls for selected curve shapes", 
                c = cgmGEN.Callback(MMCONTEXT.func_process, CURVES.get_python_call, selection, 'all','describe'),                
                )   
    

    mc.menuItem(parent=uiCurve,
                en=False,
                l = 'Mirror')  
    

def uiSection_controlCurves(parent, selection = None):
    var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
    var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
    var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
    var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)

    uiCurve = mc.menuItem(parent = parent, l='Control Curves',
                          ann = "Functions and tools for dealing with curves",                                                                                                  
                          subMenu=True)
    

    mc.menuItem(parent=uiCurve,
                l='Create Control Curve',
                c=cgmGEN.Callback(uiFunc_createCurve),
                ann='Create control curves from stored optionVars. Shape: {0} | Color: {1} | Direction: {2}'.format(var_curveCreateType.value,
                                                                                                                    var_defaultCreateColor.value,
                                                                                                                    SHARED._l_axis_by_string[var_createAimAxis.value]))                    
    mc.menuItem(parent=uiCurve,
                l='One of each',
                c=cgmGEN.Callback(uiFunc_createOneOfEach),                
                #c=lambda *a:TOOLBOX.uiFunc_createOneOfEach(),
                ann='Create one of each curve stored in cgm libraries. Size: {0} '.format(var_createSizeValue.value) )       
    
    mc.menuItem(parent = uiCurve, l = '_______________________')
    mc.menuItem(parent=uiCurve,
                l = 'Make resizeObj',
                ann = 'Make control a resize object so you can more easily shape it',                
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_controlResizeObj, None,'each','Resize obj'))        
    mc.menuItem(parent=uiCurve,
                l = 'Push resizeObj changes',
                ann = 'Push the control changes back to control',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.push_controlResizeObj, None,'each','Resize obj'))        
    mc.menuItem(parent=uiCurve,
                l = 'Mirror World Space To target',
                ann = 'Given a selection of two curves, mirror across X (for now only x)',
                c = cgmGEN.Callback(CURVES.mirror_worldSpace))        
    mc.menuItem(parent=uiCurve,
                en=False,
                l = 'Mirror')  
    

def uiSection_shapes(parent = None, selection = None, pairSelected = True):
    _str_func = 'uiSection_shapes'    
    
    #>>>Shape ==============================================================================================
    uiShape = mc.menuItem(parent = parent, l='Shape', subMenu=True,
                          ann = "Functions and tools for dealing with shapes",                                                                                                                            
                          tearOff = True)


    #---------------------------------------------------------------------------
    mc.menuItem(parent=uiShape,
                #en = pairSelected,
                l = 'shapeParent',
                ann = "shapeParent in place with a from:to selection. Maya's version is not so good",                                                                                                  
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.shapeParent_in_place, selection, 'lastFromRest','shapeParent'),
                rp = "W")   
    _d_combine = {'keepSource':False}
    mc.menuItem(parent=uiShape,
                #en = pairSelected,                
                l = 'Combine',
                ann = "Combine selected curves to the last transform",  
                #c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.shapeParent_in_place, selection, 'eachToLast','Combine',**{'keepSource':False}),                
                c = cgmGEN.Callback(MMCONTEXT.func_enumrate_all_to_last, RIGGING.shapeParent_in_place, selection,'toFrom', **_d_combine),
                rp = "NW")
    mc.menuItem(parent=uiShape,
                #en = pairSelected,                
                l = 'Add',
                ann = "Add selected shapes to the last transform",                                                                                                  
                c = cgmGEN.Callback(MMCONTEXT.func_enumrate_all_to_last, RIGGING.shapeParent_in_place, selection,'toFrom', **{}),
                rp = "NW")      

    mc.menuItem(parent=uiShape,
                l = 'Replace',
                ann = "Replace the last transforms shapes with the former ones.",                                                                                                                  
                c = cgmGEN.Callback(MMCONTEXT.func_process,
                                    RIGGING.shapeParent_in_place,
                                    selection,'lastFromRest', 'replaceShapes',
                                    **{'replaceShapes':True}),                                                        
                #c = cgmGEN.Callback(MMCONTEXT.func_all_to_last, RIGGING.shapeParent_in_place, selection,'toFrom', **_d_replace),                            
                rp = "SW")                  

    mc.menuItem(parent=uiShape,
                l = 'Extract',
                ann = "Extract selected shapes from their respective transforms",                                                                                                                                  
                c = cgmGEN.Callback(MMCONTEXT.func_context_all, RIGGING.duplicate_shape, 'selection','shape'),                            
                rp = "SW")              
    #>Color -------------------------------------------------------------------------------------------------
    uiColorShape = mc.menuItem(parent = uiShape, l='Color', 
                               ann = "Set overrideColor...",                                                                                       
                               subMenu=True)
    
    for ctxt in ['selection','children','heirarchy','scene']:
        uiContext = mc.menuItem(p=uiColorShape,
                                ann = "Set overrideColor by {0}".format(ctxt),                                                        
                                l=ctxt,subMenu=True)    

        uiColorIndexShape = mc.menuItem(p=uiContext,l='Index',                                         
                                        ann = "Set overrideColor by {0} by index".format(ctxt),                                                        
                                        subMenu=True)
        _IndexKeys = SHARED._d_colorsByIndexSets.keys()
        
        for k1 in _IndexKeys:
            _keys2 = SHARED._d_colorsByIndexSets.get(k1,[])
            _sub = False
    
            mc.menuItem(parent=uiColorIndexShape,subMenu = True,
                        en = True,
                        ann = "Set overrideColor by {0} to {1}...".format(ctxt,k1),                                                                                
                        l=k1)
    
            for k2 in _keys2:
                mc.menuItem(en = True,
                            l=k2,
                            ann = "Set overrideColor by {0} to {1}".format(ctxt,k2),                                                                                                            
                            c=cgmGEN.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_index[k2],ctxt,'shape'))                        
    
            
        uiRGBShape = mc.menuItem(parent = uiContext,
                                 en = _2016,
                                 ann = "Set overrideColor by {0} -- 2016 or above only".format(ctxt),                                                                                         
                                 l='RBG', subMenu=True)   
        
        _IndexKeys = SHARED._d_colorSetsRGB.keys()
        for k1 in _IndexKeys:
            _keys2 = SHARED._d_colorSetsRGB.get(k1,[])
            _sub = False
            if _keys2:_sub = True
    
            mc.menuItem(parent=uiRGBShape,subMenu = _sub,
                        en = True,
                        ann = "Set overrideColor by {0} to {1}...".format(ctxt,k1),                                                                                                        
                        l=k1,
                        c=cgmGEN.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[k1],ctxt,'shape'))
    
            if _sub:
                mc.menuItem(en = True,
                            l=k1,
                            c=cgmGEN.Callback(MMCONTEXT.color_override,k1,ctxt,'shape'))                    
                for k2 in _keys2:
                    _buffer = "{0}{1}".format(k1,k2)
                    mc.menuItem(en = True,
                                ann = "Set overrideColor by {0} to {1}".format(ctxt,k2),                                                                                                                                            
                                l=_buffer,
                                c=cgmGEN.Callback(MMCONTEXT.color_override,SHARED._d_colors_to_RGB[_buffer],ctxt,'shape'))              


def uiSection_mesh(parent):
    _str_func = 'uiSection_mesh'  
    
    uiMesh = mc.menuItem(parent = parent, l='Mesh', subMenu=True,tearOff = True)
    mc.menuItem(parent = uiMesh,
                l='cgmMeshTools',
                ann = "Launch cgmMeshTools - a series of tools including meshMath, shapeCasting and proxyMesh",                                                                                                       
                c=cgmGEN.Callback(meshTools.run))                                 
        #c=lambda *a: meshTools.run())         
    mc.menuItem(parent = uiMesh,
                l='abSym',
                ann = "abSymMesh by Brendan Ross - fantastic tool for some blendshape work",                                                                                                       
                c=lambda *a: mel.eval('abSymMesh'),)
    mc.menuItem(parent = uiMesh,
                l='abTwoFace',
                ann = "abTwoFace by Brendan Ross - fantastic tool for splitting blendshapes",                                                                                                       
                c=lambda *a: mel.eval('abTwoFace'),)    
    
def uiSection_skin(parent):
    _str_func = 'uiSection_skin'  
    
    uiSkin = mc.menuItem(parent = parent, l='Skin', subMenu=True)
    mc.menuItem(parent = uiSkin,
                l='abWeightLifter',
                ann = "abWeightLifter by Brendan Ross - really good tool for transferring and working with skin data",                                                                                                                       
                c=lambda *a: mel.eval('abWeightLifter'),)         
    mc.menuItem(parent = uiSkin,
                l='ngSkin',
                c=lambda *a: TOOLCALLS.ngskin()) 
    
def uiSection_attributes(parent):
    _str_func = 'uiSection_attributes'  
    
    uiAttr = mc.menuItem(parent = parent, l='Attributes', subMenu=True,
                         ann = "Function and tools for working with attributes",                                                                                                                                
                         tearOff = True)
    mc.menuItem(parent = uiAttr,
                l='cgmAttrTools',
                ann = "Launch cgmAttrTools - Collection of tools for making creating, editing and managing attributes a little less painful",                                                                                                                       
                c=cgmGEN.Callback(TOOLCALLS.attrTools))   
    
    
    _add = mc.menuItem(parent=uiAttr,subMenu=True,
                       l='Add',
                       ann = "Add attributes to selected objects...",                                                                                                                              
                       rp='S') 
    _d_attrTypes = {"string":'E','float':'S','enum':'NE','vector':'SW','int':'W','bool':'NW','message':'SE'}
    for _t,_d in _d_attrTypes.iteritems():
        mc.menuItem(parent=_add,
                    l=_t,
                    ann = "Add a {0} attribute(s) to the selected objects".format(_t),                                                                                                       
                    c = cgmGEN.Callback(ATTRTOOLS.uiPrompt_addAttr,_t,**{'autoLoadFail':True}),
                    rp=_d)
        
    mc.menuItem(parent=uiAttr, #subMenu = True,
                l = 'Compare Attrs',
                ann = "Compare the attributes of selected objects. First object is the base of comparison",                                                                                                                                                
                c = cgmGEN.Callback(MMCONTEXT.func_process, ATTRS.compare_attrs, None, 'firstToRest','Compare Attrs',True,**{}))           

    
def uiSection_nodes(parent):
    _str_func = 'uiSection_nodes'  
    
    uiNodes = mc.menuItem(parent = parent, l='Nodes', subMenu=True)

    _uic_nodes = mc.menuItem(parent = uiNodes,subMenu=True,
                             l='Create',
                             )               
    for n in SHARED._d_node_to_suffix.keys():
        mc.menuItem(parent = _uic_nodes,
                    l=n,
                    c=cgmGEN.Callback(NODES.create,'NameMe',n),                   
                    )
        
def uiSection_animUtils(parent):
    _str_func = 'uiSection_animUtils'  
    mc.menuItem(parent = parent,
                l='cgmLocinator',
                ann = "Launch cgmLocinator - a tool for aiding in the snapping of things",
                c=lambda *a: TOOLCALLS.locinator()) 
    mc.menuItem(parent = parent,
                l='cgmDynParentTool',
                ann = "Launch cgm's dynParent Tool - a tool for assisting space switching setups and more",
                c=lambda *a: TOOLCALLS.dynParentTool())   
    mc.menuItem(parent = parent,
                l='cgmSetTools',
                ann = "Launch cgm's setTools - a tool for managing maya selection sets",
                c=lambda *a: TOOLCALLS.setTools())
    mc.menuItem(parent = parent,
                l='cgmSnapTools',
                ann = "Launch cgmSnapTools - a tool for snapping things around in maya",
                c=lambda *a: TOOLCALLS.cgmSnapTools())
    mc.menuItem(parent = parent,
                l='cgmMocapBakeTool',
                ann = "Mocap Bake Tool - A tool for retargeting and baking control transforms from an animated source",
                c=lambda *a:TOOLCALLS.mocapBakeTool())    
    
    mc.menuItem(parent = parent,
                l='mlBreakdown',
                ann = "mlBreakdown by Morgan Loomis",
                c=lambda *a: ml_breakdown.ui())
    mc.menuItem(parent = parent,
                l='mlHold',
                ann = "mlHold by Morgan Loomis",
                c=lambda *a: ml_hold.ui())
    mc.menuItem(parent = parent,
                l='mlArcTracer',
                ann = "mlArcTracer by Morgan Loomis",
                c=lambda *a: ml_arcTracer.ui())         
    mc.menuItem(parent = parent,
                l='mlCopyAnim',
                ann = "mlCopyAnim by Morgan Loomis",
                c=lambda *a: ml_copyAnim.ui())

    
    mc.menuItem(parent = parent,
            l='autoTangent',
            ann = "autoTangent by Michael Comet - an oldie but a goodie for those who loathe the graph editor",
            c=lambda *a: mel.eval('autoTangent'))
    mc.menuItem(parent = parent,
                l='tweenMachine',
                ann = "tweenMachine by Justin Barrett - Fun little tweening tool",
                c=lambda *a: mel.eval('tweenMachine'))
    

    mc.menuItem(parent = parent,
                l='red9.Studio Tools',
                ann = "Launch Red 9's tools",
                c=lambda *a:Red9.start())     
    mc.menuItem(parent = parent,
                l='zoo.XferAnim',
                ann = "Tool for transferring animation - from Hamish McKenzie's zooToolbox",
                c=lambda *a:xferAnimUI.XferAnimWindow()) 
    mc.menuItem(parent = parent,
                l='zoo.Keymaster',
                ann = "from Hamish McKenzie's zooToolbox - keymaster gives you a heap of tools to manipulate keyframes - scaling around curve pivots, min/max scaling of curves/keys etc...",
                c=lambda *a: mel.eval('source zooKeymaster; zooKeymasterWin;'))    

def uiSection_layout(parent):
    _str_func = 'uiSection_layout'  
    
    mc.menuItem(parent = parent,
                l='zoo.Shots',
                ann = "from Hamish McKenzie's zooToolbox -  zooShots is a camera management tool.  It lets you create a bunch of cameras in your scene, and 'edit' them together in time.  The master camera then cuts between each 'shot' camera.  All camera attributes are maintained over the cut - focal length, clipping planes, fstop etc...",
                c=lambda *a: mel.eval('zooShots'))
    mc.menuItem(parent = parent,
            l='zoo.HUDCtrl',
            ann = "from Hamish McKenzie's zooToolbox -  zooHUDCtrl lets you easily add stuff to your viewport HUD.",
            c=lambda *a: mel.eval('zooHUDCtrl'))

def uiSection_mrs(parent):
    _str_func = 'uiSection_layout'  
    
    mc.menuItem(parent = parent,
                l='mrsAnimate',
                ann = "WIP",
                c=lambda *a:TOOLCALLS.mrsANIMATE())
                
    mc.menuItem(parent = parent,
                l='mrsBuilder',
                ann = "WIP",
                c=lambda *a:TOOLCALLS.mrsUI())
    mc.menuItem(parent = parent,
                l='MRS Documentation',
                ann = "Access to MRS Docmenation || Subscription required.",
                c=lambda *a: webbrowser.open("https://www.cgmonastery.com/teams/mrs-collaborative/documentation/"))      

    
def uiSection_hotkeys(parent):
    _str_func = 'uiSection_hotkeys'  
    
    mc.menuItem(parent = parent,
                    l='cgmMarkingMenu',
                    ann = "Setup the cgmMarking Menu",
                    c=cgmGEN.Callback(HKEY.cgmHotkeyer, 'cgmMM_tool',  'cgmMarkingMenu;', 'cgmMarkingMenuKillUI;','Marking menu for working with rigging tools', 'mel','s'))          
    
    mc.menuItem(parent = parent,
                l='zoo.Tangent Works',
                ann = "zooTangentWks is a marking menu script that provides super fast access to common tangent based operations.  Tangent tightening, sharpening, change tangent types, changing default tangents etc...",
                c=cgmGEN.Callback(HKEY.cgmHotkeyer, 'zooTangentWks',  'zooTangentWks;', 'zooTangentWksKillUI;','tangent works is a marking menu script to speed up working with the graph editor','mel','q'))    

    mc.menuItem(parent = parent,
                l='Reset ALL hotkeys',
                ann = "Reset ALL hotkeys back to maya default",
                c=cgmGEN.Callback(HKEY.hotkeys_resetAll))     
    

from cgm.lib import optionVars
from cgm.core.lib.wing import mayaWingServer as mWingServer
from cgm.lib import cgmDeveloperLib
from cgm.core.tests import cgmMeta_test as testCGM
import cgm.core.tests.cgmTests as CGMTEST
reload(CGMTEST)

def loadLocalPython():
    mel.eval('python("import cgm.core;cgm.core._reload();import cgm.core.cgm_Meta as cgmMeta;import cgm.core.cgm_Deformers as cgmDeformers;import cgm.core.cgm_General as cgmGen;import cgm.core.cgm_PuppetMeta as cgmPM;import cgm.core.cgm_RigMeta as cgmRigMeta;import Red9.core.Red9_Meta as r9Meta;import maya.cmds as mc;import cgm.core.cgmPy.validateArgs as VALID")')

def load_MorpheusMaker( *a ):
    try:
        print("Trying to load Morheus Maker 2014")
        from morpheusRig_v2.core.tools import MorpheusMaker as mMaker
        reload(mMaker)    
        mMaker.go()	
    except Exception,error:
        log.error("You appear to be missing the Morpheus pack. Or maybe angered the spirits...")
        raise Exception,error
    
def uiSection_dev(parent):
    _str_func = 'uiSection_dev' 
    
    mc.menuItem(parent = parent,
                l='Purge Option Vars',
                ann = "Purge all cgm option vars. Warning will break any open tools",
                c=lambda *a: optionVars.purgeCGM())
    
    mc.menuItem(parent = parent,
                l='Connect to Wing IDE',
                ann = "Attempts to connect to Wing IDE",
                c=lambda *a:cgmDeveloperLib.connectToWing())      
    mc.menuItem(parent = parent,
                l='Start Wing Server',
                ann = "Opens a command port for Wing IDE",
                c=lambda *a: mWingServer.startServer())
    
    mc.menuItem(parent = parent,
                l='Load Local CGM Python',
                ann = "Sets up standard cgm ptyhon imports for use in the script editor",
                c=lambda *a: loadLocalPython())
    mc.menuItem(parent = parent,
                l='Load Morpheus Maker',
                ann = "Attempt to load the Morpheus Maker - ALPHA",
                c=lambda *a: load_MorpheusMaker())    
    
    
    
    _unitTests = mc.menuItem(parent = parent,subMenu = True,tearOff = True,
                             l='Unittesting')
    
    
    
    mc.menuItem(parent = _unitTests,
                l='cgm - All',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=cgmGEN.Callback(ut_cgmTestCall))   
    mc.menuItem(parent = _unitTests,
                l='cgm - All (Debug)',
                ann = "Only reports tests to run",
                c=cgmGEN.Callback(ut_cgmTestCall,'all', **{'testCheck':True}))   
    

    _test = mc.menuItem(parent = _unitTests,subMenu = True,tearOff = True,
                        l='Test Modules') 
    _testCheck = mc.menuItem(parent = _unitTests,subMenu = True,tearOff = True,
                             l='Debug Modules')      
    
    """
    mc.menuItem(parent = _unitTests,
                l='cgm - All (Test Check)',
                ann = "Only reports tests to wrun",
                c=lambda *a: ut_cgmTestCall('all',testCheck = True))      
    mc.menuItem(parent = _unitTests,
                l='cgm - All',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=lambda *a: ut_cgmTestCall())    
    mc.menuItem(parent = _unitTests,
                l='cgm - Core',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=lambda *a: ut_cgmTestCall('coreLib'))    
    mc.menuItem(parent = _unitTests,
                l='cgm - Meta',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=lambda *a: ut_cgmTestCall('cgmMeta'))   
    mc.menuItem(parent = _unitTests,
                l='cgm - mClasses',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=lambda *a: ut_cgmTestCall('mClasses'))     """
    
    for m,l in CGMTEST._d_modules.iteritems():
        _mCheck = mc.menuItem(parent = _testCheck,subMenu = True,tearOff = True,
                              l='Debug ' + m)   
        _mTest = mc.menuItem(parent = _test,subMenu = True,tearOff = True,
                             l='Test ' + m)   
        for t in ['all'] + l:
            _t = t
            if t == 'all':
                _t = m
            mc.menuItem(parent = _mCheck,
                        l=t,
                        ann = "TEST LIST ONLY - {0} | {1}".format(m,t),
                        c=cgmGEN.Callback(ut_cgmTestCall,_t, **{'testCheck':True}))   
                        
                        #c=lambda *a: ut_cgmTestCall(_t, testCheck = True))   
            mc.menuItem(parent = _mTest,
                        l=t,
                        ann = "WARNING - Opens new file.... Test: {0} | {1}".format(m,t),
                        c=cgmGEN.Callback(ut_cgmTestCall,_t, **{'testCheck':False}))   
    
    mc.menuItem(parent = _unitTests, l = '----------------')
    
    mc.menuItem(parent = _unitTests,
                l='OLD - All',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=lambda *a: ut_allOLD())
    mc.menuItem(parent = _unitTests,
                l='OLD - meta only',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=lambda *a: ut_metaOLD()) 
    mc.menuItem(parent = _unitTests,
                l='OLD - puppet',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=lambda *a: ut_puppetOLD()) 
    mc.menuItem(parent = _unitTests,
                l='OLD - limb',
                ann = "WARNING - Opens new file...Unit test cgm.core",
                c=lambda *a: ut_limbOLD()) 
    
    #Capture ------------------------------------------
    _screenGrab = mc.menuItem(parent = parent,subMenu = True,tearOff = True,
                             l='Screen grab Mode')
    mc.menuItem(parent = _screenGrab,
                l='Off',
                c=lambda *a: CGMPROJECTS.setup_forCapture(0))    
    mc.menuItem(parent = _screenGrab,
                l='On',
                c=lambda *a: CGMPROJECTS.setup_forCapture(1))
    
def ut_cgmTestCall(*args,**kws):
    import cgm.core.tests.cgmTests as cgmTests
    reload(cgmTests)
    cgmTests.main(*args,**kws)    

def ut_allOLD():
    reload(testCGM)
    testCGM.ut_AllTheThings()
def ut_metaOLD():
    reload(testCGM)
    testCGM.ut_cgmMeta()
def ut_puppetOLD():
    reload(testCGM)
    testCGM.ut_cgmPuppet()
def ut_limbOLD():
    reload(testCGM)
    testCGM.ut_cgmLimb()
    
def uiSection_createFromSel(parent, selection = None):
    _str_func = 'uiSection_createFromSel'  
    
    mc.menuItem(parent=parent,
                    l = 'Null',
                    ann='Create a null at the selected component or transform',
                    c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'each','Create Tranform',**{'create':'null'}))        
    mc.menuItem(parent=parent,
                    l = 'Null [ mid ]',
                    ann='Create a null at the selected component or transform midpoint',                    
                    c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Tranform at mid',**{'create':'null','midPoint':'True'}))    
    
    
    mc.menuItem(parent=parent,
                l = 'Joint',
                ann='Create a joint at the selected component or transform',                
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_joint_at, None,'each','Create Joint'))
    mc.menuItem(parent=parent,
                l = 'Joint [ mid ]',
                ann='Create a joint at the selected component or transform midpoint',                                
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Joint at mid',**{'create':'joint','midPoint':'True'}))         
    
    mc.menuItem(parent=parent,
                l = 'Locator',
                ann='Create a locator at the selected component or transform',                                
                c = cgmGEN.Callback(MMCONTEXT.func_process, LOC.create, None,'each','Create Loc'))
    
    _locSub = mc.menuItem(parent=parent,subMenu=True,tearOff =True, 
                          l = 'Loc - Special')

    mc.menuItem(parent=_locSub,
                l = 'Mid',
                ann='Create a loc at the selected component or transform midpoint',                                
                c = cgmGEN.Callback(MMCONTEXT.func_process, LOC.create, None,'all','Create Loc at mid',**{'mode':'midPoint'}))           
    mc.menuItem(parent=_locSub,
                l = 'Ground Pos',
                ann='Create a loc at ground pos of the selected',                                
                c = cgmGEN.Callback(MMCONTEXT.func_process, SNAPCALLS.get_special_pos,
                                    None,'each','Create Loc at ground pos of selected',
                                    **{'arg':'groundPos',
                                       'mark':True}))               

    
    for m in ['boundingBox','axisBox','castFar','castNear','castCenter','castAllNear','castAllFar']:

            l_use = copy.copy(SHARED._l_axis_by_string)
            if m in ['boundingBox']:
                l_use.insert(0,'center')
            elif m in ['castCenter']:
                l_use = l_use[:3]
                
            label_section = m
            if m in ['castFar','castNear','castCenter']:
                label_section = m + ' self'
            mc.menuItem(parent=_locSub,subMenu = True,
                        l = label_section)
            for a in l_use:
                mc.menuItem(l = a,
                            c = cgmGEN.Callback(MMCONTEXT.func_process, SNAPCALLS.get_special_pos,
                                                None,'each','Create Loc at mid',
                                                **{'arg':m,
                                                   'mode':a,
                                                   'mark':True}),           
                            ann = "Selection to the last's {0} {1} pos".format(m,a))
            if m in ['castFar','castNear','castCenter']:
                mc.menuItem(parent=_locSub,subMenu = True,
                            l = m)            
                for a in l_use:
                    mc.menuItem(l = a,
                                c = cgmGEN.Callback(MMCONTEXT.func_process, SNAPCALLS.get_special_pos,
                                                    None,'all','Create Loc at mid',
                                                    **{'arg':m,
                                                       'mode':a,
                                                       'mark':True}),           
                                ann = "Selection to the last's {0} {1} pos".format(m,a))    
    mc.menuItem(parent=parent,
                l = 'Curve [ Cubic ]',
                ann='Create a cubic curve from eps of the selected components or transforms',                
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Curve',**{'create':'curve'}))
    mc.menuItem(parent=parent,
                l = 'Curve [ Linear ]',
                ann='Create a linear curve from eps of the selected components or transforms',                                
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Linear Curve',**{'create':'curveLinear'}))
    mc.menuItem(parent=parent,
                l = 'Axis Box',
                ann='Create an axis box proxy from selected',                                
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_axisProxy, None,'each','Create axix Proxy'))
    
def uiSection_riggingUtils(parent, selection = None):
    _str_func = 'uiSection_riggingUtils'  
    
    _p = mc.menuItem(parent=parent, subMenu = True,tearOff = True,
                     ann = 'Series of functions for typical rigging functions',
                     l = 'Rigging Utils')  
   
    _create = mc.menuItem(parent=_p,subMenu=True,
                          l='Create From Sel',
                          ann = 'Create from selected options',                        
                          )        
    _copy = mc.menuItem(parent=_p,subMenu=True,
                        l='Copy',
                        ann = 'Copy stuff in a from:to selection',                        
                        )    
    _gSet = mc.menuItem(parent=_p,subMenu=True,
                        l='Group',
                        ann = 'Grouping functions....',                        
                        )
    _attach = mc.menuItem(parent=_p,subMenu=True,tearOff = True,
                        l='Attach by',
                        ann = 'Attach to target functions',                        
                        )
    
    #Control stuff -------------------------------------------------------------------------------------------   
    uiSection_controlCurves(_p,selection)
    
    #Create stuff -------------------------------------------------------------------------------------------
    mc.menuItem(parent=_create,
                l = 'Transform',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'each','Create Tranform',**{'create':'null'}),          
                rp = "N")        
    mc.menuItem(parent=_create,
                l = 'Joint',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_joint_at, None,'each','Create Joint'),          
                #c = cgmGEN.Callback(self.button_action_per_sel,RIGGING.create_joint_at,'Create Joint'),
                rp = "NW")   
    mc.menuItem(parent=_create,
                l = 'Locator',
                c = cgmGEN.Callback(MMCONTEXT.func_process, LOC.create, None,'each','Create Loc'),                          
                #c = cgmGEN.Callback(self.button_action_per_sel,RIGGING.create_at,'Create Curve',**{'create':'curve'}),
                rp = "S")      
    mc.menuItem(parent=_create,
                l = 'Curve',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Curve',**{'create':'curve'}),                          
                #c = cgmGEN.Callback(self.button_action_per_sel,RIGGING.create_at,'Create Curve',**{'create':'curve'}),
                rp = "S")  
    mc.menuItem(parent=_create,
                l = 'Linear Curve',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Linear Curve',**{'create':'curveLinear'}),                          
                #c = cgmGEN.Callback(self.button_action_per_sel,RIGGING.create_at,'Create Curve',**{'create':'curve'}),
                rp = "S")  
    
    
    #Group stuff -------------------------------------------------------------------------------------------
    mc.menuItem(parent=_gSet,
                l = 'Just Group',
                ann = 'Simple grouping. Just like ctrl + g',                        
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group',**{'parent':False,'maintainParent':False}),)  
    mc.menuItem(parent=_gSet,
                l = 'Group Me',
                ann = 'Group selected objects matching transform as well.',                                        
                #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group',**{'parent':True,'maintainParent':False}))          
    mc.menuItem(parent=_gSet,
                l = 'In Place',
                ann = 'Group me while maintaining heirarchal position',                                                        
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.group_me, None,'each','Group In Place',**{'parent':True,'maintainParent':True}))     
    
    #Copy stuff -------------------------------------------------------------------------------------------
    mc.menuItem(parent=_copy,
                l = 'Transform',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.match_transform, None,'eachToFirst','Match Transform'),                    
                ann = "")
    mc.menuItem(parent=_copy,
                l = 'Orienation',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.match_orientation, None,'eachToFirst','Match Orientation'),                    
                ann = "")

    mc.menuItem(parent=_copy,
                l = 'Shapes',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.shapeParent_in_place, None,'lastFromRest','Copy Shapes', **{'snapFirst':True}),
                ann = "")

    _piv = mc.menuItem(parent=_copy,subMenu=True,
                       l = 'Pivot',
                       ann = "")
    
    #Pivot stuff -------------------------------------------------------------------------------------------
    mc.menuItem(parent = _piv,
                l = 'rotatePivot',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.copy_pivot, None,'eachToFirst', 'Match RP',**{'rotatePivot':True,'scalePivot':False}),                                               
                ann = "Copy the rotatePivot from:to")
    mc.menuItem(parent = _piv,
                l = 'scalePivot',
                c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.copy_pivot, None,'eachToFirst', 'Match SP', **{'rotatePivot':False,'scalePivot':True}),                                               
                ann = "Copy the scalePivot from:to")
    
    #Copy stuff -------------------------------------------------------------------------------------------
    l_modes = ['parent',
               'parentGroup',
               'conPointGroup',
               'conPointOrientGroup',
               'conParentGroup']
    for m in l_modes:
        mc.menuItem(parent=_attach,
                    l = m,
                    c = cgmGEN.Callback(MMCONTEXT.func_process, RIGCONSTRAINTS.attach_toShape, None,'eachToLast',**{'connectBy':m}),                    
                    ann = "Attach each to last by {0}".format(m))    
    
    
    #Continue... -------------------------------------------------------------------------------------------    
    mc.menuItem(parent = _p, l = '_______________________')
    mc.menuItem(parent=_p,
                l = 'DynParent Tool',
                en=True,
                c=cgmGEN.Callback(TOOLCALLS.dynParentTool),
                ann = "Tool for modifying and setting up dynamic parent groups")
    mc.menuItem(parent=_p,
                l = 'MRS - WIP!',
                en=True,
                c=cgmGEN.Callback(TOOLCALLS.mrsUI),
                ann = "Be forwarned - Dragons be here. Soon...")    
    mc.menuItem(parent=_p,
                l = 'Constraints',
                en=False,
                #c = lambda *a:buttonAction(tdToolsLib.doPointSnap()),
                #c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.match_orientation, None,'eachToFirst','Match Orientation'),                    
                ann = "")
    
    

from cgm.core.tools.lib import snap_calls as SNAPCALLS

def call_optionVar_ui():
    reload(SNAPCALLS)    
    SNAPCALLS.ui_optionVars()


def uiSection_snap(parent, selection = None ):
    _str_func = 'uiSection_snap'
        
    #>>Snap ----------------------------------------------------------------------------------------
    mc.menuItem(parent=parent,
                l = 'Point',
                c = lambda *a:SNAPCALLS.snap_action(selection,'point'),
                ann = "Point snap in a from:to selection")
    
    _pointSpecial = mc.menuItem(parent=parent,subMenu = True,tearOff=True,
                                l = 'Point Special',
                                ann = "asdfasdf")   
    
    
    mc.menuItem(parent=parent,
                l = 'Parent',
                c = lambda *a:SNAPCALLS.snap_action(selection,'parent'),
                ann = "Parent snap in a from:to selection")
    mc.menuItem(parent=parent,
                l = 'Orient',
                c = lambda *a:SNAPCALLS.snap_action(selection,'orient'),
                ann = "Orient snap in a from:to selection")
    
    #>>Point Special ----------------------------------------------------------------------------------------
    mc.menuItem(parent=_pointSpecial,
                l = 'Closest',
                c = lambda *a:SNAPCALLS.snap_action(selection,'closestPoint'),
                ann = "Closest point on target")

    mc.menuItem(parent=_pointSpecial,
                l = 'Ground (WIP)',
                c = lambda *a:SNAPCALLS.snap_action(selection,'ground'),
                ann = "Snaps selected to the ground plane")
    
    
    for m in ['boundingBox','axisBox','castFar','castNear','castCenter']:
        mc.menuItem(parent=_pointSpecial,subMenu = True,
                    l = m)
        l_use = copy.copy(SHARED._l_axis_by_string)
        if m in ['boundingBox']:
            l_use.insert(0,'center')
        elif m in ['castCenter']:
            l_use = l_use[:3]
        for a in l_use:
            mc.menuItem(l = a,
                        c = cgmGEN.Callback(SNAPCALLS.snap_action,selection,m,**{'mode':a}),
                        ann = "Selection to the last's {0} {1} pos".format(m,a))
            
        for a in l_use:
                mc.menuItem(l = a + " Each",
                            c = cgmGEN.Callback(SNAPCALLS.snap_action,selection,m,'each',**{'mode':a}),
                            ann = "Selection to each obj's {0} {1} pos".format(m,a))
                
            
    #>>Aim ----------------------------------------------------------------------------------------
    mc.menuItem(parent=parent,
                l = 'Aim',
                c = lambda *a:SNAPCALLS.snap_action(selection,'aim','eachToLast'),
                ann = "Aim snap in a from:to selection")
    
    _aim = mc.menuItem(parent=parent,subMenu = True,
                       l = 'Aim Special',
                       ann = "asdfasdf")
    mc.menuItem(parent=_aim,
                l = 'All to last',
                c = lambda *a:SNAPCALLS.snap_action(selection,'aim','eachToLast'),
                ann = "Aim all objects to the last in selection")
    mc.menuItem(parent=_aim,
                l = 'Selection Order',
                c = lambda *a:SNAPCALLS.snap_action(selection,'aim','eachToNext'),
                ann = "Aim in selection order")
    mc.menuItem(parent=_aim,
                l = 'First to Midpoint',
                c = lambda *a:SNAPCALLS.snap_action(selection,'aim','firstToRest'),
                ann = "Aim the first object to the midpoint of the rest")
    
    #>>Raycast ----------------------------------------------------------------------------------------
    mc.menuItem(parent=parent,
                l = 'RayCast',
                c = lambda *a:SNAPCALLS.raySnap_start(selection),
                ann = "RayCast snap selected objects")
    mc.menuItem(parent=parent,
                l = 'AimCast',
                c = lambda *a:SNAPCALLS.aimSnap_start(selection),
                ann = "AimCast snap selected objects")    
    
    #>>Match ----------------------------------------------------------------------------------------
    _match= mc.menuItem(parent=parent,subMenu = True,
                        l = 'Match',
                        ann = "Series of options from cgmLocinator")
    
    mc.menuItem(parent=_match,
                l = 'Self',
                c = cgmGEN.Callback(MMCONTEXT.func_process, LOCINATOR.update_obj, selection,'each','Match',False,**{'mode':'self'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                ann = "Update selected objects to match object. If the object has no match object, a loc is created")
    mc.menuItem(parent=_match,
                l = 'Target',
                c = cgmGEN.Callback(MMCONTEXT.func_process, LOCINATOR.update_obj, selection,'each','Match',False,**{'mode':'target'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                ann = "Update the match object, not the object itself")
    mc.menuItem(parent=_match,
                l = 'Buffer',
                #c = cgmGEN.Callback(buttonAction,raySnap_start(_sel)),                    
                c = cgmGEN.Callback(LOCINATOR.update_obj,**{'mode':'buffer'}),#'targetPivot':self.var_matchModePivot.value                                                                      
                ann = "Update the buffer (if exists)")    
    
    #>>Arrange ----------------------------------------------------------------------------------------
    _arrange= mc.menuItem(parent=parent,subMenu = True,tearOff=True,
                          l = 'Arrange',
                          ann = "Ordered layout of selected items")    
    mc.menuItem(parent=_arrange,
                  l = 'Linear[Even]',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{}),                                               
                  ann = ARRANGE._d_arrangeLine_ann.get('linearEven'))
    mc.menuItem(parent=_arrange,
                l = 'Linear[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{'mode':'spaced'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('linearSpaced'))
    
    mUI.MelMenuItemDiv(_arrange)        

    mc.menuItem(parent=_arrange,
              l = 'Curve[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{'mode':'even','curve':'cubic'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicEven'))
    mc.menuItem(parent=_arrange,
              l = 'Arc[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{'mode':'even','curve':'cubicArc'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicArcEven'))
    mc.menuItem(parent=_arrange,
              l = 'Arc[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{'mode':'spaced','curve':'cubicArc'}),                                               
              ann = ARRANGE._d_arrangeLine_ann.get('cubicArcSpaced'))    
    
    mUI.MelMenuItemDiv(_arrange)        
    mc.menuItem(parent=_arrange,
              l = '2[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{'mode':'even','curve':'cubicRebuild','spans':2}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild2Even'))
    mc.menuItem(parent=_arrange,
              l = '2[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{'mode':'spaced','curve':'cubicRebuild','spans':2}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild2Spaced'))
    mc.menuItem(parent=_arrange,
              l = '3[Even]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{'mode':'even','curve':'cubicRebuild','spans':3}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild3Even'))
    mc.menuItem(parent=_arrange,
              l = '3[Spaced]',
              ut = 'cgmUITemplate',
              c = cgmGEN.Callback(MMCONTEXT.func_process, ARRANGE.alongLine, None,'all', 'AlongLine',noSelect = 0, **{'mode':'spaced','curve':'cubicRebuild','spans':3}),
              ann = ARRANGE._d_arrangeLine_ann.get('cubicRebuild3Spaced'))    
    #cgmUI.mUI.MelSeparator(parent)
    mc.menuItem(parent=parent,
                l = 'Snap UI',
                c = cgmGEN.Callback(TOOLCALLS.cgmSnapTools),                                               
                ann = "Open snap tools")    
    return


def uiSection_rayCast(parent, selection = None):
    _str_func = 'uiSection_rayCast'  
    
    if selection is None:
        selection = mc.ls(sl=True)
    
    _p = mc.menuItem(parent=parent, subMenu = True,tearOff = True,
                     ann = 'Series of functions for using cgm raycasting',
                     l = 'Raycasting')
    
    mc.menuItem(parent=_p,
                l = 'RayCast Snap',
                c = lambda *a:SNAPCALLS.raySnap_start(selection),
                ann = "RayCast snap selected objects")
    mc.menuItem(parent=_p,
                l = 'AimCast',
                c = lambda *a:SNAPCALLS.aimSnap_start(selection),
                ann = "AimCast snap selected objects")    
    
    _create = mc.menuItem(parent=_p,subMenu = True,
                          l = 'Cast Create',
                          ann = "Series of options for object creation using rayCasting")
    _drag = mc.menuItem(parent=_p,subMenu = True,
                        l = 'Drag Create',
                        ann = "Series of options for object creation using rayCasting using dragging")    
    
    
    for m in ['locator','joint','jointChain','curve','duplicate','vectorLine','data']:
        mc.menuItem(parent=_create,
                    l = m,
                    c = cgmGEN.Callback(SNAPCALLS.rayCast_create,selection,m,False),
                    ann = "Create {0} by rayCasting".format(m))   
        mc.menuItem(parent=_drag,
                    l = m,
                    c = cgmGEN.Callback(SNAPCALLS.rayCast_create,selection,m,True),
                    ann = "Create {0} by drag rayCasting".format(m))            

    

def uiFunc_createOneOfEach():
    var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)        
    CURVES.create_oneOfEach(var_createSizeValue.value)

def uiFunc_createCurve():
    reload(CURVES)
    var_createAimAxis = cgmMeta.cgmOptionVar('cgmVar_createAimAxis', defaultValue = 2)
    var_curveCreateType = cgmMeta.cgmOptionVar('cgmVar_curveCreateType', defaultValue = 'circle')
    var_defaultCreateColor = cgmMeta.cgmOptionVar('cgmVar_defaultCreateColor', defaultValue = 'yellow')
    var_createSizeMode = cgmMeta.cgmOptionVar('cgmVar_createSizeMode', defaultValue=0)
    var_createSizeValue = cgmMeta.cgmOptionVar('cgmVar_createSizeValue', defaultValue=1.0)
    var_createSizeMulti = cgmMeta.cgmOptionVar('cgmVar_createSizeMultiplierValue', defaultValue=1.25)        
    CURVES.create_controlCurve(mc.ls(sl=True),
                               var_curveCreateType.value,
                               var_defaultCreateColor.value,
                               var_createSizeMode.value,
                               var_createSizeValue.value,
                               var_createSizeMulti.value,
                               SHARED._l_axis_by_string[var_createAimAxis.value])
    
    
#Option Menus -----------------------------------------------------
def uiOptionMenu_contextTD(self, parent, callback = cgmGEN.Callback):
    uiMenu_context = mc.menuItem( parent = parent, l='Context:', subMenu=True)
    
    try:self.var_contextTD
    except:self.var_contextTD = cgmMeta.cgmOptionVar('cgmVar_contextTD', defaultValue = 'selection')

    try:#>>>
        _str_section = 'Contextual TD mode'
        uiRC = mc.radioMenuItemCollection()
        #self.uiOptions_menuMode = []		
        _v = self.var_contextTD.value

        for i,item in enumerate(['selection','children','heirarchy','scene']):
            if item == _v:
                _rb = True
            else:_rb = False
            mc.menuItem(parent=uiMenu_context,collection = uiRC,
                        label=item,
                        #c = lambda *a:ui_CallAndKill(self.var_contextTD.setValue,item),
                        c = callback(self.var_contextTD.setValue,item),                                  
                        rb = _rb)                
    except Exception,err:
        log.error("|{0}| failed to load. err: {1}".format(_str_section,err))
        
def uiOptionMenu_buffers(self, callback = cgmGEN.Callback):
    try:self.uiMenuBuffers = None
    except:pass
    
    self.uiMenu_Buffers.clear()  

    uiMenu = self.uiMenu_Buffers
    
    try:self.var_rayCastTargetsBuffer
    except:self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
    try:self.var_locinatorTargetsBuffer
    except:self.var_locinatorTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_locinatorTargetsBuffer',defaultValue = [''])


    _d = {'RayCast':self.var_rayCastTargetsBuffer,
          'Match':self.var_locinatorTargetsBuffer}

    for k in _d.keys():
        var = _d[k]
        _ui = mc.menuItem(p=uiMenu, subMenu = True,
                          l = k)

        mc.menuItem(p=_ui, l="Define",
                    c= cgmGEN.Callback(cgmUI.varBuffer_define,self,var))                                

        mc.menuItem(p=_ui, l="Add Selected",
                    c= cgmGEN.Callback(cgmUI.varBuffer_add,self,var))        

        mc.menuItem(p=_ui, l="Remove Selected",
                    c= cgmGEN.Callback(cgmUI.varBuffer_remove,self,var))        


        mc.menuItem(p=_ui,l='----------------',en=False)
        mc.menuItem(p=_ui, l="Report",
                    c= cgmGEN.Callback(var.report))        
        mc.menuItem(p=_ui, l="Select Members",
                    c= cgmGEN.Callback(var.select))        
        mc.menuItem(p=_ui, l="Clear",
                    c= cgmGEN.Callback(var.clear))  

    #mc.menuItem(p=uiMenu, l="--------------",en=False)
    #mc.menuItem(p=uiMenu, l="Reload",
    #            c= cgmGEN.Callback(ui))
    
def uiChunk_rayCast(self,parent):
    self.var_createRayCast = cgmMeta.cgmOptionVar('cgmVar_createRayCast', defaultValue = 'locator')        
    self.var_rayCastTargetsBuffer = cgmMeta.cgmOptionVar('cgmVar_rayCastTargetsBuffer',defaultValue = [''])            
    self.var_rayCastMode = cgmMeta.cgmOptionVar('cgmVar_rayCastMode', defaultValue=0)
    self.var_rayCastOffsetMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetMode', defaultValue=0)
    self.var_rayCastOffsetDist = cgmMeta.cgmOptionVar('cgmVar_rayCastOffsetDist', defaultValue=1.0) 
    self.var_rayCastOrientMode = cgmMeta.cgmOptionVar('cgmVar_rayCastOrientMode', defaultValue = 0)
    self.var_rayCastDragInterval = cgmMeta.cgmOptionVar('cgmVar_rayCastDragInterval', defaultValue = .2)
    
    _inside = parent 
    
    
    #>>>Raycast ====================================================================================

    #>>>Cast Mode  -------------------------------------------------------------------------------------
    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastMode.value

    _row1 = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)


    mUI.MelSpacer(_row1,w=5)

    mUI.MelLabel(_row1,l='Cast')
    _row1.setStretchWidget( mUI.MelSeparator(_row1) )

    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastMode.value

    for i,item in enumerate(['close','mid','far','all','x','y','z']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row1,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_rayCastMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)    

    _row1.layout() 

    #>>>offset Mode  -------------------------------------------------------------------------------------
    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastOffsetMode.value        

    _row_offset = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_offset,w=5)                              
    mUI.MelLabel(_row_offset,l='Offset')
    _row_offset.setStretchWidget( mUI.MelSeparator(_row_offset) )  

    for i,item in enumerate(['None','Distance','snapCast']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row_offset,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_rayCastOffsetMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)   


    _row_offset.layout()

    #>>>offset Mode  -------------------------------------------------------------------------------------
    uiRC = mUI.MelRadioCollection()
    _on = self.var_rayCastOrientMode.value        

    _row_orient = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_orient,w=5)                              
    mUI.MelLabel(_row_orient,l='Orient')
    _row_orient.setStretchWidget( mUI.MelSeparator(_row_orient) )  

    for i,item in enumerate(['None','Normal']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row_orient,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_rayCastOrientMode.setValue,i))

        mUI.MelSpacer(_row1,w=2)   

    cgmUI.add_Button(_row_orient,'Set drag interval',
                     lambda *a:self.var_rayCastDragInterval.uiPrompt_value('Set drag interval'),
                     'Set the rayCast drag interval by ui prompt')   
    cgmUI.add_Button(_row_orient,'Set Offset',
                     lambda *a:self.var_rayCastOffsetDist.uiPrompt_value('Set offset distance'),
                     'Set the the rayCast offset distance by ui prompt')         
    mUI.MelSpacer(_row_orient,w=5)                                                  
    _row_orient.layout()

    #>>>rayCast -------------------------------------------------------------------------------------
    _row_rayCast = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_rayCast,w=5)                                              
    mUI.MelLabel(_row_rayCast,l='rayCast:')
    _row_rayCast.setStretchWidget(mUI.MelSeparator(_row_rayCast)) 


    self.uiField_rayCastCreate = mUI.MelLabel(_row_rayCast,
                                              ann='Change the default rayCast create type',
                                              ut='cgmUIInstructionsTemplate',w=100)        
    self.uiField_rayCastCreate(edit=True, label = self.var_createRayCast.value)

    self.uiPopup_createRayCast()       

    mc.button(parent=_row_rayCast,
              ut = 'cgmUITemplate',                                                                              
              l = 'Create',
              c = lambda a: SNAPCALLS.rayCast_create(None,self.var_createRayCast.value,False),
              ann = TOOLANNO._d['raycast']['create'])       
    mc.button(parent=_row_rayCast,
              ut = 'cgmUITemplate',                                                                              
              l = 'Drag',
              c = lambda a: SNAPCALLS.rayCast_create(None,self.var_createRayCast.value,True),
              ann = TOOLANNO._d['raycast']['drag'])       
    """
            mUI.MelLabel(_row_rayCast,
                         l=' | ')

            mc.button(parent=_row_rayCast,
                      ut = 'cgmUITemplate',                                                                              

                    l = 'RayCast Snap',
                    c = lambda *a:SNAPCALLS.raySnap_start(None),
                    ann = "RayCast snap selected objects")
            mc.button(parent=_row_rayCast,
                      ut = 'cgmUITemplate',                                                                                                
                      l = 'AimCast',
                      c = lambda *a:SNAPCALLS.aimSnap_start(None),
                      ann = "AimCast snap selected objects") """   

    mUI.MelSpacer(_row_rayCast,w=5)                                                  
    _row_rayCast.layout()
    