"""
------------------------------------------
nameTools: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class Factory for 
================================================================
"""
# From Python =============================================================
import copy
import re
import pprint
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_General as r9General
import cgm.core.cgm_General as cgmGEN
from cgm.core.cgmPy import str_Utils as strUtils
from cgm.lib import names
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.lib.search_utils as SEARCH
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.transform_utils as TRANS
reload(strUtils)
reload(CORESHARE)
reload(SEARCH)
# From cgm ==============================================================
from cgm.lib import (lists,
                     search,
                     dictionary,
                     settings,
                     attributes)

#namesDictionaryFile = settings.getNamesDictionaryFile()
#typesDictionaryFile = settings.getTypesDictionaryFile()
#settingsDictionaryFile = settings.getSettingsDictionaryFile()
        
#>>>Utilities
#==================================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnSceneObjectsNameDictMap(**a):   
    sceneTransformObjects =  mc.ls(shortNames = True,**a)

    SceneObjectNameDict = {}

    for obj in sceneTransformObjects:
        dictBuffer = returnObjectGeneratedNameDict(obj)
        if dictBuffer:
            SceneObjectNameDict[obj] = dictBuffer

    if not SceneObjectNameDict:
        return False
    return SceneObjectNameDict
      
#@r9General.Timer   
def returnCGMOrder():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the order for names in a list format

    ARGUMENTS:
    Nothin

    RETURNS:
    order(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #dict = dictionary.initializeDictionary(settingsDictionaryFile)
    #orderBuffer = dict.get('nameOrder')
    #return (orderBuffer.split(','))
    return CORESHARE.l_cgmNameOrder

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnCGMDivider():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the divider string

    ARGUMENTS:
    Nothin

    RETURNS:
    divider(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #dict = dictionary.initializeDictionary(settingsDictionaryFile)
    #return dict.get('nameDivider')
    return CORESHARE.str_nameDivider

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnCGMSetting(setting):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the divider string

    ARGUMENTS:
    Nothin

    RETURNS:
    divider(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #dict = dictionary.initializeDictionary(settingsDictionaryFile)
    #return (dict.get(setting))
    return CORESHARE.d_cgmTypes('setting')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnRawGeneratedName(obj,ignore=[False],removeDups=True):
    """  
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated name

    ARGUMENTS:
    obj(string) - object
    ignore(list) -  only culls out cgmtags that are 
                     generated via returnCGMOrder() function

    RETURNS:
    name(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    try:
        rawNamesDict = returnObjectGeneratedNameDict(obj,ignore)
        divider = returnCGMDivider()
        order = returnCGMOrder()
    
        nameBuilder=[]
        #>>> Dictionary driven order
        for item in order:
            buffer = rawNamesDict.get(item)
            if buffer > 0 and item not in ignore:
                if removeDups:
                    if str(buffer) in nameBuilder:
                        continue
                nameBuilder.append(str(buffer))
        return divider.join(nameBuilder)
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnCombinedNameFromDict(nameDict, stripInvalid = True, removeDups=True):
    """  
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated name

    ARGUMENTS:
    obj(string) - object
    ignore(string) - default is 'none', only culls out cgmtags that are 
                     generated via returnCGMOrder() function

    RETURNS:
    name(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    _str_func = "returnCombinedNameFromDict(%s)"%nameDict
    log.debug(">>> %s "%(_str_func) + "="*75)   
    if type(nameDict) is not dict:raise StandardError,"%s >>> nameDict is not type dict. type: %s"%(_str_func,type(nameDict))
    
    divider = returnCGMDivider()
    order = returnCGMOrder()

    nameBuilder=[]
    #>>> Dictionary driven order
    for item in order:
        buffer = nameDict.get(item)
        buffer = str(SEARCH.get_tagInfoShort(buffer,item))
        if buffer.lower() not in ['false','none','ignore',]:
            if removeDups:
                if buffer in nameBuilder:
                    continue
            nameBuilder.append(buffer)
        log.debug("|{0}| >>  buffer: {1}".format(_str_func,nameBuilder))
        
    _str = divider.join(nameBuilder)
    if stripInvalid: _str = strUtils.stripInvalidChars(_str)
    return _str

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_objNameDict(obj,ignore=[False]):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated dictionary of name info

    ARGUMENTS:
    obj(string) - object
    ignore(string) - default is 'none', only culls out cgmtags that are 
                     generated via returnCGMOrder() function

    RETURNS:
    namesDict(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    try:
        _str_funcName = "get_objNameDict"
        log.debug(">>> %s >>> "%(_str_funcName) + "="*75)
        
        if type(ignore) is not list:ignore = [ignore]    
    
        namesDict={}
        divider = returnCGMDivider()
        order = returnCGMOrder()
        nameBuilder = []
        #>>> Get our cgmVar_iables
        #userAttrs = attributes.returnUserAttributes(obj)
        #cgmAttrs = lists.returnMatchList(userAttrs,order)
        #>>> Tag ignoring
        if ignore:
            for i in ignore:
                if i in order:
                    order.remove(i)
    
        #>>> Geting our data
        for tag in order:
            tagInfo = SEARCH.get_tagInfo(obj,tag)
            if tagInfo is not False:
                namesDict[tag] = (tagInfo)
                
        _iterator = ATTR.get(obj,'cgmIterator')
        if _iterator is not False:
            log.debug("Iterator found")
            namesDict['cgmIterator'] = (_iterator)
                
        # remove tags up stream that we don't want if they don't exist on the actual object"""
        if not mc.objExists(obj+'.cgmTypeModifier'):
            if namesDict.get('cgmTypeModifier') != None:
                namesDict.pop('cgmTypeModifier')   
    
        log.debug("%s >>> initial nameDict: %s "%(_str_funcName,namesDict))    
        
        #>>> checks if the names exist as objects or it's a shape node
        ChildNameObj = False
        
        nameObj = False
        cgmNameAttrType = ATTR.get_type(obj,'cgmName')
        log.debug("cgmNameAttrType: {0}".format(cgmNameAttrType))
        
        if cgmNameAttrType == 'message':
            #nameObj = SEARCH.get_nodeTagInfo(obj,'cgmName')
            nameObj = ATTR.get_message(obj,'cgmName',simple=True)#SEARCH.get_nodeTagInfo(obj,'cgmName')
            if nameObj:
                nameObj = nameObj[0]
                nameObjDict = get_objNameDict(nameObj)
                for k in 'cgmDirection','test':
                    if nameObjDict.get(k) and namesDict.get(k):
                        namesDict.pop(k)
                log.debug("nameObj: {0}".format(nameObj))
                namesDict['cgmName'] = nameObj
                return namesDict
        
        typeTag = SEARCH.get_nodeTagInfo(obj,'cgmType')
        isType = SEARCH.VALID.get_mayaType(obj)
        isShape = SEARCH.VALID.is_shape(obj)
        
        """first see if it's a group """
        if isType == 'group' and typeTag == False:
            childrenObjects = TRANS.children_get(obj,False)            
            log.debug("%s >>> group and no typeTag..."%(_str_funcName))            
            """ if it's a transform group """
            groupNamesDict = {}
            if not nameObj:
                groupNamesDict['cgmName'] = childrenObjects[0]
            else:
                groupNamesDict['cgmName'] = nameObj
            groupNamesDict['cgmType'] = CORESHARE.d_cgmTypes.get('transform')
            if namesDict.get('cgmTypeModifier') != None:
                groupNamesDict['cgmTypeModifier'] = namesDict.get('cgmTypeModifier')
            return groupNamesDict
            """ see if there's a name tag"""
        elif isType in ['joint']:
            return namesDict
        elif isShape:
            #If we have a name object or shape
            log.debug("%s >>> nameObj not None or isType is 'shape'..."%(_str_funcName))            
            
            if isShape:
                #log.debug("%s >>> nameObj exists: '%s'..."%(_str_funcName,nameObj))                        
                #Basic child object with cgmName tag
                childNamesDict = {}
                childNamesDict['cgmName'] = namesDict.get('cgmName')
                childNamesDict['cgmType'] = namesDict.get('cgmType')
                if namesDict.get('cgmTypeModifier') != None:
                    childNamesDict['cgmTypeModifier'] = namesDict.get('cgmTypeModifier')
                if namesDict.get('cgmIterator') != None:
                    childNamesDict['cgmIterator'] = namesDict.get('cgmIterator')
                    
                return childNamesDict
            elif isShape or 'Constraint' in isType:
                """if so, it's a child name object"""
                log.debug("%s >>> child name object..."%(_str_funcName))                                    
                childNamesDict = {}
                childNamesDict['cgmName'] = TRANS.parent_get(obj,False)
                childNamesDict['cgmType'] = namesDict.get('cgmType')
                return childNamesDict
            else:
                log.debug("%s >>> No special case found. %s"%(_str_funcName,namesDict))                                                
                return namesDict
        else:
            return namesDict
    except Exception,err:
        raise cgmGEN.cgmExceptCB(Exception,err,msg=vars())
returnObjectGeneratedNameDict = get_objNameDict
