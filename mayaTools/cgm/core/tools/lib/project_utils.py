"""
------------------------------------------
project_utils: cgm.core.tools.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is for more advanced snapping functionality.
================================================================
"""
__version__ = '0.1.10282019'

import copy
import pprint

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import maya.cmds as mc
import maya
import maya.mel as mel

from cgm.core import cgm_General as cgmGEN

#Data ================================================================================================
d_dirFramework = {
'game':{'content':{'art':['Character','Enviornment','FX','Poses','Props',
                          'UI','VisDev'],
                   'audio':['BGM','Debug','SFX','UI']},
         'export':{'art':['Character','Enviornment','FX','Props','UI'],
                   'audio':['BGM','Debug','SFX']}},

'character':{'content':['animation','templates','builds','textures','poses','weights'],
             'export':['animation']},
'enviornment':{'content':['animation','textures'],
             'export':['animation']},
'prop':{'content':['animation','templates','builds','textures','poses','weights'],
        'export':['animation']},
             }


_dataConfigToStored = {'general':'d_project',
                       'enviornment':'d_env',
                       'paths':'d_paths',
                       'anim':'d_animSettings',
                       'structure':'d_structure',
                       'world':'d_world'}

l_projectPathModes = ['art','content','root']
l_projectDat = ['name','type','projectPathMode','nameStyle']
l_nameConventions = ['none','lower','capital','camelCase']
l_projectTypes = ['unity','unreal','commercial']
l_projectPaths = ['root','content','export','image']



_tangents = ['linear','spline','clamped','flat','plateau','auto']
_fps = [2,3,4,5,6,8,10,12,15,16,20,23.976,
        24,25,29.97,30,40,48,50,
        60,75,80,100,120]

_fpsStrings = ['2', '3', '4', '5', '6', '8', '10', '12', '15', '16', '20', '23.976', '24', '25', '29.97', '30', '40', '48', '50', '60', '75', '80', '100', '120']

_animSettings = [{'n':'frameRate','t':_fpsStrings,'dv':'24'},
                 {'n':'defaultInTangent','t':_tangents,'dv':'linear'},
                 {'n':'defaultOutTangent','t':_tangents,'dv':'linear'},
                 {'n':'weightedTangents','t':'bool','dv':False},
                  ]

_worldSettings = [{'n':'worldUp','t':['y','z'],'dv':'y'},
                  {'n':'linear','t':['milimeter','centimeter','meter',
                                     'inch','foot','yard'],'dv':'centimeter'},
                  {'n':'angular','t':['degrees','radians'],'dv':'degrees'},                   
                   ]

_cameraSettings = [{'n':'nearClip','t':'float','dv':.1},
                    {'n':'farClip','t':'float','dv':100000}]

_cameraSettings = [{'n':'nearClip','t':'float','dv':.1},
                    {'n':'farClip','t':'float','dv':100000}]

_structureSettings = [{'n':'assetTypes','t':'text','dv':'Character,Props,Enviornment'},
                      {'n':'charContent','t':'text','dv':','.join(d_dirFramework['character']['content'])},
                      {'n':'charExport','t':'text','dv':','.join(d_dirFramework['character']['export'])}]

_d_defaultsMap = {'anim':_animSettings,
                  'world':_worldSettings,
                  'structure':_structureSettings,}





d_defaults = {'general':{'type':'unity',
                         'projectPathMode':'art'}}


def dirCreateList_get(projectType,dirSet,key = None):
    try:
        _dType = d_dirFramework.get(projectType,{})
        pprint.pprint(_dType)
        _dDir = _dType.get(dirSet)
        
        if key == None:
            return _dDir
        if issubclass(type(_dDir),list):
            return _dDir
        return _dDir.get(key,[])
    except Exception,err:
        log.error(err)