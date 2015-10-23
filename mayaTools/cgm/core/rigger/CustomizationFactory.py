import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import cgm.core

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.lib.classes import NameFactory as nFactory
from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (curves,
                     deformers,
                     distance,
                     search,
                     lists,
                     modules,
                     constraints,
                     rigging,
                     attributes,
                     joints,
                     guiFactory)
reload(constraints)
reload(rigging)
reload(nFactory)
reload(search)
reload(deformers)
from cgm.lib.zoo.zooPyMaya import skinWeights

_d_customizationGeoGroupsToCheck = {'tongue':'tongueGeoGroup',
                                    'uprTeeth':'uprTeethGeoGroup',
                                    'lwrTeeth':'lwrTeethGeoGroup',
                                    'eyebrow':'eyebrowGeoGroup',
                                    'hair':'hairGeoGroup',
                                    'clothes':'clothesGeoGroup',
                                    'earLeft':'left_earGeoGroup',
                                    'earRight':'right_earGeoGroup',
                                    'eyeLeft':'left_eyeGeoGroup',
                                    'eyeRight':'right_eyeGeoGroup'}

_d_main_geoInfo = {'unified':{'msg':'geo_unified',
                              'msg_reset':'geo_resetUnified',
                              'msg_bridge':'geo_bridgeUnified',
                              'msg_bsBridge':'bsNode_bridgeMain'},
                   'body':{'msg':'geo_baseBody',
                           'msg_reset':'geo_resetBody',
                           'msg_bridge':'geo_bridgeBody',
                           'msg_bsBridge':'bsNode_bridgeBody'},
                   'head':{'msg':'geo_baseHead',
                           'msg_reset':'geo_resetHead',
                           'msg_bridge':'geo_bridgeHead',
                           'msg_bsBridge':'bsNode_bridgeFace'},}

#======================================================================
# Functions for a cgmMorpheusMakerNetwork
#======================================================================
def isCustomizable(self):
    """
    Checks if an asset is good to go or not
    """
    return True

#======================================================================
# Processing factory
#======================================================================
def go(*args, **kws):
    """
    Customization template builder from template file for setting up a cgmMorpheusMakerNetwork

    :parameters:
    0 - 'customizationNode'(morpheusCustomizationAsset - None) | Morpheus system biped customization asset

    :returns:
        Nothing
    ##Dict ------------------------------------------------------------------
    ##'mi_segmentCurve'(cgmObject) | segment curve
    ##'segmentCurve'(str) | segment curve string

    :raises:
    Exception | if reached

    """       
    class fncWrap(cgmGeneral.cgmFuncCls):		
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'customizationFactory.go'	
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'customizationNode',"default":'Morphy_customizationNetwork',"argType":'morpheusBipedCustomizationAsset','help':"This should be a customization asset"}]	    
            self.__dataBind__(*args, **kws)
            #Now we're gonna register some steps for our function...
            '''
	    doBridge_bsNode(self.p)
	    if stopAt == 'bsBridge':return
	    #doBody_bsNode(self)
	    #if stopAt == 'bsBody':return		
	    #doFace_bsNode(self)
	    #if stopAt == 'bsFace':return		
	    doSkinBody(self)
	    if stopAt == 'skin':return
	    doConnectVis(self)
	    if stopAt == 'vis':return
	    doLockNHide(self,p)
	    '''
            self.l_funcSteps = [{'step':'Gather Info','call':self._validate_},
                                {'step':'Mirror Template','call':self._mirrorBridge_},
                                {'step':'Rig Body','call':self._rigBodyBridge_},
                                {'step':'Constraints','call':self._do_setupConstraints_},                                
                                {'step':'RigBlocks','call':self._do_rigBlocks_},
                                {'step':'Check Reset/Bridge Geo','call':self._do_check_resetAndBridgeGeo_},                                
                                {'step':'Blendshape Bridge','call':self._do_bsNodeBridge_},
                                #{'step':'Blendshape Body','call':self._do_bsNodeBody_},
                                #{'step':'Blendshape Face','call':self._do_bsNodeFace_},
                                {'step':'Skincluster','call':self._do_skinBody_},
                                {'step':'Wraps','call':self._do_setupWraps_},	                        
                                {'step':'Connect Vis','call':self._do_connectVis_},
                                {'step':'LockNHide','call':self._do_lockNHide_},

                                ]

        def _validate_(self):
            try:
                self.mi_network = cgmMeta.validateObjArg(self.d_kws['customizationNode'],mType = cgmPM.cgmMorpheusMakerNetwork,noneValid = False)
            except Exception,error:
                raise Exception,"customizationNode is invalid | {0}".format(error)
            
            _bfr = self.mi_network.getMessageAsMeta('mSimpleFaceModule')
            if not _bfr:
                raise ValueError,"Repair mSimpleFace connection"
            self.mi_simpleFaceModule = _bfr

            try:#> Gather geo ------------------------------------------------------------------------------------------
                self.md_coreGeo = {}
                for k in _d_main_geoInfo.keys():
                    try:
                        _bfr = self.mi_network.getMessage(_d_main_geoInfo[k]['msg'],False)
                        if not _bfr:
                            raise ValueError,"Repair {0} connection | {1}".format(k,_d_main_geoInfo[k]['msg'])
                        else:self.log_debug("{0} found".format(k))   
                        
                        self.md_coreGeo[k] = {'mi_base':cgmMeta.validateObjArg(_bfr,mayaType = ['mesh'])}
                    except Exception,error:
                        raise Exception,"Core geo check failed on {0} | {1}".format(k,error)
                
                
                #geo_unified = self.mi_network.getMessage('geo_unified')
                #if not geo_unified:
                    #raise RuntimeError,"No base geo found"
                #self.mi_geo_unified = cgmMeta.validateObjArg(geo_unified,mayaType = ['mesh'])
                
                self.md_geoGroups = {}
                self.d_skinTargets = {}
                d_geoGroupsToCheck = _d_customizationGeoGroupsToCheck

                for key in d_geoGroupsToCheck.keys():
                    try:
                        self.log_info("Checking : '{0}' | msgAttr: '{1}'".format(key,d_geoGroupsToCheck[key]))
                        buffer = self.mi_network.masterNull.getMessage(d_geoGroupsToCheck[key])
                        if not buffer:raise RuntimeError,"Group not found"			    
                        mi_group = cgmMeta.validateObjArg(buffer,mayaType = ['group','transform'])
                        l_geoGroupObjs = mi_group.getAllChildren()
                        if not l_geoGroupObjs:
                            if key == 'body':
                                raise ValueError,"No body geo in base_geo_grp!"                               
                            self.log_warning("Empty group: '{0}'".format(mi_group.p_nameShort))
                        else:
                            l_toSkin = []
                            for o in l_geoGroupObjs:
                                if search.returnObjectType(o) in ['mesh','nurbsSurface']:
                                    l_toSkin.append(o) 
                                else:
                                    self.log_info("Not skinnable: '{0}'".format(o))				    
                            if not l_toSkin:
                                self.log_warning("No skinnable objects found")
                            else:
                                self.d_skinTargets[key] = l_toSkin
                                self.log_info("---To skin or attach:")			    
                                for o in l_toSkin:
                                    self.log_info("     '{0}'".format(o))				
                        self.md_geoGroups[key] = mi_group
                    except Exception,error:raise Exception,"{0} | {1}".format(key,error)			
            except Exception,error:
                raise Exception,"Geo gather fail | {0}".format(error)

            try:#> BS Gather geo ------------------------------------------------------------------------------------------	    
                self.log_info("Checking for blendshape Geo Targets")
                self.md_bsGeoGroups = {}
                self.d_bsGeoTargets = {}

                d_bodyBsGeoGroupsToCheck = {'fullbody':'fullBodyTargetsGroup',
                                            'torso':'torsoTargetsGroup'}
                d_faceBsGeoGroupsToCheck = {'mouth':'mouthTargetsGroup',
                                            'nose':'noseTargetsGroup',
                                            'brow':'browTargetsGroup',
                                            'fullFace':'fullFaceTargetsGroup'}
                d_sectionKeys = {0:'body',1:'face'}

                for i,d in enumerate([d_bodyBsGeoGroupsToCheck,d_faceBsGeoGroupsToCheck]):
                    str_sectionKey = d_sectionKeys[i]
                    self.d_bsGeoTargets[str_sectionKey] = []
                    try:
                        for key in d.keys():
                            try:
                                self.log_info("Checking : '{0}' | '{1}' | msgAttr: '{2}'".format(str_sectionKey,key,d[key]))
                                buffer = self.mi_network.masterNull.getMessage(d[key])
                                if not buffer:raise RuntimeError,"Group not found"			    
                                mi_group = cgmMeta.validateObjArg(buffer,mayaType = ['group','transform'])
                                l_geoGroupObjs = mi_group.getAllChildren()
                                if not l_geoGroupObjs:
                                    self.log_warning("Empty group: '{0}'".format(mi_group.p_nameShort))
                                else:
                                    l_toConnect = []
                                    for o in l_geoGroupObjs:
                                        if search.returnObjectType(o) in ['mesh']:
                                            l_toConnect.append(o) 
                                        else:
                                            self.log_info("Not connectable: '{0}'".format(o))				    
                                    if not l_toConnect:
                                        self.log_warning("No connectable objects found")
                                    else:
                                        self.d_bsGeoTargets[str_sectionKey].extend(l_toConnect)
                                        self.log_info("---To set as target:")			    
                                        for o in l_toConnect:
                                            self.log_info("     '{0}'".format(o))
                            except Exception,error:raise Exception,"{0} | {1}".format(key,error)			

                        self.md_bsGeoGroups[key] = mi_group
                    except Exception,error:raise Exception,"{0} | {1}".format(str_sectionKey,error)

                self.log_infoNestedDict('d_bsGeoTargets')
                self.log_infoNestedDict('md_bsGeoGroups')

            except Exception,error:
                raise Exception,"bs Geo gather fail | {0}".format(error)	

        def _mirrorBridge_(self):_mirrorTemplate_(self)
        def _rigBodyBridge_(self):_rigBody_(self)  
        def _do_setupConstraints_(self):_setupConstraints_(self) 
        def _do_bsNodeBridge_(self):_bs_bridge_(self)    	
        def _do_bsNodeBody_(self):_bs_body_(self)    
        def _do_rigBlocks_(self):_rigBlocks_(self)    	        
        def _do_bsNodeFace_(self):_bs_face_(self)    
        def _do_skinBody_(self):_skinBody_(self)    
        def _do_connectVis_(self):_connectVis_(self)   
        def _do_setupWraps_(self):_setupWraps_(self)    	
        def _do_lockNHide_(self):doLockNHide(self,self.mi_network.mNode,False)    
        def _do_check_resetAndBridgeGeo_(self):_check_resetAndBridgeGeo_(self)            

    return fncWrap(*args, **kws).go()

