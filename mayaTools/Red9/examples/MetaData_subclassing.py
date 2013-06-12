import Red9.core.Red9_Meta as r9Meta
import maya.cmds as cmds

class MyMetaExportBase(r9Meta.MetaClass):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MyMetaExportBase, self).__init__(*args,**kws) 
        self.lockState=True
        self.exportRoot=None
        
    def __bindData__(self):
        self.addAttr('version',attrType='float',min=0,max=3)
        self.addAttr('exportPath', attrType='string')
        
    def getExportPath(self):
        self.exportPath=cmds.file(q=True,sn=True)

    def getNodes(self):
        return self.exportRoot

class MyMetaExport_Character(MyMetaExportBase):
    def __init__(self,*args,**kws):
        super(MyMetaExportBase, self).__init__(*args,**kws) 
        self.lockState=True
        
    def getNodes(self):
        '''
        overloaded get method for character skeleton for example
        '''
        return cmds.ls(cmds.listRelatives(self.exportRoot,type='joint',ad=True),l=True)




class MyMetaCharacter(r9Meta.MetaRig):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MyMetaExportBase, self).__init__(*args,**kws) 
        self.lockState=True
        
    def __bindData__(self):
        self.addAttr('myRigType','')
        self.addAttr('myFloat', attrType='float', min=0, max=5)
        self.addAttr('myEnum', enumName='A:B:D:E:F', attrType='enum')

    def getChildren(self, walk=False, mAttrs=None, cAttrs=None):
        '''
        overload call for getChildren
        '''
        pass
       
    def getSkeletonRoots(self):
        '''
        get the Skeleton Root, used in the poseSaver. By default this looks
        for a message link via the attr "exportSkeletonRoot" to the skeletons root jnt
        always returns a list!
        '''
        pass 
        
    def getNodeConnectionMetaDataMap(self, node, mTypes=[]):  
        pass
    
        
#========================================================================
# This HAS to be at the END of this module so that the RED9_META_REGISTRY
# picks up all inherited subclasses when Red9.core is imported
#========================================================================   
r9Meta.registerMClassInheritanceMapping()
#r9Meta.registerMClassNodeMapping(nodes='myNewNodeType')
