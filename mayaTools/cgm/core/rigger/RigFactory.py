# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
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
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)
from cgm.core.lib import rayCaster as RayCast
from cgm.core.rigger import ModuleCurveFactory as mCurveFactory
reload(mCurveFactory)
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
reload(mControlFactory)

from cgm.core.rigger.lib.Limb import (spine,neckHead)
reload(spine)
reload(neckHead)

from cgm.lib import (cgmMath,
                     attributes,
                     deformers,
                     locators,
                     constraints,
                     modules,
                     nodes,
                     distance,
                     dictionary,
                     joints,
                     skinning,
                     rigging,
                     search,
                     curves,
                     lists,
                     )

class go(object):
    @r9General.Timer
    def __init__(self,moduleInstance,forceNew = True,**kws): 
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
	"""
	try:moduleInstance
	except StandardError,error:
	    log.error("RigFactory.go.__init__>>module instance isn't working!")
	    raise StandardError,error    
	"""
	i_module = cgmMeta.validateObjArg(moduleInstance,cgmPM.cgmModule,noneValid=True)
	if not i_module:
	    raise StandardError,"RigFactory.go.init Module instance no longer exists: '%s'"%moduleInstance

        assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
        assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
        
        log.info(">>> RigFactory.go.__init__")
        self._i_module = moduleInstance# Link for shortness
	self._i_module.__verify__()
	self._cgmClass = 'RigFactory.go'
	
	#Verify we have a puppet and that puppet has a masterControl which we need for or master scale plug
	if not self._i_module.modulePuppet._verifyMasterControl():
	    raise StandardError,"RigFactory.go.init masterControl failed to verify"
	
	self._i_masterControl = self._i_module.modulePuppet.masterControl
	self._i_masterSettings = self._i_masterControl.controlSettings
	self._i_masterDeformGroup = self._i_module.modulePuppet.masterNull.deformGroup
	

        """
        if moduleInstance.hasControls():
            if forceNew:
                deleteControls(moduleInstance)
            else:
                log.warning("'%s' has already been skeletonized"%moduleInstance.getShortName())
                return        
        """
        #>>> Gather info
        #=========================================================	
        self._l_moduleColors = self._i_module.getModuleColors()
        self._l_coreNames = self._i_module.coreNames.value
        self._i_templateNull = self._i_module.templateNull#speed link
	self._i_rigNull = self._i_module.rigNull#speed link
        self._bodyGeo = self._i_module.modulePuppet.getGeo() or ['Morphy_Body_GEO'] #>>>>>>>>>>>>>>>>>this needs better logic   
        self._version = self._i_rigNull.version
        #Joints
        self._l_skinJoints = self._i_rigNull.getMessage('skinJoints')
        self._ml_skinJoints = self._i_rigNull.skinJoints #We buffer this because when joints are duplicated, the multiAttrs extend with duplicates
        
        #>>> part name 
        self._partName = self._i_module.getPartNameBase()
        self._partType = self._i_module.moduleType or False
        
        #>>>Version Check
	#TO DO: move to moduleFactory
        if self._partType in d_moduleRigVersions.keys():
	    newVersion = d_moduleRigVersions[self._partType]
	    if self._version != newVersion:
		log.warning("RigFactory.go>>> '%s' rig version out of date: %s != %s"%(self._partType,self._version,newVersion))	
	    else:
		log.warning("RigFactory.go>>> '%s' rig version up to date !"%(self._partType))	
	else:
	    raise StandardError,"PartType ('%s') not in d_moduleRigVersions.keys: %s"%(self._partType,d_moduleRigVersions.keys())
	
        self._direction = None
        if self._i_module.hasAttr('cgmDirection'):
            self._direction = self._i_module.cgmDirection or None
               
        #>>> Instances and joint stuff
        self._jointOrientation = str(modules.returnSettingsData('jointOrientation')) or 'zyx'       
	
	#>>>Connect switches
	try: verify_moduleRigToggles(self)
	except StandardError,error:
	    raise StandardError,"init.verify_moduleRigToggles>> fail: %s"%error	
	
	#>>> Deform group for the module
	#=========================================================	
	if not self._i_module.getMessage('deformNull'):
	    #Make it and link it
	    buffer = rigging.groupMeObject(self._ml_skinJoints[0].mNode,False)
	    i_grp = cgmMeta.cgmObject(buffer,setClass=True)
	    i_grp.addAttr('cgmName',self._partName,lock=True)
	    i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
	    i_grp.doName()
	    i_grp.parent = self._i_masterDeformGroup.mNode
	    self._i_module.connectChildNode(i_grp,'deformNull','module')
	    
	self._i_deformNull = self._i_module.deformNull
	
        #Make our stuff
        if self._partType in d_moduleRigFunctions.keys():
	    self._md_controlShapes = {}
            log.info("mode: cgmLimb control building")
            #d_moduleRigFunctions[self._partType](self,**kws)
	    self.doBuild = d_moduleRigFunctions[self._partType]
            #if not limbControlMaker(self,self.l_controlsToMakeArg):
                #raise StandardError,"limbControlMaker failed!"
        else:
            raise NotImplementedError,"haven't implemented '%s' rigging yet"%self._i_module.mClass

