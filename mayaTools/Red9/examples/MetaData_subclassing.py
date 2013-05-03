import Red9.core.Red9_Meta as r9Meta
import maya.cmds as cmds

class MyMetaExportBase(r9Meta.MetaClass):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MyMetaExportBase, self).__init__(*args,**kws) 
        self.lockState=True
        
    def __bindData__(self):
        self.addAttr('version',attrType='float',min=0,max=3)
        self.addAttr('exportPath',attrType='string')
        
    def getExportPath(self):
        self.exportPath=cmds.file(q=True,sn=True)

    def getNodes(self):
        pass



class MyMetaCharacter(r9Meta.MetaRig):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MyMetaExportBase, self).__init__(*args,**kws) 
        self.lockState=True
        
    def __bindData__(self):
        self.addAttr('myRigType','')


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
r9Meta.registerMClassNodeMapping()