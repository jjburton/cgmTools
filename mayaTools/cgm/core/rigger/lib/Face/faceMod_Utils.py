"""
------------------------------------------
cgm.core.rigger: Face.faceMod_Utils
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

mouthNose rig builder
================================================================
"""
__version__ = '0310214'

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
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.core.lib import meta_Utils as metaUtils

from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.rigger.lib import joint_Utils as jntUtils
from cgm.core.lib import nameTools
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.lib import rayCaster as rayCast
from cgm.core.lib import surface_Utils as surfUtils
from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (attributes,
                     deformers,
                     joints,
                     cgmMath,
                     skinning,
                     lists,
                     dictionary,
                     distance,
                     modules,
                     search,
                     curves,
                     )

#>>Warning -- ALL of these expect a face module funcCls self arg
def returnRebuiltCurveString(crv, int_spans = 5, rpo = 0):
    try:crv.mNode
    except:crv = cgmMeta.cgmObject(crv)
    return mc.rebuildCurve (crv.mNode, ch=0, rpo=rpo, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_spans, d=3, tol=0.001)[0]		

def attach_fromDict(self,d_build):
    """
    modes
    rigAttach -- attaches follicle with control loc attached
    handleAttach -- no control loc, just attach driver with constraint
    blendAttach -- creates two attach points and a blend between the two -- mainly for the main movers (mouth, nose, eyes)
    slideAttach -- control loc unattached, 
    """
    try:#>> Attach  =======================================================================================
	mi_go = self._go#Rig Go instance link
	str_skullPlate = self.str_skullPlate
	f_offsetOfUpLoc = self.f_offsetOfUpLoc

	for i,str_tag in enumerate(d_build.keys()):
	    try:
		ml_buffer = []
		md_buffer = get_mdSidesBufferFromTag(self,str_tag)
		l_skip = d_build[str_tag].get('skip') or []
		for str_key in md_buffer.iterkeys():
		    if str_key in l_skip:
			self.log_info("{0} Skipping attach: {1}".format(str_tag,str_key))
		    else:
			ml_buffer = md_buffer[str_key]
			int_len = len(ml_buffer)

			if d_build[str_tag].get(str_key):#if we have special instructions for a direction key...
			    d_buffer = d_build[str_tag][str_key]
			else:
			    d_buffer = d_build[str_tag]

			for ii,mObj in enumerate(ml_buffer):
			    try:
				try:
				    if d_buffer.get(ii):#if we have special instructions for a index key...
					self.log_info("%s | %s > Utilizing index key"%(str_tag,str_key))
					d_use = d_buffer[ii]
					#self.log_infoNestedDict('d_buffer')
				    else:d_use = d_buffer
				    self.d_buffer = d_use
    
				    _attachTo = d_use.get('attachTo') or d_build[str_tag].get('attachTo')
				    if _attachTo == None:_attachTo = str_skullPlate
				    _parentTo = d_use.get('parentTo') or False
				    str_mode = d_use.get('mode') or 'rigAttach'
				    str_base = mObj.getBaseName() or 'NONAMETAG'
				    b_connectFollicleOffset = d_buffer.get('connectFollicleOffset') or d_build[str_tag].get('connectFollicleOffset') or False 
				except Exception,error:raise Exception,"[Query | error: {0}]".format(error)					    

				try:#Status update ----------------------------------------------------------------------
				    str_message = "Attach : '%s' | mObj: '%s' | mode: '%s' | _attachTo: '%s' | parentTo: '%s' "%(str_tag,mObj.p_nameShort,str_mode, _attachTo,_parentTo)
				    self.log_info(str_message)
				    self.progressBar_set(status = str_message,progress = ii, maxValue= int_len)
				except Exception,error:raise Exception,"[Status Update | error: {0}]".format(error)					    

				if str_mode == 'rigAttach' and _attachTo:
				    if not mObj.getMessage('masterGroup'):
					raise ValueError,"'{0}' lacks a masterGroup. Use different attach method".format(mObj.p_nameShort)
				    try:#Attach
					d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                                targetSurface = _attachTo,
				                                                createControlLoc = True,
				                                                createUpLoc = True,
				                                                f_offset = f_offsetOfUpLoc,
				                                                orientation = mi_go._jointOrientation)
				    except Exception,error:raise Exception,"[Rig mode attach. |error: {0}]".format(error)
				    try:#>> Setup curve locs ------------------------------------------------------------------------------------------
					mi_controlLoc = d_return['controlLoc']
					mi_crvLoc = mi_controlLoc.doDuplicate(parentOnly=False)
					mi_crvLoc.addAttr('cgmTypeModifier','followAttach',lock=True)
					mi_crvLoc.doName()
					mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull
					d_return['followLoc'] = mi_crvLoc #Add the curve loc
					self.md_attachReturns[mObj] = d_return										
				    except Exception,error:raise Exception,"[Loc setup. |error: {0}]".format(error)
				    #self.log_info("%s mode attached!]{%s}"%(str_mode,mObj.p_nameShort))
				elif str_mode == 'pointAttach' and _attachTo:
				    try:#Attach
					d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                                targetSurface = _attachTo,
				                                                createControlLoc = False,
				                                                createUpLoc = False,
				                                                f_offset = f_offsetOfUpLoc,
				                                                pointAttach = True,
				                                                orientation = mi_go._jointOrientation)
					self.md_attachReturns[mObj] = d_return								
					
				    except Exception,error:raise Exception,"[Point attach. |error: {0}]".format(error)
				elif str_mode == 'handleAttach' and _attachTo:
				    try:
					d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                                targetSurface = _attachTo,
				                                                createControlLoc = False,
				                                                createUpLoc = True,	
				                                                parentToFollowGroup = False,
				                                                orientation = mi_go._jointOrientation)
					self.md_attachReturns[mObj] = d_return					
				    except Exception,error:raise Exception,"[{0} fail! | error: {1}]".format(str_mode,error)				    

				elif str_mode == 'blendHandleAttach' and _attachTo:
				    '''
				    This mode is for attaching to two surfaces
				    '''
				    try:#Blend attach ==================================================================================
					try:#Query ---------------------------------------------------------------------------------------
					    _target0 = d_use['target0'] #or self.md_rigList['stableJaw'][0]
					    _defaultValue = d_use.get('defaultValue') or None
					    _suffix = d_use.get('followSuffix') or 'Deformation'
					    _d = {'handle':mObj,
				                  'target0':_target0}
					    self.d_buffer = _d						
					    d_trackLocs = {'stable':{'attachTo':_target0},
				                           'def':{'attachTo':_attachTo},}

					except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)	

					try:#Build Tracklocs -----------------------------------------------------------------------------
					    for str_t in d_trackLocs.iterkeys():
						try:
						    d_sub = d_trackLocs[str_t]
						    mi_loc = mObj.doLoc()
						    mi_loc.addAttr('cgmTypeModifier',str_t)
						    mi_loc.doName()
						    str_tmp = '%s%sLoc'%(str_base,str_t.capitalize())
						    _d['%sLoc'%str_t] = mi_loc
						    mi_loc.parent = mi_go._i_rigNull#parent to rigNull
						    try:#Attach
							d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
						                                                targetSurface = d_sub.get('attachTo'),
						                                                createControlLoc = False,
						                                                createUpLoc = False,	
						                                                attachControlLoc = False,
							                                        f_offset = f_offsetOfUpLoc,							                                        
						                                                parentToFollowGroup = True,
						                                                orientation = mi_go._jointOrientation)
							self.md_attachReturns[mi_loc] = d_return								
						    except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)
						    self.log_info("'%s' created"%str_tmp)
						    self.md_rigList[str_tmp] = [mi_loc]
						    self.__dict__['mi_%s'%str_tmp] = mi_loc
						    mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						except Exception,error:raise Exception,"!'%s' loc setup! | %s"%(str_t,error)				
					except Exception,error:raise Exception,"[Track locs! | error: {0}]".format(error)	
					try:#Blend Setup -----------------------------------------------------------------------------
					    #Query
					    mi_handle = _d['handle']		    
					    mi_0Loc = _d['stableLoc']
					    mi_1Loc = _d['defLoc']
					    mi_stableDef = _d['target0']

					    if str_mode == 'blendStableAttach':
						try:#Constrain the stable loc to the face
						    mi_controlLoc = self.md_attachReturns[mi_0Loc]['controlLoc']
						    #mc.pointConstraint(mi_faceDef.mNode,mi_controlLoc.mNode,maintainOffset = True)
						    mi_controlLoc.parent = mi_stableDef
						except Exception,error:raise Exception,"[Stable loc controlLoc! | error: {0}]".format(error)

					    try:#Create constrain the handle master Group
						str_parentConstraint = mc.parentConstraint([mi_0Loc.mNode,mi_1Loc.mNode],mi_handle.masterGroup.mNode,
					                                                   maintainOffset = True)[0]
						mi_contraint = cgmMeta.cgmNode(str_parentConstraint) 
						mi_contraint.interpType = 0							
					    except Exception,error:raise Exception,"[Parent Constraint! | error: {0}]".format(error)

					    try:
						#EndBlend
						d_blendFollowReturn = NodeF.createSingleBlendNetwork([mi_handle.mNode,'follow%s'%_suffix.capitalize()],
					                                                             [mi_handle.mNode,'resultStableFollow'],
					                                                             [mi_handle.mNode,'resultDefFollow'],
					                                                             keyable=True)
						l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
						#Connect                                  
						d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
						d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
						d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
						d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True	
						if _defaultValue is not None:
						    d_blendFollowReturn['d_driver']['mi_plug'].p_defaultValue = _defaultValue
						    d_blendFollowReturn['d_driver']['mi_plug'].value = _defaultValue
					    except Exception,error:raise Exception,"[Blend! | error: {0}]".format(error)

					except Exception,error:
					    #self.log_infoNestedDict('d_buffer')
					    raise StandardError,"!Setup follow loc blend!|!] | error: {0}".format(error)
				    except Exception,error:raise Exception,"[{0} fail! | error: {1}]".format(str_mode,error)				    
				elif str_mode == 'blendStableAttach' and _attachTo:
				    try:#Blend attach ==================================================================================
					try:#Query ---------------------------------------------------------------------------------------
					    _target0 = d_use.get('target0') or self.md_rigList['stableJaw'][0]
					    _d = {'handle':mObj,
				                  'target0':_target0}
					    self.d_buffer = _d
					    _defaultValue = d_use.get('defaultValue') or None
					    _suffix = d_use.get('followSuffix') or 'Deformation'
					except Exception,error:raise Exception,"[Query! | {0}]".format(error)

					try:#Build Tracklocs -----------------------------------------------------------------------------
					    d_trackLocs = {'stable':{'attachControlLoc':False,'parentToFollowGroup':False},
				                           'def':{'attachControlLoc':True,'parentToFollowGroup':True}}
					    for str_t in d_trackLocs.iterkeys():
						try:
						    d_sub = d_trackLocs[str_t]
						    mi_loc = mObj.doLoc()
						    mi_loc.addAttr('cgmTypeModifier',str_t)
						    mi_loc.doName()
						    str_tmp = '%s%sLoc'%(str_base,str_t.capitalize())
						    _d['%sLoc'%str_t] = mi_loc
						    mi_loc.parent = mi_go._i_rigNull#parent to rigNull			    
						    try:#Attach
							d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
						                                                targetSurface = _attachTo,
						                                                createControlLoc = True,
						                                                createUpLoc = False,	
							                                        f_offset = f_offsetOfUpLoc,							                                        
						                                                attachControlLoc = d_sub.get('attachControlLoc'),
						                                                parentToFollowGroup = d_sub.get('parentToFollowGroup'),
						                                                orientation = mi_go._jointOrientation)
							self.md_attachReturns[mi_loc] = d_return								
						    except Exception,error:raise Exception,"[Attach! | {0}]".format(error)

						    self.log_info("'%s' created"%str_tmp)

						    self.md_rigList[str_tmp] = [mi_loc]
						    self.__dict__['mi_%s'%str_tmp] = mi_loc
						    mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						except Exception,error:raise Exception,"!'%s' loc setup! | %s"%(str_t,error)				
					except Exception,error:raise Exception,"[Track locs! | {0}]".format(error)	
					try:#Blend Setup -----------------------------------------------------------------------------
					    #Query
					    mi_handle = _d['handle']		    
					    mi_stableLoc = _d['stableLoc']
					    mi_defLoc = _d['defLoc']
					    mi_stableDef = _d['target0']

					    try:#Constrain the stable loc to the face
						mi_controlLoc = self.md_attachReturns[mi_stableLoc]['controlLoc']
						#mc.pointConstraint(mi_faceDef.mNode,mi_controlLoc.mNode,maintainOffset = True)
						mi_controlLoc.parent = mi_stableDef
					    except Exception,error:raise Exception,"!Stable loc controlLoc! | %s"%(error)

					    try:#Create constrain the handle master Group
						str_parentConstraint = mc.parentConstraint([mi_stableLoc.mNode,mi_defLoc.mNode],mi_handle.masterGroup.mNode,
					                                                   maintainOffset = True)[0]
						mi_contraint = cgmMeta.cgmNode(str_parentConstraint) 
						mi_contraint.interpType = 0						
					    except Exception,error:raise Exception,"!Parent Constraint! | %s"%(error)

					    try:
						#EndBlend
						d_blendFollowReturn = NodeF.createSingleBlendNetwork([mi_handle.mNode,'follow%s'%_suffix.capitalize()],
					                                                             [mi_handle.mNode,'resultStableFollow'],
					                                                             [mi_handle.mNode,'resultDefFollow'],
					                                                             keyable=True)
						l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
						#Connect                                  
						d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
						d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
						d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
						d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True	
						if _defaultValue is not None:
						    d_blendFollowReturn['d_driver']['mi_plug'].p_defaultValue = _defaultValue
						    d_blendFollowReturn['d_driver']['mi_plug'].value = _defaultValue
					    except Exception,error:raise Exception,"[Blend! | {0}]".format(error)

					except Exception,error:
					    #self.log_infoNestedDict('d_buffer')
					    raise StandardError,"!Setup follow loc blend!|!]{%s}"%(error)
				    except Exception,error:raise Exception,"[{0} fail! | error: {1}]".format(str_mode,error)				    
				elif str_mode == 'blendAttach' and _attachTo:
				    try:#Blend attach ==================================================================================
					try:#Query ---------------------------------------------------------------------------------------
					    try:
						_ml_drivers = d_use.get('drivers') or d_build[str_tag][str_key].get('drivers') or False
						if not cgmValid.isListArg(_ml_drivers):raise ValueError,"blend attach drivers must be list"
						if len(_ml_drivers)!=2:raise ValueError,"blend attach drivers must be len 2"
					    except Exception,error:raise Exception,"[Drivers! | error: {0}]".format(error)	

					    try:
						_mControlObj = d_use.get('controlObj') or mObj
					    except Exception,error:raise Exception,"[controlObj! | error: {0}]".format(error)	

					    _d = {'handle':mObj,}
					    self.d_buffer = _d

					    _defaultValue = d_use.get('defaultValue') or None
					    _suffix = d_use.get('followSuffix') or 'Deformation'
					    if not cgmValid.isListArg(_attachTo):raise ValueError,"blend attach attachTo must be list"
					    if len(_attachTo)!=2:raise ValueError,"blend attach attachTo must be len 2"
					except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)	

					try:#Build Tracklocs -----------------------------------------------------------------------------
					    for i in range(2):
						try:
						    str_t = 'targ{0}'.format(i)
						    mi_loc = mObj.doLoc()
						    mi_loc.addAttr('cgmTypeModifier',str_t)
						    mi_loc.doName()
						    str_tmp = '%s%sLoc'%(str_base,str_t.capitalize())
						    _d['{0}Loc'.format(str_t)] = mi_loc
						    mi_loc.parent = mi_go._i_rigNull#parent to rigNull
						    try:#Attach
							d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
						                                                targetSurface = _attachTo[i],
						                                                createControlLoc = True,
						                                                createUpLoc = False,	
						                                                attachControlLoc = False,
							                                        f_offset = f_offsetOfUpLoc,							                                        
						                                                parentToFollowGroup = True,
						                                                orientation = mi_go._jointOrientation)							    
							self.md_attachReturns[mi_loc] = d_return								
						    except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)

						    self.log_info("'%s' created"%str_tmp)
						    self.md_rigList[str_tmp] = [mi_loc]
						    self.__dict__['mi_%s'%str_tmp] = mi_loc
						    mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						except Exception,error:raise Exception,"!'%s' loc setup! | %s"%(str_t,error)				
					except Exception,error:raise Exception,"[Track locs! | error: {0}]".format(error)	
					try:#Blend Setup -----------------------------------------------------------------------------
					    try:#Query
						mi_handle = _d['handle']		    
						mi_targ0Loc = _d['targ0Loc']
						mi_targ1Loc = _d['targ1Loc']
						mi_targ0Driver = self.md_attachReturns[mi_targ0Loc]['controlLoc']
						mi_targ1Driver = self.md_attachReturns[mi_targ1Loc]['controlLoc']
					    except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)	

					    try:#Constrain the stable loc to the face
						mi_targ0Driver.parent = _ml_drivers[0]
						mi_targ1Driver.parent = _ml_drivers[1]
					    except Exception,error:raise Exception,"[Stable loc controlLoc! | error: {0}]".format(error)

					    try:#Create constrain the handle master Group
						str_parentConstraint = mc.parentConstraint([mi_targ0Loc.mNode,mi_targ1Loc.mNode],mi_handle.masterGroup.mNode,
					                                                   maintainOffset = True)[0]
						mi_contraint = cgmMeta.cgmNode(str_parentConstraint) 
						mi_contraint.interpType = 0							
					    except Exception,error:raise Exception,"[Parent Constraint! | error: {0}]".format(error)

					    try:
						#EndBlend
						d_blendFollowReturn = NodeF.createSingleBlendNetwork([_mControlObj.mNode,'follow%s'%_suffix.capitalize()],
					                                                             [_mControlObj.mNode,'resultTarg0Follow'],
					                                                             [_mControlObj.mNode,'resultTarg1Follow'],
					                                                             keyable=True)
						l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
						#Connect                                  
						d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
						d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
						d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
						d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True	
						if _defaultValue is not None:
						    d_blendFollowReturn['d_driver']['mi_plug'].p_defaultValue = _defaultValue
						    d_blendFollowReturn['d_driver']['mi_plug'].value = _defaultValue
					    except Exception,error:raise Exception,"[Blend! | error: {0}]".format(error)

					except Exception,error:
					    #self.log_infoNestedDict('d_buffer')
					    raise StandardError,"!Setup follow loc blend!|!] | error: {0}".format(error)

					try:#connectFollicleOffset ==================================================================================
					    if b_connectFollicleOffset:
						for mi_loc in mi_targ0Loc,mi_targ1Loc:
						    mi_follicleOffsetGroup = self.md_attachReturns[mi_loc]['offsetGroup']
						    for attr in mi_go._jointOrientation[0]:
							attributes.doConnectAttr ((_mControlObj.mNode+'.t%s'%attr),(mi_follicleOffsetGroup.mNode+'.t%s'%attr))						    

					except Exception,error:raise Exception,"[Connect Follicle Offset! | error: {0}]".format(error)					    
				    except Exception,error:raise Exception,"[{0} fail! | error: {1}]".format(str_mode,error)				    
				elif str_mode == 'blendAttachStable' and _attachTo:
				    try:#Blend attach ==================================================================================
					try:#Query ---------------------------------------------------------------------------------------
					    _target0 = d_use.get('target0') or self.md_rigList['stableJaw'][0]
					    _mControlObj = d_use.get('controlObj') or mObj
					    _d = {'handle':mObj,
				                  'target0':_target0}
					    self.d_buffer = _d
					    _defaultValue = d_use.get('defaultValue') or None
					    _suffix = d_use.get('followSuffix') or 'Deformation'
					except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)	

					try:#Build Tracklocs -----------------------------------------------------------------------------
					    d_trackLocs = {'stable':{'attachControlLoc':False,'parentToFollowGroup':False},
				                           'def':{'attachControlLoc':True,'parentToFollowGroup':True}}
					    for i,str_t in enumerate(d_trackLocs.keys()):
						try:
						    d_sub = d_trackLocs[str_t]
						    mi_loc = mObj.doLoc()
						    mi_loc.addAttr('cgmTypeModifier',str_t)
						    mi_loc.doName()
						    str_tmp = '%s%sLoc'%(str_base,str_t.capitalize())
						    _d['%sLoc'%str_t] = mi_loc
						    if str_t == 'def':
							mi_loc.parent = mi_go._i_rigNull#parent to rigNull			    
							try:#Attach
							    d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
						                                                    targetSurface = _attachTo,
						                                                    createControlLoc = True,
						                                                    createUpLoc = False,
							                                            f_offset = f_offsetOfUpLoc,							                                            
						                                                    attachControlLoc = d_sub.get('attachControlLoc'),
						                                                    parentToFollowGroup = d_sub.get('parentToFollowGroup'),
						                                                    orientation = mi_go._jointOrientation)
							    self.md_attachReturns[mi_loc] = d_return								
							except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)

						    self.log_info("'%s' created"%str_tmp)

						    self.md_rigList[str_tmp] = [mi_loc]
						    self.__dict__['mi_%s'%str_tmp] = mi_loc
						    mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						except Exception,error:raise Exception,"!'%s' loc setup! | %s"%(str_t,error)				
					except Exception,error:raise Exception,"[Track locs! | error: {0}]".format(error)	
					try:#Blend Setup -----------------------------------------------------------------------------
					    #Query
					    mi_handle = _d['handle']		    
					    mi_stableLoc = _d['stableLoc']
					    mi_defLoc = _d['defLoc']
					    mi_stableDef = _d['target0']

					    try:#Constrain the stable loc to the face
						#mi_controlLoc = self.md_attachReturns[mi_stableLoc]['controlLoc']
						#mc.pointConstraint(mi_faceDef.mNode,mi_controlLoc.mNode,maintainOffset = True)
						#mi_controlLoc.parent = mi_stableDef
						mi_stableLoc.parent = mi_stableDef
					    except Exception,error:raise Exception,"[Stable loc controlLoc! | error: {0}]".format(error)

					    try:#Create constrain the handle master Group
						str_parentConstraint = mc.parentConstraint([mi_stableLoc.mNode,mi_defLoc.mNode],mi_handle.masterGroup.mNode,
					                                                   maintainOffset = True)[0]
						mi_contraint = cgmMeta.cgmNode(str_parentConstraint) 
						mi_contraint.interpType = 0							
					    except Exception,error:raise Exception,"[Parent Constraint! | error: {0}]".format(error)

					    try:
						#EndBlend
						d_blendFollowReturn = NodeF.createSingleBlendNetwork([_mControlObj.mNode,'follow%s'%_suffix.capitalize()],
					                                                             [_mControlObj.mNode,'resultStableFollow'],
					                                                             [_mControlObj.mNode,'resultDefFollow'],
					                                                             keyable=True)
						l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
						#Connect                                  
						d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
						d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
						d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
						d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True	
						if _defaultValue is not None:
						    d_blendFollowReturn['d_driver']['mi_plug'].p_defaultValue = _defaultValue
						    d_blendFollowReturn['d_driver']['mi_plug'].value = _defaultValue
					    except Exception,error:raise Exception,"[Blend! | error: {0}]".format(error)

					except Exception,error:
					    #self.log_infoNestedDict('d_buffer')
					    raise StandardError,"!Setup follow loc blend!|!] | error: {0}".format(error)
				    except Exception,error:raise Exception,"[{0} fail! | error: {1}]".format(str_mode,error)				    
				elif str_mode == 'slideAttach' and _attachTo:
				    try:
					d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                                targetSurface = _attachTo,
				                                                createControlLoc = True,
				                                                createUpLoc = True,	
				                                                attachControlLoc = False,
				                                                f_offset = f_offsetOfUpLoc,					                                        
				                                                parentToFollowGroup = False,
				                                                orientation = mi_go._jointOrientation)
					self.md_attachReturns[mObj] = d_return					
				    except Exception,error:raise Exception,"[{0} fail! | error: {1}]".format(str_mode,error)
				elif str_mode == 'slideHandleAttach' and _attachTo:
				    '''
				    Drive a handle position with offset
				    '''
				    try:
					d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                                targetSurface = _attachTo,
				                                                createControlLoc = True,
				                                                createUpLoc = True,	
				                                                attachControlLoc = True,
				                                                f_offset = f_offsetOfUpLoc,					                                        
				                                                parentToFollowGroup = False,
				                                                orientation = mi_go._jointOrientation)
					self.md_attachReturns[mObj] = d_return					
				    except Exception,error:raise Exception,"[{0} fail! | error: {1}]".format(str_mode,error)
				elif str_mode == 'slidePointAttach' and _attachTo:
				    '''
				    Drive a handle position with offset
				    '''
				    try:
					d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                                targetSurface = _attachTo,
				                                                createControlLoc = True,
				                                                createUpLoc = True,	
				                                                attachControlLoc = True,
				                                                f_offset = f_offsetOfUpLoc,					                                        
				                                                pointAttach = True,                                                                                        
				                                                parentToFollowGroup = False,
				                                                orientation = mi_go._jointOrientation)
					self.md_attachReturns[mObj] = d_return					
				    except Exception,error:raise Exception,"[{0} fail! | error: {1}]".format(str_mode,error)
				elif str_mode == 'parentOnly':
				    try:mObj.masterGroup.parent = _parentTo
				    except Exception,error:raise Exception,"[parentTo. | error: {0}]".format(error)		    
				    #self.log_info("%s parented!]{%s}"%(str_mode,mObj.p_nameShort))
				else:
				    raise NotImplementedError,"mode: %s "%str_mode
			    except Exception,error:  raise StandardError,"attaching: {0} | {1}".format(mObj,error)				
	    except Exception,error:  raise StandardError,"'{0}' | {1}".format(str_tag,error)			    
    except Exception,error:  raise StandardError,"[attach_fromDict |error: {0}]".format(error)	

