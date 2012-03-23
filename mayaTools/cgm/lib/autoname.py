#=================================================================================================================================================
#=================================================================================================================================================
#	autoname - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for finding stuff
# 
# REQUIRES:
# 	Maya
# 	search
# 	names
# 	attribute
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.joshburton.com
# 	Copyright 2011 Josh Burton - All Rights Reserved.
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
    sceneTransformObjects =  mc.ls(long = True,**a)
    
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

def returnIterateNumber(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Check through a scene to figure out what iterative number an obj

    REQUIRES:
    obj(string)

    RETURNS:
    order(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>> input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj

    #>>> Start function
    
    ### Get long name of obj and generate it's name dict
    buffer = mc.ls(obj,long=True)
    obj = buffer[0]
    objGeneratedNameDict = returnObjectGeneratedNameDict(obj)
    cnt = 0
    #If we have an assigned iterator, start with that
    if objGeneratedNameDict.get('cgmIterator'):
        cnt = int(objGeneratedNameDict.get('cgmIterator'))

    print ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print ('On %s' %obj)
    
    ### Simple check to see if we need to go further
    buffer = returnCombinedNameFromDict(objGeneratedNameDict)
    print buffer
    if mc.objExists(buffer):
        print ('No conflicts, good to go' %obj)
        return cnt
    else:
        print 'no'

    ### Iterate through the parent tree to iterate
    matchedParents = []
    if mc.listRelatives (obj, parent=True,type='transform'):
        matchedParents = returnMatchedNameParents(obj)
        parentNameCnt = len(matchedParents)
        cnt += parentNameCnt
        print ('Parent match number is %i!' %parentNameCnt)
    else:
        print 'no parents'
        parentNameCnt = 0
    
    ### Get our children number to know how many open name slots we need
    matchedChildren = returnMatchedNameChildren(obj)
    childNameCnt = len(matchedChildren)
    #If our count is 0 and we have any children, we're gonna start with 1
    if childNameCnt and cnt == 0:
        cnt +=1
    print ('Child match number is %i!' %childNameCnt)
    if not matchedChildren:
        print 'no kiddos'
        childNameCnt = 0
        
    print ('Count after heirarchy count is %i' %cnt)  

    ### Gonna check through the scene for other information
    sceneObjectsNameDictMap = returnSceneObjectsNameDictMap(transforms = True)
    # Check our potential range of numbers needed for availablity by named object and claimed iterators
    
    ### Check trhough scene objects for any thing else with it's name dict, if so, cnt cannot be 0
    matchList = []
    sceneObjectsNameDictMap.pop(obj)
    for k in sceneObjectsNameDictMap.keys():
        matchList.append(sceneObjectsNameDictMap.get(k))
    if objGeneratedNameDict in matchList and cnt == 0:
        print ("Another object has this nameDict, cnt increased")
        cnt +=1
    
    #Inital scene look through
    objGeneratedNameCandidateDict = returnObjectGeneratedNameDict(obj)
    if cnt >= 1:
        objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)
    
    ### Scene search for our first open number
    print ("Initial candidate is %s" %objGeneratedNameCandidateDict)
    loopBreak = 0
    foundStartNumber = False
    looped = False
    while not foundStartNumber and loopBreak <= 100:     
        bufferName = returnCombinedNameFromDict(objGeneratedNameCandidateDict)
        if mc.objExists(bufferName):
            matchNameList = mc.ls(bufferName,long=True)
            for item in matchNameList:
                print ('checking %s' %item)
                if item not in matchedChildren or matchedParents:    
                    #See if our object is the matched item
                    if not obj == item:
                        #If the generated name exists
                        if bufferName == item:
                            cnt +=1
                            looped = True
                            objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)

                        #If the generated name exists anywhere else
                        elif '|' in item:
                            buffer = item.split('|')
                            if bufferName == buffer[-1]:
                                cnt +=1
                                looped = True
                                objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)

                    else:
                        foundStartNumber = True
        else:
            print ("%s doesn't exist,checking name dictionaries" %bufferName)
            #next look through the named dictionaries
            for o in sceneObjectsNameDictMap.keys():
                if objGeneratedNameCandidateDict == sceneObjectsNameDictMap.get(o):
                    print ("%s conflicts" %o)
                    cnt+=1
                else:
                    foundStartNumber = True 
        loopBreak +=1
        
    print ('Starting available number: %i' %cnt)  
    
    if cnt >= 1:
        objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)

    ### Heirarchy

    loopBreak = 0       
    candidateSuccess = False   
    print ('Counting through')  
    while not candidateSuccess and loopBreak <= 100:
        bufferName = returnCombinedNameFromDict(objGeneratedNameCandidateDict)
        # see if the name exists in scene
        if mc.objExists(bufferName):
            matchNameList = mc.ls(bufferName,long=True)
            for item in matchNameList:
                print ('checking %s' %item)
                if item in matchedChildren or matchedParents:
                    print ('%s matched children or parents' %item)
                    candidateSuccess = True
                else:
                    #See if our object is the matched item
                    if not obj == item:
                        #If the generated name exists
                        if bufferName == item:
                            cnt +=1
                        #If the generated name exists anywhere else
                        elif '|' in item:
                            buffer = item.split('|')
                            if bufferName == buffer[-1]:
                                cnt +=1
                    else:
                        candidateSuccess = True

        else:
            print ("%s doesn't exist,checking name dictionaries" %bufferName)
            #next look through the named dictionaries
            for o in sceneObjectsNameDictMap.keys():
                if objGeneratedNameCandidateDict == sceneObjectsNameDictMap.get(o):
                    print ("%s has a name conflicts" %o)
                    cnt+=1
                else:
                    candidateSuccess = True 
        print cnt                
        objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)
        print ("candidate is now %s" %objGeneratedNameCandidateDict)     
        loopBreak+=1
    
    if cnt >=0 and parentNameCnt:
        cnt += parentNameCnt
        
    print ('Count after heirarchy flow count is %i' %cnt)  

            
    """
    for i in range(cnt,(childNameCnt+cnt+1)):
        print i
        objGeneratedNameCandidateDict['cgmIterator'] = str(i)
        print ("candidate is now %s" %objGeneratedNameCandidateDict)
        bufferName = returnCombinedNameFromDict(objGeneratedNameCandidateDict)
        # see if the name exists in cene
        if not mc.objExists(bufferName):
            print ("%s doesn't exist" %bufferName)
            #next look through the named dictionaries
            for o in sceneObjectsNameDictMap.keys():
                if objGeneratedNameCandidateDict == sceneObjectsNameDictMap.get(o):
                    print ("%s conflicts" %o)
                    break
        else:
            print ("%s exists" %bufferName)
        loopBreak+=1
    cnt+=i
    """
            
    print ('Count after range count is %i' %cnt)  

    return cnt

