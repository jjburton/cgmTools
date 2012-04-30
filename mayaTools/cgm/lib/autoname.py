#=================================================================================================================================================
#=================================================================================================================================================
#	autoname - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for finding stuff
# 
# ARGUMENTS:
# 	Maya
# 	search
# 	names
# 	attribute
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
from cgm.lib import search
from cgm.lib import attributes
from cgm.lib import dictionary
from cgm.lib import settings
from cgm.lib import lists
from cgm.lib import guiFactory
from cgm.lib.classes.NameFactory import NameFactory

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Unique Name s
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createTempUniqueNames(objList):
    uniqueNames = []
    for obj in objList:
        nameBuffer = obj
        cnt = 77
        if '|' in list(obj):
            """ find a new one """
            while mc.objExists(nameBuffer) == True:
                nameBuffer = ('%s%s%i' % (obj,'_',cnt))
                cnt+=1
            #storeInfo(obj,'tempNAME',obj,overideMessageCheck = True)
            uniqueNames.append(mc.rename(obj,nameBuffer))
        else:
            uniqueNames.append(obj)
    return uniqueNames


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
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


def returnMatchedNameParents(obj):
    ### input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj

    objGeneratedNameDict = returnObjectGeneratedNameDict(obj)
    #>>> Count our matched name children range
    if objGeneratedNameDict:
        parents = search.returnAllParents(obj)
        matchList = []
        if parents:
            parents.reverse()
            for c in parents :
                cGeneratedName = returnObjectGeneratedNameDict(c)
                if cGeneratedName == objGeneratedNameDict:
                    matchList.append(c)

        if matchList:
            return matchList
        else:
            return []
    else:
        return []

def returnMatchedNameChildren(obj):
    ### input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj

    objGeneratedNameDict = returnObjectGeneratedNameDict(obj)
    #>>> Count our matched name children range
    if objGeneratedNameDict:
        children = mc.listRelatives (obj, allDescendents=True,type='transform',fullPath=True)
        matchList = []
        if children:
            children.reverse()
            for c in children :
                cGeneratedName = returnObjectGeneratedNameDict(c)
                if cGeneratedName == objGeneratedNameDict:
                    matchList.append(c)

        if matchList:
            return matchList
        else:
            return []
    else:
        return []


