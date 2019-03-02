"""
attribute_utils
Josh Burton 
www.cgmonks.com

Refactoring attribte calls to core.
"""
# From Python =============================================================
import copy
import re
import sys
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
#DO NOT IMPORT: SEARCH
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import list_utils as LISTS
from cgm.lib import lists

_l_simpleTypes = ['string','float','enum','vector','int','bool','message']
_d_attrTypes = {'message':('message','msg'),
                'double':('float','fl','f','doubleLinear','doubleAngle','double','d'),
                'string':('string','s','str'),
                'long':('long','int','i','integer'),
                'short':('short','shrt'),
                'bool':('bool','b','boolean'),
                'enum':('enum','options','e'),
                'double3':('double3','d3'),
                'float3':('vector','vec'),
                'multi':('multi','m')}

attrCompatibilityDict = {'message':('message'),
                         'double':('float','doubleLinear','doubleAngle','double'),
                         'string':('string'),
                         'long':('long','integer'),
                         'bool':('bool',),
                         'enum':('enum'),
                         'double3':('vector','double3'),
                         'multi':('multi')}

dataConversionDict = {'long':int,
                      'string':str,
                      'bool':bool,
                      'double':float} 

d_attrCategoryLists = {'transform':('translateX','translateY','translateZ',
                                    'rotateX','rotateY','rotateZ',
                                    'scaleX','scaleY','scaleZ','visibility'),
                       'joint':('rotateOrder','rotateAxisX','rotateAxisY','rotateAxisZ',
                                'inheritsTransform','drawStyle','radius',
                                'jointTypeX','jointTypeY','jointTypeZ',
                                'stiffnessX','stiffnessY','stiffnessZ',
                                'preferredAngleX','preferredAngleY','preferredAngleZ',
                                'jointOrientX','jointOrientY','jointOrientZ','segmentScaleCompensate','showManipDefault',
                                'displayHandle','displayLocalAxis','selectHandleX','selectHandleY','selectHandleZ'),
                       'objectDisplayAttrs':('visibility','template','lodVisibility'),
                       'curveShapeAttrs':('intermediateObject','dispCV','dispEP','dispHull','dispGeometry'),
                       'locatorShape':('localPositionX','localPositionY','localPositionZ',
                                       'localScaleX','localScaleY','localScaleZ'),
                       'overrideAttrs':('overrideEnabled','overrideDisplayType',
                                        'overrideLevelOfDetail','overrideShading',
                                        'overrideTexturing','overridePlayback',
                                        'overrideVisibility','overrideColor')}

#_d_compatibility= get_compatibilityDict(False)

#>>> Utilities
#===================================================================
def reset(node, attrs = None, amount = None):
    """   
    Reset specified attributes to their default values

    :parameters:
        node(str) -- 
        attrs(str/list) -- attributes to reset

    :returns
        list of reset attrs(list)
    """
    try:
        node = VALID.mNodeString(node)
    
        if attrs == None:
            attrs = mc.listAttr(node, keyable=True, unlocked=True) or False
        else:
            attrs = VALID.listArg(attrs)
        _reset = []
        for attr in attrs:
            try:
                setValue = mc.attributeQuery(attr, listDefault=True, node=node)[0]
                if amount:
                    #x + ((y - x) * blend) -----------------------------------------
                    current = get(node,attr)
                    setValue = current + ((setValue - current)*amount)
                set(node,attr,setValue)
                _reset.append(attr)
            except Exception,err:
                log.error("{0}.{1} resetAttrs | error: {2}".format(node, attr,err))   	
        return _reset
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())

    
        
