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
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib.classes import NameFactory as nFactory
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import GuiFactory as gui
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.classes import NodeFactory as cgmNodeFactory
#reload(cgmNodeFactory)
from cgm.core.rigger.lib import morpheus_sharedData as MORPHYDATA
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
#reload(constraints)
#======================================================================
# Processing factory
#======================================================================
#l_modulesToDoOrder = ['torso','neckHead']
#This is the main key for data tracking. It is also the processing order
#l_modulesToDoOrder = ['torso','neckHead','leg_left']
#l_modulesToDoOrder = ['torso','clavicle_left','clavicle_right','arm_left','arm_right']
#l_modulesToDoOrder = ['torso','clavicle_left']
#l_modulesToDoOrder = ['torso','neckHead','leg_left','leg_right']
'''
l_modulesToDoOrder = ['torso','neckHead','leg_left','leg_right',
                      'clavicle_left','arm_left',
                      'thumb_left','index_left','middle_left','ring_left','pinky_left',                   
                      'clavicle_right','arm_right',
                      'thumb_right','index_right','middle_right','ring_right','pinky_right',
                      ]'''
'''
l_modulesToDoOrder = ['torso','neckHead','leg_left','leg_right',
                      'clavicle_left','arm_left',
                      'clavicle_right','arm_right',
                      ]'''
#l_modulesToDoOrder = ['torso']
"""

l_modulesToDoOrder = ['torso','neckHead','leg_left','leg_right']

l_modulesToDoOrder = ['torso',
                      'clavicle_left','arm_left',
                      'thumb_left','index_left','middle_left','ring_left','pinky_left'
                      ]
l_modulesToDoOrder = ['torso',
                      'clavicle_left','arm_left',
                      'thumb_left','index_left','middle_left','ring_left','pinky_left',
                      ]
"""
l_modulesToDoOrder = ['torso','neckHead','leg_left','leg_right',
                      'clavicle_left','arm_left',
                      'thumb_left','index_left','middle_left','ring_left','pinky_left',                     
                      'clavicle_right','arm_right',
                      'thumb_right','index_right','middle_right','ring_right','pinky_right'
                      ]


#This is the parent info for each module
d_moduleParents = {'torso':False,
                   'neckHead':'torso',
                   'leg_left':'torso',
                   'leg_right':'torso',
                   'foot_left':'leg_left',
                   'foot_right':'leg_right',                   
                   'clavicle_left':'torso',
                   'arm_left':'clavicle_left',
                   'thumb_left':'arm_left',
                   'index_left':'arm_left',
                   'middle_left':'arm_left',
                   'ring_left':'arm_left',
                   'pinky_left':'arm_left',
                   'clavicle_right':'torso',
                   'arm_right':'clavicle_right',
                   'thumb_right':'arm_right',
                   'index_right':'arm_right',
                   'middle_right':'arm_right',
                   'ring_right':'arm_right',
                   'pinky_right':'arm_right',                   }

d_moduleCheck = {'torso':{'moduleType':'torso'},#This is the intialization info
                 'neckHead':{'moduleType':'neckHead','cgmName':'neck'},
                 'leg_left':{'moduleType':'leg','cgmDirection':'left'},
                 'leg_right':{'moduleType':'leg','cgmDirection':'right'},
                 'foot_left':{'moduleType':'foot','cgmDirection':'left'}, 
                 'foot_right':{'moduleType':'foot','cgmDirection':'right'},                                  
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
                 'thumb_right':{'moduleType':'thumb','cgmDirection':'right'},
                 'index_right':{'moduleType':'finger','cgmDirection':'right','cgmName':'index'}, 
                 'middle_right':{'moduleType':'finger','cgmDirection':'right','cgmName':'middle'}, 
                 'ring_right':{'moduleType':'finger','cgmDirection':'right','cgmName':'ring'}, 
                 'pinky_right':{'moduleType':'finger','cgmDirection':'right','cgmName':'pinky'},                 
                 }

#This is the template settings info
d_moduleTemplateSettings = {'torso':{'handles':5,'rollOverride':'{"-1":0,"0":0}','curveDegree':2,'rollJoints':1},
                            'neckHead':{'handles':2,'rollOverride':'{}','curveDegree':2,'rollJoints':3},
                            'leg':{'handles':4,'rollOverride':'{"-1":0}','curveDegree':1,'rollJoints':3},
                            'foot':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':0},
                            'arm':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
                            'hand':{'handles':1,'rollOverride':'{}','curveDegree':1,'rollJoints':0},
                            'thumb':{'handles':4,'rollOverride':'{}','curveDegree':1,'rollJoints':0},   
                            'finger':{'handles':5,'rollOverride':'{}','curveDegree':1,'rollJoints':0},
                            'clavicle':{'handles':2,'rollOverride':'{}','curveDegree':1,'rollJoints':0},
                            }                            

#This dict is for which controls map to which keys
d_moduleControls = {'torso':['pelvis_bodyShaper','shoulders_bodyShaper'],
                    'neckHead':['neck_loc','head_loc'],
                    'head':['head_bodyShaper','headTop_bodyShaper'],
                    'leg_left':['l_upr_leg_loc','l_lwr_leg_loc','l_ankleMeat_bodyShaper','l_ball_loc'],                    
                    'leg_right':['r_upr_leg_loc','r_lwr_leg_loc','r_ankleMeat_bodyShaper','r_ball_loc'],                    
                    'foot_left':['l_ankle_bodyShaper','l_ball_loc','l_toes_bodyShaper'],                    
                    'foot_right':['r_ankle_bodyShaper','r_ball_loc','r_toes_bodyShaper'],                                        
                    'arm_left':['l_arm_loc','l_lwr_arm_loc','l_hand_bodyShaper'],
                    'hand_left':['l_hand_bodyShaper'],
                    'thumb_left':['l_thumb_1_bodyShaper','l_thumb_mid_bodyShaper',
                                  'l_thumb_2_bodyShaper','l_thumb_3_shaper1_shape2.cv[4]'],
                    'index_left':['l_root_index_loc','l_index_1_bodyShaper',
                                  'l_index_mid_bodyShaper','l_index_2_bodyShaper','l_index_2_shaperCurve1_shape2.cv[4]'], 
                    'middle_left':['l_root_middle_loc','l_middle_1_bodyShaper',
                                   'l_middle_mid_bodyShaper','l_middle_2_bodyShaper','l_middle_2_shaperCurve1_shape2.cv[4]'], 
                    'ring_left':['l_root_ring_loc','l_ring_1_bodyShaper',
                                 'l_ring_mid_bodyShaper','l_ring_2_bodyShaper','l_ring_2_shaperCurve1_shape2.cv[4]'], 
                    'pinky_left':['l_root_pinky_loc','l_pinky_1_bodyShaper',
                                  'l_pinky_mid_bodyShaper','l_pinky_2_bodyShaper',
                                  'l_pinky_1_shaperCurve3_shape2.cv[4]'],                     
                    'clavicle_left':['l_clav_loc','l_arm_loc'],
                    'clavicle_right':['r_clav_loc','r_arm_loc'],
                    'arm_right':['r_arm_loc','r_lwr_arm_loc','r_hand_bodyShaper'],
                    'thumb_right':['r_thumb_1_bodyShaper','r_thumb_mid_bodyShaper',
                                   'r_thumb_2_bodyShaper','r_thumb_3_shaper1_shape2.cv[4]'],
                    'index_right':['r_root_index_loc','r_index_1_bodyShaper',
                                   'r_index_mid_bodyShaper','r_index_2_bodyShaper','r_index_2_shaperCurve1_shape2.cv[4]'], 
                    'middle_right':['r_root_middle_loc','r_middle_1_bodyShaper',
                                    'r_middle_mid_bodyShaper','r_middle_2_bodyShaper','r_middle_2_shaperCurve1_shape2.cv[4]'], 
                    'ring_right':['r_root_ring_loc','r_ring_1_bodyShaper',
                                  'r_ring_mid_bodyShaper','r_ring_2_bodyShaper','r_ring_2_shaperCurve1_shape2.cv[4]'], 
                    'pinky_right':['r_root_pinky_loc','r_pinky_1_bodyShaper',
                                   'r_pinky_mid_bodyShaper','r_pinky_2_bodyShaper',
                                   'r_pinky_1_shaperCurve3_shape2.cv[4]'],                         
                    }


