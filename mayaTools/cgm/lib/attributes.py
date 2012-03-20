#=================================================================================================================================================
#=================================================================================================================================================
#	attribute - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with attributes
# 
# REQUIRES:
# 	Maya
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.joshburton.com
# 	Copyright 2011 Josh Burton - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
#   
#=================================================================================================================================================

import maya.cmds as mc
from cgm.lib import guiFactory,dictionary,settings,autoname


namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()


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
    
    REQUIRES:
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
    goodToGo = False
    infoData = 0
    
    #Force leave  unlocked to be on in the case of referenced objects.
    if mc.referenceQuery(obj, isNodeReferenced=True) == True:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

def copyKeyableAttrs(fromObject,toObject,attrsToCopy=[True],connectAttrs = False):
        """                                     
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Copy attributes from one object to another. If the attribute already
        exists, it'll copy the values. If it doesn't, it'll make it.

        REQUIRES:
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
                print ('Sorry, no matched attrs found.')
                return False


def copyUserAttrs(fromObject,toObject,attrsToCopy=[True]):
        """                                     
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Copy attributes from one object to another. If the attribute already
        exists, it'll copy the values. If it doesn't, it'll make it.

        REQUIRES:
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
                return True
        else:
                print ('Sorry, no matched attrs found.')
                return False
            
