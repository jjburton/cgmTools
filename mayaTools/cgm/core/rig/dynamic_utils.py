import maya.cmds as mc
from cgm.core import cgm_General as cgmGEN
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.euclid as euclid
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.locator_utils as LOC
import cgm.core.lib.curve_Utils as CURVES
from cgm.core.cgmPy.validateArgs import simpleAxis
import cgm.core.lib.name_utils as NAMES
import cgm.core.cgm_Meta as cgmMeta
from cgm.core.lib import math_utils as MATHUTILS
import cgm.core.classes.NodeFactory as NODEFACTORY
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.constraint_utils as CONSTRAINTS

import pprint
import copy
import maya.mel as mel
from cgm.core.cgmPy import validateArgs as VALID

__MAYALOCAL = 'RIGDYN'

import cgm.core.presets.cgmDynFK_presets as dynFKPresets

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class chain(object):
    hairSystem = None
    nucleus = None
    follicles = []
    ml_follicles = []
    outCurves = []
    targets = []
    baseName = None
        
    
    def __init__(self, objs = None, fwd = 'z+', up = 'y+', hairSystem=None, baseName = 'cgmDynHair', name = None):
        self.hairSystem = hairSystem
        
        _sel = mc.ls(sl=1)
        if not objs:
            if _sel:
                objs = _sel
                
        self.baseName = baseName
                
        if objs:
            self.CreateChain(objs, fwd, up, name)
            


    def CreateChain(self, objs = None, fwd = 'z+', up='y+',name = None):
        _str_func = 'CreateChain'
        
        objs = cgmMeta.asMeta( mc.ls(sl=True) )
        
        if not objs:
            return log.warning("No objects passed. Unable to createChain")
            
        if name is None:
            name = objs[-1].p_nameBase

        self.targets = self.targets + objs

        fwdAxis = simpleAxis(fwd)
        upAxis = simpleAxis(up)

        crvPositions = []

        for obj in objs:
            crvPositions.append(obj.p_position)

        crvPositions.append( DIST.get_pos_by_axis_dist(objs[-1], fwdAxis.p_string,
                                                       DIST.get_distance_between_points(crvPositions[-1],crvPositions[-2])) )

        crvPositions.insert(0, DIST.get_pos_by_axis_dist(objs[0], fwdAxis.inverse.p_string,
                                                         DIST.get_distance_between_points(crvPositions[0],crvPositions[1])*.5) )

        crv = CORERIG.create_at(create='curve',l_pos= crvPositions, baseName = name)

        # make the dynamic setup
        b_existing = False
        if self.hairSystem != None:
            log.info(cgmGEN.logString_msg(_str_func,'Using existing system: {0}'.format(self.hairSystem)))
            mc.select(self.hairSystem, add=True)
            b_existing = True
            
        mel.eval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0" }')

        # get relevant nodes
        follicle = mc.listRelatives(crv,parent=True)[0]
        mFollicle = cgmMeta.asMeta(follicle)
        mFollicle.rename("{0}_foll".format(name))
        follicle = mFollicle.mNode
        self.ml_follicles.append(mFollicle)
        
        follicleShape = mc.listRelatives(mFollicle.mNode, shapes=True)[0]
        self.hairSystem = mc.listRelatives( mc.listConnections('%s.currentPosition' % follicleShape)[0], shapes=True)[0]
        if not b_existing:
            mHairSys = cgmMeta.asMeta(self.hairSystem)
            mHairSysDag = mHairSys.getTransform(asMeta=1)
            
            mHairSysDag.rename("{0}_hairSys".format(self.baseName))
            self.hairSystem = mHairSys.mNode
            
        outCurve = mc.listConnections('%s.outCurve' % follicle)[0]
        outCurveShape = mc.listRelatives(outCurve, shapes=True)[0]
        self.nucleus = mc.listConnections( '%s.currentState' % self.hairSystem )[0]
        if not b_existing:
            pass
        mc.select( objs[0].getParent() )

        self.follicles.append(follicle)
        self.outCurves.append(outCurve)
        
        # set default properties
        mc.setAttr( '%s.pointLock' % follicleShape, 1 )
        mc.parentConstraint(objs[0].getParent(), follicle, mo=True)

        # create locators on objects
        locators = []
        prs = []

        for i, obj in enumerate(objs):
            loc = LOC.create(obj.getNameLong())
            locators.append(loc)
            
            aimNull = mc.group(em=True)
            aimNull = mc.rename('%s_aim' % obj.getShortName())
            
            poc = mc.createNode('pointOnCurveInfo', name='%s_pos' % loc)
            pocAim = mc.createNode('pointOnCurveInfo', name='%s_aim' % loc)
            pr = CURVES.getUParamOnCurve(loc, outCurve)
            
            mc.connectAttr( '%s.worldSpace[0]' % outCurveShape, '%s.inputCurve' % poc, f=True )
            mc.connectAttr( '%s.worldSpace[0]' % outCurveShape, '%s.inputCurve' % pocAim, f=True )

            mc.setAttr( '%s.parameter' % poc, pr )
            
            if i < len(objs)-1:
                nextpr = CURVES.getUParamOnCurve(objs[i+1], outCurve)
                mc.setAttr('%s.parameter' % pocAim, (nextpr + pr) * .5)
            else:
                mc.setAttr( '%s.parameter' % pocAim, len(objs)+1 )
            
            locParent = mc.group(em=True)
            locParent = mc.rename( '%s_pos' % obj.getShortName() )

            mc.connectAttr( '%s.position' % poc, '%s.translate' % locParent)
            mc.connectAttr( '%s.position' % pocAim, '%s.translate' % aimNull)
            
            aimConstraint = mc.aimConstraint( aimNull, locParent, aimVector=fwdAxis.p_vector, upVector = upAxis.p_vector, worldUpType = "objectrotation", worldUpVector = upAxis.p_vector, worldUpObject = objs[0].getParent() )

            mc.parent(loc, locParent)

    def SelectTargets(self):
        mc.select(cl = True)
        for obj in self.targets:
            mc.select(obj, add=True)
            
            
    def report(self):
        pprint.pprint(self.__dict__)
        
    def delete(self):
        pass
    
    
