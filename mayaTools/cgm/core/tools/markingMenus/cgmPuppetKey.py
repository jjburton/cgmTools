import maya.cmds as mc
import maya.mel as mel

#from cgm.lib.zoo.zooPyMaya.baseMelUI import *
from cgm.core.lib.zoo import baseMelUI as mUI
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core.classes import GuiFactory as cgmUI

from cgm.lib import guiFactory
from cgm.lib import (lists,search)
from cgm.tools.lib import animToolsLib
from cgm.tools.lib import tdToolsLib
from cgm.tools.lib import locinatorLib
#reload(animToolsLib)
from cgm.lib import locators


import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def run():
    try:
        cgmSetKeyMM = puppetKeyMarkingMenu()
    except:
        mel.eval('performSetKeyframeArgList 1 {"0", "animationList"};')

class puppetKeyMarkingMenu(mUI.BaseMelWindow):
    def __init__(self):	
        """
        Initializes the pop up menu class call
        """
        self._str_funcName = "puppetKeyMarkingMenu"
        self.optionVars = []
        IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked', value = 0)
        mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction',value = 0)			

        panel = mc.getPanel(up = True)
        if panel:
            # Attempt at fixing a bug of some tools not working when the pop up parent isn't 'viewPanes'
            if 'MayaWindow' in mc.panel(panel,q = True,ctl = True):
                panel = 'viewPanes'

        sel = search.selectCheck()

        #>>>> Clock set
        #====================================================================
        self.clockStartVar = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyClockStart', defaultValue = 0.0)	
        self.clockStartVar.value = time.clock()
        log.debug("cgmPuppetKey.clockStart: %s"%self.clockStartVar.value)

        IsClickedOptionVar.value = 0
        mmActionOptionVar.value = 0

        if mc.popupMenu('cgmMM',ex = True):
            mc.deleteUI('cgmMM')

        if panel:
            if mc.control(panel, ex = True):
                try:
                    mc.popupMenu('cgmMM', ctl = 0, alt = 0, sh = 0, mm = 1, b =1, aob = 1, p = panel,
                                 pmc = lambda *a: self.createUI('cgmMM'))
                except:
                    log.warning('Exception on set key marking menu')
                    mel.eval('performSetKeyframeArgList 1 {"0", "animationList"};')		

    def setupVariables(self):
        self.KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
        guiFactory.appendOptionVarList(self,self.KeyTypeOptionVar.name)

        self.KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)
        guiFactory.appendOptionVarList(self,self.KeyModeOptionVar.name)	

        self.mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction')

        self.BuildModuleOptionVar = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyBuildModule', defaultValue = 1)
        guiFactory.appendOptionVarList(self,self.BuildModuleOptionVar.name)	

        self.BuildPuppetOptionVar = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyBuildPuppet', defaultValue = 1)
        guiFactory.appendOptionVarList(self,self.BuildPuppetOptionVar.name)	

        self.ResetModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_ChannelResetMode', defaultValue = 0)		
        guiFactory.appendOptionVarList(self,self.ResetModeOptionVar.name)


    def createUI(self,parent):
        """
        Create the UI
        """	
        log.info("{0}".format(self._str_funcName))
        time_buildMenuStart =  time.clock()
        self.setupVariables()#Setup our optionVars

        def buttonAction(command):
            """
            execute a command and let the menu know not do do the default button action but just kill the ui
            """			
            self.mmActionOptionVar.value=1			
            command
            killUI()	

        def func_multiModuleSelect():
            """
            execute a command and let the menu know not do do the default button action but just kill the ui
            """	
            l_buffer = []
            if self.ml_modules:
                l_buffer = []
                for i_m in self.ml_modules:
                    l_buffer.extend( i_m.rigNull.moduleSet.getList() )
                mc.select(l_buffer )
            killUI()	

        def func_multiModuleKey():
            """
            execute a command and let the menu know not do do the default button action but just kill the ui
            """		
            l_slBuffer = mc.ls(sl=True) or []		    
            func_multiModuleSelect()
            setKey()
            if l_slBuffer:mc.select(l_slBuffer)
            killUI()	

        def func_multiDynSwitch(arg):
            """
            execute a command and let the menu know not do do the default button action but just kill the ui
            """		
            l_slBuffer = mc.ls(sl=True) or []		    	    
            if self.ml_modules:
                for i_m in self.ml_modules:
                    try:i_m.rigNull.dynSwitch.go(arg)
                    except Exception,error:log.error(error)
            if l_slBuffer:mc.select(l_slBuffer)		    
            killUI()	

        def func_setPuppetControlSetting(mPuppet,attr,arg):
            """
            execute a command and let the menu know not do do the default button action but just kill the ui
            """	
            l_slBuffer = mc.ls(sl=True) or []		    	    	    
            try:
                mPuppet.controlSettings_setModuleAttrs(attr,arg)
            except Exception,error:
                log.error("[func_setPuppetControlSetting fail!]{%s}"%error)
            if l_slBuffer:mc.select(l_slBuffer)		    
            killUI()	

        def func_multiReset():
            """
            execute a command and let the menu know not do do the default button action but just kill the ui
            """	
            l_slBuffer = mc.ls(sl=True) or []		    	    	    	    
            if self.ml_modules:
                for i_m in self.ml_modules:
                    i_m.animReset(self.ResetModeOptionVar.value)
            if l_slBuffer:mc.select(l_slBuffer)		    	    
            killUI()		

        def func_multiChangeDynParent(attr,option):
            """
            execute a command and let the menu know not do do the default button action but just kill the ui
            """	
            l_objects = [i_o.getShortName() for i_o in self.d_objectsInfo.keys()]
            log.info("func_multiChangeDynParent>> attr: '%s' | option: '%s' | objects: %s"%(attr,option,l_objects))
            timeStart_tmp = time.clock()
            for i_o in self.d_objectsInfo.keys():
                try:
                    mi_dynParent = self.d_objectsInfo[i_o]['dynParent'].get('mi_dynParent')
                    mi_dynParent.doSwitchSpace(attr,option)
                except Exception,error:
                    log.error("func_multiChangeDynParent>> '%s' failed. | %s"%(i_o.getShortName(),error))    

            log.info(">"*10  + ' func_multiChangeDynParent =  %0.3f seconds  ' % (time.clock()-timeStart_tmp) + '<'*10)  
            mc.select(l_objects)

        def aimObjects(self):
            _str_funcName = "%s.aimObjects"%puppetKeyMarkingMenu._str_funcName
            log.debug(">>> %s "%(_str_funcName) + "="*75) 
            l_slBuffer = mc.ls(sl=True) or []		    	    	    	    	    
            for i_obj in self.ml_objList[1:]:
                try:
                    if i_obj.hasAttr('mClass') and i_obj.mClass == 'cgmControl':
                        if i_obj._isAimable():
                            i_obj.doAim(self.i_target)
                except Exception,error:
                    log.error("%s >> obj: '%s' | error: %s"%(_str_funcName,i_obj.p_nameShort,error))
            if l_slBuffer:mc.select(l_slBuffer)		    	    

        def mirrorObjects(self):
            _str_funcName = "%s.mirrorObjects"%puppetKeyMarkingMenu._str_funcName
            log.debug(">>> %s "%(_str_funcName) + "="*75)  	    
            l_slBuffer = mc.ls(sl=True) or []		    	    	    	    	    	    
            for i_obj in self.ml_objList:
                try:i_obj.doMirrorMe()
                except Exception,error:
                    log.error("%s >> obj: '%s' | error: %s"%(_str_funcName,i_obj.p_nameShort,error))
            if l_slBuffer:mc.select(l_slBuffer)		    	    

        def children_mirror(self,module):
            _str_funcName = "%s.children_mirror"%puppetKeyMarkingMenu._str_funcName
            log.debug(">>> %s "%(_str_funcName) + "="*75)  
            l_slBuffer = mc.ls(sl=True) or []		    	    	    	    	    	    	    
            try:module.mirrorMe()
            except Exception,error:
                log.error("%s >> obj: '%s' | error: %s"%(_str_funcName,module.p_nameShort,error))	    

            for mMod in module.get_allModuleChildren():
                try:mMod.mirrorMe()
                except Exception,error:
                    log.error("%s >> obj: '%s' | error: %s"%(_str_funcName,mMod.p_nameShort,error))
            if l_slBuffer:mc.select(l_slBuffer)		    	    

        def children_mirrorPush(self,module):
            _str_funcName = "%s.children_mirror"%puppetKeyMarkingMenu._str_funcName
            log.debug(">>> %s "%(_str_funcName) + "="*75)
            l_slBuffer = mc.ls(sl=True) or []		    	    	    	    	    	    	    	    
            try:module.mirrorPush()
            except Exception,error:
                log.error("%s >> obj: '%s' | error: %s"%(_str_funcName,module.p_nameShort,error))

            for mMod in module.get_allModuleChildren():
                try:mMod.mirrorPush()
                except Exception,error:
                    log.error("%s >> obj: '%s' | error: %s"%(_str_funcName,mMod.p_nameShort,error))
            if l_slBuffer:mc.select(l_slBuffer)		    	    

        def children_mirrorPull(self,module):
            _str_funcName = "%s.children_mirror"%puppetKeyMarkingMenu._str_funcName
            log.debug(">>> %s "%(_str_funcName) + "="*75)  

            l_slBuffer = mc.ls(sl=True) or []		    	    	    	    	    	    	    	    	    
            try:module.mirrorPull()
            except Exception,error:
                log.error("%s >> obj: '%s' | error: %s"%(_str_funcName,module.p_nameShort,error))

            for mMod in module.get_allModuleChildren():
                try:mMod.mirrorPull()
                except Exception,error:
                    log.error("%s >> obj: '%s' | error: %s"%(_str_funcName,mMod.p_nameShort,error))
            if l_slBuffer:mc.select(l_slBuffer)		    	    

        IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked',value = 0)
        IsClickedOptionVar.value = 1


        #>>>> Sel check
        #====================================================================
        int_maxObjects = 5	

        l_selected = mc.ls(sl=True) or []
        if len(l_selected) <= int_maxObjects:self._l_selected = l_selected
        else:self._l_selected = l_selected[:5]

        self.ml_objList = cgmMeta.validateObjListArg(self._l_selected,cgmMeta.cgmObject,True)
        log.debug("ml_objList: %s"%self.ml_objList)	    	

        self.ml_modules = []
        self.l_modules = []
        self.l_puppets = []	
        self.ml_puppets = []
        if l_selected:selCheck = True
        else:selCheck = False

        #>>>> Aim check
        #====================================================================
        b_aimable = False
        self.i_target = False
        log.info("ml_objList: %s"%self.ml_objList)
        if len(self.ml_objList)>=2:
            time_aimStart = time.clock()	    
            for i_obj in self.ml_objList[1:]:
                if i_obj.hasAttr('mClass') and i_obj.mClass == 'cgmControl':
                    if i_obj._isAimable():
                        b_aimable = True
                        self.i_target = self.ml_objList[0]
                        break
            log.info(">"*10  + 'Aim check =  %0.3f seconds  ' % (time.clock()-time_aimStart) + '<'*10)  

        #ShowMatch = search.matchObjectCheck()

        #>>>> Build Menu
        #====================================================================		
        mc.menu(parent,e = True, deleteAllItems = True)
        mUI.MelMenuItem(parent,
                    en = selCheck,
                    l = 'Reset Selected',
                    c = lambda *a:buttonAction(animToolsLib.ml_resetChannelsCall(transformsOnly = self.ResetModeOptionVar.value)),
                    rp = 'N')  

        mUI.MelMenuItem(parent,
                    en = b_aimable,
                    l = 'Aim',
                    c = lambda *a:buttonAction(aimObjects(self)),
                    rp = 'E')   

        mUI.MelMenuItem(parent,
                    en = selCheck,
                    l = 'Mirror selected',
                    c = lambda *a:buttonAction(mirrorObjects(self)),
                    rp = 'SE')    

        mUI.MelMenuItem(parent,
                    en = selCheck,
                    l = 'dragBreakdown',
                    c = lambda *a:buttonAction(animToolsLib.ml_breakdownDraggerCall()),
                    rp = 'S')

        mUI.MelMenuItem(parent,
                    en = selCheck,
                    l = 'deleteKey',
                    c = lambda *a:deleteKey(),
                    rp = 'SW')	

        timeStart_objectList = time.clock()
        if self.ml_objList:
            self.d_objectsInfo = {}
            #first we validate
            #First we're gonna gather all of the data
            #=========================================================================================
            for i,i_o in enumerate(self.ml_objList):
                if i >= int_maxObjects:
                    log.warning("More than %s objects select, only loading first %s for speed"%(int_maxObjects,int_maxObjects))
                    break
                d_buffer = {}

                #>>> Space switching ------------------------------------------------------------------							
                if i_o.getMessage('dynParentGroup'):
                    i_dynParent = cgmMeta.validateObjArg(i_o.getMessage('dynParentGroup')[0],cgmRigMeta.cgmDynParentGroup,True)
                    d_buffer['dynParent'] = {'mi_dynParent':i_dynParent,'attrs':[],'attrOptions':{}}#Build our data gatherer					    
                    if i_dynParent:
                        for a in cgmRigMeta.d_DynParentGroupModeAttrs[i_dynParent.dynMode]:
                            if i_o.hasAttr(a):
                                d_buffer['dynParent']['attrs'].append(a)
                                lBuffer_attrOptions = []
                                for i,o in enumerate(cgmMeta.cgmAttr(i_o.mNode,a).p_enum):
                                    lBuffer_attrOptions.append(o)
                                d_buffer['dynParent']['attrOptions'][a] = lBuffer_attrOptions
                self.d_objectsInfo[i_o] = d_buffer

                #>>> Module --------------------------------------------------------------------------
                if self.BuildModuleOptionVar.value or self.BuildPuppetOptionVar.value:
                    if i_o.getMessage('rigNull'):
                        _mi_rigNull = i_o.rigNull			
                        try:_mi_module = _mi_rigNull.module
                        except Exception:_mi_module = False

                        if self.BuildModuleOptionVar.value:
                            try:
                                self.ml_modules.append(_mi_module)
                            except Exception,error:
                                log.info("Failed to append module for: %s | %s"%(i_o.getShortName(),error))

                    if self.BuildPuppetOptionVar.value:
                        try:
                            if _mi_module:
                                buffer = _mi_module.getMessage('modulePuppet')
                                if buffer:
                                    self.l_puppets.append(buffer[0])
                        except Exception,error:
                            log.info("Failed to append puppet for: %s | %s"%(i_o.getShortName(),error))
                        try:
                            buffer = i_o.getMessage('puppet')
                            if buffer:
                                self.l_puppets.append(buffer[0])
                        except Exception,error:
                            log.info("Failed to append puppet for: %s | %s"%(i_o.getShortName(),error))			
            log.info(">"*10  + ' Object list build =  %0.3f seconds  ' % (time.clock()-timeStart_objectList) + '<'*10)  
            for k in self.d_objectsInfo.keys():
                log.debug("%s: %s"%(k.getShortName(),self.d_objectsInfo.get(k)))


            #Build the menu
            #=========================================================================================
            #>> Find Common options ------------------------------------------------------------------
            timeStart_commonOptions = time.clock()    
            l_commonAttrs = []
            d_commonOptions = {}
            bool_firstFound = False
            for i_o in self.d_objectsInfo.keys():
                if 'dynParent' in self.d_objectsInfo[i_o].keys():
                    attrs = self.d_objectsInfo[i_o]['dynParent'].get('attrs') or []
                    attrOptions = self.d_objectsInfo[i_o]['dynParent'].get('attrOptions') or {}
                    if self.d_objectsInfo[i_o].get('dynParent'):
                        if not l_commonAttrs and not bool_firstFound:
                            log.debug('first found')
                            l_commonAttrs = attrs
                            state_firstFound = True
                            d_commonOptions = attrOptions
                        elif attrs:
                            log.debug(attrs)
                            for a in attrs:
                                if a in l_commonAttrs:
                                    for option in d_commonOptions[a]:			
                                        if option not in attrOptions[a]:
                                            d_commonOptions[a].remove(option)


            log.debug("Common Attrs: %s"%l_commonAttrs)
            log.debug("Common Options: %s"%d_commonOptions)
            log.info(">"*10  + ' Common options build =  %0.3f seconds  ' % (time.clock()-timeStart_commonOptions) + '<'*10)  

            #>> Build ------------------------------------------------------------------
            int_lenObjects = len(self.d_objectsInfo.keys())
            # Mutli
            if int_lenObjects == 1:
                #MelMenuItem(parent,l="-- Object --",en = False)	    					
                use_parent = parent
                state_multiObject = False
            else:
                #MelMenuItem(parent,l="-- Objects --",en = False)	    			
                iSubM_objects = mUI.MelMenuItem(parent,l="Objects(%s)"%(int_lenObjects),subMenu = True)
                use_parent = iSubM_objects
                state_multiObject = True		
                if l_commonAttrs and [d_commonOptions.get(a) for a in l_commonAttrs]:
                    for atr in d_commonOptions.keys():
                        tmpMenu = mUI.MelMenuItem( parent, l="multi Change %s"%atr, subMenu=True)
                        for i,o in enumerate(d_commonOptions.get(atr)):
                            MelMenuItem(tmpMenu,l = "%s"%o,
                                        c = cgmUI.Callback(func_multiChangeDynParent,atr,o))
            # Individual ----------------------------------------------------------------------------
            log.debug("%s"%[k.getShortName() for k in self.d_objectsInfo.keys()])
            for i_o in self.d_objectsInfo.keys():
                d_buffer = self.d_objectsInfo.get(i_o) or False
                if d_buffer:
                    if state_multiObject:
                        iTmpObjectSub = mUI.MelMenuItem(use_parent,l=" %s  "%i_o.getBaseName(),subMenu = True)
                    else:
                        mUI.MelMenuItem(parent,l="-- %s --"%i_o.getShortName(),en = False)
                        iTmpObjectSub = use_parent
                    if d_buffer.get('dynParent'):
                        mi_dynParent = d_buffer['dynParent'].get('mi_dynParent')
                        d_attrOptions = d_buffer['dynParent'].get('attrOptions') or {}			
                        for a in d_attrOptions.keys():
                            if i_o.hasAttr(a):
                                lBuffer_attrOptions = []
                                tmpMenu = mUI.MelMenuItem( iTmpObjectSub, l="Change %s"%a, subMenu=True)
                                v = mc.getAttr("%s.%s"%(i_o.mNode,a))
                                for i,o in enumerate(cgmMeta.cgmAttr(i_o.mNode,a).p_enum):
                                    if i == v:b_enable = False
                                    else:b_enable = True
                                    mUI.MelMenuItem(tmpMenu,l = "%s"%o,en = b_enable,
                                                c = cgmUI.Callback(mi_dynParent.doSwitchSpace,a,i))
                    else:
                        log.debug("'%s':lacks dynParent"%i_o.getShortName())

        #>>> Module =====================================================================================================
        timeStart_ModuleStuff = time.clock()  	    
        if self.BuildModuleOptionVar.value and self.ml_modules:
            #MelMenuItem(parent,l="-- Modules --",en = False)	    
            self.ml_modules = lists.returnListNoDuplicates(self.ml_modules)
            int_lenModules = len(self.ml_modules)
            if int_lenModules == 1:
                use_parent = parent
                state_multiModule = False
            else:
                iSubM_modules = mUI.MelMenuItem(parent,l="Modules(%s)"%(int_lenModules),subMenu = True)
                use_parent = iSubM_modules
                state_multiModule = True
                mUI.MelMenuItem( parent, l="Select",
                             c = cgmUI.Callback(func_multiModuleSelect))
                mUI.MelMenuItem( parent, l="Key",
                             c = cgmUI.Callback(func_multiModuleKey))		
                mUI.MelMenuItem( parent, l="toFK",
                             c = cgmUI.Callback(func_multiDynSwitch,0))	
                mUI.MelMenuItem( parent, l="toIK",
                             c = cgmUI.Callback(func_multiDynSwitch,1))
                mUI.MelMenuItem( parent, l="Reset",
                             c = cgmUI.Callback(func_multiReset))			

            for i_module in self.ml_modules:
                _side = cgmGeneral.verify_mirrorSideArg(i_module.getMayaAttr('cgmDirection') or 'center')
                if state_multiModule:
                    iTmpModuleSub = mUI.MelMenuItem(iSubM_modules,l=" %s  "%i_module.getBaseName(),subMenu = True)
                    use_parent = iTmpModuleSub

                else:
                    mUI.MelMenuItem(parent,l="-- %s --"%i_module.getBaseName(),en = False)
                try:#To build dynswitch
                    i_switch = i_module.rigNull.dynSwitch
                    for a in i_switch.l_dynSwitchAlias:
                        mUI.MelMenuItem( use_parent, l="%s"%a,
                                     c = cgmUI.Callback(i_switch.go,a))						
                except Exception,error:
                    log.info("Failed to build dynSwitch for: %s | %s"%(i_module.getShortName(),error))	
                try:#module basic menu
                    mUI.MelMenuItem( use_parent, l="Key",
                                 c = cgmUI.Callback(i_module.animKey))							
                    mUI.MelMenuItem( use_parent, l="Select",
                                 c = cgmUI.Callback(i_module.animSelect))	
                    mUI.MelMenuItem( use_parent, l="Reset",
                                 c = cgmUI.Callback(i_module.animReset,self.ResetModeOptionVar.value))
                    mUI.MelMenuItem( use_parent, l="Mirror",
                                 c = cgmUI.Callback(i_module.mirrorMe))

                    if i_module.moduleType not in cgmPM.__l_faceModuleTypes__:
                        _enable = True
                        if _side == 'Centre':_enable = False
                        mUI.MelMenuItem( use_parent, l="Mirror Push",en = _enable,
                                     c = cgmUI.Callback(i_module.mirrorPush))	
                        mUI.MelMenuItem( use_parent, l="Mirror Pull",en = _enable,
                                     c = cgmUI.Callback(i_module.mirrorPull))
                    else:#Face module....
                        mUI.MelMenuItem( use_parent, l="Mirror Left",
                                     c = cgmUI.Callback(i_module.mirrorLeft))	
                        mUI.MelMenuItem( use_parent, l="Mirror Right",
                                     c = cgmUI.Callback(i_module.mirrorRight))

                    mUI.MelMenuItem( use_parent, l="Toggle Sub",
                                 c = cgmUI.Callback(i_module.toggle_subVis))			    
                except Exception,error:
                    log.info("Failed to build basic module menu for: %s | %s"%(i_o.getShortName(),error))					
                try:#module children
                    if i_module.getMessage('moduleChildren'):
                        iSubM_Children = mUI.MelMenuItem( use_parent, l="Children:",
                                                      subMenu = True)
                        mUI.MelMenuItem( iSubM_Children, l="toFK",
                                     c = cgmUI.Callback(i_module.dynSwitch_children,0))	
                        mUI.MelMenuItem( iSubM_Children, l="toIK",
                                     c = cgmUI.Callback(i_module.dynSwitch_children,1))				
                        mUI.MelMenuItem( iSubM_Children, l="Key",
                                     c = cgmUI.Callback(i_module.animKey_children))							
                        mUI.MelMenuItem( iSubM_Children, l="Select",
                                     c = cgmUI.Callback(i_module.animSelect_children))
                        mUI.MelMenuItem( iSubM_Children, l="Reset",
                                     c = cgmUI.Callback(i_module.animReset_children,self.ResetModeOptionVar.value))			
                        mUI.MelMenuItem( iSubM_Children, l="Mirror",
                                     c = cgmUI.Callback(children_mirror,self,i_module))
                        if i_module.moduleType not in cgmPM.__l_faceModuleTypes__:
                            mUI.MelMenuItem( iSubM_Children, l="Mirror Push",
                                         c = cgmUI.Callback(children_mirrorPush,self,i_module))
                            mUI.MelMenuItem( iSubM_Children, l="Mirror Pull",
                                         c = cgmUI.Callback(children_mirrorPull,self,i_module))
                        mUI.MelMenuItem( iSubM_Children, l="visSub Show",
                                     c = cgmUI.Callback(i_module.animSetAttr_children,'visSub',1,True,False))				
                        mUI.MelMenuItem( iSubM_Children, l="visSub Hide",
                                     c = cgmUI.Callback(i_module.animSetAttr_children,'visSub',0,True,False))			
                except Exception,error:
                    log.info("Failed to build basic module menu for: %s | %s"%(i_o.getShortName(),error))					
                try:#module siblings
                    if i_module.getModuleSiblings():
                        iSubM_Siblings = mUI.MelMenuItem( use_parent, l="Siblings:",
                                                      subMenu = True)
                        mUI.MelMenuItem( iSubM_Siblings, l="toFK",
                                     c = cgmUI.Callback(i_module.dynSwitch_siblings,0,False))	
                        mUI.MelMenuItem( iSubM_Siblings, l="toIK",
                                     c = cgmUI.Callback(i_module.dynSwitch_siblings,1,False))				
                        mUI.MelMenuItem( iSubM_Siblings, l="Key",
                                     c = cgmUI.Callback(i_module.animKey_siblings,False))							
                        mUI.MelMenuItem( iSubM_Siblings, l="Select",
                                     c = cgmUI.Callback(i_module.animSelect_siblings,False))
                        mUI.MelMenuItem( iSubM_Siblings, l="Reset",
                                     c = cgmUI.Callback(i_module.animReset_siblings,False))			
                        mUI.MelMenuItem( iSubM_Siblings, l="Push pose",
                                     c = cgmUI.Callback(i_module.animPushPose_siblings))			
                        mUI.MelMenuItem( iSubM_Siblings, l="Mirror",
                                     c = cgmUI.Callback(i_module.mirrorMe_siblings,False))

                        if i_module.moduleType not in cgmPM.__l_faceModuleTypes__:
                            mUI.MelMenuItem( iSubM_Siblings, l="Mirror Push",
                                         c = cgmUI.Callback(i_module.mirrorPush_siblings,False))
                            mUI.MelMenuItem( iSubM_Siblings, l="Mirror Pull",
                                         c = cgmUI.Callback(i_module.mirrorPull_siblings,False))
                except Exception,error:
                    log.info("Failed to build basic module menu for: %s | %s"%(i_o.getShortName(),error))					

                mUI.MelMenuItemDiv(parent)						
        log.info(">"*10  + ' Module options build =  %0.3f seconds  ' % (time.clock()-timeStart_ModuleStuff) + '<'*10)  

        #>>> Puppet =====================================================================================================
        timeStart_PuppetStuff = time.clock()  	    
        if self.BuildPuppetOptionVar.value and self.l_puppets:
            #MelMenuItem(parent,l="-- Puppets --",en = False)	    
            self.l_puppets = lists.returnListNoDuplicates(self.l_puppets)
            self.ml_puppets = cgmMeta.validateObjListArg(self.l_puppets)
            log.info("Puppets:")
            for p in self.l_puppets:
                log.info(">>> {0}".format(p))
            int_lenPuppets = len(self.ml_puppets)
            if int_lenPuppets == 1:
                use_parent = parent
                state_multiPuppet = False
            else:
                iSubM_puppets = mUI.MelMenuItem(parent,l="Puppets(%s)"%(int_lenPuppets),subMenu = True)
                use_parent = iSubM_puppets
                state_multiPuppet = True
                mUI.MelMenuItem( parent, l="Select",
                             c = cgmUI.Callback(func_multiPuppetSelect))
                mUI.MelMenuItem( parent, l="Key",
                             c = cgmUI.Callback(func_multiPuppetKey))	
                """
		mUI.MelMenuItem( parent, l="toFK",
	                     c = cgmUI.Callback(func_multiDynSwitch,0))	
		mUI.MelMenuItem( parent, l="toIK",
	                     c = cgmUI.Callback(func_multiDynSwitch,1))	
		"""
            for i_puppet in self.ml_puppets:
                try:
                    if state_multiPuppet:
                        iTmpPuppetSub = mUI.MelMenuItem(iSubM_puppets,l=" %s  "%i_puppet.cgmName,subMenu = True)
                        use_parent = iTmpPuppetSub    
                    else:
                        mUI.MelMenuItem(parent,l="-- %s --"%i_puppet.cgmName,en = False)
                    '''
		    try:#To build dynswitch
			i_switch = i_puppet.rigNull.dynSwitch
			for a in i_switch.l_dynSwitchAlias:
			    mUI.MelMenuItem( use_parent, l="%s"%a,
					 c = cgmUI.Callback(i_switch.go,a))						
		    except Exception,error:
			log.info("Failed to build dynSwitch for: %s | %s"%(i_puppet.getShortName(),error))	
		    '''
                    try:#puppet basic menu
                        mUI.MelMenuItem( use_parent, l="Key",c = cgmUI.Callback(i_puppet.anim_key))							
                        mUI.MelMenuItem( use_parent, l="Select",c = cgmUI.Callback(i_puppet.anim_select))	
                        mUI.MelMenuItem( use_parent, l="Reset",c = cgmUI.Callback(i_puppet.anim_reset,self.ResetModeOptionVar.value))
                        mUI.MelMenuItem( use_parent, l="Mirror",c = cgmUI.Callback(i_puppet.mirrorMe))
                        mUI.MelMenuItem( use_parent, l="PushRight",c = cgmUI.Callback(i_puppet.mirror_do,'anim','symLeft'))
                        mUI.MelMenuItem( use_parent, l="PushLeft",c = cgmUI.Callback(i_puppet.mirror_do,'anim','symRight'))		    
                    except Exception,error:
                        log.info("Failed to build basic puppet menu for: %s | %s"%(i_o.getShortName(),error))

                    try:#puppet settings ===========================================================================
                        mi_puppetSettingsMenu = mUI.MelMenuItem( parent, l='Settings', subMenu=True)
                        mi_puppetControlSettings = i_puppet.masterControl.controlSettings 
                        l_settingsUserAttrs = mi_puppetControlSettings.getUserAttrs()

                        mUI.MelMenuItem( mi_puppetSettingsMenu, l="visSub Show",
                                     c = cgmUI.Callback(i_puppet.animSetAttr,'visSub',1,True))				
                        mUI.MelMenuItem( mi_puppetSettingsMenu, l="visSub Hide",
                                     c = cgmUI.Callback(i_puppet.animSetAttr,'visSub',0,True))		    

                        for attr in ['skeleton','geo','geoType']:
                            try:#Skeleton
                                if mi_puppetControlSettings.hasAttr(attr):
                                    mi_tmpMenu = mUI.MelMenuItem( mi_puppetSettingsMenu, l=attr, subMenu=True)			    
                                    mi_collectionMenu = mUI.MelRadioMenuCollection()#build our collection instance			    
                                    mi_attr = cgmMeta.cgmAttr(mi_puppetControlSettings,attr)
                                    l_options = mi_attr.getEnum()
                                    for i,str_option in enumerate(l_options):
                                        if i == mi_attr.value:b_state = True
                                        else:b_state = False
                                        mi_collectionMenu.createButton(mi_tmpMenu,l=' %s '%str_option,
                                                                       c = cgmUI.Callback(mc.setAttr,"%s"%mi_attr.p_combinedName,i),
                                                                       rb = b_state )					
                            except Exception,error:
                                log.info("option failed: %s | %s"%(attr,error))	

                        _d_moduleSettings = {'templates':{'options':['off','on'],'attr':'_tmpl'},
                                             'rigGuts':{'options':['off','lock','on'],'attr':'_rig'}}
                        for attr in _d_moduleSettings.keys():
                            try:#Skeleton
                                _l_options = _d_moduleSettings[attr]['options']
                                _attr = _d_moduleSettings[attr]['attr']
                                mi_tmpMenu = mUI.MelMenuItem( mi_puppetSettingsMenu, l=attr, subMenu=True)			    
                                for i,str_option in enumerate(_l_options):
                                    mUI.MelMenuItem( mi_tmpMenu, l=str_option,
                                                 c = cgmUI.Callback(func_setPuppetControlSetting,i_puppet,_attr,i))				
                            except Exception,error:
                                log.info("option failed: %s | %s"%(attr,error))
                    except Exception,error:
                        log.info("Failed to build puppet settings menu for: %s | %s"%(i_o.getShortName(),error))	

                except Exception,error:
                    log.info("Puppet failure: {0} | {1}".format(i_puppet.mNode,error))	

                mUI.MelMenuItemDiv(parent)						
        log.info(">"*10  + ' Puppet options build =  %0.3f seconds  ' % (time.clock()-timeStart_PuppetStuff) + '<'*10)  		


        #>>> Options menus
        #================================================================================
        mUI.MelMenuItem(parent,l = "{ Options }",en = False)

        #>>> Build Type
        BuildMenu = mUI.MelMenuItem( parent, l='Build Menus', subMenu=True)
        #BuildMenuCollection = mUI.MelRadioMenuCollection()
        b_buildModule = self.BuildModuleOptionVar.value
        mUI.MelMenuItem(BuildMenu,l=' Module ',
                    c= cgmUI.Callback(self.toggleVarAndReset,self.BuildModuleOptionVar),
                    cb= self.BuildModuleOptionVar.value )	
        mUI.MelMenuItem(BuildMenu,l=' Puppet ',
                    c= cgmUI.Callback(self.toggleVarAndReset,self.BuildPuppetOptionVar),
                    cb= self.BuildPuppetOptionVar.value )		

        #>>> Keying Options	
        KeyMenu = mUI.MelMenuItem( parent, l='Key type', subMenu=True)
        KeyMenuCollection = mUI.MelRadioMenuCollection()

        if self.KeyTypeOptionVar.value == 0:
            regKeyOption = True
            bdKeyOption = False
        else:
            regKeyOption = False
            bdKeyOption = True

        KeyMenuCollection.createButton(KeyMenu,l=' Reg ',
                                       c= cgmUI.Callback(self.toggleVarAndReset,self.KeyTypeOptionVar),
                                       rb= regKeyOption )
        KeyMenuCollection.createButton(KeyMenu,l=' Breakdown ',
                                       c= cgmUI.Callback(self.toggleVarAndReset,self.KeyTypeOptionVar),
                                       rb= bdKeyOption )

        #>>> Keying Mode
        KeyMenu = mUI.MelMenuItem( parent, l='Key Mode', subMenu=True)
        KeyMenuCollection = mUI.MelRadioMenuCollection()

        if self.KeyModeOptionVar.value == 0:
            regModeOption = True
            cbModeOption = False
        else:
            regModeOption = False
            cbModeOption = True

        KeyMenuCollection.createButton(KeyMenu,l=' Default ',
                                       c= cgmUI.Callback(self.toggleVarAndReset,self.KeyModeOptionVar),
                                       rb= regModeOption )
        KeyMenuCollection.createButton(KeyMenu,l=' Channelbox ',
                                       c= cgmUI.Callback(self.toggleVarAndReset,self.KeyModeOptionVar),
                                       rb= cbModeOption )		


        #>>> Reset Mode
        ResetMenu = mUI.MelMenuItem( parent, l='Reset Mode', subMenu=True)
        ResetMenuCollection = mUI.MelRadioMenuCollection()

        if self.ResetModeOptionVar.value == 0:
            regModeOption = True
            cbModeOption = False
        else:
            regModeOption = False
            cbModeOption = True

        ResetMenuCollection.createButton(ResetMenu,l=' Default ',
                                         c= cgmUI.Callback(self.toggleVarAndReset,self.ResetModeOptionVar),
                                         rb= regModeOption )
        ResetMenuCollection.createButton(ResetMenu,l=' Transform Attrs ',
                                         c= cgmUI.Callback(self.toggleVarAndReset,self.ResetModeOptionVar),
                                         rb= cbModeOption )			

        #mUI.MelMenuItemDiv(parent)
        """
		mUI.MelMenuItem(parent,l = 'autoTangent',
				    c = lambda *a: buttonAction(mel.eval('autoTangent')))
		mUI.MelMenuItem(parent,l = 'tweenMachine',
				    c = lambda *a: buttonAction(mel.eval('tweenMachine')))	
		mUI.MelMenuItem(parent, l = 'cgm.animTools',
	                c = lambda *a: buttonAction(cgmToolbox.loadAnimTools()))	
		mUI.MelMenuItemDiv(parent)
		mUI.MelMenuItem(parent,l = 'ml Set Key',
			        c = lambda *a: buttonAction(animToolsLib.ml_setKeyCall()))
		mUI.MelMenuItem(parent,l = 'ml Hold',
			        c = lambda *a: buttonAction(animToolsLib.ml_holdCall()))
		mUI.MelMenuItem(parent,l = 'ml Delete Key',
			        c = lambda *a: buttonAction(animToolsLib.ml_deleteKeyCall()))
		mUI.MelMenuItem(parent,l = 'ml Arc Tracer',
			        c = lambda *a: buttonAction(animToolsLib.ml_arcTracerCall()))
		"""
        #mUI.MelMenuItem(parent,l = "-"*20,en = False)
        mUI.MelMenuItemDiv(parent)							
        mUI.MelMenuItem(parent, l="Reset",
                    c=lambda *a: guiFactory.resetGuiInstanceOptionVars(self.optionVars))

        f_time = time.clock()-time_buildMenuStart
        log.info('build menu took: %0.3f seconds  ' % (f_time) + '<'*10)  

    def toggleVarAndReset(self, optionVar):
        try:
            self.mmActionOptionVar.value=1						
            optionVar.toggle()
            log.info("PuppetKey.toggleVarAndReset>>> %s : %s"%(optionVar.name,optionVar.value))
        except Exception,error:
            log.error(error)
            print "MM change var and reset failed!"


