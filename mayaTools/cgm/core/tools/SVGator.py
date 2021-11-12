"""
------------------------------------------
SVGator: cgm.core.tools
Author: Josh Burton
email: cgmonks.info@gmail.com

------------------------------------------

================================================================
"""
# From Python =============================================================
import copy
import re
import time
import pprint
import os
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import maya.mel as mel
import maya.cmds as mc

import cgm.core.classes.GuiFactory as cgmUI
from cgm.core import cgm_RigMeta as cgmRigMeta
mUI = cgmUI.mUI

from cgm.core.lib import shared_data as SHARED
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
import cgm.core.lib.transform_utils as TRANS
from cgm.core.cgmPy import path_Utils as CGMPATH
import cgm.core.lib.math_utils as MATH
from cgm.lib import lists
import cgm.core.cgmPy.os_Utils as cgmOS
import cgm.core.lib.position_utils as POS
import cgm.core.lib.geo_Utils as GEO
import cgm.core.lib.string_utils as CORESTRINGS
import cgm.core.lib.shared_data as CORESHARE
import cgm.core.cgmPy.os_Utils as CGMOS

log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start

#>>> Root settings =============================================================
__version__ = cgmGEN.__RELEASESTRING
__toolname__ ='SVGator'
_colorGood = CORESHARE._d_colors_to_RGB['greenWhite']
_colorBad = CORESHARE._d_colors_to_RGB['redWhite']

