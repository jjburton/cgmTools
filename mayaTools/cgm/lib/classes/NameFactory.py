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

from Red9.core import Red9_General as r9General

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()

cgmNameTags = 'cgmName','cgmNameModifier','cgmPosition','cgmDirection','cgmDirectionModifier','cgmIterator','cgmType','cgmTypeModifier'

#>>>Debug chunk===================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=================================================================

class NameFactory():
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Assertions to verify:
    1) An object knows what it is

    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    def __init__(self,obj):
        ### input check
        assert mc.objExists(obj) is True, "'%s' doesn't exist" %obj

        self.storeNameStrings(obj)  
        
        self.cgmName = ''
        self.cgmNameModifier = ''
        self.cgmPosition = ''
        self.cgmDirectionModifier = ''
        self.cgmDirection = ''
        self.cgmIterator = ''
        self.cgmTypeModifier = ''
        self.cgmType  = ''
        self.objGeneratedNameDict = returnObjectGeneratedNameDict(obj)
        
        self.getNameLinkObject()
        
        self.claimedIterators = []
        self.sceneObjectsNameDictMap = []
        self.matchedChildren = []
        self.matchedParents = []
        self.nameCandidateDict = {}    
        self.parentsChecked = False
        self.childrenChecked = False
        self.matchesChecked = False
        self.baseIteratorChecked = False
        self.firstOpenChecked = False

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    def storeNameStrings(self,obj):
        buffer = mc.ls(obj,long=True)
        self.nameLong = buffer[0]
        buffer = mc.ls(obj,shortNames=True)        
        self.nameShort = buffer[0]
        if '|' in buffer[0]:
            splitBuffer = buffer[0].split('|')
            self.nameBase = splitBuffer[-1]
        else:
            self.nameBase = self.nameShort

    def generateSceneDictMap(self):
        self.sceneObjectsNameDictMap = returnSceneObjectsNameDictMap(transforms = True)  
        
    def reportInfo(self):
        self.getMatchedParents()
        self.getMatchedChildren() 
        self.returnIterator()
           
        log.info (guiFactory.doPrintReportStart())
        log.info ("baseName is '%s'" %self.nameBase)
        log.info ("shortName is '%s'" %self.nameShort)
        log.info ("longName is '%s'" %self.nameLong)
        log.info(guiFactory.doPrintReportBreak())
        if self.parentNameCnt:
            log.info ('%i parents found:' %self.parentNameCnt)
            for o in self.matchedParents:
                log.info ("'%s'" % o)
        else:
            log.info ('No name parents')
            
        log.info(guiFactory.doPrintReportBreak())
        
        if self.childNameCnt:
            log.info ('%i children found:' %self.childNameCnt)
            for o in self.matchedChildren:
                log.info ("'%s'" % o)
        else:
            log.info ('No name children')
            
        log.info(guiFactory.doPrintReportBreak())

        if self.isObjectNameLinked:
            log.info ("Name link object is %s" %self.nameLinkObject)
            
        if self.matchObjectList:
            log.info ("%i match objects: "%len(self.matchObjectList))
            for o in self.matchObjectList:
                log.info ("'%s'" % o)
        else:
            log.info ('No match objects found') 
            
        log.info(guiFactory.doPrintReportBreak())
        
        if self.claimedIterators:
            log.info ("%s are claimed iterators" %self.claimedIterators)            

        log.info ("Object's Base iterator is %i" %self.baseIterator)
        log.info ('First open iterator is %i' %self.firstOpenIterator)
        log.info ("Final iterator is %i" %self.iterator )

        log.info (guiFactory.doPrintReportEnd())
        
            
    def amIMe(self,nameCandidate):
        if nameCandidate == self.nameBase:
            return True
        return False

    def getBaseIterator(self):
        if not self.parentsChecked:
            self.getMatchedParents()
        if not self.childrenChecked:
            self.getMatchedChildren()   

        self.baseIterator = 0
        #If we have an assigned iterator, start with that
        if 'cgmIterator' in self.objGeneratedNameDict.keys():
            self.baseIterator = int(self.objGeneratedNameDict.get('cgmIterator'))
        
        self.baseIteratorChecked = True
        return True


    def getMatchedNameObjects(self):
        self.matchObjectList = []
        self.matchDictionaryList = []
        
        #Get a list of objects in the scene that match the name object
        if len(self.objGeneratedNameDict.keys()) <= 1 and 'cgmType' in self.objGeneratedNameDict.keys():
            log.debug("There's only a type tag, ignoring match check")
        else:
            if not self.sceneObjectsNameDictMap:
                self.generateSceneDictMap()            
            for k in self.sceneObjectsNameDictMap.keys():
                if k not in (self.nameLong,self.nameShort): 
                    if self.sceneObjectsNameDictMap[k] == self.objGeneratedNameDict:
                        self.matchObjectList.append(k)
                        self.matchDictionaryList.append(self.sceneObjectsNameDictMap[k])
                    elif 'cgmIterator' in self.sceneObjectsNameDictMap[k].keys() and returnObjectGeneratedNameDict(k,['cgmIterator']) == self.objGeneratedNameDict:
                        self.claimedIterators.append(int(self.sceneObjectsNameDictMap[k]['cgmIterator']))
                        self.matchObjectList.append(k)
                        self.matchDictionaryList.append(self.sceneObjectsNameDictMap[k])                         
        
        
        self.matchesChecked = True


    def getMatchedParents(self):
        if not self.sceneObjectsNameDictMap:
            self.generateSceneDictMap()
            
        if self.objGeneratedNameDict:
            parents = search.returnAllParents(self.nameLong)
            if parents:
                parents.reverse()
                for p in parents :
                    buffer = mc.ls(p,shortNames=True)
                    pGeneratedName = returnObjectGeneratedNameDict(p)
                    if pGeneratedName == self.objGeneratedNameDict:
                        self.matchedParents.append(buffer[0])

        self.parentNameCnt = len(self.matchedParents)   
        self.parentsChecked = True
        
    def getNameLinkObject(self):   
        self.isObjectNameLinked = False
        if self.objGeneratedNameDict:
            if 'cgmName' in self.objGeneratedNameDict.keys():
                if mc.objExists('%s.cgmName'%self.nameLong) and mc.attributeQuery ('cgmName',node=self.nameLong,msg=True):
                    buffer = attributes.returnMessageObject(self.nameLong,'cgmName')
                    self.nameLinkObject = buffer
                    self.isObjectNameLinked = True
    

    def getMatchedChildren(self):      
        if not self.sceneObjectsNameDictMap:
            self.generateSceneDictMap()
            
        #>>> Count our matched name children range
        if self.objGeneratedNameDict:
            children = mc.listRelatives (self.nameLong, allDescendents=True,type='transform',fullPath=True)
            if children:
                children.reverse()
                for c in children :
                    buffer = mc.ls(c,shortNames=True)
                    cGeneratedName = returnObjectGeneratedNameDict(c)
                    if cGeneratedName == self.objGeneratedNameDict:
                        self.matchedChildren.append(buffer[0])

        ### Get our children number to know how many open name slots we need
        self.childNameCnt = len(self.matchedChildren)            
        self.childrenChecked = True


    def getFirstRangeIterator(self):
        #Find an available range of numbers available if we need to
        rangeTargetNumber = (self.parentNameCnt+self.childNameCnt+1)
        if rangeTargetNumber > 1:
            topParentDict = objGeneratedNameCandidateDict.copy()
            objGeneratedNameCandidateDict['cgmIterator'] = '1'
            topParentNameBuffer = returnCombinedNameFromDict(objGeneratedNameCandidateDict)

            loopBreak = 0
            foundAvailableRange= False
            while not foundAvailableRange and loopBreak <=50:
                for i in range(cnt,(cnt+rangeTargetNumber)):
                    objGeneratedNameCandidateDict['cgmIterator'] = str(i)
                    bufferName = returnCombinedNameFromDict(objGeneratedNameCandidateDict)
                    if mc.objExists(bufferName):
                        matchNameList = mc.ls(bufferName,shortNames=True)
                        for item in matchNameList:
                            if item not in self.matchedChildren:
                                if item not in self.matchedParents: 
                                    #See if our object is the matched item
                                    if not self.amIMe(item):
                                        #If the generated name exists
                                        if bufferName == item:
                                            cnt +=1

                                        #If the generated name exists anywhere else
                                        elif '|' in item:
                                            buffer = item.split('|')
                                            if bufferName == buffer[-1]:
                                                cnt +=1                              

                    else:
                        #next look through the named dictionaries
                        for o in sceneObjectsNameDictMap.keys():
                            if o not in self.matchedChildren:
                                if o not in self.matchedParents: 
                                    if objGeneratedNameCandidateDict == sceneObjectsNameDictMap.get(o):
                                        if not self.amIMe(o):
                                            cnt+=1
                    loopBreak +=1
                    if cnt == (cnt+self.parentNameCnt+self.childNameCnt+1):
                        foundAvailableRange = True

            #log.info ('Starting number with a range of %i names is : %i' %(rangeTargetNumber,cnt))   

        else:
            ### Scene search for our first open number
            loopBreak = 0
            foundAvailableNumber = False
            looped = False
            while not foundAvailableNumber and loopBreak <= 100:     
                bufferName = returnCombinedNameFromDict(objGeneratedNameCandidateDict)
                if mc.objExists(bufferName):
                    matchNameList = mc.ls(bufferName,shortNames=True)
                    for item in matchNameList:
                        if item not in self.matchedChildren:    
                            #See if our object is the matched item
                            if not self.amIMe(item):
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
                                foundAvailableNumber = True
                else:
                    #next look through the named dictionaries
                    for o in sceneObjectsNameDictMap.keys():
                        if objGeneratedNameCandidateDict == sceneObjectsNameDictMap.get(o):
                            if not self.amIMe(o):
                                #log.info ("%s has conflicting dictionary to %s" %(o,self.nameShort))
                                cnt+=1
                            else:
                                foundAvailableNumber = True 
                loopBreak +=1

        self.nameCandidateDict = objGeneratedNameCandidateDict.copy()
        if cnt >= 1:
            self.nameCandidateDict['cgmIterator'] = str(cnt)

        return cnt        

    def getFastIterator(self):
        #>>> Variation of the full on iteration check, this is a fast version that doesn't bother full scene dictioinary searches
        """
        if not self.parentsChecked:
            self.getMatchedParents()
        if not self.childrenChecked:
            self.getMatchedChildren()  
        """
        objGeneratedNameCandidateDict = returnObjectGeneratedNameDict(self.nameLong)  
        bufferName = returnCombinedNameFromDict(objGeneratedNameCandidateDict)
        cnt = 0
             
        if objGeneratedNameCandidateDict.get('cgmIterator'):
            cnt = int(objGeneratedNameCandidateDict.get('cgmIterator'))
        elif cnt == 0:
            #Check if anything else is named 0
            matchCheckDict = objGeneratedNameCandidateDict.copy()
            matchCheckDict['cgmIterator'] = str(1)
            matchBuffer = returnCombinedNameFromDict(matchCheckDict)
            if mc.objExists(matchBuffer):
                matchFound = True
                cnt = 1
        
        if cnt:
            objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)
        ### Scene search for our first open number
        loopBreak = 0
        foundAvailableNumber = False
        while foundAvailableNumber == False and loopBreak <= 100: 
            bufferName = returnCombinedNameFromDict(objGeneratedNameCandidateDict)
            if mc.objExists(bufferName):
                matchNameList = mc.ls(bufferName,shortNames=True)
                for item in matchNameList:
                    if not self.amIMe(item):
                        #If the generated name exists
                        if bufferName == item:
                            cnt +=1
                            loopBreak +=1
                            objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)
                            

                        #If the generated name exists anywhere else
                        elif '|' in item:
                            buffer = item.split('|')
                            if bufferName == buffer[-1]:
                                cnt +=1
                                loopBreak +=1                               
                                objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)
                                

                    else:
                        foundAvailableNumber = True
            else:
                foundAvailableNumber = True
            loopBreak +=1

        return cnt
                                


    def getFirstOpenIterator(self):
        if not self.baseIteratorChecked:
            self.getBaseIterator()
        if not self.matchesChecked:
            self.getMatchedNameObjects() 

        self.selfCheck = False

        ### If our object is named linked, we don't really have to do much
        if self.isObjectNameLinked:
            self.firstOpenChecked = True
            self.firstOpenIterator = 0
            return 0
        
        # Check for a base start of 0 and matched object list
        if self.baseIterator == 0 and self.matchObjectList:
            cnt = 1
        else:
            cnt = self.baseIterator

        ### Before we do anything, we'll see if our top most barent objects has claimed '1'
        ### if it has, we don't need to do much
        #Generate a name candidate
        if self.parentNameCnt:
            objGeneratedNameCandidateDict = returnObjectGeneratedNameDict(self.nameLong)
            parentTestDict = objGeneratedNameCandidateDict.copy()
            parentTestDict['cgmIterator'] = '1'
            parentTestBuffer = returnCombinedNameFromDict(parentTestDict)
            if parentTestBuffer == self.matchedParents[0]:
                objGeneratedNameCandidateDictBuffer = objGeneratedNameCandidateDict.copy()
                objGeneratedNameCandidateDictBuffer['cgmIterator'] = str(self.parentNameCnt +1)
                if self.amIMe(returnCombinedNameFromDict(objGeneratedNameCandidateDictBuffer)):
                    cnt = self.parentNameCnt +1
                    self.selfCheck = True
                    log.info ("Object's parent has '1' and child is named right")
                    self.firstOpenIterator = cnt
                    self.firstOpenChecked = True
                    return cnt

        #Remove our objected from the scene name dictionary map       
        # If any other objects in the scene, it cannot have a 0 cnt    
        if not self.sceneObjectsNameDictMap:
            self.generateSceneDictMap()
        
        if self.objGeneratedNameDict in self.matchDictionaryList and cnt == 0:
            cnt +=1

        #Generate a name candidate and a copy of the scene map
        objGeneratedNameCandidateDict = returnObjectGeneratedNameDict(self.nameLong)  
        sceneObjectsNameDictMap = self.sceneObjectsNameDictMap.copy()   

        # If there's more than one object with this dict, we have some checking to do
        if cnt:
            objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)

        if self.amIMe(returnCombinedNameFromDict(objGeneratedNameCandidateDict)) and not self.parentNameCnt:
            self.selfCheck = True
            self.firstOpenIterator = cnt
            self.firstOpenChecked = True
            return cnt

        ### First try by processing the top name parent

        ### Scene search for our first open number
        loopBreak = 0
        foundAvailableNumber = False
        looped = False
        while not foundAvailableNumber and loopBreak <= 100: 
            bufferName = returnCombinedNameFromDict(objGeneratedNameCandidateDict)
            if mc.objExists(bufferName):
                if cnt in self.claimedIterators:
                    cnt +=1 
                    break
                matchNameList = mc.ls(bufferName,shortNames=True)
                for item in matchNameList:
                    if item not in self.matchedChildren:    
                        #See if our object is the matched item
                        if not self.amIMe(item):
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
                            foundAvailableNumber = True
            else:
                #next look through the named dictionaries
                for o in sceneObjectsNameDictMap.keys():
                    if objGeneratedNameCandidateDict == sceneObjectsNameDictMap.get(o):
                        if not self.amIMe(o):
                            cnt+=1
                            objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)
                        else:
                            foundAvailableNumber = True 
            loopBreak +=1

        self.nameCandidateDict = objGeneratedNameCandidateDict.copy()
        if cnt >= 1:
            self.nameCandidateDict['cgmIterator'] = str(cnt)
        
        self.firstOpenIterator = cnt
        self.firstOpenChecked = True
        return cnt    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Meta Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    def returnIterator(self):
        cnt = self.getFirstOpenIterator()
        firstOpenIterator = cnt

        ### If our object is named linked, we don't really have to do much
        if self.isObjectNameLinked:
            self.iterator = 0
            return 0

        ###If we got this far and we're ourselves, let's bounce....
        if self.selfCheck or self.amIMe(returnCombinedNameFromDict(self.nameCandidateDict)):
            self.iterator = cnt
            return cnt


        if cnt < self.parentNameCnt + firstOpenIterator:
            cnt = self.parentNameCnt + firstOpenIterator
        
        self.iterator = cnt
        return cnt
    
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Unique Name s
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
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
    
