#=================================================================================================================================================
#=================================================================================================================================================
#	cgmMath - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with cgmMath
# 
# ARGUMENTS:
# 	rigging
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
# FUNCTION KEY:
#   1) returnDistanceBetweenPoints (point1, point2)
#   
#=================================================================================================================================================
#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
import math
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_General as cgmGeneral

#=========================================================================
def multiplyLists(lists,allowZeros = True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Muliplies a list of lists

    ARGUMENTS:
    lists(list) - [[2,3,4],[2,3,4],[2,3,4,3]]

    RETURNS:
    number(list) - [8, 27, 64, 3]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    indicesDict = {}
    lenBuffer = []
    for list in lists:
	lenBuffer.append(len(list))
    terms = max(lenBuffer)

    """ collect our values """
    for i in range(terms):
	valueBuffer = []
	for list in lists:
	    if (len(list)) > i:
		if list[i] != 0:
		    valueBuffer.append(list[i])
		elif allowZeros == True:
		    valueBuffer.append(list[i])
		else:
		    valueBuffer.append(1)
	indicesDict[i] = valueBuffer

    returnList = []
    """ multiply """
    for key in indicesDict:
	buffer = indicesDict.get(key)
	returnList.append(multiplyList(buffer))

    return returnList

def multiplyList(listToMultiply):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Muliplies all non zero values in a list

    ARGUMENTS:
    listToMultiply(listToMultiply) - [124,2,0,4]

    RETURNS:
    number(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    return reduce(lambda x,y: x*y, listToMultiply)

def list_subtract(l1,l2):
    """ 
    """
    if len(l1)!=len(l2):
	raise StandardError,"list_subtract>>> lists must be same length! l1: %s | l2: %s"%(l1,l2)
    l_return = []
    for i,x in enumerate(l1):
	l_return.append( x-l2[i])
    return l_return

def list_add(l1,l2):
    """ 
    """
    if len(l1)!=len(l2):
	raise StandardError,"list_subtract>>> lists must be same length! l1: %s | l2: %s"%(l1,l2)
    l_return = []
    for i,x in enumerate(l1):
	l_return.append( x+l2[i])
    return l_return
# ====================================================================================================================
# FUNCTION - 1
# From - http://code.activestate.com/recipes/278258-list-tools/
#
# SIGNATURE:
#	normList(L, normalizeTo=1)
#
# DESCRIPTION:
#   normalize values of a list to make its max = normalizeTo
# 
# ARGUMENTS:
#   L - list to normalize
# 	normalizeTo - the value to normalize to
#
# RETURNS:
#	normalized list
#
# ====================================================================================================================
def normList(L, normalizeTo=1):
    '''normalize values of a list to make its max = normalizeTo'''
    vMax = max(L)
    return [ x/(vMax*1.0)*normalizeTo for x in L]

def normSumList(L, normalizeTo=1.0):
    """normalize values of a list to make sum = normalizeTo
    
    For example [.2, .5] becomes [0.33333333333333331, 0.66666666666666663] for a sum of 1.0
    
    Thanks to:
    http://stackoverflow.com/questions/26785354/normalizing-a-list-of-numbers-in-python
    """
    return [float(i)/normalizeTo for i in [float(i)/sum(L) for i in L]]
# ====================================================================================================================
# FUNCTION - 2
#
# SIGNATURE:
#	divideLength(length, points)
#
# DESCRIPTION:
#   Divide a length into the positions of the number of points input
# 
# ARGUMENTS:
# 	length - 
#   points - the number of points on the length you want
#
# RETURNS:
#	point list
#
# ====================================================================================================================
def divideLength(length, points):
    """
    Pass at length and number of points on that length you want and it will return a list of the postions along that length:
    divideLength(10,5) = [0,2.5,5,7.5,10]
    """
    pointsList = []
    pointsList.append(0)

    #return mid points    
    segmentLength = length/float(points-1)
    cnt = 1
    for p in range (points-2):
	pnt = cnt * segmentLength
	cnt+=1
	pointsList.append(pnt)

    pointsList.append(length)
    return pointsList

def mag(v):
    assert type(v) in [list,tuple],"mag>>> arg must be vector"
    try:
	return math.sqrt(sum(i**2 for i in v))
    except:
	raise StandardError,"mag>>> Failure: %s"%v

def ut_isFloatEquivalent():
    assert isFloatEquivalent(-4.11241646134e-07,0.0),"sc>0.0 fail"
    assert isFloatEquivalent(-4.11241646134e-07,0.00001),"sc>0.00001 fail"
    assert isFloatEquivalent(-4.11241646134e-07,-0.0),"sc>0.00001 fail"
    assert isFloatEquivalent(0.0,-0.0),"0.0>-0.0 fail"
    assert isFloatEquivalent(0.0,0),"0.0>0 fail"

def isFloatEquivalent(f1,f2,places=4):
    """
    Compare two floats, returns if equivalent
    """ 
    #zeroCheck
    l_zeros = [-0.0,0.0]
    zeroState = False

    if round(f1,places) in l_zeros and round(f2,places) in l_zeros:
	log.debug("zero match: %s|%s"%(f1,f2))
	return True

    #reg check
    f1_rounded = round(f1,places)
    f2_rounded = round(f2,places)
    #log.debug(f1_rounded)
    #log.debug(f2_rounded) 
    if f1_rounded == f2_rounded:
	return True
    return False 

def isVectorEquivalent(v1,v2,places=7):
    """
    Compare two vectors, returns if equivalent
    """ 
    if type(v1) not in [list,tuple]:return False
    if type(v2) not in [list,tuple]:return False
    if len(v1)!= len(v2):return False 

    for i,n in enumerate(v1):
	if not isFloatEquivalent(n,v2[i],places):
	    return False
    return True

def returnSplitValueList(*args, **kws):
    """
    Function for parsing up a line of values (like a curve.u list or a surface.uv list  
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    """
	    """	
	    super(fncWrap, self).__init__(curve = None)
	    self._str_funcName = 'returnSplitValueList'	
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'minU',"default":0,
	                                  'help':"Minimum value to use to start splitting"},
	                                 {'kw':'maxU',"default":1,
	                                  'help':"Maximum value to use to start splitting"},
	                                 {'kw':'points',"default":3,
	                                  'help':"Number of points to generate values for"},
	                                 {'kw':'cullStartEnd',"default":False,
	                                  'help':"If you want the start and end culled from the list"},	                                 
	                                 {'kw':'startSplitFactor',"default":None,
	                                  'help':"inset factor for subsequent splits after then ends"},
	                                 {'kw':'insetSplitFactor',"default":None,
	                                  'help':"Multiplier for pushing splits one way or another on a curve"}]	    
	    self.__dataBind__(*args, **kws)

	def __func__(self):
	    """
	    """
	    _str_funcName = self._str_funcCombined
	    points = self.d_kws['points']
	    int_points = cgmValid.valueArg(self.d_kws['points'],minValue=1,calledFrom = _str_funcName)
	    f_insetSplitFactor = cgmValid.valueArg(self.d_kws['insetSplitFactor'],calledFrom = _str_funcName)	
	    f_startSplitFactor = cgmValid.valueArg(self.d_kws['startSplitFactor'],calledFrom = _str_funcName)		
	    f_minU = cgmValid.valueArg(self.d_kws['minU'], noneValid=True, calledFrom = _str_funcName)
	    f_maxU = cgmValid.valueArg(self.d_kws['maxU'], noneValid=True, calledFrom = _str_funcName)    
	    f_points = float(int_points)
	    int_spans = int(cgmValid.valueArg(self.d_kws['points'],minValue=5,autoClamp=True,calledFrom = _str_funcName))
	    b_cullStartEnd = cgmValid.boolArg(self.d_kws['cullStartEnd'], calledFrom = _str_funcName)
	    
	    if f_insetSplitFactor is not False or f_startSplitFactor is not False:
		if not isFloatEquivalent(f_minU,0):
		    raise StandardError,"Min U must be 0 when f_insetSplitFactor or f_startSplitFactor are used"
	    
	    try:#>>> Divide stuff
		#==========================	
		l_spanUPositions = []    
		l_uValues = [f_minU]
	
		if f_startSplitFactor is not False:
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
		    
		    #f_base = (f_maxU - f_minU) * f_insetSplitFactor
		    #f_len = (f_maxU - f_base) - (f_minU + f_base)
		    #f_factor = f_len/(f_points-1)
		    log.debug("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
		    log.debug("%s >> f_base : %s"%(_str_funcName,f_base)) 					    
		    log.debug("%s >> f_len : %s"%(_str_funcName,f_len)) 			
		    log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
		    for i in range(1,int_points-1):
			l_uValues.append(((i*f_factor)+f_base))
		    l_uValues.append(f_maxU)
		    log.debug("%s >> l_uValues : %s"%(_str_funcName,l_uValues))

		else:
		    #Figure out our u's
		    log.debug("%s >> Regular mode. Points = %s "%(_str_funcName,int_points))
		    if int_points == 1:
			l_uValues = [((f_maxU - f_minU)/2)+f_minU]
		    elif int_points == 2:
			l_uValues = [f_minU,f_maxU]
		    elif int_points == 3:
			l_uValues.append(((f_maxU - f_minU)/2)+f_minU)
			l_uValues.append(f_maxU)
		    else:
			f_factor = (f_maxU-f_minU)/(f_points-1)
			log.debug("%s >> f_maxU : %s"%(_str_funcName,f_maxU)) 
			log.debug("%s >> f_factor : %s"%(_str_funcName,f_factor))               
			for i in range(1,int_points-1):
			    l_uValues.append((i*f_factor)+f_minU)
			l_uValues.append(f_maxU)
		    log.debug("%s >> l_uValues : %s"%(_str_funcName,l_uValues))  
		    
		if b_cullStartEnd and len(l_uValues)>3:
		    l_uValues = l_uValues[1:-1]
	    except Exception,error:raise StandardError,"Divide fail | %s"%error
    
	    return l_uValues	    

    return fncWrap(*args, **kws).go()

"""
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
	l_uValues.append(f_useMaxU)"""