def verify_sizingData(mAsset = None, skinDepth = .75):
    """
    Gather info from customization asset
    """
    _str_funcName = 'verify_sizingData'	
    d_initialData = {}

    try:#>>> Verify our arg
        mAsset = cgmMeta.validateObjArg(mAsset,mClass = 'cgmMorpheusMakerNetwork',noneValid = False)
        _str_funcName = "{0}('{1}')".format(_str_funcName,mAsset.cgmName)	
    except Exception,error:
        raise Exception,"{0}Verify  fail | {1}".format(_str_funcName,error)

    #>> Collect our positional info
    #====================================================================
    #try:
        #mObjSet = mAsset.objSetAll#Should I use this or the message info
        #l_controlsBuffer = mAsset.objSetAll.value
    #except Exception,error:
        #raise Exception,"{0}Initial buffer fail | {1}".format(_str_funcName,error)
    try:
        mayaMainProgressBar = gui.doStartMayaProgressBar(len(l_modulesToDoOrder))

        for str_moduleKey in l_modulesToDoOrder:
            try:
                if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                    break
                mc.progressBar(mayaMainProgressBar, edit=True, status = "On {0} | '{1}'...".format(_str_funcName,str_moduleKey), step=1)

                if str_moduleKey not in d_moduleControls.keys():
                    log.warning("Missing controls info for: '%s'"%str_moduleKey)
                    return False
                log.debug("{0} >> On str_moduleKey: '{1}'...".format(_str_funcName,str_moduleKey))
                controls = d_moduleControls.get(str_moduleKey)
                posBuffer = []
                for c in controls:
                    if not mc.objExists(c):
                        log.warning("Necessary positioning control not found: '%s'"%c)
                        return False
                    else:
                        log.debug("{0} >> found control: '{1}'".format(_str_funcName,c))
                        i_c = cgmMeta.cgmNode(c)
                        if i_c.isComponent():#If it's a component
                            log.debug("{0} >> Component Mode!".format(_str_funcName))
                            i_loc = cgmMeta.cgmObject(mc.spaceLocator()[0])#make a loc
                            Snap.go(i_loc.mNode,targets = c,move = True, orient = False)#Snap to the surface
                            if '.f' in i_c.getComponent():
                                mc.move(0,0,-skinDepth,i_loc.mNode,r=True,os=True)
                            #i_loc.tz -= skinDepth#Offset on z by skin depth
                            pos = i_loc.getPosition()#get position
                            i_loc.delete()
                        else:
                            pos = i_c.getPosition()
                        if not pos:return False
                        posBuffer.append(pos)
                d_initialData[str_moduleKey] = posBuffer
            except Exception,error:
                raise Exception,"'{0}' key fail | {1}".format(str_moduleKey,error)
    except Exception,error:
        try:gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        except:pass	
        raise Exception,"{0} fail | {1}".format(_str_funcName,error)
    try:gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
    except:pass
    return d_initialData

