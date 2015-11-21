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
def returnSplitCurveList(*args, **kws):
    """
    Function to split a curve up u positionally 
    
    @kws
    Arg 0 | kw 'curve'(None)  -- Curve to split
    Arg 1 | kw 'points'(3)  -- Number of points to generate positions for
    Arg 2 | kw 'markPoints'(False)  -- If you want the positions marked with locators
    Arg 3 | kw 'startSplitFactor'(None)  -- inset factor for subsequent splits after then ends
    Arg 4 | kw 'insetSplitFactor'(None)  -- Multiplier for pushing splits one way or another on a curve
    Arg 5 | kw 'rebuildForSplit'(True)  -- Whether to rebuild before split (for smoother splitting)
    Arg 6 | kw 'rebuildSpans'(10)  -- How many spans for the rebuild
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    """
	    """	
	    super(fncWrap, self).__init__(curve = None)
	    self._str_funcName = 'returnSplitCurveList'	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'curve',"default":None,
	                                  'help':"Curve to split"},
	                                 {'kw':'points',"default":3,
	                                  'help':"Number of points to generate positions for"},
	                                 {'kw':'markPoints',"default":False,
	                                  'help':"If you want the positions marked with locators"},
	                                 {'kw':'startSplitFactor',"default":None,
	                                  'help':"inset factor for subsequent splits after then ends"},
	                                 {'kw':'insetSplitFactor',"default":None,
	                                  'help':"Multiplier for pushing splits one way or another on a curve"},
	                                 {'kw':'rebuildForSplit',"default":True,
	                                  'help':"Whether to rebuild before split (for smoother splitting)"},
	                                 {'kw':'minU',"default":None,
	                                  'help':"Minimum U value to use to start splitting"},
	                                 {'kw':'maxU',"default":None,
	                                  'help':"Maximum U value to use to start splitting"},
	                                 {'kw':'reverseCurve',"default":False,
	                                  'help':"Reverse the curve before split"},	                                 
	                                 {'kw':'rebuildSpans',"default":10,
	                                  'help':"How many spans for the rebuild"}]	    
	    self.__dataBind__(*args, **kws)
	    
	def __func__(self):
	    """
	    """
	    _str_funcName = self._str_funcCombined
	    curve = self.d_kws['curve']
	    points = self.d_kws['points']
	    mi_crv = cgmMeta.validateObjArg(self.d_kws['curve'],cgmMeta.cgmObject,mayaType='nurbsCurve',noneValid=False)
	    int_points = cgmValid.valueArg(self.d_kws['points'],minValue=1,calledFrom = _str_funcName)
	    f_insetSplitFactor = cgmValid.valueArg(self.d_kws['insetSplitFactor'],calledFrom = _str_funcName)	
	    f_startSplitFactor = cgmValid.valueArg(self.d_kws['startSplitFactor'],calledFrom = _str_funcName)		
	    f_kwMinU = cgmValid.valueArg(self.d_kws['minU'], noneValid=True, calledFrom = _str_funcName)	
	    f_kwMaxU = cgmValid.valueArg(self.d_kws['maxU'], noneValid=True, calledFrom = _str_funcName)	    
	    f_points = float(int_points)
	    int_spans = int(cgmValid.valueArg(self.d_kws['points'],minValue=5,autoClamp=True,calledFrom = _str_funcName))
	    b_rebuild = cgmValid.boolArg(self.d_kws['rebuildForSplit'],calledFrom = _str_funcName)
	    b_markPoints = cgmValid.boolArg(self.d_kws['markPoints'],calledFrom = _str_funcName)
	    b_reverseCurve = cgmValid.boolArg(self.d_kws['reverseCurve'],calledFrom = _str_funcName)
	    
	    try:#>>> Rebuild curve
		if b_rebuild:
		    useCurve = mc.rebuildCurve (curve, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_spans, d=3, tol=0.001)[0]
		else:
		    useCurve = mc.duplicate(curve)[0]
		    
		if b_reverseCurve:
		    useCurve = mc.reverseCurve(useCurve,rpo = True)[0]
	    except Exception,error:raise StandardError,"Rebuild fail | %s"%error
	    
	    try:#>>> Divide stuff
		#==========================	
		l_spanUPositions = []
		str_bufferU = mc.ls("%s.u[*]"%useCurve)[0]
		log.debug("%s >> u list : %s"%(_str_funcName,str_bufferU))       
		f_maxU = float(str_bufferU.split(':')[-1].split(']')[0])
		l_uValues = [0]
		
		if points == 1:
		    l_uValues = [f_maxU/2]
		elif f_startSplitFactor is not False:
		    if points < 5:
			raise StandardError,"Need at least 5 points for startSplitFactor. Points : %s"%(points)
		    log.debug("%s >> f_startSplitFactor : %s"%(_str_funcName,f_startSplitFactor))  
		    #Figure out our u's
		    f_base = f_startSplitFactor * f_maxU 
		    l_uValues.append( f_base )
		    f_len = f_maxU - (f_base *2)	
		    int_toMake = f_points-4
		    f_factor = f_len/(int_toMake+1)
		    log.debug("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
		    log.debug("%s >> f_len : %s"%(_str_funcName,f_len)) 	
		    log.debug("%s >> int_toMake : %s"%(_str_funcName,int_toMake)) 						
		    log.debug("%s >> f_base : %s"%(_str_funcName,f_base)) 			
		    log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
		    for i in range(1,int_points-3):
			l_uValues.append(((i*f_factor + f_base)))
		    l_uValues.append(f_maxU - f_base)
		    l_uValues.append(f_maxU)
		    log.debug("%s >> l_uValues : %s"%(_str_funcName,l_uValues))  	
		    
		elif f_insetSplitFactor is not False:
		    log.debug("%s >> f_insetSplitFactor : %s"%(_str_funcName,f_insetSplitFactor))  
		    #Figure out our u's
		    f_base = f_insetSplitFactor * f_maxU 
		    f_len = f_maxU - (f_base *2)	
		    f_factor = f_len/(f_points-1)
		    log.debug("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
		    log.debug("%s >> f_len : %s"%(_str_funcName,f_len)) 			
		    log.debug("%s >> f_base : %s"%(_str_funcName,f_base)) 			
		    log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
		    for i in range(1,int_points-1):
			l_uValues.append((i*f_factor))
		    l_uValues.append(f_maxU)
		    log.debug("%s >> l_uValues : %s"%(_str_funcName,l_uValues))  			
		elif f_kwMinU is not False or f_kwMaxU is not False:
		    log.debug("%s >> Sub mode. "%(_str_funcName))
		    if f_kwMinU is not False:
			if f_kwMinU > f_maxU:
			    raise StandardError, "kw minU value(%s) cannot be greater than maxU(%s)"%(f_kwMinU,f_maxU)
			f_useMinU = f_kwMinU
		    else:f_useMinU = 0.0
		    if f_kwMaxU is not False:
			if f_kwMaxU > f_maxU:
			    raise StandardError, "kw maxU value(%s) cannot be greater than maxU(%s)"%(f_kwMaxU,f_maxU)	
			f_useMaxU = f_kwMaxU
		    else:f_useMaxU = f_maxU
		    
		    if int_points == 1:
			l_uValues = [(f_useMaxU - f_useMinU)/2]
		    elif int_points == 2:
			l_uValues = [f_useMaxU,f_useMinU]		    
		    else:
			l_uValues = [f_useMinU]
			f_factor = (f_useMaxU - f_useMinU)/(f_points-1)
			log.debug("%s >> f_maxU : %s"%(_str_funcName,f_useMaxU)) 
			log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
			for i in range(1,int_points-1):
			    l_uValues.append((i*f_factor) + f_useMinU)
			l_uValues.append(f_useMaxU)
		else:
		    #Figure out our u's
		    log.debug("%s >> Regular mode. Points = %s "%(_str_funcName,int_points))
		    if int_points == 3:
			l_uValues.append(f_maxU/2)
			l_uValues.append(f_maxU)
		    else:
			f_factor = f_maxU/(f_points-1)
			log.debug("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
			log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
			for i in range(1,int_points-1):
			    l_uValues.append(i*f_factor)
			l_uValues.append(f_maxU)
		    log.debug("%s >> l_uValues : %s"%(_str_funcName,l_uValues))  
	    except Exception,error:raise StandardError,"Divide fail | %s"%error
    
	    for u in l_uValues:
		try:l_spanUPositions.append(mc.pointPosition("%s.u[%f]"%(useCurve,u)))
		except StandardError,error:raise StandardError,"Failed on pointPositioning: %s"%u			
	    log.debug("%s >> l_spanUPositions | len: %s | list: %s"%(_str_funcName,len(l_spanUPositions),l_spanUPositions))  
    
	    try:
		if b_markPoints:
		    ml_built = []
		    for i,pos in enumerate(l_spanUPositions):
			buffer =  mc.spaceLocator(n = "%s_u_%f"%(useCurve,(l_uValues[i])))[0] 
			ml_built.append( cgmMeta.cgmObject(buffer))
			log.debug("%s >> created : %s | at: %s"%(_str_funcName,ml_built[-1].p_nameShort,pos))              											
			mc.xform(ml_built[-1].mNode, t = (pos[0],pos[1],pos[2]), ws=True)
		    
		    if len(ml_built)>1:
			try:f_distance = distance.returnAverageDistanceBetweenObjects([o.mNode for o in ml_built]) * .5
			except StandardError,error:raise StandardError,"Average distance fail. Objects: %s| error: %s"%([o.mNode for o in ml_built],error)
			try:
			    for o in ml_built:
				o.scale = [f_distance,f_distance,f_distance]
			except StandardError,error:raise StandardError,"Scale fail : %s"%error
	    except StandardError,error:log.error("Mark points fail. error : %s"%(error))
	    mc.delete(useCurve)#Delete our use curve
	    return l_spanUPositions
		
    return fncWrap(*args, **kws).go()
'''
def returnSplitCurveList(curve = None,points = 3, markPoints = False, startSplitFactor = None, insetSplitFactor = None,
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
    log.debug(">>> %s >> "%_str_funcName + "="*75)   
    try:
	mi_crv = cgmMeta.validateObjArg(curve,cgmMeta.cgmObject,mayaType='nurbsCurve',noneValid=False)
	int_points = cgmValid.valueArg(points,minValue=3,calledFrom=_str_funcName)
	f_insetSplitFactor = cgmValid.valueArg(insetSplitFactor,calledFrom=_str_funcName)	
	f_startSplitFactor = cgmValid.valueArg(startSplitFactor,calledFrom=_str_funcName)		

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
	log.debug("%s >> u list : %s"%(_str_funcName,str_bufferU))       
	f_maxU = float(str_bufferU.split(':')[-1].split(']')[0])
	l_uValues = [0]

	if f_startSplitFactor is not False:
	    if points < 5:
		raise StandardError,"%s >> Need at least 5 points for startSplitFactor. Points : %s"%(_str_funcName,points)
	    log.debug("%s >> f_startSplitFactor : %s"%(_str_funcName,f_startSplitFactor))  
	    #Figure out our u's
	    f_base = f_startSplitFactor * f_maxU 
	    l_uValues.append( f_base )
	    f_len = f_maxU - (f_base *2)	
	    int_toMake = f_points-4
	    f_factor = f_len/(int_toMake+1)
	    log.debug("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
	    log.debug("%s >> f_len : %s"%(_str_funcName,f_len)) 	
	    log.debug("%s >> int_toMake : %s"%(_str_funcName,int_toMake)) 						
	    log.debug("%s >> f_base : %s"%(_str_funcName,f_base)) 			
	    log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
	    for i in range(1,int_points-3):
		l_uValues.append(((i*f_factor + f_base)))
	    l_uValues.append(f_maxU - f_base)
	    l_uValues.append(f_maxU)
	    log.debug("%s >> l_uValues : %s"%(_str_funcName,l_uValues))  			
	elif f_insetSplitFactor is not False:
	    log.debug("%s >> f_insetSplitFactor : %s"%(_str_funcName,f_insetSplitFactor))  
	    #Figure out our u's
	    f_base = f_insetSplitFactor * f_maxU 
	    f_len = f_maxU - (f_base *2)	
	    f_factor = f_len/(f_points-1)
	    log.debug("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
	    log.debug("%s >> f_len : %s"%(_str_funcName,f_len)) 			
	    log.debug("%s >> f_base : %s"%(_str_funcName,f_base)) 			
	    log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
	    for i in range(1,int_points-1):
		l_uValues.append((i*f_factor))
	    l_uValues.append(f_maxU)
	    log.debug("%s >> l_uValues : %s"%(_str_funcName,l_uValues))  			
	else:
	    #Figure out our u's
	    log.debug("%s >> Regular mode. Points = %s "%(_str_funcName,int_points))
	    if int_points == 3:
		l_uValues.append(f_maxU/2)
		l_uValues.append(f_maxU)
	    else:
		f_factor = f_maxU/(f_points-1)
		log.debug("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
		log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
		for i in range(1,int_points-1):
		    l_uValues.append(i*f_factor)
		l_uValues.append(f_maxU)
	    log.debug("%s >> l_uValues : %s"%(_str_funcName,l_uValues))  

	for u in l_uValues:
	    try:l_spanUPositions.append(mc.pointPosition("%s.u[%f]"%(useCurve,u)))
	    except StandardError,error:raise StandardError,"failed on pointPositioning: %s"%u			
	log.debug("%s >> l_spanUPositions | len: %s | list: %s"%(_str_funcName,len(l_spanUPositions),l_spanUPositions))  

	try:
	    if b_markPoints:
		ml_built = []
		for i,pos in enumerate(l_spanUPositions):
		    buffer =  mc.spaceLocator(n = "%s_u_%f"%(useCurve,(l_uValues[i])))[0] 
		    ml_built.append( cgmMeta.cgmObject(buffer))
		    log.debug("%s >> created : %s | at: %s"%(_str_funcName,ml_built[-1].p_nameShort,pos))              											
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
'''
'''
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
'''
def attachObjToCurve(*args, **kws):
    """
    Function to see if a curve is an ep curve
    @kws
    baseCurve -- curve on check
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    """
	    """	
	    super(fncWrap, self).__init__(curve = None)
	    self._str_funcName = 'attachObjToCurve'	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'obj',"default":None},
	                                 {'kw':'crv',"default":None}]	    
	    self.__dataBind__(*args, **kws)
	    #=================================================================
    
	def __func__(self):
	    """
	    """
	    obj = cgmValid.objString(self.d_kws['obj'],isTransform=True)
	    crv = cgmValid.objString(self.d_kws['crv'],mayaType='nurbsCurve')	
	    d_returnBuff = distance.returnNearestPointOnCurveInfo(obj,crv)
	    mi_poci = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
	    mc.connectAttr("%s.worldSpace"%d_returnBuff['shape'],"%s.inputCurve"%mi_poci.mNode)
	    mi_poci.parameter = d_returnBuff['parameter']
	    mc.connectAttr("%s.position"%mi_poci.mNode,"%s.t"%obj)
	    mi_poci.doStore('cgmName',obj)
	    mi_poci.doName()
	    
	    return True
    return fncWrap(*args, **kws).go()

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


