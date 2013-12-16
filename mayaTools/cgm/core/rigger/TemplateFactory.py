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
reload(attributes)
reload(constraints)
from cgm.core.lib import nameTools
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)
from cgm.core.classes import DraggerContextFactory as dragFactory
reload(dragFactory)
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
reload(mShapeCast)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    #@r9General.Timer
    def __init__(self,mModule = None,forceNew = True,loadTemplatePose = True,tryTemplateUpdate = False, geo = None, **kws): 
        """
        To do:
        Add rotation order settting
        Add module parent check to make sure parent is templated to be able to move forward, or to constrain
        Add any other piece meal data necessary
        Add a cleaner to force a rebuild
        """
        # Get our base info
        #==============	        
        #>>> module null data 
        assert mModule.isModule(),"Not a module"
        self.m = mModule# Link for shortness	
	_str_funcName = "go.__init__(%s)"%self.m.p_nameShort  
	log.info(">>> %s >>> "%(_str_funcName) + "="*75)
	
	#Before something can be templated, we need to see if it has a puppet yet
	if not self.m.getMessage('modulePuppet') and not self.m.getMessage('moduleParent'):
	    log.info(">>> %s >>> Has no modulePuppet or moduleParent. Need to create"%_str_funcName)
	    if self.m.getMessage("helper"):
		self.m.__buildSimplePuppet__()
	    else:
		log.error(">>> %s >>> Has no modulePuppet or moduleParent and no helper"%_str_funcName)		
		return False
	    
	if self.m.mClass in ['cgmEyelids','cgmEyeball']:#Some special objects don't need no stinkin templating!
	    if self.m.getMessage('helper'):
		log.info("%s >>> Helper object found. No templating necessary"%_str_funcName)	    
		return 
	
	try:#Geo -------------------------------------------------------------------------------------------
	    if geo is None:
		try:
		    if not mModule.modulePuppet.getUnifiedGeo():raise StandardError, "go>>> Module puppet missing geo"
		    else:geo = mModule.modulePuppet.getUnifiedGeo()[0]
		except StandardError,error:log.warning("geo failed to find: %s"%(error) + "="*75)  
	    cgmValid.objString(geo,noneValid=True)
	except StandardError,error:log.warning(">>> %s.go >> geo failed : %s"%(self.m.p_nameShort,error))  
	
        log.info("loadTemplatePose: %s"%loadTemplatePose)     
	self._mi_module = self.m
        if tryTemplateUpdate:
            log.info("Trying template update...")
            if updateTemplate(module,**kws):
                if loadTemplatePose:
                    log.info("Trying loadTemplatePose...")                                    
                    self.m.loadTemplatePose()                
                return
        
        if mModule.isTemplated():
            if forceNew:
                mModule.deleteTemplate()
            else:
                log.warning("'%s' has already been templated"%mModule.getShortName())
                return
        
        self.cls = "TemplateFactory.go"
        
        self.moduleNullData = attributes.returnUserAttrsToDict(self.m.mNode)
        self.templateNull = self.m.getMessage('templateNull')[0] or False
	self._i_templateNull = self.m.templateNull#link
        self.i_templateNull = self.m.templateNull#link
        self.rigNull = self.m.getMessage('rigNull')[0] or False
        self.moduleParent = self.moduleNullData.get('moduleParent')
        self.moduleColors = self.m.getModuleColors()
        self.l_coreNames = self.m.coreNames.value
	self.d_coreNamesAttrs = self.m.coreNames.d_indexToAttr
        self.corePosList = self.i_templateNull.templateStarterData
        self.foundDirections = False #Placeholder to see if we have it
        
        assert len(self.l_coreNames) == len(self.corePosList),"coreNames length and corePosList doesn't match"
        
        #>>> part name 
        self.partName = self.m.getPartNameBase()
        self.partType = self.m.moduleType or False
        self._partName = self.m.getPartNameBase()
        self._strShortName = self.m.getShortName() or False    
	
        self.direction = None
        if self.m.hasAttr('cgmDirection'):
            self.direction = self.m.cgmDirection or None
	    
	#Verify we have a puppet and that puppet has a masterControl which we need for or master scale plug
	if not self._mi_module.modulePuppet._verifyMasterControl():
	    raise StandardError,"TemplateFactory.go.__init__ >>> masterControl failed to verify"
	
	self._i_masterControl = self._mi_module.modulePuppet.masterControl
	self._i_masterSettings = self._i_masterControl.controlSettings
	self._i_deformGroup = self._mi_module.modulePuppet.masterNull.deformGroup        

        #>>> template null 
        self.templateNullData = attributes.returnUserAttrsToDict(self.templateNull)
        
        log.debug("Module: %s"%self.m.getShortName())
        log.debug("moduleNullData: %s"%self.moduleNullData)
        log.debug("partType: %s"%self.partType)
        log.debug("direction: %s"%self.direction) 
        log.debug("colors: %s"%self.moduleColors)
        log.debug("coreNames: %s"%self.l_coreNames)
        log.debug("corePosList: %s"%self.corePosList)
        
	#>>>Connect switches
	try: verify_moduleTemplateToggles(self)
	except StandardError,error:
	    raise StandardError,"init.verify_moduleTemplateToggles>> fail: %s"%error	
	
	self.l_strSteps = ['Start','template objects','curve','root control','helpers']
	self.str_progressBar = gui.doStartMayaProgressBar(len(self.l_strSteps))
        try:
	    if self.m.mClass == 'cgmLimb':
		log.debug("mode: cgmLimb Template")
		
		mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[0]), progress=0)    					    
		doMakeLimbTemplate(self)	
		
		if 'ball' in self.l_coreNames and 'ankle' in self.l_coreNames:
		    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,'Cast Pivots'), progress=1)    					    		    
		    doCastPivots(self._mi_module)
		    
	    elif self.m.mClass == 'cgmEyeball':
		log.info("mode: cgmEyeball")
		try:doMakeEyeballTemplate(self)
		except StandardError,error:log.warning(">>> %s.go >> build failed: %s"%(self.m.p_nameShort,error))  
		
	    else:
		log.info(self.m.mClass)
		raise NotImplementedError,"haven't implemented '%s' templatizing yet"%self.m.mClass
	   
	    doTagChildren(self)

	    #>>> store template settings
	    if loadTemplatePose:self.m.loadTemplatePose()	

	except StandardError,error:
	    log.error("%s.go >> build failed! | %s"%(self._strShortName,error))
	
	gui.doEndMayaProgressBar(self.str_progressBar)#Close out this progress bar   	    
        """
	self._i_templateNull.overrideEnabled = 1		
	cgmMeta.cgmAttr(self._i_masterSettings.mNode,'templateVis',lock=False).doConnectOut("%s.%s"%(self._i_templateNull.mNode,'overrideVisibility'))
	cgmMeta.cgmAttr(self._i_masterSettings.mNode,'templateLock',lock=False).doConnectOut("%s.%s"%(self._i_templateNull.mNode,'overrideDisplayType'))    
	"""
        

		
