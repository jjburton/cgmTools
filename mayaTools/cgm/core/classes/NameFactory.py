"""
------------------------------------------
ControlFactory: cgm.core
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
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General
from Red9.core import Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (lists,
                     search,
                     dictionary,
                     settings,
                     attributes)

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()

class go(object):
    """ 
    New Name Factory. Finds a 
    """
    def __init__(self,node,doName = False):
        """ 
        """
        if issubclass(type(node),r9Meta.MetaClass):
            self.i_node = node
        elif mc.objExists(node):
            self.i_node = cgmMeta.cgmNode(node)
        else:
            raise StandardError,"NameFactory.go >> node doesn't exist: '%s'"%node
        
        #Initial Data        
        self.d_nameDict = returnObjectGeneratedNameDict(self.i_node.mNode)
        
    def isNameLinked(self):   
        if self.i_node.hasAttr('cgmName') and self.i_node.getMessage('cgmName'):
            return True
        return False
    
    #@r9General.Timer
    def getMatchedParents(self):  
        parents = search.returnAllParents(self.i_node.mNode)
        self.i_nameParents = []
        if parents:
            parents.reverse()
            d_nameDict = self.i_node.getNameDict()
            for p in parents :
                i_p = cgmMeta.cgmNode(p)
                if i_p.getNameDict() == d_nameDict:
                    self.i_nameParents.append(i_p)
                    log.debug("Name parent found: '%s'"%i_p.mNode)
        return self.i_nameParents

    def getMatchedChildren(self):      
        #>>> Count our matched name children range
        children = mc.listRelatives (self.i_node.mNode, allDescendents=True,type='transform',fullPath=True)
        self.i_nameChildren = []        
        if children:
            children.reverse()
            d_nameDict = self.i_node.getNameDict()            
            for c in children :
                i_c = cgmMeta.cgmNode(c)
                if i_c.getNameDict() == d_nameDict:
                    self.i_nameChildren.append(i_c)
                    log.debug("Name child found: '%s'"%i_c.mNode)
        return self.i_nameChildren
    
    def getMatchedSiblings(self):
        self.i_nameSiblings = []
        d_nameDict = self.i_node.getNameDict()        
        for s in self.i_node.getSiblings():                    
            i_c = cgmMeta.cgmNode(s)
            if i_c.getNameDict() == d_nameDict and i_c.mNode != self.i_node.mNode:
                self.i_nameSiblings.append(i_c)
                log.debug("Name sibling found: '%s'"%i_c.mNode)                

        return self.i_nameSiblings        
    
    def getBaseIterator(self):
        int_baseIterator = 0
        #If we have an assigned iterator, start with that
        if 'cgmIterator' in self.i_node.getNameDict().keys():
            int_baseIterator = int(self.objGeneratedNameDict.get('cgmIterator'))
        return int_baseIterator
    
    #@r9General.Timer    
    def getIterator(self,node = None):
        """
        """
	if node is None:
	    i_node = self.i_node
	elif issubclass(type(node),r9Meta.MetaClass):
	    i_node = node
	elif mc.objExists(node):
	    i_node = cgmMeta.cgmNode(node)
	else:
	    raise StandardError,"NameFactory.getIterator >> node doesn't exist: '%s'"%node
	    
        self.int_iterator = 0
        
        def getNewNameCandidate(self):
            self.int_iterator+=1#add one
            self.d_nameCandidate['cgmIterator'] = str(self.int_iterator)
            self.bufferName = returnCombinedNameFromDict(self.d_nameCandidate)
            return self.bufferName
            
        if 'cgmIterator' in i_node.getNameDict().keys():
            return int(self.objGeneratedNameDict.get('cgmIterator'))
        
        #Gather info
        i_nameParents = self.getMatchedParents()
        i_nameChildren = self.getMatchedChildren()
        i_nameSiblings = self.getMatchedSiblings()
        
        if i_nameParents:#If we have parents 
            self.int_iterator =  len(i_nameParents) + 1
        elif i_nameChildren or i_nameSiblings:#If we have children, we can't be 0
            self.int_iterator = 1
            
        #Now that we have a start, we're gonna see if that name is taken by a sibling or not
        self.d_nameCandidate = i_node.getNameDict()
        if self.int_iterator:
            self.d_nameCandidate['cgmIterator'] = str(self.int_iterator)
        self.bufferName = returnCombinedNameFromDict(self.d_nameCandidate)
        
        log.info("bufferName: '%s'"%self.bufferName)
        if not mc.objExists(self.bufferName):
            log.info('Good name candidate')
            return self.int_iterator
        else:#if there is only one
            for obj in mc.ls(self.bufferName):
                i_bufferName = cgmMeta.cgmNode(obj)
                if i_node.mNode == i_bufferName.mNode:
                    log.debug("I'm me! : %s"%self.int_iterator)
                    return self.int_iterator
                
        if i_nameSiblings:#check siblings
            l_siblingShortNames = [i_s.getShortName() for i_s in i_nameSiblings]
            log.info("Checking sibblings: %s"%l_siblingShortNames)
            while self.bufferName in l_siblingShortNames and self.int_iterator <50:
                getNewNameCandidate(self)
            """
            for i_s in i_nameSiblings:
                if i_node.getShortName() == self.bufferName:
                    log.info("I'm me! : %s"%self.int_iterator)
                    return self.int_iterator                    
                elif i_s.getShortName() == self.bufferName:
                    log.info("Sibling has this")
                    getNewNameCandidate(self)
                else:
                    getNewNameCandidate(self)                    
            """
        log.info("getIterator: %s"%self.int_iterator)
        return self.int_iterator
    
    #@r9General.Timer
    def returnUniqueGeneratedName(self, ignore='none',**kws):
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
        if type(ignore) is not list:ignore = [ignore]
        log.debug("ignore: %s"%ignore)
        
        #>>> Dictionary driven order first build
        d_updatedNamesDict = returnObjectGeneratedNameDict(self.i_node.mNode,ignore)
        
        if 'cgmName' not in d_updatedNamesDict.keys() and search.returnObjectType(self.i_node.mNode) !='group':
            self.i_node.doStore('cgmName',self.i_node.getShortName())
            d_updatedNamesDict = returnObjectGeneratedNameDict(self.i_node.mNode,ignore)
            
        iterator = self.getIterator()        
        if iterator:
            d_updatedNamesDict['cgmIterator'] = str(iterator)
                
        log.info(returnCombinedNameFromDict(d_updatedNamesDict))
        return returnCombinedNameFromDict(d_updatedNamesDict)
    
    #@r9General.Timer
    def doNameObject(self,**kws):
        nameCandidate = self.returnUniqueGeneratedName(**kws)
	mc.rename(self.i_node.mNode,nameCandidate)
        #self.i_node.rename(nameCandidate)
	
        str_baseName = self.i_node.getBaseName()
        if  str_baseName != nameCandidate:
            log.warning("'%s' not named to: '%s'"%(str_baseName,nameCandidate))
            
        return str_baseName
    
    def doName(self,nameChildren=False,**kws):
	#Try naming object
	try:self.doNameObject(**kws)
	except StandardError,error:
	    raise StandardError,"NameFactory.doName.doNameObject failed: %s"%error
	
	i_rootObject = self.i_node
	
	shapes = mc.listRelatives(i_rootObject.mNode,shapes=True,fullPath=True) or []
	if shapes:
	    l_iShapes = []
	    for s in shapes:
		if not mc.referenceQuery(s, isNodeReferenced=True):
		    l_iShapes.append(cgmMeta.cgmNode(s))
	    for i_s in l_iShapes:
		log.info("on shape: '%s'"%i_s.mNode)
		self.i_node = i_s
		try:self.doNameObject(**kws)
		except StandardError,error:
		    raise StandardError,"NameFactory.doName.doNameObject child ('%s') failed: %s"%self.i_node.getShortName(),error
		    
	#Then the children
	if nameChildren:#Initialize them all so we don't lose them
	    l_iChildren = []
	    for o in mc.listRelatives(i_rootObject.mNode, allDescendents = True,type='transform',fullPath=True) or []:
		l_iChildren.append(cgmMeta.cgmNode(o))
	    
	    if l_iChildren:
		for i_c in l_iChildren:
		    log.info("on child: '%s'"%i_c.mNode)		    
		    self.i_node = i_c
		    try:self.doNameObject(**kws)
		    except StandardError,error:
			raise StandardError,"NameFactory.doName.doNameObject child ('%s') failed: %s"%self.i_node.getShortName(),error
			
        
        
#>>>Utilities
#==================================================================================
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