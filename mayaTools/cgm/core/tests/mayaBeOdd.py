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
reload(cgmGeneral)
import maya.cmds as mc
from cgm.lib import curves

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as cgmValid
import time
from cgm.core.rigger.lib import joint_Utils as jntUtils
reload(jntUtils)

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
	    return cgmMeta.dupe(root) 
	    #return jntUtils.duplicateJointInPlace(root)
	
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
	    
	    cgmGeneral.report_enviornment()
	    _hitBreakPoint = False
	    for i,t in enumerate(self.l_times_1):
		_dif = t - self.l_times_2[i]
		if _hitBreakPoint is False and _dif > 0:
		    _hitBreakPoint = i
		self.log_info("Step {0} | Method 1: {1}| Method 2: {2} | Difference: {3}".format(i,"%0.3f"%t,"%0.3f"%self.l_times_2[i],"%0.3f"%_dif))
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Iterations: {0} | Method 1: {1} | Method 2: {2} | Breakpoint: Iteration {3}".format(self.int_iterations,
	                                                                                                       "%0.3f"%_m1_time,
	                                                                                                       "%0.3f"%_m2_time,
	                                                                                                       _hitBreakPoint))
    
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
	    
	    cgmGeneral.report_enviornment()	
	    _hitBreakPoint = False
	    for i,t in enumerate(self.l_times_1):
		_dif = t - self.l_times_2[i]
		if _hitBreakPoint is False and _dif > 0:
		    _hitBreakPoint = i		
		self.log_info("Step {0} | Method 1: {1}| Method 2: {2} | Difference: {3}".format(i,"%0.3f"%t,"%0.3f"%self.l_times_2[i],"%0.3f"%_dif))
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Iterations: {0} | Method 1: {1} | Method 2: {2} | Breakpoint: Iteration {3}".format(self.int_iterations,
	                                                                                                       "%0.3f"%_m1_time,
	                                                                                                       "%0.3f"%_m2_time,
	                                                                                                       _hitBreakPoint))
    
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
	    
	    cgmGeneral.report_enviornment()	
	    _hitBreakPoint = False
	    for i,t in enumerate(self.l_times_1):
		_dif = t - self.l_times_2[i]
		if _hitBreakPoint is False and _dif > 0:
		    _hitBreakPoint = i		
		self.log_info("Step {0} | Method 1: {1}| Method 2: {2} | Difference: {3}".format(i,"%0.3f"%t,"%0.3f"%self.l_times_2[i],"%0.3f"%_dif))
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Iterations: {0} | Method 1: {1} | Method 2: {2} | Breakpoint: Iteration {3}".format(self.int_iterations,
	                                                                                                       "%0.3f"%_m1_time,
	                                                                                                       "%0.3f"%_m2_time,
	                                                                                                       _hitBreakPoint))
    
    return fncWrap(*args, **kws).go()

def speedTest_simpleLocator(iterations = 100):
    import maya.cmds as mc
    import time
    
    mc.file(new=True,f=True)
    _loc = mc.spaceLocator()[0]
    l_times = []
    for i in range(iterations):
	print("On...{0}".format(i))
	
	t1 = time.clock()		
	mc.duplicate(_loc)
	t2 = time.clock()
	l_times.append(t2-t1)
	
    for i,t in enumerate(l_times):
	print("Step {0} |  {1}".format(i,"%0.3f"%t))
	
    _str_dif = l_times[-1] - l_times[0] 
    print(" [TOTAL TIME] Just maya -- {0} | Start -- {1} | End -- {2} | [Diff] -- {3} ".format("%0.3f"%(sum(l_times)),"%0.3f"%l_times[0],"%0.3f"%l_times[-1],"%0.3f"%_str_dif))
			                   
#==============================================================================================
def speedTest_mNodeCall(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_duplicate'
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
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
		
		self.l_roots_1.extend( [jntUtils.duplicateJointInPlace(_rootString,asMeta=False)] )
		
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