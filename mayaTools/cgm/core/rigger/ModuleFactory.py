import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_CoreUtils as r9Core
from Red9.core import Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.rigger import JointFactory as jFactory
from cgm.core.rigger import RigFactory as mRig
from cgm.lib import (modules,curves,distance,attributes)
from cgm.lib.ml import ml_resetChannels

reload(attributes)
from cgm.core.lib import nameTools
from cgm.core.classes import DraggerContextFactory as dragFactory
reload(dragFactory)

##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Shared libraries
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
l_moduleStates = ['define','size','template','skeleton','rig']
l_modulesClasses = ['cgmModule','cgmLimb','cgmEyeball']
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@cgmGeneral.Timer
def isSized(self):
    """
    Return if a moudle is sized or not
    """
    log.debug(">>> %s.isSized() >> "%(self.p_nameShort) + "="*75) 		                                	                        
    handles = self.templateNull.handles
    i_coreNames = self.coreNames
    if len(i_coreNames.value) < handles:
        log.debug("%s.isSized>>> Not enough names for handles"%self.getShortName())
        return False
    if len(i_coreNames.value) > handles:
        log.debug("%s.isSized>>> Not enough handles for names"%self.getShortName())	
        return False
    if self.templateNull.templateStarterData:
	if len(self.templateNull.templateStarterData) == handles:
	    for i,pos in enumerate(self.templateNull.templateStarterData):
		if not pos:
		    log.debug("%s.isSized>>> [%s] has no data"%(self.getShortName(),i))			    
		    return False
	    return True
	else:
	    log.debug("%s.isSized>>> %i is not == %i handles necessary"%(self.getShortName(),len(self.templateNull.templateStarterData),handles))			    	    
	    return False
    else:
	log.debug("%s.isSized>>> No template starter data found"%self.getShortName())	
    return False
    
def deleteSizeInfo(self,*args,**kws):
    log.debug(">>> %s.deleteSizeInfo() >> "%(self.p_nameShort) + "="*75) 		                                	                            
    self.templateNull.__setattr__('templateStarterData','',lock=True)
    
@cgmGeneral.Timer    
def doSize(self,sizeMode='normal',geo = [],posList = [],*args,**kws):
    """
    Size a module
    1) Determine what points we need to gather
    2) Initiate draggerContextFactory
    3) Prompt user per point
    4) at the end of the day have a pos list the length of the handle list
    
    @ sizeMode
    'all' - pick every handle position
    'normal' - first/last, if child, will use last position of parent as first
    'manual' - provide a pos list to size from
    
    TODO:
    Add option for other modes
    Add geo argument that can be passed for speed
    Add clamp on value
    Add a way to pull size info from a mirror module
    """
    log.debug(">>> %s.doSize(sizeMode = %s, geo = %s, posList = %s) >> "%(self.p_nameShort,sizeMode,geo,posList) + "="*75) 		                                	                                    
    clickMode = {"heel":"surface"}    
    i_coreNames = self.coreNames
    #Gather info
    #==============      
    handles = self.templateNull.handles
    if len(i_coreNames.value) == handles:
        names = i_coreNames.value
    else:
        log.warning("Not enough names. Generating")
        names = getGeneratedCoreNames(self)
    if not geo and not self.getMessage('helper'):
        geo = self.modulePuppet.getGeo()
    log.debug("Handles: %s"%handles)
    log.debug("Names: %s"%names)
    log.debug("Puppet: %s"%self.getMessage('modulePuppet'))
    log.debug("Geo: %s"%geo)
    log.debug("sizeMode: %s"%sizeMode)
    
    i_module = self #Bridge holder for our module class to go into our sizer class
    
    #Variables
    #============== 
    if sizeMode == 'manual':#To allow for a pos list to be input
        if not posList:
            log.error("Must have posList arg with 'manual' sizeMode!")
            return False
        
        if len(posList) < handles:
            log.warning("Creating curve to get enough points")                
            curve = curves.curveFromPosList(posList)
            mc.rebuildCurve (curve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0,s=(handles-1), d=1, tol=0.001)
            posList = curves.returnCVsPosList(curve)#Get the pos of the cv's
            mc.delete(curve) 
            
        self.templateNull.__setattr__('templateStarterData',posList,lock=True)
        log.debug("'%s' manually sized!"%self.getShortName())
        return True
            
    elif sizeMode == 'normal':
        if len(names) > 1:
            namesToCreate = names[0],names[-1]
        else:
            namesToCreate = names
        log.debug("Names: %s"%names)
    else:
        namesToCreate = names        
        sizeMode = 'all'
       
    class moduleSizer(dragFactory.clickMesh):
        """Sublass to get the functs we need in there"""
        def __init__(self,i_module = i_module,**kws):
            log.debug(">>> moduleSizer.__init__")    
            if kws:log.info("kws: %s"%str(kws))
            
            super(moduleSizer, self).__init__(**kws)
            self.i_module = i_module
	    self.toCreate = namesToCreate
            log.info("Please place '%s'"%self.toCreate[0])
            
        def release(self):
            if len(self.l_return)< len(self.toCreate)-1:#If we have a prompt left
                log.info("Please place '%s'"%self.toCreate[len(self.l_return)+1])            
            dragFactory.clickMesh.release(self)

            
        def finalize(self):
            log.debug("returnList: %s"% self.l_return)
            log.debug("createdList: %s"% self.l_created)   
            buffer = [] #self.i_module.templateNull.templateStarterData
            log.debug("starting data: %s"% buffer)
            
            #Make sure we have enough points
            #==============  
            handles = self.i_module.templateNull.handles
            if len(self.l_return) < handles:
                log.warning("Creating curve to get enough points")                
                curve = curves.curveFromPosList(self.l_return)
                mc.rebuildCurve (curve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0,s=(handles-1), d=1, tol=0.001)
                self.l_return = curves.returnCVsPosList(curve)#Get the pos of the cv's
                mc.delete(curve)

            #Store info
            #==============                  
            for i,p in enumerate(self.l_return):
                buffer.append(p)#need to ensure it's storing properly
                #log.info('[%s,%s]'%(buffer[i],p))
                
            #Store locs
            #==============  
            log.debug("finish data: %s"% buffer)
            self.i_module.templateNull.__setattr__('templateStarterData',buffer,lock=True)
            #self.i_module.templateNull.templateStarterData = buffer#store it
            log.info("'%s' sized!"%self.i_module.getShortName())
            dragFactory.clickMesh.finalize(self)
        
    #Start up our sizer    
    return moduleSizer(mode = 'midPoint',
                       mesh = geo,
                       create = 'locator',
                       toCreate = namesToCreate)
    
