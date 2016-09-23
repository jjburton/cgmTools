#=================================================================================================================================================
#=================================================================================================================================================
#       deformers - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#       Series of tools for the widgety magic of deformers
#
# ARGUMENTS:
#       Maya
#   distance
#
# AUTHOR:
#       Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#       http://www.cgmonks.com
#       Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#       0.1 - 02/09/2011 - added documenation
#
#=================================================================================================================================================
import maya.cmds as mc
import maya.mel as mel
import copy

from maya.OpenMayaAnim import MFnBlendShapeDeformer
from cgm.core.lib.zoo import apiExtensions
from cgm.core.lib import geo_Utils as GEOUTILS
from cgm.core.cgmPy import validateArgs as cgmVALID
from cgm.lib import(distance,
                    names,
                    dictionary,
                    guiFactory,
                    settings,
                    search,
                    attributes,
                    skinning,
                    lists,
                    nodes,
                    rigging)
reload(names)
from cgm.lib.classes import NameFactory

typesDictionary = dictionary.initializeDictionary(settings.getTypesDictionaryFile())
settingsDictionary = dictionary.initializeDictionary( settings.getSettingsDictionaryFile())
settingsDictionaryFile = settings.getSettingsDictionaryFile()

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

def polyUniteGeo(objList,name='unitedGeo'):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Unites polys with the poly unite command. Every piece of geo must have
    a deformer node with an .outputGeometry

    ARGUMENTS:
    objList(string)
    name(string) - base name for the geo and node created

    RETURNS:
    returnList = [unifedGeoName,polyUniteNode]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    geoOutNodes = []

    """ get all of the outMesh possibilities"""
    for obj in objList:
        outGeoNode = False
        deformers = returnObjectDeformers(obj)
        if deformers:
            for i in range(len(deformers)):
                if mc.objExists(deformers[i]+'.outputGeometry') == True:
                    #Check for FFD
                    if search.returnObjectType(deformers[i]) == 'ffd':
                        geoShapes = mc.listRelatives(obj,shapes=True,fullPath=True)
                        for shape in geoShapes:
                            if 'Deformed' in shape and mc.objExists(shape+'.outMesh') == True:
                                outGeoNode = (shape+'.outMesh')
                                geoOutNodes.append(shape)                        
                    else:
                        outGeoNode = (deformers[i]+'.outputGeometry')
                        geoOutNodes.append(outGeoNode)
                if outGeoNode != False:
                    break
        else:
            geoShapes = mc.listRelatives(obj,shapes=True,fullPath=True)
            if mc.objExists(geoShapes[0]+'.outMesh') == True:
                outGeoNode = (geoShapes[0]+'.outMesh')
                geoOutNodes.append(geoShapes[0])

    if len(geoOutNodes) != len(objList):
        print "Don't have connections for all geo pieces"
        return False

    """ check for a dup list"""
    #geoOutNodes = lists.returnListNoDuplicates(geoOutNodes)
    

    """ make the node """
    uniteNode = mc.createNode('polyUnite')
    uniteNode = mc.rename(uniteNode,(name+'_polyUniteNode'))

    
    """ connect our stuff """
    nodeTracker = []
    for obj in objList:
        print "On '%s'"%obj
        try:
            index = objList.index(obj)
            print geoOutNodes[index]
            if search.returnObjectType( (geoOutNodes[index]) ) is 'shape':
                mc.connectAttr(('%s%s'% (geoOutNodes[index],'.outMesh')),('%s%s%i%s'% (uniteNode,'.inputPoly[',index,']')),f=True)
                mc.connectAttr(('%s%s'% (obj,'.worldMatrix[0]')),('%s%s%i%s'% (uniteNode,'.inputMat[',index,']')),f=True)
            else:
                # Check if we've already used this connection, if so we need to iterate
                if geoOutNodes[index] in nodeTracker:
                    mc.connectAttr(('%s%s%i%s'% (geoOutNodes[index],'[', (nodeTracker.count(geoOutNodes[index]) ) ,']')),('%s%s%i%s'% (uniteNode,'.inputPoly[',index,']')),f=True)
                else:
                    mc.connectAttr(('%s%s'% (geoOutNodes[index],'[0]')),('%s%s%i%s'% (uniteNode,'.inputPoly[',index,']')),f=True)
                mc.connectAttr(('%s%s'% (obj,'.worldMatrix[0]')),('%s%s%i%s'% (uniteNode,'.inputMat[',index,']')),f=True)
                nodeTracker.append(geoOutNodes[index])
            
        except:
            guiFactory.warning("'%s' failed to add. Verify that the object is polyGeo"%obj)
        
    """ Create our outPut mesh"""
    unitedGeoShape = mc.createNode('mesh')
    unitedGeo = mc.listRelatives(unitedGeoShape,parent=True,type='transform')

    # and the group parts node
    groupPartsNode = mc.createNode('groupParts')
    groupPartsNode = mc.rename(groupPartsNode,(name+'_groupParts'))

    """ Connect it up """
    mc.connectAttr((uniteNode+'.output'),(groupPartsNode+'.inputGeometry'))
    mc.connectAttr((groupPartsNode+'.outputGeometry'),(unitedGeoShape+'.inMesh'))

    """Store and return"""
    attributes.storeInfo(unitedGeo[0],'cgmName',name)
    attributes.storeInfo(unitedGeo[0],'cgmType','polyUniteGeo')
    unitedGeo = mc.rename(unitedGeo[0],(name+'_UniteGeo'))

    attributes.storeInfo(uniteNode,'cgmSourceObjects',(';'.join(objList)))
    attributes.storeInfo(uniteNode,'cgmResultGeo',(unitedGeo))

    return [unitedGeo,uniteNode,groupPartsNode]




def returnBaseObjectsFromDeformer(deformer):
    #I know there's a better way to do this but I don't have time to figure it out right now
    #input inputPoly
    returnList = []
    transforms = mc.ls(type='transform')

    for obj in transforms:
        deformerList = returnObjectDeformers(obj)
        if deformerList:
            if deformer in deformerList:
                returnList.append(obj)

    if returnList:
        return returnList
    else:
        return False

    """
    keepGoing = 1
    while keepGoing:
        if
        shapes = mc.listRelatives(geo,shapes=True)
        bufferObject =  attributes.returnDriverObject('%s%s' % (shapes[0],'.inMesh'))
        return attributes.returnDriverObject('%s%s' % (bufferObject,'.inputGeometry'))
    """

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Poly Unite
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnPolyUniteSourceShapes(polyUniteNode):
    i = 0
    rawDrivers = []
    if mc.objExists(polyUniteNode):
        while mc.connectionInfo (('%s%s%i%s' % (polyUniteNode,'.inputPoly[',i,']')),isDestination=True) == True:
            rawDrivers.append(attributes.returnDriverObject('%s%s%i%s' % (polyUniteNode,'.inputPoly[',i,']')))
            i+=1
        return rawDrivers
    else:
        return False

def returnPolyUniteResultGeoShape(polyUniteNode):
    bufferObject = attributes.returnDrivenObject('%s%s' % (polyUniteNode,'.output'))
    return attributes.returnDrivenObject('%s%s' % (bufferObject,'.outputGeometry'))

def returnPolyUniteNodeFromResultGeo(geo):
    shapes = mc.listRelatives(geo,shapes=True)
    if shapes:
        if mc.objExists('%s%s' % (shapes[0],'.inMesh')):
            bufferObject =  attributes.returnDriverObject('%s%s' % (shapes[0],'.inMesh'))
            if mc.objExists('%s%s' % (bufferObject,'.inputGeometry')):
                return attributes.returnDriverObject('%s%s' % (bufferObject,'.inputGeometry'))
            else:
                return False
        else:
            return False
    else:
        return False

