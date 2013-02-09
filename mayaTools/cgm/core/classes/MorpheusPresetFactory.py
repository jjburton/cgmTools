"""
------------------------------------------
GuiFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class based ui builder for cgmTools
================================================================
"""
DIR_SEPARATOR = '/' 

#>>> From Standard =============================================================
import os
import getpass
import time

#>>> From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
import copy
    
#>>> From cgm ==============================================================
import morpheusRig_v2.assets.baseMesh as mBaseMeshFolder

from cgm.core.classes import GuiFactory as gui
reload(gui)
from cgm.lib.classes import NameFactory as nFactory
from cgm.core.classes import ControlFactory as ctrlFactory
reload(ctrlFactory)

from cgm.core import cgm_Meta as cgmMeta

from cgm.lib import (search,
                     attributes,
                     guiFactory,
                     deformers,
                     dictionary)

#>>> From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General
from Red9.core import Red9_AnimationUtils as r9Anim
from Red9.core import Red9_CoreUtils as r9Core
from Red9.core import Red9_PoseSaver as r9Pose
import Red9.packages.configobj as configobj

#>>>======================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

class go(r9Pose.PoseData):
        
    def _buildPoseDict(self, nodes):  
        '''
        Overload for storing blendshape attrs
        '''   
        self.thumbnailRes=[230,230]
        
        for i,node in enumerate(nodes):
            key=r9Core.nodeNameStrip(node)
            self.poseDict[key]={}
            self.poseDict[key]['ID']=i          #selection order index
            self.poseDict[key]['longName']=node #longNode name
            
            if self.metaPose:
                self.poseDict[key]['metaData']=getMetaDict(node)   #metaSystem the node is wired too  
            
            if search.returnObjectType(node) == 'blendShape' and '.' not in node:
                channels=r9Anim.getSettableChannels(node,incStatics=True)
                channels.extend(deformers.returnBlendShapeAttributes(node))
            else:
                channels=r9Anim.getSettableChannels(node,incStatics=True)
                
                
            if channels:
                self.poseDict[key]['attrs']={}
                for attr in channels:
                    try:
                        self.poseDict[key]['attrs'][attr]=mc.getAttr('%s.%s' % (node,attr))
                    except:
                        log.debug('%s : attr is invalid in this instance' % attr)
        
     
        
        if self.poseDict:
            for node in self.poseDict.keys():
                log.info('%s: %s'%(str(node),str(self.poseDict.get(node))))
                if type(node) is dict:
                    for d_node in node.keys():
                        log.info('%s: %s'%(str(d_node),str(node.get(d_node))))
                        
    def PoseLoad(self, nodes, filepath, useFilter=True, matchMethod='fullName',
                 relativePose=False, relativeRots='projected',relativeTrans='projected'):
        """
        To Do. Overload this to verify mesh version, active mesh, check blendshapes, etc
        """        
        r9Pose.PoseData.PoseLoad(self, nodes = nodes, filepath = filepath, useFilter=useFilter, matchMethod=matchMethod,
                 relativePose=relativePose, relativeRots=relativeRots,relativeTrans=relativeTrans)

    def _matchNodesToPoseData(self, nodes, matchMethod='name'):
        """
        Overload for a new match method
        """
        if matchMethod == 'fullName':
            log.warning("In _matchNodesToPoseData OVERLOAD")                    
            matchedPairs=[]
            cleanList = []
            for node in nodes:
                cleanList.append(r9Core.nodeNameStrip(node))
            for key in self.poseDict.keys():
                if key in cleanList:
                    i = cleanList.index(key)
                    matchedPairs.append((key,cleanList[i]))  
                    log.debug("%s:%s"%(key,cleanList[i]))                      
                """
                for i,node in enumerate(cleanList):
                    if key == node:
                        matchedPairs.append((key,cleanList[i]))
                        log.debug("%s:%s"%(key,cleanList[i]))  
                """
            return matchedPairs
        else:
            return r9Pose.PoseData._matchNodesToPoseData(self, nodes = nodes, matchMethod = matchMethod)
                    
        return matchedPairs   
    def _buildInfoBlock(self):
        """
        Basic info for the pose file, this could do with expanding
        """
        self.infoDict['author']=getpass.getuser()
        self.infoDict['date']=time.ctime()
        self.infoDict['metaPose']=self.metaPose
        if self.metaRig:
            self.infoDict['metaRigNode']  =self.metaRig.mNode
            self.infoDict['metaRigNodeID']=self.metaRig.mNodeID
        if self.rootJnt:
            self.infoDict['skeletonRootJnt']=self.rootJnt    
        
        #self.howdy =  "howdy all"    
        self.infoDict['testData'] = "howdy all"