def verifyMorpheusNodeStructure(mMorpheus):
    """"
    Returns a defined Morpheus asset

    What is a morpheus asset
    """
    _str_funcName = 'verifyMorpheusNodeStructure'
    assert mMorpheus.mClass == 'cgmMorpheusPuppet',"Not a cgmMorpheusPuppet"
    d_moduleInstances = {}

    def returnModuleMatch(moduleKey):
        for i_m in mMorpheus.moduleChildren:
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

    try:
        try:# Create the modules
            #=====================================================================
            mayaMainProgressBar = gui.doStartMayaProgressBar(len(l_modulesToDoOrder))
            for str_moduleKey in l_modulesToDoOrder:
                try:
                    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                        break
                    mc.progressBar(mayaMainProgressBar, edit=True, status = "On '%s'..."%(str_moduleKey), step=1)

                    if str_moduleKey not in d_moduleParents.keys():#Make sure we have a parent
                        raise StandardError, "Missing parent info for: '%s'"%str_moduleKey
                    if str_moduleKey not in d_moduleCheck.keys():#Make sure we have a parent
                        raise StandardError, "Missing check info for: '%s'"%str_moduleKey
                        return False  

                    if str_moduleKey in d_moduleTemplateSettings.keys():#Make sure we have settings
                        d_settingsDict = d_moduleTemplateSettings[str_moduleKey]
                    elif d_moduleCheck[str_moduleKey]['moduleType'] in d_moduleTemplateSettings.keys():
                        d_settingsDict = d_moduleTemplateSettings[ d_moduleCheck[str_moduleKey]['moduleType'] ]            
                    else:
                        log.debug("Missing limb info for: '%s'"%str_moduleKey)
                        return False

                    log.debug("'{0}' structure check...".format(str_moduleKey))                
                    if str_moduleKey in d_moduleInstances.keys():#if it's already stored, use it
                        i_module = d_moduleInstances[str_moduleKey]
                    else:
                        i_module = mMorpheus.getModuleFromDict(checkDict = d_moduleCheck[str_moduleKey])#Look for it
                        d_moduleInstances[str_moduleKey] = i_module#Store it if found
                    if not i_module:
                        log.debug("'{0}' creating...".format(str_moduleKey))                
                        kw_direction = False
                        kw_name = False
                        if 'cgmDirection' in d_moduleCheck[str_moduleKey].keys():
                            kw_direction = d_moduleCheck[str_moduleKey].get('cgmDirection')
                        if 'cgmName' in d_moduleCheck[str_moduleKey].keys():
                            kw_name = d_moduleCheck[str_moduleKey].get('cgmName')            
                        i_module = mMorpheus.addModule(mClass = 'cgmLimb',mType = d_moduleCheck[str_moduleKey]['moduleType'],name = kw_name, direction = kw_direction)
                        d_moduleInstances[str_moduleKey] = i_module#Store it

                    if i_module:
                        log.debug("'{0}' verifying...".format(str_moduleKey))                
                        i_module.__verify__()

                    #>>> Settings
                    log.debug("'{0}' settings check...".format(str_moduleKey))                		
                    for key in d_settingsDict.keys():
                        i_templateNull = i_module.templateNull
                        if i_templateNull.hasAttr(key):
                            log.debug("attr: '%s'"%key)  
                            log.debug("setting: '%s'"%d_settingsDict.get(key))                  
                            try:i_templateNull.__setattr__(key,d_settingsDict.get(key)) 
                            except:log.warning("attr failed: %s"%key)

                    #>>>Parent stuff       
                    log.debug("'{0}' parent check...".format(str_moduleKey))                
                    if d_moduleParents.get(str_moduleKey):#If we should be looking for a module parent
                        if d_moduleParents.get(str_moduleKey) in d_moduleInstances.keys():
                            i_moduleParent = False
                            if i_module.getMessage('moduleParent') and i_module.getMessage('moduleParent') == [d_moduleInstances[d_moduleParents[str_moduleKey]].mNode]:
                                i_moduleParent = None
                            else:
                                i_moduleParent = d_moduleInstances[d_moduleParents.get(str_moduleKey)]
                        else:
                            i_moduleParent = mMorpheus.getModuleFromDict(checkDict = d_moduleCheck.get(d_moduleParents.get(str_moduleKey)))

                        if i_moduleParent is None:
                            log.debug("'{0}' | moduleParent already connected: '{1}'".format(str_moduleKey,d_moduleParents.get(str_moduleKey)))                
                        elif i_moduleParent:
                            i_module.doSetParentModule(i_moduleParent.mNode)
                        else:
                            log.debug("'{0}' | moduleParent not found from key: '{1}'".format(str_moduleKey,d_moduleParents.get(str_moduleKey)))
                except Exception,error:
                    raise Exception,"'{0}' | {1}".format(str_moduleKey,error)		    
        except Exception,error:raise Exception,"{0} create modules fail | {1}".format(_str_funcName,error)

        # For each module
        #=====================================================================
        gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        #i_limb.getGeneratedCoreNames()   
        return mMorpheus

    except Exception,error:
        gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    	
        raise Exception,"{0} fail | error: {1}".format(_str_funcName,error)


def setState(mAsset,state = 0,
             **kws):
    """
    """ 
    _str_funcName = 'verifyMorpheusNodeStructure'	        
    assert mAsset.mClass == 'cgmMorpheusMakerNetwork', "Not a customization Network"
    assert mAsset.mPuppet.mClass == 'cgmMorpheusPuppet',"Puppet isn't there"

    try:#>>>Kw defaults
        rebuildFrom = kws.get('rebuildFrom') or None
        forceNew =  kws.get('forceNew') or False
        tryTemplateUpdate = kws.get('tryTemplateUpdate') or True
        loadTemplatePose = kws.get('loadTemplatePose') or True

        mi_Morpheus = mAsset.mPuppet
        d_customizationData = verify_sizingData(mAsset)
    except Exception,error:
        raise Exception,"{0} defaults fail | {1}".format(_str_funcName,error)

    try:#connect our geo to our unified mesh geo
        '''
	if mAsset.getMessage('baseBodyGeo'):
	    mi_Morpheus.connectChildNode(mAsset.getMessage('baseBodyGeo')[0],'unifiedGeo')
	else:
	    log.error("{0} no baseBody geo linked to mAsset".format(_str_funcName))
	    return False	
	'''
        if not d_customizationData:
            log.error("{0} no customization data found".format(_str_funcName))
            return False
    except Exception,error:
        raise Exception,"{0} validation fail | {1}".format(_str_funcName,error)

    try:
        mayaMainProgressBar = gui.doStartMayaProgressBar(len(l_modulesToDoOrder))

        for str_moduleKey in l_modulesToDoOrder:
            try:
                if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                    break
                mc.progressBar(mayaMainProgressBar, edit=True, status = "Setting:'%s'..."%(str_moduleKey), step=1)
                mi_module = mi_Morpheus.getModuleFromDict(checkDict = d_moduleCheck[str_moduleKey])
                if not mi_module:
                    log.warning("Cannot find Module: '%s'"%str_moduleKey)
                    return False
                log.debug("Building: '%s'"%str_moduleKey)
                try:
                    kws['sizeMode'] = 'manual'
                    kws['posList'] = d_customizationData.get(str_moduleKey)
                    mi_module.setState(state,**kws)
                except StandardError,error:
                    log.error("Set state fail: '%s'"%mi_module.getShortName())
                    raise StandardError,error
            except Exception,error:
                raise Exception,"'{0}' | {1}".format(str_moduleKey,error)		
        gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
    except Exception,error:
        if kws:log.info("{0} kws : {1}".format(_str_funcName,kws))
        gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar  
        log.error(error)
        return False

def updateTemplate(mAsset,**kws):  
    assert mAsset.mClass == 'cgmMorpheusMakerNetwork', "Not a customization Network"
    assert mAsset.mPuppet.mClass == 'cgmMorpheusPuppet',"Puppet isn't there"
    _str_funcName = 'updateTemplate'	        

    try:
        d_customizationData = verify_sizingData(mAsset)
        i_Morpheus = mAsset.mPuppet
        if not d_customizationData:
            raise ValueError,"No customization data found"
    except Exception,error:
        raise Exception,"{0} validate fail | {1}".format(_str_funcName,error)

    try:
        mayaMainProgressBar = gui.doStartMayaProgressBar(len(l_modulesToDoOrder))

        for str_moduleKey in l_modulesToDoOrder:
            try:
                if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                    break
                mc.progressBar(mayaMainProgressBar, edit=True, status = "Setting:'%s'..."%(str_moduleKey), step=1)

                i_module = i_Morpheus.getModuleFromDict(checkDict = d_moduleCheck[str_moduleKey])
                if not i_module:
                    log.warning("Cannot find Module: '%s'"%str_moduleKey)
                    return False

                i_module.templateSettings_call('store')		
                i_module.doSize(sizeMode = 'manual',
                                posList = d_customizationData.get(str_moduleKey))
                i_module.doTemplate(tryTemplateUpdate = True,forceNew = True,
                                    **kws)        
            except Exception,error:
                raise Exception,"'{0}' | {1}".format(str_moduleKey,error)		
        gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
    except Exception,error:
        if kws:log.info("{0} kws : {1}".format(_str_funcName,kws))
        gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar  
        log.error(error)
        return False


