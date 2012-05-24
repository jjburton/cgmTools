"""
    Resetter
    
    Copyright (c) 2010 Bohdon Sayre
    All Rights Reserved.
    bohdon@gmail.com
    
    Description:
        This script allows you to setup controls for easy resetting,
        it stores the default values of any keyable attribute, and allows
        you to reset those attributes with a button or command
    
    Instructions:
        To run the script's gui, use:
            import boResetter
            boResetter.GUI()
        To use the script in other tools:
            >>> import boResetter
            >>> boResetter.setDefaults() # store selected node's keyable attributes as defaults
            >>> boResetter.listDefaults()
            >>> boResetter.reset() # reset selected node's attributes
    
    Version 2.2.0:
        > Much better usage within other toolsets
        > Reorganizing and simplifying overall implementation
    Version 2.1.2:
        > Rewrote main resetting method to use python evals, instead of using mel
        > Rewritten in python
        > Added channel box functionality - Set or reset the selected cb attributes using resetSmart or setDefaultsCBSelection
        > Referencing and renaming now functional because the object name is not stored
        > Smart and Xform modes added
        > Popup menus to add each function to the current shelf
        > Includes listing, resetting, and removing of defaults
        > Adds a default string to selected objects for restoring attributes
    
    Feel free to email me with any bugs, comments, or requests!
"""

import pymel.core as pm

__version__ = '2.2.0'

DEFAULTS_ATTR = 'brstDefaults'


class GUI(object):
    def __init__(self):
        self.winName = 'boResetterWin'
        #define colors
        self.colSet = [0.3, 0.36, 0.49]
        self.colRemove = [0.49, 0.3, 0.3]
        self.colReset = [0.2, 0.2, 0.2]
        self.colReset2 = [0.25, 0.25, 0.25]
        self.build()
    
    def build(self):
        #check for pre-existing window
        if pm.window(self.winName, ex=True):
            pm.deleteUI(self.winName, wnd=True)
        
        if not pm.windowPref(self.winName, ex=True):
            pm.windowPref(self.winName, tlc=(200, 200))
        pm.windowPref(self.winName, e=True, w=280, h=100)
        
        with pm.window(self.winName, rtf=1, mb=1, tlb=True, t='Resetter %s' % __version__) as self.win:
            imenu = pm.menu(l='Info')
            pm.setParent(imenu, m=True)
            pm.menuItem(l='List Objects with Defaults', c=pm.Callback(listObjectsWithDefaults))
            pm.menuItem(l='Select Objects with Defaults', c=pm.Callback(selectObjectsWithDefaults))
            pm.menuItem(l='List Defaults', c=pm.Callback(listDefaults))
            
            with pm.formLayout(nd=100) as form:
                
                with pm.frameLayout(l='Set/Remove Defaults', bs='out', mw=2, mh=2, cll=True, cl=True) as setFrame:
                    with pm.columnLayout(rs=2, adj=True):
                        pm.button(l='Set Defaults', c=pm.Callback(setDefaults), bgc=self.colSet, ann='Set defaults on the selected objects using all keyable attributes')
                        pm.button(l='Set Defaults Include Non-Keyable', c=pm.Callback(setDefaultsNonkeyable), bgc=self.colSet, ann='Set defaults on the selected objects using keyable and non-keyable attributes in the channel box')
                        pm.button(l='Set Defaults with CB Selection', c=pm.Callback(setDefaultsCBSelection), bgc=self.colSet, ann='Set defaults on the selected objects using the selected channel box attributes')
                        pm.button(l='Remove Defaults', c=pm.Callback(removeDefaults), bgc=self.colRemove, ann='Remove all defaults from the selected objects')
                        pm.button(l='Remove from All Objects', c=pm.Callback(removeAllDefaults), bgc=self.colRemove, ann='Remove defaults from all objects in the scene')
                
                with pm.frameLayout(l='Reset', bs='out', mw=2, mh=2) as resetFrame:
                    with pm.formLayout(nd=100) as resetForm:
                        b6 = pm.button(l='Smart', c=pm.Callback(resetSmart), bgc=self.colReset, ann='Reset the selected objects. Uses transform standards if no defaults are defined for translate, rotate, and scale')
                        b7 = pm.button(l='Default', c=pm.Callback(reset), bgc=self.colReset, ann='Reset the selected objects using only stored defaults, if any')
                        b8 = pm.button(l='Transform', c=pm.Callback(resetTransform), bgc=self.colReset, ann='Reset the selected objects using only transform standards for translate, rotate, scale (eg. 0, 0, 1)')
                        b9 = pm.button(l='All', c=pm.Callback(resetAll), bgc=self.colReset2, ann='Reset all objects in the scene with defaults')
                        pm.formLayout(resetForm, e=True,
                            ap=[(b6, 'left', 0, 0), (b6, 'right', 2, 25),
                                (b7, 'left', 2, 25), (b7, 'right', 2, 50),
                                 (b8, 'left', 2, 50), (b8, 'right', 2, 75),
                                  (b9, 'left', 2, 75), (b9, 'right', 2, 100), ])
                
                mw = 4
                pm.formLayout(form, e=True,
                    af=[(setFrame, 'left', mw), (setFrame, 'right', mw),
                        (resetFrame, 'left', mw), (resetFrame, 'right', mw)],
                    ac=[(resetFrame, 'top', 2, setFrame)],  )




