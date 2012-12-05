'''
------------------------------------------
Red9 Studio Pack : Maya Pipeline Solutions
email: rednineinfo@gmail.com
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

import maya.cmds as cmds
import os
import Red9.packages.configobj as configobj
import time
import getpass

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
    
    Then we use the shortName key as a lookup for the destination hierarchy
    do a matchNodes on it and if found match the attrs and apply
    
    Pose=r9Core.PoseData(NoodesToStore)
    Pose.BuildPoseDict()
    Pose.writePose('C://Pose.pose')
    
    Pose=r9Core.PoseData()
    Pose.readPose('C://Pose.pose')
    Pose.applyPose(NodeToLoadData)
    '''
    
    def __init__(self, filterSettings=None):
        '''
        I'm not passing any data in terms of nodes here, We'll deal with
        those in the PoseSave and PoseLoad calls. Leaves this open for
        expansion
        '''
        self.poseDict={}
        self.infoDict={}
        self.posePointCloudNodes=[]
        self.mayaUpAxis=r9Setup.mayaUpAxis()
        self.thumbnailRes=[128,128]
           
        # make sure we have a settings object
        if filterSettings:
            if issubclass(type(filterSettings), r9Core.FilterNode_Settings):
                self.settings=filterSettings
            else:
                raise StandardError('filterSettings param requires an r9Core.FilterNode_Settings object')
        else:
            self.settings=r9Core.FilterNode_Settings()
        self.settings.printSettings()
    
    # Build the poseDict data ---------------------------------------------
    
    def __getNodeMetaDataMap(self, node, mTypes=[]):
        '''
        This is a generic wrapper to extract metaData connection info for any given node
        used to build the pose dict up, and compare / match the data on load 
        '''
        import Red9.core.Red9_Meta as r9Meta
        mNodes={}
        connections=cmds.listConnections(node,type='network',s=True,d=False,c=True)
        if not connections:
            return connections
        for attr,node in zip(connections[::2],connections[1::2]):
            if r9Meta.isMetaNode(node,mTypes=mTypes):
                attrData=attr.split('.')
                mNodes['metaAttr']=attrData[1]
                mNodes['metaNode']=node
                #mNodes['metaSide']=cmds.getAttr('%s.mirrorSide' % node)
                #mNodes['metaSystem']=cmds.getAttr('%s.systemType' % node)
        return mNodes          

    def __buildInfoBlock(self):
        '''
        TODO: if MetaRig push some of the hard coded attrs to the info block
        ie, characterType, version etc
        '''
        self.infoDict['author']=getpass.getuser()
        self.infoDict['date']=time.ctime()
        
    def __buildPoseDict(self, nodes):  
        '''
        Build the internal poseDict up from the given nodes. This is the 
        core of the Pose System 
        '''   
        for i,node in enumerate(nodes):
            key=r9Core.nodeNameStrip(node)
            self.poseDict[key]={}
            self.poseDict[key]['ID']=i          #selection order index
            self.poseDict[key]['longName']=node #longNode name
            #self.poseDict[key]['mirrorIndex']=??
            
            if self.settings.metaRig:
                self.poseDict[key]['metaData']=self.__getNodeMetaDataMap(node)   #metaSystem the node is wired too

            channels=r9Anim.getSettableChannels(node,incStatics=True)
            if channels:
                self.poseDict[key]['attrs']={}
                for attr in channels:
                    try:
                        self.poseDict[key]['attrs'][attr]=cmds.getAttr('%s.%s' % (node,attr))
                    except:
                        log.debug('%s : attr is invalid in this instance' % attr)


