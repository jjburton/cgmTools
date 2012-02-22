#=================================================================================================================================================
#=================================================================================================================================================
#	settings - a part of rigger
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Functions to get the locations of the rigger conf files, and create default ones
# 
# REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
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

        REQUIRES:
        Nothing

        RETURNS:
        path(string)
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        """
        defaultDictionary = """### cgmAutoNameStuff
cgmName:cgmName
cgmType:cgmType
cgmNameModifier:cgmNameModifier
cgmDirection:cgmDirection
cgmModuleType:cgmModuleType
cgmIterator:cgmIterator

nameOrder:cgmNameModifier,cgmDirection,cgmName,cgmIterator,cgmType
nameDivider:_

### Part Settings
moduleTypes:master,spine,spineRicgmon,arm,leg,segment,head,quadLeg

### Part Names
head_NameList:neck,head,headTop
torso_NameList:pelvis,spine,sternum,shoulders
arm_NameList:clavicle,shoulder,elbow,wrist,uprArm,lwrArm
leg_NameList:hip,knee,ankle,uprLeg,lwrLeg
quadLeg_NameList:





head_TemplateParts:neck,head,headTop
arm_TemplateParts:shoulder,elbow,wrist
arm2_TemplateParts:clavicle,shoulder,elbow,wrist
leg_TemplateParts:hip,knee,ankle
torso_TemplateParts:pelvis,spine,sternum,shoulders
quadLeg_TemplateParts:hip,knee,ankle,ball

### Positional Data normalized to 1.0
head_PositionalData:0,.76,0|0,.85,0|0,1,0
arm_PositionalData:.125,0,0|.45,0,0|.75,0,0
arm2_PositionalData:.06,0,0|.125,0,0|.45,0,0|.75,0,0
leg_PositionalData:0,.5,0|0,.25,0|0,.05,0
torso_PositionalData:0,.5,0|0,.575,0|0,.64,0|0,.75,0

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
limbEndModules:hand,foot

### Skeletonize settings
weighted:spine,head
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

        REQUIRES:
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
