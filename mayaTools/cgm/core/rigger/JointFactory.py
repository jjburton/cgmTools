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
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.rigger.lib import joint_Utils as jntUtils
from cgm.core.lib import rayCaster as rayCast
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.classes import GuiFactory as gui
from cgm.core.classes import SnapFactory as Snap
from cgm.core.rigger.lib import module_Utils as modUtils
import cgm.core.lib.snap_utils as SNAP
from cgm.lib import (cgmMath,
                     joints,
                     rigging,
                     attributes,
                     locators,
                     distance,
                     search,
                     curves,
                     dictionary,
                     lists,
                     settings,
                     modules)

from cgm.core.lib import nameTools

#>>> Register rig functions
#=====================================================================
from cgm.core.rigger.lib.Limb import (spine,neckHead,leg,clavicle,arm,finger,thumb)
from cgm.core.rigger.lib.Face import (eyeball,eyelids,eyebrow,mouthNose)
d_moduleTypeToBuildModule = {'torso':spine,
                             'neckhead':neckHead,
                             'leg':leg,
                             'arm':arm,
                             'clavicle':clavicle,
                             'thumb':thumb,
                             'finger':finger,
                             'eyeball':eyeball,
                             'eyelids':eyelids,
                             'eyebrow':eyebrow,
                             'mouthnose':mouthNose,
                             } 
