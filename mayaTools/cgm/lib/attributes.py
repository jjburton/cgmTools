#=================================================================================================================================================
#=================================================================================================================================================
#	attribute - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with attributes
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
#
#   
#=================================================================================================================================================

import maya.cmds as mc
from cgm.lib import guiFactory,dictionary,settings

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()

attrTypesDict = {'message':['message','msg','m'],
                 'double':['float','fl','f','doubleLinear'],
                 'string':['string','s','str'],
                 'long':['long','int','i','integer'],
                 'bool':['bool','b','boolean'],
                 'enum':['enum','options','e'],
                 'vector':['vector','vec','v']}
                 
dataConversionDict = {'long':int,
                      'string':str,
                      'double':float}
                      
def returnAttrListFromStringInput (stringInput1,stringInput2 = None):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes an list of string variables to add to an object as string
    attributes. Skips it if it exists.

    ARGUMENTS:
    stringInput(string/stringList)

    RETURNS:
    [obj,attr]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if '.' in list(stringInput1):
        buffer = stringInput1.split('.')
        assert mc.objExists(buffer[0]) is True,"'%s' doesn't exsit"%buffer[0]
        assert len(buffer) == 2, "'%s' has too many .'s"%stringInput1
        obj = buffer [0]
        attr = buffer[1]
        return [obj,attr]
    elif len(stringInput1) == 2:
        assert mc.objExists(stringInput1[0]) is True,"'%s' doesn't exsit"%stringInput1[0]
        obj = stringInput1 [0]
        attr = stringInput1[1]
        return [obj,attr]
    elif stringInput2 !=None:
        assert mc.objExists(stringInput1) is True,"'%s' doesn't exsit"%stringInput1
        return [stringInput1,stringInput2]

    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Storing fuctions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def storeInfo(obj,infoType,info,overideMessageCheck = False,leaveUnlocked = False):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Stores autoname stuff to an object where the variable name is the
    infoType and the info is the info stored
    -If info is object, it connects the attribute as a message to that object
    -If info is attribute, connected to attribute
    -Otherwise, stored as string

    ARGUMENTS:
    obj(string) - object to add our tag to
    infoType(string) - cgmName, cgmType, etc
    info(string) - info to store, object to connect to, attribute to connect to
    overideMessageCheck(bool) = default -False - whether to overide the objExists check

    RETURNS:
    True/False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    typeDictionary = dictionary.initializeDictionary(typesDictionaryFile)
    namesDictionary = dictionary.initializeDictionary(namesDictionaryFile)
    settingsDictionary = dictionary.initializeDictionary(settingsDictionaryFile)
    attrTypes = returnObjectsAttributeTypes(obj)    
    goodToGo = False
    infoData = 0

    #Force leave  unlocked to be on in the case of referenced objects.
    if mc.referenceQuery(obj, isNodeReferenced=True):
        leaveUnlocked = True


    if mc.objExists(info):
        if overideMessageCheck == False:
            infoData = 'message'
    if mc.objExists(info) and '.' in list(info):
        if '[' not in info:
            infoData = 'attribute'
        else:
            infoData = 'string'
    if infoType in settingsDictionary:
        infoTypeName = settingsDictionary.get(infoType)
        goodToGo = True
        # Checks to see if the type exists in the library
        if infoType == 'cgmType':
            if info in typeDictionary:
                goodToGo = True
            else:
                goodToGo = True
    else:
        infoTypeName = infoType
        goodToGo = True

    attributeBuffer = ('%s%s%s' % (obj,'.',infoTypeName))
    """ lock check """
    wasLocked = False
    if (mc.objExists(attributeBuffer)) == True:
        if mc.getAttr(attributeBuffer,lock=True) == True:
            wasLocked = True
            mc.setAttr(attributeBuffer,lock=False)

    if goodToGo == True:
        if infoData == 'message':
            storeObjectToMessage(info,obj,infoType)
            if leaveUnlocked != True:
                mc.setAttr(('%s%s%s' % (obj,'.',infoType)),lock=True)
        else:
            """ 
            if we get this far and it's a message node we're trying
            to store other data to we need to delete it
            """
            if queryIfMessage(obj,infoTypeName) == True:
                deleteAttr(obj,infoTypeName)
            """
            Make our new string attribute if it doesn't exist
            """
            if mc.objExists(attributeBuffer) == False:
                addStringAttributeToObj(obj,infoTypeName)
                if leaveUnlocked != True:
                    mc.setAttr(attributeBuffer,lock=True)
            """
            set the data
            """
            if infoData == 'attribute':
                infoAttrType = mc.getAttr(info,type=True)
                if mc.objExists(obj+'.'+infoType):
                    objAttrType = mc.getAttr((obj+'.'+infoType),type=True)
                    if infoAttrType != objAttrType:
                        convertAttrType((obj+'.'+infoType),infoAttrType)
                print infoAttrType
                print objAttrType
                
                doConnectAttr(info,attributeBuffer)
                
                if leaveUnlocked != True:
                    mc.setAttr(attributeBuffer,lock=True)
            else:
                doSetStringAttr(attributeBuffer,info)
                if leaveUnlocked != True:
                    mc.setAttr(attributeBuffer,lock=True)
        return True
    else:
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Set/Copy/Delete Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def doGetAttr(obj,attr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for getAttr which get's message objects as well as parses double3 type 
    attributes to a list

    ARGUMENTS:
    obj(string)
    attr(string)

    RETURNS:
    attrInfo(varies)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if mc.objExists(obj+'.'+attr):
        attrType = mc.getAttr((obj+'.'+attr),type=True)
        objAttributes =(mc.listAttr (obj))
        messageBuffer = []
        messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))

        if messageQuery == True:
            query = (mc.listConnections(obj+'.'+attr))
            if not query == None:
                return query[0]
        elif attrType == 'double3':
            childrenAttrs = mc.attributeQuery(attr, node =obj, listChildren = True)
            dataBuffer = []
            for childAttr in childrenAttrs:
                dataBuffer.append(mc.getAttr(obj+'.'+childAttr))
            return dataBuffer
        elif attrType == 'double':
            parentAttr = mc.attributeQuery(attr, node =obj, listParent = True)
            if parentAttr[0] not in objAttributes:
                attrDict[attr] = (mc.getAttr((obj+'.'+attr)))
        else:
            return (mc.getAttr((obj+'.'+attr)))
    else:
        return False




    mc.attributeQuery('position', node ='closestPointOnMesh3', listChildren = True)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def doConnectAttr(fromAttr,toAttr,forceLock = False,transferConnection=False):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for setAttr which will unlock a locked node it's given
    to force a setting of the values. Also has a lock when done overide.
    In addition has transfer connections ability for buffer nodes.

    ARGUMENTS:
    attribute(string) - 'obj.attribute'
    value() - depends on the attribute type
    forceLock(bool) = False(default)
    transferConnection(bool) - (False) - whether you wante to transfer the existing connection to or not
                                        useful for buffer connections
    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    wasLocked = False
    if (mc.objExists(toAttr)) == True:
        if mc.getAttr(toAttr,lock=True) == True:
            wasLocked = True
            mc.setAttr(toAttr,lock=False)
            bufferConnection = returnDriverAttribute(toAttr)
            breakConnection(toAttr)
            mc.connectAttr(fromAttr,toAttr)
        else:
            bufferConnection = returnDriverAttribute(toAttr)
            breakConnection(toAttr)
            mc.connectAttr(fromAttr,toAttr)

    if wasLocked == True or forceLock == True:
        mc.setAttr(toAttr,lock=True)

    if transferConnection == True:
        if bufferConnection != False:
            mc.connectAttr(bufferConnection,fromAttr)


