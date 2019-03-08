"""
------------------------------------------
list_utils: cgm.core.lib.list_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
#from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================



#>>> Utilities
#===================================================================
def get_noDuplicates(l):
    """
    Get a list with no duplicates
    """    
    _l = []
    for v in l:
        if v not in _l:
            _l.append(v)
    return _l

def get_chunks(l, n):
    """
    Get chunks of the list
        
    :parameters:
        l(list) | list of things to chunkify
        n(int) | number of chunks  

    :returns
        List of chunks(list)
    
    SOURCE:
    http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python/312644#312644
    """       
    return [l[i:i+n] for i in range(0, len(l), n)]

def get_listPairs(dataList):
    """
    DESCRIPTION:
    Takes a datalist and parses it to pairs. For example [dog,cat,pig,monkey] would be
    [[dog,cat],[cat,pig],[pig,monkey]]

    ARGUMENTS:
    dataList(list)

    RETURNS:
    nestedPairList(List)
    """    
    nestedPairList = []
    dataAListIter = iter(dataList)
    cnt = 1
    for itemA in dataList[:-1]:
        itemB = dataList[cnt]
        nestedPairList.append([itemA, itemB])
        cnt +=1

    return nestedPairList