def _mirrorTemplate_(self):
    """ 
    Segement orienter. Must have a JointFactory Instance
    """ 
    try:
        # Get our base info
        #==================	        
        p = self.mi_network
        d_constraintParentTargets = {}
        d_constraintAimTargets = {}
        d_constraintPointTargets = {}
        d_constraintScaleTargets = {}
        d_constraintOrientTargets = {}    

        #Get skin joints
        try:#>>> Split out the left joints
            self.l_leftJoints = []
            self.l_leftRoots = []
            cntrCnt = 1
            for i_jnt in self.mi_network.jointList:
                self.log_info(i_jnt)
                if i_jnt.hasAttr('cgmDirection') and i_jnt.cgmDirection == 'left':
                    self.l_leftJoints.append(i_jnt.mNode)
                    if i_jnt.parent:#if it has a panent
                        i_parent = cgmMeta.cgmObject(i_jnt.parent)
                        self.log_info("'%s' child of '%s'"%(i_jnt.getShortName(),i_parent.getShortName()))
                        if not i_parent.hasAttr('cgmDirection'):
                            self.l_leftRoots.append(i_jnt.mNode)  
                            #If a joint is going to be mirrored need to grab snapshot of it's message connections to repair after mirroring
                            #Yay maya... obj.message that is '1_jnt', 'left_2_jnt' becomes '1_jnt', 'left_2_jnt,'right_2_jnt' after mirroring

                    if i_jnt.hasAttr('constraintParentTargets') and i_jnt.constraintParentTargets:
                        d_constraintParentTargets[i_jnt.getShortName()] = i_jnt.getMessage('constraintParentTargets',False)

                    if i_jnt.hasAttr('constraintAimTargets') and i_jnt.constraintAimTargets:
                        d_constraintAimTargets[i_jnt.getShortName()] = i_jnt.getMessage('constraintAimTargets',False)

                    if i_jnt.hasAttr('constraintPointTargets') and i_jnt.constraintPointTargets:
                        d_constraintPointTargets[i_jnt.getShortName()] = i_jnt.getMessage('constraintPointTargets',False)

                    if i_jnt.hasAttr('constraintScaleTargets') and i_jnt.constraintScaleTargets:
                        d_constraintScaleTargets[i_jnt.getShortName()] = i_jnt.getMessage('constraintScaleTargets',False)

                    if i_jnt.hasAttr('constraintOrientTargets') and i_jnt.constraintOrientTargets:
                        d_constraintOrientTargets[i_jnt.getShortName()] = i_jnt.getMessage('constraintOrientTargets',False)

                else:
                    #>>> tag our centre joints for mirroring later
                    i_jnt.addAttr('mirrorSide',attrType = 'enum', enumName = 'Centre:Left:Right', value = 0,keyable = False, hidden = True)
                    i_jnt.addAttr('mirrorIndex',attrType = 'int', value = cntrCnt,keyable = False, hidden = True)
                    #i_jnt.addAttr('mirrorAxis',value = 'translateX,translateY,translateZ')
                    cntrCnt+=1#enumerate won't work here

            self.l_leftJoints = lists.returnListNoDuplicates(self.l_leftJoints)
            self.l_leftRoots = lists.returnListNoDuplicates(self.l_leftRoots)
            p.joints_left = self.l_leftJoints
            p.roots_left = self.l_leftRoots
        except Exception,error:raise Exception,"left side gather fail | {0}".format(error)

        #>>> Customization network node
        self.log_info("ShaperJoints: %s"%self.mi_network.getMessage('jointList',False))
        self.log_info("leftJoints: %s"%self.mi_network.getMessage('joints_left',False))
        self.log_info("leftRoots: %s"%self.mi_network.getMessage('roots_left',False))

        try:#Mirror our joints, make mirror controls and store them appropriately
            #====================================================================
            try:
                self.l_leftJoints = self.mi_network.getMessage('joints_left',False)
                if not self.l_leftJoints:
                    raise ValueError,"No left joints found."
                if not self.mi_network.roots_left:
                    raise ValueError,"No left roots found."            
                self.l_rightJoints = []
                self.l_rightRoots = []
                segmentBuffers = []
            except Exception,error:raise Exception,"Initial checks fail. {0}".format(error)

            for r,i_root in enumerate(self.mi_network.roots_left):
                try:
                    l_mirrored = mc.mirrorJoint(i_root.mNode,mirrorBehavior = True, mirrorYZ = True)

                    mc.select(cl=True)
                    mc.select(i_root.mNode,hi=True)
                    l_base = mc.ls( sl=True )
                    segmentBuffer = []	
                    segName = i_root.getBaseName()

                    try:#Fist a quick naming loop before cullling out non joint stuff
                        ml_mirroredBuffer = cgmMeta.validateObjListArg(l_mirrored)
                        for i,mObj in enumerate(ml_mirroredBuffer):
                            if mObj.getMayaType() == 'shape':continue#...skip this one
                            mObj.cgmDirection = 'right'
                            mObj.doName()
                        for i,mObj in enumerate(ml_mirroredBuffer):#This is so inefficient...come back to this
                            l_mirrored[i] = mObj.mNode
                    except Exception,error:raise Exception,"Name loop fail | {0}".format(error)

                    try:
                        l_mirrored = mc.ls(l_mirrored,type = 'joint')#...Filter out, locs or anything
                        l_base =  mc.ls(l_base,type = 'joint')#...Filter out, locs or anything
                        if len(l_mirrored) != len(l_base):
                            raise ValueError,"Lengths don't match"
                    except Exception,error:
                        for i,obj in enumerate(l_mirrored):
                            self.log_error("{0} | should mirror | {1}".format(obj,l_base[i]))
                        raise Exception,"filter fail | {0}".format(error)

                    try:
                        int_max = len(l_mirrored)+1
                        mayaMainProgressBar = guiFactory.doStartMayaProgressBar(int_max)
                    except Exception,error:
                        self.log_error("len(l_mirrored): {0}".format(int_max))
                        raise Exception,"main progress bar set fail | {0}".format(error)

                    for i,jnt in enumerate(l_mirrored):
                        try:
                            if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                                break
                            mc.progressBar(mayaMainProgressBar, edit=True, status = "Mirroring segment '%s':'%s'..."%(segName,jnt), step=1)
                        except Exception,error:raise Exception,"progress bar set fail | {0}".format(error)
                        try:
                            i_jnt = cgmMeta.cgmObject(jnt)
                            i_jnt.doStore('cgmMirrorMatch',l_base[i])
                            attributes.storeInfo(l_base[i],'cgmMirrorMatch',i_jnt.mNode)
                        except Exception,error:raise Exception,"store fail | {0}".format(error)

                        try:#>>> Make curve
                            index = self.l_leftJoints.index(l_base[i]) #Find our main index
                            i_mirror = self.mi_network.joints_left[index] #store that mirror instance so we're not calling it every line
                            #if not i_mirror:raise ValueError,"Should have an i_mirror here"
                            buffer = mc.duplicate(i_mirror.getMessage('controlCurve')) #Duplicate curve
                            i_crv = cgmMeta.cgmObject( buffer[0] )
                            i_crv.cgmDirection = 'right'#Change direction
                            i_jnt.doStore('controlCurve',i_crv.mNode)#Store new curve to new joint
                            i_crv.doStore('cgmSource',i_jnt.mNode)
                            i_crv.doName()#name it

                        except Exception,error:
                            self.log_error("index: {0} | i_mirror: {1}".format(index,i_mirror))
                            raise Exception,"curve create fail | {0}".format(error)

                        try:#>>> Mirror the curve
                            s_prntBuffer = i_crv.parent#Shouldn't be necessary later
                            grp = mc.group(em=True)#Group world center
                            i_crv.parent = grp
                            attributes.doSetAttr(grp,'sx',-1)#Set an attr
                            i_crv.parent = s_prntBuffer
                            mc.delete(grp)
                        except Exception,error:raise Exception,"curve mirror fail | {0}".format(error)

                        try:#color it
                            l_colorRight = modules.returnSettingsData('colorRight',True)
                            if i_crv.hasAttr('cgmTypeModifier') and i_crv.cgmTypeModifier == 'secondary':
                                colorIndex = 1
                            else:
                                colorIndex = 0
                            curves.setCurveColorByName(i_crv.mNode,l_colorRight[colorIndex])#Color it, need to get secodary indexes
                            self.l_rightJoints.append(i_jnt.mNode)
                            segmentBuffer.append(i_jnt.mNode)#store to our segment buffer
                        except Exception,error:raise Exception,"Coloring fail | {0}".format(error)

                        try:#>>> Tag for mirroring
                            i_jnt.addAttr('mirrorSide',attrType = 'enum', enumName = 'Centre:Left:Right', value = 2,keyable = False, hidden = True)
                            i_jnt.addAttr('mirrorIndex',attrType = 'int', value = i+1,keyable = False, hidden = True)
                            i_jnt.addAttr('mirrorAxis',value = 'translateX,translateY,translateZ')

                            i_mirror.addAttr('mirrorSide',attrType = 'enum', enumName = 'Centre:Left:Right', value = 1,keyable = False, hidden = True)
                            i_mirror.addAttr('mirrorIndex',attrType = 'int', value = i+1,keyable = False, hidden = True)
                            i_mirror.addAttr('mirrorAxis',value = 'translateX,translateY,translateZ')
                        except Exception,error:raise Exception,"mirror tag fail | {0}".format(error)

                        try:#>>> See if we need to grab contraintTargets attr
                            if i_mirror.hasAttr('constraintParentTargets') and i_mirror.constraintParentTargets:
                                targets = []
                                for t in i_mirror.constraintParentTargets:
                                    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
                                    if 'cgmDirection' in d_search.keys() and d_search.get('cgmDirection')=='left':d_search['cgmDirection'] = 'right'
                                    testName = nFactory.returnCombinedNameFromDict(d_search)
                                    targets.append(testName)
                                d_constraintParentTargets[i_jnt.getShortName()] = targets

                            if i_mirror.hasAttr('constraintAimTargets') and i_mirror.constraintAimTargets:
                                targets = []
                                for t in i_mirror.constraintAimTargets:
                                    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
                                    if 'cgmDirection' in d_search.keys() and d_search.get('cgmDirection')=='left':d_search['cgmDirection'] = 'right'
                                    testName = nFactory.returnCombinedNameFromDict(d_search)
                                    targets.append(testName)
                                d_constraintAimTargets[i_jnt.getShortName()] = targets

                            if i_mirror.hasAttr('constraintPointTargets') and i_mirror.constraintPointTargets:
                                targets = []
                                for t in i_mirror.constraintPointTargets:
                                    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
                                    if 'cgmDirection' in d_search.keys() and d_search.get('cgmDirection')=='left':d_search['cgmDirection'] = 'right'
                                    testName = nFactory.returnCombinedNameFromDict(d_search)
                                    targets.append(testName)
                                d_constraintPointTargets[i_jnt.getShortName()] = targets	

                            if i_mirror.hasAttr('constraintScaleTargets') and i_mirror.constraintScaleTargets:
                                targets = []
                                for t in i_mirror.constraintScaleTargets:
                                    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
                                    if 'cgmDirection' in d_search.keys() and d_search.get('cgmDirection')=='left':d_search['cgmDirection'] = 'right'
                                    testName = nFactory.returnCombinedNameFromDict(d_search)
                                    targets.append(testName)
                                d_constraintScaleTargets[i_jnt.getShortName()] = targets	

                            if i_mirror.hasAttr('constraintOrientTargets') and i_mirror.constraintOrientTargets:
                                targets = []
                                for t in i_mirror.constraintOrientTargets:
                                    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
                                    if 'cgmDirection' in d_search.keys() and d_search.get('cgmDirection')=='left':d_search['cgmDirection'] = 'right'
                                    testName = nFactory.returnCombinedNameFromDict(d_search)
                                    targets.append(testName)
                                d_constraintOrientTargets[i_jnt.getShortName()] = targets	


                            """
			    #>>> See if we need to grab contraintTargets attr
			    if i_mirror.hasAttr('constraintParentTargets') and i_mirror.constraintParentTargets:
				self.log_info("constraintParentTargets detected, searching to transfer!")
				targets = []
				for t in i_mirror.constraintParentTargets:
				    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
				    if 'cgmDirection' in d_search.keys():d_search['cgmDirection'] = 'right'
				    testName = nFactory.returnCombinedNameFromDict(d_search)
				    if mc.objExists(testName):targets.append(testName)
				d_constraintParentTargets[i] = targets

			    if i_mirror.hasAttr('constraintAimTargets') and i_mirror.constraintAimTargets:
				self.log_info("constraintAimTargets detected, searching to transfer!")
				targets = []
				for t in i_mirror.constraintAimTargets:
				    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
				    if 'cgmDirection' in d_search.keys():d_search['cgmDirection'] = 'right'
				    testName = nFactory.returnCombinedNameFromDict(d_search)
				    targets.append(testName)
				d_constraintAimTargets[i] = targets	

			    if i_mirror.hasAttr('constraintPointTargets') and i_mirror.constraintPointTargets:
				self.log_info("constraintPointTargets detected, searching to transfer!")
				targets = []
				for t in i_mirror.constraintPointTargets:
				    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
				    if 'cgmDirection' in d_search.keys():d_search['cgmDirection'] = 'right'
				    testName = nFactory.returnCombinedNameFromDict(d_search)
				    targets.append(testName)
				d_constraintPointTargets[i] = targets	

			    if i_mirror.hasAttr('constraintScaleTargets') and i_mirror.constraintScaleTargets:
				self.log_info("constraintScaleTargets detected, searching to transfer!")
				targets = []
				for t in i_mirror.constraintScaleTargets:
				    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
				    if 'cgmDirection' in d_search.keys():d_search['cgmDirection'] = 'right'
				    testName = nFactory.returnCombinedNameFromDict(d_search)
				    targets.append(testName)
				d_constraintScaleTargets[i] = targets	

			    if i_mirror.hasAttr('constraintOrientTargets') and i_mirror.constraintOrientTargets:
				self.log_info("constraintOrientTargets detected, searching to transfer!")
				targets = []
				for t in i_mirror.constraintOrientTargets:
				    d_search = nFactory.returnObjectGeneratedNameDict(t.mNode)
				    if 'cgmDirection' in d_search.keys():d_search['cgmDirection'] = 'right'
				    testName = nFactory.returnCombinedNameFromDict(d_search)
				    targets.append(testName)
				d_constraintOrientTargets[i] = targets	
				"""
                        except Exception,error:raise Exception,"Target mirror transfer fail | {0}".format(error)

                    self.l_rightRoots.append(segmentBuffer[0])#Store the root
                    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar
                    segmentBuffers.append(segmentBuffer)#store the segement buffer
                except Exception,error:raise Exception,"root {0} fail | {1}".format(i_root.p_nameShort, error)

        except Exception,error:raise Exception,"actual mirror fail | {0}".format(error)

        p.roots_right = self.l_rightRoots#store the roots to our network	

        #p.addAttr('rightJoints',attrType = 'message',value = self.l_rightJoints,lock=True)
        p.joints_right = self.l_rightJoints


        #>>> 
        #==================     
        try:#Connect constraintParent/Point/Scale/AimTargets when everything is done
            if d_constraintParentTargets:
                for k in d_constraintParentTargets.keys():
                    self.log_info("'%s' targets: %s"%(k,d_constraintParentTargets[k]))
                    i_k = r9Meta.MetaClass(k)
                    i_k.addAttr('constraintParentTargets',attrType='message',value = d_constraintParentTargets[k])
            if d_constraintAimTargets:
                for k in d_constraintAimTargets.keys():
                    self.log_info("'%s' targets: %s"%(k,d_constraintAimTargets[k]))	    
                    i_k = r9Meta.MetaClass(k)
                    i_k.addAttr('constraintAimTargets',attrType='message',value = d_constraintAimTargets[k])
            if d_constraintPointTargets:
                for k in d_constraintPointTargets.keys():
                    self.log_info("'%s' targets: %s"%(k,d_constraintPointTargets[k]))	    	    
                    i_k = r9Meta.MetaClass(k)
                    i_k.addAttr('constraintPointTargets',attrType='message',value = d_constraintPointTargets[k])
            if d_constraintScaleTargets:
                for k in d_constraintScaleTargets.keys():
                    self.log_info("'%s' targets: %s"%(k,d_constraintScaleTargets[k]))	    	    
                    i_k = r9Meta.MetaClass(k)
                    i_k.addAttr('constraintScaleTargets',attrType='message',value = d_constraintScaleTargets[k])
            if d_constraintOrientTargets:
                for k in d_constraintOrientTargets.keys():
                    self.log_info("'%s' targets: %s"%(k,d_constraintOrientTargets[k]))	    	    
                    i_k = r9Meta.MetaClass(k)
                    i_k.addAttr('constraintOrientTargets',attrType='message',value = d_constraintOrientTargets[k]) 
        except Exception,error:raise Exception,"Constraint target transfer fail | {0}".format(error)

    except Exception,error:
        raise StandardError,"_mirrorTemplate_ fail | error: {0}".format(error)




