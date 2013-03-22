import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib.classes import NameFactory as nFactory
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import GuiFactory as gui
from cgm.core.rigger import TemplateFactory as tFactory

from cgm.lib import (curves,
                     deformers,
                     distance,
                     search,
                     lists,
                     modules,
                     constraints,
                     rigging,
                     attributes,
                     joints)
reload(constraints)
#======================================================================
# Processing factory
#======================================================================
#This is the main key for data tracking. It is also the processing order
l_modulesToDoOrder = ['torso']
l_modulesToDoOrderBAK2 = ['torso','clavicle_left','arm_left',
                          'clavicle_right','arm_right',
                          ]
l_modulesToDoOrderBAK = ['torso',
                      'neck',
                      'leg_left','foot_left',
                      'leg_right',
                      'clavicle_left','arm_left','hand_left',
                      'thumb_left','index_left','middle_left','ring_left','pinky_left']

#This is the parent info for each module
d_moduleParents = {'torso':False,
                   'neck':'torso',
                   'leg_left':'torso',
                   'leg_right':'torso',
                   'foot_left':'leg_left',
                   'clavicle_left':'torso',
                   'arm_left':'clavicle_left',
                   'hand_left':'arm_left',
                   'thumb_left':'hand_left',
                   'index_left':'hand_left',
                   'middle_left':'hand_left',
                   'ring_left':'hand_left',
                   'pinky_left':'hand_left',
                   'clavicle_right':'torso',
                   'arm_right':'clavicle_right',                   }

d_moduleCheck = {'torso':{'moduleType':'torso'},#This is the intialization info
                 'neck':{'moduleType':'segment','cgmName':'neck'},
                 'leg_left':{'moduleType':'leg','cgmDirection':'left'},
                 'leg_right':{'moduleType':'leg','cgmDirection':'right'},
                 'foot_left':{'moduleType':'foot','cgmDirection':'left'},                 
                 'arm_left':{'moduleType':'arm','cgmDirection':'left'},
                 'clavicle_left':{'moduleType':'clavicle','cgmDirection':'left'},
                 'hand_left':{'moduleType':'hand','cgmDirection':'left'},
                 'thumb_left':{'moduleType':'thumb','cgmDirection':'left'},
                 'index_left':{'moduleType':'finger','cgmDirection':'left','cgmName':'index'}, 
                 'middle_left':{'moduleType':'finger','cgmDirection':'left','cgmName':'middle'}, 
                 'ring_left':{'moduleType':'finger','cgmDirection':'left','cgmName':'ring'}, 
                 'pinky_left':{'moduleType':'finger','cgmDirection':'left','cgmName':'pinky'},
                 'arm_right':{'moduleType':'arm','cgmDirection':'right'},
                 'clavicle_right':{'moduleType':'clavicle','cgmDirection':'right'},
                 }

#This is the template settings info
d_moduleTemplateSettings = {'torso':{'handles':5,'rollOverride':'{"-1":0,"0":0}','curveDegree':2,'rollJoints':1},
                            'neck':{'handles':2,'rollOverride':'{}','curveDegree':2,'rollJoints':2},
                            'leg':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':2},
                            'foot':{'handles':4,'rollOverride':'{}','curveDegree':1,'rollJoints':0},
                            'arm':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':2},
                            'hand':{'handles':1,'rollOverride':'{}','curveDegree':1,'rollJoints':0},
                            'thumb':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':0},   
                            'finger':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':0},
                            'clavicle':{'handles':2,'rollOverride':'{}','curveDegree':1,'rollJoints':0},
                            }                            

