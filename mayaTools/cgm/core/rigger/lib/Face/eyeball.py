"""
------------------------------------------
cgm.core.rigger: Face.eyeball
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

eyeball rig builder
================================================================
"""
__version__ = 'faceAlpha2.02042014'

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
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.core.lib import meta_Utils as metaUtils
reload(metaUtils)
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils
reload(rUtils)
from cgm.lib import (attributes,
                     joints,
                     skinning,
                     lists,
                     dictionary,
                     distance,
                     modules,
                     search,
                     curves,
                     )

#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints']   
def __bindSkeletonSetup__(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    log.info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "-"*75)            
    try:
        if not self._cgmClass == 'JointFactory.go':
            log.error("Not a JointFactory.go instance: '%s'"%self)
            raise StandardError

    except Exception,error:
        log.error("eyeball.__bindSkeletonSetup__>>bad self!")
        raise StandardError,error

    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
    if not self._mi_module.isSkeletonized():
        raise StandardError, "%s is not skeletonized yet."%self._strShortName
    try:
        self._mi_module.rig_getReport()#report	
    except Exception,error:
        log.error("build_eyeball>>__bindSkeletonSetup__ fail!")
        raise StandardError,error   

def build_rigSkeleton(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
            self._b_autoProgressBar = True
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Gather Info','call':self.gatherInfo},
                                {'step':'Rig Joints','call':self.build_rigJoints},
                                {'step':'Connections','call':self.build_connections}
                                ]	
            #=================================================================

        def gatherInfo(self):
            mi_go = self._go#Rig Go instance link    
            self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise StandardError,"No suitable helper found"

        def build_rigJoints(self):
            #We'll have a rig joint for every joint
            mi_go = self._go#Rig Go instance link
            ml_rigJoints = mi_go.build_rigChain()	
            ml_rigJoints[0].parent = False
            self.ml_rigJoints = ml_rigJoints

        def build_connections(self):    
            #ml_jointsToConnect = []
            #ml_jointsToConnect.extend(self.ml_rigJoints)   
            mi_go = self._go#Rig Go instance link	    
            mi_go.connect_toRigGutsVis(self.ml_rigJoints)
    return fncWrap(*args, **kws).go()    

#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['eyeballFK','eyeballIK','settings']}

def build_shapes(self):
    """
    """ 
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise StandardError
    except Exception,error:
        log.error("eyeball.build_rig>>bad self!")
        raise StandardError,error

    _str_funcName = "build_shapes(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)   

    if self._i_templateNull.handles > 3:
        raise StandardError, "%s >>> Too many handles. don't know how to rig"%(_str_funcName)    

    if not self.isRigSkeletonized():
        raise StandardError, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._strShortName)	

    #>>>Build our Shapes
    #=============================================================
    try:
        mShapeCast.go(self._mi_module,['eyeball'], storageInstance=self)#This will store controls to a dict called    

    except Exception,error:
        log.error("build_eyeball>>Build shapes fail!")
        raise StandardError,error 
    return True

