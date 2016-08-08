"""
------------------------------------------
cgm.core.tests.mayaBeOdd
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import maya.cmds as mc
from cgm.core import cgm_General as cgmGeneral
from Red9.core import Red9_Meta as r9Meta
import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


import maya.mel as mel

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
            #self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))
            #self.int_children = int(cgmValid.valueArg(self.d_kws['childrenCount'],noneValid=False))
	    self.int_iterations = int(self.d_kws['iterations'])
	    self.int_children = int(self.d_kws['childrenCount'])	    
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
            mi_rootJoint = r9Meta.MetaClass(mc.joint(name = 'root'))
	    #mc.parent(mi_rootJoint.mNode,world = True)
            #mi_rootJoint.parent = False
            self.md_rootToChildren[mi_rootJoint] = []
            _last = mi_rootJoint
            for i in range(self.int_children):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = self.int_children)
                mi_child = r9Meta.MetaClass(mc.joint(name = ' "child"%i'%i))
                self.md_rootToChildren[mi_rootJoint].append(mi_child)
                #mi_child.parent = _last
		try:mc.parent(mi_child.mNode,_last.mNode)
		except:pass
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
		#self.l_roots_1.extend( [self._toCall.doDuplicate(po = True).mNode] )
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
                                #{'step':'Build stuffs','call':self._buildStuff_},
	                        {'step':'Iterate','call':self._iterate_},
	                        {'step':'Report','call':self._reportHowMayaIsStupid_}]

        def _validate_(self):
	    mc.file(new=True,f=True)
            #self.int_iterations = int(cgmValid.valueArg(self.d_kws['iterations'],noneValid=False))
            self.int_targetCount = int(self.d_kws['targetCount'])
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
	    #return r9Meta.MetaClass(string,autofill='messageOnly')
	    return r9Meta.MetaClass(string) 
        def _buildStuff_(self):
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = self.int_targetCount)
                #self.l_objects.append(mc.createNode( self.str_nodeType, n = "obj_{0}".format(i) ))
		self.l_objects.append(mc.joint(n = "obj_{0}".format(i) ))
	    
        def _iterate_(self):	
	    self.call2_func = self.test2_func
	    _first = mc.joint(n = "first")
	    #_first = mc.createNode('transform',n = "first")
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Pass 1: Substantiating Call %i"%i), progress = i, maxValue = self.int_targetCount)		
		mc.select(cl=True)
		string = mc.joint(n = "baseobj_{0}".format(i))
		if i:
		    for ii in (range(i)):
			string = mc.joint(n = "obj_{0}".format(i))
		#mc.parent(string,world = True)
		#string = mc.createNode('network',n = "obj_{0}".format(i))
		#string = mc.createNode('transform',n = "obj_{0}".format(i))
		#string = mc.createNode('transform',n = "sameName".format(i))
		#_group = mc.group(n = "obj_{0}".format(i), em=True)
		#string = mc.parent(string,_group)[0]
		t1 = time.clock()	
		self.test1_func(_first)              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
		t1 = time.clock()	
		#self.l_roots_2.extend( [self.test2_func(self._toCall)] )  
		self.call2_func(string)              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)	
			
		
		
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    #cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
		_dif1 = t - self.l_times_2[i]
		
		self.log_info("Step {0} | allAttrs: {1}| messageOnly: {2}(d{3}) ".format(i,"%0.3f"%t,
		                                                                "%0.3f"%self.l_times_2[i],
		                                                                "%0.3f"%_dif1,
		                                                                ))
	    
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Count: {0} | allAttrs: {1} | messageOnly: {2}".format(self.int_targetCount,
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
	    self.log_info("Compare 2:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_1[0] - self.l_times_2[0]),
                                                                                                    "%0.3f"%(self.l_times_1[-1] - self.l_times_2[-1]),
                                                                                                    "%0.3f"%(_m1_time - _m2_time)))  
	    
    
    return fncWrap(*args, **kws).go()

def speedTest_cacheReturn(*args, **kws):
    """
    Test for seeing how substantiation speeds are affected
    """
    _d_build = {'network':'network'}    
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_cacheReturn'
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
            self.int_targetCount = int(self.d_kws['targetCount'])
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
	    return r9Meta.MetaClass()          
	
	def test2_func(self,string):
	    return r9Meta.MetaClass(string)
	
        def _buildStuff_(self):
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Creating obj %i"%i), progress = i, maxValue = self.int_targetCount)
                #self.l_objects.append(mc.createNode( self.str_nodeType, n = "obj_{0}".format(i) ))
		self.l_objects.append(mc.joint(n = "obj_{0}".format(i) ))
	    
        def _iterate_(self):	
	    self.call2_func = self.test2_func
		
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Pass 1: Substantiating Call %i"%i), progress = i, maxValue = self.int_targetCount)		
		#string = mc.joint(n = "obj_{0}".format(i))
		string = mc.createNode('network',n = "obj_{0}".format(i))
		#string = mc.createNode('transform',n = "obj_{0}".format(i))
		t1 = time.clock()	
		n1 = self.test1_func(string)              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
		
		r9Meta.registerMClassNodeCache(n1)
		
		t1 = time.clock()	
		#self.l_roots_2.extend( [self.test2_func(self._toCall)] )  
		self.call2_func(n1.mNode)              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)	
			
		
		
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    #cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
		_dif1 = t - self.l_times_2[i]
		
		self.log_info("Step {0} | noncache: {1}| cached: {2}(d{3}) ".format(i,"%0.3f"%t,
		                                                                "%0.3f"%self.l_times_2[i],
		                                                                "%0.3f"%_dif1,
		                                                                ))
	    
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Count: {0} | noncache: {1} | cached: {2}".format(self.int_targetCount,
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
	    self.log_info("Compare 2:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_1[0] - self.l_times_2[0]),
                                                                                                    "%0.3f"%(self.l_times_1[-1] - self.l_times_2[-1]),
                                                                                                    "%0.3f"%(_m1_time - _m2_time)))  
	    
    
    return fncWrap(*args, **kws).go()

def speedTest_objectCount(iterations = 100,):
    """
    Test to see how meta reloading affects file new/open
    """
    l_times = []
    mc.file(new=True,f=True)    
    t_start = time.clock()
    _jnt = mc.joint()
    for i in range(iterations):
	log.info("On...{0}".format(i))	
	_jnt = mc.joint()
	#_jnt = mc.createNode('multiplyDivide')
	#_jnt = mc.createNode('transform')
	
	t1 = time.clock()
	#r9Meta.MetaClass(name = 'test_{0}'.format(i),nodeType='transform')
	#import maya.cmds as mc
	
	r9Meta.MetaClass(_jnt)
	#r9Meta.MetaClass(_jnt,autofill='messageOnly')
	t2 = time.clock()
	l_times.append(t2-t1)
	
    t_end = time.clock()
	
    #for i,t in enumerate(l_times):
	#log.info("Step {0} |  {1}".format(i,"%0.3f"%t))
	
    _str_dif = l_times[-1] - l_times[0] 
    _l_diffs = []
    for i in range(len(l_times)-1):
	_l_diffs.append(l_times[i+1] - l_times[i])
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
			      
			      
			      
			      
def speedTest_attrExists(*args, **kws):
    """
    Test for seeing how substantiation speeds are affected
    """
    _d_build = {'network':'network'}    
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'speedTest_attrExists'
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
            self.int_targetCount = int(self.d_kws['targetCount'])
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
	    
	def test1_func(self,mObj):
	    #return mc.attributeQuery('test_0', exists=True, node=mObj.mNode)        
	    return mc.objExists("{0}.test_0".format(mObj.mNode))
	def test2_func(self,mObj):
	    return mObj._MFnDependencyNode.hasAttribute('test_0')
	
        def _iterate_(self):	
	    self.call2_func = self.test2_func
	    mObj = r9Meta.MetaClass(name = "obj",nodeType = 'transform')	    
            for i in range(self.int_targetCount):
                self.progressBar_set(status = ("Pass 1: Substantiating Call %i"%i), progress = i, maxValue = self.int_targetCount)		
		mObj.addAttr('test_{0}'.format(i),attrType='string')
		
		t1 = time.clock()	
		n1 = self.test1_func(mObj)              
		t2 = time.clock()
		self.l_times_1.append(t2-t1)
				
		t1 = time.clock()	
		#self.l_roots_2.extend( [self.test2_func(self._toCall)] )  
		self.call2_func(mObj)              
		t2 = time.clock()
		self.l_times_2.append(t2-t1)	
			
		
		
	def _reportHowMayaIsStupid_(self):
	    _m1_time = sum(self.l_times_1)
	    _m2_time = sum(self.l_times_2)
	    
	    #cgmGeneral.report_enviornment()	    	    
	    for i,t in enumerate(self.l_times_1):
		_dif1 = t - self.l_times_2[i]
		
		self.log_info("Step {0} | call: {1}| api: {2}(d{3}) ".format(i,"%0.3f"%t,
		                                                                "%0.3f"%self.l_times_2[i],
		                                                                "%0.3f"%_dif1,
		                                                                ))
	    
	    self.log_info(cgmGeneral._str_headerDiv + " Times " + cgmGeneral._str_headerDiv + cgmGeneral._str_subLine)	
	    self.log_info("Count: {0} | call: {1} | api: {2}".format(self.int_targetCount,
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
	    self.log_info("Compare 2:1| Dif: {0} | Dif: {1} |                    Total: {2} ".format("%0.3f"%(self.l_times_1[0] - self.l_times_2[0]),
                                                                                                    "%0.3f"%(self.l_times_1[-1] - self.l_times_2[-1]),
                                                                                                    "%0.3f"%(_m1_time - _m2_time)))  
	    
    
    return fncWrap(*args, **kws).go()