#@r9General.Timer
def verify_moduleTemplateToggles(goInstance):
    """
    Rotate orders
    hips = 3
    """    
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    str_settings = str(self._i_masterSettings.getShortName())
    str_partBase = str(self._partName + '_tmpl')
    str_moduleTemplateNull = str(self._i_templateNull.getShortName())
    
    self._i_masterSettings.addAttr(str_partBase, defaultValue = 0, value = 1, attrType = 'int',minValue = 0, maxValue = 1, keyable = False,hidden = False)
    try:NodeF.argsToNodes("%s.tmplVis = if %s.%s > 0"%(str_moduleTemplateNull,str_settings,str_partBase)).doBuild()
    except StandardError,error:
	raise StandardError,"verify_moduleTemplateToggles>> vis arg fail: %s"%error
    try:NodeF.argsToNodes("%s.tmplLock = if %s.%s == 1:0 else 2"%(str_moduleTemplateNull,str_settings,str_partBase)).doBuild()
    except StandardError,error:
	raise StandardError,"verify_moduleTemplateToggles>> lock arg fail: %s"%error

    self._i_templateNull.overrideEnabled = 1		
    cgmMeta.cgmAttr(self._i_templateNull.mNode,'tmplVis',lock=False).doConnectOut("%s.%s"%(self._i_templateNull.mNode,'overrideVisibility'))
    cgmMeta.cgmAttr(self._i_templateNull.mNode,'tmplLock',lock=False).doConnectOut("%s.%s"%(self._i_templateNull.mNode,'overrideDisplayType'))    
    #nodeF.argsToNodes("%s.templateLock = if %s.templateStuff == 1:0 else 2"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()	

    return True