@cgmGeneral.Timer
def doSetParentModule(self,moduleParent,force = False):
    """
    Set a module parent of a module

    module(string)
    """
    #See if parent exists and is a module, if so...
    #>>>buffer children
    #>>>see if already connected
    #>>Check existance
        #==============	
    #Get our instance
    log.debug(">>> %s.doSetParentModule(moduleParent = %s, force = %s) >> "%(self.p_nameShort,moduleParent,force) + "="*75) 		                                	                            
    
    try:
        moduleParent.mNode#See if we have an instance

    except:
        if mc.objExists(moduleParent):
            moduleParent = r9Meta.MetaClass(moduleParent)#initialize
        else:
            log.warning("'%s' doesn't exist"%moduleParent)#if it doesn't initialize, nothing is there		
            return False	

    #Logic checks
    #==============
    if not moduleParent.hasAttr('mClass'):
        log.warning("'%s' lacks an mClass attr"%module.mNode)	    
        return False

    if moduleParent.mClass not in ['cgmModule','cgmLimb']:
        log.warning("'%s' is not a recognized module type"%moduleParent.mClass)
        return False

    if not moduleParent.hasAttr('moduleChildren'):#Quick check
        log.warning("'%s'doesn't have 'moduleChildren' attr"%moduleParent.getShortName())#if it doesn't initialize, nothing is there		
        return False	

    buffer = copy.copy(moduleParent.getMessage('moduleChildren')) or []#Buffer till we have have append functionality	

    if self.mNode in buffer:
        log.warning("'%s' already connnected to '%s'"%(self.mNode,moduleParent.getShortName()))
        return False

        #Connect
        #==============	
    else:
        log.debug("Current children: %s"%moduleParent.getMessage('moduleChildren'))
        log.debug("Adding '%s'!"%self.getShortName())    

        buffer.append(self.mNode) #Revist when children has proper add/remove handling
        moduleParent.moduleChildren = buffer
        self.moduleParent = moduleParent.mNode
        #if moduleParent.getMessage('modulePuppet'):
            #moduleParent.modulePuppet.connectModule(self.mNode) 
            
        #del moduleParent.moduleChildren #Revist when children has proper add/remove handling
        #moduleParent.connectChildren(buffer,'moduleChildren','moduleParent',force=force)#Connect
        #if moduleParent.getMessage('modulePuppet'):
            #moduleParent.modulePuppet[0].connectModule(self)
            ##self.__setMessageAttr__('modulePuppet',moduleParent.getMessage('modulePuppet')[0])#Connect puppet to 

    self.parent = moduleParent.parent
    return True


@cgmGeneral.Timer
def getGeneratedCoreNames(self):
    """ 
    Generate core names for a module and return them

    self MUST be cgmModule

    RETURNS:
    generatedNames(list)
    
    TODO:
    Where to store names?
    """
    log.debug(">>> %s.getGeneratedCoreNames() >> "%(self.p_nameShort) + "="*75) 		                                	                            
    log.debug("Generating core names via ModuleFactory - '%s'"%self.getShortName())
    i_coreNames = self.coreNames

    ### check the settings first ###
    partType = self.moduleType
    log.debug("%s partType is %s"%(self.getShortName(),partType))
    settingsCoreNames = modules.returncgmTemplateCoreNames(partType)
    handles = self.templateNull.handles
    partName = nameTools.returnRawGeneratedName(self.mNode,ignore=['cgmType','cgmTypeModifier'])

    ### if there are no names settings, genearate them from name of the limb module###
    generatedNames = []
    if settingsCoreNames == False: 
	if self.moduleType.lower() == 'eyeball':
	    generatedNames.append('%s' % (partName))	    
	else:
	    cnt = 1
	    for handle in range(handles):
		generatedNames.append('%s%s%i' % (partName,'_',cnt))
		cnt+=1
    elif int(self.templateNull.handles) > (len(settingsCoreNames)):
        log.debug(" We need to make sure that there are enough core names for handles")       
        cntNeeded = self.templateNull.handles  - len(settingsCoreNames) +1
        nonSplitEnd = settingsCoreNames[len(settingsCoreNames)-2:]
        toIterate = settingsCoreNames[1]
        iterated = []
        for i in range(cntNeeded):
            iterated.append('%s%s%i' % (toIterate,'_',(i+1)))
        generatedNames.append(settingsCoreNames[0])
        for name in iterated:
            generatedNames.append(name)
        for name in nonSplitEnd:
            generatedNames.append(name) 

    else:
        log.debug(" Culling from settingsCoreNames")        
        generatedNames = settingsCoreNames[:self.templateNull.handles]

    #figure out what to do with the names
    i_coreNames.value = generatedNames
    """
    if not self.templateNull.templateStarterData:
        buffer = []
        for n in generatedNames:
            buffer.append([str(n),[]])
        self.templateNull.templateStarterData = buffer
    else:
        for i,pair in enumerate(self.templateNull.templateStarterData):
            pair[0] = generatedNames[i]    
    """
        
    return generatedNames
