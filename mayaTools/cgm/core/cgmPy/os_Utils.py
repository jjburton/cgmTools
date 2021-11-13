"""
os_Utils
Josh Burton (under the supervision of David Bokser:)
www.cgmonastery.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
# From Python =============================================================
import re
import os
import stat
import pprint
from shutil import copyfile

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as MEL
# From cgm ==============================================================
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.cgmPy import path_Utils as cgmPath
PATH = cgmPath
from cgm.core import cgm_General as cgmGEN

#from cgm.lib.zoo.zooPy.path import Path
#import cgm.lib.zoo.zooPy.path as zooPath
#reload(zooPath)
#>>> Utilities
#===================================================================

log_start = cgmGEN.logString_start
log_sub = cgmGEN.logString_sub
log_msg = cgmGEN.logString_msg

def get_lsFromPath(str_path = None, 
                   matchArg = None, 
                   calledFrom = None,
                   removeInit = True, **kwargs):
    """
    Return files or folders of a specific type from a given path

    :parameters:
        str_path | str
            The base file path
        matchArg | str
            Type of file or folder to be returned.

    :returns:
        result

    :raises:
        TypeError | if 'str_path' is not a string
        ValueError | if 'str_path' is a recognized dir path
        TypeError | if 'matchArg' is not a string
       
    """
    def prepReturn(result,removeInit):
        for r in result:
            if '__init__' in r:
                result.remove(r)
        return result
    log.debug("get_lsFromPath str_path =  {1} | matchArg={0}".format(matchArg,str_path))
    
    _str_funcRoot = 'get_lsFromPath'
    if calledFrom: _str_funcName = "{0}.{1}({2})".format(calledFrom,_str_funcRoot,matchArg)    
    else:_str_funcName = "{0}({1})".format(_str_funcRoot,matchArg) 

    result = None 
    
    #>> Check the str_path
    if not isinstance(str_path, basestring):
        raise TypeError('path must be string | str_path = {0}'.format(str_path))
    if os.path.isfile(str_path):
        str_path = cgmPath.Path(str_path).up()
        log.info("{0} >> passed file. using dir: {1}".format(_str_funcName,str_path))        
    if not os.path.isdir(str_path):
        raise ValueError('path must validate as os.path.isdir | str_path = {0}'.format(str_path))
    
    #try:#>> Check matchArg
    if matchArg is not None:
        if issubclass(type(matchArg),list):
            _res = []
            for a in matchArg:
                _res.extend(find_files(str_path,a))
            return _res
        elif not isinstance(matchArg, basestring):
            raise TypeError('matchArg must be string | matchArg: {0}'.format(matchArg))        
    
    if matchArg is None or matchArg in ['']:
        return [ name for name in os.listdir(str_path) ] 
    
    #if '*.' in matchArg:
        #l_buffer = matchArg.split('*')        
        #return [ name for name in os.listdir(str_path) if name[-3:] == matchArg.split('*')[-1]]
        
    if matchArg.lower() in ['folder','dir']:
        return [ name for name in os.listdir(str_path) if os.path.isdir(os.path.join(str_path, name)) ]
    elif matchArg.lower() in ['maya files','maya']:
        return [ name for name in os.listdir(str_path) if name[-3:] in ['.ma','.mb'] ]
    else:
        return find_files(str_path,matchArg)
        #raise NotImplementedError,'matchArg handler not in | matchArg: {0}'.format(matchArg)
    return result

'''
	def getLibraryClips( self, library ):
		clips = {presets.LOCAL: [], presets.GLOBAL: []}
		possibleTypes = AnimClipPreset, PoseClipPreset
		for locale, localeClips in clips.iteritems():
			for dir in self._presetManager.getPresetDirs(locale):
				dir += library
				if not dir.exists():
					continue

				for f in dir.files():
					for clipType in possibleTypes:
						if f.hasExtension( clipType.EXT ):
							localeClips.append( clipType( locale, library, f.name() ) )
'''

def returnPyFilesFromFolder():
    import os
    thisFile = cgmPath.Path( __file__ )
    thisPath = thisFile.up()


    bufferList = find_files(thisPath, '*.py')
    returnList = []

    for file in bufferList:
        if '__' not in file:
            splitBuffer = file.split('.')
            returnList.append(splitBuffer[0])               
    if returnList:
        return returnList
    else:
        return False

def find_files(base, pattern):
    import fnmatch
    import os

    '''Return list of files matching pattern in base folder.'''
    """ http://stackoverflow.com/questions/4296138/use-wildcard-with-os-path-isfile"""
    return [n for n in fnmatch.filter(os.listdir(base), pattern) if
            os.path.isfile(os.path.join(base, n))]


