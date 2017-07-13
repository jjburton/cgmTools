"""
------------------------------------------
cgm_Meta: cgm.core.test
Author: Ryan Porter
email: ryan.m.porter@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Unit Tests for the validateArgs.objString function
================================================================
"""
# IMPORTS ====================================================================
import unittest
import logging
import unittest.runner
import maya.standalone

try:
    import maya.cmds as mc   
    from Red9.core import Red9_Meta as r9Meta
    from cgm.core import cgm_Meta as cgmMeta
    from cgm.core.cgmPy import validateArgs as VALID
    from cgm.core.lib import attribute_utils as ATTR
    from cgm.core.lib import transform_utils as TRANS
    from cgm.core.lib import math_utils as MATH
    
except ImportError:
    raise StandardError('objString test can only be run in Maya')

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)  
    
# CLASSES ====================================================================
  
class Test_cgmAttr(unittest.TestCase):
    pass

class Test_cgmObject(unittest.TestCase):
    def test_base(self):
        mObj = cgmMeta.cgmObject(name = 'cgmObjectTester')
        mObj.rotateOrder = 0
        
        self.assertEqual(VALID.is_transform(mObj.mNode),
                         True)
        
        _node = mc.createNode('multiplyDivide',name='cgmObjectCallMD_node')
        self.assertRaises(ValueError,
                          cgmMeta.cgmObject,
                          _node)
        
        
    def test_existing(self):
        self.maxDiff = 1000
        
        
        pCube = cgmMeta.cgmObject( mc.polyCube(name = 'cgmObject_poly')[0] )
        pCube2 = cgmMeta.cgmObject( mc.polyCube(name = 'cgmObject_poly2')[0] )        
        nCube = cgmMeta.cgmObject( mc.nurbsCube(name = 'cgmObject_nurbs')[0] )   
        TRANS.set_random(pCube,posLocal = True, rotLocal = True)
        TRANS.set_random(nCube,posLocal = True, rotLocal = True)
        
        
        #Components ==============================================================================
        _l_vtx = pCube.getComponents('vtx')
        _l_face = pCube.getComponents('face')
        self.assertEqual(len(_l_vtx),
                         8)
        self.assertEqual(len(_l_face),
                         6)        
        
        #Snap ==============================================================================
        TRANS.set_random(pCube2, posWorld=True,rotWorld = True)
    
        pCube.doSnapTo(pCube2)
        self.assertEqual(MATH.is_vector_equivalent(pCube.p_position,
                                                   pCube2.p_position),
                         True,"{0} != {1}".format(pCube.p_position, pCube2.p_position))        
        self.assertEqual(MATH.is_vector_equivalent(pCube.p_orient,
                                                   pCube2.p_orient),
                         True,"{0} != {1}".format(pCube.p_orient, pCube2.p_orient))          
        
        #Heirarchy ======================================================================
        self.assertNotEqual(pCube.getSiblings(),
                            False)       
        
        
        pCube.parent = nCube
        self.assertEqual(pCube.parent,
                         nCube.mNode)
        self.assertEqual(pCube.getParent(),
                         nCube.mNode)
        
        self.assertEqual(pCube.isChildTo(nCube),
                         True)
        self.assertEqual(nCube.isParentTo(pCube),
                         True)        
        self.assertEqual(pCube.p_nameShort in nCube.getChildren(fullPath=False),
                         True)
        self.assertIsNot(pCube.getShapes(),False)
        


        #self.assertEqual(pCube.getTransformAttrs(),
                         #nCube.getTransformAttrs())
        
        
        pCube.parent = False
        self.assertEqual(pCube.parent,
                         False)  
        
        
        
        #Parent series ==============================================================================
        pCube2.parent = pCube
        nCube.parent = pCube2
        
        self.assertEqual(pCube.getListPathTo(nCube,asMeta=True),
                         [pCube,pCube2,nCube])
        
        self.assertIsNotNone(pCube.getDescendents(),
                             )        
        self.assertEqual(nCube.getParents(True),
                         [pCube2,pCube])
        
        #getTransformAttrs?
        #doAddChild?
        #doCopyRotateOrder
        
        #>> Rotate Order...
        pCube.rotateOrder = 2
        nCube.rotateOrder = pCube.rotateOrder
        self.assertEqual(pCube.rotateOrder,
                         nCube.rotateOrder)
        
        #>> Group ===============================================================================
        _pos = TRANS.position_get(pCube2)
        #TRANS.group_me(pCube2,True,True)
        pCube2.doGroup(True,asMeta=True)
        
        self.assertEqual(MATH.is_vector_equivalent(_pos, TRANS.position_get(pCube2)),
                         True)
        
        
        #>> Transform ===============================================================================
        nCube.parent = False
        nCube.translate = pCube.translate
                
        self.assertEqual(MATH.is_vector_equivalent(nCube.translate,
                                                   pCube.translate),
                        True)        
        
        TRANS.set_random(nCube,posLocal = True, rotLocal = True)        
        self.assertNotEqual(nCube.p_position,
                            pCube.p_position)
        nCube.p_position = pCube.p_position
        self.assertEqual(MATH.is_vector_equivalent(nCube.translate,
                                                   pCube.translate),
                        True)        
        
        #...rot -------------------------------------------------------------------------------
        nCube.rotate = pCube.rotate
        self.assertEqual(MATH.is_vector_equivalent(nCube.rotate,
                                                   pCube.rotate),
                         True)    
        TRANS.set_random(nCube, rotWorld = True) 
        self.assertEqual(MATH.is_vector_equivalent(nCube.rotate,
                                                   pCube.rotate),
                         False)
        
        #log.info(nCube)
        #log.info(pCube)
        nCube.p_orient = pCube.p_orient
        self.assertEqual(MATH.is_vector_equivalent(nCube.rotate,
                                                   pCube.rotate),
                         True)
        
        #...scale -----------------------------------------------------------------------------
        nCube.resetAttrs('scale')
        mGroup = nCube.doGroup(True,True,asMeta=True)
        mGroup.scale = 2,2,2
        nCube.scale = 2,2,2
        
        self.assertEqual(nCube.getScaleLossy(),
                         [4,4,4])      
        
        
        #>> Pivots ===================================================================
        pCube.p_rotatePivot = pCube2.p_rotatePivot
        self.assertEqual(MATH.is_vector_equivalent(pCube.p_rotatePivot,
                                                   pCube2.p_rotatePivot),
                         True)          
        pCube.p_scalePivot = pCube2.p_scalePivot
        self.assertEqual(MATH.is_vector_equivalent(pCube.p_scalePivot,
                                                   pCube2.p_scalePivot),
                         True)          
        
        #self.assertNotEqual(nCube.p_orei,
        #                    pCube.p_posWorld)        
        
        
        #self.assertAlmostEquals(_pos,
        #                        TRANS.position_get(pCube),
        #                        7)
        
        #>> draw override ======================
        pCube.doOverrideColor(index = 20)
        for mShape in pCube.getShapes(True):
            self.assertEqual(mShape.overrideEnabled,
                             True)    
            self.assertEqual(mShape.overrideColor,
                             20)            
            
        #>> Contraints ===================================================================
        pCube2.p_parent = False
        _contraint = mc.parentConstraint([pCube.mNode,nCube.mNode], pCube2.mNode, maintainOffset = True)
        _mConstraint = cgmMeta.cgmObject(_contraint[0])
        
        self.assertEqual(pCube2.getConstraintsByDrivingObject(pCube.mNode,True),
                         [_mConstraint])
        self.assertItemsEqual([mObj.mNode for mObj in pCube2.getConstrainingObjects(True)],
                              [pCube.mNode,nCube.mNode])
        
        self.assertEqual([_mConstraint],
                         pCube2.getConstraintsTo(True))
        
        self.assertEqual(pCube2.getConstraintsFrom(True),
                         [_mConstraint])
    

  

