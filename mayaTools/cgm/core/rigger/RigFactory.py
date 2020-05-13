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
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.rigger.lib import module_Utils as modUtils

from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import GuiFactory as gui
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.lib import rayCaster as RayCast
from cgm.core.rigger.lib import cgmRigs_sharedData as cgmRigsData
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
from cgm.core.rigger.lib import joint_Utils as jntUtils
from cgm.core.rigger.lib.Limb import (spine,neckHead,leg,clavicle,arm,finger)
from cgm.core.rigger.lib.Face import (eyeball,eyelids,eyebrow,mouthNose)

from cgm.lib import (cgmMath,
                     attributes,
                     deformers,
                     locators,
                     constraints,
                     modules,
                     nodes,
                     distance,
                     dictionary,
                     joints,
                     skinning,
                     rigging,
                     search,
                     curves,
                     lists,
                     )
l_modulesDone  = ['torso','neckhead','leg','clavicle','arm','finger','thumb','eyeball','eyelids','eyebrow','mouthnose']
__l_faceModules__ = cgmRigsData.__l_faceModules__

#>>> Register rig functions
#=====================================================================
d_moduleTypeToBuildModule = {'leg':leg,
                             'torso':spine,
                             'neckhead':neckHead,
                             'clavicle':clavicle,
                             'arm':arm,
                             'finger':finger,
                             'thumb':finger,
                             'eyeball':eyeball,
                             'eyebrow':eyebrow,
                             'mouthnose':mouthNose,
                             'eyelids':eyelids,
                             } 
#for module in d_moduleTypeToBuildModule.keys():
#    reload(d_moduleTypeToBuildModule[module])

__l_moduleJointSingleHooks__ = cgmRigsData.__l_moduleJointSingleHooks__
__l_moduleJointMsgListHooks__ = cgmRigsData.__l_moduleJointMsgListHooks__
__l_moduleControlMsgListHooks__ = cgmRigsData.__l_moduleControlMsgListHooks__

