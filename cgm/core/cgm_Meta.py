"""
------------------------------------------
cgm_Meta: cgm.core
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

This is the Core of the MetaNode implementation of the systems.
It is uses Mark Jackson (Red 9)'s as a base.
================================================================
"""
__MAYALOCAL = 'cgmMeta'

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as OM
import maya.OpenMayaAnim as OMANIM 
try:import maya.api.OpenMaya as OM2
except:OM2 = False
    

import copy
import time
import pprint

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import OM_Utils as cgmOM
from cgm.core.lib import nameTools
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.lib import position_utils as POS
from cgm.core.lib import transform_utils as TRANS
import cgm.core.lib.snap_utils as SNAP
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import name_utils as NAMES
#reload(NAMES)
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import constraint_utils as CONSTRAINT
import cgm.core.cgmPy.path_Utils as PATHS
import cgm.core.lib.list_utils as CORELISTS

from cgm.lib.ml import ml_resetChannels
from cgm.lib import lists
from cgm.lib import search
from cgm.lib import attributes
from cgm.core.lib import attribute_utils as ATTR
from cgm.lib import constraints
from cgm.lib import dictionary
from cgm.lib import rigging
from cgm.lib import locators
from cgm.lib import names

"""from cgm.lib import (lists,
                     curves,
                     search,
                     attributes,
                     distance,
                     constraints,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory,
                     position,
                     locators)"""

# Shared Defaults ========================================================
drawingOverrideAttrsDict = {'overrideEnabled':0,
                            'overrideDisplayType':0,
                            'overrideLevelOfDetail':0,
                            'overrideShading':1,
                            'overrideTexturing':1,
                            'overridePlayback':1,
                            'overrideVisibility':1}
l_componentTypes = ['polyVertex','curveCV','surfaceCV','polyEdge','editPoint','isoparm','polyFace','polyUV','curvePoint','surfacePatch','nurbsUV']
l_cgmNameTags = ['cgmName','cgmNameModifier','cgmPosition','cgmDirection','cgmDirectionModifier','cgmIterator','cgmType','cgmTypeModifier']
#KWS ================================================================================================================
_d_KWARG_asMeta = {'kw':'asMeta',"default":True, 'help':"Whether to return as meta or not", "argType":"bool"}
_d_KWARG_attr = {'kw':'attr',"default":None, 'help':"Attribute name to look for", "argType":"string"}
_d_KWARG_value = {'kw':'value',"default":None, 'help':"Value to set", "argType":"variable"}
_d_KWARG_forceNew = {'kw':'forceNew',"default":False, 'help':"typical kw to force a new one of whatever", "argType":"bool"}
_d_KWARG_transformsOnly = {'kw':'transformsOnly',"default":True,'help':"Only reset transforms","argType":"bool"}
_d_KWARG_select = {'kw':'select',"default":False,'help':"Whether to select what has been found","argType":"bool"}
#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================
from cgm.lib.classes import NameFactory as Old_Name#   TMP<<<<<<<<<<<<<<<<<<<<<<<<

#namesDictionaryFile = cgmLIB.settings.getNamesDictionaryFile()
#typesDictionaryFile = cgmLIB.settings.getTypesDictionaryFile()
#settingsDictionaryFile = cgmLIB.settings.getSettingsDictionaryFile()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmMeta - MetaClass factory for figuring out what to do with what's passed to it
#=========================================================================    
class cgmMetaFactory(object):
    def __new__(self, node = None, name = None, nodeType = 'transform',*args,**kws):
        '''
        Idea here is if a MayaNode is passed in and has the mClass attr
        we pass that into the super(__new__) such that an object of that class
        is then instantiated and returned.
        '''	
        doName = None
        objectFlags = ['cgmObject','object','obj','transform']

        if not node and name: 
            node = name
        if not node and nodeType:
            node = True # Yes, make the sucker

        #If the node doesn't exists, make one 
        #==============           
        if node and not mc.objExists(node):#If we have a node and it exists, we'll initialize. Otherwise, we need to figure out what to make
            if nodeType in objectFlags:
                node = mc.createNode('transform')
                #log.debug("Created a transform")
            elif nodeType == 'optionVar':
                return cgmOptionVar(varName=name,*args,**kws)
            elif nodeType != 'network':
                #log.debug("Trying to make a node of this type '%s'"%nodeType)
                node = mc.createNode(nodeType)
            else:
                #log.debug("Make default node")
                node = mc.createNode('network')

        if name and node != name and node != True:
            node = mc.rename(node, name)

        #log.debug("In MetaFactory.__new__ Node is '%s'"%node)
        #log.debug("In MetaFactory.__new__ Name is '%s'"%name) 
        #log.debug("In MetaFactory.__new__ nodeType is '%s'"%nodeType)   

        #Process what to do with it
        #==============             
        mClass = ATTR.get(node,'mClass')
        if mClass:
            log.debug("Appears to be a '%s'"%mClass)
            log.debug("Specialized processing not implemented, initializing as...") 

        objType = VALID.get_mayaType(node)
        if objType == 'objectSet':
            log.debug("'%s' Appears to be an objectSet, initializing as cgmObjectSet"%node)	    
            return cgmObjectSet(node,*args,**kws)
        elif mc.ls(node,type='transform'):
            log.debug("'%s' Appears to be a transform, initializing as cgmObject"%node)
            return cgmObject(name = name, node = node,**kws)          
        else:
            log.debug("Appears to be a '%s'. Initializing as cgmNode"%objType)  
            return cgmNode(name = name, node = node,**kws)    

        return False

