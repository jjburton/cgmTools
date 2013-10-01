"""
curve Utils
Josh Burton 
www.cgmonks.com

"""
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
from maya import OpenMaya

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core.classes import NodeFactory as NodeF

reload(cgmGeneral)
from cgm.core.cgmPy import validateArgs as cgmValid
reload(cgmValid)
from cgm.lib import (distance,
                     locators,
                     attributes,
                     curves,
                     deformers,
                     lists,
                     rigging,
                     skinning,
                     dictionary,
                     search,
                     nodes,
                     joints,
                     cgmMath)
reload(distance)

#>>> Utilities
#===================================================================
def attachObjToSurface(objToAttach = None, targetSurface = None, createControlLoc = None, targetUpObj = None, orientation = None,**kws):
    """
    Function to attach an object to a surface. Actions to do:
    1)Make a transform group that follows the surface
    2)Make a follicle
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self, objToAttach = None, targetSurface = None, createControlLoc = None, targetUpObj = None, orientation = None,**kws):
	    """
	    @kws
	    source -- joint to add length to
	    target -- the attr to connect this to. If none is provided, it adds to the joint
	    connectBy -- mode
	    orienation(str) -- joint orientation
    
	    """		    
	    super(fncWrap, self).__init__(objToAttach, targetSurface,createControlLoc, targetUpObj,orientation,**kws)
	    self._str_funcName = 'attachObjToSurface'	
	    self.__dataBind__(**kws)
	    self.d_kwsDefined = {'objToAttach':objToAttach,
	                         'targetSurface':targetSurface,
	                         'targetUpObj':targetUpObj,
	                         'createControlLoc':createControlLoc,
	                         'orientation':orientation,}
	    self.l_funcSteps = [{'step':'Validate','call':self._validate},
		                {'step':'Create','call':self._create}]		    
	    #=================================================================
	    if log.getEffectiveLevel() == 10:#If debug
		self.report()
		
	def _validate(self):
	    #>> validate ============================================================================
	    self.mi_obj = cgmMeta.validateObjArg(self.d_kwsDefined['objToAttach'],cgmMeta.cgmObject,noneValid=False)
	    self.mi_targetUpObj = cgmMeta.validateObjArg(self.d_kwsDefined['targetUpObj'],cgmMeta.cgmObject,noneValid=True)
	    self.mi_targetSurface = cgmMeta.validateObjArg(self.d_kwsDefined['targetSurface'],mayaType='nurbsSurface',noneValid=False)
	    
	    self._str_funcCombined = self._str_funcCombined + "(%s,%s)"%(self.mi_obj.p_nameShort,self.mi_targetSurface.p_nameShort)
	    
	    self.l_shapes = mc.listRelatives(self.mi_targetSurface.mNode,shapes=True)
	    if len(self.l_shapes)>1:
		log.warning( "More than one shape found. Using 0. targetSurface : %s | shapes: %s"%(self.mi_targetSurface.p_nameShort,self.l_shapes) )
	    self.mi_shape = cgmMeta.validateObjArg(self.l_shapes[0],cgmMeta.cgmNode,noneValid=False)
	    self.b_createControlLoc = cgmValid.boolArg(self.d_kwsDefined['createControlLoc'],calledFrom=self._str_funcCombined)
	    
	    #Get info ============================================================================
	    self.d_closestInfo = distance.returnClosestPointOnSurfaceInfo(self.mi_obj.mNode,self.mi_targetSurface.mNode)
	    
	def _create(self):
	    d_closestInfo = self.d_closestInfo
	    
	    #>>> Follicle ============================================================================
	    l_follicleInfo = nodes.createFollicleOnMesh(self.mi_targetSurface.mNode)
	    mi_follicleFollowTrans = cgmMeta.cgmObject(l_follicleInfo[1],setClass=True)
	    mi_follicleFollowShape = cgmMeta.cgmNode(l_follicleInfo[0])
	    
	    l_follicleInfo = nodes.createFollicleOnMesh(self.mi_targetSurface.mNode)
	    mi_follicleRootTrans = cgmMeta.cgmObject(l_follicleInfo[1],setClass=True)
	    mi_follicleRootShape = cgmMeta.cgmNode(l_follicleInfo[0])	    
	    
	    #> Name ----------------------------------------------------------------------------------
	    mi_follicleFollowTrans.doStore('cgmName',self.mi_obj.mNode)
	    mi_follicleFollowTrans.addAttr('cgmTypeModifier','follow',lock=True)
	    mi_follicleFollowTrans.doName()
	    
	    mi_follicleRootTrans.doStore('cgmName',self.mi_obj.mNode)
	    mi_follicleRootTrans.addAttr('cgmTypeModifier','root',lock=True)
	    mi_follicleRootTrans.doName()
	    
	    #>Set follicle value ---------------------------------------------------------------------
	    for follShape in mi_follicleFollowShape, mi_follicleRootShape:
		follShape.parameterU = d_closestInfo['normalizedU']
		follShape.parameterV = d_closestInfo['normalizedV']
            
            self.mi_follicleFollowTrans = mi_follicleFollowTrans#link
	    self.mi_follicleFollowShape = mi_follicleFollowShape#link
	    self.mi_follicleRootTrans = mi_follicleRootTrans#link
	    self.mi_follicleRootShape = mi_follicleRootShape#link
	    
            #Groups =======================================================================================
	    mi_followGroup = mi_follicleFollowTrans.duplicateTransform()
	    mi_followGroup.doStore('cgmName',self.mi_obj.mNode)
	    mi_followGroup.addAttr('cgmTypeModifier','follow',lock=True)
	    mi_followGroup.doName()
	    self.mi_followGroup = mi_followGroup
	    self.mi_followGroup.parent = mi_follicleFollowTrans
	    
	    mi_offsetGroup = self.mi_obj.duplicateTransform()
	    mi_offsetGroup.doStore('cgmName',self.mi_obj.mNode)
	    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
	    mi_offsetGroup.doName()
	    mi_offsetGroup.parent = mi_followGroup
	    self.mi_offsetGroup =   mi_offsetGroup 
	    
	    mi_zeroGroup = cgmMeta.cgmObject( mi_offsetGroup.doGroup(True),setClass=True)	 
	    mi_zeroGroup.doStore('cgmName',self.mi_obj.mNode)
	    mi_zeroGroup.addAttr('cgmTypeModifier','zero',lock=True)
	    mi_zeroGroup.doName()	    
	    mi_zeroGroup.parent = mi_followGroup
            self.mi_zeroGroup = mi_zeroGroup
	    
	    self.mi_targetUpObj 
	    
	    #Driver loc -----------------------------------------------------------------------
	    mi_driverLoc = self.mi_obj.doLoc()
	    mi_driverLoc.doStore('cgmName',self.mi_obj.mNode)
	    mi_driverLoc.addAttr('cgmTypeModifier','driver',lock=True)
	    mi_driverLoc.doName()
	    self.mi_driverLoc = mi_driverLoc
	    mi_driverLoc.parent = mi_offsetGroup
	    
	    #Closest setup =====================================================================
	    mi_controlLoc = self.mi_obj.doLoc()
	    mi_controlLoc.doStore('cgmName',self.mi_obj.mNode)
	    mi_controlLoc.addAttr('cgmTypeModifier','control',lock=True)
	    mi_controlLoc.doName()
	    self.mi_controlLoc = mi_controlLoc
	    
	    mi_group = cgmMeta.cgmObject( mi_controlLoc.doGroup(),setClass=True )
	    mi_group.parent = mi_follicleRootTrans
	    
	    #Create decompose node --------------------------------------------------------------
	    mi_worldTranslate = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
	    mi_worldTranslate.doStore('cgmName',self.mi_obj.mNode)
	    mi_worldTranslate.doName()
	    self.mi_worldTranslate = mi_worldTranslate
	
	    attributes.doConnectAttr("%s.worldMatrix"%(mi_controlLoc.mNode),"%s.%s"%(mi_worldTranslate.mNode,'inputMatrix'))
	    
	    #Create node --------------------------------------------------------------
	    mi_cpos = NodeF.createNormalizedClosestPointNode(self.mi_obj,self.mi_targetSurface)

	    attributes.doConnectAttr ((mi_cpos.mNode+'.out_uNormal'),(mi_follicleFollowShape.mNode+'.parameterU'))
	    attributes.doConnectAttr  ((mi_cpos.mNode+'.out_vNormal'),(mi_follicleFollowShape.mNode+'.parameterV'))
	    #attributes.doConnectAttr  ((mi_controlLoc.mNode+'.translate'),(mi_cpos.mNode+'.inPosition'))
	    attributes.doConnectAttr  ((mi_worldTranslate.mNode+'.outputTranslate'),(mi_cpos.mNode+'.inPosition'))
	    
	    #Constrain =====================================================================
	    mc.pointConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)
	    mc.orientConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)    
	    
	    #mc.orientConstraint(self.mi_controlLoc.mNode, self.mi_driverLoc.mNode, maintainOffset = True) 
	    for attr in ['z']:
		attributes.doConnectAttr  ((mi_controlLoc.mNode+'.t%s'%attr),(mi_offsetGroup.mNode+'.t%s'%attr))
		
	    return
	    
	    """ make the node """
	    closestPointNode = mc.createNode ('closestPointOnSurface',name= (obj+'_closestPointInfoNode'))
	    """ to account for target objects in heirarchies """
	    attributes.doConnectAttr((surfaceLoc+'.translate'),(closestPointNode+'.inPosition'))
	    attributes.doConnectAttr((controlSurface[0]+'.worldSpace'),(closestPointNode+'.inputSurface'))
	    
	    pointOnSurfaceNode = mc.createNode ('pointOnSurfaceInfo',name= (obj+'_posInfoNode'))
	    """ Connect the info node to the surface """                  
	    attributes.doConnectAttr  ((controlSurface[0]+'.worldSpace'),(pointOnSurfaceNode+'.inputSurface'))
	    """ Contect the pos group to the info node"""
	    attributes.doConnectAttr ((pointOnSurfaceNode+'.position'),(surfaceFollowGroup+'.translate'))
	    attributes.doConnectAttr ((closestPointNode+'.parameterU'),(pointOnSurfaceNode+'.parameterU'))
	    attributes.doConnectAttr  ((closestPointNode+'.parameterV'),(pointOnSurfaceNode+'.parameterV'))
	
	    """ if we wanna aim """
	    if aimObject != False: 
		""" make some locs """
		upLoc = locators.locMeObject(surface)
		aimLoc = locators.locMeObject(aimObject)
		attributes.storeInfo(upLoc,'cgmName',obj)
		attributes.storeInfo(upLoc,'cgmTypeModifier','up')
		upLoc = NameFactoryOld.doNameObject(upLoc)
		
		attributes.storeInfo(aimLoc,'cgmName',aimObject)
		attributes.storeInfo(aimLoc,'cgmTypeModifier','aim')
		aimLoc = NameFactoryOld.doNameObject(aimLoc)
	
		attributes.storeInfo(surfaceFollowGroup,'locatorUp',upLoc)
		attributes.storeInfo(surfaceFollowGroup,'aimLoc',aimLoc)
		#mc.parent(upLoc,aimObject)
		
		boundingBoxSize = distance.returnBoundingBoxSize(surface)
		f_distance = max(boundingBoxSize)*2
		
		mc.xform(upLoc,t = [0,f_distance,0],ws=True,r=True)
		
		attributes.doConnectAttr((aimLoc+'.translate'),(closestPointNode+'.inPosition'))
	
		""" constrain the aim loc to the aim object """
		pointConstraintBuffer = mc.pointConstraint(aimObject,aimLoc,maintainOffset = True, weight = 1)
		
		""" aim it """
		aimConstraintBuffer = mc.aimConstraint(aimLoc,surfaceFollowGroup,maintainOffset = True, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
	
		""" aim the controller back at the obj"""
		aimConstraintBuffer = mc.aimConstraint(obj,aimLoc,maintainOffset = True, weight = 1, aimVector = [0,0,-1], upVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
		
		mc.parent(upLoc,aimObject)
	    else:
		mc.delete(closestPointNode)
	    
	    transformGroup = rigging.doParentReturnName(transformGroup,surfaceFollowGroup)
	    """finally parent it"""    
	    if parent == True:
		mc.parent(obj,transformGroup)
		
	    if parent == 'constrain':
		mc.parentConstraint(transformGroup,obj,maintainOffset = True)
	    
	    mc.delete(surfaceLoc)
	    return [transformGroup,surfaceFollowGroup]
	
    return fncWrap(objToAttach, targetSurface, createControlLoc, targetUpObj, orientation,**kws).go()