def get_module_data(path = None, level = None, mode = 0, cleanPyc = False):
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
    _str_func = 'get_module_data'
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
        log.info(cgmGEN._str_subLine)        
        log.info("|{0}| >> Found {1} pyc files under: {2}".format(_str_func,len(_l_pyc),path))
        for m in _l_pyc:
            print(m)
        return _l_pyc   
    
    if _b_debug:
        cgmGEN.log_info_dict(_d_files,"Files")
        cgmGEN.log_info_dict(_d_names,"Imports")
    
    if _l_duplicates:
        log.debug(cgmGEN._str_subLine)
        log.error("|{0}| >> DUPLICATE MODULES....")
        for m in _l_duplicates:
            if _b_debug:print(m)
    log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),path))
    
    log.debug(cgmGEN._str_subLine)    
    log.debug("|{0}| >> Ordered MODULES....".format(_str_func))
    for k in _l_ordered_list:
        if _b_debug:print(k)
        
    log.debug(cgmGEN._str_subLine)
    log.debug("|{0}| >> PYCD MODULES({1})....".format(_str_func,len(_l_pycd)))
    for k in _l_pycd:
        if _b_debug:print(k)
            
    return _d_files, _l_ordered_list, _l_pycd


def import_file(mFile = None, namespace = None):
    """
    Import a file with a list of items
    """
    _str_func = 'import_file'
    
    if not os.path.exists(mFile):
        log.error("|{0}| >> File doesn't exist: '{1}'".format(_str_func,mFile))
        return False
    
    _i = 0
    _name = 'IMPORT_{0}'.format(_i)
    while mc.objExists(_name):
        _i +=1
        _name = 'IMPORT_{0}'.format(_i)
    
    kws = {}
    if namespace is not None:
        kws = {'namespace':namespace}
        
    if cgmGEN.__mayaVersion__ == 11111:
        if 'cat' == 'dog':
            #file -import -type "mayaAscii"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "test" -options "v=0;"  -pr  -importFrameRate true  -importTimeRange "override" "D:/Dropbox/cgmMRS/maya/demo/mrsMakers_gettingStarted/sphere.ma";
    
            #_str =  'file -import -pr -prompt false -options "v=0;" -gn "{0}" -gr'.format(_name)
            _str =  'file -import -ignoreVersion -ra true -mergeNamespacesOnClash false -pr -options "v=0;" -gn "{0}" -gr'.format(_name)
            
            if namespace is not None:
                _str = _str + ' -namespace "{0}"'.format(namespace)
            fileString = str(mFile)
            l_fileString = list(fileString)
            for i,v in enumerate(l_fileString):
                if v == '\\':
                    l_fileString[i] = '/'
            _str = '{0} "{1}";'.format(_str,''.join(l_fileString))
            log.warning("|{0}| >> 2018 import: {1}".format(_str_func,_str))
            print _str
            MEL.eval(_str)
    #Do not use the prompt flag!
    mc.file(mFile, i = True, pr = True, force = True,  gn = _name, gr = True, **kws) 
            

    
    _l = mc.listRelatives (_name, children = True, type='transform',fullPath=True) or []
    _res = []
    for c in _l:
        _res.append(mc.parent(c, world = True)[0])
    
    mc.delete(_name)    
    return _res
    
    
