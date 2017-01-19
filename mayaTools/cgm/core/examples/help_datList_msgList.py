"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basics of datLists and msg lists
================================================================
"""
#==============================================================================================
#>> attribute_utils
#==============================================================================================
from cgm.core.lib import attribute_utils as ATTR
from cgm.core import cgm_Meta as cgmMeta

import maya.cmds as mc

#>>Intro =========================================================================
#First we're gonna make some objects 
_ml_targets = []
_mi_catcher = cgmMeta.cgmObject( mc.polySphere(n = "catcher")[0] )

for i,p in enumerate([-5,0,5]):
    _mObj = cgmMeta.cgmObject( mc.polySphere(n = "sphere_{0}".format(i))[0] )
    _mObj.translate = [p,5,0]
    _ml_targets.append(_mObj)
    
    
#>> datList =======================================================================
"""
A datList is a way to store indexed data on attributes in a connectable format.
You can store string lists by a single string attr with commas or another separator but
you can't connect a name tag (for example) to another object unless each string is on their own 
attribute.


Let's begin with storing a series of strings
"""

_l_strings = ['all','dogs','go','to','heaven']
ATTR.datList_connect(_mi_catcher.mNode,'strings',_l_strings)

#Now, select the catcher object and look at the attributes in the extra attributes section...
#you'll notice an indexed series of attributes so that

_mi_catcher.strings_0 #...will get us our value or....

ATTR.datList_exists(_mi_catcher.mNode,'strings')#...True
ATTR.datList_exists(_mi_catcher.mNode,'batman')#...False

ATTR.datList_getAttrs(_mi_catcher.mNode,'strings')#Gets our attributes
ATTR.datList_get(_mi_catcher.mNode,'strings')#Gets our values

ATTR.datList_index(_mi_catcher.mNode,'strings','dog')#...will fail as it's not in our list
ATTR.datList_index(_mi_catcher.mNode,'strings','dogs')#...gets the correct index

ATTR.datList_removeByIndex(_mi_catcher.mNode,'strings',0)#...can remove by index
ATTR.datList_remove(_mi_catcher.mNode,'strings','go')#...or by value
ATTR.datList_remove(_mi_catcher.mNode,'strings','kangaroo')#...nope, not there.

ATTR.datList_clean(_mi_catcher.mNode,'strings')#...reindexes our list with existing values
ATTR.datList_get(_mi_catcher.mNode,'strings')#Gets our values

ATTR.datList_connect(_mi_catcher.mNode,'strings',_l_strings)#...can do a clean push as well
ATTR.datList_append(_mi_catcher.mNode,'strings','maybe')
ATTR.datList_get(_mi_catcher.mNode,'strings')#...gets our new list

#...let's move to values
_l_values = [1,2,3,4,5]
ATTR.datList_connect(_mi_catcher.mNode,'values',_l_values)#...You'll see we have a new list of integer attrs
ATTR.datList_get(_mi_catcher.mNode,'values')#Gets our values

#What if we wanna mix and match
_l_values = [1,2.0,[1.1,2,4],[1,2,3,4,5,6],False,'cat',_ml_targets[0].mNode]
ATTR.datList_connect(_mi_catcher.mNode,'values',_l_values)#...New list, different attribute types
ATTR.datList_get(_mi_catcher.mNode,'values')#Gets our values


#However, if we anna deal with objects and not simple values, we need to move on to msgList...
#First let's clean up our object
ATTR.datList_purge(_mi_catcher.mNode,'values')#...
ATTR.datList_purge(_mi_catcher.mNode,'strings')#...

ATTR.msgList_connect(_mi_catcher.mNode,'example',_ml_targets)#...we can do a simple message connection or...
ATTR.msgList_connect(_mi_catcher.mNode,'example',_ml_targets,'source')#...do it with a connect back on each target

ATTR.msgList_get(_mi_catcher.mNode,'example')#...gets our return

#...this is all fine and dandy but what if we wanna store more specific message data, like an attribute or a component....
ATTR.msgList_append(_mi_catcher.mNode,'example',"{0}.tx".format(_ml_targets[0].mNode))
#...you'll note a new json dict attribute has been created. This is how we store our extra stuff

ATTR.msgList_get(_mi_catcher.mNode,'example')#...gets our new list with our extra object

ATTR.msgList_append(_mi_catcher.mNode,'example',"{0}.tx".format(_ml_targets[0].mNode))


ATTR.msgList_append(_mi_catcher.mNode,'example',"{0}.vtx[120:122]".format(_ml_targets[1].mNode))
ATTR.msgList_get(_mi_catcher.mNode,'example')#...gets our new list with our message component...

ATTR.msgList_index(_mi_catcher.mNode,'example',"{0}.vtx[120:122]".format(_ml_targets[1].mNode))#...can index

ATTR.msgList_removeByIndex(_mi_catcher.mNode,'example',[0,1])#...removes the first two

ATTR.msgList_clean(_mi_catcher.mNode,'example')#...cleans it back


"""
Yes, you can do some of this stuff with objectSets or other avenues and sometimes those work great. This
is simply another way of storing data mainly for our rigging purposes. For example, I wanted a way to store
component info for the Locinator update. Previously I'd just done a string store. The problem with that is 
sometimes an object name changes or the long name changes because of a duplicate object in scene. At that point
locinator's update would break. When I added that, attribute storing was just a short hop beyond and is more efficient
than my old method of creating a connected compatible attibute, wiring the source to that and jumping up the connections 
to get the 'message'










    