#Nice dict and nice idea, but slower to search and less flexible                        
#    def __buildPoseMetaDict(self, nodes):  
#        '''
#        Build the internal poseDict up from the given nodes. This is the 
#        core of the Pose System 
#        '''   
#        import Red9.core.Red9_Meta as r9Meta
#        mRig=r9Meta.MetaClass(nodes)
#        childMetaNodes=[mRig]
#        childMetaNodes.extend([node for node in mRig.getChildMetaNodes(walk=True)])
#        for mNode in childMetaNodes:
#            log.debug('MetaNode : %s' % mNode.mNode)
#            ctrlAttrs=cmds.listAttr(mNode.mNode,ud=True,st='%s_*' % mRig.CTRL_Prefix)
#            
#            if ctrlAttrs:
#                systemKey=r9Core.nodeNameStrip(mNode.mNode)
#                self.poseDict[systemKey]={} #metaSubsystem level
#    
#                for attrWire in ctrlAttrs:
#                    control=mNode.__getattribute__(attrWire) 
#                    if not control:
#                        log.warning('%s is unlinked and invalid' % attrWire)
#                    else:
#                        node=control[0]
#                        self.poseDict[systemKey][attrWire]={}
#                        self.poseDict[systemKey][attrWire]['longName']=node
#                        self.poseDict[systemKey][attrWire]['shortName']=r9Core.nodeNameStrip(node)
#                        channels=r9Anim.getSettableChannels(node,incStatics=True) 
#                        if channels:
#                            self.poseDict[systemKey][attrWire]['attrs']={}
#                            for attr in channels:
#                                try:
#                                    self.poseDict[systemKey][attrWire]['attrs'][attr]=cmds.getAttr('%s.%s' % (node,attr))
#                                except:
#                                    log.debug('%s : attr is invalid in this instance' % attr)
                        
                        
    # Process the data -------------------------------------------------
                                              
    def writePose(self, filepath):
        '''
        config = ConfigParser.RawConfigParser()
        config.optionxform=str #prevent options being converted to lowerCase
        config.add_section('PoseData')
        for key, val in self.poseDict.items():
            config.set('PoseData',key, val)
    
        # Writing our configuration file to 'example.cfg'
        with open(filepath, 'wb') as configfile:
            config.write(configfile)
        '''
        ConfigObj = configobj.ConfigObj(indent_type='\t')
        ConfigObj['filterNode_settings']=self.settings.__dict__
        ConfigObj['poseData']=self.poseDict
        ConfigObj['info']=self.infoDict
        ConfigObj.filename = filepath
        ConfigObj.write()

    def readPose(self, filename):
        '''
        Read the pose file and build up the internal poseDict
        TODO: do we allow the data to be filled from the pose filter thats stored???????
        '''
        if filename:
            if os.path.exists(filename):            
                #for key, val in configobj.ConfigObj(filename)['filterNode_settings'].items():
                #    self.settings.__dict__[key]=decodeString(val)
                self.poseDict=configobj.ConfigObj(filename)['poseData']
            else:
                raise StandardError('Given filepath doesnt not exist : %s' % filename)
        else:
            raise StandardError('No FilePath given to read the pose from')
    
    def matchNodesToPoseData(self, nodes, matchMethod='name'):
        '''
        Main filter to extract matching data pairs prior to processing
        return : tuple such that :  (poseDict[key], destinationNode)
        @param nodes: nodes to try and match from the poseDict
        @param matchMethod: how to match the nodes to the poseDict data
        '''
        matchedPairs=[]
        if matchMethod=='name':
            matchedPairs=r9Core.matchNodeLists([key for key in self.poseDict.keys()], nodes)
        if matchMethod=='index':
            for i, node in enumerate(nodes):
                for key in self.poseDict.keys():
                    if int(self.poseDict[key]['ID'])==i:
                        matchedPairs.append((key,node))
                        print 'poseKey : %s ' % key, self.poseDict[key]['ID'], 'matchedSource : %s' % node, i
                        break 
        if matchMethod=='metaData':
            for node in nodes:
                metaDict=self.__getNodeMetaDataMap(node)
                for key in self.poseDict.keys():
                    if self.poseDict[key]['metaData']==metaDict:
                        matchedPairs.append((key,node))
            
        return matchedPairs   
        
    def applyPose(self, matchedPairs):
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

                         
    def matchInternalPoseObjects(self, nodes=None, fromFilter=True):
        '''
        from a given poseFile return or select the internal stored objects 
        This is a throw-away and only used in the UI to select for debugging!
        '''
        InternalNodes=[]
        if not fromFilter:
            #no filter, we just pass in the longName thats stored
            for key in self.poseDict.keys():
                if cmds.objExists(self.poseDict[key]['longName']):
                    InternalNodes.append(self.poseDict[key]['longName'])
        else:
            #use the internal Poses filter and then Match against scene nodes
            if self.settings.filterIsActive():
                filterData=r9Core.FilterNode(nodes,self.settings).ProcessFilter()
                
                matchedPairs=r9Core.matchNodeLists([self.poseDict[key]['longName'] \
                                         for key in self.poseDict.keys()], filterData)
                if matchedPairs:
                    InternalNodes=filterData
        if not InternalNodes:
            raise StandardError('No Matching Nodes found!!')
        return InternalNodes
  
  
    #PosePoint Cloud ------------------------------------  
    
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
               
    def PoseSave(self, nodes, filepath, useFilter=True):
        '''
        Entry point for the generic PoseSave
        @param nodes: nodes to store the data against
        @param filepath: path to save the posefile too  
        '''   
        log.debug('PosePath given : %s' % filepath)             
        nodesToStore=nodes
        if self.settings.filterIsActive() and useFilter:
            log.info('Filter is Active')
        #if not self.settings.metaRig:
            nodesToStore=r9Core.FilterNode(nodes,self.settings).ProcessFilter()
            
        self.__buildPoseDict(nodesToStore)
        #else:
        #    self.__buildPoseMetaDict(nodes)
                
        self.__buildInfoBlock()
        self.writePose(filepath)
        sel=cmds.ls(sl=True,l=True)
        cmds.select(cl=True)
        r9General.thumbNailScreen(filepath,self.thumbnailRes[0],self.thumbnailRes[1])
        if sel:
            cmds.select(sel)
        log.info('Pose Saved Successfully to : %s' % filepath)
        

    def PoseLoad(self, nodes, filepath, useFilter=True, matchMethod='name', \
                 relativePose=False, relativeRots='projected',relativeTrans='projected'):
        '''
        Entry point for the generic PoseLoad
        @param nodes:  if given load the data to only these. If given and filter=True this is the root of the filter
        @param filepath: path to the posefile to load
        @param useFilter: If the pose has an active Filter_Settings block and this 
                        is True then use the filter on the destination hierarchy
        @param relativePose: kick in the posePointCloud to align the loaded pose relatively to the selected node
        @param relativeRots: 'projected' or 'absolute' - how to calculate the offset
        @param relativeTrans: 'projected' or 'absolute' - how to calculate the offset
        '''
        nodesToLoad=nodes
        if not os.path.exists(filepath):
            raise StandardError('Given Path does not Exist')
        if relativePose and not cmds.ls(sl=True):
            raise StandardError('Nothing selected to align Relative Pose too')
        if self.settings.filterIsActive() and useFilter:
            nodesToLoad=r9Core.FilterNode(nodes,self.settings).ProcessFilter()
        if not nodesToLoad:
            raise StandardError('Nothing selected or returned by the filter to load the pose onto')
           
        self.readPose(filepath)
                
        #Build the master list of matched nodes that we're going to apply data to
        #Note: this is built up from matching keys in the poseDict to the given nodes
        if self.settings.metaRig:
            matchMethod='metaData'
        matchedPairs=self.matchNodesToPoseData(nodesToLoad,matchMethod=matchMethod)
        
        if not matchedPairs:
            raise StandardError('No Matching Nodes found in the PoseFile!')    
        else:
            nodesToLoad.reverse() #for the snapping operations
            
            #make the reference posePointCloud and cache it's initial xforms
            if relativePose:
                reference=cmds.ls(sl=True,l=True)[0]
                self._buildOffsetCloud(nodesToLoad,reference,raw=True)
                resetCache=[cmds.getAttr('%s.translate' % self.posePointRoot), cmds.getAttr('%s.rotate' % self.posePointRoot)]  
            
            self.applyPose(matchedPairs)
            log.info('Pose Read Successfully from : %s' % filepath)

            if relativePose:
                #snap the poseCloud to the new xform of the referenced node, snap the cloud
                #to the pose, reset the clouds parent to the cached xform and then snap the 
                #nodes back to the cloud
                r9Anim.AnimFunctions.snap([reference,self.posePointRoot])
                 
                if relativeRots=='projected':
                    if self.mayaUpAxis=='y':
                        cmds.setAttr('%s.rx' % self.posePointRoot,0)
                        cmds.setAttr('%s.rz' % self.posePointRoot,0)
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        cmds.setAttr('%s.rx' % self.posePointRoot,0)
                        cmds.setAttr('%s.ry' % self.posePointRoot,0)
                    
                self._snapPosePntstoNodes()
                
                if not relativeTrans=='projected':
                    cmds.setAttr('%s.translate' % self.posePointRoot,resetCache[0][0][0],resetCache[0][0][1],resetCache[0][0][2])
                if not relativeRots=='projected':
                    cmds.setAttr('%s.rotate' % self.posePointRoot,resetCache[1][0][0],resetCache[1][0][1],resetCache[1][0][2])
               
                if relativeRots=='projected':
                    if self.mayaUpAxis=='y':
                        cmds.setAttr('%s.ry' % self.posePointRoot,resetCache[1][0][1])
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        cmds.setAttr('%s.rz' % self.posePointRoot,resetCache[1][0][2])
                if relativeTrans=='projected':
                    if self.mayaUpAxis=='y':
                        cmds.setAttr('%s.tx' % self.posePointRoot,resetCache[0][0][0])
                        cmds.setAttr('%s.tz' % self.posePointRoot,resetCache[0][0][2])
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        cmds.setAttr('%s.tx' % self.posePointRoot,resetCache[0][0][0])    
                        cmds.setAttr('%s.ty' % self.posePointRoot,resetCache[0][0][1])    
                            
                self._snapNodestoPosePnts()  
                cmds.delete(self.posePointRoot)
                cmds.select(reference)
            #loaded=cmds.spaceLocator()[0]
            #cmds.SnapTransforms(source=sourceNode, destination=loaded)
            #Matrix=MatrixOffset()
            #Matrix.setOffsetMatrix(originalRef,loaded)        
            #Matrix.ApplyOffsetMatrixToNodes(nodesToLoad)


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
        
        