def get_nameNice_string(attr):
    """
    Convert a long name to what an assumed nice name of that attribute would be. Mainly for ui checking to see if to show
    nice name or not

    :parameters:
        attr
        
    Thanks to: http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', attr)
    _res = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    _resUpper = _res.upper()
    
    return _resUpper[0] + _res[1:]

def validate_value(node, attr = None, value = None):
    """
    Validate an value to an attribute

    :parameters:
        node
        attr 
        value - 
    :returns
        None or value
    """    
    _str_func = 'validate_value'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if value is None and attr is not None:
            value = attr
    else:
        _d = validate_arg(node,attr) 
        
    _aType = get_type(_d)
    _vType = type(value)
    _b_list = False    
    if _vType in [list,tuple]:
        _b_list = True
        
    if _aType in ['long','double','double3','short','doubleAngle','doubleLinear','float','float3','time','byte','short']:
        if _aType in ['long','byte']:
            if _b_list:return [int(v) for v in value]
            return int(value)
        else:
            if _b_list:return [float(v) for v in value]
            return float(value)     
    elif _aType == 'bool':
        try:
            if value.lower() in ['t','true','tr','yes','y','1']:return True
        except:pass
        try:
            if value.lower() in ['f','false','no','n','0']:return False
        except:pass
        return bool(value)
    elif _aType == 'string':
        if _b_list:return [str(v) for v in value]
        return str(value)
    elif _aType == 'enum':
        _l = get_enum(_d).split(':')
        try:_int = int(value)
        except:_int = None
        
        if value in _l:
            return _l.index(value)
        elif _int is not None and _int <= len(_l):
            return _int
        raise ValueError,"|{0}| >>> Not a valid enum value: {1} | {2}".format(_str_func,value,_l)
    raise ValueError,"|{0}| >>> Not a valid value: {1} | type: {2} | value: {3}".format(_str_func,_d['combined'],_aType,value)
    
        
    
    
    
def validate_arg(*a):
    """
    Validate an attr arg to be more useful for the various methods of calling it

    :parameters:
        arg(varied): Object.attribute arg to check. Accepts 'obj.attr'/ obj,attr/ ['obj','attr'] formats.
    :returns
        data{dict} -- {'obj','attr','combined'}
    """
    _str_func = 'validate_arg'
    _len = len(a)
    log.debug("|{0}| >> a: {1}...".format(_str_func,a))

    if _len == 1:
        log.debug("|{0}| >> single arg...".format(_str_func)) 

        if issubclass(type(a[0]),dict):
            log.debug("|{0}| >> dict arg...".format(_str_func))             
            if a[0].get('combined'):
                log.debug("|{0}| >> passed validated arg, repassing...".format(_str_func))
                return a[0]
            raise ValueError,"This isn't a valid dict: {0}".format(a[0])

        elif type(a[0]) in [list,tuple] and len(a[0]) == 2:
            log.debug("|{0}| >> list arg...".format(_str_func))             
            _obj = a[0][0]
            _attr = a[0][1]
            _combined = "{0}.{1}".format(_obj,_attr)

        elif '.' in a[0]:
            log.debug("|{0}| >> string arg...".format(_str_func))             
            _obj = a[0].split('.')[0]
            _attr = '.'.join(a[0].split('.')[1:])
            _combined = a[0]        
        else:        
            raise ValueError,"Don't know what this is: {0}".format(a)
    else:
        log.debug("|{0}| >> multi arg...".format(_str_func))                
        _combined = "{0}.{1}".format(a[0],a[1])
        _obj = a[0]
        _attr = a[1]     
    #if not mc.objExists(_combined):  
        #raise ValueError,"{0} doesn't exist.".format(_combined)        
    return {'node':_obj,'obj':_obj ,'attr':_attr ,'combined':_combined}

def validate_attrTypeMatch(t1,t2):
    """
    Returns if attr types match
    
    :parameters:
        t1(string): attr type arg 1
        t2(string)
        
    :returns
        status(bool)
    """
    #_str_func = sys._getframe().f_code.co_name
    
    if t1 == t2:
            return True
    
    for o in _d_attrTypes.keys():
        if t1 in _d_attrTypes.get(o) and t2 in _d_attrTypes.get(o): 
            return True
    return False    

    
def get_alias(*a):
    """
    Gets the alias of an object attribute if there is one

    :parameters:
        arg(varied): Accepts 'obj.attr', ['obj','attr'] formats.
        attr(str): attribute to get the alias of

    :returns
        data{dict} -- {'obj','attr','combined'}
    """    
    _d = validate_arg(*a)
    if mc.aliasAttr(_d['combined'],q=True):
        return mc.aliasAttr(_d['combined'],q=True) 
    return None

def set_alias(node, attr = None, alias = None):
    """   
    :parameters:
        arg(varied): Accepts 'obj.attr', ['obj','attr'] formats.
        alias(str): Value to set as the alias. If none, the alias is cleared

    """        
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if alias is None and attr:
            alias = attr
    else:
        _d = validate_arg(node,attr) 
        
    alias = VALID.stringArg(alias)
    _alias_current = get_alias(_d)
    
    if alias:
        try:
            if alias != get_alias(_d['combined']):
                return mc.aliasAttr(alias, _d['combined'])
            else:log.debug("'{0}' already has that alias!".format(_d['combined']))
        except:
            log.warning("'{0}' failed to set alias of {1}!".format(_d['combined'],alias))

    else:
        if mc.aliasAttr(_d['combined'],q=True):           
            mc.aliasAttr(_d['combined'],remove=True)
            log.warning("'{0}' cleared of alias!".format(_d['combined']))

def compare_attrs(source, targets, **kws):
    """   
    Call for comparing a source object to targets to check values and attributes

    :parameters:
        source(string): Source object for a comparative base
        targets(list): objects to compare to
        kws(dict):pass through for mc.listAttr query

    :returns
        Report in the script editor

    """         
    _source = NAMES.get_short(source)
    _l_targets = VALID.objStringList(targets)

    log.info(cgmGen._str_hardLine)   

    for t in _l_targets:
        l_targetAttrs = mc.listAttr(t,**kws)
        if not l_targetAttrs:
            raise ValueError,"No attrs found. kws: {0}".format(kws)
        _t = NAMES.get_short(t)
        log.info("Comparing {0} to {1}...".format(_source,_t))
        _l_matching = []
        _l_notMatching = []
        for a in mc.listAttr(_source,**kws):
            try:
                #log.debug("Checking %s"%a)
                selfBuffer = get(_source,a)
                targetBuffer = get(t,a)
                if a in l_targetAttrs and selfBuffer != targetBuffer:
                    #bfr = ("{0} || {1} != {2}".format(a,selfBuffer,targetBuffer))
                    _l_notMatching.append([a,selfBuffer,targetBuffer])
                    continue
                _l_matching.append(a)
                    #print ("{0}.{1} != {2}.{1}".format(self.getShortName(),a,_t))
                    #log.debug("%s.%s : %s != %s.%s : %s"%(self.getShortName(),a,selfBuffer,target,a,targetBuffer))
            except Exception,error:
                log.warning(error)	
                log.warning("'%s.%s'couldn't query"%(_source,a))
        log.info("Matching attrs: {0} | Unmatching: {1}".format(len(_l_matching),len(_l_notMatching)))
        log.info(cgmGen._str_subLine)
        for b in _l_notMatching:
            log.info("attr: {0}...".format(b[0]))
            log.info("source: {0}".format(b[1]))
            log.info("target: {0}".format(b[2]))

        log.info("{0} >>".format(_t) + cgmGen._str_subLine)
    log.info(cgmGen._str_hardLine)

    return True    


def delete(*a):
    _str_func = 'delete'
    _d = validate_arg(*a) 
    _combined = _d['combined'] 
    try:
        if mc.objExists(_combined):
            if get_parent(_d):raise ValueError,"{0} is child attr, try deleting parent attr: {1}".format(_combined,get_parent(_d))
            try:
                mc.setAttr(_combined,lock=False)
            except:pass            
            try:
                break_connection(_combined)
            except:pass
            
            _out = get_driven(_d) or []
            for p in _out:
                log.warning("|{0}| >> [{1}] | breaking out plug: {2}".format(_str_func,_combined,p))     
                disconnect(_combined,p)
    
            mc.deleteAttr(_combined)  
            return True
        return False
    except Exception,err:
        pprint.pprint(vars())
        raise Exception,err
        
def get(*a, **kws):
    """   
    Replacement for getAttr which get's message objects as well as parses double3 type 
    attributes to a list  

    :parameters:
        *a(varied): - Uses validate_arg 
        **kws -- pass through for getAttr on certain types

    :returns
        value(s)
    """ 
    try:
        _str_func = 'get'
        _d = validate_arg(*a) 
        _combined = _d['combined']
        _obj = _d['obj']
        _attr = _d['attr']
        
        if kws:
            if not kws.get('sl') or not kws.get('silent'):
                kws['sl'] = True
    
        log.debug("|{0}| >> arg: {1}".format(_str_func,a))    
        if kws:log.debug("|{0}| >> kws: {1}".format(_str_func,kws))
    
        if "[" in _attr:
            log.debug("Indexed attr")
            return mc.listConnections(_combined)
    
        try:attrType = mc.getAttr(_d['combined'],type=True)
        except:
            log.debug("|{0}| >> {1} failed to return type. Exists: {2}".format(_str_func,_d['combined'],mc.objExists(_d['combined'])))            
            return None
        
        if attrType in ['TdataCompound']:
            return mc.listConnections(_combined)		
    
        if mc.attributeQuery (_attr,node=_obj,msg=True):
            #return mc.listConnections(_combined) or False 
            return get_message(_d)
        elif attrType == 'double3':
            return [mc.getAttr(_obj+'.'+ a) for a in mc.attributeQuery(_attr, node = _obj, listChildren = True)]
        #elif attrType == 'double':
            #parentAttr = mc.attributeQuery(_attr, node =_obj, listParent = True)
            #return mc.getAttr("{0}.{1}".format(_obj,parentAttr[0]), **kws)
        else:
            return mc.getAttr(_combined, **kws)
    except Exception,err:
        if has_attr(*a):
            cgmGen.cgmExceptCB(Exception,err)
        return False
def set_keyframe(node, attr = None, value = None, time = None):
    """   
    Replacement for simple setKeyframe call. Necessary because Maya's doesn't allow multi attrs like translate,scale,rotate...
    
    :parameters:
        node(str)
        attr(str)
        v-value(varied): -
        t-time(varied) - pass through for mc.setKeyframe

    :returns
        value(s)
    """ 
    _str_func = 'set_keyframe'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _node = _d['node']
    _attr = _d['attr']
    _children = get_children(_d)
    _kws = {'v':value,'t':time}
    
    if _children:
        if len(_children) == len(value):
            for i,c in enumerate(_children):
                try:mc.setKeyframe(_node,attribute=c,v=value[i], t=time)
                except Exception,err:
                    log.error("|{0}| >>  failed to set... f{1} : {2}.{3} --> {4} | {5}".format(_str_func,time,_node,_attr,value, err))
                          
        else:
            raise ValueError,"Children len to value len mismatch|| children: {0} | v: {1}".format(_children,value)
    else:
        try:mc.setKeyframe(_node,attribute=_attr,**_kws)
        except Exception,err:
            log.error("|{0}| >>  failed to set... f{1} : {2}.{3} --> {4} | {5}".format(_str_func,time,_node,_attr,value, err))
        

def set_standardFlags(node, attrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'],
                      lock=True,visible=False,keyable=False):
    """   
    Multi set keyable,lock, visible, hidden, etc...

    :parameters:
        node(str)
        attrs(str)
        lock(bool)
        visible(bool)
        keyable(bool)

    """ 
    _str_func = 'set_standardFlags'
    
    for a in attrs:
        try:
            _v = validate_arg(node,a)
            #mc.setAttr ((node+'.'+a),lock=lock, keyable=keyable, channelBox=visible)    
            set_lock(_v,lock)
            set_hidden(_v, not visible)
            set_keyable(_v,keyable)
            #if hidden is not None:
                #set_hidden(_v,hidden)
        except Exception, e:
            log.error("|{0}| >>  {1}.{2} failed...".format(_str_func,node,a))            
            for arg in e.args:
                log.warning(arg)

def set(node, attr = None, value = None, lock = False,**kws):
    """   
    Replacement for setAttr which get's message objects as well as parses double3 type 
    attributes to a list  

    :parameters:
        node(str)
        attr(str)
        value(varied): -
        forceLock -- lock after setting
        **kws -- pass through for getAttr on certain types

    :returns
        value(s)
    """ 
    _str_func = 'set'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if value == None and attr is not None:
            value = attr
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _obj = _d['node']
    _attr = _d['attr']
    _wasLocked = False

    log.debug("|{0}| >> attr: {1} | value: {2} | lock: {3}".format(_str_func,_combined,value, lock))    
    if kws:log.debug("|{0}| >> kws: {1}".format(_str_func,kws))  

    _aType =  mc.getAttr(_combined,type=True)
    _validType = validate_attrTypeName(_aType)
    
    
    if is_locked(_combined):
        _wasLocked = True
        mc.setAttr(_combined,lock=False)    

    #CONNECTED!!!
    if not is_keyed(_d):
        if break_connection(_d):
            log.debug("|{0}| >> broken connection: {1}".format(_str_func,_combined))    
            
    _current = get(_combined)
    if _current == value:
        log.debug("|{0}| >> Already has value: {1}".format(_str_func,_combined))
        if _wasLocked:set_lock(_d,True)
        return 
    
    _children = get_children(_d)
    if _children:
        if VALID.isListArg(value):
            if len(_children) != len(value):
                raise ValueError,"Must have matching len for value and children. Children: {0} | value: {1}".format(_children,value)
        else:
            value = [value for i in range(len(_children))]
        for i,c in enumerate(_children):
            mc.setAttr("{0}.{1}".format(_obj,c),value[i], **kws)
    elif _validType == 'long':
        mc.setAttr(_combined,int(float(value)), **kws)
    elif _validType == 'string':
        mc.setAttr(_combined,str(value),type = 'string', **kws)
    elif _validType == 'double':
        mc.setAttr(_combined,float(value), **kws)
    elif _validType == 'message':
        set_message(_obj, _attr, value)
    elif _validType == 'enum':
        _l = get_enum(_d).split(':')        
        if VALID.stringArg(value) and ':' in value:
            #if len(_l) != len(value.split(':')):
                #raise ValueError,"Must have matching len for editing. Current: {0} | requested: {1}".format(_l,value)
            mc.addAttr(_combined, edit=True, en = value, **kws)              
        else:
            _l = get_enum(_d).split(':')
            
            if value in _l:
                mc.setAttr(_combined, _l.index(value), **kws)
            elif value is not None and value <= len(_l):
                mc.setAttr(_combined, value, **kws)  
            else:
                mc.setAttr(_combined,value, **kws)
        
    else:
        mc.setAttr(_combined,value, **kws)

    if _wasLocked or lock:
        mc.setAttr(_combined,lock=True)    

    return

def set_lock(node, attr = None, arg = None):
    """   
    Set the lock status of an attribute

    :parameters:
        node(str)
        attr(str)
        arg(bool): -

    """ 
    _str_func = 'set_lock'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if arg is None and attr is not None:
            arg = attr
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _obj = _d['node']
    _attr = _d['attr']

    _children = get_children(_d)
    if _children:
        for i,c in enumerate(_children):
            mc.setAttr("{0}.{1}".format(_obj,c),lock = arg)    
    else:
        mc.setAttr(_combined,lock=arg) 
         
        
def set_keyable(node, attr = None, arg = None):
    """   
    Set the lock status of an attribute

    :parameters:
        node(str)
        attr(str)
        arg(bool): -

    """ 
    _str_func = 'set_keyable'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if arg is None and attr is not None:
            arg = attr        
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _obj = _d['node']
    _attr = _d['attr']
    
    _children = get_children(_d)
    if _children:
        for i,c in enumerate(_children):
            if not arg:_hidden = is_hidden(_obj,c)
            mc.setAttr("{0}.{1}".format(_obj,c),e=True,keyable = arg)
            if not arg and is_hidden(_obj,c) != _hidden:
                set_hidden(_obj,c,_hidden)
    else:
        if not arg:_hidden = is_hidden(_d)        
        mc.setAttr(_combined,e=True,keyable = arg)  
        if not arg and is_hidden(_d) != _hidden:
            set_hidden(_d,_hidden)      
            
def set_hidden(node, attr = None, arg = None):
    """   
    Set the hidden status of an attribute

    :parameters:
        node(str)
        attr(str)
        arg(bool): -

    """ 
    _str_func = 'set_hidden'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if arg is None and attr is not None:
            arg = attr        
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _node= _d['node']
    _attr = _d['attr']
    
    _children = get_children(_d) 
    
    if arg:
        if _children:
            for c in _children:
                _d_child = validate_arg(_node,c)
                if not is_hidden(_d_child):
                    if is_keyable(_d_child):
                        set_keyable(_d_child, arg = False)
                    mc.setAttr(_d_child['combined'],e=True,channelBox = False) 
    
        elif not is_hidden(_d):
            if is_keyable(_d):
                set_keyable(_d, arg = False)
            mc.setAttr(_combined,e=True,channelBox = False) 

    else:
        if _children:
            for c in _children:
                _d_child = validate_arg(_node,c)
                if is_hidden(_d_child):
                    mc.setAttr(_d_child['combined'],e=True,channelBox = True) 

        elif is_hidden(_d):
            mc.setAttr(_combined,e=True,channelBox = True)  
            
def set_default(node, attr = None, arg = None):
    """   
    Set the default value of an attribute

    :parameters:
        node(str)
        attr(str)
        arg(bool): -

    """ 
    _str_func = 'set_default'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if arg is None and attr is not None:
            arg = attr        
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _node = _d['node']
    _attr = _d['attr']
    _type = get_type(_d)
    
    _children = get_children(_d)
    if _children:
        for i,c in enumerate(_children):
            _str_c = "{0}.{1}".format(_node,c) 
            try:mc.addAttr(_str_c,e=True,defaultValue = arg)   
            except Exception,err:
                log.error("|{0}| >> {1} | arg: {2} || err: {3}".format(_str_func,_str_c,arg,err))
    elif _type == 'enum':
        _l = get_enum(_d).split(':')
        if arg in _l:
            mc.addAttr(_combined, e=True,defaultValue =_l.index(arg))
        elif arg is not None and arg <= len(_l):
            mc.addAttr(_combined, e=True,defaultValue =arg)  
        else:
            raise ValueError,"Shouldn't be here"
    else:
        try:mc.addAttr(_combined,e=True,defaultValue = arg)  
        except Exception,err:
            log.error("|{0}| >> {1} | arg: {2} || err: {3}".format(_str_func,_combined,arg,err))
            
def set_max(node, attr = None, arg = None):
    """   
    Set the max value of an attribute

    :parameters:
        node(str)
        attr(str)
        arg(bool): -

    """ 
    _str_func = 'set_max'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if arg is None and attr is not None:
            arg = attr        
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _node = _d['node']
    _attr = _d['attr']

    _children = get_children(_d)
    if _children:
        for i,c in enumerate(_children):
            _str_c = "{0}.{1}".format(_node,c) 
            try:
                if arg not in [False,None]:
                    mc.addAttr(_str_c,e=True,maxValue = arg) 
                else:
                    mc.addAttr(_str_c,e=True,hasMaxValue = False) 
            except Exception,err:
                log.error("|{0}| >> {1} | arg: {2} || err: {3}".format(_str_func,_str_c,arg,err))
    else:
        try:
            if arg not in [False,None]:
                mc.addAttr(_combined,e=True,maxValue = arg)  
            else:
                mc.addAttr(_combined,e=True,hasMaxValue = False)                  
        except Exception,err:
            log.error("|{0}| >> {1} | arg: {2} || err: {3}".format(_str_func,_combined,arg,err))
            
def set_softMax(node, attr = None, arg = None):
    """   
    Set the max value of an attribute

    :parameters:
        node(str)
        attr(str)
        arg(bool): -

    """ 
    _str_func = 'set_softMax'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if arg is None and attr is not None:
            arg = attr        
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _node = _d['node']
    _attr = _d['attr']

    if get_children(_d):
        return False
    else:
        try:
            if arg not in [False,None]:
                mc.addAttr(_combined,e=True,softMaxValue = arg)  
            else:
                mc.addAttr(_combined,e=True,hasSoftMaxValue = False)                  
        except Exception,err:
            log.error("|{0}| >> {1} | arg: {2} || err: {3}".format(_str_func,_combined,arg,err))
    return arg
            
def set_min(node, attr = None, arg = None):
    """   
    Set the min value of an attribute

    :parameters:
        node(str)
        attr(str)
        arg(bool): -

    """ 
    _str_func = 'set_min'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if arg is None and attr is not None:
            arg = attr        
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _node = _d['node']
    _attr = _d['attr']

    _children = get_children(_d)
    if _children:
        for i,c in enumerate(_children):
            _str_c = "{0}.{1}".format(_node,c) 
            try:
                if arg not in [False,None]:
                    mc.addAttr(_str_c,e=True,minValue = arg) 
                else:
                    mc.addAttr(_str_c,e=True,hasMinValue = False) 
            except Exception,err:
                log.error("|{0}| >> {1} | arg: {2} || err: {3}".format(_str_func,_str_c,arg,err))
    else:
        try:
            if arg not in [False,None]:
                mc.addAttr(_combined,e=True,minValue = arg)  
            else:
                mc.addAttr(_combined,e=True,hasMinValue = False)                  
        except Exception,err:
            log.error("|{0}| >> {1} | arg: {2} || err: {3}".format(_str_func,_combined,arg,err))
            
def set_softMin(node, attr = None, arg = None):
    """   
    Set the softMin value of an attribute

    :parameters:
        node(str)
        attr(str)
        arg(bool): -

    """ 
    _str_func = 'set_softMin'
    
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        if arg is None and attr is not None:
            arg = attr        
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _node = _d['node']
    _attr = _d['attr']

    if get_children(_d):
        return False
    else:
        try:
            if arg not in [False,None]:
                mc.addAttr(_combined,e=True,softMinValue = arg)  
            else:
                mc.addAttr(_combined,e=True,hasSoftMinValue = False)                  
        except Exception,err:
            log.error("|{0}| >> {1} | arg: {2} || err: {3}".format(_str_func,_combined,arg,err))
    return arg

def validate_attrTypeName(attrType):
    """"   
    Validates an attr type from various returns to something more consistant

    :parameters:
        attrType(string): - U

    :returns
        validatedType(string)
    """         
    _str_func = 'validate_attrTypeName'    
    for option in _d_attrTypes.keys():
        if attrType == option:return option
        if attrType in _d_attrTypes.get(option): 
            return option
    #log.debug("|{0}| >> Invalid type: {1}".format(_str_func,attrType))
    return False
    #raise ValueError,"Invalid type: {0}".format(attrType)

def is_keyed(*a):
    """   
    Returns if an attribute is keyed

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_keyed'
    _d = validate_arg(*a) 

    if mc.keyframe(_d['combined'], query=True):return True
    return False

def get_keyed(node):
    """   
    Returns if list of keyed attributes

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        attributes(list)
    """ 
    _str_func = 'get_keyed'
    _res = []
    for a in mc.listAttr(node,keyable=True):
        if is_keyed(node,a):
            _res.append(a)
            
    return _res

