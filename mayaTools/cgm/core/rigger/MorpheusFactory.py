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
l_modulesToDoOrder = ['torso','neckHead']
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

l_modulesToDoOrder = ['torso','neckHead','leg_left','leg_right',
                      'clavicle_left','arm_left',
                      'thumb_left','index_left','middle_left','ring_left','pinky_left'                      
                      'clavicle_right','arm_right',
                      'thumb_right','index_right','middle_right','ring_right','pinky_right'
                      
                      ]
"""

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
                    'neckHead':['neck_bodyShaper','head_bodyShaper'],
                    'head':['head_bodyShaper','headTop_bodyShaper'],
                    'leg_left':['l_upr_leg_bodyShaper','l_lwr_leg_bodyShaper','l_ankle_bodyShaper','l_ball_loc'],                    
                    'leg_right':['r_upr_leg_bodyShaper','r_lwr_leg_bodyShaper','r_ankle_bodyShaper','r_ball_loc'],                    
                    'foot_left':['l_ankle_bodyShaper','l_ball_loc','l_toes_bodyShaper'],                    
                    'foot_right':['r_ankle_bodyShaper','r_ball_loc','r_toes_bodyShaper'],                                        
                    'arm_left':['l_upr_arm_bodyShaper','l_lwr_arm_bodyShaper','l_hand_bodyShaper'],
                    'hand_left':['l_hand_bodyShaper'],
                    'thumb_left':['l_thumb_1_bodyShaper','l_thumb_mid_bodyShaper','l_thumb_2_bodyShaper','Morphy_Body_GEO.vtx[3]'],
                    'index_left':['Morphy_Body_GEO.f[688]','l_index_1_bodyShaper','l_index_mid_bodyShaper','l_index_2_bodyShaper','Morphy_Body_GEO.vtx[292]'], 
                    'middle_left':['Morphy_Body_GEO.f[705]','l_middle_1_bodyShaper','l_middle_mid_bodyShaper','l_middle_2_bodyShaper','Morphy_Body_GEO.vtx[188]'], 
                    'ring_left':['Morphy_Body_GEO.f[703]','l_ring_1_bodyShaper','l_ring_mid_bodyShaper','l_ring_2_bodyShaper','Morphy_Body_GEO.vtx[85]'], 
                    'pinky_left':['Morphy_Body_GEO.f[706]','l_pinky_1_bodyShaper','l_pinky_mid_bodyShaper','l_pinky_2_bodyShaper','Morphy_Body_GEO.vtx[492]'],                     
                    'clavicle_left':['Morphy_Body_GEO.f[2055]','l_upr_arm_bodyShaper'],
                    'clavicle_right':['Morphy_Body_GEO.f[4840]','r_upr_arm_bodyShaper'],
                    'arm_right':['r_upr_arm_bodyShaper','r_lwr_arm_bodyShaper','r_wristMeat_bodyShaper'],
                    'thumb_right':['r_thumb_1_bodyShaper','r_thumb_mid_bodyShaper','r_thumb_2_bodyShaper','Morphy_Body_GEO.vtx[2853]'],
                    'index_right':['Morphy_Body_GEO.f[3473]','r_index_1_bodyShaper','r_index_mid_bodyShaper','r_index_2_bodyShaper','Morphy_Body_GEO.vtx[3080]'], 
                    'middle_right':['Morphy_Body_GEO.f[3490]','r_middle_1_bodyShaper','r_middle_mid_bodyShaper','r_middle_2_bodyShaper','Morphy_Body_GEO.vtx[3006]'], 
                    'ring_right':['Morphy_Body_GEO.f[3488]','r_ring_1_bodyShaper','r_ring_mid_bodyShaper','r_ring_2_bodyShaper','Morphy_Body_GEO.vtx[2933]'], 
                    'pinky_right':['Morphy_Body_GEO.f[3491]','r_pinky_1_bodyShaper','r_pinky_mid_bodyShaper','r_pinky_2_bodyShaper','Morphy_Body_GEO.vtx[3299]'],                         
                    }


#@cgmGeneral.Timer
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
			    Snap.go(i_loc.mNode,targets = c,move = True, orient = True)#Snap to the surface
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
    except Exception,error:
	gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    	
	raise Exception,"{0} created modules fail | {1}".format(_str_funcName,error)
    
    # For each module
    #=====================================================================
    gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
    #i_limb.getGeneratedCoreNames()   
    return mMorpheus


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
	d_customizationData = verify_customizationData(mAsset)
    except Exception,error:
	raise Exception,"{0} defaults fail | {1}".format(_str_funcName,error)
    
    try:#connect our geo to our unified mesh geo
	if mAsset.getMessage('baseBodyGeo'):
	    mi_Morpheus.connectChildNode(mAsset.getMessage('baseBodyGeo')[0],'unifiedGeo')
	else:
	    log.error("{0} no baseBody geo linked to mAsset".format(_str_funcName))
	    return False	
	
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
	d_customizationData = verify_customizationData(mAsset)
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
		
		i_module.storeTemplatePose()		
		i_module.doSize(sizeMode = 'manual',
		                posList = d_customizationData.get(str_moduleKey))
		i_module.doTemplate(tryTemplateUpdate = True,
		                    **kws)        
	    except Exception,error:
		raise Exception,"'{0}' | {1}".format(str_moduleKey,error)		
	gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
    except Exception,error:
	if kws:log.info("{0} kws : {1}".format(_str_funcName,kws))
	gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar  
	log.error(error)
	return False




#>>>>>>>>>>>>>>OLD CODE, Prior to April 2014
#=====================================================================================
#>>> Utilities
#=====================================================================================
def verify_customizationData2(i_network, skinDepth = .75):
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
    log.info(i_objSet.value)
    
    controlBuffer = i_network.objSetAll.value
    for moduleKey in l_modulesToDoOrder:
        if moduleKey not in d_moduleControls.keys():
            log.warning("Missing controls info for: '%s'"%moduleKey)
            return False
        log.info("On moduleKey: '%s'"%moduleKey)
        controls = d_moduleControls.get(moduleKey)
        posBuffer = []
        for c in controls:
            if not mc.objExists(c):
                log.warning("Necessary positioning control not found: '%s'"%c)
                return False
            else:
                log.info("Found: '%s'"%c)
                i_c = cgmMeta.cgmNode(c)
                if i_c.isComponent():#If it's a component
                    log.info('Component mode')
                    i_loc = cgmMeta.cgmObject(mc.spaceLocator()[0])#make a loc
                    Snap.go(i_loc.mNode,targets = c,move = True, orient = True)#Snap to the surface
                    if '.f' in i_c.getComponent():
                        mc.move(0,0,-skinDepth,i_loc.mNode,r=True,os=True)
                    #i_loc.tz -= skinDepth#Offset on z by skin depth
                    pos = i_loc.getPosition()#get position
                    i_loc.delete()
                else:
                    pos = i_c.getPosition()
                if not pos:return False
                posBuffer.append(pos)
        d_initialData[moduleKey] = posBuffer
        
    return d_initialData
        
def verifyMorpheusNodeStructure2(i_Morpheus):
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
            raise StandardError, "Missing parent info for: '%s'"%moduleKey
        if moduleKey not in d_moduleCheck.keys():#Make sure we have a parent
            raise StandardError, "Missing check info for: '%s'"%moduleKey
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
            i_module = i_Morpheus.getModuleFromDict(checkDict = d_moduleCheck[moduleKey])#Look for it
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
                i_moduleParent = i_Morpheus.getModuleFromDict(checkDict = d_moduleCheck.get(d_moduleParents.get(moduleKey)))
            
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

def setState2(i_customizationNetwork,state = 0,
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
    
    #connect our geo to our unified mesh geo
    if i_customizationNetwork.getMessage('baseBodyGeo'):
        i_Morpheus.connectChildNode(i_customizationNetwork.getMessage('baseBodyGeo')[0],'unifiedGeo')
    
    if not d_customizationData:
        return False
    
    try:
        mayaMainProgressBar = gui.doStartMayaProgressBar(len(l_modulesToDoOrder))
        
        for moduleKey in l_modulesToDoOrder:
            if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                break
            mc.progressBar(mayaMainProgressBar, edit=True, status = "Setting:'%s'..."%(moduleKey), step=1)
            i_module = i_Morpheus.getModuleFromDict(checkDict = d_moduleCheck[moduleKey])
            if not i_module:
                log.warning("Cannot find Module: '%s'"%moduleKey)
                return False
            log.debug("Building: '%s'"%moduleKey)
            try:
                kws['sizeMode'] = 'manual'
                kws['posList'] = d_customizationData.get(moduleKey)
                i_module.setState(state,**kws)
            except StandardError,error:
                log.error("Set state fail: '%s'"%i_module.getShortName())
                raise StandardError,error
            #i_module.doSize('manual', posList = d_customizationData.get(moduleKey))
            #i_module.doTemplate()
        gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
    except Exception,error:
        gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar  
        log.error(error)
        return False
        
@r9General.Timer
def updateTemplate2(i_customizationNetwork,**kws):  
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
        
        i_module = i_Morpheus.getModuleFromDict(checkDict = d_moduleCheck[moduleKey])
        if not i_module:
            log.warning("Cannot find Module: '%s'"%moduleKey)
            return False
        log.debug("Building: '%s'"%moduleKey)
        i_module.doSize(sizeMode = 'manual',
                        posList = d_customizationData.get(moduleKey))
        i_module.doTemplate(tryTemplateUpdate = True,
                            **kws)        
    gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
        