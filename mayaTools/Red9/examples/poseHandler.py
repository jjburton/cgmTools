'''
------------------------------------------
Red9 Studio Pack: Maya Pipeline Solutions
Author: Mark Jackson
email: rednineinfo@gmail.com

Red9 blog : http://red9-consultancy.blogspot.co.uk/
MarkJ blog: http://markj3d.blogspot.co.uk
------------------------------------------

================================================================

Advanced Pose Data management!

This is a template example for a poseHandler.py file that the 
PoseSaver now optionally looks for in any pose folder. If this 
file is found then the main poseCall runs one of the two main funcs 
below, by-passing the standard PoseData.getNodes() call and allowing 
you to tailor the poseSaver on a folder by folder level.

Why?? well without this you have no real way to tailor a pose to 
a given rig other than setting up the preset in the hierarchy filter 
and changing the rootNode. Now that's fine for individuals but in a 
production environment you may want more control. You may want to
have specific handlers for finger poses, facial etc and this allows 
all of that to be done, animators just switch to a folder and that 
folder controls how the data is processed.

NOTE: 'poseObj' arg is the actual PoseData class instance passed into 
the calls from the main class. This allows you to monkey-patch and modify
the internal object on the fly if you need too.


example:
This is an example I use at work for our finger pose folder just to 
show what can be done here. The key is that you have to return a list 
of nodes that are then pushed into the poseData for processing.

def getNodesOverload(poseObj,rootNode,*args):

	#cast the given rootNode to a metaNode
	metaNode=r9Meta.MetaClass(rootNode)
	
	#catch the currently selected node
	currentSelection=cmds.ls(sl=True,l=True)

	#see if we have a left or right controller selected and switch to the
	#appropriate subMetaSystem
	if cmds.getAttr('%s.mirrorSide' % currentSelection[0])==1:
		filteredNodes=metaNode.L_Arm_System.L_Finger_System.getChildren()
	elif cmds.getAttr('%s.mirrorSide' % currentSelection[0])==2:
		filteredNodes=metaNode.R_Arm_System.R_Finger_System.getChildren()
		
	#modify the actual PoseData object, changing the data to be matched on index
	poseObj.metaPose=False
	poseObj.matchMethod='index'
	
	return filteredNodes


In the most basic case you could just construct a list of nodes
and return that!
================================================================
'''

import Red9.core.Red9_Meta as r9Meta
import maya.cmds as cmds

	
def getNodesOverload(poseObj,rootNode,*args):
	'''
	I'm just using this as a generic call for the two
	main functions below. In this initial example I'm 
	just calling the internal .getNodes() in the poseObj.
	This ensures that even if this file is preset and you've 
	done nothing to it, it will still run the default calls.
	@return: list of nodes to store/load
	'''
	return poseObj.getNodes(rootNode)


#=================================================
# Main calls used internally in the PoseData class
#=================================================

def poseGetNodesLoad(poseObj,rootNode,*args):
	'''
	PoseLoad:
	this is an entry point used to over-load the main getNodes()
	function in the PoseData object. This allows you to modify, on 
	the fly the poseObj itself as poseObj arg is the class instance
	@param poseObj: the actual instance of the PoseData object
	@param nodes: root node passed in from the UI 
	'''
	return getNodesOverload(poseObj,rootNode,*args)
	
def poseGetNodesSave(poseObj,rootNode,*args):
	'''
	PoseSave:
	this is an entry point used to over-load the main getNodes()
	function in the PoseData object. This allows you to modify, on 
	the fly the poseObj itself as poseObj arg is the class instance
	'''
	return getNodesOverload(poseObj,rootNode,*args)
	
def teardown():
	'''
	Not yet used or implemented
	'''
	pass

