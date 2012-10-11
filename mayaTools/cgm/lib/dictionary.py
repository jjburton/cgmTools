#=================================================================================================================================================
#=================================================================================================================================================
#	dictionary - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for Dictionaries
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
from cgm.lib import settings
import operator
from operator import itemgetter
from itertools import groupby

namesDictionaryFile = settings.getNamesDictionaryFile()
typesDictionaryFile = settings.getTypesDictionaryFile()
settingsDictionaryFile = settings.getSettingsDictionaryFile()

setTypes = {'animation':'animSet',
            'layout':'layoutSet',
            'modeling':'modelingSet',
            'td':'tdSet',
            'fx':'fxSet',
            'lighting':'lightingSet'}

cgmNameTags = 'cgmName','cgmNameModifier','cgmPosition','cgmDirection','cgmDirectionModifier','cgmIterator','cgmType','cgmTypeModifier'
axisDirectionsByString = ['x+','y+','z+','x-','y-','z-']

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Common Dictionaries
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
"""
Orienation and Vectors
"""
axisDirectionsByString = ['x+','y+','z+','x-','y-','z-'] #Used for several menus and what not

stringToVectorDict = {'x+':[1,0,0],
                      'x-':[-1,0,0],
                      'y+':[0,1,0],
                      'y-':[0,-1,0],
                      'z+':[0,0,1],
                      'z-':[0,0,-1]}

vectorToStringDict = {'[1,0,0]':'x+',
                      '[-1,0,0]':'x-',
                      '[0,1,0]':'y+',
                      '[0,-1,0]':'y-',
                      '[0,0,1]':'z+',
                      '[0,0,-1]':'z-'}

def validateDirectionVector(direction):
    """ 
    Returns a valid direction vector
    
    Arguments:
    direction(string/list)        
    """
    if type(direction) is list:
        for option in stringToVectorDict.keys():
            if direction == stringToVectorDict[option]: 
                return stringToVectorDict[option]
    else:
        for option in stringToVectorDict.keys():
            if direction.lower() == option: 
                return stringToVectorDict[option]
    
    return False
    

def returnStringToVectors(direction):
    if direction in stringToVectorDict.keys():
        return stringToVectorDict.get(direction)
    else:
        return False


def returnVectorToString(vector):
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
standardColorDict = {'black':1,'grayDark':2,'grayLight':3,'redDark':4,
             'blueDark':5,'blueBright':6,'greenDark':7,'violetDark':8,
             'violetBright':9,'brownReg':10,'brownDark':11,
             'orangeDark':12,'redBright':13,'greenBright':14,'blueDull':15,
             'white':16,'yellowBright':17,'blueSky':18,'teal':19,
             'pink':20,'peach':21,'yellow':22,'greenBlue':23,'tan':24,
             'olive':25,'greenYellow':26,'greenBlue':27,'blueGray':28,
             'blueGrayDark':29,'purple':30,'purpleBrown':31}

 
stateColors = {'normal':[1,1,1],
               'ready':[ 0.166262 ,0.388495 , 0.022797],
               'keyed':[0.870588, 0.447059, 0.478431],
               'locked':[0.360784, 0.407843, 0.454902],
               'connected':[0.945098, 0.945098, 0.647059],
               'reserved':[0.411765 , 0.411765 , 0.411765],
               'semiLocked':[ 0.89, 0.89, 0.89],
               'help':[0.8, 0.8, 0.8],
               'warning':[0.837, 0.399528, 0.01674],
               'error':[1, 0.0470588, 0.0677366],
               'black':[0,0,0]}

guiDirectionColors = {'center':[0.971679, 1, 0],
                      'centerSub':[0.972, 1, 0.726],
                      'left':[0.305882 ,0.814528, 1],
                      'right':[0.976471 ,0.355012, 0.310173]}

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnColorIndex(color):
    colorIndexBuffer = standardColorDict.get(color)
    if colorIndexBuffer != None:
        return colorIndexBuffer
    else:
        return None
    
def returnStateColor(newState):
    if newState in stateColors.keys():
        return stateColors.get(newState)
    else:
        return False
    
def returnGuiDirectionColor(key):
    if key in guiDirectionColors.keys():
        return guiDirectionColors.get(key)
    else:
        return False
"""
Rotate Order
"""
rotateOrderDictionary = {'xyz':0,
                         'yzx':1,
                         'zxy':2,
                         'xzy':3,
                         'yxz':4,
                         'zyx':5}    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnRotateOrderIndex(ro):
    indexBuffer = rotateOrderDictionary.get(ro)
    if indexBuffer != None:
        return indexBuffer
    else:
        return None
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def initializeDictionary(file):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reads a text file in the form of key:value per line into an active dictionary
    
    ARGUMENTS:
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

def initializeDictionaryScott(file):
    with open(file) as f:
        dictionary = dict()
        for line in f: # this is more efficient because we are not dumping the whole file into a list
            key, sep, value = line.partition(':')
            if ',' in value:
                value = map(str.strip, value.split(','))
            else:
                dictionary[colonSplit[0]] = colonSplit[1]
                value = value.strip()
            
            dictionary[key.strip()] = value
    return dictionary

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDictionaryListToList(dictionaryFile,key):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reads all of the modules attached to a masterNull and orders them from
    the settings.conf
    
    ARGUMENTS:
    masterNull(string)
    
    RETURNS:
    orderedModules(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    dictFile = initializeDictionary(dictionaryFile)
    listBuffer = dictFile[key]
    return listBuffer.split(',')
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDictionarySortedToList (dictToSort,sortByValues=True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a sorted list from a dictionary
    
    ARGUMENTS:
    dict(dict) - in {'name':value} format
    sortByValues(bool) - default is to sort by values
    
    RETURNS:
    sortedList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """   
    return sorted(dictToSort.iteritems(), key=operator.itemgetter(sortByValues))    

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Direction stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        
directionsDict = {'left':['l','left','lft','lf'],
                  'right':['r','right','rght','rt']}    

def validateStringDirection(direction):
    """ 
    Returns direction an direction is valid or not
    
    Keyword arguments:
    attrType(string)        
    """          
    dType = False
    for option in directionsDict.keys():
        if direction.lower() in directionsDict.get(option): 
            dType = option
            break
        
    return dType