#=================================================================================================================================================
#=================================================================================================================================================
#	dictionary - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for Dictionaries
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
from cgm.lib import settings

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Common Dictionaries
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
"""
Orienation and Vectors
"""
def returnStringToVectors(direction):
    vectorToStringDict = {'x+':[1,0,0],'x-':[-1,0,0],'y+':[0,1,0],'y-':[0,-1,0],'z+':[0,0,1],'z-':[0,0,-1]}
    if direction in vectorToStringDict.keys():
        return vectorToStringDict.get(direction)
    else:
        return False



def returnVectorToString(vector):
    vectorToStringDict = {'[1,0,0]':'x+','[-1,0,0]':'x-','[0,1,0]':'y+','[0,-1,0]':'y-','[0,0,1]':'z+','[0,0,-1]':'z-'}
    joinBuffer = ','.join(map(str,vector))
    buffer =   ('%s%s%s' % ("[",joinBuffer,"]"))
    stringBuffer= vectorToStringDict.get(buffer)

    if stringBuffer != None:
        return stringBuffer
    else:
        return None

"""
Colors
"""    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnColorIndex(color):
    colorDict = {'black':1,'grayDark':2,'grayLight':3,'redDark':4,'blueDark':5,'blueBright':6,'greenDark':7,'violetDark':8,'violetBright':9,'brownReg':10,'brownDark':11,'orangeDark':12,'redBright':13,'greenBright':14,'blueDull':15,'white':16,'yellowBright':17,'blueSky':18,'teal':19,'pink':20,'peach':21,'yellow':22,'greenBlue':23,'tan':24,'olive':25,'greenYellow':26,'greenBlue':27,'blueGray':28,'blueGrayDark':29,'purple':30,'purpleBrown':31}
    colorIndexBuffer = colorDict.get(color)
    if colorIndexBuffer != None:
        return colorIndexBuffer
    else:
        return None
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def returnColorDict():
    colorDict = {'black':1,'grayDark':2,'grayLight':3,'redDark':4,'blueDark':5,'blueBright':6,'greenDark':7,'violetDark':8,'violetBright':9,'brownReg':10,'brownDark':11,'orangeDark':12,'redBright':13,'greenBright':14,'blueDull':15,'white':16,'yellowBright':17,'blueSky':18,'teal':19,'pink':20,'peach':21,'yellow':22,'greenBlue':23,'tan':24,'olive':25,'greenYellow':26,'greenBlue':27,'blueGray':28,'blueGrayDark':29,'purple':30,'purpleBrown':31}
    return colorDict


def returnStateColor(newState):
    stateColors = {'normal':[1,1,1],
                   'keyed':[0.870588, 0.447059, 0.478431],
                   'locked':[0.360784, 0.407843, 0.454902],
                   'connected':[0.945098, 0.945098, 0.647059],
                   'reserved':[0.411765 , 0.411765 , 0.411765],
                   'semiLocked':[ 0.89, 0.89, 0.89],
                   'warning':[0.837, 0.399528, 0.01674],
                   'error':[1, 0.0470588, 0.0677366]}
    if newState in stateColors.keys():
        return stateColors.get(newState)
    else:
        return False
"""
Rotate Order
"""
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnRotateOrderIndex(ro):
    rotateOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5}    
    indexBuffer = rotateOrderDictionary.get(ro)
    if indexBuffer != None:
        return indexBuffer
    else:
        return None
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnRotateOrderDict():    
    rotateOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5}    
    return rotateOrderDictionary
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def initializeDictionary(file):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reads a text file in the form of key:value per line into an active dictionary
    
    REQUIRES:
    file(string) - Path and/or file
    
    RETURNS:
    Dictionary(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    f=open(file)
    readToLines = f.readlines()
    returnList = []
    dictionary = {}
    for line in readToLines:
        if line.find(':') !=-1:
            cleanName = line.rstrip()
            colonSplit = cleanName.split(':')
            if line.find(',') !=-1:
                sepNames = colonSplit[1]
                dictionary[colonSplit[0]] = sepNames
            else:
                dictionary[colonSplit[0]] = colonSplit[1]
    return dictionary

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDictionaryListToList(dictionaryFile,key):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reads all of the modules attached to a masterNull and orders them from
    the settings.conf
    
    REQUIRES:
    masterNull(string)
    
    RETURNS:
    orderedModules(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    dict = initializeDictionary(dictionaryFile)
    listBuffer = dict.get(key)
    return listBuffer.split(',')
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDictionarySortedToList (dict,sortBy='values'):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a sorted list from a dictionary
    
    REQUIRES:
    dict(dict) - in {'name':vaue} format
    sortBy(string) - default is to sort by values, you can tell it to set by keys with
                     any other value
    
    RETURNS:
    sortedList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    dictionaryList = []
    
    """ set our sort by variable """
    if sortBy == 'values':
        sorter = 1
    else:
        sorter = 0
    
    """ get list form """
    for key in dict:
        buffer = []
        buffer.append(key)
        buffer.append(dict.get(key))
        dictionaryList.append(buffer)
    
    """ sort it """
    newList = []
    from operator import itemgetter
    dictionaryList.sort(key=itemgetter(sorter))
    from itertools import groupby
    y = groupby(dictionaryList, itemgetter(sorter))
    
    for set, items in groupby(dictionaryList, itemgetter(sorter)):
        for i in items:
            newList.append(i)
    return newList
        
    

