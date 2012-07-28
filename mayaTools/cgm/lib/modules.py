#=================================================================================================================================================
#=================================================================================================================================================
#	modules - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for finding stuff from our cgm modules
# 
# ARGUMENTS:
# 	Maya
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#   0.11 - 04/04/2011 - added cvListSimplifier
#
# FUNCTION KEY:
#   1) ????
#   2) ????
#   3) ????
#   
#=================================================================================================================================================

import maya.cmds as mc

from cgm.lib.classes import NameFactory 
from cgm.lib import attributes
from cgm.lib import dictionary
from cgm.lib import settings
from cgm.lib import distance
from cgm.lib import search
from cgm.lib import lists
from cgm.lib import rigging
from cgm.lib import guiFactory

import copy
import random

reload(dictionary)
reload(lists)
reload(attributes)

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())
settingsDictionaryFile = settings.getSettingsDictionaryFile()

def cgmTagToFloatAttr(obj,cgmTag,*a, **kw):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Lays out a seies of objects in column and row format

    ARGUMENTS:
    objectList(string)
    columnNumber(int) - number of columns
    
    RETURNS:
    Nada
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    userAttrsData = attributes.returnUserAttrsToDict(obj)
    success = False
    for key in userAttrsData.keys():
        if key == cgmTag:
            try:
                return attributes.addFloatAttributeToObject (obj, userAttrsData.get(key),*a, **kw )
            except:
                return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#  Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnModuleColors(moduleNull):
    direction = search.returnTagInfo(moduleNull,'cgmDirection')
    print direction
    if direction == False:
        return returnSettingsData('colorCenter',True)
    else:
        return returnSettingsData(('color'+direction.capitalize()),True)