def verify_dir_fromDict(root = None, d = {}, case = None):
    l_keys = []
    d_toDo = {}

    _str_func = 'verify_dir_fromDict'
    log.info("|{0}| >>...".format(_str_func))
    
    mRoot = cgmPath.Path(root)
    if not mRoot.exists():
        
        log.error("Invalid root: {0}".format(root))
        return False

    _pathRoot = mRoot.asFriendly()
    log.info("|{0}| >> root: {1}".format(_str_func,_pathRoot))
    
    for k,l in d.iteritems():
        #log.info("|{0}| >> k: {1}".format(_str_func,k))
        if case == 'lower':
            k = k.lower()
            
        mDir =  cgmPath.Path( os.path.join(mRoot, k))
        if not mDir.exists():
            os.makedirs(mDir)
            log.warning("created dir: {0}".format(mDir))
            
        
        for k2 in l:
            if case == 'lower':
                k2 = k2.lower()
                
            mSub = cgmPath.Path( os.path.join(mRoot, k, k2))
            if not mSub.exists():
                os.makedirs(mSub)
                log.warning("created dir: {0}".format(mSub))                
            
        
def find_emptyDirs(path = None, 
                   addFile = False,
                   delEmpty = False,
                   level = None,):
    """
    Function for walking below a given directory looking for empty directories
    
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
    _str_func = 'find_emptyDirs'
    _b_debug = log.isEnabledFor(logging.DEBUG)

    _path = PATH.Path(path)
    
    _l_subs = []
    _d_files = {}
    _d_names = {}
    _l_empty = []
    _l_new = []
    _l_removed = []
    
    _base = _path.split()[-1]
    
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
        
        log.debug( dirs )
        log.debug(files )
        
        if not dirs and not files:
            _l_empty.append(root)
            
            if delEmpty:
                os.rmdir(root)
                _l_removed.append(root)
                continue
            
            if addFile:
                _new = os.path.join(root,"empty.txt")
                #open(_new,'x')
                os.close(os.open(_new, os.O_CREAT|os.O_EXCL))#...from stack https://stackoverflow.com/questions/43081859/how-to-create-empty-file-in-python
                _l_new.append(_new)


        if level is not None and _i >= level:break 
        _i +=1
        
    if _l_empty and not addFile:
        log.info(log_sub(_str_func,"Empty..."))
        pprint.pprint(_l_empty)
        log.info(cgmGEN._str_subLine)
    if _l_new:
        log.info(log_sub(_str_func,"New..."))        
        pprint.pprint(_l_new)
        log.info(cgmGEN._str_subLine)
        
    if _l_removed:
        log.info(log_sub(_str_func,"Removed..."))        
        pprint.pprint(_l_removed)
        log.info(cgmGEN._str_subLine)        
        
    return
 
def find_tmpFiles(path = None, level = None, cleanFiles = False,
                  endMatch = ['_batch.py','_MRSbatch.py'],
                  l_mask = ['max',
                            'mab',
                            'markdown',
                            'mapping']):
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
    _str_func = 'find_tmpFiles'
    _b_debug = log.isEnabledFor(logging.DEBUG)

    _path = PATH.Path(path)
    
    _l_subs = []
    _d_files = {}
    _d_names = {}
    
    _l_duplicates = []
    _l_errors = []
    _base = _path.split()[-1]
    _l_ordered_list = []
    _l_weirdFiles = []
    _d_weirdFiles = {}
    
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
            
            if '.' not in f:
                continue
            
            _dot_split = f.split('.')
            _extension = _dot_split[-1]
            _pre = _dot_split[0]
            
            if _extension in l_mask:
                continue
            
            if len(_extension) > 3:
                if _extension.startswith('ma') or _extension.startswith('mb'):
                    _l_weirdFiles.append(f)
                    _d_weirdFiles[f] = os.path.join(root,f)
                    continue
            
            for s in endMatch:
                if f.endswith(s):
                    _l_weirdFiles.append(f)
                    _d_weirdFiles[f] = os.path.join(root,f)
                    continue                
            

        if level is not None and _i >= level:break 
        _i +=1
        
    if cleanFiles:
        _len = 0
        for f,_path in _d_weirdFiles.iteritems():
            try:
                log.warning("Remove: {0}".format(_path))
                os.remove( _path )
                _len+=1                
            except WindowsError, e:
                try:
                    log.info("|{0}| >> Initial delete fail. attempting chmod... ".format(_str_func))                          
                    os.chmod( _path, stat.S_IWRITE )
                    os.remove( _path )
                    _len+=1                    
                except Exception,e:
                    for arg in e.args:
                        log.error(arg)   
                    raise RuntimeError,"Stop"
            
                
        log.warning("|{}| >> deleted [{}] files".format(_str_func,_len))                          
    else:
        if _d_weirdFiles:
            pprint.pprint(_d_weirdFiles)
            log.warning( cgmGEN.logString_msg(_str_func,"Found {0} files".format(len(_d_weirdFiles.keys()))) )
        else:
            log.warning( cgmGEN.logString_msg(_str_func,"No files found.") )
    return
    """
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
        """
    #return _d_files, _l_ordered_list, _l_pycd
    
    
def dup_filesInPath(path = None, count = 1, level = None, test= True):
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
    _str_func = 'find_tmpFiles'
    _b_debug = log.isEnabledFor(logging.DEBUG)

    _path = PATH.Path(path)
    _base = _path.split()[-1]
    
    l_files = []
    
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
        
        
        for f in files:
            key = False
            _pycd = False
            _long = os.path.join(root,f)
            if '.' not in f:
                continue
            if f.endswith('.meta'):
                continue
            
            print f
            
            _dot_split = f.split('.')
            _extension = _dot_split[1:]
            _pre = _dot_split[0]
            
            for i in range(count):
                newFilename = os.path.normpath(_pre + '_{0}'.format(i+1) + '.' + '.'.join(_extension))
                newFilename = os.path.join(root, newFilename)
                print newFilename
                if not test:copyfile(os.path.normpath(_long), newFilename)
                

            

        if level is not None and _i >= level:break 
        _i +=1

    return


def mkdir_recursive(path):
    #https://stackoverflow.com/questions/6004073/how-can-i-create-directories-recursively
    sub_path = os.path.dirname(path)
    if not os.path.exists(sub_path):
        mkdir_recursive(sub_path)
    if not os.path.exists(path):
        os.mkdir(path)
        


def rename_filesInPath(path = None, search = '', replace = '', test = False):
    """
    Function for walking below a given directory 
    
    :parameters
        path(str)
        search(str) | search for
        replace(str) | replace with
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
    _str_func = 'find_tmpFiles'
    #_b_debug = log.isEnabledFor(logging.DEBUG)
    
    if not search and replace:
        raise ValueError, log_msg(_str_func,"Must have search and replace")
    
    _path = PATH.Path(path)
    _base = _path.split()[-1]
    
    l_files = []
    
    log.info("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))
    
    #First loop for dirs...
    for root, dirs, files in os.walk(path, True, None):
        # Parse all the files of given path and reload python modules
        _mRoot = PATH.Path(root)
        _split = _mRoot.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]
        
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_splitUp))

                    
        for d in dirs:
            log.debug(log_sub(_str_func,"Dir: {0}".format(d)))
            if search in d or search == d:#d.find(search) > 0:
                dRenamed = d.replace(search,replace)
                dPathSource = os.path.join(root, d) #get path
                dPathTarget = os.path.join(root, dRenamed) #new path
                
                log.debug(log_msg(_str_func, "Source: {0}".format(dPathSource)))
                log.debug(log_msg(_str_func, "Target: {0}".format(dPathTarget)))
                if not test:
                    os.rename(dPathSource,dPathTarget)  
                    
    #First loop for dirs...
    for root, dirs, files in os.walk(path, True, None):
        # Parse all the files of given path and reload python modules
        _mRoot = PATH.Path(root)
        _split = _mRoot.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]
        
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_splitUp))

                
        for f in files:
            log.debug(log_sub(_str_func,"f: {0}".format(f)))
            if search in f or search == f:#d.find(search) > 0:
                dRenamed = f.replace(search,replace)
                dPathSource = os.path.join(root, f) #get path
                dPathTarget = os.path.join(root, dRenamed) #new path
                
                log.debug(log_msg(_str_func, "Source: {0}".format(dPathSource)))
                log.debug(log_msg(_str_func, "Target: {0}".format(dPathTarget)))
                if not test:
                    os.rename(dPathSource,dPathTarget)
                    

    return