@r9General.Timer
def verify_moduleRigToggles(goInstance):
    """
    Rotate orders
    hips = 3
    """    
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    str_settings = str(self._i_masterSettings.getShortName())
    str_partBase = str(self._partName + '_rig')
    str_moduleRigNull = str(self._i_rigNull.getShortName())
    
    self._i_masterSettings.addAttr(str_partBase,enumName = 'off:lock:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
    try:NodeF.argsToNodes("%s.gutsVis = if %s.%s > 0"%(str_moduleRigNull,str_settings,str_partBase)).doBuild()
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> vis arg fail: %s"%error
    try:NodeF.argsToNodes("%s.gutsLock = if %s.%s == 2:0 else 2"%(str_moduleRigNull,str_settings,str_partBase)).doBuild()
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> lock arg fail: %s"%error

    self._i_rigNull.overrideEnabled = 1		
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(self._i_rigNull.mNode,'overrideVisibility'))
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(self._i_rigNull.mNode,'overrideDisplayType'))    

    return True

def bindJoints_connect(goInstance):
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    l_rigJoints = self._i_rigNull.getMessage('rigJoints') or False
    l_skinJoints = self._i_rigNull.getMessage('skinJoints') or False
    if len(l_skinJoints)!=len(l_rigJoints):
	raise StandardError,"connect_ToBind>> Rig/Skin joint chain lengths don't match: %s"%self._i_module.getShortName()
    
    for i,i_jnt in enumerate(self._i_rigNull.skinJoints):
	log.info("'%s'>>drives>>'%s'"%(self._i_rigNull.rigJoints[i].getShortName(),i_jnt.getShortName()))
	pntConstBuffer = mc.parentConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
	#pntConstBuffer = mc.pointConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)
	#orConstBuffer = mc.orientConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)        
        
        attributes.doConnectAttr((self._i_rigNull.rigJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))
	#scConstBuffer = mc.scaleConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)                
        #Scale constraint connect doesn't work

    
    
    return True
	
@r9General.Timer
def build_spine(goInstance,buildShapes = False, buildControls = False,buildSkeleton = False, buildDeformation = False, buildRig= False):
    """
    Rotate orders
    hips = 3
    """    
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance#Link
    
    if buildShapes: spine.build_shapes(self)
    if buildControls: spine.build_controls(self)    
    if buildSkeleton: spine.build_rigSkeleton(self)
    if buildDeformation: spine.build_deformation(self)
    if buildRig: spine.build_rig(self)    
        
    return 

@r9General.Timer
def build_neckHead(goInstance,buildShapes = False, buildControls = False,buildSkeleton = False, buildDeformation = False, buildRig= False):
    """
    Rotate orders
    hips = 3
    """    
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance#Link
    
    if buildShapes: neckHead.build_shapes(self)
    if buildSkeleton: neckHead.build_rigSkeleton(self)    
    if buildControls: neckHead.build_controls(self)    
    if buildDeformation: neckHead.build_deformation(self)
    if buildRig: neckHead.build_rig(self)    
        
    return 

#>>> Register rig functions
#=====================================================================
d_moduleRigFunctions = {'torso':build_spine,'neckHead':build_neckHead,
                        }
d_moduleRigVersions = {'torso':str(spine.__version__),'neckHead':str(neckHead.__version__)
                        }
    
 