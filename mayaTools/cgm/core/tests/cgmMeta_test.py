#=========================================================================      
#=========================================================================         
from Red9.core import Red9_Meta as r9Meta
reload(r9Meta)
#from Red9.core.Red9_Meta import *
r9Meta.registerMClassInheritanceMapping()    
#========================================================================
import random
import re
import copy
import time
import logging

from cgm.lib import (distance,attributes)

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from cgm.core import cgmMeta
reload(cgmMeta)
#from cgm.core.cgmMeta import *

from cgm.core.rigger import cgmPuppet
reload(cgmPuppet)

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
        self.Morpheus = cgmPuppet.cgmPuppet(name = 'Morpheus')
        
class cgmMeta_Test():
    def __init__(self):
        function = 'cgmMeta_Test'        
        log.info(">"*20  + "  Testing '%s' "%function + "<"*20 )         
        start = time.clock()
        self.setup()
        self.test_cgmAttr()
        #self.test_attributeHandling()
        #self.test_messageAttrHandling() #On hold while deciding how to proceed with Mark
        #self.test_cgmNode()
        #self.test_cgmObject()
        #self.test_cgmObjectSet()
        #self.test_cgmOptionVar()
        #self.test_cgmPuppet() #Puppet test
        #self.test_cgmModule()
        
        #self.MetaInstance.select()
        
        log.info(">"*10  + '   cgmMeta_Test time =  %0.3f seconds  ' % (time.clock()-start) + '<'*10)    
    
    def setup(self):
        '''
        Tests proper creation of objects from flag calls
        '''        
        mc.file(new=True,f=True)
        function = 'setup'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        #Make a few objects
        #==============              
  
        #Test name and node argument passing
        #==============      
        log.info("Testing no arguments passed")
        self.MetaInstance = cgmMeta.cgmMeta()
        assert mc.objExists(self.MetaInstance.mNode)        
        
        self.test_functionCalls()
        #Initial instance deleted at end of function call
        
        log.info('>'*3 + " Testing name 'Hogwarts' being passed")
        self.MetaInstance = cgmMeta.cgmMeta(name = 'Hogwarts')
        assert mc.objExists(self.MetaInstance.mNode)        
        assert self.MetaInstance.getShortName() == 'Hogwarts'     
        
        log.info('>'*3 + " Pass node, no name...")        
        self.MetaInstance = cgmMeta.cgmMeta(node = 'Hogwarts')
        assert mc.objExists(self.MetaInstance.mNode)                
        assert self.MetaInstance.getShortName() == 'Hogwarts'     
        
        log.info('>'*3 + " Testing existing 'Hogwarts' node, new 'cgmTransform' name")
        self.MetaInstance = cgmMeta.cgmMeta(node = 'Hogwarts', name = 'cgmTransform')
        assert mc.objExists(self.MetaInstance.mNode)
        assert self.MetaInstance.getShortName() == 'cgmTransform'
        
        log.info(">"*5 + "  Node creation test complete")         
        log.info('Simple name logic =  %0.3f' % (time.clock()-start))
        
        #Create nodeType
        #============== 
        #Need to create a Node and an object for separate tests
        
        self.MetaNode = cgmMeta.cgmMeta(name = 'cgmNetwork', nodeType = 'network')
        assert mc.nodeType(self.MetaNode.mNode)=='network'
        
        self.MetaObject = cgmMeta.cgmMeta(name = 'cgmTransform',nodeType = 'transform')
        assert mc.nodeType(self.MetaObject.mNode)=='transform'
        
        self.ObjectSet = cgmMeta.cgmMeta(name = 'cgmObjectSet',nodeType = 'objectSet')
        assert mc.nodeType(self.ObjectSet.mNode)=='objectSet'
        
        #Create Test Objects and initialize
        #============== 
        nurbsCubeCatch = mc.nurbsCube()
        polyCubeCatch = mc.polyCube()  
        
        self.pCube = cgmMeta.cgmMeta(polyCubeCatch[0],name = 'pCube')
        self.nCube = cgmMeta.cgmMeta(nurbsCubeCatch[0],name = 'nCube')
        
        self.setup = True
        
        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)  
        
    def test_cgmAttr(self):
        '''
        Modified from Mark Jackson's testing for Red9
        This tests the standard attribute handing in the MetaClass.__setattr__ 
        '''
        
        self.cgmAttrNull = cgmMeta.cgmObject(name = 'cgmAttrNull',nodeType = 'transform')

        function = 'test_cgmAttr'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        node=self.cgmAttrNull
        
        #String test
        #---------------- 
        log.info('>'*3 + " String test...")
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
        
        #Int test
        #---------------- 
        log.info('>'*3 + " Int test and conversion to float...")
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
        
        #Float test
        #---------------- 
        log.info('>'*3 + " Float and softMin/softMax...")
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

        
        #Message test
        #---------------- 
        log.info('>'*3 + " Message test...")
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
        
        #Enum test
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
        
        #Copying test
        #----------------     
        #Transferring test
        #----------------    
        #NameFlags
        #----------------         
        
        node.select()
        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)    
        
    def test_attributeHandling(self):
        '''
        Modified from Mark Jackson's testing for Red9
        This tests the standard attribute handing in the MetaClass.__setattr__ 
        '''
        if not self.MetaInstance:
            self.MetaInstance = cgmMeta.cgmMeta()
            
        function = 'test_attributeHandling'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        node=self.MetaInstance
        
        #standard attribute handling
        node.addAttr('stringTest', "this_is_a_string")  #create a string attribute
        node.addAttr('fltTest', 1.333)        #create a float attribute
        node.addAttr('intTest', 3)            #create a int attribute
        node.addAttr('boolTest', False)       #create a bool attribute
        node.addAttr('enumTest',enum='A:B:D:E:F', attrType ='enum',value = 1) #create an enum attribute
        node.addAttr('vecTest', [0,0,0], attrType ='double3') #create a double3

        #testAttrs with no value flags but attr flag to use default 
        node.addAttr('stringTestNoValue', attrType = 'string')  #create a string attribute
        node.addAttr('fltTestNoValue', attrType = 'float')  #create a string attribute
        node.addAttr('intTestNoValue', attrType = 'int')  #create a string attribute
        node.addAttr('boolTestNoValue', attrType = 'bool')  #create a string attribute
        node.addAttr('enumTestNoValue', attrType = 'enum')  #create a string attribute
        #node.addAttr('vecTestNoValue', attrType ='double3') #create a double3
        
        
        #create a string attr with JSON serialized data
        testDict={'jsonFloat':1.05,'jsonInt':3,'jsonString':'string says hello','jsonBool':True}
        node.addAttr('jsonTest',testDict,attrType = 'string')

        #test the hasAttr call in the baseClass
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
        
        
        #test the actual Maya node attributes
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
        
        
        
        #now check the MetaClass __getattribute__ and __setattr__ calls
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
        
        
        #json string handlers
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
        
        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)                         
        
    def test_messageAttrHandling(self):
        '''
        test the messageLink handling in the __setattr__ block
        '''
        function = 'test_functionCalls'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        
        start = time.clock()   
        
        #if not self.MetaInstance:
            #self.MetaInstance = cgmMeta.cgmMeta() 
            
        node=r9Meta.MetaClass()
                
        #make sure we collect LONG names for these as all wrappers deal with longName
        cube1=mc.ls(mc.polyCube()[0],l=True)[0]
        cube2=mc.ls(mc.polyCube()[0],l=True)[0]
        cube3=mc.ls(mc.polyCube()[0],l=True)[0]
        cube4=mc.ls(mc.polyCube()[0],l=True)[0]
        cube5=mc.ls(mc.polyCube()[0],l=True)[0]
        cube6=mc.ls(mc.polyCube()[0],l=True)[0]
 
        node.addAttr('msgMultiTest', value=[cube1,cube2,cube3], attrType='message')   #multi Message attr
        node.addAttr('msgSingleTest', value=cube3, attrType='messageSimple')    #non-multi message attr
        node.addAttr('msgSingleTest2', value=cube3, attrType='messageSimple')    #non-multi message attr
        
        assert node.hasAttr('msgMultiTest')
        assert node.hasAttr('msgSingleTest')
        assert node.hasAttr('msgSingleTest2')
        
        assert mc.getAttr('%s.msgMultiTest' % node.mNode, type=True)=='message'
        assert mc.getAttr('%s.msgSingleTest' % node.mNode, type=True)=='message'
        assert mc.attributeQuery('msgMultiTest',node=node.mNode, multi=True)==True
        assert mc.attributeQuery('msgSingleTest',node=node.mNode, multi=True)==False
        
        #NOTE : cmds returns shortName, but all MetaClass attrs are always longName
        assert mc.listConnections('%s.msgSingleTest' % node.mNode)==[cube1],"%s"%mc.listConnections('%s.msgSingleTest' % node.mNode)
        assert mc.listConnections('%s.msgSingleTest2' % node.mNode)==[cube2],"%s"%mc.listConnections('%s.msgSingleTest2' % node.mNode)
        assert sorted(mc.listConnections('%s.msgMultiTest' % node.mNode))==[cube1,cube2,cube3]
   
        assert sorted(node.msgMultiTest)==[cube1,cube2]
        assert node.msgSingleTest==[cube3]
        
        #test the reconnect handler via the setAttr
        node.msgMultiTest=[cube5,cube6]
        assert sorted(node.msgMultiTest)==[cube5,cube6]
        assert sorted(mc.listConnections('%s.msgMultiTest' % node.mNode))==['pCube5','pCube6']
        
        node.msgMultiTest=[cube1,cube2,cube4,cube6]
        assert sorted(node.msgMultiTest)==[cube1,cube2,cube4,cube6]
        assert sorted(mc.listConnections('%s.msgMultiTest' % node.mNode))==['pCube1','pCube2','pCube4','pCube6']
        
        node.msgSingleTest=cube4
        assert node.msgSingleTest==[cube4] 
        assert mc.listConnections('%s.msgSingleTest' % node.mNode)==['pCube4'] #cmds returns a list
        node.msgSingleTest=cube3
        assert node.msgSingleTest==[cube3] 
        assert mc.listConnections('%s.msgSingleTest' % node.mNode)==['pCube3'] #cmds returns a list
        
        
        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)                         
        
        
    def test_functionCalls(self):
        function = 'test_functionCalls'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()        
      
        #select
        name = self.MetaInstance.getShortName()
        assert mc.objExists(name)
        
        mc.select(cl=True)
        self.MetaInstance.select()
        assert mc.ls(sl=True)[0]== name
        
        #rename
        self.MetaInstance.rename('FooBar')
        assert self.MetaInstance.getShortName() =='FooBar',"mNode is '%s'"%self.MetaInstance.mNode
        self.MetaInstance.select()
        assert mc.ls(sl=True)[0]=='FooBar'
        
        #convert
        #new=self.MetaInstance.convertMClassType('MetaRig')
        #assert isinstance(new,r9Meta.MetaRig)
        #assert self.MetaInstance.mClass=='MetaRig'
        
        #delete
        self.MetaInstance.delete()
        assert not mc.objExists(name)
        
        log.info(">"*5  +"Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)                         

        
    def test_cgmNode(self):
        function = 'test_cgmNode'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        if not self.MetaNode:
            self.MetaNode = cgmMeta.cgmMeta(name = 'cgmNode',nodeType = 'network')
            
        #Assert some info
        #----------------------------------------------------------   
        assert self.MetaNode.referencePrefix is not None
        
        #cgmNode functions
        #---------------------------------------------------------- 
        self.MetaNode.doName()
        assert self.MetaNode.hasAttr('cgmName') is True
        
        self.MetaObject.doCopyNameTagsFromObject(self.MetaNode.mNode)
        assert self.MetaObject.cgmName == self.MetaNode.cgmName,"CGM Name copying faild"
        
        self.MetaNode.doStore('stored',self.nCube.mNode)
        assert self.MetaNode.stored[0] == self.nCube.mNode,"'%s' is stored"%self.MetaNode.stored
        
        self.MetaNode.doRemove('stored')
        assert self.MetaNode.hasAttr('stored') is False
        
        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)                         
    
    def test_cgmObject(self):
        function = 'test_cgmObject'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        #Assert some info
        #---------------------------------------------------------- 
        
        #Let's move our test objects around and and see what we get
        #----------------------------------------------------------  
        self.MetaObject.rotateOrder = 0 #To have  base to check from
        
        #Randomly move stuff
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
        
        #Parent and assert relationship
        log.info('>'*3 + " Testing parenting...")        
        
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
        
        
        #Roate order match
        log.info('>'*3 + " Testing rotate order match function")        
        self.MetaObject.doCopyRotateOrder(self.pCube.mNode)
        assert self.MetaObject.rotateOrder == self.pCube.rotateOrder,"Copy rotate order failed"
        
        self.MetaObject.doCopyRotateOrder = self.nCube.rotateOrder #Just set it
        assert self.MetaObject.doCopyRotateOrder == self.nCube.rotateOrder
        
        #Group
        log.info("Testing grouping function")
        previousPos = distance.returnWorldSpacePosition(self.pCube.mNode)
        self.pCube.doGroup(True)
        #assert previousPos == distance.returnWorldSpacePosition(self.pCube.mNode),"previous %s != %s"%(previousPos,distance.returnWorldSpacePosition(self.pCube.mNode))
        assert self.pCube.getParent() != self.nCube.mNode,"nCube shouldn't be the parent"
        
        #setDrawingOverrideSettings
        log.info('>'*3 + " Testing drawing override functions")   
        self.pCube.overrideEnabled = 1     
        TestDict = {'overrideColor':20,'overrideVisibility':1}
        self.pCube.setDrawingOverrideSettings(TestDict, pushToShapes=True)
        
        assert self.pCube.overrideEnabled == 1
        assert self.pCube.overrideColor == 20
        assert self.pCube.overrideVisibility == 1
        
        for shape in self.pCube.getShapes():
            for a in TestDict.keys():
                assert attributes.doGetAttr(shape,a) == TestDict[a],"'%s.%s' is not %s"%(shape,a,TestDict[a])
            
        #Copy pivot
        log.info("Testing copy pivot function")        
        self.MetaObject.doCopyPivot(self.pCube.mNode)
       
        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)                         

    def test_cgmObjectSet(self):
        function = 'test_cgmObjectSet'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        self.ObjectSet = cgmMeta.cgmMeta(name = 'cgmObjectAnimationSet',nodeType = 'objectSet',setType = 'animation', qssState = True)
        self.MayaDefaultSet = cgmMeta.cgmMeta(node = 'defaultObjectSet')   
        
        #from cgm.core.cgmMeta import *
        self.ObjectSet2 = cgmMeta.cgmObjectSet(setName = 'cgmObjectAnimationSet2',value = self.ObjectSet.value )
        #Initialize another set with a value on call
        assert self.ObjectSet2.value == self.ObjectSet.value
        del self.ObjectSet2.value        
        
        #Assert some info
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
        
        #Adding and removing
        #-------------------
        log.info('>'*3 + " Adding and removing by property...")
        assert not self.ObjectSet.getList()
        
        self.ObjectSet.value = [self.pCube.mNode, self.nCube.mNode,(self.pCube.mNode+'.tx')] # Add an attribute
        
        assert self.ObjectSet.doesContain(self.pCube.mNode)
        assert self.ObjectSet.doesContain(self.nCube.mNode)
        assert '%s.translateX'%self.pCube.getShortName() in self.ObjectSet.getList(),"%s"%self.ObjectSet.getList()
        
        self.ObjectSet.value = False
        assert not self.ObjectSet.value

        #Adding and removing
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

        #Selecting/purging/copying
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
        self.ObjectSetCopy = cgmMeta.cgmMeta(catch) #Initialize copy
        assert self.ObjectSet.getList() == self.ObjectSetCopy.getList(),"Sets don't match"
        assert self.ObjectSet.objectSetType == self.ObjectSetCopy.objectSetType,"Object Set types don't match"
        assert self.ObjectSet.qssState == self.ObjectSetCopy.qssState,"qssStates don't match"
        
        #Purge
        self.ObjectSetCopy.purge()
        assert not self.ObjectSetCopy.getList(),"Dup set failed to purge"
        
        #Keying, deleting keys, reseting
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

        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)                         

    def test_cgmOptionVar(self):
        function = 'test_cgmOptionVar'
        log.info("-"*20  + "  test_cgmOptionVar '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        #Purge the optionVars
        for var in 'cgmVar_intTest','cgmVar_stringTest','cgmVar_floatTest':
            if mc.optionVar(exists = var):
                mc.optionVar(remove = var)

        # Testing creation/conversion of ine optionVar
        #-------------------------
        log.info('>'*3 + " Testing creation/conversion of ine optionVar...")   
        
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
        
        
        # String varType test and initValue Test
        #-------------------------
        log.info('>'*3 + " String varType test and initValue Test...")   
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
        log.info(self.OptionVarString.value)
        assert len(self.OptionVarString.value) == 2,"Len is %s"%len(self.OptionVarString.value)
        assert type(self.OptionVarString.value) is list,"Type is %s"%type(self.OptionVarString.value)
        
        self.OptionVarString.value = (self.nCube.mNode,self.pCube.mNode,'test3')#set via tuple
        log.info(self.OptionVarString.value)
        assert len(self.OptionVarString.value) == 3,"Len is %s"%len(self.OptionVarString.value)
        assert type(self.OptionVarString.value) is list,"Type is %s"%type(self.OptionVarString.value)
        
        # Appending to string, removing, select and exist check testing
        #-------------------------
        log.info('>'*3 + " Appending to string, removing, select and exist check testing...")   
        
        self.OptionVarString.append('test4')# append a string
        assert self.OptionVarString.value[3] == 'test4'
        
        self.OptionVarString.append(3)# append a number as a string
        assert self.OptionVarString.value[4] == '3'
        
        self.OptionVarString.append(3.0)# append a float as a string
        assert self.OptionVarString.value[5] == '3.0'
        
        self.OptionVarString.remove('3.0')# remove an item
        log.info(self.OptionVarString.value)        
        assert len(self.OptionVarString.value) == 5,"Len is %s"%len(self.OptionVarString.value)
        
        self.OptionVarString.select() # Try to select our stuff
        len(mc.ls(sl=True)) == 2
        self.OptionVarString.existCheck()#Remove maya objects that don't exist
        log.info(self.OptionVarString.value)        
        len(self.OptionVarString.value) == 2
        
        # Float testing and translation testing
        #-------------------------
        log.info('>'*3 + " Float testing and translation testing...")   
        
        self.OptionVarFloat = cgmMeta.cgmOptionVar('cgmVar_floatTest',value = 1.0,varType = 'float')#Float type
        
        assert self.OptionVarFloat.varType == 'float'
        assert self.OptionVarFloat.value == 1
        
        self.OptionVarFloat.append(2)
        log.info(self.OptionVarFloat.value)                
        assert self.OptionVarFloat.value[1] == 2.0
        
        self.OptionVarFloat.varType = 'int' #Convert to int
        log.info(self.OptionVarFloat.value)                
        
        
        # Delete checking
        #-------------------------
        log.info('>'*3 + " Delete checking...") 
        
        #Because option vars are not local. We need to delete them all...
        del self.OptionVarInt.value #Deletion from property
        assert not mc.optionVar(exists = 'cgmVar_intTest')
        
        self.OptionVarString.purge() #Deletion via purge
        assert not mc.optionVar(exists = 'cgmVar_stringTest')
        
        # Float varType test and initValue Test
        #-------------------------
        log.info('>'*3 + " String varType test and initValue Test...")   
        self.OptionVarString = cgmMeta.cgmOptionVar('cgmVar_stringTest', defaultValue='batman')#String type
        

        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)                         

    def test_cgmPuppet(self):
        function = 'test_cgmPuppet'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        self.Puppet = cgmPuppet.cgmPuppet(name = 'Kermit')
        Puppet = self.Puppet
        
        #Assertions on the network null
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the network null...")    
        assert mc.nodeType(Puppet.mNode) == 'network'
        
        puppetDefaultValues = {'cgmName':['string','Kermit'],
                               'cgmType':['string','puppetNetwork'],
                               'mClass':['string','cgmPuppet'],
                               'version':['double',1.0],
                               'masterNull':['message'],
                               'settings':['message'],
                               'geo':['message'],
                               'parts':['message']}
        
        for attr in puppetDefaultValues.keys():
            assert Puppet.hasAttr(attr),("'%s' missing attr:%s"%(self.Puppet.mNode,attr))
            assert mc.getAttr('%s.%s'%(Puppet.mNode,attr), type=True) == puppetDefaultValues.get(attr)[0], "Type is '%s'"%(mc.getAttr('%s.%s' %(Puppet.mNode,attr), type=True))
            if len(puppetDefaultValues.get(attr)) > 1:#assert that value
                log.debug("%s"% attributes.doGetAttr(Puppet.mNode,attr))                
                assert attributes.doGetAttr(Puppet.mNode,attr) == puppetDefaultValues.get(attr)[1]
                
                
        #Assertions on the settings null
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the settings null...")
        assert mc.objExists(Puppet.i_settings.mNode),"No Settings object found"
        assert mc.nodeType(Puppet.i_settings.mNode) == 'network'
        
        
        settingsDefaultValues = {'cgmName':['string','Kermit'],
                                 'cgmType':['string','info'],
                                 'cgmTypeModifier':['string','settings'],
                                 'font':['string','Arial'],
                                 'puppetType':['long',0],
                                 'axisAim':['enum',2],
                                 'axisUp':['enum',1],
                                 'axisOut':['enum',0]}        
        
        for attr in settingsDefaultValues.keys():
            assert Puppet.i_settings.hasAttr(attr),("'%s' missing attr:%s"%(Puppet.i_settings.mNode,attr))
            assert mc.getAttr('%s.%s'%(Puppet.i_settings.mNode,attr), type=True) == settingsDefaultValues.get(attr)[0], "Type is '%s'"%(mc.getAttr('%s.%s' %(Puppet.i_settings.mNode,attr), type=True))
            if len(settingsDefaultValues.get(attr)) > 1:#assert that value
                log.debug("%s"% attributes.doGetAttr(Puppet.i_settings.mNode,attr))
                assert attributes.doGetAttr(Puppet.i_settings.mNode,attr) == settingsDefaultValues.get(attr)[1]
        
                
        #Assertions on the masterNull
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the masterNull...")
        assert Puppet.i_masterNull.getShortName() == Puppet.cgmName
        assert Puppet.i_masterNull.puppet[0] == Puppet.mNode
        
        masterDefaultValues = {'cgmType':['string','ignore'],
                               'cgmModuleType':['string','master']}       
        
        for attr in masterDefaultValues.keys():
            assert Puppet.i_masterNull.hasAttr(attr),("'%s' missing attr:%s"%(Puppet.i_masterNull.mNode,attr))
            assert mc.getAttr('%s.%s'%(Puppet.i_masterNull.mNode,attr), type=True) == masterDefaultValues.get(attr)[0], "Type is '%s'"%(mc.getAttr('%s.%s' %(Puppet.i_masterNull.mNode,attr), type=True))
            if len(masterDefaultValues.get(attr)) > 1:#assert that value
                log.debug("%s"% attributes.doGetAttr(Puppet.i_masterNull.mNode,attr))
                assert attributes.doGetAttr(Puppet.i_masterNull.mNode,attr) == masterDefaultValues.get(attr)[1]
        

        #Initializing only mode to compare
        #----------------------------------------------------------
        log.info('>'*3 + " Initializing only mode to compare...")
        
        self.PuppetIO = cgmPuppet.cgmPuppet(name = 'Kermit',initializeOnly=True)#Initializatoin only method of the the same puppet         
        Puppet2 = self.PuppetIO
        
        for attr in puppetDefaultValues.keys():
            assert Puppet2.hasAttr(attr),("'%s' missing attr:%s"%(self.PuppetIO.mNode,attr))
            assert attributes.doGetAttr(Puppet2.mNode,attr) == attributes.doGetAttr(Puppet.mNode,attr)
        
        for attr in settingsDefaultValues.keys():
            assert Puppet2.i_settings.hasAttr(attr),("'%s' missing attr:%s"%(Puppet2.mNode,attr))
            assert attributes.doGetAttr(Puppet2.i_settings.mNode,attr) == attributes.doGetAttr(Puppet.i_settings.mNode,attr)
        for attr in masterDefaultValues.keys():
            assert Puppet2.i_masterNull.hasAttr(attr),("'%s' missing attr:%s"%(self.PuppetIO.mNode,attr))
            assert attributes.doGetAttr(Puppet2.i_masterNull.mNode,attr) == attributes.doGetAttr(Puppet.i_masterNull.mNode,attr)
                 
                
        #Assertions on the settings null
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the settings null  on IOPuppet...")
        assert Puppet.i_settings.mNode == Puppet2.i_settings.mNode

                
        #Assertions on the masterNull
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the masterNull on IOPuppet...")
        assert Puppet.i_masterNull.getShortName() == Puppet2.i_masterNull.getShortName()
        assert Puppet.i_masterNull.puppet[0] == Puppet2.i_masterNull.puppet[0]
        

        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)                         
    
    def test_cgmModule(self):
        function = 'test_cgmPuppet'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        if not self.Puppet:
            self.Puppet = cgmPuppet.cgmPuppet(name = 'Kermit')
        Puppet = self.Puppet
        
        Module1 = cgmPuppet.cgmModule(name = 'moduleTest',position = 'front',direction = 'right', handles = 3)
        Module1IO = cgmPuppet.cgmModule(Module1.mNode) #Should equal that of the reg process
        #Assertions on the module null
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the module null...")    
        assert Module1.cgmType == 'module'
        assert Module1.mClass == 'cgmModule'
        assert Module1.cgmName == 'moduleTest'
        assert Module1.cgmPosition == 'front'
        assert Module1.cgmDirection == 'right'
        
        assert Module1.cgmType == Module1.cgmType
        assert Module1.mClass == Module1.mClass
        assert Module1.cgmType == Module1.cgmType
        assert Module1.cgmPosition == Module1.cgmPosition
        assert Module1.cgmDirection == Module1.cgmDirection        
        
        
        #Assertions on the rig null
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the rig null...")   
        assert Module1.i_rigNull.hasAttr('cgmType')
        log.info(Module1.i_rigNull.cgmType)
        
        assert Module1.i_rigNull.cgmType == 'rigNull','%s'%Module1.i_rigNull.cgmType
        assert Module1.i_rigNull.handles == 3,'%s'%Module1.i_rigNull.handles
        assert Module1.i_rigNull.ik == False
        assert Module1.i_rigNull.fk == False
        assert Module1.i_rigNull.bendy == False
        assert Module1.i_rigNull.stretchy == False
        
        
        #Assertions on the template null
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the rig null...")   
        assert Module1.i_rigNull.hasAttr('cgmType')
        log.info(Module1.i_rigNull.cgmType)
        
        
        
        
        
        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)    
        
    def test_Template(self):
        function = 'test_Template'
        log.info("-"*20  + "  Testing '%s' "%function + "-"*20 ) 
        start = time.clock()
        
        
        #Assertions on the module null
        #----------------------------------------------------------
        log.info('>'*3 + " Assertions on the module null...")    
        assert asdfasdfasdfasdf

        
        
        log.info(">"*5  +"  Testing call '%s' took =  %0.3f'" % (function,(time.clock()-start)))
        log.info("="*70)              
