def _rigBody_(self):
    # Get our base info
    #==================	        
    p = self.mi_network
    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(self.mi_network.jointList))
    self.l_skinJoints = []

    mc.select(cl=True)
    i_controlSet = cgmMeta.cgmObjectSet(setName = 'customControls',setType = 'tdSet',qssState=True)#Build us a simple quick select set
    i_controlSetLeft = cgmMeta.cgmObjectSet(setName = 'customControlsLeft',setType = 'tdSet',qssState=True)#Build us a simple quick select set
    i_controlSetRight = cgmMeta.cgmObjectSet(setName = 'customControlsRight',setType = 'tdSet',qssState=True)#Build us a simple quick select set

    for i,i_jnt in enumerate(self.mi_network.jointList):#+ self.mi_network.rightJoints
        try:
            if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                break
            mc.progressBar(mayaMainProgressBar, edit=True, status = "On: '%s'"%i_jnt.getShortName(), step=1)

            """ Only need this if we're gonna constrain rather than skin eyes/ears
	    if i_jnt.cgmName =='ear':#update the group
		if i_jnt.cgmDirection == 'left':
		    p.masterNull.left_earGeoGroup.doCopyTransform(i_jnt.mNode)
		else:
		    p.masterNull.right_earGeoGroup.doCopyTransform(i_jnt.mNode)

	    if i_jnt.cgmName =='eye':#update the group
		if i_jnt.cgmDirection == 'left':
		    p.masterNull.left_eyeGeoGroup.doCopyTransform(i_jnt.mNode)
		else:
		    p.masterNull.right_eyeGeoGroup.doCopyTransform(i_jnt.mNode)
	    """

            if i_jnt.cgmName == 'ankle':
                buffer = updateTransform(i_jnt.controlCurve,i_jnt)	  
                i_jnt.controlCurve = buffer
                i_crv = i_jnt.controlCurve
                i_crv.parent = False
                mc.makeIdentity(i_crv.mNode, apply = True, t=True, r = True, s = True)
                vBuffer = mc.xform(i_crv.mNode,q=True,sp=True,ws=True)	    
                i_crv.scalePivotY = 0
                i_crv.cgmType = 'bodyShaper'
                i_crv.doName()
                i_jnt.doGroup(True)
                i_jnt.parent = i_crv.mNode

                i_controlSet.addObj(i_crv.mNode)#Add to our selection set

                if i_crv.cgmDirection == 'left':
                    i_controlSetLeft.addObj(i_crv.mNode)
                else:
                    i_controlSetRight.addObj(i_crv.mNode)		

            else:
                i_crv = i_jnt.controlCurve
                if i_crv:
                    i_jnt.addAttr('cgmType','bodyShaper',attrType = 'string')
                    curves.parentShapeInPlace(i_jnt.mNode,i_crv.mNode)
                    i_jnt.doName()
                    i_jnt.doGroup(True)	

                    if i_jnt.cgmName in ['hip','neck','head','shoulders','arm','hand','shoulderMeat','upr_leg']:
                        pBuffer = i_jnt.parent
                        if not pBuffer:
                            log.warning("'%s' lacks a parent. It should have one by now"%i_jnt.getShortName())
                            return False
                        i_prnt = cgmMeta.cgmObject(pBuffer)
                        parentPBuffer = i_prnt.parent
                        i_prnt.parent = False
                        if i_jnt.cgmName == 'shoulders':
                            mc.pointConstraint(parentPBuffer,i_prnt.mNode, maintainOffset=True)					    	    
                        else:
                            mc.parentConstraint(parentPBuffer,i_prnt.mNode, maintainOffset=True)
                    '''
		    if i_jnt.cgmName == 'ball':#make a ball loc
			i_loc = i_jnt.doLoc()
			i_loc.parent = i_jnt.mNode
			mc.move(0,2.455,0, [i_loc.mNode],ws=True,relative=True)
			'''
                i_controlSet.addObj(i_jnt.mNode)
                if i_crv.hasAttr('cgmTypeModifier') and i_crv.cgmTypeModifier == 'secondary':
                    i_jnt.addAttr('cgmTypeModifier',attrType='string',value = 'sub')
                if i_jnt.hasAttr('cgmDirection'):
                    if i_jnt.cgmDirection == 'left':
                        i_controlSetLeft.addObj(i_jnt.mNode)
                    elif i_jnt.cgmDirection == 'right':
                        i_controlSetRight.addObj(i_jnt.mNode)		    

            self.l_skinJoints.append(i_jnt)
        except Exception,error:
            raise Exception,"initial loop fail | jnt: {0} | error: {1}".format(i_jnt.p_nameShort,error)
    #Fix Ankles
    iLeft = cgmMeta.cgmObject('l_ankle_bodyShaper')
    iRight = cgmMeta.cgmObject('r_ankle_bodyShaper')
    iLeft.doStore('cgmMirrorMatch',iRight.mNode)
    iRight.doStore('cgmMirrorMatch',iLeft.mNode)

    #Store sets
    self.mi_network.objSet_all = i_controlSet.mNode
    self.mi_network.objSet_left = i_controlSetLeft.mNode
    self.mi_network.objSet_right = i_controlSetRight.mNode

    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
    self.mi_network.controlsLeft = i_controlSetLeft.value
    self.mi_network.controlsRight = i_controlSetRight.value

