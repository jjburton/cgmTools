#=========================================================================      
#=========================================================================
import cgm.core
cgm.core._reload()

from Red9.core import Red9_Meta as r9Meta
#from Red9.core.Red9_Meta import *
#r9Meta.registerMClassInheritanceMapping()    
#========================================================================
import random
import re
import copy
import time
import logging

from cgm.lib import (distance,attributes)
reload(attributes)
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)

import maya.cmds as mc

def TestAllTheThings():
    """"
    Catch all test for meta stuff
    """
    cgmMeta_Test()

class MorpheusBase_Test():
    def __init__(self):
        function = 'Morpheus_Test'    
        log.info(">"*20  + "  Testing '%s' "%function + "<"*20 )         
        start = time.clock()
        self.setup()
        self.getMesh()
        self.sizeTest()        

    def setup(self):
        '''
        Tests proper creation of objects from flag calls
        '''        
        mc.file(new=True,f=True)
        function = 'setup'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()       

        #Test name and node argument passing
        #==============      
        log.info("Testing no arguments passed")
        self.Morpheus = cgmPM.cgmPuppet(name = 'Morpheus')
        self.Morpheus.addModule(mClass = 'cgmLimb',mType = 'torso',handles = 4)

    def getMesh(self):
        mFile = 'J:/Dropbox/MRv2Dev/Assets/Morphy/maya/scenes/Morphy_JoshTesting.ma'
        mc.file(mFile, i = True, pr = True, force = True,prompt = False) # prompt means no error message
        
    def sizeTest(self):
        spine = cgmPM.cgmLimb(self.Morpheus.getMessage('moduleChildren')[0],handles = 4)
        spine.templateNull.curveDegree = 2
        log.info(self.Morpheus.i_geoGroup.mNode)
        log.info(self.Morpheus.i_geoGroup)        
        self.Morpheus.i_geoGroup.doAddChild('Morphy_GRP')
        log.info(spine.isSized())
        spine.getGeneratedCoreNames()
        spine.doSize()
        
