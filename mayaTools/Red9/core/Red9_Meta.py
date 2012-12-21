'''
------------------------------------------
Red9 Studio Pack: Maya Pipeline Solutions
Author: Mark Jackson
email: rednineinfo@gmail.com

Red9 blog : http://red9-consultancy.blogspot.co.uk/
MarkJ blog: http://markj3d.blogspot.co.uk
------------------------------------------

This is the Core of the MetaNode implementation of the systems. 

NOTE: if you're inheriting from 'MetaClass' in your own class you
need to make sure that the registerMClassInheritanceMapping() is called
such that the global RED9_META_REGISTERY is rebuilt and includes 
your inherited class.

================================================================


#===============================================================
# Basic MetaClass Use:
#===============================================================

    Now moved to the examples folder for more detailed explanations
    ..\Red9\examples\MetaData_Getting_started.py
    ..\Red9\examples\MetaRig_Morpheus.py
    
    Also see the unittesting folder to see what the code can do and
    what each function is expected to return
    ..\Red9\tests
'''


import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
from functools import partial

import Red9_General as r9General
import Red9.startup.setup as r9Setup

'''
#=============================================
NOTE: we can't import anything else here that imports this
Module as it screw the Class Registry and we get Cyclic imports
hence the r9Anim is LazyLoaded where needed
import Red9_AnimationUtils as r9Anim 
#=============================================
'''

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

try:
    import json as json
except:
    #Meta Fails under Maya2009 because of Python2.5 issues
    log.warning('json is not supported in Python2.5')
    #import Red9.packages.simplejson as json
    
'''    
# CRUCIAL - REGISTER INHERITED CLASSES! ==============================================    
Register available MetaClass's to a global so that other modules could externally
extend the functionality and use the base MetaClass. Note we're building this up 
from only those active Python classes who inherit from MetaClass
global RED9_META_REGISTERY 
# ==================================================================================== 
'''     
def registerMClassInheritanceMapping():
    global RED9_META_REGISTERY
    RED9_META_REGISTERY={}
    RED9_META_REGISTERY['MetaClass']=MetaClass
    for mclass in r9General.itersubclasses(MetaClass):
        RED9_META_REGISTERY[mclass.__name__]=mclass
  
def printSubClassRegistry():
    for m in RED9_META_REGISTERY:print m
    
def registerMClassNodeMapping(nodeTypes='network'):
    '''
    Hook to allow you to extend the type of nodes included in all the
    getMeta searches. Allows you to expand into using nodes of any type
    as metaNodes
    @param nodeTypes: allows you to expand metaData and use any nodeType
                    default is always 'network'
    NOTE: 
        this now validates 'nodeTypes' against Maya registered nodeTypes before being 
        allowed into the registry. Why, well lets say you have a new nodeType from a 
        plugin but that plugin isn't currently loaded, this now stops that type being 
        generically added by any custom boot sequence.
    '''
    global RED9_META_NODETYPE_REGISTERY
    MayaRegisteredNodes=cmds.allNodeTypes()
    
    RED9_META_NODETYPE_REGISTERY=['network']
    if not type(nodeTypes)==list:nodeTypes=[nodeTypes]
    for nType in nodeTypes:
        if not nType in RED9_META_NODETYPE_REGISTERY and nType in MayaRegisteredNodes:
            log.debug('nodeType : %s : added to NODETYPE_REGISTRY')
            RED9_META_NODETYPE_REGISTERY.append(nType)
  
def printMetaTypeRegistry():
    for t in RED9_META_NODETYPE_REGISTERY:print t
    
def getMClassNodeTypes():
    '''
    Generic getWrapper for all nodeTypes registered in the Meta_NodeType global
    '''    
    return RED9_META_NODETYPE_REGISTERY 


#------------------------------------------------------------------------------   
    
def attributeDataType(val):
    '''
    Validate the attribute type for all the cmds handling
    '''
    if issubclass(type(val),str):
        log.debug('Val : %s : is a string' % val)
        return 'string'
    if issubclass(type(val),bool):
        log.debug('Val : %s : is a bool')
        return 'bool'
    if issubclass(type(val),int):
        log.debug('Val : %s : is a int')
        return 'int'
    if issubclass(type(val),float):
        log.debug('Val : %s : is a float')
        return 'float'
    if issubclass(type(val),dict):
        log.debug('Val : %s : is a dict')
        return 'complex'
    if issubclass(type(val),list):
        log.debug('Val : %s : is a list')
        return 'complex'
    if issubclass(type(val),tuple):
        log.debug('Val : %s : is a tuple')
        return 'complex'
 
def isMetaNode(node, mTypes=[]):
    '''
    Simple bool, Maya Node is or isn't an mNode
    NOTE: this does not instantiate the mClass to query it like the
    isMetaNodeInherited which has to figure the subclass mapping
    @param node: Maya node to test
    @param mTypes: only match given MetaClass's
    '''
    if mTypes and not type(mTypes)==list:mTypes=[mTypes]
    if issubclass(type(node),MetaClass):
        node=node.mNode    
    if cmds.attributeQuery('mClass', exists=True, node=node):
        mClass=cmds.getAttr('%s.%s' % (node,'mClass'))
        if RED9_META_REGISTERY.has_key(mClass):
            if mTypes:
                if mClass in mTypes:
                    return True
            else:
                return True
        else:
            log.debug('isMetaNode>>InValid MetaClass attr : %s' % mClass) 
            return False
    else:
        return False

def isMetaNodeInherited(node, mInstances=[]):
    '''
    unlike isMetaNode which checks the node against a particular MetaClass,
    this expands the check to see if the node is inherited from or a subclass of
    a given Meta base class, ie, part of a system
    TODO : we COULD return the instantiated metaClass object here rather than just a bool??
    '''
    if not type(mInstances)==list:mInstances=[mInstances]
    if isMetaNode(node):
        mClass=MetaClass(node) #instantiate the metaClass so we can work out subclass mapping
        for inst in mInstances:
            print inst, RED9_META_REGISTERY[inst],type(mClass)
            if issubclass(type(mClass), RED9_META_REGISTERY[inst]):
                log.debug('MetaNode %s is of subclass >> %s' % (mClass,inst))
                return True
            
@r9General.Timer                 
def getMetaNodes(dataType='mClass', mTypes=[], mInstances=[]):
    '''
    Get all mClass nodes in scene and return as mClass objects if possible
    @param dataType: default='mClass' return the nodes already instantiated to 
                the correct class object. If not then return the Maya node itself
    @param mTypes: only return meta nodes of a given type
    @param mInstances: idea - this will check subclass inheritance, ie, MetaRig would
            return ALL nodes who's class is inherited from MetaRig. Allows you to 
            group the data more efficiently by base classes and their inheritance
    '''
    mNodes=[]
    if mTypes and not type(mTypes)==list:mTypes=[mTypes]
    for node in cmds.ls(type=getMClassNodeTypes(),l=True):
        if not mInstances:
            if isMetaNode(node, mTypes=mTypes):
                mNodes.append(node)
        else:
            if isMetaNodeInherited(node,mInstances):
                mNodes.append(node)

    if dataType=='mClass':
        return[MetaClass(node) for node in mNodes]
    else:
        return mNodes
 
