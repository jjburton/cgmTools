"""
------------------------------------------
jointTools: cgm.core.tools
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------


Huge thank you to Michael Comet for the original cometJointOrient tool
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

import maya.cmds as mc
import maya.mel as mel

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta

import cgm.core.rig.joint_utils as JOINTS
import cgm.core.lib.shared_data as SHARED
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.rigging_utils as RIGGING
import cgm.core.tools.markingMenus.lib.contextual_utils as MMCONTEXT
import cgm.core.lib.curve_Utils as CURVES
import cgm.core.lib.transform_utils as TRANS
import cgm.core.tools.lib.tool_chunks as UICHUNKS
import cgm.core.lib.position_utils as POS
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.tools.lib.annotations as TOOLANNO

#>>> Root settings =============================================================
__version__ = '0.10162017'
__toolname__ ='cgmJointTools'

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
        self.uiPopUpMenu_raycastCreate = None
        self.WINDOW_TITLE = self.__class__.WINDOW_TITLE
        self.DEFAULT_SIZE = self.__class__.DEFAULT_SIZE

    def build_menus(self):
        self.uiMenu_FirstMenu = mUI.MelMenu(l='Setup', pmc = cgmGEN.Callback(self.buildMenu_first))
        
    def uiPopup_createRayCast(self):
        if self.uiPopUpMenu_raycastCreate:
            self.uiPopUpMenu_raycastCreate.clear()
            self.uiPopUpMenu_raycastCreate.delete()
            self.uiPopUpMenu_raycastCreate = None
    
        self.uiPopUpMenu_raycastCreate = mUI.MelPopupMenu(self.uiField_rayCastCreate,button = 1)
        _popUp = self.uiPopUpMenu_raycastCreate 
    
        mUI.MelMenuItem(_popUp,
                        label = "Set Create Type",
                        en=False)     
        mUI.MelMenuItemDiv(_popUp)
    
        for m in  ['locator','joint','jointChain','curve','duplicate','vectorLine','data']:
            mUI.MelMenuItem(_popUp,
                            label = m,
                            ann = "Create {0} by rayCasting".format(m),
                            c=cgmGEN.Callback(self.cb_setRayCastCreate,m))
    def cb_setRayCastCreate(self,m):
        self.var_createRayCast.setValue(m)
        self.uiField_rayCastCreate(edit=True,label=m)
        return True
    
    def buildMenu_first(self):
        self.uiMenu_FirstMenu.clear()
        #>>> Reset Options		                     
        
        UICHUNKS.uiOptionMenu_contextTD(self, self.uiMenu_FirstMenu)
        
        mc.menuItem(parent=self.uiMenu_FirstMenu, 
                    l = 'Dat Preview',
                    c=lambda *a:uiFunc_getCreateData(self,True))        

        mUI.MelMenuItemDiv( self.uiMenu_FirstMenu )

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reload",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))

        mUI.MelMenuItem( self.uiMenu_FirstMenu, l="Reset",
                         c = lambda *a:mc.evalDeferred(self.reload,lp=True))
        
    def build_layoutWrapper(self,parent):
        _str_func = 'build_layoutWrapper'
        #self._d_uiCheckBoxes = {}
    
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
        
    self.var_contextTD = cgmMeta.cgmOptionVar('cgmVar_contextTD', defaultValue = 'selection')
    self.var_jointAimAxis = cgmMeta.cgmOptionVar('cgmVar_jointDefaultAimAxis', defaultValue = 2)
    self.var_jointUpAxis = cgmMeta.cgmOptionVar('cgmVar_jointDefaultUpAxis', defaultValue = 1)
    
    
    self.uiPB_cgmJointTools = mc.progressBar(vis=False)
    
    mc.setParent(_inside)    
    cgmUI.add_Header('Orient')
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()    
    #Orient ==================================================================================================    
    
    #>>>Tweak -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row ,w=5)

    mUI.MelLabel(_row ,l='Tweak:')        
    _row.setStretchWidget(mUI.MelSeparator(_row )) 
    _base_str = 'uiFF_orientTweak'
    
    #self._d_transformAttrFields[label] = {}
    #self._d_transformRows[label] = _row
    
    for a in list('xyz'):
        mUI.MelLabel(_row ,l=a)
        _field = mUI.MelFloatField(_row , ut='cgmUISubTemplate', w= 50 )
        self.__dict__['{0}{1}'.format(_base_str,a.capitalize())] = _field          

    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = ' + ',
              c = cgmGEN.Callback(uiFunc_tweak,self,'+'),
              ann = "Adds value relatively to current") 
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = ' - ',
              c = cgmGEN.Callback(uiFunc_tweak,self,'-'),
              ann = "Subracts value relatively to current")         
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Zero',
              c = cgmGEN.Callback(uiFunc_tweak,self,'zero'),
              ann = "Zero out the fields.") 
    
    mUI.MelSpacer(_row ,w=5)                                              
    _row.layout()     
    
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    #mUI.MelSeparator(_inside)
    
    buildRow_worldUp(self,_inside)
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    buildRow_getVector(self,_inside)    
    
    
    #>>>Aim mode -------------------------------------------------------------------------------------
    _d = {'aim':self.var_jointAimAxis,
          'up':self.var_jointUpAxis}

    for k in _d.keys():
        _var = _d[k]

        _row = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)

        mUI.MelSpacer(_row,w=5)                      
        mUI.MelLabel(_row,l='{0}:'.format(k))
        _row.setStretchWidget( mUI.MelSeparator(_row) )

        uiRC = mUI.MelRadioCollection()
        _on = _var.value

        for i,item in enumerate(SHARED._l_axis_by_string):
            if i == _on:
                _rb = True
            else:_rb = False

            uiRC.createButton(_row,label=item,sl=_rb,
                              onCommand = cgmGEN.Callback(_var.setValue,i))

            mUI.MelSpacer(_row,w=2)       
        _row.layout()     
        
    #mUI.MelSeparator(_inside)
    
    #>>Orient Row -------------------------------------------------------------------------------
    _row_orient = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding=5)
    mc.button(parent=_row_orient ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Orient Selected',
              c = cgmGEN.Callback(orientJoints,self),
              ann = "Orient selected joints")
    
    mc.button(parent=_row_orient ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Plane Up',
              c = cgmGEN.Callback(orientPlane,self,'up'),
              ann = "Orient selected joints along up plane of joints. Most useful for fingers and things like that")
    mc.button(parent=_row_orient ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Plane Out',
              c = cgmGEN.Callback(orientPlane,self,'out'),
              ann = "Orient selected joints along out plane of joints. Most useful for fingers and things like that")
    
    mc.button(parent=_row_orient, 
              ut = 'cgmUITemplate',                                                                              
              l = 'Freeze',
              ann = "Freeze selected joint's orientation - our method as we don't like Maya's",                                        
              c = cgmGEN.Callback(MMCONTEXT.func_process, JOINTS.freezeOrientation, None, 'each','freezeOrientation',False,**{}),                                                                      
              )    
    _row_orient.layout()
    mc.setParent(_inside)    
    cgmUI.add_LineSubBreak()
        
    
    #Create ==================================================================================================
    mc.setParent(_inside)    
    cgmUI.add_Header('Create')
    
    #>>>Options Row ---------------------------------------------------------------------------------------
    _row_createOptions = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_createOptions,w=2)           
    mUI.MelLabel(_row_createOptions,l='Resplit:')
    
    self.create_guiOptionVar('splitMode',defaultValue = 0) 
    
    uiRC = mUI.MelRadioCollection()
    _on = self.var_splitMode.value

    for i,item in enumerate(['none','linear','curve','sub']):
        if i == _on:
            _rb = True
        else:_rb = False

        uiRC.createButton(_row_createOptions,label=item,sl=_rb,
                          onCommand = cgmGEN.Callback(self.var_splitMode.setValue,i))

        #mUI.MelSpacer(_row_createOptions,w=2)       
    _row_createOptions.setStretchWidget( mUI.MelSeparator(_row_createOptions) )

    self.uiIF_cnt = mUI.MelIntField(_row_createOptions ,  value = 3, ut='cgmUISubTemplate', w= 30 )
    mUI.MelLabel(_row_createOptions,l='#')    
    
    mUI.MelSpacer(_row_createOptions,w=2)       

    _row_createOptions.layout()              
    
    #>>>Create Buttons Row ---------------------------------------------------------------------------------------
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()    
    _row_create = mUI.MelHSingleStretchLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row_create,w=2)
    
    self.uiCB_orient = mUI.MelCheckBox(_row_create,en=True,l='Orient',
                                       value =True,
                                       ann='Orient created joints')
    
    self.uiCB_chain = mUI.MelCheckBox(_row_create,en=True,l='Chain',
                                      value = True,
                                      ann='Parent created joints as a chain')
    
    self.uiCB_relative = mUI.MelCheckBox(_row_create,en=True,l='Relative',
                                         value = False,
                                         ann='Relative orient where the chain orientation is relative to the parent')
    
    _row_create.setStretchWidget( mUI.MelSeparator(_row_create) )
    
    #mUI.MelLabel(_row_create,l='From Selected:')    
    mc.button(parent=_row_create, 
              ut = 'cgmUITemplate',                                                                              
              l = 'From Selected',
              c=cgmGEN.Callback(createJoints,self,'each'),
              #ann = "Show the joint axis by current context",                                        
              #c= lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',1,self.var_contextTD.value,'joint',select=False),
              )
    mc.button(parent=_row_create, 
              ut = 'cgmUITemplate',                                                                              
              l = 'Mid',
              c = cgmGEN.Callback(MMCONTEXT.func_process, RIGGING.create_at, None,'all','Create Joint at mid',**{'create':'joint','midPoint':'True'}),         
              ann = 'Create a joint at the mid point of selected',
              )
    mc.button(parent=_row_create, 
              ut = 'cgmUITemplate',                                                                              
              l = 'Curve',
              c=cgmGEN.Callback(createJoints,self,'curve'),
              #ann = "Show the joint axis by current context",                                        
              #c= lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',1,self.var_contextTD.value,'joint',select=False),
              )

    mUI.MelSpacer(_row_create,w=2)    
    _row_create.layout()              
    
    if asScroll:
        #Axis ==================================================================================================    
        mc.setParent(_inside)    
        cgmUI.add_Header('Raycast')    
        mc.setParent(_inside)
        cgmUI.add_LineSubBreak()
        
        UICHUNKS.uiChunk_rayCast(self,_inside)
        
    #Axis ==================================================================================================    
    mc.setParent(_inside)    
    cgmUI.add_Header('Axis')    
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    
    #>>>Axis Show Row ---------------------------------------------------------------------------------------
    _row_axis = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mc.button(parent=_row_axis, 
              ut = 'cgmUITemplate',                                                                              
              l = '* Show',
              ann = "Show the joint axis by current context",                                        
              c= lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',1,self.var_contextTD.value,'joint',select=False),
              )

    mc.button(parent=_row_axis, 
              ut = 'cgmUITemplate',                                                                              
              l = '* Hide',
              ann = "Hide the joint axis by current context",                                        
              c= lambda *a:MMCONTEXT.set_attrs(self,'displayLocalAxis',0,self.var_contextTD.value,'joint',select=False),
              )     

    _row_axis.layout()            

    #Axis ==================================================================================================    
    mc.setParent(_inside)    
    cgmUI.add_Header('Radius')    
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()
    _row_radius = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    mc.button(parent = _row_radius,
              ut = 'cgmUITemplate',                                                                                                
              l=' / 2 ',
              c=lambda *a: radius_modify(self,'/',2),
              ann="Contextual radius editing")
    mc.button(parent = _row_radius,
              ut = 'cgmUITemplate',                                                                                                
              l=' - 10',
              c=lambda *a: radius_modify(self,'-',10),
              ann="Contextual radius editing")
    mc.button(parent = _row_radius,
              ut = 'cgmUITemplate',                                                                                                
              l='- 1',
              c=lambda *a: radius_modify(self,'-',1),
              ann="Contextual radius editing")
    mc.button(parent = _row_radius,
              ut = 'cgmUITemplate',                                                                                                
              l='+ 1',
              c=lambda *a: radius_modify(self,'+',1),
              ann="Contextual radius editing")
    mc.button(parent = _row_radius,
              ut = 'cgmUITemplate',                                                                                                
              l='+10',
              c=lambda *a: radius_modify(self,'+',10),
              ann="Contextual radius editing")
    mc.button(parent = _row_radius,
              ut = 'cgmUITemplate',                                                                                                
              l='*2',
              c=lambda *a: radius_modify(self,'*',2),
              ann="Contextual radius editing")
    _row_radius.layout()    
    
    
    
    #Utilities ==================================================================================================
    mc.setParent(_inside)    
    cgmUI.add_Header('Utilities')
    mc.setParent(_inside)
    cgmUI.add_LineSubBreak()    
    
  
    #Buttons ----------------------------------------------------------------------------------------------
    _row_utils = mUI.MelHLayout(_inside,ut='cgmUISubTemplate',padding = 5)
    
    mc.button(parent = _row_utils,
              ut = 'cgmUITemplate',                                                                                                
              l='cometJO',
              c=lambda *a: mel.eval('cometJointOrient'),
              ann="General Joint orientation tool  by Michael Comet")   
    mc.button(parent = _row_utils,
              ut = 'cgmUITemplate',                                                                                                
              l='* Select',
              c=lambda *a: contextual_select(self),
              ann="Contextual joint selection")        
    mc.button(parent = _row_utils,
              ut = 'cgmUITemplate',                                                                                                
              l='seShapeTaper',
              ann = "Fantastic blendtaper like tool for sdk poses by our pal - Scott Englert",                                                        
              c=lambda *a: mel.eval('seShapeTaper'),)   
    _row_utils.layout()
    
    
    return _inside


def contextual_select(self):
    _str_func = 'contextual_select'    
    
    _sel = MMCONTEXT.get_list(self.var_contextTD.value,'joint')
    if not _sel:
        return log.error("|{0}| >> Nothing in context: {1}".format(_str_func,self.var_contextTD.value))
    mc.select(_sel)
    return _sel

def radius_modify(self,mode='+',factor=10):
    _str_func = 'radius_modify'    
    
    _sel = MMCONTEXT.get_list(self.var_contextTD.value,'joint')
    if not _sel:
        return log.error("|{0}| >> Nothing selected".format(_str_func))
    
    for j in _sel:
        _r = ATTR.get(j,'radius')
        if mode == '+':
            _r = _r + factor
        elif mode == '-':
            _r = _r - factor
        elif mode == '*':
            _r = _r * factor
        elif mode == '/':
            _r = _r / factor
            
        ATTR.set(j,'radius',_r)
        
    
def createJoints(self, mode = 'each'):
    _str_func = 'createJoints'
    
    _d = uiFunc_getCreateData(self)
    
    _sel = MMCONTEXT.get_list()
    if not _sel:
        return log.error("|{0}| >> Nothing selected".format(_str_func))
    
    _resplit = _d['resplit']    
    _splitMode = ['linear','curve','sub'][_d['resplit']-1]
    
    if mode != 'curve':
        if _splitMode == 'sub':
            if len(_sel) == 1:
                _buffer = mc.listRelatives(_sel[0],type='joint')
                if _buffer:
                    _sel.append(_buffer[0])
        elif len(_sel) < 2:
            return log.error("|{0}| >> Need more objects for resplitting 'each' mode. ".format(_str_func))
        
    log.info("|{0}| >> mode: {1}".format(_str_func,mode))        
    mc.select(cl=True)
    #pprint.pprint(_sel)
    
    if mode == 'curve':
        for o in _sel:
            mObj = cgmMeta.validateObjArg(o,'cgmObject')
            for mShape in mObj.getShapes(asMeta=True):
                _type = mShape.getMayaType() 
                if _type == 'nurbsCurve':
                    
                    JOINTS.build_chain(curve=mShape.mNode,
                                       axisAim=_d['aim'],axisUp=_d['up'],
                                       worldUpAxis=_d['world'],count=_d['count'],splitMode='curveCast',
                                       parent=_d['parent'],
                                       orient=_d['orient'],
                                       progressBar=self.uiPB_cgmJointTools,
                                       relativeOrient=_d['relativeOrient'])
                else:
                    log.warning("|{0}| >> shape: {1} | invalid type: {2}".format(_str_func,mShape.mNode,_type))        
                    
    elif mode == 'each':
        #posList = [POS.get(o) for o in _sel]
        if not _resplit:
            log.info("|{0}| >> No resplit...".format(_str_func))                                
            JOINTS.build_chain(targetList=_sel,
                               axisAim=_d['aim'],axisUp=_d['up'],
                               worldUpAxis=_d['world'],
                               parent=_d['parent'],
                               orient=_d['orient'],
                               progressBar=self.uiPB_cgmJointTools,                               
                               relativeOrient=_d['relativeOrient'])
        else:
            log.info("|{0}| >> resplit...".format(_str_func))                    
            if _splitMode == 'sub':
                count=_d['count'] #+ len(_sel)
            else:
                count = _d['count'] 
                
            JOINTS.build_chain(targetList=_sel,
                               axisAim=_d['aim'],axisUp=_d['up'],
                               worldUpAxis=_d['world'],count=count,
                               splitMode=_splitMode,
                               parent=_d['parent'],
                               orient=_d['orient'],
                               progressBar=self.uiPB_cgmJointTools,                               
                               relativeOrient=_d['relativeOrient'])
        
    else:
        raise ValueError,"Unknown mode: {0}".format(mode)
    mc.select(_sel)
    
    
def orientJoints(self):
    _str_func = 'orientJoints'
    
    _d = uiFunc_getCreateData(self)
    
    _sel = MMCONTEXT.get_list()
    if not _sel:
        return log.error("|{0}| >> Nothing selected".format(_str_func))
    
    #pprint.pprint(_sel)
    
    JOINTS.orientChain(_sel,axisAim=_d['aim'],
                       axisUp=_d['up'],
                       worldUpAxis=_d['world'],
                       progressBar=self.uiPB_cgmJointTools,                                                      
                       relativeOrient=_d['relativeOrient'])
    mc.select(_sel)

def orientPlane(self,planarMode = 'up'):
    _str_func = 'orientPlane'
    
    _d = uiFunc_getCreateData(self)
    
    _sel = MMCONTEXT.get_list()
    if not _sel:
        return log.error("|{0}| >> Nothing selected".format(_str_func))
    
    #pprint.pprint(_sel)
    
    JOINTS.orientByPlane(_sel,axisAim=_d['aim'],
                       axisUp=_d['up'],
                       worldUpAxis=_d['world'],
                       planarMode=planarMode,
                       progressBar=self.uiPB_cgmJointTools,                                                      
                       relativeOrient=_d['relativeOrient'])
    mc.select(_sel)


def uiFunc_getOrientData(self):
    _d = {}
    _d['aim'] = SHARED._l_axis_by_string[self.var_jointAimAxis.value]
    _d['up'] = SHARED._l_axis_by_string[self.var_jointUpAxis.value]
    
    _d['world'] = [self.uiFF_worldUpX.getValue(),
                   self.uiFF_worldUpY.getValue(),
                   self.uiFF_worldUpZ.getValue()]
    return _d

def uiFunc_getCreateData(self,report=False):
    _d = {}
    _d['resplit'] = self.var_splitMode.value
    _d['orient'] = self.uiCB_orient.getValue()
    _d['parent'] = self.uiCB_chain.getValue()
    _d['count'] = self.uiIF_cnt.getValue()
    _d['relativeOrient'] = self.uiCB_relative.getValue()
    _d.update(uiFunc_getOrientData(self))
    if report:pprint.pprint(_d)
    return _d

    
def buildRow_worldUp(self,parent):
    #>>>Vector -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)
    mUI.MelSpacer(_row ,w=5)                                              
    mUI.MelLabel(_row ,l='World:')        
    _row.setStretchWidget(mUI.MelSeparator(_row )) 
    _base_str = 'uiFF_worldUp'
    
    for i,a in enumerate(list('xyz')):
        #mUI.MelLabel(_row ,l=a)
        _field = mUI.MelFloatField(_row , ut='cgmUISubTemplate', w= 60 )
        self.__dict__['{0}{1}'.format(_base_str,a.capitalize())] = _field          
        if i == 1:
            _field.setValue(1.0)
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'X',
              c = cgmGEN.Callback(uiFunc_setWorldUp,self,1.0,0,0),
              ann = "Set to X") 
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Y',
              c = cgmGEN.Callback(uiFunc_setWorldUp,self,0,1.0,0),
              ann = "Set to Y")         
    mc.button(parent=_row ,
              ut = 'cgmUITemplate',                                                                                                
              l = 'Z',
              c = cgmGEN.Callback(uiFunc_setWorldUp,self,0,0,1.0),
              ann = "Set to Z")         
    mUI.MelSpacer(_row ,w=5)                                              
    _row.layout() 
    
def buildRow_getVector(self,parent):
    #>>>Match mode -------------------------------------------------------------------------------------
    _row = mUI.MelHSingleStretchLayout(parent,ut='cgmUISubTemplate',padding = 5)

    mUI.MelSpacer(_row,w=5)                      
    mUI.MelLabel(_row,l='Vector:')
    _row.setStretchWidget( mUI.MelSeparator(_row) )
    
    for i,item in enumerate(SHARED._l_axis_by_string):
        mc.button(parent = _row,
                  ut = 'cgmUITemplate',
                  label=item,
                  c = cgmGEN.Callback(uiFunc_getVectorOfSelected,self,item),
                  ann='Get selected objects {0} vector'.format(item))

        mUI.MelSpacer(_row,w=2)           
    mc.button(parent = _row,
              ut = 'cgmUITemplate',
              label='Between Sel',
              c = cgmGEN.Callback(uiFunc_getVectorOfSelected,self,'between'),
              ann='Get the vector between the first and last selected')
    mUI.MelSpacer(_row,w=2)           


    _row.layout()   

def uiFunc_getVectorOfSelected(self,axis = 'x+'):
    if axis == 'between':
        _sel = MMCONTEXT.get_list()
    else:
        _sel = MMCONTEXT.get_list(getTransform=True)
    if not _sel:
        return log.error('Nothing selected')
    
    if axis == 'between':
        if not len(_sel) >= 2:
            raise ValueError,'Must have more than two objects selected for between mode'
        try:vec = MATH.get_vector_of_two_points(POS.get(_sel[0]),POS.get(_sel[-1]))
        except Exception,err:
            log.error("Query fail: {0}".format(_sel))
            raise Exception,err
    else:
        vec = MATH.get_obj_vector(_sel[0],axis)
    log.info("Found vector: {0}".format(vec))
    
    uiFunc_setWorldUp(self,vec[0],vec[1],vec[2])
    
def uiFunc_setWorldUp(self, x = None, y = None, z = None):
    _base_str = 'uiFF_worldUp'
    #mUI.MelFloatField(_row , ut='cgmUISubTemplate', w= 60 ).setV
    for i,arg in enumerate([x,y,z]):
        if arg is not None:
            mField = self.__dict__['{0}{1}'.format(_base_str,'xyz'[i].capitalize())]
            mField.setValue(arg)
            
def uiFunc_tweak(self, mode = 'zero'):
    _base_str = 'uiFF_orientTweak'
    #mUI.MelFloatField(_row , ut='cgmUISubTemplate', w= 60 ).setV
    
    _l = []
    for i,arg in enumerate('xyz'):
        if arg is not None:            
            mField = self.__dict__['{0}{1}'.format(_base_str,'xyz'[i].capitalize())]
            if mode == 'zero':
                mField.setValue(0.0)
            else:
                if mode == '-':
                    _l.append(-mField.getValue())                    
                else:
                    _l.append(mField.getValue())
                
    if mode != 'zero':
        _sel = MMCONTEXT.get_list(mType='joint')
        if not _sel:
            return log.error('No joints selected') 
        JOINTS.tweakOrient(_sel,_l)
    
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


 