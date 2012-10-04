#=================================================================================================================================================
#=================================================================================================================================================
#	lists - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for list stuff
# 
# ARGUMENTS:
# 	rigging
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#=================================================================================================================================================

import maya.cmds as mc


def returnListChunks(l, n):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    SOURCE:
    http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python/312644#312644
    
    DESCRIPTION:
    Spits a list into chunks
    
    ARGUMENTS:
    l(list) ex [1,2,3,4,5,6]
    n(int) - to split by
    
    RETURNS:
    splitList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """       
    return [l[i:i+n] for i in range(0, len(l), n)]

def reorderListInPlace(l, subL, direction = 0):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    SOURCE:
    Got the original idea from Hamish McKenzie for reordering attributes. Reworked a little
    
    DESCRIPTION:
    Returns a reordered list from a sublist of options and a direction
    
    ARGUMENTS:
    l(list) ex [1,2,3,4,5,6]
    subL(list) must be list within list
    direction(int) - 0 for down, 1 for up
    
    RETURNS:
    newList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    for i in subL:
        returnList = l
        if i in returnList:
            idx = returnList.index(i)
            if not direction and idx != 0:
                if idx-1 in range(len(returnList)):
                    if returnList[idx-1] not in subL:
                        returnList.remove(i)
                        returnList.insert(idx-1,i)
            elif direction and idx != len(returnList):
                if idx+1 in range(len(returnList)):
                    if returnList[idx+1] not in subL:                
                        returnList.remove(i)
                        returnList.insert(idx+1,i)
            else:
                print ("List is already in order. No change.")
        else:
           print("'%s' not in the target list. Try again..."%i)
    return returnList 


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Simplifying
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnSplitList(listToSplit, mode=0):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a list sundered in TWO
    
    ARGUMENTS:
    listToSplit(list) ex [1,2,3,4,5,6]
    mode(int) - OPTIONAL - 0 - split is default and favors the front 
                               [1,2,3],[3,4,5,6]
                           1 - favors the rear
                               [1,2,3,4],[4,5,6]
    
    RETURNS:
    splitList
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # if even...
    if len(listToSplit)%2==0:
        if mode == 0:
            halfA = listToSplit[:len(listToSplit)/2]
            halfB = listToSplit[len(listToSplit)/2-1:]

        else: 
            if len(listToSplit)%2==0:
                halfA = listToSplit[:len(listToSplit)/2 + 1]
                halfB = listToSplit[len(listToSplit)/2:]
    # if odd...
    else:
        halfA = listToSplit[:len(listToSplit)/2+ 1]
        halfB = listToSplit[len(listToSplit)/2:]
    splitList=[]
    splitList.append(halfA)
    splitList.append(halfB)
    return splitList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnFirstMidLastList(list):        
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the first middle and last items of a list of items for constraint purposes
    
    ARGUMENTS:
    list(list)
    
    RETURNS:
    bufferList(list) 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = []
    bufferList.append(list[0])
    bufferList.append(list[int(round((len(list))*1/2))])
    bufferList.append(list[-1])
    return bufferList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def returnFactoredList(listToFactor, factor):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes a list and factors it out for constraining purposes
    ex - returnFactoredList(testList, 3)
    
    ARGUMENTS:
    listToFactor(list) - ex testList = [0,1,2,3,4,5,6,7]
    factor(int)
    
    RETURNS:
    culledList(list) - ex - [[[0, 1, 2], [2, 3, 4]], [4, 5, 6, 7]]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    loopCnt = (len(listToFactor)/(factor))
    culledList = []           
    keepSplittingList =[]
    if len(listToFactor) > (factor +1):
        culledList.append(returnFirstMidLastList(listToFactor))
        bufferList = returnSplitList(listToFactor, mode=1)
        for list in bufferList:
            splitBuffer = []
            if len(list) > (factor + 1):
                culledList.append(returnFirstMidLastList(list))
                splitBuffer = (returnSplitList(list, mode=1))
                for sublist in splitBuffer:
                    keepSplittingList.append(sublist)
            else:
                culledList.append(list)                       
    
    else:
        return culledList
    if len(keepSplittingList) > 0:
        while loopCnt > 0:
            for list in keepSplittingList:
                print 'keep splitting....'
                print list
                splitBuffer = []
                if len(list) > (factor + 1):
                    culledList.append(returnFirstMidLastList(list))
                    splitBuffer = (returnSplitList(list, mode=1))
                    for subList in splitBuffer:
                        keepSplittingList.append(subList)
                else:
                    keepSplittingList.remove(list)
                    culledList.append(list)
            loopCnt -=1
    
    return culledList
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def parseListToPairs(dataList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
 	Takes a datalist and parses it to pairs. For example [dog,cat,pig,monkey] would be
 	[[dog,cat],[cat,pig],[pig,monkey]]
    
    ARGUMENTS:
    dataList(list)
    
    RETURNS:
    nestedPairList(List)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    """    
    nestedPairList = []
    dataAListIter = iter(dataList)
    cnt = 1
    for itemA in dataList[:-1]:
        itemB = dataList[cnt]
        nestedPairList.append([itemA, itemB])
        cnt +=1

    return nestedPairList
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Duplicates/Matching
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def returnPosListNoDuplicates(posSearchList,decimalPlaces=4):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Removes duplicates from a list of positions with a variance ot decimal places to check
    
    ARGUMENTS:
    posSearchList(list)
    decimalPlaces(int) - the number of decimal places to check
    
    RETURNS:
    newList(list) - list with no duplicates
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    decimalFormat = ('%s%i%s' % ("%.",decimalPlaces,"f"))
    "rebuild the list with the new formatting"
    formattedList = []
    for pos in posSearchList:
        posBuffer = []
        for n in pos:
            buffer = float(decimalFormat % (n))
            posBuffer.append(buffer)
        formattedList.append(posBuffer)
    """search"""    
    matchList = []
    returnList = []
    cnt = 0
    for pos in formattedList:
        if pos not in matchList:
            matchList.append(pos)
            returnList.append(posSearchList[cnt])
        cnt +=1
    return returnList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnMatchList(list1,list2):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a list of matches
    
    ARGUMENTS:
    searchList(list)
    
    RETURNS:
    newList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    matchList=[]
    if list1 and list2:
        for item in list1:
            if item in list2:
                matchList.append(item)
    if matchList:
        return matchList
    else:
        return []
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnMissingList(baseList,searchList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a list of items not found
    
    ARGUMENTS:
    baseList(list)
    searchList(list)
    
    RETURNS:
    missingList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    missingList=[]
    if baseList and searchList:
        for item in searchList:
            if item not in baseList:
                missingList.append(item)
    return missingList
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnListNoDuplicates(searchList):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Removes duplicates from a list
    
    ARGUMENTS:
    searchList(list)
    
    RETURNS:
    newList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    newList = []
    for item in searchList:
        if item not in newList:
            newList.append(item)
    return newList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def removeMatchedIndexEntries(searchList,searchTerm):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Removes duplicates from a list
    
    ARGUMENTS:
    searchList(list) - should be a nested list
    searchTerm(string) - what you wanna look for
    
    RETURNS:
    newList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    newList = []
    for term in searchList:
        if searchTerm not in term[0]:
            newList.append(term)
    return newList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def returnMatchedIndexEntries(searchList,searchTerm):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a list of 
    
    ARGUMENTS:
    searchList(list) - should be a nested list
    searchTerm(string) - what you wanna look for
    
    RETURNS:
    newList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    newList = []
    for term in searchList:
        if searchTerm in term[0]:
            newList.append(term)
    return newList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def returnMatchedStrippedEndList(searchList,searchTerms = ['left','right']):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Look through a list for match terms like ['left','right'] and returns a
    nested pairs list
    
    ARGUMENTS:
    searchList(list) - should be a nested list
    searchTerm(string) - what you wanna look for
    
    RETURNS:
    newList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    newList = []
    stripList = []
    matchList = []
    for term in searchList:
        currentIndex = searchList.index(term)
        set = []
        if searchTerms[0] in term:
            splitBuffer = term.split('_')
            nameBuffer = splitBuffer[:-1]
            baseName = '_'.join(nameBuffer)
            for searchTerm in searchList:
                if searchTerm != searchList[currentIndex]:
                    if searchTerms[1] in searchTerm:
                        newSplitBuffer = searchTerm.split('_')
                        newNameBuffer = newSplitBuffer[:-1]
                        newSearchTerm = '_'.join(newNameBuffer)
                        if newSearchTerm == baseName :
                            set = [term,searchTerm]
                            newList.append(set)
    return newList

def returnReplacedNameList(searchList,replaceWith = {'left':'right'}):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Look through a list for match terms like ['left','right'] and returns a
    nested pairs list
    
    ARGUMENTS:
    searchList(list) - should be a nested list
    searchTerm(string) - what you wanna look for
    
    RETURNS:
    newList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    newList = []
    for i,term in enumerate(searchList):
        for q in replaceWith.keys():
            if q in term:
                newList.append(term.replace(q,replaceWith[q]))
    return newList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# CV Lists
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
def cvListSimplifier(listToSimplify,mode):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
 	Simplifies a cv list. In a semi intelligent manner
    
    ARGUMENTS:
    listToSimplify(list) - list or nested list of cv stuff
    mode -  0 - mid only
            1 - ends only
            2 - mid and ends only
            3 - odds only
            4 - evens only
            5 - all exceipt start and end anchors
            6 - all
    
    RETURNS:
    newList(List)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    """
    culledList = []
    listLength = len(listToSimplify)
    # middle only mode
    if mode == 0:
        culledList.append(listToSimplify[int(round(listLength*1/2))])
    # ends only mode
    elif mode == 1:
        culledList.append(listToSimplify[0])
        culledList.append(listToSimplify[-1])
    # ends and mid mode
    elif mode == 2:
        culledList.append(listToSimplify[0])
        culledList.append(listToSimplify[int(round(listLength*1/2))])
        culledList.append(listToSimplify[-1])
    # odds mode
    elif mode == 3:
        #first pulling out the extra cv's on the ends rows [1] and [-2]
        tmpList = []
        tmpList.append(listToSimplify[0])
        midBuffer = listToSimplify[2:-3]
        for item in midBuffer:
            tmpList.append(item)
        tmpList.append(listToSimplify[-1])
        # now let's pick our stuff
        cnt = 1
        # checks if we have an even number or not. If it is...
        if len(tmpList)%2==0:
            for n in range (int(round(len(tmpList)*1/2))-1):
                culledList.append (tmpList[cnt])
                cnt+=2
            culledList.append (listToSimplify[-3])
        # if it's not...
        else:
            for n in range (int(round(len(tmpList)*1/2))):
                culledList.append (tmpList[cnt])
                cnt+=2
            culledList.append (tmpList[-1])
    # evens mode
    elif mode == 4:
        #first pulling out the extra cv's on the ends rows [1] and [-2]
        tmpList = []
        tmpList.append(listToSimplify[0])
        midBuffer = listToSimplify[2:-3]
        for item in midBuffer:
            tmpList.append(item)
        tmpList.append(listToSimplify[-1])
        cnt = 0
        # checks if we have an even number or not. If it is...
        if len(tmpList)%2==0:
            for n in range (int(round(len(tmpList)*1/2))):
                culledList.append (tmpList[cnt])
                cnt+=2
            culledList.append (tmpList[-1])
        # if it's not...
        else:
            for n in range (int(round(len(tmpList)*1/2))):
                culledList.append (tmpList[cnt])
                cnt+=2
            culledList.append (listToSimplify[-3])
    elif mode == 5:
        culledList.append(listToSimplify[0])
        midBuffer = listToSimplify[2:-2]
        for item in midBuffer:
            culledList.append(item)
        culledList.append(listToSimplify[-1])
    elif mode == 6:
        culledList = listToSimplify
    return culledList