class go2(object):
    """
    
    """
    def __init__(self,customizationNode = False):
        """
        Necessary info:
        1) Customization Node
        2) Gather pose info
        3) Store pose info to pickle
        4) read pose info
        5) apply pose info

        """
        #self.mayaUpAxis=r9Setup.mayaUpAxis()
        #self._customPreset=False
        
        self.customizationNode = customizationNode
        self.d_info = {}
        self.d_pose = {}
        self.d_blendshapeNodes = {}
        self.thumbnailRes=[128,128]
    
    """
    #Property so we sync the settings metaRig bool to the class customPreset bool
    def __get_customPreset(self):
        return self._customPreset
    
    def __set_customPreset(self, val):
        self._customPreset=val
                
    customPreset = property(__get_customPreset, __set_customPreset)
    
    def setCustomizationNode(self,node = False):
        if r9Meta.isMetaNodeInherited(nodes[0],'MetaRig'):
            self.metaRig=r9Meta.MetaClass(nodes[0])
        else:
            self.metaRig=r9Meta.getConnectedMetaSystemRoot(nodes)
        return self.metaRig
    """
    #==============================================================================                   
    # Gather info
    #==============================================================================
    def _buildInfoBlock(self):
        '''
        Basic info for the pose file, this could do with expanding
        '''
        self.d_info['author']=getpass.getuser()
        self.d_info['date']=time.ctime()
        
        return self.d_info
        
    def _buildPoseDict(self, nodes):  
        '''
        Build the internal poseDict up from the given nodes. This is the 
        core of the Pose System 
        '''   
        for i,node in enumerate(nodes):
            key=r9Core.nodeNameStrip(node)
            self.d_pose[key]={}
            self.d_pose[key]['ID']=i          #selection order index
            self.d_pose[key]['longName']=node #longNode name
            
            log.info(search.returnObjectType(node))
            if search.returnObjectType(node) == 'blendShape':
                channels=r9Anim.getSettableChannels(node,incStatics=True)
                channels.extend(deformers.returnBlendShapeAttributes(node))
            else:
                channels=r9Anim.getSettableChannels(node,incStatics=True)
            
            if channels:
                self.d_pose[key]['attrs']={}
                for attr in channels:
                    try:
                        self.d_pose[key]['attrs'][attr]=mc.getAttr('%s.%s' % (node,attr))
                    except:
                        log.debug('%s : attr is invalid in this instance' % attr)
        
        if self.d_pose:
            for node in self.d_pose.keys():
                log.info('%s: %s'%(str(node),str(self.d_pose.get(node))))
                if type(node) is dict:
                    for d_node in node.keys():
                        log.info('%s: %s'%(str(d_node),str(node.get(d_node))))
                        
    def buildInternalPoseData(self, nodes, useFilter=True):
        '''
        build the internal pose dict's, useful as a separate func so it
        can be used in the PoseCompare class easily. This is the main internal call
        for managing the actual pose data for save
        '''
        nodesToStore=nodes
        
        self._buildInfoBlock()    
        self._buildPoseDict(nodesToStore) 
    #==============================================================================                   
    # Write Data
    #==============================================================================
    def _writePose(self, filepath):
        '''
        Write the Pose ConfigObj to file
        '''
        ConfigObj = configobj.ConfigObj(indent_type='\t')
        #ConfigObj['filterNode_settings']=self.settings.__dict__
        ConfigObj['poseData']=self.d_pose
        ConfigObj['info']=self.d_info

        ConfigObj.filename = filepath
        ConfigObj.write()

    #Main Calls ----------------------------------------  
  
    @r9General.Timer              
    def PoseSave(self, nodes, filepath, useFilter=True):
        '''
        Entry point for the generic PoseSave
        @param nodes: nodes to store the data against OR the rootNode if the filter is active
        @param filepath: path to save the posefile too  
        @param useFilter: use the filterSettings or not
        '''   
        log.debug('PosePath given : %s' % filepath)             

        self.buildInternalPoseData(nodes, useFilter)
        self._writePose(filepath)
        
        sel=mc.ls(sl=True,l=True)
        mc.select(cl=True)
        #r9General.thumbNailScreen(filepath,self.thumbnailRes[0],self.thumbnailRes[1])
        
        if sel:
            mc.select(sel)
        log.info('Pose Saved Successfully to : %s' % filepath)

