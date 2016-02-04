"""
skin Utils
Josh Burton 
www.cgmonks.com

Core skinning data handler for cgm going forward.

Storing joint positions and vert positions so at some point can implement a method
to apply a skin without a reference object in scene if geo or joint counts don't match

Currently only regular skin clusters are storing...

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
from maya import OpenMaya

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
    
    :todo
    -- import config
    -- deal with variable influence/vertc count scenarios
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
        self.d_general = cgmGeneral.get_mayaEnviornmentDict()
        self.d_general['file'] = mc.file(q = True, sn = True)            
           
        if sourceMesh is not None:
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
        if not self.d_source:
            log.error("No source specified. Cannot validate target")
            return False
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
    
        ConfigObj.filename = filepath
        ConfigObj.write()
        return True
        
    def read(self, filepath = None, report = True):
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
    
    :param mInstanes: given metaClass to test inheritance - cls or [cls]
    '''
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):	    
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'data_import'
            self._b_reportTimes = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'data',"default":None,
                                          'help':"data instance"},
                                         ]
            self.__dataBind__(*args,**kws)
            self.l_funcSteps = [{'step':'Gather Info','call':self._info},
                                {'step':'Process Joints','call':self._processJoints}, 
                                {'step':'Process Components','call':self._processComponents},                                                                
                                {'step':'Verify Skincluster','call':self._skinCluster},
                                #{'step':'Apply Weights','call':self._applyWeights},                                                                                                
                                #{'step':'Set up skinCluster','call':self._skin},
                                ]
            #=================================================================

        def _info(self):
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
            #self.report()
            
        def _processJoints(self):
            '''
            Sort out the joint data
            '''
            #...starting joint list
            #...get from influence data
            #md_joints = {}
            
            l_dataJoints = []
            _d_influenceData = self.mData.d_sourceInfluences['influenceData']
            _l_idxKeys = [int(k) for k in _d_influenceData.keys()]#...int them to sort them properly
            _l_idxKeys.sort()
            
            for idx in _l_idxKeys:
                _bfr = _d_influenceData[str(idx)]['name']
                l_dataJoints.append(_bfr)
                #md_joints[int(idx)] = {obj:,
                #                      mObj:}
                
                
            #...see if they exist with no conflicts
            _l_jointTargets = l_dataJoints#...this will change
            _l_jointsToUse = cgmValid.objStringList(_l_jointTargets, mayaType = 'joint')
            self.log_info("Joints to use....")
            for i,j in enumerate(_l_jointsToUse):
                self.log_info("{0} : {1}".format(i,j))
                
            self.l_jointsToUse = _l_jointsToUse

        
        def _processComponents(self):
            '''
            Sort out the components
            '''            
            #...check if our vtx counts match...
            self.log_toDo("Non matching components")
            self.log_toDo("Non matching mesh types")            
            _int_sourceCnt = self.mData.d_source['pointCount']
            _int_targetCnt = self.mData.d_target['pointCount']
            _type_source = self.mData.d_source['meshType']
            _type_target = self.mData.d_target['meshType']
            self.log_infoDict(self.mData.d_target,'target dict...')
            if int(_int_sourceCnt) != int(_int_targetCnt):
                return self._FailBreak_("Haven't implemented non matching component counts | source: {0} | target: {1}".format(_int_sourceCnt,_int_targetCnt))              
            if not _type_source == _type_target:
                return self._FailBreak_("Haven't implemented non matching mesh types | source: {0} | target: {1}".format(_type_source,_type_target))              
            #...generate a component list...
            pass
        
        def _skinCluster(self):
            self.log_toDo("Add ability to check exisiting targets skin")
            self.log_toDo("Add more than just skincluster ability?...")  
            #..........................................................
            _targetMesh = self.mData.d_target['mesh']
            

            #...See if we have a skin cluster...
            _targetSkin = skinning.querySkinCluster(_targetMesh) or False
            if _targetSkin:
                self.log_info("Skincluster exists, recreating...")
                try:mc.delete(_targetSkin)
                except:pass
            
            #...create our skin cluster
            _l_bind = copy.copy(self.l_jointsToUse)
            _l_bind.append(_targetMesh)
            _targetSkin = mc.skinCluster(_l_bind,tsb=True,n=(names.getBaseName(_targetMesh)+'_skinCluster'))[0]
            self.mData.d_target['skin'] = _targetSkin#...update the stored data
            self.log_info("Created '{0}'".format(_targetSkin) + cgmGeneral._str_subLine)
            
            #...apply our settings from our skin
            for k in _skinclusterAttributesToCopy:
                _value = _skinclusterAttributesToCopy[k](self.mData.d_sourceSkin[k])
                self.log_info("Setting '{0}' to {1}".format(k,_value))
                try:attributes.doSetAttr(_targetSkin,k,_value)
                except Exception,error:
                    self.log_error("{0} failed | {1}".format(k,error))

            #...Does this skin cluster have our expected targets?
            
        def _applyWeights(self):
            '''
            '''            
            pass           
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
                            "skin": {}}
            #_validate our source
            _source = self.d_kws['source']
            _d = data().validateSourceMesh(_source)

            self._mesh = _d['mesh']
            self._skin = _d['skin']  
            self.mi_mesh = cgmMeta.cgmObject(self._mesh)
            
            
            self.mi_cluster = cgmMeta.cgmNode(self._skin)
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
            self.log_infoNestedDict('_d_skin')

            #...gather weighting data -------------------------------------------------------------------
            _d = {}
            
            _vtx = self._d_data['mesh']['component']#...link to the component type      
            
            l_sourceComponent = (mc.ls ("{0}.{1}[*]".format(self._mesh,_vtx),flatten=True))
            l_influences = self._d_skin['matrix']
            
            _d_influenceData = {}
            for i,obj in enumerate(l_influences):
                _key = str(i)
                _d_influenceData[_key] = {'name': obj,
                                          'position':distance.returnWorldSpacePosition(obj)}
            _d['influenceData'] = _d_influenceData
            
            self.progressBar_start(stepMaxValue=len(l_sourceComponent), 
                                   statusMessage='Calculating....', 
                                   interruptableState=False)
            
            _d_componentWeights = {}
            for i,vertice in enumerate(l_sourceComponent):
                self.progressBar_iter(status = 'Getting {0}'.format(vertice))
                skinValues = {}
                _key = str(i)
                
                self._d_data['mesh']['d_vertPositions'][_key] = mc.pointPosition("{0}.{1}[{2}]".format(self._mesh,_vtx,i),w=True)
                
                for ii,influence in enumerate(l_influences):
                    influenceValue = mc.skinPercent(self._skin, vertice, transform = influence, query = True)
                    if influenceValue != 0:
                        skinValues[str(ii)] = influenceValue
                        
                _d_componentWeights[_key] = skinValues 
                
                #self.log_info("Vertice {0} | Component: '{1}'".format(i,vertice))
                #for v in _d_componentWeights[str(i)].keys():
                    #self.log_info(">   {0} : {1}".format(v,_d_componentWeights[_key][v]))  
            self.progressBar_end()
            _d['componentWeights'] = _d_componentWeights
            
            self._d_data['influences'] = _d
            return self._d_data
    return fncWrap(*args,**kws).go()