'''
------------------------------------------
Red9 Studio Pack: Maya Pipeline Solutions
Author: Mark Jackson
email: rednineinfo@gmail.com

Red9 blog : http://red9-consultancy.blogspot.co.uk/
MarkJ blog: http://markj3d.blogspot.co.uk
------------------------------------------

This is a new implementation of the PoseSaver core, same file format
and ConfigObj but now supports relative pose data handled via a 
posePointCloud and the snapping core

NOTE: I use the node short name as the key in the dictionary so
ALL NODES must have unique names or you may get unexpected  results!
================================================================
'''

import Red9.startup.setup as r9Setup
import Red9_CoreUtils as r9Core
import Red9_General as r9General
import Red9_AnimationUtils as r9Anim
import Red9_Meta as r9Meta

import maya.cmds as cmds
import os
import Red9.packages.configobj as configobj
import time
import getpass
import sys

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class PoseData(object):
    '''
    Here's the plan, we build up a poseDict something like this:
    node=|group|Rig|Body|TestCtr
    
    poseDict['TestCtr']
    poseDict['TestCtr']['ID']=0   index in the Hierarchy used to build the data up
    poseDict['TestCtr']['longName']='|group|Rig|Body|TestCtr'
    poseDict['TestCtr']['attrs']['translateX']=0.5
    poseDict['TestCtr']['attrs']['translateY']=1.0
    poseDict['TestCtr']['attrs']['translateZ']=22
    
    if MetaData:
    poseDict['TestCtr']['metaData']['metaAttr']=CTRL_L_Thing    = the attr that wires this node to the MetaSubsystem
    poseDict['TestCtr']['metaData']['metaNodeID']=L_Arm_System  = the metaNode this node is wired to via the above attr
    
    Matching of nodes against this dict is via either the nodeName, node Index or
    the metaData block.
    '''
    
    def __init__(self, filterSettings=None):
        '''
        I'm not passing any data in terms of nodes here, We'll deal with
        those in the PoseSave and PoseLoad calls. Leaves this open for
        expansion
        '''
        self.poseDict={}
        self.infoDict={}
        self.skeletonDict={}
        self.posePointCloudNodes=[]
        self.filepath=''
        self.mayaUpAxis=r9Setup.mayaUpAxis()
        self.thumbnailRes=[128,128]
        
        self._metaPose=False
        self.metaRig=None # filled by the code as we process
        self.matchMethod='base' #method used to match nodes internally in the poseDict
        self.relativePose=False
        self.relativeRots='projected'
        self.relativeTrans='projected'
        self.useFilter=True
        
        # make sure we have a settings object
        if filterSettings:
            if issubclass(type(filterSettings), r9Core.FilterNode_Settings):
                self.settings=filterSettings
                self._metaPose=self.settings.metaRig
            else:
                raise StandardError('filterSettings param requires an r9Core.FilterNode_Settings object')
        else:
            self.settings=r9Core.FilterNode_Settings()
            self._metaPose=self.settings.metaRig
    
        self.settings.printSettings()
    
    #Property so we sync the settings metaRig bool to the class metaPose bool
    def __get_metaPose(self):
        return self._metaPose
    
    def __set_metaPose(self, val):
        self._metaPose=val
        self.settings.metaRig=val          
          
    metaPose = property(__get_metaPose, __set_metaPose)
    
    def setMetaRig(self,node):
        log.info('setting internal metaRig from given node : %s' % node)
        if r9Meta.isMetaNodeInherited(node,'MetaRig'):
            self.metaRig=r9Meta.MetaClass(node)
        else:
            self.metaRig=r9Meta.getConnectedMetaSystemRoot(node)
        return self.metaRig
    
    def hasFolderOverload(self):    
        posedir=os.path.dirname(self.filepath)
        return os.path.exists(os.path.join(posedir,'poseHandler.py'))
    
    def getNodesFromFolderConfig(self,rootNode,mode):
        '''
        if the poseFolder has a poseHandler.py file use that to
        return the nodes to use for the pose instead
        '''
        import imp
        log.debug('getNodesFromFolderConfig - useFilter=True : custom poseHandler running')
        posedir=os.path.dirname(self.filepath)      
        tempPoseFuncs = imp.load_source('poseHandler', os.path.join(posedir,'poseHandler.py'))
        
        if mode=='load':
            nodes=tempPoseFuncs.poseGetNodesLoad(self,rootNode)
        if mode=='save':
            nodes=tempPoseFuncs.poseGetNodesSave(self,rootNode)
        del(tempPoseFuncs)

        return nodes
                    
    def getNodes(self, nodes): # useFilter=True):
        '''
        get the nodes to process
        This is designed to allow for specific hooks to be used from user
        code stored in the pose folder itself.
        '''
        if not type(nodes)==list: nodes=[nodes]
        if self.useFilter:
            log.debug('getNodes - useFilter=True : no custom poseHandler')
            if self.settings.filterIsActive():
                return r9Core.FilterNode(nodes,self.settings).ProcessFilter() #main node filter
        else:
            log.debug('getNodes - useFilter=False : no custom poseHandler')
            return nodes
        
                      
    # Build the poseDict data ---------------------------------------------
       
    def _buildInfoBlock(self):
        '''
        Basic info for the pose file, this could do with expanding
        '''
        self.infoDict['author']=getpass.getuser()
        self.infoDict['date']=time.ctime()
        self.infoDict['metaPose']=self.metaPose
        if self.metaRig:
            self.infoDict['metaRigNode']  =self.metaRig.mNode
            self.infoDict['metaRigNodeID']=self.metaRig.mNodeID
        if self.rootJnt:
            self.infoDict['skeletonRootJnt']=self.rootJnt
        
    def _buildPoseDict(self, nodes):  
        '''
        Build the internal poseDict up from the given nodes. This is the 
        core of the Pose System 
        '''   
        if self.metaPose:
            getMetaDict=self.metaRig.getNodeConnectionMetaDataMap #optimisation

        for i,node in enumerate(nodes):
            key=r9Core.nodeNameStrip(node)
            self.poseDict[key]={}
            self.poseDict[key]['ID']=i          #selection order index
            self.poseDict[key]['longName']=node #longNode name
            
            if self.metaPose:
                self.poseDict[key]['metaData']=getMetaDict(node)   #metaSystem the node is wired too

            channels=r9Anim.getSettableChannels(node,incStatics=True)
            if channels:
                self.poseDict[key]['attrs']={}
                for attr in channels:
                    try:
                        if cmds.getAttr('%s.%s' % (node,attr),type=True)=='TdataCompound': #blendShape weights support
                            attrs=cmds.aliasAttr(node, q=True)[::2] #extract the target channels from the multi
                            for attr in attrs:
                                self.poseDict[key]['attrs'][attr]=cmds.getAttr('%s.%s' % (node,attr))
                        else:
                            self.poseDict[key]['attrs'][attr]=cmds.getAttr('%s.%s' % (node,attr))
                    except:
                        log.debug('%s : attr is invalid in this instance' % attr)

    def _buildSkeletonData(self, rootJnt):
        '''
        @param rootNode: root of the skeleton to process
        '''
        self.skeletonDict={}
        if not rootJnt:
            log.info('skeleton rootJnt joint was not found')
            return
        
        fn=r9Core.FilterNode(rootJnt)
        fn.settings.nodeTypes='joint'
        fn.settings.incRoots=False
        skeleton=fn.ProcessFilter()
        
        for jnt in skeleton:
            key=r9Core.nodeNameStrip(jnt)
            self.skeletonDict[key]={}
            self.skeletonDict[key]['attrs']={}
            for attr in ['translateX','translateY','translateZ', 'rotateX','rotateY','rotateZ']:
                try:
                    self.skeletonDict[key]['attrs'][attr]=cmds.getAttr('%s.%s' % (jnt,attr))
                except:
                    log.debug('%s : attr is invalid in this instance' % attr)

    def buildInternalPoseData(self, nodes):
        '''
        build the internal pose dict's, useful as a separate func so it
        can be used in the PoseCompare class easily. This is the main internal call
        for managing the actual pose data for save
        '''
        self.metaRig=None
        self.rootJnt=None
        if not type(nodes)==list: nodes=[nodes] #cast to list for consistency
        rootNode=nodes[0]

        if self.settings.filterIsActive() and self.useFilter:
            if self.metaPose:
                if self.setMetaRig(rootNode):
                    self.rootJnt=self.metaRig.getSkeletonRoots()
                    if self.rootJnt:
                        self.rootJnt=self.rootJnt[0]
            else:
                if cmds.attributeQuery('exportSkeletonRoot',node=rootNode,exists=True):
                    connectedSkel=cmds.listConnections('%s.%s' % (rootNode,'exportSkeletonRoot'),destination=True,source=True)
                    if connectedSkel:
                        self.rootJnt=connectedSkel[0]
                if cmds.attributeQuery('animSkeletonRoot',node=rootNode,exists=True):
                    connectedSkel=cmds.listConnections('%s.%s' % (rootNode,'animSkeletonRoot'),destination=True,source=True)
                    if connectedSkel:
                        self.rootJnt=connectedSkel[0]
        else:
            if self.metaPose:
                self.setMetaRig(rootNode)
                
        if self.hasFolderOverload():# and self.useFilter:
            nodesToStore=self.getNodesFromFolderConfig(nodes,mode='save')
        else:
            nodesToStore=self.getNodes(nodes)
                    
        self.poseDict={}         
        self._buildInfoBlock()    
        self._buildPoseDict(nodesToStore) 
        self._buildSkeletonData(self.rootJnt)
        
        
    # Process the data -------------------------------------------------
                                              
    def _writePose(self, filepath):
        '''
        Write the Pose ConfigObj to file
        '''
        ConfigObj = configobj.ConfigObj(indent_type='\t')
        ConfigObj['filterNode_settings']=self.settings.__dict__
        ConfigObj['poseData']=self.poseDict
        ConfigObj['info']=self.infoDict
        if self.skeletonDict:
            ConfigObj['skeletonDict']=self.skeletonDict
        ConfigObj.filename = filepath
        ConfigObj.write()

    @r9General.Timer 
    def _readPose(self, filename):
        '''
        Read the pose file and build up the internal poseDict
        TODO: do we allow the data to be filled from the pose filter thats stored???????
        '''
        if filename:
            if os.path.exists(filename):            
                #for key, val in configobj.ConfigObj(filename)['filterNode_settings'].items():
                #    self.settings.__dict__[key]=decodeString(val)
                self.poseDict=configobj.ConfigObj(filename)['poseData']
                if configobj.ConfigObj(filename).has_key('info'):
                    self.infoDict=configobj.ConfigObj(filename)['info']
                if configobj.ConfigObj(filename).has_key('skeletonDict'):
                    self.skeletonDict=configobj.ConfigObj(filename)['skeletonDict']
            else:
                raise StandardError('Given filepath doesnt not exist : %s' % filename)
        else:
            raise StandardError('No FilePath given to read the pose from')
      
    @r9General.Timer     
    def _applyPose(self, matchedPairs):
        '''
        @param matchedPairs: pre-matched tuples of (poseDict[key], node in scene)
        '''
        for key, dest in matchedPairs:
            log.debug('Applying Key Block : %s' % key)
            try:
                for attr, val in self.poseDict[key]['attrs'].items():
                    try:
                        val=eval(val)
                    except:
                        pass
                    log.debug('node : %s : attr : %s : val %s' % (dest,attr,val))
                    try:
                        cmds.setAttr('%s.%s' % (dest, attr), val)
                    except StandardError,err:
                        log.debug(err)
            except:
                log.debug('Pose Object Key : %s : has no Attr block data' % key)  
                  
    @r9General.Timer 
    def _matchNodesToPoseData(self, nodes):
        '''
        Main filter to extract matching data pairs prior to processing
        return : tuple such that :  (poseDict[key], destinationNode)
        NOTE: I've changed this so that matchMethod is now an internal PoseData attr
        @param nodes: nodes to try and match from the poseDict
        '''
        matchedPairs=[]
        log.info('using matchMethod : %s' % self.matchMethod)
        if self.matchMethod=='stripPrefix' or self.matchMethod=='base':
            log.info( 'matchMethodStandard : %s' % self.matchMethod)
            matchedPairs=r9Core.matchNodeLists([key for key in self.poseDict.keys()], nodes, matchMethod=self.matchMethod)
        if self.matchMethod=='index':
            for i, node in enumerate(nodes):
                for key in self.poseDict.keys():
                    if int(self.poseDict[key]['ID'])==i:
                        matchedPairs.append((key,node))
                        log.info('poseKey : %s %s >> matchedSource : %s %i' % (key, self.poseDict[key]['ID'], node, i))
                        break 
        if self.matchMethod=='metaData':               
            getMetaDict=self.metaRig.getNodeConnectionMetaDataMap #optimisation
            poseKeys=dict(self.poseDict)         #optimisation
            for node in nodes:
                try:
                    metaDict=getMetaDict(node)
                    for key in poseKeys:
                        if poseKeys[key]['metaData']==metaDict:
                            matchedPairs.append((key,node))
                            poseKeys.pop(key)
                            break
                except:
                    log.info('FAILURE to load MetaData pose blocks - Reverting to Name')
                    matchedPairs=r9Core.matchNodeLists([key for key in self.poseDict.keys()], nodes)  
        return matchedPairs   
                             
    def matchInternalPoseObjects(self, nodes=None, fromFilter=True):
        '''
        This is a throw-away and only used in the UI to select for debugging!
        from a given poseFile return or select the internal stored objects 
        '''
        InternalNodes=[]
