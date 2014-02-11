from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
#from cgm.core.cgmPy import validateArgs 
import maya.cmds as mc
def ccFuncCls(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        '''
        This is my first funcCls
        '''
        def __init__(self, *args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'ccFuncCls'                     
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'direction',"default":'l',"argType":'str','help':"This is kw for leftSide or rightSide"},
                                            {'kw':'prefix',"default":'hand',"argType":'str','help':"this is kw for parts"}]       
            self.__dataBind__(*args, **kws)
            #self.l_funcSteps = [{'step':'validateArgs','call':validateArgs.stringArg()}]# 'bool' object is not callable,how and when I could use it?
        def __func__(self):
            direction = self.d_kws['direction']
            prefix = self.d_kws['prefix'] 
            self.mi_cc = cgmMeta.cgmObject(nodeType = 'transform')
            self.mi_cc.rename(direction +'_'+ prefix + '_cc_ctrl')
            self.mi_cc.addAttr('isCTRL', True)
            self.mi_cc.doGroup()
    return fncWrap(*args, **kws).go()
      
ccFuncCls('left','hand')
ccFuncCls(reportTimes = 1)
ccFuncCls(printHelp = 1)
ccFuncCls(reportShow = 1)
#ccFuncCls(reportEnv = 1)