"""
------------------------------------------
rig_Utils: cgm.core.rigger.lib
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
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.classes import SnapFactory as Snap
import cgm.core.lib.snap_utils as SNAP
from cgm.core.lib import nameTools
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.lib import attribute_utils as ATTR
from cgm.lib import (distance,
                     attributes,
                     curves,
                     deformers,
                     lists,
                     rigging,
                     skinning,
                     dictionary,
                     search,
                     nodes,
                     joints,
                     cgmMath)

#>>> Eyeball
#===================================================================
def createEyeballRig(eyeballObject = None, ballJoint = None,
                     ikControl = None, fkControl = None,
                     driverAttr = None,
                     orientation = 'zyx',aimAxis = 'z+',upAxis = 'y+',
                     buildIK = False, buildJoystick = False,
                     moduleInstance = None,
                     d_nameTags = {'cgmDirection':'left','cgmName':'eye'},
                     setupVisBlend = False,
                     doControls = False):
    """
    Create an eyeball setup given a sphere template object

    @ Paramaters
    eyeballObject -- eyeball object that is the base object
    ballJoint -- the joint to constrain
    ikControl -- aim target
    driverAttr(attr) -- what you want to drive the blend
    """
    #>>> Check our args
    #====================================================================
    _str_funcName = 'createEyeballRig'
    log.info(">>> %s >> "%_str_funcName + "="*75)   
    d_blendSetupReturn = {}
    l_toBuild = []    
    d_return = {}
    try:
        #> Ball ------------------------------------------------------------
        mi_ball = cgmMeta.validateObjArg(eyeballObject,cgmMeta.cgmObject,noneValid=True,mayaType=['nurbsSurface','mesh','nurbsCurve'])
        if not mi_ball:raise StandardError,"bad eyeball object: %s"%eyeballObject

        f_averageSize = distance.returnBoundingBoxSizeToAverage(mi_ball.mNode)
        log.info("f_averageSize: %s"%f_averageSize)

        #> Bools ------------------------------------------------------------
        b_doControls = cgmValid.boolArg(doControls,calledFrom = _str_funcName)
        b_doIK = cgmValid.boolArg(buildIK,calledFrom = _str_funcName)
        b_doJoystick = cgmValid.boolArg(buildJoystick,calledFrom = _str_funcName)
        if b_doJoystick:
            raise NotImplementedError,"joystick setup not in yet"
        b_doVisBlend = cgmValid.boolArg(setupVisBlend,calledFrom = _str_funcName)

        #> Driver -----------------------------------------------------------
        d_attrCheckReturn = cgmMeta.validateAttrArg(driverAttr,noneValid=True) or {}
        miPlug_driver = d_attrCheckReturn.get('mi_plug') or False

        #>Controls ----------------------------------------------------------
        mi_aimTarget = cgmMeta.validateObjArg(ikControl,cgmMeta.cgmObject,noneValid=True)
        mi_fkControl = cgmMeta.validateObjArg(fkControl,cgmMeta.cgmObject,noneValid=True)

        #> axis -------------------------------------------------------------
        axis_aim = cgmValid.simpleAxis(aimAxis)
        axis_up = cgmValid.simpleAxis(upAxis)

        #Figure out what to build by making list which we will store back the locs to
        l_toBuild.append('fk')
        if b_doIK:
            l_toBuild.append('ik')
            l_toBuild.append('aimTarget')
            l_toBuild.append('upTarget')
        if len(l_toBuild) > 1:
            l_toBuild.insert(0,'blend')    
        if not l_toBuild:raise StandardError,"createEyeballRig >>> No options set to build anything. Aborting!"
    except Exception,error:
        raise StandardError,"%s >> Gather data fail! | error: %s"%(_str_funcName,error)

    try:#>>> Module instance
        i_module = False
        try:
            if moduleInstance is not None and moduleInstance.isModule():
                i_module = moduleInstance    
                log.info("%s >> module instance found: %s"%(_str_funcName,i_module.p_nameShort))		
        except:pass
        if i_module and not d_nameTags:#get some name tags from the module if we don't have them  assigned
            d_nameTags = i_module.getNameDict(ignore = 'cgmType')
    except Exception,error:
        raise StandardError,"%s >> Module check fail! | error: %s"%(_str_funcName,error)

    try:#>>> Joints
        #==================================================================== 
        mi_ballJoint = cgmMeta.validateObjArg(ballJoint,cgmMeta.cgmObject,noneValid=True,mayaType=['joint'])
        if not mi_ballJoint:
            raise NotImplementedError,"%s >>Need to implement joint creation"%(_str_funcName)
            log.info("Need to created ball joint")
            l_pos = mi_ball.getPosition()
            str_ballJoint = mc.joint (p=(l_pos[0],l_pos[1],l_pos[2]))
            mi_ballJoint = cgmMeta.validateObjArg(str_ballJoint,cgmMeta.cgmObject,noneValid=True,mayaType=['joint'])	
            mi_ballJoint.parent = False
    except Exception,error:
        raise StandardError,"%s >> Setup joints fail! | error: %s"%(_str_funcName,error)


    try:#>>> Setup transforms
        #==================================================================== 
        #What is our target
        if mi_ballJoint:mi_target = mi_ballJoint
        else:mi_target = mi_ball

        #> Build our group ---------------------------------------------------
        mi_group = mi_target.doCreateAt(copyAttrs = False)
        if d_nameTags: mi_group.doTagAndName(d_nameTags)
        d_return['mi_rigGroup'] = mi_group #store to return dict

        #> driver -------------------------------------------------------------
        if not miPlug_driver:
            miPlug_driver = cgmMeta.cgmAttr(mi_group, 'blend', 'float', keyable=True, minValue=0, maxValue= 1)

        #Build our locs
        md_locs = {}#Storage dict

        for s in l_toBuild:
            try:
                log.info("%s >> building %s"%(_str_funcName,s))
                mi_loc = mi_target.doLoc(fastMode = True) #Create it
                #Naming ----------------------------------
                if d_nameTags:
                    d_tmpNameTags = d_nameTags
                    d_tmpNameTags['cgmTypeModifier'] = s	    
                else:
                    d_tmpNameTags = {'cgmTypeModifier':s}
                mi_loc.doTagAndName(d_tmpNameTags)#Name it

                md_locs[s] = mi_loc #Store it to our dict
                mi_loc.parent = mi_group #Parent to group
            except Exception,error:
                raise StandardError, "createEyeballRig >>> Failed to create '%s' loc | error: %s"%(s,error)
        d_return['md_locs']=md_locs#store to return dict

    except Exception,error:
        raise StandardError,"%s >> Setup transform fail! | error: %s"%(_str_funcName,error)

    try:#Build our ik one ------------------------------------------
        if b_doIK:
            #First let's move our aimers and ups
            mi_aimLoc = md_locs['aimTarget']
            mi_upLoc = md_locs['upTarget']
            mi_ikLoc = md_locs['ik']

            mi_upLoc.__setattr__('t%s'%orientation[1],f_averageSize*1.5)

            #See if we have an aim target
            if mi_aimTarget:
                SNAP.go(mi_aimLoc,mi_aimTarget.mNode)#Snap to the target
                mi_aimLoc.parent = mi_aimTarget#Parent it
            else:
                mi_aimLoc.__setattr__('t%s'%orientation[0],f_averageSize*5)

            constBuffer = mc.aimConstraint(mi_aimLoc.mNode,mi_ikLoc.mNode,
                                           aimVector  = axis_aim.p_vector,
                                           upVector = axis_up.p_vector,
                                           worldUpObject = mi_upLoc.mNode,
                                           worldUpType = 'object')
    except Exception,error:
        raise StandardError,"%s >> ik setup fail! | error: %s"%(_str_funcName,error)

    try:#Build blend loc --------------------------------------------------------------
        mi_blendLoc = md_locs.get('blend') or False
        if mi_blendLoc:
            mi_fkLoc = md_locs['fk']
            mi_ikLoc = md_locs['ik']
            d_blendSetupReturn = connectBlendChainByConstraint(mi_fkLoc,mi_ikLoc,mi_blendLoc,driver = miPlug_driver, l_constraints=['point','orient'])

            #Increase the size of the loc to make it visible
            l_shapes = mi_blendLoc.getShapes()
            mi_shape = cgmMeta.cgmNode(l_shapes[0])
            mi_shape.localScaleX = f_averageSize
            mi_shape.localScaleY = f_averageSize
            mi_shape.localScaleZ = f_averageSize

    except Exception,error:
        raise StandardError,"%s >> blend loc setup fail! | error: %s"%(_str_funcName,error)

    try:#Vis blend
        #==============================================================
        if mi_blendLoc and d_blendSetupReturn and b_doVisBlend and miPlug_driver:
            log.info("%s >>Setting up vis blend"%(_str_funcName))
            #>>> Setup a vis blend result
            d_blendReturn = NodeF.createSingleBlendNetwork(miPlug_driver,
                                                           [miPlug_driver.obj.mNode,'result_ikOn'],
                                                           [miPlug_driver.obj.mNode,'result_fkOn'],
                                                           keyable=False,hidden=False)	    
            mPlug_IKon = d_blendReturn['d_result1']['mi_plug']
            mPlug_FKon = d_blendReturn['d_result2']['mi_plug']
            d_return['mPlug_fkVis'] = mPlug_FKon
            d_return['mPlug_ikVis'] = mPlug_IKon	    

    except Exception,error:
        raise StandardError,"%s >> Vis blend setup failed! | error: %s"%(_str_funcName,error)

    try:#Module stuff --------------------------------------------------------------
        if i_module:#if we have a module, connect vis
            for l in md_locs.keys():
                log.info("%s >> connecting to module: %s"%(_str_funcName,s))		
                i_loc = md_locs[l]
                i_loc.overrideEnabled = 1		
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_loc.mNode,'overrideVisibility'))    
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_loc.mNode,'overrideDisplayType'))    
    except Exception,error:
        raise StandardError,"%s >> blend loc setup fail! | error: %s"%(_str_funcName,error)

    try:#Setup contstraints for the joint
        if mi_ballJoint:
            if md_locs.get('blend'):mi_orientTarget = md_locs.get('blend')
            else:mi_orientTarget = md_locs.get('fk')
            log.info("%s >> joint orient target: '%s'"%(_str_funcName,mi_orientTarget.p_nameShort))		
            constBuffer = mc.orientConstraint(mi_orientTarget.mNode,mi_ballJoint.mNode,maintainOffset= True)
            attributes.doSetAttr(constBuffer[0],'interpType',0)

        if mi_fkControl:
            log.info("%s >> FK constraining. target: '%s' | control: '%s'"%(_str_funcName,mi_fkLoc.p_nameShort,mi_fkControl.p_nameShort))		
            constBuffer = mc.orientConstraint(mi_fkControl.mNode,mi_fkLoc.mNode,maintainOffset= True)
            attributes.doSetAttr(constBuffer[0],'interpType',0)

    except Exception,error:
        raise StandardError,"%s >> joint constraint setup fail! | error: %s"%(_str_funcName,error)

    return d_return


def create_simpleEyelidSetup(uprLidJoint = None, lwrLidJoint = None,
                             ballJoint = None,
                             controlObject = None,
                             driverAttr = None,
                             orientation = 'zyx', aimAxis = 'z+',upAxis = 'y+',
                             moduleInstance = None,
                             d_nameTags = {'cgmDirection':'left','cgmName':'eye'},
                             doControls = False):
    """
    Function to setup a simple eyelid rig.
    
    """
    #>>> Check our args
    #====================================================================
    _str_funcName = 'createEyeballRig'
    log.info(">>> %s >> "%_str_funcName + "="*75)   
    d_blendSetupReturn = {}
    l_toBuild = []    
    d_return = {}
    try:
        #> Ball ------------------------------------------------------------
        mi_ball = cgmMeta.validateObjArg(eyeballObject,cgmMeta.cgmObject,noneValid=True,mayaType=['nurbsSurface','mesh','nurbsCurve'])
        if not mi_ball:raise StandardError,"bad eyeball object: %s"%eyeballObject

        #f_averageSize = distance.returnBoundingBoxSizeToAverage(mi_ball.mNode)
        #log.info("f_averageSize: %s"%f_averageSize)

        #> Bools ------------------------------------------------------------
        '''b_doControls = cgmValid.boolArg(doControls,calledFrom = _str_funcName)
        b_doIK = cgmValid.boolArg(buildIK,calledFrom = _str_funcName)
        b_doJoystick = cgmValid.boolArg(buildJoystick,calledFrom = _str_funcName)
        if b_doJoystick:
            raise NotImplementedError,"joystick setup not in yet"
        b_doVisBlend = cgmValid.boolArg(setupVisBlend,calledFrom = _str_funcName)'''

        #> Driver -----------------------------------------------------------
        d_attrCheckReturn = cgmMeta.validateAttrArg(driverAttr,noneValid=True) or {}
        miPlug_driver = d_attrCheckReturn.get('mi_plug') or False

        #>Controls ----------------------------------------------------------
        mi_controlObject = cgmMeta.validateObjArg(controlObject,cgmMeta.cgmObject,noneValid=True)

        #> axis -------------------------------------------------------------
        axis_aim = cgmValid.simpleAxis(aimAxis)
        axis_up = cgmValid.simpleAxis(upAxis)

        #Figure out what to build by making list which we will store back the locs to
        l_toBuild.append('uprBase','uprBlend','uprTrack','lwrB')

    except Exception,error:
        raise Exception,"{0} >> Gather data fail! | error: {1}".format(_str_funcName,error)

    try:#>>> Module instance
        i_module = False
        try:
            if moduleInstance is not None and moduleInstance.isModule():
                i_module = moduleInstance    
                log.info("%s >> module instance found: %s"%(_str_funcName,i_module.p_nameShort))		
        except:pass
        if i_module and not d_nameTags:#get some name tags from the module if we don't have them  assigned
            d_nameTags = i_module.getNameDict(ignore = 'cgmType')
    except Exception,error:
        raise Exception,"{0} >> Module check fail! | error: {1}".format(_str_funcName,error)

    try:#>>> Joints
        #==================================================================== 
        mi_ballJoint = cgmMeta.validateObjArg(ballJoint,cgmMeta.cgmObject,noneValid=True,mayaType=['joint'])
        if not mi_ballJoint:
            raise NotImplementedError,"{0} >>Must have ball joint".format(_str_funcName)
    except Exception,error:
        raise Exception,"{0} >> Setup joints fail! | error: {1}"%(_str_funcName,error)


    try:#>>> Setup transforms
        #==================================================================== 
        #What is our target
        mi_target = mi_ballJoint

        #> Build our group ---------------------------------------------------
        mi_group = mi_target.doCreateAt(copyAttrs = False)
        if d_nameTags: mi_group.doTagAndName(d_nameTags)
        d_return['mi_rigGroup'] = mi_group #store to return dict

        #> driver -------------------------------------------------------------
        if not miPlug_driver:
            miPlug_driver = cgmMeta.cgmAttr(mi_group, 'blend', 'float', keyable=True, minValue=0, maxValue= 1)

        #Build our locs
        md_locs = {}#Storage dict

        for s in l_toBuild:
            try:
                log.info("{0} >> building {1}".format(_str_funcName,s))
                mi_loc = mi_target.doLoc(fastMode = True) #Create it
                #Naming ----------------------------------
                if d_nameTags:
                    d_tmpNameTags = d_nameTags
                    d_tmpNameTags['cgmTypeModifier'] = s	    
                else:
                    d_tmpNameTags = {'cgmTypeModifier':s}
                mi_loc.doTagAndName(d_tmpNameTags)#Name it

                md_locs[s] = mi_loc #Store it to our dict
                mi_loc.parent = mi_group #Parent to group
            except Exception,error:
                raise Exception, "{0} >>> Failed to create '{1}' loc | error: {2}".format(_str_funcName,s,error)
        d_return['md_locs']=md_locs#store to return dict

    except Exception,error:
        raise Exception,"{0} >> Setup transform fail! | error: {1}"%(_str_funcName,error)

    try:#Build blend loc --------------------------------------------------------------
        mi_blendLoc = md_locs.get('blend') or False
        if mi_blendLoc:
            mi_fkLoc = md_locs['fk']
            mi_ikLoc = md_locs['ik']
            d_blendSetupReturn = connectBlendChainByConstraint(mi_fkLoc,mi_ikLoc,mi_blendLoc,driver = miPlug_driver, l_constraints=['point','orient'])

            #Increase the size of the loc to make it visible
            l_shapes = mi_blendLoc.getShapes()
            mi_shape = cgmMeta.cgmNode(l_shapes[0])
            mi_shape.localScaleX = f_averageSize
            mi_shape.localScaleY = f_averageSize
            mi_shape.localScaleZ = f_averageSize

    except Exception,error:
        raise Exception,"%s >> blend loc setup fail! | error: %s"%(_str_funcName,error)

    try:#Vis blend
        #==============================================================
        if mi_blendLoc and d_blendSetupReturn and b_doVisBlend and miPlug_driver:
            log.info("%s >>Setting up vis blend"%(_str_funcName))
            #>>> Setup a vis blend result
            d_blendReturn = NodeF.createSingleBlendNetwork(miPlug_driver,
                                                           [miPlug_driver.obj.mNode,'result_ikOn'],
                                                           [miPlug_driver.obj.mNode,'result_fkOn'],
                                                           keyable=False,hidden=False)	    
            mPlug_IKon = d_blendReturn['d_result1']['mi_plug']
            mPlug_FKon = d_blendReturn['d_result2']['mi_plug']
            d_return['mPlug_fkVis'] = mPlug_FKon
            d_return['mPlug_ikVis'] = mPlug_IKon	    

    except Exception,error:
        raise Exception,"%s >> Vis blend setup failed! | error: %s"%(_str_funcName,error)

    try:#Module stuff --------------------------------------------------------------
        if i_module:#if we have a module, connect vis
            for l in md_locs.keys():
                log.info("%s >> connecting to module: %s"%(_str_funcName,s))		
                i_loc = md_locs[l]
                i_loc.overrideEnabled = 1		
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_loc.mNode,'overrideVisibility'))    
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_loc.mNode,'overrideDisplayType'))    
    except Exception,error:
        raise Exception,"%s >> blend loc setup fail! | error: %s"%(_str_funcName,error)

    try:#Setup contstraints for the joint
        if mi_ballJoint:
            if md_locs.get('blend'):mi_orientTarget = md_locs.get('blend')
            else:mi_orientTarget = md_locs.get('fk')
            log.info("%s >> joint orient target: '%s'"%(_str_funcName,mi_orientTarget.p_nameShort))		
            constBuffer = mc.orientConstraint(mi_orientTarget.mNode,mi_ballJoint.mNode,maintainOffset= True)
            attributes.doSetAttr(constBuffer[0],'interpType',0)

        if mi_fkControl:
            log.info("%s >> FK constraining. target: '%s' | control: '%s'"%(_str_funcName,mi_fkLoc.p_nameShort,mi_fkControl.p_nameShort))		
            constBuffer = mc.orientConstraint(mi_fkControl.mNode,mi_fkLoc.mNode,maintainOffset= True)
            attributes.doSetAttr(constBuffer[0],'interpType',0)

    except Exception,error:
        raise Exception,"%s >> joint constraint setup fail! | error: %s"%(_str_funcName,error)

    return d_return

#>>> Utilities
#===================================================================
def create_distanceMeasure(*args, **kws):
    """
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            """
            """	
            super(fncWrap, self).__init__(curve = None)
            self._str_funcName = 'create_measureDist'	
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'startObj',"default":None, 'argType':'maya Object',
                                          'help':"Start object. If none, loc will be created"},
                                         {'kw':'endObj',"default":None,'argType':'maya Object',
                                          'help':"end object. If none, loc will be created"},
                                         {'kw':'baseName',"default":'measure','argType':'string',
                                          'help':"String test to be used for parts of the setup."},
                                         cgmMeta._d_KWARG_asMeta] 	                                 
            self.__dataBind__(*args, **kws)
            self.l_funcSteps = [{'step':'Validate','call':self._validate_},
                                {'step':'Build','call':self._build_}]

        def _validate_(self):
            self._str_baseName = cgmValid.stringArg(self.d_kws['baseName'])
            self._b_asMeta = cgmValid.boolArg(self.d_kws['asMeta'])

            _d_check = {'start':{'key':'startObj'},
                        'end':{'key':'endObj'}}
            for str_key in _d_check.keys():
                try:
                    mi_buffer = cgmMeta.validateObjArg(self.d_kws[_d_check[str_key]['key']], mType = cgmMeta.cgmObject, noneValid = True)
                    if not mi_buffer:
                        mi_buffer = cgmMeta.asMeta(mc.spaceLocator()[0],'cgmObject',setClass=1)
                        mi_buffer.addAttr('cgmName',"%s_%s"%(self._str_baseName,str_key))
                        mi_buffer.doName()

                    self.__dict__["mi_%s"%str_key ]= mi_buffer
                except Exception,error:raise Exception,"[%s fail]{%s}"%(str_key,error)	    

        def _build_(self):
            try:#Create distance ---------------------------------------------------------
                self.mi_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
                self.mi_distanceObject = cgmMeta.cgmObject( self.mi_distanceShape.getTransform() )
                if self.d_kws['baseName']:
                    self.mi_distanceObject.addAttr('cgmName', self._str_baseName,lock = True)
                    self.mi_distanceObject.doName()
                self.mi_distanceObject.connectChildNode(self.mi_distanceShape,'shape')

            except Exception,error:raise Exception,"[Create distance fail]{%s}"%(error)

            try:#Connect  ---------------------------------------------------------
                _d_check = {'start':{'mObj':self.mi_start},
                            'end':{'mObj':self.mi_end}}	
                for str_key in _d_check.keys():
                    try:
                        _d = _d_check[str_key]
                        buffer = _d['mObj'].getPositionOutPlug()
                        if not buffer:
                            raise StandardError,"{Failed to find out plug for}"
                        mc.connectAttr (buffer,
                                        (self.mi_distanceShape.mNode+'.%sPoint'%str_key))

                        self.mi_distanceObject.connectChildNode(_d['mObj'],str_key)
                    except Exception,error:raise Exception,"[%s fail]{%s}"%(str_key,error)	    
            except Exception,error:raise Exception,"[Create distance fail]{%s}"%(error)	    

            if self._b_asMeta:
                return {'mi_shape':self.mi_distanceShape , 'mi_object':self.mi_distanceObject,
                        'mi_start':self.mi_start, 'mi_end':self.mi_end}
            return {'shape':self.mi_distanceShape.mNode , 'object':self.mi_distanceObject.mNode ,
                    'start':self.mi_start.mNode , 'end':self.mi_end.mNode }	    
    return fncWrap(*args, **kws).go()

def addCGMDynamicGroup(target = None, parentTargets = None,
                       mode = None):

    #>>> Check our args
    #====================================================================
    i_target = cgmMeta.validateObjListArg(target,cgmMeta.cgmObject,noneValid=False)
    i_parentTargets = cgmMeta.validateObjListArg(parentTargets,cgmMeta.cgmObject,noneValid=True)


    if ml_midControls and len(ml_midControls) != len(ml_newJoints):
        raise StandardError,"addCGMSegmentSubControl>>> Enough controls for joints provided! joints: %s | controls: %s"%(len(ml_midControls),len(ml_newJoints))

    i_baseParent = cgmMeta.validateObjArg(baseParent,cgmMeta.cgmObject,noneValid=False)
    i_endParent = cgmMeta.validateObjArg(endParent,cgmMeta.cgmObject,noneValid=False)
    i_segmentCurve = cgmMeta.validateObjArg(segmentCurve,cgmMeta.cgmObject,noneValid=False)
    i_segmentCurveSkinCluster = cgmMeta.validateObjArg(deformers.returnObjectDeformers(i_segmentCurve.mNode,'skinCluster')[0],
                                                       noneValid=True)


    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
    except:pass
    if i_module:
        if baseName is None: baseName = i_module.getPartNameBase()#Get part base name	    
    if baseName is None:
        if i_segmentCurve and i_segmentCurve.hasAttr('cgmName'):
            baseName = i_segmentCurve.cgmName
        else:
            baseName = 'midSegment'

    log.debug('ml_newJoints: %s'%ml_newJoints)
    log.debug('ml_midControls: %s'%ml_midControls)
    log.debug('i_baseParent: %s'%i_baseParent)
    log.debug('i_endParent: %s'%i_endParent)
    log.debug('i_segmentCurve: %s'%i_segmentCurve)
    log.debug('i_module: %s'%i_module)

#@cgmGeneral.Timer    
def addCGMSegmentSubControl(joints=None,segmentCurve = None,baseParent = None, endParent = None,
                            midControls = None, orientation = 'zyx',controlOrientation = None, controlTwistAxis = 'rotateY',
                            addTwist = True, baseName = None, rotateGroupAxis = 'rotateZ', blendLength = None, connectMidScale = True,
                            moduleInstance = None):
    """

    """
    _str_funcName = 'addCGMSegmentSubControl'
    log.info(">>> %s >> "%_str_funcName + "="*75)   

    try:#Gather data =====================================================================================
        ml_newJoints = cgmMeta.validateObjListArg(joints,cgmMeta.cgmObject,noneValid=False,mayaType='joint')
        ml_midControls = cgmMeta.validateObjListArg(midControls,cgmMeta.cgmObject,noneValid=True)

        if ml_midControls and len(ml_midControls) != len(ml_newJoints):
            raise StandardError," Enough controls for joints provided! joints: %s | controls: %s"%(len(ml_midControls),len(ml_newJoints))

        i_baseParent = cgmMeta.validateObjArg(baseParent,cgmMeta.cgmObject,noneValid=False)
        i_endParent = cgmMeta.validateObjArg(endParent,cgmMeta.cgmObject,noneValid=False)
        i_segmentCurve = cgmMeta.validateObjArg(segmentCurve,cgmMeta.cgmObject,noneValid=False)
        i_segmentCurveSkinCluster = cgmMeta.validateObjArg(deformers.returnObjectDeformers(i_segmentCurve.mNode,'skinCluster')[0],
                                                           noneValid=True)
        i_segmentGroup = i_segmentCurve.segmentGroup      

        #> Orientation ------------------------------------------------------------
        if controlOrientation is None:
            controlOrientation = orientation        

        aimVector = cgmValid.simpleAxis("%s+"%orientation[0]).p_vector
        aimVectorNegative = cgmValid.simpleAxis("%s-"%orientation[0]).p_vector
        upVector = cgmValid.simpleAxis("%s+"%orientation[1]).p_vector 
        outChannel = orientation[2]
        upChannel = '%sup'%orientation[1]            

    except Exception,error:
        raise StandardError,"%s >> data gather | error: %s"%(_str_funcName,error)  

    try:#>>> Module instance =====================================================================================
        i_module = False
        try:
            if moduleInstance is not None and moduleInstance.isModule():
                i_module = moduleInstance    
                log.info("%s >> module instance found: %s"%(_str_funcName,i_module.p_nameShort))		
        except:pass

        if i_module:
            if baseName is None: baseName = i_module.getPartNameBase()#Get part base name	    
        if baseName is None:
            if i_segmentCurve and i_segmentCurve.hasAttr('cgmName'):
                baseName = i_segmentCurve.cgmName
            else:
                baseName = 'midSegment' 

        log.debug('ml_newJoints: %s'%ml_newJoints)
        log.debug('ml_midControls: %s'%ml_midControls)
        log.debug('i_baseParent: %s'%i_baseParent)
        log.debug('i_endParent: %s'%i_endParent)
        log.debug('i_segmentCurve: %s'%i_segmentCurve)
        log.debug('i_module: %s'%i_module)      

    except Exception,error:
        raise StandardError,"%s >> Module check | error: %s"%(_str_funcName,error)     

    """    
    #>>> Check our args
    #====================================================================
    ml_newJoints = cgmMeta.validateObjListArg(joints,cgmMeta.cgmObject,noneValid=False)
    ml_midControls = cgmMeta.validateObjListArg(midControls,cgmMeta.cgmObject,noneValid=True)
    if controlOrientation is None:
        controlOrientation = orientation

    if ml_midControls and len(ml_midControls) != len(ml_newJoints):
        raise StandardError,"addCGMSegmentSubControl>>> Enough controls for joints provided! joints: %s | controls: %s"%(len(ml_midControls),len(ml_newJoints))

    i_baseParent = cgmMeta.validateObjArg(baseParent,cgmMeta.cgmObject,noneValid=False)
    i_endParent = cgmMeta.validateObjArg(endParent,cgmMeta.cgmObject,noneValid=False)
    i_segmentCurve = cgmMeta.validateObjArg(segmentCurve,cgmMeta.cgmObject,noneValid=False)
    i_segmentCurveSkinCluster = cgmMeta.validateObjArg(deformers.returnObjectDeformers(i_segmentCurve.mNode,'skinCluster')[0],
                                                       noneValid=True)
    i_segmentGroup = i_segmentCurve.segmentGroup

    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
    except:pass
    if i_module:
        if baseName is None: baseName = i_module.getPartNameBase()#Get part base name	    
    if baseName is None:
        if i_segmentCurve and i_segmentCurve.hasAttr('cgmName'):
            baseName = i_segmentCurve.cgmName
        else:
            baseName = 'midSegment'

    log.debug('ml_newJoints: %s'%ml_newJoints)
    log.debug('ml_midControls: %s'%ml_midControls)
    log.debug('i_baseParent: %s'%i_baseParent)
    log.debug('i_endParent: %s'%i_endParent)
    log.debug('i_segmentCurve: %s'%i_segmentCurve)
    log.debug('i_module: %s'%i_module)

    #Gather info
    aimVector = dictionary.stringToVectorDict.get("%s+"%orientation[0])
    aimVectorNegative = dictionary.stringToVectorDict.get("%s-"%orientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%orientation[1])    
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]    
    """
    try:#Create Constraint  Curve =============================================================================
        #Spline -----------------------------------------------------------------
        if i_segmentCurve:#If we have a curve, duplicate it
            i_constraintSplineCurve = i_segmentCurve.doDuplicate(po = False, ic = False)
        else:
            l_pos = [i_baseParent.getPosition()]
            l_pos.expand([i_obj.getPosition() for i_obj in ml_newJoints])
            l_pos.append(i_endParent.getPosition())
            i_constraintSplineCurve = cgmMeta.cgmObject( mc.curve (d=3, ep = l_pos, os=True))
            i_constraintSplineCurve.addAttr('cgmName',baseName)

        i_constraintSplineCurve.addAttr('cgmTypeModifier','constraintSpline')
        i_constraintSplineCurve.doName()

        #Skin it ---------------------------------------------------------------------
        i_constraintSplineCurveCluster = cgmMeta.cgmNode(mc.skinCluster ([i_baseParent.mNode,i_endParent.mNode],
                                                                         i_constraintSplineCurve.mNode,
                                                                         tsb=True,
                                                                         maximumInfluences = 3,
                                                                         normalizeWeights = 1,dropoffRate=2.5)[0])

        i_constraintSplineCurveCluster.addAttr('cgmName', baseName)
        i_constraintSplineCurveCluster.addAttr('cgmTypeModifier','constraint', lock=True)
        i_constraintSplineCurveCluster.doName()

        #Linear
        #====================================================================	
        i_constraintLinearCurve = cgmMeta.cgmObject( mc.curve (d=1, ep = [i_baseParent.getPosition(),i_endParent.getPosition()], os=True))
        i_constraintLinearCurve.addAttr('cgmName',baseName)
        i_constraintLinearCurve.addAttr('cgmTypeModifier','constraintLinear')
        i_constraintLinearCurve.doName()

        #Skin it ---------------------------------------------------------------------------
        i_constraintLinearCurveCluster = cgmMeta.cgmNode(mc.skinCluster ([i_baseParent.mNode,i_endParent.mNode],
                                                                         i_constraintLinearCurve.mNode,
                                                                         tsb=True,
                                                                         maximumInfluences = 1,
                                                                         normalizeWeights = 1,dropoffRate=10.0)[0])

        i_constraintLinearCurveCluster.addAttr('cgmName', baseName)
        i_constraintLinearCurveCluster.addAttr('cgmTypeModifier','constraint', lock=True)
        i_constraintLinearCurveCluster.doName()	

    except Exception,error:
        raise StandardError,"%s >> constraint curve | error: %s"%(_str_funcName,error)    

    try:#Make some up locs for the base and end aim ============================================================================
        ml_pointOnCurveInfos = []
        splineShape = mc.listRelatives(i_constraintSplineCurve.mNode,shapes=True)[0]
        linearShape = mc.listRelatives(i_constraintLinearCurve.mNode,shapes=True)[0] 
        """
        baseDist = distance.returnDistanceBetweenObjects(i_baseParent.mNode,i_endParent.mNode)/4
        #Start up
        i_upStart = i_baseParent.doCreateAt()
        i_upStart.addAttr('cgmType','midStartAimUp',attrType='string',lock=True)
        i_upStart.doName()
        i_upStart.parent = i_baseParent.mNode  
        attributes.doSetAttr(i_upStart.mNode,'t%s'%orientation[1],baseDist)

        #End up
        i_upEnd = i_endParent.doCreateAt()
        i_upEnd.addAttr('cgmType','midEndAimUp',attrType='string',lock=True)
        i_upEnd.doName()    
        i_upEnd.parent = False    
        i_upEnd.parent = i_endParent.mNode  
        attributes.doSetAttr(i_upEnd.mNode,'t%s'%orientation[1],baseDist)
        """
    except Exception,error:
        raise StandardError,"%s >> up transforms | error: %s"%(_str_funcName,error)   

    for i,i_obj in enumerate(ml_newJoints):
        if ml_midControls and ml_midControls[i]:#if we have a control curve, use it
            i_control = ml_midControls[i]
        else:#else, connect 
            i_control = i_obj
        try:#>>>Transforms     
            #Create group
            grp = i_obj.doGroup()
            i_followGroup = cgmMeta.asMeta(grp,'cgmObject',setClass=True)
            i_followGroup.addAttr('cgmTypeModifier','follow',lock=True)
            i_followGroup.doName()

            grp = i_obj.doGroup(True)	
            i_orientGroup = cgmMeta.asMeta(grp,'cgmObject',setClass=True)
            i_orientGroup.addAttr('cgmTypeModifier','orient',lock=True)
            i_orientGroup.doName()

            i_obj.parent = False#since stuff is gonna move, we'll parent back at end

            #=============================================================	
            #>>>PointTargets
            #linear follow
            i_linearFollowNull = i_obj.doCreateAt()
            i_linearFollowNull.addAttr('cgmType','linearFollow',attrType='string',lock=True)
            i_linearFollowNull.doName()
            #i_linearFollowNull.parent = i_anchorStart.mNode     
            i_linearPosNull = i_obj.doCreateAt()
            i_linearPosNull.addAttr('cgmType','linearPos',attrType='string',lock=True)
            i_linearPosNull.doName()

            #splineFollow
            i_splineFollowNull = i_obj.doCreateAt()
            i_splineFollowNull.addAttr('cgmType','splineFollow',attrType='string',lock=True)
            i_splineFollowNull.doName()	

            #>>>Orient Targets
            #aimstart
            i_aimStartNull = i_obj.doCreateAt()
            i_aimStartNull.addAttr('cgmType','aimStart',attrType='string',lock=True)
            i_aimStartNull.doName()
            i_aimStartNull.parent = i_followGroup.mNode    

            #aimEnd
            i_aimEndNull = i_obj.doCreateAt()
            i_aimEndNull.addAttr('cgmType','aimEnd',attrType='string',lock=True)
            i_aimEndNull.doName()
            i_aimEndNull.parent = i_followGroup.mNode   


            #>>>Attach 
            #=============================================================
            #>>>Spline
            l_closestInfo = distance.returnNearestPointOnCurveInfo(i_obj.mNode,i_constraintSplineCurve.mNode)
            i_closestSplinePointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
            mc.connectAttr ((splineShape+'.worldSpace'),(i_closestSplinePointNode.mNode+'.inputCurve'))	

            #> Name
            i_closestSplinePointNode.doStore('cgmName',i_obj)
            i_closestSplinePointNode.addAttr('cgmTypeModifier','spline',attrType='string',lock=True)	    
            i_closestSplinePointNode.doName()
            #>Set attachpoint value
            i_closestSplinePointNode.parameter = l_closestInfo['parameter']
            mc.connectAttr ((i_closestSplinePointNode.mNode+'.position'),(i_splineFollowNull.mNode+'.translate'))
            ml_pointOnCurveInfos.append(i_closestSplinePointNode) 

            #>>>Linear
            l_closestInfo = distance.returnNearestPointOnCurveInfo(i_obj.mNode,i_constraintLinearCurve.mNode)
            i_closestLinearPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
            mc.connectAttr ((linearShape+'.worldSpace'),(i_closestLinearPointNode.mNode+'.inputCurve'))	

            #> Name
            i_closestLinearPointNode.doStore('cgmName',i_obj)
            i_closestLinearPointNode.addAttr('cgmTypeModifier','linear',attrType='string',lock=True)	    	    
            i_closestLinearPointNode.doName()
            #>Set attachpoint value
            i_closestLinearPointNode.parameter = l_closestInfo['parameter']
            mc.connectAttr ((i_closestLinearPointNode.mNode+'.position'),(i_linearFollowNull.mNode+'.translate'))
            ml_pointOnCurveInfos.append(i_closestLinearPointNode) 	    
            i_linearPosNull.parent = i_linearFollowNull.mNode#paren the pos obj

        except Exception,error:
            raise StandardError,"%s >> build transforms | error: %s"%(_str_funcName,error)   


        #=============================================================	
        try:#>>> point Constrain
            cBuffer = mc.pointConstraint([i_splineFollowNull.mNode,i_linearPosNull.mNode],
                                         i_followGroup.mNode,
                                         maintainOffset = True, weight = 1)[0]
            i_pointConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)	

            #Blendsetup
            log.debug("i_pointConstraint: %s"%i_pointConstraint)
            log.debug("i_control: %s"%i_control)

            targetWeights = mc.pointConstraint(i_pointConstraint.mNode,q=True, weightAliasList=True)
            if len(targetWeights)>2:
                raise StandardError,"addCGMSegmentSubControl>>Too many weight targets: obj: %s | weights: %s"%(i_obj.mNode,targetWeights)

            d_midPointBlendReturn = NodeF.createSingleBlendNetwork([i_control.mNode,'linearSplineFollow'],
                                                                   [i_control.mNode,'resultSplineFollow'],
                                                                   [i_control.mNode,'resultLinearFollow'],
                                                                   keyable=True)

            #Connect                                  
            d_midPointBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_pointConstraint.mNode,targetWeights[0]))
            d_midPointBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_pointConstraint.mNode,targetWeights[1]))
            d_midPointBlendReturn['d_result1']['mi_plug'].p_hidden = True
            d_midPointBlendReturn['d_result2']['mi_plug'].p_hidden = True


        except Exception,error:
            raise StandardError,"%s >> Translate constrain setup | error: %s"%(_str_funcName,error)   

        try:#>>>Aim constraint and blend
            try:#Create our decomposeMatrix attrs
                #Start up
                i_upStart = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
                i_upStart.addAttr('cgmName',baseName,attrType='string',lock=True)                
                i_upStart.addAttr('cgmType','midStartAimUp',attrType='string',lock=True)
                i_upStart.doName()

                #Start up
                i_upEnd = cgmMeta.cgmNode(nodeType = 'decomposeMatrix')
                i_upEnd.addAttr('cgmName',baseName,attrType='string',lock=True)                
                i_upEnd.addAttr('cgmType','midEndAimUp',attrType='string',lock=True)
                i_upEnd.doName()                
            except Exception,error:
                raise StandardError,"decomposeMatrix | error: %s"%(error)                   

            cBuffer = mc.aimConstraint(i_baseParent.mNode,
                                       i_aimStartNull.mNode,
                                       maintainOffset = 0, weight = 1,
                                       aimVector = aimVectorNegative,
                                       upVector = upVector,
                                       worldUpType = 'vector' )[0]


            i_startAimConstraint = cgmMeta.asMeta(cBuffer,'cgmNode', setClass=True)
            #attributes.doConnectAttr(i_upStart.mNode,'inputMatrix')


            cBuffer = mc.aimConstraint(i_endParent.mNode,
                                       i_aimEndNull.mNode,
                                       maintainOffset = 0, weight = 1,
                                       aimVector = aimVector,
                                       upVector = upVector,
                                       worldUpType = 'vector' )[0]

            i_endAimConstraint = cgmMeta.asMeta(cBuffer,'cgmNode', setClass=True)            
            cBuffer = mc.orientConstraint([i_aimEndNull.mNode,i_aimStartNull.mNode],
                                          i_orientGroup.mNode,
                                          maintainOffset = False, weight = 1)[0]
            i_orientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode', setClass=True)	
            i_orientConstraint.interpType = 2

            #Blendsetup
            log.debug("i_orientConstraint: %s"%i_orientConstraint)
            log.debug("i_control: %s"%i_control)

            targetWeights = mc.orientConstraint(i_orientConstraint.mNode,q=True, weightAliasList=True)
            if len(targetWeights)>2:
                raise StandardError,"Too many weight targets: obj: %s | weights: %s"%(i_obj.mNode,targetWeights)

            d_midOrientBlendReturn = NodeF.createSingleBlendNetwork([i_control.mNode,'startEndAim'],
                                                                    [i_control.mNode,'resultEndAim'],
                                                                    [i_control.mNode,'resultStartAim'],
                                                                    keyable=True)

            #Connect                                  
            d_midOrientBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_orientConstraint.mNode,targetWeights[0]))
            d_midOrientBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_orientConstraint.mNode,targetWeights[1]))
            d_midOrientBlendReturn['d_result1']['mi_plug'].p_hidden = True
            d_midOrientBlendReturn['d_result2']['mi_plug'].p_hidden = True


        except Exception,error:
            raise StandardError,"%s >> Orient constrain setup | error: %s"%(_str_funcName,error)   

        try:#Skincluster work ---------------------------------------------------------------------------------------
            if i_segmentCurveSkinCluster:
                mc.skinCluster(i_segmentCurveSkinCluster.mNode,edit=True,ai=i_obj.mNode,dropoffRate = 2.5)
                #Smooth the weights
                controlCurveTightenEndWeights(i_segmentCurve.mNode,i_baseParent.mNode,i_endParent.mNode,2)	
        except Exception,error:
            raise StandardError,"%s >> Skincluster fix  | error: %s"%(_str_funcName,error)   

        try:#>>>Add Twist -------------------------------------------------------------------------------------------
            mPlug_controlDriver = cgmMeta.cgmAttr(i_control.mNode,controlTwistAxis)	    
            mPlug_midTwist = cgmMeta.cgmAttr(i_segmentCurve,'twistMid')
            mPlug_midTwist.doConnectIn(mPlug_controlDriver.p_combinedShortName)

            if addTwist == 'asdasdfasdfasdfasdfasdf':
                if not i_segmentCurve:
                    raise StandardError,"addCGMSegmentSubControl>>Cannot add twist without a segmentCurve"
                if not i_segmentCurve.getMessage('drivenJoints'):
                    raise StandardError,"addCGMSegmentSubControl>>Cannot add twist stored bind joint info on segmentCurve: %s"%i_segmentCurve.getShortName()		    

                ml_drivenJoints = i_segmentCurve.msgList_get('drivenJoints',asMeta = True)

                closestJoint = distance.returnClosestObject(i_obj.mNode,[i_jnt.mNode for i_jnt in ml_drivenJoints])
                closestIndex = [i_jnt.mNode for i_jnt in ml_drivenJoints].index(closestJoint)
                upLoc = cgmMeta.cgmObject(closestJoint).rotateUpGroup.upLoc.mNode
                i_rotateUpGroup = cgmMeta.cgmObject(closestJoint).rotateUpGroup
                plug_rotateGroup = "%s.%s"%(i_rotateUpGroup.mNode,rotateGroupAxis)
                #Twist setup start
                #grab driver
                driverNodeAttr = attributes.returnDriverAttribute(plug_rotateGroup,True) 

                #get driven
                #rotDriven = attributes.returnDrivenAttribute(driverNodeAttr,True)

                rotPlug = attributes.doBreakConnection(i_rotateUpGroup.mNode,
                                                       rotateGroupAxis)
                #Create the add node
                mPlug_controlDriver = cgmMeta.cgmAttr(i_control.mNode,controlTwistAxis)
                l_driverPlugs = [driverNodeAttr,mPlug_controlDriver.p_combinedShortName]

                #Get the driven so that we can bridge to them 
                log.debug("midFollow "+ "="*50)
                log.debug("closestIndex: %s"%closestIndex)		
                log.debug("rotPlug: %s"%rotPlug)
                log.debug("rotateGroup: %s"%plug_rotateGroup)
                log.debug("originalDriverNode: %s"%driverNodeAttr)		
                log.debug("aimVector: '%s'"%aimVector)
                log.debug("upVector: '%s'"%upVector)    
                log.debug("upLoc: '%s'"%upLoc)
                #log.debug("rotDriven: '%s'"%rotDriven)
                log.debug("driverPlugs: '%s'"%l_driverPlugs)
                log.debug("="*50)

                #>>>Twist setup 
                #Connect To follow group
                #attributes.doConnectAttr(rotPlug,"%s.r%s"%(i_midFollowGrp.mNode,
                    #                                          self._jointOrientation[0]))

                #>> Setup up the main twist add
                arg_add = "%s = %s"
                i_pmaAdd = NodeF.createAverageNode(l_driverPlugs,
                                                   operation=1)

                attributes.doConnectAttr("%s.output1D"%i_pmaAdd.mNode,plug_rotateGroup)

                #>> Let's do the blend ===============================================================
                #First split it out ------------------------------------------------------------------
                ml_beforeJoints = ml_drivenJoints[1:closestIndex]
                ml_beforeJoints.reverse()
                ml_afterJoints = ml_drivenJoints[closestIndex+1:-1]
                log.debug("beforeJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_beforeJoints])
                log.debug("afterJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_afterJoints])

                #Get our factors ------------------------------------------------------------------
                mPlugs_factors = []
                for i,fac in enumerate([0.75,0.5,0.25]):
                    mPlug_factor = cgmMeta.cgmAttr(i_segmentCurve,"out_%s_blendFactor_%s"%(closestIndex,i+1),attrType='float',lock=True)
                    #str_factor = str(1.0/(i+2))
                    str_factor = str(fac)
                    log.debug(str_factor)
                    log.debug(mPlug_factor.p_combinedShortName)
                    log.debug(mPlug_controlDriver.p_combinedShortName)
                    arg = "%s = %s * %s"%(mPlug_factor.p_combinedShortName,mPlug_controlDriver.p_combinedShortName,str_factor)
                    log.debug("%s arg: %s"%(i,arg))
                    NodeF.argsToNodes(arg).doBuild()
                    mPlugs_factors.append(mPlug_factor)

                #Connect Them ----------------------------------------------------------------------
                def addFactorToJoint(i,i_jnt):
                    try:
                        log.debug("On '%s'"%i_jnt.getShortName())

                        upLoc = i_jnt.rotateUpGroup.upLoc.mNode
                        i_rotateUpGroup = i_jnt.rotateUpGroup
                        plug_rotateGroup = "%s.%s"%(i_rotateUpGroup.mNode,rotateGroupAxis)

                        #Twist setup start
                        driverNodeAttr = attributes.returnDriverAttribute(plug_rotateGroup,True) 

                        rotPlug = attributes.doBreakConnection(i_rotateUpGroup.mNode,
                                                               rotateGroupAxis)
                        #Create the add node
                        l_driverPlugs = [driverNodeAttr,mPlugs_factors[i].p_combinedShortName]		    
                        i_pmaAdd = NodeF.createAverageNode(l_driverPlugs,
                                                           operation=1)

                        attributes.doConnectAttr("%s.output1D"%i_pmaAdd.mNode,plug_rotateGroup)
                    except Exception,error:
                        log.error("'%s' Failed | %s"%(i_jnt.getShortName(),error))

                for i,i_jnt in enumerate(ml_beforeJoints):
                    addFactorToJoint(i,i_jnt)

                for i,i_jnt in enumerate(ml_afterJoints):
                    addFactorToJoint(i,i_jnt)

        except Exception,error:
            raise StandardError,"%s >> add twist | error: %s"%(_str_funcName,error)   

        try:#>>> Connect mid scale work ---------------------------------------------------------------------------------------
            if connectMidScale:
                if not i_segmentCurve.hasAttr('scaleMidUp') or not i_segmentCurve.hasAttr('scaleMidOut'):
                    i_segmentCurve.select()
                    raise StandardError, "Segment curve missing scaleMidUp or scaleMideOut"
                mPlug_outDriver = cgmMeta.cgmAttr(i_control,"s%s"%controlOrientation[2])
                mPlug_upDriver = cgmMeta.cgmAttr(i_control,"s%s"%controlOrientation[1])
                mPlug_scaleOutDriver = cgmMeta.cgmAttr(i_control,"out_scaleOutNormal",attrType='float')
                mPlug_scaleUpDriver = cgmMeta.cgmAttr(i_control,"out_scaleUpNormal",attrType='float')
                mPlug_out_scaleUp = cgmMeta.cgmAttr(i_control,"out_scaleOutInv",attrType='float')
                mPlug_out_scaleOut = cgmMeta.cgmAttr(i_control,"out_scaleUpInv",attrType='float')	
                # -1 * (1 - driver)
                arg_up1 = "%s = 1 - %s"%(mPlug_scaleUpDriver.p_combinedShortName,mPlug_upDriver.p_combinedShortName)
                arg_out1 = "%s = 1 - %s"%(mPlug_scaleOutDriver.p_combinedShortName,mPlug_outDriver.p_combinedShortName)
                arg_up2 = "%s = -1 * %s"%(mPlug_out_scaleUp.p_combinedShortName,mPlug_scaleUpDriver.p_combinedShortName)
                arg_out2 = "%s = -1 * %s"%(mPlug_out_scaleOut.p_combinedShortName,mPlug_scaleOutDriver.p_combinedShortName)
                for arg in [arg_up1,arg_out1,arg_up2,arg_out2]:
                    NodeF.argsToNodes(arg).doBuild()

                mPlug_out_scaleUp.doConnectOut("%s.scaleMidUp"%i_segmentCurve.mNode)
                mPlug_out_scaleOut.doConnectOut("%s.scaleMidOut"%i_segmentCurve.mNode)

                #Now let's connect scale of the start and end controls to a group so it's visually consistenent
                mc.scaleConstraint([i_baseParent.mNode,i_endParent.mNode],i_orientGroup.mNode)


        except Exception,error:
            raise StandardError,"%s >> mid scale | error: %s"%(_str_funcName,error)   

        try:#Parent at very end to keep the joint from moving
            attributes.doConnectAttr("%s.worldMatrix"%(i_baseParent.mNode),"%s.%s"%(i_upStart.mNode,'inputMatrix'))
            attributes.doConnectAttr("%s.%s"%(i_upStart.mNode,"outputRotate"),"%s.%s"%(i_startAimConstraint.mNode,"upVector"))            
            attributes.doConnectAttr("%s.worldMatrix"%(i_endParent.mNode),"%s.%s"%(i_upEnd.mNode,'inputMatrix'))
            attributes.doConnectAttr("%s.%s"%(i_upEnd.mNode,"outputRotate"),"%s.%s"%(i_endAimConstraint.mNode,"upVector"))  

            for mi_const in [i_startAimConstraint,i_endAimConstraint]:
                mi_const.worldUpVector = [0,0,0]            



            if i_control != i_obj:#Parent our control if we have one
                if i_control.getMessage('masterGroup'):
                    i_control.masterGroup.parent = i_orientGroup
                else:
                    i_control.parent = i_orientGroup.mNode
                    i_control.doGroup(True)
                    mc.makeIdentity(i_control.mNode, apply=True,t=1,r=0,s=1,n=0)
                i_obj.parent = i_control.mNode
            else:
                i_obj.parent = i_orientGroup.mNode

            #Parent pieces
            i_segmentCurve.parent = i_segmentGroup.mNode	
            i_constraintLinearCurve.parent = i_segmentGroup.mNode
            i_constraintSplineCurve.parent = i_segmentGroup.mNode
            i_linearFollowNull.parent = i_segmentGroup.mNode	
            i_splineFollowNull.parent = i_segmentGroup.mNode

        except Exception,error:
            raise StandardError,"%s >> parent end | error: %s"%(_str_funcName,error)   

        return {'ml_followGroups':[i_followGroup]}

def addCGMSegmentSubControlOLD(joints=None,segmentCurve = None,baseParent = None, endParent = None,
                               midControls = None, orientation = 'zyx',controlOrientation = None,
                               addTwist = True, baseName = None, rotateGroupAxis = 'rotateZ',
                               moduleInstance = None):
    #>>> Check our args
    #====================================================================
    ml_newJoints = cgmMeta.validateObjListArg(joints,cgmMeta.cgmObject,noneValid=False)
    ml_midControls = cgmMeta.validateObjListArg(midControls,cgmMeta.cgmObject,noneValid=True)


    if ml_midControls and len(ml_midControls) != len(ml_newJoints):
        raise StandardError,"addCGMSegmentSubControl>>> Enough controls for joints provided! joints: %s | controls: %s"%(len(ml_midControls),len(ml_newJoints))

    i_baseParent = cgmMeta.validateObjArg(baseParent,cgmMeta.cgmObject,noneValid=False)
    i_endParent = cgmMeta.validateObjArg(endParent,cgmMeta.cgmObject,noneValid=False)
    i_segmentCurve = cgmMeta.validateObjArg(segmentCurve,cgmMeta.cgmObject,noneValid=False)
    i_segmentCurveSkinCluster = cgmMeta.validateObjArg(deformers.returnObjectDeformers(i_segmentCurve.mNode,'skinCluster')[0],
                                                       noneValid=True)
    i_segmentGroup = i_segmentCurve.segmentGroup

    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
    except:pass
    if i_module:
        if baseName is None: baseName = i_module.getPartNameBase()#Get part base name	    
    if baseName is None:
        if i_segmentCurve and i_segmentCurve.hasAttr('cgmName'):
            baseName = i_segmentCurve.cgmName
        else:
            baseName = 'midSegment'

    log.debug('ml_newJoints: %s'%ml_newJoints)
    log.debug('ml_midControls: %s'%ml_midControls)
    log.debug('i_baseParent: %s'%i_baseParent)
    log.debug('i_endParent: %s'%i_endParent)
    log.debug('i_segmentCurve: %s'%i_segmentCurve)
    log.debug('i_module: %s'%i_module)

    #Gather info
    aimVector = dictionary.stringToVectorDict.get("%s+"%orientation[0])
    aimVectorNegative = dictionary.stringToVectorDict.get("%s-"%orientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%orientation[1])    
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]    

    #====================================================================
    try:#Create Constraint  Curve
        #Spline
        #====================================================================	
        if i_segmentCurve:#If we have a curve, duplicate it
            i_constraintSplineCurve = i_segmentCurve.doDuplicate(po=False,ic=False)
        else:
            l_pos = [i_baseParent.getPosition()]
            l_pos.expand([i_obj.getPosition() for i_obj in ml_newJoints])
            l_pos.append(i_endParent.getPosition())
            i_constraintSplineCurve = cgmMeta.cgmObject( mc.curve (d=3, ep = l_pos, os=True))
            i_constraintSplineCurve.addAttr('cgmName',baseName)

        i_constraintSplineCurve.addAttr('cgmTypeModifier','constraintSpline')
        i_constraintSplineCurve.doName()

        #Skin it
        i_constraintSplineCurveCluster = cgmMeta.cgmNode(mc.skinCluster ([i_baseParent.mNode,i_endParent.mNode],
                                                                         i_constraintSplineCurve.mNode,
                                                                         tsb=True,
                                                                         maximumInfluences = 3,
                                                                         normalizeWeights = 1,dropoffRate=2.5)[0])

        i_constraintSplineCurveCluster.addAttr('cgmName', baseName)
        i_constraintSplineCurveCluster.addAttr('cgmTypeModifier','constraint', lock=True)
        i_constraintSplineCurveCluster.doName()

        #Linear
        #====================================================================	
        i_constraintLinearCurve = cgmMeta.cgmObject( mc.curve (d=1, ep = [i_baseParent.getPosition(),i_endParent.getPosition()], os=True))
        i_constraintLinearCurve.addAttr('cgmName',baseName)
        i_constraintLinearCurve.addAttr('cgmTypeModifier','constraintLinear')
        i_constraintLinearCurve.doName()

        #Skin it
        i_constraintLinearCurveCluster = cgmMeta.cgmNode(mc.skinCluster ([i_baseParent.mNode,i_endParent.mNode],
                                                                         i_constraintLinearCurve.mNode,
                                                                         tsb=True,
                                                                         maximumInfluences = 1,
                                                                         normalizeWeights = 1,dropoffRate=10.0)[0])

        i_constraintLinearCurveCluster.addAttr('cgmName', baseName)
        i_constraintLinearCurveCluster.addAttr('cgmTypeModifier','constraint', lock=True)
        i_constraintLinearCurveCluster.doName()	



    except Exception,error:
        log.error("addCGMSegmentSubControl>>Curve construction fail!")
        raise StandardError,error 	    

    ml_pointOnCurveInfos = []
    splineShape = mc.listRelatives(i_constraintSplineCurve.mNode,shapes=True)[0]
    linearShape = mc.listRelatives(i_constraintLinearCurve.mNode,shapes=True)[0]

    try:#Make some up locs for the base and end aim
        baseDist = distance.returnDistanceBetweenObjects(i_baseParent.mNode,i_endParent.mNode)/4
        #Start up
        i_upStart = i_baseParent.doCreateAt()
        i_upStart.addAttr('cgmType','midStartAimUp',attrType='string',lock=True)
        i_upStart.doName()
        i_upStart.parent = i_baseParent.mNode  
        attributes.doSetAttr(i_upStart.mNode,'t%s'%orientation[1],baseDist)


        #End up
        i_upEnd = i_endParent.doCreateAt()
        i_upEnd.addAttr('cgmType','midEndAimUp',attrType='string',lock=True)
        i_upEnd.doName()    
        i_upEnd.parent = False    
        i_upEnd.parent = i_endParent.mNode  
        attributes.doSetAttr(i_upEnd.mNode,'t%s'%orientation[1],baseDist)

    except Exception,error:
        log.error("addCGMSegmentSubControl>>Up transforms fail!")
        raise StandardError,error 

    for i,i_obj in enumerate(ml_newJoints):
        if ml_midControls and ml_midControls[i]:#if we have a control curve, use it
            i_control = ml_midControls[i]
        else:#else, connect 
            i_control = i_obj
        try:#>>>Transforms     
            #Create group
            grp = i_obj.doGroup()
            i_followGroup = cgmMeta.asMeta(grp,'cgmObject',setClass=True)
            i_followGroup.addAttr('cgmTypeModifier','follow',lock=True)
            i_followGroup.doName()

            grp = i_obj.doGroup(True)	
            i_orientGroup = cgmMeta.asMeta(grp,'cgmObject',setClass=True)
            i_orientGroup.addAttr('cgmTypeModifier','orient',lock=True)
            i_orientGroup.doName()

            i_obj.parent = False#since stuff is gonna move, we'll parent back at end

            #=============================================================	
            #>>>PointTargets
            #linear follow
            i_linearFollowNull = i_obj.doCreateAt()
            i_linearFollowNull.addAttr('cgmType','linearFollow',attrType='string',lock=True)
            i_linearFollowNull.doName()
            #i_linearFollowNull.parent = i_anchorStart.mNode     
            i_linearPosNull = i_obj.doCreateAt()
            i_linearPosNull.addAttr('cgmType','linearPos',attrType='string',lock=True)
            i_linearPosNull.doName()

            #splineFollow
            i_splineFollowNull = i_obj.doCreateAt()
            i_splineFollowNull.addAttr('cgmType','splineFollow',attrType='string',lock=True)
            i_splineFollowNull.doName()	

            #>>>Orient Targets
            #aimstart
            i_aimStartNull = i_obj.doCreateAt()
            i_aimStartNull.addAttr('cgmType','aimStart',attrType='string',lock=True)
            i_aimStartNull.doName()
            i_aimStartNull.parent = i_followGroup.mNode    

            #aimEnd
            i_aimEndNull = i_obj.doCreateAt()
            i_aimEndNull.addAttr('cgmType','aimEnd',attrType='string',lock=True)
            i_aimEndNull.doName()
            i_aimEndNull.parent = i_followGroup.mNode   


            #>>>Attach 
            #=============================================================
            #>>>Spline
            l_closestInfo = distance.returnNearestPointOnCurveInfo(i_obj.mNode,i_constraintSplineCurve.mNode)
            i_closestSplinePointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
            mc.connectAttr ((splineShape+'.worldSpace'),(i_closestSplinePointNode.mNode+'.inputCurve'))	

            #> Name
            i_closestSplinePointNode.doStore('cgmName',i_obj)
            i_closestSplinePointNode.addAttr('cgmTypeModifier','spline',attrType='string',lock=True)	    
            i_closestSplinePointNode.doName()
            #>Set attachpoint value
            i_closestSplinePointNode.parameter = l_closestInfo['parameter']
            mc.connectAttr ((i_closestSplinePointNode.mNode+'.position'),(i_splineFollowNull.mNode+'.translate'))
            ml_pointOnCurveInfos.append(i_closestSplinePointNode) 

            #>>>Linear
            l_closestInfo = distance.returnNearestPointOnCurveInfo(i_obj.mNode,i_constraintLinearCurve.mNode)
            i_closestLinearPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
            mc.connectAttr ((linearShape+'.worldSpace'),(i_closestLinearPointNode.mNode+'.inputCurve'))	

            #> Name
            i_closestLinearPointNode.doStore('cgmName',i_obj)
            i_closestLinearPointNode.addAttr('cgmTypeModifier','linear',attrType='string',lock=True)	    	    
            i_closestLinearPointNode.doName()
            #>Set attachpoint value
            i_closestLinearPointNode.parameter = l_closestInfo['parameter']
            mc.connectAttr ((i_closestLinearPointNode.mNode+'.position'),(i_linearFollowNull.mNode+'.translate'))
            ml_pointOnCurveInfos.append(i_closestLinearPointNode) 	    
            i_linearPosNull.parent = i_linearFollowNull.mNode#paren the pos obj

        except Exception,error:
            log.error("addCGMSegmentSubControl>>Build transforms fail! | obj: %s"%i_obj.getShortName())
            raise StandardError,error 	

        #=============================================================	
        try:#>>> point Constrain
            cBuffer = mc.pointConstraint([i_splineFollowNull.mNode,i_linearPosNull.mNode],
                                         i_followGroup.mNode,
                                         maintainOffset = True, weight = 1)[0]
            i_pointConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)	

            #Blendsetup
            log.debug("i_pointConstraint: %s"%i_pointConstraint)
            log.debug("i_control: %s"%i_control)

            targetWeights = mc.pointConstraint(i_pointConstraint.mNode,q=True, weightAliasList=True)
            if len(targetWeights)>2:
                raise StandardError,"addCGMSegmentSubControl>>Too many weight targets: obj: %s | weights: %s"%(i_obj.mNode,targetWeights)

            d_midPointBlendReturn = NodeF.createSingleBlendNetwork([i_control.mNode,'linearSplineFollow'],
                                                                   [i_control.mNode,'resultSplineFollow'],
                                                                   [i_control.mNode,'resultLinearFollow'],
                                                                   keyable=True)

            #Connect                                  
            d_midPointBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_pointConstraint.mNode,targetWeights[0]))
            d_midPointBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_pointConstraint.mNode,targetWeights[1]))



        except Exception,error:
            log.error("addCGMSegmentSubControl>>Translate constrain setup fail! | obj: %s"%i_obj.getShortName())
            raise StandardError,error 	

        try:#>>>Aim constraint and blend
            cBuffer = mc.aimConstraint(i_baseParent.mNode,
                                       i_aimStartNull.mNode,
                                       maintainOffset = True, weight = 1,
                                       aimVector = aimVectorNegative,
                                       upVector = upVector,
                                       worldUpObject = i_upStart.mNode,
                                       worldUpType = 'object' )[0]

            i_startAimConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)

            cBuffer = mc.aimConstraint(i_endParent.mNode,
                                       i_aimEndNull.mNode,
                                       maintainOffset = True, weight = 1,
                                       aimVector = aimVector,
                                       upVector = upVector,
                                       worldUpObject = i_upEnd.mNode,
                                       worldUpType = 'object' )[0]

            i_endAimConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)

            cBuffer = mc.orientConstraint([i_aimEndNull.mNode,i_aimStartNull.mNode],
                                          i_orientGroup.mNode,
                                          maintainOffset = False, weight = 1)[0]
            i_orientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode', setClass=True)	
            i_orientConstraint.interpType = 0


            #Blendsetup
            log.debug("i_orientConstraint: %s"%i_orientConstraint)
            log.debug("i_control: %s"%i_control)

            targetWeights = mc.orientConstraint(i_orientConstraint.mNode,q=True, weightAliasList=True)
            if len(targetWeights)>2:
                raise StandardError,"addCGMSegmentSubControl>>Too many weight targets: obj: %s | weights: %s"%(i_obj.mNode,targetWeights)

            d_midOrientBlendReturn = NodeF.createSingleBlendNetwork([i_control.mNode,'startEndAim'],
                                                                    [i_control.mNode,'resultEndAim'],
                                                                    [i_control.mNode,'resultStartAim'],
                                                                    keyable=True)

            #Connect                                  
            d_midOrientBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_orientConstraint.mNode,targetWeights[0]))
            d_midOrientBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_orientConstraint.mNode,targetWeights[1]))



        except Exception,error:
            log.error("addCGMSegmentSubControl>>Orient constrain setup fail! | obj: %s"%i_obj.getShortName())
            raise StandardError,error 	

        try:#Skincluster work
            if i_segmentCurveSkinCluster:
                mc.skinCluster(i_segmentCurveSkinCluster.mNode,edit=True,ai=i_obj.mNode,dropoffRate = 2.5)
                #Smooth the weights
                controlCurveTightenEndWeights(i_segmentCurve.mNode,i_baseParent.mNode,i_endParent.mNode,2)	
        except Exception,error:
            log.error("addCGMSegmentSubControl>>Skincluster fix fail! | curve: %s"%i_segmentCurve.getShortName())
            raise StandardError,error 

        try:
            if addTwist:#>>>Add Twist
                if not i_segmentCurve:
                    raise StandardError,"addCGMSegmentSubControl>>Cannot add twist without a segmentCurve"
                if not i_segmentCurve.getMessage('drivenJoints'):
                    raise StandardError,"addCGMSegmentSubControl>>Cannot add twist stored bind joint info on segmentCurve: %s"%i_segmentCurve.getShortName()		    

                ml_drivenJoints = i_segmentCurve.msgList_get('drivenJoints',asMeta = True)

                closestJoint = distance.returnClosestObject(i_obj.mNode,[i_jnt.mNode for i_jnt in ml_drivenJoints])
                upLoc = cgmMeta.cgmObject(closestJoint).rotateUpGroup.upLoc.mNode
                i_rotateUpGroup = cgmMeta.cgmObject(closestJoint).rotateUpGroup
                #Twist setup start
                #grab driver
                driverNodeAttr = attributes.returnDriverAttribute("%s.%s"%(i_rotateUpGroup.mNode,rotateGroupAxis),True)    
                #get driven
                rotDriven = attributes.returnDrivenAttribute(driverNodeAttr,True)

                rotPlug = attributes.doBreakConnection(i_rotateUpGroup.mNode,
                                                       rotateGroupAxis)

                #Get the driven so that we can bridge to them 
                log.debug("midFollow...")   
                log.debug("rotPlug: %s"%rotPlug)
                log.debug("aimVector: '%s'"%aimVector)
                log.debug("upVector: '%s'"%upVector)    
                log.debug("upLoc: '%s'"%upLoc)
                log.debug("rotDriven: '%s'"%rotDriven)

                #>>>Twist setup 
                #Connect To follow group
                #attributes.doConnectAttr(rotPlug,"%s.r%s"%(i_midFollowGrp.mNode,
                    #                                          self._jointOrientation[0]))

                #Create the add node
                i_pmaAdd = NodeF.createAverageNode([driverNodeAttr,
                                                    "%s.r%s"%(i_control.mNode,#mid handle
                                                              orientation[0])],
                                                   operation=1)
                for a in rotDriven:#BridgeBack
                    attributes.doConnectAttr("%s.output1D"%i_pmaAdd.mNode,a)	    
        except Exception,error:
            log.error("addCGMSegmentSubControl>>Add twist fail! | obj: %s"%i_obj.getShortName())
            raise StandardError,error 	

        #Parent at very end to keep the joint from moving

        if i_control != i_obj:#Parent our control if we have one
            i_control.parent = i_orientGroup.mNode
            i_control.doGroup(True)
            mc.makeIdentity(i_control.mNode, apply=True,t=1,r=0,s=1,n=0)
            i_obj.parent = i_control.mNode
        else:
            i_obj.parent = i_orientGroup.mNode

        #Parent pieces
        i_segmentCurve.parent = i_segmentGroup.mNode	
        i_constraintLinearCurve.parent = i_segmentGroup.mNode
        i_constraintSplineCurve.parent = i_segmentGroup.mNode
        i_linearFollowNull.parent = i_segmentGroup.mNode	
        i_splineFollowNull.parent = i_segmentGroup.mNode

        return {'ml_followGroups':[i_followGroup]}


#@cgmGeneral.Timer
def createCGMSegment(jointList, influenceJoints = None, addSquashStretch = True, addTwist = True,
                     startControl = None, endControl = None, segmentType = 'curve',
                     rotateGroupAxis = 'rotateZ',secondaryAxis = None,
                     baseName = None, advancedTwistSetup = False, additiveScaleSetup = False,connectAdditiveScale = False,
                     orientation = 'zyx',controlOrientation = None, moduleInstance = None):
    """
    CGM Joint Segment setup.
    Inspiriation from Jason Schleifer's work as well as http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
    on twist methods.

    The general idea is a joint chain with a start control and and end control. Full twist, squash and stretch, additive scale ability

    :parameters:
        jointList(list) | jointList of joints to setup
        influenceJoints(list) | influence joints for setup segment
        addSquashStretch(bool) | whether to setup squash and stretch in the segment
        addTwist(bool)| whether tto setup extra twist control
        startControl(inst/str) | start control object
        startControl(inst/str) | end control object
        segmentType(str) | currently only support 'curve' type.
        rotateGroupAxis(str) | the rotate axis of the rotate group for a twist setup
        secondaryAxis(arg) | pass through command for other functions
        baseName(str) | basename for various naming
        advancedTwistSetup(bool) | pass through command to createCurveSegment
        additiveScaleSetup(bool) | whether to setup additive scale
        connectAdditiveScale(bool) |whether to connect additive scale
        orientation(str) | joint orientation
        controlOrientation(str) |control orientation. Important as it sets which channels will drive twist and additive scale
        moduleInstance(arg) | 
    :returns:
        Dict ------------------------------------------------------------------
    'mi_anchorStart'
    'mi_anchorStart'
    'mi_anchorEnd'
    'mPlug_extendTwist'
    'mi_constraintStartAim'
    'mi_constraintEndAim'
    'mi_endAimConstraint'
    'mi_segmentCurve'(cgmObject) | segment curve
    'segmentCurve'(str) | segment curve string
    'mi_ikHandle'(cgmObject) | spline ik Handle
    'mi_segmentGroup'(cgmObject) | segment group containing most of the guts
    'l_driverJoints'(list) | list of string driver joint names
    'ml_driverJoints'(metalist) | cgmObject instances of driver joints
    'scaleBuffer'(str) | scale buffer node
    'mi_scaleBuffer'(cgmBufferNode) | scale buffer node for the setup
    'mPlug_extendTwist'(cgmAttr) | extend twist attribute instance
    'l_drivenJoints'(list) | list of string driven joint names
    'ml_drivenJoints'(metalist) | cgmObject instances of driven joints

    :raises:
    Exception | if reached

    """      
    _str_funcName = 'createCGMSegment'
    log.info(">>> %s >> "%_str_funcName + "="*75)   

    if segmentType != 'curve':
        raise NotImplementedError,"createCGMSegment>>>Haven't implemented segmentType: %s"%segmentType
    try:#Gather data =====================================================================================
        #> start/end control -------------------------------------------------------------        
        i_startControl = cgmMeta.validateObjArg(startControl,cgmMeta.cgmObject,noneValid=True)
        i_endControl = cgmMeta.validateObjArg(endControl,cgmMeta.cgmObject,noneValid=True)

        #> joints -------------------------------------------------------------
        if type(jointList) not in [list,tuple]:jointList = [jointList]
        if len(jointList)<3:
            raise StandardError,"createCGMSegment>>> needs at least three joints"

        ml_influenceJoints = cgmMeta.validateObjListArg(influenceJoints,cgmMeta.cgmObject,noneValid=False,mayaType=['nurbsCurve','joint'])

        try:ml_jointList = cgmMeta.validateObjListArg(jointList,cgmMeta.cgmObject,noneValid=False,mayaType=['nurbsCurve','joint'])
        except Exception,error:
            raise StandardError,"%s >>Joint metaclassing | error : %s"%(_str_funcName,error)

        #> module -------------------------------------------------------------
        i_module = False
        if i_module:
            if baseName is None: baseName = i_module.getPartNameBase()#Get part base name	    
        if baseName is None:baseName = 'testSegment'

        log.debug('i_startControl: %s'%i_startControl)
        log.debug('i_endControl: %s'%i_endControl)
        log.debug('ml_influenceJoints: %s'%ml_influenceJoints)
        log.debug('i_module: %s'%i_module)
        log.debug("baseName: %s"%baseName)  

        #Good way to verify an instance list? #validate orientation
        #Gather info
        if controlOrientation is None:
            controlOrientation = orientation   

        #> axis -------------------------------------------------------------
        axis_aim = cgmValid.simpleAxis("%s+"%orientation[0])
        axis_aimNeg = cgmValid.simpleAxis("%s-"%orientation[0])
        axis_up = cgmValid.simpleAxis("%s+"%orientation[0])

        aimVector = axis_aim.p_vector
        aimVectorNegative = axis_aimNeg.p_vector
        upVector = axis_up.p_vector   

        outChannel = orientation[2]
        upChannel = '%sup'%orientation[1]

        #> baseDistance -------------------------------------------------------------
        baseDist = distance.returnDistanceBetweenObjects(ml_jointList[0].mNode,ml_jointList[-1].mNode)/2        

    except Exception,error:
        raise StandardError,"%s >> data gather | error: %s"%(_str_funcName,error)  

    try:#>>> Module instance =====================================================================================
        i_module = False
        try:
            if moduleInstance is not None:
                if moduleInstance.isModule():
                    i_module = moduleInstance    
                    log.info("%s >> module instance found: %s"%(_str_funcName,i_module.p_nameShort))		
        except:pass
    except Exception,error:
        raise StandardError,"%s >> Module check fail! | error: %s"%(_str_funcName,error)    

    try:#Build Transforms =====================================================================================
        #Start Anchor
        i_anchorStart = ml_jointList[0].doCreateAt()
        i_anchorStart.addAttr('cgmType','anchor',attrType='string',lock=True)
        i_anchorStart.doName()
        i_anchorStart.parent = False  


        #End Anchor
        i_anchorEnd = ml_jointList[-1].doCreateAt()
        i_anchorEnd.addAttr('cgmType','anchor',attrType='string',lock=True)
        i_anchorEnd.doName()    
        i_anchorEnd.parent = False

        #if not i_startControl:i_startControl = i_anchorStart
        #if not i_endControl:i_endControl = i_anchorEnd

        #Build locs
        #=======================================================================================    
        ml_rigObjects = []
        #>>>Aims
        #Start Aim
        i_aimStartNull = ml_jointList[0].doCreateAt()
        i_aimStartNull.addAttr('cgmType','aim',attrType='string',lock=True)
        i_aimStartNull.doName()
        i_aimStartNull.parent = i_anchorStart.mNode   
        i_aimStartNull.rotateOrder = 0

        #End Aim
        i_aimEndNull = ml_jointList[-1].doCreateAt()
        i_aimEndNull.addAttr('cgmType','aim',attrType='string',lock=True)
        i_aimEndNull.doName()
        i_aimEndNull.parent = i_anchorEnd.mNode 
        i_aimEndNull.rotateOrder = 0

        #=====================================
        """
	if addTwist:
	    #>>>Twist loc
	    #Start Aim
	    i_twistStartNull = ml_jointList[0].doCreateAt()
	    i_twistStartNull.addAttr('cgmType','twist',attrType='string',lock=True)
	    i_twistStartNull.doName()
	    i_twistStartNull.parent = i_anchorStart.mNode     
	    ml_rigObjects.append(i_twistStartNull)

	    #End Aim
	    i_twistEndNull = ml_jointList[-1].doCreateAt()
	    i_twistEndNull.addAttr('cgmType','twist',attrType='string',lock=True)
	    i_twistEndNull.doName()
	    i_twistEndNull.parent = i_anchorEnd.mNode  
	    ml_rigObjects.append(i_twistEndNull)"""

        #=====================================	
        #>>>Attach
        #Start Attach
        i_attachStartNull = ml_jointList[0].doCreateAt()
        i_attachStartNull.addAttr('cgmType','attach',attrType='string',lock=True)
        i_attachStartNull.doName()
        i_attachStartNull.parent = i_anchorStart.mNode     

        #End Attach
        i_attachEndNull = ml_jointList[-1].doCreateAt()
        i_attachEndNull.addAttr('cgmType','attach',attrType='string',lock=True)
        i_attachEndNull.doName()
        i_attachEndNull.parent = i_anchorEnd.mNode  

        #=====================================	
        #>>>Up locs
        i_startUpNull = ml_jointList[0].doCreateAt()
        i_startUpNull.parent = i_anchorStart.mNode  
        i_startUpNull.addAttr('cgmType','up',attrType='string',lock=True)
        i_startUpNull.doName()
        ml_rigObjects.append(i_startUpNull)
        attributes.doSetAttr(i_startUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

        #End
        i_endUpNull = ml_jointList[-1].doCreateAt()
        i_endUpNull.parent = i_anchorEnd.mNode     	
        i_endUpNull.addAttr('cgmType','up',attrType='string',lock=True)
        i_endUpNull.doName()
        ml_rigObjects.append(i_endUpNull)
        attributes.doSetAttr(i_endUpNull.mNode,'t%s'%orientation[2],baseDist)#We're gonna push these out

        """"
	#Make our endorient fix
	i_endUpOrientNull = i_anchorEnd.doDuplicateTransform(True)
	i_endUpOrientNull.parent = i_anchorEnd.mNode
	i_endUpOrientNull.addAttr('cgmType','upOrient',attrType='string',lock=True)
	i_endUpOrientNull.doName()
	i_endUpNull.parent = i_endUpOrientNull.mNode   
	mc.orientConstraint(i_anchorStart.mNode,i_endUpOrientNull.mNode,maintainOffset = True, skip = [axis for axis in orientation[:-1]])
	"""
        #Parent the influenceJoints
        ml_influenceJoints[0].parent = i_attachStartNull.mNode
        ml_influenceJoints[-1].parent = i_attachEndNull.mNode


        #Start Aim Target
        i_aimStartTargetNull = ml_jointList[-1].doCreateAt()
        i_aimStartTargetNull.addAttr('cgmType','aimTargetStart',attrType='string',lock=True)
        i_aimStartTargetNull.doName()
        i_aimStartTargetNull.parent = ml_influenceJoints[-1].mNode     
        ml_rigObjects.append(i_aimStartTargetNull)

        #End AimTarget
        i_aimEndTargetNull = ml_jointList[0].doCreateAt()
        i_aimEndTargetNull.addAttr('cgmType','aimTargetEnd',attrType='string',lock=True)
        i_aimEndTargetNull.doName()
        i_aimEndTargetNull.parent = ml_influenceJoints[0].mNode  
        ml_rigObjects.append(i_aimEndTargetNull)

        if i_startControl and not i_startControl.parent:
            i_startControl.parent = i_attachStartNull.mNode
            i_startControl.doGroup(True)
            mc.makeIdentity(i_startControl.mNode, apply=True,t=1,r=0,s=1,n=0)

            ml_influenceJoints[0].parent = i_startControl.mNode

        if i_endControl and not i_endControl.parent:
            i_endControl.parent = i_attachEndNull.mNode
            i_endControl.doGroup(True)
            mc.makeIdentity(i_endControl.mNode, apply=True,t=1,r=0,s=1,n=0)	    
            ml_influenceJoints[-1].parent = i_endControl.mNode

        """
	if i_module:#if we have a module, connect vis
	    for i_obj in ml_rigObjects:
		i_obj.overrideEnabled = 1		
		cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideVisibility'))
		cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideDisplayType'))    
		"""
    except Exception,error:
        log.error("createCGMSegment>>Joint anchor and loc build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Constrain Nulls =====================================================================================
        cBuffer = mc.orientConstraint([i_anchorStart.mNode,i_aimStartNull.mNode],
                                      i_attachStartNull.mNode,
                                      maintainOffset = True, weight = 1)[0]
        i_startOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)
        i_startOrientConstraint.interpType = 0

        cBuffer = mc.orientConstraint([i_anchorEnd.mNode,i_aimEndNull.mNode],
                                      i_attachEndNull.mNode,
                                      maintainOffset = True, weight = 1)[0]
        i_endOrientConstraint = cgmMeta.asMeta(cBuffer,'cgmNode',setClass=True)
        i_endOrientConstraint.interpType = 0


    except Exception,error:
        log.error("createCGMSegment>>Constrain locs build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Build constraint blend =====================================================================================
        #If we don't have our controls by this point, we'll use the joints
        if not i_startControl:
            i_startControl = ml_influenceJoints[0]
        if not i_endControl:
            i_endControl = ml_influenceJoints[-1]

        #start blend
        d_startFollowBlendReturn = NodeF.createSingleBlendNetwork([i_startControl.mNode,'followRoot'],
                                                                  [i_startControl.mNode,'resultRootFollow'],
                                                                  [i_startControl.mNode,'resultAimFollow'],
                                                                  keyable=True)
        targetWeights = mc.orientConstraint(i_startOrientConstraint.mNode,q=True, weightAliasList=True)
        #Connect                                  
        d_startFollowBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_startOrientConstraint.mNode,targetWeights[0]))
        d_startFollowBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_startOrientConstraint.mNode,targetWeights[1]))
        d_startFollowBlendReturn['d_result1']['mi_plug'].p_hidden = True
        d_startFollowBlendReturn['d_result2']['mi_plug'].p_hidden = True

        #EndBlend
        d_endFollowBlendReturn = NodeF.createSingleBlendNetwork([i_endControl.mNode,'followRoot'],
                                                                [i_endControl.mNode,'resultRootFollow'],
                                                                [i_endControl.mNode,'resultAimFollow'],
                                                                keyable=True)
        targetWeights = mc.orientConstraint(i_endOrientConstraint.mNode,q=True, weightAliasList=True)
        #Connect                                  
        d_endFollowBlendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_endOrientConstraint.mNode,targetWeights[0]))
        d_endFollowBlendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_endOrientConstraint.mNode,targetWeights[1]))
        d_endFollowBlendReturn['d_result1']['mi_plug'].p_hidden = True
        d_endFollowBlendReturn['d_result2']['mi_plug'].p_hidden = True

    except Exception,error:
        log.error("createCGMSegment>>Constrain locs build fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Build segment =====================================================================================
        try:
            d_segmentBuild = createSegmentCurve(jointList, orientation = orientation,secondaryAxis = secondaryAxis, baseName = baseName,connectBy = 'scale',
                                                addMidTwist=True, advancedTwistSetup = advancedTwistSetup, moduleInstance = moduleInstance)

            mi_segmentCurve = d_segmentBuild['mi_segmentCurve']
            ml_drivenJoints = d_segmentBuild['ml_drivenJoints']
            mi_scaleBuffer = d_segmentBuild['mi_scaleBuffer']
            mi_segmentGroup = d_segmentBuild['mi_segmentGroup']
            mPlug_extendTwist = d_segmentBuild['mPlug_extendTwist']
        except Exception,error:raise Exception,"[Initial Segment build]{%s}"%error

        log.info("addSquashStretch: %s"%addSquashStretch)
        try:#Add squash
            if addSquashStretch:
                log.info("ADD SQUASH")
                addSquashAndStretchToSegmentCurveSetup(mi_scaleBuffer.mNode,
                                                       [i_jnt.mNode for i_jnt in ml_jointList],
                                                       moduleInstance=moduleInstance)
        except Exception,error:raise Exception,"[Add squash]{%s}"%error

        try:#Additive Scale 
            if additiveScaleSetup:
                log.info('additiveScaleSetup...')
                addAdditiveScaleToSegmentCurveSetup(mi_segmentCurve.mNode,orientation=orientation)
                log.info('additiveScaleSetup done...')

                if connectAdditiveScale:
                    l_plugs = ['scaleStartUp','scaleStartOut','scaleEndUp','scaleEndOut']
                    for attr in l_plugs: 
                        log.info(attr)
                        if not mi_segmentCurve.hasAttr(attr):
                            mi_segmentCurve.select()
                            raise StandardError, "Segment curve missing attr: %s"%attr

                    l_attrPrefix = ['Start','End']
                    int_runningTally = 0
                    for i,i_ctrl in enumerate([i_startControl,i_endControl]):
                        log.info("{0} | {1}".format(i,i_ctrl.p_nameShort))
                        mPlug_outDriver = cgmMeta.cgmAttr(i_ctrl,"s%s"%controlOrientation[2])
                        mPlug_upDriver = cgmMeta.cgmAttr(i_ctrl,"s%s"%controlOrientation[1])
                        mPlug_scaleOutDriver = cgmMeta.cgmAttr(i_ctrl,"out_scale%sOutNormal"%l_attrPrefix[i],attrType='float')
                        mPlug_scaleUpDriver = cgmMeta.cgmAttr(i_ctrl,"out_scale%sUpNormal"%l_attrPrefix[i],attrType='float')
                        mPlug_out_scaleUp = cgmMeta.cgmAttr(i_ctrl,"out_scale%sOutInv"%l_attrPrefix[i],attrType='float')
                        mPlug_out_scaleOut = cgmMeta.cgmAttr(i_ctrl,"out_scale%sUpInv"%l_attrPrefix[i],attrType='float')	
                        # -1 * (1 - driver)
                        arg_up1 = "%s = 1 - %s"%(mPlug_scaleUpDriver.p_combinedShortName,mPlug_upDriver.p_combinedShortName)
                        arg_out1 = "%s = 1 - %s"%(mPlug_scaleOutDriver.p_combinedShortName,mPlug_outDriver.p_combinedShortName)
                        arg_up2 = "%s = -1 * %s"%(mPlug_out_scaleUp.p_combinedShortName,mPlug_scaleUpDriver.p_combinedShortName)
                        arg_out2 = "%s = -1 * %s"%(mPlug_out_scaleOut.p_combinedShortName,mPlug_scaleOutDriver.p_combinedShortName)
                        for arg in [arg_up1,arg_out1,arg_up2,arg_out2]:
                            try:
                                NodeF.argsToNodes(arg).doBuild()
                            except Exception,err:
                                raise Exception,"arg fail {0} | error: {1}".format(arg,err)

                        mPlug_out_scaleUp.doConnectOut("%s.%s"%(mi_segmentCurve.mNode,l_plugs[int_runningTally]))
                        int_runningTally+=1
                        mPlug_out_scaleOut.doConnectOut("%s.%s"%(mi_segmentCurve.mNode,l_plugs[int_runningTally]))	    
                        int_runningTally+=1
        except Exception,error:
            raise Exception,"[Additive scale]{%s}"%error

        try:#Twist
            if addTwist:
                i_twistStartPlug = cgmMeta.cgmAttr(mi_segmentCurve.mNode,'twistStart',attrType='float',keyable=True) 
                i_twistEndPlug = cgmMeta.cgmAttr(mi_segmentCurve.mNode,'twistEnd',attrType='float',keyable=True)
                capAim = orientation[0].capitalize()
                """
		log.debug("capAim: %s"%capAim)
		d_twistReturn = addRibbonTwistToControlSetup([i_jnt.mNode for i_jnt in ml_jointList],
							     [i_twistStartPlug.obj.mNode,i_twistStartPlug.attr],
							     [i_twistEndPlug.obj.mNode,i_twistEndPlug.attr],moduleInstance=moduleInstance) 

		#Connect resulting full sum to our last spline IK joint to get it's twist
		attributes.doConnectAttr(i_twistEndPlug.p_combinedName,"%s.rotate%s"%(ml_drivenJoints[-1].mNode,capAim))
		"""	    
                if i_startControl:
                    if controlOrientation is None:
                        i_twistStartPlug.doConnectIn("%s.rotate%s"%(i_startControl.mNode,capAim))
                    else:
                        i_twistStartPlug.doConnectIn("%s.r%s"%(i_startControl.mNode,controlOrientation[0]))
                if i_endControl:
                    if controlOrientation is None:		
                        i_twistEndPlug.doConnectIn("%s.rotate%s"%(i_endControl.mNode,capAim))
                    else:
                        i_twistEndPlug.doConnectIn("%s.r%s"%(i_endControl.mNode,controlOrientation[0]))
        except Exception,error:raise Exception,"[Twist]{%s}"%error


    except Exception,error:
        log.error("createCGMSegment>>Build segment fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error     

    try:#Skin curve =====================================================================================    
        if ml_influenceJoints:#if we have influence joints, we're gonna skin our curve
            #Surface influence joints cluster#
            i_controlSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in ml_influenceJoints],
                                                                      mi_segmentCurve.mNode,
                                                                      tsb=True,
                                                                      maximumInfluences = 3,
                                                                      normalizeWeights = 1,dropoffRate=2.5)[0])

            i_controlSurfaceCluster.addAttr('cgmName', baseName, lock=True)
            i_controlSurfaceCluster.addAttr('cgmTypeModifier','segmentCurve', lock=True)
            i_controlSurfaceCluster.doName()
            """
	    if len(ml_influenceJoints) == 2:
		controlCurveSkinningTwoJointBlend(mi_segmentCurve.mNode,start = ml_influenceJoints[0].mNode,
		                                  end = ml_influenceJoints[-1].mNode,tightLength=1,
		                                  blendLength = int(len(jointList)/2))"""

    except Exception,error:
        log.error("createCGMSegment>>Build segment fail! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error 

    try:#Mid influence objects =====================================================================================   
        ml_midObjects = ml_influenceJoints[1:-1] or []
        if len(ml_midObjects)>1:
            raise NotImplementedError,"createCGMSegment>>Haven't implemented having more than one mid influence object in a single chain yet!"
        if ml_midObjects:
            #Create a dup constraint curve
            i_constraintCurve = mi_segmentCurve.doDuplicate(po = True)
            i_constraintCurve.addAttr('cgmTypeModifier','constraint')

            #Skin it

            for i_obj in ml_midObjects:
                pass
                #Create group
                #i_midInfluenceGroup = 
                #Attach
                #Make aim groups since one will be aiming backwards
                #Aim
                #AimBlend

    except Exception,error:
        log.error("createCGMSegment>>Extra Influence Object Setup Fail! %s"%[i_obj.getShortName() for i_obj in ml_influenceJoints])
        raise StandardError,error  

    try:#Aim constraints =====================================================================================
        #startAimTarget = i_aimStartTargetNull.mNode
        #endAimTarget = i_aimEndTargetNull.mNode
        startAimTarget = i_anchorEnd.mNode
        endAimTarget = i_anchorStart.mNode	
        cBuffer = mc.aimConstraint(startAimTarget,
                                   i_aimStartNull.mNode,
                                   maintainOffset = True, weight = 1,
                                   aimVector = aimVector,
                                   upVector = upVector,
                                   worldUpObject = i_startUpNull.mNode,
                                   worldUpType = 'object' ) 
        i_startAimConstraint = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)

        cBuffer = mc.aimConstraint(endAimTarget,
                                   i_aimEndNull.mNode,
                                   maintainOffset = True, weight = 1,
                                   aimVector = aimVectorNegative,
                                   upVector = upVector,
                                   worldUpObject = i_endUpNull.mNode,
                                   worldUpType = 'object' ) 
        i_endAimConstraint = cgmMeta.asMeta(cBuffer[0],'cgmNode',setClass=True)  

    except Exception,error:
        log.error("createCGMSegment>>Build aim constraints! | start joint: %s"%ml_jointList[0].getShortName())
        raise StandardError,error   

    try:#Store some necessary info to the segment curve =====================================================================================
        mi_segmentCurve.connectChildNode(i_anchorStart,'anchorStart','segmentCurve')
        mi_segmentCurve.connectChildNode(i_anchorEnd,'anchorEnd','segmentCurve')
        mi_segmentCurve.connectChildNode(i_attachStartNull,'attachStart','segmentCurve')
        mi_segmentCurve.connectChildNode(i_attachEndNull,'attachEnd','segmentCurve')

    except Exception,error:
        log.error("createCGMSegment>>Info storage fail! |  error: {0}".format(error))

    try:#Return ========================================================================================
        md_return = {'mi_segmentCurve':mi_segmentCurve,'mi_anchorStart':i_anchorStart,'mi_anchorEnd':i_anchorEnd,'mPlug_extendTwist':mPlug_extendTwist,
                     'mi_constraintStartAim':i_startAimConstraint,'mi_constraintEndAim':i_endAimConstraint}
        for k in d_segmentBuild.keys():
            if k not in md_return.keys():
                md_return[k] = d_segmentBuild[k]#...push to the return dict
        return md_return
    except Exception,error:
        log.error("createCGMSegment>>return fail| error: {0}".format(error))


def controlSurfaceSmoothWeights(controlSurface,start = None, end = None):
    """Weight fixer for surfaces"""
    if issubclass(type(controlSurface),cgmMeta.cgmNode):
        i_surface = controlSurface
    elif mc.objExists(controlSurface):
        i_surface = cgmMeta.cgmNode(controlSurface)
    else:
        raise StandardError,"controlSurfaceSmoothWeights failed. Surface doesn't exist: '%s'"%controlSurface

    l_cvs = i_surface.getComponents('cv')
    l_skinClusters = deformers.returnObjectDeformers(i_surface.mNode,deformerTypes = 'skinCluster')
    i_skinCluster = cgmMeta.cgmNode(l_skinClusters[0])
    l_influenceObjects = skinning.queryInfluences(i_skinCluster.mNode) or []

    log.debug("l_skinClusters: '%s'"%l_skinClusters)
    log.debug("i_skinCluster: '%s'"%i_skinCluster)
    log.debug("l_influenceObjects: '%s'"%l_influenceObjects)

    if not i_skinCluster and l_influenceObjects:
        raise StandardError,"controlSurfaceSmoothWeights failed. Not enough info found"

    cvStarts = [int(cv[-5]) for cv in l_cvs]
    cvEnds = [int(cv[-2]) for cv in l_cvs]

    cvStarts = lists.returnListNoDuplicates(cvStarts)
    cvEnds = lists.returnListNoDuplicates(cvEnds)
    log.debug(cvStarts)
    log.debug(cvEnds)  

    #if len{cvEnds)<4:
        #raise StandardError,"Must have enough cvEnds. cvEnds: %s"%(cvEnds)
    if len(cvEnds)<(blendLength + 2):
        raise StandardError,"Must have enough cvEnds. blendLength: %s"%(blendLength)	

    blendFactor = 1 * ((2+1)*.1)
    log.debug("blendFactor: %s"%blendFactor)

    #>>>Tie down tart and ends
    for influence in [start,end]:
        if influence == start:
            cvBlendEnds = cvEnds[:blendLength+2]
            log.debug("%s: %s"%(influence,cvBlendEnds))
        if influence == end:
            cvBlendEnds = cvEnds[-(blendLength+2):]
            cvBlendEnds.reverse()
            log.debug("%s: %s"%(influence,cvBlendEnds))
        for i,endInt in enumerate(cvBlendEnds):
            if i in [0,1]:
                for startInt in cvStarts:
                    mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s][%s]"%(i_surface.mNode,startInt,endInt)), tv = [influence,1])

            for startInt in cvStarts:
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s][%s]"%(i_surface.mNode,startInt,endInt)),
                               tv = [influence,1-(i*blendFactor)])


def controlCurveSkinningTwoJointBlend(curve,start = None, end = None, tightLength = 1, blendLength = None):
    """Weight fixer for curves"""
    if issubclass(type(curve),cgmMeta.cgmNode):
        i_curve = curve
    elif mc.objExists(curve):
        i_curve = cgmMeta.cgmNode(curve)
    else:
        raise StandardError,"curveSmoothWeights failed. Surface doesn't exist: '%s'"%curve

    l_cvs = i_curve.getComponents('cv')
    l_skinClusters = deformers.returnObjectDeformers(i_curve.mNode,deformerTypes = 'skinCluster')
    i_skinCluster = cgmMeta.cgmNode(l_skinClusters[0])
    l_influenceObjects = skinning.queryInfluences(i_skinCluster.mNode) or []

    log.debug("l_skinClusters: '%s'"%l_skinClusters)
    log.debug("i_skinCluster: '%s'"%i_skinCluster)
    log.debug("l_influenceObjects: '%s'"%l_influenceObjects)

    if not i_skinCluster and l_influenceObjects:
        raise StandardError,"curveSmoothWeights failed. Not enough info found"

    l_cvInts = [int(cv[-2]) for cv in l_cvs]
    l_cvInts = lists.returnListNoDuplicates(l_cvInts)

    if blendLength is None:
        blendFactor = 1/ float(len(l_cvInts[tightLength:-tightLength])+1)
    else:
        blendFactor = 1/ float(len(l_cvInts[tightLength:-tightLength])+(blendLength+1))

    #( len(l_cvInts[tightLength:-tightLength] )*.5)

    log.debug("blendFactor: %s "%blendFactor)

    #>>>Tie down tart and ends
    for influence in [start,end]:
        log.debug("Influence: %s"%influence)
        if influence == start:
            cvBlendRange = l_cvInts[tightLength:-tightLength]
            log.debug("%s: %s"%(influence,cvBlendRange))
            for cv in l_cvInts[:tightLength]:
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s]"%(i_curve.mNode,cv)), tv = [influence,1])

        if influence == end:
            cvBlendRange = l_cvInts[tightLength:-tightLength]
            cvBlendRange.reverse()
            log.debug("%s: %s"%(influence,cvBlendRange))
            for cv in l_cvInts[-tightLength:]:
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s]"%(i_curve.mNode,cv)), tv = [influence,1])

        if blendLength:	
            for i,cv in enumerate(cvBlendRange[:blendLength]):
                log.debug("cv: %s | blendFactor: %s"%(cv,1 - ((i+1)*blendFactor)))
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s]"%(i_curve.mNode,cv)),
                               tv = [influence,1-((i+1)*blendFactor)])	    
        else:
            for i,cv in enumerate(cvBlendRange):
                log.debug("cv: %s | blendFactor: %s"%(cv,1 - ((i+1)*blendFactor)))
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s]"%(i_curve.mNode,cv)),
                               tv = [influence,1-((i+1)*blendFactor)])

def controlCurveTightenEndWeights(curve,start = None, end = None, blendLength = 2):
    """Weight fixer for curves"""
    if issubclass(type(curve),cgmMeta.cgmNode):
        i_curve = curve
    elif mc.objExists(curve):
        i_curve = cgmMeta.cgmNode(curve)
    else:
        raise StandardError,"curveSmoothWeights failed. Surface doesn't exist: '%s'"%curve

    l_cvs = i_curve.getComponents('cv')
    l_skinClusters = deformers.returnObjectDeformers(i_curve.mNode,deformerTypes = 'skinCluster')
    i_skinCluster = cgmMeta.cgmNode(l_skinClusters[0])
    l_influenceObjects = skinning.queryInfluences(i_skinCluster.mNode) or []

    log.debug("l_skinClusters: '%s'"%l_skinClusters)
    log.debug("i_skinCluster: '%s'"%i_skinCluster)
    log.debug("l_influenceObjects: '%s'"%l_influenceObjects)

    if not i_skinCluster and l_influenceObjects:
        raise StandardError,"curveSmoothWeights failed. Not enough info found"

    l_cvInts = [int(cv[-2]) for cv in l_cvs]

    l_cvInts = lists.returnListNoDuplicates(l_cvInts)

    #if len{cvEnds)<4:
        #raise StandardError,"Must have enough cvEnds. cvEnds: %s"%(cvEnds)
    if len(l_cvInts)<(blendLength + 2):
        raise StandardError,"Must have enough cvEnds. blendLength: %s"%(blendLength)	

    blendFactor = 1 * ((blendLength+1)*.1)
    log.debug("blendFactor: %s"%blendFactor)

    #>>>Tie down tart and ends
    for influence in [start,end]:
        log.debug("Influence: %s"%influence)
        if influence == start:
            cvBlendRange = l_cvInts[:blendLength+2]
            log.debug("%s: %s"%(influence,cvBlendRange))
        if influence == end:
            cvBlendRange = l_cvInts[-(blendLength+2):]
            cvBlendRange.reverse()
            log.debug("%s: %s"%(influence,cvBlendRange))
        for i,cv in enumerate(cvBlendRange):
            if i in [0,1]:
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s]"%(i_curve.mNode,cv)), tv = [influence,1])

            else:
                mc.skinPercent(i_skinCluster.mNode,("%s.cv[%s]"%(i_curve.mNode,cv)),
                               tv = [influence,1-(i*blendFactor)])

def createSegmentCurve(*args,**kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        """
        Root of the segment setup.
        Inspiriation from Jason Schleifer's work as well as http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
        on twist methods.

        :parameters:
            0 - 'jointList'(joints - None) | List or metalist of joints
            1 - 'useCurve'(nurbsCurve - None) | Which curve to use. If None. One Created
            2 - 'orientation'(string - zyx) | What is the joints orientation
            3 - 'secondaryAxis'(maya axis arg(ex:'yup') - yup) | Only necessary when no module provide for orientating
            4 - 'baseName'(string - None) | baseName string
            5 - 'connectBy'(string - trans) | How the joint will scale
            6 - 'advancedTwistSetup'(bool - False) | Whether to do the cgm advnaced twist setup
            7 - 'addMidTwist'(bool - True) | Whether to setup a mid twist on the segment
            8 - 'moduleInstance'(cgmModule - None) | cgmModule to use for connecting on build
            9 - 'extendTwistToEnd'(bool - False) | Whether to extned the twist to the end by default

        :returns:
            Dict ------------------------------------------------------------------
            'mi_segmentCurve'(cgmObject) | segment curve
            'segmentCurve'(str) | segment curve string
            'mi_ikHandle'(cgmObject) | spline ik Handle
            'mi_segmentGroup'(cgmObject) | segment group containing most of the guts
            'l_driverJoints'(list) | list of string driver joint names
            'ml_driverJoints'(metalist) | cgmObject instances of driver joints
            'scaleBuffer'(str) | scale buffer node
            'mi_scaleBuffer'(cgmBufferNode) | scale buffer node for the setup
            'mPlug_extendTwist'(cgmAttr) | extend twist attribute instance
            'l_drivenJoints'(list) | list of string driven joint names
            'ml_drivenJoints'(metalist) | cgmObject instances of driven joints

        :raises:
            Exception | if reached

        """   	
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "createSegmentCurve"
            self._b_reportTimes = True
            self._b_autoProgressBar = 1
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'jointList',"default":None,'help':"List or metalist of joints","argType":"joints"},
                                         {'kw':'useCurve',"default":None,'help':"Which curve to use. If None. One Created","argType":"nurbsCurve"},
                                         {'kw':'orientation',"default":'zyx','help':"What is the joints orientation","argType":"string"},
                                         {'kw':'secondaryAxis',"default":'yup','help':"Only necessary when no module provide for orientating","argType":"maya axis arg(ex:'yup')"},
                                         {'kw':'baseName',"default":None,'help':"baseName string","argType":"string"},
                                         {'kw':'connectBy',"default":'trans','help':"How the joint will scale","argType":"string"},
                                         {'kw':'advancedTwistSetup',"default":False,'help':"Whether to do the cgm advnaced twist setup","argType":"bool"},
                                         {'kw':'addMidTwist',"default":True,'help':"Whether to setup a mid twist on the segment","argType":"bool"},
                                         {'kw':'moduleInstance',"default":None,'help':"cgmModule to use for connecting on build","argType":"cgmModule"},	                                 
                                         {'kw':'extendTwistToEnd',"default":False,'help':"Whether to extned the twist to the end by default","argType":"bool"}]			    

            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Verify','call':self._verify_},
                                {'step':'Curve Check','call':self._curveCheck_},
                                {'step':'Joint Checks','call':self._jointSetup_},
                                {'step':'Build Spline IK','call':self._splineIK_},
                                {'step':'Twist setup','call':self._twistSetup_},
                                {'step':'Attach','call':self._attachJoints_},
                                {'step':'Stretch setup','call':self._stretchSetup_}]

            #=================================================================
        def _verify_(self):
            try:#Query ===========================================================================================
                self.ml_joints = cgmMeta.validateObjListArg(self.d_kws['jointList'],mType = cgmMeta.cgmObject, mayaType=['joint'], noneValid = False)
                self.l_joints = [mJnt.p_nameShort for mJnt in self.ml_joints]
                self.int_lenJoints = len(self.ml_joints)#because it's called repeatedly
                self.mi_useCurve = cgmMeta.validateObjArg(self.d_kws['useCurve'],mayaType=['nurbsCurve'],noneValid = True)
                self.mi_module = cgmMeta.validateObjArg(self.d_kws['moduleInstance'],noneValid = True)
                try:self.mi_module.isModule()
                except:self.mi_module = False
                self.mi_mayaOrientation = cgmValid.simpleOrientation(self.d_kws['orientation'])
                self.str_orientation = self.mi_mayaOrientation.p_string
                self.str_secondaryAxis = cgmValid.stringArg(self.d_kws['secondaryAxis'],noneValid=True)
                self.str_baseName = cgmValid.stringArg(self.d_kws['baseName'],noneValid=True)
                self.str_connectBy = cgmValid.stringArg(self.d_kws['connectBy'],noneValid=True)		
                self.b_addMidTwist = cgmValid.boolArg(self.d_kws['addMidTwist'])
                self.b_advancedTwistSetup = cgmValid.boolArg(self.d_kws['advancedTwistSetup'])
                self.b_extendTwistToEnd= cgmValid.boolArg(self.d_kws['extendTwistToEnd'])
            except Exception,error:raise Exception,"[Query | error: {0}".format(error)  

            try:#Validate =====================================================================================
                if self.b_addMidTwist and self.int_lenJoints <4:
                    raise StandardError,"must have at least 3 joints for a mid twist setup"
                if self.int_lenJoints<3:
                    raise StandardError,"needs at least three joints"

                #Good way to verify an instance list? #validate orientation             
                #> axis -------------------------------------------------------------
                self.axis_aim = cgmValid.simpleAxis("%s+"%self.str_orientation [0])
                self.axis_aimNeg = cgmValid.simpleAxis("%s-"%self.str_orientation [0])
                self.axis_up = cgmValid.simpleAxis("%s+"%self.str_orientation [1])

                self.v_aim = self.axis_aim.p_vector#aimVector
                self.v_aimNeg = self.axis_aimNeg.p_vector#aimVectorNegative
                self.v_up = self.axis_up.p_vector   #upVector

                self.outChannel = self.str_orientation [2]#outChannel
                self.upChannel = '%sup'%self.str_orientation [1]#upChannel

            except Exception,error:
                raise StandardError,"[data validation | error: {0}".format(error)  

            try:#>>> Module instance =====================================================================================
                self.mi_rigNull = False	
                if self.mi_module:
                    self.mi_rigNull = self.mi_module.rigNull	

                    if self.str_baseName is None:
                        self.str_baseName = self.mi_module.getPartNameBase()#Get part base name	    
                        log.debug('baseName set to module: %s'%self.str_baseName)	    	    
                if self.str_baseName is None:self.str_baseName = 'testSegmentCurve'    

            except Exception,error:raise Exception,"[Module checks | error: {0}".format(error) 	    

        def _curveCheck_(self):
            try:#Query ===========================================================================================
                if self.mi_useCurve:
                    #must get a offset u position
                    self.f_MatchPosOffset = crvUtils.getUParamOnCurve(self.ml_joints[0].mNode, self.mi_useCurve.mNode)
            except Exception,error:raise Exception,"[Query | error: {0}".format(error)  

        def _jointSetup_(self):
            try:#>> Group ========================================================================================
                self.mi_grp = cgmMeta.cgmObject(name = 'newgroup')
                self.mi_grp.addAttr('cgmName', str(self.str_baseName), lock=True)
                self.mi_grp.addAttr('cgmTypeModifier','segmentStuff', lock=True)
                self.mi_grp.doName()
            except Exception,error:raise Exception,"[Group Creation | error: {0}".format(error) 	    

            try:#>> Orient ========================================================================================
                if not self.mi_module:#if it is, we can assume it's right
                    if self.str_secondaryAxis is None:
                        raise StandardError,"Must have secondaryAxis arg if no moduleInstance is passed"
                    for mJnt in self.ml_joints:
                        """
			Cannot iterate how important this step is. Lost a day trying to trouble shoot why one joint chain worked and another didn't.
			WILL NOT connect right without this.
			"""
                        try:
                            joints.orientJoint(mJnt.mNode,self.str_orientation,self.str_secondaryAxis)
                        except Exception,error:raise Exception,"['%s' orient failed]{%s}"%(mJnt.p_nameShort,error)  
            except Exception,error:raise Exception,"[Orient | error: {0}".format(error) 	    

            try:#>> Joints #=========================================================================
                l_driverJoints = mc.duplicate([mJnt.mNode for mJnt in self.ml_joints],po=True,ic=True,rc=True)
                ml_driverJoints = []
                for i,j in enumerate(l_driverJoints):
                    #self.progressBar_set(status = "Creating driver joints... ", progress = i, maxValue = self.int_lenJoints)		    				    		    		    
                    mJnt = cgmMeta.asMeta(j,'cgmObject',setClass=True)
                    mJnt.doCopyNameTagsFromObject(self.ml_joints[i].mNode,ignore=['cgmTypeModifier','cgmType'])
                    mJnt.addAttr('cgmTypeModifier','splineIK',attrType='string')
                    mJnt.doName()
                    l_driverJoints[i] = mJnt.mNode
                    ml_driverJoints.append(mJnt)
                self.ml_driverJoints = ml_driverJoints
                self.l_driverJoints = [mJnt.p_nameShort for mJnt in self.ml_driverJoints]

            except Exception,error:raise Exception,"[Driver Joints | error: {0}".format(error) 	

        def _splineIK_(self):
            if self.mi_useCurve:
                try:
                    #Because maya is stupid, when doing an existing curve splineIK setup in 2011, you need to select the objects
                    #Rather than use the flags
                    mc.select(cl=1)
                    mc.select([self.ml_driverJoints[0].mNode,self.ml_driverJoints[-1].mNode,self.mi_useCurve.mNode])
                    buffer = mc.ikHandle( simplifyCurve=False, eh = 1,curve = self.mi_useCurve.mNode,
                                          rootOnCurve=True, forceSolver = True, snapHandleFlagToggle=True,
                                          parentCurve = False, solver = 'ikSplineSolver',createCurve = False,)  
                except Exception,error:raise Exception,"[Spline IK | use curve mode | error: {0}".format(error) 	
                self.log_info(buffer)
                mi_segmentCurve = self.mi_useCurve#Link
                mi_segmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
                mi_segmentCurve.doName()		
            else:
                try:#Create Curve =======================================================================================
                    buffer = mc.ikHandle( sj=self.ml_driverJoints[0].mNode, ee=self.ml_driverJoints[-1].mNode,simplifyCurve=False,
                                          solver = 'ikSplineSolver', ns = 4, rootOnCurve=True,forceSolver = True,
                                          createCurve = True,snapHandleFlagToggle=True )  
                except Exception,error:raise Exception,"[Spline IK | build curve | error: {0}".format(error) 	

                mi_segmentCurve = cgmMeta.asMeta( buffer[2],'cgmObject',setClass=True )
                mi_segmentCurve.addAttr('cgmName',self.str_baseName,attrType='string',lock=True)    
                mi_segmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
                mi_segmentCurve.doName()

                try:#>> Module Link =======================================================================================
                    if self.mi_module:#if we have a module, connect vis
                        mi_segmentCurve.overrideEnabled = 1		
                        cgmMeta.cgmAttr(self.mi_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_segmentCurve.mNode,'overrideVisibility'))    
                        cgmMeta.cgmAttr(self.mi_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_segmentCurve.mNode,'overrideDisplayType'))    
                except Exception,error:raise Exception,"[Connect To Module | error: {0}".format(error) 

            self.mi_splineSolver = cgmMeta.cgmNode(name = 'ikSplineSolver')
            try:#>> Update func name strings ==============================================================================
                self._str_funcName = "%s(%s)"%(self._str_funcName,mi_segmentCurve.p_nameShort)
                self.__updateFuncStrings__()
            except Exception,error:self.log_error("Updating names strings | %s"%(error))	


            try:#>> Handle/Effector =======================================================================================
                mi_ikHandle = cgmMeta.asMeta( buffer[0],'cgmObject',setClass=True )
                mi_ikHandle.addAttr('cgmName',self.str_baseName,attrType='string',lock=True)    		
                mi_ikHandle.doName()
                mi_ikHandle.parent = self.mi_grp
                self.mi_ikHandle = mi_ikHandle

                mi_ikEffector = cgmMeta.asMeta( buffer[1],'cgmObject',setClass=True )
                mi_ikEffector.addAttr('cgmName',self.str_baseName,attrType='string',lock=True)  
                mi_ikEffector.doName()

                self.mi_ikEffector = mi_ikEffector
                if self.mi_useCurve:
                    self.log_info("useCurve mode > set ikHandle offset to %s"%self.f_MatchPosOffset)
                    mi_ikHandle.offset = self.f_MatchPosOffset
                mi_segmentCurve.connectChildNode(self.mi_grp,'segmentGroup','owner')
                self.mi_segmentCurve = mi_segmentCurve		
            except Exception,error:raise Exception,"[Handle/Effector | error: {0}".format(error) 	

        def _twistSetup_(self):
            try:#Pull local =======================================================================================
                ml_driverJoints = self.ml_driverJoints
                mi_ikHandle = self.mi_ikHandle
                b_addMidTwist = self.b_addMidTwist
                str_orientation = self.str_orientation

            except Exception,error:
                raise StandardError,"[Pull local | error: {0}".format(error)  

            try:#SplineIK Twist =======================================================================================
                d_twistReturn = IKHandle_addSplineIKTwist(mi_ikHandle.mNode,self.b_advancedTwistSetup)
                mPlug_twistStart = d_twistReturn['mi_plug_start']
                mPlug_twistEnd = d_twistReturn['mi_plug_end']
            except Exception,error:raise Exception,"[Initial SplineIK Twist | error: {0}".format(error)  

            try:#>>> Twist stuff
                #=========================================================================
                mPlug_factorInfluenceIn = cgmMeta.cgmAttr(self.mi_segmentCurve.mNode,"twistExtendToEnd",attrType = 'float',lock=False,keyable=True,hidden=False,minValue=0,maxValue=1)               
                self.mPlug_factorInfluenceIn = mPlug_factorInfluenceIn#Link
                d_midTwistOutPlugs = {} # dictionary of out plugs to index of joint in the before or after list
                ml_midTwistJoints = [] #exteded list of before and after joints
                int_mid = False

                if b_addMidTwist:#We need to get our factors
                    try:#>> MidTwist =====================================================================================
                        #>> Let's do the blend ===============================================================
                        try:#First split it out ------------------------------------------------------------------
                            int_mid = int(len(ml_driverJoints)/2)
                            ml_beforeJoints = ml_driverJoints[1:int_mid]
                            ml_beforeJoints.reverse()
                            ml_afterJoints = ml_driverJoints[int_mid+1:-1]
                            self.log_debug("beforeJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_beforeJoints])
                            self.log_debug("afterJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_afterJoints])
                        except Exception,error:raise Exception,"[Split fail! | error: {0}".format(error)  

                        mPlug_midTwist = cgmMeta.cgmAttr(self.mi_segmentCurve,"twistMid",attrType='float',keyable=True,hidden=False)	    
                        ml_midTwistJoints.extend(ml_beforeJoints)
                        ml_midTwistJoints.extend(ml_afterJoints)
                        ml_midTwistJoints.append(ml_driverJoints[int_mid])
                        #Get our factors ------------------------------------------------------------------
                        mPlugs_factors = []
                        maxInt = (max([len(ml_beforeJoints),len(ml_afterJoints)])) +1#This is our max blend factors we need
                        fl_fac = 1.0/maxInt#get our factor
                        log.debug("maxInt: %s"%maxInt)
                        l_factors = [ (1-(i*fl_fac)) for i in range(maxInt) ]#fill our factor list
                        int_maxLen = len(l_factors)
                        for i,fac in enumerate(l_factors):
                            #self.progressBar_set(status = "Setting up midTwist factor nodes... ", progress = i, maxValue = int_maxLen)		    				    		    		    			    
                            mPlug_midFactorIn = cgmMeta.cgmAttr(self.mi_segmentCurve,"midFactor_%s"%(i),attrType='float',value=fac,hidden=False)	    
                            mPlug_midFactorOut = cgmMeta.cgmAttr(self.mi_segmentCurve,"out_midFactor_%s"%(i),attrType='float',lock=True)
                            arg = "%s = %s * %s"%(mPlug_midFactorOut.p_combinedShortName,mPlug_midTwist.p_combinedShortName,mPlug_midFactorIn.p_combinedShortName)
                            log.debug("%s arg: %s"%(i,arg))
                            NodeF.argsToNodes(arg).doBuild()
                            #Store it
                            d_midTwistOutPlugs[i] = mPlug_midFactorOut    
                    except Exception,error:raise Exception,"[MidTwist setup fail! | error: {0}".format(error)  

                mPlugs_rollSumDrivers = []#Advanced Twist
                mPlugs_rollDrivers = []
                d_mPlugs_rotateGroupDrivers = {}
                self.md_mPlugs_rotateGroupDrivers = d_mPlugs_rotateGroupDrivers
                for i,mJnt in enumerate(ml_driverJoints):
                    #self.progressBar_set(status = "Setting up twist setup | '%s'"%self.l_driverJoints[i], progress = i, maxValue = self.int_lenJoints)		    				    		    		    			    		    
                    mPlugs_twistSumOffset = []
                    if mJnt not in [ml_driverJoints[0],ml_driverJoints[-1]]:
                        if b_addMidTwist and mJnt in ml_midTwistJoints:
                            if mJnt in ml_afterJoints:int_index = ml_afterJoints.index(mJnt)+1
                            elif mJnt in ml_beforeJoints:int_index = ml_beforeJoints.index(mJnt)+1
                            elif mJnt == ml_driverJoints[int_mid]:int_index = 0
                            else:raise StandardError,"Found no mid twist index for: '%s'"%mJnt.getShortName()

                            try:mPlug_midTwistFactor = d_midTwistOutPlugs[int_index]
                            except:raise StandardError,"Found no mid twist plug for: '%s' | %s"%(mJnt.getShortName(),d_midTwistOutPlugs.keys())
                            mPlugs_twistSumOffset.append(mPlug_midTwistFactor)

                        mPlug_baseRoll = cgmMeta.cgmAttr(mJnt,'r%s'%str_orientation[0])
                        mPlug_extendTwistFactor = cgmMeta.cgmAttr(self.mi_segmentCurve.mNode,"out_extendTwistFactor_%s"%i,attrType = 'float',lock=True)		    
                        mPlug_extendTwist = cgmMeta.cgmAttr(self.mi_segmentCurve.mNode,"out_extendTwist_%s"%i,attrType = 'float',lock=True)	
                        mPlug_twistSum = cgmMeta.cgmAttr(self.mi_segmentCurve.mNode,"out_twistSum_%s"%i,attrType = 'float',lock=True)	

                        #twistFactor = baseRoll / 2
                        arg_extendInfluenceFactor = " %s = %s / 2"%(mPlug_extendTwistFactor.p_combinedShortName,mPlug_baseRoll.p_combinedShortName)
                        #extendTwist = factorIn * factor
                        arg_extendInfluence = " %s = %s * -%s"%(mPlug_extendTwist.p_combinedShortName,mPlug_factorInfluenceIn.p_combinedShortName,mPlug_extendTwistFactor.p_combinedShortName)
                        mPlugs_twistSumOffset.append(mPlug_extendTwist)
                        arg_twistSum = " %s = %s"%(mPlug_twistSum.p_combinedShortName,' + '.join([mPlug.p_combinedShortName for mPlug in mPlugs_twistSumOffset]))

                        for arg in [arg_extendInfluenceFactor,arg_extendInfluence,arg_twistSum]:
                            self.log_debug(arg)
                            NodeF.argsToNodes(arg).doBuild() 
                        d_mPlugs_rotateGroupDrivers[i] = mPlug_twistSum

            except Exception,error:
                raise StandardError,"[Segment Twist setup | error: {0}".format(error) 

        def _attachJoints_(self):
            try:#Pull local =======================================================================================
                ml_driverJoints = self.ml_driverJoints
                ml_joints = self.ml_joints
                mi_ikHandle = self.mi_ikHandle
                b_addMidTwist = self.b_addMidTwist
                str_orientation = self.str_orientation
                mi_segmentCurve = self.mi_segmentCurve
                mi_module = self.mi_module
                mi_rigNull = self.mi_rigNull
                md_mPlugs_rotateGroupDrivers = self.md_mPlugs_rotateGroupDrivers
            except Exception,error:
                raise StandardError,"[Pull local | error: {0}".format(error)  

            try:#>>> Create up locs, follicles -------------------------------------------------------------
                ml_pointOnCurveInfos = []
                ml_upGroups = []

                #Link up
                self.ml_pointOnCurveInfos = ml_pointOnCurveInfos
                self.ml_upGroups = ml_upGroups

                #First thing we're going to do is create our 'follicles'
                l_shapes = mc.listRelatives(mi_segmentCurve.mNode,shapes=True)
                str_shape = l_shapes[0]

                for i,mJnt in enumerate(ml_joints):   
                    #self.progressBar_set(status = "Attaching| '%s'"%self.l_joints[i], progress = i, maxValue = self.int_lenJoints)		    				    		    		    			    		    		    
                    l_closestInfo = distance.returnNearestPointOnCurveInfo(mJnt.mNode,mi_segmentCurve.mNode)
                    log.debug("'%s' closest info: %s"%(mJnt.mNode,l_closestInfo))
                    #>>> POCI ----------------------------------------------------------------
                    mi_closestPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
                    mc.connectAttr ((str_shape+'.worldSpace'),(mi_closestPointNode.mNode+'.inputCurve'))	

                    #> Name
                    mi_closestPointNode.doStore('cgmName',mJnt)
                    mi_closestPointNode.doName()
                    #>Set follicle value
                    mi_closestPointNode.parameter = l_closestInfo['parameter']
                    ml_pointOnCurveInfos.append(mi_closestPointNode)

                    #>>> loc ----------------------------------------------------------------
                    mi_upLoc = mJnt.doLoc(fastMode = True)#Make up Loc
                    mi_locRotateGroup = mJnt.doCreateAt()#group in place  THIS MAY NOTE BE RIGHT, WAS (FALSE)
                    mi_locRotateGroup.parent = ml_driverJoints[i].mNode
                    mi_locRotateGroup.doStore('cgmName',mJnt)	    
                    mi_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
                    mi_locRotateGroup.doName()

                    #Store the rotate group to the joint
                    mJnt.connectChildNode(mi_locRotateGroup,'rotateUpGroup','drivenJoint')
                    mi_zeroGrp = cgmMeta.asMeta( mi_locRotateGroup.doGroup(True),'cgmObject',setClass=True )
                    mi_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
                    mi_zeroGrp.doName()

                    #connect some other data
                    mi_locRotateGroup.connectChildNode(mi_locRotateGroup.parent,'zeroGroup')
                    mi_locRotateGroup.connectChildNode(mi_upLoc,'upLoc')
                    mJnt.connectChildNode(mi_upLoc,'upLoc')
                    mc.makeIdentity(mi_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)

                    mi_upLoc.parent = mi_locRotateGroup.mNode
                    mc.move(0,10,0,mi_upLoc.mNode,os=True)#TODO - make dependent on orientation	
                    ml_upGroups.append(mi_upLoc)

                    #Connect the rotate
                    #if extendTwistToEnd:#Need at least x joints
                    mPlug_rotateDriver = md_mPlugs_rotateGroupDrivers.get(i) or False
                    if mPlug_rotateDriver:
                        mPlug_rotateDriver.doConnectOut("%s.r%s"%(mi_locRotateGroup.mNode,str_orientation[0]))
                        #ml_twistDrivers.append(mPlug_factorInfluenceOut)
                    try:
                        if mi_module:#if we have a module, connect vis
                            mi_upLoc.overrideEnabled = 1		
                            cgmMeta.cgmAttr(mi_rigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_upLoc.mNode,'overrideVisibility'))
                            cgmMeta.cgmAttr(mi_rigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_upLoc.mNode,'overrideDisplayType'))    
                    except Exception,error:raise Exception,"[module connect | error: {0}".format(error) 

                #Orient constrain our last joint to our splineIK Joint
                constBuffer = mc.orientConstraint(ml_driverJoints[-1].mNode,ml_joints[-1].mNode,maintainOffset = True)
                attributes.doSetAttr(constBuffer[0],'interpType',0)

            except Exception,error:raise Exception,"[attach and connect | error: {0}".format(error) 

        def _stretchSetup_(self):
            try:#Pull local =======================================================================================
                ml_driverJoints = self.ml_driverJoints
                ml_joints = self.ml_joints
                str_orientation = self.str_orientation
                mi_segmentCurve = self.mi_segmentCurve
                mi_grp = self.mi_grp
                mi_module = self.mi_module
                mi_rigNull = self.mi_rigNull
                ml_pointOnCurveInfos = self.ml_pointOnCurveInfos
                ml_upGroups = self.ml_upGroups		
                md_mPlugs_rotateGroupDrivers = self.md_mPlugs_rotateGroupDrivers
            except Exception,error:raise Exception,"[Pull local | error: {0}".format(error)  

            try:#>>> Scale stuff =============================================================================
                #> Create IK effectors,Create distance nodes
                ml_IKeffectors = []
                ml_IKhandles = []  
                ml_distanceObjects = []
                ml_distanceShapes = []  
                for i,mJnt in enumerate(ml_joints[:-1]):
                    try:
                        #self.progressBar_set(status = "scale guts | '%s'"%self.l_joints[i], progress = i, maxValue = self.int_lenJoints)
                        ik_buffer = mc.ikHandle (startJoint=mJnt.mNode,
                                                 endEffector = ml_joints[i+1].mNode,
                                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                                 enableHandles=True )
                        #Handle
                        mi_IK_Handle = cgmMeta.asMeta(ik_buffer[0],'cgmObject',setClass=True)
                        mi_IK_Handle.parent = ml_driverJoints[i+1].mNode
                        mi_IK_Handle.doStore('cgmName',mJnt)    
                        mi_IK_Handle.doName()

                        #Effector
                        mi_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
                        mi_IK_Effector.doStore('cgmName',mJnt)    
                        mi_IK_Effector.doName()

                        ml_IKhandles.append(mi_IK_Handle)
                        ml_IKeffectors.append(mi_IK_Effector)

                        if mi_module:#if we have a module, connect vis
                            mi_IK_Handle.overrideEnabled = 1		
                            cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_IK_Handle.mNode,'overrideVisibility'))
                            cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_IK_Handle.mNode,'overrideDisplayType'))    

                        #>> Distance nodes
                        mi_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
                        mi_distanceObject = cgmMeta.cgmObject( mi_distanceShape.getTransform() )
                        mi_distanceObject.doStore('cgmName',mJnt)
                        mi_distanceObject.addAttr('cgmType','measureNode',lock=True)
                        mi_distanceObject.doName(nameShapes = True)
                        mi_distanceObject.parent = mi_grp.mNode#parent it
                        mi_distanceObject.overrideEnabled = 1
                        mi_distanceObject.overrideVisibility = 1

                        #Connect things
                        mc.connectAttr ((ml_pointOnCurveInfos[i].mNode+'.position'),(mi_distanceShape.mNode+'.startPoint'))
                        mc.connectAttr ((ml_pointOnCurveInfos[i+1].mNode+'.position'),(mi_distanceShape.mNode+'.endPoint'))

                        ml_distanceObjects.append(mi_distanceObject)
                        ml_distanceShapes.append(mi_distanceShape)


                        if mi_module:#Connect hides if we have a module instance:
                            cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideVisibility'))
                            cgmMeta.cgmAttr(mi_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mi_distanceObject.mNode,'overrideDisplayType'))    
                    except Exception,error:raise Exception,"[Pull local | error: {0}".format(error)  
            except Exception,error:
                raise Exception,"[scale stuff setup | error: {0}".format(error) 

            try:#fix twists ==========================================================================================
                #>> Second part for the full twist setup
                aimChannel = str_orientation[0]  

                for i,mJnt in enumerate(ml_joints[:-1]):
                    #self.progressBar_set(status = "fixing twist | '%s'"%self.l_driverJoints[i], progress = i, maxValue = self.int_lenJoints)		    
                    rotBuffer = mc.xform (mJnt.mNode, q=True, ws=True, ro=True)
                    log.debug("rotBuffer: %s"%rotBuffer)
                    #Create the poleVector
                    poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,ml_IKhandles[i].mNode)  	
                    IKHandle_fixTwist(ml_IKhandles[i])

                    if mc.xform (mJnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
                        self.log_info("Found the following on '%s': %s"%(mJnt.getShortName(),mc.xform (mJnt.mNode, q=True, ws=True, ro=True)))
            except Exception,error:
                raise Exception,"[fix twists | error: {0}".format(error) 

            try:#>>>Hook up stretch/scale #==========================================================================
                #Buffer
                mi_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = self.str_baseName,overideMessageCheck=True)
                mi_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
                mi_jntScaleBufferNode.addAttr('masterScale',value = 1.0, minValue = 0.0001, attrType='float')    
                #mi_jntScaleBufferNode.addAttr('segmentScale',value = 1.0, attrType='float',minValue = 0.0) 

                mi_jntScaleBufferNode.doName()
                ml_distanceAttrs = []
                ml_resultAttrs = []

                mi_jntScaleBufferNode.connectParentNode(mi_segmentCurve.mNode,'segmentCurve','scaleBuffer')
                ml_mainMDs = []
                for i,mJnt in enumerate(ml_joints[:-1]):
                    #self.progressBar_set(status = "node setup | '%s'"%self.l_joints[i], progress = i, maxValue = self.int_lenJoints)		    

                    #Make some attrs
                    mPlug_attrDist= cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                    "distance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)
                    mPlug_attrNormalBaseDist = cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                               "normalizedBaseDistance_%s"%i,attrType = 'float',
                                                               initialValue=0,lock=True,minValue = 0)			
                    mPlug_attrNormalDist = cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                           "normalizedDistance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)		
                    mPlug_attrResult = cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                       "scaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	
                    mPlug_attrTransformedResult = cgmMeta.cgmAttr(mi_jntScaleBufferNode.mNode,
                                                                  "scaledScaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	

                    #Store our distance base to our buffer
                    try:mi_jntScaleBufferNode.store(ml_distanceShapes[i].distance)#Store to our buffer
                    except Exception,error:raise Exception,"[Failed to store joint distance: %s]{%s}"%(ml_distanceShapes[i].mNode,error)


                    if self.str_connectBy.lower() in ['translate','trans']:
                        #Let's build our args
                        l_argBuild = []
                        #distance by master
                        l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalBaseDist.p_combinedShortName,
                                                                   '{0}.{1}'.format(mi_jntScaleBufferNode.mNode,mi_jntScaleBufferNode.d_indexToAttr[i]),
                                                                   "{0}.masterScale".format(mi_jntScaleBufferNode.mNode)))
                        l_argBuild.append("{0} = {1} / {2}".format(mPlug_attrNormalDist.p_combinedShortName,
                                                                   mPlug_attrDist.p_combinedShortName,
                                                                   "{0}.masterScale".format(mi_jntScaleBufferNode.mNode)))			
                        for arg in l_argBuild:
                            self.log_info("Building: {0}".format(arg))
                            NodeF.argsToNodes(arg).doBuild()
                        #Still not liking the way this works with translate scale. looks fine till you add squash and stretch
                        try:
                            mPlug_attrDist.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))		        
                            mPlug_attrNormalDist.doConnectOut('%s.t%s'%(ml_joints[i+1].mNode,str_orientation[0]))
                            mPlug_attrNormalDist.doConnectOut('%s.t%s'%(ml_driverJoints[i+1].mNode,str_orientation[0]))    	    
                        except Exception,error:
                            raise Exception,"[Failed to connect joint attrs by scale: {0} | error: {1}]".format(mJnt.mNode,error)		    
                    else:
                        mi_mdNormalBaseDist = cgmMeta.cgmNode(nodeType='multiplyDivide')
                        mi_mdNormalBaseDist.operation = 1
                        mi_mdNormalBaseDist.doStore('cgmName',mJnt)
                        mi_mdNormalBaseDist.addAttr('cgmTypeModifier','normalizedBaseDist')
                        mi_mdNormalBaseDist.doName()

                        attributes.doConnectAttr('%s.masterScale'%(mi_jntScaleBufferNode.mNode),#>>
                                                 '%s.%s'%(mi_mdNormalBaseDist.mNode,'input1X'))
                        attributes.doConnectAttr('%s.%s'%(mi_jntScaleBufferNode.mNode,mi_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                                 '%s.%s'%(mi_mdNormalBaseDist.mNode,'input2X'))	
                        mPlug_attrNormalBaseDist.doConnectIn('%s.%s'%(mi_mdNormalBaseDist.mNode,'output.outputX'))

                        #Create the normalized distance
                        mi_mdNormalDist = cgmMeta.cgmNode(nodeType='multiplyDivide')
                        mi_mdNormalDist.operation = 1
                        mi_mdNormalDist.doStore('cgmName',mJnt)
                        mi_mdNormalDist.addAttr('cgmTypeModifier','normalizedDist')
                        mi_mdNormalDist.doName()

                        attributes.doConnectAttr('%s.masterScale'%(mi_jntScaleBufferNode.mNode),#>>
                                                 '%s.%s'%(mi_mdNormalDist.mNode,'input1X'))
                        mPlug_attrDist.doConnectOut('%s.%s'%(mi_mdNormalDist.mNode,'input2X'))	
                        mPlug_attrNormalDist.doConnectIn('%s.%s'%(mi_mdNormalDist.mNode,'output.outputX'))

                        #Create the mdNode
                        mi_mdSegmentScale = cgmMeta.cgmNode(nodeType='multiplyDivide')
                        mi_mdSegmentScale.operation = 2
                        mi_mdSegmentScale.doStore('cgmName',mJnt)
                        mi_mdSegmentScale.addAttr('cgmTypeModifier','segmentScale')
                        mi_mdSegmentScale.doName()
                        mPlug_attrDist.doConnectOut('%s.%s'%(mi_mdSegmentScale.mNode,'input1X'))	
                        mPlug_attrNormalBaseDist.doConnectOut('%s.%s'%(mi_mdSegmentScale.mNode,'input2X'))
                        mPlug_attrResult.doConnectIn('%s.%s'%(mi_mdSegmentScale.mNode,'output.outputX'))	

                        try:#Connect
                            mPlug_attrDist.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))		        
                            mPlug_attrResult.doConnectOut('%s.s%s'%(mJnt.mNode,str_orientation[0]))
                            mPlug_attrResult.doConnectOut('%s.s%s'%(ml_driverJoints[i].mNode,str_orientation[0]))
                        except Exception,error:raise Exception,"[Failed to connect joint attrs by scale: {0} | error: {1}]".format(mJnt.mNode,error)		    

                        ml_mainMDs.append(mi_mdSegmentScale)#store the md

                    #Create the normalized base distance


                    #Append our data
                    ml_distanceAttrs.append(mPlug_attrDist)
                    ml_resultAttrs.append(mPlug_attrResult)


                for axis in [str_orientation[1],str_orientation[2]]:
                    attributes.doConnectAttr('%s.s%s'%(mJnt.mNode,axis),#>>
                                             '%s.s%s'%(ml_driverJoints[i].mNode,axis))	 	
            except Exception,error:raise Exception,"[Stretch wiring | error: {0}".format(error) 

            try:#Connect last joint scale to second to last
                for axis in ['scaleX','scaleY','scaleZ']:
                    attributes.doConnectAttr('%s.%s'%(ml_joints[-2].mNode,axis),#>>
                                             '%s.%s'%(ml_joints[-1].mNode,axis))	 

                mc.pointConstraint(ml_driverJoints[0].mNode,ml_joints[0].mNode,maintainOffset = False)
            except Exception,error:raise Exception,"[constrain last end end bits | error: {0}".format(error) 

            try:#>> Connect and close =============================================================================
                mi_segmentCurve.connectChildNode(mi_jntScaleBufferNode,'scaleBuffer','segmentCurve')
                mi_segmentCurve.connectChildNode(mi_IK_Handle,'ikHandle','segmentCurve')
                mi_segmentCurve.msgList_connect('drivenJoints',ml_joints,'segmentCurve')       
                mi_segmentCurve.msgList_connect('driverJoints',ml_driverJoints,'segmentCurve')   
            except Exception,error:raise Exception,"[Final Connections | error: {0}".format(error) 

            try:#Return Prep ====================================================================================
                d_return = {'mi_segmentCurve':mi_segmentCurve,'segmentCurve':mi_segmentCurve.mNode,'mi_ikHandle':mi_IK_Handle,'mi_segmentGroup':mi_grp,
                            'l_driverJoints':self.l_driverJoints,'ml_driverJoints':ml_driverJoints,
                            'scaleBuffer':mi_jntScaleBufferNode.mNode,'mi_scaleBuffer':mi_jntScaleBufferNode,'mPlug_extendTwist':self.mPlug_factorInfluenceIn,
                            'l_drivenJoints':self.l_joints,'ml_drivenJoints':ml_joints}
            except Exception,error:raise Exception,"[Return prep | error: {0}".format(error) 
            return d_return	   		

    return fncWrap(*args,**kws).go()

def createSegmentCurve2(jointList,orientation = 'zyx', secondaryAxis = None, 
                        baseName = None, connectBy = 'trans',
                        advancedTwistSetup = False,
                        addMidTwist = True, extendTwistToEnd = False,
                        moduleInstance = None):
    """
    Stored meta data on completed segment:
    scaleBuffer
    drivenJoints     
    driverJoints 
    advancedTwistSetup(bool) -- whether to set up ramp advanced twist setup or not (default - False)
    addMidTwist(bool) -- if to setup midTwist
    extendTwistToEnd(bool) -- whether this should be on or not???
    The basics of a cgmSegment curve are a base spline IK segment which has twist controlled via twist start and end. 
    """
    _str_funcName = 'createSegmentCurve'
    log.info(">>> %s >> "%_str_funcName + "="*75)   

    try:#Gather data =====================================================================================
        jointList = cgmValid.objStringList(jointList,mayaType=['joint'])
        if addMidTwist and len(jointList) <4:
            raise StandardError,"must have at least 3 joints for a mid twist setup"
        if len(jointList)<3:
            raise StandardError,"needs at least three joints"

        #Good way to verify an instance list? #validate orientation             
        #> axis -------------------------------------------------------------
        axis_aim = cgmValid.simpleAxis("%s+"%orientation[0])
        axis_aimNeg = cgmValid.simpleAxis("%s-"%orientation[0])
        axis_up = cgmValid.simpleAxis("%s+"%orientation[0])

        aimVector = axis_aim.p_vector
        aimVectorNegative = axis_aimNeg.p_vector
        upVector = axis_up.p_vector   

        outChannel = orientation[2]
        upChannel = '%sup'%orientation[1]

        #validate orientation   

        #> joints -------------------------------------------------------------       
        #try:ml_jointList = cgmMeta.validateObjListArg(jointList,cgmMeta.cgmObject,noneValid=False,mayaType=['joint'])
        #except Exception,error:
            #raise StandardError,"%s >>Joint metaclassing | error : %s"%(_str_funcName,error)

    except Exception,error:
        raise StandardError,"%s >> data gather | error: %s"%(_str_funcName,error)  

    try:#>>> Module instance =====================================================================================
        i_module = False
        i_rigNull = False
        i_module = False    

        try:
            if moduleInstance is not None:
                if moduleInstance.isModule():
                    i_module = moduleInstance    
                    i_rigNull = i_module.rigNull
                    log.info("%s >> module instance found: %s"%(_str_funcName,i_module.p_nameShort))		
        except:pass

        if i_module:
            if baseName is None:
                baseName = i_module.getPartNameBase()#Get part base name	    
                log.debug('baseName set to module: %s'%baseName)	    	    
        if baseName is None:baseName = 'testSegmentCurve'    

    except Exception,error:
        raise StandardError,"%s >> Module check | error: %s"%(_str_funcName,error)  


    try:#Create our group
        i_grp = cgmMeta.cgmObject(name = 'newgroup')
        i_grp.addAttr('cgmName', str(baseName), lock=True)
        i_grp.addAttr('cgmTypeModifier','segmentStuff', lock=True)
        i_grp.doName()

        ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]#Initialize original joints

        if not moduleInstance:#if it is, we can assume it's right
            if secondaryAxis is None:
                raise StandardError,"createControlSurfaceSegment>>> Must have secondaryAxis arg if no moduleInstance is passed"
            for i_jnt in ml_jointList:
                """
            Cannot iterate how important this step is. Lost a day trying to trouble shoot why one joint chain worked and another didn't.
            WILL NOT connect right without this.
            """
                try:
                    joints.orientJoint(i_jnt.mNode,orientation,secondaryAxis)
                except Exception,error:raise Exception,"['%s' orient failed]{%s}"%(i_jnt.p_nameShort,error)  

    except Exception,error:
        raise StandardError,"%s >> base group | error: %s"%(_str_funcName,error)  

    try:#Joints
        #=========================================================================
        #Create spline IK joints
        #>>Surface chain    
        l_driverJoints = mc.duplicate(jointList,po=True,ic=True,rc=True)
        ml_driverJoints = []
        for i,j in enumerate(l_driverJoints):
            i_j = cgmMeta.asMeta(j,'cgmObject',setClass=True)
            i_j.doCopyNameTagsFromObject(ml_jointList[i].mNode,ignore=['cgmTypeModifier','cgmType'])
            i_j.addAttr('cgmTypeModifier','splineIK',attrType='string')
            i_j.doName()
            l_driverJoints[i] = i_j.mNode
            ml_driverJoints.append(i_j)

        #Create Curve
        i_splineSolver = cgmMeta.cgmNode(name = 'ikSplineSolver')
        buffer = mc.ikHandle( sj=ml_driverJoints[0].mNode, ee=ml_driverJoints[-1].mNode,simplifyCurve=False,
                              solver = 'ikSplineSolver', ns = 4, rootOnCurve=True,forceSolver = True,
                              createCurve = True,snapHandleFlagToggle=True )  

        i_segmentCurve = cgmMeta.asMeta( buffer[2],'cgmObject',setClass=True )
        i_segmentCurve.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
        i_segmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
        i_segmentCurve.doName()

        if i_module:#if we have a module, connect vis
            i_segmentCurve.overrideEnabled = 1		
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_segmentCurve.mNode,'overrideVisibility'))    
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_segmentCurve.mNode,'overrideDisplayType'))    

        i_ikHandle = cgmMeta.asMeta( buffer[0],'cgmObject',setClass=True )
        i_ikHandle.doName()
        i_ikEffector = cgmMeta.asMeta( buffer[1],'cgmObject',setClass=True )
        i_ikHandle.parent = i_grp.mNode

        i_segmentCurve.connectChildNode(i_grp,'segmentGroup','owner')
    except Exception,error:
        raise StandardError,"%s >> joints and curve | error: %s"%(_str_funcName,error)  

    try:#Add twist
        d_twistReturn = IKHandle_addSplineIKTwist(i_ikHandle.mNode,advancedTwistSetup)
        mPlug_twistStart = d_twistReturn['mi_plug_start']
        mPlug_twistEnd = d_twistReturn['mi_plug_end']
    except Exception,error:
        raise StandardError,"%s >> initial twist | error: %s"%(_str_funcName,error)  

    try:#>>> Twist stuff
        #=========================================================================
        mPlug_factorInfluenceIn = cgmMeta.cgmAttr(i_segmentCurve.mNode,"twistExtendToEnd",attrType = 'float',lock=False,keyable=True,hidden=False,minValue=0,maxValue=1)               
        d_midTwistOutPlugs = {} # dictionary of out plugs to index of joint in the before or after list
        ml_midTwistJoints = [] #exteded list of before and after joints
        int_mid = False
        if addMidTwist:#We need to get our factors
            #>> Let's do the blend ===============================================================
            #First split it out ------------------------------------------------------------------
            int_mid = int(len(ml_driverJoints)/2)
            ml_beforeJoints = ml_driverJoints[1:int_mid]
            ml_beforeJoints.reverse()
            ml_afterJoints = ml_driverJoints[int_mid+1:-1]
            log.debug("beforeJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_beforeJoints])
            log.debug("afterJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_afterJoints])
            mPlug_midTwist = cgmMeta.cgmAttr(i_segmentCurve,"twistMid",attrType='float',keyable=True,hidden=False)	    
            ml_midTwistJoints.extend(ml_beforeJoints)
            ml_midTwistJoints.extend(ml_afterJoints)
            ml_midTwistJoints.append(ml_driverJoints[int_mid])
            #Get our factors ------------------------------------------------------------------
            mPlugs_factors = []
            maxInt = (max([len(ml_beforeJoints),len(ml_afterJoints)])) +1#This is our max blend factors we need
            fl_fac = 1.0/maxInt#get our factor
            log.debug("maxInt: %s"%maxInt)
            l_factors = [ (1-(i*fl_fac)) for i in range(maxInt) ]#fill our factor list
            for i,fac in enumerate(l_factors):
                mPlug_midFactorIn = cgmMeta.cgmAttr(i_segmentCurve,"midFactor_%s"%(i),attrType='float',value=fac,hidden=False)	    
                mPlug_midFactorOut = cgmMeta.cgmAttr(i_segmentCurve,"out_midFactor_%s"%(i),attrType='float',lock=True)
                arg = "%s = %s * %s"%(mPlug_midFactorOut.p_combinedShortName,mPlug_midTwist.p_combinedShortName,mPlug_midFactorIn.p_combinedShortName)
                log.debug("%s arg: %s"%(i,arg))
                NodeF.argsToNodes(arg).doBuild()
                #Store it
                d_midTwistOutPlugs[i] = mPlug_midFactorOut    

        #if extendTwistToEnd:#Need at least x joints
        #mPlug_startEndDifference = cgmMeta.cgmAttr(i_segmentCurve.mNode,"startEndDifference",attrType = 'float',lock=True)	    
        #mPlug_startEndFactor = cgmMeta.cgmAttr(i_segmentCurve.mNode,"out_startEndFactor",attrType = 'float',lock=True)
        #mPlug_secondToLastJoint = cgmMeta.cgmAttr(ml_driverJoints[-2],'r%s'%orientation[0])	        
        #mPlug_factorInfluenceOut = cgmMeta.cgmAttr(i_segmentCurve.mNode,"out_extendTwistInfluence",attrType = 'float',hidden = True, lock=True)	    
        #difference = end - start
        #arg_twistDifference = " %s = %s - %s"%(mPlug_startEndDifference.p_combinedShortName,mPlug_twistStart.p_combinedShortName,mPlug_twistEnd.p_combinedShortName)
        #factor = difference / len(joints)
        #arg_twistFactor = " %s = %s / %s"%(mPlug_startEndFactor.p_combinedShortName,mPlug_secondToLastJoint.p_combinedShortName,2)
        #factorOut = factorIn * factor
        #arg_extendInfluence = " %s = %s * -%s"%(mPlug_factorInfluenceOut.p_combinedShortName,mPlug_factorInfluenceIn.p_combinedShortName,mPlug_startEndFactor.p_combinedShortName)

        """
        for arg in [arg_twistDifference,arg_twistFactor,arg_extendInfluence]:
        log.debug(arg)
        NodeF.argsToNodes(arg).doBuild() """   


        mPlugs_rollSumDrivers = []#Advanced Twist
        mPlugs_rollDrivers = []
        d_mPlugs_rotateGroupDrivers = {}

        for i,i_jnt in enumerate(ml_driverJoints):
            #if extendTwistToEnd:#Need at least x joints
            mPlugs_twistSumOffset = []
            if i_jnt not in [ml_driverJoints[0],ml_driverJoints[-1]]:
                if addMidTwist and i_jnt in ml_midTwistJoints:
                    if i_jnt in ml_afterJoints:int_index = ml_afterJoints.index(i_jnt)+1
                    elif i_jnt in ml_beforeJoints:int_index = ml_beforeJoints.index(i_jnt)+1
                    elif i_jnt == ml_driverJoints[int_mid]:int_index = 0
                    else:raise StandardError,"Found no mid twist index for: '%s'"%i_jnt.getShortName()

                    try:mPlug_midTwistFactor = d_midTwistOutPlugs[int_index]
                    except:raise StandardError,"Found no mid twist plug for: '%s' | %s"%(i_jnt.getShortName(),d_midTwistOutPlugs.keys())
                    mPlugs_twistSumOffset.append(mPlug_midTwistFactor)
                    #mPlug_baseRoll = cgmMeta.cgmAttr(i_segmentCurve.mNode,"out_addMid_%s"%i,attrType = 'float',lock=True)
                    #mPlug_driverRoll = cgmMeta.cgmAttr(i_jnt,'r%s'%orientation[0])

                    #arg_midAdd = "%s = %s + %s"%(mPlug_baseRoll.p_combinedShortName,mPlug_driverRoll.p_combinedShortName,mPlug_midTwistFactor.p_combinedShortName)
                    #log.debug("mid arg %s : %s"%(i,arg_midAdd))
                    #NodeF.argsToNodes(arg_midAdd).doBuild() 

                mPlug_baseRoll = cgmMeta.cgmAttr(i_jnt,'r%s'%orientation[0])
                mPlug_extendTwistFactor = cgmMeta.cgmAttr(i_segmentCurve.mNode,"out_extendTwistFactor_%s"%i,attrType = 'float',lock=True)		    
                mPlug_extendTwist = cgmMeta.cgmAttr(i_segmentCurve.mNode,"out_extendTwist_%s"%i,attrType = 'float',lock=True)	
                mPlug_twistSum = cgmMeta.cgmAttr(i_segmentCurve.mNode,"out_twistSum_%s"%i,attrType = 'float',lock=True)	

                #twistFactor = baseRoll / 2
                arg_extendInfluenceFactor = " %s = %s / 2"%(mPlug_extendTwistFactor.p_combinedShortName,mPlug_baseRoll.p_combinedShortName)
                #extendTwist = factorIn * factor
                arg_extendInfluence = " %s = %s * -%s"%(mPlug_extendTwist.p_combinedShortName,mPlug_factorInfluenceIn.p_combinedShortName,mPlug_extendTwistFactor.p_combinedShortName)
                mPlugs_twistSumOffset.append(mPlug_extendTwist)
                arg_twistSum = " %s = %s"%(mPlug_twistSum.p_combinedShortName,' + '.join([mPlug.p_combinedShortName for mPlug in mPlugs_twistSumOffset]))

                for arg in [arg_extendInfluenceFactor,arg_extendInfluence,arg_twistSum]:
                    log.debug(arg)
                    NodeF.argsToNodes(arg).doBuild() 

                d_mPlugs_rotateGroupDrivers[i] = mPlug_twistSum
    except Exception,error:
        raise StandardError,"%s >> twist | error: %s"%(_str_funcName,error) 
    """
	#A joints roll = current tally + offset
	mPlug_roll = cgmMeta.cgmAttr(i_segmentCurve.mNode,"in_baseRoll_%s"%i,attrType = 'float',lock=True)	
	mPlug_offset = cgmMeta.cgmAttr(i_segmentCurve.mNode,"in_offset_%s"%i,attrType = 'float',lock=False)
	mPlug_twistBase = cgmMeta.cgmAttr(i_segmentCurve.mNode,"twistBase_%s"%i,attrType = 'float',lock=True)
	mPlug_twistResult = cgmMeta.cgmAttr(i_segmentCurve.mNode,"out_twist_%s"%i,attrType = 'float',lock=True)			
	mPlug_roll.doConnectIn("%s.r%s"%(i_jnt.mNode,orientation[0]))

	#This is for our rolling tally of the roll
	mPlugs_rollSumDrivers.append(mPlug_roll)
	mPlugs_rollDrivers = mPlugs_rollSumDrivers	

	#Create the free roll value	
	arg_base = " %s = %s"%(mPlug_twistBase.p_combinedShortName,' + '.join([mPlug.p_combinedShortName for mPlug in mPlugs_rollDrivers]))
	log.debug("'%s' base arg: %s"%(i_jnt.getShortName(),arg_base))
	ml_twistDrivers = [mPlug_twistBase,mPlug_offset]

	arg_twist = " %s = %s "%(mPlug_twistResult.p_combinedShortName,' + '.join([mPlug.p_combinedShortName for mPlug in mPlugs_rollDrivers]))
	log.debug("'%s' arg: %s"%(i_jnt.getShortName(),arg_twist))	

	for arg in [arg_base,arg_twist]:
	    NodeF.argsToNodes(arg).doBuild()

	mPlugs_rollDrivers.append(mPlug_twistResult)
	"""

    try:#>>> Create up locs, follicles -------------------------------------------------------------
        ml_pointOnCurveInfos = []
        ml_upGroups = []

        #First thing we're going to do is create our 'follicles'
        shape = mc.listRelatives(i_segmentCurve.mNode,shapes=True)[0]
        for i,i_jnt in enumerate(ml_jointList):   
            l_closestInfo = distance.returnNearestPointOnCurveInfo(i_jnt.mNode,i_segmentCurve.mNode)
            log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
            #>>> POCI ----------------------------------------------------------------
            i_closestPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
            mc.connectAttr ((shape+'.worldSpace'),(i_closestPointNode.mNode+'.inputCurve'))	

            #> Name
            i_closestPointNode.doStore('cgmName',i_jnt)
            i_closestPointNode.doName()
            #>Set follicle value
            i_closestPointNode.parameter = l_closestInfo['parameter']

            ml_pointOnCurveInfos.append(i_closestPointNode)

            #>>> loc ----------------------------------------------------------------
            #First part of additive full ribbon setup
            #if i_jnt != ml_jointList[-1]:

            i_upLoc = i_jnt.doLoc()#Make up Loc
            i_locRotateGroup = i_jnt.doCreateAt()#group in place
            i_locRotateGroup.parent = ml_driverJoints[i].mNode
            i_locRotateGroup.doStore('cgmName',i_jnt)	    
            i_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
            i_locRotateGroup.doName()

            #Store the rotate group to the joint
            i_jnt.connectChildNode(i_locRotateGroup,'rotateUpGroup','drivenJoint')
            i_zeroGrp = cgmMeta.asMeta( i_locRotateGroup.doGroup(True),'cgmObject',setClass=True )
            i_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
            i_zeroGrp.doName()

            #connect some other data
            i_locRotateGroup.connectChildNode(i_locRotateGroup.parent,'zeroGroup')
            i_locRotateGroup.connectChildNode(i_upLoc,'upLoc')
            mc.makeIdentity(i_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)

            i_upLoc.parent = i_locRotateGroup.mNode
            mc.move(0,10,0,i_upLoc.mNode,os=True)#TODO - make dependent on orientation	
            ml_upGroups.append(i_upLoc)

            #Connect the rotate
            #if extendTwistToEnd:#Need at least x joints
            mPlug_rotateDriver = d_mPlugs_rotateGroupDrivers.get(i) or False
            if mPlug_rotateDriver:
                mPlug_rotateDriver.doConnectOut("%s.r%s"%(i_locRotateGroup.mNode,orientation[0]))
                #ml_twistDrivers.append(mPlug_factorInfluenceOut)

            if i_module:#if we have a module, connect vis
                i_upLoc.overrideEnabled = 1		
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideDisplayType'))    

        #Orient constrain our last joint to our splineIK Joint
        mc.orientConstraint(ml_driverJoints[-1].mNode,ml_jointList[-1].mNode,maintainOffset = True)
    except Exception,error:
        raise StandardError,"%s >> attach and connect | error: %s"%(_str_funcName,error) 

    try:#>>> Scale stuff =============================================================================
        #> Create IK effectors,Create distance nodes
        l_iIK_effectors = []
        l_iIK_handles = []  
        ml_distanceObjects = []
        ml_distanceShapes = []  
        for i,i_jnt in enumerate(ml_jointList[:-1]):
            ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                     endEffector = ml_jointList[i+1].mNode,
                                     setupForRPsolver = True, solver = 'ikRPsolver',
                                     enableHandles=True )
            #Handle
            i_IK_Handle = cgmMeta.asMeta(ik_buffer[0],'cgmObject',setClass=True)
            i_IK_Handle.parent = ml_driverJoints[i+1].mNode
            i_IK_Handle.doStore('cgmName',i_jnt)    
            i_IK_Handle.doName()

            #Effector
            i_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
            #i_IK_Effector.doStore('cgmName',i_jnt)    
            i_IK_Effector.doName()

            l_iIK_handles.append(i_IK_Handle)
            l_iIK_effectors.append(i_IK_Effector)

            if i_module:#if we have a module, connect vis
                i_IK_Handle.overrideEnabled = 1		
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideDisplayType'))    

            #>> Distance nodes
            i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
            i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
            i_distanceObject.doStore('cgmName',i_jnt)
            i_distanceObject.addAttr('cgmType','measureNode',lock=True)
            i_distanceObject.doName(nameShapes = True)
            i_distanceObject.parent = i_grp.mNode#parent it
            i_distanceObject.overrideEnabled = 1
            i_distanceObject.overrideVisibility = 1

            #Connect things
            mc.connectAttr ((ml_pointOnCurveInfos[i].mNode+'.position'),(i_distanceShape.mNode+'.startPoint'))
            mc.connectAttr ((ml_pointOnCurveInfos[i+1].mNode+'.position'),(i_distanceShape.mNode+'.endPoint'))

            ml_distanceObjects.append(i_distanceObject)
            ml_distanceShapes.append(i_distanceShape)


            if i_module:#Connect hides if we have a module instance:
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideDisplayType'))    

        #>> Second part for the full twist setup
        aimChannel = orientation[0]  
    except Exception,error:
        raise StandardError,"%s >> scale guts | error: %s"%(_str_funcName,error) 

    try:#fix twists
        for i,i_jnt in enumerate(ml_jointList[:-1]):
            rotBuffer = mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)
            log.debug("rotBuffer: %s"%rotBuffer)
            #Create the poleVector
            poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,l_iIK_handles[i].mNode)  	
            IKHandle_fixTwist(l_iIK_handles[i])

            if mc.xform (i_jnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
                log.debug("Found the following on '%s': %s"%(i_jnt.getShortName(),mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)))
    except Exception,error:
        raise StandardError,"%s >> fix twists | error: %s"%(_str_funcName,error) 

    try:#>>>Hook up scales
        #==========================================================================
        #Buffer
        i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
        i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
        i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, minValue = 0.0001, attrType='float')    
        #i_jntScaleBufferNode.addAttr('segmentScale',value = 1.0, attrType='float',minValue = 0.0) 

        i_jntScaleBufferNode.doName()
        ml_distanceAttrs = []
        ml_resultAttrs = []

        i_jntScaleBufferNode.connectParentNode(i_segmentCurve.mNode,'segmentCurve','scaleBuffer')
        ml_mainMDs = []
        for i,i_jnt in enumerate(ml_jointList[:-1]):
            #Make some attrs
            i_attrDist= cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"distance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)
            i_attrNormalBaseDist = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"normalizedBaseDistance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)			
            i_attrNormalDist = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"normalizedDistance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)		
            i_attrResult = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	
            i_attrTransformedResult = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaledScaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	

            #i_attrResultTScale = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaleTResult_%s"%i,attrType = 'float',initialValue=0,lock=True)	

            #Store our distance base to our buffer
            try:i_jntScaleBufferNode.store(ml_distanceShapes[i].distance)#Store to our buffer
            except Exception,error:
                log.error(error)
                raise StandardError,"Failed to store joint distance: %s"%ml_distanceShapes[i].mNode

            #Create the normalized base distance
            i_mdNormalBaseDist = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
            i_mdNormalBaseDist.operation = 1
            i_mdNormalBaseDist.doStore('cgmName',i_jnt)
            i_mdNormalBaseDist.addAttr('cgmTypeModifier','normalizedBaseDist')
            i_mdNormalBaseDist.doName()

            attributes.doConnectAttr('%s.masterScale'%(i_jntScaleBufferNode.mNode),#>>
                                     '%s.%s'%(i_mdNormalBaseDist.mNode,'input1X'))
            attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                     '%s.%s'%(i_mdNormalBaseDist.mNode,'input2X'))	
            i_attrNormalBaseDist.doConnectIn('%s.%s'%(i_mdNormalBaseDist.mNode,'output.outputX'))


            #Create the normalized distance
            i_mdNormalDist = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
            i_mdNormalDist.operation = 1
            i_mdNormalDist.doStore('cgmName',i_jnt)
            i_mdNormalDist.addAttr('cgmTypeModifier','normalizedDist')
            i_mdNormalDist.doName()

            attributes.doConnectAttr('%s.masterScale'%(i_jntScaleBufferNode.mNode),#>>
                                     '%s.%s'%(i_mdNormalDist.mNode,'input1X'))
            i_attrDist.doConnectOut('%s.%s'%(i_mdNormalDist.mNode,'input2X'))	
            i_attrNormalDist.doConnectIn('%s.%s'%(i_mdNormalDist.mNode,'output.outputX'))

            """
            attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
                                     '%s.%s'%(i_md.mNode,'input1X'))
            attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                     '%s.%s'%(i_md.mNode,'input2X'))"""

            #Create the mdNode
            i_mdSegmentScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
            i_mdSegmentScale.operation = 2
            i_mdSegmentScale.doStore('cgmName',i_jnt)
            i_mdSegmentScale.addAttr('cgmTypeModifier','segmentScale')
            i_mdSegmentScale.doName()
            i_attrDist.doConnectOut('%s.%s'%(i_mdSegmentScale.mNode,'input1X'))	
            i_attrNormalBaseDist.doConnectOut('%s.%s'%(i_mdSegmentScale.mNode,'input2X'))
            i_attrResult.doConnectIn('%s.%s'%(i_mdSegmentScale.mNode,'output.outputX'))


            #Create the trans scale mdNode
            """
            i_mdTransScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
            i_mdTransScale.operation = 1
            i_mdTransScale.doStore('cgmName',i_jnt)
            i_mdTransScale.addAttr('cgmTypeModifier','transScale')
            i_mdTransScale.doName()
            attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                     '%s.%s'%(i_mdTransScale.mNode,'input1X'))
            attributes.doConnectAttr(i_attrResult.p_combinedName,#>>
                                     '%s.%s'%(i_mdTransScale.mNode,'input2X'))

            #TranslateScales
            attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
                                     "%s.t%s"%(ml_jointList[i+1].mNode,orientation[0]))"""

            #Connect to the joint
            ml_distanceAttrs.append(i_attrDist)
            ml_resultAttrs.append(i_attrResult)

            if connectBy == 'translate':
                #Still not liking the way this works with translate scale. looks fine till you add squash and stretch
                try:
                    i_attrDist.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))		        
                    i_attrNormalDist.doConnectOut('%s.t%s'%(ml_jointList[i+1].mNode,orientation[0]))
                    i_attrNormalDist.doConnectOut('%s.t%s'%(ml_driverJoints[i+1].mNode,orientation[0]))    

                except Exception,error:
                    log.error(error)
                    raise StandardError,"Failed to connect joint attrs by translate: %s"%i_jnt.mNode	
            else:
                try:
                    i_attrDist.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))		        
                    i_attrResult.doConnectOut('%s.s%s'%(i_jnt.mNode,orientation[0]))
                    i_attrResult.doConnectOut('%s.s%s'%(ml_driverJoints[i].mNode,orientation[0]))

                except Exception,error:
                    log.error(error)
                    raise StandardError,"Failed to connect joint attrs by scale: %s"%i_jnt.mNode

            ml_mainMDs.append(i_mdSegmentScale)#store the md

        for axis in [orientation[1],orientation[2]]:
            attributes.doConnectAttr('%s.s%s'%(i_jnt.mNode,axis),#>>
                                     '%s.s%s'%(ml_driverJoints[i].mNode,axis))	 	
    except Exception,error:
        raise StandardError,"%s >> scale wiring | error: %s"%(_str_funcName,error) 



    try:#Connect last joint scale to second to last
        for axis in ['scaleX','scaleY','scaleZ']:
            attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                     '%s.%s'%(ml_jointList[-1].mNode,axis))	 

        mc.pointConstraint(ml_driverJoints[0].mNode,ml_jointList[0].mNode,maintainOffset = False)
    except Exception,error:
        raise StandardError,"%s >> constrain | error: %s"%(_str_funcName,error) 


    #Store info to the segment curve

    try:#>>> Store em all to our instance
        i_segmentCurve.connectChildNode(i_jntScaleBufferNode,'scaleBuffer','segmentCurve')
        i_segmentCurve.msgList_connect('drivenJoints',ml_jointList,'segmentCurve')       
        i_segmentCurve.msgList_connect('driverJoints',ml_driverJoints,'segmentCurve')   
    except Exception,error:
        raise StandardError,"%s >> final connect | error: %s"%(_str_funcName,error) 


    d_return = {'mi_segmentCurve':i_segmentCurve,'segmentCurve':i_segmentCurve.mNode,'mi_ikHandle':i_ikHandle,'mi_segmentGroup':i_grp,
                'l_driverJoints':[i_jnt.getShortName() for i_jnt in ml_driverJoints],'ml_driverJoints':ml_driverJoints,
                'scaleBuffer':i_jntScaleBufferNode.mNode,'mi_scaleBuffer':i_jntScaleBufferNode,'mPlug_extendTwist':mPlug_factorInfluenceIn,
                'l_drivenJoints':jointList,'ml_drivenJoints':ml_jointList}

    return d_return


def createSegmentCurve3(jointList,orientation = 'zyx',secondaryAxis = None, 
                        baseName = None, connectBy = 'trans', moduleInstance = None):
    """
    Stored meta data on completed segment:
    scaleBuffer
    drivenJoints     
    driverJoints 
    """
    if type(jointList) not in [list,tuple]:jointList = [jointList]

    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]

    i_module = False
    i_rigNull = False
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
                i_module = moduleInstance
                i_rigNull = i_module.rigNull
    except:
        log.error("Not a module instance, ignoring: '%s'"%moduleInstance)

    if i_module:
        if baseName is None:
            baseName = i_module.getPartNameBase()#Get part base name	    
            log.debug('baseName set to module: %s'%baseName)	    	    
    if baseName is None:baseName = 'testSegmentCurve'

    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','segmentStuff', lock=True)
    i_grp.doName()

    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]#Initialize original joints

    if not moduleInstance:#if it is, we can assume it's right
        if secondaryAxis is None:
            raise StandardError,"createControlSurfaceSegment>>> Must have secondaryAxis arg if no moduleInstance is passed"
        for i_jnt in ml_jointList:
            """
	    Cannot iterate how important this step is. Lost a day trying to trouble shoot why one joint chain worked and another didn't.
	    WILL NOT connect right without this.
	    """
            joints.orientJoint(i_jnt.mNode,orientation,secondaryAxis)


    #Joints
    #=========================================================================
    #Create spline IK joints
    #>>Surface chain    
    l_driverJoints = mc.duplicate(jointList,po=True,ic=True,rc=True)
    ml_driverJoints = []
    for i,j in enumerate(l_driverJoints):
        i_j = cgmMeta.asMeta(j,'cgmObject',setClass=True)
        i_j.doCopyNameTagsFromObject(ml_jointList[i].mNode,ignore=['cgmTypeModifier','cgmType'])
        #i_j.addAttr('cgmName',baseName,lock=True)
        i_j.addAttr('cgmTypeModifier','splineIK',attrType='string')
        i_j.doName()
        l_driverJoints[i] = i_j.mNode
        ml_driverJoints.append(i_j)

    #Create Curve
    i_splineSolver = cgmMeta.cgmNode(nodeType = 'ikSplineSolver')
    buffer = mc.ikHandle( sj=ml_driverJoints[0].mNode, ee=ml_driverJoints[-1].mNode,simplifyCurve=False,
                          solver = i_splineSolver.mNode, ns = 4, rootOnCurve=True,forceSolver = True,
                          createCurve = True,snapHandleFlagToggle=True )  

    i_segmentCurve = cgmMeta.asMeta( buffer[2],'cgmObject',setClass=True )
    i_segmentCurve.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_segmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
    i_segmentCurve.doName()

    if i_module:#if we have a module, connect vis
        i_segmentCurve.overrideEnabled = 1		
        cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_segmentCurve.mNode,'overrideVisibility'))    
        cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_segmentCurve.mNode,'overrideDisplayType'))    

    i_ikHandle = cgmMeta.asMeta( buffer[0],'cgmObject',setClass=True )
    i_ikHandle.doName()
    i_ikEffector = cgmMeta.asMeta( buffer[1],'cgmObject',setClass=True )
    i_ikHandle.parent = i_grp.mNode

    i_segmentCurve.connectChildNode(i_grp,'segmentGroup','owner')

    #Joints
    #=========================================================================
    ml_ = []
    ml_pointOnCurveInfos = []
    ml_upGroups = []

    #First thing we're going to do is create our follicles
    shape = mc.listRelatives(i_segmentCurve.mNode,shapes=True)[0]
    for i,i_jnt in enumerate(ml_jointList):   
        l_closestInfo = distance.returnNearestPointOnCurveInfo(i_jnt.mNode,i_segmentCurve.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> """Follicle""" =======================================================
        i_closestPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
        mc.connectAttr ((shape+'.worldSpace'),(i_closestPointNode.mNode+'.inputCurve'))	

        #> Name
        i_closestPointNode.doStore('cgmName',i_jnt)
        i_closestPointNode.doName()
        #>Set follicle value
        i_closestPointNode.parameter = l_closestInfo['parameter']

        ml_pointOnCurveInfos.append(i_closestPointNode)


        #>>> loc
        #First part of full ribbon wist setup
        if i_jnt != ml_jointList[-1]:
            i_upLoc = i_jnt.doLoc()#Make up Loc
            i_locRotateGroup = i_jnt.doCreateAt()#group in place
            i_locRotateGroup.parent = ml_driverJoints[i].mNode
            i_locRotateGroup.doStore('cgmName',i_jnt)	    
            i_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
            i_locRotateGroup.doName()

            #Store the rotate group to the joint
            i_jnt.connectChildNode(i_locRotateGroup,'rotateUpGroup','drivenJoint')
            i_zeroGrp = cgmMeta.asMeta( i_locRotateGroup.doGroup(True),'cgmObject',setClass=True )
            i_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
            i_zeroGrp.doName()
            #connect some other data
            i_locRotateGroup.connectChildNode(i_locRotateGroup.parent,'zeroGroup')
            i_locRotateGroup.connectChildNode(i_upLoc,'upLoc')
            mc.makeIdentity(i_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)

            i_upLoc.parent = i_locRotateGroup.mNode
            mc.move(0,10,0,i_upLoc.mNode,os=True)#TODO - make dependent on orientation	
            ml_upGroups.append(i_upLoc)


            if i_module:#if we have a module, connect vis
                i_upLoc.overrideEnabled = 1		
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideDisplayType'))    


    #Orient constrain our last joint to our splineIK Joint
    mc.orientConstraint(ml_driverJoints[-1].mNode,ml_jointList[-1].mNode,maintainOffset = True)

    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    ml_distanceObjects = []
    ml_distanceShapes = []  
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.asMeta(ik_buffer[0],'cgmObject',setClass=True)
        i_IK_Handle.parent = ml_driverJoints[i+1].mNode
        i_IK_Handle.doStore('cgmName',i_jnt)    
        i_IK_Handle.doName()

        #Effector
        i_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
        #i_IK_Effector.doStore('cgmName',i_jnt)    
        i_IK_Effector.doName()

        l_iIK_handles.append(i_IK_Handle)
        l_iIK_effectors.append(i_IK_Effector)


        if i_module:#if we have a module, connect vis
            i_IK_Handle.overrideEnabled = 1		
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideDisplayType'))    

        #>> Distance nodes
        i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
        i_distanceObject.doStore('cgmName',i_jnt)
        i_distanceObject.addAttr('cgmType','measureNode',lock=True)
        i_distanceObject.doName(nameShapes = True)
        i_distanceObject.parent = i_grp.mNode#parent it
        i_distanceObject.overrideEnabled = 1
        i_distanceObject.overrideVisibility = 1

        #Connect things
        mc.connectAttr ((ml_pointOnCurveInfos[i].mNode+'.position'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_pointOnCurveInfos[i+1].mNode+'.position'),(i_distanceShape.mNode+'.endPoint'))

        ml_distanceObjects.append(i_distanceObject)
        ml_distanceShapes.append(i_distanceShape)


        if i_module:#Connect hides if we have a module instance:
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideDisplayType'))    

    #>> Second part for the full twist setup
    aimChannel = orientation[0]  
    fixOptions = [0,90,180,-90,-180]      

    for i,i_jnt in enumerate(ml_jointList[:-1]):
        rotBuffer = mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)
        log.debug("rotBuffer: %s"%rotBuffer)
        #Create the poleVector
        poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,l_iIK_handles[i].mNode)  	
        IKHandle_fixTwist(l_iIK_handles[i])
        """
	optionCnt = 0
	while not cgmMath.isFloatEquivalent((mc.getAttr(i_jnt.mNode+'.r'+aimChannel)),0):
	    log.debug("%s.r%s: %s"%(i_jnt.getShortName(),aimChannel,mc.getAttr(i_jnt.mNode+'.r'+aimChannel)))
	    log.debug ("Trying the following for '%s':%s" %(l_iIK_handles[i].getShortName(),fixOptions[optionCnt]))
	    attributes.doSetAttr(l_iIK_handles[i].mNode,'twist',fixOptions[optionCnt])
	    optionCnt += 1
	    if optionCnt == 4:
		raise StandardError,"failed to find a good twist value to zero out poleVector: %s"%(i_jnt.getShortName())
	    """
        if mc.xform (i_jnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
            log.debug("Found the following on '%s': %s"%(i_jnt.getShortName(),mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)))

    #>>>Hook up scales
    #==========================================================================
    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    i_jntScaleBufferNode.doName()
    ml_distanceAttrs = []
    ml_resultAttrs = []

    i_jntScaleBufferNode.connectParentNode(i_segmentCurve.mNode,'segmentCurve','scaleBuffer')
    ml_mainMDs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        #Make some attrs
        i_attrDist= cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"distance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)
        i_attrNormalBaseDist = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"normalizedBaseDistance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)			
        i_attrNormalDist = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"normalizedDistance_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)		
        i_attrResult = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	
        i_attrTransformedResult = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaledScaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	

        #i_attrResultTScale = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaleTResult_%s"%i,attrType = 'float',initialValue=0,lock=True)	

        #Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(ml_distanceShapes[i].distance)#Store to our buffer
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to store joint distance: %s"%ml_distanceShapes[i].mNode

        #Create the normalized base distance
        i_mdNormalBaseDist = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_mdNormalBaseDist.operation = 1
        i_mdNormalBaseDist.doStore('cgmName',i_jnt)
        i_mdNormalBaseDist.addAttr('cgmTypeModifier','normalizedBaseDist')
        i_mdNormalBaseDist.doName()

        attributes.doConnectAttr('%s.masterScale'%(i_jntScaleBufferNode.mNode),#>>
                                 '%s.%s'%(i_mdNormalBaseDist.mNode,'input1X'))
        attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                 '%s.%s'%(i_mdNormalBaseDist.mNode,'input2X'))	
        i_attrNormalBaseDist.doConnectIn('%s.%s'%(i_mdNormalBaseDist.mNode,'output.outputX'))



        #Create the normalized distance
        i_mdNormalDist = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_mdNormalDist.operation = 1
        i_mdNormalDist.doStore('cgmName',i_jnt)
        i_mdNormalDist.addAttr('cgmTypeModifier','normalizedDist')
        i_mdNormalDist.doName()

        attributes.doConnectAttr('%s.masterScale'%(i_jntScaleBufferNode.mNode),#>>
                                 '%s.%s'%(i_mdNormalDist.mNode,'input1X'))
        i_attrDist.doConnectOut('%s.%s'%(i_mdNormalDist.mNode,'input2X'))	
        i_attrNormalDist.doConnectIn('%s.%s'%(i_mdNormalDist.mNode,'output.outputX'))



        """
	attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
	                         '%s.%s'%(i_md.mNode,'input1X'))
	attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
	                         '%s.%s'%(i_md.mNode,'input2X'))"""

        #Create the mdNode
        i_mdSegmentScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_mdSegmentScale.operation = 2
        i_mdSegmentScale.doStore('cgmName',i_jnt)
        i_mdSegmentScale.addAttr('cgmTypeModifier','segmentScale')
        i_mdSegmentScale.doName()
        i_attrDist.doConnectOut('%s.%s'%(i_mdSegmentScale.mNode,'input1X'))	
        i_attrNormalBaseDist.doConnectOut('%s.%s'%(i_mdSegmentScale.mNode,'input2X'))
        i_attrResult.doConnectIn('%s.%s'%(i_mdSegmentScale.mNode,'output.outputX'))

        #Create the trans scale mdNode
        """
	i_mdTransScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_mdTransScale.operation = 1
	i_mdTransScale.doStore('cgmName',i_jnt)
	i_mdTransScale.addAttr('cgmTypeModifier','transScale')
	i_mdTransScale.doName()
	attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
	                         '%s.%s'%(i_mdTransScale.mNode,'input1X'))
	attributes.doConnectAttr(i_attrResult.p_combinedName,#>>
	                         '%s.%s'%(i_mdTransScale.mNode,'input2X'))

	#TranslateScales
	attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
	                         "%s.t%s"%(ml_jointList[i+1].mNode,orientation[0]))"""

        #Connect to the joint
        ml_distanceAttrs.append(i_attrDist)
        ml_resultAttrs.append(i_attrResult)

        if connectBy == 'translate':
            #Still not liking the way this works with translate scale. looks fine till you add squash and stretch
            try:
                i_attrDist.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))		        
                i_attrNormalDist.doConnectOut('%s.t%s'%(ml_jointList[i+1].mNode,orientation[0]))
                i_attrNormalDist.doConnectOut('%s.t%s'%(ml_driverJoints[i+1].mNode,orientation[0]))    

            except Exception,error:
                log.error(error)
                raise StandardError,"Failed to connect joint attrs by scale: %s"%i_jnt.mNode


        else:
            try:
                i_attrDist.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))		        
                i_attrResult.doConnectOut('%s.s%s'%(i_jnt.mNode,orientation[0]))
                i_attrResult.doConnectOut('%s.s%s'%(ml_driverJoints[i].mNode,orientation[0]))

            except Exception,error:
                log.error(error)
                raise StandardError,"Failed to connect joint attrs by scale: %s"%i_jnt.mNode

        ml_mainMDs.append(i_mdSegmentScale)#store the md

        for axis in [orientation[1],orientation[2]]:
            attributes.doConnectAttr('%s.s%s'%(i_jnt.mNode,axis),#>>
                                     '%s.s%s'%(ml_driverJoints[i].mNode,axis))	 	


    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
        attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))	 

    mc.pointConstraint(ml_driverJoints[0].mNode,ml_jointList[0].mNode,maintainOffset = False)

    #Store info to the segment curve

    #>>> Store em all to our instance
    i_segmentCurve.connectChildNode(i_jntScaleBufferNode,'scaleBuffer','segmentCurve')
    i_segmentCurve.msgList_connect('drivenJoints',ml_jointList,'segmentCurve')       
    i_segmentCurve.msgList_connect('driverJoints',ml_driverJoints,'segmentCurve')   

    return {'mi_segmentCurve':i_segmentCurve,'segmentCurve':i_segmentCurve.mNode,'mi_ikHandle':i_ikHandle,'mi_segmentGroup':i_grp,
            'l_driverJoints':[i_jnt.getShortName() for i_jnt in ml_driverJoints],'ml_driverJoints':ml_driverJoints,
            'scaleBuffer':i_jntScaleBufferNode.mNode,'mi_scaleBuffer':i_jntScaleBufferNode,
            'l_drivenJoints':jointList,'ml_drivenJoints':ml_jointList}



def create_spaceLocatorForObject(obj,parentTo = False):
    raise Exception,"use cgm.core.rigger.lib.spacePivot_utils"
    try:#Get size
        i_obj = cgmMeta.validateObjArg(obj,cgmMeta.cgmObject,noneValid=False)    
        i_parent = cgmMeta.validateObjArg(parentTo,cgmMeta.cgmObject,noneValid=True)    
        bbSize = distance.returnBoundingBoxSize(i_obj.mNode,True)
        size = max(bbSize)
    except Exception,error:raise Exception,"%s >> get info | %s"%(str_shortName,error)  

    _str_funcName = "create_spaceLocatorForObject(%s)"%i_obj.p_nameShort  
    log.debug(">>> %s >>> "%(_str_funcName) + "="*75)  

    try:#>>>Create #====================================================
        from cgm.core.lib import curve_Utils as CURVES
        #CURVES.create_controlCurve(i_obj.mNode,'jack')
        i_control = cgmMeta.asMeta(CURVES.create_controlCurve(i_obj.mNode,'jack')[0],'cgmObject',setClass=True)
        log.info(i_control)
        try:l_color = curves.returnColorsFromCurve(i_obj.mNode)
        except Exception,error:raise Exception,"color | %s"%(error)          
        log.debug("l_color: %s"%l_color)
        curves.setColorByIndex(i_control.mNode,l_color[0])
    except Exception,error:raise Exception,"%s >> create | %s"%(_str_funcName,error)  
    
    try:#>>>Snap and Lock
        #====================================================	
        SNAP.go(i_control,i_obj.mNode)
    except Exception,error:raise Exception,"%s >> snapNLock | %s"%(_str_funcName,error)  
    
    try:#>>>Copy Transform
        #====================================================   
        i_newTransform = i_obj.doCreateAt()

        #Need to move this to default cgmNode stuff
        mBuffer = i_control
        i_newTransform.doCopyNameTagsFromObject(i_control.mNode)
        curves.parentShapeInPlace(i_newTransform.mNode,i_control.mNode)#Parent shape
        i_newTransform.parent = mBuffer.parent#Copy parent
        i_control = i_newTransform
        mc.delete(mBuffer.mNode)
    except Exception,error:raise Exception,"%s >> copy transform | %s"%(_str_funcName,error)  
    
    try:#>>>Register
        #====================================================    
        #Attr
        i = ATTR.get_nextAvailableSequentialAttrIndex(i_obj.mNode,"pivot")
        str_pivotAttr = str("pivot_%s"%i)
        str_objName = str(i_obj.getShortName())
        str_pivotName = str(i_control.getShortName())
    except Exception,error:raise Exception,"%s >> register | %s"%(_str_funcName,error)  
    
    try:#Build the network
        i_obj.addAttr(str_pivotAttr,enumName = 'off:lock:on', defaultValue = 2, value = 0, attrType = 'enum',keyable = False, hidden = False)
        i_control.overrideEnabled = 1
        d_ret = NodeF.argsToNodes("%s.overrideVisibility = if %s.%s > 0"%(str_pivotName,str_objName,str_pivotAttr)).doBuild()
        log.debug(d_ret)
        d_ret = NodeF.argsToNodes("%s.overrideDisplayType = if %s.%s == 2:0 else 2"%(str_pivotName,str_objName,str_pivotAttr)).doBuild()
        log.debug(d_ret)
    except Exception,error:raise Exception,"%s >> network | %s"%(_str_funcName,error)  
    
    try:
        for shape in mc.listRelatives(i_control.mNode,shapes=True,fullPath=True):
            log.debug(shape)
            mc.connectAttr("%s.overrideVisibility"%i_control.mNode,"%s.overrideVisibility"%shape,force=True)
            mc.connectAttr("%s.overrideDisplayType"%i_control.mNode,"%s.overrideDisplayType"%shape,force=True)
    except Exception,error:raise Exception,"%s >> shape connect | %s"%(_str_funcName,error)  
    
    try:#Vis 
        #>>>Name stuff
        #====================================================
        cgmMeta.cgmAttr(i_control,'visibility',lock=True,hidden=True)   
        i_control = cgmMeta.validateObjArg(i_control,'cgmControl',setClass = True)
        i_control.doStore('cgmName',i_obj)
        i_control.addAttr('cgmType','controlAnim',lock=True)    
        i_control.addAttr('cgmIterator',"%s"%i,lock=True)        
        i_control.addAttr('cgmTypeModifier','spacePivot',lock=True)

        i_control.doName(nameShapes=True)

        i_control.addAttr('cgmAlias',(i_obj.getNameAlias()+'_pivot_%s'%i),lock=True)
    except Exception,error:raise Exception,"%s >> vis | %s"%(_str_funcName,error)  
    
    try:#Store on object
        #====================================================    
        i_obj.addAttr("spacePivots", attrType = 'message',lock=True)
        if i_control.getLongName() not in i_obj.getMessage('spacePivots',True):
            buffer = i_obj.getMessage('spacePivots',True)
            buffer.append(i_control.mNode)
            i_obj.msgList_append('spacePivots',buffer,'controlTarget')
        log.debug("spacePivots: %s"%i_obj.msgList_get('spacePivots',asMeta = True))
    except Exception,error:raise Exception,"%s >> store | %s"%(_str_funcName,error)  

    try:#parent
        if i_parent:
            i_control.parent = i_parent.mNode
            i_constraintGroup = (cgmMeta.asMeta(i_control.doGroup(True),'cgmObject',setClass=True))
            i_constraintGroup.addAttr('cgmTypeModifier','constraint',lock=True)
            i_constraintGroup.doName()
            i_control.connectChildNode(i_constraintGroup,'constraintGroup','groupChild')	

            log.debug("constraintGroup: '%s'"%i_constraintGroup.getShortName())		
    except Exception,error:raise Exception,"%s >> parent | %s"%(_str_funcName,error) 

    try:#change to cgmControl
        i_control = cgmMeta.asMeta(i_control.mNode,'cgmControl', setClass=1)
    except Exception,error:raise Exception,"%s >> cgmControl conversion | %s"%(_str_funcName,error) 

    return i_control


def create_traceCurve(control,targetObject,parentTo = False, lock = True):
    #Get size
    i_control = cgmMeta.validateObjArg(control,cgmMeta.cgmObject,noneValid=True)    
    i_target = cgmMeta.validateObjArg(targetObject,cgmMeta.cgmObject,noneValid=True)        
    i_parent = cgmMeta.validateObjArg(parentTo,cgmMeta.cgmObject,noneValid=True)  

    if not i_control:
        raise StandardError,"create_traceCurve>> No control: '%s"%control
    if not i_target:
        raise StandardError,"create_traceCurve>> No targetObject: '%s"%targetObject

    #>>>Create
    #====================================================
    i_crv = cgmMeta.cgmObject( mc.curve (d=1, p = [i_control.getPosition(),i_target.getPosition()] , os=True) )
    log.debug(i_target.getMayaType())
    if i_target.getMayaType() == 'curve':
        l_color = curves.returnColorsFromCurve(i_target.mNode)
        log.debug("l_color: %s"%l_color)
        curves.setColorByIndex(i_crv.mNode,l_color[0])

    #>>>Connect
    #====================================================   
    ml_locs = []
    for i,i_obj in enumerate([i_control,i_target]):#Connect each of our handles ot the cv's of the curve we just made
        i_loc = i_obj.doLoc(fastMode = True)
        i_loc.doStore('cgmName',i_obj) #Add name tag
        i_loc.addAttr('cgmTypeModifier',value = 'traceCurve', attrType = 'string', lock=True) #Add Type
        i_loc.v = False # Turn off visibility
        i_loc.doName()	
        ml_locs.append(i_loc)

        i_obj.connectChildNode(i_loc.mNode,'traceLoc','owner')
        mc.pointConstraint(i_obj.mNode,i_loc.mNode,maintainOffset = False)#Point contraint loc to the object

        mc.connectAttr ( (i_loc.mNode+'.translate') , ('%s%s%i%s' % (i_crv.mNode, '.controlPoints[', i, ']')), f=True )

    #>>>Name
    #====================================================  
    i_crv = cgmMeta.validateObjArg(i_crv,'cgmObject',setClass = True)
    i_crv.doStore('cgmName',i_target)
    i_crv.addAttr('cgmTypeModifier',value = 'trace', attrType = 'string', lock=True)
    i_crv.doName()

    i_target.connectChildNode(i_crv.mNode,'traceCurve','owner')

    if lock:
        i_crv.overrideEnabled = 1
        i_crv.overrideDisplayType = 2
        for shape in mc.listRelatives(i_crv.mNode,shapes=True,fullPath=True):
            mc.connectAttr("%s.overrideVisibility"%i_target.mNode,"%s.overrideVisibility"%shape,force=True)
            mc.setAttr("%s.overrideDisplayType"%shape,2)
            #mc.connectAttr("%s.overrideDisplayType"%i_control.mNode,"%s.overrideDisplayType"%shape,force=True)


    return {'mi_curve':i_crv,'curve':i_crv.mNode,'ml_locs':ml_locs,'l_locs':[i_loc.mNode for i_loc in ml_locs]}


def matchValue_iterator(matchObj = None, matchAttr = None, drivenObj = None, drivenAttr = None, driverAttr = None, 
                        minIn = -180, maxIn = 180, maxIterations = 40, matchValue = None):
    """
    Started with Jason Schleifer's afr js_iterator and have 'tweaked'
    """
    if type(minIn) not in [float,int]:raise StandardError,"matchValue_iterator>>> bad minIn: %s"%minIn
    if type(maxIn) not in [float,int]:raise StandardError,"matchValue_iterator>>> bad maxIn: %s"%maxIn

    __matchMode__ = False
    #>>> Data gather and arg check        
    mi_matchObj = cgmMeta.validateObjArg(matchObj,cgmMeta.cgmObject,noneValid=True)
    d_matchAttr = cgmMeta.validateAttrArg(matchAttr,noneValid=True)
    if mi_matchObj:
        __matchMode__ = 'matchObj'
        minValue = minIn
        maxValue = maxIn 

    elif d_matchAttr:
        __matchMode__ = 'matchAttr'
    elif matchValue is not None:
        __matchMode__ = 'value'
    else:
        raise StandardError,"matchValue_iterator>>> No match given. No matchValue given"

    __drivenMode__ = False
    mi_drivenObj = cgmMeta.validateObjArg(drivenObj,cgmMeta.cgmObject,noneValid=True)
    d_drivenAttr = cgmMeta.validateAttrArg(drivenAttr,noneValid=True)    
    if mi_drivenObj:#not an object match but a value
        __drivenMode__ = 'object'
    elif d_drivenAttr:
        __drivenMode__ = 'attr'
        mPlug_driven = d_drivenAttr['mi_plug']
        f_baseValue = mPlug_driven.value	
        minRange = float(f_baseValue - 10)
        maxRange = float(f_baseValue + 10)  
        mPlug_driven
        log.debug("matchValue_iterator>>> Attr mode. Attr: %s  | baseValue: %s "%(mPlug_driven.p_combinedShortName,f_baseValue))						
    else:
        raise StandardError,"matchValue_iterator>>> No driven given"

    d_driverAttr = cgmMeta.validateAttrArg(driverAttr,noneValid=False)
    mPlug_driver = d_driverAttr['mi_plug']
    if not mPlug_driver:
        raise StandardError,"matchValue_iterator>>> No driver"	

    log.debug("matchValue_iterator>>> Source mode: %s | Target mode: %s | Driver: %s"%(__matchMode__,__drivenMode__,mPlug_driver.p_combinedShortName))  
    #===========================================================================================================
    #>>>>>>> Meat
    #>>> Check autokey
    b_autoFrameState = mc.autoKeyframe(q=True, state = True)
    if b_autoFrameState:
        mc.autoKeyframe(state = False)

    minValue = float(minIn)
    maxValue = float(maxIn)  
    f_lastClosest = None
    f_lastValue = None
    cnt_sameValue = 0
    b_matchFound = None
    b_firstIter = True
    d_valueToSetting = {}

    #Source type: value
    for i in range(maxIterations):
        if __matchMode__ == 'value':
            if __drivenMode__ == 'attr':
                log.debug("matchValue_iterator>>> Step : %s | min: %s | max: %s | baseValue: %s | current: %s"%(i,minValue,maxValue,f_baseValue,mPlug_driven.value))  					
                if cgmMath.isFloatEquivalent(mPlug_driven.value,matchValue,3):
                    log.debug("matchValue_iterator>>> Match found: %s == %s | %s: %s | step: %s"%(mPlug_driven.p_combinedShortName,matchValue,mPlug_driver.p_combinedShortName,minValue,i))  			    
                    b_matchFound = minValue
                    break
                f_currentDist = abs(matchValue-mPlug_driven.value)
                mPlug_driver.value = minValue#Set to min
                f_minDist = abs(matchValue-mPlug_driven.value)#get Dif
                f_minSetValue = mPlug_driven.value
                mPlug_driver.value = maxValue#Set to max
                f_maxDist = abs(matchValue-mPlug_driven.value)#Get dif
                f_maxSetValue = mPlug_driven.value

                f_half = ((maxValue-minValue)/2.0) + minValue#get half
                #First find range
                if f_minSetValue > matchValue or f_maxSetValue < matchValue:
                    log.error("Bad range, alternate range find. minSetValue = %s > %s < maxSetValue = %s"%(f_minSetValue,matchValue,f_maxSetValue))

                if not cgmMath.isFloatEquivalent(matchValue,0) and not cgmMath.isFloatEquivalent(minValue,0) and not cgmMath.isFloatEquivalent(f_minSetValue,0):
                    #if none of our values are 0, this is really fast
                    minValue = (minValue * matchValue)/f_minSetValue
                    log.debug("matchValue_iterator>>> Equated: %s"%minValue)		    
                    f_closest = f_minDist
                    mPlug_driver.value = minValue#Set to min			
                else:	
                    if f_minDist>f_maxDist:#if min dif greater, use half as new min
                        if f_half < minIn:
                            raise StandardError, "half min less than minValue"
                            f_half = minIn
                        minValue = f_half
                        #log.debug("matchValue_iterator>>>Going up")
                        f_closest = f_minDist
                    else:
                        if f_half > maxIn:
                            raise StandardError, "half max less than maxValue"			    
                            f_half = maxIn			
                        maxValue = f_half
                        #log.debug("matchValue_iterator>>>Going down")  
                        f_closest = f_maxDist

                #Old method
                """
		mPlug_driver.value = minValue#Set to min
		f_minDist = abs(matchValue-mPlug_driven.value)#get Dif
		f_minSetValue = mPlug_driven.value
		mPlug_driver.value = maxValue#Set to max
		f_maxDist = abs(matchValue-mPlug_driven.value)#Get dif
		f_maxSetValue = mPlug_driven.value

		f_half = ((maxValue-minValue)/2.0) + minValue#get half	

		#First find range
		if not cgmMath.isFloatEquivalent(matchValue,0) and not cgmMath.isFloatEquivalent(minValue,0) and not cgmMath.isFloatEquivalent(f_minSetValue,0):
		    #if none of our values are 0, this is really fast
		    minValue = (minValue * matchValue)/f_minSetValue
		    log.debug("matchValue_iterator>>> Equated: %s"%minValue)		    
		    f_closest = f_minDist
		    mPlug_driver.value = minValue#Set to min		    
		elif b_firstIter:
		    log.debug("matchValue_iterator>>> first iter. Trying matchValue: %s"%minValue)		    		    
		    b_firstIter = False
		    minValue = matchValue
		    f_closest = f_minDist		    
		elif f_minSetValue > matchValue or f_maxSetValue < matchValue:
		    log.debug("matchValue_iterator>>> Finding Range....")		    
		    if matchValue < mPlug_driven.value:
			#Need to shift our range down
			log.debug("matchValue_iterator>>> Down range: minSetValue: %s"%f_minSetValue)
			f_baseValue = f_maxDist		    
			minValue = f_baseValue - f_minDist
			maxValue = f_baseValue + f_minDist
			f_closest = f_minDist			
		    elif matchValue > mPlug_driven.value:
			#Need to shift our range up
			log.debug("matchValue_iterator>>> Up range: maxSetValue: %s"%f_maxSetValue)  
			f_baseValue = f_minDist		    
			minValue = f_baseValue - f_maxDist
			maxValue = f_baseValue + f_maxDist
			f_closest = f_maxDist			
		else:	
		    if f_minDist>f_maxDist:#if min dif greater, use half as new min
			if f_half < minIn:f_half = minIn
			minValue = f_half
			#log.debug("matchValue_iterator>>>Going up")
			f_closest = f_minDist
		    else:
			if f_half > maxIn:f_half = maxIn			
			maxValue = f_half
			#log.debug("matchValue_iterator>>>Going down")  
			f_closest = f_maxDist"""

                log.debug("matchValue_iterator>>>f1: %s | f2: %s | f_half: %s"%(f_minDist,f_maxDist,f_half))  
                log.debug("#"+'-'*50)

                if f_closest == f_lastClosest:
                    cnt_sameValue +=1
                    if cnt_sameValue >3:
                        log.error("matchValue_iterator>>> Value unchanged. Bad Driver. lastValue: %s | currentValue: %s"%(f_lastValue,mPlug_driven.value))		
                        break
                else:
                    cnt_sameValue = 0 
                f_lastClosest = f_closest
            else:
                log.warning("matchValue_iterator>>> driven mode not implemented with value mode: %s"%__drivenMode__)
                break		

        #>>>>>matchObjMode
        elif __matchMode__ == 'matchObj':
            pos_match = mc.xform(mi_matchObj.mNode, q=True, ws=True, rp=True)
            pos_driven = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            log.debug("matchValue_iterator>>> min: %s | max: %s | pos_match: %s | pos_driven: %s"%(minValue,maxValue,pos_match,pos_driven))  						    
            if cgmMath.isVectorEquivalent(pos_match,pos_driven,2):
                log.debug("matchValue_iterator>>> Match found: %s <<pos>> %s | %s: %s | step: %s"%(mi_matchObj.getShortName(),mi_drivenObj.getShortName(),mPlug_driver.p_combinedShortName,minValue,i))  			    
                b_matchFound = mPlug_driver.value
                break

            mPlug_driver.value = minValue#Set to min
            pos_min = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            #f_minDist = cgmMath.mag( cgmMath.list_subtract(pos_match,pos_min))#get Dif
            f_minDist = distance.returnDistanceBetweenObjects(mi_drivenObj.mNode,mi_matchObj.mNode)

            mPlug_driver.value = maxValue#Set to max
            pos_max = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            f_maxDist = distance.returnDistanceBetweenObjects(mi_drivenObj.mNode,mi_matchObj.mNode)
            f_half = ((maxValue-minValue)/2.0) + minValue#get half	

            if f_minDist>f_maxDist:#if min dif greater, use half as new min
                minValue = f_half
                f_closest = f_minDist
            else:
                maxValue = f_half
                f_closest = f_maxDist	

            if f_minDist==f_maxDist:
                minValue = minValue + .1

            if f_closest == f_lastClosest:
                cnt_sameValue +=1
                if cnt_sameValue >3:
                    log.error("matchValue_iterator>>> Value unchanged. Bad Driver. lastValue: %s | currentValue: %s"%(f_lastValue,mPlug_driver.value))		
                    break
            else:
                cnt_sameValue = 0 
            f_lastClosest = f_closest

            log.debug("matchValue_iterator>>>f1: %s | f2: %s | f_half: %s"%(f_minDist,f_maxDist,f_half))  
            log.debug("#"+'-'*50)	    

        else:
            log.warning("matchValue_iterator>>> matchMode not implemented: %s"%__matchMode__)
            break

    #>>> Check autokey back on
    if b_autoFrameState:
        mc.autoKeyframe(state = True) 

    if b_matchFound is not None:
        return b_matchFound
    #log.warning("matchValue_iterator>>> Failed to find value for: %s"%mPlug_driven.p_combinedShortName)    
    return False

#@cgmGeneral.Timer
def IKHandle_addSplineIKTwist(ikHandle,advancedTwistSetup = False):
    """
    ikHandle(arg)
    advancedTwistSetup(bool) -- Whether to setup ramp setup or not (False)
    """
    #>>> Data gather and arg check
    mi_ikHandle = cgmMeta.validateObjArg(ikHandle,cgmMeta.cgmObject,noneValid=False)
    if mi_ikHandle.getMayaType() != 'ikHandle':
        raise StandardError,"IKHandle_fixTwist>>> '%s' object not 'ikHandle'. Found type: %s"%(mi_ikHandle.getShortName(),mi_ikHandle.getMayaType())

    mi_crv = cgmMeta.validateObjArg(attributes.returnDriverObject("%s.inCurve"%mi_ikHandle.mNode),cgmMeta.cgmObject,noneValid=False)
    log.debug(mi_crv.mNode)

    mPlug_start = cgmMeta.cgmAttr(mi_crv.mNode,'twistStart',attrType='float',keyable=True, hidden=False)
    mPlug_end = cgmMeta.cgmAttr(mi_crv.mNode,'twistEnd',attrType='float',keyable=True, hidden=False)
    #mPlug_equalizedRoll = cgmMeta.cgmAttr(mi_ikHandle.mNode,'result_twistEqualized',attrType='float',keyable=True, hidden=False)
    d_return = {"mi_plug_start":mPlug_start,"mi_plug_end":mPlug_end}    
    if not advancedTwistSetup:
        mPlug_twist = cgmMeta.cgmAttr(mi_ikHandle.mNode,'twist',attrType='float',keyable=True, hidden=False)	
    else:
        mi_ikHandle.dTwistControlEnable = True
        mi_ikHandle.dTwistValueType = 2
        mi_ikHandle.dWorldUpType = 7
        mPlug_twist = cgmMeta.cgmAttr(mi_ikHandle,'dTwistRampMult')
        mi_ramp = cgmMeta.cgmNode(nodeType= 'ramp')
        mi_ramp.doStore('cgmName',mi_ikHandle)
        mi_ramp.doName()

        #Fix Ramp
        attributes.doConnectAttr("%s.outColor"%mi_ramp.mNode,"%s.dTwistRamp"%mi_ikHandle.mNode)
        d_return['mi_ramp'] = mi_ramp

    mPlug_start.doConnectOut("%s.roll"%mi_ikHandle.mNode)
    d_return['mi_plug_twist']=mPlug_twist
    #ikHandle1.twist = (ikHandle1.roll *-.77) + curve4.twistEnd # to implement
    arg1 = "%s = %s - %s"%(mPlug_twist.p_combinedShortName,mPlug_end.p_combinedShortName,mPlug_start.p_combinedShortName)
    log.debug("arg1: '%s'"%arg1)    
    log.debug( NodeF.argsToNodes(arg1).doBuild() )       

    if advancedTwistSetup:
        mc.select(mi_ramp.mNode)
        log.debug( mc.attributeInfo("%s.colorEntryList"%mi_ramp.mNode) )
        for c in mc.ls("%s.colorEntryList[*]"%mi_ramp.mNode,flatten = True):
            log.debug(c)
            log.debug( mc.removeMultiInstance( c, b = True) )
        mc.setAttr("%s.colorEntryList[0].color"%mi_ramp.mNode,0, 0, 0)
        mc.setAttr("%s.colorEntryList[1].color"%mi_ramp.mNode,1, 1, 1)
        mc.setAttr("%s.colorEntryList[1].position"%mi_ramp.mNode,1)

        mPlug_existingTwistType = cgmMeta.cgmAttr(mi_ramp,'interpolation')
        mPlug_twistType = cgmMeta.cgmAttr(mi_crv,'twistType', attrType = 'enum', enum = ":".join(mPlug_existingTwistType.p_enum))
        mPlug_twistType.doConnectOut(mPlug_existingTwistType.p_combinedShortName)	
    else:
        mPlug_existingTwistType = cgmMeta.cgmAttr(mi_ikHandle,'twistType')
        mPlug_twistType = cgmMeta.cgmAttr(mi_crv,'twistType', attrType = 'enum', enum = ":".join(mPlug_existingTwistType.p_enum))
        mPlug_twistType.twistType = 'linear'	
        mPlug_twistType.doConnectOut(mPlug_existingTwistType.p_combinedShortName)	
    return d_return

#@cgmGeneral.Timer
def IKHandle_fixTwist(ikHandle):
    #>>> Data gather and arg check    
    mi_ikHandle = cgmMeta.validateObjArg(ikHandle,cgmMeta.cgmObject,noneValid=False)
    if mi_ikHandle.getMayaType() != 'ikHandle':
        raise StandardError,"IKHandle_fixTwist>>> '%s' object not 'ikHandle'. Found tpe: %s"%(mi_ikHandle.getShortName(),mi_ikHandle.getMayaType())

    startJoint = mi_ikHandle.getMessage('startJoint')
    if not startJoint:
        raise StandardError,"IKHandle_fixTwist>>> '%s' ikHandle missing start joint: %s"%(mi_ikHandle.getShortName())
    mi_startJoint = cgmMeta.validateObjArg(startJoint[0],cgmMeta.cgmObject,noneValid=False)

    #Find the aim axis
    v_localAim = distance.returnLocalAimDirection(mi_startJoint.mNode,mi_startJoint.getChildren()[0])
    str_localAim = dictionary.returnVectorToString(v_localAim)
    str_localAimSingle = str_localAim[0]
    log.debug("IKHandle_fixTwist>>> vector aim: %s | str aim: %s"%(v_localAim,str_localAim))  

    #Check rotation:
    rotAttr = cgmMeta.cgmAttr(mi_startJoint,'r%s'%str_localAimSingle)
    #rotValue = mi_startJoint.getAttr('r%s'%str_localAimSingle)
    #First we try our rotate value
    if not cgmMath.isFloatEquivalent(rotAttr.value,0,2):
        mi_ikHandle.twist = 0
    if not cgmMath.isFloatEquivalent(rotAttr.value,0,2):
        mi_ikHandle.twist = -rotAttr.value#try inversed driven joint rotate value first

    if not cgmMath.isFloatEquivalent(rotAttr.value,0,2):#if we have a value, we need to fix it
        matchValue_iterator(drivenAttr="%s.r%s"%(mi_startJoint.mNode,str_localAimSingle),
                            driverAttr="%s.twist"%mi_ikHandle.mNode,
                            minIn = -170, maxIn = 180,
                            maxIterations = 30,
                            matchValue=0)
        log.debug("rUtils.matchValue_iterator(drivenAttr='%s.r%s',driverAttr='%s.twist',minIn = -180, maxIn = 180, maxIterations = 75,matchValue=0.0001)"%(mi_startJoint.getShortName(),str_localAimSingle,mi_ikHandle.getShortName()))
    return True


def IKHandle_create(startJoint,endJoint,solverType = 'ikRPsolver',rpHandle = False, lockMid = True, addLengthMulti = False,
                    stretch = False, globalScaleAttr = None, controlObject = None, baseName = 'ikChain', nameSuffix = None,
                    handles = [],#If one given, assumed to be mid, can't have more than length of joints
                    moduleInstance = None):
    """
    @kws
    l_jointChain1(list) -- blend list 1
    l_jointChain2(list) -- blend list 2
    l_blendChain(list) -- result chain
    solverType -- 'ikRPsolver','ikSCsolver'
    baseName -- 
    nameSuffix -- add to nameBase
    rpHandle(bool/string) -- whether to have rphandle setup, object to use if string or MetaClass
    lockMid(bool) --
    driver(attr arg) -- driver attr
    globalScaleAttr(string/cgmAttr) -- global scale attr to connect in
    addLengthMulti(bool) -- whether to setup lengthMultipliers
    controlObject(None/string) -- whether to have control to put attrs on, object to use if string or MetaClass OR will use ikHandle
    channels(list) -- channels to blend
    stretch(bool/string) -- stretch options - translate/scale
    moduleInstance -- instance to connect stuff to

    """
    ml_rigObjectsToConnect = []
    ml_rigObjectsToParent = []

    #>>> Data gather and arg check
    if solverType not in ['ikRPsolver','ikSCsolver']:
        raise StandardError,"create_IKHandle>>> solver type no good: %s"%solverType
    #Joint chain
    mi_start = cgmMeta.validateObjArg(startJoint,cgmMeta.cgmObject,noneValid=False)
    mi_end = cgmMeta.validateObjArg(endJoint,cgmMeta.cgmObject,noneValid=False)
    if not mi_end.isChildOf(mi_start):
        raise StandardError,"create_IKHandle>>> %s not a parent of %s"%(mi_start.getShortName(),mi_end.getShortName())	
    l_jointChain = mi_start.getListPathTo(mi_end)
    ml_jointChain = cgmMeta.validateObjListArg(l_jointChain,cgmMeta.cgmObject,noneValid=False)
    if len(l_jointChain)>3:
        raise StandardError,"create_IKHandle>>> Haven't tested for more than a three joint chain. Len: %s"%(len(l_jointChain))	
    log.debug("create_IKHandle>>> chain: %s"%l_jointChain)

    _foundPrerred = False
    for i_jnt in ml_jointChain:
        for attr in ['preferredAngleX','preferredAngleY','preferredAngleZ']:
            if i_jnt.getAttr(attr):
                _foundPrerred = True
                break

    #Master global control
    d_MasterGlobalScale = cgmMeta.validateAttrArg(globalScaleAttr,noneValid=True)

    #Stretch
    if stretch and stretch not in ['translate','scale']:
        log.debug("create_IKHandle>>> Invalid stretch arg: %s. Using default: 'translate'."%(stretch))
        stretch = 'translate'
    if stretch == 'scale':
        raise NotImplementedError,"create_IKHandle>>> scale method not implmented %s"

    #Handles
    ml_handles = cgmMeta.validateObjListArg(handles,cgmMeta.cgmObject,noneValid=True)
    if len(ml_handles)>len(l_jointChain):#Check handle length to joint list
        raise StandardError,"create_IKHandle>>> More handles than joins: joints:%s | handles:%s"%(len(l_jointChain),len(ml_handles))	

    mi_rpHandle = cgmMeta.validateObjArg(rpHandle,cgmMeta.cgmObject,noneValid=True)
    if mi_rpHandle and mi_rpHandle in ml_handles:
        raise StandardError,"create_IKHandle>>> rpHandle can't be a measure handle to: '%s'"%(mi_rpHandle.getShortName())		

    #Control object
    mi_control = cgmMeta.validateObjArg(controlObject,cgmMeta.cgmObject,noneValid=True)
    if mi_control:log.debug("create_IKHandle>>> mi_control from arg: %s"%mi_control.getShortName())

    #Figure out our aimaxis
    v_localAim = distance.returnLocalAimDirection(ml_jointChain[0].mNode,ml_jointChain[1].mNode)
    str_localAim = dictionary.returnVectorToString(v_localAim)
    str_localAimSingle = str_localAim[0]
    log.debug("create_IKHandle>>> vector aim: %s | str aim: %s"%(v_localAim,str_localAim))

    i_module = False
    i_rigNull = False
    try:#Module instance
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance
                i_rigNull = i_module.rigNull
                baseName = i_module.getPartNameBase()
                if nameSuffix is not None:
                    baseName = "%s_%s"%(baseName,nameSuffix)
                log.debug('baseName set to module: %s'%baseName)	    
    except:
        log.error("Not a module instance, ignoring: '%s'"%moduleInstance)    

    if not i_module:
        if nameSuffix is not None:
            baseName = "%s_%s"%(baseName,nameSuffix)	
    #=============================================================================
    #Create IK handle
    try:
        buffer = mc.ikHandle( sj=mi_start.mNode, ee=mi_end.mNode,
                              solver = solverType, forceSolver = True,
                              snapHandleFlagToggle=True )  	
    except:
        raise StandardError,"create_IKHandle>>> solver type is probably no good: %s"%solverType

    #>>> Name
    log.debug(buffer)
    i_ik_handle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
    i_ik_handle.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_ik_handle.doName()

    ml_rigObjectsToConnect.append(i_ik_handle)

    i_ik_effector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
    i_ik_effector.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_ik_effector.doName()

    #>>> Control
    if not mi_control:
        mi_control = i_ik_handle

    #>>> Store our start and end
    #i_ik_handle.connectChildNode(mi_start,'jointStart','ikOwner')
    #i_ik_handle.connectChildNode(mi_end,'jointEnd','ikOwner')

    #=============================================================================

    #>>>Stetch
    #===============================================================================
    """
    1)Build overall stretch setup
    2)Build per segment stretch setup
    3)connect by 'translate' or 'scale'
    """
    mPlug_lockMid = False  
    ml_distanceShapes = []
    ml_distanceObjects = []   

    if stretch:
        if lockMid:mPlug_lockMid = cgmMeta.cgmAttr(mi_control,'lockMid',initialValue = 0, attrType = 'float', keyable = True, minValue = 0, maxValue = 1)

        mPlug_autoStretch = cgmMeta.cgmAttr(mi_control,'autoStretch',initialValue = 1, defaultValue = 1, keyable = True, attrType = 'float', minValue = 0, maxValue = 1)
        if addLengthMulti:
            mPlug_lengthUpr= cgmMeta.cgmAttr(mi_control,'lengthUpr',attrType='float',value = 1, defaultValue = 1,minValue=0,keyable = True)
            mPlug_lengthLwr = cgmMeta.cgmAttr(mi_control,'lengthLwr',attrType='float',value = 1, defaultValue = 1,minValue=0,keyable = True)	
            ml_multiPlugs = [mPlug_lengthUpr,mPlug_lengthLwr]

        log.debug("create_IKHandle>>> stretch mode!")

        #Check our handles for stretching
        if len(ml_handles)!= len(ml_jointChain):#we need a handle per joint for measuring purposes
            log.debug("create_IKHandle>>> Making handles")
            ml_buffer = ml_handles
            ml_handles = []
            for j in ml_jointChain:
                m_match = False
                for h in ml_buffer:
                    if cgmMath.isVectorEquivalent(j.getPosition(),h.getPosition()):
                        log.debug("create_IKHandle>>> '%s' handle matches: '%s'"%(h.getShortName(),j.getShortName()))
                        m_match = h
                if not m_match:#make one
                    m_match = j.doLoc(nameLink = True)
                    m_match.addAttr('cgmTypeModifier','stretchMeasure')
                    m_match.doName()
                ml_handles.append(m_match)
                ml_rigObjectsToConnect.append(m_match)

            #>>>TODO Add hide stuff

        #>>>Do Handles
        mi_midHandle = False   
        if ml_handles:
            if len(ml_handles) == 1:
                mi_midHandle = ml_handles[0]
            else:
                mid = int((len(ml_handles))/2)
                mi_midHandle = ml_handles[mid]
            log.debug("create_IKHandle>>> mid handle: %s"%mi_midHandle.getShortName())

        log.debug("create_IKHandle>>> handles: %s"%[o.getShortName() for o in ml_handles])

        #Overall stretch
        mPlug_globalScale = cgmMeta.cgmAttr(i_ik_handle.mNode,'masterScale',value = 1.0, lock =True, hidden = True)

        """
	mi_baseLenCurve = cgmMeta.cgmObject( mc.curve (d=1, ep = [ml_jointChain[0].getPosition(),ml_jointChain[-1].getPosition()], os=True))
	mi_baseLenCurve.addAttr('cgmName',baseName)
	mi_baseLenCurve.addAttr('cgmTypeModifier','baseMeasure')
	mi_baseLenCurve.doName()
        mi_baseArcLen = cgmMeta.cgmNode( distance.createCurveLengthNode(mi_baseLenCurve.mNode) )
	log.debug("create_IKHandle>>> '%s' length : %s"%(mi_baseArcLen.getShortName(),mi_baseArcLen.arcLength))
	"""
        md_baseDistReturn = create_distanceMeasure(ml_handles[0].mNode,ml_handles[-1].mNode)
        ml_rigObjectsToParent.append(md_baseDistReturn['mi_object'])
        mPlug_baseDist = cgmMeta.cgmAttr(i_ik_handle.mNode,'ikDistBase' , attrType = 'float', value = md_baseDistReturn['mi_shape'].distance , lock =True , hidden = True)	
        mPlug_baseDistRaw = cgmMeta.cgmAttr(i_ik_handle.mNode,'ikDistRaw' , value = 1.0 , lock =True , hidden = True)
        mPlug_baseDistRaw.doConnectIn("%s.distance"%md_baseDistReturn['mi_shape'].mNode)
        mPlug_baseDistNormal = cgmMeta.cgmAttr(i_ik_handle.mNode,'result_ikBaseNormal',value = 1.0, lock =True, hidden = True)
        mPlug_ikDistNormal = cgmMeta.cgmAttr(i_ik_handle.mNode,'result_ikDistNormal',value = 1.0, lock =True, hidden = True)	
        mPlug_ikScale = cgmMeta.cgmAttr(i_ik_handle.mNode,'result_ikScale',value = 1.0, lock =True, hidden = True)
        mPlug_ikClampScale = cgmMeta.cgmAttr(i_ik_handle.mNode,'result_ikClampScale',value = 1.0, lock =True, hidden = True)
        mPlug_ikClampMax = cgmMeta.cgmAttr(i_ik_handle.mNode,'result_ikClampMax',value = 1.0, lock =True, hidden = True)

        #Normal base
        arg = "%s = %s * %s"%(mPlug_baseDistNormal.p_combinedShortName,
                              mPlug_baseDist.p_combinedShortName,
                              mPlug_globalScale.p_combinedShortName)
        NodeF.argsToNodes(arg).doBuild()

        #Normal Length
        arg = "%s = %s / %s"%(mPlug_ikDistNormal.p_combinedShortName,
                              mPlug_baseDistRaw.p_combinedShortName,
                              mPlug_globalScale.p_combinedShortName)
        NodeF.argsToNodes(arg).doBuild()	

        #ik scale
        arg = "%s = %s / %s"%(mPlug_ikScale.p_combinedShortName,
                              mPlug_baseDistRaw.p_combinedShortName,
                              mPlug_baseDistNormal.p_combinedShortName)
        NodeF.argsToNodes(arg).doBuild()	

        #ik max clamp
        """ This is for maya 2013 (at least) which honors the max over the  min """
        arg = "%s = if %s >= 1: %s else 1"%(mPlug_ikClampMax.p_combinedShortName,
                                            mPlug_ikScale.p_combinedShortName,
                                            mPlug_ikScale.p_combinedShortName)
        NodeF.argsToNodes(arg).doBuild()

        #ik clamp scale
        arg = "%s = clamp(1,%s,%s)"%(mPlug_ikClampScale.p_combinedShortName,
                                     mPlug_ikClampMax.p_combinedShortName,
                                     mPlug_ikScale.p_combinedShortName)
        NodeF.argsToNodes(arg).doBuild()	

        #Create our blend to stretch or not - blend normal base and stretch base
        mi_stretchBlend = cgmMeta.cgmNode(nodeType= 'blendTwoAttr')
        mi_stretchBlend.addAttr('cgmName','%s_stretchBlend'%(baseName),lock=True)
        mi_stretchBlend.doName()
        attributes.doSetAttr(mi_stretchBlend.mNode,"input[0]",1)
        mPlug_ikClampScale.doConnectOut("%s.input[1]"%mi_stretchBlend.mNode)
        mPlug_autoStretch.doConnectOut("%s.attributesBlender"%mi_stretchBlend.mNode)


        #Make our distance objects per segment
        #=========================================================================
        l_segments = lists.parseListToPairs(ml_handles)
        for i,seg in enumerate(l_segments):#Make our measure nodes
            buffer =  create_distanceMeasure(seg[0].mNode,seg[-1].mNode)
            ml_distanceShapes.append(buffer['mi_shape'])
            ml_distanceObjects.append(buffer['mi_object'])
            #>>>TODO Add hide stuff
        ml_rigObjectsToParent.extend(ml_distanceObjects)
        ml_rigObjectsToConnect.extend(ml_handles)

        for i,i_jnt in enumerate(ml_jointChain[:-1]):
            #Make some attrs
            mPlug_baseDist= cgmMeta.cgmAttr(i_ik_handle.mNode,"baseDist_%s"%i,attrType = 'float' , value = ml_distanceShapes[i].distance , lock=True,minValue = 0)
            mPlug_rawDist = cgmMeta.cgmAttr(i_ik_handle.mNode,"baseRaw_%s"%i,attrType = 'float', initialValue=0 , lock=True , minValue = 0)				  	    
            mPlug_normalBaseDist = cgmMeta.cgmAttr(i_ik_handle.mNode,"baseNormal_%s"%i,attrType = 'float', initialValue=0 , lock=True , minValue = 0)			
            mPlug_normalDist = cgmMeta.cgmAttr(i_ik_handle.mNode,"distNormal_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)		
            mPlug_stretchDist = cgmMeta.cgmAttr(i_ik_handle.mNode,"result_stretchDist_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)			    
            mPlug_stretchNormalDist = cgmMeta.cgmAttr(i_ik_handle.mNode,"result_stretchNormalDist_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)			    	    
            mPlug_resultSegmentScale = cgmMeta.cgmAttr(i_ik_handle.mNode,"segmentScale_%s"%i,attrType = 'float',initialValue=0,lock=True,minValue = 0)	

            #Raw distance in
            mPlug_rawDist.doConnectIn("%s.distance"%ml_distanceShapes[i].mNode)	  

            #Normal base distance
            arg = "%s = %s * %s"%(mPlug_normalBaseDist.p_combinedShortName,
                                  mPlug_baseDist.p_combinedName,
                                  mPlug_globalScale.p_combinedShortName)
            NodeF.argsToNodes(arg).doBuild()

            #Normal distance
            arg = "%s = %s / %s"%(mPlug_normalDist.p_combinedShortName,
                                  mPlug_rawDist.p_combinedName,
                                  mPlug_globalScale.p_combinedShortName)
            NodeF.argsToNodes(arg).doBuild()

            #Stretch Distance
            arg = "%s = %s * %s.output"%(mPlug_stretchDist.p_combinedShortName,
                                         mPlug_normalBaseDist.p_combinedName,
                                         mi_stretchBlend.getShortName())
            NodeF.argsToNodes(arg).doBuild()

            #Then pull the global out of the stretchdistance 
            arg = "%s = %s / %s"%(mPlug_stretchNormalDist.p_combinedShortName,
                                  mPlug_stretchDist.p_combinedName,
                                  mPlug_globalScale.p_combinedName)
            NodeF.argsToNodes(arg).doBuild()	    

            #Segment scale
            arg = "%s = %s / %s"%(mPlug_resultSegmentScale.p_combinedShortName,
                                  mPlug_normalDist.p_combinedName,
                                  mPlug_baseDist.p_combinedShortName)
            NodeF.argsToNodes(arg).doBuild()

            #Create our blend to stretch or not - blend normal base and stretch base
            mi_blend = cgmMeta.cgmNode(nodeType= 'blendTwoAttr')
            mi_blend.addAttr('cgmName','%s_stretch_to_lockMid'%(i_jnt.getBaseName()),lock=True)
            mi_blend.doName()
            if lockMid:
                mPlug_lockMid.doConnectOut("%s.attributesBlender"%mi_blend.mNode)

            if stretch == 'translate':
                #Base Normal, Dist Normal
                mPlug_stretchNormalDist.doConnectOut("%s.input[0]"%mi_blend.mNode)
                mPlug_normalDist.doConnectOut("%s.input[1]"%mi_blend.mNode)
                attributes.doConnectAttr("%s.output"%mi_blend.mNode,"%s.t%s"%(ml_jointChain[i+1].mNode,str_localAimSingle))

    #>>> addLengthMulti
    if addLengthMulti:
        log.debug("create_IKHandle>>> addLengthMulti!")		
        if len(ml_jointChain[:-1]) == 2:
            #grab the plug

            i_mdLengthMulti = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
            i_mdLengthMulti.operation = 1
            i_mdLengthMulti.doStore('cgmName',baseName)
            i_mdLengthMulti.addAttr('cgmTypeModifier','lengthMulti')
            i_mdLengthMulti.doName()

            l_mdAxis = ['X','Y','Z']
            for i,i_jnt in enumerate(ml_jointChain[:-1]):
                #grab the plug
                mPlug_driven = cgmMeta.cgmAttr(ml_jointChain[i+1],'t%s'%str_localAimSingle)
                plug = attributes.doBreakConnection(mPlug_driven.p_combinedName)
                if not plug:raise StandardError,"create_IKHandle>>> Should have found a plug on: %s.t%s"%(ml_jointChain[i+1].mNode,str_localAimSingle)

                attributes.doConnectAttr(plug,#>>
                                         '%s.input1%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect the old plug data
                ml_multiPlugs[i].doConnectOut('%s.input2%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect in the mutliDriver	
                mPlug_driven.doConnectIn('%s.output.output%s'%(i_mdLengthMulti.mNode,l_mdAxis[i]))#Connect it back to our driven

        else:
            log.error("create_IKHandle>>> addLengthMulti only currently supports 2 segments. Found: %s"%len(ml_jointChain[:-1]) )

    #>>> rpSetup
    if solverType == 'ikRPsolver' and rpHandle:
        if not mi_rpHandle:
            #Make one
            mi_rpHandle = mi_midHandle.doLoc()
            mi_rpHandle.addAttr('cgmTypeModifier','poleVector')
            mi_rpHandle.doName()
            ml_rigObjectsToConnect.append(mi_rpHandle)
        log.debug("create_IKHandle>>> rp setup mode!")
        cBuffer = mc.poleVectorConstraint(mi_rpHandle.mNode,i_ik_handle.mNode)

        #Fix rp
        #rotValue = mi_start.getAttr('r%s'%str_localAimSingle)    
        #if not cgmMath.isFloatEquivalent(rotValue,0):#if we have a value, we need to fix it
            #IKHandle_fixTwist(i_ik_handle)	


    #>>> Plug in global scale
    if d_MasterGlobalScale:
        d_MasterGlobalScale['mi_plug'].doConnectOut(mPlug_globalScale.p_combinedName)

    #>>> Connect our iModule vis stuff
    if i_module:#if we have a module, connect vis
        for i_obj in ml_rigObjectsToConnect:
            i_obj.overrideEnabled = 1		
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideDisplayType'))    
        for i_obj in ml_rigObjectsToParent:
            i_obj.parent = i_module.rigNull.mNode

    #>>> Return dict
    d_return = {'mi_handle':i_ik_handle,'mi_effector':i_ik_effector}
    if lockMid:
        d_return['mPlug_lockMid'] = mPlug_lockMid	
        d_return['ml_measureObjects']=ml_distanceObjects	
    if stretch:
        d_return['mPlug_autoStretch'] = mPlug_autoStretch
        d_return['ml_distHandles']=ml_handles
    if mi_rpHandle:
        d_return['mi_rpHandle'] = mi_rpHandle
    if addLengthMulti:
        d_return['ml_lengthMultiPlugs'] = ml_multiPlugs

    if not _foundPrerred:log.warning("create_IKHandle>>> No preferred angle values found. The chain probably won't work as expected: %s"%l_jointChain)

    return d_return   

def connectBlendChainByConstraint(l_jointChain1,l_jointChain2,l_blendChain, driver = None, l_constraints = ['point','orient']):
    """
    @kws
    l_jointChain1(list) -- blend list 1
    l_jointChain2(list) -- blend list 2
    l_blendChain(list) -- result chain

    driver(attr arg) -- driver attr
    channels(list) -- channels to blend

    """
    _str_funcName = 'connectBlendChainByConstraint'
    try:
        try:
            d_funcs = {'point':mc.pointConstraint,
                       'orient':mc.orientConstraint,
                       'scale':mc.scaleConstraint,
                       'parent':mc.scaleConstraint}
            for c in l_constraints:
                if c not in ['point','orient','scale','parent']:
                    log.warning("Bad constraint arg: %s. Removing!"%c)
                    l_constraints.remove(c)
            if not l_constraints:
                raise StandardError,"Need valid constraints: %s"%l_constraints
    
            ml_jointChain1 = cgmMeta.validateObjListArg(l_jointChain1,cgmMeta.cgmObject,noneValid=False)
            ml_jointChain2 = cgmMeta.validateObjListArg(l_jointChain2,cgmMeta.cgmObject,noneValid=False)
            ml_blendChain = cgmMeta.validateObjListArg(l_blendChain,cgmMeta.cgmObject,noneValid=False)
            d_driver = cgmMeta.validateAttrArg(driver,noneValid=True)
            mi_driver = False
            if d_driver:mi_driver = d_driver.get('mi_plug') or False
    
            if not len(ml_jointChain1) >= len(ml_blendChain) or not len(ml_jointChain2) >= len(ml_blendChain):
                raise StandardError,"Joint chains aren't equal lengths: l_jointChain1: %s | l_jointChain2: %s | l_blendChain: %s"%(len(l_jointChain1),len(l_jointChain2),len(l_blendChain))
            """
            for i,i_jnt in enumerate(ml_blendChain):
                if not cgmMath.isVectorEquivalent( i_jnt.getPosition(),ml_jointChain1[i].getPosition() ):
                    raise StandardError,"connectBlendChainByConstraint>>> joints not equivalent: %s |%s"%(i_jnt.getShortName(),ml_jointChain1[i].getShortName())
                if not cgmMath.isVectorEquivalent( i_jnt.getPosition(),ml_jointChain2[i].getPosition() ):
                    raise StandardError,"connectBlendChainByConstraint>>> joints not equivalent: %s |%s"%(i_jnt.getShortName(),ml_jointChain1[i].getShortName())
            """
            ml_nodes = []
        except Exception,error:
            raise Exception,"Initalization fail | error {0}".format(error)
        
        #>>> Actual meat
        #===========================================================
        for i,i_jnt in enumerate(ml_blendChain):
            for constraint in l_constraints:
                log.debug("connectBlendChainByConstraint>>> %s || %s = %s | %s"%(ml_jointChain1[i].getShortName(),
                                                                                 ml_jointChain2[i].getShortName(),
                                                                                 ml_blendChain[i].getShortName(),
                                                                                 constraint))	    
                i_c = cgmMeta.cgmNode( d_funcs[constraint]([ml_jointChain2[i].getShortName(),ml_jointChain1[i].getShortName()],
                                                           ml_blendChain[i].getShortName(),maintainOffset = False)[0])


                targetWeights = d_funcs[constraint](i_c.mNode,q=True, weightAliasList=True)
                if len(targetWeights)>2:
                    raise StandardError,"Too many weight targets: obj: %s | weights: %s"%(i_obj.mNode,targetWeights)

                if mi_driver:
                    d_blendReturn = NodeF.createSingleBlendNetwork(mi_driver,
                                                                   [i_c.mNode,'result_%s_%s'%(constraint,ml_jointChain1[i].getBaseName())],
                                                                   [i_c.mNode,'result_%s_%s'%(constraint,ml_jointChain2[i].getBaseName())],
                                                                   keyable=True)

                    #Connect                                  
                    d_blendReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (i_c.mNode,targetWeights[0]))
                    d_blendReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (i_c.mNode,targetWeights[1]))

                ml_nodes.append(i_c)

        d_blendReturn['ml_nodes'] = ml_nodes

        return d_blendReturn
    except Exception,error:
        for k in [l_jointChain1,l_jointChain2,l_blendChain, driver,l_constraints]:
            log.error("{0} | {1} ".format(_str_funcName,k))
        raise Exception,"%s >>  error: %s"%(_str_funcName,error) 

def connect_singleDriverAttrToMulti(drivenAttr = None, driverAttrs = None):
    """
    Function to drive a single attribute with many drivers.
    If one driver, it uses a direct connect. If multiple, it creates an average node.

    :parameters:
    0 - 'drivenAttr'(attr - None) | attr to be driven
    1 - 'driverAttrs'(attrs - None) | attrs that drive.

    :returns:
    (bool) | success

    :raises:
    Exception | if reached

    """
    _str_funcName = 'connect_singleDriverAttrToMulti' 
    _str_reportStart = "{0} >> ".format(_str_funcName) 

    try:#>>> Data gather and arg check     
        d_ret = cgmMeta.validateAttrArg(drivenAttr,noneValid=True)
        if not d_ret:
            raise ValueError,"Bad drivenAttr| {0}".format(drivenAttr)	
        mPlug_driven = d_ret['mi_plug']
        log.info("{0} driven: '{1}'".format(_str_reportStart,mPlug_driven.p_combinedShortName))

        d_ret = cgmMeta.validateAttrListArg(driverAttrs,noneValid=True)
        if not d_ret:
            raise ValueError,"Bad drivers| {0}".format(drivenAttr)	
        mlPlugs_drivers = d_ret['ml_plugs']

        for i,mPlug in enumerate(mlPlugs_drivers):
            log.info("{0} driver {1}: '{2}'".format(_str_reportStart,i,mPlug.p_combinedShortName))
    except Exception,error:raise Exception,"[{0}>> Validate |  error: {1}]".format(_str_funcName,error) 

    try:#>>> Connect   
        _int_lenDrivers = len(mlPlugs_drivers)
        if _int_lenDrivers == 1:
            log.info("{0} mode: Single driver".format(_str_reportStart))
            mPlug_driven.doConnectIn(mlPlugs_drivers[0])
        else:
            str_arg = "{0} = {1}".format(mPlug_driven.p_combinedShortName," >< ".join(mPlug.p_combinedShortName for mPlug in mlPlugs_drivers))
            log.info("{0} mode: Blend mode".format(_str_reportStart))
            log.info("{0} arg to build : '{1}'".format(_str_reportStart,str_arg))
            NodeF.argsToNodes(str_arg).doBuild()

        return True
    except Exception,error:raise Exception,"[{0}>> Connect |  error: {1}]".format(_str_funcName,error) 

def connectBlendJointChain(l_jointChain1,l_jointChain2,l_blendChain, driver = None, channels = ['translate','rotate']):
    """
    @kws
    l_jointChain1(list) -- blend list 1
    l_jointChain2(list) -- blend list 2
    l_blendChain(list) -- result chain

    driver(attr arg) -- driver attr
    channels(list) -- channels to blend

    """
    ml_jointChain1 = cgmMeta.validateObjListArg(l_jointChain1,cgmMeta.cgmObject,noneValid=False)
    ml_jointChain2 = cgmMeta.validateObjListArg(l_jointChain2,cgmMeta.cgmObject,noneValid=False)
    ml_blendChain = cgmMeta.validateObjListArg(l_blendChain,cgmMeta.cgmObject,noneValid=False)
    d_driver = cgmMeta.validateAttrArg(driver,noneValid=True)
    mi_driver = False
    if d_driver:mi_driver = d_driver.get('mi_plug') or False

    if not len(ml_jointChain1) >= len(ml_blendChain) or not len(ml_jointChain2) >= len(ml_blendChain):
        raise StandardError,"connectBlendJointChain>>> Joint chains aren't equal lengths: l_jointChain1: %s | l_jointChain2: %s | l_blendChain: %s"%(len(l_jointChain1),len(l_jointChain2),len(l_blendChain))
    """
    for i,i_jnt in enumerate(ml_blendChain):
	if not cgmMath.isVectorEquivalent( i_jnt.getPosition(),ml_jointChain1[i].getPosition() ):
	    raise StandardError,"connectBlendJointChain>>> joints not equivalent: %s |%s"%(i_jnt.getShortName(),ml_jointChain1[i].getShortName())
	if not cgmMath.isVectorEquivalent( i_jnt.getPosition(),ml_jointChain2[i].getPosition() ):
	    raise StandardError,"connectBlendJointChain>>> joints not equivalent: %s |%s"%(i_jnt.getBaseName(),ml_jointChain1[i].getBaseName())
    """
    l_channels = [c for c in channels if c in ['translate','rotate','scale']]
    if not channels:
        raise StandardError,"connectBlendJointChain>>> Need valid channels: %s"%channels

    ml_nodes = []

    #>>> Actual meat
    #===========================================================
    for i,i_jnt in enumerate(ml_blendChain):
        for channel in l_channels:
            i_node = cgmMeta.cgmNode(nodeType = 'blendColors')
            i_node.addAttr('cgmName',"%s_to_%s"%(ml_jointChain1[i].getBaseName(),ml_jointChain2[i].getBaseName()))
            i_node.addAttr('cgmTypeModifier',channel)
            i_node.doName()
            log.debug("connectBlendJointChain>>> %s || %s = %s | %s"%(ml_jointChain1[i].getBaseName(),
                                                                      ml_jointChain2[i].getBaseName(),
                                                                      ml_blendChain[i].getBaseName(),channel))
            cgmMeta.cgmAttr(i_node,'color2').doConnectIn("%s.%s"%(ml_jointChain1[i].mNode,channel))
            cgmMeta.cgmAttr(i_node,'color1').doConnectIn("%s.%s"%(ml_jointChain2[i].mNode,channel))
            cgmMeta.cgmAttr(i_node,'output').doConnectOut("%s.%s"%(i_jnt.mNode,channel))

            if mi_driver:
                cgmMeta.cgmAttr(i_node,'blender').doConnectIn(mi_driver.p_combinedName)

            ml_nodes.append(i_node)

    return ml_nodes


def addJointLengthAttr(joint,attrArg = None,connectBy = 'translate',orientation = 'zyx'):
    """
    @kws
    joint -- joint to add length to
    attrArg -- the attr to connect this to. If none is provided, it adds to the joint
    connectBy -- mode
    orienation(str) -- joint orientation

    """
    _str_funcName = 'addJointLengthAttr'
    _str_funcDebug = "%s >> ARGS >> joint : %s | attrArg : %s | connectBy : %s | orientation : %s "%(_str_funcName,joint,attrArg,connectBy,orientation)
    t_start = time.clock()        		    

    log.info(">>> %s >> "%_str_funcName + "="*75)  
    try:
        try:#Data
            _str_subFunc = "Arg validation"

            mi_joint = cgmMeta.validateObjArg(joint,cgmMeta.cgmObject)
            d_driver = cgmMeta.validateAttrArg(attrArg,noneValid=True)
            mi_driver = False
            if d_driver:mi_driver = d_driver.get('mi_plug') or False
            log.debug("attrArgDriver: %s"%d_driver)
            if not mi_driver:#If we still don't have one, make one
                mi_driver = cgmMeta.cgmAttr(mi_joint,'length',attrType = 'float')

        except Exception,error:
            raise StandardError,"%s >> FAIL STEP >> %s | %s"%(_str_funcName,_str_subFunc,error)       	

        try:#CHeck the settings
            _str_subFunc = "Check driver settings"		
            mi_driver.p_defaultValue = 1
            mi_driver.p_minValue = 0
            mi_driver.value = 1
            mi_driver.p_hidden = False
            mi_driver.p_keyable = True
        except Exception,error:
            raise StandardError,"%s >> FAIL STEP >> %s | %s"%(_str_funcName,_str_subFunc,error)   

        try:#>>> Actual meat
            #===========================================================
            _str_subFunc = "Setup"

            if connectBy == 'translate':
                #Find the child joint
                cBuffer = mc.listRelatives(mi_joint.mNode,type='joint') or False
                if len(cBuffer) == 2:
                    l_pos = mi_joint.getPosition()
                    for c in cBuffer:
                        if not cgmMath.isVectorEquivalent(l_pos,cgmMeta.cgmObject(c).getPosition()):
                            log.info("%s >> good child: %s"%(_str_funcName,c))
                            cBuffer = [c]

                if len(cBuffer)>1:
                    raise NotImplementedError,"Too many child joints to know which is length: %s"%(len(cBuffer))
                elif not cBuffer:
                    raise NotImplementedError,"No chidren joints found"

                mi_childJoint = cgmMeta.validateObjArg(cBuffer[0],cgmMeta.cgmObject)
                #Get the length
                #length = mi_childJoint.__getattribute__('t%s'%orientation[0].lower())
                length = mc.getAttr("%s.t%s"%(mi_childJoint.mNode,orientation[0].lower()))

                mi_baseAttr = cgmMeta.cgmAttr(mi_childJoint,'baseLength',value=length,lock=True)

                log.info("%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-t_start)) + "-"*75)		

                return NodeF.argsToNodes("%s.t%s = %s * %s"%(mi_childJoint.getShortName(),orientation[0].lower(),
                                                             mi_driver.p_combinedShortName,mi_baseAttr.p_combinedShortName)).doBuild()

            else:
                raise StandardError,"connectBy '%s' not available"%(mi_joint.getShortName(),connectBy)
        except Exception,error:
            raise StandardError,"%s >> FAIL STEP >> %s | %s"%(_str_funcName,_str_subFunc,error)   

    except Exception,error:
        log.error(_str_funcDebug)
        raise error


def createControlSurfaceSegment(jointList,orientation = 'zyx',secondaryAxis = None,
                                baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]

    i_module = False
    i_rigNull = False

    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
                i_rigNull = i_module.rigNull
        else:
            log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    except:pass

    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()

    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)

    i_controlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
    i_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    i_controlSurface.doName()

    if i_module:#if we have a module, connect vis
        i_controlSurface.overrideEnabled = 1		
        cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_controlSurface.mNode,'overrideVisibility'))
        cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_controlSurface.mNode,'overrideDisplayType'))    


    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    if not moduleInstance:#if it is, we can assume it's right
        if secondaryAxis is None:
            raise StandardError,"createControlSurfaceSegment>>> Must have secondaryAxis arg if no moduleInstance is passed"
        for i_jnt in ml_jointList:
            """
	    Cannot iterate how important this step is. Lost a day trying to trouble shoot why one joint chain worked and another didn't.
	    WILL NOT connect right without this.
	    """
            joints.orientJoint(i_jnt.mNode,orientation,secondaryAxis)

    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    ml_upGroups = []

    #First thing we're going to do is create our follicles
    for i,i_jnt in enumerate(ml_jointList):       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(i_jnt.mNode,i_controlSurface.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(i_controlSurface.mNode)
        i_follicleTrans = cgmMeta.asMeta(l_follicleInfo[1],'cgmObject',setClass=True)
        i_follicleShape = cgmMeta.asMeta(l_follicleInfo[0],'cgmNode')
        #> Name
        i_follicleTrans.doStore('cgmName',i_jnt)
        i_follicleTrans.doName()
        #>Set follicle value
        i_follicleShape.parameterU = l_closestInfo['normalizedU']
        i_follicleShape.parameterV = l_closestInfo['normalizedV']

        ml_follicleShapes.append(i_follicleShape)
        ml_follicleTransforms.append(i_follicleTrans)

        i_follicleTrans.parent = i_grp.mNode	

        if i_module:#if we have a module, connect vis
            i_follicleTrans.overrideEnabled = 1		
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_follicleTrans.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_follicleTrans.mNode,'overrideDisplayType'))    


        #>>> loc
        """
	First part of full ribbon wist setup
	"""
        if i_jnt != ml_jointList[-1]:
            i_upLoc = i_jnt.doLoc()#Make up Loc
            i_locRotateGroup = i_jnt.doCreateAt()#group in place
            i_locRotateGroup.parent = i_follicleTrans.mNode
            i_locRotateGroup.doStore('cgmName',i_jnt)	    
            i_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
            i_locRotateGroup.doName()

            #Store the rotate group to the joint
            i_jnt.connectChildNode(i_locRotateGroup,'rotateUpGroup','drivenJoint')
            i_zeroGrp = cgmMeta.asMeta( i_locRotateGroup.doGroup(True),'cgmObject',setClass=True )
            i_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
            i_zeroGrp.doName()
            #connect some other data
            i_locRotateGroup.connectChildNode(i_follicleTrans,'follicle','drivenGroup')
            i_locRotateGroup.connectChildNode(i_locRotateGroup.parent,'zeroGroup')
            i_locRotateGroup.connectChildNode(i_upLoc,'upLoc')

            mc.makeIdentity(i_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)


            i_upLoc.parent = i_locRotateGroup.mNode
            mc.move(0,10,0,i_upLoc.mNode,os=True)	
            ml_upGroups.append(i_upLoc)

            if i_module:#if we have a module, connect vis
                i_upLoc.overrideEnabled = 1		
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideDisplayType'))    


        #>> Surface Anchor ===================================================
    #Orient constrain our last joint to our last follicle
    #>>>DON'T Like this method --- mc.orientConstraint(ml_follicleTransforms[-1].mNode,ml_jointList[-1].mNode,maintainOffset = True)

    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    ml_distanceObjects = []
    ml_distanceShapes = []  
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.cgmObject(ik_buffer[0])
        i_IK_Handle.parent = ml_follicleTransforms[i+1].mNode
        i_IK_Handle.doStore('cgmName',i_jnt)    
        i_IK_Handle.doName()

        #Effector
        i_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
        #i_IK_Effector.doStore('cgmName',i_jnt)    
        i_IK_Effector.doName()

        l_iIK_handles.append(i_IK_Handle)
        l_iIK_effectors.append(i_IK_Effector)

        if i_module:#if we have a module, connect vis
            i_IK_Handle.overrideEnabled = 1		
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideDisplayType'))    

        #>> Distance nodes
        i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
        i_distanceObject.doStore('cgmName',i_jnt)
        i_distanceObject.addAttr('cgmType','measureNode',lock=True)
        i_distanceObject.doName(nameShapes = True)
        i_distanceObject.parent = i_grp.mNode#parent it
        i_distanceObject.overrideEnabled = 1
        i_distanceObject.overrideVisibility = 0

        #Connect things
        mc.connectAttr ((ml_follicleTransforms[i].mNode+'.translate'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_follicleTransforms[i+1].mNode+'.translate'),(i_distanceShape.mNode+'.endPoint'))

        ml_distanceObjects.append(i_distanceObject)
        ml_distanceShapes.append(i_distanceShape)

        if i_module:#Connect hides if we have a module instance:
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideDisplayType'))    


    #Connect the first joint's position since an IK handle isn't controlling it    
    attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[0].mNode,'%s.translate'%ml_jointList[0].mNode)
    #attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[-1].mNode,'%s.translate'%ml_jointList[-1].mNode)

    #>> Second part for the full twist setup
    aimChannel = orientation[0]  
    fixOptions = [0,90,180,-90,-180]      

    for i,i_jnt in enumerate(ml_jointList[:-1]):
        rotBuffer = mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)
        log.debug("rotBuffer: %s"%rotBuffer)
        #Create the poleVector
        poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,l_iIK_handles[i].mNode)  	
        optionCnt = 0
        while not cgmMath.isFloatEquivalent((mc.getAttr(i_jnt.mNode+'.r'+aimChannel)),0):
            log.debug("%s.r%s: %s"%(i_jnt.getShortName(),aimChannel,mc.getAttr(i_jnt.mNode+'.r'+aimChannel)))
            log.debug ("Trying the following for '%s':%s" %(l_iIK_handles[i].getShortName(),fixOptions[optionCnt]))
            attributes.doSetAttr(l_iIK_handles[i].mNode,'twist',fixOptions[optionCnt])
            optionCnt += 1
            if optionCnt == 4:
                raise StandardError,"failed to find a good twist value to zero out poleVector: %s"%(i_jnt.getShortName())

        if mc.xform (i_jnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
            log.debug("Found the following on '%s': %s"%(i_jnt.getShortName(),mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)))

    #>>>Hook up scales
    #==========================================================================
    #Translate scale
    """
    for i,i_jnt in enumerate(ml_jointList[1:]):
	#i is already offset, which we need as we want i to be the partn
	attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
                                 '%s.t%s'%(i_jnt.mNode,orientation[0]))	   """ 

    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    i_jntScaleBufferNode.doName()

    i_jntScaleBufferNode.connectParentNode(i_controlSurface.mNode,'surface','scaleBuffer')
    ml_mainMDs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):

        #Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(ml_distanceShapes[i].distance)#Store to our buffer
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to store joint distance: %s"%ml_distanceShapes[i].mNode

        #Create the mdNode
        i_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_md.operation = 2
        i_md.doStore('cgmName',i_jnt)
        i_md.addAttr('cgmTypeModifier','masterScale')
        i_md.doName()
        attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
                                 '%s.%s'%(i_md.mNode,'input1X'))
        attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                 '%s.%s'%(i_md.mNode,'input2X'))

        #Connect to the joint
        i_attr = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"distance_%s"%i,attrType = 'float',initialValue=0,lock=True)		
        i_attrResult = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True)	
        try:
            i_attr.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))
            i_attrResult.doConnectIn('%s.%s'%(i_md.mNode,'output.outputX'))
            i_attrResult.doConnectOut('%s.s%s'%(i_jnt.mNode,orientation[0]))

            for axis in orientation[1:]:
                attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,'masterScale'),#>>
                                         '%s.s%s'%(i_jnt.mNode,axis))	    
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to connect joint attrs: %s"%i_jnt.mNode

        #mc.pointConstraint(ml_follicleTransforms[i].mNode,i_jnt.mNode,maintainOffset = False)
        ml_mainMDs.append(i_md)#store the md



    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
        attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))	 

    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,'surfaceScaleBuffer':i_jntScaleBufferNode.mNode,'i_surfaceScaleBuffer':i_jntScaleBufferNode,'l_joints':jointList,'l_iJoints':ml_jointList}

def createConstraintSurfaceSegmentTranslatePosition(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]

    i_module = False
    i_rigNull = False
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
            i_rigNull = i_module.rigNull
        else:
            log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    except:pass

    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()

    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)

    i_controlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
    i_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    i_controlSurface.doName()

    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    l_snapToGroups = []
    il_snapToGroups = []
    il_upLocs = []

    #First thing we're going to do is create our follicles
    for i_jnt in ml_jointList:       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(i_jnt.mNode,i_controlSurface.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(i_controlSurface.mNode)
        i_follicleTrans = cgmMeta.cgmObject(l_follicleInfo[1])
        i_follicleShape = cgmMeta.cgmNode(l_follicleInfo[0])
        #> Name
        i_follicleTrans.doStore('cgmName',i_jnt)
        i_follicleTrans.doName()
        #>Set follicle value
        i_follicleShape.parameterU = l_closestInfo['normalizedU']
        i_follicleShape.parameterV = l_closestInfo['normalizedV']

        ml_follicleShapes.append(i_follicleShape)
        ml_follicleTransforms.append(i_follicleTrans)

        i_follicleTrans.parent = i_grp.mNode	

        #>> Surface Anchor ===================================================
        i_grpPos = cgmMeta.cgmObject( rigging.groupMeObject(i_jnt.mNode,False) )
        i_grpPos.doStore('cgmName',i_jnt)        
        i_grpOrient = cgmMeta.cgmObject( mc.duplicate(i_grpPos.mNode,returnRootsOnly=True,ic=True)[0] )
        i_grpPos.addAttr('cgmType','surfaceAnchor',attrType='string',lock=True)
        i_grpOrient.addAttr('cgmType','surfaceOrient',attrType='string',lock=True)
        i_grpPos.doName()
        i_grpOrient.doName()
        i_grpOrient.parent = i_grpPos.mNode

        i_jnt.connectParentNode(i_grpOrient.mNode,'snapToGroup','snapTarget')	

        #Contrain pos group
        constraint = mc.parentConstraint(i_follicleTrans.mNode,i_grpPos.mNode, maintainOffset=False)

        i_upLoc = i_jnt.doLoc()#Make up Loc
        i_upLoc.parent = i_grpPos.mNode
        mc.move(0,2,0,i_upLoc.mNode,os=True)

        #mc.aimConstraint(ml_jointList[],objGroup,maintainOffset = False, weight = 1, aimVector = aimVector, upVector = upVector, worldUpObject = upLoc, worldUpType = 'object' )        
        l_snapToGroups.append(i_grpOrient.mNode)
        il_snapToGroups.append(i_grpOrient)
        il_upLocs.append(i_upLoc)

    for i,i_grp in enumerate(il_snapToGroups[:-1]):
        mc.aimConstraint(il_snapToGroups[i+1].mNode,i_grp.mNode,
                         maintainOffset = False, weight = 1,
                         aimVector = [0,0,1], upVector = [0,1,0],
                         worldUpObject = il_upLocs[i].mNode,
                         worldUpType = 'object' )        


    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,
            'il_snapToGroups':il_snapToGroups,'l_snapToGroups':l_snapToGroups}


def createControlSurfaceSegment2(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]

    i_module = False
    i_rigNull = False
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
                i_rigNull = i_module.rigNull
        else:
            log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    except:pass

    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()

    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)

    i_controlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
    i_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    i_controlSurface.doName()

    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    ml_upGroups = []

    #First thing we're going to do is create our follicles
    for i,i_jnt in enumerate(ml_jointList):       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(i_jnt.mNode,i_controlSurface.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(i_controlSurface.mNode)
        i_follicleTrans = cgmMeta.asMeta(l_follicleInfo[1],'cgmObject',setClass=True)
        i_follicleShape = cgmMeta.asMeta(l_follicleInfo[0],'cgmNode')
        #> Name
        i_follicleTrans.doStore('cgmName',i_jnt)
        i_follicleTrans.doName()
        #>Set follicle value
        i_follicleShape.parameterU = l_closestInfo['normalizedU']
        i_follicleShape.parameterV = l_closestInfo['normalizedV']

        ml_follicleShapes.append(i_follicleShape)
        ml_follicleTransforms.append(i_follicleTrans)

        i_follicleTrans.parent = i_grp.mNode	

        #>>> loc
        """
	First part of full ribbon wist setup
	"""
        if i_jnt != ml_jointList[-1]:
            i_upLoc = i_jnt.doLoc()#Make up Loc
            i_locRotateGroup = i_jnt.doCreateAt()#group in place
            i_locRotateGroup.parent = i_follicleTrans.mNode
            i_locRotateGroup.doStore('cgmName',i_jnt)	    
            i_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
            i_locRotateGroup.doName()

            #Store the rotate group to the joint
            i_jnt.connectChildNode(i_locRotateGroup,'rotateUpGroup','drivenJoint')
            i_zeroGrp = cgmMeta.asMeta( i_locRotateGroup.doGroup(True),'cgmObject',setClass=True )
            i_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
            i_zeroGrp.doName()
            #connect some other data
            i_locRotateGroup.connectChildNode(i_follicleTrans,'follicle','drivenGroup')
            i_locRotateGroup.connectChildNode(i_locRotateGroup.parent,'zeroGroup')

            mc.makeIdentity(i_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)


            i_upLoc.parent = i_locRotateGroup.mNode
            mc.move(0,10,0,i_upLoc.mNode,os=True)	
            ml_upGroups.append(i_upLoc)


        #>> Surface Anchor ===================================================
        """
        i_grpPos = cgmMeta.cgmObject( rigging.groupMeObject(i_jnt.mNode,False) )
        i_grpPos.doStore('cgmName',i_jnt)        
        i_grpOrient = cgmMeta.cgmObject( mc.duplicate(i_grpPos.mNode,returnRootsOnly=True)[0] )
        i_grpPos.addAttr('cgmType','surfaceAnchor',attrType='string',lock=True)
        i_grpOrient.addAttr('cgmType','surfaceOrient',attrType='string',lock=True)
        i_grpPos.doName()
        i_grpOrient.doName()
        i_grpOrient.parent = i_grpPos.mNode

        constraint = mc.pointConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
        constraint = mc.orientConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
        """

    #Orient constrain our last joint to our last follicle
    #>>>DON'T Like this method --- mc.orientConstraint(ml_follicleTransforms[-1].mNode,ml_jointList[-1].mNode,maintainOffset = True)

    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    ml_distanceObjects = []
    ml_distanceShapes = []  
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.asMeta(ik_buffer[0],'cgmObject',setClass=True)
        i_IK_Handle.parent = ml_follicleTransforms[i+1].mNode
        i_IK_Handle.doStore('cgmName',i_jnt)    
        i_IK_Handle.doName()

        #Effector
        i_IK_Effector = cgmMeta.asMeta(ik_buffer[1],'cgmObject',setClass=True)        
        i_IK_Effector.doName()

        l_iIK_handles.append(i_IK_Handle)
        l_iIK_effectors.append(i_IK_Effector)	

        #>> Distance nodes
        i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
        i_distanceObject.doStore('cgmName',i_jnt)
        i_distanceObject.addAttr('cgmType','measureNode',lock=True)
        i_distanceObject.doName(nameShapes = True)
        i_distanceObject.parent = i_grp.mNode#parent it
        i_distanceObject.overrideEnabled = 1
        i_distanceObject.overrideVisibility = 0

        #Connect things
        mc.connectAttr ((ml_follicleTransforms[i].mNode+'.translate'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_follicleTransforms[i+1].mNode+'.translate'),(i_distanceShape.mNode+'.endPoint'))

        ml_distanceObjects.append(i_distanceObject)
        ml_distanceShapes.append(i_distanceShape)

    #Connect the first joint's position since an IK handle isn't controlling it    
    attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[0].mNode,'%s.translate'%ml_jointList[0].mNode)
    #attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[-1].mNode,'%s.translate'%ml_jointList[-1].mNode)

    #>> Second part for the full twist setup
    aimChannel = orientation[0]  
    fixOptions = [0,90,180,-90,-180]      

    for i,i_jnt in enumerate(ml_jointList[:-1]):
        rotBuffer = mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)
        log.debug("rotBuffer: %s"%rotBuffer)
        #Create the poleVector
        poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,l_iIK_handles[i].mNode)  	
        optionCnt = 0
        while not cgmMath.isFloatEquivalent((mc.getAttr(i_jnt.mNode+'.r'+aimChannel)),0):
            log.debug("%s.r%s: %s"%(i_jnt.getShortName(),aimChannel,mc.getAttr(i_jnt.mNode+'.r'+aimChannel)))
            log.debug ("Trying the following for '%s':%s" %(l_iIK_handles[i].getShortName(),fixOptions[optionCnt]))
            attributes.doSetAttr(l_iIK_handles[i].mNode,'twist',fixOptions[optionCnt])
            optionCnt += 1
            if optionCnt == 4:
                raise StandardError,"failed to find a good twist value to zero out poleVector: %s"%(i_jnt.getShortName())

        if mc.xform (i_jnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
            log.debug("Found the following on '%s': %s"%(i_jnt.getShortName(),mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)))

    #>>>Hook up scales
    #===================================================================
    #World scale

    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    i_jntScaleBufferNode.doName()

    i_jntScaleBufferNode.connectParentNode(i_controlSurface.mNode,'surface','scaleBuffer')
    ml_mainMDs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        #Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(ml_distanceShapes[i].distance)#Store to our buffer
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to store joint distance: %s"%ml_distanceShapes[i].mNode

        #Create the mdNode
        i_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_md.operation = 2
        i_md.doStore('cgmName',i_jnt)
        i_md.addAttr('cgmTypeModifier','masterScale')
        i_md.doName()
        attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
                                 '%s.%s'%(i_md.mNode,'input1X'))
        attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                 '%s.%s'%(i_md.mNode,'input2X'))

        #Connect to the joint
        try:
            attributes.doConnectAttr('%s.%s'%(i_md.mNode,'output.outputX'),#>>
                                     '%s.s%s'%(i_jnt.mNode,orientation[0]))
            for axis in orientation[1:]:
                attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,'masterScale'),#>>
                                         '%s.s%s'%(i_jnt.mNode,axis))	    
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to connect joint attrs: %s"%i_jnt.mNode

        ml_mainMDs.append(i_md)#store the md

        #If second to last we need to add an extra md

    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
        attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))	 

    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,'surfaceScaleBuffer':i_jntScaleBufferNode.mNode,'i_surfaceScaleBuffer':i_jntScaleBufferNode,'l_joints':jointList,'l_iJoints':ml_jointList}


def createControlSurfaceSegmentBAK2(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]

    i_module = False
    i_rigNull = False
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
                i_rigNull = i_module.rigNull
        else:
            log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    except:pass
    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()

    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)

    i_controlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
    i_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    i_controlSurface.doName()

    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    ml_upGroups = []

    #First thing we're going to do is create our follicles
    for i,i_jnt in enumerate(ml_jointList):       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(i_jnt.mNode,i_controlSurface.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(i_controlSurface.mNode)
        i_follicleTrans = cgmMeta.cgmObject(l_follicleInfo[1])
        i_follicleShape = cgmMeta.cgmNode(l_follicleInfo[0])
        #> Name
        i_follicleTrans.doStore('cgmName',i_jnt)
        i_follicleTrans.doName()
        #>Set follicle value
        i_follicleShape.parameterU = l_closestInfo['normalizedU']
        i_follicleShape.parameterV = l_closestInfo['normalizedV']

        ml_follicleShapes.append(i_follicleShape)
        ml_follicleTransforms.append(i_follicleTrans)

        i_follicleTrans.parent = i_grp.mNode	

        #>>> loc
        """
	i_upLoc = i_jnt.doLoc()#Make up Loc
	i_upLoc.parent = i_follicleTrans.mNode
	mc.move(0,2,0,i_upLoc.mNode,os=True)	
	ml_upGroups.append(i_upLoc)
	"""

        #>> Surface Anchor ===================================================
        """
        i_grpPos = cgmMeta.cgmObject( rigging.groupMeObject(i_jnt.mNode,False) )
        i_grpPos.doStore('cgmName',i_jnt)        
        i_grpOrient = cgmMeta.cgmObject( mc.duplicate(i_grpPos.mNode,returnRootsOnly=True)[0] )
        i_grpPos.addAttr('cgmType','surfaceAnchor',attrType='string',lock=True)
        i_grpOrient.addAttr('cgmType','surfaceOrient',attrType='string',lock=True)
        i_grpPos.doName()
        i_grpOrient.doName()
        i_grpOrient.parent = i_grpPos.mNode

        constraint = mc.pointConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
        constraint = mc.orientConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
        """

        #>>>Connect via constraint - no worky
        #constraint = mc.pointConstraint(i_grpOrient.mNode,i_jnt.mNode, maintainOffset=True)
        #constraint = mc.orientConstraint(i_grpOrient.mNode,i_jnt.mNode, maintainOffset=True)

        #constraints.doConstraintObjectGroup(i_transFollicle.mNode,transform,['point','orient'])
        #>>> Connect the joint
        #attributes.doConnectAttr('%s.translate'%i_grpPos.mNode,'%s.translate'%i_jnt.mNode)

    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    ml_distanceObjects = []
    ml_distanceShapes = []  
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.cgmObject(ik_buffer[0])
        i_IK_Handle.parent = ml_follicleTransforms[i+1].mNode
        i_IK_Handle.doStore('cgmName',i_jnt)    
        i_IK_Handle.doName()

        #Effector
        i_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
        #i_IK_Effector.doStore('cgmName',i_jnt)    
        i_IK_Effector.doName()

        l_iIK_handles.append(i_IK_Handle)
        l_iIK_effectors.append(i_IK_Effector)

        #>> create up loc
        #i_loc = i_jnt.doLoc()
        #mc.move(0, 10, 0, i_loc.mNode, r=True,os=True,wd=True)

        """poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,i_IK_Handle.mNode)"""

        #>> Distance nodes
        i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
        i_distanceObject.doStore('cgmName',i_jnt)
        i_distanceObject.addAttr('cgmType','measureNode',lock=True)
        i_distanceObject.doName(nameShapes = True)
        i_distanceObject.parent = i_grp.mNode#parent it
        i_distanceObject.overrideEnabled = 1
        i_distanceObject.overrideVisibility = 0

        #Connect things
        mc.connectAttr ((ml_follicleTransforms[i].mNode+'.translate'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_follicleTransforms[i+1].mNode+'.translate'),(i_distanceShape.mNode+'.endPoint'))

        ml_distanceObjects.append(i_distanceObject)
        ml_distanceShapes.append(i_distanceShape)

    #Connect the first joint's position since an IK handle isn't controlling it    
    attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[0].mNode,'%s.translate'%ml_jointList[0].mNode)

    #>>>Hook up scales
    #World scale

    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    i_jntScaleBufferNode.doName()

    i_jntScaleBufferNode.connectParentNode(i_controlSurface.mNode,'surface','scaleBuffer')

    for i,i_jnt in enumerate(ml_jointList[:-1]):
        #Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(ml_distanceShapes[i].distance)#Store to our buffer
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to store joint distance: %s"%ml_distanceShapes[i].mNode

        #Create the mdNode
        i_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_md.operation = 2
        i_md.doStore('cgmName',i_jnt)
        i_md.addAttr('cgmTypeModifier','masterScale')
        i_md.doName()
        attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
                                 '%s.%s'%(i_md.mNode,'input1X'))
        attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                 '%s.%s'%(i_md.mNode,'input2X'))

        #Connect to the joint
        try:
            attributes.doConnectAttr('%s.%s'%(i_md.mNode,'output.outputX'),#>>
                                     '%s.s%s'%(i_jnt.mNode,orientation[0]))
            for axis in orientation[1:]:
                attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,'masterScale'),#>>
                                         '%s.s%s'%(i_jnt.mNode,axis))	    
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to connect joint attrs: %s"%i_jnt.mNode

        """
	mdArg = [{'result':[i_jnt.mNode,'sy'],'drivers':[[ml_distanceShapes[i].mNode,'distance'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],'driven':[]},
	         {'result':[i_jnt.mNode,'sx'],'drivers':[[ml_distanceShapes[i].mNode,'distance'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],'driven':[]}]
	#mdArg = [{'drivers':[[i_jntScaleBufferNode,'masterScale'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],
	          #'driven':[[i_jnt.mNode,'sy'],[i_jnt.mNode,'sx']]}]

        try:NodeF.build_mdNetwork(mdArg, defaultAttrType='float',operation=2)
	except Exception,error:
	    log.error(error)
	    raise StandardError,"Failed to build network: %s"%mdArg 
	"""

    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
        attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))	 

    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,'surfaceScaleBuffer':i_jntScaleBufferNode.mNode,'i_surfaceScaleBuffer':i_jntScaleBufferNode,'l_joints':jointList,'l_iJoints':ml_jointList}


def addRibbonTwistToControlSetupRewrite(*args,**kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName= "addRibbonTwistToControlSetup"
            self._b_reportTimes = True
            self._b_autoProgressBar = 1
            self._str_funcHelp = "This is our general purpose spline IK segment\nIt has lots of features:)"
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'jointList',"default":None,'help':"List or metalist of joints","argType":"joints"},
                                         {'kw':'startControlDriver',"default":None,'help':"Start twist attribute","argType":"attribute arg"},
                                         {'kw':'endControlDriver',"default":None,'help':"Start twist attribute","argType":"attribute arg"},
                                         {'kw':'orientation',"default":'zyx','help':"What is the joints orientation","argType":"string"},
                                         {'kw':'rotateGroupAxis',"default":'rotateZ','help':"Axis which rotates the rotate group's twist","argType":"attribute string - most likely rotation"},
                                         {'kw':'moduleInstance',"default":None,'help':"cgmModule to use for connecting on build","argType":"cgmModule"}]	                                 

            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Verify','call':self._verify_}]

            #=================================================================
        def _verify_(self):
            #THIS IS PLACEHODER TILL WE GET BACK TO IT!
            return
            try:#Query ===========================================================================================
                self.ml_joints = cgmMeta.validateObjListArg(self.d_kws['jointList'],mType = cgmMeta.cgmObject, mayaType=['joint'], noneValid = False)
                self.l_joints = [mJnt.p_nameShort for mJnt in self.ml_joints]
                self.int_lenJoints = len(self.ml_joints)#because it's called repeatedly
                self.mi_useCurve = cgmMeta.validateObjArg(self.d_kws['useCurve'],mayaType=['nurbsCurve'],noneValid = True)
                self.mi_module = cgmMeta.validateObjArg(self.d_kws['moduleInstance'],noneValid = True)
                try:self.mi_module.isModule()
                except:self.mi_module = False
                self.mi_mayaOrientation = cgmValid.simpleOrientation(self.d_kws['orientation'])
                self.str_orientation = self.mi_mayaOrientation.p_string
                self.str_secondaryAxis = cgmValid.stringArg(self.d_kws['secondaryAxis'],noneValid=True)
                self.str_baseName = cgmValid.stringArg(self.d_kws['baseName'],noneValid=True)
                self.str_connectBy = cgmValid.stringArg(self.d_kws['connectBy'],noneValid=True)		
                self.b_addMidTwist = cgmValid.boolArg(self.d_kws['addMidTwist'])
                self.b_advancedTwistSetup = cgmValid.boolArg(self.d_kws['advancedTwistSetup'])
                self.b_extendTwistToEnd= cgmValid.boolArg(self.d_kws['extendTwistToEnd'])
            except Exception,error:raise Exception,"[Query | error: {0}".format(error)  

            try:#Validate =====================================================================================
                if self.b_addMidTwist and self.int_lenJoints <4:
                    raise StandardError,"must have at least 3 joints for a mid twist setup"
                if self.int_lenJoints<3:
                    raise StandardError,"needs at least three joints"

                #Good way to verify an instance list? #validate orientation             
                #> axis -------------------------------------------------------------
                self.axis_aim = cgmValid.simpleAxis("%s+"%self.str_orientation [0])
                self.axis_aimNeg = cgmValid.simpleAxis("%s-"%self.str_orientation [0])
                self.axis_up = cgmValid.simpleAxis("%s+"%self.str_orientation [1])

                self.v_aim = self.axis_aim.p_vector#aimVector
                self.v_aimNeg = self.axis_aimNeg.p_vector#aimVectorNegative
                self.v_up = self.axis_up.p_vector   #upVector

                self.outChannel = self.str_orientation [2]#outChannel
                self.upChannel = '%sup'%self.str_orientation [1]#upChannel

            except Exception,error:
                raise StandardError,"[data validation | error: {0}".format(error)  

            try:#>>> Module instance =====================================================================================
                self.mi_rigNull = False	
                if self.mi_module:
                    self.mi_rigNull = self.mi_module.rigNull	

                    if self.str_baseName is None:
                        self.str_baseName = self.mi_module.getPartNameBase()#Get part base name	    
                        log.debug('baseName set to module: %s'%self.str_baseName)	    	    
                if self.str_baseName is None:self.str_baseName = 'testSegmentCurve'    

            except Exception,error:raise Exception,"[Module checks | error: {0}".format(error) 	    
    return fncWrap(*args,**kws).go()

def addRibbonTwistToControlSetupOld(jointList,
                                    startControlDriver = None, endControlDriver = None,
                                    rotateGroupAxis = 'rotateZ',
                                    orientation = 'zyx', moduleInstance = None):
    """
    Implementing this ribbon method to or control surface setup:
    http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
    """
    def createAverageNode(driver1,driver2,driven = None):
        #Create the mdNode
        log.debug("driver1: %s"%driver1)
        log.debug("driver2: %s"%driver2)
        assert type(driver1) is list and len(driver1) == 2,"Driver1 wrong: %s"%driver1
        assert type(driver2) is list and len(driver1) == 2,"Driver2 wrong: %s"%driver2
        driver1Combined = "%s.%s"%(driver1[0],driver1[1])
        driver2Combined = "%s.%s"%(driver2[0],driver2[1])
        assert mc.objExists(driver1Combined)	
        assert mc.objExists(driver2Combined)

        if driven is not None:
            assert type(driven) is list and len(driver1) == 2,"Driven wrong: %s"%driven	    
            drivenCombined = "%s.%s"%(driven[0],driven[1])
            assert mc.objExists(drivenCombined)	    
            log.debug("drivenCombined: %s"%drivenCombined)

        log.debug("driver1Combined: %s"%driver1Combined)
        log.debug("driver2Combined: %s"%driver2Combined)

        #Create the node
        i_pma = cgmMeta.cgmNode(mc.createNode('plusMinusAverage'))
        i_pma.operation = 3
        nameBuffer = "%s_to_%s"%(mc.ls(driver1[0],sn = True)[0],mc.ls(driver2[0],sn = True)[0])
        i_pma.addAttr('cgmName',nameBuffer,lock=True)	
        #i_pma.doStore('cgmName',i_jnt)
        i_pma.addAttr('cgmTypeModifier','twist')
        i_pma.doName()

        #Make our connections
        attributes.doConnectAttr(driver1Combined,'%s.input1D[0]'%i_pma.mNode)
        attributes.doConnectAttr(driver2Combined,'%s.input1D[1]'%i_pma.mNode)

        if driven is not None:
            attributes.doConnectAttr('%s.output1D'%i_pma.mNode,drivenCombined)

        return i_pma

    def averageNetwork_three(indices):
        """ """
        log.debug("averageNetwork_three: %s"%indices)
        assert len(indices) == 3,"averageNetwork_three requires 3 indices"
        for i in indices:
            if i not in d_drivenPlugs.keys():
                raise StandardError,"Index doesn't exist in d_drivenPlugs: %s"%i
        d1 = d_driverPlugs[indices[0]]
        d2 = d_driverPlugs[indices[-1]]
        driven = d_drivenPlugs[indices[1]]

        i_buffer = createAverageNode(d1,d2,driven)
        #Register network
        d_driverPlugs[indices[1]] = [i_buffer.mNode,"output1D"]

    def averageNetwork_four(indices):
        """ 
        If we don't have an actual middle object we still need to average
        ex[0,1,2,3]
        [0,3]
        [0,3],1 | [0,3],2
        """
        log.debug("averageNetwork_four: %s"%indices)
        assert len(indices) == 4,"averageNetwork_four requires 4 indices"
        for i in indices:
            if i not in d_drivenPlugs.keys():
                raise StandardError,"Index doesn't exist in d_drivenPlugs: %s"%i
        assert indices[0] in d_drivenPlugs.keys(),"four mode indice not in d_drivenPlugs: %s"%indices[0]
        assert indices[-1] in d_drivenPlugs.keys(),"four mode indice not in d_drivenPlugs: %s"%indices[-1]

        #Get the middle driven
        driven1 = d_drivenPlugs[indices[1]]	
        driven2 = d_drivenPlugs[indices[2]]	
        driver1 = d_driverPlugs[indices[0]]
        driver2 = d_driverPlugs[indices[-1]]

        #Blend average
        blendDriverIndex = (indices[0],indices[-1])	
        try:
            if blendDriverIndex not in d_drivenPlugs.keys():
                #If our blend driver isn't in the keys, we need to make it. first check the drivers exist
                i_blendPMA = createAverageNode(driver1,driver2)
                blendConnection = [i_blendPMA.mNode,"output1D"]
            else:
                blendConnection = d_drivenPlugs[blendDriverIndex]
        except Exception,error:
            log.error(error)
            raise StandardError,"averageNetwork_four>failed to find or build blendDriver: %s"%blendDriverIndex


        #Hook up first
        createAverageNode(blendConnection,
                          driver1,
                          d_drivenPlugs[1])	
        #Hook up second
        createAverageNode(blendConnection,
                          driver2,
                          d_drivenPlugs[2])	

    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()
    if len(jointList) <3:
        raise StandardError,"addRibbonTwistToControlSetup requires 3 joints to work" 

    #moduleInstance
    i_module = False
    i_rigNull = False
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
                i_rigNull = i_module.rigNull
        else:
            log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    except:pass

    #Initialize joint list
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Gather info:
    #d_driverPlugs = {index:['obj','ry']....}
    #d_drivenPlugs = {index:['rotateGroup','.r']...}
    #twistStartPlug,twistEndPlug
    #For each joint to be connected, we need a connection plug and a rotate group
    #We need a driver start and end plug    
    d_drivenPlugs = {}
    d_driverPlugs = {}
    d_mi_jointToIndex = {}
    #Make sure all but the last have rotate groups,grab those plugs
    for i,i_jnt in enumerate(ml_jointList):
        try:
            d_mi_jointToIndex[i_jnt]=i
            if i_jnt == ml_jointList[-1]:#If it's the last
                d_drivenPlugs[i] = [i_jnt.getShortName(),"rotate%s"%aimChannel]
            else:   
                try:rotateGroupBuffer = i_jnt.getMessage('rotateUpGroup',False)[0]
                except Exception,error: raise Exception,"[No rotateUpGroup found]{%s}"%(error)

                if not rotateGroupBuffer:
                    raise StandardError,"'%s' lacks a connected rotateUpGroup!"%i_jnt.getShortName()
                if mc.objExists('%s.%s'%(rotateGroupBuffer,rotateGroupAxis)):
                    d_drivenPlugs[i] = [rotateGroupBuffer,rotateGroupAxis]
                    #We need to reparent and point constrain our rotate zero groups
                    if i_jnt.rotateUpGroup.getMessage('zeroGroup') and i_jnt.rotateUpGroup.getMessage('follicle'):
                        i_zeroGroup = i_jnt.rotateUpGroup.zeroGroup#Get zero
                        i_follicle = i_jnt.rotateUpGroup.follicle#get follicle
                        i_zeroGroup.parent = i_follicle.parent#parent zerogroup to follicle
                        """mc.pointConstraint(i_follicle.mNode,i_zeroGroup.mNode,
					   maintainOffset=False)"""	
                        mc.parentConstraint(i_follicle.mNode,i_zeroGroup.mNode,
                                            maintainOffset=True)
                else:
                    raise StandardError,"Rotate group has no axis: %s!"%rotateGroupAxis
        except Exception,error: raise Exception,"['%s' gather dataFail]{%s}"%(i_jnt.p_nameShort,error)

    #replace our start and end with our drivers
    d_driverPlugs[0] = startControlDriver
    d_driverPlugs[len(ml_jointList)-1] = endControlDriver

    log.info("drivenPlugs: %s"%d_drivenPlugs)
    log.info("driverPlugs: %s"%d_driverPlugs)

    #>>>Setup
    #Connect first and last
    #mc.pointConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
    attributes.doConnectAttr('%s.%s'%(startControlDriver[0],startControlDriver[1]),
                             '%s.%s'%(d_drivenPlugs[0][0],d_drivenPlugs[0][1]))
    index = ml_jointList.index(ml_jointList[-1]) 
    #Direct connect no worky
    #attributes.doConnectAttr('%s.%s'%(endControlDriver[0],endControlDriver[1]),
                                #'%s.%s'%(d_drivenPlugs[index][0],d_drivenPlugs[index][1]))

    #Connect rest
    if len(ml_jointList) == 3:
        #Grab two control drivers, blend between them, drive mid
        index = ml_jointList.index(ml_jointList[1])
        createAverageNode(startControlDriver,endControlDriver,d_drivenPlugs[index])
    elif len(ml_jointList) == 4:
        #Grab two control drivers, blend
        i_blendPMA = createAverageNode(startControlDriver,endControlDriver)

        #Hook up first
        createAverageNode([i_blendPMA.mNode,"output1D"],
                          startControlDriver,
                          d_drivenPlugs[1])	
        #Hook up second
        createAverageNode([i_blendPMA.mNode,"output1D"],
                          endControlDriver,
                          d_drivenPlugs[2])		
        """
	for i in [1,2]:
	    index = ml_jointList.index(ml_jointList[i])
	    createAverageNode("%s.output1D"%i_blendPMA.mNode,
	                      endControlDriver,
	                      d_drivenPlugs[index])"""	    

        #averageNetwork_four()

    else:#factor and run
        #Make a factored list
        l_factored = lists.returnFactoredConstraintList(range(len(jointList)),3)
        log.info(l_factored)
        try:
            for chunk in l_factored:
                log.info("On chunk: %s"%chunk)	    
                if len(chunk) == 3:
                    averageNetwork_three(chunk)
                elif len(chunk) == 4:
                    averageNetwork_four(chunk)
                else:
                    raise StandardError,"Chunk too long: %s"%chunk
        except Exception,error:
            log.error(error)
            raise StandardError,"Chunk failed to network: %s"%chunk

    #Finally build full sum
    i_pma = cgmMeta.cgmNode(mc.createNode('plusMinusAverage'))
    i_pma.operation = 1#Sum
    if moduleInstance:
        i_pma.addAttr('cgmName',moduleInstance.cgmName,lock=True)	
    i_pma.addAttr('cgmTypeModifier','twistSum')
    i_pma.doName()

    #Make our connections
    for i,driver in enumerate([startControlDriver,endControlDriver]):
        log.info(i)
        log.info(driver)
        attributes.doConnectAttr('%s.%s'%(driver[0],driver[1]),'%s.input1D[%s]'%(i_pma.mNode,i))

    #Last joing arg
    mPlug_finalRot = cgmMeta.cgmAttr(i_pma,"final_rotation",attrType='float')
    log.debug("startControlDriver: %s"%startControlDriver)
    arg ="%s = %s.output1D - %s.%s"%(mPlug_finalRot.p_combinedShortName,i_pma.getShortName(), startControlDriver[0],startControlDriver[1])
    NodeF.argsToNodes(arg).doBuild()
    attributes.doConnectAttr('%s'%(mPlug_finalRot.p_combinedShortName),'%s.r%s'%(jointList[-1],orientation[0]))

    return {'mi_pmaTwistSum':i_pma}

    """
    for key in d_drivenPlugs.keys():
	log.debug(d_drivenPlugs[key])
	log.debug('%s.%s'%(d_drivenPlugs[key][0],d_drivenPlugs[key][1]))
	log.debug('%s.input1D[%s]'%(i_pma.mNode,i))
	attributes.doConnectAttr('%s.%s'%(d_drivenPlugs[key][0],d_drivenPlugs[key][1]),'%s.input1D[%s]'%(i_pma.mNode,i))
	"""


def addSquashAndStretchToControlSurfaceSetupSCALETRANSLATE(attributeHolder,jointList,orientation = 'zyx', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()

    #moduleInstance
    i_rigNull = False
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
            i_rigNull = i_module.rigNull
        else:
            log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    except:pass

    #attributeHolder
    i_holder = cgmMeta.cgmNode(attributeHolder)

    #Initialize joint list
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]

    ml_scaleNodes = []
    ml_sqrtNodes = []
    ml_attrs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        #make sure attr exists
        i_attr = cgmMeta.cgmAttr(i_holder,"scaleMult_%s"%i,attrType = 'float',initialValue=1)
        outScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%outChannel)
        upScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%upChannel)

        #Create the multScale
        i_mdScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_mdScale.operation = 2
        i_mdScale.doStore('cgmName',i_jnt)
        i_mdScale.addAttr('cgmTypeModifier','multScale')
        i_mdScale.doName()
        for channel in [aimChannel,outChannel,upChannel]:
            attributes.doConnectAttr('%s.scaleResult_%s'%(i_holder.mNode,i),#>>
                                     '%s.input1%s'%(i_mdScale.mNode,channel))	    
            """attributes.doConnectAttr('%s.scale%s'%(i_jnt.mNode,aimChannel),#>>
	                             '%s.input1%s'%(i_mdScale.mNode,channel))"""
            attributes.doConnectAttr('%s'%(outScalePlug),#>>
                                     '%s.input2%s'%(i_mdScale.mNode,channel))

        #Create the sqrtNode
        i_sqrtScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_sqrtScale.operation = 3#set to power
        i_sqrtScale.doStore('cgmName',i_jnt)
        i_sqrtScale.addAttr('cgmTypeModifier','sqrtScale')
        i_sqrtScale.doName()
        for channel in [aimChannel,outChannel,upChannel]:
            attributes.doConnectAttr('%s.output%s'%(i_mdScale.mNode,channel),#>>
                                     '%s.input1%s'%(i_sqrtScale.mNode,channel))
            mc.setAttr("%s.input2"%(i_sqrtScale.mNode)+channel,.5)

        #Create the invScale
        i_invScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_invScale.operation = 2
        i_invScale.doStore('cgmName',i_jnt)
        i_invScale.addAttr('cgmTypeModifier','invScale')
        i_invScale.doName()
        for channel in [aimChannel,outChannel,upChannel]:
            mc.setAttr("%s.input1"%(i_invScale.mNode)+channel,1)	    
            attributes.doConnectAttr('%s.output%s'%(i_sqrtScale.mNode,channel),#>>
                                     '%s.input2%s'%(i_invScale.mNode,channel))

        #Create the powScale
        i_powScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_powScale.operation = 3
        i_powScale.doStore('cgmName',i_jnt)
        i_powScale.addAttr('cgmTypeModifier','powScale')
        i_powScale.doName()
        for channel in [aimChannel,outChannel,upChannel]:
            attributes.doConnectAttr('%s.output%s'%(i_invScale.mNode,channel),#>>
                                     '%s.input1%s'%(i_powScale.mNode,channel))
            attributes.doConnectAttr('%s'%(i_attr.p_combinedName),#>>
                                     '%s.input2%s'%(i_powScale.mNode,channel))

        #Create the worldScale multiplier node
        i_worldScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_worldScale.operation = 1
        i_worldScale.doStore('cgmName',i_jnt)
        i_worldScale.addAttr('cgmTypeModifier','worldScale')
        i_worldScale.doName()

        for channel in [aimChannel,outChannel,upChannel]:
            mc.setAttr("%s.input1"%(i_worldScale.mNode)+channel,1)
            #Connect powScale to the worldScale
            attributes.doConnectAttr('%s.output%s'%(i_powScale.mNode,channel),#>>
                                     '%s.input1%s'%(i_worldScale.mNode,channel))
        #Connect original plugs
        attributes.doConnectAttr('%s'%(outScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,outChannel))  
        attributes.doConnectAttr('%s'%(upScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,upChannel)) 

        #Connect to joint
        attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,outChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,outChannel))  
        attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,upChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,upChannel))

        '''attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,aimChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,aimChannel))	'''

        #>>>Fix the translate aim scale
        '''if i>0:
	    aimTransScalePlug = attributes.doBreakConnection(i_jnt.mNode,"translate%s"%aimChannel)
	    log.debug(aimTransScalePlug)
	    i_aimScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	    i_aimScale.operation = 2
	    i_aimScale.doStore('cgmName',i_jnt)
	    i_aimScale.addAttr('cgmTypeModifier','aimScale')
	    i_aimScale.doName()
	    """attributes.doConnectAttr('%s.scaleResult_%s'%(i_holder.mNode,i-1),#>>
		                     '%s.input1%s'%(i_aimScale.mNode,aimChannel))"""
	    attributes.doConnectAttr('%s.scale%s'%(ml_jointList[i-1].mNode,aimChannel),#>>
		                     '%s.input1%s'%(i_aimScale.mNode,aimChannel))	    
	    attributes.doConnectAttr('%s'%aimTransScalePlug,#>>
		                     '%s.input2%s'%(i_aimScale.mNode,aimChannel))	
	    attributes.doConnectAttr('%s.output%s'%(i_aimScale.mNode,aimChannel),#>>
		                     '%s.translate%s'%(i_jnt.mNode,aimChannel))	
	    '''
        ml_attrs.append(i_attr)


def addSquashAndStretchToSegmentCurveSetup(attributeHolder,jointList,connectBy = 'scale',
                                           orientation = 'zyx', moduleInstance = None):
    """

    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()

    #moduleInstance
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
    except:pass

    #attributeHolder
    i_holder = cgmMeta.validateObjArg(attributeHolder,cgmMeta.cgmBufferNode,noneValid=False) 

    '''
    Okay, we need to build a scale blender that will 1) give us a 0-1 value, and a condition node to use that or the segmentScale Factor
    '''
    #mPlug_result_segmentScale = cgmMeta.cgmAttr(i_holder,"result_segmentScale",attrType = 'float',hidden = True)
    #mPlug_neg_segmentScale = cgmMeta.cgmAttr(i_holder,"result_negateSegmentScale",attrType = 'float',hidden = True)
    #mPlug_blend_segmentScale = cgmMeta.cgmAttr(i_holder,"result_blendSegmentScale",attrType = 'float',hidden = True)

    mPlug_segmentScale = cgmMeta.cgmAttr(i_holder,"segmentScaleMult",attrType = 'float',
                                         initialValue=1.0,hidden=False,defaultValue=1.0,keyable=True)	
    '''
    #arg_smileOn = "{0} = if {1} >= 0: {2} else 0".format(
    arg_negateSegFactor = "{0} = 1 - {1}".format(mPlug_neg_segmentScale.p_combinedShortName,
                                                 mPlug_segmentScale.p_combinedShortName)

    arg_blendSegFactor = "{0} = {1} + {2}".format(mPlug_blend_segmentScale.p_combinedShortName,
                                                  mPlug_neg_segmentScale.p_combinedShortName,
                                                  mPlug_segmentScale.p_combinedShortName)

    arg_resSegFactor = "{0} = if {1} >= 1: {2} else {3}".format(mPlug_result_segmentScale.p_combinedShortName,
                                                                mPlug_segmentScale.p_combinedShortName,
                                                                mPlug_segmentScale.p_combinedShortName,
                                                                mPlug_blend_segmentScale.p_combinedName)

    for a in arg_negateSegFactor,arg_resSegFactor,arg_blendSegFactor:
	NodeF.argsToNodes(a).doBuild()
    '''    
    #Initialize joint list
    ml_jointList = cgmMeta.validateObjListArg(jointList,cgmMeta.cgmObject,noneValid=False)   

    ml_scaleNodes = []
    ml_sqrtNodes = []
    ml_attrs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        #make sure attr exists
        i_attr = cgmMeta.cgmAttr(i_holder,"scaleMult_{0}".format(i),attrType = 'float',initialValue=1)
        mPlug_resultScaleMult = cgmMeta.cgmAttr(i_holder,
                                                "result_scaleMultByFactor_{0}".format(i),
                                                attrType = 'float',hidden=True)

        arg_blendSegFactor = "{0} = {1} * {2}".format(mPlug_resultScaleMult.p_combinedShortName,
                                                      i_attr.p_combinedShortName,
                                                      mPlug_segmentScale.p_combinedShortName)	
        NodeF.argsToNodes(arg_blendSegFactor).doBuild()

        #outScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%outChannel)
        #upScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%upChannel)

        if connectBy == 'translate':
            mainDriver = '{0}.scaleResult_{1}'.format(i_holder.mNode,(i))
        else:
            mainDriver = '%s.scale%s'%(i_jnt.mNode,aimChannel)	
        log.debug(mainDriver)

        #Create the sqrtNode
        i_sqrtScale = cgmMeta.cgmNode(nodeType= 'multiplyDivide')
        i_sqrtScale.operation = 3#set to power
        i_sqrtScale.doStore('cgmName',i_jnt)
        i_sqrtScale.addAttr('cgmTypeModifier','sqrtScale')
        i_sqrtScale.doName()
        for channel in [outChannel,upChannel]:
            attributes.doConnectAttr(mainDriver,#>>
                                     '%s.input1%s'%(i_sqrtScale.mNode,channel))	    
            mc.setAttr("%s.input2"%(i_sqrtScale.mNode)+channel,.5)

        #Create the invScale
        i_invScale = cgmMeta.cgmNode(nodeType= 'multiplyDivide')
        i_invScale.operation = 2
        i_invScale.doStore('cgmName',i_jnt)
        i_invScale.addAttr('cgmTypeModifier','invScale')
        i_invScale.doName()
        for channel in [outChannel,upChannel]:
            mc.setAttr("%s.input1"%(i_invScale.mNode)+channel,1)	    
            attributes.doConnectAttr('%s.output%s'%(i_sqrtScale.mNode,channel),#>>
                                     '%s.input2%s'%(i_invScale.mNode,channel))

        #Create the powScale
        i_powScale = cgmMeta.cgmNode(nodeType= 'multiplyDivide')
        i_powScale.operation = 3
        i_powScale.doStore('cgmName',i_jnt)
        i_powScale.addAttr('cgmTypeModifier','powScale')
        i_powScale.doName()
        for channel in [outChannel,upChannel]:
            attributes.doConnectAttr('%s.output%s'%(i_invScale.mNode,channel),#>>
                                     '%s.input1%s'%(i_powScale.mNode,channel))
            attributes.doConnectAttr('%s'%(mPlug_resultScaleMult.p_combinedName),#>> was i_attr
                                     '%s.input2%s'%(i_powScale.mNode,channel))

        #Create the mdNode
        '''
        i_mdSegmentScaleMult = cgmMeta.cgmNode(nodeType= 'multiplyDivide')
        i_mdSegmentScaleMult.operation = 1
        i_mdSegmentScaleMult.doStore('cgmName',i_jnt)
        i_mdSegmentScaleMult.addAttr('cgmTypeModifier','segmentScaleMult')
        i_mdSegmentScaleMult.doName()            
        for channel in [outChannel,upChannel]:
            attributes.doConnectAttr('%s.output%s'%(i_powScale.mNode,channel),#>>
                                     '%s.input1%s'%(i_mdSegmentScaleMult.mNode,channel))
            attributes.doConnectAttr('%s'%(mPlug_result_segmentScale.p_combinedName),#>>
                                     '%s.input2%s'%(i_mdSegmentScaleMult.mNode,channel)) '''       

        """
	#Create the worldScale multiplier node
	i_worldScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_worldScale.operation = 1
	i_worldScale.doStore('cgmName',i_jnt)
	i_worldScale.addAttr('cgmTypeModifier','worldScale')
	i_worldScale.doName()
	for channel in [outChannel,upChannel]:
	    mc.setAttr("%s.input1"%(i_worldScale.mNode)+channel,1)
	    #Connect powScale to the worldScale
	    attributes.doConnectAttr('%s.output%s'%(i_powScale.mNode,channel),#>>
	                             '%s.input1%s'%(i_worldScale.mNode,channel))
	#Connect original plugs
	attributes.doConnectAttr('%s'%(outScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,outChannel))  
	attributes.doConnectAttr('%s'%(upScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,upChannel))""" 

        #Connect to joint
        attributes.doConnectAttr('%s.output%s'%(i_powScale.mNode,outChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,outChannel))  
        attributes.doConnectAttr('%s.output%s'%(i_powScale.mNode,upChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,upChannel)) 	

        ml_attrs.append(i_attr)

#@cgmGeneral.Timer
def addAdditiveScaleToSegmentCurveSetup(segmentCurve, orientation = 'zyx', moduleInstance = None):
    """
    Method for additive scale setup to a cgmSegment. Drivers for out/up should be setup as:
    -1 * ((1-driver1) + (1-driver2)) and connected back to the out/up in's
    """
    #>>> Validate info
    mi_segmentCurve = cgmMeta.validateObjArg(segmentCurve,'cgmObject',False)
    try:ml_drivenJoints = cgmMeta.validateObjListArg( mi_segmentCurve.msgList_get('drivenJoints',asMeta = True)[:-1],cgmMeta.cgmObject,False)
    except Exception,error:
        log.error("addAdditiveScaleToSegmentCurveSetup >> '%s' lacks driven joints"%mi_segmentCurve.getShortName())
        raise StandardError,error

    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()

    #moduleInstance
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
    except:i_module = False

    #Split it out ------------------------------------------------------------------
    ml_startBlendJoints = ml_drivenJoints[:-1]
    ml_endBlendJoints = ml_drivenJoints[1:]
    ml_endBlendJoints.reverse()#Reverse it
    ml_midBlendJoints = ml_drivenJoints[1:-1]
    log.debug("startBlendJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_startBlendJoints])
    log.debug("endBlendJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_endBlendJoints]) 

    #=====================================================================================================
    #Declare our attrs
    mPlug_in_startUp = cgmMeta.cgmAttr(mi_segmentCurve.mNode,"scaleStartUp",attrType = 'float',lock=False,keyable=True,hidden=False)
    mPlug_in_startOut = cgmMeta.cgmAttr(mi_segmentCurve.mNode,"scaleStartOut",attrType = 'float',lock=False,keyable=True,hidden=False)               
    mPlug_in_endUp = cgmMeta.cgmAttr(mi_segmentCurve.mNode,"scaleEndUp",attrType = 'float',lock=False,keyable=True,hidden=False)
    mPlug_in_endOut = cgmMeta.cgmAttr(mi_segmentCurve.mNode,"scaleEndOut",attrType = 'float',lock=False,keyable=True,hidden=False)               
    mPlug_in_midUp = cgmMeta.cgmAttr(mi_segmentCurve.mNode,"scaleMidUp",attrType = 'float',lock=False,keyable=True,hidden=False)
    mPlug_in_midOut = cgmMeta.cgmAttr(mi_segmentCurve.mNode,"scaleMidOut",attrType = 'float',lock=False,keyable=True,hidden=False)               

    #>> Let's do the blend ===============================================================
    #Get our factors ------------------------------------------------------------------
    fl_factor = 1.0/len(ml_startBlendJoints)
    log.debug("factor: %s"%fl_factor)
    dPlugs_startUps = {}
    dPlugs_startOuts = {}
    dPlugs_endUps = {}
    dPlugs_endOuts = {}
    dPlugs_midUps = {}
    dPlugs_midOuts = {}

    for i,i_jnt in enumerate(ml_startBlendJoints):#We need out factors for start and end up and outs, let's get em
        mPlug_addFactorIn = cgmMeta.cgmAttr(mi_segmentCurve,
                                            "scaleFactor_%s"%(i),attrType='float',value=(1-(fl_factor * (i))),hidden=False)	    
        mPlug_out_startFactorUp = cgmMeta.cgmAttr(mi_segmentCurve,
                                                  "out_addStartUpScaleFactor_%s"%(i),attrType='float',lock=True)
        mPlug_out_startFactorOut = cgmMeta.cgmAttr(mi_segmentCurve,
                                                   "out_addStartOutScaleFactor_%s"%(i),attrType='float',lock=True)

        mPlug_out_endFactorUp = cgmMeta.cgmAttr(mi_segmentCurve,
                                                "out_addEndUpScaleFactor_%s"%(i),attrType='float',lock=True)		
        mPlug_out_endFactorOut = cgmMeta.cgmAttr(mi_segmentCurve,
                                                 "out_addEndOutScaleFactor_%s"%(i),attrType='float',lock=True)

        startUpArg = "%s = %s * %s"%(mPlug_out_startFactorUp.p_combinedShortName,
                                     mPlug_in_startUp.p_combinedShortName,
                                     mPlug_addFactorIn.p_combinedShortName )
        startOutArg = "%s = %s * %s"%(mPlug_out_startFactorOut.p_combinedShortName,
                                      mPlug_in_startOut.p_combinedShortName,
                                      mPlug_addFactorIn.p_combinedShortName )
        endUpArg = "%s = %s * %s"%(mPlug_out_endFactorUp.p_combinedShortName,
                                   mPlug_in_endUp.p_combinedShortName,
                                   mPlug_addFactorIn.p_combinedShortName )
        endOutArg = "%s = %s * %s"%(mPlug_out_endFactorOut.p_combinedShortName,
                                    mPlug_in_endOut.p_combinedShortName, mPlug_addFactorIn.p_combinedShortName )

        for arg in [startUpArg,startOutArg,endUpArg,endOutArg]:
            log.debug("arg %s: %s"%(i,arg))
            NodeF.argsToNodes(arg).doBuild()

        #Store indexed to 
        dPlugs_startUps[i] = mPlug_out_startFactorUp
        dPlugs_startOuts[i] = mPlug_out_startFactorOut
        dPlugs_endUps[i] = mPlug_out_endFactorUp
        dPlugs_endOuts[i] = mPlug_out_endFactorOut

    #Mid factors ---------------------------------------------------------------------------
    int_mid = int(len(ml_drivenJoints)/2)
    ml_beforeJoints = ml_drivenJoints[1:int_mid]
    ml_beforeJoints.reverse()
    ml_afterJoints = ml_drivenJoints[int_mid+1:-1]
    maxInt = (max([len(ml_beforeJoints),len(ml_afterJoints)])) +1#This is our max blend factors we need    
    log.debug("beforeJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_beforeJoints])
    log.debug("afterJoints: %s"%[i_jnt.getShortName() for i_jnt in ml_afterJoints]) 

    for i in range(maxInt):
        mPlug_addFactorIn = cgmMeta.cgmAttr(mi_segmentCurve,"midFactor_%s"%(i),attrType='float',hidden=False)	    
        mPlug_out_midFactorUp = cgmMeta.cgmAttr(mi_segmentCurve,"out_addMidUpScaleFactor_%s"%(i),attrType='float',lock=True)		
        mPlug_out_midFactorOut = cgmMeta.cgmAttr(mi_segmentCurve,"out_addMidOutScaleFactor_%s"%(i),attrType='float',lock=True)	

        midUpArg = "%s = %s * %s"%(mPlug_out_midFactorUp.p_combinedShortName, mPlug_in_midUp.p_combinedShortName, mPlug_addFactorIn.p_combinedShortName )
        midOutArg = "%s = %s * %s"%(mPlug_out_midFactorOut.p_combinedShortName, mPlug_in_midOut.p_combinedShortName, mPlug_addFactorIn.p_combinedShortName )
        for arg in [midUpArg,midOutArg]:
            log.debug("mid arg %s: %s"%(i,arg))
            NodeF.argsToNodes(arg).doBuild()

        dPlugs_midUps[i] = mPlug_out_midFactorUp
        dPlugs_midOuts[i] = mPlug_out_midFactorOut	

    #Now we need to build our drivens for each joint ----------------------------------------------------------------------
    d_jointDrivers = {}
    for i_jnt in ml_drivenJoints:
        #Break our current plugs
        log.debug("driven: {0}".format(i_jnt.mNode))
        outScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%outChannel)
        upScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%upChannel)	
        d_jointDrivers[i_jnt] = {'up':[upScalePlug],'out':[outScalePlug]}#build a dict of lists for each joint indexed to joint instance
        log.debug(d_jointDrivers[i_jnt])
    #Because the last joint uses the joint before it's scale, we want the raw scale not the additive scale (the mdNode is what we want), so we need to grab that
    #d_jointDrivers[ml_drivenJoints[-1]] = {'up':[upScalePlug],'out':[outScalePlug]}
    #log.debug("startUps: %s"%[dPlugs_startUps[k].p_combinedShortName for k in dPlugs_startUps.keys()])
    #log.debug("endUps: %s"%[dPlugs_endUps[k].p_combinedShortName for k in dPlugs_endUps.keys()])

    #build a dict of lists for each joint indexed to joint instance
    for i,i_jnt in enumerate(ml_startBlendJoints):#start blends
        log.debug("startBlend %s | %s | ups: %s | outs: %s"%(i,i_jnt.getShortName(),dPlugs_startUps[i].p_combinedShortName,dPlugs_startOuts[i].p_combinedShortName))
        d_jointDrivers[i_jnt]['up'].append(dPlugs_startUps[i].p_combinedShortName)
        d_jointDrivers[i_jnt]['out'].append(dPlugs_startOuts[i].p_combinedShortName)

    for i,i_jnt in enumerate(ml_endBlendJoints):#end blends
        log.debug("endBlend %s | %s | ups: %s | outs: %s"%(i,i_jnt.getShortName(),dPlugs_endUps[i].p_combinedShortName,dPlugs_endOuts[i].p_combinedShortName))
        d_jointDrivers[i_jnt]['up'].append(dPlugs_endUps[i].p_combinedShortName)
        d_jointDrivers[i_jnt]['out'].append(dPlugs_endOuts[i].p_combinedShortName)    

    for i,i_jnt in enumerate(ml_beforeJoints):#before blends
        d_jointDrivers[i_jnt]['up'].append(dPlugs_midUps[i+1].p_combinedShortName)
        d_jointDrivers[i_jnt]['out'].append(dPlugs_midOuts[i+1].p_combinedShortName)

    for i,i_jnt in enumerate(ml_afterJoints):#after blends
        d_jointDrivers[i_jnt]['up'].append(dPlugs_midUps[i+1].p_combinedShortName)
        d_jointDrivers[i_jnt]['out'].append(dPlugs_midOuts[i+1].p_combinedShortName)

    mi_midJoint = ml_drivenJoints[int_mid]
    d_jointDrivers[mi_midJoint]['up'].append(dPlugs_midUps[0].p_combinedShortName)
    d_jointDrivers[mi_midJoint]['out'].append(dPlugs_midOuts[0].p_combinedShortName)    

    log.debug("last - %s | %s"%(ml_drivenJoints[-1].getShortName(),d_jointDrivers[ml_drivenJoints[-1]]))

    for i_jnt in d_jointDrivers.keys():#Build our 
        log.debug("%s driven >> up: %s | out: %s"%(i_jnt.getShortName(),[plug for plug in d_jointDrivers[i_jnt]['up']],[plug for plug in d_jointDrivers[i_jnt]['out']]))
        arg_up = "%s.scale%s = %s"%(i_jnt.mNode,upChannel,' + '.join(d_jointDrivers[i_jnt]['up']))
        arg_out = "%s.scale%s = %s"%(i_jnt.mNode,outChannel,' + '.join(d_jointDrivers[i_jnt]['out']))
        log.debug("arg_up: %s"%arg_up)
        log.debug("arg_out: %s"%arg_out)
        for arg in [arg_up,arg_out]:
            NodeF.argsToNodes(arg).doBuild()

    return {"mi_plug_startUp":mPlug_in_startUp,"mi_plug_startOut":mPlug_in_startOut,
            "plug_startUp":mPlug_in_startUp.p_combinedName,"plug_startOut":mPlug_in_startOut.p_combinedName,
            "mi_plug_endUp":mPlug_in_endUp,"mi_plug_endOut":mPlug_in_endOut,
            "plug_endUp":mPlug_in_endUp.p_combinedName,"plug_endOut":mPlug_in_endOut.p_combinedName,            
            "mi_plug_midUp":mPlug_in_midUp,"mi_plug_midOut":mPlug_in_midOut,
            "plug_midUp":mPlug_in_midUp.p_combinedName,"plug_midOut":mPlug_in_midOut.p_combinedName}



def addSquashAndStretchToControlSurfaceSetup(attributeHolder,jointList,connectBy = 'scale', orientation = 'zyx', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()

    #moduleInstance
    i_rigNull = False
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
            i_rigNull = i_module.rigNull
        else:
            log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    except:pass

    #attributeHolder
    i_holder = cgmMeta.cgmNode(attributeHolder)

    #Initialize joint list
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]

    ml_scaleNodes = []
    ml_sqrtNodes = []
    ml_attrs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        #make sure attr exists
        i_attr = cgmMeta.cgmAttr(i_holder,"scaleMult_%s"%i,attrType = 'float',initialValue=1)
        outScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%outChannel)
        upScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%upChannel)
        if connectBy == 'translate':
            mainDriver = '%s.scaleResult_%s'%(i_holder.mNode,i)
        else:
            mainDriver = '%s.scale%s'%(i_jnt.mNode,aimChannel)	

        #Create the multScale
        i_mdScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_mdScale.operation = 2
        i_mdScale.doStore('cgmName',i_jnt)
        i_mdScale.addAttr('cgmTypeModifier','multScale')
        i_mdScale.doName()
        for channel in [outChannel,upChannel]:
            attributes.doConnectAttr(mainDriver,#>>
                                     '%s.input1%s'%(i_mdScale.mNode,channel))
            attributes.doConnectAttr('%s'%(outScalePlug),#>>
                                     '%s.input2%s'%(i_mdScale.mNode,channel))
        #attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>

        #Create the sqrtNode
        i_sqrtScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_sqrtScale.operation = 3#set to power
        i_sqrtScale.doStore('cgmName',i_jnt)
        i_sqrtScale.addAttr('cgmTypeModifier','sqrtScale')
        i_sqrtScale.doName()
        for channel in [outChannel,upChannel]:
            attributes.doConnectAttr('%s.output%s'%(i_mdScale.mNode,channel),#>>
                                     '%s.input1%s'%(i_sqrtScale.mNode,channel))
            mc.setAttr("%s.input2"%(i_sqrtScale.mNode)+channel,.5)

        #Create the invScale
        i_invScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_invScale.operation = 2
        i_invScale.doStore('cgmName',i_jnt)
        i_invScale.addAttr('cgmTypeModifier','invScale')
        i_invScale.doName()
        for channel in [outChannel,upChannel]:
            mc.setAttr("%s.input1"%(i_invScale.mNode)+channel,1)	    
            attributes.doConnectAttr('%s.output%s'%(i_sqrtScale.mNode,channel),#>>
                                     '%s.input2%s'%(i_invScale.mNode,channel))

        #Create the powScale
        i_powScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_powScale.operation = 3
        i_powScale.doStore('cgmName',i_jnt)
        i_powScale.addAttr('cgmTypeModifier','powScale')
        i_powScale.doName()
        for channel in [outChannel,upChannel]:
            attributes.doConnectAttr('%s.output%s'%(i_invScale.mNode,channel),#>>
                                     '%s.input1%s'%(i_powScale.mNode,channel))
            attributes.doConnectAttr('%s'%(i_attr.p_combinedName),#>>
                                     '%s.input2%s'%(i_powScale.mNode,channel))

        #Create the worldScale multiplier node
        i_worldScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_worldScale.operation = 1
        i_worldScale.doStore('cgmName',i_jnt)
        i_worldScale.addAttr('cgmTypeModifier','worldScale')
        i_worldScale.doName()
        for channel in [outChannel,upChannel]:
            mc.setAttr("%s.input1"%(i_worldScale.mNode)+channel,1)
            #Connect powScale to the worldScale
            attributes.doConnectAttr('%s.output%s'%(i_powScale.mNode,channel),#>>
                                     '%s.input1%s'%(i_worldScale.mNode,channel))
        #Connect original plugs
        attributes.doConnectAttr('%s'%(outScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,outChannel))  
        attributes.doConnectAttr('%s'%(upScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,upChannel)) 

        #Connect to joint
        attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,outChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,outChannel))  
        attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,upChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,upChannel)) 	

        ml_attrs.append(i_attr)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module and Puppet axis settings
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
def doSetAimAxis(self,i):
    """
    Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
    Then Up, and Out is last.

    """
    assert i < 6,"%i isn't a viable aim axis integer"%i

    self.optionAimAxis.set(i)
    if self.optionUpAxis.get() == self.optionAimAxis.get():
        doSetUpAxis(self,i)
    if self.optionOutAxis.get() == self.optionAimAxis.get():
        doSetOutAxis(self,i)

    return True

def doSetUpAxis(self,i):
    """
    Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
    Then Up, and Out is last.

    """        
    assert i < 6,"%i isn't a viable up axis integer"%i
    axisBuffer = range(6)
    axisBuffer.remove(self.optionAimAxis.get())

    if i != self.optionAimAxis.get():
        self.optionUpAxis.set(i)  
    else:
        self.optionUpAxis.set(axisBuffer[0]) 
        guiFactory.warning("Aim axis has '%s'. Changed up axis to '%s'. Change aim setting if you want this seeting"%(dictionary.axisDirectionsByString[self.optionAimAxis.get()],dictionary.axisDirectionsByString[self.optionUpAxis.get()]))                  
        axisBuffer.remove(axisBuffer[0])

    if self.optionOutAxis.get() in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
        for i in axisBuffer:
            if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
                doSetOutAxis(self,i)
                guiFactory.warning("Setting conflict. Changed out axis to '%s'"%dictionary.axisDirectionsByString[i])                    
                break
    return True        


def doSetOutAxis(self,i):
    assert i < 6,"%i isn't a viable aim axis integer"%i

    if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
        self.optionOutAxis.set(i)
    else:
        axisBuffer = range(6)
        axisBuffer.remove(self.optionAimAxis.get())
        axisBuffer.remove(self.optionUpAxis.get())
        self.optionOutAxis.set(axisBuffer[0]) 
        guiFactory.warning("Setting conflict. Changed out axis to '%s'"%dictionary.axisDirectionsByString[ axisBuffer[0] ])                    



def copyAxisOptions(self,target):
    target.optionAimAxis
    target.optionUpAxis
    target.optionOutAxis
    self.optionAimAxis
    self.optionUpAxis
    self.optionOutAxis 

    doSetAimAxis(self,target.optionAimAxis.get())
    doSetUpAxis(self,target.optionUpAxis.get())
    doSetOutAxis(self,target.optionOutAxis.get())



def createSegmentCurveOLDOUTSIDEMAINTRANSFORM(jointList,orientation = 'zyx',secondaryAxis = None,
                                              baseName ='test', moduleInstance = None):
    """
    """
    if type(jointList) not in [list,tuple]:jointList = [jointList]

    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]

    i_rigNull = False
    i_module = False
    try:
        if moduleInstance:
            if moduleInstance.isModule():
                i_module = moduleInstance    
                i_rigNull = i_module.rigNull
        else:
            log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
        baseName = i_module.getPartNameBase()
    except:pass

    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()

    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]#Initialize original joints

    if not moduleInstance:#if it is, we can assume it's right
        if secondaryAxis is None:
            raise StandardError,"createControlSurfaceSegment>>> Must have secondaryAxis arg if no moduleInstance is passed"
        for i_jnt in ml_jointList:
            """
	    Cannot iterate how important this step is. Lost a day trying to trouble shoot why one joint chain worked and another didn't.
	    WILL NOT connect right without this.
	    """
            joints.orientJoint(i_jnt.mNode,orientation,secondaryAxis)


    #Joints
    #=========================================================================
    #Create spline IK joints
    #>>Surface chain    
    l_splineIKJoints = mc.duplicate(jointList,po=True,ic=True,rc=True)
    ml_splineIKJoints = []
    for i,j in enumerate(l_splineIKJoints):
        i_j = cgmMeta.asMeta(j,'cgmObject',setClass=True)
        i_j.addAttr('cgmName',baseName,lock=True)
        i_j.addAttr('cgmTypeModifier','splineIK',attrType='string')
        i_j.doName()
        l_splineIKJoints[i] = i_j.mNode
        ml_splineIKJoints.append(i_j)

    #Create Curve
    i_splineSolver = cgmMeta.cgmNode(nodeType = 'ikSplineSolver')
    buffer = mc.ikHandle( sj=ml_splineIKJoints[0].mNode, ee=ml_splineIKJoints[-1].mNode,simplifyCurve=False,
                          solver = i_splineSolver.mNode, ns = 4, rootOnCurve=True,forceSolver = True,
                          createCurve = True,snapHandleFlagToggle=True )  

    i_segmentCurve = cgmMeta.cgmObject( buffer[2],setClass=True )
    i_segmentCurve.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_segmentCurve.addAttr('cgmType','splineIKCurve',attrType='string',lock=True)
    i_segmentCurve.doName()
    if i_module:#if we have a module, connect vis
        i_segmentCurve.overrideEnabled = 1             
        cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_segmentCurve.mNode,'overrideVisibility'))    
        cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_segmentCurve.mNode,'overrideDisplayType'))    

    i_ikHandle = cgmMeta.asMeta( buffer[0],'cgmObject',setClass=True )
    i_ikEffector = cgmMeta.asMeta( buffer[1],'cgmObject',setClass=True )

    #Joints
    #=========================================================================
    ml_ = []
    ml_pointOnCurveInfos = []
    ml_upGroups = []

    #First thing we're going to do is create our follicles
    shape = mc.listRelatives(i_segmentCurve.mNode,shapes=True)[0]
    for i,i_jnt in enumerate(ml_jointList):   
        l_closestInfo = distance.returnNearestPointOnCurveInfo(i_jnt.mNode,i_segmentCurve.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> """Follicle""" =======================================================
        i_closestPointNode = cgmMeta.cgmNode(nodeType = 'pointOnCurveInfo')
        mc.connectAttr ((shape+'.worldSpace'),(i_closestPointNode.mNode+'.inputCurve')) 

        #> Name
        i_closestPointNode.doStore('cgmName',i_jnt)
        i_closestPointNode.doName()
        #>Set follicle value
        i_closestPointNode.parameter = l_closestInfo['parameter']

        ml_pointOnCurveInfos.append(i_closestPointNode)

        #if i_module:#if we have a module, connect vis
            #i_follicleTrans.overrideEnabled = 1                
            #cgmMeta.cgmAttr(i_module.rigNull.mNode,'visRig',lock=False).doConnectOut("%s.%s"%(i_follicleTrans.mNode,'overrideVisibility'))


        #>>> loc
        #First part of full ribbon wist setup
        if i_jnt != ml_jointList[-1]:
            i_upLoc = i_jnt.doLoc()#Make up Loc
            i_locRotateGroup = i_jnt.doCreateAt()#group in place
            i_locRotateGroup.parent = ml_splineIKJoints[i].mNode
            i_locRotateGroup.doStore('cgmName',i_jnt)         
            i_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
            i_locRotateGroup.doName()

            #Store the rotate group to the joint
            i_jnt.connectChildNode(i_locRotateGroup,'rotateUpGroup','drivenJoint')
            i_zeroGrp = cgmMeta.asMeta( i_locRotateGroup.doGroup(True),'cgmObject',setClass=True )
            i_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
            i_zeroGrp.doName()
            #connect some other data
            i_locRotateGroup.connectChildNode(i_locRotateGroup.parent,'zeroGroup')
            i_locRotateGroup.connectChildNode(i_upLoc,'upLoc')
            mc.makeIdentity(i_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)

            i_upLoc.parent = i_locRotateGroup.mNode
            mc.move(0,10,0,i_upLoc.mNode,os=True)       
            ml_upGroups.append(i_upLoc)

            if i_module:#if we have a module, connect vis
                i_upLoc.overrideEnabled = 1             
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideDisplayType'))    


    #Orient constrain our last joint to our splineIK Joint
    mc.orientConstraint(ml_splineIKJoints[-1].mNode,ml_jointList[-1].mNode,maintainOffset = True)

    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    ml_distanceObjects = []
    ml_distanceShapes = []  
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.asMeta(ik_buffer[0],'cgmObject',setClass=True)
        i_IK_Handle.parent = ml_splineIKJoints[i+1].mNode
        i_IK_Handle.doStore('cgmName',i_jnt)    
        i_IK_Handle.doName()

        #Effector
        i_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
        #i_IK_Effector.doStore('cgmName',i_jnt)    
        i_IK_Effector.doName()

        l_iIK_handles.append(i_IK_Handle)
        l_iIK_effectors.append(i_IK_Effector)

        if i_module:#if we have a module, connect vis
            i_IK_Handle.overrideEnabled = 1             
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideDisplayType'))    

        #>> Distance nodes
        i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
        i_distanceObject.doStore('cgmName',i_jnt)
        i_distanceObject.addAttr('cgmType','measureNode',lock=True)
        i_distanceObject.doName(nameShapes = True)
        i_distanceObject.parent = i_grp.mNode#parent it
        i_distanceObject.overrideEnabled = 1
        i_distanceObject.overrideVisibility = 1

        #Connect things
        mc.connectAttr ((ml_pointOnCurveInfos[i].mNode+'.position'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_pointOnCurveInfos[i+1].mNode+'.position'),(i_distanceShape.mNode+'.endPoint'))

        ml_distanceObjects.append(i_distanceObject)
        ml_distanceShapes.append(i_distanceShape)

        if i_module:#Connect hides if we have a module instance:
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideDisplayType'))    

    #>> Second part for the full twist setup
    aimChannel = orientation[0]  
    fixOptions = [0,90,180,-90,-180]      

    for i,i_jnt in enumerate(ml_jointList[:-1]):
        rotBuffer = mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)
        log.debug("rotBuffer: %s"%rotBuffer)
        #Create the poleVector
        poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,l_iIK_handles[i].mNode)      
        optionCnt = 0
        while not cgmMath.isFloatEquivalent((mc.getAttr(i_jnt.mNode+'.r'+aimChannel)),0):
            log.debug("%s.r%s: %s"%(i_jnt.getShortName(),aimChannel,mc.getAttr(i_jnt.mNode+'.r'+aimChannel)))
            log.debug ("Trying the following for '%s':%s" %(l_iIK_handles[i].getShortName(),fixOptions[optionCnt]))
            attributes.doSetAttr(l_iIK_handles[i].mNode,'twist',fixOptions[optionCnt])
            optionCnt += 1
            if optionCnt == 4:
                raise StandardError,"failed to find a good twist value to zero out poleVector: %s"%(i_jnt.getShortName())

        if mc.xform (i_jnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
            log.debug("Found the following on '%s': %s"%(i_jnt.getShortName(),mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)))

    #>>>Hook up scales
    #==========================================================================
    #Translate scale
    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float',minValue = 0.0)        
    i_jntScaleBufferNode.doName()

    i_jntScaleBufferNode.connectParentNode(i_segmentCurve.mNode,'segmentCurve','scaleBuffer')
    ml_mainMDs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):

        #Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(ml_distanceShapes[i].distance)#Store to our buffer
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to store joint distance: %s"%ml_distanceShapes[i].mNode

        #Create the mdNode
        i_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
        i_md.operation = 2
        i_md.doStore('cgmName',i_jnt)
        i_md.addAttr('cgmTypeModifier','masterScale')
        i_md.doName()
        attributes.doConnectAttr('%s.%s'%(ml_distanceShapes[i].mNode,'distance'),#>>
                                 '%s.%s'%(i_md.mNode,'input1X'))
        attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
                                 '%s.%s'%(i_md.mNode,'input2X'))

        #Connect to the joint
        i_attr = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"distance_%s"%i,attrType = 'float',initialValue=0,lock=True)                
        i_attrResult = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True)       
        try:
            i_attr.doConnectIn('%s.%s'%(ml_distanceShapes[i].mNode,'distance'))
            i_attrResult.doConnectIn('%s.%s'%(i_md.mNode,'output.outputX'))
            i_attrResult.doConnectOut('%s.s%s'%(i_jnt.mNode,orientation[0]))

            for axis in orientation[1:]:
                attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,'masterScale'),#>>
                                         '%s.s%s'%(i_jnt.mNode,axis))       
        except Exception,error:
            log.error(error)
            raise StandardError,"Failed to connect joint attrs: %s"%i_jnt.mNode

        ml_mainMDs.append(i_md)#store the md
        for axis in ['scaleX','scaleY','scaleZ']:
            attributes.doConnectAttr('%s.%s'%(i_jnt.mNode,axis),#>>
                                     '%s.%s'%(ml_splineIKJoints[i].mNode,axis))         


    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
        attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))  

    mc.pointConstraint(ml_splineIKJoints[0].mNode,ml_jointList[0].mNode,maintainOffset = False)

    #Store info to the segment curve

    #>>> Store em all to our instance
    i_segmentCurve.connectChildNode(i_jntScaleBufferNode,'scaleBuffer','segmentCurve')
    i_segmentCurve.msgList_connect('bindJoints',ml_jointList,'segmentCurve')       
    i_segmentCurve.msgList_connect('splineIKJoints',ml_splineIKJoints,'segmentCurve')   

    return {'mi_segmentCurve':i_segmentCurve,'segmentCurve':i_segmentCurve.mNode,
            'l_splineIKJoints':[i_jnt.getShortName() for i_jnt in ml_splineIKJoints],'ml_splineIKJoints':ml_splineIKJoints,
            'scaleBuffer':i_jntScaleBufferNode.mNode,'mi_scaleBuffer':i_jntScaleBufferNode,
            'l_joints':jointList,'ml_joints':ml_jointList}