def is_hidden(*a):
    """   
    hidden query

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'is_hidden'
    _d = validate_arg(*a) 
    
    hidden = not mc.getAttr(_d['combined'],channelBox=True)
    if is_keyable(_d):
        hidden = mc.attributeQuery(_d['attr'], node = _d['node'], hidden=True)	
    return hidden    
    
    
    """
    _get = mc.getAttr(_d['combined'],channelBox=True)
    _query = mc.attributeQuery(_d['attr'], node = _d['node'],channelBox=True)

    if not _query and _get:
        return False
    return True"""
    #return not mc.attributeQuery(_d['attr'], node = _d['node'],channelBox=True)

def get_enum(*a):
    """   
    Get enum

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'get_enum'
    _d = validate_arg(*a) 
    
    if get_type(_d) == 'enum':
        #return mc.addAttr(_d['combined'],q=True, en = True) 
        return mc.attributeQuery(_d['attr'], node = _d['node'], listEnum=True)[0]
    return False

def get_enumValueString(*a):
    """   
    Get enum

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'get_enumValueString'
    _d = validate_arg(*a) 
    
    if get_type(_d) == 'enum':
        enums=get_enum(_d).split(':')
        return enums[get(_d)]

    return False

def get_enumList(*a):
    _res = get_enum(*a)
    if _res:
        return _res.split(':')
    return False    
    
def is_keyable(*a):
    """   
    Keyable query

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'is_keyable'
    _d = validate_arg(*a) 

    try:
        return mc.getAttr(_d['combined'],keyable=True) 
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False
    
def is_locked(*a):
    """   
    Lock query

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'is_locked'
    _d = validate_arg(*a) 

    try:
        return mc.getAttr(_d['combined'],lock=True) 
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False
    
def is_multi(*a):
    """   
    multi query

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'is_multi'
    _d = validate_arg(*a) 

    try:
        if not is_dynamic(_d):
            return False
        return mc.addAttr(_d['combined'],q=True,m=True)
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False
    
def is_connected(*a):
    """   
    Returns if an attribute is keyed

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_connected'
    _d = validate_arg(*a) 

    if mc.connectionInfo(_d['combined'], isDestination=True):return True
    return False

def get_familyDict(*a):
    """   
    Get family dict of an attribute

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        family(dict)
    """     
    _str_func = 'get_familyDict'
    _d = validate_arg(*a)
    _combined = _d['combined']
    _obj = _d['obj']
    _attr = _d['attr']

    returnDict = {}
    buffer = mc.attributeQuery(_attr, node = _obj, listParent=True)
    if buffer is not None:
        returnDict['parent'] = buffer[0]
    buffer= mc.attributeQuery(_attr, node = _obj, listChildren=True)
    if buffer is not None:
        returnDict['children'] = buffer
    buffer= mc.attributeQuery(_attr, node = _obj, listSiblings=True)
    if buffer is not None:
        returnDict['siblings'] = buffer

    if returnDict:
        return returnDict
    return False
    
def break_connection(*a):
    """   
    Breaks connections on an attribute. Handles locks on source or end

    :parameters:
        *a -- validate_arg

    :returns
        broken connection or status
    """ 
    try:
        _str_func = 'break_connection'
        _d = validate_arg(*a) 
        _combined = _d['combined']
        _obj = _d['obj']
        _attr = _d['attr']
    
        _drivenAttr = _combined
    
        family = {}
        source = []
    
        if get_type(_d) == 'message':
            log.debug("|{0}| >> message...".format(_str_func))                        
            _dest = mc.listConnections (_combined, scn = False, d = True, s = False, plugs = True)
            if _dest:
                for c in _dest:
                    log.debug("|{0}| >> c: {1}".format(_str_func,c))                
                    disconnect(_drivenAttr,c)
    
        if (mc.connectionInfo(_combined,isDestination=True)):             
            sourceBuffer = mc.listConnections (_combined, scn = False, d = False, s = True, plugs = True)
            if not sourceBuffer:
                family = get_familyDict(_d)           
                sourceBuffer = mc.connectionInfo (_combined,sourceFromDestination=True)
            else:
                sourceBuffer = sourceBuffer[0]
    
            if not sourceBuffer:
                return log.warning("|{0}| >>No source for '{1}.{2}' found!".format(_str_func,_obj,attr))
            log.debug("|{0}| >> sourcebuffer: {1}".format(_str_func,sourceBuffer))
            if family and family.get('parent'):
                log.debug("|{0}| >> family: {1}".format(_str_func,family))
                _drivenAttr = '{0}.{1}'.format(_obj,family.get('parent'))
    
            log.debug("|{0}| >> breaking: {1} >>> to >>> {2}".format(_str_func,sourceBuffer,_drivenAttr))
    
            disconnect(sourceBuffer,_drivenAttr)
    
            return sourceBuffer
        
    
    
        return False
    except Exception,err:
        cgmGen.cgmExceptCB(Exception,err,msg=vars())
def disconnect(fromAttr,toAttr):
    """   
    Disconnects attributes. Handles locks on source or end

    :parameters:
        fromAttr(string) - 'obj.attribute'
        toAttr() - depends on the attribute type
        
    :returns
        status(bool)
    """     
    _str_func = 'connect'
    _d = validate_arg(fromAttr) 
    _combined = _d['combined']
    _obj = _d['obj']
    _attr = _d['attr']
    
    _d_to = validate_arg(toAttr)
    _toAttr = _d_to['attr']
    _combined_to = _d_to['combined']    
    

    drivenLock = False
    if mc.getAttr(_combined_to,lock=True):
        drivenLock = True
        mc.setAttr(_combined_to,lock=False)
    sourceLock = False    
    if mc.getAttr(_combined,lock=True):
        sourceLock = True
        mc.setAttr(_combined,lock=False)

    mc.disconnectAttr (_combined,_combined_to)


    if drivenLock:
        mc.setAttr(_combined_to,lock=True)

    if sourceLock:
        mc.setAttr(_combined,lock=True)
        
    return True

def connect(fromAttr,toAttr,transferConnection=False,lock = False, **kws):
    """   
    Connects attributes. Handles locks on source or end

    :parameters:
        attribute(string) - 'obj.attribute'
        value() - depends on the attribute type
        transferConnection(bool) - (False) - whether you wante to transfer the existing connection to or not
        useful for buffer connections
        lock(bool) = False(default)


    :returns
        broken connection or status
    """ 
    _str_func = 'connect'
    _d = validate_arg(fromAttr) 
    _combined = _d['combined']
    _obj = _d['obj']
    _attr = _d['attr']
    
    _d_to = validate_arg(toAttr)
    _toAttr = _d_to['attr']
    _combined_to = _d_to['combined']
    
    log.debug("|{0}| >> Connecting {1} to {2}".format(_str_func,_combined,_combined_to))

    assert _combined != _combined_to,"Cannot connect an attr to itself. The world might blow up!"

    if transferConnection: raise Exception,"Look at why you're transferring connection"

    _wasLocked = False
    _connection = False
    if (mc.objExists(_combined_to)):
        if mc.getAttr(_combined_to,lock=True):
            _wasLocked = True
            mc.setAttr(_combined_to,lock=False)

        #bufferConnection = get_driver(toAttr)
        _connection = break_connection(_d_to)
        #doBreakConnection(attrBuffer[0],attrBuffer[1])
        mc.connectAttr(_combined,_combined_to,**kws)     

    if transferConnection:
        if _connection and not is_connected(_d):
            log.debug("|{0}| >> {1} | Transferring to fromAttr: {2} | connnection: {3}".format(_str_func,toAttr,fromAttr,_connection))            
            mc.connectAttr(_connection,_combined)

    if _wasLocked or lock:
        mc.setAttr(_combined_to,lock=True)  
        
    return True


def add(obj,attr=None,attrType=None, enumOptions = ['off','on'],value=None, lock = None,*a, **kws):
    """   
    Breaks connections on an attribute. Handles locks on source or end

    :parameters:
        obj(string) -- must exist in scene
        attr(string) -- attribute name
        attrType(string) -- must be valid type. Type 'print attrTypesDict' for search dict 
        enumOptions(list) -- string list of options for enum attr types

    :returns
        combined name
    """ 
    try:
        _str_func = 'add'
        
        if '.' in obj or issubclass(type(obj),dict):
            _d = validate_arg(obj)
            attrType = attr
        else:
            _d = validate_arg(obj,attr)     
        
        _combined = _d['combined']
        _node = _d['node']
        _attr = _d['attr']
        if mc.objExists(_combined):
            raise ValueError,"{0} already exists.".format(_combined)
    
        _type = validate_attrTypeName(attrType)

        
        assert _type is not False,"'{0}' is not a valid attribute type for creation.".format(attrType)
    
        if _type == 'string':
            mc.addAttr (_node, ln = _attr, dt = 'string',*a, **kws)
        elif _type == 'double':
            mc.addAttr (_node, ln = _attr, at = 'float',*a, **kws)
        elif _type == 'long':
            mc.addAttr (_node, ln = _attr, at = 'long',*a, **kws)
        elif _type == 'double3':
            mc.addAttr (_node, ln=_attr, at= 'double3',*a, **kws)
            mc.addAttr (_node, ln=(_attr+'X'),p=_attr , at= 'double',*a, **kws)
            mc.addAttr (_node, ln=(_attr+'Y'),p=_attr , at= 'double',*a, **kws)
            mc.addAttr (_node, ln=(_attr+'Z'),p=_attr , at= 'double',*a, **kws)        
        elif _type == 'enum':
            if type(enumOptions) in [list,tuple]:
                enumOptions = '%s' %(':'.join(enumOptions))
            mc.addAttr (_node,ln = _attr, at = 'enum', en=enumOptions,*a, **kws)
            mc.setAttr ((_node+'.'+_attr),e=True,keyable=True)
        elif _type == 'bool':
            mc.addAttr (_node, ln = _attr,  at = 'bool',*a, **kws)
            mc.setAttr ((_node+'.'+_attr), edit = True, channelBox = True)
        elif _type == 'message':
            mc.addAttr (_node, ln = _attr, at = 'message',*a, **kws )
        elif _type == 'float3':
            mc.addAttr (_node, ln=_attr, at= 'float3',*a, **kws)
            mc.addAttr (_node, ln=(_attr+'X'),p=_attr , at= 'float',*a, **kws)
            mc.addAttr (_node, ln=(_attr+'Y'),p=_attr , at= 'float',*a, **kws)
            mc.addAttr (_node, ln=(_attr+'Z'),p=_attr , at= 'float',*a, **kws)        
        else:
            raise ValueError,"Don't know what to do with attrType: {0}".format(attrType)
            #return False
            
        if value is not None:
            set(_node,_attr,value=value)
        if lock:
            set_lock(_node,_attr,lock)
        return _combined        
    except Exception,err:cgmGen.cgmExceptCB(Exception,err)
def get_standardFlagsDict(*a):
    """   
    Returns a diciontary of locked,keyable,locked states of an attribute. If
    the attribute is numeric, it grabs the typical flags for that.

    :parameters:
        *a -- validate_arg

    :returns
        dict
    """ 
    _str_func = 'get_standardFlagsDict'
    _d = validate_arg(*a) 
    _combined = _d['combined']
    _obj = _d['obj']
    _attr = _d['attr']

    objAttrs = mc.listAttr(_obj, userDefined = True) or []
    dataDict = {'type':mc.getAttr(_combined,type=True),
                'locked':mc.getAttr(_combined ,lock=True),
                'keyable':mc.getAttr(_combined ,keyable=True)}

    dynamic = False
    if _attr in objAttrs:
        dynamic = True
    dataDict['dynamic'] = dynamic

    hidden = not mc.getAttr(_combined,channelBox=True)

    if dataDict.get('keyable'):
        hidden = mc.attributeQuery(_attr, node = _obj, hidden=True)
    dataDict['hidden'] = hidden

    enumData = False
    if dataDict.get('type') == 'enum' and dynamic == True:
        dataDict['enum'] = mc.addAttr(_combined,q=True, en = True)

    numeric = True
    if dataDict.get('type') in ['string','message','enum','bool']:
        numeric = False
    dataDict['numeric'] = numeric
    
    if numeric:
        _d_numeric = get_numericFlagsDict(_d)
        dataDict.update(_d_numeric)

    if dynamic:
        dataDict['readable']=mc.addAttr(_combined,q=True,r=True)
        dataDict['writable']=mc.addAttr(_combined,q=True,w=True)
        dataDict['storable']=mc.addAttr(_combined,q=True,s=True)
        dataDict['usedAsColor']=mc.addAttr(_combined,q=True,usedAsColor = True)     

    return dataDict 

def has_attr(*a):
    """   
    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(has_attr)
    """ 
    _str_func = 'has_attr'
    _d = validate_arg(*a) 

    #try:
    return mc.attributeQuery(_d['attr'],node=_d['node'],exists=True)
    #except Exception,err:
    #    log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
    #    return False
    #return False


def get_default(*a):
    """   
    Get default value

    :parameters:
        *a -- validate_arg

    :returns
        dict
    """ 
    _str_func = 'get_default'
    _d = validate_arg(*a) 
    _combined = _d['combined']
    _node = _d['node']
    _attr = _d['attr']
    
    #if not is_dynamic(_d):
    #    return False
    
    if not is_dynamic(_d):
        _long = get_nameLong(_d)
        if _long in ['translateX','translateY','translateZ','translate',
                     'rotateX','rotateY','rotateZ','rotate',
                     'scaleX','scaleY','scaleZ','scale']:
            if 'scale' in _long:
                if _long == 'scale':
                    return [1.0,1.0,1.0]
                return 1.0
            else:
                if _long in ['rotate','translate']:
                    return [0.0,0.0,0.0]
                return 0.0
        return False
    if type(mc.addAttr(_combined,q=True,defaultValue = True)) is int or float:
        _res = mc.attributeQuery(_attr, node = _node, listDefault=True)
        if _res is not False:
            if len(_res) == 1:
                return _res[0]
            return _res    
    return False

def get_max(*a):
    """   
    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        value(float) or False
    """ 
    _str_func = 'get_max'
    _d = validate_arg(*a) 

    try:
        if mc.attributeQuery(_d['attr'], node = _d['node'], maxExists=True):
            _res =  mc.attributeQuery(_d['attr'], node = _d['node'], maximum=True)
            if _res is not False:
                if len(_res) == 1:
                    return _res[0]
                return _res       
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False
    return False

def get_min(*a):
    """   
    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        value(float) or False
    """ 
    _str_func = 'get_min'
    _d = validate_arg(*a) 

    try:
        if mc.attributeQuery(_d['attr'], node = _d['node'], minExists=True):
            _res =  mc.attributeQuery(_d['attr'], node = _d['node'], minimum=True)
            if _res is not False:
                if len(_res) == 1:
                    return _res[0]
                return _res           
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False
    return False

def get_softMin(*a):
    """   
    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        value(float) or False
    """ 
    _str_func = 'get_softMin'
    _d = validate_arg(*a) 

    try:
        _res =  mc.attributeQuery(_d['attr'], node = _d['node'], softMin=True)
        if _res is not False:
            if len(_res) == 1:
                return _res[0]
            return _res     
    except Exception,err:
        log.debug("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False
    return False

def get_softMax(*a):
    """   
    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        value(float) or False
    """ 
    _str_func = 'get_softMax'
    _d = validate_arg(*a) 

    try:
        _res =  mc.attributeQuery(_d['attr'], node = _d['node'], softMax=True)
        if _res is not False:
            if len(_res) == 1:
                return _res[0]
            return _res       
    except Exception,err:
        log.debug("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False
    return False

def get_numericFlagsDict(*a):
    """   
    Returns a diciontary of max,min,ranges,softs and default settings of an attribute

    :parameters:
        *a -- validate_arg

    :returns
        dict
            default
            min
            max
            softMin
            softMax
            range
            softRange
    """ 
    _str_func = 'get_numericFlagsDict'
    _d = validate_arg(*a) 
    _combined = _d['combined']
    _obj = _d['obj']
    _attr = _d['attr']



    numeric = is_numeric(_d)


    dataDict = {}    
    # Return numeric data    
    if not numeric or get_children(_d):
        return {}
    else:
        try:
            dataDict['min'] = get_min(_d)
        except:
            dataDict['min'] = False
            log.debug("'%s.%s' failed to query min value" %(_obj,_attr))

        try:
            dataDict['max']  = get_max(_d)                  
        except:
            dataDict['max']  = False
            log.debug("'%s.%s' failed to query max value" %(_obj,_attr))

        try:
            dataDict['default'] = get_default(_d) 
        except:
            dataDict['default'] = False
            log.debug("'%s.%s' failed to query default value" %(_obj,_attr))        
        """if type(mc.addAttr(_combined,q=True,defaultValue = True)) is int or float:
            try:
                defaultValue = mc.attributeQuery(_attr, node = _obj, listDefault=True)
                if defaultValue is not False:
                    dataDict['default'] = defaultValue[0]  
            except:
                dataDict['default'] = False
                log.debug("'%s.%s' failed to query default value" %(_obj,_attr))"""

        #>>> Soft values
        try:
            dataDict['softMax'] = get_softMax(_d)                  
        except:
            dataDict['softMax']  = False

        try:
            dataDict['softMin']  =  get_softMin(_d)                  
        except:
            dataDict['softMin']  = False

        #>>> Range
        try:
            dataDict['range'] =  mc.attributeQuery(_attr, node = _obj, range=True)
        except:
            dataDict['range'] = False

        try:
            dataDict['softRange'] =  mc.attributeQuery(_attr, node = _obj, softRange=True)
        except:
            dataDict['softRange'] = False 

    return dataDict     

def get_nameNice(*a):
    """   
    Get the nice name of an attribute

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'get_nameNice'
    _d = validate_arg(*a) 

    return mc.attributeQuery(_d['attr'], node = _d['obj'], niceName = True) or False