@r9General.Timer           
def getConnectedMetaNodes(nodes, source=True, destination=True, dataType='mClass', mTypes=[], mInstances=[]):
    '''
    From a given set of Maya Nodes return all connected mNodes
    Default return is mClass objects
    @param nodes: nodes to inspect for connected meta data 
    @param source: `bool` clamp the search to the source side of the graph
    @param destination: `bool` clamp the search to the destination side of the graph
    @param dataType: default='mClass' return the nodes already instantiated to 
                    the correct class object. If not then return the Maya node
    @param mTypes: return only given MetaClass's
    @param mInstances: idea - this will check subclass inheritance, ie, MetaRig would
            return ALL nodes who's class is inherited from MetaRig. Allows you to 
            group the data more efficiently by base classes and their inheritance
    '''
    mNodes=[]
    if mTypes and not type(mTypes)==list:mTypes=[mTypes]
    #nodes=cmds.listConnections(nodes,type='network',s=source,d=destination)
    connections=[]
    for nType in getMClassNodeTypes():
        con=cmds.listConnections(nodes,type=nType,s=source,d=destination)
        if con:
            connections.extend(con)
    
    if not connections:
        return mNodes
    for node in connections:
        if not mInstances:
            if isMetaNode(node, mTypes=mTypes):
                mNodes.append(node)
        else:
            if isMetaNodeInherited(node,mInstances):
                mNodes.append(node)
            
    if dataType=='mClass':
        return [MetaClass(node) for node in set(mNodes)]
    else:
        return set(mNodes)
    
    
def getConnectedMetaRig(node):
    '''
    just in case anybody is running this, will help the transition to the new func
    '''
    raise DeprecationWarning('Deprecated function, replaced with a more generic "getConnectedMetaSystemRoot()"')

    
def getConnectedMetaSystemRoot(node):
    '''
    From a given node see if it's part of a MetaData system, if so
    walk up the parent tree till you get to top meta node and return the class. 
    '''
    mNodes=getConnectedMetaNodes(node)
    if not mNodes:
        return
    else:
        mNode=mNodes[0]
    if type(mNode)==MetaRig:
        return mNode
    else: 
        runaways=0
        while mNode and not runaways==100:
            log.debug('walking network : %s' % mNode.mNode)
            parent=mNode.getParentMetaNode()
            if not parent:
                log.debug('node is top of tree : %s' % mNode)
                return mNode
            runaways+=1
            mNode=parent
        
         

class MClassNodeUI():
    '''
    Simple UI to display all MetaNodes in the scene
    '''
    def __init__(self, mTypes=None, mInstances=None, closeOnSelect=False, \
                 funcOnSelection=None, sortBy='byClass', allowMulti=True):
        '''
        @param mNodeType: MetaNode class to search and display 'MetaRig'
        @param closeOnSelect: on text select close the UI
        @param funcOnSelection: function to run where the selected mNode is expected
            as first arg, ie funcOnSelection=cmd.select so that when run the item is 
            selected in the UI cmds.select(item) is run. Basically used as a dynamic callback
        @param sortBy: Sort the nodes found 'byClass' or 'byName' 
        '''
        self.mInstances=mInstances
        self.mTypes=mTypes
        self.closeOnSelect=closeOnSelect
        self.func=funcOnSelection #Given Function to run on the selected node when UI selected
        self.sortBy=sortBy
        self.allowMulti=allowMulti
        
        self.win = 'MetaClassFinder'
        self.mNodes=None 
        
    @classmethod
    def show(cls):
        cls()._showUI()
        
    def _showUI(self):
        if cmds.window(self.win, exists=True): cmds.deleteUI(self.win, window=True)
        window = cmds.window(self.win , title=self.win) #, widthHeight=(260, 220))

        cmds.columnLayout(adjustableColumn=True)
        cmds.separator(h=15, style='none')
        txt=self.mTypes
        if not self.mTypes:
                txt='All'
        cmds.text(label='Scene MetaNodes of type : %s' % txt)
        cmds.separator(h=15, style='none')
        if not self.allowMulti:
            cmds.textScrollList('slMetaNodeList',font="fixedWidthFont")
        else:
            cmds.textScrollList('slMetaNodeList',font="fixedWidthFont", allowMultiSelection=True)
        cmds.popupMenu('r9MetaNodeUI_Popup')
        cmds.menuItem(label='SortBy : ClassName', command=partial(self.fillScroll,'byClass'))
        cmds.menuItem(label='SortBy : NodeName', command=partial(self.fillScroll,'byName'))
        #cmds.menuItem(label='SortBy : SystemTree', command=partial(self.fillScroll,'bySystemTree'))
        cmds.menuItem(label='Graph Selected Networks', command=partial(self.graphNetwork))
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Class : All Registered', command=partial(self.fillScroll,'byName'))
        for mCls in sorted(RED9_META_REGISTERY):
            cmds.menuItem(label='Class : %s' % mCls, command=partial(self.fillScroll,'byName', mCls))
        
        cmds.button(label='Refresh', command=partial(self.fillScroll))
        cmds.separator(h=15,style='none') 
        cmds.iconTextButton( style='iconOnly', bgc=(0.7,0,0),image1='Rocket9_buttonStrap2.bmp',
                                 c=lambda *args:(r9Setup.red9ContactInfo()),h=22,w=200 )
        cmds.showWindow(window)
        self.fillScroll()
 
    def graphNetwork(self,*args):
        if r9Setup.mayaVersion()<2013:
            mel.eval('hyperGraphWindow( "", "DG")')
        else:
            mel.eval('NodeEditorWindow;NodeEditorGraphUpDownstream;')
            #mel.eval('hyperGraphWindow( "", "DG")')
        
    def selectCmd(self,*args):
        indexes=cmds.textScrollList('slMetaNodeList',q=True,sii=True)      
        if indexes:
            cmds.select(cl=True)
        for i in indexes:
            node=self.mNodes[i - 1]
            log.debug('selected : %s' % node)
            
            #func is a function passed into the UI via the funcOnSelection arg
            #this allows external classes to use this as a signal call on select
            if self.func:
                self.func(node.mNode)
            else:    
                cmds.select(node.mNode,add=True)
                
        if self.closeOnSelect:
            cmds.deleteUI('MetaClassFinder',window=True)
        
    def doubleClick(self):
        '''
        run the generic meta.getChildren call and select the results
        '''
        cmds.select(cl=True)
        cmds.select(self.mNodes[cmds.textScrollList('slMetaNodeList',q=True,sii=True)[0]-1].getChildren(walk=True))
        
    def fillScroll(self, sortBy=None, mClassToShow=None, *args):
        cmds.textScrollList('slMetaNodeList', edit=True, ra=True)
        if mClassToShow:
            self.mNodes=getMetaNodes(mTypes=mClassToShow,mInstances=None)
        else:
            mClassToShow=self.mTypes
            self.mNodes=getMetaNodes(mTypes=mClassToShow,mInstances=self.mInstances)
            
        if not sortBy: sortBy=self.sortBy
          
        if sortBy=='byClass':
            self.mNodes=sorted(self.mNodes, key=lambda x: x.mClass.upper())
        elif sortBy=='byName':
            self.mNodes=sorted(self.mNodes, key=lambda x: x.mNode.upper())

        if self.mNodes:
            width=len(self.mNodes[0].mNode)
            #figure out the width of the first cell
            for meta in self.mNodes:
                if len(meta.mNode)>width:
                    width=len(meta.mNode)
            width+=3
            #fill the scroll list
            for meta in self.mNodes:
                cmds.textScrollList('slMetaNodeList', edit=True,
                                        append=('{0:<%i}:{1:}' % width).format(meta.mNode, meta.mClass),
                                        sc=lambda *args:self.selectCmd(),
                                        dcc=lambda *x:self.doubleClick() )   


class MetaClass(object):

