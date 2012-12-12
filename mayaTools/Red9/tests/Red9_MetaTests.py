'''
------------------------------------------
Red9 Studio Pack: Maya Pipeline Solutions
Author: Mark Jackson
email: rednineinfo@gmail.com

Red9 blog : http://red9-consultancy.blogspot.co.uk/
MarkJ blog: http://markj3d.blogspot.co.uk
------------------------------------------

This is the main unittest for the Red9_Meta module and a good
example of what's expected and what the systems can do on simple data
================================================================

'''


import pymel.core as pm
import maya.cmds as cmds
import os

#import Red9_Meta as r9Meta
import Red9.core.Red9_Meta as r9Meta
import Red9.startup.setup as r9Setup


class Test_MetaClass():
    
    def setup(self):
        cmds.file(new=True,f=True)
        self.MClass=r9Meta.MetaClass(name='MetaClass_Test')

    def teardown(self):
        self.setup()
    
    def test_initNew(self):
        assert isinstance(self.MClass,r9Meta.MetaClass)
        assert self.MClass.mClass=='MetaClass'
        assert self.MClass.mNode=='MetaClass_Test'
        assert cmds.nodeType(self.MClass.mNode)=='network'
    
    def test_functionCalls(self):
        
        #select
        cmds.select(cl=True)
        self.MClass.select()
        assert cmds.ls(sl=True)[0]=='MetaClass_Test'
        
        #rename
        self.MClass.rename('FooBar')
        assert self.MClass.mNode=='FooBar'
        self.MClass.select()
        assert cmds.ls(sl=True)[0]=='FooBar'
        
        #convert
        new=self.MClass.convertMClassType('MetaRig')
        assert isinstance(new,r9Meta.MetaRig)
        assert self.MClass.mClass=='MetaRig'
        
        #delete
        self.MClass.delete()
        assert not cmds.objExists('MetaClass_Test')
        
    def test_MObject_Handling(self):
        #mNode is now handled via an MObject
        assert self.MClass.mNode=='MetaClass_Test'
        cmds.rename('MetaClass_Test','FooBar')
        assert self.MClass.mNode=='FooBar'
        
    def test_addChildMetaNode(self):
        '''
        add a new MetaNode as a child of self
        '''
        newMFacial=self.MClass.addChildMetaNode('MetaFacialRig',attr='Facial',nodeName='FacialNode') 
        assert isinstance(newMFacial,r9Meta.MetaFacialRig)
        assert newMFacial.mNode=='FacialNode'
        assert cmds.listConnections('%s.Facial' % self.MClass.mNode)==['FacialNode'] 
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
        assert cmds.listConnections('%s.Facial' % self.MClass.mNode)==['FacialNode']
        
        self.MClass.disconnectChild(self.MClass.Facial, deleteSourcePlug=True, deleteDestPlug=True)
        assert not self.MClass.hasAttr('Facial')
        assert not facialNode.hasAttr('Facial')       
    
    
    def test_connectionsToMayaNode(self):
        '''
        Test how the code handles connections to standard MayaNodes
        '''
        cube1=cmds.ls(cmds.polyCube()[0],l=True)[0]
        cube2=cmds.ls(cmds.polyCube()[0],l=True)[0]
        cube3=cmds.ls(cmds.polyCube()[0],l=True)[0]
        cube4=cmds.ls(cmds.polyCube()[0],l=True)[0]
        
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
        assert not cmds.attributeQuery('MetaClassTest',node=cube1,exists=True) #cleaned up after ourselves?
        
        self.MClass.connectChildren([cube3,cube4],'Singluar')
        assert sorted(self.MClass.Singluar)==[cube2,cube3,cube4]
        self.MClass.Singluar=cube1
        assert self.MClass.Singluar==[cube1]
        try:
            #still thinking about this....if the attr isn't a multi then
            #the __setattr__ will fail if you pass in a lots of nodes
            self.MClass.Singluar=[cube1,cube2,cube3]
        except:
            assert True
        
        self.MClass.Multiple=[cube1,cube4]
        assert sorted(self.MClass.Multiple)==[cube1,cube4]
        
    def test_connectParent(self):
        #TODO: Fill Test
        pass
    
    def test_attributeHandling(self):
        '''
        This tests the standard attribute handing in the MetaClass.__setattr__ 
        '''
        node=self.MClass
        
        #standard attribute handling
        node.addAttr('stringTest', "this_is_a_string")  #create a string attribute
        node.addAttr('fltTest', 1.333)        #create a float attribute
        node.addAttr('fltTest2', 10.5, min=0,max=15)  #create a float attribute with min/max
        node.addAttr('intTest', 3)            #create a int attribute
        node.addAttr('boolTest', False)       #create a bool attribute
        node.addAttr('enum', 'A:B:D:E:F', attrType='enum') #create an enum attribute
        node.addAttr('doubleTest', attrType='double3', value=(('dblA','dblB','dblC'),(1.12,2.55,5.0)))
        node.addAttr('doubleTest2', attrType='double3', value=(('dbl2A','dbl2B','dbl2C'),(1.0,2.0,10.0)),min=1,max=15)
                     
        #create a string attr with JSON serialized data
        testDict={'jsonFloat':1.05,'jsonInt':3,'jsonString':'string says hello','jsonBool':True}
        node.addAttr('jsonTest',testDict)

        #test the hasAttr call in the baseClass
        assert node.hasAttr('stringTest')
        assert node.hasAttr('fltTest')
        assert node.hasAttr('fltTest2')
        assert node.hasAttr('intTest')
        assert node.hasAttr('boolTest')
        assert node.hasAttr('enum')
        assert node.hasAttr('jsonTest')
        assert node.hasAttr('doubleTest')   #compound3 so it adds 3 child attrs
        assert node.hasAttr('dblA')
        assert node.hasAttr('dblB')
        assert node.hasAttr('dblC')
        assert node.hasAttr('doubleTest2')
        
        #test the actual Maya node attributes
        #------------------------------------
        assert cmds.getAttr('%s.stringTest' % node.mNode, type=True)=='string'
        assert cmds.getAttr('%s.fltTest' % node.mNode, type=True)=='double'
        assert cmds.getAttr('%s.fltTest2' % node.mNode, type=True)=='double'
        assert cmds.getAttr('%s.intTest' % node.mNode, type=True)=='long'
        assert cmds.getAttr('%s.boolTest' % node.mNode, type=True)=='bool'
        assert cmds.getAttr('%s.enum' % node.mNode, type=True)=='enum'
        assert cmds.getAttr('%s.jsonTest' % node.mNode, type=True)=='string'
        assert cmds.getAttr('%s.doubleTest' % node.mNode, type=True)=='double3'
        assert cmds.getAttr('%s.dblA' % node.mNode, type=True)=='double'
        assert cmds.getAttr('%s.dblB' % node.mNode, type=True)=='double'
        assert cmds.getAttr('%s.dblC' % node.mNode, type=True)=='double'
        
        assert cmds.getAttr('%s.stringTest' % node.mNode)=='this_is_a_string'
        assert cmds.getAttr('%s.fltTest' % node.mNode)==1.333
        assert cmds.getAttr('%s.fltTest2' % node.mNode)==10.5
        assert cmds.getAttr('%s.intTest' % node.mNode)==3
        assert cmds.getAttr('%s.boolTest' % node.mNode)==False
        assert cmds.getAttr('%s.enum' % node.mNode)==0
        assert cmds.getAttr('%s.jsonTest' % node.mNode)=='{"jsonFloat": 1.05, "jsonBool": true, "jsonString": "string says hello", "jsonInt": 3}'
        assert cmds.getAttr('%s.doubleTest' % node.mNode)==[(1.12,2.55,5.0)]
        assert cmds.getAttr('%s.dblA' % node.mNode)==1.12
        assert cmds.getAttr('%s.dblB' % node.mNode)==2.55
        assert cmds.getAttr('%s.dblC' % node.mNode)==5.0
        
        assert cmds.attributeQuery('fltTest2',node=node.mNode, max=True)==[15.0]
        assert cmds.attributeQuery('dbl2A',node=node.mNode, min=True)==[1.0]
        assert cmds.attributeQuery('dbl2A',node=node.mNode, max=True)==[15.0]


        
        #now check the MetaClass __getattribute__ and __setattr__ calls
        #--------------------------------------------------------------
        assert node.intTest==3       
        node.intTest=10     #set back to the MayaNode
        assert node.intTest==10
        #float
        assert node.fltTest==1.333
        node.fltTest=3.55   #set the float attr
        assert node.fltTest==3.55
        #float with min, max kws passed
        try: 
            #try setting the value past it's max
            node.fltTest2=22
            assert False
        except:
            assert True
        try: 
            #try setting the value past it's min
            node.fltTest2=-5
            assert False
        except:
            assert True    
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
        #double3
        assert node.doubleTest==[(1.12,2.55,5.0)]
        assert node.dblA==1.12
        assert node.dblB==2.55
        assert node.dblC==5.0
        node.doubleTest=(2.0,44.2,22.0)
        assert node.doubleTest==[(2.0,44.2,22.0)]
        try: 
            #try setting the value past it's max
            node.doubleTest2=(0,1,22)
            assert False
        except:
            assert True
        try: 
            #try setting the value past it's max
            node.dblA=-10
            assert False
        except:
            assert True
            
        del(node.boolTest)
        assert cmds.objExists(node.mNode)
        assert not node.hasAttr('boolTest')
        assert not cmds.attributeQuery('boolTest',node=node.mNode,exists=True)
    
    
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
        cmds.file(rename=os.path.join(r9Setup.red9ModulePath(),'tests','testFiles','deleteMe'))
        cmds.file(save=True,type='mayaAscii')
        cmds.file(new=True,f=True)
        cmds.file(os.path.join(r9Setup.red9ModulePath(),'tests','testFiles','deleteMe.ma'),open=True,f=True)
        
        mClass=r9Meta.getMetaNodes()[0]
        assert len(mClass.json_test)

 
    def test_messageAttrHandling(self):
        '''
        test the messageLink handling in the __setattr__ block
        '''
        node=self.MClass
                
        #make sure we collect LONG names for these as all wrappers deal with longName
        cube1=cmds.ls(cmds.polyCube()[0],l=True)[0]
        cube2=cmds.ls(cmds.polyCube()[0],l=True)[0]
        cube3=cmds.ls(cmds.polyCube()[0],l=True)[0]
        cube4=cmds.ls(cmds.polyCube()[0],l=True)[0]
        cube5=cmds.ls(cmds.polyCube()[0],l=True)[0]
        cube6=cmds.ls(cmds.polyCube()[0],l=True)[0]
 
        node.addAttr('msgMultiTest', value=[cube1,cube2], attrType='message')   #multi Message attr
        node.addAttr('msgSingleTest', value=cube3, attrType='messageSimple')    #non-multi message attr
        
        assert node.hasAttr('msgMultiTest')
        assert node.hasAttr('msgSingleTest')
        
        assert cmds.getAttr('%s.msgMultiTest' % node.mNode, type=True)=='message'
        assert cmds.getAttr('%s.msgSingleTest' % node.mNode, type=True)=='message'
        assert cmds.attributeQuery('msgMultiTest',node=node.mNode, multi=True)==True
        assert cmds.attributeQuery('msgSingleTest',node=node.mNode, multi=True)==False
        
        #NOTE : cmds returns shortName, but all MetaClass attrs are always longName
        assert sorted(cmds.listConnections('%s.msgMultiTest' % node.mNode))==['pCube1','pCube2']
        assert cmds.listConnections('%s.msgSingleTest' % node.mNode)==['pCube3'] 
   
        assert sorted(node.msgMultiTest)==[cube1,cube2]
        assert node.msgSingleTest==[cube3]
        
        #test the reconnect handler via the setAttr
        node.msgMultiTest=[cube5,cube6]
        assert sorted(node.msgMultiTest)==[cube5,cube6]
        assert sorted(cmds.listConnections('%s.msgMultiTest' % node.mNode))==['pCube5','pCube6']
        
        node.msgMultiTest=[cube1,cube2,cube4,cube6]
        assert sorted(node.msgMultiTest)==[cube1,cube2,cube4,cube6]
        assert sorted(cmds.listConnections('%s.msgMultiTest' % node.mNode))==['pCube1','pCube2','pCube4','pCube6']
        
        node.msgSingleTest=cube4
        assert node.msgSingleTest==[cube4] 
        assert cmds.listConnections('%s.msgSingleTest' % node.mNode)==['pCube4'] #cmds returns a list
        node.msgSingleTest=cube3
        assert node.msgSingleTest==[cube3] 
        assert cmds.listConnections('%s.msgSingleTest' % node.mNode)==['pCube3'] #cmds returns a list
        
        
    def test_castingStandardNode(self):
        mLambert=r9Meta.MetaClass('lambert1')
        #mLambert is just a Python MetaNode and doesn't exist as a MayaNode
        mLambert.diffuse=0.5
        assert '%0.2f' % cmds.getAttr('lambert1.diffuse')=='0.50'
        mLambert.diffuse=0.77
        assert '%0.2f' % cmds.getAttr('lambert1.diffuse')=='0.77'
        
        mLambert.color=(0.5, 0.5, 0.5)
        assert mLambert.color==[(0.5,0.5,0.5)]
        assert cmds.getAttr('lambert1.color')==[(0.5, 0.5, 0.5)]
        mLambert.color=(1.0, 0.0, 0.5)
        print mLambert.color
        assert mLambert.color==[(1.0, 0.0, 0.5)]
        assert cmds.getAttr('lambert1.color')==[(1.0, 0.0, 0.5)]


