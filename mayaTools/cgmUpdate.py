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
__version__ = '1.0.05162020'

from urllib2 import Request, urlopen, URLError
import urllib2
import webbrowser
import json
import pprint
import os
import zipfile
from shutil import move,rmtree
import datetime
import time

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
_test = 'MRS'

_pathMain = 'https://github.com/jjburton/cgmtools/commits/'
_pathPull =  "https://github.com/jjburton/cgmtools/get/"
#_pathMount  = 'https://api.github.com/repos/jjburton/cgmTools/commits/'

_pathMount  = 'https://api.bitbucket.org/2.0/repositories/jjburton/cgmtools/commits/'
#_pathRepos = 'https://api.bitbucket.org/2.0/repositories/jjburton/cgmtools/'


"""
_pathMain = 'https://bitbucket.org/jjburton/cgmtools/commits/'
_pathPull =  "https://bitbucket.org/jjburton/cgmtools/get/"
_pathMount  = 'https://api.bitbucket.org/2.0/repositories/jjburton/cgmtools/commits/'
_pathRepos = 'https://api.bitbucket.org/2.0/repositories/jjburton/cgmtools/'"""

_defaultBranch = 'stable'
_sep = os.sep

global CGM_BUILDS_DAT
CGM_BUILDS_DAT = {}

import maya.cmds as mc
import maya.mel as mel

def get_install_path(confirm = False,branch=_defaultBranch):
    """
    Install to this location...
    """
    _str_func = 'get_install_path'
    
    _path = False
    _warn = None
    _path_cgm = None
    
    try:
        #First we'll see if we have cgm installed...
        try:
            import cgm
            _path_cgm = cgm.__file__
            _path_cgm = os.path.abspath(_path_cgm)
            _path_cgm = _sep.join(_path_cgm.split(_sep)[:-2])            
            log.debug("|{0}| >> cgm path found: {1}".format(_str_func,_path_cgm))
        except:
            _path_cgm = False
        
        _path = os.path.abspath(__file__)        
        _path = _sep.join(__file__.split(_sep)[:-1])
        _path = os.path.abspath(_path)
        for check in ['repos','mayaTools']:
            if check in _path:
                _warn = " WARNING: Please don't install to your repos!Found check kw: '{0}' \n path: {1}".format(check,_path)
                log.warning(_warn)
                break
                #_path = False
    except:pass
    
    log.debug("|{0}| >> path here found: {1}".format(_str_func,_path_cgm))
    
    #pprint.pprint(vars())
    if _path_cgm:
        if os.path.normcase(_path_cgm) in [os.path.normcase(_path)]:
            log.debug("|{0}| >> paths match.".format(_str_func))
    
    if confirm:
        try:_dat = get_dat(branch,1)
        except Exception,err:
            log.error(err)
            _dat = False
        if not _dat:
            log.error("Failed to get branch dat")            
            return False
        _msg = 'Would you like to install cgmTools here: \n [ {0} ] \n  {1} \n Branch: {2} || Last Updated: {3} \n {4} \n {5}'.format(_path,'-'*100,branch,_dat[0]['date'], _dat[0]['msg'],'-'*100)
        if _warn:
            _msg = _msg + "\n {0}".format(_warn)
        _res_confirm = mc.confirmDialog(title="Install cgmTools",
                                        message = _msg,
                                        messageAlign='center',
                                        button=['OK', 'Pick New','Cancel'],
                                        defaultButton='OK',
                                        cancelButton='Cancel',
                                        dismissString='Cancel')
        if _res_confirm == 'OK':
            log.debug("|{0}| >> install here...".format(_str_func))
        elif _res_confirm == 'Pick New':
            log.debug("|{0}| >> pick...".format(_str_func))
            
            _res_pick = mc.fileDialog2(dialogStyle=2,
                                       cap = "Pick a new location please. Warning - if this path isn't in Maya's path library, install will fail.",
                                       startingDirectory = _path,
                                       fileMode = 2,
                                       okCaption = 'Install')
            if _res_pick:
                _path = os.path.abspath(_res_pick[0])
                log.debug("|{0}| >> install here...".format(_str_func))
                log.debug("|{0}| >> {1}".format(_str_func,_path))
                return _path
            else:
                return log.error("|{0}| >> Cancelled".format(_str_func))  
            
            
        else:
            return log.error("|{0}| >> Cancelled".format(_str_func))  
    return _path
    