def create_segmentfromDict(self,d_build):
    '''
    Handler for building segments from dicsts

    Modes:

    Flags
    'index'(int) -- root dict flag to specify only using a certain index of a list
    'skip'(string) -- skip one of the side flags - 'left','right','center'
    '''
    try:#>> Connect  =======================================================================================
	mi_go = self._go#Rig Go instance link
	mPlug_multpHeadScale = mi_go.mPlug_multpHeadScale

	for str_tag in d_build.iterkeys():
	    try:
		md_buffer = {}
		ml_buffer = []
		buffer = self.md_rigList[str_tag]
		if type(buffer) == dict:
		    for str_side in ['left','right','center']:
			bfr_side = buffer.get(str_side)
			if bfr_side:
			    md_buffer[str_side] = bfr_side
		else:
		    md_buffer['reg'] = buffer 
		'''
		d_build = {'uprLipSegment':{'orientation':mi_go._jointOrientation,
		    'left':{'mi_curve':mi_uprDrivenCrv},
		    'right':{'mi_curve':self.mi_uprLipDrivenReverseCrv}}}
		'''
		int_len = len(md_buffer.keys())
		for i,str_key in enumerate(md_buffer.iterkeys()):
		    if d_build[str_tag].get(str_key):#if we have special instructions for a direction key...
			d_buffer = d_build[str_tag][str_key]
		    else:
			d_buffer = d_build[str_tag]	
		    ml_buffer = md_buffer[str_key]
		    int_len = len(ml_buffer)

		    try:#Gather data ----------------------------------------------------------------------
			str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'default'
			str_orientation = d_buffer.get('orientation') or d_build[str_tag].get('orientation') or 'zyx' 
			mi_curve =  d_buffer.get('mi_curve') or d_build[str_tag].get('mi_curve') or None
			if mi_curve:str_curve = mi_curve.p_nameShort
			else:str_curve = None
			str_baseName = "{0}{1}".format(str_tag,str_key.capitalize())
		    except Exception,error:raise Exception,"[Data gather!] | error: {0}".format(error)	

		    try:#Status update ----------------------------------------------------------------------
			str_message = "Create Segment : '%s' %s | curve: '%s' | mode: '%s' "%(str_tag,str_key,str_curve,str_mode)
			self.log_info(str_message)
			self.progressBar_set(status = (str_message),progress = i, maxValue = int_len)	
		    except Exception,error:raise Exception,"[Status update] | error: {0}".format(error)	

		    if str_mode == 'default':
			d_segReturn = rUtils.createSegmentCurve(ml_buffer, addMidTwist = False,useCurve = mi_curve, baseName = str_baseName,
		                                                moduleInstance = mi_go._mi_module, connectBy = 'trans')
		    else:
			raise NotImplementedError,"not implemented : mode: %s"%_str_mode

		    try:#>> Store stuff ========================================================================
			'''
			d_return = {'mi_segmentCurve':mi_segmentCurve,'segmentCurve':mi_segmentCurve.mNode,'mi_ikHandle':mi_IK_Handle,'mi_segmentGroup':mi_grp,
			'l_driverJoints':self.l_driverJoints,'ml_driverJoints':ml_driverJoints,
			'scaleBuffer':mi_jntScaleBufferNode.mNode,'mi_scaleBuffer':mi_jntScaleBufferNode,'mPlug_extendTwist':self.mPlug_factorInfluenceIn,
			'l_drivenJoints':self.l_joints,'ml_drivenJoints':ml_joints}
			'''
			d_segReturn['mi_segmentGroup'].parent = mi_go._i_rigNull
			mi_curve = d_segReturn['mi_segmentCurve']
			self.md_rigList[str_tag]['{0}SegmentCurve'.format(str_key)] = mi_curve
			mi_curve.parent = mi_go._i_rigNull
			mi_go._i_rigNull.msgList_append(mi_curve,'segmentCurves','rigNull')
			self.md_attachReturns[mi_curve] = d_segReturn
			d_segReturn['ml_driverJoints'][0].parent = mi_go._i_faceDeformNull
			#d_segReturn['ml_driverJoints'][0].parent = self.md_rigList['faceBaseDef'][0]	
			d_segReturn['ml_drivenJoints'][0].parent = mi_go._i_faceDeformNull
			mi_go.connect_toRigGutsVis(d_segReturn['ml_drivenJoints'],vis = True)#connect to guts vis switches										
			mi_go.connect_toRigGutsVis(d_segReturn['ml_driverJoints'],vis = True)#connect to guts vis switches										
			
			#for mJnt in d_segReturn['ml_driverJoints'][0],d_segReturn['ml_drivenJoints'][0]:
			    #mJnt.parent = mi_go._i_faceDeformNull
		    except Exception,error:
			self.log_infoDict(d_segReturn,'{0} Seg Return'.format(str_tag))
			raise StandardError,"[Return processing | error: {0}]".format(error)	

		    try:#>>>Connect master scale =======================================================================================
			mi_distanceBuffer = mi_curve.scaleBuffer		
			cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn(mPlug_multpHeadScale.p_combinedShortName)    
		    except Exception,error:raise Exception,"[segment scale connect! | error: {0}]".format(error)				
	    except Exception,error:raise Exception,"[{0} | error: {1}]".format(str_tag,error)			    
    except Exception,error:raise Exception,"[create_segmentfromDict] | error: {0}".format(error)	