# Set/Get Defaults
# ----------------

def setDefaultsNonkeyable(nodes=None):
    setDefaults(nodes, nonkey=True)

def setDefaultsCBSelection(nodes=None):
    setDefaults(nodes, key=False, cbsel=True)

def setDefaults(nodes=None, attrList=[], key=True, nonkey=False, cbsel=False, attrQuery={}):
    """
    Set the default settings for the given nodes. Uses attributes based
    on the given settings. Default is to use all unlocked keyable attributes.
    Uses the selection if no nodes are given.
    
    `attrList` -- list of attributes to use. works in addition to other options
    `key` -- include keyable attributes
    `nonkey` -- include all channel box attributes, including nonkeyable
    `cbsel` -- use only the selected channel box attributes
    `attrQuery` -- a kwargs dict to be used with listAttr to find the
        attributes for which to store defaults. works in addition to other options
    """
    if nodes is None:
        nodes = pm.selected()
    if not isinstance(nodes, (list, tuple)):
        nodes = [nodes]
    nodes = [n for n in nodes if isinstance(n, (str, pm.nt.DependNode))]
    if len(nodes) == 0:
        return
    
    selAttrs = getChannelBoxSelection()
    # keyable and nonkeyable queries cannot be combined, so we build multiple queries.
    # any given customListAttr options are used as a third possible query
    queries = []
    if key:
        queries.append({'unlocked':True, 'k':True})
    if nonkey:
        queries.append({'unlocked':True, 'cb':True})
    if len(attrQuery) > 0:
        queries.append(attrQuery)
    def getAttrs(node):
        if cbsel:
            return selAttrs[node] if node in selAttrs else []
        else:
            listed = [a for a in [attrs for query in queries for attrs in node.listAttr(**query)]]
            custom = [node.attr(a) for a in attrList if node.hasAttr(a)]
            return listed + custom
    
    for n in nodes:
        attrs = getAttrs(n)
        if len(attrs) > 0:
            setDefaultsForAttrs(attrs)
        else:
            pm.warning('No matching attributes for {0} to set defaults. removing defaults'.format(n))
            removeDefaults(n)
    print('# set defaults for {0} object(s)'.format(len(nodes)))

def setDefaultsForAttrs(attrs):
    """
    Store the current values of each attr as defaults.
    Assumes the given attributes are all for the same object.
    """
    if attrs is None:
        return
    node = attrs[0].node()
    defaults = {}
    for attr in attrs:
        if attr.attrName() == DEFAULTS_ATTR:
            pm.warning('skipping {0} as it stores defaults and therefore cannot have a default'.format(attr))
            continue
        if attr.node() == node:
            try:
                defaults[attr.attrName()] = attr.get()
            except:
                # complex attributes just dont work
                pm.warning('could not store defaults for attribute: {0}'.format(attr))
    dattr = getDefaultsAttr(node, True)
    if dattr.isLocked():
        pm.warning('cannot store defaults, {0} is locked'.format(dattr))
    else:
        dattr.set(str(defaults))
        print ('# stored {0} default(s) for {1}: {2}'.format(len(defaults.keys()), node, defaults.keys()))



