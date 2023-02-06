"""
------------------------------------------
contextual_utils: cgm.core.tools.markingMenus.lib.contextual_utils
Author: Josh Burton
email: cgmonks.info@gmail.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

"""
# From Python =============================================================
import copy
import re
import time
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc


#from cgm.core import cgm_Meta as cgmMeta
import cgm.core.cgm_Meta as cgmMeta
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import shape_utils as SHAPE
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.lib import attribute_utils as ATTR
import cgm.core.lib.transform_utils as TRANS
import cgm.core.cgm_General as cgmGEN
import cgm.core.lib.list_utils as LISTS


def kill_mmTool(ui='cgmMM'):
    def _call():
        try:
            log.debug("killUI...")
            _var_mode = cgmMeta.cgmOptionVar('cgmVar_cgmMarkingMenu_menuMode', defaultValue = 0)
            log.debug('mode: {0}'.format(_var_mode))    
            if _var_mode.value in [0,1,2,3]:
                log.debug('animMode killUI')
                
                #IsClickedOptionVar = cgmMeta.cgmOptionVar('cgmVar_IsClicked')
                #mmActionOptionVar = cgmMeta.cgmOptionVar('cgmVar_mmAction')
            
                sel = mc.ls(sl=1)
            
                #>>> Timer stuff
                #=============================================================================
                var_clockStart = cgmMeta.cgmOptionVar('cgmVar_cgmMarkingMenu_clockStart', defaultValue = 0.0)    
                f_seconds = time.time()-var_clockStart.value
                log.debug(">"*10  + '   cgmMarkingMenu =  %0.3f seconds  ' % (f_seconds) + '<'*10)    
            
                if sel and f_seconds <= .5:#and not mmActionOptionVar.value:
                    log.info("|{0}| >> Set key | low time tripped".format('cgmMM'))
                    setKey()
                    
                #mmTemplate.killChildren(_str_popWindow)
                if mc.popupMenu(ui,ex = True):
                    try:mc.menu(ui,e = True, deleteAllItems = True)
                    except Exception as err:
                        log.error("Failed to delete menu items")   
                        
                    mc.deleteUI(ui) 
                    
                #pprint.pprint(vars())      
                
        except Exception as err:
            log.error(err)   
        finally:
            print(("... '{0}' killed".format(ui)))
        
    mc.evalDeferred(_call,lp=True)
    
def setKey(keyModeOverride = None):
    _str_func = "setKey"        
    KeyTypeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyType', defaultValue = 0)
    KeyModeOptionVar = cgmMeta.cgmOptionVar('cgmVar_KeyMode', defaultValue = 0)	
    selection = False
    
    log.debug("|{0}| >> keyType: {1} | keyMode: {2} |  keyModeOverride: {3}".format(_str_func,KeyTypeOptionVar.value,KeyModeOptionVar.value,keyModeOverride))  
    
    if not KeyModeOptionVar.value:#This is default maya keying mode
        selection = mc.ls(sl=True) or []
        if not selection:
            return log.warning('cgmPuppetKey.setKey>>> Nothing l_selected!')
           
            
        """if not KeyTypeOptionVar.value:
            mc.setKeyframe(selection)
        else:
            mc.setKeyframe(breakdown = True)"""
    else:#Let's check the channel box for objects
        selection = SEARCH.get_selectedFromChannelBox(False) or []
        if not selection:
            log.debug("|{0}| >> No channel box selection. ".format(_str_func))
            selection = mc.ls(sl=True) or []
            
            
    if not selection:
        return log.warning('cgmPuppetKey.setKey>>> Nothing selected!')
    
            
    if keyModeOverride:
        log.debug("|{0}| >> Key override mode. ".format(_str_func))
        if keyModeOverride== 'breakdown':
            mc.setKeyframe(selection,breakdown = True)     
        else:
            mc.setKeyframe(selection)
            
    else:
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
        
        mel.eval('timeSliderClearKey;')
        """
        if not KeyTypeOptionVar.value:
            mc.cutKey(selection)
        else:
            mc.cutKey(selection)"""
    else:#Let's check the channel box for objects
        selection = search.returnSelectedAttributesFromChannelBox(False) or []
        if not selection:
            selection = mc.ls(sl=True) or []
            if not selection:
                return log.warning('cgmPuppetKey.deleteKey>>> Nothing l_selected!')
        """
        if not KeyTypeOptionVar.value:
            mc.cutKey(selection)	    
        else:
            mc.cutKey(selection,breakdown = True)"""
        mel.eval('timeSliderClearKey;')