def connect_fromDict(self,d_build):
    '''
    handler for connecting stuff to handles,curves,surfaces or whatever
    Modes:
    rigToHandle -- given a nameRig kw, it looks through the data sets to find the handle and connect. One to one connection type
    rigToFollow --
    pointBlend -- 
    simpleSlideHandle
    rigToFollow
    parentConstraint
    pointConstraint
    offsetConnect
    
    Flags
    'index'(int) -- root dict flag to specify only using a certain index of a list
    'skip'(string) -- skip one of the side flags - 'left','right','center'
    '''
    try:#>> Connect  =======================================================================================
	mi_go = self._go#Rig Go instance link
	str_skullPlate = self.str_skullPlate
	f_offsetOfUpLoc = self.f_offsetOfUpLoc

	for str_tag in d_build.iterkeys():
	    try:
		ml_buffer = []
		md_buffer = get_mdSidesBufferFromTag(self,str_tag)

		l_skip = d_build[str_tag].get('skip') or []
		for str_key in md_buffer.iterkeys():
		    if str_key in l_skip:
			self.log_info("{0} Skipping connect: {1}".format(str_tag,str_key))
		    else:
			if d_build[str_tag].get(str_key):#if we have special instructions for a direction key...
			    d_buffer = d_build[str_tag][str_key]
			else:
			    d_buffer = d_build[str_tag]	
			ml_buffer = md_buffer[str_key]
			try:
			    int_indexBuffer = d_build[str_tag].get('index') or False
			    if int_indexBuffer is not False:
				self.log_info("%s | %s > Utilizing index call"%(str_tag,str_key))					
				ml_buffer = [ml_buffer[int_indexBuffer]]
			except Exception,error:raise Exception,"[Index call(%s)!| error: {0}]".format(error)

			int_len = len(ml_buffer)
			for i,mObj in enumerate(ml_buffer):
			    str_mObj = mObj.p_nameShort
			    try:#Gather data ----------------------------------------------------------------------
				if d_buffer.get(i):#if we have special instructions for a index key...
				    self.log_info("%s | %s > Utilizing index key"%(str_tag,str_key))
				    d_use = d_buffer[i]
				else:
				    d_use = d_buffer
				    
				str_mode = d_use.get('mode') or d_build[str_tag].get('mode') or 'rigToHandle'
				b_rewireFollicleOffset = d_use.get('rewireFollicleOffset') or d_build[str_tag].get('rewireFollicleOffset') or False 
				b_rewireFollicleOffsetRotate = d_use.get('rewireFollicleOffsetRotate') or d_build[str_tag].get('rewireFollicleOffsetRotate') or False 
				ml_driver = d_use.get('driver') or d_build[str_tag].get('driver')  or False
			    except Exception,error:raise Exception,"[Data gather!] | error: {0}".format(error)

			    try:#Status update ----------------------------------------------------------------------
				str_message = "Connecting : '%s' %s > '%s' | mode: '%s' | rewireFollicleOffset: %s"%(str_tag,str_key,str_mObj,str_mode,b_rewireFollicleOffset)
				self.log_info(str_message)
				self.progressBar_set(status = (str_message),progress = i, maxValue = int_len)	
			    except Exception,error:raise Exception,"[Status update] | error: {0}".format(error)		
			    if str_mode == 'skip':
				continue
			    elif str_mode == 'rigToSegment':
				try:
				    mi_target = mObj.skinJoint.segJoint
				    mc.pointConstraint(mi_target.mNode,mObj.masterGroup.mNode,maintainOffset = True)
				except Exception,error:raise Exception,"[Failed!] | error: {0}".format(error)
			    elif str_mode == 'simpleSlideHandle':
				try:
				    try:#See if we have a handle return
					if ml_driver: ml_handles = cgmValid.listArg(ml_driver)
					else:					
					    ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
					mi_handle = ml_handles[0]
				    except Exception,error:raise Exception,"[Query!] | error: {0}".format(error)

				    try:#Connect the control loc to the center handle
					mi_controlLoc = self.md_attachReturns[mObj]['controlLoc']
					cgmMeta.cgmAttr(mi_controlLoc,'translate').doConnectIn("{0}.translate".format(mi_handle.mNode))						
					cgmMeta.cgmAttr(mi_controlLoc,'rotate').doConnectIn("{0}.rotate".format(mi_handle.mNode))

				    except Exception,error:raise Exception,"[Control loc connect!]%error: {0}]".format(error)

				except Exception,error:raise Exception,"[{0}! | {1}]".format(str_mode,error)				    
			    elif str_mode == 'rigToHandle':
				try:
				    try:#See if we have a handle return
					if ml_driver: ml_handles = cgmValid.listArg(ml_driver)
					else:					
					    ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
					if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
					mi_handle = ml_handles[0]
				    except Exception,error:raise Exception,"[Query!] | error: {0}".format(error)

				    try:#Connect the control loc to the center handle
					mi_controlLoc = self.md_attachReturns[mObj]['controlLoc']
					mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode,maintainOffset = 1)
				    except Exception,error:raise Exception,"[Control loc connect!]%error: {0}]".format(error)

				    try:#Setup the offset to push handle rotation to the rig joint control
					#Create offsetgroup for the mid
					mi_offsetGroup = mi_go.verify_offsetGroup(mObj)	 	    
					cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
				    except Exception,error:raise Exception,"[Offset group!] | error: {0}".format(error)
				except Exception,error:raise Exception,"[{0}! | {1}]".format(str_mode,error)	
			    elif str_mode == 'toConnectedMsg':
				try:
				    try:#See if we have a handle return
					str_msgTag = d_use.get('messageTag') or d_build[str_tag].get('messageTag') or False
					if not str_msgTag:raise ValueError,"No message tag found"
					
					str_handle = mObj.getMessage(str_msgTag)
					log.info(str_handle)
					if not str_handle:raise ValueError,"No message on {0} found".format(str_msgTag)
					else: str_handle = str_handle[0]
				    except Exception,error:raise Exception,"[Query!] | error: {0}".format(error)

				    try:#Connect the control loc to the center handle
					mi_controlLoc = self.md_attachReturns[mObj]['controlLoc']
					mc.pointConstraint(str_handle,mi_controlLoc.mNode,maintainOffset = 1)
				    except Exception,error:raise Exception,"[Control loc connect!]%error: {0}]".format(error)

				    try:#Setup the offset to push handle rotation to the rig joint control
					#Create offsetgroup for the mid
					mi_offsetGroup = mi_go.verify_offsetGroup(mObj)	 	    
					cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(str_handle))
				    except Exception,error:raise Exception,"[Offset group!] | error: {0}".format(error)
				except Exception,error:raise Exception,"[{0}! | {1}]".format(str_mode,error)	
			    elif str_mode == 'rigToFollow':
				try:
				    try:#See if we have a handle return
					mi_attachTo = d_use['attachTo']
					d_current = self.md_attachReturns[mObj]
					mi_followLoc = d_current['followLoc']
					mi_controlLoc = d_current['controlLoc']					    
				    except Exception,error:raise Exception,"[Query '%s'!]{%s}"%(str_key,error)

				    try:#>> Attach  loc  --------------------------------------------------------------------------------------
					if mi_attachTo.getMayaType() == 'nurbsCurve':
					    crvUtils.attachObjToCurve(mi_followLoc.mNode,mi_attachTo.mNode)
					else:
					    d_return = surfUtils.attachObjToSurface(objToAttach = mi_followLoc,
				                                                    targetSurface = mi_attachTo.mNode,
				                                                    createControlLoc = False,
				                                                    createUpLoc = True,	
				                                                    parentToFollowGroup = False,
				                                                    orientation = mi_go._jointOrientation)
					    self.md_attachReturns[mi_followLoc] = d_return
					mc.pointConstraint(mi_followLoc.mNode,mi_controlLoc.mNode,maintainOffset = True)

				    except Exception,error:raise Exception,"[Failed to attach to crv.] | error: {0}".format(error)					    					    
				    '''
				    try:#>> Attach  loc to curve --------------------------------------------------------------------------------------
				    mi_crvLoc = d_current['crvLoc']
				    mi_controlLoc = d_current['controlLoc']
				    crvUtils.attachObjToCurve(mi_crvLoc.mNode,mi_crv.mNode)
				    mc.pointConstraint(mi_crvLoc.mNode,mi_controlLoc.mNode,maintainOffset = True)
	    
				    except Exception,error:raise Exception,"Failed to attach to crv. | ] | error: {0}".format(error)
				    try:#>> Aim the offset group  ------------------------------------------------------------------------------------------
				    if obj_idx != int_lastIndex:
					str_upLoc = d_current['upLoc'].mNode
					str_offsetGroup = d_current['offsetGroup'].mNode				    
					if obj_idx == 0:
					#If it's the interior brow, we need to aim forward and back on the chain
					#We need to make a couple of locs
					d_tomake = {'aimIn':{'target':str_centerBrowRigJoint,
						     'aimVector':cgmMath.multiplyLists([v_aim,[-1,-1,-1]])},
						'aimOut':{'target':ml_rigJoints[1].mNode,
						      'aimVector':v_aim}}
					for d in d_tomake.keys():
					    d_sub = d_tomake[d]
					    str_target = d_sub['target']
					    mi_loc = mObj.doLoc()
					    mi_loc.addAttr('cgmTypeModifier',d,lock=True)
					    mi_loc.doName()
					    mi_loc.parent = d_current['zeroGroup']
					    d_sub['aimLoc'] = mi_loc
					    v_aimVector = d_sub['aimVector']
					    if str_side == 'right':
					    v_aimVector = cgmMath.multiplyLists([v_aimVector,[-1,-1,-1]])
					    mc.aimConstraint(str_target,mi_loc.mNode,
						     maintainOffset = True,
						     weight = 1,
						     aimVector = v_aimVector, upVector = v_up,
						     worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )
					mc.orientConstraint([d_tomake['aimIn']['aimLoc'].mNode, d_tomake['aimOut']['aimLoc'].mNode],str_offsetGroup,maintainOffset = True)					
					else:
					ml_targets = [ml_rigJoints[obj_idx+1]]	
					mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup,
						 maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
				    except Exception,error:raise Exception,"Loc setup. | ] | error: {0}".format(error)
				    '''
				except Exception,error:raise Exception,"[%s!]{%s}"%(str_mode,error)					    				    
			    elif str_mode == 'pointBlend':
				try:
				    try:#See if we have a handle return
					ml_targets = d_use['targets']
					d_current = self.md_attachReturns[mObj]
					#mi_followLoc = d_current['followLoc']
					mi_controlLoc = d_current['controlLoc']					    
				    except Exception,error:raise Exception,"[Query '%s'!]{%s}"%(str_key,error)

				    try:#>> Attach  loc  --------------------------------------------------------------------------------------
					mc.pointConstraint([mObj.mNode for mObj in ml_targets],mi_controlLoc.mNode,maintainOffset = True)
				    except Exception,error:raise Exception,"Failed to attach to crv. | ] | error: {0}".format(error)	
				except Exception,error:raise Exception,"[%s!]{%s}"%(str_mode,error)					    
			    elif str_mode == 'parentConstraint':
				try:
				    try:#See if we have a handle return
					ml_targets = d_use['targets']
					d_current = self.md_attachReturns[mObj]
					#mi_followLoc = d_current['followLoc']
					mi_controlLoc = d_current['controlLoc']					    
				    except Exception,error:raise Exception,"[Query '%s'!]{%s}"%(str_key,error)
				    try:#>> Attach  loc  --------------------------------------------------------------------------------------
					mc.parentConstraint([mObj.mNode for mObj in ml_targets],mi_controlLoc.mNode,maintainOffset = True)
				    except Exception,error:raise Exception,"Failed to attach to crv. | ] | error: {0}".format(error)	
				except Exception,error:raise Exception,"[%s!]{%s}"%(str_mode,error)	
			    elif str_mode == 'pointConstraint':
				try:
				    try:#See if we have a handle return
					ml_targets = d_use['targets']
					d_current = self.md_attachReturns[mObj]
					mi_controlLoc = d_current['controlLoc']					    
				    except Exception,error:raise Exception,"[Query {0}!| error: {1}]".format(str_key,error)
				    try:#>> Attach  loc  --------------------------------------------------------------------------------------
					mc.pointConstraint([mObj.mNode for mObj in ml_targets],mi_controlLoc.mNode,maintainOffset = True)
				    except Exception,error:raise Exception,"Failed to constrain. | error: {0}]".format(error)	
				except Exception,error:raise Exception,"[{0}!| error: {1}".format(str_mode,error)
			    elif str_mode == 'offsetConnect':
				try:
				    try:#See if we have a handle return
					if ml_driver: ml_handles = cgmValid.listArg(ml_driver)
					else:					
					    ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
					if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
					mi_handle = ml_handles[0]
				    except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)

				    try:#Setup the offset to push handle rotation to the rig joint control
					#Create offsetgroup for the mid
					mi_offsetGroup = mi_go.verify_offsetGroup(mObj)	 	    
    
					cgmMeta.cgmAttr(mi_offsetGroup,'translate').doConnectIn("%s.translate"%(mi_handle.mNode))						
				    except Exception,error:raise Exception,"[Offset group!] | error: {0}".format(error)

				except Exception,error:raise Exception,"[0}!| error: {1}".format(str_mode,error)

			    elif str_mode in ['attrOffsetConnect','attrOffsetFactorConnect','smileHandleOffset']:
				try:
				    try:#See if we have a handle return
					if ml_driver: ml_handles = cgmValid.listArg(ml_driver)
					else:ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
					if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
					mi_handle = ml_handles[0]
					l_attrsToConnect = d_use.get('attrsToConnect') or d_build[str_tag].get('attrsToConnect') or ['tx','ty','tz']
					l_attrsToMirror = d_use.get('attrsToMirror') or d_build[str_tag].get('attrsToMirror') or []
					self.log_info("{0} | attrOffsetConnect | driver: {1} | attrsToConnect: {2} | attrsToMirror: {3}".format(str_mObj,ml_driver,l_attrsToConnect,l_attrsToMirror))
					
					try:mi_offsetGroup = mi_go.verify_offsetGroup(mObj)#..Create offsetgroup
					except Exception,error:raise Exception,"[offset verify fail! | error: {0}]".format(error)
				    except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)

				    try:#Setup the offset to push handle rotation to the rig joint control 
					for ii,a in enumerate(l_attrsToConnect):
					    mPlug_attrBridgeDriven = cgmMeta.cgmAttr(mi_offsetGroup,a)
					    mPlug_attrBridgeDriver = cgmMeta.cgmAttr(mi_handle,l_attrsToConnect[0])  
						    
					    if str_mode == 'attrOffsetConnect':
						if a not in l_attrsToMirror:
						    cgmMeta.cgmAttr(mi_offsetGroup,a).doConnectIn("{0}.{1}".format(mi_handle.mNode,a))
						else:
						    arg_attributeBridge = "{0} = -{1}".format(mPlug_attrBridgeDriven.p_combinedShortName,
						                                              mPlug_attrBridgeDriver.p_combinedShortName)						
						    NodeF.argsToNodes(arg_attributeBridge).doBuild()
					    elif str_mode == 'attrOffsetFactorConnect':
						str_attr = d_use.get('attrName') or d_build[str_tag].get('attrName') or 'push'
						mPlug_factor = cgmMeta.cgmAttr(mObj,str_attr, attrType = 'float', value = .75, hidden = False, defaultValue = .75)
						l_args = []
						
						if a not in l_attrsToMirror:
						    arg_factor = "{0} = {1} * {2}".format(mPlug_attrBridgeDriven.p_combinedShortName,
						                                          mPlug_factor.p_combinedShortName,
						                                          mPlug_attrBridgeDriver.p_combinedShortName)
						else:
						    arg_factor = "{0} = {1} * -{2}".format(mPlug_attrBridgeDriven.p_combinedShortName,
						                                          mPlug_factor.p_combinedShortName,
						                                          mPlug_attrBridgeDriver.p_combinedShortName)					
						NodeF.argsToNodes(arg_factor).doBuild()						

					    elif str_mode == 'smileHandleOffset':
						mPlug_smileAttrDriver = cgmMeta.cgmAttr(mi_handle,"t{0}".format(mi_go._jointOrientation[2]) )  					    
						mPlug_mouthMoveDriver = cgmMeta.cgmAttr(self.md_rigList['mouthMove'][0],'tz')						
						try:
						    mPlug_smileTarget = cgmMeta.cgmAttr(mObj,'cornerOutTarget',attrType='float',value = 2.0,hidden = False,defaultValue = 2.0)
						    
						    mPlug_smileOn = cgmMeta.cgmAttr(mObj,'res_smileOn',attrType='float',value = 0.0, keyable=False, hidden=True)                                                            
						    mPlug_smileClamped = cgmMeta.cgmAttr(mObj,'res_smileDriverClamp',attrType='float',value = 0.0, keyable=False, hidden=True)							
						    mPlug_smileValueResult = cgmMeta.cgmAttr(mObj,'res_smileValueOut',attrType='float',value = 0.0, keyable=False, hidden=True)							
						    
						    arg_smileOn = "{0} = if {1} >= 0: {2} else 0".format(mPlug_smileOn.p_combinedShortName,
						                                                         mPlug_smileAttrDriver.p_combinedShortName,
						                                                         mPlug_smileValueResult.p_combinedShortName)							    
						    
						    arg_smileDriverClamp = "{0} = clamp(0,{1},{2})".format(mPlug_smileClamped.p_combinedShortName,
						                                                           mPlug_smileTarget.p_combinedShortName,
						                                                           mPlug_smileAttrDriver.p_combinedShortName)
						    
						    arg_smileFactor = "{0} = {2} / {1}".format(mPlug_smileValueResult.p_combinedShortName,
						                                               mPlug_smileTarget.p_combinedShortName,
						                                               mPlug_smileClamped.p_combinedShortName)						    
						    #l_nodalArgs.append(arg_smileOn,arg_smileDriverClamp,arg_smileFactor)
						    for str_arg in arg_smileOn,arg_smileDriverClamp,arg_smileFactor:
							self.log_info("Building: {0}".format(str_arg))
							NodeF.argsToNodes(str_arg).doBuild()							    
						except Exception,error:raise Exception,"[smile driver! | {0}]".format(error)	
												
						if ii == 0:
						    mPlug_negateFactor = cgmMeta.cgmAttr(mObj,'negateCornerOut',attrType='float',value = -.2,hidden = False,defaultValue=-.2)
						    mPlug_negateResult = cgmMeta.cgmAttr(mObj,'res_negateCornerOut',attrType='float',value = 0.0, keyable=False, hidden=True)
						    
						    arg_negateFactor = "{0} = {1} * {2}".format(mPlug_negateResult.p_combinedShortName,
					                                                        mPlug_negateFactor.p_combinedShortName,
					                                                        mPlug_attrBridgeDriver.p_combinedShortName)
						    arg_negateOutOn = "{0} = {1} * {2}".format(mPlug_attrBridgeDriven.p_combinedShortName,
					                                                       mPlug_smileOn.p_combinedShortName,
					                                                       mPlug_negateResult.p_combinedShortName)   
						    
						    for str_arg in arg_negateFactor,arg_negateOutOn,arg_smileOn:
							self.log_info("Building: {0}".format(str_arg))
							NodeF.argsToNodes(str_arg).doBuild()	
						elif ii == 1:
						    try:#>> Main handle...
							mPlug_outFactor = cgmMeta.cgmAttr(mObj,'cornerPushMax',attrType='float',value = 1.5,hidden = False,defaultValue = 1.5)
							#mPlug_outMouthMoveInfluence = cgmMeta.cgmAttr(mObj,'mouthMoveFactor',attrType='float',value = .5,hidden = False)
							
							mPlug_outUseResult = cgmMeta.cgmAttr(mObj,'res_cornerPushUse',attrType='float',value = 0.0, keyable=False, hidden=True)
							#mPlug_outMouthMoveResult = cgmMeta.cgmAttr(mObj,'res_mouthMoveValue',attrType='float',value = 0.0, keyable=False, hidden=True)
							mPlug_outResult = cgmMeta.cgmAttr(mObj,'res_out',attrType='float',value = 0.0, keyable=False, hidden=True)
							#mPlug_sumResult = cgmMeta.cgmAttr(mObj,'res_sumFinal',attrType='float',value = 0.0, keyable=False, hidden=True)
					
							if mObj.cgmDirection == 'left':
							    arg_outFactorValue = "{0} = {1} * {2}".format(mPlug_outUseResult.p_combinedShortName,
								                                          mPlug_smileOn.p_combinedShortName,
								                                          mPlug_outFactor.p_combinedShortName) 
							    #arg_outMouthMoveValue = "{0} = {1} * {2}".format(mPlug_outMouthMoveResult.p_combinedShortName,
								#                                             mPlug_mouthMoveDriver.p_combinedShortName,
								#                                             mPlug_outMouthMoveInfluence.p_combinedShortName)
							else:
							    arg_outFactorValue = "{0} = {1} * -{2}".format(mPlug_outUseResult.p_combinedShortName,
								                                           mPlug_smileOn.p_combinedShortName,
								                                           mPlug_outFactor.p_combinedShortName) 
							    #arg_outMouthMoveValue = "{0} = {1} * -{2}".format(mPlug_outMouthMoveResult.p_combinedShortName,
								#                                              mPlug_mouthMoveDriver.p_combinedShortName,
								#                                              mPlug_outMouthMoveInfluence.p_combinedShortName)								
													
							
							#This was the same name as the above
							#arg_sum = "{0} = {1} + {2}".format(mPlug_sumResult.p_combinedShortName,
							#                                   mPlug_outMouthMoveResult.p_combinedShortName,
							#                                   mPlug_outResult.p_combinedShortName)
							
							arg_negateOutOn = "{0} = {1} * {2}".format(mPlug_outResult.p_combinedShortName,
							                                           mPlug_smileOn.p_combinedShortName,
							                                           mPlug_outUseResult.p_combinedShortName)
							
							mPlug_outResult.doConnectOut(mPlug_attrBridgeDriven.p_combinedShortName)
							
							for str_arg in arg_outFactorValue,arg_negateOutOn:
							    self.log_info("Building: {0}".format(str_arg))
							    NodeF.argsToNodes(str_arg).doBuild()
						    except Exception,error:raise Exception,"[smileHandleOffset!] | error: {0}".format(error)
						    
						    try:#>> smileHandleRotate...
							mPlug_rotateCheekVolume = cgmMeta.cgmAttr(mObj,'cheekVolumeMax',attrType='float',value = 5,hidden = False,defaultValue = 5)
							mPlug_attrRotateDriven = cgmMeta.cgmAttr(mi_offsetGroup,"r{0}".format(mi_go._jointOrientation[1]))   
							
							if mObj.cgmDirection == 'left':
							    arg_rotateOut = "{0} = {1} * -{2}".format(mPlug_attrRotateDriven.p_combinedShortName,
								                                     mPlug_rotateCheekVolume.p_combinedShortName,
								                                     mPlug_smileOn.p_combinedShortName)	
							else:
							    arg_rotateOut = "{0} = {1} * {2}".format(mPlug_attrRotateDriven.p_combinedShortName,
							                                              mPlug_rotateCheekVolume.p_combinedShortName,
							                                              mPlug_smileOn.p_combinedShortName)													      										
						
							for str_arg in [arg_rotateOut]:
							    self.log_info("Building: {0}".format(str_arg))
							    NodeF.argsToNodes(str_arg).doBuild()							
						    except Exception,error:raise Exception,"[smileHandleRotate!] | error: {0}".format(error)
						    
						    try:#>> uprSmileHandle...
							mi_uprHandle = self.md_rigList['uprSmileHandle'][str_key][0]
							try:mi_uprOffsetGroup = mi_go.verify_offsetGroup(mi_uprHandle)#..Create offsetgroup
							except Exception,error:raise Exception,"[offset verify fail! | error: {0}]".format(error)
							
							mPlug_attrBridgeUprDriven = cgmMeta.cgmAttr(mi_uprOffsetGroup,a)   
							
							mPlug_uprPushFactor = cgmMeta.cgmAttr(mi_uprHandle,'pushFactor',attrType='float',value = .5,hidden = False,defaultValue = .5)
							mPlug_uprOutResult = cgmMeta.cgmAttr(mi_uprHandle,'res_out',attrType='float',value = 0.0, keyable=False, hidden=True)
							
							arg_uprOut = "{0} = {1} * {2}".format(mPlug_attrBridgeUprDriven.p_combinedShortName,
							                                      mPlug_outResult.p_combinedShortName,
							                                      mPlug_uprPushFactor.p_combinedShortName)							
							for str_arg in [arg_uprOut]:
							    self.log_info("Building: {0}".format(str_arg))
							    NodeF.argsToNodes(str_arg).doBuild()							
						    except Exception,error:raise Exception,"[uprSmileHandle!] | error: {0}".format(error)
						else:self.log_warning("[Not sure what to do with {0} | mode: {1}]".format(a,str_mode))
				    except Exception,error:raise Exception,"[Setup!] | error: {0}".format(error)

				except Exception,error:raise Exception,"[{0}! | {1}]".format(str_mode,error)					     				
			    else:
				raise NotImplementedError,"not implemented : mode: {0}".format(str_mode)
			    
			    #Rewire stuff
			    try:#rewireFollicleOffset
				if b_rewireFollicleOffset:
				    mi_rewireHandle = d_use.get('rewireHandle') or d_build[str_tag].get('rewireHandle') or mi_handle
				    try:mi_follicleOffsetGroup = d_current['offsetGroup']
				    except Exception,error:raise ValueError,"Failed to find attach return for: {0} | {1}".format(str_mObj,error)
				    for attr in mi_go._jointOrientation[0]:
					attributes.doConnectAttr ((mi_rewireHandle.mNode+'.t%s'%attr),(mi_follicleOffsetGroup.mNode+'.t%s'%attr))						     
			    except Exception,error:raise Exception,"[rewire Follicle Offset! | error: {0}]".format(error)

			    try:#rewireFollicleOffset
				if b_rewireFollicleOffsetRotate:
				    mi_rewireHandle = d_use.get('rewireHandle') or d_build[str_tag].get('rewireHandle') or mi_handle
				    try:mi_follicleOffsetGroup = d_current['offsetGroup']
				    except Exception,error:raise ValueError,"Failed to find attach return for: {0} | {1}".format(str_mObj,error)
				    cgmMeta.cgmAttr(mi_follicleOffsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_rewireHandle.mNode))
			    except Exception,error:raise Exception,"[rewire Follicle Offset rotate! | error: {0}]".format(error)
	    except Exception,error:  raise StandardError,"[{0} | error: {1}]".format(str_tag,error)			    
    except Exception,error:  raise StandardError,"[connect_fromDict] | error: {0}".format(error)	

