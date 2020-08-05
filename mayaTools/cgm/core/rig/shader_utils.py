"""
------------------------------------------
shader_utils: cgm.core.lib
Author: Josh Burton & David Bokser
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
__MAYALOCAL = 'SHADERS'

# From Python =============================================================
import copy
import re
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
import cgm.core.cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID

from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as coreNames
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import transform_utils as TRANS
import cgm.core.lib.name_utils as NAMES



def create_uvPickerNetwork(target = None,
                           name = 'iris',
                           mode = 1,
                           enums = None,
                           count = 9, split = 3):
    _str_func = 'create_uvPickerNetwork'
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)

    if count/split != split:
        raise ValueError,"{0} || Split must divide evently to count. count: {1} | split: {2}".format(_str_func,count,split)
    
    if not target:
        target = mc.group(em=True,name='uvPickerDefault')
    
    
    if mode == 2:
        log.debug(cgmGen.logString_msg(_str_func,'2 Attr mode'))
        
        if not enums:
            enums = ['{0}_{1}'.format(name,i) for i in range(2)]
            
        for a in enums:
            ATTR.add(target,a,'enum',enumOptions=[str(i) for i in range(split)])
            
            
        for a in 'U','V':
            _a = 'res_{0}{1}'.format(name,a)
            ATTR.add(target,_a,'float',keyable=False,hidden=False)
            ATTR.set_hidden(target,_a,False)    
        
        mMD = cgmMeta.cgmNode(name = "{0}_picker_md".format(name),
                                nodeType = 'multiplyDivide')
        mMD.operation = 2
        mMD.input2X = split
        mMD.input2Y = split
        
        
        mMD.doConnectIn('input1X', "{0}.{1}".format(target,enums[0]))
        mMD.doConnectIn('input1Y', "{0}.{1}".format(target,enums[1]))
        
        
        mMD.doConnectOut('outputX', '{0}.res_{1}U'.format(target,name))
        mMD.doConnectOut('outputY', '{0}.res_{1}V'.format(target,name))
    else:
        log.debug(cgmGen.logString_msg(_str_func,'1 Attr mode'))
        
        _d_values = {9:[[.999,.666],
                        [.333,.666],
                        [.666,.666],
                        [.999,.333],
                        [.333,.333],
                        [.666,.333],
                        [.999,.999],
                        [.333,.999],
                        [.666,.999],
                        ]}
        
        l_dat = _d_values.get(count)
        if not l_dat:
            raise ValueError,"{0} | count {1} not supported".format(_str_func,count)
        
        
        
        for a in 'U','V':
            _a = 'res_{0}{1}'.format(name,a)
            ATTR.add(target,_a,'float',keyable=False,hidden=False)
            ATTR.set_hidden(target,_a,False)
            
        mPMA = cgmMeta.cgmNode(name = "{0}_picker_pma".format(name),
                                nodeType = 'plusMinusAverage')
        mPMA.operation = 1
            
        ATTR.add(target,name,'enum',enumOptions=[str(i) for i in range(9)])
        mAttr = cgmMeta.cgmAttr(target,name)
        
        for i,vSet in enumerate(l_dat):
            _iterBase = "{0}_{1}".format(name,i)
            
            if mc.objExists('%s_condNode'%_iterBase):
                mc.delete('%s_condNode'%_iterBase)
            
            mNode = cgmMeta.cgmNode(name = "{0}_condNode".format(_iterBase),
                                    nodeType = 'condition') 
            
    
            mNode.secondTerm = i
            mNode.colorIfTrueR = vSet[0]
            mNode.colorIfTrueG = vSet[1]
            
            mNode.colorIfFalseR = 0
            mNode.colorIfFalseG = 0
            
    
            mAttr.doConnectOut('%s.firstTerm'%mNode.mNode)
            ATTR.connect('%s.outColor'%mNode.mNode, "{0}.input3D[{1}]".format(mPMA.mNode,i))
            #attributes.doConnectAttr('%s.outColorR'%mNode.mNode,'%s.%s'%(c,self.connectToAttr))         
    
        mPMA.doConnectOut('output3Dx', '{0}.res_{1}U'.format(target,name))
        mPMA.doConnectOut('output3Dy', '{0}.res_{1}V'.format(target,name))



def create_uvPickerNetworkBAK(target = None, name = 'iris', split = 9):
    _str_func = 'create_uvPickerNetwork'
    log.debug("|{0}| >> ".format(_str_func)+ '-'*80)
    
    _d_values = {9:[[.999,.666],
                    [.333,.666],
                    [.666,.666],
                    [.999,.333],
                    [.333,.333],
                    [.666,.333],
                    [.999,.999],
                    [.333,.999],
                    [.666,.999],
                    ]}
    
    l_dat = _d_values.get(split)
    if not l_dat:
        raise ValueError,"{0} | split {1} not supported".format(_str_func,split)
    
    if not target:
        target = mc.group(em=True,name='uvPickerDefault')
    
    md_pmas = {}
    
    for a in 'U','V':
        _a = '{0}{1}'.format(name,a)
        ATTR.add(target,_a,'float',keyable=False,hidden=False)
        ATTR.set_hidden(target,_a,False)
        
        #if mc.objExists('%s_pma'%_iterBase):
            #mc.delete('%s_condNode'%_iterBase)
            
        mPMA = cgmMeta.cgmNode(name = "{0}_pma".format(_iterBase),
                                nodeType = 'plusMinusAverage')
        mPMA.operation = 1
        md_pmas[a] = mPMA
        
    ATTR.add(target,name,'enum',enumOptions=[str(i) for i in range(9)])
    mAttr = cgmMeta.cgmAttr(target,name)
    
    
    #Pma nodes -------------------------------------------------    
    #Condition loop ----------------------------------------
    #place 2d texture = number of rolls 
    for i,vSet in enumerate(l_dat):
        _iterBase = "{0}_{1}".format(name,i)
        
        if mc.objExists('%s_condNode'%_iterBase):
            mc.delete('%s_condNode'%_iterBase)
        
        mNode = cgmMeta.cgmNode(name = "{0}_condNode".format(_iterBase),
                                nodeType = 'condition') 
        

        mNode.secondTerm = i
        mNode.colorIfTrueR = vSet[0]
        mNode.colorIfTrueR = vSet[1]
        
        mNode.colorIfFalseR = 0
        mNode.colorIfFalseG = 0
        
        #attributes.doSetAttr(i_node.mNode,'colorIfTrueR',1)
        #attributes.doSetAttr(i_node.mNode,'colorIfFalseR',0)
        #i_node.colorIfTrueR = 1
        #i_node.colorIfTrueR = 0

        mAttr.doConnectOut('%s.firstTerm'%i_node.mNode)
        attributes.doConnectAttr('%s.outColorR'%i_node.mNode,'%s.%s'%(c,self.connectToAttr))        

    
    
        
        
    
    
    
    
    


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
            log.debug("Chooser Network good to go")

    def buildNetwork(self,*args,**kws):
        if kws:log.debug("kws: %s"%str(kws))
        if args:log.debug("args: %s"%str(args))

        #children = self.i_group.getChildren()
        mChildren = self.i_group.getChildren(asMeta=True)
        children = [mObj.p_nameShort for mObj in mChildren]
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
    
    
def shaderDat_get(nodes = []):
    if not nodes:
        nodes = mc.ls(sl=1)
        
    _res = {}
    mNodes = cgmMeta.asMeta(nodes)
    for mNode in mNodes:
        _node = mNode.mNode
        try:
            _d = {}
            
            for a in mNode.getAttrs():
                try:
                    
                    if ATTR.get_driver(_node,a):
                        continue
                    _d[a] = mNode.getMayaAttr(a)
                except Exception,err:
                    log.error("{0} | {1}".format(mNode,err))
            
            _res[mNode.mNode] = _d
            
        except Exception,err:
            log.error("{0} | {1}".format(mNode,err))
    pprint.pprint(_res)
    return _res

def shaderDat_set(dat = {},  key = None, nodes = []):
    _d = dat.get(key,False)
    if not _d:
        return False
    
    if not nodes:
        nodes = mc.ls(sl=1)
    _res = {}
    mNodes = cgmMeta.asMeta(nodes)
    
    for node in nodes:
        for a,v in _d.iteritems():
            if a  in ['color']:
                continue
            log.info(node)
            try:
                log.info('{0} --> {1}'.format(a,v))
                ATTR.set(node,a,v)
            except Exception,err:
                log.error("{0} | {1}".format(node,err))
            
            