#>>> Controls
#===================================================================
def build_controls(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_controls(%s)'%self.d_kws['goInstance']._strShortName
            self._b_autoProgressBar = True	
            self._b_reportTimes = True	    	    
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
                                {'step':'Build Groups','call':self._buildGroups_},
                                {'step':'Build Controls','call':self._buildControls_},
                                {'step':'Build Pupil/Iris','call':self._buildPupilIris_},	                        
                                {'step':'Build Connections','call':self._buildConnections_}	                        
                                ]	
            #=================================================================

        def _gatherInfo_(self):
            mi_go = self._go#Rig Go instance link
            self.md_rigList = {}
            self.str_mirrorSide = mi_go.verify_mirrorSideArg(mi_go._direction)#Get the mirror side, shakes fist @ "Centre"

            self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise StandardError,"No suitable helper found"

            if not mi_go.isShaped():
                raise StandardError,"Needs shapes to build controls"
            if not mi_go.isRigSkeletonized():
                raise StandardError,"Needs shapes to build controls"

            self.md_rigList['fk_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_eyeballFK'),cgmMeta.cgmObject) 
            self.md_rigList['ik_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_eyeballIK'),cgmMeta.cgmObject) 
            self.md_rigList['settings_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
            self.md_rigList['eyeMove_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_eyeMove'),cgmMeta.cgmObject)     
            self.md_rigList['pupil_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_pupil'),cgmMeta.cgmObject)     
            self.md_rigList['iris_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_iris'),cgmMeta.cgmObject)     

            #>> Find our joint lists ===================================================================
            self.md_jointLists = {}	    
            self.ml_rigJoints = mi_go._mi_module.rigNull.msgList_get('rigJoints')

            self.md_rigList['eyeOrb'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
                                                                              cgmName = 'eyeOrb')[0]    
            self.md_rigList['eye'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
                                                                           cgmName = 'eye')[0]	


            l_pupil = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
                                                            cgmName = 'pupil')
            if l_pupil:
                self.md_rigList['pupil'] = l_pupil[0]	
            else:
                #self.md_rigList['pupil_shape'].delete()
                self.md_rigList['pupil'] = False


            l_iris = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
                                                           cgmName = 'iris')
            if l_iris:
                self.md_rigList['iris'] = l_iris[0]	
            else:
                #self.md_rigList['iris_shape'].delete()
                self.md_rigList['iris'] = False

            #>> Running lists ===========================================================================
            self.ml_directControls = []
            self.ml_controlsAll = []


        def _buildGroups_(self):
            mi_go = self._go#Rig Go instance link

            for grp in ['controlsFKNull','controlsIKNull','eyeTrackNull']:
                i_dup = mi_go._i_constrainNull.doCreateAt(copyAttrs=True)
                i_dup.parent = mi_go._i_constrainNull.mNode
                i_dup.addAttr('cgmTypeModifier',grp,lock=True)
                i_dup.doName()
                mi_go._i_constrainNull.connectChildNode(i_dup,grp,'owner')
                self.md_rigList[grp] = i_dup

        def _buildPupilIris_(self):
            mi_go = self._go#Rig Go instance link
            str_mirrorSide = self.str_mirrorSide

            try:#>>>> Iris pupil #==================================================================	
                try:
                    _l_build = [{'tag':'iris','buildCheck':self.mi_helper.buildIris,'shape':self.md_rigList['iris_shape'],'joint':self.md_rigList['iris'],'parent':self.md_rigList['eye']},
                                {'tag':'pupil','buildCheck':self.mi_helper.buildPupil,'shape':self.md_rigList['pupil_shape'],'joint':self.md_rigList['pupil'],'parent':self.md_rigList['iris']}]
                except Exception,error:raise Exception,"[build dict]{%s}"%(error)

                for _d in _l_build:
                    try:
                        self._d_buffer = _d
                        self.log_infoNestedDict('_d_buffer')
                        _tag = _d['tag']
                        _shape = _d['shape']
                        _joint = _d['joint']
                        _b_buildCheck = _d['buildCheck']

                        if not _b_buildCheck:
                            self.log_info("Build %s toggle: off"%(_tag))
                            _shape.delete()

                        else:
                            _joint.parent =  mi_go._i_constrainNull.eyeTrackNull.mNode
                            d_buffer = mControlFactory.registerControl(_joint,useShape = _shape,
                                                                       mirrorSide = str_mirrorSide, mirrorAxis="",
                                                                       makeAimable=True,setRotateOrder ='zxy') 	    

                            mi_control = d_buffer['instance']
                            _shape.delete()

                            attributes.doSetAttr(mi_control.mNode,'overrideEnabled',0)
                            attributes.doSetAttr(mi_control.mNode,'overrideDisplayType',0)
                            cgmMeta.cgmAttr(mi_control,'radius',.0001,hidden=True)
                            mi_go._i_rigNull.connectChildNode(mi_control,'control%s'%_tag.capitalize(),"rigNull")
                            self.ml_controlsAll.append(mi_control)	
                            attributes.doSetLockHideKeyableAttr(mi_control.mNode,channels=['tx','ty','tz','rx','ry','rz','v','s%s'%mi_go._jointOrientation[0]])				
                    except Exception,error:raise Exception,"[%s]{%s}"%(_tag,error)
            except Exception,error:raise Exception,"[Build iris/pupil fail]{%s}"%(error)


        def _buildControls_(self):
            mi_go = self._go#Rig Go instance link

            try:#Query ====================================================================================
                ml_rigJoints = self.ml_rigJoints

                mi_fkShape = self.md_rigList['fk_shape']
                mi_ikShape = self.md_rigList['ik_shape']
                mi_settingsShape = self.md_rigList['settings_shape']
                mi_eyeMoveShape = self.md_rigList['eyeMove_shape']
                str_mirrorSide = self.str_mirrorSide
            except Exception,error:raise Exception,"[Query]{%s}"%error	


            try:#>>>> FK #==================================================================	
                mi_fkShape.parent = mi_go._i_constrainNull.controlsFKNull.mNode
                i_obj = mi_fkShape
                d_buffer = mControlFactory.registerControl(i_obj,copyTransform = ml_rigJoints[0],
                                                           mirrorSide = str_mirrorSide, mirrorAxis="rotateY,rotateZ",
                                                           makeAimable=True,setRotateOrder ='zxy',typeModifier='fk') 	    
                mi_controlFK = d_buffer['instance']
                mi_controlFK.axisAim = "%s+"%mi_go._jointOrientation[0]
                mi_controlFK.axisUp= "%s+"%mi_go._jointOrientation[1]	
                mi_controlFK.axisOut= "%s+"%mi_go._jointOrientation[2]

                #We're gonna lock the aim rot
                cgmMeta.cgmAttr(mi_controlFK,'r%s'%mi_go._jointOrientation[0], keyable = False, lock=True,hidden=True)
                mi_go._i_rigNull.connectChildNode(mi_controlFK,'controlFK',"rigNull")
                self.ml_controlsAll.append(mi_controlFK)	

                attributes.doSetLockHideKeyableAttr(mi_controlFK.mNode,channels=['tx','ty','tz','sx','sy','sz','v'])				

            except Exception,error:raise Exception,"[Build fk fail]{%s}"%(error)

            try:#>>>> IK 
                #==================================================================	
                mi_ikShape.parent = mi_go._i_constrainNull.controlsIKNull.mNode	
                d_buffer = mControlFactory.registerControl(mi_ikShape,
                                                           mirrorSide = str_mirrorSide, mirrorAxis="",		                                           
                                                           typeModifier='ik',addDynParentGroup=True) 	    
                mi_ikControl = d_buffer['instance']	

                mi_go._i_rigNull.connectChildNode(mi_ikControl,'controlIK',"rigNull")
                self.ml_controlsAll.append(mi_ikControl)
                attributes.doSetLockHideKeyableAttr(mi_ikControl.mNode,channels=['sx','sy','sz','v'])				

            except Exception,error:raise Exception,"[Build ik fail]{%s}"%(error)


            try:#>>>> Settings
                #==================================================================	
                mi_settingsShape.parent = mi_go._i_constrainNull.mNode

                try:#Register the control
                    d_buffer = mControlFactory.registerControl(mi_settingsShape,
                                                               mirrorSide = str_mirrorSide, mirrorAxis="",		                                           		                                               
                                                               makeAimable=False,typeModifier='settings') 
                    mi_settings = d_buffer['instance']
                    mi_go._i_rigNull.connectChildNode(mi_settings,'settings','rigNull')
                    self.ml_controlsAll.append(mi_settings)

                    #>>> Verify out vis controls	    
                    self.mPlug_result_moduleFaceSubDriver = mi_go.build_visSubFace()		    

                except Exception,error:raise StandardError,"registration | %s"%error	

                try:#Set up some attributes
                    attributes.doSetLockHideKeyableAttr(mi_settings.mNode)
                    mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',attrType='float',lock=False,keyable=True,
                                                 minValue=0,maxValue=1.0)
                except Exception,error:raise StandardError,"attribute setup | %s"%error	

            except Exception,error:raise Exception,"[Build Settings fail]{%s}"%(error)

            try:#>>>> eyeMove #==================================================================	
                mi_eyeMoveShape.parent = mi_go._i_constrainNull.mNode

                try:#Register the control
                    d_buffer = mControlFactory.registerControl(mi_eyeMoveShape,
                                                               addMirrorAttributeBridges = [["mirrorIn","t%s"%mi_go._jointOrientation[2]],
                                                                                            ["mirrorBank","r%s"%mi_go._jointOrientation[0]]],
                                                               mirrorSide = str_mirrorSide, mirrorAxis="",		                                               
                                                               makeAimable=False,typeModifier='eyeMove') 
                    mObj = d_buffer['instance']
                    mi_go._i_rigNull.connectChildNode(mObj,'eyeMove','rigNull')
                    self.ml_controlsAll.append(mObj)
                except Exception,error:raise Exception,"[registration]{%s}"%(error)

                try:#Set up some attributes
                    attributes.doSetLockHideKeyableAttr(mObj.mNode,channels = ["r%s"%mi_go._jointOrientation[1],"r%s"%mi_go._jointOrientation[2],'v'])
                except Exception,error:raise Exception,"[Attribute setup]{%s}"%(error)

                try:#Vis Connect
                    for shp in mObj.getShapes():
                        mShp = cgmMeta.cgmNode(shp)
                        mShp.overrideEnabled = 1    
                        self.mPlug_result_moduleFaceSubDriver.doConnectOut("%s.overrideVisibility"%mShp.mNode)
                except Exception,error:raise Exception,"[subVisConnect]{%s}"%(error)


            except Exception,error:raise Exception,"[Build Settings fail]{%s}"%(error)

        def _buildConnections_(self):
            #Register our mirror indices ---------------------------------------------------------------------------------------
            mi_go = self._go#Rig Go instance link	    
            int_start = self._go._i_puppet.get_nextMirrorIndex( mi_go._direction )
            for i,mCtrl in enumerate(self.ml_controlsAll):
                try:mCtrl.addAttr('mirrorIndex', value = (int_start + i))		
                except Exception,error: raise StandardError,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

            try:self._go._i_rigNull.msgList_connect('controlsAll',self.ml_controlsAll)
            except Exception,error: raise StandardError,"[Controls all connect]{%s}"%error	    
            try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
            except Exception,error: raise StandardError,"[Failed to set module objectSet]{%s}"%error

    return fncWrap(*args, **kws).go()