#>>>> Pivots stuff 
#==========================================================================================
d_pivotAttrs = {'foot':['pivot_toe','pivot_heel','pivot_ball','pivot_inner','pivot_outer']}

#@r9General.Timer
def hasPivots(self):
    """
    If a module needs pivots and has them, returns them. Checks if a module has necessary pivots.
    """
    assert self.isModule(),"%s.hasPivots>>> not a module"%self.getShortName()
    l_coreNames = self.coreNames.value
    i_templateNull = self.templateNull
    l_found = []
    l_missing = []  
    
    if 'ball' in l_coreNames and 'ankle' in l_coreNames:
	for attr in d_pivotAttrs['foot']:
	    buffer = i_templateNull.getMessage(attr)
	    if buffer:l_found.append(buffer[0])
	    else:
		l_missing.append(attr)
		log.warning("%s.hasPivots>>> missing : '%s'"%(self.getShortName(),attr))
	if l_missing:
	    log.error("%s.hasPivots>>> found: '%s' | missing: '%s'"%(self.getShortName(),l_found,l_missing))
	    return False
	return l_found
    log.error("%s.hasPivots>>> not a known module that needs pivots! |"%(self.getShortName()))
    return False  

#@r9General.Timer
def doCastPivots(self):
    assert self.isModule(),"%s.doCastPivots>>> not a module"%self.getShortName()
    l_coreNames = self.coreNames.value
    
    pivotCheck = hasPivots(self)#If we already have pivots
    if pivotCheck:
	for o in pivotCheck:mc.delete(o)#delete
    
    if 'ball' in l_coreNames and 'ankle' in l_coreNames:
	log.warning("Need to cast pivots!")
	try:
	    mShapeCast.go(self,['footPivots'])
	except StandardError,error:
	    raise StandardError,"%s.doCastPivots>>> failure! | %s"%(self.getShortName(),error)
	
    log.error("%s.doCastPivots>>> not a known module that needs pivots! |"%(self.getShortName()))
    return False

#@r9General.Timer
def doTagChildren(self): 
    try:
        for obj in self.i_templateNull.getAllChildren():
            i_obj = cgmMeta.cgmNode(obj)
            i_obj.doStore('templateOwner',self.templateNull)
    except StandardError,error:
        log.warning(error) 
        
#@r9General.Timer
def returnModuleBaseSize(self):
    log.debug(">>> returnModuleSize")
    size = 12
    if self.getState() < 1:
        log.error("'%s' has not been sized. Cannot find base size"%self.getShortName())
        return False
    if not self.getMessage('moduleParent') and self.getMessage('modulePuppet'):
        log.debug("Sizing from modulePuppet")
        return size
    elif self.getMessage('moduleParent'):#If it has a parent
        log.debug("Sizing from moduleParent")
        i_templateNull = self.templateNull #Link
        i_parent = self.moduleParent #Link
        parentState = i_parent.getState()
        if i_parent.isTemplated():#If the parent has been templated, it makes things easy
            log.debug("Parent has been templated...")
            nameCount = len(self.coreNames.value) or 1
            l_parentTemplateObjects = i_parent.templateNull.msgList_get('controlObjects',asMeta = False)
            log.debug("l_parentTemplateObjects: %s"%l_parentTemplateObjects)
            log.debug("firstPos: %s"%i_templateNull.templateStarterData[0])
            closestObj = distance.returnClosestObjectFromPos(i_templateNull.templateStarterData[0],l_parentTemplateObjects)
            #Find the closest object from the parent's template object
            log.debug("closestObj: %s"%closestObj)
            
            boundingBoxSize = distance.returnBoundingBoxSize(closestObj,True)
            log.info("bbSize = %s"%max(boundingBoxSize))
            
            size = max(boundingBoxSize) *.6
            if i_parent.moduleType == 'clavicle':
                return size * 2   
            
            if self.moduleType == 'clavicle':
                return size * .5
            elif self.moduleType == 'head':
                return size * .75
            elif self.moduleType == 'neck':
                return size * .5
            elif self.moduleType == 'leg':
                return size * 1.5
            elif self.moduleType in ['finger','thumb']:
                return size * .75                

        else:
            log.debug("Parent has not been templated...")          
    else:
        pass
    return size 

