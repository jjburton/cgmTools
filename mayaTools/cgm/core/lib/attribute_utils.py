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
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.lib import name_utils as NAMES

from cgm.lib import attributes

_d_attrTypes = {'message':('message','msg'),
                'double':('float','fl','f','doubleLinear','doubleAngle','double','d'),
                'string':('string','s','str'),
                'long':('long','int','i','integer'),
                'bool':('bool','b','boolean'),
                'enum':('enum','options','e'),
                'double3':('vector','vec','v','double3','d3'),
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


#>>> Utilities
#===================================================================
def validate_argOLD(arg):
    """
    Validate an attr arg to be more useful for the various methods of calling it

    :parameters:
        arg(varied): Object.attribute arg to check. Accepts 'obj.attr', ['obj','attr'] formats.

    :returns
        data{dict} -- {'obj','attr','combined'}
    """
    _str_func = 'validate_arg'
    if issubclass(type(arg),dict):
        if arg.get('combined'):
            log.info("|{0}| >> passed validated arg, repassing...".format(_str_func))
            return arg
        raise ValueError,"This isn't a valid dict: {0}".format(arg)
    if type(arg) in [list,tuple] and len(arg) == 2:
        obj = arg[0]
        attr = arg[1]
        combined = "%s.%s"%(arg[0],arg[1])
        if not mc.objExists(combined):
            raise StandardError,"|validate_arg| >> obj doesn't exist: %s"%combined
    elif mc.objExists(arg) and '.' in arg:
        obj = arg.split('.')[0]
        attr = '.'.join(arg.split('.')[1:])
        combined = arg
    else:
        raise ValueError,"validate_arg>>>Bad attr arg: %s"%arg

    return {'obj':obj ,'attr':attr ,'combined':combined}

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

    
def alias_get(arg, attr = None):
    """
    Gets the alias of an object attribute if there is one

    :parameters:
        arg(varied): Accepts 'obj.attr', ['obj','attr'] formats.
        attr(str): attribute to get the alias of

    :returns
        data{dict} -- {'obj','attr','combined'}
    """    
    _d = validate_arg(arg, attr)
    if mc.aliasAttr(_d['combined'],q=True):
        return mc.aliasAttr(_d['combined'],q=True) 
    return None

def alias_set(arg, alias = None):
    """   
    :parameters:
        arg(varied): Accepts 'obj.attr', ['obj','attr'] formats.
        alias(str): Value to set as the alias. If none, the alias is cleared

    """        
    _d = validate_arg(arg)    
    alias = cgmValid.stringArg(alias)
    _alias_current = alias_get(arg)
    if alias:
        try:
            if alias != alias_get(_d['combined']):
                return mc.aliasAttr(alias, _d['combined'])
            else:log.info("'{0}' already has that alias!".format(_d['combined']))
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
    _l_targets = cgmValid.objStringList(targets)

    log.info(cgmGeneral._str_hardLine)   

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
                #log.info("Checking %s"%a)
                selfBuffer = attributes.doGetAttr(_source,a)
                targetBuffer = attributes.doGetAttr(t,a)
                if a in l_targetAttrs and selfBuffer != targetBuffer:
                    #bfr = ("{0} || {1} != {2}".format(a,selfBuffer,targetBuffer))
                    _l_notMatching.append([a,selfBuffer,targetBuffer])
                    continue
                _l_matching.append(a)
                    #print ("{0}.{1} != {2}.{1}".format(self.getShortName(),a,_t))
                    #log.info("%s.%s : %s != %s.%s : %s"%(self.getShortName(),a,selfBuffer,target,a,targetBuffer))
            except Exception,error:
                log.info(error)	
                log.warning("'%s.%s'couldn't query"%(_source,a))
        log.info("Matching attrs: {0} | Unmatching: {1}".format(len(_l_matching),len(_l_notMatching)))
        log.info(cgmGeneral._str_subLine)
        for b in _l_notMatching:
            log.info("attr: {0}...".format(b[0]))
            log.info("source: {0}".format(b[1]))
            log.info("target: {0}".format(b[2]))

        log.info("{0} >>".format(_t) + cgmGeneral._str_subLine)
    log.info(cgmGeneral._str_hardLine)

    return True    


def delete(*a):
    _str_func = 'delete'
    _d = validate_arg(*a) 
    _combined = _d['combined'] 
    
    if mc.objExists(_combined):
        if get_parent(_d):raise ValueError,"{0} is child attr, try deleting parent attr: {1}".format(_combined,get_parent(_d))
        try:
            mc.setAttr(_combined,lock=False)
        except:pass            
        try:
            break_connection(_combined)
        except:pass

        mc.deleteAttr(_combined)  
        return True
    return False
        
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
    _str_func = 'get'
    _d = validate_arg(*a) 
    _combined = _d['combined']
    _obj = _d['obj']
    _attr = _d['attr']

    log.debug("|{0}| >> arg: {1}".format(_str_func,a))    
    if kws:log.debug("|{0}| >> kws: {1}".format(_str_func,kws))

    if "[" in _attr:
        log.debug("Indexed attr")
        return mc.listConnections(_combined)

    attrType = mc.getAttr(_d['combined'],type=True)
    if attrType in ['TdataCompound']:
        return mc.listConnections(_combined)		

    if mc.attributeQuery (_attr,node=_obj,msg=True):
        #return mc.listConnections(_combined) or False 
        return get_message(_d)
    elif attrType == 'double3':
        return [mc.getAttr(_obj+'.'+ a) for a in mc.attributeQuery(_attr, node = _obj, listChildren = True)]
    elif attrType == 'double':
        parentAttr = mc.attributeQuery(_attr, node =_obj, listParent = True)
        return mc.getAttr("{0}.{1}".format(_obj,parentAttr[0]), **kws)
    else:
        return mc.getAttr(_combined, **kws)

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
    else:
        _d = validate_arg(node,attr)  
    
    _combined = _d['combined']
    _obj = _d['node']
    _attr = _d['attr']
    _wasLocked = False

    log.info("|{0}| >> attr: {1} | value: {2} | lock: {3}".format(_str_func,_combined,value, lock))    
    if kws:log.debug("|{0}| >> kws: {1}".format(_str_func,kws))  

    _aType =  mc.getAttr(_combined,type=True)
    _validType = validate_attrTypeName(_aType)

    if mc.getAttr(_combined,lock=True):
        _wasLocked = True
        mc.setAttr(_combined,lock=False)    

    #CONNECTED!!!
    if not is_keyed(_d):
        if break_connection(_d):
            log.warning("|{0}| >> broken connection: {1}".format(_str_func,_combined))    
    
    _children = get_children(_d)
    if _children:
        if len(_children) != len(value):
            raise ValueError,"Must have matching len for value and children. Children: {0} | value: {1}".format(_children,value)
        for i,c in enumerate(_children):
            mc.setAttr("{0}.{1}".format(_obj,c),value[i], **kws)
    elif _validType == 'long':
        mc.setAttr(_combined,int(float(value)), **kws)
    elif _validType == 'string':
        mc.setAttr(_combined,str(value),type = 'string', **kws)
    elif _validType == 'double':
        mc.setAttr(_combined,float(value), **kws)
    elif _validType == 'message':
        set_message(value, _obj, _attr)
        
    else:
        mc.setAttr(_combined,value, **kws)

    if _wasLocked or lock:
        mc.setAttr(_combined,lock=True)    

    return


def validate_attrTypeName(attrType):
    """"   
    Validates an attr type from various returns to something more consistant

    :parameters:
        attrType(string): - U

    :returns
        validatedType(string)
    """         
    for option in _d_attrTypes.keys():
        if attrType in _d_attrTypes.get(option): 
            return option
    raise ValueError,"Invalid type: {0}".format(attrType)

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

    return not mc.getAttr(_d['combined'],channelBox=True) 


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
        return mc.addAttr(_d['combined'],q=True, en = True) 
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
    _str_func = 'break_connection'
    _d = validate_arg(*a) 
    _combined = _d['combined']
    _obj = _d['obj']
    _attr = _d['attr']

    _drivenAttr = _combined

    family = {}
    source = []

    if (mc.connectionInfo (_combined,isDestination=True)):             
        sourceBuffer = mc.listConnections (_combined, scn = False, d = False, s = True, plugs = True)
        if not sourceBuffer:
            family = get_familyDict(_d)           
            sourceBuffer = mc.connectionInfo (_combined,sourceFromDestination=True)
        else:
            sourceBuffer = sourceBuffer[0]

        if not sourceBuffer:
            return log.warning("|{0}| >>No source for '{1}.{2}' found!".format(_str_func,obj,attr))
        log.debug("|{0}| >> sourcebuffer: {1}".format(_str_func,sourceBuffer))
        if family and family.get('parent'):
            log.debug("|{0}| >> family: {1}".format(_str_func,family))
            _drivenAttr = '{0}.{1}'.format(obj,family.get('parent'))

        log.debug("|{0}| >> breaking: {1} >>> to >>> {2}".format(_str_func,sourceBuffer,_drivenAttr))

        disconnect(sourceBuffer,_drivenAttr)

        return sourceBuffer
    
    if get_type(_d) == 'message':
        _dest = mc.listConnections (_combined, scn = False, d = True, s = False, plugs = True)
        if _dest:
            for c in _dest:
                disconnect(_drivenAttr,c)

    return False

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

def connect(fromAttr,toAttr,transferConnection=False,lock = False):
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
    
    log.info("|{0}| >> Connecting {1} to {2}".format(_str_func,_combined,_combined_to))

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
        mc.connectAttr(_combined,_combined_to)     

    if transferConnection:
        if _connection and not is_connected(_d):
            log.info("|{0}| >> {1} | Transferring to fromAttr: {2} | connnection: {3}".format(_str_func,toAttr,fromAttr,_connection))            
            mc.connectAttr(_connection,_combined)

    if _wasLocked or lock:
        mc.setAttr(_combined_to,lock=True)    


def OLDdoConnectAttr(fromAttr,toAttr,forceLock = False,transferConnection=False):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for setAttr which will unlock a locked node it's given
    to force a setting of the values. Also has a lock when done overide.
    In addition has transfer connections ability for buffer nodes.

    ARGUMENTS:
    attribute(string) - 'obj.attribute'
    value() - depends on the attribute type
    forceLock(bool) = False(default)
    transferConnection(bool) - (False) - whether you wante to transfer the existing connection to or not
                                        useful for buffer connections
    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert fromAttr != toAttr,"Cannot connect an attriubute to itself. The world might blow up!"

    wasLocked = False
    if (mc.objExists(toAttr)) == True:
        if mc.getAttr(toAttr,lock=True) == True:
            wasLocked = True
            mc.setAttr(toAttr,lock=False)
        bufferConnection = returnDriverAttribute(toAttr)
        attrBuffer = returnObjAttrSplit(toAttr)
        if not attrBuffer:
            return False
        doBreakConnection(attrBuffer[0],attrBuffer[1])
        mc.connectAttr(fromAttr,toAttr)     

    if transferConnection == True:
        if bufferConnection != False:
            mc.connectAttr(bufferConnection,toAttr)

    if wasLocked == True or forceLock == True:
        mc.setAttr(toAttr,lock=True)


def add(obj,attr=None,attrType=None, enumOptions = ['off','on'],*a, **kws):
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
        mc.addAttr (_node,ln = _attr, at = 'enum', en=('%s' %(':'.join(enumOptions))),*a, **kws)
        mc.setAttr ((_node+'.'+_attr),e=True,keyable=True)

    elif _type == 'bool':
        mc.addAttr (_node, ln = _attr,  at = 'bool',*a, **kws)
        mc.setAttr ((_node+'.'+_attr), edit = True, channelBox = True)
    elif _type == 'message':
        mc.addAttr (_node, ln = _attr, at = 'message',*a, **kws )
    else:
        raise ValueError,"Don't know what to do with attrType: {0}".format(attrType)
        #return False
    return _combined        

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

def get_numericFlagsDict(*a):
    """   
    Returns a diciontary of max,min,ranges,softs and default settings of an attribute

    :parameters:
        *a -- validate_arg

    :returns
        dict
    """ 
    _str_func = 'get_numericFlagsDict'
    _d = validate_arg(*a) 
    _combined = _d['combined']
    _obj = _d['obj']
    _attr = _d['attr']

    objAttrs = mc.listAttr(_obj, userDefined = True) or []

    dynamic = False
    if _attr in objAttrs:
        dynamic = True

    numeric = True
    attrType = mc.getAttr(_combined,type=True)    
    if attrType in ['string','message','enum','bool']:
        numeric = False

    dataDict = {}    
    # Return numeric data    
    if not numeric or not dynamic or mc.attributeQuery(_attr, node = _obj, listChildren=True):
        return {}
    else:
        dataDict['min'] = False                    
        if mc.attributeQuery(_attr, node = _obj, minExists=True):
            try:
                minValue =  mc.attributeQuery(_attr, node = _obj, minimum=True)
                if minValue is not False:
                    dataDict['min'] = minValue[0]
            except:
                dataDict['min'] = False
                log.warning("'%s.%s' failed to query min value" %(_obj,_attr))

        dataDict['max'] = False                
        if mc.attributeQuery(_attr, node = _obj, maxExists=True):
            try:
                maxValue =  mc.attributeQuery(_attr, node = _obj, maximum=True)
                if maxValue is not False:
                    dataDict['max']  = maxValue[0]                    
            except:
                dataDict['max']  = False
                log.warning("'%s.%s' failed to query max value" %(_obj,_attr))

        dataDict['default'] = False             
        if type(mc.addAttr(_combined,q=True,defaultValue = True)) is int or float:
            try:
                defaultValue = mc.attributeQuery(_attr, node = _obj, listDefault=True)
                if defaultValue is not False:
                    dataDict['default'] = defaultValue[0]  
            except:
                dataDict['default'] = False
                log.warning("'%s.%s' failed to query default value" %(_obj,_attr))

        #>>> Soft values
        dataDict['softMax']  = False
        try:
            softMaxValue =  mc.attributeQuery(_attr, node = _obj, softMax=True)
            if softMaxValue is not False:
                dataDict['softMax'] = softMaxValue[0]                  
        except:
            dataDict['softMax']  = False

        dataDict['softMin']  = False
        try:
            softMinValue =  mc.attributeQuery(_attr, node = _obj, softMin=True)
            if softMinValue is not False:
                dataDict['softMin']  = softMinValue[0]                  
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

    _longName = name_getLong(_d)
    #try:
    if name:
        mc.addAttr(_d['combined'],edit = True, niceName = name)
    elif name == False:
        mc.addAttr(_d['combined'],edit = True, niceName = _d['attr'])
    return get_nameNice(_d)    

def get_nameLong(*a):
    """   
    Get the long name of an attribute

    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        status(bool)
    """ 
    _str_func = 'name_getLong'
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
    if name is None:
        name = attr
        attr = None
        _d = validate_arg(obj) 
    else:
        _d = validate_arg(obj,attr) 

    _longName = name_getLong(_d)
    #try:
    if name:
        if name != _longName:
            attributes.doRenameAttr(_d['obj'],_longName,name)
            return True
        else:
            log.debug("|{0}| >> nice name is already: {1} | combined:{2}".format(_str_func,name,_d['combined']))
            return False
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
    if _d['attr'] in mc.listAttr(_d['obj'], userDefined = True):
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

def get_rangeSoft(*a):
    """   
    :parameters:
        *a(varied): - Uses validate_arg 

    :returns
        range(bool)
    """ 
    _str_func = 'get_rangeSoft'
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
        log.error("|{0}| >> {1} | {2}".format(_str_func,_d['combined'],err))
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
    
    if getNode:
        objectBuffer =  mc.listConnections (_combined, scn = skipConversionNodes, d = False, s = True, plugs = False)
        if not objectBuffer:
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
            return NAMES.get_long(objectBuffer[0])
        else:
            return NAMES.get_short(objectBuffer[0])      
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

def get_message(messageHolder, messageAttr = None, dataAttr = None, dataKey = None, simple = False):
    """   
    This is a speciality cgm setup using both message attributes and a cgmMessageData attriubute for storing extra data via json
    Get attributes driven by an attribute

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
        
    log.info("|{0}| >> {1} | dataAttr: {2} | dataKey: {3}".format(_str_func,_combined,_dataAttr,dataKey))
    
    _msgBuffer = mc.listConnections(_combined,destination=True,source=True)
    
    if _msgBuffer and mc.objectType(_msgBuffer[0])=='reference':
        #REPAIR
        _msgBuffer = mc.listConnections(_combined,destination=True,source=True)
        
    if mc.addAttr(_combined,q=True,m=True):
        log.debug("|{0}| >> multimessage...".format(_str_func))
        
        if _msgBuffer:
            return _msgBuffer
        return False
    else:
        log.debug("|{0}| >> single message...".format(_str_func))  
        
        if simple:
            return _msgBuffer
        
        _dataAttr = 'cgmMsgData'
        if dataAttr is not None:
            _dataAttr = dataAttr
    
        if '.' in _dataAttr or issubclass(type(_dataAttr),dict):
            _d_dataAttr = validate_arg(_dataAttr)            
        else:
            _d_dataAttr = validate_arg(messageHolder,_dataAttr)           
        
        _messagedNode = mc.listConnections (_combined,destination=True,source=True)
        if _messagedNode != None:
            if mc.objExists(_messagedNode[0]) and not mc.objectType(_messagedNode[0])=='reference':
                
                mi_node = r9Meta.MetaClass(_d['node'])
                if mi_node.hasAttr(_d_dataAttr['attr']):
                    _dBuffer = mi_node.__getattribute__(_d_dataAttr['attr']) or {}
                    if _dBuffer.get(dataKey):
                        log.debug("|{0}| >> extra message data found...".format(_str_func))  
                        return [ _messagedNode[0] + '.' + _dBuffer.get(dataKey)]
                
                return _messagedNode
            else:#Try to repair it
                return repairMessageToReferencedTarget(storageObject,messageAttr)
    return False    
    
def set_message(message, messageHolder, messageAttr, dataAttr = None, dataKey = None, simple = False):
    """   
    This is a speciality cgm setup using both message attributes and a cgmMessageData attriubute for storing extra data via json
    Get attributes driven by an attribute

    :parameters:
        message(str) -- may be object, attribute, or component 
        messageHolder(str) -- object to store to
        messageAttr(str) -- 
        dataAttr(str) -- Specify the attribute to check for extra data or use default(NONE)
            cgmMsgData is our default. Data is stored as a json dict of {attr:{msg:component or attr}}
        dataKey(str/int) -- data key for extra data. If None provided, attr name is used.
        simple(bool) -- Will only store dag nodes when specified

    :returns
        status(bool)
    """
    _str_func = 'set_message'    
    
    _d = validate_arg(messageHolder,messageAttr)
    _combined = _d['combined']

    #>> Validation -----------------------------------------------------------------------------------------------
    _mode = 'reg'
    _messagedNode = None
    _messagedExtra = None
    _d_dataAttr = None
    
        
    if issubclass(type(message),list):
        if len(message) > 1:
            raise ValueError,"Not implemented multi message"
        else:
            message = message[0]
            
    if message == False:
        break_connection(_d)
        return True
    elif '.' in message:
        if cgmValid.is_component(message):
            _l_msg = cgmValid.get_component(message)  
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
    else:
        _messagedNode = message
            
    _messageLong = NAMES.get_long(message)
    
    _dataAttr = 'cgmMsgData'
    if dataAttr is not None:
        _dataAttr = dataAttr
        
    if dataKey is None:
        dataKey = messageAttr
    else:
        dataKey = unicode(dataKey)
        
    log.info("|{0}| >> mode: {1} | dataAttr: {2} | dataKey: {3}".format(_str_func,_mode, _dataAttr,dataKey))
    log.info("|{0}| >> messageHolder: {1} | messageAttr: {2}".format(_str_func,messageHolder, messageAttr))
    log.info("|{0}| >> messagedNode: {1} | messagedExtra: {2} | messageLong: {3}".format(_str_func,_messagedNode, _messagedExtra, _messageLong))
    
    if _messagedExtra:
        if '.' in _dataAttr:
            _d_dataAttr = validate_arg(_dataAttr)            
        else:
            _d_dataAttr = validate_arg(messageHolder,_dataAttr)

    #>> Node store ------------------------------------------------------------------------------------------------------------
    def storeMsg(msgNode,msgExtra,holderDict,dataAttrDict=None, dataKey = None):
        connect((msgNode + ".message"),holderDict['combined'])
        if msgExtra:
            log.info("|{0}| >> '{1}.{2}' stored to: '{3}'".format(_str_func,msgNode,msgExtra, holderDict['combined']))
            
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
        
        log.info("|{0}| >> '{1}' stored to: '{2}'".format(_str_func,msgNode, _combined))        
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
                log.info("|{0}| >> message match. Good to go".format(_str_func))                            
                return True
            else:
                break_connection(_d)
                storeMsg(_messagedNode, _messagedExtra, _d, _d_dataAttr,dataKey)
            
        else:
            log.debug("|{0}| >> multimessage...".format(_str_func))  
            if _buffer and NAMES.get_long(_buffer[0]) == _messageLong:
                log.info("|{0}| >> message match. Good to go".format(_str_func))                            
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
        log.info("|{0}| >> new attr...".format(_str_func))                    
        add(messageHolder,messageAttr,'message',m=False)
        storeMsg(_messagedNode, _messagedExtra, _d, _d_dataAttr,dataKey)
        
    return True

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
        _data = get_enum(_d)
    else:
        _data = get(_d)
          
    delete(_d)
    
    #Rebuild -----------------------------------------------------------   
    
    if _attrType == 'enum':
        if _data:
            if cgmValid.stringArg(_data):
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
        
        
        try:set(_d,value = _data)
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
    
    


def OLDdoConvertAttrType(targetAttrName,attrType):
    """ 
    Keyword arguments:
    targetAttrName(string) -- name for an existing attribute name
    attrType(string) -- desired attribute type

    """    
    assert mc.objExists(targetAttrName) is True,"'%s' doesn't exist!"%targetAttrName

    aType = False
    for option in attrTypesDict.keys():
        if attrType in attrTypesDict.get(option): 
            aType = option
            break

    assert aType is not False,"'%s' is not a valid attribute type!"%attrType


    #>>> Get data
    targetLock = False
    if mc.getAttr((targetAttrName),lock = True) == True:
        targetLock = True
        mc.setAttr(targetAttrName,lock = False)

    targetType = mc.getAttr(targetAttrName,type=True)

    buffer = targetAttrName.split('.')
    targetObj = buffer[0]
    targetAttr = buffer[-1]


    #>>> Do the stuff
    if aType != targetType:
        # get data connection and data to transfer after we make our new attr
        # see if it's a message attribute to copy    
        connection = ''
        if mc.attributeQuery (targetAttr,node=targetObj,msg=True):
            dataBuffer = (returnMessageObject(targetObj,targetAttr))
        else:
            connection = returnDriverAttribute(targetAttrName)            
            dataBuffer = mc.getAttr(targetAttrName)

        if targetType == 'enum':           
            dataBuffer = mc.addAttr((targetObj+'.'+targetAttr),q=True, en = True)


        doDeleteAttr(targetObj,targetAttr)

        """if it doesn't exist, make it"""
        if aType == 'string':
            mc.addAttr (targetObj, ln = targetAttr,  dt = aType )

        elif aType == 'enum':
            enumStuff  = 'off:on'
            if dataBuffer:
                if type(dataBuffer) is str or type(dataBuffer) is unicode:
                    enumStuff = dataBuffer
            mc.addAttr (targetObj, ln = targetAttr, at=  'enum', en = enumStuff)

        elif aType == 'double3':
            mc.addAttr (targetObj, ln=targetAttr, at= 'double3')
            mc.addAttr (targetObj, ln=(targetAttr+'X'),p=targetAttr , at= 'double')
            mc.addAttr (targetObj, ln=(targetAttr+'Y'),p=targetAttr , at= 'double')
            mc.addAttr (targetObj, ln=(targetAttr+'Z'),p=targetAttr , at= 'double')
        else:
            mc.addAttr (targetObj, ln = targetAttr,  at = aType )

        if connection:
            try:
                doConnectAttr(connection,targetAttrName)
            except:
                log.warning("Couldn't connect '%s' to the '%s'"%(connection,targetAttrName))

        elif dataBuffer is not None:
            if mc.objExists(dataBuffer) and aType == 'message':
                storeObjectToMessage(dataBuffer,targetObj,targetAttr)
            else:
                try:
                    if aType == 'long':
                        mc.setAttr(targetAttrName,int(float(dataBuffer)))
                    elif aType == 'string':
                        mc.setAttr(targetAttrName,str(dataBuffer),type = aType)
                    elif aType == 'double':
                        mc.setAttr(targetAttrName,float(dataBuffer))   
                    else:
                        mc.setAttr(targetAttrName,dataBuffer,type = aType)
                except:
                    log.warning("Couldn't add '%s' to the '%s'"%(dataBuffer,targetAttrName))


        if targetLock:
            mc.setAttr(targetAttrName,lock = True)
            
def OLDreorderAttributes(obj,attrs,direction = 0):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Acknowledgement:
    Thank you to - http://www.the-area.com/forum/autodesk-maya/mel/how-can-we-reorder-an-attribute-in-the-channel-box/

    DESCRIPTION:
    Reorders attributes on an object

    ARGUMENTS:
    obj(string) - obj with message attrs
    attrs(list) must be attributes on the object
    direction(int) - 0 is is negative (up on the channelbox), 1 is positive (up on the channelbox)

    RETURNS:
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert direction in [0,1],"Direction must be 0 for negative, or 1 for positive movement"
    for attr in attrs:
        assert mc.objExists(obj+'.'+attr) is True, "reorderAttributes error. '%s.%s' doesn't exist. Swing and a miss..."%(obj,atr)

    userAttrs = mc.listAttr(obj,userDefined = True)

    attrsToMove = []
    for attr in userAttrs:
        if not mc.attributeQuery(attr, node = obj,listParent = True):
            attrsToMove.append(attr)

    lists.reorderListInPlace(attrsToMove,attrs,direction)

    #To reorder, we need delete and undo in the order we want
    for attr in attrsToMove:
        try:
            attrBuffer = '%s.%s'%(obj,attr)
            lockState = False
            if mc.getAttr(attrBuffer,lock=True) == True:
                lockState = True
                mc.setAttr(attrBuffer,lock=False)

            mc.deleteAttr('%s.%s'%(obj,attr))

            mc.undo()

            if lockState:
                mc.setAttr(attrBuffer,lock=True)

        except:
            log.warning("'%s' Failed to reorder"%attr)
            

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
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
    _l_user = mc.listAttr(node, userDefined=True)
    for a in _l_user:
        if '_' in a:
            _split = a.split('_')
            _int_ = _split[-1]
            _str_ = ('_').join(_split[:-1])
            if str(attr) == _str_:
                try:
                    _res[int(_int_)] = a
                except:
                    log.warning("|{0}| >> {1}.{2} failed to int. | int: {3}".format(_str_func,NAMES.get_short(node),a,_int_))     	               	
    return _res	


def msgList_exists(self,attr):
    """
    Fast check to see if we have data on this attr chain
    """
    try:
        #log.debug(">>> %s.msgList_exists(attr = '%s') >> "%(self.p_nameShort,attr) + "="*75)  
        d_attrs = self.get_sequentialAttrDict(attr)
        for i,k in enumerate(d_attrs.keys()):
            str_attr = d_attrs[i]
            if self.getMessage(d_attrs[i]):
                return True
        #log.debug("-"*100)            	               	
        return False   
    except StandardError,error:
        raise StandardError, "%s.msgList_exists >>[Error]<< : %s"(self.p_nameShort,error)

def msgList_connect(self, nodes, attr = None, connectBack = None):
    """
    Because multimessage data can't be counted on for important sequential connections we have
    implemented this.

    @param node: Maya node to connect to this mNode
    @param attr: Base name for the message attribute sequence. It WILL be appended with '_' as in 'attr_0'
    @param connectBack: attr name to connect back to self
    @param purge: Whether to purge before build

    """	
    _str_funcName = "%s.msgList_connect()"%self.p_nameShort  
    #log.debug(">>> %s.msgList_connect( attr = '%s', connectBack = '%s') >> "%(self.p_nameShort,attr,connectBack) + "="*75) 	    
    try:
        #ml_nodes = cgmValid.objStringList(nodes,noneValid=True)	    
        ml_nodes = validateObjListArg(nodes,noneValid=True)
        if ml_nodes:self.msgList_purge(attr)#purge first
        for i,mi_node in enumerate(ml_nodes):
            str_attr = "%s_%i"%(attr,i)
            try:attributes.storeObjectToMessage(mi_node.mNode,self.mNode,str_attr)
            except StandardError,error:log.error("%s >> i : %s | node: %s | attr : %s | connect back error: %s"%(_str_funcName,str(i),mi_node.p_nameShort,str_attr,error))
            if connectBack is not None:
                try:attributes.storeObjectToMessage(self.mNode,mi_node.mNode,connectBack)
                except StandardError,error:log.error("%s >> i : %s | node: %s | connectBack : %s | connect back error: %s"%(_str_funcName,str(i),mi_node.p_nameShort,connectBack,error))
            #log.debug("'%s.%s' <<--<< '%s.msg'"%(self.p_nameShort,str_attr,mi_node.p_nameShort))
        #log.debug("-"*100)            	
        return True
    except StandardError,error:
        raise StandardError, "%s.msgList_connect >>[Error]<< : %s"(self.p_nameShort,error)	

def msgList_get(self,attr = None, asMeta = True, cull = True):
    """
    @param attr: Base name for the message attribute sequence. It WILL be appended with '_' as in 'attr_0'
    @param asMeta: Returns a MetaClass object list
    @param cull: Whether to remove empty entries in the returned list
    """
    try:
        #log.debug(">>> %s.get_msgList(attr = '%s') >> "%(self.p_nameShort,attr) + "="*75)  
        d_attrs = self.get_sequentialAttrDict(attr)
        l_return = []
        ml_return = []
        for i,k in enumerate(d_attrs.keys()):
            str_msgBuffer = self.getMessage(d_attrs[i],False)
            if str_msgBuffer:str_msgBuffer = str_msgBuffer[0]

            l_return.append(str_msgBuffer)
            if asMeta:
                ml_return.append( validateObjArg(str_msgBuffer,noneValid=True) )
                #log.debug("index: %s | msg: '%s' | mNode: %s"%(i,str_msgBuffer,ml_return[i]))
            else:log.debug("index: %s | msg: '%s' "%(i,str_msgBuffer))

        if cull:
            l_return = [o for o in l_return if o]
            if asMeta: ml_return = [o for o in ml_return if o]

        #log.debug("-"*100)  
        if asMeta:return ml_return
        return l_return
    except StandardError,error:
        raise StandardError, "%s.get_msgList >>[Error]<< : %s"(self.p_nameShort,error)

def msgList_getMessage(self,attr = None, longNames = True, cull = True):
    """
    msgList equivalent to regular getMessage call
    @param attr: Base name for the message attribute sequence. It WILL be appended with '_' as in 'attr_0'
    @param longNames: Returns a MetaClass object list
    @param cull: Whether to remove empty entries in the returned list
    """
    try:
        #log.debug(">>> %s.msgList_getMessage(attr = '%s') >> "%(self.p_nameShort,attr) + "="*75)  
        d_attrs = self.get_sequentialAttrDict(attr)
        l_return = []
        for i,k in enumerate(d_attrs.keys()):
            str_msgBuffer = self.getMessage(d_attrs[i],longNames = longNames)
            if str_msgBuffer:str_msgBuffer = str_msgBuffer[0]
            l_return.append(str_msgBuffer)
            #log.debug("index: %s | msg: '%s' "%(i,str_msgBuffer))
        if cull:
            l_return = [o for o in l_return if o]
        #log.debug("-"*100)  
        return l_return
    except StandardError,error:
        raise StandardError, "%s.msgList_getMessage >>[Error]<< : %s"(self.p_nameShort,error)

def msgList_append(self, node, attr = None, connectBack = None):
    """
    Append node to msgList

    Returns index
    """
    #try:
    i_node = validateObjArg(node,noneValid=True)
    if not i_node:
        raise StandardError, " %s.msgList_append >> invalid node: %s"%(self.p_nameShort,node)
    #if not self.msgList_exists(attr):
        #raise StandardError, " %s.msgList_append >> invalid msgList attr: '%s'"%(self.p_nameShort,attr)		

    #log.debug(">>> %s.msgList_append(node = %s, attr = '%s') >> "%(self.p_nameShort,i_node.p_nameShort,attr) + "="*75)  

    ml_nodes = self.msgList_get(attr,asMeta=True)
    if i_node in ml_nodes:
        #log.debug(">>> %s.msgList_append >> Node already connected: %s "%(self.p_nameShort,i_node.p_nameShort) + "="*75) 
        idx = ml_nodes.index(i_node)	    
        return idx
    else:
        #log.debug("%s"%i_node.p_nameShort)
        ml_nodes.append(i_node)
        idx = ml_nodes.index(i_node)
        self.msgList_connect(ml_nodes,attr,connectBack)
        return idx
    #log.debug("-"*100)            	               	
    return True 

def msgList_index(self, node, attr = None):
    """
    Return the index of a node if it's in a msgList
    """
    i_node = validateObjArg(node,noneValid=True)
    if not i_node:
        raise StandardError, " %s.msgList_index >> invalid node: %s"%(self.p_nameShort,node)
    if not self.msgList_exists(attr):
        raise StandardError, " %s.msgList_index >> invalid msgList attr: '%s'"%(self.p_nameShort,attr)		
    #log.debug(">>> %s.msgList_index(node = %s, attr = '%s') >> "%(self.p_nameShort,i_node.p_nameShort,attr) + "="*75)  
    ml_nodes = self.msgList_get(attr,asMeta=True)	
    if i_node in ml_nodes:
        #log.debug(">>> %s.msgList_index >> Node already connected: %s "%(self.p_nameShort,i_node.p_nameShort) + "="*75)  		
        return ml_nodes.index(i_node)
    #log.debug("-"*100)            	               	
    return False

def msgList_remove(self, nodes, attr = None):
    """
    Return the index of a node if it's in a msgList
    """
    ml_nodesToRemove = validateObjListArg(nodes,noneValid=True)
    if not ml_nodesToRemove:
        raise StandardError, " %s.msgList_index >> invalid nodes: %s"%(self.p_nameShort,nodes)
    if not self.msgList_exists(attr):
        raise StandardError, " %s.msgList_append >> invalid msgList attr: '%s'"%(self.p_nameShort,attr)		
    #log.debug(">>> %s.msgList_remove(nodes = %s, attr = '%s') >> "%(self.p_nameShort,nodes,attr) + "="*75)  
    ml_nodes = self.msgList_get(attr,asMeta=True)
    b_removedSomething = False
    for i_n in ml_nodesToRemove:
        if i_n in ml_nodes:
            ml_nodes.remove(i_n)
            #log.debug(">>> %s.msgList_remove >> Node removed: %s "%(self.p_nameShort,i_n.p_nameShort) + "="*75)  				
            b_removedSomething = True
    if b_removedSomething:
        self.msgList_connect(ml_nodes,attr)
        return True	    
    #log.debug("-"*100)            	               	
    return False

def msgList_purge(self,attr):
    """
    Purge all the attributes of a msgList
    """
    try:
        #log.debug(">>> %s.get_msgList(attr = '%s') >> "%(self.p_nameShort,attr) + "="*75)  
        d_attrs = self.get_sequentialAttrDict(attr)
        for i,k in enumerate(d_attrs.keys()):
            str_attr = d_attrs[i]
            self.doRemove(str_attr)
            #log.debug("Removed: '%s'"%str_attr)

        #log.debug("-"*100)            	               	
        return True   
    except StandardError,error:
        raise StandardError, "%s.msgList_purge >>[Error]<< : %s"(self.p_nameShort,error)

def msgList_clean(self,attr,connectBack = None):
    """
    Removes empty entries and pushes back
    """
    try:
        #log.debug(">>> %s.msgList_clean(attr = '%s') >> "%(self.p_nameShort,attr) + "="*75)  
        l_attrs = self.msgList_get(attr,False,True)
        self.msgList_connect(l_attrs,attr,connectBack)
        #log.debug("-"*100)            	               	
        return True   
    except StandardError,error:
        raise StandardError, "%s.msgList_clean >>[Error]<< : %s"(self.p_nameShort,error)


def copy(fromObject, fromAttr, toObject = None, toAttr = None,
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
        connectTargetToSource(bool) --useful for moving attribute controls to another object. default False

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
        log.info("|{0}| >> No toObject specified. Using fromObject: {1}".format(_str_func,fromObject))
        _toObject = fromObject
    if _toAttr is None:
        log.info("|{0}| >> No toAttr specified. Using fromAttr: {1}".format(_str_func,fromAttr))
        _toAttr = fromAttr
    _d_targetAttr = validate_arg(_toObject,_toAttr)
    
    if _combined == _d_targetAttr['combined']:
        raise ValueError,"Cannot copy to self."
        
    
    #>>> Gather info --------------------------------------------------------------------------------------
    _d_sourceFlags = get_standardFlagsDict(_d)
    
    if values and not validate_attrTypeName(_d_sourceFlags['type']):
        log.warning("|{0}| >> {1} is a {2} attr and not valid for copying".format(_str_func,_d['combined'],_d_sourceFlags['type']))
        return False   

    cgmGeneral.log_info_dict(_d_sourceFlags,_combined)
    
    _driver = get_driver(_d,skipConversionNodes=True)
    _driven = get_driven(_d,skipConversionNodes=True)
    _data = get(_d)
    
    log.info("|{0}| >> data: {1}".format(_str_func,_data))    
    log.info("|{0}| >> driver: {1}".format(_str_func,_driver))
    log.info("|{0}| >> driven: {1}".format(_str_func,_driven))    
    
    #>>> First get our attribute ---------------------------------------------------------------------
    _goodToGo = True
    _targetExisted = False
    _relockSource = False    
    
    cgmGeneral.log_info_dict(_d_targetAttr)
    if mc.objExists(_d_targetAttr['combined']):
        _targetExisted = True
        _d_targetFlags = get_standardFlagsDict(_d_targetAttr)
        
        if not validate_attrTypeName(_d_targetFlags['type']):
            log.warning("|{0}| >> {1} may not copy correctly. Type did not validate.".format(_str_func,_d_targetAttr['combined']))
        
        if not validate_attrTypeMatch(_d_sourceFlags['type'],_d_targetFlags['type']):
            if _d_targetAttr['dynamic'] and convertToMatch:
                log.warning("|{0}| >> {1} Not the correct type, conversion necessary...".format(_str_func,_d_targetAttr['combined']))
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
   
    if _driver:
        if _d_sourceFlags['type'] != 'message':
            log.debug("|{0}| >> Driver: {1}".format(_str_func,_driver))
            try:connect(_driver,_d_targetAttr['combined'])
            except Exception,err:
                log.error("|{0}| >> Failed to connect {1} >--> {2} | err: {3}".format(_str_func,_driver,_d_targetAttr['combined'],err))        
                    
    if _driven:
        log.debug("|{0}| >> Driven: {1}".format(_str_func,_driven))
        for c in _driven:
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

#>>>>REFACTORING>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def OLDreturnCompatibleAttrs(sourceObj,sourceAttr,target,*a, **kw):
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




def OLDreturnAttributeDataDict(obj,attr,value = True,incoming = True, outGoing = True):
    """ 
    Returns a diciontary of parent,children,sibling of an attribute or False if nothing found   

    Keyword arguments:
    obj(string) -- must exist in scene
    attr(string) -- name for an attribute    
    """       
    assert mc.objExists("%s.%s"%(obj,attr)) is True,"'%s.%s' doesn't exist!"%(obj,attr)

    returnDict = {}
    if value:
        returnDict['value'] = doGetAttr(obj,attr)
    if incoming:
        returnDict['incoming'] = returnDriverAttribute('%s.%s'%(obj,attr),False)
    if outGoing:
        returnDict['outGoing'] = returnDrivenAttribute('%s.%s'%(obj,attr),False)

    return returnDict



def OLDreturnAttrListFromStringInput (stringInput1,stringInput2 = None):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Takes an list of string variables to add to an object as string
    attributes. Skips it if it exists.

    ARGUMENTS:
    stringInput(string/stringList)

    RETURNS:
    [obj,attr]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    if '.' in list(stringInput1):
        buffer = stringInput1.split('.')
        assert mc.objExists(buffer[0]) is True,"'%s' doesn't exsit"%buffer[0]
        assert len(buffer) == 2, "'%s' has too many .'s"%stringInput1
        obj = buffer [0]
        attr = buffer[1]
        return [obj,attr]
    elif len(stringInput1) == 2:
        assert mc.objExists(stringInput1[0]) is True,"'%s' doesn't exsit"%stringInput1[0]
        obj = stringInput1 [0]
        attr = stringInput1[1]
        return [obj,attr]
    elif stringInput2 !=None:
        assert mc.objExists(stringInput1) is True,"'%s' doesn't exsit"%stringInput1
        return [stringInput1,stringInput2]

    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Storing fuctions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDstoreInfo(obj,infoType,info,overideMessageCheck = False,leaveUnlocked = False):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Stores autoname stuff to an object where the variable name is the
    infoType and the info is the info stored
    -If info is object, it connects the attribute as a message to that object
    -If info is attribute, connected to attribute
    -Otherwise, stored as string

    ARGUMENTS:
    obj(string) - object to add our tag to
    infoType(string) - cgmName, cgmType, etc
    info(string) - info to store, object to connect to, attribute to connect to
    overideMessageCheck(bool) = default -False - whether to overide the objExists check

    RETURNS:
    True/False
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    typeDictionary = dictionary.initializeDictionary(typesDictionaryFile)
    namesDictionary = dictionary.initializeDictionary(namesDictionaryFile)
    settingsDictionary = dictionary.initializeDictionary(settingsDictionaryFile)
    attrTypes = returnObjectsAttributeTypes(obj)    
    goodToGo = False
    infoData = 0

    #Figure out the data type
    #==============      
    if type(info) is list:
        for o in info:
            if mc.objExists(o) and not overideMessageCheck:
                infoData = 'multiMessage'
                log.debug('Multi message mode!')
                break
    elif mc.objExists(info) and not overideMessageCheck and not '.' in list(info):#attribute check
        infoData = 'message'

    elif mc.objExists(info) and '.' in list(info):
        if '[' not in info:
            infoData = 'attribute'
        else:
            infoData = 'string'

    #Force leave  unlocked to be on in the case of referenced objects.
    if mc.referenceQuery(obj, isNodeReferenced=True):
        leaveUnlocked = True

    if infoType in settingsDictionary:
        infoTypeName = settingsDictionary.get(infoType)
        goodToGo = True
        # Checks to see if the type exists in the library
        if infoType == 'cgmType':
            if info in typeDictionary:
                goodToGo = True
            else:
                goodToGo = True
    else:
        infoTypeName = infoType
        goodToGo = True

    attributeBuffer = ('%s%s%s' % (obj,'.',infoTypeName))
    """ lock check """
    wasLocked = False
    if (mc.objExists(attributeBuffer)) == True:
        if mc.getAttr(attributeBuffer,lock=True) == True:
            wasLocked = True
            mc.setAttr(attributeBuffer,lock=False)

    if goodToGo == True:
        if infoData == 'message':
            storeObjectToMessage(info,obj,infoType)
            if leaveUnlocked != True:
                mc.setAttr(('%s%s%s' % (obj,'.',infoType)),lock=True)
        elif infoData == 'multiMessage':
            storeObjectsToMessage(info,obj,infoType)#Multi message!
        else:
            """ 
            if we get this far and it's a message node we're trying
            to store other data to we need to delete it
            """
            if mc.objExists(attributeBuffer) and mc.attributeQuery (infoTypeName,node=obj,msg=True):
                doDeleteAttr(obj,infoTypeName)
            """
            Make our new string attribute if it doesn't exist
            """
            if mc.objExists(attributeBuffer) == False:
                addStringAttributeToObj(obj,infoTypeName)
                if leaveUnlocked != True:
                    mc.setAttr(attributeBuffer,lock=True)
            """
            set the data
            """
            if infoData == 'attribute':
                infoAttrType = mc.getAttr(info,type=True)
                if mc.objExists(obj+'.'+infoType):
                    objAttrType = mc.getAttr((obj+'.'+infoType),type=True)
                    if infoAttrType != objAttrType:
                        doConvertAttrType((obj+'.'+infoType),infoAttrType)


                doConnectAttr(info,attributeBuffer)

                if leaveUnlocked != True:
                    mc.setAttr(attributeBuffer,lock=True)
            else:
                doSetStringAttr(attributeBuffer,info)
                if leaveUnlocked != True:
                    mc.setAttr(attributeBuffer,lock=True)
        return True
    else:
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Set/Copy/Delete Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    





def OLDdoMultiSetAttr(objList, attribute, value, forceLock = False, *a, **kw):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pushes doSetAttr to a list of objects

    ARGUMENTS:
    objList(list)
    attribute(string)
    value() - depends on the attribute type
    forceLock(bool) = False(default)

    RETURNS:
    Success
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    for obj in objList:
        attrBuffer = '%s.%s'%(obj,attribute)
        if (mc.objExists(attrBuffer)):
            doSetAttr(obj,attribute,value,forceLock,**kw)
        else:
            log.warning("'%s' doesn't exist! Skipping..."%attrBuffer)

def OLDsetAttrsFromDict(obj, attrs = None, pushToShapes = False):
    """
    Function for changing drawing override settings on on object

    Keyword arguments:
    attrs -- default will set all override attributes to default settings
    (dict) - pass a dict in and it will attempt to set the key to it's indexed value ('attr':1}
    (list) - if a name is provided and that attr is an override attr, it'll reset only that one
    """
    # First make sure the drawing override attributes exist on our instanced object
    log.info("THIS FUNCTION ISN'T DONE!")
    #Get what to act on
    targets = [obj]
    if pushToShapes:
        buffer = mc.listRelatives(self.mNode,shapes=True,fullPath=fullPath) or []
        if buffer:	
            targets.extend(buffer)

    for t in targets:
        if issubclass(attrs,dict):
            for a in attrs.keys():
                try:
                    attributes.doSetAttr(t,a,attrs[a])
                except Exception,error:
                    raise Exception, "There was a problem setting '%s.%s' to %s"%(obj,a,attrs[a])


def OLDdoSetStringAttr(attribute,value,forceLock = False):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for setAttr which will unlock a locked node it's given
    to force a setting of the values. Also has a lock when done overide

    ARGUMENTS:
    attribute(string) - 'obj.attribute'
    value() - depends on the attribute type
    forceLock(bool) = False(default)

    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    wasLocked = False
    if (mc.objExists(attribute)) == True:
        if mc.getAttr(attribute,lock=True) == True:
            wasLocked = True
            doBreakConnection(attribute)
            mc.setAttr(attribute,lock=False)
            mc.setAttr(attribute,value, type='string')
        else:
            doBreakConnection(attribute)
            mc.setAttr(attribute,value, type='string')

    if wasLocked == True or forceLock == True:
        mc.setAttr(attribute,lock=True)

def OLDdoRenameAttr(obj,oldAttrName,newAttrName,forceLock = False):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Replacement for setAttr which will unlock a locked node it's given
    to force a setting of the values. Also has a lock when done overide

    ARGUMENTS:
    attribute(string) - 'obj.attribute'
    value() - depends on the attribute type
    forceLock(bool) = False(default)

    RETURNS:
    nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    wasLocked = False
    combinedBuffer = '%s.%s'%(obj,oldAttrName)
    if (mc.objExists(combinedBuffer)) == True:
        if mc.getAttr(combinedBuffer,lock=True) == True:
            wasLocked = True
            mc.setAttr(combinedBuffer,lock=False)
            mc.renameAttr(combinedBuffer,newAttrName)
        else:
            mc.renameAttr(combinedBuffer,newAttrName)

    if wasLocked == True or forceLock == True:
        newBuffer = '%s.%s'%(obj,newAttrName)
        mc.setAttr(newBuffer,lock=True)

def OLDreturnMatchNameAttrsDict(fromObject,toObject,attributes=[True],directMatchOnly = False,*a, **kw ):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tries to find match attrs regardless of name alias or what not in dict form.

    ARGUMENTS:
    fromObject(string) - obj with attrs
    toObject(string) - obj to check
    attrsToCopy(list) - list of attr names to copy, if [True] is used, it will do all of them
    directMatchOnly(bool) =- whether to check longNames (ignores alias'). Default is the wider search (False)

    If attriubtes is set to default ([True]), you can pass keywords and arguments into a listAttr call for the 
    search parameters


    RETURNS:
    matchAttrs(dict) = {sourceAttr:targetAttr, }
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    matchAttrs = {}
    if attributes[0] is True:
        attributes = mc.listAttr(fromObject, *a, **kw) or []

    if attributes:
        for attr in attributes:
            if mc.objExists('%s.%s'%(fromObject, attr) ):
                if directMatchOnly:
                    if mc.objExists('%s.%s'%(toObject, attr) ):
                        matchAttrs[attr] = attr                        
                else:
                    try:
                        buffer = mc.attributeQuery(attr,node=fromObject,longName=True) or ''                    
                        if mc.objExists('%s.%s'%(toObject, buffer) ):
                            matchAttrs[attr] = buffer
                    except:
                        log.warning("'%s' failed to query a long name to check"%attr)
        if matchAttrs:
            return matchAttrs
        else:
            return False
    return False


def OLDcopyKeyableAttrs(fromObject,toObject,attrsToCopy=[True],connectAttrs = False):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copy attributes from one object to another. If the attribute already
    exists, it'll copy the values. If it doesn't, it'll make it.

    ARGUMENTS:
    fromObject(string) - obj with attrs
    toObject(string) - obj to copy to
    attrsToCopy(list) - list of attr names to copy, if [True] is used, it will do all of them

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrDict = {}
    keyableAttrs =(mc.listAttr (fromObject, keyable=True))
    matchAttrs = []
    lockAttrs = {}
    if keyableAttrs == None:
        return False
    else:
        if attrsToCopy[0] == 1:
            matchAttrs = keyableAttrs
        else:
            for attr in attrsToCopy:
                if attr in keyableAttrs:
                    matchAttrs.append(attr)
    """ Get the attribute types of those the source object"""
    attrTypes = returnObjectsAttributeTypes(fromObject)

    print ('The following attrirbues will be created and copied')
    print matchAttrs
    #>>> The creation of attributes part
    if len(matchAttrs)>0:
        for attr in matchAttrs:
            """ see if it was locked, unlock it and store that it was locked """
            if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
                lockAttrs[attr] = True
                mc.setAttr((fromObject+'.'+attr),lock=False)
            """if it doesn't exist, make it"""
            if mc.objExists(toObject+'.'+attr) is not True:
                attrType = (attrTypes.get(attr))

                if attrType == 'string':
                    mc.addAttr (toObject, ln = attr,  dt =attrType )
                elif attrType == 'enum':
                    enumStuff = mc.attributeQuery(attr, node=fromObject, listEnum=True)
                    mc.addAttr (toObject, ln=attr, at= 'enum', en=enumStuff[0])
                elif attrType == 'double3':
                    mc.addAttr (toObject, ln=attr, at= 'double3')
                    mc.addAttr (toObject, ln=(attr+'X'),p=attr , at= 'double')
                    mc.addAttr (toObject, ln=(attr+'Y'),p=attr , at= 'double')
                    mc.addAttr (toObject, ln=(attr+'Z'),p=attr , at= 'double')
                else:
                    mc.addAttr (toObject, ln = attr,  at =attrType )
        """ copy values """
        mc.copyAttr(fromObject,toObject,attribute=matchAttrs,v=True,ic=True)

        """ relock """
        for attr in lockAttrs.keys():
            mc.setAttr((fromObject+'.'+attr),lock=True)
            mc.setAttr((toObject+'.'+attr),lock=True)


        """ Make it keyable """    
        for attr in matchAttrs:
            mc.setAttr((toObject+'.'+attr),keyable=True)

        if connectAttrs:
            for attr in matchAttrs:
                doConnectAttr((toObject+'.'+attr),(fromObject+'.'+attr))

        return True

    else:
        return False


def OLDcopyUserAttrs(fromObject,toObject,attrsToCopy=[True]):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copy attributes from one object to another. If the attribute already
    exists, it'll copy the values. If it doesn't, it'll make it.

    ARGUMENTS:
    fromObject(string) - obj with attrs
    toObject(string) - obj to copy to
    attrsToCopy(list) - list of attr names to copy, if [True] is used, it will do all of them

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrDict = {}
    userAttrs =(mc.listAttr (fromObject, userDefined=True))
    matchAttrs = []
    lockAttrs = {}
    if userAttrs == None:
        return False
    else:
        if attrsToCopy[0] == 1:
            matchAttrs = userAttrs
        else:
            for attr in attrsToCopy:
                if attr in userAttrs:
                    matchAttrs.append(attr)
    """ Get the attribute types of those the source object"""
    attrTypes = returnObjectsAttributeTypes(fromObject)

    #>>> The creation of attributes part
    messageAttrs = {}
    if len(matchAttrs)>0:
        for attr in matchAttrs:
            # see if it's a message attribute to copy  
            if mc.attributeQuery (attr,node=fromObject,msg=True):
                messageAttrs[attr] = (returnMessageObject(fromObject,attr))

            """ see if it was locked, unlock it and store that it was locked """
            if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
                lockAttrs[attr] = True
                mc.setAttr((fromObject+'.'+attr),lock=False)

            """if it doesn't exist, make it"""
            if mc.objExists(toObject+'.'+attr) is not True:
                attrType = (attrTypes.get(attr))
                if attrType == 'string':
                    mc.addAttr (toObject, ln = attr,  dt =attrType )
                elif attrType == 'enum':
                    enumStuff = mc.attributeQuery(attr, node=fromObject, listEnum=True)
                    mc.addAttr (toObject, ln=attr, at= 'enum', en=enumStuff[0])
                elif attrType == 'double3':
                    mc.addAttr (toObject, ln=attr, at= 'double3')
                    mc.addAttr (toObject, ln=(attr+'X'),p=attr , at= 'double')
                    mc.addAttr (toObject, ln=(attr+'Y'),p=attr , at= 'double')
                    mc.addAttr (toObject, ln=(attr+'Z'),p=attr , at= 'double')
                else:
                    mc.addAttr (toObject, ln = attr,  at =attrType )
        """ copy values """
        mc.copyAttr(fromObject,toObject,attribute=matchAttrs,v=True,ic=True,oc=True,keepSourceConnections=True)

        if messageAttrs:
            for a in messageAttrs.keys():
                storeInfo(toObject,a,messageAttrs.get(a))

        """ relock """
        for attr in lockAttrs.keys():
            mc.setAttr((fromObject+'.'+attr),lock=True)
            mc.setAttr((toObject+'.'+attr),lock=True)
        return True
    else:
        return False

def OLDcopyNameTagAttrs(fromObject,toObject):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Copy cgmTag attrs from one object to another. 

    ARGUMENTS:
    fromObject(string) - obj with attrs
    toObject(string) - obj to copy to

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    lockAttrs = {}
    attrsToCopy = ['cgmName','cgmType','cgmDirection','cgmPosition','cgmNameModifier','cgmTypeModifier','cgmDirectionModifier']
    tagsDict = returnUserAttrsToDict(fromObject)

    #>>> The creation of attributes part
    if len(tagsDict.keys())>0:
        for attr in tagsDict.keys():

            """if it doesn't exist, store  it"""
            if mc.objExists(fromObject+'.'+attr) and attr in attrsToCopy:
                """ see if it was locked, unlock it and store that it was locked """  
                if mc.getAttr((fromObject+'.'+attr),lock=True) == True:
                    lockAttrs[attr] = True

                storeInfo(toObject,attr,tagsDict.get(attr))


        """ relock """
        for attr in lockAttrs.keys():
            mc.setAttr((fromObject+'.'+attr),lock=True)
            mc.setAttr((toObject+'.'+attr),lock=True)
        return True
    else:
        return False

def OLDswapNameTagAttrs(object1,object2):
    """                                     
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Swap cgmNameTag attrs from one object to another. 

    ARGUMENTS:
    fromObject(string) - 
    toObject(string) - 

    RETURNS:
    None
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    object1LockAttrs = {}
    object2LockAttrs = {}

    attrsToCopy = ['cgmName','cgmType','cgmDirection','cgmPosition','cgmNameModifier','cgmTypeModifier','cgmDirectionModifier']
    object1TagsDict = returnUserAttrsToDict(object1)
    object2TagsDict = returnUserAttrsToDict(object2)

    object1TagTypesDict = returnObjectsAttributeTypes(object1,userDefined = True)
    object2TagTypesDict = returnObjectsAttributeTypes(object2,userDefined = True)

    #>>> execution stuff
    if object1TagsDict and object2TagsDict:
        #>>> Object 1
        for attr in object1TagsDict.keys():
            """if it doesn't exist, store  it"""
            if mc.objExists(object1+'.'+attr) and attr in attrsToCopy:
                """ see if it was locked, unlock it and store that it was locked """  
                if mc.getAttr((object1+'.'+attr),lock=True) == True:
                    object1LockAttrs[attr] = True

                doDeleteAttr(object1,attr) 
        #Copy object 2's tags to object 1            
        for attr in object2TagsDict.keys():
            if object2TagTypesDict.get(attr) == 'message':
                storeInfo(object1,attr,object2TagsDict.get(attr))
            else:
                storeInfo(object1,attr,object2TagsDict.get(attr),True)

        #>>> Object 2
        for attr in object2TagsDict.keys():
            """if it doesn't exist, store  it"""
            if mc.objExists(object2+'.'+attr) and attr in attrsToCopy:
                """ see if it was locked, unlock it and store that it was locked """  
                if mc.getAttr((object2+'.'+attr),lock=True) == True:
                    object2LockAttrs[attr] = True

                doDeleteAttr(object2,attr) 

        #Copy object 1's tags to object 2                      
        for attr in object1TagsDict.keys():
            if object1TagTypesDict.get(attr) == 'message':
                storeInfo(object2,attr,object1TagsDict.get(attr))
            else:
                storeInfo(object2,attr,object1TagsDict.get(attr),True)

    else:
        log.warning("Selected objects don't have cgmTags to swap")





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

def OLDdoToggleTemplateDisplayMode(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Toggles the template disply mode of an object

    ARGUMENTS:
    obj(string) - the object we'd like to startfrom

    RETURNS:
    Nothin
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    shapes = mc.listRelatives(obj,shapes = True)  

    if shapes > 0:
        for shape in shapes:
            currentState = doGetAttr(shape,'template')
            doSetAttr(shape, 'template', not currentState)

    else:
        currentState = doGetAttr(obj,'template')
        doSetAttr(obj,'template', not currentState)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDdoDeleteAttr(obj,attr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Deletes and attribute if it exists. Even if it's locked

    ARGUMENTS:
    attr(string) - the attribute to delete

    RETURNS:
    True/False depending if it found anything to destroy
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrBuffer = (obj+'.'+attr)
    if mc.objExists(attrBuffer) and not mc.attributeQuery(attr, node = obj, listParent=True):
        try:
            mc.setAttr(attrBuffer,lock=False)
        except:pass            
        try:
            doBreakConnection(attrBuffer)
        except:pass

        mc.deleteAttr(attrBuffer)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Joint Related
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDsetRotationOrderObj (obj, ro):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object and rotation order (xyz,xzy,etc) into it and it will
    set the object to that rotation order

    ARGUMENTS:
    obj(string) - object
    ro(string) - rotation order 
                            xyz,yzx,zxy,xzy,yxz,zyx,none

    RETURNS:
    success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ pass an object and rotation order (xyz,xzy,etc) into it and it will set the object to that rotation order """
    validRO = True
    rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}
    if not ro in rotationOrderDictionary:
        print (ro + ' is not a valid rotation order. Expected one of the following:')
        print rotationOrderDictionary
        validRO = False
    else:  
        correctRo = rotationOrderDictionary[ro]        
        mc.setAttr ((obj+'.rotateOrder'), correctRo)
    return validRO
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Utility Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def OLDdoSetLockHideKeyableAttr (obj,lock=True,visible=False,keyable=False,channels=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an oject, True/False for locking it, True/False for visible in
    channel box, and which channels you want locked in ('tx','ty',etc) form

    ARGUMENTS:
    obj(string)
    lock(bool)
    visible(bool)
    keyable(bool)
    channels(list) - (tx,ty,vis,whatever)

    RETURNS:
    None
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    lockOptions = ('tx','ty','tz','rx','ry','rz','sx','sy','sz','v')
    for channel in channels:
        if channel in lockOptions:        
            mc.setAttr ((obj+'.'+channel),lock=lock, keyable=keyable, channelBox=visible)                   
        else:
            print (channel + ' is not a valid option. Skipping.')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Connections Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>




#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Search Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDreturnObjectsAttributeTypes(obj,*a, **kw ):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with user attributes and it will return a dictionary attribute's data types

    ARGUMENTS:
    obj(string) - obj with attrs
    any arguments for the mc.listAttr command

    RETURNS:
    attrDict(Dictionary) - dictionary in terms of {[attrName : type],[etc][etc]}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj) is True, "'%s' doesn't exist"%obj
    attrs =(mc.listAttr (obj,*a, **kw ))
    attrDict = {}
    if not attrs == None:   
        for attr in attrs:
            try:
                attrDict[attr] = (mc.getAttr((obj+'.'+attr),type=True))
            except:
                pass
        return attrDict
    else:
        return False

def OLDreturnObjectsAttributeByTypeDict(obj,typeCheck = [],*a, **kw ):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with  it will return a dictionary of attribute names by type keys

    ARGUMENTS:
    obj(string) - obj with attrs
    typeCheck(list) == list of attribute types to look for. default [] will query all
    any arguments for the mc.listAttr command

    RETURNS:
    attrDict(Dictionary) - dictionary in terms of {[type : attr1,attr2],[etc][etc]}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj) is True, "'%s' doesn't exist"%obj

    attrs =(mc.listAttr (obj,*a, **kw ))
    typeDict = {}    
    if typeCheck:
        for check in typeCheck:
            typeDict[check] = []

    if not attrs == None:   
        for attr in attrs:
            try:               
                typeBuffer = mc.getAttr((obj+'.'+attr),type=True) or None
                if typeCheck:
                    if typeBuffer and typeBuffer in typeDict.keys():
                        typeDict[typeBuffer].append(attr)
                else:
                    if typeBuffer and typeBuffer in typeDict.keys():
                        typeDict[typeBuffer].append(attr)
                    elif typeBuffer:
                        typeDict[typeBuffer] = [attr]                    
            except:
                pass
    if typeDict: 
        for key in typeDict.keys():
            if typeDict.get(key):
                return typeDict
    return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDreturnUserAttributes(obj,*a,**kw):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns user created attributes of an object

    ARGUMENTS:
    obj(string) - obj to check

    RETURNS:
    messageList - nested list in terms of [[attrName, target],[etc][etc]]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    buffer = mc.listAttr(obj,ud=True)
    if buffer > 0:
        return buffer
    else:
        return False



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDreturnObjAttrSplit(attr):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Simple attribute string splitter

    ARGUMENTS:
    attr(string) - obj with message attrs

    RETURNS:
    returnBuffer(list) -- [obj,attr]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(attr) is True,"'%s' doesn't exist!"
    returnBuffer = []

    if '.' in list(attr):
        splitBuffer = attr.split('.')
        if splitBuffer >= 2:
            returnBuffer = [splitBuffer[0],'.'.join(splitBuffer[1:])]

        if returnBuffer:
            return returnBuffer
    return False  

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDreturnMessageAttrs(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with messages, it will return a nested list in terms of [[attrName, target],[etc][etc]]

    ARGUMENTS:
    obj(string) - obj with message attrs

    RETURNS:
    messageList(Dictionary) - dictionary in terms of {[attrName : target],[etc][etc]}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    messageList = {}
    objAttributes =(mc.listAttr (obj, userDefined=True))
    if not objAttributes == None:
        for attr in objAttributes:                    
            messageBuffer = []
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            if messageQuery == True:
                query = (mc.listConnections(obj+'.'+attr))
                if not query == None:
                    messageList[attr] = (query[0])
        return messageList
    else:
        return False
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
    log.info("Reference connection found, attempting to fix...")

    messageConnectionsOut =  mc.listConnections("%s.message"%(obj), p=1)
    if messageConnectionsOut and ref:
        for plug in messageConnectionsOut:
            if ref in plug:
                log.info("Checking '%s'"%plug)                
                matchObj = plug.split('.')[0]#Just get to the object
                doConnectAttr("%s.message"%matchObj,targetAttr)
                log.info("'%s' restored to '%s'"%(targetAttr,matchObj))

                if len(messageConnectionsOut)>1:#fix to first, report other possibles
                    log.warning("Found more than one possible connection. Candidates are:'%s'"%"','".join(messageConnectionsOut))
                    return False
                return matchObj
    log.warning("No message connections and reference found")
    return False

def OLDreturnMessageAttrsAsList(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with messages, it will return a nested list in terms of [[attrName, target],[etc][etc]]

    ARGUMENTS:
    obj(string) - obj with message attrs

    RETURNS:
    messageList - nested list in terms of [[attrName, target],[etc][etc]]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    messageList = []
    objAttributes =(mc.listAttr (obj, userDefined=True))
    if not objAttributes == None:
        for attr in objAttributes:                    
            messageBuffer = []
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            if messageQuery == True:
                query = (mc.listConnections(obj+'.'+attr))
                if not query == None:
                    messageBuffer.append (attr)
                    messageBuffer.append (query[0])
                    messageList.append (messageBuffer)
        return messageList
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDreturnUserAttrsToDict(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with user attributes and it will return a dictionary of the data back

    ARGUMENTS:
    obj(string) - obj with attrs

    RETURNS:
    attrDict(Dictionary) - dictionary in terms of {[attrName : target],[etc][etc]}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrDict = {}
    objAttributes =(mc.listAttr (obj, userDefined=True)) or []
    attrTypes = returnObjectsAttributeTypes(obj,userDefined = True)

    if objAttributes:
        for attr in objAttributes:                    
            messageBuffer = []
            messageQuery = (mc.attributeQuery (attr,node=obj,msg=True))
            attrType = attrTypes.get(attr)
            if messageQuery == True:
                query = returnMessageData(obj,attr)
                attrDict[attr] = (query)
            elif attrType == 'double3':
                childrenAttrs = mc.attributeQuery(attr, node =obj, listChildren = True)
                dataBuffer = []
                for childAttr in childrenAttrs:
                    dataBuffer.append(mc.getAttr(obj+'.'+childAttr))
                attrDict[attr] = dataBuffer
            elif attrType == 'double':
                parentAttr = mc.attributeQuery(attr, node =obj, listParent = True)
                if parentAttr:
                    if parentAttr[0] not in objAttributes:
                        attrDict[attr] = (mc.getAttr((obj+'.'+attr)))
                    else:
                        attrDict[attr] = (mc.getAttr((obj+'.'+attr)))                    
                else:
                    attrDict[attr] = (mc.getAttr((obj+'.'+attr)))                    
            else:
                if attrType != 'attributeAlias':
                    buffer = mc.getAttr(obj+'.'+attr)
                    if buffer is not None:
                        attrDict[attr] = (buffer)

        return attrDict
    else:
        return False
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDreturnUserAttrsToList(obj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object into it with user attributes and it will return a dictionary of the data back

    ARGUMENTS:
    obj(string) - obj with attrs

    RETURNS:
    attrsList(list) - nested list in terms of [[attrName : target],[etc][etc]]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnList = []
    bufferDict = returnUserAttrsToDict(obj)
    if bufferDict:
        for key in bufferDict.keys():
            buffer = []
            buffer.append(key)
            buffer.append(bufferDict.get(key))
            returnList.append(buffer)
        return returnList
    return False


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Creation Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDaddRotateOrderAttr (obj,name):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Add a rotate order attr

    ARGUMENTS:
    obj(string) - object to add attributes to
    attrList(list) - list of attributes to add

    RETURNS:
    NA
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    try:
        mc.addAttr(obj, ln=name, at = 'enum',en = 'xyz:yzx:zxy:xzy:yxz:zyx')
        mc.setAttr((obj+'.'+name),e = True, keyable = True )
        return ("%s.%s"%(obj,name))
    except StandardError,error:
        log.error("addRotateOrderAttr>>Failure! '%s' failed to add '%s'"%(obj,name))
        raise StandardError,error       

def OLDaddPickAxisAttr(obj,name):
    """ 
    Add an axis picker attr

    ARGUMENTS:
    obj(string) - object to add attributes to
    name(string) - name of the attr to make
    """
    try:
        mc.addAttr(obj, ln=name, at = 'enum',en = 'x+:y+:z+:x-:y-:z-')
        mc.setAttr((obj+'.'+name),e = True, keyable = True )
        return ("%s.%s"%(obj,name))
    except:
        log.warning("'%s' failed to add '%s'"%(obj,name))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Message Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def OLDstoreObjNameToMessage (obj, storageObj):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds the obj name as a message attribute to the storage object

    ARGUMENTS:
    obj(string) - object to store
    storageObject(string) - object to store the info to

    RETURNS:
    Nothing
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    attrCache = ('%s%s%s' % (storageObj,'.',obj))
    if  mc.objExists (attrCache):  
        print (attrCache+' already exists')
    else:
        mc.addAttr (storageObj, ln=obj, at= 'message')
        mc.connectAttr ((obj+".message"),(storageObj+'.'+ obj))

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def OLDstoreObjectToMessage (obj, storageObj, messageName):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Adds the obj name as a message attribute to the storage object with
    a custom message attribute name

    ARGUMENTS:
    obj(string) - object to store
    storageObject(string) - object to store the info to
    messageName(string) - message name to store it as

    RETURNS:
    Success
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    assert mc.objExists(obj) is True,"'%s' doesn't exist"%(obj)
    assert mc.objExists(storageObj) is True,"'%s' doesn't exist"%(storageObj)

    attrCache = (storageObj+'.'+messageName)
    objLong = mc.ls(obj,long=True)
    if len(objLong)>1:
        log.warning("Can't find long name for storage, found '%s'"%objLong)
        return False 
    objLong = objLong[0]

    storageLong = mc.ls(storageObj,long=True)
    if len(storageLong)>1:
        log.warning("Can't find long name for storage, found '%s'"%storageLong)
        return False
    storageLong = storageLong[0]

    try:
        if  mc.objExists (attrCache):
            if mc.attributeQuery (messageName,node=storageObj,msg=True) and not mc.addAttr(attrCache,q=True,m=True):
                if returnMessageObject(storageObj,messageName) != obj:
                    log.debug(attrCache+' already exists. Adding to existing message node.')
                    doBreakConnection(attrCache)
                    #mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),force=True)
                    doConnectAttr((obj+".message"),(storageObj+'.'+ messageName))
                    return True 
                else:
                    log.debug("'%s' already stored to '%s.%s'"%(obj,storageObj,messageName))
            else:
                connections = returnDrivenAttribute(attrCache)
                if connections:
                    for c in connections:
                        doBreakConnection(c)

                log.debug("'%s' already exists. Not a message attr, converting."%attrCache)
                doDeleteAttr(storageObj,messageName)

                buffer = mc.addAttr (storageObj, ln=messageName, at= 'message')                
                #mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName),force=True)
                doConnectAttr((obj+".message"),(storageObj+'.'+ messageName))                

                return True
        else:
            mc.addAttr (storageObj, ln=messageName, at= 'message')
            #mc.connectAttr ((obj+".message"),(storageObj+'.'+ messageName))
            doConnectAttr((obj+".message"),(storageObj+'.'+ messageName))	    
            return True
    except StandardError,error:
        log.warning(error)
        return False