class Reference():
    def __init__():
        pass
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
                    self.skeletonDict[key]['attrs'][attr]=mc.getAttr('%s.%s' % (jnt,attr))
                except:
                    log.debug('%s : attr is invalid in this instance' % attr)

    def buildInternalPoseData(self, nodes, useFilter=True):
        '''
        build the internal pose dict's, useful as a separate func so it
        can be used in the PoseCompare class easily. This is the main internal call
        for managing the actual pose data for save
        '''
        nodesToStore=nodes
        self.metaRig=None
        self.rootJnt=None
        
        if self.settings.filterIsActive() and useFilter:
            nodesToStore=r9Core.FilterNode(nodes,self.settings).ProcessFilter() #main node filter
            
            if not type(nodes)==list: nodes=[nodes]
            if self.customPreset:
                if self.setCustomizationNode(nodes):
                    self.rootJnt=self.metaRig.getSkeletonRoot()
            else:
                if mc.attributeQuery('animSkeletonRoot',node=nodes[0],exists=True):
                    self.rootJnt=mc.listConnections('%s.%s' % (nodes[0],'animSkeletonRoot'),destination=True,source=True)[0]
                     
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
        ConfigObj['poseData']=self.d_pose
        ConfigObj['info']=self.d_info
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
                self.d_pose=configobj.ConfigObj(filename)['poseData']
                if configobj.ConfigObj(filename).has_key('info'):
                    self.d_info=configobj.ConfigObj(filename)['info']
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
                for attr, val in self.d_pose[key]['attrs'].items():
                    try:
                        val=eval(val)
                    except:
                        pass
                    log.debug('node : %s : attr : %s : val %s' % (dest,attr,val))
                    try:
                        mc.setAttr('%s.%s' % (dest, attr), val)
                    except StandardError,err:
                        log.debug(err)
            except:
                log.debug('Pose Object Key : %s : has no Attr block data' % key)  

                         
    def matchInternalPoseObjects(self, nodes=None, fromFilter=True):
        '''
        This is a throw-away and only used in the UI to select for debugging!
        from a given poseFile return or select the internal stored objects 
        '''
        InternalNodes=[]
        if not fromFilter:
            #no filter, we just pass in the longName thats stored
            for key in self.d_pose.keys():
                if mc.objExists(self.d_pose[key]['longName']):
                    InternalNodes.append(self.d_pose[key]['longName'])
        else:
            #use the internal Poses filter and then Match against scene nodes
            if self.settings.filterIsActive():
                filterData=r9Core.FilterNode(nodes,self.settings).ProcessFilter()
                
                matchedPairs=r9Core.matchNodeLists([self.d_pose[key]['longName'] \
                                         for key in self.d_pose.keys()], filterData)
                if matchedPairs:
                    InternalNodes=filterData
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

        self.posePointRoot=mc.ls(mc.spaceLocator(name='posePointCloud'),l=True)[0]   
        
        ppcShape=mc.listRelatives(self.posePointRoot,type='shape')[0] 
        mc.setAttr( "%s.localScaleZ" % ppcShape, 30)
        mc.setAttr( "%s.localScaleX" % ppcShape, 30)
        mc.setAttr( "%s.localScaleY" % ppcShape, 30)
        
        if self.mayaUpAxis=='y':
            mc.setAttr('%s.rotateOrder' % self.posePointRoot, 2)
        if rootReference:# and not mesh:
            r9Anim.AnimFunctions.snap([rootReference,self.posePointRoot]) 
        for node in nodes:
            pnt=mc.spaceLocator(name='pp_%s' % r9Core.nodeNameStrip(node))[0]
            if not raw:
                r9Anim.AnimFunctions.snap([node,pnt])
            mc.parent(pnt,self.posePointRoot)
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
    def PoseSave(self, nodes, filepath, useFilter=True):
        '''
        Entry point for the generic PoseSave
        @param nodes: nodes to store the data against OR the rootNode if the filter is active
        @param filepath: path to save the posefile too  
        @param useFilter: use the filterSettings or not
        '''   
        log.debug('PosePath given : %s' % filepath)             

        self.buildInternalPoseData(nodes, useFilter)
        self._writePose(filepath)
        
        sel=mc.ls(sl=True,l=True)
        mc.select(cl=True)
        r9General.thumbNailScreen(filepath,self.thumbnailRes[0],self.thumbnailRes[1])
        
        if sel:
            mc.select(sel)
        log.info('Pose Saved Successfully to : %s' % filepath)
        
        
    @r9General.Timer
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
        if not type(nodes)==list:nodes=[nodes]
        
        nodesToLoad=nodes
        if not os.path.exists(filepath):
            raise StandardError('Given Path does not Exist')
        if relativePose and not mc.ls(sl=True):
            raise StandardError('Nothing selected to align Relative Pose too')
        if self.settings.filterIsActive() and useFilter:
            nodesToLoad=r9Core.FilterNode(nodes,self.settings).ProcessFilter()
        if not nodesToLoad:
            raise StandardError('Nothing selected or returned by the filter to load the pose onto')
           
        self._readPose(filepath)

        if self.customPreset:
            if self.d_info.has_key('customPreset') and eval(self.d_info['customPreset']) and self.setCustomizationNode(nodes):
                matchMethod='metaData'
            else:
                log.debug('Warning, trying to load a NON customPreset to a MRig - switching to NameMatching')  
                 
        #Build the master list of matched nodes that we're going to apply data to
        #Note: this is built up from matching keys in the poseDict to the given nodes
        matchedPairs=self._matchNodesToPoseData(nodesToLoad,matchMethod=matchMethod)
        
        if not matchedPairs:
            raise StandardError('No Matching Nodes found in the PoseFile!')    
        else:
            nodesToLoad.reverse() #for the snapping operations
            
            #make the reference posePointCloud and cache it's initial xforms
            if relativePose:
                reference=mc.ls(sl=True,l=True)[0]
                self._buildOffsetCloud(nodesToLoad,reference,raw=True)
                resetCache=[mc.getAttr('%s.translate' % self.posePointRoot), mc.getAttr('%s.rotate' % self.posePointRoot)]  
            
            self._applyPose(matchedPairs)
            log.info('Pose Read Successfully from : %s' % filepath)

            if relativePose:
                #snap the poseCloud to the new xform of the referenced node, snap the cloud
                #to the pose, reset the clouds parent to the cached xform and then snap the 
                #nodes back to the cloud
                r9Anim.AnimFunctions.snap([reference,self.posePointRoot])
                 
                if relativeRots=='projected':
                    if self.mayaUpAxis=='y':
                        mc.setAttr('%s.rx' % self.posePointRoot,0)
                        mc.setAttr('%s.rz' % self.posePointRoot,0)
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        mc.setAttr('%s.rx' % self.posePointRoot,0)
                        mc.setAttr('%s.ry' % self.posePointRoot,0)
                    
                self._snapPosePntstoNodes()
                
                if not relativeTrans=='projected':
                    mc.setAttr('%s.translate' % self.posePointRoot,resetCache[0][0][0],resetCache[0][0][1],resetCache[0][0][2])
                if not relativeRots=='projected':
                    mc.setAttr('%s.rotate' % self.posePointRoot,resetCache[1][0][0],resetCache[1][0][1],resetCache[1][0][2])
               
                if relativeRots=='projected':
                    if self.mayaUpAxis=='y':
                        mc.setAttr('%s.ry' % self.posePointRoot,resetCache[1][0][1])
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        mc.setAttr('%s.rz' % self.posePointRoot,resetCache[1][0][2])
                if relativeTrans=='projected':
                    if self.mayaUpAxis=='y':
                        mc.setAttr('%s.tx' % self.posePointRoot,resetCache[0][0][0])
                        mc.setAttr('%s.tz' % self.posePointRoot,resetCache[0][0][2])
                    elif self.mayaUpAxis=='z': # fucking Z!!!!!!
                        mc.setAttr('%s.tx' % self.posePointRoot,resetCache[0][0][0])    
                        mc.setAttr('%s.ty' % self.posePointRoot,resetCache[0][0][1])    
                            
                self._snapNodestoPosePnts()  
                mc.delete(self.posePointRoot)
                mc.select(reference)
    