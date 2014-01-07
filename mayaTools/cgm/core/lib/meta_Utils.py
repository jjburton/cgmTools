"""
meta Utils
Josh Burton 
www.cgmonks.com

For use with meta instance data
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

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.lib import modules
#>>> Utilities
#===================================================================
def sort_listToDictByAttrs(ml_toSort = None,l_attrsToCheck = None):
    """
    Function to sort a a list of meta instances by a list of attributes. For example:
    list of [mObj1, mObj2] and attrs of ['cgmDirection','cgmName'].
    
    @kws
    ml_toSort -- meta list of cgmNodes
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,ml_toSort = None,l_attrsToCheck = None, **kws):
	    """
	    """	
	    super(fncWrap, self).__init__(curve = None)
	    self._b_WIP =True
	    self._str_funcName = 'sort_listToDictByAttrs'	
	    self.__dataBind__(**kws)
	    self.d_kws = {'ml_toSort':ml_toSort,
	                         'l_attrsToCheck':l_attrsToCheck}
	    #=================================================================
    
	def __func__(self):
	    """
	    """
	    self.d_return = {}
	    ml_toSort = self.d_kws['ml_toSort']
	    ml_toCull = copy.copy(ml_toSort)
	    self.l_attrsToCheck = cgmValid.stringListArg( self.d_kws['l_attrsToCheck'],True,self._str_funcCombined)
	    self.d_objAttrs = {}
	    self.d_objAttrKeys = {}
	    self.d_matchObjects = {}
	    self.d_keys = {}
	    for i,mObj in enumerate(ml_toSort):
		self.d_objAttrs[i] = {}
		self.d_objAttrKeys[i] = []
		activeDict = {}		
		try:
		    l_validTags = []
		    for ii,attr in enumerate(self.l_attrsToCheck):
			if attr not in self.d_keys.keys():
			    self.d_keys[attr] = []
			buffer = mObj.getAttr(attr)
			if buffer:
			    l_validTags.append(attr)
			    self.d_objAttrKeys[i].append(buffer)
			    self.d_objAttrs[i][attr] = buffer
			    if buffer not in  self.d_matchObjects.keys():
				self.d_matchObjects[buffer] = []
			    self.d_matchObjects[buffer].append(mObj)
			    if buffer not in self.d_keys[attr]:self.d_keys[attr].append(buffer)

		except Exception,error:
		    log.error("%s faild: %s"%(self._str_reportStart,error))
		
		    
	    #Build our dict --------------------------------------------------------------------
	    l_keys = []
	    for i,idx in enumerate(self.d_objAttrKeys.keys()):
		activeBuffer = False
		l_valueKeys = self.d_objAttrKeys.get(idx)
		for ii,value in enumerate(l_valueKeys):
		    if ii == 0 and value != l_valueKeys[-1] :
			activeBuffer = self.d_return.setdefault(value,{})
		    elif value == l_valueKeys[-1]:
			activeBuffer = self.d_return.setdefault(value,[])
		    else:
			activeBuffer = activeBuffer.setdefault(value,{})
			
		
		    if type(activeBuffer) is list:
			activeBuffer.append(ml_toSort[i])
		     

	    self.d_buffer = self.d_return
	    self.report()
	    return self.d_return
    return fncWrap(ml_toSort,l_attrsToCheck).go()


def get_matchedListFromAttrDict(*args,**kws):
    """
    Function to search t a a list of meta instances by a dict of attributes/values. 
    
    @args
    objects to search
    
    @kws
    attr kws
    
    Example ussage:
    metaUtils.get_matchedListFromAttrDict(m1.rigNull.msgList_get('handleJoints'),cgmDirection = 'left',cgmName = 'brow')
    metaUtils.get_matchedListFromAttrDict(m1.rigNull.msgList_get('handleJoints'),{'cgmDirection':'left','cgmName' : 'uprCheek'})
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'get_matchedListFromAttrDict'	
	    self.__dataBind__(*args,**kws)
	    
	    if len(args)>1:
		self.d_check = args[1]
	    elif 'checkDict' in kws.keys():
		self.d_check = kws.get('checkDict')
	    else:
		d_kws = {}
		for kw in kws:
		    if kw not in self._l_reportMask:
			d_kws[kw] = kws[kw]
		self.d_check = d_kws
	       
	    #=================================================================
	    #log.info(">"*3 + " Log Level: %s "%log.getEffectiveLevel())	
    
	def __func__(self):
	    """
	    """
	    assert type(self.d_check) is dict,"Arg must be dictionary. %s | %s"%(self.d_check,type(self.checkDict))
	    
	    self.ml_return = []
	    ml_toSearch = self._l_funcArgs
	    assert type(self._l_funcArgs) in [list,tuple],"Args must be list. %s | %s"%(type(self._l_funcArgs),self._l_funcArgs)
	    
	    d_check = self.d_check
	    
	    for arg in self._l_funcArgs:
		type_buffer = type(arg)
		if type_buffer in [list,tuple]:
		    l_buffer = arg
		elif type_buffer != dict:
		    l_buffer = [arg]
		else:
		    l_buffer = []
		    
		for mObj in l_buffer:
		    int_matches = 0
		    for key in d_check.keys():
			value = d_check.get(key)			
			try:
			    if mObj.hasAttr(key) and mObj.getAttr(key) == value:
				int_matches +=1
				log.debug("Match: %s | %s"%(mObj.p_nameShort,key))
			except Exception,error:
			    log.error("%s failed: %s | %s | %s | error: %s"%(self._str_reportStart,mObj,key,value,error))
		    if int_matches == len(d_check.keys()):
			self.ml_return.append(mObj) 

	    return self.ml_return
    return fncWrap(*args,**kws).go()

def getSettingsColors(arg = None):
    try:
	return modules.returnSettingsData(('color'+arg.capitalize()),True)
    except:
	return modules.returnSettingsData('colorCenter',True)