def doPurgeNull(null):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Delete all non 'cgm' type user attributes on an object
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    infoNullDict(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    userAttrsData = attributes.returnUserAttrsToDict(null)
    if not userAttrsData:
        return False
    for attr in userAttrsData.keys():
        if 'cgm' not in attr:
            attributes.doDeleteAttr(null,attr)
            guiFactory.warning("Deleted: '%s.%s'"%(null,attr))    

def purgeCGMAttrsFromObject(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Delete all  'cgm' type user attributes on an object
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    infoNullDict(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    userAttrsData = attributes.returnUserAttrsToList(obj)
    attrsToPurge = lists.returnMatchedIndexEntries(userAttrsData,'cgm')
    if len(attrsToPurge):
        for attr in attrsToPurge:
            attributes.doDeleteAttr(obj,attr[0]) 
            guiFactory.warning("Deleted: '%s.%s'"%(obj,attr[0]))
        return True
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Creation Processes
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createMasterNull(characterName='nothingNothing'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a masterNull for a character/asset
    
    ARGUMENTS:
    characterName(string)
    
    RETURNS:
    masterNull(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if characterName == 'nothingNothing':
        randomOptions = ['David','Josh','NameMe','Homer','Georgie']
        characterName = random.choice(randomOptions)
    
    #Create main null
    masterNullBuffer = mc.group (empty=True)
    attributes.storeInfo(masterNullBuffer,'cgmName',characterName)   
    attributes.storeInfo(masterNullBuffer,'cgmType','ignore')
    attributes.storeInfo(masterNullBuffer,'cgmModuleType','master')
    masterNull = NameFactory.doNameObject(masterNullBuffer)
    
    #Create modules container null
    modulesGroupBuffer = mc.group (empty=True)
    attributes.storeInfo(modulesGroupBuffer,'cgmName','modules')   
    attributes.storeInfo(modulesGroupBuffer,'cgmType','group')
    modulesGroup = NameFactory.doNameObject(modulesGroupBuffer)
    modulesGroup = rigging.doParentReturnName(modulesGroup,masterNull)
    attributes.storeObjectToMessage (modulesGroup, masterNull, 'modulesGroup')
    
    #Create modules container null
    meshGroupBuffer = mc.group (empty=True)
    attributes.storeInfo(meshGroupBuffer,'cgmName','geo')   
    attributes.storeInfo(modulesGroupBuffer,'cgmType','group')
    meshGroup = NameFactory.doNameObject(modulesGroupBuffer)
    meshGroup = rigging.doParentReturnName(meshGroup,masterNull)
    attributes.storeObjectToMessage (meshGroup, masterNull, 'geoGroup')
    
    #Create master info null
    masterInfoNull = createInfoNull('master')
    attributes.storeObjectToMessage (masterInfoNull, masterNull, 'info')
    masterInfoNull = rigging.doParentReturnName(masterInfoNull,masterNull)
    
    #Create modules info null
    modulesInfoNull = createInfoNull('modules')
    attributes.storeObjectToMessage (modulesInfoNull, masterInfoNull, 'modules')
    modulesInfoNull = rigging.doParentReturnName(modulesInfoNull,masterInfoNull)
    
    #Create mesh info null
    meshInfoNull = createInfoNull('geo')
    attributes.storeObjectToMessage (meshInfoNull, masterInfoNull, 'geo')
    modulesInfoNull = rigging.doParentReturnName(meshInfoNull,masterInfoNull)
    
    #Create global settings info null
    settingsInfoNull = createInfoNull('settings')
    attributes.storeObjectToMessage (settingsInfoNull, masterInfoNull, 'settings')
    settingsInfoNull = rigging.doParentReturnName(settingsInfoNull,masterInfoNull)
    defaultFont = returnSettingsData('defaultTextFont')
    attributes.storeInfo(settingsInfoNull,'font',defaultFont)

    return masterNull
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def createInfoNull(infoType):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates an infoNull
    
    ARGUMENTS:
    infoType(string)
    
    RETURNS:
    infoNull(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    createBuffer = mc.group (empty=True)
    attributes.storeInfo(createBuffer,'cgmName',infoType)
    attributes.storeInfo(createBuffer,'cgmType','infoNull')
    mc.xform (createBuffer, os=True, piv= (0,0,0)) 
    infoNull = NameFactory.doNameObject(createBuffer,True)
    return infoNull
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Basic Processes
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def saveTemplateToModule(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
	* Save the new positional information from the template objects
	* Collect all names of objects for a delete list
	* If anything in the module doesn't belong there, un parent it, report it
		* like a template object parented to another obect

    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """  
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Variables
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Get our base info
    """ module null data """
    moduleNullData = attributes.returnUserAttrsToDict(moduleNull)
        
    """ part name """
    partName = NameFactory.returnUniqueGeneratedName(moduleNull, ignore = 'cgmType')
    partType = moduleNullData.get('cgmModuleType')
    direction = moduleNullData.get('cgmDirection')
    
    """ template null """
    templateNull = moduleNullData.get('templateNull')
    templateNullData = attributes.returnUserAttrsToDict(templateNull)
    
    """ template object nulls """
    templatePosObjectsInfoNull = returnInfoTypeNull(moduleNull,'templatePosObjects')
    templatePosObjectsInfoData = attributes.returnUserAttrsToDict (templatePosObjectsInfoNull)
    templateControlObjectsNull = returnInfoTypeNull(moduleNull,'templateControlObjects')
    templateControlObjectsData = attributes.returnUserAttrsToDict (templateControlObjectsNull)

    
    """ rig null """
    rigNull = moduleNullData.get('rigNull')
    
    """ Start objects stuff """
    templateStarterDataInfoNull = returnInfoTypeNull(moduleNull,'templateStarterData')
    templateControlObjectsDataNull = returnInfoTypeNull(moduleNull,'templateControlObjectsData')

    """ AutonameStuff """
    divider = NameFactory.returnCGMDivider()    
    moduleRootBuffer =  returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    moduleRoot = moduleRootBuffer[0]
    templateObjects = []
    coreNamesArray = [] 
    #>>>TemplateInfo
    for key in templatePosObjectsInfoData.keys():
        if (mc.attributeQuery (key,node=templatePosObjectsInfoNull,msg=True)) == True:
            templateObjects.append (templatePosObjectsInfoData[key])
        coreNamesArray.append (key)
    
    posTemplateObjects = []
    """ Get the positional template objects"""
    for obj in templateObjects:
        bufferList = obj.split(divider)
        if (typesDictionary.get('templateObject')) in bufferList:
            posTemplateObjects.append(obj)
    """ get our control template objects """
    controlTemplateObjects=[]
    for key in templateControlObjectsData.keys():
        if (mc.attributeQuery (key,node=templateControlObjectsNull,msg=True)) == True:
            controlTemplateObjects.append (templateControlObjectsData[key])

    """put objects in order of closeness to root"""
    posTemplateObjects = distance.returnDistanceSortedList(moduleRoot,posTemplateObjects)
    controlTemplateObjects = distance.returnDistanceSortedList(moduleRoot,controlTemplateObjects)
    curve = (templatePosObjectsInfoData['curve'])
    
    #>>> get our orientation helpers
    helperObjects = []
    for obj in posTemplateObjects:
        helperObjects.append(attributes.returnMessageObject(obj,'orientHelper'))
        
    masterOrient = (attributes.returnMessageObject(moduleRoot,'orientHelper'))
    
    print ('%s%s'% (moduleNull,' data acquired...'))
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Save Data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Get the data
    """ pos objects """
    storageData = []
    for obj in posTemplateObjects:
        storageData.append(mc.xform (obj, q=True, ws=True, sp=True))
    
    """ orientation helpers """
    for obj in helperObjects:
        storageData.append(mc.xform (obj,  q=True, os=True, ro=True))
        
    storageData.append(mc.xform (masterOrient, q=True, os=True, ro=True))
    print storageData
    """ template control objects data"""
    tempateControlObjectsStorageData = []
    for obj in controlTemplateObjects:
        print obj
        tempateControlObjectsStorageData.append(mc.xform (obj, q=True, ws=True, t=True))
        tempateControlObjectsStorageData.append(mc.xform (obj,  q=True, os=True, ro=True))
        rootScale = (mc.xform (moduleRoot, q=True, relative = True, scale=True))
        objScaleBuffer = (mc.xform (obj, q=True, relative = True, scale=True))
        objScale = []
        cnt = 0
        for scale in objScaleBuffer:
            objScale.append(scale*rootScale[cnt])
            cnt+=1
        tempateControlObjectsStorageData.append(objScale)
    print tempateControlObjectsStorageData

    #>>> Store the data to the initial objects pos
    """ Get the attributes to store to"""
    initialObjectsTemplateDataBuffer = attributes.returnUserAttrsToList(templateStarterDataInfoNull)
    initialObjectsPosData = lists.removeMatchedIndexEntries(initialObjectsTemplateDataBuffer,'cgm')

    """ store it"""
    cnt=0
    for set in initialObjectsPosData:
        attrBuffer = set[0]
        xBuffer = (templateStarterDataInfoNull+'.'+attrBuffer+'X')
        yBuffer = (templateStarterDataInfoNull+'.'+attrBuffer+'Y')
        zBuffer = (templateStarterDataInfoNull+'.'+attrBuffer+'Z')
        dataSet = storageData[cnt]
        mc.setAttr (xBuffer, dataSet[0])
        mc.setAttr (yBuffer, dataSet[1])
        mc.setAttr (zBuffer, dataSet[2])
        cnt+=1
        
    #>>> Store the data to the initial objects pos
    """ Get the attributes to store to"""
    templateControlObjectsDataNullBuffer = attributes.returnUserAttrsToList(templateControlObjectsDataNull)
    templateControlObjectsData = lists.removeMatchedIndexEntries(templateControlObjectsDataNullBuffer,'cgm')
    
    """ store it"""
    cnt=0
    for set in templateControlObjectsData:
        attrBuffer = set[0]
        xBuffer = (templateControlObjectsDataNull+'.'+attrBuffer+'X')
        yBuffer = (templateControlObjectsDataNull+'.'+attrBuffer+'Y')
        zBuffer = (templateControlObjectsDataNull+'.'+attrBuffer+'Z')
        dataSet = tempateControlObjectsStorageData[cnt]
        mc.setAttr (xBuffer, dataSet[0])
        mc.setAttr (yBuffer, dataSet[1])
        mc.setAttr (zBuffer, dataSet[2])
        cnt+=1 
        
    #>>>>>>need to add locking>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    print ('%s%s'% (moduleNull,' template object positional/rotational/scale data stored...'))
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Save skin joints to skin joints null
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Delete stuff
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ Gather our objects"""
    toDeleteList = search.returnObjectsOwnedByModuleNull(templateNull)
    print toDeleteList
    
    for obj in toDeleteList:
        if mc.objExists(obj) == True:
            print ('%s%s'% (obj,' deleted...'))
            mc.delete(obj)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Change Tag
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    mc.setAttr ((moduleNull+'.templateState'), 0)
    mc.setAttr ((moduleNull+'.skeletonState'), 1)
    
    #add locking
    
    print ('%s%s'% (moduleNull,' done'))
    return 'done'



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Joints Specific
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnSegmentedJointList(limbJoints):
    cullList = copy.copy(limbJoints)
    
    """put objects in order of closeness to root"""
    cullList = distance.returnDistanceSortedList(cullList[0],cullList)
    
    #>>> Segment our joint list by names
    jointSegmentsList = []
    
    while len(cullList) > 0:
        matchTerm = search.returnTagInfo(cullList[0],'cgmName')
        objSet = returnMatchedTagsFromObjectList(cullList,'cgmName',matchTerm)
        jointSegmentsList.append(objSet)
        for obj in objSet:
            cullList.remove(obj)
    
    return jointSegmentsList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Logic Checks
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def moduleStateCheck(obj,stateChecks):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Easy way to check the status of a module by inputing the checks to....check
    
    ARGUMENTS:
    moduleNull(string)
    state(list) - ['template','skeleton','rig']
    
    
    RETURNS:
    nestedDict(dict) - nested dictionary of various null's infos
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    moduleNull= search.returnObjectModule(obj)
    checkLists = []
    for check in stateChecks:
        checkLists.append(mc.getAttr (('%s%s%s%s' % (moduleNull,'.',check,'State'))))
    if len(checkLists) == 1:
        return checkLists[0]
    else:        
        cnt=1
        check = checkLists[0]
        for i in range(len(checkLists[1:])):
            check = check * checkLists[cnt]
            cnt+=1
        return check
    
    
    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Data
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDirectionalInfo(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns directional info from a module to a list and False 
    in an entry if no data is there
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    direction(list) - ['left','front'], [False,'back'] etc
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnList = []
    returnList.append(search.returnTagInfo(moduleNull,'cgmDirection'))
    returnList.append(search.returnTagInfo(moduleNull,'cgmPosition'))
    return returnList
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def returnDirectionalInfoToString(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns directional info from a module to a string and 'None' if 
    there is not directional info
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    direction(string) - 'left_front'
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    info = returnDirectionalInfo(moduleNull)
    formatInfoCatch = []
    for i in info:
        if i != False:
            formatInfoCatch.append(i)
            
    if len(formatInfoCatch) >0:
        return ('_'.join(formatInfoCatch))
    elif len(formatInfoCatch) ==0 :
        return 'None'

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnSettingsDataAsFloat(setting):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a particular setting data piece as number info rather than string
    
    ARGUMENTS:
    setting(string)
    
    RETURNS:
    info(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dataBuffer = returnSettingsData(setting)
    print dataBuffer
    returnList = []
    if '|' in list(dataBuffer):
        listSplit = dataBuffer.split('|')
        for pos in listSplit:
            posBufferRaw = pos.split(',')
            posBuffer = []
            for n in posBufferRaw:
                posBuffer.append(float(n))
            returnList.append(posBuffer)
        return returnList
    elif ',' in list(dataBuffer):
        listSplit = dataBuffer.split(',')
        for n in listSplit:
            returnList.append(float(n))
        return returnList
    elif '.' in list(dataBuffer):
        return (float(dataBuffer))
    else:
        return (int(dataBuffer))
        
        

def returnSettingsData(setting,parsed=True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the divider string
    
    ARGUMENTS:
    setting(string) - the dictionary key to get the data from
    
    RETURNS:
    divider(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    dataBuffer = (dict.get(setting))
    if parsed == False:
        return dataBuffer
    else:        
        if '|' in list(dataBuffer):
            return dataBuffer.split('|')
        elif ',' in list(dataBuffer):
            return dataBuffer.split(',')
        else:
            return dataBuffer
            
    
    
def returnInfoNullObjects(moduleNull,infoType,types='templateObject'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the template null of a module
    
    ARGUMENTS:
    moduleNull(string)
    infoType(string)
    
    RETURNS:
    templateNull(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    infoNull = returnInfoTypeNullFromModule(moduleNull,infoType)
    infoNullData = attributes.returnUserAttrsToDict (infoNull)
    infoNullObjects = []
    coreNamesArray = []  
    divider = NameFactory.returnCGMDivider()

    for key in infoNullData.keys():
        if (mc.attributeQuery (key,node=infoNull,msg=True)) == True:
            infoNullObjects.append(infoNullData[key])
        coreNamesArray.append (key)
        
    if types == 'all':
        return infoNullObjects
    else:
        returnBuffer = []
        for obj in infoNullObjects:
            bufferList = obj.split(divider)
            if typesDictionary.get(types) in bufferList:
                returnBuffer.append(obj)
        return returnBuffer


def returnPartNestedMessages(partNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a nested dictionary of template objects info connected to a part
    
    ARGUMENTS:
    partNull(obj)
    
    RETURNS:
    nestedDict(dict) - nested dictionary of various null's infos
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objectsDict = attributes.returnMessageAttrs(partNull)
    returnDict = {}
    for key in objectsDict.keys():
        returnDict[key] =  attributes.returnMessageAttrs(objectsDict[key])
    return returnDict

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returncgmTemplatePartPositionData(part):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the order for names in a list format
    
    ARGUMENTS:
    Nothin
    
    RETURNS:
    settings(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    returnList = []
    listBuffer = dict.get('%s%s'%(part,'_PositionalData'))
    if listBuffer != None:
        listSplit = listBuffer.split('|')
        for pos in listSplit:
            posBufferRaw = pos.split(',')
            posBuffer = []
            for n in posBufferRaw:
                posBuffer.append(float(n))
            returnList.append(posBuffer)
        return returnList
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returncgmTemplatePartNames(part):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the part names for a part
    
    ARGUMENTS:
    Nothin
    
    RETURNS:
    settings(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    settingsBuffer = dict.get('%s%s'%(part,'_TemplateParts'))
    if settingsBuffer > 0:
        return (settingsBuffer.split(','))
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returncgmTemplateCoreNames(part):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the part names for a part
    
    ARGUMENTS:
    Nothin
    
    RETURNS:
    settings(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    settingsBuffer = dict.get('%s%s'%(part,'_NameList'))
    if settingsBuffer > 0:
        return (settingsBuffer.split(','))
    else:
        return False
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returncgmTemplateSizeRatios(part):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the part names for a part
    
    ARGUMENTS:
    Nothin
    
    RETURNS:
    settings(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    settingsBuffer = dict.get('%s%s'%(part,'_sizeRatios'))
    if settingsBuffer > 0:
        splitBufferRaw = (settingsBuffer.split(','))
        returnBuffer = []
        for n in splitBufferRaw:
            returnBuffer.append(float(n))
        return returnBuffer
    else:
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Template Null
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnTemplateNull(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the template null of a module
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    templateNull(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    return (attributes.returnMessageObject(moduleNull,'templateNull'))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnTemplateObjects(moduleNull,types='templateObject'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the template null of a module
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    templateNull(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    templateNull = returnTemplateNull(moduleNull)
    templateNullData = attributes.returnUserAttrsToDict (templateNull)
    templateObjects = []
    coreNamesArray = []  
    divider = NameFactory.returnCGMDivider()

    for key in templateNullData.keys():
        if (mc.attributeQuery (key,node=templateNull,msg=True)) == True:
            templateObjects.append(templateNullData[key])
        coreNamesArray.append (key)
        
    if types == 'all':
        return templateObjects
    else:
        returnBuffer = []
        for obj in templateObjects:
            bufferList = obj.split(divider)
            if (typesDictionary.get(types)) in bufferList:
                returnBuffer.append(obj)
        return returnBuffer

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def returnSceneModules():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns all modules in a scene file
    
    ARGUMENTS:
    
    
    RETURNS:
    moduleList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """  
    transformsList = mc.ls(tr=True)
    moduleList = []
    for obj in transformsList:
        userAttrsBuffer = attributes.returnUserAttributes(obj)
        if userAttrsBuffer > 0:
            for attr in userAttrsBuffer:
                if attr == 'cgmType':
                    attrBuffer = mc.getAttr('%s%s%s'%(obj,'.',attr))
                    if attrBuffer == 'module':
                        moduleList.append(obj)  
    return moduleList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnOrderedChildrenModules(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns children parts organized by part type and direction
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    returnDict(dict) - {type:{direction:['1','2'
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modules = returnSceneModules()
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Info gathering
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    moduleParents ={}
    for module in modules:
        moduleParents[module] = attributes.returnMessageObject(module,'moduleParent')
    print moduleParents
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Parsing out Children
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    childrenModules = []
    
    """ first we're gonna find all modules that have our module as it's parent"""
    for key in moduleParents.keys():
        if moduleParents.get(key) == moduleNull:
            childrenModules.append(key)

    print childrenModules
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Further parsing
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    moduleTypes = {}
    typesPresent = []
    """ first get the types and a simplified types present list """
    for module in childrenModules:
        isType = search.returnTagInfo(module,'cgmModuleType')
        typesPresent.append(isType)
        moduleTypes[module] = isType 
        
    typesPresent = lists.returnListNoDuplicates(typesPresent)
    
    """ get the data together for return """
    moduleDirectionalInfo = {}
    directionsPresent = []
    for module in childrenModules:
        isDirection = returnDirectionalInfoToString(module)
        directionsPresent.append(isDirection)
        moduleDirectionalInfo[module] = isDirection
        
    directionsPresent = lists.returnListNoDuplicates(directionsPresent)
        
    returnDict = {}
    for t in typesPresent:
        tagBuffer = {}
        for d in directionsPresent:
            dBuffer = []
            for module in childrenModules:
                if moduleTypes.get(module) == t:
                    if moduleDirectionalInfo.get(module) == d:
                        dBuffer.append(module)
            if len(dBuffer) > 0:
                tagBuffer[d] = dBuffer
        returnDict[t] = tagBuffer
        
    if len(returnDict) > 0:
        return returnDict
    else:
        return False
        
          
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnOrderedParentModules(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns ordered list of modules connected to a master that have children
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    orderedModules(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    modules = returnSceneModules()
    
    moduleParents ={}
    for module in modules:
        moduleParents[module] = attributes.returnMessageObject(module,'moduleParent')

    moduleChildren ={}
    for module in modules:
        childrenBuffer = []
        for checkModule in modules:
            if attributes.returnMessageObject(checkModule,'moduleParent') == module:
                childrenBuffer.append(checkModule)
        if len(childrenBuffer) >  0:
            moduleChildren[module] = childrenBuffer
    
    orderedModules = []
    for key in moduleChildren.keys():
        if moduleParents.get(key) == masterNull:
            orderedModules.append(key)
            moduleChildren.pop(key)

    """ parse out the parent modules through the remaning modules"""
    while len(moduleChildren)>0:
        for module in orderedModules:
            for key in moduleChildren.keys():
                if moduleParents.get(key) == module:
                    orderedModules.append(key)
                    moduleChildren.pop(key)
 
    return orderedModules


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnOrderedModules(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reads all of the modules attached to a masterNull and orders them 
    by moduleParent heirarchy
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    orderedModules(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    modules = returnSceneModules()
    
    moduleParents ={}
    for module in modules:
        moduleParents[module] = attributes.returnMessageObject(module,'moduleParent')
        
    orderedModules = []
    for key in moduleParents.keys():
        if moduleParents.get(key) == masterNull:
            orderedModules.append(key)
            moduleParents.pop(key)

    while len(moduleParents)>0:
        for module in orderedModules:
            for key in moduleParents.keys():
                if moduleParents.get(key) == module:
                    orderedModules.append(key)
                    moduleParents.pop(key)
    
    return orderedModules
        
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        

def returnModules(masterNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns all the modules connected to a master null
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    modules(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    modulesNull = returnInfoTypeNull(masterNull,'modules')
    moduleNames = attributes.returnMessageAttrs(modulesNull)
    modules = []
    for module in moduleNames:
        modules.append(attributes.returnMessageObject(modulesNull,module))
    return modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Info Null
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def returnInfoNullsFromModule(moduleNull):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns all info nulls of a module as a dictionary
    
    ARGUMENTS:
    moduleNull(string)
    
    RETURNS:
    infoNullDict(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    moduleInfoNull = attributes.returnMessageObject(moduleNull,'info')
    return attributes.returnUserAttrsToDict(moduleInfoNull)
    
    
def returnInfoTypeNullFromModule(moduleNull,infoType):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns an info null from a module
    
    ARGUMENTS:
    masterNull(string)
    infoType(string)
    
    RETURNS:
    infoNull(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    moduleInfoNull = attributes.returnMessageObject(moduleNull,'info')
    infoNull = attributes.returnMessageObject(moduleInfoNull,infoType)
    return infoNull

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnInfoTypeNull(masterNull,infoType):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns an info null from a masterNull
    
    ARGUMENTS:
    masterNull(string)
    infoType(string)
    
    RETURNS:
    infoNull(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    masterInfoNull = attributes.returnMessageObject(masterNull,'info')
    infoNull = attributes.returnMessageObject(masterInfoNull,infoType)
    return infoNull

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Puppet Nulls
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def returnPuppetObjects():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Looks for master objects and returns a list of the objects
    
    ARGUMENTS:
    nothing
    
    RETURNS:
    masterList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    transformsList = mc.ls(tr=True)
    mastersList = []
    for obj in transformsList:
        userAttrsBuffer = attributes.returnUserAttributes(obj)
        if userAttrsBuffer > 0:
            for attr in userAttrsBuffer:
                if attr == 'cgmModuleType':
                    attrBuffer = mc.getAttr('%s%s%s'%(obj,'.',attr))
                    if attrBuffer == 'master':
                        mastersList.append(obj)
                        
    return mastersList


