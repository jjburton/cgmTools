#=================================================================================================================================================
#=================================================================================================================================================
#	skinning - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for skinning
#
# ARGUMENTS:
# 	Maya
#   distance
#   rigging
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
# FUNCTION KEY:
#   1) locMe - creates locators at the pivots of every object selected - matching translation, rotation and rotation order
#
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.lib import distance
from cgm.lib import rigging
from cgm.lib import cgmMath
from cgm.lib import guiFactory

from zooPyMaya import apiExtensions
from maya.OpenMayaAnim import MFnSkinCluster
from maya.OpenMaya import MIntArray, MDagPathArray


reload (distance)


# Maya version check
mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Surfaces
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def controlSurfaceSmoothWeights(surface):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Early version of a weight smoother for a

    ARGUMENTS:
    surface(string)

    RETURNS:
    Nada
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    cvList = (mc.ls ([surface+'.cv[*][*]'],flatten=True))
    print cvList
    skinCluster = querySkinCluster (surface)
    influenceObjects = queryInfluences (skinCluster)
    print influenceObjects
    #find the closest influence object to the start
    startObject =  (distance.returnClosestObjToCV (cvList[0], influenceObjects))
    print startObject
    #find the closest influence object to the end
    endObject = (distance.returnClosestObjToCV (cvList[-1], influenceObjects))
    print endObject
    #getting the last cv list number
    cvChainLength =  ((len(cvList)-1)/2)
    #set the skin weights for the top and bottom
    mc.skinPercent (skinCluster,(surface+'.cv[0:1][0:1]'), tv = [startObject,1])
    mc.skinPercent (skinCluster,('%s%s%i%s%i%s' % (surface,'.cv[0:1][',(cvChainLength-1),':',cvChainLength,']')), tv = [endObject,1])
    #Blend in the nearest row to the start and end
    mc.skinPercent (skinCluster,(surface+'.cv[0:1][2]'), tv = [startObject,.4])
    mc.skinPercent (skinCluster,('%s%s%i%s' % (surface,'.cv[0:1][',(cvChainLength-1),']')), tv = [endObject,.4])

