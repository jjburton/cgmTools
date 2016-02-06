"""
skinDat
Josh Burton 
www.cgmonks.com

Core skinning data handler for cgm going forward.

Storing joint positions and vert positions so at some point can implement a method
to apply a skin without a reference object in scene if geo or joint counts don't match

Currently only regular skin clusters are storing...

Features...
- Skin data gather
- Read/write skin data to a readable config file
- Apply skinning data to geo of different vert count
- 

Thanks to Alex Widener for some ideas on how to set things up.

"""
# From Python =============================================================
import copy
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.OpenMaya as OM
import maya.OpenMayaAnim as OMA

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import Red9.packages.configobj as configobj

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.lib import (search,
                     names,
                     attributes,
                     rigging,
                     distance,
                     skinning)

class data(object):
    '''
    Class to handle skin data. Utilizes red9.packages.ConfigObj for storage format. Storing what might be an excess of info
    to make it more useful down the road for applying skinning data to meshes that don't have the same vert counts or joint counts.
    
    :param mInstanes: given metaClass to test inheritance - cls or [cls]
    
    '''    
    _configToStored = {'source':'d_source',
                       'general':'d_general',
                       'skin':'d_sourceSkin',
                       'influences':'d_sourceInfluences'} 
    
    _geoToComponent = {'mesh':'vtx'}
    
    def __init__(self, sourceMesh = None, targetMesh = None, filepath = None, **kws):
        """

        """        
        self.d_source = {}
        self.d_sourceSkin = {}        
        self.d_target = {}
        self.d_sourceInfluences = {}
        self.d_weights = {}
        self.d_general = cgmGeneral.get_mayaEnviornmentDict()
        self.d_general['file'] = mc.file(q = True, sn = True)            
           
        if sourceMesh is not None or mc.ls(sl=True):
            self.validateSourceMesh(sourceMesh)
        if targetMesh is not None:
            self.d_target = self.validateTargetMesh(targetMesh)
        if filepath is not None:
            try:self.read(filepath)
            except:log.error("Filepath failed to read.")
            
    @classmethod   
    def validateMeshArg(self, mesh = None):
        '''
        Validates a mesh and returns a dict of data
        
        :param mesh: mesh to evaluate
        
        '''        
        _mesh = None 
        _skin = None
        if mesh is None:
            #if self.d_kws.get('sourceMesh'):
                #log.info("Using stored sourceMesh data")
                #sourceMesh = self.d_kws.get('sourceMesh')
            #else:
            log.info("No source specified, checking if selection found")
            _bfr = mc.ls(sl=True)
            if not _bfr:raise ValueError,"No selection found and no source arg"
            mesh = _bfr[0]
            
        _type = search.returnObjectType(mesh)
        
        if _type in ['mesh', 'nurbsCurve', 'nurbsSurface']:
            if _type in ['nurbsCurve','nurbsSurface']:
                raise  NotImplementedError, "Haven't implemented nurbsCurve or nurbsSurface yet"
            log.info("Skinnable object '{0}', checking skin".format(mesh))
            _mesh = mesh
            _skin = skinning.querySkinCluster(_mesh) or False
            if _skin:
                log.info("Found skin '{0}' on '{1}'".format(_skin,_mesh))
        elif _type in ['skinCluster']:
            log.info("skinCluster '{0}' passed...".format(mesh))
            _skin = mesh
            _mesh = attributes.doGetAttr(_skin,'outputGeometry')[0]
            log.info("Found: {0}".format(_mesh))
        else:
            raise ValueError,"Not a usable mesh type : {0}".format(_type)
        
        _shape = mc.listRelatives(_mesh,shapes=True,fullPath=False)[0]
        _return = {'mesh':_mesh,
                   'meshType':_type,
                   'shape':_shape,
                   'skin':_skin,
                   'component':data._geoToComponent.get(_type, False),
                   'pointCount':mc.polyEvaluate(_shape, vertex=True)
                   }
        return _return  
    
    def validateSourceMesh(self, sourceMesh = None):
        '''
        Validates a source mesh and returns a dict of data
        
        :param sourceMesh: mesh to evaluate
        
        '''        
        _d_Mesh = self.validateMeshArg(sourceMesh)
        self.d_source = _d_Mesh
        log.info("Source Mesh validated...")
        return _d_Mesh
        
    def validateTargetMesh(self, targetMesh = None):
        #if not self.d_source:
            #log.error("No source specified. Cannot validate target")
            #return False
        _d_Mesh = self.validateMeshArg(targetMesh)
        self.d_target = _d_Mesh
        log.info("Target Mesh validated...")
        return _d_Mesh

    def validateFilepath(self, filepath = None, fileMode = 0):
        '''
        Validates a given filepath or generates one with dialog if necessary
        '''        
        if filepath is None:
            startDir = mc.workspace(q=True, rootDirectory=True)
            filepath = mc.fileDialog2(dialogStyle=2, fileMode=fileMode, startingDirectory=startDir,
                                      fileFilter='Config file (*.cfg)')
            if filepath:filepath = filepath[0]
            
        if filepath is None:
            return False
        self.str_filepath = filepath
        log.info("filepath validated...")        
        return filepath

    def updateSourceSkinData(self):
        '''
        Updates the stored source skinning data
        '''        
        if not self.d_source:
            raise ValueError, "No source found. Cannot write data"
        
        if not self.d_sourceSkin:
            _d = gather_skinning_dict(self.d_source['mesh'])      
            self.d_source.update(_d['mesh'])#...update source dict
            self.d_sourceSkin = _d['skin']
            self.d_sourceInfluences = _d['influences']
            self.d_weights = _d['weights']
            return True
        return False
            
    def write(self, filepath = None):
        '''
        Write the Data ConfigObj to file
        '''
        filepath = self.validateFilepath(filepath)
        self.updateSourceSkinData()
            
        ConfigObj = configobj.ConfigObj(indent_type='\t')
        ConfigObj['configType']= 'cgmSkinConfig'        
        ConfigObj['source']=self.d_source
        ConfigObj['general']=self.d_general
        ConfigObj['skin']=self.d_sourceSkin
        ConfigObj['influences']=self.d_sourceInfluences        
        ConfigObj['weights']=self.d_weights
        ConfigObj.filename = filepath
        ConfigObj.write()
        return True
        
    def read(self, filepath = None, report = False):
        '''
        Read the Data ConfigObj from file and report the data if so desired.
        '''        
        filepath = self.validateFilepath(filepath, fileMode = 1)
        if not os.path.exists(filepath):            
            raise ValueError('Given filepath doesnt not exist : %s' % filepath)   
        
        _config = configobj.ConfigObj(filepath)
        if _config.get('configType') != 'cgmSkinConfig':
            raise ValueError,"This isn't a cgmSkinConfig config | {0}".format(filepath)
                
        for k in data._configToStored.keys():
            if _config.has_key(k):
                self.__dict__[data._configToStored[k]] = _config[k]
            else:
                log.error("Config file missing section {0}".format(k))
                return False
            
        if report:self.report()
        return True
    
    def applySkin(self,**kws):
        return applySkin(self,**kws)
        
    def report(self):
        log.info("Read Data Report "+ cgmGeneral._str_hardBreak)
        log.info("Config File: {0}".format(self.str_filepath))
        for k in data._configToStored.keys():
            _d_bfr = self.__dict__[data._configToStored[k]]
            if _d_bfr:
                log.info("{0} ".format(k) + cgmGeneral._str_subLine)
                l_keys = _d_bfr.keys()
                l_keys.sort()
                for k1 in l_keys:
                    _bfr = _d_bfr[k1]
                    if isinstance(_bfr,dict):
                        log.info(">" + "Nested Dict: {0}".format(k1) + cgmGeneral._str_subLine)
                        l_bufferKeys = _bfr.keys()
                        l_bufferKeys.sort()
                        for k2 in l_bufferKeys:
                            log.info("-"*3 +'>' + " {0} : {1} ".format(k2,_bfr[k2]))			
                    else:
                        log.info(">" + " {0} : {1} ".format(k1,_d_bfr[k1]))                	    

        