def get_mdSidesBufferFromTag(self,str_tag):
    '''
    Process a dict against to a md_rigList
    '''
    md_buffer = {}
    buffer = self.md_rigList[str_tag]
    if type(buffer) == dict:
	for str_side in ['left','right','center']:
	    bfr_side = buffer.get(str_side)
	    if bfr_side:
		md_buffer[str_side] = bfr_side
    else:
	md_buffer['reg'] = buffer
    return md_buffer

def create_influenceJoints(self,d_build):
    '''
    Create influence joints from objects in the md_rigList
    
    :parameters:
	parentToHandle | whether to parent the influence joint's offset group to the handle
    '''
    try:#>> Infuence joints  =======================================================================================
	mi_go = self._go#Rig Go instance link
	str_skullPlate = self.str_skullPlate

	for str_tag in d_build.iterkeys():
	    try:
		ml_buffer = []
		md_buffer = get_mdSidesBufferFromTag(self,str_tag)

		l_skip = d_build[str_tag].get('skip') or []

		str_newTag = '{0}InfluenceJoints'.format(str_tag)
		self.md_rigList[str_newTag] = {}#...start new dict	

		for str_side in md_buffer.iterkeys():
		    if str_side in l_skip:
			self.log_info("%s Skipping aim: %s"%(str_tag,str_side))
		    else:
			try:
			    if d_build[str_tag].get(str_side):#if we have special instructions for a direction key...
				d_buffer = d_build[str_tag][str_side]
			    else:
				d_buffer = d_build[str_tag]	
			    ml_buffer = md_buffer[str_side]

			    try:
				int_indexBuffer = d_build[str_tag].get('index') or False
				if int_indexBuffer is not False:
				    self.log_info("%s | %s > Utilizing index call"%(str_tag,str_side))					
				    ml_buffer = [ml_buffer[int_indexBuffer]]
			    except Exception,error:raise Exception,"[Index call!| error: {0}]".format(error)
			    
			    try:
				int_len = len(ml_buffer)
				_d = {}
				self.d_buffer = _d
				int_len = len(ml_buffer)			    
				ml_influenceJoints = []	
				b_parentToHandle = d_buffer.get('parentToHandle') or d_build[str_tag].get('parentToHandle') or False 

			    except Exception,error:raise Exception,"[Query | error: {0}]".format(error)					    
			    		    
			    for idx,mJnt in enumerate(ml_buffer):
				str_mObj = mJnt.p_nameShort

				try:#Status update ----------------------------------------------------------------------
				    str_message = "Creating influence joint : '{0}' {1} > '{2}'".format(str_tag,str_side,str_mObj)
				    self.log_info(str_message)
				    self.progressBar_set(status = (str_message),progress = idx, maxValue = int_len)	
				except Exception,error:raise Exception,"[Status update] | error: {0}".format(error)	

				try:#Create----------------------------------------------------------------------
				    #mi_influenceJoint = cgmMeta.cgmNode( mc.joint()).convertMClassType('cgmObject')
				    mi_influenceJoint = cgmMeta.cgmObject( mc.joint(),setClass = True)
				    Snap.go(mi_influenceJoint,mJnt.mNode,orient=True)
				    mi_influenceJoint.rotateOrder = mJnt.rotateOrder
				    mi_influenceJoint.doCopyNameTagsFromObject(mJnt.mNode,ignore=['cgmType'])	
				    mi_influenceJoint.addAttr('cgmTypeModifier','influence',lock=True)
				    mi_influenceJoint.doName()
				    mJnt.connectChildNode(mi_influenceJoint,'influenceJoint','sourceJoint')
				    ml_influenceJoints.append(mi_influenceJoint)
				    mi_influenceJoint.parent = mi_go._i_deformNull	
				    
				except Exception,error:raise Exception,"[influence joint for '{0}'! | error: {1}]".format(str_mObj,error)				    

				try:#Create offsetgroup for the mid
				    mi_offsetGroup = cgmMeta.asMeta( mi_influenceJoint.doGroup(True),'cgmObject',setClass=True)	 
				    mi_offsetGroup.doStore('cgmName',mi_influenceJoint)
				    mi_offsetGroup.addAttr('cgmTypeModifier','master',lock=True)
				    mi_offsetGroup.doName()
				    mi_influenceJoint.connectChildNode(mi_offsetGroup,'masterGroup','groupChild')
				    
				    if b_parentToHandle:
					mi_offsetGroup.parent = mJnt
				except Exception,error:raise Exception,"[masterGroup for '{0}'! | error: {1}]".format(str_mObj,error)				    
			    
			    jntUtils.metaFreezeJointOrientation(ml_influenceJoints)
			    mi_go.connect_toRigGutsVis(ml_influenceJoints, vis = True)#connect to guts vis switches
			    self.md_rigList[str_newTag][str_side] = ml_influenceJoints#...store
			except Exception,error:raise Exception,"[side: {0} | error: {1}]".format(str_side,error)			     
	    except Exception,error:
		try:self.log_infoNestedDict('d_buffer')
		except:pass
		raise Exception,"[tag: {0} | error: {1}]".format(str_tag,error)			    
    except Exception,error: raise Exception,"[create_influenceJoint] | error: {0}".format(error)
    