#        if not fromFilter:
            #no filter, we just pass in the longName thats stored
        for key in self.poseDict.keys():
            if cmds.objExists(self.poseDict[key]['longName']):
                InternalNodes.append(self.poseDict[key]['longName'])
            elif cmds.objExists(key):
                InternalNodes.append(key)
#        else:
#            #use the internal Poses filter and then Match against scene nodes
#            if self.settings.filterIsActive():
#                filterData=r9Core.FilterNode(nodes,self.settings).ProcessFilter()
#                
#                matchedPairs=r9Core.matchNodeLists([self.poseDict[key]['longName'] \
#                                         for key in self.poseDict.keys()], filterData)
#                if matchedPairs:
#                    InternalNodes=filterData
        if not InternalNodes:
            raise StandardError('No Matching Nodes found!!')
        return InternalNodes
  
  
    #Pose Point Cloud (PPC) ------------------------------------  
    
    def _buildOffsetCloud(self,nodes,rootReference=None,raw=False):
        '''
        Build a point cloud up for each node in nodes
        @param nodes: list of objects to be in the cloud
        @param rootReference: the node used for the initial pibot location
        @param raw: build the cloud but DON'T snap the nodes into place - an optimisation for the PoseLoad sequence
        '''
        self.posePointCloudNodes=[]

        self.posePointRoot=cmds.ls(cmds.spaceLocator(name='posePointCloud'),l=True)[0]   
        
        ppcShape=cmds.listRelatives(self.posePointRoot,type='shape')[0] 
        cmds.setAttr( "%s.localScaleZ" % ppcShape, 30)
        cmds.setAttr( "%s.localScaleX" % ppcShape, 30)
        cmds.setAttr( "%s.localScaleY" % ppcShape, 30)
        
        if self.mayaUpAxis=='y':
            cmds.setAttr('%s.rotateOrder' % self.posePointRoot, 2)
        if rootReference:# and not mesh:
            r9Anim.AnimFunctions.snap([rootReference,self.posePointRoot]) 
        for node in nodes:
            pnt=cmds.spaceLocator(name='pp_%s' % r9Core.nodeNameStrip(node))[0]
            if not raw:
                r9Anim.AnimFunctions.snap([node,pnt])
            cmds.parent(pnt,self.posePointRoot)
            self.posePointCloudNodes.append((pnt,node))
        return self.posePointCloudNodes
        
    def _snapPosePntstoNodes(self):
        '''
        snap each pntCloud point to their respective Maya nodes
        '''
        for pnt,node in self.posePointCloudNodes:
            log.debug('snapping PPT : %s' % pnt)
            r9Anim.AnimFunctions.snap([node,pnt])
            
    def _snapNodestoPosePnts(self):
        '''
        snap each MAYA node to it's respective pntCloud point
        '''
        for pnt,node in self.posePointCloudNodes:
            log.debug('snapping Ctrl : %s' % node)
            r9Anim.AnimFunctions.snap([pnt,node])   
    
    
    #Main Calls ----------------------------------------  
  
    @r9General.Timer              
    def PoseSave(self, nodes, filepath, useFilter=True, storeThumbnail=True):
        '''
        Entry point for the generic PoseSave
        @param nodes: nodes to store the data against OR the rootNode if the filter is active
        @param filepath: path to save the posefile too  
        @param useFilter: use the filterSettings or not
        '''   
        log.debug('PosePath given : %s' % filepath)  
        #push args to object - means that any poseHandler.py file has access to them           
        self.filepath=filepath
        self.useFilter=useFilter
        
        self.buildInternalPoseData(nodes)
        self._writePose(filepath)
        
        if storeThumbnail:
            sel=cmds.ls(sl=True,l=True)
            cmds.select(cl=True)
            r9General.thumbNailScreen(filepath,self.thumbnailRes[0],self.thumbnailRes[1])    
            if sel:
                cmds.select(sel)
        log.info('Pose Saved Successfully to : %s' % filepath)
        
        
    @r9General.Timer
    def PoseLoad(self, nodes, filepath, useFilter=True, relativePose=False, relativeRots='projected',relativeTrans='projected'):
        '''
        Entry point for the generic PoseLoad
        @param nodes:  if given load the data to only these. If given and filter=True this is the rootNode for the filter
        @param filepath: path to the posefile to load
        @param useFilter: If the pose has an active Filter_Settings block and this 
                        is True then use the filter on the destination hierarchy
        @param relativePose: kick in the posePointCloud to align the loaded pose relatively to the selected node
        @param relativeRots: 'projected' or 'absolute' - how to calculate the offset
        @param relativeTrans: 'projected' or 'absolute' - how to calculate the offset
        '''
        if not os.path.exists(filepath):
            raise StandardError('Given Path does not Exist')
        if relativePose and not cmds.ls(sl=True):
            raise StandardError('Nothing selected to align Relative Pose too')
        if not type(nodes)==list:nodes=[nodes] #cast to list for consistency
        rootNode=nodes[0]
        
        #push args to object - means that any poseHandler.py file has access to them          
        self.relativePose=relativePose
        self.relativeRots=relativeRots
        self.relativeTrans=relativeTrans
        self.filepath=filepath
        self.useFilter=useFilter
        
        if self.metaPose:
            self.setMetaRig(rootNode)
                
        if self.hasFolderOverload():# and useFilter:
            nodesToLoad=self.getNodesFromFolderConfig(nodes,mode='load')
        else:
            nodesToLoad=self.getNodes(nodes)
        if not nodesToLoad:
            raise StandardError('Nothing selected or returned by the filter to load the pose onto')
           
        self._readPose(filepath)

        if self.metaPose:
            if self.infoDict.has_key('metaPose') and eval(self.infoDict['metaPose']) and self.metaRig:
                self.matchMethod='metaData'
            else:
                log.debug('Warning, trying to load a NON metaPose to a MRig - switching to NameMatching')  
                 
        #Build the master list of matched nodes that we're going to apply data to
        #Note: this is built up from matching keys in the poseDict to the given nodes
        matchedPairs=self._matchNodesToPoseData(nodesToLoad)
        
        if not matchedPairs:
            raise StandardError('No Matching Nodes found in the PoseFile!')    
        else:
            nodesToLoad.reverse() #for the snapping operations
            
            #make the reference posePointCloud and cache it's initial xforms
            if self.relativePose:
                reference=cmds.ls(sl=True,l=True)[0]
                self._buildOffsetCloud(nodesToLoad,reference,raw=True)
                resetCache=[cmds.getAttr('%s.translate' % self.posePointRoot), cmds.getAttr('%s.rotate' % self.posePointRoot)]  
            
            self._applyPose(matchedPairs)
            log.info('Pose Read Successfully from : %s' % filepath)

            if self.relativePose:
                #snap the poseCloud to the new xform of the referenced node, snap the cloud
                #to the pose, reset the clouds parent to the cached xform and then snap the 
                #nodes back to the cloud
                r9Anim.AnimFunctions.snap([reference,self.posePointRoot])
                 
                if self.relativeRots=='projected':
                    if self.mayaUpAxis=='y':
                        cmds.setAttr('%s.rx' % self.posePointRoot,0)
                        cmds.setAttr('%s.rz' % self.posePointRoot,0)
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        cmds.setAttr('%s.rx' % self.posePointRoot,0)
                        cmds.setAttr('%s.ry' % self.posePointRoot,0)
                    
                self._snapPosePntstoNodes()
                
                if not self.relativeTrans=='projected':
                    cmds.setAttr('%s.translate' % self.posePointRoot,resetCache[0][0][0],resetCache[0][0][1],resetCache[0][0][2])
                if not self.relativeRots=='projected':
                    cmds.setAttr('%s.rotate' % self.posePointRoot,resetCache[1][0][0],resetCache[1][0][1],resetCache[1][0][2])
               
                if self.relativeRots=='projected':
                    if self.mayaUpAxis=='y':
                        cmds.setAttr('%s.ry' % self.posePointRoot,resetCache[1][0][1])
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        cmds.setAttr('%s.rz' % self.posePointRoot,resetCache[1][0][2])
                if self.relativeTrans=='projected':
                    if self.mayaUpAxis=='y':
                        cmds.setAttr('%s.tx' % self.posePointRoot,resetCache[0][0][0])
                        cmds.setAttr('%s.tz' % self.posePointRoot,resetCache[0][0][2])
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        cmds.setAttr('%s.tx' % self.posePointRoot,resetCache[0][0][0])    
                        cmds.setAttr('%s.ty' % self.posePointRoot,resetCache[0][0][1])    
                            
                self._snapNodestoPosePnts()  
                cmds.delete(self.posePointRoot)
                cmds.select(reference)