d_importOptions = {'ExtrudeCull':{'ann':'Extrude and cull to get a clean flat front'},
                   'Triangulate':{'s':'Triangulate','ann':'Triangulate the mesh'},
                   'MoveToCenter':{'s':'Center','ann':'Move to world center'},
                   'Viewport':{'ann':'Change viewport options'}}

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = '{0}_ui'.format(__toolname__)    
    WINDOW_TITLE = '{1} - {0}'.format(__version__,__toolname__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 425,275
    TOOLNAME = '{0}.ui'.format(__toolname__)
    
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
        
        self.uiCB_d = {}
        self.uiTF = {}
 
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     
        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="SVG Viewport",
                         c = lambda *a:uiButton_setViewportShading())

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #self._d_uiCheckBoxes = {}
    
        #_MainForm = mUI.MelFormLayout(parent,ut='cgmUISubTemplate')
        _MainForm = mUI.MelFormLayout(self,ut='cgmUITemplate')
        _column = buildColumn_main(self,_MainForm,True)

    
        _row_cgm = cgmUI.add_cgmFooter(_MainForm)            
        _MainForm(edit = True,
                  af = [(_column,"top",0),
                        (_column,"left",0),
                        (_column,"right",0),                        
                        (_row_cgm,"left",0),
                        (_row_cgm,"right",0),                        
                        (_row_cgm,"bottom",0),
    
                        ],
                  ac = [(_column,"bottom",2,_row_cgm),
                        ],
                  attachNone = [(_row_cgm,"top")])
        
    def uiFunc_importSVG(self):
        str_func = 'data.uiFunc_importSVG'
        log.debug(log_start(str_func))
        
        self.uiFunc_viewportLighting()
        
        _startDir = self.uiTF['source'].getValue()
        if not os.path.exists(_startDir):
            log.warning("Invalid source path: {}".format(_startDir))            
            _startDir = False
        
        _path = VALID.filepath(None, fileMode =1, fileFilter='SVG File (*.svg)',startDir=_startDir)
        if not _path:
            log.warning("No file specified")                        
            return
        
        d_options = {}
        d_options['pivotMode'] = self.uiOM_pivot.getValue()
        d_options['triangulate'] = self.uiCB_d['Triangulate'].getValue()
        d_options['extrudeAndCull'] = self.uiCB_d['ExtrudeCull'].getValue()
        d_options['moveToCenter'] = self.uiCB_d['MoveToCenter'].getValue()
        
        #pprint.pprint(d_options)

        _res = svg_import(_path,**d_options)
        
        pprint.pprint(_res)
        
    def uiFunc_importBatchSVG(self):
        str_func = 'data.uiFunc_importBatchSVG'
        log.debug(log_start(str_func))
        
        self.uiFunc_viewportLighting()
        
        _startDir = self.uiTF['source'].getValue()
        if not os.path.exists(_startDir):
            log.warning("Invalid source path: {}".format(_startDir))            
            _startDir = False
            
        l = CGMOS.find_files(_startDir,'*.svg')
        pprint.pprint(l)
        
        d_options = {}
        d_options['pivotMode'] = self.uiOM_pivot.getValue()
        d_options['triangulate'] = self.uiCB_d['Triangulate'].getValue()
        d_options['extrudeAndCull'] = self.uiCB_d['ExtrudeCull'].getValue()
        d_options['moveToCenter'] = self.uiCB_d['MoveToCenter'].getValue()        
        
        for f in l:
            try:
                log.info(log_sub(str_func,"File: {}".format(f)))                        
                _res = svg_import(os.path.join(_startDir,f),**d_options)
                pprint.pprint(_res)                  
            except Exception,err:
                log.error(err)            
            
        return
    
    def uiFunc_viewportLighting(self):
        str_func = 'data.uiFunc_importExportBatchSVG'
        log.debug(log_start(str_func))
        
        if self.uiCB_d['Viewport'].getValue():
            uiButton_setViewportShading()
        
    def uiFunc_importExportBatchSVG(self):
        str_func = 'data.uiFunc_importExportBatchSVG'
        log.debug(log_start(str_func))
        
        self.uiFunc_viewportLighting()
        
        _startDir = self.uiTF['source'].getValue()
        if not os.path.exists(_startDir):
            log.warning("Invalid source path: {}".format(_startDir))            
            _startDir = False
            
        l = CGMOS.find_files(_startDir,'*.svg')
        pprint.pprint(l)
        
        d_options = {}
        d_options['pivotMode'] = self.uiOM_pivot.getValue()
        d_options['triangulate'] = self.uiCB_d['Triangulate'].getValue()
        d_options['extrudeAndCull'] = self.uiCB_d['ExtrudeCull'].getValue()
        d_options['moveToCenter'] = self.uiCB_d['MoveToCenter'].getValue()        
        
        ml_mesh = []
        
        for f in l:
            try:
                log.info(log_sub(str_func,"File: {}".format(f)))                        
                _res = svg_import(os.path.join(_startDir,f),**d_options)
                ml_mesh.append(_res[0])
                pprint.pprint(_res)                  
            except Exception,err:
                log.error(err)
        if ml_mesh:
            self.uiFunc_exportSVG(ml_mesh)
            
            
        return    
        

        

        
        #pprint.pprint(d_options)

 
        
    def uiFunc_exportSVG(self, ml = None):
        str_func = 'data.uiFunc_exportSVG'
        log.debug(log_start(str_func))
        
        _export = self.uiTF['export'].getValue()
        if not os.path.exists(_export):
            log.warning("Invalid export path: {}".format(_startDir))            
            return False
        
        if ml == None:
            ml = cgmMeta.asMeta(sl=1,noneValid=True) or False
            
        if not ml:
            return log.error(log_msg(str_func,"Nothing selected"))

        for mObj in ml:
            log.info(log_sub(str_func,"Obj: {}".format(mObj.mNode)))            
            try:
                _nameBase = mObj.p_nameBase
                _nameStrip = mObj.p_nameBase.split('_')[:-1]
                _nameStrip = '_'.join(_nameStrip)
                print _nameStrip
                
                mObj.rename("{}_ORIGINAL".format(_nameBase))
                mExport = mObj.doDuplicate(po=False)
                mExport.rename(_nameBase)
                
                mc.delete(mExport.mNode, ch=1)
                
                mExport.select()            
                
                _exportPath = os.path.normpath( os.path.join(_export, "{}.fbx".format(_nameStrip)) )
                print _exportPath
                
                mel.eval('FBXExport -f \"{}\" -s'.format(_exportPath.replace('\\', '/')))
                mExport.delete()
                
                mObj.rename(_nameBase)
            except Exception,err:
                log.error(err)
        