class Test_cgmObjectSet(unittest.TestCase):
    def test_all(self):
        mObjectSetDefault = cgmMeta.cgmObjectSet('defaultObjectSet')
        mObjectSetAnim = cgmMeta.cgmObjectSet(name='cgmObjectAnimationSet',setType = 'animation', qssState = True)
        mObjectSetAnim2 = cgmMeta.cgmObjectSet(name='cgmObjectAnimationSet2',setType = 'animation', qssState = True) 
        
        mPCube = cgmMeta.cgmObject( mc.polyCube(name = 'cgmObjectSetTarget_poly')[0] )
        mNCube = cgmMeta.cgmObject( mc.nurbsCube(name = 'cgmObjectSetTarget_nurbs')[0] )   
        TRANS.set_random(mPCube,posLocal = True, rotLocal = True)
        TRANS.set_random(mNCube,posLocal = True, rotLocal = True)


        self.assertEqual(mObjectSetAnim.value,
                         mObjectSetAnim2.value)
        
        #Maya set type...
        self.assertEqual(mObjectSetDefault.mayaSetState,
                         True)
        self.assertEqual(mObjectSetAnim.mayaSetState,
                         False)   
        
        #Qss checks...
        self.assertEqual(mObjectSetDefault.qssState,
                         False)  
        self.assertEqual(mObjectSetAnim.qssState,
                         True)
        
        mObjectSetAnim.qssState = False
        self.assertEqual(mObjectSetAnim.qssState,
                         False)  
        

        #Set types...
        self.assertEqual(mObjectSetAnim.objectSetType,
                         'animation')
        mObjectSetAnim.objectSetType = 'modeling'
        self.assertEqual(mObjectSetAnim.objectSetType,
                         'modeling')       
        
        #>>>Values ----------------------------------------------------------------------------
        
        self.assertEqual(mObjectSetAnim.getList(),
                         [])
        
        
        
        mObjectSetAnim.value = [mPCube.mNode, mNCube.mNode, mNCube.mNode+'.tx']
        
        self.assertEqual(mObjectSetAnim.contains(mPCube.mNode),
                         True)
        self.assertEqual(mObjectSetAnim.contains(mNCube.mNode),
                         True)   
        
        self.assertEqual(mObjectSetAnim.contains("{0}.translateX".format(mNCube.mNode)),
                         True)           
        
        mObjectSetAnim.value = False
        self.assertEqual(mObjectSetAnim.value,
                         [])    
        
        #>>>Add ----------------------------------------------------------------------------
        mObjectSetAnim.value = False
        
        mObjectSetAnim.add(mNCube.mNode)
        mObjectSetAnim.add(mPCube.mNode)
        mObjectSetAnim.add(mPCube.mNode + '.tx')
        
        self.assertEqual(mObjectSetAnim.contains(mPCube.mNode),
                         True)
        self.assertEqual(mObjectSetAnim.contains(mNCube.mNode),
                         True)   
        
        self.assertEqual(mObjectSetAnim.contains("{0}.translateX".format(mPCube.mNode)),
                         True)       
        
        mObjectSetAnim.remove(mPCube.mNode)
        mObjectSetAnim.remove(mNCube.mNode)
        self.assertEqual(mObjectSetAnim.contains(mPCube.mNode),
                         False)
        self.assertEqual(mObjectSetAnim.contains(mNCube.mNode),
                         False)     
        
        #>>>SelectPurgeCopy ----------------------------------------------------------------------------
        mObjectSetAnim.add(mNCube.mNode)
        mObjectSetAnim.add(mPCube.mNode)    
        
        mc.select(cl=True)
        mObjectSetAnim.select()
        
        self.assertEqual(mObjectSetAnim.getList(),
                         mc.ls(sl=True)) 
        
        mc.select(cl=True)
        mObjectSetAnim.selectSelf()
        self.assertEqual([mObjectSetAnim.mNode],
                         mc.ls(sl=True))     
        
        #>>Copy set...
        mObjectSetAnimCopy = mObjectSetAnim.copy()
        self.assertEqual(mObjectSetAnim.getList(),
                         mObjectSetAnimCopy.getList()) 
        self.assertEqual(mObjectSetAnim.objectSetType,
                         mObjectSetAnimCopy.objectSetType )
        self.assertEqual(mObjectSetAnim.qssState,
                         mObjectSetAnimCopy.qssState) 
        
        #>>Purge...
        mObjectSetAnimCopy.purge()
        self.assertEqual(mObjectSetAnimCopy.getList(),
                         [])
        
        #>>>Keying,deleting keys, resetting ----------------------------------------------------------------------------
        mNCube.tx = 2
        
        mObjectSetAnim.value = False
        mObjectSetAnim.add("{0}.tx".format(mNCube.mNode))
        
        mObjectSetAnim.key()
        self.assertEqual(ATTR.is_keyed(mNCube.mNode,'tx'),
                         True)
        self.assertEqual(ATTR.is_keyed(mNCube.mNode,'ty'),
                         False)        
        
        mObjectSetAnim.deleteKey()
        self.assertEqual(ATTR.is_keyed(mNCube.mNode,'tx'),
                         False) 
        
        mObjectSetAnim.reset()
        self.assertEqual(mNCube.tx,
                         0)

