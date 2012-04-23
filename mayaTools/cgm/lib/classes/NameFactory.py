#=================================================================================================================================================
#=================================================================================================================================================
#	autoname - a part of cgmTools
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
from cgm.lib import autoname
from cgm.lib import attributes
from cgm.lib import dictionary
from cgm.lib import settings
from cgm.lib import lists
from cgm.lib import guiFactory

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()

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
        self.objGeneratedNameDict = autoname.returnObjectGeneratedNameDict(obj)
        self.getCGMTags()
        
        self.getNameLinkObject()

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
    def getCGMTags(self):
        self.cgmName = search.findRawTagInfo(self.nameLong,'cgmName')
        self.cgmNameModifier = search.findRawTagInfo(self.nameLong,'cgmNameModifier')
        self.cgmPosition = search.findRawTagInfo(self.nameLong,'cgmPosition')
        self.cgmDirectionModifier = search.findRawTagInfo(self.nameLong,'cgmDirectionModifier')
        self.cgmDirection = search.findRawTagInfo(self.nameLong,'cgmDirection')
        self.cgmIterator = search.findRawTagInfo(self.nameLong,'cgmIterator')
        self.cgmTypeModifier = search.findRawTagInfo(self.nameLong,'cgmTypeModifier')
        self.cgmType  = search.findRawTagInfo(self.nameLong,'cgmType')
                
            
    
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
        self.sceneObjectsNameDictMap = autoname.returnSceneObjectsNameDictMap(transforms = True)  
        
    def reportInfo(self):
        self.getMatchedParents()
        self.getMatchedChildren() 
        self.returnIterator()
           
        print (guiFactory.doPrintReportStart())
        print ("baseName is '%s'" %self.nameBase)
        print ("shortName is '%s'" %self.nameShort)
        print ("longName is '%s'" %self.nameLong)
        print(guiFactory.doPrintReportBreak())
        if self.parentNameCnt:
            print ('%i parents found:' %self.parentNameCnt)
            for o in self.matchedParents:
                print ("'%s'" % o)
        else:
            print ('No name parents')
            
        print(guiFactory.doPrintReportBreak())
        
        if self.childNameCnt:
            print ('%i children found:' %self.childNameCnt)
            for o in self.matchedChildren:
                print ("'%s'" % o)
        else:
            print ('No name children')
            
        print(guiFactory.doPrintReportBreak())

        if self.isObjectNameLinked:
            print ("Name link object is %s" %self.nameLinkObject)
            
        if self.matchObjectList:
            print ("%i match objects: "%len(self.matchObjectList))
            for o in self.matchObjectList:
                print ("'%s'" % o)
        else:
            print ('No match objects found') 
            
        print(guiFactory.doPrintReportBreak())

        print ("Object's Base iterator is %i" %self.childNameCnt)
        print ('First open iterator is %i' %self.firstOpenIterator)
        print ("Final iterator is %i" %self.iterator )
        

        print (guiFactory.doPrintReportEnd())
            
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
        if self.objGeneratedNameDict.get('cgmIterator'):
            self.baseIterator = int(self.objGeneratedNameDict.get('cgmIterator'))
        
        self.baseIteratorChecked = True


    def getMatchedNameObjects(self):
        self.matchObjectList = []
        self.matchDictionaryList = []
        

        
        #Get a list of objects in the scene that match the name object
        if len(self.objGeneratedNameDict.keys()) <= 1 and 'cgmType' in self.objGeneratedNameDict.keys():
            guiFactory.warning("There's only a type tag, ignoring match check")
        else:
            if not self.sceneObjectsNameDictMap:
                self.generateSceneDictMap()            
            for k in self.sceneObjectsNameDictMap.keys():
                if k not in (self.nameLong,self.nameShort): 
                    if self.sceneObjectsNameDictMap.get(k) == self.objGeneratedNameDict:
                        self.matchObjectList.append(k)
                        self.matchDictionaryList.append(self.sceneObjectsNameDictMap.get(k))
        
        
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
                    pGeneratedName = autoname.returnObjectGeneratedNameDict(p)
                    if pGeneratedName == self.objGeneratedNameDict:
                        self.matchedParents.append(buffer[0])

        self.parentNameCnt = len(self.matchedParents)   
        self.parentsChecked = True
        
    def getNameLinkObject(self):   
        self.isObjectNameLinked = False
        if self.objGeneratedNameDict:
            if 'cgmName' in self.objGeneratedNameDict.keys():
                if attributes.queryIfMessage(self.nameLong,'cgmName'):
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
                    cGeneratedName = autoname.returnObjectGeneratedNameDict(c)
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
            topParentNameBuffer = autoname.returnCombinedNameFromDict(objGeneratedNameCandidateDict)

            loopBreak = 0
            foundAvailableRange= False
            while not foundAvailableRange and loopBreak <=50:
                for i in range(cnt,(cnt+rangeTargetNumber)):
                    objGeneratedNameCandidateDict['cgmIterator'] = str(i)
                    bufferName = autoname.returnCombinedNameFromDict(objGeneratedNameCandidateDict)
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

            #print ('Starting number with a range of %i names is : %i' %(rangeTargetNumber,cnt))   

        else:
            ### Scene search for our first open number
            loopBreak = 0
            foundAvailableNumber = False
            looped = False
            while not foundAvailableNumber and loopBreak <= 100:     
                bufferName = autoname.returnCombinedNameFromDict(objGeneratedNameCandidateDict)
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
                                #print ("%s has conflicting dictionary to %s" %(o,self.nameShort))
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
        objGeneratedNameCandidateDict = autoname.returnObjectGeneratedNameDict(self.nameLong)  
        bufferName = autoname.returnCombinedNameFromDict(objGeneratedNameCandidateDict)
        cnt = 0
        
        # Check for match parents, return len + 1
        """
        if self.matchedParents:
            return len(self.matchedParents) + 1
        elif self.matchedChildren:
            if len(self.matchedParents) == 0:
                # if children, and no parents, use...
                return 1
            else:
                # Start looking after 1
                cnt = 1 
        """
             
        if objGeneratedNameCandidateDict.get('cgmIterator'):
            cnt = objGeneratedNameCandidateDict.get('cgmIterator')
        elif cnt == 0:
            #Check if anything else is named 1
            matchCheckDict = objGeneratedNameCandidateDict.copy()
            matchCheckDict['cgmIterator'] = str(1)
            matchBuffer = autoname.returnCombinedNameFromDict(matchCheckDict)
            if mc.objExists(matchBuffer):
                matchFound = True
                cnt = 1
        
        if cnt:
            objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)
        ### Scene search for our first open number
        loopBreak = 0
        foundAvailableNumber = False
        while foundAvailableNumber == False and loopBreak <= 100: 
            bufferName = autoname.returnCombinedNameFromDict(objGeneratedNameCandidateDict)
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

        cnt = self.baseIterator

        ### Before we do anything, we'll see if our top most barent objects has claimed '1'
        ### if it has, we don't need to do much
        #Generate a name candidate
        if self.parentNameCnt:
            objGeneratedNameCandidateDict = autoname.returnObjectGeneratedNameDict(self.nameLong)
            parentTestDict = objGeneratedNameCandidateDict.copy()
            parentTestDict['cgmIterator'] = '1'
            parentTestBuffer = autoname.returnCombinedNameFromDict(parentTestDict)
            if parentTestBuffer == self.matchedParents[0]:
                objGeneratedNameCandidateDictBuffer = objGeneratedNameCandidateDict.copy()
                objGeneratedNameCandidateDictBuffer['cgmIterator'] = str(self.parentNameCnt +1)
                if self.amIMe(autoname.returnCombinedNameFromDict(objGeneratedNameCandidateDictBuffer)):
                    cnt = self.parentNameCnt +1
                    self.selfCheck = True
                    print ("Object's parent has '1' and child is named right")
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
        objGeneratedNameCandidateDict = autoname.returnObjectGeneratedNameDict(self.nameLong)  
        sceneObjectsNameDictMap = self.sceneObjectsNameDictMap.copy()   

        # If there's more than one object with this dict, we have some checking to do
        if cnt:
            objGeneratedNameCandidateDict['cgmIterator'] = str(cnt)

        if self.amIMe(autoname.returnCombinedNameFromDict(objGeneratedNameCandidateDict)) and not self.parentNameCnt:
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
            bufferName = autoname.returnCombinedNameFromDict(objGeneratedNameCandidateDict)
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
        if self.selfCheck or self.amIMe(autoname.returnCombinedNameFromDict(self.nameCandidateDict)):
            self.iterator = cnt
            return cnt


        if cnt < self.parentNameCnt + firstOpenIterator:
            cnt = self.parentNameCnt + firstOpenIterator
        
        self.iterator = cnt
        return cnt