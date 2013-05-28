"""
------------------------------------------
cgm_Meta: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is the Core of the MetaNode implementation of the systems.
It is uses Mark Jackson (Red 9)'s as a base.
================================================================
"""

import maya.cmds as mc
import maya.mel as mel
import copy

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General


# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (lists,
                     search,
                     attributes,
                     distance,
                     constraints,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory,
                     locators)

reload(attributes)
reload(search)

#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmDynamicMatch
#=========================================================================
class cgmDynamicMatch(cgmMeta.cgmObject):
    def __init__(self,node = None, name = None, dynNull = None, dynSuffix = None, dynPrefix = None,
                 dynMatchTargets = None, dynSnapTargets = None, dynObject = None,
                 dynMode = None, setClass = False,*args,**kws):
        """
        Dynamic Match Setup. Inspiration for this comes from Jason Schleifer's great AFR work. Retooling for our own purposes.
        The basic idea is a class based match setup for matching fk ik or whatever kind of matching that needs to happen.
	
	There are two kinds of match types: MatchTargets and SnapTargets.
	A MatchTarget setup creates a match object from our dynObject to match to,
	a SnapTarget is just a mappting to give an exisitng transform to snap to
        
        Keyword arguments:
        dynMatchTargets(list) -- list of match targets
        mode(list) -- parent/follow/orient
        """
	l_plugBuffer = ['dynMatchDriver']
	if dynSuffix is not None:
	    l_plugBuffer.append(str(dynSuffix))    
	if dynPrefix is not None:
	    l_plugBuffer.insert(0,str(dynPrefix))  
	    
	str_dynMatchDriverPlug = '_'.join(l_plugBuffer)
    
	def _isNullValidForObject(obj,null):
	    """
	    To pass a null in the initialzation as the null, we need to check a few things
	    """
	    i_object = cgmMeta.validateObjArg(obj,cgmMeta.cgmObject,noneValid=True)
	    i_null = cgmMeta.validateObjArg(null,cgmDynamicMatch,noneValid=True)
	    if not i_object or not i_null:#1) We need args
		return False
	    if i_object.hasAttr(str_dynMatchDriverPlug):#3) the object is already connected
		if i_object.getMessageInstance(str_dynMatchDriverPlug) != i_null:
		    log.info("cgmDynamicMatch.isNullValidForObject>> Object already has dynMatchDriver: '%s'"%i_object.getMessage(str_dynMatchDriverPlug))
		    return False
		else:
		    return True
	    return True	
	
        ### input check  
        log.info("In cgmDynamicMatch.__init__ node: %s"%node)
	i_dynObject = cgmMeta.validateObjArg(dynObject,cgmMeta.cgmObject,noneValid=True)
	i_argDynNull = cgmMeta.validateObjArg(dynNull,cgmDynamicMatch,noneValid=True)
	log.info("i_dynObject: %s"%i_dynObject)
	__justMade__ = False
	
	#TODO allow to set dynNull
	if i_dynObject:
	    pBuffer = i_dynObject.getMessage(str_dynMatchDriverPlug) or False
	    log.info("pBuffer: %s"%pBuffer)
	    if pBuffer:
		node = pBuffer[0]
	    elif _isNullValidForObject( i_dynObject,i_argDynNull):
		log.info("cgmDynamicMatch.__init__>>Null passed and valid")
		node = i_argDynNull.mNode
		__justMade__ = False		
	    else:#we're gonna make a null
		i_node = i_dynObject.doDuplicateTransform()
		i_node.addAttr('mClass','cgmDynamicMatch')
		node = i_node.mNode
		__justMade__ = True
	
	super(cgmDynamicMatch, self).__init__(node = node,name = name,nodeType = 'transform') 
	
	#Unmanaged extend to keep from erroring out metaclass with our object spectific attrs
	self.UNMANAGED.extend(['arg_ml_dynMatchTargets','_mi_dynObject','_str_dynMatchDriverPlug','d_indexToAttr','l_dynAttrs'])
	if i_dynObject:self._mi_dynObject = i_dynObject
	else:self._mi_dynObject = False
	    
	if kws:log.info("kws: %s"%str(kws))
	if args:log.info("args: %s"%str(args)) 	
	doVerify = kws.get('doVerify') or False
	self._str_dynMatchDriverPlug = str_dynMatchDriverPlug
	
	arg_ml_dynMatchTargets = cgmMeta.validateObjListArg(dynMatchTargets,cgmMeta.cgmObject,noneValid=True)
	arg_ml_dynSnapTargets = cgmMeta.validateObjListArg(dynSnapTargets,cgmMeta.cgmObject,noneValid=True)
	
	log.info("arg_ml_dynMatchTargets: %s"%arg_ml_dynMatchTargets)
	
        if not self.isReferenced():
	    if not self.__verify__(*args,**kws):
		raise StandardError,"cgmDynamicMatch.__init__>> failed to verify!"
	    
	for p in arg_ml_dynMatchTargets:
	    log.info("Adding dynMatchTarget: %s"%p.mNode)
	    self.addDynMatchTarget(p)
	log.info("cgmDynamicMatch.__init__>> dynMatchTargets: %s"%self.getMessage('dynMatchTargets',False))
	    
	for p in arg_ml_dynSnapTargets:
	    log.info("Adding dynSnapTarget: %s"%p.mNode)
	    self.addDynSnapTarget(p)
	log.info("cgmDynamicMatch.__init__>> dynSnapTargets: %s"%self.getMessage('dynSnapTargets',False))
		
	if __justMade__ and i_dynObject:
	    self.addDynObject(i_dynObject)
	    #self.rebuild()
	    
	log.info("self._str_dynMatchDriverPlug>> '%s'"%self._str_dynMatchDriverPlug)
	
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # functions
    #======================================================================
    def __verify__(self,*args,**kws):
	if self.hasAttr('mClass') and self.mClass!='cgmDynamicMatch':
	    raise StandardError, "cgmDynamicMatch.__verify__>> This object has a another mClass and setClass is not set to True"
	#Check our attrs
	if self._mi_dynObject:
	    self.addDynObject(self._mi_dynObject)
	self.addAttr('mClass','cgmDynamicMatch',lock=True)#We're gonna set the class because it's necessary for this to work
	self.addAttr('cgmType','dynMatchDriver',lock=True)#We're gonna set the class because it's necessary for this to work
	
        self.addAttr('dynObject',attrType = 'messageSimple',lock=True)
	self.addAttr('dynHiddenSwitch',attrType = 'bool')	
        self.addAttr('dynMatchTargets',attrType = 'message',lock=True)
	self.addAttr('dynDrivers',attrType = 'message',lock=True)
	self.addAttr('dynPrematchAttrs',attrType = 'string',lock=True)
	self.addAttr('dynIterAttrs',attrType = 'string',lock=True)
	self.addAttr('dynIterSettings',attrType = 'string',lock=True)
	
	#Unlock all transform attriutes
	for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
	    cgmMeta.cgmAttr(self,attr,lock=False)
	self.doName()
	return True
    
    def rebuild(self,*a,**kw):
        """ Rebuilds the buffer data cleanly """ 
	log.info("rebuild>>>")
	#Must have at least 2 targets
	if len(self.dynMatchTargets)<2:
	    log.error("cgmDynamicMatch.rebuild>> Need at least two dynMatchTargets. Build failed: '%s'"%self.getShortName())
	    return False
	i_object = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=False)
	
	#TODO First scrub nodes and what not
	
	#Check our attrs
	d_attrBuffers = {}
	for a in self.l_dynAttrs:
	    if i_object.hasAttr(a):#we probably need to index these to the previous settings in case order changes
		d_attrBuffers[a] = attributes.doGetAttr(i_object.mNode,a)
	    if a not in d_DynMatchTargetNullModeAttrs[self.dynMode]:
		attributes.doDeleteAttr(i_object.mNode,a)
	if d_attrBuffers:log.info("d_attrBuffers: %s"%d_attrBuffers)
	
	l_parentShortNames = [cgmNode(o).getNameAlias() for o in self.getMessage('dynMatchTargets')]
	log.info("parentShortNames: %s"%l_parentShortNames)
	
	for a in d_DynMatchTargetNullModeAttrs[self.dynMode]:
	    i_object.addAttr(a,attrType='enum',enumName = ':'.join(l_parentShortNames),keyable = True, hidden=False)
	
	#Make our nulls
	#One per parent, copy parent transform
	#Make our attrs
	if self.dynMode == 2:#Follow - needs an extra follow null
	    self.verifyFollowDriver()
	elif self.dynFollow:
	    mc.delete(self.getMessage('dynFollow'))
	
	#Verify our parent drivers:
	for i_p in [cgmMeta.cgmObject(o) for o in self.getMessage('dynMatchTargets')]:
	    log.info("verifyMatchTargetDriver: %s"%i_p.getShortName())
	    self.verifyMatchTargetDriver(i_p)
	
	#i_object.addAttr('space',attrType='enum',enumName = ':'.join(l_parentShortNames),keyable = True, hidden=False)
	
	#Verify constraints    
	self.verifyConstraints()
	
	return 'Done'    
	#Check constraint

    def addDynObject(self,arg):
	i_object = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=False)
	if i_object == self:
	    raise StandardError, "cgmDynamicMatch.addDynObject>> Cannot add self as dynObject"
	
	if i_object.hasAttr(self._str_dynMatchDriverPlug) and i_object.getMessageInstance(self._str_dynMatchDriverPlug) == self:
	    log.info("cgmDynamicMatch.addDynObject>> dynObject already connected: '%s'"%i_object.getShortName())
	    return True
	
	log.info("cgmDynamicMatch.addDynObject>> Adding dynObject: '%s'"%i_object.getShortName())
	self.connectChildNode(i_object,'dynObject',self._str_dynMatchDriverPlug)#Connect the nodes
	self.doStore('cgmName',i_object.mNode)
	
	if not self.parent:#If we're not parented, parent to dynObject, otherwise, it doen't really matter where this is
	    self.parent = i_object.mNode
	    
    def addPrematchData(self,d_arg):
	#>>Get our Attribute registered
	i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
	if not i_dynObject:raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Must have dynObject. None found"	    
	if type(d_arg) not in [dict]:raise StandardError,"%s.addDynIterTarget>> Arg must be in dict form {attr:value}. Found: %s"%(self.getShortName(),d_arg)
	
	d_prematchAttrs = self.dynPrematchAttrs or {}
	
	for k in d_arg.keys():
	    if not i_dynObject.hasAttr(k):
		log.warning("%s.addDynIterTarget>> dynObject lacks attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName,k))
	    else:
		d_prematchAttrs[k] = d_arg[k]
		
	
	#push it back
	self.dynPrematchAttrs = d_prematchAttrs
	
    def setPrematchData(self):
	i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
	if not i_dynObject:raise StandardError, "%s.setPrematchData>> Must have dynObject. None found"%self.getShortName()    
	
	d_prematchAttrs = self.dynPrematchAttrs or {}
	for k in d_prematchAttrs.keys():
	    if i_dynObject.hasAttr(k):i_dynObject.__setattr__(k,d_prematchAttrs[k])
	    else:
		log.warning("%s.setPrematchData>> dynObject lacks attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName,k))
		d_prematchAttrs.pop(k)
	#push it back
	self.dynPrematchAttrs = d_prematchAttrs	
    
    #======================================================================		
    #>>> Iter match stuff
    def getIterDrivenList(self):
	l_iterDriven = []
	ml_iterDriven = []
	for i in range(75):
	    buffer = self.getMessage('iterDriven_%s'%i,False)
	    if buffer:
		l_iterDriven.extend(buffer)
		ml_iterDriven.extend(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	    else:break
	log.info("%s.getIterDrivenList>>> Iter driven -- cnt: %s | lists: %s"%(self.getShortName(),len(l_iterDriven),l_iterDriven)) 	
	return ml_iterDriven
    
    def getIterMatchList(self):
	l_iterMatch = []
	ml_iterMatch = []
	for i in range(75):
	    buffer = self.getMessage('iterMatch_%s'%i,False)
	    if buffer:
		l_iterMatch.extend(buffer)
		ml_iterMatch.extend(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	    else:break
	log.info("%s.getIterMatchList>>> Iter Match -- cnt: %s | lists: %s"%(self.getShortName(),len(l_iterMatch),l_iterMatch)) 	
	return ml_iterMatch
    
    def addDynIterTarget(self, drivenObject = None, matchObject = None, driverAttr = None,
                         maxValue = None, minValue = None, iterations = 50, iterIndex = None):
	"""
	dynIterTargetSetup
	
	Validate the drivenObject, matchObject
	"""
	#>>> Validate
	i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
	if not i_dynObject:raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Must have dynObject. None found"	    
	if not i_dynObject.hasAttr(driverAttr): raise StandardError, "cgmDynamicMatch.addDynIterTarget>> dynObject lacks attr: %s.%s "%(i_dynObject.getShortName,driverAttr)
	
	mPlug_driverAttr = cgmMeta.cgmAttr(i_dynObject,driverAttr)
	i_drivenObject = cgmMeta.validateObjArg(drivenObject,cgmMeta.cgmObject,noneValid=True)
	i_matchObject = cgmMeta.validateObjArg(matchObject,cgmMeta.cgmObject,noneValid=True)
	
	#Get our iter driven stuff
	ml_iterDriven = self.getIterDrivenList()#Get the list
	
	if i_dynObject == i_drivenObject:
	    raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Cannot add self as target"
	log.info(">>>>>>>>>>>>> Start add %s"%[iobj.mNode for iobj in ml_iterDriven])
	log.info("cgmDynamicMatch.addDynIterTarget>> driven obj: %s"%i_drivenObject)
	
	if i_drivenObject in ml_iterDriven:
	    log.info("cgmDynamicMatch.addDynIterTarget>> Object already connected: %s"%i_drivenObject.getShortName())
	    index_iterDriven = ml_iterDriven.index(i_drivenObject)
	else:#add it
	    index = self.returnNextAvailableAttrCnt("iterDriven_")
	    log.info(index)
	    self.connectChildNode(i_drivenObject,'iterDriven_%s'%index)	    
	    ml_iterDriven.append(i_drivenObject)
	    log.info(ml_iterDriven)
	    index_iterDriven = ml_iterDriven.index(i_drivenObject)
	    if index != index_iterDriven:
		raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Iter driven indexes do not match!"
	#======================================================================
	#Get our iter match stuff
	ml_iterMatch = self.getIterMatchList()
	
	if not i_matchObject.isTransform():
	    raise StandardError, "cgmDynamicMatch.addDynIterTarget>> SnapTarget has no transform: '%s'"%i_matchObject.getShortName()
	if i_dynObject == i_matchObject:
	    raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Cannot add self as target"
	log.info("cgmDynamicMatch.addDynIterTarget>> match obj: %s"%i_matchObject)
	log.info(">>>>>>>>>>>>> Start add %s"%[iobj.mNode for iobj in ml_iterMatch])
	if i_matchObject in ml_iterMatch:
	    log.info("cgmDynamicMatch.addDynIterTarget>> Object already connected: %s"%i_matchObject.getShortName())
	    index_iterMatch = ml_iterMatch.index(i_matchObject)
	
	else:#add it
	    index = self.returnNextAvailableAttrCnt("iterMatch_")
	    self.connectChildNode(i_matchObject,'iterMatch_%s'%index)
	    ml_iterMatch.append(i_matchObject)
	    
	    index_iterMatch = ml_iterMatch.index(i_matchObject)
	    if index != index_iterMatch:
		raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Iter match indexes do not match!"	    
	#======================================================================		
	#>>Get our Attribute registered
	d_iterSettings = self.dynIterSettings or {}
	l_iterAttrsBuffer = self.dynIterAttrs or []
	if mPlug_driverAttr.attr in l_iterAttrsBuffer:
	    log.info("cgmDynamicMatch.addDynIterTarget>> Attr already in, checking: '%s'"%mPlug_driverAttr.p_combinedShortName)	    
	else:
	    l_iterAttrsBuffer.append(mPlug_driverAttr.attr)
	index_IterAttr = l_iterAttrsBuffer.index(mPlug_driverAttr.attr)	
	self.dynIterAttrs = l_iterAttrsBuffer#Push back to attr
	
	#>>> Build our dict
	d_buffer = {}
	l_keyValues = [minValue,maxValue,iterations]
	l_keyNames = ['minValue','maxValue','iterations']
	for i,key in enumerate(l_keyNames):
	    if l_keyValues[i] is not None and type(l_keyValues[i]) in [float,int]:
		d_buffer[key] = l_keyValues[i]
	    elif l_keyValues[i] is not None:
		log.info("cgmDynamicMatch.addDynIterTarget>> Bad value for '%s': %s"%(key,l_keyValues[i]))	    		
	d_buffer['driven'] = index_iterDriven
	d_buffer['match'] = index_iterMatch
	
	#Store it
	d_iterSettings[mPlug_driverAttr.attr] = d_buffer
	self.dynIterSettings = d_iterSettings
	#======================================================================
	
    @r9General.Timer
    def doIter(self):
	"""
	"""
	#>>>Gather info
	i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
	if not i_dynObject:raise StandardError, "cgmDynamicMatch.doIter>> Must have dynObject. None found"	    
	
	ml_iterDriven = self.getIterDrivenList()#Get the list
	ml_iterMatch = self.getIterMatchList()#Get the list
	
	l_attrBuffer = self.dynIterAttrs or []#Check attrs
	if not l_attrBuffer:raise StandardError, "cgmDynamicMatch.doIter>> Must have iter attrs. None found"	    
	
	self.setPrematchData()#set our prematches for proper matching
	
	for a in l_attrBuffer:
	    if not i_dynObject.hasAttr(a):raise StandardError, "cgmDynamicMatch.doIter>> Missing iter attr: %s.%s "%(i_dynObject.getShortName(),a)#has attr    
	    if not self.dynIterSettings.get(a):raise StandardError, "cgmDynamicMatch.doIter>> Missing iter setting for attr: %s.%s "%(i_dynObject.getShortName(),a)#has setting	    
	    if 'driven' not in self.dynIterSettings[a].keys():raise StandardError, "%s.doIter>> Missing driven setting for attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName(),a)#has setting	    
	    if 'match' not in self.dynIterSettings[a].keys():raise StandardError, "%s.doIter>> Missing match setting for attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName(),a)#has setting	    
	    
	    if len(ml_iterDriven)< self.dynIterSettings[a]['driven']:raise StandardError, "%s.doIter>> Missing att's driven: attr: %s | index: %s "%(self.getShortName(),a,self.dynIterSettings[a]['driven'])#has setting	    
	    if len(ml_iterMatch)< self.dynIterSettings[a]['match']:raise StandardError, "%s.doIter>> Missing att's match: attr: %s | index: %s "%(self.getShortName(),a,self.dynIterSettings[a]['match'])#has setting	    
	
	log.info("%s.doIter>> Looks good to go to iter"%(self.getShortName()))
	
	#per iter attr, go
	for a in l_attrBuffer:
	    mPlug_driverAttr = cgmMeta.cgmAttr(i_dynObject,a)
	    log.info("%s.doIter>> iterating setup on : '%s.%s'"%(self.getShortName(),i_dynObject.getShortName(),a))
	    i_drivenObject = ml_iterDriven[self.dynIterSettings[a]['driven']]
	    i_matchObject = ml_iterMatch[self.dynIterSettings[a]['match']]
	    log.info("%s.doIter>> driven: '%s'"%(self.getShortName(),i_drivenObject.getShortName()))
	    log.info("%s.doIter>> match: '%s'"%(self.getShortName(),i_matchObject.getShortName()))
	    minValue = self.dynIterSettings[a].get('minValue') or 0
	    maxValue = self.dynIterSettings[a].get('maxValue') or 359
	    iterations = self.dynIterSettings[a].get('iterations') or 50
	    
	    rUtils.matchValue_iterator(i_matchObject,drivenObj=i_drivenObject,driverAttr=mPlug_driverAttr.p_combinedName,minIn=minValue,maxIn=maxValue,maxIterations=iterations)

	
    #==============================================================================
    def addDynSnapTarget(self,arg = None, alias = None):
	"""
	
	"""
	#>>> Validate
	i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
	if not i_dynObject:raise StandardError, "cgmDynamicMatch.addDynSnapTarget>> Must have dynObject. None found"	    
	
	i_dSnapTarget = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
	if not i_dSnapTarget:
	    i_dSnapTarget = i_dynObject.doLoc()
	    log.info("cgmDynamicMatch.addDynSnapTarget>> Added snap loc: %s"%i_dSnapTarget.getShortName())
	if self == i_dSnapTarget:
	    raise StandardError, "cgmDynamicMatch.addDynSnapTarget>> Cannot add self as target"
	if not i_dSnapTarget.isTransform():
	    raise StandardError, "cgmDynamicMatch.addDynSnapTarget>> SnapTarget has no transform: '%s'"%i_dSnapTarget.getShortName()
	if i_dSnapTarget.rotateOrder != i_dynObject.rotateOrder:
	    raise StandardError, "cgmDynamicMatch.addDynSnapTarget>> Rotate Order of target doesn't match dynChild: child: '%s' | snapTarget: '%s"%(i_dynObject.getShortName(),i_dSnapTarget.getShortName())	    
	
	ml_dynSnapTargets = [cgmMeta.cgmObject(o) for o in self.getMessage('dynSnapTargets')]
	
	log.info(">>>>>>>>>>>>> Start add %s"%self.getMessage('dynSnapTargets',False))
	if i_dSnapTarget in ml_dynSnapTargets:
	    log.info("cgmDynamicMatch.addDynSnapTarget>> Object already connected: %s"%i_dSnapTarget.getShortName())
	    return True
	
	if alias is not None:
	    i_dynSnapTarget.addAttr('cgmAlias', str(alias),lock = True)
	
	#>>> Connect it
	log.info("cgmDynamicMatch.addDynSnapTarget>> Adding target: '%s'"%i_dSnapTarget.getShortName())
	ml_dynSnapTargets.append(i_dSnapTarget)	
	log.info(">>>>>>>>>>>>> data add %s"%ml_dynSnapTargets)	
	self.connectChildrenNodes(ml_dynSnapTargets,'dynSnapTargets')#Connect the nodes
	log.info(">>>>>>>>>>>>> after add %s"%self.getMessage('dynSnapTargets',False))
	
    def addDynMatchTarget(self,arg, alias = None, l_matchAttrs = None):
	"""
	
	"""
	#>>> Validate
	i_dMatchTarget = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
	if not i_dMatchTarget:raise StandardError, "cgmDynamicMatch.addDynMatchTarget>> Failed to cgmMeta.validate: %s"%arg	    
	if self == i_dMatchTarget:
	    raise StandardError, "cgmDynamicMatch.addDynMatchTarget>> Cannot add self as target"
	if not i_dMatchTarget.isTransform():
	    raise StandardError, "cgmDynamicMatch.addDynMatchTarget>> MatchTarget has no transform: '%s'"%i_dMatchTarget.getShortName()
	log.info("cgmDynamicMatch.addDynMatchTarget>> '%s'"%i_dMatchTarget.getShortName())

	ml_dynMatchTargets = [cgmMeta.cgmObject(o) for o in self.getMessage('dynMatchTargets')]
	log.info(">>>>>>>>>>>>> Start add %s"%self.getMessage('dynMatchTargets',False))
	
	if i_dMatchTarget in ml_dynMatchTargets:
	    log.info("cgmDynamicMatch.addDynMatchTarget>> Object already connected: %s"%i_dMatchTarget.getShortName())
	    self.verifyMatchTargetDriver(i_dMatchTarget,l_matchAttrs)	    
	    return True
	
	if alias is not None:
	    i_dynMatchTarget.addAttr('cgmAlias', str(alias),lock = True)
	
	#>>> Connect it
	log.info("cgmDynamicMatch.addDynMatchTarget>> Adding target: '%s'"%i_dMatchTarget.getShortName())
	ml_dynMatchTargets.append(i_dMatchTarget)	
	log.info(">>>>>>>>>>>>> data add %s"%ml_dynMatchTargets)	
	self.connectChildrenNodes(ml_dynMatchTargets,'dynMatchTargets')#Connect the nodes
	log.info(">>>>>>>>>>>>> after add %s"%self.getMessage('dynMatchTargets',False))
	
	#Verify our driver for the target
	self.verifyMatchTargetDriver(i_dMatchTarget,l_matchAttrs)
	    
    def verifyMatchTargetDriver(self,arg,l_matchAttrs = None):
	"""
	1) if arg is a dynMatchTarget
	2) check it's driver
	3) Make if necesary
	"""	
	i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
	if not i_dynObject:raise StandardError, "cgmDynamicMatch.verifyMatchTargetDriver>> Must have dynObject. None found"	    
	i_dMatchTarget = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
	if not i_dMatchTarget:
	    raise StandardError, "cgmDynamicMatch.verifyMatchTargetDriver>> arg fail: %s"%arg
	log.info(self.dynMatchTargets)
	if i_dMatchTarget.getLongName() not in self.getMessage('dynMatchTargets',True):
	    raise StandardError, "cgmDynamicMatch.verifyMatchTargetDriver>> not a dynMatchTarget: %s"%i_dMatchTarget.getShortName()
	
	index = self.getMessage('dynMatchTargets',True).index(i_dMatchTarget.getLongName())
	log.info("cgmDynamicMatch.verifyMatchTargetDriver>> dynMatchTargets index: %s"%index)
	l_dynDrivers = self.getMessage('dynDrivers',True)
	
	#See if we have a good driver
	foundMatch = False
	if l_dynDrivers and len(l_dynDrivers) > index:
	    buffer = l_dynDrivers[index]
	    log.info("buffer: %s"%cgmMeta.cgmObject( buffer ).getMessage('dynMatchTarget',True))
	    log.info("object: %s"%i_dynObject.getLongName())
	    if cgmMeta.cgmObject( buffer ).getMessage('dynMatchTarget',True) == [i_dynObject.getLongName()]:
		log.info("dynDriver: found")
		i_driver = cgmMeta.validateObjArg(l_dynDrivers[index],cgmMeta.cgmObject,noneValid=False)
		foundMatch = True
	if not foundMatch:
	    log.info("dynDriver: creating")	
	    i_driver = i_dynObject.doDuplicateTransform()
	    l_dynDrivers.insert(index,i_driver.mNode)
	    self.connectChildrenNodes(l_dynDrivers,'dynDrivers','dynMaster')
	    
	i_driver.parent = i_dMatchTarget.mNode
	i_driver.doStore('cgmName',"%s_toMatch_%s"%(i_dMatchTarget.getNameAlias(),i_dynObject.getNameAlias())) 
	i_driver.addAttr('cgmType','dynDriver')
	i_driver.addAttr('mClass','cgmMeta.cgmObject')	
	i_driver.addAttr('dynMatchAttrs',attrType='string',lock=True)	
	i_driver.doName()

	i_driver.rotateOrder = i_dynObject.rotateOrder#Match rotate order
	log.info("dynDriver: '%s' >> '%s'"%(i_dMatchTarget.getShortName(),i_driver.getShortName()))
	
	#self.connectChildNode(i_driver,'dynDriver_%s'%index,'dynMaster')	
	i_driver.connectChildNode(i_dynObject,'dynMatchTarget')
	
	
	#>>> Match attr setting
	if l_matchAttrs is None and not i_driver.getAttr('dynMatchAttrs'):
	    #Only preload this if we have no arg and none are set
	    log.info("Preloading attrs....")
	    l_matchAttrs = ['translate','rotate']
	    
	if l_matchAttrs:
	    for attr in l_matchAttrs:
		if not i_dynObject.hasAttr(attr) and i_dMatchTarget.hasAttr(attr):
		    log.warning("cgmDynamicMatch.verifyMatchTargetDriver>> both object and target lack attribute, removing: '%s'"%attr)
		    l_matchAttrs.remove(attr)
		    
	    i_driver.addAttr("dynMatchAttrs",value = l_matchAttrs, attrType='string', lock = True)    
	
    def doMatch(self, match = None):
	"""
	@kws
	snap -- index of snap object
	match -- index of match object
	"""
	#>>>Initial info
	i_object = self.getMessageInstance('dynObject')
	log.info("cgmDynamicMatch.doMatch>> Object : %s"%i_object.getShortName())
	
	#>>>Figure out our match object
	index = False
	if match is not None and type(match) is int:
	    if match > len(self.dynMatchTargets)-1:
		raise StandardError,"cgmDynamicMatch.doMatch>> Match Index(%s) greater than targets: %s"%(match,self.getMessage('dynMatchTargets',False))
	    if match > len(self.dynDrivers)-1:
		raise StandardError,"cgmDynamicMatch.doMatch>> Match Index(%s) greater than drivers: %s"%(match,self.getMessage('dynDrivers',False))	
	    index = match		    
	elif len(self.dynMatchTargets)>0:#use the first
	    index = 0		    
	else:
	    raise StandardError,"cgmDynamicMatch.doMatch>> No valid arg:  match: %s"%(match)	

	i_driver = cgmMeta.validateObjArg(self.dynDrivers[index],cgmMeta.cgmObject)
	i_target = cgmMeta.validateObjArg(self.dynMatchTargets[index],cgmMeta.cgmObject)	    
	log.info("cgmDynamicMatch.doMatch>> Driver on : %s"%i_driver.getShortName())
	
	#>>>Prematch attr set
	if i_driver.getAttr('dynMatchAttrs'):#if we have something
	    for attr in i_driver.dynMatchAttrs:
		if attr.lower() in ['translate','t']:
		    objTrans = mc.xform (i_driver.mNode, q=True, ws=True, rp=True)#Get trans		    
		    log.info("cgmDynamicMatch.doMatch>> match translate! %s"%objTrans)		    
		    mc.move (objTrans[0],objTrans[1],objTrans[2], [i_object.mNode])#Set trans
		if attr.lower() in ['rotate','r']:
		    objRot = mc.xform (i_driver.mNode, q=True, ws=True, ro=True)#Get rot
		    log.info("cgmDynamicMatch.doMatch>> match rotate! %s"%objRot)		    
		    mc.rotate (objRot[0], objRot[1], objRot[2], [i_object.mNode], ws=True)#Set rot	
		if attr.lower() in ['scale']:
		    objScale = [v for v in mc.getAttr ("%s.scale"%i_target.mNode)[0]]#Get rot
		    log.info("cgmDynamicMatch.doMatch>> match scale! %s"%objScale)		    		    
		    mc.scale (objScale[0], objScale[1], objScale[2], [i_object.mNode], os=True)#Set rot	
	else:
	    raise NotImplementedError,"cgmDynamicMatch.doMatch>> no attrs found: %s"%i_driver.getAttr('dynMatchAttrs')
   
    def doSnap(self,snap = None, snapMode = ['point','orient']):
	"""
	@kws
	snap -- index of snap object
	"""
	#>>>Initial info
	i_object = self.getMessageInstance('dynObject')
	log.info("cgmDynamicMatch.doSnap>> Object : %s"%i_object.getShortName())
	
	#>>>Figure out our match object
	index = False
	if snap is not None and type(snap) is int:
	    if snap > len(self.dynSnapTargets):
		raise StandardError,"cgmDynamicMatch.doSnap>> Snap Index(%s) greater than targets: %s"%(snap,self.getMessage('dynSnapTargets',False))	
	    index = snap	
	    i_driver = cgmMeta.validateObjArg(self.dynSnapTargets[index],cgmMeta.cgmObject)
	else:
	    raise StandardError,"cgmDynamicMatch.doSnap>> No valid arg: snap: %s | match: %s"%(snap,match)	


	log.info("cgmDynamicMatch.doSnap>> Driver on : %s"%i_driver.getShortName())
	
	#>>>Prematch attr set
	for attr in snapMode:
	    if attr.lower() in ['move','point','parent','translate']:
		objTrans = mc.xform (i_driver.mNode, q=True, ws=True, rp=True)#Get trans		    
		log.info("cgmDynamicMatch.doSnap>> match translate! %s"%objTrans)		    
		mc.move (objTrans[0],objTrans[1],objTrans[2], [i_object.mNode])#Set trans
	    if attr.lower() in ['orient','parent','rotate']:
		objRot = mc.xform (i_driver.mNode, q=True, ws=True, ro=True)#Get rot
		log.info("cgmDynamicMatch.doSnap>> match rotate! %s"%objRot)		    
		mc.rotate (objRot[0], objRot[1], objRot[2], [i_object.mNode], ws=True)#Set rot			
	    
	
    def doPurge(self):
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False
	
	l_dynDrivers = self.getMessage('dynDrivers') or []
	for d in l_dynDrivers:
	    try:
		i_driver = cgmMeta.cgmObject(d)
		if not i_driver.getConstraintsFrom():
		    mc.delete(i_driver.mNode)
	    except:log.warning("cgmDynamicMatch.doPurge>> found no driver on : %s"%d)
	
	i_object = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True)
	if i_object:
	    for a in self.l_dynAttrs:
		if i_object.hasAttr(a):
		    attributes.doDeleteAttr(i_object.mNode,a)
	    if i_object.hasAttr('dynMatchTargetNull'):
		attributes.doDeleteAttr(i_object.mNode,'dynMatchTargetNull')
		
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmDynParentGroup
#=========================================================================
d_DynParentGroupModeAttrs = {0:['space'],
                             1:['orientTo'],
                             2:['orientTo','follow']}
class cgmDynParentGroup(cgmMeta.cgmObject):
    def __init__(self,node = None, name = None, dynGroup = None,
                 dynParents = None,dynChild = None,
                 dynMode = None, setClass = False,*args,**kws):
        """ 
        Dynamic parent group class. This is a rework of the great work done by our talented
	friend John Doublestein and is done with permission.
        
        Keyword arguments:
        dynParents(list) -- list of parent targets
        mode(list) -- parent/follow/orient
        """

	def _isGroupValidForChild(child,group):
	    """
	    To pass a group in the initialzation as the group, we need to check a few things
	    """
	    i_child = cgmMeta.validateObjArg(child,cgmMeta.cgmObject,noneValid=True)
	    i_group = cgmMeta.validateObjArg(group,cgmMeta.cgmObject,noneValid=True)
	    if not i_child or not i_group:#1) We need args
		return False
	    
	    if not i_child.isChildOf(i_group):#2) the child has to be a child of the group
		return False
	    if i_child.hasAttr('dynParentGroup'):#3) the child is already connected
		if i_child.dynParentGroup != i_group:
		    log.debug("cgmDynParentGroup.isGroupValidForChild>> Child already has dynParentGroup: '%s'"%i_child.getMessage('dynParentGroup'))
		    return False
		else:
		    return True
	    return True	
        ### input check  
        log.debug("In cgmDynParentGroup.__init__ node is '%s'"%node)
	i_dynChild = cgmMeta.validateObjArg(dynChild,cgmMeta.cgmObject,noneValid=True)
	i_argDynGroup = cgmMeta.validateObjArg(dynGroup,cgmMeta.cgmObject,noneValid=True)
	log.debug("i_dynChild: %s"%i_dynChild)
	__justMade__ = False
	#TODO allow to set dynGroup
	if i_dynChild:
	    pBuffer = i_dynChild.getMessage('dynParentGroup') or False
	    log.debug("pBuffer: %s"%pBuffer)
	    if pBuffer:
		node = pBuffer[0]
	    elif _isGroupValidForChild( i_dynChild,i_argDynGroup):
		log.debug("cgmDynParentGroup.__init__>>Group passed and valid")
		node = i_argDynGroup.mNode
		__justMade__ = False		
	    else:#we're gonna make a group
		node = i_dynChild.doGroup()
		__justMade__ = True
	
	super(cgmMeta.cgmObject, self).__init__(node = node,name = name,nodeType = 'transform') 
	self.l_dynAttrs = ['space','follow','orientTo']
	
	#Unmanaged extend to keep from erroring out metaclass with our object spectific attrs
	self.UNMANAGED.extend(['arg_ml_dynParents','_mi_dynChild','_mi_followDriver','d_indexToAttr','l_dynAttrs'])
	if i_dynChild:self._mi_dynChild=i_dynChild
	else:self._mi_dynChild=False
	    
	if kws:log.debug("kws: %s"%str(kws))
	if args:log.debug("args: %s"%str(args)) 	
	doVerify = kws.get('doVerify') or False
	
	arg_ml_dynParents = cgmMeta.validateObjListArg(dynParents,cgmMeta.cgmObject,noneValid=True)
	log.debug("arg_ml_dynParents: %s"%arg_ml_dynParents)
	
        if not self.isReferenced():
	    if not self.__verify__(*args,**kws):
		raise StandardError,"cgmDynParentGroup.__init__>> failed to verify!"
	    
	log.debug("cgmDynParentGroup.__init__>> dynParents: %s"%self.getMessage('dynParents',False))
	for p in arg_ml_dynParents:
	    log.debug("Adding dynParent: %s"%p.mNode)
	    self.addDynParent(p)
	    
	if dynMode is not None:
	    try:
		self.dynMode = dynMode
	    except StandardError,error:
		log.error("cgmDynParentGroup.__init__>>mode set fal! | dynMode: %s | error: "%(dynMode,error))
	    
	if __justMade__ and i_dynChild and arg_ml_dynParents:
	    self.addDynChild(i_dynChild)
	    self.rebuild()
	
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # functions
    #======================================================================
    def __verify__(self,*args,**kws):
	if self.hasAttr('mClass') and self.mClass!='cgmDynParentGroup':
	    raise StandardError, "cgmDynParentGroup.__verify__>> This object has a another mClass and setClass is not set to True"
	#Check our attrs
	if self._mi_dynChild:
	    self.addDynChild(self._mi_dynChild)
	    #self.doStore('cgmName',self._mi_dynChild.mNode)
	self.addAttr('mClass','cgmDynParentGroup',lock=True)#We're gonna set the class because it's necessary for this to work
	self.addAttr('cgmType','dynParentGroup',lock=True)#We're gonna set the class because it's necessary for this to work
	
	self.addAttr('dynMode',attrType = 'enum', enumName= 'space:orient:follow', keyable = False, hidden=True)
        self.addAttr('dynChild',attrType = 'messageSimple',lock=True)
        self.addAttr('dynParents',attrType = 'message',lock=True)
	self.addAttr('dynDrivers',attrType = 'message',lock=True)
	self.addAttr('dynFollow',attrType = 'messageSimple',lock=True)				
	
	#Unlock all transform attriutes
	for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
	    cgmMeta.cgmAttr(self,attr,lock=False)
	self.doName()
	return True
    
    def rebuild(self,*a,**kw):
        """ Rebuilds the buffer data cleanly """ 
	log.debug("rebuild>>>")
	#Must have at least 2 targets
	if len(self.dynParents)<2:
	    log.error("cgmDynParentGroup.rebuild>> Need at least two dynParents. Build failed: '%s'"%self.getShortName())
	    return False
	i_child = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,noneValid=False)
	
	#TODO First scrub nodes and what not
	
	#Check our attrs
	d_attrBuffers = {}
	for a in self.l_dynAttrs:
	    if i_child.hasAttr(a):#we probably need to index these to the previous settings in case order changes
		d_attrBuffers[a] = attributes.doGetAttr(i_child.mNode,a)
	    if a not in d_DynParentGroupModeAttrs[self.dynMode]:
		attributes.doDeleteAttr(i_child.mNode,a)
	if d_attrBuffers:log.debug("d_attrBuffers: %s"%d_attrBuffers)
	
	l_parentShortNames = [cgmNode(o).getNameAlias() for o in self.getMessage('dynParents')]
	log.debug("parentShortNames: %s"%l_parentShortNames)
	
	for a in d_DynParentGroupModeAttrs[self.dynMode]:
	    i_child.addAttr(a,attrType='enum',enumName = ':'.join(l_parentShortNames),keyable = True, hidden=False)
	
	#Make our groups
	#One per parent, copy parent transform
	#Make our attrs
	if self.dynMode == 2:#Follow - needs an extra follow group
	    self.verifyFollowDriver()
	elif self.dynFollow:
	    mc.delete(self.getMessage('dynFollow'))
	
	#Verify our parent drivers:
	for i_p in [cgmMeta.cgmObject(o) for o in self.getMessage('dynParents')]:
	    log.debug("verifyParentDriver: %s"%i_p.getShortName())
	    self.verifyParentDriver(i_p)
	
	#i_child.addAttr('space',attrType='enum',enumName = ':'.join(l_parentShortNames),keyable = True, hidden=False)
	
	#Verify constraints    
	self.verifyConstraints()
	
	return 'Done'    
	#Check constraint

    def addDynChild(self,arg):
	i_child = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
	if i_child == self:
	    raise StandardError, "cgmDynParentGroup.addDynChild>> Cannot add self as dynChild"
	
	#Make sure the child is a descendant
	if not self.isParentOf(i_child):
	    log.warning("cgmDynParentGroup.addDynChild>> dynChild isn't not heirarchal child: '%s'"%i_child.getShortName())
	    return False
	
	if i_child.hasAttr('dynParentGroup') and i_child.dynParentGroup == self:
	    log.debug("cgmDynParentGroup.addDynChild>> dynChild already connected: '%s'"%i_child.getShortName())
	    return True
	
	log.debug("cgmDynParentGroup.addDynChild>> Adding dynChild: '%s'"%i_child.getShortName())
	self.connectChildNode(i_child,'dynChild','dynParentGroup')#Connect the nodes
	self.doStore('cgmName',i_child.mNode)
	#Must be a descendant
	#Add attrs per mode
	#setup per mode
	#see if it has a dynDriver per target
	#if we make changes, we have to veriy
	
    def addDynParent(self,arg,index = None, alias = None):
	i_dParent = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
	if not i_dParent:
	    raise StandardError, "cgmDynParentGroup.addDynParent>> Failed to cgmMeta.validate: %s"%arg	    
	if self == i_dParent:
	    raise StandardError, "cgmDynParentGroup.addDynParent>> Cannot add self as target"
	if not i_dParent.isTransform():
	    raise StandardError, "cgmDynParentGroup.addDynParent>> Target has no transform: '%s'"%i_dParent.getShortName()
	log.debug("cgmDynParentGroup.addDynParent>> '%s'"%i_dParent.getShortName())

	ml_dynParents = [cgmMeta.cgmObject(o) for o in self.getMessage('dynParents')]
	log.debug(">>>>>>>>>>>>> Start add %s"%self.getMessage('dynParents',False))
	
	if i_dParent in ml_dynParents:
	    log.debug("cgmDynParentGroup.addDynParent>> Child already connected: %s"%i_dParent.getShortName())
	    return True
	
	if alias is not None:
	    i_dynParent.addAttr('cgmAlias', str(alias),lock = True)
	
	log.debug("cgmDynParentGroup.addDynParent>> Adding target: '%s'"%i_dParent.getShortName())
	ml_dynParents.append(i_dParent)	
	log.debug(">>>>>>>>>>>>> data add %s"%ml_dynParents)	
	self.connectChildrenNodes(ml_dynParents,'dynParents')#Connect the nodes
	log.debug(">>>>>>>>>>>>> after add %s"%self.getMessage('dynParents',False))
	
    def verifyConstraints(self):
	"""
	1) are we constrained
	2) are constraints correct - right type, right targets...it's probably faster just to rebuild...
	3) 
	"""
	l_dynParents = self.getMessage('dynParents')
	if len(l_dynParents)<2:
	    log.error("cgmDynParentGroup.verifyConstraints>> Need at least two dynParents. Build failed: '%s'"%self.getShortName())
	    return False
	if self.dynMode == 2 and not self.dynFollow:
	    raise StandardError, "cgmDynParentGroup.verifyConstraints>> must have follow driver for follow mode: '%s'"%self.getShortName()
	try:#initialize parents
	    ml_dynParents = cgmMeta.validateObjListArg(l_dynParents,cgmMeta.cgmObject,False)
	    #l_dynDrivers = [i_obj.getMessage('dynDriver')[0] for i_obj in ml_dynParents]
	    l_dynDrivers = self.getMessage('dynDrivers')
	    i_dynChild = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,False)	    
	except StandardError,error:
	    raise StandardError,"cgmDynParentGroup.verifyConstraints>> dynParent/dynChild initialization failed! | %s"%(error)
	try:#Check current
	    currentConstraints = self.getConstraintsTo()
	    log.debug("currentConstraints: %s"%currentConstraints)
	    if currentConstraints:mc.delete(currentConstraints)#Delete existing constraints
	    if self.dynMode == 2:
		followConstraints = self.dynFollow.getConstraintsTo()
		log.debug("followConstraints: %s"%followConstraints)		
		if followConstraints:mc.delete(followConstraints)#Delete existing constraints		
	except StandardError,error:
	    log.error("cgmDynParentGroup.verifyConstraints>> Delete constraints fail! | %s"%(error))
	
	children = self.getChildren()
	ml_children = [cgmMeta.cgmObject(c) for c in children]
	for i_c in ml_children:
	    i_c.parent = self.parent
	
	try:#Build constraints
	    i_dynParentConst = False
	    i_dynPointConst = False
	    i_dynOrientConst = False
	    
	    if self.dynMode == 0:#Parent
		cBuffer = mc.parentConstraint(l_dynDrivers,self.mNode,maintainOffset = True)[0]
		i_dynConst = cgmNode(cBuffer)
	    if self.dynMode == 1:#Orient
		cBuffer = mc.orientConstraint(l_dynDrivers,self.mNode,maintainOffset = True)[0]
		i_dynConst = cgmNode(cBuffer)
	    if self.dynMode == 2:#Follow - needs an extra follow group
		pBuffer = mc.pointConstraint(self.dynFollow.mNode,self.mNode,maintainOffset = True)[0]
		cBuffer = mc.parentConstraint(l_dynDrivers,self.dynFollow.mNode,maintainOffset = True)[0]
		oBuffer = mc.orientConstraint(l_dynDrivers,self.mNode,maintainOffset = True)[0]
		
		i_dynFollowConst = cgmNode(cBuffer)
		i_dynPointConst = cgmNode(pBuffer)
		i_dynConst = cgmNode(oBuffer)
	except StandardError,error:
	    log.error("cgmDynParentGroup.verifyConstraints>> Build constraints fail! | %s"%(error))
	try:#Name and store    
	    for i_const in [i_dynParentConst,i_dynPointConst,i_dynOrientConst]:
		if i_const:
		    i_const.doStore('cgmName',i_dynChild.mNode) 
		    i_const.addAttr('cgmTypeModifier','dynDriver')
		    i_const.addAttr('mClass','cgmNode')	
		    i_const.doName()
		    
	    if i_dynParentConst:self.connectChildNode(i_dynParentConst,'dynParentConstraint','dynMaster')
	    if i_dynPointConst:self.connectChildNode(i_dynPointConst,'dynPointConstraint','dynMaster')	
	    if i_dynOrientConst:self.connectChildNode(i_dynOrientConst,'dynOrientConstraint','dynMaster')	
	except StandardError,error:
	    log.error("cgmDynParentGroup.verifyConstraints>> Name and store fail! | %s"%(error))
	
	#Build nodes
	ml_nodes = []
	for i,i_p in enumerate(ml_dynParents):
	    if self.dynMode == 2:#Follow
		i_followCondNode = cgmNode(nodeType='condition')
		i_followCondNode.operation = 0
		mc.connectAttr("%s.follow"%i_dynChild.mNode,"%s.firstTerm"%i_followCondNode.mNode)
		mc.setAttr("%s.secondTerm"%i_followCondNode.mNode,i)
		mc.setAttr("%s.colorIfTrueR"%i_followCondNode.mNode,1)
		mc.setAttr("%s.colorIfFalseR"%i_followCondNode.mNode,0)
		mc.connectAttr("%s.outColorR"%i_followCondNode.mNode,"%s.w%s"%(i_dynFollowConst.mNode,i))
		
		i_followCondNode.doStore('cgmName',i_p.mNode) 
		i_followCondNode.addAttr('cgmTypeModifier','dynFollow')
		i_followCondNode.addAttr('mClass','cgmNode')	
		i_followCondNode.doName()
		
		ml_nodes.append(i_followCondNode)
		
	    i_condNode = cgmNode(nodeType='condition')
	    i_condNode.operation = 0
	    attr = d_DynParentGroupModeAttrs[self.dynMode][0]
	    mc.connectAttr("%s.%s"%(i_dynChild.mNode,attr),"%s.firstTerm"%i_condNode.mNode)
	    mc.setAttr("%s.secondTerm"%i_condNode.mNode,i)
	    mc.setAttr("%s.colorIfTrueR"%i_condNode.mNode,1)
	    mc.setAttr("%s.colorIfFalseR"%i_condNode.mNode,0)
	    mc.connectAttr("%s.outColorR"%i_condNode.mNode,"%s.w%s"%(i_dynConst.mNode,i))
	    
	    i_condNode.doStore('cgmName',"%s_to_%s"%(i_dynChild.getShortName(),i_p.getShortName())) 
	    i_condNode.addAttr('cgmTypeModifier','dynParent')
	    i_condNode.addAttr('mClass','cgmNode')	
	    i_condNode.doName()	 
	    
	self.connectChildrenNodes(ml_nodes,'dynNodes','dynMaster')
	    
	for i_c in ml_children:
	    i_c.parent = self.mNode
	    
    def verifyParentDriver(self,arg):
	"""
	1) if arg is a dynParent
	2) check it's driver
	3) Make if necesary
	"""
	i_dynChild = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,noneValid=True) 
	if not i_dynChild:
	    raise StandardError, "cgmDynParentGroup.verifyParentDriver>> Must have dynChild. None found"	    
	i_dParent = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
	if not i_dParent:
	    raise StandardError, "cgmDynParentGroup.verifyParentDriver>> arg fail: %s"%arg
	log.debug(self.dynParents)
	if i_dParent.getLongName() not in self.getMessage('dynParents',True):
	    raise StandardError, "cgmDynParentGroup.verifyParentDriver>> not a dynParent: %s"%i_dParent.getShortName()
	
	index = self.getMessage('dynParents',True).index(i_dParent.getLongName())
	log.debug("cgmDynParentGroup.verifyParentDriver>> dynParents index: %s"%index)
	#dBuffer = self.getMessage('dyDriver_%s'%index)
	l_dynDrivers = self.getMessage('dynDrivers',True)
	
	#See if we have a good driver
	foundMatch = False
	if l_dynDrivers and len(l_dynDrivers) > index:
	    buffer = l_dynDrivers[index]
	    log.debug("buffer: %s"%cgmMeta.cgmObject( buffer ).getMessage('dynTarget',True))
	    log.debug("child: %s"%i_dynChild.getLongName())
	    if cgmMeta.cgmObject( buffer ).getMessage('dynTarget',True) == [i_dynChild.getLongName()]:
		log.debug("dynDriver: found")
		i_driver = cgmMeta.validateObjArg(l_dynDrivers[index],cgmMeta.cgmObject,noneValid=False)
		foundMatch = True
	if not foundMatch:
	    log.debug("dynDriver: creating")	
	    i_driver = i_dynChild.doDuplicateTransform()
	    l_dynDrivers.insert(index,i_driver.mNode)
	    self.connectChildrenNodes(l_dynDrivers,'dynDrivers','dynMaster')
	    #i_driver = i_dParent.doDuplicateTransform()
	    
	i_driver.parent = i_dParent.mNode
	i_driver.doStore('cgmName',"%s_driving_%s"%(i_dParent.getNameAlias(),i_dynChild.getNameAlias())) 
	i_driver.addAttr('cgmType','dynDriver')
	i_driver.addAttr('mClass','cgmMeta.cgmObject')	
	i_driver.doName()

	i_driver.rotateOrder = i_dynChild.rotateOrder#Match rotate order
	log.debug("dynDriver: '%s' >> '%s'"%(i_dParent.getShortName(),i_driver.getShortName()))
	
	#self.connectChildNode(i_driver,'dynDriver_%s'%index,'dynMaster')	
	i_driver.connectChildNode(i_dynChild,'dynTarget')	
	
    def verifyParentDriver2(self,arg):
	"""
	1) if arg is a dynParent
	2) check it's driver
	3) Make if necesary
	"""
	i_dParent = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
	if not i_dParent:
	    raise StandardError, "cgmDynParentGroup.verifyParentDriver>> arg fail: %s"%arg
	log.debug(self.dynParents)
	if i_dParent.getLongName() not in self.getMessage('dynParents',True):
	    raise StandardError, "cgmDynParentGroup.verifyParentDriver>> not a dynParent: %s"%i_dParent.getShortName()
	    
	gBuffer = i_dParent.getMessage('dynDriver') or False
	if gBuffer:
	    log.debug("dynDriver: found")
	    i_driver = cgmMeta.validateObjArg(gBuffer[0],cgmMeta.cgmObject,noneValid=False)
	else:
	    log.debug("dynDriver: creating")	
	    #i_driver = self._mi_dynChild.doDuplicateTransform()	    
	    i_driver = i_dParent.doDuplicateTransform()
	    
	i_driver.parent = i_dParent.mNode
	i_driver.doStore('cgmName',i_dParent.mNode) 
	i_driver.addAttr('cgmType','dynDriver')
	i_driver.addAttr('mClass','cgmMeta.cgmObject')	
	i_driver.doName()
	
	i_driver.rotateOrder = i_dParent.rotateOrder#Match rotate order
	log.debug("dynDriver: '%s' >> '%s'"%(i_dParent.getShortName(),i_driver.getShortName()))
	i_dParent.connectChildNode(i_driver,'dynDriver','dynMaster')	
	
	
    def verifyFollowDriver(self):
	i_dynChild = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,True)
	if not i_dynChild:
	    raise StandardError, "cgmDynParentGroup.verifyFollowDriver>> no dynChild found"
	
	gBuffer = self.getMessage('dynFollow') or False
	if gBuffer:
	    i_followDriver = cgmMeta.validateObjArg(gBuffer[0],cgmMeta.cgmObject,noneValid=True)
	else:
	    i_followDriver = i_dynChild.doDuplicateTransform()
	    
	i_followDriver.doStore('cgmName',i_dynChild.mNode) 
	i_followDriver.addAttr('cgmType','dynFollow')
	i_followDriver.addAttr('mClass','cgmMeta.cgmObject')		
	i_followDriver.doName()
	
	i_followDriver.rotateOrder = i_dynChild.rotateOrder#Match rotate order
	log.debug("dynFollow: '%s'"%i_followDriver.getShortName())
	
	self.connectChildNode(i_followDriver,'dynFollow','dynMaster')
	self._mi_followDriver = i_followDriver
	
    def doSwitchSpace(self,attr,index,deleteLoc = True):
	#Swich setting shile holding 
	l_attrs = ['space','follow','orientTo']
	if attr not in l_attrs:
	    raise StandardError,"cgmDynParentGroup.doSwitchSpace>> Not a valid attr: %s"%attr	
	
	i_child = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,True)
	d_attr = cgmMeta.validateAttrArg([i_child.mNode,attr])
	if not i_child and d_attr:
	    raise StandardError,"cgmDynParentGroup.doSwitchSpace>> doSwitchSpace doesn't have enough info. Rebuild recommended"
	if index == i_child.getAttr(attr):
	    log.debug("cgmDynParentGroup.doSwitchSpace>> Already that mode")	    
	    return True
	elif index+1 > len(d_attr['mi_plug'].p_enum):
	    raise StandardError,"cgmDynParentGroup.doSwitchSpace>> Index(%s) greater than options: %s"%(index,d_attr['mi_plug'].getEnum())	
	    
	
	objTrans = mc.xform (i_child.mNode, q=True, ws=True, rp=True)#Get trans
	objRot = mc.xform (i_child.mNode, q=True, ws=True, ro=True)#Get rot
	i_loc = i_child.doLoc()#loc
	
	mc.setAttr("%s.%s"%(i_child.mNode,attr),index)#Change it
	mc.move (objTrans[0],objTrans[1],objTrans[2], [i_child.mNode])#Set trans
	mc.rotate (objRot[0], objRot[1], objRot[2], [i_child.mNode], ws=True)#Set rot	
	
	if deleteLoc:i_loc.delete()
	
    def doPurge(self):
	if self.isReferenced():
	    log.warning('This function is not designed for referenced buffer nodes')
	    return False
	nodes = self.getMessage('dynNodes') or False
	if nodes:mc.delete(nodes)
	l_dynParents = self.getMessage('dynParents') or []
	for d in l_dynParents:
	    try:
		i_driver = cgmMeta.cgmObject( cgmMeta.cgmObject(d).getMessage('dynDriver')[0] )
		if not i_driver.getConstraintsFrom():
		    mc.delete(i_driver.mNode)
	    except:log.warning("cgmDynParentGroup.doPurge>> found no driver on : %s"%d)
	
	dynFollow = self.getMessage('dynFollow',False)
	if dynFollow:
	    try:mc.delete(dynFollow)
	    except:log.warning("cgmDynParentGroup.doPurge>> dynFollow failed to delete: %s"%dynFollow)
	
	currentConstraints = self.getConstraintsTo()
	if currentConstraints:mc.delete(currentConstraints)#Delete existing constraints	
	
	i_child = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,noneValid=True)
	if i_child:
	    for a in self.l_dynAttrs:
		if i_child.hasAttr(a):
		    attributes.doDeleteAttr(i_child.mNode,a)
	    if i_child.hasAttr('dynParentGroup'):
		attributes.doDeleteAttr(i_child.mNode,'dynParentGroup')

#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
r9Meta.registerMClassInheritanceMapping()
#r9Meta.registerMClassNodeMapping(nodeTypes = ['network','transform','objectSet'])#What node types to look for