class cgmMetaFunc(cgmGEN.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """
        self._str_func= "subFunc"		
        super(cgmMetaFunc, self).__init__(*args, **kws)
        #self._l_ARGS_KWS_DEFAULTS = [{'kw':'mNodeInstance',"default":None}]
        #=================================================================  

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmNode - subclass to Red9.MetaClass
#=========================================================================
def isTransform(node):
    return SEARCH.is_transform(node)

def getTransform(node):
    return SEARCH.get_transform(node)


def reinitializeMetaClass(node):
    try:#See if we have an mNode
        node.mNode
        mObj = node
    except:#initialze
        mObj = r9Meta.MetaClass(node)
    _buffer = mObj.mNode

    _keyCheck = mc.ls(mObj.mNode,long=True)[0]
    if _keyCheck in list(r9Meta.RED9_META_NODECACHE.keys()):
        log.debug('Cached already and class to be changed....')

        try:
            r9Meta.RED9_META_NODECACHE.pop(_keyCheck)
            log.debug("Pushed from cache: {0}".format(_buffer))
        except Exception as error:
            raise Exception(error)

    return r9Meta.MetaClass(_buffer)

def set_mClassInline(self, setClass = None):
    try:#>>> TO CHECK IF WE NEED TO CLEAR CACHE ---------------------------------------------------------
        _reinitialize = False
        _str_func = "set_mClassInline( '{0}' )".format(self.mNode)	

        if self.isReferenced():
            raise ValueError("Cannot set a referenced node's mClass")

        _currentMClass = ATTR.get(self.mNode,'mClass')#...use to avoid exceptions	
        _b_flushCacheInstance = False

        if setClass in [True, 1]:
            setClass = type(self).__name__	

        if setClass not in r9Meta.RED9_META_REGISTERY:
            log.error("{0} | mClass value not registered, cannot set. - '{1}'".format(_str_func,setClass))	
            return False

        if setClass:#...if we're going to set the mClass attr...
            if _currentMClass:#...does it have a current mClass attr value?
                if _currentMClass != setClass:#...if not the same, replace
                    log.error("Cannot change mClass type during init. Use self.convertMClassType(setClass)")		    
                else:
                    log.debug("{0} | mClasses match. ignoring...".format(_str_func))				    		
            else:#...if we have no value, set it
                log.warning("{0} | no mClass value, setting to '{1}'".format(_str_func,setClass))				
                self.addAttr('mClass',setClass)
                _reinitialize = True

        return _reinitialize
    except Exception as error:
        raise Exception("set_mClassInline fail >> %s"%error)

class cgmTest(r9Meta.MetaClass):
    def __bind__(self):pass	    
    def __init__(self,node = None, name = None,nodeType = 'network',**kws):	
        """ 
        Utilizing Red 9's MetaClass. Intialized a node in cgm's system.
        """			
        super(cgmTest, self).__init__(node=node, name = name, nodeType = nodeType)
        log.info("cached: {0}".format(self.cached))
        log.info("setClass: {0}".format(setClass))			
        log.info("kws: {0}".format(kws))		

class cgmNode(r9Meta.MetaClass):
    def __init__(self,node = None, name = None,nodeType = 'network', **kws):
            """ 
            Utilizing Red 9's MetaClass. Intialized a node in cgm's system.
            """
            _str_func = 'cgmNodeNew.__init__'
            createdState = True
            if node is not None and mc.objExists(node):
                log.debug("|{0}| >> Exists ".format(_str_func))                                                
                createdState = False
            elif name is not None and mc.objExists(name):
                log.debug("|{0}| >> Exists ".format(_str_func))                                                                
                createdState = False
    
            #ComponentMode ----------------------------------------------------------------------
            componentMode = False
            component = False	
            if node is not None:
                if VALID.is_component(node):
                    componentMode = True
                    component = node.split('.')[-1]
                    node = node.split('.')[0]
    
            _autofill = kws.get('autofill',False)
    
            super(cgmNode, self).__init__(node,name = name,nodeType = nodeType,autofill = _autofill, **kws)
    
    
            #>>> TO USE Cached instance ---------------------------------------------------------
            if self.cached:
                log.debug("|{0}| >> using cache: {1}".format(_str_func,self._lastDagPath))
                return

            #====================================================================================
            #...see if extending unmanaged is necessary    	
            for a in '__justCreatedState__','__componentMode__','__component__':
                if a not in self.UNMANAGED:
                    self.UNMANAGED.append(a)   	
            try:
                object.__setattr__(self, '__componentMode__', componentMode)
                object.__setattr__(self, '__component__', component)
                object.__setattr__(self, '__justCreatedState__', createdState)	    
            except Exception as e:
                log.error("|{0}| >> Failed to extend...".format(_str_func))                
                r9Meta.printMetaCacheRegistry()                
                for arg in e.args:
                    log.error(arg)            
                raise Exception(e)
            
    def __repr__(self):
        try:
            if self.hasAttr('mClass'):
                return "(node: '{0}' | mClass: {1} | class: {2})".format(self.mNode.split('|')[-1], self.mClass, self.__class__)
            else:
                return "(node: '{0}' | class: {1})".format(self.mNode.split('|')[-1], self.__class__)
        except:
            # if this fails we have a dead node more than likely
            try:
                RED9_META_NODECACHE.pop(object.__getattribute__(self, "_lastUUID"))
                log.debug("Dead mNode %s removed from cache..." % object.__getattribute__(self, "_lastDagPath"))
            except:pass
            try:
                return ("Dead mNode : Last good dag path was: %s" % object.__getattribute__(self, "_lastDagPath"))
            except:
                return "THIS NODE BE DEAD BY THINE OWN HAND"
    
    def hasAttr(self, attr):
        '''
        simple wrapper check for attrs on the mNode itself.
        Note this is not run in some of the core internal calls in this baseClass
        '''
        if self.isValidMObject():
            try:
                _result = self._MFnDependencyNode.hasAttribute(attr)
                if not _result:#..this pass gets the alias
                    #Must rewrap the mobj, if you don't it kills the existing mNode and corrupts its cache entry
                    #2011 bails because it lacks the api call anyway, 2012 and up work with this
                    mobj= OM.MObject()
                    selList=OM.MSelectionList()
                    selList.add(self._MObject)
                    selList.getDependNode(0,mobj)		    
                    _result = self._MFnDependencyNode.findAlias(attr,mobj)
                return _result
            except Exception as e:
                #log.error('hasAttr failure...{0}'.format(err))#...this was just to see if I had an error
                for arg in e.args:
                    log.error(arg)                  
                return mc.objExists("{0}.{1}".format(self.mNode, attr)) 
            
    #========================================================================================================    
    #>>> Overloads - Departures from red9's core...
    #======================================================================================================== 
    def __setMessageAttr__(self,attr,value, force = True, ignoreOverload = False,**kws):
        try:
            if ignoreOverload:#just use Mark's
                log.info('r9Method...')
                r9Meta.MetaClass.__setMessageAttr__(self,attr,value,**kws)
            else:
                if value:
                    if issubclass(type(value),list):
                        value = [VALID.mNodeString(o) for o in value]
                    else:
                        value = VALID.mNodeString(value)
                ATTR.set_message(self.mNode, attr, value)   
        except Exception as err:cgmGEN.cgmExceptCB(Exception,err)
        
    def addAttr(self, attr,value = None, attrType = None, enumName = None,initialValue = None,lock = None,keyable = None, hidden = None,*args,**kws):
        _str_func = 'addAttr'
        
        log.debug("|{0}| >> node: {1} | attr: {2} | attrType: {3}".format(_str_func,self.p_nameShort,attr, attrType))
        
        if attr not in self.UNMANAGED and not attr=='UNMANAGED':  
            if self.hasAttr(attr):#Quick create check for initial value
                initialCreate = False
                if self.isReferenced():
                    log.warning('This is a referenced node, cannot add attr: %s.%s'%(self.getShortName(),attr))
                    return False
                
                #Conversion create
                #validatedAttrType = attributes.validateRequestedAttrType(attrType)
                if attrType is not None:
                    validatedAttrType = ATTR.validate_attrTypeName(attrType)
                    if validatedAttrType in ['string','float','double','long']:
                        currentType = ATTR.get_type(self.mNode,attr)
                        if currentType != validatedAttrType:
                            log.info("cgmNode.addAttr >> %s != %s : %s.%s. Converting."%(validatedAttrType,currentType,self.getShortName(),attr))
                            ATTR.convert_type(self.mNode,attr,validatedAttrType)
                            #cgmAttr(self, attrName = attr, attrType=validatedAttrType)                
            else:
                initialCreate = True
                if value is None and initialValue is not None:#If no value and initial value, use it
                    value = initialValue
            
            if enumName is None and attrType == 'enum':
                enumName = "off:on"		
                
            if value is not None and not attrType:
                if VALID.isListArg(value):
                    log.debug("|{0}| >> value arg and no attrType...{1}".format(_str_func,value))
                    _good = True
                    for v in value:
                        if VALID.valueArg(v) is False:
                            log.debug("|{0}| >> not a number: {1}".format(_str_func,v))
                            _good = False
                            break
                    if _good and len(value) == 3:
                        log.debug("|{0}| >> all values, setting to double3.{1}".format(_str_func,value))                        
                        attrType = 'double3'

            if attrType == 'enum':
                r9Meta.MetaClass.addAttr(self,attr,value=value,attrType = attrType,enumName = enumName, *args,**kws)
            else:
                r9Meta.MetaClass.addAttr(self,attr,value=value,attrType = attrType, *args,**kws)	

            if value is not None and r9Meta.MetaClass.__getattribute__(self,attr) != value: 
                if ATTR.is_connected([self.mNode,attr]):
                    ATTR.break_connection(self.mNode,attr)
                self.__setattr__(attr,value,**kws)
  
            #Easy carry for flag handling - until implemented
            #==============  
            if keyable is not None or hidden is not None:
                cgmAttr(self, attrName = attr, keyable=keyable,hidden = hidden)
            if lock is not None:
                mc.setAttr(('%s.%s'%(self.mNode,attr)),lock=lock)	

            return True
        return False

    def connectChildNode(self, node, attr, connectBack = None, srcAttr=None):
        """
        Replacing Mark's connect child with our own which connects to .message connections.

        Fast method of connecting message links to the mNode as parents
        @param node: Maya nodes to connect to this mNode
        @param attr: Name for the message attribute on self to connec to the parent

        @param srcAttr: If given this becomes the attr on the node which connects it 
                        to the parent. If NOT given the connection attr is the parent.message
        """
        if issubclass(type(node), r9Meta.MetaClass):
            node=node.mNode        

        ATTR.set_message(self.mNode, attr, node)            

        if connectBack is not None:
            ATTR.set_message(node, connectBack,self.mNode )            
        return True    
    
    def connectParentNode(self, node, attr, connectBack = None, srcAttr=None):
        """
        Replacing Mark's connect Parent with our own which connects to .message connections.

        Fast method of connecting message links to the mNode as parents
        @param node: Maya nodes to connect to this mNode
        @param attr: Name for the message attribute on self to connec to the parent

        @param srcAttr: If given this becomes the attr on the node which connects it 
                        to the parent. If NOT given the connection attr is the parent.message
        """
        if issubclass(type(node), r9Meta.MetaClass):
            node=node.mNode        
        #if connectBack and not mc.attributeQuery(connectBack, exists=True, node=node):
            #add to parent node
            #mc.addAttr(node,longName=connectBack, at='message', m=False)
        
        ATTR.set_message(self.mNode, attr, node)            

        if connectBack is not None:
            ATTR.set_message(node, connectBack,self.mNode )            
        return True


    def connectChildrenNodes(self, nodes, attr, connectBack = None, force=True):
        """
        Replacement connector using .msg connections
        """
        if type(nodes) not in [list,tuple]:nodes=[nodes]
        nodesToDo = []
        for node in nodes:
            if issubclass(type(node), r9Meta.MetaClass):
                nodesToDo.append(node.mNode) 
            elif mc.objExists(node):
                nodesToDo.append(node) 
            else:
                log.warning("connectChildrenNodes can't add: '%s'"%node)

        ATTR.set_message(self.mNode, attr, nodesToDo)            
        
        if connectBack is not None:
            for i,node in enumerate(nodesToDo):
                ATTR.set_message(node, connectBack, self.mNode)                                

    
    #========================================================================================================
    #>>> Names...
    #========================================================================================================
    def uiPrompt_rename(self,title = None):
        _short = self.p_nameShort
        if title is None:
            _title = 'Rename {0}'.format(_short)
        else:_title = title
        result = mc.promptDialog(title=_title,
                                 message='Current: {0} | type: {1}'.format(_short,self.getMayaType()),
                                 button=['OK', 'Cancel'],
                                 text = self.p_nameBase,
                                 defaultButton='OK',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')
        if result == 'OK':
            _v =  mc.promptDialog(query=True, text=True)
            self.rename(_v)
        else:
            log.error("|{0}| Name change cancelled".format(self.mNode))
            return False 
    
    def getNameShort(self):
        return NAMES.short(self.mNode)
   
    def getNameLong(self):
        return NAMES.long(self.mNode)
    
    def getNameBase(self):
        return NAMES.base(self.mNode)
    
    def asAttrString(self,arg):
        return "{0}.{1}".format(self.mNode,str(arg))
    def getNameMatches(self,report=False):
        """Get any other nodes sharing the same base node as this one"""
        _str_func = 'getNameMatches'
        log.debug("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
        _str_short = self.p_nameShort
        res = []
        for o in mc.ls(self.p_nameBase):
            if o != _str_short:
                log.debug("|{0}| >> found: {1}".format(_str_func,o)+ '-'*80)
                res.append(o)
        if report and res:
            log.info("|{0}| >>  {1}".format(_str_func,self)+ '-'*80)
            log.info("Self long: '{0}'".format(self.p_nameLong))
            for i,v in enumerate(res):
                log.info("idx: {0} | obj: '{1}'".format(i,v))
                
            log.info(cgmGEN._str_subLine)
        return res
    
    getShortName = getNameShort
    getLongName = getNameLong
    getBaseName = getNameBase

    #Some name properties
    p_nameShort = property(getNameShort)
    p_nameLong = property(getNameLong)
    p_nameBase = property(getNameBase)   
    
    #Reference Prefix
    #==============    
    def getReferencePrefix(self):
        return SEARCH.get_referencePrefix(self)
    p_referencePrefix = property(getReferencePrefix)   
    
    #getNodeChildren = getChildren
    #cgmNaming stuff...
    #================================================================
    def doName(self,sceneUnique=False,nameChildren=False,fastIterate = True,fastName = True,**kws):
        """
        Rename an object with our name tag system
        
        :parameters:
            sceneUnique(bool): Whether to make a scene unique name
            nameChildren(bool): Whether to rename children
            fastIterate(bool)
            fastName(bool)
            
        :returns
            newName(str)
        """   
        #try:
        if fastName:
            d_updatedNamesDict = self.getNameDict()
            ignore = kws.get('ignore') or []
            if 'cgmName' not in list(d_updatedNamesDict.keys()):
                test = {}
                if self.getMayaType() !='group' and 'cgmName' not in ignore:
                    _short = self.getShortName()
                    for k,v in list(d_updatedNamesDict.items()):
                        if v and v in _short:
                            _short = _short.replace(v,'')
                    _short = NAMES.clean(_short)
                    d_updatedNamesDict['cgmName'] = _short

            _str_nameCandidate =  nameTools.returnCombinedNameFromDict(d_updatedNamesDict)
            mc.rename(self.mNode, _str_nameCandidate	)
            if nameChildren:
                for mObj in validateObjListArg(TRANS.descendents_get(self.mNode)):
                    mObj.doName()
                    
        else:
            if sceneUnique:
                log.error("Remove this cgmNode.doName sceneUnique call")
            if self.isReferenced():
                log.error("'%s' is referenced. Cannot change name"%self.mNode)
                return False	
            #Name it
            NameFactory(self).doName(nameChildren = nameChildren,fastIterate=fastIterate,**kws)	  
        return self.mNode
        #except Exception,err:
            #cgmGEN.cgmExceptCB(Exception,err,localDat=vars())
            
    def getNameDict(self,**kws):
        #reload(nameTools)
        return nameTools.returnObjectGeneratedNameDict(self.mNode,**kws) or {} 
    
    def doTagAndName(self,d_tags, **kws):
        """
        Add tags and name in one fell swoop
        """
        if type(d_tags)is not dict:
            raise ValueError("{}.doTagAndName >> d_tags not dict : {}".format(self.p_nameShort,d_tags))		    
        for tag in list(d_tags.keys()):
            self.doStore(tag,d_tags[tag])
        self.doName()
        return self.mNode

            
    def getNameAlias(self):
        if self.hasAttr('cgmAlias'):
            return self.cgmAlias
        buffer =  nameTools.returnRawGeneratedName(self.mNode, ignore = ['cgmType'])
        if buffer:return buffer
        else:return self.getBaseName()
    p_nameAlias = getNameAlias
        
    def doCopyNameTagsFromObject(self,target,ignore=[False]):
        """
        Get name tags from a target object (connected)

        Keywords
        ignore(list) - tags to ignore

        Returns
        success(bool)
        """
        _str_func = 'doCopyNameTagsFromObject'
        
        log.debug("|{0}| >> node: {1} | target: {2} | ignore: {3}".format(_str_func,self.p_nameShort,target, ignore))
        
        if type(ignore) not in [list,tuple]:ignore = [ignore]
        
        assert mc.objExists(target),"Target doesn't exist"
        
        targetCGM = nameTools.returnObjectGeneratedNameDict(target,ignore = ignore)
        #cgmGEN.log_info_dict(targetCGM)
        didSomething = False
        
        
        for tag,v in list(targetCGM.items()):
            if tag in ignore:continue
            if ATTR.has_attr(target,tag):
                ATTR.copy_to(target,tag,self.mNode,inConnection=True)
                didSomething = True

        #self.update()
        return didSomething

    #========================================================================================================
    #>>> Transforms...
    #========================================================================================================
    def getParent(self,asMeta = False):
        buffer = TRANS.parent_get(self)
        if buffer and asMeta:
            return validateObjArg(buffer,mType = cgmObject)
        return buffer

    p_parent = property(getParent)
    parent = p_parent
    
    def getSiblings(self,asMeta = False):
        _res = TRANS.siblings_get(self)
        if _res and asMeta:
            return validateObjListArg(_res,'cgmNode')
        return _res     
    
    def getComponent(self):
        """
        Replacement mNode call for component mode
        """
        if self.__componentMode__ and self.__component__:
            buffer = '%s.%s'%(self.mNode,self.__component__)
            if mc.objExists(buffer):return buffer
            else:log.warning("Component no longer exists: %s"%self.__component__)
            return self.mNode
        return self.mNode

    def isComponent(self):
        """
        Returns if what is stored is a component
        """
        if self.__componentMode__ and self.__component__:
            buffer = '%s.%s'%(self.mNode,self.__component__)
            if mc.objExists(buffer):return True
            else:log.warning("Component no longer exists: %s"%self.__component__)
            return False
        return False  
    
    
    def getComponents(self,arg = False, flatten = True):
        """
        Query components of a given type on our node
        
        :parameters:
            arg(str): type to query. ex: vtx,face,edge,etc...
            flatten(bool): whether to flatten the list or not
    
        :returns
            list of components(list)
        """           
        return mc.ls(['%s.%s[*]'%(self.mNode,arg)],flatten=flatten)

        """
        else:
            try:
                objType = self.getMayaType()
                if objType in ['mesh','polyVertex','polyEdge','polyFace','nurbsCurve',
                               'nurbsSurface','shape','surfaceCV']:
                    if objType == 'mesh':
                        return mc.ls([self.mNode+'.vtx[*]'],flatten=True)
                    elif objType == 'polyVertex':
                        return self.getComponent()
                    elif objType in ['polyEdge','polyFace']:
                        mc.select(cl=True)
                        mc.select(self.mNode)
                        mel.eval("PolySelectConvert 3")
                        return mc.ls(sl=True,fl=True)
                    elif objType in ['nurbsCurve','nurbsSurface']:
                        l_components = []
                        shapes = mc.listRelatives(self.mNode,shapes=True,fullPath=True)
                        if shapes:
                            for shape in shapes:
                                l_components.extend(mc.ls ([shape+'.ep[*]'],flatten=True))
                            return l_components
                        else:
                            return mc.ls([self.mNode+'.ep[*]'],flatten=True)
                    elif objType == 'shape':
                        return mc.ls ([self.mNode+'.ep[*]'],flatten=True)
                    elif objType == 'surfaceCV':
                        return self.getComponent()
                    else:
                        return self.getComponent()
                return False 
            except StandardError,error:
                log.warning("getComponents: %s"%error)	
                return False    """
        
    def getPosition(self,*a,**kws):
        if self.isComponent():
            return POS.get(self.getComponent(),*a,**kws)        
        return TRANS.position_get(self.mNode, *a,**kws)
    
    
    def getPositionOLD(self,space = 'world'):
        if self.isComponent():
            return POS.get(self.getComponent())
            objType = self.getMayaType()	    
            if objType in ['polyVertex','polyUV','surfaceCV','curveCV','editPoint','nurbsUV','curvePoint']:
                if worldSpace:return mc.pointPosition(self.getComponent(),world = True)
                return mc.pointPosition(self.getComponent(),local = True)
            elif objType in ['polyFace','polyEdge']:
                mc.select(cl=True)
                mc.select(self.getComponent())
                mel.eval("PolySelectConvert 3")
                verts = mc.ls(sl=True,fl=True)
                posList = []
                for vert in verts:
                    if worldSpace:posList.append( mc.pointPosition(vert,world = True) )
                    else:posList.append( mc.pointPosition(vert,local = True) )			    
                pos = DIST.get_average_position(posList)
                mc.select(cl=True)
                return pos
            else:
                raise NotImplementedError("Don't know how to position '%s's componentType: %s"%(self.getShortName,objType))

        else:
            return POS.get(self.getComponent(),space = 'world')    
        
    def getDag(self,asMeta = False):
        _res = VALID.getTransform(self.mNode)
        
        if _res and asMeta:
            return cgmObject(_res)
        return _res
        """Find the transform of the object"""
        buffer = mc.ls(self.mNode, type = 'transform') or False
        if buffer:
            return buffer[0]
        else:
            buffer = mc.listRelatives(self.mNode,parent=True,type='transform') or False
        if buffer:
            return buffer[0]
        return False
    getTransform = getDag
    
    #========================================================================================================     
    #>>> Attributes 
    #========================================================================================================      
    def isAttrKeyed(self,attr):
        return ATTR.is_keyed([self.mNode,attr])
        #return ATTR.is_keyed(self, *a,**kws)
    
    def isAttrConnected(self,attr):
        return ATTR.is_connected([self.mNode,attr])
    
    def doStore(self,*a,**kws):
        """   
        Store information to an attribute.
        
        Supported: message,doubleArray,json dicts and much more
        
        :parameters:
            node(str) -- 
            attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
            data(varied) -- data to add
            attrType(varied) -- specify, if not specified will pick best guess
            lock(bool)
    
        :returns
            status(bool)
        """        
        return ATTR.store_info(self.mNode,*a,**kws)
    
    def copyAttrTo(self,*a,**kws):
        """   
        Copy attributes from one object to another as well as other options. If the attribute already
        exists, it'll copy the values. If it doesn't, it'll make it. If it needs to convert, it can.
        It will not make toast.  
    
        :parameters:
            fromAttr(string) - source attribute
            toObject(string) - obj to copy to
            toAttr(string) -- name of the attr to copy to . Default is None which will create an 
                          attribute of the fromAttr name on the toObject if it doesn't exist
            convertToMatch(bool) -- whether to automatically convert attribute if they need to be. Default True                  
            values(bool) -- copy values. default True
            inputConnections(bool) -- default False
            outGoingConnections(bool) -- default False
            keepSourceConnections(bool)-- keeps connections on source. default True
            copySettings(bool) -- copy the attribute state of the fromAttr (keyable,lock,hidden). default True
            driven(string) -- 'source','target' - whether to connect source>target or target>source
    
        :returns
            success(bool)
        """         
        return ATTR.copy_to(self.mNode,*a,**kws)  
    
    def getMayaAttr(self,*a,**kws):
        return ATTR.get(self.mNode,*a,**kws)
    getAttr = getMayaAttr#...TEMP
    
    def setMayaAttr(self,*a,**kws):
        return ATTR.set(self.mNode,*a,**kws)
    
    def getMayaAttrString(self,attr=None, nameCall = 'short'):
        return "{0}.{1}".format(getattr(NAMES,nameCall)(self.mNode), attr)
    
    def doConnectIn(self, attr=None, source = None, transferConnections = False, lock=False,**kws):
        """   
        Connect a source to a given attribute(s) on our node. You may only have one source. You may have multiple
        attrs
    
        :parameters:
            attr(list/string) - Can connect multiple at once
            source(string) - What we're plugging in. If a value with no '.' is input, it will look for that attr on our node
    
        :returns
            success(bool)
        """         
        if not VALID.isListArg(attr):
            attr = [attr]
        
        _res = []  
        for a in attr:    
            if '.' in source:
                _res.append( ATTR.connect(source, self.getMayaAttrString(a),transferConnections, lock,**kws) )          
            else:
                _res.append( ATTR.connect(self.getMayaAttrString(source), self.getMayaAttrString(a),transferConnections, lock,**kws) ) 
        return _res
    
    def doConnectOut(self, attr=None, target = None, transferConnections = False, lock=False,**kws):
        if not VALID.isListArg(target):
            target = [target]
        
        _res = []    
        for t in target:
            if '.' in t:
                _res.append( ATTR.connect(self.getMayaAttrString(attr),
                                          t,
                                          transferConnections,
                                          lock,**kws) ) 
            else:
                _res.append( ATTR.connect(self.getMayaAttrString(attr),
                                          self.getMayaAttrString(t),
                                          transferConnections, lock,**kws) )             
            
        return _res
    
    def getEnumValueString(self,attr):
        return ATTR.get_enumValueString(self.mNode,attr)
    
    def getAttrs(self,**kws):
        return mc.listAttr(self.mNode,**kws) or []   
    
    def doRemove(self,a):
        _str_func = 'doRemove'
        log.warning("|{0}| >> please remove call...".format(_str_func))
        return self.delAttr(a)
    
    def resetAttrs(self, attrs = None, transformsOnly = None, visible = None,keyable=True):
        """   
        Reset specified attributes to their default values
        
        :parameters:
            node(str) -- 
            attrs(str/list) -- attributes to reset
            
        :returns
            list of reset attrs(list)
        """        
        obj = self.p_nameShort

        if attrs == None:
            attrs = mc.listAttr(obj, keyable=keyable, unlocked=True) or False
        else:
            attrs = VALID.listArg(attrs)
            
        l_trans = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ']
        _reset = {}
        
        d_defaults = {}
        for plug in ['defaultValues','transResets']:
            if self.hasAttr(plug):
                d_defaults = getattr(self,plug)
        
        for attr in attrs:
            try:
                if transformsOnly is not None and transformsOnly:
                    if ATTR.get_nameLong(obj,attr) not in l_trans:
                        continue
                dVal = d_defaults.get(attr)
                if dVal is not None:
                    default = dVal
                else:
                    default = mc.attributeQuery(attr, listDefault=True, node=obj)[0]
                ATTR.set(obj,attr,default)
                _reset[attr] = default
            except Exception as err:
                log.error("{0}.{1} resetAttrs | error: {2}".format(obj, attr,err))   	
        return _reset
    
    def setAttrFlags(self,*a,**kws):
        """   
        Multi set keyable,lock, visible, hidden, etc...
    
        :parameters:
            node(str)
            attrs(str)
            lock(bool)
            visible(bool)
            keyable(bool)
    
        """        
        return ATTR.set_standardFlags(self.mNode,*a,**kws)    
    
    def verifyAttrDict(self,d_attrs,**kws):
        if type(d_attrs) is not dict:
            raise ValueError("Not a dict: %s"%self.p_nameShort)
        
        _keys = list(d_attrs.keys())
        _keys.sort()
        
        for attr in _keys:
            try:	
                buffer = d_attrs.get(attr)
                if ':' in buffer:
                    self.addAttr(attr,attrType = 'enum', enumName= buffer,**kws)		    
                else:
                    self.addAttr(attr,attrType = buffer,**kws)
            except Exception as error:
                log.error("%s.verifyAttrDict >>> Failed to add attr: %s | data: %s | error: %s"%(self.p_nameShort,attr,d_attrs.get(attr),error))
        return True
    
    #========================================================================================================     
    #>>> Query 
    #========================================================================================================     
    def getMayaType(self):
        return VALID.get_mayaType(self.mNode)
    
    def getPositionOutPlug(self,asMeta = False):
        l_elibiblePlugs = ['worldPosition','position'] 
        d_plugTypes= {'worldPosition':'worldPosition[0]','position':'position'}
        _res = False
        for attr in l_elibiblePlugs:
            if self.hasAttr(attr):
                _res = "{0}.{1}".format(self.mNode,d_plugTypes.get(attr))
        if _res and asMeta:
            return validateAttrArg(_res)
        return _res
    
    
    #========================================================================================================     
    #>>> Message stuff 
    #========================================================================================================        
    def getMessage(self,attr,fullPath = True, asMeta = False, dataAttr = None, dataKey = None, simple = True,*args,**kws):
        """
        This maybe odd to some, but we treat traditional nodes as regular message connections. However, sometimes, you want a message like connection
        to an attribute. To do this, we devised a method of creating a compaptble attr on the object to recieve the message, 
        connecting the attribute you want to connect to that attribute and then when you call an attribute as getMessage, if it is not a message attr
        it tries to trace back that connection to an attribute.
        simple MUST be True by default
        """
        _str_func = 'getMessage'
        _res = ATTR.get_message(self.mNode,attr,dataAttr=dataAttr,dataKey=dataKey,simple=simple)
        #_res = ATTR.get_message(self.mNode,attr,simple=True)
        
        if asMeta and _res:
            return validateObjListArg(_res)
        if _res and fullPath:
            return [NAMES.long(o) for o in _res]
        return _res    
    
    def getMessageAsMeta(self,attr,asList=False):
        """
        This is for when you need to build a attr name in 
        """
        _str_func = 'getMessageAsMeta'
        buffer = self.getMessage(attr)
        if not buffer:
            return False
        if '.' in buffer:
            try:return validateAttrArg(buffer)['mi_plug']
            except Exception as e:
                log.error("|{0}| >> Failed to query attr: {1}.{2} ...".format(_str_func,self.p_nameShort,attr))                                
                for arg in e.args:
                    log.error(arg)      
                raise Exception(e)
            
        if asList or len(buffer) > 1:
            return validateObjListArg(buffer)
        return validateObjArg(buffer)
    #========================================================================================================     
    #>>> msgLists... 
    #========================================================================================================        
    def msgList_connect(self,*a,**kws):
        """
        Append node to msgList

        Returns index
        """
        return ATTR.msgList_connect(self.mNode,*a,**kws)
    def msgList_getMessage(self,*a,**kws):#TEMP
        return ATTR.msgList_get(self.mNode,*a,**kws)

    def msgList_get(self,*a,**kws):
        """   
        Get msgList return.
        
        :parameters:
            attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
            mode(str) -- what kind of data to be looking for
                NONE - just get the data
                message - getMessage
            dataAttr(str) - Attr to store extra info. If none specified, makes default
            cull(bool) - Cull for empty entries
            asMeta(bool) - Whether to return data as meta or not
    
        :returns
            msgList(list)
        """
        _asMeta = kws.get('asMeta',True)
        
        try:kws.pop('asMeta')
        except:pass
        
        _res = ATTR.msgList_get(self.mNode,*a,**kws)
        
        #if not _res:
            #return []

        if _res and _asMeta:
            return validateObjListArg(_res,noneValid=True)
        return _res

    def msgList_append(self,*a,**kws):
        """
        Append node to msgList

        Returns index
        """
        
        return ATTR.msgList_append(self.mNode,*a,**kws)
      

    def msgList_index(self,*a,**kws):
        """
        Return the index of a node if it's in a msgList
        """
        return ATTR.msgList_index(self.mNode,*a,**kws)
    

    def msgList_remove(self,*a,**kws):
        """
        Return the index of a node if it's in a msgList
        """
        return ATTR.msgList_remove(self.mNode,*a,**kws)
  

    def msgList_purge(self,*a,**kws):
        """
        Purge all the attributes of a msgList
        """
        return ATTR.msgList_purge(self.mNode,*a,**kws)
        

    def msgList_clean(self,*a,**kws):
        """
        Removes empty entries and pushes back
        """
        return ATTR.msgList_clean(self.mNode,*a,**kws)


    def msgList_exists(self,*a,**kws):
        """
        Fast check to see if we have data on this attr chain
        """
        return ATTR.msgList_exists(self.mNode,*a,**kws)
        

    def getSequentialAttrDict(self,attr = None):
        """
        Get a sequential attr dict. Our attr should be listed without the tail '_'
        ex: {0: u'back_to_back_0', 1: u'back_to_back_1'}
        """
        return ATTR.get_sequentialAttrDict(self.mNode,attr)
    
    def datList_connect(self,*a,**kws):
        """
        Append node to datList

        Returns index
        """
        return ATTR.datList_connect(self.mNode,*a,**kws)
    
    def datList_get(self,*a,**kws):
        """   
        Get datList return.
        
        :parameters:
            attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
            mode(str) -- what kind of data to be looking for
                NONE - just get the data
                message - getMessage
            dataAttr(str) - Attr to store extra info. If none specified, makes default
            cull(bool) - Cull for empty entries
            asMeta(bool) - Whether to return data as meta or not
    
        :returns
            datList(list)
        """
        _asMeta = kws.get('asMeta',True)
        

        
        _res = ATTR.datList_get(self.mNode,*a,**kws)
        
        #if not _res:
            #return []

        return _res

    def datList_append(self,*a,**kws):
        """
        Append node to datList

        Returns index
        """
        return ATTR.datList_append(self.mNode,*a,**kws)
      

    def datList_index(self,*a,**kws):
        """
        Return the index of a node if it's in a datList
        """
        return ATTR.datList_index(self.mNode,*a,**kws)
    

    def datList_remove(self,*a,**kws):
        """
        Return the index of a node if it's in a datList
        """
        return ATTR.datList_remove(self.mNode,*a,**kws)
  

    def datList_purge(self,*a,**kws):
        """
        Purge all the attributes of a datList
        """
        return ATTR.datList_purge(self.mNode,*a,**kws)
        

    def datList_clean(self,*a,**kws):
        """
        Removes empty entries and pushes back
        """
        return ATTR.datList_clean(self.mNode,*a,**kws)

    def datList_exists(self,*a,**kws):
        """
        Fast check to see if we have data on this attr chain
        """
        return ATTR.datList_exists(self.mNode,*a,**kws)    
    
    #========================================================================================================     
    #>>> Utilities... 
    #========================================================================================================      
    def stringModuleCall(self, module = None,  func = '', *args,**kws):
        """
        Function to call from a given module a function by string name with args and kws. 
        """
        _short = self.p_nameShort        
        _str_func = 'stringModuleCall( {0} )'.format(_short)
        _res = None
        if not args:
            _str_args = ''
            args = [self]
        else:
            _str_args = ','.join(str(a) for a in args) + ','
            args = [self] + [a for a in args]
        
        try:
            return getattr(module,func)(*args,**kws)
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err)
        if not kws:
            kws = {}
            _kwString = ''  
        else:
            _l = []
            for k,v in list(kws.items()):
                _l.append("{0}={1}".format(k,v))
            _kwString = ','.join(_l)  
            
        try:
            #reload(module)
            log.debug("|{0}| >> On: {1}.{2}".format(_str_func,module.__name__, _short))     
            log.debug("|{0}| >> {1}.{2}({3}{4})...".format(_str_func,_short,func,_str_args,_kwString))                                    
            _res = getattr(module,func)(*args,**kws)
        except Exception as err:
            #print(cgmGEN._str_hardLine)
            print((cgmGEN._str_subLine))            
            print(("  |{0}| >> Failure: {1}".format(_str_func, err.__class__)))
            print(("  Node: {0}".format(_short)))
            print(("  Module: {0} ".format(module)))            
            print(("  Func: {0} ".format(func)))            
            """
            if args:
                print(cgmGEN._str_headerDiv + "  Args...")
                for a in args:
                    print("      {0}".format(a))
            if kws:
                print(cgmGEN._str_headerDiv + "  KWS...")
                for k,v in kws.iteritems():
                    print("      {0} : {1}".format(k,v))"""
                    
            #print(cgmGEN._str_baseStart + "  Errors...")
            #for a in err.args:
                #log.error(a)
            #raise Exception,err
            cgmGEN.cgmExceptCB(Exception,err)
        return _res    
    
    def doLoc(self,forceBBCenter = False,nameLink = False, fastMode = False):
        """
        Create a locator from an object
    
        Keyword arguments:
        forceBBCenter(bool) -- whether to force a bounding box center (default False)
        nameLink(bool) -- whether to copy name tags or link the object to cgmName
        """
        #_str_func = '{0}.doLoc'.format(self.p_nameShort)
        #t_master = time.time()	            
        #t1 = time.time()	
         
        buffer = False
        if self.isComponent():
            buffer =  locators.locMeObject(self.getComponent(),forceBBCenter = forceBBCenter)
            #log.info("{0}>> component loc: {1}".format(_str_func, "%0.3f seconds"%(time.time() - t1)))
            #t1 = time.time()	            
        else:
            #if self.isTransform():
            #log.info("{0}>> transform loc: {1}".format(_str_func, "%0.3f seconds"%(time.time() - t1)))
            #t1 = time.time()     
            #if fastMode:
            buffer = cgmObject(mc.spaceLocator()[0])
            buffer.rotateOrder = self.rotateOrder
            
            if forceBBCenter:
                objTrans = POS.get(self.mNode,'bb')
            else:
                objTrans = mc.xform(self.mNode, q=True, ws=True, sp=True)
                
            objRot = mc.xform(self.mNode, q=True, ws=True, ro=True)
            objRotAxis = mc.xform(self.mNode, q=True, os=True, ra=True)
        
            mc.move (objTrans[0],objTrans[1],objTrans[2], buffer.mNode)			
            mc.rotate (objRot[0], objRot[1], objRot[2], buffer.mNode, ws=True)
            for i,a in enumerate(['X','Y','Z']):
                ATTR.set(buffer.mNode, 'rotateAxis{0}'.format(a), objRotAxis[i])                    
            #else:
                #buffer = locators.locMeObject(self.mNode,forceBBCenter = forceBBCenter)                    
        if not buffer:
            return False
        
        i_loc = validateObjArg(buffer,'cgmObject',setClass = True)#setClass=True
        #log.info("{0}>> validate: {1}".format(_str_func, "%0.3f seconds"%(time.time() - t1)))
        #t1 = time.time()            
        #if nameLink:
            #i_loc.connectChildNode(self,'cgmName')
        if not nameLink:
            #i_loc.doCopyNameTagsFromObject(self.mNode,ignore=['cgmType'])
            #i_loc.doName()
            i_loc.rename(NAMES.get_base(self.mNode)+'_loc')
            #log.info("{0}>> name: {1}".format(_str_func, "%0.3f seconds"%(time.time() - t1)))
            #t1 = time.time()            
        #log.info("{0}>> total: {1}".format(_str_func, "%0.3f seconds"%(time.time() - t_master)))            
        return i_loc
    
    def doDuplicate(self, **kws):
        """
        Return a duplicated object instance

        @Keyword arguments:
        breakMessagePlugsOut(bool) -- whether to break the outgoing message connections because Maya duplicates regardless of duplicate flags
        """
        #parentOnly = True, inputConnections = True,
        if self.isComponent():
            log.warning("doDuplicate fail. Cannot duplicate components")
            raise ValueError("doDuplicate fail. Cannot duplicate component: '%s'"%self.getShortName())

        breakMessagePlugsOut = kws.pop('breakMessagePlugsOut',False) 
        _keys = list(kws.keys())
        if 'po' not in _keys and 'parentOnly' not in _keys:
            kws['parentOnly'] = True
            
        if 'ic' not in _keys and 'inputConnections' not in _keys:
                        kws['inputConnections'] = True
                        
        buffer = mc.duplicate(self.mNode,**kws)[0]
        buffer = mc.rename(buffer, self.getBaseName()+'_DUPLICATE')
        i_obj = validateObjArg(buffer)	    

        if breakMessagePlugsOut:
            b_sourceLock = False
            b_drivenLock = False
            _str_messageCombined = '%s.msg'%i_obj.mNode

            if mc.getAttr(_str_messageCombined,lock=True):
                b_drivenLock = True
                mc.setAttr(_str_messageCombined,lock=False)

            for plug in mc.listConnections(_str_messageCombined,plugs =True):
                b_sourceLock = False
                if '[' in plug:
                    str_plug = plug.split('[')[0]
                else:str_plug = plug

                if mc.getAttr(str_plug,lock=True):#if locked, unlock
                    b_sourceLock = True
                    mc.setAttr(str_plug,lock=False)	

                try: mc.setAttr(str_plug,lock=False)
                except:raise Exception("%s.doDuplicate >> can't unlock '%s'"%(self.p_nameShort,str_plug))

                mc.disconnectAttr(_str_messageCombined,plug)
                if b_sourceLock:
                    mc.setAttr(str_plug,lock=False)
            if b_drivenLock:
                mc.setAttr(_str_messageCombined,lock=False) 
        return i_obj
    
    def doOverrideColor(self,*a,**kws):
        """
        Sets the color of a shape or object via override. In Maya 2016, they introduced 
        rgb value override.
        
        :parameters
            target(str): What to color - shape or transform with shapes
            key(varied): if str will check against our shared color dict definitions for rgb and index entries
            index(int): Color index
            rgb(list): rgb values to set in Maya 2016 or above
            pushToShapes(bool): Push the overrides to shapes of passed transforms
    
        """       
        #key = None, index = None, rgb = None, pushToShapes = True,
        return RIGGING.override_color(self.mNode,*a,**kws)
    
    
    
    #========================================================================================================     
    #>>> THESE ARE GOING AWAY... 
    #========================================================================================================    
    def getCGMNameTags(self,ignore=[False]):#TEMP...till transition to new rigger is done
        """
        Get the cgm name tags of an object.
        """
        self.cgm = {}
        for tag in l_cgmNameTags:
            if tag not in ignore:
                self.cgm[tag] = SEARCH.get_tagInfo(self.mNode,tag)
        return self.cgm        

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmObject - sublass to cgmNode
#=========================================================================   
class cgmObject(cgmNode):     
    def __init__(self,node = None, name = 'cgmObject', **kws):
        """
        asdfas
        """
        if kws and kws.get('nodeType') == 'joint':
            if node == None:
                mc.select(cl=True)
                node = mc.joint(name = name)
        super(cgmObject, self).__init__(node = node, name = name,nodeType = 'transform')

        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.info("Cached...")
            return
        
        if not VALID.is_transform(self.mNode):
            raise ValueError("[{0}] not a transform! The cgmObject class was designed to work with objects with transforms".format(self.mNode))
        
        self.p_translate = self.translate    
        self.p_rotate = self.rotate
        self.p_scale = self.scale   
        self.p_eulerAngles = self.rotate
        

    #========================================================================================================
    #>>> Heirarchy ...
    #========================================================================================================  
    def getParent(self,asMeta = False,fullPath = True):
        _res = TRANS.parent_get(self,fullPath)
        if _res and asMeta:
            return validateObjArg(_res,'cgmObject')
        return _res


    def doParent(self,target = False):
        """
        Function for parenting a maya instanced object while maintaining a correct object instance.

        Keyword arguments:
        parent(string) -- Target parent
        """
        return TRANS.parent_set(self.mNode,target)
        if target: #if we have a target parent
            if VALID.isListArg(target):
                target = target[0]
                print("Target arg is list, using first entry")
            try:
                bfr_target = target.p_nameLong
            except:
                try:
                    bfr_target = cgmNode(target).p_nameLong
                except Exception as error:
                    if not mc.objExists(target):
                        raise Exception("'{0}' - target object doesn't exist" .format(target)) 
                    raise Exception(error)
                    #raise Exception,error

            if bfr_target == self.getParent():
                return True

            try:#...simply try 		
                mc.parent(self.mNode,bfr_target)
                return True
            except:pass

            try:
                mc.parent(self.mNode, bfr_target)
                return True
            except Exception as error:
                raise Exception(error)
            raise Exception("Failed to parent")
        else:#If not, do so to world
            rigging.doParentToWorld(self.mNode)
            return True

    parent = property(getParent, doParent)
    p_parent = property(getParent, doParent)
    
    def getParents(self, asMeta = False, fullPath = False):
        """
        Get all the parents of a given node where the last parent is the top of the heirarchy
        
        :parameters:
            node(str): Object to check
            asMeta(bool): Whether to return data as meta or not
            fullPath(bool): Whether you want long names or not
    
        :returns
            parents(list)
        """ 
        _res = TRANS.parents_get(self,fullPath)
        if _res and asMeta:
            return validateObjListArg(_res)
        return _res  
    
    def getSiblings(self,asMeta = False, fullPath = False):
        """
        Get all the siblings of a given node that share the same heirarchal level
        
        :parameters:
            node(str): Object to check
            asMeta(bool): Whether to return data as meta or not
            fullPath(bool): Whether you want long names or not
    
        :returns
            siblings(list)
        """         
        _res = TRANS.siblings_get(self, fullPath)
        if _res and asMeta:
            return validateObjListArg(_res)
        return _res  
    
    def getDescendents(self, asMeta = False, fullPath = False, type = 'transform'):
        """
        Get all the children of a given node
        
        :parameters:
            node(str): Object to check
            asMeta(bool): Whether to return data as meta or not
            fullPath(bool): Whether you want long names or not
    
        :returns
            children(list)
        """         
        _res = TRANS.descendents_get(self, fullPath,type)
        if _res and asMeta:
            return validateObjListArg(_res)
        return _res 
    getAllChildren = getDescendents
    
    def getChildren(self, asMeta = False, fullPath = True, type = 'transform'):
        """
        Get the children of a given node
        
        :parameters:
            node(str): Object to check
            asMeta(bool): Whether to return data as meta or not
            fullPath(bool): Whether you want long names or not
    
        :returns
            children(list)
        """         
        _res = TRANS.children_get(self, fullPath, type)
        if _res and asMeta:
            return validateObjListArg(_res)
        return _res  
    
    def getShapes(self, asMeta = False, fullPath = True):
        """
        Get all the shapes of a given node where the last parent is the top of the heirarchy
        
        :parameters:
            node(str): Object to check
            asMeta(bool): Whether to return data as meta or not
            fullPath(bool): Whether you want long names or not
    
        :returns
            parents(list)
        """         
        _res = TRANS.shapes_get(self, fullPath)
        if _res and asMeta:
            return validateObjListArg(_res)
        return _res
    
    def getListPathTo(self,target,asMeta = False, fullPath = False):
        """
        Get the list path from one node to another in a given heirarchy
        
        :parameters:
            node(str): Object to check
            asMeta(bool): Whether to return data as meta or not
            fullPath(bool): Whether you want long names or not
    
        :returns
            listPath(list)
        """         
        _res = TRANS.get_listPathTo(self, target, fullPath)
        if _res and asMeta:
            return validateObjListArg(_res)
        return _res   
    
    def isParentTo(self,child):
        """
        Query whether a given node is a child of our mNode
        
        :parameters:
            node(str): Object to check
            child(str): Whether to return data as meta or not
    
        :returns
            status(bool)
        """         
        return TRANS.is_parentTo(self,child)
    isParentOf = isParentTo
    
    def isChildTo(self,parent):
        """
        Query whether a given node is a parent of our mNode
        
        :parameters:
            node(str): Object to check
            child(str): Whether to return data as meta or not
    
        :returns
            status(bool)
        """                 
        return TRANS.is_childTo(self,parent)
    isChildOf = isChildTo
    
    def isVisible(self,checkShapes=False):
        _str_func = 'isVisible'
        try:
            if not OM2:
                raise ValueError("haven't implemented non OM2 version")
            _state = None
            sel2 = OM2.MSelectionList()#...make selection list
            sel2.add(self.mNode)#...add to list
            _state = sel2.getDagPath(0).isVisible()   
            if not checkShapes:
                return _state  
            _states = [_state]
            if checkShapes:
                for s in self.getShapes():
                    sel2.clear()
                    sel2.add(s)
                    _states.append(sel2.getDagPath(0).isVisible())
            if False in _states:
                return False
            return True
            
        except Exception as err:
            log.error(cgmGEN.logString_msg(_str_func,err))
    #========================================================================================================
    #>>> Position/Rotation/Scale ...
    #========================================================================================================      
    #Make Dave happy stuff============================================================================
    def doSnapTo(self,*a,**kws):
        return TRANS.snap(self, *a,**kws)
    def doAim(self,*a,**kws):
        TRANS.aim(self,*a,**kws)
    def doAimAtPoint(self,*a,**kws):
        TRANS.aim_atPoint(self,*a,**kws)    
    
    #...trans ------------------------------------------------------------------------------     
    """def getPosition(self,*a,**kws):
        return TRANS.position_get(self, *a,**kws)"""
    def setPosition(self,*a,**kws):
        return TRANS.position_set(self, *a,**kws)
    
    def getPositionAsEuclid(self,*a,**kws):
        kws['asEuclid'] = True
        return self.getPosition(*a,**kws)
    
    p_position = property(cgmNode.getPosition,setPosition)
    p_positionEuclid = property(getPositionAsEuclid,setPosition)
    
    #...rot ------------------------------------------------------------------------------
    def getOrient(self,*a,**kws):
        return TRANS.orient_get(self,*a,**kws)
    def setOrient(self,*a,**kws):
        return TRANS.orient_set(self,*a,**kws)
    
    p_orient = property(getOrient,setOrient)
    
    def getRotateAxis(self,*a,**kws):
        return TRANS.rotateAxis_get(self,*a,**kws)
    def setRotateAxis(self,*a,**kws):
        return TRANS.rotateAxis_set(self,*a,**kws)
    p_rotateAxis = property(getRotateAxis,setRotateAxis)
        
    #...scale ------------------------------------------------------------------------------
    def getScaleLossy(self,*a,**kws):
        return TRANS.scaleLossy_get(self,*a,**kws)  
    
    #...pivots ------------------------------------------------------------------------------
    def getRotatePivot(self,*a,**kws):
        return TRANS.rotatePivot_get(self,*a,**kws)
    def setRotatePivot(self,*a,**kws):
        return TRANS.rotatePivot_set(self,*a,**kws)
    def getScalePivot(self,*a,**kws):
        return TRANS.scalePivot_get(self,*a,**kws)
    def setScalePivot(self,*a,**kws):
        return TRANS.scalePivot_set(self,*a,**kws)    
    p_rotatePivot = property(getRotatePivot,setRotatePivot)
    p_scalePivot = property(getScalePivot,setScalePivot)
    
    def doPivotsRecenter(self):
        return TRANS.pivots_recenter(self)
    def doPivotsZeroTransform(self):
        return TRANS.pivots_zeroTransform(self)
    
    def getBBSize(self):
        return POS.get_bb_size(self,*a,**kws)    
    def getBBCenter(self):
        return POS.get_bb_center(self,*a,**kws) 
    
    
    #...vectors
    def getAxisVector(self,*a,**kws):
        return TRANS.vector_byAxis(self.mNode, *a,**kws)
    def createVectorLine(self,*a,**kws):
        return TRANS.create_vectorCurveFromObj(self.mNode, *a,**kws)
    def getPositionByAxisDistance(self,*a,**kws):
        #reload(TRANS)
        return TRANS.position_getByAxisDistance(self.mNode, *a,**kws)    
    #...matrix ------------------------------------------------------------------------------
    def getWorldMatrix(self,*a,**kws):
            return TRANS.worldMatrix(self,*a,**kws)     
    p_worldMatrix = property(getWorldMatrix)
    
    
    #...transform data ---------------------------------------------------------------------
    def getTransformDirection(self,*a,**kws):
        return TRANS.transformDirection(self,*a,**kws)    
    def getTransformPoint(self,*a,**kws):
        return TRANS.transformPoint(self,*a,**kws)     
    def getTransformInverseDirection(self,*a,**kws):
        return TRANS.transformInverseDirection(self,*a,**kws)     
    def getTransformInversePoint(self,*a,**kws):
        return TRANS.transformInversePoint(self,*a,**kws)
    
    def dagLock(self,state=True,ignore = None, visibilty= False,keyable = False):
        _attrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
        _ignore = VALID.listArg(ignore)
        if ignore:
            for a in _ignore:
                if a in _attrs:
                    _attrs.remove(a)
        kws = {'lock':True,
               'visible':visibilty,
               'keyable':keyable}
        if not state:
            for k,v in list(kws.items()):
                kws[k] = not v
        return ATTR.set_standardFlags(self.mNode,_attrs, **kws)
    
    #========================================================================================================
    #>>> Get info...
    #========================================================================================================
    """
    def getTransformAttrs(self):
        self.transformAttrs = []
        for attr in 'translate','translateX','translateY','translateZ','rotate','rotateX','rotateY','rotateZ','scaleX','scale','scaleY','scaleZ','visibility','rotateOrder':
            if mc.objExists(self.mNode+'.'+attr):
                self.transformAttrs.append(attr)
        return self.transformAttrs"""

    #def getFamilyDict(self,asMeta = False):
        #""" Get the parent, child and shapes of the object."""
        #return {'parent':self.getParent(asMeta=asMeta),'children':self.getChildren(asMeta=asMeta),'shapes':self.getShapes(asMeta=asMeta)} or {}


    def getPositionOutPlug(self,autoLoc=True):
        #raise ValueError,"Where are we using this?"
        if self.getMayaType() == 'locator':
            return cgmNode(self.getShapes()[0]).getPositionOutPlug()	    
        else:
            buffer = cgmNode.getPositionOutPlug(self)
            if not buffer and autoLoc:
                #See if we have one
                if self.getMessage('positionLoc'):
                    i_loc = cgmObject(self.getMessage('positionLoc')[0])		    
                else:
                    i_loc = self.doLoc()
                    i_loc.parent = self.mNode
                    self.connectChildNode(i_loc,'positionLoc','owner')
                return cgmNode(i_loc.getShapes()[0]).returnPositionOutPlug()	    		    
            else:return buffer

    def getDeformers(self,deformerTypes = 'all',asMeta = False):
        _deformers = []
        _result = []	
        _deformerTypes = VALID.listArg(deformerTypes)
        objHistory = mc.listHistory(self.mNode,pruneDagObjects=True)
        if objHistory:
            for node in objHistory:
                typeBuffer = mc.nodeType(node, inherited=True)
                if 'geometryFilter' in typeBuffer:
                    _deformers.append(node)
        if len(_deformers)>0:
            if _deformerTypes == ['all']:
                _result = _deformers
            else:
                foundDeformers = []
                #Do a loop to figure out if the types are there
                _deformerTypes = [str(d).lower() for d in _deformerTypes]		
                for d in _deformers:
                    if str(VALID.get_mayaType(d)).lower() in _deformerTypes:
                        foundDeformers.append(d)
                if foundDeformers:
                    _result = foundDeformers
        if asMeta:
            return validateObjListArg(_result)
        return _result	

    #=========================================================================  
    # Rigging Functions
    #=========================================================================  
    def doCopyPivot(self,sourceObject,rotatePivot = True, scalePivot = True):
        return RIGGING.copy_pivot(self,sourceObject,rotatePivot,scalePivot)

    def doMatchTransform(self, source=None, rotateOrder=True, rotateAxis=True, rotatePivot=True, scalePivot=True):
        """ Copy the transform from a source object to the current instanced maya object. """
        return RIGGING.match_transform(self, source,rotateOrder,rotateAxis,rotatePivot,scalePivot)

    def doGroup(self,maintain=False, parentTo = True, asMeta = False, typeModifier = None, setClass = False):
        #buffer = rigging.groupMeObject(self.mNode,True,maintain)  
        buffer = TRANS.group_me(self,parentTo,maintain)
        if typeModifier:
            ATTR.store_info(buffer,'cgmTypeModifier',typeModifier)
            self.connectChildNode(buffer,typeModifier + 'Group','source')
        if buffer and asMeta:
            mGrp = validateObjArg(buffer,'cgmObject',setClass=setClass)
            if typeModifier:
                mGrp.doName()
            return mGrp
        return buffer
    
    def doCreateAt(self, create = 'null', copyAttrs = False, connectAs= None, asMeta = True, setClass=False):
        mCreated = validateObjArg( RIGGING.create_at(self.mNode, create), 'cgmObject', setClass=setClass)
        
        if copyAttrs:
            _short = self.mNode
            _target = mCreated.mNode
            _l = mc.listAttr(self.mNode, ud=True) or []
            for attr in _l:
                ATTR.copy_to(_short,attr,_target,attr)
                #cgmAttr(self,attr).doCopyTo(mObj.mNode,attr,connectSourceToTarget = False)	    
            #self.addAttr('cgmType','null',lock=True)
            mCreated.doName()
        elif self.hasAttr('cgmName'):
            mc.rename(mCreated.mNode, self.p_nameBase+'_Transform')
            
        if connectAs:
            self.connectChildNode(mCreated.mNode,connectAs,'source')
            
        if not asMeta:
            return mCreated.mNode
        return mCreated        
        
    
    

    """def doZeroGroup(self,connect=True):
        i_group = validateObjArg(self.doGroup(True), cgmObject)
        i_group.addAttr('cgmTypeModifier','zero')
        if connect:self.connectChildNode(i_group,'zeroGroup','cgmName')
        i_group.doName()	
        return i_group"""

    """def doDuplicateTransform(self,copyAttrs = False):
 
        mObj = cgmObject( rigging.groupMeObject(self.mNode,parent = False)) 
        if copyAttrs:
            _short = self.mNode
            _target = mObj.mNode
            _l = mc.listAttr(self.mNode, ud=True) or []
            for attr in _l:
                ATTR.copy_to(_short,attr,_target,attr)
                #cgmAttr(self,attr).doCopyTo(mObj.mNode,attr,connectSourceToTarget = False)	    
            self.addAttr('cgmType','null',lock=True)
            mObj.doName()
        elif mObj.hasAttr('cgmName'):
            ATTR.delete(mObj,'cgmName')
            mc.rename(mObj.mNode, self.p_nameBase+'_Transform')
        return mObj"""


    """def setDrawingOverrideSettings(self, attrs = None, pushToShapes = False):
        Function for changing drawing override settings on on object

        Keyword arguments:
        attrs -- default will set all override attributes to default settings
                 (dict) - pass a dict in and it will attempt to set the key to it's indexed value ('attr':1}
                 (list) - if a name is provided and that attr is an override attr, it'll reset only that one
        # First make sure the drawing override attributes exist on our instanced object
        for a in drawingOverrideAttrsDict:
            assert mc.objExists('%s.%s'%(self.mNode,a)),"'%s.%s' doesn't exist"%(self.mNode,a)

        #Get what to act on
        targets = [self.mNode]
        if pushToShapes:
            shapes = self.getShapes()
            if shapes:
                targets.extend(shapes)

        for t in targets:
            #Get to business
            if attrs is None or False:
                for a in drawingOverrideAttrsDict:
                    ATTR.set(t,a,drawingOverrideAttrsDict[a])

            if type(attrs) is dict:
                for a in attrs.keys():
                    try:
                        ATTR.set(t,a,attrs[a])
                    except:
                        raise AttributeError, "There was a problem setting '%s.%s' to %s"%(self.mNode,a,drawingOverrideAttrsDict[a])


            if type(attrs) is list:
                for a in attrs:
                    if a in drawingOverrideAttrsDict:
                        try:
                            ATTR.set(self.mNode,a,drawingOverrideAttrsDict[a])
                        except:
                            raise AttributeError, "There was a problem setting '%s.%s' to %s"%(self.mNode,a,drawingOverrideAttrsDict[a])
                    else:
                        log.warning("'%s.%s' doesn't exist"%(t,a)) """
                        
    #========================================================================================================
    #>>> Constraints ...
    #========================================================================================================
    def getConstraintsTo(self, asMeta = False, fullPath = False, **kws):
        buffer = CONSTRAINT.get_constraintsTo(self,fullPath, **kws)
        if asMeta and buffer:
            return validateObjListArg(buffer)
        return buffer

    def getConstraintsFrom(self,asMeta = False, fullPath = False, **kws):
        buffer = CONSTRAINT.get_constraintsFrom(self,fullPath, **kws)
        if asMeta and buffer:
            return validateObjListArg(buffer)
        return buffer

    def getConstrainingObjects(self,asMeta = False, fullPath = False, select = False):
        l_constainingObjects = []	    
        ml_buffer = self.getConstraintsTo(True,fullPath)
        if ml_buffer:
            for mConstraint in ml_buffer:
                targets = CONSTRAINT.get_targets(mConstraint)
                if targets:l_constainingObjects.extend(targets)

        if asMeta and ml_buffer:
            return validateObjListArg(l_constainingObjects)
        if select:
            mc.select(l_constainingObjects)
        return l_constainingObjects

    def getConstraintsByDrivingObject(self,obj,asMeta = False, fullPath = False):
        buffer = CONSTRAINT.get_constraintsByDrivingObject(self.mNode,obj,fullPath)
        if asMeta and buffer:
            return validateObjListArg(buffer)
        return buffer
    
    
    def isConstrainedBy(self,obj):        
        l_constraints = self.getConstraintsTo()
        if not l_constraints:
            return False
        else:
            try:
                obj.mNode
                i_obj = obj
            except:
                i_obj = cgmObject(obj)

            returnList = []
            for c in l_constraints:
                targets = CONSTRAINT.get_targets(c,fullPath=True)
                if i_obj.getLongName() in targets:
                    returnList.append(c)
            if returnList:return returnList	
        return False
        
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmObjectSet - subclass to cgmNode
#=========================================================================  
class cgmController(cgmNode): 
    def __init__(self,node = None, name = 'null',**kws):
        """ 
        Class for control specific functions

        Keyword arguments:
        obj(string)     
        autoCreate(bool) - whether to create a transforum if need be
        """
        
        try:
            if node is None:
                raise ValueError("need an existing controller")
            super(cgmController, self).__init__(node = node, name = name)
            
        except Exception as error:
            raise Exception("cgmController.__init__ fail! | %s"%error)

        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:return
        
    def index_get(self,arg=None):
        if arg:
            return mc.controller(self.mNode,edit=True, idx=arg)
        return mc.controller(self.mNode,q=True, idx=1)
    
    def parent_set(self,mParentController, idx = None, msgConnect=False):
        
        mParentController.cycleWalkSibling = 1
        #try:self.doConnectIn('prepopulate',"{0}.prepopulate".format(mParentController.mNode))
        #except:
        #    pass
        
        if idx is None:
            idx = ATTR.get_nextCompoundIndex(mParentController.mNode,'children') or 0
        
        if msgConnect:
            self.doConnectOut('msg',"{0}.children[{1}]".format(mParentController.mNode,idx))
        else:
            self.doConnectOut('parent',"{0}.children[{1}]".format(mParentController.mNode,idx))
        
    def purge(self):
        _connect = ATTR.get_driver(self.mNode, 'prepopulate')
        if _connect:
            ATTR.break_connection(self.mNode,'prepopulate')
            
        _connect = ATTR.get_driven(self.mNode,'parent')
        if _connect:
            ATTR.break_connection(self.mNode,'parent')
            
    
    
    
    """
    def parent_get(self,arg=None):
        return mc.controller(self.mNode,q=True, parent=1)
    
    def parent_set(self,arg=None):
        if arg:
            return mc.controller(self.mNode,edit=True, parent=arg)
        return mc.controller(self.mNode,edit=True, unparent=1)
    
    def pickWalk(self,direction=None, arg=None):
        if not direction:
            raise ValueError,'direction required'
        d_dir = {'up':'pwu',
                 'down':'pwd',
                 'left':'pwl',
                 'right':'pwr'}
        _arg = arg or 1
        _kws = {d_dir.get(direction):_arg}
        
        if arg:
            return mc.controller(self.mNode,edit=True,**_kws )
        return mc.controller(self.mNode,q=True,**_kws)"""
    
   
        
        
def controller_get(self,verify=False):
    if cgmGEN.__mayaVersion__ < 2018:
        log.warning('Controllers not supported before maya 2018')
        return True
    mController = self.getMessageAsMeta('mController')
    if not mController:
        mc.controller(self.mNode)
        mController = validateObjArg(mc.controller(self.mNode,q=True)[0],mType='cgmController')
        self.connectParentNode(mController,'mController','source')
    if verify:
        mController.doStore('mClass','cgmController')
        return cgmController(mController.mNode)
    return mController
    
class cgmControl(cgmObject): 
    def __init__(self,node = None, name = 'null',**kws):
        """ 
        Class for control specific functions

        Keyword arguments:
        obj(string)     
        autoCreate(bool) - whether to create a transforum if need be
        """
        try: super(cgmControl, self).__init__(node = node, name = name,nodeType = 'transform')
        except Exception as error:
            raise Exception("cgmControl.__init__ fail! | %s"%error)

        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:return

    #>>> Module stuff
    #========================================================================
    def _hasModule(self):
        try:
            if self.getAttr('module'):
                return True
            return False
        except Exception as error:
            log.error("%s._hasModule>> _hasModule fail | %s"%(self.getShortName(),error))	    
            return False

    def _hasSwitch(self):
        try:
            if self.module.rigNull.dynSwitch:
                return True
            return False
        except Exception as error:
            log.error("%s._hasSwitch>> _hasSwitch fail | %s"%(self.getShortName(),error))
            return False	
        
    def controller_get(self,verify=False):
        return controller_get(self,verify)

    #>>> Lock stuff
    #========================================================================    
    def _setControlGroupLocks(self,lock = True, constraintGroup = False):
        _str_func = "_setGroupLocks(%s)"%self.p_nameShort  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75) 
        try:
            l_groups = ['masterGroup','zeroGroup']
            if constraintGroup: l_groups.append('constraintGroup')
            l_attrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
            for g in l_groups:
                try:
                    if self.getMessage(g):
                        mi_group = self.getMessageAsMeta(g)
                        #log.debug("%s >>> found %s | %s"%(_str_func,g,mi_group.p_nameShort))						
                        for a in l_attrs:
                            cgmAttr(mi_group,a,lock=lock)
                except Exception as error:raise Exception("%s >>> | %s"%(g,error))			    
        except Exception as error:
            raise Exception("%s >>> Fail | %s"%(_str_func,error))
    #>>> Aim stuff
    #========================================================================
    def _isAimable(self):
        try:
            if self.hasAttr('axisAim') and self.hasAttr('axisUp'):
                return self._verifyAimable()
            return False
        except Exception as error:
            log.error("cgmControl._verifyAimable>> _verifyAimable fail | %s"%error)
            return False

        if self.axisAim == self.axisUp or self.axisAim == self.axisOut or self.axisUp == self.axisOut:
            log.error("cgmControl._verifyAimable>> Axis settings cannot be the same")	    
            return False
        return True

    def _verifyAimable(self):
        try:
            SNAP.verify_aimAttrs(self.mNode)
            #self.addAttr('axisAim', attrType='enum',enumName = 'x+:y+:z+:x-:y-:z-',initialValue=2, keyable = True, lock = False, hidden = False) 
            #self.addAttr('axisUp', attrType='enum',enumName = 'x+:y+:z+:x-:y-:z-',initialValue=1, keyable = True, lock = False, hidden = False) 
            #self.addAttr('axisOut', attrType='enum', enumName = 'x+:y+:z+:x-:y-:z-',initialValue=0, keyable = True, lock = False, hidden = False) 
            return True
        except Exception as error:
            raise Exception("cgmControl._verifyAimable fail! | %s"%error)	

    def doAim(self,target = None):
        try:
            if not self._isAimable():
                log.warning("Not an aimable control: '%s'"%self.getShortName())
                return False
            i_target = validateObjArg(target,cgmObject,noneValid=True)
            if not i_target:
                log.warning("Invalid aim target : '%s'"%target)
                return False	    

            l_enums = mc.attributeQuery('axisAim', node=self.mNode, listEnum=True)[0].split(':')

            aimVector = dictionary.stringToVectorDict.get("%s"%l_enums[self.axisAim])
            upVector = dictionary.stringToVectorDict.get("%s"%l_enums[self.axisUp])
            outVector = dictionary.stringToVectorDict.get("%s"%l_enums[self.axisOut])

            #log.debug("aimVector: %s"%aimVector)
            #log.debug("upVector: %s"%upVector)
            #log.debug("outVector: %s"%outVector)
            aimConstraintBuffer = mc.aimConstraint(i_target.mNode,self.mNode,maintainOffset = False, weight = 1, aimVector = aimVector, upVector = upVector, worldUpType = 'scene' )
            mc.delete(aimConstraintBuffer)
        except Exception as error:
            raise Exception("%s.doAim fail! | %s"%(self.getShortName(),error))

    #>>> Mirror stuff
    #========================================================================
    def _verifyMirrorable(self):
        _str_func = "%s._verifyMirrorable()"%self.p_nameShort
        #log.debug(">>> %s "%(_str_func) + "="*75)    	
        try:
            if self.hasAttr('mirrorSide'):
                if ATTR.get_type(self.mNode,'mirrorSide')!='enum':
                    ATTR.delete(self.mNode,'mirrorSide')
                    #self.delAttr('mirrorSide')
                    #ATTR.delete()
                    #ATTR.add(self.mNode,'mirrorSide',enumOptions=['Centre','Left','Right'])
                    
            self.addAttr('mirrorSide',attrType = 'enum', enumName = 'Centre:Left:Right', initialValue = 0,keyable = False, hidden = True, lock =False)
            self.addAttr('mirrorIndex',attrType = 'int',keyable = False, hidden = True, lock = True)
            self.addAttr('mirrorAxis',initialValue = '',attrType = 'string',lock=False)
            return True
        except Exception as error:
            raise Exception("%s >>> error: %s"%(_str_func,error)) 

    def isMirrorable(self):
        _str_func = "%s.isMirrorable()"%self.p_nameShort
        #log.debug(">>> %s "%(_str_func) + "="*75)    	
        attrs = ['mirrorSide','mirrorIndex','mirrorAxis']
        try:
            for a in attrs:
                if not self.hasAttr(a):
                    log.error("%s >> lacks attr: '%s'"%(_str_func,a))
                    return False
            """if not self.getMessage('cgmMirrorMatch'):
		log.error("%s >> lacks mirrorMatch: '%s'"%(_str_func,a))
		return False"""
            return True
        except Exception as error:
            raise Exception("%s >>> error: %s"%(_str_func,error)) 

    def doMirrorMe(self,mode = ''):
        _str_func = "%s.doMirrorMe()"%self .p_nameShort
        #log.debug(">>> %s "%(_str_func) + "="*75) 	
        try:
            if not self.isMirrorable():
                return False
            r9Anim.MirrorHierarchy([self.mNode]).mirrorData(mode = mode)
        except Exception as error:
            raise Exception("%s >>> error: %s"%(_str_func,error)) 
    """
    def doPushToMirrorObject2(self,method='Anim'):
        if not self.isMirrorable():
            return False
        log.info(self.i_object.mNode)
        log.info(self.mirrorObject)

        i_mirrorSystem = r9Anim.MirrorHierarchy([self.i_object.mNode,self.mirrorObject])
	#i_mirrorSystem=r9Anim.MirrorHierarchy()
	i_mirrorSystem.makeSymmetrical(self.i_object.mNode,self.mirrorObject)
        """

    def doPushToMirrorObject(self,method='Anim'):
        _str_func = "%s.doMirrorMe()"%self.p_nameShort
        #log.debug(">>> %s "%(_str_func) + "="*75) 	
        try:
            if not self.getMessage('mirrorMatch'):
                return False

            i_mirrorSystem = r9Anim.MirrorHierarchy([self.i_object.mNode,self.mirrorObject])
            i_mirrorObject = cgmObject(self.getMessage('mirrorMatch')[0])

            if method=='Anim':
                transferCall = r9Anim.AnimFunctions().copyKeys
                inverseCall = r9Anim.AnimFunctions.inverseAnimChannels
            else:
                transferCall= r9Anim.AnimFunctions().copyAttributes
                inverseCall = r9Anim.AnimFunctions.inverseAttributes

            transferCall([self.i_object.mNode,i_mirrorObject])
            #inverse the values
            inverseCall(i_mirrorObject,i_mirrorSystem.getMirrorAxis(i_mirrorObject))

            i_mirrorSystem.objs = [self.i_object.mNode,i_mirrorObject]#Overload as it was erroring out
        except Exception as error:
            raise Exception("%s >>> error: %s"%(_str_func,error))
        
    def controlTags_getDat(self):
        if not self.hasAttr('cgmControlTags'):
            self.addAttr('cgmControlTags',attrType='string')
        return self.cgmControlTags or {}
        
    def controlTags_getKeys(self):
        return self.controlTags_getDat().keys()
    
    def controlTags_setKeyValue(self,key,v):
        _d = self.controlTags_getDat()
        _d[key] = v
        self.cgmControlTags = _d
    def controlTags_removeKey(self,key):
        _d = self.controlTags_getDat()
        _d.remove(key)
        self.cgmControlTags = _d

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmObjectSet - subclass to cgmNode
#=========================================================================  
setTypes = {'animation':'animSet',
            'layout':'layoutSet',
            'modeling':'modelingSet',
            'td':'tdSet',
            'fx':'fxSet',
            'lighting':'lightingSet'}

class cgmObjectSet(cgmNode):
    """ 
    Maya Object Set Class handler
    """ 	   
    def __init__(self,setName = None,setType = False,qssState = None,value = None,nameOnCall = False,**kws):
        """ 
        Intializes an set factory class handler

        Keyword arguments:
        setName(string) -- name for the set

        """
        __nodeType = 'objectSet'
        ### input check  
        if setName is not None:
            if mc.objExists(setName):
                assert SEARCH.get_mayaType(setName) == __nodeType,"Not an object set"    
                super(cgmObjectSet, self).__init__(node = setName)  
            else:
                super(cgmObjectSet, self).__init__(node = None,name = setName,nodeType = __nodeType)
        else:
            super(cgmObjectSet, self).__init__(node = setName,nodeType = __nodeType)


        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:return

        #====================================================================================	
        #log.debug("In cgmObjectSet.__init__ setName is '%s'"%setName)
        #log.debug("In cgmObjectSet.__init__ setType is '%s'"%setType) 
        #log.debug("In cgmObjectSet.__init__ qssState is '%s'"%qssState) 

        #self.UNMANAGED.extend(['objectSetType','qssState','mayaSetState'])
        for a in 'objectSetType','qssState','mayaSetState':
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a)   	
        self.mayaSetState = False

        #Maya Set?
        #==============
        for check in ['defaultCreaseDataSet',
                      'defaultObjectSet',
                      'defaultLightSet',
                      'initialParticleSE',
                      'initialShadingGroup',
                      'tweakSet']:
            if check in self.mNode and not self.qssState:
                self.mayaSetState = True

        #Set on call options
        #==============
        if setType:
            self.doSetType(setType)

        if qssState is not None:
            self.makeQss(qssState)

        #Attempt to set a value on call
        if value is not None:           
            self.value = value	
            
        if nameOnCall:
            self.uiPrompt_rename()

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #Qss
    #==============    
    def isQss(self):
        """
        Returns if an object set is a qss set or not
        """
        if mc.sets(self.mNode,q=True,text=True)== 'gCharacterSet':
            return True
        else:
            return False

    def makeQss(self,arg):
        """
        Makes an object set a qss set (if possible)
        """
        assert not self.mayaSetState,"'%s' is a maya set and may not be changed to a qss"%(self.mNode)  

        if arg:
            if mc.sets(self.mNode,q=True,text=True)!= 'gCharacterSet':
                mc.sets(self.mNode, edit = True, text = 'gCharacterSet')
                log.debug("'%s' is now a qss"%(self.mNode))
                self.qssState = True
                return True

        else:
            if mc.sets(self.mNode,q=True,text=True)== 'gCharacterSet':
                mc.sets(self.mNode, edit = True, text = '')            
                log.debug("'%s' is no longer a qss"%(self.mNode)) 
                self.qssState = False	
                return False

    qssState = property(isQss, makeQss)


    #ObjectSet Type
    #==============  
    def getSetType(self):
        """
        Returns the objectSet type as defined by CG Monks
        """
        buffer = SEARCH.get_tagInfo(self.mNode,'cgmType')
        if buffer:
            for k in list(setTypes.keys()):
                if buffer == setTypes[k]:
                    #log.debug('Found match')
                    return k
            else:
                return buffer
        else:return False

    def doSetType(self,setType = None):
        """
        Set a an objectSet's type
        """
        assert type(setType) is str, "Set type must be a string command. '%s'"%setType
        assert not self.isReferenced(), "Cannot change the type of a referenced set"
        assert not self.mayaSetState, "Cannot change type of a maya default set"

        if setType is not None:
            doSetType = setType
            if setType in list(setTypes.keys()):
                doSetType = setTypes.get(setType)
            if SEARCH.get_tagInfo(self.mNode,'cgmType') != doSetType:
                if ATTR.store_info(self.mNode,'cgmType',doSetType):
                    #self.doName()
                    #log.debug("'%s' renamed!"%(self.mNode))  
                    return self.mNode
                else:               
                    log.warning("'%s' failed to store info"%(self.mNode))  
                    return False
        else:
            ATTR.delete(self.mNode,'cgmType')
            #ATTR.delete(self.mNode,'cgmType')
            self.doName()
            log.debug("'%s' renamed!"%(self.mNode))  
            return self.mNode

    objectSetType = property(getSetType, doSetType)

    #Value
    #==============  
    def getMetaList(self):
        return validateObjListArg(self.getList(),noneValid=True)   

    def getList(self,asMeta=False):
        _res = mc.sets(self.mNode, q = True) or []   
        if asMeta:
            return validateObjListArg(_res)
        return _res
    
    def log(self):
        print((cgmGEN._str_subLine))
        _data = self.getList()        

        log.info(cgmGEN._str_baseStart * 2 + " objectSet: {0} | type: {1} | count: {2}".format(self.p_nameShort,self.getSetType(),len(_data)))
        for i,v in enumerate(_data):
            log.info("idx: {0} | obj: {1}".format(i,v))
        log.info(cgmGEN._str_subLine)            

    def doSetList(self, objectList = []):
        """
        Reset the list with the objects provided
        """
        self.purge()
        if type(objectList) is list:
            for o in objectList:
                self.addObj(o)
        else:
            self.addObj(objectList)

        return self.getList()
    
    def deleteSet(self):
        if not self.isReferenced():
            del(self)	    

    value = property(getList, doSetList, deleteSet)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def contains(self,obj):
        _short = NAMES.short(obj)
        for o in self.getList():
            if NAMES.short(o) == _short:
                return True
        return False
    doesContain = contains

    def getParents(self):
        """ 
        Updates the stored data

        Stores basic data, qss state and type

        """
        return mc.listSets(o=self.mNode) or False
    def extend(self,*args):
        """ 
        New store method
        """	
        _str_func = "cgmObjectSet -- %s.extend()"%self.p_nameShort
        log.info(">>> %s "%(_str_func) + "="*75) 	
        if type(args) not in [list,tuple]:
            args = [args]
        elif len(args) == 1:
            args = args[0]

        try:
            for o in args:
                try:o.mNode
                except: o = cgmNode(o)

                if o.mNode not in self.getList():
                    try: mc.sets(o.mNode,add = self.mNode)
                    except Exception as error:
                        raise Exception(" add: %s | error : %s"%(o.p_nameShort,error)) 
                else:log.debug("%s >> already contain : %s"%(_str_func,o.p_nameShort))
        except Exception as error:
            raise Exception("%s >>  error : %s"%(_str_func,error)) 

    def append(self,info,*a,**kws):
        """ 
        Store information to a set in maya via case specific attribute.

        Keyword arguments:
        info(string) -- must be an object in the scene

        """
        _str_func = 'append'
        if not mc.objExists(info):
            log.debug("'%s' doesn't exist. Cannot add to object set."%info)
            return False
        if info == self.mNode:
            return False

        if info in self.getList():
            #log.debug("'%s' is already stored on '%s'"%(info,self.mNode))    
            return
        try:
            mc.sets(info,add = self.mNode)
            #log.debug("'%s' added to '%s'!"%(info,self.mNode))  	
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    addObj = append
    add = append

    def addSelected(self): 
        """ Store selected objects """
        # First look for attributes in the channel box
        SelectCheck = False

        channelBoxCheck = SEARCH.get_selectedFromChannelBox()
        if channelBoxCheck:
            SelectCheck = True
            for item in channelBoxCheck:
                self.add(item)
            return

        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        #log.info("Storing : %s"%toStore)
        for item in toStore:
            self.add(item)
            SelectCheck = True 

        if not SelectCheck:
            log.warning("No selection found")   

    def remove(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        _str_func = 'remove'
        buffer = mc.ls(info,shortNames=True)   
        info = buffer[0]

        # if not self.doesContain(info):
        #     log.debug("'%s' isn't already stored '%s'"%(info,self.mNode))    
        #     return
        try:
            mc.sets(info,rm = self.mNode)    
            log.debug("'%s' removed from '%s'!"%(info,self.mNode))  
            log.info("|{0}| >> removed from objectSet: {1} | data: {2}".format(_str_func,self.p_nameShort,info))   

        except:
            log.error("'%s' failed to remove from '%s'"%(info,self.mNode))    
    removeObj = remove
    def removeSelected(self): 
        """ Store elected objects """
        SelectCheck = False

        # First look for attributes in the channel box
        channelBoxCheck = SEARCH.get_selectedFromChannelBox()
        if channelBoxCheck:
            SelectCheck = True                            
            for item in channelBoxCheck:
                self.remove(item)
            return

        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.remove(item)
                SelectCheck = True                                
            except:
                log.error("Couldn't remove '%s'"%(item)) 

        if not SelectCheck:
            log.warning("No selection found")   

    def purge(self):
        """ Purge all set memebers from a set """
        try:
            mc.sets( clear = self.mNode)
            log.debug("'%s' purged!"%(self.mNode))     
        except:
            log.error("'%s' failed to purge"%(self.mNode)) 

    def copy(self):
        """ Duplicate a set """
        _str_func = 'copy'
        buffer = mc.sets(name = ('%s_Copy'%self.mNode), copy = self.mNode)
        log.debug("'%s' duplicated!"%(self.mNode))
        #log.info("|{0}| >> Appended to objectSet: {1} | data: {2}".format(_str_func,self.p_nameShort,info))   
        log.warning("|{0}| >> New objectSet : {1} | from: {2}".format(_str_func, buffer, self.p_nameShort))   

        for attr in dictionary.cgmNameTags:
            if mc.objExists("%s.%s"%(self.mNode,attr)):
                ATTR.copy_to(self.mNode,attr,buffer)
                
        mDup = cgmObjectSet(buffer)
        if self.isQss():
            mDup.makeQss(True)
        if self.getSetType():
            mDup.doSetType(self.getSetType())
        return mDup


    def select(self):
        """ 
        Select set members or connected objects
        """ 
        if self.getList():
            mc.select(self.getList())
            return

        log.warning("'%s' has no data"%(self.mNode))  
        return False

    def selectSelf(self):
        """ 
        Select set members or connected objects
        """ 
        mc.select(self.mNode,noExpand=True)

    def key(self,*a,**kw):
        """ Select the seted objects """        
        if self.getList():
            mc.select(self.getList())
            mc.setKeyframe(*a,**kw)
            return True

        log.warning("'%s' has no data"%(self.mNode))  
        return False

    def reset(self):
        """ Reset the set objects """        
        if self.getList():
            #mc.select(self.getList())
            #ml_resetChannels.main()  
            for obj in self.getList():
                try:
                    if '.' in obj:
                        l_buffer = obj.split('.')
                        obj = l_buffer[0]
                        attrs = [l_buffer[1]]
                    else:
                        attrs = mc.listAttr(obj, keyable=True, unlocked=True) or False

                    if attrs:
                        for attr in attrs:
                            try:
                                default = mc.attributeQuery(attr, listDefault=True, node=obj)[0]
                                mc.setAttr(obj+'.'+attr, default)
                            except Exception as error:
                                mc.setAttr(obj+'.'+attr, 0)
                                #log.error("'{0}' reset | error: {1}".format(attr,error))   				    
                except Exception as error:
                    log.debug("'{0}' reset fail | obj: '{1}' | error: {2}".format(self.p_nameShort,obj,error))   
            return True

        log.warning("'%s' has no data"%(self.mNode))  
        return False

    def deleteKey(self,*a,**kw):
        """ Select the seted objects """        
        if self.getList():
            mc.select(self.getList())
            mc.cutKey(*a,**kw)
            return True

        log.warning("'%s' has no data"%(self.mNode))  
        return False   

    def deleteCurrentKey(self):
        """ Select the seted objects """        
        if self.getList():
            mc.select(self.getList())
            mel.eval('timeSliderClearKey;')
            return True

        log.warning("'%s' has no data"%(self.mNode))  
        return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmOptionVar - class wrapper for optionVariables in Maya
#=========================================================================
optionVarTypeDict = {'int':['int','i','integer',1,0],
                     'float':['f','float','fl',1.0,0.0],
                     'string':['string','str','s']}  
class cgmOptionVar(object):  
    """ 
    OptionVar Class handler

    """
    def __init__(self,varName = None,varType = None,value = None, defaultValue = None):
        """ 
        Intializes an optionVar class handler

        Keyword arguments:
        varName(string) -- name for the optionVar
        varType(string) -- 'int','float','string' (default 'int')
        value() -- will attempt to set the optionVar with the value
        defaultValue() -- will ONLY use if the optionVar doesn't exist

        """
        #Default to creation of a var as an int value of 0
        if varName is None:
            raise Exception("You must have a optionVar name on call even if it's creating one")
        ### input check
        self.name = varName

        #>>> If it doesn't exist, create, else update
        if not mc.optionVar(exists = self.name):
            if varType is not None:
                requestVarType = self.returnVarTypeFromCall(varType)
            elif defaultValue is not None:
                requestVarType = VALID.get_dataType(defaultValue)                
            elif value is not None:
                requestVarType = VALID.get_dataType(value)
            else:
                requestVarType = 'int'

            if requestVarType:
                self.create(requestVarType)
                if defaultValue is not None:
                    self.initialStore(defaultValue)
                elif value is not None:
                    self.initialStore(value)

            else:
                log.warning("'%s' is not a valid variable type"%varType)

        else:               
            self.update(varType)

            #Attempt to set a value on call
            if value is not None:           
                self.value = value

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #value
    #==============    
    def getValue(self):
        if mc.optionVar(exists = self.name):
            return mc.optionVar(q=self.name)
        else:
            #log.debug("'%s' no longer exists as an option var!"%self.name)
            raise Exception("'%s' no longer exists as an option var!"%self.name)

    def setValue(self,value):
        if type(value) is list or type(value) is tuple:
            self.__init__(self.name,self.varType,value = value[0])#Reinitialize
            if len(value) > 1:
                for v in value[1:]:
                    self.append(v)
        else:
            if self.varType == 'int':
                try:
                    mc.optionVar(iv = (self.name,int(float(value))))
                except:
                    log.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))

            elif self.varType == 'float':
                try:
                    mc.optionVar(fv = (self.name,float(value)))

                except:
                    log.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))

            elif self.varType == 'string':
                try:
                    mc.optionVar(sv = (self.name,str(value)))
                except:
                    log.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))
        object.__setattr__(self, self.name, value)
        log.debug(self)

    def uiPrompt_value(self,title = None):
        if title is None:
            _title = 'Set {0}'.format(self.name)
        else:_title = title
        result = mc.promptDialog(title=_title,
                                 message='Current: {0} | type: {1}'.format(self.value,self.varType),
                                 button=['OK', 'Cancel'],
                                 text = self.value,
                                 defaultButton='OK',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')
        if result == 'OK':
            _v =  mc.promptDialog(query=True, text=True)
            self.value = _v
        else:
            log.error("|{0}| value change cancelled".format(self.name))
            return False 
            
    def purge(self):
        """ 
        Purge an optionVar from maya
        """
        try:
            mc.optionVar(remove = self.name)     
        except:
            log.warning("'%s' doesn't exist"%(self.name))

    value = property(getValue, setValue, purge)#get,set,del

    #varType
    #==============    
    def getType(self):
        dataBuffer = mc.optionVar(q=self.name)                                         
        typeBuffer = VALID.get_dataType(dataBuffer) or 'string'
        if not typeBuffer:
            log.warning("I don't know what this is!")
            return False
        return typeBuffer


    def setType(self,varType = None):
        if not mc.optionVar(exists = self.name):
            if varType is not None:
                requestVarType = self.returnVarTypeFromCall(varType)             
            else:
                log.warning("Not sure what '%s' is, making as int"%varType)
                requestVarType = 'int'

            if requestVarType:
                self.create(requestVarType)	    
            else:
                log.warning("'%s' is not a valid variable type"%varType) 
        else:
            self.update(varType)

    varType = property(getType, setType)

    def __repr__(self):
        try:return "{0}(var: {1}, type: {2}, value: {3})".format(self.__class__, self.name, self.getType(), self.value)
        except:return self
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    def initialStore(self,value):
        if type(value) is list:
            self.extend(value)
        else:
            if type(self.value) is list:
                self.append(value)                            
            else:
                if value != self.value:
                    self.setValue(value)

    def returnVarTypeFromCall(self, varTypeCheck):    
        for option in list(optionVarTypeDict.keys()):
            if varTypeCheck in optionVarTypeDict.get(option):
                return option
        return 'int'

    def update(self,varType = None):
        """ 
        Update the data in case some other process has changed on optionVar
        """
        dataBuffer = self.value 
        requestVarType = self.returnVarTypeFromCall(varType)

        if not mc.optionVar(exists = self.name):
            if requestVarType:
                self.create(self.form)
                return
            else:
                return log.warning("'%s' is not a valid variable type"%varType)  

        else:
            #If it exists, first check for data buffer
            #log.info(dataBuffer)
            typeBuffer = VALID.get_dataType(dataBuffer) or False
            if not typeBuffer:
                #log.debug('Changing to int!')
                typeBuffer = 'int'

            if varType is not None:    
                if typeBuffer == requestVarType:
                    #log.debug("Checks out")
                    return                
                else:
                    log.debug("Converting optionVar type...")
                    self.create(requestVarType)
                    if dataBuffer is not None:
                        #log.debug("Attempting to set with: %s"%dataBuffer)
                        self.value = dataBuffer
                        #log.debug("Value : %s"%self.value)
                    return  

    def create(self,doType):
        """ 
        Makes an optionVar.
        """
        #log.debug( "Creating '%s' as '%s'"%(self.name,doType) )

        if doType == 'int':
            mc.optionVar(iv=(self.name,0))
        elif doType == 'float':
            mc.optionVar(fv=(self.name,0))
        elif doType == 'string':
            mc.optionVar(sv=(self.name,''))
        elif doType == 'bool':
            mc.optionVar(iv=(self.name,0))
        elif doType == 'data':
            mc.optionVar(sv=(self.name,''))

    def clear(self):
        """
        Clear the data from an option var
        """
        doName = self.name
        doType = self.varType
        self.purge()
        self.__init__(doName,doType)

    def append(self,value): 
        if type(self.value) is list or type(self.value) is tuple:
            if value in self.value:
                return log.debug("'%s' already added"%(value))

        if self.varType == 'int':
            try:
                mc.optionVar(iva = (self.name,int(value)))
                #log.debug("'%s' added to '%s'"%(value,self.name))

            except:
                log.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))

        elif self.varType == 'float':
            try:
                mc.optionVar(fva = (self.name,float(value)))
                #log.debug("'%s' added to '%s'"%(value,self.name))

            except:
                log.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))

        elif self.varType == 'string':
            try:
                mc.optionVar(sva = (self.name,str(value)))
                for i in "",'':
                    if i in self.value:
                        self.remove(i)

                #log.debug("'%s' added to '%s'"%(value,self.name))           

            except:
                log.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.varType))
                
    def append_recent(self,arg):
        _str_func = 'cgmOptionVar.append_recent'
        log.debug(cgmGEN.logString_start(_str_func))
        
        if type(self.value) is list:
            if arg not in self.value:
                l_buffer = self.value
                l_buffer.insert(0,arg)
            else:
                return False
                
        else:
            if arg != self.value:
                l_buffer = [arg,self.value]
            else:
                return False
        
        if len(l_buffer) > 5:
            l_buffer = l_buffer[:5]        
            
        self.value =  l_buffer

    def remove(self,value):
        if value in self.value:
            try:         
                i = self.value.index(value)
                mc.optionVar(removeFromArray = (self.name,i))
                self.update(self.form)
                #log.debug("'%s' removed from '%s'"%(value,self.name))
            except:
                log.debug("'%s' failed to remove '%s'"%(value,self.name))
        else:
            log.debug("'%s' wasn't found in '%s'"%(value,self.name))

    def removeIndex(self,value):
        if type(self.getValue()) is list and value < len(self.getValue()):
            try:         
                mc.optionVar(removeFromArray = (self.name,value))
                self.update(self.form)
                #log.debug("'%s' removed from '%s'"%(value,self.name))
            except:
                log.debug("'%s' failed to remove '%s'"%(value,self.name))
        else:
            log.debug("'%s' isn't a list or is smaller than the given value of %i"%(self.name,value))

    def extend(self,valuesList):
        assert type(valuesList) is list,"'%s' not a list"%(valuesList)

        for v in valuesList:
            if type(self.value) is list:
                if v not in self.value:
                    self.append(v)
            else:
                if v != self.value:
                    self.append(v)

    def toggle(self):
        """
        Toggles an int type variable
        """
        assert self.varType == 'int',"'%s' not an int type var"%(self.name)

        self.value = not self.value
        #log.debug("'%s':%s"%(self.name,self.value))


    def select(self):
        """
        Attempts to select the items of a optionVar buffer
        """
        try:
            selectList = []
            if self.value:
                for item in self.value:
                    if mc.objExists(item):
                        if '.' in item:
                            buffer = mc.ls(item,o=True)
                            if mc.objExists(buffer[0]):
                                selectList.append(buffer[0])
                        else:
                            selectList.append(item)
    
            if selectList:
                mc.select(selectList)
            else:
                log.warning("'%s' is empty!"%self.name)
        except Exception as err:
            return log.error("cgmOptionVar.select fail | {0}".format(err))
        
    def existCheck(self):
        """
        Removes non existing items
        """
        for item in self.value:
            if not mc.objExists(item):
                self.remove(item)
                log.debug("'%s' removed from '%s'"%(item,self.name))
                
    def report(self):
        """
        Simple report from value
        """
        _value = self.value
        log.info(cgmGEN._str_baseStart * 2 + " OptionVar: {0} | type: {1} | value: {2}".format(self.name,self.varType,self.value))
        if issubclass(type(_value),list):
            for i,v in enumerate(_value):
                log.info("idx: {0} | {1}".format(i,v))
        log.info(cgmGEN._str_subLine)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmBuffer - replacement for a multimessage attribute. Stores a list to object
#=========================================================================
class cgmBufferNode(cgmNode):
    def __init__(self,node = None, name = None, value = None, nodeType = 'network', overideMessageCheck = False, **kws):
        """ 
        Replacement for a multimessage attribute when you want to be able to link to an attr

        Keyword arguments:
        setName(string) -- name for the set

        To Do:
        Add extend,append, replace, remove functions
        """
        ### input check  
        #log.debug("In cgmBuffer.__init__ node is '%s'"%node)
        #raise DeprecationWarning,"Not using this anymore..."

        super(cgmBufferNode, self).__init__(node = node,name = name,nodeType = nodeType) 

        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:return

        #====================================================================================

        #self.UNMANAGED.extend(['l_buffer','d_buffer','value','d_indexToAttr','_kw_overrideMessageCheck'])
        for a in 'l_buffer','d_buffer','value','d_indexToAttr','_kw_overrideMessageCheck':
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a)  	
        self._kw_overrideMessageCheck = overideMessageCheck


        if not self.isReferenced():
            self.__verify__()	    
            if not self.__verify__():
                raise Exception("cgmBufferNode.__init__>> failed to verify : '%s'!"%self.getShortName())
            if value is not None:
                self.value = value	
        self.updateData()


    def __verify__(self,**kws):
        #log.debug("cgmBufferNode>>> in %s.__verify__()"%self.getShortName())
        self.addAttr('messageOverride',initialValue = self._kw_overrideMessageCheck,attrType = 'bool',lock=True)
        return True   
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #value
    #==============    
    def getValue(self):
        return self.l_buffer

    #@cgmGEN.TimerDebug   
    def setValue(self,value):
        if self.isReferenced():
            log.warning('This function is not designed for referenced buffer nodes')
            return False
        self.purge()#wipe it to reset it
        if type(value) is list or type(value) is tuple:
            for i in value:
                self.store(i)
        else:
            self.store(value) 

    value = property(getValue, setValue)#get,set

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     
    def returnNextAvailableCnt(self):
        """ Get's the next available item number """        
        return ATTR.get_nextAvailableSequentialAttrIndex(self.mNode,'item')


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def updateData(self,*a,**kw):
        """ Updates the stored data """
        self.l_buffer = []
        self.d_buffer = {}
        self.d_indexToAttr = {}
        l_itemAttrs = []
        d_indexToAttr = {}
        for attr in self.getAttrs(ud=True):
            if 'item_' in attr:
                index = int(attr.split('item_')[-1])
                dataBuffer = ATTR.get(self.mNode,attr)
                data = dataBuffer
                self.d_buffer[attr] = data
                self.d_indexToAttr[index] = attr
                self.l_buffer.append(data)

        #verify data order
        for key in list(self.d_indexToAttr.keys()):
            self.l_buffer[key] = self.d_buffer[self.d_indexToAttr[key]]

    def rebuild(self,*a,**kw):
        """ Rebuilds the buffer data cleanly """ 
        if self.isReferenced():
            log.warning('This function is not designed for referenced buffer nodes')
            return False	
        listCopy = copy.copy(self.l_buffer)
        self.value = listCopy
        self.updateData()

    def store(self,info,index = None,allowDuplicates = True,*a,**kw):
        """ 
        Store information to an object in maya via case specific attribute.

        Keyword arguments:
        info(string) -- must be an object in the scene

        """
        if self.isReferenced():
            log.warning('This function is not designed for referenced buffer nodes')
            return False

        if not mc.objExists(info) and self.messageOverride != True:
            log.warning("'%s' doesn't exist"%info)
            return

        if not allowDuplicates and info in self.l_buffer:
            #log.debug("'%s' is already stored on '%s'"%(info,self.mNode))    
            return


        if index is not None and index < len(self.l_buffer):
            cnt = index
        else:
            cnt = self.returnNextAvailableCnt()
        if self.messageOverride:
            cgmAttr(self.mNode,('item_'+str(cnt)),value = info,lock=True)	    
        else:
            attributes.storeInfo(self.mNode,('item_'+str(cnt)),info)	    

        #attributes.storeInfo(self.mNode,('item_'+str(cnt)),info,overideMessageCheck = self.messageOverride)
        self.updateData()
        #self.l_buffer.append(info)
        #self.d_buffer['item_'+str(cnt)] = info

    def doStoreSelected(self): 
        """ Store elected objects """
        # First look for attributes in the channel box
        if self.isReferenced():
            log.warning('This function is not designed for referenced buffer nodes')
            return False

        channelBoxCheck = SEARCH.get_selectedFromChannelBox()
        if channelBoxCheck:
            for item in channelBoxCheck:
                self.store(item)
            return

        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.store(item)
            except:
                log.warning("Couldn't store '%s'"%(item))     

    def remove(self,info,*a,**kw):
        """ Store information to an object in maya via case specific attribute. """
        if self.isReferenced():
            log.warning('This function is not designed for referenced buffer nodes')
            return False

        if info not in self.l_buffer:
            log.warning("'%s' isn't already stored '%s'"%(info,self.mNode))    
            return

        for key in list(self.d_buffer.keys()):
            if self.d_buffer.get(key) == info:
                ATTR.delete(self.mNode,key)
                self.l_buffer.remove(info)
                self.d_buffer.pop(key)

        log.warning("'%s' removed!"%(info))  

        self.updateData()

    def doRemoveSelected(self): 
        """ Store elected objects """
        # First look for attributes in the channel box
        if self.isReferenced():
            log.warning('This function is not designed for referenced buffer nodes')
            return False

        channelBoxCheck = SEARCH.get_selectedFromChannelBox()
        if channelBoxCheck:
            for item in channelBoxCheck:
                self.remove(item)
            return

        # Otherwise add the objects themselves
        toStore = mc.ls(sl=True,flatten=True) or []
        for item in toStore:
            try:
                self.remove(item)
            except:
                log.warning("Couldn't remove '%s'"%(item)) 

    def purge(self):
        """ Purge all buffer attributes from an object """
        if self.isReferenced():
            log.warning('This function is not designed for referenced buffer nodes')
            return False

        userAttrs = mc.listAttr(self.mNode,userDefined = True) or []
        for attr in userAttrs:
            if 'item_' in attr:
                ATTR.delete(self.mNode,attr)
                #log.debug("Deleted: '%s.%s'"%(self.mNode,attr))  

        self.l_buffer = []
        self.d_buffer = {}        

    def select(self):
        """ 
        Select the buffered objects. Need to work out nested searching better
        only goes through two nexts now
        """        
        if self.l_buffer:
            selectList = []
            # Need to dig down through the items
            for item in self.l_buffer:
                if SEARCH.get_tagInfo(item,'cgmType') == 'objectBuffer':
                    tmpFactory = cgmBuffer(item)
                    selectList.extend(tmpFactory.l_buffer)

                    for item in tmpFactory.l_buffer:
                        if SEARCH.get_tagInfo(item,'cgmType') == 'objectBuffer':
                            subTmpFactory = cgmBuffer(item)   
                            selectList.extend(subTmpFactory.l_buffer)

                else:
                    selectList.append(item)

            mc.select(selectList)
            return

        log.warning("'%s' has no data"%(self.mNode))  
        return False

    def key(self,*a,**kw):
        """ Select the buffered objects """        
        if self.l_buffer:
            mc.select(self.l_buffer)
            mc.setKeyframe(*a,**kw)
            return True

        log.warning("'%s' has no data"%(self.mNode))  
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmAttr - separate class
#=========================================================================    
class cgmAttr(object):
    """ 
    Initializes a maya attribute as a class obj. 9/10 times, you can just use a cgmNode with innate attr handling
    """
    attrTypesDict = {'message':['message','msg','m'],
                     'double':['float','fl','f','doubleLinear','doubleAngle','double','d'],
                     'string':['string','s','str'],
                     'long':['long','int','i','integer'],
                     'bool':['bool','b','boolean'],
                     'enum':['enum','options','e'],
                     'double3':['vector','vec','v','double3','d3']}    

    def __init__(self,objName = None,attrName = None,attrType = False,value = None,enum = None,initialValue = None,lock = None,keyable = None, hidden = None, minValue = None, maxValue = None, defaultValue = None,*a, **kw):
        """
        Asserts attribute's existance then initializes. If 
        an existing attribute name on an object is called and the attribute type is different,it converts it. All functions
        ignore locks on attributes and will act when called regardless of target settings

        :parameters:
            obj | string/metaNode
        	Att's object
            attrName | string
                name for an attribute to initialize
            attrType | string
                must be valid attribute type
            value | variable
                set value on call or creation
            enum | mayaEnumCommand arg
                What enum options to use
            initialValue | variable
                Only sets on attr creation, not existing
            ...most other flags

        :returns
            cgmAttr instance

        """        
        ### input check
        #>>> Initialization ==================   
        try: 
            objName.mNode
            self.obj = objName
        except:
            assert mc.objExists(objName) is True, "'%s' doesn't exist" %objName
            self.obj = cgmNode(objName)	    

        #if attrType:attrType = attributes.validateRequestedAttrType(attrType)
        if attrType:attrType = ATTR.validate_attrTypeName(attrType)

        #value/attr type logic check
        #==============  
        if enum is not None:
            self.attrType = attrType = 'enum'
        elif value and attrType is False and not self.obj.hasAttr(attrName):
            if type(value) is list:
                for o in value:
                    if mc.objExists(o):
                        self.attrType = 'message'		
                        log.debug('Multi message mode!')
                        break
                    self.attrType = 'double3'#Need better detection here for json and what not
            elif mc.objExists(value):
                #log.debug("'%s' exists. creating as message."%value)
                self.attrType = 'message'		
            else:
                dataReturn = VALID.get_dataType(value)
                #log.debug("Trying to create attr of type '%s'"%dataReturn)
                self.attrType =  ATTR.validate_attrTypeName(dataReturn)
        else:
            self.attrType =  ATTR.validate_attrTypeName(attrType)

        self.attr = attrName
        initialCreate = False

        # If it exists we need to check the type. 
        if mc.objExists('%s.%s'%(self.obj.mNode,attrName)):
            #log.info("'%s.%s' exists"%(self.obj.mNode,attrName))
            currentType = mc.getAttr('%s.%s'%(self.obj.mNode,attrName),type=True)
            #log.info("Current type is '%s'"%currentType)
            if not ATTR.validate_attrTypeMatch(self.attrType,currentType) and self.attrType is not False:
                if self.obj.isReferenced():
                    log.error("'%s' is referenced. cannot convert '%s' to '%s'!"%(self.obj.mNode,attrName,attrType))                   
                self.doConvert(self.attrType)             
            else:
                self.attr = attrName
                self.attrType = currentType   
        else:
            try:
                _type = self.attrType
                if not _type:
                    _type = 'string'
                ATTR.add(self.obj.mNode,attrName,_type)
                """ if self.attrType == False:
                     self.attrType = 'string'
                     attributes.addStringAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                 elif self.attrType == 'double':
                     attributes.addFloatAttributeToObject(self.obj.mNode,attrName,*a, **kw)
                 elif self.attrType == 'string':
                     attributes.addStringAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                 elif self.attrType == 'long':
                     attributes.addIntegerAttributeToObj(self.obj.mNode,attrName,*a, **kw) 
                 elif self.attrType == 'double3':
                     attributes.addVectorAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                 elif self.attrType == 'enum':
                     attributes.addEnumAttrToObj(self.obj.mNode,attrName,*a, **kw)
                 elif self.attrType == 'bool':
                     attributes.addBoolAttrToObject(self.obj.mNode,attrName,*a, **kw)
                 elif self.attrType == 'message':
                     attributes.addMessageAttributeToObj(self.obj.mNode,attrName,*a, **kw)
                 else:
                     log.error("'%s' is an unknown form to this class"%(self.attrType))"""
                initialCreate = True

            except Exception as error:
                log.error("addAttr>>Failure! '%s' failed to add '%s' | type: '%s'"%(self.obj.mNode,attrName,self.attrType))
                raise Exception(error)                  

        if enum:
            try:
                self.setEnum(enum)
            except:
                log.error("Failed to set enum value of '%s'"%enum)        

        if initialValue is not None and initialCreate:
            self.set(initialValue)

        elif value is not None:
            self.set(value)

        if minValue is not None:
            try:
                self.p_minValue = minValue
            except:
                log.error("addAttr>>minValue on call Failure! %s"%minValue)

        if maxValue is not None:
            try:
                self.p_maxValue = maxValue
            except:
                log.error("addAttr>>minValue on call Failure! %s"%maxValue)

        if defaultValue is not None:
            try:
                self.p_defaultValue = defaultValue
            except:
                log.error("addAttr>>minValue on call Failure! %s"%defaultValue)

        if keyable is not None:
            self.doKeyable(keyable)   

        if hidden is not None:
            self.doHidden(hidden)

        if lock is not None:
            self.doLocked(lock)

        #log.debug("'%s' initialized. Value: '%s'"%(self.p_combinedName,self.value))
    def __repr__(self):
        try:return "{0}(node: '{1}', attr: '{2}')".format(self.__class__, self.obj.p_nameShort, self.attr)
        except:return self    
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Properties
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    #value
    #==============    
    def set(self,value,*a, **kw):
        """ 
        Set attr value based on attr type

        Keyword arguments:
        value(varied)   
        *a, **kw
        """
        try:	
            if self.obj.hasAttr(self.attr):
                if self.attrType == 'message':
                    self.doStore(value)	    
                elif self.getChildren():
                    #log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedName,"','".join(self.getChildren())))
                    for i,c in enumerate(self.getChildren()):
                        try:
                            cInstance = cgmAttr(self.obj.mNode,c)                        
                            if type(value) is list and len(self.getChildren()) == len(value): #if we have the same length of values in our list as we have children, use them
                                cInstance.value = value[i]
                            else:    
                                ATTR.set(cInstance.obj.mNode,cInstance.attr, value, *a, **kw)
                        except Exception as error:
                            fmt_args = [c,error]
                            s_errorMsg = "On child: {0}| error: {1}".format(*fmt_args)			    
                            raise Exception(s_errorMsg)
                else:
                    ATTR.set(self.obj.mNode,self.attr, value, *a, **kw)	
            object.__setattr__(self, self.attr, self.value)
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, value, error]
            s_errorMsg = "{0}.{1}.set() | Value: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)        

    def get(self,*a, **kw):
        """ 
        Get and store attribute value based on attr type

        Keyword arguments:
        *a, **kw
        """    
        try:
            if self.attrType == 'message':
                return ATTR.get_message(self.obj.mNode,self.attr)
                #return attributes.returnMessageData(self.obj.mNode,self.attr)
            else:
                return ATTR.get(self.obj.mNode,self.attr)
        except Exception as error:
            log.warning("'%s.%s' failed to get | %s"%(self.obj.mNode,self.attr,error))

    def doDelete(self):
        """ 
        Deletes an attribute
        """   
        try:
            ATTR.delete(self.obj.mNode,self.attr)
            log.warning("'%s.%s' deleted"%(self.obj.mNode,self.attr))
            del(self)

        except:
            log.error("'%s.%s' failed to delete"%(self.obj.mNode,self.attr))  

    value = property(get, set, doDelete)#get,set,del
    p_value = property(get, set, doDelete)#get,set,del

    #>>> Property - p_combinedName ==================             
    def asCombinedName(self):
        return '%s.%s'%(self.obj.mNode,self.attr)  
    p_combinedName = property(asCombinedName)

    def asCombinedShortName(self):
        return '%s.%s'%(self.obj.getShortName(),self.attr)  
    p_combinedShortName = property(asCombinedShortName) 

    def asCombinedLongName(self):
        return '{0}.{1}'.format(self.obj.p_nameLong,self.attr)  
    p_combinedLongName = property(asCombinedLongName)

    #>>> Property - p_nameLong ================== 
    def getEnum(self):
        #attributeQuery(attr, node=self.mNode, listEnum=True)[0].split(':')
        return mc.attributeQuery(self.attr, node = self.obj.mNode, listEnum=True)[0].split(':') or False	
    def setEnum(self,enumCommand):
        """ 
        Set the options for an enum attribute

        Keyword arguments:
        enumCommand(string) -- 'off:on', 'off=0:on=2', etc
        """   
        fmt_args = [self.obj.p_nameShort, self.p_nameLong, enumCommand]
        s_baseMsg = "{0}.{1}.setEnum() | enumCommand: {2}".format(*fmt_args)	
        try:
            if self.attrType == 'enum':
                if ":".join(self.p_enum) != VALID.stringListArg(enumCommand):
                    mc.addAttr ((self.obj.mNode+'.'+self.attr), e = True, at=  'enum', en = enumCommand)
                    #log.debug("'%s.%s' has been updated!"%(self.obj.mNode,self.attr))
                else:log.info("%s | already set"%s_baseMsg)
            else:
                log.warning("%s | not an enum. Invalid call"%(s_baseMsg))
        except Exception as error:
            fmt_args = [s_baseMsg, error]
            s_errorMsg = "{0} | error: {1}".format(*fmt_args)	    
            log.error(s_errorMsg)     

    p_enum = property (getEnum,setEnum)

    #==========================================  
    # Basic flag properties
    #==========================================   
    #>>> Property - p_locked ==================    
    def isLocked(self):
        return mc.getAttr(self.p_combinedName, lock=True)

    def doLocked(self,arg = True):
        """ 
        Set lock state of an attribute

        Keyword arguments:
        arg(bool)
        """ 
        try:
            arg =  VALID.boolArg(arg)
            if arg:
                if self.getChildren():
                    #log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedShortName,"','".join(self.getChildren())))
                    for c in self.getChildren():
                        cInstance = cgmAttr(self.obj.mNode,c)                                            
                        if not cInstance.p_locked:
                            mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,lock = True) 
                            #log.debug("'%s.%s' locked!"%(cInstance.obj.mNode,cInstance.attr))

                elif not self.p_locked:
                    mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,lock = True) 
                    #log.debug("'%s.%s' locked!"%(self.obj.mNode,self.attr))

            else:
                if self.getChildren():
                    #log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedShortName,"','".join(self.getChildren())))
                    for c in self.getChildren():
                        cInstance = cgmAttr(self.obj.mNode,c)                                            
                        if cInstance.p_locked:
                            mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,lock = False) 
                            #log.debug("'%s.%s' unlocked!"%(cInstance.obj.mNode,cInstance.attr))

                elif self.p_locked:
                    mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,lock = False)           
                    #log.debug("'%s.%s' unlocked!"%(self.obj.mNode,self.attr))
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, arg, error]
            s_errorMsg = "{0}.{1}.doLocked() | arg: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)   
    p_locked = property (isLocked,doLocked)
    p_lock = property (isLocked,doLocked)

    #>>> Property - p_hidden ================== 
    def isHidden(self):
        hidden = not mc.getAttr(self.p_combinedName,channelBox=True)
        if self.p_keyable:
            hidden = mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, hidden=True)	
        return hidden
    def doHidden(self,arg = True):
        """ 
        Set hidden state of an attribute

        Keyword arguments:
        arg(bool)
        """ 
        try:
            arg =  VALID.boolArg(arg)
            if arg:
                if self.getChildren():
                    #log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedShortName,"','".join(self.getChildren())))
                    for c in self.getChildren():
                        cInstance = cgmAttr(self.obj.mNode,c)                                            
                        if not cInstance.p_hidden:
                            if cInstance.p_keyable:
                                cInstance.doKeyable(False)
                            mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,channelBox = False) 
                            #log.debug("'%s.%s' hidden!"%(cInstance.obj.mNode,cInstance.attr))

                elif not self.p_hidden:
                    if self.p_keyable:
                        self.doKeyable(False)
                    mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,channelBox = False) 
                    #log.debug("'%s.%s' hidden!"%(self.obj.mNode,self.attr))

            else:
                if self.getChildren():
                    #log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedShortName,"','".join(self.getChildren())))
                    for c in self.getChildren():
                        cInstance = cgmAttr(self.obj.mNode,c)                                            
                        if cInstance.p_hidden:
                            mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,channelBox = True) 
                            #log.debug("'%s.%s' unhidden!"%(cInstance.obj.mNode,cInstance.attr))

                elif self.p_hidden:
                    mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,channelBox = True)           
                    #log.debug("'%s.%s' unhidden!"%(self.obj.mNode,self.attr))
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, arg, error]
            s_errorMsg = "{0}.{1}.doHidden() | arg: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)   	
    p_hidden = property (isHidden,doHidden) 

    #>>> Property - p_locked ==================
    def isKeyable(self):
        return mc.getAttr(self.p_combinedName,keyable=True)
    def doKeyable(self,arg = True):
        """ 
        Set keyable state of an attribute

        Keyword arguments:
        arg(bool)
        """         
        KeyableTypes = ['long','float','bool','double','enum','double3','doubleAngle','doubleLinear']  
        fmt_args = [self.obj.p_nameShort, self.p_nameLong, arg]
        s_baseMsg = "{0}.{1}.doKeyable() | arg: {2}".format(*fmt_args)		
        try:
            arg =  VALID.boolArg(arg)

            if self.attrType not in KeyableTypes:
                #log.debug("'%s' not a keyable attrType"%self.attrType)
                return False

            if arg:
                if self.getChildren():
                    #log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedShortName,"','".join(self.getChildren())))
                    for c in self.getChildren():
                        cInstance = cgmAttr(self.obj.mNode,c)                                            
                        if not cInstance.p_keyable:
                            mc.setAttr(cInstance.p_combinedName,e=True,keyable = True) 
                            #log.debug("'%s.%s' keyable!"%(cInstance.obj.mNode,cInstance.attr))
                            cInstance.p_hidden = False

                elif not self.p_keyable:
                    mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,keyable = True) 
                    #log.debug("'%s.%s' keyable!"%(self.obj.mNode,self.attr))
                    self.p_hidden = False
            else:
                if self.getChildren():
                    #log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedShortName,"','".join(self.getChildren())))
                    for c in self.getChildren():
                        cInstance = cgmAttr(self.obj.mNode,c)                                            
                        if cInstance.p_keyable:
                            mc.setAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,keyable = False) 
                            #log.debug("'%s.%s' unkeyable!"%(cInstance.obj.mNode,cInstance.attr))
                            if not mc.getAttr(cInstance.p_combinedName,channelBox=True):
                                cInstance.doHidden(False)                

                elif self.p_keyable:
                    mc.setAttr((self.obj.mNode+'.'+self.attr),e=True,keyable = False)           
                    #log.debug("'%s.%s' unkeyable!"%(self.obj.mNode,self.attr))
                    if not mc.getAttr(self.p_combinedName,channelBox=True):
                        self.doHidden(False)  
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, arg, error]
            s_errorMsg = "{0}.{1}.doKeyable() | arg: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)   
    p_keyable = property (isKeyable,doKeyable) 

    #==========================================    
    # Name flag properties
    #==========================================       
    #>>> Property - p_nameAlias ===============
    def getAlias(self):
        if mc.aliasAttr(self.p_combinedName,q=True):
            return mc.aliasAttr(self.p_combinedName,q=True) 
        return None

    def doAlias(self,arg):
        """ 
        Set the alias of an attribute

        Keyword arguments:
        arg(string) -- name you want to use as an alias
        """   
        fmt_args = [self.obj.p_nameShort, self.p_nameLong, arg]
        s_baseMsg = "{0}.{1}.doAlias() | arg: {2}".format(*fmt_args)		
        try:
            arg = VALID.stringArg(arg)
            if arg:
                try:
                    if arg != self.p_nameAlias:
                        return mc.aliasAttr(arg,self.p_combinedName)
                    else:log.debug("'%s.%s' already has that alias!"%(self.obj.getShortName(),self.attr))
                except:
                    log.warning("'%s.%s' failed to set alias of '%s'!"%(self.obj.mNode,self.attr,arg))

            else:
                if self.p_nameAlias:
                    self.attr = self.p_nameLong                
                    mc.aliasAttr(self.p_combinedName,remove=True)
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, arg, error]
            s_errorMsg = "{0}.{1}.doAlias() | arg: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)   
    p_nameAlias = property (getAlias,doAlias)

    #>>> Property - p_nameNice ================== 
    def getNiceName(self):
        return mc.attributeQuery(self.attr, node = self.obj.mNode, niceName = True) or False
    def doNiceName(self,arg):
        """ 
        Set the nice name of an attribute

        Keyword arguments:
        arg(string) -- name you want to use as a nice name
        """    
        return ATTR.renameNice(self.obj.mNode,self.attr,arg)
    
        fmt_args = [self.obj.p_nameShort, self.p_nameLong, arg]
        s_baseMsg = "{0}.{1}.doNiceName() | arg: {2}".format(*fmt_args)	
        try:
            if arg:
                mc.addAttr(self.p_combinedName,edit = True, niceName = arg)
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, arg, error]
            s_errorMsg = "{0}.{1}.doNiceName() | arg: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)   

    p_nameNice = property (getNiceName,doNiceName)

    #>>> Property - p_nameLong ================== 
    def getNameLong(self):
        return ATTR.get_nameLong(self.obj.mNode,self.attr)

    def doRename(self,arg):
        """ 
        Rename an attribute as something else

        Keyword arguments:
        arg(string) -- name you want to use as a nice name
        """
        _res = ATTR.rename(self.obj.mNode,self.attr,arg)
        if _res:
            self.attr = arg
        return self.attr
           
    p_nameLong = property (getNameLong,doRename)

    #================================================    
    # Numeric properties
    #================================================    
    #>>> Property - p_defaultValue ==================  
    def getDefault(self):
        if not self.isNumeric():
            #log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
            return False
        try:
            defaultValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, listDefault=True)
            if defaultValue is not False:
                return defaultValue[0]
            return False
        except:
            #log.debug("'%s' failed to query default value" %self.p_combinedName)
            return False

    def doDefault(self,value = None):
        """ 
        Set default settings of an attribute

        Keyword arguments:
        value(string) -- value or False to reset
        """   
        fmt_args = [self.obj.p_nameShort, self.p_nameLong]
        s_baseMsg = "{0}.{1}.doDefault()".format(*fmt_args)		
        try:
            if self.isNumeric(): 
                if value is not None:
                    if self.getChildren():
                        #log.debug("'%s' has children, running set command on '%s'"%(self.p_combinedShortName,"','".join(self.getChildren())))
                        for c in self.getChildren():
                            cInstance = cgmAttr(self.obj.mNode,c)                        
                            try:
                                mc.addAttr((cInstance.obj.mNode+'.'+cInstance.attr),e=True,defaultValue = value)
                            except:
                                log.debug("'%s' failed to set a default value"%cInstance.p_combinedName)                

                    else:     
                        try:
                            mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,defaultValue = value)
                        except:
                            log.debug("'%s.%s' failed to set a default value"%(self.obj.mNode,self.attr))     
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, value, error]
            s_errorMsg = "{0}.{1}.doDefault() | value: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)    
    p_defaultValue = property (getDefault,doDefault)


    #>>> Property - p_minValue ==================       
    def getMinValue(self):
        if not self.isNumeric():
            #log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
            return False
        try:
            minValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, minimum=True)	    
            if minValue is not False:
                return minValue[0]
            return False
        except Exception as error:
            #log.debug(error)
            #log.debug("'%s' failed to query min value" %self.p_combinedName)
            return False

    def doMin(self,value = None):
        """ 
        Set min value for a numeric attribute

        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        try:
            if self.isNumeric() and not self.getChildren(): 
                if value is False or None:
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasMinValue = False)
                        log.warning("'%s.%s' had it's min value cleared"%(self.obj.mNode,self.attr))                     
                    except:
                        log.error("'%s.%s' failed to clear a min value"%(self.obj.mNode,self.attr))

                elif value is not None:
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,minValue = value)
                    except:
                        log.error("'%s.%s' failed to set a default value"%(self.obj.mNode,self.attr))
                if self.value < value:
                    self.value = value
                    log.warning("Value changed due to new min. Value is now %s"%value)
            else:
                #log.debug("'%s' is not a numeric attribute"%self.p_combinedName)	    
                return False
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, value, error]
            s_errorMsg = "{0}.{1}.doMin() | value: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)  		    
    p_minValue = property (getMinValue,doMin)

    #>>> Property - p_softMin ==================  
    def getSoftMin(self):
        if not self.isNumeric():
            #log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
            return False
        try:
            minValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, softMin=True)
            if minValue is not False:
                return minValue[0]
            return False
        except:
            return False

    def doSoftMin(self,value = None):
        """ 
        Set soft min value for a numeric attribute

        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        try:
            if self.isNumeric() and not self.getChildren(): 
                if value is False:
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasSoftMinValue = 0)
                        log.warning("'%s.%s' had it's soft max value cleared"%(self.obj.mNode,self.attr))                     
                    except:
                        log.error("'%s.%s' failed to clear a soft max value"%(self.obj.mNode,self.attr))  
                elif value is not None:
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,softMinValue = value)
                    except:
                        log.error("'%s.%s' failed to set a soft max value"%(self.obj.mNode,self.attr))
                else:
                    #log.debug("'%s' is not a numeric attribute"%self.p_combinedName)	    
                    return False
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, value, error]
            s_errorMsg = "{0}.{1}.doSoftMin() | value: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)  
    p_softMin = property (getSoftMin,doSoftMin)
    p_softMinValue = property (getSoftMin,doSoftMin)

    #>>> Property - p_softMax ==================  
    def getSoftMax(self):
        if not self.isNumeric():
            #log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
            return False
        try:
            maxValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, softMax=True)
            if maxValue is not False:
                return maxValue[0]
            return False
        except:
            return False

    def doSoftMax(self,value = None):
        """ 
        Set soft max value for a numeric attribute

        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        try:
            if self.isNumeric() and not self.getChildren(): 
                if value is False:
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasSoftMaxValue = 0)
                        log.warning("'%s.%s' had it's soft max value cleared"%(self.obj.mNode,self.attr))                     
                    except:
                        log.error("'%s.%s' failed to clear a soft max value"%(self.obj.mNode,self.attr))  
                elif value is not None:
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,softMaxValue = value)
                    except:
                        log.error("'%s.%s' failed to set a soft max value"%(self.obj.mNode,self.attr))
                else:
                    #log.debug("'%s' is not a numeric attribute"%self.p_combinedName)	    
                    return False
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, value, error]
            s_errorMsg = "{0}.{1}.doSoftMax() | value: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)  
    p_softMax = property (getSoftMax,doSoftMax)
    p_softMaxValue = property (getSoftMax,doSoftMax)

    #>>> Property - p_maxValue ==================         
    def getMaxValue(self):
        if not self.isNumeric():
            #log.debug("'%s' is not a numeric attribute"%self.p_combinedName)
            return False
        try:
            maxValue =  mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, maximum=True)
            if maxValue is not False:
                return maxValue[0]
            return False
        except:
            #log.debug("'%s' failed to query max value" %self.p_combinedName)
            return False

    def doMax(self,value = None):
        """ 
        Set max value for a numeric attribute

        Keyword arguments:
        value(string) -- value or False to reset
        """ 
        try:
            if self.isNumeric() and not self.getChildren(): 
                if value is False or None:
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,hasMaxValue = False)
                        log.warning("'%s.%s' had it's max value cleared"%(self.obj.mNode,self.attr))                     
                    except:
                        log.error("'%s.%s' failed to clear a max value"%(self.obj.mNode,self.attr))
                elif value is not None:
                    try:
                        mc.addAttr((self.obj.mNode+'.'+self.attr),e=True,maxValue = value)
                    except:
                        log.error("'%s.%s' failed to set a default value"%(self.obj.mNode,self.attr))
                if self.value > value:
                    self.value = value
                    log.warning("Value changed due to new max. Value is now %s"%value)
            else:
                log.error("'%s' is not a numeric attribute"%self.p_combinedName)	    
                return False
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, value, error]
            s_errorMsg = "{0}.{1}.doMax() | value: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)  		    
    p_maxValue = property (getMaxValue,doMax)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Queries ==================  
    def isDynamic(self):
        if self.attr in mc.listAttr(self.obj.mNode, userDefined = True):
            return True
        log.error("%s.isDynamic: False"%self.p_combinedShortName)
        return False
    def isNumeric(self):
        if mc.getAttr(self.p_combinedName,type=True) in ['string','message','enum','bool']:
            return False
        return True
    def isReadable(self):
        if not self.isDynamic():
            log.warning("'%s' is not a dynamic attribute. 'readable' not relevant"%self.p_combinedName)	    	    	    
            return False
        return mc.addAttr(self.p_combinedName,q=True,r=True) or False
    def isWritable(self):
        if not self.isDynamic():
            log.warning("'%s' is not a dynamic attribute. 'writable' not relevant"%self.p_combinedName)	    	    
            return False
        return mc.addAttr(self.p_combinedName,q=True,w=True) or False
    def isStorable(self):
        if not self.isDynamic():
            log.warning("'%s' is not a dynamic attribute. 'storable' not relevant"%self.p_combinedName)	    	    
            return False
        return mc.addAttr(self.p_combinedName,q=True,s=True) or False    
    def isUsedAsColor(self):
        if not self.isDynamic():
            log.warning("'%s' is not a dynamic attribute. 'usedAsColor' not relevant"%self.p_combinedName)	    
            return False
        return mc.addAttr(self.p_combinedName,q=True,usedAsColor=True) or False  

    def isUserDefined(self):
        l_userDefined = mc.listAttr(self.obj.mNode, userDefined = True) or []
        if self.p_nameLong in l_userDefined:
            return True
        return False

    def getRange(self):
        fmt_args = [self.obj.p_nameShort, self.p_nameLong]
        s_funcMsg = "{0}.{1}.getRange()".format(*fmt_args)
        try:
            if not self.isNumeric():
                log.warning("'%s' is not a numeric attribute. 'range' not relevant"%self.p_combinedName)	    
                return False
            return mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, range=True) or False 
        except Exception as error:
            fmt_args = [s_funcMsg, error]
            s_errorMsg = "{0} |  error: {1}".format(*fmt_args)	    
            log.error(s_errorMsg)  	

    def getSoftRange(self):
        try:	
            if not self.isNumeric():
                log.warning("'%s' is not a numeric attribute. 'range' not relevant"%self.p_combinedName)	    
                return False
            return mc.attributeQuery(self.p_nameLong, node = self.obj.mNode, softRange=True) or False     
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.getSoftRange()".format(*fmt_args)	    
            fmt_args = [s_funcMsg, error]
            s_errorMsg = "{0} |  error: {1}".format(*fmt_args)	    
            log.error(s_errorMsg)      
    #>>> Family ==================  
    def getChildren(self,asMeta = False):
        try:
            asMeta = VALID.boolArg(asMeta)
            try:buffer = mc.attributeQuery(self.attr, node = self.obj.mNode, listChildren=True) or []
            except:buffer = []
            if asMeta:
                return [cgmAttr(self.obj.mNode,c) for c in buffer]
            return buffer
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.getChildren()".format(*fmt_args)		    
            fmt_args = [s_funcMsg, asMeta, error]
            s_errorMsg = "{0} |  asMeta: {1}| error: {2}".format(*fmt_args)	    
            log.error(s_errorMsg)   

    def getParent(self,asMeta = False):
        try:
            asMeta = VALID.boolArg(asMeta)
            buffer = mc.attributeQuery(self.attr, node = self.obj.mNode, listParent=True) or []
            if asMeta:
                return [cgmAttr(self.obj.mNode,c) for c in buffer]
            return buffer
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.getParent()".format(*fmt_args)		    
            fmt_args = [s_funcMsg, asMeta, error]
            s_errorMsg = "{0} |  asMeta: {1}| error: {2}".format(*fmt_args)	    
            log.error(s_errorMsg)   

    def getSiblings(self,asMeta = False):
        try:
            asMeta = VALID.boolArg(asMeta)
            buffer = mc.attributeQuery(self.attr, node = self.obj.mNode, listSiblings=True) or []
            if asMeta:
                return [cgmAttr(self.obj.mNode,c) for c in buffer]
            return buffer
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.getSiblings()".format(*fmt_args)		    
            fmt_args = [s_funcMsg, asMeta, error]
            s_errorMsg = "{0} |  asMeta: {1}| error: {2}".format(*fmt_args)	    
            log.error(s_errorMsg)   	

    #>>> Connections ==================  
    def getDriven(self,obj=False,skipConversionNodes = False,asMeta = False):
        try:
            asMeta = VALID.boolArg(asMeta)   
            buffer =  ATTR.get_driven(self.obj.mNode,self.attr,obj,skipConversionNodes) or []
            #log.info(self.obj.mNode)
            ##log.info(self.attr)
            #log.info(obj)
            #log.info(skipConversionNodes)
            #log.info(buffer)
            #buffer =  attributes.returnDrivenObject(self.p_combinedName,skipConversionNodes) or []
            if asMeta:
                if obj:
                    return validateObjListArg(buffer)
                else:
                    return validateAttrListArg(buffer)['ml_plugs']
            
            return buffer

        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.getDriven()".format(*fmt_args)		    
            fmt_args = [s_funcMsg, obj, skipConversionNodes, asMeta, error]
            s_errorMsg = "{0} |  obj: {1} | skipConversionNodes: {2} | asMeta: {3}| error: {4}".format(*fmt_args)	    
            log.error(s_errorMsg)   

    def getDriver(self,obj=False,skipConversionNodes = False,asMeta = False):
        try:
            asMeta = VALID.boolArg(asMeta)   
            buffer =  ATTR.get_driver(self.obj.mNode,self.attr,obj,skipConversionNodes) or []                
            #buffer =  attributes.returnDrivenObject(self.p_combinedName,skipConversionNodes) or []
            if asMeta:
                if obj:
                    return validateObjListArg(buffer)
                else:
                    return validateAttrListArg(buffer)['ml_plugs']
            
            return buffer
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.getDriven()".format(*fmt_args)		    
            fmt_args = [s_funcMsg, obj, skipConversionNodes, asMeta, error]
            s_errorMsg = "{0} |  obj: {1} | skipConversionNodes: {2} | asMeta: {3}| error: {4}".format(*fmt_args)	    
            log.error(s_errorMsg)  	

    def doCopySettingsTo(self,attrArg):
        """ 
        Copies settings from one attr to another

        Keyword arguments:
        attrArg(validateAttrArg arg)        
        """
        try:
            d_targetReturn = validateAttrArg(attrArg,noneValid=False)
            mPlug_target = d_targetReturn['mi_plug']

            if self.isNumeric():
                if not mPlug_target.isNumeric():
                    raise Exception("source is numeric: '%s' | target is not: '%s'"%(self.p_combinedShortName,mPlug_target.p_combinedShortName))
                if self.p_defaultValue is not False:mPlug_target.p_defaultValue = self.p_defaultValue
                if self.p_minValue is not False:mPlug_target.p_minValue = self.p_minValue
                if self.p_maxValue is not False:mPlug_target.p_maxValue = self.p_maxValue
                if self.p_softMax is not False:mPlug_target.p_softMax = self.p_softMax
                if self.p_softMin is not False:mPlug_target.p_softMin = self.p_softMin

            mPlug_target.p_hidden = self.p_hidden
            mPlug_target.p_locked = self.p_locked
            if mPlug_target.attrType not in ['string','message']:mPlug_target.p_keyable = self.p_keyable
            return True
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, attrArg, error]
            s_errorMsg = "{0}.{1}.doCopySettingsTo() | attrArg: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)  

    def doConvert(self,attrType):
        """ 
        Converts an attribute type from one to another while preserving as much data as possible.

        Keyword arguments:
        attrType(string)        
        """	
        try:
            if self.obj.isReferenced():
                log.error("'%s' is referenced. cannot convert '%s' to '%s'!"%(self.obj.mNode,self.attr,attrType))                           
            if self.getChildren():
                log.error("'%s' has children, can't convert"%self.p_combinedName)
            keyable = copy.copy(self.p_keyable)
            hidden =  copy.copy(self.p_hidden)
            locked =  copy.copy(self.p_locked)
            storedNumeric = False
            if self.isNumeric() and not self.getChildren():
                storedNumeric = True
                minimum =  copy.copy(self.p_minValue)
                maximum =  copy.copy(self.p_maxValue)
                default =  copy.copy(self.p_defaultValue)
                softMin =  copy.copy(self.p_softMin)
                softMax =  copy.copy(self.p_softMax)

            ATTR.convert_type(self.obj.mNode,self.attr,attrType)

            #>>> Reset variables
            self.doHidden(hidden)
            self.doKeyable(keyable)        
            self.doLocked(locked)

            if self.isNumeric() and not self.getChildren() and storedNumeric:
                if softMin is not False or int(softMin) !=0 :
                    self.doSoftMin(softMin)
                if softMax is not False or int(softMax) !=0 :
                    self.doSoftMax(softMax)            
                if minimum is not False:
                    self.doMin(minimum)
                if maximum is not False:
                    self.doMax(maximum)
                if default is not False:
                    self.doDefault(default)

            self.attrType = mc.getAttr(self.p_combinedName,type=True)    
            #log.debug("'%s.%s' converted to '%s'"%(self.obj.mNode,self.attr,attrType))
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.doConvert()".format(*fmt_args)	    
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, attrType, error]
            s_errorMsg = "{0}.{1}.doConvert() | attrType: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)             
    def isMulti(self):
        return mc.addAttr("%s.%s"%(self.obj.mNode,self.attr),q=True,m=True)
    def isIndexMatters(self):
        return mc.addAttr("%s.%s"%(self.obj.mNode,self.attr),q=True,im=True)

    def getMessage(self,*a, **kw):
        """ 
        Get and store attribute value as if they were messages. Used for bufferFactory to use a connected
        attribute as a poor man's attribute message function

        Keyword arguments:
        *a, **kw
        """   
        try:
            return ATTR.get_message(self.obj.mNode,self.attr)
            """return attributes.returnMessageObject(self.obj.mNode,self.attr)
            if search.returnObjectType(self.value) == 'reference':
                if attributes.repairMessageToReferencedTarget(self.obj.mNode,self.attr,*a,**kw):
                    return attributes.returnMessageObject(self.obj.mNode,self.attr)"""                        
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, error]
            s_errorMsg = "{0}.{1}.getMessage() | error: {2}".format(*fmt_args)	    
            log.error(s_errorMsg)  


    def doStore(self,infoToStore,convertIfNecessary = True):
        """ 
        Store information to an object. If the info exits as an object, it stores as a message node. Otherwise there are
        other storing methods.

        Keyword arguments:
        infoToStore(string) -- string of information to store
        convertIfNecessary(bool) -- whether to convert the attribute if it needs to to store it. Default (True)
        """   
        if self.attrType == 'message':
            self.obj.doStore(self.attr,infoToStore)
        elif convertIfNecessary:
            self.doConvert('message')
            self.obj.doStore(self.attr,infoToStore)                

        #except:
            #  log.error("'%s.%s' failed to store '%s'"%(self.obj.mNode,self.attr,infoToStore))

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Connections and transfers
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def returnCompatibleFromTarget(self,target,*a, **kw):
        """ 
        Attempts to make a connection from instanced attribute to a target

        Keyword arguments:
        target(string) - object or attribute to connect to
        *a, **kw
        """ 
        try:
            #mi_target = validateObjArg(target)
            return ATTR.get_compatible(self.obj.mNode,self.p_nameLong,target)
            #return attributes.returnCompatibleAttrs(self.obj.mNode,self.p_nameLong,mi_target.mNode,*a, **kw)
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, target, error]
            s_errorMsg = "{0}.{1}.returnCompatibleFromTarget() | target: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)  

    def doConnectOut(self,target,*a, **kw):
        """ 
        Attempts to make a connection from instanced attribute to a target

        Keyword arguments:
        target(string) - object or attribute to connect to
        *a, **kw
        """ 
        #log.debug(">>> %s >>> "%(_str_func) + "="*75) 	
        try:
            try:d_target = validateAttrArg(target,noneValid=False)
            except Exception as error:raise Exception("%s failed to validate: %s"%(target,error))
            mPlug_target = d_target.get('mi_plug')

            if mPlug_target:
                if mPlug_target.getChildren() and not self.getChildren():
                    for cInstance in mPlug_target.getChildren(asMeta=True):
                        log.info("Single to multi mode. Children detected. Connecting to child: {0}".format(cInstance.p_combinedName))
                        ATTR.connect(self.p_combinedName,cInstance.p_combinedName)
                        #attributes.doConnectAttr(self.p_combinedName,cInstance.p_combinedName)
                else:
                    try:ATTR.connect(self.p_combinedName,mPlug_target.p_combinedName)
                    except Exception as error:raise Exception("connection fail: %s"%(error))		    
            else:
                log.warning("Source failed to validate: %s"%(source) + "="*75)            			    
                return False	    

            #log.debug(">>> %s.doConnectOut >>-->>  %s "%(self.p_combinedShortName,mPlug_target.p_combinedName) + "="*75)            						
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.doConnectOut()".format(*fmt_args)	    
            fmt_args = [s_funcMsg, target, error]
            s_errorMsg = "{0} | target: {1} | error: {2}".format(*fmt_args)	    
            log.error(s_errorMsg)  

    def doConnectIn(self,source,childIndex = False,*a, **kw):
        """ 
        Attempts to make a connection from a source to our instanced attribute

        Keyword arguments:
        source(string) - object or attribute to connect to
        *a, **kw
        """ 
        try:
            try:d_source = validateAttrArg(source,noneValid=False)
            except Exception as error:raise Exception("%s failed to validate: %s"%(source,error))
            mPlug_source = d_source.get('mi_plug')
            if mPlug_source:
                if self.getChildren() and not mPlug_source.getChildren():
                    for cInstance in self.getChildren(asMeta=True):
                        log.info("Single to multi mode. Children detected. Connecting to child: {0}".format(cInstance.p_combinedName))
                        ATTR.connect(mPlug_source.p_combinedName,cInstance.p_combinedName)
                else:
                    try:ATTR.connect(mPlug_source.p_combinedName,self.p_combinedName)
                    except Exception as error:raise Exception("connection fail: %s"%(error))		
                #log.debug(">>> %s.doConnectIn <<--<<  %s "%(self.p_combinedShortName,mPlug_source.p_combinedName) + "="*75)            						
            else:
                log.warning("Source failed to validate: %s"%(source) + "="*75)            			    
                return False
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong]
            s_funcMsg = "{0}.{1}.doConnectIn()".format(*fmt_args)	    
            fmt_args = [s_funcMsg, source, error]
            s_errorMsg = "{0} | source: {1} | error: {2}".format(*fmt_args)	    
            log.error(s_errorMsg)  

    def doCopyTo(self,target, targetAttrName = None, *a,**kw):
        """                                     
        Replacement for Maya's since maya's can't handle shapes....blrgh...
        Copy attributes from one object to another as well as other options. If the attribute already
        exists, it'll copy the values. If it doesn't, it'll make it. If it needs to convert, it can.
        It will not make toast.

        Keywords:
        toObject(string) - obj to copy to
        targetAttrName(string) -- name of the attr to copy to . Default is None which will create an 
                          attribute oft the fromAttr name on the toObject if it doesn't exist
        convertToMatch(bool) -- whether to convert if necessary.default True        
        values(bool) -- copy values. default True
        inputConnections(bool) -- default False
        outGoingConnections(bool) -- default False
        keepSourceConnections(bool)-- keeps connections on source. default True
        copyAttrSettings(bool) -- copy the attribute state of the fromAttr (keyable,lock,hidden). default True
        connectSourceToTarget(bool) useful for moving attribute controls to another object. default False

        RETURNS:
        success(bool)
        """
        try:
            assert mc.objExists(target),"'%s' doesn't exist"%target
            assert mc.ls(target,long=True) != [self.obj.mNode], "Can't transfer to self!"
            functionName = 'doCopyTo'
            if targetAttrName is None: targetAttrName = self.attr
            convertToMatch = kw.pop('convertToMatch',True)
            values = kw.pop('values',True)
            inConnection = kw.pop('inConnection',False)
            outConnections = kw.pop('outConnections',False)
            keepSourceConnections = kw.pop('keepSourceConnections',True)
            copySettings = kw.pop('copySettings',True)
            _driven = kw.pop('driven',None)
            connectSourceToTarget = kw.pop('connectSourceToTarget',False)
            connectTargetToSource = kw.pop('connectTargetToSource',False)  


            copyTest = [values,inConnection,outConnections,keepSourceConnections,connectSourceToTarget,copySettings]

            if sum(copyTest) < 1:
                log.warning("You must have at least one option for copying selected. Otherwise, you're looking for the 'doDuplicate' function.")            
                return False

            if '.' in list(target):
                targetBuffer = target.split('.')
                if len(targetBuffer) == 2:
                    ATTR.copy_to(self.obj.mNode,
                                 self.p_nameLong,
                                 targetBuffer[0],
                                 targetBuffer[1],
                                 convertToMatch = convertToMatch,
                                 values=values, inConnection = inConnection,
                                 outConnections=outConnections, keepSourceConnections = keepSourceConnections,
                                 copySettings = copySettings, 
                                 driven= _driven)               

                else:
                    log.warning("Yeah, not sure what to do with this. Need an attribute call with only one '.'")
            else:
                ATTR.copy_to(self.obj.mNode,
                             self.p_nameLong,
                             target,
                             targetAttrName,
                             convertToMatch = convertToMatch,
                             values=values, inConnection = inConnection,
                             outConnections=outConnections, keepSourceConnections = keepSourceConnections,
                             copySettings = copySettings, 
                             driven= _driven)               
            #except:
            #    log.warning("'%s' failed to copy to '%s'!"%(target,self.p_combinedName))          
            self.doCopySettingsTo([target,targetAttrName])

            return True
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, target, targetAttrName, error]
            s_errorMsg = "{0}.{1}.doCopyTo() | target: {2} | | targetAttrName: {3} | error: {4}".format(*fmt_args)	    
            log.error(s_errorMsg)  

    def doTransferTo(self,target):
        """ 
        Transfer an instanced attribute to a target with all settings and connections intact

        Keyword arguments:
        target(string) -- object to transfer it to
        *a, **kw
        """ 
        try:
            mi_target = validateObjArg(target,cgmObject)
            assert self.isUserDefined() is not False,"'%s' isn't user defined. Transferring this attribute is probably a bad idea. Might we suggest doCopyTo along with a connect to source option"%self.p_combinedShortName        
            assert mi_target != self.obj.mNode, "Can't transfer to self!"
            assert self.isDynamic() is True,"'%s' is not a dynamic attribute."%self.p_combinedShortName
            fmt_args = [self.p_nameLong, self.obj.p_nameShort, mi_target.p_nameShort]	    
            log.warning("Transferring attr: '{0}' | from '{1}' to '{2}'".format(*fmt_args))	
            s_attrBuffer = copy.copy(self.p_nameLong)
            #mc.copyAttr(self.obj.mNode,self.target.obj.mNode,attribute = [self.target.attr],v = True,ic=True,oc=True,keepSourceConnections=True)
            ATTR.copy_to(self.obj.mNode,
                                  self.p_nameLong,
                                  mi_target.mNode,
                                  self.p_nameLong,
                                  convertToMatch = True,
                                  values = True, inConnection = True,
                                  outConnections = True, keepSourceConnections = False,
                                  copySettings = True, driven = False)
            self.doDelete()
            return cgmAttr(mi_target,s_attrBuffer)
        except Exception as error:
            fmt_args = [self.obj.p_nameShort, self.p_nameLong, target, error]
            s_errorMsg = "{0}.{1}.doTransferTo() | target: {2} | error: {3}".format(*fmt_args)	    
            log.error(s_errorMsg)  
                 
class NameFactory(object):
    """ 
    New Name Factory. Finds a 
    """
    def __init__(self,node,doName = False):
        """ 
        """
        try:
            self.mNode
            self.i_node = self
        except:
            self.i_node = validateObjArg(node,cgmNode,noneValid=False)

        """    
        if issubclass(type(node),cgmNode):
            self.i_node = node
        elif mc.objExists(node):
            self.i_node = cgmNode(node)
        else:
            raise StandardError,"NameFactory.go >> node doesn't exist: '%s'"%node
        """
        _str_func = "NameFactory.__init__"  
        #log.debug(">>> %s >>> node: %s | doName: %s"%(_str_func,node,doName) + "="*75)
        #Initial Data        
        self.i_nameParents = []
        self.i_nameChildren = []
        self.i_nameSiblings = []

    def isNameLinked(self,node = None):  
        _str_func = "NameFactory.isNameLinked"  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75)
        try:
            if node is None:
                i_node = self.i_node
            elif issubclass(type(node),cgmNode):
                i_node = node
            elif mc.objExists(node):
                i_node = cgmNode(node)
            else:
                raise Exception("NameFactory.isNameLinked >> node doesn't exist: '%s'"%node)

            if i_node.hasAttr('cgmName') and i_node.getMessage('cgmName'):
                return True
            return False
        except Exception as error:
            raise Exception("%s >>> node: %s |error : %s"%(_str_func,node,error))

    #@r9General.Timer
    def getMatchedParents(self, node = None):  
        _str_func = "NameFactory.getMatchedParents"  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75)
        #try:
        if node is None:
            i_node = self.i_node
        elif issubclass(type(node),cgmNode):
            i_node = node
        elif mc.objExists(node):
            i_node = cgmNode(node)
        else:
            raise Exception("NameFactory.getMatchedParents >> node doesn't exist: '%s'"%node)

        parents = TRANS.parents_get(i_node.mNode)
        self.i_nameParents = []
        if parents:
            #parents.reverse()
            d_nameDict = i_node.getNameDict()
            for p in parents :
                i_p = cgmNode(p)
                if i_p.getNameDict() == d_nameDict:
                    self.i_nameParents.append(i_p)
                    #log.debug("Name parent found: '%s'"%i_p.mNode)
                else:break
        return self.i_nameParents
        #except Exception as error:
        #    pprint.pprint(vars())
        #    raise Exception("%s >>> node: %s |error : %s"%(_str_func,node,error))

    def getMatchedChildren(self, node = None):  
        _str_func = "NameFactory.getMatchedChildren"  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75)
        try:	
            if node is None:
                i_node = self.i_node
            elif issubclass(type(node),cgmNode):
                i_node = node
            elif mc.objExists(node):
                i_node = cgmNode(node)
            else:
                raise Exception("NameFactory.getMatchedChildren >> node doesn't exist: '%s'"%node)

            #>>> Count our matched name children range
            children = mc.listRelatives (i_node.mNode, allDescendents=True,type='transform',fullPath=True)
            self.i_nameChildren = []        
            if children:
                #children.reverse()
                d_nameDict = i_node.getNameDict()            
                for c in children :
                    i_c = cgmNode(c)
                    if i_c.getNameDict() == d_nameDict:
                        self.i_nameChildren.append(i_c)
                        #log.debug("Name child found: '%s'"%i_c.mNode)
                    else:break
            return self.i_nameChildren
        except Exception as error:
            raise Exception("%s >>> node: %s |error : %s"%(_str_func,node,error))

    def getMatchedSiblings(self, node = None):
        _str_func = "NameFactory.getMatchedSiblings"  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75)
        if node is None:
            i_node = self.i_node
        elif issubclass(type(node),cgmNode):
            i_node = node
        elif mc.objExists(node):
            i_node = cgmNode(node)
        else:
            raise Exception("NameFactory.getMatchedSiblings >> node doesn't exist: '%s'"%node)

        self.i_nameSiblings = []
        d_nameDict = i_node.getNameDict()        
        for mSib in i_node.getSiblings(asMeta = True):                    
            if mSib.getNameDict() == d_nameDict and mSib.mNode != i_node.mNode:
                self.i_nameSiblings.append(mSib)

        return self.i_nameSiblings

    #@r9General.Timer    
    def getFastIterator(self, node = None):
        """
        Fast iterate finder
        """
        _str_func = "NameFactory.getFastIterator"  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75)
        try:
            if node is None:i_node = self.i_node
            else:i_node = validateObjArg(node,noneValid=False)
            #log.debug("%s >> node : '%s'"%(_str_func,i_node.p_nameShort))               
            self.int_fastIterator = 0

            #If we have an assigned iterator, start with that
            d_nameDict = i_node.getNameDict()		
            if 'cgmIterator' in list(d_nameDict.keys()):
                #log.debug("%s >> Found cgmIterator : %s"%(_str_func,d_nameDict.get('cgmIterator')))               	
                return int(d_nameDict.get('cgmIterator'))

            self.d_nameCandidate = d_nameDict
            self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)  

            #Now that we have a start, we're gonna see if that name is taken by a sibling or not
            def getNewNameCandidate(self):
                self.int_fastIterator+=1#add one
                #log.debug("Counting in getBaseIterator: %s"%self.int_fastIterator)				
                self.d_nameCandidate['cgmIterator'] = str(self.int_fastIterator)
                self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
                #log.debug("Checking: '%s'"%self.bufferName)
                return self.bufferName

            mc.rename(i_node.mNode,self.bufferName)#Name it
            #log.debug("Checking: '%s'"%self.bufferName)
            if self.bufferName != i_node.getShortName():
                self.int_fastIterator = 1
                self.d_nameCandidate['cgmIterator'] = str(self.int_fastIterator)
                self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
                mc.rename(i_node.mNode,self.bufferName)#Name it
                while self.bufferName != i_node.getShortName() and self.int_fastIterator <100:
                    getNewNameCandidate(self)	
                    mc.rename(i_node.mNode,self.bufferName)#Name it

            #log.debug("fastIterator: %s"%self.int_fastIterator)
            return self.int_fastIterator
        except Exception as error:
            raise Exception("%s >>> node: %s |error : %s"%(_str_func,i_node.p_nameShort,error))

    #@r9General.Timer    
    def getBaseIterator(self, node = None):
        _str_func = "NameFactory.getBaseIterator"  
        
        if node is None:
            i_node = self.i_node
        elif issubclass(type(node),cgmNode):
            i_node = node
        elif mc.objExists(node):
            i_node = cgmNode(node)
        else:
            raise Exception("NameFactory.getBaseIterator >> node doesn't exist: '%s'"%node)

        self.int_baseIterator = 0
        #If we have an assigned iterator, start with that
        d_nameDict = i_node.getNameDict()
        if d_nameDict.get('cgmIterator'):
            return int(d_nameDict.get('cgmIterator'))

        #Gather info
        i_nameParents = self.getMatchedParents(i_node)
        i_nameChildren = self.getMatchedChildren(i_node)
        i_nameSiblings = self.getMatchedSiblings(i_node)

        if i_nameParents:#If we have parents 
            self.int_baseIterator =  len(i_nameParents) + 1
        elif i_nameChildren or i_nameSiblings:#If we have children, we can't be 0
            self.int_baseIterator = 1

        #Now that we have a start, we're gonna see if that name is taken by a sibling or not
        if i_nameSiblings:#check siblings
            def getNewNameCandidate(self):
                self.int_baseIterator+=1#add one
                #log.debug("Counting in getBaseIterator: %s"%self.int_baseIterator)				
                self.d_nameCandidate['cgmIterator'] = str(self.int_baseIterator)
                self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
                #log.debug("Checking: '%s'"%self.bufferName)
                return self.bufferName	    

            self.d_nameCandidate = i_node.getNameDict()
            if self.int_baseIterator:
                self.d_nameCandidate['cgmIterator'] = str(self.int_baseIterator)
            self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)

            l_siblingShortNames = [i_s.getBaseName() for i_s in i_nameSiblings]
            #log.debug("Checking siblings: %s"%l_siblingShortNames)
            #log.debug("Checking: '%s'"%self.bufferName)	    
            while self.bufferName in l_siblingShortNames and self.int_baseIterator <100:
                getNewNameCandidate(self)	

        #log.debug("baseIterator: %s"%self.int_baseIterator)
        return self.int_baseIterator


    #@r9General.Timer    
    def getIterator(self,node = None):
        """
        """
        _str_func = "NameFactory.getIterator"  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75)
        if node is None:i_node = self.i_node
        else:i_node = validateObjArg(node,noneValid=False)

        self.int_iterator = 0

        def getNewNameCandidate(self):
            self.int_iterator+=1#add one
            #log.debug("%s >> Counting in getIterator: %s"%(_str_func,self.int_iterator)	 )   
            self.d_nameCandidate['cgmIterator'] = str(self.int_iterator)
            self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)
            return self.bufferName

        d_nameDict = i_node.getNameDict()
        if d_nameDict.get('cgmIterator') is not None:
            return int(d_nameDict.get('cgmIterator'))

        #Gather info
        i_nameParents = self.getMatchedParents(node = i_node)
        i_nameChildren = self.getMatchedChildren(node = i_node)
        i_nameSiblings = self.getMatchedSiblings(node = i_node)

        if i_nameParents:#If we have parents 
            self.int_iterator = self.getBaseIterator(i_nameParents[-1]) + len(i_nameParents)
        else:
            self.int_iterator = self.getBaseIterator(node = i_node)

        #Now that we have a start, we're gonna see if that name is taken by a sibling or not
        self.d_nameCandidate = i_node.getNameDict()
        if self.int_iterator:
            self.d_nameCandidate['cgmIterator'] = str(self.int_iterator)
        self.bufferName = nameTools.returnCombinedNameFromDict(self.d_nameCandidate)

        #log.debug("bufferName: '%s'"%self.bufferName)
        if not mc.objExists(self.bufferName):
            #log.debug('Good name candidate')
            return self.int_iterator
        else:#if there is only one
            for obj in mc.ls(self.bufferName):
                i_bufferName = cgmNode(obj)
                if i_node.mNode == i_bufferName.mNode:
                    #log.debug("I'm me! : %s"%self.int_iterator)
                    return self.int_iterator

        if i_nameSiblings:#check siblings
            l_siblingShortNames = [i_s.getBaseName() for i_s in i_nameSiblings]
            #log.debug("Checking siblings: %s"%l_siblingShortNames)
            while self.bufferName in l_siblingShortNames and self.int_iterator <100:
                getNewNameCandidate(self)
            """
		for i_s in i_nameSiblings:
		    if i_node.getShortName() == self.bufferName:
			log.debug("I'm me! : %s"%self.int_iterator)
			return self.int_iterator                    
		    elif i_s.getShortName() == self.bufferName:
			log.debug("Sibling has this")
			getNewNameCandidate(self)
		    else:
			getNewNameCandidate(self)                    
		"""
        #log.debug("getIterator: %s"%self.int_iterator)
        return self.int_iterator


    #@r9General.Timer
    def returnUniqueGeneratedName(self, ignore='none',node = None,fastIterate = True, **kws):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Returns a generated name with iteration for heirarchy objects with the same tag info

        ARGUMENTS:
        ignore(string) - default is 'none', only culls out cgmtags that are 
                         generated via returnCGMOrder() function

        RETURNS:
        name(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        _str_func = "NameFactory.returnUniqueGeneratedName"  

        if node is None:i_node = self.i_node
        elif issubclass(type(node),cgmNode):i_node = node
        elif mc.objExists(node):i_node = cgmNode(node)
        else:raise Exception("NameFactory.getIterator >> node doesn't exist: '%s'"%node)

        if type(ignore) is not list:ignore = [ignore]
        #log.debug("ignore: %s"%ignore)

        #>>> Dictionary driven order first build
        d_updatedNamesDict = nameTools.returnObjectGeneratedNameDict(i_node.mNode,ignore)

        if 'cgmName' not in list(d_updatedNamesDict.keys()) and SEARCH.get_mayaType(i_node.mNode) !='group' and 'cgmName' not in ignore:
            i_node.addAttr('cgmName',i_node.getShortName(),attrType = 'string',lock = True)
            #d_updatedNamesDict = nameTools.returnObjectGeneratedNameDict(i_node.mNode,ignore)
            d_updatedNamesDict['cgmName'] = i_node.getShortName()

        if fastIterate:  
            iterator = self.getFastIterator(node = i_node)
        else:
            iterator = self.getIterator(node = i_node)  
        if iterator:
            d_updatedNamesDict['cgmIterator'] = str(iterator)    
        #log.debug(nameTools.returnCombinedNameFromDict(d_updatedNamesDict))
        _str_nameCandidate =  nameTools.returnCombinedNameFromDict(d_updatedNamesDict)
        return _str_nameCandidate
       

    #@r9General.Timer
    def doNameObject(self,node = None,fastIterate = True, **kws):
        _str_func = "NameFactory.doNameObject"  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75)
        if node is None:i_node = self.i_node
        elif issubclass(type(node),cgmNode):i_node = node
        elif mc.objExists(node):i_node = cgmNode(node)
        else:raise Exception("NameFactory.doNameObject >> node doesn't exist: '%s'"%node)
        #log.debug("Naming: '%s'"%i_node.getShortName())
        nameCandidate = self.returnUniqueGeneratedName(node = i_node, fastIterate=fastIterate,**kws)
        #log.debug("nameCandidate: %s"%nameCandidate)
        try:mc.rename(i_node.mNode,nameCandidate)
        except Exception as error:log.error("%s >> %s"%(_str_func,error))
        #i_node.rename(nameCandidate)

        str_baseName = i_node.getBaseName()
        if  str_baseName != nameCandidate:
            log.debug("'%s' not named to: '%s'"%(str_baseName,nameCandidate))

        return str_baseName


    #@r9General.Timer    
    def doName(self,fastIterate = True,nameChildren=False,nameShapes = False,node = None,**kws):
        _str_func = "NameFactory.doName"  
        #log.debug(">>> %s >>> "%(_str_func) + "="*75)
        if node is None:i_node = self.i_node
        elif issubclass(type(node),cgmNode):i_node = node
        elif mc.objExists(node):i_node = cgmNode(node)
        else:raise Exception("NameFactory.doName >> node doesn't exist: '%s'"%node)

        #Try naming object
        self.doNameObject(node = i_node,fastIterate=fastIterate,**kws)
       
        i_rootObject = i_node

        if nameShapes:
            shapes = mc.listRelatives(i_rootObject.mNode,shapes=True,fullPath=True) or []
            if shapes:
                l_iShapes = []
                for s in shapes:
                    if not mc.referenceQuery(s, isNodeReferenced=True):
                        l_iShapes.append(cgmNode(s))
                for i_s in l_iShapes:
                    #log.debug("on shape: '%s'"%i_s.mNode)
                    try:self.doNameObject(node = i_s, fastIterate=fastIterate,**kws)
                    except Exception as error:
                        raise Exception("NameFactory.doName.doNameObject child ('%s') failed: %s"%i_node.getShortName()).with_traceback(error)

        #Then the children
        if nameChildren:#Initialize them all so we don't lose them
            l_iChildren = []
            for o in mc.listRelatives(i_rootObject.mNode, allDescendents = True,type='transform',fullPath=True) or []:
                l_iChildren.append(cgmNode(o))

            if l_iChildren:
                l_iChildren.reverse()
                for i_c in l_iChildren:
                    #log.debug("on child: '%s'"%i_c.mNode)		    
                    try:self.doNameObject(node = i_c,fastIterate=fastIterate,**kws)
                    except Exception as error:
                        raise Exception("NameFactory.doName.doNameObject child ('%s') failed: %s"%i_node.getShortName()).with_traceback(error)





#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================  
def getMetaNodesInitializeOnly(mTypes = ['cgmPuppet','cgmMorpheusPuppet','cgmMorpheusMakerNetwork'],dataType = '',asMeta = False):
    """
    Meant to be a faster get command than Mark's for nodes we only want initializeOnly mode
    """
    """
    checkList = r9Meta.getMetaNodes(mAttrs = 'mClass', mTypes=mTypes,dataType = '')
    returnList = []
    for o in checkList:
	i_o = False
	try:i_o = r9Meta.MetaClass(o,initializeOnly = True)
	except:log.warning("'%s' can't take initializeOnly kw"%o)
	if i_o and i_o.hasAttr('mClass') and i_o.mClass in mTypes:
	    if dataType == 'metaClass':
		returnList.append(i_o)
	    else:
		returnList.append(i_o.mNode)
    """
    checkList = mc.ls(type='network')
    l_return = []
    for o in checkList:
        if ATTR.get(o,'mClass') in mTypes:
            l_return.append(o)
    if asMeta:
        ml_return = []
        for o in l_return:
            ml_return.append(r9Meta.MetaClass(o))
        return ml_return
    return l_return

#=======================================================================================================      
# Argument validation
#=======================================================================================================  
class ModuleFunc(cgmGEN.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """	
        try:
            try:moduleInstance = kws['moduleInstance']
            except:moduleInstance = args[0]
            try:
                assert isModule(moduleInstance)
            except Exception as error:raise Exception("Not a module instance : %s"%error)	
        except Exception as error:raise Exception("ModuleFunc failed to initialize | %s"%error)
        self._str_func= "testFModuleFuncunc"		
        super(ModuleFunc, self).__init__(*args, **kws)

        self.mi_module = moduleInstance	
        self._l_ARGS_KWS_DEFAULTS = [{'kw':'moduleInstance',"default":None}]	
        #=================================================================