def dup_dirsBelow(pathSource = None, pathTarget = None,  search = '', replace = '', test = False, skip = ['meta','.mayaSwatches']):
    """
    Function for walking below a given directory 
    
    """    
    _str_func = 'dup_dirsInPath'
    #_b_debug = log.isEnabledFor(logging.DEBUG)
    
    if not search and replace:
        raise ValueError, log_msg(_str_func,"Must have search and replace")
    
    _path = PATH.Path(pathSource)
    _base = _path.split()[-1]
    
    l_files = []
    
    log.info("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))
    
    #First loop for dirs...
    for root, dirs, files in os.walk(pathSource, True, None):
        # Parse all the files of given path and reload python modules
        _mRoot = PATH.Path(root)
        _split = _mRoot.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base)+1:]
        
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_splitUp))

        
        for d in dirs:
            if not _splitUp:
                continue
            if d in skip:
                continue
            #if d == _split[0]:
                #continue
            
            log.debug(log_sub(_str_func,d))
            
            dPathSource = os.path.join(root, d) #get path
            _pathTarget = [pathTarget] + _splitUp + [d]
            dPathTarget = os.path.join(*_pathTarget) #new path

            log.debug(log_msg(_str_func, "Source: {0}".format(dPathSource)))
            log.debug(log_msg(_str_func, "Target: {0}".format(dPathTarget)))            
            if not test:
                mkdir_recursive(dPathTarget)
            
            """
            if search in d or search == d:#d.find(search) > 0:
                dRenamed = d.replace(search,replace)
                dPathSource = os.path.join(root, d) #get path
                dPathTarget = os.path.join(root, dRenamed) #new path
                
                log.debug(log_msg(_str_func, "Source: {0}".format(dPathSource)))
                log.debug(log_msg(_str_func, "Target: {0}".format(dPathTarget)))
                if not test:
                    pass#os.rename(dPathSource,dPathTarget)  """
            