def getObjectsWithDefaults(nodes=None):
    """
    Return all objects with defaults.
    Searches the given nodes, or all nodes if none are given.
    """
    if nodes is None:
        nodes = pm.ls()
    return [obj for obj in nodes if obj.hasAttr(DEFAULTS_ATTR)]

def getDefaultsAttr(node, create=False):
    """ Return the defaults attribute for the given nodeect """
    if not isinstance(node, (str, pm.nt.DependNode)):
        raise TypeError('expected node or node name, got {0}'.format(type(node).__name__))
    node = pm.PyNode(node)
    if create and not node.hasAttr(DEFAULTS_ATTR):
        if node.isReadOnly() or node.isLocked():
            pm.warning('Cannot add defaults to {0}. Node is locked or read-only'.format(node))
            return
        node.addAttr(DEFAULTS_ATTR, dt='string')
        dattr = node.attr(DEFAULTS_ATTR)
        dattr.set('{}')
    if node.hasAttr(DEFAULTS_ATTR):
        return node.attr(DEFAULTS_ATTR)

def getDefaults(node):
    """ Returns the defaults of a node, if they exist, as a dictionary. """
    from pymel.core import dt
    from pymel.core.datatypes import Matrix
    
    dattr = getDefaultsAttr(node)
    if dattr is not None:
        defaultsRaw = None
        val = dattr.get()
        try:
            defaultsRaw = eval(val)
        except:
            pass
        # validate defaults
        if not isinstance(defaultsRaw, dict):
            pm.warning('invalid defaults found on: {0}'.format(node))
            return {}
        # process defaults
        defaults = {}
        for k, v in defaultsRaw.items():
            # skip the defaults attribute itself, if it somehow got in there
            if k == DEFAULTS_ATTR:
                pm.warning('skipping attribute {0}. it stores defaults and is therefore unable to have a default'.format(k))
                continue
            if not node.hasAttr(k):
                pm.warning('skipping default, {0} has no attribute .{1}'.format(node, k))
                continue
            # backwards compatibility checking
            if type(node.attr(k).get()) != type(v):
                pm.warning('default values for {0} are deprecated. please re-set the defaults'.format(node.attr(k)))
                # parse the value assuming its a tuple (old resetter)
                if isinstance(v, tuple) and len(v) == 1:
                    v = v[0]
            defaults[node.attr(k)] = v
        return defaults
    return {}
    



def removeDefaults(nodes=None):
    """
    Remove defaults from the given nodes.
    Returns the nodes for which defaults were removed.
    """
    if nodes is None:
        nodes = pm.selected()
    if not isinstance(nodes, (list, tuple)):
        nodes = [nodes]

    removed = []
    for n in nodes:
        if n.isReadOnly() or n.isLocked():
            pm.warning('Could not remove defaults from {0}. Node is locked or read-only.'.format(n))
            continue
        dattr = getDefaultsAttr(n)
        if dattr is not None:
            removed.append(pm.PyNode(n))
            dattr.delete()
    return removed

def removeAllDefaults():
    """ Remove all defaults from all objects in the scene. """
    return removeDefaults(getObjectsWithDefaults())



# Resetting
# ---------

def resetDefault(nodes=None):
    pm.warning('boResetter.resetDefault() is deprecated. please use reset() instead.')
    reset(nodes)

def resetSmart(nodes=None):
    reset(nodes, useDefaults=True, useStandards=True)

def resetXform(*args, **kwargs):
    pm.warning('boResetter.resetXForm() is deprecated. please use resetTransform() instead.')
    resetTransform()

def resetTransform(nodes=None):
    reset(nodes, useDefaults=False, useStandards=True)

def resetAll():
    reset(getObjectsWithDefaults())