#    class ManagedDict(dict):
#        __slots__ = ["callback"]
#        def __init__(self, callback, *args, **kwargs):
#            self.callback = callback
#            dict.__init__(self, *args, **kwargs)
#        def _wrap(method):
#            def wrapper(self, *args, **kwargs):
#                result = method(self, *args, **kwargs)
#                self.callback()
#                print 'newItems : ', self.items()
#                print 'result : ', result
#                return result
#            return wrapper
#        __delitem__ = _wrap(dict.__delitem__)
#        __setitem__ = _wrap(dict.__setitem__)
#        __getitem__ = _wrap(dict.__getitem__)
#        clear = _wrap(dict.clear)
#        pop = _wrap(dict.pop)
#        popitem = _wrap(dict.popitem)
#        setdefault = _wrap(dict.setdefault)
#        update =  _wrap(dict.update)
 
#    class LinkedDict(dict):
#        '''
#        This is an interesting idea, the __getattribute__ in the mClass will return a standard
#        dict from a serialized json attr which means that that dict is then unaware of the 
#        original data. This is a bit of candy so that the __getattribute__ now returns this class
#        as a dict with the __setitems__ over-loaded to push any changes directly back to the 
#        mClass attr itself!
#        '''
#        def __init__(self,mClassCached,*args,**kws):
#            super(MetaClass.LinkedDict, self).__init__(*args,**kws)  
#            self.cachedMetaClass=mClassCached[0]
#            self.cachedMetaClassAttr=mClassCached[1]
#            self.cachedKeys=[]
#            if len(mClassCached)==3:
#                self.cachedKeys=(mClassCached[2])
#            
#        def __setitem__(self, key, value):
#            super(MetaClass.LinkedDict, self).__setitem__(key, value)
#            print 'Re-Serializing back to MayaNode Here'
#            baseDict=getattr(self.cachedMetaClass,self.cachedMetaClassAttr)
#            print baseDict, key
#            print self.items()
#            keys=self.cachedKeys
#            keys.append(key)
#            print ("baseDict%s" % "['%s']" % '\'][\''.join(keys))
#            #eval("baseDict%s=%s" % "['%s']" % '\'][\''.join(keys)) = {key: value for key, value in self.items()}
#            print 'newBaseDict', baseDict
#            setattr(self.cachedMetaClass,self.cachedMetaClassAttr,{key: value for key, value in self.items()})
#            
#        def __getitem__(self, key):
#            data=super(MetaClass.LinkedDict,self).__getitem__(key)
#            if issubclass(type(data),dict):
#                self.cachedKeys.append(key)
#                print 'cachedKeys >> :' , self.cachedKeys
#                return MetaClass.LinkedDict([self.cachedMetaClass,self.cachedMetaClassAttr,self.cachedKeys],data)
#            return data
            
            
    def __new__(cls, *args, **kws):
        '''
        Idea here is if a MayaNode is passed in and has the mClass attr
        we pass that into the super(__new__) such that an object of that class
        is then instantiated and returned.
        '''
        mClass=None
        mNode=None
        if args:
            mNode=args[0]
            if isMetaNode(mNode):
                mClass=cmds.getAttr('%s.%s' % (mNode,'mClass'))
        if mClass:
            log.debug("mClass derived from MayaNode Attr : %s" % mClass)
            if RED9_META_REGISTERY.has_key(mClass):   
                _registeredMClass=RED9_META_REGISTERY[mClass]
                try:
                    log.debug('Instantiating existing mClass : %s >> %s' % (mClass,_registeredMClass))
                    return super(cls.__class__, cls).__new__(_registeredMClass)
                except:
                    log.debug('Failed to initialize mClass : %s' % _registeredMClass)
                    pass
            else:
                raise StandardError('Node has an unRegistered mClass attr set')
        else:
            log.debug("mClass not found or Registered")
            return super(cls.__class__, cls).__new__(cls)    
    
    def __init__(self, node=None, name=None, nodeType='network', autofill='all'):
        '''
        Base Class for Meta support. This manages all the attribute
        and class management for all subsequent inherited classes
        @param node: Maya Node - if given we test it for the mClass attribute, if it exists
                    we initialize a class of that type and return. If not passed in then we 
                    make a new network node for the type given. 
        @param name: only used on create, name to set for the new Maya Node (self.mNode) 
        @param nodeType: allows you to specify a node of type to create as a new mClass node.
                        default is 'network', not that for any node to show up in the get
                        calls that type MUST be registered in the RED9_META_NODETYPE_REGISTERY
        @param autofill: 'str' cast all the MayaNode attrs into the class dict by default. 
                    Updated: modes: 'all' or 'messageOnly'. all casts every attr, messageOnly 
                    fills the node with just message linked attrs (designed for MetaClass work 
                    with HIK characterNode)
        NOTE: mNode is now a wrap on the MObject so will always be in sync even if the node is renamed/parented
        '''
        #data that will not get pushed to the Maya node 
        object.__setattr__(self, '_mNode', '')
        object.__setattr__(self, '_MObject', '')
        object.__setattr__(self, 'UNMANAGED', ['mNode',
                                               '_MObject',
                                               '_mNode']) 
        if not node: 
            if not name:
                name=str(self.__class__.__name__)
            #no MayaNode passed in so make a fresh network node (default)
            node=cmds.createNode(nodeType,name=name)
            self.mNode=node
            self.addAttr('mClass', value=str(self.__class__.__name__)) #! MAIN ATTR !: used to know what class to instantiate.
            self.addAttr('mNodeID', value=name)                        #! MAIN NODE ID !: used by pose systems to ID the node.
            
            log.debug('New Meta Node Created')
            cmds.setAttr('%s.%s' % (self.mNode,'mClass'), e=True,l=True) #lock it
            cmds.setAttr('%s.%s' % (self.mNode,'mNodeID'),e=True,l=True) #lock it
        else:
            self.mNode=node
            if not self.hasAttr('mNodeID'):
                #for casting None MetaData, standard Maya nodes into the api
                self.mNodeID=node.split('|')[-1].split(':')[-1]
            if isMetaNode(node):
                log.debug('Meta Node Passed in : %s' % node)
            else:
                log.debug('Standard Maya Node being metaManaged')
                
        #bind any default attrs up - note this should be overloaded where required
        self.__bindData__()
        
        #This is useful! so we have a node with a lot of attrs, or just a simple node
        #this block if activated will auto-fill the object.__dict__ with all the available
        #Maya node attrs, so you get autocomplete on ALL attrs in the script editor!
        if autofill=='all' or autofill=='messageOnly':
            self.__fillAttrCache__(autofill)
     
     
    def __bindData__(self):
        '''
        This is intended as an entry point to allow you to bind whatever attrs or extras 
        you need at a class level. It's called by the __init__ ...
        Intended to be overloaded as and when needed when inheriting from MetaClass
        NOTE:
            #to bind a new attr and serilaize it to the self.mNode (Maya node)
            self.addAttr('newDefaultAttr',attrType='string') 
            
            #to bind a new attribute to the python object only, not serialized to Maya node
            self.newClassAttr=None  :or:   self.__setattr__('newAttr',None)      
        '''
        pass    
     
    #Cast the mNode attr to the actual MObject so it's no longer limited by string dagpaths       
    #yes I know Pymel does this for us but I don't want the overhead!  
    def __get_mNode(self):
        if self._MObject: 
            #if we have an object thats a dagNode, ensure we return FULL Path
            if OpenMaya.MObject.hasFn(self._MObject, OpenMaya.MFn.kDagNode):
                dPath = OpenMaya.MDagPath()
                OpenMaya.MDagPath.getAPathTo(self._MObject, dPath)
                return dPath.fullPathName()
            else:
                depNodeFunc = OpenMaya.MFnDependencyNode(self._MObject)
                return depNodeFunc.name()    
    
    def __set_mNode(self, node):
        if node:
            mobj=OpenMaya.MObject()
            selList=OpenMaya.MSelectionList()
            selList.add(node)
            selList.getDependNode(0,mobj)
            self._mNode=node
            self._MObject=mobj             
                
    mNode = property(__get_mNode, __set_mNode)
    
    
    def __repr__(self):
        if self.hasAttr('mClass'):
            return "%s(mClass: '%s', node: '%s')"  % (self.__class__, self.mClass, self.mNode.split('|')[-1])
        else:
            return "%s(Wrapped Standard MayaNode, node: '%s')"  % (self.__class__, self.mNode.split('|')[-1])
        
    def __fillAttrCache__(self, level):
        '''
        go through all the attributes on the given node and cast each one of them into 
        the main object.__dict__ this means they all show in the scriptEditor and autocomplete!
        This is ONLY for ease of use when dot complete in Maya, nothing more
        '''
        if level=='messageOnly':
            attrs=[attr for attr in cmds.listAttr(self.mNode) if cmds.getAttr('%s.%s' % (self.mNode,attr),type=True)=='message']
        else:
            attrs=cmds.listAttr(self.mNode)
        for attr in attrs:
            try:
                #we only want to fill the __dict__ we don't want the overhead
                #of reading the attr data as thats done on demand.
                object.__setattr__(self, attr, None)
            except:
                pass
    
    
    # Attribuite Management block 
    #-----------------------------------------------------------------------------------    
           
    def __setEnumAttr__(self,attr,value):
        '''
        Enums : I'm allowing you to set value by either the index or the display text
        '''
        if attributeDataType(value)=='string':
            log.debug('set enum attribute by string :  %s' % value)
            enums=cmds.attributeQuery(attr, node=self.mNode, listEnum=True)[0].split(':')
            try:
                value=enums.index(value)
            except:
                raise ValueError('Invalid enum string passed in: string is not in enum keys')
        log.debug('set enum attribute by index :  %s' % value)
        cmds.setAttr('%s.%s' % (self.mNode, attr), value)
    
    def __setMessageAttr__(self,attr,value,force=True):
        '''
        Message : by default in the __setattr_ I'm assuming that the nodes you pass in are to be 
        the ONLY connections to that msgLink and all other current connections will be deleted
        hence cleanCurrent=True
        '''
        if cmds.attributeQuery(attr, node=self.mNode, multi=True)==False: 
            if attributeDataType(value)=='complex':
                raise ValueError("You can't connect multiple nodes to a singluar message plug via __setattr__")
            log.debug('set singular message attribute connection:  %s' % value)
            self.connectChild(value, attr, cleanCurrent=True, force=force)
        else:
            log.debug('set multi-message attribute connection:  %s' % value)
            self.connectChildren(value, attr, cleanCurrent=True, force=force)
                   
    def __setattr__(self, attr, value, force=True, **kws):
        '''
        Overload the base setattr to manage the MayaNode itself
        '''
        object.__setattr__(self, attr, value)
        
        if attr not in self.UNMANAGED and not attr=='UNMANAGED':
            if cmds.attributeQuery(attr, exists=True, node=self.mNode):
                locked=False
                if self.attrIsLocked(attr) and force:
                    self.attrSetLocked(attr,False)
                    locked=True
                    
                #Enums Handling
                if cmds.attributeQuery(attr, node=self.mNode, enum=True):
                    self.__setEnumAttr__(attr, value)
                          
                #Message Link handling
                elif cmds.attributeQuery(attr, node=self.mNode, message=True):          
                    self.__setMessageAttr__(attr, value, force)     
                          
                #Standard Attribute
                else:
                    attrString='%s.%s' % (self.mNode, attr)      # mayaNode.attribute for cmds.get/set calls
                    attrType=cmds.getAttr(attrString, type=True) # the MayaNode attribute valueType
                    valueType=attributeDataType(value)           # DataType passed in to be set as Value
                    log.debug('valueType : %s' % valueType)
                    
                    if attrType=='string':
                        if valueType=='string':
                            log.debug('set string attribute:  %s' % value)
                            cmds.setAttr(attrString, value, type='string')
                            return
                        elif valueType=='complex':
                            log.debug('set string attribute to complex :  %s' % self.__serializeComplex(value))
                            cmds.setAttr(attrString, self.__serializeComplex(value), type='string')
                            return
                    elif attrType in ['double3','float3'] and valueType=='complex':
                        try:
                            log.debug('set %s attribute' % attrType)
                            cmds.setAttr(attrString, value[0], value[1], value[2])
                        except ValueError, error:
                            raise ValueError(error)
                    else:
                        cmds.setAttr(attrString, value)
                    
                if locked:
                    self.attrSetLocked(attr,True)
            else:
                log.debug('attr : %s doesnt exist on MayaNode > class attr only' % attr)  
             
    def __getattribute__(self, attr):
        '''
        Overload the method to always return the MayaNode
        attribute if it's been serialized to the MayaNode
        '''  
        try:
            #this stops recursion, do not getAttr on mNode here
            mNode=object.__getattribute__(self, "_mNode")
            
            #MayaNode processing - retrieve attr from the MayaNode if we can
            if cmds.objExists(mNode):
                if cmds.attributeQuery(attr, exists=True, node=mNode):
                    attrType=cmds.getAttr('%s.%s' % (mNode,attr),type=True)
                    
                    #Message Link handling
                    #=====================
                    if attrType=='message':
                        msgLinks=cmds.listConnections('%s.%s' % (mNode,attr),destination=True,source=True) #CHANGE : Source=True
                        if msgLinks:
                            msgLinks=cmds.ls(msgLinks,l=True) #cast to longNames!
                            if cmds.attributeQuery(attr, node=mNode, m=True): #multi message
                                return msgLinks
                            else:
                                #TODO : this is questionable? if the attr has multi connects we need to deal with that
                                #and return all connected metaNodes as a list here!
                                if isMetaNode(msgLinks[0]):
                                    #we have a linked MClass node so instantiate the class object
                                    log.debug('%s :  Connected data is an mClass Object, returning the Class' % msgLinks[0])
                                    return MetaClass(msgLinks[0])
                                else:
                                    return msgLinks#[0] Modified, all message links now return a list of connections
                        else:
                            return
                    #Standard Maya Attr handling
                    #===========================
                    attrVal=cmds.getAttr('%s.%s' % (mNode,attr))
                    if attrType=='string':
                        #for string data we pass it via the JSON decoder such that
                        #complex data can be managed and returned correctly
                        try:
                            attrVal=self.__deserializeComplex(attrVal)
                            if type(attrVal)==dict:
                                log.debug('Making LinkedDict')
                                return attrVal
                                #return self.LinkedDict([self,attr],attrVal)
                        except:
                            log.debug('string is not JSON deserializable')
                    elif attrType=='double3' or attrType=='float3':
                        return attrVal[0] #return (x,x,x) not [(x,x,x)]
                else:
                    attrVal=object.__getattribute__(self, attr)
            else:
                attrVal=object.__getattribute__(self, attr)
            return attrVal
        except StandardError,error:
            raise StandardError(error)
  
    def __serializeComplex(self,data):  
        '''
        Serialize complex data such as dicts to a JSON string
        
        Test the len of the string, anything over 32000 (16bit) gets screwed by the 
        Maya attribute template and truncated IF you happened to select the string in the
        Attribute Editor. For long strings we need to force lock the attr here!
        bit thanks to MarkJ for that as it was doing my head in!!
        http://markj3d.blogspot.co.uk/2012/11/maya-string-attr-32k-limit.html
        '''
        if len(data)>32700:
            log.debug('Warning >> Length of string is over 16bit Maya Attr Template limit - lock this after setting it!')  
        return json.dumps(data)  
    
    def __deserializeComplex(self,data):  
        '''
        Deserialize data from a JSON string back to it's original complex data
        '''
        #log.debug('deserializing data via JSON')
        if type(data) == unicode:
            return json.loads(str(data)) 
        return json.loads(data)  
      
    def __delattr__(self, attr): 
        try:
            object.__delattr__(self, attr)
            if cmds.attributeQuery(attr, exists=True, node=self.mNode):
                cmds.deleteAttr('%s.%s' % (self.mNode, attr))
        except StandardError,error:
            raise StandardError(error)
          
    def hasAttr(self, attr):
        '''
        simple wrapper check for attrs on the mNode itself.
        Note this is not run in some of the core internal calls in this baseClass
        '''
        return cmds.attributeQuery(attr, exists=True, node=self.mNode)
    
    def attrIsLocked(self,attr):
        return cmds.getAttr('%s.%s' % (self.mNode,attr),l=True)
   
    def attrSetLocked(self,attr,state):
        try:
            if not self.isReferenced():
                cmds.setAttr('%s.%s' % (self.mNode,attr),l=state)
        except StandardError,error:
            log.debug(error)
                                                                               
    def addAttr(self, attr, value=None, attrType=None, hidden=False, **kws):
        '''
        Wrapped version of Maya addAttr that manages the basic type flags for you 
        whilst also setting the attr on the MayaNode/class object itself. 
        I now merge in **kws to the dict I pass to the add command so you can 
        specify all standard cmds.addAttr flags in the same call.
        @param attr:  attribute name to add (standard 'longName' flag)
        @param value: initial value to set, if given the attribute type is automatically set for you
        @param attrType: specify the exact type of attr to add. By default I try and resolve
                    this for you from the type of value passed in.
        @param hidden: whether the attr is set available in the channelBox (only applies keyable attrs)

        NOTE: specific attr management for given types below:
            double3: self.addAttr(attr='attrName', attrType='double3',value=(value1,value2,value3))
            float3:  self.addAttr(attr='attrName', attrType='float3', value=(value1,value2,value3))
            enum:    self.addAttr(attr='attrName', attrType='enum',   value=1, enumName='Centre:Left:Right') 
        '''
        DataTypeKws={'string': {'longName':attr,'dt':'string'},\
                     'int':    {'longName':attr,'at':'long'},\
                     'bool':   {'longName':attr,'at':'bool'},\
                     'float':  {'longName':attr,'at':'double'},\
                     'float3': {'longName':attr,'at':'float3'},\
                     'double3':{'longName':attr,'at':'double3'},\
                     'enum':   {'longName':attr,'at':'enum'},\
                     'complex':{'longName':attr,'dt':'string'},\
                     'message':{'longName':attr,'at':'message','m':True,'im':False},\
                     'messageSimple':{'longName':attr,'at':'message','m':False}}      
        
        Keyable=['int','float','bool','enum','double3']  

        if attrType and attrType=='enum' and not kws.has_key('enumName'):
            raise ValueError('enum attrType must be passed with "enumName" keyword in args')       
        
        if cmds.attributeQuery(attr, exists=True, node=self.mNode):
            #if attr exists do we force the value here?? NOOOO as I'm using this 
            #to ensure that when we initialize certain classes base attrs exist. 
            log.debug('"%s" :  Attr already exists on the Node' % attr)
            if attrType=='enum':
                #enum handler this means you can use the addAttr to force changes/updates
                #to enumName setups, forcing possible updates via self.__bindData__
                log.debug('enum strings being updated to : %s' % kws['enumName'])
                cmds.addAttr('%s.%s' % (self.mNode,attr),e=True,enumName=kws['enumName'])
            #TODO: allow min, max, hidden, keyable attrs all to be modified here?
            return
        else:
            try:
                if not attrType:
                    attrType=attributeDataType(value)
                           
                DataTypeKws[attrType].update(kws) #merge in **kws, allows you to pass in all the standard addAttr kws   
                log.debug('valueType : %s > dataType kws: %s' % (attrType,DataTypeKws[attrType]))
                cmds.addAttr(self.mNode, **DataTypeKws[attrType])

                if attrType=='double3' or attrType=='float3':
                    attr1='%sX' % attr
                    attr2='%sY' % attr
                    attr3='%sZ' % attr                       
                    cmds.addAttr(self.mNode,longName=attr1,at='double',parent=attr,**kws)
                    cmds.addAttr(self.mNode,longName=attr2,at='double',parent=attr,**kws)
                    cmds.addAttr(self.mNode,longName=attr3,at='double',parent=attr,**kws)
                    object.__setattr__(self, attr1, None) #don't set it, just add it to the object
                    object.__setattr__(self, attr2, None) #don't set it, just add it to the object
                    object.__setattr__(self, attr3, None) #don't set it, just add it to the object                     
                    if attrType in Keyable and not hidden:
                        cmds.setAttr('%s.%s' % (self.mNode,attr1),e=True,keyable=True) 
                        cmds.setAttr('%s.%s' % (self.mNode,attr2),e=True,keyable=True)
                        cmds.setAttr('%s.%s' % (self.mNode,attr3),e=True,keyable=True)
                else:
                    if attrType in Keyable and not hidden:
                        cmds.setAttr('%s.%s' % (self.mNode, attr),e=True,keyable=True)
                                   
                if value:
                    self.__setattr__(attr, value, force=False)
                else:
                    #bind the attr to the python object if no value passed in
                    object.__setattr__(self, attr, None)
            except StandardError,error:
                raise StandardError(error)
     
    
    # Utity Functions
    #-------------------------------------------------------------------------------------
                  
    def select(self):
        cmds.select(self.mNode)
        
    def rename(self,name):
        '''
        rename the mNode itself
        '''
        cmds.rename(self.mNode,name)
        self.mNode=name
        
    def delete(self):
        '''
        delete the mNode and this class instance
        '''
        cmds.delete(self.mNode)
        del(self)
    
    def convertMClassType(self,newMClass):
        '''
        change the current mClass type of the node and re-initialize the object
        '''
        if RED9_META_REGISTERY.has_key(newMClass):
            cmds.setAttr('%s.%s' % (self.mNode,'mClass'),e=True,l=False) 
            self.mClass=newMClass
            cmds.setAttr('%s.%s' % (self.mNode,'mClass'),e=True,l=True) 
            return MetaClass(self.mNode)
        else:
            raise StandardError('given class is not in the mClass Registry : %s' % newMClass)

    def isReferenced(self):
        '''
        is node.mNode referenced?
        '''
        return cmds.referenceQuery(self.mNode,inr=True)
    
    def nameSpace(self):
        '''
        If the namespace is nested this will return a list where 
        [-1] is the direct namespace of the node
        '''
        return self.mNode.split(':')[:-1]
    
    
    # Connection Management Block 
    #---------------------------------------------------------------------------------
    
    def connectChildren(self, nodes, attr, srcAttr=None, cleanCurrent=False, force=True):
        '''
        Fast method of connecting message links to the mNode as children
        @param nodes: Maya nodes to connect to this mNode
        @param attr: Name for the message attribute 
        @param srcAttr: If given this becomes the attr on the child node which connects it 
                        to self.mNode. If NOT given this attr is set to self.mNodeID
        @param cleanCurrent:  Disconnect and clean any currently connected nodes to this attr.
                        Note this is operating on the mNode side of the connection, removing
                        any currently connected nodes to this attr prior to making the new ones
        @param force: Maya's default connectAttr 'force' flag, if the srcAttr is already connected 
                        to another node force the connection to the new attr 
        TODO: do we move the cleanCurrent to the end so that if the connect fails you're not left 
        with a half run setup?
        '''
        if not issubclass(type(nodes),list):
            nodes=[nodes]
        #make sure we have the attr on the mNode
        self.addAttr(attr, attrType='message')
        if cleanCurrent:
            #disconnect and cleanup any current plugs to this message attr
            self.__disconnectCurrentAttrPlugs(attr)  
        if not srcAttr:
            srcAttr=self.mNodeID  #attr on the nodes source side for the child connection
        for node in nodes:
            if not cmds.attributeQuery(srcAttr, exists=True, node=node):
                cmds.addAttr(node,longName=srcAttr,at='message',m=True,im=False)
            try:
                cmds.connectAttr('%s.%s' % (self.mNode,attr),'%s.%s' % (node,srcAttr), f=force)
            except StandardError,error:
                log.warning(error)
                
    def connectChild(self, node, attr, srcAttr=None, cleanCurrent=True, force=True):
        '''
        Fast method of connecting message links to the mNode as child
        NOTE: this call by default manages the attr to only ONE CHILD to
        avoid this use cleanCurrent=False
        @param node: Maya node to connect to this mNode
        @param attr: Name for the message attribute  
        @param srcAttr: If given this becomes the attr on the child node which connects it 
                        to self.mNode. If NOT given this attr is set to self.mNodeID
        @param cleanCurrent: Disconnect and clean any currently connected nodes to this attr.
                        Note this is operating on the mNode side of the connection, removing
                        any currently connected nodes to this attr prior to making the new ones
        @param force: Maya's default connectAttr 'force' flag, if the srcAttr is already connected 
                        to another node force the connection to the new attr
        TODO: do we move the cleanCurrent to the end so that if the connect fails you're not left 
        with a half run setup?
        
        '''
        #make sure we have the attr on the mNode, if we already have a MULIT-message
        #should we throw a warning here???
        self.addAttr(attr, attrType='messageSimple')
        if issubclass(type(node), MetaClass):
            node=node.mNode 
        try:
            if cleanCurrent:
                #disconnect and cleanup any current plugs to this message attr
                self.__disconnectCurrentAttrPlugs(attr)      
            if not srcAttr:          
                srcAttr=self.mNodeID  #attr on the nodes source side for the child connection
            if not cmds.attributeQuery(srcAttr, exists=True, node=node):
                cmds.addAttr(node,longName=srcAttr, at='message', m=False)
            cmds.connectAttr('%s.%s' % (self.mNode,attr),'%s.%s' % (node,srcAttr), f=force)
        except StandardError,error:
            log.warning(error)
                          
    def connectParent(self, node, attr, srcAttr=None):
        '''
        Fast method of connecting message links to the mNode as parents
        @param nodes: Maya nodes to connect to this mNode
        @param attr: Name for the message attribute on eth PARENT!
        @param srcAttr: If given this becomes the attr on the node which connects it 
                        to the parent. If NOT given this attr is set to parents shortName

        '''
        if issubclass(type(node), MetaClass):
            if not srcAttr:
                srcAttr=node.mNodeID
            node=node.mNode        
        if not srcAttr:
            srcAttr=node.split('|')[-1].split(':')[-1]
        self.addAttr(srcAttr, attrType='message')
        try:
            if not cmds.attributeQuery(attr, exists=True, node=node):
                #add to parent node
                cmds.addAttr(node,longName=attr, at='message', m=False)
            cmds.connectAttr('%s.%s' % (node,attr),'%s.%s' % (self.mNode,srcAttr))
        except StandardError,error:
                log.warning(error)
    
    def __disconnectCurrentAttrPlugs(self, attr):
        '''
        from a given attr on the mNode disconnect any current connections and 
        clean up the plugs by deleting the existing attributes
        '''
        currentConnects=self.__getattribute__(attr)
        if currentConnects:
            if not isinstance(currentConnects,list):
                currentConnects=[currentConnects]
            for connection in currentConnects:
                try:
                    log.debug('message Attr : %s > already connect : %s' % (attr,connection))
                    self.disconnectChild(connection, attr=attr, deleteSourcePlug=True, deleteDestPlug=False)
                except:
                    log.warning('Failed to unconnect current message link')
                                           
    def disconnectChild(self, node, attr=None, deleteSourcePlug=True, deleteDestPlug=True):
        '''
        disconnect a given child node from the mNode. Default is to remove
        the connection attribute in the process, cleaning up both sides of
        the connection
        
        TODO: Need to check the Attribute before wildly disconnecting. This is fine
        if the node is connected to the MNode on once via a single message link, but if
        its connected to multiple message attrs then this needs checking.
        @param node: the Maya node to disconnect from the mNode
        @param deleteSourcePlug: if True delete SOURCE side attribiute after disconnection
        @param deleteDestPlug: if True delete the DESTINATION side attribiute after disconnection
        '''
        searchConnection=self.mNode
        if attr:
            searchConnection='%s.%s' % (self.mNode,attr)
        if isMetaNode(node): 
            node=node.mNode
        cons=cmds.listConnections(node,s=True,d=False,p=True,c=True)
        if not cons:
            raise StandardError('%s is not connected to the mNode %s' % (node,self.mNode))
        for sPlug,dPlug in zip(cons[0::2],cons[1::2]):
            if searchConnection in dPlug:
                log.debug('Disconnecting %s from %s' % (dPlug,sPlug))
                cmds.disconnectAttr(dPlug,sPlug)
                if deleteSourcePlug:
                    try:
                        #del(sPlug)
                        log.debug('Deleting Source Attr %s' % (sPlug))
                        cmds.deleteAttr(sPlug)
                    except:
                        log.warning('Failed to Remove mNode Connection Attr')
                if deleteDestPlug:
                    try:
                        #del(dPlug)
                        log.debug('Deleting Dest Attr %s' % (sPlug))
                        cmds.deleteAttr(dPlug)
                    except:
                        log.warning('Failed to Remove Node Connection Attr')
                break
  

    # Get Nodes Management Block
    #---------------------------------------------------------------------------------
    
    def addChildMetaNode(self, mClass, attr, nodeName=None):
        '''
        Generic call to add a MetaNode as a Child of self
        @param mClass: mClass to generate, given as a valid key to the RED9_META_REGISTERY ie 'MetaRig'
        @param attr: message attribute to wire the new node too
        @param name: optional name to give the new name
        '''
        if RED9_META_REGISTERY.has_key(mClass):
            childClass=RED9_META_REGISTERY[mClass]
            mChild=childClass(name=nodeName)
            self.connectChild(mChild, attr)
            return mChild
    
    def getChildMetaNodes(self, walk=False):
        '''
        Find any connected Child MetaNodes to this mNode
        @param walk: walk the connected network and return ALL children conntected in the tree
        '''
        if not walk:
            return getConnectedMetaNodes(self.mNode,source=False,destination=True)
        else:
            metaNodes=[]
            children=getConnectedMetaNodes(self.mNode,source=False,destination=True)
            if children:
                runaways=0
                depth=0
                processed=[]
                extendedChildren=[]
                
                while children and runaways<=1000:
                    for child in children:
                        if child.mNode not in processed:
                            metaNodes.append(child)
                            #log.info('mNode added to metaNodes : %s' % child.mNode)
                        children.remove(child)
                        processed.append(child.mNode)                
                        #log.info( 'connections too : %s' % child.mNode)
                        extendedChildren.extend(getConnectedMetaNodes(child.mNode,source=False,destination=True))
                        #log.info('left to process : %s' % ','.join([c.mNode for c in children]))
                        if not children:
                            if extendedChildren:
                                log.info('Child MetaNode depth extended %i' % depth)
                                log.info('Extended Depth child List: %s' % ','.join([c.mNode for c in extendedChildren]))
                                children.extend(extendedChildren)
                                extendedChildren=[]
                                depth+=1
                        runaways+=1           
                return metaNodes
        return []
    
    def getParentMetaNode(self):
        '''
        Find any connected Parent MetaNode to this mNode
        '''
        mNodes=getConnectedMetaNodes(self.mNode,source=True,destination=False)
        if mNodes:
            return mNodes[0]
                               
    def getChildren(self, walk=True):
        '''
        This finds all UserDefined attrs of type message and returns all connected nodes
        This is now being run in the MetaUI on doubleClick. This is a generic call, implemented 
        and over-loaded on a case by case basis. At the moment the MetaRig class simple calls
        mRig.getRigCtrls() in the call, but it means that we don't call .mRig.getRigCtrls()
        in generic meta functions.
        @param walk: walk all subMeta connections and include all their children too
        '''
        childMetaNodes=[self]
        children=[]
        if walk:
            childMetaNodes.extend([node for node in self.getChildMetaNodes(walk=True)])
        for node in childMetaNodes:
            log.debug('MetaNode : %s' % node.mNode)
            for attr in cmds.listAttr(self.mNode,ud=True):
                if cmds.getAttr('%s.%s' % (self.mNode,attr),type=True)=='message':
                    msgLinked=cmds.listConnections('%s.%s' % (self.mNode,attr),destination=True,source=False)
                    if msgLinked:
                        msgLinked=cmds.ls(msgLinked,l=True) #cast to longNames!
                        #print msgLinked,attr
                        children.extend(msgLinked)
        return children

        