'''
def SampleFunc(*args,**kws):
    class fncWrap(cgmGEN.cgmFuncCls):
	def __init__(self,*args,**kws):
	    """
	    """	
	    self._str_func= "testFModuleFuncunc"		
	    super(fncWrap, self).__init__(*args, **kws)
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'moduleInstance',"default":None}]	
	    #=================================================================

    return fncWrap(*args,**kws).go()
'''
#>>>>> Validation stuff...

def asMeta(*args,**kws):
    '''
    Simple pass through for validate meta objects. Rather than having to call for validateObjListArg or validateObjArg. It returns what it is passed.

    @kws
    See validateObjArg
    '''  
    try:
        try:_selected = kws.pop('sl')
        except:_selected = False
        arg = None
        
        if _selected:
            l = mc.ls(sl=1)
            if l:
                args = [l]
                
        if args:
            arg = args[0]
        elif kws:
            arg = kws.get('arg')
            
        if arg and VALID.isListArg(arg):#make sure it's not a list
            return validateObjListArg(*args,**kws)
        return validateObjArg(*args,**kws)
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        """
        log.error("cgmMeta.asMeta failure... --------------------------------------------------")
        if args:
            for i,arg in enumerate(args):
                log.error("arg {0}: {1}".format(i,arg))
        if kws:
            for items in kws.items():
                log.error("kw: {0}".format(items))	
        log.error("...cgmMeta.asMeta failure --------------------------------------------------")
        """
        raise Exception(error)
    
