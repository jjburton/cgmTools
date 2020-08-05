"""
------------------------------------------
general_utils: cgm.core.rig
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------


================================================================
"""
# From Python =============================================================
import copy
import re
import time
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
import Red9.core.Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rigging_utils as RIG
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.math_utils as MATH
#reload(DIST)
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.name_utils as NAMES
import cgm.core.lib.search_utils as SEARCH
import cgm.core.lib.position_utils as POS
from cgm.core.classes import NodeFactory as NODEFAC

from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import euclid as EUCLID
from cgm.core.lib import locator_utils as LOC
#reload(ATTR)
@cgmGEN.Timer
def reset_channels_fromMode(nodes=None, mode = 0,selectedChannels=None):
    """
    :mode
        0 - all
        1 - transformsOnly
        2 - keyableOnly
    """
    if not nodes:
        nodes = mc.ls(sl=True)
        if not nodes:
            return    
         
    if mode == 0:
        _d = {'transformsOnly':False,
              'keyableOnly':False}
    elif mode == 1:
        _d = {'transformsOnly':True,
              'keyableOnly':False}
    elif mode == 2:
        _d = {'transformsOnly':True,
              'keyableOnly':True}
    
    if selectedChannels == None:
        try:selectedChannels = cgmMeta.cgmOptionVar('cgmVar_KeyMode').value
        except:
            log.debug("nope...")
            selectedChannels = False
    _d['selectedChannels'] = selectedChannels
    _d['nodes'] = nodes
    reset_channels(**_d)

@cgmGEN.Timer
def reset_channels(nodes=None,selectedChannels=False, transformsOnly=False, excludeChannels=None, keyableOnly=False):
    '''
    Modified from Morgan Loomis' great reset call to expand options...
    '''
    gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
    _reset = {}
    if not nodes:
        nodes = mc.ls(sl=True)
        if not nodes:
            return

    if excludeChannels:
        if not isinstance(excludeChannels, (list, tuple)):
            excludeChannels = [excludeChannels]

    chans = None
    if selectedChannels:
        chans = mc.channelBox(gChannelBoxName, query=True, sma=True)

    l_trans = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ','tx','ty','yz','rx','ry','rz','sx','sy','sz']


    for obj in nodes:
        #mObj = r9Meta.MetaClass(obj)

        attrs = chans
        if not chans:
            attrs = mc.listAttr(obj, keyable=True, unlocked=True)
            if excludeChannels:
                attrs = [x for x in attrs if x not in excludeChannels]

        if transformsOnly:
            attrs = [x for x in attrs if x in l_trans]
        if keyableOnly:
            attrs = [x for x in attrs if ATTR.is_keyable(obj,x)]

        d_defaults = {}
        for plug in ['defaultValues','transResets']:
            if ATTR.has_attr(obj, plug):
                d_defaults = getattr(r9Meta.MetaClass(obj),plug)

        if not attrs:
            log.warning("{0} resetAttrs | no attributes offered!".format(obj))            
            continue
        for a in attrs:
            try:
                if transformsOnly is not None and transformsOnly:
                    if ATTR.get_nameLong(obj,a) not in l_trans:
                        continue
                dVal = d_defaults.get(a)
                if dVal is not None:
                    default = dVal
                else:
                    default = mc.attributeQuery(a, listDefault=True, node=obj)[0]
                ATTR.set(obj,a,default)
                _reset[a] = default
            except Exception,err:
                log.error("{0}.{1} resetAttrs | error: {2}".format(obj, a,err))
    
    #pprint.pprint(vars())
    return _reset

    return




