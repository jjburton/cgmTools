#=================================================================================================================================================
#=================================================================================================================================================
#	names - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with names, renaming and whatnot
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
# FUNCTION KEY:
#   1) ????
#   2) ????
#   3) ????
#   
#=================================================================================================================================================

import maya.cmds as mc

# ====================================================================================================================
# FUNCTION - 1
#
# SIGNATURE:
#	stripSuffix (obj)
#
# DESCRIPTION:
#   Strips the suffix if it has one
# 
# ARGUMENTS:
# 	obj - object
#
# RETURNS:
#	Stripped name
#
# ====================================================================================================================
def initializeDictionary(file):
    """ returns a name dictionary based on a config file where the items to be input
    In a format of "key1:item1" per line"""
    f=open(file)
    readToLines = f.readlines()
    returnList = []
    nameDictionary = {}
    #gather the 
    for line in readToLines:
        if line.find(':') !=-1:
            cleanName = line.rstrip()
            colonSplit = cleanName.split(':')
            if line.find(',') !=-1:
                sepNames = colonSplit[1]
                nameDictionary[colonSplit[0]] = sepNames
            else:
                nameDictionary[colonSplit[0]] = colonSplit[1]
    return nameDictionary
# ====================================================================================================================
# FUNCTION - 2
#
# SIGNATURE:
#	returnShortName(longName)
#
# DESCRIPTION:
#   Returns a short name for an input long one
# 
# ARGUMENTS:
# 	longName
#
# RETURNS:
#	[True/False,shortName/errorMessage]
#
# ====================================================================================================================
def returnShortName(longName):
    returnedDictionary = initializeDictionary('C:\Users\Josh\Documents\maya\python/namePrefs.conf')
    nameDictionary = returnedDictionary
    returnList = []
    condition = False
    match = nameDictionary.get(longName)
    if match > 1:
        returnList.append (True)
        returnList.append (match)        
    else:
        returnList.append (False)
        returnList.append ('%s%s%s' %('No match for >>',objectType,'<<, add it to the dictionary or check your spelling/case'))
    return returnList

# ====================================================================================================================
# FUNCTION - 3
#
# SIGNATURE:
#	stripSuffix (obj)
#
# DESCRIPTION:
#   Strips the suffix if it has one
# 
# ARGUMENTS:
# 	obj - object
#
# RETURNS:
#	Stripped name
#
# ====================================================================================================================

def stripSuffixObj (obj):
    """ Strips the suffix if it has one """
    stripped = '_'.join(obj.split('_')[0:-1])
    if not stripped:
        return obj
    return stripped

# ====================================================================================================================
# FUNCTION - 4
#
# SIGNATURE:
#	stripSuffixList (objList)
#
# DESCRIPTION:
#   Strips the suffix of an list of objects
# 
# ARGUMENTS:
# 	objList - list of objects to strip
#
# RETURNS:
#	List of the stripped names
#
# ====================================================================================================================

def stripSuffixList (objList):
    """strips the suffix off an list of objects and returns the new names in an list (suffix being understood as whatever is after the LAST "_" in a name"""
    coreNameList = []
    for name in objList:
        buffer = stripSuffixObj (name)
        coreNameList.append (buffer)
    return coreNameList

def addPrefixObj (prefix,obj):
    """ adds the prefix to the object name """
    newName = (prefix+'_'+obj)
    mc.rename (obj, newName)
    return newName

def addPrefixList (prefix,objList):
    """strips the suffix off an list of objects and returns the new names in an list (suffix being understood as whatever is after the LAST "_" in a name"""
    newNameList = []
    for name in objList:
        buffer = addPrefixObj (prefix,name)
        newNameList.append (buffer)
    return newNameList
    
def addSuffixObj (suffix,obj):
    """ adds the suffix to the object name """
    newName = (obj+'_'+suffix)
    mc.rename (obj, newName)
    return newName
    
def addSuffixList (suffix,objList):
    """adds a suffix to an list of objects and returns the new names in an list (suffix being understood as whatever is after the LAST "_" in a name"""
    newNameList = []
    for name in objList:
        buffer = addSuffixObj (suffix,name)
        newNameList.append (buffer)
    return newNameList
# ====================================================================================================================
# FUNCTION - 3
#
# SIGNATURE:
#	renameJointChainList (jointList, startJointName, interiorJointRootName)
#
# DESCRIPTION:
#   Renames a joint chain procedurally 
# 
# ARGUMENTS:
# 	jointList - list of joints to be renamed (should be a hierarchy)
#   startJointName - what you want the root of the chain to be called (ie. 'pelvis' or 'spine_root')
#   interiorJointRootName = what you want the iterative name to be (ie. 'spine' for 'spine_01', 'spine_02', etc)
#
# RETURNS:
#	List of the new joints
#
# ====================================================================================================================

def renameJointChainList (jointList, startJointName, interiorJointRootName):
    """ Renames a joint chain procedurally """
    newJointList = []
    jntBuffer = mc.rename (jointList[0],startJointName)
    newJointList.append (jntBuffer)
    cnt = 1
    for jnt in jointList[1:-1]:
        jntBuffer = mc.rename (jnt,('%s%s%02i' % (interiorJointRootName,'_',cnt)))
        newJointList.append (jntBuffer)
        cnt += 1
    jntBuffer = mc.rename (jointList[-1], (interiorJointRootName+'_end'))
    newJointList.append (jntBuffer)
    return newJointList

# ====================================================================================================================
# FUNCTION - 4
#
# SIGNATURE:
#	returnDistanceBetweenPoints (point1, point2)
#
# DESCRIPTION:
#   Get's the distance bewteen two points
# 
# ARGUMENTS:
# 	point1 - [x,x,x]
# 	point1 - [x,x,x]
#
# RETURNS:
#	distance
#
# ====================================================================================================================

def renameObjectListFromList (objList,nameList):
    """ renames a list of objects with a list of names, returns the new list"""
    cnt = 0
    if not (len(objList)) == (len(nameList)):
        print ('You need more names. Lists must be equal length')
        return False
    else:
        for obj in objList:
            mc.rename (obj,nameList[cnt])
            cnt += 1
        return nameList
        