try:
    createMetaNode = r9Meta.createMetaNode
except Exception as err:
    log.error(" r9Meta.createMetaNode failed to link. You have an old red9 library in your pathing. Resolve for full functionality")
    for arg in err.args:
        log.error(arg)            
    
def createMetaNode(mType = None, *args, **kws):
    _str_func = 'createMetaNode'
    
    _r9ClassRegistry = r9Meta.getMClassMetaRegistry()
    
    if not type(mType) in [str,str]:
        try: mType = mType.__name__
        except Exception as error:
            raise ValueError("mType not a string and not a usable class name. mType: {0}".format(mType))	
    if mType not in _r9ClassRegistry:
        raise ValueError("mType not found in class registry. mType: {0}".format(mType))    
    
    _call = _r9ClassRegistry.get(mType)
    
    log.debug("|{0}| >> mType: {1} | class: {2}".format(_str_func,mType,_call))             
  
    try:    
        return _call(*args,**kws)
    except Exception as err:
        log.info("|{0}| >> mType: {1} | class: {2}".format(_str_func,mType,_call))                     
        if args:
            log.info("|{0}| >> Args...".format(_str_func))                         
            for i,arg in enumerate(args):
                log.info("    arg {0}: {1}".format(i,arg))
        if kws:
            log.info("|{0}| >> Kws...".format(_str_func))                                     
            for items in list(kws.items()):
                log.info("    kw: {0}".format(items))   
                
        for arg in err.args:
            log.error(arg)            
        cgmGEN.cgmExceptCB(Exception,err)
        #raise Exception,err
    
    
    