#>>> Utilities
#===================================================================
_skinclusterAttributesToCopy = {'envelope':float,#...dictionary for pulling config data to native data type
                                'bindMethod':int,
                                'skinningMethod':int,
                                'useComponents':bool,
                                'normalizeWeights':int,
                                "deformUserNormals":bool}

def applySkin(*args,**kws):
    '''
    Gathers skinning information - most likely for export to a file.
    
    :param data: data instance
    :param influenceMode: string arg of which mode to use for the influence data
       :target - Uses existing target objects skin cluster influences
       :source - Uses source mesh's skin cluster influences
       :config - Uses config files joint names
    '''
    _d_influenceModes = {'target':{'expectedKWs':[],'skinned':True,'indexMatch':True},#...use the target influences
                         'config':{},
                         'source':{},
                         'list':{}
                         }    
    class fncWrap(cgmGeneral.cgmFuncCls):

        def __init__(self,*args, **kws):	    
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'applySkin'
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'data',"default":None,
                                          'help':"data instance"},
                                         {'kw':'influenceMode',"default":'Exisiting',
                                          'help':"Mode by which to map influence data"},                                                                                  ]
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Gather Info','call':self._fnc_info},
                                {'step':'Process Influence Mode','call':self._fnc_processInfluenceMode}, 
                                {'step':'Process Data','call':self._fnc_processData},                                                                
                                {'step':'Verify Skincluster','call':self._fnc_skinCluster},
                                {'step':'Apply Weights Data','call':self._fnc_applyData},                                                                                                
                                ]
            #=================================================================

        def _fnc_info(self):
            #>> validate ============================================================================
            #_validate our source
            _data = self.d_kws['data']
            if isinstance(type(_data),type(data)):
                self.mData = _data
            else:
                raise ValueError,"Not a data instance"
            
            if not _data.d_source:
                raise ValueError,"No source data on data object"
            if not _data.d_target:
                raise ValueError,"No target data on data object"
            if not _data.d_sourceInfluences:
                return self._FailBreak_("No influence data. Read a config file to the data object.")
            
            _influenceMode = self.d_kws.get('influenceMode')
            if _influenceMode in _d_influenceModes.keys():
                self._influenceMode = _influenceMode
                self.log_info("influenceMode: '{0}'".format(_influenceMode))
            else:
                return self._FailBreak_("Unknown influenceMode arg ['{0}'] | Valid args{1}".format(_influenceMode,_d_influenceModes.keys()))                
            
            #self.report()
            self._d_jointToWeighting = {}
            self._d_vertToWeighting = {}
            self._l_processed = []
            self._b_smooth = False#...whether to smooth at the end of the weight copy
            
        def _fnc_processInfluenceMode(self):
            '''
            Sort out the joint data
            
            If joitn list is passed, try to use that, if not,
            Try skin cluster on target, cluster on source
            '''
            _mode = self._influenceMode
            _l_configInfluenceList = self.get_ConfigJointList()#...get our config influence list
            
            
            _targetMesh = self.mData.d_target['mesh']
            #...See if we have a skin cluster...
            _targetSkin = skinning.querySkinCluster(_targetMesh) or False            
            
            if _mode == 'config':
                _l_jointTargets = _l_configInfluenceList
                
            elif _mode == 'list':
                _l_joints = self.d_kws.get('jointList')
                if not _l_joints:
                    return self._FailBreak_("jointList kw required. '{0}' influenceMode".format(_mode))                
                if not cgmValid.isListArg(_l_joints):
                    return self._FailBreak_("jointList is not a list. '{0}' influenceMode".format(_mode))                
                if len(_l_joints) != len(_l_configInfluenceList):
                    return self._FailBreak_("Non matching counts on target influences({0}) and config data({1}) | Cannot use '{2}' influenceMode".format(len(_l_joints),len(_l_configInfluenceList),_mode))                
                _l_jointTargets = _l_joints
               

            elif _mode == 'target':
                if not _targetSkin:
                    return self._FailBreak_("Target mesh not skinned, cannot use '{0}' influenceMode".format(_mode))                
                _l_targetInfluences = mc.listConnections(_targetSkin+'.matrix') or []
                
                if len(_l_targetInfluences) != len(_l_configInfluenceList):
                    return self._FailBreak_("Non matching counts on target influences({0}) and config data({1}) | Cannot use '{2}' influenceMode".format(len(_l_targetInfluences),len(_l_configInfluenceList),_mode))                
                    
                _l_jointTargets = _l_targetInfluences
                
            #...see if they exist with no conflicts
            #_l_jointTargets = l_dataJoints#...this will change
            try:_l_jointsToUse = cgmValid.objStringList(_l_jointTargets, mayaType = 'joint')
            except Exception,Error:return self._FailBreak_("influenceMode '{0}' joint check fail | {1}".format(_mode,Error))
            
            #self.log_info("Joints to use....")
            #for i,j in enumerate(_l_jointsToUse):
                #self.log_info("{0} : {1} | config idxed to: {2}".format(i,j,_l_configInfluenceList[i]))
                
            self.l_jointsToUse = _l_jointsToUse
            
        def get_ConfigJointList(self):
            _l = []
            _d_influenceData = self.mData.d_sourceInfluences['data']
            _l_idxKeys = [int(k) for k in _d_influenceData.keys()]#...int them to sort them properly
            _l_idxKeys.sort()

            for idx in _l_idxKeys:
                _bfr = _d_influenceData[str(idx)]['name']
                _l.append(_bfr)                
            return _l
        
        def _fnc_processData(self):
            '''
            Sort out the components
            '''            
            #...check if our vtx counts match...
            self.log_toDo("Non matching components")
            self.log_toDo("Non matching mesh types")   
            self.mData.d_target = data.validateMeshArg(self.mData.d_target['mesh'])#...update
            
            _int_sourceCnt = int(self.mData.d_source['pointCount'])
            _int_targetCnt = int(self.mData.d_target['pointCount'])
            _type_source = self.mData.d_source['meshType']
            _type_target = self.mData.d_target['meshType']
            _target = self.mData.d_target['mesh']
            _component = self.mData.d_target['component']
            self.log_infoDict(self.mData.d_target,'target dict...')
            
            #if int(_int_sourceCnt) != int(_int_targetCnt):
                #return self._FailBreak_("Haven't implemented non matching component counts | source: {0} | target: {1}".format(_int_sourceCnt,_int_targetCnt))              
            if not _type_source == _type_target:
                return self._FailBreak_("Haven't implemented non matching mesh types | source: {0} | target: {1}".format(_type_source,_type_target))              
            
            #...generate a processed list...
            #[[jntIdx,v],[jntIdx,v]....] -- the count in the list is the vert count
            _raw_componentWeights = self.mData.d_sourceInfluences['componentWeights']
            _raw_blendweights = self.mData.d_sourceInfluences['blendWeights']
            
            _l_cleanData = []
            
            #...First loop is to only initially clean the data...
            for i in range(_int_sourceCnt):#...for each vert
                _str_i = str(i)
                _subL = []
                
                _bfr_raw = _raw_componentWeights[_str_i]
                _bfr_clean = {}
                for k,value in _bfr_raw.iteritems():
                    _bfr_clean[int(k)] = float(value)
                #self.log_info("vert {0} : {1}".format(i,_bfr_clean))
                _l_cleanData.append(_bfr_clean)
            self._l_processed = _l_cleanData#...initiall push data
                
                
            if int(_int_sourceCnt) != int(_int_targetCnt):
                try:#closest to remap ------------------------------------------------------------------------
                    self.log_warning("Non matching component counts. Using closestTo method to remap")
                    _l_closestRetarget = []
                    #...generate a posList of the source data
                    l_source_pos = []
                    _d_pos = self.mData.d_source['d_vertPositions']
                    for i in range(_int_sourceCnt):
                        l_source_pos.append([float(v) for v in _d_pos[str(i)]])#...turn our strings to values
                       
                    self.progressBar_start(stepMaxValue=_int_targetCnt, 
                                           statusMessage='Calculating....', 
                                           interruptableState=False)  
                    
                    for i in range(_int_targetCnt):
                        _str_vert = "{0}.{1}[{2}]".format(_target,_component,i)
                        self.progressBar_iter(status = "Finding closest to '{0}'".format(_str_vert))                                        
                        
                        #self.log_info(_str_vert)
                        _pos = distance.returnWorldSpacePosition(_str_vert)#...get position       
                        _closestPos = distance.returnClosestPoint(_pos, l_source_pos)#....get closest
                        _closestIdx = l_source_pos.index(_closestPos)
                        #self.log_info("target idx: {0} | Closest idx: {0} | pos:{1}".format(i,_closestIdx,_closestPos))
                        _l_closestRetarget.append(_l_cleanData[_closestIdx])
                    self.progressBar_end()
                        
                    self._l_processed = _l_closestRetarget#...push it backs
                    self._b_smooth = True
                    
                    if _int_targetCnt >= _int_sourceCnt:
                        self._f_smoothWeightsValue = .00005
                    else:
                        self._f_smoothWeightsValue = .5
                        
                    self.log_info("closestTo remap complete...")
                except Exception,error:
                    raise Exception,"closestTo remap failure | {0}".format(error)
            self._refineProcessedData()
            
        
        def _refineProcessedData(self):
            """
            Push the processed data to dicts for easier calling...
            """
            #self._d_jointToWeighting = {jIdx:{vIDX:v}}
            #self._d_vertToWeighting = {vIdx:{jIdx:v...}} 
            
            for i in range(len(self.l_jointsToUse)):
                self._d_jointToWeighting[i] = {}
            
            for i,d_pair in enumerate(self._l_processed):
                self._d_vertToWeighting[i] = d_pair
                
                for j_idx in d_pair.keys():
                    self._d_jointToWeighting[j_idx][i] = d_pair[j_idx] 
            
            #self.log_infoDict(self._d_vertToWeighting,'Vert To Weighting')
            #self.log_infoDict(self._d_jointToWeighting,'Joint To Weighting')
                    
        
        def _fnc_skinCluster(self):
            self.log_toDo("Add ability to check exisiting targets skin")
            self.log_toDo("Add more than just skincluster ability?...")  
            #..........................................................
            _targetMesh = self.mData.d_target['mesh']

            #...See if we have a skin cluster...
            _targetSkin = skinning.querySkinCluster(_targetMesh) or False
            if _targetSkin:
                self.log_info("Skincluster exists, recreating...")
                #try:mc.delete(_targetSkin)
                #except:pass
            else:
                #...create our skin cluster                
                _l_bind = copy.copy(self.l_jointsToUse)
                _l_bind.append(_targetMesh)                
                _targetSkin = mc.skinCluster(_l_bind,tsb=True,n=(names.getBaseName(_targetMesh)+'_skinCluster'))[0]                
            

            self.mData.d_target['skin'] = _targetSkin#...update the stored data
            self.log_info("Created '{0}'".format(_targetSkin) + cgmGeneral._str_subLine)
            
            #...Does this skin cluster have our expected targets?
            
        def _fnc_applyData(self):
            '''
            '''    
            _targetSkin = self.mData.d_target['skin']   
                    
            mi_skinCluster = cgmMeta.cgmNode(_targetSkin)
            skinFn = OMA.MFnSkinCluster( mi_skinCluster.mNodeMObject )
                
            #...Set our weights ------------------------------------------------------------------------------------
            weightListP = skinFn.findPlug( "weightList" )
            weightListObj = weightListP.attribute()
            weightsP = skinFn.findPlug( "weights" )
        
            tmpIntArray = OM.MIntArray()
            baseFmtStr = mi_skinCluster.mNode +'.weightList[%d]'  #pre build this string: fewer string ops == faster-ness!
            
            self.progressBar_start(stepMaxValue=self.mData.d_target['pointCount'], 
                                   statusMessage='Calculating....', 
                                   interruptableState=False)        
            
            for vertIdx in self._d_vertToWeighting.keys():
                self.progressBar_iter(status = 'Setting {0}'.format(vertIdx))                
                _d_vert = self._d_vertToWeighting[vertIdx]#...{0:value,...}
                
                #we need to use the api to query the physical indices used
                weightsP.selectAncestorLogicalIndex( vertIdx, weightListObj )
                weightsP.getExistingArrayAttributeIndices( tmpIntArray )
        
                weightFmtStr = baseFmtStr % vertIdx +'.weights[{0}]'
            
                #clear out any existing skin data - and awesomely we cannot do this with the api - so we need to use a weird ass mel command
                for n in range( tmpIntArray.length() ):
                    mc.removeMultiInstance( weightFmtStr.format(tmpIntArray[n]) )            
            
                #at this point using the api or mel to set the data is a moot point...  we have the strings already so just use mel
                for jointIdx in _d_vert.keys():
                    #self.log_info(" vtx: {0} | jnt:{1} | value:{2}".format(vertIdx,jointIdx, _d_vert[jointIdx]))
                    mc.setAttr( weightFmtStr.format(jointIdx), _d_vert[jointIdx] )              
            self.progressBar_end()
            
            #...blendWeights
            
            #self.setBlendWeights(dagPath, components)
                    
            #...apply our settings from our skin...
            for k in _skinclusterAttributesToCopy:
                _value = _skinclusterAttributesToCopy[k](self.mData.d_sourceSkin[k])
                self.log_info("Setting '{0}' to {1}".format(k,_value))
                try:attributes.doSetAttr(_targetSkin,k,_value)
                except Exception,error:
                    self.log_error("{0} failed | {1}".format(k,error))
                    
            #...smooth process
            if self._b_smooth:
                self.log_warning("Smoothing weights ({0})...".format(self._f_smoothWeightsValue))
                mc.skinCluster(_targetSkin,e = True, smoothWeights = self._f_smoothWeightsValue ,smoothWeightsMaxIterations = 2)
                #mc.skinCluster(_targetSkin,e = True, smoothWeights = .0005,smoothWeightsMaxIterations = 10)
    return fncWrap(*args,**kws).go()