def copyNameTagAttrs(fromObject,toObject):
        """                                     
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Copy cgmTag attrs from one object to another. 

        REQUIRES:
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
                print ('Sorry, no matched attrs found.')
                return False
            
def swapNameTagAttrs(object1,object2):
        """                                     
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Swap cgmNameTag attrs from one object to another. 

        REQUIRES:
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
        
        object1TagTypesDict = returnObjectsUserAttributeTypes(object1)
        object2TagTypesDict = returnObjectsUserAttributeTypes(object2)

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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
        attribute(string)

        RETURNS:
        Success - drivenAttribute(string)
        Failure - False
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        if (mc.connectionInfo (attribute,isSource=True)) == True:
                destinationBuffer = (mc.connectionInfo (attribute,destinationFromSource=True))
                return destinationBuffer[0]
        else:
                return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDrivenObject(attribute):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Returns the driven object of an attribute if there is one

        REQUIRES:
        attribute(string)

        RETURNS:
        Success - drivenObj(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        objectBuffer =  returnDrivenAttribute (attribute)
        if objectBuffer:
                strippedObject = '.'.join(objectBuffer.split('.')[0:-1])
                return strippedObject
        else:
                return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectsAttributeTypes(obj):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Pass an object into it with user attributes and it will return a dictionary attribute's data types

        REQUIRES:
        obj(string) - obj with attrs

        RETURNS:
        attrDict(Dictionary) - dictionary in terms of {[attrName : type],[etc][etc]}
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        attrs =(mc.listAttr (obj))
        attrDict = {}
        if not attrs == None:   
                for attr in attrs:
                        try:
                                attrDict[attr] = (mc.getAttr((obj+'.'+attr),type=True))
                        except:
                                guiFactory.warning("%s didn't query" %attr)
                return attrDict
        else:
                print ('Sorry, no attributes found.')
                return False

def returnObjectsUserAttributeTypes(obj):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Pass an object into it with user attributes and it will return a dictionary attribute's data types

        REQUIRES:
        obj(string) - obj with attrs

        RETURNS:
        attrDict(Dictionary) - dictionary in terms of {[attrName : type],[etc][etc]}
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        attrs =(mc.listAttr (obj, userDefined=True))
        attrDict = {}
        if not attrs == None:   
                for attr in attrs:
                        attrDict[attr] = (mc.getAttr((obj+'.'+attr),type=True))
                return attrDict
        else:
                print ('Sorry, no user attributes found.')
                return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnUserAttributes(obj):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Returns user created attributes of an object

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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
                print ('Sorry, no message attributes found.')
                return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnMessageAttrsAsList(obj):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Pass an object into it with messages, it will return a nested list in terms of [[attrName, target],[etc][etc]]

        REQUIRES:
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
                print ('Sorry, no message attributes found.')
                return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnUserAttrsToDict(obj):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Pass an object into it with user attributes and it will return a dictionary of the data back

        REQUIRES:
        obj(string) - obj with attrs

        RETURNS:
        attrDict(Dictionary) - dictionary in terms of {[attrName : target],[etc][etc]}
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        attrDict = {}
        objAttributes =(mc.listAttr (obj, userDefined=True))
        attrTypes = returnObjectsUserAttributeTypes(obj)
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
                print ('Sorry, no attributes found.')
                return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnUserAttrsToList(obj):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Pass an object into it with user attributes and it will return a dictionary of the data back

        REQUIRES:
        obj(string) - obj with attrs

        RETURNS:
        attrsList(list) - nested list in terms of [[attrName : target],[etc][etc]]
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        attrsList = []
        objAttributes =(mc.listAttr (obj, userDefined=True))
        attrTypes = returnObjectsUserAttributeTypes(obj)
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
                print ('Sorry, no attributes found.')
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

        REQUIRES:
        obj(string) - object to add attributes to
        attrList(list) - list of attributes to add

        RETURNS:
        NA
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        mc.addAttr(obj, ln=name, at = 'enum',en = 'xyz:yzx:zxy:xzy:yxz:zyx')
        mc.setAttr((obj+'.'+name),e = True, keyable = True )
        return (obj+'.'+name)

def addAttributesToObj (obj, attributeTypesDict):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Takes an list of string variables to add to an object as string
        attributes. Skips it if it exists.

        REQUIRES:
        obj(string) - object to add attributes to
        attrList(list) - list of attributes to add

        RETURNS:
        NA
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        """sort the keys"""
        sortedAttributes = dictionary.returnDictionarySortedToList(attributeTypesDict,sortBy='values')

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
def addStringAttributeToObj (obj, attr):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Takes an list of string variables to add to an object as string
        attributes. Skips it if it exists.

        REQUIRES:
        obj(string) - object to add attributes to
        attrList(list) - list of attributes to add

        RETURNS:
        NA
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        attrCache = (obj+'.'+attr)
        if not mc.objExists (attrCache):
                return (mc.addAttr (obj, ln = attr,  dt = 'string'))
        else:
                print ('"' + attrCache + '" exists, moving on')


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addStringAttributesToObj (obj, attrList):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Takes an list of string variables to add to an object as string attributes. Skips it if it exists.
        Input -obj, attrList(list).

        REQUIRES:
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
                else:
                        print ('"' + attrCache + '" exists, moving on')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addFloatAttributeToObject (obj, attr, minValue = None, maxValue = None, default = None):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Adds a float attribute to an object

        REQUIRES:
        obj(string) - object to add attribute to
        attr(string) - attribute name to add
        minValue(int/float) - minimum value
        maxValue(int/float) - maximum value
        default(int/float) - default value

        RETURNS:
        Attribute full name (string) - ex obj.attribute
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        """ gotta be a betterway to flag this """
        attrCache = (obj+'.'+attr)
        if not mc.objExists (attrCache):
                if not minValue == None:
                        if not maxValue == None:           
                                mc.addAttr (obj, ln = attr,  at = 'float', min = minValue, max = maxValue, dv = default )
                                mc.setAttr (attrCache, edit=True, keyable = True)
                                return attrCache
                        else:
                                mc.addAttr (obj, ln = attr,  at = 'float', min = minValue, dv = default )
                                mc.setAttr (attrCache, edit=True, keyable = True)
                                return attrCache
                else:
                        if not maxValue == None:
                                mc.addAttr (obj, ln = attr,  at = 'float', max = maxValue, dv = default )
                                mc.setAttr (attrCache, edit=True, keyable = True)
                                return attrCache
                        else:
                                mc.addAttr (obj, ln = attr,  at = 'float', dv = default )
                                mc.setAttr (attrCache, edit=True, keyable = True)
                                return attrCache   
        else:
                print ('"' + attrCache + '" exists, moving on')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addEnumAttrToObj (obj,attrName,optionList=['off','on'], default=None):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Adds a enum attribute to an object

        REQUIRES:
        obj(string) - object to add attribute to
        attrName(list)
        optionList(list)
        default(int/float) - default value

        RETURNS:
        Attribute full name (string) - ex obj.attribute
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        attrCache = (obj+'.'+attrName)
        if not mc.objExists (attrCache):
                mc.addAttr(obj,ln = attrName, at = 'enum', en=('%s' %(':'.join(optionList))))
                mc.setAttr ((obj+'.'+attrName),e=True,keyable=True)

                return attrCache
        else:
                return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addFloatAttrsToObj (obj,attrList, minValue = None, maxValue=None, default=None):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Adds a float attribute to an object

        REQUIRES:
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
                attrCache = addFloatAttributeToObject (obj, attr, minValue, maxValue, default)
                attrsCache.append(attrCache)
        return attrsCache
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def addBoolAttrToObject(obj, attr):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Adds a section break for an attribute list

        REQUIRES:
        obj(string) - object to add attribute to
        attr(string) - name for the section break

        RETURNS:
        Nothing
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        attrCache = (obj+'.'+attr)
        if not mc.objExists (attrCache):
                mc.addAttr (obj, ln = attr,  at = 'bool')
                mc.setAttr (attrCache, edit = True, channelBox = True)
        else:
                print ('"' + attrCache + '" exists, moving on')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def addSectionBreakAttrToObj(obj, attr):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Adds a section break for an attribute list

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
        obj(string) - object to store
        storageObject(string) - object to store the info to
        messageName(string) - message name to store it as

        RETURNS:
        Nothing
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        attrCache = (storageObj+'.'+messageName)
        if  mc.objExists (attrCache):  
                print (attrCache+' already exists. Adding to existing message node.')
                breakConnection(attrCache)
                mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),force=True)
        else:
                mc.addAttr (storageObj, ln=messageName, at= 'message')
                mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def storeObjListNameToMessage (objList, storageObj):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Adds the obj names as  message attributes to the storage object

        REQUIRES:
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

        REQUIRES:
        obj(string) - obj with message attrs

        RETURNS:
        messageList - nested list in terms of [[attrName, target],[etc][etc]]
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        if mc.objExists(obj+'.'+attr) != False:
                messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
                if messageQuery == True:
                        return True
                else:
                        return False
        else:
                return False