def returnFastIterateNumber(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Check through a scene to figure out what iterative number an obj

    ARGUMENTS:
    obj(string)

    RETURNS:
    order(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>> input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
    
    objToQuery = NameFactory(obj)
    
    return objToQuery.getFastIterator()

    
    
def returnIterateNumber(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Check through a scene to figure out what iterative number an obj

    ARGUMENTS:
    obj(string)

    RETURNS:
    order(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>> input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
    
    objToQuery = NameFactory(obj)
    objToQuery.getMatchedParents()
    objToQuery.getMatchedChildren()
    
    # First thing we do is if our object has a parent name object, we process from that object back
    if objToQuery.parentNameCnt:
        parentToQuery = NameFactory(objToQuery.matchedParents[0])
        cnt =  parentToQuery.returnIterator()
        cnt =  cnt + objToQuery.parentNameCnt
        # So we have a top parent
        objNameCandidate = objToQuery.objGeneratedNameDict.copy()
        objNameCandidate['cgmIterator'] = str(cnt)
        bufferName = returnCombinedNameFromDict(objNameCandidate)
        # If it exists in our existing tree, it forces a nameModifier tag
        if mc.objExists(bufferName) and not objToQuery.amIMe(bufferName):
            if bufferName not in objToQuery.matchedChildren and bufferName in parentToQuery.matchedChildren:
                attributes.storeInfo(obj,'cgmNameModifier','branched')
                attributes.storeInfo(obj,'cgmIterator',str(cnt))
                print ("%s has a duplicate in the same heirarchy!" %obj)
        #print ("Count after checking name parent is %i" %cnt)
        return cnt
    #otherwise, we process it by itself
    else:
        cnt = objToQuery.returnIterator()
        return cnt
        
        
    


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
def returnUniqueGeneratedName(obj,sceneUnique = False,ignore='none'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated name with iteration for heirarchy objects with the same tag info

    ARGUMENTS:
    obj(string) - object
    ignore(string) - default is 'none', only culls out cgmtags that are 
                     generated via returnCGMOrder() function

    RETURNS:
    name(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>> Dictionary driven order first build
    def doBuildName():
        nameBuilder=[]
        for item in order:
            buffer = updatedNamesDict.get(item)
            # Check for short name
            buffer = search.returnTagInfoShortName(buffer,item)
            if buffer > 0 and buffer != 'ignore':
                nameBuilder.append(buffer)

        return divider.join(nameBuilder)
    
    rawNamesDict = returnObjectGeneratedNameDict(obj,ignore)
    divider = returnCGMDivider()
    updatedNamesDict = returnObjectGeneratedNameDict(obj,ignore)
    order = returnCGMOrder()
    
    if 'cgmName' not in updatedNamesDict.keys():
        buffer = mc.ls(obj,shortNames = True)
        attributes.storeInfo(obj,'cgmName',buffer[0],True)
        updatedNamesDict = returnObjectGeneratedNameDict(obj,ignore)

    coreName = doBuildName()
    
    """ add the iterator to the name dictionary if our object exists"""
    nameFactory = NameFactory(obj)
    
    if not sceneUnique:
        iterator = returnFastIterateNumber(obj)
        if iterator > 0:
            updatedNamesDict['cgmIterator'] = str(iterator)
            coreName = doBuildName()
    else:
        iterator = returnIterateNumber(obj)
        if iterator > 0:
            updatedNamesDict['cgmIterator'] = str(iterator)
            coreName = doBuildName()
    
    return returnCombinedNameFromDict(updatedNamesDict)







#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnRawGeneratedName(obj,ignore='none'):
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
    rawNamesDict = returnObjectGeneratedNameDict(obj,ignore)
    divider = returnCGMDivider()
    order = returnCGMOrder()


    nameBuilder=[]
    #>>> Dictionary driven order
    for item in order:
        buffer = rawNamesDict.get(item)
        if buffer > 0 and buffer != 'ignore':
            nameBuilder.append(buffer)
    return divider.join(nameBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
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
            if '|' or '[' or ']' in buffer:
                bufferList = list(buffer)
                for i in buffer:
                    if i == '[' or i == ']' or i == '|':
                        bufferList.remove(i) 
                    elif i == '.':
                        cnt = buffer.index(i)
                        bufferList.pop(cnt)
                        bufferList.insert(cnt,'_')
                    elif i == ':':
                        cnt = bufferList.index(i)
                        bufferList.pop(cnt)
                        bufferList.insert(cnt,'to')
                buffer = ''.join(bufferList)
                
            nameBuilder.append(buffer)
    
    return divider.join(nameBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectGeneratedNameDict(obj,ignore='none'):
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
    if ignore != 'none':
        if ignore in order:
            order.remove(ignore)

    #>>> Geting our data
    for tag in order:
        tagInfo = search.findRawTagInfo(obj,tag)
        if tagInfo is not False:
            namesDict[tag] = (tagInfo)
    """ remove tags up stream that we don't want if they don't exist on the actual object"""
    if mc.objExists(obj+'.cgmTypeModifier') != True:
        if namesDict.get('cgmTypeModifier') != None:
            namesDict.pop('cgmTypeModifier')   


    #>>> checks if the names exist as objects or it's a shape node
    ChildNameObj = False
    nameObj = search.returnTagInfo(obj,'cgmName')
    typeTag = search.returnTagInfo(obj,'cgmType')
    isType = search.returnObjectType(obj)
    childrenObjects = search.returnChildrenObjects(obj)
    """first see if it's a group """
    if childrenObjects > 0 and isType == 'transform' and typeTag == False:
        """ if it's a transform group """
        groupNamesDict = {}
        if not nameObj:
            groupNamesDict['cgmName'] = childrenObjects[0]
        else:
            groupNamesDict['cgmName'] = nameObj
        groupNamesDict['cgmType'] = typesDictionary.get('transform')
        if namesDict.get('cgmDirection') != None:
            groupNamesDict['cgmDirection'] = namesDict.get('cgmDirection')
        if namesDict.get('cgmDirectionModifier') != None:
            groupNamesDict['cgmDirectionModifier'] = namesDict.get('cgmDirectionModifier')
        if namesDict.get('cgmTypeModifier') != None:
            groupNamesDict['cgmTypeModifier'] = namesDict.get('cgmTypeModifier')
        return groupNamesDict
        """ see if there's a name tag"""
    elif nameObj != None or isType == 'shape':
        """if there is, does it exist """
        if mc.objExists(nameObj) == True:
            """basic child object with cgmName tag """
            childNamesDict = {}
            childNamesDict['cgmName'] = namesDict.get('cgmName')
            childNamesDict['cgmType'] = namesDict.get('cgmType')
            if namesDict.get('cgmDirection') != None:
                childNamesDict['cgmDirection'] = namesDict.get('cgmDirection')
            if namesDict.get('cgmNameModifier') != None:
                childNamesDict['cgmNameModifier'] = namesDict.get('cgmNameModifier')
            if namesDict.get('cgmDirectionModifier') != None:
                childNamesDict['cgmDirectionModifier'] = namesDict.get('cgmDirectionModifier')
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


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Functions that do stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doNameObject(obj,sceneUnique = False):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Names an object, when forceOverride is False, will select conflicting objects

    ARGUMENTS:
    obj(string) - the object we'd like to name
    forceOverride(bool)- whether to rename conflicts or not

    RETURNS:
    newName(string) on success
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    ### input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
    name = returnUniqueGeneratedName(obj,sceneUnique = sceneUnique)
    nameFactory = NameFactory(obj)
    
    if nameFactory.amIMe(name):
        guiFactory.warning("'%s' is already named correctly."%nameFactory.nameBase)
        return name
    else:
        objLong = mc.ls(obj,long=True)
        renameBuffer = mc.rename(objLong,name)

        shapes = mc.listRelatives(renameBuffer,shapes=True,fullPath=True)
        if shapes:
            for shape in shapes:
                name = returnUniqueGeneratedName(shape,sceneUnique = sceneUnique)
                mc.rename(shape,name)
    
        return renameBuffer

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doRenameHeir(obj,sceneUnique = False):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Names an object's heirarchy below

    ARGUMENTS:
    obj(string) - the object we'd like to startfrom

    RETURNS:
    newNames(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    ### input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
    
    #children = mc.listRelatives(obj,allDescendents=True,type='transform')
    # Create a tmp group to store out objects to so that we can get them back even if heirarchal names change
    tmpGroup = mc.group(em=True)
    attributes.storeInfo(tmpGroup,('name'+str(0)),obj)
    
    newNames = []
    childrenList = []
    children = mc.listRelatives(obj,allDescendents=True,fullPath=True)
    children.reverse()

    cnt = 1
    for c in children:
        attributes.storeInfo(tmpGroup,('name'+str(cnt)),c)
        cnt += 1
        
    toNameAttrs = attributes.returnUserAttributes(tmpGroup)
    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(toNameAttrs),'Naming')

    for attr in toNameAttrs:
        if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
            break
        
        objectToName = (attributes.returnMessageObject(tmpGroup,attr))
        mc.progressBar(mayaMainProgressBar, edit=True, status = ("Naming '%s'"%objectToName), step=1)

        buffer =  doNameObject( objectToName,sceneUnique )
        if buffer:
            newNames.append(buffer)
            
        
    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
            

    mc.delete(tmpGroup)
    return newNames

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doUpdateName(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Names an object's heirarchy below

    ARGUMENTS:
    obj(string) - the object we'd like to startfrom

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    ### input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj

    typeDictionary = dictionary.initializeDictionary(typesDictionaryFile)
    attrName = ('%s%s' % (obj,'.cgmName'))
    # Look for cgmName tag
    if search.returnNameTag(obj) is not False:
        if mc.getAttr(attrName,lock=True) == True:
            mc.setAttr(attrName,lock=False)
        mc.setAttr(attrName,obj, type='string')
        mc.setAttr(attrName,lock=True)
    else:
        attributes.storeInfo(obj,'cgmName',obj,True)
    return doNameObject(obj)