#>>> Main class function
#=====================================================================
def go(*args, **kws):
    """
    Customization rig builder from template file for setting up a cgmMorpheusMakerNetwork

    :parameters:

    :returns:

    :raises:

    """       
    class fncWrap(cgmGeneral.cgmFuncCls):		
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_func = 'RigFactory.go'	
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._cgmClass = 'RigFactory.go'
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'mModule',"default":None,"argType":'cgmModule','help':"This must be a cgm module"},
                                         {'kw':'forceNew',"default":True,"argType":'bool','help':"Whether to force a new one"},
                                         {'kw':'autoBuild',"default":True,"argType":'bool','help':"Whether to autobuild or not"},
                                         {'kw':'ignoreRigCheck',"default":False,"argType":'bool','help':"Whether to ignore the rig check on initialization"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            self.l_funcSteps = [{'step':'Initial Validation','call':self._fncStep_validate_},
                                {'step':'Buffer Data','call':self._fncStep_bufferData_}, 	                        
                                {'step':'Need Rigging?','call':self._fncStep_rigNeed_},
                                {'step':'Dynamic Switch','call':self._fncStep_dynamicSwitch_},                       	                        	                        
                                {'step':'Module rig checks','call':self._fncStep_moduleRigChecks_},                       	                        	                        	                        
                                {'step':'Deform/Constrain groups','call':self._fncStep_deformGroup_},    
                                {'step':'Process','call':self._fncStep_process_},                       	                        	                        	                        	                        	                        
                                ]

        def _fncStep_validate_(self):
            assert self.d_kws['mModule'].isModule(),"Not a module"
            self._mi_module = self.d_kws['mModule']# Link for shortness
            self._i_rigNull = self._mi_module.rigNull#speed link

            self._strShortName = self._mi_module.getShortName() or False	    
            self._str_func = "{0}('{1}')".format(self._str_func,self._strShortName)
            self.__updateFuncStrings__()

            self._i_puppet = self._mi_module.modulePuppet
            self._i_puppet.__verifyGroups__()

            self._mi_moduleParent = False
            if self._mi_module.getMessage('moduleParent'):
                self._mi_moduleParent = self._mi_module.moduleParent

            self._b_forceNew = cgmValid.boolArg(self.d_kws['forceNew'])
            self._b_ignoreRigCheck= cgmValid.boolArg(self.d_kws['ignoreRigCheck'])
            self._b_autoBuild = cgmValid.boolArg(self.d_kws['autoBuild'])

            '''
	    try:#Geo -------------------------------------------------------------------------------------------

		if self.d_kws['geo'] is None:
		    try:
			self.d_kws['geo'] = self._i_puppet.getUnifiedGeo()
			if not self.d_kws['geo']:
			    raise ValueError, "Module puppet missing geo"
		    except StandardError,error:log.warning("geo failed to find: {0}".format(error) + "="*75) 
		self.str_geo = cgmValid.objString(self.d_kws['geo'],mayaType=['mesh','nurbsSurface'])
	    except StandardError,error:self.log_error("geo failed : {0}".format(error))  
	    '''

            #Some basic assertions
            assert self._mi_module.isSkeletonized(),"Module is not skeletonized: '{0}'".format(self._strShortName)

        def _fncStep_rigNeed_(self):
            if self._mi_moduleParent:
                if not self._mi_moduleParent.isRigged():
                    raise StandardError,"'module parent is not rigged yet: '{0}'".format(self._mi_moduleParent.getShortName())

            #Then we want to see if we have a moduleParent to see if it's rigged yet
            __b_rigged = self._mi_module.isRigged()
            if __b_rigged and not self._b_forceNew and self._b_ignoreRigCheck is not True:
                return self._SuccessReturn_("Aready rigged and not forceNew")

            if not isBuildable(self):
                raise StandardError,"The builder for module type '{0}' is not ready".format(self._partType)

            try:
                self._outOfDate = False
                if self._version != self._buildVersion:
                    self._outOfDate = True	    
                    self.log_warning("Rig version out of date: {0} != {1}".format(self._version,self._buildVersion))	
                else:
                    if self._b_forceNew and self._mi_module.isRigged():
                        self._mi_module.rigDelete()
                    self.log_debug("Rig version up to date !")
            except Exception,error:raise Exception,"Version check fail | error: {0}".format(error)

        def _fncStep_dynamicSwitch_(self):
            if not self._i_rigNull.getMessage('dynSwitch'):
                self._i_dynSwitch = cgmRigMeta.cgmDynamicSwitch(dynOwner=self._i_rigNull.mNode)
            else:
                self._i_dynSwitch = self._i_rigNull.dynSwitch

        def _fncStep_dynamicSwitch2_(self):
            pass	    
        def _fncStep_bufferData_(self):
            try:#Master control ---------------------------------------------------------
                self._i_masterControl = self._mi_module.modulePuppet.masterControl
                self.mPlug_globalScale = cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')	    
                self._i_masterSettings = self._i_masterControl.controlSettings
                self._i_masterDeformGroup = self._mi_module.modulePuppet.masterNull.deformGroup	 
            except Exception,error:raise Exception,"Master control | error: {0}".format(error)
            
            try:#Module stuff ------------------------------------------------------------
                self._l_moduleColors = self._mi_module.getModuleColors()            
                self._l_coreNames = self._mi_module.coreNames.value
                self._i_templateNull = self._mi_module.templateNull#speed link
                self._i_rigNull = self._mi_module.rigNull#speed link
                self._bodyGeo = self._mi_module.modulePuppet.getGeo() or ['Morphy_Body_GEO'] #>>>>>>>>>>>>>>>>>this needs better logic   
                self._version = self._i_rigNull.version
                self._direction = self._mi_module.getAttr('cgmDirection')
            except Exception,error:raise Exception,"Module stuff | error: {0}".format(error)

            try:#Mirror stuff
                self._str_mirrorDirection = self._mi_module.get_mirrorSideAsString()
                self._f_skinOffset = self._i_puppet.getAttr('skinDepth') or 1 #Need to get from puppet!<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<		
            except Exception,error:raise Exception,"Mirror stuff | error: {0}".format(error)

            try:#Joints ------------------------------------------------------------------
                self._ml_moduleJoints = self._i_rigNull.msgList_get('moduleJoints',asMeta = True,cull = True)
                if not self._ml_moduleJoints:raise StandardError, "No module joints found!"
                self._l_moduleJoints = [j.p_nameShort for j in self._ml_moduleJoints]
                self._ml_skinJoints = self._mi_module.rig_getSkinJoints()
                for mJnt in self._ml_moduleJoints:
                    attributes.doSetAttr(mJnt.mNode,'displayLocalAxis',0)
                    
                if not self._ml_skinJoints:raise StandardError,"No Skin joints found"
                if not self._ml_moduleJoints:raise StandardError, "No module joints found!"        
                self._l_skinJoints = [j.p_nameShort for j in self._ml_skinJoints]
            except Exception,error:raise Exception,"Joints | error: {0}".format(error)
            
            try:#>>> part name -----------------------------------------------------------------
                self._partName = self._mi_module.getPartNameBase()
                self._partType = self._mi_module.moduleType.lower() or False
            except Exception,error:raise Exception,"Part Name | error: {0}".format(error)

            try:#>>> Instances and joint stuff ----------------------------------------------------
                self._mi_orientation = cgmValid.simpleOrientation(str(modules.returnSettingsData('jointOrientation')) or 'zyx')
                self._jointOrientation = self._mi_orientation.p_string      
                self._vectorAim = self._mi_orientation.p_aim.p_vector
                self._vectorUp = self._mi_orientation.p_up.p_vector
                self._vectorOut = self._mi_orientation.p_out.p_vector
                self._vectorAimNegative = self._mi_orientation.p_aimNegative.p_vector
                self._vectorUpNegative = self._mi_orientation.p_upNegative.p_vector
                self._vectorOutNegative = self._mi_orientation.p_outNegative.p_vector
            except Exception,error:raise Exception,"Vectors | error: {0}".format(error)

            #>>> Some place holders ----------------------------------------------------	    
            self._md_controlShapes = {}


        def _fncStep_moduleRigChecks_(self):
            #>>>Connect switches
            try: verify_moduleRigToggles(self)
            except Exception,error:raise Exception,"Module rig toggle fail | error: {0}".format(error)

            #>>> Object Set
            try: self._mi_module.__verifyObjectSet__()
            except Exception,error:raise Exception,"Object set fail | error: {0}".format(error)

        def _fncStep_deformGroup_(self):
            try:
                if self._partType.lower() in __l_faceModules__:
                    self.log_info("Face module...")
                    self._i_headModule = False
                    self._mi_parentHeadHandle = False
                    self.verify_headModule()
                    self.verify_faceModuleAttachJoint()
                    #self.verify_faceSkullPlate()
                    self.verify_faceDeformNull()#make sure we have a face deform null
                    self.verify_faceScaleDriver()#scale driver

                    try:#>> Constrain  head stuff =======================================================================================
                        mi_parentHeadHandle = self._mi_parentHeadHandle
                        mi_constrainNull =  self._i_faceDeformNull	    
                        try:
                            if not mi_constrainNull.isConstrainedBy(mi_parentHeadHandle.mNode):
                                mc.parentConstraint(mi_parentHeadHandle.mNode,mi_constrainNull.mNode)
                                #for attr in 'xzy':
                                    #mi_go.mPlug_multpHeadScale.doConnectOut("%s.s%s"%(mi_constrainNull.mNode,attr))
                                mc.scaleConstraint(mi_parentHeadHandle.mNode,mi_constrainNull.mNode)
                        except Exception,error:raise Exception,"Failed to constrain | %s"%error
                    except Exception,error:raise Exception,"!constrain stuff to the head! | %s"%(error)				    
            except Exception,error:raise Exception,"Face module fail | error: {0}".format(error)

            try:#>>> Deform group for the module =====================================================
                if not self._mi_module.getMessage('deformNull'):
                    if self._partType in ['eyebrow', 'mouthnose']:
                        #Make it and link it ------------------------------------------------------
                        buffer = rigging.groupMeObject(self.str_faceAttachJoint,False)
                        i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
                        i_grp.addAttr('cgmName',self._partName,lock=True)
                        i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
                        i_grp.doName()
                        i_grp.parent = self._i_faceDeformNull	
                        self._mi_module.connectChildNode(i_grp,'deformNull','module')
                        self._mi_module.connectChildNode(i_grp,'constrainNull','module')
                        self._i_deformNull = i_grp#link
                    else:
                        #Make it and link it
                        if self._partType in ['eyelids']:
                            buffer = rigging.groupMeObject(self._mi_moduleParent.deformNull.mNode,False)			
                        else:
                            buffer = rigging.groupMeObject(self._ml_skinJoints[0].mNode,False)

                        i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
                        i_grp.addAttr('cgmName',self._partName,lock=True)
                        i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
                        i_grp.doName()
                        i_grp.parent = self._i_masterDeformGroup.mNode
                        self._mi_module.connectChildNode(i_grp,'deformNull','module')
                        if self._partType in ['eyeball']:
                            self._mi_module.connectChildNode(i_grp,'constrainNull','module')	
                            i_grp.parent = self._i_faceDeformNull				
                self._i_deformNull = self._mi_module.deformNull
            except Exception,error:raise Exception,"Deform null fail | error: {0}".format(error)


            try:#>>> Constrain Deform group for the module ==========================================
                if not self._mi_module.getMessage('constrainNull'):
                    if self._partType not in __l_faceModules__ or self._partType in ['eyelids']:
                        #Make it and link it
                        buffer = rigging.groupMeObject(self._i_deformNull.mNode,False)
                        i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
                        i_grp.addAttr('cgmName',self._partName,lock=True)
                        i_grp.addAttr('cgmTypeModifier','constrain',lock=True)	 
                        i_grp.doName()
                        i_grp.parent = self._i_deformNull.mNode
                        self._mi_module.connectChildNode(i_grp,'constrainNull','module')
                self._i_constrainNull = self._mi_module.constrainNull
            except Exception,error:raise Exception,"Constrain null fail | error: {0}".format(error)
            
            try:
                self._b_noRollMode = False
                self._b_addMidTwist = True
                if self._i_templateNull.getMayaAttr('rollJoints') == 0:
                    self._b_noRollMode = True
                    self._b_addMidTwist = False
                    self.log_info("No rollJoint mode...")                
            except Exception,err:raise Exception,"Roll joint checks | error: {0}".format(err)




        def _fncStep_process_(self):
            if self._partType in l_modulesDone:
                if self._outOfDate and self._b_autoBuild:
                    self.doBuild(**kws)
                else:self.log_warning("No autobuild.")
            else:self.log_warning("'{0}' module type not in done list. No auto build".format(self.buildModule.__name__) )       

        def doBuild(self,buildTo = '',**kws):
            """
            Return if a module is shaped or not
            """

            _str_func = "go.doBuild({0})".format(self._strShortName)
            mayaMainProgressBar = None
            try:
                d_build = self.buildModule.__d_buildOrder__
                int_keys = d_build.keys()

                #Build our progress Bar
                mayaMainProgressBar = gui.doStartMayaProgressBar(len(int_keys))
                for k in int_keys:
                    try:	
                        str_name = d_build[k].get('name','noName')
                        func_current = d_build[k].get('function')
                        _str_subFunc = str_name

                        if mayaMainProgressBar:mc.progressBar(mayaMainProgressBar, edit=True, status = "%s >>Rigging>> step:'%s'..."%(self._strShortName,str_name), progress=k+1)    
                        func_current(self)

                        if buildTo.lower() == str_name:
                            log.debug("%s.doBuild >> Stopped at step : %s"%(self._strShortName,str_name))
                            break
                    except Exception,error:
                        raise Exception,"%s.doBuild >> Step %s failed! | %s"%(self._strShortName,str_name,error)

                if mayaMainProgressBar:gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    
            except Exception,error:
                if mayaMainProgressBar:gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar    		
                raise Exception,"{0} | error: {1}".format(_str_func,error)
        def isShaped(self):
            """
            Return if a module is shaped or not
            """
            _str_func = "go.isShaped({0})".format(self._strShortName)  
            if self._partType in d_moduleTypeToBuildModule.keys():
                checkShapes = d_moduleTypeToBuildModule[self._partType].__d_controlShapes__
            else:
                self.log_debug("isShaped>>> Don't have a shapeDict, can't check. Passing...")	    
                return True
            for key in checkShapes.keys():
                for subkey in checkShapes[key]:
                    if not self._i_rigNull.getMessage('{0}_{1}'.format(key,subkey)):
                        if not self._i_rigNull.msgList_get('{0}_{1}'.format(key,subkey),asMeta = False):
                            if not self._i_rigNull.msgList_get('{0}'.format(subkey),False):
                                self.log_error("isShaped >>> Missing {0} '{1}' ".format(key,subkey))
                                return False
            return True
        def isRigSkeletonized(self):
            """
            Return if a module is rig skeletonized or not
            """
            _str_func = "go.isRigSkeletonized({0})".format(self._strShortName)  
            try:
                for key in self._l_jointAttrs:
                    if not self._i_rigNull.getMessage('{0}'.format(key)) and not self._i_rigNull.msgList_get('{0}'.format(key),asMeta = False):
                        self.log_error("isRigSkeletonized >>> Missing key '{0}'".format(key))
                        return False		
                return True
            except Exception,error:raise Exception,"{0} >>  {1}".format(_str_func,error)    


        #>>> NOT REWRITTEN ==============================================================
        def verify_faceModuleAttachJoint(self):
            _str_func = "go.verify_faceModuleAttachJoint(%s)"%self._mi_module.p_nameShort  

            #Find our head attach joint ------------------------------------------------------------------------------------------------
            self.str_faceAttachJoint = False
            if not self._i_headModule:
                raise StandardError,"%s >> Must have a head module"%_str_func
            try:
                mi_end = self._i_headModule.rigNull.msgList_get('moduleJoints')[-1]
                buffer =  mi_end.getMessage('scaleJoint')
                if buffer:
                    buffer2 =  mi_end.scaleJoint.getMessage('rigJoint')
                    if buffer2:
                        self.str_faceAttachJoint = buffer2[0]
                    else:
                        self.str_faceAttachJoint = buffer[0]
                else:
                    self.str_faceAttachJoint = mi_end.mNode
            except Exception,error:
                log.error("%s failed to find root joint from moduleParent | %s"%(_str_func,error))

            return self.str_faceAttachJoint

        def verify_faceSkullPlate(self,*args,**kws):
            return fnc_verify_faceSkullPlate(self,*args,**kws)

        def verify_faceDeformNull(self):
            """
            Return if a module is rig skeletonized or not
            """
            _str_func = "go.verify_faceDeformNull(%s)"%self._mi_module.p_nameShort  
            log.debug(">>> %s "%(_str_func) + "="*75)
            if self._partType not in __l_faceModules__:
                raise StandardError, "%s >> Not a face module"%_str_func

            #Try to see if we ahve a face attach joint ==============================
            try:self.str_faceAttachJoint
            except:
                try:self.verify_faceModuleAttachJoint()
                except Exception,error:
                    raise StandardError, "%s >> error: %s"%(_str_func,error)


            #Check if we have a face deformNull on a parent --------------------------	    
            buffer = self._mi_moduleParent.getMessage('faceDeformNull')
            if buffer:
                self._mi_module.connectChildNode(buffer[0],'faceDeformNull')
                self._i_rigNull.connectChildNode(buffer[0],'faceDeformNull')
                self._i_faceDeformNull = self._mi_moduleParent.faceDeformNull
                return True

            #Make it and link it ------------------------------------------------------
            buffer = rigging.groupMeObject(self.str_faceAttachJoint,False)
            i_grp = cgmMeta.asMeta(buffer,'cgmObject',setClass=True)
            i_grp.addAttr('cgmName','face',lock=True)
            i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
            i_grp.doName()
            i_grp.parent = self._i_masterDeformGroup.mNode	
            self._mi_module.connectChildNode(i_grp,'faceDeformNull')	
            self._mi_moduleParent.connectChildNode(i_grp,'faceDeformNull','module')
            self._i_faceDeformNull = i_grp#link
            return True

        def verify_headModule(self):
            try:
                if self._partType not in __l_faceModules__:
                    log.info("Not a face module, not gonna find a head from here")
                    return False
    
                if self._partType == 'eyelids':
                    self._i_headModule = self._mi_module.moduleParent.moduleParent
                else:
                    self._i_headModule = self._mi_module.moduleParent
                
                if not self._i_headModule.rigNull.getMessage('handleIK'):
                    self.log_info("No Handle IK found. Using module joint")
                    self._mi_parentHeadHandle = self._i_headModule.rigNull.msgList_get('moduleJoints')[-1]	                    
                else:
                    self._mi_parentHeadHandle = self._i_headModule.rigNull.handleIK	    
                return self._i_headModule
            except Exception,error:
                raise Exception,"verify_headModule fail | {0}".format(error)

        def verify_faceScaleDriver(self):
            try:
                mi_parentHeadHandle = self._mi_parentHeadHandle
                mi_parentBlendPlug = cgmMeta.cgmAttr(mi_parentHeadHandle,'scale')
                mi_faceDeformNull = self._i_faceDeformNull
                #connect blend joint scale to the finger blend joints
                '''
		for i_jnt in ml_blendJoints:
		    mi_parentBlendPlug.doConnectOut("%s.scale"%i_jnt.mNode)
		'''	

                #intercept world scale and add in head scale
                mPlug_multpHeadScale = cgmMeta.cgmAttr(mi_faceDeformNull,'out_multpHeadScale',value = 1.0,defaultValue=1.0,lock = True)

                mPlug_globalScale = cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')
                mPlug_globalScale.doConnectOut(mPlug_multpHeadScale)
                NodeF.argsToNodes("%s = %s * %s.sy"%(mPlug_multpHeadScale.p_combinedShortName,
                                                     mPlug_globalScale.p_combinedShortName,
                                                     mi_parentHeadHandle.p_nameShort)).doBuild()
                self.mPlug_multpHeadScale = mPlug_multpHeadScale
            except Exception,error:raise Exception,"verify_faceScaleDriver! | {0}".format(error)

        def verify_offsetGroup(self,mObj):
            try:
                mi_buffer = mObj.getMessageAsMeta('offsetGroup')
                if mi_buffer:
                    return mi_buffer
                else:
                    mi_offsetGroup = cgmMeta.asMeta( mObj.doGroup(True),'cgmObject',setClass=True)	 
                    mi_offsetGroup.doStore('cgmName',mObj)
                    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
                    mi_offsetGroup.doName()
                    mObj.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')	                
                    return mi_offsetGroup	
            except Exception,error:raise Exception,"[verify_offsetGroup! | error: {0}]".format(error)  

        def verify_faceSettings(self):
            """
            Return if a module is rig skeletonized or not
            """
            _str_func = "go.verify_faceSettings(%s)"%self._mi_module.p_nameShort  
            log.debug(">>> %s "%(_str_func) + "="*75)
            if self._partType not in __l_faceModules__:
                raise StandardError, "%s >> Not a face module"%_str_func

            #>> Constrain Null ==========================================================    
            if self._i_rigNull.getMessage('settings'):
                return True

            #Check if we have a settings control on parent module --------------------------	    
            buffer = self._i_headModule.rigNull.getMessage('settings')
            if buffer:
                self._i_rigNull.connectChildNode(buffer[0],'settings')		    
                return True

            raise Exception,"No face settings found!"

        def collectObjectTypeInRigNull(self,objType = 'locator'):
            try:
                ml_objs = []
                for mObj in self._i_rigNull.getChildren(asMeta = 1):
                    if mObj.getMayaType() == objType:
                        ml_objs.append(mObj)
                if ml_objs:
                    mi_group = cgmMeta.asMeta(mc.group(em=True),'cgmObject',setClass=1)
                    mi_group.addAttr('cgmName',objType)
                    mi_group.doName()
                    mi_group.parent = self._i_rigNull		    
                    for mObj in ml_objs:
                        mObj.parent = mi_group
            except Exception,error:raise Exception,"[collectObjectTypeInRigNull({0}! | error: {1}]".format(objType,error)  

        def collect_worldDynDrivers(self):
            try:
                ml_objs = []
                mi_worldSpaceObjectsGroup = self._i_puppet.masterNull.worldSpaceObjectsGroup
                mi_charSpaceObjectsGroup = self._i_puppet.masterNull.characterSpaceObjectsGroup
                
                for mObj in self._i_masterControl.getChildren(asMeta = 1):
                    if mObj.getMayaAttr('cgmType') in ['dynDriver']:
                        mObj.parent = mi_worldSpaceObjectsGroup
                for mObj in self.self._i_puppet.masterNull.getChildren(asMeta = 1):
                    if mObj.getMayaAttr('cgmType') in ['dynDriver']:
                        mObj.parent = mi_charSpaceObjectsGroup 
                        
            except Exception,error:raise Exception,"[collectObjectTypeInRigNull ! | error: {0}]".format(error)  

        def verify_mirrorSideArg(self,arg  = None):
            _str_func = "return_mirrorSideAsString(%s)"%self._mi_module.p_nameShort   
            log.debug(">>> %s "%(_str_func) + "="*75)   
            try:
                if arg is not None and arg.lower() in ['right','left']:
                    return arg.capitalize()
                else:
                    return 'Centre'
            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error) 

        def cleanTempAttrs(self):
            for key in self._shapesDict.keys():
                for subkey in self._shapesDict[key]:
                    self._i_rigNull.doRemove('%s_%s'%(key,subkey))
            return True

        def _get_influenceChains(self):
            return get_influenceChains(self._mi_module)	

        def _get_segmentHandleChains(self):
            return get_segmentHandleChains(self._mi_module)

        def _get_segmentChains(self):
            return get_segmentChains(self._mi_module)

        def _get_rigDeformationJoints(self):
            return get_rigDeformationJoints(self._mi_module)

        def _get_handleJoints(self):
            return self._mi_module.rig_getRigHandleJoints(asMeta = True)

        def _get_simpleRigJointDriverDict(self):
            return get_simpleRigJointDriverDict(self._mi_module)
        def _get_eyeLook(self):
            return get_eyeLook(self._mi_module)
        def _verify_eyeLook(self):
            return verify_eyeLook(self._mi_module)   
        def get_report(self):
            self._mi_module.rig_getReport()
        def _set_versionToCurrent(self):
            self._i_rigNull.version = str(self._buildVersion)	

        #>> Connections
        #=====================================================================
        def connect_toRigGutsVis(self, ml_objects, vis = True, doShapes = False):
            try:
                _str_func = "go.connect_toRigGutsVis(%s)"%self._mi_module.p_nameShort  
                #log.debug(">>> %s "%(_str_func) + "="*75)
                #start = time.clock()	

                if type(ml_objects) not in [list,tuple]:ml_objects = [ml_objects]
                for i_obj in ml_objects:
                    if doShapes:
                        for shp in i_obj.getShapes():
                            mShp = cgmMeta.cgmNode(shp)
                            mShp.overrideEnabled = 1		
                            if vis: cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mShp.mNode,'overrideVisibility'))
                            cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mShp.mNode,'overrideDisplayType'))    
                    else:
                        i_obj.overrideEnabled = 1		
                        if vis: cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideVisibility'))
                        cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideDisplayType'))    

                #log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)

            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)

        def connect_pushOverridesToShapes(self,ml_objects):
            for mObj in ml_objects:
                _overrideEnabled = mObj.overrideEnabled
                _overrideVisibilityDriver = attributes.returnDrivenAttribute("%s.overrideVisibility"%mObj.mNode)
                _overrideDisplayTypeDriver = attributes.returnDrivenAttribute("%s.overrideDisplayType"%mObj.mNode)

                if _overrideEnabled:
                    for shp in i_obj.getShapes():
                        mShp = cgmMeta.cgmNode(shp)
                        mShp.overrideEnabled = 1
                        if _overrideVisibilityDriver: attributes.doConnectAttr(_overrideVisibilityDriver,"%s.overrideVisibility"%mObj.mNode)
                        if _overrideDisplayTypeDriver: attributes.doConnectAttr(_overrideDisplayTypeDriver,"%s.overrideDisplayType"%mObj.mNode)
                    attributes.doSetAttr(mObj.mNode, "overrideEnabled", 0)
                    attributes.doSetAttr(mObj.mNode, "overrideVisibility", 1)
                    attributes.doSetAttr(mObj.mNode, "overrideDisplayType", 0)
                else:
                    log.info("%s : no override enabled!"%mObj.p_nameShort)


        def connect_restoreJointLists(self):
            raise DeprecationWarning, "Please remove this instance of 'connect_restoreJointLists'"
            try:
                if self._ml_rigJoints:
                    log.debug("%s.connect_restoreJointLists >> Found rig joints to store back"%self._strShortName)
                    self._i_rigNull.connectChildrenNodes(self._ml_rigJoints,'rigJoints','rigNull')
                self._i_rigNull.connectChildrenNodes(self._ml_skinJoints,'skinJoints','rigNull')#Push back
                self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back
            except Exception,error:
                raise StandardError,"%s.connect_restoreJointLists >> Failure: %s"%(self._strShortName,error)

        #>> Attributes
        #=====================================================================	
        def _verify_moduleMasterScale(self):
            _str_func = "go._verify_moduleMasterScale(%s)"%self._mi_module.p_nameShort  
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()	
            try:
                mPlug_moduleMasterScale = cgmMeta.cgmAttr(self._i_rigNull,'masterScale',value = 1.0,defaultValue=1.0)
                mPlug_globalScale = cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')
                mPlug_globalScale.doConnectOut(mPlug_moduleMasterScale)
                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	    
            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)


        def _get_masterScalePlug(self):
            _str_func = "go._verify_moduleMasterScale(%s)"%self._mi_module.p_nameShort  
            log.debug(">>> %s "%(_str_func) + "="*75)
            try:
                if self._i_rigNull.hasAttr('masterScale'):
                    return cgmMeta.cgmAttr(self._i_rigNull,'masterScale')
                return cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')
            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)   


        def build_visSub(self):
            _str_func = "go.build_visSub(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()	
            try:
                mi_settings = self._i_rigNull.settings
                #Add our attrs
                mPlug_moduleSubDriver = cgmMeta.cgmAttr(mi_settings,'visSub', value = 1, defaultValue = 1, attrType = 'int', minValue=0,maxValue=1,keyable = False,hidden = False)
                mPlug_result_moduleSubDriver = cgmMeta.cgmAttr(mi_settings,'visSub_out', defaultValue = 1, attrType = 'int', keyable = False,hidden = True,lock=True)

                #Get one of the drivers
                if self._mi_module.getAttr('cgmDirection') and self._mi_module.cgmDirection.lower() in ['left','right']:
                    str_mainSubDriver = "%s.%sSubControls_out"%(self._i_masterControl.controlVis.getShortName(),
                                                                self._mi_module.cgmDirection)
                else:
                    str_mainSubDriver = "%s.subControls_out"%(self._i_masterControl.controlVis.getShortName())

                iVis = self._i_masterControl.controlVis
                visArg = [{'result':[mPlug_result_moduleSubDriver.obj.mNode,mPlug_result_moduleSubDriver.attr],
                           'drivers':[[iVis,"subControls_out"],[mi_settings,mPlug_moduleSubDriver.attr]]}]
                NodeF.build_mdNetwork(visArg)

                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	    
                return mPlug_result_moduleSubDriver

            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)   

        def build_visSubFace(self):
            _str_func = "go.build_visSubFace(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()	
            try:
                mi_settings = self._i_rigNull.settings
                #Add our attrs
                mPlug_moduleSubFaceDriver = cgmMeta.cgmAttr(mi_settings,'visSubFace', value = 1, defaultValue = 1, attrType = 'int', minValue=0,maxValue=1,keyable = False,hidden = False)
                mPlug_result_moduleSubFaceDriver = cgmMeta.cgmAttr(mi_settings,'visSubFace_out', defaultValue = 1, attrType = 'int', keyable = False,hidden = True,lock=True)

                #Get one of the drivers
                if self._mi_module.getAttr('cgmDirection') and self._mi_module.cgmDirection.lower() in ['left','right']:
                    str_mainSubDriver = "%s.%sSubControls_out"%(self._i_masterControl.controlVis.getShortName(),
                                                                self._mi_module.cgmDirection)
                else:
                    str_mainSubDriver = "%s.subControls_out"%(self._i_masterControl.controlVis.getShortName())

                iVis = self._i_masterControl.controlVis
                visArg = [{'result':[mPlug_result_moduleSubFaceDriver.obj.mNode,mPlug_result_moduleSubFaceDriver.attr],
                           'drivers':[[iVis,"subControls_out"],[mi_settings,mPlug_moduleSubFaceDriver.attr]]}]
                NodeF.build_mdNetwork(visArg)

                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	    
                return mPlug_result_moduleSubFaceDriver

            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error) 


        #>>> Joint chains
        #=====================================================================
        def mirrorChainOrientation(self,ml_chain):
            _str_func = "go.mirrorChainOrientation(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()	
            try:
                #Get our segment joints
                for mJoint in ml_chain:
                    mJoint.parent = False

                for mJoint in ml_chain:
                    mJoint.__setattr__("r%s"%self._jointOrientation[2],180)

                for i,mJoint in enumerate(ml_chain[1:]):
                    mJoint.parent = ml_chain[i]

                jntUtils.metaFreezeJointOrientation(ml_chain)

                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	    
                return ml_chain
            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)  

        def build_rigChain(self):
            _str_func = "go.build_rigChain(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()	
            try:
                #Get our segment joints
                l_rigJointsExist = self._i_rigNull.msgList_get('rigJoints',asMeta = False, cull = True)
                if l_rigJointsExist:
                    log.error("Deleting existing rig chain")
                    mc.delete(l_rigJointsExist)

                l_rigJoints = mc.duplicate([i_jnt.mNode for i_jnt in self._ml_skinJoints],po=True,ic=True,rc=True)
                ml_rigJoints = [cgmMeta.cgmObject(j) for j in l_rigJoints]

                for i,mJnt in enumerate(ml_rigJoints):
                    #log.info(mJnt.p_nameShort)		
                    mJnt.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
                    l_rigJoints[i] = mJnt.mNode
                    mJnt.connectChildNode(self._l_skinJoints[i],'skinJoint','rigJoint')#Connect	    
                    if mJnt.hasAttr('scaleJoint'):
                        if mJnt.scaleJoint in self._ml_skinJoints:
                            int_index = self._ml_skinJoints.index(mJnt.scaleJoint)
                            mJnt.connectChildNode(l_rigJoints[int_index],'scaleJoint','sourceJoint')#Connect
                    if mJnt.hasAttr('rigJoint'):mJnt.doRemove('rigJoint')

                #Name loop
                ml_rigJoints[0].parent = False
                for mJnt in ml_rigJoints:
                    mJnt.doName()		
                self._ml_rigJoints = ml_rigJoints
                self._l_rigJoints = [i_jnt.p_nameShort for i_jnt in ml_rigJoints]
                self._i_rigNull.msgList_connect('rigJoints',ml_rigJoints,'rigNull')#connect	
                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	    
                return ml_rigJoints
            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)  


        def build_handleChain(self,typeModifier = 'handle',connectNodesAs = False): 
            _str_func = "go.build_handleChain(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()		
            try:
                ml_handleJoints = self._mi_module.rig_getHandleJoints()
                ml_handleChain = []

                for i,i_handle in enumerate(ml_handleJoints):
                    i_new = i_handle.doDuplicate()
                    if ml_handleChain:i_new.parent = ml_handleChain[-1]#if we have data, parent to last
                    else:i_new.parent = False
                    i_new.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
                    i_new.doName()

                    #i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
                    ml_handleChain.append(i_new)

                #self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
                #self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back
                log.debug("%s.buildHandleChain >> built '%s handle chain: %s"%(self._strShortName,typeModifier,[i_j.getShortName() for i_j in ml_handleChain]))
                if connectNodesAs not in [None,False] and type(connectNodesAs) in [str,unicode]:
                    self._i_rigNull.msgList_connect(connectNodesAs,ml_handleChain,'rigNull')#Push back

                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
                return ml_handleChain

            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)  

        def duplicate_jointChain(self,ml_jointList = None, typeModifier = 'handle',connectNodesAs = False): 
            _str_func = "go.duplicate_jointChain(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()		
            try:
                ml_dupChain = []
                for i,i_handle in enumerate(ml_jointList):
                    i_new = i_handle.doDuplicate()
                    if ml_dupChain:i_new.parent = ml_dupChain[-1]#if we have data, parent to last
                    else:i_new.parent = False
                    i_new.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
                    i_new.doName()
                    ml_dupChain.append(i_new)

                log.debug("%s.duplicate_jointChain >> built '%s handle chain: %s"%(self._strShortName,typeModifier,[i_j.getShortName() for i_j in ml_dupChain]))
                if connectNodesAs not in [None,False] and type(connectNodesAs) in [str,unicode]:
                    self._i_rigNull.msgList_connect(connectNodesAs,ml_dupChain,'rigNull')#Push back

                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
                return ml_dupChain

            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)  

        def duplicate_moduleJoint(self, index = None, typeModifier = 'duplicate', connectNodesAs = False):    
            """
            This is only necessary because message connections are duplicated and make duplicating connected joints problematic
            """
            _str_func = "go.duplicate_moduleJoint(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()		
            try:
                if index is None:
                    raise StandardError, "%s.duplicate_moduleJoint >> No index specified"%(self._strShortName)
                if type(index) is not int:
                    raise StandardError, "%s.duplicate_moduleJoint >> index not int: %s | %s"%(self._strShortName,index,type(index))
                if index > len(self._ml_moduleJoints)+1:
                    raise StandardError, "%s.duplicate_moduleJoint >> index > len(moduleJoints): %s | %s"%(self._strShortName,index,(len(self._ml_moduleJoints)+1))

                i_target = self._ml_moduleJoints[index]
                buffer = mc.duplicate(i_target.mNode,po=True,ic=True)[0]
                i_new = cgmMeta.validateObjArg(buffer,cgmMeta.cgmObject)
                i_new.parent = False

                i_new.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
                i_new.doName()

                #Push back our nodes
                self.connect_restoreJointLists()#Push back
                log.debug("%s.duplicate_moduleJoint >> created: %s"%(self._strShortName,i_new.p_nameShort))
                if connectNodesAs not in [None,False] and type(connectNodesAs) in [str,unicode]:
                    self._i_rigNull.connectChildNode(i_new,connectNodesAs,'rigNull')#Push back

                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
                return i_new

            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)  

        def build_segmentChains(self, ml_segmentHandleJoints = None, connectNodes = True):
            _str_func = "go.build_segmentChains(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()
            ml_segmentChains = []
            if ml_segmentHandleJoints is None:
                ml_segmentHandleJoints = get_segmentHandleTargets(self._mi_module)

            if not ml_segmentHandleJoints:raise StandardError,"%s.build_segmentChains>> failed to get ml_segmentHandleJoints"%self._strShortName

            l_segPairs = lists.parseListToPairs(ml_segmentHandleJoints)

            for i,ml_pair in enumerate(l_segPairs):
                index_start = self._ml_moduleJoints.index(ml_pair[0])
                index_end = self._ml_moduleJoints.index(ml_pair[-1]) + 1
                buffer_segmentTargets = self._ml_moduleJoints[index_start:index_end]

                log.debug("segment %s: %s"%(i,buffer_segmentTargets))

                ml_newChain = []
                for i2,j in enumerate(buffer_segmentTargets):
                    i_j = j.doDuplicate()
                    i_j.addAttr('cgmTypeModifier','seg_{0}'.format(i),attrType='string',lock=True)
                    i_j.addAttr('cgmIterator',attrType = 'string',value='{0}'.format(i2),lock=True)			
                    i_j.doName()
                    #i_j.connectionChildNode(j,'segJoint','sourceJoint') <<<<<<FINISH THIS 
                    if ml_newChain:
                        i_j.parent = ml_newChain[-1].mNode
                    ml_newChain.append(i_j)

                ml_newChain[0].parent = False#Parent to deformGroup
                ml_segmentChains.append(ml_newChain)

            #Sometimes last segement joints have off orientaions, we're gonna fix
            joints.doCopyJointOrient(ml_segmentChains[-1][-2].mNode,ml_segmentChains[-1][-1].mNode)
            for segmentChain in ml_segmentChains:
                jntUtils.metaFreezeJointOrientation([i_jnt.mNode for i_jnt in segmentChain])

            #Connect stuff ============================================================================================    
            #self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
            #self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back	
            if connectNodes:
                for i,ml_chain in enumerate(ml_segmentChains):
                    l_chain = [i_jnt.getShortName() for i_jnt in ml_chain]
                    log.debug("segment chain %s: %s"%(i,l_chain))
                    self._i_rigNull.msgList_connect('segment%s_Joints'%i,ml_chain,"rigNull")

            log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
            return ml_segmentChains



        def build_simpleInfluenceChains(self,addMidInfluence = True):
            """

            """
            _str_func = "go.build_simpleInfluenceChains(%s)"%self._strShortName
            log.debug(">>> %s "%(_str_func) + "="*75)
            start = time.clock()
            try:
                ml_handleJoints = self._mi_module.rig_getHandleJoints()
                ml_segmentHandleJoints = get_segmentHandleTargets(self._mi_module)

                #>> Make influence joints ================================================================================
                l_influencePairs = lists.parseListToPairs(ml_segmentHandleJoints)
                ml_influenceJoints = []
                ml_influenceChains = []

                for i,m_pair in enumerate(l_influencePairs):#For each pair
                    str_nameModifier = 'seg_%s'%i	    
                    l_tmpChain = []
                    ml_midJoints = []	    
                    for ii,i_jnt in enumerate(m_pair):
                        i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
                        i_new.parent = False
                        i_new.addAttr('cgmNameModifier',str_nameModifier,attrType='string',lock=True)
                        i_new.addAttr('cgmTypeModifier','influence',attrType='string',lock=True)		
                        if l_tmpChain:
                            i_new.parent = l_tmpChain[-1].mNode
                        i_new.doName()
                        i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations    
                        l_tmpChain.append(i_new)

                    if addMidInfluence:
                        log.debug("%s.build_simpleInfuenceChains>>> Splitting influence segment: 2 |'%s' >> '%s'"%(self._mi_module.getShortName(),m_pair[0].getShortName(),m_pair[1].getShortName()))
                        l_new_chain = joints.insertRollJointsSegment(l_tmpChain[0].mNode,l_tmpChain[1].mNode,1)
                        #Let's name our new joints
                        for ii,jnt in enumerate(l_new_chain):
                            i_jnt = cgmMeta.asMeta(jnt,'cgmObject',setClass=True)
                            i_jnt.doCopyNameTagsFromObject(m_pair[0].mNode)
                            i_jnt.addAttr('cgmName','%s_mid_%s'%(m_pair[0].cgmName,ii),lock=True)
                            i_jnt.addAttr('cgmNameModifier',str_nameModifier,attrType='string',lock=True)		
                            i_jnt.addAttr('cgmTypeModifier','influence',attrType='string',lock=True)		
                            i_jnt.doName()
                            ml_midJoints.append(i_jnt)

                    #Build the chain lists -------------------------------------------------------------------------------------------
                    ml_segmentChain = [l_tmpChain[0]]
                    if ml_midJoints:
                        ml_segmentChain.extend(ml_midJoints)
                    ml_segmentChain.append(l_tmpChain[-1])
                    for i_j in ml_segmentChain:ml_influenceJoints.append(i_j)
                    ml_influenceChains.append(ml_segmentChain)#append to influence chains

                    log.debug("%s.buildHandleChain >> built handle chain %s: %s"%(self._strShortName,i,[i_j.getShortName() for i_j in ml_segmentChain]))

                #Copy orientation of the very last joint to the second to last
                joints.doCopyJointOrient(ml_influenceChains[-1][-2].mNode,ml_influenceChains[-1][-1].mNode)

                #Figure out how we wanna store this, ml_influence joints 
                for i_jnt in ml_influenceJoints:
                    i_jnt.parent = False

                for i_j in ml_influenceJoints:
                    jntUtils.metaFreezeJointOrientation(i_j.mNode)#Freeze orientations

                #Connect stuff ============================================================================================    
                for i,ml_chain in enumerate(ml_influenceChains):
                    l_chain = [i_jnt.getShortName() for i_jnt in ml_chain]
                    log.debug("%s.build_simpleInfuenceChains>>> split chain: %s"%(self._mi_module.getShortName(),l_chain))
                    self._i_rigNull.msgList_connect('segment%s_InfluenceJoints'%i,ml_chain,"rigNull")

                log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
                return {'ml_influenceChains':ml_influenceChains,'ml_influenceJoints':ml_influenceJoints,'ml_segmentHandleJoints':ml_segmentHandleJoints}
            except Exception,error:
                raise StandardError,"%s >> %s"%(_str_func,error)  	

    f1 = fncWrap(*args, **kws)
    f1.go()
    return f1