class PosePointCloud(object):
    '''
    PosePointCloud is the technique inside the PoseSaver used to snap the pose into 
    relative space. It's been added as a tool in it's own right as it's sometimes
    useful to be able to shift poses in global space.
    '''
    def __init__(self,rootReference,nodes,filterSettings=None,mesh=None):
        '''
        @param rootReference: the object to be used as the PPT's pivot reference
        @param nodes: feed the nodes to process in as a list, if a filter is given 
                      then these are the rootNodes for it
        @param filterSettings: pass in a filterSettings object to filter the given hierarchy
        @param mesh: this is really for reference, rather than make a locator, pass in a reference geo
                     which is then shapeSwapped for the PPC root node giving great reference!
        '''
        self.poseObject=PoseData() 
        self.mesh=mesh
        self.refMesh='posePointCloudGeoRef'
        self.refMeshShape='posePointCloudGeoRefShape'
        
        if filterSettings:
            if not issubclass(type(filterSettings), r9Core.FilterNode_Settings):
                raise StandardError('filterSettings param requires an r9Core.FilterNode_Settings object')
            elif filterSettings.filterIsActive():
                self.poseObject.settings=filterSettings
                nodes=r9Core.FilterNode(nodes,self.poseObject.settings).ProcessFilter()
        if nodes:
            nodes.reverse() #for the snapping operations
            self.poseObject._buildOffsetCloud(nodes, rootReference=rootReference)
        if mesh:
            self.shapeSwapMesh()
        cmds.select(self.poseObject.posePointRoot)
    
    def shapeSwapMesh(self):
        '''
        Swap the mesh Geo so it's a shape under the PPC transform root
        TODO: Make sure that the duplicate message link bug is covered!!
        '''
        cmds.duplicate(self.mesh,rc=True,n=self.refMesh)[0]
        r9Core.LockChannels().processState(self.refMesh,['tx','ty','tz','rx','ry','rz','sx','sy','sz'],\
                                           mode='fullkey',hierarchy=False)                                      
        cmds.parent(self.refMesh,self.poseObject.posePointRoot)
        cmds.makeIdentity(self.refMesh,apply=True,t=True,r=True)
        cmds.parent(self.refMeshShape,self.poseObject.posePointRoot,r=True,s=True)
        cmds.delete(self.refMesh)

    def applyPosePointCloud(self):
        self.poseObject._snapNodestoPosePnts()
        
    def snapPosePointsToPose(self):
        self.poseObject._snapPosePntstoNodes()
        if self.mesh:
            cmds.delete(self.refMeshShape)
            self.shapeSwapMesh()
            cmds.refresh()
        
    def delete(self):
        cmds.delete(self.poseObject.posePointRoot)
        

