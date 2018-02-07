"""
------------------------------------------
reloadFactory: cgm.core.reloadFactory
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

Module to handle some of the insanity of reloading our libraries.
"""
# From Python =============================================================
import os
import stat


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


#Need to walk below a folder and find modules and folders...
#Only modules with __init__ will be queryable, so preferably walk those folders as well.
import cgm_General as cgmGen
from cgm.core.cgmPy import path_Utils as PATH

## ----------------------------------------------------------------------
'''
	MODULEFACTORY.PY
	Functions for (re)loading module class types.
'''
## ----------------------------------------------------------------------
class ModuleFactoryException(Exception):
    pass


## ----------------------------------------------------------------------
class ModuleFactory(object):
    def __init__(self):
        self.modulePath = os.sep.join( [__file__.rpartition( os.sep )[0], 'modules'] )
        self.modules = [ x.partition('.')[0] for x in os.listdir(self.modulePath) if x.endswith('.py') 
                         and not x.count('__init') 
                         and not x.count('module_base') ]

    ## ----------------------------------------------------------------------

    def __getitem__(self, key):
        return(self.getClass(key))

    def __setitem__(self, key, value):
        raise ValueError("ModuleFactory does not allow the setting of values through brackets.")

    ## ----------------------------------------------------------------------
    def getClass(self, name):

        for item in self.modules:
            modName = item.split('.')[0]
            if modName == name:
                impmod = __import__('witch.modules.'+modName, {}, {}, [modName])
                reload(impmod)
                theClass = impmod.__getattribute__( modName )
                return(theClass)

        ## class not found!
        raise ModuleFactoryException('Class not found or unloadable: %s.' % name)
    
    
class Reloader(object):
    """
    This class contains methods for reloading the toolkit from source.
    """

    #: Get name of the top-level module name to be reloaded.
    toolkit_module_name = os.path.basename(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )


    def __init__(self, name=toolkit_module_name):
        """
        The constructor.

        :param name: ``str`` containing name of the top-level root module to reload.
            Defaults to the name of the Rigging Tools module.
        """
        
        self.logger = logging.getLogger(__name__)

        self.reloadModule(name)


    def reloadModule(self, name, *args):
        """
        This method reloads the toolkit.

        :param name: ``str`` containing name of the top-level root module to reload.
        """
        module = __import__(name, globals(), locals(), ['*'], -1)

        path = module.__path__[0]

        self.__reloadRecursive(path, name)

        self.logger.info('Successfully reloaded all modules!')


    def __reloadRecursive(self, path, parent_name):
        """
        This method recursively reloads all modules and sub-modules from a given
        path and parent.

        :param path: ``str`` path to top-level module to reload files from.
        :param parent_name: ``str`` name of the top-level parent module.
        """

        for root, dirs, files in os.walk(path, True, None):

            # Parse all the files of given path and reload python modules
            for f in files:

                if f.endswith('.py'):
                    if f == '__init__.py':
                        name = parent_name
                    else:
                        name = parent_name + '.' + f[:-3]

                    self.logger.debug('Reloaded module : {0}'.format(name))

                    try:
                        module = __import__(name, globals(), locals(), ['*'], -1)
                        reload(module)

                    except ImportError, e:
                        for arg in e.args:
                            self.logger.debug(arg)

                    except Exception, e:
                        for arg in e.args:
                            self.logger.debug(arg)

            # Now reload sub modules as well
            for dir_name in dirs:
                self.__reloadRecursive(
                    os.path.join(path, dir_name), parent_name+'.'+dir_name
                )

            break
        
class module_data(object):
    def __init__(self, path = None):
            """
            The constructor.
    
            :param name: ``str`` containing name of the top-level root module to reload.
                Defaults to the name of the Rigging Tools module.
            """
            #log.info(path[0])
            
            