def returnCGMOrder():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the order for names in a list format

    REQUIRES:
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

    REQUIRES:
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

    REQUIRES:
    Nothin

    RETURNS:
    divider(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    dict = dictionary.initializeDictionary(settingsDictionaryFile)
    return (dict.get(setting))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnUniqueGeneratedName(obj,ignore='none'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated name with iteration for heirarchy objects with the same tag info

    REQUIRES:
    obj(string) - object
    ignore(string) - default is 'none', only culls out cgmtags that are 
                     generated via returnCGMOrder() function

    RETURNS:
    name(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    rawNamesDict = returnObjectGeneratedNameDict(obj,ignore)
    iterator = returnIterateNumber(obj)
    divider = returnCGMDivider()
    order = returnCGMOrder()

    """ add the iterator to the name dictionary """
    if iterator > 0:
        rawNamesDict['cgmIterator'] = str(iterator)

    #>>> First we generate a name with the iterator in it

    #>>> Dictionary driven order first build
    def doBuildName():
        nameBuilder=[]
        for item in order:
            buffer = rawNamesDict.get(item)
            # Check for short name
            buffer = search.returnTagInfoShortName(buffer,item)
            if buffer > 0 and buffer != 'ignore':
                nameBuilder.append(buffer)

        return divider.join(nameBuilder)

    coreName = doBuildName()
    objNameCandidate = coreName

    # Accounting for ':' in a name
    if ':' in coreName:
        buffer = list(coreName)
        cnt = coreName.index(':')
        buffer.remove(':')
        buffer.insert(cnt,'to')
        objNameCandidate = ''.join(buffer)
    
            
    return objNameCandidate







#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnRawGeneratedName(obj,ignore='none'):
    """  
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated name

    REQUIRES:
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

    REQUIRES:
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
            nameBuilder.append(buffer)
    return divider.join(nameBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectGeneratedNameDict(obj,ignore='none'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a generated dictionary of name info

    REQUIRES:
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
    #>>> Get our cgmVariables
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
    #nameObj = namesDict.get('cgmName')
    typeTag = search.returnTagInfo(obj,'cgmType')
    isType = search.returnObjectType(obj)
    childrenObjects = search.returnChildrenObjects(obj)
    """first see if it's a group """
    if childrenObjects > 0 and isType == 'transform' and typeTag == False:
        """ if it's a transform group """
        groupNamesDict = {}
        groupNamesDict['cgmName'] = childrenObjects[0]
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
def doNameObject(obj,forceOverride = True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Names an object, when forceOverride is False, will select conflicting objects

    REQUIRES:
    obj(string) - the object we'd like to name
    forceOverride(bool)- whether to rename conflicts or not

    RETURNS:
    newName(string) on success
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    ### input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
    
    name = returnUniqueGeneratedName(obj)
    objLong = mc.ls(obj,long=True)
    conflictList = mc.ls(name,long = True)
    matchedList = []
    for o in conflictList:
        if o != objLong[0]:
            matchedList.append(o)
            if forceOverride:
                mc.rename(o,'Name_Conflict')
    
    if forceOverride:        
        renameBuffer = mc.rename(obj,name)
    
        shapes = mc.listRelatives(renameBuffer,shapes=True,fullPath=True)
        if shapes != None:
            for shape in shapes:
                name = returnUniqueGeneratedName(shape)
                mc.rename(shape,name)
    
        return renameBuffer
    
    else:
        mc.select(matchedList)
        guiFactory.warning("The following have conficting names : %s" %matchedList)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doRenameHeir(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Names an object's heirarchy below

    REQUIRES:
    obj(string) - the object we'd like to startfrom

    RETURNS:
    newNames(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    ### input check
    assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj
    
    #children = mc.listRelatives(obj,allDescendents=True,type='transform')
    newNames = []
    newNames.append(doNameObject(obj))
    childrenList = []
    children = mc.listRelatives(newNames[0],allDescendents=True,fullPath=True)

    for c in children:
        childrenList.append(doNameObject(c))
    newNames.append(childrenList)
    return newNames

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doUpdateName(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Names an object's heirarchy below

    REQUIRES:
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