def simpleControlSurfaceSmoothWeights(surface,maxBlend = 3):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Early version of a weight smoother for a

    ARGUMENTS:
    surface(string)

    RETURNS:
    Nada
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    cvList = (mc.ls ([surface+'.cv[*][*]'],flatten=True))
    skinCluster = querySkinCluster (surface)
    influenceObjects = queryInfluences (skinCluster)

    #find the closest influence object to the start
    startObject =  (distance.returnClosestObjToCV (cvList[0], influenceObjects))
    #find the closest influence object to the end
    endObject = (distance.returnClosestObjToCV (cvList[-1], influenceObjects))
    #getting the last cv list number
    cvChainLength =  ((len(cvList)-1)/2)

    #Smooth interior weights
    """ get our interior CVs """
    interiorCvList = []
    cnt = 1
    for i in range(cvChainLength):
        interiorCvList.append('%s%s%i%s' % (surface,'.cv[0][',cnt,']'))
        interiorCvList.append('%s%s%i%s' % (surface,'.cv[1][',cnt,']'))
        cnt += 1

    """ overall blend """
    for cv in interiorCvList:
        closestObject = (distance.returnClosestObjToCV (cv, influenceObjects))
        closestObjectsDict = distance.returnClosestObjectsFromAim(closestObject,influenceObjects)
        upObjects = closestObjectsDict.get('up')
        downObjects = closestObjectsDict.get('dn')
        objectsToCheck = []
        if upObjects != None:
            objectsToCheck += upObjects
        if downObjects != None:
            objectsToCheck += downObjects
        blendInfluences =[]
        blendInfluences.append(closestObject)
        distances = []
        cnt = 1
        print objectsToCheck
        while cnt < maxBlend and cnt < len(objectsToCheck):
            closestSubObj = distance.returnClosestObject(closestObject, objectsToCheck)
            blendInfluences.append(closestSubObj)
            objectsToCheck.remove(closestSubObj)
            cnt+=1

        """ get our distances to normalize """
        locBuffer = locators.locMeSurfaceCV(cv)
        for obj in blendInfluences:
            distances.append(distance.returnDistanceBetweenObjects(locBuffer,obj))
        normalizedDistances = cgmMath.normList(distances, normalizeTo=1)
        cnt = 0
        for obj in blendInfluences:
            mc.skinPercent (skinCluster,cv, tv = [obj,normalizedDistances[cnt]])
            cnt +=1
        mc.delete(locBuffer)

    """ Set closest cv's to respective infuences to max """
    cvList1 = []
    cvList2 = []
    for i in range(cvChainLength):
        cvList1.append('%s%s%i%s' % (surface,'.cv[0][',cnt,']'))
        cvList2.append('%s%s%i%s' % (surface,'.cv[1][',cnt,']'))
        cnt += 1
    for obj in influenceObjects:
        closestCV1 = distance.returnClosestCVFromList(obj, cvList1)
        mc.skinPercent (skinCluster,closestCV1, tv = [obj,1])
        closestCV2 = distance.returnClosestCVFromList(obj, cvList2)
        mc.skinPercent (skinCluster,closestCV2, tv = [obj,1])

    #set the skin weights for the top and bottom
    mc.skinPercent (skinCluster,(surface+'.cv[0:1][0:1]'), tv = [startObject,1])
    mc.skinPercent (skinCluster,('%s%s%i%s%i%s' % (surface,'.cv[0:1][',(cvChainLength-1),':',cvChainLength,']')), tv = [endObject,1])
    #Blend in the nearest row to the start and end
    mc.skinPercent (skinCluster,(surface+'.cv[0:1][2]'), tv = [startObject,1])
    mc.skinPercent (skinCluster,('%s%s%i%s' % (surface,'.cv[0:1][',(cvChainLength-2),']')), tv = [endObject,1])

    mc.skinPercent (skinCluster,(surface+'.cv[0:1][3]'), tv = [startObject,.7])
    mc.skinPercent (skinCluster,('%s%s%i%s' % (surface,'.cv[0:1][',(cvChainLength-3),']')), tv = [endObject,.7])



