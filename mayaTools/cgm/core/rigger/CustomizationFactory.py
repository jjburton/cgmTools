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
from cgm.lib import (curves,distance,search,lists,modules,attributes)


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
    def __init__(self,customizationNode = 'MorpheusCustomization'): 
        """
        To do:
        1) Gather info, make sure we have everything
        2) Mirror joints properly
        3) mirror controls 
        4) Shape parent controls to their joints
        5) Setup rig
        """
        # Get our base info
        #==================	        
        #>>> Customization network node
        log.info(">>> go.__init__")
        if mc.objExists('MorpheusCustomization'):
            p = cgmMeta.cgmNode('MorpheusCustomization')
        else:
            p = cgmMeta.cgmNode(name = 'MorpheusCustomization')
        
        p.addAttr('cgmType','cgmCustomizationNetwork',lock=True)
        p.addAttr('leftJoints',attrType = 'message',lock=True)
        p.addAttr('leftRoots',attrType = 'message',lock=True)
        
        self.cls = "CustomizationFactory.go"
        self.p = p# Link for shortness
        
        #>>> Split out the left joints
        self.l_leftJoints = []
        self.l_leftRoots = []
        for i_jnt in self.p.jointList:
            if i_jnt.hasAttr('cgmDirection') and i_jnt.cgmDirection == 'left':
               self.l_leftJoints.append(i_jnt.mNode)
               if i_jnt.parent:#if it has a panent
                   i_parent = cgmMeta.cgmObject(i_jnt.parent)
                   log.debug("'%s' child of '%s'"%(i_jnt.getShortName(),i_parent.getShortName()))
                   if not i_parent.hasAttr('cgmDirection'):
                       self.l_leftRoots.append(i_jnt.mNode)
        self.l_leftJoints = lists.returnListNoDuplicates(self.l_leftJoints)
        self.l_leftRoots = lists.returnListNoDuplicates(self.l_leftRoots)
        p.leftJoints = self.l_leftJoints
        p.leftRoots = self.l_leftRoots
                   
        #>>> Customization network node
        log.info("ShaperJoints: %s"%self.p.getMessage('jointList',False))
        log.info("leftJoints: %s"%self.p.getMessage('leftJoints',False))
        log.info("leftRoots: %s"%self.p.getMessage('leftRoots',False))
        
        #log.info("partType: %s"%self.partType)
        #log.info("direction: %s"%self.direction) 
        #log.info("colors: %s"%self.moduleColors)
        #log.info("coreNames: %s"%self.coreNames)
        #log.info("corePosList: %s"%self.corePosList)
        
        
        #Mirror our joints, make mirror controls and store them appropriately
        #====================================================================
        self.l_leftJoints = self.p.getMessage('leftJoints',False)
        for i_root in self.p.leftRoots:
            l_mirrored = mc.mirrorJoint(i_root.mNode,mirrorBehavior = True, mirrorYZ = True)
            mc.select(cl=True)
            mc.select(i_root.mNode,hi=True)
            l_base = mc.ls( sl=True )
            for i,jnt in enumerate(l_mirrored):
                log.info("On '%s'..."%jnt)
                i_jnt = cgmMeta.cgmObject(jnt)
                i_jnt.cgmDirection = 'right'
                i_jnt.doName()
                i_jnt.doStore('cgmMirrorMatch',l_base[i])
                attributes.storeInfo(l_base[i],'cgmMirrorMatch',i_jnt.mNode)
                
                #>>> Make curve
                index = self.l_leftJoints.index(l_base[i]) #Find our main index
                buffer = mc.duplicate(self.p.leftJoints[index].controlCurve.mNode) #Duplicate curve
                i_crv = cgmMeta.cgmObject( buffer[0] )
                i_crv.cgmDirection = 'right'#Change direction
                i_jnt.doStore('controlCurve',i_crv.mNode)#Store new curve to new joint
                i_crv.doStore('cgmSource',i_jnt.mNode)
                i_crv.doName()#name it
                
                #>>> Mirror the curve
                s_prntBuffer = i_crv.parent#Shouldn't be necessary later
                grp = mc.group(em=True)#Group world center
                i_crv.parent = grp
                attributes.doSetAttr(grp,'sx',-1)#Set an attr
                i_crv.parent = s_prntBuffer
                mc.delete(grp)
                
                l_colorRight = modules.returnSettingsData('colorRight',True)                
                curves.setCurveColorByName(i_crv.mNode,l_colorRight[0])#Color it, need to get secodary indexes
                

        """
        if self.m.mClass == 'cgmLimb':
            log.info("mode: cgmLimb Template")
            doMakeLimbTemplate(self)
        else:
            raise NotImplementedError,"haven't implemented '%s' templatizing yet"%self.m.mClass
            """