def doSetAttr(attribute,value,forceLock = False):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for setAttr which will unlock a locked node it's given
    to force a setting of the values. Also has a lock when done overide

    ARGUMENTS:
    attribute(string) - 'obj.attribute'
    value() - depends on the attribute type
    forceLock(bool) = False(default)

    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    wasLocked = False
    if (mc.objExists(attribute)) == True:
        if mc.getAttr(attribute,lock=True) == True:
            wasLocked = True
            mc.setAttr(attribute,lock=False)
            mc.setAttr(attribute,value)
        else:
            mc.setAttr(attribute,value)

    if wasLocked == True or forceLock == True:
        mc.setAttr(attribute,lock=True)

def doSetStringAttr(attribute,value,forceLock = False):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for setAttr which will unlock a locked node it's given
    to force a setting of the values. Also has a lock when done overide

    ARGUMENTS:
    attribute(string) - 'obj.attribute'
    value() - depends on the attribute type
    forceLock(bool) = False(default)

    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    wasLocked = False
    if (mc.objExists(attribute)) == True:
        if mc.getAttr(attribute,lock=True) == True:
            wasLocked = True
            breakConnection(attribute)
            mc.setAttr(attribute,lock=False)
            mc.setAttr(attribute,value, type='string')
        else:
            breakConnection(attribute)
            mc.setAttr(attribute,value, type='string')

    if wasLocked == True or forceLock == True:
        mc.setAttr(attribute,lock=True)
        