#This dict is for which controls map to which keys
d_moduleControls = {'torso':['pelvis_bodyShaper','shoulders_bodyShaper'],
                    'neck':['neck_bodyShaper','head_bodyShaper'],
                    'head':['head_bodyShaper','headTop_bodyShaper'],
                    'leg_left':['l_upr_leg_bodyShaper','l_lwr_leg_bodyShaper','l_ankle_bodyShaper'],                    
                    'leg_right':['r_upr_leg_bodyShaper','r_lwr_leg_bodyShaper','r_ankle_bodyShaper'],                    
                    'foot_left':['l_ankle_bodyShaper','l_heel_bodyShaper','l_ball_bodyShaper','l_toes_bodyShaper'],                    
                    'arm_left':['l_upr_arm_bodyShaper','l_lwr_arm_bodyShaper','l_wristMeat_bodyShaper'],
                    'hand_left':['l_hand_bodyShaper'],
                    'thumb_left':['l_thumb_1_bodyShaper','l_thumb_mid_bodyShaper','l_thumb_2_bodyShaper'],
                    'index_left':['l_index_1_bodyShaper','l_index_mid_bodyShaper','l_index_2_bodyShaper'], 
                    'middle_left':['l_middle_1_bodyShaper','l_middle_mid_bodyShaper','l_middle_2_bodyShaper'], 
                    'ring_left':['l_ring_1_bodyShaper','l_ring_mid_bodyShaper','l_ring_2_bodyShaper'], 
                    'pinky_left':['l_pinky_1_bodyShaper','l_pinky_mid_bodyShaper','l_pinky_2_bodyShaper'],                     
                    'clavicle_left':['Morphy_Body_GEO.f[1648]','l_upr_arm_bodyShaper'],
                    'clavicle_right':['Morphy_Body_GEO.f[4433]','r_upr_arm_bodyShaper'],
                    'arm_right':['r_upr_arm_bodyShaper','r_lwr_arm_bodyShaper','r_wristMeat_bodyShaper'],
                    }

#=====================================================================================
#>>> Utilities
#=====================================================================================
@r9General.Timer
def verify_customizationData(i_network, skinDepth = 2.5):
    """
    Gather info from customization asset
    
    from morpheusRig_v2.core import MorpheusFactory as morphyF
    reload(morphyF)
    morphyF.verify_customizationData('Morphy_customizationNetwork')
    """
    #These are the controls we'll drive positional data from to plug to our modules
    d_initialData = {}
    
    #>>> Verify our arg
    try:i_network.mNode
    except:
        if mc.objExists(i_network):
            i_network = r9Meta.MetaClass(i_network)
        else:
            log.error("'%s' doesn't exist"%i_network)
            return False
    assert i_network.mClass == 'cgmMorpheusMakerNetwork',"Not a cgmMorpheusMakerNetwork. Aborted!"
    
    #>> Collect our positional info
    #====================================================================
    i_objSet = i_network.objSetAll#Should I use this or the message info
    log.debug(i_objSet.value)
    
    controlBuffer = i_network.objSetAll.value
    for moduleKey in l_modulesToDoOrder:
        if moduleKey not in d_moduleControls.keys():
            log.warning("Missing controls info for: '%s'"%moduleKey)
            return False
        log.debug("On moduleKey: '%s'"%moduleKey)
        controls = d_moduleControls.get(moduleKey)
        posBuffer = []
        for c in controls:
            if not mc.objExists(c):
                log.warning("Necessary positioning control not found: '%s'"%c)
                return False
            else:
                log.debug("Found: '%s'"%c)
                i_c = cgmMeta.cgmNode(c)
                if i_c.isComponent():#If it's a component
                    i_loc = cgmMeta.cgmObject(mc.spaceLocator()[0])#make a loc
                    Snap.go(i_loc.mNode,targets = c,move = True, orient = True)#Snap to the surface
                    i_loc.tz -= skinDepth#Offset on z by skin depth
                    pos = i_loc.getPosition()#get position
                    i_loc.delete()
                else:
                    pos = i_c.getPosition()
                if not pos:return False
                posBuffer.append(pos)
        d_initialData[moduleKey] = posBuffer
        
    return d_initialData
        