class PoseCompare(object):
    '''
    This is aimed at comparing the current pose with a given one, be that a 
    pose file on disc, a pose class object. It will compare the main [poseData].keys 
    and for key in keys compare, with tolerance, the [attrs] block. With tolerance
    so it handles float data correctly.
    
    #build an mPose object and fill the internal poseDict
    mPoseA=r9Pose.PoseData()
    mPoseA.metaPose=True
    mPoseA.buildInternalPoseData(cmds.ls(sl=True))
    
    mPoseB=r9Pose.PoseData()
    mPoseB.metaPose=True
    mPoseB.buildInternalPoseData(cmds.ls(sl=True))
    
    compare=r9Pose.PoseCompare(mPoseA,mPoseB)
    
    .... or .... 
    compare=r9Pose.PoseCompare(mPoseA,'H:/Red9PoseTests/thisPose.pose')
    .... or ....
    compare=r9Pose.PoseCompare('H:/Red9PoseTests/thisPose.pose','H:/Red9PoseTests/thatPose.pose')
        
    compare.compare() #>> bool, True = same
    compare.fails['failedAttrs']
    '''
    def __init__(self, currentPose, referencePose, angularTolerance=0.01, linearTolerance=0.01, compareDict='poseDict'):
        '''
        make sure we have 2 PoseData objects to compare
        @param currentPose: either a PoseData object or a valid pose file
        @param referencePose: either a PoseData object or a valid pose file
        @param tolerance: tolerance by which floats are matched
        @param angularTolerance: the tolerance used to check rotate attr float values
        @param linearTolerance: the tolerance used to check all other float attrs
        @param compareDict: the internal main dict in the pose file to compare the data with
                    NOTE in the new setup if the skeletonRoot jnt is found we add a whole 
                    new dict to serialize the current skeleton data to the pose, this means that
                    we can compare a pose on a rig via the internal skeleton transforms as well
                    as the actual rig controllers...makes validation a lot more accurate for export
        '''
        self.compareDict=compareDict
        self.angularTolerance=angularTolerance
        self.angularAttrs=['rotateX','rotateY','rotateZ']
        
        self.linearTolerance=linearTolerance
        self.linearAttrs=['translateX','translateY','translateZ']
        
        if isinstance(currentPose,PoseData):
            self.currentPose=currentPose
        elif os.path.exists(currentPose):
            self.currentPose=PoseData()
            self.currentPose._readPose(currentPose)
            
        if isinstance(referencePose,PoseData):    
            self.referencePose=referencePose
        elif os.path.exists(referencePose):
            self.referencePose=PoseData()
            self.referencePose._readPose(referencePose)

    def __addFailedAttr(self,key,attr):
        '''
        add failed attrs data to the dict
        '''
        if not self.fails.has_key('failedAttrs'):
            self.fails['failedAttrs']={}
        if not self.fails['failedAttrs'].has_key(key):
            self.fails['failedAttrs'][key]={}
        if not self.fails['failedAttrs'][key].has_key('attrMismatch'):
            self.fails['failedAttrs'][key]['attrMismatch']=[]
        self.fails['failedAttrs'][key]['attrMismatch'].append(attr)
       
    def compare(self):
        '''
        Compare the 2 PoseData objects via their internal [key][attrs] blocks
        return a bool. After processing self.fails is a dict holding all the fails
        for processing later if required
        '''
        self.fails={}
        logprint='PoseCompare returns : ========================================\n'
        currentDic = getattr(self.currentPose, self.compareDict) 
        referenceDic=getattr(self.referencePose, self.compareDict) 
        
        if not currentDic or not referenceDic:
            raise StandardError('missing pose section <<%s>> compare aborted' % self.compareDict)
        
        for key, attrBlock in currentDic.items():
            if referenceDic.has_key(key):
                referenceAttrBlock=referenceDic[key]
            else:
                #log.info('Key Mismatch : %s' % key)
                logprint+='ERROR: Key Mismatch : %s\n' % key
                if not self.fails.has_key('missingKeys'):
                    self.fails['missingKeys']=[]
                self.fails['missingKeys'].append(key)
                continue

            for attr, value in attrBlock['attrs'].items():
                #attr missing completely from the key
                if not referenceAttrBlock['attrs'].has_key(attr):
                    if not self.fails.has_key('failedAttrs'):
                        self.fails['failedAttrs']={}
                    if not self.fails['failedAttrs'].has_key(key):
                        self.fails['failedAttrs'][key]={}
                    if not self.fails['failedAttrs'][key].has_key('missingAttrs'):
                        self.fails['failedAttrs'][key]['missingAttrs']=[]
                    self.fails['failedAttrs'][key]['missingAttrs'].append(attr)
                    #log.info('missing attribute in data : "%s.%s"' % (key,attr))
                    logprint+='ERROR: Missing attribute in data : "%s.%s"\n' % (key,attr)
                    continue
                
                #test the attrs value matches
                value=r9Core.decodeString(value)                                 #decode as this may be a configObj
                refValue=r9Core.decodeString(referenceAttrBlock['attrs'][attr])  #decode as this may be a configObj
                
                if type(value)==float:
                    matched=False
                    if attr in self.angularAttrs:
                        matched=r9Core.floatIsEqual(value, refValue, self.angularTolerance, allowGimbal=True)
                    else:
                        matched=r9Core.floatIsEqual(value, refValue, self.linearTolerance, allowGimbal=False)
                    if not matched:
                        self.__addFailedAttr(key, attr)
                        #log.info('AttrValue float mismatch : "%s.%s" currentValue=%s >> expectedValue=%s' % (key,attr,value,refValue))
                        logprint+='ERROR: AttrValue float mismatch : "%s.%s" currentValue=%s >> expectedValue=%s\n' % (key,attr,value,refValue)
                        continue    
                elif not value==refValue:
                    self.__addFailedAttr(key, attr)
                    #log.info('AttrValue mismatch : "%s.%s" currentValue=%s >> expectedValue=%s' % (key,attr,value,refValue))
                    logprint+='ERROR: AttrValue mismatch : "%s.%s" currentValue=%s >> expectedValue=%s\n' % (key,attr,value,refValue)
                    continue                 
                
        if self.fails.has_key('missingKeys') or self.fails.has_key('failedAttrs'):
            logprint+='PoseCompare returns : ========================================'
            print logprint
            return False
        return True

         

