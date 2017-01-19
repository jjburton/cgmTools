"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basis of meta
================================================================
"""
import maya.cmds as mc
from Red9.core import Red9_Meta as r9Meta
from cgm.core import cgm_Meta as cgmMeta

#==============================================================================================
#>> mNode
#==============================================================================================
mc.file(new=True,f=True)#...let's start with a clean file
mc.group(em=True, n = 'testingNull')#...let's make a null
n1 = r9Meta.MetaClass('testingNull')#...now it's instantiated as a MetaClass to our given catcher 'n1'
n1.mNode#...returns it's dag handle
mc.group(n1.mNode)#...let's group our null
n1.mNode#...still returns our object

#>>Rename it =========================================================================
mc.rename('testingNull','Whatchamacallit')
n1.mNode#...still returns our object

#==============================================================================================
#>> Special attributes, caching and the registries
#==============================================================================================
mc.file(new=True,f=True)#...let's start with a clean file
#Go to the outliner and make sure DAG objects only is off

mc.createNode('network', n = 'cmdCreated')#...let's make a null via cmd call
o1 = r9Meta.MetaClass('cmdCreated')#...and instantiating it
n1 = r9Meta.MetaClass(nodeType='network', name='callCreated')#...let's make one via meta call

#>>How are they the same? =========================================================================
#They both are instantiated nodes that have all the features native to meta.
o1#...
n1#...they both show as instantiated r9Meta.MetaClass nodes
o1.mNode
n1.mNode#...both return fine
o1.select()
n1.select()
#... all the base functionality is there. You get the idea

#>>How are they different? =========================================================================
#Take a moment to select each node and look at their user attributes in the attribute editor
#You'll notice that our meta call created node has several user attributes
mc.listAttr(o1.mNode, userDefined = True)
mc.listAttr(n1.mNode, userDefined = True)


#>>Caching =========================================================================
r9Meta.printMetaTypeRegistry()#...this is a list of the kinds of maya nodes registered for creation and searching
r9Meta.printSubClassRegistry()#...this is a list of metaClass subclasses registered in memory.


#One of the main benefits of meta nodes is that they may be cached for speed. Let's look at the cache.
r9Meta.printMetaCacheRegistry()#...one of our nodes is cached, one is not
r9Meta.registerMClassNodeCache(o1)#...let's push our cmd created node into the cache
r9Meta.printMetaCacheRegistry()#...now it is cached with it's dag handle

r9Meta.resetCache()


r9Meta.printMetaCacheRegistry()#...returns a list of cached nodes. It will most likely be empty


#>>Conversion =========================================================================
#...The wrong way....
n1.mClass = 'cgmNode'#let's try changing our mClass and...
n1 = r9Meta.MetaClass('callCreated')#...reinstantiating it
n1#...hmmm, still returns okay as it was cached. Note the mClass attr in the result doesn't match the class type

#...add an mClass attribute to an uncached node
mc.createNode('network', n = 'toConvert')#...let's make a null via cmd call
o2 = r9Meta.MetaClass('toConvert')#...and instantiating it
o2.addAttr('mClass','cgmNode')#...we'll give it another tag
o2#...it's still gonna return as a metaClass unitl we reinstantiate it
o2_re = r9Meta.MetaClass('toConvert')#...and instantiating it
o2_re#...
o2#...still gives the orginal
o2.mNode
o2_re.mNode
#...same dag handle but differnt mClass Types and different functions on each

#...okay but what if it's cached or call created...
o2.delete()
#...same as before...
mc.createNode('network', n = 'toConvert')#...let's make a null via cmd call
o2 = r9Meta.MetaClass('toConvert')#...and instantiating it
o2.addAttr('mClass','cgmNode')#...we'll give it another tag
r9Meta.registerMClassNodeCache(o2)#...let's push our cmd created node in to the cache
o2_re = r9Meta.MetaClass('toConvert')#...and instantiating it
o2#...
o2_re#...still gives the original
#...now we're getting the cached version instead of a new instantiation

#...okay, how bout a call created node?
o2.delete()
n2 = r9Meta.MetaClass(nodeType='network', name='toConvert')#...let's make one via meta call. It caches by default
n2.mClass = 'cgmNode'#...we'll give it another tag
n2_re = r9Meta.MetaClass(n2.mNode)#...and instantiating it
n2_re#...still gives the original


#...what if we give a node an unknown mClass?
mc.createNode('network', n = 'invalidMClass')#...let's make a null via cmd call
mc.addAttr ('invalidMClass', ln = 'mClass', dt = 'string')
mc.setAttr('invalidMClass.mClass','noIdea',type = 'string')
o3 = r9Meta.MetaClass('invalidMClass')#...and instantiating it
o3#...it's gonna reuturn as a MetaClass because it's mClass is unknown
cgmMeta.cgmNode('invalidMClass')#...I can also call it as a cgmNode with no issue because no valid mClass is set
o3.mClass = 'cgmNode'#...if i set it's mClass to a known mClass however
r9Meta.MetaClass('invalidMClass')#...it's gonna now always return as a cgmNode as it's a valid mClass value

#...so, long story short. Manually changing a node's mClass attribute is not a reliable method of changing the type it instantiates to 
#...The right way...

#r9's method
n3 = r9Meta.MetaClass(nodeType='network', name='r9Convert')#...let's make one via meta call
r9Meta.convertMClassType(n3,'cgmNode')#... This converts our node to a cgmNode type

#cgm's Method
cgmMeta.validateObjArg(n3.mNode,'MetaClass',setLogLevel = 'debug')#...this initially wont' change because our current class is a subclass of MetaClass, trust that this is a feature and not a bug
cgmMeta.validateObjArg(n3.mNode,'MetaClass',setClass = True, setLogLevel = 'debug')#...this pass will get it as we have our setClass flag on
cgmMeta.validateObjArg(n3.mNode,'cgmNode',setClass = True, setLogLevel = 'info')#...convert it back and get out of debug

#==============================================================================================
#>> Data storage
#==============================================================================================
mc.file(new=True,f=True)#...let's start with a clean file
#Go to the outliner and make sure DAG objects only is off

n1 = r9Meta.MetaClass(nodeType='network', name='r9Example')#...let's make one via meta call

#>>Json =========================================================================
d_test ={'jsonFloat':1.05,'Int':3,'jsonString':'string says hello','jsonBool':True}
n1.addAttr('jsonTest', d_test)  #create a string attr with JSON serialized data
n1.jsonTest['jsonString']     #will deserialize the MayaNode jsonTest attr back to a dict and return its key['stringTest']
n1.jsonTest['jsonString'] = 'string says no'#...can you change it this way?
n1.jsonTest['jsonString']#...no

#In order to change the dict you have to push your json dict, mod it and push it back
d_test['jsonString'] = 'string says no'
n1.jsonTest = d_test#...push it back
n1.jsonTest
type(n1.jsonTest['jsonFloat'])#...yup that's a float
type(n1.jsonTest['jsonBool'])#...data type is retained

#>>Message/Multimessage =========================================================================
# First we're gonna make some objects to deal with, say 4
# and store them to a list for easy calling
l_cubes = []
for i in range(4):
    l_cubes.append(mc.polyCube()[0])

n1.addAttr('msgSingleTest', value= l_cubes[0], attrType='messageSimple')
n1.msgSingleTest  #>> ['pCube1']   
n1.msgSingleTest='pCube2'#...note, if you're watching in the attribute editor, maya may not update to see the change, just reselect your storage object.
n1.msgSingleTest  #>> ['pCube2'] # NOTE pCube1 had now been disconnected and the msg connected to Cube2
delattr(n1,'msgSingleTest')# delete that attr

#create a multi-message attr and wire pCube1 to it, indexMatters=False
n1.addAttr('msgMultiTest', value= l_cubes, attrType='message')  
n1.msgMultiTest   #>> [u'|pCube1', u'|pCube2', u'|pCube3', u'|pCube4'], note they are not in creation order.
l_cubes
# This is an issue with mutimessage attributes should you need ordered lists

n1.msgMultiTest='pCube1'
n1.msgMultiTest   #>> ['pCube1'] #the others have now been disconnected
n1.msgMultiTest=['pCube2','pCube3']
n1.msgMultiTest   #>>['pCube2','pCube3']

#... Let's look at a potential problem with multi message attributes and how they're natively connected.
from cgm.lib import attributes
attributes.storeObjectsToMessage(l_cubes,n1.mNode,'msgMultiTest')#...this uses maya's connection format
n1.msgMultiTest   #>> looks good...
mc.duplicate(l_cubes[2])
n1.msgMultiTest   #>> um...our list grew. There is a bug in some versions of maya that this connection is duplicated.
#I'm not sure what versions are fixed. This is part of the reason why we created the data storage method we'll see in a moment

#>>message Treatment =========================================================================
#We have made several changes to r9's stuff in how we do messages, it is however compatible with r9's stuff
#One of our calls to store info is doStore
#First we're gonna make a catcher node
mi_catchMeObj = cgmMeta.cgmObject(name = 'catchMe')
mi_catcherObj = cgmMeta.cgmObject(name = 'msgCather')

#One of our calls to store info is doStore
mi_catcherObj.doStore('objNoMessage',mi_catchMeObj.mNode,overideMessageCheck = True)#It's gonna just store a string, no message....
mi_catcherObj.doStore('objNoMessage',mi_catchMeObj.mNode,overideMessageCheck = False)#Now it's a message...woot!
#So maya can do that, what if you wanted to do something neater like say, store an attribute
mi_catcherObj.doStore('objTX',"%s.tx"%mi_catchMeObj.mNode)#It's gonna just store a string, no message....
mi_catchMeObj.tx = 4#our attribute changed. That's because, this storage method stores on a compatible attribute format
#That's great and all, but we were talking about messages...
mi_catcherObj.getMessage('objTX')# we get the attribute, neato...
mi_catcherObj.getMessageAsMeta('objTX')# we get the attribute, neato...cgmAttr for the win
#implementing attr setup to msgLists is on the ToDO list
#==============================================================================================


#>>msgList(cgmMeta only) =========================================================================
#Let's look at the concept of the msgList
mi_catcherObj = cgmMeta.cgmObject(name = 'msgListCather')

#First we're gonna make some objects to deal with, say 5
md_msgListObjs = {}#...md is our designater for meta dicts
ml_msgListObjs = []#...ml is our designator for meta lists
for i in range(5):
    try:mObj= cgmMeta.cgmObject('msgListObj_{0}'.format(i))
    except:mObj= cgmMeta.cgmObject(name = 'msgListObj_{0}'.format(i))
    md_msgListObjs[i] = mObj
    ml_msgListObjs.append(mObj)

#Connect the first two objects, you can pass metaclass or string objects
mi_catcherObj.msgList_connect([ml_msgListObjs[0],ml_msgListObjs[1].mNode],'msgAttr','connectBack')
ml_msgListObjs[0].connectBack#what do you know, we connected back to our holder we can also dance a little with that...
ml_msgListObjs[0].connectBack.msgAttr_0.connectBack.msgAttr_1#The mind truly spins....message walking for the win:)

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
mi_catcherObj.msgList_get('msgAttr',False) 

#Say we wanna purge this data...
mi_catcherObj.msgList_purge('msgAttr')#Our attrs are gone... so sad....

#==============================================================================================
#>> Message Walking/Node Linking
#==============================================================================================
mc.file(new=True,f=True)#...let's start with a clean file
#Go to the outliner and make sure DAG objects only is off

p1 = r9Meta.MetaClass(name='parentNode', nodeType='network')
mc.createNode('network', n = 'childNode1')#...let's make a null via cmd call
#We're doing it this way so that the child node is NOT tagged for meta
c1 = r9Meta.MetaClass('childNode1')
c2 = r9Meta.MetaClass(name='childNode2', nodeType='network')

#...just msgSimple Connections
p1.addAttr('simpleConnect', value= c1, attrType='messageSimple')
p1.simpleConnect#...this only returns the dag handle because our child isn't mClassed

p1.addAttr('simpleConnect2', value= c2, attrType='messageSimple')
p1.simpleConnect2#...now we get meta because the child connection is a mClassed node

#...child/parent node connections. This idea is more for doing two way connections
p1.connectChild(c2, 'childConnection2', 'parentConnection')#...the first attr is what will be on the parent, the second is how the child will connect back...
p1.childConnection2#...meta connect
c2.parentConnection#...and back
#...and walk
p1.childConnection2.parentConnection.mNode

#==============================================================================================
#>> Data Searching
#==============================================================================================
mc.file(new=True,f=True)#...let's start with a clean file
#...let's make some stuff
n1 = r9Meta.MetaClass(name = 'MetaClass_1', nodeType='network')
n2 = r9Meta.MetaClass(name = 'MetaClass_child', nodeType = 'network')
c1 = cgmMeta.cgmNode(name = 'cgmNode_1')
c2 = cgmMeta.cgmObject(name = 'cgmObject_1')

#Let's set some attrs so we can search with an enumerated loop
for i,o in enumerate([n1,n2,c1,c2]):
    o.addAttr('testAttr',i)
    
n1.connectChild(n2, 'childNode', srcAttr='parentNode')#...wire this so we can see some stuff later
n1.connectChild(c1, 'childNode2', srcAttr='parentNode')#...and another

#>>Instance query =========================================================================
#Okay, now let's search some stuff
#First, a call just to see some info about meta class inheritance as registered in the subclass registry
r9Meta.getMClassInstances(r9Meta.MetaClass)

#...make it more readable
for o in r9Meta.getMClassInstances(r9Meta.MetaClass):print o
#...as you can see there are a lot of subclasses. What if we just wanted to see subclasses to cgmObject
for o in r9Meta.getMClassInstances(cgmMeta.cgmObject):print o#...quite a few less

#>>getMetaNodes =========================================================================
#...just to make seeing stuff a little easier, we're gonna make a little pass through function
def _res(l):
    for o in l:print o

_res(r9Meta.getMetaNodes())#...returns all metaNodes in the scene
_res(r9Meta.getMetaNodes(dataType = ''))#...returns as dag strings
_res(r9Meta.getMetaNodes(mTypes = 'cgmObject'))#...only returns a given meta type
_res(r9Meta.getMetaNodes(mTypes = r9Meta.MetaClass))#...only returns a given meta type
_res(r9Meta.getMetaNodes(mInstances = 'cgmNode'))#...returns both the cgmNode in the scene and the cgmObject as it's a subclass to cgmNode

_res(r9Meta.getMetaNodes(mAttrs = 'tx=0'))#...get any nodes with a tx value of 1
_res(r9Meta.getMetaNodes(mAttrs = 'testAttr=2'))#...get our set attr
_res(r9Meta.getMetaNodes(mAttrs = 'NOT:testAttr=2'))#...get any nodes that don't have this value


#...relational 
_res(n1.getChildren())#...can see all our children of our 'parent' node
_res(n1.getChildren(asMeta = True))#...can get data as meta
n1.getChildren(cAttrs = ['childNode'])#....cAttrs checks the wiring
n1.getChildren(cAttrs = ['childNode2'])

n1.getChildren(nAttrs = ['testAttr'])#...both have the attribute so both are returned

c1.getParentMetaNode()#...get a parent node from a child

#...connections
n1.getNodeConnections(c1.mNode)#...get connects between two nodes 
c1.getNodeConnections(n1.mNode)
n2.getNodeConnections(n1.mNode)












#==============================================================================================
#>> Extra
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



def jointStuff_standard():
    l_joints = mc.ls(sl = 1)

    for jnt in l_joints:#Validation loop before doing stuff...
        if not mc.objectType(jnt) == 'joint':
            raise ValueError,"Not a joint: {0}".format(jnt)
        
    for i,jnt in enumerate(l_joints):   
        #First we're gonna create a curve at each joint. Name, parent and snap it ...
        jnt = mc.rename(jnt,"ourChain_{0}_jnt".format(i))#...gotta catch stuff when you rename it
        str_crv = mc.circle(normal = [1,0,0], ch = 0)[0]
        str_crv = mc.parent(str_crv,jnt)[0]#...gotta catch stuff when you parent it
        str_crv = mc.rename(str_crv, '{0}_crv'.format(jnt))#...everytime it changes
        mc.delete(mc.parentConstraint(jnt, str_crv, maintainOffset = False))
               
        #Now we wanna add a locator at each joint - matching, position,orientation,rotation order
        loc = mc.spaceLocator(n = "{0}_loc".format(jnt))[0]
        ro = mc.getAttr('{0}.rotateOrder'.format(jnt))
        mc.setAttr('{0}.rotateOrder'.format(loc),ro)
        mc.delete(mc.parentConstraint(jnt, loc, maintainOffset = False))
             
        #Now if we wanna store data on each object one to another...
        mc.addAttr (jnt, ln='curveObject', at= 'message')
        mc.connectAttr ((str_crv+".message"),(jnt+'.curveObject'))
        mc.addAttr (str_crv, ln='targetJoint', at= 'message')
        mc.connectAttr ((jnt+".message"),(str_crv+'.targetJoint'))    
        
        mc.addAttr (loc, ln='source', at= 'message')
        mc.connectAttr ((jnt+".message"),(loc+'.source'))          
        #...the contains none of the built in checking and verifying built in to metaData and if you tried to
        #...run this on message attributes that existed or were locked or 15 other scenerios, it would fail
        
        
        

def jointStuff_meta():
    ml_joints = cgmMeta.validateObjListArg(mc.ls(sl=1), mayaType = 'joint')#...gets us a validated meta data list of our selection
    
    for i,mJnt in enumerate(ml_joints):
        mJnt.rename("ourChain_{0}_jnt".format(i))
        mi_crv = r9Meta.MetaClass( mc.circle(normal = [1,0,0], ch = 0)[0])
        mc.parent(mi_crv.mNode, mJnt.mNode)
        mi_crv.rename('{0}_crv'.format(mJnt.p_nameBase))#...p_nameBase property cgmMeta only
        mc.delete(mc.parentConstraint(mJnt.mNode, mi_crv.mNode, maintainOffset = False))
        
        #...loc
        mJnt.doLoc()#..doLoc cgmMeta only        
        
        #...same data storage
        mJnt.connectChildNode(mi_crv,'curveObject','targetJoint')
        

        
        
        
        
        
        