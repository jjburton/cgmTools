"""
------------------------------------------
cgm_Meta: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is the Core of the MetaNode implementation of the systems.
It is uses Mark Jackson (Red 9)'s as a base.
================================================================
"""
import maya.cmds as mc
import maya.mel as mel
import copy
import time
import inspect
import sys

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.lib import search
from cgm.core import cgm_General as cgmGeneral
reload(cgmGeneral)

# Shared Defaults ========================================================

#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmMeta - MetaClass factory for figuring out what to do with what's passed to it
#=========================================================================    
#Values ==================================================================
def ut_isFloatEquivalent():
    assert isFloatEquivalent(-4.11241646134e-07,0.0),"sc>0.0 fail"
    assert isFloatEquivalent(-4.11241646134e-07,0.00001),"sc>0.00001 fail"
    assert isFloatEquivalent(-4.11241646134e-07,-0.0),"sc>0.00001 fail"
    assert isFloatEquivalent(0.0,-0.0),"0.0>-0.0 fail"
    assert isFloatEquivalent(0.0,0),"0.0>0 fail"
    return True

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
    log.debug("f1_rounded: %s"%f1_rounded)
    log.debug("f2_rounded: %s"%f2_rounded)    
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

#>>> Basics ============================================================== 
def stringArg(arg = None,noneValid = True,calledFrom = None):
    """
    Simple string validation
    """
    log.debug(">>> stringArg >> arg = %s"%arg + "="*75) 
    if calledFrom: _str_funcName = "%s.stringArg(%s)"%(calledFrom,arg)    
    else:_str_funcName = "stringArg(%s)"%arg       
    if type(arg) in [str,unicode]:
	return arg
    elif noneValid:
	return None
    else: raise StandardError, ">>> stringArg >> Arg failed: arg = %s | type: %s"%(arg,type(arg))

def stringListArg(l_args = None, noneValid = False, calledFrom = None):
    log.debug(">>> stringArg >> l_args = %s"%l_args + "="*75) 
    calledFrom = stringArg(calledFrom,noneValid=True)    
    if calledFrom: _str_funcName = "%s.stringArg"%(calledFrom)
    else:_str_funcName = "objStringList"    
    t_start = time.clock()
    try:
	if type(l_args) not in [list,tuple]:l_args = [l_args]
	returnList = []
	for arg in l_args:
	    buffer = stringArg(arg,noneValid,calledFrom)
	    if buffer:returnList.append(buffer)
	    else:log.warning("%s >> failed: '%s'"%(_str_funcName,arg))
	return returnList
    except StandardError,error:
	log.error("%s >>Failure! l_args: %s "%(_str_funcName,l_args))
	raise StandardError,error 
    
def boolArg(arg = None, calledFrom = None):
    """
    Bool validation
    """
    log.debug(">>> boolArg >> arg = %s"%arg + "="*75)   
    calledFrom = stringArg(calledFrom,noneValid=True)
    if calledFrom: _str_funcName = "%s.boolArg(%s)"%(calledFrom,arg)
    else:_str_funcName = "boolArg(%s)"%arg
    if type(arg) is bool:
	return arg
    elif type(arg) is int and arg in [0,1]:
	return bool(arg)
    else: raise StandardError, ">>> %s >> Arg failed"%(_str_funcName)
	
def objString(arg = None, mayaType = None, noneValid = False, isTransform = None, calledFrom = None):
    """
    validate an objString. Use cgmMeta version for instances
    
    arg -- obj or instance
    mayaType -- maya type to validate to
    noneValid -- whether none is a valid arg
    """
    log.debug(">>> objString >> arg = %s"%arg + "="*75)
    
    calledFrom = stringArg(calledFrom,noneValid=True)
    if calledFrom: _str_funcName = "%s.objString(%s)"%(calledFrom,arg)
    else:_str_funcName = "objString(%s)"%arg
    t_start = time.clock()
    
    if len(mc.ls(arg)) > 1:
	raise StandardError,"More than one object named %s"%arg
    try:
	argType = type(arg)
	if argType in [list,tuple]:#make sure it's not a list
	    if len(arg) ==1:
		arg = arg[0]
	    elif arg == []:
		arg = None
	    else:
		raise StandardError,"%s >>> arg cannot be list or tuple"%_str_funcName	
	if not noneValid:
	    if arg in [None,False]:
		raise StandardError,"%s >>> arg cannot be None"%_str_funcName
	else:
	    if arg in [None,False]:
		if arg not in [None,False]:log.warning("%s >>> arg fail"%_str_funcName)
		return False
			
	if not mc.objExists(arg):
	    if noneValid: return False
	    else:
		raise StandardError,"%s>>> Doesn't exist: '%s'"%(_str_funcName,arg)
			
	if mayaType is not None and len(mayaType):
	    if type(mayaType) not in [tuple,list]:l_mayaTypes = [mayaType]
	    else: l_mayaTypes = mayaType	    
	    str_type = search.returnObjectType(arg)
	    if str_type not in l_mayaTypes:
		if noneValid:
		    log.warning("%s >>> '%s' Not correct mayaType: mayaType: '%s' != currentType: '%s'"%(_str_funcName,arg,str_type,l_mayaTypes))
		    return False
		raise StandardError,"%s >>> '%s' Not correct mayaType: mayaType: '%s' != currentType: '%s'"%(_str_funcName,arg,str_type,l_mayaTypes)			    	
	if isTransform is not None:
	    if isTransform and not mc.ls(arg,type='transform'):
		if noneValid:
		    log.warning("%s >>> '%s' has no transform"%(_str_funcName,arg))		    
		    return False
		raise StandardError,"%s >>> '%s' has no transform"%(_str_funcName,arg)	    	
	return arg
    
    except StandardError,error:
	log.error("%s >>Failure! arg: %s | mayaType: %s"%(_str_funcName,arg,mayaType))
	raise StandardError,error  
    