def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    cgmUI.add_Header('Single')
    """
    #>>>Objects Load Row ---------------------------------------------------------------------------------------
    _row_objLoad = mUI.MelHSingleStretchLayout(_inside,ut='cgmUITemplate',padding = 5)        

    mUI.MelSpacer(_row_objLoad,w=10)
    mUI.MelLabel(_row_objLoad, 
                 l='Source:')

    uiTF_objLoad = mUI.MelLabel(_row_objLoad,ut='cgmUITemplate',l='',
                                en=True)

    self.uiTF_objLoad = uiTF_objLoad
    cgmUI.add_Button(_row_objLoad,'<<',
                     cgmGEN.Callback(uiFunc_load_selected,self),
                     "Load first selected object.")  
    _row_objLoad.setStretchWidget(uiTF_objLoad)
    mUI.MelSpacer(_row_objLoad,w=10)

    _row_objLoad.layout()
    uiFunc_load_selected(self)
    """
    for key in ['source','export']:
        _plug = 'var_path_{0}'.format(key)
        try:self.__dict__[_plug]
        except:self.create_guiOptionVar('path_{0}'.format(key),defaultValue = '')             
        
        mUI.MelSeparator(_inside,ut='cgmUISubTemplate',h=3)
        
        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                          
        mUI.MelLabel(_row,l='{0}: '.format(CORESTRINGS.capFirst(key)))
        
        self.uiTF[key] =  mUI.MelTextField(_row,
                                           text = self.__dict__[_plug].getValue(),
                                           ann='Local Path | {0}'.format(key),
                                           #cc = cgmGEN.Callback(uiCC_checkPath,self,key,'local'),)
                                           )
        _row.setStretchWidget( self.uiTF[key] )
        
        mc.button(parent=_row,
                  l = 'Set',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiButton_setPathToTextField,self,key,self.uiTF),
                  )
        mc.button(parent=_row,
                  l = 'Explorer',
                  ut = 'cgmUITemplate',
                  c = cgmGEN.Callback(uiButton_openPath,self,key,self.uiTF),
                  )        
        mUI.MelSpacer(_row,w=5)                                  
        _row.layout()
        
           
    
    
    #>>> Import options ---------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate')
    mUI.MelSpacer(_row,w=1)
    
    mUI.MelLabel(_row,l="  Options:")
    _row.setStretchWidget(mUI.MelSeparator(_row,w=10))
    
    for o,d in d_importOptions.iteritems():
        _plug = 'var_{0}'.format(o)
        try:self.__dict__[_plug]
        except:self.create_guiOptionVar('{0}'.format(o),defaultValue = 1)
        
        cb = mUI.MelCheckBox(_row,
                             l = d.get('s',o),
                             annotation = d.get('ann'),
                             value = self.__dict__[_plug].value,
                             onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                             offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))
        self.uiCB_d[o] = cb
        #mUI.MelSpacer(_row,w=5)
        
    mUI.MelSpacer(_row,w=1)
    _row.layout()
    
    
    
    #>>> ---------------------------------------------------------------------------------------------------

    
    _mRow = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 10)
    mUI.MelLabel(_mRow,l="  Pivot:")
    #_mRow.setStretchWidget(mUI.MelSeparator(_mRow,))            

    _optionMenu = mUI.MelOptionMenu(_mRow,ut = 'cgmUITemplate',h=25)
    mUI.MelSpacer(_mRow,w=10)
    
    _mRow.setStretchWidget(_optionMenu)
    
    self.uiOM_pivot = _optionMenu
    
    _plug = 'var_pivot'
    try:self.__dict__[_plug]
    except:self.create_guiOptionVar('pivot'.format(o),defaultValue = 'frontBottom')
    
    for o in ['none','frontCenter','frontBottom']:
        _optionMenu.append(o)
    
    _optionMenu.selectByValue(self.__dict__[_plug].value)
    _mRow.layout()
    
    
    mc.setParent(_inside)
    mUI.MelSpacer(_inside,h=5)
    #cgmUI.add_HeaderBreak()
    #mUI.MelSpacer(_inside,h=5)
    
    #>>> Buttons --------------------------------------------------------------------------------------------
    _row_base = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mc.button(parent=_row_base,
              l = 'Import',
              ut = 'cgmUITemplate',
              c = lambda *a:self.uiFunc_importSVG(),
              ann = "Import SVG")

    mc.button(parent=_row_base,
              l = 'Export',
              ut = 'cgmUITemplate',
              c = lambda *a:self.uiFunc_exportSVG(),              
              #c = lambda *a:SNAPCALLS.snap_action(None,'closestPoint'),
              ann = "Export SVG")    
    _row_base.layout()     
    
    #Batch ===================================================================================================
    mc.setParent(_inside)    
    cgmUI.add_Header('Batch')
    mUI.MelSpacer(_inside,h=5)
    _row_base = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mc.button(parent=_row_base,
              l = 'Import all SVG',
              ut = 'cgmUITemplate',
              c = lambda *a:self.uiFunc_importBatchSVG(),              
              #c = lambda *a:SNAPCALLS.snap_action(None,'closestPoint'),
              ann = "Batch import SVGs from path")    
    _row_base.layout()      
    
    
    mUI.MelSpacer(_inside,h=5)
    
    _row_base = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mc.button(parent=_row_base,
              l = 'Import/Export All',
              ut = 'cgmUITemplate',
              c = lambda *a:self.uiFunc_importExportBatchSVG(),              
              #c = lambda *a:SNAPCALLS.snap_action(None,'closestPoint'),
              ann = "Batch import/export SVGs from path")    
    _row_base.layout()
    
    mUI.MelSpacer(_inside,h=5)
    """
    _row_base = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mc.button(parent=_row_base,
              l = 'ViewPort Shading',
              ut = 'cgmUITemplate',
              c = lambda *a:uiButton_setViewportShading(),              
              #c = lambda *a:SNAPCALLS.snap_action(None,'closestPoint'),
              ann = "Change viewport options")    
    _row_base.layout()    """          
    
    return _inside
    
