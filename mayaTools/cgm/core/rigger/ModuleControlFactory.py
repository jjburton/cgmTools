"""
Module for building controls for cgmModules

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

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.lib import rayCaster as RayCast
from cgm.core.rigger.lib import rig_Utils as rUtils
import cgm.core.rigger.lib.spacePivot_utils as SPACEPIVOTS
#reload(SPACEPIVOTS)
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
                     )

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
def registerControl(*args,**kws):
    """
    Function to register a control and get it ready for the rig

    @kws
    0 - 'controlObject'(mObject - None) -- The object to use as a control
    1 - 'typeModifier'(string - None) -- Tag for cgmTypeModifier for naming
    2 - 'copyTransform'(mObject - None) -- Object to copy the transform of for our control object
    3 - 'copyPivot'(mObject - None) -- Object to copy the pivot of for our control object
    4 - 'shapeParentTo'(mObject - None) -- Object to shape parent our control curve to to use that transform
    5 - 'useShape'(mObject - None) -- Object to use the curve shape of for our control
    6 - 'setRotateOrder'(rotateOrder - None) -- Argument for a rotate order to set
    7 - 'autoLockNHide'(bool - None) -- Try to set lock and hide
    8 - 'mirrorAxis'(string - None) -- Mirror axis to set - using red9's setup terms
    9 - 'mirrorSide'(string/int - None) -- Mirror side - using red9's setup terms
    10 - 'makeMirrorable'(bool - True) -- Setup for mirrorability (using red9) -- implied by other mirror args
    11 - 'addDynParentGroup'(False) -- Add a dynParent group setup
    12 - 'addExtraGroups'(int - False) -- Number of nested extra groups desired
    13 - 'addConstraintGroup'(bool - False) -- If a group just above the control is desired for consraining
    14 - 'freezeAll'(bool - False) -- Freeze all transforms on the control object
    15 - 'addSpacePivots'(int - False) -- Number of space pivots to generate and connect
    16 - 'controlType'(string - None) -- Tag for cgmType
    17 - 'aim'(string/int - None) -- aim axis to use
    18 - 'up'(string/int - None) -- up axis to use
    19 - 'out'(string/int - None) -- out axis to use
    20 - 'makeAimable'(mObject - False) -- Make object aimable -- implied by aim/up/out
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args,**kws):
            """
            """    
            super(fncWrap, self).__init__(*args, **kws)
            if args:self.mi_control = cgmMeta.validateObjArg(args[0],cgmMeta.cgmObject,noneValid=False)
            try:self._str_funcName = "registerControl(%s)"%self.mi_control.p_nameShort  
            except:self._str_funcName = "registerControl"
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'controlObject', "default":None, 'help':"The object to use as a control", "argType":"mObject"},
                                         {'kw':'copyTransform', "default":None, 'help':"Object to copy the transform of for our control object", "argType":"mObject"},
                                         {'kw':'copyPivot', "default":None, 'help':"Object to copy the pivot of for our control object", "argType":"mObject"},
                                         {'kw':'shapeParentTo',"default":None,'help':"Object to shape parent our control curve to to use that transform","argType":"mObject"},
                                         {'kw':'useShape',"default":None,'help':"Object to use the curve shape of for our control","argType":"mObject"},
                                         {'kw':'setRotateOrder',"default":None,'help':"Argument for a rotate order to set","argType":"rotateOrder"},
                                         {'kw':'autoLockNHide',"default":None,'help':"Try to set lock and hide","argType":"bool"},
                                         {'kw':'mirrorAxis',"default":None,'help':"Mirror axis to set - using red9's setup terms","argType":"string"},
                                         {'kw':'mirrorSide',"default":None,'help':"Mirror side - using red9's setup terms","argType":"string/int"},
                                         {'kw':'makeMirrorable',"default":True,'help':"Setup for mirrorability (using red9) -- implied by other mirror args","argType":"bool"},
                                         {'kw':'addDynParentGroup',"default":False,'help':"Add a dynParent group setup"},
                                         {'kw':'addExtraGroups',"default":False,'help':"Number of nested extra groups desired","argType":"int"},
                                         {'kw':'addConstraintGroup',"default":False,'help':"If a group just above the control is desired for consraining","argType":"bool"},
                                         {'kw':'freezeAll',"default":False,'help':"Freeze all transforms on the control object","argType":"bool"},
                                         {'kw':'addSpacePivots',"default":False,'help':"Number of space pivots to generate and connect","argType":"int"},
                                         {'kw':'controlType',"default":None,'help':"Tag for cgmType","argType":"string"},
                                         {'kw':'typeModifier', "default":None, 'help':"Tag for cgmTypeModifier for naming", "argType":"string"},	                                 
                                         {'kw':'addForwardBack',"default":None,'help':"Forward Back driver setup. Looking for an attribute to drive","argType":"mAttr"},	                                 
                                         {'kw':'addMirrorAttributeBridges',"default":None,'help':"Attribute to drive the same channel on mirrored objects. Looking for an nested list [[attrName,attr],...]","argType":"nested list"},	                                 	                                 
                                         {'kw':'aim',"default":None,'help':"aim axis to use","argType":"string/int"},
                                         {'kw':'up',"default":None,'help':"up axis to use","argType":"string/int"},
                                         {'kw':'out',"default":None,'help':"out axis to use","argType":"string/int"},
                                         {'kw':'makeAimable',"default":False,'help':"Make object aimable -- implied by aim/up/out","argType":"mObject"},]

            self.__dataBind__(*args,**kws)	
            #=================================================================
            self.l_funcSteps = [{'step':'validate','call':self._validate},
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

        def _validate(self):
            assert type(self.d_kws['addExtraGroups']) in [int,bool]
            assert type(self.d_kws['addSpacePivots']) in [int,bool]

            i_obj = self.mi_control
            self.mi_control = cgmMeta.asMeta(i_obj,'cgmControl', setClass=True)

            self.str_mirrorAxis = VALID.stringArg(self.d_kws['mirrorAxis'],calledFrom = self._str_funcCombined)
            self.str_mirrorSide = VALID.stringArg(self.d_kws['mirrorSide'],calledFrom = self._str_funcCombined)
            self.b_makeMirrorable = VALID.boolArg(self.d_kws['makeMirrorable'],calledFrom = self._str_funcCombined)

            self._addMirrorAttributeBridges = self.d_kws.get('addMirrorAttributeBridges') or False
            if self._addMirrorAttributeBridges :
                if type(self._addMirrorAttributeBridges ) not in [list,tuple]:raise StandardError,"[Bad addMirrorAttributeBridge arg]{arg: %s}"%self._addMirrorAttributeBridge 
                for i,l in enumerate(self._addMirrorAttributeBridges):
                    if type(l) not in [list,tuple]:raise StandardError,"[Bad addMirrorAttributeBridge arg: %s]{arg: %s}"%(i,l) 			
            # Running lists ------------------------------------------------------------------------------------------
            self.ml_groups = []#Holder for groups
            self.ml_constraintGroups = []
            self.ml_spacePivots = []

        def _copyTransform(self):		    
            copyTransform = self.d_kws['copyTransform']
            if copyTransform is not None:
                if issubclass(type(copyTransform),cgmMeta.cgmNode):
                    i_target = copyTransform
                elif mc.objExists(copyTransform):
                    i_target = cgmMeta.cgmObject(copyTransform)
                else:
                    raise StandardError,"Failed to find suitable copyTransform object: '%s"%copyTransform

                #Need to move this to default cgmNode stuff
                mBuffer = self.mi_control
                i_newTransform = cgmMeta.cgmObject( rigging.groupMeObject(i_target.mNode,False) )
                for a in mc.listAttr(self.mi_control.mNode, userDefined = True):
                    attributes.doCopyAttr(self.mi_control.mNode,a,i_newTransform.mNode)
                curves.parentShapeInPlace(i_newTransform.mNode,self.mi_control.mNode)#Parent shape
                i_newTransform.parent = self.mi_control.parent#Copy parent
                self.mi_control = cgmMeta.asMeta(i_newTransform,'cgmControl', setClass=True)
                mc.delete(mBuffer.mNode)

        def _shapeParent(self):		    
            shapeParentTo = self.d_kws['shapeParentTo']
            if shapeParentTo:
                try:
                    i_target = cgmMeta.validateObjArg(shapeParentTo,cgmMeta.cgmObject)
                    curves.parentShapeInPlace(i_target.mNode,self.mi_control.mNode)
                    i_target = cgmMeta.asMeta(i_target,'cgmControl',setClass = True)
                    #self.mi_control.delete()
                    self.mi_control = i_target#replace the control with the joint    
                except Exception,error:raise StandardError,"shapeParentTo | %s"%error

            useShape = self.d_kws['useShape']
            if useShape is not None:
                try:
                    i_shape = cgmMeta.validateObjArg(useShape,cgmMeta.cgmObject,mayaType='nurbsCurve')
                    curves.parentShapeInPlace(self.mi_control.mNode,i_shape.mNode)
                except Exception,error:raise StandardError,"useShape | %s"%error

        def _copyPivot(self):		    
            copyPivot = self.d_kws['copyPivot']
            if copyPivot is not None:
                try:
                    if issubclass(type(copyPivot),cgmMeta.cgmNode):
                        i_target = copyPivot
                    elif mc.objExists(copyPivot):
                        i_target = cgmMeta.cgmObject(copyPivot)
                    else:
                        raise StandardError,"Failed to find suitable copyTransform object: '%s"%copyPivot

                    #Need to move this to default cgmNode stuff
                    self.mi_control.doCopyPivot(i_target.mNode)
                except Exception,error:raise StandardError,"copyPivot | %s"%error

        def _naming(self):		    
            typeModifier = self.d_kws['typeModifier']
            self.mi_control.addAttr('cgmType','controlAnim',lock=True)    
            if typeModifier is not None:
                self.mi_control.addAttr('cgmTypeModifier',str(typeModifier),lock=True)
            self.mi_control.doName()#self.mi_control.doName(nameShapes=True)

        def _aimSetup(self):		    
            aim = self.d_kws['aim']
            up = self.d_kws['up']
            makeAimable = self.d_kws['makeAimable']

            if aim is not None or up is not None or makeAimable:
                self.mi_control._verifyAimable()

        def _rotateOrder(self):	    		
            controlType = self.d_kws['controlType']
            setRotateOrder = self.d_kws['setRotateOrder']

            _rotateOrder = False
            if setRotateOrder is not None:
                _rotateOrder = setRotateOrder
            elif controlType in __d_rotateOrderDefaults__.keys():
                _rotateOrder = __d_rotateOrderDefaults__[controlType]
            elif self.mi_control.getAttr('cgmName') in __d_rotateOrderDefaults__.keys():
                _rotateOrder = __d_rotateOrderDefaults__[self.mi_control.getAttr('cgmName')]
            else:
                log.debug("%s rotateOrder not set on: '%s'"%(self._str_reportStart,self.mi_control.p_nameShort))

            #Set it ---------------------------------------------------------------
            if _rotateOrder:
                _rotateOrder = dictionary.validateRotateOrderString(_rotateOrder)
                mc.xform(self.mi_control.mNode, rotateOrder = _rotateOrder)


        def _initialFreeze(self):	    		
            freezeAll = self.d_kws['freezeAll']
            if freezeAll:
                mc.makeIdentity(self.mi_control.mNode, apply=True,t=1,r=1,s=1,n=0)

        def _groupsSetup(self):	    		
            addDynParentGroup = self.d_kws['addDynParentGroup']
            addSpacePivots = self.d_kws['addSpacePivots']
            shapeParentTo = self.d_kws['shapeParentTo']
            addExtraGroups = self.d_kws['addExtraGroups']
            addConstraintGroup = self.d_kws['addConstraintGroup']

            try:
                if addDynParentGroup or addSpacePivots or self.mi_control.getAttr('cgmName') == 'cog' or self._addMirrorAttributeBridges:
                    self.mi_control.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)
            except Exception,error:
                raise StandardError,"spacer | %s"%(error)       

            #==================================================== 
            if not shapeParentTo:
                #First our master group:
                try:
                    i_masterGroup = (cgmMeta.asMeta(self.mi_control.doGroup(True), 'cgmObject', setClass=True))
                    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
                    i_masterGroup.doName()
                    self.mi_control.connectChildNode(i_masterGroup,'masterGroup','groupChild')
                except Exception,error:raise StandardError,"masterGroup | %s"%(error)

                if addDynParentGroup:
                    try:
                        i_dynGroup = (cgmMeta.cgmObject(self.mi_control.doGroup(True)))
                        i_dynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=self.mi_control,dynGroup=i_dynGroup)
                        i_dynGroup.doName()

                        i_zeroGroup = (cgmMeta.cgmObject(self.mi_control.doGroup(True)))
                        i_zeroGroup.addAttr('cgmTypeModifier','zero',lock=True)
                        i_zeroGroup.doName()
                        self.mi_control.connectChildNode(i_zeroGroup,'zeroGroup','groupChild')
                    except Exception,error:raise StandardError,"dynGroup | %s"%(error)

                if addExtraGroups:
                    try:
                        for i in range(addExtraGroups):
                            i_group = (cgmMeta.asMeta(self.mi_control.doGroup(True),'cgmObject',setClass=True))
                            if type(addExtraGroups)==int and addExtraGroups>1:#Add iterator if necessary
                                i_group.addAttr('cgmIterator',str(i+1),lock=True)
                                i_group.doName()
                            self.ml_groups.append(i_group)
                        self.mi_control.msgList_connect("extraGroups",self.ml_groups,'groupChild')
                    except Exception,error:raise StandardError,"extra Groups | %s"%(error)

                if addConstraintGroup:#ConstraintGroups
                    try:
                        i_constraintGroup = (cgmMeta.asMeta(self.mi_control.doGroup(True),'cgmObject',setClass=True))
                        i_constraintGroup.addAttr('cgmTypeModifier','constraint',lock=True)
                        i_constraintGroup.doName()
                        self.ml_constraintGroups.append(i_constraintGroup)
                        self.mi_control.connectChildNode(i_constraintGroup,'constraintGroup','groupChild')	    	    
                    except Exception,error:raise StandardError,"constraintGroup | %s"%(error)

        def _spacePivots(self):	    		
            addSpacePivots = self.d_kws['addSpacePivots']
            if addSpacePivots:
                parent = self.mi_control.getMessage('masterGroup')[0]
                for i in range(int(addSpacePivots)):
                    try:
                        #i_pivot = rUtils.create_spaceLocatorForObject(self.mi_control.mNode,parent)
                        i_pivot = SPACEPIVOTS.create(self.mi_control.mNode,parent)
                        self.ml_spacePivots.append(i_pivot)
                        #log.info("spacePivot created: {0}".format(i_pivot.p_nameShort))			
                    except Exception,error:
                        raise StandardError,"space pivot %s | %s"%(i,error)

        def _mirrorSetup(self):	
            str_mirrorSide = self.str_mirrorSide
            str_mirrorAxis = self.str_mirrorAxis
            b_makeMirrorable = self.b_makeMirrorable
            if str_mirrorSide is not None or b_makeMirrorable:
                for mObj in [self.mi_control] + self.ml_spacePivots:
                    #log.info("mirrorsetup: {0}".format(mObj.p_nameShort))
                    try:self.mi_control._verifyMirrorable()
                    except Exception,error:raise StandardError,"_mirrorSetup | %s"%(error)
                    l_enum = cgmMeta.cgmAttr(self.mi_control,'mirrorSide').p_enum
                    if str_mirrorSide in l_enum:
                        log.debug("%s >> %s >> found in : %s"%(self._str_funcCombined, "mirrorSetup", l_enum))		
                        try:
                            self.mi_control.mirrorSide = l_enum.index(str_mirrorSide)
                            log.debug("%s >> %s >> mirrorSide set to: %s"%(self._str_funcCombined,"mirrorSetup",self.mi_control.mirrorSide ))						    
                        except Exception,error:raise StandardError,"str_mirrorSide : %s | %s"%(str_mirrorSide,error)
                    if str_mirrorAxis:
                        try:
                            self.mi_control.mirrorAxis = str_mirrorAxis
                            log.debug("%s >> %s >> str_mirrorAxis set: %s"%(self._str_funcCombined,"mirrorSetup",str_mirrorAxis))				    
                        except Exception,error:raise StandardError,"str_mirrorAxis : %s | %s"%(str_mirrorAxis,error)
                for mObj in self.mi_control.msgList_get('spacePivots'):
                    try:
                        try:mObj._verifyMirrorable()
                        except Exception,error:raise StandardError,"_mirrorSetup | %s"%(error)
                        #cgmMeta.cgmAttr(mObj,'mirrorSide').doConnectIn(self.mi_control,'mirrorSide')
                        #cgmMeta.cgmAttr(self.mi_control,'mirrorAxis').doCopyTo(mObj,connectTargetToSource = 1)
                        attributes.storeInfo(mObj.mNode,'mirrorAxis',"{0}.mirrorAxis".format(self.mi_control.mNode))
                        attributes.storeInfo(mObj.mNode,'mirrorSide',"{0}.mirrorSide".format(self.mi_control.mNode))

                    except Exception,error:raise StandardError,"spacePivot failed failed! {0}| error: {1}".format(mObj,error)

        def _freeze(self):	    		
            shapeParentTo = self.d_kws['shapeParentTo']
            freezeAll = self.d_kws['freezeAll']
            controlType = self.d_kws['controlType']

            if not shapeParentTo:
                if not freezeAll:
                    if self.mi_control.getAttr('cgmName') == 'cog' or controlType in __l_fullFreezeTypes__:
                        mc.makeIdentity(self.mi_control.mNode, apply=True,t=1,r=1,s=1,n=0)	
                    else:
                        mc.makeIdentity(self.mi_control.mNode, apply=True,t=1,r=0,s=1,n=0)
                else:
                    mc.makeIdentity(self.mi_control.mNode, apply=True,t=1,r=1,s=1,n=0)

        def _mirrorAttributeBridges_(self):	    		
            addForwardBack = self.d_kws['addForwardBack']

            if addForwardBack:
                mPlug_forwardBackDriver = cgmMeta.cgmAttr(self.mi_control,"forwardBack",attrType = 'float',keyable=True)
                try:
                    mPlug_forwardBackDriven = cgmMeta.validateAttrArg([self.mi_control,addForwardBack])['mi_plug']
                except Exception,error:raise StandardError,"push pull driver | %s"%(error)

                if self.str_mirrorSide.lower() == 'right':
                    arg_forwardBack = "%s = -%s"%(mPlug_forwardBackDriven.p_combinedShortName,
                                                  mPlug_forwardBackDriver.p_combinedShortName)		    
                else:
                    arg_forwardBack = "%s = %s"%(mPlug_forwardBackDriven.p_combinedShortName,
                                                 mPlug_forwardBackDriver.p_combinedShortName)

                mPlug_forwardBackDriven.p_locked = True
                mPlug_forwardBackDriven.p_hidden = True
                mPlug_forwardBackDriven.p_keyable = False		
                NodeF.argsToNodes(arg_forwardBack).doBuild()

            if self._addMirrorAttributeBridges:
                for l_bridge in self._addMirrorAttributeBridges:
                    _attrName = VALID.stringArg(l_bridge[0])
                    _attrToBridge = VALID.stringArg(l_bridge[1])
                    if not self.mi_control.hasAttr(_attrToBridge):
                        raise StandardError,"['%s' lacks the bridge attr '%s']"%(self.mi_control.p_nameShort,_attrToBridge)

                    mPlug_attrBridgeDriver = cgmMeta.cgmAttr(self.mi_control,_attrName,attrType = 'float',keyable=True)
                    try:
                        mPlug_attrBridgeDriven = cgmMeta.validateAttrArg([self.mi_control,_attrToBridge])['mi_plug']
                    except Exception,error:raise StandardError,"[validate control attribute bridge attr]{%s}"%(error)

                    if self.str_mirrorSide.lower() == 'right':
                        arg_attributeBridge = "%s = -%s"%(mPlug_attrBridgeDriven.p_combinedShortName,
                                                          mPlug_attrBridgeDriver.p_combinedShortName)		    
                    else:
                        arg_attributeBridge = "%s = %s"%(mPlug_attrBridgeDriven.p_combinedShortName,
                                                         mPlug_attrBridgeDriver.p_combinedShortName)

                    mPlug_attrBridgeDriven.p_locked = True
                    mPlug_attrBridgeDriven.p_hidden = True
                    mPlug_attrBridgeDriven.p_keyable = False		
                    NodeF.argsToNodes(arg_attributeBridge).doBuild()

        def _lockNHide(self):	
            autoLockNHide = self.d_kws['autoLockNHide']	    
            if autoLockNHide:
                if self.mi_control.hasAttr('cgmTypeModifier'):
                    if self.mi_control.cgmTypeModifier.lower() == 'fk':
                        attributes.doSetLockHideKeyableAttr(self.mi_control.mNode,channels=['tx','ty','tz','sx','sy','sz'])
                if self.mi_control.cgmName.lower() == 'cog':
                    attributes.doSetLockHideKeyableAttr(self.mi_control.mNode,channels=['sx','sy','sz'])
                cgmMeta.cgmAttr(self.mi_control,'visibility',lock=True,hidden=True)   
        def _returnBuild(self):
            return {'instance':self.mi_control,'self.ml_groups':self.ml_groups,'self.ml_constraintGroups':self.ml_constraintGroups}	
        #def _return_(self):
            #self.log_info("in Return....")
            #return {'instance':self.mi_control,'self.ml_groups':self.ml_groups,'self.ml_constraintGroups':self.ml_constraintGroups}	            
    return fncWrap(*args,**kws).go()