def _setupConstraints_(self):
    l_aimJoints = []
    for i,i_jnt in enumerate(self.mi_network.jointList):
        constraintTypes = []
        constraintTargets = {}
        aimTargets = []
        aim_ijnt = False
        str_cgmName = i_jnt.cgmName
        #Gather the info to set stuff up
        if i_jnt.hasAttr('constraintScaleTargets'):
            constraintTypes.append('scale')
            constraintTargets['scale'] = i_jnt.getMessage('constraintScaleTargets',False)	
        if i_jnt.hasAttr('constraintParentTargets'):
            constraintTypes.append('parent')
            #if 'scale' not in constraintTypes:
                #constraintTypes.append('scale')#parent type needs scale
                #constraintTargets['scale'] = i_jnt.getMessage('constraintParentTargets',False)			
            constraintTargets['parent'] = i_jnt.getMessage('constraintParentTargets',False)	    
        if i_jnt.hasAttr('constraintPointTargets'):
            constraintTypes.append('point')	    
            constraintTargets['point'] = i_jnt.getMessage('constraintPointTargets',False)
        if i_jnt.hasAttr('constraintOrientTargets'):
            constraintTypes.append('orient')	    
            constraintTargets['orient'] = i_jnt.getMessage('constraintOrientTargets',False)

        if i_jnt.hasAttr('constraintAimTargets'):
            l_aimJoints.append(i_jnt)
            #aimTargets = i_jnt.getMessage('constraintAimTargets',False)

        if constraintTypes:
            log.info("'{0}' constraint list: {1}".format(i_jnt.getShortName(), constraintTypes))

            #if 'aim' in constraintTypes and aimTargets:
                #aim_ijnt = True
                #constraintTypes.remove('aim')

            if constraintTypes and constraintTargets:
                #Need to pair through to see when constraints can be setup together
                constraintPairs = []
                cullList = copy.copy(constraintTypes)
                while cullList:
                    for C in cullList:
                        pairBuffer = []
                        cTargets = constraintTargets.get(C)	
                        for c in constraintTypes:
                            if cTargets == constraintTargets.get(c):
                                pairBuffer.append(c)
                                cullList.remove(c)
                        constraintPairs.append(pairBuffer)

                log.info("constraintPairs: %s"%constraintPairs)   
                for pair in constraintPairs:
                    targets = constraintTargets.get(pair[0])
                    log.info("%s targets: %s"%(pair, targets))
                    pBuffer = i_jnt.parent
                    i_prnt = cgmMeta.cgmObject(pBuffer)
                    i_prnt.addAttr('cgmTypeModifier','%sConstraint'%('_'.join(pair)),'string')	    
                    #parentPBuffer = i_prnt.parent
                    #i_prnt.parent = False
                    i_prnt.doName()	
                    """
		    if i_jnt.hasAttr('constraintAimTargets'):
			mode = 0
		    else:
			mode = 1
			"""
                    mode = 0
                    if 'scale' in pair and str_cgmName in ['eyeOrb','mouth','noseBase']:
                        pair.remove('scale')
                        driverAttr = 'scaleX'
                        l_driverAttrs = []
                        for obj in targets:
                            l_driverAttrs.append("{0}.{1}".format(obj,driverAttr))
                        rUtils.connect_singleDriverAttrToMulti("{0}.scale".format(i_prnt.mNode) ,l_driverAttrs)			

                    if i_jnt.controlPart == 'face':
                        constraints.doConstraintObjectGroup(targets,group = i_prnt.mNode,constraintTypes=pair,mode=0)		                        
                        #i_prnt.parent = parentPBuffer
                    else:
                        i_prnt.parent = False			
                        constraints.doConstraintObjectGroup(targets,group = i_prnt.mNode,constraintTypes=pair,mode=mode)		

    if l_aimJoints:
        for i_jnt in l_aimJoints:
            if i_jnt.cgmName == 'ankleMeat':
                if i_jnt.cgmDirection == 'left':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = [0,1,0], upVector = [0,0,1], worldUpVector = [0,0,-1], worldUpType = 'vector' )    		
                elif i_jnt.cgmDirection == 'right':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = [0,-1,0], upVector = [0,0,-1], worldUpVector = [0,0,-1], worldUpType = 'vector' )    			    


            elif i_jnt.controlPart == 'face':
                """
                a  = cgmMeta.cgmObject()
                a.doGroup(True)
                i_jnt.doGroup(True)
                """
                if i_jnt.hasAttr('cgmDirection') and i_jnt.cgmDirection == 'left':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = True, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = [0,1,0], worldUpType = 'vector' )    
                elif i_jnt.hasAttr('cgmDirection') and i_jnt.cgmDirection == 'right':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = True, weight = 1, aimVector = [0,0,-1], upVector = [0,-1,0], worldUpVector = [0,1,0], worldUpType = 'vector' )    		
            else:
                if i_jnt.cgmDirection == 'left':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = [0,0,1], worldUpType = 'vector' )    
                elif i_jnt.cgmDirection == 'right':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,-1,0], worldUpVector = [0,0,1], worldUpType = 'vector' )    

            attributes.doSetLockHideKeyableAttr(i_jnt.mNode,channels = ['rx','ry','rz'])		
    mc.delete('controlCurves')




