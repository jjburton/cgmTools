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
                    'leg_left':['l_upr_leg_loc','l_lwr_leg_loc','l_ankle_bodyShaper','l_ball_loc'],                    
                    'leg_right':['r_upr_leg_loc','r_lwr_leg_loc','r_ankle_bodyShaper','r_ball_loc'],                    
                    'foot_left':['l_ankle_bodyShaper','l_ball_loc','l_toes_bodyShaper'],                    
                    'foot_right':['r_ankle_bodyShaper','r_ball_loc','r_toes_bodyShaper'],                                        
                    'arm_left':['l_arm_loc','l_lwr_arm_loc','l_hand_bodyShaper'],
                    'hand_left':['l_hand_bodyShaper'],
                    'thumb_left':['l_thumb_1_bodyShaper','l_thumb_mid_bodyShaper','l_thumb_2_bodyShaper','l_thumb_3_shaper1_shape2.cv[4]'],
                    'index_left':['l_root_index_loc','l_index_1_bodyShaper','l_index_mid_bodyShaper','l_index_2_bodyShaper','l_index_2_shaperCurve1_shape2.cv[4]'], 
                    'middle_left':['l_root_middle_loc','l_middle_1_bodyShaper','l_middle_mid_bodyShaper','l_middle_2_bodyShaper','l_middle_2_shaperCurve1_shape2.cv[4]'], 
                    'ring_left':['l_root_ring_loc','l_ring_1_bodyShaper','l_ring_mid_bodyShaper','l_ring_2_bodyShaper','l_ring_2_shaperCurve1_shape2.cv[4]'], 
                    'pinky_left':['l_root_pinky_loc','l_pinky_1_bodyShaper','l_pinky_mid_bodyShaper','l_pinky_2_bodyShaper','l_pinky_1_shaperCurve3_shape2.cv[4]'],                     
                    'clavicle_left':['l_clav_loc','l_arm_loc'],
                    'clavicle_right':['r_clav_loc','r_arm_loc'],
                    'arm_right':['r_arm_loc','r_lwr_arm_loc','r_hand_bodyShaper'],
                    'thumb_right':['r_thumb_1_bodyShaper','r_thumb_mid_bodyShaper','r_thumb_2_bodyShaper','r_thumb_3_shaper1_shape2.cv[4]'],
                    'index_right':['r_root_index_loc','r_index_1_bodyShaper','r_index_mid_bodyShaper','r_index_2_bodyShaper','r_index_2_shaperCurve1_shape2.cv[4]'], 
                    'middle_right':['r_root_middle_loc','r_middle_1_bodyShaper','r_middle_mid_bodyShaper','r_middle_2_bodyShaper','r_middle_2_shaperCurve1_shape2.cv[4]'], 
                    'ring_right':['r_root_ring_loc','r_ring_1_bodyShaper','r_ring_mid_bodyShaper','r_ring_2_bodyShaper','r_ring_2_shaperCurve1_shape2.cv[4]'], 
                    'pinky_right':['r_root_pinky_loc','r_pinky_1_bodyShaper','r_pinky_mid_bodyShaper','r_pinky_2_bodyShaper','r_pinky_1_shaperCurve3_shape2.cv[4]'],                         
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
		
		i_module.storeTemplatePose()		
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
	
def geo_verify(*args,**kws):
    '''
    Function to gather, duplicate and place geo for a Morpheus asset
    '''
    class fncWrap(MorpheusNetworkFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._b_reportTimes = True
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset] 
	    self.__dataBind__(*args,**kws)
	    self._str_funcName = "morphyAsset.geo_verify('{0}')".format(self._mi_asset.cgmName)		    	    
	    self.__updateFuncStrings__()
	    self.l_funcSteps = [{'step':'Verify','call':self._fncStep_validate_},
	                        {'step':'Connect/Parent','call':self._fncStep_process_}]	

	def _fncStep_validate_(self):
	    if not self._mi_asset.getMessage('mPuppet'):
		raise ValueError,"Missing Puppet"
	    self._mi_puppet = self._mi_asset.mPuppet
		
	    self.l_baseBodyGeo = self._mi_asset.getMessage('baseBodyGeo')
	    if not self.l_baseBodyGeo:
		raise ValueError,"Missing baseBodyGeo"		
	    
	    l_geo = geo_getActive(self._mi_asset)
	    if not l_geo:
		raise ValueError,"geo_getActive failed to find any geo"
	    self.l_geo = l_geo
	    
	def _fncStep_process_(self):
	    try:
		mi_puppet = self._mi_puppet
	    except Exception,error:
		raise Exception,"Bring local fail | {0}".format(error)
	    
	    self.log_warning("This is a wip function. This needs to resolve what final geo is being used better")
	    
	    try:
		if not self._mi_puppet.getMessage('unifiedGeo'):
		    self.log_warning("Creating unified geo...")
		    
		    newMesh = mc.duplicate(self.l_baseBodyGeo[0])
		    mMesh = cgmMeta.cgmObject(newMesh[0])
		    mMesh.doStore('cgmName',"{0}.cgmName".format(mi_puppet.mNode))
		    #mMesh.addAttr('cgmName','DONOTTOUCH_RESET',attrType='string',lock=True)
		    mMesh.doName()		
		    mMesh.parent = mi_puppet.masterNull.geoGroup#...parent it
		    self._mi_puppet.doStore('unifiedGeo',mMesh.mNode)
		else:
		    self.log_info("Unified geo found")
	    except Exception,error:raise Exception,"Unified Geo fail | {0}".format(error)		
		#i_target.visibility = False	
	    
	    return True
	    #resetGeo = p.getMessage('resetGeo')
	    #unifiedGeo attr on puppet
	    '''
	    if resetGeo:#if we have one, we're good to go
		log.info('Reset Geo exists!')
	    else:
		newMesh = mc.duplicate(baseGeo)
		i_target = cgmMeta.cgmObject(newMesh[0])
		i_target.addAttr('cgmName','DONOTTOUCH_RESET',attrType='string',lock=True)
		i_target.doName()
		i_target.parent = p.masterNull.bsGeoGroup.mNode#parent it
		p.doStore('resetGeo',i_target.mNode)
		i_target.visibility = False
		
		log.info('Reset good!')'''	    
    return fncWrap(*args,**kws).go()