class Test_SearchCalls():
    
    def setup(self):
        cmds.file(new=True,f=True)
        r9Meta.MetaClass(name='MetaClass_Test')
        r9Meta.MetaRig(name='MetaRig_Test')
        r9Meta.MetaRigSupport(name='MetaRigSupport_Test')
        r9Meta.MetaFacialRig(name='MetaFacialRig_Test')
        r9Meta.MetaFacialRigSupport(name='MetaFacialRigSupport_Test')

    def teardown(self):
        self.setup()    
           
    def test_isMetaNode(self):
        assert r9Meta.isMetaNode('MetaRig_Test')
        assert r9Meta.isMetaNode('MetaRig_Test', mTypes=['MetaRig'])
        assert r9Meta.isMetaNode('MetaRig_Test', mTypes='MetaRig')
        assert not r9Meta.isMetaNode('MetaRig_Test', mTypes='MonkeyBollox')
        assert not r9Meta.isMetaNode('MetaRig_Test', mTypes='MetaFacialRigSupport_Test')
        cube1=cmds.ls(cmds.polyCube()[0],l=True)[0]
        assert not r9Meta.isMetaNode(cube1)
        
    def test_isMetaNodeInherited(self):
        assert r9Meta.isMetaNodeInherited('MetaFacialRig_Test','MetaRig')
        assert r9Meta.isMetaNodeInherited('MetaFacialRig_Test','MetaClass')
        assert not r9Meta.isMetaNodeInherited('MetaFacialRig_Test','MetaRigSubSystem')
    
    def test_getMetaNodes(self):
        nodes=sorted(r9Meta.getMetaNodes(),key=lambda x: x.mClass.upper())
        assert [n.mClass for n in nodes]==['MetaClass','MetaFacialRig','MetaFacialRigSupport','MetaRig','MetaRigSupport']
        
        nodes=sorted(r9Meta.getMetaNodes(mTypes=['MetaRig','MetaFacialRig']),key=lambda x: x.mClass.upper())
        assert [n.mClass for n in nodes]==['MetaFacialRig','MetaRig']
        
        nodes=r9Meta.getMetaNodes(dataType=None, mTypes=['MetaRig'])
        assert nodes==['MetaRig_Test']
        
        #mInstances tests
        nodes=r9Meta.getMetaNodes(dataType=None, mInstances=['MetaRig'])
        assert nodes==['MetaFacialRig_Test', 'MetaRig_Test']
        nodes=r9Meta.getMetaNodes(mInstances=['MetaRig'])
        assert [n.mNodeID for n in nodes]==['MetaFacialRig_Test', 'MetaRig_Test']
        nodes=r9Meta.getMetaNodes(mInstances=['MetaClass'])
        assert sorted([n.mNode for n in nodes])==['MetaClass_Test',
                                                  'MetaFacialRigSupport_Test',
                                                  'MetaFacialRig_Test',
                                                  'MetaRigSupport_Test',
                                                  'MetaRig_Test']  
          
    def test_getConnectedMetaNodes(self):
        #nodes, source=True, destination=True, dataType='mClass', mTypes=[]):
        #TODO: Fill Test
        pass
        
    
    def test_getConnectedMetaSystemRoot(self):
        #TODO: Fill Test
        pass
    
    