def uiFunc_load_selected(self, bypassAttrCheck = False):
    _str_func = 'uiFunc_load_selected'  
    #self._ml_ = []
    self._mTransformTarget = False

    _sel = mc.ls(sl=True,type='transform')

    #Get our raw data
    if _sel:
        mNode = cgmMeta.validateObjArg(_sel[0])
        _short = mNode.p_nameBase            
        log.debug("|{0}| >> Target: {1}".format(_str_func, _short))
        self._mTransformTarget = mNode

        uiFunc_updateTargetDisplay(self)
    else:
        log.warning("|{0}| >> Nothing selected.".format(_str_func))            
        uiFunc_clear_loaded(self)

    #uiFunc_updateFields(self)
    #self.uiReport_do()
    #self.uiFunc_updateScrollAttrList()

def uiFunc_clear_loaded(self):
    _str_func = 'uiFunc_clear_loaded'  
    self._mTransformTarget = False
    #self._mGroup = False
    self.uiTF_objLoad(edit=True, l='',en=False)      
    #self.uiField_report(edit=True, l='...')
    #self.uiReport_objects()
    #self.uiScrollList_parents.clear()
    
    #for o in self._l_toEnable:
        #o(e=True, en=False)  
     
def uiFunc_updateTargetDisplay(self):
    _str_func = 'uiFunc_updateTargetDisplay'  
    #self.uiScrollList_parents.clear()

    if not self._mTransformTarget:
        log.info("|{0}| >> No target.".format(_str_func))                        
        #No obj
        self.uiTF_objLoad(edit=True, l='',en=False)
        self._mGroup = False

        #for o in self._l_toEnable:
            #o(e=True, en=False)
        return
    
    _short = self._mTransformTarget.p_nameBase
    self.uiTF_objLoad(edit=True, ann=_short)
    
    if len(_short)>20:
        _short = _short[:20]+"..."
    self.uiTF_objLoad(edit=True, l=_short)   
    
    self.uiTF_objLoad(edit=True, en=True)
    
    return



