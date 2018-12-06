import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
__version__ = 0.03012013

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
#from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import GuiFactory as gui
from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.lib import (modules,
                     cgmMath,
                     curves,
                     lists,
                     distance,
                     locators,
                     constraints,
                     attributes,
                     position,
                     search,
                     logic)

from cgm.core.lib import nameTools
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.classes import DraggerContextFactory as dragFactory
from cgm.core.rigger import ModuleShapeCaster as mShapeCast

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
    ##Dict ------------------------------------------------------------------
    ##'mi_segmentCurve'(cgmObject) | segment curve
    ##'segmentCurve'(str) | segment curve string

    :raises:
    Exception | if reached

    """       
    class fncWrap(cgmGeneral.cgmFuncCls):		
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'TemplateFactory.go'	
            self._b_reportTimes = 0 #..we always want this on so we're gonna set it on
            self._cgmClass = 'TemplateFactory.go'
            '''
	    mModule = None,
	    forceNew = True,
	    loadTemplatePose = True,
	    tryTemplateUpdate = False,
	    geo = None,
	    **kws
	    '''
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'mModule',"default":None,"argType":'cgmModule','help':"This must be a cgm module"},
                                         {'kw':'forceNew',"default":True,"argType":'bool','help':"Whether to force a new one"},
                                         {'kw':'loadTemplatePose',"default":True,"argType":'bool','help':"Whether to attempt to load a tempate pose or now"},
                                         {'kw':'tryTemplateUpdate',"default":True,"argType":'bool','help':"Whether to attempt to update the template with saved settings after creation"},
                                         {'kw':'geo',"default":None,"argType":'mGeo,str','help':"Geo to use for processing"}]	    
            self.__dataBind__(*args, **kws)

            self.l_funcSteps = [{'step':'Initial Validation','call':self._step_validate_},
                                {'step':'Need Templating?','call':self._step_templateNeed_},
                                {'step':'Templating Data Bind','call':self._step_templatingDataBind_},	                        
                                {'step':'Checking template toggles','call':self._step_verifyModuleTemplateToggles_},
                                {'step':'Main process','call':self._step_templateProcess_},
                                {'step':'Tag Children','call':self._step_tagChildren_},	                        	                        
                                ]

        def _step_validate_(self):
            assert self.d_kws['mModule'].isModule(),"Not a module"
            self._mi_module = self.d_kws['mModule']# Link for shortness
            self._str_reportStart = "{0}('{1}')".format(self._str_reportStart,self._mi_module.p_nameShort)

            if self.d_kws['loadTemplatePose']:#trying this
                self.l_funcSteps.append({'step':'Load Template Pose','call':self._step_poseLoad_})

            try:#Geo -------------------------------------------------------------------------------------------
                if self.d_kws['geo'] is None:
                    try:
                        self.d_kws['geo'] = self._mi_module.modulePuppet.getUnifiedGeo()
                        if not self.d_kws['geo']:
                            raise ValueError, "Module puppet missing geo"
                    except StandardError,error:log.warning("geo failed to find: %s"%(error) + "="*75) 
                self.str_geo = cgmValid.objString(self.d_kws['geo'],mayaType=['mesh','nurbsSurface'])
            except StandardError,error:
                self.log_error(" geo failed : {0}".format(error))  

        def _step_templateNeed_(self):
            #Before something can be templated, we need to see if it has a puppet yet
            if not self._mi_module.getMessage('modulePuppet') and not self._mi_module.getMessage('moduleParent'):
                self.log_debug("No modulePuppet or moduleParent. Need to create")
                if self._mi_module.getMessage("helper"):
                    self._mi_module.__buildSimplePuppet__()
                else:
                    self.log_error("No modulePuppet or moduleParent and no helper")		
                    return

            if self._mi_module.mClass in ['cgmEyelids','cgmEyeball']:#Some special objects don't need no stinkin templating!
                if self._mi_module.getMessage('helper'):
                    log.info("Helper object found. No templating necessary")	    
                    return 

            if self.d_kws['tryTemplateUpdate']:
                self.log_info("Trying template update...")
                if self._mi_module.templateSettings_call('update'):
                    self.log_info("Template update...")		    
                    if self.d_kws['loadTemplatePose']:
                        self.log_info("Trying loadTemplatePose...")                                    
                        try:self._mi_module.templateSettings_call('load')
                        except Exception,err:
                            self.log_error("Load pose fail: {0}".format(err))
                            return False
                    return self._SuccessReturn_()

            if self._mi_module.isTemplated():
                if self.d_kws['forceNew']:
                    self._mi_module.deleteTemplate()
                else:
                    log.warning("'%s' has already been templated"%mModule.getShortName())
                    return self._SuccessReturn_()


        def _step_templatingDataBind_(self):

            self.mi_modulePuppet = self._mi_module.modulePuppet

            self.cls = "TemplateFactory.go"

            self.moduleNullData = attributes.returnUserAttrsToDict(self._mi_module.mNode)
            self._mi_templateNull = self._mi_module.templateNull#link

            self.rigNull = self._mi_module.getMessage('rigNull')[0] or False
            self.moduleParent = self.moduleNullData.get('moduleParent')
            self.moduleColors = self._mi_module.getModuleColors()
            self.l_coreNames = self._mi_module.coreNames.value
            self.d_coreNamesAttrs = self._mi_module.coreNames.d_indexToAttr
            self.corePosList = self._mi_templateNull.templateStarterData
            self.foundDirections = False #Placeholder to see if we have it

            assert len(self.l_coreNames) == len(self.corePosList),"coreNames length and corePosList doesn't match"

            #>>> part name 
            self.partName = self._mi_module.getPartNameBase()
            self.partType = self._mi_module.moduleType or False
            self._partName = self._mi_module.getPartNameBase()
            self._strShortName = self._mi_module.getShortName() or False    

            self.direction = None
            if self._mi_module.hasAttr('cgmDirection'):
                self.direction = self._mi_module.cgmDirection or None

            #Verify we have a puppet and that puppet has a masterControl which we need for or master scale plug
            if not self.mi_modulePuppet.getMessage('masterControl'):
                if not self.mi_modulePuppet._verifyMasterControl():
                    raise StandardError,"MasterControl failed to verify"

            self._mi_masterControl = self._mi_module.modulePuppet.masterControl
            self._mi_masterSettings = self._mi_masterControl.controlSettings
            self._mi_deformGroup = self._mi_module.modulePuppet.masterNull.deformGroup        

            #>>> template null 
            self.templateNullData = attributes.returnUserAttrsToDict(self._mi_templateNull.mNode)

            #>>>Connect switches

        def _step_verifyModuleTemplateToggles_(self):
            verify_moduleTemplateToggles(self)
        def _step_templateProcess_(self):
            try:
                if self._mi_module.mClass == 'cgmLimb':
                    log.debug("mode: cgmLimb Template")

                    build_limbTemplate(self)	

                    if 'ball' in self.l_coreNames and 'ankle' in self.l_coreNames:
                        try:
                            doCastPivots(self._mi_module)
                        except Exception,error:raise Exception,"Cast pivots fail | {0}".format(error)

                elif self._mi_module.mClass == 'cgmEyeball':
                    log.info("mode: cgmEyeball")
                    try:doMakeEyeballTemplate(self)
                    except StandardError,error:log.warning(">>> %s.go >> build failed: %s"%(self._mi_module.p_nameShort,error))  

                else:
                    raise NotImplementedError,"haven't implemented '{0} templatizing yet".format(self._mi_module.mClass)

            except Exception,error:
                raise Exception,"build fail! |{0}".format(error)

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


#@r9General.Timer
def verify_moduleTemplateToggles(goInstance):
    """
    Rotate orders
    hips = 3
    """    
    self = goInstance#Link

    str_settings = str(self._mi_masterSettings.getShortName())
    str_partBase = str(self._partName + '_tmpl')
    str_moduleTemplateNull = str(self._mi_templateNull.getShortName())

    self._mi_masterSettings.addAttr(str_partBase, defaultValue = 0, value = 1, attrType = 'int',minValue = 0, maxValue = 1, keyable = False,hidden = False)
    try:NodeF.argsToNodes("%s.tmplVis = if %s.%s > 0"%(str_moduleTemplateNull,str_settings,str_partBase)).doBuild()
    except StandardError,error:
        raise StandardError,"verify_moduleTemplateToggles>> vis arg fail: %s"%error
    try:NodeF.argsToNodes("%s.tmplLock = if %s.%s == 1:0 else 2"%(str_moduleTemplateNull,str_settings,str_partBase)).doBuild()
    except StandardError,error:
        raise StandardError,"verify_moduleTemplateToggles>> lock arg fail: %s"%error

    self._mi_templateNull.overrideEnabled = 1		
    cgmMeta.cgmAttr(self._mi_templateNull.mNode,'tmplVis',lock=False).doConnectOut("%s.%s"%(self._mi_templateNull.mNode,'overrideVisibility'))
    cgmMeta.cgmAttr(self._mi_templateNull.mNode,'tmplLock',lock=False).doConnectOut("%s.%s"%(self._mi_templateNull.mNode,'overrideDisplayType'))    
    #nodeF.argsToNodes("%s.templateLock = if %s.templateStuff == 1:0 else 2"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()	

    return True


#>>Template curve

def store_baseLength(mModule):
    """
    If a module needs pivots and has them, returns them. Checks if a module has necessary pivots.
    """
    _str_funcName = "{0}.store_curveLength".format(mModule.p_nameShort)
    try:
        mi_templateNull = mModule.templateNull
        ml_controlObjects = mi_templateNull.msgList_get('controlObjects')
        if not ml_controlObjects:
            raise ValueError,"No control objects on msgList"
        #f_distance = distance.returnDistanceBetweenPoints(ml_controlObjects[0].getParent(asMeta = 1).getPosition(),ml_controlObjects[-1].getParent(asMeta = 1).getPosition())		
        #mi_templateNull.doStore('moduleBaseLength',f_distance )
        #log.info("Base Length: {0}".format(f_distance))

        if mi_templateNull.getMessage('curve'):
            try:

                f_crvLen = distance.returnCurveLength(mi_templateNull.getMessage('curve')[0])
                mi_templateNull.doStore('curveBaseLength',f_crvLen )
                log.debug("Curve Length: {0}".format(f_crvLen))
                return True
            except Exception,error:self.log_error("Failed to get curve length | {0}".format(error))

        else:
            log.error("No curve on {0} found. Cannot store_baseLength".format(mModule.p_nameShort))
            return False
    except Exception,error:raise Exception,"{0} | {1}".format(_str_funcName,error)

#>>>> Pivots stuff 
#==========================================================================================
d_pivotAttrs = {'foot':['pivot_toe','pivot_heel','pivot_ball','pivot_inner','pivot_outer']}

#@r9General.Timer
def hasPivots(mModule):
    """
    If a module needs pivots and has them, returns them. Checks if a module has necessary pivots.
    """
    _str_funcName = "hasPivots"
    try:
        assert mModule.isModule(),"%s.hasPivots>>> not a module"%mModule.getShortName()
        l_coreNames = mModule.coreNames.value
        l_found = []
        l_missing = []  

        if 'ball' in l_coreNames and 'ankle' in l_coreNames:
            for attr in d_pivotAttrs['foot']:
                buffer = mModule.templateNull.getMessage(attr)
                if buffer:l_found.append(buffer[0])
                else:
                    l_missing.append(attr)
                    log.warning("%s.hasPivots>>> missing : '%s'"%(mModule.getShortName(),attr))
            if l_missing:
                log.error("%s.hasPivots>>> found: '%s' | missing: '%s'"%(mModule.getShortName(),l_found,l_missing))
                return False
            return l_found
        return False  
    except Exception,error:raise Exception,"{0} | {1}".format(_str_funcName,error)

#@r9General.Timer
def doCastPivots(mModule):
    try:
        _str_shortName = mModule.p_nameShort

        assert mModule.isModule(),"Not a module"
        l_coreNames = mModule.coreNames.value

        pivotCheck = hasPivots(mModule)#If we already have pivots
        if pivotCheck:
            for o in pivotCheck:mc.delete(o)#delete

        if 'ball' in l_coreNames and 'ankle' in l_coreNames:
            log.warning("Need to cast pivots!")
            try:
                mShapeCast.go(mModule,['footPivots'])
            except StandardError,error:
                raise StandardError,"%s.doCastPivots>>> failure! | %s"%(_str_shortName,error)

        return False
    except Exception,error:raise Exception,"doCastPivots | arg: {0} | {1}".format(mModule, error)

#@r9General.Timer
def doTagChildren(self): 
    try:
        mi_templateNull = self.templateNull
        for mObj in mi_templateNull.getAllChildren(asMeta = True):
            mObj.doStore('templateOwner',mi_templateNull)
    except StandardError,error:
        raise StandardError,"doTagChildren | {0}".format(error)

@cgmGeneral.Timer
def returnModuleBaseSize(self):
    try:
        size = 12
        if self.getState() < 1:
            log.error("'%s' has not been sized. Cannot find base size"%self.getShortName())
            return False
        if not self.getMessage('moduleParent') and self.getMessage('modulePuppet'):
            log.debug("Sizing from modulePuppet")
            return size
        elif self.getMessage('moduleParent'):#If it has a parent
            log.debug("Sizing from moduleParent")
            i_parent = self.moduleParent #Link
            parentState = i_parent.getState()
            mi_templateNull = self.templateNull
            if i_parent.isTemplated():#If the parent has been templated, it makes things easy
                log.debug("Parent has been templated...")
                nameCount = len(self.coreNames.value) or 1
                l_parentTemplateObjects = i_parent.templateNull.msgList_get('controlObjects',asMeta = False)
                closestObj = distance.returnClosestObjectFromPos(mi_templateNull.templateStarterData[0],l_parentTemplateObjects)
                #Find the closest object from the parent's template object
                #log.debug("closestObj: %s"%closestObj)
                boundingBoxSize = distance.returnBoundingBoxSize(closestObj,True)
                #log.info("bbSize = %s"%max(boundingBoxSize))

                size = max(boundingBoxSize) *.6
                if i_parent.moduleType == 'clavicle':
                    return size * 2   
                if self.moduleType == 'clavicle':
                    return size * .5
                elif self.moduleType == 'head':
                    return size * .5
                elif self.moduleType == 'neck':
                    return size * .5
                elif self.moduleType in ['arm','leg']:
                    return size * .75
                elif self.moduleType in ['finger','thumb']:
                    return size * .75 

            else:
                log.debug("Parent has not been templated...")          
        else:
            pass
        return size 
    except Exception,error:raise Exception,"returnModuleBaseSize | {0} ".format(error)

#@r9General.Timer
def constrainToParentModule(self):
    """
    Pass a module class. Constrains template root to parent's closest template object
    """
    try:
        log.debug(">>> constrainToParentModule")
        if not self.isTemplated():
            log.error("Must be template state to contrainToParentModule: '%s' "%self.getShortName())
            return False

        if not self.getMessage('moduleParent'):
            return False
        else:
            log.debug("looking for moduleParent info")
            i_parent = self.moduleParent #Link
            parentState = i_parent.getState()
            if i_parent.isTemplated():#If the parent has been templated, it makes things easy
                log.debug("Parent has been templated...")
                l_parentTemplateObjects = i_parent.templateNull.msgList_getMessage('controlObjects')
                log.debug("l_parentTemplateObjects: %s"%l_parentTemplateObjects)
                closestObj = distance.returnClosestObject(i_templateNull.getMessage('root')[0],l_parentTemplateObjects)
                log.debug("closestObj: %s"%closestObj)
                if l_parentTemplateObjects.index(closestObj) == 0:#if it's the first object, connect to the root
                    log.info('Use root for parent object')
                    closestObj = i_parent.templateNull.root.mNode

                #Find the closest object from the parent's template object
                log.debug("closestObj: %s"%closestObj)
                l_constraints = cgmMeta.cgmObject(self._mi_templateNull.root.parent).getConstraintsTo()
                if cgmMeta.cgmObject(self._mi_templateNull.root.parent).isConstrainedBy(closestObj):
                    log.debug("Already constrained!")
                    return True
                elif l_constraints:mc.delete(l_constraints)

                return constraints.doConstraintObjectGroup(closestObj,group = i_templateNull.root.parent,constraintTypes=['point'])
            else:
                log.debug("Parent has not been templated...")           
                return False
    except Exception,error:raise Exception,"constrainToParentModule | {0}".format(error)

#>>> Template makers ============================================================================================	
@cgmGeneral.Timer
def doMakeEyeballTemplate(self):  
    """
    Self should be a TemplateFactory.go
    """
    """
    returnList = []
    templObjNameList = []
    templHandleList = []
    """
    try:
        log.debug(">>> doMakeLimbTemplate")
        assert self.cls == 'TemplateFactory.go',"Not a TemlateFactory.go instance!"

        #Gather limb specific data and check
        #==============
        mi_helper = self._mi_module.helper
        if not mi_helper:
            raise StandardError,"No helper found!"

        b_irisControl = mi_helper.irisHelper
        b_pupilControl = mi_helper.pupilHelper

        mi_helper.parent = self._mi_module.templateNull
    except Exception,error:raise Exception,"doMakeEyeballTemplate | {0}".format(error)


    return True

def build_limbTemplate(*args, **kws):
    class fncWrap_build_limbTemplate(modUtils.templateStep):
        def __init__(self,*args, **kws):
            super(fncWrap_build_limbTemplate, self).__init__(*args, **kws)
            self._str_funcName = 'build_LimbTemplate(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args, **kws)
            #self._b_ExceptionInterupt = True
            self._b_autoProgressBar = True
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Build Handles','call':self._step_buildHandles},
                                {'step':'Build Template Curve','call':self._step_buildCurve},
                                {'step':'Build Root','call':self._step_buildRootCurve},
                                {'step':'Store','call':self._step_storeObjects},
                                {'step':'Build Orient Helpers','call':self._step_buildOrientHelpers},
                                {'step':'Parent','call':self._step_parentObjects},
                                ]
            #=================================================================
            #self.l_strSteps = ['Start','template objects','curve','root control','helpers']

        def _step_buildHandles(self):
            mi_go = self._go

            try:#Gather limb specific data and check
                #==============
                mi_go.curveDegree = mi_go._mi_templateNull.curveDegree
                mi_go.rollOverride = mi_go._mi_templateNull.rollOverride

                mi_go.doCurveDegree = getGoodCurveDegree(mi_go)
                if not mi_go.doCurveDegree:raise ValueError,"Curve degree didn't query"

                f_size = returnModuleBaseSize(mi_go._mi_module)
                self.log_debug("f_size : {0}".format(f_size))
                lastCountSizeMatch = len(mi_go.corePosList) -1	 

                if not mi_go.corePosList:
                    raise ValueError,"No mi_go.corePosList"
            except Exception,error:raise Exception,"Gather info fail | {0} ".format(error)

            self.l_tmplHandles = []
            mi_go.ml_controlObjects = []
            mi_go._mi_locs = []
            for i,pos in enumerate(mi_go.corePosList):# Don't like this sizing method but it is what it is for now
                try:
                    self.log_debug("Creating pos: {0}".format(pos))

                    #>> Make each of our base handles
                    #=============================        
                    if i == 0:
                        sizeMultiplier = 1
                    elif i == lastCountSizeMatch:
                        sizeMultiplier = .8
                    else:
                        sizeMultiplier = .75

                    #>>> Create and set attributes on the object
                    i_obj = cgmMeta.asMeta( curves.createControlCurve('sphere',(f_size * sizeMultiplier)),'cgmObject',setClass=True )
                    #i_obj = cgmMeta.cgmObject( curves.createControlCurve('sphere',(f_size * sizeMultiplier)),'cgmObject' ,setLogLevel = 'debug')                    
                    curves.setCurveColorByName(i_obj.mNode,mi_go.moduleColors[0])
                    i_obj.doStore('cgmName',mi_go.l_coreNames[i]) 
                    #i_obj.doStore('cgmName','%s.%s'%(mi_go._mi_module.coreNames.mNode,mi_go.d_coreNamesAttrs[i]))        
                    if mi_go.direction != None:
                        i_obj.addAttr('cgmDirection',value = mi_go.direction,attrType = 'string',lock=True)  
                    i_obj.addAttr('cgmType','templateObject',lock=True) 
                    i_obj.doName()#Name it

                    mc.move (pos[0], pos[1], pos[2], [i_obj.mNode], a=True)
                    i_obj.parent = mi_go._mi_templateNull

                    #>>> Loc it and store the loc
                    i_loc =  i_obj.doLoc()
                    i_loc.addAttr('cgmType',value = 'templateCurveLoc', attrType = 'string', lock=True) #Add Type
                    i_loc.v = False # Turn off visibility
                    i_loc.doName()

                    mi_go._mi_locs.append(i_loc)
                    i_obj.connectChildNode(i_loc.mNode,'curveLoc','owner')
                    i_loc.parent = mi_go._mi_templateNull#parent to the templateNull
                    mc.pointConstraint(i_obj.mNode,i_loc.mNode,maintainOffset = False)#Point contraint loc to the object

                    self.l_tmplHandles.append (i_obj.mNode)
                    mi_go.ml_controlObjects.append(i_obj)
                except Exception,error:raise Exception,"Create Obj {0} fail | {1} ".format(i,error)

        def _step_buildCurve(self):
            mi_go = self._go

            #>> Make the curve
            #============================= 
            try:
                self._mi_crv = cgmMeta.asMeta( mc.curve (d=mi_go.doCurveDegree, p = mi_go.corePosList , os=True),'cgmObject',setClass=True )
            except Exception,error:raise Exception,"Create | {0} ".format(error)

            try:
                self._mi_crv.doStore('cgmName',"{0}.cgmName".format(mi_go._mi_module.mNode))
                #self._mi_crv.addAttr('cgmName',value = str(mi_go._mi_module.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
                if mi_go.direction != None:
                    self._mi_crv.addAttr('cgmDirection',value = mi_go.direction, attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
                self._mi_crv.addAttr('cgmType',value = 'templateCurve', attrType = 'string', lock=True)
                self._mi_crv.doName()
            except Exception,error:raise Exception,"Naming | {0} ".format(error)

            curves.setCurveColorByName(self._mi_crv.mNode,mi_go.moduleColors[0])

            self._mi_crv.parent = mi_go._mi_templateNull    

            self._mi_crv.setDrawingOverrideSettings({'overrideEnabled':1,'overrideDisplayType':2},True)

            for i,i_obj in enumerate(mi_go.ml_controlObjects):#Connect each of our handles ot the cv's of the curve we just made
                mc.connectAttr ( (i_obj.curveLoc.mNode+'.translate') , ('%s%s%i%s' % (self._mi_crv.mNode, '.controlPoints[', i, ']')), f=True )

            mi_go.foundDirections = returnGeneralDirections(mi_go,self.l_tmplHandles)

        def _step_buildRootCurve(self):
            mi_go = self._go

            #>> Create root control
            #=============================  

            rootSize = (distance.returnBoundingBoxSizeToAverage(self.l_tmplHandles[0],True)*1.25)    
            self._mi_rootControl = cgmMeta.validateObjArg( curves.createControlCurve('cube',rootSize),'cgmObject',setClass = True )

            curves.setCurveColorByName(self._mi_rootControl.mNode,mi_go.moduleColors[0])
            self._mi_rootControl.addAttr('cgmName',value = str(mi_go._mi_module.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug    
            self._mi_rootControl.addAttr('cgmType',value = 'templateRoot', attrType = 'string', lock=True)
            #if mi_go.direction != None:
                #self._mi_rootControl.addAttr('cgmDirection',value = mi_go.direction, attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
            self._mi_rootControl.doName()

            #>>> Position it
            if mi_go._mi_module.moduleType in ['clavicle']:
                position.movePointSnap(self._mi_rootControl.mNode,self.l_tmplHandles[0])
            else:
                position.movePointSnap(self._mi_rootControl.mNode,self.l_tmplHandles[0])

            #See if there's a better way to do this
            if mi_go._mi_module.moduleType not in ['foot']:
                if len(self.l_tmplHandles)>1:
                    log.debug("setting up constraints...")        
                    constBuffer = mc.aimConstraint(self.l_tmplHandles[-1],self._mi_rootControl.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = mi_go.worldUpVector, worldUpType = 'vector' )
                    mc.delete (constBuffer[0])    
                elif mi_go._mi_module.getMessage('moduleParent'):
                    #l_parentTemplateObjects =  mi_go._mi_module.moduleParent.templateNull.getMessage('controlObjects')
                    helper = mi_go._mi_module.moduleParent.templateNull.msgList_get('controlObjects',asMeta = True)[-1].helper.mNode
                    if helper:
                        log.info("helper: %s"%helper)
                        constBuffer = mc.orientConstraint( helper,self._mi_rootControl.mNode,maintainOffset = False)
                        mc.delete (constBuffer[0])    

            self._mi_rootControl.parent = mi_go._mi_templateNull
            self._mi_rootControl.doGroup(maintain=True)

        def _step_storeObjects(self):
            mi_go = self._go	

            #>> Store objects
            #=============================      
            mi_go._mi_templateNull.curve = self._mi_crv.mNode
            mi_go._mi_templateNull.root = self._mi_rootControl.mNode
            mi_go._mi_templateNull.msgList_connect('controlObjects',self.l_tmplHandles)

            mi_go._mi_rootControl =self._mi_rootControl#link to carry

            store_baseLength(mi_go._mi_module)#Store our base length before we move stuff around

        def _step_buildOrientHelpers(self):
            mi_go = self._go	   
            doCreateOrientationHelpers(mi_go)

        def _step_parentObjects(self):
            mi_go = self._go	
            doParentControlObjects(mi_go._mi_module)

            #if mi_go._mi_module.getMessage('moduleParent'):#If we have a moduleParent, constrain it
                #constrainToParentModule(mi_go.m)

            #doOrientTemplateObjectsToMaster(mi_go._mi_module)


    return fncWrap_build_limbTemplate(*args, **kws).go()

def doMakeLimbTemplate2(self):  
    """
    Self should be a TemplateFactory.go
    """
    """
    returnList = []
    templObjNameList = []
    templHandleList = []
    """
    log.debug(">>> doMakeLimbTemplate")
    assert self.cls == 'TemplateFactory.go',"Not a TemlateFactory.go instance!"

    try:#Gather limb specific data and check
        #==============
        self.curveDegree = self._mi_templateNull.curveDegree
        self.rollOverride = self._mi_templateNull.rollOverride

        doCurveDegree = getGoodCurveDegree(self)
        if not doCurveDegree:raise ValueError,"Curve degree didn't query"

        #>>>Scale stuff
        size = returnModuleBaseSize(self._mi_module)

        lastCountSizeMatch = len(self.corePosList) -1
    except Exception,error:raise Exception,"Gather limb data | {0}".format(error)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Making the template objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[1]), progress=1)    					    
    try:
        templHandleList = []
        self.ml_controlObjects = []
        self._mi_locs = []
        for i,pos in enumerate(self.corePosList):# Don't like this sizing method but it is what it is for now
            #>> Make each of our base handles
            #=============================        
            if i == 0:
                sizeMultiplier = 1
            elif i == lastCountSizeMatch:
                sizeMultiplier = .8
            else:
                sizeMultiplier = .75

            #>>> Create and set attributes on the object
            i_obj = cgmMeta.validateObjArg( curves.createControlCurve('sphere',(size * sizeMultiplier)),'cgmObject',setClass = True )

            curves.setCurveColorByName(i_obj.mNode,self.moduleColors[0])

            i_obj.doStore('cgmName','%s.%s'%(self._mi_module.coreNames.mNode,self.d_coreNamesAttrs[i]))        
            #i_obj.addAttr('cgmName',value = str(self.l_coreNames[i]), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
            if self.direction != None:
                i_obj.addAttr('cgmDirection',value = self.direction,attrType = 'string',lock=True)  
            i_obj.addAttr('cgmType',value = 'templateObject', attrType = 'string',lock=True) 
            i_obj.doName()#Name it

            mc.move (pos[0], pos[1], pos[2], [i_obj.mNode], a=True)
            i_obj.parent = self._mi_templateNull

            #>>> Loc it and store the loc
            #i_loc = cgmMeta.cgmObject( i_obj.doLoc() )
            i_loc =  i_obj.doLoc()
            i_loc.addAttr('cgmName',value = self._mi_module.getShortName(), attrType = 'string', lock=True) #Add name tag
            i_loc.addAttr('cgmType',value = 'templateCurveLoc', attrType = 'string', lock=True) #Add Type
            i_loc.v = False # Turn off visibility
            i_loc.doName()

            self._mi_locs.append(i_loc)
            i_obj.connectChildNode(i_loc.mNode,'curveLoc','owner')
            i_loc.parent = self._mi_templateNull#parent to the templateNull

            mc.pointConstraint(i_obj.mNode,i_loc.mNode,maintainOffset = False)#Point contraint loc to the object

            templHandleList.append (i_obj.mNode)
            self.ml_controlObjects.append(i_obj)
    except Exception,error:raise Exception,"Template object creation | {0}".format(error)

    try:#>> Make the curve
        #============================= 
        mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[2]), progress=2)    					        
        i_crv = cgmMeta.validateObjArg( mc.curve (d=doCurveDegree, p = self.corePosList , os=True),'cgmObject',setClass = True )

        i_crv.addAttr('cgmName',value = str(self._mi_module.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
        if self.direction != None:
            i_crv.addAttr('cgmDirection',value = self.direction, attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug

        i_crv.addAttr('cgmType',value = 'templateCurve', attrType = 'string', lock=True)
        curves.setCurveColorByName(i_crv.mNode,self.moduleColors[0])
        i_crv.parent = self._mi_templateNull    
        i_crv.doName()
        i_crv.setDrawingOverrideSettings({'overrideEnabled':1,'overrideDisplayType':2},True)

        for i,i_obj in enumerate(self.ml_controlObjects):#Connect each of our handles ot the cv's of the curve we just made
            mc.connectAttr ( (i_obj.curveLoc.mNode+'.translate') , ('%s%s%i%s' % (i_crv.mNode, '.controlPoints[', i, ']')), f=True )


        self.foundDirections = returnGeneralDirections(self,templHandleList)
        log.debug("directions: %s"%self.foundDirections )
    except Exception,error:raise Exception,"template curve | {0}".format(error)

    try:#>> Create root control
        #=============================  
        mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[3]), progress=3)    					        

        rootSize = (distance.returnBoundingBoxSizeToAverage(templHandleList[0],True)*1.25)    
        i_rootControl = cgmMeta.validateObjArg( curves.createControlCurve('cube',rootSize),'cgmObject',setClass = True )

        curves.setCurveColorByName(i_rootControl.mNode,self.moduleColors[0])
        i_rootControl.addAttr('cgmName',value = str(self._mi_module.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug    
        i_rootControl.addAttr('cgmType',value = 'templateRoot', attrType = 'string', lock=True)
        if self.direction != None:
            i_rootControl.addAttr('cgmDirection',value = self.direction, attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
        i_rootControl.doName()

        #>>> Position it
        if self._mi_module.moduleType in ['clavicle']:
            position.movePointSnap(i_rootControl.mNode,templHandleList[0])
        else:
            position.movePointSnap(i_rootControl.mNode,templHandleList[0])

        #See if there's a better way to do this
        log.debug("templHandleList: %s"%templHandleList)
        if self._mi_module.moduleType not in ['foot']:
            if len(templHandleList)>1:
                log.debug("setting up constraints...")        
                constBuffer = mc.aimConstraint(templHandleList[-1],i_rootControl.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = self.worldUpVector, worldUpType = 'vector' )
                mc.delete (constBuffer[0])    
            elif self._mi_module.getMessage('moduleParent'):
                #l_parentTemplateObjects =  self._mi_module.moduleParent.templateNull.getMessage('controlObjects')
                helper = self._mi_module.moduleParent.templateNull.msgList_get('controlObjects',asMeta = True)[-1].helper.mNode
                if helper:
                    log.info("helper: %s"%helper)
                    constBuffer = mc.orientConstraint( helper,i_rootControl.mNode,maintainOffset = False)
                    mc.delete (constBuffer[0])    

        i_rootControl.parent = self._mi_templateNull
        i_rootControl.doGroup(maintain=True)
    except Exception,error:raise Exception,"Root creation | {0}".format(error)


    try:#>> Store objects
        #=============================      
        self._mi_templateNull.curve = i_crv.mNode
        self._mi_templateNull.root = i_rootControl.mNode
        self._mi_templateNull.msgList_connect('controlObjects',templHandleList)

        self._mi_rootControl = i_rootControl#link to carry
    except Exception,error:raise Exception,"store | {0}".format(error)

    try:#>> Orientation helpers
        #=============================      
        mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[3]), progress=3)    					            
        """ Make our Orientation Helpers """
        doCreateOrientationHelpers(self)
        doParentControlObjects(self)

        #if self._mi_module.getMessage('moduleParent'):#If we have a moduleParent, constrain it
            #constrainToParentModule(self.m)

        #doOrientTemplateObjectsToMaster(self._mi_module)
    except Exception,error:raise Exception,"Orientation helpers | {0}".format(error)

    return True

def doOrientTemplateObjectsToMaster(self):
    log.info(">>> %s.doOrientTemplateObjectsToMaster >> "%self.p_nameShort + "="*75)            	
    try:
        i_rootOrient = self.templateNull.orientRootHelper
        for i_obj in self.templateNull.msgList_get('controlObjects',asMeta = True):
            mHelper = i_obj.helper
            #orient the group above
            mi_loc = mHelper.doLoc()
            Snap.go(i_obj.parent,mi_loc.mNode,move=False,orient=True)
            mi_loc.delete()
    except Exception,error:raise Exception,"doOrientTemplateObjectsToMaster | {0}".format(error)

def doCreateOrientationHelpers(self):
    """ 
    """
    try:
        try:#Gather limb specific data and check
            #===================================
            #'orientHelpers':'messageSimple',#Orientation helper controls
            #'orientRootHelper':'messageSimple',#Root orienation helper

            helperObjects = []
            helperObjectGroups = []
            returnBuffer = []
            root = self._mi_templateNull.getMessage('root')[0]
            objects =  self._mi_templateNull.msgList_get('controlObjects',asMeta = False)
        except Exception,error:raise Exception,"data gather | {0}".format(error)

        try:#>> Create orient root control
            #=============================     
            orientRootSize = (distance.returnBoundingBoxSizeToAverage(root,True)*2.5)    
            i_orientRootControl = cgmMeta.validateObjArg( curves.createControlCurve('circleArrow1',orientRootSize),'cgmObject',setClass = True )

            curves.setCurveColorByName(i_orientRootControl.mNode,self.moduleColors[0])
            i_orientRootControl.addAttr('cgmName',value = str(self._mi_module.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug    
            i_orientRootControl.addAttr('cgmType',value = 'templateOrientRoot', attrType = 'string', lock=True)
            i_orientRootControl.doName()
        except Exception,error:raise Exception,"Orient root control | {0}".format(error)

        try:#>>> Store it
            i_orientRootControl.connectParent(self._mi_templateNull,'orientRootHelper','owner')#Connect it to it's object      
        except Exception,error:raise Exception,"Store orient control | {0}".format(error)

        try:#>>> Position and set up follow groups
            position.moveParentSnap(i_orientRootControl.mNode,root)    
            i_orientRootControl.parent = root #parent it to the root
            i_orientRootControl.doGroup(maintain = True)#group while maintainting position

            mc.pointConstraint(objects[0],i_orientRootControl.parent,maintainOffset = False)#Point contraint orient control to the first helper object
            mc.aimConstraint(objects[-1],i_orientRootControl.parent,maintainOffset = True, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpObject = root, worldUpType = 'objectRotation' )
            attributes.doSetLockHideKeyableAttr(i_orientRootControl.mNode,True,False,False,['tx','ty','tz','rx','ry','sx','sy','sz','v'])

            self._ml_orientHelpers = []#we're gonna store the instances so we can get them all after parenting and what not
        except Exception,error:raise Exception,"Position/setup follow groups | {0}".format(error)

        try:#>> Sub controls
            #============================= 
            if len(objects) == 1:#If a single handle module
                i_obj = cgmMeta.cgmObject(objects[0])
                position.moveOrientSnap(objects[0],root)
            else:
                for i,obj in enumerate(objects):
                    #>>> Create and color      
                    size = (distance.returnBoundingBoxSizeToAverage(obj,True)*2) # Get size
                    i_obj = cgmMeta.validateObjArg(curves.createControlCurve('circleArrow2Axis',size),'cgmObject',setClass = True)#make the curve
                    curves.setCurveColorByName(i_obj.mNode,self.moduleColors[1])
                    #>>> Tag and name
                    i_obj.doCopyNameTagsFromObject(obj)
                    i_obj.doStore('cgmType','templateOrientHelper',True)        
                    i_obj.doName()

                    #>>> Link it to it's object and append list for full store
                    i_obj.connectParent(obj,'helper','owner')#Connect it to it's object      
                    self._ml_orientHelpers.append(i_obj)
                    #>>> initial snapping """
                    position.movePointSnap(i_obj.mNode,obj)

                    if i < len(objects)-1:#If we have a pair for it, aim at that pairs aim, otherwise, aim at the second to last object
                        constBuffer = mc.aimConstraint(objects[i+1],i_obj.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = self.foundDirections[1], worldUpType = 'vector' )
                    else:
                        constBuffer = mc.aimConstraint(objects[-2],i_obj.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,1,0], worldUpVector = self.foundDirections[1], worldUpType = 'vector' )

                    if constBuffer:mc.delete(constBuffer)

                    #>>> follow groups
                    i_obj.parent = obj
                    i_obj.doGroup(maintain = True)

                    if i < len(objects)-1:#If we have a pair for it, aim at that pairs aim, otherwise, aim at the second to last object
                        mc.aimConstraint(objects[i+1],i_obj.parent,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = [0,1,0], worldUpObject = i_orientRootControl.mNode, worldUpType = 'objectrotation' )
                    else:
                        constBuffer = mc.aimConstraint(objects[-2],i_obj.parent,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,1,0], worldUpObject = i_orientRootControl.mNode, worldUpType = 'objectrotation' )

                    #>>> ConnectVis, lock and hide
                    #mc.connectAttr((visAttr),(helperObj+'.v'))
                    if obj == objects[-1]:
                        attributes.doSetLockHideKeyableAttr(i_obj.mNode,True,False,False,['tx','ty','tz','ry','sx','sy','sz','v'])            
                    else:
                        attributes.doSetLockHideKeyableAttr(i_obj.mNode,True,False,False,['tx','ty','tz','ry','sx','sy','sz','v'])
                    i_obj.rotateOrder = 5	    
        except Exception,error:raise Exception,"sub controls | {0}".format(error)

        try:#>>> Get data ready to go forward
            bufferList = []
            for o in self._ml_orientHelpers:
                bufferList.append(o.mNode)
            self._mi_templateNull.msgList_connect('orientHelpers',bufferList)
            self._mi_orientRootHelper = i_orientRootControl
        except Exception,error:raise Exception,"forward data | {0}".format(error)
        return True
    except Exception,error:raise Exception,"doCreateOrientationHelpers | {0}".format(error)

