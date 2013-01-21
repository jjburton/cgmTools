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
from cgm.lib import (curves,distance,search)
reload(attributes)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Temp
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def autoTagControls(customizationNode = 'MorpheusCustomization',l_controls=None): 
    """
    For each joint:
    1) tag it mClass as cgmObject
    2) Find the closest curve
    3) Tag that curve as a cgmObject mClass
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    assert mc.objExists(customizationNode),"'%s' doesn't exist"%customizationNode
    log.info(">>> autoTagControls")
    log.info("l_joints: %s"%customizationNode)
    log.info("l_controls: %s"%l_controls)
    p = r9Meta.MetaClass(customizationNode)
    buffer = p.getMessage('jointList')
    for o in buffer:
        i_o = cgmMeta.cgmObject(o)
        i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)    
    if l_controls is None:#If we don't have any controls passed
        l_iControls = []
        if mc.objExists('controlCurves'):#Check the standard group
            l_controls = search.returnAllChildrenObjects('controlCurves')
        for c in l_controls:
            i_c = cgmMeta.cgmObject(c)
            i_c.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
            l_iControls.append(i_c.mNode)
        p.addAttr('controlCurves',attrType = 'message', value = l_iControls)
    for i_o in p.jointList:
        closestObject = distance.returnClosestObject(i_o.mNode,p.getMessage('controlCurves'))
        if closestObject:
            log.info("'%s' <<tagging>> '%s'"%(i_o.getShortName(),closestObject))            
            i_closestObject = cgmMeta.cgmObject(closestObject)
            i_closestObject.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
            i_o.addAttr('controlCurve',value = i_closestObject.mNode,attrType = 'messageSimple', lock = True)
            i_closestObject.addAttr('cgmSource',value = i_o.mNode,attrType = 'messageSimple', lock = True)
            i_closestObject.doCopyNameTagsFromObject(i_o.mNode,['cgmType','cgmTypeModifier'])
            
            i_o.addAttr('cgmTypeModifier','shaper',attrType='string',lock = True)            
            i_closestObject.addAttr('cgmType','bodyShaper',attrType='string',lock = True)
            
            i_o.doName()
            i_closestObject.doName()
            
def doTagCurveFromJoint(curve = None, joint = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if curve is None:
        curve = mc.ls(sl=True)[1] or False
    if joint is None:
        joint = mc.ls(sl=True)[0] or False
        
    assert mc.objExists(curve),"'%s' doesn't exist"%curve
    assert mc.objExists(joint),"'%s' doesn't exist"%joint
    
    log.info(">>> doTagCurveFromJoint")
    log.info("curve: %s"%curve)
    log.info("joint: %s"%joint)
    i_o = cgmMeta.cgmObject(joint)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
    
    i_crv = cgmMeta.cgmObject(curve)
    i_crv.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
    i_o.addAttr('controlCurve',value = i_crv.mNode,attrType = 'messageSimple', lock = True)
    i_crv.addAttr('cgmSource',value = i_o.mNode,attrType = 'messageSimple', lock = True)
    i_crv.doCopyNameTagsFromObject(i_o.mNode,['cgmType','cgmTypeModifier'])
    
    i_o.addAttr('cgmTypeModifier','shaper',attrType='string',lock = True)            
    i_crv.addAttr('cgmType','bodyShaper',attrType='string',lock = True)
    
    i_o.doName()
    i_crv.doName()
    return True
    
            
            

        
        
    


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    @r9General.Timer
    def __init__(self,module,forceNew = False): 
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
        log.info(">>> go.__init__")        
        assert module.mClass in ['cgmModule','cgmLimb'],"Not a module"
        if module.isTemplated():
            if not forceNew:
                log.error("'%s' has already been templated"%module.getShortName())
                raise StandardError,"'%s' has already been templated"%module.getShortName()
            else:
                raise NotImplementedError,"Need to make a cleaner"
        
        self.cls = "TemplateFactory.go"
        self.m = module# Link for shortness
        
        self.moduleNullData = attributes.returnUserAttrsToDict(self.m.mNode)
        self.templateNull = self.m.getMessage('templateNull')[0] or False
        self.rigNull = self.m.getMessage('rigNull')[0] or False
        self.moduleParent = self.moduleNullData.get('moduleParent')
        self.moduleColors = self.m.getModuleColors()
        self.coreNames = self.m.coreNames.value
        self.corePosList = self.m.templateNull.templateStarterData
        self.foundDirections = False #Placeholder to see if we have it
        
        assert len(self.coreNames) == len(self.corePosList),"coreNames length and corePosList doesn't match"
        
        #>>> part name 
        self.partName = NameFactory.returnUniqueGeneratedName(self.m.mNode, ignore = 'cgmType')
        self.partType = self.m.moduleType or False
        
        self.direction = None
        if self.m.hasAttr('cgmDirection'):
            self.direction = self.m.cgmDirection or None
        
        #>>> template null 
        self.templateNullData = attributes.returnUserAttrsToDict(self.templateNull)
        self.curveDegree = self.m.templateNull.curveDegree
        self.rollOverride = self.m.templateNull.rollOverride
        
        log.info("Module: %s"%self.m.getShortName())
        log.info("moduleNullData: %s"%self.moduleNullData)
        log.info("partType: %s"%self.partType)
        log.info("direction: %s"%self.direction) 
        log.info("colors: %s"%self.moduleColors)
        log.info("coreNames: %s"%self.coreNames)
        log.info("corePosList: %s"%self.corePosList)
        

        if self.m.mClass == 'cgmLimb':
            log.info("mode: cgmLimb Template")
            doMakeLimbTemplate(self)
        else:
            raise NotImplementedError,"haven't implemented '%s' templatizing yet"%self.m.mClass