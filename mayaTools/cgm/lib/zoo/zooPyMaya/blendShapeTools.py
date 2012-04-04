import maya.OpenMaya as om
import maya.cmds as cmd
from math import sqrt

class BlendShape():
	def __init__( self, nodeName ):
		self.name = nodeName
		self.__minRowLength = 5
	def __repr__( self ):
		return self.targets
	def __str__( self ):
		return str(self.__repr__())
	def __add__( self, value ):
		'''value should be a string or a list of strings (object names)'''
		if isinstance(value,str):
			self.append(value)
		elif isinstance(value,list) or isinstance(value,tuple):
			for val in value:
				self.__add__(val)
		else:
			raise ArithmeticError("only supports adding strings (name of a known target object) or lists/tuples of strings")

		return self
	def __sub__( self, value ):
		'''value should be a string or a list of strings (object names)'''
		if isinstance(value,str):
			self.pop(value)
		elif isinstance(value,list) or isinstance(value,tuple):
			for val in value:
				self.__add__(val)
		else:
			raise ArithmeticError("only supports subtracting strings (name of a known target object) or lists/tuples of strings")

		return self
	def __getattr__( self, attr ):
		if attr in self.targets:
			return cmd.getAttr(self.name +'.'+ attr)
		#else:
		#	raise AttributeError("the %s target doesn't exist"%(attr,))
	def __getitem__( self, idx ):
		return cmd.getAttr(self.name +'.w['+ idx +']')
	def append( self, shapeNameToAdd=None, name=None ):
		'''deals with adding a target of name shape to the blendshape'''
		if shapeNameToAdd == None:
			#in this case the user wants to append the current shape of the object being driven to the target list
			dupe = cmd.duplicate(self.obj)[0]
			shapeNameToAdd = dupe
			self.zeroTweak()

		if cmd.objExists(shapeNameToAdd):
			if name != None:
				shapeNameToAdd = cmd.rename(shapeNameToAdd,name)

			#make sure the name doesn't clash with an existing target name - otherwise maya will bork
			while shapeNameToAdd in self.targets:
				shapeNameToAdd += 'Dupe'

			numTgts = len(self.targets)
			cmd.blendShape(self.name,edit=True,target=(self.obj,numTgts,shapeNameToAdd,1.0))
			self.collapse(shapeNameToAdd)
			self.zeroTweak()

			return shapeNameToAdd
	def expand( self, targetToExpand ):
		'''makes all the target shapes appear as objects in the scene - objects are placed to the right
		(assuming +z is facing forward and +y up) of the base object placed a bounding box width apart.
		row length is at least 5, but for large numbers of targets it takes the square root of the target
		count'''
		SEPARATION_X = 1.3
		SEPARATION_Y = 1.3

		expanded = self.expanded
		targets = self.targets
		num = len(expanded)
		if targetToExpand in targets:
			if self.isExpanded(targetToExpand):
				return self.getExpandedName(targetToExpand)

			obj = self.obj
			maxRowLength = max(self.__minRowLength,int(sqrt(len(targets))))

			#get the size of the object so we can place them away from the original
			bbox = cmd.getAttr(obj +'.bbmn')[0] + cmd.getAttr(obj +'.bbmx')[0]
			size = ( (bbox[3]-bbox[0])*SEPARATION_X, (bbox[4]-bbox[1])*SEPARATION_Y )
			x = num%maxRowLength + 1
			y = int(num/maxRowLength) * -1

			index = self.getTargetIdx(targetToExpand)
			self.setTargetWeight(targetToExpand,1,crossfade=True)
			dupe = cmd.duplicate(obj)[0]
			dupe = cmd.rename(dupe,targetToExpand)
			cmd.connectAttr(dupe +'.worldMesh[0]', self.name +'.inputTarget[0].inputTargetGroup['+ str(index) +'].inputTargetItem[6000].inputGeomTarget')

			#now move the objects away from the base so they're easier to visualize
			cmd.move(size[0]*x,size[1]*y,0,dupe,moveX=True,moveY=True,relative=True)

			return dupe
		else:
			raise AttributeError("target doesn't exist")
	def expandAll( self ):
		'''expands all targets - convenience really.  this is horribly inefficient, but unless the target count
		grows into the multi thousands this shouldn't become a problem...'''
		initSelection = cmd.ls(selection=True)
		targets = self.targets
		weights = self.weights
		dupes = []
		for target in targets:
			weight = cmd.getAttr(self.name +'.'+ target)
			dupes.append(self.expand(target))
			self.setTargetWeight(target,weight,False)

		if initSelection: cmd.select(initSelection)
		return dupes
	def __getExpanded( self ):
		expanded = cmd.listConnections(self.name +'.it',destination=False)
		if expanded: return expanded
		else: return []
	expanded = property(__getExpanded)
	def getExpandedName( self, target ):
		index = self.getTargetIdx(target)
		expanded = cmd.listConnections(self.name +'.it[0].inputTargetGroup['+ str(index) +'].inputTargetItem[6000].inputGeomTarget',destination=False)
		if expanded: return expanded[0]
		else: return []
	def isExpanded( self, target=None ):
		'''returns whether a given target has been expanded or not.  if no target is given this will return
		whether ANY target has been expanded'''
		cons = self.__getExpanded()
		if target:
			if self.getExpandedName(target) in cons:
				return True
		else:
			if cons: return True
		return False
	def collapse( self, targetToCollapse ):
		'''collapses the given target object so it's no longer visible in the scene'''
		if self.isExpanded(targetToCollapse):
			expandedName = self.getExpandedName(targetToCollapse)
			cmd.delete(expandedName)
	def collapseAll( self ):
		for target in self.targets:
			self.collapse(target)
	def pop( self, targetToRemove ):
		'''pops the given shape name or shape index out of the blendShape node - creating the object in
		the scene, and removing it from the blendShape node'''
		targets = self.targets
		indicies = self.indicies
		if targetToRemove in targets:
			blendIdx = self.getTargetIdx(targetToRemove)
			shape = self.expand(targetToRemove)
			cmd.blendShape(self.name,edit=True,remove=True,target=(self.obj,blendIdx,shape,1.0))

			return shape
		else:
			raise AttributeError("target doesn't exist")
	def remove( self, targetToRemove ):
		cmd.delete(self.pop(targetToRemove))
	def update( self, targetToUpdate ):
		'''overwrites the target name given with the current shape of self.name'''
		targets = self.targets
		if targetToUpdate in targets:
			nameIdx = targets.index(targetToUpdate)
			baseDupe = cmd.duplicate(self.obj)[0]
			self.zeroTweak()
			newTarget = self.expand(targetToUpdate)
			cmd.select((baseDupe,newTarget))
			tmpBlendNode = cmd.blendShape()[0]
			cmd.setAttr(tmpBlendNode +'.w[0]',1)
			cmd.delete(newTarget,constructionHistory=True)
			cmd.delete(baseDupe)
			self.collapse(targetToUpdate)
			cmd.select(self.obj)
		else:
			raise AttributeError("target doesn't exist")
	def zeroTweak( self ):
		'''deals with zeroing out the tweak node values that have accumulated on a base mesh'''
		tweakNode = cmd.ls(cmd.listHistory(self.shape),type='tweak')[0]
		totalVertCount = cmd.getAttr(self.shape +'.vrts',size=True)
		for n in range(totalVertCount):
			cmd.setAttr(tweakNode +'.vlist[0].vt['+ str(n) +']',0,0,0)
	def __getTargetNameandIndicies( self ):
		'''returns a list of the target names on the blendshape.  both the index list and
		the name list are guaranteed to be in the correct order'''
		indicies = []
		aliasList = cmd.aliasAttr(self.name,query=True)
		if aliasList == None: return []
		for n in range(1,len(aliasList),2):
			idx = int(aliasList[n][7:][:-1])
			indicies.append(idx)

		indicies.sort()
		names = [None]*len(indicies)  #build the name array of the correct size
		for n in range(0,len(aliasList),2):
			curNameIdx = int(aliasList[n+1][7:][:-1])
			for i in range(len(indicies)):
				if curNameIdx == indicies[i]:
					names[i] = aliasList[n]

		return names,indicies
	def __getTargetNames( self ):
		'''returns a list of the target names on the blendshape'''
		names,indicies = self.__getTargetNameandIndicies()
		return names
	targets = property(__getTargetNames)
	def __getTargetWeights( self ):
		'''returns a list of the target names on the blendshape'''
		return cmd.getAttr(self.name +'.w')[0]
	weights = property(__getTargetWeights)
	def __getIndicies( self ):
		'''returns a list of the target names on the blendshape'''
		names,indicies = self.__getTargetNameandIndicies()
		return indicies
	indicies = property(__getIndicies)
	def getTargetIdx( self, target ):
		'''given a target name this method will return its index in the weight attribute'''
		indicies = []
		aliasList = cmd.aliasAttr(self.name,query=True)
		if aliasList == None:
			raise Exception( "not aliasAttr found on %s"%(self.name,))

		for n in range(0,len(aliasList),2):
			if aliasList[n] == target:
				idx = aliasList[n+1][7:][:-1]
				return int(idx)

		raise AttributeError("target doesn't exist")
	def __getObject( self ):
		return cmd.listRelatives(self.__getShape(),parent=True)[0]
	obj = property(__getObject)
	def __getShape( self ):
		return cmd.ls(cmd.listHistory(self.name +'.outputGeometry',future=True),type='mesh')[0]
	shape = property(__getShape)
	def rename( self, oldName, newName ):
		'''will rename a blend shape target - if the target doesn't exist, the method does nothing...'''
		names = self.targets
		aliasList = cmd.aliasAttr(self.name,query=True)
		if oldName in names:
			idx = aliasList.index(oldName)
			aliasList[idx] = newName
			for n in range(1,len(aliasList),2): aliasList[n] = self.name +'.'+ aliasList[n]

			#now remove all the alias'
			for name in names: cmd.aliasAttr(self.name +'.'+ name,remove=True)

			#finally rebuild the alias'
			cmdStr = 'aliasAttr ' + ' '.join(aliasList) +';'
			maya.mel.eval(cmdStr)
	def setTargetWeight( self, target, weight, additive=False, crossfade=False ):
		inititalWeight = cmd.getAttr(self.name +'.'+ target)
		if target in self.targets:
			#print 'data:',target,weight,additive,crossfade
			cmd.setAttr(self.name +'.'+ target,weight)
			if crossfade:
				pct = abs(1-weight) / 1
				idx = self.targets.index(target)
				others = self.targets[:]
				others.pop(idx)
				for other in others:
					otherWeight = abs(cmd.getAttr(self.name +'.'+ other))
					cmd.setAttr(self.name +'.'+ other,min(0,otherWeight*pct))
		else:
			raise AttributeError("target doesn't exist")
	def setAllWeights( self, weight=0 ):
		targets = self.targets
		for index in self.indicies:
			self.setTargetWeight(targets[index],weight,False)
	def propagateTweaks( self ):
		'''propagates the data currently in the tweak node to all target objects - this is useful when large
		changes to a basemesh need to be made across all targets.  NOTE: this is only possible if targets
		are expanded...'''
		tweakNode = cmd.ls(cmd.listHistory(self.shape),type='tweak')[0]
		self.collapseAll()
		self.expandAll()
		self.zeroTweak()
		self.collapseAll()
		#need to connect the tweak node up to targets...
	def deleteHistory( self ):
		'''does a collapse history without destroying blendshape data - this essentially allows you do change
		topology on a blendshape setup easily'''
		self.collapseAll() #make sure everything is collapsed
		newTargets = self.expandAll() #do an expand to ensure all the targets have the same topology as the base mesh

		#now we just need to delete the history and rebuild the blendshape setup
		obj = self.obj
		cmd.delete(obj,constructionHistory=True)
		newTargets += [obj]
		self.name = cmd.blendShape(newTargets)[0]
		self.collapseAll()
	def setWeightApi( self, target, weight ):
		'''this only exists because its not undoable - which strangely enough is useful - see vBlendShapeManager.mel->doSlideCmd() for details'''
		sTmp = om.MSelectionList()
		sTmp.add(self.name)
		idx = self.getTargetIdx(target)
		blendShapeObj = om.MObject()
		sTmp.getDependNode(0,blendShapeObj)
		blendFn = om.MFnDependencyNode(blendShapeObj)
		weightPG = om.MPlug(blendFn.findPlug("w"))
		targetPG = om.MPlug(weightPG.elementByPhysicalIndex(idx))
		targetPG.setFloat(weight)


