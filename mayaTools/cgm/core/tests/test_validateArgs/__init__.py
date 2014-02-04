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

	suite = unittest.TestSuite()

	for mod in modules:
		module = "cgm.core.tests.test_validateArgs.test_validateArgs_{0}".format(mod)

		try:
			exec("import {0}".format(module))
			exec("reload({0})".format(module))
		except ImportError:
			logging.exception("Couldn't import module: {0}".format(module))

		suite.addTest( unittest.defaultTestLoader.loadTestsFromName(module) )

	unittest.TextTestRunner(verbosity=v).run(suite)