#=====================================================================================================
#>>> Rig
#=====================================================================================================
@cgmGeneral.Timer
def doRig(self,*args,**kws):
    log.debug(">>> %s.doRig() >> "%(self.p_nameShort) + "="*75) 		            
    if not isSkeletonized(self):
        log.warning("%s.doRig>>> Not skeletonized"%self.getShortName())
        return False      
    if self.moduleParent and not isRigged(self.moduleParent):
	log.warning("%s.doRig>>> Parent module is not rigged: '%s'"%(self.getShortName(),self.moduleParent.getShortName()))
        return False 
    
    mRig.go(self,*args,**kws)      
    if not isRigged(self):
	log.warning("%s.doRig>>> Failed To Rig"%self.getShortName())
        return False
    
    rigConnect(self)
    
    return True
    #except StandardError,error:
        #log.warning(error)    

@cgmGeneral.Timer
def isRigged(self):
    """
    Return if a module is rigged or not
    """
    log.debug(">>> %s.isRigged() >> "%(self.p_nameShort) + "="*75) 
    """
    if not isSkeletonized(self):
        log.warning("%s.isRigged>>> Not skeletonized"%self.getShortName())
        return False   """
    i_coreNames = self.coreNames    
    coreNamesValue = i_coreNames.value
    i_rigNull = self.rigNull
    str_shortName = self.getShortName()
    
    ml_rigJoints = i_rigNull.msgList_get('rigJoints',asMeta = True)
    l_rigJoints = [i_j.p_nameShort for i_j in ml_rigJoints]
    l_skinJoints = mRig.get_skinJoints(self,asMeta=False)
    
    if not ml_rigJoints:
        log.debug("moduleFactory.isRigged('%s')>>>> No rig joints"%str_shortName)
	i_rigNull.version = ''#clear the version	
        return False
    
    #Not a fan of this test
    if not ml_rigJoints[0].getConstraintsTo():
	return False
        
    if len( l_skinJoints ) < len( l_rigJoints ):
        log.warning("moduleFactory.isRigged('%s')>>>> %s != %s. Not enough rig joints"%(str_shortName,len(l_skinJoints),len(l_rigJoints)))
	i_rigNull.version = ''#clear the version        
        return False
    
    for attr in ['controlsFK','controlsAll']:
        if not i_rigNull.msgList_get(attr,asMeta = False):
            log.debug("moduleFactory.isRigged('%s')>>>> No data found on '%s'"%(str_shortName,attr))
	    i_rigNull.version = ''#clear the version            
            return False    
            
    return True

@cgmGeneral.Timer
def rigDelete(self,*args,**kws):
    #1 zero out controls
    #2 see if connected, if so break connection
    #3 delete everything but the rig - rigNull, deform stuff
    #Data get
    log.debug(">>> %s.rigDelete() >> "%(self.p_nameShort) + "="*75) 		                                	                            
    
    str_shortName = self.getShortName()
    
    #if not isRigged(self):
        #raise StandardError,"moduleFactory.rigDelete('%s')>>>> Module not rigged"%(str_shortName)
    log.debug(">>> %s.rigDelete() >> "%(self.p_nameShort) + "="*75) 		            
    
    if isRigConnected(self):
	rigDisconnect(self)#Disconnect
    """
    try:
        objList = returnTemplateObjects(self)
        if objList:
            mc.delete(objList)
        for obj in self.templateNull.getChildren():
            mc.delete(obj)
        return True
    except StandardError,error:
        log.warning(error)"""
    i_rigNull = self.rigNull
    rigNullStuff = i_rigNull.getAllChildren()
    #Build a control master group List
    l_masterGroups = []
    for i_obj in i_rigNull.msgList_get('controlsAll'):
	if i_obj.hasAttr('masterGroup'):
	    l_masterGroups.append(i_obj.getMessage('masterGroup',False)[0])
	    
    log.debug("moduleFactory.rigDisconnect('%s')>> masterGroups found: %s"%(str_shortName,l_masterGroups))  
    for obj in l_masterGroups:
	if mc.objExists(obj):
	    mc.delete(obj)
	    
    if self.getMessage('deformNull'):
	mc.delete(self.getMessage('deformNull'))
	
    mc.delete(self.rigNull.getChildren())
    
    i_rigNull.version = ''#clear the version
    
    return True

@cgmGeneral.Timer
def isRigConnected(self,*args,**kws):
    log.debug(">>> %s.isRigConnected() >> "%(self.p_nameShort) + "="*75) 		                
    str_shortName = self.getShortName()
    if not isRigged(self):
        log.debug("moduleFactory.isRigConnected('%s')>>>> Module not rigged"%(str_shortName))
	return False
    i_rigNull = self.rigNull
    ml_rigJoints = i_rigNull.msgList_get('rigJoints',asMeta = True)
    ml_skinJoints = mRig.get_skinJoints(self,asMeta=True)
    
    for i,i_jnt in enumerate(ml_skinJoints):
	try:
	    if not i_jnt.isConstrainedBy(ml_rigJoints[i].mNode):
		log.debug("'%s'>>not constraining>>'%s'"%(ml_rigJoints[i].getShortName(),i_jnt.getShortName()))
		return False
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"moduleFactory.isRigConnected('%s')>> Joint failed: %s"%(str_shortName,i_jnt.getShortName())

    return True