def dup_structure(pathSource = None, pathTarget = None,  copyFiles = False, search = '', replace = '', test = False, skip = ['.mayaSwatches']):
    """
    Function for walking below a given directory 
    
    """
    _str_func = 'dup_dirsInPath'
    from shutil import copyfile
    
    #_b_debug = log.isEnabledFor(logging.DEBUG)
    
    if not search and replace:
        raise ValueError, log_msg(_str_func,"Must have search and replace")
    
    _path = PATH.Path(pathSource)
    _base = _path.split()[-1]
    
    l_files = []
    
    log.info("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))
    
    #First loop for dirs...
    for root, dirs, files in os.walk(pathSource, True, None):
        # Parse all the files of given path and reload python modules
        _mRoot = PATH.Path(root)
        _split = _mRoot.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base)+1:]
        
        #_rootUse = os.path.join(*_split)
        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_split))        
        log.debug("|{0}| >> On splitup: {1}".format(_str_func,_splitUp))    
        
        if _splitUp and _splitUp[-1] in skip:
            log.debug(log_sub(_str_func,"skip found: {0}".format(d)))                
            continue

        
        for d in dirs:
            if not _splitUp:
                continue
            if d in skip:
                log.debug(log_sub(_str_func,"skip found: {0}".format(d)))                
                continue
            #if d == _split[0]:
                #continue
            
            log.debug(log_sub(_str_func,d))
            
            dPathSource = os.path.join(root, d) #get path
            _pathTarget = [pathTarget] + _splitUp + [d]
            dPathTarget = os.path.join(*_pathTarget) #new path

            log.debug(log_msg(_str_func, "Source: {0}".format(dPathSource)))
            log.debug(log_msg(_str_func, "Target: {0}".format(dPathTarget)))            
            if not test:
                mkdir_recursive(dPathTarget)
            
        if copyFiles:
            dPathSource = root #get path
            _pathTarget = [pathTarget] + _splitUp
            dPathTarget = os.path.join(*_pathTarget) #new path
            if not test:
                mkdir_recursive(dPathTarget)
            
            for f in files:
                log.debug(log_sub(_str_func,"f: {0}".format(f)))
                fPathSource =  os.path.join(dPathSource, f)
                fPathTarget =  os.path.join(dPathTarget, f)
                """
                _good = True
                for k in _splitUp:
                    if k in skip:
                        log.debug(log_sub(_str_func,"skip found: {0}".format(fPathSource)))
                        _good = False
                        continue                    
                if not _good:
                    continue"""
                
                log.debug(log_msg(_str_func, "Source: {0}".format(fPathSource)))
                log.debug(log_msg(_str_func, "Target: {0}".format(fPathTarget)))
                
                if not test:
                    copyfile(fPathSource, fPathTarget)
                    log.info(log_msg(_str_func, "Target: {0}".format(fPathTarget)))
                
                
                """
                if search in f or search == f:#d.find(search) > 0:
                    dRenamed = f.replace(search,replace)
                    dPathSource = os.path.join(root, f) #get path
                    dPathTarget = os.path.join(root, dRenamed) #new path
                    
                    log.debug(log_msg(_str_func, "Source: {0}".format(dPathSource)))
                    log.debug(log_msg(_str_func, "Target: {0}".format(dPathTarget)))
                    if not test:
                        os.rename(dPathSource,dPathTarget)"""
                """
                if search in d or search == d:#d.find(search) > 0:
                    dRenamed = d.replace(search,replace)
                    dPathSource = os.path.join(root, d) #get path
                    dPathTarget = os.path.join(root, dRenamed) #new path
                    
                    log.debug(log_msg(_str_func, "Source: {0}".format(dPathSource)))
                    log.debug(log_msg(_str_func, "Target: {0}".format(dPathTarget)))
                    if not test:
                        pass#os.rename(dPathSource,dPathTarget)  """
            
            