class Test_cgmOptionVar(unittest.TestCase):
    pass

class Test_cgmNode_msgList(unittest.TestCase):    
    def setUp(self):
        
        try:self.mi_catcherObj = cgmMeta.cgmNode('msgListCatcher')
        except:
            self.mi_catcherObj = cgmMeta.cgmNode(name= 'msgListCatcher',nodeType = 'transform')
            TRANS.set_random(self.mi_catcherObj,posLocal = True, rotLocal = True)
            
        
        self.md_msgListObjs = {}
        self.l_strLong = []
        self.l_strShort = []
        self.ml_objs = []
        for i in range(5):
            try:mObj = cgmMeta.cgmNode('msgListTarget_%i'%i)
            except:
                mObj = cgmMeta.cgmNode(name = 'msgListTarget_%i'%i,nodeType = 'transform')
                TRANS.set_random(mObj,posLocal = True, rotLocal = True)
                
            self.md_msgListObjs[i] = mObj
            self.l_strLong.append(mObj.mNode)
            self.l_strShort.append(mObj.p_nameShort)
            self.ml_objs.append(mObj)        
        
    def test_a_connect(self):
        mi_catcher = self.mi_catcherObj
        md_objs = self.md_msgListObjs
        
        #connect
        self.mi_catcherObj.msgList_connect('msgAttr',[md_objs[0],md_objs[1].mNode],'connectBack')
        
        
        #check connections
        self.assertEqual(mi_catcher.msgAttr_0,
                         md_objs[0])
        self.assertEqual(mi_catcher.msgAttr_1.mNode,
                         md_objs[1].mNode)
        self.assertEqual(md_objs[0].connectBack,
                         self.mi_catcherObj)
        
    def test_b_get(self):
        mi_catcher = self.mi_catcherObj
        md_objs = self.md_msgListObjs    
        
        self.assertEqual(mi_catcher.msgList_exists('msgAttr'),True)
        
        self.assertEqual(mi_catcher.msgList_get('msgAttr', asMeta = True),
                         self.ml_objs[:2]
                         )
        self.assertEqual(mi_catcher.msgList_get('msgAttr', asMeta = False),
                         [mObj.p_nameShort for mObj in self.ml_objs[:2]]
                         )     
        
    def test_c_append(self):
        mi_catcher = self.mi_catcherObj
        md_objs = self.md_msgListObjs

        mi_catcher.msgList_append('msgAttr',md_objs[2].mNode,connectBack = 'connectBack')


        self.assertEqual(mi_catcher.msgAttr_2,
                         md_objs[2]
                         )    
        self.assertEqual(md_objs[2].connectBack,
                         mi_catcher)
        
        
        ml_buffer = self.mi_catcherObj.msgList_get('msgAttr',asMeta=True)
        self.assertEqual([mObj.mNode for mObj in ml_buffer],
                         [mObj.mNode for mObj in self.ml_objs[:3]]
                         )
        self.assertEqual(len(ml_buffer),3)
        
        
    def test_d_index(self):
        mi_catcher = self.mi_catcherObj
        md_objs = self.md_msgListObjs
        
        self.assertEqual(mi_catcher.msgList_index('msgAttr',md_objs[0]),
                         0)
        self.assertEqual(mi_catcher.msgList_index('msgAttr',md_objs[1].mNode),
                         1)   
        self.assertEqual(mi_catcher.msgList_index('msgAttr',md_objs[1].mNode),
                         1)            

    def test_e_remove(self):
        mi_catcher = self.mi_catcherObj
        md_objs = self.md_msgListObjs 
        
        mi_catcher.msgList_remove('msgAttr',md_objs[2])
        
        ml_buffer = self.mi_catcherObj.msgList_get('msgAttr')
        
        self.assertEqual(ml_buffer,
                         self.ml_objs[:2])
        self.assertEqual(len(ml_buffer),
                         2)     
        
    def test_f_purge(self):
        mi_catcher = self.mi_catcherObj
        md_objs = self.md_msgListObjs 
        
        mi_catcher.msgList_purge('msgAttr')
        
        ml_buffer = self.mi_catcherObj.msgList_get('msgAttr')
                
        self.assertEqual(ml_buffer,
                         [])
        self.assertEqual(len(ml_buffer),
                         0)            
    
    def test_g_clean(self):
        mi_catcher = self.mi_catcherObj
        md_objs = self.md_msgListObjs
        ml_objs = self.ml_objs    


        mi_catcher.msgList_connect('msgAttr', ml_objs, 'connectBack')
        ATTR.break_connection(mi_catcher.mNode, 'msgAttr_2')#Break it
        
        
        ml_buffer = mi_catcher.msgList_get('msgAttr', cull = True)
        self.assertEqual(len(ml_buffer),
                         4)              
        
        mi_catcher.msgList_clean('msgAttr')
        ml_buffer2 = mi_catcher.msgList_get('msgAttr')
        self.assertEqual(ml_buffer,
                         ml_buffer2)
        self.assertEqual(len(ml_buffer2),
                         4)      
         
    