@cgmGeneral.Timer
def rigConnect(self,*args,**kws):
    log.debug(">>> %s.rigConnect() >> "%(self.p_nameShort) + "="*75) 		                    
    str_shortName = self.getShortName()
    if not isRigged(self):
        raise StandardError,"moduleFactory.rigConnect('%s')>>>> Module not rigged"%(str_shortName)
    if isRigConnected(self):
        raise StandardError,"moduleFactory.rigConnect('%s')>>>> Module already connected"%(str_shortName)
    
    i_rigNull = self.rigNull
    ml_rigJoints = i_rigNull.msgList_get('rigJoints',asMeta = True)
    ml_skinJoints = mRig.get_skinJoints(self,asMeta=True)

    if len(ml_skinJoints)!=len(ml_rigJoints):
	raise StandardError,"moduleFactory.rigConnect('%s')>> Rig/Skin joint chain lengths don't match"%self.getShortName()
    
    for i,i_jnt in enumerate(ml_skinJoints):
	try:
	    log.debug("'%s'>>drives>>'%s'"%(ml_rigJoints[i].getShortName(),i_jnt.getShortName()))
	    pntConstBuffer = mc.pointConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
	    orConstBuffer = mc.orientConstraint(ml_rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
	    attributes.doConnectAttr((ml_rigJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))
	except:
	    raise StandardError,"moduleFactory.rigConnect('%s')>> Joint failed: %s"%i_jnt.getShortName()

    return True

@cgmGeneral.Timer
def rigDisconnect(self,*args,**kws):
    """
    See if rigged and connected. Zero. Gather constraints, delete, break connections
    """
    log.debug(">>> %s.rigDisconnect() >> "%(self.p_nameShort) + "="*75) 		                        
    str_shortName = self.getShortName()
    if not isRigged(self):
        raise StandardError,"moduleFactory.rigDisconnect('%s')>>>> Module not rigged"%(str_shortName)
    if not isRigConnected(self):
        raise StandardError,"moduleFactory.rigDisconnect('%s')>>>> Module not connected"%(str_shortName)
    
    mc.select(cl=True)
    mc.select(self.rigNull.msgList_getMessage('controlsAll'))
    ml_resetChannels.main(transformsOnly = False)
    
    i_rigNull = self.rigNull
    l_rigJoints = i_rigNull.getMessage('rigJoints') or False
    l_skinJoints = i_rigNull.getMessage('skinJoints') or False
    l_constraints = []
    for i,i_jnt in enumerate(i_rigNull.skinJoints):
	try:
	    l_constraints.extend( i_jnt.getConstraintsTo() )
	    attributes.doBreakConnection("%s.scale"%i_jnt.mNode)
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"moduleFactory.rigDisconnect('%s')>> Joint failed: %s"%(str_shortName,i_jnt.getShortName())
    log.debug("moduleFactory.rigDisconnect('%s')>> constraints found: %s"%(str_shortName,l_constraints))
    mc.delete(l_constraints)
    return True

def rig_getReport(self,*args,**kws):    
    mRig.get_report(self,*args,**kws)      
    return True
    #except StandardError,error:
        #log.warning(error)
	
def rig_getSkinJoints(self,asMeta = True): 
    """
    if not isSkeletonized(self):
        log.warning("%s.rig_getSkinJoints>>> Not skeletonized"%self.getShortName())
        return False    """   
    return mRig.get_skinJoints(self,asMeta)      
	
def rig_getHandleJoints(self,asMeta = True):
    """
    Find the module handle joints
    """
    try:
	return mRig.get_handleJoints(self,asMeta)
    except StandardError,error:
	raise StandardError,"%s.rig_getHandleJoints >> failed: %s"%(self.getShortName(),error)
    
def rig_getRigHandleJoints(self,asMeta = True):
    """
    Find the module handle joints
    """
    try:
	return mRig.get_rigHandleJoints(self,asMeta)
    except StandardError,error:
	raise StandardError,"%s.rig_getRigHandleJoints >> failed: %s"%(self.getShortName(),error)
    
#=====================================================================================================
#>>> Template
#=====================================================================================================
@cgmGeneral.Timer
def isTemplated(self):
    """
    Return if a module is templated or not
    """
    log.debug(">>> %s.isTemplated() >> "%(self.p_nameShort) + "="*75) 		                        
    coreNamesValue = self.coreNames.value
    if not coreNamesValue:
        log.debug("No core names found")
        return False
    if not self.getMessage('templateNull'):
        log.debug("No template null")
        return False       
    if not self.templateNull.getChildren():
        log.debug("No children found in template null")
        return False   
    if not self.getMessage('modulePuppet'):
        log.debug("No modulePuppet found")
        return False   	
    if not self.modulePuppet.getMessage('masterControl'):
        log.debug("No masterControl")
	return False
	
    if self.mClass in ['cgmModule','cgmLimb']:
	#Check our msgList attrs
	#=====================================================================================
	ml_controlObjects = self.templateNull.msgList_get('controlObjects')
	for attr in 'controlObjects','orientHelpers':
	    if not self.templateNull.msgList_getMessage(attr):
		log.warning("No data found on '%s'"%attr)
		return False        
	
	#Check the others
	for attr in 'root','curve','orientRootHelper':
	    if not self.templateNull.getMessage(attr):
		if attr == 'orientHelpers' and len(controlObjects)==1:
		    pass
		else:
		    log.warning("No data found on '%s'"%attr)
		    return False    
	    
	if len(coreNamesValue) != len(ml_controlObjects):
	    log.debug("Not enough handles.")
	    return False    
	    
	if len(ml_controlObjects)>1:
	    for i_obj in ml_controlObjects:#check for helpers
		if not i_obj.getMessage('helper'):
		    log.debug("'%s' missing it's helper"%i_obj.getShortName())
		    return False
	
	#self.moduleStates['templateState'] = True #Not working yet
	return True
    elif self.mClass == 'cgmEyeball':
	return True

@cgmGeneral.Timer
def doTemplate(self,*args,**kws):
    log.debug(">>> %s.doTemplate() >> "%(self.p_nameShort) + "="*75) 		                        
    
    if not isSized(self):
        log.warning("Not sized: '%s'"%self.getShortName())
        return False      
    tFactory.go(self,*args,**kws)      
    if not isTemplated(self):
        log.warning("Template failed: '%s'"%self.getShortName())
        return False
    return True
    #except StandardError,error:
        #log.warning(error)    
    
@cgmGeneral.Timer
def deleteTemplate(self,*args,**kws):
    log.debug(">>> %s.deleteTemplate() >> "%(self.p_nameShort) + "="*75) 		                            
    try:
        objList = returnTemplateObjects(self)
        if objList:
            mc.delete(objList)
        for obj in self.templateNull.getChildren():
            mc.delete(obj)
        return True
    except StandardError,error:
        log.warning(error)
        
@cgmGeneral.Timer
def returnTemplateObjects(self):
    log.debug(">>> %s.returnTemplateObjects() >> "%(self.p_nameShort) + "="*75) 		                                
    try:
        templateNull = self.templateNull.getShortName()
        returnList = []
        for obj in mc.ls(type = 'transform'):
            if attributes.doGetAttr(obj,'templateOwner') == templateNull:
                returnList.append(obj)
        return returnList
    except StandardError,error:
        log.warning(error)        
#=====================================================================================================
#>>> Skeleton
#=====================================================================================================
@cgmGeneral.Timer
def get_rollJointCountList(self):
    try:
	log.debug(">>> %s.get_rollJointCountList() >> "%(self.p_nameShort) + "="*75) 		                                	
	int_rollJoints = self.templateNull.rollJoints
	d_rollJointOverride = self.templateNull.rollOverride
	if type(d_rollJointOverride) is not dict:d_rollJointOverride = {}
	
	l_segmentRollCount = [int_rollJoints for i in range(self.templateNull.handles-1)]
	    
	if d_rollJointOverride:
	    for k in d_rollJointOverride.keys():
		try:
		    l_segmentRollCount[int(k)]#If the arg passes
		    l_segmentRollCount[int(k)] = d_rollJointOverride.get(k)#Override the roll value
		except:log.warning("%s:%s rollOverride arg failed"%(k,d_rollJointOverride.get(k)))
	log.debug("%s.get_rollJointCountList >>  %s"%(self.getShortName(),l_segmentRollCount))
	return l_segmentRollCount
    except StandardError,error:
	raise StandardError,"%s.get_rollJointCountList >> failed: %s"%(self.getShortName(),error)
	
@cgmGeneral.Timer
def isSkeletonized(self):
    """
    Return if a module is skeletonized or not
    """
    log.debug(">>> %s.isSkeletonized() >> "%(self.p_nameShort) + "="*75) 
    """
    if not isTemplated(self):
        log.debug("Not templated, can't be skeletonized yet")
        return False"""
    
    l_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta=False)
    if not l_moduleJoints:
        log.debug("No skin joints found")
        return False  
    
    #>>> How many joints should we have 
    goodCount = returnExpectedJointCount(self)
    currentCount = len(l_moduleJoints)
    if  currentCount < (goodCount-1):
        log.warning("Expected at least %s joints. %s found: '%s'"%(goodCount-1,currentCount,self.getShortName()))
        return False
    return True