class cgmDynFK(cgmMeta.cgmObject):
    baseName = None
    fwd = None
    up = None
    startFrame = None
    useExistingNucleus = True
    upSetup = 'liveStart'
    
    def __init__(self,node = None, name = None,
                 objs = None, fwd = 'z+', up = 'y+',
                 upSetup = 'guess',
                 hairSystem=None,
                 useExistingNucleus = True,
                 baseName = 'hair',
                 startFrame = -50,
                 extendStart = None,
                 extendEnd = None,
                 upControl = False,
                 aimUpMode = 'joint',
                 *args,**kws):
        """ 
        
        upSetup
           liveStart
           control

        """
        ### input check  
        _sel = mc.ls(sl=1)
        if not objs and node is None:
            if _sel:objs = _sel
        
        super(cgmDynFK, self).__init__(node = node,name = baseName,nodeType = 'transform') 
        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            return
        
        #====================================================================================
        #for a in 'arg_ml_dynParents','_mi_dynChild','_mi_followDriver','d_indexToAttr','l_dynAttrs':
            #if a not in self.UNMANAGED:
                #self.UNMANAGED.append(a)
                
        self.dagLock(ignore=['v'])

        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        
        self.fwd = fwd
        self.up = up
        self.startFrame = startFrame
        self.baseName = baseName
        self.useExistingNucleus = useExistingNucleus
        self.upSetup = upSetup
        self.extendEnd = extendEnd
        self.extendStart = extendStart
        self.aimUpMode = aimUpMode
        self.upControl = upControl
       
        if not node:
            self.rename("{0}_dynFK".format(self.baseName))
            self.doStore('cgmName', self.baseName)
            
        if objs:
            self.chain_create(objs, fwd, up, name=name)        
        
        self.report()
        
        if _sel:
            mc.select(_sel)
    
    def get_nextIdx(self):
        mDat = self.get_dat()
        dChains = mDat.get('chains')
        _exists = False
        _i = 0
        while dChains.get(_i):
            _i+=1
        return _i
        return ATTR.get_nextAvailableSequentialAttrIndex(self.mNode, "chain")
        
    def chain_rebuild(self, idx = None, objs = None, **kws):
        _str_func = 'chain_rebuild'
        dat = self.get_dat()
        mNucleus = dat['mNucleus']
        mHairSysShape = dat['mHairSysShape']
        
        l_do = []
        if idx:
            if dat['chains'].get(idx):
                l_do.append(idx)
        else:
            l_do = dat['chains'].keys()
            
        log.debug(cgmGEN.logString_msg(_str_func, 'To do: {0}'.format(l_do)))
        for idx in l_do:
            log.debug(cgmGEN.logString_sub(_str_func, 'On: {0}'.format(idx)))            
            _d = dat['chains'][idx]
            ml_targets = _d['mTargets']
            self.targets_disconnect(idx)#...remove contraints
            mDynFKParent = ml_targets[0].getMessageAsMeta('dynFKParentGroup')
            if mDynFKParent:
                ml_targets[0].p_parent = mDynFKParent.p_parent
                mDynFKParent.delete()
            
            self.chain_deleteByIdx(idx)
            
            self.chain_create(ml_targets,**kws)
            self.targets_connect(idx)#...remove contraints
            log.debug(cgmGEN.logString_msg(_str_func, 'chain {0} done'.format(idx)))
            

    
    def get_nucleus(self,mNucleus=None):
        """Try to get the nucleus from the scene to use for other setups"""
        if mNucleus is not None:
           return cgmMeta.validateObjArg(mNucleus,noneValid=True)
        else:
            mNucleus = cgmMeta.validateObjArg('cgmDynFK_nucleus',noneValid=True)
        return mNucleus
        
    def chain_deleteByIdx(self, idx = None):
        if idx is None:
            return log.warning("Must have an idx to remove")
        
        # mDat = self.get_dat()
        
        # _d = mDat['chains'].get(idx)
        # mGrp = _d.get('mGrp')

        chain = self.msgList_get('chain')[idx]
        
        #mGrp = self.getMessageAsMeta("chain_{0}".format(idx))
        if chain:
            chain.delete()
            ATTR.msgList_clean(self.mNode,'chain')
            return log.info("Removed idx: {0}".format(idx))
        else:
            return log.warning("No chain found at idx: {0}".format(idx))
            
    def chain_removeAll(self):
        ml = self.msgList_get('chain')
        for i,mGrp in enumerate(ml):
            log.warning("Removing: {0} | {1}".format(i,mGrp.mNode))
            mGrp.delete()
        
        self.msgList_purge('chain')
    
    def chain_setOrientUpByIdx(self, idx=None, axis=None):
        if idx is None:
            return log.warning("Must have an idx to set orient")

        chain = self.msgList_get('chain')[idx]

        for parent in chain.msgList_get('mParents'):
            for constraint in CONSTRAINTS.get_constraintsFrom(parent, typeFilter='aimConstraint'):
                constraintNode = cgmMeta.asMeta(constraint)
                if axis is None:
                    constraintNode.worldUpType = 4
                else:
                    constraintNode.worldUpType = 2
                    constraintNode.upVector = axis.p_vector
                    constraintNode.worldUpVector = axis.p_vector

        chain.up = str(axis)

        return str(axis)

    def chain_create(self, objs = None,
                     fwd = None, up=None,
                     name = None,
                     upSetup = "guess",
                     extendStart = None,
                     extendEnd = True,
                     mNucleus=None,
                     upControl = None,
                     aimUpMode = None,
                     **kws):
        
        _str_func = 'chain_create'
        
        if not objs:
            _sel = mc.ls(sl=1)
            if _sel:objs = _sel
        
        ml = cgmMeta.asMeta( objs, noneValid = True )
        ml_baseTargets = copy.copy(ml)
        
        if not ml:
            return log.warning("No objects passed. Unable to chain_create")
            
        if not name:
            name = ml[-1].p_nameBase
                    
        _idx = self.get_nextIdx()
        

        #Make our sub group...
        mGrp = self.doCreateAt(setClass=1)
        mGrp.p_parent = self
        mGrp.rename("chain_{0}_grp".format(name))
        mGrp.dagLock()
        self.connectChildNode(mGrp.mNode,'chain_{0}'.format(_idx),'owner')
        
        
        #holders and dat...
        ml_targets = []
        ml_posLocs = []
        ml_aim_locs = []
        
        fwd = fwd or self.fwd
        up = up or self.up
        upSetup = upSetup or self.upSetup
        extendStart = extendStart or self.extendStart
        extendEnd = extendEnd or self.extendEnd
        upControl = upControl or self.upControl
        aimUpMode = aimUpMode or self.aimUpMode
        
        #fwdAxis = simpleAxis(fwd)
        #upAxis = simpleAxis(up)

        fwdAxis = TRANS.closestAxisTowardObj_get(ml[0], ml[1])
        upAxis = TRANS.crossAxis_get(fwdAxis)

        mGrp.doStore('fwd', fwdAxis.p_string)
        mGrp.doStore('up', upAxis.p_string)

        #Curve positions...
        l_pos = []
        
        if upSetup == 'manual':
            if len(ml) < 2:
                log.debug(cgmGEN.logString_msg(_str_func, 'Single count. Adding extra handle.'))
                mLoc = ml[0].doLoc()
                mLoc.rename("chain_{0}_end_loc".format(name))
                _size = DIST.get_bb_size(ml[0],True,'max')
                mLoc.p_position = ml[0].getPositionByAxisDistance(fwdAxis.p_string,_size)
                ml.append(mLoc)
                mLoc.p_parent = mGrp
            
            for obj in ml:
                l_pos.append(obj.p_position)
                
                
            _v_baseDist = DIST.get_distance_between_points(l_pos[-1],l_pos[-2])
            _v_baseDist = MATHUTILS.Clamp(_v_baseDist, .5,None)

            _p_baseExtend = DIST.get_pos_by_axis_dist(ml[-1],
                                                      fwdAxis.p_string,
                                                      _v_baseDist)
            
            
            if extendEnd:
                log.debug(cgmGEN.logString_msg(_str_func, 'extendEnd...'))
                
                extendEnd = VALID.valueArg(extendEnd)
                
                if issubclass(type(extendEnd),bool):#VALID.boolArg(extendEnd):
                    log.debug(cgmGEN.logString_msg(_str_func, 'extendEnd | guess'))
                    l_pos.append(_p_baseExtend)
                elif extendEnd:
                    log.debug(cgmGEN.logString_msg(_str_func, 'extendEnd | {0}'.format(extendEnd)))
                    
                    l_pos.append( DIST.get_pos_by_axis_dist(ml[-1],
                                                            fwdAxis.p_string,
                                                            extendEnd ))                            
            else:
                l_pos.append( _p_baseExtend)
        
            if extendStart:
                f_extendStart = VALID.valueArg(extendStart)
                if f_extendStart:
                    l_pos.insert(0, DIST.get_pos_by_axis_dist(ml[0],
                                                              fwdAxis.inverse.p_string,
                                                              f_extendStart ))
                    
        else:
            log.debug(cgmGEN.logString_msg(_str_func, 'Resolving aim'))
            if len(ml) < 2:
                return log.error(cgmGEN.logString_msg(_str_func, 'Single count. Must use manual upSetup and aim/up args'))
            
            for obj in ml:
                l_pos.append(obj.p_position)
            
            _vecEnd = MATHUTILS.get_vector_of_two_points(l_pos[-2],l_pos[-1])
            if extendEnd:
                log.debug(cgmGEN.logString_msg(_str_func, 'extendEnd...'))
                
                extendEnd = VALID.valueArg(extendEnd)
                
                if issubclass(type(extendEnd),bool):#VALID.boolArg(extendEnd):
                    log.debug(cgmGEN.logString_msg(_str_func, 'extendEnd | guess'))
                    
                    l_pos.append( DIST.get_pos_by_vec_dist(l_pos[-1], _vecEnd,
                                                           (DIST.get_distance_between_points(l_pos[-2],l_pos[-1])/2)))
                elif extendEnd:
                    log.debug(cgmGEN.logString_msg(_str_func, 'extendStart | {0}'.format(extendEnd)))
                    
                    l_pos.append( DIST.get_pos_by_vec_dist(l_pos[-1], _vecEnd,
                                                           extendEnd))
            
            if extendStart:
                f_extendStart = VALID.valueArg(extendStart)
                if f_extendStart:
                    log.debug(cgmGEN.logString_msg(_str_func, 'extendStart...'))
                    
                    _vecStart = MATHUTILS.get_vector_of_two_points(l_pos[1],l_pos[0])
                    
                    l_pos.insert(0, DIST.get_pos_by_vec_dist(l_pos[0],
                                                             _vecStart,
                                                             f_extendStart))

        #pprint.pprint(l_pos)
        
        #for i,p in enumerate(l_pos):
        #    LOC.create(position=p,name='p_{0}'.format(i))
            
        crv = CORERIG.create_at(create='curve',l_pos= l_pos, baseName = name)
        mInCrv = cgmMeta.asMeta(crv)
        mInCrv.rename("{0}_inCrv".format(name))
        mGrp.connectChildNode(mInCrv.mNode,'mInCrv')
        mc.select(cl=1)

        # make the dynamic setup
        log.debug(cgmGEN.logString_sub(_str_func,'dyn setup'))
        b_existing = False
        b_existing_nucleus = False
        
        mHairSys = self.getMessageAsMeta('mHairSysShape')
        if mHairSys:
            mHairSysDag = mHairSys.getTransform(asMeta=1)
            log.info(cgmGEN.logString_msg(_str_func,'Using existing system: {0}'.format(mHairSys.mNode)))
            mc.select(mHairSysDag.mNode, add=True)
            b_existing = True
            
        if self.useExistingNucleus or mNucleus:
            mNucleus = self.get_nucleus(mNucleus)
            if mNucleus:
                #mc.select(mNucleus.mNode,add=1)
                b_existing_nucleus = True
                log.info(cgmGEN.logString_msg(_str_func,'Using existing nucleus: {0}'.format(mNucleus.mNode)))
                self.connectChildNode(mNucleus.mNode,'mNucleus')
        
        mc.select(mInCrv.mNode,add=True)
        mel.eval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0" }')

        # get relevant nodes
        follicle = mc.listRelatives(mInCrv.mNode,parent=True)[0]
        mFollicle = cgmMeta.asMeta(follicle)
        mFollicle.rename("{0}_foll".format(name))
        parent = mFollicle.getParent(asMeta=1)
        mFollicle.p_parent = mGrp
        mFollicleShape = mFollicle.getShapes(1)[0]
        mc.delete(parent.mNode)
        
        _follicle = mFollicle.mNode
        mGrp.connectChildNode(mFollicle.mNode,'mFollicle','group')
        
        follicleShape = mFollicleShape.mNode#mc.listRelatives(mFollicle.mNode, shapes=True)[0]
        _hairSystem = mc.listRelatives( mc.listConnections('%s.currentPosition' % follicleShape)[0],
                                        shapes=True)[0]
        if not b_existing:
            mHairSys = cgmMeta.asMeta(_hairSystem)
            mHairSysDag = mHairSys.getTransform(asMeta=1)
            
            mHairSysDag.rename("{0}_hairSys".format(self.baseName))
            self.connectChildNode(mHairSysDag.mNode,'mHairSysDag','owner')
            self.connectChildNode(mHairSys.mNode,'mHairSysShape','owner')
            
            mHairSysDag.p_parent = self
            _hairSystem = mHairSys.mNode
            
        outCurve = mc.listConnections('%s.outCurve' % _follicle)[0]
        mCrv = cgmMeta.asMeta(outCurve)
        parent = mCrv.getParent(asMeta=1)

        outCurveShape = mc.listRelatives(mCrv.mNode, shapes=True)[0]
        mCrv.p_parent = mGrp.mNode
        
        mc.delete(parent.mNode)
        _nucleus = mc.listConnections( '%s.currentState' % mHairSys.mNode )[0]
        
        if not b_existing_nucleus:
            mNucleus = cgmMeta.asMeta(_nucleus)
            mNucleus.rename("cgmDynFK_nucleus")            
            #self.connectChildNode(mNucleus.mNode,'mNucleus','owner')
            self.connectChildNode(mNucleus.mNode,'mNucleus')
            
            if self.startFrame is not None:
                mNucleus.startFrame = self.startFrame
        else:
            #Because maya is crappy we gotta manually wire the existing nucleus
            ##startFrame out to startFrame in
            ##outputObjects[x] - nextState
            ##shape.currentState>inputActive[x]
            ##shape.startState>inputActiveStart[x]
            if cgmMeta.asMeta(_nucleus).mNode != mNucleus.mNode:
                mc.delete(_nucleus)

            _useNucleus = mNucleus.mNode

            """
            _useIdx = ATTR.get_nextCompoundIndex(mNucleus.mNode,'outputObjects')
            log.info("useIdx: {0}".format(_useIdx))
            ATTR.connect('{0}.outputObjects[{1}]'.format(_useNucleus,_useIdx),'{0}.nextState'.format(_hairSystem))
            ATTR.connect('{0}.currentState'.format(_hairSystem),'{0}.inputActive[{1}]'.format(_useNucleus,_useIdx))
            ATTR.connect('{0}.startState'.format(_hairSystem),'{0}.inputActiveStart[{1}]'.format(_useNucleus,_useIdx))"""            
            
            
        mParent = ml[0].getParent(asMeta=1)
        if not mParent:
            mParent = ml[0].doGroup(1,1,
                                    asMeta=True,
                                    typeModifier = 'dynFKParent',
                                    setClass='cgmObject')
        #else:
            #mParent.getParent(asMeta=1)
        
        mGrp.connectChildNode(mCrv.mNode,'mOutCrv','group')

        #self.follicles.append(follicle)
        #self.outCurves.append(outCurve)
        
        # set default properties
        mFollicleShape.pointLock = 1
        #mc.setAttr( '%s.pointLock' % follicleShape, 1 )
        mc.parentConstraint(ml[0].getParent(), _follicle, mo=True)
        
        # create locators on objects
        locators = []
        prs = []
        
        ml_locs = []
        ml_aims = []
        ml_prts = []
        
        _upVector = None
        if upSetup == 'guess':
            log.debug(cgmGEN.logString_msg(_str_func, 'Resolving up/aim'))
            poci_base = CURVES.create_pointOnInfoNode(mInCrv.mNode,1)
            mPoci_base = cgmMeta.asMeta(poci_base)
            
            _upVector = mPoci_base.normalizedNormal
            log.debug(cgmGEN.logString_msg(_str_func, "upVector: {0}".format(_upVector)))        
        
        
        #Let's make an up object as the parent of the root isn't good enough
        mUp = ml[0].doCreateAt(setClass=1)
        mUp.rename("chain_{0}_up".format(name))
        mUp.p_parent = mGrp
        
        if _upVector:
            SNAP.aim_atPoint(mUp.mNode,
                             DIST.get_pos_by_vec_dist(mUp.p_position,
                                                      _upVector,
                                                      10),aimAxis='y+',upAxis='z+')
        
        if upControl:
            log.debug(cgmGEN.logString_msg(_str_func,'upControl'))
            if len(ml_baseTargets)>1:
                sizeControl = DIST.get_distance_between_targets([mObj.mNode for mObj in ml_baseTargets],True)
            else:
                sizeControl = DIST.get_bb_size(ml[0],True,'max')
                
            crv = CURVES.create_controlCurve(mUp.mNode,'arrowSingle', size= sizeControl, direction = 'y+')
            CORERIG.shapeParent_in_place(mUp.mNode, crv, False)
            mUpGroup = mUp.doGroup(True,True,
                                   asMeta=True,
                                   typeModifier = 'master',
                                   setClass='cgmObject')
            
            mc.parentConstraint(ml[0].getParent(), mUpGroup.mNode, mo=True)
            
            
        else:
            mc.parentConstraint(ml[0].getParent(), mUp.mNode, mo=True)
            
        
        # create control joint chain
        mc.select(cl=True)
        chain = []
        for obj in ml:
            if len(chain) > 0:
                mc.select(chain[-1])
            jnt = mc.joint(name='%s_%s_jnt' % (name, obj.p_nameBase))
            SNAP.matchTarget_set(jnt, obj.mNode)
            mObj = cgmMeta.asMeta(jnt)
            mObj.doSnapTo(mObj.getMessageAsMeta('cgmMatchTarget'))

            chain.append(jnt)

        mc.parent(chain[0], _follicle)
        mInCrv.p_parent = mGrp

        mc.bindSkin(mInCrv.mNode, chain[0], ts=True)


        log.debug(cgmGEN.logString_msg(_str_func,'aimUpMode: {0}'.format(aimUpMode)))
        
        
        for i, mObj in enumerate(ml):
            if not i:
                mUpUse = mUp
            else:
                mUpUse = ml_locs[-1]
                
            mLoc = cgmMeta.asMeta( LOC.create(mObj.getNameLong()) )
            loc = mLoc.mNode
            ml_locs.append(mLoc)
            #loc = LOC.create(mObj.getNameLong())
            
            mAim = mLoc.doGroup(False,False,
                                 asMeta=True,
                                 typeModifier = 'aim',
                                 setClass='cgmObject')
            ml_aims.append(mAim)
            #aimNull = mc.group(em=True)
            #aimNull = mc.rename('%s_aim' % mObj.getShortName())
            
            poc = CURVES.create_pointOnInfoNode(outCurveShape)