@r9General.Timer
def verifyMorpheusNodeStructure(i_Morpheus):
    """"
    Returns a defined Morpheus asset
    
    What is a morpheus asset
    """
    assert i_Morpheus.mClass == 'cgmMorpheusPuppet',"Not a cgmMorpheusPuppet"
    
    def returnModuleMatch(moduleKey):
        for i_m in i_Morpheus.moduleChildren:
            matchBuffer = 0
            for key in d_moduleCheck[moduleKey].keys():
                log.debug("attr: %s"%key)
                log.debug("value: '%s"%i_m.__dict__[key])
                log.debug("checkTo: '%s'"%d_moduleCheck[moduleKey].get(key))
                if i_m.hasAttr(key) and i_m.__dict__[key] == d_moduleCheck[moduleKey].get(key):
                    matchBuffer +=1
            if matchBuffer == len(d_moduleCheck[moduleKey].keys()):
                log.debug("Found Morpheus Module: '%s'"%moduleKey)
                return i_m
        return False
 
    d_moduleInstances = {}
    
    # Create the modules
    #=====================================================================
    mayaMainProgressBar = gui.doStartMayaProgressBar(len(l_modulesToDoOrder))
    
    for moduleKey in l_modulesToDoOrder:
        if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
            break
        mc.progressBar(mayaMainProgressBar, edit=True, status = "On segment '%s'..."%(moduleKey), step=1)
        
        if moduleKey not in d_moduleParents.keys():#Make sure we have a parent
            log.info("Missing parent info for: '%s'"%moduleKey)
            return False
        if moduleKey not in d_moduleCheck.keys():#Make sure we have a parent
            log.info("Missing check info for: '%s'"%moduleKey)
            return False  

        if moduleKey in d_moduleTemplateSettings.keys():#Make sure we have settings
            d_settingsDict = d_moduleTemplateSettings[moduleKey]
        elif d_moduleCheck[moduleKey]['moduleType'] in d_moduleTemplateSettings.keys():
            d_settingsDict = d_moduleTemplateSettings[ d_moduleCheck[moduleKey]['moduleType'] ]            
        else:
            log.info("Missing limb info for: '%s'"%moduleKey)
            return False

        log.debug("Have all setup info. Checking structure...")
        if moduleKey in d_moduleInstances.keys():#if it's already stored, use it
            i_module = d_moduleInstances[moduleKey]
        else:
            i_module = i_Morpheus.getModuleFromDict(d_moduleCheck[moduleKey])#Look for it
            d_moduleInstances[moduleKey] = i_module#Store it if found
        if not i_module:
            log.info("Need to create: '%s'"%moduleKey)
            kw_direction = False
            kw_name = False
            if 'cgmDirection' in d_moduleCheck[moduleKey].keys():
                kw_direction = d_moduleCheck[moduleKey].get('cgmDirection')
            if 'cgmName' in d_moduleCheck[moduleKey].keys():
                kw_name = d_moduleCheck[moduleKey].get('cgmName')            
            i_module = i_Morpheus.addModule(mClass = 'cgmLimb',mType = d_moduleCheck[moduleKey]['moduleType'],name = kw_name, direction = kw_direction)
            d_moduleInstances[moduleKey] = i_module#Store it
            
        if i_module:i_module.__verify__()
            
        #>>> Settings
        for key in d_settingsDict.keys():
            i_templateNull = i_module.templateNull
            if i_templateNull.hasAttr(key):
                log.debug("attr: '%s'"%key)  
                log.debug("setting: '%s'"%d_settingsDict.get(key))                  
                try:i_templateNull.__setattr__(key,d_settingsDict.get(key)) 
                except:log.warning("attr failed: %s"%key)
        #>>>Parent stuff        
        if d_moduleParents.get(moduleKey):#If we should be looking for a module parent
            if d_moduleParents.get(moduleKey) in d_moduleInstances.keys():
                i_moduleParent = False
                if i_module.getMessage('moduleParent') and i_module.getMessage('moduleParent') == [d_moduleInstances[d_moduleParents[moduleKey]].mNode]:
                    i_moduleParent = None
                else:
                    i_moduleParent = d_moduleInstances[d_moduleParents.get(moduleKey)]
            else:
                i_moduleParent = i_Morpheus.getModuleFromDict(d_moduleCheck.get(d_moduleParents.get(moduleKey)))
            
            if i_moduleParent is None:
                log.info("moduleParent already connected: '%s'"%d_moduleParents.get(moduleKey))                
            elif i_moduleParent:
                i_module.doSetParentModule(i_moduleParent.mNode)
            else:
                log.info("moduleParent not found from key: '%s'"%d_moduleParents.get(moduleKey))
        
    # For each module
    #=====================================================================
    gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
    #i_limb.getGeneratedCoreNames()    
    return i_Morpheus

