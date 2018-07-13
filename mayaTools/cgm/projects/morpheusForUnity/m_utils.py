import copy
import re
import pprint
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib.classes import NameFactory as nFactory
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import GuiFactory as gui
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.classes import NodeFactory as NODEFACTORY
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.rig.ik_utils as IK
import cgm.core.rig.constraint_utils as RIGCONSTRAINTS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.rig.skin_utils as RIGSKIN
import cgm.core.lib.math_utils as MATH
reload(NODEFACTORY)
from cgm.lib import (curves,
                     deformers,
                     distance,
                     search,
                     lists,
                     modules,
                     constraints,
                     rigging,
                     attributes,
                     joints)
reload(constraints)


def rigJoint_verify(joints = [], name=True, connect=True):
    try:
        if not joints:
            joints = mc.ls(sl=True,type='joint')
            
        ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
        ml_rigJoints = []
        
        for i,mObj in enumerate(ml_joints):
            mDirect = mObj.getMessageAsMeta('rigJoint')
            if not mDirect:
                mDirect = mObj.doDuplicate(po=True)
                if name:
                    if 'sknJnt' not in mObj.p_nameBase:
                        mObj.rename( "{0}_sknJnt".format(mObj.p_nameBase) )
                mDirect.rename( mObj.p_nameBase.replace('sknJnt','rig') )
                mDirect.connectChildNode(mObj,'skinJoint','rigJoint')
            
            ml_rigJoints.append(mDirect)
            """
            if i > 0:
                if ml_joints[i].parent:
                    _buffer = ml_joints[i].getParent(asMeta=True).getMessage('rigJoint')
                    if _buffer:
                        mDirect.parent =_buffer[0]"""
            
            if connect:
                mc.pointConstraint([mDirect.mNode], mObj.mNode, maintainOffset = True)
                mc.orientConstraint([mDirect.mNode], mObj.mNode, maintainOffset = True)
                mc.scaleConstraint([mDirect.mNode], mObj.mNode, maintainOffset = True)
                
        return ml_rigJoints
    
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())
        
        
def driverGroup_verify(joints = []):
    try:
        if not joints:
            joints = mc.ls(sl=True)
            
        ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
        ml_new = []
        
        for i,mObj in enumerate(ml_joints):
            mDriver = mObj.getMessageAsMeta('driverGroup')
            if not mDriver:
                mDriver = mObj.doGroup(True,asMeta=True,typeModifier = 'driver')
            ml_new.append(mDriver)

        return ml_new
    
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())
        


def rigJoint_connect(joints = []):
    try:
        if not joints:
            joints = mc.ls(sl=True,type='joint')
            
        ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
        ml_rigJoints = []
        
        for i,mObj in enumerate(ml_joints):
            mDirect = mObj.getMessageAsMeta('rigJoint')
            if not mDirect:
                log.error("{0} missing rig joint!".format(mObj.p_nameShort))
                continue
            ml_rigJoints.append(mDirect)
            mc.pointConstraint([mDirect.mNode], mObj.mNode, maintainOffset = True)
            mc.orientConstraint([mDirect.mNode], mObj.mNode, maintainOffset = True)
            mc.scaleConstraint([mDirect.mNode], mObj.mNode, maintainOffset = True)
            
        return ml_rigJoints
    
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())
        

def rigJoint_connectFromRig(joints = []):
    try:
        if not joints:
            joints = mc.ls(sl=True,type='joint')
            
        ml_joints = cgmMeta.validateObjListArg(joints,'cgmObject')
        ml_rigJoints = []
        
        for i,mObj in enumerate(ml_joints):
            mDriven = mObj.getMessageAsMeta('skinJoint')
            if not mDriven:
                log.error("{0} missing skin joint!".format(mObj.p_nameShort))
                continue
            ml_rigJoints.append(mDriven)     
            log.error("Connecting {0} --> {1}".format(mObj.p_nameShort,
                                                     mDriven.p_nameShort))  
           
            mc.pointConstraint([mObj.mNode], mDriven.mNode, maintainOffset = True)
            mc.orientConstraint([mObj.mNode], mDriven.mNode, maintainOffset = True)
        return ml_rigJoints
    
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())
        
        