def renameNice(node=None, attr=None, name=None):
    """   
    Set the long name of an attribute

    :parameters:
        node(string)
        attr(string)
        name(string) -- new name. If None, assumes obj arg is combined and uses attr. If False, clears the nice name

    :returns
        status(bool)
    """ 
    _str_func = 'rename'
    if name is None:
        name = attr
        attr = None
        _d = validate_arg(node) 
    else:
        _d = validate_arg(node,attr) 

    _lock = is_locked(_d)
    if _lock:
        set_lock(_d,False)
        
    _longName = get_nameLong(_d)
    #try:
    if name:
        mc.addAttr(_d['combined'],edit = True, niceName = name)
    elif name == False:
        mc.addAttr(_d['combined'],edit = True, niceName = _d['attr'])
    if _lock:set_lock(_d,True)
    return get_nameNice(_d)    

def get_nameLong(*a):
    """   
    Get the long name of an attribute

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'get_nameLong'
    _d = validate_arg(*a) 
    try:
        return mc.attributeQuery(_d['attr'], node = _d['obj'], longName = True) or False
    except:
        if mc.objExists(_d['combined']):
            return _d['attr']
        else:
            raise RuntimeError,"Attr does not exist: {0}".format(_d['combined'])

def rename(obj=None, attr=None, name=None):
    """   
    Set the long name of an attribute

    :parameters:
        obj(string)
        attr(string)
        name(string) -- new name. If None, assumes obj arg is combined and uses attr

    :returns
        status(bool)
    """ 
    _str_func = 'rename'
    _res = None
    
    if name is None:
        name = attr
        attr = None
        _d = validate_arg(obj) 
    else:
        _d = validate_arg(obj,attr) 
    
    _lock = is_locked(_d)
    if _lock:
        set_lock(_d,False)
    
    _longName = get_nameLong(_d)
    #try:
    if name:
        if name != _longName:
            mc.renameAttr("{0}.{1}".format(_d['obj'],_longName),name)
            #attributes.doRenameAttr(_d['obj'],_longName,name)
            _res = True
        else:
            log.debug("|{0}| >> nice name is already: {1} | combined:{2}".format(_str_func,name,_d['combined']))
            _res = False
    
    if _lock:set_lock(obj,name,True)
    if _res is not None:
        return _res
    raise ValueError,"No new attr name provided"

def is_dynamic(*a):
    """   
    Returns if an attribute is dynamic

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_dynamic'
    _d = validate_arg(*a) 
    _ud = mc.listAttr(_d['obj'], userDefined = True) or []
    if _d['attr'] in _ud:
        return True
    return False

def is_numeric(*a):
    """   
    Returns if an attribute is numeric

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_numeric'
    _d = validate_arg(*a) 
    if mc.getAttr(_d['combined'],type=True) in ['string','message','enum','bool']:
        return False
    return True

def is_readable(*a):
    """   
    Returns if an attribute is readable

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_readable'
    _d = validate_arg(*a) 
    if not is_dynamic(_d):
        return False
    return mc.addAttr(_d['combined'],q=True,r=True) or False

def is_writable(*a):
    """   
    Returns if an attribute is writable

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_writable'
    _d = validate_arg(*a) 
    if not is_dynamic(_d):
        return False
    return mc.addAttr(_d['combined'],q=True,w=True) or False

def is_storable(*a):
    """   
    Returns if an attribute is storable

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_storable'
    _d = validate_arg(*a) 
    if not is_dynamic(_d):
        return False
    return mc.addAttr(_d['combined'],q=True,s=True) or False

def is_usedAsColor(*a):
    """   
    Returns if an attribute is usedAsColor

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_usedAsColor'
    _d = validate_arg(*a) 
    if not is_dynamic(_d):
        return False
    return mc.addAttr(_d['combined'],q=True,usedAsColor=True) or False

def is_userDefined(*a):
    """   
    Returns if an attribute is userDefined

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'is_userDefined'
    _d = validate_arg(*a) 

    if get_nameLong(_d) in mc.listAttr(_d['node'],userDefined=True):
        return True
    return False

def get_range(*a):
    """   
    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        range(bool)
    """ 
    _str_func = 'get_range'
    _d = validate_arg(*a) 

    try:return mc.attributeQuery(_d['attr'], node = _d['node'], range=True) or False 
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False

def get_softRange(*a):
    """   
    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        range(bool)
    """ 
    _str_func = 'get_softRange'
    _d = validate_arg(*a) 

    try:return mc.attributeQuery(_d['attr'], node = _d['node'], softRange=True) or False 
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False

def get_children(*a):
    """   
    Get children of an attribute

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        children(list)
    """ 
    _str_func = 'get_children'
    _d = validate_arg(*a) 

    try:return mc.attributeQuery(_d['attr'], node = _d['node'], listChildren=True) or [] 
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False

def get_parent(*a):
    """   
    Get parent of an attribute

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        children(list)
    """ 
    _str_func = 'get_parent'
    _d = validate_arg(*a) 

    try:
        _buffer = mc.attributeQuery(_d['attr'], node = _d['node'], listParent=True) or [] 
        if _buffer:return _buffer[0]
        return _buffer
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False   

def get_siblings(*a):
    """   
    Get siblings of an attribute

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        siblings(list)
    """ 
    _str_func = 'get_siblings'
    _d = validate_arg(*a) 

    try:
        return mc.attributeQuery(_d['attr'], node = _d['node'], listSiblings=True) or [] 
    except Exception,err:
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False  
    
