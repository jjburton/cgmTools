"""
Module for building controls for cgmModules

"""
# From Python =============================================================
import copy
import re
import time
import pprint
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.curve_Utils as CURVES
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.lib import rayCaster as RayCast
from cgm.core.rigger.lib import rig_Utils as rUtils
import cgm.core.rigger.lib.spacePivot_utils as SPACEPIVOTS
reload(SPACEPIVOTS)
reload(ATTR)
"""
from cgm.lib import (attributes,
                     cgmMath,
                     locators,
                     modules,
                     distance,
                     dictionary,
                     rigging,
                     search,
                     curves,
                     lists,
                     )"""

from cgm.core.lib import nameTools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
__l_fullFreezeTypes__ = ['cog']
__d_rotateOrderDefaults__ = {'cog':3,#xzy
                             'master':3,
                             'hips':0,#xyz
                             'shoulders':2#zyx,
                             }


def register(controlObject = None,#(mObject - None) -- The object to use as a control
             typeModifier = None,#(string - None) -- Tag for cgmTypeModifier for naming
             copyTransform = None,#(mObject - None) -- Object to copy the transform of for our control object
             copyPivot = None,#(mObject - None) -- Object to copy the pivot of for our control object
             shapeParentTo = None, #'(mObject - None) -- Object to shape parent our control curve to to use that transform
             useShape = None, #'(mObject - None) -- Object to use the curve shape of for our control
             setRotateOrder = None,#'(rotateOrder - None) -- Argument for a rotate order to set
             autoLockNHide = None,#'(bool - None) -- Try to set lock and hide
             mirrorAxis = None,#'(string - None) -- Mirror axis to set - using red9's setup terms
             mirrorSide = None,#'(string/int - None) -- Mirror side - using red9's setup terms
             makeMirrorable = True,#'(bool - True) -- Setup for mirrorability (using red9) -- implied by other mirror args
             addDynParentGroup = False,#'(False) -- Add a dynParent group setup
             addExtraGroups = False,#'(int - False) -- Number of nested extra groups desired
             addConstraintGroup = False,#'(bool - False) -- If a group just above the control is desired for consraining
             freezeAll = False,#'(bool - False) -- Freeze all transforms on the control object
             noFreeze = False,
             addSpacePivots = False,#'(int - False) -- Number of space pivots to generate and connect
             controlType = None,#'(string - None) -- Tag for cgmType
             aim = None,#'(string/int - None) -- aim axis to use
             up = None,#'(string/int - None) -- up axis to use
             out = None,#'(string/int - None) -- out axis to use
             makeAimable = None,#'(mObject - False) -- Make object aimable -- implied by aim/up/out):
             **kws):

    _str_func = 'register'
    """
    [{'step':'validate','call':self._validate},
    {'step':'Copy Transform','call':self._copyTransform},
    {'step':'Shape Parent','call':self._shapeParent},
    {'step':'Copy Pivot','call':self._copyPivot},
    {'step':'Naming','call':self._naming},
    {'step':'Aim Setup','call':self._aimSetup},
    {'step':'Rotate Order','call':self._rotateOrder},
    {'step':'Initial Freeze','call':self._initialFreeze},
    {'step':'Groups Setup','call':self._groupsSetup},
    {'step':'Space Pivot','call':self._spacePivots},
    {'step':'Mirror Setup','call':self._mirrorSetup},	                        
    {'step':'Freeze','call':self._freeze},
    {'step':'Mirror Attribute Bridges','call':self._mirrorAttributeBridges_},	                        
    {'step':'lock N Hide','call':self._lockNHide},
    {'step':'Return build','call':self._returnBuild}]
    """
    try:
        #Validate ================================================================================================
        mi_control = cgmMeta.validateObjArg(controlObject,'cgmControl', setClass=True)
        
        str_mirrorAxis = VALID.stringArg(mirrorAxis,calledFrom = _str_func)
        str_mirrorSide = cgmGeneral.verify_mirrorSideArg(mirrorSide)#VALID.stringArg(mirrorSide,calledFrom = _str_func)
        b_makeMirrorable = VALID.boolArg(makeMirrorable,calledFrom = _str_func)
    
        _addMirrorAttributeBridges = kws.get('addMirrorAttributeBridges',False)
        addForwardBack = kws.get('addForwardBack',False)
        
        if _addMirrorAttributeBridges :
            if type(_addMirrorAttributeBridges ) not in [list,tuple]:
                raise ValueError,"[Bad addMirrorAttributeBridge arg]{arg: %s}"%_addMirrorAttributeBridge 
            for i,l in enumerate(_addMirrorAttributeBridges):
                if type(l) not in [list,tuple]:
                    raise ValueError,"[Bad addMirrorAttributeBridge arg: %s]{arg: %s}"%(i,l) 			
        
        # Running lists ------------------------------------------------------------------------------------------
        ml_groups = []#Holder for groups
        ml_constraintGroups = []
        ml_spacePivots = []
    
        #Copy Transform ================================================================================================
        if copyTransform is not None:
            mTarget = cgmMeta.validateObjArg(copyTransform,'cgmObject',noneValid=True)
            if not mTarget:
                raise StandardError,"Failed to find suitable copyTransform object: '%s"%copyTransform
    
            #Need to move this to default cgmNode stuff
            mBuffer = mi_control
            i_newTransform = cgmMeta.cgmObject( rigging.groupMeObject(mTarget.mNode,False) )
            for a in mc.listAttr(mi_control.mNode, userDefined = True):
                ATTR.copy_to(mi_control.mNode,a,i_newTransform.mNode)
            curves.parentShapeInPlace(i_newTransform.mNode,mi_control.mNode)#Parent shape
            i_newTransform.parent = mi_control.parent#Copy parent
            mi_control = cgmMeta.asMeta(i_newTransform,'cgmControl', setClass=True)
            mc.delete(mBuffer.mNode)    
          
        #ShapeParent ================================================================================================
        if shapeParentTo:
            i_target = cgmMeta.validateObjArg(shapeParentTo,'cgmObject')
            CORERIG.shapeParent_in_place(i_target.mNode,mi_control.mNode)
            i_target = cgmMeta.asMeta(i_target,'cgmControl',setClass = True)
            #mi_control.delete()
            mi_control = i_target#replace the control with the joint    
    
        if useShape is not None:
            i_shape = cgmMeta.validateObjArg(useShape,cgmMeta.cgmObject,mayaType='nurbsCurve')
            curves.parentShapeInPlace(mi_control.mNode,i_shape.mNode)
            
        #Copy Pivot ============================================================================================
        if copyPivot is not None:
            if issubclass(type(copyPivot),cgmMeta.cgmNode):
                i_target = copyPivot
            elif mc.objExists(copyPivot):
                i_target = cgmMeta.cgmObject(copyPivot)
            else:
                raise StandardError,"Failed to find suitable copyTransform object: '%s"%copyPivot
    
            #Need to move this to default cgmNode stuff
            mi_control.doCopyPivot(i_target.mNode)
    
        #Naming ============================================================================================
        mi_control.addAttr('cgmType','controlAnim',lock=True)    
        if typeModifier is not None:
            mi_control.addAttr('cgmTypeModifier',str(typeModifier),lock=True)
        mi_control.doName()#mi_control.doName(nameShapes=True) 
            
            
        #Rotate Order ============================================================================================
        _rotateOrder = False
        if setRotateOrder is not None:
            _rotateOrder = setRotateOrder
        elif controlType in __d_rotateOrderDefaults__.keys():
            _rotateOrder = __d_rotateOrderDefaults__[controlType]
        elif mi_control.getAttr('cgmName') in __d_rotateOrderDefaults__.keys():
            _rotateOrder = __d_rotateOrderDefaults__[mi_control.getAttr('cgmName')]
        else:
            log.debug("|{0}| >> Rotate order not set on: {1}".format(_str_func,mi_control.p_nameShort))  
            
            
        #Set it ---------------------------------------------------------------
        if _rotateOrder:
            mRotateOrder = VALID.simpleOrientation(_rotateOrder)
            #dictionary.validateRotateOrderString(_rotateOrder)
            
            mc.xform(mi_control.mNode, rotateOrder = mRotateOrder.p_string)
            
        #Initial Freeze ============================================================================================
        if freezeAll:
            mc.makeIdentity(mi_control.mNode, apply=True,t=1,r=1,s=1,n=0)    
        
        #Groups ============================================================================================
        if addDynParentGroup or addSpacePivots or mi_control.getAttr('cgmName') == 'cog' or _addMirrorAttributeBridges:
            mi_control.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)
            ATTR.reorder(mi_control.mNode, '________________',top=True )
        #Aim Setup ============================================================================================
        if aim is not None or up is not None or makeAimable:
            mi_control._verifyAimable()  
       
        #First our master group:
        i_masterGroup = (cgmMeta.asMeta(mi_control.doGroup(True), 'cgmObject', setClass=True))
        i_masterGroup.doStore('cgmName',mi_control)
        i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
        i_masterGroup.doName()
        mi_control.connectChildNode(i_masterGroup,'masterGroup','groupChild')
    
        if addDynParentGroup:
            i_dynGroup = (cgmMeta.cgmObject(mi_control.doGroup(True)))
            i_dynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=mi_control,dynGroup=i_dynGroup)
            i_dynGroup.doName()
            """
            i_zeroGroup = (cgmMeta.cgmObject(mi_control.doGroup(True)))
            i_zeroGroup.addAttr('cgmTypeModifier','zero',lock=True)
            i_zeroGroup.doName()
            mi_control.connectChildNode(i_zeroGroup,'zeroGroup','groupChild')"""
    
        if addExtraGroups:
            for i in range(addExtraGroups):
                i_group = (cgmMeta.asMeta(mi_control.doGroup(True),'cgmObject',setClass=True))
                if type(addExtraGroups)==int and addExtraGroups>1:#Add iterator if necessary
                    i_group.addAttr('cgmIterator',str(i+1),lock=True)
                    i_group.doName()
                ml_groups.append(i_group)
            mi_control.msgList_connect("extraGroups",ml_groups,'groupChild')
    
        if addConstraintGroup:#ConstraintGroups
            i_constraintGroup = (cgmMeta.asMeta(mi_control.doGroup(True),'cgmObject',setClass=True))
            i_constraintGroup.addAttr('cgmTypeModifier','constraint',lock=True)
            i_constraintGroup.doName()
            ml_constraintGroups.append(i_constraintGroup)
            mi_control.connectChildNode(i_constraintGroup,'constraintGroup','groupChild')	    	    
        
    
        #Space Pivot ============================================================================================
        if addSpacePivots:
            parent = mi_control.getMessage('masterGroup')[0]
            for i in range(int(addSpacePivots)):
                #i_pivot = rUtils.create_spaceLocatorForObject(mi_control.mNode,parent)
                i_pivot = SPACEPIVOTS.create(mi_control.mNode,parent)
                ml_spacePivots.append(i_pivot)
                #log.info("spacePivot created: {0}".format(i_pivot.p_nameShort))			
    
    
        #Mirror Setup ============================================================================================
        if str_mirrorSide is not None or b_makeMirrorable:
            for mObj in [mi_control] + ml_spacePivots:
                mi_control._verifyMirrorable()
                l_enum = cgmMeta.cgmAttr(mi_control,'mirrorSide').p_enum
                if str_mirrorSide in l_enum:
                    #log.debug("|{0}| >> Rotate order not set on: {1}".format(_str_func,mi_control.p_nameShort))                  
                    #log.debug("%s >> %s >> found in : %s"%(_str_funcCombined, "mirrorSetup", l_enum))		
                    mi_control.mirrorSide = l_enum.index(str_mirrorSide)
                if str_mirrorAxis:
                    mi_control.mirrorAxis = str_mirrorAxis
            for mObj in mi_control.msgList_get('spacePivots'):
                mObj._verifyMirrorable()
                mi_control.doConnectOut('mirrorAxis',mObj.mNode + '.mirrorAxis')
                mi_control.doConnectOut('mirrorSide',mObj.mNode + '.mirrorSide')
                
                #cgmMeta.cgmAttr(mObj,'mirrorSide').doConnectIn(mi_control,'mirrorSide')
                #cgmMeta.cgmAttr(mi_control,'mirrorAxis').doCopyTo(mObj,connectTargetToSource = 1)
                #ATTR.connect(mObj.mNode + '.mirrorAxis',"{0}.mirrorAxis".format(mi_control.mNode))
                #ATTR.connect(mObj.mNode + 'mirrorSide',"{0}.mirrorSide".format(mi_control.mNode))
    
        #Freeze ============================================================================================
        if not shapeParentTo and noFreeze is not True:
            if not freezeAll:
                if mi_control.getAttr('cgmName') == 'cog' or controlType in __l_fullFreezeTypes__:
                    mc.makeIdentity(mi_control.mNode, apply=True,t=1,r=1,s=1,n=0)	
                else:
                    mc.makeIdentity(mi_control.mNode, apply=True,t=1,r=0,s=1,n=0)
            else:
                mc.makeIdentity(mi_control.mNode, apply=True,t=1,r=1,s=1,n=0)    
        
        #Mirror attriubte Bridges ============================================================================================
        if addForwardBack:
            mPlug_forwardBackDriver = cgmMeta.cgmAttr(mi_control,"forwardBack",attrType = 'float',keyable=True)
            try:
                mPlug_forwardBackDriven = cgmMeta.validateAttrArg([mi_control,addForwardBack])['mi_plug']
            except Exception,error:raise StandardError,"push pull driver | %s"%(error)
        
            if str_mirrorSide.lower() == 'right':
                arg_forwardBack = "%s = -%s"%(mPlug_forwardBackDriven.p_combinedShortName,
                                              mPlug_forwardBackDriver.p_combinedShortName)		    
            else:
                arg_forwardBack = "%s = %s"%(mPlug_forwardBackDriven.p_combinedShortName,
                                             mPlug_forwardBackDriver.p_combinedShortName)
        
            mPlug_forwardBackDriven.p_locked = True
            mPlug_forwardBackDriven.p_hidden = True
            mPlug_forwardBackDriven.p_keyable = False		
            NodeF.argsToNodes(arg_forwardBack).doBuild()
        
        if _addMirrorAttributeBridges:
            for l_bridge in _addMirrorAttributeBridges:
                _attrName = VALID.stringArg(l_bridge[0])
                _attrToBridge = VALID.stringArg(l_bridge[1])
                if not mi_control.hasAttr(_attrToBridge):
                    raise StandardError,"['%s' lacks the bridge attr '%s']"%(mi_control.p_nameShort,_attrToBridge)
    
                mPlug_attrBridgeDriver = cgmMeta.cgmAttr(mi_control,_attrName,attrType = 'float',keyable=True)
                try:
                    mPlug_attrBridgeDriven = cgmMeta.validateAttrArg([mi_control,_attrToBridge])['mi_plug']
                except Exception,error:raise StandardError,"[validate control attribute bridge attr]{%s}"%(error)
    
                if str_mirrorSide.lower() == 'right':
                    arg_attributeBridge = "%s = -%s"%(mPlug_attrBridgeDriven.p_combinedShortName,
                                                      mPlug_attrBridgeDriver.p_combinedShortName)		    
                else:
                    arg_attributeBridge = "%s = %s"%(mPlug_attrBridgeDriven.p_combinedShortName,
                                                     mPlug_attrBridgeDriver.p_combinedShortName)
    
                mPlug_attrBridgeDriven.p_locked = True
                mPlug_attrBridgeDriven.p_hidden = True
                mPlug_attrBridgeDriven.p_keyable = False		
                NodeF.argsToNodes(arg_attributeBridge).doBuild()    
        
        #lock N Hide ============================================================================================
        if mi_control.hasAttr('visibility'):
            mi_control.visibility = True
        
        if autoLockNHide:
            if mi_control.hasAttr('cgmTypeModifier'):
                if mi_control.cgmTypeModifier.lower() == 'fk':
                    ATTR.set_standardFlags(mi_control.mNode,attrs=['tx','ty','tz','sx','sy','sz'])
            if mi_control.cgmName.lower() == 'cog':
                ATTR.set_standardFlags(mi_control.mNode,attrs=['sx','sy','sz'])
            cgmMeta.cgmAttr(mi_control,'visibility',lock=True,hidden=True)
            
        if mi_control.hasAttr('cgmIterator'):
            ATTR.set_standardFlags(mi_control.mNode,attrs=['cgmIterator'])
        
        str_base = mi_control.p_nameBase
        for i,mShape in enumerate(mi_control.getShapes(asMeta=True)):
            mShape.rename("{0}_shape_{1}".format(str_base,i))
            #mShape.doName()
        
        #return ============================================================================================
        #pprint.pprint(vars())
        
        return {'mObj':mi_control,'instance':mi_control,'ml_groups':ml_groups,'ml_constraintGroups':ml_constraintGroups}	
    except Exception,err: cgmGeneral.cgmExceptCB(Exception,err)