for module in d_moduleTypeToBuildModule.keys():
    try:reload(d_moduleTypeToBuildModule[module])
    except Exception,err:raise Exception,"Failed to reload: {0} | {1}".format(module,err)

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def go(*args, **kws):
    """
    Customization template builder from template file for setting up a cgmMorpheusMakerNetwork

    :parameters:
    0 - 'customizationNode'(morpheusCustomizationAsset - None) | Morpheus system biped customization asset

    :returns:
        Nothing

    :raises:
    Exception | if reached

    """       
    class fncWrap(cgmGeneral.cgmFuncCls):		
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'go'	
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._cgmClass = 'JointFactory.go'
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'mModule',"default":None,"argType":'cgmModule','help':"This must be a cgm module"},
                                         {'kw':'forceNew',"default":True,"argType":'bool','help':"Whether to force a new one"},
                                         {'kw':'saveTemplatePose',"default":True,"argType":'bool','help':"Whether to attempt to load a tempate pose or now"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            self.l_funcSteps = [{'step':'Initial Validation','call':self._step_validate_},
                                {'step':'Need Building?','call':self._step_buildNeed_},
                                {'step':'Data Bind','call':self._step_jointDataBind_},	                        
                                {'step':'Main process','call':self._step_jointProcess_},
                                #{'step':'Tag Children','call':self._step_tagChildren_},	                        	                        
                                ]

        def _step_validate_(self):
            assert self.d_kws['mModule'].isModule(),"Not a module"
            assert self.d_kws['mModule'].isTemplated(),"Not Templated"
            self._mi_module = self.d_kws['mModule']# Link for shortness
            self._str_reportStart = "{0}('{1}')".format(self._str_reportStart,self._mi_module.p_nameShort)
            self.cls = "JointFactory.go"
            self._cgmClass = "JointFactory.go"
            
            try:#>>> Instances and joint stuff ----------------------------------------------------
                self._mi_orientation = cgmValid.simpleOrientation(str(modules.returnSettingsData('jointOrientation')) or 'zyx')
                self._jointOrientation = self._mi_orientation.p_string  
            except Exception,error:raise Exception,"Vectors | error: {0}".format(error)            

        def _step_buildNeed_(self):
            mi_module = self._mi_module
            self._strShortName = self._mi_module.getShortName() or False     

            #>>> store template settings
            if self.d_kws['saveTemplatePose'] and not self._mi_module.getMessage('helper'):
                self.log_debug("Saving template pose..")
                self._mi_module.templateSettings_call('store')

            if self._mi_module.isSkeletonized():
                if self.d_kws['forceNew']:
                    self._mi_module.skeletonDelete()
                else:
                    self.log_info("'{0}' has already been Skeletonized. Done.".format(self._strShortName))
                    return self._SuccessReturn_()

        def _step_jointDataBind_(self):
            self.rigNull = self._mi_module.getMessage('rigNull')[0] or False
            self._mi_rigNull = self._mi_module.rigNull
            self._mi_puppet = self._mi_module.modulePuppet	
            self.moduleColors = self._mi_module.getModuleColors()

            self.foundDirections = False #Placeholder to see if we have it

            #>>> part name 
            self._partName = self._mi_module.getPartNameBase()
            self._partType = self._mi_module.moduleType.lower() or False

            self.direction = None
            if self._mi_module.hasAttr('cgmDirection'):
                self.direction = self._mi_module.cgmDirection or None

            #>>> template null 
            self._mi_templateNull = self._mi_module.templateNull

            #>>> Gather info
            #=========================================================	
            self._l_coreNames = self._mi_module.coreNames.value  
            self.str_jointOrientation = modules.returnSettingsData('jointOrientation')
            self._d_handleToHandleJoints = {}

            if not hasJointSetup(self):
                raise StandardError, "Need to add to build dict"

        def _step_jointProcess_(self):
            if self._mi_module.mClass == 'cgmLimb':
                self.curveDegree = self._mi_templateNull.curveDegree	
                self._mi_root = self._mi_templateNull.root
                self._mi_orientRootHelper = self._mi_templateNull.orientRootHelper
                self._mi_curve = self._mi_templateNull.curve
                self._ml_controlObjects = self._mi_templateNull.msgList_get('controlObjects')

                self.log_debug("mode: cgmLimb Skeletonize")
                build_limbSkeleton(self)

                try:self.modSpecificBuild(self)#...this is post stuff
                except Exception,error:raise Exception,"Post stuff fail | {0}".format(error)

                #Only going to tag our handleJoints at the very end because of message connection duplication

                try:
                    for mObj in self._ml_controlObjects:
                        mObj.connectChildNode(self.ml_moduleJoints[self._d_handleToHandleJoints[mObj]],'handleJoint')	
                except Exception,error:self.log_error("Tagging fail | error: {0}".format(error)) 

            elif self._mi_module.mClass == 'cgmEyeball':
                log.info(">>> %s.go >> eyeball mode!"%(self._mi_module.p_nameShort))
                try:doSkeletonizeEyeball(self)
                except Exception,error:log.warning(">>> %s.go >> build failed: %s"%(self._mi_module.p_nameShort,error)) 
            elif self._mi_module.mClass == 'cgmEyelids':
                log.info(">>> %s.go >> eyelids mode!"%(self._mi_module.p_nameShort))
                try:doSkeletonizeEyelids(self)
                except Exception,error:log.warning(">>> %s.go >> build failed: %s"%(self._mi_module.p_nameShort,error)) 
            elif self._mi_module.mClass == 'cgmEyebrow':
                log.info(">>> %s.go >> eyebrow mode!"%(self._mi_module.p_nameShort))
                doSkeletonizeEyebrow(self)
            elif self._mi_module.mClass == 'cgmMouthNose':
                log.info(">>> %s.go >> mouthNose mode!"%(self._mi_module.p_nameShort))
                try:doSkeletonizeMouthNose(self)
                except Exception,error:log.warning(">>> %s.go >> build failed: %s"%(self._mi_module.p_nameShort,error)) 	    
            else:
                raise NotImplementedError,"haven't implemented '{0}' skeletonizing yet yet".format(self._mi_module.mClass)


        def _step_tagChildren_(self):
            doTagChildren(self._mi_module)

        def _step_poseLoad_(self):
            #>>> store template settings
            self._mi_module.templateSettings_call('load')	



            """
            self._mi_templateNull.overrideEnabled = 1		
            cgmMeta.cgmAttr(self._mi_masterSettings.mNode,'templateVis',lock=False).doConnectOut("%s.%s"%(self._mi_templateNull.mNode,'overrideVisibility'))
            cgmMeta.cgmAttr(self._mi_masterSettings.mNode,'templateLock',lock=False).doConnectOut("%s.%s"%(self._mi_templateNull.mNode,'overrideDisplayType'))    
            """
    return fncWrap(*args, **kws).go()

class JointFactoryFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """
        try:
            try:goInstance = args[0]
            except:goInstance = kws['goInstance']
            if not goInstance._cgmClass == "JointFactory.go":
                raise StandardError,"Not a JointFactory.go instance: '%s'"%goInstance
            assert mc.objExists(goInstance._mi_module.mNode),"Module no longer exists"
        except Exception,error:
            if args:self.log_info("args: {0}".format(args))
            if kws:self.log_info("kws: {0}".format(kws))            
            raise Exception,("JointFactoryFunc fail: {0}".format(error))

        super(JointFactoryFunc, self).__init__(*args,**kws)

        self._str_funcName = 'JointFactoryFunc(%s)'%goInstance._mi_module.p_nameShort
        self._l_ARGS_KWS_DEFAULTS = [{'kw':'goInstance',"default":goInstance}]

        self.__dataBind__(**kws)
        self.mi_go = goInstance
        self.mi_module = goInstance._mi_module

        #=================================================================

def hasJointSetup(self):
    try:
        log.debug(">>> %s.hasJointSetup >> "%(self._strShortName) + "="*75)      

        if self._partType not in d_moduleTypeToBuildModule.keys():
            self.log_error("%s.hasJointSetup>>> '%s' Not in d_moduleTypeToBuildModule"%(self._strShortName,self._partType))	
            return False

        try:#Version
            self._buildVersion = d_moduleTypeToBuildModule[self._partType].__version__    
        except:
            self.log_error("%s.hasJointSetup>>> Missing version"%(self._strShortName))	
            return False

        try:#Joints list
            self.modSpecificBuild = d_moduleTypeToBuildModule[self._partType].__bindSkeletonSetup__
            self.modSpecificBuildModule = d_moduleTypeToBuildModule[self._partType]
        except:
            self.log_error("%s.hasJointSetup>>> Missing Joint Setup Function"%(self._strShortName))	
            return False	

        return True  
    except Exception,error:
        raise Exception,"hasJointSetup fail | error: {0}".format(error)

def doSkeletonizeEyeball(self):
    """     
    """
    #>>> Get our base info =========================================================================
    _str_funcName = "doSkeletonizeEyeball(%s)"%self._mi_module.p_nameShort  
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)   

    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self._mi_module.mNode),"Module no longer exists"
    assert self._mi_module.mClass == 'cgmEyeball',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(_str_funcName,self._mi_module.mClass)
    ml_moduleJoints = []
    ml_buildObjects = []
    _str_orientation = self.str_jointOrientation #Link

    #>>> Build ====================================================================================
    #Find our helper
    mi_helper = cgmMeta.validateObjArg(self._mi_module.getMessage('helper'),noneValid=True)
    if not mi_helper:raise StandardError,"%s >>> No suitable helper found"%(_str_funcName)

    #See if we need to mirror the shapes stuff
    mi_helperMirror = False

    ml_buildObjects.append(mi_helper)
    log.info("%s >>> helper: '%s'"%(_str_funcName,mi_helper.p_nameShort))

    #Pupil and Iris
    if mi_helper.buildPupil:
        try:ml_buildObjects.append(mi_helper.pupilHelper)
        except Exception,error:raise StandardError,"%s >>> Missing Iris helper | error: %s "%(_str_funcName,error)
    if mi_helper.buildIris:
        try:ml_buildObjects.append(mi_helper.irisHelper)
        except Exception,error:raise StandardError,"%s >>> Missing Iris helper | error: %s "%(_str_funcName,error)

    log.info("%s >>> buildObjects: %s"%(_str_funcName,[o.p_nameShort for o in ml_buildObjects]))
    str_partName = self._partName

    #Joint build
    l_initialJoints = []
    for o in ml_buildObjects:
        l_initialJoints.append( mc.joint(p = o.getPosition()) )

    #Parent, tag
    for i,j in enumerate(l_initialJoints):
        i_j = cgmMeta.asMeta(j,'cgmObject',setClass = True)
        i_j.doCopyNameTagsFromObject( ml_buildObjects[i].mNode,ignore=['cgmTypeModifier','cgmType'] )#copy Tags
        i_j.parent = False
        ml_moduleJoints.append(i_j)
        self._mi_rigNull.connectChildNode(i_j,'%sJoint'%i_j.cgmName)

    #>>> Orient -------------------------------------------------------------
    #Make our up loc
    try:
        _str_upLoc = locators.locMeCvFromCvIndex(mi_helper.getShapes()[0],2)   
        mi_upLoc = cgmMeta.asMeta(_str_upLoc,'cgmObject')
        mi_aimLoc = mi_helper.pupilHelper.doLoc(fastMode = True)
        v_aim = cgmValid.simpleAxis(_str_orientation[0]).p_vector
        v_up = cgmValid.simpleAxis(_str_orientation[1]).p_vector

        constraintBuffer = mc.aimConstraint(mi_aimLoc.mNode,ml_moduleJoints[0].mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
        mc.delete(constraintBuffer[0])    
        for o in [mi_aimLoc,mi_upLoc]:
            o.delete()    
        #Copy eyeball orient to children
        if len(ml_moduleJoints)>1:
            for o in ml_moduleJoints[1:]:
                o.parent = ml_moduleJoints[0]#Parent back
            joints.doCopyJointOrient(ml_moduleJoints[0].mNode,[jnt.mNode for jnt in ml_moduleJoints[1:]])

        try:#Create eye orb joint
            i_dupJnt = ml_moduleJoints[0].doDuplicate(parentOnly = True)#Duplicate
            i_dupJnt.addAttr('cgmName','eyeOrb')#Tag
            ml_moduleJoints[0].parent = i_dupJnt#Parent
            ml_moduleJoints.insert(0,i_dupJnt)
        except:
            raise StandardError, "eye orb fail! | %s"%(_str_funcName,error)

        #Connect back
        self._mi_rigNull.msgList_connect('moduleJoints',ml_moduleJoints,'rigNull')
        log.info("%s >>> built the following joints: %s"%(_str_funcName,[o.p_nameShort for o in ml_moduleJoints]))
    except Exception,error:
        raise StandardError, "%s >>> Orient fail | Error: %s"%(_str_funcName,error)

    #>>> Flag our handle joints
    #===========================
    try:
        for mJnt in ml_moduleJoints:
            mJnt.doName()
        self._mi_rigNull.msgList_connect('handleJoints',ml_moduleJoints) 
        self._mi_rigNull.msgList_connect('skinJoints',ml_moduleJoints) 
    except Exception,error:
        raise StandardError, "%s >>> Skin/Handle connect fail | Error: %s"%(_str_funcName,error)

    #Connect to parent =========================================================
    try:
        if self._mi_module.getMessage('moduleParent'):#If we have a moduleParent, constrain it
            connectToParentModule(self._mi_module)    
    except Exception,error:
        raise StandardError, "%s >>> Failed parent connect | Error: %s"%(_str_funcName,error)

    return True

def doSkeletonizeEyelids(self):
    """     
    """
    #>>> Get our base info =========================================================================
    _str_funcName = "doSkeletonizeEyelids(%s)"%self._mi_module.p_nameShort  
    log.info(">>> %s "%(_str_funcName) + "="*75)   
    assert self.cls == 'JointFactory.go',"Not a JointFactory.go instance!"
    assert mc.objExists(self._mi_module.mNode),"Module no longer exists"
    assert self._mi_module.mClass == 'cgmEyelids',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(_str_funcName,self._mi_module.mClass)
    ml_moduleJoints = []
    _str_orientation = self.str_jointOrientation #Link
    try:#>>> Get info ====================================================================================
        #Find our helper
        mi_helper = cgmMeta.validateObjArg(self._mi_module.getMessage('helper'),noneValid=True)
        if not mi_helper:raise StandardError,"%s >>> No suitable helper found"%(_str_funcName)
        if not mi_helper.buildLids:
            raise StandardError,"%s >>> %s.buildLids is off "%(_str_funcName,mi_helper.p_nameShort)

        try:mi_uprLidBase = cgmMeta.validateObjArg(mi_helper.getMessage('uprLidHelper'),noneValid=False)
        except Exception,error:raise StandardError,"%s >>> Missing uprlid helper | error: %s "%(_str_funcName,error)
        try:mi_lwrLidBase = cgmMeta.validateObjArg(mi_helper.getMessage('lwrLidHelper'),noneValid=False)
        except Exception,error:raise StandardError,"%s >>> Missing uprlid helper | error: %s "%(_str_funcName,error)
        try:int_lwrLidJoints = mi_helper.getMayaAttr('lwrLidJoints')
        except Exception,error:raise StandardError,"%s >>> Missing lwrLid joint count | error: %s "%(_str_funcName,error)
        try:int_uprLidJoints = mi_helper.getMayaAttr('uprLidJoints')
        except Exception,error:raise StandardError,"%s >>> Missing uprLid joint count | error: %s "%(_str_funcName,error)       
        log.info("%s >>> helper: '%s'"%(_str_funcName,mi_helper.p_nameShort))
        log.info("%s >>> mi_uprLidBase: '%s'"%(_str_funcName,mi_uprLidBase.p_nameShort))
        log.info("%s >>> mi_lwrLidBase: '%s'"%(_str_funcName,mi_lwrLidBase.p_nameShort))
        log.info("%s >>> uprCount : %s"%(_str_funcName,int_uprLidJoints))
        log.info("%s >>> lwrCount : %s"%(_str_funcName,int_lwrLidJoints))

        #Curves --------------------------------------------------------------------------------
        str_partName = self._partName	
        d_buildCurves = {'upr':{'crv':mi_uprLidBase,'count':int_uprLidJoints,'ml_joints':[]},
                         'lwr':{'crv':mi_lwrLidBase,'count':int_lwrLidJoints,'ml_joints':[]}}

        #Orient info ------------------------------------------------------------------------------------------------
        v_aimNegative = cgmValid.simpleAxis(_str_orientation[0]+"-").p_vector
        v_aim = cgmValid.simpleAxis(_str_orientation[0]).p_vector	
        v_up = cgmValid.simpleAxis(_str_orientation[1]).p_vector	
        v_upNegative = cgmValid.simpleAxis(_str_orientation[1]+"-").p_vector	
        v_out = cgmValid.simpleAxis(_str_orientation[2]).p_vector	
        v_outNegative = cgmValid.simpleAxis(_str_orientation[2]+"-").p_vector	

        #Orient info
        _str_upLoc = locators.locMeCvFromCvIndex(mi_helper.getShapes()[0],2)   
        mi_upLoc = cgmMeta.asMeta(_str_upLoc,'cgmObject')	

    except Exception,error:
        raise StandardError,"Data gather fail! | error: %s "%(error)       

    try:
        for k in d_buildCurves.keys():
            mi_crv = d_buildCurves[k].get('crv')#get instance
            int_count = d_buildCurves[k].get('count')#get int
            log.info("%s >>> building joints for %s curve | count: %s"%(_str_funcName,k, int_count))
            try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)#startSplitFactor=.05
            except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(_str_funcName,error)       
            d_buildCurves[k]['l_pos'] = l_pos#Store it
            log.info("%s >>> '%s' pos list: %s"%(_str_funcName,k, l_pos))
            l_jointBuffer = []
            ml_jointBuffer = d_buildCurves[k].get('ml_joints')
            ml_endJoints = []
            if k == 'lwr':l_pos = l_pos[1:-1]
            int_last = len(l_pos)
            for i,pos in enumerate(l_pos):
                try:#Create and name
                    mc.select(cl=True)
                    mi_end = cgmMeta.asMeta(mc.joint(p = pos),'cgmObject',setClass = True)
                    mi_end.parent = False
                    ml_buffer = [mi_end]
                    mi_end.doCopyNameTagsFromObject( self._mi_module.mNode,ignore=['cgmTypeModifier','cgmType'] )#copy Tags
                    mi_end.addAttr('cgmName',"%sLid"%(k),lock=True)		    
                    mi_end.addAttr('cgmIterator',i,lock=True,hidden=True)
                    #mi_end.addAttr('cgmNameModifier','inner',lock=True)	
                    #if i == int_last:mi_end.addAttr('cgmNameModifier','outer',lock=True)			
                    mi_end.doName()
                    l_jointBuffer.append(mi_end)
                    ml_moduleJoints.append(mi_end)
                    ml_endJoints.append(mi_end)
                    ml_jointBuffer.append(mi_end)
                    log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(_str_funcName,k,i,[o.p_nameShort for o in ml_buffer]))
                except Exception,error:
                    raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error) 
            #d_buildCurves[k]['nestedml_joints'] = l_jointBuffer #nested list
            d_buildCurves[k]['ml_endJoints'] = ml_endJoints #nested list
            self._mi_rigNull.msgList_connect('moduleJoints_%s'%k,ml_endJoints,'rigNull')  		
    except Exception,error:
        raise StandardError,"[{0} build] | error: {1} ".format(_str_funcName,error)  
    try:
        for k in d_buildCurves.keys():
            ml_jointBuffer = d_buildCurves[k].get('ml_joints')#link our list to pull from

            for i,mJnt in enumerate(ml_jointBuffer):
                try:#aim constraint
                    #mi_upLoc = cgmMeta.cgmObject('l_eye_move_jnt_loc')
                    passKWS = {'weight' : 1, 'aimVector' : v_aimNegative, 'upVector' : v_up, 'worldUpVector' : [0,1,0],
                               'worldUpObject' : mi_upLoc.mNode, 'worldUpType' : 'object'} 	               
                    mi_target = mi_helper
                    
                    """passKWS = {'weight' : 1, 'upVector' : v_aimNegative, 'worldUpVector' : [0,1,0],
                               'worldUpObject' : mi_helper.mNode, 'worldUpType' : 'object'} 	
                    if self._mi_module.cgmDirection == 'left':
                        passKWS['aimVector'] = v_outNegative
                    else:
                        passKWS['aimVector'] = v_out

                    if k == 'upr':
                        if mJnt in [ml_jointBuffer[0],ml_jointBuffer[-1]]:
                            mi_target = mi_helper
                            passKWS = {'weight' : 1, 'aimVector' : v_aimNegative, 'upVector' : v_up, 'worldUpVector' : [0,1,0],
                                       'worldUpObject' : mi_upLoc.mNode, 'worldUpType' : 'object'} 			    
                        else:
                            mi_target = ml_jointBuffer[i-1]
                    else:
                        if i == 0:
                            mi_target = d_buildCurves['upr']['ml_joints'][0]
                        else:
                            mi_target = ml_jointBuffer[i-1]"""
                    
                    #SNAP.aim(mJnt.mNode,mi_helper.mNode,v_aimNegative,v_up,'vector',[0,1,0])
                    #constraintBuffer = mc.aimConstraint(mi_target.mNode,mJnt.mNode,maintainOffset = False, **passKWS)
                    #mc.delete(constraintBuffer)  			    
                    #mi_end.parent = mi_root
                except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
                try:#copy orient
                    pass
                    #joints.doCopyJointOrient(mi_root.mNode,mi_end.mNode)		
                except Exception,error:raise StandardError,"curve: %s | pos count: %s | Copy orient fail | error: %s "%(k,i,error)       		
                try:#freeze
                    jntUtils.metaFreezeJointOrientation(mJnt)
                except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
    except Exception,error:
        raise StandardError,"[{0} orient] | error: {1} ".format(_str_funcName,error) 

    for o in [mi_upLoc]:
        o.delete()      

    #>>> Connections
    #===========================
    try:
        #self._mi_rigNull.msgList_connect(ml_moduleJoints,'handleJoints') 
        self._mi_rigNull.msgList_connect('skinJoints',ml_moduleJoints) 
        self._mi_rigNull.msgList_connect('moduleJoints',ml_moduleJoints) 

    except Exception,error:
        raise StandardError, "%s >>> Skin/Handle connect fail | Error: %s"%(_str_funcName,error)

    #Connect to parent =========================================================
    try:
        if self._mi_module.getMessage('moduleParent'):#If we have a moduleParent, constrain it
            log.info("%s >>> Need to implement Module parent connect"%(_str_funcName))
            connectToParentModule(self._mi_module)    
    except Exception,error:
        raise StandardError, "%s >>> Failed parent connect | Error: %s"%(_str_funcName,error)

    return True

def doSkeletonizeEyebrow(goInstance = None):
    class fncWrap(JointFactoryFunc):
        def __init__(self,goInstance = None):
            """
            """	
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'doSkeletonizeEyebrow(%s)'%self.mi_module.p_nameShort
            self._b_autoProgressBar = True
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
                                {'step':'Build midBrow','call':self._buildMidBrow_},	                        
                                {'step':'Build brow','call':self._buildBrow_},
                                {'step':'Build Cheek','call':self._buildCheek_},
                                {'step':'Build Temple','call':self._buildTemple_},
                                {'step':'Build Squash and Stretch Cage','call':self._buildSquashStretchCage_},
                                {'step':'Connect','call':self._connect_}]

            assert self.mi_module.mClass == 'cgmEyebrow',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(_str_funcName,self.mi_module.mClass)

            #The idea is to register the functions needed to be called
            #=================================================================

        def _gatherInfo_(self): 
            self.str_orientation = self.mi_go.str_jointOrientation #Link
            self.str_partName = self.mi_go._partName	
            self.ml_moduleJoints = []
            self.md_moduleJoints = {}

            try:
                self.l_targetMesh = self.mi_go._mi_puppet.getUnifiedGeo() or self.mi_go._mi_puppet.getGeo() or 'Morphy_Body_GEO1'#>>>>>>>>>>>>>>>>>this needs better logic   
            except Exception,error:
                raise error

            #Find our head attach joint ------------------------------------------------------------------------------------------------
            self.str_rootJoint = False
            if self.mi_module.getMessage('moduleParent'):
                try:
                    mi_end = self.mi_module.moduleParent.rigNull.msgList_get('moduleJoints')[-1]
                    buffer =  mi_end.getMessage('scaleJoint')
                    if buffer:
                        self.str_rootJoint = buffer[0]
                    else:
                        self.str_rootJoint = mi_end.mNode
                except Exception,error:
                    log.error("%s failed to find root joint from moduleParent | %s"%(self._str_reportStart,error))

            #Orient info ------------------------------------------------------------------------------------------------
            self.v_aimNegative = cgmValid.simpleAxis(self.str_orientation[0]+"-").p_vector
            self.v_aim = cgmValid.simpleAxis(self.str_orientation[0]).p_vector	
            self.v_up = cgmValid.simpleAxis(self.str_orientation[1]).p_vector	
            self.v_upNegative = cgmValid.simpleAxis(self.str_orientation[1]+"-").p_vector	
            self.v_out = cgmValid.simpleAxis(self.str_orientation[2]).p_vector	
            self.v_outNegative = cgmValid.simpleAxis(self.str_orientation[2]+"-").p_vector	

            #Find our helpers -------------------------------------------------------------------------------------------
            self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise StandardError,"%s >>> No suitable helper found"%(_str_funcName)

            self.mi_leftBrowCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftBrowHelper'),noneValid=False)
            self.mi_rightBrowCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightBrowHelper'),noneValid=False)

            self.mi_leftTempleCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftTempleHelper'),noneValid=False)
            self.mi_rightTempleCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightTempleHelper'),noneValid=False)

            self.mi_leftUprCheekCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftUprCheekHelper'),noneValid=False)
            self.mi_rightUprCheekCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightUprCheekHelper'),noneValid=False)

            self.mi_squashCastHelper = cgmMeta.validateObjArg(self.mi_helper.getMessage('squashCastHelper'),noneValid=True)
            self.mi_uprFacePivotHelper = cgmMeta.validateObjArg(self.mi_helper.getMessage('uprFacePivotHelper'),noneValid=True)

            self.mi_jawPlate = cgmMeta.validateObjArg(self.mi_helper.getMessage('jawPlate'),noneValid=True)
            self.mi_skullPlate = cgmMeta.validateObjArg(self.mi_helper.getMessage('skullPlate'),noneValid=True)

            #Get some data from helpers --------------------------------------------------------------------------------------
            self.int_browJointsCnt = self.mi_helper.browJoints
            self.int_templeJointsCnt = self.mi_helper.templeJoints
            self.int_cheekJointsCnt = self.mi_helper.cheekJoints	

            return True

        def _buildSquashStretchCage_(self): 
            if not self.mi_helper.buildSquashStretch:
                return False
            if not self.mi_skullPlate:
                log.error("%s Squash and stretch on. No skull plate found"%(self._str_reportStart))
                return False

            d_casts = {'top':{'direction':self.str_orientation[1]+"+"},
                       'left':{'direction':self.str_orientation[2]+"+"},
                       'right':{'direction':self.str_orientation[2]+"-"},
                       'back':{'direction':self.str_orientation[0]+"-"}}

            self.d_squash = d_casts

            #Need to build some locs
            for k in d_casts.keys():
                str_cast = d_casts[k]['direction']
                d_return = rayCast.findMeshIntersectionFromObjectAxis(self.l_targetMesh[0],self.mi_squashCastHelper.mNode,str_cast) or {}
                pos = d_return.get('hit')
                if not pos:
                    log.warning("rayCast.findMeshIntersectionFromObjectAxis(%s,%s,%s)"%(self.l_targetMesh[0],self.mi_squashCastHelper.mNode,str_cast))
                    raise StandardError, "Failed to find hit." 
                log.debug("%s >>> Squash stretch cast. key: %s | cast: %s | pos:%s"%(self._str_reportStart,k, str_cast,pos))
                try:#Create and name
                    mc.select(cl=True)
                    mi_jnt = cgmMeta.asMeta(mc.joint(p = pos),'cgmObject',setClass = True)
                    mi_jnt.parent = False
                    mi_jnt.addAttr('cgmDirection',k ,lock=True)			    
                    mi_jnt.addAttr('cgmName',"head",lock=True)	
                    mi_jnt.addAttr('cgmNameModifier',"squash",lock=True)			    
                    mi_jnt.doName()
                except Exception,error:
                    raise StandardError,"Create fail. direction: %s | pos : %s | error: %s "%(k,pos,error)       
                try:#Orient
                    constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
                    mc.delete(constraintBuffer)
                    mi_jnt.parent = self.str_rootJoint
                except Exception,error:raise StandardError,"Orient fail. direction: %s | pos : %s | error: %s "%(k,pos,error)       

                jntUtils.metaFreezeJointOrientation(mi_jnt)

                self.d_squash[k]['ml_joints'] = [mi_jnt] #nested list
                self.ml_moduleJoints.append(mi_jnt)

            return True

        def _buildMidBrow_(self): 	    
            #We need to find the middle point between 
            l_leftCV = self.mi_leftBrowCrv.getComponents('cv')
            l_rightCV = self.mi_rightBrowCrv.getComponents('cv')
            pos = distance.returnAveragePointPosition( [mc.pointPosition(l_leftCV[0],w=True),mc.pointPosition(l_rightCV[0],w=True)] )

            try:#Create and name --------------------------------------------------------------------------------
                mc.select(cl=True)
                mi_jnt = cgmMeta.asMeta(mc.joint(p = pos),'cgmObject',setClass = True)
                mi_jnt.parent = False
                mi_jnt.addAttr('cgmName',"brow",lock=True)
                mi_jnt.addAttr('cgmDirection',"center",lock=True)		    					
                mi_jnt.doName()
                #log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_templeJoints]))
            except Exception,error:
                raise StandardError,"error: %s "%(error)       
            try:#Orient
                constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
                mc.delete(constraintBuffer)
                mi_jnt.parent = self.str_rootJoint
            except Exception,error:raise StandardError,"error: %s "%(error)       

            jntUtils.metaFreezeJointOrientation(mi_jnt)	  

            self.ml_moduleJoints.append(mi_jnt)
            self.md_moduleJoints['midBrow'] = mi_jnt
            #self.mi_go._mi_rigNull.msgList_connect(mi_jnt,'moduleCenterBrowJoints','rigNull')#Connect

            return True

        def _buildBrow_(self): 	    
            d_buildCurves = {'left':{'crv':self.mi_leftBrowCrv},
                             'right':{'crv':self.mi_rightBrowCrv}}	    
            self.d_browCurveBuild = d_buildCurves


            try:#>> We're gonna make an up loc
                mi_midBrow = self.md_moduleJoints['midBrow']
                #mi_upLoc = mi_midBrow.doLoc()
                #mi_upLoc.parent = mi_midBrow
                #mi_upLoc.__setattr__("t%s"%self.str_orientation[1],20)
            except Exception,error:
                raise StandardError,"[Up loc creation] | error: {0}".format(error)  


            for k in d_buildCurves.keys():#Make our left and right joints
                mi_crv = d_buildCurves[k].get('crv')#get instance
                int_count = self.int_browJointsCnt#get int
                log.debug("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
                try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
                except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)       
                d_buildCurves[k]['l_pos'] = l_pos#Store it
                log.debug("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
                l_jointBuffer = []
                ml_endJoints = []
                ml_browJoints = []
                for i,pos in enumerate(l_pos):
                    try:#Create and name
                        mc.select(cl=True)
                        mi_jnt = cgmMeta.asMeta(mc.joint(p = pos),'cgmObject',setClass = True)
                        mi_jnt.parent = False
                        mi_jnt.addAttr('cgmName',"brow",lock=True)		    			
                        mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
                        mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
                        mi_jnt.doName()
                        l_jointBuffer.append(mi_jnt)
                        ml_browJoints.append(mi_jnt)
                        #log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_browJoints]))
                    except Exception,error:
                        raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)   

                #Aim Pass ------------------------------------------------------------------------------
                if k == 'left':
                    v_aim = self.v_outNegative
                    v_up = self.v_aim	
                    f_offset = 20
                else:
                    v_aim = self.v_out
                    v_up = self.v_aim
                    f_offset = 20	

                for i,mi_jnt in enumerate(ml_browJoints):
                    try:#Orient
                        if mi_jnt == ml_browJoints[-1]:
                            joints.doCopyJointOrient(ml_browJoints[-2].mNode,mi_jnt.mNode)
                            mi_upLoc = mi_jnt.doLoc(fastMode = True)	

                            mi_upLoc.parent = mi_jnt
                            mi_upLoc.__setattr__("t%s"%self.str_orientation[0],f_offset)
                            mi_upLoc.parent = False
                        else:
                            mi_upLoc = mi_jnt.doLoc(fastMode = True)
                            mc.move (0,0,20, mi_upLoc.mNode, r=True, rpr = True, ws = True, wd = True)	

                        if i == 0:mi_target = mi_midBrow
                        else:mi_target = ml_browJoints[i-1]			


                        passKWS = {'weight' : 1, 'aimVector' : v_aim, 'upVector' : v_up,
                                   'worldUpObject' : mi_upLoc.mNode,'worldUpType' : 'object'}

                        mc.delete( mc.aimConstraint(mi_target.mNode, mi_jnt.mNode,**passKWS))         
                        mi_jnt.parent = self.str_rootJoint

                        mi_upLoc.delete()
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
                    try:#freeze
                        jntUtils.metaFreezeJointOrientation(mi_jnt)
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
                d_buildCurves[k]['ml_joints'] = ml_browJoints #nested list
                #self.mi_go._mi_rigNull.msgList_connect(ml_browJoints,'moduleBrowJoints_%s'%k,'rigNull')
                self.ml_moduleJoints.extend(ml_browJoints)

            return True

        def _buildCheek_(self): 
            if not self.mi_helper.buildUprCheek:
                log.info("%s >>> Build cheek toggle: off"%(self._str_reportStart))
                return True

            d_buildCurves = {'left':{'crv':self.mi_leftUprCheekCrv},
                             'right':{'crv':self.mi_rightUprCheekCrv}}	

            self.d_cheekCurveBuild = d_buildCurves

            for k in d_buildCurves.keys():#Make our left and right joints
                mi_crv = d_buildCurves[k].get('crv')#get instance
                int_count = self.int_cheekJointsCnt#get int
                log.debug("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
                #Get our l_pos on which to build the joints ------------------------------------------------------------
                if int_count == 1:
                    l_pos = [ mc.pointPosition(mi_crv.getComponents('cv')[0], w = True)]
                else:
                    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
                    except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)       
                d_buildCurves[k]['l_pos'] = l_pos#Store it
                log.debug("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
                l_jointBuffer = []
                ml_endJoints = []
                ml_cheekJoints = []
                for i,pos in enumerate(l_pos):
                    try:#Create and name
                        mc.select(cl=True)
                        mi_jnt = cgmMeta.asMeta(mc.joint(p = pos),'cgmObject',setClass = True)
                        mi_jnt.parent = False
                        mi_jnt.addAttr('cgmName',"uprCheek",lock=True)		    			
                        mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
                        mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
                        mi_jnt.doName()
                        l_jointBuffer.append(mi_jnt)
                        ml_cheekJoints.append(mi_jnt)
                        #log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_cheekJoints]))
                    except Exception,error:
                        raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
                    try:#Orient
                        constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
                        mc.delete(constraintBuffer)
                        mi_jnt.parent = self.str_rootJoint
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
                    try:#freeze
                        jntUtils.metaFreezeJointOrientation(mi_jnt)
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
                d_buildCurves[k]['ml_joints'] = ml_cheekJoints #nested list
                #self.mi_go._mi_rigNull.msgList_connect(ml_cheekJoints,'moduleCheekJoints_%s'%k,'rigNull')
                self.ml_moduleJoints.extend(ml_cheekJoints)

            return True

        def _buildTemple_(self): 
            if not self.mi_helper.buildTemple:
                log.info("%s >>> Build temple toggle: off"%(self._str_reportStart))
                return True

            d_buildCurves = {'left':{'crv':self.mi_leftTempleCrv},
                             'right':{'crv':self.mi_rightTempleCrv}}	

            self.d_templeCurveBuild = d_buildCurves

            for k in d_buildCurves.keys():#Make our left and right joints
                mi_crv = d_buildCurves[k].get('crv')#get instance
                int_count = self.int_templeJointsCnt#get int
                log.debug("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
                #Get our l_pos on which to build the joints ------------------------------------------------------------
                if int_count == 1:
                    l_pos = [ mc.pointPosition(mi_crv.getComponents('cv')[0], w = True)]
                else:
                    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
                    except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)       
                d_buildCurves[k]['l_pos'] = l_pos#Store it
                log.debug("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
                l_jointBuffer = []
                ml_endJoints = []
                ml_templeJoints = []
                for i,pos in enumerate(l_pos):
                    try:#Create and name
                        mc.select(cl=True)
                        mi_jnt = cgmMeta.asMeta(mc.joint(p = pos),'cgmObject',setClass = True)
                        mi_jnt.parent = False
                        mi_jnt.addAttr('cgmName',"temple",lock=True)		    			
                        mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
                        mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
                        mi_jnt.doName()
                        l_jointBuffer.append(mi_jnt)
                        ml_templeJoints.append(mi_jnt)
                        #log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_templeJoints]))
                    except Exception,error:
                        raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
                    try:#Orient
                        constraintBuffer = mc.normalConstraint(self.l_targetMesh[0],mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
                        mc.delete(constraintBuffer)
                        mi_jnt.parent = self.str_rootJoint
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
                    try:#freeze
                        jntUtils.metaFreezeJointOrientation(mi_jnt)
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
                d_buildCurves[k]['ml_joints'] = ml_templeJoints #nested list
                #self.mi_go._mi_rigNull.msgList_connect(ml_templeJoints,'moduleTempleJoints_%s'%k,'rigNull')
                self.ml_moduleJoints.extend(ml_templeJoints)

            return True

        def _connect_(self): 
            self.mi_go._mi_rigNull.msgList_connect('moduleJoints',self.ml_moduleJoints,'rigNull')
            self.mi_go._mi_rigNull.msgList_connect('skinJoints',self.ml_moduleJoints)

            return True

    #We wrap it so that it autoruns and returns
    return fncWrap(goInstance).go() 

def doSkeletonizeMouthNose(*args,**kws):
    class fncWrap(JointFactoryFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = 'doSkeletonizeMouthNose(%s)'%self.mi_module.p_nameShort
            #self._b_autoProgressBar = True
            self._b_reportTimes = 1
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
                                {'step':'Build Nose','call':self._buildNose_},
                                {'step':'Build UprCheek','call':self._buildUprCheek_},
                                {'step':'Build Smile Lines','call':self._buildSmile_},
                                {'step':'Build Jaw','call':self._buildJaw_},
                                {'step':'Build Cheek','call':self._buildCheek_},	                        	                        
                                {'step':'Build Lips','call':self._buildLips_},
                                {'step':'Build Tongue','call':self._buildTongue_},
                                {'step':'Build Teeth','call':self._buildTeeth_},	                                                        
                                {'step':'Connect','call':self._connect_}]


            assert self.mi_module.mClass == 'cgmMouthNose',"%s >>> Module is not type: 'cgmMouthNose' | type is: '%s'"%(self._str_funcName,self.mi_module.mClass)
            
            #The idea is to register the functions needed to be called
            #=================================================================

        def _gatherInfo_(self): 
            self.str_orientation = self.mi_go.str_jointOrientation #Link
            self.str_partName = self.mi_go._partName	
            
            try:
                self.l_targetMesh = self.mi_go._mi_puppet.getUnifiedGeo() or self.mi_go._mi_puppet.getGeo() or 'Morphy_Body_GEO1'#>>>>>>>>>>>>>>>>>this needs better logic   
            except Exception,error:
                raise error
            
            #Find our head attach joint ------------------------------------------------------------------------------------------------
            self.str_rootJoint = False
            if self.mi_module.getMessage('moduleParent'):
                try:
                    mi_end = self.mi_module.moduleParent.rigNull.msgList_get('moduleJoints')[-1]
                    buffer =  mi_end.getMessage('scaleJoint')
                    if buffer:self.str_rootJoint = buffer[0]
                    else:self.str_rootJoint = mi_end.mNode
                except Exception,error:
                    log.error("%s failed to find root joint from moduleParent | %s"%(self._str_reportStart,error))
            
            #Orient info ------------------------------------------------------------------------------------------------
            self.v_aimNegative = cgmValid.simpleAxis(self.str_orientation[0]+"-").p_vector
            self.v_aim = cgmValid.simpleAxis(self.str_orientation[0]).p_vector	
            self.v_up = cgmValid.simpleAxis(self.str_orientation[1]).p_vector	
            self.v_upNegative = cgmValid.simpleAxis(self.str_orientation[1]+"-").p_vector	
            self.v_out = cgmValid.simpleAxis(self.str_orientation[2]).p_vector	
            self.v_outNegative = cgmValid.simpleAxis(self.str_orientation[2]+"-").p_vector
            
            #Find our helpers -------------------------------------------------------------------------------------------
            self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise StandardError,"No suitable helper found"
            
            for attr in self.mi_helper.getAttrs(userDefined = True):#Get allof our Helpers
                if "Helper" in attr:
                    try:self.__dict__["mi_%s"%attr.replace('Helper','Crv')] = cgmMeta.validateObjArg(self.mi_helper.getMessage(attr),noneValid=False)
                    except Exception,error:raise StandardError, " Failed to find '%s' | %s"%(attr,error)
            #...using skull plate self.mi_skullPlate = cgmMeta.validateObjArg(self.mi_helper.getMessage('skullPlate'),noneValid=False)
            self.mi_skullPlate = cgmMeta.validateObjArg(self.mi_go._mi_puppet.getMessage('unifiedGeo'),noneValid=False)            
            self.str_skullPlate = self.mi_skullPlate.mNode
            
            #Get some data from helpers --------------------------------------------------------------------------------------
            self.int_lipCount = self.mi_helper.lipJoints
            self.int_cheekLoftCount = self.mi_helper.cheekLoftCount
            self.int_cheekCount = self.mi_helper.cheekJoints
            self.int_nostrilCount = self.mi_helper.nostrilJoints
            self.int_uprCheekCount = self.mi_helper.uprCheekJoints
            self.int_tongueCount = self.mi_helper.tongueJoints
            self.int_smileLineCount = self.mi_helper.smileLineCount

            #Running lists ============================================================================================
            self.ml_moduleJoints = []
            self.md_moduleJoints = {}
            return True

        def _buildJaw_(self):
            str_skullPlate = self.str_skullPlate

            try:#jaw Root ==============================================================================================
                mi_crv = self.mi_jawPivotCrv
                tag = 'jaw'
                try:#Create an name -------------------------------------------------------------------------
                    mi_root = cgmMeta.asMeta(mc.joint(p = mi_crv.getPosition()),'cgmObject',setClass = True)
                    mi_root.addAttr('cgmName',tag,lock=True)		    			
                    mi_root.doName()
                    self.ml_moduleJoints.append(mi_root)
                    self.md_moduleJoints[tag] = mi_root
                except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error)
                try:#Aim Constraint -------------------------------------------------------------------------
                    mi_upLoc = mi_root.doLoc(fastMode = True)
                    mi_aimLoc = mi_root.doLoc(fastMode = True)
                    mi_upLoc.parent = mi_crv
                    mi_aimLoc.parent = mi_crv
                    mi_aimLoc.__setattr__("t%s"%self.str_orientation[0],10)
                    mi_upLoc.__setattr__("t%s"%self.str_orientation[1],10)
                    mc.delete( mc.aimConstraint(mi_aimLoc.mNode,mi_root.mNode,
                                                weight = 1, aimVector = self.v_aim, upVector = self.v_up,
                                                worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )		    
                    mi_root.parent = self.str_rootJoint
                    jntUtils.metaFreezeJointOrientation(mi_root)
                    mc.delete([mi_upLoc.mNode,mi_aimLoc.mNode])
                except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error) 
                self.mi_go._mi_rigNull.msgList_connect('jawJoint',mi_root)		
            except Exception,error:raise StandardError,"jaw root | %s "%(error) 

            try:#JawLine ==============================================================================================
                if not self.mi_helper.buildJawLine:
                    self.log_warning("buildJawLine is off")
                    return True
                mi_crv = self.mi_jawLineCrv
                tag = 'jawLine'
                l_build = [{'direction':'center','minU':None,'maxU':None, 'reverse':False, 'count':1},
                           {'direction':'left','minU':None,'maxU':.3, 'reverse':False,'count':3},
                           {'direction':'right','minU':None,'maxU':.3, 'reverse':True,'count':3}]
                md_buffer = {}
                for d in l_build:#First loop creates and stores to runnin md
                    int_cnt = d['count']
                    str_direction = d['direction']
                    md_buffer[str_direction] = []
                    ml_createdbuffer = []
                    if int_cnt == 1:
                        l_pos = [crvUtils.getMidPoint(mi_crv.mNode)]
                    else:
                        l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode, int_cnt, minU = d['minU'], maxU = d['maxU'], reverseCurve = d['reverse'], rebuildForSplit=True)
                    ##log.info("%s l_pos : %s"%(self._str_reportStart, l_pos))
                    int_lenMax = len(l_pos)
                    for i,pos in enumerate(l_pos):
                        try:#Create an name -------------------------------------------------------------------------
                            self.progressBar_set(status = "Creating %s '%s'"%(str_direction,i), progress = i, maxValue = int_lenMax)						    								    

                            mc.select(cl=True)
                            str_mdTag = "%s_%s_%s"%(str_direction,tag,i)
                            mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject',setClass=True )
                            mi_jnt.addAttr('cgmName',tag,lock=True)
                            if str_direction is not None:
                                mi_jnt.addAttr('cgmDirection',str_direction,lock=True)
                            if int_cnt > 1:
                                mi_jnt.addAttr('cgmIterator',i,lock=True)		    			
                            mi_jnt.doName()
                            ml_createdbuffer.append(mi_jnt)
                            self.md_moduleJoints[str_mdTag] = mi_jnt
                            md_buffer[str_direction].append(mi_jnt)
                        except Exception,error:raise StandardError,"%s create and name fail | %s "%(str_mdTag,error)
                        try:#Snap
                            Snap.go(mi_jnt,self.str_skullPlate,snapToSurface=True)
                            if str_direction == 'center':mi_jnt.__setattr__("t%s"%self.str_orientation[2],0)
                        except Exception,error:
                            raise StandardError,"snap to mesh | pos count: %s | error: %s "%(k,i,error) 
                    self.ml_moduleJoints.extend(ml_createdbuffer)		    
                    self.mi_go._mi_rigNull.msgList_connect("%s_%sJoint"%(str_direction,tag),ml_createdbuffer)		

                for d in l_build:#Second loop aims....
                    str_direction = d['direction']		    
                    try:#Orienting -------------------------------------------------------------------------
                        str_mirror = False
                        ml_joints = md_buffer[str_direction]


                        ##log.info("%s direction: %s"%(self._str_reportStart,str_direction))
                        ##log.info("%s joints: %s"%(self._str_reportStart,[mJnt.p_nameShort for mJnt in ml_joints]))	
                        int_lenMax = len(ml_joints)
                        for i,mi_jnt in enumerate(ml_joints):
                            self.progressBar_set(status = "Orienting %s '%s'"%(str_direction,i), progress = i, maxValue = int_lenMax)						    								    
                            if str_direction == 'center':
                                mc.delete( mc.aimConstraint(self.md_moduleJoints['noseUnder'].mNode, mi_jnt.mNode,
                                                            weight = 1, aimVector = self.v_up, upVector = self.v_aimNegative,
                                                            worldUpObject = mi_root.mNode, worldUpType = 'object' ) )				
                                #joints.doCopyJointOrient(mi_root.mNode,mi_jnt.mNode)
                                '''
				mc.delete( mc.normalConstraint(str_skullPlate,mi_jnt.mNode, weight = 1,
				                               aimVector = self.v_aim, upVector = self.v_up,
				                               worldUpType = 'scene' ))
							       '''
                            else:
                                if i == 0:
                                    mi_aimObj = ml_joints[i+1]
                                    if str_direction == 'right':
                                        str_mirror = 'left'
                                        v_aim = self.v_out
                                    else:
                                        str_mirror = 'right'
                                        v_aim = self.v_outNegative				    
                                else:
                                    mi_aimObj = ml_joints[i-1]
                                    if str_direction == 'right':
                                        str_mirror = 'left'
                                        v_aim = self.v_outNegative
                                    else:
                                        str_mirror = 'right'
                                        v_aim = self.v_out				    
                                mi_upObj = md_buffer[str_mirror][0]
                                ##log.info("%s aiming '%s' @ '%s' | up: '%s'"%(self._str_reportStart,mi_jnt.p_nameShort,mi_aimObj.p_nameShort,mi_upObj.p_nameShort))									    
                                mc.delete( mc.aimConstraint(mi_aimObj.mNode, mi_jnt.mNode,
                                                            weight = 1, aimVector = v_aim, upVector = self.v_aimNegative,
                                                            worldUpObject = mi_upObj.mNode, worldUpType = 'object' ) )			    

                            mi_jnt.parent = mi_root.mNode
                            jntUtils.metaFreezeJointOrientation(mi_jnt)		    
                    except Exception,error:raise StandardError,"%s orient fail | %s "%(str_mdTag,error) 
            except Exception,error:raise StandardError,"JawLine | %s "%(error) 	    
            return True	

        def _buildLips_(self):
            if not self.mi_helper.buildJawLine:
                self.log_warning("buildJawLine is off. Not building Lips")
                return True            
            
            str_skullPlate = self.str_skullPlate

            l_build = [{'tag':'lipUpr','crv':self.mi_lipUprCrv, 'minU':None, 'maxU':None, 'count':self.int_lipCount, 'startSplitFactor':.05, 'parent':self.str_rootJoint},
                       {'tag':'lipLwr','crv':self.mi_lipLwrCrv, 'minU':None, 'maxU':None, 'count':self.int_lipCount, 'startSplitFactor':.05,'parent':self.md_moduleJoints['jaw']},
                       {'tag':'lipOver','crv':self.mi_lipOverTraceCrv,'minU':.1, 'maxU':.9, 'count':3, 'startSplitFactor': None, 'parent':self.str_rootJoint},
                       {'tag':'lipUnder','crv':self.mi_lipUnderTraceCrv,'minU':.1, 'maxU':.9, 'count':3, 'startSplitFactor': None, 'parent':self.md_moduleJoints['jaw']}]

            md_buffer = {}
            for d in l_build:#First loop creates and stores to runnin md
                int_cnt = d['count']
                tag = d['tag']
                md_buffer[tag] = {'ml_list':[]}
                mi_crv = d['crv']

                try:#Get positions ----------------------------------------------------------------------------------
                    if int_cnt == 1: l_pos = [crvUtils.getMidPoint(mi_crv.mNode)]
                    else: 
                        l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode, int_cnt, minU = d['minU'], maxU = d['maxU'], startSplitFactor=d['startSplitFactor'], rebuildForSplit=True)
                    if tag == 'lipLwr': l_pos = l_pos[1:-1]
                except Exception,error:raise StandardError,"%s get positions | %s "%(tag,error)

                int_lenMax = len(l_pos)
                int_last = int_lenMax-1

                for i,pos in enumerate(l_pos):
                    try:#Create an name -------------------------------------------------------------------------
                        self.progressBar_set(status = "Creating %s '%s'"%(tag,i), progress = i, maxValue = int_lenMax)						    								    
                        mc.select(cl=True)
                        mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject', setClass=True )
                        if i in [0,int_last] and tag == 'lipUpr':
                            mi_jnt.addAttr('cgmName','lipCorner',lock=True)			    			    
                        else:
                            mi_jnt.addAttr('cgmName',tag,lock=True)	
                        md_buffer[tag]['ml_list'].append(mi_jnt)
                        self.ml_moduleJoints.append(mi_jnt)			    
                    except Exception,error:raise StandardError,"%s create | %s "%(tag,error)

            for d in l_build:#Second loop split and names....
                md_sides = {}		    
                tag = d['tag']		    
                ml_buffer = md_buffer[tag]['ml_list']
                ###log.info("%s %s >> %s"%(self._str_reportStart,tag,ml_buffer))		    
                try:#Split ----------------------------------------------------------------------------------
                    #We need to split our list
                    int_len = len(ml_buffer)
                    int_mid = int(int_len/2)	

                    if int_len%2==0:#If even,no mid....
                        raise StandardError, "Need to write this..."
                        md_sides['left'] = ml_buffer[:int_mid + 1]
                        md_sides['right'] = ml_buffer[int_mid:]
                    else:#odd
                        if tag == 'lipUpr':
                            md_sides['left'] = ml_buffer[1:int_mid]
                            md_sides['center'] = [ml_buffer[int_mid]]			
                            md_sides['right'] = ml_buffer[int_mid+1:-1]			    
                            md_sides['leftCorner'] = [ml_buffer[0]]
                            md_sides['rightCorner'] = [ml_buffer[-1]]	
                            self.md_moduleJoints['leftLipCorner'] = ml_buffer[0]
                            self.md_moduleJoints['rightLipCorner'] = ml_buffer[-1] 
                            self.mi_go._mi_rigNull.msgList_connect("left_lipCornerJoint",ml_buffer[0])			    			    
                            self.mi_go._mi_rigNull.msgList_connect("right_lipCornerJoint",ml_buffer[-1])			    			    
                        else:
                            md_sides['left'] = ml_buffer[:int_mid]
                            md_sides['center'] = [ml_buffer[int_mid]]			
                            md_sides['right'] = ml_buffer[int_mid+1:]			    
                    md_sides['right'].reverse()
                except Exception,error:raise StandardError,"%s split | %s "%(tag,error)

                for k in md_sides.keys():
                    ml_side = md_sides[k]
                    int_len = len(ml_side)
                    ###log.info("%s | %s >> %s"%(tag,k,int_len))
                    if 'left' in k:str_direction = 'left'
                    elif 'right' in k:str_direction = 'right'
                    else: str_direction = 'center'

                    #Store it -----------------------------------------------------------------
                    self.mi_go._mi_rigNull.msgList_connect(ml_side,"%s_%sJoint"%(str_direction,tag))			    
                    #self.ml_moduleJoints.extend(ml_createdbuffer)		    
                    #self.mi_go._mi_rigNull.msgList_connect(ml_createdbuffer,"%s_%s"%(str_direction,tag))	

                    #md_jointsToDirection = []
                    int_lenMax = len(ml_side)
                    int_last = int_lenMax-1			

                    for i,mi_jnt in enumerate(ml_side):
                        self.progressBar_set(status = "Orienting %s '%s'"%(k,i), progress = i, maxValue = int_lenMax)						    								    
                        l_tagBuild = [str_direction,mi_jnt.cgmName]#Need to build our storage tag
                        if 'left' in k:
                            mi_jnt.addAttr('cgmDirection','left',lock=True)
                        elif 'right' in k:
                            mi_jnt.addAttr('cgmDirection','right',lock=True)
                        else:
                            mi_jnt.addAttr('cgmDirection',k,lock=True)
                        if int_len > 1:
                            mi_jnt.addAttr('cgmIterator',i,lock=True)
                            l_tagBuild.append("%s"%i)
                        mi_jnt.doName()	
                        if k == 'center':mi_jnt.__setattr__("t%s"%self.str_orientation[2],0)			
                        str_mdTag = "_".join(l_tagBuild)
                        self.md_moduleJoints[str_mdTag] = mi_jnt#Store to our module joint running list
                        try:#>>> Orient -----------------------------------------------------------------------
                            if str_direction == 'right':
                                v_aimIn = self.v_out
                                v_aimOut = self.v_outNegative				
                            else:
                                v_aimIn = self.v_outNegative
                                v_aimOut = self.v_out					

                            #First we contrain to the skill plate for our intial orientation
                            mc.delete( mc.normalConstraint(str_skullPlate,mi_jnt.mNode, weight = 1,
                                                           aimVector = self.v_aim, upVector = self.v_up,
                                                           worldUpType = 'scene' ))

                            #Then we're gonna do a more careful aim with a blend
                            if str_direction != 'center' and 'Corner' not in mi_jnt.cgmName and tag not in ['lipOver','lipUnder']:
                                if i == 0:
                                    mi_aimOut = self.md_moduleJoints[str_direction+'LipCorner']	
                                    mi_aimIn = ml_side[i+1]
                                elif i == int_last:
                                    mi_aimOut = ml_side[i-1]
                                    mi_aimIn = md_sides['center'][0]			    
                                else:
                                    mi_aimOut = ml_side[i-1]
                                    mi_aimIn = ml_side[i+1]

                                #up loc ------------------------------------------------------------------------
                                mi_upLoc = mi_jnt.doLoc(fastMode = True)
                                mi_upLoc.parent = mi_jnt
                                mi_upLoc.__setattr__("t%s"%self.str_orientation[1],10)
                                mi_upLoc.parent = False

                                mi_locIn = mi_jnt.doLoc(fastMode = True)
                                mi_locOut = mi_jnt.doLoc()

                                mc.delete( mc.aimConstraint(mi_aimIn.mNode, mi_locIn.mNode,
                                                            weight = 1, aimVector = v_aimIn, upVector = self.v_up,
                                                            worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )	
                                mc.delete( mc.aimConstraint(mi_aimOut.mNode, mi_locOut.mNode,
                                                            weight = 1, aimVector = v_aimOut, upVector = self.v_up,
                                                            worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )
                                mc.delete( mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_jnt.mNode,
                                                               weight = 1) )
                                mc.delete([mi_locIn.mNode,mi_locOut.mNode,mi_upLoc.mNode])
                                '''
				#aim....
				###log.info("%s aiming '%s' @ '%s' | up: '%s'"%(self._str_reportStart,mi_jnt.p_nameShort,mi_aimObj.p_nameShort,mi_upLoc.p_nameShort))									    				    
				mc.delete( mc.aimConstraint(mi_aimObj.mNode, mi_jnt.mNode,
			                                    weight = 1, aimVector = v_aim, upVector = self.v_up,
			                                    worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )
				mi_upLoc.delete()
				'''
                            mi_jnt.parent = d['parent']
                            jntUtils.metaFreezeJointOrientation(mi_jnt)		    
                        except Exception,error:raise StandardError,"%s (%s) orient fail | %s "%(str_mdTag,mi_jnt.p_nameShort,error) 			    
            return True	

        def _buildNose_(self):
            if not self.mi_helper.buildNose:
                self.log_warning("buildNose is off.")
                return True    
            
            str_skullPlate = self.str_skullPlate
            md_noseBuilt = {} #We're gonna use this as a running list 
            int_lenNoseSteps = 4
            try:#Nose Root ==============================================================================================
                self.progressBar_set(status = "Creating root", progress = 0, maxValue = int_lenNoseSteps)						    		
                mi_crv = self.mi_noseBaseCastCrv
                l_components = mi_crv.getComponents('cv')
                tag = 'noseBase'
                try:#Create our root -------------------------------------------------------------------------
                    l_checkPos = [{'direction':'left','minU':.05,'maxU':.4, 'reverse':False},
                                  {'direction':'right','minU':.05,'maxU':.4, 'reverse':True}]

                    l_pos = []
                    for d in l_checkPos:
                        l_pos.extend( crvUtils.returnSplitCurveList(mi_crv.mNode,
                                                                    1, minU = .05, maxU = .4,
                                                                    reverseCurve = d['reverse'], rebuildForSplit=True))		    

                    pos = distance.returnAveragePointPosition(l_pos)

                    mi_root = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject', setClass=True )
                    mi_root.addAttr('cgmName',tag,lock=True)		    			
                    mi_root.doName()
                    self.ml_moduleJoints.append(mi_root)
                    md_noseBuilt[tag] = mi_root
                    self.mi_go._mi_rigNull.msgList_connect("%sJoint"%(tag),mi_root)
                    mi_root.__setattr__("t%s"%self.str_orientation[2],0)#center

                except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error)
                try:#Normal Constraint -------------------------------------------------------------------------
                    constraintBuffer = mc.normalConstraint(str_skullPlate,mi_root.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
                    mc.delete(constraintBuffer)
                    mi_root.parent = self.str_rootJoint
                    jntUtils.metaFreezeJointOrientation(mi_root)		    
                except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error) 
            except Exception,error:raise StandardError,"Nose root | %s "%(error) 

            try:#Profile Crv ==============================================================================================
                mi_crv = self.mi_noseProfileCrv
                l_components = mi_crv.getComponents('cv')
                l_build = [{'tag':'noseTop','idx':-1,"aim":self.v_upNegative,'parent' : self.str_rootJoint,
                            "up":self.v_aim,"target":"skullPlate","upTarget":None},
                           {'tag':'noseUnder','idx':0, "aim":self.v_aimNegative,
                            "up":self.v_up,"target":"skullPlate","upTarget":None},
                           {'tag':'noseTip','idx':2, "aim":self.v_aimNegative,
                            "up":self.v_up,"target":"noseBase","upTarget":"noseTop"}]
                int_lenProfile = len(l_build)
                for i,d in enumerate(l_build):#First loop creates and stores to runnin md
                    try:#Create an name -------------------------------------------------------------------------
                        tag = d['tag']
                        idx = d['idx']
                        self.progressBar_set(status = "Creating '%s'"%tag, progress = i, maxValue = int_lenProfile)						    					
                        str_loc = locators.doLocPos( distance.returnWorldSpacePosition(l_components[idx]) )[0]
                        d_ret = distance.returnNearestPointOnCurveInfo(str_loc,mi_crv.mNode)
                        mc.delete(str_loc)#Delete the loc
                        mi_jnt = cgmMeta.asMeta( mc.joint(p = d_ret['position']),'cgmObject', setClass=True )
                        mi_jnt.addAttr('cgmName',tag,lock=True)		    			
                        mi_jnt.doName()
                        self.ml_moduleJoints.append(mi_jnt)
                        md_noseBuilt[tag] = mi_jnt
                        self.md_moduleJoints[tag] = mi_jnt
                        #Store it...
                        self.mi_go._mi_rigNull.msgList_connect("%sJoint"%(tag),mi_jnt)
                        if tag in ['noseTop','noseUnder']:
                            mi_jnt.__setattr__("t%s"%self.str_orientation[2],0)#center
                    except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error)  
                for i,d in enumerate(l_build):#Second pass aims. Two passes because we're aming at one another
                    try:#Normal Constraint -------------------------------------------------------------------------
                        self.progressBar_set(status = "Orienting '%s'"%tag, progress = i, maxValue = int_lenProfile)						    								
                        tag = d['tag']
                        v_aim = d['aim']
                        v_up = d['up']
                        target = d['target']
                        up = d['upTarget']
                        mi_jnt = md_noseBuilt[ tag ]
                        if target == 'skullPlate':
                            mc.delete( mc.normalConstraint(str_skullPlate,mi_jnt.mNode, weight = 1,
                                                           aimVector = self.v_aim, upVector = self.v_up,
                                                           worldUpType = 'scene' ))
                        else:
                            mc.delete( mc.aimConstraint(md_noseBuilt[ target ].mNode,mi_jnt.mNode,
                                                        weight = 1, aimVector = v_aim, upVector = v_up,
                                                        worldUpObject = md_noseBuilt[ up ].mNode, worldUpType = 'object' ) )
                        if d.get('parent'): mi_jnt.parent = d.get('parent')			    
                        else: mi_jnt.parent = mi_root.mNode
                        jntUtils.metaFreezeJointOrientation(mi_jnt)		    
                    except Exception,error:raise StandardError,"%s orient fail | %s "%(tag,error) 
            except Exception,error:raise StandardError,"Profile | %s "%(error) 

            try:#Nostril ==============================================================================================
                mi_crv = self.mi_noseBaseCastCrv
                int_cnt = self.int_nostrilCount
                tag = 'nostril'
                try:
                    str_bufferU = mc.ls("%s.u[*]"%mi_crv.mNode)[0]
                    f_maxU = float(str_bufferU.split(':')[-1].split(']')[0])
                except Exception,error:raise StandardError,"[Get max U fail!]{%s} "%(error) 

                if int_cnt == 1:
                    l_build = [{'direction':'left','minU':.05,'maxU':.4, 'reverse':False, 'rootPos':mc.pointPosition("%s.u[%f]"%(mi_crv.mNode,0))},
                               {'direction':'right','minU':.05,'maxU':.4, 'reverse':True, 'rootPos':mc.pointPosition("%s.u[%f]"%(mi_crv.mNode,f_maxU))}]
                else:
                    raise NotImplementedError,"Don't know how to deal with more than one nostril joint yet"

                for d in l_build:#First loop creates and stores to runnin md
                    l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode, int_cnt, minU = .05, maxU = .4, reverseCurve = d['reverse'], rebuildForSplit=True)
                    l_pos.insert(0,d['rootPos'])
                    str_direction = d['direction']		    
                    ##log.info("%s l_pos : %s"%(self._str_reportStart, l_pos))
                    ml_createdbuffer = []
                    int_lenMax = len(l_pos)
                    for i,pos in enumerate(l_pos):
                        try:#Create an name -------------------------------------------------------------------------
                            str_mdTag = "%s_%s_%s"%(str_direction,tag,i)
                            self.progressBar_set(status = "Creating %s '%s'"%(str_direction,tag), progress = i, maxValue = int_lenMax)						    								    
                            mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject', setClass=True )
                            mi_jnt.addAttr('cgmName',tag,lock=True)		    						    
                            mi_jnt.addAttr('cgmDirection',str_direction,lock=True)
                            mi_jnt.addAttr('cgmIterator',i,lock=True,hidden = True)		    			
                            mi_jnt.doName()
                            mi_jnt.parent = False
                            self.ml_moduleJoints.append(mi_jnt)
                            md_noseBuilt[str_mdTag] = mi_jnt
                            self.md_moduleJoints[str_mdTag] = mi_jnt	
                            ml_createdbuffer.append(mi_jnt)

                        except Exception,error:raise StandardError,"[%s create and name fail]{%s}"%(str_mdTag,error) 
                    int_lenCreated = len(ml_createdbuffer)
                    for idx,mJnt in enumerate(ml_createdbuffer):
                        try:#Aim -------------------------------------------------------------------------
                            self.progressBar_set(status = "Orienting %s '%s'"%(str_direction,tag), progress = i, maxValue = int_lenCreated)						    								    
                            if idx == 0:
                                mTarget = ml_createdbuffer[1]
                                if str_direction == 'left':
                                    v_aim = self.v_outNegative
                                else:
                                    v_aim = self.v_out			    
                            else:
                                mTarget = ml_createdbuffer[idx-1]
                                v_aim = self.v_out
                                if str_direction == 'left':
                                    v_aim = self.v_out
                                else:
                                    v_aim = self.v_outNegative					
                            '''
			    mc.delete( mc.aimConstraint(md_noseBuilt[ 'noseBase' ].mNode, mJnt.mNode,
					weight = 1, aimVector = self.v_aimNegative, upVector = self.v_up,
					worldUpObject = md_noseBuilt[ 'noseTop' ].mNode, worldUpType = 'object' ) )
			    '''
                            mc.delete( mc.aimConstraint(mTarget.mNode, mJnt.mNode,
                                                        weight = 1, aimVector = v_aim, upVector = self.v_aimNegative,
                                                        worldUpObject = md_noseBuilt[ 'noseBase' ].mNode, worldUpType = 'object' ) )
                            mJnt.parent = mi_root.mNode
                            jntUtils.metaFreezeJointOrientation(mJnt)		    
                        except Exception,error:raise StandardError,"%s orient fail | %s "%(str_mdTag,error) 
                    #Store it...	    
                    self.mi_go._mi_rigNull.msgList_connect("%s_%sJoint"%(str_direction,tag),ml_createdbuffer)		    
            except Exception,error:raise StandardError,"Nostril | %s "%(error) 	    

            self.md_noseBuilt = md_noseBuilt
            return True

        def _buildSmile_(self):
            if not self.mi_helper.buildCheek:
                self.log_warning("buildCheek is off. Not building smile line ")
                return True      
            
            md_smileBuilt = {} #We're gonna use this as a running list 
            self.md_smileBuilt = md_smileBuilt#link it
            d_buildCurves = {'left':{'crv':self.mi_smileLeftCrv},
                             'right':{'crv':self.mi_smileRightCrv}}	

            #Get some statics
            int_count = self.int_smileLineCount#...was 5	    
            str_skullPlate = self.str_skullPlate

            for k in d_buildCurves.keys():#Make our left and right joints
                mi_crv = d_buildCurves[k].get('crv')#get instance
                ##log.info("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
                #Get our l_pos on which to build the joints ------------------------------------------------------------
                try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count, rebuildSpans=10)
                except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)  

                d_buildCurves[k]['l_pos'] = l_pos#Store it
                ##log.info("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
                ml_createdbuffer = []
                int_lenMax = len(l_pos)
                for i,pos in enumerate(l_pos):
                    self.progressBar_set(status = "Creating '%s' %s"%(k,i), progress = i, maxValue = int_lenMax)						    
                    try:#Create and name -----------------------------------------------------------------------------------------------
                        mc.select(cl=True)
                        mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject', setClass=True )
                        mi_jnt.parent = False
                        mi_jnt.addAttr('cgmName',"smileLine",lock=True)		    			
                        mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
                        mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
                        mi_jnt.doName()
                        self.ml_moduleJoints.append(mi_jnt)
                        ml_createdbuffer.append(mi_jnt)
                        ##log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_cheekJoints]))
                    except Exception,error:
                        raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       

                    #try:#Snap
                        #Snap.go(mi_jnt,self.str_skullPlate,snapToSurface=True)	
                    #except Exception,error:
                        #raise StandardError,"snap to mesh | pos count: %s | error: %s "%(k,i,error)       

                    try:#Orient -----------------------------------------------------------------------------------------------
                        mc.delete( mc.normalConstraint(str_skullPlate,mi_jnt.mNode, weight = 1,
                                                       aimVector = self.v_aim, upVector = self.v_up,
                                                       worldUpType = 'scene' ))
                        mi_jnt.parent = self.str_rootJoint
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
                    try:#Freeze -----------------------------------------------------------------------------------------------
                        jntUtils.metaFreezeJointOrientation(mi_jnt)
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       		

                for idx,mJnt in enumerate(ml_createdbuffer[1:]):#Second aim pass
                    self.progressBar_set(status = "Orienting %s %s"%(k,i), progress = idx, maxValue = int_lenMax)						    		    
                    try:#up loc -------------------------------------------------------------------------
                        mi_upLoc = mJnt.doLoc(fastMode = True)
                        mi_upLoc.parent = mJnt
                        mi_upLoc.__setattr__("t%s"%self.str_orientation[0],10)		    
                        mi_upLoc.parent = False
                    except Exception,error:raise StandardError,"[second orient fail]{%s}"%(error) 		


                    try:#Aim -------------------------------------------------------------------------	
                        mTarget = ml_createdbuffer[idx]
                        mc.delete( mc.aimConstraint(mTarget.mNode, mJnt.mNode,
                                                    weight = 1, aimVector = self.v_up, upVector = self.v_aim,
                                                    worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) )
                        mi_upLoc.delete()
                        jntUtils.metaFreezeJointOrientation(mJnt)		    
                    except Exception,error:raise StandardError,"[second orient fail]{%s}"%(error) 		

                #Store it...	    
                self.mi_go._mi_rigNull.msgList_connect("%s_%sJoint"%(k,'smileLine'),ml_createdbuffer)		   
            return True

        def _buildTongue_(self):
            if not self.mi_helper.buildTongue:
                self.log_warning("buildTongue is off.")
                return True 
            
            md_smileBuilt = {} #We're gonna use this as a running list 
            self.md_smileBuilt = md_smileBuilt#link it                            	

            #Get some statics
            int_count = self.int_tongueCount	    
            str_skullPlate = self.str_skullPlate
            mi_crv = self.mi_tongueCrv#get instance	    
            str_squashStart = self.mi_squashStartCrv.mNode

            ##log.info("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
            try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode, int_count, rebuildSpans=10)
            except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)  

            ##log.info("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
            ml_tongueJoints = []
            int_last = len(l_pos)-1
            for i,pos in enumerate(l_pos):
                try:#Create and name -----------------------------------------------------------------------------------------------
                    mc.select(cl=True)
                    mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject', setClass=True )
                    mi_jnt.addAttr('cgmName',"tongue",lock=True)		    			
                    mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
                    mi_jnt.doName()
                    self.ml_moduleJoints.append(mi_jnt)
                    ml_tongueJoints.append(mi_jnt)
                    mi_jnt.__setattr__("t%s"%self.str_orientation[2],0)#center		    
                    ##log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_tongueJoints]))
                except Exception,error:
                    raise StandardError,"pos count: %s | error: %s "%(i,error)       
            for i,mi_jnt in enumerate(ml_tongueJoints):
                try:#Orient -----------------------------------------------------------------------------------------------
                    if i == 0:
                        mi_jnt.parent = self.md_moduleJoints['jaw']

                    if i == int_last:
                        v_aim = self.v_aimNegative
                    else:
                        v_aim = self.v_aim
                    if mi_jnt != ml_tongueJoints[-1]:
                        mc.delete( mc.aimConstraint(ml_tongueJoints[i+1].mNode, mi_jnt.mNode,
                                                    weight = 1, aimVector = v_aim, upVector = self.v_up,
                                                    worldUpObject = str_squashStart, worldUpType = 'object' ) )			
                    else:
                        joints.doCopyJointOrient(ml_tongueJoints[-2].mNode,ml_tongueJoints[-1].mNode)
                except Exception,error:raise StandardError,"pos count: %s | Constraint fail | error: %s "%(i,error)       
                try:#Freeze -----------------------------------------------------------------------------------------------
                    if i > 0:
                        mi_jnt.parent = ml_tongueJoints[i-1]
                    jntUtils.metaFreezeJointOrientation(mi_jnt)
                except Exception,error:raise StandardError,"| pos count: %s | Freeze orientation fail | error: %s "%(i,error)       		
            #Store it...		    
            self.mi_go._mi_rigNull.msgList_connect("%sJoint"%('tongue'),ml_tongueJoints)		    
            return True	
        
        def _buildTeeth_(self):
            str_skullPlate = self.str_skullPlate

            try:#teeth Root ==============================================================================================
                mi_crv = self.mi_go._mi_module.helper.mouthMidCastHelper
                
                tag = 'teeth'
                try:
                    pos =  crvUtils.returnSplitCurveList(mi_crv.mNode,1)[0]
                except Exception,error:raise StandardError,"Position get fail | {0}".format(error)
                
                l_positionsTags = ['upper','lower']
                for p in l_positionsTags: 
                    try:#Create an name -------------------------------------------------------------------------
                        mi_jnt = cgmMeta.asMeta(mc.joint(p = pos),'cgmObject',setClass = True)
                        mi_jnt.addAttr('cgmName',tag,lock=True)	
                        mi_jnt.addAttr('cgmPosition',p,lock=True)		    			                        
                        mi_jnt.doName()
                        self.ml_moduleJoints.append(mi_jnt)
                        
                        if p is 'upper':
                            mi_jnt.parent = self.str_rootJoint
                            self.mi_go._mi_rigNull.msgList_connect('teethUprJoint',mi_jnt)		                            
                        else:
                            mi_jnt.parent = self.md_moduleJoints['jaw']      
                            self.mi_go._mi_rigNull.msgList_connect('teethLwrJoint',mi_jnt)		                                                        
                    except Exception,error:raise StandardError,"%s create and name fail | %s "%(tag,error)
                    
                    try:#Orient -------------------------------------------------------------------------
                        joints.orientJoint(mi_jnt.mNode, orientation=self.mi_go._mi_orientation.p_string, 
                                          up=self.mi_go._mi_orientation.p_string[1])
                        jntUtils.metaFreezeJointOrientation(mi_jnt.mNode)
                    except Exception,error:raise StandardError,"{0} create and name fail | {1} ".format(tag,error) 
                    

            except Exception,error:raise StandardError,"Teeth | {0} ".format(error) 

        def _buildUprCheek_(self): 
            if not self.mi_helper.buildUprCheek:
                self.log_warning("buildUprCheek is off.")
                return True             

            d_buildCurves = {'left':{'crv':self.mi_leftUprCheekCrv},
                             'right':{'crv':self.mi_rightUprCheekCrv}}	
            self.d_cheekCurveBuild = d_buildCurves

            for k in d_buildCurves.keys():#Make our left and right joints
                mi_crv = d_buildCurves[k].get('crv')#get instance
                int_count = self.int_uprCheekCount#get int
                log.debug("%s >>> building joints for %s curve | count: %s"%(self._str_reportStart,k, int_count))
                #Get our l_pos on which to build the joints ------------------------------------------------------------
                if int_count == 1:
                    l_pos = [ mc.pointPosition(mi_crv.getComponents('cv')[0], w = True)]
                else:
                    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
                    except Exception,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(self._str_reportStart,error)       
                d_buildCurves[k]['l_pos'] = l_pos#Store it
                log.debug("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
                ml_jointBuffer = []
                ml_endJoints = []
                ml_cheekJoints = []
                int_lenMax = len(l_pos)
                for i,pos in enumerate(l_pos):
                    try:#Create and name
                        self.progressBar_set(status = "Creating '%s' %s"%(k,i), progress = i, maxValue = int_lenMax)						    

                        mc.select(cl=True)
                        mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject', setClass=True )
                        mi_jnt.parent = False
                        mi_jnt.addAttr('cgmName',"uprCheek",lock=True)		    			
                        mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
                        mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
                        mi_jnt.doName()
                        ml_jointBuffer.append(mi_jnt)
                        ml_cheekJoints.append(mi_jnt)
                        self.ml_moduleJoints.append(mi_jnt)			
                        ##log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_cheekJoints]))
                    except Exception,error:
                        raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
                    try:#Orient
                        constraintBuffer = mc.normalConstraint(self.str_skullPlate,mi_jnt.mNode, weight = 1, aimVector = self.v_aim, upVector = self.v_up, worldUpType = 'scene' )
                        mc.delete(constraintBuffer)
                        mi_jnt.parent = self.str_rootJoint
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)       
                    try:#freeze
                        jntUtils.metaFreezeJointOrientation(mi_jnt)
                    except Exception,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
                d_buildCurves[k]['ml_joints'] = ml_cheekJoints #nested list
                #Store it...	    
                self.mi_go._mi_rigNull.msgList_connect("%s_%sJoint"%(k,'uprCheek'),ml_jointBuffer)		
            return True

        def _buildCheek_(self): 
            if not self.mi_helper.buildCheek:
                self.log_warning("buildCheek is off.")
                return True  
            
            int_jointCnt = self.int_cheekCount
            int_loftCnt = self.int_cheekLoftCount

            d_buildCurves = {'left':{'uprCrv':self.mi_leftUprCheekCrv,'maxU':.35,'reverseCurve' : False},
                             'right':{'uprCrv':self.mi_rightUprCheekCrv,'maxU':.35,'reverseCurve' : True}}	
            self.d_cheekCurveBuild = d_buildCurves
            l_posList = []
            for k in d_buildCurves.keys():#Make our left and right joints
                d_buffer = d_buildCurves[k]
                mi_uprCrv = d_buildCurves[k].get('uprCrv')#get instance
                #log.info("%s >>> building joints for %s curve | lofts: %s | count: %s"%(self._str_reportStart,k, int_loftCnt, int_jointCnt))

                #Get our l_pos on which to build the joints ------------------------------------------------------------
                #try:l_posUpr = crvUtils.returnSplitCurveList(mi_uprCrv.mNode,int_jointCnt,rebuildSpans=10)
                #except Exception,error:raise StandardError,"upr split fail | error: %s "%(error) 

                try:l_posLwr = crvUtils.returnSplitCurveList(self.mi_jawLineCrv.mNode,int_jointCnt,rebuildSpans=10, maxU = d_buffer['maxU'], reverseCurve = d_buffer['reverseCurve'] )
                except Exception,error:raise StandardError,"lwr split fail | error: %s "%(error)   

                str_lwrCurve = mc.curve (d=1, p = l_posLwr , os=True)
                str_loft = mc.loft([mi_uprCrv.mNode,str_lwrCurve],uniform = True,degree = 1,ss = 1)[0]

                try:#loft split
                    str_bufferUV = mc.ls("%s.u[*][*]"%str_loft)[0]
                    log.debug("%s >> u list : %s"%(self._str_reportStart,str_bufferUV))       		
                    l_splitBuffer = str_bufferUV.split('][')
                    str_bufferU  = l_splitBuffer[0]
                    str_bufferV = l_splitBuffer[1]
                    f_maxU = float(str_bufferU.split(':')[-1])
                    f_maxV = float(str_bufferV.split(':')[-1].split(']')[0])
                    log.debug("maxU : %s | maxV: %s"%(f_maxU,f_maxV))

                    l_uValues = cgmMath.returnSplitValueList(0,f_maxU,1)
                    l_vValues = cgmMath.returnSplitValueList(0,f_maxV,int_jointCnt+1)
                    #log.info("l_uValues : %s "%(l_uValues))
                    #log.info("l_vValues : %s "%(l_vValues))
                    l_pos = []
                    for v in l_vValues[:-1]:
                        l_pos.append(mc.pointPosition("%s.uv[%s][%s]"%(str_loft,l_uValues[0],v)))
                    mc.delete(str_loft,str_lwrCurve)
                except Exception,error:raise StandardError,"loft split fail | error: %s "%(error)   

                d_buildCurves[k]['l_pos'] = l_pos#Store it
                #log.info("%s >>> '%s' pos list: %s"%(self._str_reportStart,k, l_pos))
                ml_jointBuffer = []
                ml_endJoints = []
                ml_cheekJoints = []
                int_lenMax = len(l_pos)
                for i,pos in enumerate(l_pos):
                    try:#Create and name
                        self.progressBar_set(status = "Creating '%s' %s"%(k,i), progress = i, maxValue = int_lenMax)						    
                        mc.select(cl=True)
                        mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject', setClass=True )
                        mi_jnt.parent = False
                        mi_jnt.addAttr('cgmName',"cheek",lock=True)		    			
                        mi_jnt.addAttr('cgmDirection',"%s"%(k),lock=True)		    
                        mi_jnt.addAttr('cgmIterator',i,lock=True,hidden=True)			
                        mi_jnt.doName()
                        ml_jointBuffer.append(mi_jnt)
                        ml_cheekJoints.append(mi_jnt)
                        self.ml_moduleJoints.append(mi_jnt)			
                        ##log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(self._str_reportStart,k,i,[o.p_nameShort for o in ml_cheekJoints]))
                    except Exception,error:
                        raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
                    try:#Snap
                        Snap.go(mi_jnt,self.str_skullPlate,snapToSurface=True)	
                    except Exception,error:
                        raise StandardError,"snap to mesh | pos count: %s | error: %s "%(k,i,error)       
                try:#Orienting -------------------------------------------------------------------------
                    str_mirror = False
                    str_direction = k		    
                    ##log.info("%s direction: %s"%(self._str_reportStart,str_direction))
                    ##log.info("%s joints: %s"%(self._str_reportStart,[mJnt.p_nameShort for mJnt in ml_joints]))	
                    int_lenMax = len(ml_jointBuffer)
                    mi_upObj = self.md_moduleJoints['jaw']			
                    for i,mi_jnt in enumerate(ml_jointBuffer):
                        self.progressBar_set(status = "Orienting %s '%s'"%(str_direction,i), progress = i, maxValue = int_lenMax)						    								    
                        if i == 0:
                            mi_aimObj = ml_jointBuffer[i+1]
                            if str_direction == 'right':
                                str_mirror = 'left'
                                v_aim = self.v_out
                            else:
                                str_mirror = 'right'
                                v_aim = self.v_outNegative				    
                        else:
                            mi_aimObj = ml_jointBuffer[i-1]
                            if str_direction == 'right':
                                str_mirror = 'left'
                                v_aim = self.v_outNegative
                            else:
                                str_mirror = 'right'
                                v_aim = self.v_out				    
                        ##log.info("%s aiming '%s' @ '%s' | up: '%s'"%(self._str_reportStart,mi_jnt.p_nameShort,mi_aimObj.p_nameShort,mi_upObj.p_nameShort))									    
                        mc.delete( mc.aimConstraint(mi_aimObj.mNode, mi_jnt.mNode,
                                                    weight = 1, aimVector = v_aim, upVector = self.v_aimNegative,
                                                    worldUpObject = mi_upObj.mNode, worldUpType = 'object' ) )			    

                        mi_jnt.parent = self.str_rootJoint
                        jntUtils.metaFreezeJointOrientation(mi_jnt)		    
                except Exception,error:raise StandardError,"[%s orient fail]{%s}"%(k,error) 		
                d_buildCurves[k]['ml_joints'] = ml_cheekJoints #nested list
                #Store it...	    
                self.mi_go._mi_rigNull.msgList_connect("%s_%sJoint"%(k,'cheek'),ml_cheekJoints)				
            return True

        def _connect_(self): 
            log.info("%s len - %s"%(self._str_reportStart,len(self.ml_moduleJoints)))	    
            #for mi_jnt in self.ml_moduleJoints:
                #log.info("'%s'"%(mi_jnt.p_nameShort))
            self.mi_go._mi_rigNull.msgList_connect('moduleJoints','rigNull',self.ml_moduleJoints)
            self.mi_go._mi_rigNull.msgList_connect('skinJoints',self.ml_moduleJoints)	    
            return True

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()  



def build_limbSkeleton(*args, **kws):
    class fncWrap_build_limbTemplate(modUtils.skeletonizeStep):
        def __init__(self,*args, **kws):
            super(fncWrap_build_limbTemplate, self).__init__(*args, **kws)
            self._str_funcName = 'build_limbSkeleton({0})'.format(self.d_kws['goInstance']._strShortName)	
            self.__dataBind__(*args, **kws)
            self._b_ExceptionInterupt = True
            self._b_autoProgressBar = True
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Validate','call':self._step_validate},
                                {'step':'Parent Check','call':self._step_parentCheck},
                                {'step':'Initial Creation','call':self._step_initialCreation},
                                {'step':'Naming','call':self._step_naming},
                                {'step':'Orient','call':self._step_orientInitial},
                                {'step':'Flagging','call':self._step_jointFlags},
                                #{'step':'Parent','call':self._step_parentObjects},
                                ]
            #=================================================================
            #self.l_strSteps = ['Start','template objects','curve','root control','helpers']

        def _step_validate(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)

            try:#Gather limb specific data and check
                #========================================================================
                pass
            except Exception,error:raise Exception,"Gather info fail | {0} ".format(error)

            # Get our base info
            #==================	        	    
            self.str_curve = mi_go._mi_curve.mNode
            self.l_limbJoints = []

            #>>> Check roll joint args
            rollJoints = mi_go._mi_templateNull.rollJoints
            self.d_rollJointOverride = mi_go._mi_templateNull.rollOverride
            if type(self.d_rollJointOverride) is not dict:
                self.d_rollJointOverride = False


        def _step_parentCheck(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)

            try:#>>> See if we have have a suitable parent joint to use
                # We'll know it is if the first template position shares an equivalent position with it's parentModule
                #======================================================
                self.mi_parentJointToUse = False

                pos = distance.returnWorldSpacePosition( mi_go._ml_controlObjects[0].mNode )
                self.log_debug("pos: %s"%pos)

                #Get parent position, if we have one
                if mi_go._mi_module.getMessage('moduleParent'):
                    self.log_debug("Found moduleParent, checking joints...")
                    self.mi_parentRigNull = mi_go._mi_module.moduleParent.rigNull
                    self.l_parentJoints = self.mi_parentRigNull.msgList_get('moduleJoints',asMeta=False)
                    if self.l_parentJoints:
                        parent_pos = distance.returnWorldSpacePosition( self.l_parentJoints[-1] )
                        self.log_debug("parentPos: %s"%parent_pos)  

                    self.log_debug("Equivalent: %s"%cgmMath.isVectorEquivalent(pos,parent_pos))
                    if cgmMath.isVectorEquivalent(pos,parent_pos):#if they're equivalent
                        self.mi_parentJointToUse = cgmMeta.asMeta(self.l_parentJoints[-1],'cgmObject')

            except Exception,error:raise Exception,"Parent check fail | {0} ".format(error)

        def _step_initialCreation(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)

            #>>> Make if our segment only has one handle
            #==========================================	
            mi_go.b_parentStole = False
            if len(mi_go._ml_controlObjects) == 1:
                try:
                    if self.mi_parentJointToUse:
                        self.log_debug("Single joint: moduleParent mode")
                        #Need to grab the last joint for this module
                        self.l_limbJoints = [self.l_parentJoints[-1]]
                        self.mi_parentRigNull.msgList_connect('moduleJoints',self.l_parentJoints[:-1],'rigNull')
                        mi_go.b_parentStole = True	    
                    else:
                        self.log_debug("Single joint: no parent mode")
                        self.l_limbJoints.append ( mc.joint (p=(pos[0],pos[1],pos[2]))) 
                except Exception,error:raise Exception,"Single object mode fail | {0} ".format(error)
            else:
                try:
                    if self.mi_parentJointToUse:
                        self.log_debug("Stealing parent joint : {0} | will no longer exist".format(self.mi_parentJointToUse.mNode))
                        #We're going to reconnect all but the last joint back to the parent module and delete the last parent joint which we're replacing
                        self.mi_parentRigNull.msgList_connect('moduleJoints',self.l_parentJoints[:-1],'rigNull')
                        mc.delete(self.mi_parentJointToUse.mNode)
                        mi_go.b_parentStole = True

                    #>>> Make the limb segment
                    #==========================
                    try:#>> Get U Positions
                        l_spanUPositions = []
                        #>>> Divide stuff
                        for i_obj in mi_go._ml_controlObjects:#These are our base span u positions on the curve
                            l_spanUPositions.append(distance.returnNearestPointOnCurveInfo(i_obj.mNode,self.str_curve)['parameter'])
                        l_spanSegmentUPositions = lists.parseListToPairs(l_spanUPositions)
                        #>>>Get div per span
                        l_spanDivs = mi_go._mi_module.get_rollJointCountList() or []

                        self.log_debug("l_spanSegmentUPositions: %s"%l_spanSegmentUPositions)
                        self.log_debug("l_spanDivs: %s"%l_spanDivs)	    
                    except Exception,error:raise Exception,"Get U Positions fail | {0} ".format(error)

                    try:#>>>Get div per span 
                        _str_subFunc = "initial Joint creation"

                        l_jointUPositions = []
                        for i,segment in enumerate(l_spanSegmentUPositions):#Split stuff up
                            #Get our span u value distance
                            length = segment[1]-segment[0]
                            div = length / (l_spanDivs[i] +1)
                            tally = segment[0]
                            l_jointUPositions.append(tally)
                            for i in range(l_spanDivs[i] +1)[1:]:
                                tally = segment[0]+(i*div)
                                l_jointUPositions.append(tally)
                        l_jointUPositions.append(l_spanUPositions[-1])

                        l_jointPositions = []
                        for u in l_jointUPositions:
                            l_jointPositions.append(mc.pointPosition("%s.u[%f]"%(self.str_curve,u)))


                        #>>> Remove the duplicate positions"""
                        l_jointPositions = lists.returnPosListNoDuplicates(l_jointPositions)
                        #>>> Actually making the joints
                        for pos in l_jointPositions:
                            self.l_limbJoints.append ( mc.joint (p=(pos[0],pos[1],pos[2]))) 
                    except Exception,error:raise Exception,"Get U Positions fail | {0} ".format(error)
                except Exception,error:raise Exception,"regular segment mode fail | {0} ".format(error)

        def _step_naming(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)	    
            """ 
	    Copy naming information from template objects to the joints closest to them
	    copy over a cgmNameModifier tag from the module first
	    """
            ml_handleJoints = []
            try:#>>>First we need to find our matches
                _str_subFunc = "Find matches"	
                self.log_debug("Finding matches from module controlObjects")
                for mObj in mi_go._ml_controlObjects:
                    closestJoint = distance.returnClosestObject(mObj.mNode,self.l_limbJoints)
                    idx = self.l_limbJoints.index(closestJoint)
                    #transferObj = attributes.returnMessageObject(obj,'cgmName')
                    """Then we copy it"""
                    attributes.copyUserAttrs(mObj.mNode,closestJoint,attrsToCopy=['cgmPosition','cgmNameModifier','cgmDirection','cgmName'])
                    mi_go._d_handleToHandleJoints[mObj] = idx
                    mObj.connectChildNode(closestJoint,'handleJoint')
                    ml_handleJoints.append(cgmMeta.asMeta(closestJoint))
            except Exception,error:raise Exception,"Match find fail | {0} ".format(error)

            try:#>>>If we stole our parents anchor joint, we need to to reconnect it
                if mi_go.b_parentStole:
                    mi_parentControl = mi_go._mi_module.moduleParent.templateNull.msgList_get('controlObjects')[-1]
                    self.log_debug("parentControl: %s"%mi_parentControl.getShortName())
                    closestJoint = distance.returnClosestObject(mi_parentControl.mNode,self.l_limbJoints)	
                    mi_parentControl.connectChildNode(closestJoint,'handleJoint')
            except Exception,error:raise Exception,"Stolen parent repair fail | {0} ".format(error)


            try:#>>>Store it
                mi_go._mi_rigNull.msgList_connect('moduleJoints',self.l_limbJoints,'rigNull')
            except Exception,error:raise Exception,"Store msgList fail | {0} ".format(error)

            #>>>Store these joints and rename the heirarchy
            try:#Metaclassing our objects
                ii = 1
                ml_moduleJoints = [cgmMeta.asMeta(o,'cgmObject',setClass=True) for o in self.l_limbJoints]
                for i,mObj in enumerate(ml_moduleJoints):
                    mObj.addAttr('d_jointFlags', '{}',attrType = 'string', lock=True, hidden=True) 
                    if mObj in ml_handleJoints:
                        ii = 1
                    elif mObj.parent in ml_handleJoints:
                        mObj.addAttr('cgmIterator',ii,lock=True,hidden=True)
                        mObj.addAttr('cgmNameModifier',value = 'roll')
                        ii +=1
                    else:
                        mObj.addAttr('cgmIterator',ii,lock=True,hidden=True) 
                        mObj.addAttr('cgmNameModifier',value = 'roll')                        
                        ii +=1                        
                    """if not mObj.hasAttr('cgmName'):
                        if not mObj.hasAttr('cgmIterator'):
                            mObj.addAttr('cgmIterator',ii,lock=True,hidden=True) 
                            ii+=1
                        else:
                            ii = mObj.cgmIterator =1
                    else:
                        ii = 2"""
                    mObj.doName()
            except Exception,error:raise Exception,"Joint flag/metaing fail | {0} ".format(error)

            self.ml_moduleJoints = ml_moduleJoints

        def _step_orientInitial(self):
            try:
                mi_go = self._go
                ml_moduleJoints = self.ml_moduleJoints
                mi_go.ml_moduleJoints = ml_moduleJoints#...push	    
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)	 

            try:doOrientSegment(mi_go)
            except Exception,error:raise Exception,"Segment orientation failed: %s"%error    

        def _step_jointFlags(self):
            try:
                mi_go = self._go
                ml_moduleJoints = self.ml_moduleJoints	
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)	 
            l_moduleJoints = [i_j.mNode for i_j in ml_moduleJoints]#store

            #>>> Set its radius and toggle axis visbility on
            """jointSize = (distance.returnDistanceBetweenObjects (l_moduleJoints[0],
                                                                l_moduleJoints[-1])/len(l_moduleJoints))"""
            attributes.doMultiSetAttr(l_moduleJoints,'radi',1)

            #>>> Flag our handle joints
            #===========================
            ml_handles = []
            ml_handleJoints = []
            for i_obj in mi_go._ml_controlObjects:
                if i_obj.hasAttr('handleJoint'):
                    #d_buffer = i_obj.handleJoint.d_jointFlags
                    #d_buffer['isHandle'] = True
                    #i_obj.handleJoint.d_jointFlags = d_buffer
                    ml_handleJoints.append(i_obj.handleJoint)

            mi_go._mi_rigNull.msgList_connect('handleJoints',ml_handleJoints,'rigNull')
            mi_go._mi_rigNull.msgList_connect('skinJoints',ml_moduleJoints) 

            return True 
    return fncWrap_build_limbTemplate(*args, **kws).go()



