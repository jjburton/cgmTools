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
    arg = [{'result':[i_o,'leftSubControls'],'drivers':[[i_o,'left'],[i_o,'sub'],[i_o,'controls']]},
           {'result':[i_o,'rightSubControls'],'drivers':[[i_o,'right'],[i_o,'sub'],[i_o,'controls']]},
           {'result':[i_o,'leftControls'],'drivers':[[i_o,'left'],[i_o,'controls']]},
           {'result':[i_o,'rightControls'],'drivers':[[i_o,'right'],[i_o,'controls']]}
            ]
    
    i_o = cgmMeta.cgmNode('null1')
    nf.build_mdNetwork(arg)
    """
    compatibleAttrs = ['bool','int','enum']
    def __init__(self, arg, defaultAttrType = 'bool',*args,**kws):
	
        """Constructor"""
	self.d_iAttrs = {}#attr instances stores as {index:instance}
	self.l_iAttrs = []#Indices for iAttrs
	self.d_resultNetworksToBuild = {}#Index desctiptions of networks to build {target:[[1,2],3]}
	self.d_connectionsToMake = {}#Connections to make
	self.d_mdNetworksToBuild = {}#indexed to l_mdNetworkIndices
	self.l_mdNetworkIndices = []#Indices of md networks
	self.l_good_mdNetworks = []#good md networks by arg [1,2]
	self.d_good_mdNetworks = {}#md instances indexed to l_good_mdNetworks
		
        #>>>Keyword args	
        log.debug(">>> visNetwork.__init__")
	if kws:log.debug("kws: %s"%str(kws))
	if args:log.debug("args: %s"%str(args))
	
	#>>>Check arg
	self.validateArg(arg,defaultAttrType = defaultAttrType,*args,**kws)
	log.debug("resultNetworks: %s"%self.d_resultNetworksToBuild)
	
	#>>>Build network
	log.debug("Building mdNetworks: %s"%self.d_mdNetworksToBuild)
	log.debug("Building mdNetworks indices: %s"%self.l_mdNetworkIndices)
	for i,k in enumerate(self.l_iAttrs):
	    log.debug("%s >> %s"%(i,self.d_iAttrs[i].p_combinedName))
	
	for resultIndex in self.d_mdNetworksToBuild.keys():#For each stored index dict key
	    #To do, add a check to see if a good network exists before making another
	    iNetwork = self.validateMDNetwork(resultIndex)
	    
	    #if iNetwork:
		#self.d_iAttrs[resultIndex].doConnectIn(iNetwork.)
     
	#a = cgmMeta.cgmAttr()
	#a.p_combinedName
	#>>>Connect stuff
	log.debug("Making connections: %s"%self.d_connectionsToMake)	
	for sourceIndex in self.d_connectionsToMake.keys():#For each stored index dict key
	    source = self.d_iAttrs.get(sourceIndex)#Get the source attr's instance
	    for targetIndex in self.d_connectionsToMake.get(sourceIndex):#for each target of that source
		target = self.d_iAttrs.get(targetIndex)#Get the instance
		source.doConnectOut(target.p_combinedName)#Connect
	    
    def validateArg(self,arg,defaultAttrType,*args,**kws):
	assert type(arg) is list,"Argument must be list"
	#>>> 
	def validateObjAttr(obj,attr,defaultAttrType):
	    """
	    Return a cgmAttr if everything checks out
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
		i_obj.addAttr(attr,attrType = defaultAttrType,initialValue=1)
	    
	    return self.register_iAttr(i_obj,attr)
	#========================================================
	for i,a in enumerate(arg):
	    iDrivers = []
	    iDriven = []
	    iResult = False
	    bufferArg = {}
	    log.debug("Checking: %s"%a)
	    if type(a) is dict:
		log.debug("...is dict")
		if 'result' and 'drivers' in a.keys():
		    log.debug("...found necessary keys")
		    if type(a.get('result')) is list and len(a.get('result'))==2:
		        log.debug("...Checking 'result'")			
			obj = a.get('result')[0]
			attr = a.get('result')[1]
			index = validateObjAttr(obj,attr,defaultAttrType)
			self.d_iAttrs[index].p_locked = True
			self.d_iAttrs[index].p_hidden = True			
			iResult = index
			log.debug("iResult: %s"%iResult)
		    if type(a.get('drivers')) is list:
			for pair in a.get('drivers'):
			    if len(pair) == 2:
				log.debug("driver: %s"%pair)				
				obj = pair[0]
				attr = pair[1]		
				iDrivers.append(validateObjAttr(obj,attr,defaultAttrType))
			log.debug("iDrivers: %s"%iDrivers)
		    if type(a.get('driven')) is list:
			for pair in a.get('driven'):
			    if len(pair) == 2:
				log.debug("driven: %s"%pair)				
				obj = pair[0]
				attr = pair[1]	
				index = validateObjAttr(obj,attr,defaultAttrType)
				self.d_iAttrs[index].p_locked = True
				self.d_iAttrs[index].p_hidden = True
				iDriven.append(index)
			log.debug("iDriven %s"%iDriven)
		
		if type(iResult) is int and iDrivers:
		    log.debug('Storing arg data')
		    
		    if len(iDrivers) == 1:
			self.d_connectionsToMake[iDrivers[0]]=[iResult]		
		    elif len(iDrivers) == 2:
			if iDrivers in self.l_mdNetworkIndices:
			    log.debug("Go ahead and connect it")
			else:
			    self.l_mdNetworkIndices.append(iDrivers)#append the drivers
			    index = self.l_mdNetworkIndices.index(iDrivers)
			    self.d_mdNetworksToBuild[iResult] = [iDrivers]
		    else:
			log.debug('asdf')
			
			buffer = iDrivers[:2]
			if buffer not in self.l_mdNetworkIndices:
			    self.l_mdNetworkIndices.append(buffer)#append the drivers
			    index = self.l_mdNetworkIndices.index(buffer)
			    self.d_mdNetworksToBuild[iResult] = [buffer]
			for n in iDrivers[2:]:#Figure out the md's to build
			    buffer = [buffer]
			    buffer.append(n)
			    if buffer not in self.l_mdNetworkIndices:
				self.l_mdNetworkIndices.append(buffer)#append the drivers
				index = self.l_mdNetworkIndices.index(buffer)
				self.d_mdNetworksToBuild[iResult] = buffer
 
		    #>>> network
		    self.d_resultNetworksToBuild[iResult]=iDrivers
		    if iDriven:
			self.d_connectionsToMake[iResult]=iDriven
			
    def validateMDNetwork(self,buildNetworkIndex):
	"""
	arg should be in the form of [[int,int],int...int]
	the first arg should always be a pair as the base md node paring, the remainging ones are daiy chained form that
	"""
	def verifyMDNetwork(source1Index, source2Index):
	    """
	    If it doesn't exist, make it, otherwise, register the connection
	    """
	    log.debug("Creating mdNetwork: %s"%arg[0])
	    source1 = self.d_iAttrs[source1Index]#get the sources
	    source2 = self.d_iAttrs[source2Index]
	    log.debug("source1: %s"%source1.p_combinedName)
	    log.debug("source2: %s"%source2.p_combinedName)
	    
	    #se if this connection exists now that we know the connectors
	    i_md = None	    
	    matchCandidates = []
	    source1Driven = source1.getDriven(obj=True)	    
	    if source1.getDriven():
		log.debug("1Driven: %s"%source1Driven)
		for c in source1Driven:
		    if search.returnObjectType(c) == 'multiplyDivide':
			matchCandidates.append(c)
	    source2Driven = source2.getDriven(obj=True)
	    if matchCandidates and source2Driven:
		log.debug("matchCandidates: %s"%matchCandidates)		
		log.debug("2Driven: %s"%source2Driven)		
		for c in source2Driven:
		    if c in matchCandidates:
			log.debug("Found existing md node: %s"%c)
			i_md = cgmMeta.cgmNode(c)#Iniitalize the match
			break

	    if i_md is None:
		i_md = cgmMeta.cgmNode(name = 'test',nodeType = 'multiplyDivide')#make the node	
		
		source1.doConnectOut("%s.input1X"%i_md.mNode)
		source2.doConnectOut("%s.input2X"%i_md.mNode)
		#Name it
		source1Name = source1.p_combinedName
		source1Name = ''.join(source1Name.split('|')[-1].split(':')[-1].split('_'))
		source2Name = source2.p_combinedName
		source2Name = ''.join(source2Name.split('|')[-1].split(':')[-1].split('_'))    
		i_md.doStore('cgmName',"%s_to_%s"%(source1Name,source2Name))
		i_md.doName()
	    
	    #Store to our good network and the output attr
	    self.l_good_mdNetworks.append(arg[0])#append it to get our index lib
	    index = self.l_good_mdNetworks.index(arg[0])#get index
	    self.d_good_mdNetworks[index]=i_md#store the instance
	    i_mdBuffer = i_md
	    self.i_mdOutAttrIndex = self.register_iAttr(i_md,'outputX')
	    log.debug("self.i_mdOutAttrIndex: %s"%self.i_mdOutAttrIndex)
	    
	log.debug(">>> in build_mdNetwork.validateMDNetwork")
	arg = self.d_mdNetworksToBuild.get(buildNetworkIndex)
	log.debug("arg: %s"%arg)
	
	if type(arg) is not list:
	    log.error("validateMDNetwork args must be a list")
	    return False
	if len(arg)>2 and type(arg[0]) is not list and len(arg[0]) == 2:
	    log.error("validateMDNetwork arg[0] must be a list with 2 keys")
	    return False    
	#Let's get the first mdNode checked
	i_mdBuffer = False
	self.i_mdOutAttrIndex = None
	
	#Need to add check to see if the network exists from sourc
	if arg[0] not in self.l_good_mdNetworks:
	    log.debug("creating first md node")
	    verifyMDNetwork(arg[0][0],arg[0][1])
	else:
	    log.debug("Finding exsiting network")
	    nodeIndex = self.l_good_mdNetworks.index(arg[0])
	    log.debug("nodeIndex: %s"%nodeIndex)
	    i_md = self.d_good_mdNetworks[nodeIndex]#get the md instance
	    log.debug("i_md: '%s'"%i_md.getShortName())	    
	    self.i_mdOutAttrIndex = self.register_iAttr(i_md,'outputX')
  
	for connection in arg[1:]:
	    log.debug("self.i_mdOutAttrIndex: %s"%self.i_mdOutAttrIndex)	    
	    log.debug("...Adding connection: %s"%connection)
	    if self.i_mdOutAttrIndex is None:
		raise ValueError,"self.i_mdOutAttrIndex is :%s"%self.i_mdOutAttrIndex
	    if connection not in self.d_iAttrs.keys():
		raise ValueError,"connection index not in self.l_iAttrs: %s"%connection		
	    verifyMDNetwork(self.i_mdOutAttrIndex ,connection)
	
	if self.i_mdOutAttrIndex is not None:#Register our connection to make
	    log.debug("adding connection: %s = [%s]"%(self.i_mdOutAttrIndex,buildNetworkIndex))
	    self.d_connectionsToMake[self.i_mdOutAttrIndex]=[buildNetworkIndex]
    
    def register_iAttr(self, i_obj,attr):
	"""
	i_obj - cgmNode,cgmObject
	attr(string) - attr name to register
	"""
	combinedName = "%s.%s"%(i_obj.mNode,attr)
	if not mc.objExists(combinedName):
	    log.error("Cannot register nonexistant attr: %s"%combinedName)
	    return False	
	if not combinedName in self.l_iAttrs:
	    i_attr = cgmMeta.cgmAttr(i_obj,attr,keyable = False)
	    log.debug("iAttr: %s"%i_attr)
	    self.l_iAttrs.append(combinedName)
	    self.d_iAttrs[self.l_iAttrs.index(combinedName)] = i_attr
	    
	return self.l_iAttrs.index(combinedName)


