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

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral

#>>> Utilities
#===================================================================
class rigStep(cgmGeneral.cgmFuncCls):
    def __init__(self,goInstance = None,**kws):
	"""
	"""	
	super(rigStep, self).__init__(self,**kws)
	try:
	    assert goInstance._cgmClass == 'RigFactory.go'
	except StandardError,error:
	    raise StandardError,"Not a RigFactory.go : %s"%error	
	
	self._str_funcName = 'moduleStep(%s)'%goInstance._strShortName	
	self.__dataBind__(**kws)
	self.d_kwsDefined = {'goInstance':goInstance}
	self._go = goInstance
	self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	#=================================================================
	
    def _getData(self):
	"""
	"""
	goInstance = self.d_kwsDefined['goInstance']
	self.report()
	
class example(rigStep):
    def __init__(self,goInstance = None, **kws):
	"""
	"""	
	super(example, self).__init__(goInstance,**kws)
	
	self._str_funcName = 'example(%s)'%self.d_kwsDefined['goInstance']._strShortName	
	self.__dataBind__(**kws)
	self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	#=================================================================	

    def _getData(self):
	"""
	"""
	goInstance = self.d_kwsDefined['goInstance']
	self.report()
	
def exampleWrap(goInstance = None):
    class example(rigStep):
	def __init__(self,goInstance = None):
	    """
	    """	
	    super(example, self).__init__(goInstance)
	    self._str_funcName = 'example(%s)'%self.d_kwsDefined['goInstance']._strShortName	
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	    #The idea is to register the functions needed to be called
	    #=================================================================	    
    
	def _getData(self):
	    """
	    """
	    goInstance = self.d_kwsDefined['goInstance']
	    self.report()
	    
    #We wrap it so that it autoruns and returns
    return example(goInstance).go()