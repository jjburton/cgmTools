"""
skin Utils
Josh Burton 
www.cgmonks.com

Thanks to Alex Widener for some ideas on how to set things up.

"""
# From Python =============================================================
import copy

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
                     rigging,
                     distance,
                     skinning)

class data(object):
    '''
    Class to handle skin data. Utilizes red9.packages.ConfigObj for storage format.
    
    :param mInstanes: given metaClass to test inheritance - cls or [cls]
    
    :todo
    -- gather data
    -- d
    '''
    def __init__(self, sourceMesh = None, targetMesh = None, filepath = None, **kws):
        """

        """        
        self.d_source = {}
        self.d_sourceSkin = {}        
        self.d_target = {}
        self.d_sourceInfluences = {}
        self.d_general = cgmGeneral.get_mayaEnviornmentDict()
        self.d_general['file'] = mc.file(q = True, sn = True)            
        
        self.str_filepath = filepath
        
        """
        self.d_kws = {'sourceMesh':sourceMesh,
                      'targetMesh':targetMesh,
                      'filepath':filepath}
        for k in kws.keys():
            if k not in self.d_kws.keys():
                self.d_kws[k] = kws[k]"""
        
                
        if sourceMesh is not None:
            self.d_source = self.validateSourceMesh(sourceMesh)
            #self.d_data =  gather_skinning_dict(sourceMesh) 
        #if targetMesh is not None:
            #self._validateTargetMesh(targetMesh)

    @classmethod   
    def validateSourceMesh(self, sourceMesh = None):
        '''
        Validates a source mesh and returns a dict of data
        
        :param sourceMesh: mesh to evaluate
        
        '''        
        _mesh = None
        _skin = None
        
        if sourceMesh is None:
            #if self.d_kws.get('sourceMesh'):
                #log.info("Using stored sourceMesh data")
                #sourceMesh = self.d_kws.get('sourceMesh')
            #else:
            log.info("No source specified, checking if selection found")
            _bfr = mc.ls(sl=True)
            if not _bfr:raise ValueError,"No selection found and no source arg"
            sourceMesh = _bfr[0]
            
        _type = search.returnObjectType(sourceMesh)
        
        if _type in ['mesh', 'nurbsCurve', 'nurbsSurface']:
            log.info("Skinnable object, checking skin")
            _skin = skinning.querySkinCluster(sourceMesh)
            _mesh = sourceMesh
            if _skin:
                log.info("Found skin: '{0}' on '{1}'".format(_skin,sourceMesh))
            else:
                raise ValueError,"No skin cluster found"
        elif _type in ['skinCluster']:
            log.info("skinCluster passed...")
            _skin = sourceMesh
        else:
            raise RuntimeError,"Failed to find source data."
        
        _mi_mesh = cgmMeta.cgmObject(_mesh)
        _shape = _mi_mesh.getShapes()[0]
        
        _return = {'mesh':_mesh,
                   'skin':_skin,
                   'meshType':_type,
                   'mi_mesh':_mi_mesh,
                   'shape':_shape,
                   'pointCount':mc.polyEvaluate(_shape, vertex=True)
                   }
        return _return
        
    def validateTargetMesh(self, targetMesh = None):
        log.info(self.d_source)
        raise NotImplementedError,"Haven't finished this one yet..."
    
    @classmethod
    def validateFilepath(self, filepath = None):
        if filepath is None:
            startDir = mc.workspace(q=True, rootDirectory=True)
            filepath = mc.fileDialog2(dialogStyle=2, fileMode=0, startingDirectory=startDir,
                                      fileFilter='Config file (*.cfg)')
            if filepath:filepath = filepath[0]
            
        if filepath is None:
            return False
        
        return filepath
    
    def updateSourceSkinData(self):
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
        ConfigObj['source']=self.d_source
        ConfigObj['general']=self.d_general
        ConfigObj['skin']=self.d_sourceSkin
        ConfigObj['influences']=self.d_sourceInfluences        
    
        ConfigObj.filename = filepath
        ConfigObj.write()
        
    def read(self, filepath = None):
        pass
    
    
        
#>>> Utilities
#===================================================================
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
            _d = data.validateSourceMesh(_source)

            self._mesh = _d['mesh']
            self._skin = _d['skin']  
            self.mi_mesh = _d['mi_mesh']
            
            
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


            #...gather weighting data -------------------------------------------------------------------
            _d = {}
            
            _d_geo_v = {'mesh':'vtx'}
            _vtx = _d_geo_v[self._d_data['mesh']['meshType']]#...link to the component type      
            
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
                
                self.log_info("Vertice {0} | Component: '{1}'".format(i,vertice))
                for v in _d_componentWeights[str(i)].keys():
                    self.log_info(">   {0} : {1}".format(v,_d_componentWeights[_key][v]))  
            self.progressBar_end()
            _d['componentWeights'] = _d_componentWeights
            
            self._d_data['influences'] = _d
            return self._d_data
    return fncWrap(*args,**kws).go()