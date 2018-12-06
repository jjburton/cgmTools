"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basis of cgmMeta.cgmNode
================================================================
"""
from cgm.core import cgm_Meta as cgmMeta

#==============================================================================================
#>> cgmMeta.cgmObject
#==============================================================================================
from cgm.core import cgm_Meta as cgmMeta
import maya.cmds as mc

#Let's start by making a series of objects

#>>message Treatment =========================================================================
#We have made several changes to r9's stuff in how we do messages, it is however compatible with r9's stuff
#One of our calls to store info is doStore
#First we're gonna make a catcher node
mi_catchMeObj = cgmMeta.cgmObject(name = 'catchMe')
mi_catcherObj = cgmMeta.cgmObject(name = 'msgCather')

#One of our calls to store info is doStore
mi_catcherObj.doStore('objNoMessage',mi_catchMeObj,overideMessageCheck = True)#It's gonna just store a string, no message....
mi_catcherObj.doStore('objNoMessage',mi_catchMeObj,overideMessageCheck = False)#Now it's a message...woot!
#So maya can do that, what if you wanted to do something neater like say, store an attribute
mi_catcherObj.doStore('objTX',"%s.tx"%mi_catchMeObj.mNode)#It's gonna just store a string, no message....
mi_catchMeObj.tx = 4#our attribute changed. That's because, this storage method stores on a compatible attribute format
#That's great and all, but we were talking about messages...
mi_catcherObj.getMessage('objTX')# we get the attribute, neato...
mi_catcherObj.getMessageAsMeta('objTX')# we get the attribute, neato...cgmAttr for the win
#implementing attr setup to msgLists is on the ToDO list
#==============================================================================================

#>>Component use ==============================================================================
#We'll make a shphere and buffer that...
l_sphereReturn = mc.sphere(nsp  = 4, name = 'MySphere')
mi_sphere = cgmMeta.cgmNode(l_sphereReturn[0])#We'll meta the sphere object
mi_sphere.mNode#Just like an mNode, but what if we wanna instance a component...
mi_cv = cgmMeta.cgmNode("%s.cv[3][0]"%mi_sphere.mNode)#metaNode a cv
mi_cv.mNode#We get the shape back
mi_cv.getComponent()#We get the component
mi_cv.isComponent()#Yup
mi_sphere.isComponent()#Nope...it's a sphere
mi_sphere.getComponents('cv')#List of cv's
mi_sphere.getPosition()#Get our position,arg is world space or not, default is worldspace(True)
mi_cv.getPosition()#Get the position of the cv
mi_cv.getTransform()#Get the transform of the component
#==============================================================================================

#>>Properties =================================================================================
mi_sphere.p_nameBase#name string along
mi_sphere.p_nameLong#long name form
mi_sphere.p_nameShort#short name form
mi_sphere.p_referencePrefix#Gonna be false as we're not referenced
mi_sphere.p_parent#returns our parent, on cgmObject, you can set as well, we'll get more into it there
#==============================================================================================

#>>msgList ====================================================================================
#Let's look at the concept of the msgList
mi_catcherObj = cgmMeta.cgmObject(name = 'msgListCather')

#First we're gonna make some objects to deal with, say 5
md_msgListObjs = {}
ml_msgListObjs = []
for i in range(5):
    try:mObj= cgmMeta.cgmObject('msgListObj_%i'%i)
    except:mObj= cgmMeta.cgmObject(name = 'msgListObj_%i'%i)
    md_msgListObjs[i] = mObj
    ml_msgListObjs.append(mObj)

#Connect the first two objects, you can pass metaclass or string objects
mi_catcherObj.msgList_connect([ml_msgListObjs[0],ml_msgListObjs[1].mNode],'msgAttr','connectBack')
ml_msgListObjs[0].connectBack#what do you know, we connected back to our holder we can also dance a little with that...
ml_msgListObjs[0].connectBack.msgAttr_0.connectBack.msgAttr_1#The mind truly spins....:)

#Let's query it
mi_catcherObj.msgList_get('msgAttr')#Query our list, it's going to default to do it as meta

#Say we wanted just the objlist
mi_catcherObj.msgList_get('msgAttr',asMeta=False)

#We can also do a getMessage call which offers a few more options
mi_catcherObj.msgList_getMessage('msgAttr',longNames = True)

#Appending is supported
mi_catcherObj.msgList_append(ml_msgListObjs[2],'msgAttr')
mi_catcherObj.msgList_get('msgAttr',False) #What do you know, we have the new on there...

#Indexing is supported
mi_catcherObj.msgList_index(ml_msgListObjs[2],'msgAttr')
#As is checking if we have a msgList on an attr name
mi_catcherObj.msgList_exists('msgAttr')
mi_catcherObj.msgList_exists('isAnyoneThere')#Nope...

#Let's remove the first
mi_catcherObj.msgList_remove(ml_msgListObjs[0],'msgAttr')
mi_catcherObj.msgList_get('msgAttr',False) #We Removed the first

#Let's store em all
mi_catcherObj.msgList_connect(ml_msgListObjs,'msgAttr','connectBack')
#Let's delete number 2....
ml_msgListObjs[2].delete()
mi_catcherObj.msgList_get('msgAttr',asMeta=False,cull = False)#That entry is empty now...When cull is off, on by default
#What if we want to clean this list without the empty
mi_catcherObj.msgList_clean('msgAttr')
#And we have a clean list again...

#Say we wanna purge this data...
mi_catcherObj.msgList_purge('msgAttr')#Our attrs are gone... so sad....
#==============================================================================================

#>>Other Calls ================================================================================
mi_cv.getMayaType()#Because maya's type return thing isn't so hot....
mi_sphere.getMayaType()
mi_sphere.doDuplicate()#its gonna give us a duplicate, but only a null?....
mi_dup = mi_sphere.doDuplicate(parentOnly=False)#Now it works

mi_loc = mi_sphere.doLoc()#We can loc items with the same maker cgmLocinator uses
mi_cvLoc = mi_cv.doLoc()#We can loc components too...

#We're gonna add an enum to look at something...
mi_sphere.addAttr('testEnum',attrType = 'enum')
mi_sphere.testEnum#nice, but what if we want as a string
mi_sphere.getEnumValueString('testEnum')

mi_loc.returnPositionOutPlug()#This is a wip one but it works for most necessary things, handy for nodal work
#==============================================================================================
