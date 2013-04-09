"""
------------------------------------------
cgm_General: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class for general cgmMeta Stuff
================================================================
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
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (lists,
                     search,
                     attributes)
reload(search)

def validateObjArg(arg = None,mType = None, noneValid = False, default_mType = cgmMeta.cgmNode):
    """
    validate an objArg to be able to get instance of the object
    
    arg -- obj or instance
    mType -- if not None, make sure instance is this type
    noneValid -- whether none is a valid arg
    default_mType -- type to intialize as for default
    """
    
    try:
	argType = type(arg)
	if argType in [list,tuple]:#make sure it's not a list
	    raise StandardError,"validateObjArg>>> arg cannot be list or tuple: %s"%arg	
	if not noneValid:
	    if arg in [None,False]:
		raise StandardError,"validateObjArg>>> arg cannot be None"
	else:
	    if arg in [None,False]:return True
	
	if issubclass(argType,r9Meta.MetaClass):#we have an instance already
	    i_arg = arg
	elif not mc.objExists(arg):
	    raise StandardError,"validateObjArg>>> Doesn't exist: %s"%arg	
	elif mType is not None:
	    i_autoInstance = r9Meta.MetaClass(arg)
	    if issubclass(type(i_autoInstance),mType):
		return i_autoInstance
	    elif i_autoInstance.hasAttr('mClass') and i_autoInstance.mClass != str(mType).split('.')[-1]:
		raise StandardError,"validateObjArg>>> Not correct mType: mType:%s != %s"%(type(i_autoInstance),mType)	
	    log.info("validateObjArg>>> Initializing as mType: %s"%mType)	
	    i_arg =  mType(arg)
	else:
	    log.info("validateObjArg>>> Initializing as defaultType: %s"%default_mType)
	    i_arg = default_mType(arg)
	
	return i_arg
    except StandardError,error:
	log.error("validateObjArg>>Failure! arg: %s | mType: %s"%(arg,mType))
	raise StandardError,error

def unittest_validateObjArg():
    i_node = cgmMeta.cgmNode(nodeType='transform')
    i_obj = cgmMeta.cgmObject(nodeType='transform')
    null = mc.group()
    
    try:validateObjArg()
    except:log.info("Empty arg should have failed and did")
    
    assert i_obj == validateObjArg(i_obj.mNode),"string arg failed"
    log.info("String arg passed!")
    assert i_obj == validateObjArg(i_obj),"instance arg failed"
    log.info("instance arg passed!")
    
    i_returnObj = validateObjArg(i_obj.mNode,cgmMeta.cgmObject)
    assert issubclass(type(i_returnObj),cgmMeta.cgmObject),"String + mType arg failed!"
    log.info("String + mType arg failed!")
    
    assert i_obj == validateObjArg(i_obj,cgmMeta.cgmObject),"Instance + mType arg failed!"
    log.info("Instance + mType arg failed!")
    
    try:validateObjArg(i_node.mNode,cgmMeta.cgmObject)
    except:log.info("Validate cgmNode as cgmObject should have failed and did")
    
    assert issubclass(type(validateObjArg(null)),cgmMeta.cgmNode),"Null string failed!"
    log.info("Null string passed!")
    
    i_null = validateObjArg(null,cgmMeta.cgmObject)
    assert issubclass(type(i_null),cgmMeta.cgmObject),"Null as cgmObject failed!"
    log.info("Null as cgmObjectpassed!")
    
    
    i_null.delete()
    i_node.delete()
    i_obj.delete()


def validateAttrArg(arg,defaultType = 'float',**kws):
    """
    Validate an attr arg to usable info
    Arg should be sting 'obj.attr' or ['obj','attr'] format.

    """
    try:
	if type(arg) in [list,tuple] and len(arg) == 2:
	    obj = arg[0]
	    attr = arg[1]
	    combined = "%s.%s"%(arg[0],arg[1])
	elif '.' in arg:
	    obj = arg.split('.')[0]
	    attr = '.'.join(arg.split('.')[1:])
	    combined = arg
	else:
	    raise StandardError,"validateAttrArg>>>Bad attr arg: %s"%arg
	
	if not mc.objExists(obj):
	    raise StandardError,"validateAttrArg>>>obj doesn't exist: %s"%obj
	    
	if not mc.objExists(combined):
	    log.info("validateAttrArg>>> '%s'doesn't exist, creating attr!"%combined)
	    i_plug = cgmMeta.cgmAttr(obj,attr,attrType=defaultType,**kws)
	else:
	    i_plug = cgmMeta.cgmAttr(obj,attr,**kws)	    
	
	return {'obj':obj ,'attr':attr ,'combined':combined,'mi_plug':i_plug}
    except StandardError,error:
	log.error("validateAttrArg>>Failure! arg: %s"%arg)
	raise StandardError,error