def fbx_cleaner(delete = False, spaceString = '03FBXASC032'):
    """
    Find all the sill attributes fbx adds on import

    :parameters:
        delete | whether to delete all userDefined attrs or not
        spaceString | Search string for what fbx did with spaces from max or other app. Replaces with underscore
    """
    _str_func = 'fbx_cleaner'
    log.debug("|{0}| >> ...".format(_str_func))

    _res = {}
    for o in mc.ls():
        _res[o] = []
        _l = mc.listAttr(o,userDefined=True) or []
        for a in _l:
            _res[o].append(a)
        _shapes = TRANS.shapes_get(o)

        if _shapes:
            for s in _shapes:
                _res[s] = []
                _l = mc.listAttr(s,userDefined=True) or []
                for a in _l:
                    _res[s].append(a)

    print cgmGEN._str_hardBreak
    l_renamed = []
    for k,l in _res.iteritems():
        if l:
            print cgmGEN._str_subLine
            print(cgmGEN._str_baseStart * 2 + " node: '{0}' | attrs: {1}...".format(k,len(l)))
            for i,a in enumerate(l):
                print("   {0} | '{1}'".format(i,a))
                if delete:
                    ATTR.delete(k,a)
        if spaceString:
            if spaceString in NAMES.get_base(k) and k not in l_renamed:
                new = mc.rename(k, NAMES.get_base(k).replace(spaceString,'_'))
                print(" Rename  {0} | '{1}'".format(k,new))
                l_renamed.append(k)


    print cgmGEN._str_hardBreak