#-------------------------------------------------------------------------------
# Name:        get_image_size
# Purpose:     extract image dimensions given a file path using just
#              core modules
#
# Author:      Paulo Scardine (based on code from Emmanuel VAISSE)
#
# Created:     26/09/2013
# Copyright:   (c) Paulo Scardine 2013
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import struct

class UnknownImageFormat(Exception):
    pass

def get_image_size(file_path):
    """
    Return (width, height) for a given img file content - no external
    dependencies except the os and struct modules from core
    """
    size = os.path.getsize(file_path)

    with open(file_path) as input:
        height = -1
        width = -1
        data = input.read(25)

        if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
            # GIFs
            w, h = struct.unpack("<HH", data[6:10])
            width = int(w)
            height = int(h)
        elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
              and (data[12:16] == 'IHDR')):
            # PNGs
            w, h = struct.unpack(">LL", data[16:24])
            width = int(w)
            height = int(h)
        elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
            # older PNGs?
            w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)
        elif (size >= 2) and data.startswith('\377\330'):
            # JPEG
            msg = " raised while trying to decode as JPEG."
            input.seek(0)
            input.read(2)
            b = input.read(1)
            try:
                while (b and ord(b) != 0xDA):
                    while (ord(b) != 0xFF): b = input.read(1)
                    while (ord(b) == 0xFF): b = input.read(1)
                    if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                        input.read(3)
                        h, w = struct.unpack(">HH", input.read(4))
                        break
                    else:
                        input.read(int(struct.unpack(">H", input.read(2))[0])-2)
                    b = input.read(1)
                width = int(w)
                height = int(h)
            except struct.error:
                raise UnknownImageFormat("StructError" + msg)
            except ValueError:
                raise UnknownImageFormat("ValueError" + msg)
            except Exception as e:
                raise UnknownImageFormat(e.__class__.__name__ + msg)
        else:
            raise UnknownImageFormat(
                "Sorry, don't know how to get information from this file."
            )

    return width, height