"""
------------------------------------------
spacePivot_utils: cgm.core.rigger.lib
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

================================================================
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
from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import nameTools
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import distance_utils as DIST
from cgm.lib import curves

def delete():
    """   
    Delete existing spacePivots

    :parameters:
        obj(str) - Should have space pivots on it

    :returns
       MPtjomg
    """ 
    _str_func = 'delete'   


def clear(obj):
    """   
    Clear existing spacePivots

    :parameters:
        obj(str) - Should have space pivots on it

    :returns
       MPtjomg
    """ 
    _str_func = 'clear'    
    mObj = cgmMeta.validateObjArg(obj,'cgmObject',noneValid=False)    
    _res = False
    ml_spacePivots = mObj.msgList_get('spacePivots')
    if ml_spacePivots:
        log.debug("|{0}| >> SpacePivots found...".format(_str_func))    
        mc.delete([mPivot.mNode for mPivot in ml_spacePivots])
        _res = True
    
    for a in mc.listAttr(obj,ud=True) or []:
        if a.startswith('pivot_'):
            log.debug("|{0}| >> Removing attr: {1}".format(_str_func,a))                
            ATTR.delete(mObj.mNode,a)
            _res = True
            
    return True
 
def create(obj,parentTo = False):
    """   
    Create a spacePivot from a given object

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        mSpacePivot(metaList)
    """ 
    _str_func = 'create'
    
    #....inital...
    i_obj = cgmMeta.validateObjArg(obj,cgmMeta.cgmObject,noneValid=False)    
    i_parent = cgmMeta.validateObjArg(parentTo,cgmMeta.cgmObject,noneValid=True)    
    bbSize = DIST.get_bb_size(i_obj.mNode)
    size = max(bbSize)

    #>>>Create #====================================================
    #CURVES.create_controlCurve(i_obj.mNode,'jack')
    i_control = cgmMeta.asMeta(CURVES.create_controlCurve(i_obj.mNode,'jack')[0],'cgmObject',setClass=True)
    log.debug(i_control)
    try:l_color = curves.returnColorsFromCurve(i_obj.mNode)
    except Exception,error:raise Exception,"color | %s"%(error)          
    log.debug("l_color: %s"%l_color)
    curves.setColorByIndex(i_control.mNode,l_color[0])
    
    #>>>Snap and Lock
    #====================================================	
    #Snap.go(i_control,i_obj.mNode,move=True, orient = True)

    #>>>Copy Transform
    #====================================================   
    i_newTransform = i_obj.doCreateAt()

    #Need to move this to default cgmNode stuff
    mBuffer = i_control
    i_newTransform.doCopyNameTagsFromObject(i_control.mNode)
    curves.parentShapeInPlace(i_newTransform.mNode,i_control.mNode)#Parent shape
    i_newTransform.parent = mBuffer.parent#Copy parent
    i_control = i_newTransform
    mc.delete(mBuffer.mNode)
    
    #>>>Register
    #====================================================    
    #Attr
    i = ATTR.get_nextAvailableSequentialAttrIndex(i_obj.mNode,"pivot")
    str_pivotAttr = str("pivot_%s"%i)
    str_objName = str(i_obj.getShortName())
    str_pivotName = str(i_control.getShortName())
    
    #Build the network
    i_obj.addAttr(str_pivotAttr,enumName = 'off:lock:on', defaultValue = 2, value = 0, attrType = 'enum',keyable = False, hidden = False)
    i_control.overrideEnabled = 1
    d_ret = NodeF.argsToNodes("%s.overrideVisibility = if %s.%s > 0"%(str_pivotName,str_objName,str_pivotAttr)).doBuild()
    log.debug(d_ret)
    d_ret = NodeF.argsToNodes("%s.overrideDisplayType = if %s.%s == 2:0 else 2"%(str_pivotName,str_objName,str_pivotAttr)).doBuild()
    
    for shape in mc.listRelatives(i_control.mNode,shapes=True,fullPath=True):
        log.debug(shape)
        mc.connectAttr("%s.overrideVisibility"%i_control.mNode,"%s.overrideVisibility"%shape,force=True)
        mc.connectAttr("%s.overrideDisplayType"%i_control.mNode,"%s.overrideDisplayType"%shape,force=True)
    
    #Vis 
    #>>>Name stuff
    #====================================================
    cgmMeta.cgmAttr(i_control,'visibility',lock=True,hidden=True)   
    i_control = cgmMeta.validateObjArg(i_control,'cgmControl',setClass = True)
    i_control.doStore('cgmName',i_obj)
    i_control.addAttr('cgmType','controlAnim',lock=True)    
    i_control.addAttr('cgmIterator',"%s"%i,lock=True)        
    i_control.addAttr('cgmTypeModifier','spacePivot',lock=True)

    i_control.doName(nameShapes=True)

    i_control.addAttr('cgmAlias',(i_obj.getNameAlias()+'_pivot_%s'%i),lock=False)
    
    #Store on object
    #====================================================    
    i_obj.addAttr("spacePivots", attrType = 'message',lock=True)
    _l_spacePivots = i_obj.getMessage('spacePivots',True) or []
    if i_control.getLongName() not in _l_spacePivots:
        #_l_spacePivots = i_obj.getMessage('spacePivots',True)
        #_l_spacePivots.append(i_control.mNode)
        i_obj.msgList_append('spacePivots',i_control,'controlTarget')
    log.debug("spacePivots: %s"%i_obj.msgList_get('spacePivots',asMeta = True))

    #parent
    if i_parent:
        i_control.parent = i_parent.mNode
        i_constraintGroup = (cgmMeta.asMeta(i_control.doGroup(True),'cgmObject',setClass=True))
        i_constraintGroup.addAttr('cgmTypeModifier','constraint',lock=True)
        i_constraintGroup.doName()
        i_control.connectChildNode(i_constraintGroup,'constraintGroup','groupChild')	

        log.debug("constraintGroup: '%s'"%i_constraintGroup.getShortName())		

    #change to cgmControl
    i_control = cgmMeta.asMeta(i_control.mNode,'cgmControl', setClass=1)

    return i_control

def add(obj, parentTo = False, count = 1, clean = False):
    """   
    Add multiple space pivots to an object

    :parameters:
        obj(str) - Should have space pivots on it
        count(int) - how many to add
        clean(bool) - whether to clean existing pivots off before adding

    :returns
       metaList
    """ 
    _str_func = 'add' 
    
    mObj = cgmMeta.validateObjArg(obj,'cgmObject',noneValid=False)    
    mParent = cgmMeta.validateObjArg(parentTo,'cgmObject',noneValid=True)
    _res = []
    
    if clean:
        clean(obj)
    
    for i in range(count):
        _int = i+1
        log.debug("|{0}| >> adding {1}".format(_str_func,_int))   
        _res.append( create(mObj,mParent) )
        
    return _res
        
    
    
    
    
    