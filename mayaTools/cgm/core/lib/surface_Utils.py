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
def returnNormalizedUV(mesh, uValue, vValue):
    """
    uv Values from many functions need to be normalized to be correct when using those values for other functions
    
    The calculcaion for doing so is 
    size = maxV - minV
    sum = rawV + minV
    normalValue = sum / size
    
    :parameters:
	mesh(string) | Surface to normalize to
	uValue(float) | uValue to normalize 
	vValue(float) | vValue to normalize 

    :returns:
	Dict ------------------------------------------------------------------
	'uv'(double2) |  point from which we cast
	'uValue'(float) | normalized uValue
	'vValue'(float) | normalized vValue
	
    :raises:
	Exception | if reached
	
    """      
    try:
	_str_funcName = 'returnNormalizedUV'

	try:#Validation ----------------------------------------------------------------
	    mesh = cgmValid.objString(mesh,'nurbsSurface', calledFrom = _str_funcName)
	    if len(mc.ls(mesh))>1:
		raise StandardError,"{0}>>> More than one mesh named: {1}".format(_str_funcName,mesh)
	    _str_objType = search.returnObjectType(mesh)
	    
	    l_shapes = mc.listRelatives(mesh, shapes=True)
	    if len(l_shapes)>1:
		log.debug( "More than one shape found. Using 0. targetSurface : %s | shapes: %s"%(mesh,l_shapes) )
	    mi_shape = cgmMeta.validateObjArg(l_shapes[0],cgmMeta.cgmNode,noneValid=False)
	    
	    uMin = mi_shape.mnu
	    uMax = mi_shape.mxu
	    vMin = mi_shape.mnv
	    vMax = mi_shape.mxv
	    
	except Exception,error:raise Exception,"Validation failure | {0}".format(error) 		

	try:#Calculation ----------------------------------------------------------------
	    uSize = uMax - uMin
	    vSize = vMax - vMin
	    
	    uSum = uMin + uValue
	    vSum = vMin + vValue
	    
	    uNormal = uSum / uSize
	    vNormal = vSum / vSize
	except Exception,error:raise Exception,"Calculation |{0}".format(error) 		
	    
	try:
	    d_return = {'uv':[uNormal,vNormal],'uValue':uNormal,'vValue':vNormal}
	    return d_return 
	except Exception,error:raise Exception,"Return prep |{0}".format(error) 		

    except Exception,error:
	log.error(">>> {0} >> Failure! mesh: '{1}' | uValue: {2} | vValue {3}".format(_str_funcName,mesh,uValue,vValue))
	log.error(">>> {0} >> error: {1}".format(_str_funcName,error))        
	return None



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
	                                 {'kw':"pointAttach","default":False,'help':"pointConstrain only"},	                  	                                 
	                                 {'kw':"parentToFollowGroup","default":False,'help':"Parent the main object to the follow group"},	                  
	                                 {'kw':"attachControlLoc","default":True,'help':"Whether to setup a controlLoc attach setup"},	
	                                 {'kw':"connectOffset","default":True,'help':"Whether to connect the controlLoc fffset",'argType':'bool'},	                  	                                 	                                 
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
	    self.b_attachControlLoc = cgmValid.boolArg(self.d_kws['attachControlLoc'],calledFrom=self._str_funcCombined)
	    self.b_connectOffset = cgmValid.boolArg(self.d_kws['connectOffset'],calledFrom=self._str_funcCombined)
	    self.b_pointAttach = cgmValid.boolArg(self.d_kws['pointAttach'],calledFrom=self._str_funcCombined)
	    
	    self.f_offset = cgmValid.valueArg(self.d_kws['f_offset'], calledFrom=self._str_funcCombined)
	    #Get info ============================================================================
	    self.d_closestInfo = distance.returnClosestPointOnSurfaceInfo(self.mi_obj.mNode,self.mi_targetSurface.mNode)
	    
	    #Running Lists ============================================================================
	    self.md_return = {}
	    
	def _create(self):
	    #>> Quick links ============================================================================ 
	    d_closestInfo = self.d_closestInfo
	    
	    if self.b_attachControlLoc or not self.b_createControlLoc:
		try:#>>> Follicle ============================================================================	    
		    l_follicleInfo = nodes.createFollicleOnMesh(self.mi_targetSurface.mNode)
		    mi_follicleAttachTrans = cgmMeta.asMeta(l_follicleInfo[1],'cgmObject',setClass=True)
		    mi_follicleAttachShape = cgmMeta.asMeta(l_follicleInfo[0],'cgmNode')	    
		    
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
		except Exception,error:raise StandardError,"!Attach Follicle! | %s"%(error)
	    
	    if not self.b_createControlLoc:#If we don't have a control loc setup, we're just attaching to the surface
		try:#Groups =======================================================================================
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
			#mc.pointConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)
			#mc.orientConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)  
			if self.b_pointAttach:
			    mc.pointConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)
			else:
			    mc.parentConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)
			
		except Exception,error:raise StandardError,"!Groups - no control Loc setup! | %s"%(error)
		
		
	    else:#Setup control loc stuff
		try:#>>> Follicle ============================================================================
		    l_follicleInfo = nodes.createFollicleOnMesh(self.mi_targetSurface.mNode)
		    mi_follicleFollowTrans = cgmMeta.asMeta(l_follicleInfo[1],'cgmObject',setClass=True)
		    mi_follicleFollowShape = cgmMeta.asMeta(l_follicleInfo[0],'cgmNode')
		    
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
		    
		except Exception,error:raise StandardError,"!Follicle - attach Loc setup! | %s"%(error)
		    
		mi_offsetGroup = self.mi_obj.duplicateTransform()
		mi_offsetGroup.doStore('cgmName',self.mi_obj.mNode)
		mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		mi_offsetGroup.doName()
		mi_offsetGroup.parent = mi_followGroup
		self.mi_offsetGroup = mi_offsetGroup 
		self.md_return["offsetGroup"] = mi_offsetGroup
		
		if self.b_attachControlLoc:mi_follicleFollowTrans.connectChildNode(mi_offsetGroup,"followOffsetGroup","follicle")
	
		mi_zeroGroup = cgmMeta.asMeta( mi_offsetGroup.doGroup(True),'cgmObject',setClass=True)	 
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
		
		if self.b_attachControlLoc:
		    mi_group = cgmMeta.asMeta( mi_controlLoc.doGroup(),'cgmObject',setClass=True )
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
		#mc.pointConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)
		#mc.orientConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)    
		
		if self.b_pointAttach:
		    mc.pointConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)
		else:
		    mc.parentConstraint(self.mi_driverLoc.mNode, self.mi_obj.mNode, maintainOffset = True)
		    
		if self.b_attachControlLoc:
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
	    
	    if self.md_return.get("follicleFollow"):
		mi_follicleFollowTrans.connectChild(mi_driverLoc,"driverLoc","follicle")
				
	    return self.md_return
	
    return fncWrap(*args,**kws).go()