def deleteEntireMetaRigStructure(searchNode=None):
    '''
    This is a hard core unplug and cleanup of all attrs added by the
    MetaRig, all connections and all nodes. Use CAREFULLY!    
    '''
    import Red9_AnimationUtils as r9Anim #lazy to stop cyclic as anim also import meta
    if searchNode and not cmds.objExists(searchNode):
        raise StandardError('given searchNode doesnt exist')
    if not searchNode:
        searchNode=cmds.ls(sl=True)[0]
    mRig=getConnectedMetaSystemRoot(searchNode)
    if not mRig:
        raise StandardError('No root MetaData system node found from given searchNode')
    mNodes=[]
    mNodes.append(mRig)
    mNodes.extend(mRig.getChildMetaNodes(walk=True)) 
    mNodes.reverse()
    
    for a in mNodes:print a
    
    for metaChild in mNodes:
        for child in metaChild.getChildren(walk=False):
            metaChild.disconnectChild(child)
            r9Anim.MirrorHierarchy().deleteMirrorIDs(child)
            #For the time being I'm adding the OLD mirror markers to this 
            #call for the sake of cleanup on old rigs
            if cmds.attributeQuery('MirrorMarker', exists=True, node=child):
                cmds.deleteAttr('%s.MirrorMarker' % child)
            if cmds.attributeQuery('MirrorList', exists=True, node=child):
                cmds.deleteAttr('%s.MirrorList' % child)
            if cmds.attributeQuery('MirrorAxis', exists=True, node=child):
                cmds.deleteAttr('%s.MirrorAxis' % child)
        metaChild.delete()
    