def doOrientSegment(*args, **kws):
    class fncWrap_doOrientSegment(modUtils.skeletonizeStep):
        def __init__(self,*args, **kws):
            super(fncWrap_doOrientSegment, self).__init__(*args, **kws)
            self._str_funcName = 'doOrientSegment({0})'.format(self.d_kws['goInstance']._strShortName)	
            self.__dataBind__(*args, **kws)
            self._b_autoProgressBar = True
            self._b_reportTimes = True
            self._b_ExceptionInterupt = True
            self.l_funcSteps = [{'step':'Validate','call':self._step_validate},
                                {'step':'Main orient pass','call':self._step_mainOrient},
                                {'step':'Parent connect','call':self._step_connectToParent},	                        
                                {'step':'Freeze Orientation','call':self._step_freeze},
                                {'step':'Speical case','call':self._step_specialCase},
                                ]
            #=================================================================
            #self.l_strSteps = ['Start','template objects','curve','root control','helpers']

        def _step_validate(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)

            try:self.ml_moduleJoints = mi_go.ml_moduleJoints
            except:
                self.log_info("Initialing module joints...")
                self.ml_moduleJoints = self._mi_rigNull.msgList_get('moduleJoints',asMeta = True)
            try:self.l_moduleJoints = mi_go.l_moduleJoints
            except:
                self.log_info("Initialing joints list...")
                self.l_moduleJoints = [mJnt.p_nameShort for mJnt in self.ml_moduleJoints]   


            try:#>>> orientation vectors
                #=======================    
                self.orientationVectors = search.returnAimUpOutVectorsFromOrientation(mi_go.str_jointOrientation)
                self.wantedAimVector = self.orientationVectors[0]
                self.wantedUpVector = self.orientationVectors[1]  
                self.log_debug("self.wantedAimVector: %s"%self.wantedAimVector)
                self.log_debug("self.wantedUpVector: %s"%self.wantedUpVector)
            except Exception,error:raise Exception,"orientation vectors fail | {0} ".format(error)

            #>>> Put objects in order of closeness to root
            #l_limbJoints = distance.returnDistanceSortedList(l_limbJoints[0],l_limbJoints)

        def _step_mainOrient(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)

            #>>> Segment our joint list by cgmName, prolly a better way to optimize this
            l_cull = copy.copy(self.l_moduleJoints)
            if len(l_cull)==1:
                try:
                    self.log_debug('Single joint orient mode')
                    helper = mi_go._mi_templateNull.orientRootHelper.mNode
                    if helper:
                        self.log_debug("helper: %s"%helper)
                        constBuffer = mc.orientConstraint( helper,l_cull[0],maintainOffset = False)
                        mc.delete (constBuffer[0])  
                        #Push rotate to jointOrient
                        i_jnt = cgmMeta.asMeta(l_cull[0],'cgmObject')
                except Exception,error:raise Exception,"Single joint orient fail | {0} ".format(error)

            else:#Normal mode
                try:
                    self.log_debug('Normal orient mode')        
                    mi_go.l_jointSegmentIndexSets= []
                    while l_cull:
                        matchTerm = search.findRawTagInfo(l_cull[0],'cgmName')
                        buffer = []
                        objSet = search.returnMatchedTagsFromObjectList(l_cull,'cgmName',matchTerm)
                        for o in objSet:
                            buffer.append(self.l_moduleJoints.index(o))
                        mi_go.l_jointSegmentIndexSets.append(buffer)
                        for obj in objSet:
                            l_cull.remove(obj)

                    #>>> un parenting the chain
                    for i,mJnt in enumerate(self.ml_moduleJoints):
                        if i != 0:
                            mJnt.parent = False
                        mJnt.displayLocalAxis = 1#tmp
                        try:
                            mJnt.rotateOrder = mi_go.str_jointOrientation
                        except Exception,error:
                            log.error("doOrientSegment>>rotate order set fail: %s"%mJnt.getShortName())

                    #>>>per segment stuff
                    assert len(mi_go.l_jointSegmentIndexSets) == len(mi_go._mi_module.coreNames.value)#quick check to make sure we've got the stuff we need
                    cnt = 0
                    self.log_info("Segment Index sets: %s"%mi_go.l_jointSegmentIndexSets)
                    for cnt,segment in enumerate(mi_go.l_jointSegmentIndexSets):#for each segment
                        try:
                            self.log_debug("On segment: %s"%segment)
                            try:
                                lastCnt = len(mi_go.l_jointSegmentIndexSets)-1
                                segmentHelper = mi_go._ml_controlObjects[cnt].getMessage('helper')[0]
                                helperObjectCurvesShapes =  mc.listRelatives(segmentHelper,shapes=True,path = True)
                                upLoc = locators.locMeCvFromCvIndex(helperObjectCurvesShapes[0],30)   
                            except Exception,error: 
                                raise Exception,"Initial data | error: {0}".format(error)
                            
                            if not mc.objExists(segmentHelper) and search.returnObjectType(segmentHelper) != 'nurbsCurve':
                                raise StandardError,"doOrientSegment>>> No helper found"

                            if cnt != lastCnt:
                                #>>> Create our up object from from the helper object 
                                #>>> make a pair list
                                #pairList = lists.parseListToPairs(segment)
                                """for pair in pairList:
				    constraintBuffer = mc.aimConstraint(self.ml_moduleJoints[pair[1]].mNode,self.ml_moduleJoints[pair[0]].mNode,maintainOffset = False, weight = 1, aimVector = self.wantedAimVector, upVector = self.wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
				    mc.delete(constraintBuffer[0])"""
                                for index in segment:
                                    if index != 0:
                                        self.ml_moduleJoints[index].parent = self.ml_moduleJoints[index-1].mNode
                                    self.ml_moduleJoints[index].rotate  = [0,0,0]			
                                    self.ml_moduleJoints[index].jointOrient  = [0,0,0]	

                                    #self.log_debug("%s aim to %s"%(self.ml_moduleJoints[index].mNode,self.ml_moduleJoints[index+1].mNode))
                                    constraintBuffer = mc.aimConstraint(self.ml_moduleJoints[index+1].mNode,self.ml_moduleJoints[index].mNode,maintainOffset = False, weight = 1, aimVector = self.wantedAimVector, upVector = self.wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
                                    mc.delete(constraintBuffer[0])

                                    #Push rotate to jointOrient
                                    #self.ml_moduleJoints[index].jointOrient = self.ml_moduleJoints[index].rotate
                                    #self.ml_moduleJoints[index].rotate = [0,0,0]

                                mc.delete(upLoc)
                                #>>>  Increment and delete the up loc """
                            else:
                                self.log_debug(">>> Last count")
                                #>>> Make an aim object and move it """
                                mJnt = self.ml_moduleJoints[segment[-1]]
                                self.log_debug(mJnt.getShortName())
                                mJnt.parent = self.ml_moduleJoints[segment[-1]-1].mNode
                                mJnt.jointOrient  = [0,0,0]
                                #self.ml_moduleJoints[index].rotate  = [0,0,0]					

                                aimLoc = locators.locMeObject(segmentHelper)
                                aimLocGroup = rigging.groupMeObject(aimLoc)
                                mc.move (0,0,10, aimLoc, localSpace=True)
                                constraintBuffer = mc.aimConstraint(aimLoc,mJnt.mNode,maintainOffset = False, weight = 1, aimVector = self.wantedAimVector, upVector = self.wantedUpVector, worldUpVector = [0,1,0], worldUpObject = upLoc, worldUpType = 'object' )
                                mc.delete(constraintBuffer[0])
                                mc.delete(aimLocGroup)
                                mc.delete(upLoc)

                        except Exception,error:
                            self.log_error("ml_moduleJoints = {0}".format(self.ml_moduleJoints))
                            raise Exception,"Segment fail| cnt: {0} | segment: {1}| error: {2} ".format(cnt,segment,error)

                    try:#>>>Reconnect the joints
                        for cnt,mJnt in enumerate(self.ml_moduleJoints[1:]):#parent each to the one before it
                            mJnt.parent = self.ml_moduleJoints[cnt].mNode
                            cgmMeta.cgmAttr(mJnt,"inverseScale").doConnectIn("%s.scale"%mJnt.parent)
                    except Exception,error: 
                        raise Exception,"Reconnect fail | error: {0}".format(error)
                except Exception,error:raise Exception,"Normal mode orient fail | {0} ".format(error)

            if mi_go._mi_module.moduleType in ['foot']:
                self.log_debug("Special case orient")
                if len(self.ml_moduleJoints) > 1:
                    helper = mi_go._mi_templateNull.orientRootHelper.mNode
                    if helper:
                        self.log_debug("Root joint fix...")                
                        rootJoint = self.ml_moduleJoints[0]
                        self.ml_moduleJoints[1].parent = False #unparent the first child
                        constBuffer = mc.orientConstraint( helper,rootJoint,maintainOffset = False)
                        mc.delete (constBuffer[0])   
                        self.ml_moduleJoints[1].parent = rootJoint
                        self.ml_moduleJoints[1].jointOrient = self.ml_moduleJoints[1].rotate
                        self.ml_moduleJoints[1].rotate = [0,0,0]        

            # 
        def _step_connectToParent(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)

            #Connect to parent
            try:
                connectToParentModule(mi_go._mi_module)    
            except Exception,error:raise Exception, "Failed to connect to module parent | error: {0}".format(error)
        def _step_freeze(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)

            #""" Freeze the rotations """
            try:
                jntUtils.metaFreezeJointOrientation(self.ml_moduleJoints) 
            except Exception,error:
                raise Exception,"Failed to freeze rotations | %s"%error

        def _step_specialCase(self):
            try:mi_go = self._go
            except Exception,error:raise Exception,"bring data local fail | {0} ".format(error)

            for i,mJnt in enumerate(self.ml_moduleJoints):
                self.log_debug(mJnt.getMayaAttr('cgmName'))
                if mJnt.getMayaAttr('cgmName') in ['ankle']:
                    self.log_debug("Copy orient from parent mode: %s"%mJnt.getShortName())
                    joints.doCopyJointOrient(mJnt.parent,mJnt.mNode)

            return True	    
    return fncWrap_doOrientSegment(*args, **kws).go()


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def deleteSkeleton(*args,**kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args,**kws):
            """
            """
            try:mModule = kws['mModule']
            except:
                try:mModule = args[0]
                except:pass	    

            super(fncWrap, self).__init__(*args, **kws)
            self._mi_module = mModule
            self._str_moduleName = mModule.p_nameShort
            self._str_funcName= "deleteSkeleton('%s')"%self._str_moduleName	
            self.__dataBind__(*args,**kws)		    	    	    
            #=================================================================
        def __func__(self):
            try:#Query ========================================================
                mi_module = self._mi_module
                kws = self.d_kws		
                ml_skinJoints = mi_module.rig_getSkinJoints(asMeta = True)
                l_skinJoints = [i_j.p_nameLong for i_j in ml_skinJoints if i_j ]  		
            except Exception,error:raise StandardError,"[Query]{%s}"%error

            #We need to see if any of or moduleJoints have children
            l_strayChildren = []
            l_safeToDeleteChildren = []
            for i_jnt in ml_skinJoints:
                buffer = i_jnt.getChildren(True)
                for c in buffer:
                    if c not in l_skinJoints:
                        try:
                            i_c = cgmMeta.asMeta(c,'cgmObject')
                            i_c.parent = False
                            l_strayChildren.append(i_c.mNode)
                            if not i_c.getMessage('rigNull'):
                                self.log_warning("Deleting non connected stray child: '{0}'".format(i_c.p_nameShort))
                                mc.delete(i_c.mNode)
                        except Exception,error:
                            self.log_warning(error)     

            self.log_info("l_strayChildren: %s"%l_strayChildren)    
            mi_module.msgList_purge('skinJoints')
            mi_module.msgList_purge('moduleJoints')
            mi_module.msgList_purge('handleJoints')
            if l_skinJoints:
                mc.delete(l_skinJoints)
            else:return False	    
            return True
    return fncWrap(*args,**kws).go()


def connectToParentModule(self):
    """
    Pass a module class. Constrains template root to parent's closest template object
    """
    try:
        log.debug(">>> %s.connectToParentModule >> "%self.p_nameShort + "="*75)  
        try:
            l_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta=False) 

            if self._UTILS.isRootModule(self):
                log.info("NEED TO CONNECT TO PUPPET")
                try:
                    rigging.doParentReturnName(l_moduleJoints[0],self.modulePuppet.masterNull.skeletonGroup.mNode)		
                except Exception,error:raise Exception,"root module parent fail | {0} ".format(error)

            else:
                l_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta = False) 

                if not self.getMessage('moduleParent'):
                    return False
                else:
                    #>>> Get some info
                    i_rigNull = self.rigNull #Link
                    i_parent = self.moduleParent #Link
                    if i_parent.isSkeletonized():#>> If we have a module parent
                        #>> If we have another anchor
                        if self.moduleType == 'eyelids':
                            str_targetObj = i_parent.rigNull.msgList_get('moduleJoints',asMeta = False)[0]
                            for jnt in l_moduleJoints:
                                #mJoint.parent = str_targetObj
                                rigging.doParentReturnName(jnt,str_targetObj)

                        else:
                            l_parentSkinJoints = i_parent.rigNull.msgList_get('moduleJoints',asMeta = False)
                            str_targetObj = distance.returnClosestObject(l_moduleJoints[0],l_parentSkinJoints)
                            rigging.doParentReturnName(l_moduleJoints[0],str_targetObj)		
                    else:
                        log.error("Parent has not been skeletonized...")           
                        return False  
                return True
        except Exception,error:
            if not self.isSkeletonized():
                log.error("Must be skeletonized to contrainToParentModule: '%s' "%self.getShortName())
            raise Exception,error	
    except Exception,error:raise Exception,"connectToParentModule fail | {0} ".format(error)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  

def skeletonizeCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Skeletonizes a character

    ARGUMENTS:
    masterNull(string)

    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = modules.returnModules(masterNull)
    orderedModules = modules.returnOrderedModules(modules)
    #>>> Do the spine first
    stateCheck = modules.moduleStateCheck(orderedModules[0],['template'])
    if stateCheck == 1:
        spineJoints = skeletonize(orderedModules[0])
    else:
        print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

    #>>> Do the rest
    for module in orderedModules[1:]:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck == 1:
            templateNull = modules.returnTemplateNull(module)
            root =  modules.returnInfoNullObjects(module,'templatePosObjects',types='templateRoot')

            #>>> See if our item has a non default anchor
            anchored = storeTemplateRootParent(module) 
            if anchored == True:
                anchor =  attributes.returnMessageObject(root[0],'skeletonParent')
                closestJoint = distance.returnClosestObject(anchor,spineJoints)
            else:
                closestJoint = distance.returnClosestObject(root[0],spineJoints) 

            l_limbJoints = skeletonize(module)
            rootName = rigging.doParentReturnName(l_limbJoints[0],closestJoint)
            print rootName
        else:
            print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def skeletonStoreCharacter(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    stores a skeleton of a character

    ARGUMENTS:
    masterNull(string)

    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = modules.returnModules(masterNull)
    orderedModules = modules.returnOrderedModules(modules)
    #>>> Do the spine first
    stateCheck = modules.moduleStateCheck(orderedModules[0],['template'])
    if stateCheck == 1:
        spineJoints = modules.saveTemplateToModule(orderedModules[0])
    else:
        print ('%s%s' % (module,' has already been skeletonized. Moving on...'))

    #>>> Do the rest
    for module in orderedModules[1:]:
        stateCheck = modules.moduleStateCheck(module,['template'])
        if stateCheck == 1:
            templateNull = modules.returnTemplateNull(module)        
            modules.saveTemplateToModule(module)
        else:
            print ('%s%s' % (module,' has already been skeletonized. Moving on...'))



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>            

def storeTemplateRootParent(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Stores the template root parent to the root control if there is a new one

    ARGUMENTS:
    moduleNull(string)

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    templateNull = modules.returnTemplateNull(moduleNull)
    root =   modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    parent = search.returnParentObject(root, False)
    if parent != templateNull:
        if parent != False:
            attributes.storeObjectToMessage(parent,root,'skeletonParent')
            return True
    return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
#>>> Tools    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>