def _skinBody_(self):
    p = self.mi_network
    #Get skin joints

    if not self.l_skinJoints:
        self.log_warning("No skin joints found!")
        return False	
        #if not returnSkinJoints(self):
            #log.error("No skinJoints found")

    l_skinJoints = []
    i_jntEyeLeft = False
    i_jntEyeRight = False
    i_jntEarLeft = False
    i_jntEarRight = False

    for i_jnt in self.l_skinJoints:
        if i_jnt.cgmName not in ['ear']:
            l_skinJoints.append(i_jnt.mNode)
        if i_jnt.cgmName == 'ear':
            if i_jnt.cgmDirection == 'left':
                i_jntEarLeft = i_jnt
            else:
                i_jntEarRight = i_jnt		
        elif i_jnt.cgmName == 'eye':
            if i_jnt.cgmDirection == 'left':
                i_jntEyeLeft = i_jnt
            else:
                i_jntEyeRight = i_jnt
        elif i_jnt.cgmName == 'mouthCavity':
            mJnt_mouthCavity = i_jnt


    d_skinJoints = {'body':l_skinJoints,
                    'tongue':[mJnt_mouthCavity.mNode],
                    'uprTeeth':[mJnt_mouthCavity.mNode],
                    'lwrTeeth':[mJnt_mouthCavity.mNode],
                    'earLeft':[i_jntEarLeft.mNode],
                    'earRight':[i_jntEarRight.mNode],
                    'eyeLeft':[i_jntEyeLeft.mNode],
                    'eyeRight':[i_jntEyeRight.mNode]}	

    #>>> Main skin 
    #> Gather geo and skin
    for key in d_skinJoints.keys():
        try:
            log.info("Working to skin: {0}".format(key))
            if key == 'body':
                l_toSkin = [self.md_coreGeo['unified']['mi_base'].mNode,
                            self.md_coreGeo['head']['mi_base'].mNode]
            else:
                l_toSkin = self.d_skinTargets[key]
            if not l_toSkin:
                raise ValueError,"No skin targets found!"
            if not d_skinJoints.get(key):
                raise ValueError,"No skin joints"	    
            else:
                for geo in l_toSkin:
                    self.log_info("Skinning: '{0}'".format(geo))
                    toBind = d_skinJoints[key] + [geo]#...combine
                    cluster = mc.skinCluster(toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
                    mi_cluster = cgmMeta.cgmNode(cluster[0])
                    if key == 'body':
                        pass
                    else:
                        mi_cluster.doCopyNameTagsFromObject(self.md_geoGroups[key].mNode,ignore=['cgmTypeModifier','cgmType'])
                    mi_cluster.addAttr('mClass','cgmNode',attrType='string',lock=True)
                    mi_cluster.doName()
        except Exception,error:raise Exception,"Skinning {0} fail! | {1}".format(key,error)	
        
        try:
            unified_base = self.md_coreGeo['unified']['mi_base'].mNode
            l_geo =  self.d_skinTargets.get('hair') or []
            for g in l_geo:
                #Wrap
                
                skinWeights.transferSkinning( unified_base, g )
                cgmMeta.cgmNode(g).doStore('skinMaster',unified_base)
                self.log_info("Skinning: '{0}'".format(g))
                
        except Exception,error:raise Exception,"Skin hair stuff | {1}".format(error)	        

def _setupWraps_(self):
    p = self.mi_network

    #>>> Main skin 
    #> Gather geo and skin
    l_wrapKeys = ['eyebrow','clothes']
    for key in l_wrapKeys:
        try:
            l_geo = self.d_skinTargets.get(key) or []

            for g in l_geo:
                #Wrap
                self.log_info("Wrapping: '{0}'".format(g))
                deformers.wrapDeformObject(g, self.md_coreGeo['unified']['mi_base'].mNode)
        except Exception,error:raise Exception,"{0} | {1}".format(key,error)		

def _connectVis_(self):
    p = self.mi_network
    iVis = p.masterControl.controlVis
    for c in self.mi_network.objSet_all.value:
        if '.' not in c:
            i_c = cgmMeta.cgmNode(c)
            i_attr = cgmMeta.cgmAttr(i_c,'visibility',hidden = True,lock = True)

            if i_c.hasAttr('cgmTypeModifier') and i_c.cgmTypeModifier == 'sub':
                if i_c.hasAttr('cgmDirection'):
                    if i_c.cgmDirection == 'left':
                        i_attr.doConnectIn("%s.leftSubControls_out"%iVis.mNode)
                    if i_c.cgmDirection == 'right':
                        i_attr.doConnectIn("%s.rightSubControls_out"%iVis.mNode)
                else:
                    i_attr.doConnectIn("%s.subControls_out"%iVis.mNode)

            else:
                if i_c.hasAttr('cgmDirection'):
                    if i_c.cgmDirection == 'left':
                        i_attr.doConnectIn("%s.leftControls_out"%iVis.mNode)
                    if i_c.cgmDirection == 'right':
                        i_attr.doConnectIn("%s.rightControls_out"%iVis.mNode)
                else:
                    i_attr.doConnectIn("%s.controls"%iVis.mNode)


#>>>GEO Stuff
def _check_resetAndBridgeGeo_(self):
    """ 
    Checks the reset and Bridge geo exists. Creates it if not.
    """ 
    # Get our base info
    #==================	        
    log.info(">>> go._check_resetAndBridgeGeo_") 
    p = self.mi_network

    #>>> Check Resetter
    #=================================================
    for k in _d_main_geoInfo.keys():
        _d = _d_main_geoInfo[k]
        try:
            try:
                _bfr = p.getMessage(_d['msg_reset'])
                if _bfr:
                    log.info('{0} Reset Geo exists!'.format(k))
                else:
                    mi_newMesh = self.md_coreGeo[k]['mi_base'].doDuplicate(False)
                    self.md_coreGeo[k]['mi_reset'] = mi_newMesh
                    mi_newMesh.addAttr('cgmName',k,attrType='string',lock=True)
                    mi_newMesh.addAttr('cgmTypeModifier','DONOTTOUCH_RESET',attrType='string',lock=True)                    
                    mi_newMesh.doName()
                    mi_newMesh.parent =  p.masterNull.bsGeoGroup
                    
                    p.doStore(_d['msg_reset'],mi_newMesh.mNode)
                    
                    mi_newMesh.v = False
                    log.info('{0} Reset Geo created!'.format(k))     
            except Exception,error:
                raise Exception,"!Reset Check!| {1}".format(error)
            
            try:
                _bfr = p.getMessage(_d['msg_bridge'])
                if _bfr:
                    log.info('{0} Bridge Geo exists!'.format(k))
                else:
                    mi_newMesh = self.md_coreGeo[k]['mi_base'].doDuplicate(False)
                    self.md_coreGeo[k]['mi_bridge'] = mi_newMesh
                    mi_newMesh.addAttr('cgmName', k,attrType='string',lock=True)
                    mi_newMesh.addAttr('cgmTypeModifier','bsBridge',lock = True)
                    mi_newMesh.doName()
                    mi_newMesh.parent =  p.masterNull.bsGeoGroup
                    
                    p.doStore(_d['msg_bridge'],mi_newMesh.mNode)
                    mi_newMesh.v = False
                    
                    log.info('{0} Bridge Geo created!'.format(k))     
            except Exception,error:
                raise Exception,"!Bridge Check!| {1}".format(error)            
        except Exception,error:
            raise Exception,"Failed on {0} | {1}".format(k,error)
        
def _rigBlocks_(self):
    """ 
    Checks the reset and Bridge geo exists. Creates it if not.
    """ 
    # Get our base info
    #==================	        
    log.info(">>> go._rigBlocks_") 
    d_joints = {}
    for i_jnt in self.l_skinJoints:
        tag_name = i_jnt.cgmName
        if tag_name == 'eye':
            if i_jnt.cgmDirection == 'left':
                d_joints['eye_left'] = i_jnt
            else:
                d_joints['eye_right'] = i_jnt
        elif tag_name == 'head':
            d_joints['head'] = i_jnt
        elif tag_name == 'mouthCavity':
            d_joints['mouthCavity'] = i_jnt
        elif tag_name == 'brow':
            d_joints['brow'] = i_jnt
             
    mi_template = self.mi_simpleFaceModule.templateNull
    mi_template.rigBlock_eye_left.parent = d_joints['eye_left']
    mi_template.rigBlock_eye_right.parent = d_joints['eye_right']
    mi_template.rigBlock_face_upr.parent = d_joints['brow']
    mi_template.rigBlock_face_lwr.parent = d_joints['mouthCavity']
    
    mi_template.rigBlock_eye_left.v = False
    mi_template.rigBlock_eye_right.v = False
    mi_template.rigBlock_face_upr.v = False
    mi_template.rigBlock_face_lwr.v = False  
    
    

    return
    #>>> Check Resetter
    #=================================================
    for k in _d_main_geoInfo.keys():
        _d = _d_main_geoInfo[k]
        try:
            try:
                _bfr = p.getMessage(_d['msg_reset'])
                if _bfr:
                    log.info('{0} Reset Geo exists!'.format(k))
                else:
                    mi_newMesh = self.md_coreGeo[k]['mi_base'].doDuplicate(False)
                    self.md_coreGeo[k]['mi_reset'] = mi_newMesh
                    mi_newMesh.addAttr('cgmName',k,attrType='string',lock=True)
                    mi_newMesh.addAttr('cgmTypeModifier','DONOTTOUCH_RESET',attrType='string',lock=True)                    
                    mi_newMesh.doName()
                    mi_newMesh.parent =  p.masterNull.bsGeoGroup
                    
                    p.doStore(_d['msg_reset'],mi_newMesh.mNode)
                    
                    mi_newMesh.v = False
                    log.info('{0} Reset Geo created!'.format(k))     
            except Exception,error:
                raise Exception,"!Reset Check!| {1}".format(error)
            
            try:
                _bfr = p.getMessage(_d['msg_bridge'])
                if _bfr:
                    log.info('{0} Bridge Geo exists!'.format(k))
                else:
                    mi_newMesh = self.md_coreGeo[k]['mi_base'].doDuplicate(False)
                    self.md_coreGeo[k]['mi_bridge'] = mi_newMesh
                    mi_newMesh.addAttr('cgmName', k,attrType='string',lock=True)
                    mi_newMesh.addAttr('cgmTypeModifier','bsBridge',lock = True)
                    mi_newMesh.doName()
                    mi_newMesh.parent =  p.masterNull.bsGeoGroup
                    
                    p.doStore(_d['msg_bridge'],mi_newMesh.mNode)
                    mi_newMesh.v = False
                    
                    log.info('{0} Bridge Geo created!'.format(k))     
            except Exception,error:
                raise Exception,"!Bridge Check!| {1}".format(error)            
        except Exception,error:
            raise Exception,"Failed on {0} | {1}".format(k,error)    
        
def _bs_bridge_(self):
    """ 
    Sets up main,face and body blendshape bridges
    """ 
    # Get our base info
    #==================	        
    log.info(">>> go.doBridge_bsNode") 
    p = self.mi_network
    l_targets = []  
    
    try:#>>> Facewrap geo bridge (shape pushed back into main bridge from wrapped unified geo to face)
        #=================================================
        #1) dup unified
        #2) wrap to head
        #3) add to body blendshape
        self.log_info('Facewrap bridge setup')
        bridgeFaceBlendshapeNode = p.getMessage('bsNode_bridgeFace')
        bridgeFace= p.getMessage('geo_bridgeHead')
    
        if not bridgeFace:
            raise ValueError,"Should have 'geo_bridgeHead'" 
        if not bridgeFaceBlendshapeNode:
            raise ValueError,"Should have a 'bsNode_bridgeFace'"
        
        try:#create and connect
            _d = self.md_coreGeo['unified']
            mi_newMesh = self.md_coreGeo['unified']['mi_reset'].doDuplicate(False)#....dup
            _d['mi_faceWrapBridge'] = mi_newMesh
            mi_newMesh.addAttr('cgmTypeModifier','faceWrapBridge',attrType='string',lock=True)                    
            mi_newMesh.doName()
            mi_newMesh.parent =  p.masterNull.bsGeoGroup
            p.doStore('geo_unifiedHeadWrapBridge',mi_newMesh.mNode)  
            mi_newMesh.v = False
        except Exception,error:
            raise Exception,"Create fail | {0}".format(error)    
        
        try:#wrap
            deformers.wrapDeformObject(mi_newMesh.mNode, bridgeFace)
        except Exception,error:
            raise Exception,"wrap fail | {0}".format(error)          
    except Exception,error:
        raise Exception,"Facewrap bridge fail | {0}".format(error)  
    
    try:#>>> Check Main bridge
        #=================================================
        bridgeMainBlendshapeNode = p.getMessage('bsNode_bridgeMain')
        mi_bridgeBody = p.getMessageAsMeta('geo_bridgeUnified')
    
        if bridgeMainBlendshapeNode and mi_bridgeBody:#if we have one, we're good to go
            log.info('Main Bridge exists!')
        else:
            try:
                #Blendshape	
                bsNode_unified = deformers.buildBlendShapeNode( self.md_coreGeo['unified']['mi_base'].mNode,
                                                                [mi_bridgeBody.mNode, mi_newMesh.mNode],'tmp')
                mi_bsNode = cgmMeta.validateObjArg(bsNode_unified,'cgmNode',setClass = True)
                mi_bsNode.addAttr('cgmName','unifiedBridge',attrType='string',lock=True)    
                mi_bsNode.doName()
                p.bsNode_bridgeMain = mi_bsNode.mNode	
                log.info('Unified Bridge good!')
            except Exception,error:
                self.log_warning('miBase: {0}'.format( self.md_coreGeo['unified']['mi_base']))
                #self.log_warning('mi_bridgeBody: {0}'.format( mi_bridgeBody))            
                raise Exception,"build fail | {0}".format(error) 
            
        attrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
        for a in attrs:
            self.log_info("Setting: {0}".format(a))
            attributes.doSetAttr(mi_bsNode.mNode,a,1)#...turn it on the bridge targets            
    except Exception,error:
        raise Exception,"Unified bridge fail | {0}".format(error) 
    
    try:#>>> Set the correct weights on the unified bridge facewrap target to keep it from pushing over
        #=================================================
        self.log_info('Facewrap bridge blendshapeNode setup')        
        try:#clear 
            str_unified = self.md_coreGeo['unified']['mi_base'].mNode
            str_unifedBSNode = mi_bsNode.mNode
            str_head =  self.md_coreGeo['head']['mi_base'].mNode
            vtx_max = mc.polyEvaluate(str_unified,v=True)
            for i,vtx in enumerate(range(0,vtx_max)):
                self.progressBar_set( status = "Clearing {0}".format(i), progress = i, maxValue = vtx_max)		    				    		    		                    
                mc.setAttr('{0}.inputTarget[0].inputTargetGroup[1].targetWeights[{1}]'.format(str_unifedBSNode,vtx),0.0)  
        except Exception,error:
            raise Exception,"clear fail | {0}".format(error)  
        
        try:#clear 
            vtx_max = mc.polyEvaluate(str_head,v=True)
            
            for i,vtx in enumerate(range(0,vtx_max)):
                self.progressBar_set( status = "Setting {0}".format(i), progress = i, maxValue = vtx_max)		    				    		    		                                    
                pos = distance.returnWorldSpacePosition('{0}.vtx[{1}]'.format(str_head,vtx))
                val = distance.returnClosestPointOnMeshInfoFromPos(pos,str_unified)['closestVertexIndex']
                mc.setAttr('{0}.inputTarget[0].inputTargetGroup[1].targetWeights[{1}]'.format(str_unifedBSNode,val),1.0)  
        except Exception,error:
            raise Exception,"set fail | {0}".format(error)              
    except Exception,error:
        raise Exception,"facewrap target weights per vertex | {0}".format(error)       
    return True
    
    try:#>>> Setup the bridge blendshape node
        #=================================================
        self.log_info('Facewrap bridge blendshapeNode setup')        
        try:#create 
            #Blendshape	
            bsNode_unified = deformers.buildBlendShapeNode( mi_bridgeBody.mNode,[mi_newMesh.mNode],'tmp')
            mi_bsNode = cgmMeta.validateObjArg(bsNode_unified,'cgmNode',setClass = True)
            mi_bsNode.addAttr('cgmName','bodyBridge',attrType='string',lock=True)    
            mi_bsNode.doName()
            attributes.doSetAttr(mi_bsNode.mNode,mi_newMesh.getShortName(),1)
            p.bsNode_bridgeBody = mi_bsNode.mNode	
            log.info('Body Bridge good!')
        except Exception,error:
            raise Exception,"Create fail | {0}".format(error)    
                
    except Exception,error:
        raise Exception,"bridge bsNode fail | {0}".format(error)       

    """#Blendshape	
    bsNode = deformers.buildBlendShapeNode(p.bridgeMainGeo,l_targets,'tmp')

    i_bsNode = cgmMeta.cgmNode(bsNode)
    i_bsNode.addAttr('cgmName','bridgeTargets',attrType='string',lock=True)    
    i_bsNode.addAttr('mClass','cgmNode',attrType='string',lock=True)
    i_bsNode.doName()
    attributes.doSetAttr(i_bsNode.mNode,i_target.getShortName(),1)#Turn it on	

    attrs = deformers.returnBlendShapeAttributes(i_bsNode.mNode)
    for a in attrs:
        self.log_info(a)
        attributes.doSetAttr(i_bsNode.mNode,a,1)#Turn it on	the bridge targets
    log.info('Bridge good!')

    return True       

    #>>> Check Face Bridge
    #================================================= 
    '''
    Make sure we have a faceBridge, create and connect 
    '''
    bridgeFaceBlendshapeNode = p.getMessage('bsNode_bridgeFace')
    bridgeFace= p.getMessage('geo_bridgeHead')

    if not bridgeFace:
        raise ValueError,"Should have geo_bridgeHead"
    
    try:#Create a bridge for the facial stuff to be wrapped to
        _d = self.md_coreGeo['unified']
        mi_newMesh = self.md_coreGeo['unified']['mi_reset'].doDuplicate(False)
        _d['mi_faceWrapBridge'] = mi_newMesh
        mi_newMesh.addAttr('cgmTypeModifier','faceWrapBridge',attrType='string',lock=True)                    
        mi_newMesh.doName()
        mi_newMesh.parent =  p.masterNull.bsGeoGroup
        p.doStore(_d['msg_reset'],mi_newMesh.mNode)  
        mi_newMesh.v = False
    except Exception,error:
        self.log_warning('miBase: {0}'.format( self.md_coreGeo['unified']['mi_base']))
        self.log_warning('mi_bridgeBody: {0}'.format( mi_bridgeBody))            
        raise Exception,"Face wrap bridge fail | {0}".format(error)        
    #Connect add that to the list of the blendshapes for the unified bsNOde
    #Create that unified bsNode
    #Weighting so only the face is affected


    l_targets.extend(p.getMessage('bridgeFaceGeo'))
    
    return

    #>>> Check Body Bridge
    #================================================= 
    bridgeBodyBlendshapeNode = p.getMessage('bsNode_bridgeBody')

    if not p.getMessage('bridgeBodyGeo'):
        newMesh = mc.duplicate(geo_unified)
        i_target = cgmMeta.cgmObject(newMesh[0])
        i_target.addAttr('cgmName','bodyBridge',attrType='string',lock=True)
        i_target.doName()
        i_target.parent = p.masterNull.bsGeoGroup.mNode#parent it
        p.bridgeBodyGeo = i_target.mNode
        i_target.visibility = False

    l_targets.extend(p.getMessage('bridgeBodyGeo'))



    #Blendshape	
    bsNode = deformers.buildBlendShapeNode(p.bridgeMainGeo,l_targets,'tmp')

    i_bsNode = cgmMeta.cgmNode(bsNode)
    i_bsNode.addAttr('cgmName','bridgeTargets',attrType='string',lock=True)    
    i_bsNode.addAttr('mClass','cgmNode',attrType='string',lock=True)
    i_bsNode.doName()
    attributes.doSetAttr(i_bsNode.mNode,i_target.getShortName(),1)#Turn it on	

    attrs = deformers.returnBlendShapeAttributes(i_bsNode.mNode)
    for a in attrs:
        self.log_info(a)
        attributes.doSetAttr(i_bsNode.mNode,a,1)#Turn it on	the bridge targets
    log.info('Bridge good!')

    return True    """

def _bs_body_(self):
    """ 
    Sets up body blendshapes
    """ 
    # Get our base info
    #==================	        
    log.info(">>> go._bs_body_") 
    p = self.mi_network
    geo_unified = self.mi_geo_unified.mNode 
    l_targets = self.d_bsGeoTargets['body']

    if not l_targets:
        log.error("No geo found")
        return False

    str_bridge = p.getMessage('bridgeBodyGeo')
    if not str_bridge:
        log.error("No body bridge geo found")
        return False
    str_bridge = str_bridge[0]

    bsNode = deformers.buildBlendShapeNode(str_bridge,l_targets,'tmp')

    i_bsNode = cgmMeta.cgmNode(bsNode)
    i_bsNode.addAttr('cgmName','body',attrType='string',lock=True)    
    i_bsNode.addAttr('mClass','cgmNode',attrType='string',lock=True)
    #i_bsNode.addAttr('targetsGroup',targetGeoGroup,attrType='messageSimple',lock=True)

    i_bsNode.doName()
    p.bodyBlendshapeNodes = i_bsNode.mNode

    #Add these to our obj set as well as the bsNode
    p.objSet_all.addObj(i_bsNode.mNode)
    attrs = deformers.returnBlendShapeAttributes(i_bsNode.mNode)
    for a in attrs:
        p.objSet_all.addObj("{0}.{1}".format(i_bsNode.mNode,a))

def _bs_face_(self):
    """ 
    Sets up face blendshapes
    """ 
    # Get our base info
    #==================	        
    log.info(">>> go._bs_face_") 
    p = self.mi_network
    geo_unified = self.mi_geo_unified.mNode 
    l_targets = self.d_bsGeoTargets['face']

    if not l_targets:
        log.error("No geo found")
        return False

    str_bridge = p.getMessage('bridgeFaceGeo')

    if not str_bridge:
        log.error("No face bridge geo found")
        return False
    str_bridge = str_bridge[0]

    bsNode = deformers.buildBlendShapeNode(str_bridge,l_targets,'tmp')

    i_bsNode = cgmMeta.cgmNode(bsNode)
    i_bsNode.addAttr('cgmName','face',attrType='string',lock=True)    
    i_bsNode.addAttr('mClass','cgmNode',attrType='string',lock=True)
    #i_bsNode.addAttr('targetsGroup',targetGeoGroup,attrType='messageSimple',lock=True)

    i_bsNode.doName()
    p.faceBlendshapeNodes = i_bsNode.mNode

    #Add these to our obj set as well as the bsNode
    p.objSet_all.addObj(i_bsNode.mNode)
    attrs = deformers.returnBlendShapeAttributes(i_bsNode.mNode)
    for a in attrs:
        p.objSet_all.addObj("{0}.{1}".format(i_bsNode.mNode,a))


@r9General.Timer
def returnSkinJoints(self):
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    log.info(">>> go.returnSkinJoints")  
    l_skinJoints  = ['pelvis_body_shaper']
    l_skinJoints.extend( search.returnChildrenJoints(l_skinJoints[0]) )
    log.info (l_skinJoints)
    self.l_skinJoints = l_skinJoints
    return l_skinJoints  


def doAddControlConstraints(self):
    """ 
    Segement orienter. Must have a JointFactory Instance
    """ 
    log.info(">>> doRigBody")
    # Get our base info
    #==================	        
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    l_aimJoints = []
    for i,i_jnt in enumerate(self.p.jointList):
        constraintTypes = []
        constraintTargets = {}
        aimTargets = []
        aim_ijnt = False
        #Gather the info to set stuff up
        if i_jnt.hasAttr('constraintScaleTargets'):
            constraintTypes.append('scale')
            constraintTargets['scale'] = i_jnt.getMessage('constraintScaleTargets',False)	
        if i_jnt.hasAttr('constraintParentTargets'):
            constraintTypes.append('parent')
            #if 'scale' not in constraintTypes:
                #constraintTypes.append('scale')#parent type needs scale
                #constraintTargets['scale'] = i_jnt.getMessage('constraintParentTargets',False)			
            constraintTargets['parent'] = i_jnt.getMessage('constraintParentTargets',False)	    
        if i_jnt.hasAttr('constraintPointTargets'):
            constraintTypes.append('point')	    
            constraintTargets['point'] = i_jnt.getMessage('constraintPointTargets',False)
        if i_jnt.hasAttr('constraintOrientTargets'):
            constraintTypes.append('orient')	    
            constraintTargets['orient'] = i_jnt.getMessage('constraintOrientTargets',False)

        if i_jnt.hasAttr('constraintAimTargets'):
            l_aimJoints.append(i_jnt)
            #aimTargets = i_jnt.getMessage('constraintAimTargets',False)

        if constraintTypes:
            log.info("'%s' constraint list: %s"%(i_jnt.getShortName(), constraintTypes))

            #if 'aim' in constraintTypes and aimTargets:
                #aim_ijnt = True
                #constraintTypes.remove('aim')

            if constraintTypes and constraintTargets:
                #Need to pair through to see when constraints can be setup together
                constraintPairs = []
                cullList = copy.copy(constraintTypes)
                while cullList:
                    for C in cullList:
                        pairBuffer = []
                        cTargets = constraintTargets.get(C)	
                        for c in constraintTypes:
                            if cTargets == constraintTargets.get(c):
                                pairBuffer.append(c)
                                cullList.remove(c)
                        constraintPairs.append(pairBuffer)

                log.info("constraintPairs: %s"%constraintPairs)   
                for pair in constraintPairs:
                    targets = constraintTargets.get(pair[0])
                    log.info("%s targets: %s"%(pair, targets))
                    pBuffer = i_jnt.parent
                    i_prnt = cgmMeta.cgmObject(pBuffer)
                    i_prnt.addAttr('cgmTypeModifier','%sConstraint'%('_'.join(pair)),'string')	    
                    parentPBuffer = i_prnt.parent
                    i_prnt.parent = False
                    i_prnt.doName()	
                    """
		    if i_jnt.hasAttr('constraintAimTargets'):
			mode = 0
		    else:
			mode = 1
			"""
                    mode = 0
                    if i_jnt.controlPart == 'face':
                        constraints.doConstraintObjectGroup(targets,group = i_prnt.mNode,constraintTypes=pair,mode=1)		                        
                        i_prnt.parent = parentPBuffer
                    else:
                        constraints.doConstraintObjectGroup(targets,group = i_prnt.mNode,constraintTypes=pair,mode=mode)		

    if l_aimJoints:
        for i_jnt in l_aimJoints:
            if i_jnt.cgmName == 'ankleMeat':
                if i_jnt.cgmDirection == 'left':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = [0,1,0], upVector = [0,0,1], worldUpVector = [0,0,-1], worldUpType = 'vector' )    		
                elif i_jnt.cgmDirection == 'right':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = [0,-1,0], upVector = [0,0,-1], worldUpVector = [0,0,-1], worldUpType = 'vector' )    			    


            elif i_jnt.controlPart == 'face':
                """
                a  = cgmMeta.cgmObject()
                a.doGroup(True)
                i_jnt.doGroup(True)
                """
                if i_jnt.hasAttr('cgmDirection') and i_jnt.cgmDirection == 'left':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = True, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = [0,1,0], worldUpType = 'vector' )    
                elif i_jnt.hasAttr('cgmDirection') and i_jnt.cgmDirection == 'right':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = True, weight = 1, aimVector = [0,0,-1], upVector = [0,-1,0], worldUpVector = [0,1,0], worldUpType = 'vector' )    		
            else:
                if i_jnt.cgmDirection == 'left':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,1], upVector = [0,1,0], worldUpVector = [0,0,1], worldUpType = 'vector' )    
                elif i_jnt.cgmDirection == 'right':
                    constBuffer = mc.aimConstraint( i_jnt.getMessage('constraintAimTargets',False),i_jnt.mNode,maintainOffset = False, weight = 1, aimVector = [0,0,-1], upVector = [0,-1,0], worldUpVector = [0,0,1], worldUpType = 'vector' )    

            attributes.doSetLockHideKeyableAttr(i_jnt.mNode,channels = ['rx','ry','rz'])		


    mc.delete('controlCurves')