@r9General.Timer
def setState(i_customizationNetwork,state = False,
             **kws):
    """"
    Returns a defined Morpheus asset
    
    What is a morpheus asset
    """ 
    assert i_customizationNetwork.mClass == 'cgmMorpheusMakerNetwork', "Not a customization Network"
    assert i_customizationNetwork.mPuppet.mClass == 'cgmMorpheusPuppet',"Puppet isn't there"
    
    #>>>Kw defaults
    rebuildFrom = kws.get('rebuildFrom') or None
    forceNew =  kws.get('forceNew') or False
    tryTemplateUpdate = kws.get('tryTemplateUpdate') or True
    loadTemplatePose = kws.get('loadTemplatePose') or True
    
    i_Morpheus = i_customizationNetwork.mPuppet
    d_customizationData = verify_customizationData(i_customizationNetwork)
    
    if not d_customizationData:
        return False
    
    mayaMainProgressBar = gui.doStartMayaProgressBar(len(l_modulesToDoOrder))
    
    for moduleKey in l_modulesToDoOrder:
        if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
            break
        mc.progressBar(mayaMainProgressBar, edit=True, status = "Setting:'%s'..."%(moduleKey), step=1)
        
        
        i_module = i_Morpheus.getModuleFromDict(d_moduleCheck[moduleKey])
        if not i_module:
            log.warning("Cannot find Module: '%s'"%moduleKey)
            return False
        log.debug("Building: '%s'"%moduleKey)
        i_module.setState(state,
                          sizeMode = 'manual',
                          posList = d_customizationData.get(moduleKey),
                          **kws)
        #i_module.doSize('manual', posList = d_customizationData.get(moduleKey))
        #i_module.doTemplate()
    gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        
@r9General.Timer
def updateTemplate(i_customizationNetwork,**kws):  
    assert i_customizationNetwork.mClass == 'cgmMorpheusMakerNetwork', "Not a customization Network"
    assert i_customizationNetwork.mPuppet.mClass == 'cgmMorpheusPuppet',"Puppet isn't there"
    
    d_customizationData = verify_customizationData(i_customizationNetwork)
    i_Morpheus = i_customizationNetwork.mPuppet
    
    if not d_customizationData:
        return False
    
    mayaMainProgressBar = gui.doStartMayaProgressBar(len(l_modulesToDoOrder))
    
    for moduleKey in l_modulesToDoOrder:
        if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
            break
        mc.progressBar(mayaMainProgressBar, edit=True, status = "Setting:'%s'..."%(moduleKey), step=1)
        
        i_module = i_Morpheus.getModuleFromDict(d_moduleCheck[moduleKey])
        if not i_module:
            log.warning("Cannot find Module: '%s'"%moduleKey)
            return False
        log.debug("Building: '%s'"%moduleKey)
        i_module.doSize(sizeMode = 'manual',
                        posList = d_customizationData.get(moduleKey))
        i_module.doTemplate(tryTemplateUpdate = True,
                            **kws)        
    gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        