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
import cgm.core.lib.position_utils as POS
import cgm.core.lib.distance_utils as DIST
#reload(NODEFACTORY)
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
#reload(constraints)


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
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        
        
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
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        


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
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        

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
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        


def split_blends(driven1 = None,
                 driven2 = None,
                 sealDriver1 = None,
                 sealDriver2 = None,
                 sealDriverMid = None,
                 nameSeal1 = 'left',
                 nameSeal2 = 'right',
                 nameSealMid = 'center',
                 maxValue = 10.0,
                 inTangent = 'auto',
                 outTangent = 'auto',
                 settingsControl = None,
                 buildNetwork = True):
    """
    Split for blend data
    """
    try:
        _str_func = 'split_blends'
        d_dat = {1:{'dist1':[],
                    'dist2':[],
                    'distMid':[]},
                 2:{'dist1':[],
                    'dist2':[],
                    'distMid':[]}}
        _lock=False
        _hidden=False
        #>>> Verify ===================================================================================
        log.debug("|{0}| >> driven1 [Check]...".format(_str_func))        
        d_dat[1]['driven'] = cgmMeta.validateObjListArg(driven1,
                                                mType = 'cgmObject',
                                                mayaType=['joint'], noneValid = False)
        log.debug("|{0}| >> driven2 [Check]...".format(_str_func))                
        d_dat[2]['driven'] = cgmMeta.validateObjListArg(driven2,
                                                mType = 'cgmObject',
                                                mayaType=['joint'], noneValid = False)
        
        mSettings = cgmMeta.validateObjArg(settingsControl,'cgmObject')
        
        if buildNetwork:
            log.debug("|{0}| >> buildNetwork | building driver attrs...".format(_str_func))                            
            mPlug_sealMid = cgmMeta.cgmAttr(mSettings.mNode,
                                            'seal_{0}'.format(nameSealMid),
                                            attrType='float',
                                            minValue=0.0,
                                            maxValue = maxValue,
                                            lock=False,
                                            keyable=True)
            mPlug_seal1 = cgmMeta.cgmAttr(mSettings.mNode,
                                          'seal_{0}'.format(nameSeal1),
                                          attrType='float',
                                          minValue=0.0,
                                          maxValue = maxValue,
                                          lock=False,
                                          keyable=True)
            mPlug_seal2 = cgmMeta.cgmAttr(mSettings.mNode,
                                          'seal_{0}'.format(nameSeal2),
                                          attrType='float',
                                          minValue=0.0,
                                          maxValue = maxValue,
                                          lock=False,
                                          keyable=True)            
        
        pos1 = POS.get(sealDriver1)
        pos2 = POS.get(sealDriver2)
        posMid = POS.get(sealDriverMid)
        
        normMin = maxValue * .1
        normMax = maxValue - normMin
        
        for idx,dat in d_dat.iteritems():
            mDriven = dat['driven']
            
            d_tmp = {'dist1':{'pos':pos1,
                              'res':dat['dist1']},
                     'dist2':{'pos':pos2,
                              'res':dat['dist2']},
                     'distMid':{'pos':posMid,
                                'res':dat['distMid']},
                     }
            
            for mObj in mDriven:
                for n,d in d_tmp.iteritems():
                    dTmp = DIST.get_distance_between_points(d['pos'],mObj.p_position)
                    if MATH.is_float_equivalent(dTmp,0.0):
                        dTmp = 0.0
                    d['res'].append(dTmp)
        
            dat['dist1Norm'] = MATH.normalizeList(dat['dist1'],normMax)
            dat['dist2Norm'] = MATH.normalizeList(dat['dist2'],normMax)
            dat['distMidNorm'] = MATH.normalizeList(dat['distMid'],normMax)
            
            dat['dist1On'] = [v + normMin for v in dat['dist1Norm']]
            dat['dist2On'] = [v + normMin for v in dat['dist2Norm']]
            dat['distMidOn'] = [v + normMin for v in dat['distMidNorm']]
            
            if buildNetwork:
                log.debug("|{0}| >> buildNetwork | building driver attrs...".format(_str_func))
                dat['mPlugs'] = {'1':{},
                                 '2':{},
                                 'mid':{},
                                 'on':{},
                                 'off':{},
                                 'sum':{}}
                for i,mObj in enumerate(mDriven):
                    log.debug("|{0}| >> buildNetwork | On: {1}".format(_str_func,mObj) + cgmGEN._str_subLine)
                    dat['mPlugs']['1'][i] = cgmMeta.cgmAttr(mSettings,
                                                         'set{0}_idx{1}_blend{2}'.format(idx,i,'1'),
                                                         attrType='float',
                                                         keyable = False,lock=_lock,hidden=_hidden)
                    dat['mPlugs']['2'][i] = cgmMeta.cgmAttr(mSettings,
                                                         'set{0}_idx{1}_blend{2}'.format(idx,i,'2'),
                                                         attrType='float',
                                                         keyable = False,lock=_lock,hidden=_hidden)
                    dat['mPlugs']['mid'][i] = cgmMeta.cgmAttr(mSettings,
                                                         'set{0}_idx{1}_blend{2}'.format(idx,i,'mid'),
                                                         attrType='float',
                                                         keyable = False,lock=_lock,hidden=_hidden)                    
                    dat['mPlugs']['on'][i] = cgmMeta.cgmAttr(mSettings,
                                                           'set{0}_idx{1}_on'.format(idx,i),
                                                           attrType='float',
                                                           keyable = False,lock=_lock,hidden=_hidden)
                    dat['mPlugs']['off'][i] = cgmMeta.cgmAttr(mSettings,
                                                          'set{0}_idx{1}_off'.format(idx,i),
                                                          attrType='float',
                                                          keyable = False,lock=_lock,hidden=_hidden)
                    
                    dat['mPlugs']['sum'][i] = cgmMeta.cgmAttr(mSettings,
                                                           'set{0}_idx{1}_sum'.format(idx,i),
                                                           attrType='float',
                                                           keyable = False,lock=_lock,hidden=_hidden)
                    
                    args = []
                    args.append("{0} = {1} + {2} + {3}".format(dat['mPlugs']['sum'][i].p_combinedShortName,
                                                               dat['mPlugs']['1'][i].p_combinedShortName,
                                                               dat['mPlugs']['2'][i].p_combinedShortName,
                                                               dat['mPlugs']['mid'][i].p_combinedShortName))
                    args.append("{0} = clamp(0 , 1.0, {1}".format(dat['mPlugs']['on'][i].p_combinedShortName,
                                                                  dat['mPlugs']['sum'][i].p_combinedShortName,))
                    args.append("{0} = 1.0 - {1}".format(dat['mPlugs']['off'][i].p_combinedShortName,
                                                         dat['mPlugs']['on'][i].p_combinedShortName,))                    
                    for a in args:
                        NODEFACTORY.argsToNodes(a).doBuild()
                        
                    log.debug("|{0}| >> buildNetwork | On: {1}".format(_str_func,mObj))
                    
                    zeroMid = 0
                    zero1 = 0
                    zero2 = 0
                    if i:
                        zero1 = dat['dist1On'][i-1]
                        
                    try:zero2 = dat['dist2On'][i+1]
                    except:zero2 = 0
                        #zero1 = MATH.Clamp(dat['dist1On'][i-1],normMin,maxValue)
                        #zero2 = MATH.Clamp(dat['dist2On'][i-1],normMin,maxValue)

                    mc.setDrivenKeyframe(dat['mPlugs']['1'][i].p_combinedShortName,
                                         currentDriver = mPlug_seal1.p_combinedShortName,
                                         itt=inTangent,ott=outTangent,
                                         driverValue = zero1,value = 0.0)
                    
                    mc.setDrivenKeyframe(dat['mPlugs']['1'][i].p_combinedShortName,
                                         currentDriver = mPlug_seal1.p_combinedShortName,
                                         itt=inTangent,ott=outTangent,                                         
                                         driverValue = dat['dist1On'][i],value = 1.0)
                    
                    
                    mc.setDrivenKeyframe(dat['mPlugs']['2'][i].p_combinedShortName,
                                         currentDriver = mPlug_seal2.p_combinedShortName,
                                         itt=inTangent,ott=outTangent,                                         
                                         driverValue = zero2,value = 0.0)                    
                    mc.setDrivenKeyframe(dat['mPlugs']['2'][i].p_combinedShortName,
                                         currentDriver = mPlug_seal2.p_combinedShortName,
                                         itt=inTangent,ott=outTangent,                                         
                                         driverValue = dat['dist2On'][i],value = 1.0)
                    
                    last1 = dat['dist1On'][i]
                    last2 = dat['dist2On'][i]
                    
                    
                    mc.setDrivenKeyframe(dat['mPlugs']['mid'][i].p_combinedShortName,
                                         currentDriver = mPlug_sealMid.p_combinedShortName,
                                         itt=inTangent,ott=outTangent,                                         
                                         driverValue = zeroMid,value = 0.0)                    
                    mc.setDrivenKeyframe(dat['mPlugs']['mid'][i].p_combinedShortName,
                                         currentDriver = mPlug_sealMid.p_combinedShortName,
                                         itt=inTangent,ott=outTangent,                                         
                                         driverValue = dat['distMidOn'][i],value = 1.0)
        
        #pprint.pprint(d_dat)
        #return d_dat

        for idx,dat in d_dat.iteritems():
            for plugSet,mSet in dat['mPlugs'].iteritems():
                for n,mPlug in mSet.iteritems():
                    mPlug.p_lock=True
                    mPlug.p_hidden = True
                
        
        
        
        return d_dat
        
        
        
    except Exception,err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())    
    
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
                
                sealSplit = False,
                sealDriver1 = None,
                sealDriver2 = None,
                sealDriverMid = None,
                sealName1 = 'left',
                sealName2 = 'right',
                sealNameMid = 'center',
                
                maxValue = 10.0,

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
        
        if specialMode and specialMode not in ['noStartEnd','endsToInfluences']:
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
        
        #Special Mode =================================================================================
        if specialMode in ['noStartEnd','endsToInfluences']:
            log.debug("|{0}| >> Special Mode: {1}".format(_str_func,specialMode)+cgmGEN._str_subLine)

            if specialMode == 'endsToInfluences':
                d_special = {'1start':{'mObj':d_dat[1]['driven'][0],
                                       'mDriver':d_dat[1]['mInfluences'][0]},
                             '1end':{'mObj':d_dat[1]['driven'][-1],
                                       'mDriver':d_dat[1]['mInfluences'][-1]},
                             '2start':{'mObj':d_dat[2]['driven'][0],
                                       'mDriver':d_dat[2]['mInfluences'][0]},
                             '2end':{'mObj':d_dat[2]['driven'][-1],
                                     'mDriver':d_dat[2]['mInfluences'][-1]}}
                
                for n,dat in d_special.iteritems():
                    mObj = dat['mObj']
                    mDriven = md_drivers[mObj]
                    mDriver = dat['mDriver']
                    log.debug("|{0}| >> {1} | Driver: {2}".format(_str_func,i,mDriven))
                    
                    _const = mc.parentConstraint([mDriver.mNode],mDriven.mNode,maintainOffset=True)[0]
                    ATTR.set(_const,'interpType',2)
                
            d_dat[1]['driven'] = d_dat[1]['driven'][1:-1]
            d_dat[2]['driven'] = d_dat[2]['driven'][1:-1]            
            driven1 = driven1[1:-1]
            driven2 = driven2[1:-1]
        
        #>>> Setup our Attributes ================================================================
        log.debug("|{0}| >> Settings...".format(_str_func))        
        if settingsControl:
            mSettings = cgmMeta.validateObjArg(settingsControl,'cgmObject')
        else:
            mSettings = d_dat[1]['mSurf']
        

        
        
        mPlug_sealHeight = cgmMeta.cgmAttr(mSettings.mNode,
                                     'sealHeight',
                                     attrType='float',
                                     lock=False,
                                     keyable=True)
        mPlug_sealHeight.doDefault(.5)
        mPlug_sealHeight.value = .5

    
        #>>> Setup blend results --------------------------------------------------------------------
        if sealSplit:
            d_split = split_blends(driven1,#d_dat[1]['driven'],
                                   driven2,#d_dat[2]['driven'],
                                   sealDriver1,
                                   sealDriver2,
                                   sealDriverMid,
                                   nameSeal1=sealName1,
                                   nameSeal2=sealName2,
                                   nameSealMid=sealNameMid,
                                   settingsControl = mSettings,
                                   maxValue=maxValue)
            for k,d in d_split.iteritems():
                d_dat[k]['mPlugs'] = d['mPlugs']
            
        else:
            mPlug_seal = cgmMeta.cgmAttr(mSettings.mNode,
                                         'seal',
                                         attrType='float',
                                         lock=False,
                                         keyable=True)
            
            mPlug_sealOn = cgmMeta.cgmAttr(mSettings,'result_sealOn',attrType='float',
                                           defaultValue = 0,keyable = False,lock=True,
                                           hidden=False)
        
            mPlug_sealOff= cgmMeta.cgmAttr(mSettings,'result_sealOff',attrType='float',
                                           defaultValue = 0,keyable = False,lock=True,
                                           hidden=False)
        
            NODEFACTORY.createSingleBlendNetwork(mPlug_seal.p_combinedName,
                                                 mPlug_sealOn.p_combinedName,
                                                 mPlug_sealOff.p_combinedName)
            
            d_dat[1]['mPlug_sealOn'] = mPlug_sealOn
            d_dat[1]['mPlug_sealOff'] = mPlug_sealOff
            d_dat[2]['mPlug_sealOn'] = mPlug_sealOn
            d_dat[2]['mPlug_sealOff'] = mPlug_sealOff                    
            
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

            mSkinCluster.doStore('cgmName', dat['mSurf'])
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
                mTrackBase.doStore('cgmName',mObj)
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
                    
                    _res = RIGCONSTRAINTS.attach_toShape(mTrack.mNode, mSurf.mNode, 'parent')
                    mFollicle = _res[-1]['mFollicle']#cgmMeta.asMeta(follicle)
                    mFollShape = _res[-1]['mFollicleShape']#cgmMeta.asMeta(shape)
                
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
                
                if sealSplit:
                    dat['mPlugs']['off'][i].doConnectOut('%s.%s' % (_const,targetWeights[0]))
                    dat['mPlugs']['on'][i].doConnectOut('%s.%s' % (_const,targetWeights[1]))                    
                else:
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
            
        #pprint.pprint(d_dat)
        return
    
    
    
            
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())