class Test_MetaRig():
    
    def setup(self):
        cmds.file(os.path.join(r9Setup.red9ModulePath(),'tests','testFiles','MetaRig_baseTests.ma'),open=True,f=True)
        self.mRig=self.addMetaRig()
        
    def teardown(self):
        self.setup()   
        
    def addMetaRig(self):
        '''
        Add a basic MetaRig network to the file including MetaSubSystems and MetaSupport
        '''
        mRig=r9Meta.MetaRig(name='RED_Rig')

        #Link the MainCtrl , this is used as Root for some of the functions
        mRig.addRigCtrl('World_Ctrl','Main', mirrorData={'side':'Centre', 'slot':1})
        
        #Left Arm SubMeta Systems --------------------------
        lArm= mRig.addMetaSubSystem('Arm', 'Left', nodeName='L_ArmSystem', attr='L_ArmSystem')
        lArm.addRigCtrl('L_Wrist_Ctrl','L_Wrist', mirrorData={'side':'Left','slot':1})
        lArm.addRigCtrl('L_Elbow_Ctrl','L_Elbow', mirrorData={'side':'Left','slot':2})
        lArm.addRigCtrl('L_Clav_Ctrl','L_Clav', mirrorData={'side':'Left','slot':3})
        #Left Leg SubMeta Systems --------------------------
        lLeg= mRig.addMetaSubSystem('Leg', 'Left', nodeName='L_LegSystem')
        lLeg.addRigCtrl('L_Foot_Ctrl','L_Foot', mirrorData={'side':'Left','slot':4})
        lLeg.addRigCtrl('L_Knee_Ctrl', 'L_Knee',   mirrorData={'side':'Left','slot':5})
        
        #Right Arm SubMeta Systems --------------------------
        rArm= mRig.addMetaSubSystem('Arm', 'Right', nodeName='R_ArmSystem', attr='R_ArmSystem')
        rArm.addRigCtrl('R_Wrist_Ctrl','R_Wrist', mirrorData={'side':'Right','slot':1})
        rArm.addRigCtrl('R_Elbow_Ctrl','R_Elbow', mirrorData={'side':'Right','slot':2})
        rArm.addRigCtrl('R_Clav_Ctrl','R_Clav', mirrorData={'side':'Right', 'slot':3})
        #Right Leg SubMeta System --------------------------
        rLeg= mRig.addMetaSubSystem('Leg', 'Right', nodeName='R_LegSystem', attr='R_LegSystem')
        rLeg.addRigCtrl('R_Foot_Ctrl','R_Foot', mirrorData={'side':'Right','slot':4})
        rLeg.addRigCtrl('R_Knee_Ctrl', 'R_Knee',   mirrorData={'side':'Right','slot':5})
        
        #Spine SubMeta System -------------------------------
        spine= mRig.addMetaSubSystem('Spine', 'Centre', nodeName='SpineSystem', attr='SpineSystem')
        spine.addRigCtrl('COG__Ctrl','Root',  mirrorData={'side':'Centre','slot':2})
        spine.addRigCtrl('Hips_Ctrl','Hips', mirrorData={'side':'Centre','slot':3})  
        spine.addRigCtrl('Chest_Ctrl','Chest', mirrorData={'side':'Centre','slot':4})
        spine.addRigCtrl('Head_Ctrl','Head',  mirrorData={'side':'Centre','slot':5})
        
        #add SupportMeta Nodes ------------------------------
        #this is a really basic demo, for the sake of this you could
        #just wire all the support nodes to one MetaSupport, but this 
        #shows what you could do for really complex setups
        lArm.addSupportMetaNode('L_ArmSupport')
        lArm.L_ArmSupport.addSupportNode('ikHandle1','IKHandle')
        rArm.addSupportMetaNode('R_ArmSupport')
        rArm.R_ArmSupport.addSupportNode('ikHandle2','IKHandle')
        lLeg.addSupportMetaNode('L_LegSupport')
        lLeg.L_LegSupport.addSupportNode('ikHandle5','IKHandle')
        rLeg.addSupportMetaNode('R_LegSupport')
        rLeg.R_LegSupport.addSupportNode('ikHandle6','IKHandle')
        spine.addSupportMetaNode('SpineSupport')
        spine.SpineSupport.addSupportNode('ikHandle3','NeckIK')
        spine.SpineSupport.addSupportNode('ikHandle4','SpineIK')
        
        return mRig
    
    
    def test_basicRigStructure(self):
        
        mRig=r9Meta.getConnectedMetaSystemRoot('L_Wrist_Ctrl')
        
        assert type(mRig)==r9Meta.MetaRig
        assert mRig.mNode=='RED_Rig'
        assert mRig.CTRL_Main[0]=='|World_Ctrl'
        
        #test the Left Arm wires
        assert type(mRig.L_ArmSystem)==r9Meta.MetaRigSubSystem
        assert mRig.L_ArmSystem.mNode=='L_ArmSystem'
        assert mRig.L_ArmSystem.systemType=='Arm'
        assert mRig.L_ArmSystem.mirrorSide==1
        assert mRig.L_ArmSystem.CTRL_L_Wrist[0]=='|World_Ctrl|L_Wrist_Ctrl'
        assert mRig.L_ArmSystem.CTRL_L_Elbow[0]=='|World_Ctrl|COG__Ctrl|L_Elbow_Ctrl'
        ctrl=r9Meta.MetaClass(mRig.L_ArmSystem.CTRL_L_Wrist[0])
        assert ctrl.mirrorSide==1 #?????? consistency of attrs on node and metaSubsystems!!!!!!!
        assert ctrl.mirrorIndex==1
        
        #test the Right Leg wires
        assert type(mRig.R_LegSystem)==r9Meta.MetaRigSubSystem
        assert r9Meta.isMetaNode('R_LegSystem')
        assert mRig.R_LegSystem.mNode=='R_LegSystem'
        assert mRig.R_LegSystem.systemType=='Leg'
        assert mRig.R_LegSystem.mirrorSide==2
        assert mRig.R_LegSystem.CTRL_R_Foot[0]=='|World_Ctrl|R_Foot_Ctrl'
        assert mRig.R_LegSystem.CTRL_R_Knee[0]=='|World_Ctrl|R_Knee_Ctrl'
        ctrl=r9Meta.MetaClass(mRig.R_LegSystem.CTRL_R_Foot[0])
        assert ctrl.mirrorSide==2 #?????? consistency of attrs on node and metaSubsystems!!!!!!!
        assert ctrl.mirrorIndex==4
        
        #test the Left Leg wires 
        #:NOTE slight difference in the naming as we didn't pass in the attr when making the subSystem
        assert type(mRig.L_Leg_System)==r9Meta.MetaRigSubSystem
        assert r9Meta.isMetaNode('L_LegSystem')
        assert mRig.L_Leg_System.mNode=='L_LegSystem'
        assert mRig.L_Leg_System.systemType=='Leg'
        assert mRig.L_Leg_System.mirrorSide==1      
        
        #test the Spine wires
        assert type(mRig.SpineSystem)==r9Meta.MetaRigSubSystem
        assert mRig.SpineSystem.mNode=='SpineSystem'
        assert mRig.SpineSystem.systemType=='Spine'
        assert mRig.SpineSystem.mirrorSide==0
        assert mRig.SpineSystem.CTRL_Hips[0]=='|World_Ctrl|COG__Ctrl|Hips_Ctrl'
        assert mRig.SpineSystem.CTRL_Chest[0]=='|World_Ctrl|COG__Ctrl|Chest_Ctrl'
        ctrl=r9Meta.MetaClass(mRig.SpineSystem.CTRL_Chest[0])
        assert ctrl.mirrorSide==0 #?????? consistency of attrs on node and metaSubsystems!!!!!!!
        assert ctrl.mirrorIndex==4
        
        #test the MetaRigSupport nodes
        assert type(mRig.L_ArmSystem.L_ArmSupport)==r9Meta.MetaRigSupport
        assert mRig.L_ArmSystem.L_ArmSupport.mNode=='L_ArmSupport'
        assert mRig.L_ArmSystem.L_ArmSupport.SUP_IKHandle[0]=='|World_Ctrl|L_Wrist_Ctrl|ikHandle1'
        assert mRig.SpineSystem.SpineSupport.SUP_NeckIK[0]=='|World_Ctrl|COG__Ctrl|Chest_Ctrl|Head_Ctrl|ikHandle3'
        assert mRig.SpineSystem.SpineSupport.SUP_SpineIK[0]=='|World_Ctrl|COG__Ctrl|Chest_Ctrl|ikHandle4'
        
        
    def test_getRigCtrls(self):
        assert self.mRig.getRigCtrls()==['|World_Ctrl']
        assert self.mRig.getRigCtrls(walk=True)==['|World_Ctrl', 
                                                  '|World_Ctrl|R_Foot_Ctrl', 
                                                  '|World_Ctrl|R_Knee_Ctrl',
                                                  '|World_Ctrl|COG__Ctrl', 
                                                  '|World_Ctrl|COG__Ctrl|Hips_Ctrl',
                                                  '|World_Ctrl|COG__Ctrl|Chest_Ctrl', 
                                                  '|World_Ctrl|COG__Ctrl|Chest_Ctrl|Head_Ctrl', 
                                                  '|World_Ctrl|L_Wrist_Ctrl', 
                                                  '|World_Ctrl|COG__Ctrl|L_Elbow_Ctrl',
                                                  '|World_Ctrl|COG__Ctrl|Chest_Ctrl|L_Clav_Ctrl', 
                                                  '|World_Ctrl|L_Foot_Ctrl',
                                                  '|World_Ctrl|L_Knee_Ctrl', 
                                                  '|World_Ctrl|R_Wrist_Ctrl', 
                                                  '|World_Ctrl|COG__Ctrl|R_Elbow_Ctrl', 
                                                  '|World_Ctrl|COG__Ctrl|Chest_Ctrl|R_Clav_Ctrl'] 
        
        assert self.mRig.R_ArmSystem.getRigCtrls()==['|World_Ctrl|R_Wrist_Ctrl', 
                                                     '|World_Ctrl|COG__Ctrl|R_Elbow_Ctrl', 
                                                     '|World_Ctrl|COG__Ctrl|Chest_Ctrl|R_Clav_Ctrl']

        assert self.mRig.R_ArmSystem.getChildren()==['|World_Ctrl|R_Wrist_Ctrl', 
                                                     '|World_Ctrl|COG__Ctrl|R_Elbow_Ctrl', 
                                                     '|World_Ctrl|COG__Ctrl|Chest_Ctrl|R_Clav_Ctrl']  
        