def create_specialLocsFromDict(self,d_build):
    '''
    '''
    try:#>> Infuence joints  =======================================================================================
	mi_go = self._go#Rig Go instance link

	for str_tag in d_build.iterkeys():
	    try:
		ml_buffer = []
		md_buffer = get_mdSidesBufferFromTag(self,str_tag)

		l_skip = d_build[str_tag].get('skip') or []

		for str_side in md_buffer.iterkeys():
		    if str_side in l_skip:
			self.log_info("{0} Skipping loc creation: {1}".format(str_tag,str_side))
		    else:
			try:
			    if d_build[str_tag].get(str_side):#if we have special instructions for a direction key...
				d_buffer = d_build[str_tag][str_side]
			    else:
				d_buffer = d_build[str_tag]	
			    ml_buffer = md_buffer[str_side]

			    try:
				int_indexBuffer = d_build[str_tag].get('index') or False
				if int_indexBuffer is not False:
				    self.log_info("{0} | {1} > Utilizing index call".format(str_tag,str_side))					
				    ml_buffer = [ml_buffer[int_indexBuffer]]
			    except Exception,error:raise Exception,"[Index call!| error: {0}]".format(error)
			    
			    int_len = len(ml_buffer)
			    _d = {}
			    self.d_buffer = _d
			    int_len = len(ml_buffer)	
			    
			    b_storeCreatedToRigList = d_buffer.get('storeCreatedToRigList') or d_build[str_tag].get('storeCreatedToRigList') or False 
			    
			    str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'No idea'			    			    
			    str_tagPlusMode = "{0}_{1}".format(str_tag,str_mode)
			    if b_storeCreatedToRigList:
				if not self.md_rigList.get(str_tagPlusMode):#if we don't have an entry...
				    self.md_rigList[str_tagPlusMode] = {}#..add it
				if not self.md_rigList[str_tagPlusMode].get(str_side):#If we don't have the side..
				    self.md_rigList[str_tagPlusMode][str_side] = []#..add it
				__l_storeBack = self.md_rigList[str_tagPlusMode][str_side]#..buffer
			    for idx,mJnt in enumerate(ml_buffer):
				str_mObj = mJnt.p_nameShort
				f_dist = d_buffer.get('offsetDist') or d_build[str_tag].get('offsetDist') or 100

				try:#Status update ----------------------------------------------------------------------
				    str_message = "Creating special loc joint : '{0}' {1} > '{2}' | mode: {3}".format(str_tag,str_side,str_mObj, str_mode)
				    self.log_info(str_message)
				    self.progressBar_set(status = (str_message),progress = idx, maxValue = int_len)	
				except Exception,error:raise Exception,"[Status update] | error: {0}".format(error)	
				
				try:#>> Standard stuff
				    mi_loc = mJnt.doLoc()
				    mi_loc.parent = mJnt
				    
				    mi_loc.doStore('cgmName',str_mObj)
				    mi_loc.addAttr('cgmTypeModifier',str_mode,lock=True)
				    mi_loc.doName()   
				    
				    mi_go.connect_toRigGutsVis(mi_loc, vis = True)#...connect to guts vis switches
				    mJnt.connectChildNode(mi_loc,str_mode,'source')#...store
				    
				    if b_storeCreatedToRigList: __l_storeBack.append(mi_loc)
				    
				except Exception,error:raise Exception,"[Standard stuff] | error: {0}".format(error)	
				
				if str_mode == 'handleAimOut':
				    if str_side == 'left':#...offset
					setattr(mi_loc,"t{0}".format(mi_go._jointOrientation[0]),f_dist)
				    else:
					setattr(mi_loc,"t{0}".format(mi_go._jointOrientation[0]),-f_dist)

				elif str_mode == 'surfTrackLoc':	
				    mi_loc.parent = mi_go._i_rigNull
				    mi_masterGroup = (cgmMeta.asMeta(mi_loc.doGroup(True),'cgmObject',setClass=True))
				    mi_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
				    mi_masterGroup.doName()
				    mi_loc.connectChildNode(mi_masterGroup,'masterGroup','groupChild')
				    
				    mi_masterGroup.parent = mi_go._i_rigNull
				else:
				    raise NotImplementedError,"Don't know this mode"
			except Exception,error:raise Exception,"[side: {0} | error: {1}]".format(str_side,error)			     
	    except Exception,error:
		try:self.log_infoNestedDict('d_buffer')
		except:pass
		raise Exception,"[tag: {0} | error: {1}]".format(str_tag,error)			    
    except Exception,error: raise Exception,"[create_specialLocsFromDict] | error: {0}".format(error)
    
