"""
Module for building controls for cgmModules

"""
# From Python =============================================================
import copy
import re
import time
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid

from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import rayCaster as RayCast
from cgm.core.lib import rigging_utils as coreRigging
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.lib import meta_Utils as metaUtils
from cgm.core.lib import shapeCaster as ShapeCast
import cgm.core.lib.name_utils as NAMES
import cgm.core.lib.snap_utils as SNAP
#reload(Snap)
import cgm.core.lib.transform_utils as TRANS
from cgm.lib import (cgmMath,
                     locators,
                     modules,
                     distance,
                     dictionary,
                     rigging,
                     search,
                     curves,
                     lists,
                     )

from cgm.core.lib import nameTools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    def __init__(self,moduleInstance,controlTypes = [],targetObjects = [],storageInstance = False,b_midSplits = None,**kws): 
        """
        Class factor generating module controls

        @kws
        moduleInstance -- must be a module instance
        """
        self.d_controlBuildFunctions = {'cog':self.build_cog,
                                        'hips':self.build_hips,
                                        'segmentFK':self.build_segmentFKHandles,
                                        'segmentIK':self.build_segmentIKHandles,
                                        'segmentFK_Loli':self.build_segmentFKLoliHandles,
                                        'torsoIK':self.build_torsoIKHandles,
                                        'loliHandles':self.build_loliHandles,
                                        'midIK':self.build_midIKHandle,
                                        'footPivots':self.build_footPivots,
                                        'foot':self.build_footShape,
                                        'cap':self.build_moduleCap,
                                        'hand':self.build_handShape,
                                        'clavicle':self.build_clavicle,
                                        'eyeball':shapeCast_eyeball,
                                        'eyeballFK':self.build_eyeballFK,
                                        'eyeballIK':self.build_eyeballIK,
                                        'eyelids':shapeCast_eyelids,#self.build_eyelids,
                                        'eyeLook':shapeCast_eyeLook,#self.build_eyeLook
                                        'eyebrow':shapeCast_eyebrow,
                                        'mouthNose':shapeCast_mouthNose,	                                
                                        'eyeballSettings':self.build_eyeballSettings,
                                        'settings':self.build_settings}
        # Get our base info
        #==============	        
        #>>> module null data
        if not moduleInstance.isModule():
            log.error("Not a cgmModule: '%s'"%moduleInstance)
            return 
        if not mc.objExists(moduleInstance.mNode):
            raise Exception,"RigFactory.go.init Module instance no longer exists: '%s'"%moduleInstance

        if type(controlTypes) is not list:controlTypes = [controlTypes]

        self._strShortName = moduleInstance.p_nameShort  
        _str_funcName = "go.__init__(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)

        assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        	
        self._mi_module = moduleInstance# Link for shortness	

        #>>> Gather info
        #=========================================================
        try:
            self._b_midSplits = b_midSplits
            self.l_moduleColors = self._mi_module.getModuleColors()
            self._mi_puppet = self._mi_module.modulePuppet
            self.l_coreNames = self._mi_module.coreNames.value
            self._mi_templateNull = self._mi_module.templateNull#speed link
            self._mi_rigNull = self._mi_module.rigNull#speed link
            self._targetMesh = self._mi_puppet.getUnifiedGeo()
            if not self._targetMesh:
                _bfr = self._mi_puppet.getUnifiedGeo()
                if _bfr:
                    self._targetMesh = _bfr[0]
                else:
                    raise ValueError,"Need a mesh"
            self._ml_targetObjects = cgmMeta.validateObjListArg(targetObjects, cgmMeta.cgmObject,noneValid=True)
            self._ml_controlObjects = self._mi_templateNull.msgList_get('controlObjects')
            log.info('initial...done')
            #>>> part name 
            self.str_partName = self._mi_module.getPartNameBase()
            self.str_partType = self._mi_module.moduleType or False

            self._direction = self._mi_module.getMayaAttr('cgmDirection') or None
            log.info("part...done")
            #>>> Instances and joint stuff
            self.str_jointOrientation = str(modules.returnSettingsData('jointOrientation')) or 'zyx'#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<   
            self.f_skinOffset = self._mi_puppet.getMayaAttr('skinDepth') or 1 #Need to get from puppet!<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<		
            self._verifyCastObjects()#verify cast objects
            log.info('castObjects')
            self.d_returnControls = {}	
            self.md_ReturnControls = {}	
            self.d_returnPivots = {}		
            self.md_returnPivots = {}   
            self.md_fkControls = {}
            self.md_segmentHandles = {}
            self._baseModuleDistance = self._returnBaseDistance()
            self._baseModuleThickness = self._returnBaseThickness()
            
        except Exception,error:
            
            raise Exception,"{0} >> [Module data gather fail] error: {1}".format(self._strShortName,error)	
        
        #>>> We need to figure out which control to make
        #===================================================================================
        self.l_controlsToMakeArg = []	

        if controlTypes:#If we get an override
            for c in controlTypes:
                if self._validateControlArg(c):
                    self.l_controlsToMakeArg.append(c)
        log.debug("l_controlsToMakeArg: %s"%self.l_controlsToMakeArg)
        
        #self.d_controlShapes = mControlFactory.limbControlMaker(self.m,self.l_controlsToMakeArg)
        if not self.l_controlsToMakeArg:
            log.debug("No arguments for shapes to cast.Initializing only.")
        for key in self.l_controlsToMakeArg:
            try:
                try:
                    self.d_controlBuildFunctions[key](self,**kws)
                except:
                    self.d_controlBuildFunctions[key](**kws)
            except Exception,error:
                if kws:
                    cgmGeneral.walk_dat(kws)
                for arg in error.args:
                    log.error(arg)
                raise Exception,"controlBuildFunction Call {0} fail | error: {1}".format(key,error)
            #if key not in self.d_returnControls:
                #log.warning("Necessary control shape(s) was not built: '%s'"%key)
                #raise Exception,"Did not get all necessary controls built"

        if storageInstance:
            try:
                storageInstance._d_controlShapes = self.d_returnControls
                storageInstance._md_controlShapes = self.md_ReturnControls
                storageInstance._md_fkControls = self.md_fkControls
                storageInstance._md_controlPivots = self.md_returnPivots

            except Exception,error:
                log.error("storage fail]{%s}"%storageInstance) 
                raise Exception,"Did not get all necessary controls built"

        if self.ml_specialLocs:
            mc.delete([i_obj.mNode for i_obj in self.ml_specialLocs])

    def _validateControlArg(self,arg):
        """returns function"""
        if arg in self.d_controlBuildFunctions.keys():
            return True
        log.warning("_validateControlArg couldn't find: %s"%arg)
        return False

    def _pushKWsDict(self,d_kws = None,i=None, l_objectsToDo = None):
        """
        Pushes specific kws dict during 
        """
        if l_objectsToDo is None:
            l_objectsToDo = self.l_controlSnapObjects

        if type(d_kws) is not dict:
            raise Exception, "_pushKWsDict>> 'd_kws' arg not a dict: %s"%d_kws
        
        log.debug("_pushKWsDict >> " + "="*50)
        if d_kws:
            #push d_kws
            if d_kws.get(i):
                for k in d_kws[i].keys():
                    log.debug("%s: %s"%(k,d_kws[i].get(k)))
                    self.__dict__[k] = d_kws[i].get(k)
            elif i == len(l_objectsToDo)-1 and d_kws.get(-1):
                log.debug('last mode')
                for k in d_kws[-1].keys():
                    log.debug("%s: %s"%(k,d_kws[-1].get(k)))			
                    self.__dict__[k] = d_kws[-1].get(k)
            else:
                for k in d_kws['default'].keys():
                    log.debug("%s: %s"%(k,d_kws['default'].get(k)))			
                    self.__dict__[k] = d_kws['default'].get(k)
        log.debug("_pushKWsDict << " + "="*50)

        return True

    def _verifyCastObjects(self):
        """
        Some module types need more cast positions than exist (like a finger).
        This makes sure we have the ones we need and pushes them to the segment stuff
        """
        self.l_controlSnapObjects = []
        for mi_obj in self._ml_controlObjects:
            self.l_controlSnapObjects.append(mi_obj.helper.mNode)  
        self.l_segmentControls = []
        self.l_segmentHandles = []
        self.ml_specialLocs = []

        #Create end locs
        #if self._mi_module.moduleType.lower() in ['finger','thumb']:
        if self._mi_module.moduleType.lower() in ['asdf']:	
            mi_lastLoc = cgmMeta.cgmObject(self.l_controlSnapObjects[-1]).doLoc(fastMode = True)	
            mi_lastLoc.doGroup()
            #Distance stuff    
            d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,
                                                                  mi_lastLoc.mNode,
                                                                  self.str_jointOrientation[0]+'+',
                                                                  pierceDepth=self.f_skinOffset*15) or {}
            if not d_return.get('hit'):
                raise Exception,"go._verifyCastObjects>>failed to get hit to measure first distance"
            dist_cast = distance.returnDistanceBetweenPoints(mi_lastLoc.getPosition(),d_return['hit']) * 1.25
            mi_lastLoc.__setattr__("t"+self.str_jointOrientation[0],dist_cast*.6)#Move
            pBuffer = mi_lastLoc.parent
            mi_lastLoc.parent = False
            mc.delete(pBuffer)
            self.ml_specialLocs.append(mi_lastLoc)
            self.l_controlSnapObjects.append(mi_lastLoc.mNode)

        self.l_indexPairs = lists.parseListToPairs(list(range(len(self.l_controlSnapObjects))))
        self.l_segments = lists.parseListToPairs(self.l_controlSnapObjects)	    
        return True

    def _returnBaseThickness(self):
        #We're going to cast from the middle of our limb segment to reduce the chance of firing to nowhere
        #Start by casting along template up and out
        _str_funcName = "go._returnBaseThickness(%s)"%self._strShortName
        log.info(">>> %s ..."%(_str_funcName) + "="*75)
        log.info("%s >> self.l_controlSnapObjects = %s"%(_str_funcName,self.l_controlSnapObjects))
        log.info("%s >> self._targetMesh = %s"%(_str_funcName,self._targetMesh))	    
        if self.l_controlSnapObjects and self._targetMesh:
            midIndex = int(len(self.l_controlSnapObjects)/2)
            log.info("%s >> midIndex = %s"%(_str_funcName,midIndex))	    		
            try:
                d_return = ShapeCast.returnBaseControlSize(self.l_controlSnapObjects[midIndex],self._targetMesh,axis=[self.str_jointOrientation[1],self.str_jointOrientation[2]])
            except Exception,error:
                log.info("cast objects: {0}".format(self.l_controlSnapObjects))
                log.info("target mesh: {0}".format(self._targetMesh))
                log.info("axis: {0}".format(self.str_jointOrientation))
                raise Exception,"shapeCast.returnBaseControlSize send | {0}".format(error)
            #log.info("%s >> d_return = %s"%(_str_funcName,d_return))	    		
            #l_lengths = [d_return[k] for k in d_return.keys()]
            #log.info("%s >> l_lengths = %s"%(_str_funcName,l_lengths))	    				
            #average = (sum(l_lengths))/len(l_lengths)
            return d_return['average'] #*1.25
        elif self._mi_module.getMessage('helper'):
            return distance.returnBoundingBoxSizeToAverage(self._mi_module.getMessage('helper'))
        else:
            raise Exception, "%s >> Not enough info to figure out"%_str_funcName

    def _returnBaseDistance(self):
        if len(self.l_controlSnapObjects) >1:
            return distance.returnDistanceBetweenObjects(self.l_controlSnapObjects[0],self.l_controlSnapObjects[-1])/10
        return 1
    def build_eyelids(self):
        _str_funcName = "go.build_eyelids(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 	
        try:
            try:#>>Info gather =====================================================================
                mi_helper = self._mi_module.helper
                if not mi_helper:raise Exception,"No suitable helper found"    

                try:ml_uprLidHandles = self._mi_rigNull.msgList_get('handleJoints_upr')
                except Exception,error:raise Exception,"Missing uprlid handleJoints | error: %s "%(error)
                try:ml_lwrLidHandles = self._mi_rigNull.msgList_get('handleJoints_lwr',asMeta = False)
                except Exception,error:raise Exception,"Missing lwrlid handleJoints | error: %s "%(error)  
                log.info("%s >>> ml_uprLidHandles : %s "%(_str_funcName,[mObj.mNode for mObj in ml_uprLidHandles]))	
                log.info("%s >>> ml_lwrLidHandles : %s"%(_str_funcName,[mObj.mNode for mObj in ml_lwrLidHandles]))		

                __baseDistance = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_uprLidHandles]) /2 
                log.info("%s >>> baseDistance : %s"%(_str_funcName,__baseDistance))				
            except Exception,error:
                raise Exception,"Gather Data fail! | error: %s"%(error)  

            ml_handleCrvs = []
            for mObj in ml_uprLidHandles + ml_lwrLidHandles:
                try:
                    if mObj.getAttr('isSubControl') or mObj in [ml_uprLidHandles[0],ml_uprLidHandles[-1]]:
                        _size = __baseDistance * .6
                    else:_size = __baseDistance
                    mi_crv =  cgmMeta.asMeta(curves.createControlCurve('circle',size = _size,direction=self.str_jointOrientation[0]+'+'),'cgmObject', setClass=False)	
                    SNAP.go(mi_crv,mObj.mNode,move=True,orient=False)
                    str_grp = mi_crv.doGroup()
                    mi_crv.__setattr__("t%s"%self.str_jointOrientation[0],__baseDistance)
                    mi_crv.parent = False
                    mc.delete(str_grp)
                    #>>Color curve		    		    
                    if mObj.getAttr('isSubControl'):
                        curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[1])  
                    else:curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])  
                    #>>Copy tags and name		    
                    mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                    mi_crv.doName()
                    mi_crv.connectChildNode(mObj,'handleJoint','controlCurve')
                    ml_handleCrvs.append(mi_crv)
                    #>>Copy pivot
                    mi_crv.doCopyPivot(mObj.mNode)
                except Exception,error:
                    raise Exception,"Curve create fail! handle: '%s' | error: %s"%(mObj.p_nameShort,error)  

            self.d_returnControls['l_handleCurves'] = [mObj.p_nameShort for mObj in ml_handleCrvs]
            self.md_ReturnControls['ml_handleCurves'] = ml_handleCrvs
            self._mi_rigNull.msgList_connect('handleCurves',ml_handleCrvs,'owner')
            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        except Exception,error:
            log.error("%s >>> fail]{%s}"%(_str_funcName,error) )
            return False

    def build_eyeballSettings(self):
        _str_funcName = "go.build_eyeballSettings(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        try:
            mi_helper = self._mi_module.helper
            _baseDistance = distance.returnDistanceBetweenObjects(mi_helper.mNode, mi_helper.pupilHelper.mNode)

            mi_crv = cgmMeta.asMeta( curves.createControlCurve('gear',
                                                                  direction = 'z+',
                                                                  size = _baseDistance*.5,
                                                                  absoluteSize=False),'cgmObject',setClass=False)
            SNAP.go(mi_crv,mi_helper.mNode)
            mi_tmpGroup = cgmMeta.cgmObject( mi_crv.doGroup())
            mi_crv.__setattr__('t%s'%self.str_jointOrientation[0],_baseDistance * 2)
            mi_crv.parent = False
            mi_tmpGroup.delete()

            #>>Copy tags and name
            mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
            mi_crv.addAttr('cgmType',attrType='string',value = 'settings',lock=True)
            mi_crv.doName()          	    

            #Color
            curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[1])    
            self.d_returnControls['settings'] = mi_crv.mNode
            self.md_ReturnControls['settings'] = mi_crv
            self._mi_rigNull.connectChildNode(mi_crv,'shape_settings','owner')
            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        except Exception,error:
            log.error("%s >>> fail]{%s}"%(_str_funcName,error) )
            return False

    def build_eyeballFK(self):
        _str_funcName = "go.build_eyeballFK(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)	
        time_func = time.clock() 		
        try:
            mi_helper = self._mi_module.helper
            _baseDistance = distance.returnDistanceBetweenObjects(mi_helper.mNode, mi_helper.pupilHelper.mNode)	    
            mi_crvBase = cgmMeta.cgmObject( curves.createControlCurve('circle',
                                                                      direction = 'z+',
                                                                      size = _baseDistance * .75,
                                                                      absoluteSize=False),setClass=False)
            SNAP.go(mi_crvBase,mi_helper.mNode)
            mi_tmpGroup = cgmMeta.cgmObject( mi_crvBase.doGroup())
            mi_crvBase.__setattr__('t%s'%self.str_jointOrientation[0],_baseDistance * 2)
            mi_crvBase.parent = False
            mi_tmpGroup.delete()

            #Make a trace curve
            _str_trace = mc.curve (d=1, ep = [mi_helper.getPosition(),mi_crvBase.getPosition()], os=True)#build curves as we go to see what's up
            log.info(_str_trace)
            l_curvesToCombine = [_str_trace,mi_crvBase.mNode]

            #>>>Combine the curves
            try:newCurve = curves.combineCurves(l_curvesToCombine) 
            except Exception,error:raise Exception,"Failed to combine | error: %s"%error

            mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(mi_helper.mNode,False) )

            try:curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
            except Exception,error:raise Exception,"Parent shape in place fail | error: %s"%error

            mc.delete(_str_trace)

            #>>Copy tags and name
            mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
            mi_crv.addAttr('cgmType',attrType='string',value = 'eyeball_FK',lock=True)
            mi_crv.doName()          	    

            #Color
            curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])    
            self.d_returnControls['eyeballFK'] = mi_crv.mNode
            self.md_ReturnControls['eyeballFK'] = mi_crv
            self._mi_rigNull.connectChildNode(mi_crv,'shape_eyeballFK','owner')

            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        except Exception,error:
            log.error("%s >>> fail]{%s}"%(_str_funcName,error) )
            return False

    def build_eyeballIK(self):
        _str_funcName = "go.build_eyeballIK(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        try:
            mi_helper = self._mi_module.helper
            _baseDistance = distance.returnDistanceBetweenObjects(mi_helper.mNode, mi_helper.pupilHelper.mNode)	    	    
            mi_crv = cgmMeta.asMeta( curves.createControlCurve('fatCross',
                                                                  direction = 'z+',
                                                                  size = _baseDistance*.75,
                                                                  absoluteSize=False),'cgmObject',
                                        setClass=False)
            SNAP.go(mi_crv,mi_helper.mNode)
            mi_tmpGroup = cgmMeta.cgmObject( mi_crv.doGroup())
            mi_crv.__setattr__('t%s'%self.str_jointOrientation[0],_baseDistance * 6)
            mi_crv.parent = False
            mi_tmpGroup.delete()

            #>>Copy tags and name
            mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
            mi_crv.addAttr('cgmType',attrType='string',value = 'eyeball_IK',lock=True)
            mi_crv.doName()          	    

            #Color
            curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])    
            self.d_returnControls['eyeballFK'] = mi_crv.mNode
            self.md_ReturnControls['eyeballFK'] = mi_crv
            self._mi_rigNull.connectChildNode(mi_crv,'shape_eyeballIK','owner')

            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        except Exception,error:
            log.error("%s >>> fail]{%s}"%(_str_funcName,error) )
            return False

    def build_eyeLook(self):
        _str_funcName = "go.build_eyeLook(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)	
        time_func = time.clock() 		
        try:#we need to find an eye module/head module
            mi_helper = self._mi_module.helper
            _baseDistance = distance.returnDistanceBetweenObjects(mi_helper.mNode, mi_helper.pupilHelper.mNode)	    	    
            mi_crv = cgmMeta.asMeta( curves.createControlCurve('arrow4Fat',
                                                                  direction = 'z+',
                                                                  size = _baseDistance * 1.5,
                                                                  absoluteSize=False),'cgmObject',setClass=False)	    
            SNAP.go(mi_crv,mi_helper.mNode)
            mi_tmpGroup = cgmMeta.cgmObject( mi_crv.doGroup())
            mi_crv.__setattr__('t%s'%self.str_jointOrientation[0],_baseDistance * 6)

            mi_crv.parent = False
            mi_tmpGroup.delete()

            #if self.str_partType == "eyeball":
            mi_crv.__setattr__('t%s'%self.str_jointOrientation[2],0)

        except Exception,error:
            log.error("%s >>> Find info | %s"%(_str_funcName,error) )

        try:    
            #>>Copy tags and name
            #mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
            mi_crv.addAttr('cgmName',attrType='string',value = self._mi_puppet.cgmName,lock=True)	    	    
            mi_crv.addAttr('cgmTypeModifier',attrType='string',value = 'eyeLook',lock=True)
            mi_crv.doName()          	    

            #Color
            l_color = modules.returnSettingsData('colorCenter',True)
            curves.setCurveColorByName(mi_crv.mNode,l_color[0])    
            self.d_returnControls['eyeLook'] = mi_crv.mNode
            self.md_ReturnControls['eyeLook'] = mi_crv
            self._mi_rigNull.connectChildNode(mi_crv,'shape_eyeLook','owner')

            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        except Exception,error:
            log.error("%s >>> fail]{%s}"%(_str_funcName,error) )
            return False

    def build_cog(self):
        _str_funcName = "go.build_cog(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)	
        time_func = time.clock() 	
        
        multiplier = 1.1
        #tmplRoot = self._mi_templateNull.root.mNode
        tmplRoot = self._ml_controlObjects[0]
        #mi_loc = tmplRoot.doLoc(fastMode = True)#make loc for sizing
        #mi_loc.doGroup()#group to zero
        #sizeReturn = ShapeCast.returnBaseControlSize(mi_loc,self._targetMesh,axis=['x','y'])#Get size
        #fl_size = sizeReturn.get('average')
        #mc.delete(mi_loc.parent)#delete loc	    
        #ize = fl_size/4
        size = self._baseModuleThickness/2
        ml_curvesToCombine = []
        mi_crvBase = cgmMeta.asMeta( curves.createControlCurve('arrowSingleFat3d',direction = 'y-',size = size,absoluteSize=False),'cgmObject',setClass=False)
        mi_crvBase.scaleY = 2
        mi_crvBase.scaleZ = .75
        SNAP.go(mi_crvBase, tmplRoot.mNode) #Snap it
        i_grp = cgmMeta.cgmObject( mi_crvBase.doGroup() )
        
        try:
            for i,rot in enumerate([0,90,90,90]):
                log.debug(rot)
                #rot, shoot, move, dup
                #log.debug("curve: %s | rot int: %s | grp: %s"%(mi_crvBase.mNode,i, i_grp.mNode))
                i_grp.rotateY = i_grp.rotateY + rot
                #Shoot
                d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_crvBase.mNode)
                if not d_return.get('hit'):
                    log.info(d_return)
                    raise Exception,"build_cog>> failed to get hit. Mesh '{0}' object probably isn't in mesh".format(self._targetMesh.mNode)
                #log.debug("hitDict: %s"%d_return)
                dist = distance.returnDistanceBetweenPoints(mi_crvBase.getPosition(),d_return['hit'])+(self.f_skinOffset*7)#self._baseModuleThickness/4
                #log.debug("dist: %s"%dist)
                #log.debug("crv: %s"%mi_crvBase.mNode)
                mi_crvBase.__setattr__("tz",dist)
                mi_tmp = mi_crvBase.doDuplicate(parentOnly=False)
                #log.debug(mi_tmp)
                mi_tmp.parent = False
                ml_curvesToCombine.append(mi_tmp)
                mi_crvBase.__setattr__("tz",0)
        except Exception,error:
            raise Exception,"Rotate dup | {0}".format(error)                    

        i_grp.delete()
        
        try:
            log.info(ml_curvesToCombine)
            mi_crv = cgmMeta.cgmObject( curves.combineCurves([i_obj.mNode for i_obj in ml_curvesToCombine]) )
            #log.debug("mi_crv: %s"%mi_crv.mNode)
        except Exception,error:
            raise Exception,"Reinitialize | {0}".format(error)            

        try:#>>Copy tags and name
            mi_crv.addAttr('cgmName',attrType='string',value = 'cog',lock=True)        
            mi_crv.addAttr('cgmType',attrType='string',value = 'controlCurve',lock=True)
            mi_crv.doName()        

            mc.xform(mi_crv.mNode, cp=True)
            mc.makeIdentity(mi_crv.mNode, apply=True,s=1,n=0)	
        except Exception,error:
            raise Exception,"Copy tags | {0}".format(error)
        
        try:#>>> Color
            curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])    
            self.d_returnControls['cog'] = mi_crv.mNode
            self.md_ReturnControls['cog'] = mi_crv
            self._mi_rigNull.connectChildNode(mi_crv,'shape_cog','owner')
        except Exception,error:
            raise Exception,"Color | {0}".format(error)
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         



    def build_hips(self):
        _str_funcName = "go.build_hips(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)	
        time_func = time.clock() 	

        distanceMult = .5	    
        orientHelper = self.l_controlSnapObjects[1]
        log.debug(orientHelper)
        mi_loc = cgmMeta.cgmNode(orientHelper).doLoc(fastMode = True)#make loc for sizing
        mi_loc.doGroup()#group to zero

        d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_loc.mNode,'z-')
        if not d_return.get('hit'):
            log.info(d_return)
            log.info(self._targetMesh)
            raise Exception,"build_hips>>failed to get hit. Master template object probably isn't in mesh"
        dist = distance.returnDistanceBetweenPoints(mi_loc.getPosition(),d_return['hit'])
        mi_loc.tz = -dist *.2	

        returnBuffer = ShapeCast.createWrapControlShape(mi_loc.mNode,self._targetMesh,
                                                        curveDegree=3,
                                                        insetMult = .2,
                                                        closedCurve=True,
                                                        points = 8,
                                                        closestInRange=False,
                                                        maxDistance=self._baseModuleThickness,                                                        
                                                        posOffset = [0,0,self.f_skinOffset*3],
                                                        extendMode='')
        mi_crvRound = returnBuffer['instance']

        str_traceCrv = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_loc.mNode,
                                                      latheAxis='x',aimAxis='y+',
                                                      curveDegree=3,
                                                      closedCurve=False,
                                                      closestInRange=False,
                                                      maxDistance=self._baseModuleThickness,
                                                      l_specifiedRotates=[0,-30,-60,-90,-120,-150,-180],
                                                      posOffset = [0,0,self.f_skinOffset*3],
                                                      )

        mi_crv = cgmMeta.cgmObject ( curves.combineCurves([mi_crvRound.mNode,str_traceCrv]) )

        mc.delete(mi_loc.getParents()[-1])

        #>>Copy tags and name
        mi_crv.addAttr('cgmName',attrType='string',value = 'hips',lock=True)        
        mi_crv.addAttr('cgmType',attrType='string',value = 'controlCurve',lock=True)
        mi_crv.doName()        

        #>>> Color
        coreRigging.match_transform(mi_crv.mNode, self._ml_controlObjects[1].mNode)
        
        curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])    
        self.d_returnControls['hips'] = mi_crv.mNode
        self.md_ReturnControls['hips'] = mi_crv
        self._mi_rigNull.connectChildNode(mi_crv,'shape_hips','owner')

        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         


    #@cgmGeneral.Timer    
    def build_segmentFKHandles(self):
        _str_funcName = "go.build_segmentFKHandles(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        try:
            l_segmentControls = []
            ml_segmentControls = []
            if self.str_partType == 'torso':
                #l_segmentsToDo = self.l_segments[1:-1]
                l_segmentsToDo = self.l_segments[1:]
            else:
                l_segmentsToDo = self.l_segments
            log.debug("segments: %s"%l_segmentsToDo)
            self.l_specifiedRotates = None
            d_kws = False
            self.posOffset = [0,0,self.f_skinOffset*3]
            self.maxDistance = self._baseModuleThickness 
            self.joinHits = [0,2,4,6,8]	  
            self.points = 10
            self.closestInRange = False

            if self._mi_module.moduleType.lower() in ['finger','thumb']:
                self.posOffset = [0,0,self.f_skinOffset/2]
                self.maxDistance = self._baseModuleThickness * .75
                self.joinHits = [0,5]	    
                self.closestInRange = True

            for i,seg in enumerate(l_segmentsToDo):	
                if d_kws:		
                    self._pushKWsDict(d_kws,i)
                returnBuffer = ShapeCast.createWrapControlShape(seg,self._targetMesh,
                                                                points = self.points,
                                                                curveDegree=1,
                                                                insetMult = .3,
                                                                posOffset = self.posOffset,
                                                                joinMode=True,
                                                                maxDistance=self.maxDistance,		                                      
                                                                joinHits = self.joinHits,
                                                                closestInRange=self.closestInRange,
                                                                extendMode='segment')
                mi_crv = returnBuffer['instance']	    
                #>>> Color
                curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
                mi_crv.addAttr('cgmType',attrType='string',value = 'segFKCurve',lock=True)	
                mi_crv.doName()

                #Store for return
                l_segmentControls.append( mi_crv.mNode )
                ml_segmentControls.append( mi_crv )

            self.d_returnControls['segmentFK'] = l_segmentControls 
            self.md_ReturnControls['segmentFK'] = ml_segmentControls
            self._mi_rigNull.msgList_connect('shape_segmentFK',ml_segmentControls,'owner')
            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        except Exception,error:
            log.error("build_segmentFKHandles fail]{%s}"%error) 
            return False

    #@cgmGeneral.Timer    
    def build_segmentFKLoliHandles(self):
        _str_funcName = "go.build_segmentFKLoliHandles(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 	
        
        l_segmentControls = []
        ml_segmentControls = []
        if self.str_partType == 'torso':
            l_toDo = self.l_controlSnapObjects[1:-1]
        else:
            #l_toDo = self.l_segments
            l_toDo = self.l_controlSnapObjects
            
        #figure out our settings
        #================================================================
        #defaults first
        d_kws = {}
        self.posOffset = []
        self.l_specifiedRotates = None
        self.joinMode = False
        self.closedCurve = False
        self.rotateBank = None
        self.latheAxis = 'z'
        self.aimAxis = 'y+'
        self.rotateBank = None	
        self.rootOffset = []
        self.rootRotate = None
        self.posOffset = [0,0,self._baseModuleDistance *2]
        self.subSize = self.f_skinOffset*5
        self.curveDegree = 1
        self.minRotate = None
        self.maxRotate = None
        self.vectorOffset = None
        if 'neck' in self.str_partType:
            d_kws = {'default':{'posOffset':[],
                                'vectorOffset':self.f_skinOffset*5,                                
                                'minRotate':-70,
                                'maxRotate':70,                                
                                'latheAxis':'z',
                                #'subSize':self._baseModuleDistance * 2,
                                'closedCurve':False,
                                'rootOffset':[],
                                'aimAxis':'y+'},
                     0:{'rootOffset':[0,0,2],},
                     -1:{'l_specifiedRotates':None,
                         'vectorOffset':self.f_skinOffset*5,
                         'points':9,
                         'rootOffset':[0,0,0],
                         'closedCurve':False,
                         'curveDegree':3,
                         'minRotate':-90,
                         'maxRotate':90},}
            #self.posOffset = [0,0,self.f_skinOffset*5]
            #self.l_specifiedRotates = [-30,-10,0,10,30]
            #self.latheAxis = 'z'
            #self.aimAxis = 'y+'
            
        elif 'leg' in self.str_partType:
            d_kws = {'default':{'closedCurve':False,
                                'latheAxis':'z',
                                'l_specifiedRotates':[-60,-40,-20,0,20,40,60],
                                'rootOffset':[],
                                'rootRotate':None},
                     0:{},
                     -2:{}}	
            d_kws[0]['l_specifiedRotates'] = [-110,-90,-60,-30,0,30,60,90,110]
            d_kws[0]['rootOffset'] = [0,0,self.f_skinOffset*8]	

            self.posOffset = [0,0,self.f_skinOffset*3]
            if self._direction == 'left':
                self.aimAxis = 'x+'
            else:self.aimAxis = 'x-'
            
        elif 'arm' in self.str_partType:
            d_kws = {'default':{'closedCurve':True,
                                'latheAxis':'z',
                                'rootOffset':[],
                                'rootRotate':None},
                     0:{'rootOffset':[0,0,self.f_skinOffset*8]}}	
            #d_kws[0]['l_specifiedRotates'] = [-90,-60,-30,0,30,60,90]
            #d_kws[0]['closedCurve'] = False

            self.posOffset = [0,0,self.f_skinOffset*3]
            if self._direction == 'left':
                self.aimAxis = 'x+'
            else:self.aimAxis = 'x-'

        elif self.str_partType in ['index','middle','ring','pinky','thumb','finger']:
            d_kws = {'default':{'closedCurve':True,
                                'latheAxis':'z',
                                'l_specifiedRotates':[],
                                'maxDistance':self._baseModuleThickness,
                                'rootOffset':[],
                                'rootRotate':None},
                     0:{}}	
            d_kws[0]['l_specifiedRotates'] = [-60,-30,0,30,60]
            d_kws[0]['maxDistance'] = self._baseModuleThickness * 10	
            d_kws[0]['closedCurve'] = False
            self.posOffset = [0,0,self.f_skinOffset/2]
        
        log.debug("Snap Objects: %s"%l_toDo)
        for i,obj in enumerate(l_toDo):			
            #make ball
            self._pushKWsDict(d_kws,i)
            log.info("On obj: {0}".format(NAMES.short(obj)))
            
            #Few more special cases
            """if cgmMeta.cgmObject(obj).getAttr('cgmName') in ['ankle']:
                log.debug('Special rotate mode')
                self.rootRotate = [0,0,0]
                self.latheAxis = 'y'"""
                
            returnBuffer = ShapeCast.createWrapControlShape(obj,self._targetMesh,
                                                            curveDegree=self.curveDegree,
                                                            insetMult = .2,
                                                            points = 9,
                                                            closedCurve= self.closedCurve,
                                                            aimAxis = self.aimAxis,
                                                            latheAxis = self.latheAxis,
                                                            minRotate = self.minRotate,
                                                            maxRotate = self.maxRotate,
                                                            subSize=self.subSize ,
                                                            vectorOffset=self.vectorOffset,
                                                            l_specifiedRotates = self.l_specifiedRotates,
                                                            posOffset = self.posOffset,
                                                            rootOffset = self.rootOffset,
                                                            rootRotate = self.rootRotate,
                                                            maxDistance=self._baseModuleThickness,
                                                            extendMode='loliwrap')
            
            mi_newCurve = returnBuffer['instance']
            mi_newCurve.doCopyPivot(obj)
            
            if 'head' in obj:
                print 'Head mode!'
                crv1 = ShapeCast.createMeshSliceCurve(self._targetMesh,obj,'y','z+',
                                                      minRotate=-90,maxRotate=90,
                                                      closedCurve=False,
                                                      #posOffset= [0,0,self.f_skinOffset*5],
                                                      vectorOffset=self.vectorOffset,
                                                     )
                crv2 = ShapeCast.createMeshSliceCurve(self._targetMesh,obj,'x','z+',
                                                      minRotate=-90,maxRotate=0,
                                                      closedCurve=False,
                                                      offsetMode='vector',
                                                      #posOffset= [0,0,self.f_skinOffset*5],
                                                      vectorOffset=self.vectorOffset,
                                                     )                
                coreRigging.shapeParent_in_place(mi_newCurve.mNode,[crv1,crv2],False)
            #>>> Color
            curves.setCurveColorByName(mi_newCurve.mNode,self.l_moduleColors[0])                    
            mi_newCurve.addAttr('cgmType',attrType='string',value = 'loliHandle',lock=True)	
            mi_newCurve.doName()
            
            #Store for return
            l_segmentControls.append( mi_newCurve.mNode )
            ml_segmentControls.append( mi_newCurve )	
            
            

        self.d_returnControls['segmentFK_Loli'] = l_segmentControls 
        self.md_ReturnControls['segmentFK_Loli'] = ml_segmentControls
        self._mi_rigNull.msgList_connect('shape_segmentFKLoli',ml_segmentControls,'owner')
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         	    



    #@cgmGeneral.Timer    
    def build_moduleCap(self):
        try:
            _str_funcName = "go.build_moduleCap(%s)"%self._strShortName
            log.info(">>> %s >>> "%(_str_funcName) + "="*75)
            time_func = time.clock() 		    
            l_segmentControls = []
            ml_segmentControls = []
            log.debug("self._targetMesh: %s"%self._targetMesh)
            #figure out our settings
            #================================================================
            #defaults first
            d_kws = {}
            self.posOffset = []
            self.l_specifiedRotates = None
            self.joinMode = False
            self.closedCurve = True
            self.latheAxis = self.str_jointOrientation[0]
            self.aimAxis = self.str_jointOrientation[1] + '+'
            self.rotateBank = None	
            self.rootOffset = []
            self.rootRotate = None	
            _snapObject = self.l_controlSnapObjects[-1]
            self.maxDistance = self._baseModuleThickness
            _lastCreated = False
            if self.str_partType in ['index','middle','ring','pinky','thumb','finger']:
                d_kws = {'default':{'rootOffset':[],
                                    'maxDistance': self._baseModuleThickness * 1.5,
                                    'posOffset':[0,0,self.f_skinOffset/2],
                                    'rootRotate':None},
                         0:{}}	

                mi_lastLoc = cgmMeta.cgmObject(self.l_controlSnapObjects[-2]).doLoc(fastMode = True)	
                mi_lastLoc.doGroup()
                #Distance stuff    
                d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,
                                                                      mi_lastLoc.mNode,
                                                                      self.str_jointOrientation[0]+'+',
                                                                      pierceDepth=self.f_skinOffset*15) or {}
                if not d_return.get('hit'):
                    raise Exception,"go._verifyCastObjects>>failed to get hit to measure first distance"
                dist_cast = distance.returnDistanceBetweenPoints(mi_lastLoc.getPosition(),d_return['hit']) * 1.25
                mi_lastLoc.__setattr__("t"+self.str_jointOrientation[0],dist_cast*.6)#Move
                pBuffer = mi_lastLoc.parent
                mi_lastLoc.parent = False
                mc.delete(pBuffer)
                self.ml_specialLocs.append(mi_lastLoc)
                _snapObject = mi_lastLoc.mNode

            #>>>Cast
            self._pushKWsDict(d_kws)
            log.debug("snapObject: %s"%_snapObject)
            returnBuffer = ShapeCast.createWrapControlShape(_snapObject,self._targetMesh,
                                                            curveDegree=3,
                                                            insetMult = .2,
                                                            closedCurve= self.closedCurve,
                                                            aimAxis = self.aimAxis,
                                                            latheAxis = self.latheAxis,
                                                            l_specifiedRotates = self.l_specifiedRotates,
                                                            posOffset = self.posOffset,
                                                            rootOffset = self.rootOffset,
                                                            rootRotate = self.rootRotate,
                                                            maxDistance=self.maxDistance,
                                                            extendMode='endCap')
            mi_newCurve = returnBuffer['instance']
            mi_newCurve.doCopyPivot(_snapObject)

            #>>> Color
            curves.setCurveColorByName(mi_newCurve.mNode,self.l_moduleColors[0])                    
            mi_newCurve.addAttr('cgmType',attrType='string',value = 'moduleCap',lock=True)	
            mi_newCurve.doName()

            #Store for return
            l_segmentControls.append( mi_newCurve.mNode )
            ml_segmentControls.append( mi_newCurve )		

            self.d_returnControls['moduleCap'] = mi_newCurve.mNode 
            self.md_ReturnControls['moduleCap'] = mi_newCurve
            self._mi_rigNull.connectChildNode(mi_newCurve,'shape_moduleCap','owner')

            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        except Exception,error:
            log.error("build_moduleCap fail]{%s}"%error) 
            return False
    #@cgmGeneral.Timer    
    def build_clavicle(self):
        """
        build foot shape and pivot locs at the same time
        """
        _str_funcName = "go.build_clavicle(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        l_segmentControls = []
        ml_SegmentControls = []
        mi_startObj = False
        mi_endObj = False

        #Our controls
        #============================================================================	
        #find the foot. 1) Build search dict	
        ml_controlSnapObjects = []
        for mi_obj in self._ml_controlObjects:
            ml_controlSnapObjects.append(mi_obj.helper)  
        log.debug("helperObjects: %s"%[i_obj.getShortName() for i_obj in ml_controlSnapObjects])
        if len(ml_controlSnapObjects) > 2:
            raise Exception,"go.build_clavicle>>> Must have only 2 control objects. Found: %s"%(len(ml_controlSnapObjects))

        mi_startObj = ml_controlSnapObjects[0]
        mi_endObj = ml_controlSnapObjects[1]

        #Get our helper objects
        #============================================================================
        mi_startLoc = mi_startObj.doLoc(fastMode = True)
        mi_endLoc = mi_endObj.doLoc(fastMode = True)

        #Get our distance for our casts
        if self._direction == 'left':
            self.aimAxis = self.str_jointOrientation[2] + '-'
            axis_distanceDirectionCast = self.str_jointOrientation[2] + '+'
            l_specifiedRotates = [-15,-30,-90,-120,-180]
            rootRotate = -30
        else:
            self.aimAxis = self.str_jointOrientation[2] + '+'
            axis_distanceDirectionCast = self.str_jointOrientation[2] + '-'	    
            l_specifiedRotates = [15,30,90,120,180]
            rootRotate = 30	    

        dist_inset = distance.returnDistanceBetweenPoints(mi_endLoc.getPosition(),mi_startLoc.getPosition()) *.3

        #Move our cast locs
        mi_startLoc.doGroup()#zero
        mi_endLoc.doGroup()#zero
        mi_startLoc.__setattr__('t%s'%self.str_jointOrientation[0],dist_inset)
        mi_endLoc.__setattr__('t%s'%self.str_jointOrientation[0],-dist_inset/2)	
        mi_startLoc.__setattr__('r%s'%self.str_jointOrientation[1],rootRotate)
        mi_endLoc.__setattr__('r%s'%self.str_jointOrientation[1],rootRotate)

        #mi_castLoc = cgmMeta.dupe(mi_startLoc,asMeta = True)[0]
        mi_castLoc = mi_startLoc.doDuplicate()
        
        Snap.go(mi_castLoc,self._targetMesh,True,False,midSurfacePos=True, axisToCheck = [self.str_jointOrientation[2]])
        
        #Distance stuff    
        d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh, mi_endLoc.mNode, axis_distanceDirectionCast, pierceDepth=self.f_skinOffset*2) or {}
        if not d_return.get('hit'):
            raise Exception,"go.build_clavicle>>failed to get hit to measure first distance"
        dist_cast = distance.returnDistanceBetweenPoints(mi_endLoc.getPosition(),d_return['hit']) * 1.25

        log.debug("go.build_clavicle>>cast distance: %s"%dist_cast)
        log.debug("go.build_clavicle>>inset distance: %s"%dist_inset)

        #Cast our stuff
        #============================================================================
        self.posOffset = [0,0,self.f_skinOffset*3]
        self.latheAxis = self.str_jointOrientation[0]
        log.debug("aim: %s"%self.aimAxis)
        log.debug("lathe: %s"%self.latheAxis)

        d_startReturn = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_startLoc.mNode,offsetMode='vector',maxDistance = dist_cast,l_specifiedRotates = l_specifiedRotates,
                                                       closedCurve = False,curveDegree=3,midMeshCast=True,axisToCheck=['x'],posOffset = self.posOffset,returnDict = True,
                                                       latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)

        d_endReturn = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_endLoc.mNode,offsetMode='vector',maxDistance = dist_cast,l_specifiedRotates = l_specifiedRotates,
                                                     closedCurve = False,curveDegree=3,midMeshCast=True,axisToCheck=['x'],posOffset = self.posOffset,returnDict = True,
                                                     latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)


        #Let's collect the points to join

        l_curvesToCombine = [d_startReturn['curve'],d_endReturn['curve']]	

        joinReturn = ShapeCast.joinCurves(l_curvesToCombine)

        l_curvesToCombine.extend(joinReturn)

        mc.delete([mi_startLoc.parent,mi_endLoc.parent])

        #Combine and finale
        #============================================================================
        newCurve = curves.combineCurves(l_curvesToCombine) 
        mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(mi_startObj.mNode,False) )
        curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
        mc.delete(newCurve)

        #>>> Color
        curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
        mi_crv.doCopyNameTagsFromObject(mi_startObj.mNode,ignore = ['cgmType'])
        mi_crv.addAttr('cgmType',attrType='string',value = 'clavicle',lock=True)	    
        mi_crv.doName()

        self.d_returnControls['clavicle'] = mi_crv.mNode 		
        self.md_ReturnControls['clavicle'] = mi_crv	
        self._mi_rigNull.connectChildNode(mi_crv,'shape_clavicle','owner')

        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         


    #@cgmGeneral.Timer	
    def build_midIKHandle(self):
        _str_funcName = "go.build_midIKHandle(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        try:
            l_segmentControls = []
            ml_segmentControls = []

            mi_mid = False
            if 'arm' in self.str_partType:
                for obj in self.l_controlSnapObjects:
                    if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'elbow':
                        mi_mid = cgmMeta.cgmObject(obj)
                        break
            if 'leg' in self.str_partType:
                for obj in self.l_controlSnapObjects:
                    if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'knee':
                        mi_mid = cgmMeta.cgmObject(obj)
                        break   
            if not mi_mid:
                raise Exception, "build_midIKHandle>>> currently needs an arm or leg"

            #figure out our settings
            #================================================================
            #defaults first
            """
	    returnBuffer = ShapeCast.createWrapControlShape(mi_mid.mNode,self._targetMesh,
	                                                    points = 10,
	                                                    curveDegree=3,
	                                                    insetMult = .5,
	                                                    posOffset = [0,0,self.f_skinOffset*3],
	                                                    joinMode=True,
	                                                    joinHits = [0,5],
	                                                    extendMode='cylinder')

	    mi_newCurve = returnBuffer['instance']"""
            mi_newCurve = cgmMeta.cgmObject(curves.createControlCurve('sphere',size = self._baseModuleThickness * .75))
            mi_newCurve.doCopyNameTagsFromObject(mi_mid.mNode)

            SNAP.go(mi_newCurve,obj,True, True)#Snap to main object

            #>>> Color
            curves.setCurveColorByName(mi_newCurve.mNode,self.l_moduleColors[0])                    
            mi_newCurve.addAttr('cgmType',attrType='string',value = 'midIK',lock=True)	
            mi_newCurve.doName()

            #Store for return
            l_segmentControls.append( mi_newCurve.mNode )
            ml_segmentControls.append( mi_newCurve )		

            self.d_returnControls['midIK'] = mi_newCurve.mNode 
            self.md_ReturnControls['midIK'] = mi_newCurve
            self._mi_rigNull.connectChildNode(mi_newCurve,'shape_midIK','owner')

            log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        except Exception,error:
            log.error("build_midIKHandle fail]{%s}"%error) 
            return False

    #@cgmGeneral.Timer	
    def build_loliHandles(self):
        _str_funcName = "go.build_loliHandles(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        #Target objects expected
        #if not self._ml_targetObjects:raise Exception,"build_loliHandles requires target objects"
        
        l_controls = []
        ml_controls = []

        for i,i_target in enumerate(self._ml_controlObjects):	
            d_size = ShapeCast.returnBaseControlSize(i_target,self._targetMesh,axis=[self.str_jointOrientation[1],self.str_jointOrientation[2]])#Get size			
            l_size = d_size.get('average')
            size = sum(l_size)/1.5

            log.debug("loli size return: %s"%d_size)
            log.debug("loli size: %s"%size)
            i_ball = cgmMeta.cgmObject(curves.createControlCurve('sphere',size = size/4))
            SNAP.go(i_ball,i_target.mNode,True, True)#Snap to main object

            #make ball
            returnBuffer = ShapeCast.createWrapControlShape(i_target.mNode,self._targetMesh,
                                                            curveDegree=3,
                                                            insetMult = .2,
                                                            closedCurve=False,
                                                            maxDistance=self._baseModuleThickness,		                                      
                                                            l_specifiedRotates = [-30,-10,0,10,30],
                                                            posOffset = [0,0,self.f_skinOffset*1.2],
                                                            extendMode='')
            mi_crv = returnBuffer['instance']
            l_eps = mi_crv.getComponents('ep')
            midIndex = int(len(l_eps)/2)
            log.debug("eps: %s"%l_eps)
            log.debug("mid: %s"%midIndex)

            #Move the ball
            pos = distance.returnWorldSpacePosition(l_eps[midIndex])
            mc.xform( i_ball.mNode, translation = pos, ws = True)#Snap to the mid ep
            mc.move(0,self.f_skinOffset*3,0,i_ball.mNode,relative = True,os=True)

            #Make the curve between the two 
            traceCurve = mc.curve(degree = 1, ep = [pos,i_ball.getPosition()])

            #Combine
            mi_newCurve = cgmMeta.cgmObject( curves.combineCurves([mi_crv.mNode,i_ball.mNode,traceCurve]) )

            #>>> Color
            curves.setCurveColorByName(mi_newCurve.mNode,self.l_moduleColors[0])                    
            mi_crv.addAttr('cgmType',attrType='string',value = 'loliHandle',lock=True)	
            mi_crv.doName()

            #Store for return
            l_controls.append( mi_newCurve.mNode )
            ml_controls.append( mi_newCurve )

        self.d_returnControls['loliHandles'] = l_controls 
        self.md_ReturnControls['loliHandles'] = ml_controls

        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         		

    #@cgmGeneral.Timer	
    def build_torsoIKHandles(self):
        _str_funcName = "go.build_torsoIKHandles(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)	
        time_func = time.clock() 	
        
        
        #Build our top ==============================================================================
        multiplier = 1.1
        #tmplRoot = self._mi_templateNull.root.mNode
        tmplRoot = self._ml_controlObjects[-2]
        mi_loc = tmplRoot.doLoc(fastMode = True)#make loc for sizing
        mi_loc.doGroup()#group to zero
        sizeReturn = ShapeCast.returnBaseControlSize( self._ml_controlObjects[-2],self._targetMesh,axis=['z','y','z+','z-'])#Get size
         
        fl_size = sizeReturn.get('average')
        mc.delete(mi_loc.parent)#delete loc	    
        size = fl_size/4
        ml_curvesToCombine = []
        mi_crvBase = cgmMeta.asMeta( curves.createControlCurve('arrowSingleFat3d',direction = 'y-',size = size,absoluteSize=False),'cgmObject',setClass=False)
        mi_crvBase.rz = 90
        #mi_crvBase.scaleZ = .75
        SNAP.go(mi_crvBase, tmplRoot.mNode) #Snap it
        
        dist = distance.returnDistanceBetweenPoints(mi_crvBase.getPosition(),self._ml_controlObjects[-1].getPosition()) * .5
        #reload(TRANS)
        TRANS.position_set(mi_crvBase.mNode, [0,dist,0],relative= True)
        
        i_grp = cgmMeta.cgmObject( mi_crvBase.doGroup() )
        mi_crvBase.scaleY = 3         
        mc.makeIdentity(mi_crvBase.mNode, apply=True,s=1,n=0)	
        
        try:
            for i,rot in enumerate([0,180]):
                log.debug(rot)
                #rot, shoot, move, dup
                #log.debug("curve: %s | rot int: %s | grp: %s"%(mi_crvBase.mNode,i, i_grp.mNode))
                i_grp.rotateX = i_grp.rotateX + rot
                #Shoot
                d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_crvBase.mNode,firstHit=False)
                if not d_return.get('hit'):
                    log.info(d_return)
                    raise Exception,"build_cog>> failed to get hit. Mesh '{0}' object probably isn't in mesh".format(self._targetMesh.mNode)
                #log.debug("hitDict: %s"%d_return)
                dist = distance.returnDistanceBetweenPoints(mi_crvBase.getPosition(),d_return['hit'])+(self.f_skinOffset*5)
                #log.debug("dist: %s"%dist)
                #log.debug("crv: %s"%mi_crvBase.mNode)
                mi_crvBase.__setattr__("tz",dist * 1.1)
                mi_tmp = mi_crvBase.doDuplicate(parentOnly=False)
                #log.debug(mi_tmp)
                mi_tmp.parent = False
                ml_curvesToCombine.append(mi_tmp)
                mi_crvBase.__setattr__("tz",0)
        except Exception,error:
            raise Exception,"Rotate dup | {0}".format(error)                    
        i_grp.delete()
    
        try:
            log.info(ml_curvesToCombine)
            mi_crv = cgmMeta.cgmObject( curves.combineCurves([i_obj.mNode for i_obj in ml_curvesToCombine]) )
            
            #log.debug("mi_crv: %s"%mi_crv.mNode)
        except Exception,error:
            raise Exception,"Reinitialize | {0}".format(error)            
    
        try:#>>Copy tags and name
            coreRigging.match_transform(mi_crv.mNode, self._ml_controlObjects[-1].mNode)
            
            curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])    
            
            mi_crv.doCopyNameTagsFromObject(self.l_controlSnapObjects[-1],ignore = ['cgmType'])
            mi_crv.addAttr('cgmType',attrType='string',value = 'ikCurve',lock=True)	    
            mi_crv.doName()

            self.d_returnControls['segmentIKEnd'] = mi_crv.mNode 		
            self.md_ReturnControls['segmentIKEnd'] = mi_crv
            self._mi_rigNull.connectChildNode(mi_crv,'shape_handleIK','owner')
        except Exception,error:
            raise Exception,"Color | {0}".format(error)
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         
        #rigging.copyPivot(mi_crv.mNode, self._ml_controlObjects[-1].mNode)
        #mi_crv.doCopyTransform(self._ml_controlObjects[-1])          

        try:
            l_segmentControls = []
            ml_segmentControls = []

            l_segmentsToDo = self.l_segments[1:]

            for i,seg in enumerate(l_segmentsToDo):
                returnBuffer = ShapeCast.createWrapControlShape(seg[0],self._targetMesh,
                                                                points = 17,
                                                                curveDegree=3,
                                                                insetMult = .5,
                                                                posOffset = [0,0,self.f_skinOffset],
                                                                joinMode=True,
                                                                closestInRange = False,
                                                                maxDistance=self._baseModuleThickness,		                                      
                                                                extendMode='disc')
                mi_crv = returnBuffer['instance']	    
                #>>> Color
                curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[1])                    
                mi_crv.addAttr('cgmType',attrType='string',value = 'segIKCurve',lock=True)	
                mi_crv.doName()

                #Store for return
                l_segmentControls.append( mi_crv.mNode )
                ml_segmentControls.append( mi_crv )

                #Snap pivot to handle joint?
                mObj = cgmMeta.cgmObject(seg[0])
                if mObj.getMessage('owner'):
                    #log.info("Owner!")
                    _handleJointBuffer = mObj.owner.getMessage('handleJoint')
                    if _handleJointBuffer:
                        rigging.copyPivot(mi_crv.mNode,_handleJointBuffer[0])		


            self.d_returnControls['segmentIK'] = l_segmentControls 
            self.md_ReturnControls['segmentIK'] = ml_segmentControls
            self._mi_rigNull.msgList_connect('shape_segmentIK',ml_segmentControls,'owner')

            if len(self.l_segments)>2:
                objects = self.l_controlSnapObjects[-2:]
            else:
                objects = self.l_segments[-1]
            #"""l_specifiedRotates = [0,30,60,160,180,200,220,300,330]"""
            
            
            
            """returnBuffer = ShapeCast.createWrapControlShape(self.l_segments[-1],self._targetMesh,
                                                            points = 12 ,
                                                            curveDegree=3,
                                                            insetMult = .05,
                                                            posOffset = [0,0,self.f_skinOffset*3],
                                                            joinHits = [0,6],	                                          
                                                            joinMode=True,
                                                            maxDistance=self._baseModuleThickness*.6,
                                                            extendMode='segment')
            
            mi_crv = returnBuffer['instance']

            #>>> Color
            curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
            mi_crv.doCopyNameTagsFromObject(self.l_controlSnapObjects[-1],ignore = ['cgmType'])
            mi_crv.addAttr('cgmType',attrType='string',value = 'ikCurve',lock=True)	    
            mi_crv.doName()

            self.d_returnControls['segmentIKEnd'] = mi_crv.mNode 		
            self.md_ReturnControls['segmentIKEnd'] = mi_crv
            self._mi_rigNull.connectChildNode(mi_crv,'shape_handleIK','owner')"""
        except Exception,error:
            raise Exception,"segment handles | {0}".format(err)
        
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         



    def build_settings(self):
        _str_funcName = "go.build_settings(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        l_segmentControls = []
        ml_SegmentControls = []
        mi_footModule = False

        #Find our settings
        #============================================================================	
        self.latheAxis = self.str_jointOrientation[0]
        self.aimAxis = self.str_jointOrientation[1] + '-'
        self.outAxis = self.str_jointOrientation[2]
        self.posOffset = [0,0,self.f_skinOffset*6]
        self.settingsVector = [0,1,0]	    	
        self.gearVector = [0,0,-1]
        _moveMultiplier = 1.5
        _direction = self.outAxis+'+'
        index = -1
        index_size = index
        _castMode = 'vector'	
        _sizeMultiplier = 1
        if self.str_partType == 'leg':
            index = -2
            index_size = -2
            self.settingsVector = [0,0,-1]
        elif self.str_partType == 'arm':
            index_size = 1
            index = 0    
            _direction = self.aimAxis	    
            #self.settingsVector = [0,1,0]	    	
            self.settingsVector = [0,1,0]
            _moveMultiplier = 1.5
        elif self._mi_module.moduleType.lower() in ['finger','thumb']:
            index_size = -2
            index = 1
            _direction = self.str_jointOrientation[2] + '+'  
            self.settingsVector = [0,1,0]
            _castMode = 'axis'
            self.aimAxis = self.str_jointOrientation[1] + '+'	    
            _moveMultiplier = 2
            _sizeMultiplier = .75
        i_target = cgmMeta.cgmObject( self.l_controlSnapObjects[index] )
        i_sizeTarget = cgmMeta.cgmObject( self.l_controlSnapObjects[index_size] )

        mi_rootLoc = i_target.doLoc(fastMode = True)
        mi_sizeLoc = i_sizeTarget.doLoc(fastMode = True)

        #Size the settings control
        d_size = ShapeCast.returnBaseControlSize(mi_sizeLoc,self._targetMesh,axis=[self.outAxis])#Get size
        #baseSize = d_size.get(d_size.keys()[0])
        baseSize = d_size.get('average') * _sizeMultiplier
        log.debug("build_settings>>> baseSize: %s"%baseSize)

        i_gear = cgmMeta.cgmObject(curves.createControlCurve('gear',size = baseSize,direction=_direction))	

        #Move stuff
        SNAP.go(i_gear.mNode,mi_rootLoc.mNode,True, False)#Snap to main object

        #Move the ball
        if _castMode == 'vector':
            d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_rootLoc.mNode,vector = self.settingsVector,firstHit=True)
            if not d_return.get('hit'):
                raise Exception,"go.build_settings>>failed to get hit to measure distance"

            mc.move(d_return['hit'][0],d_return['hit'][1],d_return['hit'][2],i_gear.mNode,absolute = True,ws=True)
            #SNAP.go(i_gear.mNode,mi_rootLoc.mNode,positiomove = False, orient = False, aim=True, aimVector=[0,0,-1])
            SNAP.aim(i_gear.mNode,mi_rootLoc.mNode,'z-')
            mc.move(self.posOffset[0]*_moveMultiplier,self.posOffset[1]*_moveMultiplier,self.posOffset[2]*_moveMultiplier, [i_gear.mNode], r = True, rpr = True, os = True, wd = True)
            mi_rootLoc.delete()
            mi_sizeLoc.delete()
        else:#Axis mode
            d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_rootLoc.mNode,axis = self.aimAxis,firstHit=True)		    
            if not d_return.get('hit'):
                raise Exception,"go.build_settings>>failed to get hit to measure distance"	    
            dist_move = distance.returnDistanceBetweenPoints(mi_rootLoc.getPosition(),d_return['hit'])
            log.debug("axis cast move: %s"%dist_move)
            grp = mi_rootLoc.doGroup(True)
            mi_rootLoc.__setattr__("t%s"%self.str_jointOrientation[1],dist_move*_moveMultiplier)

            SNAP.go(i_gear.mNode,mi_rootLoc.mNode,True,True)	    
            mc.delete(mi_rootLoc.parent)
            mi_sizeLoc.delete()	    


        #Combine and finale
        #============================================================================
        i_gear.doCopyPivot(i_target.mNode)
        #>>> Color
        curves.setCurveColorByName(i_gear.mNode,self.l_moduleColors[0])                    
        #i_gear.doCopyNameTagsFromObject(i_target.mNode,ignore = ['cgmType'])
        i_gear.addAttr('cgmName',self.str_partName,attrType='string',lock=True)	    
        i_gear.addAttr('cgmType',attrType='string',value = 'settings',lock=True)	    
        i_gear.doName()

        self.d_returnControls['settings'] = i_gear.mNode 		
        self.md_ReturnControls['settings'] = i_gear		
        self._mi_rigNull.connectChildNode(i_gear,'shape_settings','owner')
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

    #@cgmGeneral.Timer
    def build_footPivots(self):
        """
        build foot pivot locs 
        """
        _str_funcName = "go.build_footPivots(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        mi_footModule = False
        mi_ball = False
        mi_ankle = False

        #Find our foot
        #============================================================================	
        if self.str_partType == 'foot':
            raise NotImplementedError,"haven't implemented foot"
        elif self.str_partType == 'legSimple':
            #find the foot. 1) Build search dict
            d_search = {'moduleType':'foot'}
            for key in ['cgmDirection','cgmPosition']:
                buffer = self._mi_module.getAttr(key)
                if buffer:
                    d_search[key] = buffer
            #Find it
            mi_footModule = self._mi_puppet.getModuleFromDict(d_search)
            ml_children = self._mi_module.moduleChildren
            if mi_footModule in ml_children:log.debug("found match modules: %s"%mi_footModule)

            ml_controlSnapObjects = []
            for mi_obj in mi_footModule.templateNull.msgList_get('controlObjects'):
                ml_controlSnapObjects.append(mi_obj.helper)  
            log.debug("helperObjects: %s"%[i_obj.getShortName() for i_obj in ml_controlSnapObjects])
            if ml_controlSnapObjects[1].cgmName != 'ball':
                raise Exception,"go.build_footShape>>> Expected second snap object to be 'ball'. Found: %s"%ml_controlSnapObjects[1].mNode
            mi_ball = ml_controlSnapObjects[1]
            mi_ankle = ml_controlSnapObjects[0]

        elif self.str_partType == 'leg':
            for obj in self.l_controlSnapObjects:
                if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'ankle':
                    mi_ankle = cgmMeta.cgmObject(obj)
                    break
            for obj in self.l_controlSnapObjects:
                if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'ball':
                    mi_ball = cgmMeta.cgmObject(obj)
                    break

        if not mi_ball and not mi_ankle:
            raise Exception,"go.build_footShape>>> Haven't found a foot module to build from"

        #Get our helper objects
        #============================================================================
        mi_heelLoc = mi_ankle.doLoc(fastMode = True)
        mi_ballLoc = mi_ball.doLoc(fastMode = True)
        mi_heelLoc.__setattr__('r%s'%self.str_jointOrientation[2],0)
        mi_heelLoc.__setattr__('t%s'%self.str_jointOrientation[1],mi_ballLoc.getAttr('t%s'%self.str_jointOrientation[1]))

        #Get our distance for our front cast

        d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,self.str_jointOrientation[0]+'+',pierceDepth=self.f_skinOffset*15) or {}
        if not d_return.get('hit'):
            raise Exception,"go.build_footShape>>failed to get hit to measure first distance"
        dist = distance.returnDistanceBetweenPoints(mi_ballLoc.getPosition(),d_return['hit']) *1.5
        log.debug("go.build_footShape>>front distance: %s"%dist)

        #Pivots
        #===================================================================================
        try:#Ball pivot
            mi_ballPivot = mi_ballLoc.doLoc(fastMode = True)
            mi_ballPivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
            mi_ballPivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
            mi_ballPivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
            mi_ballPivot.doName()
            self.d_returnPivots['ball'] = mi_ballPivot.mNode 		
            self.md_returnPivots['ball'] = mi_ballPivot	
        except Exception,err:
            raise Exception,"Ball pivot fail << {0} >>".format(err)
        
        try:#Toe pivot
            mi_toePivot =  mi_ballLoc.doLoc(fastMode = True)
            mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_toePivot.mNode)
            mi_toePivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
            mi_toePivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
            mi_toePivot.addAttr('cgmName','toe',lock=True)	
            mi_toePivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
            mi_toePivot.doName()	
            #mc.rotate (objRot[0], objRot[1], objRot[2], str_pivotToe, ws=True)	
            self.d_returnPivots['toe'] = mi_toePivot.mNode 		
            self.md_returnPivots['toe'] = mi_toePivot	
        except Exception,err:
            raise Exception,"toe pivot fail << {0} >>".format(err)
        
        try:#Inner bank pivots
            if self._direction == 'left':
                innerAim = self.str_jointOrientation[2]+'-'
                outerAim = self.str_jointOrientation[2]+'+'
    
            else:
                innerAim = self.str_jointOrientation[2]+'+'
                outerAim = self.str_jointOrientation[2]+'-'
    
            d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,innerAim,pierceDepth=self.f_skinOffset*5) or {}
            if not d_return.get('hit'):
                raise Exception,"go.build_footShape>>failed to get inner bank hit"	
            mi_innerPivot =  mi_ballLoc.doLoc(fastMode = True)
            mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_innerPivot.mNode)
            mi_innerPivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
            mi_innerPivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
            mi_innerPivot.addAttr('cgmName','ball',lock=True)	
            mi_innerPivot.addAttr('cgmDirectionModifier','inner',lock=True)		    
            mi_innerPivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
            mi_innerPivot.doName()		
            self.d_returnPivots['inner'] = mi_innerPivot.mNode 		
            self.md_returnPivots['inner'] = mi_innerPivot	
    
            d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,outerAim,pierceDepth=self.f_skinOffset*5) or {}
            if not d_return.get('hit'):
                raise Exception,"go.build_footShape>>failed to get outer bank hit"	
            mi_outerPivot =  mi_ballLoc.doLoc(fastMode = True)
            mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_outerPivot.mNode)
            mi_outerPivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
            mi_outerPivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
            mi_outerPivot.addAttr('cgmName','ball',lock=True)	
            mi_outerPivot.addAttr('cgmDirectionModifier','outer',lock=True)		    	    
            mi_outerPivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
            mi_outerPivot.doName()	
            self.d_returnPivots['outer'] = mi_outerPivot.mNode 		
            self.md_returnPivots['outer'] = mi_outerPivot	
        except Exception,err:
            raise Exception,"Banks fail << {0} >>".format(err)
        
        try:#Heel pivot
            mi_heelPivot =  mi_heelLoc.doLoc(fastMode = True)
            mi_heelPivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
            _v = mc.xform(mi_heelPivot.mNode, q = True, t = True, ws = True)
            mi_heelPivot.__setattr__('t%s'%self.str_jointOrientation[1],_v[1] * .5)
    
            d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_heelPivot.mNode,self.str_jointOrientation[0]+'-',pierceDepth=self.f_skinOffset*5) or {}
            if not d_return.get('hit'):
                raise Exception,"Hit failed"	
            mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_heelPivot.mNode)
            mi_heelPivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
            mi_heelPivot.addAttr('cgmName','heel',lock=True)	
            mi_heelPivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
            mi_heelPivot.doName()		
            self.d_returnPivots['heel'] = mi_heelPivot.mNode 		
            self.md_returnPivots['heel'] = mi_heelPivot		
    
            mi_ballLoc.delete()
            mi_heelLoc.delete()
        except Exception,err:
            raise Exception,"heel pivot fail << {0} >>".format(err)
        
        #Store em all
        self._mi_templateNull.connectChildNode(mi_toePivot,'pivot_toe','module')
        self._mi_templateNull.connectChildNode(mi_heelPivot,'pivot_heel','module')
        self._mi_templateNull.connectChildNode(mi_ballPivot,'pivot_ball','module')
        self._mi_templateNull.connectChildNode(mi_innerPivot,'pivot_inner','module')
        self._mi_templateNull.connectChildNode(mi_outerPivot,'pivot_outer','module')

        #Parent
        for p in mi_toePivot,mi_heelPivot,mi_ballPivot,mi_innerPivot,mi_outerPivot:
            p.parent = self._mi_templateNull.mNode	
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

    #@cgmGeneral.Timer
    def build_footShape(self):
        """
        build foot shape and pivot locs at the same time
        """
        _str_funcName = "go.build_footShape(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        l_segmentControls = []
        ml_SegmentControls = []
        mi_footModule = False
        mi_ball = False
        mi_ankle = False

        #Find our foot
        #============================================================================	
        if self.str_partType == 'foot':
            raise NotImplementedError,"haven't implemented foot"
        elif self.str_partType == 'legSimple':
            #find the foot. 1) Build search dict
            d_search = {'moduleType':'foot'}
            for key in ['cgmDirection','cgmPosition']:
                buffer = self._mi_module.getAttr(key)
                if buffer:
                    d_search[key] = buffer
            #Find it
            mi_footModule = self._mi_puppet.getModuleFromDict(d_search)
            ml_children = self._mi_module.moduleChildren
            if mi_footModule in ml_children:log.debug("found match modules: %s"%mi_footModule)

            ml_controlSnapObjects = []
            for mi_obj in mi_footModule.templateNull.msgList_get('controlObjects'):
                ml_controlSnapObjects.append(mi_obj.helper)  
            log.debug("helperObjects: %s"%[i_obj.getShortName() for i_obj in ml_controlSnapObjects])
            if ml_controlSnapObjects[1].cgmName != 'ball':
                raise Exception,"go.build_footShape>>> Expected second snap object to be 'ball'. Found: %s"%ml_controlSnapObjects[1].mNode
            mi_ball = ml_controlSnapObjects[1]
            mi_ankle = ml_controlSnapObjects[0]

        elif self.str_partType == 'leg':
            for obj in self.l_controlSnapObjects:
                if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'ankle':
                    mi_ankle = cgmMeta.cgmObject(obj)
                    break
            for obj in self.l_controlSnapObjects:
                if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'ball':
                    mi_ball = cgmMeta.cgmObject(obj)
                    break

        if not mi_ball and not mi_ankle:
            raise Exception,"go.build_footShape>>> Haven't found a foot module to build from"

        #Get our helper objects
        #============================================================================
        mi_heelLoc = mi_ankle.doLoc(fastMode = True)
        mi_ballLoc = mi_ball.doLoc(fastMode = True)
        mi_heelLoc.__setattr__('r%s'%self.str_jointOrientation[2],0)
        mi_heelLoc.__setattr__('t%s'%self.str_jointOrientation[1],mi_ballLoc.getAttr('t%s'%self.str_jointOrientation[1]))

        #Get our distance for our front cast

        d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,self.str_jointOrientation[0]+'+',pierceDepth=self.f_skinOffset*15) or {}
        if not d_return.get('hit'):
            raise Exception,"go.build_footShape>>failed to get hit to measure first distance"
        dist = distance.returnDistanceBetweenPoints(mi_ballLoc.getPosition(),d_return['hit']) *1.25
        log.debug("go.build_footShape>>front distance: %s"%dist)

        #Pivots
        #===================================================================================
        """
	#Ball pivot
	mi_ballPivot = mi_ballLoc.doLoc(fastMode = True)
	mi_ballPivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
	mi_ballPivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
	mi_ballPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_ballPivot.doName()
	self.d_returnPivots['ball'] = mi_ballPivot.mNode 		
	self.md_returnPivots['ball'] = mi_ballPivot	

	#Toe pivot
	mi_toePivot =  mi_ballLoc.doLoc(fastMode = True)
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_toePivot.mNode)
	mi_toePivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
	mi_toePivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
	mi_toePivot.addAttr('cgmName','toe',lock=True)	
	mi_toePivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_toePivot.doName()	
	#mc.rotate (objRot[0], objRot[1], objRot[2], str_pivotToe, ws=True)	
	self.d_returnPivots['toe'] = mi_toePivot.mNode 		
	self.md_returnPivots['toe'] = mi_toePivot	

	#Inner bank pivots
	if self._direction == 'left':
	    innerAim = self.str_jointOrientation[2]+'-'
	    outerAim = self.str_jointOrientation[2]+'+'

	else:
	    innerAim = self.str_jointOrientation[2]+'+'
	    outerAim = self.str_jointOrientation[2]+'-'

	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,innerAim,pierceDepth=self.f_skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise Exception,"go.build_footShape>>failed to get inner bank hit"	
	mi_innerPivot =  mi_ballLoc.doLoc(fastMode = True)
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_innerPivot.mNode)
	mi_innerPivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
	mi_innerPivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
	mi_innerPivot.addAttr('cgmName','inner',lock=True)	
	mi_innerPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_innerPivot.doName()		
	self.d_returnPivots['inner'] = mi_innerPivot.mNode 		
	self.md_returnPivots['inner'] = mi_innerPivot	

	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,outerAim,pierceDepth=self.f_skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise Exception,"go.build_footShape>>failed to get inner bank hit"	
	mi_outerPivot =  mi_ballLoc.doLoc(fastMode = True)
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_outerPivot.mNode)
	mi_outerPivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
	mi_outerPivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
	mi_outerPivot.addAttr('cgmName','outer',lock=True)	
	mi_outerPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_outerPivot.doName()	
	self.d_returnPivots['outer'] = mi_outerPivot.mNode 		
	self.md_returnPivots['outer'] = mi_outerPivot	

	#Heel pivot
	mi_heelPivot =  mi_heelLoc.doLoc(fastMode = True)
	mi_heelPivot.__setattr__('r%s'%self.str_jointOrientation[2],0)
	mi_heelPivot.__setattr__('t%s'%self.str_jointOrientation[1],.25)

	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_heelPivot.mNode,self.str_jointOrientation[0]+'-',pierceDepth=self.f_skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise Exception,"go.build_footShape>>failed to get inner bank hit"	
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_heelPivot.mNode)
	mi_heelPivot.__setattr__('t%s'%self.str_jointOrientation[1],0)
	mi_heelPivot.addAttr('cgmName','heel',lock=True)	
	mi_heelPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_heelPivot.doName()		
	self.d_returnPivots['heel'] = mi_heelPivot.mNode 		
	self.md_returnPivots['heel'] = mi_heelPivot		
	"""
        #Cast our stuff
        #============================================================================
        self.posOffset = [0,0,self.f_skinOffset*3]
        self.latheAxis = self.str_jointOrientation[1]
        self.aimAxis = self.str_jointOrientation[0] + '+'

        if self._direction == 'left':
            l_specifiedRotates = [-40,-20,0,20,60,80]

        else:
            l_specifiedRotates = [40,20,0,-20,-60,-80]

        d_return = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_ballLoc.mNode,offsetMode='vector',maxDistance = dist,l_specifiedRotates = l_specifiedRotates,
                                                  closedCurve = False,curveDegree=1,posOffset = self.posOffset,returnDict = True,
                                                  latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)
        str_frontCurve = d_return['curve']

        #Heel cast

        self.aimAxis = self.str_jointOrientation[0] + '-'	
        if self._direction == 'left':
            l_specifiedRotates = [-90,-60,-20,-10,0,10,20,40,60,80]#foot back, closed false, closest in range false

        else:
            l_specifiedRotates = [90,60,20,10,0,-10,-20,-40,-60,-80]
        d_return = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_heelLoc.mNode,offsetMode='vector',maxDistance = 1000,l_specifiedRotates = l_specifiedRotates,
                                                  closedCurve = False,curveDegree=1,posOffset = self.posOffset,returnDict = True,
                                                  latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=True)
        str_backCurve = d_return['curve']

        #side cast
        self.aimAxis = self.str_jointOrientation[0] + '+'
        if self._direction == 'left':
            l_specifiedRotates = [-100,-80,-50]#foot front closest, closed false, closest in range true

        else:
            l_specifiedRotates =  [100,80,50]

        d_return = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_ballLoc.mNode,offsetMode='vector',maxDistance = 1000,l_specifiedRotates = l_specifiedRotates,
                                                  closedCurve = False,curveDegree=1,posOffset = self.posOffset,returnDict = True,
                                                  latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=True)
        str_sideCurve = d_return['curve']

        #Let's collect the points of the curves
        l_pos = []
        l_basePos = []
        ballY = distance.returnWorldSpacePosition(mi_ballLoc.mNode)[1]/2
        log.debug("ballY: %s"%ballY)
        for crv in [str_frontCurve,str_backCurve,str_sideCurve]:
            for ep in cgmMeta.cgmNode(crv).getComponents('ep'):
                buffer = distance.returnWorldSpacePosition(ep)
                l_pos.append( [buffer[0],ballY,buffer[2]] )
                l_basePos.append( [buffer[0],0,buffer[2]] )
            mc.delete(crv)

        l_pos.append(l_pos[0])#append to close loop
        l_basePos.append(l_basePos[0])#append to close loop

        mi_ballLoc.delete()
        mi_heelLoc.delete()	

        topCrv = mc.curve(degree = 3, ep = l_pos)
        baseCrv = mc.curve(degree = 3, ep = l_basePos)

        #Combine and finale
        #============================================================================
        newCrv = curves.combineCurves([topCrv,baseCrv])
        mi_crv = cgmMeta.cgmObject(newCrv)

        mi_crv.doCopyPivot(mi_ankle.mNode)
        #>>> Color
        curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
        mi_crv.doCopyNameTagsFromObject(mi_ankle.mNode,ignore = ['cgmType'])
        mi_crv.addAttr('cgmType',attrType='string',value = 'foot',lock=True)	    
        mi_crv.doName()

        self.d_returnControls['foot'] = mi_crv.mNode 		
        self.md_ReturnControls['foot'] = mi_crv	
        self._mi_rigNull.connectChildNode(mi_crv,'shape_foot','owner')

        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

    #@cgmGeneral.Timer
    def build_handShape(self):
        """
        build hand shape and pivot locs at the same time
        """
        _str_funcName = "go.build_handShape(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        l_segmentControls = []
        ml_SegmentControls = []
        mi_handModule = False
        mi_palm = False
        mi_wrist = False

        #Find our hand
        #============================================================================	
        if self.str_partType == 'hand':
            raise NotImplementedError,"haven't implemented hand"
        elif self.str_partType == 'armSimple':
            raise NotImplementedError,"haven't implemented hand"

        elif self.str_partType == 'arm':
            for obj in self.l_controlSnapObjects:
                if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'wrist':
                    mi_wrist = cgmMeta.cgmObject(obj)
                    break
            for obj in self.l_controlSnapObjects:
                if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'palm':
                    mi_palm = cgmMeta.cgmObject(obj)
                    break

        if not mi_wrist:
            raise Exception,"go.build_handShape>>> Haven't found a wrist to build from"

        #Get our helper objects
        #============================================================================
        mi_wristLoc = mi_wrist.doLoc(fastMode = True)
        d_wristSize = ShapeCast.returnBaseControlSize(mi_wristLoc.mNode,self._targetMesh,[self.str_jointOrientation[1],self.str_jointOrientation[2]])
        #Average the wrist size
        dist_wristSize = d_wristSize.get('average')
        log.debug("dist_wristSize: %s"%dist_wristSize)	

        if mi_palm:
            mi_palmLoc = mi_palm.doLoc(fastMode = True)
        else:
            mi_palmLoc = mi_wristLoc.doDuplicate()
            mi_palmLoc.doGroup()
            mi_palmLoc.__setattr__('t%s'%self.str_jointOrientation[0],dist_wristSize/4)

        mi_wristLoc.doGroup()
        mi_wristLoc.__setattr__('t%s'%self.str_jointOrientation[0],-dist_wristSize/2)

        #Get our distance for our casts
        if self._direction == 'left':
            self.aimAxis = self.str_jointOrientation[2] + '-'
            axis_distanceDirectionCast = self.str_jointOrientation[2] + '+'
            rootRotate = -30
        else:
            self.aimAxis = self.str_jointOrientation[2] + '+'
            axis_distanceDirectionCast = self.str_jointOrientation[2] + '-'	    
            rootRotate = 30	   

        #Distance stuff    
        d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_palmLoc.mNode,axis_distanceDirectionCast,pierceDepth=self.f_skinOffset*15) or {}
        if not d_return.get('hit'):
            raise Exception,"go.build_clavicle>>failed to get hit to measure first distance"
        dist_cast = distance.returnDistanceBetweenPoints(mi_palmLoc.getPosition(),d_return['hit']) * 4

        #Cast our stuff
        #============================================================================
        self.posOffset = [0,0,self.f_skinOffset*3]
        self.latheAxis = self.str_jointOrientation[0]
        log.debug("aim: %s"%self.aimAxis)
        log.debug("lathe: %s"%self.latheAxis)
        log.debug("dist: %s"%dist_cast)

        d_startReturn = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_wristLoc.mNode,offsetMode='vector',maxDistance = dist_cast,
                                                       closedCurve = True,curveDegree=3,midMeshCast=True,axisToCheck=[self.str_jointOrientation[1],self.str_jointOrientation[2]],posOffset = self.posOffset,returnDict = True,
                                                       latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)

        d_endReturn = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_palmLoc.mNode,offsetMode='vector',maxDistance = dist_cast,
                                                     closedCurve = True,curveDegree=3,midMeshCast=True,axisToCheck=[self.str_jointOrientation[1],self.str_jointOrientation[2]],posOffset = self.posOffset,returnDict = True,
                                                     latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)


        #Let's collect the points to join
        l_curvesToCombine = [d_startReturn['curve'],d_endReturn['curve']]	
        joinReturn = ShapeCast.joinCurves(l_curvesToCombine,mode = 'quartered')

        l_curvesToCombine.extend(joinReturn)

        mc.delete([mi_wristLoc.parent,mi_palmLoc.parent])

        #Combine and finale
        #============================================================================
        newCurve = curves.combineCurves(l_curvesToCombine) 
        mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(mi_wrist.mNode,False) )
        curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
        mc.delete(newCurve)

        #>>> Color
        curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
        mi_crv.doCopyNameTagsFromObject(mi_wrist.mNode,ignore = ['cgmType'])
        mi_crv.addAttr('cgmType',attrType='string',value = 'hand',lock=True)	    
        mi_crv.doName()

        self.d_returnControls['hand'] = mi_crv.mNode 		
        self.md_ReturnControls['hand'] = mi_crv	
        self._mi_rigNull.connectChildNode(mi_crv,'shape_hand','owner')

        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

    #@cgmGeneral.Timer
    def build_segmentIKHandles(self):
        _str_funcName = "go.build_segmentIKHandles(%s)"%self._strShortName
        log.info(">>> %s >>> "%(_str_funcName) + "="*75)
        time_func = time.clock() 		
        l_segmentControls = []
        ml_SegmentControls = []

        #Defaults
        self.posOffset = [0,0,self.f_skinOffset*1.2]
        self.l_specifiedRotates = None	
        self.joinMode = True
        self.closedCurve = True
        self.rotateBank = None	    
        #self.maxDistance = 1000
        self.maxDistance = self._baseModuleThickness
        log.info("Max Distance: {0}".format(self.maxDistance))
        self.aimAxis = 'y+'
        self.latheAxis = 'z'
        self.insetMult = .1
        self.points = 8
        self.rootRotate = None
        self.rootOffset = None
        self.midMeshCast = True
        self.axisToCheck = [self.str_jointOrientation[1]]
        d_kws = {}
        l_objectsToDo = []

        #Figure out some flag stuff
        if 'neck' in self.str_partType:
            #self.maxDistance = 1000
            self.insetMult = .05
            self.posOffset = [0,0,self.f_skinOffset*2]
            d_kws = {'default':{'l_specifiedRotates':None,
                                'joinMode': True,
                                'rotateBank':None,
                                'closedCurve':True,
                                'aimAxis':'y+'},
                     0:{'rotateBank':10},
                     -1:{'closedCurve':False,'l_specifiedRotates':[-90,-60,-30,0,30,60,90],'rotateBank':-10}}

        elif self.str_partType == 'leg':
            """Use influence joints to cast these"""
            l_objectsToDo = self.l_controlSnapObjects[:-1]
            self.posOffset = [0,0,self.f_skinOffset*2]
            self.points = 12
            d_kws = {'default':{'closedCurve':True,
                                'l_specifiedRotates':[],
                                'insetMult':.15,
                                'rootRotate':None,
                                'rootOffset':[],
                                'rotateBank':[]},
                     0:{'rootOffset':[0,0,self.f_skinOffset*6]},
                     -1:{'rootOffset':[0,0,-self.f_skinOffset*6]}}

            if self._direction == 'left':
                self.aimAxis = 'x+'
                d_kws['default']['aimAxis']= 'x+'
                d_kws[0]['rotateBank'] = -10
            else:
                self.aimAxis = 'x-'		
                d_kws['default']['aimAxis']= 'x-'
                d_kws[0]['rotateBank'] = 10

        elif self.str_partType == 'arm':
            self.posOffset = [0,0,self.f_skinOffset*2]
            self.points = 12
            self.midMeshCast = False

            d_kws = {'default':{'closedCurve':True,
                                'l_specifiedRotates':[],
                                'insetMult':.15,
                                'rootRotate':None,
                                'rootOffset':[],
                                'midMeshCast':True,
                                'rotateBank':[]},
                     0:{'rootOffset':[0,0,self.f_skinOffset*3],
                        'midMeshCast':False,},
                     -1:{'rootOffset':[0,0,-self.f_skinOffset*3]}}

            if self._direction == 'left':
                self.aimAxis = 'x+'
                d_kws['default']['aimAxis']= 'x+'
                d_kws[0]['rotateBank'] = -10
            else:
                self.aimAxis = 'x-'		
                d_kws['default']['aimAxis']= 'x-'
                d_kws[0]['rotateBank'] = 10

        if self._ml_targetObjects:
            l_objectsToDo = [i_o.mNode for i_o in self._ml_targetObjects]
        elif not l_objectsToDo:
            l_objectsToDo = self.l_controlSnapObjects

        for i,obj in enumerate(l_objectsToDo):
            mObj = cgmMeta.cgmObject(obj)
            log.info(obj)
            self._pushKWsDict(d_kws,i,l_objectsToDo)
            log.debug(">>>>>>>>>>>aim: %s"%self.aimAxis)
            log.debug(">>>>>>>>>> lathe: %s"%self.latheAxis)
            log.debug(">>>>>>>>>> l_specifiedRotates: %s"%self.l_specifiedRotates)
            log.info(">>>>>>>>>> distance: %s"%self.maxDistance)
            #Few more special cases
            if mObj.getAttr('cgmName') in ['ankle'] and not self._ml_targetObjects:
                log.debug('Special rotate mode')
                self.rootRotate = [0,0,0]
                self.latheAxis = 'y'	 

            if mObj.getAttr('cgmName') in ['hip']:
                self.l_specifiedRotates = [-90,-60,-30,0,30,60,90]
                self.closedCurve = False

            returnBuffer = ShapeCast.createWrapControlShape(obj,self._targetMesh,
                                                            points = 8,
                                                            curveDegree=3,
                                                            insetMult = self.insetMult,
                                                            latheAxis = self.latheAxis,
                                                            aimAxis = self.aimAxis,	                                          
                                                            maxDistance = self.maxDistance,
                                                            rotateBank = self.rotateBank,
                                                            posOffset = self.posOffset,
                                                            rootRotate = self.rootRotate,
                                                            rootOffset = self.rootOffset,
                                                            closedCurve = self.closedCurve,
                                                            midMeshCast = self.midMeshCast,
                                                            closestInRange=False,
                                                            l_specifiedRotates = self.l_specifiedRotates,
                                                            joinMode=self.joinMode,
                                                            extendMode='disc',
                                                            axisToCheck = self.axisToCheck)
            mi_crv = returnBuffer['instance']	    
            #>>> Color
            curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[1])                    
            mi_crv.addAttr('cgmType',attrType='string',value = 'segIKCurve',lock=True)	
            mi_crv.doName()

            #Snap pivot to handle joint? <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  THIS IS NEW TEST CODE - 05.14.2014
            if mObj.getMessage('owner'):
                log.info("Owner!")
                _handleJointBuffer = mObj.getMessage('handleJoint')
                if _handleJointBuffer:
                    rigging.copyPivot(mi_crv.mNode,_handleJointBuffer[0])

            #Store for return
            l_segmentControls.append( mi_crv.mNode )
            ml_SegmentControls.append( mi_crv )

        self.d_returnControls['segmentIK'] = l_segmentControls 
        self.md_ReturnControls['segmentIK'] = ml_SegmentControls
        self._mi_rigNull.msgList_connect('shape_segmentIK',ml_SegmentControls,'owner')
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

        #except Exception,error:
        #	log.error("build_segmentIKHandles]{%s}"%error) 
        #	return False

