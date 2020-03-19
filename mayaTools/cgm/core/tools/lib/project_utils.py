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
d_dirFramework = {
'game':{'content':['Character','Environment','FX','Poses','Props','Cutscene',
                          'UI','VisDev'],
                   #'audio':['BGM','Debug','SFX','UI'],
         'export':['Character','Environment','FX','Props','UI','Cutscene'],
                   #'audio':['BGM','Debug','SFX']},
                   },

'character':{'content':['animation','templates','builds','textures','poses','weights','geo'],
             'export':['animation']},
'environment':{'content':['animation','textures','geo'],
             'export':['animation']},
'sub':{'content':['animation','environment'],
       'export':['animation','environment']},
'prop':{'content':['animation','templates','builds','textures','poses','weights','geo'],
        'export':['animation']},
             }


_dataConfigToStored = {'general':'d_project',
                       'paths':'d_paths',
                       'pathsUser':'d_pathsUser',
                       'pathsProject':'d_pathsProject',
                       'anim':'d_animSettings',
                       'structure':'d_structure',
                       'world':'d_world'}

l_projectPathModes = ['art','content','root']
l_projectDat = ['name','type','nameStyle','lock']
l_nameConventions = ['none','lower','capital','upper','camelCase','capFirst']
l_userMode = ['general','master']
l_projectTypes = ['unity','unreal','commercial']
l_projectPaths = ['root','content','export','image']



_tangents = ['linear','spline','clamped','flat','plateau','auto']
_fps = [2,3,4,5,6,8,10,12,15,16,20,23.976,
        24,25,29.97,30,40,48,50,
        60,75,80,100,120]

_fpsStrings = ['2fps', '3fps', '4fps', '5fps', '6fps', '8fps', '10fps', '12fps', '15fps', '16fps', '20fps',
               '23.976fps', '24fps', '25fps', '29.97fps', '30fps', '40fps', '48fps', '50fps', '60fps', '75fps', '80fps', '100fps', '120fps']


#Settings/Options ... ---------------------------------------------------------------------------
_projSettings = [{'n':'name','t':'text','dv':'Name me'},
                 {'n':'type','t':l_projectTypes,'dv':'unity'},
                 {'n':'type','t':l_projectTypes,'dv':'unity'},
                 {'n':'lock','t':'bool','dv':'false'},
                 
                 #{'n':'projectPathMode','t':l_projectPathModes,'dv':'art'},
                 {'n':'nameStyle','t':l_nameConventions,'dv':'none'},
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
                   ]

_cameraSettings = [{'n':'nearClip','t':'float','dv':.1},
                    {'n':'farClip','t':'float','dv':100000}]

_cameraSettings = [{'n':'nearClip','t':'float','dv':.1},
                    {'n':'farClip','t':'float','dv':100000}]

_structureSettings = [{'n':'assetTypes','t':'text','dv':['Character','Props','Environment']},
                      {'n':'charContent','t':'text','dv':d_dirFramework['character']['content']},
                      {'n':'charExport','t':'text','dv':d_dirFramework['character']['export']},
                      {'n':'propContent','t':'text','dv':d_dirFramework['prop']['content']},
                      {'n':'propExport','t':'text','dv':d_dirFramework['prop']['export']},
                      {'n':'subContent','t':'text','dv':d_dirFramework['sub']['content']},
                      {'n':'subExport','t':'text','dv':d_dirFramework['sub']['export']},                      
                      {'n':'envContent','t':'text','dv':d_dirFramework['environment']['content']},
                      {'n':'envExport','t':'text','dv':d_dirFramework['environment']['content']}]

_d_defaultsMap = {'general':_projSettings,
                  'anim':_animSettings,
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
        
        

