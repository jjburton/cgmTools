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
reload(search)
class build_mdNetwork(object):
    """
    Build a md network. Most useful for for vis networks.
    
    @kws
    results(list) -- [{resultlist:,drivers:list,driven:list},...]
    >>result(list) -- obj,attr
    >>drivers(nested list) -- [[obj,attr]...]#len must be 2
    >>driven(nested list) -- [[obj,attr]...]#can be None
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
    def __init__(self, arg, defaultAttrType = 'bool', operation = 1,*args,**kws):
	
        """Constructor"""
	self.d_iAttrs = {}#attr instances stores as {index:instance}
	self.l_iAttrs = []#Indices for iAttrs
	self.d_resultNetworksToBuild = {}#Index desctiptions of networks to build {target:[[1,2],3]}
	self.d_connectionsToMake = {}#Connections to make
	self.d_mdNetworksToBuild = {}#indexed to l_mdNetworkIndices
	self.l_mdNetworkIndices = []#Indices of md networks
	self.l_good_mdNetworks = []#good md networks by arg [1,2]
	self.d_good_mdNetworks = {}#md instances indexed to l_good_mdNetworks
	
	self.kw_operation = operation
	
        #>>>Keyword args	
        log.info(">>> visNetwork.__init__")
	if kws:log.info("kws: %s"%str(kws))
	if args:log.info("args: %s"%str(args))
	
	#>>>Check arg
	self.validateArg(arg,defaultAttrType = defaultAttrType,*args,**kws)
	log.info("resultNetworks: %s"%self.d_resultNetworksToBuild)
	
	#>>>Build network
	log.info("Building mdNetworks: %s"%self.d_mdNetworksToBuild)
	log.info("Building mdNetworks indices: %s"%self.l_mdNetworkIndices)
	for i,k in enumerate(self.l_iAttrs):
	    log.info("%s >> %s"%(i,self.d_iAttrs[i].p_combinedName))
	
	for resultIndex in self.d_mdNetworksToBuild.keys():#For each stored index dict key
	    #To do, add a check to see if a good network exists before making another
	    iNetwork = self.validateMDNetwork(resultIndex)
	    
	    #if iNetwork:
		#self.d_iAttrs[resultIndex].doConnectIn(iNetwork.)
     
	#a = cgmMeta.cgmAttr()
	#a.p_combinedName
	#>>>Connect stuff
	log.info("Making connections: %s"%self.d_connectionsToMake)	
	for sourceIndex in self.d_connectionsToMake.keys():#For each stored index dict key
	    source = self.d_iAttrs.get(sourceIndex)#Get the source attr's instance
	    log.info("source: '%s'"%source.p_combinedName)	    
	    for targetIndex in self.d_connectionsToMake.get(sourceIndex):#for each target of that source
		target = self.d_iAttrs.get(targetIndex)#Get the instance
		log.info("target: '%s'"%target.p_combinedName)	    		
		#source.doConnectOut(target.p_combinedName)#Connect
		attributes.doConnectAttr(source.p_combinedName,target.p_combinedName)
	    
    def validateArg(self,arg,defaultAttrType,*args,**kws):
	assert type(arg) is list,"Argument must be list"
	#>>> 
	def validateObjAttr(obj,attr,defaultAttrType):
	    """
	    Return a cgmAttr if everything checks out
	    """
	    log.info("verifyObjAttr: '%s',%s'"%(obj,attr))
	    if type(attr) not in [str,unicode]:
		log.warning("attr arg must be string: '%s'"%attr)
		return False
	    try:#Try to link an instance
		obj.mNode
		i_obj = obj
	    except:#Else try to initialize
		if mc.objExists(obj):
		    log.info("initializing '%s'"%obj)
		    i_obj = cgmMeta.cgmNode(obj)	    				
		else:
		    log.info("'%s' doesn't exist" %obj)
		    return False
	    #Check attr
	    if not i_obj.hasAttr(attr):
		log.info("...making attr: '%s'"%attr)
		i_obj.addAttr(attr,attrType = defaultAttrType,initialValue=1)
	    
	    return self.register_iAttr(i_obj,attr)
	#========================================================
	for i,a in enumerate(arg):
	    iDrivers = []
	    iDriven = []
	    iResult = False
	    bufferArg = {}
	    log.info("Checking: %s"%a)
	    if type(a) is dict:
		log.info("...is dict")
		if 'result' and 'drivers' in a.keys():
		    log.info("...found necessary keys")
		    if type(a.get('result')) is list and len(a.get('result'))==2:
		        log.info("...Checking 'result'")			
			obj = a.get('result')[0]
			attr = a.get('result')[1]
			index = validateObjAttr(obj,attr,defaultAttrType)
			self.d_iAttrs[index].p_locked = True
			self.d_iAttrs[index].p_hidden = True			
			iResult = index
			log.info("iResult: %s"%iResult)
		    if type(a.get('drivers')) is list:
			for pair in a.get('drivers'):
			    if len(pair) == 2:
				log.info("driver: %s"%pair)				
				obj = pair[0]
				attr = pair[1]		
				iDrivers.append(validateObjAttr(obj,attr,defaultAttrType))
			log.info("iDrivers: %s"%iDrivers)
		    if type(a.get('driven')) is list:
			for pair in a.get('driven'):
			    if len(pair) == 2:
				log.info("driven: %s"%pair)				
				obj = pair[0]
				attr = pair[1]	
				index = validateObjAttr(obj,attr,defaultAttrType)
				self.d_iAttrs[index].p_locked = True
				self.d_iAttrs[index].p_hidden = True
				iDriven.append(index)
			log.info("iDriven %s"%iDriven)
		
		if type(iResult) is int and iDrivers:
		    log.info('Storing arg data')
		    
		    if len(iDrivers) == 1:
			self.d_connectionsToMake[iDrivers[0]]=[iResult]		
		    elif len(iDrivers) == 2:
			if iDrivers in self.l_mdNetworkIndices:
			    log.info("Go ahead and connect it")
			else:
			    self.l_mdNetworkIndices.append(iDrivers)#append the drivers
			    index = self.l_mdNetworkIndices.index(iDrivers)
			    self.d_mdNetworksToBuild[iResult] = [iDrivers]
		    else:
			log.info('asdf')
			
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
	    log.info("Creating mdNetwork: %s"%arg[0])
	    source1 = self.d_iAttrs[source1Index]#get the sources
	    source2 = self.d_iAttrs[source2Index]
	    log.info("source1: %s"%source1.p_combinedName)
	    log.info("source2: %s"%source2.p_combinedName)
	    
	    #se if this connection exists now that we know the connectors
	    i_md = None	    
	    matchCandidates = []
	    source1Driven = source1.getDriven(obj=True)	    
	    if source1.getDriven():
		log.info("1Driven: %s"%source1Driven)
		for c in source1Driven:
		    if search.returnObjectType(c) == 'multiplyDivide':
			matchCandidates.append(c)
	    source2Driven = source2.getDriven(obj=True)
	    if matchCandidates and source2Driven:
		log.info("matchCandidates: %s"%matchCandidates)		
		log.info("2Driven: %s"%source2Driven)		
		for c in source2Driven:
		    if c in matchCandidates:
			log.info("Found existing md node: %s"%c)
			i_md = cgmMeta.cgmNode(c)#Iniitalize the match
			if i_md.operation != self.kw_operation:
			    i_md.operation = self.kw_operation
			    log.warning("Operation of existing node '%s' has been changed: %s"%(i_md.getShortName(),self.kw_operation))
			break

	    if i_md is None:
		i_md = cgmMeta.cgmNode(name = 'test',nodeType = 'multiplyDivide')#make the node	
		i_md.operation = self.kw_operation
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
	    log.info("self.i_mdOutAttrIndex: %s"%self.i_mdOutAttrIndex)
	    
	log.info(">>> in build_mdNetwork.validateMDNetwork")
	arg = self.d_mdNetworksToBuild.get(buildNetworkIndex)
	log.info("arg: %s"%arg)
	
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
	    log.info("creating first md node")
	    verifyMDNetwork(arg[0][0],arg[0][1])
	else:
	    log.info("Finding exsiting network")
	    nodeIndex = self.l_good_mdNetworks.index(arg[0])
	    log.info("nodeIndex: %s"%nodeIndex)
	    i_md = self.d_good_mdNetworks[nodeIndex]#get the md instance
	    log.info("i_md: '%s'"%i_md.getShortName())	    
	    self.i_mdOutAttrIndex = self.register_iAttr(i_md,'outputX')
  
	for connection in arg[1:]:
	    log.info("self.i_mdOutAttrIndex: %s"%self.i_mdOutAttrIndex)	    
	    log.info("...Adding connection: %s"%connection)
	    if self.i_mdOutAttrIndex is None:
		raise ValueError,"self.i_mdOutAttrIndex is :%s"%self.i_mdOutAttrIndex
	    if connection not in self.d_iAttrs.keys():
		raise ValueError,"connection index not in self.l_iAttrs: %s"%connection		
	    verifyMDNetwork(self.i_mdOutAttrIndex ,connection)
	
	if self.i_mdOutAttrIndex is not None:#Register our connection to make
	    log.info("adding connection: %s = [%s]"%(self.i_mdOutAttrIndex,buildNetworkIndex))
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
	    log.info("iAttr: %s"%i_attr)
	    self.l_iAttrs.append(combinedName)
	    self.d_iAttrs[self.l_iAttrs.index(combinedName)] = i_attr
	    
	return self.l_iAttrs.index(combinedName)


class build_conditionNetworkFromGroup(object):
    def __init__(self, group, chooseAttr = 'switcher', controlObject = None, connectTo = 'visibility',*args,**kws):
	"""Constructor"""
	self.d_iAttrs = {}#attr instances stores as {index:instance}
	self.l_iAttrs = []#Indices for iAttrs
	self.d_resultNetworksToBuild = {}#Index desctiptions of networks to build {target:[[1,2],3]}
	self.i_group = False
	self.i_control = False
	self.connectToAttr = connectTo
	self.i_attr = False
	
        #>>>Keyword args	
        log.debug(">>> build_conditionNetworkFromGroup.__init__")
	if kws:log.debug("kws: %s"%str(kws))
	if args:log.debug("args: %s"%str(args))
	
	#Check our group
	if not mc.objExists(group):
	    log.error("Group doesn't exist: '%s'"%group)
	    return
	elif not search.returnObjectType(group) == 'group':
	    log.error("Object is not a group: '%s'"%search.returnObjectType(group))
	    return
	self.i_group = cgmMeta.cgmObject(group)
	if not self.i_group.getChildren():
	    log.error("No children detected: '%s'"%group)
	    return	
	
	#Check our control
	if controlObject is None or not mc.objExists(controlObject):
	    log.error("No suitable control object found: '%s'"%controlObject)
	    return
	else:
	    i_controlObject = cgmMeta.cgmNode(controlObject)
	    self.i_attr = cgmMeta.cgmAttr(i_controlObject,chooseAttr,attrType = 'enum',initialValue = 1)
	if self.buildNetwork(*args,**kws):
	    log.info("Chooser Network good to go")
	
    def buildNetwork(self,*args,**kws):
	if kws:log.info("kws: %s"%str(kws))
	if args:log.info("args: %s"%str(args))
	
	children = self.i_group.getChildren()
	children.insert(0,'none')
	
	#Make our attr
	if len(children) == 2:
	    self.i_attr.doConvert('bool')#Like bool better
	    #self.i_attr.setEnum('off:on')
	else:
	    self.i_attr.setEnum(':'.join(children))
	
	for i,c in enumerate(children[1:]):
	    i_c = cgmMeta.cgmNode(c)
	    #see if the node exists
	    condNodeTest = attributes.returnDriverObject('%s.%s'%(c,self.connectToAttr))
	    if condNodeTest:
		i_node = cgmMeta.cgmNode(condNodeTest)
	    else:
		if mc.objExists('%s_condNode'%c):
		    mc.delete('%s_condNode'%c)
		i_node = cgmMeta.cgmNode(name = 'tmp', nodeType = 'condition') #Make our node
	    
	    i_node.addAttr('cgmName', i_c.getShortName(), attrType = 'string')
	    i_node.addAttr('cgmType','condNode')
	    i_node.doName()
	    i_node.secondTerm = i+1
	    attributes.doSetAttr(i_node.mNode,'colorIfTrueR',1)
	    attributes.doSetAttr(i_node.mNode,'colorIfFalseR',0)
	    #i_node.colorIfTrueR = 1
	    #i_node.colorIfTrueR = 0
	    
	    self.i_attr.doConnectOut('%s.firstTerm'%i_node.mNode)
	    attributes.doConnectAttr('%s.outColorR'%i_node.mNode,'%s.%s'%(c,self.connectToAttr))
	
	return True
		
def createAverageNode(drivers,driven = None,operation = 3):
    #Create the mdNode
    log.info(1)    
    if type(drivers) not in [list,tuple]:raise StandardError,"createAverageNode>>> drivers arg must be list"
    l_driverReturns = []
    for d in drivers:
	l_driverReturns.append(attributes.validateAttrArg(d))
    d_driven = False
    if driven is not None:
	d_driven = attributes.validateAttrArg(driven)
    
    if d_driven:
	drivenCombined =  d_driven['combined']
	log.info("drivenCombined: %s"%drivenCombined)
    log.info(2)
    #Create the node
    i_pma = cgmMeta.cgmNode(mc.createNode('plusMinusAverage'))
    i_pma.operation = operation
    l_objs = []
    #Make our connections
    for i,d in enumerate(l_driverReturns):
	log.info("Driver %s: %s"%(i,d['combined']))
	attributes.doConnectAttr(d['combined'],'%s.input1D[%s]'%(i_pma.mNode,i),True)
	l_objs.append(mc.ls(d['obj'],sn = True)[0])#Get the name
    log.info(3)
    
    i_pma.addAttr('cgmName',"_".join(l_objs),lock=True)	
    i_pma.addAttr('cgmTypeModifier','twist',lock=True)
    i_pma.doName()

    if driven is not None:
	attributes.doConnectAttr('%s.output1D'%i_pma.mNode,drivenCombined,True)
	
    return i_pma

def groupToConditionNodeSet(group,chooseAttr = 'switcher', controlObject = None, connectTo = 'visibility'):
    """
    Hack job for the gig to make a visibility switcher for all the first level of children of a group
    """
    children = search.returnChildrenObjects(group) #Check for children

    if not children: #If none, break out
	guiFactory("'%s' has no children! Aborted."%group)
	return False
    if controlObject is None:
	controlObject = group
    
    #Make our attr
    a = AttrFactory.AttrFactory(controlObject,chooseAttr,'enum')
    children.insert(0,'none')
    print children
    if len(children) == 2:
	a.setEnum('off:on')
    else:
	a.setEnum(':'.join(children))
    
    for i,c in enumerate(children[1:]):
	print i
	print c
	#see if the node exists
	condNodeTest = attributes.returnDriverObject('%s.%s'%(c,connectTo))
	if condNodeTest:
	    buffer = condNodeTest
	else:
	    if mc.objExists('%s_condNode'%c):
		mc.delete('%s_condNode'%c)
	    buffer = nodes.createNamedNode('%s_picker'%c,'condition') #Make our node
	print buffer
	attributes.doSetAttr(buffer,'secondTerm',i+1)
	attributes.doSetAttr(buffer,'colorIfTrueR',1)
	attributes.doSetAttr(buffer,'colorIfFalseR',0)
	
	a.doConnectOut('%s.firstTerm'%buffer)
	attributes.doConnectAttr('%s.outColorR'%buffer,'%s.%s'%(c,connectTo))