"""
------------------------------------------
cgm_Meta: cgm.core.test.test_coreLib.test_NODEFACTORY
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
# IMPORTS ====================================================================
import unittest
import logging
import unittest.runner
import maya.standalone

try:
    import maya.cmds as mc   
    #from Red9.core import Red9_Meta as r9Meta
    from cgm.core import cgm_Meta as cgmMeta
    import cgm.core.cgm_General as cgmGEN
    from cgm.core.cgmPy import validateArgs as VALID
    import cgm.core.classes.NodeFactory as NODEFACTORY
except ImportError:
    raise StandardError('Test can only be run in Maya')

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)  
    
# CLASSES ====================================================================
class Test_argsToNodes(unittest.TestCase):            
    def test_a_condition(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort
        
        
        arg = "%s.condResult = if %s.ty == 3:5 else 1"%(str_obj,str_obj)
        d_return = NODEFACTORY.argsToNodes(arg).doBuild()
        
        _ml_nodes = d_return.get('ml_nodes')
        _ml_outPlugs = d_return.get('ml_outPlugs')
        _plugCall = mc.listConnections("%s.condResult"%(mObj.mNode),plugs=True,scn = True)
        _combinedName = _ml_outPlugs[0].p_combinedName
        
        
        self.assertIsNotNone(_ml_outPlugs)
        self.assertEqual(len(_ml_outPlugs),1)
        self.assertIsNotNone(_ml_nodes)
        self.assertEqual(len(_ml_nodes),1)   
        
        self.assertEqual(_ml_nodes[0].getMayaType(),
                         'condition')
        
        self.assertEqual(_ml_nodes[0].operation, 0)
        self.assertEqual(str(_plugCall[0]),
                         _combinedName)
        
        mObj.ty = 3
        self.assertEqual(mObj.condResult, 5)
        mObj.ty = 1
        self.assertEqual(mObj.condResult, 1)
        
        return
    
    def test_b_multiInvsersion(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort
        
        arg = "%s.inverseMultThree = 3 * -%s.tx"%(str_obj,str_obj)
        d_return = NODEFACTORY.argsToNodes(arg).doBuild()
        log.debug(d_return['ml_outPlugs'])
        assert d_return['l_nodes'], "Should have made something"
        assert len(d_return['l_nodes']) == 2, "Only two nodes should be made. Found: %s"%len(d_return['l_nodes'])
        assert d_return['ml_nodes'][0].getMayaType() == 'multiplyDivide',"%s != md"%d_return['ml_nodes'][0].getMayaType()
        assert d_return['ml_nodes'][1].getMayaType() == 'multiplyDivide',"%s != md"%d_return['ml_nodes'][1].getMayaType()

        plugCall = mc.listConnections("%s.inverseMultThree"%(mObj.mNode),plugs=True,scn = True)
        assert d_return['ml_nodes'][-1].operation == 1, "Operation not 1"	
        combinedName = d_return['ml_outPlugs'][-1].p_combinedName
        assert str(plugCall[0]) == d_return['ml_outPlugs'][-1].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
        assert mObj.inverseMultThree == 3* -mObj.tx,"Inversion doesn't match"        
        
    def test_c_simpleInvsersion(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort
            
        arg = "%s.simpleInversion = -%s.tx"%(str_obj,str_obj)
        d_return = NODEFACTORY.argsToNodes(arg).doBuild()
        log.debug(d_return['ml_outPlugs'])
        assert d_return['l_nodes'], "Should have made something"
        assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
        assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'multiplyDivide',"%s != pma"%d_return['ml_outPlugs'][0].obj.getMayaType()
        plugCall = mc.listConnections("%s.simpleInversion"%(mObj.mNode),plugs=True,scn = True)
        assert d_return['ml_nodes'][0].operation == 1, "Operation not 1"	
        combinedName = d_return['ml_outPlugs'][0].p_combinedName
        assert str(plugCall[0]) == d_return['ml_outPlugs'][0].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
        assert mObj.simpleInversion == -mObj.tx,"Inversion doesn't match"        
            
    def test_d_average(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort   
        
        arg = "%s.sumAverage1 = 4 >< 4 >< 4"%(str_obj)
        d_return =NODEFACTORY.argsToNodes(arg).doBuild()
        assert d_return['l_nodes'], "Should have made something"
        assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
        assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'plusMinusAverage',"%s != pma"%d_return['ml_outPlugs'][0].obj.getMayaType()
        assert d_return['ml_nodes'][0].operation == 3, "Operation not 3"

        assert mObj.sumAverage1 == 4,"Average is wrong: 4 != %s"%mObj.sumAverage1        
            
    def test_e_directConnect(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort
        
        arg = "%s.directConnect = %s.ty"%(str_obj,str_obj)
        NODEFACTORY.argsToNodes(arg).doBuild()
        log.debug(mc.listConnections("%s.directConnect"%str_obj,source = True,scn = True))
        plugCall = mc.listConnections("%s.directConnect"%(mObj.mNode),plugs=True,scn = True)	
        assert plugCall[0] == '%s.translateY'%mObj.getShortName(),log.error("Direct connect failed. Plug call:{0}".format(plugCall))
        
            
    def test_f_multiConnect(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort
        
        arg = "%s.directConnect, %s.ry = %s.ty"%(str_obj,str_obj,str_obj)
        NODEFACTORY.argsToNodes(arg).doBuild()
        log.debug(mc.listConnections("%s.directConnect"%str_obj,source = True,scn = True))
        plugCall = mc.listConnections("%s.directConnect"%(mObj.mNode),plugs=True,scn = True)	
        assert plugCall[0] == '%s.translateY'%mObj.getShortName(),log.error("Direct connect failed: directConnect")
        plugCall = mc.listConnections("%s.rotateY"%(mObj.mNode),plugs=True,scn = True)	
        log.debug(plugCall)
        assert plugCall[0] == '%s.translateY'%mObj.getShortName(),log.error("Direct connect failed: rotateY")
            
    def test_g_sum(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort
        
        mObj.tx = 1
        mObj.ty = 2
        mObj.tz = 3
        arg = "%s.sumResult1 = %s.tx - %s.ty - %s.tz"%(str_obj,str_obj,str_obj,str_obj)
        d_return =NODEFACTORY.argsToNodes(arg).doBuild()
        log.debug(d_return['ml_outPlugs'])
        assert d_return['l_nodes'], "Should have made something"
        assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
        assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'plusMinusAverage',"%s != pma"%d_return['ml_outPlugs'][0].obj.getMayaType()
        plugCall = mc.listConnections("%s.sumResult1"%(mObj.mNode),plugs=True,scn = True)
        assert d_return['ml_nodes'][0].operation == 2, "Operation not 2"	
        combinedName = d_return['ml_outPlugs'][0].p_combinedName
        assert str(plugCall[0]) == d_return['ml_outPlugs'][0].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
        assert mObj.sumResult1 == mObj.tx - mObj.ty - mObj.tz,"Sum doesn't match"        
            
    def test_h_clamp(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort
        
        mObj.tz = 3
        arg = "%s.clampResult = clamp(0,1,%s.tz"%(str_obj,str_obj)
        d_return =NODEFACTORY.argsToNodes(arg).doBuild()
        log.debug(d_return['ml_outPlugs'])
        assert d_return['l_nodes'], "Should have made something"
        assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
        assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'clamp',"%s != clamp"%d_return['ml_outPlugs'][0].obj.getMayaType()
        plugCall = mc.listConnections("%s.clampResult"%(mObj.mNode),plugs=True,scn = True)
        combinedName = d_return['ml_outPlugs'][0].p_combinedName
        assert str(plugCall[0]) == d_return['ml_outPlugs'][0].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
        assert mObj.clampResult == 1,"Value 1 fail"
        mObj.tz = .5
        assert mObj.clampResult == .5,"Value 2 fail"
        
    def test_i_range(self):
        try:mObj = cgmMeta.cgmObject('argsToNodes_catch')
        except:mObj = cgmMeta.cgmObject(name = 'argsToNodes_catch')
        str_obj = mObj.p_nameShort
        
        mObj.tz = 5
        arg = "%s.setRangeResult = setRange(0,1,0,10,%s.tz"%(str_obj,str_obj)
        d_return =NODEFACTORY.argsToNodes(arg).doBuild()
        log.debug(d_return['ml_outPlugs'])
        assert d_return['l_nodes'], "Should have made something"
        assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
        assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'setRange',"%s != setRange"%d_return['ml_outPlugs'][0].obj.getMayaType()
        plugCall = mc.listConnections("%s.setRangeResult"%(mObj.mNode),plugs=True,scn = True)
        combinedName = d_return['ml_outPlugs'][0].p_combinedName
        assert str(plugCall[0]) == d_return['ml_outPlugs'][0].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
        assert mObj.setRangeResult == .5,"Value 1 fail"
        mObj.tz = 10
        assert mObj.setRangeResult == 1,"Value 2 fail"        
        
            
    def holder(self):
        mObj = cgmMeta.cgmObject(name = 'awesomeArgObj_loc')
        str_obj = mObj.getShortName()
    

    
        try:#Mult inversion
            arg = "%s.inverseMultThree = 3 * -%s.tx"%(str_obj,str_obj)
            d_return =NODEFACTORY.argsToNodes(arg).doBuild()
            log.debug(d_return['ml_outPlugs'])
            assert d_return['l_nodes'], "Should have made something"
            assert len(d_return['l_nodes']) == 2, "Only two nodes should be made. Found: %s"%len(d_return['l_nodes'])
            assert d_return['ml_nodes'][0].getMayaType() == 'multiplyDivide',"%s != md"%d_return['ml_nodes'][0].getMayaType()
            assert d_return['ml_nodes'][1].getMayaType() == 'multiplyDivide',"%s != md"%d_return['ml_nodes'][1].getMayaType()
    
            plugCall = mc.listConnections("%s.inverseMultThree"%(mObj.mNode),plugs=True,scn = True)
            assert d_return['ml_nodes'][-1].operation == 1, "Operation not 1"	
            combinedName = d_return['ml_outPlugs'][-1].p_combinedName
            assert str(plugCall[0]) == d_return['ml_outPlugs'][-1].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
            assert mObj.inverseMultThree == 3* -mObj.tx,"Inversion doesn't match"
    
        except StandardError,error:
            log.error("test_argsToNodes>>Inversion mult 3 Failure! '%s'"%(error))
            raise StandardError,error      
    
        try:#Simple inversion 
            arg = "%s.simpleInversion = -%s.tx"%(str_obj,str_obj)
            d_return =NODEFACTORY.argsToNodes(arg).doBuild()
            log.debug(d_return['ml_outPlugs'])
            assert d_return['l_nodes'], "Should have made something"
            assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
            assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'multiplyDivide',"%s != pma"%d_return['ml_outPlugs'][0].obj.getMayaType()
            plugCall = mc.listConnections("%s.simpleInversion"%(mObj.mNode),plugs=True,scn = True)
            assert d_return['ml_nodes'][0].operation == 1, "Operation not 1"	
            combinedName = d_return['ml_outPlugs'][0].p_combinedName
            assert str(plugCall[0]) == d_return['ml_outPlugs'][0].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
            assert mObj.simpleInversion == -mObj.tx,"Inversion doesn't match"
    
        except StandardError,error:
            log.error("test_argsToNodes>>Simple inversion Failure! '%s'"%(error))
            raise StandardError,error  
    
        try:#Simple Average 
            arg = "%s.sumAverage1 = 4 >< 4 >< 4"%(str_obj)
            d_return =NODEFACTORY.argsToNodes(arg).doBuild()
            assert d_return['l_nodes'], "Should have made something"
            assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
            assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'plusMinusAverage',"%s != pma"%d_return['ml_outPlugs'][0].obj.getMayaType()
            assert d_return['ml_nodes'][0].operation == 3, "Operation not 3"
    
            assert mObj.sumAverage1 == 4,"Average is wrong: 4 != %s"%mObj.sumAverage1
    
        except StandardError,error:
            log.error("test_argsToNodes>>Simple sum Failure! '%s'"%(error))
            raise StandardError,error      
    
        try:#Test direct connect
            arg = "%s.directConnect = %s.ty"%(str_obj,str_obj)
            NODEFACTORY.argsToNodes(arg).doBuild()
            log.debug(mc.listConnections("%s.directConnect"%str_obj,source = True,scn = True))
            plugCall = mc.listConnections("%s.directConnect"%(mObj.mNode),plugs=True,scn = True)	
            assert plugCall[0] == '%s.translateY'%mObj.getShortName(),log.error("Direct connect failed. Plug call:{0}".format(plugCall))
        except StandardError,error:
            log.error("test_argsToNodes>>Single Connect Failure! '%s'"%(error))
            raise StandardError,error   
    
        try:#Multi direct connect
            arg = "%s.directConnect, %s.ry = %s.ty"%(str_obj,str_obj,str_obj)
            NODEFACTORY.argsToNodes(arg).doBuild()
            log.debug(mc.listConnections("%s.directConnect"%str_obj,source = True,scn = True))
            plugCall = mc.listConnections("%s.directConnect"%(mObj.mNode),plugs=True,scn = True)	
            assert plugCall[0] == '%s.translateY'%mObj.getShortName(),log.error("Direct connect failed: directConnect")
            plugCall = mc.listConnections("%s.rotateY"%(mObj.mNode),plugs=True,scn = True)	
            log.debug(plugCall)
            assert plugCall[0] == '%s.translateY'%mObj.getShortName(),log.error("Direct connect failed: rotateY")
    
        except StandardError,error:
            log.error("test_argsToNodes>>Multi Connect Failure! '%s'"%(error))
            raise StandardError,error  
    
        try:#Simple sum 
            mObj.tx = 1
            mObj.ty = 2
            mObj.tz = 3
            arg = "%s.sumResult1 = %s.tx - %s.ty - %s.tz"%(str_obj,str_obj,str_obj,str_obj)
            d_return =NODEFACTORY.argsToNodes(arg).doBuild()
            log.debug(d_return['ml_outPlugs'])
            assert d_return['l_nodes'], "Should have made something"
            assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
            assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'plusMinusAverage',"%s != pma"%d_return['ml_outPlugs'][0].obj.getMayaType()
            plugCall = mc.listConnections("%s.sumResult1"%(mObj.mNode),plugs=True,scn = True)
            assert d_return['ml_nodes'][0].operation == 2, "Operation not 2"	
            combinedName = d_return['ml_outPlugs'][0].p_combinedName
            assert str(plugCall[0]) == d_return['ml_outPlugs'][0].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
            assert mObj.sumResult1 == mObj.tx - mObj.ty - mObj.tz,"Sum doesn't match"
    
        except StandardError,error:
            log.error("test_argsToNodes>>Simple sum Failure! '%s'"%(error))
            raise StandardError,error   
    
        try:#clamp 
            mObj.tz = 3
            arg = "%s.clampResult = clamp(0,1,%s.tz"%(str_obj,str_obj)
            d_return =NODEFACTORY.argsToNodes(arg).doBuild()
            log.debug(d_return['ml_outPlugs'])
            assert d_return['l_nodes'], "Should have made something"
            assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
            assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'clamp',"%s != clamp"%d_return['ml_outPlugs'][0].obj.getMayaType()
            plugCall = mc.listConnections("%s.clampResult"%(mObj.mNode),plugs=True,scn = True)
            combinedName = d_return['ml_outPlugs'][0].p_combinedName
            assert str(plugCall[0]) == d_return['ml_outPlugs'][0].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
            assert mObj.clampResult == 1,"Value 1 fail"
            mObj.tz = .5
            assert mObj.clampResult == .5,"Value 2 fail"
    
        except StandardError,error:
            log.error("test_argsToNodes>>Clamp fail! '%s'"%(error))
            raise StandardError,error       
    
        try:#setRange 
            mObj.tz = 5
            arg = "%s.setRangeResult = setRange(0,1,0,10,%s.tz"%(str_obj,str_obj)
            d_return =NODEFACTORY.argsToNodes(arg).doBuild()
            log.debug(d_return['ml_outPlugs'])
            assert d_return['l_nodes'], "Should have made something"
            assert len(d_return['l_nodes']) == 1, "Only one node should be made. Found: %s"%len(d_return['l_nodes'])
            assert d_return['ml_outPlugs'][0].obj.getMayaType() == 'setRange',"%s != setRange"%d_return['ml_outPlugs'][0].obj.getMayaType()
            plugCall = mc.listConnections("%s.setRangeResult"%(mObj.mNode),plugs=True,scn = True)
            combinedName = d_return['ml_outPlugs'][0].p_combinedName
            assert str(plugCall[0]) == d_return['ml_outPlugs'][0].p_combinedName,"Connections don't match: %s | %s"%(plugCall[0],combinedName)
            assert mObj.setRangeResult == .5,"Value 1 fail"
            mObj.tz = 10
            assert mObj.setRangeResult == 1,"Value 2 fail"
    
        except StandardError,error:
            log.error("test_argsToNodes>>setRangeResult failure! '%s'"%(error))
            raise StandardError,error   
    
        if deleteObj:mObj.delete()
        """
        for arg in ["awesomeArgObj_loc.tx + awesomeArgObj_loc.ty + awesomeArgObj_loc.tz = awesomeArgObj_loc.sumResult1",
                    "1 + 2 + 3 = awesomeArgObj_loc.simpleSum",#Working
                    "1 >< 2 >< 3 = awesomeArgObj_loc.simpleAv",#Working
                    "3 * -awesomeArgObj_loc.ty = awesomeArgObj_loc.inverseMultThree",#Working
                    "4 - 2 = awesomeArgObj_loc.simpleMathResult",#Working
                    "-awesomeArgObj_loc.ty = awesomeArgObj_loc.ty",#Working
                    "awesomeArgObj_loc.ty * 3 = awesomeArgObj_loc.multResult",#Working
                    "awesomeArgObj_loc.ty + 3 + awesomeArgObj_loc.ty = awesomeArgObj_loc.sumResult",#Working
                    "if awesomeArgObj_loc.ty > 3;awesomeArgObj_loc.result2"]:
        try:nodeF.argsToNodes(arg).doBuild()
        except StandardError,error:
            log.error("test_argsToNodes>>arg fail! %s"%arg)
            raise StandardError,error  """        