#mc.createNode('pointOnCurveInfo', name='%s_pos' % loc)
            mPoci_obj = cgmMeta.asMeta(poc)
            mPoci_obj.rename('%s_pos' % loc)
            pocAim = CURVES.create_pointOnInfoNode(outCurveShape)
            #mc.createNode('pointOnCurveInfo', name='%s_aim' % loc)
            
            pr = CURVES.getUParamOnCurve(loc, outCurve)
            mPoci_obj.parameter = pr
            
            #mc.connectAttr( '%s.worldSpace[0]' % outCurveShape, '%s.inputCurve' % poc, f=True )
            #mc.connectAttr( '%s.worldSpace[0]' % outCurveShape, '%s.inputCurve' % pocAim, f=True )

            #mc.setAttr( '%s.parameter' % poc, pr )
            
            if i < len(ml)-1:
                nextpr = CURVES.getUParamOnCurve(ml[i+1], outCurve)
                mc.setAttr('%s.parameter' % pocAim, (nextpr))# + pr))# * .5)
            else:
                if extendStart:
                    mc.setAttr( '%s.parameter' % pocAim, len(ml)+1 )                    
                else:
                    mc.setAttr( '%s.parameter' % pocAim, len(ml) )
                    
                    
            
            mLocParent = mLoc.doGroup(False,False,
                                      asMeta=True,
                                      typeModifier = 'pos',
                                      setClass='cgmObject')
            ml_prts.append(mLocParent)
            #locParent = mc.group(em=True)
            #locParent = mc.rename( '%s_pos' % mObj.getShortName() )

            mc.connectAttr( '%s.position' % mPoci_obj.mNode, '%s.translate' % mLocParent.mNode)
            mc.connectAttr( '%s.position' % pocAim, '%s.translate' % mAim.mNode)
            
            
            
            if aimUpMode == 'master':
                aimConstraint = mc.aimConstraint( mAim.mNode,
                                                  mLocParent.mNode,
                                                  aimVector=fwdAxis.p_vector,
                                                  upVector = upAxis.p_vector,
                                                  worldUpType = "objectrotation",
                                                  worldUpVector = upAxis.p_vector,
                                                  worldUpObject = mUp.mNode )
            elif aimUpMode == 'orientToMaster':
                mc.orientConstraint( mUp.mNode,
                                     mLocParent.mNode,
                                     maintainOffset = 1)
                
            elif aimUpMode == 'sequential':
                aimConstraint = mc.aimConstraint( mAim.mNode,
                                                  mLocParent.mNode,
                                                  aimVector=fwdAxis.p_vector,
                                                  upVector = upAxis.p_vector,
                                                  worldUpType = "objectrotation",
                                                  worldUpVector = upAxis.p_vector,
                                                  worldUpObject = mUpUse.mNode )                
            elif aimUpMode == 'joint':
                aimConstraint = mc.aimConstraint( mAim.mNode,
                                                  mLocParent.mNode,
                                                  aimVector=fwdAxis.p_vector,
                                                  upVector = upAxis.p_vector,
                                                  worldUpType = "objectrotation",
                                                  worldUpVector = upAxis.p_vector,
                                                  worldUpObject = chain[i] )  
            elif aimUpMode == 'curveNormal':
                mUpLoc = mLoc.doGroup(False,False,
                                      asMeta=True,
                                      typeModifier = 'up',
                                      setClass='cgmObject')
                mUpLoc.p_parent = mLocParent
                
                aimConstraint = mc.aimConstraint( mAim.mNode,
                                                  mLocParent.mNode,
                                                  aimVector=fwdAxis.p_vector,
                                                  upVector = upAxis.p_vector,
                                                  worldUpType = "object")
                
                mPlusMinusAverage = cgmMeta.cgmNode(name="{0}_pma".format(mObj.p_nameBase),
                                                    nodeType = 'plusMinusAverage')
                mPlusMinusAverage.operation = 3
                
                mPoci_obj.doConnectOut('position','{0}.input3D[0]'.format(mPlusMinusAverage.mNode))
                mPoci_obj.doConnectOut('normalizedNormal','{0}.input3D[1]'.format(mPlusMinusAverage.mNode))
                mUpLoc.doConnectIn('translate','{0}.output3D'.format(mPlusMinusAverage.mNode))

            
            
            mLoc.p_parent = mLocParent
            mAim.p_parent = mGrp
            mLocParent.p_parent = mGrp
            
            #mc.parent(loc, locParent)
        
        mCrv.rename("{0}_outCrv".format(name))
        mCrvParent = mCrv.getParent(asMeta=1)
        mCrvParent.p_parent = mGrp
        
        mGrp.msgList_connect('mLocs',ml_locs)
        mGrp.msgList_connect('mAims',ml_aims)
        mGrp.msgList_connect('mParents',ml_prts)
        mGrp.msgList_connect('mTargets',ml)
        mGrp.msgList_connect('mBaseTargets',ml_baseTargets)
        mGrp.msgList_connect('mObjJointChain',chain)
        mGrp.doStore('cgmName', name)

        mNucleus.doConnectOut('startFrame',"{0}.startFrame".format(mHairSys.mNode))
        
    def report(self):
        _d = {'up':self.up,
              'fwd':self.fwd,
              'baseName':self.baseName}
        
        pprint.pprint(_d)
        pprint.pprint(self.get_dat())
        
    def get_dat(self):
        _res = {'mNucleus':self.getMessageAsMeta('mNucleus'),
                'mHairSysDag':self.getMessageAsMeta('mHairSysDag'),
                'mHairSysShape':self.getMessageAsMeta('mHairSysShape'),
                'chains':{},
                }
        
        ml_chains = self.msgList_get('chain')
        for i,mGrp in enumerate(ml_chains):
            _d = {'mGrp':mGrp,
                  'mFollicle':mGrp.getMessageAsMeta('mFollicle'),
                  'mInCrv':self.getMessageAsMeta('mInCrv'),
                  'mOutCrv':mGrp.getMessageAsMeta('mOutCrv'),
                  }
            
            for lnk in 'mLocs','mAims','mParents','mTargets', 'mObjJointChain':
                _d[lnk] = mGrp.msgList_get(lnk)
                
            _res['chains'][i] = _d
        
        #pprint.pprint(_res)
        return _res
    
    def toggle(self,arg):
        _str_func = 'toggle'
        log.info("|{0}| >> {1}".format(_str_func,arg))
        
        mNucleus=self.getMessageAsMeta('mNucleus')
        if mNucleus:
            mNucleus.enable = arg
            
        mHairSysShape=self.getMessageAsMeta('mHairSysShape')
        if mHairSysShape:
            if arg:
                mHairSysShape.simulationMethod = 3
            else:
                mHairSysShape.simulationMethod = 0
                
        if arg:
            log.warning("|{0}| >> Playback rate set to every frame".format(_str_func))
            mc.playbackOptions(e=True, playbackSpeed = 0, maxPlaybackSpeed = 0)
        else:
            mc.playbackOptions(e=True, playbackSpeed = 1, maxPlaybackSpeed = 0)
            #playbackOptions -e -playbackSpeed 0 -maxPlaybackSpeed 0;
            
        
    def profile_load(self,arg='default',clean=True):
        mNucleus=self.getMessageAsMeta('mNucleus')
        mHairSysShape=self.getMessageAsMeta('mHairSysShape')
        if not mNucleus and mHairSysShape:
            return log.warning("Nucleus and hairShape required for profile load")
        
        
        profile_load(mNucleus,arg,clean=clean)
        profile_load(mHairSysShape,arg,clean=clean)
        
        
        
        return 
        #reload(dynFKPresets)
        _d = dynFKPresets.d_chain.get(arg)
        if not _d:
            return log.warning("Profile has no data: {0}".format(arg))
        
        d_n = _d.get('n') or {}
        d_hs = _d.get('hs') or {}
        
        pprint.pprint(_d)
        _nucleus = mNucleus.mNode
        for a,v in d_n.iteritems():
            log.debug("Nucleus || {0} | {1}".format(a,v))
            try:
                mNucleus.__setattr__(a,v)
            except Exception,err:
                log.warning("Nucleus | Failed to set: {0} | {1} | {2}".format(a,v,err))
                
        for a,v in d_hs.iteritems():
            log.debug("mHairSys || {0} | {1}".format(a,v))            
            try:
                mHairSysShape.__setattr__(a,v)
            except Exception,err:
                log.warning("mHairSys | Failed to set: {0} | {1} | {2}".format(a,v,err))
        return True
       
    def get_chains(self, idx=None):
        chains = self.msgList_get('chain')
        if idx:
            chains = [chains[idx]]

        return chains

    def targets_connect(self,idx=None):
        for chain in self.get_chains(idx):
            for i,mObj in enumerate(chain.msgList_get('mTargets')):
                mc.parentConstraint([chain.msgList_get('mLocs')[i].mNode, mObj.mNode])
    def targets_disconnect(self,idx=None):
        for chain in self.get_chains(idx):
            for i,mObj in enumerate(chain.msgList_get('mTargets')):
                _buffer = mObj.getConstraintsTo()

                if _buffer:
                    mc.delete(_buffer)
    
    def targets_select(self,idx=None):
        ml= []
        for chain in self.get_chains(idx):
            for i,mObj in enumerate(chain.msgList_get('mTargets')):
                if 'loc' not in mObj.mNode:
                    ml.append(mObj)
        
        mc.select([mObj.mNode for mObj in ml])
        return ml

                
    def delete(self):
        pass



