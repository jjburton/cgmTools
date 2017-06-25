"""
------------------------------------------
cgm_Meta: cgm.core.test
Author: Ryan Porter
email: ryan.m.porter@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Unit Tests for the validateArgs module
================================================================
"""
# IMPORTS ====================================================================
import unittest
import logging

import maya.cmds as mc

from cgm.core import cgm_General as cgmGEN
import cgm
from cgm.core.cgmPy import path_Utils as PATH

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

modules = [
    'boolArgs',
    'objString',
    'stringArgs',
    'valueArg'
]

def main(**kwargs):	
	v = kwargs.get('verbosity', 2)
	#cgm.core._reload() 
	sceneSetup()

	suite = unittest.TestSuite()
	loader = unittest.TestLoader()

	tests = loader.discover(PATH.Path(__file__).up())
	
	testRunner = unittest.runner.TextTestRunner(verbosity=v)
	
	for t in tests:
		for t2 in t:
			for t3 in t2:
				print t3
				print t3._testMethodName
				
				for k in t3.__dict__.keys():
					print k
				#exec("reload({0})".format(t3))
	return
	
	#try:
	testRunner.run(tests)
	"""
	except Exception,err:
		for arg in err.args:
			log.error(arg)                
		raise Exception,err	"""


def mainBAK(**kwargs):	
	v = kwargs.get('verbosity', 2)

	suite = unittest.TestSuite()

	for mod in modules:
		logging.info(cgmGEN._str_hardBreak)
		logging.info("Testing module: {0}".format(mod))		
		module = "cgm.core.tests.test_validateArgs.test_validateArgs_{0}".format(mod)

		try:
			exec("import {0}".format(module))
			exec("reload({0})".format(module))
		except ImportError:
			logging.exception("Couldn't import module: {0}".format(module))

		suite.addTest( unittest.defaultTestLoader.loadTestsFromName(module) )

	unittest.TextTestRunner(verbosity=v).run(suite)