def ribbon_seal(driven1 = None,
                driven2 = None,
                
                influences1 = None,
                influences2 = None,
                
                msgDriver = None,#...msgLink on joint to a driver group for constaint purposes
                
                
                extendEnds = False,
                
                
                loftAxis = 'z',
                
                orientation = 'zyx',
                secondaryAxis = 'y+',
                
                baseName = None,
                baseName1=None,
                baseName2=None,
                
                connectBy = 'constraint',
                
                sectionSpans = 1, 
                settingsControl = None,
                specialMode = None,

                moduleInstance = None,
                parentGutsTo = None):
    
    try:
        _str_func = 'ribbon_seal'
        
        ml_rigObjectsToConnect = []
        md_drivers = {}
        md_base = {}
        md_seal = {}
        md_blend = {}
        md_follicles = {}
        md_follicleShapes ={}
        
        d_dat = {1:{},
                 2:{}}
        
        if msgDriver:
            ml_missingDrivers = []
            
        def check_msgDriver(mObj):
            mDriver = mObj.getMessageAsMeta(msgDriver)
            if mDriver:
                md_drivers[mObj] = mDriver
            else:
                log.error("|{0}| >> Missing driver: {1}".format(_str_func,mObj))
                ml_missingDrivers.append(mObj)
                return False
        
        #>>> Verify ===================================================================================
        log.debug("|{0}| >> driven1 [Check]...".format(_str_func))        
        d_dat[1]['driven'] = cgmMeta.validateObjListArg(driven1,
                                                mType = 'cgmObject',
                                                mayaType=['joint'], noneValid = False)
        log.debug("|{0}| >> driven2 [Check]...".format(_str_func))                
        d_dat[2]['driven'] = cgmMeta.validateObjListArg(driven2,
                                                mType = 'cgmObject',
                                                mayaType=['joint'], noneValid = False)
        
        #Check our msgDrivers -----------------------------------------------------------
        if msgDriver:
            log.debug("|{0}| >> msgDriver [Check]...".format(_str_func))
            for mObj in d_dat[1]['driven'] + d_dat[2]['driven']:
                if mObj not in ml_missingDrivers:
                    check_msgDriver(mObj)
            if ml_missingDrivers:
                raise ValueError,"Missing drivers. See errors."
            log.debug("|{0}| >> msgDriver [Pass]...".format(_str_func))
            
            
        d_dat[1]['int_driven']  = len(d_dat[1]['driven'])
        d_dat[2]['int_driven']  = len(d_dat[2]['driven'])
        
        log.debug("|{0}| >> Driven lengths   {1} | {2}".format(_str_func,d_dat[1]['int_driven'] ,d_dat[2]['int_driven'] ))                
        
        
        log.debug("|{0}| >> influences1 [Check]...".format(_str_func))                
        d_dat[1]['mInfluences']  = cgmMeta.validateObjListArg(influences1,
                                                    mType = 'cgmObject',
                                                    mayaType=['joint'], noneValid = False)
        
        log.debug("|{0}| >> influences2 [Check]...".format(_str_func))                    
        d_dat[2]['mInfluences']  = cgmMeta.validateObjListArg(influences2,
                                                    mType = 'cgmObject',
                                                    mayaType=['joint'], noneValid = False)        
        
        
        d_dat[1]['int_influences'] = len(d_dat[1]['mInfluences'] )
        d_dat[2]['int_influences'] = len(d_dat[2]['mInfluences'] )
        
        log.debug("|{0}| >> Influence lengths   {1} | {2}".format(_str_func,
                                                                  d_dat[1]['int_influences'],
                                                                  d_dat[2]['mInfluences']))                        
        
        
        mi_mayaOrientation = VALID.simpleOrientation(orientation)
        str_orientation = mi_mayaOrientation.p_string
        str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)        
        
        if specialMode and specialMode not in ['noStartEnd']:
            raise ValueError,"Unknown special mode: {0}".format(specialMode)        
        
        #module -----------------------------------------------------------------------------------------------
        mModule = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
        #try:mModule.isModule()
        #except:mModule = False
    
        mi_rigNull = False	
        if mModule:
            log.debug("|{0}| >> mModule [Check]...".format(_str_func))            
            mi_rigNull = mModule.rigNull	
            if str_baseName is None:
                str_baseName = mModule.getPartNameBase()#Get part base name	    
        if not baseName:baseName = 'testRibbonSeal' 
        if not baseName1:baseName1 = 'ribbon1'
        if not baseName2:baseName2 = 'ribbon2'
        
        d_check = {'driven1':d_dat[1]['int_driven'] ,
                   'driven2':d_dat[2]['int_driven'] }
        
        for k,i in d_check.iteritems():
            if i<3:
                raise ValueError,"needs at least three driven. Found : {0} | {1}".format(k,i)
        
        log.debug("|{0}| >> Group [Check]...".format(_str_func))                    
        if parentGutsTo is None:
            mGroup = cgmMeta.cgmObject(name = 'newgroup')
            mGroup.addAttr('cgmName', str(baseName), lock=True)
            mGroup.addAttr('cgmTypeModifier','segmentStuff', lock=True)
            mGroup.doName()
        else:
            mGroup = cgmMeta.validateObjArg(parentGutsTo,'cgmObject',False)
            
        if mModule:
            mGroup.parent = mModule.rigNull
    
        #Good way to verify an instance list? #validate orientation             
        #> axis -------------------------------------------------------------
        """
        axis_aim = VALID.simpleAxis("{0}+".format(str_orientation[0]))
        axis_aimNeg = axis_aim.inverse
        axis_up = VALID.simpleAxis("{0}+".format(str_orientation [1]))
        axis_out = VALID.simpleAxis("{0}+".format(str_orientation [2]))
    
        v_aim = axis_aim.p_vector#aimVector
        v_aimNeg = axis_aimNeg.p_vector#aimVectorNegative
        v_up = axis_up.p_vector   #upVector
        v_out = axis_out.p_vector
        
        str_up = axis_up.p_string
        
        loftAxis2 = False
        #Figure out our loft axis stuff
        if loftAxis not in  orientation:
            _lower_loftAxis = loftAxis.lower()
            if _lower_loftAxis in ['out','up']:
                if _lower_loftAxis == 'out':
                    loftAxis = str_orientation[2]
                else:
                    loftAxis = str_orientation[1]
            else:
                raise ValueError,"Not sure what to do with loftAxis: {0}".format(loftAxis)
        """

        outChannel = str_orientation[2]#outChannel
        upChannel = str_orientation[1]
        #upChannel = '{0}up'.format(str_orientation[1])#upChannel
        

        
        #>>> Ribbon Surface ============================================================================        
        log.debug("|{0}| >> Ribbons generating...".format(_str_func))
        
        l_surfaceReturn1 = IK.ribbon_createSurface(d_dat[1]['driven'],loftAxis,sectionSpans,extendEnds)
    
        d_dat[1]['mSurf'] = cgmMeta.validateObjArg( l_surfaceReturn1[0],'cgmObject',setClass = True )
        d_dat[1]['mSurf'].addAttr('cgmName',str(baseName1),attrType='string',lock=True)    
        d_dat[1]['mSurf'].addAttr('cgmType','controlSurface',attrType='string',lock=True)
        d_dat[1]['mSurf'].doName()
        
        l_surfaceReturn2 = IK.ribbon_createSurface(d_dat[2]['driven'],loftAxis,sectionSpans,extendEnds)        
        d_dat[2]['mSurf'] = cgmMeta.validateObjArg( l_surfaceReturn1[0],'cgmObject',setClass = True )
        d_dat[2]['mSurf'].addAttr('cgmName',str(baseName2),attrType='string',lock=True)    
        d_dat[2]['mSurf'].addAttr('cgmType','controlSurface',attrType='string',lock=True)
        d_dat[2]['mSurf'].doName()        


        log.debug("d_dat[1]['mSurf']: {0}".format(d_dat[1]['mSurf']))
        log.debug("d_dat[2]['mSurf']: {0}".format(d_dat[2]['mSurf']))
        


        ml_toConnect = []
        ml_toConnect.extend([d_dat[1]['mSurf'],d_dat[2]['mSurf']])
        
        
        #>>> Setup our Attributes ================================================================
        log.debug("|{0}| >> Settings...".format(_str_func))        
        if settingsControl:
            mSettings = cgmMeta.validateObjArg(settingsControl,'cgmObject')
        else:
            mSettings = d_dat[1]['mSurf']
        
        mPlug_seal = cgmMeta.cgmAttr(mSettings.mNode,
                                     'seal',
                                     attrType='float',
                                     lock=False,
                                     keyable=True)
        
        
        
        mPlug_sealHeight = cgmMeta.cgmAttr(mSettings.mNode,
                                     'sealHeight',
                                     attrType='float',
                                     lock=False,
                                     keyable=True)

    
        #>>> Setup blend results --------------------------------------------------------------------
        mPlug_sealOn = cgmMeta.cgmAttr(mSettings,'result_sealOn',attrType='float',
                                                 defaultValue = 0,keyable = False,lock=True,
                                                 hidden=False)
        mPlug_sealOff= cgmMeta.cgmAttr(mSettings,'result_sealOff',attrType='float',
                                         defaultValue = 0,keyable = False,lock=True,
                                         hidden=False)
    
        NODEFACTORY.createSingleBlendNetwork(mPlug_seal.p_combinedName,
                                             mPlug_sealOn.p_combinedName,
                                             mPlug_sealOff.p_combinedName)        
        
        
        
        
        mPlug_FavorOneMe = cgmMeta.cgmAttr(mSettings,'result_sealOneMe',attrType='float',
                                         defaultValue = 0,keyable = False,lock=True,
                                         hidden=False)
        mPlug_FavorOneThee = cgmMeta.cgmAttr(mSettings,'result_sealOneThee',attrType='float',
                                             defaultValue = 0,keyable = False,lock=True,
                                             hidden=False)
        mPlug_FavorTwoMe = cgmMeta.cgmAttr(mSettings,'result_sealTwoMe',attrType='float',
                                                 defaultValue = 0,keyable = False,lock=True,
                                                 hidden=False)
        mPlug_FavorTwoThee = cgmMeta.cgmAttr(mSettings,'result_sealTwoThee',attrType='float',
                                             defaultValue = 0,keyable = False,lock=True,
                                             hidden=False)    
        
        NODEFACTORY.createSingleBlendNetwork(mPlug_sealHeight.p_combinedName,
                                             mPlug_FavorOneThee.p_combinedName,
                                             mPlug_FavorOneMe.p_combinedName)
        NODEFACTORY.createSingleBlendNetwork(mPlug_sealHeight.p_combinedName,
                                             mPlug_FavorTwoThee.p_combinedName,
                                             mPlug_FavorTwoMe.p_combinedName)        
        
        d_dat[1]['mPlug_sealOn'] = mPlug_sealOn
        d_dat[1]['mPlug_sealOff'] = mPlug_sealOff
        d_dat[2]['mPlug_sealOn'] = mPlug_sealOn
        d_dat[2]['mPlug_sealOff'] = mPlug_sealOff
        
        d_dat[1]['mPlug_me'] = mPlug_FavorOneMe
        d_dat[1]['mPlug_thee'] = mPlug_FavorOneThee
        d_dat[2]['mPlug_me'] = mPlug_FavorTwoMe
        d_dat[2]['mPlug_thee'] = mPlug_FavorTwoThee        
        
            
        """
        b_attachToInfluences = False
        if attachEndsToInfluences:
            log.debug("|{0}| >> attachEndsToInfluences flag. Checking...".format(_str_func))
            if influences and len(influences) > 1:
                b_attachToInfluences = True
            log.debug("|{0}| >> b_attachToInfluences: {1}".format(_str_func,b_attachToInfluences))
            """
        
        
        #>>> Skinning ============================================================================
        log.debug("|{0}| >> Skinning Ribbons...".format(_str_func))
        
        for idx,dat in d_dat.iteritems():
            max_influences = 2
            mode_tighten = 'twoBlend'
            blendLength = int(dat['int_driven']/2)
            blendMin = 2
            _hardLength = 2
    
            if extendEnds:
                blendMin = 4
                _hardLength = 4
                mode_tighten = None
    
    
            if dat['int_influences'] > 2:
                mode_tighten = None
                #blendLength = int(int_lenInfluences/2)
                max_influences = MATH.Clamp( blendLength, 2, 4)
                blendLength = MATH.Clamp( int(dat['int_influences']/2), 2, 6)
    
            if dat['int_influences'] == dat['int_driven']:
                _hardLength = 3
            #Tighten the weights...
 
    
            mSkinCluster = cgmMeta.validateObjArg(mc.skinCluster ([mObj.mNode for mObj in dat['mInfluences']],
                                                                  dat['mSurf'].mNode,
                                                                  tsb=True,
                                                                  maximumInfluences = max_influences,
                                                                  normalizeWeights = 1,dropoffRate=5.0),
                                                  'cgmNode',
                                                  setClass=True)

            mSkinCluster.doStore('cgmName', dat['mSurf'].mNode)
            mSkinCluster.doName()    

            #Tighten the weights...
            RIGSKIN.surface_tightenEnds(dat['mSurf'].mNode,
                                        hardLength = _hardLength,
                                        blendLength=blendLength,
                                        mode=mode_tighten)        
            
        #>>> Meat ============================================================================
        ml_processed = []
        for idx,dat in d_dat.iteritems():
            idx_seal = 1
            if idx == 1:
                idx_seal = 2
            dat_seal = d_dat[idx_seal]
            log.debug("|{0}| >> Building [{1}] | seal idx: {2} |".format(_str_func,
                                                                       idx,
                                                                       idx_seal)+cgmGEN._str_subLine)
            
            mSurfBase = dat['mSurf']
            mSurfSeal = dat_seal['mSurf']
            
            for i,mObj in enumerate(dat['driven']):
                if mObj in ml_processed:
                    log.debug("|{0}| >> Already completed: {1}".format(_str_func,mObj))                    
                    continue
                ml_processed.append(mObj)
                log.debug("|{0}| >> {1} | Driven: {2}".format(_str_func,i,mObj))
                mDriven = md_drivers[mObj]
                log.debug("|{0}| >> {1} | Driver: {2}".format(_str_func,i,mDriven))
                
                log.debug("|{0}| >> Create track drivers...".format(_str_func))                
                mTrackBase = mDriven.doCreateAt(setClass=True)
                mTrackBase.doStore('cgmName',mObj.mNode)
                mTrackSeal = mTrackBase.doDuplicate()
                mTrackBlend = mTrackBase.doDuplicate()
                
                mTrackSeal.doStore('cgmType','trackSeal')
                mTrackBase.doStore('cgmType','trackBase')
                mTrackBlend.doStore('cgmType','trackBlend')
                
                for mTrack in mTrackBase,mTrackSeal,mTrackBlend:
                    mTrack.doName()
                    
                log.debug("|{0}| >> Attach drivers...".format(_str_func))
                
                d_tmp = {'base':{'mSurf':mSurfBase,
                                 'mTrack':mTrackBase},
                         'seal':{'mSurf':mSurfSeal,
                                 'mTrack':mTrackSeal},
                         }
                
                for n,d in d_tmp.iteritems():
                    mTrack = d['mTrack']
                    mSurf = d['mSurf']
                    
                    follicle,shape = RIGCONSTRAINTS.attach_toShape(mTrack.mNode, mSurf.mNode, 'parent')
                    mFollicle = cgmMeta.asMeta(follicle)
                    mFollShape = cgmMeta.asMeta(shape)
                
                    md_follicleShapes[mObj] = mFollShape
                    md_follicles[mObj] = mFollicle
                
                    mFollicle.parent = mGroup.mNode
                
                    if mModule:#if we have a module, connect vis
                        mFollicle.overrideEnabled = 1
                        cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(mFollicle.mNode,'overrideVisibility'))
                        cgmMeta.cgmAttr(mModule.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(mFollicle.mNode,'overrideDisplayType'))
                        
                #Blend point --------------------------------------------------------------------
                _const = mc.parentConstraint([mTrackBase.mNode,mTrackSeal.mNode],mTrackBlend.mNode)[0]
                ATTR.set(_const,'interpType',2)
                
                targetWeights = mc.parentConstraint(_const,q=True, weightAliasList=True)
                    
                #Connect                                  
                if idx==1:
                    dat['mPlug_thee'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    dat['mPlug_me'].doConnectOut('%s.%s' % (_const,targetWeights[1]))
                else:
                    dat['mPlug_me'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    dat['mPlug_thee'].doConnectOut('%s.%s' % (_const,targetWeights[1]))                
                
                #seal --------------------------------------------------------------------
                _const = mc.parentConstraint([mTrackBase.mNode,mTrackBlend.mNode],mDriven.mNode)[0]
                ATTR.set(_const,'interpType',2)                
                
                targetWeights = mc.parentConstraint(_const,q=True, weightAliasList=True)
                dat['mPlug_sealOff'].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                dat['mPlug_sealOn'].doConnectOut('%s.%s' % (_const,targetWeights[1]))
                
            log.debug("|{0}| >> Blend drivers...".format(_str_func))
            
            
        """
        #Simple contrain
        if b_attachToInfluences and mJnt in [ml_joints[0],ml_joints[-1]]:
            if mJnt == ml_joints[0]:
                mUse = ml_influences[0]
            else:
                mUse = ml_influences[-1]
            mc.parentConstraint([mUse.mNode], mDriven.mNode, maintainOffset=True)
        else:
            mc.parentConstraint([mDriver.mNode], mDriven.mNode, maintainOffset=True)
        """
            
        pprint.pprint(d_dat)
        return
    
    
    
            
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())