def objStringList(l_args = None, mayaType = None, noneValid = False,isTransform = None, calledFrom = None):
    log.debug(">>> objStringList >> l_args = %s"%l_args + "="*75) 
    calledFrom = stringArg(calledFrom,noneValid=True)    
    if calledFrom: _str_funcName = "%s.objStringList"%(calledFrom)
    else:_str_funcName = "objStringList"    
    t_start = time.clock()
    try:
	if type(l_args) not in [list,tuple]:l_args = [l_args]
	returnList = []
	for arg in l_args:
	    buffer = objString(arg,mayaType,noneValid,isTransform,calledFrom)
	    if buffer:returnList.append(buffer)
	    else:log.warning("%s >> failed: '%s'"%(_str_funcName,arg))
	return returnList
    except StandardError,error:
	log.error("%s >>Failure! l_args: %s | mayaType: %s"%(_str_funcName,l_args,mayaType))
	raise StandardError,error 

def valueArg(numberToCheck = None,inRange = None, minValue = None, maxValue = None, isValue = None,
             noneValid = True, isEquivalent = None, autoClamp = False, calledFrom = None):
    """
    @Parameters
    numberTocheck -- main number arg
    inRange -- provide a range list to check
    minValue -- 
    maxValue --
    isValue -- 
    isEquivalent
    autoClamp -- try to return a number
    """
    log.debug(">>> valueArg >> numberToCheck = %s"%numberToCheck + "="*75) 
    calledFrom = stringArg(calledFrom,noneValid=True)    
    if calledFrom: _str_funcName = "%s.valueArg"%(calledFrom)
    else:_str_funcName = "valueArg"  
    try:
	if numberToCheck is None:raise Exception,"numberToCheck cannot be none."
	if type(numberToCheck) not in [float,int]:
	    raise ValueError,"%s not a number. Type: %s"%(numberToCheck,type(numberToCheck))
	if inRange is not None:
	    if numberToCheck < min(inRange) or numberToCheck > max(inRange):
		raise ValueError,"{0} is not in range {1}".format(numberToCheck,inRange)
	if type(minValue) in [float,int]:
	    if not numberToCheck >= minValue:
		if autoClamp:
		    return minValue		    
		raise ValueError,"{0} is less than minValue {1}".format(numberToCheck,minValue)
	if type(maxValue) in [float,int]:
	    if not numberToCheck <= maxValue:
		if autoClamp:
		    return maxValue
		raise ValueError,"{0} is more than maxValue {1}".format(numberToCheck,minValue)
	if type(isEquivalent) in [float,int]:
	    if not isFloatEquivalent(isEquivalent,numberToCheck):
		raise ValueError,"{0} is not equivalent {1}".format(numberToCheck,numberToCheck)
	if type(isValue) in [float,int]:
	    if numberToCheck != isValue:
		raise ValueError,"{0} is not the value {1}".format(numberToCheck,isValue)
	return numberToCheck
    except Exception,error:
	if noneValid:
	    return False
	log.error("{0} >>Failure! int: {1} | range: {2} | min: {3} | max: {4} | isValue: {5} | calledFrom: '{6}'".format(_str_funcName,numberToCheck,inRange,minValue,maxValue,isValue,calledFrom))
	raise Exception,error 
    
#>>> Maya orientation ============================================================================
d_rotateOrder = {'xyz':0,
                 'yzx':1,
                 'zxy':2,
                 'xzy':3,
                 'yxz':4,
                 'zyx':5}   
