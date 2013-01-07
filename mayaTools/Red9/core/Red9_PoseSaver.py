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
        self.posePointCloudNodes=[]
        self.mayaUpAxis=r9Setup.mayaUpAxis()
        self.thumbnailRes=[128,128]
        self.metaPose=False
           
        # make sure we have a settings object
        if filterSettings:
            if issubclass(type(filterSettings), r9Core.FilterNode_Settings):
                self.settings=filterSettings
            else:
                raise StandardError('filterSettings param requires an r9Core.FilterNode_Settings object')
        else:
            self.settings=r9Core.FilterNode_Settings()
            
        self.metaPose=self.settings.metaRig
        self.settings.printSettings()
           
        
    # Build the poseDict data ---------------------------------------------
    #@r9General.Timer
    def _getNodeMetaDataMap(self, node, mTypes=[]):
        '''
        This is a generic wrapper to extract metaData connection info for any given node
        used to build the pose dict up, and compare / match the data on load 
        @param node: node to inspect and get the connection data back from
        @return: mNodes={} which is directly pushed into the PoseFile under the [metaData] key
        TODO: Maybe this should go into the MetaRig class then it could be over-loaded
              by others using different wiring setups?
        '''
        mNodes={}
        #why not use the r9Meta.getConnectedMetaNodes ?? > well here we're using 
        #the c=True flag to get both plugs back in one go to process later
        connections=[]
        for nType in r9Meta.getMClassNodeTypes():
            con=cmds.listConnections(node,type=nType,s=True,d=False,c=True,p=True)
            if con:
                connections.extend(con)
        if not connections:
            return connections
        data=connections[-1].split('.')
        if r9Meta.isMetaNode(data[0],mTypes=mTypes):
            mNodes['metaAttr']=data[1]
            try:
                mNodes['metaNodeID']=cmds.getAttr('%s.mNodeID' % data[0])
            except:
                mNodes['metaNodeID']=node.split(':')[-1].split('|')[-1]
        return mNodes          

    def _buildInfoBlock(self):
        '''
        Basic info for the pose file, this could do with expanding
        '''
        self.infoDict['author']=getpass.getuser()
        self.infoDict['date']=time.ctime()
        self.infoDict['metaPose']=self.metaPose
        
    def _buildPoseDict(self, nodes):  
        '''
        Build the internal poseDict up from the given nodes. This is the 
        core of the Pose System 
        '''   
        if self.metaPose:
            getMetaDict=self._getNodeMetaDataMap #optimisation

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
                        self.poseDict[key]['attrs'][attr]=cmds.getAttr('%s.%s' % (node,attr))
                    except:
                        log.debug('%s : attr is invalid in this instance' % attr)


    # Process the data -------------------------------------------------
                                              
    def _writePose(self, filepath):
        '''
        Write the Pose ConfigObj to file
        '''
        ConfigObj = configobj.ConfigObj(indent_type='\t')
        ConfigObj['filterNode_settings']=self.settings.__dict__
        ConfigObj['poseData']=self.poseDict
        ConfigObj['info']=self.infoDict
        ConfigObj.filename = filepath
        ConfigObj.write()

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
            else:
                raise StandardError('Given filepath doesnt not exist : %s' % filename)
        else:
            raise StandardError('No FilePath given to read the pose from')
        
    @r9General.Timer 
    def _matchNodesToPoseData(self, nodes, matchMethod='name'):
        '''
        Main filter to extract matching data pairs prior to processing
        return : tuple such that :  (poseDict[key], destinationNode)
        @param nodes: nodes to try and match from the poseDict
        @param matchMethod: how to match the nodes to the poseDict data, maybe this should 
                be passed directly in to the matchNodeLists call so we can deal with prefix etc?
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
            getMetaDict=self._getNodeMetaDataMap #optimisation
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

                         
    def matchInternalPoseObjects(self, nodes=None, fromFilter=True):
        '''
        This is a throw-away and only used in the UI to select for debugging!
        from a given poseFile return or select the internal stored objects 
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
            nodesToStore=r9Core.FilterNode(nodes,self.settings).ProcessFilter()
            
        self._buildInfoBlock()    
        self._buildPoseDict(nodesToStore) 
        self._writePose(filepath)
        
        sel=cmds.ls(sl=True,l=True)
        cmds.select(cl=True)
        r9General.thumbNailScreen(filepath,self.thumbnailRes[0],self.thumbnailRes[1])
        
        if sel:
            cmds.select(sel)
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
        nodesToLoad=nodes
        if not os.path.exists(filepath):
            raise StandardError('Given Path does not Exist')
        if relativePose and not cmds.ls(sl=True):
            raise StandardError('Nothing selected to align Relative Pose too')
        if self.settings.filterIsActive() and useFilter:
            nodesToLoad=r9Core.FilterNode(nodes,self.settings).ProcessFilter()
        if not nodesToLoad:
            raise StandardError('Nothing selected or returned by the filter to load the pose onto')
           
        self._readPose(filepath)

        if self.metaPose:
            if self.infoDict.has_key('metaPose') and eval(self.infoDict['metaPose']):
                matchMethod='metaData'
            else:
                log.debug('Warning, trying to load a NON metaPose to a MRig - switching to NameMatching')  
                 
        #Build the master list of matched nodes that we're going to apply data to
        #Note: this is built up from matching keys in the poseDict to the given nodes
        matchedPairs=self._matchNodesToPoseData(nodesToLoad,matchMethod=matchMethod)
        
        if not matchedPairs:
            raise StandardError('No Matching Nodes found in the PoseFile!')    
        else:
            nodesToLoad.reverse() #for the snapping operations
            
            #make the reference posePointCloud and cache it's initial xforms
            if relativePose:
                reference=cmds.ls(sl=True,l=True)[0]
                self._buildOffsetCloud(nodesToLoad,reference,raw=True)
                resetCache=[cmds.getAttr('%s.translate' % self.posePointRoot), cmds.getAttr('%s.rotate' % self.posePointRoot)]  
            
            self._applyPose(matchedPairs)
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
    
    fNode=r9Core.FilterNode(cmds.ls(sl=True)[0])
    fNode.settings.metaRig=True
    nodes=fNode.ProcessFilter()
    
    #build an mPose object and fill the internal poseDict
    mPoseA=r9Pose.PoseData()
    mPoseA._buildPoseDict(nodes)

    mPoseB=r9Pose.PoseData()
    mPoseB._buildPoseDict(nodes)
    
    compare=r9Pose.PoseCompare(mPoseA,mPoseB)
    .... or .... 
    compare=r9Pose.PoseCompare(mPoseA,'H:/Red9PoseTests/thisPose.pose')
    .... or ....
    compare=r9Pose.PoseCompare('H:/Red9PoseTests/thisPose.pose','H:/Red9PoseTests/thatPose.pose')
        
    compare.compare() #>> bool, True = same
    compare.fails['failedAttrs']
    '''
    def __init__(self, currentPose, referencePose):
        '''
        make sure we have 2 PoseData objects to compare
        @param currentPose: either a PoseData object or a valid pose file
        @param referencePose: either a PoseData object or a valid pose file
        '''
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
       
    def compare(self, tolerance=0.001):
        '''
        Compare the 2 PoseData objects via their internal [key][attrs] blocks
        return a bool. After processing self.fails is a dict holding all the fails
        for processing later if required
        @param tolerance: tolerance by which floats are matched
        '''
        self.fails={}
        
        for key, attrBlock in self.currentPose.poseDict.items():
            if self.referencePose.poseDict.has_key(key):
                referenceAttrBlock=self.referencePose.poseDict[key]
            else:
                log.info('Key Mismatch : %s' % key)
                if not self.fails.has_key('missingKeys'):
                    self.fails['missingKeys']=[]
                self.fails['missingKeys'].append(key)
                continue
            
            for attr, value in attrBlock['attrs'].items():
                #attr missing completely from the key
                if not referenceAttrBlock['attrs'].has_key(attr):
                    if not self.fails['failedAttrs'].has_key(key):
                        self.fails['failedAttrs'][key]={}
                    if not self.fails['failedAttrs'][key].has_key('missingAttrs'):
                        self.fails['failedAttrs'][key]['missingAttrs']=[]
                    self.fails['failedAttrs'][key]['missingAttrs'].append(attr)
                    continue
                
                #test the attrs value matches
                value=r9Core.decodeString(value)                                 #decode as this may be a configObj
                refValue=r9Core.decodeString(referenceAttrBlock['attrs'][attr])  #decode as this may be a configObj
                
                if type(value)==float:
                    if not r9Core.floatIsEqual(value, refValue, tolerance):
                        self.__addFailedAttr(key, attr)
                        log.info('AttrValue float mismatch : "%s.%s" currentValue=%s >> expectedValue=%s' % (key,attr,value,refValue))
                        continue    
                elif not value==refValue:
                    self.__addFailedAttr(key, attr)
                    log.info('AttrValue mismatch : "%s.%s" currentValue=%s >> expectedValue=%s' % (key,attr,value,refValue))
                    continue                 
                
        if self.fails.has_key('missingKeys') or self.fails.has_key('failedAttrs'):
            return False
        return True

        
        
        
        
        
        
