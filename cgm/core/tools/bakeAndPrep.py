import maya.cmds as mc
import os
import pprint
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging

from cgm.core import cgm_Meta as cgmMeta

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def BakeAndPrep(bakeSetName = 'bake_tdSet',
                deleteSetName = "delete_tdSet",
                exportSetName = "export_tdSet",
                startFrame = None,
                endFrame = None,
                euler = True,
                tangent = 'auto'):
    
    baked = Bake(bakeSetName,startFrame = startFrame,endFrame=endFrame, euler=euler, tangent=tangent)
    if baked:
        prepped = Prep(deleteSetName,
                       exportSetName)
    else:
        print("Not baked, so not prepping")

    if not prepped:
        print("Not prepped")

    return prepped

def Bake(assets, bakeSetName = 'bake_tdSet',
         startFrame = None,
         endFrame = None,
         euler = True,
         tangent = 'auto'):
    _str_func = 'Bake'
    
    if startFrame is None:
        startFrame =  mc.playbackOptions(q=True, min=True)
    if endFrame is None:
        endFrame =  mc.playbackOptions(q=True, max=True)
        
    
    baked = False

    #if(mc.optionVar(exists='cgm_bake_set')):
        #bakeSetName = mc.optionVar(q='cgm_bake_set')

    # set tangent options to spline
    currentTangent = mc.keyTangent( q=True, g=True, ott=True )[0]
    mc.keyTangent( g=True, ott="linear" )
    
    #Eval mode ----
    _evalMode = mc.evaluationManager(q=True, mode=True)
    mc.evaluationManager(mode='off')
    
    bakeTransforms = []
    bakeSets = []

    currentTime = mc.currentTime(q=True)
    log.debug("{0} ||currentTime: {1}".format(_str_func,currentTime))

    for asset in assets:
        #if ':' in assets:
        log.debug("{0} || asset: {1}".format(_str_func,asset))
        
        topNodeSN = asset.split(':')[-1]

        # gather data
        namespaces = asset.split(':')[:-1]

        if len(namespaces) > 0:
            ns = ':'.join( asset.split(':')[:-1] ) + ':'
        else:
            ns = "%s_" % asset.split('|')[-1]
        
        # bake
        bakeSet = "%s%s" % (ns, bakeSetName)
        if mc.objExists(bakeSet):
            if bakeSet not in bakeSets:
                bakeSets.append(bakeSet)
                bakeTransforms += mc.sets(bakeSet, q=True)
        else:
            bakeTransforms.append(asset)
        #else:
        #    bakeTransforms.append(asset)
        log.debug("{0} || bakeSet: {1}".format(_str_func,bakeSet))

    if len(bakeTransforms) > 0:
        log.debug("{0} || baking transforms".format(_str_func))
        
        #pprint.pprint(bakeTransforms)
        log.debug("{0} || time | start: {1} | end: {2}".format(_str_func,startFrame,endFrame))
        
        mc.bakeResults( bakeTransforms, 
                        simulation=True, 
                        t=( startFrame, endFrame), 
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
        
        #Filter euler
        if euler or tangent:
            for obj in bakeTransforms:
                if euler:
                    for a in ['rotateX','rotateY','rotateZ']:
                        try:mc.filterCurve( obj + '_' + a )
                        except Exception as err:
                            print(("{0} | {1} | {2}".format(obj,a,err)))
                            
                if tangent:
                    _anim = mc.listConnections(obj, type = 'animCurve')
                    if _anim:
                        mc.keyTangent(_anim, e=1, itt=tangent,ott=tangent,animation='keysOrObjects')            
            
            

        baked = True
    else:
        baked = False

    mc.keyTangent( g=True, ott=currentTangent )

    #eval mode restore ----
    if _evalMode[0] != 'off':
        print(("Eval mode restored: {0}".format(_evalMode[0])))
        mc.evaluationManager(mode = _evalMode[0])

    mc.currentTime(currentTime)

    return baked

def Prep(removeNamespace = False, 
         deleteSetName = "delete_tdSet",
         exportSetName = "export_tdSet",
         zeroRoot = False):
    
    _str_func = 'Prep'
    
    prepped = True
    
    
    #if(mc.optionVar(exists='cgm_delete_set')):
    #    deleteSetName = mc.optionVar(q='cgm_delete_set')
    #if(mc.optionVar(exists='cgm_export_set')):
    #    exportSetName = mc.optionVar(q='cgm_export_set')

    try:
        topNode = cgmMeta.asMeta(mc.ls(sl=True)[0])
    except:
        print("Select top node and try again.")
        return

    currentTime = mc.currentTime(q=True)

    topNodeSN = topNode.mNode.split(':')[-1]

    namespaces = topNode.mNode.split(':')[:-1]
    
    log.debug("{0} || topNode: {1}".format(_str_func,format(topNodeSN)))
    
    log.debug("{0} || ref import".format(_str_func))
    
    # import reference
    if( mc.referenceQuery(topNode.mNode, isNodeReferenced=True) ):
        refFile = mc.referenceQuery( topNode.mNode ,filename=True )
        topRefNode = mc.referenceQuery( topNode.mNode, referenceNode=True, topReference=True)
        topRefFile = mc.referenceQuery(topRefNode, filename=True)

        while refFile != topRefFile:
            mc.file(topRefFile, ir=True)
            topRefNode = mc.referenceQuery( topNode.mNode, referenceNode=True, topReference=True)
            topRefFile = mc.referenceQuery(topRefNode, filename=True)

        mc.file(topRefFile, ir=True)

    log.debug("{0} || namespaces".format(_str_func))
    
    if len(namespaces) > 0:
        for space in namespaces[:-1]:
            mc.namespace( removeNamespace = space, mergeNamespaceWithRoot = True)


        ns = '%s:' % namespaces[-1].replace('|', '')
    else:
        ns = None
        #ns = "%s_" % topNode.mNode
    
    if ns:
        exportSet = "%s%s" % (ns, exportSetName)
        deleteSet = "%s%s" % (ns, deleteSetName)
    else:
        exportSet = exportSetName
        deleteSet = deleteSetName
        
    exportSetObjs = []
    
    log.debug("{0} || export set: {1}".format(_str_func,exportSet))
    
    
    if mc.objExists(exportSet):
        exportSetObjs = cgmMeta.asMeta(mc.sets(exportSet, q=True))
    else:
        exportSetObjs = [topNode]

    # delete garbage
    
        
    log.debug("{0} || delete set: {1}".format(_str_func,deleteSet))
    


    if exportSetObjs:
        for exportObj in exportSetObjs:
            log.debug("{0} || exportObj: {1}".format(_str_func,exportObj.mNode))
            mc.delete(mc.listRelatives(exportObj.mNode, ad=True, type='constraint', fullPath = 1))

            if zeroRoot and mc.objExists('{0}.cgmTypeModifier'.format(exportObj.mNode)):
                if mc.getAttr('{0}.cgmTypeModifier'.format(exportObj.mNode)) == 'rootMotion':
                    log.debug("{0} || Zeroing root: {1}".format(_str_func,exportObj.mNode))
                    mc.cutKey(exportObj.mNode, at=['translate', 'rotate'], clear=True)
                    mc.setAttr('{0}.translate'.format(exportObj.mNode), 0, 0, 0, type='float3')
                    mc.setAttr('{0}.rotate'.format(exportObj.mNode), 0, 0, 0, type='float3')
                    
    if(mc.objExists(deleteSet)):
        mc.delete( mc.sets( deleteSet, q=True ) )  
    else:
        print("No delete set found.")  
        prepped = False    
                    
                    
    if removeNamespace and len(exportSetObjs) > 0:
        l_deformers = []
        for mObj in exportSetObjs:
            l_deformers.extend(mObj.getDeformers(asMeta=1) or [])
            
        for obj in cgmMeta.asMeta(mc.listRelatives([x.mNode for x in exportSetObjs], ad=True, fullPath = 1)) + exportSetObjs + l_deformers:
            if ':' in obj.mNode:
                mc.rename(obj.mNode, obj.mNode.split(':')[-1])

        #exportSetObjs = [x.split(':')[-1] for x in exportSetObjs]

    # export
    newTopNode = '%s%s' % (ns, topNodeSN)
    if not mc.objExists(newTopNode):
        if mc.objExists(topNode.mNode):
            newTopNode = topNode
    else:
        newTopNode = cgmMeta.asMeta(newTopNode)
            
    log.debug("{0} || topNode: {1}".format(_str_func,newTopNode.mNode))
            
    
    # revert to old name
    #for i, tempObj in enumerate(namespaceTransforms):
    #    tempObj.name = origNames[i]

    # revert to previous settings
    mc.currentTime(currentTime)

    if(mc.objExists(exportSet)):
        mc.select( mc.sets( exportSet, q=True ) ) 
    else:
        print(("No export set found ({0}). Selecting top node.".format(exportSet)))
        mc.select( topNode.mNode )
        prepped = False

    exportObjs = cgmMeta.asMeta(mc.ls(sl=True))
    for obj in exportObjs:
        log.debug("{0} || parent pass: {1}".format(_str_func,obj))
        
        try:
            mc.parent(obj.mNode, w=True)
        except:
            print(("%s already a child of 'world'" % obj))
            
            
    if removeNamespace:#...attempt to clean name space stuff
        for mObj in cgmMeta.asMeta(mc.ls("{}:*".format(ns))):
            mObj.rename(mObj.p_nameBase.replace("{}:".format(ns),''))            

    mc.select( [x.mNode for x in exportObjs] )

    mc.refresh()
            

    return prepped

def MakeExportCam(inputCam):
    inputCamShape = mc.listRelatives(inputCam, shapes=True, fullPath = 1)[0]
    exportCam, exportCamShape = mc.camera(name='exportCam')
    mc.parentConstraint(inputCam, exportCam, mo=False)
    mc.connectAttr('%s.focalLength' % inputCam, '%s.focalLength' % exportCamShape)

    return exportCam