def validateObjArg(arg = None, mType = None, noneValid = False,
                   default_mType = None,
                   mayaType = None, setClass = False):
    """
    validate an objArg to be able to get instance of the object

    @kws
    0 - 'arg'(mObject - None) -- mObject instance or string
    1 - 'mType'(mClass - None) -- what mType to be looking for
    2 - 'noneValid'(bool - False) -- Whether None is a valid argument or not
    3 - 'default_mType'(mClass - <class 'cgm.core.cgm_Meta.cgmNode'>) -- What type to initialize as if no mClass is set
    4 - 'mayaType'(str/list - None) -- If the object needs to be a certain object type
    5 - 'setClass'
    """    
    _str_func = 'validateObjArg'

    #Pull kws local ====================================================================
    #arg = _d_kws['arg']
    #mType = _d_kws['mType']
    #noneValid = _d_kws['noneValid']
    #default_mType = _d_kws['default_mType']
    #mayaType = _d_kws['mayaType']		
    #setClass = _d_kws['setClass']	
    mTypeClass = False
    _r9ClassRegistry = r9Meta.getMClassMetaRegistry()
    _convert = False
    str_type = None
    
    if mType is not None:
        t1 = time.time()
        if not type(mType) in [str,str]:
            try: mType = mType.__name__
            except Exception as error:
                raise ValueError("mType not a string and not a usable class name. mType: {0}".format(mType))	
        if mType not in _r9ClassRegistry:
            raise ValueError("mType not found in class registry. mType: {0}".format(mType))
        t2 = time.time()
        log.debug("initial mType... %0.6f"%(t2-t1))
    #------------------------------------------------------------------------------------
    _mi_arg = False

    argType = type(arg)
    if argType in [list,tuple]:#make sure it's not a list
        if len(arg) ==1:
            arg = arg[0]
        elif arg == []:
            arg = None
        else:raise ValueError("arg cannot be list or tuple or longer than 1 length: %s"%arg)	
        
    if not noneValid:
        if arg in [None,False]:
            raise ValueError("Invalid arg({0}). noneValid = False".format(arg))
    else:
        if arg in [None,False]:
            if arg not in [None,False]:log.warning("%s arg fail: %s"%(__str_reportStart,arg))
            return False
    try:
        arg.mNode
        _mi_arg = arg
        _arg = arg.mNode
        log.debug("instance already...")		
    except:
        log.debug("not an instance arg...")
        try:_arg = names.getLongName(arg)
        except Exception as err:
            if noneValid:return False
            raise err 
    if not _arg:
        if noneValid:return False
        else:
            raise ValueError("'{0}' is not a valid arg. Validated to {1}".format(arg,_arg))

    _argShort = names.getShortName(_arg)

    log.debug("Checking: '{0} | mType: {1}'".format(_arg,mType))
    mTypeClass = _r9ClassRegistry.get(mType)

    if mayaType is not None and len(mayaType):
        t1 = time.time()		
        log.debug("Checking mayaType...")
        if type(mayaType) not in [tuple,list]:l_mayaTypes = [mayaType]
        else: l_mayaTypes = mayaType
        #str_type = search.returnObjectType(_mi_arg.getComponent())
        str_type = VALID.get_mayaType(_arg)
        if str_type not in l_mayaTypes:
            if noneValid:
                log.warning("%s '%s' mayaType: '%s' not in: '%s'"%(__str_reportStart,_argShort,str_type,l_mayaTypes))
                return False
            raise Exception("'%s' mayaType: '%s' not in: '%s'"%(_argShort,str_type,l_mayaTypes))			    	
        t2 = time.time()
        log.debug("mayaType not None time... %0.6f"%(t2-t1))		    

    #Get our cache key
    _mClass = ATTR.get(_argShort,'mClass')

    _UUID2016 = False#...a flag to see if we need a reg UUID attr 
    try:
        _UUID2016 = mc.ls(_argShort, uuid=True)[0]
    except:pass

    if _UUID2016:
        log.debug(">2016 UUID: {0}...".format(_UUID2016))
        _UUID = _UUID2016
        try:
            ATTR.delete(_argShort,'UUID')				    
            log.debug("Clearing attr UUID: {0}".format(arg))
        except:pass
    else:
        _UUID = ATTR.get(_argShort,'UUID')

    log.debug("Cache keys|| UUID: {0} | mClass: {1}".format(_UUID,_mClass))
    _wasCached = False

    #See if it's in the cache
    _keys = list(r9Meta.RED9_META_NODECACHE.keys())
    _cacheKey = None
    _cached = None
    _unicodeArg = str( _arg)
    _change = False

    if _UUID in _keys:
        _cacheKey = _UUID
        _cached = r9Meta.RED9_META_NODECACHE.get(_UUID)
    elif _unicodeArg in _keys:
        _cacheKey = _unicodeArg
        _cached = r9Meta.RED9_META_NODECACHE.get(_unicodeArg)	

    #_cached = r9Meta.RED9_META_NODECACHE.get(_UUID,None) or r9Meta.RED9_META_NODECACHE.get(_arg,None)
    log.debug("cacheKey: {0}".format(_cacheKey))

    if _cached is not None:
        t1 = time.time()		
        log.debug("Already cached")
        _cachedMClass = ATTR.get(_arg,'mClass') or False
        _cachedType = type(_cached)
        log.debug("Cached mNode: {0}".format(_cached.mNode))		
        log.debug("Cached mClass: {0}".format(_cachedMClass))
        log.debug("Cached Type: {0}".format(_cachedType))
        _change = False
        _redo = False
        #...gonna see if our cache is obviously wrong
        if _arg != _cached.mNode:
            log.debug("mNodes don't match. Need new UUID our our new arg")
            log.debug("Clearing UUID...")
            #ATTR.delete(_arg,'UUID')	
            try:ATTR.set(_argShort,'UUID','')
            except:pass		    
            _redo = True

        elif _cachedType == mTypeClass:
            log.debug("cachedType({0}) match ({1})".format(_cachedType,mTypeClass))
            if setClass and not _cachedMClass:
                log.debug("...ensuring proper categorization next time")
                try:ATTR.add(_argShort, 'mClass','string')
                except:pass		    
                try:ATTR.add(_argShort,'UUID','string')
                except:pass
                ATTR.set(_argShort,'mClass',mType,True)
            return _cached

        elif _cachedMClass:#...check our types and subclass stuff
            if mType is not None:
                if _cachedType != mTypeClass:
                    log.debug("cached Type doesn't match({0})".format(mTypeClass))			    			
                    _change = True
                elif _cachedMClass != mType:
                    log.debug("mClass value ({0}). doesn't match({1})".format(_cachedMClass,mType))
                    _change = True

                #attributes.storeInfo(_arg, 'mClass', mType, overideMessageCheck=True)
                #ATTR.add(_arg,'UUID','string')

        elif mTypeClass:
            log.debug("No cached mClass or type")
            try:
                if issubclass(type(_cached), mTypeClass ):
                    log.debug("subclass match")
                    _change = False
                    if setClass:
                        log.debug("subclass match not good enough")
                        _change = True
            except Exception as err:
                log.warning("cached subclass check failed | {0}".format(err))                
                _change = True

        if _change:
            log.debug("..subclass check")
            try:
                if issubclass(_cachedType, mTypeClass) and not setClass:
                    log.debug("...but is subclass")
                    _change = False
                else:
                    log.debug("...not a subclass")			
            except Exception as err:
                log.warning("cachedType: {0}".format(_cachedType))
                log.warning("mTypeClass: {0}".format(mTypeClass))                
                log.warning("Change cached subclass check failed | {0}".format(err))                
                
        if not _change and not _redo:
            t2 = time.time()
            log.debug("Cache good %0.6f"%(t2-t1))		    
            return _cached
        elif _change:
            if not setClass:
                if noneValid:
                    return False
                else:
                    raise ValueError("'{0}' is not a valid arg. Not class or subclass: {1}".format(arg,mTypeClass))
            
            log.debug("conversion necessary.removing from cache")
            _wasCached = True
            if _cachedMClass:
                log.debug("Clearing mClass...")
                #_cached.mClass = ''
                ATTR.delete(_argShort,'mClass')
            if _UUID:
                log.debug("Clearing UUID...")
                ATTR.delete(_argShort,'UUID')			
                #_cached.UUID = ''			
            r9Meta.RED9_META_NODECACHE.pop(_cacheKey)

        t2 = time.time()
        log.debug("Cache check %0.6f"%(t2-t1))	

    if mType:
        t1 = time.time()				    		
        if setClass or _wasCached:
            log.debug("setClass...")
            #attributes.storeInfo(_arg, 'mClass', mType, overideMessageCheck=True)
            t_attr = time.time()				    		
            try:ATTR.add(_argShort, 'mClass','string')
            except:pass		    
            try:
                if not _UUID2016:
                    ATTR.add(_argShort,'UUID','string')
            except:pass
            if not ATTR.has_attr(_argShort,'mClass'):
                ATTR.add(_argShort,'mClass','string',value=mType,lock=True)
            else:
                ATTR.set(_argShort,'mClass',mType,True)
            t2 = time.time()		    
            log.debug("attrSet %0.6f"%(t2-t_attr))	
            log.debug("setClass %0.6f"%(t2-t1))	
        else:
            t2 = time.time()
            log.debug("no setClass. Returning %0.6f"%(t2-t1))	

        _mClass = ATTR.get(_argShort,'mClass')
        if _mClass and _mClass not in _r9ClassRegistry:
            raise ValueError("stored mClass not found in class registry. mClass: {0}".format(_mClass))		
        _mi_arg =  mTypeClass(_argShort)
    else:
        t1 = time.time()				    				
        log.debug("no mType arg...")
        if _mClass:
            if _mClass not in _r9ClassRegistry:
                raise ValueError("stored mClass not found in class registry. mClass: {0}".format(_mClass))			
            mTypeClass = _r9ClassRegistry.get(_mClass)
            log.debug("mClass registered... '{0}' | {1}".format(_argShort,mTypeClass))		    
            _mi_arg =  mTypeClass(_argShort)
        else:
            if default_mType:
                log.debug("no mType.Using default...")
                if not type(default_mType) in [str,str]:
                    try: default_mType = default_mType.__name__
                    except Exception as error:
                        raise ValueError("mType not a string and not a usable class name. default_mType: {0}".format(default_mType))				
                try:_mi_arg =  _r9ClassRegistry.get(default_mType)(_argShort)
                except Exception as error:
                    raise Exception("default mType ({1}) initialization fail | {0}".format(error,default_mType))				
            else:
                if not str_type:str_type = VALID.get_mayaType(_arg)
                
                if str_type == 'controller':
                    log.debug("controller...")
                    try:_mi_arg = cgmController(_argShort) 
                    except Exception as error:
                        raise Exception("cgmController initialization fail | {0}".format(error))	
                elif VALID.is_transform(_argShort):
                    log.debug("Transform...")
                    try:_mi_arg = cgmObject(_argShort) 
                    except Exception as error:
                        raise Exception("cgmObject initialization fail | {0}".format(error))	
                else:
                    log.debug("Node...")
                    try:_mi_arg = cgmNode(_argShort) 
                    except Exception as error:
                        raise Exception("cgmNode initialization fail | {0}".format(error))	
        log.debug("leaving mType None...")
        t2 = time.time()
        log.debug("... %0.6f"%(t2-t1))				

    log.debug("Returning...{0}".format(_mi_arg))
    return _mi_arg	  