def removePolyUniteNode(polyUniteNode):
    rawDrivers = returnPolyUniteSourceShapes(polyUniteNode)

    if not mc.objExists(polyUniteNode):
        return guiFactory.warning('%s does not exist' %polyUniteNode)
    mc.delete(polyUniteNode)
    
    for obj in rawDrivers:
        if search.returnObjectType(obj) is 'shape':
            transform = mc.listRelatives (obj,parent=True, type ='transform')
            nameBuffer = mc.listRelatives (obj,parent=True, type ='transform')
            mc.setAttr((transform[0]+'.visibility'),1)
            mc.setAttr((obj+'.intermediateObject'),0)
            
            
            if not mc.referenceQuery(obj, isNodeReferenced=True):
                buffer = rigging.doParentToWorld(transform[0])
                mc.rename(buffer,nameBuffer[0])





#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# General Deformer Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def isSkinned(obj = None):
    try:_str_funcName = "{0}.isSkinned()".format(obj)
    except:_str_funcName = "isSkinned()"
    try:
	if returnObjectDeformers(obj,'skinCluster'):
	    return True
	return False
    except StandardError,error:
	log.error("obj: {0}".format(obj))
	raise StandardError, "{0} fail | error: {1}"(_str_funcName,error)    


def returnObjectDeformers(obj, deformerTypes = 'all'):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ACKNOWLEDGEMENT
    Pythonized from - http://www.scriptswell.net/2010/09/mel-list-all-deformers-on-mesh.html

    DESCRIPTION:
    Returns a list of deformers on an object in order from top to bottom

    ARGUMENTS:
    obj(string)

    RETURNS:
    deformers(list)/False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objHistory = mc.listHistory(obj,pruneDagObjects=True)
    deformers = []
    if objHistory:
        for node in objHistory:
            typeBuffer = mc.nodeType(node, inherited=True)
            if 'geometryFilter' in typeBuffer:
                deformers.append(node)
    if len(deformers)>0:
        if deformerTypes == 'all':
            return deformers
        else:
            foundDeformers = []
            #Do a loop to figure out if the types are there
            for deformer in deformers:
                if search.returnObjectType(deformer) == deformerTypes:
                    foundDeformers.append(deformer)
            if len(foundDeformers)>0:
                return foundDeformers
            else:
                return []

    else:
        return []

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def reorderDeformersByType(obj, deformerOrder = ['skinCluster','blendShape','tweak']):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    ACKNOWLEDGEMENT
    Reorders deformers on an object by deformer type

    DESCRIPTION:
    Returns a list of deformers on an object in order from top to bottom

    ARGUMENTS:
    obj(string)
    deformerOrder(list) - (['skinCluster','blendShape','tweak'])
    >>>> Options are sculpt, cluster, jointCluster, lattice, wire, jointLattice, boneLattice, blendShape.

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    deformers = returnObjectDeformers(obj)
    orderedDeformers = []
    if deformers:
        for deformerType in deformerOrder:
            for deformer in deformers:
                if search.returnObjectType(deformer) == deformerType:
                    orderedDeformers.append(deformer)
                    deformers.remove(deformer)

        for deformer in deformers:
            orderedDeformers.append(deformer)
        # pair up the list
        orderedDeformerPairs = lists.parseListToPairs(orderedDeformers)
        for pair in orderedDeformerPairs:
            mc.reorderDeformers(pair[0],pair[1],obj)
        return True
    else:
        print ('No deformers on ' + obj)
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def reorderDeformersByOrderedList(obj, deformerOrder):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Reorders deformers on an object by a list of deformers

    ARGUMENTS:
    obj(string)
    deformerOrder(list) - list of the order youw ant

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    deformers = returnObjectDeformers(obj)
    orderedDeformers = []
    existsCheck = True
    if deformers:
        # pair up the list
        orderedDeformerPairs = lists.parseListToPairs(deformerOrder)
        for pair in orderedDeformerPairs:
            mc.reorderDeformers(pair[0],pair[1],obj)
        return True
    else:
        print ('No deformers on ' + obj)
        return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Pose Buffer stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def blendShapeNodeToPoseBuffer(name,blendShapeNode,doConnect = True, transferConnections = True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes the attributes of a blendshape, adds them as attributes, connects them and transfers
    any driver should you choose

    ARGUMENTS:
    name(string)
    blendShapeNode(string)
    doConnect(bool) - (True) - if you want to connect the atributes to the new ones
    transferConnections(bool) - (True) - if you wanna transfer exisiting connections or not


    RETURNS:
    returnList(list) - [poseBuffer(string),newAttrs(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ first get the blendshape attrs """
    blendShapeAttrs = search.returnBlendShapeAttributes(blendShapeNode)

    returnList =  nodes.createPoseBuffer(name,blendShapeAttrs)

    newAttrs = returnList[1]

    if doConnect == True:
        for attr in blendShapeAttrs:
            listIndex = blendShapeAttrs.index(attr)
            attributes.doConnectAttr((newAttrs[listIndex]),(blendShapeNode+'.'+attr),False,transferConnections)


    return returnList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def updateBlendShapeNodeToPoseBuffer(poseBuffer,blendShapeNode,doConnect = True, transferConnections = True, removeMissingShapes = True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Updates a blendshape to posebuffer connection with new attrs (need to
    make it remove non existing ones, maybe make the creation one tag it's parent blendshape node)

    ARGUMENTS:
    poseBuffer(string)
    blendShapeNode(string)
    doConnect(bool) - (True) - if you want to connect the atributes to the new ones
    transferConnections(bool) - (True) - if you wanna transfer exisiting connections or not


    RETURNS:
    returnList(list) - [poseBuffer(string),newAttrs(list)]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ first get the blendshape attrs """
    blendShapeAttrs = search.returnBlendShapeAttributes(blendShapeNode)
    initialPoseBufferAttrs = attributes.returnUserAttributes(poseBuffer)

    removeAttrsBuffer = lists.returnMissingList(blendShapeAttrs,initialPoseBufferAttrs)
    newAttrs = lists.returnMissingList(initialPoseBufferAttrs,blendShapeAttrs)

    newAttrs = attributes.addFloatAttrsToObj(poseBuffer, newAttrs,dv = 0)
    poseBufferAttrs = attributes.returnUserAttributes(poseBuffer)

    if doConnect:
        for attr in newAttrs:
            try:
                attributes.doConnectAttr((poseBuffer+'.'+attr),(blendShapeNode+'.'+attr),False,transferConnections)
            except:
                guiFactory.warning('%s%s%s%s' % ((poseBuffer+'.'+attr),' to ',(blendShapeNode+'.'+attr),' failed!' ))

    removeAttrs = []
    if removeMissingShapes:
        for attr in removeAttrsBuffer:
            if 'cgm' not in attr:
                removeAttrs.append((poseBuffer+'.'+attr))
                mc.deleteAttr((poseBuffer+'.'+attr))

    return [newAttrs,removeAttrs]

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def connectBlendShapeNodeToPoseBuffer(blendShapeNode,poseBuffer):
    blendShapeChannels = search.returnBlendShapeAttributes(blendShapeNode)
    poseBufferAttributes = attributes.returnUserAttributes(poseBuffer)

    for blendShapeChannel in blendShapeChannels:
        if blendShapeChannel in poseBufferAttributes:
            attributes.doConnectAttr((poseBuffer+'.'+blendShapeChannel),(blendShapeNode+'.'+blendShapeChannel),False)

def returnBlendShapeNodeFromPoseBuffer(poseBuffer):
    poseBufferAttributes = attributes.returnUserAttributes(poseBuffer)
    drivenObjects = []
    if poseBufferAttributes:
        for attr in poseBufferAttributes:
            try:
                buffer = attributes.returnDrivenObject(poseBuffer+'.'+attr)
                if search.returnObjectType(buffer) == 'blendShape':
                    drivenObjects.append(buffer)
            except:
                pass
        drivenObjects = lists.returnListNoDuplicates(drivenObjects)
        return drivenObjects
    else:
        guiFactory.warning("No blendshape node connected to %s found" %poseBuffer)
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Wrap Deformers
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def influenceWrapObject(targetObject,sourceObject,duplicateObject = False, polySmoothness = 0):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function to influence wrap one object to another rather than 

    ARGUMENTS:
    targetObject(string)
    sourceObject(string)
    duplicateObject(bool) whether to duplicate the object or not
    polySmoothness(float) - amount of smoothness on the deformed object

    RETURNS:
    returnList(list) - [skinCluster,wrappedTargetObject,joint]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """

    #...make a dup to bake
    if duplicateObject == True:
        wrappedTargetObject = mc.duplicate(targetObject)
        wrappedTargetObject = rigging.doParentToWorld(wrappedTargetObject)
        wrappedTargetObject = mc.rename(wrappedTargetObject,(targetObject+'_baked'))

        mc.delete(wrappedTargetObject,ch=True)#...delete the history
    else:
        wrappedTargetObject = targetObject
	
    if isSkinned(targetObject):
	raise ValueError,"Target object is skinned! Can't contineue | {0}".format(targetObject)
	
    try:#Buffer render flags
	'''have to buffer these as when you wrap deform, they get screwy on the source object'''
	_l_sourceAttrs = ['castsShadows','receivesShadows','motionBlur','primaryVisibility','smoothShading',
	                  'smoothShading','visibleInReflections','visibleInRefractions','doubleSided']
	_d_sourceAttrs = {}
	_d_targetAttrs = {}
	_sourceShape = mc.listRelatives(sourceObject,shapes=True,fullPath=True)[0]
	_targetShape = mc.listRelatives(wrappedTargetObject,shapes=True,fullPath=True)[0]
	for a in _l_sourceAttrs:
	    _d_sourceAttrs[a] = attributes.doGetAttr(_sourceShape,a)
	    _d_targetAttrs[a] = attributes.doGetAttr(_targetShape,a)
    except Exception,err:
	raise Exception,"influenceWrapObject >> Render flag query | {0}".format(err)

    try:#...inluence wrap
	#create joint
	#Skincluster
	#add influence (use geometry) with influence
	mc.select(cl=1)
	_jnt = mc.joint(p = [0,0,0], n = "{0}_influenceWrap_{1}_jnt".format(names.getBaseName(targetObject),
	                                                                    names.getBaseName(sourceObject)))
	_cluster = mc.skinCluster([_jnt,wrappedTargetObject],
	                          tsb = True,
	                          normalizeWeights = True,
	                          mi = 4, dr = 5,
	                          n = "{0}_influenceWrap_skinCluster".format(names.getBaseName(targetObject)))[0]
	mc.skinCluster(_cluster, e = True,
	               addInfluence = sourceObject,
	               wt = 100.0, useGeometry = 1,
	               polySmoothness = polySmoothness)
	attributes.doSetAttr(_cluster,'useComponents',True)

    except Exception,err:
	raise Exception,"influenceWrapObject >> influence wrap apply | {0}".format(err)	
    
    try:#...restore shape attrs
	for a,v in _d_sourceAttrs.iteritems():
	    try:
		attributes.doSetAttr(_sourceShape,a,v)      
	    except Exception,error:
		log.error("failed to restore {0}-{1} | error: {2}".format(a,v,error))
	for a,v in _d_targetAttrs.iteritems():
	    try:
		attributes.doSetAttr(_targetShape,a,v)      
	    except Exception,error:
		log.error("failed to restore {0}-{1} | error: {2}".format(a,v,error))
    except Exception,err:
	raise Exception,"influenceWrapObject >> Render flag apply | {0}".format(err)		
    return [_cluster,wrappedTargetObject,_jnt]


def wrapDeformObject(targetObject, sourceObject, duplicateObject = False):
    """
    --- Updated - 04.21.2016
    
    Function for baking a series of blendshapes from one object to another

    :parameters:
	targetObject(str): Object to wrap
	sourceObject(str): Object to wrap to
	duplicateObject(bool):whether to duplicate object or not

    :returns
	returnList(list) - [wrapDeformer,wrappedTargetObject]
    """    

    #Make a dup to bake
    if duplicateObject == True:
        wrappedTargetObject = mc.duplicate(targetObject)
        wrappedTargetObject = rigging.doParentToWorld(wrappedTargetObject)
        wrappedTargetObject = mc.rename(wrappedTargetObject,(targetObject+'_baked'))

        """ Freeze """
        #mc.makeIdentity(wrappedTargetObject,apply=True, t=True,r=True,s=True)
        mc.delete(wrappedTargetObject,ch=True)
    else:
        wrappedTargetObject = targetObject
	
    #Buffer render flags
    '''have to buffer these as when you wrap deform, they get screwy on the source object'''
    _l_sourceAttrs = ['castsShadows','receivesShadows','motionBlur','primaryVisibility','smoothShading',
                      'smoothShading','visibleInReflections','visibleInRefractions','doubleSided']
    _d_sourceAttrs = {}
    _d_targetAttrs = {}
    _sourceShape = mc.listRelatives(sourceObject,shapes=True,fullPath=True)[0]
    _targetShape = mc.listRelatives(wrappedTargetObject,shapes=True,fullPath=True)[0]
    for a in _l_sourceAttrs:
	_d_sourceAttrs[a] = attributes.doGetAttr(_sourceShape,a)
	_d_targetAttrs[a] = attributes.doGetAttr(_targetShape,a)

    #Wrap deformer"""
    _l_wrapBuffer = returnObjectDeformers(wrappedTargetObject, deformerTypes = 'wrap')
    mc.select([wrappedTargetObject,sourceObject])
    mc.CreateWrap()#...this doesn't return our wrap...thanks maya
    _l_wrapBufferPost = returnObjectDeformers(wrappedTargetObject, deformerTypes = 'wrap')
    for o in _l_wrapBufferPost:
	if o not in _l_wrapBuffer:
	    wrapDeformer = o
	    continue
    
    wrapDeformer = mc.rename(wrapDeformer, (names.getBaseName(targetObject)+'_wrapDeformer'))
    
    """"wrapDeformerBuffer = mc.deformer(wrappedTargetObject, type='wrap')
    wrapDeformer = wrapDeformerBuffer[0]
    wrapDeformer = mc.rename(wrapDeformer,(mc.ls(targetObject,shortNames=True)[0]+'_wrapDeformer'))
    #cause maya is stupid and doesn't have a python equivalent
    mc.select(wrappedTargetObject,r=True)
    mc.select(sourceObject,tgl=True)
    mel.eval('AddWrapInfluence')
    mc.select(cl=True)"""
    
    """
    CreateWrap;
    performCreateWrap false;
    deformer -type wrap pSphere1;
    """
    
    #...deformer attriputes
    _d = {'envelope':1,
          'weightThreshold':1,
          'maxDistance':100,
          'autoWeightThreshold':1,
          'falloffMode':0}
    
    for k in _d.keys():
	try:
	    _v = _d[k]
	    attributes.doSetAttr(wrapDeformer,k,_v)
	    log.debug("wrapDeformObject >> {0} Set {1} - {2}".format(wrapDeformer,k,_v))	    
	except Exception,error:
	    log.error("wrapDeformObject >> failed to set {0}-{1} | error: {2}".format(k,_v,error))
	    
    #...restore shape attrs
    for a,v in _d_sourceAttrs.iteritems():
	try:
	    attributes.doSetAttr(_sourceShape,a,v)      
	except Exception,error:
	    log.error("wrapDeformObject >> failed to restore {0}-{1} | error: {2}".format(a,v,error))
    for a,v in _d_targetAttrs.iteritems():
	try:
	    attributes.doSetAttr(_targetShape,a,v)      
	except Exception,error:
	    log.error("wrapDeformObject >> failed to restore {0}-{1} | error: {2}".format(a,v,error))	    
    return ([wrapDeformer,wrappedTargetObject])

def proximityWrapObject(targetObject, sourceObject, duplicateObject = False,
                        proximityMode = 1, expandBy = 'softSelect', expandAmount = 'default'):
    """
    --- Updated - 04.21.2016
    
    Function for proximity 
    
    See cgm.core.lib.geo_Utils.get_proximityGeo for more details on the mesh creation

    :parameters:
	targetObject(str): Object to wrap
	sourceObject(str): Object to wrap to
	duplicateObject(bool):whether to duplicate target or not
	proximityMode(int):search by
           0: rayCast interior
           1: bounding box -- THIS IS MUCH FASTER
        expandBy(str): None
                       expandSelection: uses polyTraverse to grow selection
                       softSelect: use softSelection with linear falloff by the expandAmount Distance
        expandAmount(float/int): amount to expand.

    :returns
	returnList(list) - [wrapDeformer,wrappedTargetObject,proximeshWrapDeformer,proximesh]
    """    
    #Make a dup to bake
    if duplicateObject == True:
        wrappedTargetObject = mc.duplicate(targetObject)
        wrappedTargetObject = rigging.doParentToWorld(wrappedTargetObject)
        wrappedTargetObject = mc.rename(wrappedTargetObject,(targetObject+'_baked'))

        """ Freeze """
        #mc.makeIdentity(wrappedTargetObject,apply=True, t=True,r=True,s=True)
        mc.delete(wrappedTargetObject,ch=True)
    else:
        wrappedTargetObject = targetObject
	
    #Generate proximity Mesh
    _proxiMesh = GEOUTILS.get_proximityGeo(wrappedTargetObject, sourceObject,
                                           returnMode = 4,
                                           mode=proximityMode, 
                                           expandBy=expandBy, 
                                           expandAmount=expandAmount)[0]
    
    #Create wraps
    _mainWrap = wrapDeformObject (wrappedTargetObject, _proxiMesh)
    _proxiWrap = wrapDeformObject(_proxiMesh, sourceObject)
    
    return [_mainWrap[0], wrappedTargetObject ,_proxiWrap[0],_proxiMesh]
    
    
	

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Blendshape Baking
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def bakeBlendShapeNodesToTargetObject(targetObject = None,sourceObject = None, blendShapeNodes= None,
                                      baseNameToUse = False, stripPrefix = False,
                                      ignoreInbetweens = False, ignoreTargets = False,
                                      cullNoChangeGeo = True, tolerance = .002,
                                      wrapMethod = 'wrap', proximityMode = 1, expandBy = 'softSelect',expandAmount = 'default',
                                      polySmoothness = 0,
                                      transferConnections = True):
    """
    Update 07.14.2016
    DESCRIPTION:
    Function for baking a series of blendshapes from one object to another

    ARGUMENTS:
    targetObject(string)
    sourceObject(string)
    blendShapeNodes(list) the nodes to bake from
    baseNameToUse(bool/string) - if it's False, it uses the target Object name, else, it uses what is supplied
    stripPrefix(bool)
    ignoreInbetweens(bool)
    ignoreTargets(list) - list of targets to ignore
    cullNoChangeGeo(bool) - Remove shapes that don't change the base
    tolearance(float) - amount of tolerance for the cull check
    wrapMethod(int):
            0:wrap
	    1:influence wrap
	    2:proximity wrap
    proximityMode(int):search by
       0: rayCast interior
       1: bounding box -- THIS IS MUCH FASTER
    expandBy(str): None
		   expandSelection: uses polyTraverse to grow selection
		   softSelect: use softSelection with linear falloff by the expandAmount Distance
    expandAmount(float/int): amount to expand.
    polySmoothness(float) -- only valid for influence wrap method
    transferConnections(bool) - if True, builds a new blendshape node and transfers the connections from our base objects

    RETURNS:
    Success(bool)
    """
    _wrapMethods = ['wrap','influence wrap','proximity wrap']
    if cgmVALID.stringArg(wrapMethod):
	if wrapMethod not in _wrapMethods:
	    raise ValueError,"{0} not in wrapMethods: {1}".format(wrapMethod,_wrapMethods)
	_wrapMethod = _wrapMethods.index(wrapMethod)
    elif wrapMethod > len(_wrapMethods):
	raise ValueError,"{0} not valid value for wrapMethod. Greater than length of possible values: {1}".format(wrapMethod,_wrapMethods)
    else:
	_wrapMethod = wrapMethod
		
    if targetObject is None:
	raise ValueError,"'targetObject' cannot be None"
    elif sourceObject is None:	
	raise ValueError,"'sourceObject' cannot be None"
    elif blendShapeNodes is None:   
	raise ValueError,"'blendShapeNodes' cannot be None"
	
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prep
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    blendShapeNamesBaked = []
    l_bakedGeo = []
    
    blendShapeNodes = cgmVALID.listArg(blendShapeNodes)
    
    """ size """
    #sizeBuffer = distance.returnBoundingBoxSize(targetObject)
    #sizeX = sizeBuffer[0]
    #sizeY = sizeBuffer[1]

    """ base name """
    #if not baseNameToUse:
    #    baseNameToUse = ''
    #else:
    #    baseNameToUse = baseNameToUse + '_'
	

    #Wrap
    attributes.doSetLockHideKeyableAttr(targetObject, lock = False, visible = True, keyable=True)#...make sure our target geo can be wrapped
    
    l_delete = []
    if _wrapMethod is 0:
	wrapBuffer = wrapDeformObject(targetObject,sourceObject,True)
	l_delete = [wrapBuffer[0]]
    elif _wrapMethod is 1:
	wrapBuffer = influenceWrapObject(targetObject,sourceObject,True,polySmoothness)
	l_delete = [wrapBuffer[0],wrapBuffer[2]]
    elif _wrapMethod is 2:
	wrapBuffer = proximityWrapObject(targetObject, sourceObject, 
	                                 True, proximityMode, expandBy,expandAmount)
	l_delete = [wrapBuffer[0], wrapBuffer[2], wrapBuffer[3]]
	
    targetObjectBaked = wrapBuffer[1]
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Meat of it
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    d_blendshapeData = {}
    l_blendshapeKeys = []#...list to index well
    l_bakedShapeKeys = []
    l_culled = []
    int_cnt = 0
    
    for bsn in blendShapeNodes:
	try:
	    l_bsChannels = returnBlendShapeAttributes(bsn)
	    d_blendShapeConnections = {}
	    d_currentConnections = {}
	    """ first loop stores and sets everything to 0 """
	    for shape in l_bsChannels:
		blendShapeBuffer = (bsn + '.' + shape)
		""" get the connection """
		d_blendShapeConnections[shape] = attributes.returnDriverAttribute(blendShapeBuffer)	
		
		d_blendshapeData[int_cnt] = {'shape':shape,
		                             'fullShape':blendShapeBuffer,
		                             'connection':d_blendShapeConnections[shape]}#...establish our subdict						
		int_cnt += 1#...advance our count
		
		if ignoreTargets and shape in ignoreTargets:
		    continue
		
		log.debug('breaking connection on: {0}'.format(blendShapeBuffer))
		attributes.doBreakConnection(blendShapeBuffer)
		attributes.doSetAttr(bsn,shape,0)
	
	    # Bake it
	    bakedGeo = bakeBlendShapes(sourceObject, targetObjectBaked, bsn, baseNameToUse, stripPrefix, ignoreInbetweens, ignoreTargets)
	    l_bakedShapeKeys.extend([names.getBaseName(o) for o in bakedGeo])
	
	    if cullNoChangeGeo:
		l_good = []
		for i,o in enumerate(bakedGeo):
		    if GEOUTILS.is_equivalent(targetObject,o, tolerance):
			l_culled.append(o)
			mc.delete(o)
		    else:l_good.append(o)
		bakedGeo = l_good
		    
	    l_bakedGeo.extend(bakedGeo)
		    
	    """ restore connections """
	    for shape in l_bsChannels:
		if ignoreTargets and shape in ignoreTargets:
		    continue
	
		blendShapeBuffer = (bsn+'.'+shape)
		""" Restore the connection """
		log.debug('connecting {0} | {1}'.format(shape,d_blendShapeConnections[shape]))
		if d_blendShapeConnections[shape]:
		    attributes.doConnectAttr(d_blendShapeConnections[shape],blendShapeBuffer)
	except Exception,error:
	    raise Exception,"{0} | error: {1}".format(bsn, error)


	
    # Need to build a new blendshape node?
    newBlendShapeNode = False
    
    if transferConnections and l_bakedGeo:
	try:
	    # Build it			
	    newBlendShapeNode = buildBlendShapeNode(targetObject, l_bakedGeo)
	    newBlendShapeChannels = returnBlendShapeAttributes(newBlendShapeNode)
	    #if len(newBlendShapeChannels)!= len(d_blendshapeData.keys()):
		#log.warning("Cannot transfer connections. Lengths of data lists do not match")
		
	    for i,shape in enumerate(newBlendShapeChannels):
		blendShapeBuffer = (newBlendShapeNode+'.'+shape)
		currentIndex = newBlendShapeChannels.index(shape)
		currentIndex = l_bakedShapeKeys.index(shape)
		if d_blendshapeData[currentIndex]['connection'] != False:
		    attributes.doConnectAttr(d_blendshapeData[currentIndex]['connection'],blendShapeBuffer)
		else:
		    log.warning("Couldn't find connection data for {0}".format(blendShapeBuffer))
	except Exception,error:
	    raise Exception,"Transfer connection fail | error: {0}".format(error)
	
   
	    #blendShape -e  -tc 0 -rm -t pSphere1 152 pSphere1_bsGeo_grp|l_fingers_facet 1 -t pSphere1 152 pSphere1 1 pSphere1_bsNode;
	
    log.debug("Delete: {0}".format(l_delete))
    mc.delete(l_delete)
    mc.delete(targetObjectBaked) 
    
    _tar_baseName = names.getBaseName(targetObject)
    
    if l_culled:
	log.info("Culled the following ({0}) targets for '{1}' on '{2}':".format(len(l_culled),_tar_baseName,blendShapeNodes))
	for o in l_culled:
	    log.info("    " + o)
	    
    if not l_bakedGeo:
	return []    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Finish out
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #Group geo ----------------------------------------------------------------------------------------------------
    meshGroup = mc.group( em=True)
    if baseNameToUse is not False:
        attributes.storeInfo(meshGroup,'cgmName', baseNameToUse)
    else:
	attributes.storeInfo(meshGroup,'cgmName', _tar_baseName)
    attributes.storeInfo(meshGroup,'cgmTypeModifier', 'blendShapeGeo')
    meshGroup = NameFactory.doNameObject(meshGroup)

    for i,geo in enumerate(l_bakedGeo):
        l_bakedGeo[i] = rigging.doParentReturnName(geo,meshGroup)
	
    #return prep ----------------------------------------------------------------------------------------------------
    l_return = [meshGroup,
                l_bakedGeo]
    if newBlendShapeNode:
	l_return.append(newBlendShapeNode)
    return l_return

def bakeBlendShapeNodeToTargetObject(targetObject,sourceObject, blendShapeNode, baseNameToUse = False, 
                                     stripPrefix = False,ignoreInbetweens = False, ignoreTargets = False, 
                                     transferConnections = True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for baking a series of blendshapes from one object to another

    ARGUMENTS:
    targetObject(string)
    sourceObject(string)
    blendShapeNode(string) the node to bake from
    baseNameToUse(bool/string) - if it's False, it uses the target Object name, else, it uses what is supplied
    stripPrefix(bool)
    ignoreInbetweens(bool)
    ignoreTargets(list) - list of targets to ignore
    transferConnections(bool) - if True, builds a new blendshape node and transfers the connections from our base objects

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prep
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ declare variables """
    returnList = []
    blendShapeNamesBaked = []
    blendShapeConnections = []
    currentConnections = []
    bakedGeo = []

    """ size """
    sizeBuffer = distance.returnBoundingBoxSize(targetObject)
    sizeX = sizeBuffer[0]
    sizeY = sizeBuffer[1]

    """ base name """
    if baseNameToUse == False:
        baseName = ''
    else:
        baseName = baseNameToUse + '_'

    """ wrap deform object """
    wrapBuffer = wrapDeformObject(targetObject,sourceObject,True)
    targetObjectBaked = wrapBuffer[1]

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Meat of it
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    blendShapeNodeChannels = returnBlendShapeAttributes(blendShapeNode)

    blendShapeShortNames = []
    """ first loop stores and sets everything to 0 """

    for shape in blendShapeNodeChannels:
        keepGoing = True
        if ignoreTargets != False:
            if shape in ignoreTargets:
                keepGoing = False
            else:
                keepGoing = True

        blendShapeBuffer = (blendShapeNode + '.' + shape)
        """ get the connection """
        blendShapeConnections.append(attributes.returnDriverAttribute(blendShapeBuffer))

        if keepGoing == True:
            print ('breaking....' + blendShapeBuffer)
            """break it """
            attributes.doBreakConnection(blendShapeBuffer)
            attributes.doSetAttr(blendShapeNode,shape,0)

    # Bake it
    bakedGeo = bakeBlendShapes(sourceObject, targetObjectBaked, blendShapeNode, baseNameToUse, stripPrefix, ignoreInbetweens, ignoreTargets)


    """ restore connections """
    for shape in blendShapeNodeChannels:
        keepGoing = True
        if ignoreTargets != False:
            if shape in ignoreTargets:
                keepGoing = False
            else:
                keepGoing = True

        currentIndex = blendShapeNodeChannels.index(shape)
        blendShapeBuffer = (blendShapeNode+'.'+shape)
        """ Restore the connection """
        if keepGoing == True:
            print ('connecting....' + blendShapeBuffer)
            print blendShapeConnections[currentIndex]
            if blendShapeConnections[currentIndex] != False:
                attributes.doConnectAttr(blendShapeConnections[currentIndex],blendShapeBuffer)


    # Need to build a new blendshape node?
    if transferConnections == True:
        # Build it
        newBlendShapeNode = buildBlendShapeNode(targetObject, bakedGeo, baseNameToUse)

        newBlendShapeChannels = returnBlendShapeAttributes(newBlendShapeNode)

        for shape in newBlendShapeChannels:
            blendShapeBuffer = (newBlendShapeNode+'.'+shape)
            currentIndex = newBlendShapeChannels.index(shape)
            if blendShapeConnections[currentIndex] != False:
                attributes.doConnectAttr(blendShapeConnections[currentIndex],blendShapeBuffer)

    """delete the wrap"""
    mc.delete(wrapBuffer[0])

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Finish out
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ group for geo """
    meshGroup = mc.group( em=True)
    if baseNameToUse != False:
        attributes.storeInfo(meshGroup,'cgmName', baseNameToUse)
    attributes.storeInfo(meshGroup,'cgmTypeModifier', 'blendShapeGeo')
    meshGroup = NameFactory.doNameObject(meshGroup)

    for geo in bakedGeo:
        rigging.doParentReturnName(geo,meshGroup)

    returnList.append(meshGroup)
    returnList.append(bakedGeo)

    mc.delete(targetObjectBaked)
    return returnList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def bakeCombinedBlendShapeNodeToTargetObject(targetObject,sourceObject, blendShapeNode, baseName = False, directions=['left','right']):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for baking a series of blendshapes from one object to another when you have a left/right variant

    ARGUMENTS:
    targetObject(string)
    sourceObject(string)
    blendShapeNode(string) the node to bake from
    baseName(bool/string) - if it's False, it uses the target Object name, else, it uses what is supplied
    directions[list] = (['left','right'])

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prep
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ declare variables """
    returnList = []
    blendShapeNamesBaked = []
    blendShapeConnections = []
    currentConnections = []
    bakedGeo = []

    """ size """
    sizeBuffer = distance.returnBoundingBoxSize(targetObject)
    sizeX = sizeBuffer[0]
    sizeY = sizeBuffer[1]

    """ base name """
    if baseName == False:
        baseName = ''
    else:
        baseName = baseName + '_'

    """reference check """
    refPrefix = search.returnReferencePrefix(sourceObject)
    if refPrefix != False:
        referencePrefix = (search.returnReferencePrefix(sourceObject) + ':')
    else:
        referencePrefix = ''

    """ wrap deform object """
    wrapBuffer = wrapDeformObject(targetObject,sourceObject,True)
    targetObjectBaked = wrapBuffer[1]

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Meat of it
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    #setAttr ($wrapDeformer[0] + ".autoWeightThreshold") 1;
    """ cause maya is stupid and doesn't have a python equivalent"""
    mc.select(targetObjectBaked,r=True)
    mc.select(sourceObject,tgl=True)
    mel.eval('AddWrapInfluence')
    mc.select(cl=True)

    """
    may need to add this in later
    //reorders deformation order for proper baking of skinned mesh
    //reorderDeformers "tweak1" "face_skinCluster" $deformerGeo;
    """

    blendShapeNodeChannels = search.returnBlendShapeAttributes(blendShapeNode)
    blendShapeShortNames = []

    """ first loop stores and sets everything to 0 """
    for shape in blendShapeNodeChannels:
        blendShapeBuffer = (blendShapeNode+'.'+shape)
        blendShapeConnections.append(attributes.returnDriverAttribute(blendShapeBuffer))
        """break it """
        attributes.doBreakConnection(blendShapeBuffer)
        attributes.doSetAttr(blendShapeNode,shape,0)

    """ Find pairs """
    blendshapePairs = lists.returnMatchedStrippedEndList(blendShapeNodeChannels,directions)

    """ first loop stores and sets everything to 0 """
    for pair in blendshapePairs:
        blendShapeBuffer = (blendShapeNode+'.'+pair[0])
        splitBuffer = pair[0].split('_')
        nameBuffer = splitBuffer[:-1]
        pairBaseName = '_'.join(nameBuffer)

        if '_' in list(pairBaseName):
            newSplitBuffer = pair[0].split('_')
            newNameBuffer = newSplitBuffer[1:]
            blendShapeShortNames.append('_'.join(newNameBuffer))
        else:
            blendShapeShortNames.append(pairBaseName)

    t=1
    pair = 0
    for i in range (len(blendshapePairs)):
        row = i//5
        if t>5:
            t=1
        """ start extracting """
        blendShapeNodeChannelsBuffer = blendshapePairs[pair]
        shape1 = blendShapeNodeChannelsBuffer[0]
        shape2 = blendShapeNodeChannelsBuffer[1]
        attributes.doSetAttr(blendShapeNode,shape1,1)
        attributes.doSetAttr(blendShapeNode,shape2,1)
        dupBuffer = mc.duplicate(targetObjectBaked)
        splitBuffer = blendShapeShortNames[pair].split('_')
        nameBuffer = splitBuffer[:-1]
        shortName = '_'.join(nameBuffer)

        dupBuffer = mc.rename (dupBuffer,(baseName+shortName))
        mc.xform(dupBuffer,r=True,t=[((sizeX*(t+1.2))*1.5),(sizeY*row*-1.5),0])
        bakedGeo.append(dupBuffer)

        attributes.doSetAttr(blendShapeNode,shape1,0)
        attributes.doSetAttr(blendShapeNode,shape2,0)
        pair +=1
        t+=1

    """ restore connections """
    for shape in blendShapeNodeChannels:
        currentIndex = blendShapeNodeChannels.index(shape)
        blendShapeBuffer = (blendShapeNode+'.'+shape)
        """ Restore the connection """
        if blendShapeConnections[currentIndex] != False:
            attributes.doConnectAttr(blendShapeConnections[currentIndex],blendShapeBuffer)

    """delete the wrap"""
    mc.delete(wrapBuffer[0])

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Finish out
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ group for geo """
    meshGroup = mc.group( em=True)
    attributes.storeInfo(meshGroup,'cgmName', baseName)
    attributes.storeInfo(meshGroup,'cgmTypeModifier', 'blendShapeGeo')
    meshGroup = NameFactory.doNameObject(meshGroup)

    for geo in bakedGeo:
        rigging.doParentReturnName(geo,meshGroup)

    returnList.append(meshGroup)
    returnList.append(bakedGeo)

    mc.delete(targetObjectBaked)
    return returnList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def bakeCombinedBlendShapeNode(sourceObject, blendShapeNode, baseNameToUse = False, directions=['left','right']):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for baking a series of blendshapes out from one object that have a split type

    ARGUMENTS:
    sourceObject(string)
    sourceObject(string)
    blendShapeNode(string) the node to bake from
    baseName(bool/string) - if it's False, it uses the target Object name, else, it uses what is supplied
    directions[list] = (['left','right'])

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prep
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ declare variables """
    returnList = []
    blendShapeNamesBaked = []
    blendShapeConnections = []
    currentConnections = []
    bakedGeo = []

    """ size """
    sizeBuffer = distance.returnBoundingBoxSize(sourceObject)
    sizeX = sizeBuffer[0]
    sizeY = sizeBuffer[1]

    """ base name """
    if baseNameToUse == False:
        baseName = ''
    else:
        baseName = baseNameToUse + '_'


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Meat of it
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    blendShapeNodeChannels = search.returnBlendShapeAttributes(blendShapeNode)
    blendShapeShortNames = []

    """ first loop stores and sets everything to 0 """
    for shape in blendShapeNodeChannels:
        blendShapeBuffer = (blendShapeNode+'.'+shape)
        blendShapeConnections.append(attributes.returnDriverAttribute(blendShapeBuffer))
        """break it """
        attributes.doBreakConnection(blendShapeBuffer)
        attributes.doSetAttr(blendShapeNode,shape,0)

    """ Find pairs """
    blendshapePairs = lists.returnMatchedStrippedEndList(blendShapeNodeChannels,directions)

    """ first loop stores and sets everything to 0 """
    for pair in blendshapePairs:
        blendShapeBuffer = (blendShapeNode+'.'+pair[0])
        splitBuffer = pair[0].split('_')
        nameBuffer = splitBuffer[:-1]
        pairBaseName = '_'.join(nameBuffer)

        if '_' in list(pairBaseName):
            newSplitBuffer = pair[0].split('_')
            newNameBuffer = newSplitBuffer[1:]
            blendShapeShortNames.append('_'.join(newNameBuffer))
        else:
            blendShapeShortNames.append(pairBaseName)

    t=1
    pair = 0
    for i in range (len(blendshapePairs)):
        row = i//5
        if t>5:
            t=1
        """ start extracting """
        blendShapeNodeChannelsBuffer = blendshapePairs[pair]
        shape1 = blendShapeNodeChannelsBuffer[0]
        shape2 = blendShapeNodeChannelsBuffer[1]
        blendShape1Buffer = (blendShapeNode+'.'+shape1)
        blendShape2Buffer = (blendShapeNode+'.'+shape2)
        attributes.doSetAttr(blendShapeNode,shape1,1)
        attributes.doSetAttr(blendShapeNode,shape2,1)
        dupBuffer = mc.duplicate(sourceObject)


        splitBuffer = blendShapeShortNames[pair].split('_')
        if len(splitBuffer)>1:
            nameBuffer = splitBuffer[:-1]
        else:
            nameBuffer = splitBuffer
        shortName = '_'.join(nameBuffer)

        dupBuffer = mc.rename (dupBuffer,(baseName+shortName))
        """ Unlock it """
        attributes.doSetLockHideKeyableAttr(dupBuffer,False,True,True)

        mc.xform(dupBuffer,r=True,t=[((sizeX*(t+1.2))*1.5),(sizeY*row*-1.5),0])
        bakedGeo.append(dupBuffer)

        attributes.doSetAttr(blendShapeNode,shape1,0)
        attributes.doSetAttr(blendShapeNode,shape2,0)
        pair +=1
        t+=1

    """ restore connections """
    for shape in blendShapeNodeChannels:
        currentIndex = blendShapeNodeChannels.index(shape)
        blendShapeBuffer = (blendShapeNode+'.'+shape)
        """ Restore the connection """
        if blendShapeConnections[currentIndex] != False:
            attributes.doConnectAttr(blendShapeConnections[currentIndex],blendShapeBuffer)


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Finish out
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ group for geo """
    meshGroup = mc.group( em=True)
    attributes.storeInfo(meshGroup,'cgmName', baseNameToUse)
    attributes.storeInfo(meshGroup,'cgmTypeModifier', 'blendShapeGeo')
    meshGroup = NameFactory.doNameObject(meshGroup)

    for geo in bakedGeo:
        rigging.doParentReturnName(geo,meshGroup)

    returnList.append(meshGroup)
    returnList.append(bakedGeo)

    return returnList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def bakeBlendShapeNode(sourceObject, blendShapeNode, baseNameToUse = False, stripPrefix = False, ignoreInbetweens = False, ignoreTargets = False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for exporting an object's blendshapes

    ARGUMENTS:
    targetObject(string)
    sourceObject(string)
    blendShapeNode(string) the node to bake from
    baseName(bool/string) - if it's False, it uses the target Object name, else, it uses what is supplied
    stripPrefix(bool) - whether to strip the first '_' segment
    ignoreInbetweens(bool)
    ignoreTargets(list) - targets to ignore in the processing

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prep
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ declare variables """
    returnList = []
    blendShapeNamesBaked = []
    blendShapeConnections = []
    currentConnections = []

    """ base name """
    if baseNameToUse == False:
        baseName = ''
    else:
        baseName = baseNameToUse + '_'


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Meat of it
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    targetDict = returnBlendShapeTargetsAndWeights(sourceObject,blendShapeNode)
    targetSets = []
    blendShapeNodeChannels = []

    for key in targetDict.keys():
        targetSetBuffer = targetDict.get(key)
        targetSets.append(targetSetBuffer)

        baseSet = targetSetBuffer[-1]
        blendShapeNodeChannels.append(baseSet[0])

    blendShapeShortNames = []

    """ first loop gets connections, breaks them and sets everything to 0 """
    for shape in blendShapeNodeChannels:
        blendShapeBuffer = (blendShapeNode+'.'+shape)
        """ get the connection """
        blendShapeConnections.append(attributes.returnDriverAttribute(blendShapeBuffer))
        print blendShapeConnections
        """break it """
        attributes.doBreakConnection(blendShapeBuffer)
        attributes.doSetAttr(blendShapeNode,shape,0)


    # Bake it
    bakedGeo = bakeBlendShapes(sourceObject, sourceObject, blendShapeNode, baseNameToUse, stripPrefix, ignoreInbetweens, ignoreTargets)


    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Finish out
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ restore connections """
    for shape in blendShapeNodeChannels:
        currentIndex = blendShapeNodeChannels.index(shape)
        blendShapeBuffer = (blendShapeNode+'.'+shape)
        """ Restore the connection """
        if blendShapeConnections[currentIndex] != False:
            attributes.doConnectAttr(blendShapeConnections[currentIndex],blendShapeBuffer)

    """ group for geo """
    meshGroup = mc.group( em=True)
    if baseNameToUse != False:
        attributes.storeInfo(meshGroup,'cgmName', baseNameToUse)
    attributes.storeInfo(meshGroup,'cgmTypeModifier', 'blendShapeGeo')
    meshGroup = NameFactory.doNameObject(meshGroup)

    for geo in bakedGeo:
        rigging.doParentReturnName(geo,meshGroup)

    returnList.append(meshGroup)
    returnList.append(bakedGeo)

    return returnList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Blendshape Utilities
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def buildBlendShapeNode(targetObject, blendShapeTargets, nameBlendShape = False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Builds a blendshape node, while looking for in between shapes and connecting them accordingly

    ARGUMENTS:
    targetObject(string)
    blendShapeTargets(list) -
    nameBlendShape(bool/string) - if it's False, it uses the target Object name, else, it uses what is supplied

    RETURNS:
    blendShapeNode(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    # Name stuff
    if nameBlendShape:
        blendShapeNodeName = (str(nameBlendShape) + '_bsNode')
    else:
        blendShapeNodeName = (names.getBaseName(targetObject) + '_bsNode')

    #First look through the targetObjects for inbetween shapes
    baseTargets = []
    inbetweenTargets = []
    for obj in blendShapeTargets:
        if mc.objExists(obj+'.cgmBlendShapeTargetParent'):
            inbetweenTargets.append(obj)
        else:
            baseTargets.append(obj)

    # Make the blendshape node
    try:blendShapeNode = mc.blendShape(baseTargets,targetObject, n = blendShapeNodeName)
    except Exception,error:
	raise Exception,"blendshape build fail | name: {0} | targetObject: {1} | error: {2}".format(blendShapeNodeName,targetObject,error)
    if inbetweenTargets:
	blendShapeChannels = returnBlendShapeAttributes(blendShapeNode[0])	
	# Handle the inbetweens
	for obj in inbetweenTargets:
	    objAttrs = attributes.returnUserAttrsToDict(obj)
    
	    targetParent = objAttrs.get('cgmBlendShapeTargetParent')
	    targetValue = float(objAttrs.get('cgmBlendShapeInbetweenWeight'))
	    bsIndice = blendShapeChannels.index(targetParent)
    
	    mc.blendShape(blendShapeNode[0], edit = True, ib = True , target = [targetObject,bsIndice,obj,targetValue])

    return blendShapeNode[0]



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def bakeBlendShapes(sourceObject, targetObject, blendShapeNode, baseNameToUse = False, stripPrefix = False, ignoreInbetweens = False, ignoreTargets = False):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for exporting an objects blendshapes

    ARGUMENTS:
    targetObject(string)
    sourceObject(string)
    blendShapeNode(string) the node to bake from
    baseName(bool/string) - if it's False, it uses the target Object name, else, it uses what is supplied
    stripPrefix(bool) - whether to strip the first '_' segment
    ignoreInbetweens(bool) - whether to include inbetween targets or not
    ignoreTargets(list) - targets you want ignored during processing

    RETURNS:
    bakedGeo(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    targetDict = returnBlendShapeTargetsAndWeights(sourceObject,blendShapeNode)
    
    """ size """
    sizeBuffer = distance.returnBoundingBoxSize(targetObject)
    sizeX = sizeBuffer[0]
    sizeY = sizeBuffer[1]

    #  base name
    if baseNameToUse == False:
        baseName = ''
    else:
        baseName = baseNameToUse + '_'

    t=1
    i=0
    bakedGeo = []
    for key in targetDict.keys():

        targetSetBuffer = targetDict.get(key)

        if ignoreInbetweens == False:
            targetSetProcessSet = targetSetBuffer
        else:
            targetSetProcessSet = targetSetBuffer[-1:]

        if len(targetSetProcessSet) > 1:
            isInbetween = True
            targetSetProcessSet.reverse()
        else:
            isInbetween = False

        cnt = 0
        for targetSet in targetSetProcessSet:
            row = i//5
            if t>5:
                t=1

            # Check for it being an ignore target
            nameBuffer = targetSet[0]
            keepGoing = True

            if ignoreTargets != False:
                if nameBuffer in ignoreTargets:
                    keepGoing = False
                else:
                    keepGoing = True

            if keepGoing:
                #process the name
                if '_' in list(nameBuffer) and stripPrefix == True:
                    splitBuffer = nameBuffer.split('_')
                    newNameBuffer = splitBuffer[1:]
                    newName = ('_'.join(newNameBuffer))
                else:
                    newName = nameBuffer

                #>>> Start extracting
                #set our values
                mc.blendShape(blendShapeNode, edit = True, weight = [key,targetSet[1]])
                dupBuffer = mc.duplicate(targetObject)
                dupBuffer = mc.rename (dupBuffer,(baseName+newName))

                # Take care of inbetween tagging
                if isInbetween == True:
                    if cnt == 0:
                        rootTarget = dupBuffer
                    else:
                        attributes.storeInfo(dupBuffer,'cgmBlendShapeTargetParent',rootTarget)
                        attributes.storeInfo(dupBuffer,'cgmBlendShapeInbetweenWeight',targetSet[1])

                # Unlock it
                attributes.doSetLockHideKeyableAttr(dupBuffer,False,True,True)
                mc.xform(dupBuffer,r=True,t=[((sizeX*(t+1.2))*1.5),(sizeY*row*-1.5),0])
                bakedGeo.append(dupBuffer)

                # Iterate
                i+=1
                t+=1
                cnt+=1

        if keepGoing == True:
            mc.blendShape(blendShapeNode, edit = True, weight = [key,0])

    return bakedGeo

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Blendshape Info
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnBlendShapeAttributes(blendshapeNode):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns cv coordinates from a surface CV

    ARGUMENTS:
    surfaceCV(string)

    RETURNS:
    coordinates(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    return (mc.listAttr((blendshapeNode+'.weight'),m=True))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnBlendShapeBaseObjects(blendShapeNode):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the base objects of a blendshape node

    ARGUMENTS:
    blendShapeNode(string)

    RETURNS:
    baseObjects(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prep
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    #Declare the blendshape node as an MObject
    blendShapeNode = apiExtensions.asMObject( blendShapeNode )
    #Attach the functions set
    bsFn = MFnBlendShapeDeformer (blendShapeNode)
    baseObjectsObjArray = apiExtensions.MObjectArray()
    bsFn.getBaseObjects(baseObjectsObjArray)

    baseObjects = []
    for i in range( baseObjectsObjArray.length() ):
        baseObjects.append( str( apiExtensions.asMObject(baseObjectsObjArray[i]) )  )
    return baseObjects

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnBlendShapeIndexList(blendShapeNode):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for baking a series of blendshapes from one object to another when you have a left/right variant

    ARGUMENTS:
    targetObject(string)
    sourceObject(string)
    blendShapeNode(string) the node to bake from
    baseName(bool/string) - if it's False, it uses the target Object name, else, it uses what is supplied
    directions[list] = (['left','right'])

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prep
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    #Declare the blendshape node as an MObject
    blendShapeNode = apiExtensions.asMObject( blendShapeNode )
    #Attach the functions set
    bsFn = MFnBlendShapeDeformer (blendShapeNode)
    weightListIntArray = apiExtensions.MIntArray()

    bsFn.weightIndexList(weightListIntArray)

    return weightListIntArray

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Blendshape Inbetweening
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnBlendShapeTargetsAndWeights(sourceObject, blendShapeNodeName):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Function for returning the targets per blendshape index, including inbetween shapes

    ARGUMENTS:
    sourceObject(string)
    blendShapeNode(string)

    RETURNS:
    targetDict(dict) - {0:[[target_1,.5],[target_2,1.0]],1:[[target_3,1.0]].....}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Prep
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    targetIndices = returnBlendShapeIndexList(blendShapeNodeName)
    sourceObjectShapes = mc.listRelatives(sourceObject, shapes = True)
    print sourceObjectShapes

    #Declare the blendshape node as an MObject
    blendShapeNode = apiExtensions.asMObject( blendShapeNodeName )
    #Attach the functions set
    bsFn = MFnBlendShapeDeformer (blendShapeNode)

    #Declare variables
    baseObjects = apiExtensions.MObjectArray()
    #>>>>May need better logic for detecting the base
    bsFn.getBaseObjects(baseObjects)

    baseObjectBuffer = returnBlendShapeBaseObjects(blendShapeNodeName)
    #base = apiExtensions.asMObject( baseObjectBuffer[0])
    #base = apiExtensions.asMObject( sourceObjectShapes[0] )
    base =  apiExtensions.asMObject( (baseObjects[0]) )

    targetDict = {}

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Meat
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    for i in targetIndices:
        targetsReturnBuffer = []
        targetsObjArray = apiExtensions.MObjectArray()
        bsFn.getTargets(base,i,targetsObjArray)

        for t in range( targetsObjArray.length() ):
            targetReturnBuffer = []
            shapeNameBuffer = ( str(apiExtensions.asMObject(targetsObjArray[t])) )
            geoNameBuffer = mc.listRelatives(shapeNameBuffer,parent = True)
            targetReturnBuffer.append(geoNameBuffer[0])
            # Get the destination attr from which to calculate the inbetween weight
            shapeConnectionAttr = mc.connectionInfo((shapeNameBuffer+'.worldMesh'),destinationFromSource=True)
            targetBuffer = shapeConnectionAttr[0].split('.',)
            indexOneBuffer = targetBuffer[-2].split('[',)
            indexTwoBuffer = indexOneBuffer[1].split(']',)
            rawIndex = int(indexTwoBuffer[0])
            # Calculate inbetween weight using Maya's index = weight * 1000 + 5000 formula
            inbetweenWeight = float( (rawIndex-5000) * .001 )

            #Prep data
            targetReturnBuffer.append(inbetweenWeight)
            targetsReturnBuffer.append(targetReturnBuffer)
        targetDict[i] = targetsReturnBuffer

    return targetDict