def reset(nodes=None, useDefaults=True, useStandards=False, useCBSelection=True):
    """
    Reset the given node's attributes to their default values.
    Uses the selection if no nodes are given.
    
    `useDefaults` -- use the defaults to reset attributes
    `useStandards` -- reset transform, rotate, scale to 0, 0, and 1
        if no defaults are found for those attributes.
    `useCBSelection` -- if there is a channel box selection, use it
        to limit which attributes will be reset
    """
    if nodes is None:
        nodes = pm.selected()
    else:
        if not isinstance(nodes, (list, tuple)):
            if not isinstance(nodes, (str, unicode, pm.nt.DependNode)):
                raise TypeError('expected node, node name, or list of nodes; got {0}'.format(type(nodes).__name__))
            nodes = [nodes]
        nodes = [pm.PyNode(n) for n in nodes]
    
    selAttrs = getChannelBoxSelection()
    for n in nodes:
        settings = {}
        # add stored defaults
        if useDefaults:
            defaults = getDefaults(n)
            settings.update(defaults)
        # add standard transform reset values
        if useStandards and len(settings) == 0:
            for a in [i+j for i in 'trs' for j in 'xyz']:
                # standards are only added if they are settable
                if n.hasAttr(a) and n.attr(a).isSettable():
                    settings[n.attr(a)] = 1 if 's' in a else 0
        # trim using cb selection
        if useCBSelection and len(selAttrs) > 0:
            nodeSelAttrs = {} if not selAttrs.has_key(n) else selAttrs[n]
            delAttrs = [a for a in settings.keys() if a not in nodeSelAttrs]
            for a in delAttrs:
                del settings[a]
                
        for attr, value in settings.items():
            if attr.isSettable():
                try:
                    attr.set(value)
                except Exception as e:    
                    print ('# skipping {0}. could not set attribute:'.format(attr))
                    print (e)
            else:
                print ('# skipping {0}. attribute not settable'.format(attr))


# Utils
# -----

def listObjectsWithDefaults():
    nodes = getObjectsWithDefaults()
    print('\n# Objects with defaults ({0})'.format(len(nodes)))
    for n in nodes:
        print('#   {0}'.format(n))

def listDefaults(nodes=None):
    if nodes is None:
        sel = pm.selected()
        if len(sel) > 0:
            nodes = sel
        else:
            nodes = getObjectsWithDefaults()
    nodesWithDefaults = [n for n in nodes if n.hasAttr(DEFAULTS_ATTR)]
    print('\n# Object defaults ({0})'.format(len(nodesWithDefaults)))
    for n in nodesWithDefaults:
        defaults = getDefaults(n)
        print('#   {0}: {1}'.format(n, defaults))

def selectObjectsWithDefaults():
    pm.select(getObjectsWithDefaults())


def getChannelBoxSelection(main=True, shape=True, out=True, hist=True):
    """
    Returns a dictionary representing the current selection in the channel box.
    
    eg. {myNode: ['attr1', 'attr2'], myOtherNode: ['attr1', 'attr2', 'attr3']}
    
    Includes attributes from these sections:
    `main` -- the main attributes section
    `shape` -- the shape nodes section
    `out` -- the outputs section of the node
    `hist` -- the inputs (history) section of the node
    """
    
    def cbinfo(flag):
        return pm.channelBox('mainChannelBox', q=True, **{flag:True})
    
    # for all flags {0} = m, s, o, or h (main, selected, out, history)
    # see channelBox documentation for flag specifications
    opts = {'m':main, 's':shape, 'o':out, 'h':hist}
    modes = [i[0] for i in opts.items() if i[1]]
    objFlag = '{0}ol' # o=object l=list
    attrFlag = 's{0}a' # s=selected, a=attrs
    
    result = {}
    for mode in modes:
        objs = cbinfo(objFlag.format(mode))
        attrs = cbinfo(attrFlag.format(mode))
        if objs is not None and attrs is not None:
            for obj in objs:
                pyobj = pm.PyNode(obj)
                if not result.has_key(pyobj):
                    result[pyobj] = []
                thisObjsAttrs = [pyobj.attr(a) for a in attrs if pyobj.hasAttr(a)]
                result[pyobj].extend(thisObjsAttrs)
    
    return result

