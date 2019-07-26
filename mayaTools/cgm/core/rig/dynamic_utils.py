import maya.cmds as mc
from cgm.core import cgm_General as cgmGEN
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.euclid as euclid
import cgm.core.lib.rigging_utils as CORERIG
import cgm.core.lib.locator_utils as LOC
import cgm.core.lib.curve_Utils as CURVE
from cgm.core.cgmPy.validateArgs import simpleAxis
import cgm.core.lib.name_utils as NAMES
import cgm.core.cgm_Meta as cgmMeta
import pprint
import maya.mel as mel


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
            pr = CURVE.getUParamOnCurve(loc, outCurve)
            
            mc.connectAttr( '%s.worldSpace[0]' % outCurveShape, '%s.inputCurve' % poc, f=True )
            mc.connectAttr( '%s.worldSpace[0]' % outCurveShape, '%s.inputCurve' % pocAim, f=True )

            mc.setAttr( '%s.parameter' % poc, pr )
            
            if i < len(objs)-1:
                nextpr = CURVE.getUParamOnCurve(objs[i+1], outCurve)
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
    hairSystem = None
    mHairSystem = None
    nucleus = None
    mNucleus = None
    baseName = None
    fwd = None
    up = None
    
    def __init__(self,node = None, name = None,
                 objs = None, fwd = 'z+', up = 'y+',
                 hairSystem=None, baseName = 'hair',
                 *args,**kws):
        """ 

        """
        ### input check  
        _sel = mc.ls(sl=1)
        if not objs:
            if _sel:objs = _sel
        
        super(cgmDynFK, self).__init__(node = node,name = name,nodeType = 'transform') 
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
        
        if hairSystem:
            self.hairSystem = hairSystem
            self.mHairSystem = cgmMeta.asMeta(hairSystem,noneValid=True)
        
        self.fwd = fwd
        self.up = up
                
        self.baseName = baseName
        
        self.rename("{0}_dynFK".format(self.baseName))
                
        if objs:self.chain_create(objs, fwd, up, name)        
        
        self.report()
        
        if _sel:
            mc.select(_sel)
    
    def get_nextIdx(self):
        return ATTR.get_nextAvailableSequentialAttrIndex(self.mNode, "chain")
        
    def chain_create(self, objs = None,
                     fwd = None, up=None,
                     name = None):
        
        _str_func = 'chain_create'
        
        ml = cgmMeta.asMeta( objs )

        if not ml:
            return log.warning("No objects passed. Unable to chain_create")
            
        if name is None:
            name = ml[-1].p_nameBase
                    
        _idx = self.get_nextIdx()
        
        #Make our sub group...
        mGrp = self.doCreateAt(setClass=1)
        mGrp.p_parent = self
        mGrp.rename("chain_{0}_{1}_grp".format(_idx,name))
        mGrp.dagLock()
        self.connectChildNode(mGrp.mNode,'chain_{0}'.format(_idx),'owner')
        
        
        #holders and dat...
        ml_targets = []
        ml_posLocs = []
        ml_aim_locs = []
        
        fwd = fwd or self.fwd
        up = up or self.up

        fwdAxis = simpleAxis(fwd)
        upAxis = simpleAxis(up)

        #Curve positions...
        l_pos = []
        
            
        for obj in ml:
            l_pos.append(obj.p_position)
            
        if len(ml)>1:
            l_pos.append( DIST.get_pos_by_axis_dist(ml[-1],
                                                           fwdAxis.p_string,
                                                           DIST.get_distance_between_points(l_pos[-1],l_pos[-2])) )
    
            l_pos.insert(0, DIST.get_pos_by_axis_dist(ml[0],
                                                      fwdAxis.inverse.p_string,
                                                      DIST.get_distance_between_points(l_pos[0],l_pos[1])*.5) )
        else:
            pass

        crv = CORERIG.create_at(create='curve',l_pos= l_pos, baseName = name)
        

        # make the dynamic setup
        log.debug(cgmGEN.logString_sub(_str_func,'dyn setup'))
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
        mFollicle.getParent(asMeta=1).p_parent = self
        
        _follicle = mFollicle.mNode
        mGrp.connectChildNode(mFollicle.mNode,'mFollicle','group')
        
        
        follicleShape = mc.listRelatives(mFollicle.mNode, shapes=True)[0]
        _hairSystem = mc.listRelatives( mc.listConnections('%s.currentPosition' % follicleShape)[0],
                                        shapes=True)[0]
        if not b_existing:
            mHairSys = cgmMeta.asMeta(_hairSystem)
            mHairSysDag = mHairSys.getTransform(asMeta=1)
            
            mHairSysDag.rename("{0}_hairSys".format(self.baseName))
            self.connectChildNode(mHairSysDag.mNode,'mHairSysDag','owner')
            self.connectChildNode(mHairSys.mNode,'mHairSysShape','owner')
            
            mHairSysDag.p_parent = self
            self.hairSystem = mHairSys.mNode
            
        outCurve = mc.listConnections('%s.outCurve' % _follicle)[0]
        outCurveShape = mc.listRelatives(outCurve, shapes=True)[0]
        _nucleus = mc.listConnections( '%s.currentState' % self.hairSystem )[0]
        if not b_existing:
            mNucleus = cgmMeta.asMeta(_nucleus)
            mNucleus.rename("{0}_nucleus".format(self.baseName))            
            self.connectChildNode(mNucleus.mNode,'mNucleus','owner')
            mNucleus.p_parent=self
            
        
        ml[0].getParent(asMeta=1).select()
        mCrv = cgmMeta.asMeta(outCurve)
        mGrp.connectChildNode(mCrv.mNode,'mOutCrv','group')

        #self.follicles.append(follicle)
        #self.outCurves.append(outCurve)
        
        # set default properties
        mc.setAttr( '%s.pointLock' % follicleShape, 1 )
        mc.parentConstraint(ml[0].getParent(), _follicle, mo=True)
        
        # create locators on objects
        locators = []
        prs = []
        
        ml_locs = []
        ml_aims = []
        ml_prts = []
        
        #Let's make an up object as the parent of the root isn't good enough
        mUp = ml[0].doCreateAt(setClass=1)
        mUp.rename("chain_{0}_{1}_up".format(_idx,name))
        mUp.p_parent = mGrp
        mc.parentConstraint(ml[0].getParent(), mUp.mNode, mo=True)
        
        for i, mObj in enumerate(ml):
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
            
            
            poc = mc.createNode('pointOnCurveInfo', name='%s_pos' % loc)
            pocAim = mc.createNode('pointOnCurveInfo', name='%s_aim' % loc)
            pr = CURVE.getUParamOnCurve(loc, outCurve)
            
            mc.connectAttr( '%s.worldSpace[0]' % outCurveShape, '%s.inputCurve' % poc, f=True )
            mc.connectAttr( '%s.worldSpace[0]' % outCurveShape, '%s.inputCurve' % pocAim, f=True )

            mc.setAttr( '%s.parameter' % poc, pr )
            
            if i < len(ml)-1:
                nextpr = CURVE.getUParamOnCurve(ml[i+1], outCurve)
                mc.setAttr('%s.parameter' % pocAim, (nextpr + pr) * .5)
            else:
                mc.setAttr( '%s.parameter' % pocAim, len(ml)+1 )
            
            mLocParent = mLoc.doGroup(False,False,
                                      asMeta=True,
                                      typeModifier = 'pos',
                                      setClass='cgmObject')
            ml_prts.append(mLocParent)
            #locParent = mc.group(em=True)
            #locParent = mc.rename( '%s_pos' % mObj.getShortName() )

            mc.connectAttr( '%s.position' % poc, '%s.translate' % mLocParent.mNode)
            mc.connectAttr( '%s.position' % pocAim, '%s.translate' % mAim.mNode)
            
            aimConstraint = mc.aimConstraint( mAim.mNode, mLocParent.mNode, aimVector=fwdAxis.p_vector, upVector = upAxis.p_vector, worldUpType = "objectrotation", worldUpVector = upAxis.p_vector, worldUpObject = mUp.mNode )
            
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
        

    def report(self):
        _d = {'hairSystem':self.hairSystem,
              'up':self.up,
              'fwd':self.fwd,
              'baseName':self.baseName}
        
        pprint.pprint(_d)
        
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
                  'mOutCrv':mGrp.getMessageAsMeta('mOutCrv'),
                  }
            
            for lnk in 'mLocs','mAims','mParents','mTargets':
                _d[lnk] = mGrp.msgList_get(lnk)
                
            _res['chains'][i] = _d
        
        pprint.pprint(_res)
        return _res
    
    def delete(self):
        pass        
        
        
        
d_profiles = {'default':{'n':{'subSteps':12,
                              'maxCollisionIterations':49,
                              'gravity':98}}}

#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================      
cgmMeta.r9Meta.registerMClassInheritanceMapping()
