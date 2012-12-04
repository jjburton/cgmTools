#=========================================================================      
#Pupper requirements- We force the update on the Red9 internal registry  
# Puppet - network node
# >>
#=========================================================================         
from cgm.lib.Red9.core import Red9_Meta as r9Meta
reload(r9Meta)
from cgm.lib.Red9.core.Red9_Meta import *
r9Meta.registerMClassInheritanceMapping()    
#========================================================================

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.lib.classes import NameFactory
from cgm.lib.classes import AttrFactory
reload(AttrFactory)
from cgm.core.classes.AttrFactory import *

from cgm.core import cgmMeta
reload(cgmMeta)
from cgm.core.cgmMeta import *

import random
import re
import copy
########################################################################
class cgmPuppet(cgmMetaClass):
    """"""
    #----------------------------------------------------------------------
    def __init__(self,*args,**kws):
        """Constructor"""
        #>>>Keyword args
        name = kws.pop('name',False)
        #characterType = kws.pop('characterType','')
        #initializeOnly = kws.pop('initializeOnly',False)
        
        #Need a simple return of
        puppets = simplePuppetReturn()
        #If a node is provided, check if it's a cgmPuppet
        #If a name is provided, see if there's a puppet with that name, 
        #If nothing is provided, just make one
        if name:
            if puppets:
                for p in puppets:
                    if attributes.doGetAttr(p,'cgmName') == name:
                        log.info("Puppet tagged '%s' exists. Checking..."%name)
                        super(cgmPuppet, self).__init__(node = p,*args,**kws)
                        name = attributes.doGetAttr(p,'cgmName')
                        break
            else:
                super(cgmPuppet, self).__init__(*args,**kws)
        else:
            super(cgmPuppet, self).__init__(*args,**kws)
            if not attributes.doGetAttr(self.mNode,'cgmName'):
                randomOptions = ['ReallyNameMe','SolarSystem_isADumbName','David','Josh','Ryan','NameMe','Homer','Georgie','PleaseNameMe','NAMEThis','PleaseNameThisPuppet']
                buffer = random.choice(randomOptions)
                cnt = 0
                while mc.objExists(buffer) and cnt<10:
                    cnt +=1
                    buffer = random.choice(randomOptions)
                name = buffer                 
                               
        self.cgmName = name
        #self.verify()
        
    def __bindData__(self):
        #Default to creation of a var as an int value of 0
        ### input check   
        self.addAttr('cgmName','')
        self.addAttr('cgmType','puppetNetwork')
        self.addAttr('masterNull',type='messageSimple')        
        self.addAttr('puppetGroup',type='messageSimple')
        self.addAttr('modulesGroup',type='messageSimple')
        self.addAttr('noTransformGroup',type='messageSimple')
        self.addAttr('geoGroup',type='messageSimple')
        self.addAttr('info',type='messageSimple')
        
    #----------------------------------------------------------------------
    def verify(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """            
        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()
        
        masterNull = cgmMasterNull(puppet = self)
        self.doStore('masterNull',masterNull.mNode)
            
class cgmMasterNull(cgmObject):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, *args,**kws):
        """Constructor"""
        #>>>Keyword args
        puppet = kws.pop('puppet',False)
        super(cgmMasterNull, self).__init__(*args,**kws)
        
        if puppet:
            self.doStore('cgmName',puppet.cgmName)
            
        self.verify()
        

    def verify(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """ 
        AttrFactory(self,'cgmName',initialValue = '')
        AttrFactory(self,'cgmType',initialValue = 'ignore')
        AttrFactory(self,'cgmModuleType',value = 'master')   
        
        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()
        
        
def simplePuppetReturn():
    catch = mc.ls(type='network')
    returnList = []
    if catch:
        for o in catch:
            if attributes.doGetAttr(o,'mClass') == 'cgmPuppet':
                returnList.append(o)
    return returnList
          