def validateObjArgOLD(*args,**kws):
    """
    validate an objArg to be able to get instance of the object

    @kws
    0 - 'arg'(mObject - None) -- mObject instance or string
    1 - 'mType'(mClass - None) -- what mType to be looking for
    2 - 'noneValid'(bool - False) -- Whether None is a valid argument or not
    3 - 'default_mType'(mClass - <class 'cgm.core.cgm_Meta.cgmNode'>) -- What type to initialize as if no mClass is set
    4 - 'mayaType'(str/list - None) -- If the object needs to be a certain object type
    5 - 'setClass'
    """    
    class fncWrap(cgmGEN.cgmFuncCls):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args, **kws)
            self._str_func= "validateObjArg"
            #self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'arg',"default":None,'help':"mObject instance or string","argType":"mObject"},
                                         {'kw':'mType',"default":None,'help':"what mType to be looking for","argType":"mClass"},
                                         {'kw':'noneValid',"default":False,'help':"Whether None is a valid argument or not","argType":"bool"},
                                         {'kw':'default_mType',"default":None,'help':"What type to initialize as if no mClass is set","argType":"mClass"},
                                         {'kw':'mayaType',"default":None,'help':"If the object needs to be a certain object type","argType":"str/list"},
                                         {'kw':'setClass',"default":None,'help':"Flag for reinitialization to this class","argType":"bool"}]	                                 
            self.__dataBind__(*args,**kws)
            #=================================================================

        def __func__(self,*args,**kws):
            #Pull kws local ====================================================================
            arg = self.d_kws['arg']
            mType = self.d_kws['mType']
            noneValid = self.d_kws['noneValid']
            default_mType = self.d_kws['default_mType']
            mayaType = self.d_kws['mayaType']		
            setClass = self.d_kws['setClass']	
            mTypeClass = False
            _r9ClassRegistry = r9Meta.getMClassMetaRegistry()
            _convert = False

            if mType is not None:
                t1 = time.time()
                if not type(mType) in [str,str]:
                    try: mType = mType.__name__
                    except Exception as error:
                        raise ValueError("mType not a string and not a usable class name. mType: {0}".format(mType))	
                if mType not in _r9ClassRegistry:
                    raise ValueError("mType not found in class registry. mType: {0}".format(mType))
                t2 = time.time()
                self.log_debug("initial mType... %0.6f"%(t2-t1))
            #------------------------------------------------------------------------------------
            self.mi_arg = False

            argType = type(arg)
            if argType in [list,tuple]:#make sure it's not a list
                if len(arg) ==1:
                    arg = arg[0]
                elif arg == []:
                    arg = None
                else:raise ValueError("arg cannot be list or tuple or longer than 1 length: %s"%arg)	
            if not noneValid:
                if arg in [None,False]:
                    raise ValueError("Invalid arg({0}). noneValid = False".format(arg))
            else:
                if arg in [None,False]:
                    if arg not in [None,False]:log.warning("%s arg fail: %s"%(self._str_reportStart,arg))
                    return False
            try:
                arg.mNode
                self.mi_arg = arg
                _arg = arg.mNode
                self.log_debug("instance already...")		
            except:
                self.log_debug("not an instance arg...")
                try:_arg = names.getLongName(arg)
                except Exception as err:
                    if noneValid:return False
                    raise err 
            if not _arg:
                if noneValid:return False
                else:
                    raise ValueError("'{0}' is not a valid arg. Validated to {1}".format(arg,_arg))

            _argShort = names.getShortName(_arg)

            self.log_debug("Checking: '{0} | mType: {1}'".format(_arg,mType))
            mTypeClass = _r9ClassRegistry.get(mType)

            if mayaType is not None and len(mayaType):
                t1 = time.time()		
                self.log_debug("Checking mayaType...")
                if type(mayaType) not in [tuple,list]:l_mayaTypes = [mayaType]
                else: l_mayaTypes = mayaType
                #str_type = search.returnObjectType(self.mi_arg.getComponent())
                str_type = SEARCH.get_mayaType(_arg)
                if str_type not in l_mayaTypes:
                    if noneValid:
                        log.warning("%s '%s' mayaType: '%s' not in: '%s'"%(self._str_reportStart,_argShort,str_type,l_mayaTypes))
                        return False
                    raise Exception("'%s' mayaType: '%s' not in: '%s'"%(_argShort,str_type,l_mayaTypes))			    	
                t2 = time.time()
                self.log_debug("mayaType not None time... %0.6f"%(t2-t1))		    

            #Get our cache key
            _mClass = ATTR.get(_argShort,'mClass')

            _UUID2016 = False#...a flag to see if we need a reg UUID attr 
            try:_UUID2016= mc.ls(_argShort, uuid=True)[0]
            except:pass

            if _UUID2016:
                self.log_debug(">2016 UUID: {0}...".format(_UUID2016))
                _UUID = _UUID2016
                try:
                    ATTR.delete(_argShort,'UUID')				    
                    self.log_debug("Clearing attr UUID...")
                except:pass
            else:
                _UUID = ATTR.get(_argShort,'UUID')

            self.log_debug("Cache keys|| UUID: {0} | mClass: {1}".format(_UUID,_mClass))
            _wasCached = False

            #See if it's in the cache
            _keys = list(r9Meta.RED9_META_NODECACHE.keys())
            _cacheKey = None
            _cached = None
            _unicodeArg = str( _arg)

            if _UUID in _keys:
                _cacheKey = _UUID
                _cached = r9Meta.RED9_META_NODECACHE.get(_UUID)
            elif _unicodeArg in _keys:
                _cacheKey = _unicodeArg
                _cached = r9Meta.RED9_META_NODECACHE.get(_unicodeArg)	

            #_cached = r9Meta.RED9_META_NODECACHE.get(_UUID,None) or r9Meta.RED9_META_NODECACHE.get(_arg,None)
            self.log_debug("cacheKey: {0}".format(_cacheKey))

            if _cached is not None:
                t1 = time.time()		
                self.log_debug("Already cached")
                _cachedMClass = ATTR.get(_arg,'mClass') or False
                _cachedType = type(_cached)
                self.log_debug("Cached mNode: {0}".format(_cached.mNode))		
                self.log_debug("Cached mClass: {0}".format(_cachedMClass))
                self.log_debug("Cached Type: {0}".format(_cachedType))
                _change = False
                _redo = False
                #...gonna see if our cache is obviously wrong
                if _arg != _cached.mNode:
                    self.log_debug("mNodes don't match. Need new UUID our our new arg")
                    self.log_debug("Clearing UUID...")
                    #ATTR.delete(_arg,'UUID')	
                    try:ATTR.set(_argShort,'UUID','')
                    except:pass		    
                    _redo = True

                elif _cachedType == mTypeClass:
                    self.log_debug("cachedType({0}) match ({1})".format(_cachedType,mTypeClass))
                    if setClass and not _cachedMClass:
                        self.log_debug("...ensuring proper categorization next time")
                        try:ATTR.add(_argShort, 'mClass','string')
                        except:pass		    
                        try:ATTR.add(_argShort,'UUID','string')
                        except:pass
                        ATTR.set(_argShort,'mClass',mType,True)
                    return _cached

                elif _cachedMClass:#...check our types and subclass stuff
                    if mType is not None:
                        if _cachedType != mTypeClass:
                            self.log_debug("cached Type doesn't match({0})".format(mTypeClass))			    			
                            _change = True
                        elif _cachedMClass != mType:
                            self.log_debug("mClass value ({0}). doesn't match({1})".format(_cachedMClass,mType))
                            _change = True

                        #attributes.storeInfo(_arg, 'mClass', mType, overideMessageCheck=True)
                        #ATTR.add(_arg,'UUID','string')

                else:
                    self.log_debug("No cached mClass or type")
                    _change = True

                    if issubclass(type(_cached), mTypeClass ):
                        self.log_debug("subclass match")
                        _change = False
                        if setClass:
                            self.log_debug("subclass match not good enough")
                            _change = True

                """if _change:
		    self.log_debug("change...")
		    if setClass:
			_convert = True
		    else:
			self.log_debug('bad')
			raise Exception,"[setClass False. mTypeClass: {0} | type:{1}]".format(mTypeClass,
					                                                      type( _cached))	"""	
                if _change:
                    self.log_debug("..subclass check")
                    if issubclass(_cachedType, mTypeClass) and not setClass:
                        self.log_debug("...but is subclass")
                        _change = False
                    else:
                        self.log_debug("...not a subclass")			

                if not _change and not _redo:
                    t2 = time.time()
                    self.log_debug("Cache good %0.6f"%(t2-t1))		    
                    return _cached
                elif _change:
                    self.log_debug("conversion necessary.removing from cache")
                    _wasCached = True
                    if _cachedMClass:
                        self.log_debug("Clearing mClass...")
                        #_cached.mClass = ''
                        ATTR.delete(_argShort,'mClass')
                    if _UUID:
                        self.log_debug("Clearing UUID...")
                        ATTR.delete(_argShort,'UUID')			
                        #_cached.UUID = ''			
                    r9Meta.RED9_META_NODECACHE.pop(_cacheKey)

                t2 = time.time()
                self.log_debug("Cache check %0.6f"%(t2-t1))	

            if mType:
                t1 = time.time()				    		
                if setClass or _wasCached:
                    self.log_debug("setClass...")
                    #attributes.storeInfo(_arg, 'mClass', mType, overideMessageCheck=True)
                    t_attr = time.time()				    		
                    try:ATTR.add(_argShort, 'mClass','string')
                    except:pass		    
                    try:
                        if not _UUID2016:
                            ATTR.add(_argShort,'UUID','string')
                    except:pass
                    ATTR.set(_argShort,'mClass',mType,True)
                    t2 = time.time()		    
                    self.log_debug("attrSet %0.6f"%(t2-t_attr))	
                    self.log_debug("setClass %0.6f"%(t2-t1))	
                else:
                    t2 = time.time()
                    self.log_debug("no setClass. Returning %0.6f"%(t2-t1))	

                _mClass = ATTR.get(_argShort,'mClass')
                if _mClass and _mClass not in _r9ClassRegistry:
                    raise ValueError("stored mClass not found in class registry. mClass: {0}".format(_mClass))		
                self.mi_arg =  mTypeClass(_argShort)
            else:
                t1 = time.time()				    				
                self.log_debug("no mType arg...")
                if _mClass:
                    if _mClass not in _r9ClassRegistry:
                        raise ValueError("stored mClass not found in class registry. mClass: {0}".format(_mClass))			
                    mTypeClass = _r9ClassRegistry.get(_mClass)
                    self.log_debug("mClass registered... '{0}' | {1}".format(_argShort,mTypeClass))		    
                    self.mi_arg =  mTypeClass(_argShort)
                else:
                    if default_mType:
                        self.log_debug("no mType.Using default...")
                        if not type(default_mType) in [str,str]:
                            try: default_mType = default_mType.__name__
                            except Exception as error:
                                raise ValueError("mType not a string and not a usable class name. default_mType: {0}".format(default_mType))				
                        try:self.mi_arg =  _r9ClassRegistry.get(default_mType)(_argShort)
                        except Exception as error:
                            raise Exception("default mType ({1}) initialization fail | {0}".format(error,default_mType))				
                    elif isTransform(_argShort):
                        self.log_debug("Transform...")
                        try:self.mi_arg = cgmObject(_argShort) 
                        except Exception as error:
                            raise Exception("cgmObject initialization fail | {0}".format(error))	
                    else:
                        self.log_debug("Node...")
                        try:self.mi_arg = cgmNode(_argShort) 
                        except Exception as error:
                            raise Exception("cgmNode initialization fail | {0}".format(error))	
                self.log_debug("leaving mType None...")
                t2 = time.time()
                self.log_debug("... %0.6f"%(t2-t1))				

            self.log_debug("Returning...{0}".format(self.mi_arg))
            return self.mi_arg	  
    return fncWrap(*args,**kws).go()  