def build_rig(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_rig(%s)'%self.d_kws['goInstance']._strShortName
            self._b_autoProgressBar = True	
            self._b_reportTimes = True	    	    
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
                                {'step':'Setup Eye','call':self._setupEye_},
                                {'step':'Setup DynParent Group','call':self._dynParentGroup_},	  
                                {'step':'Setup Defaults','call':self._setupDefaults_},	                        	                        
                                ]	
            #=================================================================

        def _gatherInfo_(self):
            mi_go = self._go#Rig Go instance link
            self.md_rigList = {}

            self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise StandardError,"No suitable helper found"

            try:#verify eye look
                mi_go._verify_eyeLook()
            except Exception,error: raise StandardError,"[Faied to verify eye look]{%s}"%error


            #>> Find our joint lists ===================================================================
            self.md_jointLists = {}	    
            self.ml_rigJoints = mi_go._mi_module.rigNull.msgList_get('rigJoints')

            self.md_rigList['eyeOrbJoint'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
                                                                                   cgmName = 'eyeOrb')[0]    

            self.md_rigList['eyeJoint'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
                                                                                cgmName = 'eye')[0]	  

            if self.mi_helper.buildIris:
	 
                self.md_rigList['irisJoint'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
                                                                                     cgmName = 'iris')[0] 
                try:self.md_rigList['controlIris'] = mi_go._i_rigNull.controlIris
                except Exception,error:raise StandardError,"iris fail]{%s}"%(error)  
                
            if self.mi_helper.buildPupil:
                self.md_rigList['pupilJoint'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
                                                                                      cgmName = 'pupil')[0] 
                try:self.md_rigList['controlPupil'] = mi_go._i_rigNull.controlPupil
                except Exception,error:raise StandardError,"pupil fail]{%s}"%(error)  
                
            #>> Running lists ===========================================================================	    
            try:self.md_rigList['eyeLook'] = mi_go._get_eyeLook()
            except Exception,error:raise StandardError,"[eyeLook fail]{%s}"%(error)	    
            try:self.md_rigList['controlIK'] = mi_go._i_rigNull.controlIK
            except Exception,error:raise StandardError,"controlIK fail]{%s}"%(error)
            try:self.md_rigList['controlFK'] = mi_go._i_rigNull.controlFK
            except Exception,error:raise StandardError,"controlFK fail]{%s}"%(error)
            try:self.md_rigList['settings'] = mi_go._i_rigNull.settings
            except Exception,error:raise StandardError,"controlIK fail]{%s}"%(error)	
            try:self.md_rigList['eyeMove'] = mi_go._i_rigNull.eyeMove
            except Exception,error:raise StandardError,"eyeMove fail]{%s}"%(error)

            #Settings
            self.mPlug_FKIK = cgmMeta.cgmAttr(self.md_rigList['settings'].mNode,'blend_FKIK')
            #self.log_infoNestedDict('md_rigList')

        def _setupDefaults_(self):
            try:#Query ====================================================================================
                mi_go = self._go#Rig Go instance link
                mPlug_FKIK = self.mPlug_FKIK
            except Exception,error:raise Exception,"[Query]{%s}"%error	

            mPlug_FKIK.p_defaultValue = 1
            mPlug_FKIK.value = 1

        def _dynParentGroup_(self):
            try:#Query ====================================================================================
                mi_go = self._go#Rig Go instance link
                mi_controlIK = self.md_rigList['controlIK']
                mi_eyeLook = self.md_rigList['eyeLook']
            except Exception,error:raise Exception,"[Query]{%s}"%error	

            ml_eyeDynParents = [mi_eyeLook]
            for mObj in mi_eyeLook.dynParentGroup.msgList_get('dynParents'):
                ml_eyeDynParents.append(mObj)

            #if mi_go._mi_moduleParent:
                #ml_eyeDynParents.append(mi_go._mi_moduleParent.rigNull.rigJoints[0])	    
            #ml_eyeDynParents.append(mi_go._i_masterControl)

            #Add our parents
            i_dynGroup = mi_controlIK.dynParentGroup
            log.info("Dyn group at setup: %s"%i_dynGroup)
            i_dynGroup.dynMode = 0

            for o in ml_eyeDynParents:
                i_dynGroup.addDynParent(o)
            i_dynGroup.rebuild()	

        def _setupEye_(self):
            try:#Query ====================================================================================
                mi_go = self._go#Rig Go instance link

                mi_controlFK = self.md_rigList['controlFK']
                mi_controlIK = self.md_rigList['controlIK']
                #mi_irisControl = self.md_rigList['controlIris']
                #mi_pupilControl = self.md_rigList['controlPupil']

                mi_eyeJoint = self.md_rigList['eyeJoint']
                mi_eyeMove = self.md_rigList['eyeMove']		
                mi_eyeLook = self.md_rigList['eyeLook']
                mi_eyeOrbJoint = self.md_rigList['eyeOrbJoint']
                #mi_irisJoint = self.md_rigList['irisJoint']
                #mi_pupilJoint = self.md_rigList['pupilJoint']
                mi_settings = self.md_rigList['settings']
                mi_helper = self.mi_helper
                mPlug_FKIK = self.mPlug_FKIK
                str_mirrorSide = mi_go._direction

                ml_rigJoints = self.ml_rigJoints
                v_aim = mi_go._vectorAim
                v_up = mi_go._vectorUp
            except Exception,error:raise Exception,"[Query]{%s}"%error	

            try:#Base eye setup ==============================================================================
                d_return = rUtils.createEyeballRig(mi_helper,ballJoint = mi_eyeJoint,
                                                   ikControl = mi_controlIK, fkControl = mi_controlFK,
                                                   buildIK=True, driverAttr=mPlug_FKIK,
                                                   setupVisBlend = True,
                                                   moduleInstance = mi_go._mi_module)

                d_return['mi_rigGroup'].parent = mi_go._i_constrainNull.mNode#parent rig group to constrain null
                mi_fkLoc = d_return['md_locs']['fk']#Grab the fk loc
                mi_go._i_rigNull.connectChildNode(mi_fkLoc,'locFK','rigNull')
                self.log_info(">> fkLoc: %s "%(mi_fkLoc.p_nameShort)) 

                mi_blendLoc = d_return['md_locs']['blend']#Grab the blend loc	
                mi_go._i_rigNull.connectChildNode(mi_blendLoc,'locBlend','rigNull')
                self.log_info(">> blendLoc: %s "%(mi_blendLoc.p_nameShort)) 
            except Exception,error:raise Exception,"[Base eye setup]{%s}"%(error)

            try:#Connect vis blend between fk/ik ==============================================================
                #>>> Setup a vis blend result
                mPlug_FKon = d_return['mPlug_fkVis']
                mPlug_IKon = d_return['mPlug_ikVis']
                self.log_info(" >> mPlug_FKon: %s "%(mPlug_FKon.p_combinedShortName)) 
                self.log_info(" >> mPlug_IKon: %s "%(mPlug_IKon.p_combinedShortName)) 

                mPlug_FKon.doConnectOut("%s.visibility"%mi_go._i_constrainNull.controlsFKNull.mNode)
                mPlug_IKon.doConnectOut("%s.visibility"%mi_go._i_constrainNull.controlsIKNull.mNode)

                try:#Setup constain loc
                    mi_settingsFKLoc = mi_settings.doLoc()
                    mi_settingsFKLoc.parent = mi_controlFK
                    mi_go.connect_toRigGutsVis(mi_settingsFKLoc)
                    _str_const = mc.parentConstraint([mi_settingsFKLoc.mNode,mi_controlIK.mNode],mi_settings.masterGroup.mNode,maintainOffset = False)[0]
                    l_weightTargets = mc.parentConstraint(_str_const,q=True,weightAliasList = True)

                    mPlug_FKon.doConnectOut("%s.%s"%(_str_const,l_weightTargets[0]))
                    mPlug_IKon.doConnectOut("%s.%s"%(_str_const,l_weightTargets[1])) 

                except Exception,error:raise StandardError,"constrain loc | %s"%error	
            except Exception,error:raise Exception,"[fk/ik blend setup fail]{%s}"%(error)


            try:#Setup pupil and iris #==================================================================	
                #OLD SETUP ----The gist of what we'll do is setup identical attributes on both fk and ik controls
                #and then blend between the two to drive what is actually influencing the joints
                #scale = (fk_result * fk_pupil) + (ik_result *ik_pupil)

                mc.parentConstraint(mi_eyeJoint.mNode, mi_go._i_constrainNull.eyeTrackNull.mNode,maintainOffset = 1)
                #attributes.doConnectAttr("%s.s"%mi_irisControl.mNode,"%s.s"%mi_irisJoint.mNode)
                #attributes.doConnectAttr("%s.s"%mi_irisControl.mNode,"%s.s"%mi_irisJoint.mNode)
                #mc.scaleConstraint(mi_irisControl.mNode,mi_irisJoint.mNode)
                #mc.scaleConstraint(mi_pupilControl.mNode,mi_pupilJoint.mNode)

                '''
		l_extraSetups = ['pupil','iris']
		for i,n in enumerate(l_extraSetups):
		    buffer = mi_go._i_rigNull.getMessage('%sJoint'%n)
		    if buffer:    
			self.log_info(" >> Seting up %s"%(n)) 
			mi_tmpJoint = cgmMeta.cgmObject(buffer[0])
			mi_rigJoint = mi_tmpJoint.rigJoint
			mPlug_tmp = cgmMeta.cgmAttr(mi_settings,'%s'%n,attrType='float',initialValue=1,keyable=True, defaultValue=1)
			for a in mi_go._jointOrientation[1:]:
			    mPlug_tmp.doConnectOut("%s.s%s"%(mi_rigJoint.mNode,a))		
			"""
			mPlug_FK_in = cgmMeta.cgmAttr(ml_controlsFKNull[0],'%s'%n,attrType='float',initialValue=1,keyable=True, defaultValue=1)
			mPlug_FK_out = cgmMeta.cgmAttr(ml_controlsFKNull[0],'%s_fkResult'%n,attrType='float',hidden=False,lock=True)	    
			mPlug_IK_in = cgmMeta.cgmAttr(mi_controlIK,'%s'%n,attrType='float',initialValue=1,keyable=True,defaultValue=1)
			mPlug_IK_out = cgmMeta.cgmAttr(mi_controlIK,'%s_ikResult'%n,attrType='float',hidden=False,lock=True)	    
			mPlug_Blend_out = cgmMeta.cgmAttr(mi_tmpJoint,'%s_blendResult'%n,attrType='float',hidden=False,lock=True)	    
			NodeF.argsToNodes("%s = %s * %s"%(mPlug_FK_out.p_combinedShortName,
							  mPlug_FKon.p_combinedShortName,
							  mPlug_FK_in.p_combinedShortName)).doBuild()
			NodeF.argsToNodes("%s = %s * %s"%(mPlug_IK_out.p_combinedShortName,
							  mPlug_IKon.p_combinedShortName,
							  mPlug_IK_in.p_combinedShortName)).doBuild()	 
			NodeF.argsToNodes("%s = %s + %s"%(mPlug_Blend_out.p_combinedShortName,
							  mPlug_FK_out.p_combinedShortName,
							  mPlug_IK_out.p_combinedShortName)).doBuild()	
			for a in self._jointOrientation[1:]:
			    mPlug_Blend_out.doConnectOut("%s.s%s"%(mi_tmpJoint.mNode,a))
			"""
			'''
            except Exception,error:raise Exception,"[pupil setup fail]{%s}"%(error)

            try:#Parent and constraining bits ==================================================================
                #mi_eyeMove.masterGroup.parent = mi_eye
                mi_eyeOrbJoint.parent = mi_eyeMove
                mi_eyeMove.masterGroup.parent = mi_go._i_faceDeformNull
                mc.parentConstraint(mi_eyeMove.mNode,
                                    mi_go._i_constrainNull.mNode,maintainOffset = True)		
                mc.scaleConstraint(mi_eyeMove.mNode,
                                   mi_go._i_constrainNull.mNode,maintainOffset = True)			
                '''
		try:#Constrain to parent module
		    ml_rigJoints[0].parent = mi_go._i_constrainNull.mNode
		    if mi_go._mi_moduleParent:
			mc.parentConstraint(mi_go._mi_moduleParent.rig_getSkinJoints()[-1].mNode,
			                    mi_go._i_constrainNull.mNode,maintainOffset = True)
		except Exception,error:
		    raise StandardError,"[Connect to parent fail]{%s}"%(error)
		'''
                try:#Lock Groups ======================================================================
                    for mi_ctrl in [mi_controlFK,mi_controlIK,mi_settings]:
                        mi_ctrl._setControlGroupLocks(True)
                except Exception,error:
                    raise StandardError,"[Lock N Hide groups]{%s}"%(error)

                #Final stuff
                mi_go._set_versionToCurrent()
            except Exception,error:raise Exception,"[Parent and constraining bits ]{%s}"%(error) 
    return fncWrap(*args, **kws).go()

