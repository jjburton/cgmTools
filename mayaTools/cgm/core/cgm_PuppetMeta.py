"""
------------------------------------------
cgm_PuppetMeta: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is the core MetaClass structure for cgm's modular rigger.
================================================================
"""
import maya.cmds as mc

import random
import re
import copy
import time

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim


#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import curve_Utils as CURVES
import cgm.core.lib.shape_utils as SHAPES
import cgm.core.lib.rigging_utils as RIG
import cgm.core.lib.distance_utils as DIST
import cgm_Meta as cgmMeta
from cgm.core.lib import nameTools
from cgm.core.rigger import ModuleFactory as mFactory
from cgm.core.rigger import PuppetFactory as pFactory
from cgm.core.classes import NodeFactory as nodeF
from cgm.core.lib import attribute_utils as ATTR
from cgm.lib import (modules,
                     distance,
                     deformers,
                     controlBuilder,
                     attributes,
                     search,
                     curves)
#for m in DIST,RIG:
#    reload(m)
    
cgmModuleTypes = mFactory.__l_modulesClasses__
__l_faceModuleTypes__ = mFactory.__l_faceModules__
_l_moduleStates = mFactory._l_moduleStates

########################################################################
class cgmPuppet(cgmMeta.cgmNode):
    """"""
    #----------------------------------------------------------------------
    #@cgmGEN.Timer
    def __init__(self, node = None, name = None, initializeOnly = False, doVerify = False, *args,**kws):
        _str_func = 'cgmPuppet.__init__'
        log.debug("|{0}| >> ...".format(_str_func))                        
        """
        if node:
            _buffer = ATTR.get_message(node,'puppet')
            if _buffer:
                log.info("|{0}| >> Passed masterNull [{1}]. Using puppet [{2}]".format(_str_func,node,_buffer[0]))                
                node = _buffer [0]"""
    
        super(cgmPuppet, self).__init__(node = node, name = name, nodeType = 'network') 

        #====================================================================================	
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            log.debug('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
            return
        #====================================================================================

        #self.UNMANAGED.extend(['i_masterNull','_UTILS'])
        for a in 'i_masterNull','_UTILS':
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a) 	
        self._UTILS = pFactory

        if self.__justCreatedState__ or doVerify:
            if self.isReferenced():
                log.error("|{0}| >> Cannot verify referenced nodes".format(_str_func))
                return
            elif not self.__verify__(name,**kws):
                raise RuntimeError,"|{0}| >> Failed to verify: {1}".format(_str_func,self.mNode)
          
    #====================================================================================

    def __verify__(self,name = None):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """             
        _short = self.p_nameShort
        _str_func = "cgmPuppet.__verify__({0})".format(_short)

        #============== 
        #Puppet Network Node ================================================================
        self.addAttr('mClass', initialValue='cgmPuppet',lock=True)  
        if name is not None and name:
            self.addAttr('cgmName',name, attrType='string', lock = True)
        self.addAttr('cgmType','puppetNetwork')
        self.addAttr('version',initialValue = 1.0, lock=True)  
        self.addAttr('masterNull',attrType = 'messageSimple',lock=True)  
        self.addAttr('masterControl',attrType = 'messageSimple',lock=True)  	
        self.addAttr('moduleChildren',attrType = 'message',lock=True) 
        self.addAttr('unifiedGeo',attrType = 'messageSimple',lock=True) 

        #Settings ============================================================================
        defaultFont = modules.returnSettingsData('defaultTextFont')
        self.addAttr('font',attrType = 'string',initialValue=defaultFont,lock=True)   
        self.addAttr('axisAim',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=2) 
        self.addAttr('axisUp',enumName = 'x+:y+:z+:x-:y-:z-', attrType = 'enum',initialValue=1) 
        self.addAttr('axisOut',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=0) 
        self.addAttr('skinDepth',attrType = 'float',initialValue=.75,lock=True)   

        self.doName()

        #MasterNull ===========================================================================
        if not self.getMessage('masterNull'):#If we don't have a masterNull, make one
            cgmMasterNull(puppet = self)
        else:
            self.masterNull.__verify__()
            
        if self.masterNull.getShortName() != self.cgmName:
            self.masterNull.doName()
            if self.masterNull.getShortName() != self.cgmName:
                log.warning("Master Null name still doesn't match what it should be.")
        
        ATTR.set_standardFlags(self.masterNull.mNode,attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        #self.__verifyGroups__()


        #Quick select sets ================================================================
        self.__verifyObjectSet__()

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Groups
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        self.__verifyGroups__()

        return True
    
    def atFactory(self, func = 'get_report', *args,**kws):
        """
        Function to call a self function by string. For menus and other reasons
        """
        _str_func = 'atFactory'
        _short = self.p_nameShort
        _res = None
        
        if not args:
            _str_args = ''
            args = [self]
        else:
            _str_args = ','.join(str(a) for a in args) + ','
            args = [self] + [a for a in args]
        if not kws:
            kws = {}
            _kwString = ''  
        else:
            _l = []
            for k,v in kws.iteritems():
                _l.append("{0}={1}".format(k,v))
            _kwString = ','.join(_l)  
        try:
            log.debug("|{0}| >> On: {1}".format(_str_func,_short))     
            log.debug("|{0}| >> {1}.{2}({3}{4})...".format(_str_func,_short,func,_str_args,_kwString))                                    
            _res = getattr(pFactory,func)(*args,**kws)
        except Exception,err:
            log.error(cgmGEN._str_hardLine)
            log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
            log.error("Node: {0} | func: {1}".format(_short,func))            
            if args:
                log.error("Args...")
                for a in args:
                    log.error("      {0}".format(a))
            if kws:
                log.error(" KWS...".format(_str_func))
                for k,v in kws.iteritems():
                    log.error("      {0} : {1}".format(k,v))   
            log.error("Errors...")
            for a in err.args:
                log.error(a)
            log.error(cgmGEN._str_subLine)
            raise Exception,err
        return _res
    def changeName(self,name = ''):
        if name == self.cgmName:
            log.error("Puppet already named '%s'"%self.cgmName)
            return
        if name != '' and type(name) is str:
            log.warn("Changing name from '%s' to '%s'"%(self.cgmName,name))
            self.cgmName = name
            self.__verify__()

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Puppet Utilities
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def __verifyGroups__(self):
        _short = self.p_nameShort
        _str_func = "__verifyGroups__({0})".format(_short)
        
        mMasterNull = self.masterNull
        
        if not mMasterNull:
            raise ValueError, "No masterNull"
        
        for attr in 'deform','noTransform','geo','parts','worldSpaceObjects','puppetSpaceObjects':
            _link = attr+'Group'
            mGroup = mMasterNull.getMessage(_link,asMeta=True)# Find the group
            if mGroup:mGroup = mGroup[0]
                                                
            if not mGroup:
                mGroup = cgmMeta.cgmObject(name=attr)#Create and initialize
                mGroup.doName()
                mGroup.connectParentNode(mMasterNull.mNode,'puppet', attr+'Group')
                
            log.debug("|{0}| >> attr: {1} | mGroup: {2}".format(_str_func, attr, mGroup))

            # Few Case things
            #==============            
            if attr in ['geo','parts']:
                mGroup.p_parent = mMasterNull.noTransformGroup
            elif attr in ['deform','puppetSpaceObjects'] and self.getMessage('masterControl'):
                mGroup.p_parent = self.getMessage('masterControl')[0]	    
            else:    
                mGroup.p_parent = mMasterNull
                
            ATTR.set_standardFlags(mGroup.mNode)
            
            if attr == 'worldSpaceObjects':
                mGroup.addAttr('cgmAlias','world')
            elif attr == 'puppetSpaceObjects':
                mGroup.addAttr('cgmAlias','puppet')



    def __verifyObjectSet__(self):
        _str_func = "__verifyObjectSet__({0})".format(self.p_nameShort)
        #Quick select sets ================================================================
        mSet = self.getMessage('puppetSet',asMeta=True)
        if mSet:
            mSet = mSet[0]
        else:#
            mSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
            mSet.connectParentNode(self.mNode,'puppet','puppetSet')

        ATTR.copy_to(self.mNode,'cgmName',mSet.mNode,'cgmName',driven = 'target')
        mSet.doName()



    def tracePuppet(self):
        pass #Do this later.Trace a puppet to be able to fully delete everything.
        #self.nodes_list.append()
        raise NotImplementedError
    """
    def doName(self,sceneUnique=False,nameChildren=False,**kws):
        #if not self.getTransform() and self.__justCreatedState__:
            #log.error("Naming just created nodes, causes recursive issues. Name after creation")
            #return False
        if self.isReferenced():
            log.error("'%s' is referenced. Cannot change name"%self.mNode)
            return False
        mc.rename(self.mNode,nameTools.returnCombinedNameFromDict(self.getNameDict()))"""

    def delete(self):
        """
        Delete the Puppet
        """
        mc.delete(self.masterNull.mNode)
        mc.delete(self.mNode)
        del(self)

    def addModule(self,mClass = 'cgmModule',**kws):
        """
        Create and connect a new module

        moduleType(string) - type of module to create

        p = cgmPM.cgmPuppet(name='Morpheus')
        p.addModule(mClass = 'cgmLimb',mType = 'torso')
        p.addModule(mClass = 'cgmLimb',mType = 'neck', moduleParent = 'spine_part')
        p.addModule(mClass = 'cgmLimb',mType = 'head', moduleParent = 'neck_part')
        p.addModule(mClass = 'cgmLimb',mType = 'arm',direction = 'left', moduleParent = 'spine_part')
        """   
        if mClass == 'cgmModule':
            tmpModule = cgmModule(**kws)   
        elif mClass == 'cgmLimb':
            tmpModule = cgmLimb(**kws)
        else:
            log.warning("'%s' is not a known module type. Cannot initialize"%mClass)
            return False

        self.connectModule(tmpModule)
        return tmpModule

    ##@r9General.Timer
    def connectModule(self,module,force = True,**kws):
        """
        Connects a module to a puppet

        module(string)
        """
        #See if it's connected
        #If exists, connect
        #Get instance
        #==============	
        buffer = copy.copy(self.getMessage('moduleChildren')) or []#Buffer till we have have append functionality	
        #self.i_masterNull = self.masterNull

        try:
            module.mNode#see if we have an instance
            if module.mNode in buffer and force != True:
                #log.warning("'%s' already connnected to '%s'"%(module.getShortName(),self.i_masterNull.getShortName()))
                return False 	    
        except:
            if mc.objExists(module):
                if mc.ls(module,long=True)[0] in buffer and force != True:
                    #log.warning("'%s' already connnected to '%s'"%(module,self.i_masterNull.getShortName()))
                    return False

                module = r9Meta.MetaClass(module)#initialize

            else:
                log.warning("'%s' doesn't exist"%module)#if it doesn't initialize, nothing is there		
                return False	

        #Logic checks
        #==============	
        if not module.hasAttr('mClass'):
            log.warning("'%s' lacks an mClass attr"%module.mNode)	    
            return False

        elif module.mClass not in cgmModuleTypes:
            log.warning("'%s' is not a recognized module type"%module.mClass)
            return False

        #Connect
        #==============	
        else:
            #if log.getEffectiveLevel() == 10:log.debug("Current children: %s"%self.getMessage('moduleChildren'))
            #if log.getEffectiveLevel() == 10:log.debug("Adding '%s'!"%module.getShortName())    

            buffer.append(module.mNode)
            self.__setMessageAttr__('moduleChildren',buffer) #Going to manually maintaining these so we can use simpleMessage attr  parents
            module.modulePuppet = self.mNode
            #del self.moduleChildren
            #self.connectChildren(buffer,'moduleChildren','modulePuppet',force=force)#Connect	    
            #module.__setMessageAttr__('modulePuppet',self.mNode)#Connect puppet to 

        #module.parent = self.i_partsGroup.mNode
        module.doParent(self.masterNull.partsGroup.mNode)

        return True

    def getGeo(self):
        return pFactory.getGeo(self)

    def getUnifiedGeo(self,*args,**kws):
        kws['mPuppet'] = self	
        return pFactory.getUnifiedGeo(*args,**kws)

    def getModuleFromDict(self,*args,**kws):
        """
        Pass a check dict of attributes and arguments. If that module is found, it returns it.
        checkDict = {'moduleType':'torso',etc}
        """
        kws['mPuppet'] = self	
        return pFactory.getModuleFromDict(*args,**kws)

    def getModules(self,*args,**kws):
        """
        Returns ordered modules. If you just need modules, they're always accessible via self.moduleChildren
        """
        kws['mPuppet'] = self	
        return pFactory.getModules(*args,**kws)   

    def getOrderedModules(self,*args,**kws):
        """
        Returns ordered modules. If you just need modules, they're always accessible via self.moduleChildren
        """
        kws['mPuppet'] = self		
        return pFactory.getOrderedModules(*args,**kws)

    def get_mirrorIndexDict(self,*args,**kws):
        """
        """
        kws['mPuppet'] = self			
        return pFactory.get_mirrorIndexDict(*args,**kws)

    def state_set(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.setState)
        """
        kws['mPuppet'] = self	
        return pFactory.state_set(*args,**kws)

    def get_nextMirrorIndex(self,*args,**kws):
        """
        """
        kws['mPuppet'] = self			
        return pFactory.get_nextMirrorIndex(*args,**kws) 

    def gatherModules(self,*args,**kws):
        """
        Gathers all connected module children to the puppet
        """
        kws['mPuppet'] = self
        return pFactory.gatherModules(*args,**kws)    

    def getState(self,*args,**kws):
        """
        Returns puppet state. That is the minimum state of it's modules
        """
        kws['mPuppet'] = self	
        return pFactory.getState(*args,**kws) 

    #>>> Animation
    #========================================================================
    def animSetAttr(self,*args,**kws):
        kws['mPuppet'] = self
        return pFactory.animSetAttr(*args,**kws) 

        #return pFactory.animSetAttr(self,attr, value, settingsOnly)
    def controlSettings_setModuleAttrs(self,*args,**kws):
        kws['mPuppet'] = self
        return pFactory.controlSettings_setModuleAttrs(*args,**kws)     

    def toggle_subVis(self):
        try:
            self.masterControl.controlVis.subControls = not self.masterControl.controlVis.subControls
        except:pass

    def anim_key(self,**kws):
        _str_func = "%s.animKey()"%self.p_nameShort  
        start = time.clock()
        b_return = None
        _l_callSelection = mc.ls(sl=True) or []
        try:
            try:buffer = self.puppetSet.getList()
            except:buffer = []
            if buffer:
                mc.select(buffer)
                mc.setKeyframe(**kws)
                b_return =  True
            b_return = False
            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)     
            if _l_callSelection:mc.select(_l_callSelection)                	    
            return b_return
        except Exception,error:
            log.error("%s.animKey>> animKey fail | %s"%(self.getBaseName(),error))
            return False

    def mirrorMe(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirrorMe(*args,**kws)

    def mirror_do(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirror_do(*args,**kws)

    def mirrorSetup_verify(self,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirrorSetup_verify(**kws)   

    def anim_reset(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.animReset(*args,**kws)

    def anim_select(self):
        _str_func = "%s.anim_select()"%self.p_nameShort  
        start = time.clock()
        try:self.puppetSet.select()
        except:pass
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)     
        return buffer

    def isCustomizable(self):
        return False 

    def isTemplated(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isTemplated(*args,**kws)
    #def poseStore_templateSettings(self,*args,**kws):
        #kws['mPuppet'] = self			
        #return pFactory.poseStore_templateSettings(*args,**kws)
    #def poseLoad_templateSettings(self,*args,**kws):
        #kws['mPuppet'] = self			
        #return pFactory.poseLoad_templateSettings(*args,**kws)

    def templateSettings_call(self,*args,**kws):
        '''
        Call for doing multiple functions with templateSettings.

        :parameters:
            mode | string
        reset:reset controls
        store:store data to modules
        load:load data from modules
        query:get current data
        export:export to a pose file
        import:import from a  pose file
            filepath | string/None -- if None specified, user will be prompted
        '''
        kws['mPuppet'] = self			
        return pFactory.templateSettings_call(*args,**kws)

    def isSized(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isSized(*args,**kws)
    
    def isSkeletonized(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isSkeletonized(*args,**kws)
    @cgmGEN.Timer
    def _verifyMasterControl(self,**kws):
        """ 
        """
        _str_func = "_verifyMasterControl({0})".format(self.p_nameShort)
        self.__verifyGroups__()#...make sure everythign is there
        
        # Master Curve
        #==================================================================
        masterControl = attributes.returnMessageObject(self.mNode,'masterControl')
        if mc.objExists( masterControl ):
            mi_masterControl = self.masterControl
        else:
            #Get size
            if not kws.get('size'):
                if self.getGeo():
                    averageBBSize = distance.returnBoundingBoxSizeToAverage(self.masterNull.geoGroup.mNode)
                    kws['size'] = averageBBSize * .75
                elif len(self.moduleChildren) == 1 and self.moduleChildren[0].getMessage('helper'):
                    averageBBSize = distance.returnBoundingBoxSizeToAverage(self.moduleChildren[0].getMessage('helper'))		
                    kws['size'] = averageBBSize * 1.5
                elif 'size' not in kws.keys():kws['size'] = 50
            mi_masterControl = cgmMasterControl(puppet = self,**kws)#Create and initialize
            mi_masterControl.__verify__()
        mi_masterControl.parent = self.masterNull.mNode
        mi_masterControl.doName()
        

        # Vis setup
        # Setup the vis network
        #====================================================================
        try:
            if not mi_masterControl.hasAttr('controlVis') or not mi_masterControl.getMessage('controlVis'):
                log.error("This is an old master control or the vis control has been deleted. rebuild")
            else:
                iVis = mi_masterControl.controlVis
                visControls = 'left','right','sub','main'
                visArg = [{'result':[iVis,'leftSubControls_out'],'drivers':[[iVis,'left'],[iVis,'subControls'],[iVis,'controls']]},
                          {'result':[iVis,'rightSubControls_out'],'drivers':[[iVis,'right'],[iVis,'subControls'],[iVis,'controls']]},
                          {'result':[iVis,'subControls_out'],'drivers':[[iVis,'subControls'],[iVis,'controls']]},		      
                          {'result':[iVis,'leftControls_out'],'drivers':[[iVis,'left'],[iVis,'controls']]},
                          {'result':[iVis,'rightControls_out'],'drivers':[[iVis,'right'],[iVis,'controls']]}
                          ]
                nodeF.build_mdNetwork(visArg)
        except Exception,err:
            log.error("{0} >> visNetwork fail! {1}".format(_str_func,err))
            raise StandardError,err 	

        # Settings setup
        # Setup the settings network
        #====================================================================	
        i_settings = mi_masterControl.controlSettings
        str_nodeShort = str(i_settings.getShortName())
        #Skeleton/geo settings
        for attr in ['skeleton','geo','proxy']:
            i_settings.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
            nodeF.argsToNodes("%s.%sVis = if %s.%s > 0"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
            nodeF.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()

        #Geotype
        #i_settings.addAttr('geoType',enumName = 'reg:proxy', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
        #for i,attr in enumerate(['reg','proxy']):
        #    nodeF.argsToNodes("%s.%sVis = if %s.geoType == %s:1 else 0"%(str_nodeShort,attr,str_nodeShort,i)).doBuild()    
        
        
        
        #Divider
        i_settings.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)

        #i_settings.addAttr('templateVis',attrType = 'float',lock=True,hidden = True)
        #i_settings.addAttr('templateLock',attrType = 'float',lock=True,hidden = True)	
        #i_settings.addAttr('templateStuff',enumName = 'off:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
        #nodeF.argsToNodes("%s.templateVis = if %s.templateStuff > 0"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()
        #nodeF.argsToNodes("%s.templateLock = if %s.templateStuff == 1:0 else 2"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()	


        #>>> Deform group
        #=====================================================================	
        if self.masterNull.getMessage('deformGroup'):
            self.masterNull.deformGroup.parent = mi_masterControl.mNode

        mi_masterControl.addAttr('cgmAlias','world',lock = True)


        #>>> Skeleton Group
        #=====================================================================	
        if not self.masterNull.getMessage('skeletonGroup'):
            #Make it and link it
            #i_grp = mi_masterControl.doDuplicateTransform()
            mGrp = cgmMeta.createMetaNode('cgmObject')
            mGrp.doSnapTo(mi_masterControl.mNode)
            
            #mGrp.doRemove('cgmName')
            mGrp.addAttr('cgmTypeModifier','skeleton',lock=True)	 
            mGrp.parent = mi_masterControl.mNode
            self.masterNull.connectChildNode(mGrp,'skeletonGroup','module')

            mGrp.doName()
        else:
            mGrp = self.masterNull.skeletonGroup


        #Verify the connections
        mGrp.overrideEnabled = 1             
        cgmMeta.cgmAttr(i_settings,'skeletonVis',lock=False).doConnectOut("%s.%s"%(mGrp.mNode,'overrideVisibility'))    
        cgmMeta.cgmAttr(i_settings,'skeletonLock',lock=False).doConnectOut("%s.%s"%(mGrp.mNode,'overrideDisplayType'))    


        #>>>Connect some flags
        #=====================================================================
        i_geoGroup = self.masterNull.geoGroup
        i_geoGroup.overrideEnabled = 1		
        cgmMeta.cgmAttr(i_settings.mNode,'geoVis',lock=False).doConnectOut("%s.%s"%(i_geoGroup.mNode,'overrideVisibility'))
        cgmMeta.cgmAttr(i_settings.mNode,'geoLock',lock=False).doConnectOut("%s.%s"%(i_geoGroup.mNode,'overrideDisplayType'))  

        try:self.masterNull.puppetSpaceObjectsGroup.parent = mi_masterControl
        except:pass
        
        return True


class cgmPuppetOLD(cgmMeta.cgmNode):
    """"""
    #----------------------------------------------------------------------
    #@cgmGEN.Timer
    def __init__(self, node = None, name = None, initializeOnly = False, doVerify = False, *args,**kws):
        """Constructor"""

        '''#>>>Keyword args
        puppet = kws.pop('puppet',None)

        #Need a simple return of
        puppets = pFactory.simplePuppetReturn()

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Finding the network node and name info from the provided information
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>          
        ##If a node is provided, check if it's a cgmPuppet
        ##If a name is provided, see if there's a puppet with that name, 
        ##If nothing is provided, just make one
        if node is None and name is None and args:
            #if log.getEffectiveLevel() == 10:log.debug("Checking '%s'"%args[0])
            node = args[0]

        if puppets:#If we have puppets, check em
            #if log.getEffectiveLevel() == 10:log.debug("Found the following puppets: '%s'"%"','".join(puppets))            
            if name is not None or node is not None:    
                if node is not None and node in puppets:
                    puppet = node
                    name = attributes.doGetAttr(node,'cgmName')
                else:
                    for p in puppets:
                        if attributes.doGetAttr(p,'cgmName') in [node,name]:
                            #if log.getEffectiveLevel() == 10:log.debug("Puppet tagged '%s' exists. Checking '%s'..."%(attributes.doGetAttr(p,'cgmName'),p))
                            puppet = p
                            name = attributes.doGetAttr(p,'cgmName')
                            break

        if not name:
            log.warning("No puppet name found")
            name = search.returnRandomName()  

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Verify or Initialize
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>           
        #if log.getEffectiveLevel() == 10:log.debug("Puppet is '%s'"%name)
        if puppet is None:puppetCreatedState = True
        else:puppetCreatedState = False'''

        super(cgmPuppet, self).__init__(node = node, name = name, nodeType = 'network') 

        #====================================================================================	
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            log.debug('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
            return
        #====================================================================================

        #self.UNMANAGED.extend(['i_masterNull','_UTILS'])
        for a in 'i_masterNull','_UTILS':
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a) 	
        self._UTILS = pFactory

        #self.__justCreatedState__ = puppetCreatedState

        try:#>>> Puppet Network Initialization Procedure ==================       
            if self.isReferenced():# or initializeOnly:
                pass
                #if not self.initialize():
                    #log.warning("'%s' failed to initialize. Please go back to the non referenced file to repair!"%name)
                    #raise StandardError,"'%s' failed to initialize. Please go back to the non referenced file to repair!"%name
            elif self.__justCreatedState__ or doVerify:
                #if log.getEffectiveLevel() == 10:log.debug("Verifying...")
                try:
                    if not self.__verify__(name,**kws):
                        #log.critical("'%s' failed to __verify__!"%name)
                        raise StandardError,"'%s' failed to verify!"%name
                except Exception,error:
                    raise Exception,"%s >>> verify fail | error : %s"%(self.p_nameShort,error) 

        except Exception,error:raise Exception,"verify checks...| {0}".format(error)

    #====================================================================================
    #@cgmGEN.Timer    
    def initialize(self):
        """ 
        Initializes the various components a masterNull for a character/asset.

        RETURNS:
        success(bool)
        """  
        #Puppet Network Node
        #==============
        try:
            if not issubclass(type(self),cgmPuppet):
                log.error("'%s' is not a puppet. It's mClass is '%s'"%(self.mNode, attributes.doGetAttr(self.mNode,'mClass')))
                return False

            return True
        except Exception,error:raise Exception,"self.initialize fail >> {0}".format(error)

    #@cgmGEN.Timer
    def __verify__(self,name = None):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """             
        _str_func = "cgmPuppet.__verify__(%s)"%self.p_nameShort
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	

        #============== 
        try:#Puppet Network Node ================================================================
            #if log.getEffectiveLevel() == 10:log.debug(1)
            self.addAttr('mClass', initialValue='cgmPuppet',lock=True)  
            if name is not None and name:
                self.addAttr('cgmName',name, attrType='string', lock = True)
            self.addAttr('cgmType','puppetNetwork')
            self.addAttr('version',initialValue = 1.0, lock=True)  
            self.addAttr('masterNull',attrType = 'messageSimple',lock=True)  
            self.addAttr('masterControl',attrType = 'messageSimple',lock=True)  	
            self.addAttr('moduleChildren',attrType = 'message',lock=True) 
            self.addAttr('unifiedGeo',attrType = 'messageSimple',lock=True) 
        except Exception,error:
            raise StandardError,"%s >>> Puppet network |error : %s"%(_str_func,error)

        try:#Settings ============================================================================
            #if log.getEffectiveLevel() == 10:log.debug(2)	
            defaultFont = modules.returnSettingsData('defaultTextFont')
            self.addAttr('font',attrType = 'string',initialValue=defaultFont,lock=True)   
            self.addAttr('axisAim',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=2) 
            self.addAttr('axisUp',enumName = 'x+:y+:z+:x-:y-:z-', attrType = 'enum',initialValue=1) 
            self.addAttr('axisOut',enumName = 'x+:y+:z+:x-:y-:z-',attrType = 'enum',initialValue=0) 
            self.addAttr('skinDepth',attrType = 'float',initialValue=.75,lock=True)   

            self.doName()
            #if log.getEffectiveLevel() == 10:log.debug("Network good...")
        except Exception,error:
            raise StandardError,"%s >>> Settings |error : %s"%(_str_func,error)

        try:#MasterNull ===========================================================================
            if not self.getMessage('masterNull'):#If we don't have a masterNull, make one
                self.i_masterNull = cgmMasterNull(puppet = self)
            else:
                self.i_masterNull = self.masterNull#Linking to instance for faster processing. Good idea?
                self.i_masterNull.__verify__()
                
            if self.i_masterNull.getShortName() != self.cgmName:
                self.masterNull.doName()
                if self.i_masterNull.getShortName() != self.cgmName:
                    log.warning("Master Null name still doesn't match what it should be.")
                    #return False
            attributes.doSetLockHideKeyableAttr(self.i_masterNull.mNode,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz'])
        except Exception,error:
            raise Exception,"%s >>> MasterNull | error : %s"%(_str_func,error)	
        
        self.__verifyGroups__()


        try:#Quick select sets ================================================================
            self.__verifyObjectSet__()

        except Exception,error:
            raise Exception,"%s >>> ObjectSet | error : %s"%(_str_func,error)

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Groups
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
        try:
            self.__verifyGroups__()
        except Exception,error:
            raise Exception,"%s >>> groups |error : %s"%(_str_func,error)	

        return True

    def changeName(self,name = ''):
        if name == self.cgmName:
            log.error("Puppet already named '%s'"%self.cgmName)
            return
        if name != '' and type(name) is str:
            log.warn("Changing name from '%s' to '%s'"%(self.cgmName,name))
            self.cgmName = name
            self.__verify__()

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Puppet Utilities
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    def __verifyGroups__(self):
        _str_func = "__verifyGroups__({0})".format(self.p_nameShort)
        try:#Quick select sets ================================================================
            #if log.getEffectiveLevel() == 10:log.debug(5)
            mi_masterNull = self.masterNull
            for attr in 'deform','noTransform','geo','parts','worldSpaceObjects':
                grp = attributes.returnMessageObject(mi_masterNull.mNode,attr+'Group')# Find the group
                Attr = 'i_' + attr+'Group'#Get a better attribute store string           
                if mc.objExists( grp ):
                    self.__dict__[Attr]  = r9Meta.MetaClass(grp)#initialize
                    #if log.getEffectiveLevel() == 10:log.debug("'%s' initialized as 'self.%s'"%(grp,Attr))
                else:#Make it
                    #if log.getEffectiveLevel() == 10:log.debug('Creating %s'%attr)                                    
                    self.__dict__[Attr]= cgmMeta.cgmObject(name=attr)#Create and initialize
                    self.__dict__[Attr].doName()
                    self.__dict__[Attr].connectParentNode(mi_masterNull.mNode,'puppet', attr+'Group')
                    #if log.getEffectiveLevel() == 10:log.debug("Initialized as 'self.%s'"%(Attr))                    
                    self.__dict__[Attr].__verify__()

                # Few Case things
                #==============            
                if attr == 'geo':
                    self.__dict__[Attr].doParent(self.i_noTransformGroup)
                elif attr == 'deform' and self.getMessage('masterControl'):
                    self.__dict__[Attr].doParent(self.getMessage('masterControl')[0])		    
                else:    
                    self.__dict__[Attr].doParent(mi_masterNull)
                attributes.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode ) 	    
        except Exception,error:raise Exception,"{0} | error : {1}".format(_str_func,error)    



    def __verifyObjectSet__(self):
        _str_func = "__verifyObjectSet__({0})".format(self.p_nameShort)
        try:#Quick select sets ================================================================
            if not self.getMessage('puppetSet'):#
                i_selectSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
                i_selectSet.connectParentNode(self.mNode,'puppet','puppetSet')

            i_selectSet = self.puppetSet
            cgmMeta.cgmAttr(self,'cgmName').doCopyTo(i_selectSet.mNode,connectTargetToSource =True)
            i_selectSet.doName()		    

        except Exception,error:raise Exception,"{0} >>> ObjectSet | error : {1}".format(_str_func,error)


    def tracePuppet(self):
        pass #Do this later.Trace a puppet to be able to fully delete everything.
        #self.nodes_list.append()
        raise NotImplementedError

    def doName(self,sceneUnique=False,nameChildren=False,**kws):
        """
        Cause puppets are stupid
        """
        #if not self.getTransform() and self.__justCreatedState__:
            #log.error("Naming just created nodes, causes recursive issues. Name after creation")
            #return False
        if self.isReferenced():
            log.error("'%s' is referenced. Cannot change name"%self.mNode)
            return False
        mc.rename(self.mNode,nameTools.returnCombinedNameFromDict(self.getNameDict()))

    def delete(self):
        """
        Delete the Puppet
        """
        mc.delete(self.masterNull.mNode)
        mc.delete(self.mNode)
        del(self)

    def addModule(self,mClass = 'cgmModule',**kws):
        """
        Create and connect a new module

        moduleType(string) - type of module to create

        p = cgmPM.cgmPuppet(name='Morpheus')
        p.addModule(mClass = 'cgmLimb',mType = 'torso')
        p.addModule(mClass = 'cgmLimb',mType = 'neck', moduleParent = 'spine_part')
        p.addModule(mClass = 'cgmLimb',mType = 'head', moduleParent = 'neck_part')
        p.addModule(mClass = 'cgmLimb',mType = 'arm',direction = 'left', moduleParent = 'spine_part')
        """   
        if mClass == 'cgmModule':
            tmpModule = cgmModule(**kws)   
        elif mClass == 'cgmLimb':
            tmpModule = cgmLimb(**kws)
        else:
            log.warning("'%s' is not a known module type. Cannot initialize"%mClass)
            return False

        self.connectModule(tmpModule)
        return tmpModule

    ##@r9General.Timer
    def connectModule(self,module,force = True,**kws):
        """
        Connects a module to a puppet

        module(string)
        """
        #See if it's connected
        #If exists, connect
        #Get instance
        #==============	
        buffer = copy.copy(self.getMessage('moduleChildren')) or []#Buffer till we have have append functionality	
        self.i_masterNull = self.masterNull

        try:
            module.mNode#see if we have an instance
            if module.mNode in buffer and force != True:
                log.warning("'%s' already connnected to '%s'"%(module.getShortName(),self.i_masterNull.getShortName()))
                return False 	    
        except:
            if mc.objExists(module):
                if mc.ls(module,long=True)[0] in buffer and force != True:
                    log.warning("'%s' already connnected to '%s'"%(module,self.i_masterNull.getShortName()))
                    return False

                module = r9Meta.MetaClass(module)#initialize

            else:
                log.warning("'%s' doesn't exist"%module)#if it doesn't initialize, nothing is there		
                return False	

        #Logic checks
        #==============	
        if not module.hasAttr('mClass'):
            log.warning("'%s' lacks an mClass attr"%module.mNode)	    
            return False

        elif module.mClass not in cgmModuleTypes:
            log.warning("'%s' is not a recognized module type"%module.mClass)
            return False

        #Connect
        #==============	
        else:
            #if log.getEffectiveLevel() == 10:log.debug("Current children: %s"%self.getMessage('moduleChildren'))
            #if log.getEffectiveLevel() == 10:log.debug("Adding '%s'!"%module.getShortName())    

            buffer.append(module.mNode)
            self.__setMessageAttr__('moduleChildren',buffer) #Going to manually maintaining these so we can use simpleMessage attr  parents
            module.modulePuppet = self.mNode
            #del self.moduleChildren
            #self.connectChildren(buffer,'moduleChildren','modulePuppet',force=force)#Connect	    
            #module.__setMessageAttr__('modulePuppet',self.mNode)#Connect puppet to 

        #module.parent = self.i_partsGroup.mNode
        module.doParent(self.masterNull.partsGroup.mNode)

        return True

    def getGeo(self,*args,**kws):
        kws['mPuppet'] = self
        return pFactory.getGeo(*args,**kws)

    def getUnifiedGeo(self,*args,**kws):
        kws['mPuppet'] = self	
        return pFactory.getUnifiedGeo(*args,**kws)

    def getModuleFromDict(self,*args,**kws):
        """
        Pass a check dict of attributes and arguments. If that module is found, it returns it.
        checkDict = {'moduleType':'torso',etc}
        """
        kws['mPuppet'] = self	
        return pFactory.getModuleFromDict(*args,**kws)

    def getModules(self,*args,**kws):
        """
        Returns ordered modules. If you just need modules, they're always accessible via self.moduleChildren
        """
        kws['mPuppet'] = self	
        return pFactory.getModules(*args,**kws)   

    def getOrderedModules(self,*args,**kws):
        """
        Returns ordered modules. If you just need modules, they're always accessible via self.moduleChildren
        """
        kws['mPuppet'] = self		
        return pFactory.getOrderedModules(*args,**kws)

    def get_mirrorIndexDict(self,*args,**kws):
        """
        """
        kws['mPuppet'] = self			
        return pFactory.get_mirrorIndexDict(*args,**kws)

    def state_set(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.setState)
        """
        kws['mPuppet'] = self	
        return pFactory.state_set(*args,**kws)

    def get_nextMirrorIndex(self,*args,**kws):
        """
        """
        kws['mPuppet'] = self			
        return pFactory.get_nextMirrorIndex(*args,**kws) 

    def gatherModules(self,*args,**kws):
        """
        Gathers all connected module children to the puppet
        """
        kws['mPuppet'] = self
        return pFactory.gatherModules(*args,**kws)    

    def getState(self,*args,**kws):
        """
        Returns puppet state. That is the minimum state of it's modules
        """
        kws['mPuppet'] = self	
        return pFactory.getState(*args,**kws) 

    #>>> Animation
    #========================================================================
    def animSetAttr(self,*args,**kws):
        kws['mPuppet'] = self
        return pFactory.animSetAttr(*args,**kws) 

        #return pFactory.animSetAttr(self,attr, value, settingsOnly)
    def controlSettings_setModuleAttrs(self,*args,**kws):
        kws['mPuppet'] = self
        return pFactory.controlSettings_setModuleAttrs(*args,**kws)     

    def toggle_subVis(self):
        try:
            self.masterControl.controlVis.subControls = not self.masterControl.controlVis.subControls
        except:pass

    def anim_key(self,**kws):
        _str_func = "%s.animKey()"%self.p_nameShort  
        start = time.clock()
        b_return = None
        _l_callSelection = mc.ls(sl=True) or []
        try:
            try:buffer = self.puppetSet.getList()
            except:buffer = []
            if buffer:
                mc.select(buffer)
                mc.setKeyframe(**kws)
                b_return =  True
            b_return = False
            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)     
            if _l_callSelection:mc.select(_l_callSelection)                	    
            return b_return
        except Exception,error:
            log.error("%s.animKey>> animKey fail | %s"%(self.getBaseName(),error))
            return False

    def mirrorMe(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirrorMe(*args,**kws)

    def mirror_do(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirror_do(*args,**kws)

    def mirrorSetup_verify(self,**kws):
        kws['mPuppet'] = self			
        return pFactory.mirrorSetup_verify(**kws)   

    def anim_reset(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.animReset(*args,**kws)

    def anim_select(self):
        _str_func = "%s.anim_select()"%self.p_nameShort  
        start = time.clock()
        try:self.puppetSet.select()
        except:pass
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_func,(time.clock()-start)) + "-"*75)     
        return buffer

    def isCustomizable(self):
        return False 

    def isTemplated(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isTemplated(*args,**kws)
    #def poseStore_templateSettings(self,*args,**kws):
        #kws['mPuppet'] = self			
        #return pFactory.poseStore_templateSettings(*args,**kws)
    #def poseLoad_templateSettings(self,*args,**kws):
        #kws['mPuppet'] = self			
        #return pFactory.poseLoad_templateSettings(*args,**kws)

    def templateSettings_call(self,*args,**kws):
        '''
        Call for doing multiple functions with templateSettings.

        :parameters:
            mode | string
        reset:reset controls
        store:store data to modules
        load:load data from modules
        query:get current data
        export:export to a pose file
        import:import from a  pose file
            filepath | string/None -- if None specified, user will be prompted
        '''
        kws['mPuppet'] = self			
        return pFactory.templateSettings_call(*args,**kws)

    def isSized(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isSized(*args,**kws)
    def isSkeletonized(self,*args,**kws):
        kws['mPuppet'] = self			
        return pFactory.isSkeletonized(*args,**kws)

    def _verifyMasterControl(self,**kws):
        """ 
        """
        _str_func = "cgmPuppet._verifyMasterControl(%s)"%self.p_nameShort    
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        # Master Curve
        #==================================================================
        masterControl = attributes.returnMessageObject(self.mNode,'masterControl')
        if mc.objExists( masterControl ):
            #If exists, initialize it                                 	    
            mi_masterControl = self.masterControl
        else:#Make it
            #Get size
            if not kws.get('size'):
                if self.getGeo():
                    averageBBSize = distance.returnBoundingBoxSizeToAverage(self.masterNull.geoGroup.mNode)
                    kws['size'] = averageBBSize * .75
                elif len(self.moduleChildren) == 1 and self.moduleChildren[0].getMessage('helper'):
                    averageBBSize = distance.returnBoundingBoxSizeToAverage(self.moduleChildren[0].getMessage('helper'))		
                    kws['size'] = averageBBSize * 1.5
                elif 'size' not in kws.keys():kws['size'] = 50
            mi_masterControl = cgmMasterControl(puppet = self,**kws)#Create and initialize
            mi_masterControl.__verify__()
        mi_masterControl.parent = self.masterNull.mNode
        mi_masterControl.doName()
        """    
	except Exception,error:
	    log.error("_verifyMasterControl>> masterControl fail! "%error)
	    raise StandardError,error """

        # Vis setup
        # Setup the vis network
        #====================================================================
        try:
            if not mi_masterControl.hasAttr('controlVis') or not mi_masterControl.getMessage('controlVis'):
                log.error("This is an old master control or the vis control has been deleted. rebuild")
            else:
                iVis = mi_masterControl.controlVis
                visControls = 'left','right','sub','main'
                visArg = [{'result':[iVis,'leftSubControls_out'],'drivers':[[iVis,'left'],[iVis,'subControls'],[iVis,'controls']]},
                          {'result':[iVis,'rightSubControls_out'],'drivers':[[iVis,'right'],[iVis,'subControls'],[iVis,'controls']]},
                          {'result':[iVis,'subControls_out'],'drivers':[[iVis,'subControls'],[iVis,'controls']]},		      
                          {'result':[iVis,'leftControls_out'],'drivers':[[iVis,'left'],[iVis,'controls']]},
                          {'result':[iVis,'rightControls_out'],'drivers':[[iVis,'right'],[iVis,'controls']]}
                          ]
                nodeF.build_mdNetwork(visArg)
        except Exception,err:
            log.error("{0} >> visNetwork fail! {1}".format(_str_func,err))
            raise StandardError,err 	

        # Settings setup
        # Setup the settings network
        #====================================================================	
        i_settings = mi_masterControl.controlSettings
        str_nodeShort = str(i_settings.getShortName())
        #Skeleton/geo settings
        for attr in ['skeleton','geo',]:
            i_settings.addAttr(attr,enumName = 'off:lock:on', defaultValue = 1, attrType = 'enum',keyable = False,hidden = False)
            nodeF.argsToNodes("%s.%sVis = if %s.%s > 0"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()
            nodeF.argsToNodes("%s.%sLock = if %s.%s == 2:0 else 2"%(str_nodeShort,attr,str_nodeShort,attr)).doBuild()

        #Geotype
        i_settings.addAttr('geoType',enumName = 'reg:proxy', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
        for i,attr in enumerate(['reg','proxy']):
            nodeF.argsToNodes("%s.%sVis = if %s.geoType == %s:1 else 0"%(str_nodeShort,attr,str_nodeShort,i)).doBuild()    

        #Divider
        i_settings.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)

        #i_settings.addAttr('templateVis',attrType = 'float',lock=True,hidden = True)
        #i_settings.addAttr('templateLock',attrType = 'float',lock=True,hidden = True)	
        #i_settings.addAttr('templateStuff',enumName = 'off:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
        #nodeF.argsToNodes("%s.templateVis = if %s.templateStuff > 0"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()
        #nodeF.argsToNodes("%s.templateLock = if %s.templateStuff == 1:0 else 2"%(i_settings.getShortName(),i_settings.getShortName())).doBuild()	


        #>>> Deform group
        #=====================================================================	
        if self.masterNull.getMessage('deformGroup'):
            self.masterNull.deformGroup.parent = mi_masterControl.mNode

        mi_masterControl.addAttr('cgmAlias','world',lock = True)


        #>>> Skeleton Group
        #=====================================================================	
        if not self.masterNull.getMessage('skeletonGroup'):
            #Make it and link it
            i_grp = mi_masterControl.doDuplicateTransform()
            i_grp = cgmMeta.validateObjArg(i_grp,'cgmObject',setClass = True)
            i_grp.doRemove('cgmName')
            i_grp.addAttr('cgmTypeModifier','skeleton',lock=True)	 
            i_grp.parent = mi_masterControl.mNode
            self.masterNull.connectChildNode(i_grp,'skeletonGroup','module')

            i_grp.doName()

        self._i_skeletonGroup = self.masterNull.skeletonGroup	

        #Verify the connections
        self._i_skeletonGroup.overrideEnabled = 1             
        cgmMeta.cgmAttr(i_settings,'skeletonVis',lock=False).doConnectOut("%s.%s"%(self._i_skeletonGroup.mNode,'overrideVisibility'))    
        cgmMeta.cgmAttr(i_settings,'skeletonLock',lock=False).doConnectOut("%s.%s"%(self._i_skeletonGroup.mNode,'overrideDisplayType'))    


        #>>>Connect some flags
        #=====================================================================
        i_geoGroup = self.masterNull.geoGroup
        i_geoGroup.overrideEnabled = 1		
        cgmMeta.cgmAttr(i_settings.mNode,'geoVis',lock=False).doConnectOut("%s.%s"%(i_geoGroup.mNode,'overrideVisibility'))
        cgmMeta.cgmAttr(i_settings.mNode,'geoLock',lock=False).doConnectOut("%s.%s"%(i_geoGroup.mNode,'overrideDisplayType'))  

        self.masterNull.worldSpaceObjectsGroup.parent = mi_masterControl

        return True

class cgmMorpheusPuppet(cgmPuppet):
    """
    def __init__(self, node = None, name = None, initializeOnly = False, *args,**kws):
    cgmPuppet.__init__(self, node = node, name = name, initializeOnly = initializeOnly, *args,**kws)
        """

    def get_customizationNetwork(self):
        """
        Call to check message connections for a customization network
        """
        for plug in mc.listConnections("{0}.message".format(self.mNode)):
            #log.info("Checking {0}".format(plug))
            if attributes.doGetAttr(plug,'mClass') == 'cgmMorpheusMakerNetwork':
                return cgmMeta.asMeta(plug)
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Special objects
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
class cgmMasterNull(cgmMeta.cgmObject):
    """"""
    #----------------------------------------------------------------------
    ##@r9General.Timer    
    def __init__(self,node = None, name = 'Master',doVerify = False, *args,**kws):
        """Constructor"""
        #>>>Keyword args
        if mc.objExists(name) and node is None:
            node = name

        super(cgmMasterNull, self).__init__(node=node, name = name)
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================	

        #====================================================================================
        if not self.isReferenced():   
            if self.__justCreatedState__ or doVerify:
                if not self.__verify__(**kws):
                    raise StandardError,"Failed!"

    ##@r9General.Timer    
    def __verify__(self,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
        puppet = kws.pop('puppet',False)
        if puppet and not self.isReferenced():
            #if log.getEffectiveLevel() == 10:log.debug("Puppet provided!")
            #if log.getEffectiveLevel() == 10:log.debug(puppet.cgmName)
            #if log.getEffectiveLevel() == 10:log.debug(puppet.mNode)
            #self.doStore('cgmName',puppet.mNode+'.cgmName')
            ATTR.copy_to(puppet.mNode,'cgmName',self.mNode,driven='target')
            self.addAttr('puppet',attrType = 'messageSimple')
            if not self.connectParentNode(puppet,'puppet','masterNull'):
                raise StandardError,"Failed to connect masterNull to puppet network!"

        self.addAttr('mClass',value = 'cgmMasterNull',lock=True)
        self.addAttr('cgmName',initialValue = '',lock=True)
        self.addAttr('cgmType',initialValue = 'ignore',lock=True)
        self.addAttr('cgmModuleType',value = 'master',lock=True)   
        self.addAttr('partsGroup',attrType = 'messageSimple',lock=True)   
        self.addAttr('deformGroup',attrType = 'messageSimple',lock=True)   	
        self.addAttr('noTransformGroup',attrType = 'messageSimple',lock=True)   
        self.addAttr('geoGroup',attrType = 'messageSimple',lock=True)   

        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()
        return True

    def __bindData__(self):
        pass

class cgmInfoNode2(cgmMeta.cgmNode):
    """"""
    def __init__(self,node = None, name = None, doVerify = False, *args,**kws):
        """Constructor"""
        #if log.getEffectiveLevel() == 10:log.debug(">>> cgmInfoNode.__init__")
        #if kws:log.debug("kws: %s"%kws)

        puppet = kws.pop('puppet',False)#to pass a puppet instance in 
        infoType = kws.pop('infoType','')

        #>>>Keyword args
        super(cgmInfoNode, self).__init__(node=node, name = name,*args,**kws)
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================	

        #====================================================================================
        #if log.getEffectiveLevel() == 10:log.debug("puppet :%s"%puppet)
        if puppet:
            self.doStore('cgmName',puppet.mNode+'.cgmName')
            self.connectParentNode(puppet, 'puppet',infoType)               

        self.addAttr('cgmName', attrType = 'string', initialValue = '',lock=True)
        if infoType == '':
            if self.hasAttr('cgmTypeModifier'):
                infoType = self.cgmTypeModifier
            else:
                infoType = 'settings'

        self.addAttr('cgmTypeModifier',infoType,lock=True)
        self.addAttr('cgmType','info',lock=True)

        if not self.isReferenced():
            if self.__justCreatedState__ or doVerify:
                if not self.__verify__():
                    raise StandardError,"Failed!"

    ##@r9General.Timer
    def __verify__(self):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
        #if log.getEffectiveLevel() == 10:log.debug(">"*10 + " cgmInfoNode.verify.... " + "<"*10)
        #See if it's named properly. Need to loop back after scene stuff is querying properly
        self.doName()  
        return True


    def __bindData__(self):
        pass

class cgmMasterControl(cgmMeta.cgmObject):
    """
    Make a master control curve
    """
    def __init__(self,*args,**kws):
        """Constructor"""				
        #>>>Keyword args
        super(cgmMasterControl, self).__init__(*args,**kws)
        
        #====================================================================================	
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            log.debug('CACHE : Aborting __init__ on pre-cached {0} Object'.format(self))
            return
        #====================================================================================
        
        doVerify = kws.get('doVerify') or False

        if self.__justCreatedState__ or doVerify:
            if not self.__verify__(*args,**kws):
                raise StandardError,"Failed to verify!"	

    @cgmGEN.Timer
    def __verify__(self,*args,**kws):
        puppet = kws.pop('puppet',False)
        if puppet and not self.isReferenced():
            ATTR.copy_to(puppet.mNode,'cgmName',self.mNode,driven='target')
            self.connectParentNode(puppet,'puppet','masterControl')
        else:
            self.addAttr('cgmName','MasterControl')

        #Check for shapes, if not, build
        self.color =  modules.returnSettingsData('colorMaster',True)

        #>>> Attributes
        if kws and 'name' in kws.keys():
            self.addAttr('cgmName', kws.get('name'), attrType = 'string')

        self.addAttr('cgmType','controlMaster',attrType = 'string')
        #self.addAttr('axisAim',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=2, keyable = False, hidden=True)
        #self.addAttr('axisUp',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=1, keyable = False, hidden=True)
        #self.addAttr('axisOut',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=0, keyable = False, hidden=True)
        #self.addAttr('setRO',attrType = 'enum', enumName= 'xyz:yzx:zxy:xzy:yxz:zyx',initialValue=0, keyable = True, hidden=False)
        #attributes.doConnectAttr('%s.setRO'%self.mNode,'%s.rotateOrder'%self.mNode,True)

        self.addAttr('controlVis', attrType = 'messageSimple',lock=True)
        self.addAttr('visControl', attrType = 'bool',keyable = False,initialValue= 1)

        self.addAttr('controlSettings', attrType = 'messageSimple',lock=True)
        self.addAttr('settingsControl', attrType = 'bool',keyable = False,initialValue= 1)

        #Connect and Lock the scale stuff
        attributes.doConnectAttr(('%s.scaleY'%self.mNode),('%s.scaleX'%self.mNode),True)
        attributes.doConnectAttr(('%s.scaleY'%self.mNode),('%s.scaleZ'%self.mNode),True)
        cgmMeta.cgmAttr(self,'scaleX',lock=True,hidden=True)
        cgmMeta.cgmAttr(self,'scaleZ',lock=True,hidden=True)
        yAttr = cgmMeta.cgmAttr(self,'scaleY')
        yAttr.p_nameAlias = 'masterScale'
        
        #=====================================================================
        #>>> Curves!
        #=====================================================================
        #>>> Master curves
        _shapes = self.getShapes()
        if len(_shapes)<3:
            self.rebuildControlCurve(**kws)
        #======================
        _size = DIST.get_bb_size(self.mNode,True,True)
        _controlVis = self.getMessage('controlVis')
        _controlSettings = self.getMessage('controlSettings')
        
        if not _controlVis or not _controlSettings:
            _d = {'controlVis':['eye',-45,'visControl'],
                  'controlSettings':['gear',45,'settingsControl']}
            _distance = _size *.4
            _subSize = _size *.15
            mLoc = self.doLoc()
            
            for k in _d.keys():
                mCrv = cgmMeta.validateObjArg(CURVES.create_fromName(_d[k][0],_subSize,'y+'),'cgmObject',setClass=True)
                mLoc.ry = _d[k][1]
                mCrv.p_position = mLoc.getPositionByAxisDistance('z+',_distance)
                mCrv.p_parent = self.mNode

                mCrv.rename(_d[k][2])
                
                ATTR.set_standardFlags(mCrv.mNode)
                RIG.override_color(mCrv.mNode,'yellowBright')                

                ATTR.connect("{0}.{1}".format(self.mNode,_d[k][2]),"{0}.v".format(mCrv.mNode))
                
                if k == 'controlVis':
                    mCrv.addAttr('controls',attrType = 'bool',keyable = False, initialValue = 1)
                    mCrv.addAttr('subControls',attrType = 'bool',keyable = False, initialValue = 1)
                    
                    self.controlVis = mCrv.mNode
                    
                elif k == 'controlSettings':
                    self.controlSettings = mCrv.mNode
                
            mLoc.delete()
                
        """
        #>>> Sub controls
        if not self.getMessage('controlVis'):
            buffer = controlBuilder.childControlMaker(self.mNode, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 135, controls = ['controlVisibility'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
            i_c = cgmMeta.cgmObject(buffer.get('controlVisibility'))
            i_c.addAttr('mClass','cgmObject')
            i_c.doName()	
            curves.setCurveColorByName(i_c.mNode,self.color[0])#Set the color
            self.controlVis = i_c.mNode #Link it

            attributes.doConnectAttr(('%s.visControl'%self.mNode),('%s.v'%i_c.mNode),True)

            #Vis control attrs
            self.controlVis.addAttr('controls', attrType = 'bool',keyable = False,initialValue= 1)
            self.controlVis.addAttr('subControls', attrType = 'bool',keyable = False,initialValue= 1)
            
        #>>> Settings Control
        if not self.getMessage('controlSettings'):
            buffer = controlBuilder.childControlMaker(self.mNode, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 225, controls = ['controlSettings'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
            i_c = cgmMeta.validateObjArg(buffer.get('controlSettings'),'cgmObject',setClass = True)
            i_c.doName()	
            curves.setCurveColorByName(i_c.mNode,self.color[0])#Set the color	    
            self.controlSettings = i_c.mNode #Link it	

            attributes.doConnectAttr(('%s.settingsControl'%self.mNode),('%s.v'%i_c.mNode),True)"""
        self.doName()


        return True

    ##@r9General.Timer
    def rebuildControlCurve(self, size = None,font = None,**kws):
        """
        Rebuild the master control curve
        """
        l_shapes = self.getShapes()
        self.color =  modules.returnSettingsData('colorMaster',True)
        
        #>>> Figure out the control size 	
        if size == None:#
            if l_shapes:
                size = DIST.get_bb_size(self.mNode,True,True)
            else:
                size = 10
        #>>> Figure out font	
        if font == None:#
            if kws and 'font' in kws.keys():font = kws.get('font')		
            else:font = 'arial'
            
        #>>> Delete shapes
        if l_shapes:
            mc.delete(l_shapes)

        #>>> Build the new
        mCrv = cgmMeta.validateObjArg(CURVES.create_fromName('masterAnim',size,'z+'),'cgmObject',setClass=True)
        RIG.shapeParent_in_place(self.mNode,mCrv.mNode,keepSource=False)       
        l_shapes = self.getShapes(fullPath=True)
        RIG.override_color(l_shapes[0],'yellow')
        RIG.override_color(l_shapes[1],'white')        
        
        #i_o = cgmMeta.cgmObject( curves.createControlCurve('masterAnim',size))#Create and initialize
        #curves.setCurveColorByName( i_o.mNode,self.color[0] )
        #curves.setCurveColorByName( i_o.getShapes()[1],self.color[1] )

        #>>> Build the text curve if cgmName exists
        if self.hasAttr('cgmName'):
            nameSize = DIST.get_bb_size(l_shapes[1],True,True)
            log.info(l_shapes[1])
            log.info(nameSize)
            _textCurve = CURVES.create_text(self.cgmName, size = nameSize * .8, font = font)
            ATTR.set(_textCurve,'rx',-90)
            RIG.override_color(_textCurve,'yellow')
            RIG.shapeParent_in_place(self.mNode,_textCurve,keepSource=False)
            
            """rootShapes = i_o.getShapes()#Get the shapes
            nameScaleBuffer = distance.returnAbsoluteSizeCurve(rootShapes[1])#Get the scale
            nameScale = max(nameScaleBuffer) * .8#Get the new scale
            masterText = curves.createTextCurveObject(self.cgmName,size=nameScale,font=font)
            curves.setCurveColorByName(masterText,self.color[0])#Set the color
            mc.setAttr((masterText+'.rx'), -90)#Rotate the curve
            curves.parentShapeInPlace(self.mNode,masterText)#Shape parent it
            mc.delete(masterText)"""


        self.doName()    


class cgmMasterControlOLD(cgmMeta.cgmObject):
    """
    Make a master control curve
    """
    def __init__(self,*args,**kws):
        """Constructor"""				
        #>>>Keyword args
        super(cgmMasterControl, self).__init__(*args,**kws)
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================	

        #====================================================================================
        #if log.getEffectiveLevel() == 10:log.debug(">>> cgmMasterControl.__init__")
        #if kws:log.debug("kws: %s"%str(kws))
        #if args:log.debug("args: %s"%str(args)) 	
        doVerify = kws.get('doVerify') or False

        if not self.isReferenced():
            if self.__justCreatedState__ or doVerify:
                if not self.__verify__(*args,**kws):
                    raise StandardError,"Failed!"	

    @cgmGEN.Timer
    def __verify__(self,*args,**kws):
        puppet = kws.pop('puppet',False)
        if puppet and not self.isReferenced():
            #if log.getEffectiveLevel() == 10:log.debug("Puppet provided!")
            #if log.getEffectiveLevel() == 10:log.debug(puppet.cgmName)
            #if log.getEffectiveLevel() == 10:log.debug(puppet.mNode)
            #self.doStore('cgmName',puppet.mNode+'.cgmName')
            ATTR.copy_to(puppet.mNode,'cgmName',self.mNode,driven='target')
            self.addAttr('puppet',attrType = 'messageSimple')
            self.connectParentNode(puppet,'puppet','masterControl') 	

        #Check for shapes, if not, build
        self.color =  modules.returnSettingsData('colorMaster',True)

        #>>> Attributes
        if kws and 'name' in kws.keys():
            self.addAttr('cgmName', kws.get('name'), attrType = 'string')

        self.addAttr('cgmType','controlMaster',attrType = 'string')
        self.addAttr('axisAim',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=2, keyable = False, hidden=True)
        self.addAttr('axisUp',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=1, keyable = False, hidden=True)
        self.addAttr('axisOut',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=0, keyable = False, hidden=True)
        self.addAttr('setRO',attrType = 'enum', enumName= 'xyz:yzx:zxy:xzy:yxz:zyx',initialValue=0, keyable = True, hidden=False)
        attributes.doConnectAttr('%s.setRO'%self.mNode,'%s.rotateOrder'%self.mNode,True)

        self.addAttr('controlVis', attrType = 'messageSimple',lock=True)
        self.addAttr('visControl', attrType = 'bool',keyable = False,initialValue= 1)

        self.addAttr('controlSettings', attrType = 'messageSimple',lock=True)
        self.addAttr('settingsControl', attrType = 'bool',keyable = False,initialValue= 1)

        #Connect and Lock the scale stuff
        attributes.doConnectAttr(('%s.scaleY'%self.mNode),('%s.scaleX'%self.mNode),True)
        attributes.doConnectAttr(('%s.scaleY'%self.mNode),('%s.scaleZ'%self.mNode),True)
        cgmMeta.cgmAttr(self,'scaleX',lock=True,hidden=True)
        cgmMeta.cgmAttr(self,'scaleZ',lock=True,hidden=True)
        yAttr = cgmMeta.cgmAttr(self,'scaleY')
        yAttr.p_nameAlias = 'masterScale'

        #=====================================================================
        #>>> Curves!
        #=====================================================================
        #>>> Master curves
        if not self.getShapes() or len(self.getShapes())<3:
            #if log.getEffectiveLevel() == 10:log.debug("Need to build shapes")
            self.rebuildControlCurve(**kws)

        #======================
        #>>> Sub controls
        visControl = attributes.returnMessageObject(self.mNode,'controlVis')
        if not mc.objExists( visControl ):
            #if log.getEffectiveLevel() == 10:log.debug('Creating visControl')
            buffer = controlBuilder.childControlMaker(self.mNode, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 135, controls = ['controlVisibility'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
            i_c = cgmMeta.cgmObject(buffer.get('controlVisibility'))
            i_c.addAttr('mClass','cgmObject')
            i_c.doName()	
            curves.setCurveColorByName(i_c.mNode,self.color[0])#Set the color
            self.controlVis = i_c.mNode #Link it

            attributes.doConnectAttr(('%s.visControl'%self.mNode),('%s.v'%i_c.mNode),True)

            #Vis control attrs
            self.controlVis.addAttr('controls', attrType = 'bool',keyable = False,initialValue= 1)
            self.controlVis.addAttr('subControls', attrType = 'bool',keyable = False,initialValue= 1)
            #>>> Settings Control
            settingsControl = attributes.returnMessageObject(self.mNode,'controlSettings')

            if not mc.objExists( settingsControl ):
                #if log.getEffectiveLevel() == 10:log.debug('Creating settingsControl')
                buffer = controlBuilder.childControlMaker(self.mNode, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 225, controls = ['controlSettings'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
                i_c = cgmMeta.validateObjArg(buffer.get('controlSettings'),'cgmObject',setClass = True)
                i_c.doName()	
                curves.setCurveColorByName(i_c.mNode,self.color[0])#Set the color	    
                self.controlSettings = i_c.mNode #Link it	

                attributes.doConnectAttr(('%s.settingsControl'%self.mNode),('%s.v'%i_c.mNode),True)
        self.doName()


        return True

    ##@r9General.Timer
    def rebuildControlCurve(self, size = None,font = None,**kws):
        """
        Rebuild the master control curve
        """
        #if log.getEffectiveLevel() == 10:log.debug('>>> rebuildControlCurve')
        ml_shapes = cgmMeta.validateObjListArg( self.getShapes(),noneValid=True )
        self.color =  modules.returnSettingsData('colorMaster',True)

        #>>> Figure out the control size 	
        if size == None:#
            if ml_shapes:
                absSize =  distance.returnAbsoluteSizeCurve(self.mNode)
                size = max(absSize)
            else:size = 125
        #>>> Figure out font	
        if font == None:#
            if kws and 'font' in kws.keys():font = kws.get('font')		
            else:font = 'arial'
        #>>> Delete shapes
        if ml_shapes:
            for s in ml_shapes:s.delete()	

        #>>> Build the new
        i_o = cgmMeta.cgmObject( curves.createControlCurve('masterAnim',size))#Create and initialize
        curves.setCurveColorByName( i_o.mNode,self.color[0] )
        curves.setCurveColorByName( i_o.getShapes()[1],self.color[1] )

        #>>> Build the text curve if cgmName exists
        if self.hasAttr('cgmName'):
            rootShapes = i_o.getShapes()#Get the shapes
            nameScaleBuffer = distance.returnAbsoluteSizeCurve(rootShapes[1])#Get the scale
            nameScale = max(nameScaleBuffer) * .8#Get the new scale
            masterText = curves.createTextCurveObject(self.cgmName,size=nameScale,font=font)
            curves.setCurveColorByName(masterText,self.color[0])#Set the color
            mc.setAttr((masterText+'.rx'), -90)#Rotate the curve
            curves.parentShapeInPlace(self.mNode,masterText)#Shape parent it
            mc.delete(masterText)

        #>>>Shape parent it
        curves.parentShapeInPlace(self.mNode,i_o.mNode)
        mc.delete(i_o.mNode)

        self.doName()    

class cgmModuleBufferNode(cgmMeta.cgmBufferNode):
    """"""
    ##@r9General.Timer    
    def __init__(self,node = None, name = None ,initializeOnly = False,*args,**kws):
        #DO NOT PUT A DEFAULT NAME IN THE DEFINITION...RECURSIVE HELL
        #if log.getEffectiveLevel() == 10:log.debug(">>> cgmModuleBufferNode.__init__")
        #if kws:log.debug("kws: %s"%kws)    

        """Constructor"""
        module = kws.get('module') or False
        bufferType = kws.get('bufferType') or ''
        doVerify = kws.get('doVerify') or False

        #>>> Keyword args
        super(cgmModuleBufferNode, self).__init__(node=node, name = name,*args,**kws)
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================	

        #====================================================================================	
        #if log.getEffectiveLevel() == 10:log.debug(">"*10 + " cgmModuleBufferNode.init.... " + "<"*10)
        #if log.getEffectiveLevel() == 10:log.debug(args)
        #if log.getEffectiveLevel() == 10:log.debug(kws)        

        if not self.isReferenced(): 
            if self.__justCreatedState__ or doVerify:	    
                if not self.__verify__(**kws):
                    raise StandardError,"Failed!"

    ##@r9General.Timer
    def __verify__(self,*args,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """ 
        _str_func = "cgmModuleBufferNode.__verify__(%s)"%(self.p_nameShort)
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)  

        cgmMeta.cgmBufferNode.__verify__(self,**kws)

        module = kws.get('module') or False
        bufferType = kws.get('bufferType') or ''

        #>>> Buffer type set    
        if bufferType == '':
            if self.hasAttr('cgmTypeModifier'):
                bufferType = self.cgmTypeModifier
            else:
                bufferType = 'cgmBuffer'   

        #>>> Attr check    
        self.addAttr('cgmName', attrType = 'string', initialValue = '',lock=True)
        #self.addAttr('cgmTypeModifier',initialValue = bufferType,lock=True)
        self.addAttr('cgmType','cgmBuffer',lock=True)
        self.addAttr('module',attrType = 'messageSimple')

        #>>> Module stuff   
        if module:
            try:
                module = module.mNode
            except:
                module = module
            self.connectParentNode(module,'module',bufferType) 

        if self.getMessage('module'):
            self.doStore('cgmName',self.getMessage('module',False)[0])#not long name
            #self.doStore('cgmName',self.getMessage('module',False)[0],overideMessageCheck = True)#not long name
        self.doName()       
        #self.doName(**kws)  
        return True

    def __bindData__(self):
        pass



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# MODULE Base class
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
"""
InfoNullsNames = ['settings',
                  'setupOptions',
                  'templatePosObjects',
                  'visibilityOptions',
                  'templateControlObjects',
                  'coreNames',
                  'templateStarterData',
                  'templateControlObjectsData',
                  'skinJoints',
                  'rotateOrders']"""

moduleStates = ['define','template','deform','rig']

initLists = []
initDicts = ['infoNulls','parentTagDict']
initStores = ['ModuleNull','refState']
initNones = ['refPrefix','moduleClass']

defaultSettings = {'partType':'none'}
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
moduleNulls_toMake = 'rig','template' #These will be created and connected to a module and parented under them    
#moduleBuffers_toMake = ['coreNames']

rigNullAttrs_toMake = {'version':'string',#Attributes to be initialzed for any module
                       #'fk':'bool',
                       #'ik':'bool',
                       'gutsLock':'int',
                       'gutsVis':'int',                       
                       #'skinJoints':'message',
                       'dynSwitch':'messageSimple'}

templateNullAttrs_toMake = {'version':'string',
                            'gutsLock':'int',
                            'gutsVis':'int',
                            'controlsVis':'int',
                            'controlsLock':'int',
                            'root':'messageSimple',#The module root                            
                            'handles':'int',                            
                            'templateStarterData':'string',#this will be a json dict
                            'controlObjectTemplatePose':'string'}

class cgmModule(cgmMeta.cgmObject):
    ##@r9General.Timer
    def __init__(self,*args,**kws):
        """ 
        Intializes an module master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored

        Naming and template tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        """
        #if log.getEffectiveLevel() == 10:log.debug(">>> cgmModule.__init__")
        #if kws:log.debug("kws: %s"%str(kws))         
        #if args:log.debug("args: %s"%str(args))            

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Figure out the node
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>          
        ##If a node is provided, use it
        ##If a name is provided, see if there's node for it
        ##If nothing is provided, just make one     


        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Verify or Initialize
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
        super(cgmModule, self).__init__(*args,**kws) 

        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        log.debug("cgmModule.__init__ ...")	
        #====================================================================================	
        #self.UNMANAGED.extend(['_UTILS','kw_name','kw_moduleParent','kw_forceNew','kw_initializeOnly', 'kw_handles','kw_rollJoints','kw_callNameTags'])	
        for a in '_UTILS','kw_name','kw_moduleParent','kw_forceNew','kw_initializeOnly','kw_handles','kw_rollJoints','kw_callNameTags':
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a)  		
        self._UTILS = mFactory

        #====================================================================================
        #Keywords - need to set after the super call
        #==============         
        doVerify = kws.get('doVerify') or False
        self.kw_name= kws.get('name') or False        
        self.kw_moduleParent = kws.get('moduleParent') or False
        self.kw_forceNew = kws.get('forceNew') or False
        self.kw_initializeOnly = kws.get('initializeOnly') or False  
        self.kw_handles = kws.get('handles') or 1 # can't have 0 handles  
        self.kw_rollJoints = kws.get('rollJoints') or 0 # can't have 0 handles  


        self.kw_callNameTags = {'cgmPosition':kws.get('position') or False, 
                                'cgmDirection':kws.get('direction') or False, 
                                'cgmDirectionModifier':kws.get('directionModifier') or False,
                                'cgmNameModifier':kws.get('nameModifier') or False}

        #>>> Initialization Procedure ================== 
        if not self.isReferenced():
            if self.__justCreatedState__ or doVerify:	    
                if not self.__verify__(**kws):
                    log.critical("'%s' failed to verify!"%self.mNode)
                    raise StandardError,"'%s' failed to verify!"%self.mNode 
                return

        #if not self.initialize():
            #log.critical("'%s' failed to initialize. Please go back to the non referenced file to repair!"%self.mNode)
            #raise StandardError,"'%s' failed to initialize!"%self.mNode

    ##@r9General.Timer
    #def atMFactory(self,func,*args,**kws):
        #kws['mModule'] = self	
        #return mFactory.__dict__[func](self,*args,**kws)
    
    def atFactory(self, func = 'getState', *args,**kws):
        """
        Function to call a self function by string. For menus and other reasons
        """
        _str_func = 'atFactory'
        _short = self.p_nameShort
        _res = None
        if not args:
            _str_args = ''
            args = [self]
        else:
            _str_args = ','.join(str(a) for a in args) + ','
            args = [self] + [a for a in args]

        if not kws:
            kws = {}
            _kwString = ''  
        else:
            _l = []
            for k,v in kws.iteritems():
                _l.append("{0}={1}".format(k,v))
            _kwString = ','.join(_l)  
        try:
            log.debug("|{0}| >> On: {1}".format(_str_func,_short))     
            log.debug("|{0}| >> {1}.{2}({3}{4})...".format(_str_func,_short,func,_str_args,_kwString))                                    
            _res = getattr(mFactory,func)(*args,**kws)
        except Exception,err:
            log.error(cgmGEN._str_hardLine)
            log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
            log.error("Node: {0} | func: {1}".format(_short,func))            
            if args:
                log.error("Args...")
                for a in args:
                    log.error("      {0}".format(a))
            if kws:
                log.error(" KWS...".format(_str_func))
                for k,v in kws.iteritems():
                    log.error("      {0} : {1}".format(k,v))   
            log.error("Errors...")
            for a in err.args:
                log.error(a)
            log.error(cgmGEN._str_subLine)
            raise Exception,err
        return _res
    def initialize(self,**kws):
        """ 
        Initializes the various components a moduleNull for a character/asset.

        RETURNS:
        success(bool)
        """  
        _str_func = "cgmModule.initialize(%s)"%(self.p_nameShort)
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)  	
        #Puppet Network Node
        #==============
        if not issubclass(type(self),cgmModule):
            log.error("'%s' is cgmModule"%(self.mNode))
            return False

        for attr in moduleBuffers_toMake:
            #if log.getEffectiveLevel() == 10:log.debug("checking: %s"%attr)
            Attr = 'i_' + attr#Get a better attribute store string   
            obj = attributes.returnMessageObject(self.mNode,attr)# Find the object
            if not obj:return False

        return True # Experimetning, Don't know that we need to check this stuff as it's for changing info, not to be used in process

    def __verify__(self,**kws):
        """"""
        """ 
        Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

        RETURNS:
        success(bool)
        """
        _str_func = "cgmModule.__verify__(%s)"%(self.p_nameShort)      
        self.addAttr('mClass', initialValue='cgmModule',lock=True) 
        self.addAttr('cgmType',value = 'module',lock=True)

        if self.kw_name:#If we have a name, store it
            self.addAttr('cgmName',self.kw_name,attrType='string',lock=True)
        elif 'mType' in kws.keys():
            self.addAttr('cgmName',kws['mType'],attrType='string',lock=True)	    

        if attributes.doGetAttr(self.mNode,'cgmType') != 'module':
            log.error("'%s' is not a module. It's mClass is '%s'"%(self.mNode, attributes.doGetAttr(self.mNode,'mClass')))
            return False

        #Store tags from init call
        #==============  
        for k in self.kw_callNameTags.keys():
            if self.kw_callNameTags.get(k):
                self.addAttr(k,value = self.kw_callNameTags.get(k),lock = True)
        self.doName()  

        #Attributes
        #==============  
        self.addAttr('moduleType',initialValue = 'base',lock=True)

        self.addAttr('moduleParent',attrType='messageSimple')#Changed to message for now till Mark decides if we can use single
        self.addAttr('modulePuppet',attrType='messageSimple')
        self.addAttr('moduleChildren',attrType='message')

        stateDict = {'templateState':0,'rigState':0,'skeletonState':0} #Initial dict
        self.addAttr('moduleStates',attrType = 'string', initialValue=stateDict, lock = True)

        self.addAttr('rigNull',attrType='messageSimple',lock=True)
        self.addAttr('templateNull',attrType='messageSimple',lock=True)
        self.addAttr('deformNull',attrType='messageSimple',lock=True)	
        self.addAttr('coreNames',attrType='messageSimple',lock=True)

        #if log.getEffectiveLevel() == 10:log.debug("Module null good...")
        #>>> Rig/Template Nulls ==================   

        #Initialization
        #==============      
        for attr in moduleNulls_toMake:
            grp = attributes.returnMessageObject(self.mNode,attr+'Null')# Find the group
            Attr = 'i_' + attr+'Null'#Get a better attribute store string           
            if mc.objExists( grp ):
                try:     
                    self.__dict__[Attr] = r9Meta.MetaClass(grp)#Initialize if exists  
                except:
                    log.error("'%s' group failed. Please verify puppet."%attr)                    
                    return False   

            else:#Make it
                self.__dict__[Attr]= cgmMeta.cgmObject(name=attr)#Create and initialize
                self.__dict__[Attr].connectParentNode(self.mNode,'module', attr+'Null')                
                self.__dict__[Attr].addAttr('cgmType',attr+'Null',lock=True)

            self.__dict__[Attr].doParent(self.mNode)
            self.__dict__[Attr].doName()

            attributes.doSetLockHideKeyableAttr( self.__dict__[Attr].mNode )

        """for attr in moduleBuffers_toMake:
            obj = attributes.returnMessageObject(self.mNode,attr)# Find the object
            Attr = 'i_' + attr#Get a better attribute store string           
            if mc.objExists( obj ):
                try:     
                    self.__dict__[Attr]  = r9Meta.MetaClass(obj)#Initialize if exists  
                except:
                    log.error("'%s' null failed. Please verify modules."%attr)                    
                    return False               
            else:#Make it
                self.__dict__[Attr]= cgmModuleBufferNode(module = self, name = attr, bufferType = attr, overideMessageCheck = True)#Create and initialize
            self.__dict__[Attr].__verify__()"""

        #Attrbute checking
        #=================
        self.__verifyAttributesOn__(self.i_rigNull,rigNullAttrs_toMake)
        self.__verifyAttributesOn__(self.i_templateNull,templateNullAttrs_toMake)

        #Set Module Parent if we have that kw
        #=================		
        if self.kw_moduleParent:
            self.doSetParentModule(self.kw_moduleParent)

        return True

    #@cgmGEN.Timer
    def __verifyAttributesOn__(self,null,dictToUse):
        #Attrbute checking
        #=================
        if type(dictToUse) is not dict:
            raise StandardError,"Not a dict: %s"%null
        i_null = cgmMeta.asMeta(null)
        if not i_null:
            raise StandardError,"Not a valid object: %s"%dictToUse	

        for attr in sorted(dictToUse.keys()):#See table just above cgmModule
            try:
                #if log.getEffectiveLevel() == 10:log.debug("Checking '%s' on template Null"%attr)	
                if attr == 'rollJoints':
                    #if log.getEffectiveLevel() == 10:log.debug("rollJoints: %s"%self.kw_rollJoints)
                    if self.kw_rollJoints == 0:
                        i_null.addAttr(attr,initialValue = self.kw_rollJoints, attrType = dictToUse[attr],lock = True )                
                    else:
                        i_null.addAttr(attr,initialValue = self.kw_rollJoints, attrType = dictToUse[attr],lock = True )                		    	    
                elif attr == 'handles':
                    if self.kw_handles == 1:
                        i_null.addAttr(attr,initialValue = self.kw_handles, attrType = dictToUse[attr],lock = True,min = 1 )                
                    else:
                        i_null.addAttr(attr,initialValue = self.kw_handles, attrType = dictToUse[attr],lock = True,min = 1 )                
                elif attr == 'rollOverride':
                    i_null.addAttr(attr,initialValue = '{}', attrType = dictToUse[attr],lock = True )                                
                else:
                    i_null.addAttr(attr,attrType = dictToUse[attr],lock = True )   
            except Exception,error:
                log.error(">>> %s.%s >> failed: %s"%(self.p_nameShort,attr,error))     

    def __verifyObjectSet__(self):
        _str_func = "__verifyObjectSet__(%s)"%self.p_nameShort
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)		
        try:#Quick select sets ================================================================
            if not self.rigNull.getMessage('moduleSet'):#
                i_selectSet = cgmMeta.cgmObjectSet(setType='animSet',qssState=True)
                i_selectSet.connectParentNode(self.rigNull.mNode,'rigNull','moduleSet')

            i_selectSet = self.rigNull.moduleSet
            i_selectSet.doStore('cgmName',self)
            i_selectSet.doName()

            if self.getMessage('modulePuppet'):
                mi_modulePuppet = self.modulePuppet
                if not mi_modulePuppet.getMessage('puppetSet'):
                    mi_modulePuppet.__verifyObjectSet__()
                try:self.modulePuppet.puppetSet.addObj(i_selectSet.mNode)
                except Exception,error:raise Exception,"Failed to add to puppetSet | error: {0}".format(error)

        except Exception,error:
            raise StandardError,"%s >>> ObjectSet | error : %s"%(_str_func,error)

    def getModuleColors(self):
        direction = search.returnTagInfo(self.mNode,'cgmDirection')
        if not direction:
            return modules.returnSettingsData('colorCenter',True)
        else:
            return modules.returnSettingsData(('color'+direction.capitalize()),True)

    def getPartNameBase(self):
        return nameTools.returnRawGeneratedName(self.mNode, ignore = ['cgmType'])

    def getSettingsControl(self):
        """
        Call to figure out a module's settings control
        """
        _str_func = "getSettingsControl(%s)"%self.p_nameShort
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)  
        mi_rigNull = self.rigNull#Link
        try:
            return mi_rigNull.settings#fastest check
        except:log.debug("%s >>> No settings connected. Probably not rigged, so let's check ..."%_str_func)
        if self.moduleType in __l_faceModuleTypes__:
            #if log.getEffectiveLevel() == 10:log.debug("%s >>> Face module..."%_str_func)
            try:return self.moduleParent.rigNull.settings#fastest check
            except:log.debug("%s >>> No moduleParent settings connected..."%_str_func)	    
            try:return self.modulePuppet.masterControl.controlSettings#fastest check
            except:log.debug("%s >>> No masterControl settings found..."%_str_func)	    

        log.error("%s >>> Unable to find settings control."%(_str_func))
        return False

    def doSetParentModule(self,*args,**kws):
        """
        Set a module parent of a module

        module(string)
        """
        kws['mModule'] = self
        mFactory.doSetParentModule(*args,**kws)

    def getGeneratedCoreNames(self,*args,**kws):
        return mFactory.getGeneratedCoreNames(self,*args,**kws)

    def isModule(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isModule)
        """
        return mFactory.isModule(self,**kws)

    def get_mirrorSideAsString(self,*args,**kws):
        kws['mModule'] = self	
        return mFactory.get_mirrorSideAsString(*args,**kws) 

    def get_moduleSiblings(self,*args,**kws):
        kws['mModule'] = self	
        return mFactory.get_moduleSiblings(*args,**kws)   

    #>>> States
    #===========================================================
    def getState(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.getState)
        """
        kws['mModule'] = self	
        return mFactory.getState(*args,**kws)

    def setState(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.setState)
        """
        kws['mModule'] = self	
        return mFactory.setState(*args,**kws)

    def stateCheck(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.checkState)
        """
        kws['mModule'] = self	
        return mFactory.checkState(*args,**kws)	

    #>>> Sizing
    #===========================================================
    def doSize(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doSize)
        """
        kws['mModule'] = self	
        return mFactory.doSize(*args,**kws)
    def isSized(self,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isSized)
        """
        kws['mModule'] = self	
        return mFactory.isSized(**kws)  

    #>>> Templates
    #===========================================================    
    def isTemplated(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isTemplated)
        """
        kws['mModule'] = self	
        return mFactory.isTemplated(*args,**kws)

    def template_update(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.template_update)
        """
        kws['mModule'] = self	
        return mFactory.template_update(*args,**kws) 

    def templateSettings_call(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.template_call)
        """
        kws['mModule'] = self	
        return mFactory.templateSettings_call(*args,**kws) 

    def doTemplate(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doTemplate)
        """
        kws['mModule'] = self	
        return mFactory.doTemplate(*args,**kws)

    def deleteTemplate(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.deleteTemplate)
        """
        kws['mModule'] = self	
        return mFactory.deleteTemplate(*args,**kws) 


    #>>> Skeletonize
    #===========================================================  
    def isSkeletonized(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isSkeletonized)
        """
        kws['mModule'] = self	
        return mFactory.isSkeletonized(*args,**kws)

    def doSkeletonize(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doSkeletonize)
        """
        kws['mModule'] = self		
        return mFactory.doSkeletonize(*args,**kws)

    def skeletonDelete(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.deleteSkeleton)
        """
        kws['mModule'] = self	
        return mFactory.deleteSkeleton(*args,**kws)

    #>>> Rig
    #===========================================================
    def doRig(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.doRig)
        """
        kws['mModule'] = self	
        return mFactory.doRig(*args,**kws)

    def isRigged(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isRigged)
        """
        kws['mModule'] = self	
        return mFactory.isRigged(*args,**kws)  

    def isRigConnected(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.isRigConnected)
        """
        kws['mModule'] = self	
        return mFactory.isRigConnected(*args,**kws)  

    def rigConnect(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rigConnect)
        """
        kws['mModule'] = self	
        return mFactory.rigConnect(*args,**kws) 

    def rigDisconnect(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rigDisconnect)
        """
        kws['mModule'] = self	
        return mFactory.rigDisconnect(*args,**kws)  

    def rigDelete(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rigDisconnect)
        """
        kws['mModule'] = self	
        return mFactory.rigDelete(*args,**kws)     

    def rig_getReport(self):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rig_getReport)
        """
        return mFactory.rig_getReport(self)  

    def rig_getSkinJoints(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rig_getSkinJoints)
        """
        kws['mModule'] = self	
        return mFactory.rig_getSkinJoints(*args,**kws)  

    def rig_getHandleJoints(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rig_getHandleJoints)
        """
        kws['mModule'] = self	
        return mFactory.rig_getHandleJoints(*args,**kws)

    def rig_getRigHandleJoints(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.rig_getRigHandleJoints)
        """
        kws['mModule'] = self	
        return mFactory.rig_getRigHandleJoints(*args,**kws)      

    def get_rollJointCountList(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.get_rollJointCountList)
        """
        kws['mModule'] = self	
        return mFactory.get_rollJointCountList(*args,**kws)  

    def get_controls(self,*args,**kws):
        """
        from cgm.core.rigger import ModuleFactory as mFactory
        help(mFactory.get_controls)
        """
        kws['mModule'] = self	
        return mFactory.get_controls(*args,**kws)

    def puppetSettings_setAttr(self,*args,**kws):
        kws['mModule'] = self			
        return mFactory.puppetSettings_setAttr(*args,**kws)

    #>>> Animation
    #========================================================================
    def animKey(self,**kws):
        try:

            _result = False
            _l_callSelection = mc.ls(sl=True) or []

            buffer = self.rigNull.moduleSet.getList()
            if buffer:
                mc.select(buffer)
                mc.setKeyframe(**kws)
                _result = True
            if _l_callSelection:mc.select(_l_callSelection)
            return _result
        except Exception,error:
            log.error("%s.animKey>> animKey fail | %s"%(self.getBaseName(),error))
            return False

    def animSelect(self,**kws):
        try:
            buffer = self.rigNull.moduleSet.getList()
            if buffer:
                mc.select(buffer)
                return True
            return False
        except Exception,error:
            log.error("%s.animSelect>> animSelect fail | %s"%(self.getBaseName(),error))
            return False

    def animReset(self,*args, **kws):
        kws['mModule'] = self		
        return mFactory.animReset(*args, **kws)
    def mirrorMe(self,*args,**kws):
        kws['mModule'] = self	
        return mFactory.mirrorMe(*args, **kws)

    def mirrorPush(self,**kws):
        kws['mModule'] = self	
        return mFactory.mirrorPush(**kws)
    def mirrorPull(self,**kws):
        kws['mModule'] = self	
        return mFactory.mirrorPull(**kws)
    def getMirror(self,**kws):
        kws['mModule'] = self	
        return mFactory.get_mirror(**kws)
    def mirrorLeft(self,**kws):
        kws['mModule'] = self	
        return mFactory.mirrorSymLeft(**kws)
    def mirrorRight(self,**kws):
        kws['mModule'] = self	
        return mFactory.mirrorSymRight(**kws)  
    def mirror_do(self,**kws):
        kws['mModule'] = self	
        return mFactory.mirror_do(**kws)      
    #>>> Module Children
    #========================================================================
    def get_allModuleChildren(self,*args,**kws):
        kws['mModule'] = self	
        return mFactory.get_allModuleChildren(*args,**kws) 

    def animReset_children(self,*args,**kws):
        kws['mModule'] = self		
        return mFactory.animReset_children(*args,**kws) 

    def animKey_children(self,*args,**kws):
        kws['mModule'] = self		
        return mFactory.animKey_children(*args,**kws)

    def animSelect_children(self,*args,**kws):
        kws['mModule'] = self		
        return mFactory.animSelect_children(*args,**kws)

    def dynSwitch_children(self,*args,**kws):
        kws['mModule'] = self		
        return mFactory.dynSwitch_children(*args,**kws)

    def animSetAttr_children(self,*args,**kws):
        kws['mModule'] = self			
        return mFactory.animSetAttr_children(*args,**kws)

    #>>> Module Siblings
    #========================================================================  
    def getModuleSiblings(self,*args,**kws):
        kws['mModule'] = self			
        return mFactory.get_moduleSiblings(*args,**kws) 

    def animReset_siblings(self,*args,**kws):
        kws['mModule'] = self				
        return mFactory.animReset_siblings(*args,**kws)  

    def mirrorMe_siblings(self,*args,**kws):
        kws['mModule'] = self				
        return mFactory.mirrorMe_siblings(*args,**kws)

    def mirrorPull_siblings(self,*args,**kws):
        kws['mModule'] = self				
        return mFactory.mirrorPull_siblings(*args,**kws)

    def mirrorPush_siblings(self,*args,**kws):
        kws['mModule'] = self				
        return mFactory.mirrorPush_siblings(*args,**kws) 

    def animPushPose_siblings(self,*args,**kws):
        kws['mModule'] = self				
        return mFactory.animPushPose_siblings(*args,**kws) 

    def animKey_siblings(self,*args,**kws):
        kws['mModule'] = self				
        return mFactory.animKey_siblings(*args,**kws)  

    def animSelect_siblings(self,*args,**kws):
        kws['mModule'] = self				
        return mFactory.animSelect_siblings(*args,**kws)  

    def dynSwitch_siblings(self,*args,**kws):
        kws['mModule'] = self				
        return mFactory.dynSwitch_siblings(*args,**kws)

    def get_joints(self,**kws):
        kws['mModule'] = self	
        return mFactory.get_joints(**kws)

    #>>> Toggles
    #========================================================================  
    def toggle_subVis(self,*args,**kws):
        kws['mModule'] = self					
        return mFactory.toggle_subVis(*args,**kws)   

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Limb stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
d_limb_rigNullAttrs_toMake = {'stretchy':'bool',
                              'bendy':'bool',
                              'twist':'bool'}

d_limb_templateNullAttrs_toMake = {'rollJoints':'int',#How many splits per segement
                                   'rollOverride':'string',#Override
                                   'curveDegree':'int',#Degree of the template curve, 0 for purely point to point curve
                                   'posObjects':'message',#Not 100% on this one
                                   'controlObjects':'message',#Controls for setting the template
                                   'curve':'messageSimple',#Module curve
                                   'orientHelpers':'messageSimple',#Orientation helper controls
                                   'orientRootHelper':'messageSimple',#Root orienation helper
                                   }

limbTypes = {'segment':{'handles':3,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'finger':{'handles':5,'rollOverride':'{"0":1}','curveDegree':0,'rollJoints':0},
             'clavicle':{'handles':1,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'arm':{'handles':3,'rollOverride':'{}','curveDegree':0,'rollJoints':3},
             'leg':{'handles':4,'rollOverride':'{}','curveDegree':2,'rollJoints':3},
             'legSimple':{'handles':3,'rollOverride':'{}','curveDegree':2,'rollJoints':3}, 
             'armSimple':{'handles':3,'rollOverride':'{}','curveDegree':2,'rollJoints':3},                          
             'torso':{'handles':5,'rollOverride':'{"-1":0,"0":0}','curveDegree':2,'rollJoints':2},
             'tail':{'handles':5,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'head':{'handles':1,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'neckHead':{'handles':2,'rollOverride':'{}','curveDegree':1,'rollJoints':3},
             'foot':{'handles':3,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'hand':{'handles':1,'rollOverride':'{}','curveDegree':0,'rollJoints':0},
             'thumb':{'handles':4,'rollOverride':'{}','curveDegree':1,'rollJoints':0}                          
             }

class cgmLimb(cgmModule):
    #@cgmGEN.Timer    
    def __init__(self,*args,**kws):
        """ 
        Intializes an module master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored

        mType(string) -- must be in cgm_PuppetMeta.limbTypes.keys()
        Naming and template tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        """
        #if log.getEffectiveLevel() == 10:log.debug(">>> cgmLimb.__init__")
        #if kws:log.debug("kws: %s"%str(kws))         
        #if args:log.debug("args: %s"%str(args))  

        start = time.clock()	

        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']

        super(cgmLimb, self).__init__(*args,**kws) 
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================

    def __verify__(self,**kws):
        cgmModule.__verify__(self,**kws)
        #super(cgmLimb,self).__verify(**kws)
        if 'mType' not in kws.keys() and self.moduleType in limbTypes.keys():
            #if log.getEffectiveLevel() == 10:log.debug("'%s' type checks out."%self.moduleType)	    
            moduleType = self.moduleType
        elif 'mType' in kws.keys():
            moduleType = kws['mType']
        elif 'name' in kws.keys():
            moduleType = kws['name']
        else:
            moduleType = kws.pop('mType','segment')	

        if not moduleType in limbTypes.keys():
            #if log.getEffectiveLevel() == 10:log.debug("'%s' type is unknown. Using segment type"%moduleType)
            moduleType = 'segment'

        if self.moduleType != moduleType:
            #if log.getEffectiveLevel() == 10:log.debug("Changing type to '%s' type"%moduleType)
            self.moduleType = moduleType

        #>>> Attributes ...
        self.__verifyAttributesOn__(self.i_rigNull,d_limb_rigNullAttrs_toMake)
        self.__verifyAttributesOn__(self.i_templateNull,d_limb_templateNullAttrs_toMake)

        settings = limbTypes[moduleType]
        if settings:
            for attr in settings.keys():
                self.templateNull.addAttr(attr, initialValue = settings[attr],lock = True) 

        return True

#>>> SimpleFace  =====================================================================================================
d_simpleFace_rigNullAttrs_toMake = {'gui_main':'messageSimple',
                                    'gui_cam':'messageSimple',
                                    #'jnt_jaw':'messageSimple',
                                    'geo_head':'messageSimple',                                    
                                    'geo_bridgeHead':'messageSimple',
                                    'geo_reset':'messageSimple',
                                    'bsNode_bridge':'messageSimple',                                    
                                    }

d_simpleFace_templateNullAttrs_toMake = {'rigBlock_eye_left':'messageSimple',
                                         'rigBlock_eye_right':'messageSimple',
                                         'rigBlock_face_lwr':'messageSimple',
                                         'rigBlock_face_upr':'messageSimple',                                         
                                         }

class cgmSimpleBSFace(cgmModule):
    def __init__(self,*args,**kws):
        """ 
        Intializes an simpleFace master class handler
        """
        _str_func = "cgmSimpleBSFace.__init__"    
        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']

        super(cgmSimpleBSFace, self).__init__(*args,**kws) 

        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================

    def __verify__(self,**kws):
        cgmModule.__verify__(self,**kws)

        self.moduleType = 'simpleFace'

        #>>> Attributes ...
        self.__verifyAttributesOn__(self.rigNull,d_simpleFace_rigNullAttrs_toMake)
        self.__verifyAttributesOn__(self.templateNull,d_simpleFace_templateNullAttrs_toMake)
        return True

#>>> Eyeball =====================================================================================================
d_eyeball_rigNullAttrs_toMake = {'irisControl':'bool',#Whether we should have a iris setup
                                 'pupilControl':'bool',#Whether we should have a pupil control
                                 }

d_eyeball_templateNullAttrs_toMake = {}

class cgmEyeball(cgmModule):
    #@cgmGEN.Timer    
    def __init__(self,*args,**kws):
        """ 
        Intializes an eyeball master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored

        mType(string) -- must be in cgm_PuppetMeta.limbTypes.keys()
        Naming and template tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        """
        _str_func = "cgmEyeball.__init__"    
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        #if kws:log.debug("%s >>> kws: %s"%(_str_func,str(kws)))         
        #if args:log.debug("%s >>> args: %s"%(_str_func,str(args))) 

        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']
        super(cgmEyeball, self).__init__(*args,**kws) 

        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================	

        #====================================================================================
    def __verify__(self,**kws):
        cgmModule.__verify__(self,**kws)
        moduleType = kws.pop('mType','eyeball')	

        self.moduleType = moduleType

        #>>> Attributes ...
        self.__verifyAttributesOn__(self.i_rigNull,d_eyeball_rigNullAttrs_toMake)
        self.__verifyAttributesOn__(self.i_templateNull,d_eyeball_templateNullAttrs_toMake)

        settings = {'handles': 1}
        if settings:
            for attr in settings.keys():
                self.templateNull.addAttr(attr, value = settings[attr],lock = True)   
        return True

#>>> Eyelids =====================================================================================================
d_eyelids_rigNullAttrs_toMake = {}
d_eyelids_templateNullAttrs_toMake = {}

class cgmEyelids(cgmModule):
    #@cgmGEN.Timer    
    def __init__(self,*args,**kws):
        """ 
        Intializes an eyelids master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored

        mType(string) -- must be in cgm_PuppetMeta.limbTypes.keys()
        Naming and template tags. All Default to False
        position(string) -- position tag
        direction(string) -- direction
        directionModifier(string)
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        """
        _str_func = "cgmEyelids.__init__"    
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        #if kws:log.debug("%s >>> kws: %s"%(_str_func,str(kws)))         
        #if args:log.debug("%s >>> args: %s"%(_str_func,str(args))) 

        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']
        super(cgmEyelids, self).__init__(*args,**kws) 
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================	

        #====================================================================================
    def __verify__(self,**kws):
        cgmModule.__verify__(self,**kws)
        moduleType = kws.pop('mType','eyelids')	

        self.moduleType = moduleType

        #>>> Attributes ...
        self.__verifyAttributesOn__(self.i_rigNull,d_eyelids_rigNullAttrs_toMake)
        self.__verifyAttributesOn__(self.i_templateNull,d_eyelids_templateNullAttrs_toMake)

        settings = {'handles': 5}
        if settings:
            for attr in settings.keys():
                self.templateNull.addAttr(attr, value = settings[attr],lock = True)   
        return True

#>>> Brow  =====================================================================================================
d_eyebrow_rigNullAttrs_toMake = {'templateControl':'bool',#Whether we should have a iris setup
                                 'uprCheekControl':'bool',#Whether we should have a pupil control
                                 }

d_eyebrow_templateNullAttrs_toMake = {}

class cgmEyebrow(cgmModule):
    def __init__(self,*args,**kws):
        """ 
        Intializes an brow master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored

        mType(string) -- must be in cgm_PuppetMeta.limbTypes.keys()
        Naming and template tags. All Default to False
        position(string) -- position tag
        nameModifier(string)
        forceNew(bool) --whether to force the creation of another if the object exists
        """
        _str_func = "cgmEyebrow.__init__"    
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        #if kws:log.debug("%s >>> kws: %s"%(_str_func,str(kws)))         
        #if args:log.debug("%s >>> args: %s"%(_str_func,str(args))) 

        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']
        super(cgmEyebrow, self).__init__(*args,**kws) 
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================
    def __verify__(self,**kws):
        cgmModule.__verify__(self,**kws)

        self.moduleType = 'eyebrow'

        #>>> Attributes ...
        self.__verifyAttributesOn__(self.i_rigNull,d_eyebrow_rigNullAttrs_toMake)
        self.__verifyAttributesOn__(self.i_templateNull,d_eyebrow_templateNullAttrs_toMake)

        settings = {'handles': 3}
        if settings:
            for attr in settings.keys():
                self.templateNull.addAttr(attr, value = settings[attr],lock = True)   
        return True

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Rig Blocks
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
d_rigBlockAttrs_toMake = {'version':'string',#Attributes to be initialzed for any block
                          #'buildAs':'string',
                          #'autoMirror':'bool',
                          #'direction':'none:left:right:center',
                          #'position':'none:front:back:upper:lower:forward',
                          'moduleTarget':'messageSimple',
                          'blockState':'string',
                          'blockDat':'string',
                          'blockMirror':'messageSimple'}

class cgmRigBlockOLD(cgmMeta.cgmControl):
    #These lists should be set up per rigblock as a way to get controls from message links
    _l_controlLinks = []
    _l_controlmsgLists = []

    def __init__(self,*args,**kws):
        """ 
        The root of the idea of cgmRigBlockOLD is to be a sizing mechanism and build options for
        our modular rigger.

        Args:
        node = existing module in scene
        name = treated as a base name

        """
        _str_func = "cgmRigBlockOLD.__init__"   
        log.debug("{0}...".format(_str_func))		
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        #if kws:log.debug("%s >>> kws: %s"%(_str_func,str(kws)))         
        #if args:log.debug("%s >>> args: %s"%(_str_func,str(args)))    

        #>>Verify or Initialize
        super(cgmRigBlockOLD, self).__init__(*args,**kws) 
        log.debug("{0} cache check...".format(_str_func))			
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        log.debug("{0} cache check fail...".format(_str_func))		

        #====================================================================================
        #Keywords - need to set after the super call
        #==============         
        __doVerify__ = kws.get('doVerify') or False

        #self.UNMANAGED.extend(['kw_name','kw_moduleParent','kw_forceNew','kw_initializeOnly','kw_callNameTags'])	
        for a in 'kw_name','kw_moduleParent','kw_forceNew','kw_initializeOnly','kw_callNameTags':
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a) 	
        self.kw_name= kws.get('name',False)        
        self.kw_moduleParent = kws.get('moduleParent',False)
        self.kw_forceNew = kws.get('forceNew',False)
        self.kw_initializeOnly = kws.get('initializeOnly',False)  
        self.kw_callNameTags = {'cgmPosition':kws.get('position',False), 
                                'cgmDirection':kws.get('direction',False), 
                                'cgmDirectionModifier':kws.get('directionModifier',False),
                                'cgmNameModifier':kws.get('nameModifier',False)}

        #>>> Initialization Procedure ================== 
        if not self.isReferenced():
            if self.__justCreatedState__ or __doVerify__:	
                log.debug("{0} verify...".format(_str_func))				
                if not self.__verify__(**kws):
                    log.critical("'%s' failed to verify!"%self.mNode)
                    raise StandardError,"'%s' failed to verify!"%self.mNode 
                return
        #if log.getEffectiveLevel() == 10:log.debug("'%s' Checks out!"%self.getShortName())

    def __verify__(self,**kws):
        """"""
        """ 
	Verifies the various components a puppet network for a character/asset. If a piece is missing it replaces it.

	RETURNS:
	success(bool)
	"""
        _str_func = "cgmRigBlockOLD.__verify__"    
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)

        if self.isReferenced():
            raise StandardError,"%s >>> is referenced. Cannot verify"%_str_func

        #>>> Block transform ==================                   
        self.addAttr('mClass', initialValue='cgmRigBlockOLD',lock=True) 
        #self.addAttr('cgmType',value = 'rigHelper',lock=True)	

        if self.kw_name:#If we have a name, store it
            self.addAttr('cgmName',self.kw_name,attrType='string',lock=True)
        elif 'buildAs' in kws.keys():
            self.addAttr('cgmName',kws['buildAs'],attrType='string',lock=True)	    

        #Store tags from init call
        #==============  
        for k in self.kw_callNameTags.keys():
            if self.kw_callNameTags.get(k):
                #if log.getEffectiveLevel() == 10:log.debug(k + " : " + str(self.kw_callNameTags.get(k)))                
                self.addAttr(k,value = self.kw_callNameTags.get(k),lock = True)
                #if log.getEffectiveLevel() == 10:log.debug(str(self.getNameDict()))
                #if log.getEffectiveLevel() == 10:log.debug(self.__dict__[k])


        #Attrbute checking
        #=================
        self.verifyAttrDict(d_rigBlockAttrs_toMake,keyable = False, hidden = False)
        #if log.getEffectiveLevel() == 10:log.debug("%s.__verify__ >>> kw_callNameTags: %s"%(self.p_nameShort,self.kw_callNameTags))	    	
        d_enumToCGMTag = {'cgmDirection':'direction','cgmPosition':'position'}
        for k in d_enumToCGMTag.keys():
            if k in self.kw_callNameTags.keys():
                try:self.__setattr__(d_enumToCGMTag.get(k),self.kw_callNameTags.get(k))
                except Exception,error: log.error("%s.__verify__ >>> Failed to set key: %s | data: %s | error: %s"%(self.p_nameShort,k,self.kw_callNameTags.get(k),error))

        self.doName()   

        return True

    def doName(self, *a, **kws):
        """
        Override to handle difference with rig block
        
        """
        _str_func = 'doName'
        
        #Get Raw name
        _d = nameTools.returnObjectGeneratedNameDict(self.mNode)
        
        for a in 'puppetName','baseName':
            if self.hasAttr(a):
                _d['cgmName'] = ATTR.get(self.mNode,a)
                
        _d['cgmTypeModifier'] = ATTR.get(self.mNode,'blockType')
        _d['cgmType'] = 'block'
        
        #Check for special attributes to replace data, name
        self.rename(nameTools.returnCombinedNameFromDict(_d))
        
    def __verifyModule__(self):
        """ 
        Verify
        """
        _str_func = "cgmRigBlockOLD.__verifyModule__"    
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)

        #First see if we have a module
        if not self.getMessage('moduleTarget'):
            #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> No module found. Building... "%(_str_func))
            self.__buildModule__()
        return True

    def __buildModule__(self):
        """
        General Module build before expected pass to individual blocks for specialization
        """	
        #>>> Gather basic info for module build
        d_kws = {}
        d_kws['name'] = self.cgmName
        #Direction
        str_direction = self.getEnumValueString('direction')
        if str_direction in ['left','right']:
            d_kws['direction'] = str_direction
        #Position
        str_position = self.getEnumValueString('position')	    
        if str_position != 'none':
            d_kws['position'] = str_position

        self._d_buildKWS = d_kws    

    def get_controls(self, asMeta = False):
        """
        Function which MUST be overloaded
        """	
        #>>> Gather basic info for module build
        _str_func = "{0}.get_controls() >> ".format(self.p_nameShort)
        if asMeta:
            _result = [self]
        else:
            _result = [self.mNode]
        for plug in self.__class__._l_controlLinks:
            if asMeta:
                _buffer = self.getMessageAsMeta(plug)
                if _buffer:
                    _result.append(_buffer)
            else:
                _buffer = self.getMessage(plug)
                if _buffer:
                    _result.extend(_buffer)
                else:
                    log.error("{2} Failed to find message on: {0}.{1}".format(self.p_nameShort,plug,_str_func))
        if not self.__class__._l_controlmsgLists:
            log.debug("{0} No msgList attrs registered".format(_str_func))
        else:
            for plug in self.__class__._l_controlmsgLists:
                _buffer = self.msgList_get(plug, asMeta = asMeta)
                if _buffer:
                    _result.extend(_buffer)
                else:
                    log.error("{2} Failed to find msgList on: {0}.{1}".format(self.p_nameShort,plug,_str_func))	    
        return _result

    def __buildSimplePuppet__(self):
        """
        Build a simple puppet for itself
        """
        _str_func = "cgmRigBlockOLD.__buildSimplePuppet__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        mi_module = self.moduleTarget
        if not mi_module:
            try:
                mi_module = self.__buildModule__()
            except Exception,error:
                raise StandardError, ">>> %s>>> module build failed. error: %s"%(_str_func,error)
        if mi_module.getMessage('modulePuppet'):
            return False

        mi_puppet = cgmPuppet(name = mi_module.getNameAlias())
        mi_puppet.connectModule(mi_module)	
        if mi_module.getMessage('moduleMirror'):
            mi_puppet.connectModule(mi_module.moduleMirror)
        mi_puppet.gatherModules()#Gather any modules in the chain
        return mi_puppet

    def __updateSizeData__(self):
        """For overload"""
        pass

class cgmEyeballBlock(cgmRigBlockOLD):
    d_attrsToMake = {'buildIris':'bool',
                     'buildPupil':'bool',
                     'buildLids':'bool',
                     'componentJoints':'bool',
                     'uprLidJoints':'int',
                     'lwrLidJoints':'int',
                     'pupilHelper':'messageSimple',
                     'irisHelper':'messageSimple',
                     'uprLidHelper':'messageSimple',
                     'lwrLidHelper':'messageSimple',
                     'moduleEyelids':'messageSimple'} 
    d_defaultSettings = {'buildIris':True,'buildPupil':True,'buildLids':True,'componentJoints':False,
                         'uprLidJoints':5,'lwrLidJoints':5}
    d_helperSettings = {'iris':{'plug':'irisHelper','check':'buildIris'},
                        'pupil':{'plug':'pupilHelper','check':'buildIris'}}

    #These lists should be set up per rigblock as a way to get controls from message links
    _l_controlLinks = ['pupilHelper','irisHelper','uprLidHelper','lwrLidHelper']
    _l_controlmsgLists = []

    def __init__(self,*args,**kws):
        """ 
        """
        _str_func = "cgmEyeballBlock.__init__"  
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        #if kws:log.debug("kws: %s"%str(kws))         
        #if args:log.debug("args: %s"%str(args))  

        if 'name' not in kws.keys():
            kws['name'] = 'eye'  
        super(cgmEyeballBlock, self).__init__(*args,**kws) 
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================
    def __verify__(self,**kws):
        _str_func = "cgmEyeballBlock.__verify__(%s)"%self.p_nameShort    
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        cgmRigBlockOLD.__verify__(self,**kws)

        #>>> Attributes ..
        self.addAttr('buildAs','cgmEyeball',lock=True)
        self.verifyAttrDict(cgmEyeballBlock.d_attrsToMake,keyable = False, hidden = False)
        for attr in cgmEyeballBlock.d_defaultSettings.keys():
            try:self.addAttr(attr, value = cgmEyeballBlock.d_defaultSettings[attr], defaultValue = cgmEyeballBlock.d_defaultSettings[attr])
            except Exception,error: raise StandardError,"%s.__verify__ >>> Failed to set value on: %s | data: %s | error: %s"%(self.p_nameShort,attr,cgmEyeballBlock.d_defaultSettings[attr],error)
        if not self.getShapes():
            self.__rebuildShapes__()

        self.doName()        
        return True

    def __rebuildShapes__(self,size = None):
        _str_func = "cgmEyeballBlock.__rebuildShapes__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        if self.isReferenced():
            raise StandardError,"%s >>> is referenced. Cannot verify"%_str_func

        l_shapes = self.getShapes()
        if l_shapes:
            mc.delete(l_shapes)

        ml_shapes = cgmMeta.validateObjListArg( self.getShapes(),noneValid=True )
        self.color = getSettingsColors( self.getAttr('cgmDirection') )

        #>>> Figure out the control size 	
        if size is None:#
            if l_shapes:
                absSize =  distance.returnAbsoluteSizeCurve(self.mNode)
                size = max(absSize)
            else:size = 10

        #>>> Delete shapes
        if l_shapes:
            mc.delete(ml_shapes)

        #>>> Build the eyeorb
        l_curveShapes = []
        l_curveShapes.append(mc.curve( d = 3,p = [[-1.9562614856650922e-17, 0.27234375536457955, 0.42078583109797302], [3.6231144545942155e-17, 0.44419562780377575, 0.2927550836423139], [1.2335702099837762e-16, 0.55293025498339243, -0.0036181380792718819], [1.4968222251671369e-16, 0.38920758821246809, -0.39338278937226923], [8.8443099225711831e-17, -0.0024142895734145229, -0.55331090087007562], [-2.4468224144040798e-17, -0.39262563725601413, -0.38997137672626969], [-1.2297164287833005e-16, -0.55294077490394233, 0.0012071651865769651], [-1.6080353342952326e-16, -0.44037303463385957, 0.29661659753593533], [-1.3886669551328167e-16, -0.27181045164087791, 0.42314656824251157]],k = (1.0, 1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.0, 7.0)))
        l_curveShapes.append(mc.curve( d = 3,p = [[0.27234375536457939, 1.734683000445787e-16, 0.42078583109797307], [0.44419562780377558, 1.2740478502632556e-16, 0.29275508364231401], [0.55293025498339232, -1.3852290198695529e-18, -0.0036181380792717592], [0.38920758821246809, -1.5060930340872423e-16, -0.39338278937226911], [-0.0024142895734143997, -2.1183887958462436e-16, -0.55331090087007562], [-0.3926256372560139, -1.4930322064116459e-16, -0.3899713767262698], [-0.55294077490394222, 4.6217148477624099e-19, 0.0012071651865768424], [-0.44037303463385952, 1.2888319214868455e-16, 0.29661659753593522], [-0.27117872614283267, 1.7437212447837615e-16, 0.42314656824251151]],k = (1.0, 1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.0, 7.0)))
        l_curveShapes.append(mc.curve( d = 3,p = [[9.7144514654701197e-17, -0.27151128700632393, 0.4226944232293004], [0.071575100224478827, -0.27101472617476752, 0.42269442322930045], [0.21517305056594385, -0.2111533666759117, 0.4226944232293004], [0.30072197725858107, 0.00196779544506197, 0.42269442322930029], [0.21167818985563105, 0.21394895499628236, 0.42269442322930018], [-0.0013130587947546969, 0.30092899899893094, 0.42269442322930012], [-0.21353716294939432, 0.21209359123764582, 0.42269442322930018], [-0.30072769872395522, -0.0006565404922469105, 0.42269442322930029], [-0.21332222008560683, -0.2130230418667757, 0.4226944232293004], [-0.069207355235434434, -0.27162900941733881, 0.42269442322930045], [1.1410775855283418e-16, -0.27151128700632399, 0.4226944232293004]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        l_curveShapes.append(mc.curve( d = 3,p = [[0.0, -0.49825526937946768, 2.2126978888235788e-16], [0.131348759885549, -0.49734402162391972, 3.0084413217208814e-16], [0.39486795357586341, -0.38749135902787507, 2.3439409455508664e-16], [0.55186033493999953, 0.0036111369820883686, -2.1843820862340872e-18], [0.38845447152927703, 0.39262159367483379, -2.3749738105919298e-16], [-0.002409617923089843, 0.552240244276892, -3.3405093821679339e-16], [-0.39186590664792353, 0.38921678211230448, -2.3543780552354256e-16], [-0.55187083450450314, -0.0012048293219408162, 7.2880303374564086e-19], [-0.39147146111426462, -0.39092243375831293, 2.3646955671973833e-16], [-0.12700366826764278, -0.49847130390333205, 3.0152602688544059e-16], [3.1129555427347658e-17, -0.49825526937946774, 2.2126978888235788e-16]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)))
        str_orb = curves.combineCurves(l_curveShapes)	

        curves.parentShapeInPlace(self.mNode,str_orb)#parent shape in place	
        curves.setCurveColorByName(self.mNode,self.color[0])#Set the color	    	
        mc.delete(str_orb)	

        #>>>Build the Iris and pupil
        l_buildOrder = ['pupil','iris','uprLid','lwrLid']
        d_buildCurves = {'pupil':mc.circle(normalZ = 1,radius = .09)[0],
                         'iris':mc.circle(normalZ = 1,radius = .18)[0],
                         'uprLid': mc.curve( d = 7,p = [[-0.44983530883670614, -0.071322594849904483, 0.36447022867017792], [-0.41829822121153859, -0.076896548997831424, 0.36029350648460373], [-0.37965007473058976, -0.068979541432776223, 0.38851433033177529], [-0.30723268320699781, 0.069290384212930434, 0.47810854649572376], [-0.17722744036745491, 0.18746372246544851, 0.59390774699001958], [0.10824468618298072, 0.21321584685485462, 0.584725411742131], [0.3298348785746214, 0.15455892134311355, 0.47446094679578343], [0.45662395681608442, 0.0061289393759054178, 0.32035084692498095], [0.45876148344130957, -0.081023121388213326, 0.25124022530758361]],k = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0)),
                         'lwrLid':mc.curve( d = 7,p = [[-0.45053674825700091, -0.073162071798690526, 0.36480978291355348], [-0.42304044071766306, -0.067231612899713564, 0.3610575914584816], [-0.39997680161862192, -0.077368790745462476, 0.38742660957006148], [-0.27603943705561623, -0.19069469101646774, 0.4998691161966955], [-0.14516156462612845, -0.2266921348862958, 0.57038517412610701], [0.10764440316710838, -0.24084200820627188, 0.55850510170499423], [0.32024605633174202, -0.20780685290092293, 0.4559870301884088], [0.43357025439741831, -0.10483423978152118, 0.28188913131160498], [0.46005845201487922, -0.083167671103495877, 0.24918293340572251]],k = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0)),
                         }
        ml_curves = []
        md_curves = {}
        for k in l_buildOrder:
            str_return = d_buildCurves.get(k)
            mi_obj = cgmMeta.asMeta(str_return,'cgmObject',setClass = True)
            mi_obj.addAttr('cgmName',k)#tag
            mi_obj.addAttr('cgmType',value = 'rigHelper',lock=True)		    
            curves.setCurveColorByName(mi_obj.mNode,self.color[0])#Set the color	    			
            ml_curves.append(mi_obj)#append
            md_curves[k] = mi_obj
            mi_obj.doName()#Name	

            if k in ['uprLid','lwrLid']:
                mi_obj.doCopyPivot(self)

            self.connectChildNode(mi_obj,'%sHelper'%k,'mi_block')

        #Second pass on doing parenting and some lock work
        for k in md_curves.keys():
            mi_obj = md_curves.get(k)
            if k == 'pupil':
                mi_obj.parent = md_curves.get('iris')		
            else:
                mi_obj.parent = self.mNode#parent to inherit names
            if k in ['iris','pupil']:
                mi_obj.tz = .46
                mc.makeIdentity(mi_obj.mNode,apply=True,t=1,r=1,s=1,n=0)

            cgmMeta.cgmAttr(mi_obj,'sx').doConnectIn("%s.scaleY"%mi_obj.mNode)
            attributes.doSetLockHideKeyableAttr(mi_obj.mNode,lock=True,visible=False,keyable=False,channels=['tx','ty','rx','ry','rz','sx','sz','v'])

        #Connect in our scales so we're scaling the eye one one channel
        cgmMeta.cgmAttr(self,'sx').doConnectIn("%s.scaleY"%self.mNode)
        cgmMeta.cgmAttr(self,'sz').doConnectIn("%s.scaleY"%self.mNode)
        for a in ['sx','sz','rotate','v']:
            cgmMeta.cgmAttr(self,a,keyable=False,lock=True,hidden=True)

        #attributes.doSetLockHideKeyableAttr(self.mNode,lock=True,visible=False,keyable=False,channels=['tx','ty','rx','ry','rz','sx','sz','v'])

    def __mirrorBuild__(self):
        _str_func = "cgmEyeballBlock.__buildMirror__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)

        try:
            try:#Mirror Block =====================================================================
                if not self.getMessage('blockMirror'):
                    mi_dup = self.doDuplicate(po = False)
                    l_pivot = mc.xform(self.mNode,q=True, sp = True,ws=True)
                    self.connectChildNode(mi_dup,"blockMirror","blockMirror")
                    attributes.doBreakConnection(mi_dup.mNode,'moduleTarget')
                mi_mirror = self.blockMirror  
                str_direction = self.getEnumValueString('direction') 
                if str_direction == 'left':_str_useDirection = 'right'
                elif str_direction == 'right':_str_useDirection = 'left'
                else:_str_useDirection = 'none'
                mi_mirror.direction = _str_useDirection
                mi_mirror.cgmDirection = mi_mirror.getEnumValueString('direction')
                mi_mirror.doName()

            except Exception,error:raise StandardError,"Failed to mirror mirror shapes | error: %s "%(error)
            try:#Find our shapes =====================================================================
                l_shapes = ['iris','pupil','uprLid','lwrLid']
                ml_crvs = [mi_mirror]
                l_children = mi_mirror.getAllChildren(True)
                for c in l_children:
                    i_c = cgmMeta.cgmNode(c)
                    for shape in l_shapes:
                        if i_c.getAttr('cgmName') == shape:
                            mi_mirror.connectChildNode(i_c,'%sHelper'%shape,'mi_block')
                            ml_crvs.append(i_c)
                            if shape in ['uprLid','lwrLid']:#mirror
                                mc.scale( -1,1,1,i_c.getComponents('cv'),pivot = l_pivot ,r=True)		

                #for a in ['lwrLid','uprLid']:
                    #mc.scale( -1,1,1,mi_mirror.getMessageAsMeta("%sHelper"%a).getComponents('cv'),pivot = l_pivot ,  r=True)		
            except Exception,error:raise StandardError,"Failed to mirror mirror shapes | error: %s "%(error)
            try:#Color =====================================================================
                __color = getSettingsColors( mi_mirror.getAttr('cgmDirection') )
                for mCrv in ml_crvs:
                    curves.setCurveColorByName(mCrv.mNode,__color[0])#Set the color	    
            except Exception,error:raise StandardError,"Color mirror| error: %s "%(error)
            self.__mirrorPush__()
            return mi_mirror
        except Exception,error:raise StandardError,"%s >> | error: %s "%(_str_func,error)

    def __mirrorPush__(self):
        cgmRigBlockOLD.__buildModule__(self)
        _str_func = "cgmEyeballBlock.__pushToMirror__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        try:
            if not self.getMessage('blockMirror'):
                log.warning("%s >> no blockMirror found"%_str_func)
                return False
            mi_mirror = self.blockMirror

            mi_mirror.tx = -self.tx
            mi_mirror.ty = self.ty
            mi_mirror.tz = self.tz
            mi_mirror.sy = self.sy 
        except Exception,error:raise StandardError,"[{0} - main mirror] | error: {1} ".format(_str_func,error)

        try:
            mi_pupilMirror = mi_mirror.pupilHelper
            mi_irisMirror = mi_mirror.irisHelper

            mi_irisMirror.ty = self.irisHelper.ty
            mi_irisMirror.tz = self.irisHelper.tz

            mi_pupilMirror.ty = self.pupilHelper.ty
            mi_pupilMirror.tz = self.pupilHelper.tz
            mi_pupilMirror.sy = self.pupilHelper.sy
        except Exception,error:raise StandardError,"[{0} - iris/pupil] | error: {1} ".format(_str_func,error)

        try:
            mi_uprLidMirror = mi_mirror.uprLidHelper
            mi_lwrLidMirror = mi_mirror.lwrLidHelper

            CURVES.mirrorCurve(self.uprLidHelper.mNode, mi_uprLidMirror.mNode,mirrorAcross='x')
            CURVES.mirrorCurve(self.lwrLidHelper.mNode, mi_lwrLidMirror.mNode,mirrorAcross='x')	    

        except Exception,error:raise StandardError,"[{0} - eyelids] | error: {1} ".format(_str_func,error)



    def __buildModule__(self):
        cgmRigBlockOLD.__buildModule__(self)
        _str_func = "cgmEyeballBlock.__buildModule__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        try:
            bfr_name = self._d_buildKWS.get('name') or None
            bfr_position = self._d_buildKWS.get('position') or None
            bfr_direction = self._d_buildKWS.get('direction') or None

            try:#Eyeball module
                #===================================================================
                i_module = cgmEyeball(name = bfr_name,
                                      position = bfr_position,
                                      direction = bfr_direction)
                self.connectChildNode(i_module,"moduleTarget","helper")
            except Exception,error:raise StandardError,"Failed to build eyeball module | error: %s "%(error)
            try:#Eyelids module
                #===================================================================
                i_eyelidsModule = cgmEyelids(name = 'eyelids',
                                             position = bfr_position,
                                             direction = bfr_direction)
                i_eyelidsModule.doSetParentModule(i_module)
                self.connectChildNode(i_eyelidsModule,"moduleEyelids","helper")

            except Exception,error:raise StandardError,"Failed to build eyelids module | error: %s "%(error)
            try:#Mirror ============================================================
                if self.autoMirror:
                    #if log.getEffectiveLevel() == 10:log.debug("%s >> mirror mode"%(_str_func))
                    if not self.getMessage('blockMirror'):
                        mi_mirror = self.__mirrorBuild__()
                    else:
                        mi_mirror = self.blockMirror
                        bfr_mirrorDirection = mi_mirror.cgmDirection

                    try:#Eyeball module
                        #===================================================================
                        i_moduleMirror = cgmEyeball(name = bfr_name,
                                                    position = bfr_position,
                                                    direction = bfr_mirrorDirection)
                        i_module.connectChildNode(i_moduleMirror,"moduleMirror","moduleMirror")
                        mi_mirror.connectChildNode(i_moduleMirror,"moduleTarget","helper")		    
                    except Exception,error:raise StandardError,"Failed to mirror eyeball module | error: %s "%(error)
                    try:#Eyelids module
                        #===================================================================
                        i_eyelidsModuleMirror = cgmEyelids(name = 'eyelids',
                                                           position = bfr_position,
                                                           direction = bfr_mirrorDirection)
                        i_eyelidsModuleMirror.doSetParentModule(i_moduleMirror)
                        mi_mirror.connectChildNode(i_eyelidsModuleMirror,"moduleEyelids","helper")
                    except Exception,error:raise StandardError,"Failed to mirror eyelids module | error: %s "%(error)
            except Exception,error:raise StandardError,"failed to mirror | error: %s "%(error)
            self.__storeNames__()

            #Size it
            self.__updateSizeData__()

            #>>>Let's do our manual sizing
            return i_module
        except Exception,error:raise StandardError,"%s >>>  error: %s "%(_str_func,error)

    def __storeNames__(self):
        #Store our names
        _str_func = "cgmEyeballBlock.__storeNames__(%s)"%self.p_nameShort   	
        if not self.getMessage("moduleTarget"):
            raise StandardError," %s >>> No Module!"%(_str_func)

        l_names= ['eyeball']
        if self.buildIris:l_names.append('iris')
        if self.buildPupil:l_names.append('pupil')
        self.moduleTarget.coreNames.value = l_names
        try:#Mirror ============================================================
            if self.autoMirror:
                self.moduleTarget.moduleMirror.coreNames.value = l_names
        except Exception,error:raise StandardError,"%s >>>  mirror error: %s "%(_str_func,error)

        return True

    def __updateSizeData__(self):
        """For overload"""
        _str_func = "cgmEyeballBlock.__updateSizeData__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        if not self.getMessage('moduleTarget'):
            raise StandardError,">>> %s >>> No module found "%(_str_func)

        i_module = self.moduleTarget#Lilnk
        l_pos = [self.getPosition()]
        d_helpercheck = cgmEyeballBlock.d_helperSettings#Link

        """
	for k in d_helpercheck.keys():
	    try:
		if self.getAttr(d_helpercheck[k].get('check')) and self.getMessage(d_helpercheck[k].get('plug')):
		    l_pos.append(self.getMessageAsMeta(d_helpercheck[k].get('plug')).getPosition())
	    except Exception,error:
		log.error(">>> %s >>> helper check failed: %s | error: %s"%(_str_func,k,error))	
	"""
        ##ml_helpers = self.msgList_get('ml_helpers')#Get our helpers
        """
	if self.buildPupil:
	    try:l_pos.append(self.pupilHelper.getPosition())
	    except Exception,error:raise StandardError,"%s >>> Missing Pupil helper | error: %s "%(_str_func,error)
	if self.buildIris:
	    try:l_pos.append(self.irisHelper.getPosition())
	    except Exception,error:raise StandardError,"%s >>> Missing Iris helper | error: %s "%(_str_func,error)

	log.info("%s >>> l_pos: %s"%(_str_func,l_pos))		

	#Push handles
	i_module.templateNull.handles = len(l_pos)

	i_module.doSize(sizeMode = 'manual',
	                 posList = l_pos)
	"""
        return True

class cgmEyebrowBlock(cgmRigBlockOLD):
    d_attrsToMake = {'buildTemple':'bool',
                     'buildSquashStretch':'bool',                                          
                     'buildUprCheek':'bool',                     
                     'browJoints':'int',
                     'templeJoints':'int',
                     'cheekJoints':'int',                                          
                     'leftBrowHelper':'messageSimple',
                     'rightBrowHelper':'messageSimple',
                     'leftTempleHelper':'messageSimple',
                     'rightTempleHelper':'messageSimple',  
                     'leftUprCheekHelper':'messageSimple',                     
                     'rightUprCheekHelper':'messageSimple',
                     'squashCastHelper':'messageSimple',                                          
                     'uprFacePivotHelper':'messageSimple',                                                               
                     'skullPlate':'messageSimple', 
                     'jawPlate':'messageSimple',                                          
                     'moduleBrow':'messageSimple'} 
    d_defaultSettings = {'buildTemple':True,'buildSquashStretch':True,'buildCheek':True,
                         'browJoints':4,'templeJoints':2,'cheekJoints':2}
    d_helperSettings = {'iris':{'plug':'irisHelper','check':'buildIris'},
                        'pupil':{'plug':'pupilHelper','check':'buildIris'}}
    _l_controlLinks = ['leftBrowHelper','rightBrowHelper',
                       'leftTempleHelper','rightTempleHelper',
                       'leftUprCheekHelper','rightUprCheekHelper',
                       'squashCastHelper','uprFacePivotHelper']
    _l_controlmsgLists = []
    def __init__(self,*args,**kws):
        """ 
        """
        _str_func = "cgmEyebrowBlock.__init__"  
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        #if kws:log.debug("kws: %s"%str(kws))         
        #if args:log.debug("args: %s"%str(args))  

        if 'name' not in kws.keys():
            kws['name'] = 'brow'  
        super(cgmEyebrowBlock, self).__init__(*args,**kws) 
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================
    def __verify__(self,**kws):
        _str_func = "cgmEyebrowBlock.__verify__(%s)"%self.p_nameShort    
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        cgmRigBlockOLD.__verify__(self,**kws)

        #>>> Attributes ..
        self.addAttr('buildAs','cgmEyebrow',lock=True)
        self.verifyAttrDict(cgmEyebrowBlock.d_attrsToMake,keyable = False, hidden = False)
        for attr in cgmEyebrowBlock.d_defaultSettings.keys():
            try:self.addAttr(attr, value = cgmEyebrowBlock.d_defaultSettings[attr], defaultValue = cgmEyebrowBlock.d_defaultSettings[attr])
            except Exception,error: raise StandardError,"%s.__verify__ >>> Failed to set value on: %s | data: %s | error: %s"%(self.p_nameShort,attr,cgmEyebrowBlock.d_defaultSettings[attr],error)
        if not self.getShapes():
            self.__rebuildShapes__()

        self.doName()        
        return True

    def __rebuildShapes__(self,size = None):
        _str_func = "cgmEyebrowBlock.__rebuildShapes__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)	
        if self.isReferenced():
            raise StandardError,"%s >>> is referenced. Cannot verify"%_str_func

        ml_shapes = cgmMeta.validateObjListArg( self.getShapes(),noneValid=True )
        self.color = getSettingsColors( self.getAttr('cgmDirection') )

        #>> restore some settings
        self.direction = 'center'
        self.autoMirror = True

        #>>> Figure out the control size 	
        if size is None:#
            if ml_shapes:
                absSize =  distance.returnAbsoluteSizeCurve(self.mNode)
                size = max(absSize)
            else:size = 10

        #>>> Delete shapes
        if ml_shapes:
            #if log.getEffectiveLevel() == 10:log.debug("%s >>> deleting: %s"%(_str_func,ml_shapes))	    
            mc.delete([mObj.mNode for mObj in ml_shapes])

        #>>> Main Shape
        str_root =  mc.curve( d = 1,p = [[0.0, 2.2934297141192093, -5.0924369479492732e-16], [-0.68646875796765439, 1.2637265771677275, -2.8060366856047015e-16], [-0.34323437898382719, 1.2637265771677275, -2.8060366856047015e-16], [-0.34323437898382719, 0.34323437898382719, -7.6213342078152378e-17], [-1.2637265771677275, 0.34323437898382719, -7.6213342078152378e-17], [-1.2637265771677275, 0.68646875796765439, -1.5242668415630476e-16], [-2.2934297141192093, 0.0, 0.0], [-1.2637265771677275, -0.68646875796765439, 1.5242668415630476e-16], [-1.2637265771677275, -0.34323437898382719, 7.6213342078152378e-17], [-0.34323437898382719, -0.34323437898382719, 7.6213342078152378e-17], [-0.34323437898382719, -1.2637265771677275, 2.8060366856047015e-16], [-0.68646875796765439, -1.2637265771677275, 2.8060366856047015e-16], [0.0, -2.2934297141192093, 5.0924369479492732e-16], [0.68646875796765439, -1.2637265771677275, 2.8060366856047015e-16], [0.34323437898382719, -1.2637265771677275, 2.8060366856047015e-16], [0.34323437898382719, -0.34323437898382719, 7.6213342078152378e-17], [1.2637265771677275, -0.34323437898382719, 7.6213342078152378e-17], [1.2637265771677275, -0.68646875796765439, 1.5242668415630476e-16], [2.2934297141192093, 0.0, 0.0], [1.2637265771677275, 0.68646875796765439, -1.5242668415630476e-16], [1.2637265771677275, 0.34323437898382719, -7.6213342078152378e-17], [0.34323437898382719, 0.34323437898382719, -7.6213342078152378e-17], [0.34323437898382719, 1.2637265771677275, -2.8060366856047015e-16], [0.68646875796765439, 1.2637265771677275, -2.8060366856047015e-16], [0.0, 2.2934297141192093, -5.0924369479492732e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0))	

        curves.parentShapeInPlace(self.mNode,str_root)#parent shape in place	
        curves.setCurveColorByName(self.mNode,self.color[0])#Set the color	    	
        mc.delete(str_root)


        #>>>Build the Brow curves
        l_buildOrder = ['leftBrow','rightBrow','leftTemple','rightTemple','leftUprCheek','rightUprCheek']
        d_buildCurves = {'leftBrow': mc.curve( d = 3,p = [[3.2074032095569307, 0.088162999957347665, -2.3016555193378068], [4.251097108912214, 0.024232165150834817, -2.4497118908209892], [6.3384849076227407, -0.10362950446324248, -2.7458246337874641], [8.7788670165788485, -0.72794558079678495, -5.7291335329457826], [9.4595644079063881, -2.2640763188546771, -7.2217667690319409], [9.7999131035701303, -3.0321416878841205, -7.96808338707506]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 3.0, 3.0)),
                         'rightBrow': mc.curve( d = 3,p = [[-3.2074032095569307, 0.088162999957347665, -2.3016555193378068], [-4.251097108912214, 0.024232165150834817, -2.4497118908209892], [-6.3384849076227407, -0.10362950446324248, -2.7458246337874641], [-8.7788670165788485, -0.72794558079678495, -5.7291335329457826], [-9.4595644079063881, -2.2640763188546771, -7.2217667690319409], [-9.7999131035701303, -3.0321416878841205, -7.96808338707506]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 3.0, 3.0)),
                         'leftTemple': mc.curve( d = 1,p = [[11.540519886111845, -5.2113010025090887, -12.865421648687006], [10.689684322507841, -5.4688004729911484, -9.7566605218848697]],k = (0.0, 3.2333609258955258)),
                         'rightTemple': mc.curve( d = 1,p = [[-11.540519886111845, -5.2113010025090887, -12.865421648687006], [-10.689684322507841, -5.4688004729911484, -9.7566605218848697]],k = (0.0, 3.2333609258955258)),
                         'leftUprCheek': mc.curve( d = 3,p = [[10.261528402499881, -9.0683619621701723, -8.3652067775967627], [9.9616161190362469, -9.5687755274758786, -7.6585499901992584], [9.361791552108933, -10.569602658087973, -6.2452364154043138], [6.4660266032352167, -9.9530720383801849, -4.5705546635419321], [5.0181441287983555, -9.6448067285263903, -3.7332137876107456]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0)),
                         'rightUprCheek': mc.curve( d = 3,p = [[-10.261528402499881, -9.0683619621701723, -8.3652067775967627], [-9.9616161190362469, -9.5687755274758786, -7.6585499901992584], [-9.361791552108933, -10.569602658087973, -6.2452364154043138], [-6.4660266032352167, -9.9530720383801849, -4.5705546635419321], [-5.0181441287983555, -9.6448067285263903, -3.7332137876107456]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0)),

                         }

        d_colors = {'left':getSettingsColors('left'),
                    'right':getSettingsColors('right')}

        ml_curves = []
        md_curves = {}
        for k in l_buildOrder:
            str_return = d_buildCurves.get(k)
            mi_obj = cgmMeta.asMeta(str_return,'cgmObject',setClass = True)
            mi_obj.addAttr('cgmName',k)#tag
            mi_obj.addAttr('cgmType',value = 'rigHelper',lock=True)
            if 'left' in k:
                curves.setCurveColorByName(mi_obj.mNode,d_colors.get('left')[0])#Set the color	    					
            else:
                curves.setCurveColorByName(mi_obj.mNode,d_colors.get('right')[0])#Set the color	 

            ml_curves.append(mi_obj)#append
            md_curves[k] = mi_obj
            mi_obj.doName()#Name	

            mi_obj.doCopyPivot(self)

            self.connectChildNode(mi_obj,'%sHelper'%k,'mi_block')

            mi_obj.parent = self
            for a in ['scale','translate','rotate','v']:
                cgmMeta.cgmAttr(mi_obj,a,keyable=False,lock=True,hidden=True)	

        #Connect in our scales so we're scaling the eye one one channel
        cgmMeta.cgmAttr(self,'sx').doConnectIn("%s.scaleY"%self.mNode)
        cgmMeta.cgmAttr(self,'sz').doConnectIn("%s.scaleY"%self.mNode)
        for a in ['sx','sz','rotate','v']:
            cgmMeta.cgmAttr(self,a,keyable=False,lock=True,hidden=True)

    def mirrorBrowCurvesTMP(self):
        _str_func = "cgmEyebrowBlock.mirrorBrowCurves(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        try:
            CURVES.mirrorCurve(self.getMessage('leftBrowHelper')[0],self.getMessage('rightBrowHelper')[0],mirrorAcross='x',mirrorThreshold = .05)
        except Exception,error:log.error("%s >> | error: %s "%(_str_func,error))
        try:
            CURVES.mirrorCurve(self.getMessage('leftTemplateHelper')[0],self.getMessage('rightTemplateHelper')[0],mirrorAcross='x',mirrorThreshold = .05)
        except Exception,error:log.error("%s >> | error: %s "%(_str_func,error)) 

        try:
            CURVES.mirrorCurve(self.getMessage('leftUprCheekHelper')[0],self.getMessage('rightUprCheekHelper')[0],mirrorAcross='x',mirrorThreshold = .05)
        except Exception,error:log.error("%s >> | error: %s "%(_str_func,error)) 

    def __buildModule__(self):
        cgmRigBlockOLD.__buildModule__(self)
        _str_func = "cgmEyebrowBlock.__buildModule__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        try:
            bfr_name = self._d_buildKWS.get('name') or None
            bfr_position = self._d_buildKWS.get('position') or None

            try:#Brow module
                #===================================================================
                i_module = cgmEyebrow(name = bfr_name,
                                      position = bfr_position)
                self.connectChildNode(i_module,"moduleTarget","helper")
            except Exception,error:raise StandardError,"Failed to build eyeball module | error: %s "%(error)

            except Exception,error:raise StandardError,"Failed to build eyelids module | error: %s "%(error)
            try:#Mirror ============================================================
                if self.autoMirror:
                    pass
                    #if log.getEffectiveLevel() == 10:log.debug("%s >> mirror mode"%(_str_func))
            except Exception,error:raise StandardError,"Failed to mirror | error: %s "%(error)

            #self.__storeNames__()

            #Size it
            #self.__updateSizeData__()

            #>>>Let's do our manual sizing
            return i_module
        except Exception,error:raise StandardError,"%s >>>  error: %s "%(_str_func,error)

    def __storeNames__(self):
        #Store our names
        _str_func = "cgmEyebrowBlock.__storeNames__(%s)"%self.p_nameShort   	
        if not self.getMessage("moduleTarget"):
            raise StandardError," %s >>> No Module!"%(_str_func)

        l_names= ['brow']
        if self.buildIris:l_names.append('iris')
        if self.buildPupil:l_names.append('pupil')
        self.moduleTarget.coreNames.value = l_names
        try:#Mirror ============================================================
            if self.autoMirror:
                self.moduleTarget.moduleMirror.coreNames.value = l_names
        except Exception,error:raise StandardError,"%s >>>  mirror error: %s "%(_str_func,error)

        return True

    def __updateSizeData__(self):
        """For overload"""
        _str_func = "cgmEyebrowBlock.__updateSizeData__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        if not self.getMessage('moduleTarget'):
            raise StandardError,">>> %s >>> No module found "%(_str_func)

        i_module = self.moduleTarget#Lilnk
        l_pos = [self.getPosition()]
        d_helpercheck = cgmEyeballBlock.d_helperSettings#Link

        return True

#>>> MouthNose  =====================================================================================================
d_mouthNose_rigNullAttrs_toMake = {'templateControl':'bool',#
                                   }

d_mouthNose_templateNullAttrs_toMake = {}
class cgmMouthNose(cgmModule):
    def __init__(self,*args,**kws):
        """ 
        Intializes a mouth/nose master class handler
        Args:
        node = existing module in scene
        name = treated as a base name

        Keyword arguments:
        moduleName(string) -- either base name or the name of an existing module in scene
        moduleParent(string) -- module parent to connect to. MUST exist if called. If the default False flag is passed, it looks for what's stored
        """
        if not kws:kws = {'mType':'mouthNose'}
        if 'name' not in kws.keys() and 'mType' in kws.keys():
            kws['name'] = kws['mType']
        super(cgmMouthNose, self).__init__(*args,**kws) 
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================
    def __verify__(self,*args,**kws):
        cgmModule.__verify__(self,*args,**kws)
        self.moduleType = 'mouthNose'

        #>>> Attributes ...
        self.__verifyAttributesOn__(self.i_rigNull,d_mouthNose_rigNullAttrs_toMake)
        self.__verifyAttributesOn__(self.i_templateNull,d_mouthNose_templateNullAttrs_toMake)

        settings = {'handles': 3}
        for attr in settings.keys():
            self.templateNull.addAttr(attr, value = settings[attr],lock = True)   
        return True

class cgmMouthNoseBlock(cgmRigBlockOLD):
    d_attrsToMake = {'buildSquashStretch':'bool',
                     'buildNose':'bool',                                                               
                     'buildNostril':'bool',                                          
                     'buildCheek':'bool',
                     'buildTongue':'bool',                     
                     'buildUprCheek':'bool',                     
                     'buildJawLine':'bool',                                          
                     'nostrilJoints':'int',
                     'cheekLoftCount':'int',
                     'smileLineCount':'int',
                     'componentJoints':'bool',                     
                     'cheekJoints':'int',
                     'tongueJoints':'int',                     
                     'lipJoints':'int',                       
                     'uprCheekJoints':'int',                     
                     'noseProfileHelper':'messageSimple',
                     'noseMidCastHelper':'messageSimple',
                     'noseBaseCastHelper':'messageSimple',
                     'lipUprHelper':'messageSimple',  
                     'lipLwrHelper':'messageSimple',                   
                     'lipOverTraceHelper':'messageSimple',
                     'lipUnderTraceHelper':'messageSimple',                                          
                     'mouthTopCastHelper':'messageSimple',
                     'mouthMidCastHelper':'messageSimple',                                                               
                     'mouthLowCastHelper':'messageSimple',
                     'leftUprCheekHelper':'messageSimple',                     
                     'rightUprCheekHelper':'messageSimple',                     
                     'jawLineHelper':'messageSimple',
                     'smileLeftHelper':'messageSimple',                                                                                    
                     'smileRightHelper':'messageSimple',
                     'jawPivotHelper':'messageSimple',
                     'tongueHelper':'messageSimple',                     
                     'squashStartHelper':'messageSimple',
                     'squashEndHelper':'messageSimple',                      
                     'skullPlate':'messageSimple', 
                     'moduleNose':'messageSimple'} 
    d_defaultSettings = {'buildNose':True,'buildNostril':True,'buildUprCheek':True,'componentJoints':False,'buildTongue':True,'buildSquashStretch':True,'buildJawLine':True,
                         'uprCheekJoints':3,'nostrilJoints':1,'cheekLoftCount':2,'smileLineCount':6,'lipJoints':7,'cheekJoints':3,'tongueJoints':5}
    d_helperSettings = {'iris':{'plug':'irisHelper','check':'buildIris'},
                        'pupil':{'plug':'pupilHelper','check':'buildIris'}}
    _l_controlLinks = ['noseProfileHelper','noseMidCastHelper','noseBaseCastHelper',
                       'lipUprHelper',  
                       'lipLwrHelper',                   
                       'lipOverTraceHelper',
                       'lipUnderTraceHelper',                                          
                       'mouthTopCastHelper',
                       'mouthMidCastHelper',                                                               
                       'mouthLowCastHelper',
                       'leftUprCheekHelper',                     
                       'rightUprCheekHelper',                     
                       'jawLineHelper',
                       'smileLeftHelper',                                                                                    
                       'smileRightHelper',
                       'jawPivotHelper',
                       'tongueHelper',                     
                       'squashStartHelper',
                       'squashEndHelper',                       ]
    _l_controlmsgLists = []
    def __init__(self,*args,**kws):
        """ 
        """
        log.debug("cgmMouthNoseBlock.__init__...")
        if not kws:kws = {}
        if 'name' not in kws.keys():
            kws['name'] = 'mouthNose'  
        super(cgmMouthNoseBlock, self).__init__(*args,**kws) 
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            #log.debug('CACHE : Aborting __init__ on pre-cached %s Object' % self.mNode)
            return
        #====================================================================================
    def __verify__(self,*args,**kws):
        cgmRigBlockOLD.__verify__(self,*args,**kws)

        #>>> Attributes ..
        self.addAttr('buildAs','cgmMouthNose',lock=True)
        self.verifyAttrDict(cgmMouthNoseBlock.d_attrsToMake,keyable = False, hidden = False)
        for attr in cgmMouthNoseBlock.d_defaultSettings.keys():
            try:self.addAttr(attr, value = cgmMouthNoseBlock.d_defaultSettings[attr], defaultValue = cgmMouthNoseBlock.d_defaultSettings[attr])
            except Exception,error: raise StandardError,"%s.__verify__ >>> Failed to set value on: %s | data: %s | error: %s"%(self.p_nameShort,attr,cgmMouthNoseBlock.d_defaultSettings[attr],error)
        if not self.getShapes():
            self.__rebuildShapes__(*args,**kws)  
        self.doName()        
        return True

    def __rebuildShapes__(self,*args,**kws):
        _mNodeSelf = self
        class fncWrap(cgmMeta.cgmMetaFunc):
            def __init__(self,*args,**kws): 
                super(fncWrap, self).__init__(*args,**kws)	
                self.mi_mNode = _mNodeSelf
                self._str_func= "cgmMouthNoseBlock.__rebuildShapes__(%s)"%self.mi_mNode.p_nameShort	
                self._l_ARGS_KWS_DEFAULTS = [{'kw':'size',"default":None,'help':"Sizing parameter for the build","argType":"int"}]		
                self.__dataBind__(*args,**kws)	
                #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
                #=================================================================
            def __func__(self):
                size = self.d_kws['size']

                if _mNodeSelf.isReferenced():
                    raise StandardError,"%s >>> is referenced. Cannot verify"%_str_func

                ml_shapes = cgmMeta.validateObjListArg( _mNodeSelf.getShapes(),noneValid=True )
                self.color = getSettingsColors( _mNodeSelf.getAttr('cgmDirection') )

                #>> restore some settings
                _mNodeSelf.direction = 'center'
                _mNodeSelf.autoMirror = True

                try:#>>> Figure out the control size ================================================================================ 	 
                    if size is None:#
                        if ml_shapes:
                            absSize =  distance.returnAbsoluteSizeCurve(_mNodeSelf.mNode)
                            size = max(absSize)
                        else:size = 10
                except Exception,error:raise StandardError,"Size check | %s"%error

                #>>> Delete shapes ================================================================================
                try:
                    if ml_shapes:
                        mc.delete([mObj.mNode for mObj in ml_shapes])
                except Exception,error:raise StandardError,"Deleting | %s"%error

                try:#>>> Main Shape ================================================================================
                    str_root =  mc.curve( d = 1,p = [[0.0, 2.2934297141192093, -5.0924369479492732e-16], [-0.68646875796765439, 1.2637265771677275, -2.8060366856047015e-16], [-0.34323437898382719, 1.2637265771677275, -2.8060366856047015e-16], [-0.34323437898382719, 0.34323437898382719, -7.6213342078152378e-17], [-1.2637265771677275, 0.34323437898382719, -7.6213342078152378e-17], [-1.2637265771677275, 0.68646875796765439, -1.5242668415630476e-16], [-2.2934297141192093, 0.0, 0.0], [-1.2637265771677275, -0.68646875796765439, 1.5242668415630476e-16], [-1.2637265771677275, -0.34323437898382719, 7.6213342078152378e-17], [-0.34323437898382719, -0.34323437898382719, 7.6213342078152378e-17], [-0.34323437898382719, -1.2637265771677275, 2.8060366856047015e-16], [-0.68646875796765439, -1.2637265771677275, 2.8060366856047015e-16], [0.0, -2.2934297141192093, 5.0924369479492732e-16], [0.68646875796765439, -1.2637265771677275, 2.8060366856047015e-16], [0.34323437898382719, -1.2637265771677275, 2.8060366856047015e-16], [0.34323437898382719, -0.34323437898382719, 7.6213342078152378e-17], [1.2637265771677275, -0.34323437898382719, 7.6213342078152378e-17], [1.2637265771677275, -0.68646875796765439, 1.5242668415630476e-16], [2.2934297141192093, 0.0, 0.0], [1.2637265771677275, 0.68646875796765439, -1.5242668415630476e-16], [1.2637265771677275, 0.34323437898382719, -7.6213342078152378e-17], [0.34323437898382719, 0.34323437898382719, -7.6213342078152378e-17], [0.34323437898382719, 1.2637265771677275, -2.8060366856047015e-16], [0.68646875796765439, 1.2637265771677275, -2.8060366856047015e-16], [0.0, 2.2934297141192093, -5.0924369479492732e-16]],k = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0))	

                    curves.parentShapeInPlace(_mNodeSelf.mNode,str_root)#parent shape in place	
                    curves.setCurveColorByName(_mNodeSelf.mNode,self.color[0])#Set the color	    	
                    mc.delete(str_root)
                except Exception,error:raise StandardError,"Main shape | %s"%error


                try:#>>>Build the Brow curves ================================================================================
                    l_buildOrder = [{'crv':'noseProfile','build':mc.curve( d = 3,p = [[0.0071058104709784686, 2.8157872873693464, -1.5303367770731064], [8.8224690376410021e-34, 3.6036757230719445, -0.12815530395825903], [-0.022857528316571063, 5.6133128322901484, 1.7578810638711033], [0.0084687663164082494, 6.4378123657563435, -1.3531125841832754], [-0.040077561738581124, 8.2676761853471135, -3.5536332527857937], [0.0, 9.8178480085368562, -3.8394009886168767]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 3.0, 3.0))},
                                    {'crv':'noseMidCast','build':mc.curve( d = 3,p = [[1.6983394422024412, 5.2813359016787444, -2.9400486872124318], [1.6310453158808398, 5.3898339770375969, -2.5744822722452056], [1.4131940779627328, 5.5038999136491213, -1.7243073078472229], [0.73100829748370899, 5.9963203078795573, -0.83600170561425813], [0.057109115093676763, 6.3348867875182577, -0.53743731237954862], [-0.73100829748370899, 5.9963203078795573, -0.83600170561425813], [-1.4131940779627328, 5.5038999136491213, -1.7243073078472229], [-1.6310453158808398, 5.3898339770375969, -2.5744822722452056], [-1.6983394422024412, 5.2813359016787444, -2.9400486872124318]],k = (0.0, 0.0, 0.0, 0.16666666666666663, 0.33333333333333337, 0.5, 0.66666666666666674, 0.83333333333333337, 1.0, 1.0, 1.0))},
                                    {'crv':'noseBaseCast','build':mc.curve( d = 3,p = [[2.4985515433249095, 3.8486761019605069, -3.0705716915104269], [2.7299954103202286, 3.9195089351071601, -2.3897403808922881], [2.3376354969600279, 3.9523314663460951, -1.4944812669517447], [1.319591935027461, 4.0428286553548958, -0.49851545672136766], [0.029496350099690382, 4.1066002869620206, 1.0815918576672807], [-1.319591935027461, 4.0428286553548958, -0.49851545672136766], [-2.3376354969600279, 3.9523314663460951, -1.4944812669517447], [-2.7299954103202286, 3.9195089351071601, -2.3897403808922881], [-2.4985515433249095, 3.8486761019605069, -3.0705716915104269]],k = (0.0, 0.0, 0.0, 0.16666666666666663, 0.33333333333333337, 0.5, 0.66666666666666674, 0.83333333333333337, 1.0, 1.0, 1.0))},
                                    {'crv':'lipUpr','build':mc.curve( d = 3,p = [[2.9305258839798061, -0.17091337891787362, -3.3275438749864925], [2.8061136667804929, -0.08408510729458385, -3.1506082613480508], [2.4508219073064383, 0.054068689883337129, -2.7319226134277663], [1.8307537832329963, 0.32717945883189259, -1.9157491446310644], [0.97707033634765039, 0.49164296205066194, -1.3999622476763776], [9.3467220516264686e-34, 0.40238616637327596, -1.2039892399981049], [-0.97707033634765028, 0.49164296205063351, -1.3999622476763847], [-1.8307537832329961, 0.32717945883186417, -1.9157491446310679], [-2.4508219073064379, 0.054068689883308707, -2.7319226134277699], [-2.8061136667804925, -0.084085107294612271, -3.1506082613480544], [-2.9305258839798061, -0.17091337891790204, -3.3275438749864961]],k = (0.0, 0.0, 0.0, 0.125, 0.25000000000000011, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.0, 1.0))},
                                    {'crv':'lipLwr','build':mc.curve( d = 3,p = [[2.9305258839798061, -0.17091337891790204, -3.3275438749864961], [2.7603606199527406, -0.23847238755482181, -3.1779971372257592], [2.4521198201384178, -0.51147110433913667, -2.9279302632533195], [1.7320614023491856, -0.744044177399104, -2.3015214821935608], [0.88785464627450406, -0.82492983255991703, -1.9985183572134098], [9.3467220516264686e-34, -0.94476820689476426, -1.8359184280694087], [-0.87132121772734594, -0.82613500683052621, -2.00906552013614], [-1.7088438956313943, -0.73009313709894741, -2.3113876951650312], [-2.4387125345003793, -0.49839488302342261, -2.9336080203078403], [-2.7404636916985536, -0.2269968762737733, -3.1814085738706694], [-2.9305258839798061, -0.17091337891793046, -3.3275438749864996]],k = (0.0, 0.0, 0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.0, 1.0))},
                                    {'crv':'lipOverTrace','build':mc.curve( d = 3,p = [[2.9305258839798061, 0.56699713055132861, -3.334341498870252], [2.8061136667804929, 0.68033535469334083, -3.1549652892727309], [2.4508219073064383, 0.88189673933626977, -2.7209843290457734], [1.8307537832329963, 1.2785742124775936, -1.8755317852591489], [0.97707033634765039, 1.521208352478169, -1.3400917451471877], [9.3467220516264686e-34, 1.463177923561517, -1.1151891047616367], [-0.97707033634765028, 1.5212083524781121, -1.3400917451471877], [-1.8307537832329961, 1.2785742124775368, -1.8755317852591453], [-2.4508219073064379, 0.88189673933624135, -2.7209843290457698], [-2.8061136667804925, 0.68033535469331241, -3.1549652892727309], [-2.9305258839798061, 0.56699713055130019, -3.334341498870252]],k = (0.0, 0.0, 0.0, 0.125, 0.25000000000000011, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.0, 1.0))},
                                    {'crv':'lipUnderTrace','build':mc.curve( d = 3,p = [[3.1483484461419113, -1.0523475410344645, -3.8069003514597881], [2.9655349970215177, -1.1779084481836435, -3.6826061680550879], [2.6343830189966577, -1.6553904409133793, -3.4998018901966574], [1.8608035010094508, -2.0970539844398672, -2.9712819764923353], [0.95384784392420441, -2.2578444652306189, -2.7106832974747164], [1.0041452972186513e-33, -2.4719034457568227, -2.58279652394517], [-0.93608550496640852, -2.2589690363780051, -2.7203834440351571], [-1.835860264166588, -2.0728990868443589, -2.9779968767162188], [-2.6199791854948784, -1.6330514856255149, -3.502876437450837], [-2.944159153356559, -1.158436700149025, -3.6838873387920472], [-3.1483484461419113, -1.0523475410345213, -3.8069003514598023]],k = (0.0, 0.0, 0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.0, 1.0))},
                                    {'crv':'mouthTopCast','build':mc.curve( d = 2,p = [[2.2796384177507973, 3.7721611655865956, -3.0037282536322945], [1.8739271773282293, 3.7604478794155227, -2.9387368699568501], [1.4064199710533587, 3.749925941526925, -2.8726569572412748], [0.71220288592933301, 3.7441085150249478, -2.7851699911626571], [8.8224690376410021e-34, 3.7456390400398334, -2.7589283736493244], [-0.71220288592933301, 3.7441085150249478, -2.7851699911626566], [-1.4064199710533587, 3.749925941526925, -2.8726569572412748], [-1.8739271773282296, 3.7604478794155227, -2.9387368699568501], [-2.2796384177507978, 3.7721611655865956, -3.003728253632294]],k = (0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.0))},
                                    {'crv':'mouthMidCast','build':mc.curve( d = 2,p = [[2.9305258839798061, -0.17091337891783454, -3.3275438749864801], [2.4787664175593829, -0.20372786955008948, -3.0561236532050842], [1.6993434363491937, -0.19141450743114774, -2.69144974476675], [0.83818093956168649, -0.1921663573192447, -2.3939422900672511], [8.8224690376410021e-34, -0.20813625813288539, -2.366722750679763], [-0.83818093956168649, -0.1921663573192447, -2.3939422900672511], [-1.6993434363491937, -0.19141450743114774, -2.69144974476675], [-2.4787664175593829, -0.20372786955006816, -3.0561236532050842], [-2.9305258839798061, -0.17091337891780256, -3.3275438749864801]],k = (0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.0))},
                                    {'crv':'mouthLowCast','build': mc.curve( d = 2,p = [[2.2750711435754827, -4.5250079607757385, -4.8421803069800671], [1.946581442422419, -4.5345230614859275, -4.5596708389540979], [1.5457132757601855, -4.5430703894700741, -4.2861348982129774], [1.0860042803187031, -4.5477960828606427, -4.1226033604674237], [0.0, -4.5465527853399124, -3.9132990694195846], [-1.0860042803187044, -4.5477960828606427, -4.1226033604674237], [-1.5457132757601868, -4.5430703894701026, -4.2861348982129748], [-1.9465814424224199, -4.5345230614859275, -4.5596708389540961], [-2.2750711435754836, -4.5250079607757385, -4.8421803069800662]],k = (0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.0))},
                                    {'crv':'jawLine','build':mc.curve( d = 3,p = [[10.280120866755682, 0.25156895683588232, -14.674226505769099], [9.8838593938489243, -0.45064659559670872, -13.653800138426188], [9.4048726640343236, -1.5645032943484125, -11.099299406228145], [7.2365077189624243, -3.085889188098264, -8.991315934011892], [4.7770336494068033, -4.5397574281530808, -6.8594451775956067], [1.4964809599950355, -5.3271768164440232, -4.0600676436545236], [-1.342102488616838, -5.3476785269627385, -4.1749655830569701], [-4.6738388336380563, -4.4669441161316001, -6.7814883355823401], [-7.2386874087871984, -3.0948622262322658, -8.9156442241085578], [-9.1909972678893652, -1.6073111610383251, -11.266970470266923], [-9.8887878551793271, -0.42215506140215098, -13.614331737181931], [-10.379444055515531, 0.2576728932989738, -14.674226505769099]],k = (0.0, 0.0, 0.0, 0.11111111111111116, 0.22222222222222221, 0.33333333333333337, 0.44444444444444442, 0.55555555555555558, 0.66666666666666674, 0.77777777777777779, 0.88888888888888884, 1.0, 1.0, 1.0))},
                                    {'crv':'smileLeft','build': mc.curve( d = 3,p = [[1.9719219725546537, 5.2630842124150377, -3.1751890702552501], [3.4117328415495929, 5.1794941062202042, -3.516485999812339], [4.577691638408484, 2.9534427292250314, -4.0605168197016113], [4.6757209802557789, 0.4025284021136315, -4.7607797185328478], [3.8815734401047433, -1.9931313539364908, -4.3450543358402003], [2.3352378738230142, -3.263798226801498, -3.962077171287536]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 3.0, 3.0))},
                                    {'crv':'smileRight','build': mc.curve( d = 2,p = [[-1.9719219725546537, 5.2630842124150377, -3.1751890702552501], [-3.1779007947145459, 4.8581891345421298, -3.5126066116582666], [-4.3637834902508787, 2.8782470458953355, -4.0003303220717186], [-4.4957910645456307, 0.44046596054249676, -4.5434565034310861], [-3.6578843946194062, -1.8427749234695909, -4.3470213033400062], [-2.3352378738230142, -3.263798226801498, -3.962077171287536]],k = (0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0))},              
                                    {'crv':'squashStart','pos':[0.0, 5.8829912280671977, -7.8415670853293538],
                                     'build':curves.createControlCurve('arrowsLocator3d',5)},
                                    {'crv':'squashEnd','pos':[0.0, -4.457696693978674, -7.8245184630993476],
                                     'build':curves.createControlCurve('arrowsLocator3d',5)},
                                    {'crv':'jawPivot','pos':[0.0, 4.1497239011318925, -16.516275079037065],
                                     'build':curves.createControlCurve('arrowsLocator3d',5)},
                                    {'crv':'tongue','pos':[0.0, -.907, -9.58],
                                     'build':mc.curve( d = 3,p = [[-2.7755575615628914e-17, 0.0, 0.0], [-2.7755575615628914e-17, 0.60756963071641867, 1.1236862664769891], [-2.7755575615628914e-17, 0.82636477358125882, 3.2889585672224815], [-2.7755575615628914e-17, 0.68210872178182591, 5.1264759555862316], [-2.7755575615628914e-17, 0.45514461965462005, 6.0748467903335328]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0))},
                                    {'crv':'leftUprCheek','build':mc.curve( d = 3,p = [[10.261528402499881, 6.5673628044320083, -9.7737008952598554], [9.9616161190362469, 6.066949239126302, -9.0670441078623512], [9.361791552108933, 5.0661221085142074, -7.6537305330674066], [6.4660266032352167, 5.6826527282219956, -5.9790487812050248], [5.0181441287983555, 5.9909180380757903, -5.1417079052738384]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0))},
                                    {'crv':'rightUprCheek','build':mc.curve( d = 3,p = [[-10.261528402499881, 6.5673628044320083, -9.7737008952598554], [-9.9616161190362469, 6.066949239126302, -9.0670441078623512], [-9.361791552108933, 5.0661221085142074, -7.6537305330674066], [-6.4660266032352167, 5.6826527282219956, -5.9790487812050248], [-5.0181441287983555, 5.9909180380757903, -5.1417079052738384]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0))}]

                    d_colors = {'left':getSettingsColors('left'),
                                'right':getSettingsColors('right'),
                                'center':getSettingsColors('center')}

                    ml_curves = []
                    md_curves = {}
                    for d in l_buildOrder:
                        try:
                            str_name = d.get('crv')
                            self.str_name = str_name
                            str_return = d.get('build')
                            self.str_return = str_return

                            mi_obj = cgmMeta.asMeta(str_return,'cgmObject',setClass = True)#instance
                            mi_obj.addAttr('cgmName',str_name)#tag
                            mi_obj.addAttr('cgmType',value = 'rigHelper',lock=True)
                            if 'left' in str_name or 'Left' in str_name:
                                curves.setCurveColorByName(mi_obj.mNode,d_colors.get('left')[0])#Set the color	    					
                            elif 'right' in str_name or 'Right' in str_name:
                                curves.setCurveColorByName(mi_obj.mNode,d_colors.get('right')[0])#Set the color	 
                            elif 'Cast' in str_name or 'Pivot' in str_name or 'squash' in str_name:
                                curves.setCurveColorByName(mi_obj.mNode,'greenBright')#Set the color	 				
                            else:
                                curves.setCurveColorByName(mi_obj.mNode,d_colors.get('center')[0])#Set the color	 

                            ml_curves.append(mi_obj)#append
                            md_curves[str_name] = mi_obj
                            mi_obj.doName()#Name

                            l_keys = d.keys()
                            if not 'pos' in l_keys:
                                mi_obj.doCopyPivot(_mNodeSelf)
                            else:
                                mi_obj.translate = d.get('pos')

                            _mNodeSelf.connectChildNode(mi_obj,'%sHelper'%str_name,'mi_block')
                            mi_obj.parent = _mNodeSelf

                            #Lock n hide
                            if not 'pos' in l_keys:
                                for a in ['scale','translate','rotate','v']:
                                    cgmMeta.cgmAttr(mi_obj,a,keyable=False,lock=True,hidden=True)				    
                            else:
                                for a in ['tx','ry','rz','scale','v']:
                                    cgmMeta.cgmAttr(mi_obj,a,keyable=False,lock=True,hidden=True)					
                        except Exception,error:raise StandardError,"%s | %s"%(str_name,error)			
                except Exception,error:raise StandardError,"Curves | %s"%error

                try: #Connect in our scales so we're scaling the eye one one channel
                    cgmMeta.cgmAttr(_mNodeSelf,'sx').doConnectIn("%s.scaleY"%_mNodeSelf.mNode)
                    cgmMeta.cgmAttr(_mNodeSelf,'sz').doConnectIn("%s.scaleY"%_mNodeSelf.mNode)
                    for a in ['sx','sz','rotate','v']:
                        cgmMeta.cgmAttr(_mNodeSelf,a,keyable=False,lock=True,hidden=True)
                except Exception,error:raise StandardError,"Finalize | %s"%error
        return fncWrap(*args,**kws).go()

    def mirrorBrowCurvesTMP(self):
        _str_func = "cgmMouthNoseBlock.mirrorBrowCurves(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        try:
            CURVES.mirrorCurve(self.getMessage('leftBrowHelper')[0],self.getMessage('rightBrowHelper')[0],mirrorAcross='x',mirrorThreshold = .05)
        except Exception,error:log.error("%s >> | error: %s "%(_str_func,error))
        try:
            CURVES.mirrorCurve(self.getMessage('leftTemplateHelper')[0],self.getMessage('rightTemplateHelper')[0],mirrorAcross='x',mirrorThreshold = .05)
        except Exception,error:log.error("%s >> | error: %s "%(_str_func,error)) 

        try:
            CURVES.mirrorCurve(self.getMessage('leftUprCheekHelper')[0],self.getMessage('rightUprCheekHelper')[0],mirrorAcross='x',mirrorThreshold = .05)
        except Exception,error:log.error("%s >> | error: %s "%(_str_func,error)) 

    def __buildModule__(self,*args,**kws):
        cgmRigBlockOLD.__buildModule__(self,*args,**kws)
        _mNodeSelf = self
        class fncWrap(cgmMeta.cgmMetaFunc):
            def __init__(self,*args,**kws): 
                super(fncWrap, self).__init__(*args,**kws)
                self.mi_mNode = _mNodeSelf
                self._str_func= "cgmMouthNoseBlock.__buildModule__(%s)"%self.mi_mNode.p_nameShort	
                #self._l_ARGS_KWS_DEFAULTS = [{'kw':'size',"default":None,'help':"Sizing parameter for the build","argType":"int"}]		
                self.__dataBind__(*args,**kws)	
                self.l_funcSteps = [{'step':'Mouth Build','call':self._checkMouthModule}]
                #=================================================================
            def _checkMouthModule(self):
                bfr_name = _mNodeSelf._d_buildKWS.get('name') or None
                bfr_position = _mNodeSelf._d_buildKWS.get('position') or None

                i_module = cgmMouthNose(name = bfr_name,
                                        position = bfr_position)
                _mNodeSelf.connectChildNode(i_module,"moduleTarget","helper")	

        return fncWrap(*args,**kws).go()	
        """
	try:
	    bfr_name = self._d_buildKWS.get('name') or None
	    bfr_position = self._d_buildKWS.get('position') or None

	    try:#Brow module
		#===================================================================
		i_module = cgmMouthNose(name = bfr_name,
		                      position = bfr_position)
		self.connectChildNode(i_module,"moduleTarget","helper")
	    except Exception,error:raise StandardError,"Failed to build eyeball module | error: %s "%(error)

	    except Exception,error:raise StandardError,"Failed to build eyelids module | error: %s "%(error)
	    try:#Mirror ============================================================
		if self.autoMirror:
		    pass
		    #if log.getEffectiveLevel() == 10:log.debug("%s >> mirror mode"%(_str_func))
	    except Exception,error:raise StandardError,"Failed to mirror | error: %s "%(error)

	    #self.__storeNames__()

	    #Size it
	    #self.__updateSizeData__()

	    #>>>Let's do our manual sizing
	    return i_module
	except Exception,error:raise StandardError,"%s >>>  error: %s "%(_str_func,error)
	"""
    def __storeNames__(self):
        #Store our names
        _str_func = "cgmMouthNoseBlock.__storeNames__(%s)"%self.p_nameShort   	
        if not self.getMessage("moduleTarget"):
            raise StandardError," %s >>> No Module!"%(_str_func)

        l_names= ['brow']
        if self.buildIris:l_names.append('iris')
        if self.buildPupil:l_names.append('pupil')
        self.moduleTarget.coreNames.value = l_names
        try:#Mirror ============================================================
            if self.autoMirror:
                self.moduleTarget.moduleMirror.coreNames.value = l_names
        except Exception,error:raise StandardError,"%s >>>  mirror error: %s "%(_str_func,error)

        return True

    def __updateSizeData__(self):
        """For overload"""
        _str_func = "cgmMouthNoseBlock.__updateSizeData__(%s)"%self.p_nameShort   
        #if log.getEffectiveLevel() == 10:log.debug(">>> %s >>> "%(_str_func) + "="*75)
        if not self.getMessage('moduleTarget'):
            raise StandardError,">>> %s >>> No module found "%(_str_func)

        i_module = self.mi_module#Lilnk
        l_pos = [self.getPosition()]
        d_helpercheck = cgmEyeballBlock.d_helperSettings#Link

        return True	

#Minor Utilities
def getSettingsColors(arg = None):
    try:
        return modules.returnSettingsData(('color'+arg.capitalize()),True)
    except:
        return modules.returnSettingsData('colorCenter',True)


#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
r9Meta.registerMClassInheritanceMapping()
#=========================================================================