"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basis of logger
================================================================
"""
#>> Logging start block =============================================================
import logging#Standard to python for a while now...
logging.basicConfig()#Basic configuration setup
log = logging.getLogger(__name__)#This initialized a log for this module
log.setLevel(logging.INFO)#Generally we default a module to info
#>> Logging end block =============================================================

#>>Info
log.info("yay!")
#When we do this in the script editor, it will be formatted like '# __main__ : yay! # '
#When we have this setup in a module it will list the module name in place of __main__

log.debug("what was that now?")#Nothing is going to happen...that's because our log level is set to info

#>>Debug 
log.setLevel(logging.DEBUG)#We're gonna change the log level to debug
log.debug("what was that now?")#try it again...and we see something

#>> Other calls
#There are several other calls we can do as well, give them a try
log.debug("what was that now?")
log.error("Something be amiss!")
log.warning("Something doesn't seem right..")
log.critical("Very, very bad!")

#What if we wanted to change the log level of a module we've imported
from cgm.core import cgm_Meta as cgmMeta
cgmMeta.log.setLevel(cgmMeta.logging.DEBUG)#Would set cgmMeta to debug
cgmMeta.log.setLevel(cgmMeta.logging.INFO)#Would set cgmMeta back to info