def get_data(path = None, level = None, mode = 0, cleanPyc = False):
    """
    Function for walking below a given directory looking for modules to reload. It finds modules that have pyc's as
    well for help in reloading. There is a cleaner on it as well to clear all pycs found.
    
    :parameters
        path(str)
        level(int) - Depth to search. None means everything
        mode(int)
            0 - normal
            1 - pycs only
        self(instance): cgmMarkingMenu
        cleanPyc: Delete pycs after check
    :returns
        _d_files,_l_ordered,_l_pycd
        _d_files - dict of import key to file
        _l_ordered - ordered list of module keys as found
        _l_pycd - list of modules that were _pycd
    
    """
    _str_func = 'get_data'
    _b_debug = log.isEnabledFor(logging.DEBUG)

    _path = PATH.Path(path)
    
    _l_subs = []
    _d_files = {}
    _d_names = {}
    _d_pycd = {}
    _d_pycs = {}
    
    _l_duplicates = []
    _l_errors = []
    _l_pyc = []
    _l_pycd = []
    _base = _path.split()[-1]
    _l_ordered_list = []
    
    log.debug("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,path))                                               
    _i = 0
    for root, dirs, files in os.walk(path, True, None):
        # Parse all the files of given path and reload python modules
        _mRoot = PATH.Path(root)
        _split = _mRoot.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]
        
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_splitUp))   
        
        _mod = False
        _l_sub = []
        for f in files:
            key = False
            _pycd = False
            _long = os.path.join(root,f)
            if f.endswith('.pyc'):
                #name = f[:-4]                        
                #key = f
                _l_pyc.append(os.path.join(root,f))                    
            if f.endswith('.py'):
                _str_pycCheck = _long.replace('.py','.pyc')
                if os.path.exists(_str_pycCheck):
                    _pycd = True
                    
                if f == '__init__.py':
                    if _i == 0:
                        key = _base
                        name = _base
                    else:
                        key = '.'.join(_splitUp)
                        name = _subRoot
                    _mod = key
                else:
                    name = f[:-3]                        
                    if _i == 0:
                        key = '.'.join([_base,name])                            
                    else:
                        key = '.'.join(_splitUp + [name])
                        
            #log.debug("|{0}| >> found: {1}".format(_str_func,name)) 
            if key:
                if key not in _d_files.keys():
                    if key != _mod:_l_sub.append(key)                    
                    _d_files[key] = os.path.join(root,f)
                    _d_names[key] = name
                    _d_pycd[key] = _pycd
                    if _pycd:
                        _l_pycd.append(key)
                        _d_pycs[key] = _str_pycCheck
                else:
                    _l_duplicates.append("{0} >> {1} ".format(key, os.path.join(root,f)))

                """
                try:
                    module = __import__(name, globals(), locals(), ['*'], -1)
                    reload(module)

                except ImportError, e:
                    for arg in e.args:
                        logger.debug(arg)

                except Exception, e:
                    for arg in e.args:
                        logger.debug(arg)

        # Now reload sub modules as well
        for dir_name in dirs:
            __reloadRecursive(
                os.path.join(path, dir_name), parent_name+'.'+dir_name
            )"""
        if _mod:
            _l_ordered_list.append(_mod)
        if _l_sub:_l_ordered_list.extend(_l_sub)                    
            
        if level is not None and _i >= level:break 
        _i +=1
    
    if cleanPyc:
        _l_failed = []
        log.debug("|{0}| >> Found {1} pyc files under: {2}".format(_str_func,len(_l_pyc),path))                        
        for _file in _l_pyc:
        #for k in _l_ordered_list:
            #if k in _l_pycd:
            log.debug("|{0}| >> Attempting to clean pyc for: {1} ".format(_str_func,_file))  
            if not _file.endswith('.pyc'):
                raise ValueError,"Should NOT be here"
            try:
                os.remove( _file )
            except WindowsError, e:
                try:
                    log.info("|{0}| >> Initial delete fail. attempting chmod... ".format(_str_func))                          
                    os.chmod( _file, stat.S_IWRITE )
                    os.remove( _file )                          
                except Exception,e:
                    for arg in e.args:
                        log.error(arg)   
                    raise RuntimeError,"Stop"
        _l_pyc = []
        
    
    if mode == 1:
        log.info(cgmGen._str_subLine)        
        log.info("|{0}| >> Found {1} pyc files under: {2}".format(_str_func,len(_l_pyc),path))
        for m in _l_pyc:
            print(m)
        return _l_pyc   
    
    if _b_debug:
        cgmGen.log_info_dict(_d_files,"Files")
        cgmGen.log_info_dict(_d_names,"Imports")
    
    if _l_duplicates:
        log.debug(cgmGen._str_subLine)
        log.error("|{0}| >> DUPLICATE MODULES....")
        for m in _l_duplicates:
            if _b_debug:print(m)
    log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),path))
    
    log.debug(cgmGen._str_subLine)    
    log.debug("|{0}| >> Ordered MODULES....".format(_str_func))
    for k in _l_ordered_list:
        if _b_debug:print(k)
        
    log.debug(cgmGen._str_subLine)
    log.debug("|{0}| >> PYCD MODULES({1})....".format(_str_func,len(_l_pycd)))
    for k in _l_pycd:
        if _b_debug:print(k)
            
    return _d_files, _l_ordered_list, _l_pycd
            
class test(object):
    def __init__(self):
        print 'test'