def get_type(*a):
    """   
    Get attr type

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'get_type'
    _d = validate_arg(*a) 

    try:
        return mc.getAttr(_d['combined'],type=True) 
    except Exception,err:
        log.debug("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
        return False  
    
def get_driver(node, attr = None, getNode = False, skipConversionNodes = False, longNames = True):
    """   
    Get the driver of an attribute if it is there

    :parameters:
        node(str) -- 
        attr(str)
        getNode(bool) -- if you want the dag node or the attribute(s)
        skipConversionNodes(bool) -- whether you want conversion nodes included in query
        longNames(bool) -- how you want the data returned name wise

    :returns
        driver(string)
    """
    _str_func = 'get_driver'    
    if attr is None:
        _d = validate_arg(node)
    else:
        _d = validate_arg(node,attr)     

    _combined = _d['combined']
    
    if not is_connected(_d):
        return False
    
    if getNode:
        objectBuffer =  mc.listConnections (_combined, scn = skipConversionNodes, d = False, s = True, plugs = False)
        if not objectBuffer:
            _p = get_parent(_d)
            if _p:
                log.debug("|{0}| >> parent check: {1}".format(_str_func,_p))
                return get_driver(_d['node'],_p,getNode,skipConversionNodes,longNames)
            return False
        if longNames:	
            return NAMES.get_long(objectBuffer[0])
        else:
            return NAMES.get_short(objectBuffer[0])      
    else:
        if (mc.connectionInfo (_combined,isDestination=True)) == True:
            sourceBuffer = mc.listConnections (_combined, scn = skipConversionNodes, d = False, s = True, plugs = True)
            if not sourceBuffer:
                sourceBuffer = [mc.connectionInfo (_combined,sourceFromDestination=True)]   
            if sourceBuffer:
                if skipConversionNodes and VALID.get_mayaType(sourceBuffer) == 'unitConversion':
                    _p = get_parent(_d)
                    if _p:
                        log.debug("|{0}| >> parent check: {1}".format(_str_func,_p))
                        return get_driver(_d['node'],_p,getNode,skipConversionNodes,longNames)                    
                    
                if longNames:		    
                    return NAMES.get_long(sourceBuffer[0])
                else:
                    return NAMES.get_short(sourceBuffer[0])
            return False
    return False    

def get_driven(node, attr = None, getNode = False, skipConversionNodes = False, longNames = True):
    """   
    Get attributes driven by an attribute

    :parameters:
        node(str) -- 
        attr(str)
        getNode(bool) -- if you want the dag node or the attribute(s)
        skipConversionNodes(bool) -- whether you want conversion nodes included in query
        longNames(bool) -- how you want the data returned name wise

    :returns
        driver(string)
    """
    _str_func = 'get_driven'    
    if attr is None:
        _d = validate_arg(node)
    else:
        _d = validate_arg(node,attr)     

    _combined = _d['combined']
    
    if getNode:
        objectBuffer =  mc.listConnections (_combined, scn = skipConversionNodes, d = True, s = False, plugs = False)
        if not objectBuffer:
            return False
        if longNames:	
            return [NAMES.get_long(o) for o in objectBuffer]
        else:
            return [NAMES.get_short(o) for o in objectBuffer]     
    else:
        if (mc.connectionInfo (_combined,isSource=True)) == True:
            destinationBuffer = mc.listConnections (_combined, scn = skipConversionNodes, d = True, s = False, plugs = True)
            if not destinationBuffer:
                destinationBuffer = mc.connectionInfo (_combined,destinationFromSource=True) 
            if destinationBuffer:
                _l = []
                for lnk in destinationBuffer:
                    if longNames:		    
                        _l.append( NAMES.get_long(lnk) )
                    else:
                        _l.append( NAMES.get_short(lnk) )
                return _l
            return False
    return False 

def get_messageLong(*a,**kws):
    _res = get_message(*a,**kws)
    if _res:
        return [NAMES.get_long(o) for o in _res]
    return _res

def get_message(messageHolder, messageAttr = None, dataAttr = None, dataKey = None, simple = False):
    """   
    This is a speciality cgm setup using both message attributes and a cgmMessageData attriubute for storing extra data via json
    Get attributes driven by an attribute.

    :parameters:
        messageHolder(str) -- object to store to
        messageAttr(str) -- 
        dataAttr(str) -- Specify the attribute to check for extra data or use default(NONE)
            cgmMsgData is our default. Data is stored as a json dict of {attr:{msg:component or attr}}
        dataKey(str/int) -- data key for extra data. If None provided, attr name is used.
        simple -- ignore extra data

    :returns
        data(list)
    """  
    _str_func = 'get_message'    
    _dataAttr = dataAttr
    if '.' in messageHolder or issubclass(type(messageHolder),dict):
        _d = validate_arg(messageHolder)
        _dataAttr = messageAttr
    else:
        _d = validate_arg(messageHolder,messageAttr)     
    _combined = _d['combined']       
            
    if dataKey is None:
        dataKey = messageAttr
    else:
        dataKey = unicode(dataKey)
        
    log.debug("|{0}| >> {1} | dataAttr: {2} | dataKey: {3}".format(_str_func,_combined,_dataAttr,dataKey))
    
    if not mc.objExists(_combined):
        log.debug("|{0}| >> {1} | No attribute exists".format(_str_func,_combined))        
        return False
    _type = get_type(_d)
    if _type in ['string']:
        log.debug("|{0}| >> special message attr...".format(_str_func))
        _msgBuffer = mc.listConnections(_combined,p=True)
        if _msgBuffer and len(_msgBuffer) == 1:
            _msgBuffer = [_msgBuffer[0].split('.')[0]]
        else:
            return False
            raise ValueError,"not sure what to do with this: {0}".format(_msgBuffer)
    else:
        _msgBuffer = mc.listConnections(_combined,destination=True,source=True,shapes=True)
        
        if _msgBuffer and mc.objectType(_msgBuffer[0])=='reference':
            #REPAIR
            _msgBuffer = mc.listConnections(_combined,destination=True,source=True)
        
    if is_multi(_d):
        log.debug("|{0}| >> multimessage...".format(_str_func))
        
        if _msgBuffer:
            return _msgBuffer
        return False
    else:
        log.debug("|{0}| >> single message...".format(_str_func))  
        
        if simple:
            return _msgBuffer
        
        _dataAttr = 'cgmMsgData'
        if dataAttr:
            _dataAttr = dataAttr
    
        if '.' in _dataAttr or issubclass(type(_dataAttr),dict):
            _d_dataAttr = validate_arg(_dataAttr)            
        else:
            _d_dataAttr = validate_arg(messageHolder,_dataAttr)           
        
        #_messagedNode = mc.listConnections (_combined,destination=True,source=True)
        if _msgBuffer != None:
            if mc.objExists(_msgBuffer[0]) and not mc.objectType(_msgBuffer[0])=='reference':
                
                mi_node = r9Meta.MetaClass(_d['node'])
                if mi_node.hasAttr(_d_dataAttr['attr']):
                    _dBuffer = mi_node.__getattribute__(_d_dataAttr['attr']) or {}
                    if _dBuffer.get(dataKey):
                        log.debug("|{0}| >> extra message data found...".format(_str_func))  
                        return [ _msgBuffer[0] + '.' + _dBuffer.get(dataKey)]
                
                return _msgBuffer
            else:#Try to repair it
                return repairMessageToReferencedTarget(storageObject,messageAttr)
    return False    
    
def set_message(messageHolder, messageAttr, message, dataAttr = None, dataKey = None, simple = False, connectBack = None):
    """   
    This is a speciality cgm setup using both message attributes and a cgmMessageData attriubute for storing extra data via json
    Get attributes driven by an attribute

    :parameters:
        messageHolder(str) -- object to store to
        messageAttr(str) -- 
        message(str) -- may be object, attribute, shape, or component 
        dataAttr(str) -- Specify the attribute to check for extra data or use default(NONE)
            cgmMsgData is our default. Data is stored as a json dict of {attr:{msg:component or attr}}
        dataKey(str/int) -- data key for extra data. If None provided, attr name is used.
        simple(bool) -- Will only store dag nodes when specified

    :returns
        status(bool)
    """
    try:
        _str_func = 'set_message'    
        
        _d = validate_arg(messageHolder,messageAttr)
        _combined = _d['combined']
    
        #>> Validation -----------------------------------------------------------------------------------------------
        _mode = 'reg'
        _messagedNode = None
        _messagedExtra = None
        _d_dataAttr = None
        
        if dataAttr is None:
            dataAttr = "{0}_datdict".format(messageAttr)        
        
        _multi = False
        if mc.objExists(_combined) and mc.addAttr(_combined,q=True,m=True):
            _multi = True
            if not message:
                log.debug("|{0}| >> multimessage delete...".format(_str_func))
                delete(_combined)
                add(_combined,'message',m=True,im=False)

                return True            
            
        if issubclass(type(message),list) or _multi:
            def storeMsgMulti(msgNodes,holderDict):
                for n in msgNodes:
                    try:
                        connect((n + ".message"),holderDict['combined'],nextAvailable=True)
                    except Exception,err:
                        log.warning("|{0}| >> {1} failed: {2}".format(_str_func, n, err))  
            if len(message) > 1 or _multi:#MULTIMESSAGE MODE...
                if mc.objExists(_combined):
                    if not get_type(_combined) == 'message':
                        log.warning("|{0}| >> Not a message attribute. converting..".format(_str_func))  
                        delete(_d)
                        add(messageHolder,messageAttr,'message',m=True,im=False)
                        storeMsgMulti(message,_d)
                        return True
                    _buffer = get_message(_combined,dataAttr)        
                    if not mc.addAttr(_combined,q=True,m=True):#not multi...
                        log.warning("|{0}| >> Not a multi message attribute. converting..".format(_str_func))  
                        delete(_d)
                        add(messageHolder,messageAttr,'message',m=True,im=False)
                        storeMsgMulti(message,_d)
                        return True                    
                        
                    else:
                        log.debug("|{0}| >> multimessage...".format(_str_func))  
                        _messageLong = [NAMES.get_long(m) for m in message]
                        if _buffer and [NAMES.get_long(m) for m in _buffer] == _messageLong:
                            log.debug("|{0}| >> message match. Good to go".format(_str_func))                            
                            return True
                        else:
                            log.debug("|{0}| >> No match...".format(_str_func))                                                    
                            connections = get_driven(_combined)
                            if connections:
                                for c in connections:
                                    break_connection(c)
                
                            delete(_d)
                            add(messageHolder,messageAttr,'message',m=True,im=False)
                            storeMsgMulti(message,_d)
                
                else:
                    log.debug("|{0}| >> new attr...".format(_str_func))                    
                    add(messageHolder,messageAttr,'message',m=True,im=False)
                    storeMsgMulti(message,_d)
                return True
            else:
                message = message[0]
                
        if message == False:
            break_connection(_d)
            return True
        
        elif '.' in message:
            if VALID.is_component(message):
                _l_msg = VALID.get_component(message)  
                _messagedNode = _l_msg[1]            
                if simple:
                    message = _l_msg[1]
                    log.debug("|{0}| >> simple. Using {1} | {2}".format(_str_func,message,_l_msg))
                else:
                    _mode = 'comp'
                    log.debug("|{0}| >> componentMessage: {1}".format(_str_func,_l_msg)) 
                    _messagedExtra = _l_msg[0]
            else:
                _d_msg = validate_arg(message)   
                _messagedNode = _d_msg['node']            
                if simple:
                    message = _d_msg['node']
                    log.debug("|{0}| >> simple. Using {1} | {2}".format(_str_func,message,_d_msg))                
                else:
                    _mode = 'attr'
                    log.debug("|{0}| >> attrMessage: {1}".format(_str_func,_d_msg))
                    _messagedExtra = _d_msg['attr']
        elif VALID.is_shape(message):
            _mode = 'shape'
            _messagedNode = message
        else:
            _messagedNode = message
                
        _messageLong = NAMES.get_long(message)
        
        _dataAttr = 'cgmMsgData_'
        if dataAttr is not None:
            _dataAttr = dataAttr
            
        if dataKey is None:
            dataKey = messageAttr
        else:
            dataKey = unicode(dataKey)
            
        log.debug("|{0}| >> mode: {1} | dataAttr: {2} | dataKey: {3}".format(_str_func,_mode, _dataAttr,dataKey))
        log.debug("|{0}| >> messageHolder: {1} | messageAttr: {2}".format(_str_func,messageHolder, messageAttr))
        log.debug("|{0}| >> messagedNode: {1} | messagedExtra: {2} | messageLong: {3}".format(_str_func,_messagedNode, _messagedExtra, _messageLong))
        
    
        if _messagedExtra:
            if '.' in _dataAttr:
                _d_dataAttr = validate_arg(_dataAttr)            
            else:
                _d_dataAttr = validate_arg(messageHolder,_dataAttr)
    
        #>> Node store ------------------------------------------------------------------------------------------------------------
        def storeMsg(msgNode,msgExtra,holderDict,dataAttrDict=None, dataKey = None, mode = None):
            if mode not in ['sphape']:
                connect((msgNode + ".message"),holderDict['combined'])
                
            if msgExtra:
                log.debug("|{0}| >> '{1}.{2}' stored to: '{3}'".format(_str_func,msgNode,msgExtra, holderDict['combined']))
                
                if not mc.objExists(dataAttrDict['combined']):
                    add(dataAttrDict['node'],dataAttrDict['attr'],'string')
                            
                if get_type(dataAttrDict['combined']) != 'string':
                    raise ValueError,"DataAttr must be string. {0} is type {1}".format(dataAttrDict['combined'], get_type(dataAttrDict['combined']) )
                
                mi_node = r9Meta.MetaClass(_d['node'])
                _dBuffer = mi_node.__getattribute__(dataAttrDict['attr']) or {}
                _dBuffer[dataKey] = _messagedExtra
                log.debug("|{0}| >> buffer: {1}".format(_str_func,_dBuffer))
                mi_node.__setattr__(dataAttrDict['attr'], _dBuffer)
                #setlock
                return True
            
            log.debug("|{0}| >> '{1}' stored to: '{2}'".format(_str_func,msgNode, _combined))        
            return True
        
        if _mode == 'shape':
            copy_to(_messagedNode,'viewName',messageHolder,messageAttr,driven='target')
            storeMsg(_messagedNode, _messagedExtra, _d, _d_dataAttr,dataKey,'shape')  
            #set_lock(_d,True)
            return True
        if mc.objExists(_combined):
            if not get_type(_combined) == 'message':
                log.warning("|{0}| >> Not a message attribute. converting..".format(_str_func))  
                delete(_d)
                add(messageHolder,messageAttr,'message',m=False)
                storeMsg(_messagedNode, _messagedExtra, _d, _d_dataAttr,dataKey)
                return True
            
            _buffer = get_message(_combined,dataAttr,dataKey = dataKey, simple = simple)        
            if not mc.addAttr(_combined,q=True,m=True):#not multi...
                log.debug("|{0}| >> messageSimple...".format(_str_func))
                if _buffer and NAMES.get_long(_buffer[0]) == _messageLong:
                    log.debug("|{0}| >> message match. Good to go".format(_str_func))                            
                    return True
                else:
                    break_connection(_d)
                    storeMsg(_messagedNode, _messagedExtra, _d, _d_dataAttr,dataKey)
                
            else:
                log.debug("|{0}| >> multimessage...".format(_str_func))  
                if _buffer and NAMES.get_long(_buffer[0]) == _messageLong:
                    log.debug("|{0}| >> message match. Good to go".format(_str_func))                            
                    return True
                else:
                    connections = get_driven(_combined)
                    if connections:
                        for c in connections:
                            break_connection(c)
        
                    delete(_d)
                    add(messageHolder,messageAttr,'message',m=False)
                    storeMsg(_messagedNode, _messagedExtra, _d, _d_dataAttr,dataKey)
        
        else:
            log.debug("|{0}| >> new attr...".format(_str_func))                    
            add(messageHolder,messageAttr,'message',m=False)
            storeMsg(_messagedNode, _messagedExtra, _d, _d_dataAttr,dataKey)
            
        return True
    except Exception,err:cgmGen.cgmExceptCB(Exception,err)
    
def convert_type(node = None, attr = None, attrType = None):
    """   
     Attempts to convert an existing attrType from one type to another. 
     Enum's are stored to strings as 'option1;option2'.
     Strings with a ';' will split to enum options on conversion.

    :parameters:
        node(str) -- 
        attr(str) -- 
        attrType(str) -- 

    :returns
        status(bool)
    """
    _str_func = 'convert_type'    
    
    _attrType = attrType
    if '.' in node or issubclass(type(node),dict):
        _d = validate_arg(node)
        _attrType = attr
    else:
        _d = validate_arg(node,attr)  
    _combined = _d['combined']
    
    _attrType = validate_attrTypeName(_attrType)
    _typeCurrent = validate_attrTypeName(get_type(_d))
    
    log.debug("|{0}| >> attr: {1} | type: {2} | targetType: {3}".format(_str_func,_combined,_typeCurrent, _attrType))
    
    if _attrType == _typeCurrent:
        log.debug("|{0}| >> {1} already target type.".format(_str_func,_combined))
        return True
    
    #Gather data -----------------------------------------------------------------------
    _lock = False
    if is_locked(_d):
        _lock = True
        mc.setAttr(_combined,lock=False)
        
    _driver = None
    _driven = None
    _data = None
    _enum = 'off','on'
    
    _driver = get_driver(_d,skipConversionNodes=True)
    _driven = get_driven(_d,skipConversionNodes=True)
    
    if _typeCurrent == 'enum':
        _enum = get_enum(_d).split(':')

    if _typeCurrent == 'message':
        _data = get_message(_d)
    elif _typeCurrent == 'enum':
        _data = get_enumValueString(_d)
    else:
        _data = get(_d)
          
    delete(_d)
    
    #Rebuild -----------------------------------------------------------   
    
    if _attrType == 'enum':
        if _data:
            if VALID.stringArg(_data):
                for o in [":",",",";"]:
                    if o in _data:
                        _enum = _data.split(o)
                        break
                                    
    add(_d,_attrType,enumOptions=_enum)
        
    if _data is not None:
        log.debug("|{0}| >> Data setting: {1}".format(_str_func,_data))    
        try:
            if _attrType == 'string':
                if _typeCurrent == 'message':
                    _data = ','.join(_data)
                else:
                    _data = str(_data)
            elif _attrType == 'double':
                _data = float(_data)
            elif _attrType == 'long':
                _data = int(_data)
        except Exception,err:
            log.error("|{0}| >> Failed to convert data: {1} | type: {2} | err: {3}".format(_str_func,_data,_attrType,err))        
        
        
        try:set(_d, value = _data)
        except Exception,err:
            log.error("|{0}| >> Failed to set back data buffer {1} | data: {2} | err: {3}".format(_str_func,_combined,_data,err))        

    if _driver and _typeCurrent != 'message':
        log.debug("|{0}| >> Driver: {1}".format(_str_func,_driver))
        try:connect(_driver,_combined)
        except Exception,err:
            log.error("|{0}| >> Failed to connect {1} >--> {2} | err: {3}".format(_str_func,_driver,_combined,err))        
                
    if _driven:
        log.debug("|{0}| >> Driven: {1}".format(_str_func,_driven))
        for c in _driven:
            log.debug("|{0}| >> driven: {1}".format(_str_func,c))
            try:connect(_combined,c)
            except Exception,err:
                log.error("|{0}| >> Failed to connect {1} >--> {2} | err: {3}".format(_str_func,_combined,c,err))        
        
    if _lock:
        mc.setAttr(_combined,lock = True)     
    return True

def reorder_ud(node):
    ud = mc.listAttr(node,ud=True)
    if ud:
        ud.sort()
        reorder(node,ud,top=True)

def reorder(node = None, attrs = None, direction = 0,top = False):
    """   
    :Acknowledgement:
    Thank you to - http://www.the-area.com/forum/autodesk-maya/mel/how-can-we-reorder-an-attribute-in-the-channel-box/

    Reorders attributes on an object

    :parameters:
        node(str) -- 
        attrs(list) must be attributes on the object
        direction(int) - 0 is is negative (up on the channelbox), 1 is positive (up on the channelbox)

    :returns
        status(bool)
    """
    _str_func = 'reorder'    
    
    attrs = VALID.listArg(attrs)
    
    for a in attrs:
        assert mc.objExists(node+'.'+a) is True, "|{0}|>> . '{1}.{2}' doesn't exist. Swing and a miss...".format(_str_func,node,a)
        
    _l_user = mc.listAttr(node,userDefined = True)
    _to_move = []
    
    for a in _l_user:
        if not is_hidden(node,a):
            _to_move.append(a)

    log.debug(_to_move)
    if top:
        attrs.reverse()
        for a in attrs:
            if a in _to_move:
                _to_move.remove(a)
                _to_move.insert(0,a)
    else:
        _to_move = lists.reorderListInPlace(_to_move,attrs,direction)
    log.debug(_to_move)
    
    #To reorder, we need delete and undo in the order we want
    _d_locks = {}
    _l_relock = []
    
    for a in _to_move:
        try:
            mc.undoInfo(ock=True)
            _d = validate_arg(node,a)
            _lock = False
            if is_locked(_d):
                set_lock(_d,False)
                _lock = True
                
            #mc.undo(ock=True)
            #mc.deleteAttr(_d['combined'])
            delete(_d)
            #delete(_d)


        except Exception,err:
            log.error("|{0}| >> {1} || err: {2}".format(_str_func,_d['combined'],err))
        finally:
            mc.undoInfo(cck=True)
            mc.undo()
            if _lock:
                set_lock(_d,True)            
            
    mc.select(node)
    

#>>>==============================================================================================
#>> datList/msgList
#>>>==============================================================================================
def get_sequentialAttrDict(node, attr = None):
    """   
    Get dict of sequential attrs. This is mainly used for our own storage methods

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'get_sequentialAttrDict'
    
    _res = {}
    _l_user = mc.listAttr(node, userDefined=True) or []
    for a in _l_user:
        if '_' in a:
            _split = a.split('_')
            _int_ = _split[-1]
            _str_ = ('_').join(_split[:-1])
            if str(attr) == _str_:
                try:
                    _res[int(_int_)] = a
                except:
                    log.debug("|{0}| >> {1}.{2} failed to int. | int: {3}".format(_str_func,NAMES.get_short(node),a,_int_))     	               	
    return _res