#>>> Functions
#=============================================================================================================
class RigFactoryFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """
        try:
            goInstance = args[0]			    
            if not issubclass(type(goInstance),go):
                raise StandardError,"Not a RigFactory.go instance: '%s'"%goInstance
            assert mc.objExists(goInstance._mi_module.mNode),"Module no longer exists"
        except Exception,error:raise Exception,"RigFactoryFunc fail | %s"%error

        super(RigFactoryFunc, self).__init__(*args, **kws)
        self._str_moduleShortName = goInstance._strShortName

        self._str_func = 'RigFactoryFunc(%s)'%self._str_moduleShortName	

        self._l_ARGS_KWS_DEFAULTS = [{'kw':'goInstance',"default":None}]
        #self.__dataBind__(*args,**kws)	

        self.mi_go = goInstance
        self.mi_module = goInstance._mi_module


def testFunc(*args,**kws):
    class fncWrap(RigFactoryFunc):
        def __init__(self,*args,**kws):
            """
            """    
            super(fncWrap, self).__init__(*args, **kws)
            self._str_func = 'testFunc(%s)'%self._str_moduleShortName	

            #EXTEND our args and defaults
            self._l_ARGS_KWS_DEFAULTS.extend([{'kw':'cat',"default":None}])
            self.__dataBind__(*args,**kws)	
            self.l_funcSteps = [{'step':'Get Data','call':self._getData}]

            #=================================================================

        def _getData(self):
            """
            """
            self.report()  
    return fncWrap(*args,**kws).go()

def fnc_verify_faceSkullPlate(*args,**kws):
    class fncWrap(RigFactoryFunc):
        def __init__(self,*args,**kws):
            """
            """    
            super(fncWrap, self).__init__(*args, **kws)
            self._str_func = '__verify_faceSkullPlate(%s)'%self._str_moduleShortName	

            #EXTEND our args and defaults
            #self._l_ARGS_KWS_DEFAULTS.extend([{'kw':'cat',"default":None}])
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Find skullPlate','call':self._findData}]

        def _findData(self):
            mi_go = self.mi_go
            #>> validate ============================================================================
            mModuleParent = self.mi_module.moduleParent
            mParentRigNull = mModuleParent.rigNull
            buffer = mParentRigNull.getMessage('skullPlate')
            if buffer:
                mi_go._mi_skullPlate = cgmMeta.validateObjArg(mParentRigNull.getMessage('skullPlate'),cgmMeta.cgmObject,noneValid=True)
                mi_go._mi_skullPlate.parent = False

                return True

            #See if we have a helper
            mi_go._mi_rigHelper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
            if mi_go._mi_rigHelper:#See if we have a connected skullPlate
                mi_skullPlate = cgmMeta.validateObjArg(mi_go._mi_rigHelper.getMessage('skullPlate'),cgmMeta.cgmObject,noneValid=True)
                if mi_skullPlate:#then we connect it
                    log.info("%s '%s' connected to module parent"%(self._str_reportStart,mi_skullPlate.p_nameShort))
                    mParentRigNull.connectChildNode(mi_skullPlate,'skullPlate','module')
                    mi_go._mi_skullPlate = mi_skullPlate
                    mi_skullPlate.parent = False
                    return True
            return False
    return fncWrap(*args,**kws).go()

def isBuildable(goInstance):
    self = goInstance
    _str_func = "%s.isBuildable"%self._strShortName
    log.debug(">>> %s "%(_str_func) + "="*75)  
    log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

    try:
        self = goInstance#Link

        if self._partType not in d_moduleTypeToBuildModule.keys():
            log.error("%s.isBuildable>>> Not in d_moduleTypeToBuildModule"%(self._strShortName))	
            return False

        try:#Version
            self._buildVersion = d_moduleTypeToBuildModule[self._partType].__version__    
        except:
            log.error("%s.isBuildable>>> Missing version"%(self._strShortName))	
            return False	
        try:#Shapes dict
            self._shapesDict = d_moduleTypeToBuildModule[self._partType].__d_controlShapes__    
        except:
            log.error("%s.isBuildable>>> Missing shape dict in module"%(self._strShortName))	
            return False	
        try:#Joints list
            self._l_jointAttrs = d_moduleTypeToBuildModule[self._partType].__l_jointAttrs__    
        except:
            log.error("%s.isBuildable>>> Missing joint attr list in module"%(self._strShortName))	
            return False
        try:#Build Module
            #self.build = d_moduleTypeToBuildModule[self._partType].__build__
            self.buildModule = d_moduleTypeToBuildModule[self._partType]
        except:
            log.error("%s.isBuildable>>> Missing Build Module"%(self._strShortName))	
            return False	    
        try:#Build Dict
            d_moduleTypeToBuildModule[self._partType].__d_buildOrder__
        except:
            log.error("%s.isBuildable>>> Missing Build Function Dictionary"%(self._strShortName))	
            return False	    


        return True
    except Exception,error:
        raise Exception,"%s >> %s"%(_str_func,error)


def verify_moduleRigToggles(goInstance):
    """
    Rotate orders
    hips = 3
    """    
    self = goInstance
    _str_func = "%s.verify_moduleRigToggles"%self._strShortName
    log.debug(">>> %s "%(_str_func) + "="*75)   
    start = time.clock()   
    log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

    try:
        str_settings = str(self._i_masterSettings.getShortName())
        str_partBase = str(self._partName + '_rig')
        str_moduleRigNull = str(self._i_rigNull.getShortName())

        self._i_masterSettings.addAttr(str_partBase,enumName = 'off:lock:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
        try:NodeF.argsToNodes("%s.gutsVis = if %s.%s > 0"%(str_moduleRigNull,str_settings,str_partBase)).doBuild()
        except Exception,error:
            raise StandardError,"verify_moduleRigToggles>> vis arg fail: %s"%error
        try:NodeF.argsToNodes("%s.gutsLock = if %s.%s == 2:0 else 2"%(str_moduleRigNull,str_settings,str_partBase)).doBuild()
        except Exception,error:
            raise StandardError,"verify_moduleRigToggles>> lock arg fail: %s"%error

        self._i_rigNull.overrideEnabled = 1		
        cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(self._i_rigNull.mNode,'overrideVisibility'))
        cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(self._i_rigNull.mNode,'overrideDisplayType'))    

        log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)
        return True
    except Exception,error:
        raise StandardError,"%s >> %s"%(_str_func,error)


def bindJoints_connect(goInstance):   
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance
    start = time.clock()    
    log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

    try:
        _str_func = "%s.bindJoints_connect"%self._strShortName  
        log.debug(">>> %s "%(_str_func) + "="*75)      

        l_rigJoints = self._i_rigNull.msgList_get('rigJoints',False) or False
        l_skinJoints = self._i_rigNull.msgList_get('skinJoints',False) or False
        log.debug("%s.connect_ToBind>> skinJoints:  len: %s | joints: %s"%(self._mi_module.getShortName(),len(l_skinJoints),l_skinJoints))
        if not l_rigJoints:
            raise StandardError,"connect_ToBind>> No Rig Joints: %s "%(self._mi_module.getShortName())
        if len(l_skinJoints)!=len(l_rigJoints):
            raise StandardError,"connect_ToBind>> Rig/Skin joint chain lengths don't match: %s | len(skinJoints): %s | len(rigJoints): %s"%(self._mi_module.getShortName(),len(l_skinJoints),len(l_rigJoints))

        for i,i_jnt in enumerate(self._i_rigNull.skinJoints):
            log.debug("'%s'>>drives>>'%s'"%(self._i_rigNull.rigJoints[i].getShortName(),i_jnt.getShortName()))
            pntConstBuffer = mc.parentConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
            #pntConstBuffer = mc.pointConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)
            #orConstBuffer = mc.orientConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)        

            attributes.doConnectAttr((self._i_rigNull.rigJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))
            #scConstBuffer = mc.scaleConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)                
            #Scale constraint connect doesn't work
        log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)

        return True
    except Exception,error:
        raise StandardError,"%s >> %s"%(_str_func,error)


def bindJoints_connectToBlend(goInstance):
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance
    _str_func = "%s.verify_moduleRigToggles"%self._strShortName
    log.debug(">>> %s "%(_str_func) + "="*75)  
    log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

    start = time.clock()        
    try:
        l_rigJoints = self._i_rigNull.msgList_get('blendJoints',False) or False
        l_skinJoints = self._i_rigNull.msgList_get('skinJoints',False) or False
        if len(l_skinJoints)!=len(l_rigJoints):
            raise StandardError,"bindJoints_connectToBlend>> Blend/Skin joint chain lengths don't match: %s"%self._mi_module.getShortName()

        for i,i_jnt in enumerate(self._i_rigNull.skinJoints):
            log.debug("'%s'>>drives>>'%s'"%(self._i_rigNull.blendJoints[i].getShortName(),i_jnt.getShortName()))
            pntConstBuffer = mc.parentConstraint(self._i_rigNull.blendJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
            #pntConstBuffer = mc.pointConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)
            #orConstBuffer = mc.orientConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)        

            attributes.doConnectAttr((self._i_rigNull.blendJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))
            #scConstBuffer = mc.scaleConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)                
            #Scale constraint connect doesn't work
            log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
        return True
    except Exception,error:
        raise StandardError,"%s >> %s"%(_str_func,error)

#>>> Module rig functions
"""
You should only pass modules into these 
"""

def get_skinJointsOLD(self, asMeta = True):
    try:
        _str_func = "%s.get_skinJoints"%self.p_nameShort  
        log.debug(">>> %s "%(_str_func) + "="*75) 
        start = time.clock()       
        log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

        """
	if not self.isSkeletonized():
	    raise StandardError,"%s.get_skinJoints >> not skeletonized."%(self.p_nameShort)"""
        ml_skinJoints = []
        ml_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
        for i,i_j in enumerate(ml_moduleJoints):
            ml_skinJoints.append(i_j)
            for attr in __l_moduleJointSingleHooks__:
                str_attrBuffer = i_j.getMessage(attr)
                if str_attrBuffer:ml_skinJoints.append( cgmMeta.validateObjArg(str_attrBuffer) )
            for attr in __l_moduleJointMsgListHooks__:
                l_buffer = i_j.msgList_get(attr,asMeta = asMeta,cull = True)

        log.debug("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
        if asMeta:return ml_skinJoints
        if ml_skinJoints:
            return [obj.p_nameShort for obj in ml_skinJoints]
    except Exception,error:
        raise StandardError, "%s >> %s"(_str_func,error)	

def get_rigDeformationJoints(self,asMeta = True):
    #Get our joints that segment joints will connect to
    try:
        _str_func = "%s.get_rigHandleJoints"%self.p_nameShort  
        log.debug(">>> %s "%(_str_func) + "="*75) 	
        start = time.clock()        		
        log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

        ml_rigJoints = self.rigNull.msgList_get('rigJoints')
        if not ml_rigJoints:
            log.error("%s.get_rigDeformationJoints >> no rig joints found"%self.getShortName())
            return []	    
        ml_defJoints = []
        for i_jnt in ml_rigJoints:
            if not i_jnt.getMessage('scaleJoint'):
                ml_defJoints.append(i_jnt)

        log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	

        if asMeta:return ml_defJoints
        elif ml_defJoints:return [j.p_nameShort for j in ml_defJoints]
        return []

    except Exception,error:
        raise StandardError,"get_rigDeformationJoints >> self: %s | error: %s"%(self,error)


def get_segmentHandleTargets(self):
    """
    Figure out which segment handle target joints
    """
    try:
        _str_func = "%s.get_segmentHandleTargets"%self.p_nameShort  
        log.debug(">>> %s "%(_str_func) + "="*75) 
        start = time.clock()        		
        log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

        ml_handleJoints = self.rig_getHandleJoints()
        log.debug(ml_handleJoints)
        if not ml_handleJoints:
            log.error("%s.get_segmentHandleTargets >> failed to find any handle joints at all"%(self.p_nameShort))
            raise StandardError
        ml_segmentHandleJoints = []#To use later as well

        #>> Find our segment handle joints ======================================================================
        #Get our count of roll joints
        l_segmentRollCounts = self.get_rollJointCountList()
        log.debug(l_segmentRollCounts)
        for i,int_i in enumerate(l_segmentRollCounts):
            if int_i > 0:
                ml_segmentHandleJoints.extend([ml_handleJoints[i],ml_handleJoints[i+1]])

        ml_segmentHandleJoints = lists.returnListNoDuplicates(ml_segmentHandleJoints)
        l_segmentHandleJoints = [i_jnt.getShortName() for i_jnt in ml_segmentHandleJoints]
        log.debug("%s.get_segmentHandleTargets >> segmentHandleJoints : %s"%(self.getShortName(),l_segmentHandleJoints))

        log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	

        return ml_segmentHandleJoints    

    except Exception,error:
        log.error("get_segmentHandleTargets >> self: %s | error: %s"%(self,error))
        return False


def get_influenceChains(self):
    try:
        #>>>Influence Joints
        _str_func = "%s.get_influenceChains"%self.p_nameShort  
        log.debug(">>> %s "%(_str_func) + "="*75) 	
        start = time.clock()        		
        log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

        l_influenceChains = []
        ml_influenceChains = []
        for i in range(100):
            str_check = 'segment%s_InfluenceJoints'%i
            buffer = self.rigNull.msgList_get(str_check,asMeta = False)
            log.debug("Checking %s: %s"%(str_check,buffer))
            if buffer:
                l_influenceChains.append(buffer)
                ml_influenceChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
            else:
                break 
        log.debug("%s._get_influenceChains>>> Segment Influence Chains -- cnt: %s | lists: %s"%(self.getShortName(),len(l_influenceChains),l_influenceChains)) 		
        log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)	
        return ml_influenceChains
    except Exception,error:
        raise StandardError,"_get_influenceChains >> self: %s | error: %s"%(self,error)

def get_segmentHandleChains(self):
    try:
        _str_func = "%s.get_segmentHandleChains"%self.p_nameShort  
        log.debug(">>> %s "%(_str_func) + "="*75) 	
        start = time.clock()        		
        log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

        l_segmentHandleChains = []
        ml_segmentHandleChains = []
        for i in range(50):
            buffer = self.rigNull.msgList_get('segmentHandles_%s'%i,asMeta = False)
            if buffer:
                l_segmentHandleChains.append(buffer)
                ml_segmentHandleChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
            else:
                break
        log.debug("%s._get_segmentHandleChains>>> Segment Handle Chains -- cnt: %s | lists: %s"%(self.getShortName(),len(l_segmentHandleChains),l_segmentHandleChains)) 	
        log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)		
        return ml_segmentHandleChains
    except Exception,error:
        raise StandardError,"_get_segmentHandleChains >> self: %s | error: %s"%(self,error)

def get_segmentChains(self):
    try:
        #Get our segment joints
        _str_func = "%s.get_segmentChains"%self.p_nameShort  
        log.debug(">>> %s "%(_str_func) + "="*75) 
        start = time.clock()        		
        log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

        l_segmentChains = []
        ml_segmentChains = []
        for i in range(50):
            buffer = self.rigNull.msgList_get('segment%s_Joints'%i,asMeta = False)
            if buffer:
                l_segmentChains.append(buffer)
                ml_segmentChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
            else:
                break
        log.debug("%s.get_segmentChains>>> Segment Chains -- cnt: %s | lists: %s"%(self.getShortName(),len(l_segmentChains),l_segmentChains)) 
        log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)			
        return ml_segmentChains
    except Exception,error:
        raise StandardError,"get_segmentChains >> self: %s | error: %s"%(self,error)


def get_rigJointDriversDict(self,printReport = True):
    """
    Figure out what drives skin joints. BLend joints should have the priority, then segment joints
    """
    _str_func = "%s.get_rigJointDriversDict"%self.p_nameShort  
    log.debug(">>> %s "%(_str_func) + "="*75)   
    start = time.clock()        		
    log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)

    def __findDefJointFromRigJoint(i_jnt):	    
        if i_jnt.getMessage('rigJoint'):
            i_rigJoint = cgmMeta.validateObjArg(i_jnt.rigJoint,cgmMeta.cgmObject)
            if i_rigJoint.hasAttr('scaleJoint'):
                i_scaleJnt = cgmMeta.validateObjArg(i_jnt.scaleJoint,cgmMeta.cgmObject)
                if i_scaleJnt.getShortName() in l_cullRigJoints:
                    #log.debug("Checking: %s | %s"%(i_jnt,i_rigJnt))
                    d_rigIndexToDriverInstance[ml_rigJoints.index(i_scaleJnt)] = i_jnt	
                    return
                else:log.warning("%s no in cull list"%i_rigJnt.getShortName())	    	    


            if i_rigJoint.getShortName() in l_cullRigJoints:
                d_rigIndexToDriverInstance[ml_rigJoints.index(i_scaleJnt)] = i_jnt			
                return
            else:log.warning("%s no in cull list"%i_rigJnt.getShortName())	    	    
        return False

    #>>>Initial checks
    ml_blendJoints = []
    mll_segmentChains = []

    try:
        ml_rigJoints = self.rigNull.msgList_get('rigJoints')
    except:
        log.error("%s.get_deformationRigDriversDict >> no rig joints found"%self.getShortName())
        return {}

    try:ml_blendJoints = self.rigNull.msgList_get('rigJoints')
    except:log.warning("%s.get_deformationRigDriversDict >> no blend joints found"%self.getShortName())

    try:mll_segmentChains = get_segmentChains(self)
    except Exception,error:
        log.error("%s.get_deformationRigDriversDict >> mll_segmentChains failure: %s"%(self.getShortName(),error))

    if not ml_blendJoints:log.warning("%s.get_deformationRigDriversDict >> no blend joints found"%self.getShortName())
    if not mll_segmentChains:log.warning("%s.get_deformationRigDriversDict >> no segment found"%self.getShortName())

    #>>>Declare
    l_cullRigJoints = [i_jnt.getShortName() for i_jnt in ml_rigJoints]	
    d_rigIndexToDriverInstance = {}
    ml_matchTargets = []
    if mll_segmentChains:
        l_matchTargets = []
        for i,ml_chain in enumerate(mll_segmentChains):
            if i == len(mll_segmentChains)-1:
                ml_matchTargets.extend([i_jnt for i_jnt in ml_chain])
            else:
                ml_matchTargets.extend([i_jnt for i_jnt in ml_chain[:-1]])		


    #First let's get our blend joints taken care of:
    if ml_blendJoints:
        for i,i_jnt in enumerate(ml_blendJoints):
            if i_jnt.getMessage('rigJoint'):
                i_rigJnt = cgmMeta.validateObjArg(i_jnt.rigJoint,cgmMeta.cgmObject)
                if i_rigJnt.getShortName() in l_cullRigJoints:
                    #log.debug("Checking: %s | %s"%(i_jnt,i_rigJnt))
                    d_rigIndexToDriverInstance[ml_rigJoints.index(i_rigJnt)] = i_jnt
                    try:l_cullRigJoints.remove(i_rigJnt.getShortName())
                    except:log.error("%s failed to remove from cull list: %s"%(i_rigJnt.getShortName(),l_cullRigJoints))
                else:
                    log.warning("%s no in cull list"%i_rigJnt.getShortName())


    #If we have matchTargets, we're going to match them	
    if ml_matchTargets:
        for i,i_jnt in enumerate(ml_matchTargets):
            if i_jnt.getMessage('rigJoint'):
                i_rigJnt = cgmMeta.validateObjArg(i_jnt.rigJoint,cgmMeta.cgmObject)
                if i_rigJnt.getMessage('scaleJoint'):
                    log.debug("Scale joint found!")
                    i_scaleJnt = cgmMeta.validateObjArg(i_rigJnt.scaleJoint,cgmMeta.cgmObject)
                    if i_scaleJnt.getShortName() in l_cullRigJoints:
                        #log.debug("Checking: %s | %s"%(i_jnt,i_rigJnt))
                        d_rigIndexToDriverInstance[ml_rigJoints.index(i_scaleJnt)] = i_jnt	
                        try:l_cullRigJoints.remove(i_scaleJnt.getShortName())
                        except:log.error("%s failed to remove from cull list: %s"%(i_scaleJnt.getShortName(),l_cullRigJoints))			
                    else:log.warning("scale joint %s not in cull list"%i_rigJnt.getShortName())	   		    

                elif i_rigJnt.getShortName() in l_cullRigJoints:
                    #log.debug("Checking: %s | %s"%(i_jnt,i_rigJnt))
                    d_rigIndexToDriverInstance[ml_rigJoints.index(i_rigJnt)] = i_jnt
                    try:l_cullRigJoints.remove(i_rigJnt.getShortName())
                    except:log.error("%s failed to remove from cull list: %s"%(i_rigJnt.getShortName(),l_cullRigJoints))	
                else:
                    log.warning("%s no in cull list"%i_rigJnt.getShortName())

    #If we have any left, do a distance check
    l_matchTargets = [i_jnt.mNode for i_jnt in ml_matchTargets]
    for i,jnt in enumerate(l_cullRigJoints):
        i_jnt = cgmMeta.cgmObject(jnt)
        attachJoint = distance.returnClosestObject(jnt,l_matchTargets)
        int_match = l_matchTargets.index(attachJoint)
        d_rigIndexToDriverInstance[ml_rigJoints.index(i_jnt)] = ml_matchTargets[int_match]    
        l_cullRigJoints.remove(jnt)

    if printReport or l_cullRigJoints:
        log.debug("%s.get_rigJointDriversDict >> "%self.getShortName() + "="*50)
        for i,i_jnt in enumerate(ml_rigJoints):
            if d_rigIndexToDriverInstance.has_key(i):
                log.debug("'%s'  << driven by << '%s'"%(i_jnt.getShortName(),d_rigIndexToDriverInstance[i].getShortName()))		    
            else:
                log.debug("%s  << HAS NO KEY STORED"%(i_jnt.getShortName()))	

        log.debug("No matches found for %s | %s "%(len(l_cullRigJoints),l_cullRigJoints))	    
        log.debug("="*75)

    if l_cullRigJoints:
        raise StandardError,"%s to find matches for all rig joints: %s"%(i_scaleJnt.getShortName())

    log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)		    
    return d_rigIndexToDriverInstance

    #except Exception,error:
        #raise StandardError,"get_rigJointDriversDict >> self: %s | error: %s"%(self,error)


def get_simpleRigJointDriverDict(self,printReport = True):
    log.debug(">>> %s.get_simpleRigJointDriverDict() >> "%(self.p_nameShort) + "="*75) 				    
    """
    Figure out what drives skin joints. BLend joints should have the priority, then segment joints
    """
    _str_func = "%s.get_simpleRigJointDriverDict"%self.p_nameShort  
    log.debug(">>> %s "%(_str_func) + "="*75)   
    log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)    
    start = time.clock()        		    
    #>>>Initial checks
    ml_blendJoints = []
    mll_segmentChains = []
    try:
        ml_moduleJoints = self.rigNull.msgList_get('moduleJoints')
        #ml_moduleJoints = cgmMeta.validateObjListArg(self.rigNull.moduleJoints,cgmMeta.cgmObject,noneValid=False)
    except:
        log.error("%s.get_simpleRigJointDriverDict >> no rig joints found"%self.getShortName())
        return {}
    try:
        ml_rigJoints = self.rigNull.msgList_get('rigJoints')
    except:
        log.error("%s.get_simpleRigJointDriverDict >> no rig joints found"%self.getShortName())
        return {}

    try:
        ml_blendJoints = self.rigNull.msgList_get('blendJoints')
    except:log.warning("%s.get_simpleRigJointDriverDict >> no blend joints found"%self.getShortName())

    try:mll_segmentChains = get_segmentChains(self)
    except Exception,error:
        log.error("%s.get_simpleRigJointDriverDict >> mll_segmentChains failure: %s"%(self.getShortName(),error))

    if not ml_blendJoints:log.error("%s.get_simpleRigJointDriverDict >> no blend joints found"%self.getShortName())
    if not mll_segmentChains:log.error("%s.get_simpleRigJointDriverDict >> no segment found"%self.getShortName())
    if not ml_blendJoints or not mll_segmentChains:
        return False

    #>>>Declare
    d_rigJointDrivers = {}

    ml_moduleRigJoints = []#Build a list of our module rig joints
    for i,i_j in enumerate(ml_moduleJoints):
        ml_moduleRigJoints.append(i_j.rigJoint)

    l_cullRigJoints = [i_jnt.getShortName() for i_jnt in ml_moduleRigJoints]	

    ml_matchTargets = []
    if mll_segmentChains:
        l_matchTargets = []
        for i,ml_chain in enumerate(mll_segmentChains):
            ml_matchTargets.extend([i_jnt for i_jnt in ml_chain[:-1]])	

    #First time we just check segment chains
    l_matchTargets = [i_jnt.getShortName() for i_jnt in ml_matchTargets]
    for i,i_jnt in enumerate(ml_moduleRigJoints):
        attachJoint = distance.returnClosestObject(i_jnt.mNode,l_matchTargets)
        i_match = cgmMeta.cgmObject(attachJoint)
        if cgmMath.isVectorEquivalent(i_match.getPosition(),i_jnt.getPosition()):
            d_rigJointDrivers[i_jnt.mNode] = i_match
            l_cullRigJoints.remove(i_jnt.getShortName())
            if i_match in ml_matchTargets:
                ml_matchTargets.remove(i_match)
        else:
            log.debug("'%s' is not in same place as '%s'. Going to second match"%(i_match.getShortName(),i_jnt.getShortName()))

    #Now we add blend joints to search list and check again
    ml_matchTargets.extend(ml_blendJoints)    
    l_matchTargets = [i_jnt.getShortName() for i_jnt in ml_matchTargets]
    ml_cullList = cgmMeta.validateObjListArg(l_cullRigJoints,cgmMeta.cgmObject)
    for i,i_jnt in enumerate(ml_cullList):
        attachJoint = distance.returnClosestObject(i_jnt.mNode,l_matchTargets)
        i_match = cgmMeta.cgmObject(attachJoint)
        log.debug("Second match: '%s':'%s'"%(i_jnt.getShortName(),i_match.getShortName()))	
        d_rigJointDrivers[i_jnt.mNode] = i_match
        l_cullRigJoints.remove(i_jnt.getShortName())
        if i_match in ml_matchTargets:
            ml_matchTargets.remove(i_match)

    if printReport or l_cullRigJoints:
        log.debug("%s.get_simpleRigJointDriverDict >> "%self.getShortName() + "="*50)
        for i,i_jnt in enumerate(ml_moduleRigJoints):
            if d_rigJointDrivers.has_key(i_jnt.mNode):
                log.debug("'%s'  << driven by << '%s'"%(i_jnt.getShortName(),d_rigJointDrivers[i_jnt.mNode].getShortName()))		    
            else:
                log.debug("%s  << HAS NO KEY STORED"%(i_jnt.getShortName()))	

        log.debug("No matches found for %s | %s "%(len(l_cullRigJoints),l_cullRigJoints))	    
        log.debug("="*75)

    if l_cullRigJoints:
        raise StandardError,"%s.get_simpleRigJointDriverDict >> failed to find matches for all rig joints: %s"%(self.getShortName(),l_cullRigJoints)

    d_returnBuffer = {}
    for str_mNode in d_rigJointDrivers.keys():
        d_returnBuffer[cgmMeta.cgmObject(str_mNode)] = d_rigJointDrivers[str_mNode]

    log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)		
    return d_returnBuffer

    #except Exception,error:
        #raise StandardError,"get_rigJointDriversDict >> self: %s | error: %s"%(self,error)

def get_report(self):
    try:
        _str_func = "%s.get_report"%self.p_nameShort  
        #log.debug(">>> %s "%(_str_func) + "="*75)  
        #log.info("'%s' NEEDS CONVERSION TO cgmFuncCls"%_str_func)
        start = time.clock()        		    
        if not self.isSkeletonized():
            log.error("%s.get_report >> Not skeletonized. Wrong report."%(self.p_nameShort))
            return False
        l_moduleJoints = self._UTILS.get_joints(self, moduleJoints = True)
        l_skinJoints = self._UTILS.get_joints(self,skinJoints = True)
        ml_handleJoints = self.rig_getHandleJoints() or []
        l_rigJoints = self._UTILS.get_joints(self,rigJoints = True)
        ml_rigHandleJoints = self.rig_getRigHandleJoints() or []
        ml_rigDefJoints = get_rigDeformationJoints(self) or []
        ml_segmentHandleTargets = get_segmentHandleTargets(self) or []

        log.info("%s.get_report >> "%self.getShortName() + "="*50)
        log.info("moduleJoints: len - %s | %s"%(len(l_moduleJoints),l_moduleJoints))	
        log.info("skinJoints: len - %s | %s"%(len(l_skinJoints),l_skinJoints))	
        log.info("handleJoints: len - %s | %s"%(len(ml_handleJoints),[i_jnt.getShortName() for i_jnt in ml_handleJoints]))	
        log.info("rigJoints: len - %s | %s"%(len(l_rigJoints),l_rigJoints))	
        log.info("rigHandleJoints: len - %s | %s"%(len(ml_rigHandleJoints),[i_jnt.getShortName() for i_jnt in ml_rigHandleJoints]))	
        log.info("rigDeformationJoints: len - %s | %s"%(len(ml_rigDefJoints),[i_jnt.getShortName() for i_jnt in ml_rigDefJoints]))	
        log.info("segmentHandleTargets: len - %s | %s"%(len(ml_segmentHandleTargets),[i_jnt.getShortName() for i_jnt in ml_segmentHandleTargets]))	

        log.info("="*75)
        log.info("%s >> Time >> = %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)		
    except Exception,error:
        raise StandardError,"get_report >> self: %s | error: %s"%(self,error)	

#Module Rig Functions ===================================================================================================    
#!! Duplicated from ModuleFactory due to importing loop 
class ModuleFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """	
        try:
            try:mModule = kws['mModule']
            except:mModule = args[0]
            try:
                assert mModule.isModule()
            except Exception,error:raise Exception,"Not a module instance : %s"%error	
        except Exception,error:raise Exception,"ModuleFunc failed to initialize | %s"%error
        self._str_func= "testFModuleFuncunc"		
        super(ModuleFunc, self).__init__(*args, **kws)

        self.mi_module = mModule	
        self._l_ARGS_KWS_DEFAULTS = [{'kw':'mModule',"default":None}]	
        #=================================================================

