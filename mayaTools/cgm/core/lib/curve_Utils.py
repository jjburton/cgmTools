"""
cgmLimb
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


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
from cgm.core.cgmPy import validateArgs as cgmValid
reload(cgmValid)
from cgm.lib import (distance,
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
@cgmGeneral.Timer
def returnSplitCurveList(curve = None,points = 3, markPoints = False,
                         rebuildForSplit = True,rebuildSpans = 10):
	"""
	Splits a curve given a number of points and returns those world space positions.

	@Parameters
	curve -- must be a curve instance or obj string
	points -- number of points you want on the curve
	markPoints(bool) -- whether you want locators at the points. Mainly for testing
	rebuildForSplit(bool) -- whether to 'smooth' the curve
	rebuildSpans(int) -- number of spans on the rebuild

	returns l_pos
	"""
	_str_funcName = 'returnSplitCurveList'
	log.info(">>> %s >> "%_str_funcName + "="*75)   
	try:
		mi_crv = cgmMeta.validateObjArg(curve,cgmMeta.cgmObject,mayaType='nurbsCurve',noneValid=False)
		int_points = cgmValid.valueArg(points,minValue=3,calledFrom=_str_funcName)
		f_points = float(int_points)
		int_spans = int(cgmValid.valueArg(points,minValue=5,autoClamp=True,calledFrom=_str_funcName))
		b_rebuild = cgmValid.boolArg(rebuildForSplit,calledFrom=_str_funcName)
		b_markPoints = cgmValid.boolArg(markPoints,calledFrom=_str_funcName)
		
		#>>> Rebuild curve
		if b_rebuild:
			useCurve = mc.rebuildCurve (curve, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_spans, d=3, tol=0.001)[0]
		else:
			useCurve = curve
	
		#>>> Divide stuff
		#==========================	
		l_spanUPositions = []
		str_bufferU = mc.ls("%s.u[*]"%useCurve)[0]
		log.info("%s >> u list : %s"%(_str_funcName,str_bufferU))       
		f_maxU = float(str_bufferU.split(':')[-1].split(']')[0])
	
		#Figure out our u's
		l_uValues = [0]
		f_factor = f_maxU/(f_points-1)
		log.info("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
		log.info("%s >> f_factor : %s"%(_str_funcName,f_factor))               
		for i in range(1,int_points-1):
			l_uValues.append(i*f_factor)
		l_uValues.append(f_maxU)
		log.info("%s >> l_uValues : %s"%(_str_funcName,l_uValues))  
	
		for u in l_uValues:
			try:l_spanUPositions.append(mc.pointPosition("%s.u[%f]"%(useCurve,u)))
			except StandardError,error:raise StandardError,"failed on pointPositioning: %s"%u			
		log.info("%s >> l_spanUPositions | len: %s | list: %s"%(_str_funcName,len(l_spanUPositions),l_spanUPositions))  
		
		try:
			if b_markPoints:
				ml_built = []
				for i,pos in enumerate(l_spanUPositions):
					buffer =  mc.spaceLocator(n = "%s_u_%f"%(useCurve,(l_uValues[i])))[0] 
					ml_built.append( cgmMeta.cgmObject(buffer))
					log.info("%s >> created : %s | at: %s"%(_str_funcName,ml_built[-1].p_nameShort,pos))              											
					mc.xform(ml_built[-1].mNode, t = (pos[0],pos[1],pos[2]), ws=True)
				
				try:f_distance = distance.returnAverageDistanceBetweenObjects([o.mNode for o in ml_built]) * .5
				except StandardError,error:raise StandardError,"Average distance fail. Objects: %s| error: %s"%([o.mNode for o in ml_built],error)
				try:
					for o in ml_built:
						o.scale = [f_distance,f_distance,f_distance]
				except StandardError,error:raise StandardError,"Scale fail : %s"%error
		except StandardError,error:log.error("%s >>> Mark points fail. error : %s"%(_str_funcName,error))
		if b_rebuild:mc.delete(useCurve)
		return l_spanUPositions
	except StandardError,error:
		raise StandardError,"%s >>> error : %s"%(_str_funcName,error)

@cgmGeneral.Timer
def attachObjToCurve(obj = None, crv = None):
	"""
	@Parameters
	obj -- obj string
	crv -- crv string to attach to

	returns param
	"""
	_str_funcName = 'attachObjToCurve'
	log.info(">>> %s >> "%_str_funcName + "="*75)
	try:
		obj = cgmValid.objString(obj,isTransform=True)
		crv = cgmValid.objString(crv,mayaType='nurbsCurve')	
		d_returnBuff = distance.returnNearestPointOnCurveInfo(obj,crv)
		mi_poci = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
		mc.connectAttr("%s.worldSpace"%d_returnBuff['shape'],"%s.inputCurve"%mi_poci.mNode)
		mi_poci.parameter = d_returnBuff['parameter']
		mc.connectAttr("%s.position"%mi_poci.mNode,"%s.t"%obj)
		mi_poci.doStore('cgmName',obj)
		mi_poci.doName()
		
	except StandardError,error:
		raise StandardError,"%s >>> error : %s"%(_str_funcName,error)	

@cgmGeneral.Timer
def getUParamOnCurve(obj = None, crv = None):
	"""
	Props to Marco Giordano for this method. Oddly, the distance method is faster....

	@Parameters
	curve -- must be a curve instance or obj string
	points -- number of points you want on the curve

	returns param
	"""
	_str_funcName = 'getUParamOnCurve'
	log.info(">>> %s >> "%_str_funcName + "="*75)
	mi_obj = cgmValid.objString(obj)
	mi_crv = cgmValid.objString(crv,mayaType='nurbsCurve')
	mi_shape = cgmMeta.validateObjArg(mc.listRelatives(mi_crv,shapes = True)[0],mayaType='shape')
	pos = mc.xform(mi_obj,q=True, t=True, ws=True)
	point = OpenMaya.MPoint(pos[0],pos[1],pos[2])
	#object.__getattribute__(self, "_MObject")
	curveFN = OpenMaya.MFnNurbsCurve(mi_shape.__getattribute__("_MObject"))
	paramUtil = OpenMaya.MScriptUtil()
	paramPtr = paramUtil.asDoublePtr()
	isOnCurve = curveFN.isPointOnCurve(point)
	if isOnCurve:
		curveFN.getParamAtPoint(point,paramPtr,0.001,OpenMaya.MSpace.kObject)
	else:
		point = curveFN.closestPoint(point,paramPtr,0.001,OpenMaya.MSpace.kObject)
		curveFN.getParamAtPoint(point,paramPtr,0.001,OpenMaya.MSpace.kObject)
		
	buffer = paramPtr
	del(paramPtr)
	return paramUtil.getDouble(buffer)
	