_l_to_clean = ['cgm','cgmToolbox.mel','cgmToolbox.py','Red9',]#...'cgmUpdate.py'
def clean_install_path(path = None):
    if path == None:
        path = get_install_path()
        for check in ['repos','mayaTools']:
            if check in path:
                return log.error("Please don't clean your repos. Found check: '{0}' | path: {1}".format(check,path))
    
    _path = os.path.abspath(path)
    #pprint.pprint(vars())
    
    for f in os.listdir(_path):
        if f in _l_to_clean:
            try:
                _pathFile = _sep.join([_path,f])
                log.debug("Cleaning: {0} >> {1} ...".format(f,_pathFile))
                if '.' in f:
                    os.unlink(_pathFile)
                else:
                    rmtree(_pathFile)
            except Exception,err:log.warning("Clean fail| {0} | {1}".format(f,err))
                
     
    
#zFile = 'D:\\Dropbox\\My Documents\\maya\\2018\\scripts\\stuff.zip'
zFile = 'D:\\Dropbox\\My Documents\\maya\\2018\\scripts\\0c122db7cfd4d0269df8be1bf72269c4b86d3870.zip'

def unzip(zFile = zFile, deleteZip = True, cleanFirst = False, targetPath = None):
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
    _zipRoot = None
    _name_list = zip_ref.namelist()
    
    if cleanFirst:
        log.debug("Unzip: cleaning...")        
        clean_install_path(_dir)                
    
    try:
        mayaMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
        mc.progressBar( mayaMainProgressBar,
                        edit=True,
                        beginProgress=True,
                        isInterruptable=True,
                        status="Exctracting: {0}".format(_path),
                        minValue = 0,
                        step=1,
                        vis=True,
                        maxValue= len(_name_list))
        
        for i,f in enumerate(zip_ref.namelist()):
            mc.progressBar(mayaMainProgressBar,
                           edit=True,
                           progress = i)
            
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
                if not _zipRoot:
                    _zipRoot = ''.join(f.split('mayaTools')[0])
                    _match = True
                    while _match:
                        for c in ["/",_sep]:
                            if _zipRoot.endswith(c):
                                _zipRoot=''.join(list(_zipRoot)[:-1])
                        _match = False
                        
                zip_ref.extract(f,_dir)
        zip_ref.close()
        
        log.debug("Dir: {0}".format(_dir))
        log.debug("Zip Dir: {0}".format(_zipDir))
        log.debug("Zip Root: {0}".format(_zipRoot))
        
        if targetPath:
            _path_target = os.path.abspath(targetPath)
        else:
            _path_target = _dir
            
        _path_mayaTools = _sep.join([_dir,_zipDir,'mayaTools'])
            
        log.debug("Path mayaTools: {0}".format(_path_mayaTools))
        
        for f in os.listdir(_path_mayaTools):
            _dst = _sep.join([_path_target,f])
            _src = _sep.join([_path_mayaTools,f])
            log.debug("Copy: {0} >> {1} ...".format(_src,_dst))
            
            try:move(_src, _dst)
            except:pass
            
        try:rmtree(_sep.join([_dir,_zipDir]))
        except Exception,err:log.debug("Remove unzip temp fail | {0}".format(err))
            

        
    except Exception, err:
        log.error("Zip exception: {0}".format(err))
    finally:
        if mayaMainProgressBar:mc.progressBar(mayaMainProgressBar, edit=True, endProgress=True)
        if deleteZip:
            try:os.unlink(zFile)
            except Exception,err:log.error("Delete zip fail | {0}".format(err))        

def download(url='http://weknowyourdreams.com/images/mountain/mountain-03.jpg', mode = None):
    """
    :Attribution
    https://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
    
    """
    log.debug(" url: {0}".format(url))
        
    if mode == 'default':
        file = webbrowser.open(url, new=0, autoraise=True)    
        log.info("Go check your default download folder for: {0}".format(''.join(url.split('/')[-1])))
        return
    
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
                prcnt = file_size_dl * 100. / file_size
                #status = r"%10d  [%3.2f%%]" % (file_size_dl, prcnt)
                status = r"  [%3.2f%%]" % (prcnt,)
                mc.progressBar(mayaMainProgressBar,
                               edit=True,
                               progress = (int(prcnt))-1,
                               maxValue=100)
                #status = status + chr(8)*( int(prcnt))
                #print( status )
        f.close()
        return file_name
    except URLError, e:
            print 'It appears this is not working...URL or Timeout Error :(', e
    finally:
        if mayaMainProgressBar:mc.progressBar(mayaMainProgressBar, edit=True, endProgress=True)
        
        print '...'            
    

def get_download(branch = _defaultBranch, idx = 0,  mode = None):
    """
    
    """   
    #pprint.pprint(_dat)
    
    #Get our zip   
    try:_dat = get_dat(branch,idx+1)[idx]
    except:_dat=None
    
    if not _dat:
        return log.error("No build dat found. {0} | idx: {1}".format(branch,idx))
    
    url =  "https://github.com/jjburton/cgmTools/archive/" + _dat['hash'] + ".zip"
    log.debug(" url: {0}".format(url))    
    
    if mode == 'url':
        return url
    
    #Download...
    _zip = download(url)
    return _zip