def isEP(*args, **kws):
    """
    Function to see if a curve is an ep curve
    @kws
    baseCurve -- curve on check
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    """
	    """	
	    super(fncWrap, self).__init__(curve = None)
	    self._str_funcName = 'isEP'	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'curve',"default":None},
	                                 {'kw':'reportTimes',"default":False}]	    
	    self.__dataBind__(*args, **kws)
	    #=================================================================
	    #log.info(">"*3 + " Log Level: %s "%log.getEffectiveLevel())	
    
	def __func__(self):
	    """
	    """
	    self.mi_crv = cgmMeta.validateObjArg(self.d_kws['curve'],mayaType='nurbsCurve',noneValid=False)
	    self._str_funcCombined = self._str_funcCombined + "(%s)"%self.mi_crv.p_nameShort
	    l_cvs = self.mi_crv.getComponents('cv')	    	    
	    if len(l_cvs)-len(self.mi_crv.getComponents('ep')) < 2:
		return True
	    else: return False	     
    return fncWrap(*args, **kws).go()

def getMidPoint(*args, **kws):
    """
    Function to see if a curve is an ep curve
    @kws
    baseCurve -- curve on check
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    """
	    """	
	    super(fncWrap, self).__init__(curve = None)
	    self._str_funcName = 'getMidPoint'	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'curve',"default":None}]	    
	    self.__dataBind__(*args, **kws)
	    #=================================================================
	    #log.info(">"*3 + " Log Level: %s "%log.getEffectiveLevel())	
    
	def __func__(self):
	    """
	    """
	    self.mi_crv = cgmMeta.validateObjArg(self.d_kws['curve'],mayaType='nurbsCurve',noneValid=False)
	    self._str_funcCombined = self._str_funcCombined + "('%s')"%self.mi_crv.p_nameShort
	    
	    try:self.str_bufferU = mc.ls("{0}{1}".format(self.mi_crv.mNode,".u[*]"))[0]
	    except Exception,error:raise Exception,"ls fail | error: {0}".format(error)
	    self.f_maxU = float(self.str_bufferU.split(':')[-1].split(']')[0])	
	    
	    return mc.pointPosition("%s.u[%f]"%(self.mi_crv.mNode,self.f_maxU/2), w=True)
    return fncWrap(*args, **kws).go()