def get_nextAvailableSequentialAttrIndex(node, attr = None):
    """   
    Get next available attribute in sequence.

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        type(string)
    """ 
    _str_func = 'get_nextAvailableSequentialAttrIndex'
    
    _exists = False
    _i = 0
    while _exists == False and _i < 100:
        _attr = "{0}_{1}".format(attr,_i)
        log.debug("|{0}| >> attr: {1}".format(_str_func,_attr))        
        if has_attr(node,_attr):
            _i += 1
        else:
            _exists = True
            return _i            
    return False

def datList_purge(node = None, attr = None, dataAttr=None):
    """   
    Purge a dat list if it exists.

    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...

    :returns
        status(bool)
    """    
    _str_func = 'datList_purge'        
    d_attrs = get_sequentialAttrDict(node,attr)
    
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)
        """
    for k in d_attrs.keys():
        str_attr = d_attrs[k]
        delete(node,str_attr)
        log.debug("|{0}| >> Removed: '{1}.{2}'".format(_str_func,node,str_attr))
        
    try:
        if r9Meta.MetaClass(node).hasAttr(dataAttr):
            delete(node,dataAttr)
            log.debug("|{0}| >> Removed: '{1}.{2}'".format(_str_func,node,dataAttr))
    except:pass
    
    return True    
msgList_purge = datList_purge

def datList_exists(node = None, attr = None, mode = None, dataAttr = None):
    """   
    Check if a cgm datList exists.

    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        mode(str) -- msg - only checks for messages for msgList

    :returns
        status(bool)
    """
    _str_func = 'datList_exists'    
    
    d_attrs = get_sequentialAttrDict(node,attr)
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)    
    
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)
        """
    for i,k in enumerate(d_attrs.keys()):
        str_attr = d_attrs[i]
        if mode == 'message':
            if get_message(node,str_attr,dataAttr):
                return True
        elif get(node,str_attr) is not None:
            return True
    return False  

def msgList_exists(node = None, attr = None,dataAttr = None):
    return datList_exists(node,attr,'message',dataAttr)

def msgList_connect(node = None, attr = None, data = None, connectBack = None, dataAttr = None):
    """   
    Because multimessage data can't be counted on for important sequential connections we have
    implemented this.

    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...

    :returns
        status(bool)
    """
    _str_func = 'msgList_connect'    
    _l_dat = VALID.mNodeStringList(data)
    
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)
        
    #_l_dat = VALID.objStringList(data,noneValid=True)
    log.debug("|{0}| >> node: {1} | attr: {2} | connectBack: {3} | dataAttr: {4}".format(_str_func,node,attr,connectBack,dataAttr))
    log.debug("|{0}| >> data | len: {1} | list: {2}".format(_str_func, len(_l_dat), _l_dat))
    
    datList_purge(node,attr)
    
    mi_node = r9Meta.MetaClass(node)
    
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)
        
    mi_node.addAttr(_str_dataAttr, value="",attrType= 'string')
    _dBuffer = {'mode':'msg'}
    log.debug("|{0}| >> buffer: {1}".format(_str_func,_dBuffer))
    mi_node.__setattr__(_str_dataAttr, _dBuffer)    
    """
    
    for i,_node in enumerate(_l_dat):
        str_attr = "{0}_{1}".format(attr,i)
        
        set_message(node, str_attr, _node, dataAttr, i)
       
        if connectBack is not None:
            if '.' in _node:
                _n = _node.split('.')[0]
            else:_n = _node
            set_message(_n, connectBack, node, simple = True)
    
    return True
msgList_set = msgList_connect
def datList_connect(node = None, attr = None, data = None, mode = None, dataAttr=None,enum='off:on'):
    """   
    Because multimessage data can't be counted on for important sequential connections we have
    implemented this.

    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        data(varied) -- whatever you want stored
        mode(str) -- what kind of data to be looking for
            NONE - just get the data
            message - getMessage
    :returns
        status(bool)
    """
    _str_func = 'datList_connect'    
    
    _l_dat = VALID.listArg(data)
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)
        
    log.debug("|{0}| >> node: {1} | attr: {2} | mode: {3}".format(_str_func,node,attr,mode))
    log.debug("|{0}| >> data | len: {1} | list: {2}".format(_str_func, len(_l_dat), _l_dat))
    
    l_attrs = datList_getAttrs(node,attr)
    d_driven = {}
    for i,a in enumerate(l_attrs):
        _driven = get_driven(node,a)
        if _driven:
            d_driven[i] = _driven
        else:
            d_driven[i] = False
            
    datList_purge(node,attr)
    
    #mi_node = r9Meta.MetaClass(node)
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)    
    """
    if mode == 'message':
        msgList_connect(node,attr,_l_dat,dataAttr=dataAttr)
        if _plug:
            for p in _plug:
                try:
                    connect("{0}.{1}".format(node,attr), p)
                except Exception,err:
                    log.warning("|{0}| >> Failed to reconnect {1} | driven: {2} | err: {3}".format(_str_func, str_attr,p,err ))
        
    elif mode == 'enum':
        for i,v in enumerate(_l_dat):
            str_attr = "{0}_{1}".format(attr,i)
            if not has_attr(node,str_attr):
                log.info(cgmGEN.logString_msg(_str_func,'New enum dat attr: {0} | {1}'.format(str_attr, v)))
                
                add(node,str_attr,'enum',value= v, enumOptions=enum,keyable=False)
            else:
                log.info(cgmGEN.logString_msg(_str_func,'Exisiting enum dat attr: {0} | {1}'.format(str_attr, v)))
                strValue = get_enumValueString(node,str_attr)
                add(node,str_attr,'enum',enumOptions=enum,value = v, keyable=False)
                if strValue:
                    set(node,str_attr,strValue)        
        
    else:
        """_str_dataAttr = "{0}_datdict".format(attr)
        mi_node.addAttr(_str_dataAttr, value="",attrType= 'string')
        _dBuffer = {'mode':'msg'}
        log.debug("|{0}| >> buffer: {1}".format(_str_func,_dBuffer))
        mi_node.__setattr__(_str_dataAttr, _dBuffer)"""    
        
        for i,_data in enumerate(_l_dat):
            str_attr = "{0}_{1}".format(attr,i)
            store_info(node, str_attr, _data, mode)
            _plug =  d_driven.get(i)
            if _plug:
                for p in _plug:
                    try:
                        connect("{0}.{1}".format(node,str_attr), p)
                    except Exception,err:
                        log.warning("|{0}| >> Failed to reconnect {1} | driven: {2} | err: {3}".format(_str_func, str_attr,p,err ))
                    
    return True

def msgList_get(node = None, attr = None, dataAttr = None, cull = False, ):
    return datList_get(node,attr,'message', dataAttr, cull)

def datList_get(node = None, attr = None, mode = None, dataAttr = None, cull = False,enum=False ):
    """   
    Get datList return.
    
    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        mode(str) -- what kind of data to be looking for
            NONE - just get the data
            message - getMessage
        dataAttr(str) - Attr to store extra info. If none specified, makes default
        cull(bool) - Cull for empty entries

    :returns
        dataList(list)
    """
    _str_func = 'datList_get'
    
    if mode is not None:
        _mode = validate_attrTypeName(mode)
    else:_mode = mode
    
    log.debug("|{0}| >> node: {1} | attr: {2} | mode: {3} | cull: {4}".format(_str_func,node,attr,_mode,cull))
    
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)    
    """
    d_attrs = get_sequentialAttrDict(node,attr)
    
    l_return = []
    ml_return = []
    
    for k in d_attrs.keys():
        if _mode == 'message':
            _res = get_message(node,d_attrs[k], dataAttr, k ) or None
            if _res:_res = _res[0]
        else:
            try:
                if enum:
                    if get_type(node,d_attrs[k]) == 'enum':
                        _res = get_enumValueString(node,d_attrs[k])
                    else:
                        _res = get(node,d_attrs[k])
                else:
                    _res = get(node,d_attrs[k])
            except Exception,err:
                log.warning("|{0}| >> {1}.{2} Failed! || err: {3}".format(_str_func,node,d_attrs[k],err))
                _res = None
        if issubclass(type(_res),list):
            if _mode == 'message' or mc.objExists(_res[0]):
                l_return.extend(_res)
            else:l_return.append(_res)
        else:l_return.append(_res)
        #if asMeta:
            #ml_return.append( validateObjArg(str_msgBuffer,noneValid=True) )
            #log.debug("index: %s | msg: '%s' | mNode: %s"%(i,str_msgBuffer,ml_return[i]))
        #else:log.debug("index: %s | msg: '%s' "%(i,str_msgBuffer))

    if cull:
        l_return = [o for o in l_return if o != None]
    if l_return.count(None) == len(l_return):
        return []
    return l_return

def datList_getAttrs(node = None, attr = None):
    """   
    Get the attributes of a datList
    
    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...

    :returns
        status(bool)
    """
    _str_func = 'datList_get'
    
    d_attrs = get_sequentialAttrDict(node,attr)
    return [d_attrs[i] for i in d_attrs.keys()]
msgList_getAttrs = datList_getAttrs

def msgList_index(node = None, attr = None, data = None, dataAttr = None):
    return datList_index(node,attr,VALID.mNodeString(data),'message',dataAttr)

def datList_index(node = None, attr = None, data = None, mode = None, dataAttr = None):
    """   
    Index a value in a given datList.
    
    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        data(str) -- data to index
        mode(str) -- what kind of data to be looking for
            NONE - just get the data
            message - getMessage
    :returns
        status(bool)
    """
    _str_func = 'datList_index'    
    
    log.debug("|{0}| >> node: {1} | attr: {2} | data: {3} | mode: {4}".format(_str_func,node,attr,data,mode))
    
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)     
    """
    _l_dat = datList_get(node,attr,mode,dataAttr,False)
    idx = None    
    
    if mode == 'message':
        _l_long = [NAMES.get_long(o) for o in _l_dat]
        _str_long = NAMES.get_long(data)
        #log.debug(_l_long)
        #log.debug(_str_long)
        if _str_long in _l_long:
            idx = _l_long.index(_str_long)
    elif data in _l_dat:
        if _l_dat.count(data) > 1:
            raise ValueError,"More than one entry"
        else:
            idx = _l_dat.index(data) 
    
    if idx is None:
        log.debug("|{0}| >> Data not found. node: {1} | attr: {2} | data: {3} | mode: {4}".format(_str_func,node,attr,data,mode))
        log.debug("|{0}| >> values...".format(_str_func))
        for i,v in enumerate(_l_dat):
            log.debug("idx: {0} | {1}".format(i,v))
        raise ValueError,"Data not found"
    return idx

