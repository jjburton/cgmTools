"""
------------------------------------------
project_utils: cgm.core.tools.lib
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

This is for more advanced snapping functionality.
================================================================
"""
__version__ = '0.1.12212019'

import copy
import pprint

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import maya.cmds as mc
import maya
import maya.mel as mel

from cgm.core import cgm_General as cgmGEN

#Data ================================================================================================
_animatable_content = ['animation','template','rig','textures','poses','weights','geo']
_fbxVersions = cgmGEN.get_mayaFBXVersionsAvailable()

d_dirFramework = {
'game':{'content':['Character','Environment','FX','Poses','Props','Cutscene',
                          'UI','VisDev'],
                   #'audio':['BGM','Debug','SFX','UI'],
         'export':['Character','Environment','FX','Props','UI','Cutscene'],
                   #'audio':['BGM','Debug','SFX']},
                   },
'character':{'content': _animatable_content,
             'export':['animation'],
             'dir':'characters'},
'environment':{'content':['animation','textures','geo'],
             'export':['animation'],
             'dir':'environments'},
'sub':{'content':['animation','environment'],
       'export':['animation','environment'],
       'dir':'sub'},
'prop':{'content': _animatable_content,
        'export':['animation'],
        'dir':'props'},
'sequence':{'content':['shot'],
            'export':['shot'],
            'dir':'sequences'},
'ui':{'content':[],
      'dir':'UI'},
'fx':{'content':[],
      'dir':'FX'},
'visdev':{'content':[],
          'dir':'VisDev'},
'default':{'content':[]},
'audio':{'content':['BGM','Debug','SFX','UI'],
            'export':['BGM','Debug','SFX']},
'cutscene':{'content':['animation'],
            'export':['animation'],
            'dir':'cutscenes'},
'proxy':{'content':['animation','template','rig','poses','geo'],
         'dir':'proxies'}}


d_projType ={'game':['character','environment','fx','visdev','ui','prop','poses','cutscene'],
             'film':['character','environment','fx','visdev','prop','poses','sequence']}

def dirCreateList_get2(projectType,dirSet=None,key = None):
    try:
        _dType = d_dirFramework.get(projectType,{})
        pprint.pprint(_dType)
        _dDir = _dType.get(dirSet)
        
        if key == None:
            return _dDir
        if issubclass(type(_dDir),list):
            return _dDir
        return _dDir.get(key,[])
    except Exception as err:
        log.error(err)
        

def dirCreateList_get(projectType,dirSet=None,key = None):
    l_assets = d_projType.get(projectType,False)
    if not l_assets:
        raise ValueError("Invalid projectType: {0}".format(projectType))
    
    if not dirSet:
        return l_assets

    l_set = []
    for k in l_assets:
        d = d_dirFramework.get(k,{})
        if not d:
            log.warning("No data on {0}".format(k))
        #if d.has_key(dirSet):
            #l_set.append(d.get('dir',k))
        l_set.append(k)
    return l_set

def asset_getBaseList(arg=None,key=None):
    _dAsset = d_dirFramework.get(arg,{})
    
    if key == None:
        return _dAsset
    if issubclass(type(_dAsset),list):
        return _dAsset
    return _dAsset.get(key,[])    
    




_dataConfigToStored = {'general':'d_project',
                       'paths':'d_paths',
                       'pathsUser':'d_pathsUser',
                       'colors':'d_colors',
                       'exportOptions':'d_exportOptions',
                       'pathsProject':'d_pathsProject',
                       'anim':'d_animSettings',
                       'structure':'d_structure',
                       #'assetDat':'assetDat',
                       'world':'d_world'}

l_projectPathModes = ['art','content','root']
l_projectDat = ['name','type','nameStyle','mayaVersion','mayaVersionCheck','mayaFilePref','dirMask','lock']
l_nameConventions = ['none','lower','capital','upper','camelCase','capFirst']
l_mayaVersions = ['2016','2017','2018','2019','2020','2022','2023','2024','2025','2026','2027','2028']
l_userMode = ['general','master']
l_projectTypes = ['unity','unreal','commercial']
l_projectPaths = ['root','content','export','image','scriptUI','poses','scripts']
l_mayaFileType = ['ma','mb']


_tangents = ['linear','spline','clamped','flat','plateau','stepped','auto']
_fps = [2,3,4,5,6,8,10,12,15,16,20,23.976,
        24,25,29.97,30,40,48,50,
        60,75,80,100,120]