class Test_cgmNode(unittest.TestCase):                   
    def test_base(self):
        mNode = cgmMeta.cgmNode(name = 'Hogwarts', nodeType = 'transform')
        
        #Name calls ==============================================================================
        self.assertEqual(str(mNode.p_nameBase),'Hogwarts')
        self.assertEqual(str(mNode.p_nameShort),'Hogwarts')
        self.assertEqual(str(mNode.p_nameLong),'|Hogwarts')
        
        mNode.rename('Batman')
        self.assertEqual(str(mNode.p_nameBase),'Batman')

        self.assertEqual(mNode.getReferencePrefix(),False)
        
        #>>Naming calls =========================================================================
        _str_new = 'badabing'
        mNode.addAttr('cgmName',_str_new)
        
        self.assertEqual(mNode.hasAttr('cgmName'),True)
        
        mNode.doName()
        
        self.assertEqual(str(mNode.p_nameBase),_str_new+'_grp')
        
        mNode_target = cgmMeta.cgmNode(name = 'target', nodeType = 'transform')
        mNode_target.doCopyNameTagsFromObject(mNode.mNode)
        
        self.assertEqual(mNode_target.hasAttr('cgmName'),True)        
        self.assertEqual(mNode.cgmName,mNode_target.cgmName)
        
        
        #Destruction =============================================================================
        _str = mNode.getNameShort()
        mNode.delete()
        
        self.assertEqual(mc.objExists(_str),False)
        mc.Undo()
        
    def test_attributeHandling(self):
        _str_func = 'test_attributeHandling'
        
        mObj = cgmMeta.cgmNode(name = 'attrHandlingTest', nodeType = 'transform')
        TRANS.set_random(mObj,posLocal = True, rotLocal = True)
        
        _d_attrTypesToDefaults = {'string':'this_is_a_string',
                                  'float':1.333,
                                  'int':3,
                                  'bool':False,
                                  'double3':[0,0,0]}
        
        
        _short = mObj.mNode
        for t,v in _d_attrTypesToDefaults.iteritems():
            mObj.addAttr("{0}TestFromValue".format(t),v)
            mObj.addAttr("{0}TestNoValue".format(t),attrType=t)
            
            _match = t
            if t == 'float':
                _match = 'double'    
            elif t == 'int':
                _match = 'long'
                
            self.assertEqual(mc.getAttr("{0}.{1}TestFromValue".format(_short,t), type=True),
                             _match)
            self.assertEqual(mc.getAttr("{0}.{1}TestNoValue".format(_short,t), type=True),
                             _match)   
            
            #From Value tests...
            _v = mc.getAttr("{0}.{1}TestFromValue".format(_short,t))            
            if t not in ['double3']:
                self.assertEqual(_v,
                                 v,"{0}.{1}TestFromValue value is wrong {2} != {3}".format(_short,t,_v,v))
            else:
                self.assertEqual(_v,
                                 [(0,0,0)],"{0}.{1}TestFromValue value is wrong {2} != {3}".format(_short,t,_v,v))   
                
            #No value Tests
            _v = mc.getAttr("{0}.{1}TestNoValue".format(_short,t))
            if t in ['string']:
                self.assertEqual(_v,
                                 None,"{0}.{1}TestNoValue value is wrong {2} != None".format(_short,t,_v))                
            elif t != 'double3':
                self.assertEqual(_v,
                                 0,"{0}.{1}TestNoValue value is wrong {2} != None".format(_short,t,_v))    
                
                
        mObj.addAttr('enumTest',enumName='A:B:D:E:F', attrType ='enum',value = 1) #create an enum attribute 
        mObj.addAttr('enumTestNoValue', attrType = 'enum')  #create a string attribute
        
        self.assertEqual( mc.getAttr('{0}.enumTest'.format(_short)),1)
        self.assertEqual( mc.getAttr('{0}.enumTestNoValue'.format(_short)),0)
        
        
        testDict={'jsonFloat':1.05,'jsonInt':3,'jsonString':'string says hello','jsonBool':True}
        mObj.addAttr('jsonTest',testDict,attrType = 'string')     
        self.assertEqual( mc.getAttr('{0}.jsonTest'.format(_short)),
                          '{"jsonFloat": 1.05, "jsonBool": true, "jsonString": "string says hello", "jsonInt": 3}')
  
        
        for a in mc.listAttr(mObj.mNode, ud=True):
            self.assertEqual(mObj.hasAttr(a),True,"attr: {0} failed to find".format(a))
            
            
        #Now check meta calls ===================================================================
        self.assertEqual(mObj.intTestFromValue,3)
        mObj.intTestFromValue = 10
        self.assertEqual(mObj.intTestFromValue,10)
        
        self.assertEqual(mObj.floatTestFromValue,1.333)
        mObj.floatTestFromValue = 3.575
        self.assertEqual(mObj.floatTestFromValue,3.575)  
        
        self.assertEqual(mObj.stringTestFromValue,'this_is_a_string')
        mObj.stringTestFromValue = 'changed to this'
        self.assertEqual(mObj.stringTestFromValue,'changed to this')          

        self.assertEqual(mObj.boolTestFromValue,False)
        mObj.boolTestFromValue = True
        self.assertEqual(mObj.boolTestFromValue,True)
        
        
        self.assertEqual(mObj.enumTest,1)
        mObj.enumTest = 'A'
        self.assertEqual(mObj.enumTest,0)        
        mObj.enumTest = 3
        self.assertEqual(mObj.enumTest,3)  
        
        
        self.assertEqual(mObj.double3TestFromValueX,0)
        mObj.double3TestFromValueX = 1
        self.assertEqual(mObj.double3TestFromValueX,1)  
        mObj.double3TestFromValue = 2,2,2
        self.assertEqual(mObj.double3TestFromValueX,2.0)          
        self.assertEqual(mObj.double3TestFromValue,(2.0,2.0,2.0))  
        
        
        self.assertEqual(type(mObj.jsonTest),dict)
        self.assertEqual(mObj.jsonTest,testDict )
        for k,v in testDict.iteritems():
            self.assertEqual(mObj.jsonTest[k],v)
  
        del(mObj.boolTestFromValue)
        self.assertEqual(mc.objExists(_short),True)
        self.assertEqual(mObj.hasAttr('boolTestFromValue'),False)
        self.assertEqual(mc.attributeQuery('boolTestFromValue',node=_short,exists=True), False)
        mc.undo()
             
        
    def test_messageHandling(self):
        mObj = cgmMeta.cgmNode(name = 'msgHandlingTest', nodeType = 'transform')
        TRANS.set_random(mObj,posLocal = True, rotLocal = True)
        
        _short = mObj.mNode
        
        ml_cubes = []
        for i in range(4):
            _cube =  mc.polyCube(n = 'msgHandlingObj_{0}'.format(i))
            ml_cubes.append(cgmMeta.cgmNode(_cube[0]))
            TRANS.set_random(_cube[0],posLocal = True, rotLocal = True)
        
        #...connect
        mObj.addAttr('msgMultiTest', value=[ml_cubes[0].mNode,ml_cubes[1].mNode,ml_cubes[2].mNode], attrType='message')   #multi Message attr
        mObj.addAttr('msgSingleTest', value=ml_cubes[2].mNode, attrType='messageSimple')    #non-multi message attr
        mObj.addAttr('msgSingleTest2', value=ml_cubes[2].mNode, attrType='messageSimple')    #non-multi message attr
    
        #...check attr data
        for a in ['msgMultiTest','msgSingleTest','msgSingleTest2']:
            self.assertEqual(mObj.hasAttr(a), True, "On: " + a)
            self.assertEqual(mc.getAttr("{0}.{1}".format(_short,a), type=True),'message')
            
            _multi = False
            if a == 'msgMultiTest':
                _multi=True
            self.assertEqual(mc.attributeQuery(a,node=_short, multi=True),_multi)
            
        #...check values
        self.assertEqual(mObj.msgSingleTest, [ml_cubes[2].mNode])
        self.assertEqual(mObj.msgSingleTest, mObj.msgSingleTest2)
        
        self.assertEqual(mObj.msgMultiTest, [o.mNode for o in ml_cubes[:3]])
        self.assertEqual(mObj.getMessage('msgMultiTest',False),[o.p_nameShort for o in ml_cubes[:3]])
        self.assertEqual(mObj.getMessage('msgMultiTest',True),[o.mNode for o in ml_cubes[:3]])
        
        mObj.msgSingleTest2 = ml_cubes[0].mNode
        self.assertEqual(mObj.msgSingleTest2, [ml_cubes[0].mNode])


    def test_datList(self):
        #_str_func = 'test_msgList'
        #log.info("To do...{0}".format(_str_func))     
        #raise NotImplementedError
        pass
    
    def test_nodeTypes_create(self):
        _l = ['transform','objectSet','clamp','setRange',
              'addDoubleLinear','condition','multiplyDivide','plusMinusAverage']
        for t in _l:
            mNode = cgmMeta.cgmNode(name = t + 'CreateByType', nodeType = t)
            if VALID.get_mayaType(mNode.mNode) != t:
                raise Exception,"'{0}' nodeType not created. Type is '{1}'".format(t,VALID.get_mayaType(mNode.mNode))

        
# FUNCTIONS ==================================================================       
def main(**kwargs):
    #testCases = [Test_r9Issues,]
    
    suite = unittest.TestSuite()

    #for testCase in testCases:
        #suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testCase))

    debug = kwargs.get('debug', False)

    if debug:
        suite.debug()
    else:
        unittest.TextTestRunner(verbosity=2).run(suite)