def geo_getActive(*args,**kws):
    '''
    Factory Rewrite of mirror functions.
    TODO -- replace the many mirror functions here
    '''
    class fncWrap(MorpheusNetworkFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    #self._b_reportTimes = True
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mMorpheusAsset] 
	    self.__dataBind__(*args,**kws)
	    self._str_funcName = "morphyAsset.geo_getActive('{0}')".format(self._mi_asset.cgmName)		    	    
	    self.__updateFuncStrings__()

	def __func__(self):
	    self.log_warning("This is a wip function. This needs to resolve what final geo is being used better")
	    #Gather, duplicate, 
	    try:
		self.log_info("Base body geo: {0}".format(self._mi_asset.baseBodyGeo))
	    except Exception,error: raise Exception,"gather fail | error: {0}".format(error)
	    
	    return self._mi_asset.baseBodyGeo

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
	    self.__dataBind__(*args,**kws)
	    self._str_funcName = "morphyAsset.puppet_verify('{0}')".format(self._mi_asset.cgmName)		    	    
	    self.__updateFuncStrings__()
	    self._b_autoProgressBar = 1
	    self.l_funcSteps = [{'step':'Puppet Check','call':self._fncStep_puppet_},
	                        #{'step':'Geo','call':self._fncStep_geo_},
	                        {'step':'Master Control','call':self._fncStep_masterControl_},	                        
	                        {'step':'Nodes','call':self._fncStep_nodes_},
	                        ]	

	def _fncStep_puppet_(self):
	    if not self._mi_asset.getMessage('mPuppet'):
		raise ValueError,"Missing Puppet"
	    self._mi_puppet = self._mi_asset.mPuppet
	    if not self._mi_puppet.getMessage('masterNull'):
		raise ValueError,"Puppet missing masterNull. Reverify and rerun"	
	    
	    
	def _fncStep_geo_(self):
	    geo_verify(self._mi_asset)
	    
	def _fncStep_masterControl_(self):
	    #Verify we have a puppet and that puppet has a masterControl which we need for or master scale plug
	    if not self._mi_puppet.getMessage('masterControl'):
		if not self._mi_puppet._verifyMasterControl():
		    raise StandardError,"MasterControl failed to verify"
	    
	    mi_assetMasterControl = self._mi_asset.masterControl#...masterControl of the asset
	    mi_settings = mi_assetMasterControl.controlSettings
	    mi_masterNull = self._mi_puppet.masterNull
	    mi_puppetMasterControl = self._mi_puppet.masterControl
	    mi_partsGroup = self._mi_puppet.masterNull.partsGroup
	    #mi_masterNull.overrideEnabled = 1	
	    #cgmMeta.cgmAttr(mi_settings.mNode,'puppetVis',lock=False).doConnectOut("%s.%s"%(mi_puppetMasterControl.mNode,'v'))	    
	    cgmMeta.cgmAttr(mi_settings.mNode,'puppetVis',lock=False).doConnectOut("%s.%s"%(mi_partsGroup.mNode,'overrideVisibility'))
	    cgmMeta.cgmAttr(mi_settings.mNode,'puppetLock',lock=False).doConnectOut("%s.%s"%(mi_partsGroup.mNode,'overrideDisplayType'))    
	    for a in ['translate','rotate','scale']:
		cgmMeta.cgmAttr(mi_puppetMasterControl,a,lock=True)
	    mi_puppetMasterControl.v = 0
	    
	def _fncStep_nodes_(self):
	    verifyMorpheusNodeStructure(self._mi_puppet)
	   
    return fncWrap(*args,**kws).go()