#@r9General.Timer
def doParentControlObjects(mModule):
    """
    Needs instanced module
    """
    try:
        mi_templateNull = mModule.templateNull

        i_root = mi_templateNull.root
        ml_controlObjects = mi_templateNull.msgList_get('controlObjects',asMeta = True)

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        #>> Parent objects
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        for i_obj in ml_controlObjects:
            i_obj.parent = i_root.mNode

        #ml_controlObjects[0].doGroup(maintain=True)#Group to zero out
        #ml_controlObjects[-1].doGroup(maintain=True)  

        log.debug(mi_templateNull.msgList_getMessage('controlObjects',False))
        """
	if mModule.moduleType not in ['foot']:
	    constraintGroups = constraints.doLimbSegmentListParentConstraint(i_templateNull.msgList_getMessage('controlObjects',False))    
	    """
        for i_obj in ml_controlObjects:
            pBuffer = i_obj.doGroup(maintain=True)
            i_parent = cgmMeta.asMeta(i_obj.parent,'cgmObject',setClass=True)
            i_obj.addAttr('owner',i_parent.mNode,attrType = 'messageSimple',lock=True)

    except Exception,error:raise Exception,"doParentControlObjects | {0}".format(error)


#@r9General.Timer
def updateTemplate2(mModule = None, saveTemplatePose = False, **kws):
    """
    Function to update a skeleton if it's been resized
    """
    try:
        mModule = kws.get['mModule'] or mModule
        saveTemplatePose = kws.get['saveTemplatePose'] or saveTemplatePose

        #if not mModule.isSized():
            #log.warning("'%s' not sized. Can't update"%mModule.getShortName())
            #return False
        if not mModule.isTemplated():
            log.warning("'%s' not templated. Can't update"%mModule.getShortName())
            return False

        if saveTemplatePose:
            mModule.templateSettings_call('store')#Save our pose before destroying anything

        mi_templateNull = mModule.templateNull

        corePosList = mi_templateNull.templateStarterData
        i_root = mi_templateNull.root
        ml_controlObjects = mi_templateNull.msgList_get('controlObjects',asMeta = True)

        #if not cgmMath.isVectorEquivalent(i_templateNull.controlObjects[0].translate,[0,0,0]):
            #raise StandardError,"updateTemplate: doesn't currently support having a moved first template object"
            #return False

        mc.xform(i_root.parent, translation = corePosList[0],worldSpace = True)
        mc.xform(ml_controlObjects[0].parent, translation = corePosList[0],worldSpace = True)

        for i,i_obj in enumerate(ml_controlObjects[1:]):
            log.info(i_obj.getShortName())
            #objConstraints = constraints.returnObjectConstraints(i_obj.parent)
            #if objConstraints:mc.delete(objConstraints) 
            #buffer = search.returnParentsFromObjectToParent(i_obj.mNode,i_root.mNode)
            #i_obj.parent = False
            #if buffer:mc.delete(buffer)
            mc.xform(i_obj.mNode, translation = corePosList[1:][i],worldSpace = True) 

        buffer = search.returnParentsFromObjectToParent(ml_controlObjects[0].mNode,i_root.mNode)
        ml_controlObjects[0].parent = False
        if buffer:mc.delete(buffer)

        doParentControlObjects(mModule)
        doCastPivots(mModule)

        mModule.templateSettings_call('load')#Restore the pose
        return True
    except Exception,error:raise Exception,"updateTemplate | {0}".format(error)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
