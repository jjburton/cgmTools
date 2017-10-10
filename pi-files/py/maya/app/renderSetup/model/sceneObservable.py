class SceneObservable(object):
    def __del__(self):
        pass
    
    
    def __init__(self):
        pass
    
    
    def activate(self):
        pass
    
    
    def activated(self):
        pass
    
    
    def deactivate(self):
        pass
    
    
    def register(self, eventType, observer):
        pass
    
    
    def unregister(self, eventType, observer):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    ALL_EVENTS = 'AllSceneEvents'
    
    
    CONNECTION_CHANGED = 'ConnectionChanged'
    
    
    NODE_ADDED = 'NodeAdded'
    
    
    NODE_REMOVED = 'NodeRemoved'
    
    
    NODE_RENAMED = 'NodeRenamed'
    
    
    NODE_REPARENTED = 'NodeReparented'



def sceneObserversEnabled():
    pass


def enableSceneObservers(value):
    pass


def instance():
    pass



_renderSetup_sceneObserversEnabled = True

_sceneObservable = None