class MetaRig(MetaClass):
    '''
    Initial test for a MetaRig labelling system
    '''
    def __init__(self,*args,**kws):
        '''
        @param name: name of the node and in this case, the RigSystem itself
        '''
        super(MetaRig, self).__init__(*args,**kws)
        self.CTRL_Prefix='CTRL' #prefix for all connected CTRL_ links added
        self.rigGlobalCtrlAttr='CTRL_Main' #attribute linked to the top globalCtrl in the rig
    
    def __bindData__(self):
        self.addAttr('version',1.0) #ensure these are added by default
        self.addAttr('rigType', '') #ensure these are added by default  
        self.addAttr('renderMeshes', attrType='message')
           
    def addGenericCtrls(self, nodes):
        '''
        Pass in a list of objects to become generic, non specific
        controllers for a given setup. These are all connected to the same slot
        so don't have the search capability that the funct below gives
        '''
        self.connectChildren(nodes, 'RigCtrls')
        
    def addRigCtrl(self, node, ctrType, mirrorData=None, boundData=None):
        '''
        Add a single CTRL of managed type
        @param node: Maya node to add
        @param ctrType: Attr name to assign this too
        @param mirrorData: {side:'Left', slot:int, axis:'translateX,rotateY,rotateZ'..}  
        @param boundData: {} any additional attrData, set on the given node as attrs 
        
        #NOTE: mirrorData[slot] must NOT == 0 as it'll be handled as not set by the core
        #NOTE: ctrType >> 'Main' is the equivalent of the RootNode in the FilterNode calls
        '''
        import Red9_AnimationUtils as r9Anim #lazy load to avoid cyclic imports
        
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        self.connectChild(node,'%s_%s' % (self.CTRL_Prefix,ctrType))  
        if mirrorData:
            mirror=r9Anim.MirrorHierarchy()
            axis=None
            if mirrorData.has_key('axis'):
                axis = mirrorData['axis']
            mirror.setMirrorIDs(node,
                                side=mirrorData['side'],
                                slot=mirrorData['slot'],
                                axis=axis)
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    log.debug('Adding boundData to node : %s:%s' %(key,value))
                    MetaClass(node).addAttr(key, value=value)
                         
    def getRigCtrls(self, walk=False):
        '''
        Find all connected controllers for this node. Note, if you've added
        them using the .addRigCtrl() then this function will return only those,
        else it'll return those added by the addGenericCtrls() call
        @param walk: step into all child MetaSystems and return their Ctrls too
        '''
        controllers=[]
        childMetaNodes=[self]
        if walk:
            childMetaNodes.extend([node for node in self.getChildMetaNodes(walk=True)])
        for node in childMetaNodes:
            log.debug('MetaNode : %s' % node.mNode)
            ctrlAttrs=cmds.listAttr(node.mNode,ud=True,st='%s_*' % self.CTRL_Prefix)
            if ctrlAttrs:
                for attr in ctrlAttrs:
                    control=node.__getattribute__(attr) #now returns a list regardless 
                    if not control:
                        log.warning('%s is unlinked and invalid' % attr)
                    else:
                        controllers.append(control[0])
            elif node.hasAttr('RigCtrls'):
                controllers.extend(node.RigCtrls)
        return controllers

    def getChildren(self, walk=False):
        return self.getRigCtrls(walk=walk)
        

    #Do we supply a few generic presets?
    #---------------------------------------------------------------------------------
    
    def addWristCtrl(self,node,side,axis=None):
        self.addRigCtrl(node,'%s_Wrist' % side[0], 
                        mirrorData={'side':side, 'slot':1,'axis':axis})
    def addElbowCtrl(self,node,side,axis=None):
        self.addRigCtrl(node,'%s_Elbow' % side[0], 
                        mirrorData={'side':side, 'slot':2,'axis':axis})
    def addClavCtrl(self,node,side,axis=None):
        self.addRigCtrl(node,'%s_Clav' % side[0], 
                        mirrorData={'side':side, 'slot':3,'axis':axis})  
    def addFootCtrl(self,node,side,axis=None):
        self.addRigCtrl(node,'%s_Foot' % side[0], 
                        mirrorData={'side':side, 'slot':4,'axis':axis})
    def addKneeCtrl(self,node,side,axis=None):
        self.addRigCtrl(node,'%s_Knee' % side[0], 
                        mirrorData={'side':side, 'slot':5,'axis':axis})
    def addPropCtrl(self,node,side,axis=None):
        self.addRigCtrl(node,'%s_Prop' % side[0], 
                        mirrorData={'side':side, 'slot':6,'axis':axis})

    #NOTE: Main should be the Top World Space Control for the entire rig
    #====================================================================
    def addMainCtrl(self,node,side='Centre',axis=None):
        self.addRigCtrl(node,'Main', 
                        mirrorData={'side':side, 'slot':1,'axis':axis})      
    def addRootCtrl(self,node,side='Centre',axis=None):
        self.addRigCtrl(node,'Root', 
                        mirrorData={'side':side, 'slot':2,'axis':axis})
    def addHipCtrl(self,node,side='Centre',axis=None):
        self.addRigCtrl(node,'Hips', 
                        mirrorData={'side':side, 'slot':3,'axis':axis})        
    def addChestCtrl(self,node,side='Centre',axis=None):
        self.addRigCtrl(node,'Chest', 
                        mirrorData={'side':side, 'slot':4,'axis':axis})
    def addHeadCtrl(self,node,side='Centre',axis=None):
        self.addRigCtrl(node,'Head', 
                        mirrorData={'side':side, 'slot':5,'axis':axis})
    def addNeckCtrl(self,node,side='Centre',axis=None):
        self.addRigCtrl(node,'Neck', 
                        mirrorData={'side':side, 'slot':6,'axis':axis})
 
    def addSupportMetaNode(self, attr, nodeName=None): 
        '''
        Not sure the best way to do this, but was thinking that the main mRig
        node should be able to have sub MetaClass nodes to cleanly define
        what nodes are AnimCtrls, and what nodes you want to tag as Support
        subsystems, ie, ikSolvers and construction nodes within the rig
        
        @param attr: Attribute used in the message link. Note this is what you use
                     to transerve the Dag tree so use something sensible!  
        @param nodeName: Name of the MetaClass network node created
        '''
        if not nodeName:
            nodeName=attr
        return self.addChildMetaNode('MetaRigSupport', attr=attr, nodeName=nodeName)
  
    def addSupportNode(self, node, attr, boundData=None):
        '''
        Add a single MAYA node flagged as a SUPPORT node of managed type
        Really in the MetaRig design these should be wired to a MetaRigSupport node
        @param node: Maya node to add
        @param attr: Attr name to assign this too  
        @param boundData: {} Data to set on the given node as attrs 
        '''
        self.connectChild(node,'SUP_%s' % attr)  
        if boundData:
            if issubclass(type(boundData),dict):  
                for key, value in boundData.iteritems():
                    log.debug('Adding boundData to node : %s:%s' %(key,value))
                    MetaClass(node).addAttr(key, value=value)  
                        
    def addMetaSubSystem(self, systemType, side,  attr=None, nodeName=None): 
        '''
        Basic design of a MetaRig is that you have sub-systems hanging off an mRig
        node, managing all controllers and data for a particular system, such as an
        Arm system. 
        
        @param systemType: Attribute used in the message link. Note this is what you use
                     to transerve the Dag tree so use something sensible! 
        @param mirrorSide: Side to designate the system. This is an enum: Centre,Left,Right
        @param nodeName: Name of the MetaClass network node created
        '''
        import Red9_AnimationUtils as r9Anim
        r9Anim.MirrorHierarchy()._validateMirrorEnum(side) #??? do we just let the enum __setattr__ handle this?

        if not attr:
            attr='%s_%s_System' % (side[0],systemType)
        if not nodeName:
            nodeName=attr
        subSystem=self.addChildMetaNode('MetaRigSubSystem', attr=attr, nodeName=nodeName) 
        
        #set the attrs on the newly created subSystem MetaNode
        subSystem.systemType=systemType
        subSystem.mirrorSide=side
        return subSystem
                             
    def getMirrorData(self):                       
        '''
        Bind the MirrorObject to this instance
        '''
        import Red9_AnimationUtils as r9Anim 
        self.MirrorClass=r9Anim.MirrorHierarchy(nodes=self.getRigCtrls()) 
        return self.MirrorClass
                  
    