def constrain_fromDict(self,d_build):
    '''
    handler for constraining bits

    Modes:
    lipLineBlend -- special lip line mode
    singleTarget -- aims at a single target
    segmentSingleAim -- aim one to the next. last aims at second to last
    segmentStartAim -- all aim back to first, first aims at second

    Flags
    'index'(int) -- root dict flag to specify only using a certain index of a list
    'skip'(string) -- skip one of the side flags - 'left','right','center'
    '''
    try:#>> constrain  =======================================================================================
	mi_go = self._go#Rig Go instance link

	for str_tag in d_build.iterkeys():
	    ml_buffer = []
	    md_buffer = get_mdSidesBufferFromTag(self,str_tag)
	    d = {}
	    l_skip = d_build[str_tag].get('skip') or []
	    for str_side in md_buffer.iterkeys():
		try:
		    if str_side in l_skip:
			self.log_info("{0} Skipping aim: {1}".format(str_tag,str_side))
		    else:
			try:
			    if d_build[str_tag].has_key(str_side):#if we have special instructions for a direction key...
				d_buffer = d_build[str_tag][str_side]
				self.log_warning("{0} using side dict".format(str_side))
			    else:
				d_buffer = d_build[str_tag]	
			    ml_buffer = md_buffer[str_side]

			    try:
				int_indexBuffer = d_build[str_tag].get('index') or False
				if int_indexBuffer is not False:
				    self.log_info("%s | %s > Utilizing index call"%(str_tag,str_side))					
				    ml_buffer = [ml_buffer[int_indexBuffer]]
			    except Exception,error:raise Exception,"[Index call!| error: {0}]".format(error)
			    int_len = len(ml_buffer)
			    _d = {}
			    self.d_buffer = _d
			    int_last = len(ml_buffer)-1	
			except Exception,error:raise Exception,"[Side data query! | error: {0}]".format(error)

			for idx,mObj in enumerate(ml_buffer):
			    try:#Gather data ----------------------------------------------------------------------
				if d_buffer.get(idx):#if we have special instructions for a index key...
				    self.log_info("%s | %s > Utilizing index key"%(str_tag,str_key))
				    d_use = d_buffer[idx]
				else:
				    d_use = d_buffer
				
				str_mObj = mObj.p_nameShort
				mi_masterGroup = mObj.masterGroup				
				str_mode = d_use.get('mode') or d_build[str_tag].get('mode') or 'point'
				ml_targets = d_use.get('targets') or d_build[str_tag].get('targets') or False
			    except Exception,error:raise Exception,"[Data gather!] | error: {0}".format(error)
			    
			    try:#Status update ----------------------------------------------------------------------
				str_message = "Constraining : '{0}' {1} > '{2}'".format(str_tag,str_side,str_mObj)
				self.log_info(str_message)
				self.progressBar_set(status = (str_message),progress = idx, maxValue = int_len)	
			    except Exception,error:raise Exception,"[Status update] | error: {0}".format(error)	


			    if str_mode == 'point':#This is pretty much just for the lip rig line for now
				self.log_info("Side: '{0}' | idx: %s | Aiming :'{1}' | to:'{2}' ".format(str_side,idx,str_mObj,[mTarget.mNode for mTarget in ml_targets]))					
				try:
				    mc.pointConstraint([mTarget.mNode for mTarget in ml_targets], mi_masterGroup.mNode,
				                       weight = 1, maintainOffset = True)
				except Exception,error:raise Exception,"[constraint! | error: {0}]".format(error)						
			    else:
				raise NotImplementedError,"Mode not implemented : '{0}'".format(str_mode)
		except Exception,error: raise Exception,"['{0}' '{1}' fail] | error: {2}".format(str_tag, str_side,error)
    except Exception,error: raise Exception,"[constrain_fromDict] | error: {0}".format(error)
    