def matchValue_iterator(matchObj = None,
                        matchAttr = None,
                        drivenObj = None,
                        drivenAttr = None,
                        driverAttr = None, 
                        minIn = -179, maxIn = 179, maxIterations = 40, matchValue = None,
                        iterMode = 'step'):
    """
    Started with Jason Schleifer's afr js_iterator and 'tweaked'

    matchObj - The object to match to the driven
    driven - the object moved by the driver


    """
    _str_func = 'matchValue_iterator'
    log.debug("|{0}| >> ...".format(_str_func))    

    if type(minIn) not in [float,int]:raise ValueError,"matchValue_iterator>>> bad minIn: %s"%minIn
    if type(maxIn) not in [float,int]:raise ValueError,"matchValue_iterator>>> bad maxIn: %s"%maxIn

    __matchMode__ = False

    #>>> Data gather and arg check        
    mi_matchObj = cgmMeta.validateObjArg(matchObj,'cgmObject',noneValid=True)
    d_matchAttr = cgmMeta.validateAttrArg(matchAttr,noneValid=True)

    if mi_matchObj:
        __matchMode__ = 'matchObj'
        minValue = minIn
        maxValue = maxIn 

    elif d_matchAttr:
        __matchMode__ = 'matchAttr'
    elif matchValue is not None:
        __matchMode__ = 'value'
    else:
        raise ValueError,"|{0}| >> No match given. No matchValue given".format(_str_func)


    __drivenMode__ = False
    mi_drivenObj = None

    if drivenObj and drivenAttr:
        d_drivenAttr = cgmMeta.validateAttrArg("{0}.{1}".format(drivenObj,drivenAttr),noneValid=True)        
    else:
        mi_drivenObj = cgmMeta.validateObjArg(drivenObj,'cgmObject',noneValid=True)
        d_drivenAttr = cgmMeta.validateAttrArg(drivenAttr,noneValid=True)

    if mi_drivenObj and not drivenAttr:#not an object match but a value
        __drivenMode__ = 'object'
    elif d_drivenAttr:
        __drivenMode__ = 'attr'
        mPlug_driven = d_drivenAttr['mi_plug']
        f_baseValue = mPlug_driven.value	
        minRange = float(f_baseValue - 10)
        maxRange = float(f_baseValue + 10)  
        mPlug_driven
        log.debug("|{0}| >> Attr mode. Attr: {1} | baseValue: {2} ".format(_str_func,mPlug_driven.p_combinedShortName,f_baseValue))

    else:
        raise ValueError,"|{0}| >> No driven given".format(_str_func)


    d_driverAttr = cgmMeta.validateAttrArg(driverAttr,noneValid=False)
    mPlug_driver = d_driverAttr['mi_plug']
    if not mPlug_driver:
        raise ValueError,"|{0}| >> No driver given".format(_str_func)


    log.debug("|{0}| >> Source mode: {1} | Target mode: {2}| Driver: {3}".format(_str_func,__matchMode__,__drivenMode__,mPlug_driver.p_combinedShortName))

    # Meat ==========================================================================================
    b_autoFrameState = mc.autoKeyframe(q=True, state = True)
    if b_autoFrameState:
        mc.autoKeyframe(state = False)

    minValue = float(minIn)
    maxValue = float(maxIn)

    minUse = copy.copy(minValue)
    maxUse = copy.copy(maxValue)
    f_lastClosest = None
    f_lastValue = None
    cnt_sameValue = 0
    b_matchFound = None
    b_firstIter = True
    d_valueToSetting = {}

    #Source type: value
    for i in range(maxIterations):
        if __matchMode__ == 'value':
            if __drivenMode__ == 'attr':
                if iterMode == 'bounce':
                    log.debug("matchValue_iterator>>> Step : %s | min: %s | max: %s | baseValue: %s | current: %s"%(i,minValue,maxValue,f_baseValue,mPlug_driven.value))
                    if MATH.is_float_equivalent(mPlug_driven.value,matchValue,3):
                        log.debug("matchValue_iterator>>> Match found: %s == %s | %s: %s | step: %s"%(mPlug_driven.p_combinedShortName,matchValue,mPlug_driver.p_combinedShortName,minValue,i))  			    
                        b_matchFound = minValue
                        break

                    f_currentDist = abs(matchValue-mPlug_driven.value)
                    mPlug_driver.value = minValue#Set to min
                    f_minDist = abs(matchValue-mPlug_driven.value)#get Dif
                    f_minSetValue = mPlug_driven.value
                    mPlug_driver.value = maxValue#Set to max
                    f_maxDist = abs(matchValue-mPlug_driven.value)#Get dif
                    f_maxSetValue = mPlug_driven.value

                    f_half = ((maxValue-minValue)/2.0) + minValue#get half
                    #First find range
                    if f_minSetValue > matchValue or f_maxSetValue < matchValue:
                        log.error("Bad range, alternate range find. minSetValue = %s > %s < maxSetValue = %s"%(f_minSetValue,matchValue,f_maxSetValue))

                    if not MATH.is_float_equivalent(matchValue,0) and not MATH.is_float_equivalent(minValue,0) and not MATH.is_float_equivalent(f_minSetValue,0):
                        #if none of our values are 0, this is really fast
                        minValue = (minValue * matchValue)/f_minSetValue
                        log.debug("matchValue_iterator>>> Equated: %s"%minValue)		    
                        f_closest = f_minDist
                        mPlug_driver.value = minValue#Set to min			
                    else:	
                        if f_minDist>f_maxDist:#if min dif greater, use half as new min
                            if f_half < minIn:
                                raise StandardError, "half min less than minValue"
                                f_half = minIn
                            minValue = f_half
                            #log.debug("matchValue_iterator>>>Going up")
                            f_closest = f_minDist
                        else:
                            if f_half > maxIn:
                                raise StandardError, "half max less than maxValue"			    
                                f_half = maxIn			
                            maxValue = f_half
                            #log.debug("matchValue_iterator>>>Going down")  
                            f_closest = f_maxDist

                elif iterMode == 'step':
                    currentDriven = mPlug_driven.value
                    if i == 0:
                        log.debug("|{0}| >> First step getting base data...".format(_str_func))                        
                        f_lastValue = currentDriven
                        _stepSmall = .000001
                        minStep = _stepSmall
                        _stepBig = 10
                        f_stepBase = mPlug_driver.value
                        f_stepEnd = f_stepBase + _stepBig

                        """
                        mPlug_driver.value = currentDriven + .1
                        f_up = mPlug_driven.value 

                        mPlug_driver.value = currentDriven - .1
                        f_down = mPlug_driven.value

                        diff_up = abs(f_baseValue - f_down)
                        diff_dn = abs(f_baseValue - f_up)
                        log.debug("|{0}| >> up :{1} | down: {2}".format(_str_func,diff_up,diff_dn))
                        if diff_up > diff_dn:
                            _dir = 'up'
                            _mult = 1
                        else:
                            _dir = 'dn'
                            _mult = -1"""

                    log.info(cgmGEN._str_subLine)

                    log.debug("|{0}| >> Iter :{1} | stepBase: {2} | stepEnd: {5} | step: {6} | current: {3} | match: {4}".format(_str_func,
                                                                                                                                 i,
                                                                                                                                 f_stepBase,
                                                                                                                                 currentDriven,
                                                                                                                                 matchValue,
                                                                                                                                 f_stepEnd,
                                                                                                                                 _stepBig))
                    if MATH.is_float_equivalent(currentDriven,matchValue,3):
                        log.debug("|{0}| >> Match found...".format(_str_func))
                        b_matchFound = f_stepBase
                        break

                    f_currentDist = (matchValue-currentDriven)
                    mPlug_driver.value = f_stepBase#setp min
                    f_minValue = mPlug_driven.value
                    f_minDist = (matchValue-mPlug_driven.value)#get Dif

                    mPlug_driver.value = f_stepEnd
                    f_maxDist = (matchValue-mPlug_driven.value)#Get dif
                    f_maxValue = mPlug_driven.value


                    f_stepHalf = f_stepBase + ((_stepBig/2.0))
                    f_half = f_stepHalf
                    mPlug_driver.value = f_half
                    f_halfDist = (matchValue-mPlug_driven.value)#Get dif
                    f_halfValue = mPlug_driven.value

                    log.debug("|{0}| >> minValue: {1} | halfValue: {3} | maxValue: {2} | current: {4}".format(_str_func,f_minValue,f_maxValue,f_halfValue,currentDriven))

                    log.debug("|{0}| >> minDist: {1} | halfDist: {3} | maxDist: {2} |  | currentDist: {4}".format(_str_func,f_minDist,f_maxDist,f_halfDist,f_currentDist))

                    log.debug("|{0}| >> baseStep: {1} | halfStep: {3} | endStep: {2} | ".format(_str_func,f_stepBase,f_stepEnd,f_stepHalf))

                    if matchValue > f_minValue and matchValue < f_maxValue:
                        log.debug("|{0}| >> Between...".format(_str_func))
                        #(minStep *_mult)
                        if matchValue < f_halfValue:
                            log.debug("|{0}| >> Less than half".format(_str_func))
                            f_stepBase = f_stepBase
                            f_stepEnd = f_stepHalf
                        elif matchValue > f_halfValue:
                            log.debug("|{0}| >> more than half".format(_str_func))
                            f_stepBase = f_stepHalf
                            f_stepEnd = f_stepBase + (_stepBig)
                        else:
                            f_stepBase = f_stepBase + (_stepSmall)

                        _stepBig = _stepBig/2.0

                        #minStep = f_lastValue + minStep
                    elif matchValue > f_maxValue:
                        log.debug("|{0}| >> Greater".format(_str_func))
                        _dir = 'up'
                        _mult = 1
                        _stepBig = 10
                        f_stepBase = f_stepEnd
                        f_stepEnd = f_stepEnd + (_stepBig)

                    elif matchValue < f_minValue:
                        log.debug("|{0}| >> Less...".format(_str_func))
                        _dir = 'dn'
                        _stepBig = -10
                        f_stepBase = f_stepBase + (_stepBig)
                        f_stepEnd = f_stepBase + (_stepBig)
                    else:
                        raise ValueError,"nope"

                    f_closest = f_stepBase


                #Old method
                """
		mPlug_driver.value = minValue#Set to min
		f_minDist = abs(matchValue-mPlug_driven.value)#get Dif
		f_minSetValue = mPlug_driven.value
		mPlug_driver.value = maxValue#Set to max
		f_maxDist = abs(matchValue-mPlug_driven.value)#Get dif
		f_maxSetValue = mPlug_driven.value

		f_half = ((maxValue-minValue)/2.0) + minValue#get half	

		#First find range
		if not MATH.is_float_equivalent(matchValue,0) and not MATH.is_float_equivalent(minValue,0) and not MATH.is_float_equivalent(f_minSetValue,0):
		    #if none of our values are 0, this is really fast
		    minValue = (minValue * matchValue)/f_minSetValue
		    log.debug("matchValue_iterator>>> Equated: %s"%minValue)		    
		    f_closest = f_minDist
		    mPlug_driver.value = minValue#Set to min		    
		elif b_firstIter:
		    log.debug("matchValue_iterator>>> first iter. Trying matchValue: %s"%minValue)		    		    
		    b_firstIter = False
		    minValue = matchValue
		    f_closest = f_minDist		    
		elif f_minSetValue > matchValue or f_maxSetValue < matchValue:
		    log.debug("matchValue_iterator>>> Finding Range....")		    
		    if matchValue < mPlug_driven.value:
			#Need to shift our range down
			log.debug("matchValue_iterator>>> Down range: minSetValue: %s"%f_minSetValue)
			f_baseValue = f_maxDist		    
			minValue = f_baseValue - f_minDist
			maxValue = f_baseValue + f_minDist
			f_closest = f_minDist			
		    elif matchValue > mPlug_driven.value:
			#Need to shift our range up
			log.debug("matchValue_iterator>>> Up range: maxSetValue: %s"%f_maxSetValue)  
			f_baseValue = f_minDist		    
			minValue = f_baseValue - f_maxDist
			maxValue = f_baseValue + f_maxDist
			f_closest = f_maxDist			
		else:	
		    if f_minDist>f_maxDist:#if min dif greater, use half as new min
			if f_half < minIn:f_half = minIn
			minValue = f_half
			#log.debug("matchValue_iterator>>>Going up")
			f_closest = f_minDist
		    else:
			if f_half > maxIn:f_half = maxIn			
			maxValue = f_half
			#log.debug("matchValue_iterator>>>Going down")  
			f_closest = f_maxDist"""

                #log.debug("matchValue_iterator>>>f1: %s | f2: %s | f_half: %s"%(f_minDist,f_maxDist,f_half))  
                #log.debug("#"+'-'*50)

                if f_closest == f_lastClosest:
                    cnt_sameValue +=1
                    if cnt_sameValue >3:
                        log.error("matchValue_iterator>>> Value unchanged. Bad Driver. lastValue: %s | currentValue: %s"%(f_lastValue,mPlug_driven.value))		
                        break
                else:
                    cnt_sameValue = 0 
                f_lastClosest = f_closest
            else:
                log.warning("matchValue_iterator>>> driven mode not implemented with value mode: %s"%__drivenMode__)
                break		

        #>>>>>matchObjMode
        elif __matchMode__ == 'matchObj':
            pos_match = mc.xform(mi_matchObj.mNode, q=True, ws=True, rp=True)
            pos_driven = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            log.debug("matchValue_iterator>>> min: %s | max: %s | pos_match: %s | pos_driven: %s"%(minValue,maxValue,pos_match,pos_driven))  						    
            if MATH.is_vector_equivalent(pos_match,pos_driven,2):
                log.debug("matchValue_iterator>>> Match found: %s <<pos>> %s | %s: %s | step: %s"%(mi_matchObj.getShortName(),mi_drivenObj.getShortName(),mPlug_driver.p_combinedShortName,minValue,i))  			    
                b_matchFound = mPlug_driver.value
                break

            mPlug_driver.value = minValue#Set to min
            pos_min = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            #f_minDist = MATH.mag( MATH.list_subtract(pos_match,pos_min))#get Dif
            f_minDist = distance.returnDistanceBetweenObjects(mi_drivenObj.mNode,mi_matchObj.mNode)

            mPlug_driver.value = maxValue#Set to max
            pos_max = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            f_maxDist = distance.returnDistanceBetweenObjects(mi_drivenObj.mNode,mi_matchObj.mNode)
            f_half = ((maxValue-minValue)/2.0) + minValue#get half	

            if f_minDist>f_maxDist:#if min dif greater, use half as new min
                minValue = f_half
                f_closest = f_minDist
            else:
                maxValue = f_half
                f_closest = f_maxDist	

            if f_minDist==f_maxDist:
                minValue = minValue + .1

            if f_closest == f_lastClosest:
                cnt_sameValue +=1
                if cnt_sameValue >3:
                    log.error("matchValue_iterator>>> Value unchanged. Bad Driver. lastValue: %s | currentValue: %s"%(f_lastValue,mPlug_driver.value))		
                    break
            else:
                cnt_sameValue = 0 
            f_lastClosest = f_closest

            log.debug("matchValue_iterator>>>f1: %s | f2: %s | f_half: %s"%(f_minDist,f_maxDist,f_half))  
            log.debug("#"+'-'*50)	    

        else:
            log.warning("matchValue_iterator>>> matchMode not implemented: %s"%__matchMode__)
            break

    #>>> Check autokey back on
    if b_autoFrameState:
        mc.autoKeyframe(state = True) 

    if b_matchFound is not None:
        return b_matchFound
    #log.warning("matchValue_iterator>>> Failed to find value for: %s"%mPlug_driven.p_combinedShortName)    
    return False