def gather_skinning_dict(*args,**kws):
    '''
    Gathers skinning information - most likely for export to a file.
    
    :param mInstanes: given metaClass to test inheritance - cls or [cls]
    '''
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):	    
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'gather_skinning_dict'
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'source',"default":None,
                                          'help':"source object or skin cluster"},
                                         ]
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Validate','call':self._validate},
                                {'step':'Gather Skin Data','call':self._gather_skin},
                                ]
            #=================================================================

        def _validate(self):
            #>> validate ============================================================================
            self._d_data = {"mesh": {},
                            "skin": {},
                            "weights":{},
                            "blendWeights":[],
                            "influences":{}}
            
            #_validate our source
            _source = self.d_kws['source']
            _d = data().validateSourceMesh(_source)

            self._mesh = _d['mesh']
            self._skin = _d['skin']  
            self.mi_mesh = cgmMeta.cgmObject(self._mesh)
            self.mi_cluster = cgmMeta.cgmNode(self._skin)
            
            # Get the skinCluster MObject
            self.selectionList = OM.MSelectionList()
            self.selectionList.add(self._skin, True)
            self.mobject = OM.MObject()
            self.selectionList.getDependNode(0, self.mobject)
            self.fn = OMA.MFnSkinCluster(self.mobject)            
            """self.data = {'weights' : {},
                         'blendWeights' : [],
                         }"""
            
            _d['name'] = self.mi_mesh.mNode
            _d['d_vertPositions'] = {}
            
            self._d_data['mesh'] = _d
                        
        def _gather_skin(self):
            self._d_skin = {}
            _d = {}
            
            #for a in 'useComponents','skinningMethod','normalize','geometryType','bindMethod',
            #'normalizeWeights',
            #'maintainMaxInfluences','maxInfluences','dropoffRate','smoothness','lockweights':
            for a in self.mi_cluster.getAttrs():#...first gather general attributes
                try:
                    _bfr = self.mi_cluster.getMayaAttr(a)
                    if _bfr is not None:_d[a] = _bfr
                except:
                    self.log_error("{0} failed to query".format(a))
                               
            self._d_skin = _d#...link back
            self._d_data['skin'] = _d            
            #self.log_infoNestedDict('_d_skin')
            

            #...gather weighting data -------------------------------------------------------------------
            _d = {}
            dagPath, components = self.__getGeometryComponents()
            #self.log_info('dagPath: {0}'.format(dagPath))
            #self.log_info('components: {0}'.format(components))
            self.gatherInfluenceData(dagPath, components)
            self.gatherBlendWeightData(dagPath, components)
            _vtx = self._d_data['mesh']['component']#...link to the component type 
            l_sourceComponent = (mc.ls ("{0}.{1}[*]".format(self._mesh,_vtx),flatten=True))
            l_influences = self._d_skin['matrix']
            
            self.progressBar_start(stepMaxValue=len(l_sourceComponent), 
                                   statusMessage='Calculating....', 
                                   interruptableState=False)
            
            _d_componentWeights = {}            

            for i,vertice in enumerate(l_sourceComponent):
                self.progressBar_iter(status = 'Getting {0}'.format(vertice))
                skinValues = {}
                _key = str(i)
                
                self._d_data['mesh']['d_vertPositions'][_key] = mc.pointPosition("{0}.{1}[{2}]".format(self._mesh,_vtx,i),w=True)
                                
                """for ii,influence in enumerate(l_influences):
                    influenceValue = mc.skinPercent(self._skin, vertice, transform = influence, query = True)
                    if influenceValue != 0:
                        skinValues[str(ii)] = influenceValue"""
                
                for ii,influence in enumerate(l_influences):
                    _bfr = self._d_data['weights'][str(ii)][i]#...pull from our weights data to be much much faster...
                    if _bfr != 0:
                        skinValues[str(ii)] = _bfr
                
                _d_componentWeights[_key] = skinValues 

            self.progressBar_end()
            #self.log_infoDict( _d_componentWeights, "Component Weights...")            
            self._d_data['influences']['componentWeights'] = _d_componentWeights
            return self._d_data
        
        def __getGeometryComponents(self):
            # Has jurisdiction over what is allowed to be influenced.
            fnSet = OM.MFnSet(self.fn.deformerSet())
            members = OM.MSelectionList()
            fnSet.getMembers(members, False)
            dagPath = OM.MDagPath()
            components = OM.MObject()
            members.getDagPath(0, dagPath, components)
            return dagPath, components
    
        def __getCurrentWeights(self, dagPath, components):
            weights = OM.MDoubleArray()
            util = OM.MScriptUtil()
            util.createFromInt(0)
            pUInt = util.asUintPtr()
            self.fn.getWeights(dagPath, components, weights, pUInt)
            return weights
    
        def gatherInfluenceData(self, dagPath, components):
            """
            Get the influence data
            """
            weights = self.__getCurrentWeights(dagPath, components)
    
            influencePaths = OM.MDagPathArray()
            numInfluences = self.fn.influenceObjects(influencePaths)
            numComponentsPerInfluence = weights.length() / numInfluences
            
            self.progressBar_start(stepMaxValue=influencePaths.length(), 
                                   statusMessage='Calculating....', 
                                   interruptableState=False)
            _d_influenceData = {}            
            for i in range(influencePaths.length()):
                _k = str(i)
                influenceName = influencePaths[i].partialPathName()
                influenceWithoutNamespace = names.getBaseName(influenceName)
                
                _d_influenceData[_k] = {'name': influenceWithoutNamespace,
                                        'position':distance.returnWorldSpacePosition(influenceName)}
                
                # store weights by influence & not by namespace so it can be imported with different namespaces.
                self.progressBar_iter(status = 'Getting {0}...data'.format(influenceName))                                
                self._d_data['weights'][_k] = \
                    [weights[jj*numInfluences+i] for jj in range(numComponentsPerInfluence)]
                
            self._d_data['influences']['data'] = _d_influenceData  
            self.progressBar_end()
    
        def gatherBlendWeightData(self, dagPath, components):
            weights = OM.MDoubleArray()
            self.fn.getBlendWeights(dagPath, components, weights)
            self._d_data['influences']['blendWeights'] = [weights[i] for i in range(weights.length())]  
            
    return fncWrap(*args,**kws).go()