def doConnectVis(self):
    log.info(">>> doConnectVis")
    # Get our base info
    #==================	        
    assert self.cls == 'CustomizationFactory.go',"Not a CustomizationFactory.go instance!"
    assert mc.objExists(self.p.mNode),"Customization node no longer exists"
    p = self.p

    iVis = p.masterControl.controlVis

    for c in self.p.objSet_all.value:
        if '.' not in c:
            i_c = cgmMeta.cgmNode(c)
            i_attr = cgmMeta.cgmAttr(i_c,'visibility',hidden = True,lock = True)

            if i_c.hasAttr('cgmTypeModifier') and i_c.cgmTypeModifier == 'sub':
                if i_c.hasAttr('cgmDirection'):
                    if i_c.cgmDirection == 'left':
                        i_attr.doConnectIn("%s.leftSubControls_out"%iVis.mNode)
                    if i_c.cgmDirection == 'right':
                        i_attr.doConnectIn("%s.rightSubControls_out"%iVis.mNode)
                else:
                    i_attr.doConnectIn("%s.subControls_out"%iVis.mNode)

            else:
                if i_c.hasAttr('cgmDirection'):
                    if i_c.cgmDirection == 'left':
                        i_attr.doConnectIn("%s.leftControls_out"%iVis.mNode)
                    if i_c.cgmDirection == 'right':
                        i_attr.doConnectIn("%s.rightControls_out"%iVis.mNode)
                else:
                    i_attr.doConnectIn("%s.controls"%iVis.mNode)