def get_build_bit(branch = _defaultBranch, idx = 0, mode = None):
    """
    
    """
    if idx is None:
        idx = int(raw_input("Enter Commit # (1-10) to download a download associated .zip files: "))
        if idx is None:
            return log.error("No idx. {0} | idx: {1}".format(branch,idx))
            
    
    try:_dat = get_dat(branch)[idx]
    except:_dat=None
    
    if not _dat:
        return log.error("No build dat found. {0} | idx: {1}".format(branch,idx))
    
    #pprint.pprint(_dat)
    
    #Get our zip
    url =  "https://bitbucket.org/jjburton/cgmtools/get/" + _dat['hash'] + ".zip"
    log.debug(" url: {0}".format(url))
    
    if mode == 'url':
        return url
    
    #Download...
    _zip = download(url)
    return _zip

def get_dat(branch = 'master', limit = 3, update = False, reportMode=False):
    """
    
    """
    """branch = raw_input("Enter the name of the Branch ('Master' or 'Stable') to see a summary of last 10 commits: ")"""
    _str_func = 'get_dat'
    print '='*100            
    print("|{0}| >> Branch: {1}".format(_str_func,branch))
    
    global CGM_BUILDS_DAT
    #pprint.pprint(CGM_BUILDS_DAT)
    
    if CGM_BUILDS_DAT and not update:
        _dat = CGM_BUILDS_DAT.get(branch,None)
        if _dat:
            log.debug('Checking buffer...')
            if len(_dat) >= limit:
                log.debug("passing buffer...")                          
                return _dat
            
    route = 'https://api.github.com/repos/jjburton/cgmTools/commits?sha=' + branch
    
    #request = Request(route)
    print("|{0}| >> Route: {1}".format(_str_func,route))
    
    try:
        response = urlopen(route)
        stable = json.load(response)
        _l_res = []
        #pprint.pprint(stable)
        i = 0
        for idx,d in enumerate(stable):
            if i >= limit:
                break
            print '-'*100
            
            #pprint.pprint(d)
            _dCommit = d['commit']
            _hash = d['sha']
            _msg = _dCommit['message']
            _dateRaw= _dCommit['committer']['date']
            
            try:
                _tmp = datetime.datetime.strptime( _dateRaw[:-1], "%Y-%m-%dT%H:%M:%S")
                _date = _tmp.strftime("%m.%d.%Y - %H:%M:%S").__str__()                
            except:_date = _dateRaw
            
            _l_res.append({'hash':_hash,
                           'msg': _msg,
                           'date':_date,
                           'dateRaw':_dateRaw,
                           'url':d['html_url'],
                           'dateRaw':_dateRaw})
            print("{0} | {1} ...".format(idx,
                                                  _date,
                                                  _msg,
                                                  ))
            print _msg
            #print '...' + "{0}{1}".format(_pathMain,_hash)

            i+=1
            
        #_len = len(stable)
        #log.debug("|{0}| >> Showing {1} of {2}".format(_str_func,limit,_len))
        
        #pprint.pprint(_l_res)
        CGM_BUILDS_DAT[branch] = _l_res
        print '='*100        
        
        if reportMode:
            return        
        return _l_res 

    except URLError, e:
        pprint.pprint(vars())
        print 'It appears this is not working...URL or Timeout Error :(', e
        print 'More than likely your internet is down or the server is.'
    finally:
        print '...'
        
def get_dat_bit(branch = 'master', limit = 3, update = False):
    """
    
    """
    """branch = raw_input("Enter the name of the Branch ('Master' or 'Stable') to see a summary of last 10 commits: ")"""
    
    _str_func = 'get_dat'
    log.debug("|{0}| >> Branch: {1}".format(_str_func,branch))
    
    global CGM_BUILDS_DAT
    #pprint.pprint(CGM_BUILDS_DAT)
    
    if CGM_BUILDS_DAT and not update:
        _dat = CGM_BUILDS_DAT.get(branch,None)
        if _dat:
            log.debug('Checking buffer...')
            if len(_dat) >= limit:
                log.debug("passing buffer...")                          
                return _dat
            
    route = _pathMount + branch

    request = Request(route)
    log.debug("|{0}| >> Route: {1}".format(_str_func,request))
    
    try:
        response = urlopen(request)
        stable = json.load(response)
        _l_res = []
        _len = len(stable['values'])
        log.debug("|{0}| >> List of {1}".format(_str_func,_len))
        
        for idx in range(_len):
            if idx == limit:break
            #log.debug('-'*80)            
            _hash = stable['values'][idx]['hash']
            _msg = stable['values'][idx]['message']
            _dateRaw= stable['values'][idx]['date']
            
            try:_date = datetime.datetime.strptime( _dateRaw[:-6], "%Y-%m-%dT%H:%M:%S").__str__()
            except:_date = _date
            
            _l_res.append({'hash':_hash,
                           'msg': _msg,
                           'date':_date,
                           'dateRaw':_dateRaw})
            log.debug("{0} | {1}{2} | date: {3} |msg: {4}".format(idx,
                                                                  _pathMain,
                                                                  _hash,
                                                                  _date,
                                                                  _msg,
                                                                  ))
            
        #pprint.pprint(_d_res)
        pprint.pprint(_l_res)
        CGM_BUILDS_DAT[branch] = _l_res
        return _l_res 

    except URLError, e:
        pprint.pprint(vars())
        print 'It appears this is not working...URL or Timeout Error :(', e
    finally:
        print '...'

