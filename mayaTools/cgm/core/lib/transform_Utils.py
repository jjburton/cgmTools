"""
------------------------------------------
GuiFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class based ui builder for cgmTools
================================================================
"""

#>>> From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
import copy

#>>> From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

#>>> From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid

from cgm.lib import (search,
                     lists,
                     attributes,
                     guiFactory,
                     deformers,
                     dictionary)

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================
_d_KWARG_mTransform = {'kw':'mTransform', "default":None, 'help':"This must be a transform", "argType":"Transform"}

class TransformFunction(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
	"""
	"""
	super(TransformFunction, self).__init__(self,*args,**kws)	
	self._str_funcName = 'TransformFunction'	
	self._l_ARGS_KWS_DEFAULTS = [{'kw':'mTransform', "default":None, 'help':"This is your RigFactory go instance", "argType":"RigFactory.go"},
	                             ]
	self.__dataBind__(*args, **kws)
	
	try:
	    try:mi_transform = kws['mTransform']
	    except:
		try:mi_transform = args[0]
		except:raise StandardError,"No kw or arg transform found'"
	    try:mi_transform.mNode
	    except:mi_transform = r9Meta.MetaClass(mi_transform)
	except Exception,error:raise Exception,"TransformFunction failed to initialize | %s"%error
	
	self._mi_transform = mi_transform
	self._b_ExceptionInterupt = True
	
def getDeformers2(*args,**kws):
    class fncWrap(TransformFunction):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = "getDeformers('%s')"%self._mi_puppet.cgmName
	    self._l_ARGS_KWS_DEFAULTS = [_d_KWARG_mTransform,
	                                 {'kw':'deformerTypes', "default":['all'], 'help':"kinds of deformers you'd like to get", "argType":"RigFactory.go"}
	                                 ]
					 
	    self.__dataBind__(*args,**kws)
	    raise NotImplementedError, "Not sure this is needed"
	    #=================================================================
	    
	def __func__(self):
	    """
	    """
	    return deformers.returnObjectDeformers(self._mi_transform.mNode,self.d_kws['deformerTypes'])
    return fncWrap(*args,**kws).go()

def get_deformers(self,deformerTypes = 'all'):
    """
    
    """	
    try:_str_funcName = "{0}.get_deformers()".format(self.p_nameShort)
    except:_str_funcName = "get_deformers()"
    
    try:
	return deformers.returnObjectDeformers(self.mNode,deformerTypes)
    except StandardError,error:
	log.error("Self: {0}".format(self))
	log.error("deformerTypes: {0}".format(deformerTypes))	
	raise StandardError, "{0} fail | error: {1}"(_str_funcName,error)
    
def isSkinned(self):
    """
    
    """	
    try:_str_funcName = "{0}.isSkinned()".format(self.p_nameShort)
    except:_str_funcName = "isSkinned()"
    
    try:
	if get_deformers(self,'skinCluster'):
	    return True
	return False
    except StandardError,error:
	log.error("Self: {0}".format(self))
	log.error("deformerTypes: {0}".format(deformerTypes))	
	raise StandardError, "{0} fail | error: {1}"(_str_funcName,error)
    