def convertAttrType(targetAttrName,attrType):
    """ 
    Attempts to convert an existing attrType from one type to another. 
    Enum's are stored to strings as 'option1;option2'.
    Strings with a ';' will split to enum options on conversion.
    
    Keyword arguments:
    targetAttrName(string) -- name for an existing attribute name
    attrType(string) -- desired attribute type
    
    """    
    assert mc.objExists(targetAttrName) is True,"'%s' doesn't exist!"%targetAttrName
    
    aType = False
    for option in attrTypesDict.keys():
        if attrType in attrTypesDict.get(option): 
            aType = option
            break
        
    assert aType is not False,"'%s' is not a valid attribute type!"%attrType
    
            
    #>>> Get data
    targetLock = False
    if mc.getAttr((targetAttrName),lock = True) == True:
        targetLock = True
        mc.setAttr(targetAttrName,lock = False)
    
    targetType = mc.getAttr(targetAttrName,type=True)
    
    buffer = targetAttrName.split('.')
    targetObj = buffer[0]
    targetAttr = buffer[-1]
    
    print "Target object is '%s'"%targetObj
    print "Target attr is '%s'"%targetAttr
    
    #>>> Do the stuff
    if aType != targetType:
        # get data connection and data to transfer after we make our new attr
        # see if it's a message attribute to copy    
        connection = ''
        if queryIfMessage(targetObj,targetAttr):
            dataBuffer = (returnMessageObject(targetObj,targetAttr))
        else:
            connection = returnDriverAttribute(targetAttrName)            
            dataBuffer = mc.getAttr(targetAttrName)
        
        if targetType == 'enum':
            enumStuff = mc.attributeQuery(targetAttr, node = targetObj, listEnum=True)
            buffer = enumStuff[0].split(':')
            dataBuffer = ';'.join(buffer)
            
        print "Data buffer is '%s'"%dataBuffer   
        
        deleteAttr(targetObj,targetAttr)
        
        """if it doesn't exist, make it"""
        if aType == 'string':
            mc.addAttr (targetObj, ln = targetAttr,  dt = aType )
            
        elif aType == 'enum':
            if dataBuffer:
                if ';' in dataBuffer:
                    enumStuff = dataBuffer.split(';')
                else:
                    enumStuff = [dataBuffer]
            else:
                enumStuff = ['off','on']
            print enumStuff
            mc.addAttr (targetObj, ln = targetAttr, at=  'enum', en = ':'.join(enumStuff))
            
        elif aType == 'double3':
            mc.addAttr (targetObj, ln=targetAttr, at= 'double3')
            mc.addAttr (targetObj, ln=(targetAttr+'X'),p=targetAttr , at= 'double')
            mc.addAttr (targetObj, ln=(targetAttr+'Y'),p=targetAttr , at= 'double')
            mc.addAttr (targetObj, ln=(targetAttr+'Z'),p=targetAttr , at= 'double')
        else:
            mc.addAttr (targetObj, ln = targetAttr,  at = aType )
            
        if connection:
            try:
                doConnectAttr(connection,targetAttrName)
            except:
                guiFactory.warning("Couldn't connect '%s' to the '%s'"%(connection,targetAttrName))
                
        elif dataBuffer is not None:
            if mc.objExists(dataBuffer) and aType == 'message':
                storeObjectToMessage(dataBuffer,targetObj,targetAttr)
            else:
                try:
                    if aType == 'long':
                        mc.setAttr(targetAttrName,int(float(dataBuffer)))
                    elif aType == 'string':
                        mc.setAttr(targetAttrName,str(dataBuffer),type = aType)
                    elif aType == 'double':
                        mc.setAttr(targetAttrName,float(dataBuffer))   
                    else:
                        mc.setAttr(targetAttrName,dataBuffer,type = aType)
                except:
                    guiFactory.warning("Couldn't add '%s' to the '%s'"%(dataBuffer,targetAttrName))
                    
                
        if targetLock:
            mc.setAttr(targetAttrName,lock = True)
            


def copyKeyableAttrs(fromObject,toObject,attrsToCopy=[True],connectAttrs = False):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copy attributes from one object to another. If the attribute already
    exists, it'll copy the values. If it doesn't, it'll make it.

    ARGUMENTS:
    fromObject(string) - obj with attrs
    toObject(string) - obj to copy to
    attrsToCopy(list) - list of attr names to copy, if [True] is used, it will do all of them

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrDict = {}
    keyableAttrs =(mc.listAttr (fromObject, keyable=True))
    matchAttrs = []
    lockAttrs = {}
    if keyableAttrs == None:
        return False
    else:
        if attrsToCopy[0] == 1:
            matchAttrs = keyableAttrs
        else:
            for attr in attrsToCopy:
                if attr in keyableAttrs:
                    matchAttrs.append(attr)
    """ Get the attribute types of those the source object"""
    attrTypes = returnObjectsAttributeTypes(fromObject)

    print ('The following attrirbues will be created and copied')
    print matchAttrs
    #>>> The creation of attributes part
    if len(matchAttrs)>0:
        for attr in matchAttrs:
            """ see if it was locked, unlock it and store that it was locked """
            if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
                lockAttrs[attr] = True
                mc.setAttr((fromObject+'.'+attr),lock=False)
            """if it doesn't exist, make it"""
            if mc.objExists(toObject+'.'+attr) is not True:
                attrType = (attrTypes.get(attr))
                print attrType
                if attrType == 'string':
                    mc.addAttr (toObject, ln = attr,  dt =attrType )
                elif attrType == 'enum':
                    enumStuff = mc.attributeQuery(attr, node=fromObject, listEnum=True)
                    mc.addAttr (toObject, ln=attr, at= 'enum', en=enumStuff[0])
                elif attrType == 'double3':
                    mc.addAttr (toObject, ln=attr, at= 'double3')
                    mc.addAttr (toObject, ln=(attr+'X'),p=attr , at= 'double')
                    mc.addAttr (toObject, ln=(attr+'Y'),p=attr , at= 'double')
                    mc.addAttr (toObject, ln=(attr+'Z'),p=attr , at= 'double')
                else:
                    mc.addAttr (toObject, ln = attr,  at =attrType )
        """ copy values """
        mc.copyAttr(fromObject,toObject,attribute=matchAttrs,v=True,ic=True)

        """ relock """
        for attr in lockAttrs.keys():
            mc.setAttr((fromObject+'.'+attr),lock=True)
            mc.setAttr((toObject+'.'+attr),lock=True)


        """ Make it keyable """    
        for attr in matchAttrs:
            mc.setAttr((toObject+'.'+attr),keyable=True)

        if connectAttrs:
            for attr in matchAttrs:
                doConnectAttr((toObject+'.'+attr),(fromObject+'.'+attr))

        return True

    else:
        return False