def build_matchSystem(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_matchSystem(%s)'%self.d_kws['goInstance']._strShortName
            self._b_autoProgressBar = True	
            self._b_reportTimes = True	    	    
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
                                {'step':'Build','call':self._build_}     ]	
            #=================================================================

        def _gatherInfo_(self):
            mi_go = self._go#Rig Go instance link
            try:
                self.mi_eyeLook = mi_go._get_eyeLook()
                self.mi_eyeLookDynSwitch = self.mi_eyeLook.dynSwitch
            except Exception,error:raise StandardError,"[eyeLook fail]{%s}"%(error)	

            try:self.mi_controlIK = mi_go._i_rigNull.controlIK
            except Exception,error:raise StandardError,"[controlIK fail]{%s}"%(error)

            try:self.mi_controlFK=  mi_go._i_rigNull.controlFK 
            except Exception,error:raise StandardError,"[controlFK fail]{%s}"%(error)

            try:self.ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
            except Exception,error:raise StandardError,"[rigJoints fail]{%s}"%(error)

            try:self.mi_settings = mi_go._i_rigNull.settings
            except Exception,error:raise StandardError,"[settings fail]{%s}"%(error)

            try:self.mi_locBlend= mi_go._i_rigNull.locBlend
            except Exception,error:raise StandardError,"[mi_locBlend fail]{%s}"%(error)

            try:self.mi_locFK= mi_go._i_rigNull.locFK
            except Exception,error:raise StandardError,"[mi_locFK fail]{%s}"%(error)	

            self.ml_fkJoints = mi_go._i_rigNull.msgList_get('fkJoints')
            self.ml_ikJoints = mi_go._i_rigNull.msgList_get('ikJoints')

            try:self.mi_dynSwitch = mi_go._i_dynSwitch
            except Exception,error:raise StandardError,"[dynSwitch fail]{%s}"%(error)

        def _build_(self):
            try:#>>> First IK to FK
                i_ikMatch = cgmRigMeta.cgmDynamicMatch(dynObject=self.mi_controlIK,
                                                       dynPrefix = "FKtoIK",
                                                       dynMatchTargets=self.mi_locBlend)
            except Exception,error:raise StandardError,"[ik to fk fail]{%s}"%(error)  

            try:#>>> FK to IK
                #============================================================================
                i_fkMatch = cgmRigMeta.cgmDynamicMatch(dynObject = self.mi_controlFK,
                                                       dynPrefix = "IKtoFK",
                                                       dynMatchTargets=self.mi_locBlend)
            except Exception,error:raise StandardError,"[fk to ik fail! | error: %s"%(error)   

            #>>> Register the switches
            try:
                self.mi_dynSwitch.addSwitch('snapToFK',[self.mi_settings.mNode,'blend_FKIK'],
                                            0,
                                            [i_fkMatch])

                self.mi_dynSwitch.addSwitch('snapToIK',[self.mi_settings.mNode,'blend_FKIK'],
                                            1,
                                            [i_ikMatch])

                self.mi_eyeLookDynSwitch.addSwitch('snapToFK',[self.mi_settings.mNode,'blend_FKIK'],
                                                   0,
                                                   [i_fkMatch])
                self.mi_eyeLookDynSwitch.addSwitch('snapToIK',[self.mi_settings.mNode,'blend_FKIK'],
                                                   1,
                                                   [i_ikMatch])	
            except Exception,error:raise StandardError,"[switch setup fail]{%s}"%(error)   
    return fncWrap(*args, **kws).go()

#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'rig','function':build_rig},
                    4:{'name':'match','function':build_matchSystem},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------