def msgList_append(node = None, attr = None, data = None, connectBack = None,dataAttr=None):
    _data = VALID.mNodeString(data)
    _res = datList_append(node, attr,VALID.mNodeString(data),'message',dataAttr)
    if connectBack is not None:
        set_message(_data, connectBack, node, dataAttr)
    return _res


def datList_append(node = None, attr = None, data = None, mode = None, dataAttr = None):
    """   
    Append datList.
    
    :parameters:
        data(varied) -- object or value to add to our datList
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...

    :returns
        status(bool)
    """
    _str_func = 'datList_append'    
    
    log.debug("|{0}| >> node: {1} | attr: {2} | data: {3} | mode: {4}".format(_str_func,node,attr,data,mode))
    
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)
        """
    _l_dat = datList_get(node,attr,mode,dataAttr,False)
    _len = len(_l_dat)
    _idx = _len
    
        
    if mode == 'message':
        set_message(node, "{0}_{1}".format(attr,_idx), data, dataAttr, dataKey=_idx)
    else:
        store_info(node,"{0}_{1}".format(attr,_idx),data)
    
    return _idx

def datList_setByIndex(node = None, attr = None, data = None, mode = None, dataAttr=None, indices=None):
    """   
    Set datList value by index.
    
    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        indices(ints) -- indexes you want removed
    :returns
        status(bool)
    """
    _str_func = 'datList_setByIndex'    
    _indices = VALID.listArg(indices)
    d_attrs = get_sequentialAttrDict(node,attr)
    
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)

    
    log.debug("|{0}| >> node: {1} | attr: {2} | indices: {3}".format(_str_func,node,attr,_indices))
    
    for i in d_attrs.keys():
        if i in _indices:
            log.warning("|{0}| >> Setting... | idx: {1} | attr: {2}".format(_str_func,i,d_attrs[i]))
            
            if mode == 'message':
                set_message(node,d_attrs[i],data,dataAttr=dataAttr)

                
            else:
                _plug = get_driven(node,d_attrs[i]) or False
                store_info(node, d_attrs[i], data, mode)
                if _plug:
                    for p in _plug:
                        try:
                            connect("{0}.{1}".format(node,d_attrs[i]), p)
                        except Exception,err:
                            log.warning("|{0}| >> Failed to reconnect {1} | driven: {2} | err: {3}".format(_str_func, str_attr,p,err ))
            
    
    return True

def datList_removeByIndex(node = None, attr = None, indices = None):
    """   
    Append datList.
    
    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        indices(ints) -- indexes you want removed
    :returns
        status(bool)
    """
    _str_func = 'datList_removeByIndex'    
    _indices = VALID.listArg(indices)
    d_attrs = get_sequentialAttrDict(node,attr)
    
    log.debug("|{0}| >> node: {1} | attr: {2} | indices: {3}".format(_str_func,node,attr,_indices))
    
    for i in d_attrs.keys():
        if i in _indices:
            log.warning("|{0}| >> removing... | idx: {1} | attr: {2}".format(_str_func,i,d_attrs[i]))
            delete(node,d_attrs[i])
    
    return True
msgList_removeByIndex = datList_removeByIndex
  
def msgList_remove(node = None, attr = None, data = None, dataAttr = None):
    return datList_remove(node,attr,VALID.mNodeString(data),'message',dataAttr)

def datList_remove(node = None, attr = None, data = None, mode = None, dataAttr = None):
    """   
    Append datList.
    
    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        data(varied) -- object or value to remove from our datList
        mode(str) -- what kind of data to be looking for
            NONE - just get the data
            message - getMessage
    :returns
        status(bool)
    """
    _str_func = 'datList_remove'    
    _data = VALID.listArg(data)        
    d_attrs = get_sequentialAttrDict(node,attr)
    
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)
        """
    log.debug("|{0}| >> node: {1} | attr: {2} | data: {3} | mode: {4}".format(_str_func,node,attr,data,mode))
    
    _action = False
    if mode == 'message':
        _data = VALID.objStringList(_data,calledFrom=_str_func)
        _l_dat_long = [NAMES.get_long(o) for o in _data]  
        
        for i in d_attrs.keys():
            _o = get_message(node, d_attrs[i],"{0}_datdict".format(attr), dataKey=i)
            if _o and NAMES.get_long(_o) in _l_dat_long:
                log.debug("|{0}| >> removing... | idx: {1} | attr: {2} | value: {3}".format(_str_func,i,d_attrs[i],_o))
                delete(node,d_attrs[i])       
                _action = True
    else:
        d_attrs = get_sequentialAttrDict(node,attr)
        for i in d_attrs.keys():
            _v =  get(node,d_attrs[i])
            if _v in _data:
                log.debug("|{0}| >> removing... | idx: {1} | attr: {2} | value: {3}".format(_str_func,i,d_attrs[i],_v))
                delete(node,d_attrs[i])
                _action = True
    return _action
                
      
def msgList_clean(node = None, attr = None,dataAttr=None):
    return datList_clean(node,attr,'message',dataAttr)

def datList_clean(node = None, attr = None, mode = None, dataAttr = None):
    """   
    Remove dead data from a datList and reconnect
    
    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        mode(str) -- what kind of data to be looking for
            NONE - just get the data
            message - getMessage
    :returns
        status(bool)
    """
    _str_func = 'datList_clean'    
    
    if dataAttr is None:
        dataAttr = "{0}_datdict".format(attr)
    
    """
    if dataAttr is not None:
        _str_dataAttr = dataAttr
    else:
        _str_dataAttr = "{0}_datdict".format(attr)
        """
    l_dat = datList_get(node,attr,mode,dataAttr,True)
    
    if mode == 'message':
        return msgList_connect(node,attr,l_dat,dataAttr=dataAttr)
    else:
        return datList_connect(node,attr,l_dat,mode,dataAttr)
#>>>==============================================================================================
#>> Utilities
#>>>==============================================================================================

def copy_to(fromObject, fromAttr, toObject = None, toAttr = None,
            convertToMatch = True, values = True, inConnection = False, outConnections = False,
            keepSourceConnections = True, copySettings = True,
            driven = None):
    """   
    Copy attributes from one object to another as well as other options. If the attribute already
    exists, it'll copy the values. If it doesn't, it'll make it. If it needs to convert, it can.
    It will not make toast.  

    :parameters:
        fromObject(string) - obj with attrs
        fromAttr(string) - source attribute
        toObject(string) - obj to copy to
        toAttr(string) -- name of the attr to copy to . Default is None which will create an 
                      attribute of the fromAttr name on the toObject if it doesn't exist
        convertToMatch(bool) -- whether to automatically convert attribute if they need to be. Default True                  
        values(bool) -- copy values. default True
        inputConnections(bool) -- default False
        outGoingConnections(bool) -- default False
        keepSourceConnections(bool)-- keeps connections on source. default True
        copySettings(bool) -- copy the attribute state of the fromAttr (keyable,lock,hidden). default True
        driven(string) -- 'source','target' - whether to connect source>target or target>source

    :returns
        success(bool)
    """ 
    _str_func = 'copy'
    
    _d = validate_arg(fromObject,fromAttr) 
    _combined = _d['combined']
    _node = _d['node']
    _attr = _d['attr']
    _toObject = toObject
    _toAttr = toAttr
    
    if _toObject is None:
        log.debug("|{0}| >> No toObject specified. Using fromObject: {1}".format(_str_func,fromObject))
        _toObject = fromObject
    if _toAttr is None:
        log.debug("|{0}| >> No toAttr specified. Using fromAttr: {1}".format(_str_func,fromAttr))
        _toAttr = fromAttr
    _d_targetAttr = validate_arg(_toObject,_toAttr)
    
    if _combined == _d_targetAttr['combined']:
        raise ValueError,"Cannot copy to self."
        
    log.debug("|{0}| >> source: {1}".format(_str_func,_combined))    
    log.debug("|{0}| >> target: {1} | {2}".format(_str_func,_toObject,_toAttr))    
    
    #>>> Gather info --------------------------------------------------------------------------------------
    _d_sourceFlags = get_standardFlagsDict(_d)
    
    if values and not validate_attrTypeName(_d_sourceFlags['type']):
        log.warning("|{0}| >> {1} is a {2} attr and not valid for copying".format(_str_func,_d['combined'],_d_sourceFlags['type']))
        return False   

    #cgmGen.log_info_dict(_d_sourceFlags,_combined)
    
    _driver = get_driver(_d,skipConversionNodes=True)
    _driven = get_driven(_d,skipConversionNodes=True)
    _data = get(_d)
    
    log.debug("|{0}| >> data: {1}".format(_str_func,_data))    
    log.debug("|{0}| >> driver: {1}".format(_str_func,_driver))
    log.debug("|{0}| >> driven: {1}".format(_str_func,_driven))    
    
    #>>> First get our attribute ---------------------------------------------------------------------
    _goodToGo = True
    _targetExisted = False
    _relockSource = False    
    
    #cgmGen.log_info_dict(_d_targetAttr)
    if mc.objExists(_d_targetAttr['combined']):
        _targetExisted = True
        _d_targetFlags = get_standardFlagsDict(_d_targetAttr)
        
        if not validate_attrTypeName(_d_targetFlags['type']):
            log.warning("|{0}| >> {1} may not copy correctly. Type did not validate.".format(_str_func,_d_targetAttr['combined']))
        
        if not validate_attrTypeMatch(_d_sourceFlags['type'],_d_targetFlags['type']):
            if _d_targetFlags['dynamic'] and convertToMatch:
                log.debug("|{0}| >> {1} Not the correct type, conversion necessary...".format(_str_func,_d_targetAttr['combined']))
                #_relockSource
                convert_type(_d_targetAttr,_d_sourceFlags['type'])
            else:
                raise Exception,"|{0}| >> {1} Not the correct type, conversion necessary and convertToMatch is off".format(_str_func,_d_targetAttr['combined'])
                _goodToGo = False
    else:
        add(_d_targetAttr, _d_sourceFlags['type'])
            
    #>>> Get our values over -------------------------------------------------------------------------
    
    if _data is not None :
        try:set(_d_targetAttr,value = _data)
        except Exception,err:
            log.error("|{0}| >> Failed to set back data buffer {1} | data: {2} | err: {3}".format(_str_func,_d_targetAttr['combined'],_data,err))        
   
    if _driver and inConnection:
        if _d_sourceFlags['type'] != 'message':
            log.debug("|{0}| >> Current Driver: {1}".format(_str_func,_driver))
            try:connect(_driver,_d_targetAttr['combined'])
            except Exception,err:
                log.error("|{0}| >> Failed to connect {1} >--> {2} | err: {3}".format(_str_func,_driver,_d_targetAttr['combined'],err))        
                    
    if _driven and outConnections:
        log.debug("|{0}| >> Current Driven: {1}".format(_str_func,_driven))
        for c in _driven:
            _d_driven = validate_arg(c)
            if _d_driven['combined'] != _d_targetAttr['combined']:
                log.debug("|{0}| >> driven: {1}".format(_str_func,c))
                try:connect(_d_targetAttr['combined'],c)
                except Exception,err:
                    log.error("|{0}| >> Failed to connect {1} >--> {2} | err: {3}".format(_str_func,_d_targetAttr['combined'],c,err))        
        
        
    if copySettings:
        if _d_sourceFlags.get('enum'):
            mc.addAttr (_d_targetAttr['combined'], e = True, at=  'enum', en = _d_sourceFlags['enum'])
        if _d_sourceFlags['numeric']:
            _children = get_children(_d)
            if _children:
                for c in _children:
                    _d_c = get_standardFlagsDict(_node,c)
                    _buffer = "{0}.{1}".format(_d_targetAttr['node'],c)
                    if _d_c['default']:
                        mc.addAttr(_buffer,e=True,dv = _d_c['default'])
                    if _d_c['max']:
                        mc.addAttr(_buffer,e=True,maxValue = _d_c['max'])                
                    if _d_c['min']:
                        mc.addAttr(_buffer,e=True,minValue = _d_c['min'])                
                    if _d_c['softMax']:
                        mc.addAttr(_buffer,e=True,softMaxValue = _d_c['softMax'])                
                    if _d_c['softMin']:
                        mc.addAttr(_buffer,e=True,softMinValue = _d_c['softMin'])                      
            else:
                if _d_sourceFlags['default']:
                    mc.addAttr(_d_targetAttr['combined'],e=True,dv = _d_sourceFlags['default'])
                if _d_sourceFlags['max']:
                    mc.addAttr(_d_targetAttr['combined'],e=True,maxValue = _d_sourceFlags['max'])                
                if _d_sourceFlags['min']:
                    mc.addAttr(_d_targetAttr['combined'],e=True,minValue = _d_sourceFlags['min'])                
                if _d_sourceFlags['softMax']:
                    mc.addAttr(_d_targetAttr['combined'],e=True,softMaxValue = _d_sourceFlags['softMax'])                
                if _d_sourceFlags['softMin']:
                    mc.addAttr(_d_targetAttr['combined'],e=True,softMinValue = _d_sourceFlags['softMin'])                
 
        mc.setAttr(_d_targetAttr['combined'],e=True,channelBox = not _d_sourceFlags['hidden'])
        mc.setAttr(_d_targetAttr['combined'],e=True,keyable = _d_sourceFlags['keyable'])
        mc.setAttr(_d_targetAttr['combined'],e=True,lock = _d_sourceFlags['locked'])
 
     
    if driven == 'target':
        try:            
            connect(_d,_d_targetAttr)
        except Exception,err:
            log.error("|{0}| >> Failed to connect source to target {1} >--> {2} | err: {3}".format(_str_func,_combined,_d_targetAttr['combined'],err))        
    elif driven == 'source':
        try:            
            connect(_d_targetAttr,_d)
        except Exception,err:
            log.error("|{0}| >> Failed to connect target to source {1} >--> {2} | err: {3}".format(_str_func,_d_targetAttr['combined'],_combined,err))        
           
    if _d_sourceFlags['locked']:
        mc.setAttr(_d_targetAttr['combined'],lock = True)  
        
    return True