#Profiles ========================================================================================
d_shortHand = {'nucleus':'n',
               'hairSystem':'hs'}
l_ignore = ['currentTime','startFrame']

d_attrMap = {'n':{'gravity':['gravity','gravityDirection',],
                  'air':['airDensity','windSpeed','windDirection','windNoise'],
                  'groundPlane':['usePlane','planeOrigin','planeNormal',
                                 'planeBounce','planeFriction','planeStickiness'],
                  'solverAttributes':['subSteps','maxCollisionIterations',
                                      'collisionLayerRange', 'timingOutput']},
             'hs':{'base':['simulationMethod','displayQuality'],
                   'clumpAndHairShape':['hairsPerClump','subSegments','thinning','clumpTwist','bendFollow',
                                        'clumpWidth','hairWidth', 'clumpWidthScale', 'hairWidthScale','clumpInterpolation',
                                        'curl','curlFrequency',
                                        'clumpCurl', 'clumpFlatness'],
                   'collisions':['collide','selfCollide',
                                 'collisionFlag','selfCollisionFlag',
                                 'collideStrength', 'collisionLayer','numCollideNeighbors',
                                 'collideGround','collideOverSample',
                                 'maxSelfCollisionIterations','drawCollideWidth',
                                 'maxSelfCollideIterations','collideWidthOffset','selfCollideWidthScale',
                                 'solverDisplay','bounce','friction','stickiness','staticCling'],
                   'dynamicProperties':['stretchResistance','compressionResistance','bendResistance',
                                        'twistResistance', 'extraBendLinks', 'restLengthScale',
                                        'stiffnessScale', 'startCurveAttract', 'attractionDamp',
                                        'attractionScale','bend','bendAnisotropy'],
                   'forces':['mass','drag','tangentialDrag','motionDrag','damp','stretchDamp', 'dynamicsWeight'],
                   'turbulance':['turbulenceStrength','turbulenceFrequency','turbulenceSpeed'],
                   'others':['detailNoise','noStretch','diffuseRand','displacementScale','groundHeight',
                             'iterations','interpolationRange','lengthFlex','stiffness','repulsion',
                             'noise','noiseFrequency','noiseMethod','valRand']}}

