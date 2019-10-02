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
__version__ = "10.01.2019"
__MAYALOCAL = 'CGMPROJECT'


# From Python =============================================================
import copy
import os
import pprint

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
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as cgmValid
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

from cgm.lib import (search,
                     names,
                     cgmMath,
                     attributes,
                     rigging,
                     distance,
                     skinning)

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = 'cgmProjectManager'    
    WINDOW_TITLE = 'cgmProjectManager - {0}'.format(__version__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 350,500
    TOOLNAME = 'cgmProjectManager.ui'
    
    def insert_init(self,*args,**kws):
        _str_func = '__init__[{0}]'.format(self.__class__.TOOLNAME)            
        log.info("|{0}| >>...".format(_str_func))        

        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))
        log.info(self.__call__(q=True, title=True))

        self.__version__ = __version__
        self.__toolName__ = self.__class__.WINDOW_NAME	

        #self.l_allowedDockAreas = []
        self.WINDOW_TITLE = self.__class__.WINDOW_TITLE
        self.DEFAULT_SIZE = self.__class__.DEFAULT_SIZE
        
        
        self.mDat = data()

    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))
        self.uiMenu_help = mUI.MelMenu(l='Help', pmc = cgmGEN.Callback(self.buildMenu_help))
        

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='Settings' )
        #uiMenuItem_matchMode(self,self.uiMenu_FirstMenu)
        
        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu, label='Utils' )
        
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Dock",
                         c = lambda *a:self.do_dock())        

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def buildMenu_help( self, *args):
        self.uiMenu_help.clear()
        
        mUI.MelMenuItem( self.uiMenu_help, l="Dat | log ",
                         c=lambda *a: self.mDat.log_self( ))
        mc.menuItem(parent=self.uiMenu_help,
                    l = 'Get Help',
                    c='import webbrowser;webbrowser.open("https://http://docs.cgmonks.com/mrs.html");',                        
                    rp = 'N')    
        mUI.MelMenuItem( self.uiMenu_help, l="Log Self",
                         c=lambda *a: cgmUI.log_selfReport(self) )   

        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
    
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        
        _column = mUI.MelScrollLayout(parent=_MainForm)
        self.bUI_main(_column)
        #self.mManager = manager(parent = _column)
        
        #for k in self.__dict__.keys():
        #    if str(k).startswith('var_'):
        #        self.mManager.__dict__[k] = self.__dict__[k]
        
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
        _MainForm(edit = True,
                  af = [(_column,"top",0),
                        (_column,"left",0),
                        (_column,"right",0),
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [#(_column,"top",2,_context),
                        (_column,"bottom",2,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])
        
    def bUI_main(self,parent):
        self.mLabel_projectName = mUI.MelLabel(parent,label='Project X'.upper(), al = 'center', ut = 'cgmUIHeaderTemplate')
        
        
    
        #Pose Path ===============================================================================
        uiRow_pose = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate')
        self.uiPop_root = None
        
        mUI.MelSpacer(uiRow_pose,w=2)    
        
        mUI.MelLabel(uiRow_pose,label='Root:')
        mUI.MelSpacer(uiRow_pose,w=2)    
        """
        self.uiField_path = mUI.MelLabel(uiRow_pose,
                                         ann='Change the current path',
                                         label = 'None',
                                         ut='cgmUIInstructionsTemplate',w=100) """   
        
        
        self.cgmUIField_rootPath = mUI.MelTextField(uiRow_pose,
                                                    ann='The root path for our pose calls',
                                                    #cc = lambda *x:self._uiCB_setPosePath(field=False),
                                                    text = '')
                                                 
        uiRow_pose.setStretchWidget(self.cgmUIField_rootPath)
        
        mc.button(parent=uiRow_pose,
                  l = 'Set Path',
                  ut = 'cgmUITemplate',
                  #c= lambda *x:self.uiCB_setPosePath(fileDialog=True),
                  #en = _d.get('en',True),
                  #c = cgmGEN.Callback(uiCB_contextualAction,self,**_arg),
                  #ann = _d.get('ann',b))
                  )
        """
        mc.button(parent=uiRow_pose,
                  l = 'Test',
                  ut = 'cgmUITemplate',
                  c= lambda *x:log.info("Mode: {0} | local: {1} | project: {2}".format(self.var_pathMode.getValue(),self.posePathLocal, self.posePathProject)),
                  )"""
        mUI.MelSpacer(uiRow_pose,w=2)
        uiRow_pose.layout()
        mc.setParent(self)
        
        #self.uiPopup_setPath()
    





class data(object):
    '''
    Class to handle skin data. Utilizes red9.packages.ConfigObj for storage format. Storing what might be an excess of info
    to make it more useful down the road for applying skinning data to meshes that don't have the same vert counts or joint counts.
    
    :param sourchMesh: Mesh to export data from
    :param targetMesh: Mesh to import data to
    :param filepath: File to read on call or via self.read() call to browse to one
    
    '''    
    _configToStored = {'general':'d_project',
                       'enviornment':'d_env',
                       'animSettings':'d_animSettings'}
    _geoToComponent = {'mesh':'vtx'}
    
    def __init__(self, project = None, filepath = None, **kws):
        """

        """        
        self.str_filepath = None
        self.d_env = cgmGEN.get_mayaEnviornmentDict()
        self.d_env['file'] = mc.file(q = True, sn = True)
        self.d_project = {}
        self.d_animSettings = {}
        
        if filepath is not None:
            try:self.read(filepath)
            except:log.error("Filepath failed to read.")
            
            
        return
        if sourceMesh is not None:
            self.validateSourceMesh(sourceMesh)
        if targetMesh is not None:
            self.validateTargetMesh(targetMesh)
        if sourceMesh is None and targetMesh is None and mc.ls(sl=True):
            self.validateSourceMesh(sourceMesh)            

            
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

    def write(self, filepath = None):
        '''
        Write the Data ConfigObj to file
        '''
        filepath = self.validateFilepath(filepath)
            
        ConfigObj = configobj.ConfigObj(indent_type='\t')
        ConfigObj['configType']= 'cgmProject'
        for k in data._configToStored.keys():
            ConfigObj[k] = self.__dict__[data._configToStored[k]] 
        
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
            
        if report:self.log_self()
        return True
    
    def log_self(self):
        _d = copy.copy(self.__dict__)
        pprint.pprint(_d)
        
        return 
        log.info("Read Data Report "+ cgmGEN._str_hardBreak)
        log.info("Config File: {0}".format(self.str_filepath))
        for k in data._configToStored.keys():
            _d_bfr = self.__dict__[data._configToStored[k]]
            if _d_bfr:
                log.info("{0} ".format(k) + cgmGEN._str_subLine)
                l_keys = _d_bfr.keys()
                l_keys.sort()
                for k1 in l_keys:
                    _bfr = _d_bfr[k1]
                    if isinstance(_bfr,dict):
                        print(">" + "Nested Dict: {0}".format(k1) + cgmGEN._str_subLine)
                        l_bufferKeys = _bfr.keys()
                        l_bufferKeys.sort()
                        for k2 in l_bufferKeys:
                            print("-"*3 +'>' + " {0} : {1} ".format(k2,_bfr[k2]))			
                    else:
                        print(">" + " {0} : {1} ".format(k1,_d_bfr[k1]))                	    
                print(cgmGEN._str_subLine)
        
#>>> Utilities
#===================================================================
