import maya.cmds as mc

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.lib import (search,attributes)
from cgm.lib.classes import NameFactory

#Shared Settings
#========================= 
geoTypes = 'nurbsSurface','mesh','poly','subdiv'

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Puppet Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
@r9General.Timer   
def simplePuppetReturn():
    catch = mc.ls(type='network')
    returnList = []
    if catch:
        for o in catch:
            if attributes.doGetAttr(o,'mClass') == 'cgmPuppet':
                returnList.append(o)
    return returnList


@r9General.Timer   
def getGeo(self):
    """
    Returns geo in a puppets geo folder, ALL geo to be used by a puppet should be in there
    """    
    geo = []
    
    for o in self.i_geoGroup.getChildren():
        if search.returnObjectType(o) in geoTypes:
            buff = mc.ls(o,long=True)
            geo.append(buff[0])
    return geo