def copyUserAttrs(fromObject,toObject,attrsToCopy=[True]):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copy attributes from one object to another. If the attribute already
    exists, it'll copy the values. If it doesn't, it'll make it.

    ARGUMENTS:
    fromObject(string) - obj with attrs
    toObject(string) - obj to copy to
    attrsToCopy(list) - list of attr names to copy, if [True] is used, it will do all of them

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrDict = {}
    userAttrs =(mc.listAttr (fromObject, userDefined=True))
    matchAttrs = []
    lockAttrs = {}
    if userAttrs == None:
        return False
    else:
        if attrsToCopy[0] == 1:
            matchAttrs = userAttrs
        else:
            for attr in attrsToCopy:
                if attr in userAttrs:
                    matchAttrs.append(attr)
    """ Get the attribute types of those the source object"""
    attrTypes = returnObjectsAttributeTypes(fromObject)

    #>>> The creation of attributes part
    messageAttrs = {}
    if len(matchAttrs)>0:
        for attr in matchAttrs:
            # see if it's a message attribute to copy    
            if queryIfMessage(fromObject,attr):
                messageAttrs[attr] = (returnMessageObject(fromObject,attr))
                
            """ see if it was locked, unlock it and store that it was locked """
            if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
                lockAttrs[attr] = True
                mc.setAttr((fromObject+'.'+attr),lock=False)
                
            """if it doesn't exist, make it"""
            if mc.objExists(toObject+'.'+attr) is not True:
                attrType = (attrTypes.get(attr))
                if attrType == 'string':
                    mc.addAttr (toObject, ln = attr,  dt =attrType )
                elif attrType == 'enum':
                    enumStuff = mc.attributeQuery(attr, node=fromObject, listEnum=True)
                    mc.addAttr (toObject, ln=attr, at= 'enum', en=enumStuff[0])
                elif attrType == 'double3':
                    mc.addAttr (toObject, ln=attr, at= 'double3')
                    mc.addAttr (toObject, ln=(attr+'X'),p=attr , at= 'double')
                    mc.addAttr (toObject, ln=(attr+'Y'),p=attr , at= 'double')
                    mc.addAttr (toObject, ln=(attr+'Z'),p=attr , at= 'double')
                else:
                    mc.addAttr (toObject, ln = attr,  at =attrType )
        """ copy values """
        mc.copyAttr(fromObject,toObject,attribute=matchAttrs,v=True,ic=True,oc=True,keepSourceConnections=True)
        
        if messageAttrs:
            for a in messageAttrs.keys():
                storeInfo(toObject,a,messageAttrs.get(a))

        """ relock """
        for attr in lockAttrs.keys():
            mc.setAttr((fromObject+'.'+attr),lock=True)
            mc.setAttr((toObject+'.'+attr),lock=True)
        return True
    else:
        return False

def copyNameTagAttrs(fromObject,toObject):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copy cgmTag attrs from one object to another. 

    ARGUMENTS:
    fromObject(string) - obj with attrs
    toObject(string) - obj to copy to

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    lockAttrs = {}
    attrsToCopy = ['cgmName','cgmType','cgmDirection','cgmPosition','cgmNameModifier','cgmTypeModifier','cgmDirectionModifier']
    tagsDict = returnUserAttrsToDict(fromObject)

    #>>> The creation of attributes part
    if len(tagsDict.keys())>0:
        for attr in tagsDict.keys():

            """if it doesn't exist, store  it"""
            if mc.objExists(fromObject+'.'+attr) and attr in attrsToCopy:
                """ see if it was locked, unlock it and store that it was locked """  
                if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
                    lockAttrs[attr] = True

                storeInfo(toObject,attr,tagsDict.get(attr))


        """ relock """
        for attr in lockAttrs.keys():
            mc.setAttr((fromObject+'.'+attr),lock=True)
            mc.setAttr((toObject+'.'+attr),lock=True)
        return True
    else:
        return False

def swapNameTagAttrs(object1,object2):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Swap cgmNameTag attrs from one object to another. 

    ARGUMENTS:
    fromObject(string) - 
    toObject(string) - 

    RETURNS:
    None
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    object1LockAttrs = {}
    object2LockAttrs = {}

    attrsToCopy = ['cgmName','cgmType','cgmDirection','cgmPosition','cgmNameModifier','cgmTypeModifier','cgmDirectionModifier']
    object1TagsDict = returnUserAttrsToDict(object1)
    object2TagsDict = returnUserAttrsToDict(object2)

    object1TagTypesDict = returnObjectsAttributeTypes(object1,userDefined = True)
    object2TagTypesDict = returnObjectsAttributeTypes(object2,userDefined = True)

    #>>> execution stuff
    if object1TagsDict and object2TagsDict:
        #>>> Object 1
        for attr in object1TagsDict.keys():
            """if it doesn't exist, store  it"""
            if mc.objExists(object1+'.'+attr) and attr in attrsToCopy:
                """ see if it was locked, unlock it and store that it was locked """  
                if mc.getAttr((object1+'.'+attr),lock=True) == True:
                    object1LockAttrs[attr] = True

                deleteAttr(object1,attr) 
        #Copy object 2's tags to object 1            
        for attr in object2TagsDict.keys():
            if object2TagTypesDict.get(attr) == 'message':
                storeInfo(object1,attr,object2TagsDict.get(attr))
            else:
                storeInfo(object1,attr,object2TagsDict.get(attr),True)

        #>>> Object 2
        for attr in object2TagsDict.keys():
            """if it doesn't exist, store  it"""
            if mc.objExists(object2+'.'+attr) and attr in attrsToCopy:
                """ see if it was locked, unlock it and store that it was locked """  
                if mc.getAttr((object2+'.'+attr),lock=True) == True:
                    object2LockAttrs[attr] = True

                deleteAttr(object2,attr) 

        #Copy object 1's tags to object 2                      
        for attr in object1TagsDict.keys():
            if object1TagTypesDict.get(attr) == 'message':
                storeInfo(object2,attr,object1TagsDict.get(attr))
            else:
                storeInfo(object2,attr,object1TagsDict.get(attr),True)

    else:
        guiFactory.warning("Selected objects don't have cgmTags to swap")





