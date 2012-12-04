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
        name = kws.pop('name','')
        #>>>Keyword args
        characterType = kws.pop('characterType','')
        initializeOnly = kws.pop('initializeOnly',False)
                
        if mc.objExists(name):
            cgmMetaClass.__init__(self,node=characterName)#initialize with the name and do a fast check            
            if self.cgmModuleType == 'master':
                log.info("'%s' exists. Checking..."%name)
            else:
                log.error("'%s' isn't a puppet module. Can't initialize"%name)
        else:
            cgmMetaClass.__init__(self) 
            if name == '':
                randomOptions = ['ReallyNameMe','SolarSystem_isADumbName','David','Josh','Ryan','NameMe','Homer','Georgie','PleaseNameMe','NAMEThis','PleaseNameThisPuppet']
                buffer = random.choice(randomOptions)
                cnt = 0
                while mc.objExists(buffer) and cnt<10:
                    cnt +=1
                    buffer = random.choice(randomOptions)
                name = buffer  
            
        self.cgmName = name   
        
    def __bindData__(self):
        #Default to creation of a var as an int value of 0
        ### input check   
        self.addAttr('cgmName','')
        self.addAttr('cgmType','puppetNetwork')
        self.addAttr('puppetGroup',type='messageSimple')
        self.addAttr('modulesGroup',type='messageSimple')
        self.addAttr('noTransformGroup',type='messageSimple')
        self.addAttr('geoGroup',type='messageSimple')
        self.addAttr('info',type='messageSimple')
        
        
    #----------------------------------------------------------------------
    def verify(self):
        """"""
        """ 
        Verifies the various components a masterNull for a character/asset. If a piece is missing it replaces it.
        
        RETURNS:
        success(bool)
        """            
        #Puppet null
        try:
            if not mc.objExists(self.nameBase):
                buffer = mc.group(empty=True)
                self.PuppetNull = ObjectFactory(buffer)
            else:
                self.PuppetNull = ObjectFactory(self.nameBase)
            
            self.PuppetNull.store('cgmName',self.nameBase,True)   
            self.PuppetNull.store('cgmType','ignore')
            self.PuppetNull.store('cgmModuleType','master')
                 
            if self.PuppetNull.nameShort != self.nameBase:
                self.PuppetNull.doName(False)
            
            attributes.doSetLockHideKeyableAttr(self.PuppetNull.nameShort,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        except:
            guiFactory.warning("Puppet null failed!")
            
        #Checks our modules container null
        created = False
        #Initialize message attr
        self.msgModulesGroup = AttrFactory(self.PuppetNull,'modulesGroup','message')
        if not self.msgModulesGroup.get():
            self.ModulesGroup = ObjectFactory(mc.group(empty=True))            
            self.msgModulesGroup.doStore(self.ModulesGroup.nameShort)
            created = True
        else:
            self.ModulesGroup = ObjectFactory(self.msgModulesGroup.get())
            
        self.ModulesGroup.store('cgmName','modules')   
        self.ModulesGroup.store('cgmType','group')
        
        self.ModulesGroup.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.ModulesGroup.doName(False)
            
        self.msgModulesGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.ModulesGroup.nameShort)

            
        #Checks our noTransform container null
        created = False        
        self.msgNoTransformGroup = AttrFactory(self.PuppetNull,'noTransformGroup','message')
        if not self.msgNoTransformGroup.get():
            self.NoTransformGroup = ObjectFactory(mc.group(empty=True))
            self.msgNoTransformGroup.doStore(self.NoTransformGroup.nameShort)
            created = True
        else:
            self.NoTransformGroup = ObjectFactory(self.msgNoTransformGroup.get())
            
        self.NoTransformGroup.store('cgmName','noTransform')   
        self.NoTransformGroup.store('cgmType','group')
        
        self.NoTransformGroup.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.NoTransformGroup.doName(False)
            
        self.msgNoTransformGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.NoTransformGroup.nameShort)
         
            
        #Checks our geo container null
        created = False        
        self.msgGeoGroup = AttrFactory(self.PuppetNull,'geoGroup','message')
        if not self.msgGeoGroup.get():
            self.GeoGroup = ObjectFactory(mc.group(empty=True))
            self.msgGeoGroup.doStore(self.GeoGroup.nameShort)            
            created = True
        else:
            self.GeoGroup = ObjectFactory(self.msgGeoGroup.get())
            
        self.GeoGroup.store('cgmName','geo')   
        self.GeoGroup.store('cgmType','group')
        
        self.GeoGroup.doParent(self.msgNoTransformGroup.get())
        
        if created:
            self.GeoGroup.doName(False)
            
        self.msgGeoGroup.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.GeoGroup.nameShort)
        
        #Checks master info null
        created = False        
        self.msgPuppetInfo = AttrFactory(self.PuppetNull,'info','message')
        if not self.msgPuppetInfo.get():
            self.PuppetInfoNull = ObjectFactory(mc.group(empty=True))
            self.msgPuppetInfo.doStore(self.PuppetInfoNull.nameShort)               
            created = True
        else:
            self.PuppetInfoNull = ObjectFactory(self.msgPuppetInfo.get())
            
            
        self.PuppetInfoNull.store('cgmName','master')   
        self.PuppetInfoNull.store('cgmType','info')
        
        self.PuppetInfoNull.doParent(self.PuppetNull.nameShort)
        
        if created:
            self.PuppetInfoNull.doName(False)
            
        self.msgPuppetInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.PuppetInfoNull.nameShort)
        
            
        #Checks modules info null
        created = False        
        self.msgModuleInfo = AttrFactory(self.msgPuppetInfo.get(),'modules','message')
        if not self.msgModuleInfo.get():
            self.ModuleInfoNull = ObjectFactory(mc.group(empty=True))
            self.msgModuleInfo.doStore(self.ModuleInfoNull.nameShort)     
            created = True
        else:
            self.ModuleInfoNull = ObjectFactory(self.msgModuleInfo.get())
            
        self.ModuleInfoNull.store('cgmName','modules')   
        self.ModuleInfoNull.store('cgmType','info')
        
        self.ModuleInfoNull.doParent(self.PuppetInfoNull.nameShort)
        
        if created:
            self.ModuleInfoNull.doName(False)
            
        self.msgModuleInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.ModuleInfoNull.nameShort)
        
        #Initialize our modules null as a buffer
        self.ModulesBuffer = BufferFactory(self.ModuleInfoNull.nameShort)
        
        #Checks geo info null
        created = False        
        self.msgGeoInfo = AttrFactory(self.msgPuppetInfo.get(),'geo','message')
        if not self.msgGeoInfo.get():
            self.GeoInfoNull = ObjectFactory(mc.group(empty=True))
            self.msgGeoInfo.doStore(self.GeoInfoNull.nameShort)              
            created = True
        else:
            self.GeoInfoNull = ObjectFactory(self.msgGeoInfo.get())
            
        self.GeoInfoNull.store('cgmName','geo')   
        self.GeoInfoNull.store('cgmType','info')
        
        self.GeoInfoNull.doParent(self.msgPuppetInfo.get())
        
        if created:
            self.GeoInfoNull.doName(False)
            
        self.msgGeoInfo.updateData()   
            
        attributes.doSetLockHideKeyableAttr(self.GeoInfoNull.nameShort) 
        
        #Checks settings info null
        created = False        
        self.msgSettingsInfo = AttrFactory(self.msgPuppetInfo.get(),'settings','message')
        if not self.msgSettingsInfo.get():
            self.SettingsInfoNull = ObjectFactory(mc.group(empty=True))
            self.msgSettingsInfo.doStore(self.SettingsInfoNull.nameShort)   
            created = True
        else:
            self.SettingsInfoNull = ObjectFactory(self.msgSettingsInfo.get())
            
        self.SettingsInfoNull.store('cgmName','settings')   
        self.SettingsInfoNull.store('cgmType','info')
        defaultFont = modules.returnSettingsData('defaultTextFont')
        self.SettingsInfoNull.store('font',defaultFont)
        
        self.SettingsInfoNull.doParent(self.msgPuppetInfo.get())
        
        if created:
            self.SettingsInfoNull.doName(False)
            
        self.msgSettingsInfo.updateData()   
        
        
        self.optionPuppetMode = AttrFactory(self.SettingsInfoNull,'optionPuppetTemplateMode','int',initialValue = 0)      
        
        self.optionAimAxis= AttrFactory(self.SettingsInfoNull,'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=2) 
        self.optionUpAxis= AttrFactory(self.SettingsInfoNull,'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=1) 
        self.optionOutAxis= AttrFactory(self.SettingsInfoNull,'axisOut','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=0)         
            
        attributes.doSetLockHideKeyableAttr(self.SettingsInfoNull.nameShort) 
        
        return True
        
    
    