def create_radialCurveLoft(*args,**kws):
    """
    Function to create a surface from a curve.
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
	    self._str_funcName = 'create_radialCurveLoft'
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'crvToLoft',"default":None,
	                                  'help':"Curve which will be lofted"},
	                                 {'kw':'aimPointObject',"default":None,
	                                  'help':"Point object from which to loft"},
	                                 {'kw':'f_offset',"default":-.5,
	                                  'help':"Width of this new surface"},
	                                 ]
	    self.__dataBind__(*args,**kws)
	    self.l_funcSteps = [{'step':'Validate','call':self._validate},
		                {'step':'Create','call':self._create}
	                        ]
	    
	    #=================================================================
		
	def _validate(self):
	    #>> validate ============================================================================
	    self.mi_crv = cgmMeta.validateObjArg(self.d_kws['crvToLoft'],cgmMeta.cgmObject,noneValid=False,mayaType = ['nurbsCurve'])
	    try:self.mi_target = cgmMeta.validateObjArg(self.d_kws['aimPointObject'],cgmMeta.cgmObject,noneValid=False)
	    except:
		cgmValid.valueArg
	    #self._str_funcCombined = self._str_funcCombined + "(%s,%s)"%(self.mi_obj.p_nameShort,self.mi_targetSurface.p_nameShort)	    
	    self.f_offset = cgmValid.valueArg(self.d_kws['f_offset'], calledFrom=self._str_funcCombined)
	    self.d_info = {'l_eps':self.mi_crv.getComponents('ep'),
	                   'l_cvs':self.mi_crv.getComponents('cv'),
	                   'l_constraints':[],
	                   'ml_locators':[],
	                   'l_locPos':[]}
	    
	    #Running Lists ============================================================================
	    self.md_return = {}
	    
	def _create(self):
	    #Get our 
	    l_eps = self.d_info['l_eps']
	    l_cvs = self.d_info['l_cvs']	
	    int_cvCount = len(l_cvs)
	    #l_locs = locators.locMeCVsOnCurve(self.mi_crv.mNode)
	    self.progressBar_setMaxStepValue(int_cvCount)
	    
	    for i,cv in enumerate(l_cvs):
		try:#Loc loop
		    self.progressBar_iter(status = cv, step = i)
		    #create it
		    v_pos = p = mc.pointPosition(cv)
		    str_loc = mc.spaceLocator()[0]
		    mi_loc = cgmMeta.cgmObject(str_loc)
		    mi_loc.translate = v_pos
		    #self.d_info['ml_locators'].append(mi_loc)
		    #aim it
		    self.d_info['l_constraints'].append( mc.aimConstraint(self.mi_target.mNode,str_loc,maintainOffset = False,
			                                                  weight = 1, aimVector = [0,0,-1], upVector = [0,1,0],
			                                                  worldUpVector = [0,1,0], worldUpType = 'scene')[0])
		    #move
		    mc.move(0,0,self.f_offset, str_loc, r = True, os = True)
		    
		    #Get pos
		    self.d_info['l_locPos'].append(mi_loc.getPosition())
		    mi_loc.delete()
		    
		except Exception,error:
		    raise StandardError,"Loc creation %s | %s"%(cv,error)
		
	    #create new rail crv
	    str_newRailCrv = mc.curve(d = 2,p = self.d_info['l_locPos'], os = True)
	    mc.rebuildCurve (str_newRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_cvCount + 2, d=3, tol=0.001)[0]
	    
	    str_rebuiltCastCrv = mc.rebuildCurve (self.mi_crv.mNode, ch=0, rpo= 0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_cvCount + 2, d=3, tol=0.001)[0]

	    #create profile crv
	    str_profileCrv = mc.curve(d = 1,p = [mc.pointPosition(self.d_info['l_eps'][0]),self.d_info['l_locPos'][0]], os = True)
	    
	    str_surf = mc.singleProfileBirailSurface(str_profileCrv,str_rebuiltCastCrv,str_newRailCrv,ch=0)[0]
	    
	    #Delete
	    mc.delete(str_newRailCrv,str_profileCrv,str_rebuiltCastCrv)

	    return cgmMeta.cgmObject(str_surf)
	
    return fncWrap(*args,**kws).go()

