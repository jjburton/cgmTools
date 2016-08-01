"""
------------------------------------------
cgm.core.tests.mayaBeOdd
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
from cgm.core import cgm_General as cgmGeneral
import maya.cmds as mc
from cgm.lib import curves

from cgm.core import cgm_Meta as cgmMeta
from Red9.core import Red9_Meta as r9Meta
from cgm.core.cgmPy import validateArgs as cgmValid
import time
from cgm.core.rigger.lib import joint_Utils as jntUtils
from cgm.lib import names
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def duplicateJointChain(joint):
    mJoint = cgmMeta.cgmObject(joint)
    ml_joints = [mJoint]
    ml_children = mJoint.getAllChildren(fullPath=True, asMeta=True)
    ml_children.reverse()
    if ml_children:
	ml_joints.extend(ml_children)
	
    ml_dups = []
    
    for i,mObj in enumerate(ml_joints):
    	mDup = cgmMeta.cgmObject(mc.joint())
    	mc.delete(mc.parentConstraint(mObj.mNode,mDup.mNode))
    	mDup.rotateOrder = mObj.rotateOrder
    	mDup.jointOrient = mObj.jointOrient
    	mc.rename(mDup.mNode, mObj.getBaseName())
    	if i is 0:
    	    mDup.parent = mObj.parent	    
    	else:
    	    mDup.parent = ml_dups[-1]
    	ml_dups.append(mDup)
	
    return [ml_dups[0].mNode]

def speedTest_duplicate(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_duplicate'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'iterations',"default":10,"argType":'int','help':"How many times to duplicate"},
                                         {'kw':'childrenCount',"default":5,"argType":'int','help':"How many children"},
	                                 {'kw':'parentOnly',"default":False,"argType":'bool','help':"whether to dup parent only"}
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
                                {'step':'Build stuffs','call':self._buildStuff_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))
            self.int_children = int(cgmValid.valueArg(self.d_kws['childrenCount'],noneValid=False))
            self.b_po = cgmValid.boolArg(self.d_kws['parentOnly'],noneValid=False)            
	    
            self.l_valueBuffer = [i for i in range(self.int_iterations)]
            self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_roots_1  = []
	    self.l_roots_2 = []
	    
	def test1_func(self,root):
	    return mc.duplicate(root, po = self.b_po,un = False,ic = False, rr = True, rc = False)                
	
	def test2_func(self,root):
	    return duplicateJointChain(root)                
	
        def _buildStuff_(self):
            mi_rootJoint = cgmMeta.cgmObject(mc.joint(name = 'root'))
            mi_rootJoint.parent = False
            self.md_rootToChildren[mi_rootJoint] = []
            _last = mi_rootJoint
            for i in range(self.int_children):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = self.int_children)
                mi_child = cgmMeta.cgmObject(mc.joint(name = ' "child"%i'%i))
                self.md_rootToChildren[mi_rootJoint].append(mi_child)
                mi_child.parent = _last
		mi_child.ty = (i)
                _last = mi_child#...change for the next
                
	    self.mi_rootJoint = mi_rootJoint
	    
        def _iterate_(self):
	    _rootString = self.mi_rootJoint.mNode
	    
	    #pass 1....
            for i in range(self.int_iterations):
                self.progressBar_set(status = ("Pass 1: Iterating Duplicate %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.l_roots_1.extend( self.test1_func(_rootString) )              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
	    mc.delete(self.l_roots_1)
		
	    for i in range(self.int_iterations):
		self.progressBar_set(status = ("Pass 2: Iterating Duplicate %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.l_roots_2.extend( self.test2_func(_rootString) )              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)
		
		
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
		_dif = t - self.l_times_2[i]
		self.log_info("Step {0} | Method 1: {1}| Method 2: {2} | Difference: {3}".format(i,"%0.3f"%t,"%0.3f"%self.l_times_2[i],"%0.3f"%_dif))
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Iterations: {0} | Children: {1} | Method 1: {2} | Method 2: {3}".format(self.int_iterations,
	                                                                                           self.int_children,
	                                                                                           "%0.3f"%_m1_time,
	                                                                                           "%0.3f"%_m2_time))
    
    return fncWrap(*args, **kws).go()

def speedTest_duplicateInPlace(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_duplicateInPlace'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'iterations',"default":10,"argType":'int','help':"How many times to duplicate"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
                                {'step':'Build stuffs','call':self._buildStuff_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))	    
            self.l_valueBuffer = [i for i in range(self.int_iterations)]
            self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_roots_1  = []
	    self.l_roots_2 = []
	    
	def test1_func(self,root):
	    return mc.duplicate(root, po = True,un = False,ic = False, rr = True, rc = False)                
	
	def test2_func(self,root):
	    #return cgmMeta.dupe(root) 
	    return jntUtils.duplicateJointInPlace(root)
	
        def _buildStuff_(self):
            mi_rootJoint = cgmMeta.cgmObject(mc.joint(name = 'root'))
            mi_rootJoint.parent = False
            self.md_rootToChildren[mi_rootJoint] = []
            _last = mi_rootJoint
	    self.ml_children = []
            for i in range(9):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = 9)
                mi_child = cgmMeta.cgmObject(mc.joint(name = ' "child"%i'%i))
                self.md_rootToChildren[mi_rootJoint].append(mi_child)
                mi_child.parent = _last
		mi_child.ty = (i)
                _last = mi_child#...change for the next
                self.ml_children.append(mi_child)
		
	    self.mi_rootJoint = mi_rootJoint
	    
        def _iterate_(self):
	    _jointToDup = self.ml_children[5].mNode
	    
	    #pass 1....
            for i in range(self.int_iterations):
                self.progressBar_set(status = ("Pass 1: Iterating Duplicate %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.l_roots_1.extend( self.test1_func(_jointToDup) )              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
	    #mc.delete(self.l_roots_1)
		
	    for i in range(self.int_iterations):
		self.progressBar_set(status = ("Pass 2: Iterating Duplicate %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.l_roots_2.extend( [self.test2_func(_jointToDup)] )              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)
		
		
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    _hitBreakPoint = None
	    for i,t in enumerate(self.l_times_1):
		_dif = t - self.l_times_2[i]
		if _hitBreakPoint is None and _dif > 0:
		    _hitBreakPoint = i
		self.log_info("Step {0} | Method 1: {1}| Method 2: {2} | Difference: {3}".format(i,"%0.3f"%t,"%0.3f"%self.l_times_2[i],"%0.3f"%_dif))
	    
	    self.log_info("Iterations: {0} | Breakpoint Step: {1}".format(self.int_iterations,
	                                                                  _hitBreakPoint))
	    self.log_info("Method 1 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_1[0],
	                                                                                            "%0.3f"%self.l_times_1[-1],
	                                                                                            "%0.3f"%(self.l_times_1[-1] - self.l_times_1[0]),
	                                                                                            "%0.3f"%_m1_time))
	    self.log_info("Method 2 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_2[0],
	                                                                                            "%0.3f"%self.l_times_2[-1],
	                                                                                            "%0.3f"%(self.l_times_2[-1] - self.l_times_2[0]),
	                                                                                            "%0.3f"%_m2_time))    
	    self.log_info("Compare  |   Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_2[0] - self.l_times_1[0]),
	                                                                                            "%0.3f"%(self.l_times_2[-1] - self.l_times_1[-1]),
	                                                                                            "%0.3f"%(_m2_time - _m1_time)))   
	    cgmGeneral.report_enviornmentSingleLine()
    return fncWrap(*args, **kws).go()

def speedTest_duplicateCurve(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_duplicateCurve'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'iterations',"default":10,"argType":'int','help':"How many times to duplicate"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
                                {'step':'Build stuffs','call':self._buildStuff_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))	    
            self.l_valueBuffer = [i for i in range(self.int_iterations)]
            self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_roots_1  = []
	    self.l_roots_2 = []
	    
	def test1_func(self,root):
	    return mc.duplicate(root, po = True,un = False,ic = False, rr = True, rc = False)                
	
	def test2_func(self,root):
	    return cgmMeta.dupe(root)                
	
        def _buildStuff_(self):
            mi_root = cgmMeta.cgmObject(curves.createCurve('sphere'))
            mi_root.parent = False
            self.md_rootToChildren[mi_root] = []
            _last = mi_root		
	    self.mi_root = mi_root
	    
        def _iterate_(self):	    
	    #pass 1....
	    _toDup = self.mi_root.mNode
	    
            for i in range(self.int_iterations):
                self.progressBar_set(status = ("Pass 1: Iterating Duplicate %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.l_roots_1.extend( self.test1_func(_toDup) )              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
	    mc.file(new=True,f=True)
	    self._buildStuff_()
		
	    for i in range(self.int_iterations):
		self.progressBar_set(status = ("Pass 2: Iterating Duplicate %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.l_roots_2.extend( [self.test2_func(_toDup)] )              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)
		
		
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    _hitBreakPoint = None
	    for i,t in enumerate(self.l_times_1):
		_dif = t - self.l_times_2[i]
		if _hitBreakPoint is None and _dif > 0:
		    _hitBreakPoint = i		
		self.log_info("Step {0} | Method 1: {1}| Method 2: {2} | Difference: {3}".format(i,"%0.3f"%t,"%0.3f"%self.l_times_2[i],"%0.3f"%_dif))
	    self.log_info("Iterations: {0} | Breakpoint Step: {1}".format(self.int_iterations,
	                                                                  _hitBreakPoint))
	    self.log_info("Method 1 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_1[0],
	                                                                                            "%0.3f"%self.l_times_1[-1],
	                                                                                            "%0.3f"%(self.l_times_1[-1] - self.l_times_1[0]),
	                                                                                            "%0.3f"%_m1_time))
	    self.log_info("Method 2 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_2[0],
	                                                                                            "%0.3f"%self.l_times_2[-1],
	                                                                                            "%0.3f"%(self.l_times_2[-1] - self.l_times_2[0]),
	                                                                                            "%0.3f"%_m2_time))    
	    self.log_info("Compare  |   Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_2[0] - self.l_times_1[0]),
	                                                                                            "%0.3f"%(self.l_times_2[-1] - self.l_times_1[-1]),
	                                                                                            "%0.3f"%(_m2_time - _m1_time)))   
	    cgmGeneral.report_enviornmentSingleLine()
    
    return fncWrap(*args, **kws).go()

def speedTest_duplicateLocator(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_duplicateLocator'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'iterations',"default":10,"argType":'int','help':"How many times to duplicate"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
                                {'step':'Build stuffs','call':self._buildStuff_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))	    
            self.l_valueBuffer = [i for i in range(self.int_iterations)]
            self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_roots_1  = []
	    self.l_roots_2 = []
	    
	def test1_func(self,root):
	    return mc.duplicate(root, po = True,un = False,ic = False, rr = True, rc = False)                
	
	def test2_func(self,root):
	    return cgmMeta.dupe(root)                
	
        def _buildStuff_(self):
            mi_root = cgmMeta.cgmObject(mc.spaceLocator()[0])
            mi_root.parent = False
            self.md_rootToChildren[mi_root] = []
            _last = mi_root		
	    self.mi_root = mi_root
	    
        def _iterate_(self):	    
	    #pass 1....
	    _toDup = self.mi_root.mNode
	    
            for i in range(self.int_iterations):
                self.progressBar_set(status = ("Pass 1: Iterating Duplicate %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.l_roots_1.extend( self.test1_func(_toDup) )              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
	    mc.delete(self.l_roots_1)
		
	    for i in range(self.int_iterations):
		self.progressBar_set(status = ("Pass 2: Iterating Duplicate %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.l_roots_2.extend( [self.test2_func(_toDup)] )              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)
		
		
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    _hitBreakPoint = None
	    for i,t in enumerate(self.l_times_1):
		_dif = t - self.l_times_2[i]
		if _hitBreakPoint is None and _dif > 0:
		    _hitBreakPoint = i		
		self.log_info("Step {0} | Method 1: {1}| Method 2: {2} | Difference: {3}".format(i,"%0.3f"%t,"%0.3f"%self.l_times_2[i],"%0.3f"%_dif))
	    self.log_info("Iterations: {0} | Breakpoint Step: {1}".format(self.int_iterations,
	                                                                  _hitBreakPoint))
	    self.log_info("Method 1 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_1[0],
	                                                                                            "%0.3f"%self.l_times_1[-1],
	                                                                                            "%0.3f"%(self.l_times_1[-1] - self.l_times_1[0]),
	                                                                                            "%0.3f"%_m1_time))
	    self.log_info("Method 2 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_2[0],
	                                                                                            "%0.3f"%self.l_times_2[-1],
	                                                                                            "%0.3f"%(self.l_times_2[-1] - self.l_times_2[0]),
	                                                                                            "%0.3f"%_m2_time))    
	    self.log_info("Compare  |   Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_2[0] - self.l_times_1[0]),
	                                                                                            "%0.3f"%(self.l_times_2[-1] - self.l_times_1[-1]),
	                                                                                            "%0.3f"%(_m2_time - _m1_time)))   
	    cgmGeneral.report_enviornmentSingleLine()   
    return fncWrap(*args, **kws).go()

import maya.cmds as mc
import maya.mel as mel
import time
def speedTest_simpleLocator(iterations = 100):
    mc.file(new=True,f=True)
    _loc = mc.spaceLocator()[0]
    l_times = []
    
    for i in range(iterations):
	print("On...{0}".format(i))
	
	t1 = time.clock()		
	mc.duplicate(_loc, po = False, ic = False, un = False)
	t2 = time.clock()
	l_times.append(t2-t1)
	
    for i,t in enumerate(l_times):
	print("Step {0} |  {1}".format(i,"%0.3f"%t))
	
    _str_dif = l_times[-1] - l_times[0] 
    print(" CGM Simple loc duplication -- {0} | Start -- {1} | End -- {2} | [Diff] -- {3} ".format("%0.3f"%(sum(l_times)),"%0.3f"%l_times[0],"%0.3f"%l_times[-1],"%0.3f"%_str_dif))
    print(" Maya: {0} | OS: {1}".format(mel.eval( 'about -%s'%'version'), mel.eval( 'about -%s'%'operatingSystemVersion')))
			                   
#==============================================================================================
def speedTest_mNodeCall(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_mNodeCall'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = False
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'iterations',"default":10,"argType":'int','help':"How many times to duplicate"},
                                         {'kw':'childrenCount',"default":5,"argType":'int','help':"How many children"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
                                {'step':'Build stuffs','call':self._buildStuff_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))
            self.int_children = int(cgmValid.valueArg(self.d_kws['childrenCount'],noneValid=False))
	    
            self.l_valueBuffer = [i for i in range(self.int_iterations)]
            self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_roots_1  = []
	    self.l_roots_2 = []
	    
	def test1_func(self,string):
	    return string            
	
	def test2_func(self,mObj):
	    return mObj.mNode           
	
        def _buildStuff_(self):
            mi_rootJoint = cgmMeta.cgmObject(mc.joint(name = 'root'))
            mi_rootJoint.parent = False
            self.md_rootToChildren[mi_rootJoint] = []
            _last = mi_rootJoint
            for i in range(self.int_children):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = self.int_children)
                mi_child = cgmMeta.cgmObject(mc.joint(name = ' "child"%i'%i))
                self.md_rootToChildren[mi_rootJoint].append(mi_child)
                mi_child.parent = _last
		mi_child.ty = (i)
                _last = mi_child#...change for the next
		
	    self._toCall = self.md_rootToChildren[mi_rootJoint][4]   
	    self.mi_rootJoint = mi_rootJoint
	    
        def _iterate_(self):
	    _rootString = self._toCall.mNode
	    
	    #pass 1....
            for i in range(self.int_iterations):
                self.progressBar_set(status = ("Pass 1: Iterating Call %i"%i), progress = i, maxValue = self.int_iterations)		
		t1 = time.clock()	
		self.test1_func(_rootString)              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
		t1 = time.clock()	
		self.l_roots_2.extend( [self.test2_func(self._toCall)] )              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)		
		
		#self.l_roots_1.extend( [jntUtils.duplicateJointInPlace(_rootString,asMeta=False)] )
		self.l_roots_1.extend( [self._toCall.doDuplicate(po = True).mNode] )
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
		_dif = t - self.l_times_2[i]
		self.log_info("Step {0} | Method 1: {1}| Method 2: {2} | Difference: {3}".format(i,"%0.3f"%t,"%0.3f"%self.l_times_2[i],"%0.3f"%_dif))
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Iterations: {0} | Children: {1} | Method 1: {2} | Method 2: {3}".format(self.int_iterations,
	                                                                                           self.int_children,
	                                                                                           "%0.3f"%_m1_time,
	                                                                                           "%0.3f"%_m2_time))
    
    return fncWrap(*args, **kws).go()


def speedTest_substantiation(*args, **kws):
    """
    Test for seeing how substantiation speeds are affected
    """
    _d_build = {'network':'network'}    
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_substantiation'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'targetCount',"default":10,"argType":'int','help':"How many objects to create"},
                                         {'kw':'build',"default":'network',"argType":'string','help':"What kind of base node to build to test"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
                                {'step':'Build stuffs','call':self._buildStuff_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            #self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))
            self.int_targetCount = int(cgmValid.valueArg(self.d_kws['targetCount'],noneValid=False))
	    self.str_nodeType = self.d_kws['build']
	    
            #self.l_valueBuffer = [i for i in range(self.int_iterations)]
            #self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            #self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_times_3 = []
	    self.l_times_4 = []
	    self.l_roots_1  = []
	    self.l_roots_2 = []
	    self.l_roots_3 = []
	    self.l_roots_4 = []
	    self.l_objects = []
	    
	def test1_func(self,string):
	    return r9Meta.MetaClass(string)          
	
	def test2_func(self,string):
	    #return cgmMeta_optimize.cgmNode2(string)
	    #return cgmMeta.cgmNode(string)
	    #return cgmMeta.validateObjArgOLD(string,'cgmObject',setClass = True)	
	    return cgmMeta.cgmNode(string)	    
	def test22_func(self,string):
	    pass
	    #return cgmMeta.cgmObject(string)
	def call2_func(self):pass
	
	def test3_func(self,string):
	    #return string
	    #cgmMeta_optimize	    
	    #return string
	    #return cgmMeta.cgmObject(string)
	    #return cgmMeta_optimize.cgmNode2(string)
	    return cgmMeta.validateObjArg(string)	    	    
	    #return cgmMeta.validateObjArg(string)
	
        def _buildStuff_(self):
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = self.int_targetCount)
                #self.l_objects.append(mc.createNode( self.str_nodeType, n = "obj_{0}".format(i) ))
		_jnt = mc.joint(n = "obj_{0}".format(i) )
		mc.select(cl=True)
		self.l_objects.append(_jnt)
	    
        def _iterate_(self):
	    self.call2_func = self.test2_func
	    """if self.str_nodeType == 'network':
		self.call2_func = self.test2_func
	    else:
		self.call2_func = self.test22_func"""
		
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Pass 1: Substantiating Call %i"%i), progress = i, maxValue = self.int_targetCount)		
		
		t1 = time.clock()	
		self.test1_func(self.l_objects[i])              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
		t1 = time.clock()	
		self.call2_func(self.l_objects[i])              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)	
		
		t1 = time.clock()	
		self.test3_func(self.l_objects[i])              
		t2 = time.clock()
		self.l_times_3.append(t2-t1)	
		
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    _m3_time = sum(self.l_times_3)
	    
	    #cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
                self.progressBar_set(status = ("Pass 1: Reporting %i"%i), progress = i, maxValue = len(self.l_times_1))				
		_dif1 = t - self.l_times_2[i]
		_dif2 = t - self.l_times_3[i]
		
		self.log_info("Step {0} | MetaClass: {1}| cgmNode: {2}(d{4}) | validate: {3}(d{5})".format(i,"%0.4f"%t,
		                                                                                           "%0.4f"%self.l_times_2[i],
		                                                                                           "%0.4f"%self.l_times_3[i],		                                                                                           
		                                                                                           "%0.4f"%_dif1,
		                                                                                           "%0.4f"%_dif2,
		                                                                                           ))
	    
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Count: {0} | MetaClass: {1} | cgmNode: {2} | validate: {3}".format(self.int_targetCount,
	                                                                                            "%0.4f"%_m1_time,
	                                                                                            "%0.4f"%_m2_time,
	                                                                                            "%0.4f"%_m3_time))
	    self.log_info("Method 1 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.4f"%self.l_times_1[0],
	                                                                                            "%0.4f"%self.l_times_1[-1],
	                                                                                            "%0.4f"%(self.l_times_1[-1] - self.l_times_1[0]),
	                                                                                            "%0.4f"%_m1_time))
	    self.log_info("Method 2 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.4f"%self.l_times_2[0],
                                                                                                    "%0.4f"%self.l_times_2[-1],
                                                                                                    "%0.4f"%(self.l_times_2[-1] - self.l_times_2[0]),
                                                                                                    "%0.4f"%_m2_time))
	    self.log_info("Method 3 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.4f"%self.l_times_3[0],
	                                                                                            "%0.4f"%self.l_times_3[-1],
	                                                                                            "%0.4f"%(self.l_times_3[-1] - self.l_times_3[0]),
	                                                                                            "%0.4f"%_m3_time))    	    
	    self.log_info("Compare 2:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.4f"%(self.l_times_1[0] - self.l_times_2[0]),
                                                                                                    "%0.4f"%(self.l_times_1[-1] - self.l_times_2[-1]),
                                                                                                    "%0.4f"%(_m1_time - _m2_time)))  
	    self.log_info("Compare 3:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.4f"%(self.l_times_1[0] - self.l_times_3[0]),
	                                                                                             "%0.4f"%(self.l_times_1[-1] - self.l_times_3[-1]),
	                                                                                             "%0.4f"%(_m1_time - _m3_time)))   	    	    
    
    return fncWrap(*args, **kws).go()


def speedTest_cgmValidateObjArgKWS(*args, **kws):
    """
    Test for seeing how substantiation speeds are affected
    """
    _d_build = {'network':'network'}    
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_cgmValidateObjArgKWS'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'targetCount',"default":10,"argType":'int','help':"How many objects to create"},
                                         {'kw':'build',"default":'network',"argType":'string','help':"What kind of base node to build to test"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
                                #{'step':'Build stuffs','call':self._buildStuff_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            #self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))
            self.int_targetCount = int(cgmValid.valueArg(self.d_kws['targetCount'],noneValid=False))
	    self.str_nodeType = self.d_kws['build']
	    
            #self.l_valueBuffer = [i for i in range(self.int_iterations)]
            #self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            #self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_times_3 = []
	    self.l_times_4 = []
	    self.l_roots_1  = []
	    self.l_roots_2 = []
	    self.l_roots_3 = []
	    self.l_roots_4 = []
	    self.l_objects = []
	    
	def test1_func(self,string):
	    return cgmMeta.validateObjArg(string)          
	
	def test2_func(self,string):
	    return cgmMeta.validateObjArgOLD(string,mType = "cgmControl", setClass = True)
	    #return cgmMeta.validateObjArg(string)          
	    #return cgmMeta.validateObjArg(string,mType = "cgmNode")          
	
	def test3_func(self,string):
	    return cgmMeta.validateObjArg(string,mType = "cgmControl", setClass = True)          	    
	    #return cgmMeta.validateObjArg(string, mayaType = 'network')          
	
        def _buildStuff_(self):
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = self.int_targetCount)
                self.l_objects.append(mc.createNode( self.str_nodeType, n = "obj_{0}".format(i) ))
		
	    
        def _iterate_(self):	
		
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Pass 1: Substantiating Call %i"%i), progress = i, maxValue = self.int_targetCount)		
		self.l_objects.append(mc.createNode( self.str_nodeType, n = "obj_{0}".format(i) ))
		t1 = time.clock()	
		self.test1_func(self.l_objects[i])              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
		#_string = mc.createNode( self.str_nodeType, n = "old_{0}".format(i) )
		_string = cgmMeta.cgmObject(n = "old_{0}".format(i))
		t1 = time.clock()
		self.test2_func(_string)              
		#self.test2_func(self.l_objects[i])              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)	
		
		#_string = mc.createNode( self.str_nodeType, n = "new_{0}".format(i) )
		_string = cgmMeta.cgmObject(n = "new_{0}".format(i))		
		t1 = time.clock()
		self.test3_func(_string)  
		#self.test3_func(self.l_objects[i])              
		t2 = time.clock()
		self.l_times_3.append(t2-t1)	

	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    _m3_time = sum(self.l_times_3)
	    
	    #cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
		_dif1 = t - self.l_times_2[i]
		_dif2 = t - self.l_times_3[i]
		
		self.log_info("Step {0} | Base 1: {1}| call2: {2}({4}) | call3: {3}({5})".format(i,"%0.3f"%t,
		                                                                                           "%0.3f"%self.l_times_2[i],
		                                                                                           "%0.3f"%self.l_times_3[i],		                                                                                           
		                                                                                           "%0.3f"%_dif1,
		                                                                                           "%0.3f"%_dif2,
		                                                                                           ))
	    
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Count: {0} | Base: {1} | call2: {2} | call3: {3}".format(self.int_targetCount,
	                                                                            "%0.3f"%_m1_time,
	                                                                            "%0.3f"%_m2_time,
	                                                                            "%0.3f"%_m3_time))
	    self.log_info("Method 1 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_1[0],
			                                                                                        "%0.3f"%self.l_times_1[-1],
			                                                                                        "%0.3f"%(self.l_times_1[-1] - self.l_times_1[0]),
			                                                                                        "%0.3f"%_m1_time))
	    self.log_info("Method 2 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_2[0],
                                                                                                    "%0.3f"%self.l_times_2[-1],
                                                                                                    "%0.3f"%(self.l_times_2[-1] - self.l_times_2[0]),
                                                                                                    "%0.3f"%_m2_time))
	    self.log_info("Method 3 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_3[0],
	                                                                                            "%0.3f"%self.l_times_3[-1],
	                                                                                            "%0.3f"%(self.l_times_3[-1] - self.l_times_3[0]),
	                                                                                            "%0.3f"%_m3_time))    	    
	    self.log_info("Compare 2:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_2[0] - self.l_times_1[0]),
                                                                                                    "%0.3f"%(self.l_times_2[-1] - self.l_times_1[-1]),
                                                                                                    "%0.3f"%(_m2_time - _m1_time)))  
	    self.log_info("Compare 3:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_3[0] - self.l_times_1[0]),
	                                                                                             "%0.3f"%(self.l_times_3[-1] - self.l_times_1[-1]),
	                                                                                             "%0.3f"%(_m3_time - _m1_time)))   	    	    
    
    return fncWrap(*args, **kws).go()

import cgm
def speedTest_reloadMetaFile(iterations = 100):
    """
    Test to see how meta reloading affects file new/open
    """
    l_times = []
    t_start = time.clock()
    for i in range(iterations):
	log.info("On...{0}".format(i))
	cgm.core._reload()
	
	t1 = time.clock()
	#r9Meta.MetaClass(name = 'test_{0}'.format(i),nodeType='network')
	mc.file(new=True,f=True)
	
	t2 = time.clock()
	l_times.append(t2-t1)
	
    t_end = time.clock()
	
    #for i,t in enumerate(l_times):
	#log.info("Step {0} |  {1}".format(i,"%0.3f"%t))
	
    _str_dif = l_times[-1] - l_times[0] 
    _l_diffs = []
    for i in range(len(l_times)-1):
	_l_diffs.append(l_times[i] - l_times[i+1])
    _averageDiff = sum(_l_diffs)/len(_l_diffs)
    _totalTime = t_end - t_start
    _totalIterTime = (sum(l_times)) 
    log.info(" speedTest_reloadMeta -- {0} | Start -- {1} | End -- {2} | [Diff] -- {3} | AverageIncrease: {4}".format("%0.3f"%(sum(l_times)),
                                                                                                                            "%0.3f"%l_times[0],
                                                                                                                            "%0.3f"%l_times[-1],
                                                                                                                            "%0.3f"%_str_dif,
                                                                                                                            _averageDiff))
    log.info("Time total: {0} | IterTime: {1} | Unaccounted: {2}".format("%0.3f"%(_totalTime),
                                                                         "%0.3f"%(_totalIterTime),
                                                                         "%0.3f"%(_totalTime - _totalIterTime)))
    log.info(" Maya: {0} | OS: {1}".format(mel.eval( 'about -%s'%'version'), mel.eval( 'about -%s'%'operatingSystemVersion')))
			      
			      
def speedTest_reloadMeta(iterations = 100,):
    """
    Test to see how meta reloading affects file new/open
    """
    l_times = []
    t_start = time.clock()
    for i in range(iterations):
	log.info("On...{0}".format(i))
	#cgm.core._reload()
	
	t1 = time.clock()
	r9Meta.MetaClass(name = 'test_{0}'.format(i),nodeType='transform')
	
	t2 = time.clock()
	l_times.append(t2-t1)
	
    t_end = time.clock()
	
    #for i,t in enumerate(l_times):
	#log.info("Step {0} |  {1}".format(i,"%0.3f"%t))
	
    _str_dif = l_times[-1] - l_times[0] 
    _l_diffs = []
    for i in range(len(l_times)-1):
	_l_diffs.append(l_times[i] - l_times[i+1])
    _averageDiff = sum(_l_diffs)/len(_l_diffs)
    _totalTime = t_end - t_start
    _totalIterTime = (sum(l_times)) 
    log.info(" speedTest_reloadMeta -- {0} | Start -- {1} | End -- {2} | [Diff] -- {3} | AverageIncrease: {4}".format("%0.3f"%(sum(l_times)),
                                                                                                                            "%0.3f"%l_times[0],
                                                                                                                            "%0.3f"%l_times[-1],
                                                                                                                            "%0.3f"%_str_dif,
                                                                                                                            _averageDiff))
    log.info("Time total: {0} | IterTime: {1} | Unaccounted: {2}".format("%0.3f"%(_totalTime),
                                                                         "%0.3f"%(_totalIterTime),
                                                                         "%0.3f"%(_totalTime - _totalIterTime)))
    log.info(" Maya: {0} | OS: {1}".format(mel.eval( 'about -%s'%'version'), mel.eval( 'about -%s'%'operatingSystemVersion')))
			      
			      
def speedTest_conversion(*args, **kws):
    """
    Test for seeing how substantiation speeds are affected
    """
    _d_build = {'network':'network'}    
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_conversion'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'targetCount',"default":10,"argType":'int','help':"How many objects to create"},
                                         {'kw':'build',"default":'network',"argType":'string','help':"What kind of base node to build to test"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            #self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))
            self.int_targetCount = int(cgmValid.valueArg(self.d_kws['targetCount'],noneValid=False))
	    self.str_nodeType = self.d_kws['build']
	    
            #self.l_valueBuffer = [i for i in range(self.int_iterations)]
            #self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            #self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_objects = []
	    
	def test1_func(self,string):
	    return r9Meta.convertMClassType(string,cgmMeta.cgmNode)          
	
	def test2_func(self,string):
	    return cgmMeta.validateObjArg(string,cgmMeta.cgmNode, setClass = True)      
	       
        def _iterate_(self):	
		
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Pass 1: Substantiating Call %i"%i), progress = i, maxValue = self.int_targetCount)		
		#self.l_objects.append(mc.createNode( self.str_nodeType, n = "obj_{0}".format(i) ))
		_string = r9Meta.MetaClass(name  = "r9_{0}".format(i), nodeType = 'network')
		t1 = time.clock()	
		self.test1_func(_string)              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
		#_string = mc.createNode( self.str_nodeType, n = "old_{0}".format(i) )
		_string = r9Meta.MetaClass(name = "cgm_{0}".format(i), nodeType = 'network')
		t1 = time.clock()
		self.test2_func(_string)              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)	
				

	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    #cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
		_dif1 = t - self.l_times_2[i]
		
		self.log_info("Step {0} | Base 1: {1}| call2: {2}({3}) |".format(i,"%0.3f"%t,
		                                                                 "%0.3f"%self.l_times_2[i],
		                                                                 "%0.3f"%_dif1,
		                                                                 ))
	    
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Count: {0} | Base: {1} | call2: {2}".format(self.int_targetCount,
	                                                               "%0.3f"%_m1_time,
	                                                               "%0.3f"%_m2_time))
	    self.log_info("Method 1 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_1[0],
	                                                                                            "%0.3f"%self.l_times_1[-1],
	                                                                                            "%0.3f"%(self.l_times_1[-1] - self.l_times_1[0]),
	                                                                                            "%0.3f"%_m1_time))
	    self.log_info("Method 2 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_2[0],
                                                                                                    "%0.3f"%self.l_times_2[-1],
                                                                                                    "%0.3f"%(self.l_times_2[-1] - self.l_times_2[0]),
                                                                                                    "%0.3f"%_m2_time))
	  
	    self.log_info("Compare 2:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_2[0] - self.l_times_1[0]),
                                                                                                    "%0.3f"%(self.l_times_2[-1] - self.l_times_1[-1]),
                                                                                                    "%0.3f"%(_m2_time - _m1_time)))  
	  
    return fncWrap(*args, **kws).go()


def speedTest_jointDepth(*args, **kws):
    """
    Test for seeing how substantiation speeds are affected
    """
    _d_build = {'network':'network'}    
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_jointDepth'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'targetCount',"default":10,"argType":'int','help':"How many objects to create"},
                                         {'kw':'build',"default":'network',"argType":'string','help':"What kind of base node to build to test"},
                                         ]	    
            self.__dataBind__(*args, **kws)
            
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            #self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))
            self.int_targetCount = int(cgmValid.valueArg(self.d_kws['targetCount'],noneValid=False))
	    self.str_nodeType = self.d_kws['build']
	    
            #self.l_valueBuffer = [i for i in range(self.int_iterations)]
            #self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            #self.md_rootToChildren = {}
            self.l_times_1 = []
	    self.l_times_2 = []
	    self.l_times_3 = []
	    self.l_times_4 = []
	    self.l_roots_1  = []
	    self.l_roots_2 = []
	    self.l_roots_3 = []
	    self.l_roots_4 = []
	    self.l_objects = []
	    self.md_rootToChildren={}
	def test1_func(self,string):
	    return r9Meta.MetaClass(string)          
	
	def test2_func(self,string):
	    #_buffer = r9Meta.MetaClass(string)
	    #r9Meta.registerMClassNodeCache(_buffer)
	    #return string
	    return cgmMeta.cgmNode(string)
	    #return cgmMeta._d_KWARG_asMeta
	    #return r9Meta.RED9_META_NODECACHE
	    #return cgmMeta.validateObjArg(string,mType = "cgmNode")          
	
	def test3_func(self,string):
	    #return string
	    return cgmMeta.validateObjArg(string, 'cgmNode')
	    #return r9Meta.MetaClass(string)          
	    #return cgmMeta.validateObjArg(string,'cgmNode', setClass = False)          	    
	    #return cgmMeta.validateObjArg(string, mayaType = 'network')          
	
        def _buildStuff_(self):
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = self.int_targetCount)
                self.l_objects.append(mc.createNode( self.str_nodeType, n = "obj_{0}".format(i) ))
		
	    
        def _iterate_(self):	
	    mi_rootJoint = cgmMeta.cgmObject(mc.joint(name = 'root'))
	    mi_rootJoint.parent = False
	    self.md_rootToChildren[mi_rootJoint] = []
	    _last = mi_rootJoint	    
		
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Pass 1: Substantiating Call %i"%i), progress = i, maxValue = self.int_targetCount)		
		mi_child = cgmMeta.cgmObject(mc.joint(name = ' "child"%i'%i))
		self.md_rootToChildren[mi_rootJoint].append(mi_child)
		mi_child.parent = _last
		mi_child.ty = (i) * .1
		_last = names.getShortName(mi_child.mNode)#...change for the next		
		#_last = mi_child.mNode
		
		self.l_objects.append(mc.createNode( self.str_nodeType, n = "obj_{0}".format(i) ))
		t1 = time.clock()	
		self.test1_func(_last)              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
		#_string = mc.createNode( self.str_nodeType, n = "old_{0}".format(i) )
		t1 = time.clock()
		self.test2_func(_last)              
		#self.test2_func(self.l_objects[i])              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)	
		
		#_string = mc.createNode( self.str_nodeType, n = "new_{0}".format(i) )
		t1 = time.clock()
		self.test3_func(_last)  
		#self.test3_func(self.l_objects[i])              
		t2 = time.clock()
		self.l_times_3.append(t2-t1)	
		
		self._str_last = _last

	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    _m3_time = sum(self.l_times_3)
	    
	    #cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
		_dif1 = t - self.l_times_2[i]
		_dif2 = t - self.l_times_3[i]
		
		self.log_info("Step {0} | Base 1: {1}| call2: {2}({4}) | call3: {3}({5})".format(i,"%0.3f"%t,
		                                                                                           "%0.3f"%self.l_times_2[i],
		                                                                                           "%0.3f"%self.l_times_3[i],		                                                                                           
		                                                                                           "%0.3f"%_dif1,
		                                                                                           "%0.3f"%_dif2,
		                                                                                           ))
	    self.log_info("last: {0}".format(self._str_last))
		
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Count: {0} | Base: {1} | call2: {2} | call3: {3}".format(self.int_targetCount,
	                                                                            "%0.3f"%_m1_time,
	                                                                            "%0.3f"%_m2_time,
	                                                                            "%0.3f"%_m3_time))
	    self.log_info("Method 1 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_1[0],
			                                                                                        "%0.3f"%self.l_times_1[-1],
			                                                                                        "%0.3f"%(self.l_times_1[-1] - self.l_times_1[0]),
			                                                                                        "%0.3f"%_m1_time))
	    self.log_info("Method 2 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_2[0],
                                                                                                    "%0.3f"%self.l_times_2[-1],
                                                                                                    "%0.3f"%(self.l_times_2[-1] - self.l_times_2[0]),
                                                                                                    "%0.3f"%_m2_time))
	    self.log_info("Method 3 | Start: {0} | End: {1} | Difference: {2} | Total: {3} ".format("%0.3f"%self.l_times_3[0],
	                                                                                            "%0.3f"%self.l_times_3[-1],
	                                                                                            "%0.3f"%(self.l_times_3[-1] - self.l_times_3[0]),
	                                                                                            "%0.3f"%_m3_time))    	    
	    self.log_info("Compare 2:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_2[0] - self.l_times_1[0]),
                                                                                                    "%0.3f"%(self.l_times_2[-1] - self.l_times_1[-1]),
                                                                                                    "%0.3f"%(_m2_time - _m1_time)))  
	    self.log_info("Compare 3:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_3[0] - self.l_times_1[0]),
	                                                                                             "%0.3f"%(self.l_times_3[-1] - self.l_times_1[-1]),
	                                                                                             "%0.3f"%(_m3_time - _m1_time)))   	    	    
    
    return fncWrap(*args, **kws).go()