def killUI():
    log.info("killUI()...")        
    IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked')
    mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction')

    sel = search.selectCheck()

    #>>> Timer stuff
    #=============================================================================
    var_clockStart = cgmMeta.cgmOptionVar('cgmVar_PuppetKeyClockStart', defaultValue = 0.0)    
    f_seconds = time.clock()-var_clockStart.value
    log.debug(">"*10  + '   cgmPuppetKey =  %0.3f seconds  ' % (f_seconds) + '<'*10)    

    #>>>Delete our gui and default behavior
    if mc.popupMenu('cgmMM',ex = True):
        mc.deleteUI('cgmMM')
    if sel and f_seconds <= .5 and not mmActionOptionVar.value:
        setKey()

def setKey():
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	

    if not KeyModeOptionVar.value:#This is default maya keying mode
        selection = mc.ls(sl=True) or []
        if not selection:
            return log.warning('cgmPuppetKey.setKey>>> Nothing l_selected!')

        if not KeyTypeOptionVar.value:
            mc.setKeyframe(selection)
        else:
            mc.setKeyframe(breakdown = True)
    else:#Let's check the channel box for objects
        selection = search.returnSelectedAttributesFromChannelBox(False) or []
        if not selection:
            selection = mc.ls(sl=True) or []
            if not selection:
                return log.warning('cgmPuppetKey.setKey>>> Nothing l_selected!')

        if not KeyTypeOptionVar.value:
            mc.setKeyframe(selection)
        else:
            mc.setKeyframe(selection,breakdown = True)	

def deleteKey():
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	

    if not KeyModeOptionVar.value:#This is default maya keying mode
        selection = mc.ls(sl=True) or []
        if not selection:
            return log.warning('cgmPuppetKey.deleteKey>>> Nothing l_selected!')

        if not KeyTypeOptionVar.value:
            mc.cutKey(selection)	    
        else:
            mc.cutKey(selection)	    
    else:#Let's check the channel box for objects
        selection = search.returnSelectedAttributesFromChannelBox(False) or []
        if not selection:
            selection = mc.ls(sl=True) or []
            if not selection:
                return log.warning('cgmPuppetKey.deleteKey>>> Nothing l_selected!')

        if not KeyTypeOptionVar.value:
            mc.cutKey(selection)	    
        else:
            mc.cutKey(selection,breakdown = True)	