def getPercentPointOnCurve(*args, **kws):
    """
    Function to find a factored point on a maxU curve length
    @kws
    baseCurve -- curve on check
    factor -- value on that curve
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    """
	    """	
	    super(fncWrap, self).__init__(curve = None)
	    self._str_funcName = 'getPercentPointOnCurve'	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'curve',"default":None},
	                                 {'kw':'factor',"default":.1}]	    
	    self.__dataBind__(*args, **kws)
	    #=================================================================
	    #log.info(">"*3 + " Log Level: %s "%log.getEffectiveLevel())	
    
	def __func__(self):
	    """
	    """	    
	    self.f_factor = cgmValid.valueArg(self.d_kws['factor'],minValue=0,maxValue=1.0)
	    self.mi_crv = cgmMeta.validateObjArg(self.d_kws['curve'],mayaType='nurbsCurve',noneValid=False)
	    #self._str_funcCombined = self._str_funcCombined + "('{0}')".format(self.mi_crv.p_nameShort)	    
	    try:self.str_bufferU = mc.ls("{0}{1}".format(self.mi_crv.mNode,".u[*]"))[0]
	    except Exception,error:raise Exception,"ls fail | error: {0}".format(error)
	    self.f_maxU = float(self.str_bufferU.split(':')[-1].split(']')[0])	
	    
	    return mc.pointPosition("%s.u[%f]"%(self.mi_crv.mNode,self.f_maxU*self.f_factor), w=True)
    return fncWrap(*args, **kws).go()
    
def convertCurve(*args, **kws):
    """
    Function to convert a curve
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
	    self._str_funcName = 'convertCurve'	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'baseCurve',"default":None},
	                                 {'kw':'arg',"default":'ep'},
	                                 {'kw':"keepOriginal","default":True}]	    
	    self.__dataBind__(*args, **kws)
	    #=================================================================
	    #log.info(">"*3 + " Log Level: %s "%log.getEffectiveLevel())	
    
	def __func__(self):
	    """
	    """
	    self.mi_baseCurve = cgmMeta.validateObjArg(self.d_kws['baseCurve'],mayaType='nurbsCurve',noneValid=False)
	    self._str_funcCombined = self._str_funcCombined + "(%s)"%self.mi_baseCurve.p_nameShort
	    
	    self.str_arg = cgmValid.stringArg(self.d_kws['arg'],noneValid=True)
	    self.b_keepOriginal = cgmValid.boolArg(self.d_kws['keepOriginal'], calledFrom=self._str_funcCombined)
	    
	    if isEP(self.mi_baseCurve):
		log.warning("%s %s already an ep curve"%(self._str_reportStart,self.mi_baseCurve.p_nameShort))
		return False
	    
	    mi_crv = self.mi_baseCurve
	    if self.str_arg.lower() == 'ep':
		l_pos = []
		for cv in mi_crv.getComponents('cv'):
		    locatorName = locators.locMeObject(cv)
		    pos = distance.returnClosestUPosition(locatorName,mi_crv.mNode)
		    mc.delete(locatorName)
		    l_pos.append( pos )	
		if not self.b_keepOriginal:mi_crv.delete()
		return mc.curve(d = 2,ep = l_pos, os = True)
		#return curves.curveFromPosList(l_pos)
	    raise NotImplementedError,"arg: %s"%self.str_arg
	
    return fncWrap(*args, **kws).go()