@cgmGeneral.Timer
def doSkeletonize(self,*args,**kws):
    log.debug(">>> %s.doSkeletonize() >> "%(self.p_nameShort) + "="*75) 		                                	    
    try:
        if not isTemplated(self):
            log.warning("Not templated, can't skeletonize: '%s'"%self.getShortName())
            return False      
        jFactory.go(self,*args,**kws)      
        if not isSkeletonized(self):
            log.warning("Skeleton build failed: '%s'"%self.getShortName())
            return False
        return True
    except StandardError,error:
	raise StandardError,"%s.doSkeletonize >> failed: %s"%(self.getShortName(),error)	

@cgmGeneral.Timer       
def deleteSkeleton(self,*args,**kws): 
    log.debug(">>> %s.deleteSkeleton() >> "%(self.p_nameShort) + "="*75) 		                                	        
    if isSkeletonized(self):
        jFactory.deleteSkeleton(self,*args,**kws)
    return True

@cgmGeneral.Timer
def returnExpectedJointCount(self):
    """
    Function to figure out how many joints we should have on a module for the purpose of isSkeletonized check
    """
    log.debug(">>> %s.returnExpectedJointCount() >> "%(self.p_nameShort) + "="*75) 		                                	            
    handles = self.templateNull.handles
    if handles == 0:
        log.warning("Can't count expected joints. 0 handles: '%s'"%self.getShortName())
        return False
    
    if self.templateNull.hasAttr('rollJoints'):
	rollJoints = self.templateNull.rollJoints 
	d_rollJointOverride = self.templateNull.rollOverride 
	
	l_spanDivs = []
	for i in range(0,handles-1):
	    l_spanDivs.append(rollJoints)    
    
	if type(d_rollJointOverride) is dict:
	    for k in d_rollJointOverride.keys():
		try:
		    l_spanDivs[int(k)]#If the arg passes
		    l_spanDivs[int(k)] = d_rollJointOverride.get(k)#Override the roll value
		except:log.warning("%s:%s rollOverride arg failed"%(k,d_rollJointOverride.get(k)))    
	
	int_count = 0
	for i,n in enumerate(l_spanDivs):
	    int_count +=1
	    int_count +=n
	int_count+=1#add the last handle back
	return int_count
    else:
	return self.templateNull.handles