_fpsStrings = ['2fps', '3fps', '4fps', '5fps', '6fps', '8fps', '10fps', '12fps', '15fps', '16fps', '20fps',
               '23.976fps', '24fps', '25fps', '29.97fps', '30fps', '40fps', '48fps', '50fps', '60fps', '75fps', '80fps', '100fps', '120fps']


#Settings/Options ... ---------------------------------------------------------------------------
_projSettings = [{'n':'name','t':'text','dv':'Name me'},
                 {'n':'type','t':l_projectTypes,'dv':'unity'},
                 {'n':'lock','t':'bool','dv':'false'},
                 {'n':'mayaVersion','t':l_mayaVersions,'dv':'2018'},
                 {'n':'mayaVersionCheck','t':'bool','dv':'false'},                 
                 {'n':'mayaFilePref','t':l_mayaFileType,'dv':'mb'},
                 #{'n':'projectPathMode','t':l_projectPathModes,'dv':'art'},
                 {'n':'nameStyle','t':l_nameConventions,'dv':'none'},
                 {'n':'dirMask','t':'text','dv':""},
                 ]
                 
_animSettings = [{'n':'frameRate','t':_fpsStrings,'dv':'24fps'},
                 {'n':'defaultInTangent','t':_tangents,'dv':'linear'},
                 {'n':'defaultOutTangent','t':_tangents,'dv':'linear'},
                 {'n':'weightedTangents','t':'bool','dv':False},
                  ]

_worldSettings = [{'n':'worldUp','t':['y','z'],'dv':'y'},
                  {'n':'linear','t':['milimeter','centimeter','meter',
                                     'inch','foot','yard'],'dv':'centimeter'},
                  {'n':'angular','t':['degrees','radians'],'dv':'degrees'},
                  {'n':'gridLengthAndWidth','t':'float','dv':1600},
                  {'n':'gridLinesEvery','t':'float','dv':400},
                  {'n':'gridSubdivisions','t':'int','dv':16},
                  
                  
                   ]

_colorSettings = [{'n':'project','t':'color','dv':[.6,.3,.3]},
                  {'n':'secondary','t':'color','dv':[.8,.15,.15]},
                  ]

_cameraSettings = [{'n':'nearClip','t':'float','dv':.1},
                    {'n':'farClip','t':'float','dv':100000}]

_cameraSettings = [{'n':'nearClip','t':'float','dv':.1},
                    {'n':'farClip','t':'float','dv':100000}]

_structureSettings = []
"""
_structureSettings = [{'n':'assetTypes','t':'text','dv':['Character','Props','Environment']},
                      {'n':'charContent','t':'text','dv':d_dirFramework['character']['content']},
                      {'n':'charExport','t':'text','dv':d_dirFramework['character']['export']},
                      {'n':'propContent','t':'text','dv':d_dirFramework['prop']['content']},
                      {'n':'propExport','t':'text','dv':d_dirFramework['prop']['export']},
                      {'n':'subContent','t':'text','dv':d_dirFramework['sub']['content']},
                      {'n':'subExport','t':'text','dv':d_dirFramework['sub']['export']},                      
                      {'n':'envContent','t':'text','dv':d_dirFramework['environment']['content']},
                      {'n':'envExport','t':'text','dv':d_dirFramework['environment']['content']}]
                      """

_exportOptionSettings = [{'n':'removeNameSpace','t':'bool','dv':False},
                         {'n':'zeroRoot','t':'bool','dv':True},
                         {'n':'postEuler','t':'bool','dv':True},
                         {'n':'reducer','t':'bool','dv':False},
                         {'n':'simplify','t':'bool','dv':False},
                         {'n':'exportShotsToIndividualFiles','t':'bool','dv':False},


                         {'n':'sampleBy','t':'float','dv':1.0},
                         {'n':'fbxVersion','t':['default'] + _fbxVersions,'dv':'default'},
                         {'n':'postTangent','t':['none','auto','linear','step'],'dv':'auto'}]

_d_defaultsMap = {'general':_projSettings,
                  'anim':_animSettings,
                  'world':_worldSettings,
                  'colors':_colorSettings,
                  'exportOptions':_exportOptionSettings,
                  'structure':_structureSettings,}


d_defaults = {'general':{'type':'unity',
                         'projectPathMode':'art'}}




        
        