class simpleOrientation():
    """ 
    """
    def __init__(self,arg = None, calledFrom = None):
	calledFrom = stringArg(calledFrom,noneValid=True)
	
	if calledFrom: _str_funcName = "%s.simpleOrientation"%(calledFrom)
	else:_str_funcName = "simpleOrientation"  
	
	log.debug(">>> %s(arg = %s)"%(_str_funcName,arg) + "="*75)
	str_arg = stringArg(arg,noneValid=False,calledFrom = _str_funcName)
	        
        if str_arg.lower() in d_rotateOrder.keys():
            self.str_orientation = str_arg.lower()
	else:
            self.str_orientation = False

	if self.str_orientation is False :
	    log.info("str_orientation: %s"%self.str_orientation)	    
            raise StandardError, ">>> %s(arg = %s) Failed to validate as a simple orientation"%(_str_funcName,arg)
	    
    def asString(self):
	return self.str_orientation
    
    def getAimAxis(self):
	return simpleAxis(self.str_orientation[0])
    def getUpAxis(self):
	return simpleAxis(self.str_orientation[1])
    def getOutAxis(self):
	return simpleAxis(self.str_orientation[2]) 
    def getAimAxisNegative(self):
	return simpleAxis(self.str_orientation[0]+"-")
    def getUpAxisNegative(self):
	return simpleAxis(self.str_orientation[1]+"-")
    def getOutAxisNegative(self):
	return simpleAxis(self.str_orientation[2]+"-")     
    def getRotateOrderIndex(self):
	return d_rotateOrder.get(self.str_orientation)     
    p_string = property(asString)
    p_aim = property(getAimAxis)
    p_up = property(getUpAxis)
    p_out = property(getOutAxis)
    p_ro = property(getRotateOrderIndex)
    p_aimNegative = property(getAimAxisNegative)
    p_upNegative = property(getUpAxisNegative)
    p_outNegative = property(getOutAxisNegative)   
    
#>>> Simple Axis ==========================================================================
l_axisDirectionsByString = ['x+','y+','z+','x-','y-','z-'] #Used for several menus and what not

d_stringToVector = {'x+':[1,0,0],
                      'x-':[-1,0,0],
                      'y+':[0,1,0],
                      'y-':[0,-1,0],
                      'z+':[0,0,1],
                      'z-':[0,0,-1]}

d_vectorToString = {'[1,0,0]':'x+',
                      '[-1,0,0]':'x-',
                      '[0,1,0]':'y+',
                      '[0,-1,0]':'y-',
                      '[0,0,1]':'z+',
                      '[0,0,-1]':'z-'}
d_tupleToString = {'(1, 0, 0)':'x+',
                   '(-1, 0, 0)':'x-',
                   '(0, 1,  0)':'y+',
                   '(0,-1,0)':'y-',
                   '(0, 0, 1)':'z+',
                   '(0, 0, -1)':'z-'}
d_shortAxisToLong = {'x':'x+','y':'y+','z':'z+'}

class simpleAxis():
    """ 
    """
    def __init__(self,arg):
	_str_funcName = "simpleAxis"    
	log.debug(">>> %s(arg = %s)"%(_str_funcName,arg) + "="*75)
	t_start = time.clock()
	
        self.str_axis = None
        self.v_axis = None
        
        if arg in d_shortAxisToLong.keys():
            self.str_axis = d_shortAxisToLong.get(arg) or False
            self.v_axis = d_stringToVector.get(self.str_axis) or False
            
        elif arg in d_stringToVector.keys():
            self.v_axis = d_stringToVector.get(arg) or False
            self.str_axis = arg
        
        elif str(arg) in d_vectorToString.keys():
            self.str_axis = d_vectorToString.get(str(arg)) or False 
            self.v_axis = d_stringToVector.get(self.str_axis) or False
	    
        elif str(arg) in d_tupleToString.keys():
            self.str_axis = d_tupleToString.get(str(arg)) or False 
            self.v_axis = d_stringToVector.get(self.str_axis) or False
            
        elif ' ' in list(str(arg)):
            splitBuffer = str(arg).split(' ')
            newVectorString =  ''.join(splitBuffer)
            self.str_axis = d_vectorToString.get(newVectorString) or False
            self.v_axis = d_stringToVector.get(self.str_axis) or False
	    
	if self.str_axis is False or self.v_axis is False:
	    log.info("v_axis: %s"%self.v_axis)
	    log.info("str_axis: %s"%self.str_axis)	    
            raise StandardError, ">>> %s(arg = %s) Failed to validate as a simple maya axis"%(_str_funcName,arg)
	    
    def asString(self):
	return self.str_axis
    def asVector(self):
	return self.v_axis
    
    p_vector = property(asVector)
    p_string = property(asString)
    