def getGoodCurveDegree(self):
    try:
        log.debug(">>> getGoodCurveDegree")
        try:
            doCurveDegree = self._mi_templateNull.curveDegree
        except:
            raise ValueError,"Failed to get module curve degree"

        if doCurveDegree == 0:
            doCurveDegree = 1
        else:
            if len(self.corePosList) <= 3:
                doCurveDegree = 1
            #else:
                #doCurveDegree = len(self.corePosList) - 1

        if doCurveDegree > 0:        
            return doCurveDegree
        return False
    except Exception,error:raise Exception,"getGoodCurveDegree | {0}".format(error)

#@r9General.Timer
def returnGeneralDirections(self,objList):
    """
    Get general direction of a list of objects in a module
    """
    try:
        log.debug(">>> returnGeneralDirections")
        
        try:
            self.generalDirection = logic.returnHorizontalOrVertical(objList)
        except Exception,error:
            raise Exception,"[logic fail| error: {0}]".format(error)
        
        if self.generalDirection == 'vertical' and 'leg' not in self._mi_module.moduleType:
            self.worldUpVector = [0,0,-1]
        elif self.generalDirection == 'vertical' and 'leg' in self._mi_module.moduleType:
            self.worldUpVector = [0,0,1]
        else:
            self.worldUpVector = [0,1,0]    
        return [self.generalDirection,self.worldUpVector]
    except Exception,error:
        log.error(objList)
        raise Exception,"[returnGeneralDirections fail | error: {0}]".format(error)


