#=================================================================================================================================================
#=================================================================================================================================================
#	sdk - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of functions for working with SDK stuff
# 
# ARGUMENTS:
# 	rigging
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#   0.11 = 4/2/2011 - added documentation for all the scripts written during River Monsters gig
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel

from cgm.lib import guiFactory
from cgm.lib import search
from cgm.lib import lists

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Naming Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def copySetDrivenKey(sourceDriver,targetDriver,drivenObject,targetObject):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    ACKNOWLEDGEMENT:
    Jason Schleifer's AFR Materials.

    DESCRIPTION:
    Copies an SDK

    ARGUMENTS:
    sourceDriver(string)
    targetDriver(string)
    drivenObject(string)
    targetObject(string)

    RETURNS:
    driverCurves(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Get driven attributes
    drivenAttributes = mc.setDrivenKeyframe(drivenObject,q=True, dn=True)
    if not drivenAttributes:
        guiFactory.warning('No driven attributes found on %s' %drivenObject)
    else:
        # Get drivers
        for attr in drivenAttributes:
            print attr
            drivers = mc.setDrivenKeyframe(attr,q=True, dr=True)
            if not sourceDriver in drivers:
                guiFactory.warning('%s not found in the sdk drivers' %sourceDriver)
            else:
                # Get curve info
                curveInfo = returnSetDrivenCurveInfo(sourceDriver,attr)
                
                for key in curveInfo.keys():
                    attrBuffer = attr.split('.')
                    # set the SDK's
                    mc.setDrivenKeyframe(targetObject+'.'+attrBuffer[-1], currentDriver = targetDriver, driverValue = key,value = curveInfo[key])
                
                #Copy Curve tangents and stuff
                oldCurve = returnDriverCurve(sourceDriver,attr)
                newCurve = returnDriverCurve(targetDriver,attr)
                
                weight = mc.keyTangent(oldCurve[0],q=True, wt=True)
                mc.keyTangent(newCurve[0],edit=True,wt=weight[0])
                
                #copy the bits
                copyAnimCurveSettingsToCurve(oldCurve[0],newCurve[0])





def returnDriverCurve(driverAttribute,drivenObject):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    ACKNOWLEDGEMENT:
    Jason Schleifer's AFR Materials.

    DESCRIPTION:
    Returns the anim curve from a driver to a driven object

    ARGUMENTS:
    driverAttribute(string)
    drivenObject(string)

    RETURNS:
    driverCurves(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    driverFuture = mc.listConnections(driverAttribute,type = 'animCurve')
    buffer = mc.listConnections(drivenObject,s=True)
    drivenPast = mc.listHistory(buffer[0])

    return lists.returnMatchList(driverFuture,drivenPast)



def returnSetDrivenCurveInfo(driverAttribute,drivenObject):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    DESCRIPTION:
    Returns the info for a sdk curve

    ARGUMENTS:
    driverAttribute(string)
    drivenObject(string)

    RETURNS:
    curveInfo(dict){time:value,etc...}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    driverCurve = returnDriverCurve(driverAttribute,drivenObject)
    
    if driverCurve:
        setDrivenCurveInfo = {}
        keyCnt = mc.keyframe(driverCurve[0],q=True, keyframeCount = True)
        curveValues = mc.keyframe(driverCurve[0],q=True, vc=True)

        for cnt in range(keyCnt):
            
            # Because maya is stupid and the syntax for this in pythong unfathomable my mere mortals such as I
            mel.eval('string $animCurve = "%s";' %driverCurve[0])
            mel.eval('int $cnt = %i;' %cnt)
            keyTimeValue = mel.eval('keyframe -index $cnt -query -fc $animCurve')
            
            setDrivenCurveInfo[keyTimeValue[0]] = (curveValues[cnt])
            
        return setDrivenCurveInfo



def returnCurveKeyInfoWIP(animCurve):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    DESCRIPTION:
    Returns the info for a sdk curve

    ARGUMENTS:
    driverAttribute(string)
    drivenObject(string)

    RETURNS:
    curveInfo(dict){time:value,etc...}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    setCurveKeyInfo = {}
    keyCnt = mc.keyframe(animCurve,q=True, keyframeCount = True)

    for cnt in range(keyCnt):
        individualCurveKeyInfo = {}
        # Because maya is stupid and the syntax for this in pythong unfathomable my mere mortals such as I
        mel.eval('string $animCurve = "%s";' %driverCurve[0])
        mel.eval('int $cnt = %i;' %cnt)
        keyTimeValue = mel.eval('keyframe -index $cnt -query -fc $animCurve')
        
        individualCurveKeyInfo['tangentsLocked'] = (mc.keyTangent())
        
        
        
        
        setDrivenCurveInfo[keyTimeValue[0]] = (individualCurveKeyInfo)
        
    return setDrivenCurveInfo



def copyAnimCurveSettingsToCurve(sourceCurve,targetCurve):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    DESCRIPTION:
    Returns the info for a sdk curve

    ARGUMENTS:
    driverAttribute(string)
    drivenObject(string)

    RETURNS:
    curveInfo(dict){time:value,etc...}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    keyCnt = mc.keyframe(sourceCurve,q=True, keyframeCount = True)
    
    # Because maya is stupid and the syntax for this in python is unfathomable my mere mortals such as I
    mel.eval('string $sourceCurve = "%s";' %sourceCurve)
    mel.eval('string $targetCurve = "%s";' %targetCurve)
    
    for cnt in range(keyCnt):
        mel.eval('int $key = %i;' %cnt)
        
        #Lock
        mel.eval("$lock = `keyTangent -index $key -query -lock $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -lock $lock[0] $targetCurve;" )     

        #outY
        mel.eval("$outY = `keyTangent -index $key -query -oy $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -oy $outY[0] $targetCurve;" )  
        
        #outX
        mel.eval("$outX = `keyTangent -index $key -query -ox $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -ox $outX[0] $targetCurve;" ) 
        
        #outWeight
        mel.eval("$outWeight = `keyTangent -index $key -query -ow $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -ow $outWeight[0] $targetCurve;" ) 
        
        #inY
        mel.eval("$inY = `keyTangent -index $key -query -iy $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -iy $inY[0] $targetCurve;" )  
        
        #inX
        mel.eval("$inX = `keyTangent -index $key -query -ix $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -ix $inX[0] $targetCurve;" ) 
        
        #inWeight
        mel.eval("$inWeight = `keyTangent -index $key -query -iw $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -iw $inWeight[0] $targetCurve;" ) 
        
        #outAngle
        mel.eval("$outAngle = `keyTangent -index $key -query -oa $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -oa $outAngle[0] $targetCurve;" )  
        
        #inAngle
        mel.eval("$inAngle = `keyTangent -index $key -query -ia $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -ia $inAngle[0] $targetCurve;" ) 
        
        #inTangentType
        mel.eval("$inTangentType = `keyTangent -index $key -query -itt $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -itt $inTangentType[0] $targetCurve;" )  
        
        #outTangentType
        mel.eval("$outTangentType = `keyTangent -index $key -query -ott $sourceCurve`;")
        mel.eval("keyTangent -e -index $key -ott $outTangentType[0] $targetCurve;" ) 
        



def returnDrivenJoints(driverAttribute):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    DESCRIPTION:
    Returns driven objects from a driver Attribute

    ARGUMENTS:
    obj(string)
    attr(string)

    RETURNS:
    attrInfo(varies)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    drivenJoints = []

    attrConnections = mc.listConnections(driverAttribute, scn = True, s = False, t = 'animCurve')
    if attrConnections:
        for animCurve in attrConnections:
            drivenJoint = search.seekDownStream(animCurve,'joint')
            if mc.objExists(drivenJoint):
                drivenJoints.append(drivenJoint)
        drivenJoints = lists.returnListNoDuplicates(drivenJoints)
        return drivenJoints

    else:
        guiFactory.warning('No anim curves found to be connected')
        return False
    
        """
		for($animCurve in $attrConnections){
			$drivenJoint = seekDownStream($animCurve,"joint",0);
			$jointList[$i] = $drivenJoint;
			$i = $i + 1;
			}				
			$drivenJointList = stringArrayRemoveDuplicates($jointList);	
			$i = 0;
		"""


def updateSDKWithCurrentObjectInfo (obj, sdkAttribute, driverValues = [0,1]):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    asdf

    ARGUMENTS:
    jointList(list) - list of joints in order


    RETURNS:
    newJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>> Get the info
    channelKeyList = ('translateX','translateY','translateZ','rotateX','rotateY','rotateZ')
    for channel in channelKeyList:
        for v in driverValues:
            mc.setDrivenKeyframe(obj,attribute = channel, currentDriver = sdkAttribute, driverValue = v)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