def mirrorCurve(*args, **kws):
    """
    Function to mirror a curve or push mirror settings to a second curve
    if a second curve is specified
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
	    self._str_funcName = 'mirrorCurve'
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'baseCurve',"default":None},
	                                 {'kw':'targetCurve',"default":None},
	                                 {'kw':"mirrorThreshold","default":.5},
	                                 {'kw':"mirrorAcross","default":'x'},
	                                 {'kw':"blendBias","default":.5},
	                                 {'kw':"reportTimes","default":False}]	    
	    self.__dataBind__(*args, **kws)
	    self.l_funcSteps = [{'step':'Validate','call':self._validate},
		                {'step':'Create','call':self._create}]	
	    #=================================================================
    
	def _validate(self):
	    """
	    Validate the args, get our data
	    """
	    self.mi_baseCurve = cgmMeta.validateObjArg(self.d_kws['baseCurve'],mayaType='nurbsCurve',noneValid=False)
	    self.mi_targetCurve = cgmMeta.validateObjArg(self.d_kws['targetCurve'],mayaType='nurbsCurve',noneValid=True)
	    self.f_threshold = cgmValid.valueArg(self.d_kws['mirrorThreshold'],calledFrom = self._str_funcCombined)
	    
	    self.str_mirrorAcross = cgmValid.stringArg(self.d_kws['mirrorAcross'],noneValid=True)
	    self.int_across = 0#This is the index to check -- ie pos[0] for x
	    if self.str_mirrorAcross.lower() != 'x':
		raise NotImplementedError, "Only implmeneted x mirror so far | kw: %s"%self.str_mirrorAcross
    
	def _create(self):
	    mi_base = self.mi_baseCurve
	    mi_target = self.mi_targetCurve
	    
	    self.l_baseCvPos = []
	    self.d_base = self.getCurveMirrorData(mi_base)
	    
	    if not mi_target:#if no target, mirror self
		if not self.d_base['b_oneSided']:
		    if self.d_base['b_even']:
			log.info("%s Even mirror"%self._str_reportStart)			
			l_cvPos = self.d_base['l_cvPos']
			l_cvs = self.d_base['l_cvs']			
			int_split = int(len(l_cvPos)/2)
			log.info(int_split)
			l_splitDriven = l_cvs[int_split:]
			l_splitDriver = l_cvs[:int_split]
			l_splitDriverPos = l_cvPos[:int_split]			
			l_splitDriverPos.reverse()
			log.info("%s l_splitDriven: %s"%(self._str_reportStart,l_splitDriven))
			log.info("%s l_splitDriver: %s"%(self._str_reportStart,l_splitDriver))			
			for i,cv in enumerate(l_splitDriven):
			    pos = l_splitDriverPos[i]
			    mc.move(-pos[0],pos[1],pos[2], cv, ws=True)
			return True
		    else:
			log.info("%s nonEven mirror"%self._str_reportStart)			
			l_cvPos = self.d_base['l_cvPos']
			l_cvs = self.d_base['l_cvs']			
			int_split = int(len(l_cvPos)/2)
			l_cvPos.pop(int_split)
			l_cvs.pop(int_split)
			l_splitDriven = l_cvs[int_split:]
			l_splitDriver = l_cvs[:int_split]
			l_splitDriverPos = l_cvPos[:int_split]			
			l_splitDriverPos.reverse()
			log.info("%s l_splitDriven: %s"%(self._str_reportStart,l_splitDriven))
			log.info("%s l_splitDriver: %s"%(self._str_reportStart,l_splitDriver))			
			for i,cv in enumerate(l_splitDriven):
			    pos = l_splitDriverPos[i]
			    mc.move(-pos[0],pos[1],pos[2], cv, ws=True)
			return True		
		else:#it's one sided
		    log.info("%s Build other side. New crv"%self._str_reportStart)
		    l_epPos = self.d_base['l_epPos']
		    l_otherSide = copy.copy(l_epPos)
		    l_otherSide.reverse()
		    for i,pos in enumerate(l_otherSide):
			l_otherSide[i] = [-pos[0],pos[1],pos[2]]
			
		    #l_newCurvePos = l_epPos + l_otherSide
		    l_newCurvePos = l_otherSide
		    l_newCurvePos = lists.returnListNoDuplicates(l_newCurvePos)
		    
		    self.mi_created = cgmMeta.cgmObject( mc.curve(d=2,p=l_newCurvePos,os = True) )
		    self.mi_created.rename( mi_base.p_nameBase + '_mirrored')
		    
		    #
		    if self.d_base['b_startInThreshold'] or self.d_base['b_endInThreshold']:
			#In this case we need to combine and rebuild the curve
			try:
			    str_attachedCurves  = mc.attachCurve([self.mi_created.mNode,self.mi_baseCurve.mNode],
			                                         blendBias = self.d_kws['blendBias'])
			except Exception,error:raise StandardError,"Attach curve | %s"%error
			#mc.delete(self.mi_created.mNode)#delete the old one
			#self.mi_created = cgmMeta.cgmObject(str_attachedCurves[0])
			#int_spans = (len(l_epPos)*1.5)
			int_spans = len(l_epPos)+1			
			try:
			    mc.rebuildCurve (self.mi_created.mNode, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_spans, d=3, tol=0.001)
			except Exception,error:raise StandardError,"Rebuild curve | %s"%error
			try:
			    mc.reverseCurve (self.mi_created.mNode, rpo=1)
			except Exception,error:raise StandardError,"Reverse curve | %s"%error			
		    self.mi_created.rename( mi_base.p_nameBase + '_mirrored')
		    return self.mi_created.p_nameShort
		    
		#See if we need to make new curve to have stuff to mirror
	    else:#if we have a target
		self.d_target = self.getCurveMirrorData(mi_target)
		l_cvsBase = self.d_base['l_cvs']			
		l_cvsTarget = self.d_target['l_cvs']
		if len(l_cvsBase) != len(l_cvsTarget):
		    raise NotImplementedError,"Haven't added ability to do curves of differing cv lengths yet"
		for i,pos in enumerate(self.d_base['l_cvPos']):
		    mc.move(-pos[0],pos[1],pos[2], l_cvsTarget[i], ws=True)
		    
		return True
		    
	def getCurveMirrorData(self,mi_crv):
	    d_return = {}
	    d_return['f_bbMin'] = mi_crv.boundingBoxMin[self.int_across]
	    d_return['f_bbMax'] = mi_crv.boundingBoxMax[self.int_across]
	    d_return['b_oneSided'] = False
	    d_return['b_balanced'] = False
	    d_return['b_weighted'] = None	    
	    	    
	    #> First see our push direction ----------------------------------------------------------
	    try:
		if cgmMath.isFloatEquivalent( d_return['f_bbMax'], d_return['f_bbMin']):
		    d_return['b_balanced'] = 1
		    
		if d_return['f_bbMax'] > d_return['f_bbMin']:
		    d_return['b_weighted'] = 1
		elif d_return['f_bbMax'] < d_return['f_bbMin']:
		    d_return['b_weighted'] = -1
	    except Exception,error:raise StandardError,"Push direction check | %s"%error

	    #> Check thresholds ----------------------------------------------------------------------
	    try:
		if -d_return['f_bbMin'] <= self.f_threshold and d_return['f_bbMax'] >= self.f_threshold or d_return['f_bbMin'] <= -self.f_threshold and d_return['f_bbMax'] <= -self.f_threshold:
		    d_return['b_oneSided'] = True		
		"""if abs(d_return['f_bbMin']) <= self.f_threshold or abs(d_return['f_bbMax']) <= self.f_threshold:
		    d_return['b_oneSided'] = True"""
	    except Exception,error:raise StandardError,"Threshholds check | %s"%error
	
	    #> Is ep --------------------------------------------------------------------
	    try:
		d_return['b_epState'] = isEP(mi_crv)
	    except Exception,error:raise StandardError,"ep check | %s"%error
	    
	    #> Get positions -------------------------------------------------------------------------
	    try:
		l_cvs = mi_crv.getComponents('cv')	    	    		
		l_cvPos = []
		l_epPos = []
		if d_return['b_epState']:
		    for ep in  mi_crv.getComponents('ep'):
			pos = mc.pointPosition(ep,w=True)
			l_epPos.append( pos )	
		    for cv in l_cvs:
			l_cvPos.append( mc.pointPosition(cv,w=True) )	
		else:
		    for cv in l_cvs:
			l_cvPos.append( mc.pointPosition(cv,w=True) )	 
			#Get an ep value
			locatorName = locators.locMeObject(cv)
			pos = distance.returnClosestUPosition(locatorName,mi_crv.mNode)
			mc.delete(locatorName)
			l_epPos.append( pos )	 
			
		d_return['l_cvPos'] = l_cvPos
		d_return['l_epPos'] = l_epPos	    
		d_return['l_cvs'] = l_cvs
	    except Exception,error:raise StandardError,"Get positions | %s"%error
	     
	    #> Is even --------------------------------------------------------------------
	    try:
		if len(l_cvs)%2==0:#even
		    d_return['b_even'] = True
		else: d_return['b_even'] = False
	    except Exception,error:"Even check | %s"%error
	    
	    #> Which end is bigger
	    try:
		if abs(l_cvPos[0][self.int_across]) <= self.f_threshold:
		    d_return['b_startInThreshold'] = True
		else:d_return['b_startInThreshold'] = False
		if abs(l_cvPos[-1][self.int_across]) <= self.f_threshold:
		    d_return['b_endInThreshold'] = True
		else:d_return['b_endInThreshold'] = False
	    except Exception,error:raise StandardError,"End check | %s"%error
	    
	    return d_return
	
    return fncWrap(*args, **kws).go()