def get_branch_names():
    _str_func = 'get_branch_names'
    
    route = _pathRepos + 'refs/branches'
    log.debug("|{0}| >> Route: {1}".format(_str_func,route))
    
    request = Request(route)
    log.debug('Route: {0}'.format(request))
    
    try:
        response = urlopen(request)
        stable = json.load(response)
        idx = 1
        _res = []
        
        #pprint.pprint(stable.get('values'))
        for i,d_branch in enumerate(stable.get('values',[])):
            _name = d_branch.get('name')
            if _name:
                _res.append(_name)
            log.debug('name: {0} : {1}'.format(i,d_branch.get('name')))
        
        return _res
        """
        while _dat
        while idx < 50 +1:
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
        """
    except URLError, e:
        print 'It appears this is not working...URL or Timeout Error :(', e
    finally:
        print '...'

def here(branch = _defaultBranch, idx = 0, cleanFirst = True, run = True):
    """
    """
    _str_func = 'here'
    _path = get_install_path(True,branch)
    if not _path:
        return log.error("|{0}| >>No Path picked...".format(_str_func,_path))

    log.debug("|{0}| >> path: {1}".format(_str_func,_path))
    
    #get_dat(branch,5,update=True)
    try:
        #_zip = get_build(branch,idx)
        _zip = get_download(branch,idx)
    except Exception,err:
        log.error(err)
        
        log.error("|{0}| >> Failed to acquire zip. Check branch name: {1}".format(_str_func,branch))
        return
    
    if not _zip:
        log.error("|{0}| >> Failed to acquire zip. Most likely invalid branch string: {1}".format(_str_func,branch))
        return        
    
    
    log.debug("|{0}| >> zip: {1}".format(_str_func,_zip))
    
    unzip(_zip,True,cleanFirst, targetPath=_path)
    
    if run:
        try:
            mel.eval('rehash')
            import cgm
            cgm.core._reload()
            mel.eval('cgmToolbox')
        except Exception,err:
            return log.error("Failed to load cgm | {0}".format(err))



def gitHub(branch = 'master'):
    response= urlopen('https://api.github.com/repos/jjburton/cgmTools/commits')
    

def ryan():

    while 1==1:
        branch = raw_input("Enter the name of the Branch ('Master' or 'Stable') to see a summary of last 10 commits: ")
        mount = 'https://api.bitbucket.org/2.0/repositories/jjburton/cgmtools/commits/?until='
        if (branch == 'master' or branch == 'Master' or branch== 'MASTER'):
            route = mount+'master'
            break
        if (branch == 'stable' or branch == 'Stable' or branch == 'STABLE'):
            route = mount+'stable'
            break
    request = Request(route)
    
    try:
        response = urlopen(request)
        stable = json.load(response)
        idx = 1
        last10 = []
        print 'Here Are the Last 10 Commits:'
    
        while idx < 11:
            hsh = stable['values'][idx]['hash']
            msg = stable['values'][idx]['message']
            last10.append({'hash':hsh, 'message':msg, 'index':idx})
            print '#' + str(idx) + '. ' + 'https://bitbucket.org/jjburton/cgmtools/commits/' + hsh, ' msg: ' + msg
            idx+=1
        match = 'no'
    
        while match == 'no' :
            commitIdx = int(raw_input("Enter Commit # (1-10) to download a download associated .zip files: "))
            for commit in last10 :
                if commit['index'] == commitIdx:
                    match = 'yes'
                    print 'Success! Downloading Zip Files for this commit: ' + 'https://bitbucket.org/' + commit['hash']
                    url =  "https://bitbucket.org/jjburton/cgmtools/get/" + commit['hash'] + ".zip"
                    file = webbrowser.open(url, new=0, autoraise=True)
                if match == 'no' :
                    print 'Please enter a number 1-10'
    
    except URLError, e:
        print 'It appears this is not working...URL or Timeout Error :(', e
        


