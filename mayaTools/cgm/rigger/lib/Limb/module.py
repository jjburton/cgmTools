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


defaultSettings = {'partType':'none',
                   'stiffIndex':0,
                   'curveDegree':1,
                   'rollJoints':3,
                   'handles':3,
                   'bendy':True,
                   'stretchy':True,
                   'fk':True,
                   'ik':True}

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
        if not self.refState:
            if not self.verifyLimbModule():
                guiFactory.warning("'%s' failed to verify!"%self.ModuleNull.nameShort)
                return False
        else:
            guiFactory.report("'%s' Referenced. Cannot verify, initializing Limb module."%self.ModuleNull.nameShort)
            if not self.initializeLimbModule():
                guiFactory.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%self.ModuleNull.nameShort)
                return False
            
        guiFactory.report("'%s' checks out"%self.ModuleNull.nameShort)
        guiFactory.doPrintReportEnd()
            
    def verifyLimbModule(self):
        """
        Verifies the integrity of the Limb module. Repairing and restoring broken connections or deleted items.
        """        
        #Initialize all of our options
        for k in defaultSettings.keys():
            try:
                self.__dict__[k]
            except:
                self.__dict__[k] = defaultSettings[k]
            
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType','string',value= self.partType)
        
        if self.infoNulls['setupOptions']:
            self.SetupOptionsNull = ObjectFactory( self.infoNulls['setupOptions'].value )
            self.optionFK = AttrFactory(self.SetupOptionsNull,'fk','bool',initialValue= self.fk)
            self.optionIK = AttrFactory(self.SetupOptionsNull,'ik','bool',initialValue= self.ik)
            self.optionStretchy = AttrFactory(self.SetupOptionsNull,'stretchy','bool',initialValue= self.stretchy)
            self.optionBendy = AttrFactory(self.SetupOptionsNull,'bendy','bool',initialValue= self.bendy)
            
            self.optionHandles = AttrFactory(self.SetupOptionsNull,'handles','int',initialValue=self.handles)
            self.optionRollJoints = AttrFactory(self.SetupOptionsNull,'rollJoints','int',initialValue=self.rollJoints)
            self.optionStiffIndex= AttrFactory(self.SetupOptionsNull,'stiffIndex','int',initialValue=self.stiffIndex)
            self.optionCurveDegree= AttrFactory(self.SetupOptionsNull,'curveDegree','int',initialValue=self.curveDegree)
        else:
            guiFactory.warning("Setup options null is missing from '%s'. Rebuild"%self.ModuleNull.nameShort)
            return False
        if self.infoNulls['visibilityOptions']:
            self.VisibilityOptionsNull = ObjectFactory( self.infoNulls['visibilityOptions'].value )
            
            self.visOrientHelpers = AttrFactory(self.VisibilityOptionsNull,'visOrientHelpers','bool',initialValue=0)
            self.visControlHelpers = AttrFactory(self.VisibilityOptionsNull,'visControlHelpers','bool',initialValue=0)
        else:
            guiFactory.warning("Visibility options null is missing from '%s'. Rebuild"%self.ModuleNull.nameShort)
            return False
        
        return True
    
    def initializeLimbModule(self):
        """
        Verifies the integrity of the Limb module. Repairing and restoring broken connections or deleted items.
        """        
        #Initialize all of our options
        self.afModuleType = AttrFactory(self.ModuleNull,'moduleType')
        
        LimbSettingAttrs ={'fk':'bool',
                    'ik':'bool',
                    'stretchy':'bool',
                    'bendy':'bool',
                    'handles':'int',
                    'rollJoints':'int',
                    'stiffIndex':'int',
                    'curveDegree':'int'}
        
        if self.infoNulls['setupOptions']:
            self.SetupOptionsNull = ObjectFactory( self.infoNulls['setupOptions'].value )
            self.optionFK = AttrFactory(self.SetupOptionsNull,'fk')
            self.optionIK = AttrFactory(self.SetupOptionsNull,'ik')
            self.optionStretchy = AttrFactory(self.SetupOptionsNull,'stretchy')
            self.optionBendy = AttrFactory(self.SetupOptionsNull,'bendy')
            
            self.optionHandles = AttrFactory(self.SetupOptionsNull,'handles')
            self.optionRollJoints = AttrFactory(self.SetupOptionsNull,'rollJoints')
            self.optionStiffIndex= AttrFactory(self.SetupOptionsNull,'stiffIndex')
            self.optionCurveDegree= AttrFactory(self.SetupOptionsNull,'curveDegree')
            
        if self.infoNulls['visibilityOptions']:
            self.VisibilityOptionsNull = ObjectFactory( self.infoNulls['visibilityOptions'].value )
            self.visOrientHelpers = AttrFactory(self.VisibilityOptionsNull,'visOrientHelpers')
            self.visControlHelpers = AttrFactory(self.VisibilityOptionsNull,'visControlHelpers')
                    
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
        
        
        Limb.__init__(self,moduleName,moduleParent,position,direction,directionModifier,nameModifier,*a,**kw)
        
        