@cgmGEN.Timer
def get_metaNodeSnapShot():
    #return [cgmMeta.cgmNode(n) for n in SEARCH.get_nodeSnapShot()]
    #_res= [r9Meta.MetaClass(n) for n in SEARCH.get_nodeSnapShot()]
    #return cgmMeta.asMeta(SEARCH.get_nodeSnapShot())
    _res =  SEARCH.get_nodeSnapShot()
    
def get_nodeSnapShot(asMeta = 1):
    _str_func = 'get_nodeSnapShot'
    #return mc.ls(l=True,dag=True)    
    _res = mc.ls(l=True)
    if asMeta:
        return cgmMeta.asMeta(_res)
    return _res
    
def get_nodeSnapShotDifferential(l,asMeta=1):
    l2 = get_nodeSnapShot(asMeta)
    _res = []
    for o in l2:
        if o not in l:
            _res.append(o)
    return _res

def check_nameMatches(self,mlControls,justReport = False):
    _str_func = 'check_nameMatches'
    log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)

    _nameMatches = False
    mlControls  = cgmMeta.validateObjListArg(mlControls)

    for mCtrl in mlControls:
        if mCtrl.getNameMatches(True):
            _nameMatches = True
    if _nameMatches and not justReport:
        raise ValueError,"Fix this name match"
    return True

