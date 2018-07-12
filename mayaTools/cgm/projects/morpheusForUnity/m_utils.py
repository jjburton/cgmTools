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
from cgm.core.classes import NodeFactory as cgmNodeFactory
from cgm.core.cgmPy import validateArgs as VALID

reload(cgmNodeFactory)
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
        ml_driven1 = cgmMeta.validateObjListArg(driven1,
                                                mType = 'cgmObject',
                                                mayaType=['joint'], noneValid = False)
        log.debug("|{0}| >> driven2 [Check]...".format(_str_func))                
        ml_driven2 = cgmMeta.validateObjListArg(driven2,
                                                mType = 'cgmObject',
                                                mayaType=['joint'], noneValid = False)
        
        #Check our msgDrivers -----------------------------------------------------------
        if msgDriver:
            log.debug("|{0}| >> msgDriver [Check]...".format(_str_func))
            for mObj in ml_driven1 + ml_driven2:
                if mObj not in ml_missingDrivers:
                    check_msgDriver(mObj)
            if ml_missingDrivers:
                raise ValueError,"Missing drivers. See errors."
            log.debug("|{0}| >> msgDriver [Pass]...".format(_str_func))
            
            
        int_lenDriven1 = len(ml_driven1)
        int_lenDriven2 = len(ml_driven2)
        
        log.debug("|{0}| >> Driven lengths   {1} | {2}".format(_str_func,int_lenDriven1,int_lenDriven2))                
        
        
        log.debug("|{0}| >> influences1 [Check]...".format(_str_func))                
        ml_influences1 = cgmMeta.validateObjListArg(influences1,
                                                    mType = 'cgmObject',
                                                    mayaType=['joint'], noneValid = False)
        
        log.debug("|{0}| >> influences2 [Check]...".format(_str_func))                    
        ml_influences2 = cgmMeta.validateObjListArg(influences2,
                                                    mType = 'cgmObject',
                                                    mayaType=['joint'], noneValid = False)        
        
        
        int_lenInfluences1 = len(ml_influences1)
        int_lenInfluences2 = len(ml_influences2)
        
        log.debug("|{0}| >> Influence lengths   {1} | {2}".format(_str_func,
                                                                  int_lenInfluences1,
                                                                  int_lenInfluences2))                        
        
        
        mi_mayaOrientation = VALID.simpleOrientation(orientation)
        str_orientation = mi_mayaOrientation.p_string
        str_secondaryAxis = VALID.stringArg(secondaryAxis,noneValid=True)        
        
        if specialMode and specialMode not in ['noStartEnd']:
            raise ValueError,"Unknown special mode: {0}".format(specialMode)        
        

        return
        
        #module -----------------------------------------------------------------------------------------------
        mModule = cgmMeta.validateObjArg(moduleInstance,noneValid = True)
        #try:mModule.isModule()
        #except:mModule = False
    
        mi_rigNull = False	
        if mModule:
            log.debug("|{0}| >> Module found. mModule: {1}...".format(_str_func,mModule))                                    
            mi_rigNull = mModule.rigNull	
            if str_baseName is None:
                str_baseName = mModule.getPartNameBase()#Get part base name	    
        if not baseName:baseName = 'testRibbonSeal' 
        if not baseName1:baseName1 = 'ribbon1'
        if not baseName2:baseName2 = 'ribbon2'
        
        #pprint.pprint(vars())
        return        


        if int_lenJoints<3:
            pprint.pprint(vars())
            raise ValueError,"needs at least three joints"
        
        if parentGutsTo is None:
            mGroup = cgmMeta.cgmObject(name = 'newgroup')
            mGroup.addAttr('cgmName', str(str_baseName), lock=True)
            mGroup.addAttr('cgmTypeModifier','segmentStuff', lock=True)
            mGroup.doName()
        else:
            mGroup = cgmMeta.validateObjArg(parentGutsTo,'cgmObject',False)
            
            
        if mModule:
            mGroup.parent = mModule.rigNull
    
        if additiveScaleEnds and not extendEnds:
            extendEnds=True
    
    
        #Good way to verify an instance list? #validate orientation             
        #> axis -------------------------------------------------------------
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
        
        #Ramp values -------------------------------------------------------------------------
        if extraSquashControl:
            l_scaleFactors = MATH.get_blendList(int_lenJoints,squashFactorMax,squashFactorMin,squashFactorMode)
        
        #Squash stretch -------------------------------------------------------------------------
        b_squashStretch = False
        if squashStretch is not None:
            b_squashStretch = True
            if squashStretch == 'both':
                loftAxis2 = str_orientation[1]
                
            """
            mTransGroup = cgmMeta.cgmObject(name = 'newgroup')
            mTransGroup.addAttr('cgmName', str(str_baseName), lock=True)
            mTransGroup.addAttr('cgmTypeModifier','segmentTransStuff', lock=True)
            mTransGroup.doName()"""
            
            
            
        outChannel = str_orientation[2]#outChannel
        upChannel = str_orientation[1]
        #upChannel = '{0}up'.format(str_orientation[1])#upChannel
        l_param = []  
        
        
        mControlSurface2 = False
        ml_surfaces = []
        
        #>>> Ribbon Surface ================================================================================        
        if mi_useSurface:
            raise NotImplementedError,'Not done with passed surface'
        else:
            log.debug("|{0}| >> Creating surface...".format(_str_func))
            l_surfaceReturn = ribbon_createSurface(jointList,loftAxis,sectionSpans,extendEnds)
        
            mControlSurface = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
            mControlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
            mControlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
            mControlSurface.doName()
            
            ml_surfaces.append(mControlSurface)
            
            if loftAxis2:
                log.debug("|{0}| >> Creating surface...".format(_str_func))
                l_surfaceReturn2 = ribbon_createSurface(jointList,loftAxis2,sectionSpans,extendEnds)
            
                mControlSurface2 = cgmMeta.validateObjArg( l_surfaceReturn[0],'cgmObject',setClass = True )
                mControlSurface2.addAttr('cgmName',str(baseName),attrType='string',lock=True)
                mControlSurface2.addAttr('cgmTypeModifier','up',attrType='string',lock=True)
                mControlSurface2.addAttr('cgmType','controlSurface',attrType='string',lock=True)
                mControlSurface2.doName()
        
                ml_surfaces.append(mControlSurface2)
        
        log.debug("mControlSurface: {0}".format(mControlSurface))
        _surf_shape = mControlSurface.getShapes()[0]
        minU = ATTR.get(_surf_shape,'minValueU')
        maxU = ATTR.get(_surf_shape,'maxValueU')
    
        
        ml_toConnect = []
        ml_toConnect.extend(ml_surfaces)
        
        mArcLenCurve = None
        mArcLenDag = None
        
        if b_squashStretch and squashStretchMain == 'arcLength':
            log.debug("|{0}| >> Creating arc curve setup...".format(_str_func))
            
            minV = ATTR.get(_surf_shape,'minValueV')
            maxV = ATTR.get(_surf_shape,'maxValueV')
            
            plug = '{0}_segScale'.format(str_baseName)
            plug_dim = '{0}_arcLengthDim'.format(str_baseName)
            plug_inverse = '{0}_segInverseScale'.format(str_baseName)
            
            mArcLen = cgmMeta.validateObjArg(mc.createNode('arcLengthDimension'),setClass=True)
            mArcLenDag = mArcLen.getTransform(asMeta=True)
            
            mArcLen.uParamValue = MATH.average(minU,maxU)
            mArcLen.vParamValue = maxV
            mArcLenDag.rename('{0}_arcLengthNode'.format(str_baseName))
            
            mControlSurface.connectChildNode(mArcLen.mNode,plug_dim,'arcLenDim')
    
            log.debug("|{0}| >> created: {1}".format(_str_func,mArcLen)) 
    
            #infoNode = CURVES.create_infoNode(mCrv.mNode)
            
            ATTR.connect("{0}.worldSpace".format(mControlSurface.getShapes()[0]), "{0}.nurbsGeometry".format(mArcLen.mNode))
    
            mArcLen.addAttr('baseDist', mArcLen.arcLengthInV,attrType='float',lock=True)
            log.debug("|{0}| >> baseDist: {1}".format(_str_func,mArcLen.baseDist)) 
    
            mPlug_inverseScale = cgmMeta.cgmAttr(mArcLen.mNode,plug_inverse,'float')
            
            l_argBuild=[]
            
            """
            if not masterScalePlug or masterScalePlug == 'create':
                plug_master = '{0}_segMasterScale'.format(str_baseName)
                mPlug_masterScale = cgmMeta.cgmAttr(mArcLen.mNode,plug_master,'float')
                l_argBuild.append("{0} = {1} / {2}".format(mPlug_masterScale.p_combinedShortName,
                                                           '{0}.arcLengthInV'.format(mArcLen.mNode),
                                                           "{0}.baseDist".format(mArcLen.mNode)))
                masterScalePlug = mPlug_masterScale"""
                
            
            """
            l_argBuild.append("{0} = {1} / {2}".format(mPlug_masterScale.p_combinedShortName,
                                                       '{0}.arcLength'.format(mInfoNode.mNode),
                                                       "{0}.baseDist".format(mCrv.mNode)))"""
            l_argBuild.append("{0} = {2} / {1}".format(mPlug_inverseScale.p_combinedShortName,
                                                       '{0}.arcLengthInV'.format(mArcLen.mNode),
                                                       "{0}.baseDist".format(mArcLen.mNode)))        
            
            
            for arg in l_argBuild:
                log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                NodeF.argsToNodes(arg).doBuild()
                
                
            
            
            
            """
            crv = CORERIG.create_at(None,'curve',l_pos= [mJnt.p_position for mJnt in ml_joints])
            mCrv = cgmMeta.validateObjArg(crv,'cgmObject',setClass=True)
            mCrv.rename('{0}_measureCrv'.format( baseName))
            
            ml_toConnect.append(mCrv)
            
            mArcLenCurve = mCrv
            
            mControlSurface.connectChildNode(mCrv,plug_curve,'ribbon')
    
            log.debug("|{0}| >> created: {1}".format(_str_func,mCrv)) 
    
            infoNode = CURVES.create_infoNode(mCrv.mNode)
    
            mInfoNode = cgmMeta.validateObjArg(infoNode,'cgmNode',setClass=True)
            mCrv.addAttr('baseDist', mInfoNode.arcLength,attrType='float',lock=True)
            mInfoNode.rename('{0}_{1}_measureCIN'.format( baseName,plug))
    
            log.debug("|{0}| >> baseDist: {1}".format(_str_func,mCrv.baseDist)) 
    
            #mPlug_masterScale = cgmMeta.cgmAttr(mCrv.mNode,plug,'float')
            mPlug_inverseScale = cgmMeta.cgmAttr(mCrv.mNode,plug_inverse,'float')
            
            l_argBuild=[]
    
            l_argBuild.append("{0} = {2} / {1}".format(mPlug_inverseScale.p_combinedShortName,
                                                       '{0}.arcLength'.format(mInfoNode.mNode),
                                                       "{0}.baseDist".format(mCrv.mNode)))        
            
            
            for arg in l_argBuild:
                log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                NodeF.argsToNodes(arg).doBuild()"""
        
        if b_squashStretch and masterScalePlug is not None:
            log.debug("|{0}| >> Checking masterScalePlug: {1}".format(_str_func, masterScalePlug))        
            if masterScalePlug == 'create':
                log.debug("|{0}| >> Creating measure curve setup...".format(_str_func))
                
                plug = 'segMasterScale'
                plug_curve = 'segMasterMeasureCurve'
                crv = CORERIG.create_at(None,'curveLinear',l_pos= [ml_joints[0].p_position, ml_joints[1].p_position])
                mCrv = cgmMeta.validateObjArg(crv,'cgmObject',setClass=True)
                mCrv.rename('{0}_masterMeasureCrv'.format( baseName))
        
                mControlSurface.connectChildNode(mCrv,plug_curve,'rigNull')
        
                log.debug("|{0}| >> created: {1}".format(_str_func,mCrv)) 
        
                infoNode = CURVES.create_infoNode(mCrv.mNode)
        
                mInfoNode = cgmMeta.validateObjArg(infoNode,'cgmNode',setClass=True)
                mInfoNode.addAttr('baseDist', mInfoNode.arcLength,attrType='float')
                mInfoNode.rename('{0}_{1}_measureCIN'.format( baseName,plug))
        
                log.debug("|{0}| >> baseDist: {1}".format(_str_func,mInfoNode.baseDist)) 
        
                mPlug_masterScale = cgmMeta.cgmAttr(mControlSurface.mNode,plug,'float')
        
                l_argBuild=[]
                l_argBuild.append("{0} = {1} / {2}".format(mPlug_masterScale.p_combinedShortName,
                                                           '{0}.arcLength'.format(mInfoNode.mNode),
                                                           "{0}.baseDist".format(mInfoNode.mNode)))
                for arg in l_argBuild:
                    log.debug("|{0}| >> Building arg: {1}".format(_str_func,arg))
                    NodeF.argsToNodes(arg).doBuild()                
        
            else:
                if issubclass(type(masterScalePlug),cgmMeta.cgmAttr):
                    mPlug_masterScale = masterScalePlug
                else:
                    d_attr = cgmMeta.validateAttrArg(masterScalePlug)
                    if not d_attr:
                        raise ValueError,"Ineligible masterScalePlug: {0}".format(masterScalePlug)
                    mPlug_masterScale  = d_attr['mPlug']
                
            if not mPlug_masterScale:
                raise ValueError,"Should have a masterScale plug by now"
        
        if settingsControl:
            mSettings = cgmMeta.validateObjArg(settingsControl,'cgmObject')
        else:
            mSettings = mControlSurface
            
        b_attachToInfluences = False
        if attachEndsToInfluences:
            log.debug("|{0}| >> attachEndsToInfluences flag. Checking...".format(_str_func))
            if influences and len(influences) > 1:
                b_attachToInfluences = True
            log.debug("|{0}| >> b_attachToInfluences: {1}".format(_str_func,b_attachToInfluences))    
    except Exception,err:
        cgmGEN.cgmException(Exception,err,msg=vars())