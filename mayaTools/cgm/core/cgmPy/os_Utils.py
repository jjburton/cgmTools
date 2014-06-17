"""
os_Utils
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
# From Python =============================================================
import re
import os

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core.cgmPy import validateArgs as cgmValid

#>>> Utilities
#===================================================================
def get_lsFromPath(str_path = None, 
                   matchArg = None, 
                   calledFrom = None,**kwargs):
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
    log.debug("get_lsFromPath str_path =  {1} | matchArg={0}".format(matchArg,str_path))
    
    _str_funcRoot = 'get_lsFromPath'
    if calledFrom: _str_funcName = "{0}.{1}({2})".format(calledFrom,_str_funcRoot,matchArg)    
    else:_str_funcName = "{0}({1})".format(_str_funcRoot,matchArg) 

    result = None 
    
    #>> Check the str_path
    if not isinstance(str_path, basestring):
        raise TypeError('path must be string | str_path = {0}'.format(str_path))
    if not os.path.isdir(str_path):
        raise ValueError('path must validate as os.path.isdir | str_path = {0}'.format(str_path))
    
    #try:#>> Check matchArg
    if matchArg is not None and not isinstance(matchArg, basestring):
        raise TypeError('matchArg must be string | matchArg: {0}'.format(matchArg))        
    
    if matchArg is None or matchArg in ['']:
        return [ name for name in os.listdir(str_path) ] 
    
    if '*.' in matchArg:
        #l_buffer = matchArg.split('*')        
        return [ name for name in os.listdir(str_path) if name[-3:] == matchArg.split('*')[-1]]
        
    if matchArg.lower() in ['folder','dir']:
        return [ name for name in os.listdir(str_path) if os.path.isdir(os.path.join(str_path, name)) ]
    elif matchArg.lower() in ['maya files','maya']:
        return [ name for name in os.listdir(str_path) if name[-3:] in ['.ma','.mb'] ]
    else:
        raise NotImplementedError,'matchArg handler not in | matchArg: {0}'.format(matchArg)
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