#Shared Settings
#========================= 
_d_KWARG_mMorpheusAsset = {'kw':'mMorpheusAsset',"default":None,'help':"cgmMorpheusMakerNetwork mNode or str name","argType":"cgmPuppet"}

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Asset Wrapper
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
l_geoGroups = ['bodyGeo','bsGeo','unifiedGeo','earGeo','eyeGeo','customGeo','eyebrowGeo','teethGeo','tongueGeo']
l_earGeoGroups = ['left_earGeo','right_earGeo']
l_eyeGeoGroups = ['left_eyeGeo','right_eyeGeo']
l_teethGeoGroups = ['upper_teethGeo','lower_teethGeo']
l_bsTargetGroups = ['faceTargets','bodyTargets']	
d_geoStoreKeyToGeoGroups = {'tongue':'tongueGeoGroup',
                            'unified':'unifiedGeoGroup',
                            'uprTeeth':'upper_teethGeoGroup',
                            'lwrTeeth':'lower_teethGeoGroup',
                            'eyebrow':'eyebrowGeoGroup',
                            'earLeft':'left_earGeoGroup',
                            'earRight':'right_earGeoGroup',
                            'eyeLeft':'left_eyeGeoGroup',
                            'eyeRight':'right_eyeGeoGroup',
                            'body':'bodyGeoGroup'}

#List of priorities of tags to look for joint data for
d_geoGroupTagToSkinClusterTag = {'tongue':['tongue','jaw','head'],
                                 'unified':['bodyNoEyes'],
                                 'uprTeeth':['head','uprTeeth'],
                                 'lwrTeeth':['lowerTeeth','jaw','head'],
                                 'eyebrow':['eyebrow','uprHead','head'],
                                 'earLeft':['earLeft','uprHead','head'],
                                 'earRight':['earRight','uprHead','head'],
                                 'eyeLeft':['eyeLeft','uprHead','head'],
                                 'eyeRight':['eyeRight','uprHead','head'],
                                 'body':['bodySansEyes']}

class MorpheusNetworkFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """	
        try:
            try:asset = kws['mMorpheusAsset']
            except:
                try:asset = args[0]
                except:raise StandardError,"No kw or arg asset found'"
            if asset.mClass not in ['cgmMorpheusMakerNetwork']:
                raise StandardError,"[mMorpheusAsset: '%s']{Not a asset!}"%asset.mNode
        except Exception,error:raise StandardError,"MorpheusNetworkFunc failed to initialize | %s"%error
        self._str_funcName= "testMorpheusNetworkFunc"		
        super(MorpheusNetworkFunc, self).__init__(*args, **kws)
        self._mi_asset = asset
        self._b_ExceptionInterupt = False
        self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset]	
        #=================================================================

def puppet_updateGeoFromAsset(*args,**kws):
    '''
    Function to gather, duplicate and place geo for a Morpheus asset

    Geo we should have:
    1) Unified body geo for curve casing
    2) Additional geo in appropriate groups
    3) Reset body for blendshapes
    4) Blendshape building here?
    '''
    class fncWrap(MorpheusNetworkFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset,
                                         #{'kw':'clean',"default":'Morphy_customizationNetwork',"argType":'morpheusBipedCustomizationAsset','help':"This should be a customization asset"},
                                         ]
            self.__dataBind__(*args,**kws)
            self._str_funcName = "morphyAsset.puppet_updateGeoFromAsset('{0}')".format(self._mi_asset.cgmName)		    	    
            self.__updateFuncStrings__()
            self.l_funcSteps = [{'step':'Verify','call':self._fncStep_validate_},
                                {'step':'Mesh creation','call':self._fncStep_process_},
                                ]	

        def _fncStep_validate_(self):
            if not self._mi_asset.getMessage('mPuppet'):
                raise ValueError,"Missing Puppet"
            self._mi_puppet = self._mi_asset.mPuppet
            self._mi_puppetMasterNull = self._mi_puppet.masterNull
            self._mi_puppetGeoGroup = self._mi_puppetMasterNull.geoGroup

            self.l_baseBodyGeo = self._mi_asset.getMessage('baseBodyGeo')
            if not self.l_baseBodyGeo:
                raise ValueError,"Missing baseBodyGeo"		

            d_AssetGeo = get_assetActiveGeo(self._mi_asset) or {}
            if not d_AssetGeo.get('d_geoTargets'):
                raise ValueError,"geo_getActive failed to find any geo"
            self.d_AssetGeo = d_AssetGeo

            puppet_purgeGeo(self._mi_asset)


        def _fncStep_process_(self):
            try:
                mi_puppet = self._mi_puppet
            except Exception,error:
                raise Exception,"Bring local fail | {0}".format(error)

            self.log_warning("This is a wip function. This needs to resolve what final geo is being used better")

            try:
                if not self._mi_puppet.getMessage('unifiedGeo'):
                    self.log_warning("Creating unified geo...THIS NEEDS TO BE A BETTER METHOD AT SOME POINT USING REAL UNIFED GEO CALL")
                    newMesh = mc.duplicate(self.l_baseBodyGeo[0])
                    mMesh = cgmMeta.cgmObject(newMesh[0])
                    mMesh.doStore('cgmName',"{0}.cgmName".format(mi_puppet.mNode),attrType = 'msg')
                    attributes.doSetLockHideKeyableAttr(mMesh.mNode,False,True,True)
                    #mMesh.addAttr('cgmName','DONOTTOUCH_RESET',attrType='string',lock=True)
                    mMesh.parent = self._mi_puppetGeoGroup.unifiedGeoGroup#...parent it		    
                    mMesh.doName()		
                    self._mi_puppet.doStore('unifiedGeo',mMesh)

                    mMesh.setDrawingOverrideSettings(pushToShapes=False)

                else:
                    self.log_info("Unified geo found")
            except Exception,error:raise Exception,"Base Geo fail | {0}".format(error)		
                #i_target.visibility = False	

            try:
                for str_key in self.d_AssetGeo.get('d_geoTargets'):
                    if str_key in ['body']:continue
                    buffer = self.d_AssetGeo.get('d_geoTargets')[str_key]
                    if buffer:
                        for obj in buffer:
                            self.log_debug("'{0}' |  need to duplicate: '{1}'".format(str_key,obj))
                            newMesh = mc.duplicate(obj)
                            mMesh = cgmMeta.cgmObject(newMesh[0])
                            mMesh.doCopyNameTagsFromObject(obj)
                            attributes.doSetLockHideKeyableAttr(mMesh.mNode,False,True,True)			    
                            #mMesh.addAttr('cgmName','DONOTTOUCH_RESET',attrType='string',lock=True)
                            mMesh.parent = False
                            self.log_debug("'{0}' |  parenting to: '{1}'".format(str_key,d_geoStoreKeyToGeoGroups.get(str_key)))
                            mMesh.parent = self._mi_puppetGeoGroup.getMessageAsMeta(d_geoStoreKeyToGeoGroups.get(str_key))#...parent it		    
                            mMesh.doName()	

                            mMesh.setDrawingOverrideSettings(pushToShapes=False)

            except Exception,error:raise Exception,"Geo duplication | {0}".format(error)	    
            return True

    return fncWrap(*args,**kws).go()

def puppet_purgeGeo(*args,**kws):
    '''
    Function to gather, duplicate and place geo for a Morpheus asset
    '''
    class fncWrap(MorpheusNetworkFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset,
                                         #{'kw':'clean',"default":'Morphy_customizationNetwork',"argType":'morpheusBipedCustomizationAsset','help':"This should be a customization asset"},
                                         ]
            self.__dataBind__(*args,**kws)
            self._str_funcName = "morphyAsset.puppet_purgeGeo('{0}')".format(self._mi_asset.cgmName)		    	    
            self.__updateFuncStrings__()
            self.l_funcSteps = [{'step':'Clean','call':self._fncStep_clean_},
                                ]	

        def _fncStep_clean_(self):
            if not self._mi_asset.getMessage('mPuppet'):
                raise ValueError,"Missing Puppet"
            self._mi_puppet = self._mi_asset.mPuppet
            self._mi_puppetMasterNull = self._mi_puppet.masterNull
            self._mi_puppetGeoGroup = self._mi_puppetMasterNull.geoGroup

            self.l_baseBodyGeo = self._mi_asset.getMessage('baseBodyGeo')
            if not self.l_baseBodyGeo:
                raise ValueError,"Missing baseBodyGeo"	

            try:
                mi_puppet = self._mi_puppet
            except Exception,error:
                raise Exception,"Bring local fail | {0}".format(error)

            d_currentPuppetGeo = get_puppetGeo(self._mi_asset)
            if d_currentPuppetGeo.get('d_geoTargets'):
                for str_key in d_currentPuppetGeo.get('d_geoTargets'):
                    buffer = d_currentPuppetGeo.get('d_geoTargets')[str_key]
                    if buffer:
                        for obj in buffer:
                            #self.log_info("'{0}' |  deleting: '{1}'".format(str_key,obj.p_nameShort))			    
                            try:mc.delete(obj.mNode)
                            except Exception,error:self.log_error("{0} failed to delete | {1}".format(obj,error))

    return fncWrap(*args,**kws).go()

def puppet_verifyGeoDeformation(*args,**kws):
    '''
    '''
    class fncWrap(MorpheusNetworkFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset,
                                         #{'kw':'clean',"default":'Morphy_customizationNetwork',"argType":'morpheusBipedCustomizationAsset','help':"This should be a customization asset"},
                                         ]
            self.__dataBind__(*args,**kws)
            self._str_funcName = "morphyAsset.puppet_verifyGeoDeformation('{0}')".format(self._mi_asset.cgmName)		    	    
            self.__updateFuncStrings__()
            self.l_funcSteps = [{'step':'Verify','call':self._fncStep_validate_},
                                {'step':'Skinning','call':self._fncStep_skinning_},
                                ]	

        def _fncStep_validate_(self):
            if not self._mi_asset.getMessage('mPuppet'):
                raise ValueError,"Missing Puppet"

            self._mi_puppet = self._mi_asset.mPuppet
            if not self._mi_puppet.isSkeletonized():
                return self._FailBreak_("Puppet not skeletonized")

            self._mi_puppetMasterNull = self._mi_puppet.masterNull
            self._mi_puppetGeoGroup = self._mi_puppetMasterNull.geoGroup

            self._d_skinBindDict = self._mi_puppet._UTILS.get_jointsBindDict(self._mi_puppet)

            d_puppetGeo = get_puppetGeo(self._mi_asset) or {}
            if not d_puppetGeo.get('d_geoTargets'):
                raise ValueError,"get_puppetGeo failed to find any geo"
            self.d_puppetGeo = d_puppetGeo

        def _fncStep_skinning_(self):
            try:
                mi_puppet = self._mi_puppet
            except Exception,error:
                raise Exception,"Bring local fail | {0}".format(error)

            try:
                #reload(deformers)
                for str_key in self.d_puppetGeo.get('d_geoTargets'):
                    try:
                        __ml_skinJoints = False
                        l_geo = self.d_puppetGeo.get('d_geoTargets')[str_key]
                        if l_geo:
                            try:l_skinKeyBuffer = d_geoGroupTagToSkinClusterTag[str_key]
                            except Exception,error:raise Exception,"Skin key list fail | {0}".format(str_key)
                            self.log_info("...looking to skin to one of {0}".format(l_skinKeyBuffer))
                            for k in l_skinKeyBuffer:
                                buffer = self._d_skinBindDict.get(k)
                                if buffer:
                                    self.log_info("found skin joints on key: {0} | cnt : {1}".format(k,len(buffer)))
                                    __ml_skinJoints = buffer
                                    break			    
                            for mObj in l_geo:
                                try:
                                    str_shortName = mObj.p_nameShort			    
                                    self.log_info("'{0}' | Checking: '{1}'".format(str_key,str_shortName))			    
                                    if deformers.isSkinned(mObj.mNode):
                                        self.log_info("... is skinned")
                                    else:
                                        if not __ml_skinJoints:
                                            raise ValueError,"No skin joints found"
                                        self.log_info("Skinning: '{0}'".format(mObj))
                                        toBind = [mJnt.mNode for mJnt in __ml_skinJoints] + [mObj.mNode]
                                        cluster = mc.skinCluster(toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
                                        mi_cluster = cgmMeta.cgmNode(cluster[0])
                                        mi_cluster.doStore('cgmName',mObj.mNode)					
                                        #mi_cluster.doCopyNameTagsFromObject(mObj.mNode,ignore=['cgmTypeModifier','cgmType'])
                                        mi_cluster.addAttr('mClass','cgmNode',attrType='string',lock=True)
                                        mi_cluster.doName()
                                except Exception,error:
                                    raise Exception,"mObj fail {0} | {1}".format(mObj,error)
                    except Exception,error:
                        raise Exception,"key {0} | {1}".format(str_key,error)
            except Exception,error:raise Exception,"Geo duplication | {0}".format(error)	    
            return True

    return fncWrap(*args,**kws).go()

def get_assetActiveGeo(*args,**kws):
    '''
    This function should return the active geo from the asset to then ensure that the puppet has as well.
    '''
    class fncWrap(MorpheusNetworkFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset] 
            self._str_funcName = "morphyAsset.get_assetActiveGeo('{0}')".format(self._mi_asset.cgmName)
            self.l_funcSteps = [{'step':'Validate','call':self._fncStep_validate_},
                                {'step':'Base Body','call':self._fncStep_baseBodyCheck_},
                                {'step':'Geo Groups','call':self._fncStep_searchGeoGroups_},
                                ]	

            self.__dataBind__(*args,**kws)
            #self.__updateFuncStrings__()
            self._returnDict = {}

        def _fncStep_validate_(self):
            self._mi_assetMasterNull = self._mi_asset.masterNull
            self._mi_assetGeoGroup = self._mi_assetMasterNull.geoGroup	    

        def _fncStep_baseBodyCheck_(self):
            self.log_warning("This is a wip function. This needs to resolve what final geo is being used better")
            try:
                self.log_info("Base body geo: {0}".format(self._mi_asset.baseBodyGeo))
            except Exception,error: raise Exception,"gather fail | error: {0}".format(error)
            #self._returnDict['baseBody']
            self._returnDict['baseBody'] = self._mi_asset.baseBodyGeo

        def _fncStep_searchGeoGroups_(self):
            try:#> Gather geo ------------------------------------------------------------------------------------------	    
                self._returnDict['md_geoGroups'] = {}
                self._returnDict['d_geoTargets']= {}
                d_geoGroupsToCheck = MORPHYDATA._d_customizationGeoGroupsToCheck

                for key in d_geoGroupsToCheck.keys():
                    try:
                        self.log_debug("Checking : '{0}' | msgAttr: '{1}'".format(key,d_geoGroupsToCheck[key]))
                        buffer = self._mi_assetMasterNull.getMessage(d_geoGroupsToCheck[key])
                        if not buffer:raise RuntimeError,"Group not found"			    
                        mi_group = cgmMeta.validateObjArg(buffer,mayaType = ['group'])
                        l_geoGroupObjs = mi_group.getAllChildren(fullPath = True)
                        if not l_geoGroupObjs:
                            self.log_warning("Empty group: '{0}'".format(mi_group.p_nameShort))
                        else:
                            l_toSkin = []
                            for o in l_geoGroupObjs:
                                if search.returnObjectType(o) in ['mesh','nurbsSurface']:
                                    if attributes.doGetAttr(o,'v'):
                                        l_toSkin.append(o) 
                                    else:
                                        self.log_info("'{0}' | Not visible. Ignoring: '{1}'".format(key,o))				    
                                else:self.log_debug("Not skinnable: '{0}'".format(o))				    
                            if not l_toSkin:
                                self.log_warning("No skinnable objects found")
                            else:
                                self._returnDict['d_geoTargets'][key] = l_toSkin 
                                self.log_debug("--- Good Geo for {0}:".format(key))			    
                                for o in l_toSkin:
                                    self.log_debug("     '{0}'".format(o))				
                        self._returnDict['md_geoGroups'][key]  = mi_group
                    except Exception,error:raise Exception,"{0} | {1}".format(key,error)			
            except Exception,error:
                raise Exception,"Geo gather fail | {0}".format(error)	    

            #self.log_infoDict(self._returnDict)
            return self._returnDict
    return fncWrap(*args,**kws).go()

def get_puppetGeo(*args,**kws):
    '''
    This function should return the active geo from the asset to then ensure that the puppet has as well.
    '''
    class fncWrap(MorpheusNetworkFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset] 
            self._str_funcName = "morphyAsset.get_puppetGeo('{0}')".format(self._mi_asset.cgmName)
            self.l_funcSteps = [{'step':'Validate','call':self._fncStep_validate_},
                                {'step':'Geo Groups','call':self._fncStep_searchGeoGroups_},
                                ]	

            self.__dataBind__(*args,**kws)

        def _fncStep_validate_(self):
            if not self._mi_asset.getMessage('mPuppet'):
                raise ValueError,"Missing Puppet"
            self._mi_puppet = self._mi_asset.mPuppet
            if not self._mi_puppet.getMessage('masterNull'):
                raise ValueError,"Puppet missing masterNull. Reverify and rerun"	
            self._mi_puppetMasterNull = self._mi_puppet.masterNull
            self._mi_puppetGeoGroup = self._mi_puppetMasterNull.geoGroup

            self._returnDict = {}

        def _fncStep_searchGeoGroups_(self):
            try:#> Gather geo ------------------------------------------------------------------------------------------	    
                self._returnDict['md_geoGroups'] = {}
                self._returnDict['d_geoTargets']= {}


                for key in d_geoStoreKeyToGeoGroups.keys():
                    try:
                        self.log_debug("Checking : '{0}' | msgAttr: '{1}'".format(key,d_geoStoreKeyToGeoGroups[key]))
                        buffer = self._mi_puppetGeoGroup.getMessage(d_geoStoreKeyToGeoGroups[key])
                        if not buffer:raise RuntimeError,"Group not found"			    
                        mi_group = cgmMeta.validateObjArg(buffer,mayaType = ['group','transform'])
                        l_geoGroupObjs = mi_group.getAllChildren(fullPath = True)
                        if not l_geoGroupObjs:
                            self.log_debug("Empty group: '{0}'".format(mi_group.p_nameShort))
                        else:
                            l_toSkin = []
                            for o in l_geoGroupObjs:
                                if search.returnObjectType(o) in ['mesh','nurbsSurface']:
                                    l_toSkin.append(cgmMeta.cgmObject(o)) 
                                else:
                                    self.log_debug("Not skinnable: '{0}'".format(o))				    
                            if not l_toSkin:
                                self.log_warning("No skinnable objects found")
                            else:
                                self._returnDict['d_geoTargets'][key] = l_toSkin 
                                self.log_debug("--- Good Geo for {0}:".format(key))			    
                                for o in l_toSkin:
                                    self.log_debug("     '{0}'".format(o))				
                        self._returnDict['md_geoGroups'][key]  = mi_group
                    except Exception,error:raise Exception,"{0} | {1}".format(key,error)			
            except Exception,error:
                raise Exception,"Geo gather fail | {0}".format(error)	    

            #self.log_infoDict(self._returnDict)
            return self._returnDict
    return fncWrap(*args,**kws).go()

def puppet_verifyAll(*args,**kws):
    '''
    '''
    class fncWrap(MorpheusNetworkFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset] 
            self._str_funcName = "morphyAsset.puppet_verify('{0}')".format(self._mi_asset.cgmName)		    	    
            self.__updateFuncStrings__()
            self._b_autoProgressBar = 1
            self.l_funcSteps = [{'step':'Puppet Check','call':self._fncStep_puppet_},
                                {'step':'Nodes','call':self._fncStep_nodes_},
                                {'step':'Geo Groups','call':self._fncStep_geoGroups_},
                                {'step':'Geo','call':self._fncStep_geo_},	                        
                                {'step':'Master Control','call':self._fncStep_masterControl_},	                        	                        
                                ]	
            self.__dataBind__(*args,**kws)

        def _fncStep_puppet_(self):
            if not self._mi_asset.getMessage('mPuppet'):
                raise ValueError,"Missing Puppet"
            self._mi_puppet = self._mi_asset.mPuppet
            if not self._mi_puppet.getMessage('masterNull'):
                raise ValueError,"Puppet missing masterNull. Reverify and rerun"	

            self._mi_puppetMasterNull = self._mi_puppet.masterNull

        def _fncStep_geo_(self):
            puppet_updateGeoFromAsset(self._mi_asset)

        def _fncStep_masterControl_(self):
            #Verify we have a puppet and that puppet has a masterControl which we need for or master scale plug
            if not self._mi_puppet.getMessage('masterControl'):
                if not self._mi_puppet._verifyMasterControl():
                    raise StandardError,"MasterControl failed to verify"

            mi_assetMasterControl = self._mi_asset.masterControl#...masterControl of the asset
            mi_settings = mi_assetMasterControl.controlSettings
            mi_masterNull = self._mi_puppet.masterNull
            mi_puppetMasterControl = self._mi_puppet.masterControl
            self._mi_mi_puppetMasterControl = mi_puppetMasterControl

            mi_partsGroup = self._mi_puppet.masterNull.partsGroup
            #mi_masterNull.overrideEnabled = 1	
            #cgmMeta.cgmAttr(mi_settings.mNode,'puppetVis',lock=False).doConnectOut("%s.%s"%(mi_puppetMasterControl.mNode,'v'))	    
            cgmMeta.cgmAttr(mi_settings.mNode,'puppetVis',lock=False).doConnectOut("%s.%s"%(mi_partsGroup.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(mi_settings.mNode,'puppetLock',lock=False).doConnectOut("%s.%s"%(mi_partsGroup.mNode,'overrideDisplayType'))    
            for a in ['translate','rotate','scale']:
                cgmMeta.cgmAttr(mi_puppetMasterControl,a,lock=True)
            #mi_puppetMasterControl.v = 0

        def _fncStep_nodes_(self):
            verifyMorpheusNodeStructure(self._mi_puppet)

        def _fncStep_geoGroups_(self):
            mi_masterNull = self._mi_puppetMasterNull
            mi_geoGroup = self._mi_puppetMasterNull.geoGroup

            self.log_info("Checking geo groups...")	    
            for attr in l_geoGroups + l_earGeoGroups + l_eyeGeoGroups + l_bsTargetGroups + l_teethGeoGroups:
                try:
                    self.log_info("On: {0}".format(attr))
                    str_plug = attr+'Group'
                    str_newAttrName = '_mi_' + attr+  'Group'#Get a better attribute store string    
                    mi_geoGroup.addAttr(attr+'Group',attrType = 'messageSimple', lock = True)
                    bfr_grp = mi_geoGroup.getMessage(str_plug)
                    try:
                        if not bfr_grp:
                            #if log.getEffectiveLevel() == 10:log.debug('Creating %s'%attr)                                    
                            mGrp = cgmMeta.cgmObject(name=attr)#Create and initialize
                            mGrp.addAttr('cgmName',attr)
                            mGrp.doName()
                            mGrp.connectParentNode(mi_geoGroup.mNode,'puppet', str_plug)
                        else:
                            mGrp = mi_geoGroup.getMessageAsMeta(str_plug)
                        self.__dict__[str_newAttrName] = mGrp
                    except Exception,error:raise Exception,"Group verify fail | {0}".format(error)

                    try:
                        #>>> Special data parsing to get things named how we want
                        if not mGrp.hasAttr('cgmDirection'):
                            if 'left' in attr:
                                buffer = mGrp.cgmName
                                buffer = buffer.split('left_')
                                mGrp.doStore('cgmName',''.join(buffer[1:]),overideMessageCheck = True)		
                                mGrp.doStore('cgmDirection','left')
                            if 'right' in attr:
                                buffer = mGrp.cgmName
                                buffer = buffer.split('right_')
                                mGrp.doStore('cgmName',''.join(buffer[1:]),overideMessageCheck = True)		
                                mGrp.doStore('cgmDirection','right')
                        if not mGrp.hasAttr('cgmPosition'):
                            if 'upper' in attr:
                                buffer = mGrp.cgmName
                                buffer = buffer.split('upper_')
                                mGrp.doStore('cgmName',''.join(buffer[1:]),overideMessageCheck = True)		
                                mGrp.doStore('cgmPosition','upper')
                            if 'lower' in attr:
                                buffer = mGrp.cgmName
                                buffer = buffer.split('lower_')
                                mGrp.doStore('cgmName',''.join(buffer[1:]),overideMessageCheck = True)		
                                mGrp.doStore('cgmPosition','lower')
                        if 'Geo' in attr:
                            buffer = mGrp.cgmName
                            buffer = buffer.split('Geo')
                            mGrp.doStore('cgmName',''.join(buffer[0]),overideMessageCheck = True)		
                            mGrp.doStore('cgmTypeModifier','geo',overideMessageCheck = True)
                            mGrp.doName()
                    except Exception,error:raise Exception,"Special parse fail | {0}".format(error)

                    try:# Few Case things
                        #==============            
                        if attr in l_geoGroups:
                            mGrp.parent = mi_geoGroup
                        elif attr in l_earGeoGroups:
                            mGrp.parent = self._mi_earGeoGroup
                        elif attr in l_eyeGeoGroups:
                            mGrp.parent = self._mi_eyeGeoGroup	    
                        elif attr in l_bsTargetGroups:
                            mGrp.parent = self._mi_bsGeoGroup	
                        elif attr in l_teethGeoGroups:
                            mGrp.parent = self._mi_teethGeoGroup	
                        else:    
                            mGrp.parent = self._mi_geoGroup
                    except Exception,error:raise Exception,"Parent fail | {0}".format(error)
                    attributes.doSetLockHideKeyableAttr( mGrp.mNode )
                except Exception,error:
                    self.log_error("Group check fail. | attr: '{0}' | error: {1}".format(attr,error))	    

    return fncWrap(*args,**kws).go()

#============================================================================================================
#>>> Face Controls
#============================================================================================================
_d_faceBufferAttributes = {"sneer":{'attrs':['up','dn'],
                                      'sideAttrs':'*'},                           
                           "lipRoll":{'attrs':['upr_out','upr_in','lwr_out','lwr_in'],
                                      'sideAttrs':'*'}}

_d_controlToDrivenSetup = {'mouth':{'control':'mouth_anim',
                                    'controlType':'joystickReg',
                                    'dir':{'up':{'driven':'mouth_up',
                                                 'driver':'ty'},
                                           'down':{'driven':'mouth_dn',
                                                   'driver':'ty'},
                                           'left':{'driven':'mouth_left',
                                                   'driver':'tx'},
                                           'right':{'driven':'mouth_right',
                                                    'driver':'tx'}}}}
_d_faceControlsToConnect = {'upper_lipRoll':{'control':'upper_lipRoll_anim',
                                             'wiringDict':{'lipRoll_upr_out_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                                                           'lipRoll_upr_in_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},
                                                           'lipRoll_upr_out_right':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                                                           'lipRoll_upr_in_right':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},                                                           
                                                           }},   
                            'lower_lipRoll':{'control':'lower_lipRoll_anim',
                                             'wiringDict':{'lipRoll_lwr_out_left':{'driverAttr':'-tx','driverAttr2':'ty','mode':'cornerBlend'},
                                                           'lipRoll_lwr_in_left':{'driverAttr':'-tx','driverAttr2':'-ty','mode':'cornerBlend'},
                                                           'lipRoll_lwr_out_right':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'},
                                                           'lipRoll_lwr_in_right':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'},                                                           
                                                           }},                              
                            }

#{'lipRoll_out_left':{'driverAttr':'tx','driverAttr2':'ty','mode':'cornerBlend'}}
#_wiringDict = {'lipRoll_in_left':{'driverAttr':'tx','driverAttr2':'-ty','mode':'cornerBlend'}}
def faceControls_verify(*args, **kws):
    """
    Function to split a curve up u positionally 

    @kws
    Arg 0 | kw 'curve'(None)  -- Curve to split
    Arg 1 | kw 'points'(3)  -- Number of points to generate positions for
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            """
            """	
            super(fncWrap, self).__init__(*args, **kws)
            self._b_reportTimes = True
            self._str_funcName = 'faceControls_verify'	
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'attributeHolder',"default":None,
                                          'help':"Name of the attribute Holder"},]	    
            self.l_funcSteps = [{'step':'Verify Attribute Holder','call':self._fncStep_attributeHolder_},
                                {'step':'Verify Attributes','call':self._fncStep_attributes_},
                                {'step':'Verify Control Wiring','call':self._fncStep_controlWiring_}
                                ]	    
            self.__dataBind__(*args, **kws)

        def _fncStep_attributeHolder_(self):
            """
            """
            _obj = False
            self._mi_obj = False
            self._d_controls = {}
            
            if self.d_kws['attributeHolder'] is not None:
                _obj = cgmValid.objString(arg=self.d_kws['attributeHolder'], noneValid=True, 
                                           calledFrom=self._str_funcName)
                if not _obj:
                   return self._FailBreak_("Bad obj")
               
                self._mi_obj = cgmMeta.cgmNode(_obj)
                
            if not _obj:
                self.log_info("Must create attributeHolder")
                self._mi_obj = cgmMeta.cgmObject()
                
            if not self._mi_obj:
                return self._FailBreak_("Should have had an object by now")
            else:#...check naming stuff
                self._mi_obj.addAttr('cgmName','face')
                self._mi_obj.addAttr('cgmType','attrHolder')
                self._mi_obj.doName()
                
            self.log_info(self._mi_obj)
            self._str_attrHolder = self._mi_obj.mNode
            
        def _fncStep_attributes_(self):
            l_sections = _d_faceBufferAttributes.keys()
            l_sections.sort()
            
            for section in l_sections:
                self._mi_obj.addAttr("XXX_{0}_attrs_XXX".format(section),
                                     attrType = 'int',
                                     keyable = False,
                                     hidden = False,lock=True) 
                
                _d_section = _d_faceBufferAttributes[section]
                l_attrs = _d_section.get('attrs')
                l_attrs.sort()
                
                #Build our names
                l_sidesAttrs = _d_section.get('sideAttrs') or []
                if l_sidesAttrs == '*':
                    l_sidesAttrs = copy.copy(l_attrs)
                    
                for a in l_attrs:
                    l_name = [section,a]                    
                    l_names = []
                    if a in l_sidesAttrs:
                        for side in ['left','right']:
                            l_buffer = copy.copy(l_name)
                            l_buffer.append(side)
                            l_names.append(l_buffer)
                    if not l_names:l_names = [l_name]
                    for n in l_names:
                        #self.log_info(n)
                        self._mi_obj.addAttr("_".join(n),attrType = 'float',hidden = False)
                        
        def _fncStep_controlWiring_(self):
            for key in _d_faceControlsToConnect.keys():
                try:
                    _d_control = _d_faceControlsToConnect[key]
                    control = _d_control['control']
                    _d_wiring = _d_control['wiringDict']
                    
                    if not mc.objExists(control):
                        self.log_error("Control not found: {0}".format(control))
                        continue
                    try:
                        cgmNodeFactory.connect_controlWiring(control,self._mi_obj,
                                                             _d_wiring,
                                                             baseName = key,
                                                             trackAttr = True)
                    except Exception,error:
                        raise Exception,"wire call fail | error: {0}".format(error)                         
                    #self._d_controls[key] = cgmMeta.cgmObject(control)

                except Exception,error:
                    raise Exception,"Control '{0}' fail | error: {1}".format(key,error)                
                
    return fncWrap(*args,**kws).go()

def get_blendshapeListToMake():
    l_sections = _d_faceBufferAttributes.keys()
    l_sections.sort()    
    l_allNames = []
    for section in l_sections:        
        _d_section = _d_faceBufferAttributes[section]
        l_attrs = _d_section.get('attrs')
        l_attrs.sort()
        
        #Build our names
        l_sidesAttrs = _d_section.get('sideAttrs') or []
        if l_sidesAttrs == '*':
            l_sidesAttrs = copy.copy(l_attrs)
            
        for a in l_attrs:
            l_name = [section,a]                    
            l_names = []
            if a in l_sidesAttrs:
                for side in ['left','right']:
                    l_buffer = copy.copy(l_name)
                    l_buffer.append(side)
                    l_names.append(l_buffer)
            if not l_names:l_names = [l_name]
            for n in l_names:
                #self.log_info(n)
                l_allNames.append("_".join(n))
    
    log.info("{0} Blendshapes to create:".format(len(l_allNames)))
    for n in l_allNames:
        print(n)    