def nurbsCVSmoothWeights(cv):
    surface = '.'.join(cv.split('.')[0:-1])
    skinCluster = querySkinCluster (surface)
    cvPos = mc.pointPosition (cv,world=True)
    wantedName = (cv + 'loc')
    actualName = mc.spaceLocator (n= wantedName)
    mc.move (cvPos[0],cvPos[1],cvPos[2], [actualName[0]])
    influenceObjects = queryInfluences (skinCluster)
    culledList = influenceObjects
    """figure out our closest objects"""
    bestChoices = []
    cnt = 5
    while cnt >= 0:
        goodChoice =  (distance.returnClosestObjToCV (cv, culledList))
        culledList.remove(goodChoice)
        bestChoices.append (goodChoice)
        print bestChoices
        cnt-=1
    distanceList = []
    for obj in bestChoices:
        distanceList.append (distance.returnDistanceBetweenObjects(actualName[0],obj))
        print distanceList
    """ return normalization value """
    buffer=0
    y = 1 + (x-A)*(10-1)/(B-A)
    for value in distanceList:
        buffer += value
    print buffer
    normalize = ((len(distanceList))*.1)
    print normalize
    mc.delete (actualName[0])

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utility Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def skinMeshFromMesh(sourceMesh,targetMesh):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes a skinned mesh, gets it's influences, creates a new skinCluster for the target mesh, then copies the weights over

    ARGUMENTS:
    sourceMesh(string)
    targetMesh(string)

    RETURNS:
    newSkinCluster(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    oldSkinCluster = querySkinCluster(sourceMesh)
    influenceJoints = queryInfluences(oldSkinCluster)

    """ Skin, copy weights """
    skinSet = influenceJoints
    skinSet.append(targetMesh)
    newSkinCluster = mc.skinCluster(skinSet,tsb=True,n=(targetMesh+'_skinCluster'))
    copyWeightsByClosestVertice(sourceMesh,targetMesh)


    return newSkinCluster


def cleanMeshReskin(objWithSkinCluster,name):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes a skinned mesh, duplicates it to get rid of history, reskins and copies the weights from the old mesh

    ARGUMENTS:
    objWithSkinCluster(string)
    name(string)

    RETURNS:
    newMesh(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    oldSkinCluster = querySkinCluster(objWithSkinCluster)
    influenceJoints = queryInfluences(oldSkinCluster)

    """ duplicate, skin, copy weights """
    newMesh = mc.duplicate(objWithSkinCluster)
    skinSet = influenceJoints + newMesh
    newSkinCluster = mc.skinCluster(skinSet,tsb=True,n=(name+'_skinCluster'))
    #mc.copySkinWeights(ds=newSkinCluster[0],ss=oldSkinCluster,noMirror=True)
    copyWeights(objWithSkinCluster,newMesh)

    """ name it """
    newMesh = mc.rename(newMesh,(name+'_geo'))

    return newMesh

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Copying weights
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def copySkinWeightBetweenVertices(sourceVertice,targetVertice):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ACKNOWLEDGEMENT:
    Modified from TD Matt - http://td-matt.blogspot.com/2011/05/copying-skin-weight-values-between.html

    DESCRIPTION:


    ARGUMENTS:
    skinCluster(string)
    vertJointWeightData(list)

    RETURNS:
    None
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    targetMeshBuffer = targetVertice.split('.')
    sourceMeshBuffer = sourceVertice.split('.')

    targetSkinCluster = querySkinCluster(targetMeshBuffer[0])
    sourceSkinCluster = querySkinCluster(sourceMeshBuffer[0])

    sourceInfluences = queryInfluences(sourceSkinCluster)

    skinValues = []
    for influence in sourceInfluences:
        influenceValue = mc.skinPercent(sourceSkinCluster, sourceVertice, transform = influence, query = True)
        #influenceValue = mc.skinPercent(sourceSkinCluster, sourceVertice, value = True, query = True)
        if influenceValue != 0:
            skinValues.append([influence,influenceValue])

    print skinValues
    for tvSet in skinValues:
        ''' set the weight and lock it after to avoid normalization errors '''
        mc.skinPercent(targetSkinCluster, targetVertice, tv= tvSet)
        #mc.setAttr((tvSet[0]+'.liw'),1)

    for tvSet in skinValues:
        ''' unlock it '''
        mc.setAttr((tvSet[0]+'.liw'),0)
    #mc.skinPercent(targetSkinCluster, v, transform = influence, value = influenceValue)

    pass


def setSkinWeights( skinCluster, vertJointWeightData ):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ACKNOWLEDGEMENT:
    From Hammish - http://www.macaronikazoo.com/?p=417

    DESCRIPTION:


    ARGUMENTS:
    skinCluster(string)
    vertJointWeightData(list)
        vertJointWeightData is a list of 2-tuples containing the vertex component name, and a list of 2-tuples
    containing the joint name and weight.  ie it looks like this:
    [ ('someMesh.vtx[0]', [('joint1', 0.25), 'joint2', 0.75)]),
    ('someMesh.vtx[1]', [('joint1', 0.2), 'joint2', 0.7, 'joint3', 0.1)]),
    ... ]

    RETURNS:
    None
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """

    #convert the vertex component names into vertex indices
    idxJointWeight = []
    for vert, jointsAndWeights in vertJointWeightData:
        idx = int( vert[ vert.rindex( '[' )+1:-1 ] )
        idxJointWeight.append( (idx, jointsAndWeights) )

    #get an MObject for the skin cluster node
    skinCluster = apiExtensions.asMObject( skinCluster )
    skinFn = MFnSkinCluster( skinCluster )

    #construct a dict mapping joint names to joint indices
    jApiIndices = {}
    _tmp = MDagPathArray()
    skinFn.influenceObjects( _tmp )
    for n in range( _tmp.length() ):
        jApiIndices[ str( _tmp[n].node() ) ] = skinFn.indexForInfluenceObject( _tmp[n] )

    weightListP = skinFn.findPlug( "weightList" )
    weightListObj = weightListP.attribute()
    weightsP = skinFn.findPlug( "weights" )

    tmpIntArray = MIntArray()
    baseFmtStr = str( skinCluster ) +'.weightList[%d]'  #pre build this string: fewer string ops == faster-ness!

    for vertIdx, jointsAndWeights in idxJointWeight:

        #we need to use the api to query the physical indices used
        weightsP.selectAncestorLogicalIndex( vertIdx, weightListObj )
        weightsP.getExistingArrayAttributeIndices( tmpIntArray )

        weightFmtStr = baseFmtStr % vertIdx +'.weights[%d]'

        #clear out any existing skin data - and awesomely we cannot do this with the api - so we need to use a weird ass mel command
        for n in range( tmpIntArray.length() ):
            mc.removeMultiInstance( weightFmtStr % tmpIntArray[n] )


        #at this point using the api or mel to set the data is a moot point...  we have the strings already so just use mel
        for joint, weight in jointsAndWeights:
            if weight:
                infIdx = jApiIndices[ joint ]
                mc.setAttr( weightFmtStr % infIdx, weight )


def copyWeightsByClosestVertice(sourceMesh, targetMesh):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tool to copy weights from one mesh to another by checking for the closest vertice to each vertice

    ARGUMENTS:
    sourceMesh(string)
    targetMesh(string)

    RETURNS:
    None
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(sourceMesh) is True,"'%s' doesn't exist" %sourceMesh
    assert mc.objExists(targetMesh) is True,"'%s' doesn't exist" %targetMesh

    targetSkinCluster = querySkinCluster(targetMesh)

    influenceData = returnVerticeJointWeightDataToDict(sourceMesh)

    targetVertexList = (mc.ls ([targetMesh+'.vtx[*]'],flatten=True))
    sourceVertexList = (mc.ls ([sourceMesh+'.vtx[*]'],flatten=True))

    rebuiltVertWeightData = []

    for v in targetVertexList:
        verticeBuffer = [v]

        """ find the closest vert """
        closestVert = distance.returnClosestObject(v,sourceVertexList)
        print ("Copying " + closestVert + " >>>> " + v)
        """ rebuild our vert weighting data to set"""
        verticeBuffer.append(influenceData.get(closestVert))
        rebuiltVertWeightData.append(verticeBuffer)


    setSkinWeights(targetSkinCluster,rebuiltVertWeightData)
    return rebuiltVertWeightData

def copyWeightsByClosestVerticeFromVert(sourceMesh, targetVert):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    New
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(sourceMesh) is True,"'%s' doesn't exist" %sourceMesh
    assert mc.objExists(targetVert) is True,"'%s' doesn't exist" %targetVert
    
    targetMeshBuffer = targetVert.split('.')
    print targetMeshBuffer
    targetSkinCluster = querySkinCluster(targetMeshBuffer[0])
    print  targetSkinCluster
    influenceData = returnVerticeJointWeightDataToDict(sourceMesh)
    print influenceData
    sourceVertexList = (mc.ls ([sourceMesh+'.vtx[*]'],flatten=True))
    print sourceVertexList
    rebuiltVertWeightData = []


    """ find the closest vert """
    verticeBuffer = [targetVert]
    closestVert = distance.returnClosestObject(targetVert,sourceVertexList)
    print ("Copying " + closestVert + " >>>> " + targetVert)
    """ rebuild our vert weighting data to set"""
    verticeBuffer.append(influenceData.get(closestVert))
    rebuiltVertWeightData.append(verticeBuffer)

    setSkinWeights(targetSkinCluster,rebuiltVertWeightData)
    return rebuiltVertWeightData

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Get Influences
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def queryInfluences(skinCluster):
    return mc.skinCluster (skinCluster, q=True,weightedInfluence=True)

def queryInfluences2(skinCluster):
    return mc.listConnections(skinCluster+'.matrix')

def returnExcessInfluenceVerts(mesh, maxInfluences):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for finding vertices that are over X influences

    ARGUMENTS:
    mesh(string)
    maxInfluences(int)

    RETURNS:
    badVertices(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    skinCluster = querySkinCluster(mesh)
    vertices = (mc.ls ([mesh+'.vtx[*]'],flatten=True))

    badVertices = []

    if mayaVersion >= 2011:
        #Find the bad verts
        for v in range(len(vertices)):
            currentVert = ('%s%s%s%s' % (mesh,'.vtx[',v,']'))
            influenceList = mc.skinPercent(skinCluster, currentVert, query=True, transform=None)
            if len(influenceList) > maxInfluences:
                badVertices.append(currentVert)
        return badVertices
    else:
        guiFactory.warning('Old Maya Version Mode')
        #Find the bad verts
        for v in vertexList:
            rawInfluenceList = mc.skinPercent(skinCluster, v, query=True, transform=None)
            valuesList = mc.skinPercent(skinCluster, v, query=True, value=True)
            cnt = 0
            influenceList = []
            for obj in rawInfluenceList:
                if valuesList[cnt] > 0:
                    influenceList.append(obj)
                cnt+=1
            if len(influenceList) > maxInfluences:
                badVertices.append(v)
        return badVertices



def returnVerticeJointWeightDataToList(sourceMesh):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for getting vertice influce weight data

    ARGUMENTS:
    sourceMesh(string)

    RETURNS:
    returnList(list) - [[u'Dingo.vtx[0]', [[u'head_squash1', 0.31655514240264893], [u'skin_head_root1', 0.68344485759735107]]],...]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    sourceSkinCluster = querySkinCluster(sourceMesh)
    sourceVertexList = (mc.ls ([sourceMesh+'.vtx[*]'],flatten=True))
    influenceList = queryInfluences(sourceSkinCluster)
    returnList = []

    for vertice in sourceVertexList:
        verticeBuffer = [vertice]
        skinValues = []
        for influence in influenceList:
            influenceValue = mc.skinPercent(sourceSkinCluster, vertice, transform = influence, query = True)
            if influenceValue != 0:
                skinValues.append([influence,influenceValue])
        verticeBuffer.append(skinValues)
        returnList.append(verticeBuffer)

    return returnList

def returnVerticeJointWeightDataToDict(sourceMesh):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for getting vertice influce weight data

    ARGUMENTS:
    sourceMesh(string)

    RETURNS:
    returnList(dict) - {[u'Oswald_Head.vtx[0]', [[u'head_squash1', 0.31655514240264893], [u'skin_head_root1', 0.68344485759735107]]],...}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    sourceSkinCluster = querySkinCluster(sourceMesh)
    print sourceSkinCluster
    sourceVertexList = (mc.ls ([sourceMesh+'.vtx[*]'],flatten=True))
    print sourceVertexList
    influenceList = queryInfluences(sourceSkinCluster)
    print influenceList
    returnDict= {}

    for vertice in sourceVertexList:
        skinValues = []
        for influence in influenceList:
            influenceValue = mc.skinPercent(sourceSkinCluster, vertice, transform = influence, query = True)
            if influenceValue != 0:
                skinValues.append([influence,influenceValue])
        returnDict[vertice] = skinValues

    return returnDict

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Skin Cluster Info
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def querySkinCluster(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Query an meesh objects skin cluster if it has one

    ARGUMENTS:
    obj(string)

    RETURNS:
    skinCluster(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mel.eval ('$mesh = "%s";' % (obj))
    skin = mel.eval('findRelatedSkinCluster($mesh);')
    return skin



def querySkinCluster(obj):
    mel.eval ('$mesh = "%s";' % (obj))
    skin = mel.eval('findRelatedSkinCluster($mesh);')
    return skin