class MetaRigSubSystem(MetaRig):
    '''
    SubClass of the MRig, designed to organize Rig sub-systems (ie L_ArmSystem, L_LegSystem..)
    within a complex rig structure. This or MetaRig should have the Controllers wired to it
    '''
    def __init__(self,*args,**kws):
        super(MetaRigSubSystem, self).__init__(*args,**kws)  

    def __bindData__(self):
        self.addAttr('systemType', attrType='string')
        self.addAttr('mirrorSide',enumName='Centre:Left:Right',attrType='enum')  
 
 
class MetaRigSupport(MetaClass):
    '''
    SubClass of MetaClass, designed to organize support nodes, solvers and other internal
    nodes within a complex rig structure which you may need to ID at a later date.
    Controllers should NOT be wired to this node
    '''
    def __init__(self,*args,**kws):
        super(MetaRigSupport, self).__init__(*args,**kws)  
        
    def __bindData__(self):
        '''
        over-load and blank so that the MetaRig bindData doesn't get inherited
        '''
        pass
    
    def addSupportNode(self, node, attr, boundData=None):
        '''
        Add a single MAYA node flagged as a SUPPORT node of managed type
        @param node: Maya node to add
        @param attr: Attr name to assign this too  
        @param boundData: {} Data to set on the given node as attrs 
        '''
        self.connectChild(node,'SUP_%s' % attr)  
        if boundData:
            if issubclass(type(boundData),dict):  
                for key, value in boundData.iteritems():
                    log.debug('Adding boundData to node : %s:%s' %(key,value))
                    MetaClass(node).addAttr(key, value=value)  
                    
                    
