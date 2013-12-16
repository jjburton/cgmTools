# From Python =============================================================
import copy
import re
import time
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.rigger.lib import joint_Utils as jntUtils
from cgm.core.lib import rayCaster as rayCast
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.classes import GuiFactory as gui
from cgm.core.classes import SnapFactory as Snap

from cgm.lib import (cgmMath,
                     joints,
                     rigging,
                     attributes,
                     locators,
                     distance,
                     autoname,
                     search,
                     curves,
                     dictionary,
                     lists,
                     settings,
                     modules)
reload(joints)
reload(cgmMath)
from cgm.core.lib import nameTools

#>>> Register rig functions
#=====================================================================
from cgm.core.rigger.lib.Limb import (spine,neckHead,leg,clavicle,arm,finger,thumb)
from cgm.core.rigger.lib.Face import (eyeball,eyelids,eyebrow,mouthNose)
d_moduleTypeToBuildModule = {'torso':spine,
                             'neckhead':neckHead,
                             'leg':leg,
                             'arm':arm,
                             'clavicle':clavicle,
                             'thumb':thumb,
                             'finger':finger,
                             'eyeball':eyeball,
                             'eyelids':eyelids,
                             'eyebrow':eyebrow,
                             'mouthnose':mouthNose,
                            } 
for module in d_moduleTypeToBuildModule.keys():
    reload(d_moduleTypeToBuildModule[module])

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    def __init__(self,mModule,forceNew = True,saveTemplatePose = True,**kws): 
        """
        To do:
        Add rotation order settting
        Add module parent check to make sure parent is templated to be able to move forward, or to constrain
        Add any other piece meal data necessary
        Add a cleaner to force a rebuild
        """
        # Get our base info
        #==============	        
        #>>> module null data 
        #assert mModule.mClass in ['cgmModule','cgmLimb'],"Not a module"
        assert mModule.isTemplated(),"Module is not templated"
	mc.select(cl=1)#Clear our selection because we're gonna be making joints
        #assert object is templated
        #assert ...	
	self.cls = "JointFactory.go"
	self._cgmClass = "JointFactory.go"
        self._mi_module = mModule# Link for shortness
	_str_funcName = "go.__init__(%s)"%self._mi_module.p_nameShort  
	log.info(">>> %s >>> "%(_str_funcName) + "="*75)
	
        if mModule.isSkeletonized():
            if forceNew:
                deleteSkeleton(mModule)
            else:
                log.warning("'%s' has already been skeletonized"%mModule.getShortName())
                return        
        
        #>>> store template settings
        if saveTemplatePose and not self._mi_module.getMessage('helper'):
            log.debug("Saving template pose in JointFactory.go")
            self._mi_module.storeTemplatePose()
        
        self.rigNull = self._mi_module.getMessage('rigNull')[0] or False
        self._mi_rigNull = self._mi_module.rigNull
        self._mi_puppet = self._mi_module.modulePuppet	
        self.moduleColors = self._mi_module.getModuleColors()
        self.l_coreNames = self._mi_module.coreNames.value
        self.foundDirections = False #Placeholder to see if we have it
                
        #>>> part name 
        self._partName = self._mi_module.getPartNameBase()
        self._partType = self._mi_module.moduleType.lower() or False
        self._strShortName = self._mi_module.getShortName() or False
	
        self.direction = None
        if self._mi_module.hasAttr('cgmDirection'):
            self.direction = self._mi_module.cgmDirection or None
        
        #>>> template null 
        self._mi_templateNull = self._mi_module.templateNull
	
        #>>> Gather info
        #=========================================================	
        self._l_coreNames = self._mi_module.coreNames.value  
        self.str_jointOrientation = modules.returnSettingsData('jointOrientation')
        self._d_handleToHandleJoints = {}
	

	if not hasJointSetup(self):
	    raise StandardError, "Need to add to build dict"
	
	#Skeletonize
	self.str_progressBar = gui.doStartMayaProgressBar(4)
	try:
	    if self._mi_module.mClass == 'cgmLimb':
		#Gather specific data for Limb
		#>>> Instances and joint stuff
		self.curveDegree = self._mi_templateNull.curveDegree	
		self._mi_root = self._mi_templateNull.root
		self._mi_orientRootHelper = self._mi_templateNull.orientRootHelper
		self._mi_curve = self._mi_templateNull.curve
		self._ml_controlObjects = self._mi_templateNull.msgList_get('controlObjects')
		
		log.debug("Module: %s"%self._mi_module.getShortName())
		log.debug("partType: %s"%self._partType)
		log.debug("direction: %s"%self.direction) 
		log.debug("colors: %s"%self.moduleColors)
		log.debug("coreNames: %s"%self.l_coreNames)
		log.debug("root: %s"%self._mi_root.getShortName())
		log.debug("curve: %s"%self._mi_curve.getShortName())
		log.debug("orientRootHelper: %s"%self._mi_orientRootHelper.getShortName())
		log.debug("rollJoints: %s"%self._mi_templateNull.rollJoints)
		log.debug("jointOrientation: %s"%self.str_jointOrientation)
		log.debug("hasJointSetup: %s"%hasJointSetup(self))		
		
		log.debug("mode: cgmLimb Skeletonize")
		mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Skeletonize>> step:'%s' "%(self._strShortName,'Skeletonize'), progress=0)    		
		doSkeletonizeLimb(self)
		
		mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Skeletonize>> step:'%s' "%(self._strShortName,'Special Joints'), progress=4)    				
		self.build(self)
		
		#Only going to tag our handleJoints at the very end because of message connection duplication
		for i_obj in self._ml_controlObjects:
		    i_obj.connectChildNode(self._d_handleToHandleJoints[i_obj],'handleJoint')	    
	    elif self._mi_module.mClass == 'cgmEyeball':
		log.info(">>> %s.go >> eyeball mode!"%(self._mi_module.p_nameShort))
		try:doSkeletonizeEyeball(self)
		except Exception,error:log.warning(">>> %s.go >> build failed: %s"%(self._mi_module.p_nameShort,error)) 
	    elif self._mi_module.mClass == 'cgmEyelids':
		log.info(">>> %s.go >> eyelids mode!"%(self._mi_module.p_nameShort))
		try:doSkeletonizeEyelids(self)
		except Exception,error:log.warning(">>> %s.go >> build failed: %s"%(self._mi_module.p_nameShort,error)) 
	    elif self._mi_module.mClass == 'cgmEyebrow':
		log.info(">>> %s.go >> eyebrow mode!"%(self._mi_module.p_nameShort))
		try:doSkeletonizeEyebrow(self)
		except Exception,error:log.warning(">>> %s.go >> build failed: %s"%(self._mi_module.p_nameShort,error)) 
	    elif self._mi_module.mClass == 'cgmMouthNose':
		log.info(">>> %s.go >> mouthNose mode!"%(self._mi_module.p_nameShort))
		try:doSkeletonizeMouthNose(self,**kws)
		except Exception,error:log.warning(">>> %s.go >> build failed: %s"%(self._mi_module.p_nameShort,error)) 	    
	    else:
		raise NotImplementedError,"haven't implemented '%s' skeletonizing yet yet"%self._mi_module.mClass
	except Exception,error:
	    log.error("%s.go >> build failed! | %s"%(self._strShortName,error))
	gui.doEndMayaProgressBar(self.str_progressBar)#Close out this progress bar        
	log.info("%s.go >> build completed!"%(self._strShortName) + "-"*75)
	
class JointFactoryFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
	"""
	"""
	try:
	    try:goInstance = args[0]
	    except:goInstance = kws['goInstance']
	    if not issubclass(type(goInstance),go):
		raise StandardError,"Not a JointFactory.go instance: '%s'"%goInstance
	    assert mc.objExists(goInstance._mi_module.mNode),"Module no longer exists"
	except Exception,error:raise StandardError,error
	
	super(JointFactoryFunc, self).__init__(*args,**kws)
	
	self._str_funcName = 'JointFactoryFunc(%s)'%goInstance._mi_module.p_nameShort
	self._l_ARGS_KWS_DEFAULTS = [{'kw':'goInstance',"default":goInstance}]
	
	self.__dataBind__(**kws)
	self.mi_go = goInstance
	self.mi_module = goInstance._mi_module
	
	#=================================================================
	
def hasJointSetup(self):
    if not issubclass(type(self),go):
	log.error("Not a JointFactory.go instance: '%s'"%self)
	raise StandardError
    self = self#Link
    log.debug(">>> %s.hasJointSetup >> "%(self._strShortName) + "="*75)      
    
    if self._partType not in d_moduleTypeToBuildModule.keys():
	log.error("%s.isBuildable>>> '%s' Not in d_moduleTypeToBuildModule"%(self._strShortName,self._partType))	
	return False
    
    try:#Version
	self._buildVersion = d_moduleTypeToBuildModule[self._partType].__version__    
    except:
	log.error("%s.isBuildable>>> Missing version"%(self._strShortName))	
	return False
    
    try:#Joints list
	self.build = d_moduleTypeToBuildModule[self._partType].__bindSkeletonSetup__
	self.buildModule = d_moduleTypeToBuildModule[self._partType]
    except:
	log.error("%s.isBuildable>>> Missing Joint Setup Function"%(self._strShortName))	
	return False	
    
    return True  