def aim_fromDict(self,d_build):
    '''
    handler for aiming stuff to handles,curves,surfaces or whatever

    Modes:
    lipLineBlend -- special lip line mode
    singleTarget -- aims at a single target
    segmentSingleAim -- aim one to the next. last aims at second to last
    segmentStartAim -- all aim back to first, first aims at second

    Flags
    'index'(int) -- root dict flag to specify only using a certain index of a list
    'skip'(string) -- skip one of the side flags - 'left','right','center'
    '''
    try:#>> Aim  =======================================================================================
	mi_go = self._go#Rig Go instance link
	str_skullPlate = self.str_skullPlate

	for str_tag in d_build.iterkeys():
	    ml_buffer = []
	    md_buffer = get_mdSidesBufferFromTag(self,str_tag)
	    d = {}
	    l_skip = d_build[str_tag].get('skip') or []
	    for str_side in md_buffer.iterkeys():
		try:
		    if str_side in l_skip:
			self.log_info("{0} Skipping aim: {1}".format(str_tag,str_side))
		    else:
			try:
			    if d_build[str_tag].has_key(str_side):#if we have special instructions for a direction key...
				d_buffer = d_build[str_tag][str_side]
				self.log_warning("{0} using side dict".format(str_side))
			    else:
				d_buffer = d_build[str_tag]	
			    ml_buffer = md_buffer[str_side]

			    try:
				int_indexBuffer = d_build[str_tag].get('index') or False
				if int_indexBuffer is not False:
				    self.log_info("%s | %s > Utilizing index call"%(str_tag,str_side))					
				    ml_buffer = [ml_buffer[int_indexBuffer]]
			    except Exception,error:raise Exception,"[Index call!| error: {0}]".format(error)
			    int_len = len(ml_buffer)
			    _d = {}
			    self.d_buffer = _d
			    int_last = len(ml_buffer)-1	
			    try:#Vectors
				if str_side == 'right':
				    v_aimIn = mi_go._vectorOut
				    v_aimOut = mi_go._vectorOutNegative	
				    ml_buffer = copy.copy(ml_buffer)
				    ml_buffer.reverse()
				    v_up = mi_go._vectorUp
				else:
				    v_aimIn = mi_go._vectorOutNegative
				    v_aimOut = mi_go._vectorOut	
				    v_up = mi_go._vectorUp

				_d['v_aimIn'] = v_aimIn
				_d['v_aimOut'] = v_aimOut
				_d['v_up'] = v_up										
			    except Exception,error:raise Exception,"[Vector query!| error: {0}]".format(error)

			except Exception,error:raise Exception,"[Side data query! | error: {0}]".format(error)


			for idx,mObj in enumerate(ml_buffer):
			    str_mObj = mObj.p_nameShort

			    try:#Status update ----------------------------------------------------------------------
				str_message = "Aiming : '{0}' {1} > '{2}'".format(str_tag,str_side,str_mObj)
				self.log_info(str_message)
				self.progressBar_set(status = (str_message),progress = idx, maxValue = int_len)	
			    except Exception,error:raise Exception,"[Status update] | error: {0}".format(error)	

			    try:#Gather data ----------------------------------------------------------------------
				try:d_current = self.md_attachReturns[mObj]
				except:
				    d_current = {}
				    self.log_warning("'%s' | no attachReturn"%str_mObj)	

				str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'lipLineBlend'
				mi_upLoc = d_buffer.get('upLoc') or d_build[str_tag].get('upLoc') or d_current.get('upLoc') or False
				mi_masterGroup = mObj.masterGroup
				_d['str_mode'] = str_mode
				_d['upLoc'] = mi_upLoc	
			    except Exception,error:raise Exception,"[Gather Data] | error: {0}".format(error)

			    try:#Aim Offset group ----------------------------------------------------------------------
				'''
				We need to first find our target which be a child to our aimOffset group. Sometimes that's the basic offset group
				'''
				mi_offsetTarget = d_buffer.get('offsetGroup') or d_build[str_tag].get('offsetGroup') or False
				if not mi_offsetTarget:
				    try: mi_offsetTarget = d_current['offsetGroup']#See if we have an offset group
				    except:
					self.log_warning("'{0}' |No offset group in build dict. Checking object".format(str_mObj))
					try:
					    mi_offsetTarget = mObj.offsetGroup
					except:
					    self.log_warning("'%s' | No offset group found. Using object"%str_mObj)					
					    mi_offsetTarget = mObj

				mi_aimOffsetGroup = cgmMeta.asMeta(mi_offsetTarget.doGroup(True),'cgmObject',setClass=True)
				mi_aimOffsetGroup.doStore('cgmName',mObj)
				mi_aimOffsetGroup.addAttr('cgmTypeModifier','AimOffset',lock=True)
				mi_aimOffsetGroup.doName()
				mObj.connectChildNode(mi_aimOffsetGroup,"aimOffsetGroup","childObject")					    
			    except Exception,error:raise Exception,"[AimOffset group] | error: {0}".format(error)

			    if str_mode == 'lipLineSegmentBlend':#This is pretty much just for the lip rig line for now
				try:#Getting up loc --------------------------------------------------------------------
				    self.log_info("'%s' | getting up loc..."%str_mObj)
				    if str_side == 'center':
					mi_segmentCurve =  mObj.skinJoint.segJoint.segmentCurve
					mi_upLoc = d_buffer['midUpLoc']
					mi_midHandle = d_buffer['midHandle']
					l_centerTargets = d_buffer['centerTargets']
				    else:
					mi_upLoc = mObj.skinJoint.segJoint.upLoc
				except Exception,error:raise Exception,"['%s' upLoc!]{%s}"%(str_mObj,error)

				try:
				    str_baseKey = d_buffer.get('baseKey') or d_build[str_tag].get('baseKey') or str_tag
				    if not str_baseKey:raise Exception,"No baseKey found!"
				    self.log_info("'{0}' | baseKey: {1}".format(str_mObj,str_baseKey))					    

				    _d['baseKey'] = str_baseKey		
				    try:#Vectors
					self.log_info("'%s' | getting vectors..."%str_mObj)					    						
					v_up = _d.get('v_up') or mi_go._vectorUp

					if str_side == 'right':
					    v_aimIn = mi_go._vectorOut
					    v_aimOut = mi_go._vectorOutNegative	
					    ml_buffer = copy.copy(ml_buffer)
					    ml_buffer.reverse()
					else:
					    v_aimIn = mi_go._vectorOutNegative
					    v_aimOut = mi_go._vectorOut	

					_d['v_aimIn'] = v_aimIn
					_d['v_aimOut'] = v_aimOut
					_d['v_up'] = v_up										
				    except Exception,error:raise Exception,"[Vector query!] | error: {0}".format(error)					    

				except Exception,error:raise Exception,"[{0} query | error: {1}]".format(str_mode,error)					

				try:
				    self.log_info("'{0}' | getting targets...".format(str_mObj))					    											    
				    if str_side != 'center':					
					#Get objects
					if idx == 0:
					    mi_aimOut = self.md_rigList['lipCornerRig'][str_side][0]
					    mi_aimIn = ml_buffer[idx+1].masterGroup
					elif idx == int_last:
					    mi_aimOut = ml_buffer[idx-1].masterGroup
					    mi_aimIn = md_buffer['center'][0].masterGroup			    
					else:
					    mi_aimOut = ml_buffer[idx-1].masterGroup
					    mi_aimIn = ml_buffer[idx+1].masterGroup
				    else:
					mi_aimOut = self.md_rigList[str_baseKey]['left'][-1].masterGroup
					mi_aimIn = self.md_rigList[str_baseKey]['right'][-1].masterGroup	
				    _d['aimIn'] = mi_aimIn.mNode
				    _d['aimOut'] = mi_aimOut.mNode
				except Exception,error:raise Exception,"[Get aim targets] | error: {0}".format(error)

				#self.log_info("Side: '%s' | idx: %s | Aiming :'%s' | in:'%s' | out:'%s' | up:'%s' "%(str_side,idx,str_mObj,mi_aimIn.p_nameShort,mi_aimOut.p_nameShort,mi_upLoc.p_nameShort))

				#loc creation ------------------------------------------------------------------------
				try:
				    self.log_info("'{0}' | making locs...".format(str_mObj))					    											    
				    mi_locIn = mObj.doLoc()
				    mi_locIn.addAttr('cgmTypeModifier','aimIn',lock=True)
				    mi_locIn.doName()					    

				    mi_locOut = mObj.doLoc()
				    mi_locOut.addAttr('cgmTypeModifier','aimOut',lock=True)
				    mi_locOut.doName()	

				    mi_go.connect_toRigGutsVis([mi_locIn,mi_locOut],vis = 1, doShapes = True)#connect to guts vis switches

				    mi_locIn.parent = mi_masterGroup
				    mi_locOut.parent = mi_masterGroup
				except Exception,error:raise Exception,"[Aim loc creation!] | error: {0}".format(error)
				try:
				    if str_side == 'center':
					#If it's our center we're going to aim at the up object with the aimout/in as up vectors -- bad, Josh
					'''
					mc.aimConstraint(mi_upLoc.mNode, mi_locIn.mNode,
							 weight = 1, aimVector = v_up, upVector = v_aimIn,
							 maintainOffset = 0,
							 worldUpObject = mi_aimIn.mNode, worldUpType = 'object' ) 
					mc.aimConstraint(mi_upLoc.mNode, mi_locOut.mNode,
							 weight = 1, aimVector = v_up, upVector = v_aimOut,
							 maintainOffset = 0,					                     
							 worldUpObject = mi_aimOut.mNode, worldUpType = 'object' )
					mi_contraint = cgmMeta.cgmNode(mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_aimOffsetGroup.mNode,
											   maintainOffset = True,					                        
											   weight = 1)[0]) 
					''' 
					mi_locIn.parent = l_centerTargets[0]
					mi_locOut.parent = l_centerTargets[1]                                                
					mi_contraint = cgmMeta.cgmNode(mc.orientConstraint(l_centerTargets, mi_aimOffsetGroup.mNode,
				                                                           maintainOffset = True,					                        
				                                                           weight = 1)[0])                                                 
					mi_contraint.interpType = 0						
					#mi_contraint = cgmMeta.cgmNode(mc.orientConstraint([mi_midHandle.mNode], mObj.masterGroup.mNode,
											    #maintainOffset = 1,					                        
											    # weight = 1)[0]) 

					#cgmMeta.cgmAttr(mi_midHandle,'result_averageRoll').doConnectOut("%s.r%s"%(mi_aimOffsetGroup.mNode,mi_go._jointOrientation[2]))
				    else:
					mc.aimConstraint(mi_aimIn.mNode, mi_locIn.mNode,
				                         weight = 1, aimVector = v_aimIn, upVector = v_up,
				                         maintainOffset = 1,
				                         worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
					mc.aimConstraint(mi_aimOut.mNode, mi_locOut.mNode,
				                         weight = 1, aimVector = v_aimOut, upVector = v_up,
				                         maintainOffset = 1,					                     
				                         worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
					mi_contraint = cgmMeta.cgmNode(mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_aimOffsetGroup.mNode,
				                                                           maintainOffset = True,					                        
				                                                           weight = 1)[0]) 
				    mi_contraint.interpType = 0
				except Exception,error:raise Exception,"[Constraints setup!] | error: {0}".format(error)
			    elif str_mode in  ['segmentSingleAim','segmentStartAim']:
				try:#>>Vectors ----------------------------------------------------------------------
				    self.log_info("'%s' | getting vectors..."%str_mObj)					    						
				    v_up = d_buffer.get('v_up') or d_build[str_tag].get('v_up') or False
				    v_aim = d_buffer.get('v_aim') or d_build[str_tag].get('v_aim') or False
				    if not v_aim:
					self.log_infoDict(d_buffer,'d_buffer')
					self.log_infoDict(d_build[str_tag],'d_build')
					
					raise ValueError,"No v_aim found"
				    v_aimNegative = [v*-1 for v in v_aim]
				except Exception,error:raise Exception,"[{0} Vector query!] | error: {1}".format(str_mode,error)	
				
				try:#>>Targets ----------------------------------------------------------------------
				    if str_mode == 'segmentSingleAim':
					if mObj != ml_buffer[-1]:
					    mi_target = ml_buffer[idx +1].masterGroup
					    v_useAim = v_aim
					else:
					    mi_target = ml_buffer[-2].masterGroup
					    v_useAim = v_aimNegative
				    else:
					if mObj == ml_buffer[0]:
					    mi_target = ml_buffer[1].masterGroup
					    v_useAim = v_aim
					else:
					    mi_target = ml_buffer[0].masterGroup
					    v_useAim = v_aimNegative                                                
				except Exception,error:raise Exception,"[Targets query!] | error: {0}".format(error)	

				try:#>>Aim ----------------------------------------------------------------------
				    mc.aimConstraint(mi_target.mNode, mi_aimOffsetGroup.mNode,
			                             weight = 1, aimVector = v_useAim, upVector = v_up,
			                             maintainOffset = True,
			                             worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
				except Exception,error:raise Exception,"[Constraints setup!] | error: {0}".format(error)
				
			    elif str_mode == 'singleBlend':#...single aim blend
				try:#>>Gather data ----------------------------------------------------------------------
				    d_target0 = d_buffer.get('d_target0') or d_build[str_tag].get('d_target0')
				    d_target1 = d_buffer.get('d_target1') or d_build[str_tag].get('d_target1')
				    if not d_target0:raise StandardError,"Failed to get d_target0"
				    if not d_target1:raise StandardError,"Failed to get d_target1"
				    up_target0 = d_target0.get('upLoc') or mi_upLoc
				    up_target1 = d_target1.get('upLoc') or mi_upLoc
				except Exception,error:
				    self.log_warning("d_buffer: {0}".format(d_buffer))
				    raise Exception,"[Gather Data] | error: {0}".format(error)											
				try:
				    mi_locIn = mObj.doLoc()
				    mi_locIn.addAttr('cgmTypeModifier','aim0',lock=True)
				    mi_locIn.doName()					    

				    mi_locOut = mObj.doLoc()
				    mi_locOut.addAttr('cgmTypeModifier','aim1',lock=True)
				    mi_locOut.doName()	

				    mi_go.connect_toRigGutsVis([mi_locIn,mi_locOut],vis = 1, doShapes = True)#connect to guts vis switches

				    mi_locIn.parent = mi_aimOffsetGroup.parent
				    mi_locOut.parent = mi_aimOffsetGroup.parent
				except Exception,error:raise Exception,"[Aim loc creation!] | error: {0}".format(error)
				try:
				    mc.aimConstraint(d_target0['target'].mNode, mi_locIn.mNode,
			                             weight = 1, aimVector = d_target0['v_aim'], upVector = d_target0['v_up'],
			                             maintainOffset = 1,
			                             worldUpObject = up_target0.mNode, worldUpType = 'object' ) 
				    mc.aimConstraint(d_target1['target'].mNode, mi_locOut.mNode,
			                             weight = 1, aimVector = d_target1['v_aim'], upVector = d_target1['v_up'],
			                             maintainOffset = 1,					                     
			                             worldUpObject = up_target1.mNode, worldUpType = 'object' ) 
				    mi_contraint = cgmMeta.cgmNode(mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_aimOffsetGroup.mNode,
			                                                               maintainOffset = True,					                        
			                                                               weight = 1)[0]) 
				    mi_contraint.interpType = 0
				except Exception,error:raise Exception,"[Constraints setup!] | error: {0}".format(error)
			    elif str_mode == 'singleTarget':
				try:				
				    '''
				    d_build = {'noseUnderRig':{'mode':'singleTarget','aimVector':mi_go._vectorUpNegative,'upVector':mi_go._vectorAim,
						   'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseUnderTarget}}
					'''
				    mi_aimTo = d_buffer['aimTarget']
				    v_up = d_buffer['v_up']
				    v_aim = d_buffer['v_aim']
				    _d['mi_aimTo'] = mi_aimTo
				    _d['v_up'] = v_up
				    _d['v_aim'] = v_aim
				except Exception,error:raise Exception,"[%s query]{%s}"%(str_mode,error)
				self.log_info("Side: '%s' | idx: %s | Aiming :'%s' | to:'%s' | up:'%s' "%(str_side,idx,str_mObj,mi_aimTo.p_nameShort,mi_upLoc.p_nameShort))					
				try:
				    mc.aimConstraint(mi_aimTo.mNode, mi_aimOffsetGroup.mNode,
			                             weight = 1, aimVector = v_aimIn, upVector = v_up,
			                             maintainOffset = True,
			                             worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
				except Exception,error:raise Exception,"[Constraints setup!] | error: {0}".format(error)	
			    elif str_mode == 'singleVectorAim':
				try:				
				    ml_aimTo = d_buffer['aimTargets']
				    if type(ml_aimTo) not in [list,tuple]:ml_aimTo = [ml_aimTo]
				    v_up = d_buffer['v_up']
				    v_aim = d_buffer['v_aim']
				    _d['ml_aimTo'] = ml_aimTo
				    _d['v_up'] = v_up
				    _d['v_aim'] = v_aim
				except Exception,error:raise Exception,"[%s query]{%s}"%(str_mode,error)
				self.log_info("Side: '%s' | idx: %s | Aiming :'%s' | to:'%s' | up:'%s' "%(str_side,idx,str_mObj,[mTarget.mNode for mTarget in ml_aimTo],mi_upLoc.p_nameShort))					
				try:
				    mc.aimConstraint([mTarget.mNode for mTarget in ml_aimTo], mi_aimOffsetGroup.mNode,
			                             weight = 1, aimVector = v_aimIn, upVector = v_up,
			                             maintainOffset = True,
			                             worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
				except Exception,error:raise Exception,"[singleVectorAim setup!] | error: {0}".format(error)						


			    else:
				raise NotImplementedError,"Mode not implemented : '{0}'".format(str_mode)
		except Exception,error: raise Exception,"['{0}' '{1}' fail] | error: {2}".format(str_tag, str_side,error)
    except Exception,error: raise Exception,"[aim_fromDict] | error: {0}".format(error)
    
def skin_fromDict(self,d_build):
    try:#>> skin  =======================================================================================
	mi_go = self._go#Rig Go instance link
	self.progressBar_setMaxStepValue(len(d_build.keys()))

	for str_tag in d_build.iterkeys():
	    try:
		self.progressBar_iter(status = ("Skinning : '%s'"%str_tag))									
		try:#Build list
		    __target = d_build[str_tag]['target']
		    __bindJoints = d_build[str_tag]['bindJoints']
		    __mi = d_build[str_tag].get('mi') or 5
		    __dr = d_build[str_tag].get('dr') or 7
		except Exception,error:raise Exception,"[get data |error: {0}]".format(error)

		try:#Cluster
		    ret_cluster = mc.skinCluster([mObj.mNode for mObj in [__target] + __bindJoints], tsb = True, normalizeWeights = True, mi = __mi, dr = __dr)
		    i_cluster = cgmMeta.asMeta(ret_cluster[0],'cgmNode',setClass=True)
		    i_cluster.doStore('cgmName',__target)
		    i_cluster.doName()		
		except Exception,error:raise Exception,"[Cluster |error: {0}]".format(error)

	    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)			    
    except Exception,error:  raise StandardError,"[skin_fromDict |error: {0}]".format(error)	

def create_plateFromDict(self,md_plateBuilds):
    try:#Main plates -----------------------------------------------------------------------------	
	mi_go = self._go#Rig Go instance link		
	self.progressBar_setMaxStepValue(len(md_plateBuilds.keys()))

	for str_name in md_plateBuilds.iterkeys():
	    try:
		self.progressBar_iter(status = ("Plate build: '%s'"%str_name))						
		d_buffer = md_plateBuilds[str_name]#get the dict
		self.d_buffer = d_buffer
		str_mode = d_buffer.get('mode')
		if str_mode == 'cheekLoft':
		    try:#Cheek loft
			l_deleteBuffer = []
			str_direction = d_buffer['direction']
			#str_name = d_buffer['name']
			mi_smileCrv = d_buffer['smileCrv']
			d_buffer['uprCheekJoints'] = self.md_rigList['uprCheekRig'][str_direction]#[:-1]
			d_buffer['cheekJoints'] = self.md_rigList['cheekRig'][str_direction]				
			d_buffer['jawLineJoints'] = self.md_rigList['jawLine'][str_direction]
			d_buffer['sneerHandle'] = self.md_rigList['sneerHandle'][str_direction][0]
			d_buffer['smileBaseHandle'] = self.md_rigList['smileBaseHandle'][str_direction][0]				

			try:#Build our rail curves
			    l_railCrvs = []
			    ml_uprCheekRev = copy.copy(d_buffer['uprCheekJoints'])
			    ml_uprCheekRev.reverse()
			    ml_jawLineRev = copy.copy(d_buffer['jawLineJoints'])
			    ml_jawLineRev.reverse()

			    ml_startRailObjs = [d_buffer['sneerHandle']] + ml_uprCheekRev
			    ml_endRailObjs = [d_buffer['smileBaseHandle']] + ml_jawLineRev
			    #self.log_info("startRailObjs: %s"%[mObj.p_nameShort for mObj in ml_startRailObjs])
			    #self.log_info("endRailObjs: %s"%[mObj.p_nameShort for mObj in ml_endRailObjs])
			    #self.log_info("cheekJoints: %s"%[mObj.p_nameShort for mObj in d_buffer['cheekJoints']])

			    str_startRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_startRailObjs], os = True)
			    str_endRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endRailObjs], os = True)

			    #str_startRailCrv = mc.rebuildCurve (str_startRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
			    #str_endRailCrv = mc.rebuildCurve (str_endRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
			    str_startRailCrv = returnRebuiltCurveString(str_startRailCrv,5,1)
			    str_endRailCrv = returnRebuiltCurveString(str_endRailCrv,5,1)

			except Exception,error:raise Exception,"[Rail curve build |error: {0}]".format(error)

			try:				    
			    ml_endProfileObjs = [ml_startRailObjs[-1],d_buffer['cheekJoints'][0], ml_endRailObjs[-1]]
			    #self.log_info("endProfileObjs: %s"%[mObj.p_nameShort for mObj in ml_endProfileObjs])
			    str_endProfileCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endProfileObjs], os = True)
			    str_startProfileCrv = mc.rebuildCurve (mi_smileCrv.mNode, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
			    str_endProfileCrvRebuilt = mc.rebuildCurve (str_endProfileCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]

			except Exception,error:raise Exception,"[Profile curves build |error: {0}]".format(error)	

			try:
			    str_loft = mc.doubleProfileBirailSurface( str_startProfileCrv, str_endProfileCrvRebuilt,
		                                                      str_startRailCrv, str_endRailCrv, 
		                                                      blendFactor = .5,constructionHistory=0, object=1, polygon=0, transformMode=0)[0]
			except Exception,error:raise Exception,"[birail create |error: {0}]".format(error)	

			mc.delete([str_startProfileCrv,str_startRailCrv,str_endRailCrv,str_endProfileCrv])#Delete the rebuilt curves
		    except Exception,error:raise Exception,"[Reg plate loft |error: {0}]".format(error)	
		elif str_mode == 'liveSurface':
		    try:
			str_loft = mc.loft([mCrv.mNode for mCrv in d_buffer['crvs']],ch = True, uniform = True,degree = 3,ss = 3)[0]			    
		    except Exception,error:raise Exception,"[Live Surface loft | error: {0}]".format(error)	
		else:
		    try:#Reg curve loft
			l_crvsRebuilt = []
			for mi_crv in d_buffer['crvs']:#rebuild crvs
			    l_crvsRebuilt.append(returnRebuiltCurveString(mi_crv,4))

			str_loft = mc.loft(l_crvsRebuilt,uniform = True,degree = 3,ss = 3)[0]
			mc.delete(l_crvsRebuilt)#Delete the rebuilt curves
		    except Exception,error:raise Exception,"[Reg plate loft |error: {0}]".format(error)	

		try:#tag, name, store
		    mi_obj = cgmMeta.cgmObject(str_loft)
		    mi_obj.parent = mi_go._i_rigNull#parent to rigNull
		    self.__dict__['mi_%sPlate'%(str_name)] = mi_obj
		    mi_obj.addAttr('cgmName',d_buffer.get('name') or str_name,lock=True)
		    try:mi_obj.addAttr('cgmDirection',str_direction ,lock=True)
		    except:pass
		    mi_obj.addAttr('cgmTypeModifier','plate',lock=True)					    
		    mi_obj.doName()
		    mi_go._i_rigNull.connectChildNode(mi_obj,"%sPlate"%str_name,'module')
		except Exception,error:raise Exception,"[Tag/Name/Store |error: {0}]".format(error)	

	    except Exception,error:raise Exception,"%s | %s"%(str_name,error)	
	    #self.log_infoNestedDict('d_buffer')		    
    except Exception,error:raise Exception,"[create_plateFromDict | error: {0}]".format(error)

def create_ribbonsFromDict(self,md_ribbonBuilds):
    try:#Ribbons -----------------------------------------------------------------------------	
	mi_go = self._go#Rig Go instance link		
	self.progressBar_setMaxStepValue(len(md_ribbonBuilds.keys()))		
	for str_name in md_ribbonBuilds.iterkeys():
	    try:
		self.progressBar_iter(status = ("Ribbon build: '%s'"%str_name))			
		d_buffer = md_ribbonBuilds[str_name]#get the dict
		self.d_buffer = d_buffer
		f_dist = mi_go._f_skinOffset*.5

		if d_buffer.get('mode') == 'radialLoft':
		    try:mi_obj = surfUtils.create_radialCurveLoft(d_buffer['extrudeCrv'].mNode,d_buffer['aimObj'].mNode,f_dist)
		    except Exception,error:raise Exception,"[Radial Loft |error: {0}]".format(error)
		else:
		    try:#Regular loft -----------------------------------------------------------------------
			ml_joints = d_buffer['joints']
			mi_crv = d_buffer['extrudeCrv']

			try:#Make our loft loc -----------------------------------------------------------------------
			    #f_dist = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_joints])*.05
			    d_buffer['dist'] = f_dist

			    mi_loc = ml_joints[-1].doLoc()
			    mi_loc.doGroup()
			except Exception,error:raise Exception,"[loft loc | error: {0}]".format(error)

			try:#Cross section creation -----------------------------------------------------------------------
			    l_profileCrvPos = []
			    for dist in [0,f_dist]:
				mi_loc.__setattr__("t%s"%mi_go._jointOrientation[1],dist)
				l_profileCrvPos.append(mi_loc.getPosition())

			    str_profileCrv = mc.curve(d = 1,ep = l_profileCrvPos, os = True)
			except Exception,error:raise Exception,"[Cross section creation |error: {0}]".format(error)

			try:#Extrude crv -----------------------------------------------------------------------
			    str_extruded = mc.extrude([str_profileCrv,mi_crv.mNode],et = 1, sc = 1,ch = 1,useComponentPivot = 0,fixedPath=1)[0]
			    mi_obj = cgmMeta.cgmObject(str_extruded)
			    mc.delete(mi_loc.parent,str_profileCrv)
			except Exception,error:raise Exception,"[Extrude crv | error: {0}]".format(error)	
		    except Exception,error:raise Exception,"[Regular loft |error: {0}]".format(error)
		try:
		    self.__dict__['mi_%sRibbon'%(str_name)] = mi_obj
		    mi_obj.parent = mi_go._i_rigNull#parent to rigNull			    
		    mi_obj.addAttr('cgmName',str_name,lock=True)
		    mi_obj.addAttr('cgmTypeModifier','ribbon',lock=True)			    
		    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
		    except:pass
		    mi_obj.doName()
		    mi_go._i_rigNull.connectChildNode(mi_obj,"%sRibbon"%str_name,'module')			    
		except Exception,error:raise Exception,"[Naming | error: {0}]".format(error)
		#self.log_infoNestedDict('d_buffer')
	    except Exception,error:raise Exception,"%s | %s"%(str_name,error)
    except Exception,error:raise Exception,"[create_ribbonsFromDict |error: {0}]".format(error)

def create_curvesFromDict(self,d_build):
    try:#Ribbons -----------------------------------------------------------------------------	
	mi_go = self._go#Rig Go instance link		
	self.progressBar_setMaxStepValue(len(d_build.keys()))		
	for str_name in d_build.iterkeys():
	    try:
		self.progressBar_iter(status = ("Curve build: '%s'"%str_name))			
		d_buffer = d_build[str_name]#get the dict
		self.d_buffer = d_buffer
		f_dist = mi_go._f_skinOffset*.5

		if d_buffer.get('mode') == 'asdfasdfasdf':
		    pass
		else:
		    try:#Curve -----------------------------------------------------------------------
			ml_objs = d_buffer['pointTargets']
			str_curve = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_objs], os = True)
			mi_obj = cgmMeta.asMeta(str_curve,'cgmObject',setClass=True)
		    except Exception,error:raise Exception,"[Regular curve | error: {0}]".format(error)
		try:
		    self.__dict__['mi_%sCrv'%(str_name)] = mi_obj
		    mi_obj.addAttr('cgmName',str_name,lock=True)
		    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
		    except:pass
		    mi_obj.doName()
		    mi_go._i_rigNull.connectChildNode(mi_obj,"%sCrv"%str_name,'module')	
		    mi_obj.parent = mi_go._i_rigNull#parent to rigNull			    			    
		except Exception,error:raise Exception,"[Naming |error: {0}]".format(error)
		#self.log_infoNestedDict('d_buffer')
	    except Exception,error:raise Exception,"%s | %s"%(str_name,error)
    except Exception,error:raise Exception,"[create_curvesFromDict |error: {0}]".format(error)