def store_info(node = None, attr = None, data = None, attrType = None, lock = True):
    """   
    Store information to an attribute.
    
    Supported: message,doubleArray,json dicts and much more
    
    :parameters:
        node(str) -- 
        attr(str) -- base name for the datList. becomes attr_0,attr_1,etc...
        data(varied) -- data to add
        attrType(varied) -- specify, if not specified will pick best guess
        lock(bool)

    :returns
        status(bool)
    """
    try:
        _str_func = 'store_info'    
        _data = VALID.listArg(data)        
    
        
        if attrType is None:
            #if mc.objExists(_data[0]) and _data[0] not in ['front','top','side','perp']:
            #    attrType = 'message'
            _mNode = False
            try:
                _data = [o.mNode for o in _data]
                _mNode=True
                attrType = 'message'
                log.debug("|{0}| >> mNode no arg passed...".format(_str_func))            
                
            except:pass
            if not _mNode:
                if len(_data)==3:
                    attrType = 'double3'
                elif len(_data)>3:
                    attrType = 'doubleArray'
                
        log.debug("|{0}| >> node: {1} | attr: {2} | data: {3} | attrType: {4}".format(_str_func,node,attr,_data,attrType))
        
        #>> Store our data #-------------------------------------------------------------------------
        
        if attrType in ['message','msg','messageSimple']:
            log.debug("|{0}| >> message...".format(_str_func))            
            set_message(node,attr,_data)
        elif attrType in ['double3']:
            log.debug("|{0}| >> list...".format(_str_func))            
            mi_node = r9Meta.MetaClass(node)
            
            if mi_node.hasAttr(attr):
                try:set(node,attr,_data)
                except:
                    log.warning("|{0}| >> removing... | node: {1} | attr: {2} | value: {3}".format(_str_func,node,attr,mi_node.__getattribute__(attr)))        
                    delete(node,attr)
                    mi_node.addAttr(attr,_data, attrType = attrType)
            else:
                mi_node.addAttr(attr,_data, attrType = attrType)
                
        else:
            log.debug("|{0}| >> default...".format(_str_func))                        
            mi_node = r9Meta.MetaClass(node)
            
            if mi_node.hasAttr(attr):
                try:set(node,attr,_data[0])
                except:
                    log.warning("|{0}| >> removing... | node: {1} | attr: {2} | value: {3}".format(_str_func,node,attr,mi_node.__getattribute__(attr)))        
                    delete(node,attr)
                    mi_node.addAttr(attr,_data[0], attrType = attrType)
            else:
                mi_node.addAttr(attr,_data[0], attrType = attrType)
            
        if lock:
            set_lock(node,attr,lock)
        return True
    except Exception,err:
        raise cgmGen.cgmExceptCB(Exception,err)
def get_attrsByTypeDict(node,typeCheck = [],*a,**kws):
    """   
    Replacement for getAttr which get's message objects as well as parses double3 type 
    attributes to a list  

    :parameters:
        *a(varied): - Uses validate_arg 
        **kws -- pass through for getAttr on certain types

    :returns
        value(s)
    """ 
    attrs =(mc.listAttr (node,*a, **kws ))
    typeDict = {}    
    if typeCheck:
        for check in typeCheck:
            typeDict[check] = []

    if not attrs == None:   
        for a in attrs:
            try:               
                typeBuffer  = get_type(node,a)
                if typeCheck:
                    if typeBuffer and typeBuffer in typeDict.keys():
                        typeDict[typeBuffer].append(a)
                else:
                    if typeBuffer and typeBuffer in typeDict.keys():
                        typeDict[typeBuffer].append(a)
                    elif typeBuffer:
                        typeDict[typeBuffer] = [a]                    
            except:
                pass
    #cgmGen.print_dict(typeDict)
    
    if typeDict: 
        for key in typeDict.keys():
            if typeDict.get(key):
                return typeDict
    return False   

def get_compatible(node,attr,targetNode, direction = 'to'):
    """   
    Get attributes driven by an attribute

    :parameters:
        node(str) -- 
        attr(str)
        getNode(bool) -- if you want the dag node or the attribute(s)
        skipConversionNodes(bool) -- whether you want conversion nodes included in query
        longNames(bool) -- how you want the data returned name wise

    :returns
        driver(string)
    """
    _str_func = 'get_compatible'    
    _d = validate_arg(node,attr) 
    _res = []
    _type = get_type(_d)
    _l_goodTypes = []
    
    _d_compatibility= get_compatibilityDict(False)
    
    for a in mc.listAttr(targetNode):
        try:
            _combined = "{0}.{1}".format(targetNode,a)
            
            if direction == 'to':
                for k,types in _d_compatibility.iteritems():
                    log.debug(k + ' ' + _type)
                    if _type in types:
                        log.debug(k)
                        _l_goodTypes.append(k)
            else:
                pass
        except Exception,err:
            log.debug("|{0}| >> Attr failed: {1}.{2} || err: {3}".format(_str_func,targetNode,a,err))
    return _res

def get_compatibilityDict(report = False):
    """   
    Get a compatibility dict to know what kinds of attributes are compatible with others. We do this by testing connections.
    

    :returns
        driver(string)
    """
    _str_func = 'get_compatibilityDict' 
    
    _l_created = []
    _l_d_byType = []
    _l_types = []
    _d_attrsByType = {}
    _d_compatible = {}
    _d_nodePairs = {}
    
    for t in 'transform','multiplyDivide':
        _buffer = VALID.listArg( mc.createNode (t,name= (t+'_testing')))
        _l_created.extend( _buffer )
        
            #_l_created.append( VALID.get_transform(_buffer[0]))
        _buffer2 = VALID.listArg( mc.createNode (t,name= (t+'_testing2')))
        _t2 = _buffer[0]
        _l_created.extend( _buffer2 )        
        
        _d_nodePairs[_buffer[0]] = _buffer2[0]
        
    for o in _l_created:
        for a in ['string','float','enum','message']:
            add(o,a+'test',a,keyable=True)
        
    for o in _l_created:
        if report:log.debug("|{0}| >> getting attrs for {1}".format(_str_func,o))
        _d = get_attrsByTypeDict(o,keyable=True) 
        _l_d_byType.append( _d )
        for k in _d.keys():
            if k not in _d_attrsByType.keys():
                _d_attrsByType[k] = []
            for a in _d[k]:
                _d_attrsByType[k].append(a)
                
    if report:cgmGen.print_dict(_d_attrsByType,'Attr type by keys',_str_func)
    
    for k in _d_attrsByType.keys():
        _d_compatible[k] = {'out':[],'in':[]}
        for k2 in _d_attrsByType.keys():
            for n in _d_nodePairs.keys():
                atr = _d_attrsByType[k][0]
                if has_attr(n,atr):
                    n2 = _d_nodePairs[n]
                _n1_comb =  "{0}.{1}".format(n,atr)
                
                for atr2 in _d_attrsByType[k2]:
                    if has_attr(n2,atr2):
                        _n2_comb = "{0}.{1}".format(n2,atr2)
                        break
              
                    
                if _n1_comb and _n2_comb:
                    try:
                        connect(_n1_comb,_n2_comb)
                        if get(_n1_comb) == get(_n2_comb):
                            _d_compatible[k]['out'].append(k2)
                            if report:log.debug("|{0}| >> Connected out: {1} | type: {2}>{3} || value: {4}".format(_str_func,
                                                                                                                  _n1_comb,
                                                                                                                  k,k2,get(_n1_comb)))                
                        break_connection(_n2_comb)
                    
                    except:
                        pass
                    try:
                        connect(_n2_comb,_n1_comb)
                        if get(_n1_comb) == get(_n2_comb):
                            _d_compatible[k]['in'].append(k2)
                            if report:log.debug("|{0}| >> Connected in: {1} | type: {2}>{3} || value: {4}".format(_str_func,
                                                                                                                  _n1_comb,
                                                                                                                  k,k2,get(_n1_comb)))                
                        break_connection(_n1_comb)
                    
                    except:
                        pass   
        _d_compatible[k]['out'] = LISTS.get_noDuplicates(_d_compatible[k]['out'])
        _d_compatible[k]['in'] = LISTS.get_noDuplicates(_d_compatible[k]['in'])
        
    mc.delete(_l_created)
    
    if report:cgmGen.print_dict(_d_compatible,'Compatible',_str_func)
    
    return _d_compatible
        
    
    
    
            
    
def returnCompatibleAttrs(sourceObj,sourceAttr,target,*a, **kw):
    """ 
    Returns compatible attributes

    Keyword arguments:
    attrType1(string)  
    attrType1(string)  
    """
    assert mc.objExists('%s.%s'%(sourceObj,sourceAttr)) is True,"returnCompatibleAttrs error. '%s.%s' doesn't exist."%(sourceObj,sourceAttr)
    assert mc.objExists(target) is True,"'%s' doesn't exist."%(target)

    sourceType = validateRequestedAttrType( mc.getAttr((sourceObj+'.'+sourceAttr),type=True) )
    if sourceType:
        returnBuffer = []
        bufferDict = returnObjectsAttributeByTypeDict(target,attrTypesDict.get(sourceType),*a, **kw) or {}
        for key in bufferDict.keys():
            returnBuffer.extend(bufferDict.get(key))
        if returnBuffer:    
            return returnBuffer
    return False    
    

    
#>>>>REFACTORING>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def OLDdoSetOverrideSettings(obj,enabled=True,displayType=1,levelOfDetail = 0,overrideShading=1,overrideTexturing=1,overridePlayback=1,overrideVisible=1):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Sets drawing override settings on an object or it's shapes

    ARGUMENTS:
    obj(string) - the object we'd like to startfrom
    enabled(bool) - whether to enable the override or not
    displayType(int) - (1)
                Modes - 0 - Normal
                        1 - Template
                        2 - Reference

    levelOfDetail(int) -(0)
                Modes - 0 - Full
                        1 - Bounding Box
    overrideShading(bool) - (1)
    overrideTexturing(bool) - (1)
    overridePlayback(bool) - (1)
    overrideVisible(bool) - (1)

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    shapes = mc.listRelatives(obj,shapes = True)
    if shapes > 0:
        for shape in shapes:
            doSetAttr(shape, 'overrideEnabled', enabled)
            doSetAttr(shape, 'overrideDisplayType', displayType)
            doSetAttr(shape, 'overrideLevelOfDetail', levelOfDetail)
            doSetAttr(shape, 'overrideShading', overrideShading)
            doSetAttr(shape, 'overrideTexturing', overrideTexturing)
            doSetAttr(shape, 'overridePlayback', overridePlayback)
            doSetAttr(shape, 'overrideVisible', overrideVisible)
    else:
        doSetAttr(obj, 'overrideEnabled', enabled)
        doSetAttr(obj, 'overrideDisplayType', displayType)
        doSetAttr(obj, 'overrideLevelOfDetail', levelOfDetail)
        doSetAttr(obj, 'overrideShading', overrideShading)
        doSetAttr(obj, 'overrideTexturing', overrideTexturing)
        doSetAttr(obj, 'overridePlayback', overridePlayback)
        doSetAttr(obj, 'overrideVisible', overrideVisible)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDrepairMessageToReferencedTarget(obj,attr):
    """
    To be repairable, there must have been a message connection both directions.

    Assertions - 
    1) Target Attribute must be a message attribute
    2) Target is connected to a reference node

    Returns -
    Success(bool)

    """
    targetAttr = "%s.%s"%(obj,attr)
    assert mc.attributeQuery (attr,node=obj,msg=True), "'%s' isn't a message attribute. Aborted"%targetAttr

    objTest = mc.listConnections(targetAttr, p=1)
    assert mc.objectType(objTest[0]) == 'reference',"'%s' isn't returning a reference. Aborted"%targetAttr 

    ref = objTest[0].split('RN.')[0] #Get to the ref
    log.debug("Reference connection found, attempting to fix...")

    messageConnectionsOut =  mc.listConnections("%s.message"%(obj), p=1)
    if messageConnectionsOut and ref:
        for plug in messageConnectionsOut:
            if ref in plug:
                log.debug("Checking '%s'"%plug)                
                matchObj = plug.split('.')[0]#Just get to the object
                doConnectAttr("%s.message"%matchObj,targetAttr)
                log.debug("'%s' restored to '%s'"%(targetAttr,matchObj))

                if len(messageConnectionsOut)>1:#fix to first, report other possibles
                    log.warning("Found more than one possible connection. Candidates are:'%s'"%"','".join(messageConnectionsOut))
                    return False
                return matchObj
    log.warning("No message connections and reference found")
    return False