def doSkeletonizeEyeball(self):
    """     
    """
    #>>> Get our base info =========================================================================
    _str_funcName = "doSkeletonizeEyeball(%s)"%self._mi_module.p_nameShort  
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)   
    
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self._mi_module.mNode),"Module no longer exists"
    assert self._mi_module.mClass == 'cgmEyeball',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(_str_funcName,self._mi_module.mClass)
    ml_moduleJoints = []
    ml_buildObjects = []
    _str_orientation = self.str_jointOrientation #Link
    
    #>>> Build ====================================================================================
    #Find our helper
    mi_helper = cgmMeta.validateObjArg(self._mi_module.getMessage('helper'),noneValid=True)
    if not mi_helper:raise StandardError,"%s >>> No suitable helper found"%(_str_funcName)
    
    #See if we need to mirror the shapes stuff
    mi_helperMirror = False
    
    ml_buildObjects.append(mi_helper)
    log.info("%s >>> helper: '%s'"%(_str_funcName,mi_helper.p_nameShort))
    
    #Pupil and Iris
    if mi_helper.buildPupil:
	try:ml_buildObjects.append(mi_helper.pupilHelper)
	except Exception,error:raise StandardError,"%s >>> Missing Iris helper | error: %s "%(_str_funcName,error)
    if mi_helper.buildIris:
	try:ml_buildObjects.append(mi_helper.irisHelper)
	except Exception,error:raise StandardError,"%s >>> Missing Iris helper | error: %s "%(_str_funcName,error)
    
    log.info("%s >>> buildObjects: %s"%(_str_funcName,[o.p_nameShort for o in ml_buildObjects]))
    str_partName = self._partName
    
    #Joint build
    l_initialJoints = []
    for o in ml_buildObjects:
	l_initialJoints.append( mc.joint(p = o.getPosition()) )
    
    #Parent, tag
    for i,j in enumerate(l_initialJoints):
	i_j = cgmMeta.cgmObject(j,setClass=True)
	i_j.doCopyNameTagsFromObject( ml_buildObjects[i].mNode,ignore=['cgmTypeModifier','cgmType'] )#copy Tags
	i_j.parent = False
	ml_moduleJoints.append(i_j)
	self._mi_rigNull.connectChildNode(i_j,'%sJoint'%i_j.cgmName)
    
    #>>> Orient -------------------------------------------------------------
    #Make our up loc
    try:
	_str_upLoc = locators.locMeCvFromCvIndex(mi_helper.getShapes()[0],2)   
	mi_upLoc = cgmMeta.cgmObject(_str_upLoc)
	mi_aimLoc = mi_helper.pupilHelper.doLoc()
	v_aim = cgmValid.simpleAxis(_str_orientation[0]).p_vector
	v_up = cgmValid.simpleAxis(_str_orientation[1]).p_vector
	
	constraintBuffer = mc.aimConstraint(mi_aimLoc.mNode,ml_moduleJoints[0].mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
	mc.delete(constraintBuffer[0])    
	for o in [mi_aimLoc,mi_upLoc]:
	    o.delete()    
	#Copy eyeball orient to children
	if len(ml_moduleJoints)>1:
	    for o in ml_moduleJoints[1:]:
		o.parent = ml_moduleJoints[0]#Parent back
	    joints.doCopyJointOrient(ml_moduleJoints[0].mNode,[jnt.mNode for jnt in ml_moduleJoints[1:]])
	    
	try:#Create eye orb joint
	    i_dupJnt = ml_moduleJoints[0].doDuplicate()#Duplicate
	    i_dupJnt.addAttr('cgmName','eyeOrb')#Tag
	    ml_moduleJoints[0].parent = i_dupJnt#Parent
	    ml_moduleJoints.insert(0,i_dupJnt)
	except:
	    raise StandardError, "eye orb fail! | %s"%(_str_funcName,error)
	    
	#Connect back
	self._mi_rigNull.msgList_connect(ml_moduleJoints,'moduleJoints','rigNull')
	log.info("%s >>> built the following joints: %s"%(_str_funcName,[o.p_nameShort for o in ml_moduleJoints]))
    except Exception,error:
	raise StandardError, "%s >>> Orient fail | Error: %s"%(_str_funcName,error)
    
    #>>> Flag our handle joints
    #===========================
    try:
	for mJnt in ml_moduleJoints:
	    mJnt.doName()
	self._mi_rigNull.msgList_connect(ml_moduleJoints,'handleJoints') 
	self._mi_rigNull.msgList_connect(ml_moduleJoints,'skinJoints') 
    except Exception,error:
	raise StandardError, "%s >>> Skin/Handle connect fail | Error: %s"%(_str_funcName,error)
    
    #Connect to parent =========================================================
    try:
	if self._mi_module.getMessage('moduleParent'):#If we have a moduleParent, constrain it
	    connectToParentModule(self._mi_module)    
    except Exception,error:
	raise StandardError, "%s >>> Failed parent connect | Error: %s"%(_str_funcName,error)
    
    return True
	
def doSkeletonizeEyelids(self):
    """     
    """
    #>>> Get our base info =========================================================================
    _str_funcName = "doSkeletonizeEyelids(%s)"%self._mi_module.p_nameShort  
    log.info(">>> %s "%(_str_funcName) + "="*75)   
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self._mi_module.mNode),"Module no longer exists"
    assert self._mi_module.mClass == 'cgmEyelids',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(_str_funcName,self._mi_module.mClass)
    ml_moduleJoints = []
    _str_orientation = self.str_jointOrientation #Link
    try:#>>> Get info ====================================================================================
	#Find our helper
	mi_helper = cgmMeta.validateObjArg(self._mi_module.getMessage('helper'),noneValid=True)
	if not mi_helper:raise StandardError,"%s >>> No suitable helper found"%(_str_funcName)
	if not mi_helper.buildLids:
	    raise StandardError,"%s >>> %s.buildLids is off "%(_str_funcName,mi_helper.p_nameShort)
	
	try:mi_uprLidBase = cgmMeta.validateObjArg(mi_helper.getMessage('uprLidHelper'),noneValid=False)
	except Exception,error:raise StandardError,"%s >>> Missing uprlid helper | error: %s "%(_str_funcName,error)
	try:mi_lwrLidBase = cgmMeta.validateObjArg(mi_helper.getMessage('lwrLidHelper'),noneValid=False)
	except Exception,error:raise StandardError,"%s >>> Missing uprlid helper | error: %s "%(_str_funcName,error)
	try:int_lwrLidJoints = mi_helper.getAttr('lwrLidJoints')
	except Exception,error:raise StandardError,"%s >>> Missing lwrLid joint count | error: %s "%(_str_funcName,error)
	try:int_uprLidJoints = mi_helper.getAttr('uprLidJoints')
	except Exception,error:raise StandardError,"%s >>> Missing uprLid joint count | error: %s "%(_str_funcName,error)       
	log.info("%s >>> helper: '%s'"%(_str_funcName,mi_helper.p_nameShort))
	log.info("%s >>> mi_uprLidBase: '%s'"%(_str_funcName,mi_uprLidBase.p_nameShort))
	log.info("%s >>> mi_lwrLidBase: '%s'"%(_str_funcName,mi_lwrLidBase.p_nameShort))
	log.info("%s >>> uprCount : %s"%(_str_funcName,int_uprLidJoints))
	log.info("%s >>> lwrCount : %s"%(_str_funcName,int_lwrLidJoints))
	
	#Curves --------------------------------------------------------------------------------
	str_partName = self._partName	
	d_buildCurves = {'upr':{'crv':mi_uprLidBase,'count':int_uprLidJoints},
	                 'lwr':{'crv':mi_lwrLidBase,'count':int_lwrLidJoints}}
	
	#Orient info
	_str_upLoc = locators.locMeCvFromCvIndex(mi_helper.getShapes()[0],2)   
	mi_upLoc = cgmMeta.cgmObject(_str_upLoc)
	v_aim = cgmValid.simpleAxis(_str_orientation[0]+"-").p_vector
	v_up = cgmValid.simpleAxis(_str_orientation[1]).p_vector	
    
    except Exception,error:
	raise StandardError,"Data gather fail! | error: %s "%(error)       
    
    try:
	for k in d_buildCurves.keys():
	    mi_crv = d_buildCurves[k].get('crv')#get instance
	    int_count = d_buildCurves[k].get('count')#get int
	    log.info("%s >>> building joints for %s curve | count: %s"%(_str_funcName,k, int_count))
	    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10,startSplitFactor=.05)
	    except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(_str_funcName,error)       
	    d_buildCurves[k]['l_pos'] = l_pos#Store it
	    log.info("%s >>> '%s' pos list: %s"%(_str_funcName,k, l_pos))
	    l_jointBuffer = []
	    ml_endJoints = []
	    if k == 'lwr':l_pos = l_pos[1:-1]
	    for i,pos in enumerate(l_pos):
		try:#Create and name
		    int_last = len(l_pos)
		    mc.select(cl=True)
		    #mi_root = cgmMeta.cgmObject( mc.joint(p = mi_helper.getPosition()),setClass=True )
		    mi_end = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
		    mi_end.parent = False
		    ml_buffer = [mi_end]
		    mi_end.doCopyNameTagsFromObject( self._mi_module.mNode,ignore=['cgmTypeModifier','cgmType'] )#copy Tags
		    mi_end.addAttr('cgmName',"%sLid"%(k),lock=True)		    
		    mi_end.addAttr('cgmIterator',i,lock=True,hidden=True)
		    #mi_end.addAttr('cgmNameModifier','inner',lock=True)	
		    #if i == int_last:mi_end.addAttr('cgmNameModifier','outer',lock=True)			
		    mi_end.doName()
		    l_jointBuffer.append(mi_end)
		    ml_moduleJoints.append(mi_end)
		    ml_endJoints.append(mi_end)
		    log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(_str_funcName,k,i,[o.p_nameShort for o in ml_buffer]))
		except Exception,error:
		    raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
		try:#aim constraint
		    constraintBuffer = mc.aimConstraint(mi_helper.mNode,mi_end.mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
		    mc.delete(constraintBuffer[0])  		
		    #mi_end.parent = mi_root
		except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
		try:#copy orient
		    pass
		    #joints.doCopyJointOrient(mi_root.mNode,mi_end.mNode)		
		except Exception,error:raise StandardError,"curve: %s | pos count: %s | Copy orient fail | error: %s "%(k,i,error)       		
		try:#freeze
		    jntUtils.metaFreezeJointOrientation(mi_end)
		except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
	    #d_buildCurves[k]['nestedml_joints'] = l_jointBuffer #nested list
	    d_buildCurves[k]['ml_endJoints'] = ml_endJoints #nested list
	    self._mi_rigNull.msgList_connect(ml_endJoints,'moduleJoints_%s'%k,'rigNull')
	    
    except Exception,error:
	raise StandardError,"%s >> Joint build fail! | error: %s "%(_str_funcName,error)       
       
    for o in [mi_upLoc]:
	o.delete()      
    
    #>>> Connections
    #===========================
    try:
	#self._mi_rigNull.msgList_connect(ml_moduleJoints,'handleJoints') 
	self._mi_rigNull.msgList_connect(ml_moduleJoints,'skinJoints') 
	self._mi_rigNull.msgList_connect(ml_moduleJoints,'moduleJoints') 
	
    except Exception,error:
	raise StandardError, "%s >>> Skin/Handle connect fail | Error: %s"%(_str_funcName,error)
    
    #Connect to parent =========================================================
    try:
	if self._mi_module.getMessage('moduleParent'):#If we have a moduleParent, constrain it
	    log.info("%s >>> Need to implement Module parent connect"%(_str_funcName))
	    connectToParentModule(self._mi_module)    
    except Exception,error:
	raise StandardError, "%s >>> Failed parent connect | Error: %s"%(_str_funcName,error)
    
    return True

def doSkeletonizeEyebrow(goInstance = None):
    class fncWrap(JointFactoryFunc):
	def __init__(self,goInstance = None):
	    """
	    """	
	    super(fncWrap, self).__init__(goInstance)
	    self._str_funcName = 'doSkeletonizeEyebrow(%s)'%self.mi_module.p_nameShort
	    self._b_autoProgressBar = True
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        {'step':'Build brow','call':self._buildBrow_},
	                        {'step':'Build Cheek','call':self._buildCheek_},
	                        {'step':'Build Temple','call':self._buildTemple_},
	                        {'step':'Build midBrow','call':self._buildMidBrow_},
	                        {'step':'Build Squash and Stretch','call':self._buildSquashStretch_},
	                        {'step':'Connect','call':self._connect_}]
	    
	    assert self.mi_module.mClass == 'cgmEyebrow',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(_str_funcName,self.mi_module.mClass)
	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    
	def _gatherInfo_(self): 
	    self.str_orientation = self.mi_go.str_jointOrientation #Link
	    self.str_partName = self.mi_go._partName	
	    self.ml_moduleJoints = []
	    
	    try:
		self.l_targetMesh = self.mi_go._mi_puppet.getUnifiedGeo() or self.mi_go._mi_puppet.getGeo() or 'Morphy_Body_GEO1'#>>>>>>>>>>>>>>>>>this needs better logic   
	    except Exception,error:
		raise error
	    
	    #Find our head attach joint ------------------------------------------------------------------------------------------------
	    self.str_rootJoint = False
	    if self.mi_module.getMessage('moduleParent'):
		try:
		    mi_end = self.mi_module.moduleParent.rigNull.msgList_get('moduleJoints')[-1]
		    buffer =  mi_end.getMessage('scaleJoint')
		    if buffer:
			self.str_rootJoint = buffer[0]
		    else:
			self.str_rootJoint = mi_end.mNode
		except Exception,error:
		    log.error("%s failed to find root joint from moduleParent | %s"%(self._str_reportStart,error))
	    
	    #Orient info ------------------------------------------------------------------------------------------------
	    self.v_aimNegative = cgmValid.simpleAxis(self.str_orientation[0]+"-").p_vector
	    self.v_aim = cgmValid.simpleAxis(self.str_orientation[0]).p_vector	
	    self.v_up = cgmValid.simpleAxis(self.str_orientation[1]).p_vector	
	    
	    #Find our helpers -------------------------------------------------------------------------------------------
	    self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"%s >>> No suitable helper found"%(_str_funcName)
	    
	    self.mi_leftBrowCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftBrowHelper'),noneValid=False)
	    self.mi_rightBrowCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightBrowHelper'),noneValid=False)
	    
	    self.mi_leftTempleCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftTempleHelper'),noneValid=False)
	    self.mi_rightTempleCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightTempleHelper'),noneValid=False)
	    
	    self.mi_leftUprCheekCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftUprCheekHelper'),noneValid=False)
	    self.mi_rightUprCheekCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightUprCheekHelper'),noneValid=False)
	    
	    self.mi_squashCastHelper = cgmMeta.validateObjArg(self.mi_helper.getMessage('squashCastHelper'),noneValid=True)
	    self.mi_uprFacePivotHelper = cgmMeta.validateObjArg(self.mi_helper.getMessage('uprFacePivotHelper'),noneValid=True)
	    
	    self.mi_jawPlate = cgmMeta.validateObjArg(self.mi_helper.getMessage('jawPlate'),noneValid=True)
	    self.mi_skullPlate = cgmMeta.validateObjArg(self.mi_helper.getMessage('skullPlate'),noneValid=True)
	    
	    #Get some data from helpers --------------------------------------------------------------------------------------
	    self.int_browJointsCnt = self.mi_helper.browJoints
	    self.int_templeJointsCnt = self.mi_helper.templeJoints
	    self.int_cheekJointsCnt = self.mi_helper.cheekJoints	
	    
	    return True
	
	def _buildSquashStretch_(self): 
	    if not self.mi_helper.buildSquashStretch:
		return False
	    if not self.mi_skullPlate:
		log.error("%s Squash and stretch on. No skull plate found"%(self._str_reportStart))
		return False
	    
	    d_casts = {'top':{'direction':self.str_orientation[1]+"+"},
	               'left':{'direction':self.str_orientation[2]+"+"},
	               'right':{'direction':self.str_orientation[2]+"-"},
	               'back':{'direction':self.str_orientation[0]+"-"}}
	    
	    self.d_squash = d_casts
	    
	    #Need to build some locs
	    for k in d_casts.keys():
		str_cast = d_casts[k]['direction']
		d_return = rayCast.findMeshIntersectionFromObjectAxis(self.l_targetMesh[0],self.mi_squashCastHelper.mNode,str_cast)
		pos = d_return.get('hit')
		if not pos:
		    log.warning("rayCast.findMeshIntersectionFromObjectAxis(%s,%s,%s)"%(self.l_targetMesh[0],self.mi_squashCastHelper.mNode,str_cast))
		    raise StandardError, "Failed to find hit." 
		log.debug("%s >>> Squash stretch cast. key: %s | cast: %s | pos:%s"%(self._str_reportStart,k, str_cast,pos))
		try:#Create and name
		    mc.select(cl=True)
		    mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
		    mi_jnt.parent = False
		    mi_jnt.addAttr('cgmDirection',k ,lock=True)			    
		    mi_jnt.addAttr('cgmName',"head",lock=True)	
		    mi_jnt.addAttr('cgmNameModifier',"squash",lock=True)			    
		    mi_jnt.doName()
		except Exception,error:
		    raise StandardError,"Create fail. direction: %s | pos : %s | error: %s "%(k,pos,error)       
		try:#Orient
		    constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
		    mc.delete(constraintBuffer)
		    mi_jnt.parent = self.str_rootJoint
		except Exception,error:raise StandardError,"Orient fail. direction: %s | pos : %s | error: %s "%(k,pos,error)       
       
		jntUtils.metaFreezeJointOrientation(mi_jnt)
		
		self.d_squash[k]['ml_joints'] = [mi_jnt] #nested list
		self.ml_moduleJoints.append(mi_jnt)
		
	    return True
	
	def _buildMidBrow_(self): 	    
	    d_buildCurves = {'left':{'crv':self.mi_leftTempleCrv},
		             'right':{'crv':self.mi_rightTempleCrv}}	
	    
	    self.d_midBuild = d_buildCurves
	    
	    #We need to find the middle point between 
	    l_leftCV = self.mi_leftBrowCrv.getComponents('cv')
	    l_rightCV = self.mi_rightBrowCrv.getComponents('cv')
	    pos = distance.returnAveragePointPosition( [mc.pointPosition(l_leftCV[0],w=True),mc.pointPosition(l_rightCV[0],w=True)] )
	    
	    try:#Create and name
		mc.select(cl=True)
		mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
		mi_jnt.parent = False
		mi_jnt.addAttr('cgmName',"brow",lock=True)
		mi_jnt.addAttr('cgmDirection',"center",lock=True)		    					
		mi_jnt.doName()
		#log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_templeJoints]))
	    except Exception,error:
		raise StandardError,"error: %s "%(error)       
	    try:#Orient
		constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
		mc.delete(constraintBuffer)
		mi_jnt.parent = self.str_rootJoint
	    except Exception,error:raise StandardError,"error: %s "%(error)       
	  
	    jntUtils.metaFreezeJointOrientation(mi_jnt)	  
	    
	    self.ml_moduleJoints.append(mi_jnt)
	    d_buildCurves['ml_joints'] = [mi_jnt] #nested list
	    #self.mi_go._mi_rigNull.msgList_connect(mi_jnt,'moduleCenterBrowJoints','rigNull')#Connect
	    
	    return True
		
	def _buildBrow_(self): 	    
	    d_buildCurves = {'left':{'crv':self.mi_leftBrowCrv},
		             'right':{'crv':self.mi_rightBrowCrv}}	    
	    self.d_browCurveBuild = d_buildCurves
	    
	    for k in d_buildCurves.keys():#Make our left and right joints
		mi_crv = d_buildCurves[k].get('crv')#get instance
		int_count = self.int_browJointsCnt#get int
		log.debug("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
		try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
		except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)       
		d_buildCurves[k]['l_pos'] = l_pos#Store it
		log.debug("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
		l_jointBuffer = []
		ml_endJoints = []
		ml_browJoints = []
		for i,pos in enumerate(l_pos):
		    try:#Create and name
			mc.select(cl=True)
			mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
			mi_jnt.parent = False
			mi_jnt.addAttr('cgmName',"brow",lock=True)		    			
			mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
			mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
			mi_jnt.doName()
			l_jointBuffer.append(mi_jnt)
			ml_browJoints.append(mi_jnt)
			#log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_browJoints]))
		    except Exception,error:
			raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
		    try:#Orient
			constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
			mc.delete(constraintBuffer)
			mi_jnt.parent = self.str_rootJoint
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
		    try:#freeze
			jntUtils.metaFreezeJointOrientation(mi_jnt)
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
		d_buildCurves[k]['ml_joints'] = ml_browJoints #nested list
		#self.mi_go._mi_rigNull.msgList_connect(ml_browJoints,'moduleBrowJoints_%s'%k,'rigNull')
		self.ml_moduleJoints.extend(ml_browJoints)
	    
	    return True
	
	def _buildCheek_(self): 
	    if not self.mi_helper.buildUprCheek:
		log.info("%s >>> Build cheek toggle: off"%(self._str_reportStart))
		return True
	    
	    d_buildCurves = {'left':{'crv':self.mi_leftUprCheekCrv},
		             'right':{'crv':self.mi_rightUprCheekCrv}}	
	    
	    self.d_cheekCurveBuild = d_buildCurves
	    
	    for k in d_buildCurves.keys():#Make our left and right joints
		mi_crv = d_buildCurves[k].get('crv')#get instance
		int_count = self.int_cheekJointsCnt#get int
		log.debug("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
		#Get our l_pos on which to build the joints ------------------------------------------------------------
		if int_count == 1:
		    l_pos = [ mc.pointPosition(mi_crv.getComponents('cv')[0], w = True)]
		else:
		    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
		    except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)       
		d_buildCurves[k]['l_pos'] = l_pos#Store it
		log.debug("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
		l_jointBuffer = []
		ml_endJoints = []
		ml_cheekJoints = []
		for i,pos in enumerate(l_pos):
		    try:#Create and name
			mc.select(cl=True)
			mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
			mi_jnt.parent = False
			mi_jnt.addAttr('cgmName',"uprCheek",lock=True)		    			
			mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
			mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
			mi_jnt.doName()
			l_jointBuffer.append(mi_jnt)
			ml_cheekJoints.append(mi_jnt)
			#log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_cheekJoints]))
		    except Exception,error:
			raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
		    try:#Orient
			constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
			mc.delete(constraintBuffer)
			mi_jnt.parent = self.str_rootJoint
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
		    try:#freeze
			jntUtils.metaFreezeJointOrientation(mi_jnt)
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
		d_buildCurves[k]['ml_joints'] = ml_cheekJoints #nested list
		#self.mi_go._mi_rigNull.msgList_connect(ml_cheekJoints,'moduleCheekJoints_%s'%k,'rigNull')
		self.ml_moduleJoints.extend(ml_cheekJoints)
		
	    return True
	
	def _buildTemple_(self): 
	    if not self.mi_helper.buildTemple:
		log.info("%s >>> Build temple toggle: off"%(self._str_reportStart))
		return True
	    
	    d_buildCurves = {'left':{'crv':self.mi_leftTempleCrv},
		             'right':{'crv':self.mi_rightTempleCrv}}	
	    
	    self.d_templeCurveBuild = d_buildCurves
	    
	    for k in d_buildCurves.keys():#Make our left and right joints
		mi_crv = d_buildCurves[k].get('crv')#get instance
		int_count = self.int_templeJointsCnt#get int
		log.debug("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
		#Get our l_pos on which to build the joints ------------------------------------------------------------
		if int_count == 1:
		    l_pos = [ mc.pointPosition(mi_crv.getComponents('cv')[0], w = True)]
		else:
		    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
		    except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)       
		d_buildCurves[k]['l_pos'] = l_pos#Store it
		log.debug("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
		l_jointBuffer = []
		ml_endJoints = []
		ml_templeJoints = []
		for i,pos in enumerate(l_pos):
		    try:#Create and name
			mc.select(cl=True)
			mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
			mi_jnt.parent = False
			mi_jnt.addAttr('cgmName',"temple",lock=True)		    			
			mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
			mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
			mi_jnt.doName()
			l_jointBuffer.append(mi_jnt)
			ml_templeJoints.append(mi_jnt)
			#log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_templeJoints]))
		    except Exception,error:
			raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
		    try:#Orient
			constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
			mc.delete(constraintBuffer)
			mi_jnt.parent = self.str_rootJoint
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
		    try:#freeze
			jntUtils.metaFreezeJointOrientation(mi_jnt)
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
		d_buildCurves[k]['ml_joints'] = ml_templeJoints #nested list
		#self.mi_go._mi_rigNull.msgList_connect(ml_templeJoints,'moduleTempleJoints_%s'%k,'rigNull')
		self.ml_moduleJoints.extend(ml_templeJoints)
		
	    return True
	
	def _connect_(self): 
	    self.mi_go._mi_rigNull.msgList_connect(self.ml_moduleJoints,'moduleJoints','rigNull')
	    self.mi_go._mi_rigNull.msgList_connect(self.ml_moduleJoints,'skinJoints')
	    
	    return True
 	    	
    #We wrap it so that it autoruns and returns
    return fncWrap(goInstance).go() 

def doSkeletonizeMouthNose(*args,**kws):
    class fncWrap(JointFactoryFunc):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'doSkeletonizeMouthNose(%s)'%self.mi_module.p_nameShort
	    self._b_autoProgressBar = True
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        {'step':'Build Nose','call':self._buildNose_},
	                        {'step':'Build UprCheek','call':self._buildUprCheek_},
	                        {'step':'Build Cheek','call':self._buildCheek_},	                        
	                        {'step':'Build Smile Lines','call':self._buildSmile_},
	                        {'step':'Build Jaw','call':self._buildJaw_},
	                        {'step':'Build Lips','call':self._buildLips_},
	                        {'step':'Build Tongue','call':self._buildTongue_},	                        
	                        {'step':'Connect','call':self._connect_}]
	                        
	    
	    assert self.mi_module.mClass == 'cgmMouthNose',"%s >>> Module is not type: 'cgmMouthNose' | type is: '%s'"%(self._str_funcName,self.mi_module.mClass)
	    
	    #The idea is to register the functions needed to be called
	    #=================================================================
	    
	def _gatherInfo_(self): 
	    self.str_orientation = self.mi_go.str_jointOrientation #Link
	    self.str_partName = self.mi_go._partName	
	    
	    try:
		self.l_targetMesh = self.mi_go._mi_puppet.getUnifiedGeo() or self.mi_go._mi_puppet.getGeo() or 'Morphy_Body_GEO1'#>>>>>>>>>>>>>>>>>this needs better logic   
	    except Exception,error:
		raise error
	    
	    #Find our head attach joint ------------------------------------------------------------------------------------------------
	    self.str_rootJoint = False
	    if self.mi_module.getMessage('moduleParent'):
		try:
		    mi_end = self.mi_module.moduleParent.rigNull.msgList_get('moduleJoints')[-1]
		    buffer =  mi_end.getMessage('scaleJoint')
		    if buffer:self.str_rootJoint = buffer[0]
		    else:self.str_rootJoint = mi_end.mNode
		except Exception,error:
		    log.error("%s failed to find root joint from moduleParent | %s"%(self._str_reportStart,error))
	    
	    #Orient info ------------------------------------------------------------------------------------------------
	    self.v_aimNegative = cgmValid.simpleAxis(self.str_orientation[0]+"-").p_vector
	    self.v_aim = cgmValid.simpleAxis(self.str_orientation[0]).p_vector	
	    self.v_up = cgmValid.simpleAxis(self.str_orientation[1]).p_vector	
	    self.v_upNegative = cgmValid.simpleAxis(self.str_orientation[1]+"-").p_vector	
	    self.v_out = cgmValid.simpleAxis(self.str_orientation[2]).p_vector	
	    self.v_outNegative = cgmValid.simpleAxis(self.str_orientation[2]+"-").p_vector
	    
	    #Find our helpers -------------------------------------------------------------------------------------------
	    self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    for attr in self.mi_helper.getAttrs(userDefined = True):#Get allof our Helpers
		if "Helper" in attr:
		    try:self.__dict__["mi_%s"%attr.replace('Helper','Crv')] = cgmMeta.validateObjArg(self.mi_helper.getMessage(attr),noneValid=False)
		    except Exception,error:raise StandardError, " Failed to find '%s' | %s"%(attr,error)
	    self.mi_skullPlate = cgmMeta.validateObjArg(self.mi_helper.getMessage('skullPlate'),noneValid=False)
	    self.str_skullPlate = self.mi_skullPlate.mNode
	    
	    #Get some data from helpers --------------------------------------------------------------------------------------
	    self.int_lipCount = self.mi_helper.lipJoints
	    self.int_cheekLoftCount = self.mi_helper.cheekLoftCount
	    self.int_cheekCount = self.mi_helper.cheekJoints
	    self.int_nostrilCount = self.mi_helper.nostrilJoints
	    self.int_uprCheekCount = self.mi_helper.uprCheekJoints
	    self.int_tongueCount = self.mi_helper.tongueJoints
	    
	    #Running lists ============================================================================================
	    self.ml_moduleJoints = []
	    self.md_moduleJoints = {}
	    return True
	
	def _buildJaw_(self):
	    str_skullPlate = self.str_skullPlate
	    
	    try:#jaw Root ==============================================================================================
		mi_crv = self.mi_jawPivotCrv
		tag = 'jaw'
		try:#Create an name -------------------------------------------------------------------------
		    mi_root = cgmMeta.cgmObject( mc.joint(p = mi_crv.getPosition()),setClass=True )
		    mi_root.addAttr('cgmName',tag,lock=True)		    			
		    mi_root.doName()
		    self.ml_moduleJoints.append(mi_root)
		    self.md_moduleJoints[tag] = mi_root
		except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error)
		try:#Aim Constraint -------------------------------------------------------------------------
		    mi_upLoc = mi_root.doLoc()
		    mi_aimLoc = mi_root.doLoc()
		    mi_upLoc.parent = mi_crv
		    mi_aimLoc.parent = mi_crv
		    mi_aimLoc.__setattr__("t%s"%self.str_orientation[0],10)
		    mi_upLoc.__setattr__("t%s"%self.str_orientation[1],10)
		    mc.delete( mc.aimConstraint(mi_aimLoc.mNode,mi_root.mNode,
	                                        weight = 1, aimVector = self.v_aim, upVector = self.v_up,
	                                        worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )		    
		    mi_root.parent = self.str_rootJoint
		    jntUtils.metaFreezeJointOrientation(mi_root)
		    mc.delete([mi_upLoc.mNode,mi_aimLoc.mNode])
		except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error) 
		self.mi_go._mi_rigNull.msgList_connect(mi_root,'jawJoint')		
	    except Exception,error:raise StandardError,"jaw root | %s "%(error) 
	    	    
	    try:#JawLine ==============================================================================================
		mi_crv = self.mi_jawLineCrv
		tag = 'jawLine'
		l_build = [{'direction':'center','minU':None,'maxU':None, 'reverse':False, 'count':1},
		           {'direction':'left','minU':None,'maxU':.3, 'reverse':False,'count':3},
	                   {'direction':'right','minU':None,'maxU':.3, 'reverse':True,'count':3}]
		md_buffer = {}
		for d in l_build:#First loop creates and stores to runnin md
		    int_cnt = d['count']
		    str_direction = d['direction']
		    md_buffer[str_direction] = []
		    ml_createdbuffer = []
		    if int_cnt == 1:
			l_pos = [crvUtils.getMidPoint(mi_crv.mNode)]
		    else:
			l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode, int_cnt, minU = d['minU'], maxU = d['maxU'], reverseCurve = d['reverse'], rebuildForSplit=True)
		    ##log.info("%s l_pos : %s"%(self._str_reportStart, l_pos))
		    for i,pos in enumerate(l_pos):
			try:#Create an name -------------------------------------------------------------------------
			    mc.select(cl=True)
			    str_mdTag = "%s_%s_%s"%(str_direction,tag,i)
			    mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
			    mi_jnt.addAttr('cgmName',tag,lock=True)
			    if str_direction is not None:
				mi_jnt.addAttr('cgmDirection',str_direction,lock=True)
			    if int_cnt > 1:
				mi_jnt.addAttr('cgmIterator',i,lock=True)		    			
			    mi_jnt.doName()
			    ml_createdbuffer.append(mi_jnt)
			    self.md_moduleJoints[str_mdTag] = mi_jnt
			    md_buffer[str_direction].append(mi_jnt)
			except Exception,error:raise StandardError,"%s create and name fail | %s "%(str_mdTag,error)
			try:#Snap
			    Snap.go(mi_jnt,self.str_skullPlate,snapToSurface=True)
			    if str_direction == 'center':mi_jnt.__setattr__("t%s"%self.str_orientation[2],0)
			except Exception,error:
			    raise StandardError,"snap to mesh | pos count: %s | error: %s "%(k,i,error) 
		    self.ml_moduleJoints.extend(ml_createdbuffer)		    
		    self.mi_go._mi_rigNull.msgList_connect(ml_createdbuffer,"%s_%sJoint"%(str_direction,tag))		
		    
		for d in l_build:#Second loop aims....
		    str_direction = d['direction']		    
		    try:#Orienting -------------------------------------------------------------------------
			str_mirror = False
			ml_joints = md_buffer[str_direction]
			
			if str_direction == 'right':
			    str_mirror = 'left'
			    v_aim = self.v_out
			else:
			    str_mirror = 'right'
			    v_aim = self.v_outNegative
			    
			##log.info("%s direction: %s"%(self._str_reportStart,str_direction))
			##log.info("%s joints: %s"%(self._str_reportStart,[mJnt.p_nameShort for mJnt in ml_joints]))			
			for i,mi_jnt in enumerate(ml_joints):
			    if str_direction == 'center':
				mc.delete( mc.normalConstraint(str_skullPlate,mi_jnt.mNode, weight = 1,
				                               aimVector = self.v_aim, upVector = self.v_up,
				                               worldUpType = 'scene' ))
			    else:
				if mi_jnt == ml_joints[-1]:
				    mi_aimObj = md_buffer['center'][0]
				else:mi_aimObj = ml_joints[i+1]
				mi_upObj = md_buffer[str_mirror][0]
				##log.info("%s aiming '%s' @ '%s' | up: '%s'"%(self._str_reportStart,mi_jnt.p_nameShort,mi_aimObj.p_nameShort,mi_upObj.p_nameShort))									    
				mc.delete( mc.aimConstraint(mi_aimObj.mNode, mi_jnt.mNode,
				                            weight = 1, aimVector = v_aim, upVector = self.v_aimNegative,
				                            worldUpObject = mi_upObj.mNode, worldUpType = 'object' ) )			    
			
			    mi_jnt.parent = mi_root.mNode
			    jntUtils.metaFreezeJointOrientation(mi_jnt)		    
		    except Exception,error:raise StandardError,"%s orient fail | %s "%(str_mdTag,error) 
	    except Exception,error:raise StandardError,"JawLine | %s "%(error) 	    
	    return True	
	
	def _buildLips_(self):
	    str_skullPlate = self.str_skullPlate
	    	    	    
	    l_build = [{'tag':'lipUpr','crv':self.mi_lipUprCrv, 'minU':None, 'maxU':None, 'count':self.int_lipCount, 'startSplitFactor':.1, 'parent':self.str_rootJoint},
	               {'tag':'lipLwr','crv':self.mi_lipLwrCrv, 'minU':None, 'maxU':None, 'count':self.int_lipCount, 'startSplitFactor':.1,'parent':self.md_moduleJoints['jaw']},
	               {'tag':'lipOver','crv':self.mi_lipOverTraceCrv,'minU':.25, 'maxU':.75, 'count':3, 'startSplitFactor': None, 'parent':self.str_rootJoint},
	               {'tag':'lipUnder','crv':self.mi_lipUnderTraceCrv,'minU':.25, 'maxU':.75, 'count':3, 'startSplitFactor': None, 'parent':self.md_moduleJoints['jaw']}]
	    
	    md_buffer = {}
	    for d in l_build:#First loop creates and stores to runnin md
		int_cnt = d['count']
		tag = d['tag']
		md_buffer[tag] = {'ml_list':[]}
		mi_crv = d['crv']
		
		try:#Get positions ----------------------------------------------------------------------------------
		    if int_cnt == 1: l_pos = [crvUtils.getMidPoint(mi_crv.mNode)]
		    else: 
			l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode, int_cnt, minU = d['minU'], maxU = d['maxU'], startSplitFactor=d['startSplitFactor'], rebuildForSplit=True)
		    if tag == 'lipLwr': l_pos = l_pos[1:-1]
		except Exception,error:raise StandardError,"%s get positions | %s "%(tag,error)
		
		int_last = len(l_pos)-1
		for i,pos in enumerate(l_pos):
		    try:#Create an name -------------------------------------------------------------------------
			mc.select(cl=True)
			mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
			if i in [0,int_last] and tag == 'lipUpr':
			    mi_jnt.addAttr('cgmName','lipCorner',lock=True)			    			    
			else:
			    mi_jnt.addAttr('cgmName',tag,lock=True)	
			md_buffer[tag]['ml_list'].append(mi_jnt)
			self.ml_moduleJoints.append(mi_jnt)			    
		    except Exception,error:raise StandardError,"%s create | %s "%(tag,error)
		    
	    for d in l_build:#Second loop split and names....
		md_sides = {}		    
		tag = d['tag']		    
		ml_buffer = md_buffer[tag]['ml_list']
		###log.info("%s %s >> %s"%(self._str_reportStart,tag,ml_buffer))		    
		try:#Split ----------------------------------------------------------------------------------
		    #We need to split our list
		    int_len = len(ml_buffer)
		    int_mid = int(int_len/2)	
		    
		    if int_len%2==0:#If even,no mid....
			raise StandardError, "Need to write this..."
			md_sides['left'] = ml_buffer[:int_mid + 1]
			md_sides['right'] = ml_buffer[int_mid:]
		    else:#odd
			if tag == 'lipUpr':
			    md_sides['left'] = ml_buffer[1:int_mid]
			    md_sides['center'] = [ml_buffer[int_mid]]			
			    md_sides['right'] = ml_buffer[int_mid+1:-1]			    
			    md_sides['leftCorner'] = [ml_buffer[0]]
			    md_sides['rightCorner'] = [ml_buffer[-1]]	
			    self.md_moduleJoints['leftLipCorner'] = ml_buffer[0]
			    self.md_moduleJoints['rightLipCorner'] = ml_buffer[-1] 
			    self.mi_go._mi_rigNull.msgList_connect(ml_buffer[0],"left_lipCornerJoint")			    			    
			    self.mi_go._mi_rigNull.msgList_connect(ml_buffer[-1],"right_lipCornerJoint")			    			    
			else:
			    md_sides['left'] = ml_buffer[:int_mid]
			    md_sides['center'] = [ml_buffer[int_mid]]			
			    md_sides['right'] = ml_buffer[int_mid+1:]			    
		    md_sides['right'].reverse()
		except Exception,error:raise StandardError,"%s split | %s "%(tag,error)
		    
		for k in md_sides.keys():
		    ml_side = md_sides[k]
		    int_len = len(ml_side)
		    ###log.info("%s | %s >> %s"%(tag,k,int_len))
		    if 'left' in k:str_direction = 'left'
		    elif 'right' in k:str_direction = 'right'
		    else: str_direction = 'center'
		    
		    #Store it -----------------------------------------------------------------
		    self.mi_go._mi_rigNull.msgList_connect(ml_side,"%s_%sJoint"%(str_direction,tag))			    
		    #self.ml_moduleJoints.extend(ml_createdbuffer)		    
		    #self.mi_go._mi_rigNull.msgList_connect(ml_createdbuffer,"%s_%s"%(str_direction,tag))	
		    
		    #md_jointsToDirection = []
		    for i,mi_jnt in enumerate(ml_side):
			int_last = len(ml_side)-1			
			l_tagBuild = [str_direction,mi_jnt.cgmName]#Need to build our storage tag
			if 'left' in k:
			    mi_jnt.addAttr('cgmDirection','left',lock=True)
			elif 'right' in k:
			    mi_jnt.addAttr('cgmDirection','right',lock=True)
			else:
			    mi_jnt.addAttr('cgmDirection',k,lock=True)
			if int_len > 1:
			    mi_jnt.addAttr('cgmIterator',i,lock=True)
			    l_tagBuild.append("%s"%i)
			mi_jnt.doName()	
			if k == 'center':mi_jnt.__setattr__("t%s"%self.str_orientation[2],0)			
			str_mdTag = "_".join(l_tagBuild)
			self.md_moduleJoints[str_mdTag] = mi_jnt#Store to our module joint running list
			try:#>>> Orient -----------------------------------------------------------------------
			    if str_direction == 'right':
				v_aimIn = self.v_out
				v_aimOut = self.v_outNegative				
			    else:
				v_aimIn = self.v_outNegative
				v_aimOut = self.v_out					
				
			    #First we contrain to the skill plate for our intial orientation
			    mc.delete( mc.normalConstraint(str_skullPlate,mi_jnt.mNode, weight = 1,
			                                   aimVector = self.v_aim, upVector = self.v_up,
			                                   worldUpType = 'scene' ))
			    
			    #Then we're gonna do a more careful aim with a blend
			    if str_direction != 'center' and 'Corner' not in mi_jnt.cgmName and tag not in ['lipOver','lipUnder']:
				if i == 0:
				    mi_aimOut = self.md_moduleJoints[str_direction+'LipCorner']	
				    mi_aimIn = ml_side[i+1]
				elif i == int_last:
				    mi_aimOut = ml_side[i-1]
				    mi_aimIn = md_sides['center'][0]			    
				else:
				    mi_aimOut = ml_side[i-1]
				    mi_aimIn = ml_side[i+1]
				    
				#up loc ------------------------------------------------------------------------
				mi_upLoc = mi_jnt.doLoc()
				mi_upLoc.parent = mi_jnt
				mi_upLoc.__setattr__("t%s"%self.str_orientation[1],10)
				mi_upLoc.parent = False
				
				mi_locIn = mi_jnt.doLoc()
				mi_locOut = mi_jnt.doLoc()
				
				mc.delete( mc.aimConstraint(mi_aimIn.mNode, mi_locIn.mNode,
			                                    weight = 1, aimVector = v_aimIn, upVector = self.v_up,
			                                    worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )	
				mc.delete( mc.aimConstraint(mi_aimOut.mNode, mi_locOut.mNode,
			                                    weight = 1, aimVector = v_aimOut, upVector = self.v_up,
			                                    worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )
				mc.delete( mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_jnt.mNode,
			                                       weight = 1) )
				mc.delete([mi_locIn.mNode,mi_locOut.mNode,mi_upLoc.mNode])
				'''
				#aim....
				###log.info("%s aiming '%s' @ '%s' | up: '%s'"%(self._str_reportStart,mi_jnt.p_nameShort,mi_aimObj.p_nameShort,mi_upLoc.p_nameShort))									    				    
				mc.delete( mc.aimConstraint(mi_aimObj.mNode, mi_jnt.mNode,
			                                    weight = 1, aimVector = v_aim, upVector = self.v_up,
			                                    worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )
				mi_upLoc.delete()
				'''
			    mi_jnt.parent = d['parent']
			    jntUtils.metaFreezeJointOrientation(mi_jnt)		    
			except Exception,error:raise StandardError,"%s (%s) orient fail | %s "%(str_mdTag,mi_jnt.p_nameShort,error) 			    
	    return True	
	
	def _buildNose_(self):
	    str_skullPlate = self.str_skullPlate
	    md_noseBuilt = {} #We're gonna use this as a running list 
	    
	    try:#Nose Root ==============================================================================================
		mi_crv = self.mi_noseBaseCastCrv
		l_components = mi_crv.getComponents('cv')
		tag = 'noseBase'
		try:#Create our root -------------------------------------------------------------------------
		    l_checkPos = [{'direction':'left','minU':.05,'maxU':.4, 'reverse':False},
		                  {'direction':'right','minU':.05,'maxU':.4, 'reverse':True}]
		    
		    l_pos = []
		    for d in l_checkPos:
			l_pos.extend( crvUtils.returnSplitCurveList(mi_crv.mNode,
			                                            1, minU = .05, maxU = .4,
			                                            reverseCurve = d['reverse'], rebuildForSplit=True))		    
		       
		    pos = distance.returnAveragePointPosition(l_pos)
		    
		    mi_root = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
		    mi_root.addAttr('cgmName',tag,lock=True)		    			
		    mi_root.doName()
		    self.ml_moduleJoints.append(mi_root)
		    md_noseBuilt[tag] = mi_root
		    self.mi_go._mi_rigNull.msgList_connect(mi_root,"%sJoint"%(tag))
		    mi_root.__setattr__("t%s"%self.str_orientation[2],0)#center
		    
		except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error)
		try:#Normal Constraint -------------------------------------------------------------------------
		    constraintBuffer = mc.normalConstraint(str_skullPlate,mi_root.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
		    mc.delete(constraintBuffer)
		    mi_root.parent = self.str_rootJoint
		    jntUtils.metaFreezeJointOrientation(mi_root)		    
		except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error) 
	    except Exception,error:raise StandardError,"Nose root | %s "%(error) 
		
	    try:#Profile Crv ==============================================================================================
		mi_crv = self.mi_noseProfileCrv
		l_components = mi_crv.getComponents('cv')
		l_build = [{'tag':'noseTop','idx':-1,"aim":self.v_upNegative,'parent' : self.str_rootJoint,
		            "up":self.v_aim,"target":"skullPlate","upTarget":None},
		           {'tag':'noseUnder','idx':0, "aim":self.v_aimNegative,
		            "up":self.v_up,"target":"skullPlate","upTarget":None},
		           {'tag':'noseTip','idx':2, "aim":self.v_aimNegative,
		            "up":self.v_up,"target":"noseBase","upTarget":"noseTop"}]
		for d in l_build:#First loop creates and stores to runnin md
		    try:#Create an name -------------------------------------------------------------------------
			tag = d['tag']
			idx = d['idx']
			str_loc = locators.doLocPos( distance.returnWorldSpacePosition(l_components[idx]) )[0]
			d_ret = distance.returnNearestPointOnCurveInfo(str_loc,mi_crv.mNode)
			mc.delete(str_loc)#Delete the loc
			mi_jnt = cgmMeta.cgmObject( mc.joint(p = d_ret['position']),setClass=True )
			mi_jnt.addAttr('cgmName',tag,lock=True)		    			
			mi_jnt.doName()
			self.ml_moduleJoints.append(mi_jnt)
			md_noseBuilt[tag] = mi_jnt
			self.md_moduleJoints[tag] = mi_jnt
			#Store it...
			self.mi_go._mi_rigNull.msgList_connect(mi_jnt,"%sJoint"%(tag))
			if tag in ['noseTop','noseUnder']:
			    mi_jnt.__setattr__("t%s"%self.str_orientation[2],0)#center
		    except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error)  
		for d in l_build:#Second pass aims. Two passes because we're aming at one another
		    try:#Normal Constraint -------------------------------------------------------------------------
			tag = d['tag']
			v_aim = d['aim']
			v_up = d['up']
			target = d['target']
			up = d['upTarget']
			mi_jnt = md_noseBuilt[ tag ]
			if target == 'skullPlate':
			    mc.delete( mc.normalConstraint(str_skullPlate,mi_jnt.mNode, weight = 1,
			                                   aimVector = self.v_aim, upVector = self.v_up,
			                                   worldUpType = 'scene' ))
			else:
			    mc.delete( mc.aimConstraint(md_noseBuilt[ target ].mNode,mi_jnt.mNode,
				                        weight = 1, aimVector = v_aim, upVector = v_up,
				                        worldUpObject = md_noseBuilt[ up ].mNode, worldUpType = 'object' ) )
			if d.get('parent'): mi_jnt.parent = d.get('parent')			    
			else: mi_jnt.parent = mi_root.mNode
			jntUtils.metaFreezeJointOrientation(mi_jnt)		    
		    except Exception,error:raise StandardError,"%s orient fail | %s "%(tag,error) 
	    except Exception,error:raise StandardError,"Profile | %s "%(error) 
	    
	    try:#Nostril ==============================================================================================
		mi_crv = self.mi_noseBaseCastCrv
		int_cnt = self.int_nostrilCount
		tag = 'nostril'
		if int_cnt == 1:
		    l_build = [{'direction':'left','minU':.05,'maxU':.4, 'reverse':False},
		               {'direction':'right','minU':.05,'maxU':.4, 'reverse':True}]
		else:
		    raise NotImplementedError,"Don't know how to deal with more than one nostril joint yet"
		
		for d in l_build:#First loop creates and stores to runnin md
		    l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode, int_cnt, minU = .05, maxU = .4, reverseCurve = d['reverse'], rebuildForSplit=True)
		    str_direction = d['direction']		    
		    ##log.info("%s l_pos : %s"%(self._str_reportStart, l_pos))
		    ml_createdbuffer = []
		    for i in range(int_cnt):
			try:#Create an name -------------------------------------------------------------------------
			    str_mdTag = "%s_%s_%s"%(str_direction,tag,i)
			    mi_jnt = cgmMeta.cgmObject( mc.joint(p = l_pos[i]),setClass=True )
			    mi_jnt.addAttr('cgmName',tag,lock=True)		    						    
			    mi_jnt.addAttr('cgmDirection',str_direction,lock=True)
			    mi_jnt.addAttr('cgmIterator',i,lock=True,hidden = True)		    			
			    mi_jnt.doName()
			    self.ml_moduleJoints.append(mi_jnt)
			    md_noseBuilt[str_mdTag] = mi_jnt
			    self.md_moduleJoints[str_mdTag] = mi_jnt	
			    ml_createdbuffer.append(mi_jnt)
			    
			except Exception,error:raise StandardError,"%s create and name fail | %s "%(str_mdTag,error)  
			try:#Normal Constraint -------------------------------------------------------------------------
			    mc.delete( mc.aimConstraint(md_noseBuilt[ 'noseBase' ].mNode, mi_jnt.mNode,
				                        weight = 1, aimVector = self.v_aimNegative, upVector = self.v_up,
				                        worldUpObject = md_noseBuilt[ 'noseTop' ].mNode, worldUpType = 'object' ) )
			    mi_jnt.parent = mi_root.mNode
			    jntUtils.metaFreezeJointOrientation(mi_jnt)		    
			except Exception,error:raise StandardError,"%s orient fail | %s "%(str_mdTag,error) 
		    #Store it...	    
		    self.mi_go._mi_rigNull.msgList_connect(ml_createdbuffer,"%s_%sJoint"%(str_direction,tag))		    
	    except Exception,error:raise StandardError,"Nostril | %s "%(error) 	    
	    
	    self.md_noseBuilt = md_noseBuilt
	    return True
	
	def _buildSmile_(self):
	    md_smileBuilt = {} #We're gonna use this as a running list 
	    self.md_smileBuilt = md_smileBuilt#link it
	    d_buildCurves = {'left':{'crv':self.mi_smileLeftCrv},
		             'right':{'crv':self.mi_smileRightCrv}}	
	    
	    #Get some statics
	    int_count = 5	    
	    str_skullPlate = self.str_skullPlate
	    			
	    for k in d_buildCurves.keys():#Make our left and right joints
		mi_crv = d_buildCurves[k].get('crv')#get instance
		##log.info("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
		#Get our l_pos on which to build the joints ------------------------------------------------------------
		try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count, rebuildSpans=10)
		except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)  
		
		d_buildCurves[k]['l_pos'] = l_pos#Store it
		##log.info("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
		ml_createdbuffer = []
		for i,pos in enumerate(l_pos):
		    try:#Create and name -----------------------------------------------------------------------------------------------
			mc.select(cl=True)
			mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
			mi_jnt.parent = False
			mi_jnt.addAttr('cgmName',"smileLine",lock=True)		    			
			mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
			mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
			mi_jnt.doName()
			self.ml_moduleJoints.append(mi_jnt)
			ml_createdbuffer.append(mi_jnt)
			##log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_cheekJoints]))
		    except Exception,error:
			raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
		    
		    #try:#Snap
			#Snap.go(mi_jnt,self.str_skullPlate,snapToSurface=True)	
		    #except Exception,error:
			#raise StandardError,"snap to mesh | pos count: %s | error: %s "%(k,i,error)       
		    
		    try:#Orient -----------------------------------------------------------------------------------------------
			mc.delete( mc.normalConstraint(str_skullPlate,mi_jnt.mNode, weight = 1,
			                               aimVector = self.v_aim, upVector = self.v_up,
			                               worldUpType = 'scene' ))
			mi_jnt.parent = self.str_rootJoint
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
		    try:#Freeze -----------------------------------------------------------------------------------------------
			jntUtils.metaFreezeJointOrientation(mi_jnt)
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       		
		    #Store it...	    
		    self.mi_go._mi_rigNull.msgList_connect(ml_createdbuffer,"%s_%sJoint"%(k,'smileLine'))		   
	    return True
	
	def _buildTongue_(self):
	    md_smileBuilt = {} #We're gonna use this as a running list 
	    self.md_smileBuilt = md_smileBuilt#link it                            	
	    
	    #Get some statics
	    int_count = self.int_tongueCount	    
	    str_skullPlate = self.str_skullPlate
	    mi_crv = self.mi_tongueCrv#get instance	    
	    str_squashStart = self.mi_squashStartCrv.mNode
	    
	    ##log.info("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
	    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode, int_count, rebuildSpans=10)
	    except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)  
	    
	    ##log.info("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
	    ml_tongueJoints = []
	    int_last = len(l_pos)-1
	    for i,pos in enumerate(l_pos):
		try:#Create and name -----------------------------------------------------------------------------------------------
		    mc.select(cl=True)
		    mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
		    mi_jnt.addAttr('cgmName',"tongue",lock=True)		    			
		    mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
		    mi_jnt.doName()
		    self.ml_moduleJoints.append(mi_jnt)
		    ml_tongueJoints.append(mi_jnt)
		    mi_jnt.__setattr__("t%s"%self.str_orientation[2],0)#center		    
		    ##log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_tongueJoints]))
		except Exception,error:
		    raise StandardError,"pos count: %s | error: %s "%(i,error)       
	    for i,mi_jnt in enumerate(ml_tongueJoints):
		try:#Orient -----------------------------------------------------------------------------------------------
		    if i == 0:
			mi_jnt.parent = self.md_moduleJoints['jaw']
			
		    if i == int_last:
			v_aim = self.v_aimNegative
		    else:
			v_aim = self.v_aim
		    if mi_jnt != ml_tongueJoints[-1]:
			mc.delete( mc.aimConstraint(ml_tongueJoints[i+1].mNode, mi_jnt.mNode,
		                                    weight = 1, aimVector = v_aim, upVector = self.v_up,
		                                    worldUpObject = str_squashStart, worldUpType = 'object' ) )			
		    else:
			joints.doCopyJointOrient(ml_tongueJoints[-2].mNode,ml_tongueJoints[-1].mNode)
		except Exception,error:raise StandardError,"pos count: %s | Constraint fail | error: %s "%(i,error)       
		try:#Freeze -----------------------------------------------------------------------------------------------
		    if i > 0:
			mi_jnt.parent = ml_tongueJoints[i-1]
		    jntUtils.metaFreezeJointOrientation(mi_jnt)
		except Exception,error:raise StandardError,"| pos count: %s | Freeze orientation fail | error: %s "%(i,error)       		
	    #Store it...		    
	    self.mi_go._mi_rigNull.msgList_connect(ml_tongueJoints,"%sJoint"%('tongue'))		    
	    return True	
	
	def _buildUprCheek_(self): 
	    if not self.mi_helper.buildUprCheek:
		#log.info("%s >>> Build upr cheek toggle: off"%(self._str_reportStart))
		return True

	    d_buildCurves = {'left':{'crv':self.mi_leftUprCheekCrv},
		             'right':{'crv':self.mi_rightUprCheekCrv}}	
	    self.d_cheekCurveBuild = d_buildCurves
	    
	    for k in d_buildCurves.keys():#Make our left and right joints
		mi_crv = d_buildCurves[k].get('crv')#get instance
		int_count = self.int_uprCheekCount#get int
		log.debug("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
		#Get our l_pos on which to build the joints ------------------------------------------------------------
		if int_count == 1:
		    l_pos = [ mc.pointPosition(mi_crv.getComponents('cv')[0], w = True)]
		else:
		    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
		    except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)       
		d_buildCurves[k]['l_pos'] = l_pos#Store it
		log.debug("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
		ml_jointBuffer = []
		ml_endJoints = []
		ml_cheekJoints = []
		for i,pos in enumerate(l_pos):
		    try:#Create and name
			mc.select(cl=True)
			mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
			mi_jnt.parent = False
			mi_jnt.addAttr('cgmName',"uprCheek",lock=True)		    			
			mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
			mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
			mi_jnt.doName()
			ml_jointBuffer.append(mi_jnt)
			ml_cheekJoints.append(mi_jnt)
			self.ml_moduleJoints.append(mi_jnt)			
			##log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_cheekJoints]))
		    except Exception,error:
			raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
		    try:#Orient
			constraintBuffer = mc.normalConstraint(self.str_skullPlate,mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
			mc.delete(constraintBuffer)
			mi_jnt.parent = self.str_rootJoint
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
		    try:#freeze
			jntUtils.metaFreezeJointOrientation(mi_jnt)
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
		d_buildCurves[k]['ml_joints'] = ml_cheekJoints #nested list
		#Store it...	    
		self.mi_go._mi_rigNull.msgList_connect(ml_jointBuffer,"%s_%sJoint"%(k,'uprCheek'))		
	    return True
	
	def _buildCheek_(self): 
	    if not self.mi_helper.buildCheek:
		#log.info("%s >>> Build cheek toggle: off"%(self._str_reportStart))
		return True
	    int_jointCnt = self.int_cheekCount
	    int_loftCnt = self.int_cheekLoftCount
	    
	    d_buildCurves = {'left':{'uprCrv':self.mi_leftUprCheekCrv,'maxU':.35,'reverseCurve' : False},
	                     'right':{'uprCrv':self.mi_rightUprCheekCrv,'maxU':.35,'reverseCurve' : True}}	
	    self.d_cheekCurveBuild = d_buildCurves
	    l_posList = []
	    for k in d_buildCurves.keys():#Make our left and right joints
		d_buffer = d_buildCurves[k]
		mi_uprCrv = d_buildCurves[k].get('uprCrv')#get instance
		#log.info("%s >>> building joints for %s curve | lofts: %s | count: %s"%(self._str_reportStart,k, int_loftCnt, int_jointCnt))
		
		#Get our l_pos on which to build the joints ------------------------------------------------------------
		#try:l_posUpr = crvUtils.returnSplitCurveList(mi_uprCrv.mNode,int_jointCnt,rebuildSpans=10)
		#except Exception,error:raise StandardError,"upr split fail | error: %s "%(error) 
		
		try:l_posLwr = crvUtils.returnSplitCurveList(self.mi_jawLineCrv.mNode,int_jointCnt,rebuildSpans=10, maxU = d_buffer['maxU'], reverseCurve = d_buffer['reverseCurve'] )
		except Exception,error:raise StandardError,"lwr split fail | error: %s "%(error)   
		
		str_lwrCurve = mc.curve (d=1, p = l_posLwr , os=True)
		str_loft = mc.loft([mi_uprCrv.mNode,str_lwrCurve],uniform = True,degree = 1,ss = 1)[0]
		
		try:#loft split
		    str_bufferUV = mc.ls("%s.u[*][*]"%str_loft)[0]
		    log.debug("%s >> u list : %s"%(self._str_reportStart,str_bufferUV))       		
		    l_splitBuffer = str_bufferUV.split('][')
		    str_bufferU  = l_splitBuffer[0]
		    str_bufferV = l_splitBuffer[1]
		    f_maxU = float(str_bufferU.split(':')[-1])
		    f_maxV = float(str_bufferV.split(':')[-1].split(']')[0])
		    log.debug("maxU : %s | maxV: %s"%(f_maxU,f_maxV))
		    
		    l_uValues = cgmMath.returnSplitValueList(0,f_maxU,1)
		    l_vValues = cgmMath.returnSplitValueList(0,f_maxV*.8,int_jointCnt)
		    #log.info("l_uValues : %s "%(l_uValues))
		    #log.info("l_vValues : %s "%(l_vValues))
		    l_pos = []
		    for v in l_vValues:
			l_pos.append(mc.pointPosition("%s.uv[%s][%s]"%(str_loft,l_uValues[0],v)))
		    mc.delete(str_loft,str_lwrCurve)
		except Exception,error:raise StandardError,"loft split fail | error: %s "%(error)   
		
		d_buildCurves[k]['l_pos'] = l_pos#Store it
		#log.info("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
		l_jointBuffer = []
		ml_endJoints = []
		ml_cheekJoints = []
		for i,pos in enumerate(l_pos):
		    try:#Create and name
			mc.select(cl=True)
			mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
			mi_jnt.parent = False
			mi_jnt.addAttr('cgmName',"cheek",lock=True)		    			
			mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
			mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
			mi_jnt.doName()
			l_jointBuffer.append(mi_jnt)
			ml_cheekJoints.append(mi_jnt)
			self.ml_moduleJoints.append(mi_jnt)			
			##log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_cheekJoints]))
		    except Exception,error:
			raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
		    try:#Snap
			Snap.go(mi_jnt,self.str_skullPlate,snapToSurface=True)	
		    except Exception,error:
			raise StandardError,"snap to mesh | pos count: %s | error: %s "%(k,i,error)       
		    
		    try:#Orient
			constraintBuffer = mc.normalConstraint(self.str_skullPlate,mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
			mc.delete(constraintBuffer)
			mi_jnt.parent = self.str_rootJoint
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
		    try:#freeze
			jntUtils.metaFreezeJointOrientation(mi_jnt)
		    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
		d_buildCurves[k]['ml_joints'] = ml_cheekJoints #nested list
		#Store it...	    
		self.mi_go._mi_rigNull.msgList_connect(ml_cheekJoints,"%s_%sJoint"%(k,'cheek'))				
	    return True
		
	def _connect_(self): 
	    log.info("%s len - %s"%(self._str_reportStart,len(self.ml_moduleJoints)))	    
	    #for mi_jnt in self.ml_moduleJoints:
		#log.info("'%s'"%(mi_jnt.p_nameShort))
	    self.mi_go._mi_rigNull.msgList_connect(self.ml_moduleJoints,'moduleJoints','rigNull')
	    self.mi_go._mi_rigNull.msgList_connect(self.ml_moduleJoints,'skinJoints')	    
	    return True
 	    	
    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()  
    
def doSkeletonizeLimb(self):
    """ 
    DESCRIPTION:
    Basic limb skeletonizer
    
    ARGUMENTS:
    stiffIndex(int) - the index of the template objects you want to not have roll joints
                      For example, a value of -1 will let the chest portion of a spine 
                      segment be solid instead of having a roll segment. Default is the modules setting
    RETURNS:
    l_limbJoints(list)
    """
    # Get our base info
    #==================	        
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self._mi_module.mNode),"module no longer exists"
    _str_funcName = "doSkeletonizeLimb(%s)"%self._strShortName   
    log.debug(">>> %s >>> "%(_str_funcName) + "="*75)    
    start = time.clock()
    
    try:
	_str_subFunc = "Info gather"
	curve = self._mi_curve.mNode
	partName = self._partName
	l_limbJoints = []
    
	#>>> Check roll joint args
	rollJoints = self._mi_templateNull.rollJoints
	d_rollJointOverride = self._mi_templateNull.rollOverride
	if type(d_rollJointOverride) is not dict:
	    d_rollJointOverride = False
	    
	log.debug("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-start)) + "-"*75)
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#>>> See if we have have a suitable parent joint to use
	# We'll know it is if the first template position shares an equivalent position with it's parentModule
	#======================================================
	_str_subFunc = "Parent check"	
	i_parentJointToUse = False
	
	pos = distance.returnWorldSpacePosition( self._ml_controlObjects[0].mNode )
	log.debug("pos: %s"%pos)
	#Get parent position, if we have one
	if self._mi_module.getMessage('moduleParent'):
	    log.debug("Found moduleParent, checking joints...")
	    i_parentRigNull = self._mi_module.moduleParent.rigNull
	    parentJoints = i_parentRigNull.msgList_getMessage('moduleJoints')
	    log.debug(parentJoints)
	    if parentJoints:
		parent_pos = distance.returnWorldSpacePosition( parentJoints[-1] )
		log.debug("parentPos: %s"%parent_pos)  
		
	    log.debug("Equivalent: %s"%cgmMath.isVectorEquivalent(pos,parent_pos))
	    if cgmMath.isVectorEquivalent(pos,parent_pos):#if they're equivalent
		i_parentJointToUse = cgmMeta.cgmObject(parentJoints[-1])
		
	log.debug("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-start)) + "-"*50)
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    #>>> Make if our segment only has one handle
    #==========================================	
    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Skeletonize>> step:'%s' "%(self._strShortName,'Parent Check...'), progress=1)    				    
    self.b_parentStole = False
    if len(self._ml_controlObjects) == 1:
        if i_parentJointToUse:
            log.debug("Single joint: moduleParent mode")
            #Need to grab the last joint for this module
            l_limbJoints = [parentJoints[-1]]
            i_parentRigNull.msgList_connect(parentJoints[:-1],'moduleJoints','rigNull')
	    self.b_parentStole = True	    
        else:
            log.debug("Single joint: no parent mode")
            l_limbJoints.append ( mc.joint (p=(pos[0],pos[1],pos[2]))) 
    else:
        if i_parentJointToUse:
            #We're going to reconnect all but the last joint back to the parent module and delete the last parent joint which we're replacing
            i_parentRigNull.msgList_connect(parentJoints[:-1],'moduleJoints','rigNull')
            mc.delete(i_parentJointToUse.mNode)
	    self.b_parentStole = True
            
        #>>> Make the limb segment
        #==========================
	try:
	    _str_subFunc = "getUPositions"		    
	    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Skeletonize>> step:'%s' "%(self._strShortName,'Making segment joints...'), progress=1)    				    	
	    l_spanUPositions = []
	    #>>> Divide stuff
	    for i_obj in self._ml_controlObjects:#These are our base span u positions on the curve
		l_spanUPositions.append(distance.returnNearestPointOnCurveInfo(i_obj.mNode,curve)['parameter'])
	    l_spanSegmentUPositions = lists.parseListToPairs(l_spanUPositions)
	    #>>>Get div per span
	    l_spanDivs = self._mi_module.get_rollJointCountList() or []
	    
	    log.debug("l_spanSegmentUPositions: %s"%l_spanSegmentUPositions)
	    log.debug("l_spanDivs: %s"%l_spanDivs)	    

	    log.debug("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-start)) + "-"*50)
	except Exception,error:
	    raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

        
	try:#>>>Get div per span 
	    _str_subFunc = "initial Joint creation"
	    
	    l_jointUPositions = []
	    for i,segment in enumerate(l_spanSegmentUPositions):#Split stuff up
		#Get our span u value distance
		length = segment[1]-segment[0]
		div = length / (l_spanDivs[i] +1)
		tally = segment[0]
		l_jointUPositions.append(tally)
		for i in range(l_spanDivs[i] +1)[1:]:
		    tally = segment[0]+(i*div)
		    l_jointUPositions.append(tally)
	    l_jointUPositions.append(l_spanUPositions[-1])
		    
	    l_jointPositions = []
	    for u in l_jointUPositions:
		l_jointPositions.append(mc.pointPosition("%s.u[%f]"%(curve,u)))
		
		
	    #>>> Remove the duplicate positions"""
	    l_jointPositions = lists.returnPosListNoDuplicates(l_jointPositions)
	    #>>> Actually making the joints
	    for pos in l_jointPositions:
		l_limbJoints.append ( mc.joint (p=(pos[0],pos[1],pos[2]))) 
	    
	    log.debug("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-start)) + "-"*50)
	except Exception,error:
	    raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

               
    #>>> Naming
    #=========== 
    """ 
    Copy naming information from template objects to the joints closest to them
    copy over a cgmNameModifier tag from the module first
    """
    #attributes.copyUserAttrs(moduleNull,l_limbJoints[0],attrsToCopy=['cgmNameModifier'])
    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Skeletonize>> step:'%s' "%(self._strShortName,'Naming...'), progress=2)    				    
    
    try:#>>>First we need to find our matches
	_str_subFunc = "Find matches"	
	log.debug("Finding matches from module controlObjects")
	for i_obj in self._ml_controlObjects:
	    closestJoint = distance.returnClosestObject(i_obj.mNode,l_limbJoints)
	    #transferObj = attributes.returnMessageObject(obj,'cgmName')
	    """Then we copy it"""
	    attributes.copyUserAttrs(i_obj.mNode,closestJoint,attrsToCopy=['cgmPosition','cgmNameModifier','cgmDirection','cgmName'])
	    self._d_handleToHandleJoints[i_obj] = cgmMeta.cgmNode(closestJoint)
	    i_obj.connectChildNode(closestJoint,'handleJoint')
	    
	log.debug("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-start)) + "-"*50)
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#>>>If we stole our parents anchor joint, we need to to reconnect it
	_str_subFunc = "ParentStole reconnect"		
	log.debug("%s"%_str_subFunc)
	if self.b_parentStole:
	    i_parentControl = self._mi_module.moduleParent.templateNull.msgList_get('controlObjects')[-1]
	    log.debug("parentControl: %s"%i_parentControl.getShortName())
	    closestJoint = distance.returnClosestObject(i_parentControl.mNode,l_limbJoints)	
	    i_parentControl.connectChildNode(closestJoint,'handleJoint')
	log.debug("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-start)) + "-"*50)
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #>>>Store it
    self._mi_rigNull.msgList_connect(l_limbJoints,'moduleJoints','rigNull')
  

    #>>>Store these joints and rename the heirarchy
    try:#Metaclassing our objects
	_str_subFunc = "Metaclassing our objects"
	log.debug("%s"%_str_subFunc)		
	for i,o in enumerate(l_limbJoints):
	    i_o = cgmMeta.cgmObject(o)
	    i_o.addAttr('mClass','cgmObject',lock=True) 
	    i_o.addAttr('d_jointFlags', '{}',attrType = 'string', lock=True, hidden=True) 
	    
	ml_moduleJoints = self._mi_rigNull.msgList_get('moduleJoints',asMeta = True)  
	
	log.debug("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-start)) + "-"*50)
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#Naming
	_str_subFunc = "Naming"	
	log.debug("%s"%_str_subFunc)	
	ml_moduleJoints[0].doName(nameChildren=True,fastIterate=True)#name
	log.debug("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-start)) + "-"*50)
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    l_moduleJoints = [i_j.p_nameShort for i_j in ml_moduleJoints]#store
    
    #>>> Orientation    
    #=============== 
    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Skeletonize>> step:'%s' "%(self._strShortName,'Orienting...'), progress=3)    				        
    try:
	if not doOrientSegment(self):
	    raise StandardError, "Orient failed"
    except Exception,error:
        raise StandardError,"Segment orientation failed: %s"%error    
    
    #>>> Set its radius and toggle axis visbility on
    jointSize = (distance.returnDistanceBetweenObjects (l_moduleJoints[0],l_moduleJoints[-1])/6)
    reload(attributes)
    #jointSize*.2
    attributes.doMultiSetAttr(l_moduleJoints,'radi',3)
    
    #>>> Flag our handle joints
    #===========================
    ml_handles = []
    ml_handleJoints = []
    for i_obj in self._ml_controlObjects:
	if i_obj.hasAttr('handleJoint'):
	    #d_buffer = i_obj.handleJoint.d_jointFlags
	    #d_buffer['isHandle'] = True
	    #i_obj.handleJoint.d_jointFlags = d_buffer
	    ml_handleJoints.append(i_obj.handleJoint)
    
    self._mi_rigNull.msgList_connect(ml_handleJoints,'handleJoints','rigNull')
	    
    return True 

@cgmGeneral.Timer
def doOrientSegment(self):
    """ 
    Segement orienter. Must have a JointFactory Instance
    """ 
    # Get our base info
    #==================	        
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self._mi_module.mNode),"module no longer exists"
    
    ml_moduleJoints = self._mi_rigNull.msgList_get('moduleJoints',asMeta = True)
    l_moduleJoints = [i_j.p_nameShort for i_j in ml_moduleJoints]    
    
    #self._mi_rigNull = self._mi_module.rigNull#refresh
    log.debug(">>> %s.doOrientSegment >> "%self._strShortName + "="*75)            
        
    #>>> orientation vectors
    #=======================    
    orientationVectors = search.returnAimUpOutVectorsFromOrientation(self.str_jointOrientation)
    wantedAimVector = orientationVectors[0]
    wantedUpVector = orientationVectors[1]  
    log.debug("wantedAimVector: %s"%wantedAimVector)
    log.debug("wantedUpVector: %s"%wantedUpVector)
    
    #>>> Put objects in order of closeness to root
    #l_limbJoints = distance.returnDistanceSortedList(l_limbJoints[0],l_limbJoints)
    
    #>>> Segment our joint list by cgmName, prolly a better way to optimize this
    l_cull = copy.copy(l_moduleJoints)
    if len(l_cull)==1:
        log.debug('Single joint orient mode')
        helper = self._mi_templateNull.orientRootHelper.mNode
        if helper:
            log.debug("helper: %s"%helper)
            constBuffer = mc.orientConstraint( helper,l_cull[0],maintainOffset = False)
            mc.delete (constBuffer[0])  
	    #Push rotate to jointOrient
	    i_jnt = cgmMeta.cgmObject(l_cull[0])
	    ##i_jnt.jointOrient = i_jnt.rotate
	    ##i_jnt.rotate = [0,0,0]
	    
    else:#Normal mode
        log.debug('Normal orient mode')        
        self.l_jointSegmentIndexSets= []
        while l_cull:
            matchTerm = search.findRawTagInfo(l_cull[0],'cgmName')
            buffer = []
            objSet = search.returnMatchedTagsFromObjectList(l_cull,'cgmName',matchTerm)
            for o in objSet:
                buffer.append(l_moduleJoints.index(o))
            self.l_jointSegmentIndexSets.append(buffer)
            for obj in objSet:
                l_cull.remove(obj)
            
        #>>> un parenting the chain
        for i,i_jnt in enumerate(ml_moduleJoints):
	    if i != 0:
		i_jnt.parent = False
            i_jnt.displayLocalAxis = 1#tmp
	    #Reset the jointRotate before orientating
	    ##i_jnt.jointOrient = [0,0,0]	    
	    #Set rotateOrder
            try:
		#i_jnt.rotateOrder = 2
                i_jnt.rotateOrder = self.str_jointOrientation
	    except Exception,error:
		log.error("doOrientSegment>>rotate order set fail: %s"%i_jnt.getShortName())
    
        #>>>per segment stuff
        assert len(self.l_jointSegmentIndexSets) == len(self._mi_module.coreNames.value)#quick check to make sure we've got the stuff we need
        cnt = 0
	log.debug("Segment Index sets: %s"%self.l_jointSegmentIndexSets)
        for cnt,segment in enumerate(self.l_jointSegmentIndexSets):#for each segment
	    log.debug("On segment: %s"%segment)	    
	    lastCnt = len(self.l_jointSegmentIndexSets)-1
            segmentHelper = self._ml_controlObjects[cnt].getMessage('helper')[0]
            helperObjectCurvesShapes =  mc.listRelatives(segmentHelper,shapes=True)
            upLoc = locators.locMeCvFromCvIndex(helperObjectCurvesShapes[0],30)        
            if not mc.objExists(segmentHelper) and search.returnObjectType(segmentHelper) != 'nurbsCurve':
                raise StandardError,"doOrientSegment>>> No helper found"
	    
            if cnt != lastCnt:
		log.debug(cnt)
                #>>> Create our up object from from the helper object 
                #>>> make a pair list
                #pairList = lists.parseListToPairs(segment)
                """for pair in pairList:
                    constraintBuffer = mc.aimConstraint(ml_moduleJoints[pair[1]].mNode,ml_moduleJoints[pair[0]].mNode,maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
                    mc.delete(constraintBuffer[0])"""
		for index in segment:
		    if index != 0:
			ml_moduleJoints[index].parent = ml_moduleJoints[index-1].mNode
		    ml_moduleJoints[index].rotate  = [0,0,0]			
		    ml_moduleJoints[index].jointOrient  = [0,0,0]	
		    
		    log.debug("%s aim to %s"%(ml_moduleJoints[index].mNode,ml_moduleJoints[index+1].mNode))
		    constraintBuffer = mc.aimConstraint(ml_moduleJoints[index+1].mNode,ml_moduleJoints[index].mNode,maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
		    mc.delete(constraintBuffer[0])
		    
		    #Push rotate to jointOrient
		    #ml_moduleJoints[index].jointOrient = ml_moduleJoints[index].rotate
		    #ml_moduleJoints[index].rotate = [0,0,0]
		    
		mc.delete(upLoc)
                """for index in segment[-1:]:
		    log.debug("%s orient to %s"%(ml_moduleJoints[index].mNode,ml_moduleJoints[index-1].mNode))		    
                    constraintBuffer = mc.orientConstraint(ml_moduleJoints[index-1].mNode,ml_moduleJoints[index].mNode,maintainOffset = False, weight = 1)
                    mc.delete(constraintBuffer[0])"""
                #>>>  Increment and delete the up loc """
            else:
		log.debug(">>> Last count")
                #>>> Make an aim object and move it """
		i_jnt = ml_moduleJoints[segment[-1]]
		log.debug(i_jnt.getShortName())
		i_jnt.parent = ml_moduleJoints[segment[-1]-1].mNode
		i_jnt.jointOrient  = [0,0,0]
		#ml_moduleJoints[index].rotate  = [0,0,0]					

                aimLoc = locators.locMeObject(segmentHelper)
                aimLocGroup = rigging.groupMeObject(aimLoc)
                mc.move (0,0,10, aimLoc, localSpace=True)
                constraintBuffer = mc.aimConstraint(aimLoc,i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = wantedAimVector, upVector = wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
                mc.delete(constraintBuffer[0])
                mc.delete(aimLocGroup)
                mc.delete(upLoc)
		#>>>Push the first joints orient to 		
		#i_jnt.jointOrient = i_jnt.rotate
		#i_jnt.rotate = [0,0,0]	
        #>>>Reconnect the joints
        for cnt,i_jnt in enumerate(ml_moduleJoints[1:]):#parent each to the one before it
            i_jnt.parent = ml_moduleJoints[cnt].mNode
	    i_p = cgmMeta.cgmObject(i_jnt.parent)
	    #Verify inverse scale connection
	    cgmMeta.cgmAttr(i_jnt,"inverseScale").doConnectIn("%s.scale"%i_p.mNode)

    if self._mi_module.moduleType in ['foot']:
        log.debug("Special case orient")
        if len(l_moduleJoints) > 1:
            helper = self._mi_templateNull.orientRootHelper.mNode
            if helper:
                log.debug("Root joint fix...")                
                rootJoint = l_moduleJoints[0]
                ml_moduleJoints[1].parent = False #unparent the first child
                constBuffer = mc.orientConstraint( helper,rootJoint,maintainOffset = False)
                mc.delete (constBuffer[0])   
                ml_moduleJoints[1].parent = rootJoint
		ml_moduleJoints[1].jointOrient = ml_moduleJoints[1].rotate
		ml_moduleJoints[1].rotate = [0,0,0]        
    
    #Copy 

    #Connect to parent
    try:
	if self._mi_module.getMessage('moduleParent'):#If we have a moduleParent, constrain it
	    connectToParentModule(self._mi_module)    
    except:
	raise StandardError, "Failed to connect to module parent"
    
    #""" Freeze the rotations """
    try:
	jntUtils.metaFreezeJointOrientation(ml_moduleJoints) 
    except Exception,error:
	raise StandardError,"Failed to freeze rotations | %s"%error

    try:
	for i,i_jnt in enumerate(ml_moduleJoints):
	    log.debug(i_jnt.getAttr('cgmName'))
	    if i_jnt.getAttr('cgmName') in ['ankle']:
		log.debug("Copy orient from parent mode: %s"%i_jnt.getShortName())
		joints.doCopyJointOrient(i_jnt.parent,i_jnt.mNode)
    except:
	raise StandardError, "Failed to Copy parent joint orient"    
    return True




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def deleteSkeletonOLD(self,*args,**kws):  
    #MUST BE A MODULE
    if not self.isSkeletonized():
        log.warning("Not skeletonized. Cannot delete skeleton: '%s'"%self.getShortName())
        return False
    log.debug(">>> %s.deleteSkeleton >> "%self.p_nameShort + "="*75)            
    
    ml_skinJoints = self.rig_getSkinJoints(asMeta = True)
    l_skinJoints = [i_j.p_nameLong for i_j in ml_skinJoints if i_j ]  
    
    #We need to see if any of or moduleJoints have children
    l_strayChildren = []
    for i_jnt in ml_skinJoints:
        buffer = i_jnt.getChildren(True)
        for c in buffer:
            if c not in l_skinJoints:
                try:
                    i_c = cgmMeta.cgmObject(c)
                    i_c.parent = False
                    l_strayChildren.append(i_c.mNode)
                except Exception,error:
                    log.warning(error)     
		    
    log.debug("l_strayChildren: %s"%l_strayChildren)    
    self.msgList_purge('skinJoints')
    self.msgList_purge('moduleJoints')
    self.msgList_purge('handleJoints')
    
    if l_skinJoints:
	mc.delete(l_skinJoints)
    else:return False
	

    
    return True

def connectToParentModule(self):
    """
    Pass a module class. Constrains template root to parent's closest template object
    """
    log.debug(">>> %s.connectToParentModule >> "%self.p_nameShort + "="*75)            
    if not self.isSkeletonized():
        log.error("Must be skeletonized to contrainToParentModule: '%s' "%self.getShortName())
        return False
    
    ml_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta = True)
    l_moduleJoints = [i_o.p_nameShort for i_o in ml_moduleJoints]
    if not self.getMessage('moduleParent'):
        return False
    else:
        #>>> Get some info
        i_rigNull = self.rigNull #Link
        i_parent = self.moduleParent #Link
        parentState = i_parent.getState() 
        if i_parent.isSkeletonized():#>> If we have a module parent
            #>> If we have another anchor
	    if self.moduleType == 'eyelids':
		str_targetObj = i_parent.rigNull.msgList_getMessage('moduleJoints')[0]
		for mJoint in ml_moduleJoints:
		    mJoint.parent = str_targetObj
	    else:
		l_parentSkinJoints = i_parent.rigNull.msgList_getMessage('moduleJoints')
		str_targetObj = distance.returnClosestObject(l_moduleJoints[0],l_parentSkinJoints)
		ml_moduleJoints[0].parent = str_targetObj
            
        else:
            log.error("Parent has not been skeletonized...")           
            return False  
    return True


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  

def skeletonizeCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Skeletonizes a character
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = modules.returnModules(masterNull)
    orderedModules = modules.returnOrderedModules(modules)
    #>>> Do the spine first
    stateCheck = modules.moduleStateCheck(orderedModules[0],['template'])
    if stateCheck == 1:
        spineJoints = skeletonize(orderedModules[0])
    else:
        print ('%s%s' % (module,' has already been skeletonized. Moving on...'))
    
    #>>> Do the rest
    for module in orderedModules[1:]:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck == 1:
            templateNull = modules.returnTemplateNull(module)
            root =  modules.returnInfoNullObjects(module,'templatePosObjects',types='templateRoot')
            
            #>>> See if our item has a non default anchor
            anchored = storeTemplateRootParent(module) 
            if anchored == True:
                anchor =  attributes.returnMessageObject(root[0],'skeletonParent')
                closestJoint = distance.returnClosestObject(anchor,spineJoints)
            else:
                closestJoint = distance.returnClosestObject(root[0],spineJoints) 
        
            l_limbJoints = skeletonize(module)
            rootName = rigging.doParentReturnName(l_limbJoints[0],closestJoint)
            print rootName
        else:
            print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def skeletonStoreCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    stores a skeleton of a character
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = modules.returnModules(masterNull)
    orderedModules = modules.returnOrderedModules(modules)
    #>>> Do the spine first
    stateCheck = modules.moduleStateCheck(orderedModules[0],['template'])
    if stateCheck == 1:
        spineJoints = modules.saveTemplateToModule(orderedModules[0])
    else:
        print ('%s%s' % (module,' has already been skeletonized. Moving on...'))
    
    #>>> Do the rest
    for module in orderedModules[1:]:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck == 1:
            templateNull = modules.returnTemplateNull(module)        
            modules.saveTemplateToModule(module)
        else:
            print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

       
         
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>            

def storeTemplateRootParent(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Stores the template root parent to the root control if there is a new one
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    templateNull = modules.returnTemplateNull(moduleNull)
    root =   modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    parent = search.returnParentObject(root, False)
    if parent != templateNull:
        if parent != False:
            attributes.storeObjectToMessage(parent,root,'skeletonParent')
            return True
    return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#>>> Tools    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