#=====================================================================================================
#>>> States
#=====================================================================================================        
@cgmGeneral.Timer
def validateStateArg(stateArg):
    #>>> Validate argument
    if type(stateArg) in [str,unicode]:
        stateArg = stateArg.lower()
        if stateArg in l_moduleStates:
            stateIndex = l_moduleStates.index(stateArg)
            stateName = stateArg
        else:
            log.warning("Bad stateArg: %s"%stateArg)
            return False
    elif type(stateArg) is int:
        if stateArg<= len(l_moduleStates):
            stateIndex = stateArg
            stateName = l_moduleStates[stateArg]         
        else:
            log.warning("Bad stateArg: %s"%stateArg)
            return False        
    else:
        log.warning("Bad stateArg: %s"%stateArg)
        return False
    return [stateIndex,stateName]
    
@cgmGeneral.Timer
def isModule(self):
    """
    Simple module check
    """
    if not self.hasAttr('mClass'):
        log.warning("Has no 'mClass', not a module: '%s'"%self.getShortName())
        return False
    if self.mClass not in l_modulesClasses:
        log.warning("Class not a known module type: '%s'"%self.mClass)
        return False  
    log.debug("Is a module: : '%s'"%self.getShortName())
    return True

@cgmGeneral.Timer
def getState(self):
    """ 
    Check module state ONLY from the state check attributes
    
    RETURNS:
    state(int) -- indexed to ModuleFactory.l_moduleStates
    
    Possible states:
    define
    sized
    templated
    skeletonized
    rigged
    """
    if not isModule(self):
        return False
    d_CheckList = {'size':isSized,
                   'template':isTemplated,
                   'skeleton':isSkeletonized,
                   'rig':isRigged,
                   }
    goodState = 0
    for i,state in enumerate(l_moduleStates):
        if state in d_CheckList.keys():
            if d_CheckList[state](self):
                goodState = i
            else:break
        elif i != 0:
            log.warning("Need test for: '%s'"%state)
    log.debug("'%s' state: %s | '%s'"%(self.getShortName(),goodState,l_moduleStates[goodState]))
    return goodState

@cgmGeneral.Timer
def setState(self,stateArg,rebuildFrom = None, *args,**kws):
    """ 
    Set a module's state
    
    @rebuild -- force it to rebuild each step
    TODO:
    Make template info be stored when leaving
    """
    log.debug(">>> %s.setState( stateArg = %s , rebuildFrom = %s) >> "%(self.p_nameShort,stateArg,rebuildFrom) + "="*75) 		                                	        
    log.debug("stateArg: %s"%stateArg)
    
    if rebuildFrom is not None:
        rebuildArgs = validateStateArg(rebuildFrom)
        if rebuildArgs:
            log.debug("'%s' rebuilding from: '%s'"%(self.getShortName(),rebuildArgs[1]))
            changeState(self,rebuildArgs[1],*args,**kws)
        
    changeState(self, stateArg, *args,**kws)
        
    
