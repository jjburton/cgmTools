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
def attachObjToSurface(*args,**kws):
    """
    objToAttach = None
    targetSurface = None
    createControlLoc False
    createUpLoc = None
    f_offset = 1.0
    orientation = 'zyx',
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    """
	    @kws
	    source -- joint to add length to
	    target -- the attr to connect this to. If none is provided, it adds to the joint
	    connectBy -- mode
	    orienation(str) -- joint orientation
    
	    """		    
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'attachObjToSurface'
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'objToAttach',"default":None,'help':"Object to attach to the surface"},
	                                 {'kw':'targetSurface',"default":None},
	                                 {'kw':"createControlLoc","default":True},
	                                 {'kw':"createUpLoc","default":False},
	                                 {'kw':"parentToFollowGroup","default":False},	                  
	                                 {'kw':'f_offset',"default":1.0},
	                                 {'kw':'orientation',"default":'zyx'}]
	    self.__dataBind__(*args,**kws)
	    
	    self.l_funcSteps = [{'step':'Validate','call':self._validate},
		                {'step':'Create','call':self._create}]
	    
	    #=================================================================
		
	def _validate(self):
	    #>> validate ============================================================================
	    self.mi_obj = cgmMeta.validateObjArg(self.d_kws['objToAttach'],cgmMeta.cgmObject,noneValid=False)
	    self.mi_targetSurface = cgmMeta.validateObjArg(self.d_kws['targetSurface'],mayaType='nurbsSurface',noneValid=False)
	    self.mi_orientation = cgmValid.simpleOrientation( self.d_kws['orientation'] )
	    self._str_funcCombined = self._str_funcCombined + "(%s,%s)"%(self.mi_obj.p_nameShort,self.mi_targetSurface.p_nameShort)
	    
	    self.l_shapes = mc.listRelatives(self.mi_targetSurface.mNode,shapes=True)
	    if len(self.l_shapes)>1:
		log.debug( "More than one shape found. Using 0. targetSurface : %s | shapes: %s"%(self.mi_targetSurface.p_nameShort,self.l_shapes) )
	    self.mi_shape = cgmMeta.validateObjArg(self.l_shapes[0],cgmMeta.cgmNode,noneValid=False)
	    self.b_createControlLoc = cgmValid.boolArg(self.d_kws['createControlLoc'],calledFrom=self._str_funcCombined)
	    self.b_createUpLoc = cgmValid.boolArg(self.d_kws['createUpLoc'],calledFrom=self._str_funcCombined)
	    self.b_parentToFollowGroup = cgmValid.boolArg(self.d_kws['parentToFollowGroup'],calledFrom=self._str_funcCombined)
	    
	    self.f_offset = cgmValid.valueArg(self.d_kws['f_offset'], calledFrom=self._str_funcCombined)
	    #Get info ============================================================================
	    self.d_closestInfo = distance.returnClosestPointOnSurfaceInfo(self.mi_obj.mNode,self.mi_targetSurface.mNode)
	    
	    #Running Lists ============================================================================
	    self.md_return = {}
	    
	def _create(self):
	    #>> Quick links ============================================================================ 
	    d_closestInfo = self.d_closestInfo
	    
	    #>>> Follicle ============================================================================	    
	    l_follicleInfo = nodes.createFollicleOnMesh(self.mi_targetSurface.mNode)
	    mi_follicleAttachTrans = cgmMeta.cgmObject(l_follicleInfo[1],setClass=True)
	    mi_follicleAttachShape = cgmMeta.cgmNode(l_follicleInfo[0])	    
	    
	    #> Name ----------------------------------------------------------------------------------
	    mi_follicleAttachTrans.doStore('cgmName',self.mi_obj.mNode)
	    mi_follicleAttachTrans.addAttr('cgmTypeModifier','attach',lock=True)
	    mi_follicleAttachTrans.doName()
	    
	    #>Set follicle value ---------------------------------------------------------------------
	    mi_follicleAttachShape.parameterU = d_closestInfo['normalizedU']
	    mi_follicleAttachShape.parameterV = d_closestInfo['normalizedV']
            
	    self.mi_follicleAttachTrans = mi_follicleAttachTrans#link
	    self.mi_follicleAttachShape = mi_follicleAttachShape#link
	    self.mi_obj.connectChildNode(mi_follicleAttachTrans,"follicleAttach","targetObject")
	    self.md_return["follicleAttach"] = mi_follicleAttachTrans
	    self.md_return["follicleAttachShape"] = mi_follicleAttachShape
	    
	    if not self.b_createControlLoc:#If we don't have a control loc setup, we're just attaching to the surface
		#Groups =======================================================================================
		mi_followGroup = self.mi_obj.doDuplicateTransform(True)
		mi_followGroup.doStore('cgmName',self.mi_obj.mNode)
		mi_followGroup.addAttr('cgmTypeModifier','follow',lock=True)
		mi_followGroup.doName()	    
		mi_followGroup.parent = mi_follicleAttachTrans
		
		if self.b_parentToFollowGroup:
		    #raise StandardError,"shouldn't be here"		    
		    self.mi_obj.parent = mi_followGroup	
		    self.md_return["followGroup"] = mi_followGroup
		else:
		    #Driver loc -----------------------------------------------------------------------
		    mi_driverLoc = self.mi_obj.doLoc()
		    mi_driverLoc.doStore('cgmName',self.mi_obj.mNode)
		    mi_driverLoc.addAttr('cgmTypeModifier','driver',lock=True)
		    mi_driverLoc.doName()
		    self.mi_driverLoc = mi_driverLoc
		    mi_driverLoc.parent = mi_followGroup
		    mi_driverLoc.visibility = False
		
		    self.md_return["driverLoc"] = mi_driverLoc
		    #Constrain =====================================================================
		    mc.pointConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)
		    mc.orientConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)  		    
		
	    else:#Setup control loc stuff
		#raise StandardError,"nope"
		#>>> Follicle ============================================================================
		l_follicleInfo = nodes.createFollicleOnMesh(self.mi_targetSurface.mNode)
		mi_follicleFollowTrans = cgmMeta.cgmObject(l_follicleInfo[1],setClass=True)
		mi_follicleFollowShape = cgmMeta.cgmNode(l_follicleInfo[0])
		
		#> Name ----------------------------------------------------------------------------------
		mi_follicleFollowTrans.doStore('cgmName',self.mi_obj.mNode)
		mi_follicleFollowTrans.addAttr('cgmTypeModifier','follow',lock=True)
		mi_follicleFollowTrans.doName()
		
		#>Set follicle value ---------------------------------------------------------------------
		mi_follicleFollowShape.parameterU = d_closestInfo['normalizedU']
		mi_follicleFollowShape.parameterV = d_closestInfo['normalizedV']
		
		self.mi_follicleFollowTrans = mi_follicleFollowTrans#link
		self.mi_follicleFollowShape = mi_follicleFollowShape#link
		self.md_return["follicleFollow"] = mi_follicleFollowTrans
		self.md_return["follicleFollowShape"] = mi_follicleFollowShape
		
		self.mi_obj.connectChildNode(mi_follicleFollowTrans,"follicleFollow")
	
		#Groups =======================================================================================
		mi_followGroup = mi_follicleFollowTrans.duplicateTransform()
		mi_followGroup.doStore('cgmName',self.mi_obj.mNode)
		mi_followGroup.addAttr('cgmTypeModifier','follow',lock=True)
		mi_followGroup.doName()
		self.mi_followGroup = mi_followGroup
		self.mi_followGroup.parent = mi_follicleFollowTrans
		self.md_return["followGroup"] = mi_followGroup
		
		mi_offsetGroup = self.mi_obj.duplicateTransform()
		mi_offsetGroup.doStore('cgmName',self.mi_obj.mNode)
		mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		mi_offsetGroup.doName()
		mi_offsetGroup.parent = mi_followGroup
		self.mi_offsetGroup = mi_offsetGroup 
		self.md_return["offsetGroup"] = mi_offsetGroup
		mi_follicleFollowTrans.connectChildNode(mi_offsetGroup,"followOffsetGroup","follicle")
		
		mi_zeroGroup = cgmMeta.cgmObject( mi_offsetGroup.doGroup(True),setClass=True)	 
		mi_zeroGroup.doStore('cgmName',self.mi_obj.mNode)
		mi_zeroGroup.addAttr('cgmTypeModifier','zero',lock=True)
		mi_zeroGroup.doName()	    
		mi_zeroGroup.parent = mi_followGroup
		self.mi_zeroGroup = mi_zeroGroup
		self.md_return["zeroGroup"] = mi_zeroGroup
				
		#Driver loc -----------------------------------------------------------------------
		mi_driverLoc = self.mi_obj.doLoc()
		mi_driverLoc.doStore('cgmName',self.mi_obj.mNode)
		mi_driverLoc.addAttr('cgmTypeModifier','driver',lock=True)
		mi_driverLoc.doName()
		self.mi_driverLoc = mi_driverLoc
		mi_driverLoc.parent = mi_offsetGroup
		mi_driverLoc.visibility = False
		
		self.md_return["driverLoc"] = mi_driverLoc
		
		#Closest setup =====================================================================
		mi_controlLoc = self.mi_obj.doLoc()
		mi_controlLoc.doStore('cgmName',self.mi_obj.mNode)
		mi_controlLoc.addAttr('cgmTypeModifier','control',lock=True)
		mi_controlLoc.doName()
		self.mi_controlLoc = mi_controlLoc
		self.md_return["controlLoc"] = mi_controlLoc
		
		mi_group = cgmMeta.cgmObject( mi_controlLoc.doGroup(),setClass=True )
		mi_group.parent = mi_follicleAttachTrans
		
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
		for attr in self.mi_orientation.p_string[0]:
		    attributes.doConnectAttr  ((mi_controlLoc.mNode+'.t%s'%attr),(mi_offsetGroup.mNode+'.t%s'%attr))
		    
		if self.b_createUpLoc:#Make our up loc =============================================================
		    mi_upLoc = mi_zeroGroup.doLoc()
		    mi_upLoc.doStore('cgmName',self.mi_obj.mNode)
		    mi_upLoc.addAttr('cgmTypeModifier','up',lock=True)
		    mi_upLoc.doName()
		    mi_upLoc.parent = mi_zeroGroup
		    self.md_return["upLoc"] = mi_upLoc
		    mi_follicleFollowTrans.connectChildNode(mi_upLoc,"followUpLoc","follicle")
		    
		    #Move it ----------------------------------------------------------------------------------------
		    mi_upLoc.__setattr__("t%s"%self.mi_orientation.p_string[0],self.f_offset)
				
	    return self.md_return
	
    return fncWrap(*args,**kws).go()
