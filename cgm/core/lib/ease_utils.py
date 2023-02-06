"""
------------------------------------------
ease_utils: cgm.core.lib
Author: David Bokser
email: dbokser@cgmonks.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

algorithms from https://easings.net/

================================================================
"""

def easeInOutQuad(x):
	return 2.0 * x * x if x < 0.5 else 1.0 - pow(-2.0 * x + 2.0, 2.0) / 2.0

def easeInOutCubic(x):
	return 4.0 * x * x * x if x < 0.5 else 1.0 - pow(-2.0 * x + 2.0, 3.0) / 2.0