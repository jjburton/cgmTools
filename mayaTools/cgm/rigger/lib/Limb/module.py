"""
cgmLimb
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
import maya.cmds as mc
from cgm.lib.classes import NameFactory
from cgm.lib.classes.AttrFactory import *

from cgm.rigger.ModuleFactory import *


from cgm.lib import (search,
                     distance,
                     names,
                     attributes,
                     names,
                     rigging,
                     constraints,
                     curves,
                     dictionary,
                     settings,
                     lists,
                     modules,
                     position,
                     cgmMath,
                     controlBuilder)


import re
import copy

reload(search)
reload(distance)
reload(names)
reload(attributes)
reload(names)
reload(rigging)
reload(constraints)
reload(curves)
reload(dictionary)
reload(settings)
reload(lists)
reload(modules)
reload(cgmMath)
reload(controlBuilder)

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
namesDictionary = dictionary.initializeDictionary( settings.getNamesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())

""" 1 """
class Limb(ModuleFactory):
    """
    Limb class which inherits the ModuleFactory master class
    """
    def __init__(self,*a,**kw):
        
        guiFactory.doPrintReportStart()
        
        #Initialize the standard module
        ModuleFactory.__init__(self,*a,**kw)
        
        #Then check the subclass specific stuff
        if not self.verifyLimbModule():
            guiFactory.warning("'%s' failed to verify!"%self.moduleNull)
            
        guiFactory.report("'%s' checks out"%self.moduleNull)
        guiFactory.doPrintReportEnd()
            
    def verifyLimbModule(self):
        """
        Verifies the integrity of the Limb module. Repairing and restoring broken connections or deleted items.
        """        
        #Initialize all of our options
        self.aModuleType = AttrFactory(self.moduleNull,'moduleType','string',value = self.partType)
        
        if self.infoNulls['setupOptions']:
            null = self.infoNulls['setupOptions'].value
            self.aFK = AttrFactory(null,'fk','bool',initialValue=0)
            self.aIK = AttrFactory(null,'ik','bool',initialValue=0)
            self.aStretchy = AttrFactory(null,'stretchy','bool',initialValue=0)
            self.aBendy = AttrFactory(null,'bendy','bool',initialValue=0)
            
            self.aHandles = AttrFactory(null,'handles','int',initialValue=self.handles)
            self.aRollJoints = AttrFactory(null,'rollJoints','int',initialValue=self.rollJoints)
            self.aStiffIndex= AttrFactory(null,'stiffIndex','int',initialValue=self.stiffIndex)
            self.aCurveDegree= AttrFactory(null,'curveDegree','int',initialValue=self.curveDegree)
            
        if self.infoNulls['visibilityOptions']:
            null = self.infoNulls['visibilityOptions'].value
            
            self.aVisOrientHelpers = AttrFactory(null,'visOrientHelpers','bool',initialValue=0)
            self.aVisControlHelpers = AttrFactory(null,'visControlHelpers','bool',initialValue=0)
                    
        return True


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Define Subclasses
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
class Segment(Limb):
    def __init__(self, moduleName ='segment', moduleParent = False, handles = 3, position = False, direction = False, directionModifier = False, nameModifier = False,*a, **kw):
        self.partType = 'segment'
        self.stiffIndex = 0
        self.curveDegree = 1
        self.rollJoints = 3
        self.handles = handles
        
        
        Limb.__init__(self,moduleName,moduleParent,position,direction,directionModifier,nameModifier*a,**kw)
        
        