#@r9General.Timer
def constrainToParentModule(self):
    """
    Pass a module class. Constrains template root to parent's closest template object
    """
    log.debug(">>> constrainToParentModule")
    if not self.isTemplated():
        log.error("Must be template state to contrainToParentModule: '%s' "%self.getShortName())
        return False
    
    if not self.getMessage('moduleParent'):
        return False
    else:
        log.debug("looking for moduleParent info")
        i_templateNull = self.templateNull #Link
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
            l_constraints = cgmMeta.cgmObject(i_templateNull.root.parent).getConstraintsTo()
            if cgmMeta.cgmObject(i_templateNull.root.parent).isConstrainedBy(closestObj):
                log.debug("Already constrained!")
                return True
            elif l_constraints:mc.delete(l_constraints)
                
            return constraints.doConstraintObjectGroup(closestObj,group = i_templateNull.root.parent,constraintTypes=['point'])
        else:
            log.debug("Parent has not been templated...")           
            return False
	
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
    log.debug(">>> doMakeLimbTemplate")
    assert self.cls == 'TemplateFactory.go',"Not a TemlateFactory.go instance!"
    
    #Gather limb specific data and check
    #==============
    mi_helper = self.m.helper
    if not mi_helper:
	raise StandardError,"No helper found!"
    
    b_irisControl = mi_helper.irisHelper
    b_pupilControl = mi_helper.pupilHelper
    
    mi_helper.parent = self.m.templateNull
    
    
    return True