def doSetOverrideSettings(obj,enabled=True,displayType=1,levelOfDetail = 0,overrideShading=1,overrideTexturing=1,overridePlayback=1,overrideVisible=1):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Sets drawing override settings on an object or it's shapes

    ARGUMENTS:
    obj(string) - the object we'd like to startfrom
    enabled(bool) - whether to enable the override or not
    displayType(int) - (1)
                Modes - 0 - Normal
                        1 - Template
                        2 - Reference

    levelOfDetail(int) -(0)
                Modes - 0 - Full
                        1 - Bounding Box
    overrideShading(bool) - (1)
    overrideTexturing(bool) - (1)
    overridePlayback(bool) - (1)
    overrideVisible(bool) - (1)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    shapes = mc.listRelatives(obj,shapes = True)
    if shapes > 0:
        for shape in shapes:
            doSetAttr((shape+'.overrideEnabled'),enabled)
            doSetAttr((shape+'.overrideDisplayType'),displayType)
            doSetAttr((shape+'.overrideLevelOfDetail'),levelOfDetail)
            doSetAttr((shape+'.overrideShading'),overrideShading)
            doSetAttr((shape+'.overrideTexturing'),overrideTexturing)
            doSetAttr((shape+'.overridePlayback'),overridePlayback)
            doSetAttr((shape+'.overrideVisible'),overrideVisible)
    else:
        doSetAttr((obj+'.overrideEnabled'),enabled)
        doSetAttr((obj+'.overrideDisplayType'),displayType)
        doSetAttr((obj+'.overrideLevelOfDetail'),levelOfDetail)
        doSetAttr((obj+'.overrideShading'),overrideShading)
        doSetAttr((obj+'.overrideTexturing'),overrideTexturing)
        doSetAttr((obj+'.overridePlayback'),overridePlayback)
        doSetAttr((obj+'.overrideVisible'),overrideVisible)