def doLockNHide(self, customizationNode = 'MorpheusCustomization', unlock = False):
    """
    Lock and hides for a Morpheus customization asset
    """
    log.info(">>> doLockNHide")
    # Get our base info
    #==================	        
    try:
        customizationNode.mNode
        p = customizationNode
    except:
        if mc.objExists(customizationNode):
            p = r9Meta.MetaClass(customizationNode)
        else:
            p = cgmPM.cgmMorpheusMakerNetwork(name = customizationNode)

    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(len(self.mi_network.objSet_all.value))    
    for c in self.mi_network.objSet_all.value:        
        if '.' not in c and mc.ls(c, type='transform'):
            i_c = cgmMeta.cgmNode(c)
            if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
                break
            mc.progressBar(mayaMainProgressBar, edit=True, status = "LockNHide: '%s'"%i_c.getShortName(), step=1)            

            if unlock:
                for c in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
                    cgmMeta.cgmAttr(i_c,c,lock=False,keyable=True,hidden=False)

                if i_c.hasAttr('radius'):
                    cgmMeta.cgmAttr(i_c,'radius',value = 5, hidden = False, keyable = False)
                    i_c.drawStyle = 0
            elif i_c.hasAttr('cgmName'):
                #Special Stuff
                str_name = i_c.cgmName
                if str_name in ['arm','head','face','eye','eyeOrb']:
                    attributes.doConnectAttr(('%s.scaleZ'%i_c.mNode),('%s.scaleX'%i_c.mNode),True)
                    attributes.doConnectAttr(('%s.scaleZ'%i_c.mNode),('%s.scaleY'%i_c.mNode),True)
                    cgmMeta.cgmAttr(i_c,'scaleX',lock=True,hidden=True)
                    cgmMeta.cgmAttr(i_c,'scaleY',lock=True,hidden=True)		    
                    zAttr = cgmMeta.cgmAttr(i_c,'scaleZ')
                    zAttr.p_nameAlias = '%sScale'%str_name                    
                    i_c.rotateOrder = 5#This is to fix a bug happening on scale cycle error

                #>>>All translates/rotates
                if str_name in ['ankleMeat','kneeMeat','hipMeat','arm','shoulderMeat','head','face']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['tx','ty','tz','rx','ry','rz'])                 


                #>>> Translates ==================================================== 
                #>>> all
                if str_name in ['upr_arm']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['tx','ty','tz'])	 		
                #>>> tx
                if str_name in ['quad','hamstring','lwr_leg','torsoMid','pelvis','sternum','shoulders','trapezius',
                                'foreArm','lwr_arm','hand','neck',
                                'thumb_1', 'thumb_mid', 'thumb_2',
                                'index_1', 'index_mid', 'index_2',
                                'middle_1', 'middle_mid', 'middle_2',
                                'ring_1', 'ring_mid', 'ring_2',
                                'pinky_1', 'pinky_mid', 'pinky_2','lwrFace',
                                'noseTop', 'noseMid', 'noseBase', 'noseTip','neckTop',
                                'brow', 'forehead', 'headTop','mouth', 'underLip','underNose','cranium',
                                'mouthCavity', 'lwrFace', 'chin', 'headBack']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['tx'])	                 
                #>>> ty
                if str_name in ['ankle','toes','ball','heel','lwr_leg','bicep','tricep',
                                'foreArm','elbowMeat','lwr_arm','hand','neck','pectoral','brow',
                                'thumb_1', 'thumb_mid', 'thumb_2',
                                'index_1', 'index_mid', 'index_2',
                                'middle_1', 'middle_mid', 'middle_2',
                                'ring_1', 'ring_mid', 'ring_2',
                                'pinky_1', 'pinky_mid', 'pinky_2']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['ty'])	
                #>>> tz
                if str_name in ['torsoMid','pelvis','sternum','shoulders','trapezius','elbowMeat','neckTop',]:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['tz'])	

                #>>> Rotates ========================================================
                #> All rotates
                if str_name in ['ankle','toes','ball','heel','calf','lwr_leg','upr_leg',
                                'hamstring','quad','sternum','shoulders','upr_arm','lwr_arm',
                                'shoulderBlade','trapezius','bicep','tricep','foreArm',
                                'elbowMeat','hand', 'neck','pectoral'
                                'thumb_1', 'thumb_mid', 'thumb_2',
                                'index_1', 'index_mid', 'index_2',
                                'middle_1', 'middle_mid', 'middle_2',
                                'ring_1', 'ring_mid', 'ring_2',#jaw,
                                'pinky_1', 'pinky_mid', 'pinky_2','cranium','lwrFace',
                                'brow', 'eyeOrb', 'mouth', 'mouthCavity']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['rx','ry','rz'])	
                #> rx
                if str_name in ['asdf','eye']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['rx'])
                #> ry
                if str_name in ['forehead','noseBase','neckTop','eye','headTop']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['ry'])
                #> rz
                if str_name in ['forehead','noseBase','neckTop','headTop']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['rz'])	

                #>>> Scales ========================================================
                #>>>sx
                if str_name in ['arm']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['sx'])                           
                #>>>sy
                if str_name in ['ankleMeat','quad','hamstring','torsoMid','cranium','pelvis','lwrFace',
                                'arm','calf','sternum','neckTop','noseTop']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['sy'])            
                #>>>sz
                if str_name in ['lwr_leg','hipMeat','wristMeat','lwr_arm','noseTop','lwrFace','upr_arm','ball']:
                    attributes.doSetLockHideKeyableAttr(i_c.mNode,channels = ['sz']) 

                if i_c.hasAttr('radius'):
                    cgmMeta.cgmAttr(i_c,'radius',value = 0, hidden = True, lock=True, keyable = False)
                    i_c.drawStyle = 7#make it a square so we can hide it

                #>>> Limits ==================================================== 
                #>>> all
                if str_name in ['eye']:
                    mc.transformLimits(i_c.mNode, sz = [-1,1], esz = [0,1])
                if str_name in ['lwrFace']:
                    mc.transformLimits(i_c.mNode, ty = [-2,0], ety = [1,0])
    for loc in mc.ls(type='locator'):
        mShape = cgmMeta.cgmNode(loc)
        str_transform =  mShape.getTransform()
        mLoc = cgmMeta.cgmObject(str_transform)
        for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            cgmMeta.cgmAttr(str_transform,a,lock=not unlock,keyable=True,hidden=False)
        mLoc.v = unlock


    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)
    #mc.cycleCheck(e=False)
    log.warning("Cycle check turned off")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