def store_and_name(mObj,d):
    _str_func = 'store_and_name'
    for t,v in d.iteritems():
        if v in [None]:
            continue
        log.debug("|{0}| >> {1} | {2}.".format(_str_func,t,v))            
        mObj.doStore(t,v)
    mObj.doName()

def plug_insertNewValues(driven = None, drivers = [], replace = False, mode = 'multiply'):
    """
    Given an attribute, add in new values to it. If it has a plug, use that 
    """
    try:
        _str_func = 'plug_insertNewValues'
        log.debug("|{0}| >>  ".format(_str_func)+ '-'*80)

        if mode not in ['multiply']:
            raise ValueError,"Mode not supported: {0}".format(mode)

        d_driven = cgmMeta.validateAttrArg(driven)
        mPlug = d_driven['mPlug']

        ml_drivers = []
        mPreDriver = mPlug.getDriver(asMeta=True)
        log.debug("|{0}| >>  Pre Driver: {1}".format(_str_func,mPreDriver))

        for d in drivers:
            d_driver = cgmMeta.validateAttrArg(d)
            if d_driver:
                ml_drivers.append(d_driver['mPlug'])
                log.debug("|{0}| >>  Driver: {1}".format(_str_func,d_driver['mPlug']))
            else:
                log.debug("|{0}| >>  Failed to validate: {1}".format(_str_func,d))


        if not ml_drivers:
            raise ValueError, "No drivers validated"

        if not replace:
            ml_drivers.insert(0,mPreDriver[0])

        if len(ml_drivers) < 2:
            raise ValueError,"Must have more than two drivers. Found: {0}".format(ml_drivers)
        ATTR.break_connection(mPlug.p_combinedName)

        lastNode = None
        for i,mDriver in enumerate(ml_drivers[:-1]):
            if not lastNode:
                lastNode = mc.createNode('multDoubleLinear')
                mDriver.doConnectOut(lastNode + '.input1')
                ml_drivers[i+1].doConnectOut(lastNode + '.input2')
            else:
                newNode = mc.createNode('multDoubleLinear')
                ATTR.connect(lastNode+'.output',newNode + '.input1')
                ml_drivers[i+1].doConnectOut(newNode + '.input2')

                lastNode=newNode

        ATTR.connect(lastNode+'.output',mPlug.p_combinedName)







    except Exception,err:
        #pprint.pprint(vars())
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
        raise Exception,err
    
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
        #pprint.pprint(d_dat[1]['driven'])
        #pprint.pprint(d_dat[2]['driven'])

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
                        NODEFAC.argsToNodes(a).doBuild()

                    zeroMid = 0
                    zero1 = 0
                    zero2 = 0
                    
                    """
                    1
                    'dist1Norm': [9.0, 7.202468187218439, 4.077128668939619],
                    'dist1On': [10.0, 8.20246818721844, 5.077128668939619],
                    'dist2': [2.055457665682541, 3.632951746156667, 4.537290944991008],
                    'dist2Norm': [4.077128668939596, 7.206186711809993, 9.0],
                    'dist2On': [5.077128668939596, 8.206186711809993, 10.0],
                    
                    2
                    'dist1On': [10.0, 7.77630635569009, 4.3748619466292595],
                    'dist2': [1.6982080013368184, 3.4097921203066526, 4.528739916989064],
                    'dist2Norm': [3.3748619466301477, 6.7763063556899725, 9.0],
                    'dist2On': [4.374861946630148, 7.7763063556899725, 10.0],
                    
                    """
                    

                    try:zero1 = dat['dist1On'][i+1]
                    except:zero1 = 0
                    
                    if i:
                        try:zero2 = dat['dist2On'][i-1]
                        except:zero2 = 0
                        
                    #try:zeroMid = dat['distMidOn'][i-1]
                    #except:zeroMid= 0
                        
                   #if i:
                   #     zero1 = dat['dist1On'][i-1]

                    #try:zero2 = dat['dist2On'][i+1]
                    #except:zero2 = 0
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
        
        

