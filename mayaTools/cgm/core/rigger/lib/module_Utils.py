"""
cgmLimb
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral

#>>> Utilities
#===================================================================
class rigStep(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """	
        super(rigStep, self).__init__(self,*args,**kws)
        goInstance = args[0]
        self._b_ExceptionInterupt = True
        try:
            assert goInstance._cgmClass == 'RigFactory.go'
        except StandardError,error:
            raise StandardError,"Not a RigFactory.go : %s"%error	

        self._str_funcName = 'moduleStep(%s)'%goInstance._strShortName	
        self._l_ARGS_KWS_DEFAULTS = [{'kw':'goInstance', "default":None, 'help':"This is your RigFactory go instance", "argType":"RigFactory.go"},
                                     {'kw':'reportTimes', "default":True, 'help':"Change to report defaults", "argType":"bool"}]
        self.__dataBind__(*args, **kws)
        self._go = goInstance
        #self.l_funcSteps = [{'step':'Get Data','call':self._getData}]

        #=================================================================

class templateStep(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """	
        super(templateStep, self).__init__(self,*args,**kws)
        goInstance = args[0]
        try:
            assert goInstance._cgmClass == 'TemplateFactory.go'
        except StandardError,error:
            raise StandardError,"Not a TemplateFactory.go : %s"%error	
        self._b_ExceptionInterupt = False
        self._str_funcName = 'templateStep(%s)'%goInstance._strShortName	
        self._l_ARGS_KWS_DEFAULTS = [{'kw':'goInstance', "default":None, 'help':"This is your TemplateFactory go instance", "argType":"RigFactory.go"},
                                     {'kw':'reportTimes', "default":True, 'help':"Change to report defaults", "argType":"bool"}]
        self.__dataBind__(*args, **kws)
        self._go = goInstance


class skeletonizeStep(cgmGeneral.cgmFuncCls):
    def __init__(self,*args,**kws):
        """
        """	
        super(skeletonizeStep, self).__init__(self,*args,**kws)
        goInstance = args[0]
        try:
            assert goInstance._cgmClass == 'JointFactory.go'
        except StandardError,error:
            raise StandardError,"Not a JointFactory.go : %s"%error	
        self._b_ExceptionInterupt = False	
        self._str_funcName = 'skeletonizeStep(%s)'%goInstance._strShortName	
        self._l_ARGS_KWS_DEFAULTS = [{'kw':'goInstance', "default":None, 'help':"This is your JointFactory go instance", "argType":"RigFactory.go"},
                                     {'kw':'reportTimes', "default":True, 'help':"Change to report defaults", "argType":"bool"}]
        self.__dataBind__(*args, **kws)
        self._go = goInstance


def exampleWrap(*args, **kws):
    class example(rigStep):
        def __init__(self,*args, **kws):
            """
            """	
            super(example, self).__init__(*args, **kws)
            self._str_funcName = 'example()'	
            self.__dataBind__(*args, **kws)
            self.l_funcSteps = [{'step':'Get Data','call':self._getData}]
            #The idea is to register the functions needed to be called
            #=================================================================	    

        def _getData(self):
            """
            """
            self.report()

    #We wrap it so that it autoruns and returns
    return example(*args, **kws).go()