def get_dat(target = None, differential=False, module = dynFKPresets):
    _str_func = 'get_dat'
    mTar = cgmMeta.asMeta(target, noneValid = True)
    if not mTar:
        return log.error(cgmGEN.logString_msg(_str_func, "No valid target"))
    
    _type = mTar.getMayaType()
    _key = d_shortHand.get(_type,_type)    
    log.info(cgmGEN.logString_msg(_str_func,"mTar: {0} | {1}".format(_type, mTar)))
    
    #_d = ATTR.get_attrsByTypeDict(mTar.mNode)
    #pprint.pprint(_d)
    _res = {}
    _tar = mTar.mNode
    for section,l in d_attrMap.get(_key).iteritems():
        log.debug(cgmGEN.logString_msg(_str_func,section))        
        for a in l:
            if a in l_ignore:
                continue
            try:
                _v = ATTR.get(_tar,a)
                log.debug(cgmGEN.logString_msg(_str_func,"{0} | {1}".format(a,_v)))        
                
            except Exception,err:
                log.error("Failed to query: {0} | {1} | {2}".format(_tar, a, err))
            if _v is not None:
                _res[str(a)] = _v
            
    if differential:
        log.debug(cgmGEN.logString_msg(_str_func,"Getting differential"))
        _d_base = profile_get('base')
        _d_baseSet = _d_base.get(_key,module)
        if _d_baseSet:
            log.debug(cgmGEN.logString_msg(_str_func,"Found base set..."))
            _res_use = {}
            for k,v in  _res.iteritems():
                if v != _d_baseSet[k]:
                    log.debug(cgmGEN.logString_msg(_str_func,"Storing: {0} | {1}".format(k,v)))                    
                    _res_use[k] = v
                #else:
                #    log.debug(cgmGEN.logString_msg(_str_func,"Same: {0} | {1}".format(k,v)))
            return {_key:_res_use}
        
    #pprint.pprint(_res)
    return _res