class Test_MetaClass():
    def testAll(self):
        pass
    
    def setup(self):
        mc.file(new=True,f=True)
        self.MClass=r9Meta.MetaClass(name='MetaClass_Test')

    def teardown(self):
        self.setup()
    
    def test_initNew(self):
        assert isinstance(self.MClass,r9Meta.MetaClass)
        assert self.MClass.mClass=='MetaClass'
        assert self.MClass.mNode=='MetaClass_Test'
        assert mc.nodeType(self.MClass.mNode)=='network'
    
    def test_functionCalls(self):
        
        #select
        mc.select(cl=True)
        self.MClass.select()
        assert mc.ls(sl=True)[0]=='MetaClass_Test'
        
        #rename
        self.MClass.rename('FooBar')
        assert self.MClass.mNode=='FooBar'
        self.MClass.select()
        assert mc.ls(sl=True)[0]=='FooBar'
        
        #convert
        new=self.MClass.convertMClassType('MetaRig')
        assert isinstance(new,r9Meta.MetaRig)
        assert self.MClass.mClass=='MetaRig'
        
        #delete
        self.MClass.delete()
        assert not mc.objExists('MetaClass_Test')
        
    def test_MObject_Handling(self):
        #mNode is now handled via an MObject
        assert self.MClass.mNode=='MetaClass_Test'
        mc.rename('MetaClass_Test','FooBar')
        assert self.MClass.mNode=='FooBar'
        
    def test_addChildMetaNode(self):
        '''
        add a new MetaNode as a child of self
        '''
        newMFacial=self.MClass.addChildMetaNode('MetaFacialRig',attr='Facial',nodeName='FacialNode') 
        assert isinstance(newMFacial,r9Meta.MetaFacialRig)
        assert newMFacial.mNode=='FacialNode'
        assert mc.listConnections('%s.Facial' % self.MClass.mNode)==['FacialNode'] 
        assert isinstance(self.MClass.Facial,r9Meta.MetaFacialRig)
        
    def test_getChildMetaNodes(self):
        pass    
        
    def test_connectionsToMetaNodes(self):   
        '''
        Test how the code handles connections to other MetaNodes
        '''
        facialNode=r9Meta.MetaFacialRig(name='FacialNode')
        self.MClass.connectChild(facialNode,'Facial')
        
        assert self.MClass.Facial.mNode=='FacialNode'
        assert isinstance(self.MClass.Facial, r9Meta.MetaFacialRig)
        assert self.MClass.hasAttr('Facial')
        assert facialNode.hasAttr('Facial')
        assert mc.listConnections('%s.Facial' % self.MClass.mNode)==['FacialNode']
        
        self.MClass.disconnectChild(self.MClass.Facial, deleteSourcePlug=True, deleteDestPlug=True)
        assert not self.MClass.hasAttr('Facial')
        assert not facialNode.hasAttr('Facial')       
    
    
    def test_connectionsToMayaNode(self):
        '''
        Test how the code handles connections to standard MayaNodes
        '''
        cube1=mc.ls(mc.polyCube()[0],l=True)[0]
        cube2=mc.ls(mc.polyCube()[0],l=True)[0]
        cube3=mc.ls(mc.polyCube()[0],l=True)[0]
        cube4=mc.ls(mc.polyCube()[0],l=True)[0]
        
        #Singular Child
        self.MClass.connectChild(cube1,'Singluar')
        assert self.MClass.Singluar==[cube1]
        #Multi Children
        self.MClass.connectChildren([cube2,cube3],'Multiple')
        assert sorted(self.MClass.Multiple)==[cube2,cube3]
        
        #get the MetaNode back from the cube1 connection and retest
        found=r9Meta.getConnectedMetaNodes(cube1)[0]
        assert isinstance(found,r9Meta.MetaClass)
        assert found.mNode=='MetaClass_Test'
        assert found.mClass=='MetaClass'
        assert sorted(found.Multiple)==[cube2,cube3]
    
        #connect something else to Singluar
        self.MClass.connectChild(cube2,'Singluar')
        assert self.MClass.Singluar==[cube2]
        assert not mc.attributeQuery('Singluar',node=cube1,exists=True) #cleaned up after ourselves?
        
        self.MClass.connectChildren([cube3,cube4],'Singluar')
        assert sorted(self.MClass.Singluar)==[cube2,cube3,cube4]
        self.MClass.Singluar=cube1
        assert self.MClass.Singluar==[cube1]
        try:
            #still thinking about this....if the attr isn't a multi then
            #the __setattr__ will fail if you pass in a lots of nodes
            self.MClass.Singular=[cube1,cube2,cube3]
        except:
            assert True
        
        self.MClass.Multiple=[cube1,cube4]
        assert sorted(self.MClass.Multiple)==[cube1,cube4]
        
    def test_connectParent(self):
        pass
    
    def test_attributeHandling(self):
        '''
        This tests the standard attribute handing in the MetaClass.__setattr__ 
        '''
        node=self.MClass
        
        #standard attribute handling
        node.addAttr('stringTest', "this_is_a_string")  #create a string attribute
        node.addAttr('fltTest', 1.333)        #create a float attribute
        node.addAttr('intTest', 3)            #create a int attribute
        node.addAttr('boolTest', False)       #create a bool attribute
        node.addAttr('enum', 'A:B:D:E:F', type='enum') #create an enum attribute
        
        #create a string attr with JSON serialized data
        testDict={'jsonFloat':1.05,'jsonInt':3,'jsonString':'string says hello','jsonBool':True}
        node.addAttr('jsonTest',testDict)

        #test the hasAttr call in the baseClass
        assert node.hasAttr('stringTest')
        assert node.hasAttr('fltTest')
        assert node.hasAttr('intTest')
        assert node.hasAttr('boolTest')
        assert node.hasAttr('enum')
        assert node.hasAttr('jsonTest')
        
        #test the actual Maya node attributes
        #------------------------------------
        assert mc.getAttr('%s.stringTest' % node.mNode, type=True)=='string'
        assert mc.getAttr('%s.fltTest' % node.mNode, type=True)=='double'
        assert mc.getAttr('%s.intTest' % node.mNode, type=True)=='long'
        assert mc.getAttr('%s.boolTest' % node.mNode, type=True)=='bool'
        assert mc.getAttr('%s.enum' % node.mNode, type=True)=='enum'
        assert mc.getAttr('%s.jsonTest' % node.mNode, type=True)=='string'
        
        assert mc.getAttr('%s.stringTest' % node.mNode)=='this_is_a_string'
        assert mc.getAttr('%s.fltTest' % node.mNode)==1.333
        assert mc.getAttr('%s.intTest' % node.mNode)==3
        assert mc.getAttr('%s.boolTest' % node.mNode)==False
        assert mc.getAttr('%s.enum' % node.mNode)==0
        assert mc.getAttr('%s.jsonTest' % node.mNode)=='{"jsonFloat": 1.05, "jsonBool": true, "jsonString": "string says hello", "jsonInt": 3}'
        
        #now check the MetaClass __getattribute__ and __setattr__ calls
        #--------------------------------------------------------------
        assert node.intTest==3       
        node.intTest=10     #set back to the MayaNode
        assert node.intTest==10
        #float
        assert node.fltTest==1.333
        node.fltTest=3.55   #set the float attr
        assert node.fltTest==3.55
        #string
        assert node.stringTest=='this_is_a_string'
        node.stringTest="change the text"   #set the string attr
        assert node.stringTest=='change the text'
        #bool
        assert node.boolTest==False
        node.boolTest=True  #set bool
        assert node.boolTest==True
        #enum
        assert node.enum==0
        node.enum='B'
        assert node.enum==1
        node.enum=2
        assert node.enum==2
        #json string handlers
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
    
    
    def test_longJsonDumps(self):
        '''
        Test the handling of LONG serialized Json data - testing the 16bit string attrTemplate handling
        NOTE: if you set a string to over 32,767 chars and don't lock the attr once made, selecting
        the textField in the AttributeEditor will truncate the data, hence this test!
        '''
        data= "x" * 40000
        self.MClass.addAttr('json_test', data)
        assert len(self.MClass.json_test)==40000
        
        #save the file and reload to ensure the attr is consistent
        mc.file(rename=os.path.join(r9Setup.red9ModulePath(),'tests','testFiles','deleteMe'))
        mc.file(save=True,type='mayaAscii')
        mc.file(new=True,f=True)
        mc.file(os.path.join(r9Setup.red9ModulePath(),'tests','testFiles','deleteMe.ma'),open=True,f=True)
        
        mClass=r9Meta.getMetaNodes()[0]
        assert len(mClass.json_test)

 
    def test_messageAttrHandling(self):
        '''
        test the messageLink handling in the __setattr__ block
        '''
        node=self.MClass
                
        #make sure we collect LONG names for these as all wrappers deal with longName
        cube1=mc.ls(mc.polyCube()[0],l=True)[0]
        cube2=mc.ls(mc.polyCube()[0],l=True)[0]
        cube3=mc.ls(mc.polyCube()[0],l=True)[0]
        cube4=mc.ls(mc.polyCube()[0],l=True)[0]
        cube5=mc.ls(mc.polyCube()[0],l=True)[0]
        cube6=mc.ls(mc.polyCube()[0],l=True)[0]
 
        node.addAttr('msgMultiTest', value=[cube1,cube2], type='message')   #multi Message attr
        node.addAttr('msgSingleTest', value=cube3, type='messageSimple')    #non-multi message attr
        
        assert node.hasAttr('msgMultiTest')
        assert node.hasAttr('msgSingleTest')
        
        assert mc.getAttr('%s.msgMultiTest' % node.mNode, type=True)=='message'
        assert mc.getAttr('%s.msgSingleTest' % node.mNode, type=True)=='message'
        assert mc.attributeQuery('msgMultiTest',node=node.mNode, multi=True)==True
        assert mc.attributeQuery('msgSingleTest',node=node.mNode, multi=True)==False
        
        #NOTE : cmds returns shortName, but all MetaClass attrs are always longName
        assert sorted(mc.listConnections('%s.msgMultiTest' % node.mNode))==['pCube1','pCube2']
        assert mc.listConnections('%s.msgSingleTest' % node.mNode)==['pCube3'] 
   
        assert sorted(node.msgMultiTest)==[cube1,cube2]
        assert node.msgSingleTest==[cube3]
        
        #test the reconnect handler via the setAttr
        node.msgMultiTest=[cube5,cube6]
        assert sorted(node.msgMultiTest)==[cube5,cube6]
        assert sorted(mc.listConnections('%s.msgMultiTest' % node.mNode))==['pCube5','pCube6']
        
        node.msgMultiTest=[cube1,cube2,cube4,cube6]
        assert sorted(node.msgMultiTest)==[cube1,cube2,cube4,cube6]
        assert sorted(mc.listConnections('%s.msgMultiTest' % node.mNode))==['pCube1','pCube2','pCube4','pCube6']
        
        node.msgSingleTest=cube4
        assert node.msgSingleTest==[cube4] 
        assert mc.listConnections('%s.msgSingleTest' % node.mNode)==['pCube4'] #cmds returns a list
        node.msgSingleTest=cube3
        assert node.msgSingleTest==[cube3] 
        assert mc.listConnections('%s.msgSingleTest' % node.mNode)==['pCube3'] #cmds returns a list
        
        