def rename_deformers(nodes= [],deformerTypes='all'):
    if not nodes:
        nodes = mc.ls(sl=1)
        
    ml_nodes = cgmMeta.asMeta(nodes)
    for mObj in ml_nodes:
        for mDef in mObj.getDeformers(deformerTypes,True):
            log.info("Renaming: {0}".format(mDef))
            mc.rename(mDef.mNode, "{0}_{1}".format(mObj.p_nameBase,
                                                   SEARCH.get_tagInfoShort(mDef.getMayaType())))
            #mDef.doName()
            

def objectDat_get(nodes = []):
    if not nodes:
        nodes = mc.ls(sl=1)
        
    _res = {}
    mNodes = cgmMeta.asMeta(nodes)
    for mNode in mNodes:
        try:
            _res[mNode.mNode] = {'pos':mNode.p_position, 'orient':mNode.p_orient}
        except Exception,err:
            log.error("{0} | {1}".format(mNode,err))
    pprint.pprint(_res)
    return _res

def objectDat_set(dat = {}, position = True, orient = True):
    for Node,d in dat.iteritems():
        try:
            log.info(Node)
            mNode = cgmMeta.asMeta(Node)
            if position:
                mNode.p_position = d['pos']
            if orient:
                mNode.p_orient = d['orient']
        except Exception,err:
            log.error("{0} | {1}".format(mNode,err))
    
    
