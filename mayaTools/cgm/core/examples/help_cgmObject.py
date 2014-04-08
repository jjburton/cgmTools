"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basis of cgmMeta.cgmObject
================================================================
"""
from cgm.core import cgm_Meta as cgmMeta

#==============================================================================================
#>> cgmMeta.cgmObject
#==============================================================================================
from cgm.core import cgm_Meta as cgmMeta
import maya.cmds as mc
import copy

#Let's start by making a series of objects

#>>Parenting ====================================================================================
#First we're gonna make some objects to deal with, say 5
ml_cgmObjects = []
for i in range(5):
    mObj= cgmMeta.cgmObject(mc.joint(p = [0,0,2*i],name = 'generatedCGMObject_%i'%i))
    ml_cgmObjects.append(mObj)

#Neat,now we have a few joints to play with...let's play
ml_cgmObjects[1].p_parent = False #We're gonna parent the idx 1 joint to the world by passing it false

for mObj in ml_cgmObjects:mObj.p_parent = False #Let's parent them all to the world
for i,mObj in enumerate(ml_cgmObjects[1:]):mObj.p_parent = ml_cgmObjects[i] #Parent em back

#What if we wanted to parent idx 2 and 3 both to 1?
ml_cgmObjects[2].p_parent = ml_cgmObjects[0]#We can pass the mClass
ml_cgmObjects[2].tx = 2#just to be a little clearer

ml_cgmObjects[4].p_parent = ml_cgmObjects[1].mNode#We can pass the string mNode
ml_cgmObjects[1].tx = -2 #and a little more clear
ml_cgmObjects[4].tx = 0 #and a little more clear

ml_cgmObjects[4].p_parent #returns just the parent
ml_cgmObjects[4].getParent(asMeta = 1) #what if we want as a parent. the property uses this command with the default asMeta of False
ml_cgmObjects[4].getParent(asMeta = 1).p_nameShort #daisy chain the calls
#==============================================================================================

#>>Family ====================================================================================
ml_cgmObjects[4].getAllParents()#we can get all the parents of an object as well as the imediate
ml_cgmObjects[4].getAllParents(fullPath = True)#We can get full paths
ml_cgmObjects[4].getAllParents(asMeta = 1)#We can get those as meta too

ml_cgmObjects[0].getChildren()#We can get immediate children
ml_cgmObjects[0].getChildren(asMeta = True)#as meta or full path too

ml_cgmObjects[0].getAllChildren()#We can get all dag children
ml_cgmObjects[0].getAllChildren(asMeta = True)#as meta or full path too

ml_cgmObjects[0].getShapes()# Hmm...no shapes, let's try something with shapes

mi_sphere = cgmMeta.cgmObject(mc.sphere()[0]) #let's wrap a sphere
mi_sphere.getShapes() #Get some shapes
mi_sphere.getShapes(asMeta = 1) #as meta too

#What about some other relative checks...
ml_cgmObjects[1].getSiblings() #What is a sibling? A sibling is a definition of our own...
#It is an object at the same heirarchal level as another object of matching type to our source
ml_cgmObjects[1].getSiblings(asMeta = 1) #Can do the asMeta call as well

ml_cgmObjects[1].getFamilyDict()#Another way to get a few bits of data...

ml_cgmObjects[4].isChildOf(ml_cgmObjects[0]) #We can check up the dag tree for a logic check..
ml_cgmObjects[4].isChildOf(ml_cgmObjects[2]) #This one is not a child of that joint

ml_cgmObjects[0].isParentOf(ml_cgmObjects[1]) #Can check the other relationship as well
ml_cgmObjects[4].isParentOf(ml_cgmObjects[2])

ml_cgmObjects[4].getListPathTo(ml_cgmObjects[0])#Another way to get some data
ml_cgmObjects[0].getListPathTo(ml_cgmObjects[4])#front or back
#==============================================================================================

#>>Name Stuff ====================================================================================
#Let's start by tagging our root joint
ml_cgmObjects[0].addAttr('cgmName','testing') #This is our main tag
ml_cgmObjects[0].doName()#Our object has been renamed with this name tag and it autotyped

#Let's add some direction tags to idx 1/2
ml_cgmObjects[1].addAttr('cgmDirection','left') #Direction tag of left
ml_cgmObjects[2].addAttr('cgmDirection','right') #...and right

for idx in [1,2]:ml_cgmObjects[idx].doName()
#Now our two joints are prefixed with their directions, note they have inherited their parent's name, note the children are not named...

for idx in [1,2]:ml_cgmObjects[idx].doName(nameChildren = True)# Neat, now the children are named
for idx in [1,2]:ml_cgmObjects[idx].doName(fastIterate = False, nameChildren = True)
#The most thorough name tag is turning off fastIterate, it is slower so we don't use very often. If you're just doing manual stuff if's fine.
#If you're running large processes, you'll wanna avoid

#Another thing nametags can be are messages, let's try that.
mi_locToName = cgmMeta.cgmObject(mc.spaceLocator()[0])
mi_locToName.addAttr('cgmName',ml_cgmObjects[0].mNode,attrType = 'messageSimple')#we're gonna store the first joint to the locators, cgmName tag
mi_locToName.doName() #You'll see it's taken the name of the name linked object and named with that

#So what's going on with this stuff? When objects are named, they generate a name dictionary and build a name from that...
ml_cgmObjects[4].getNameDict() #Even though this object has none of these cgmNameTag attributes, it nonethless, inherits those names
ml_cgmObjects[4].parent = False
ml_cgmObjects[4].getNameDict()#Now the only thing the name dict contains is it's type which all objects have
ml_cgmObjects[4].parent = ml_cgmObjects[1]#Parent back for now

#Let's add another tag to our root
ml_cgmObjects[0].addAttr('cgmTypeModifier','skin') 
ml_cgmObjects[0].doName(nameChildren = True)#Hmmm...so there are some tags which aren't inherited, type modifiers are not but types are
del(ml_cgmObjects[0].cgmTypeModifier)
ml_cgmObjects[0].addAttr('cgmPosition','front') 
ml_cgmObjects[0].doName(nameChildren = True)#Positons are inheritable
#==============================================================================================


#>>Rigging functions ==========================================================================
ml_cgmObjects[1].doGroup(maintain = True)#You'll see we get a new group maintaining our objects's position
ml_cgmObjects[1].doGroup(maintain = False)#This will not maintain our heirarchy and generate a new group

#Copy pivot this is for objects with shapes
mi_copyPivotToMe = cgmMeta.cgmObject(mc.sphere(name = 'copyPivotToMe')[0])
mi_copyPivotFromMe = cgmMeta.cgmObject(mc.sphere(name = 'copyPivotFromMe')[0])
mi_copyPivotFromMe.ty = 5
mi_copyPivotToMe.doCopyPivot(mi_copyPivotFromMe)
mi_copyPivotToMe.select()#Look at it's pivot

#Contraints 
#Let's start by contrainting a couple of joints
mc.pointConstraint(ml_cgmObjects[4].mNode,ml_cgmObjects[3].mNode,maintainOffset = False)
mc.orientConstraint(ml_cgmObjects[2].mNode,ml_cgmObjects[3].mNode,maintainOffset = False)

#Great, now what....
ml_cgmObjects[3].getConstraintsTo()#Get the constraint to
ml_cgmObjects[3].getConstraintsTo(asMeta = True)

ml_cgmObjects[4].getConstraintsFrom()#Get the constraint from
ml_cgmObjects[4].getConstraintsFrom(asMeta = True)

ml_cgmObjects[3].isConstrainedBy(ml_cgmObjects[2])#Get a constraint from one object to another
#==============================================================================================