def validateObjListArg(l_args = None, mType = None, noneValid = False, default_mType = None, mayaType = None, setClass = False):
    """
    validate an objArg to be able to get instance of the object

    @kws
    0 - 'arg'(mObject - None) -- mObject instance or string
    1 - 'mType'(mClass - None) -- what mType to be looking for
    2 - 'noneValid'(bool - False) -- Whether None is a valid argument or not
    3 - 'default_mType'(mClass - <class 'cgm.core.cgm_Meta.cgmNode'>) -- What type to initialize as if no mClass is set
    4 - 'mayaType'(str/list - None) -- If the object needs to be a certain object type
    5 - 'setClass'
    """    
    _str_fun = 'validateObjArg'
    if type(l_args) not in [list,tuple]:l_args = [l_args]
    returnList = []
    kws = {'mType':mType,'noneValid':noneValid,'default_mType':default_mType,'mayaType':mayaType,'setClass':setClass}
    for arg in l_args:
        buffer = validateObjArg(arg,**kws)
        if buffer:returnList.append(buffer)
    return returnList	        
    
def validateObjListArgOLD(*args,**kws):
    """
    validate an objArg to be able to get instance of the object

    @kws
    0 - 'l_args'(mObjects - None) -- mObject instance or string list
    1 - 'mType'(mClass - None) -- what mType to be looking for
    2 - 'noneValid'(bool - False) -- Whether None is a valid argument or not
    3 - 'default_mType'(mClass - <class 'cgm.core.cgm_Meta.cgmNode'>) -- What type to initialize as if no mClass is set
    4 - 'mayaType'(str/list - None) -- If the object needs to be a certain object type
    """    
    class fncWrap(cgmGEN.cgmFuncCls):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args, **kws)
            self._str_func= "validateObjListArg"			    
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'l_args',"default":None,'help':"mObject instance or string list","argType":"mObjects"},
                                         {'kw':'mType',"default":None,'help':"what mType to be looking for","argType":"mClass"},
                                         {'kw':'noneValid',"default":False,'help':"Whether None is a valid argument or not","argType":"bool"},
                                         {'kw':'default_mType',"default":cgmNode,'help':"What type to initialize as if no mClass is set","argType":"mClass"},
                                         {'kw':'mayaType',"default":None,'help':"If the object needs to be a certain object type","argType":"str/list"},
                                         {'kw':'setClass',"default":None,'help':"Flag for reinitialization to this class","argType":"bool"}]	                                 

            self.__dataBind__(*args,**kws)
            #=================================================================

        def __func__(self,*args,**kws):
            #Pull kws local ====================================================================
            l_args = self.d_kws['l_args']
            mType = self.d_kws['mType']	    
            noneValid = self.d_kws['noneValid']
            default_mType = self.d_kws['default_mType']
            mayaType = self.d_kws['mayaType']
            kws = self.d_kws
            #------------------------------------------------------------------------------------
            if type(l_args) not in [list,tuple]:l_args = [l_args]
            returnList = []
            for arg in l_args:
                buffer = validateObjArg(arg,**kws)
                if buffer:returnList.append(buffer)
            return returnList	    
    return fncWrap(*args,**kws).go()

