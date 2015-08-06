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
# cgmDynamicSwitch
#=========================================================================
class cgmDynamicSwitch(cgmMeta.cgmObject):
    def __init__(self,node = None, name = None, dynSuffix = None, dynPrefix = None,
                 dynOwner = None, moduleInstance = None,
                 *args,**kws):
        """
        Dynamic Switch Setup. Controller class for cgmDynamicMatch setups. The idea is to register various switches that then are switched and set on call. 
        For example, on the leg 1)ik>fk, 2) fk>ik no knee, 3)fk>ik knee setup

        Keyword arguments:
        dynSwitchTargets(list) -- list of match targets
        mode(list) -- parent/follow/orient
        """
        l_plugBuffer = ['dynSwitch']
        if dynSuffix is not None:
            l_plugBuffer.append(str(dynSuffix))    
        if dynPrefix is not None:
            l_plugBuffer.insert(0,str(dynPrefix))  
        str_dynSwitchDriverPlug = '_'.join(l_plugBuffer)
	
        if dynOwner is not None:
	    if mc.objExists(dynOwner):
		node = attributes.returnMessageObject(dynOwner, str_dynSwitchDriverPlug) or None
		#log.debug("pBuffer: %s"%pBuffer)
		#if pBuffer:
		    #node = pBuffer[0]

        log.debug("In cgmDynamicSwitch.__init__ node: %s"%node)
	log.debug("In cgmDynamicSwitch.__init__ name: %s"%name)	
	
        super(cgmDynamicSwitch, self).__init__(node = node, name = name) 
	
	#====================================================================================
    
	#Unmanaged extend to keep from erroring out metaclass with our object spectific attrs
	self.UNMANAGED.extend(['_str_dynSwitchDriverPlug','d_indexToAttr','l_dynAttrs'])	
	
	#>>> TO USE Cached instance ---------------------------------------------------------
	if self.cached:
	    log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.__class__)
	    return

        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args)) 	
        doVerify = kws.get('doVerify') or False
	
        self._str_dynSwitchDriverPlug = str_dynSwitchDriverPlug

        if not self.isReferenced():
            if not self.__verify__(*args,**kws):
                raise StandardError,"cgmDynamicSwitch.__init__>> failed to verify!"
	    
	#>>>dynOwner
	i_dynOwner = cgmMeta.validateObjArg(dynOwner,'cgmObject',noneValid=True)#...this must be after the super. If before, it blows things up...not sure why...
        if i_dynOwner:
            self.setDynOwner(i_dynOwner)

        log.debug("self._str_dynSwitchDriverPlug>> '%s'"%self._str_dynSwitchDriverPlug)

    def __verify__(self,*args,**kws):
        log.debug("In %s.__verify__ "%self.getShortName())	
        if self.hasAttr('mClass') and self.mClass!='cgmDynamicSwitch':
            raise StandardError, "cgmDynamicSwitch.__verify__>> This object has a another mClass and setClass is not set to True"

        self.addAttr('mClass','cgmDynamicSwitch',lock=True)#We're gonna set the class because it's necessary for this to work
        self.addAttr('cgmType','dynSwitchSystem',lock=True)#We're gonna set the class because it's necessary for this to work

        self.addAttr('dynOwner',attrType = 'messageSimple',lock=True)
        self.addAttr('l_dynSwitchAlias',initialValue='[]',attrType = 'string',lock=True)
        self.addAttr('d_dynSwitchSettings',initialValue='{}',attrType = 'string',lock=True)
        self.addAttr('d_dynSwitchPostSettings',initialValue='{}',attrType = 'string',lock=True)

        #Unlock all transform attriutes
        for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            cgmMeta.cgmAttr(self,attr,lock=False)
        self.doName()
        return True

    def verifyStoredAttr(self,attrArg):
        """Verify an attr is stored and return the index"""
        #Switch attr
        l_attrs = self.getStoredAttrsList()
        d_attrReturn = cgmMeta.validateAttrArg(attrArg,noneValid=True)
        if not d_attrReturn:
            log.error("%s.verifyStoredAttr>> Invalid attrArg arg: '%s'"%(self.getShortName(),attrArg))
            return False

        mPlug_attr = d_attrReturn['mi_plug']
        if mPlug_attr.p_combinedName in l_attrs:
            log.debug("%s.verifyStoredAttr>> SwitchAttr already connected: %s"%(self.getShortName(),mPlug_attr.p_combinedShortName))
            index_attr = l_attrs.index(mPlug_attr.p_combinedName)

        else:#add it
            index =  self.returnNextAvailableAttrCnt("dynStoredAttr_")
            log.debug("%s.verifyStoredAttr>> Attr to register: '%s'"%(self.getShortName(),mPlug_attr.p_combinedShortName))
            self.doStore('dynStoredAttr_%s'%index,mPlug_attr.p_combinedName)	
            l_attrs.append(mPlug_attr.p_combinedName)

            index_attr = l_attrs.index(mPlug_attr.p_combinedName)
            if index != index_attr:
                raise StandardError, "%s.verifyStoredAttr>> switch attr indexes do not match!"%self.getShortName()  	
        return index_attr

    def setDynOwner(self,arg):
        i_object = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=False)
        if i_object == self:
            raise StandardError, "%s.setDynOwner>> Cannot add self as dynObject"%self.getShortName()

        if i_object.hasAttr(self._str_dynSwitchDriverPlug) and i_object.getAttr(self._str_dynSwitchDriverPlug) == self:
            log.debug("%s.setDynOwner>> dynOwner already connected: '%s'"%(self.getShortName(),i_object.getShortName()))
            return True

        log.debug("%s.setDynOwner>> Adding dynObject: '%s'"%(self.getShortName(),i_object.getShortName()))
        self.connectChildNode(i_object,'dynOwner',self._str_dynSwitchDriverPlug)#Connect the nodes
        self.doStore('cgmName',i_object.mNode)
        self.doName()

        if not self.parent:#If we're not parented, parent to dynObject, otherwise, it doen't really matter where this is
            self.parent = i_object.mNode

    def setPostmatchAliasAttr(self,alias = None, attrArg = None, attrValue = None):
        str_alias = str(alias)
        l_dynSwitchAliasBuffer = self.l_dynSwitchAlias
        if str_alias not in l_dynSwitchAliasBuffer:
            raise StandardError,"%s.setPostmatchArg>> alias not found. Can't add: '%s'"%(self.getShortName(),str_alias)

        index_attr = self.verifyStoredAttr(attrArg)

        #>>Get our Attribute registered
        d_dynSwitchPostSettings = self.d_dynSwitchPostSettings or {}

        #>>> Build our dict
        d_buffer = d_dynSwitchPostSettings.get(str_alias) or {}
        l_keyValues = [attrValue]
        l_keyNames = ['atrV']
        for i,key in enumerate(l_keyNames):
            if l_keyValues[i] is not None and type(l_keyValues[i]) in [float,int]:
                d_buffer[key] = l_keyValues[i]
            elif l_keyValues[i] is not None:
                log.error("%s.setPostmatchAliasAttr>> Bad value for '%s': %s"%(self.getShortName(),key,l_keyValues[i]))	    		
        d_buffer['atrIdx'] = index_attr	

        d_dynSwitchPostSettings[str_alias] = d_buffer
        self.d_dynSwitchPostSettings = d_dynSwitchPostSettings#push back

    #======================================================================		
    #>>> Switch stuff
    def getMatchSetsList(self,maxCheck = 75):
        l_iterAttr = []
        ml_iterAttr = []
        for i in range(maxCheck):
            if i == maxCheck-1 or not self.msgList_exists('ml_dynMatchSet_%s'%i):
                break
            else:
                l_buffer = self.msgList_get('ml_dynMatchSet_%s'%i,asMeta=False)
                l_iterAttr.append(l_buffer)
                ml_iterAttr.append(cgmMeta.validateObjListArg(l_buffer,cgmMeta.cgmObject))
        log.debug("%s.getMatchSetsList>>> dynMatch sets -- cnt: %s | lists: %s"%(self.getShortName(),len(l_iterAttr),l_iterAttr)) 	
        return ml_iterAttr

    def getStoredAttrsList(self,maxCheck = 75,asMeta = False):
        l_iterAttr = []
        ml_iterAttr = []
        for i in range(maxCheck):
            buffer = self.getMessage('dynStoredAttr_%s'%i,False)
            if i == maxCheck-1 or not buffer:
                break
            else:
                d_attrReturn = cgmMeta.validateAttrArg(buffer,noneValid=True)
                if not d_attrReturn:
                    log.error("%s.getStoredAttrsList>> Invalid attr arg: '%s'"%(self.getShortName(),buffer))
                    break
                mPlug_switchAttr = d_attrReturn['mi_plug']		
                l_iterAttr.append(mPlug_switchAttr.p_combinedName)
                ml_iterAttr.append(mPlug_switchAttr)
        log.debug("%s.getStoredAttrsList>>> switchAttrs sets -- cnt: %s | lists: %s"%(self.getShortName(),len(l_iterAttr),l_iterAttr)) 	
        if asMeta:return ml_iterAttr
        return l_iterAttr

    def addSwitch(self, alias = None, switchAttrArg = None, switchAttrValue = None, ml_dynMatchSet = None, postSwitchArg = None):
        """
        @kws
        alias(string) -- what the switch will be called
        switchAttrArg(arg) -- cgmMeta.validateAttrArg arg
        switchAttrValue() -- what value to set the switch atter post match
        ml_dynMatchSet -- meta list of cgmDynamicMatch objects
        postSwitchArg(arg) -- {attrArg:value}
        """
        #>>> Validate
        ml_dynMatchSet = cgmMeta.validateObjListArg(ml_dynMatchSet,cgmDynamicMatch,noneValid=True) 
        if not ml_dynMatchSet:raise StandardError, "%s.addDynIterTarget>> Must have ml_dynMatchSet. None found"%self.getShortName()	    
        str_alias = str(alias)

        #======================================================================
        #Switch attr
        index_switchAttr = self.verifyStoredAttr(switchAttrArg)

        #======================================================================
        #Get our match set stuff
        ml_dynMatchSets = self.getMatchSetsList()
        log.debug("cgmDynamicMatch.addSwitch>> match set: %s"%[dynMatch.getShortName() for dynMatch in ml_dynMatchSet])
        for i,mSet in enumerate(ml_dynMatchSets):
            log.debug("cgmDynamicMatch.addSwitch>> match set %s: %s"%(i,[dynMatch.getShortName() for dynMatch in mSet]))

        if ml_dynMatchSet in ml_dynMatchSets:
            log.debug("%s.addSwitch>> Set already connected: %s"%(self.getShortName(),[mSet.getShortName() for mSet in ml_dynMatchSet]))
            index_dynMatchSet = ml_dynMatchSets.index(ml_dynMatchSet)

        else:#add it
            ml_dynMatchSets.append(ml_dynMatchSet)
            index_dynMatchSet = ml_dynMatchSets.index(ml_dynMatchSet)
            self.msgList_connect(ml_dynMatchSet,'ml_dynMatchSet_%s'%index_dynMatchSet)	    
            #if index != index_dynMatchSet:
                #raise StandardError, "%s.addSwitch>> match set indexes do not match!"%self.getShortName()  	    
        #======================================================================	

        #>>Get our Attribute registered
        d_dynSwitchSettings = self.d_dynSwitchSettings or {}
        l_dynSwitchAliasBuffer = self.l_dynSwitchAlias or []
        if str_alias in l_dynSwitchAliasBuffer:
            log.debug("%s.addSwitch>> Attr already in, checking: '%s'"%(self.getShortName(),switchAttrArg))    
        else:
            l_dynSwitchAliasBuffer.append(str_alias)

        index_alias = l_dynSwitchAliasBuffer.index(str_alias)	
        self.l_dynSwitchAlias = l_dynSwitchAliasBuffer#Push back to attr

        #>>> Build our dict
        d_buffer = {}
        l_keyValues = [switchAttrValue]
        l_keyNames = ['atrV']
        for i,key in enumerate(l_keyNames):
            if l_keyValues[i] is not None and type(l_keyValues[i]) in [float,int]:
                d_buffer[key] = l_keyValues[i]
            elif l_keyValues[i] is not None:
                log.debug("%s.addSwitch>> Bad value for '%s': %s"%(self.getShortName(),key,l_keyValues[i]))	    		
        d_buffer['setIdx'] = index_dynMatchSet
        d_buffer['atrIdx'] = index_switchAttr

        #Store it
        d_dynSwitchSettings[str_alias] = d_buffer
        self.d_dynSwitchSettings = d_dynSwitchSettings
        #======================================================================
        if postSwitchArg is not None:
            self.setPostmatchAliasAttr(postSwitchArg)

    #@r9General.Timer	
    def go(self,arg):
        """
        The actual switcher
        """
        def postSet(str_aliasToDo):
            if str_aliasToDo in self.d_dynSwitchPostSettings.keys():
                d_buffer = self.d_dynSwitchPostSettings.get(str_aliasToDo)
                idx_attr = d_buffer.get('atrIdx')
                str_attr = self.getMessage('dynStoredAttr_%s'%idx_attr,False)
                d_postAttrReturn = cgmMeta.validateAttrArg(str_attr,noneValid=True)
                if not d_postAttrReturn:
                    log.error("%s.go>> Invalid switchAttrArg arg: '%s'"%(self.getShortName(),str_attr))
                    return False
                mPlug_postAttr = d_postAttrReturn['mi_plug']
                log.debug("%s.go>> post attr: '%s'"%(self.getShortName(),mPlug_postAttr.p_combinedShortName))	
                log.debug("%s.go>> mPlug_postAttr: %s"%(self.getShortName(),d_buffer.get('atrV')))	
                mPlug_postAttr.value = d_buffer.get('atrV')	

        def isPostSet(str_aliasToDo):
            if str_aliasToDo in self.d_dynSwitchPostSettings.keys():
                d_buffer = self.d_dynSwitchPostSettings.get(str_aliasToDo)
                idx_attr = d_buffer.get('atrIdx')
                str_attr = self.getMessage('dynStoredAttr_%s'%idx_attr,False)
                d_postAttrReturn = cgmMeta.validateAttrArg(str_attr,noneValid=True)
                if not d_postAttrReturn:
                    log.error("%s.go>> Invalid switchAttrArg arg: '%s'"%(self.getShortName(),str_attr))
                    return False
                mPlug_postAttr = d_postAttrReturn['mi_plug']
                log.debug("%s.go>> post attr: '%s'"%(self.getShortName(),mPlug_postAttr.p_combinedShortName))	
                log.debug("%s.go>> mPlug_postAttr: %s"%(self.getShortName(),d_buffer.get('atrV')))	
                if mPlug_postAttr.value != d_buffer.get('atrV'):
                    return False
            return True

        #>>> Validate
        if type(arg) is int:
            if arg > len(self.l_dynSwitchAlias):
                raise StandardError, "%s.go>> int arg %s > than alias list: %s"%(self.getShortName(),arg,self.l_dynSwitchAlias)	    
            str_aliasToDo = self.l_dynSwitchAlias[arg]
        elif type(arg) in [unicode,str]:
            if arg not in self.l_dynSwitchAlias:
                raise StandardError, "%s.go>> str arg %s not in alias list: %s"%(self.getShortName(),arg,self.l_dynSwitchAlias)	     
            str_aliasToDo = arg

        log.debug("%s.go>> str_aliasToDo: %s"%(self.getShortName(),str_aliasToDo))
        d_buffer = self.d_dynSwitchSettings
        ml_dynMatchSet = self.msgList_get("ml_dynMatchSet_%s"%d_buffer[str_aliasToDo]['setIdx'])
        fl_value = d_buffer[str_aliasToDo].get('atrV')

        #>>> Attr2
        idx_attr = d_buffer[str_aliasToDo].get('atrIdx')
        log.debug("%s.go>> idx_attr: %s"%(self.getShortName(),idx_attr))
        str_attr = self.getMessage('dynStoredAttr_%s'%idx_attr,False)
        d_attrReturn = cgmMeta.validateAttrArg(str_attr,noneValid=True)
        if not d_attrReturn:
            log.error("%s.go>> Invalid switchAttrArg arg: '%s'"%(self.getShortName(),str_attr))
            return False
        mPlug_switchAttr = d_attrReturn['mi_plug']

        if mPlug_switchAttr.value == fl_value and isPostSet(str_aliasToDo):
            log.debug("%s.go>> Already in: %s'"%(self.getShortName(),str_aliasToDo))
            postSet(str_aliasToDo)	    
            return True

        log.debug("%s.go>> alias: '%s'"%(self.getShortName(),str_aliasToDo))
        log.debug("%s.go>> set: %s"%(self.getShortName(),[mSet.getShortName() for mSet in ml_dynMatchSet]))
        log.debug("%s.go>> switch attr: '%s'"%(self.getShortName(),mPlug_switchAttr.p_combinedShortName))	
        log.debug("%s.go>> value: %s"%(self.getShortName(),fl_value))

        #======================================================================	
        #>>>Execute
        #Do all matching
        for mSet in ml_dynMatchSet:
            mSet.doMatch()

        #Iter    
        for mSet in ml_dynMatchSet:
            mSet.doIter()

        #AttrMatch    
        for mSet in ml_dynMatchSet:
            mSet.doAttrMatch()

        mPlug_switchAttr.value = fl_value

        postSet(str_aliasToDo)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmDynamicMatch
#=========================================================================
class cgmDynamicMatch(cgmMeta.cgmObject):
    def __init__(self,node = None, name = None, dynNull = None, dynSuffix = None, dynPrefix = None,
                 dynMatchTargets = None, dynSnapTargets = None, dynObject = None,
                 dynMode = None, *args,**kws):
        """
        Dynamic Match Setup. Inspiration for this comes from Jason Schleifer's great AFR work. Retooling for our own purposes.
        The basic idea is a class based match setup for matching fk ik or whatever kind of matching that needs to happen.

        There are three kinds of match types: MatchTargets and SnapTargets.
        1) MatchTarget setup creates a match object from our dynObject to match to,
        2) SnapTarget is just a mappting to give an exisitng transform to snap to
        3) iterTargets are a bit more complicated and involve changing the values of one thing, which moves thing two to match thing 3 and stops

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
                if i_object.getMessageAsMeta(str_dynMatchDriverPlug) != i_null:
                    log.warning("cgmDynamicMatch.isNullValidForObject>> Object already has dynMatchDriver: '%s'"%i_object.getMessage(str_dynMatchDriverPlug))
                    return False
                else:
                    return True
            return True	

        ### input check  
        log.debug("In cgmDynamicMatch.__init__ node: %s"%node)
        i_dynObject = cgmMeta.validateObjArg(dynObject,cgmMeta.cgmObject,noneValid=True)
        i_argDynNull = cgmMeta.validateObjArg(dynNull,cgmDynamicMatch,noneValid=True)
        log.debug("i_dynObject: %s"%i_dynObject)
        __justMade__ = False

        #TODO allow to set dynNull
        if i_dynObject:
            pBuffer = i_dynObject.getMessage(str_dynMatchDriverPlug) or False
            log.debug("pBuffer: %s"%pBuffer)
            if pBuffer:
                node = pBuffer[0]
            elif _isNullValidForObject( i_dynObject,i_argDynNull):
                log.debug("cgmDynamicMatch.__init__>>Null passed and valid")
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

	#>>> TO USE Cached instance ---------------------------------------------------------
	if self.cached:
	    log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.__class__)
	    return
	#====================================================================================
	
        if i_dynObject:self._mi_dynObject = i_dynObject
        else:self._mi_dynObject = False

        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args)) 	
        doVerify = kws.get('doVerify') or False
        self._str_dynMatchDriverPlug = str_dynMatchDriverPlug

        arg_ml_dynMatchTargets = cgmMeta.validateObjListArg(dynMatchTargets,cgmMeta.cgmObject,noneValid=True)
        arg_ml_dynSnapTargets = cgmMeta.validateObjListArg(dynSnapTargets,cgmMeta.cgmObject,noneValid=True)

        log.debug("arg_ml_dynMatchTargets: %s"%arg_ml_dynMatchTargets)

        if not self.isReferenced():
            if not self.__verify__(*args,**kws):
                raise StandardError,"cgmDynamicMatch.__init__>> failed to verify!"

        for p in arg_ml_dynMatchTargets:
            log.debug("Adding dynMatchTarget: %s"%p.mNode)
            self.addDynMatchTarget(p)
        log.debug("cgmDynamicMatch.__init__>> dynMatchTargets: %s"%self.msgList_getMessage('dynMatchTargets',False))

        for p in arg_ml_dynSnapTargets:
            log.debug("Adding dynSnapTarget: %s"%p.mNode)
            self.addDynSnapTarget(p)
        log.debug("cgmDynamicMatch.__init__>> dynSnapTargets: %s"%self.msgList_getMessage('dynSnapTargets',False))

        if __justMade__ and i_dynObject:
            self.addDynObject(i_dynObject)
            #self.rebuild()

        log.debug("self._str_dynMatchDriverPlug>> '%s'"%self._str_dynMatchDriverPlug)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # functions
    #======================================================================
    def __verify__(self,*args,**kws):
        log.debug(">>> %s.__verify__() >> "%(self.p_nameShort) + "="*75)  
        if self.hasAttr('mClass') and self.mClass!='cgmDynamicMatch':
            raise StandardError, "cgmDynamicMatch.__verify__>> This object has a another mClass and setClass is not set to True"
        #Check our attrs
        if self._mi_dynObject:
            self.addDynObject(self._mi_dynObject)
        self.addAttr('mClass','cgmDynamicMatch',lock=True)#We're gonna set the class because it's necessary for this to work
        self.addAttr('cgmType','dynMatchDriver',lock=True)#We're gonna set the class because it's necessary for this to work

        self.addAttr('dynObject',attrType = 'messageSimple',lock=True)
        self.addAttr('dynHiddenSwitch',attrType = 'bool')	
        #self.addAttr('dynMatchTargets',attrType = 'message',lock=True)
        #self.addAttr('dynDrivers',attrType = 'message',lock=True)
        self.addAttr('dynPrematchAttrs',attrType = 'string',lock=True)
        self.addAttr('dynIterAttrs',attrType = 'string',lock=True)
        self.addAttr('dynIterSettings',attrType = 'string',lock=True)

        self.addAttr('l_dynMatchAttrs',initialValue='[]',attrType = 'string',lock=True)		
        self.addAttr('d_dynMatchAttrSettings',initialValue='{}',attrType = 'string',lock=True)	

        #Unlock all transform attriutes
        for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            cgmMeta.cgmAttr(self,attr,lock=False)
        self.doName()
        return True

    def rebuild(self,*a,**kw):
        """ Rebuilds the buffer data cleanly """ 
        log.debug(">>> %s.rebuild() >> "%(self.p_nameShort) + "="*75)  
        #Must have at least 2 targets
        l_dynMatchTargets.msgList_getMessage('dynMatchTargets')
        if len(l_dynMatchTargets)<2:
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
        if d_attrBuffers:log.debug("d_attrBuffers: %s"%d_attrBuffers)

        l_parentShortNames = [cgmMeta.cgmNode(o).getNameAlias() for o in self.msgList_getMessage('dynMatchTargets')]
        log.debug("parentShortNames: %s"%l_parentShortNames)

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
        for i_p in [cgmMeta.cgmObject(o) for o in self.msgList_getMessage('dynMatchTargets')]:
            log.debug("verifyMatchTargetDriver: %s"%i_p.getShortName())
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

        if i_object.hasAttr(self._str_dynMatchDriverPlug) and i_object.getMessageAsMeta(self._str_dynMatchDriverPlug) == self:
            log.debug("cgmDynamicMatch.addDynObject>> dynObject already connected: '%s'"%i_object.getShortName())
            return True

        log.debug("cgmDynamicMatch.addDynObject>> Adding dynObject: '%s'"%i_object.getShortName())
        self.connectChildNode(i_object,'dynObject',self._str_dynMatchDriverPlug)#Connect the nodes
        self.doStore('cgmName',i_object.mNode)

        if not self.parent:#If we're not parented, parent to dynObject, otherwise, it doen't really matter where this is
            self.parent = i_object.mNode

    def addPrematchData(self,d_arg):
        log.debug(">>> %s.addPrematchData(d_arg = %s) >> "%(self.p_nameShort,d_arg) + "="*75)  	
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
        log.debug(">>> %s.setPrematchData() >> "%(self.p_nameShort) + "-"*75)  
        i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
        if not i_dynObject:raise StandardError, "%s.setPrematchData>> Must have dynObject. None found"%self.getShortName()    

        d_prematchAttrs = self.dynPrematchAttrs or {}
        for k in d_prematchAttrs.keys():
            if i_dynObject.hasAttr(k):i_dynObject.__setattr__(k,d_prematchAttrs[k])
            else:
                log.warning("%s.setPrematchData>> dynObject lacks attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName,k))
                d_prematchAttrs.pop(k)
        return True

    #======================================================================		
    #>>> Iter match stuff
    #======================================================================
    def getIterDrivenList(self):
        log.debug(">>> %s.getIterDrivenList() >> "%(self.p_nameShort) + "-"*75)  	
        l_iterDriven = []
        ml_iterDriven = []
        for i in range(75):
            buffer = self.getMessage('iterDriven_%s'%i,False)
            if buffer:
                l_iterDriven.extend(buffer)
                ml_iterDriven.extend(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
            else:break
        log.debug("%s.getIterDrivenList>>> Iter driven -- cnt: %s | lists: %s"%(self.getShortName(),len(l_iterDriven),l_iterDriven)) 	
        return ml_iterDriven

    def getIterMatchList(self):
        log.debug(">>> %s.getIterMatchList() >> "%(self.p_nameShort) + "-"*75)  		
        l_iterMatch = []
        ml_iterMatch = []
        for i in range(75):
            buffer = self.getMessage('iterMatch_%s'%i,False)
            if buffer:
                l_iterMatch.extend(buffer)
                ml_iterMatch.extend(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
            else:break
        log.debug("%s.getIterMatchList>>> Iter Match -- cnt: %s | lists: %s"%(self.getShortName(),len(l_iterMatch),l_iterMatch)) 	
        return ml_iterMatch

    def addDynIterTarget(self, drivenObject = None, matchObject = None, matchTarget = None, driverAttr = None, drivenAttr = None, matchAttr = None,
                         maxValue = None, minValue = None, maxIter = 50, iterIndex = None):
        """
        dynIterTargetSetup

        @kws
        drivenObject(str/inst) -- the object that is moved by the driverAttr
        matchObject(str/inst) -- the object the driven object should match, if None, matchTarget is required which will make one
        matchTarget(str/inst) -- the object under which the matchObject is parented
        drivenAttr(str) -- attribute that is driven (must exist on driven object)
        matchAttr(str) -- attribute that needs to match drivenAttr (must exist on match object)
        driverAttr(str) -- the attribute which will be iterated
        maxValue(float) -- max in value for iteration
        minValue(float) -- min in value for the iteration
        maxIter(int) -- maximum iterations to find a good value
        iterIndex(int) -- not implemented

        """
        log.debug(">>> %s.addDynIterTarget() >> "%(self.p_nameShort) + "-"*75)  			
        #>>> Validate
        i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
        if not i_dynObject:raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Must have dynObject. None found"	    
        if not i_dynObject.hasAttr(driverAttr): raise StandardError, "cgmDynamicMatch.addDynIterTarget>> dynObject lacks attr: %s.%s "%(i_dynObject.getShortName,driverAttr)

        mPlug_driverAttr = cgmMeta.cgmAttr(i_dynObject,driverAttr)
        i_drivenObject = cgmMeta.validateObjArg(drivenObject,cgmMeta.cgmObject,noneValid=True)
        i_matchObject = cgmMeta.validateObjArg(matchObject,cgmMeta.cgmObject,noneValid=True)
        i_matchTarget = cgmMeta.validateObjArg(matchTarget,cgmMeta.cgmObject,noneValid=True)

        if not i_matchObject and i_matchTarget:#see if we need to make a match object
            i_matchObject = i_drivenObject.doDuplicateTransform()
            i_matchObject.parent = i_matchTarget.mNode
            i_matchObject.doStore('cgmName',"%s_toMatch_%s"%(i_drivenObject.getNameAlias(),i_matchTarget.getNameAlias())) 
            i_matchObject.addAttr('cgmType','dynIterMatchObject')
            i_matchObject.addAttr('mClass','cgmObject')	
            i_matchObject.doName()	    
            log.debug("%s.addDynIterTarget>> match object created: %s"%(self.getShortName(),i_matchObject.getShortName()))
        elif not i_matchObject:
            raise StandardError, "%s.addDynIterTarget>> if no match object is provided, a match target is necessary"%self.getShortName()


        #Get our iter driven stuff
        ml_iterDriven = self.getIterDrivenList()#Get the list

        #if i_dynObject == i_drivenObject:
            #raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Cannot add self as target"
        log.debug(">>>>>>>>>>>>> Start add %s"%[iobj.mNode for iobj in ml_iterDriven])
        log.debug("cgmDynamicMatch.addDynIterTarget>> driven obj: %s"%i_drivenObject)

        if i_drivenObject in ml_iterDriven:
            log.debug("cgmDynamicMatch.addDynIterTarget>> Object already connected: %s"%i_drivenObject.getShortName())
            index_iterDriven = ml_iterDriven.index(i_drivenObject)
        else:#add it
            index = self.msgList_append(i_drivenObject,'iterDriven')	    
            ml_iterDriven.append(i_drivenObject)
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
        log.debug("cgmDynamicMatch.addDynIterTarget>> match obj: %s"%i_matchObject)
        log.debug(">>>>>>>>>>>>> Start add %s"%[iobj.mNode for iobj in ml_iterMatch])
        if i_matchObject in ml_iterMatch:
            log.debug("cgmDynamicMatch.addDynIterTarget>> Object already connected: %s"%i_matchObject.getShortName())
            index_iterMatch = ml_iterMatch.index(i_matchObject)

        else:#add it
            index = self.msgList_append(i_matchObject,'iterMatch')
            ml_iterMatch.append(i_matchObject)
            index_iterMatch = ml_iterMatch.index(i_matchObject)
            if index != index_iterMatch:
                raise StandardError, "cgmDynamicMatch.addDynIterTarget>> Iter match indexes do not match!"	    
        #======================================================================		
        #>>Get our Attribute registered
        d_iterSettings = self.dynIterSettings or {}
        l_iterAttrsBuffer = self.dynIterAttrs or []
        if mPlug_driverAttr.attr in l_iterAttrsBuffer:
            log.debug("cgmDynamicMatch.addDynIterTarget>> Attr already in, checking: '%s'"%mPlug_driverAttr.p_combinedShortName)	    
        else:
            l_iterAttrsBuffer.append(mPlug_driverAttr.attr)
        index_IterAttr = l_iterAttrsBuffer.index(mPlug_driverAttr.attr)	
        self.dynIterAttrs = l_iterAttrsBuffer#Push back to attr

        #>>> Build our dict
        d_buffer = {}
        l_keyValues = [minValue,maxValue,maxIter,matchAttr,drivenAttr]
        l_keyNames = ['minValue','maxValue','maxIter','matchAttr','drivenAttr']
        for i,key in enumerate(l_keyNames):
            if l_keyValues[i] is not None and type(l_keyValues[i]) in [float,int]:
                d_buffer[key] = l_keyValues[i]
            elif i == 3 and l_keyValues[i] is not None and i_matchObject.hasAttr(l_keyValues[i]):
                d_buffer['matchAttr'] = l_keyValues[i]
            elif i == 4 and l_keyValues[i] is not None and i_drivenObject.hasAttr(l_keyValues[i]):
                d_buffer['drivenAttr'] = l_keyValues[i]
            elif l_keyValues[i] is not None:
                log.error("cgmDynamicMatch.addDynIterTarget>> Bad value for '%s': %s"%(key,l_keyValues[i]))	    		
        d_buffer['driven'] = index_iterDriven
        d_buffer['match'] = index_iterMatch

        #Store it
        d_iterSettings[mPlug_driverAttr.attr] = d_buffer
        self.dynIterSettings = d_iterSettings
        #======================================================================

    #@cgmGeneral.Timer
    def doIter(self):
        """
        """
        try:
            log.debug(">>> %s.doIter() >> "%(self.p_nameShort) + "-"*75)  				    
            #>>>Gather info
            i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
            if not i_dynObject:raise StandardError, "cgmDynamicMatch.doIter>> Must have dynObject. None found"	    

            ml_iterDriven = self.getIterDrivenList()#Get the list
            ml_iterMatch = self.getIterMatchList()#Get the list

            l_attrBuffer = self.dynIterAttrs or []#Check attrs
            if not l_attrBuffer:
                log.debug("%s.doIter>> Must have iter attrs. None found"%self.getShortName())
                return False

            self.setPrematchData()#set our prematches for proper matching

            for a in l_attrBuffer:
                if not i_dynObject.hasAttr(a):raise StandardError, "cgmDynamicMatch.doIter>> Missing iter attr: %s.%s "%(i_dynObject.getShortName(),a)#has attr    
                if not self.dynIterSettings.get(a):raise StandardError, "cgmDynamicMatch.doIter>> Missing iter setting for attr: %s.%s "%(i_dynObject.getShortName(),a)#has setting	    
                if 'driven' not in self.dynIterSettings[a].keys():raise StandardError, "%s.doIter>> Missing driven setting for attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName(),a)#has setting	    
                if 'match' not in self.dynIterSettings[a].keys():raise StandardError, "%s.doIter>> Missing match setting for attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName(),a)#has setting	    

                if len(ml_iterDriven)< self.dynIterSettings[a]['driven']:raise StandardError, "%s.doIter>> Missing att's driven: attr: %s | index: %s "%(self.getShortName(),a,self.dynIterSettings[a]['driven'])#has setting	    
                if len(ml_iterMatch)< self.dynIterSettings[a]['match']:raise StandardError, "%s.doIter>> Missing att's match: attr: %s | index: %s "%(self.getShortName(),a,self.dynIterSettings[a]['match'])#has setting	    

            log.debug("%s.doIter>> Looks good to go to iter"%(self.getShortName()))

            #per iter attr, go
            for a in l_attrBuffer:
                mPlug_driverAttr = cgmMeta.cgmAttr(i_dynObject,a)
                log.debug("%s.doIter>> iterating setup on : '%s.%s'"%(self.getShortName(),i_dynObject.getShortName(),a))
                i_drivenObject = ml_iterDriven[self.dynIterSettings[a]['driven']]
                i_matchObject = ml_iterMatch[self.dynIterSettings[a]['match']]
                log.debug("%s.doIter>> driven: '%s'"%(self.getShortName(),i_drivenObject.getShortName()))
                log.debug("%s.doIter>> match: '%s'"%(self.getShortName(),i_matchObject.getShortName()))	
                minValue = self.dynIterSettings[a].get('minValue') or 0
                maxValue = self.dynIterSettings[a].get('maxValue') or 359
                log.debug("%s.doIter>> minValue: '%s'"%(self.getShortName(),minValue))
                log.debug("%s.doIter>> maxValue: '%s'"%(self.getShortName(),maxValue))			
                maxIter = self.dynIterSettings[a].get('maxIter') or 50

                if self.dynIterSettings[a].get('matchAttr') and self.dynIterSettings[a].get('drivenAttr'):
                    log.debug("%s.doIter>> iter attr match mode"%(self.getShortName()))
                    matchValue = i_matchObject.getAttr( self.dynIterSettings[a].get('matchAttr') )
                    mPlug_drivenAttr = cgmMeta.cgmAttr(i_drivenObject,self.dynIterSettings[a].get('drivenAttr'))
                    log.debug("%s.doIter>> value: %s"%(self.getShortName(),matchValue))
                    log.debug("%s.doIter>> drivenAttr: %s"%(self.getShortName(),mPlug_drivenAttr.p_combinedShortName))
                    log.debug("%s.doIter>>"%(self.getShortName()) + "="*60)

                    rUtils.matchValue_iterator(driverAttr= mPlug_driverAttr.p_combinedName,
                                               drivenAttr = mPlug_drivenAttr.p_combinedName, 
                                               matchValue = matchValue,
                                               minIn=minValue,maxIn=maxValue,
                                               maxIterations=maxIter)

                else:
                    rUtils.matchValue_iterator(i_matchObject,drivenObj=i_drivenObject,driverAttr=mPlug_driverAttr.p_combinedName,minIn=minValue,maxIn=maxValue,maxIterations=maxIter)
        except Exception,error:
            log.error("%s.doIter>> Failure!"%(self.getShortName()))
            raise Exception,error

    #======================================================================		
    #>>> Attr match stuff    
    def getAttrMatchList(self,maxCheck = 75):
        log.debug(">>> %s.getAttrMatchList() >> "%(self.p_nameShort) + "-"*75)  				    	
        l_matchAttr = []
        ml_matchAttr = []
        for i in range(maxCheck):
            buffer = self.getMessage('dynMatchAttr_%s'%i,False)
            if i == maxCheck-1 or not buffer:
                break
            else:
                d_attrReturn = cgmMeta.validateAttrArg(buffer,noneValid=True)
                if not d_attrReturn:
                    log.error("%s.getAttrMatchList>> Invalid attr arg: '%s'"%(self.getShortName(),buffer))
                    break
                mPlug_matchAttr = d_attrReturn['mi_plug']		
                l_matchAttr.append(mPlug_matchAttr.p_combinedName)
                ml_matchAttr.append(mPlug_matchAttr)
        log.debug("%s.getAttrMatchList>>> match attrs -- cnt: %s | lists: %s"%(self.getShortName(),len(l_matchAttr),l_matchAttr)) 	
        return l_matchAttr

    def addDynAttrMatchTarget(self, dynObjectAttr = None, matchAttrArg = None):
        """
        Dyn Attr match setup

        @kws
        dynObjectAttr(str) -- attribute that set (must exist on i_dynObject)
        matchAttrArg(arg) -- attr arg (cgmMeta.validateAttrArg())
        """
        log.debug(">>> %s.addDynAttrMatchTarget() >> "%(self.p_nameShort) + "-"*75)  				    		
        #>>> Validate
        i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
        if not i_dynObject:raise StandardError, "cgmDynamicMatch.addDynAttrMatchTarget>> Must have dynObject. None found"	    
        if not i_dynObject.hasAttr(dynObjectAttr): raise StandardError, "%s.addDynAttrMatchTarget>> dynObject lacks attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName,dynObjectAttr)

        mPlug_dynObj = cgmMeta.cgmAttr(i_dynObject,dynObjectAttr)

        #Attr arg
        d_matchAttrArgReturn = cgmMeta.validateAttrArg(matchAttrArg,noneValid=True)
        if not d_matchAttrArgReturn:
            raise StandardError, "%s.addDynAttrMatchTarget>> Invalid matchAttrArg arg: '%s'"%(self.getShortName(),matchAttrArg)	
        mPlug_matchAttr = d_matchAttrArgReturn['mi_plug']

        #======================================================================
        #Match attr
        l_matchAttrs = self.getAttrMatchList()

        if mPlug_matchAttr.p_combinedName in l_matchAttrs:
            log.debug("%s.addDynAttrMatchTarget>> match already connected: %s"%(self.getShortName(),mPlug_matchAttr.p_combinedShortName))
            index_matchAttr = l_matchAttrs.index(mPlug_matchAttr.p_combinedName)

        else:#add it
            index =  self.returnNextAvailableAttrCnt("dynMatchAttr_")
            log.debug("%s.addDynAttrMatchTarget>> Attr to register: '%s'"%(self.getShortName(),mPlug_matchAttr.p_combinedShortName))
            self.doStore('dynMatchAttr_%s'%index,mPlug_matchAttr.p_combinedName)	
            l_matchAttrs.append(mPlug_matchAttr.p_combinedName)

            index_matchAttr = l_matchAttrs.index(mPlug_matchAttr.p_combinedName)
            if index != index_matchAttr:
                raise StandardError, "%s.addDynAttrMatchTarget>> match attr indexes do not match!"%self.getShortName()  	

        #======================================================================		
        #>>Get our Attribute registered
        d_dynMatchAttrSettings = self.d_dynMatchAttrSettings or {}
        l_dynMatchAttrs = self.l_dynMatchAttrs or []
        if mPlug_dynObj.attr in l_dynMatchAttrs:
            log.debug("%s.addDynAttrMatchTarget>> Attr already in, checking: '%s'"%(self.getShortName(),mPlug_dynObj.p_combinedShortName))
        else:
            l_dynMatchAttrs.append(mPlug_dynObj.attr)
        index_selfAttr = l_dynMatchAttrs.index(mPlug_dynObj.attr)	
        self.l_dynMatchAttrs = l_dynMatchAttrs#Push back to attr

        #>>> Build our dict
        #d_buffer = {}   		
        #d_buffer['mtchIdx'] = index_matchAttr

        #Store it
        d_dynMatchAttrSettings[mPlug_dynObj.attr] = index_matchAttr
        self.d_dynMatchAttrSettings = d_dynMatchAttrSettings
        #======================================================================

    #@cgmGeneral.Timer
    def isAttrMatch(self):
        """
        See if our attrs match like they should
        """
        log.debug(">>> %s.isAttrMatch() >> "%(self.p_nameShort) + "-"*75)  				    			
        try:
            #>>>Gather info
            i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
            if not i_dynObject:raise StandardError, "cgmDynamicMatch.doAttrMatch>> Must have dynObject. None found"	    

            ml_attrMatchObj = self.getAttrMatchList()#Get the list

            l_dynMatchAttrs = self.l_dynMatchAttrs or []#Check attrs
            if not l_dynMatchAttrs:
                log.debug("%s.doAttrMatch>> Must have match attrs. None found"%self.getShortName())
                return False

            for a in l_dynMatchAttrs:
                if not i_dynObject.hasAttr(a):raise StandardError, "cgmDynamicMatch.doAttrMatch>> Missing iter attr: %s.%s "%(i_dynObject.getShortName(),a)#has attr    
                if self.d_dynMatchAttrSettings.get(a) is None:raise StandardError, "cgmDynamicMatch.doAttrMatch>> Missing attrMatch setting for attr: %s.%s "%(i_dynObject.getShortName(),a)#has setting	    
                #if 'objIdx' not in self.d_dynMatchAttrSettings[a].keys():raise StandardError, "%s.doAttrMatch>> Missing driven setting for attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName(),a)#has setting	    
                #if 'mtchAtr' not in self.d_dynMatchAttrSettings[a].keys():raise StandardError, "%s.doAttrMatch>> Missing match setting for attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName(),a)#has setting	    

            log.debug("%s.doAttrMatch>> Looks good to go to match"%(self.getShortName()))

            #per iter attr, go
            for a in l_dynMatchAttrs:
                #>>> Attr2
                index_matchAttr = self.d_dynMatchAttrSettings.get(a)
                log.debug("%s.doAttrMatch>> index_matchAttr: %s"%(self.getShortName(),index_matchAttr))
                str_attr = self.getMessage('dynMatchAttr_%s'%index_matchAttr,False)
                d_matchAttrReturn = cgmMeta.validateAttrArg(str_attr,noneValid=True)
                if not d_matchAttrReturn:
                    log.error("%s.doAttrMatch>> Invalid matchAttr arg found: '%s'"%(self.getShortName(),str_attr))
                    return False
                mPlug_matchAttr = d_matchAttrReturn['mi_plug']

                log.debug("%s.go>> alias: '%s'"%(self.getShortName(),str_attr))
                log.debug("%s.go>> match attr: '%s'"%(self.getShortName(),mPlug_matchAttr.p_combinedShortName))	

                mPlug_dynObjAttr = cgmMeta.cgmAttr(i_dynObject,a)

                try:
                    if mPlug_dynObjAttr.value != mPlug_matchAttr.value:
                        return False
                except Exception,error:
                    log.error("%s.go>> failed to set value! | %s"%(self.getShortName(),error))
                    return False

                log.debug("%s.doAttrMatch>> set value: %s"%(self.getShortName(),mPlug_dynObjAttr.value))		
            return True

        except Exception,error:
            log.error("%s.doAttrMatch>> Failure!"%(self.getShortName()))
            raise Exception,error

    #@cgmGeneral.Timer
    def doAttrMatch(self):
        """
        """
        log.debug(">>> %s.doAttrMatch() >> "%(self.p_nameShort) + "-"*75)  				    				
        try:
            #>>>Gather info
            i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
            if not i_dynObject:raise StandardError, "cgmDynamicMatch.doAttrMatch>> Must have dynObject. None found"	    

            ml_attrMatchObj = self.getAttrMatchList()#Get the list

            l_dynMatchAttrs = self.l_dynMatchAttrs or []#Check attrs
            if not l_dynMatchAttrs:
                log.debug("%s.doAttrMatch>> Must have match attrs. None found"%self.getShortName())
                return False

            for a in l_dynMatchAttrs:
                if not i_dynObject.hasAttr(a):raise StandardError, "cgmDynamicMatch.doAttrMatch>> Missing iter attr: %s.%s "%(i_dynObject.getShortName(),a)#has attr    
                if self.d_dynMatchAttrSettings.get(a) is None:raise StandardError, "cgmDynamicMatch.doAttrMatch>> Missing attrMatch setting for attr: %s.%s "%(i_dynObject.getShortName(),a)#has setting	    
                #if 'objIdx' not in self.d_dynMatchAttrSettings[a].keys():raise StandardError, "%s.doAttrMatch>> Missing driven setting for attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName(),a)#has setting	    
                #if 'mtchAtr' not in self.d_dynMatchAttrSettings[a].keys():raise StandardError, "%s.doAttrMatch>> Missing match setting for attr: %s.%s "%(self.getShortName(),i_dynObject.getShortName(),a)#has setting	    

            log.debug("%s.doAttrMatch>> Looks good to go to match"%(self.getShortName()))

            #per iter attr, go
            for a in l_dynMatchAttrs:
                #>>> Attr2
                index_matchAttr = self.d_dynMatchAttrSettings.get(a)
                log.debug("%s.doAttrMatch>> index_matchAttr: %s"%(self.getShortName(),index_matchAttr))
                str_attr = self.getMessage('dynMatchAttr_%s'%index_matchAttr,False)
                d_matchAttrReturn = cgmMeta.validateAttrArg(str_attr,noneValid=True)
                if not d_matchAttrReturn:
                    log.error("%s.doAttrMatch>> Invalid matchAttr arg found: '%s'"%(self.getShortName(),str_attr))
                    return False
                mPlug_matchAttr = d_matchAttrReturn['mi_plug']

                log.debug("%s.go>> alias: '%s'"%(self.getShortName(),str_attr))
                log.debug("%s.go>> match attr: '%s'"%(self.getShortName(),mPlug_matchAttr.p_combinedShortName))	

                mPlug_dynObjAttr = cgmMeta.cgmAttr(i_dynObject,a)

                try:
                    mPlug_dynObjAttr.value = mPlug_matchAttr.value
                except Exception,error:
                    log.error("%s.go>> failed to set value! | %s"%(self.getShortName(),error))
                    return False

                log.debug("%s.doAttrMatch>> set value: %s"%(self.getShortName(),mPlug_dynObjAttr.value))		


        except Exception,error:
            log.error("%s.doAttrMatch>> Failure!"%(self.getShortName()))
            raise Exception,error
    #==============================================================================
    def addDynSnapTarget(self,arg = None, alias = None):
        """

        """
        log.debug(">>> %s.addDynSnapTarget() >> "%(self.p_nameShort) + "-"*75)  				    					
        #>>> Validate
        i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
        if not i_dynObject:raise StandardError, "cgmDynamicMatch.addDynSnapTarget>> Must have dynObject. None found"	    

        i_dSnapTarget = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
        if not i_dSnapTarget:
            i_dSnapTarget = i_dynObject.doLoc()
            log.debug("cgmDynamicMatch.addDynSnapTarget>> Added snap loc: %s"%i_dSnapTarget.getShortName())
        if self == i_dSnapTarget:
            raise StandardError, "cgmDynamicMatch.addDynSnapTarget>> Cannot add self as target"
        if not i_dSnapTarget.isTransform():
            raise StandardError, "cgmDynamicMatch.addDynSnapTarget>> SnapTarget has no transform: '%s'"%i_dSnapTarget.getShortName()
        if i_dSnapTarget.rotateOrder != i_dynObject.rotateOrder:
            raise StandardError, "cgmDynamicMatch.addDynSnapTarget>> Rotate Order of target doesn't match dynChild: child: '%s' | snapTarget: '%s"%(i_dynObject.getShortName(),i_dSnapTarget.getShortName())	    

        ml_dynSnapTargets = [cgmMeta.cgmObject(o) for o in self.msgList_getMessage('dynSnapTargets')]

        log.debug(">>>>>>>>>>>>> Start add %s"%self.msgList_getMessage('dynSnapTargets',False))
        if i_dSnapTarget in ml_dynSnapTargets:
            log.debug("cgmDynamicMatch.addDynSnapTarget>> Object already connected: %s"%i_dSnapTarget.getShortName())
            return True

        #>>> Connect it
        log.debug("cgmDynamicMatch.addDynSnapTarget>> Adding target: '%s'"%i_dSnapTarget.getShortName())	
        self.msgList_append(i_dynSnapTarget,'dynSnapTargets')#Connect the nodes

        if alias is not None:
            i_dynSnapTarget.addAttr('cgmAlias', str(alias),lock = True)

        log.debug(">>>>>>>>>>>>> after add %s"%self.msgList_getMessage('dynSnapTargets',False))

    def addDynMatchTarget(self,arg, alias = None, l_matchAttrs = None):
        """

        """
        try:
            log.debug(">>> %s.addDynMatchTarget() >> "%(self.p_nameShort) + "-"*75)  				    						
            #>>> Validate
            i_dMatchTarget = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
            if not i_dMatchTarget:raise StandardError, "cgmDynamicMatch.addDynMatchTarget>> Failed to cgmMeta.validate: %s"%arg	    
            if self == i_dMatchTarget:
                raise StandardError, "cgmDynamicMatch.addDynMatchTarget>> Cannot add self as target"
            if not i_dMatchTarget.isTransform():
                raise StandardError, "cgmDynamicMatch.addDynMatchTarget>> MatchTarget has no transform: '%s'"%i_dMatchTarget.getShortName()
            log.debug("cgmDynamicMatch.addDynMatchTarget>> '%s'"%i_dMatchTarget.getShortName())

            ml_dynMatchTargets = [cgmMeta.cgmObject(o) for o in self.msgList_get('dynMatchTargets',asMeta=False)]
            log.debug(">>>>>>>>>>>>> Start add %s"%self.msgList_get('dynMatchTargets',False))

            if i_dMatchTarget in ml_dynMatchTargets:
                log.debug("cgmDynamicMatch.addDynMatchTarget>> Object already connected: %s"%i_dMatchTarget.getShortName())
                self.verifyMatchTargetDriver(i_dMatchTarget,l_matchAttrs)	    
                return True

            if alias is not None:
                i_dynMatchTarget.addAttr('cgmAlias', str(alias),lock = True)

            #>>> Connect it
            log.debug("cgmDynamicMatch.addDynMatchTarget>> Adding target: '%s'"%i_dMatchTarget.getShortName())
            ml_dynMatchTargets.append(i_dMatchTarget)	
            self.msgList_connect(ml_dynMatchTargets,'dynMatchTargets')#Connect the nodes
            log.debug(">>>>>>>>>>>>> after add %s"%self.msgList_get('dynMatchTargets',False))

            #Verify our driver for the target
            self.verifyMatchTargetDriver(i_dMatchTarget,l_matchAttrs)
        except Exception,error:raise Exception,"addDynMatchTarget fail! | {0}".format(error)

    def verifyMatchTargetDriver(self,arg,l_matchAttrs = None):
        """
        1) if arg is a dynMatchTarget
        2) check it's driver
        3) Make if necesary
        """	
        log.debug(">>> %s.verifyMatchTargetDriver() >> "%(self.p_nameShort) + "-"*75)  				    							
        i_dynObject = cgmMeta.validateObjArg(self.getMessage('dynObject')[0],cgmMeta.cgmObject,noneValid=True) 
        if not i_dynObject:raise StandardError, "cgmDynamicMatch.verifyMatchTargetDriver>> Must have dynObject. None found"	    
        i_dMatchTarget = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
        if not i_dMatchTarget:
            raise StandardError, "cgmDynamicMatch.verifyMatchTargetDriver>> arg fail: %s"%arg
        l_dynMatchTargets = self.msgList_getMessage('dynMatchTargets',True)
        log.debug(l_dynMatchTargets)
        if i_dMatchTarget.getLongName() not in l_dynMatchTargets:
            raise StandardError, "cgmDynamicMatch.verifyMatchTargetDriver>> not a dynMatchTarget: %s"%i_dMatchTarget.getShortName()

        index = l_dynMatchTargets.index(i_dMatchTarget.getLongName())
        log.debug("cgmDynamicMatch.verifyMatchTargetDriver>> dynMatchTargets index: %s"%index)
        ml_dynDrivers = self.msgList_get('dynDrivers',asMeta=True)
        l_dynDrivers = [obj.p_nameLong for obj in ml_dynDrivers]

        #See if we have a good driver
        foundMatch = False
        if l_dynDrivers and len(l_dynDrivers) > index:
            buffer = l_dynDrivers[index]
            log.debug("buffer: %s"%cgmMeta.cgmObject( buffer ).getMessage('dynMatchTarget',True))
            log.debug("object: %s"%i_dynObject.getLongName())
            if cgmMeta.cgmObject( buffer ).getMessage('dynMatchTarget',True) == [i_dynObject.getLongName()]:
                log.debug("dynDriver: found")
                i_driver = cgmMeta.validateObjArg(l_dynDrivers[index],cgmMeta.cgmObject,noneValid=False)
                foundMatch = True
        if not foundMatch:
            log.debug("dynDriver: creating")	
            i_driver = i_dynObject.doDuplicateTransform()
            l_dynDrivers.insert(index,i_driver.mNode)
            self.msgList_connect(l_dynDrivers,'dynDrivers','dynMaster')

        i_driver.parent = i_dMatchTarget.mNode
        i_driver.doStore('cgmName',"%s_toMatch_%s"%(i_dMatchTarget.getNameAlias(),i_dynObject.getNameAlias())) 
        i_driver.addAttr('cgmType','dynDriver')
        i_driver.addAttr('mClass','cgmObject')	
        i_driver.addAttr('dynMatchAttrs',attrType='string',lock=True)	
        i_driver.doName()

        i_driver.rotateOrder = i_dynObject.rotateOrder#Match rotate order
        log.debug("dynDriver: '%s' >> '%s'"%(i_dMatchTarget.getShortName(),i_driver.getShortName()))

        #self.connectChildNode(i_driver,'dynDriver_%s'%index,'dynMaster')	
        i_driver.connectChildNode(i_dynObject,'dynMatchTarget')

        #>>> Match attr setting
        if l_matchAttrs is None and not i_driver.getAttr('dynMatchAttrs'):
            #Only preload this if we have no arg and none are set
            log.debug("Preloading attrs....")
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
        log.debug(">>> %s.doMatch() >> "%(self.p_nameShort) + "-"*75)  				    								
        #>>>Initial info
        i_object = self.getMessageAsMeta('dynObject')
        log.debug("cgmDynamicMatch.doMatch>> Object : %s"%i_object.getShortName())
        l_dynMatchTargets = self.msgList_getMessage('dynMatchTargets')
        l_dynDrivers= self.msgList_getMessage('dynDrivers')

        #>>>Figure out our match object
        index = False
        if match is not None and type(match) is int:
            if match > len(l_dynMatchTargets)-1:
                raise StandardError,"cgmDynamicMatch.doMatch>> Match Index(%s) greater than targets: %s"%(match,self.msgList_getMessage('dynMatchTargets',False))
            if match > len(l_dynDrivers)-1:
                raise StandardError,"cgmDynamicMatch.doMatch>> Match Index(%s) greater than drivers: %s"%(match,self.msgList_getMessage('dynDrivers',False))	
            index = match		    
        elif len(l_dynMatchTargets)>0:#use the first
            index = 0		    
        else:
            raise StandardError,"cgmDynamicMatch.doMatch>> No valid arg:  match: %s"%(match)	

        i_driver = cgmMeta.validateObjArg(l_dynDrivers[index],cgmMeta.cgmObject,noneValid = False)
        i_target = cgmMeta.validateObjArg(l_dynMatchTargets[index],cgmMeta.cgmObject,cgmMeta.cgmObject,noneValid = False)	
        log.debug("cgmDynamicMatch.doMatch>> Driver on : %s"%i_driver.getShortName())

        #>>>Prematch attr set
        if i_driver.getAttr('dynMatchAttrs'):#if we have something
            for attr in i_driver.dynMatchAttrs:
                if attr.lower() in ['translate','t']:
                    objTrans = mc.xform (i_driver.mNode, q=True, ws=True, rp=True)#Get trans		    
                    log.debug("cgmDynamicMatch.doMatch>> match translate! %s"%objTrans)		    
                    mc.move (objTrans[0],objTrans[1],objTrans[2], [i_object.mNode])#Set trans
                if attr.lower() in ['rotate','r']:
                    objRot = mc.xform (i_driver.mNode, q=True, ws=True, ro=True)#Get rot
                    log.debug("cgmDynamicMatch.doMatch>> match rotate! %s"%objRot)		    
                    mc.rotate (objRot[0], objRot[1], objRot[2], [i_object.mNode], ws=True)#Set rot	
                if attr.lower() in ['scale']:
                    objScale = [v for v in mc.getAttr ("%s.scale"%i_target.mNode)[0]]#Get rot
                    log.debug("cgmDynamicMatch.doMatch>> match scale! %s"%objScale)		    		    
                    mc.scale (objScale[0], objScale[1], objScale[2], [i_object.mNode], os=True)#Set rot	
        else:
            raise NotImplementedError,"cgmDynamicMatch.doMatch>> no attrs found: %s"%i_driver.getAttr('dynMatchAttrs')

    def doSnap(self,snap = None, snapMode = ['point','orient']):
        """
        @kws
        snap -- index of snap object
        """
        log.debug(">>> %s.doSnap() >> "%(self.p_nameShort) + "-"*75)  				    									
        #>>>Initial info
        i_object = self.getMessageAsMeta('dynObject')
        l_dynDrivers= self.msgList_getMessage('dynSnapTargets')

        #>>>Figure out our match object
        index = False
        if snap is not None and type(snap) is int:
            if snap > len(l_dynDrivers):
                raise StandardError,"cgmDynamicMatch.doSnap>> Snap Index(%s) greater than targets: %s"%(snap,l_dynDrivers)	
            index = snap	
            i_driver = cgmMeta.validateObjArg(l_dynDrivers[index],cgmMeta.cgmObject)
        else:
            raise StandardError,"cgmDynamicMatch.doSnap>> No valid arg: snap: %s | snapMode: %s"%(snap,snapMode)	


        log.debug("cgmDynamicMatch.doSnap>> Driver on : %s"%i_driver.getShortName())

        #>>>Prematch attr set
        for attr in snapMode:
            if attr.lower() in ['move','point','parent','translate']:
                objTrans = mc.xform (i_driver.mNode, q=True, ws=True, rp=True)#Get trans		    
                log.debug("cgmDynamicMatch.doSnap>> match translate! %s"%objTrans)		    
                mc.move (objTrans[0],objTrans[1],objTrans[2], [i_object.mNode])#Set trans
            if attr.lower() in ['orient','parent','rotate']:
                objRot = mc.xform (i_driver.mNode, q=True, ws=True, ro=True)#Get rot
                log.debug("cgmDynamicMatch.doSnap>> match rotate! %s"%objRot)		    
                mc.rotate (objRot[0], objRot[1], objRot[2], [i_object.mNode], ws=True)#Set rot			

    def doPurge(self):
        log.debug(">>> %s.doPurge() >> "%(self.p_nameShort) + "-"*75)  				    										
        if self.isReferenced():
            log.warning('This function is not designed for referenced nodes')
            return False

        l_dynDrivers = self.msgList_get('dynDrivers',asMeta=False) or []
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
                 dynMode = None,*args,**kws):
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
	#>>> TO USE Cached instance ---------------------------------------------------------
	if self.cached:
	    log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
	    return
	#====================================================================================
	
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

        log.debug("cgmDynParentGroup.__init__>> dynParents: %s"%self.msgList_getMessage('dynParents',False))
        for p in arg_ml_dynParents:
            log.debug("Adding dynParent: %s"%p.mNode)
            self.addDynParent(p)

        if dynMode is not None:
            try:
                self.dynMode = dynMode
            except Exception,error:
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
        log.debug(">>> %s.__verify__() >> "%(self.p_nameShort) + "="*75) 
        try:
            #Check our attrs
            if self._mi_dynChild:
                self.addDynChild(self._mi_dynChild)
                #self.doStore('cgmName',self._mi_dynChild.mNode)
            self.addAttr('mClass','cgmDynParentGroup',lock=True)#We're gonna set the class because it's necessary for this to work
            self.addAttr('cgmType','dynParentGroup',lock=True)#We're gonna set the class because it's necessary for this to work

            self.addAttr('dynMode',attrType = 'enum', enumName= 'space:orient:follow', keyable = False, hidden=True)
            self.addAttr('dynChild',attrType = 'messageSimple',lock=True)
            self.addAttr('dynFollow',attrType = 'messageSimple',lock=True)				

            #Unlock all transform attriutes
            for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
                cgmMeta.cgmAttr(self,attr,lock=False)
            self.doName()
            return True
        except Exception,error:
            raise Exception, ">>> %s.__verify__() Fail! >> %s"%(self.p_nameShort,error)


    def rebuild(self,*a,**kw):
        """ Rebuilds the buffer data cleanly """ 
        log.debug(">>> %s.rebuild() >> "%(self.p_nameShort) + "="*75) 		        	
        #Must have at least 2 targets
        l_dynParents = self.msgList_getMessage('dynParents',False)
        if len(l_dynParents)<2:
            log.error("cgmDynParentGroup.rebuild>> Need at least two dynParents. Build failed: '%s'"%self.getShortName())
            return False
        i_child = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,noneValid=False)

        #TODO First scrub nodes and what not
        self._setLocks(False)
	
        #Check our attrs
        d_attrBuffers = {}
        for a in self.l_dynAttrs:
            if i_child.hasAttr(a):#we probably need to index these to the previous settings in case order changes
                d_attrBuffers[a] = attributes.doGetAttr(i_child.mNode,a)
            if a not in d_DynParentGroupModeAttrs[self.dynMode]:
                attributes.doDeleteAttr(i_child.mNode,a)
        if d_attrBuffers:log.debug("d_attrBuffers: %s"%d_attrBuffers)

        l_parentShortNames = [cgmMeta.cgmNode(o).getNameAlias() for o in l_dynParents]
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
        for o in l_dynParents:
            log.debug("verifyParentDriver: %s"%o)
            self.verifyParentDriver(o)

        #i_child.addAttr('space',attrType='enum',enumName = ':'.join(l_parentShortNames),keyable = True, hidden=False)

        #Verify constraints    
        self.verifyConstraints()
        self._setLocks(True)	
        return 'Done'    
        #Check constraint

    def addDynChild(self,arg):
        log.debug(">>> %s.addDynChild(arg = %s) >> "%(self.p_nameShort,arg) + "="*75) 		        		
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
        log.debug(">>> %s.addDynParent(arg = %s, index = %s, alias = %s) >> "%(self.p_nameShort,arg,index,alias) + "="*75) 		        		
        i_dParent = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
        if not i_dParent:
            raise StandardError, "cgmDynParentGroup.addDynParent>> Failed to cgmMeta.validate: %s"%arg	    
        if self == i_dParent:
            raise StandardError, "cgmDynParentGroup.addDynParent>> Cannot add self as target"
        if not i_dParent.isTransform():
            raise StandardError, "cgmDynParentGroup.addDynParent>> Target has no transform: '%s'"%i_dParent.getShortName()
        log.debug("cgmDynParentGroup.addDynParent>> '%s'"%i_dParent.getShortName())
        l_dynParents = self.msgList_getMessage('dynParents')
        ml_dynParents = [cgmMeta.cgmObject(o) for o in l_dynParents]
        log.debug(">>>>>>>>>>>>> Start add %s"%l_dynParents)

        if i_dParent in ml_dynParents:
            log.debug("cgmDynParentGroup.addDynParent>> Child already connected: %s"%i_dParent.getShortName())
            return True

        if alias is not None:
            i_dynParent.addAttr('cgmAlias', str(alias),lock = True)

        log.debug("cgmDynParentGroup.addDynParent>> Adding target: '%s'"%i_dParent.getShortName())
        ml_dynParents.append(i_dParent)	
        self.msgList_append(i_dParent,'dynParents')#Connect the nodes
        log.debug(">>>>>>>>>>>>> after add %s"%self.msgList_getMessage('dynParents'))

    def verifyConstraints(self):
        """
        1) are we constrained
        2) are constraints correct - right type, right targets...it's probably faster just to rebuild...
        3) 
        """
	try:
	    log.debug(">>> %s.verifyConstraints() >> "%(self.p_nameShort) + "="*75) 		        			
	    l_dynParents = self.msgList_getMessage('dynParents')
	    if len(l_dynParents)<2:
		log.error("cgmDynParentGroup.verifyConstraints>> Need at least two dynParents. Build failed: '%s'"%self.getShortName())
		return False
	    if self.dynMode == 2 and not self.getMessage('dynFollow'):
		raise StandardError, "cgmDynParentGroup.verifyConstraints>> must have follow driver for follow mode: '%s'"%self.getShortName()
	    try:#initialize parents
		ml_dynParents = cgmMeta.validateObjListArg(l_dynParents,cgmMeta.cgmObject,False)
		#l_dynDrivers = [i_obj.getMessage('dynDriver')[0] for i_obj in ml_dynParents]
		l_dynDrivers = self.msgList_getMessage('dynDrivers')
		i_dynChild = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,False)	    
	    except Exception,error:
		raise Exception,"cgmDynParentGroup.verifyConstraints>> dynParent/dynChild initialization failed! | %s"%(error)
	    try:#Check current
		currentConstraints = self.getConstraintsTo()
		log.debug("currentConstraints: %s"%currentConstraints)
		if currentConstraints:mc.delete(currentConstraints)#Delete existing constraints
		if self.dynMode == 2:
		    followConstraints = self.dynFollow.getConstraintsTo()
		    log.debug("followConstraints: %s"%followConstraints)		
		    if followConstraints:mc.delete(followConstraints)#Delete existing constraints		
	    except Exception,error:
		raise Exception,"cgmDynParentGroup.verifyConstraints>> Delete constraints fail! | %s"%(error)
    
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
		    i_dynConst = cgmMeta.cgmNode(cBuffer)
		if self.dynMode == 1:#Orient
		    cBuffer = mc.orientConstraint(l_dynDrivers,self.mNode,maintainOffset = True)[0]
		    i_dynConst = cgmMeta.cgmNode(cBuffer)
		if self.dynMode == 2:#Follow - needs an extra follow group
		    pBuffer = mc.pointConstraint(self.dynFollow.mNode,self.mNode,maintainOffset = True)[0]
		    cBuffer = mc.parentConstraint(l_dynDrivers,self.dynFollow.mNode,maintainOffset = True)[0]
		    oBuffer = mc.orientConstraint(l_dynDrivers,self.mNode,maintainOffset = True)[0]
    
		    i_dynFollowConst = cgmMeta.cgmNode(cBuffer)
		    i_dynPointConst = cgmMeta.cgmNode(pBuffer)
		    i_dynConst = cgmMeta.cgmNode(oBuffer)
	    except Exception,error:
		raise Exception,"cgmDynParentGroup.verifyConstraints>> Build constraints fail! | %s"%(error)
	    try:#Name and store    
		for i_const in [i_dynParentConst,i_dynPointConst,i_dynOrientConst]:
		    if i_const:
			i_const.doStore('cgmName',i_dynChild.mNode) 
			i_const.addAttr('cgmTypeModifier','dynDriver')
			#i_const.addAttr('mClass','cgmNode')	
			i_const.doName()
    
		if i_dynParentConst:self.connectChildNode(i_dynParentConst,'dynParentConstraint','dynMaster')
		if i_dynPointConst:self.connectChildNode(i_dynPointConst,'dynPointConstraint','dynMaster')	
		if i_dynOrientConst:self.connectChildNode(i_dynOrientConst,'dynOrientConstraint','dynMaster')	
	    except Exception,error:
		raise Exception,"cgmDynParentGroup.verifyConstraints>> Name and store fail! | %s"%(error)
    
	    #Build nodes
	    try:
		ml_nodes = []
		for i,i_p in enumerate(ml_dynParents):
		    if self.dynMode == 2:#Follow
			i_followCondNode = cgmMeta.cgmNode(nodeType='condition')
			i_followCondNode.operation = 0
			mc.connectAttr("%s.follow"%i_dynChild.mNode,"%s.firstTerm"%i_followCondNode.mNode)
			mc.setAttr("%s.secondTerm"%i_followCondNode.mNode,i)
			mc.setAttr("%s.colorIfTrueR"%i_followCondNode.mNode,1)
			mc.setAttr("%s.colorIfFalseR"%i_followCondNode.mNode,0)
			mc.connectAttr("%s.outColorR"%i_followCondNode.mNode,"%s.w%s"%(i_dynFollowConst.mNode,i))
	
			i_followCondNode.doStore('cgmName',i_p.mNode) 
			i_followCondNode.addAttr('cgmTypeModifier','dynFollow')
			#i_followCondNode.addAttr('mClass','cgmNode')	
			i_followCondNode.doName()
	
			ml_nodes.append(i_followCondNode)
	
		    i_condNode = cgmMeta.cgmNode(nodeType='condition')
		    i_condNode.operation = 0
		    attr = d_DynParentGroupModeAttrs[self.dynMode][0]
		    mc.connectAttr("%s.%s"%(i_dynChild.mNode,attr),"%s.firstTerm"%i_condNode.mNode)
		    mc.setAttr("%s.secondTerm"%i_condNode.mNode,i)
		    mc.setAttr("%s.colorIfTrueR"%i_condNode.mNode,1)
		    mc.setAttr("%s.colorIfFalseR"%i_condNode.mNode,0)
		    mc.connectAttr("%s.outColorR"%i_condNode.mNode,"%s.w%s"%(i_dynConst.mNode,i))
	
		    i_condNode.doStore('cgmName',"%s_to_%s"%(i_dynChild.getShortName(),i_p.getShortName())) 
		    i_condNode.addAttr('cgmTypeModifier','dynParent')
		    #i_condNode.addAttr('mClass','cgmNode')	
		    i_condNode.doName()	 
	    except Exception,error:
		raise Exception,"cgmDynParentGroup.verifyConstraints>> Connection fail! | %s"%(error)
	    self.msgList_connect(ml_nodes,'dynNodes','dynMaster')
    
	    for i_c in ml_children:
		i_c.parent = self.mNode
	except Exception,error:
	    raise Exception,"verifyConstraints | {0}".format(error)
    def verifyParentDriver(self,arg):
        """
        1) if arg is a dynParent
        2) check it's driver
        3) Make if necesary
        """
        log.debug(">>> %s.verifyParentDriver(arg = %s) >> "%(self.p_nameShort,arg) + "="*75) 		        		
        i_dynChild = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,noneValid=True) 
        if not i_dynChild:
            raise StandardError, "cgmDynParentGroup.verifyParentDriver>> Must have dynChild. None found"	    
        i_dParent = cgmMeta.validateObjArg(arg,cgmMeta.cgmObject,noneValid=True)
        if not i_dParent:
            raise StandardError, "cgmDynParentGroup.verifyParentDriver>> arg fail: %s"%arg
	
	index = False
	ml_dynParents = self.msgList_get('dynParents')
	l_dynParents = [obj.mNode for obj in ml_dynParents]
	if i_dParent.mNode in l_dynParents:
	    index = l_dynParents.index(i_dParent.mNode)
        if index is False:
            raise StandardError, "cgmDynParentGroup.verifyParentDriver>> not a dynParent: %s"%i_dParent.getShortName()

        log.debug("cgmDynParentGroup.verifyParentDriver>> dynParents index: %s"%index)
        #dBuffer = self.getMessage('dyDriver_%s'%index)
        ml_dynDrivers = self.msgList_get('dynDrivers',asMeta=True)
        l_dynDrivers = [obj.p_nameLong for obj in ml_dynDrivers]

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
            self.msgList_connect(l_dynDrivers,'dynDrivers','dynMaster')
            #i_driver = i_dParent.doDuplicateTransform()

        i_driver.parent = i_dParent.mNode
        i_driver.doStore('cgmName',"%s_driving_%s"%(i_dParent.getNameAlias(),i_dynChild.getNameAlias())) 
        i_driver.addAttr('cgmType','dynDriver')
        i_driver.addAttr('mClass','cgmObject')	
        i_driver.doName()

        i_driver.rotateOrder = i_dynChild.rotateOrder#Match rotate order
        log.debug("dynDriver: '%s' >> '%s'"%(i_dParent.getShortName(),i_driver.getShortName()))

        #self.connectChildNode(i_driver,'dynDriver_%s'%index,'dynMaster')	
        i_driver.connectChildNode(i_dynChild,'dynTarget')	

    def verifyFollowDriver(self):
        log.debug(">>> %s.verifyFollowDriver() >> "%(self.p_nameShort) + "="*75) 		        			
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
        i_followDriver.addAttr('mClass','cgmObject')		
        i_followDriver.doName()

        i_followDriver.rotateOrder = i_dynChild.rotateOrder#Match rotate order
        log.debug("dynFollow: '%s'"%i_followDriver.getShortName())

        self.connectChildNode(i_followDriver,'dynFollow','dynMaster')
        self._mi_followDriver = i_followDriver

    #@cgmGeneral.Timer
    def doSwitchSpace(self,attr,arg,deleteLoc = True):
        log.debug(">>> %s.doSwitchSpace(attr = %s, arg = %s, deleteLoc = %s) >> "%(self.p_nameShort,attr,arg,deleteLoc) + "="*75) 		        			
        #Swich setting shile holding 
        l_attrs = ['space','follow','orientTo']
        if attr not in l_attrs:
            raise StandardError,"cgmDynParentGroup.doSwitchSpace>> Not a valid attr: %s"%attr	

        i_child = cgmMeta.validateObjArg(self.getMessage('dynChild')[0],cgmMeta.cgmObject,True)
        d_attr = cgmMeta.validateAttrArg([i_child.mNode,attr])
        if not i_child and d_attr:
            raise StandardError,"cgmDynParentGroup.doSwitchSpace>> doSwitchSpace doesn't have enough info. Rebuild recommended"

        #Validate the arg
        if type(arg) is int:
            index = arg
        elif arg in d_attr['mi_plug'].p_enum:
            index = d_attr['mi_plug'].p_enum.index(arg)
        else:
            raise StandardError,"%s.doSwitchSpace>> faile to find index from -- arg: %s | attr: %s"%(self.getShortName(),arg,attr)

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
        log.debug(">>> %s.doPurge() >> "%(self.p_nameShort) + "="*75) 		        			
        if self.isReferenced():
            log.warning('This function is not designed for referenced buffer nodes')
            return False
        nodes = self.msgList_get('dynNodes',asMeta=False)
        if nodes:mc.delete(nodes)
        l_dynParents = self.msgList_getMessage('dynParents')
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
    def _setLocks(self,lock=True):
        _str_funcName = "_setLocks(%s)"%self.p_nameShort  
        log.info(">>> %s >>> "%(_str_funcName) + "="*75) 
        try:
            l_attrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']					
            for a in l_attrs:
                cgmMeta.cgmAttr(self,a,lock=lock)
        except Exception,error:
            raise Exception,"%s >>> Fail | %s"%(_str_funcName,error)	

#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
r9Meta.registerMClassInheritanceMapping()
#r9Meta.registerMClassNodeMapping(nodeTypes = ['network','transform','objectSet'])#What node types to look for