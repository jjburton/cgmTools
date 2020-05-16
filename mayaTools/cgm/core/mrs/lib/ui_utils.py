"""
------------------------------------------
ui_utils: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
__MAYALOCAL = 'MRSUI'

import random
import re
import copy
import time
import os

import maya.cmds as mc

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
import Red9.core.Red9_CoreUtils as r9Core

#from Red9.core import Red9_AnimationUtils as r9Anim
from cgm.core import cgm_General as cgmGEN

import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

import cgm.core.mrs.lib.animate_utils as MRSANIMUTILS
import cgm.core.mrs.lib.general_utils as BLOCKGEN


class mrsScrollList(mUI.BaseMelWidget):
    '''
    NOTE: you probably want to use the MelObjectScrollList instead!
    '''
    WIDGET_CMD = mc.iconTextScrollList
    KWARG_CHANGE_CB_NAME = 'sc'

    ALLOW_MULTI_SELECTION = True
    def __new__( cls, parent, *a, **kw ):
        if 'ams' not in kw and 'allowMultiSelection' not in kw:
            kw[ 'ams' ] = cls.ALLOW_MULTI_SELECTION
        return mUI.BaseMelWidget.__new__( cls, parent, *a, **kw )
    
    def __init__( self, parent, *a, **kw ):
        mUI.BaseMelWidget.__init__( self, parent, *a, **kw )
        self._appendCB = None
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_itc = []
        self._d_itc =  {}
        self.filterField = None
        self.b_selCommandOn = True
        self.rebuild()
        self.cmd_select = None
        self(e=True, sc = self.selCommand)
        self.mDat = MRSANIMUTILS.get_sharedDatObject()#MRSANIMUTILS.MRSDAT
        
    def __getitem__( self, idx ):
        return self.getItems()[ idx ]

    def setItems( self, items ):
        self.clear()
        for i in items:
            self.append( i )
    def getItems( self ):
        return self._items
        
    def getSelectedItems( self ):
        return self( q=True, si=True ) or []
        
    def getSelectedIdxs( self ):
        return [ idx-1 for idx in self( q=True, sii=True ) or [] ]
        
    def selectByIdx( self, idx ):
        self( e=True, selectIndexedItem=idx+1 )  #indices are 1-based in mel land - fuuuuuuu alias!!!

    def selectByValue( self, value):
        self( e=True, selectItem=value )
        
    def selectByBlock(self,Block):
        log.debug(cgmGEN.logString_start('selectByBlock'))        
        
        ml = VALID.listArg(Block)
        _cleared = False
        for Block in ml:
            if Block in self._ml_loaded:
                if not _cleared:
                    self.clearSelection()
                    _cleared = True
                self.selectByIdx(self._ml_loaded.index(Block))
                self.setHLC(Block)
            
    def getSelectedBlocks( self):
        log.debug(cgmGEN.logString_start('getSelectedBlocks'))                
        _indicesRaw = self.getSelectedIdxs()
        if not _indicesRaw:
            log.debug("Nothing selected")
            return []
        _indices = []
        for i in _indicesRaw:
            _indices.append(int(str(i).split('L')[0]))
        return [self._ml_loaded[i] for i in _indices]

    def append( self, item ):
        self( e=True, append=item )
        self._items.append(item)
        
    def appendItems( self, items ):
        for i in items: self.append( i )
        
    def allowMultiSelect( self, state ):
        self( e=True, ams=state )
    
    def report(self):
        log.debug(cgmGEN.logString_start('report'))                
        log.info("Scene: "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_scene):
            print ("{0} | {1} | {2}".format(i,self._l_strings[i],mObj))
            
        log.info("Loaded "+cgmGEN._str_subLine)
        for i,mObj in enumerate(self._ml_loaded):
            print("{0} | {1}".format(i, mObj))
            
        pprint.pprint(self._ml_scene)
        
    def set_selCallBack(self,func,*args,**kws):
        log.debug(cgmGEN.logString_start('set_selCallBack'))                
        self.selCommand = func
        self.selArgs = args
        self.selkws = kws
    
    def setHLC(self,mBlock=None):
        log.debug(cgmGEN.logString_start('setHLC'))        
        if mBlock:
            try:
                _color = self._d_itc[mBlock]
                log.info("{0} | {1}".format(mBlock,_color))
                _color = [v*.7 for v in _color]
                self(e =1, hlc = _color)
                return
            except Exception,err:
                log.error(err)
                
            try:self(e =1, hlc = [.5,.5,.5])
            except:pass
            
    def selCommand(self):
        log.debug(cgmGEN.logString_start('selCommand'))
        l_indices = self.getSelectedIdxs()
        mBlock = self.getSelectedBlocks()
        if mBlock:
            self.setHLC(mBlock[0])
            pprint.pprint(mBlock)
            self.mDat._ml_listNodes = mBlock
        if self.b_selCommandOn and self.cmd_select:
            if len(l_indices)<=1:
                return self.cmd_select()
        return False
    
    def rebuild( self ):
        _str_func = 'rebuild'
        self.mDat = MRSANIMUTILS.get_sharedDatObject()#MRSANIMUTILS.MRSDAT
        
        log.debug(cgmGEN.logString_start(_str_func))
        self.b_selCommandOn = False
        ml_sel = self.getSelectedBlocks()
        self( e=True, ra=True )
        
        try:self(e =1, hlc = [.5,.5,.5])
        except:pass        
        
        self._items = []
        self._ml_scene = []
        self._ml_loaded = []
        self._l_strings = []
        self._l_str_loaded = []
        self._l_itc = []
        self._d_itc  = {}
        #...
        _ml,_l_strings = BLOCKGEN.get_uiModuleScollList_dat(showSide=1,presOnly=1)
        
        self._ml_scene = _ml
        self._l_itc = []
        
        d_colors = {'left':[.4,.4,1],
                    'right':[.9,.2,.2],
                    'center':[.8,.8,0]}
        
        def getString(pre,string):
            i = 1
            _check = ''.join([pre,string])
            while _check in self._l_strings and i < 100:
                _check = ''.join([pre,string,' | NAMEMATCH [{0}]'.format(i)])
                i +=1
            return _check
        
        def get_side(mNode):
            _cgmDirection = mNode.getMayaAttr('cgmDirection')
            if _cgmDirection:
                if _cgmDirection[0].lower() == 'l':
                    return 'left'
                return 'right'
            return 'center'
        
        for i,mBlock in enumerate(_ml):
            _arg = get_side(mBlock)
            _color = d_colors.get(_arg,d_colors['center'])
            self._l_itc.append(_color)            
            self._d_itc[mBlock] = _color
            try:
                _str_base = mBlock.UTILS.get_uiString(mBlock)#mBlock.p_nameBase#
                #_modType = mBlock.getMayaAttr('moduleType')
                #if _modType:
                    #_str_base = _str_base + ' | [{0}]'.format(_modType)
            except:_str_base = 'FAIL | {0}'.format(mBlock.mNode)
            _pre = _l_strings[i]
            self._l_strings.append(getString(_pre,_str_base))
            
        self.update_display()
        
        if ml_sel:
            try:self.selectByBlock(ml_sel)
            except Exception,err:
                print err
        self.b_selCommandOn = True

    def clear( self ):
        log.debug(cgmGEN.logString_start('clear'))                
        self( e=True, ra=True )
        self._l_str_loaded = []
        self._ml_loaded = []
        
    def clearSelection( self,):
        self( e=True, deselectAll=True )
    def set_filterObj(self,obj=None):
        self.filterField = obj

    def update_display(self,searchFilter='',matchCase = False):
        _str_func = 'update_display'
        log.debug(cgmGEN.logString_start(_str_func))
        
        l_items = self.getSelectedItems()
        
        if self.filterField is not None:
            searchFilter = self.filterField.getValue()
        
        self.clear()
        try:
            for i,strEntry in enumerate(r9Core.filterListByString(self._l_strings,
                                                                  searchFilter,
                                                                  matchcase=matchCase)):
                if strEntry in self._l_str_loaded:
                    log.warning("Duplicate string")
                    continue
                self.append(strEntry)
                self._l_str_loaded.append(strEntry)
                idx = self._l_strings.index(strEntry)
                _mBlock = self._ml_scene[idx]
                self._ml_loaded.append(_mBlock)
                #_color = d_state_colors.get(_mBlock.getEnumValueString('blockState'))
                _color = self._d_itc[_mBlock]
                try:self(e=1, itc = [(i+1,_color[0],_color[1],_color[2])])
                except:pass

        except Exception,err:
            log.error("|{0}| >> err: {1}".format(_str_func, err))  
            for a in err:
                log.error(a)
        
        #if l_items:
            #try:self.selectByValue(l_items)
            #except Exception,err:
                #print err
    
    def func_byBlock(self,func,*args,**kws):
        try:
            for mBlock in self.getSelectedBlocks():
                try:
                    res = func( *args, **kws )
                except Exception,err:
                    try:log.debug("Func: {0}".format(_func.__name__))
                    except:log.debug("Func: {0}".format(_func))
      
                    if args:
                        log.debug("args: {0}".format(args))
                    if kws:
                        log.debug("kws: {0}".format(kws))
                    for a in err.args:
                        log.debug(a)
                    raise Exception,err
        except:pass
        finally:
            self.rebuild()
            
    def selectCallBack(self,func=None,*args,**kws):
        print self.getSelectedBlocks()