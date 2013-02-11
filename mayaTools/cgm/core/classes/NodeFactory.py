"""
------------------------------------------
NodeFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class Factory for building node networks
================================================================
"""
# From Python =============================================================
import copy
import re

#TEMP
import cgm.core
cgm.core._reload()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (lists,
                     search,
                     attributes)

class build_mdNetwork(object):
    """
    Build a md network. Most useful for for vis networks.
    
    @kws
    results(list) -- [{resultlist:,drivers:list,driven:list},...]
    >>result(list) -- obj,attr
    >>drivers(nested list) -- [[obj,attr]...]#len must be 2
    >>drivern(nested list) -- [[obj,attr]...]#can be None
    [ {'result':obj1,resultAttr,'drivers':[[dObj,dAttr2],[dObj,dAttr2]],'driven' = None} ]
    
    results must have at least one driver
    1 drive r-- direct connect
    
    Example:
    from cgm.core.classes import NodeFactory as nf
    reload(nf)
    from cgm.core import cgm_Meta as cgmMeta
    arg = [{'result':[i_o,'result'],'drivers':[[i_o,'driver1'],[i_o,'driver2']],'driven':[[i_o,'driven1']]}]
    arg = [{'result':['null1','result'],'drivers':[['null1','driver1'],['null1','driver2']],'driven':[['null1','driven1']]}]
    arg = {}
    i_o = cgmMeta.cgmNode('null1')
    nf.build_mdNetwork(arg)
    
    Working info:
    self.d_iAttrs = dict of iAttrs indexed l_iAttrs indices
    self.l_iAttrs = index compare list of shortName.attr
    {results index:drivers indexes]
    self.l_iDrivens = 
    """
    compatibleAttrs = ['bool','int','enum']
    def __init__(self, arg, defaultAttrType = 'bool',*args,**kws):
	
        """Constructor"""
	self.d_iAttrs = {}
	self.l_iAttrs = []
	self.d_resultNetworksToBuild = {}
	self.d_connectionsToMake = {}
	self.d_mdNetworksToBuild = {}#indexed to l_mdNetworkIndices
	self.l_mdNetworkIndices = []#Indices of md networks
	
        #>>>Keyword args	
        log.debug(">>> visNetwork.__init__")
	if kws:log.info("kws: %s"%str(kws))
	if args:log.debug("args: %s"%str(args))
	
	#>>>Check arg
	self.validateArg(arg,defaultAttrType = defaultAttrType,*args,**kws)
	log.info("resultNetworks: %s"%self.d_resultNetworksToBuild)
	log.info("connectionsToMake: %s"%self.d_connectionsToMake)
	log.info("mdNetworksToBuild: %s"%self.d_mdNetworksToBuild)
	
	    
    def validateArg(self,arg,defaultAttrType,*args,**kws):
	assert type(arg) is list,"Argument must be list"
	#>>> 
	def validateObjAttr(obj,attr,defaultAttrType):
	    """
	    Return a cgm attr if everything checks out
	    """
	    log.debug("verifyObjAttr: '%s',%s'"%(obj,attr))
	    if type(attr) is not str:
		log.warning("attr arg must be string: '%s'"%attr)
		return False
	    try:#Try to link an instance
		obj.mNode
		i_obj = obj
	    except:#Else try to initialize
		if mc.objExists(obj):
		    log.debug("initializing '%s'"%obj)
		    i_obj = cgmMeta.cgmNode(obj)	    				
		else:
		    log.debug("'%s' doesn't exist" %obj)
		    return False
	    #Check attr
	    if not i_obj.hasAttr(attr):
		log.debug("...making attr: '%s'"%attr)
		i_obj.addAttr(attr,attrType = defaultAttrType)
	    
	    combinedNameCheck = "%s.%s"%(i_obj.mNode,attr)
	    if not combinedNameCheck in self.l_iAttrs:
		i_attr = cgmMeta.cgmAttr(i_obj,attr,keyable = False)
		log.debug("iAttr: %s"%i_attr)
		self.l_iAttrs.append(combinedNameCheck)
		self.d_iAttrs[self.l_iAttrs.index(combinedNameCheck)] = i_attr
		
	    return self.l_iAttrs.index(combinedNameCheck)
	#========================================================
	for i,a in enumerate(arg):
	    iDrivers = []
	    iDriven = []
	    iResult = False
	    bufferArg = {}
	    log.info("Checking: %s"%a)
	    if type(a) is dict:
		log.debug("...is dict")
		if 'result' and 'drivers' in a.keys():
		    log.debug("...found necessary keys")
		    if type(a.get('result')) is list and len(a.get('result'))==2:
		        log.debug("...Checking 'result'")			
			obj = a.get('result')[0]
			attr = a.get('result')[1]
			iResult = validateObjAttr(obj,attr,defaultAttrType)
			log.info("iResult: %s"%iResult)
		    if type(a.get('drivers')) is list:
			for pair in a.get('drivers'):
			    if len(pair) == 2:
				log.debug("driver: %s"%pair)				
				obj = pair[0]
				attr = pair[1]		
				iDrivers.append(validateObjAttr(obj,attr,defaultAttrType))
			log.info("iDrivers: %s"%iDrivers)
		    if type(a.get('driven')) is list:
			for pair in a.get('driven'):
			    if len(pair) == 2:
				log.debug("driven: %s"%pair)				
				obj = pair[0]
				attr = pair[1]		
				iDriven.append(validateObjAttr(obj,attr,defaultAttrType))
			log.info("iDriven %s"%iDriven)
		
		if type(iResult) is int and iDrivers:
		    log.info('Storing arg data')
		    """
		    if len(iDrivers) == 1:
			self.d_connectionsToMake[iDrivers[0]]=[iResult]		
		    elif len(iDrivers) == 2:
			if iDrivers.sort() in self.l_mdNetworkIndices:
			    l_mdNetworkIndices
			else:
			    index = len(self.l_mdNetworkIndices)			
			    self.d_mdNetworksToBuild[index] = iDrivers.sort()
		    else:
			log.info('asdf')
			buffer = iDrivers[:1]
			if buffer.sort() not in self.d_mdNetworksToBuild:
			    index = len(self.d_mdNetworksToBuild.keys())
			    self.d_mdNetworksToBuild[index] = buffer
			    self.l_mdNetworkIndices.append(index)
			
			   
			cullList = copy.copy(iDrivers)
			while cullList:
			    log.info("cull: %s"%cullList[:1])
			    """    
		    #>>> network
		    self.d_resultNetworksToBuild[iResult]=iDrivers
		    if iDriven:
			self.d_connectionsToMake[iResult]=iDriven
			


