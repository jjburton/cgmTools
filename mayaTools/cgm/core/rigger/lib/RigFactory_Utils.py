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
import time
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.classes import SnapFactory as Snap

from cgm.core.lib import nameTools
from cgm.core.classes import NodeFactory as NodeF

#>>> Eyeball
#===================================================================
class RigFactoryFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
	"""
	"""
	try:
	    if not issubclass(type(args[0]),go):
		raise StandardError,"Not a RigFactory.go instance: '%s'"%args[0]
	    assert mc.objExists(args[0]._mi_module.mNode),"Module no longer exists"
	except Exception,error:raise StandardError,"RigFactoryFunc fail | %s"%error
	
	super(RigFactoryFunc, self).__init__(*args, **kws)
	self._str_funcName = 'RigFactoryFunc(%s)'%args[0]._mi_module.p_nameShort	
	
	self._l_ARGS_KWS_DEFAULTS = [{'kw':'goInstance',"default":None}]
	self.__dataBind__(*args,**kws)	
	
	goInstance = self.d_kws['goInstance']		
	self.mi_go = goInstance
	self.mi_module = goInstance._mi_module
	self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
	
	#=================================================================
	
    def _getData(self):
	"""
	"""
	self.report()  
	
def testFunc(*args,**kws):
    class fncWrap(RigFactoryFunc):
	def __init__(self,*args,**kws):
	    """
	    """    
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'testFunc(%s)'%args[0]._mi_module.p_nameShort	
	    
	    self._l_ARGS_KWS_DEFAULTS.extend([{'kw':'cat',"default":None}])
	    self.__dataBind__(*args,**kws)	
	    
    return fncWrap(*args,**kws).go()
