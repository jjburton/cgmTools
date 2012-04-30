#=================================================================================================================================================
#=================================================================================================================================================
#	settings - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Functions to get the locations of the rigger conf files, and create default ones
# 
# ARGUMENTS:
#	Nothing
# 
# AUTHOR:
#	David Bokser (under the supervision of python guru Josh Burton) - dbokser@gmail.com
#	http://www.davidbokser.com
#	Copyright 2011 David Bokser - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 08/22/2011 - initial release
#=================================================================================================================================================

import os

def getNamesDictionaryFile():
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Function to get location of cgmNames.conf settings file

        ARGUMENTS:
        Nothing

        RETURNS:
        path(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cgmNames.conf')
        if not os.path.exists(path):
                print "Names Dictionary Not Found! Creating..."
                path = makeDefaultNamesDictionary()

        return path

def getTypesDictionaryFile():
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Function to get location of cgmTypes.conf settings file

        ARGUMENTS:
        Nothing

        RETURNS:
        path(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cgmTypes.conf')
        if not os.path.exists(path):
                print "Types Dictionary Not Found! Creating..."
                path = makeDefaultTypesDictionary()

        return path

def getSettingsDictionaryFile():
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Function to get location of cgmSettings.conf settings file

        ARGUMENTS:
        Nothing

        RETURNS:
        path(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cgmSettings.conf')
        if not os.path.exists(path):
                print "Settings Dictionary Not Found! Creating..."
                path = makeDefaultSettingsDictionary()

        return path

def makeDefaultNamesDictionary():
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Function to create default cgmNames.conf settings file

        ARGUMENTS:
        Nothing

        RETURNS:
        path(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        defaultDictionary = """### Normal stuff




## rigger stuff
module:part
modules:parts

### Types

null:null
blendShapeGeo:bsGeo
object:obj
skinCluster:skinNode


### General acgmreviations
left:l 
right:r 
blendShape:bs
quickSelectSet:qss
characterSet:cs
template:tmpl


### Controls
controlMaster:all

### Body Stuff

#Torso
cog:cog
head:head
neck:neck
torso:spine


#Arms
clavicle:clav
arm:arm
uprArm:uprArm
elbow:elbow
lwrArm:lwrArm

#Leg
leg:leg
uprLeg:uprLeg
knee:knee
lwrLeg:lwrLeg

#Digits
finger1:thumb
finger2:index
finger3:middle
finger4:ring
finger5:pinky
toe1:big
toe2:index
toe3:middle
toe4:ring
toe5:pinky
"""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cgmNames.conf')
        if not os.path.exists(path):
                f = open(path, 'w')
                f.write(defaultDictionary)
                f.close()
        else:
                print "File already exists. Will not overwrite!"
                return False

        return path

def makeDefaultTypesDictionary():
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Function to create default cgmTypes.conf settings file

        ARGUMENTS:
        Nothing

        RETURNS:
        path(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        defaultDictionary = """### Null stuff
masterNull:mainNull
rigNull:rigNull
partsNull:partsNull
module:part

#> Templates
templateRoot:tmplRoot
templateNull:tmplNull
templateObject:tmplObj
templateLocator:tmplLoc
templateCurve:tmplCrv

#> Info Stuff
infoNull:info
skinJointNull:sknJntNull
ignore:ignore



### Custom Types
null:null
group:grp
object:obj
skinCluster:skinNode
blendShapeGeo:bsGeo

### Controls
controlMaster:placer
controlAnim:anim

### Sets
quickSelectSet:qss
characterSet:cs

### Maya Types
camera:cam
transform:transf
group:grp
locator:loc


subdiv:subGeo
mesh:geo
nurbsCurve:crv
nurbsSurface:surf


ambientLight:amLght
spotLight:spLght
pointLight:pntLght


joint:jnt
skinJoint:skinJnt
ikHandle:ikH
ikEffector:ikE


###Contraints
orientConstraint:orConst
parentConstraint:prntConst
pointConstraint:pntConst
aimConstraint:aimConst
scaleConstraint:scConst
geometryConstraint:geoConst
normalConstraint:normConst
tangentConstraint:tangConst
poleVectorConstraint:pvConst


### Nodes
pointOnSurfaceInfoNode:posInfoNode
frameCacheNode:fCacheNode
plusMinusAverageNode:pmAvNode
closestPointOnSurfaceNode:cPntOnSurfNode
blendShapeNode:bsNode
multiplyDivideNode:mdNode
remapNode:remapNode
reverseNode:revNode
"""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cgmTypes.conf')
        if not os.path.exists(path):
                f = open(path, 'w')
                f.write(defaultDictionary)
                f.close()
        else:
                print "File already exists. Will not overwrite!"
                return False

        return path

def makeDefaultSettingsDictionary():
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Function to create default cgmSettings.conf settings file

        ARGUMENTS:
        Nothing

        RETURNS:
        path(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        defaultDictionary = """### cgmAutoNameStuff
cgmModifier:cgmModifier



cgmName:cgmName
cgmType:cgmType
cgmNameModifier:cgmNameModifier
cgmTypeModifier:cgmTypeModifier
cgmDirectionModifier:cgmDirectionModifier
cgmDirection:cgmDirection
cgmModuleType:cgmModuleType
cgmIterator:cgmIterator
cgmPosition:cgmPosition

nameOrder:cgmPosition,cgmDirectionModifier,cgmDirection,cgmNameModifier,cgmName,cgmIterator,cgmTypeModifier,cgmType
nameDivider:_

defaultTextFont:Arial


### Color settings. Side:primary,secondary
### yellowBright,olive
colorLeft:blueBright,blueSky
colorRight:redBright,redDark
colorCenter:greenBright,greenBlue
colorMaster:yellowBright,olive

### Part Settings
moduleTypes:master,spine,spineRicgmon,arm,leg,segment,head,quadLeg

### Part Names
foot_NameList:heel,ball,toe
head_NameList:neck,head,headTop
torso_NameList:pelvis,spine,sternum,shoulders
arm_NameList:shoulder,elbow,wrist,uprArm,lwrArm
leg_NameList:hip,knee,ankle,uprLeg,lwrLeg
clavicle_NameList:clavicle,clavicleEnd


### References Part Names
head_TemplateParts:0,1,2
arm_TemplateParts:0,1,2
leg_TemplateParts:0,1,2
torso_TemplateParts:0,1,2,3
clavicle_TemplateParts:0,1,2,3


### Positional Data normalized to 1.0
finger_PositionalData:0,0,.2|0,0,.5|0,0,.7|0,0,.85|0,0,1
foot_PositionalData:0,0,-.25|0,0,.55|0,0,1
torso_PositionalData:0,0,.05|0,0,.6|0,0,.95
head_PositionalData:0,0,.1|0,0,.35|0,0,1
arm_PositionalData:0,0,0|0,0,.45|0,0,1
leg_PositionalData:0,0,0|0,0,.5|0,0,1
clavicle_PositionalData:.35,0,-.15|0,0,0

### Joint Settings
jointOrientation:zyx
#>>>orientationOptions = ['xyz','yzx','zxy','xzy','yxz','zyx','none']
#>>>For this to work, you always use a setup of first axis is aim, second is up, third is out

verticalJointUpDirection:zdown
horizontalJointUpDirection:yup
#>>>secondaryAxisOptions = ['xup','xdown','yup','ydown','zup','zdown','none']


### Process OrderSettings
moduleProcessOrder:spine,limb,limbEnd,other
spineModules:spine,spineRicgmon,torso
limbModules:arm,leg,head,arm2
limbEndModules:hand,foot,clavicle


### Rig process steps
module_ProcessSteps:initialized,templated,skeletonized,rigged


"""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cgmSettings.conf')
        if not os.path.exists(path):
                f = open(path, 'w')
                f.write(defaultDictionary)
                f.close()
        else:
                print "File already exists. Will not overwrite!"
                return False

        return path



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnShortName(key,dictionary):
        """ 
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        DESCRIPTION:
        Returns a short name for an input long one

        ARGUMENTS:
        key(string) - the key in the dictionary you're looking for
        dictionary(dict) - dictionary you wanna search

        RETURNS:
        Success - shortName(string)
        Failure - False
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        if key in dictionary:
                return (dictionary.get(key))        
        else:
                print ('%s%s%s' %('No match for >>',key,'<<, add it to the dictionary or check your spelling/case'))
                return False