class BlendShapePV(BlendShape):
	def __init__( self, nodeName ):
		BlendShape.__init__(self,nodeName)
		cmd.loadPlugin('blendTools',quiet=True)
		self.falloffWeights = []
	def setAllSliders( self, weight ):
		for target in self.targets:
			BlendShape.setTargetWeight( self, target, weight )
	def setTargetWeight( self, target, weight, additive=False, crossfade=False, falloff=0, selection=None ):
		'''deals with setting the weight map for a named shape'''
		targets = self.targets
		indicies = self.indicies
		if target in targets:
			idx = self.getTargetIdx(target)

			#determine the default selection to use
			if selection == None:
				sel = cmd.ls(selection=True)
				if sel: selection = cmd.polyListComponentConversion(sel,toVertex=True)
				else: selection = self.obj +'.vtx[*]'
			if selection == '*': selection = self.obj +'.vtx[*]'
			#print 'data:',target,weight,falloff,additive,crossfade,selection
			#cmd.blendPerVert(selection,node=self.name,target=idx,weight=weight,falloff=falloff,additive=additive,crossfade=crossfade)
			cmd.applyFalloffArray(n=self.name,t=tgtIdx,w=weight,add=additive,x=crossfade,undo=True,l=self.falloffWeights)
		else:
			raise AttributeError("target doesn't exist")
	def setAllWeights( self, weight=0 ):
		targets = self.targets
		for target in targets:
			self.setTargetWeight(target,weight)
	def generateFalloffList( self, falloff ):
		maya.mel.eval('$g_vertFallOffWeights = `getFalloffArray -f %f`;'%falloff)
		#self.falloffWeights = cmd.getFalloffArray(f=falloff)
	def setWeightApi( self, target, weight, additive=False, crossfade=False ):
		'''uses the current falloff weight list'''
		if not self.falloffWeights: return  #if no falloff weight map has been generated, bail
		tgtIdx = self.targets.index(target)
		#cmd.applyFalloffArray(node=self.name,target=tgtIdx,w=weight,add=additive,x=crossfade,l=self.falloffWeights)
		addStr,xStr = '',''
		if additive: addStr = '-add'
		if crossfade: xStr = '-x'
		maya.mel.eval('applyFalloffArray -n %s -t %d -w %f %s %s -l $g_vertFallOffWeights;')%( self.name,tgtIdx,weight,addStr,xStr)


def getBlendFromObject( object ):
	blendNodes = cmd.ls(cmd.listHistory(object),type='blendShape')
	if blendNodes != None:
		return blendNodes[0]


def clamp( value, min=0, max=1):
	if value<min: return min
	if value>max: return max
	return value


#end