def doToggleTemplateDisplayMode(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Toggles the template disply mode of an object

    ARGUMENTS:
    obj(string) - the object we'd like to startfrom

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    shapes = mc.listRelatives(obj,shapes = True)  

    if shapes > 0:
        for shape in shapes:
            currentState = doGetAttr(shape,'template')
            doSetAttr((shape+'.template'), not currentState)

    else:
        currentState = doGetAttr(obj,'template')
        doSetAttr((obj+'.template'), not currentState)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def deleteAttr(obj,attr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Deletes and attribute if it exists. Even if it's locked

    ARGUMENTS:
    attr(string) - the attribute to delete

    RETURNS:
    True/False depending if it found anything to destroy
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrBuffer = (obj+'.'+attr)
    if (mc.objExists(attrBuffer)) == True:
        if mc.getAttr(attrBuffer,lock=True) == True:
            mc.setAttr(attrBuffer,lock=False)
        mc.deleteAttr(attrBuffer)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Joint Related
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def setRotationOrderObj (obj, ro):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object and rotation order (xyz,xzy,etc) into it and it will
    set the object to that rotation order

    ARGUMENTS:
    obj(string) - object
    ro(string) - rotation order 
                            xyz,yzx,zxy,xzy,yxz,zyx,none

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ pass an object and rotation order (xyz,xzy,etc) into it and it will set the object to that rotation order """
    validRO = True
    rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
    if not ro in rotationOrderDictionary:
        print (ro + ' is not a valid rotation order. Expected one of the following:')
        print rotationOrderDictionary
        validRO = False
    else:  
        correctRo = rotationOrderDictionary[ro]        
        mc.setAttr ((obj+'.rotateOrder'), correctRo)
    return validRO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utility Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def doSetLockHideKeyableAttr (obj,lock=True,visible=False,keyable=False,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an oject, True/False for locking it, True/False for visible in
    channel box, and which channels you want locked in ('tx','ty',etc) form

    ARGUMENTS:
    obj(string)
    lock(bool)
    visible(bool)
    keyable(bool)
    channels(list) - (tx,ty,vis,whatever)

    RETURNS:
    None
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    lockOptions = ('tx','ty','tz','rx','ry','rz','sx','sy','sz','v')
    for channel in channels:
        if channel in lockOptions:        
            mc.setAttr ((obj+'.'+channel),lock=lock, keyable=keyable, channelBox=visible)                   
        else:
            print (channel + ' is not a valid option. Skipping.')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Connections Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def breakConnection(attr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Breaks a connection on an attribute if there is one

    ARGUMENTS:
    attr(string) - the attribute to break the connection on

    RETURNS:
    True/False depending if it found anything to break
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    source = []
    if (mc.connectionInfo (attr,isDestination=True)):
        source = (mc.connectionInfo (attr,sourceFromDestination=True))
        print source

        #>>>See if stuff is locked
        if mc.getAttr(attr,lock=True):
            print ('attr locked')
            mc.setAttr(attr,lock=False)
        driverAttr = returnDriverAttribute(attr)
        if driverAttr:
            print ('ODriver is %s' %driverAttr)
            if mc.getAttr(driverAttr,lock=True):
                mc.setAttr(driverAttr,lock=False)
        try:
            print ('On %s' %source)
            mc.disconnectAttr (source,attr)
            return source
        except:
            guiFactory.warning('Unable to break connection. See script dump')
    else:
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnDriverAttribute(attribute):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the driverAttribute of an attribute if there is one

    ARGUMENTS:
    attribute(string)

    RETURNS:
    Success - driverAttribute(string)
    Failure - False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if (mc.connectionInfo (attribute,isDestination=True)) == True:
        sourcebuffer = (mc.connectionInfo (attribute,sourceFromDestination=True))
        return sourcebuffer
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDriverObject(attribute):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the driver of an attribute if there is one

    ARGUMENTS:
    attribute(string)

    RETURNS:
    Success - driverObj(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objectBuffer =  returnDriverAttribute (attribute)
    if objectBuffer:
        strippedObject = '.'.join(objectBuffer.split('.')[0:-1])
        return strippedObject
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDrivenAttribute(attribute):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the drivenAttribute of an attribute if there is one

    ARGUMENTS:
    attribute(string)

    RETURNS:
    Success - drivenAttribute(string)
    Failure - False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if (mc.connectionInfo (attribute,isSource=True)) == True:
        destinationBuffer = (mc.connectionInfo (attribute,destinationFromSource=True))
        return destinationBuffer
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDrivenObject(attribute):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the driven object of an attribute if there is one

    ARGUMENTS:
    attribute(string)

    RETURNS:
    Success - drivenObj(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objectsBuffer =  returnDrivenAttribute (attribute)
    returnBuffer = []
    if objectsBuffer:
        for o in objectsBuffer:
            strippedObject = '.'.join(o.split('.')[0:-1])
            returnBuffer.append( strippedObject )
        return returnBuffer
    else:
        return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectsAttributeTypes(obj,*a, **kw ):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with user attributes and it will return a dictionary attribute's data types

    ARGUMENTS:
    obj(string) - obj with attrs
    any arguments for the mc.listAttr command

    RETURNS:
    attrDict(Dictionary) - dictionary in terms of {[attrName : type],[etc][etc]}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj) is True, "'%s' doesn't exist"%obj
    attrs =(mc.listAttr (obj,*a, **kw ))
    attrDict = {}
    if not attrs == None:   
        for attr in attrs:
            try:
                attrDict[attr] = (mc.getAttr((obj+'.'+attr),type=True))
            except:
                pass
        return attrDict
    else:
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnUserAttributes(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns user created attributes of an object

    ARGUMENTS:
    obj(string) - obj to check

    RETURNS:
    messageList - nested list in terms of [[attrName, target],[etc][etc]]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    buffer = mc.listAttr(obj,ud=True)
    if buffer > 0:
        return buffer
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnMessageObject(storageObject, messageAttr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the object linked to the message attribute

    ARGUMENTS:
    storageObject(string) - object holding the message attr
    messageAttr(string) - name of the message attr

    RETURNS:
    messageObject(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrBuffer = (storageObject+'.'+messageAttr)
    if mc.objExists(attrBuffer) == True:
        messageObject = (mc.listConnections (attrBuffer))
        if messageObject != None:
            return messageObject[0]
        else:
            return False
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnMessageObjs(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with messages, it will return a list of the objects

    ARGUMENTS:
    obj(string) - obj with message attrs

    RETURNS:
    messageObject(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objList = []
    objAttributes =(mc.listAttr (obj, userDefined=True))
    if not objAttributes == None:
        for attr in objAttributes:                    
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            if messageQuery == True:
                query = (mc.listConnections(obj+'.'+attr))
                if not query == None:
                    objList.append (query[0])
        return objList
    else:
        return False  
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnMessageAttrs(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with messages, it will return a nested list in terms of [[attrName, target],[etc][etc]]

    ARGUMENTS:
    obj(string) - obj with message attrs

    RETURNS:
    messageList(Dictionary) - dictionary in terms of {[attrName : target],[etc][etc]}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    messageList = {}
    objAttributes =(mc.listAttr (obj, userDefined=True))
    if not objAttributes == None:
        for attr in objAttributes:                    
            messageBuffer = []
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            if messageQuery == True:
                query = (mc.listConnections(obj+'.'+attr))
                if not query == None:
                    messageList[attr] = (query[0])
        return messageList
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnMessageAttrsAsList(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with messages, it will return a nested list in terms of [[attrName, target],[etc][etc]]

    ARGUMENTS:
    obj(string) - obj with message attrs

    RETURNS:
    messageList - nested list in terms of [[attrName, target],[etc][etc]]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    messageList = []
    objAttributes =(mc.listAttr (obj, userDefined=True))
    if not objAttributes == None:
        for attr in objAttributes:                    
            messageBuffer = []
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            if messageQuery == True:
                query = (mc.listConnections(obj+'.'+attr))
                if not query == None:
                    messageBuffer.append (attr)
                    messageBuffer.append (query[0])
                    messageList.append (messageBuffer)
        return messageList
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnUserAttrsToDict(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with user attributes and it will return a dictionary of the data back

    ARGUMENTS:
    obj(string) - obj with attrs

    RETURNS:
    attrDict(Dictionary) - dictionary in terms of {[attrName : target],[etc][etc]}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrDict = {}
    objAttributes =(mc.listAttr (obj, userDefined=True))
    attrTypes = returnObjectsAttributeTypes(obj,userDefined = True)
    if not objAttributes == None:
        for attr in objAttributes:                    
            messageBuffer = []
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            attrType = attrTypes.get(attr)
            if messageQuery == True:
                query = (mc.listConnections(obj+'.'+attr))
                if not query == None:
                    attrDict[attr] = (query[0])
            elif attrType == 'double3':
                childrenAttrs = mc.attributeQuery(attr, node =obj, listChildren = True)
                dataBuffer = []
                for childAttr in childrenAttrs:
                    dataBuffer.append(mc.getAttr(obj+'.'+childAttr))
                attrDict[attr] = dataBuffer
            elif attrType == 'double':
                parentAttr = mc.attributeQuery(attr, node =obj, listParent = True)
                if parentAttr != None:
                    if parentAttr[0] not in objAttributes:
                        attrDict[attr] = (mc.getAttr((obj+'.'+attr)))
            else:
                attrDict[attr] = (mc.getAttr((obj+'.'+attr)))
        return attrDict
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnUserAttrsToList(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with user attributes and it will return a dictionary of the data back

    ARGUMENTS:
    obj(string) - obj with attrs

    RETURNS:
    attrsList(list) - nested list in terms of [[attrName : target],[etc][etc]]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrsList = []
    attrTypes = returnUserAttrsToDict(obj)
    objAttributes = attrTypes.keys()
    
    if not objAttributes == None:
        for attr in objAttributes:                    
            messageBuffer = []
            buffer = []
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            attrType = attrTypes.get(attr)
            if messageQuery == True:
                query = (mc.listConnections(obj+'.'+attr))
                if not query == None:
                    buffer.append(attr)
                    buffer.append(query[0])
                    attrsList.append(buffer)
            elif attrType == 'double3':
                childrenAttrs = mc.attributeQuery(attr, node =obj, listChildren = True)
                dataBuffer = []
                for childAttr in childrenAttrs:
                    dataBuffer.append(mc.getAttr(obj+'.'+childAttr))
                buffer.append(attr)
                buffer.append(dataBuffer)
                attrsList.append(buffer)
            elif attrType == 'double':
                parentAttr = mc.attributeQuery(attr, node =obj, listParent = True)
                if parentAttr[0] not in objAttributes:
                    buffer.append(attr)
                    buffer.append(mc.getAttr((obj+'.'+attr)))
                    attrsList.append(buffer)            
            else:
                buffer.append(attr)
                buffer.append(mc.getAttr((obj+'.'+attr)))
                attrsList.append(buffer)
        return attrsList
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Creation Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addRotateOrderAttr (obj,name):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Add a rotate order attr

    ARGUMENTS:
    obj(string) - object to add attributes to
    attrList(list) - list of attributes to add

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    try:
        mc.addAttr(obj, ln=name, at = 'enum',en = 'xyz:yzx:zxy:xzy:yxz:zyx')
        mc.setAttr((obj+'.'+name),e = True, keyable = True )
        return ("%s.%s"%(obj,name))
    except:
        guiFactory.warning("'%s' failed to add '%s'"%(obj,name))
        

def addAttributesToObj (obj, attributeTypesDict):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes an list of string variables to add to an object as string
    attributes. Skips it if it exists.

    ARGUMENTS:
    obj(string) - object to add attributes to
    attrList(list) - list of attributes to add

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """sort the keys"""
    sortedAttributes = dictionary.returnDictionarySortedToList(attributeTypesDict,True)

    """ make em"""
    for set in sortedAttributes:
        attr = set[0]
        attrType = set[1]
        attrCache = (obj+'.'+attr)
        if not mc.objExists (attrCache):
            if attrType == 'string':
                mc.addAttr (obj, ln = attr,  dt =attrType )
            elif attrType == 'double3':
                mc.addAttr (obj, ln=attr, at= 'double3')
                mc.addAttr (obj, ln=(attr+'X'),p=attr , at= 'double')
                mc.addAttr (obj, ln=(attr+'Y'),p=attr , at= 'double')
                mc.addAttr (obj, ln=(attr+'Z'),p=attr , at= 'double')
            else:
                mc.addAttr (obj, ln = attr,  at =attrType )

        else:
            print ('"' + attrCache + '" exists, moving on')


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addStringAttributeToObj (obj,attr,*a, **kw ):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a string attribute to an object, passing forward commands


    ARGUMENTS:
    obj(string)
    attr(string)

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

    try: 
        mc.addAttr (obj, ln = attr, dt = 'string',*a, **kw)
        return ("%s.%s"%(obj,attr))
    except:
        guiFactory.warning("'%s' failed to add '%s'"%(obj,attr))
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addIntegerAttributeToObj (obj,attr,*a, **kw ):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a integer attribute to an object, passing forward commands


    ARGUMENTS:
    obj(string)
    attr(string)

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

    try: 
        mc.addAttr (obj, ln = attr, at = 'long',*a, **kw)
        return ("%s.%s"%(obj,attr))
    except:
        guiFactory.warning("'%s' failed to add '%s'"%(obj,attr))
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addMessageAttributeToObj (obj,attr,*a, **kw ):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a integer attribute to an object, passing forward commands


    ARGUMENTS:
    obj(string)
    attr(string)

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

    try: 
        mc.addAttr (obj, ln = attr, at = 'message',*a, **kw )
        return ("%s.%s"%(obj,attr))
    except:
        guiFactory.warning("'%s' failed to add '%s'"%(obj,attr))
        return False   
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addVectorAttributeToObj (obj,attr,*a, **kw):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a vector attribute to an object, passing forward commands

    ARGUMENTS:
    obj(string)
    attr(string)

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """    
    try: 
        mc.addAttr (obj, ln=attr, at= 'double3',*a, **kw)
        mc.addAttr (obj, ln=(attr+'X'),p=attr , at= 'double',*a, **kw)
        mc.addAttr (obj, ln=(attr+'Y'),p=attr , at= 'double',*a, **kw)
        mc.addAttr (obj, ln=(attr+'Z'),p=attr , at= 'double',*a, **kw)       
        return ("%s.%s"%(obj,attr))
    
    except:
        guiFactory.warning("'%s' failed to add '%s'"%(obj,attr))
        return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addStringAttributesToObj (obj, attrList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes an list of string variables to add to an object as string attributes. Skips it if it exists.
    Input -obj, attrList(list).

    ARGUMENTS:
    obj(string) - object to add attributes to
    attrList(list) - list of attributes to add

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    for attr in attrList:        
        attrCache = (obj+'.'+attr)
        if not mc.objExists (attrCache):
            mc.addAttr (obj, ln = attr,  dt = 'string')
            return ("%s.%s"%(obj,attr))            
        else:
            print ('"' + attrCache + '" exists, moving on')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addFloatAttributeToObject (obj, attr,*a, **kw):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a float attribute to an object

    ARGUMENTS:
    obj(string) - object to add attribute to
    attr(string) - attribute name to add
    minValue(int/float) - minimum value
    maxValue(int/float) - maximum value
    default(int/float) - default value

    RETURNS:
    Attribute full name (string) - ex obj.attribute
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

    try: 
        mc.addAttr (obj, ln = attr, at = 'float',*a, **kw)
        return ("%s.%s"%(obj,attr))
    except:
        guiFactory.warning("'%s' failed to add '%s'"%(obj,attr))
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addEnumAttrToObj (obj,attr,optionList=['off','on'],*a, **kw):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a enum attribute to an object

    ARGUMENTS:
    obj(string) - object to add attribute to
    attrName(list)
    optionList(list)
    default(int/float) - default value

    RETURNS:
    Attribute full name (string) - ex obj.attribute
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

    try: 
        mc.addAttr (obj,ln = attr, at = 'enum', en=('%s' %(':'.join(optionList))),*a, **kw)
        mc.setAttr ((obj+'.'+attr),e=True,keyable=True)
        return ("%s.%s"%(obj,attr))
    except:
        guiFactory.warning("'%s' failed to add '%s'"%(obj,attr))
        return False
    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addFloatAttrsToObj (obj,attrList, *a, **kw):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a float attribute to an object

    ARGUMENTS:
    obj(string) - object to add attribute to
    attrList(list) - attribute name to add
    minValue(int/float) - minimum value
    maxValue(int/float) - maximum value
    default(int/float) - default value

    RETURNS:
    Attribute full name (string) - ex obj.attribute
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrsCache=[]
    for attr in attrList:
        attrCache = addFloatAttributeToObject (obj, attr, *a, **kw)
        attrsCache.append(attrCache)
    return attrsCache
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addBoolAttrToObject(obj, attr, *a, **kw):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a section break for an attribute list

    ARGUMENTS:
    obj(string) - object to add attribute to
    attr(string) - name for the section break

    RETURNS:
    Success
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj+'.'+attr) is False,"'%s' already has an attr called '%s'"%(obj,attr)

    try: 
        mc.addAttr (obj, ln = attr,  at = 'bool',*a, **kw)
        mc.setAttr ((obj+'.'+attr), edit = True, channelBox = True)

        return True
    except:
        guiFactory.warning("'%s' failed to add '%s'"%(obj,attr))
        return False
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addSectionBreakAttrToObj(obj, attr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds a section break for an attribute list

    ARGUMENTS:
    obj(string) - object to add attribute to
    attr(string) - name for the section break

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrCache = (obj+'.'+attr)
    if not mc.objExists (attrCache):
        mc.addAttr (obj, ln = attr,  at = 'bool')
        mc.setAttr (attrCache, lock = True, channelBox = True)
    else:
        print ('"' + attrCache + '" exists, moving on')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Message Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def storeObjNameToMessage (obj, storageObj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds the obj name as a message attribute to the storage object

    ARGUMENTS:
    obj(string) - object to store
    storageObject(string) - object to store the info to

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrCache = ('%s%s%s' % (storageObj,'.',obj))
    if  mc.objExists (attrCache):  
        print (attrCache+' already exists')
    else:
        mc.addAttr (storageObj, ln=obj, at= 'message')
        mc.connectAttr ((obj+".message"),(storageObj+'.'+ obj))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def storeObjectToMessage (obj, storageObj, messageName):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds the obj name as a message attribute to the storage object with
    a custom message attribute name

    ARGUMENTS:
    obj(string) - object to store
    storageObject(string) - object to store the info to
    messageName(string) - message name to store it as

    RETURNS:
    Success
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrCache = (storageObj+'.'+messageName)
    try:
        if  mc.objExists (attrCache):
            if queryIfMessage(storageObj,messageName):
                print (attrCache+' already exists. Adding to existing message node.')
                breakConnection(attrCache)
                mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),force=True)
                return True                
            else:
                connections = returnDrivenAttribute(attrCache)
                if connections:
                    for c in connections:
                        breakConnection(c)
                        
                guiFactory.warning("'%s' already exists. Not a message attr, converting."%attrCache)
                deleteAttr(storageObj,messageName)
                
                buffer = mc.addAttr (storageObj, ln=messageName, at= 'message')                
                mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),force=True)
                
                        
                return True
        else:
            mc.addAttr (storageObj, ln=messageName, at= 'message')
            mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName))
            return True
    except:
        return False
    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def storeObjListNameToMessage (objList, storageObj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds the obj names as  message attributes to the storage object

    ARGUMENTS:
    objList(string) - object to store
    storageObj(string) - object to store the info to

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    for obj in objList:
        storeObjNameToMessage (obj, storageObj)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def queryIfMessage(obj,attr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with messages, it will return a nested list in terms of [[attrName, target],[etc][etc]]

    ARGUMENTS:
    obj(string) - obj with message attrs

    RETURNS:
    messageList - nested list in terms of [[attrName, target],[etc][etc]]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if mc.objExists(obj+'.'+attr) != False:
        try:
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            if messageQuery == True:
                return True
        except:
            return False
    else:
        return False