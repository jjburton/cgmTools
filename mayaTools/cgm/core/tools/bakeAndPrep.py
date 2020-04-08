import maya.cmds as mc
import os

def BakeAndPrep():
    baked = Bake()
    if baked:
        prepped = Prep()
    else:
        print "Not baked, so not prepping"

    if not prepped:
        print "Not prepped"

    return prepped

def Bake(assets):
    baked = False

    bakeSetName = "bakeSet"
    if(mc.optionVar(exists='cgm_bake_set')):
        bakeSetName = mc.optionVar(q='cgm_bake_set')

    # set tangent options to spline
    currentTangent = mc.keyTangent( q=True, g=True, ott=True )[0]
    mc.keyTangent( g=True, ott="spline" )
    
    #Eval mode ----
    _evalMode = mc.evaluationManager(q=True, mode=True)
    mc.evaluationManager(mode='off')
    
    bakeTransforms = []
    bakeSets = []

    currentTime = mc.currentTime(q=True)

    for asset in assets:
        if ':' in assets:
            topNodeSN = asset.split(':')[-1]

            # gather data
            namespaces = asset.split(':')[:-1]

            if len(namespaces) > 0:
                ns = ':'.join( asset.split(':')[:-1] ) + ':'
            else:
                ns = "%s_" % asset.split('|')[-1]
            
            # bake
            bakeSet = "%s%s" % (ns, bakeSetName)
            if(mc.objExists(bakeSet) and bakeSet not in bakeSets):
                bakeSets.append(bakeSet)
                bakeTransforms += mc.sets(bakeSet, q=True)
        else:
            bakeTransforms.append(asset)

    if len(bakeTransforms) > 0:
        mc.bakeResults( bakeTransforms, 
                        simulation=True, 
                        t=( mc.playbackOptions(q=True, min=True), mc.playbackOptions(q=True, max=True) ), 
                        sampleBy=1, 
                        disableImplicitControl=True,
                        preserveOutsideKeys = False, 
                        sparseAnimCurveBake = False,
                        removeBakedAttributeFromLayer = False, 
                        removeBakedAnimFromLayer = True, 
                        bakeOnOverrideLayer = False, 
                        minimizeRotation = True, 
                        controlPoints = False, 
                        shape = True )

        mc.setInfinity(bakeTransforms, pri='constant', poi='constant')

        baked = True
    else:
        baked = False

    mc.keyTangent( g=True, ott=currentTangent )

    #eval mode restore ----
    if _evalMode[0] != 'off':
        print "Eval mode restored: {0}".format(_evalMode[0])
        
        mc.evaluationManager(mode = _evalMode[0])

    mc.currentTime(currentTime)

    return baked

def Prep(removeNamespace = False):
    prepped = True

    deleteSetName = "deleteSet"
    exportSetName = "exportSet"

    if(mc.optionVar(exists='cgm_delete_set')):
        deleteSetName = mc.optionVar(q='cgm_delete_set')
    if(mc.optionVar(exists='cgm_export_set')):
        exportSetName = mc.optionVar(q='cgm_export_set')

    try:
        topNode = mc.ls(sl=True)[0]
    except:
        print "Select top node and try again."
        return

    currentTime = mc.currentTime(q=True)

    topNodeSN = topNode.split(':')[-1]

    namespaces = topNode.split(':')[:-1]
    
    # import reference
    if( mc.referenceQuery(topNode, isNodeReferenced=True) ):
        refFile = mc.referenceQuery( topNode ,filename=True )
        topRefNode = mc.referenceQuery( topNode, referenceNode=True, topReference=True)
        topRefFile = mc.referenceQuery(topRefNode, filename=True)

        while refFile != topRefFile:
            mc.file(topRefFile, ir=True)
            topRefNode = mc.referenceQuery( topNode, referenceNode=True, topReference=True)
            topRefFile = mc.referenceQuery(topRefNode, filename=True)

        mc.file(topRefFile, ir=True)

    if len(namespaces) > 0:
        for space in namespaces[:-1]:
            mc.namespace( removeNamespace = space, mergeNamespaceWithRoot = True)

        ns = '%s:' % namespaces[-1]
    else:
        ns = "%s_" % topNode

    exportSet = "%s%s" % (ns, exportSetName)
    exportSetObjs = []

    if mc.objExists(exportSet):
        exportSetObjs = mc.sets(exportSet, q=True)
    else:
        exportSetObjs = [topNode]

    if removeNamespace and len(exportSetObjs) > 0:
        for obj in mc.listRelatives(exportSetObjs, ad=True) + exportSetObjs:
            mc.rename(obj, obj.split(':')[-1])

    # delete garbage
    deleteSet = "%s%s" % (ns, deleteSetName)
    if(mc.objExists(deleteSet)):
        mc.delete( mc.sets( deleteSet, q=True ) )  
    else:
        print "No delete set found."  
        prepped = False

    if len(exportSetObjs) > 0:
        mc.delete(mc.listRelatives(exportSetObjs, ad=True, type='constraint'))

    # export
    newTopNode = '%s%s' % (ns, topNodeSN)
    if not mc.objExists(newTopNode):
        if mc.objExists(topNode):
            newTopNode = topNode
    
    # revert to old name
    #for i, tempObj in enumerate(namespaceTransforms):
    #    tempObj.name = origNames[i]

    # revert to previous settings
    mc.currentTime(currentTime)

    if(mc.objExists(exportSet)):
        mc.select( mc.sets( exportSet, q=True ) ) 
    else:
        print "No export set found. Selecting top node."
        mc.select( topNode )
        prepped = False

    exportObjs = mc.ls(sl=True)
    for obj in exportObjs:
        try:
            mc.parent(obj, w=True)
        except:
            print "%s already a child of 'world'" % obj

    mc.select(exportObjs)

    mc.refresh()

    return prepped

def MakeExportCam(inputCam):
    inputCamShape = mc.listRelatives(inputCam, shapes=True)[0]
    exportCam, exportCamShape = mc.camera(name='exportCam')
    mc.parentConstraint(inputCam, exportCam, mo=False)
    mc.connectAttr('%s.focalLength' % inputCam, '%s.focalLength' % exportCamShape)

    return exportCam