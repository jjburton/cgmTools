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

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.lib import (lists,
                     search,
                     dictionary,
                     settings,
                     attributes)

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()
        
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
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    orderBuffer = dict.get('nameOrder')
    return (orderBuffer.split(','))
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
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    return dict.get('nameDivider')

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
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    return (dict.get(setting))


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnRawGeneratedName(obj,ignore=[False]):
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
    rawNamesDict = returnObjectGeneratedNameDict(obj,ignore)
    divider = returnCGMDivider()
    order = returnCGMOrder()

    nameBuilder=[]
    #>>> Dictionary driven order
    for item in order:
        buffer = rawNamesDict.get(item)
        if buffer > 0 and item not in ignore:
            nameBuilder.append(buffer)
    return divider.join(nameBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def returnCombinedNameFromDict(nameDict):
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
    divider = returnCGMDivider()
    order = returnCGMOrder()

    nameBuilder=[]
    #>>> Dictionary driven order
    for item in order:
        buffer = nameDict.get(item)
        buffer = search.returnTagInfoShortName(buffer,item)
        if buffer > 0 and buffer != 'ignore':
            #if '|' or '[' or ']' in buffer:
            bufferList = list(buffer)
            #log.info("buffer: %s"%buffer)
            returnList = []
            try:
                if int(bufferList[0]) == 0:
                    bufferList.insert(0,'_')
            except:pass
            for i,n in enumerate(bufferList):
                if n == '.':
                    returnList.append('_')
                elif n in [';',':']:
                    returnList.append('to')
                elif n not in ['[',']','|',',']:
                    returnList.append(str(n))
                else:
                    log.debug("nameTools.returnCombinedNameFromDict>> Not sure what to do with: %s"%n)                
            nameBuilder.append(''.join(returnList))
    
    return divider.join(nameBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectGeneratedNameDict(obj,ignore=[False]):
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
    _str_funcName = "returnObjectGeneratedNameDict(%s,ignore = %s)"%(obj,ignore)
    log.debug(">>> %s >>> "%(_str_funcName) + "="*75)    
		
    if type(ignore) is not list:ignore = [ignore]    
    typesDictionary = dictionary.initializeDictionary(typesDictionaryFile)
    namesDictionary = dictionary.initializeDictionary(namesDictionaryFile)
    settingsDictionary = dictionary.initializeDictionary(settingsDictionaryFile)
    namesDict={}
    divider = returnCGMDivider()
    order = returnCGMOrder()
    nameBuilder = []
    #>>> Get our cgmVar_iables
    userAttrs = attributes.returnUserAttributes(obj)
    cgmAttrs = lists.returnMatchList(userAttrs,order)
    #>>> Tag ignoring
    if ignore:
        for i in ignore:
            if i in order:
                order.remove(i)

    #>>> Geting our data
    for tag in order:
        tagInfo = search.findRawTagInfo(obj,tag)
        if tagInfo is not False:
            namesDict[tag] = (tagInfo)
            
    # remove tags up stream that we don't want if they don't exist on the actual object"""
    if not mc.objExists(obj+'.cgmTypeModifier'):
        if namesDict.get('cgmTypeModifier') != None:
            namesDict.pop('cgmTypeModifier')   

    #>>> checks if the names exist as objects or it's a shape node
    ChildNameObj = False
    nameObj = search.returnTagInfo(obj,'cgmName')
    typeTag = search.returnTagInfo(obj,'cgmType')
    isType = search.returnObjectType(obj)
    childrenObjects = search.returnChildrenObjects(obj)
    """first see if it's a group """
    if isType == 'group' and typeTag == False:
        log.debug("group and no typeTag")
        """ if it's a transform group """
        groupNamesDict = {}
        if not nameObj:
            groupNamesDict['cgmName'] = childrenObjects[0]
        else:
            groupNamesDict['cgmName'] = nameObj
        groupNamesDict['cgmType'] = typesDictionary.get('transform')
        if namesDict.get('cgmTypeModifier') != None:
            groupNamesDict['cgmTypeModifier'] = namesDict.get('cgmTypeModifier')
        return groupNamesDict
        """ see if there's a name tag"""
    elif nameObj != None or isType == 'shape':
        #If we have a name object or shape
        log.debug("nameObj not None or isType is 'shape'")
        if mc.objExists(nameObj) and mc.attributeQuery ('cgmName',node=obj,msg=True):
            log.debug("nameObj exists: '%s'"%nameObj)
            #Basic child object with cgmName tag
            childNamesDict = {}
            childNamesDict['cgmName'] = namesDict.get('cgmName')
            childNamesDict['cgmType'] = namesDict.get('cgmType')
            if namesDict.get('cgmTypeModifier') != None:
                childNamesDict['cgmTypeModifier'] = namesDict.get('cgmTypeModifier')
            
            return childNamesDict
        elif isType == 'shape' or 'Constraint' in isType:
            """if so, it's a child name object"""
            childNamesDict = {}
            childNamesDict['cgmName'] = search.returnParentObject(obj,False)
            childNamesDict['cgmType'] = namesDict.get('cgmType')
            return childNamesDict
        elif typeTag == 'infoNull':
            """if so, it's a special case"""
            moduleObj = search.returnMatchedTagObjectUp(obj,'cgmType','module')
            masterObj = search.returnMatchedTagObjectUp(obj,'cgmType','master')
            if moduleObj != False:
                moduleName = returnUniqueGeneratedName(moduleObj,ignore='cgmType')
                childNamesDict = {}
                childNamesDict['cgmName'] = (moduleName+'_'+nameObj)
                childNamesDict['cgmType'] = namesDict.get('cgmType')
                return childNamesDict   
            elif masterObj != False:
                masterName = returnUniqueGeneratedName(masterObj,ignore='cgmType')
                childNamesDict = {}
                childNamesDict['cgmName'] = (masterName+'_'+nameObj)
                childNamesDict['cgmType'] = namesDict.get('cgmType')
                return childNamesDict   
            else:
                return namesDict
        else:
            return namesDict
    else:
        return namesDict