def get_eyeLook(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_func= "get_eyeLook(%s)"%self.mi_module.p_nameShort	
            self.__dataBind__(*args,**kws)	
            self.l_funcSteps = [{'step':'Find','call':self.__func__}]

            #=================================================================
        def __func__(self):
            #We need a module type, find a head etc
            if self.mi_module.moduleType != 'eyeball':
                raise StandardError, "Don't know how to build from non eyeball type yet"

            try:#Query ======================================================
                mi_module = self.mi_module
                mi_rigNull = self.mi_module.rigNull
                mi_puppet = self.mi_module.modulePuppet

                try:return mi_module.eyeLook
                except:pass

                try:return mi_module.moduleParent.eyeLook
                except:pass
                ml_puppetEyelooks = mi_puppet.msgList_get('eyeLook')
                if ml_puppetEyelooks:
                    if len(ml_puppetEyelooks) == 1 and ml_puppetEyelooks[0]:
                        return ml_puppetEyelooks[0]
                    else:
                        raise StandardError,"More than one puppet eye look"
                self.log_info("Failed to find eyeLook.")
                return False

            except Exception,error:raise Exception,"!Query! | %s"%(error)
    return fncWrap(*args,**kws).go()

def verify_eyeLook(*args,**kws):
    class fncWrap(ModuleFunc):
        def __init__(self,*args,**kws):
            """
            """
            super(fncWrap, self).__init__(*args, **kws)
            self._str_func= "verify_eyeLook(%s)"%self.mi_module.p_nameShort	
            self._b_reportTimes = True
            self.__dataBind__(*args,**kws)	
            self.l_funcSteps = [{'step':'Verify','call':self._verify_},
                                {'step':'Build','call':self._build_}]

            #=================================================================
        def _verify_(self):
            #We need a module type, find a head etc
            if self.mi_module.moduleType != 'eyeball':
                raise StandardError, "Don't know how to build from non eyeball type yet"

            try:#Query ======================================================
                mi_buildModule = self.mi_module
                mi_rigNull = self.mi_module.rigNull
                mi_puppet = self.mi_module.modulePuppet

                try:self._mi_moduleParent = mi_buildModule.moduleParent
                except:self._mi_moduleParent = False		

            except Exception,error:raise Exception,"!Query! | %s"%(error)

            #self._ml_puppetEyeLook = mi_puppet.msgList_get('eyeLook')
            #try:self._mi_moduleEyeLook = mi_buildModule.eyeLook
            #except:self._mi_moduleEyeLook = False

            #Running lists
            self.ml_controlsAll = []

        def _build_(self):
            #self check
            _eyeLook = get_eyeLook(self.mi_module)
            if _eyeLook:
                self.log_info("Found eye look already...")
                return _eyeLook

            try:#Query ======================================================
                mi_buildModule = self.mi_module
                mi_rigNull = self.mi_module.rigNull
                mi_puppet = self.mi_module.modulePuppet
                mi_faceDeformNull = self.mi_module.faceDeformNull
            except Exception,error:raise Exception,"!Query! | %s"%(error)

            try:mShapeCast.go(mi_buildModule,['eyeLook'])
            except Exception,error:raise Exception,"shapeCast | %s"%(error)	    
            try:mi_eyeLookShape = mi_rigNull.getMessageAsMeta('shape_eyeLook')
            except Exception,error:raise Exception,"grabShape | %s"%(error)	    
            mi_rigNull.doRemove('shape_eyeLook')
            try:d_buffer = mControlFactory.registerControl(mi_eyeLookShape.mNode,addDynParentGroup=True,
                                                           mirrorSide = 'center', mirrorAxis="translateX,rotateY,rotateZ",		                                               	                                                   
                                                           addSpacePivots=2)
            except Exception,error:raise Exception,"register Control | %s"%(error)
            mi_eyeLookShape = d_buffer['instance']
            mi_eyeLookShape.masterGroup.parent = mi_faceDeformNull
            self.mi_eyeLookShape = mi_eyeLookShape
            self.ml_controlsAll.append(mi_eyeLookShape)

            try:#Gather Parent Space Targets ======================================================
                self.ml_dynParentsToAdd = []
                mi_puppet = self.mi_module.modulePuppet
                #Need to find the head and shoulders -- need to do this better TODO

                mi_moduleParent = self._mi_moduleParent
                mi_parentRigNull = False#holder
                if mi_moduleParent:
                    mi_parentRigNull = mi_moduleParent.rigNull
                    if mi_parentRigNull.getMessage('handleIK'):
                        self.ml_dynParentsToAdd.append( mi_parentRigNull.handleIK )

                    try:mi_moduleParentsParent = mi_moduleParent.moduleParent
                    except:mi_moduleParentsParent = False		
                    if mi_moduleParentsParent:  
                        mi_parentsParentRigNull = mi_moduleParentsParent.rigNull
                        if mi_parentsParentRigNull.getMessage('handleIK'):
                            self.ml_dynParentsToAdd.append( mi_parentsParentRigNull.handleIK )		    
                        if mi_parentsParentRigNull.getMessage('cog'):
                            self.ml_dynParentsToAdd.append( mi_parentsParentRigNull.cog )	    

                self.ml_dynParentsToAdd.append(mi_puppet.masterControl)		
            except Exception,error:raise Exception,"!Gather parent space targets! | %s"%(error)

            try:#Setup dynamic parent ======================================================
                #Add our parents
                mi_dynGroup = mi_eyeLookShape.dynParentGroup
                mi_dynGroup.dynMode = 0
                ml_spacePivots = False
                if mi_eyeLookShape.msgList_get('spacePivots',asMeta = False):
                    ml_spacePivots = mi_eyeLookShape.msgList_get('spacePivots',asMeta = True)
                    self.ml_dynParentsToAdd.extend(ml_spacePivots)		    
                    self.ml_controlsAll.extend(ml_spacePivots)

                self.log_info(">>> Dynamic parents to add: %s"%([i_obj.getShortName() for i_obj in self.ml_dynParentsToAdd]))

                for o in self.ml_dynParentsToAdd:
                    mi_dynGroup.addDynParent(o)
                mi_dynGroup.rebuild()	    
            except Exception,error:raise Exception,"dynParent setup | %s"%(error)	

            try:#Connections ======================================================
                mi_puppet.msgList_append('eyeLook',mi_eyeLookShape,'puppet')
                mi_buildModule.connectChildNode(mi_eyeLookShape,'eyeLook')	
                if mi_moduleParent:
                    mi_parentRigNull.connectChildNode(mi_eyeLookShape,'eyeLook','rigNull')
            except Exception,error:raise Exception,"!Connections! | %s"%(error)		    

            try:#DynSwitch ======================================================
                mi_dynSwitch = cgmRigMeta.cgmDynamicSwitch(dynOwner=mi_eyeLookShape.mNode)
            except Exception,error:raise Exception,"!dynSwitch! | %s"%(error)	

            try:#Set locks ======================================================
                mi_eyeLookShape._setControlGroupLocks(True)
            except Exception,error:raise Exception,"!set group Locks! | %s"%(error)	

            try:#Set mirror =======================================================
                int_start = mi_puppet.get_nextMirrorIndex('centre')#"Centre"...really, Mark? :)
                for i,mCtrl in enumerate(self.ml_controlsAll):
                    try:mCtrl.addAttr('mirrorIndex', value = (int_start + i))		
                    except Exception,error: raise Exception,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

                #try:mi_go._i_rigNull.msgList_connect(self.ml_controlsAll,'controlsAll')
                #except Exception,error: raise StandardError,"!Controls all connect!| %s"%error	    
                #try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
                #except Exception,error: raise StandardError,"!Failed to set module objectSet! | %s"%error
            except Exception,error:raise Exception,"!Mirror Setup! | %s"%(error)	

            try:#moduleParent Stuff =======================================================
                if mi_moduleParent:
                    try:
                        for mCtrl in self.ml_controlsAll:
                            mi_parentRigNull.msgList_append('controlsAll',mCtrl)
                    except Exception,error: raise Exception,"!Controls all connect!| %s"%error	    
                    try:mi_parentRigNull.moduleSet.extend(self.ml_controlsAll)
                    except Exception,error: raise Exception,"!Failed to set module objectSet! | %s"%error
            except Exception,error:raise Exception,"!Module Parent registration! | %s"%(error)	

    return fncWrap(*args,**kws).go()