def profile_get(arg = None, module = dynFKPresets ):
    reload(module)
    return module.__dict__.get(arg)

def profile_load(target = None, arg = None, module = dynFKPresets, clean = True):
    _str_func = 'profile_apply'
    mTar = cgmMeta.asMeta(target, noneValid = True)
    if not mTar:
        return log.error(cgmGEN.logString_msg(_str_func, "No valid target"))
    
    _type = mTar.getMayaType()
    _key = d_shortHand.get(_type,_type)    
    log.info(cgmGEN.logString_msg(_str_func,"mTar: {0} | {1}".format(_type, mTar)))
    
    _d_profile = profile_get(arg,module)
    if not _d_profile:
        log.warning("Invalid profile: {0}".format(arg))        
        return False
    
    _d_type = _d_profile.get(_key)
    if not _d_type:
        log.warning("No {0}  dat".format(_type))
        return False
    
    if clean:
        d_use = profile_get('base',module).get(_key)
        d_use.update(_d_type)
    else:
        d_use = _d_type
    
    _node = mTar.mNode
    for a,v in d_use.iteritems():
        log.debug("{0} || {1} | {2}".format(_type, a,v))
        try:
            ATTR.set(_node, a, v)
            #mNucleus.__setattr__(a,v)
        except Exception,err:
            log.warning("{3} | Failed to set: {0} | {1} | {2}".format(a,v,err, _type))    
    
    
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
cgmMeta.r9Meta.registerMClassInheritanceMapping()