def svg_import(path=None, pivotMode = 'frontCenter',
               extrudeDepth = None,
               matName = 'UnlitVertexColor',
               moveToCenter = True, 
               triangulate = True,extrudeAndCull=True):
    _name = os.path.split(path)[-1]
    _name = _name.replace('.svg','')
    _name = CORESTRINGS.stripInvalidChars(_name)
    
    #Import our file....then we need to find all the nodes because maya is stupid
    _i = 0
    _nameGroup = 'SVGIMPORT_{0}'.format(_i)
    while mc.objExists(_nameGroup):
        _i +=1
        _nameGroup = 'IMPORT_{0}'.format(_i)    
    
    mc.file(path, i=True, type='SVG',gn=_nameGroup,gr=True)
    
    mGroup = cgmMeta.asMeta(_nameGroup)
    mMesh = mGroup.getChildren(asMeta=1)[0]
    mMesh.p_parent = False
    mGroup.delete()
    
    
    mMesh.rename('{}_geo'.format(_name))
    
    
    #SVG ====================================================================================
    mSVG = cgmMeta.asMeta(mc.listConnections("{}.msg".format(mMesh.mNode)))[0]
    
    mSVG.curveResolution = 8
    mSVG.enableExtrusion = 0#...
    
    mSVG.rename('{}_SVG'.format(_name))
    
    #Pivot ==================================================================================
    if pivotMode == 'frontCenter':
        p = POS.get_bb_pos(mMesh.mNode,False,'z+')
        TRANS.rotatePivot_set(mMesh.mNode, p)
        TRANS.scalePivot_set(mMesh.mNode, p)
    elif pivotMode == 'frontBottom':
        p = POS.get_bb_pos(mMesh.mNode,False,'z+')
        p2 = POS.get_bb_pos(mMesh.mNode,False,'y-')
        pNew = [p[0],p2[1],p[2]]
        TRANS.rotatePivot_set(mMesh.mNode, pNew)
        TRANS.scalePivot_set(mMesh.mNode, pNew)
        
    if moveToCenter:
        mMesh.p_position = 0,0,0
    mc.makeIdentity(mMesh.mNode,apply=True,translate =True, rotate = True, scale=True)
    
    
    
    
    #Trianglulate =================================================================================
    if triangulate:
        mc.polyTriangulate(mMesh.mNode)
    
    #Cleanup back geo =============================================================================
    if extrudeAndCull:
        bb_size = TRANS.bbSize_get(mMesh.mNode)
        bb_size = [x*1.2 for x in bb_size]
        mBox = cgmMeta.asMeta( mc.polyCube(depth= bb_size[2],width=bb_size[0], height = bb_size[1], ch=False) )[0]
        mBox.p_position = POS.get_bb_pos(mMesh.mNode,False,'z-')
        
        GEO.get_proximityGeo(mBox.mNode,[mMesh.mNode],returnMode=1)
        mel.eval("PolySelectTraverse 1;")
        mc.delete()
        
        mBox.delete()
    
    #Mats =======================================================================================
    shadeEng = mc.listConnections(mMesh.getShapes()[0] , type = 'shadingEngine')
    materials = mc.ls(mc.listConnections(shadeEng ), materials = True) 
    ml_mats = []
    
    if matName and mc.objExists(matName):
        mMat = cgmMeta.asMeta(matName)
        
        sets = mc.ls(mc.listConnections(mMat.mNode ), sets = True)        
        mc.sets(mMesh.mNode, edit=True, forceElement = sets[0])
        mc.sets(mMesh.mNode, remove = 'initialShadingGroup')
        
        ml_mats.append(mMat)
        
        
    else:
        for i,m in enumerate(materials):
            if matName:
                _wanted = matName
            else:
                _wanted = ('{}_{}_MAT'.format(_name,i))
                            
            mMat = cgmMeta.asMeta(m)
    
            
            if not mc.objExists(_wanted):
                mMat.rename(_wanted)
                
            ml_mats.append(mMat)
    
    
    _res = [mMesh,mSVG,ml_mats]
    pprint.pprint(_res)
    return _res
    
def uiButton_setPathToTextField(self,key,d_fields, mode='project'):
    basicFilter = "*"
    if key in ['image','scriptUI']:
        x = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=1)
    else:
        x = mc.fileDialog2(fileFilter=basicFilter, dialogStyle=2, fm=3)
        
    if x:
        _plug = 'var_path_{0}'.format(key)
        try:self.__dict__[_plug]
        except:self.create_guiOptionVar('{0}'.format(key),defaultValue = '')        
        
        mField = d_fields[key]
        if not os.path.exists(x[0]):
            mField(edit=True,bgc = _colorBad)
            raise ValueError,"Invalid path: {0}".format(x[0])
        
        mField.setValue( x[0] )
        mField(edit=True,bgc = _colorGood) 
        self.__dict__[_plug].value = mField.getValue()
        
def uiButton_openPath(self,key,d_fields):
    mField = d_fields[key]
    _path = mField.getValue()
    if not os.path.exists(_path):
        raise ValueError,"Invalid path: {0}".format(_path)
    os.startfile(_path)
    

def uiButton_setViewportShading():
    str_func = 'uiButton_setViewportShading'
    log.debug(log_start(str_func))
    
    _panel = mc.getPanel( withFocus = True)
    try:
        #print _panel
        mc.modelEditor( _panel, edit = True, dl = 'flat',displayAppearance = 'flatShaded', interactiveBackFaceCull = True, activeOnly = False)
        mc.ogs(reset=True)
        #mel.eval('dR_setModelEditorTypes;')
        
        #mc.modelEditor( _panel, edit = True, displayAppearance = 'flatShaded',activeOnly = False)
        #print  mc.modelEditor( _panel, q = True, displayAppearance = True)
        #mc.modelEditor( _panel, edit = True, interactiveBackFaceCull=True,activeOnly = False)
        #print  mc.modelEditor( _panel, q = True, interactiveBackFaceCull = True)
        #mc.modelEditor( _panel, edit = True, dl = 'flat',activeOnly = False)
        #print  mc.modelEditor( _panel, q = True, dl = True)        
    except Exception,err:
        log.error(err)
    