class ShapeCasterFunc(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """
        try:goInstance = args[0]
        except:goInstance = kws['goInstance']
        assert mc.objExists(goInstance._mi_module.mNode),"Module no longer exists"

        super(ShapeCasterFunc, self).__init__(*args,**kws)

        self._str_funcName = 'ModuleShapeCaster(%s)'%goInstance._mi_module.p_nameShort
        self._l_ARGS_KWS_DEFAULTS = [{'kw':'goInstance',"default":None}]

        self.__dataBind__(*args,**kws)
        self.mi_go = goInstance
        self.mi_module = goInstance._mi_module
        #=================================================================

def shapeCast_eyebrow(*args,**kws):
    class fncWrap(ShapeCasterFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = 'shapeCast_eyebrow(%s)'%self.mi_module.p_nameShort
            self._b_autoProgressBar = 1	    
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
                                {'step':'Brow Shapes','call':self._browShapes_},
                                {'step':'Cheek Shapes','call':self._uprCheekShapes_},
                                {'step':'Temple Shapes','call':self._templeShapes_},	                        
                                {'step':'Face Pins','call':self._facePins_},
                                ]

            assert self.mi_module.mClass == 'cgmEyebrow',"%s >>> Module is not type: 'cgmEyebrow' | type is: '%s'"%(self._str_funcName,self.mi_module.mClass)

            #The idea is to register the functions needed to be called
            #=================================================================
            if log.getEffectiveLevel() == 10:self.report()#If debug

        def _gatherInfo_(self): 
            self.str_orientation = self.mi_go.str_jointOrientation #Link
            self.str_partName = self.mi_go.str_partName		    

            self.d_colors = {'left':metaUtils.getSettingsColors('left'),
                             'right':metaUtils.getSettingsColors('right'),
                             'center':metaUtils.getSettingsColors('center')}

            #Orient info ------------------------------------------------------------------------------------------------
            self.v_aimNegative = cgmValid.simpleAxis(self.str_orientation[0]+"-").p_vector
            self.v_aim = cgmValid.simpleAxis(self.str_orientation[0]).p_vector	
            self.v_up = cgmValid.simpleAxis(self.str_orientation[1]).p_vector	

            #Find our helpers -------------------------------------------------------------------------------------------
            self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise Exception,"%s >>> No suitable helper found"%(_str_funcName)
            self.mi_leftBrowCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftBrowHelper'),noneValid=False)

            #>> Find our joint lists ===================================================================
            ml_handleJoints = self.mi_module.rigNull.msgList_get('handleJoints')
            ml_rigJoints = self.mi_module.rigNull.msgList_get('rigJoints')

            self.ml_browLeftHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                            cgmDirection = 'left',
                                                                            cgmName = 'brow')
            self.ml_browRightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                             cgmDirection = 'right',
                                                                             cgmName = 'brow')	 
            self.ml_browCenterHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                              cgmDirection = 'center',
                                                                              cgmName = 'brow')
            if not self.ml_browLeftHandles:raise Exception,"Failed to find left brow handle joints"
            if not self.ml_browRightHandles:raise Exception,"Failed to find right brow handle joints"
            if not self.ml_browCenterHandles:raise Exception,"Failed to find center brow rig joints"

            #>> Cheek --------------------------------------------------------------------------
            self.ml_cheekLeftHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                             cgmDirection = 'left',
                                                                             cgmName = 'uprCheek')
            self.ml_cheekRightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                              cgmDirection = 'right',
                                                                              cgmName = 'uprCheek')		    

            #>> Temple --------------------------------------------------------------------------
            self.ml_templeLeftHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                              cgmDirection = 'left',
                                                                              cgmName = 'temple')
            self.ml_templeRightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                               cgmDirection = 'right',
                                                                               cgmName = 'temple')

            #Rig joints... ---------------------------------------------------------------------
            self.ml_leftRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                          cgmDirection = 'left')
            self.ml_rightRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                           cgmDirection = 'right')
            self.ml_centerRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                            cgmDirection = 'center')	
            self.ml_topRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                         cgmDirection = 'top')	
            self.ml_backRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                          cgmDirection = 'back')		    
            if not self.ml_leftRigJoints:raise Exception,"Failed to find left rig joints"
            if not self.ml_rightRigJoints:raise Exception,"Failed to find right rig joints"
            if not self.ml_centerRigJoints:raise Exception,"Failed to find center rig joints"	    

            #>> calculate ------------------------------------------------------------------------
            self.f_browLength = distance.returnCurveLength(self.mi_helper.leftBrowHelper.mNode)	    	    
            self.f_baseDistance = self.f_browLength /10
            '''
	    ml_measureJointList = self.ml_browLeftHandles
	    try:#Get a casted base distance
		d_return = RayCast.findMeshIntersectionFromObjectAxis(self.mi_go._targetMesh[0],ml_measureJointList[0].mNode,axis=self.str_orientation[0]+'+')
		if d_return:
		    pos = d_return.get('hit')			
		    self.f_baseDistance = distance.returnDistanceBetweenPoints(pos,ml_measureJointList[0].getPosition()) * 2
		if not d_return:raise Exception
	    except:
		self.f_baseDistance = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_measureJointList]) /4 		
	    '''
            #>> Running lists --------------------------------------------------------------------
            self.ml_handles = []
            self.ml_pinHandles = []

            return True

        def _browShapes_(self): 

            d_build = {'left':{'jointList': self.ml_browLeftHandles},
                       'right':{'jointList': self.ml_browRightHandles},
                       'center':{'jointList': self.ml_browCenterHandles},}

            for str_direction in d_build.keys():
                ml_handleCrvs = []		
                ml_jointList = d_build[str_direction].get('jointList')
                l_colors = self.d_colors[str_direction]
                __baseDistance = self.f_baseDistance
                """
		try:#Get a casted base distance
		    d_return = RayCast.findMeshIntersectionFromObjectAxis(self.mi_go._targetMesh[0],ml_jointList[0].mNode,axis=self.str_orientation[0]+'+')
		    if d_return:
			pos = d_return.get('hit')			
			__baseDistance = distance.returnDistanceBetweenPoints(pos,ml_jointList[0].getPosition()) * 2
		    if not d_return:raise Exception
		except:
		    __baseDistance = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_jointList]) /4 		
		"""
                int_lenMax = len(ml_jointList)    
                for i,mObj in enumerate(ml_jointList):
                    self.progressBar_set(status = "shaping : '%s'... "%mObj.p_nameShort, progress = i, maxValue = int_lenMax)		    				    		    		    		    
                    try:
                        if mObj.getAttr('isSubControl') or len(ml_jointList) >1 and mObj in [ml_jointList[1]]:
                            _size = __baseDistance * 1
                            _color = l_colors[1]
                        else:
                            _size = __baseDistance * 1.5
                            _color = l_colors[0]

                        if str_direction == 'center':
                            _size = __baseDistance * 1			    

                        mi_crv =  cgmMeta.asMeta(curves.createControlCurve('circle',size = _size,direction=self.str_orientation[0]+'+'),'cgmObject',setClass=False)	
                        SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)
                        str_grp = mi_crv.doGroup()
                        if str_direction == 'right':
                            mi_crv.__setattr__("t%s"%self.str_orientation[0],-__baseDistance*2)
                        else:
                            mi_crv.__setattr__("t%s"%self.str_orientation[0],__baseDistance*2)			    
                        mi_crv.parent = False
                        mc.delete(str_grp)

                        #>>Color curve --------------------------------------------------------------------------------		    		    
                        if mObj.getAttr('isSubControl'):
                            curves.setCurveColorByName(mi_crv.mNode,_color)  
                        else:curves.setCurveColorByName(mi_crv.mNode,_color)  
                        #>>Copy tags and name		    
                        mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                        mi_crv.doName()
                        mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
                        ml_handleCrvs.append(mi_crv)

                    except Exception,error:
                        raise Exception,"Curve create fail! handle: '%s' | error: %s"%(mObj.p_nameShort,error)  

                self.ml_handles.extend(ml_handleCrvs)	    

        def _uprCheekShapes_(self): 
            if not self.ml_cheekLeftHandles and self.ml_cheekRightHandles:
                return False

            d_build = {'left':{'jointList': self.ml_cheekLeftHandles},
                       'right':{'jointList': self.ml_cheekRightHandles},
                       }

            for str_direction in d_build.keys():
                ml_handleCrvs = []		
                ml_jointList = d_build[str_direction].get('jointList')
                l_colors = self.d_colors[str_direction]
                __baseDistance = self.f_baseDistance
                """
		try:#Get a casted base distance
		    d_return = RayCast.findMeshIntersectionFromObjectAxis(self.mi_go._targetMesh[0],ml_jointList[0].mNode,axis=self.str_orientation[0]+'+')
		    if d_return:
			pos = d_return.get('hit')			
			__baseDistance = distance.returnDistanceBetweenPoints(pos,ml_jointList[0].getPosition()) * 2
		    if not d_return:raise Exception
		except:
		    __baseDistance = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_jointList]) /4 		
		"""
                for mObj in ml_jointList:
                    try:
                        if mObj.getAttr('isSubControl') or len(ml_jointList) >1 and mObj in [ml_jointList[1]]:
                            _size = __baseDistance * .8
                            _color = l_colors[1]
                        else:
                            _size = __baseDistance * 1.5
                            _color = l_colors[0]

                        mi_crv =  cgmMeta.cgmObject(curves.createControlCurve('circle',size = _size,direction=self.str_orientation[0]+'+'),setClass=False)	
                        SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)
                        str_grp = mi_crv.doGroup()
                        if str_direction == 'right':
                            mi_crv.__setattr__("t%s"%self.str_orientation[0],-__baseDistance)
                        else:
                            mi_crv.__setattr__("t%s"%self.str_orientation[0],__baseDistance)

                        mi_crv.parent = False
                        mc.delete(str_grp)

                        #>>Color curve --------------------------------------------------------------------------------		    		    
                        if mObj.getAttr('isSubControl'):
                            curves.setCurveColorByName(mi_crv.mNode,_color)  
                        else:curves.setCurveColorByName(mi_crv.mNode,_color)  
                        #>>Copy tags and name		    
                        mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                        mi_crv.doName()
                        mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
                        ml_handleCrvs.append(mi_crv)

                    except Exception,error:
                        raise Exception,"Curve create fail! handle: '%s' | error: %s"%(mObj.p_nameShort,error)  
                self.ml_handles.extend(ml_handleCrvs)

        def _templeShapes_(self): 
            if not self.ml_templeLeftHandles and self.ml_templeRightHandles:
                return False

            d_build = {'left':{'jointList': self.ml_templeLeftHandles},
                       'right':{'jointList': self.ml_templeRightHandles},
                       }

            for str_direction in d_build.keys():
                ml_handleCrvs = []		
                ml_jointList = d_build[str_direction].get('jointList')
                l_colors = self.d_colors[str_direction]
                __baseDistance = self.f_baseDistance

                for mObj in ml_jointList:
                    try:
                        if mObj.getAttr('isSubControl') or len(ml_jointList) >1 and mObj in [ml_jointList[1]]:
                            _size = __baseDistance * .8
                            _color = l_colors[1]
                        else:
                            _size = __baseDistance * 1.1
                            _color = l_colors[0]

                        mi_crv =  cgmMeta.asMeta(curves.createControlCurve('circle',size = _size,direction=self.str_orientation[0]+'+'),'cgmObject',setClass=False)	
                        SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)
                        str_grp = mi_crv.doGroup()
                        if str_direction == 'right':
                            mi_crv.__setattr__("t%s"%self.str_orientation[0],-__baseDistance)
                        else:
                            mi_crv.__setattr__("t%s"%self.str_orientation[0],__baseDistance)			

                        mi_crv.parent = False
                        mc.delete(str_grp)

                        #>>Color curve --------------------------------------------------------------------------------		    		    
                        if mObj.getAttr('isSubControl'):
                            curves.setCurveColorByName(mi_crv.mNode,_color)  
                        else:curves.setCurveColorByName(mi_crv.mNode,_color)  
                        #>>Copy tags and name		    
                        mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                        mi_crv.doName()
                        mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
                        ml_handleCrvs.append(mi_crv)

                    except Exception,error:
                        raise Exception,"Curve create fail! handle: '%s' | error: %s"%(mObj.p_nameShort,error)  
                self.ml_handles.extend(ml_handleCrvs)	

        def _facePins_(self): 
            #distance.returnCurveLength(self.mi_jawLineCrv.mNode)
            __baseDistance = self.f_browLength / 5
            log.info("%s >>> baseDistance : %s"%(self._str_reportStart,__baseDistance))

            d_build = {'left':{'jointList': self.ml_leftRigJoints},
                       'right':{'jointList': self.ml_rightRigJoints},
                       'center':{'jointList': self.ml_centerRigJoints + self.ml_topRigJoints + self.ml_backRigJoints},}

            for str_direction in d_build.keys():
                ml_handleCrvs = []		
                ml_jointList = d_build[str_direction].get('jointList')
                l_colors = self.d_colors[str_direction]
                _size = __baseDistance / 3
                _color = l_colors[1]	

                if str_direction == 'right':
                    str_cast = self.str_orientation[0]+'-'	
                else:
                    str_cast = self.str_orientation[0]+'+'	

                int_lenMax = len(ml_jointList)
                for i,mObj in enumerate(ml_jointList):
                    self.progressBar_set(status = "shaping : '%s'... "%mObj.p_nameShort, progress = i, maxValue = int_lenMax)		    				    		    		    
                    try:
                        mi_crv =  cgmMeta.asMeta(curves.createControlCurve('semiSphere',size = _size,direction=str_cast),'cgmObject',setClass=False)	
                        try:
                            d_return = RayCast.findMeshIntersectionFromObjectAxis(self.mi_go._targetMesh[0],mObj.mNode,axis=str_cast)
                            if d_return:
                                pos = d_return.get('hit')			
                                mc.move (pos[0],pos[1],pos[2], mi_crv.mNode)
                                mc.delete( mc.orientConstraint(mObj.mNode,mi_crv.mNode,maintainOffset = False))
                            if not d_return:raise Exception
                        except:
                            SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)
                            if str_direction == 'right':
                                pass
                                #mi_crv.__setattr__("r%s"%self.str_orientation[1],(mi_crv.getAttr("r%s"%self.str_orientation[1]) + 180))		
                        #>>Color curve --------------------------------------------------------------------------------		    		    
                        curves.setCurveColorByName(mi_crv.mNode,_color) 

                        #>>Copy tags and name		    
                        mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                        mi_crv.addAttr('cgmTypeModifier','direct',lock=True)
                        mi_crv.doName()
                        mi_crv.connectChildNode(mObj,'targetJoint','controlShape')
                        ml_handleCrvs.append(mi_crv)

                        #>>Copy pivot ---------------------------------------------------------------------------------
                        #mi_crv.doCopyPivot(mObj.mNode)
                    except Exception,error:
                        raise Exception,"Curve create fail! handle: '%s' | error: %s"%(mObj.p_nameShort,error)  
                self.ml_pinHandles.extend(ml_handleCrvs)	

    def _connect_(self): 
        self.mi_go.d_returnControls['l_handleCurves'] = [mObj.p_nameShort for mObj in self.ml_handles]
        self.mi_go.md_ReturnControls['ml_handleCurves'] = self.ml_handles
        self._mi_rigNull.msgList_connect('shape_handleCurves',self.ml_handleCrvs,'owner')

        self.mi_go.d_returnControls['l_pinCurves'] = [mObj.p_nameShort for mObj in self.ml_handles]
        self.mi_go.md_ReturnControls['ml_pinCurves'] = self.ml_handles
        self._mi_rigNull.msgList_connect('shape_pinCurves',self.ml_pinHandles,'owner')

        return True

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()  

def shapeCast_mouthNose(*args,**kws):
    class fncWrap(ShapeCasterFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = 'shapeCast_mouthNose(%s)'%self.mi_module.p_nameShort
            self._b_autoProgressBar = 1	    
            self._b_reportTimes = 1
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
                                #{'step':'Jaw Shapes','call':self._jawShapes_},	                        
                                {'step':'Tongue Shapes','call':self._tongueShapes_},
                                {'step':'Teeth Shapes','call':self._teethShapes_},                                
                                #{'step':'Basic Shapes','call':self._simpleShapeCasts_},	                        
                                #{'step':'MouthMove Shapes','call':self._mouthMoveShape_},
                                #{'step':'Nose Move Shape','call':self._noseMoveShape_},	                        	                        
                                #{'step':'Face Pins','call':self._facePins_},
                                #may not be needed{'step':'Connect','call':self._connect_},
                                ]

            assert self.mi_module.mClass == 'cgmMouthNose',"%s >>> Module is not type: 'cgmMouthNose' | type is: '%s'"%(self._str_funcName,self.mi_module.mClass)

            #The idea is to register the functions needed to be called
            #=================================================================
            if log.getEffectiveLevel() == 10:self.report()#If debug

        def _gatherInfo_(self): 
            self.str_orientation = self.mi_go.str_jointOrientation #Link
            self.str_partName = self.mi_go.str_partName		    
            self.d_colors = {'left':metaUtils.getSettingsColors('left'),
                             'right':metaUtils.getSettingsColors('right'),
                             'center':metaUtils.getSettingsColors('center')}

            #Orient info ------------------------------------------------------------------------------------------------
            self.v_aimNegative = cgmValid.simpleAxis(self.str_orientation[0]+"-").p_vector
            self.v_aim = cgmValid.simpleAxis(self.str_orientation[0]).p_vector	
            self.v_up = cgmValid.simpleAxis(self.str_orientation[1]).p_vector	

            #Find our helpers -------------------------------------------------------------------------------------------
            self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise Exception,"%s >>> No suitable helper found"%(_str_funcName)

            #self.mi_skullPlate = cgmMeta.validateObjArg(self.mi_helper.getMessage('skullPlate'),noneValid=False)
            #self.str_skullPlate = self.mi_skullPlate.mNode

            #>> Find our joint lists ===================================================================
            ml_handleJoints = self.mi_module.rigNull.msgList_get('handleJoints')
            ml_rigJoints = self.mi_module.rigNull.msgList_get('rigJoints')
            self.md_handles = {}
            d_ = self.md_handles#short version	 
            
            if True is False:#OLD STUFF...from joint build method
                #Mouth --------------------------------------------------------------------------
                d_['lipUprCenter'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                           cgmDirection = 'center',
                                                                           cgmName = 'lipUpr')	    
                d_['lipUprLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                         cgmDirection = 'left',
                                                                         cgmName = 'lipUpr')
                d_['lipUprRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                          cgmDirection = 'right',
                                                                          cgmName = 'lipUpr')
                d_['lipLwrCenter'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                           cgmDirection = 'center',
                                                                           cgmName = 'lipLwr')	    	    
                d_['lipLwrLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                         cgmDirection = 'left',
                                                                         cgmName = 'lipLwr')
                d_['lipLwrRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                          cgmDirection = 'right',
                                                                          cgmName = 'lipLwr') 
                d_['lipCornerLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                            cgmDirection = 'left',
                                                                            cgmName = 'lipCorner')
                d_['lipCornerRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                             cgmDirection = 'right',
                                                                             cgmName = 'lipCorner')  
                d_['mouthMove'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                        cgmName = 'mouthMove')  	    
                #Smile Line --------------------------------------------------------------------------
                d_['sneerLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                        cgmDirection = 'left',
                                                                        cgmName = 'sneer')
                d_['sneerRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                         cgmDirection = 'right',
                                                                         cgmName = 'sneer') 
                d_['smileLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                        cgmDirection = 'left',
                                                                        cgmName = 'smile')
                d_['smileRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                         cgmDirection = 'right',
                                                                         cgmName = 'smile')  
                d_['uprSmileLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                           cgmDirection = 'left',
                                                                           cgmName = 'uprSmile')
                d_['uprSmileRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                            cgmDirection = 'right',
                                                                            cgmName = 'uprSmile') 	    
                d_['smileBaseLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                            cgmDirection = 'left',
                                                                            cgmName = 'smileBase')
                d_['smileBaseRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                             cgmDirection = 'right',
                                                                             cgmName = 'smileBase') 
    
                #>> nose --------------------------------------------------------------------------
                d_['noseTip'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                      cgmName = 'noseTip')
                d_['noseUnder'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                        cgmName = 'noseUnder')	
                d_['nostrilLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                          cgmDirection = 'left',
                                                                          cgmName = 'nostril')	
                d_['nostrilRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                           cgmDirection = 'right',
                                                                           cgmName = 'nostril')	
                d_['nose'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                   cgmName = 'noseMove')		    
                d_['noseTop'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                      cgmName = 'noseTop')		    
                #>> Cheek --------------------------------------------------------------------------
                d_['uprCheekOuterLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                                cgmDirection = 'left',cgmPosition = 'outer',
                                                                                cgmName = 'uprCheek')
                d_['uprCheekOuterRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                                 cgmDirection = 'right',cgmPosition = 'outer',
                                                                                 cgmName = 'uprCheek')
                d_['uprCheekInnerLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                                cgmDirection = 'left',cgmPosition = 'inner',
                                                                                cgmName = 'uprCheek')
                d_['uprCheekInnerRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                                 cgmDirection = 'right',cgmPosition = 'inner',
                                                                                 cgmName = 'uprCheek')	    
                d_['cheekAnchorLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                              cgmDirection = 'left',
                                                                              cgmName = 'cheekAnchor')	
                d_['cheekAnchorRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                               cgmDirection = 'right',
                                                                               cgmName = 'cheekAnchor')	    
                #>> Jaw --------------------------------------------------------------------------	    
                d_['jaw'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                  cgmName = 'jaw')
                '''
                d_['jawAnchorLeft'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                            cgmDirection = 'left',
                                                                            cgmName = 'jawAnchor')	
                d_['jawAnchorRight'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                            cgmDirection = 'right',
                                                                            cgmName = 'jawAnchor')	
                                                                            '''
                d_['chin'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                   cgmName = 'chin')	    	
                d_['jawLineCenter'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                            cgmDirection = 'center',
                                                                            cgmName = 'jawLine')
                
            d_['tongueTip'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                    cgmName = 'tongueTip')
            d_['tongueBase'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
                                                                     cgmName = 'tongueBase')  
            d_['teethUpr'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                     cgmName = 'teeth',
                                                                     cgmPosition = 'upper')  
            d_['teethLwr'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                     cgmName = 'teeth',
                                                                     cgmPosition = 'lower')              
            for k in d_.iterkeys():
                buffer = d_.get(k)
                if not buffer:raise Exception,"Failed to find %s handle joints"%k
                if len(buffer) == 1:
                    d_[k] = buffer[0]

            #Rig joints... ---------------------------------------------------------------------
            self.ml_leftRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                          cgmDirection = 'left')
            self.ml_rightRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                           cgmDirection = 'right')
            self.ml_centerRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                            cgmDirection = 'center')

            '''for tag in ['noseTip','noseTop','noseUnder','noseBase']:
                self.ml_centerRigJoints.extend(metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                                     cgmName = tag))

            if not self.ml_leftRigJoints:raise Exception,"Failed to find left rig joints"
            if not self.ml_rightRigJoints:raise Exception,"Failed to find right rig joints"
            if not self.ml_centerRigJoints:raise Exception,"Failed to find center rig joints"'''

            self.ml_rigCull = []
            self.ml_rigCull.extend(metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                         cgmName = 'tongue'))
            self.ml_rigCull.extend(metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                         cgmName = 'jaw'))
            self.ml_rigCull.extend(metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
                                                                         cgmName = 'teeth'))	    
            log.info("%s cull list:"%self._str_reportStart)
            #for mJnt in self.ml_rigCull:
                #log.info(">>> " + mJnt.p_nameShort)

            try:#>> calculate ------------------------------------------------------------------------
                #ml_measureJointList = [d_['smileBaseLeft'],d_['smileLeft'],d_['sneerLeft']]
                #self.f_baseDistance = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_measureJointList]) /4 		
                #self.f_mouthWidth = distance.returnDistanceBetweenObjects(self.md_handles['lipCornerRight'].mNode,self.md_handles['lipCornerLeft'].mNode)
                self.f_mouthWidth = distance.returnCurveLength(self.mi_helper.getMessage('mouthMidCastHelper'))                                
                self.f_baseDistance = self.f_mouthWidth / 4
            except Exception,error:raise Exception,"Initial distance calculation | %s"%error
            #>> Running lists --------------------------------------------------------------------
            self.ml_handles = []
            self.ml_pinHandles = []
            self.report()
            return True

        def _tongueShapes_(self): 
            #if not self.md_handles['tongue']:
                #return False

            ml_handleCrvs = []		

            l_colors = self.d_colors['center']
            __baseDistance = self.f_baseDistance
            _size = self.f_mouthWidth
            log.info(_size)

            d_build = {'tongueBase':{'mi_obj': self.md_handles['tongueBase'],'shape':'circleArrow','shapeMulti':1.25},
                       'tongueTip':{'mi_obj': self.md_handles['tongueTip'],'shape':'arrowsOnBall','centerPivot':True}}

            for str_name in d_build.keys():
                d_buffer = d_build[str_name]
                try:
                    mObj = d_buffer['mi_obj']
                    str_shape = d_buffer['shape']
                    f_multi = d_buffer.get('shapeMulti') or 1
                    b_centerPivot = d_buffer.get('centerPivot') or False
                    mi_crv =  cgmMeta.asMeta(curves.createControlCurve(str_shape,size = (_size * f_multi),direction=self.str_orientation[0]+'+'),'cgmObject',setClass=False)	
                    if b_centerPivot:
                        mc.xform(mi_crv.mNode,ws = True, piv = distance.returnCenterPivotPosition(mi_crv.mNode))
                    SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)

                    mi_crv.__setattr__("s%s"%self.str_orientation[1],.4)
                    mc.makeIdentity(mi_crv.mNode, apply=True,s=1,n=0)	

                    #>>Color curve --------------------------------------------------------------------------------		    		    
                    curves.setCurveColorByName(mi_crv.mNode,l_colors[0])  

                    #>>Copy tags and name --------------------------------------------------------------------------------		    
                    mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                    mi_crv.doName()
                    mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
                    ml_handleCrvs.append(mi_crv)

                except Exception,error:
                    raise Exception,"%s create fail! | error: %s"%(str_name,error)  
            self.ml_handles.extend(ml_handleCrvs)
            
        def _teethShapes_(self): 
            #if not self.md_handles['tongue']:
                #return False
            #self.mi_helper.getMessage('mouthMidCastHelper')
            ml_handleCrvs = []		

            l_colors = self.d_colors['center']
            __baseDistance = self.f_baseDistance
            _size = self.f_mouthWidth
            _mi_baseCurve = self.mi_helper.getMessageAsMeta('mouthMidCastHelper')
            ml_handleCrvs = []		
            d_build = {'teethUpr':{'mi_obj': self.md_handles['teethUpr'],'shape':'U','shapeMulti':.1,'offset_up':.5},
                       'teethLwr':{'mi_obj': self.md_handles['teethLwr'],'shape':'L','shapeMulti':.1,'offset_up':-.5}}

            for str_name in d_build.keys():
                d_buffer = d_build[str_name]
                try: 
                    mObj = d_buffer['mi_obj']
                    f_multi = d_buffer.get('shapeMulti') or 1
                    str_shape = d_buffer['shape']                    
                    b_centerPivot = d_buffer.get('centerPivot') or False
                    f_offset_up = d_buffer.get('offset_up') or 0.0
                    #mi_crv =  cgmMeta.asMeta(curves.createControlCurve(str_shape,size = (_size * f_multi),direction=self.str_orientation[0]+'+'),'cgmObject',setClass=False)	
                    mi_crv =  cgmMeta.asMeta(curves.createTextCurve(str_shape,size = (_size * f_multi)),'cgmObject',setClass=False)	
                    
                    if b_centerPivot:
                        mc.xform(mi_crv.mNode,ws = True, piv = distance.returnCenterPivotPosition(mi_crv.mNode))
                    SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)

                    #mi_crv.__setattr__("s%s"%self.str_orientation[1], .2)
                    mc.xform(mi_crv.mNode, t = [0,f_offset_up,0], r = True)
                    
                    mc.makeIdentity(mi_crv.mNode, apply=True,s=1,n=0)	

                    #>>Color curve --------------------------------------------------------------------------------		    		    
                    curves.setCurveColorByName(mi_crv.mNode,l_colors[0])  

                    #>>Copy tags and name --------------------------------------------------------------------------------		    
                    mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                    mi_crv.doName()
                    mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
                    ml_handleCrvs.append(mi_crv)

                except Exception,error:
                    raise Exception,"%s create fail! | error: %s"%(str_name,error)  
            self.ml_handles.extend(ml_handleCrvs)
            
        def _mouthMoveShape_(self): 	    
            ml_handleCrvs = []		

            l_colors = self.d_colors['center']
            __baseDistance = self.f_baseDistance
            _size = self.f_mouthWidth

            mObj = self.md_handles['mouthMove']
            str_shape = 'squareRounded'
            f_multi = .4

            #b_centerPivot = d_buffer.get('centerPivot') or False
            mi_crv =  cgmMeta.asMeta(curves.createControlCurve(str_shape,size = (_size * f_multi),direction=self.str_orientation[0]+'+'),'cgmObject',setClass=False)	
            #if b_centerPivot:
                #mc.xform(mi_crv.mNode,ws = True, piv = distance.returnCenterPivotPosition(mi_crv.mNode))

            SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)
            pos1 = self.md_handles['lipLwrCenter'].controlShape.getPosition()
            pos2 = self.md_handles['lipUprCenter'].controlShape.getPosition()
            pos = distance.returnAveragePointPosition([pos1,pos2])
            mc.move (pos[0],pos[1],pos[2], mi_crv.mNode)

            mi_crv.__setattr__("s%s"%self.str_orientation[1],.1)	    
            mc.makeIdentity(mi_crv.mNode, apply=True,s=1,n=0)	

            #>>Color curve --------------------------------------------------------------------------------		    		    
            curves.setCurveColorByName(mi_crv.mNode,l_colors[0])  

            #>>Copy tags and name --------------------------------------------------------------------------------		    
            mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
            mi_crv.doName()
            mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
            ml_handleCrvs.append(mi_crv)

            self.ml_handles.extend(ml_handleCrvs)

        def _noseMoveShape_(self): 	    
            ml_handleCrvs = []		

            l_colors = self.d_colors['center']
            __baseDistance = self.f_baseDistance
            _size = self.f_mouthWidth

            mObj = self.md_handles['nose']
            mi_castLoc = self.md_handles['noseTip'].doLoc(fastMode = True)
            pos1 = self.md_handles['nostrilLeft'].getPosition()
            pos2 = self.md_handles['nostrilRight'].getPosition()
            pos = distance.returnAveragePointPosition([pos1,pos2])
            f_castDistance = distance.returnDistanceBetweenPoints(pos1,pos2) * 1.5
            mc.move (pos[0],pos[1],pos[2], mi_castLoc.mNode)	    

            str_crv = ShapeCast.createMeshSliceCurve(self.mi_go._targetMesh[0],mi_castLoc.mNode,
                                                     rotateBank = -30,curveDegree=3,posOffset = [0,0,self.mi_go.f_skinOffset/2],
                                                     maxDistance=f_castDistance,
                                                     points=8,returnDict = False,latheAxis=self.str_orientation[0],
                                                     aimAxis=self.str_orientation[1]+'-')
            mi_crv =  cgmMeta.asMeta(str_crv,'cgmObject',setClass=False)	
            mi_castLoc.delete()
            #b_centerPivot = d_buffer.get('centerPivot') or False
            #if b_centerPivot:
                #mc.xform(mi_crv.mNode,ws = True, piv = distance.returnCenterPivotPosition(mi_crv.mNode))

            #>>Color curve --------------------------------------------------------------------------------		    		    
            curves.setCurveColorByName(mi_crv.mNode,l_colors[0])  

            #>>Copy tags and name --------------------------------------------------------------------------------		    
            mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
            mi_crv.doName()
            mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
            ml_handleCrvs.append(mi_crv)

            self.ml_handles.extend(ml_handleCrvs)

        def _jawShapes_(self): 	    
            ml_handleCrvs = []		

            l_colors = self.d_colors['center']
            __baseDistance = self.f_baseDistance
            _size = self.f_mouthWidth

            mObj = self.md_handles['jaw']
            mTarget = self.md_handles['jawLineCenter']
            str_shape = 'arrowsOnBall'
            f_multi = .5

            #b_centerPivot = d_buffer.get('centerPivot') or False
            mi_crv =  cgmMeta.asMeta(curves.createControlCurve(str_shape,size = (_size * f_multi),direction=self.str_orientation[0]+'+'),'cgmObject',setClass=False)	
            #if b_centerPivot:
                #mc.xform(mi_crv.mNode,ws = True, piv = distance.returnCenterPivotPosition(mi_crv.mNode))

            SNAP.go(mi_crv,mTarget.mNode,move=True,orient=True)
            SNAP.go(mi_crv,self.mi_go._targetMesh[0],snapToSurface=True)					

            mi_crv.__setattr__("s%s"%self.str_orientation[2],1.5)
            mi_crv.__setattr__("s%s"%self.str_orientation[0],.6)	    
            mc.makeIdentity(mi_crv.mNode, apply=True,s=1,n=0)	

            #>>Color curve --------------------------------------------------------------------------------		    		    
            curves.setCurveColorByName(mi_crv.mNode,l_colors[0])  

            #>>Copy tags and name --------------------------------------------------------------------------------		    
            mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
            mi_crv.doName()
            mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
            ml_handleCrvs.append(mi_crv)

            #>>Orient 
            mc.delete( mc.normalConstraint(self.str_skullPlate,mi_crv.mNode, weight = 1,
                                           aimVector = self.v_aim, upVector = self.v_up,
                                           worldUpType = 'scene' ))	    

            self.ml_handles.extend(ml_handleCrvs)

        def _simpleShapeCasts_(self):	
            l_build = [{'key':'smileLeft','isSub':True},{'key':'smileBaseLeft','isSub':True},{'key':'sneerLeft'},{'key':'uprSmileLeft','isSub':True},
                       {'key':'smileRight','isSub':True},{'key':'smileBaseRight','isSub':True},{'key':'sneerRight'},{'key':'uprSmileRight','isSub':True},	
                       {'key':'lipUprCenter','multi':.5},{'key':'lipUprLeft','isSub':True},{'key':'lipUprRight','isSub':True},
                       {'key':'lipLwrCenter','multi':.5},{'key':'lipLwrLeft','isSub':True},{'key':'lipLwrRight','isSub':True},
                       {'key':'lipCornerLeft'},{'key':'lipCornerRight'},{'key':'chin'},
                       #{'key':'jawAnchorLeft'},{'key':'jawAnchorRight'},
                       {'key':'cheekAnchorLeft'},{'key':'cheekAnchorRight'},
                       {'key':'uprCheekOuterLeft'},{'key':'uprCheekInnerLeft','isSub':True},{'key':'uprCheekInnerRight','isSub':True},{'key':'uprCheekOuterRight'},	               
                       {'key':'noseTop','isSub':True},{'key':'noseTip','isSub':True},{'key':'noseUnder','isSub':True},{'key':'nostrilLeft','isSub':True},{'key':'nostrilRight','isSub':True}]
            ml_handleCrvs = []
            int_lenMax = len(l_build)	    
            for i,d in enumerate(l_build):
                try:#For each key ================================================================================
                    try:#Get info --------------------------------------------------------------------------------
                        mObj = self.md_handles[d['key']]
                        _str_mObj = mObj.p_nameShort
                        try:str_direction = mObj.cgmDirection.lower()
                        except:str_direction = 'center'
                        l_colors = self.d_colors[str_direction]
                        __baseDistance = self.f_baseDistance

                        b_isSub = d.get('isSub') or False
                        f_multi = d.get('multi') or .8
                        _size = __baseDistance * f_multi
                        if b_isSub:
                            _size = _size * .7
                            _color = l_colors[1]
                            _shape = 'circle'			    
                        else:
                            _color = l_colors[0]
                            _shape = 'squareRounded'

                        self.progressBar_set(status = "On: '%s'"%_str_mObj, progress = i, maxValue = int_lenMax)		    				    		    

                    except Exception,error:
                        raise Exception,"%s info fail | %s"%(i,error)

                    mi_crv =  cgmMeta.asMeta(curves.createControlCurve(_shape,size = _size, direction=self.str_orientation[0]+'+'),'cgmObject',setClass=False)	
                    SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)
                    str_grp = mi_crv.doGroup()
                    if str_direction == 'right':
                        mi_crv.__setattr__("t%s"%self.str_orientation[0],-__baseDistance)
                    else:
                        mi_crv.__setattr__("t%s"%self.str_orientation[0],__baseDistance)

                    mi_crv.parent = False
                    mc.delete(str_grp)

                    #>>Color curve --------------------------------------------------------------------------------		    		    
                    curves.setCurveColorByName(mi_crv.mNode,_color)

                    #>>Copy tags and name --------------------------------------------------------------------------------		    
                    mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                    mi_crv.doName()
                    mi_crv.connectChildNode(mObj,'handleJoint','controlShape')
                    ml_handleCrvs.append(mi_crv)

                except Exception,error:
                    try:raise Exception,"Curve create fail! handle: '%s' | error: %s"%(mObj.p_nameShort,error)
                    except Exception,error:raise Exception,"Curve create fail! handle: '%s' | error: %s"%(mObj,error)
            self.ml_handles.extend(ml_handleCrvs)	

        def _facePins_(self): 
            __baseDistance = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in self.ml_leftRigJoints]) /2 
            log.info("%s >>> baseDistance : %s"%(self._str_reportStart,__baseDistance))

            d_build = {'left':{'jointList': self.ml_leftRigJoints},
                       'right':{'jointList': self.ml_rightRigJoints},
                       'center':{'jointList': self.ml_centerRigJoints},}

            for str_direction in d_build.keys():
                ml_handleCrvs = []		
                ml_jointList = d_build[str_direction].get('jointList')
                l_colors = self.d_colors[str_direction]
                _size = __baseDistance / 5
                _color = l_colors[1]	

                if str_direction == 'right':
                    str_cast = self.str_orientation[0]+'-'	
                else:
                    str_cast = self.str_orientation[0]+'+'	

                int_lenMax = len(ml_jointList)		
                for i,mObj in enumerate(ml_jointList):
                    _str_obj = mObj.p_nameShort
                    self.progressBar_set(status = "'%s' | '%s'"%(str_direction,_str_obj), progress = i, maxValue = int_lenMax)		    				    		    

                    if mObj not in self.ml_rigCull:
                        try:
                            mi_crv =  cgmMeta.asMeta(curves.createControlCurve('semiSphere',size = _size,direction=str_cast),'cgmObject',setClass=False)	
                            try:
                                d_return = RayCast.findMeshIntersectionFromObjectAxis(self.mi_go._targetMesh[0],mObj.mNode,axis=str_cast)
                                if d_return:
                                    pos = d_return.get('hit')			
                                    mc.move (pos[0],pos[1],pos[2], mi_crv.mNode)
                                    mc.delete( mc.orientConstraint(mObj.mNode,mi_crv.mNode,maintainOffset = False))
                                if not d_return:raise Exception
                            except:
                                SNAP.go(mi_crv,mObj.mNode,move=True,orient=True)
                                if str_direction == 'right':
                                    pass
                                    #mi_crv.__setattr__("r%s"%self.str_orientation[1],(mi_crv.getAttr("r%s"%self.str_orientation[1]) + 180))		
                            #>>Color curve --------------------------------------------------------------------------------		    		    
                            curves.setCurveColorByName(mi_crv.mNode,_color) 

                            #>>Copy tags and name		    
                            mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                            mi_crv.addAttr('cgmTypeModifier','direct',lock=True)
                            mi_crv.doName()
                            mi_crv.connectChildNode(mObj,'targetJoint','controlShape')
                            ml_handleCrvs.append(mi_crv)

                            #>>Copy pivot ---------------------------------------------------------------------------------
                            #mi_crv.doCopyPivot(mObj.mNode)
                        except Exception,error:
                            raise Exception,"[Curve create fail! handle: '%s']{%s}"%(_str_obj,error)  
                self.ml_pinHandles.extend(ml_handleCrvs)	

        def _connect_(self): 
            self.mi_go.d_returnControls['l_handleCurves'] = [mObj.p_nameShort for mObj in self.ml_handles]
            self.mi_go.md_ReturnControls['ml_handleCurves'] = self.ml_handles
            self._mi_rigNull.msgList_connect('shape_handleCurves',self.ml_handleCrvs,'owner')

            self.mi_go.d_returnControls['l_pinCurves'] = [mObj.p_nameShort for mObj in self.ml_handles]
            self.mi_go.md_ReturnControls['ml_pinCurves'] = self.ml_handles
            self._mi_rigNull.msgList_connect('shape_pinCurves',self.ml_pinHandles,'owner')

            return True

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()  

def shapeCast_eyeball(*args,**kws):
    class fncWrap(ShapeCasterFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = 'shapeCast_eyeball(%s)'%self.mi_module.p_nameShort
            self._b_autoProgressBar = 1
            self._b_reportTimes = 1
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
                                {'step':'Build Iris','call':self._buildIris_},
                                {'step':'Build Pupil','call':self._buildPupil_},	                        
                                {'step':'Build FK','call':self._buildFK_},
                                {'step':'Build IK','call':self._buildIK_},
                                {'step':'Build Settings','call':self._buildSettings_},
                                {'step':'Build Eye Move','call':self._buildEyeMove_},
                                {'step':'Clean up','call':self._cleanUp_},
                                ]
            assert self.mi_module.mClass == 'cgmEyeball',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(self._str_funcName,self.mi_module.mClass)
            #The idea is to register the functions needed to be called
            #=================================================================
            if log.getEffectiveLevel() == 10:self.report()#If debug

        def _gatherInfo_(self): 
            self.str_orientation = self.mi_go.str_jointOrientation #Link
            self.str_partName = self.mi_go.str_partName		    
            self.str_direction = self.mi_go._direction	    
            self.d_colors = {'left':metaUtils.getSettingsColors('left'),
                             'right':metaUtils.getSettingsColors('right'),
                             'center':metaUtils.getSettingsColors('center')}

            self._f_midMulti = 2.5

            #Orient info ------------------------------------------------------------------------------------------------
            self.log_info('orient...')
            
            self.v_aimNegative = cgmValid.simpleAxis(self.str_orientation[0]+"-").p_vector
            self.v_aim = cgmValid.simpleAxis(self.str_orientation[0]).p_vector	
            self.v_up = cgmValid.simpleAxis(self.str_orientation[1]).p_vector	
            #Find our helpers -------------------------------------------------------------------------------------------
            self.log_info('main helpers...')
            
            self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise Exception,"%s >>> No suitable helper found"%(_str_funcName)

            #Find our helpers -------------------------------------------------------------------------------------------
            self.log_info('sub helpers...')            
            for attr in self.mi_helper.getAttrs(userDefined = True):#Get allof our Helpers
                if "Helper" in attr:
                    try:self.__dict__["mi_%s"%attr.replace('Helper','Crv')] = cgmMeta.validateObjArg(self.mi_helper.getMessage(attr),noneValid=False)
                    except Exception,error:raise Exception, " Failed to find '%s' | %s"%(attr,error)

            self._b_buildIris = self.mi_helper.buildIris
            self._b_buildPupil = self.mi_helper.buildPupil	    

            #>> Find our joint lists ===================================================================
            self.log_info('jointlist...')            
            ml_rigJoints = self.mi_module.rigNull.msgList_get('rigJoints')	    

            #>> calculate ------------------------------------------------------------------------
            self.log_info('calculate...')
            
            self.f_baseDistance = distance.returnDistanceBetweenObjects(self.mi_helper.mNode,
                                                                        self.mi_helper.pupilHelper.mNode)
            
            #_tmpScale = distance.returnBoundingBoxSize(self.mi_irisCrv.mNode)
            #self.f_irisSize = (_tmpScale[0]+_tmpScale[1])/2
            self.f_irisSize = distance.returnCurveDiameter(self.mi_irisCrv.mNode) 
            
            #_tmpScale = distance.returnBoundingBoxSize(self.mi_pupilCrv.mNode)
            #self.f_pupilSize = (_tmpScale[0]+_tmpScale[1])/2
            self.f_pupilSize = distance.returnCurveDiameter(self.mi_pupilCrv.mNode)

            #>> Get the iris/pupil base position
            self.log_info('baseDat...')
            
            mi_loc = cgmMeta.cgmNode("%s|curveShape2.ep[3]"%self.mi_helper.mNode).doLoc(fastMode = True)
            mi_loc.parent = self.mi_helper
            mi_loc.tz *= -1
            self._baseIrisPos = mi_loc.getPosition()
            self.mi_irisPosLoc = mi_loc

            #distance.returnBoundingBoxSizeToAverage(self.mi_irisCrv.mNode)
            #>> Running lists --------------------------------------------------------------------
            self.ml_handles = []	    
            return True

        def _buildFK_(self):
            try:#query ===========================================================
                mi_helper = self.mi_helper
                _baseDistance = self.f_baseDistance 
                _irisSize = self.f_irisSize
            except Exception,error: raise Exception,"!Query]{%s}"%error

            try:#Curve creation ===========================================================
                ml_curvesToCombine = []
                mi_tmpCrv = cgmMeta.asMeta( curves.createControlCurve('circle',
                                                                      direction = 'z+',
                                                                      size = _irisSize * .75,
                                                                      absoluteSize=False),'cgmObject',setClass=False)
                SNAP.go(mi_tmpCrv,mi_helper.mNode)
                mi_tmpGroup = cgmMeta.cgmObject( mi_tmpCrv.doGroup())
                mi_tmpCrv.__setattr__('t%s'%self.str_orientation[0],_baseDistance * self._f_midMulti)
                ml_curvesToCombine.append(mi_tmpCrv.doDuplicate(parentOnly = False))
                ml_curvesToCombine[-1].parent = False

                #SNAP.go(mi_tmpGroup.mNode,self.mi_irisPosLoc.mNode)
                mi_tmpCrv.__setattr__('t%s'%self.str_orientation[0],_baseDistance * 1.75)
                mi_tmpCrv.scale = [.75,.75,.75]
                ml_curvesToCombine.append(mi_tmpCrv.doDuplicate(parentOnly = False))
                ml_curvesToCombine[-1].parent = False

                l_trace = ShapeCast.joinCurves(ml_curvesToCombine)
                mi_last = ml_curvesToCombine.pop(-1)
                mi_last.delete()

                ml_curvesToCombine.extend([cgmMeta.cgmNode(crv) for crv in l_trace])
                mi_tmpGroup.delete()
                '''
		#Make a trace curve
		_str_trace = mc.curve (d=1, ep = [mi_helper.getPosition(),mi_crvBase.getPosition()], os=True)#build curves as we go to see what's up
		log.info(_str_trace)
		l_curvesToCombine = [_str_trace,mi_crvBase.mNode]
		'''
                #>>>Combine the curves
                try:newCurve = curves.combineCurves([mObj.mNode for mObj in ml_curvesToCombine]) 
                except Exception,error:raise Exception,"!Failed to combine]{%s}"%error

                mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(mi_helper.mNode,False) )

                try:curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
                except Exception,error:raise Exception,"Parent shape in place fail | error: %s"%error

                mc.delete(newCurve)
            except Exception,error: raise Exception,"!Curve create]{%s}"%error

            try:#Tag,name, color ===========================================================
                mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
                mi_crv.addAttr('cgmType',attrType='string',value = 'eyeball_FK',lock=True)
                mi_crv.doName()          	    

                #Color
                curves.setCurveColorByName(mi_crv.mNode,self.d_colors[self.str_direction][0]) 
            except Exception,error: raise Exception,"!Tag,name,color]{%s}"%error

            try:#connect ===========================================================
                self.mi_go.d_returnControls['eyeballFK'] = mi_crv.mNode
                self.mi_go.md_ReturnControls['eyeballFK'] = mi_crv
                self.mi_go._mi_rigNull.connectChildNode(mi_crv,'shape_eyeballFK','owner')
            except Exception,error: raise Exception,"!Connect]{%s}"%error

        def _buildIK_(self):
            try:#query ===========================================================
                mi_helper = self.mi_helper
                f_baseDistance = self.f_baseDistance  
                _irisSize = self.f_irisSize		
            except Exception,error: raise Exception,"!Query]{%s}"%error

            try:#Curve creation ===========================================================
                mi_crv = cgmMeta.asMeta( curves.createControlCurve('fatCross',
                                                                      direction = 'z+',
                                                                      size = _irisSize * 1,
                                                                      absoluteSize=False),'cgmObject',
                                            setClass=False)
                SNAP.go(mi_crv,mi_helper.mNode)
                mi_tmpGroup = cgmMeta.cgmObject( mi_crv.doGroup())
                mi_crv.__setattr__('t%s'%self.str_orientation[0],f_baseDistance * 6)
                mi_crv.parent = False
                mi_tmpGroup.delete()

            except Exception,error: raise Exception,"!Curve create]{%s}"%error

            try:#Tag,name, color ===========================================================
                mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
                mi_crv.addAttr('cgmType',attrType='string',value = 'eyeball_IK',lock=True)
                mi_crv.doName()          	    

                #Color
                curves.setCurveColorByName(mi_crv.mNode,self.d_colors[self.str_direction][0]) 
            except Exception,error: raise Exception,"!Tag,name,color]{%s}"%error

            try:#connect ===========================================================
                self.mi_go.d_returnControls['eyeballIK'] = mi_crv.mNode
                self.mi_go.md_ReturnControls['eyeballIK'] = mi_crv
                self.mi_go._mi_rigNull.connectChildNode(mi_crv,'shape_eyeballIK','owner')
            except Exception,error: raise Exception,"!Connect]{%s}"%error

        def _buildSettings_(self):
            try:#query ===========================================================
                mi_helper = self.mi_helper
                f_baseDistance = self.f_baseDistance  
                _irisSize = self.f_irisSize	
                log.info(f_baseDistance)
                log.info(_irisSize)		
            except Exception,error: raise Exception,"!Query]{%s}"%error

            try:#Curve creation ===========================================================		
                mi_crv = cgmMeta.asMeta( curves.createControlCurve('gear',
                                                                   direction = 'z+',
                                                                   size = _irisSize*.5,
                                                                   absoluteSize=False),'cgmObject',setClass=False)
                SNAP.go(mi_crv,mi_helper.mNode)
                mi_tmpGroup = cgmMeta.cgmObject( mi_crv.doGroup())
                mi_crv.__setattr__('t%s'%self.str_orientation[0],f_baseDistance * self._f_midMulti)
                mi_crv.parent = False
                mi_tmpGroup.delete()

            except Exception,error: raise Exception,"!Curve create]{%s}"%error

            try:#Tag,name, color ===========================================================
                mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
                mi_crv.addAttr('cgmType',attrType='string',value = 'settings',lock=True)
                mi_crv.doName()          	    

                #Color
                curves.setCurveColorByName(mi_crv.mNode,self.d_colors[self.str_direction][1]) 
            except Exception,error: raise Exception,"!Tag,name,color]{%s}"%error

            try:#connect ===========================================================
                self.mi_go.d_returnControls['settings'] = mi_crv.mNode
                self.mi_go.md_ReturnControls['settings'] = mi_crv
                self.mi_go._mi_rigNull.connectChildNode(mi_crv,'shape_settings','owner')
            except Exception,error: raise Exception,"!Connect]{%s}"%error

        def _buildEyeMove_(self):
            try:#query ===========================================================
                mi_helper = self.mi_helper
                f_baseDistance = self.f_baseDistance  
                f_size = distance.returnBoundingBoxSizeToAverage(mi_helper.irisHelper.mNode)
            except Exception,error: raise Exception,"!Query]{%s}"%error

            try:#Curve creation ===========================================================
                '''
		f_castDistance = distance.returnBoundingBoxSizeToAverage(mi_helper.mNode)
		str_crv = ShapeCast.createMeshSliceCurve(self.mi_go._targetMesh[0],mi_helper.mNode,
		                                          rotateBank = 30,curveDegree=3,posOffset = [0,0,self.mi_go.f_skinOffset/2],
		                                          maxDistance=f_castDistance,
		                                          points=8,returnDict = False,latheAxis=self.str_orientation[0],
		                                          aimAxis=self.str_orientation[0]+'+')
		mi_crv =  cgmMeta.cgmObject(str_crv,setClass=False)'''	
                #mi_crv =  cgmMeta.cgmObject(curves.createControlCurve('squareRounded',size = f_size * .5,direction=self.str_orientation[0]+'+'),setClass=False)	

                mi_loc = mi_helper.doLoc(fastMode = True)
                mi_tmpGroup = cgmMeta.cgmObject( mi_loc.doGroup())
                mi_loc.__setattr__('t%s'%self.str_orientation[0],f_baseDistance * 1.5)

                #Make a trace curve
                _str_trace = mc.curve (d=1, ep = [mi_helper.getPosition(),mi_loc.getPosition()], os=True)#build curves as we go to see what's up
                log.info(_str_trace)
                #l_curvesToCombine = [_str_trace,mi_crvBase.mNode]

                #>>>Combine the curves
                '''
		try:newCurve = curves.combineCurves(l_curvesToCombine) 
		except Exception,error:raise Exception,"!Failed to combine]{%s}"%error
		'''
                mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(mi_helper.mNode,False) )
                '''
		if mi_helper.getEnumValueString('direction') == 'right':#mirror control setup
		    self.log_info("mirroring EyeMove")
		    mi_crv.__setattr__("r%s"%self.str_orientation[2],180)'''

                try:curves.parentShapeInPlace(mi_crv.mNode,_str_trace)#Parent shape
                except Exception,error:raise Exception,"Parent shape in place fail | %s"%error

                mc.delete(_str_trace,mi_tmpGroup.mNode)		

            except Exception,error: raise Exception,"!Curve create]{%s}"%error

            try:#Tag,name, color ===========================================================
                mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
                mi_crv.addAttr('cgmType',attrType='string',value = 'eyeMove',lock=True)
                mi_crv.doName()          	    

                #Color
                curves.setCurveColorByName(mi_crv.mNode,self.d_colors[self.str_direction][1]) 
            except Exception,error: raise Exception,"!Tag,name,color]{%s}"%error

            try:#connect ===========================================================
                self.mi_go.d_returnControls['eyeMove'] = mi_crv.mNode
                self.mi_go.md_ReturnControls['eyeMove'] = mi_crv
                self.mi_go._mi_rigNull.connectChildNode(mi_crv,'shape_eyeMove','owner')
            except Exception,error: raise Exception,"!Connect]{%s}"%error

        def _buildIris_(self):
            try:#query ===========================================================
                mi_helper = self.mi_helper
                mi_irisCrv = self.mi_irisCrv
                _irisSize = self.f_irisSize
                _baseDistance = self.f_baseDistance  
                _baseIrisPos = self._baseIrisPos
            except Exception,error: raise Exception,"!Query]{%s}"%error
            
            try:#Curve creation ===========================================================
                ml_curvesToCombine = []
                try:
                    mi_tmpCrv = cgmMeta.asMeta( curves.createControlCurve('circle',
                                                                          direction = 'z+',
                                                                          size = _irisSize,
                                                                          absoluteSize=False),'cgmObject',setClass=False)
                except Exception,error: raise Exception,"Initial create | {0}".format(error)
                
                try:
                    SNAP.go(mi_tmpCrv,mi_irisCrv.mNode)
                    
                    mc.move(_baseIrisPos[0],_baseIrisPos[1],_baseIrisPos[2], mi_tmpCrv.mNode,  a = True)
                    mi_tmpGroup = cgmMeta.cgmObject( mi_tmpCrv.doGroup())
                    mi_tmpCrv.__setattr__('t%s'%self.str_orientation[0], .01)
                    ml_curvesToCombine.append(mi_tmpCrv.doDuplicate(parentOnly = False))
                    ml_curvesToCombine[-1].parent = False
                    
                    mi_tmpCrv.__setattr__('t%s'%self.str_orientation[0],-.01)
                    ml_curvesToCombine.append(mi_tmpCrv.doDuplicate(parentOnly = False))
                    ml_curvesToCombine[-1].parent = False
    
                    mi_tmpGroup.delete()
                except Exception,error: raise Exception,"Move | {0}".format(error)
                
                #>>>Combine the curves
                try:newCurve = curves.combineCurves([mObj.mNode for mObj in ml_curvesToCombine]) 
                except Exception,error:raise Exception,"!Failed to combine]{%s}"%error
                try:
                    mi_crv = cgmMeta.cgmObject(newCurve)
                except Exception,error: raise Exception,"New curve | {0}".format(error)
                
            except Exception,error: raise Exception,"!Curve create]{%s}"%error

            try:#Tag,name, color ===========================================================
                mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
                mi_crv.addAttr('cgmType',attrType='string',value = 'iris',lock=True)
                mi_crv.doName()          	    

                #Color
                curves.setCurveColorByName(mi_crv.mNode,self.d_colors[self.str_direction][0]) 
            except Exception,error: raise Exception,"!Tag,name,color]{%s}"%error

            try:#connect ===========================================================
                self.mi_go.d_returnControls['iris'] = mi_crv.mNode
                self.mi_go.md_ReturnControls['iris'] = mi_crv
                self.mi_go._mi_rigNull.connectChildNode(mi_crv,'shape_iris','owner')
            except Exception,error: raise Exception,"!Connect]{%s}"%error

        def _buildPupil_(self):
            try:#query ===========================================================
                mi_helper = self.mi_helper
                mi_pupilCrv = self.mi_pupilCrv
                _pupilSize = self.f_pupilSize
                _baseDistance = self.f_baseDistance  
                _baseIrisPos = self._baseIrisPos
            except Exception,error: raise Exception,"!Query]{%s}"%error

            try:#Curve creation ===========================================================
                ml_curvesToCombine = []
                mi_tmpCrv = cgmMeta.asMeta( curves.createControlCurve('circle',
                                                                      direction = 'z+',
                                                                      size = _pupilSize,
                                                                      absoluteSize=False),'cgmObject',setClass=False)
                SNAP.go(mi_tmpCrv,mi_pupilCrv.mNode)
                mc.move(_baseIrisPos[0],_baseIrisPos[1],_baseIrisPos[2], mi_tmpCrv.mNode,  a = True)
                mi_tmpGroup = cgmMeta.cgmObject( mi_tmpCrv.doGroup())
                mi_tmpCrv.__setattr__('t%s'%self.str_orientation[0], .01)
                ml_curvesToCombine.append(mi_tmpCrv.doDuplicate(parentOnly = False))
                ml_curvesToCombine[-1].parent = False

                mi_tmpCrv.__setattr__('t%s'%self.str_orientation[0],-.01)
                ml_curvesToCombine.append(mi_tmpCrv.doDuplicate(parentOnly = False))
                ml_curvesToCombine[-1].parent = False

                mi_tmpGroup.delete()

                #>>>Combine the curves
                try:newCurve = curves.combineCurves([mObj.mNode for mObj in ml_curvesToCombine]) 
                except Exception,error:raise Exception,"!Failed to combine]{%s}"%error

                #mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(mi_pupilCrv.mNode,False) )

                #try:curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
                #except Exception,error:raise Exception,"Parent shape in place fail | error: %s"%error

                #mc.delete(newCurve)
                mi_crv = cgmMeta.cgmObject(newCurve)
            except Exception,error: raise Exception,"!Curve create]{%s}"%error

            try:#Tag,name, color ===========================================================
                mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
                mi_crv.addAttr('cgmType',attrType='string',value = 'pupil',lock=True)
                mi_crv.doName()          	    

                #Color
                curves.setCurveColorByName(mi_crv.mNode,self.d_colors[self.str_direction][0]) 
            except Exception,error: raise Exception,"!Tag,name,color]{%s}"%error

            try:#connect ===========================================================
                self.mi_go.d_returnControls['pupil'] = mi_crv.mNode
                self.mi_go.md_ReturnControls['pupil'] = mi_crv
                self.mi_go._mi_rigNull.connectChildNode(mi_crv,'shape_pupil','owner')
            except Exception,error: raise Exception,"!Connect]{%s}"%error
        def _cleanUp_(self):
            self.mi_irisPosLoc.delete()
    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()

def shapeCast_eyelids(*args,**kws):
    class fncWrap(ShapeCasterFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = 'shapeCast_eyelids(%s)'%self.mi_module.p_nameShort
            self._b_autoProgressBar = 1
            self._b_reportTimes = 1
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},	
                                {'step':'Build Shapes','call':self._buildShapes_},
                                ]
            assert self.mi_module.mClass == 'cgmEyelids',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(self._str_funcName,self.mi_module.mClass)
            #The idea is to register the functions needed to be called
            #=================================================================
            if log.getEffectiveLevel() == 10:self.report()#If debug

        def _gatherInfo_(self): 
            '''	    
            try:ml_uprLidHandles = self._mi_rigNull.msgList_get('handleJoints_upr')
            except Exception,error:raise Exception,"Missing uprlid handleJoints | error: %s "%(error)
            try:ml_lwrLidHandles = self._mi_rigNull.msgList_getMessage('handleJoints_lwr')
            except Exception,error:raise Exception,"Missing lwrlid handleJoints | error: %s "%(error)  
            log.info("%s >>> ml_uprLidHandles : %s "%(_str_funcName,[mObj.mNode for mObj in ml_uprLidHandles]))	
            log.info("%s >>> ml_lwrLidHandles : %s"%(_str_funcName,[mObj.mNode for mObj in ml_lwrLidHandles]))		

            __baseDistance = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_uprLidHandles]) /2 
            log.info("%s >>> baseDistance : %s"%(_str_funcName,__baseDistance))	
            '''
            '''
	    self.str_orientation = self.mi_go.str_jointOrientation #Link
	    self.str_partName = self.mi_go.str_partName		    
	    self.str_direction = self.mi_go._direction
	    self.d_colors = {'left':metaUtils.getSettingsColors('left'),
	                     'right':metaUtils.getSettingsColors('right'),
	                     'center':metaUtils.getSettingsColors('center')}

	    #Orient info ------------------------------------------------------------------------------------------------
	    self.v_aimNegative = cgmValid.simpleAxis(self.str_orientation[0]+"-").p_vector
	    self.v_aim = cgmValid.simpleAxis(self.str_orientation[0]).p_vector	
	    self.v_up = cgmValid.simpleAxis(self.str_orientation[1]).p_vector	
	    '''
            #Find our helpers -------------------------------------------------------------------------------------------
            self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise Exception,"%s >>> No suitable helper found"%(_str_funcName)

            #>> Find our joint lists ===================================================================
            try:self.ml_uprLidHandles = self.mi_go._mi_rigNull.msgList_get('handleJoints_upr')
            except Exception,error:raise Exception,"Missing uprlid handleJoints | %s "%(error)
            try:self.ml_lwrLidHandles = self.mi_go._mi_rigNull.msgList_get('handleJoints_lwr')
            except Exception,error:raise Exception,"Missing lwrlid handleJoints | %s "%(error)  

            #>> calculate ------------------------------------------------------------------------
            #self.f_baseDistance = distance.returnCurveLength(self.mi_helper.lwrLidHelper.mNode) /4
            #_tmpScale = distance.returnBoundingBoxSize(self.mi_helper.pupilHelper.mNode)
            #self.f_baseDistance = (_tmpScale[0]+_tmpScale[1])/3
            self.f_baseDistance = ( distance.returnCurveDiameter(self.mi_helper.pupilHelper.mNode))/1

        def _buildShapes_(self):
            #query ===========================================================
            mi_go = self.mi_go
            mi_helper = self.mi_helper
            __baseDistance = self.f_baseDistance 
            ml_uprLidHandles = self.ml_uprLidHandles 
            ml_lwrLidHandles = self.ml_lwrLidHandles

            #Curve creation ===========================================================
            ml_handleCrvs = []
            for mObj in ml_uprLidHandles + ml_lwrLidHandles:
                try:
                    if mObj.getAttr('isSubControl') or mObj in [ml_uprLidHandles[0],ml_uprLidHandles[-1]]:
                        _size = __baseDistance * .6
                    else:_size = __baseDistance
                    mi_crv =  cgmMeta.asMeta(curves.createControlCurve('circle',size = _size,direction=mi_go.str_jointOrientation[0]+'+'),'cgmObject',setClass=False)	
                    SNAP.go(mi_crv,mObj.mNode)
                    str_grp = mi_crv.doGroup()
                    mi_crv.__setattr__("t%s"%mi_go.str_jointOrientation[0],__baseDistance*2)
                    mi_crv.parent = False
                    mc.delete(str_grp)

                    #>>Color curve		    		    
                    if mObj.getAttr('isSubControl'):
                        curves.setCurveColorByName(mi_crv.mNode,mi_go.l_moduleColors[1])  
                    else:curves.setCurveColorByName(mi_crv.mNode,mi_go.l_moduleColors[0])  
                    #>>Copy tags and name		    
                    mi_crv.doCopyNameTagsFromObject(mObj.mNode,ignore = ['cgmType'])
                    mi_crv.doName()
                    mi_crv.connectChildNode(mObj,'handleJoint','controlCurve')
                    ml_handleCrvs.append(mi_crv)
                    #>>Copy pivot
                    mi_crv.doCopyPivot(mObj.mNode)
                except Exception,error:
                    raise Exception,"(handle: '%s' | error: %s )"%(mObj.p_nameShort,error)  

            #connect ===========================================================
            mi_go.d_returnControls['l_handleCurves'] = [mObj.p_nameShort for mObj in ml_handleCrvs]
            mi_go.md_ReturnControls['ml_handleCurves'] = ml_handleCrvs
            mi_go._mi_rigNull.msgList_connect('handleCurves',ml_handleCrvs,'owner')

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()  

def shapeCast_eyeLook(*args,**kws):
    class fncWrap(ShapeCasterFunc):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = 'shapeCast_eyeLook(%s)'%self.mi_module.p_nameShort
            self._b_autoProgressBar = 1
            self._b_reportTimes = 1
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},	
                                {'step':'Build Shape','call':self._buildShapes_},
                                ]
            assert self.mi_module.mClass == 'cgmEyeball',"%s >>> Module is not type: 'cgmEyeball' | type is: '%s'"%(self._str_funcName,self.mi_module.mClass)
            #The idea is to register the functions needed to be called
            #=================================================================
            if log.getEffectiveLevel() == 10:self.report()#If debug

        def _gatherInfo_(self): 
            mi_go = self.mi_go

            #Find our helpers -------------------------------------------------------------------------------------------
            self.mi_helper = cgmMeta.validateObjArg(self.mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise Exception,"%s >>> No suitable helper found"%(_str_funcName)

            self.mi_parentModule = self.mi_module.moduleParent

            #>> calculate ------------------------------------------------------------------------
            self.f_baseDistance = distance.returnDistanceBetweenObjects(self.mi_helper.mNode, self.mi_helper.pupilHelper.mNode) 


        def _buildShapes_(self):
            try:#query ===========================================================
                mi_go = self.mi_go
                mi_helper = self.mi_helper
                __baseDistance = self.f_baseDistance 
                mi_parentModule = self.mi_parentModule
            except Exception,error: raise Exception,"[Query]{%s}"%error

            try:#Curve creation ===========================================================
                mi_crv = cgmMeta.asMeta( curves.createControlCurve('arrow4Fat',
                                                                   direction = 'z+',
                                                                   size = __baseDistance * 1.5,
                                                                   absoluteSize=False),'cgmObject',setClass=False)	    
                SNAP.go(mi_crv,mi_helper.mNode)
                mi_tmpGroup = cgmMeta.cgmObject( mi_crv.doGroup())
                mi_crv.__setattr__('t%s'%mi_go.str_jointOrientation[0],__baseDistance * 6)

                mi_crv.parent = False
                mi_tmpGroup.delete()

                mi_crv.__setattr__('t%s'%mi_go.str_jointOrientation[2],0)	
            except Exception,error: raise Exception,"[Curve create]{%s}"%error

            try:#>>Copy tags and name
                #mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
                mi_crv.addAttr('cgmName',attrType='string',value = mi_parentModule.cgmName,lock=True)	    	    
                mi_crv.addAttr('cgmTypeModifier',attrType='string',value = 'eyeLook',lock=True)
                mi_crv.doName()          	    

                #Color
                l_color = modules.returnSettingsData('colorCenter',True)
                curves.setCurveColorByName(mi_crv.mNode,l_color[0])    

            except Exception,error: raise Exception,"[Connect]{%s}"%error

            try:#connect ===========================================================
                mi_go._mi_rigNull.connectChildNode(mi_crv,'shape_eyeLook','owner')
                mi_go.d_returnControls['eyeLook'] = mi_crv.mNode
                mi_go.md_ReturnControls['eyeLook'] = mi_crv		
            except Exception,error: raise Exception,"[Connect]{%s}"%error

    #We wrap it so that it autoruns and returns
    return fncWrap(*args,**kws).go()  

def build_eyeLook(self):
    _str_funcName = "go.build_eyeLook(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)	
    time_func = time.clock() 		
    try:#we need to find an eye module/head module
        mi_helper = self._mi_module.helper
        _baseDistance = distance.returnDistanceBetweenObjects(mi_helper.mNode, mi_helper.pupilHelper.mNode)	    	    
        mi_crv = cgmMeta.asMeta( curves.createControlCurve('arrow4Fat',
                                                           direction = 'z+',
                                                           size = _baseDistance * 1.5,
                                                           absoluteSize=False),'cgmObject',setClass=False)	    
        SNAP.go(mi_crv,mi_helper.mNode)
        mi_tmpGroup = cgmMeta.cgmObject( mi_crv.doGroup())
        mi_crv.__setattr__('t%s'%self.str_jointOrientation[0],_baseDistance * 6)

        mi_crv.parent = False
        mi_tmpGroup.delete()

        #if self.str_partType == "eyeball":
        mi_crv.__setattr__('t%s'%self.str_jointOrientation[2],0)

    except Exception,error:
        log.error("%s >>> Find info | %s"%(_str_funcName,error) )

    try:    
        #>>Copy tags and name
        #mi_crv.doCopyNameTagsFromObject(mi_helper.mNode,ignore = ['cgmType','cgmTypeModifier'])
        mi_crv.addAttr('cgmName',attrType='string',value = self._mi_puppet.cgmName,lock=True)	    	    
        mi_crv.addAttr('cgmTypeModifier',attrType='string',value = 'eyeLook',lock=True)
        mi_crv.doName()          	    

        #Color
        l_color = modules.returnSettingsData('colorCenter',True)
        curves.setCurveColorByName(mi_crv.mNode,l_color[0])    
        self.d_returnControls['eyeLook'] = mi_crv.mNode
        self.md_ReturnControls['eyeLook'] = mi_crv
        self._mi_rigNull.connectChildNode(mi_crv,'shape_eyeLook','owner')

        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-time_func)) + "-"*75)         

    except Exception,error:
        log.error("%s >>> fail]{%s}"%(_str_funcName,error) )
        return False