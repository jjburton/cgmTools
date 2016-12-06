"""
control_utils
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

from cgm.lib import attributes
from cgm.core.lib import attribute_utils as coreAttr

#>>> Utilities
#===================================================================
def set_primeScaleAxis(control = None, primeAxis = None, slaveOthers = False, alias = None):
    """
    Set a single axis of scale for a given control. The other channels are locked and hidden.
    
    :parameters:
        control(str): Object to change
        primeAxis(str/idx): X,Y,Z or index
        slaveOthers(bool): Whether to drive the remaining attributes of the given channel
        alias(str): If given, will attempt to alias the primeAxis

    :returns
        success(bool)
    """   
    _str_func = 'set_primeAxis'
    _l = ['X','Y','Z']
    _primeAxis = cgmValid.kw_fromList(primeAxis, _l)
    _idx = _l.index(_primeAxis)
    _attr_prime = 'scale{0}'.format(_primeAxis)
    
    _l_others = []
    for i,v in enumerate(_l):
        if i != _idx:
            _l_others.append(v)
    
    log.debug("{0} || control:{1}".format(_str_func,control))    
    log.debug("{0} || primeAxis:{1}".format(_str_func,_primeAxis))
    log.debug("{0} || slaveOthers:{1}".format(_str_func,slaveOthers))
    log.debug("{0} || alias:{1}".format(_str_func,alias))
    log.debug("{0} || prime attr:{1}".format(_str_func,_attr_prime))
    log.debug("{0} || other attrs:{1}".format(_str_func,_l_others))
        
    if alias:
        coreAttr.alias_set("{0}.{1}".format(control,_attr_prime),alias)
            
    for attr in _l_others:
        if slaveOthers:
            try:attributes.doConnectAttr("{0}.{1}".format(control,_attr_prime),
                                         "{0}.scale{1}".format(control,attr.capitalize()),
                                         transferConnection=True)
            except:pass
        attributes.doSetLockHideKeyableAttr(control, lock = True, visible= False, keyable=False, channels=['s{0}'.format(attr.lower())])
           
    return True

    