def get_planeIntersect(planeSource = None, target = None, planeAxis = 'z+', objAxis = 'z+', mark = False):
    _str_func = 'get_planeIntersect'
    
    if target:
        mTarget = cgmMeta.asMeta(target)
    else:
        mTarget = cgmMeta.asMeta(mc.ls(sl=1))
        if not mTarget:
            return log.error(cgmGEN.logString_msg( _str_func, 'No Target'))
        mTarget = mTarget[0]
    
    mObj = cgmMeta.asMeta(planeSource)
        
    planePoint = VALID.euclidVector3Arg(mObj.p_position)
    planeNormal = VALID.euclidVector3Arg(mObj.getAxisVector(planeAxis))

    
    rayPoint = VALID.euclidVector3Arg(mTarget.p_position)
    rayDirection = VALID.euclidVector3Arg(mTarget.getAxisVector(objAxis))
    
    plane = EUCLID.Plane( EUCLID.Point3(planePoint.x, planePoint.y, planePoint.z),
                          EUCLID.Point3(planeNormal.x, planeNormal.y, planeNormal.z) )
    pos = plane.intersect( EUCLID.Line3( EUCLID.Point3(rayPoint.x, rayPoint.y, rayPoint.z), EUCLID.Vector3(rayDirection.x, rayDirection.y, rayDirection.z) ) )
    
    if mark:
        LOC.create(position = pos, name = 'pewpew_planeIntersect')
        
    return pos