def autoTagControls(customizationNode = 'MorpheusCustomization',l_controls=None): 
    """
    For each joint:
    1) tag it mClass as cgmObject
    2) Find the closest curve
    3) Tag that curve as a cgmObject mClass
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    assert mc.objExists(customizationNode),"'%s' doesn't exist"%customizationNode
    log.info(">>> autoTagControls")
    log.info("l_joints: %s"%customizationNode)
    log.info("l_controls: %s"%l_controls)
    p = r9Meta.MetaClass(customizationNode)
    buffer = p.getMessage('jointList')
    for o in buffer:
        i_o = cgmMeta.cgmObject(o)
        i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)    
    if l_controls is None:#If we don't have any controls passed
        l_iControls = []
        if mc.objExists('controlCurves'):#Check the standard group
            l_controls = search.returnAllChildrenObjects('controlCurves')
        for c in l_controls:
            i_c = cgmMeta.cgmObject(c)
            i_c.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
            l_iControls.append(i_c.mNode)
        #p.addAttr('controlCurves',attrType = 'message', value = l_iControls)
        p.controlCurves = l_iControls
    for i_o in p.jointList:
        closestObject = distance.returnClosestObject(i_o.mNode,p.getMessage('controlCurves'))
        if closestObject:
            log.info("'%s' <<tagging>> '%s'"%(i_o.getShortName(),closestObject))            
            i_closestObject = cgmMeta.cgmObject(closestObject)
            i_closestObject.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
            i_o.addAttr('controlCurve',value = i_closestObject.mNode,attrType = 'messageSimple', lock = True)
            i_closestObject.addAttr('cgmSource',value = i_o.mNode,attrType = 'messageSimple', lock = True)
            i_closestObject.doCopyNameTagsFromObject(i_o.mNode,['cgmType','cgmTypeModifier'])

            i_o.addAttr('cgmType','shaper',attrType='string',lock = True)            
            i_closestObject.addAttr('cgmType','bodyShaper',attrType='string',lock = True)

            i_o.doName()
            i_closestObject.doName()

def doTagCurveFromJoint(curve = None, joint = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if curve is None:
        curve = mc.ls(sl=True)[1] or False
    if joint is None:
        joint = mc.ls(sl=True)[0] or False

    assert mc.objExists(curve),"'%s' doesn't exist"%curve
    assert mc.objExists(joint),"'%s' doesn't exist"%joint

    log.info(">>> doTagCurveFromJoint")
    log.info("curve: %s"%curve)
    log.info("joint: %s"%joint)
    i_o = cgmMeta.cgmObject(joint)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)

    i_crv = cgmMeta.cgmObject(curve)
    i_crv.addAttr('mClass','cgmObject',attrType = 'string', lock = True)
    i_o.addAttr('controlCurve',value = i_crv.mNode,attrType = 'messageSimple', lock = True)
    i_crv.addAttr('cgmSource',value = i_o.mNode,attrType = 'messageSimple', lock = True)
    i_crv.doCopyNameTagsFromObject(i_o.mNode,['cgmType','cgmTypeModifier'])

    #i_o.addAttr('cgmTypeModifier','shaper',attrType='string',lock = True)            
    i_crv.addAttr('cgmType','shaper',attrType='string',lock = True)

    i_o.doName()
    i_crv.doName()
    return True

def doTagParentContrainToTargets(obj = None, targets = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if obj is None:
        obj = mc.ls(sl=True)[-1] or False
    if targets is None:
        targets = mc.ls(sl=True)[:-1] or False

    assert mc.objExists(obj),"'%s' doesn't exist"%obj
    assert targets,"No targets found"
    for t in targets:
        assert mc.objExists(t),"'%s' doesn't exist"%t

    log.info(">>> doTagContrainToTargets")
    log.info("obj: %s"%obj)
    log.info("targets: %s"%targets)
    i_o = cgmMeta.cgmObject(obj)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)

    i_o.addAttr('constraintParentTargets',attrType='message',value = targets)
    return True

def doTagAimContrainToTargets(obj = None, targets = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if obj is None:
        obj = mc.ls(sl=True)[-1] or False
    if targets is None:
        targets = mc.ls(sl=True)[:-1] or False

    assert mc.objExists(obj),"'%s' doesn't exist"%obj
    assert targets,"No targets found"
    for t in targets:
        assert mc.objExists(t),"'%s' doesn't exist"%t

    log.info(">>> doTagContrainToTargets")
    log.info("obj: %s"%obj)
    log.info("targets: %s"%targets)
    i_o = cgmMeta.cgmObject(obj)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)

    i_o.addAttr('constraintAimTargets',attrType='message',value = targets)
    return True

def doTagPointContrainToTargets(obj = None, targets = None): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if obj is None:
        obj = mc.ls(sl=True)[-1] or False
    if targets is None:
        targets = mc.ls(sl=True)[:-1] or False

    assert mc.objExists(obj),"'%s' doesn't exist"%obj
    assert targets,"No targets found"
    for t in targets:
        assert mc.objExists(t),"'%s' doesn't exist"%t

    log.info(">>> doTagContrainToTargets")
    log.info("obj: %s"%obj)
    log.info("targets: %s"%targets)
    i_o = cgmMeta.cgmObject(obj)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)

    i_o.addAttr('constraintPointTargets',attrType='message',value = targets)
    return True

def doTagContrainToTargets(obj = None, targets = None, constraintTypes = ['point']): 
    """
    """
    # Get our base info
    #==============	        
    #>>> module null data 
    if obj is None:
        obj = mc.ls(sl=True)[-1] or False
    if targets is None:
        targets = mc.ls(sl=True)[:-1] or False

    assert mc.objExists(obj),"'%s' doesn't exist"%obj
    assert targets,"No targets found"
    for t in targets:
        assert mc.objExists(t),"'%s' doesn't exist"%t

    log.info(">>> doTagContrainToTargets")
    log.info("obj: %s"%obj)
    log.info("targets: %s"%targets)
    i_o = cgmMeta.cgmObject(obj)
    i_o.addAttr('mClass','cgmObject',attrType = 'string', lock = True)

    for c in constraintTypes:
        if c in ['point','aim','scale','parent','orient']:
            i_o.addAttr('constraint%sTargets'%c.capitalize(),attrType='message',value = targets)
        else:
            log.warning("'%s' not a known constraint type"%c)
    return True

@r9General.Timer
def updateTransform(i_curve,i_sourceObject):
    log.info(">>> updateTransform: '%s'"%i_curve.getShortName())    
    childrenToWorld = []	
    children = mc.listRelatives(i_curve.mNode,children=True,type = 'transform')
    if children:
        for c in children:
            childrenToWorld.append(rigging.doParentToWorld(c))
    transform = rigging.groupMeObject(i_sourceObject.mNode,False,False)
    i_transform = cgmMeta.cgmObject(transform)
    for attr in i_curve.getUserAttrs():
        attributes.doCopyAttr(i_curve.mNode,attr,transform)
    for attr in i_sourceObject.getUserAttrs():
        attributes.doCopyAttr(i_sourceObject.mNode,attr,transform)
    buffer = curves.parentShapeInPlace(transform,i_curve.mNode)
    mc.delete(i_curve.mNode)
    if childrenToWorld:
        for c in childrenToWorld:
            rigging.doParentReturnName(c,transform)
    return i_transform.mNode

def reportContrainToTags():
    for o in mc.ls(sl=True):
        i_jnt = cgmMeta.cgmNode(o)

        #Gather the info to set stuff up
        if i_jnt.hasAttr('constraintScaleTargets'):
            log.info("'%s' constraintScaleTargets: %s"%(o,i_jnt.getMessage('constraintScaleTargets',False)))
        if i_jnt.hasAttr('constraintParentTargets'):
            log.info("'%s' constraintParentTargets: %s"%(o,i_jnt.getMessage('constraintParentTargets',False)))

        if i_jnt.hasAttr('constraintPointTargets'):
            log.info("'%s' constraintPointTargets: %s"%(o,i_jnt.getMessage('constraintPointTargets',False)))

        if i_jnt.hasAttr('constraintOrientTargets'):
            log.info("'%s' constraintOrientTargets: %s"%(o,i_jnt.getMessage('constraintOrientTargets',False)))

        if i_jnt.hasAttr('constraintAimTargets'):
            log.info("'%s' constraintAimTargets: %s"%(o,i_jnt.getMessage('constraintAimTargets',False)))