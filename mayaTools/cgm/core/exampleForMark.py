# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim
from cgm.lib import attributes
import maya.cmds as mc
#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

class ChildClass(r9Meta.MetaClass):
    def __init__(self,*args,**kws):    
        log.info('ChildClass.__init__ --')	
        #Pull out our args/kws we need  ----------------------------------------------------------------------	
        node = kws.get('node')
        name = kws.get('name')
        _setClass = kws.get('setClass') or None
        if args:
            node = args[0]
            if len(args)>1:
                name = args[1]
            else:
                name = kws.get('name')

        if node is None or name is not None and mc.objExists(name):
            log.info("Created node")
            createdState = True
        else:
            createdState = False
            
        if _setClass:
            log.info("Preinitialize, setClass | default {0} | Maybe you shouldn't do this...".format(type(self).__name__))	
            try:#>>> TO CHECK IF WE NEED TO CLEAR CACHE ---------------------------------------------------------
                _currentMClass = attributes.doGetAttr(node,'mClass')#...use to avoid exceptions	
        
                if _setClass in [True, 1]:
                    _setClass = type(self).__name__	
        
                if _setClass not in r9Meta.RED9_META_REGISTERY:
                    log.error("mClass value not registered - '{0}'".format(_setClass))
                _setMClass = False
                if _setClass:#...if we're going to set the mClass attr...
                    if _currentMClass:#...does it have a current mClass attr value?
                        if _currentMClass != _setClass:#...if not the same, replace
                            log.warning("mClasses don't match. Changing to '{0}'".format(_setClass))				    
                            #mc.setAttr('%s.mClass' %(node), value = _setClass)	
                            attributes.doSetAttr(node,'mClass',_setClass,True)				
                            attributes.doSetAttr(node,'UUID','',True)
                            _setMClass = True
                        else:
                            log.info("mClasses match. ignoring...")				    		
                    else:#...if we have no value, set it
                        log.info("No mClass value, setting...")
                        _setMClass = True
                    if _setMClass:
                        if not mc.objExists("{0}.mClass".format(node)):
                            attributes.doAddAttr(node, 'mClass', 'string')
                        if not mc.objExists("{0}.UUID".format(node)):
                            attributes.doAddAttr(node, 'UUID', 'string')				
                        attributes.doSetAttr(node,'UUID','',True)
                        attributes.doSetAttr(node,'mClass',_setClass,True)			    
            except Exception,error:
                log.error("pre setClass fail >> %s"%error)
           

        super(ChildClass, self).__init__(*args,**kws)
 

        #>>> TO USE Cached instance ---------------------------------------------------------
        if self.cached:
            log.info('ChildClass.__init__ -- Using cached')
            return
        
class ChildClass2(ChildClass):  
    def __init__(self,*args,**kws):
        super(ChildClass2, self).__init__(*args,**kws)
        log.info('ChildClass2.__init__ --')
	
class ChildClass3(ChildClass):  
    def __init__(self,*args,**kws):
        super(ChildClass3, self).__init__(*args,**kws)
        log.info('ChildClass3.__init__ --')
        
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in