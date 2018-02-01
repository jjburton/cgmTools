"""
------------------------------------------
toolbox: cgmUpdate
Author: Josh Burton,Ryan Comingdeer
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is housed outside our core stuff to be able to access and update it.
================================================================
"""
__version__ = '0.1.01312018'

from urllib2 import Request, urlopen, URLError
import urllib2
import webbrowser
import json
import pprint
import os
import zipfile
from shutil import move

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_pathMain = 'https://bitbucket.org/jjburton/cgmtools/commits/'
_pathPull =  "https://bitbucket.org/jjburton/cgmtools/get/"
_pathMount  = 'https://api.bitbucket.org/2.0/repositories/jjburton/cgmtools/commits/?until='
_sep = os.sep

global CGM_BUILDS_DAT
CGM_BUILDS_DAT = {}

import maya.cmds as mc
import maya.mel as mel

def get_install_path():
    """
    Install to this location...
    """
    _path = False
    try:
        #First we'll see if we have cgm installed...
        _path = _sep.join(__file__.split(_sep)[:-1])
        if 'repos' in _path:
            log.error("Please don't install to your repos: {0}".format(_path))
            #_path = False
    except:pass
    
    return _path
    
def unzip(zFile = 'D://Dropbox//My Documents//maya//2018//scripts//fcb07f5e84eb0db7c97e00d9d164f9a117545e34.zip'):
    if not os.path.exists(zFile):
        return log.error("Bad zip path: {0}".format(zFile))
    
    _path = os.path.abspath(zFile)
    _dir = _sep.join(_path.split(_sep)[:-1])
    _match = True
    pprint.pprint(vars())
    
    #while _match:
    #    for c in ["/",_sep]:
    #        if _dir.endswith(c):
    #            _dir=''.join(list(_dir)[:-1])
    #    _match = False
        
    zip_ref = zipfile.ZipFile(_path, 'r')
    
    #zip_ref.extractall(_dir)
    #print zip_ref.infoList()
    #print zip_ref.getinfo()
    _done = []
    _zipDir = None
    for f in zip_ref.namelist():
        if  'mayaTools' in f:
            log.debug("Unzipping: {0}...".format(f))
            _done.append(f)
            if not _zipDir:
                _zipDir = ''.join(f.split('mayaTools')[:-1])
                _match = True
                while _match:
                    for c in ["/",_sep]:
                        if _zipDir.endswith(c):
                            _zipDir=''.join(list(_zipDir)[:-1])
                    _match = False
                    
                    
            zip_ref.extract(f,_dir)
    
    zip_ref.close()
    
    print _dir
    print _zipDir

    _path_mayaTools = _sep.join([_dir,_zipDir,'mayaTools'])
    
    for f in os.listdir(_path_mayaTools):
        _dst = _sep.join([_dir,f])
        _src = _sep.join([_path_mayaTools,f])
        log.debug("Copy: {0} >> {1} ...".format(_src,_dst))
        
        try:move(_src, _dst)
        except:pass
    
def download(url='http://weknowyourdreams.com/images/mountain/mountain-03.jpg'):
    log.debug(" url: {0}".format(url))
        
        
    #file = webbrowser.open(url, new=0, autoraise=True)    
    #log.info(file)
    
    mayaMainProgressBar = None
    file_size_dl = 0
    block_sz = 8192
    
    try:
        _dir = get_install_path()
        file_name = _sep.join([_dir,url.split('/')[-1]])
        
        u = urllib2.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        
        file_size = None
        try:file_size = int(meta.getheaders("Content-Length")[0])
        except:pass
        
        msg = "Downloading: {0} | Bytes: {1}".format (file_name, file_size)
        print msg
        

        
        mayaMainProgressBar = None
        if file_size:
            mayaMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
            mc.progressBar( mayaMainProgressBar,
                            edit=True,
                            beginProgress=True,
                            isInterruptable=True,
                            status=msg,
                            minValue = 0,
                            step=1,
                            vis=True,
                            maxValue= 100 )            
        
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
        
            file_size_dl += len(buffer)
            f.write(buffer)
            if file_size:
                status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                #mc.progressBar(mayaMainProgressBar, edit=True, step = file_size_dl * 100. / file_size)                
                #status = status + chr(8)*(len(status)+1)
                log.debug( status )
                
        f.close()
        return file_name
    except URLError, e:
            print 'It appears this is not working...URL or Timeout Error :(', e
    finally:
        if mayaMainProgressBar:mc.progressBar(mayaMainProgressBar, edit=True, endProgress=True)
        
        print '...'            
    

def get_build(branch = 'mrs', idx = 0):
    """
    
    """
    if idx is None:
        idx = int(raw_input("Enter Commit # (1-10) to download a download associated .zip files: "))
        if idx is None:
            return log.error("No idx. {0} | idx: {1}".format(branch,idx))
            
    
    _dat = get_dat(branch).get(idx,None)
    if not _dat:
        return log.error("No build dat found. {0} | idx: {1}".format(branch,idx))
    
    #pprint.pprint(_dat)
    
    #Get our zip
    url =  "https://bitbucket.org/jjburton/cgmtools/get/" + _dat['hash'] + ".zip"
    log.debug(" url: {0}".format(url))
    
    #Download...
    _zip = download(url)
    return _zip

def get_dat(branch = 'master', limit = 3, update = False):
    """
    
    """
    """branch = raw_input("Enter the name of the Branch ('Master' or 'Stable') to see a summary of last 10 commits: ")"""
    log.debug('Branch: {0}'.format(branch))
    
    global CGM_BUILDS_DAT
    pprint.pprint(CGM_BUILDS_DAT)
    
    if CGM_BUILDS_DAT and not update:
        _dat = CGM_BUILDS_DAT.get(branch,None)
        if _dat:
            log.debug('Checking buffer...')
            if len(_dat.keys()) >= limit:
                log.debug("passing buffer...")                          
                return _dat
            
    route = _pathMount + str(branch).lower()

    request = Request(route)
    log.debug('Route: {0}'.format(request))
    
    try:
        response = urlopen(request)
        stable = json.load(response)
        idx = 1
        _d_res = {}
        
        print 'Here Are the Last 10 Commits:'
    
        while idx < limit +1:
            log.debug('checking....{0}'.format(idx))
            _hash = stable['values'][idx]['hash']
            _msg = stable['values'][idx]['message']
            _d_res[idx-1] = {'hash':_hash,
                           'msg': _msg}
            print("{0} | {1}{2} | msg: {3}".format(idx,
                                                    _pathMain,
                                                    _hash,
                                                    _msg,
                                                    ))
            idx+=1
            
        #pprint.pprint(_d_res)
        CGM_BUILDS_DAT[branch] = _d_res
        return _d_res 

    except URLError, e:
        print 'It appears this is not working...URL or Timeout Error :(', e
    finally:
        print '...'
        



