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
def returnIterateNumber(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Check through a scene to figure out what iterative number an obj
    
    REQUIRES:
    obj(string) LONG NAME
    
    RETURNS:
    order(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    buffer = mc.ls(obj,long=True)
    sceneTransformObjects =  mc.ls(transforms=True, long = True)
    obj = buffer[0]
    objGeneratedNameDict = returnObjectGeneratedNameDict(obj)
    cnt = 0
    
    print ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print ('On %s' %obj)
    
    ### Get our base iterator first
    #>Start by looking through for any object with that name
    oGeneratedName = returnCombinedNameFromDict(objGeneratedNameDict)
    print ('GeneratedName is  %s' %oGeneratedName)
    matchNameList = mc.ls(oGeneratedName,long=True)
    print ('MatchList is  %s' %matchNameList)
    for item in matchNameList:
        #See if our object is the matched item
        if not obj == item:
            #If the generated name exists
            if oGeneratedName == item:
                print ('Matched %s' %item)
                cnt +=1
            #If the generated name exists anywhere else
            elif '|' in item:
                buffer = item.split('|')
                if oGeneratedName == buffer[-1]:
                    print ('Matched %s' %item)
                    cnt +=1
            
    print ('Count with name is %i' %cnt)
    
    ### Finding a range of children objects we need available
    childNameCnt = 0
    children = mc.listRelatives (obj, allDescendents=True,type='transform',fullPath=True)
    #>>> Count our matched name children range
    if children:
        children.reverse()
        for c in children :
            cGeneratedName = returnObjectGeneratedNameDict(c)
            if cGeneratedName == objGeneratedNameDict:
                childNameCnt +=1
                
    print ('Child match number is %i!' %childNameCnt)
    
    #>>> If our count is 0 and we have any children, we're gonna start with 1
    if childNameCnt and cnt == 0:
        cnt +=1
            
    print ('Count after heirarchy count is %i' %cnt)  
 
    ### Now need to check for available ranges
    
    """
    
    #>>> First get a list of all objects with transforms in the scene
    sceneTransformObjects =  mc.ls(transforms=True, long = True)
    


    #>>> Iterate through the parent tree to iterate
    parents = search.returnAllParents(obj)
    if parents:
        matchParentCnt = 0
        print ('Parents are %s' %parents)
        parentGeneratedNames = []
        #>>> first iterate through the heirarchy
        print objGeneratedNameDict
        print '>>>'
        for p in parents:
            pGeneratedName = returnObjectGeneratedNameDict(p)
            print pGeneratedName
            if pGeneratedName == objGeneratedNameDict:
                print ('Found parent match at %s!' %p)
                matchParentCnt+=1
                if p in sceneTransformObjects:
                    sceneTransformObjects.remove(p)
        if matchParentCnt:
            cnt += matchParentCnt
        print '>>>'
        
    #>>> Check children for the name dict
    children = mc.listRelatives (obj, allDescendents=True,type='transform',fullPath=True)
    if children:
        print ('Children are %s' %children)
        for c in children:
            cGeneratedName = returnObjectGeneratedNameDict(c)
            if cGeneratedName == objGeneratedNameDict:
                cnt+=1
                print ('Found child match at %s!' %c)
                if c in sceneTransformObjects:
                    sceneTransformObjects.remove(c)
                break

    print ('Count after heirarchy count is %i' %cnt)  
    
    #>>> Lastly look through the remaining objects in the scene
    sceneWideMatches = []
    for o in sceneTransformObjects:
        if oGeneratedName in o and o != obj:
            sceneWideMatches.append(o)
            cnt +=1
    print ('Scene Matches are after heirarchy count is %s' %sceneWideMatches)  
    print ('Count after scene count is %i' %cnt)  
    """
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
        
    #add to our iterator if it exists
    """ first we're gonna see how many objects with this name exist """
    objectsWithThisListedName = mc.ls('%s%s' % ('*',objNameCandidate))
    realDuplicates = []
    for name in objectsWithThisListedName:
        if '|' in list(name) or objNameCandidate == name:
            realDuplicates.append(name)

    cnt = len(realDuplicates)-1
    if mc.objExists(objNameCandidate) == False:
        return objNameCandidate
        
    elif len(realDuplicates) == 1:
        """ if the object is the candidate, name is good """
        if obj == objNameCandidate:
            return objNameCandidate
        else:
            """ if the objects exists and it isn't the object, start iterating"""
            cnt = 2
            while mc.objExists(objNameCandidate) == True and obj == objNameCandidate:
                cnt +=1
                objNameCandidate = ('%s%i' % (objNameCandidate,cnt))
            return objNameCandidate
    elif len(realDuplicates)>1:
        """if there's more than one of them in the scene, start iterating"""
        cnt = 2
        while mc.objExists(objNameCandidate) == True:
                cnt +=1
                objNameCandidate = ('%s%i' % (objNameCandidate,cnt))
        return objNameCandidate
    else:
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
def doNameObject(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Names an object
    
    REQUIRES:
    obj(string) - the object we'd like to name
    
    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    name = returnUniqueGeneratedName(obj)
    renameBuffer = mc.rename(obj,name)
    shapes = mc.listRelatives(renameBuffer,shapes=True,fullPath=True)
    if shapes != None:
        for shape in shapes:
            name = returnUniqueGeneratedName(shape)
            mc.rename(shape,name)
    
    return renameBuffer
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
    


