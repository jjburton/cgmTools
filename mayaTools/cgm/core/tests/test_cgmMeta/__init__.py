"""
------------------------------------------
cgm_Meta: cgm.core.test
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Unit Tests for the validateArgs module
================================================================
"""
# IMPORTS ====================================================================
import unittest

import unittest.runner
import maya.standalone

import logging
import time

from cgm.core import cgm_General as cgmGEN
import cgm.core
from cgm.core.cgmPy import path_Utils as PATH
import maya.cmds as mc

def sceneSetup():
	try:mc.file(new=True,f=True)
	except Exception,err:
		log.error("New File fail!")
		for arg in err.args:
			log.error(arg)                
		raise Exception,err  

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.WARNING)

modules = ['base',
           'mClasses'
           ]

def main(**kwargs):	
	v = kwargs.get('verbosity', 2)
	cgm.core._reload() 
	sceneSetup()
	
	_t_start = time.clock()
	_len_all = 0
	
	for mod in modules:
		#logging.info("Testing module: {0}".format(mod))
		suite = unittest.TestSuite()
		print(cgmGEN._str_hardBreak)
		print(">>> Testing: {0} ".format(mod) + '-'*100)		
		
		module = "cgm.core.tests.test_cgmMeta.test_{0}".format(mod)
		

		try:
			exec("import {0}".format(module))
			exec("reload({0})".format(module))
		except Exception,err:
			log.error("New File fail!")
			for arg in err.args:
				log.error(arg)                
			raise Exception,err		

		tests = unittest.defaultTestLoader.loadTestsFromName(module)
		suite.addTest( tests)		
		unittest.TextTestRunner(verbosity=v).run(suite)
		
		print("Tests: ")
		if v == 1:
			for t in tests:
				for t2 in t:
					print( "   > " + t2._testMethodName.split('test_')[-1] )
					_len_all += 1
		print(cgmGEN._str_subLine)
		print(">>> Module complete : {0} | {1} ...".format(mod,format(module)))		
		
	print("Completed [{0}] tests in [{1}] modules >> Time >> = {2} seconds".format(_len_all, len(modules), "%0.3f"%(time.clock()-_t_start))) 
	cgmGEN.report_enviornmentSingleLine()
	print(cgmGEN._str_hardBreak)	
	

def mainRunner(**kwargs):	
	v = kwargs.get('verbosity', 2)
	cgm.core._reload() 
	sceneSetup()
	
	suite = unittest.TestSuite()
	#maya.standalone.initialize()
	loader = unittest.TestLoader()
	
	tests = loader.discover(PATH.Path(__file__).up())
	testRunner = unittest.runner.TextTestRunner()
	
	try:
		testRunner.run(tests)
	except Exception,err:
		for arg in err.args:
			log.error(arg)                
		raise Exception,err	
	
	
def mainBAK(**kwargs):	
	v = kwargs.get('verbosity', 2)
	cgm.core._reload() 
	sceneSetup()
	
	suite = unittest.TestSuite()
	logging.info(cgmGEN._str_hardBreak)
	logging.info("Testing: {0}...".format(__name__.split('.')[-1]))
	
	for mod in modules:
		#logging.info("Testing module: {0}".format(mod))
		module = "cgm.core.tests.test_cgmMeta.test_{0}".format(mod)

		try:
			exec("import {0}".format(module))
			exec("reload({0})".format(module))
		except Exception,err:
			log.error("New File fail!")
			for arg in err.args:
				log.error(arg)                
			raise Exception,err		
		#except ImportError:
			#logging.exception("Couldn't import module: {0}".format(module))

		suite.addTest( unittest.defaultTestLoader.loadTestsFromName(module) )

	unittest.TextTestRunner(verbosity=v).run(suite)	
"""
import unittest
import unittest.runner
import maya.standalone

maya.standalone.initialize()

loader = unittest.TestLoader()                                          
tests = loader.discover(tests_directory)                                        
testRunner = unittest.runner.TextTestRunner()                           

try:
    testRunner.run(tests)
except:
    raise
finally:
    maya.standalone.uninitialize()

"""