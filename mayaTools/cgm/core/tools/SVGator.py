"""
------------------------------------------
baseTool: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
Example ui to start from
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

#>>> Root settings =============================================================
__version__ = cgmGEN.__RELEASESTRING
__toolname__ ='SVGator'

class ui(cgmUI.cgmGUI):
    USE_Template = 'cgmUITemplate'
    WINDOW_NAME = '{0}_ui'.format(__toolname__)    
    WINDOW_TITLE = '{1} - {0}'.format(__version__,__toolname__)
    DEFAULT_MENU = None
    RETAIN = True
    MIN_BUTTON = True
    MAX_BUTTON = False
    FORCE_DEFAULT_SIZE = True  #always resets the size of the window when its re-created  
    DEFAULT_SIZE = 425,350
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

 
    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))

    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     

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
        

def buildColumn_main(self,parent, asScroll = False):
    """
    Trying to put all this in here so it's insertable in other uis
    
    """   
    if asScroll:
        _inside = mUI.MelScrollLayout(parent,useTemplate = 'cgmUISubTemplate') 
    else:
        _inside = mUI.MelColumnLayout(parent,useTemplate = 'cgmUISubTemplate') 
    
    cgmUI.add_Header('Single')
    
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
    """
    _row_objLoad.layout()

    #>>>Report ---------------------------------------------------------------------------------------
    _row_report = mUI.MelHLayout(_inside ,ut='cgmUIInstructionsTemplate',h=20)
    self.uiField_report = mUI.MelLabel(_row_report,
                                       bgc = SHARED._d_gui_state_colors.get('help'),
                                       label = '...',
                                       h=20)
    _row_report.layout() """
    _row_objLoad.layout()
    uiFunc_load_selected(self)
    
    #>>> Import options ---------------------------------------------------------------------------------------
    _row = mUI.MelHLayout(_inside,ut='cgmUISubTemplate')
    d = ['Extrude & Cull','Trianglulate','Move to Center']
    mUI.MelSpacer(_row,w=5)
    
    for o in d:
        mUI.MelCheckBox(_row,
                        l = o)
                        #annotation = 'Create qss set: {0}'.format(k),
                        #value = self.__dict__[_plug].value,
                        #onCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,1),
                        #offCommand = cgmGEN.Callback(self.__dict__[_plug].setValue,0))    
        mUI.MelSpacer(_row,w=5)
        
    mUI.MelSpacer(_row,w=5)
    _row.layout()
    
    
    
    #>>> ---------------------------------------------------------------------------------------------------
    _mRow = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 10)
    mUI.MelLabel(_mRow,l="  Pivot")
    #_mRow.setStretchWidget(mUI.MelSeparator(_mRow,))            

    _optionMenu = mUI.MelOptionMenu(_mRow,ut = 'cgmUITemplate',h=25)
    mUI.MelSpacer(_mRow,w=10)
    
    _mRow.setStretchWidget(_optionMenu)
    
    self.uiOM_pivot = _optionMenu
    
    for o in ['none','frontCenter','frontBottom']:
        _optionMenu.append(o)
    
    _mRow.layout()
    
    
    mc.setParent(_inside)
    cgmUI.add_LineBreak()    
    cgmUI.add_HeaderBreak()
    
    #>>> Buttons --------------------------------------------------------------------------------------------
    _row_base = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mc.button(parent=_row_base,
              l = 'Import',
              ut = 'cgmUITemplate',
              #c = lambda *a:SNAPCALLS.snap_action(None,'point'),
              ann = "Point snap in a from:to selection")

    mc.button(parent=_row_base,
              l = 'Export',
              ut = 'cgmUITemplate',                    
              #c = lambda *a:SNAPCALLS.snap_action(None,'closestPoint'),
              ann = "Closest point on target")    
    _row_base.layout()     
    
    #Batch ===================================================================================================
    mc.setParent(_inside)    
    cgmUI.add_Header('Batch')
    
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
               triangulate = True,extrudeAndCull=True):
    reload(CORESTRINGS)
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
    for i,m in enumerate(materials):
        if matName:
            _wanted = matName
        else:
            _wanted = ('{}_{}_MAT'.format(_name,i))
        if mc.objExists(_wanted):
            mc.delete(_wanted)
            
        mMat = cgmMeta.asMeta(m)
        mMat.rename(_wanted)
        ml_mats.append(mMat)
    
    _res = [mMesh,mSVG,ml_mats]
    pprint.pprint(_res)
    return _res
    
 