@cgmGeneral.Timer
def changeState(self,stateArg, rebuildFrom = None, forceNew = False, *args,**kws):
    """ 
    Changes a module state
    
    TODO:
    Make template info be stored skeleton builds
    Make template builder read and use pose data stored
    
    
    """
    log.debug(">>> %s.changeState( stateArg = %s , rebuildFrom = %s, forceNew = %s) >> "%(self.p_nameShort,stateArg,rebuildFrom,forceNew) + "="*75) 		                                	            
    d_upStateFunctions = {'size':doSize,
                           'template':doTemplate,
                           'skeleton':doSkeletonize,
                           'rig':doRig,
                           }
    d_downStateFunctions = {'define':deleteSizeInfo,
                            'size':deleteTemplate,
                            'template':deleteSkeleton,
                            'skeleton':rigDelete,
                            }
    d_deleteStateFunctions = {'size':deleteSizeInfo,
                              'template':deleteTemplate,#handle from factory now
                              'skeleton':deleteSkeleton,
                              'rig':rigDelete,
                              }    
    log.debug(">>> In ModuleFactory.changeState")
    log.debug("stateArg: %s"%stateArg)
    log.debug("rebuildFrom: %s"%rebuildFrom)
    log.debug("forceNew: %s"%forceNew)
    
    if not isModule(self):
        return False
    
    stateArgs = validateStateArg(stateArg)
    if not stateArgs:
        log.warning("Bad stateArg from changeState: %s"%stateArg)
        return False
    
    stateIndex = stateArgs[0]
    stateName = stateArgs[1]
    
    log.debug("stateIndex: %s | stateName: '%s'"%(stateIndex,stateName))
    
    #>>> Meat
    #========================================================================
    currentState = getState(self) 
    if currentState == stateIndex and rebuildFrom is None and not forceNew:
        if not forceNew:log.warning("'%s' already has state: %s"%(self.getShortName(),stateName))
        return True
    #If we're here, we're going to move through the set states till we get to our spot
    log.debug("Changing states now...")
    if stateIndex > currentState:
        startState = currentState+1        
        log.debug(' up stating...')        
        log.debug("Starting doState: '%s'"%l_moduleStates[startState])
        doStates = l_moduleStates[startState:stateIndex+1]
        log.debug("doStates: %s"%doStates)        
        for doState in doStates:
            if doState in d_upStateFunctions.keys():
                if not d_upStateFunctions[doState](self,*args,**kws):return False
                else:
                    log.debug("'%s' completed: %s"%(self.getShortName(),doState))
            else:
                log.warning("No up state function for: %s"%doState)
    elif stateIndex < currentState:#Going down
        log.debug('down stating...')        
        l_reverseModuleStates = copy.copy(l_moduleStates)
        l_reverseModuleStates.reverse()
        startState = currentState      
        log.debug(' up stating...')     
        log.debug("l_reverseModuleStates: %s"%l_reverseModuleStates)
        log.debug("Starting downState: '%s'"%l_moduleStates[startState])
        rev_start = l_reverseModuleStates.index( l_moduleStates[startState] )+1
        rev_end = l_reverseModuleStates.index( l_moduleStates[stateIndex] )+1
        doStates = l_reverseModuleStates[rev_start:rev_end]
        log.debug("toDo: %s"%doStates)
        
        for doState in doStates:
            log.debug("doState: %s"%doState)
            if doState in d_downStateFunctions.keys():
                if not d_downStateFunctions[doState](self,*args,**kws):return False
                else:log.debug("'%s': %s"%(self.getShortName(),doState))
            else:
                log.warning("No down state function for: %s"%doState)  
    else:
        log.debug('Forcing recreate')
        if stateName in d_upStateFunctions.keys():
            #d_deleteStateFunctions[stateName](self)
            if not d_upStateFunctions[stateName](self,*args,**kws):return False
            return True
        
    
@cgmGeneral.Timer
def storePose_templateSettings(self):
    """
    Builds a template's data settings for reconstruction.
    
    exampleDict = {'root':{'test':[0,1,0]},
                'controlObjects':{0:[1,1,1]}}
    """  
    _str_funcName = "storePose_templateSettings(%s)"%self.p_nameShort  
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)   
    
    if self.getMessage('helper'):
	log.warning(">>> %s | Error: Cannot currently store pose with rigBlocks"%_str_funcName)
	return False
    def buildDict_AnimAttrsOfObject(node,ignore = ['visibility']):
        attrDict = {}
        attrs = r9Anim.getSettableChannels(node,incStatics=True)
        if attrs:
            for attr in attrs:
                if attr not in ignore:
                    try:attrDict[attr]=mc.getAttr('%s.%s' % (node,attr))
                    except:log.debug('%s : attr is invalid in this instance' % attr)
        return attrDict
        
    exampleDict = {'root':{'test':[0,1,0]},
                   'orientRootHelper':{'test':[0,1,0]},
                   'controlObjects':{0:[1,1,1]},
                   'helperObjects':{0:[]}}    
    if not isModule(self):return False
    if not isTemplated(self):return False
    
    poseDict = {}
    i_templateNull = self.templateNull
    i_templateNull.addAttr('controlObjectTemplatePose',attrType = 'string')#make sure attr exists
    #>>> Get the root
    poseDict['root'] = buildDict_AnimAttrsOfObject(i_templateNull.getMessage('root')[0])
    poseDict['orientRootHelper'] = buildDict_AnimAttrsOfObject(i_templateNull.getMessage('orientRootHelper')[0])
    poseDict['controlObjects'] = {}
    poseDict['helperObjects'] = {}
    
    for i,i_node in enumerate(i_templateNull.controlObjects):
        poseDict['controlObjects'][str(i)] = buildDict_AnimAttrsOfObject(i_node.mNode)
        if i_node.getMessage('helper'):
            poseDict['helperObjects'][str(i)] = buildDict_AnimAttrsOfObject(i_node.helper.mNode)
    
    #Store it        
    i_templateNull.controlObjectTemplatePose = poseDict
    return poseDict

@cgmGeneral.Timer
def readPose_templateSettings(self):
    """
    Builds a template's data settings for reconstruction.
    
    exampleDict = {'root':{'test':[0,1,0]},
                'controlObjects':{0:[1,1,1]}}
    """   
    log.debug(">>> %s.readPose_templateSettings() >> "%(self.p_nameShort) + "="*75) 		                                	                
    if not isModule(self):return False
    if not isTemplated(self):return False
    
    i_templateNull = self.templateNull    
    poseDict = i_templateNull.controlObjectTemplatePose
    if type(poseDict) is not dict:
        return False
    
    #>>> Get the root
    for key in ['root','orientRootHelper']:
        if poseDict[key]:
            for attr, val in poseDict[key].items():
                try:
                    val=eval(val)
                except:pass      
                try:
                    mc.setAttr('%s.%s' % (i_templateNull.getMessage(key)[0],attr), val)
                except StandardError,err:
                    log.error(err)   
                    
    for key in poseDict['controlObjects']:
        for attr, val in poseDict['controlObjects'][key].items():
            try:
                val=eval(val)
            except:pass      
        
            try:
                mc.setAttr('%s.%s' % (i_templateNull.getMessage('controlObjects')[int(key)], attr), val)
            except StandardError,err:
                log.error(err) 
                
    for key in poseDict['helperObjects']:
        for attr, val in poseDict['helperObjects'][key].items():
            try:
                val=eval(val)
            except:pass      
        
            try:
                if i_templateNull.controlObjects[int(key)].getMessage('helper'):
                    log.debug(i_templateNull.controlObjects[int(key)].getMessage('helper')[0])
                    mc.setAttr('%s.%s' % (i_templateNull.controlObjects[int(key)].getMessage('helper')[0], attr), val)
            except StandardError,err:
                log.error(err)    
                
    return True