class MetaFacialRig(MetaRig):
    '''
    SubClass of the MetaRig, designed to be manage Facial systems in the MetaData
    Dag tree for organizing Facial Controllers and support nodes
    '''
    def __init__(self,*args,**kws):
        super(MetaFacialRig, self).__init__(*args,**kws) 
        self.CTRL_Prefix='FACE'    
        
    def __bindData__(self):
        '''
        over-load and blank so that the MetaRig bindData doesn't get inherited
        '''
        pass


class MetaFacialRigSupport(MetaClass):
    '''
    SubClass of the MetaClass, designed to organize support nodes, solvers and other internal
    nodes within a complex rig structure which you may need to ID at a later date.
    Controllers should NOT be wired to this node
    '''
    def __init__(self,*args,**kws):
        super(MetaFacialRigSupport, self).__init__(*args,**kws)       
        
    def addSupportNode(self, node, attr, boundData=None):
        '''
        Add a single MAYA node flagged as a SUPPORT node of managed type
        @param node: Maya node to add
        @param attr: Attr name to assign this too  
        @param boundData: {} Data to set on the given node as attrs 
        '''
        self.connectChild(node,'SUP_%s' % attr)  
        if boundData:
            if issubclass(type(boundData),dict):  
                for key, value in boundData.iteritems():
                    log.debug('Adding boundData to node : %s:%s' %(key,value))
                    MetaClass(node).addAttr(key, value=value)  