#Attr validation ===============================================================================================================
'''
def validateAttrArg(*args,**kws):
    """
    Validate an attr arg to usable info


    """    
    class fncWrap(cgmGEN.cgmFuncCls):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_func= "validateAttrArg"			    
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'arg',"default":None,
	                                  'help':"Arg should be sting 'obj.attr' or ['obj','attr'] format","argType":"mObjects"},
	                                 {'kw':'defaultType',"default":'float','help':"Attr type to look for","argType":"string"},
	                                 {'kw':'noneValid',"default":False,'help':"Whether None is a valid argument or not","argType":"bool"}]	                                 
	    self.__dataBind__(*args,**kws)
	    #=================================================================

	def __func__(self,*args,**kws):
	    #Pull kws local ====================================================================
	    arg = self.d_kws['arg']
	    defaultType = self.d_kws['defaultType']	    
	    noneValid = self.d_kws['noneValid']
	    kws = self.d_kws
	    mi_obj = False
	    #------------------------------------------------------------------------------------
	    try:
		try:
		    combined = arg.p_combinedName
		    obj = arg.obj.mNode
		    attr = arg.attr
		    mi_obj = arg
		    return {'obj':obj ,'attr':attr ,'combined':combined,'mi_plug':arg}
		except:
		    if type(arg) in [list,tuple]:
			if  len(arg) == 2:
			    try:
				obj = arg[0].mNode
				mi_obj = arg[0]
			    except:
				obj = arg[0]
			    attr = arg[1]
			    combined = "%s.%s"%(obj,attr)
			elif len(arg) == 1:
			    arg = arg[0]
			    obj = arg.split('.')[0]
			    attr = '.'.join(arg.split('.')[1:])
			    combined = arg		    
		    elif '.' in arg:
			obj = arg.split('.')[0]
			attr = '.'.join(arg.split('.')[1:])
			combined = arg
		    else:raise StandardError,"validateAttrArg>>>Bad attr arg: %s"%arg
		if not mc.objExists(obj):
		    raise StandardError,"validateAttrArg>>>obj doesn't exist: %s"%obj
		if not mc.objExists(combined):
		    if noneValid:
			return False
		    else:
			if mi_obj: i_plug = cgmAttr(mi_obj,attr,attrType=defaultType,**kws)  
			else: i_plug = cgmAttr(obj,attr,attrType=defaultType,**kws)
		elif mi_obj:i_plug = cgmAttr(mi_obj,attr,**kws)	
		else:i_plug = cgmAttr(obj,attr,**kws)
		return {'obj':obj ,'attr':attr ,'combined':combined,'mi_plug':i_plug}
	    except StandardError,error:
		if noneValid:
		    return False	    
    return fncWrap(*args,**kws).go()

'''
def validateAttrArg(arg,defaultType = 'float',noneValid = False,**kws):
    """
    Validate an attr arg to usable info
    Arg should be sting 'obj.attr' or ['obj','attr'] format.
    """
    _str_func = 'validateAttrArg'
    #log.debug(">>> %s >> "%_str_func + "="*75)
    mi_obj = False
    try:
        try:
            combined = arg.p_combinedName
            obj = arg.obj.mNode
            attr = arg.attr
            mi_obj = arg
            return {'obj':obj ,'attr':attr ,'combined':combined,'mi_plug':arg}

        except:
            #log.debug("cgmAttr call failed: %s"%arg)	    
            if type(arg) in [list,tuple]:
                if  len(arg) == 2:
                    try:
                        #log.debug(arg[0].mNode)
                        obj = arg[0].mNode
                        mi_obj = arg[0]
                    except:
                        #log.debug("mNode call fail")
                        obj = arg[0]
                    attr = arg[1]
                    combined = "%s.%s"%(obj,attr)
                elif len(arg) == 1:
                    arg = arg[0]
                    obj = arg.split('.')[0]
                    attr = '.'.join(arg.split('.')[1:])
                    combined = arg		    
            elif '.' in arg:
                obj = arg.split('.')[0]
                attr = '.'.join(arg.split('.')[1:])
                combined = arg
            else:raise Exception("validateAttrArg>>>Bad attr arg: %s"%arg)
        if not mc.objExists(obj):
            raise Exception("validateAttrArg>>>obj doesn't exist: %s"%obj)
        if not mc.objExists(combined):
            if noneValid:
                #log.debug("Not found: '%s'"%combined)
                return False
            else:
                #log.debug("validateAttrArg>>> '%s'doesn't exist, creating attr (%s)!"%(combined,defaultType))
                if mi_obj: i_plug = cgmAttr(mi_obj,attr,attrType=defaultType,**kws)  
                else: i_plug = cgmAttr(obj,attr,attrType=defaultType,**kws)
        elif mi_obj:i_plug = cgmAttr(mi_obj,attr,**kws)	
        else:i_plug = cgmAttr(obj,attr,**kws)
        return {'obj':obj ,'attr':attr ,'combined':combined,'mi_plug':i_plug,'mPlug':i_plug}
    except Exception as err:
        #log.debug("validateAttrArg>>Failure! arg: %s"%arg)	
        if noneValid:
            return False
        raise Exception("{0} >> arg: {1} | defaultType: {2} | noneValid: {3} | {4}".format(_str_func,
                                                                                           arg,
                                                                                           defaultType,noneValid,err))

def validateAttrListArg(l_args = None,defaultType = 'float',noneValid = False,**kws):
    try:
        #log.debug(">>> validateAttrListArg >> l_args = %s"%l_args + "="*75)            	
        if type(l_args) not in [list,tuple]:l_args = [l_args]
        l_mPlugs = []
        l_combined = []
        l_raw = []
        for arg in l_args:
            buffer = validateAttrArg(arg,defaultType,noneValid,**kws)
            if buffer and buffer['combined'] not in l_combined:
                l_mPlugs.append(buffer['mi_plug'])
                l_combined.append(buffer['combined'])
                l_raw.append(buffer)
            else:
                log.warning("validateAttrListArg>> Failed to validate: %s"%arg)		
        #log.debug("validateAttrListArg>> validated: %s"%l_combined)
        return {'ml_plugs':l_mPlugs,'combined':l_combined,'raw':l_raw}
    except Exception as error:
        log.error("validateAttrListArg>>Failure! l_args: %s | defaultType: %s"%(l_args,defaultType))
        raise Exception(error)    

class cgmBlendShape(cgmNode):
    def __init__(self):
        raise DeprecationWarning("cgmBlendshape moved to cgm_Deformers.cgmBlendshape")
    
    
    
class pathList(object):
    def __init__(self, optionVar = 'testPath'):
        self.l_paths = []
        self.mOptionVar = cgmOptionVar(optionVar,'string')
    
    def append(self, arg = None):
        _str_func = 'pathList.append'
        log.debug(cgmGEN.logString_start(_str_func))
        mPath = PATHS.Path(arg)
        if mPath.exists():
            log.debug(cgmGEN.logString_msg(_str_func,'Path exists | {0}'.format(arg)))
            _friendly = mPath.asFriendly()
            self.mOptionVar.append(_friendly)
            self.l_paths.append(_friendly)
            
        else:
            log.warning(cgmGEN.logString_msg(_str_func,'Invalid Path | {0}'.format(arg)))
            
    def verify(self):
        _str_func = 'pathList.verify'
        log.debug(cgmGEN.logString_start(_str_func))
        self.l_paths = []
        
        if type(self.mOptionVar.value) is list:
            for p in self.mOptionVar.value:
                log.debug(p)
                mPath = PATHS.Path(p)
                if not mPath.exists():
                    log.warning(cgmGEN.logString_msg(_str_func,"{} | Path doesn't exist. removing: {}".format(self.mOptionVar.name,p)))
                    #self.mOptionVar.remove(p)
                else:
                    self.l_paths.append(p)
        else:
            _p = self.mOptionVar.value
            mPath = PATHS.Path(_p)
            if not mPath.exists():
                log.warning(cgmGEN.logString_msg(_str_func,"{} | Path doesn't exist. removing: {}".format(self.mOptionVar.name,_p)))
                #self.mOptionVar = ''
            else:
                self.l_paths = [_p]
                
        
        self.l_paths = CORELISTS.get_noDuplicates(self.l_paths)
        self.mOptionVar.clear()
        for p in self.l_paths:
            self.mOptionVar.append(p)


        
        
       
                
    def remove(self,arg = None):
        _str_func = 'pathList.remove'
        log.debug(cgmGEN.logString_start(_str_func))
        self.mOptionVar.remove(arg)
        
    def log_self(self):
        log.info(cgmGEN._str_hardBreak)        
        log.info(cgmGEN.logString_start('pathList.log_self'))
        self.mOptionVar.report()
        
        log.info(cgmGEN.logString_start('//pathList.log_self'))
        log.info(cgmGEN._str_hardBreak)
        
    def clear(self):
        self.mOptionVar.clear()
        self.l_paths = []
        
        
    def append_recent(self,arg=None):
        _str_func = 'pathList.append_recent'
        log.debug(cgmGEN.logString_start(_str_func))
        
        mPath = PATHS.Path(arg)
        self.verify()#...verify to make sure we have a good list

        
        if mPath.exists():
            log.debug(cgmGEN.logString_msg(_str_func,'Path exists | {0}'.format(arg)))
            _friendly = mPath.asFriendly()
            self.l_paths.insert(0,_friendly)
            if len(self.l_paths) > 5:
                self.l_paths = self.l_paths[:5]
                
            self.mOptionVar.value =  self.l_paths
        
    def ui(self):
        pass
        
        
    
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in