#=====================================================================================================
#>>> Children functions
#=====================================================================================================  
@cgmGeneral.Timer
def getAllModuleChildren(self):
    """
    Finds all module descendants of a module.
    """   
    log.debug(">>> %s.getAllModuleChildren() >> "%(self.p_nameShort) + "="*75) 		                                	                    
    if not isModule(self):return False
    ml_children = []
    ml_childrenCull = copy.copy(self.moduleChildren)
                   
    cnt = 0
    #Process the childdren looking for parents as children and so on and so forth, appending them as it finds them
    while len(ml_childrenCull)>0 and cnt < 100:#While we still have a cull list
        cnt+=1                        
        if cnt == 99:
            log.error('%s.getAllModuleChildren >> Max count')
        for i_child in ml_childrenCull:
	    log.debug("i_child: %s"%i_child.getShortName())
	    if i_child not in ml_children:
		ml_children.append(i_child)
	    for i_subChild in i_child.moduleChildren:
		ml_childrenCull.append(i_subChild)
	    ml_childrenCull.remove(i_child) 
                    
    return ml_children

@cgmGeneral.Timer
def animKey_children(self,**kws):
    """
    Key module and all module children controls
    """   
    log.debug(">>> %s.animKey_children() >> "%(self.p_nameShort) + "="*75) 		                                	                    
    if not isModule(self):return False    
    try:
	l_controls = self.rigNull.msgList_getMessage('controlsAll') or []
	ml_children = getAllModuleChildren(self)
	if ml_children:mayaMainProgressBar = cgmGeneral.doStartMayaProgressBar(len(ml_children)) 
	for i,i_c in enumerate(ml_children):
	    mc.progressBar(mayaMainProgressBar, edit=True, status = "%s.animKey_children>> gathering controls:'%s' "%(self.p_nameShort,i_c.p_nameShort), progress=i)    				        				    
	    buffer = i_c.rigNull.msgList_getMessage('controlsAll')
	    if buffer:
		l_controls.extend(buffer)
		
	if ml_children:
	    try:cgmGeneral.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar        	
	    except:pass	   
	    
	if l_controls:
	    mc.select(l_controls)
	    mc.setKeyframe(**kws)
	    return True
	return False
    except StandardError,error:
	log.error("%s.animKey_children>> animKey fail | %s"%(self.getBaseName(),error))
	return False
    
@cgmGeneral.Timer
def animSelect_children(self,**kws):
    """
    Select module and all module children controls
    """     
    log.debug(">>> %s.animSelect_children() >> "%(self.p_nameShort) + "="*75) 		                                	                        
    if not isModule(self):return False    
    try:
	l_controls = self.rigNull.msgList_getMessage('controlsAll') or []
	ml_children = getAllModuleChildren(self)
	if ml_children:mayaMainProgressBar = cgmGeneral.doStartMayaProgressBar(len(ml_children)) 
	for i,i_c in enumerate(ml_children):
	    mc.progressBar(mayaMainProgressBar, edit=True, status = "%s.animSelect_children>> gathering controls:'%s' "%(self.p_nameShort,i_c.p_nameShort), progress=i)    				        				    
	    buffer = i_c.rigNull.msgList_getMessage('controlsAll')
	    if buffer:
		l_controls.extend(buffer)
		
	if ml_children:
	    try:cgmGeneral.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar        	
	    except:pass	   
	
	if l_controls:
	    mc.select(l_controls)
	    return True
	return False
    except StandardError,error:
	log.error("%s.animSelect>> animSelect fail | %s"%(self.getBaseName(),error))
	return False   

@cgmGeneral.Timer 
def dynSwitch_children(self,arg):
    """
    Key module and all module children
    """  
    log.debug(">>> %s.dynSwitch_children() >> "%(self.p_nameShort) + "="*75) 		                                	                        
    if not isModule(self):return False  
    
    
    try:
	ml_children = getAllModuleChildren(self)
	mayaMainProgressBar = cgmGeneral.doStartMayaProgressBar(len(ml_children))    
	for i,i_c in enumerate(ml_children):
	    try:
		mc.progressBar(mayaMainProgressBar, edit=True, status = "%s.dynSwitch_children>> step:'%s' "%(self.p_nameShort,i_c.p_nameShort), progress=i)    				        			
		i_c.rigNull.dynSwitch.go(arg)
	    except StandardError,error:
		log.error("%s.dynSwitch_children>>  child: %s | %s"%(self.getBaseName(),i_c.getShortName(),error))
	cgmGeneral.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar        	
    except StandardError,error:
	try:cgmGeneral.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar        	
	except:pass
	log.error("%s.dynSwitch_children>> fail | %s"%(self.getBaseName(),error))
	return False  