@cgmGeneral.Timer
def doMakeLimbTemplate(self):  
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
    
    #Gather limb specific data and check
    #==============
    self.curveDegree = self.i_templateNull.curveDegree
    self.rollOverride = self.i_templateNull.rollOverride
    
    doCurveDegree = getGoodCurveDegree(self)
    if not doCurveDegree:raise ValueError,"Curve degree didn't query"
    
    #>>>Scale stuff
    size = returnModuleBaseSize(self.m)
    
    lastCountSizeMatch = len(self.corePosList) -1
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Making the template objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[1]), progress=1)    					    
    
    templHandleList = []
    self.ml_controlObjects = []
    self.i_locs = []
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
        i_obj = cgmMeta.cgmObject( curves.createControlCurve('sphere',(size * sizeMultiplier)) )
        i_obj.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
        
        curves.setCurveColorByName(i_obj.mNode,self.moduleColors[0])
	
	i_obj.doStore('cgmName','%s.%s'%(self.m.coreNames.mNode,self.d_coreNamesAttrs[i]))        
        #i_obj.addAttr('cgmName',value = str(self.l_coreNames[i]), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
        if self.direction != None:
            i_obj.addAttr('cgmDirection',value = self.direction,attrType = 'string',lock=True)  
        i_obj.addAttr('cgmType',value = 'templateObject', attrType = 'string',lock=True) 
        i_obj.doName()#Name it
        
        mc.move (pos[0], pos[1], pos[2], [i_obj.mNode], a=True)
        i_obj.parent = self.templateNull
        
        #>>> Loc it and store the loc
        #i_loc = cgmMeta.cgmObject( i_obj.doLoc() )
        i_loc =  i_obj.doLoc()
        i_loc.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
        i_loc.addAttr('cgmName',value = self.m.getShortName(), attrType = 'string', lock=True) #Add name tag
        i_loc.addAttr('cgmType',value = 'templateCurveLoc', attrType = 'string', lock=True) #Add Type
        i_loc.v = False # Turn off visibility
        i_loc.doName()
        
        self.i_locs.append(i_loc)
        i_obj.connectChildNode(i_loc.mNode,'curveLoc','owner')
        i_loc.parent = self.templateNull#parent to the templateNull
        
        mc.pointConstraint(i_obj.mNode,i_loc.mNode,maintainOffset = False)#Point contraint loc to the object
                    
        templHandleList.append (i_obj.mNode)
        self.ml_controlObjects.append(i_obj)
        
    #>> Make the curve
    #============================= 
    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[2]), progress=2)    					        
    i_crv = cgmMeta.cgmObject( mc.curve (d=doCurveDegree, p = self.corePosList , os=True) )
    i_crv.addAttr('mClass','cgmObject',lock=True)#tag it so it can initialize later
    
    i_crv.addAttr('cgmName',value = str(self.m.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
    if self.direction != None:
        i_crv.addAttr('cgmDirection',value = self.direction, attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug

    i_crv.addAttr('cgmType',value = 'templateCurve', attrType = 'string', lock=True)
    curves.setCurveColorByName(i_crv.mNode,self.moduleColors[0])
    i_crv.parent = self.templateNull    
    i_crv.doName()
    i_crv.setDrawingOverrideSettings({'overrideEnabled':1,'overrideDisplayType':2},True)
        
    for i,i_obj in enumerate(self.ml_controlObjects):#Connect each of our handles ot the cv's of the curve we just made
        mc.connectAttr ( (i_obj.curveLoc.mNode+'.translate') , ('%s%s%i%s' % (i_crv.mNode, '.controlPoints[', i, ']')), f=True )
        
    
    self.foundDirections = returnGeneralDirections(self,templHandleList)
    log.debug("directions: %s"%self.foundDirections )
    
    #>> Create root control
    #=============================  
    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[3]), progress=3)    					        
    
    rootSize = (distance.returnBoundingBoxSizeToAverage(templHandleList[0],True)*1.25)    
    i_rootControl = cgmMeta.cgmObject( curves.createControlCurve('cube',rootSize) )
    i_rootControl.addAttr('mClass','cgmObject',lock=True)
    
    curves.setCurveColorByName(i_rootControl.mNode,self.moduleColors[0])
    i_rootControl.addAttr('cgmName',value = str(self.m.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug    
    i_rootControl.addAttr('cgmType',value = 'templateRoot', attrType = 'string', lock=True)
    if self.direction != None:
        i_rootControl.addAttr('cgmDirection',value = self.direction, attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug
    i_rootControl.doName()

    #>>> Position it
    if self.m.moduleType in ['clavicle']:
        position.movePointSnap(i_rootControl.mNode,templHandleList[0])
    else:
        position.movePointSnap(i_rootControl.mNode,templHandleList[0])
    
    #See if there's a better way to do this
    log.debug("templHandleList: %s"%templHandleList)
    if self.m.moduleType not in ['foot']:
        if len(templHandleList)>1:
            log.info("setting up constraints...")        
            constBuffer = mc.aimConstraint(templHandleList[-1],i_rootControl.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = self.worldUpVector, worldUpType = 'vector' )
            mc.delete (constBuffer[0])    
        elif self.m.getMessage('moduleParent'):
            #l_parentTemplateObjects =  self.m.moduleParent.templateNull.getMessage('controlObjects')
            helper = self.m.moduleParent.templateNull.msgList_get('controlObjects',asMeta = True)[-1].helper.mNode
            if helper:
                log.info("helper: %s"%helper)
                constBuffer = mc.orientConstraint( helper,i_rootControl.mNode,maintainOffset = False)
                mc.delete (constBuffer[0])    
    
    i_rootControl.parent = self.templateNull
    i_rootControl.doGroup(maintain=True)
    
    
    #>> Store objects
    #=============================      
    self.i_templateNull.curve = i_crv.mNode
    self.i_templateNull.root = i_rootControl.mNode
    self.i_templateNull.msgList_connect(templHandleList,'controlObjects')
    
    self.i_rootControl = i_rootControl#link to carry

    #>> Orientation helpers
    #=============================      
    mc.progressBar(self.str_progressBar, edit=True, status = "%s >>Template>> step:'%s' "%(self._strShortName,self.l_strSteps[3]), progress=3)    					            
    """ Make our Orientation Helpers """
    doCreateOrientationHelpers(self)
    doParentControlObjects(self.m)

    #if self.m.getMessage('moduleParent'):#If we have a moduleParent, constrain it
        #constrainToParentModule(self.m)
	
    doOrientTemplateObjectsToMaster(self.m)
    
    return True

def doOrientTemplateObjectsToMaster(self):
    log.info(">>> %s.doOrientTemplateObjectsToMaster >> "%self.p_nameShort + "="*75)            	
    i_rootOrient = self.templateNull.orientRootHelper
    for i_obj in self.templateNull.msgList_get('controlObjects',asMeta = True):
	#orient the group above
	Snap.go(i_obj.parent,i_obj.helper.mNode,move=False,orient=True)
    
#@r9General.Timer
def doCreateOrientationHelpers(self):
    """ 
    """
    log.debug(">>> addOrientationHelpers")
    assert self.cls == 'TemplateFactory.go',"Not a TemlateFactory.go instance!"
    assert mc.objExists(self.m.mNode),"module no longer exists"
    #Gather limb specific data and check
    #===================================
    #'orientHelpers':'messageSimple',#Orientation helper controls
    #'orientRootHelper':'messageSimple',#Root orienation helper

    helperObjects = []
    helperObjectGroups = []
    returnBuffer = []
    root = self.i_templateNull.getMessage('root')[0]
    objects =  self.i_templateNull.msgList_get('controlObjects',asMeta = False)
    log.debug(root)
    log.debug(objects)
    log.debug(self.foundDirections)
    
    #>> Create orient root control
    #=============================     
    orientRootSize = (distance.returnBoundingBoxSizeToAverage(root,True)*2.5)    
    i_orientRootControl = cgmMeta.cgmObject( curves.createControlCurve('circleArrow1',orientRootSize) )
    i_orientRootControl.addAttr('mClass','cgmObject',lock=True)
    
    curves.setCurveColorByName(i_orientRootControl.mNode,self.moduleColors[0])
    i_orientRootControl.addAttr('cgmName',value = str(self.m.getShortName()), attrType = 'string', lock=True)#<<<<<<<<<<<FIX THIS str(call) when Mark fixes bug    
    i_orientRootControl.addAttr('cgmType',value = 'templateOrientRoot', attrType = 'string', lock=True)
    i_orientRootControl.doName()
    
    #>>> Store it
    i_orientRootControl.connectParent(self.templateNull,'orientRootHelper','owner')#Connect it to it's object      
    
    #>>> Position and set up follow groups
    position.moveParentSnap(i_orientRootControl.mNode,root)    
    i_orientRootControl.parent = root #parent it to the root
    i_orientRootControl.doGroup(maintain = True)#group while maintainting position
    
    mc.pointConstraint(objects[0],i_orientRootControl.parent,maintainOffset = False)#Point contraint orient control to the first helper object
    mc.aimConstraint(objects[-1],i_orientRootControl.parent,maintainOffset = True, weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpObject = root, worldUpType = 'objectRotation' )
    attributes.doSetLockHideKeyableAttr(i_orientRootControl.mNode,True,False,False,['tx','ty','tz','rx','ry','sx','sy','sz','v'])
    
    self.i_orientHelpers = []#we're gonna store the instances so we can get them all after parenting and what not
    #>> Sub controls
    #============================= 
    if len(objects) == 1:#If a single handle module
        i_obj = cgmMeta.cgmObject(objects[0])
        position.moveOrientSnap(objects[0],root)
    else:
        for i,obj in enumerate(objects):
            log.debug("on %s"%(mc.ls(obj,shortNames=True)[0]))
            #>>> Create and color      
            size = (distance.returnBoundingBoxSizeToAverage(obj,True)*2) # Get size
            i_obj = cgmMeta.cgmObject(curves.createControlCurve('circleArrow2Axis',size))#make the curve
            i_obj.addAttr('mClass','cgmObject',lock=True)
            curves.setCurveColorByName(i_obj.mNode,self.moduleColors[1])
            #>>> Tag and name
            i_obj.doCopyNameTagsFromObject(obj)
            i_obj.doStore('cgmType','templateOrientHelper',True)        
            i_obj.doName()
            
            #>>> Link it to it's object and append list for full store
            i_obj.connectParent(obj,'helper','owner')#Connect it to it's object      
            self.i_orientHelpers.append(i_obj)
            log.debug(i_obj.owner)
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
	    
    #>>> Get data ready to go forward
    bufferList = []
    for o in self.i_orientHelpers:
        bufferList.append(o.mNode)
    self.i_templateNull.msgList_connect(bufferList,'orientHelpers')
    self.i_orientRootHelper = i_orientRootControl
    log.debug("orientRootHelper: [%s]"%self.i_templateNull.orientRootHelper.getShortName())   
    log.debug("orientHelpers: %s"%self.i_templateNull.msgList_getMessage('orientHelpers'))

    return True

#@r9General.Timer
def doParentControlObjects(self):
    """
    Needs instanced module
    """
    log.info(">>> doParentControlObjects")
    i_templateNull = self.templateNull#link for speed
    i_root = i_templateNull.root
    ml_controlObjects = i_templateNull.msgList_get('controlObjects',asMeta = True)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>> Parent objects
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    for i_obj in ml_controlObjects:
        i_obj.parent = i_root.mNode
        
    #ml_controlObjects[0].doGroup(maintain=True)#Group to zero out
    #ml_controlObjects[-1].doGroup(maintain=True)  
    
    log.debug(i_templateNull.msgList_getMessage('controlObjects',False))
    """
    if self.moduleType not in ['foot']:
        constraintGroups = constraints.doLimbSegmentListParentConstraint(i_templateNull.msgList_getMessage('controlObjects',False))    
	"""
    for i_obj in ml_controlObjects:
	pBuffer = i_obj.doGroup(maintain=True)
	i_parent = cgmMeta.cgmObject(i_obj.parent,setClass=True)
	i_obj.addAttr('owner',i_parent.mNode,attrType = 'messageSimple',lock=True)
         
    return

#@r9General.Timer
def updateTemplate(self,saveTemplatePose = False,**kws):
    """
    Function to update a skeleton if it's been resized
    """
    if not self.isSized():
        log.warning("'%s' not sized. Can't update"%self.getShortName())
        return False
    if not self.isTemplated():
        log.warning("'%s' not templated. Can't update"%self.getShortName())
        return False
    
    if saveTemplatePose:self.storeTemplatePose()#Save our pose before destroying anything
        
    i_templateNull = self.templateNull#link for speed
    corePosList = i_templateNull.templateStarterData
    i_root = i_templateNull.root
    ml_controlObjects = i_templateNull.msgList_get('controlObjects',asMeta = True)
    
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
    
    doParentControlObjects(self)
    doCastPivots(self)
    
    self.loadTemplatePose()#Restore the pose
    return True



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
def getGoodCurveDegree(self):
    log.debug(">>> getGoodCurveDegree")
    try:
        doCurveDegree = self.i_templateNull.curveDegree
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

#@r9General.Timer
def returnGeneralDirections(self,objList):
    """
    Get general direction of a list of objects in a module
    """
    log.debug(">>> returnGeneralDirections")

    self.generalDirection = logic.returnHorizontalOrVertical(objList)
    if self.generalDirection == 'vertical' and 'leg' not in self.m.moduleType:
        self.worldUpVector = [0,0,-1]
    elif self.generalDirection == 'vertical' and 'leg' in self.m.moduleType:
        self.worldUpVector = [0,0,1]
    else:
        self.worldUpVector = [0,1,0]    
    return [self.generalDirection,self.worldUpVector]