def batchPatchPoses(posedir, config, poseroot, load=True, save=True, patchfunc=None,\
                    relativePose=False, relativeRots=False, relativeTrans=False):
    '''
    whats this?? a fast method to run through all the poses in a given dictionary and update
    or patch them. If patchfunc isn't given it'll just run through and resave the pose - updating 
    the systems if needed. If it is then it gets run between the load and save calls.
    @param posedir: directory of poses to process
    @param config: hierarchy settings cfg to use to ID the nodes (hierarchy tab preset = filterSettings object)
    @param poseroot: root node to the filters - poseTab rootNode/MetaRig root
    @param patchfunc: optional function to run between the load and save call in processing, great for
            fixing issues on mass with poses. Note we now pass pose file back into this func as an arg
    @param load: should the batch load the pose
    @param save: should the batch resave the pose
    '''

    filterObj=r9Core.FilterNode_Settings()
    filterObj.read(os.path.join(r9Setup.red9ModulePath(), 'presets', config))#'Crytek_New_Meta.cfg'))
    mPose=PoseData(filterObj)
    
    files=os.listdir(posedir)
    files.sort()
    for f in files:
        if f.lower().endswith('.pose'):
            if load:
                mPose.PoseLoad(poseroot, os.path.join(posedir,f), useFilter=True, relativePose=relativePose, relativeRots=relativeRots, relativeTrans=relativeTrans) 
            if patchfunc:
                patchfunc(f)
            if save:
                mPose.PoseSave(poseroot, os.path.join(posedir,f), useFilter=True, storeThumbnail=False) 
            log.info('Processed Pose File :  %s' % f)

        
        
        