def cgmMeta_Test(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'cgmMeta_Test'	
	    self._b_autoProgressBar = 1
	    self._b_reportTimes = 1
	        
	    self.__dataBind__(*args, **kws)
	    self.l_funcSteps = [{'step':'Setup','call':self._setup_},	                        
	                        {'step':'cgmNode function calls','call':self._cgmNodeCalls_},
	                        {'step':'Attribute Handling','call':self._attributeHandling_},
	                        {'step':'Maya Message attribute handling','call':self._messageAttrHandling_},	                        
	                        {'step':'validateObj tests','call':self._validateObjArg_},
	                        {'step':'cgmAttr','call':self._cgmAttr_},
	                        {'step':'NodeFactory','call':self._NodeFactory_},
	                        {'step':'cgmObject calls','call':self._cgmObjectCalls_},
	                        {'step':'cgmObjectSet calls','call':self._cgmObjectSetCalls_},
	                        {'step':'cgmOptionVar calls','call':self._cgmOptionVarCalls_},
	                        {'step':'cgmBufferNode calls','call':self._cgmBufferNodeCalls_},
	                        {'step':'NameFactory','call':self._nameFactory_},
	                        {'step':'Puppet tests','call':cgmPuppet_tests},	                        
	                        ]
	def _setup_(self):
	    '''
	    Tests proper creation of objects from flag calls
	    '''    
	    try:mc.file(new=True,f=True)
	    except Exception,error:raise StandardError,"[File Open]{%s}"%error
	    
	    try:#Simple Node creation ==================================================================
		try:#Test name and node argument passing
		    self.MetaInstance = cgmMeta.cgmMetaFactory()
		    assert mc.objExists(self.MetaInstance.mNode)        
		except Exception,error:raise StandardError,"[Name/node arg]{%s}"%error
	
		#self.test_functionCalls()
		#Initial instance deleted at end of function call
	
		try:
		    self.MetaInstance = cgmMeta.cgmMetaFactory(name = 'Hogwarts')
		    assert mc.objExists(self.MetaInstance.mNode)        
		    assert self.MetaInstance.getShortName() == 'Hogwarts'     
		except Exception,error:raise StandardError,"['Hogwarts' being passed]{%s}"%error
	
		try:
		    self.MetaInstance = cgmMeta.cgmMetaFactory(node = 'Hogwarts')
		    assert mc.objExists(self.MetaInstance.mNode)                
		    assert self.MetaInstance.getShortName() == 'Hogwarts'     
		except Exception,error:raise StandardError,"[Pass node, no name...]{%s}"%error
	
		try:
		    self.MetaInstance = cgmMeta.cgmMetaFactory(node = 'Hogwarts', name = 'cgmTransform')
		    assert mc.objExists(self.MetaInstance.mNode)
		    assert self.MetaInstance.getShortName() == 'cgmTransform'
		except Exception,error:raise StandardError,"[Existing 'Hogwarts' node, new 'cgmTransform' name]{%s}"%error
	    except Exception,error:raise StandardError,"[Simple Node creation]{%s}"%error
	    
	    try:#Create nodeType ==================================================================
		self.MetaNode = cgmMeta.cgmMetaFactory(name = 'cgmNetwork', nodeType = 'network')
		assert mc.nodeType(self.MetaNode.mNode)=='network'
	
		self.MetaObject = cgmMeta.cgmMetaFactory(name = 'cgmTransform',nodeType = 'transform')
		assert mc.nodeType(self.MetaObject.mNode)=='transform'
	
		self.ObjectSet = cgmMeta.cgmMetaFactory(name = 'cgmObjectSet',nodeType = 'objectSet')
		assert mc.nodeType(self.ObjectSet.mNode)=='objectSet'
		
	    except Exception,error:raise StandardError,"[Create nodeType]{%s}"%error
    
	    try:#Create Test Objects and initialize
		#============== 
		nurbsCubeCatch = mc.nurbsCube()
		polyCubeCatch = mc.polyCube()  
		self.pCube = cgmMeta.cgmMetaFactory(polyCubeCatch[0],name = 'pCube')
		self.nCube = cgmMeta.cgmMetaFactory(nurbsCubeCatch[0],name = 'nCube')
	    except Exception,error:raise StandardError,"[Create nurbs/poly cubes]{%s}"%error
	
	def _cgmNodeCalls_(self): 
	    #select
	    _str_name = self.MetaInstance.getShortName()
	    assert mc.objExists(_str_name)
    
	    mc.select(cl=True)
	    self.MetaInstance.select()
	    assert mc.ls(sl=True)[0]== _str_name
    
	    try:#rrename
		self.MetaInstance.rename('FooBar')
		assert self.MetaInstance.getShortName() =='FooBar',"mNode is '%s'"%self.MetaInstance.mNode
		self.MetaInstance.select()
		assert mc.ls(sl=True)[0]=='FooBar'
	    except Exception,error:raise StandardError,"[rename]{%s}"%error
    
	    #convert
	    #new=self.MetaInstance.convertMClassType('MetaRig')
	    #assert isinstance(new,r9Meta.MetaRig)
	    #assert self.MetaInstance.mClass=='MetaRig'
    
	    try:#delete
		self.MetaInstance.delete()
		assert not mc.objExists(_str_name)
		mc.undo()		
	    except Exception,error:raise StandardError,"[delete]{%s}"%error
	    
	    
	    if not self.MetaNode:
		self.MetaNode = cgmMeta.cgmMetaFactory(name = 'cgmNode',nodeType = 'network')
    
	    #Assert some info
	    #----------------------------------------------------------   
	    assert self.MetaNode.referencePrefix is not None
    
	    #cgmNode functions
	    #---------------------------------------------------------- 
	    self.MetaNode.doName()
	    assert self.MetaNode.hasAttr('cgmName') is True
    
	    self.MetaObject.doCopyNameTagsFromObject(self.MetaNode.mNode)
	    assert self.MetaObject.cgmName == self.MetaNode.cgmName,"CGM Name copying failed"
    
	    self.MetaNode.doStore('stored',self.nCube.mNode)
	    assert self.MetaNode.stored[0] == self.nCube.mNode,"'%s' is stored"%self.MetaNode.stored
    
	    self.MetaNode.doRemove('stored')
	    assert self.MetaNode.hasAttr('stored') is False	    
	def _validateObjArg_(self):
	    try:
		null = mc.group(em=True)    
		i_node = cgmMeta.cgmNode(nodeType='transform')
		i_obj = cgmMeta.cgmObject(nodeType='transform')
	    except Exception,error:raise StandardError,"[creation]{%s}"%error
	    
	    try:cgmMeta.validateObjArg()
	    except:log.info("Empty arg should have failed and did")
	    else:
		raise StandardError,"Empty arg should have failed and did NOT"
	    
	    assert i_obj == cgmMeta.validateObjArg(i_obj.mNode),"string arg failed"
	    log.info("String arg passed!")
	    assert i_obj == cgmMeta.validateObjArg(i_obj),"instance arg failed"
	    log.info("instance arg passed!")
	    
	    i_returnObj = cgmMeta.validateObjArg(i_obj.mNode,cgmMeta.cgmObject)
	    assert issubclass(type(i_returnObj),cgmMeta.cgmObject),"String + mType arg failed!"
	    log.info("String + mType arg passed!")
	    
	    assert i_obj == cgmMeta.validateObjArg(i_obj,cgmMeta.cgmObject),"Instance + mType arg failed!"
	    log.info("Instance + mType arg passed!")
	    
	    try:validateObjArg(i_node.mNode,cgmMeta.cgmObject)
	    except:log.info("Validate cgmNode as cgmObject should have failed and did")
	    
	    assert issubclass(type(cgmMeta.validateObjArg(null)),cgmMeta.cgmNode),"Null string failed!"
	    log.info("Null string passed!")
	    
	    i_null = cgmMeta.validateObjArg(null,cgmMeta.cgmObject)
	    assert issubclass(type(i_null),cgmMeta.cgmObject),"Null as cgmObject failed!"
	    log.info("Null as cgmObjectpassed!")
	    
	    i_null.delete()
	    i_node.delete()
	    i_obj.delete()    
	def _cgmAttr_(self):    
	    self.cgmAttrNull = cgmMeta.cgmObject(name = 'cgmAttrNull',nodeType = 'transform')
	    node=self.cgmAttrNull
    
	    try:#String test
		#---------------- 
		self.cgmString = cgmMeta.cgmAttr(node,'stringTest',value = 'testing', keyable = True, lock=True)
		assert node.hasAttr('stringTest')
		assert self.cgmString.obj.mNode == node.mNode 
		assert self.cgmString.attrType == 'string'        
		assert self.cgmString.p_locked == True
		assert self.cgmString.stringTest == 'testing'
		assert self.cgmString.get() == 'testing'
	
		self.cgmString.value = 'catRatDog' #Change via declaration   
		assert self.cgmString.stringTest == 'catRatDog'
	
		assert self.cgmString.p_keyable == False
	    except Exception,error:raise StandardError,"[string test]{%s}"%error
    
	    try:#NameFlags
		#----------------   
		assert self.cgmString.p_nameLong == 'stringTest'
		self.cgmString.p_nameNice = 'strTst'
		assert self.cgmString.p_nameNice == 'strTst'
		self.cgmString.p_nameLong = 'stringTestChanged'
		assert self.cgmString.p_nameLong == 'stringTestChanged'
		self.cgmString.p_nameNice = 'stringTestChanged'
	
		self.cgmTx = cgmMeta.cgmAttr(node,'tx')
		self.cgmTx.p_nameAlias = 'thatWay'
		assert self.cgmTx.p_nameAlias == 'thatWay'
	    except Exception,error:raise StandardError,"[name flags]{%s}"%error
    
	    try:#Int test
		#---------------- 
		self.cgmIntAttr = cgmMeta.cgmAttr(node,'intTest',value = 7, keyable = True, lock=True)
		assert node.hasAttr('intTest')        
		assert self.cgmIntAttr.obj.mNode == node.mNode 
		assert self.cgmIntAttr.attrType == 'long', self.cgmIntAttr.attrType          
		assert self.cgmIntAttr.p_locked == True
		self.cgmIntAttr.p_hidden == False #Unhide        
		assert self.cgmIntAttr.intTest == 7
		assert attributes.doGetAttr(node.mNode,'intTest') == 7
		assert self.cgmIntAttr.get() == 7,self.cgmIntAttr.intTest
		assert self.cgmIntAttr.p_keyable == True   
		assert self.cgmIntAttr.p_hidden == False   
	
	
		#Assert some knowns
		assert self.cgmIntAttr.isDynamic()#Should be true
		assert self.cgmIntAttr.isNumeric()
		assert self.cgmIntAttr.isReadable()
		assert self.cgmIntAttr.isStorable()
		assert self.cgmIntAttr.isWritable()
	
		#mins, defaults, maxes
		log.info('>'*3 + " Int test --max,min,range...")        
		self.cgmIntAttr.p_defaultValue = 5
		assert self.cgmIntAttr.p_defaultValue == 5,self.cgmIntAttr.p_defaultValue
		self.cgmIntAttr.p_minValue = 1
		self.cgmIntAttr.p_maxValue = 6
		assert self.cgmIntAttr.value == 6,self.cgmIntAttr.value#new max should have cut it off 
		assert self.cgmIntAttr.p_minValue == 1
		assert self.cgmIntAttr.p_maxValue == 6
		assert self.cgmIntAttr.getRange() == [1,6],self.cgmIntAttr.getRange()
	
		log.info('>'*3 + " Int test -- conversion to float and back...")                
		self.cgmIntAttr.doConvert('float')#Convert to a float
		assert self.cgmIntAttr.attrType == 'double', self.cgmIntAttr.attrType          
		assert self.cgmIntAttr.intTest == 6.0
		#ssert self.cgmIntAttr.getRange() == [1.0,6.0],self.cgmIntAttr.getRange()#should have converted min/max as well
	
	
		self.cgmIntAttr.doConvert('int')#Convert back
		assert self.cgmIntAttr.attrType == 'long', self.cgmIntAttr.attrType          
		assert self.cgmIntAttr.p_locked == True
		assert self.cgmIntAttr.intTest == 6  
	    except Exception,error:raise StandardError,"[Int tests]{%s}"%error

	    try:#Float test
		self.cgmFloatAttr = cgmMeta.cgmAttr(node,'floatTest',value = 1.333, keyable = True, lock=True)
		assert node.hasAttr('floatTest')                
		assert self.cgmFloatAttr.obj.mNode == node.mNode 
		assert self.cgmFloatAttr.attrType == 'double', self.cgmFloatAttr.attrType 
	
		self.cgmFloatAttr.p_maxValue = 6       
		self.cgmFloatAttr.p_softMax = 5.5
		assert self.cgmFloatAttr.p_softMax == 5.5
		self.cgmFloatAttr.p_softMin = .5
		self.cgmFloatAttr.p_minValue = 0      
		assert self.cgmFloatAttr.p_softMin == .5
		assert self.cgmFloatAttr.getSoftRange() == [.5,5.5],self.cgmFloatAttr.getSoftRange()
		assert self.cgmFloatAttr.getRange() == [0,6.0],self.cgmFloatAttr.getRange()
	
		self.cgmFloatAttr.p_keyable = False
		assert self.cgmFloatAttr.p_keyable == False
	    except Exception,error:raise StandardError,"[float tests]{%s}"%error
    
    
	    try:#Message test
		#---------------- 
		self.cgmSingleMsgAttr = cgmMeta.cgmAttr(node,'messageTest',value = self.pCube.mNode,lock=True) 
		self.cgmSingleMsgAttr2 = cgmMeta.cgmAttr(node,'messageTest2',value = self.pCube.mNode,lock=True) 
		assert node.hasAttr('messageTest')                
		assert node.hasAttr('messageTest2')                        
		assert [self.pCube.getLongName()] == self.cgmSingleMsgAttr.value, self.cgmSingleMsgAttr.value
		assert [self.pCube.getLongName()] == self.cgmSingleMsgAttr2.value, self.cgmSingleMsgAttr.value
		assert self.cgmSingleMsgAttr.value == self.cgmSingleMsgAttr2.value #These should be the same thing
	
		self.cgmSingleMsgAttr.value = self.nCube.mNode#change value
		assert self.nCube.getLongName() in self.cgmSingleMsgAttr.value, self.cgmSingleMsgAttr.value
	
		self.cgmMultiMsgAttr = cgmMeta.cgmAttr(node,'multiMessageTest',value = [self.nCube.mNode, self.pCube.mNode],lock=True) 
		assert node.hasAttr('multiMessageTest')                                
		assert self.cgmMultiMsgAttr.isMulti()
		assert not self.cgmMultiMsgAttr.isIndexMatters()
		assert len(self.cgmMultiMsgAttr.value) == 2,self.cgmMultiMsgAttr.value
		assert self.nCube.getLongName() in self.cgmMultiMsgAttr.value
	
		self.cgmMultiMsgAttr.value = self.nCube.mNode #make a simple message by declaration of content
		assert not self.cgmMultiMsgAttr.isMulti(),self.cgmMultiMsgAttr.value       
	
		self.cgmMultiMsgAttr.value = [self.nCube.mNode]#Reassign value
		assert len(self.cgmMultiMsgAttr.value) == 1,self.cgmMultiMsgAttr.value        
		assert self.cgmMultiMsgAttr.isMulti(),self.cgmMultiMsgAttr.value
		assert self.cgmMultiMsgAttr.value == [self.nCube.getLongName()]
	
		self.cgmMultiMsgAttr.value = [self.nCube.mNode, self.pCube.mNode]#And again to what we started with
		assert self.cgmMultiMsgAttr.value == [self.nCube.mNode, self.pCube.mNode]      
	
		#attributes.storeInfo(node.mNode,'multiMessageTest',[self.nCube.mNode, self.pCube.mNode])
	    except Exception,error:raise StandardError,"[Message tests]{%s}"%error
	
	    try:#Enum test
		#---------------- 
		log.info('>'*3 + " Enum test and connection to float...")
		self.cgmEnumAttr = cgmMeta.cgmAttr(node,'enumTest',value = 3, enum = '1:2:3:red:4:5:6')
		assert node.hasAttr('enumTest')                                        
		assert self.cgmEnumAttr.value == 3
		assert self.cgmEnumAttr.p_hidden == False
		self.cgmEnumAttr.doConnectOut(self.cgmFloatAttr.p_combinedName)#Connect 
		assert self.cgmEnumAttr.getDriven() == [self.cgmFloatAttr.p_combinedName]," %s not equal to [%s]"%(self.cgmEnumAttr.getDriven(), self.cgmFloatAttr.p_combinedName)#This should be what's connected
	
		#Double3 test
		#---------------- 
		log.info('>'*3 + " Double3 and connection from float...")        
		self.cgmVectorAttr = cgmMeta.cgmAttr(node,'vecTest',value = [3,1,2])
		self.cgmVectorXAttr = cgmMeta.cgmAttr(node,'vecTestX')                
		assert node.hasAttr('vecTest')  
		assert node.hasAttr('vecTestX')
		assert self.cgmVectorAttr.value == [3.0,1.0,2.0],self.cgmVectorAttr.value
		log.info(self.cgmVectorXAttr.value)
		assert self.cgmVectorXAttr.value == self.cgmVectorAttr.value[0],self.cgmVectorXAttr.value
		self.cgmVectorAttr.value = [1,44,7]#Don't currently support () args
		assert self.cgmVectorAttr.value == [1.0,44.0,7.0],self.cgmVectorAttr.value
		self.cgmVectorXAttr.doConnectIn(self.cgmFloatAttr.p_combinedName)
		assert self.cgmVectorXAttr.getDriver() == self.cgmFloatAttr.p_combinedName," %s not equal to [%s]"%(self.cgmVectorXAttr.getDriver(), self.cgmFloatAttr.p_combinedName)#This should be what's connected
	    except Exception,error:raise StandardError,"[enum]{%s}"%error
	    #node.select()	    
	def _NodeFactory_(self):
	    NodeF.test_argsToNodes()	
	def _attributeHandling_(self):
	    '''
	    Modified from Mark Jackson's testing for Red9
	    This tests the standard attribute handing in the MetaClass.__setattr__ 
	    '''
	    if not self.MetaInstance:
		self.MetaInstance = cgmMeta.cgmMetaFactory()
        
	    node=self.MetaInstance
    
	    try:#standard attribute handling
		node.addAttr('stringTest', "this_is_a_string")  #create a string attribute
		node.addAttr('fltTest', 1.333)        #create a float attribute
		node.addAttr('intTest', 3)            #create a int attribute
		node.addAttr('boolTest', False)       #create a bool attribute
		node.addAttr('enumTest',enumName='A:B:D:E:F', attrType ='enum',value = 1) #create an enum attribute
		node.addAttr('vecTest', [0,0,0], attrType ='double3') #create a double3
	    except Exception,error:raise StandardError,"[Standard handling]{%s}"%error
    
	    try:#testAttrs with no value flags but attr flag to use default 
		node.addAttr('stringTestNoValue', attrType = 'string')  #create a string attribute
		node.addAttr('fltTestNoValue', attrType = 'float')  #create a string attribute
		node.addAttr('intTestNoValue', attrType = 'int')  #create a string attribute
		node.addAttr('boolTestNoValue', attrType = 'bool')  #create a string attribute
		node.addAttr('enumTestNoValue', attrType = 'enum')  #create a string attribute
		#node.addAttr('vecTestNoValue', attrType ='double3') #create a double3
	    except Exception,error:raise StandardError,"[test creation - no values]{%s}"%error
    
    
	    try:#create a string attr with JSON serialized data
		testDict={'jsonFloat':1.05,'jsonInt':3,'jsonString':'string says hello','jsonBool':True}
		node.addAttr('jsonTest',testDict,attrType = 'string')
	    except Exception,error:raise StandardError,"[json serialized]{%s}"%error
    
	    try:#test the hasAttr call in the baseClass
		assert node.hasAttr('stringTest')
		assert node.hasAttr('fltTest')
		assert node.hasAttr('intTest')
		assert node.hasAttr('boolTest')
		assert node.hasAttr('enumTest')
		assert node.hasAttr('jsonTest')
		assert node.hasAttr('vecTest')
		assert node.hasAttr('stringTestNoValue')
		assert node.hasAttr('fltTestNoValue')
		assert node.hasAttr('intTestNoValue')
		assert node.hasAttr('boolTestNoValue')
		assert node.hasAttr('enumTestNoValue')
	    except Exception,error:raise StandardError,"[created?]{%s}"%error
    
    
	    try:#test the actual Maya node attributes
		#------------------------------------
		assert mc.getAttr('%s.stringTest' % node.mNode, type=True)=='string'
		assert mc.getAttr('%s.fltTest' % node.mNode, type=True)=='double' or 'float', "Type is '%s'"%mc.getAttr('%s.fltTest' % node.mNode, type=True)
		assert mc.getAttr('%s.intTest' % node.mNode, type=True)=='long'
		assert mc.getAttr('%s.boolTest' % node.mNode, type=True)=='bool'
		assert mc.getAttr('%s.enumTest' % node.mNode, type=True)=='enum'
		assert mc.getAttr('%s.jsonTest' % node.mNode, type=True)=='string'
	
		assert mc.getAttr('%s.stringTest' % node.mNode)=='this_is_a_string'
		assert mc.getAttr('%s.fltTest' % node.mNode)==1.333,"Value is %s"%mc.getAttr('%s.fltTest' % node.mNode)
		assert mc.getAttr('%s.intTest' % node.mNode)==3
		assert mc.getAttr('%s.boolTest' % node.mNode)==False
		assert mc.getAttr('%s.enumTest' % node.mNode)==1
		assert mc.getAttr('%s.jsonTest' % node.mNode)=='{"jsonFloat": 1.05, "jsonBool": true, "jsonString": "string says hello", "jsonInt": 3}',"Value is '%s'%"%self.jsonTest
		assert mc.getAttr('%s.vecTest' % node.mNode)== [(0, 0, 0)]
	
	
		assert mc.getAttr('%s.stringTestNoValue' % node.mNode)==None
		assert mc.getAttr('%s.fltTestNoValue' % node.mNode)==0
		assert mc.getAttr('%s.intTestNoValue' % node.mNode)==0
		assert mc.getAttr('%s.boolTestNoValue' % node.mNode)==0
		assert mc.getAttr('%s.enumTestNoValue' % node.mNode)==0
	    except Exception,error:raise StandardError,"[Test created]{%s}"%error
	
    
    
	    try:#now check the MetaClass getMessage and __setattr__ calls
		#--------------------------------------------------------------
		assert node.intTest==3       
		node.intTest=10     #set back to the MayaNode
		assert node.intTest==10
		#float
		assert node.fltTest==1.333
		node.fltTest = 3.55   #set the float attr
		assert node.fltTest==3.55,"Value is %s"%node.fltTest
		#string
		assert node.stringTest=='this_is_a_string'
		node.stringTest="change the text"   #set the string attr
		assert node.stringTest=='change the text'
		#bool
		assert node.boolTest==False
		node.boolTest=True  #set bool
		assert node.boolTest==True
		#enum
		assert node.enumTest==1
		node.enumTest='A'
		assert node.enumTest==0
		node.enumTest=2
		assert node.enumTest==2
		#double3
		assert node.vecTestX==0
		node.vecTestX = 1
		assert node.vecTestX==1
		node.vecTest = 2,2,2
		assert node.vecTestX==2
		assert node.vecTest == (2.0, 2.0, 2.0),'%s'%node.vecTest
	    except Exception,error:raise StandardError,"[Meta calls the same?]{%s}"%error
    
    
	    try:#json string handlers
		assert type(node.jsonTest)==dict
		assert node.jsonTest=={'jsonFloat':1.05,'jsonInt':3,'jsonString':'string says hello','jsonBool':True}
		assert node.jsonTest['jsonFloat']==1.05
		assert node.jsonTest['jsonInt']==3 
		assert node.jsonTest['jsonString']=='string says hello'
		assert node.jsonTest['jsonBool']==True 
	
		del(node.boolTest)
		assert mc.objExists(node.mNode)
		assert not node.hasAttr('boolTest')
		assert not mc.attributeQuery('boolTest',node=node.mNode,exists=True)
	    except Exception,error:raise StandardError,"[json handling]{%s}"%error
	    
	def _messageAttrHandling_(self):
	    '''
	    test the messageLink handling in the __setattr__ block
	    '''
    
	    node=cgmMeta.cgmObject(name='MessageCatcher')
    
	    try:#make sure we collect LONG names for these as all wrappers deal with longName
		cube1= cgmMeta.cgmNode(mc.polyCube()[0])
		cube2= cgmMeta.cgmNode(mc.polyCube()[0])
		cube3= cgmMeta.cgmNode(mc.polyCube()[0])
		cube4= cgmMeta.cgmNode(mc.polyCube()[0])
		cube5= cgmMeta.cgmNode(mc.polyCube()[0])
		cube6= cgmMeta.cgmNode(mc.polyCube()[0])
	    except Exception,error:raise StandardError,"[cube creation]{%s}"%error
    
	    try:
		node.addAttr('msgMultiTest', value=[cube1.mNode,cube2.mNode,cube3.mNode], attrType='message')   #multi Message attr
		node.addAttr('msgSingleTest', value=cube3.mNode, attrType='messageSimple')    #non-multi message attr
		node.addAttr('msgSingleTest2', value=cube3.mNode, attrType='messageSimple')    #non-multi message attr
	
		assert node.hasAttr('msgMultiTest')
		assert node.hasAttr('msgSingleTest')
		assert node.hasAttr('msgSingleTest2')
	
		assert mc.getAttr('%s.msgMultiTest' % node.mNode, type=True)=='message'
		assert mc.getAttr('%s.msgSingleTest' % node.mNode, type=True)=='message'
		assert mc.attributeQuery('msgMultiTest',node=node.mNode, multi=True)==True
		assert mc.attributeQuery('msgSingleTest',node=node.mNode, multi=True)==False
	    except Exception,error:raise StandardError,"[attr creation]{%s}"%error
    
	    #NOTE : cmds returns shortName, but all MetaClass attrs are always longName
	    try:
		assert attributes.returnMessageData(node.mNode,'msgSingleTest') == [cube3.getLongName()],"%s is not [%s]"%(attributes.returnMessageData(node.mNode,'msgSingleTest'),cube3.getLongName())
		assert node.msgSingleTest2==[cube3.getLongName()]
		assert node.msgMultiTest ==[cube1.mNode,cube2.mNode,cube3.mNode],"%s is not [%s,%s,%s]"%(node.getMessage('msgMultiTest',False),cube1.mNode,cube2.mNode,cube3.mNode)        
		assert node.getMessage('msgMultiTest',False) ==[cube1.getShortName(),cube2.getShortName(),cube3.getShortName()],"%s is not [%s,%s,%s]"%(node.getMessage('msgMultiTest',False),cube1.mNode,cube2.mNode,cube3.mNode)
		node.msgSingleTest2 = cube1.mNode
		assert node.msgSingleTest2 == [cube1.mNode],node.msgSingleTest2
	    except Exception,error:raise StandardError,"[connections?]{%s}"%error
	
                     
        	    
	def _cgmObjectCalls_(self):
    	    #Let's move our test objects around and and see what we get
	    #----------------------------------------------------------  
	    self.MetaObject.rotateOrder = 0 #To have  base to check from
    
	    try:#Randomly move stuff
		for attr in 'translateX','translateY','translateZ','rotateX','rotateY','rotateZ':
		    self.pCube.__setattr__(attr,random.choice(range(1,10)))
		for attr in 'scaleX','scaleY','scaleZ':
		    self.pCube.__setattr__(attr,random.choice([1,.5,.75]))
		self.pCube.rotateOrder = random.choice(range(1,5))#0 not an option for accurate testing
	
		for attr in 'translateX','translateY','translateZ','rotateX','rotateY','rotateZ':
		    self.nCube.__setattr__(attr,random.choice(range(1,10)))
		for attr in 'scaleX','scaleY','scaleZ':
		    self.nCube.__setattr__(attr,random.choice([1,.5,.75]))
		self.nCube.rotateOrder = random.choice(range(1,5))
	    except Exception,error:raise StandardError,"[Move stuff]{%s}"%error
    
	    try:#Parent and assert relationship
		#mc.parent(self.pCube.mNode,self.nCube.mNode)#parent pCube to nCube
		self.pCube.parent = self.nCube.mNode
		assert self.pCube.getParent() == self.nCube.mNode,"nCube is not parent"
		assert self.pCube.parent == self.nCube.mNode,"nCube is not parent"
		assert self.pCube.getShortName() in self.nCube.getChildren(),"pCube is not in children - %s"%self.nCube.getChildren()
		assert self.pCube.getShapes() is not None,"No Shapes found on pCube" #Check for shapes on nurbs
		assert self.nCube.getTransformAttrs() == self.pCube.getTransformAttrs(), "Transform attribute lists don't match"
	
		self.pCube.parent = False #Unparent
		assert self.pCube.parent == False #Verify 
		self.pCube.doAddChild(self.nCube.mNode)#Parent by adding as child
		assert self.nCube.getShortName() in self.pCube.getChildren(),"Not in the children : %s"%self.pCube.getChildren()
	    except Exception,error:raise StandardError,"[Parenting]{%s}"%error
	
	
	    try:#Rotate order match
		self.MetaObject.doCopyRotateOrder(self.pCube.mNode)
		assert self.MetaObject.rotateOrder == self.pCube.rotateOrder,"Copy rotate order failed"
	
		self.MetaObject.doCopyRotateOrder = self.nCube.rotateOrder #Just set it
		assert self.MetaObject.doCopyRotateOrder == self.nCube.rotateOrder
	    except Exception,error:raise StandardError,"[Rotate order]{%s}"%error
    
	    try:#Group
		previousPos = distance.returnWorldSpacePosition(self.pCube.mNode)
		self.pCube.doGroup(True)
		#assert previousPos == distance.returnWorldSpacePosition(self.pCube.mNode),"previous %s != %s"%(previousPos,distance.returnWorldSpacePosition(self.pCube.mNode))
		assert self.pCube.getParent() != self.nCube.mNode,"nCube shouldn't be the parent"
	    except Exception,error:raise StandardError,"[Grouping]{%s}"%error
    
	    try:#setDrawingOverrideSettings
		self.pCube.overrideEnabled = 1     
		TestDict = {'overrideColor':20,'overrideVisibility':1}
		self.pCube.setDrawingOverrideSettings(TestDict, pushToShapes=True)
	
		assert self.pCube.overrideEnabled == 1
		assert self.pCube.overrideColor == 20
		assert self.pCube.overrideVisibility == 1
	
		for shape in self.pCube.getShapes():
		    for a in TestDict.keys():
			assert attributes.doGetAttr(shape,a) == TestDict[a],"'%s.%s' is not %s"%(shape,a,TestDict[a])
	    except Exception,error:raise StandardError,"[Drawing overrides]{%s}"%error
    
	    try:#Copy pivot
		self.MetaObject.doCopyPivot(self.pCube.mNode)
	    except Exception,error:raise StandardError,"[copy pivot]{%s}"%error
                        
	def _cgmObjectSetCalls_(self):
	    try:
		self.ObjectSet = cgmMeta.cgmMetaFactory(name = 'cgmObjectAnimationSet',nodeType = 'objectSet',setType = 'animation', qssState = True)
		self.MayaDefaultSet = cgmMeta.cgmMetaFactory(node = 'defaultObjectSet')   
    
		#from cgm.core.cgmMeta import *
		self.ObjectSet2 = cgmMeta.cgmObjectSet(setName = 'cgmObjectAnimationSet2',value = self.ObjectSet.value )
		#Initialize another set with a value on call
		assert self.ObjectSet2.value == self.ObjectSet.value
		del self.ObjectSet2.value        
	    except Exception,error:raise StandardError,"[Initial]{%s}"%error
    
	    try:#Assert some info
		#---------------- 
		log.info('>'*3 + " Checking object Set States...")
		assert self.MayaDefaultSet.mayaSetState == True
		assert self.ObjectSet.mayaSetState == False
	
		assert self.MayaDefaultSet.qssState == False
		assert self.ObjectSet.qssState == True
		self.ObjectSet.qssState = False
		assert self.ObjectSet.qssState == False
	
		assert self.ObjectSet.objectSetType == 'animation',"Type is '%s'"%self.ObjectSet.objectSetType
		self.ObjectSet.objectSetType = 'modeling'
		assert self.ObjectSet.objectSetType == 'modeling'
	    except Exception,error:raise StandardError,"[Initial assertations]{%s}"%error
    
	    try:#Adding and removing
		#-------------------
		log.info('>'*3 + " Adding and removing by property...")
		assert not self.ObjectSet.getList()
	
		self.ObjectSet.value = [self.pCube.mNode, self.nCube.mNode,(self.pCube.mNode+'.tx')] # Add an attribute
	
		assert self.ObjectSet.doesContain(self.pCube.mNode)
		assert self.ObjectSet.doesContain(self.nCube.mNode)
		assert '%s.translateX'%self.pCube.getShortName() in self.ObjectSet.getList(),"%s"%self.ObjectSet.getList()
	
		self.ObjectSet.value = False
		assert not self.ObjectSet.value
	    except Exception,error:raise StandardError,"[Add/remove by property]{%s}"%error
	
	    try:#Adding and removing
		#-------------------
		log.info('>'*3 + " Adding and removing...")
		assert not self.ObjectSet.getList()
	
		self.ObjectSet.addObj(self.pCube.mNode)
		self.ObjectSet.addObj(self.nCube.mNode)
		self.ObjectSet.addObj(self.pCube.mNode+'.tx') # Add an attribute
	
		assert self.ObjectSet.doesContain(self.pCube.mNode)
		assert self.ObjectSet.doesContain(self.nCube.mNode)
		assert '%s.translateX'%self.pCube.getShortName() in self.ObjectSet.getList(),"%s"%self.ObjectSet.getList()
	
		self.ObjectSet.removeObj(self.pCube.mNode)
		self.ObjectSet.removeObj(self.nCube.mNode)
		log.info("%s"%self.pCube.getShortName() )
	
		assert not self.ObjectSet.doesContain(self.pCube.mNode),"%s"%self.ObjectSet.getList()
		assert not self.ObjectSet.doesContain(self.nCube.mNode),"%s"%self.ObjectSet.getList()
	    except Exception,error:raise StandardError,"[Check adds]{%s}"%error
    
	    try:#Selecting/purging/copying
		#-------------------------
		log.info('>'*3 + " Selecting, purging, copying...") 
	
		mc.select(cl=True)
		self.ObjectSet.select()#Select set
		assert mc.ls(sl = True) == self.ObjectSet.getList()
	
		mc.select(cl=True)
		self.ObjectSet.selectSelf() # Select Self
		assert mc.ls(sl = True) == [self.ObjectSet.mNode]
	
		#Copy set
		catch = self.ObjectSet.copy()
		self.ObjectSetCopy = cgmMeta.cgmMetaFactory(catch) #Initialize copy
		assert self.ObjectSet.getList() == self.ObjectSetCopy.getList(),"Sets don't match"
		assert self.ObjectSet.objectSetType == self.ObjectSetCopy.objectSetType,"Object Set types don't match"
		assert self.ObjectSet.qssState == self.ObjectSetCopy.qssState,"qssStates don't match"
	
		#Purge
		self.ObjectSetCopy.purge()
		assert not self.ObjectSetCopy.getList(),"Dup set failed to purge"
	    except Exception,error:raise StandardError,"[Selecting/purging/copying]{%s}"%error
    
	    try:#Keying, deleting keys, reseting
		#------------------------------- 
		log.info('>'*3 + " Keying, deleting keys, reseting...")        
	
		self.pCube.tx = 2
	
		self.ObjectSet.key()#Key    
		assert mc.findKeyframe( self.pCube.mNode, curve=True, at='translateX' ),"translateX should have a key"
		assert mc.findKeyframe( self.pCube.mNode, curve=True, at='translateY' ) is None,"translateY shouldn't have a key"
	
		self.ObjectSet.deleteKey()#Delete key
		assert mc.findKeyframe( self.pCube.mNode, curve=True, at='translateX' ) is None
	
		self.ObjectSet.reset()
		assert self.pCube.tx == 0
	    except Exception,error:raise StandardError,"[Keying, deleting keys, reseting]{%s}"%error
	def _cgmOptionVarCalls_(self):
	    try:#Purge the optionVars
		for var in 'cgmVar_intTest','cgmVar_stringTest','cgmVar_floatTest':
		    if mc.optionVar(exists = var):
			mc.optionVar(remove = var)
	    except Exception,error:raise StandardError,"[manual purge]{%s}"%error
    
	    try:# Testing creation/conversion of ine optionVar
		#-------------------------
		self.OptionVarInt = cgmMeta.cgmOptionVar('cgmVar_intTest')#No arg should default to int
	
		assert self.OptionVarInt.varType == 'int',"Form should be int by default"
		assert self.OptionVarInt.value == 0,"Value should be 0"
	
		self.OptionVarInt.value = 3
		assert self.OptionVarInt.value == 3,"Value should be 3"
	
		self.OptionVarInt.varType = 'float'
		assert self.OptionVarInt.value == 3.0,"Value should be 3.0"
		assert self.OptionVarInt.varType == 'float',"Form should be float after conversion"
	
		self.OptionVarInt.varType = 'string'
		assert self.OptionVarInt.value == '3.0',"Value should be 3.0"
		assert self.OptionVarInt.varType == 'string',"Form should be string after conversion"
	
		self.OptionVarInt.varType = 'int'
		assert self.OptionVarInt.value == 3,"Value should be 3, found %s"%self.OptionVarInt.value
		assert self.OptionVarInt.varType == 'int',"Form should be string after conversion"
	
		self.OptionVarInt.value = 0
		self.OptionVarInt.toggle()
		assert self.OptionVarInt.value == 1
	    except Exception,error:raise StandardError,"[Creation/Conversion...]{%s}"%error
	
    
	    try:# String varType test and initValue Test
		self.OptionVarString = cgmMeta.cgmOptionVar('cgmVar_stringTest', defaultValue='batman')#String type
	
		self.OptionVarString.varType = 'string'
		assert self.OptionVarString.value == 'batman',"Value should be 'batman, found %s on %s'"%(self.OptionVarString.value,self.OptionVarString.name)
		assert self.OptionVarString.varType == 'string',"Form should be string after conversion"
	
		self.OptionVarString.value = 'testing'
		assert self.OptionVarString.value == 'testing',"Value should be 'testing'"
		self.OptionVarString = cgmMeta.cgmOptionVar('cgmVar_stringTest', defaultValue='batman')#String type
		assert self.OptionVarString.value == 'testing',"Value should be 'testing' after reinitializaton"
		self.OptionVarString = cgmMeta.cgmOptionVar('cgmVar_stringTest', value = 'cats', defaultValue='batman')#String type
		assert self.OptionVarString.value == 'cats',"Value should be 'cats' after reinitializaton"
	
		self.OptionVarString.value = [self.nCube.mNode,self.pCube.mNode]#Set via list
		assert len(self.OptionVarString.value) == 2,"Len is %s"%len(self.OptionVarString.value)
		assert type(self.OptionVarString.value) is list,"Type is %s"%type(self.OptionVarString.value)
	
		self.OptionVarString.value = (self.nCube.mNode,self.pCube.mNode,'test3')#set via tuple
		assert len(self.OptionVarString.value) == 3,"Len is %s"%len(self.OptionVarString.value)
		assert type(self.OptionVarString.value) is list,"Type is %s"%type(self.OptionVarString.value)
	    except Exception,error:raise StandardError,"[String tests]{%s}"%error
    
	    try:# Appending to string, removing, select and exist check testing
		#-------------------------	
		self.OptionVarString.append('test4')# append a string
		assert self.OptionVarString.value[3] == 'test4'
	
		self.OptionVarString.append(3)# append a number as a string
		assert self.OptionVarString.value[4] == '3'
	
		self.OptionVarString.append(3.0)# append a float as a string
		assert self.OptionVarString.value[5] == '3.0'
	
		self.OptionVarString.remove('3.0')# remove an item
		assert len(self.OptionVarString.value) == 5,"Len is %s"%len(self.OptionVarString.value)
	
		self.OptionVarString.select() # Try to select our stuff
		len(mc.ls(sl=True)) == 2
		self.OptionVarString.existCheck()#Remove maya objects that don't exist
		len(self.OptionVarString.value) == 2
	    except Exception,error:raise StandardError,"[Apend/Remove/select/exists...]{%s}"%error
    
	    try:# Float testing and translation testing
		#-------------------------
		self.OptionVarFloat = cgmMeta.cgmOptionVar('cgmVar_floatTest',value = 1.0,varType = 'float')#Float type
	
		assert self.OptionVarFloat.varType == 'float'
		assert self.OptionVarFloat.value == 1
	
		self.OptionVarFloat.append(2)
		log.info(self.OptionVarFloat.value)                
		assert self.OptionVarFloat.value[1] == 2.0
	
		self.OptionVarFloat.varType = 'int' #Convert to int
		log.info(self.OptionVarFloat.value)                
	    except Exception,error:raise StandardError,"[Float]{%s}"%error
	
    
	    try:# Delete checking	
		#Because option vars are not local. We need to delete them all...
		del self.OptionVarInt.value #Deletion from property
		assert not mc.optionVar(exists = 'cgmVar_intTest')
	
		self.OptionVarString.purge() #Deletion via purge
		assert not mc.optionVar(exists = 'cgmVar_stringTest')
	    except Exception,error:raise StandardError,"[delete]{%s}"%error
		
    
	    try:# Float varType test and initValue Test
		#-------------------------
		log.info('>'*3 + " String varType test and initValue Test...")   
		self.OptionVarString = cgmMeta.cgmOptionVar('cgmVar_stringTest', defaultValue='batman')#String type
	    except Exception,error:raise StandardError,"[float init value]{%s}"%error
	def _cgmBufferNodeCalls_(self):
	    self.BufferNode = cgmMeta.cgmBufferNode(name = 'testBuffer',value = ['test1','test2'],overideMessageCheck = True)#No arg should default to int
    
	    assert self.BufferNode.value == ['test1','test2'],"Value should be ['test1','test2'], is %s"%self.BufferNode.value
	    assert self.BufferNode.hasAttr('messageOverride'),"Missing message override"
	    assert self.BufferNode.messageOverride == True,"Message Override should be True. Is %s"%self.BufferNode.messageOverride
	    assert self.BufferNode.returnNextAvailableCnt() == 2
	    self.BufferNode.messageOverride = False
	    self.BufferNode.store(self.BufferNode.mNode)
	    assert self.BufferNode.value[2]==self.BufferNode.mNode
	       
	def _nameFactory_(self):	    
	    nf = cgmMeta.NameFactory
	    #>>> Create some nodes
	    i_net1 = cgmMeta.cgmNode(name = 'net',nodeType = 'network')        
	    i_net1.addAttr('cgmName','net', attrType = 'string')
	    assert nf(i_net1).getBaseIterator() == 0,"baseIterator: %s"%nf(i_net1).getBaseIterator()
	    
	    i_net2 = cgmMeta.cgmNode( mc.duplicate(i_net1.mNode)[0] )
	    assert nf(i_net1).getMatchedSiblings() == [i_net2],"%s"%nf(i_net1).getMatchedSiblings()
	    assert nf(i_net2).getMatchedSiblings() == [i_net1],"%s"%nf(i_net2).getMatchedSiblings()
	    assert nf(i_net1).getBaseIterator() == 1,"%s"%"baseIterator: %s"%nf(i_net1).getBaseIterator()
	    assert i_net1.getNameDict() == i_net2.getNameDict(),"Name dicts not equal"
	    assert nf(i_net1).getIterator() == 1
	    i_net1.doName(fastIterate = False)
	    assert nf(i_net2).getIterator() == 2
	    nf(i_net2).doNameObject(fastIterate = False)
	    assert '2' in list(i_net2.mNode),"2 not in : '%s'"%i_net2.mNode
	    
	    #Transform nodes
	    i_trans1a = cgmMeta.cgmObject(name = 'trans')
	    i_parent = cgmMeta.cgmObject(name = 'parent')
	    i_parent.addAttr('cgmName','nameParent', attrType = 'string')
	    
	    i_trans1b = cgmMeta.cgmObject(mc.duplicate(i_trans1a.mNode)[0] )
	    i_trans1a.parent = i_parent.mNode
	    i_trans1b.parent = i_parent.mNode
	    assert i_trans1b.mNode in i_trans1a.getSiblings(),"%s"%i_trans1a.getSiblings()
	    assert nf(i_trans1a).getMatchedSiblings() == [i_trans1b],"%s"%nf(i_trans1a).getMatchedSiblings()
	    assert nf(i_trans1b).getMatchedSiblings() == [i_trans1a],"%s"%nf(i_trans1b).getMatchedSiblings()        
	    assert nf(i_trans1b).returnUniqueGeneratedName(fastIterate = False) == nf(i_trans1a).returnUniqueGeneratedName(fastIterate = False),"Not returning same name buffer"
	    
	    #Name different ways
	    bufferName =  nf(i_trans1a).returnUniqueGeneratedName(fastIterate = False)
	    nf(i_trans1a).doNameObject(i_trans1b,fastIterate = False)#name second object from firsts call
	    assert i_trans1b.getShortName() == bufferName,"Not the expected name after alternate naming method"
	    buffer1Name =  nf(i_trans1a).returnUniqueGeneratedName(fastIterate = False)
	    buffer2Name = i_trans1b.getShortName()
	    nf(i_parent).doName(nameChildren = True,fastIterate = False)#Name Heir
	    assert i_trans1b.getShortName() == buffer2Name,"%s != %s"%(i_trans1b.getShortName(),buffer2Name)
	    
	    for i_n in [i_net1,i_net2,i_trans1a,i_trans1b,i_parent]:
		assert issubclass(type(i_n),cgmMeta.cgmNode),"%s not a cgmNode"%i_n
		
	def _puppetTests_(self):    
	    self.Puppet = cgmPM.cgmPuppet(name = 'Kermit')
	    Puppet = self.Puppet
    
	    try:#Assertions on the network null
		#----------------------------------------------------------
		assert mc.nodeType(Puppet.mNode) == 'network'
	
		puppetDefaultValues = {'cgmName':['string','Kermit'],
		                       'cgmType':['string','puppetNetwork'],
		                       'mClass':['string','cgmPuppet'],
		                       'version':['double',1.0],
		                       'masterNull':['message'],
		                       'font':['string','Arial'],
		                       'axisAim':['enum',2],
		                       'axisUp':['enum',1],
		                       'axisOut':['enum',0]}                                   
	
		for attr in puppetDefaultValues.keys():
		    assert Puppet.hasAttr(attr),("'%s' missing attr:%s"%(self.Puppet.mNode,attr))
		    assert mc.getAttr('%s.%s'%(Puppet.mNode,attr), type=True) == puppetDefaultValues.get(attr)[0], "Type is '%s'"%(mc.getAttr('%s.%s' %(Puppet.mNode,attr), type=True))
		    if len(puppetDefaultValues.get(attr)) > 1:#assert that value
			log.debug("%s"% attributes.doGetAttr(Puppet.mNode,attr))                
			assert attributes.doGetAttr(Puppet.mNode,attr) == puppetDefaultValues.get(attr)[1],"%s is not %s"%(attributes.doGetAttr(Puppet.mNode,attr),puppetDefaultValues.get(attr)[1])
	    except Exception,error:raise StandardError,"[network null]{%s}"%error
    
	    try:#Assertions on the masterNull
		#----------------------------------------------------------
		log.info('>'*3 + " Assertions on the masterNull...")
		assert Puppet.masterNull.getShortName() == Puppet.cgmName
		assert Puppet.masterNull.puppet.mNode == Puppet.mNode,Puppet.masterNull.puppet
		
	
		masterDefaultValues = {'cgmType':['string','ignore'],
		                       'cgmModuleType':['string','master']}       
	
		for attr in masterDefaultValues.keys():
		    assert Puppet.masterNull.hasAttr(attr),("'%s' missing attr:%s"%(Puppet.masterNull.mNode,attr))
		    assert mc.getAttr('%s.%s'%(Puppet.masterNull.mNode,attr), type=True) == masterDefaultValues.get(attr)[0], "Type is '%s'"%(mc.getAttr('%s.%s' %(Puppet.masterNull.mNode,attr), type=True))
		    if len(masterDefaultValues.get(attr)) > 1:#assert that value
			log.debug("%s"% attributes.doGetAttr(Puppet.masterNull.mNode,attr))
			assert attributes.doGetAttr(Puppet.masterNull.mNode,attr) == masterDefaultValues.get(attr)[1]
	    except Exception,error:raise StandardError,"[masterNull]{%s}"%error
	
    
	    try:#Initializing only mode to compare
		#----------------------------------------------------------
	
		self.PuppetIO = cgmPM.cgmPuppet(name = 'Kermit',initializeOnly=True)#Initializatoin only method of the the same puppet         
		Puppet2 = self.PuppetIO
	
		for attr in puppetDefaultValues.keys():
		    assert Puppet2.hasAttr(attr),("'%s' missing attr:%s"%(self.PuppetIO.mNode,attr))
		    assert attributes.doGetAttr(Puppet2.mNode,attr) == attributes.doGetAttr(Puppet.mNode,attr)
	
		for attr in masterDefaultValues.keys():
		    assert Puppet2.masterNull.hasAttr(attr),("'%s' missing attr:%s"%(self.PuppetIO.mNode,attr))
		    assert attributes.doGetAttr(Puppet2.masterNull.mNode,attr) == attributes.doGetAttr(Puppet.masterNull.mNode,attr)
	    except Exception,error:raise StandardError,"[Fast initialize]{%s}"%error
	
	    try:#Assertions on the masterNull
		#----------------------------------------------------------
		log.info('>'*3 + " Assertions on the masterNull on IOPuppet...")
		assert Puppet.masterNull.getShortName() == Puppet2.masterNull.getShortName()
		assert Puppet.masterNull.puppet == Puppet2.masterNull.puppet
		
		try:
		    Puppet2.__verify__()
		except StandardError,error:
			log.error("test_cgmPuppet>>Puppet2.__verify() Failed!  %s"%error)
			raise StandardError,error 
	    except Exception,error:raise StandardError,"[compare]{%s}"%error
                       	    
	def _cgmModuleTests_(self):
	    try:
		self.Puppet
	    except:
		self.Puppet = cgmPM.cgmPuppet(name = 'Kermit')
	    Puppet = self.Puppet
    
	    try:
		Module1 = cgmPM.cgmModule(name = 'arm',position = 'front',direction = 'right', handles = 3)
		Module1IO = cgmPM.cgmModule(Module1.mNode,initializeOnly = True) #Should equal that of the reg process
	    except Exception,error:raise StandardError,"[creation]{%s}"%error
	    
	    try:#Assertions on the module null
		#----------------------------------------------------------
		log.info('>'*3 + " Assertions on the module null...")    
		assert Module1.cgmType == 'module',str(Module1.cgmType)
		assert Module1.mClass == 'cgmModule'
		assert Module1.cgmName == 'arm'
		assert Module1.cgmPosition == 'front'
		assert Module1.cgmDirection == 'right'
	
		assert Module1.cgmType == Module1IO.cgmType
		assert Module1.mClass == Module1IO.mClass
		assert Module1.cgmType == Module1IO.cgmType
		assert Module1.cgmPosition == Module1IO.cgmPosition
		assert Module1.cgmDirection == Module1IO.cgmDirection       
	    except Exception,error:raise StandardError,"[Module null and compare]{%s}"%error
    
	    try:#Assertions on the rig null
		#----------------------------------------------------------
		log.info('>'*3 + " Assertions on the rig null...")   
		assert Module1.i_rigNull.hasAttr('cgmType')
		log.debug(Module1.i_rigNull.cgmType)
	
		assert Module1.i_rigNull.cgmType == 'rigNull','%s'%Module1.i_rigNull.cgmType
		assert Module1.i_rigNull.ik == False
		assert Module1.i_rigNull.fk == False
	
		assert Module1.i_rigNull.mNode == Module1.rigNull.mNode
	    except Exception,error:raise StandardError,"[rigNull and compare]{%s}"%error
    
	    try:#Assertions on the template null
		#----------------------------------------------------------
		log.info('>'*3 + " Assertions on the template null...")   
		assert Module1.i_rigNull.hasAttr('cgmType')
		log.debug(Module1.i_templateNull.cgmType)
		assert Module1.i_templateNull.mNode == Module1.templateNull.mNode
		assert Module1.i_templateNull.handles == 3,'%s'%Module1.i_templateNull.handles
	    except Exception,error:raise StandardError,"[templateNull]{%s}"%error
    
	    try:#Assertions on the coreNames bufferNode
		#----------------------------------------------------------
		log.info('>'*3 + " Assertions on the coreNames bufferNode...") 
		assert Module1.coreNames.mClass == 'cgmModuleBufferNode'
	    except Exception,error:raise StandardError,"[coreNames]{%s}"%error
    
	    try:#Connect Modules
		#----------------------------------------------------------
		log.info('>'*3 + " Connect Modules...")   
		self.Puppet.connectModule(Module1)
		
		assert Module1.modulePuppet.mNode == self.Puppet.mNode
		assert Module1.getMessage('modulePuppet') == [self.Puppet.mNode],"'%s' != '%s'"%(Module1.getMessage('modulePuppet'),self.Puppet.mNode)
	    except Exception,error:raise StandardError,"[connect]{%s}"%error
	     
	
	    try:
		log.info('>'*3 + " Creating Limb module with moduleParent Flag...")           
		Module2 = cgmPM.cgmLimb(name = 'hand',moduleParent = Module1)
		#assert Module2.getMessage('moduleParent')[0] == Module1.mNode #connection via flag isn't working yet
	    except Exception,error:raise StandardError,"[Creating with moduleParent]{%s}"%error
    
	    try:
		log.info("Connecting '%s' to '%s'"%(Module2.getShortName(),Module1.getShortName()))
		log.info(Module1.mClass)
		log.info(Module2.mClass)        
		Module2.doSetParentModule(Module1)
		assert Module2.getMessage('moduleParent') == [Module1.mNode]
	    except Exception,error:raise StandardError,"[doSetParentModule]{%s}"%error    
    return fncWrap(*args, **kws).go()

def cgmPuppet_tests(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'cgmPuppet_tests'	
	    self._b_autoProgressBar = 1
	    self._b_reportTimes = 1
	        
	    self.__dataBind__(*args, **kws)
	    self.l_funcSteps = [{'step':'cgmPuppet calls','call':self._puppetTests_},
	                        {'step':'cgmModule calls','call':self._cgmModuleTests_},
	                        ]
	
	def _puppetTests_(self):    
	    self.Puppet = cgmPM.cgmPuppet(name = 'Kermit')
	    Puppet = self.Puppet
    
	    try:#Assertions on the network null
		#----------------------------------------------------------
		assert mc.nodeType(Puppet.mNode) == 'network'
	
		puppetDefaultValues = {'cgmName':['string','Kermit'],
		                       'cgmType':['string','puppetNetwork'],
		                       'mClass':['string','cgmPuppet'],
		                       'version':['double',1.0],
		                       'masterNull':['message'],
		                       'font':['string','Arial'],
		                       'axisAim':['enum',2],
		                       'axisUp':['enum',1],
		                       'axisOut':['enum',0]}                                   
	
		for attr in puppetDefaultValues.keys():
		    assert Puppet.hasAttr(attr),("'%s' missing attr:%s"%(self.Puppet.mNode,attr))
		    assert mc.getAttr('%s.%s'%(Puppet.mNode,attr), type=True) == puppetDefaultValues.get(attr)[0], "Type is '%s'"%(mc.getAttr('%s.%s' %(Puppet.mNode,attr), type=True))
		    if len(puppetDefaultValues.get(attr)) > 1:#assert that value
			log.debug("%s"% attributes.doGetAttr(Puppet.mNode,attr))                
			assert attributes.doGetAttr(Puppet.mNode,attr) == puppetDefaultValues.get(attr)[1],"%s is not %s"%(attributes.doGetAttr(Puppet.mNode,attr),puppetDefaultValues.get(attr)[1])
	    except Exception,error:raise StandardError,"[network null]{%s}"%error
    
	    try:#Assertions on the masterNull
		#----------------------------------------------------------
		#log.info('>'*3 + " Assertions on the masterNull...")
		assert Puppet.masterNull.getShortName() == Puppet.cgmName
		assert Puppet.masterNull.puppet.mNode == Puppet.mNode,Puppet.masterNull.puppet
		
	
		masterDefaultValues = {'cgmType':['string','ignore'],
		                       'cgmModuleType':['string','master']}       
	
		for attr in masterDefaultValues.keys():
		    assert Puppet.masterNull.hasAttr(attr),("'%s' missing attr:%s"%(Puppet.masterNull.mNode,attr))
		    assert mc.getAttr('%s.%s'%(Puppet.masterNull.mNode,attr), type=True) == masterDefaultValues.get(attr)[0], "Type is '%s'"%(mc.getAttr('%s.%s' %(Puppet.masterNull.mNode,attr), type=True))
		    if len(masterDefaultValues.get(attr)) > 1:#assert that value
			log.debug("%s"% attributes.doGetAttr(Puppet.masterNull.mNode,attr))
			assert attributes.doGetAttr(Puppet.masterNull.mNode,attr) == masterDefaultValues.get(attr)[1]
	    except Exception,error:raise StandardError,"[masterNull]{%s}"%error
	
    
	    try:#Initializing only mode to compare
		#----------------------------------------------------------
		self.PuppetIO = cgmPM.cgmPuppet(name = 'Kermit',initializeOnly=True)#Initializatoin only method of the the same puppet         
		Puppet2 = self.PuppetIO
	
		for attr in puppetDefaultValues.keys():
		    assert Puppet2.hasAttr(attr),("'%s' missing attr:%s"%(self.PuppetIO.mNode,attr))
		    assert attributes.doGetAttr(Puppet2.mNode,attr) == attributes.doGetAttr(Puppet.mNode,attr)
	
		for attr in masterDefaultValues.keys():
		    assert Puppet2.masterNull.hasAttr(attr),("'%s' missing attr:%s"%(self.PuppetIO.mNode,attr))
		    assert attributes.doGetAttr(Puppet2.masterNull.mNode,attr) == attributes.doGetAttr(Puppet.masterNull.mNode,attr)
	    except Exception,error:raise StandardError,"[Fast initialize]{%s}"%error
	
	    try:#Assertions on the masterNull
		#----------------------------------------------------------
		#log.info('>'*3 + " Assertions on the masterNull on IOPuppet...")
		assert Puppet.masterNull.getShortName() == Puppet2.masterNull.getShortName()
		assert Puppet.masterNull.puppet == Puppet2.masterNull.puppet
		
		try:
		    Puppet2.__verify__()
		except StandardError,error:
			log.error("test_cgmPuppet>>Puppet2.__verify() Failed!  %s"%error)
			raise StandardError,error 
	    except Exception,error:raise StandardError,"[compare]{%s}"%error
                       	    
	def _cgmModuleTests_(self):
	    try:
		self.Puppet
	    except:
		self.Puppet = cgmPM.cgmPuppet(name = 'Kermit')
	    Puppet = self.Puppet
    
	    try:
		Module1 = cgmPM.cgmModule(name = 'arm',position = 'front',direction = 'right', handles = 3)
		Module1IO = cgmPM.cgmModule(Module1.mNode,initializeOnly = True) #Should equal that of the reg process
	    except Exception,error:raise StandardError,"[creation]{%s}"%error
	    
	    try:#Assertions on the module null
		#----------------------------------------------------------
		#log.info('>'*3 + " Assertions on the module null...")    
		assert Module1.cgmType == 'module',str(Module1.cgmType)
		assert Module1.mClass == 'cgmModule'
		assert Module1.cgmName == 'arm'
		assert Module1.cgmPosition == 'front'
		assert Module1.cgmDirection == 'right'
	
		assert Module1.cgmType == Module1IO.cgmType
		assert Module1.mClass == Module1IO.mClass
		assert Module1.cgmType == Module1IO.cgmType
		assert Module1.cgmPosition == Module1IO.cgmPosition
		assert Module1.cgmDirection == Module1IO.cgmDirection       
	    except Exception,error:raise StandardError,"[Module null and compare]{%s}"%error
    
	    try:#Assertions on the rig null
		#----------------------------------------------------------
		#log.info('>'*3 + " Assertions on the rig null...")   
		assert Module1.i_rigNull.hasAttr('cgmType')
		log.debug(Module1.i_rigNull.cgmType)
	
		assert Module1.i_rigNull.cgmType == 'rigNull','%s'%Module1.i_rigNull.cgmType
		assert Module1.i_rigNull.ik == False
		assert Module1.i_rigNull.fk == False
	
		assert Module1.i_rigNull.mNode == Module1.rigNull.mNode
	    except Exception,error:raise StandardError,"[rigNull and compare]{%s}"%error
    
	    try:#Assertions on the template null
		#----------------------------------------------------------
		log.info('>'*3 + " Assertions on the template null...")   
		assert Module1.i_rigNull.hasAttr('cgmType')
		log.debug(Module1.i_templateNull.cgmType)
		assert Module1.i_templateNull.mNode == Module1.templateNull.mNode
		assert Module1.i_templateNull.handles == 3,'%s'%Module1.i_templateNull.handles
	    except Exception,error:raise StandardError,"[templateNull]{%s}"%error
    
	    try:#Assertions on the coreNames bufferNode
		#----------------------------------------------------------
		log.info('>'*3 + " Assertions on the coreNames bufferNode...") 
		assert Module1.coreNames.mClass == 'cgmModuleBufferNode'
	    except Exception,error:raise StandardError,"[coreNames]{%s}"%error
    
	    try:#Connect Modules
		#----------------------------------------------------------
		log.info('>'*3 + " Connect Modules...")   
		self.Puppet.connectModule(Module1)
		
		assert Module1.modulePuppet.mNode == self.Puppet.mNode
		assert Module1.getMessage('modulePuppet') == [self.Puppet.mNode],"'%s' != '%s'"%(Module1.getMessage('modulePuppet'),self.Puppet.mNode)
	    except Exception,error:raise StandardError,"[connect]{%s}"%error
	     
	
	    try:
		log.info('>'*3 + " Creating Limb module with moduleParent Flag...")           
		Module2 = cgmPM.cgmLimb(name = 'hand',moduleParent = Module1)
		#assert Module2.getMessage('moduleParent')[0] == Module1.mNode #connection via flag isn't working yet
	    except Exception,error:raise StandardError,"[Creating with moduleParent]{%s}"%error
    
	    try:
		log.info("Connecting '%s' to '%s'"%(Module2.getShortName(),Module1.getShortName()))
		log.info(Module1.mClass)
		log.info(Module2.mClass)        
		Module2.doSetParentModule(Module1)
		assert Module2.getMessage('moduleParent') == [Module1.mNode]
	    except Exception,error:raise StandardError,"[doSetParentModule]{%s}"%error
	    
    return fncWrap(*args, **kws).go()