#@r9General.Timer   
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

#@r9General.Timer   
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

    
#@r9General.Timer   
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
                log.info ("%s has a duplicate in the same heirarchy!" %obj)
        #log.info ("Count after checking name parent is %i" %cnt)
        return cnt
    #otherwise, we process it by itself
    else:
        cnt = objToQuery.returnIterator()
        return cnt
        
        

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
def returnUniqueGeneratedName(obj,sceneUnique = False,fastIterate = True, ignore='none',**kws):
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
    if type(ignore) is not list:ignore = [ignore]
    log.debug("sceneUnique: %s"%sceneUnique)
    log.debug("fastIterate: %s"%fastIterate)
    log.debug("ignore: %s"%ignore)
    
    #>>> Dictionary driven order first build
    def doBuildName():
        nameBuilder=[]
        for item in order:
            buffer = updatedNamesDict.get(item)
            # Check for short name
            buffer = search.returnTagInfoShortName(buffer,item)
            if buffer and buffer != 'ignore':
                nameBuilder.append(buffer)

        return divider.join(nameBuilder)
    
    rawNamesDict = returnObjectGeneratedNameDict(obj,ignore)
    divider = returnCGMDivider()
    updatedNamesDict = returnObjectGeneratedNameDict(obj,ignore)
    order = returnCGMOrder()
    
    if 'cgmName' not in updatedNamesDict.keys() and search.returnObjectType(obj) !='group':
        buffer = mc.ls(obj,shortNames = True)
        attributes.storeInfo(obj,'cgmName',buffer[0],True)
        updatedNamesDict = returnObjectGeneratedNameDict(obj,ignore)

    coreName = doBuildName()
    
    """ add the iterator to the name dictionary if our object exists"""
    nameFactory = NameFactory(obj)
    
    if sceneUnique:
        if fastIterate:
            iterator = returnFastIterateNumber(obj)            
        else:
            iterator = returnIterateNumber(obj)
        if iterator > 0:
            updatedNamesDict['cgmIterator'] = str(iterator)
            coreName = doBuildName()
            
    log.debug(returnCombinedNameFromDict(updatedNamesDict))
    return returnCombinedNameFromDict(updatedNamesDict)


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
            #if mc.objExists(tagInfo):
                #tagInfo = mc.ls(tagInfo,sn=True)[0]
                #log.info("shortening")
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
    if isType == 'group' and typeTag == False:
        """ if it's a transform group """
        groupNamesDict = {}
        if not nameObj:
            groupNamesDict['cgmName'] = childrenObjects[0]
        else:
            groupNamesDict['cgmName'] = nameObj
        groupNamesDict['cgmType'] = typesDictionary.get('transform')
        if namesDict.get('cgmPosition') != None:
            groupNamesDict['cgmPosition'] = namesDict.get('cgmPosition')        
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
            if namesDict.get('cgmPosition') != None:
                childNamesDict['cgmPosition'] = namesDict.get('cgmPosition')            
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
#@r9General.Timer   
def doNameObject(obj,sceneUnique = False,fastIterate = True):
    """ 
    Names an object

    ARGUMENTS:
    obj(string) - the object we'd like to name
    sceneUnique(bool)- whether to do a full scene check or just the faster check

    RETURNS:
    newName(string) on success
    
    """
    ### input check
    if not mc.objExists(obj):
        log.warning("'%s' doesn't exist" %obj)
        return False
    assert mc.referenceQuery(obj, isNodeReferenced=True) is not True, "'%s' is referenced, can't name!" %obj
    
    name = returnUniqueGeneratedName(obj,sceneUnique, fastIterate)
    nameFactory = NameFactory(obj)
    
    if nameFactory.amIMe(name):
        log.debug("'%s' is already named correctly."%nameFactory.nameBase)
        return name
    else:
        objLong = mc.ls(obj,long=True)
        renameBuffer = mc.rename(objLong,name)

        shapes = mc.listRelatives(renameBuffer,shapes=True,fullPath=True)
        if shapes:
            for shape in shapes:
                if not mc.referenceQuery(shape, isNodeReferenced=True):
                    name = returnUniqueGeneratedName(shape,sceneUnique, fastIterate)
                    mc.rename(shape,name)
        #log.info("renameBuffer: '%s'"%renameBuffer)
        #log.info("renameBuffer long: '%s'"%mc.ls(renameBuffer,long=True))        
        return renameBuffer
        #return mc.ls(renameBuffer,long=True)[0]
        

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def doRenameHeir(obj,sceneUnique = False,fastIterate = True):
    """ 
    Names an object's heirarchy below

    ARGUMENTS:
    obj(string) - the object we'd like to startfrom
    sceneUnique(bool)- whether to do a full scene check or just the faster check

    RETURNS:
    newNames(list)
    
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

        buffer =  doNameObject( objectToName,sceneUnique,fastIterate )
        if buffer:
            newNames.append(buffer)
            
        
    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
            

    mc.delete(tmpGroup)
    return newNames

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#@r9General.Timer   
def doUpdateName(obj,*a, **kw):
    """ 
    Updates the name of an object

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
    return doNameObject(obj,*a, **kw)