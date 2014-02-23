import maya.cmds as mc
import copy
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as om
from zooPyMaya import apiExtensions
from cgm.core import cgm_General as cgmGeneral
from cgm.lib import (locators,
                     dictionary,
                     cgmMath,
                     lists,
                     geo,
                     distance)
import os

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#unit testing
def ut_rayCasterSurfaceFuncCls(surface, raySource, rayDir, maxDistance = 1000):
	assert type('surface') in [str], "surface is not a string!"
	assert type('raySource') in [int, float], "raySource is not int or float!"
	assert type('rayDir') in [int, float], "rayDir is not int or float!"
	assert type('maxDistance') in [int, float], "maxDistance is not int or float!"

def rayCasterSurfaceFuncCls(*args, **kws):
			
	class fncWrap(cgmGeneral.cgmFuncCls):
		'''
		This is rayCasterSurface funcCls
		'''

		def __init__(self, *args, **kws):
			super(fncWrap, self).__init__(*args, **kws)
			self._str_funcName = 'rayCasterSurfaceFuncCls'                     
			self._l_ARGS_KWS_DEFAULTS = [{'kw':'surface',"default":'',"argType":'str','help':"currently nurbs surface only"},
                                   {'kw':'raySource',"default":[0,0,0],"argType":'double3','help':"point in world space"},
                                   {'kw':'rayDir',"default":[0,0,0],"argType":'double3','help':"world space vector"},
                                   {'kw':'maxDistance', "default":1000,"argType":'float','help':"maxDistance"},
                                   {'kw':'obj',"default":'',"argType":'string','help':"an object"},
                                   {'kw':'axis',"default":'z+',"argType":'string','help':"object's axis"},
                                   {'kw':'vector',"default":False,"argType":'bool','help':"object's vector"},
                                   {'kw':'singleReturn',"default":True,"argType":'bool','help':"singleReturn"},
                                   {'kw':'axisToCheck',"default":['x','z'],"argType":'list','help':"axisToCheck"},
                                   {'kw':'maxIterations',"default":10,"argType":'float','help':"maxIterations"},
                                   {'kw':'pierceDepth',"default":4,"argType":'float','help':"maxIterations"}]      
			self.__dataBind__(*args, **kws)
			surface = self.d_kws['surface']
			raySource = self.d_kws['raySource']
			rayDir = self.d_kws['rayDir']
			maxDistance = self.d_kws['maxDistance']
							
			self.l_funcSteps = [{'step':'findSurfaceIntersections','call':self.findSurfaceIntersections()},
	                        	{'step':'findSurfaceIntersectionFromObjectAxis','call':self.findSurfaceIntersectionFromObjectAxis()},
	                        	{'step':'findSurfaceMidPointFromObject','call':self.findSurfaceMidPointFromObject()},
	                        	{'step':'findFurthestPointInRangeFromObject','call':self.findFurthestPointInRangeFromObject()}]
	   
						
			# Functions	

			
		def findSurfaceIntersections(self):
			'''
			Return the pierced points on a surface from a raySource and rayDir
			'''		
							 
			try:
				self._str_funcName = 'findSurfaceIntersections'
				log.debug(">>> %s >> "%self._str_funcName + "="*75)
				if len(mc.ls(surface))>1:
					raise StandardError,"findSurfaceIntersections>>> More than one surface named: %s"%surface
				self.selectionList = om.MSelectionList()
				self.selectionList.add(surface)
				self.surfacePath = om.MDagPath()
				self.selectionList.getDagPath(0, self.surfacePath)
				self.surfaceFn = om.MFnNurbsSurface(self.surfacePath)
				raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
				self.rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])
				self.hitPoints = om.MFloatPointArray()
	            	
				#Set up a variable for each remaining parameter in the
				#MFnNurbsSurface::allIntersections call. We could have supplied these as
				#literal values in the call, but this makes the example more readable.
				self.sortIds = False
				
				#maxDist
				self.raySourceVector = om.MVector(raySource[0], raySource[1], raySource[2])
				self.hitPointVector = om.MVector(hitPoint[0], hitPoint[1], hitPoint[2])
				self.distVector = om.MVector.length(raySourceVector - hitPointVector)
				self.maxDist = om.MDistance.internalToUI(distVector)
				log.debug("maxDist: %s"%maxDist)
				
				#other variables
				self.paramU = None
				self.paramV = None
				self.ignoreTrimBoundaries = False
				self.kMFnNurbsEpsilon = [0,0,0]
				self.ReturnStatus = None

					            	
				#Get the closest intersection.
				self.gotHit = self.surfaceFn.closestPoint(raySource, self.rayDirection, self.paramU, self.paramV, 
				self.ignoreTrimBoundaries, self.kMFnNurbsEpsilon, om.MSpace.kObject, self.ReturnStatus)
								
				#Return the intersection as a Python list.
				if self.gotHit:
					self.returnDict = {}
					self.hitList = []
					self.uvList = []
					for i in range( self.hitPoints.length() ):
						self.hitList.append( [self.hitPoints[i].x, self.hitPoints[i].y, self.hitPoints[i].z])
						self.hitMPoint = om.MPoint(self.hitPoints[i])
						self.pArray = [0.0,0.0]
						self.x1 = om.MScriptUtil()
						self.x1.createFromList(pArray, 2)
						self.uvPoint = x1.asFloat2Ptr()
						self.uvSet = None
						self.uvReturn = self.surfaceFn.getParamAtPoint(self.hitMPoint,self.uvPoint,self.paramU,self.paramV, self.ignoreTrimBoundaries, om.MSpace.kObject, self.kMFnNurbsEpsilon)
									
						self.uValue = om.MScriptUtil.getFloat2ArrayItem(self.uvPoint, 0, 0) or False
						self.vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
						self.uvList.append([self.uValue,self.vValue])
									
						self.returnDict = {'hits':self.hitList,'source':[raySource.x,raySource.y,raySource.z],'uvs':self.uvList}
						return self.returnDict
				else:
					return None
			except StandardError,error:
				log.error(">>> %s >> surface: %s | raysource: %s | rayDir %s | error: %s"%(_str_funcName,surface,raySource,rayDir,error))
				return None
			            	
		def findSurfaceIntersectionFromObjectAxis(surface, obj, axis = 'z+', vector = False, maxDistance = 1000, singleReturn = True):            	
			'''
			Find surface intersections for an object's axis
			'''
			try:
				self._str_funcName = 'findSurfaceIntersectionFromObjectAxis'
				log.debug(">>> %s >> "%self._str_funcName + "="*75)
				if len(mc.ls(surface))>1:
					raise StandardError,"findSurfaceIntersectionFromObjectAxis>>> More than one surface named: %s"%surface                	
				if not vector or type(vector) not in [list,tuple]:
					self.d_matrixVectorIndices = {'x':[0,1,2],'y': [4,5,6],'z' : [8,9,10]}
					self.matrix = mc.xform(obj, q=True,  matrix=True, worldSpace=True)
					
					#>>> Figure out our vector
					if axis not in dictionary.stringToVectorDict.keys():
						log.error("findSurfaceIntersectionFromObjectAxis axis arg not valid: '%s'"%axis)
						return False 
					if list(axis)[0] not in self.d_matrixVectorIndices.keys():
						log.error("findSurfaceIntersectionFromObjectAxis axis arg not in d_matrixVectorIndices: '%s'"%axis)
						return False
					vector = [self.matrix[i] for i in self.d_matrixVectorIndices.get(list(axis)[0])]
					if list(axis)[1] == '-':
						for i,v in enumerate(vector):
							vector[i]=-v
				if singleReturn:
					return findSurfaceIntersection(surface, distance.returnWorldSpacePosition(obj), rayDir=vector, maxDistance = maxDistance)
				else:
					return findSurfaceIntersections(surface, distance.returnWorldSpacePosition(obj), rayDir=vector, maxDistance = maxDistance)
			except StandardError,error:
				log.error(">>> %s >> surface: %s | obj: %s | axis %s | vector: %s | error: %s"%(self._str_funcName,surface,obj,axis,vector,error))
				return None 	

		def findSurfaceMidPointFromObject(surface,obj,axisToCheck = ['x','z'], vector = False, maxDistance = 1000, maxIterations = 10,**kws):            	
			'''
			findSurfaceMidPointFromObject
			'''
			try:
				self._str_funcName = 'findSurfaceMidPointFromObject'
				log.debug(">>> %s >> "%self._str_funcName + "="*75)
				if len(mc.ls(surface))>1:
					raise StandardError,"findSurfaceMidPointFromObject>>> More than one surface named: %s"%surface      
				if type(axisToCheck) not in [list,tuple]:axisToCheck=[axisToCheck]
				axis = ['x','y','z']
				for a in axisToCheck :
					if a not in axis:
						raise StandardError,"findSurfaceMidPointFromObject>>> Not a valid axis : %s not in ['x','y','z']"%axisToCheck
				self.l_lastPos = []
				self.loc = locators.locMeObjectStandAlone(obj)
				for i in range(maxIterations):
					self.l_positions = []
					for a in axisToCheck:
						log.debug("firing: %s"%a)
						self.d_posReturn = findSurfaceIntersectionFromObjectAxis(surface, self.loc, axis = '%s+'%a,vector=vector,maxDistance = maxDistance) 
						self.d_negReturn = findSurfaceIntersectionFromObjectAxis(surface, self.loc, axis = '%s-'%a,vector=vector,maxDistance = maxDistance) 
						if 'hit' in self.d_posReturn.keys() and self.d_negReturn.keys():
							self.l_pos = [self.d_posReturn.get('hit'),self.d_negReturn.get('hit')]
							self.pos = distance.returnAveragePointPosition(self.l_pos)
							self.l_positions.append(self.pos)
					if len(self.l_positions) == 1:
						self.l_pos =  self.l_positions[0]
					else:
						self.l_pos =  distance.returnAveragePointPosition(self.l_positions)
					if self.l_lastPos:self.dif = cgmMath.mag( cgmMath.list_subtract(self.l_pos,self.l_lastPos) )
					else:self.dif = 'No last'
					log.debug("findSurfaceMidPointFromObject>>> Step : %s | dif: %s | last: %s | pos: %s "%(i,self.dif,self.l_lastPos,self.l_pos))
					if self.l_lastPos and cgmMath.isVectorEquivalent(self.l_lastPos,self.l_pos,2):
						log.debug("findSurfaceMidPointFromObject>>> Match found step: %s"%(i))
						mc.delete(self.loc)
						return self.l_pos 
					mc.move(self.l_pos[0],self.l_pos[1],self.l_pos[2],self.loc,ws=True)
					self.l_lastPos = self.l_pos#If we get to here, add the current	
				mc.delete(self.loc)	
				return self.l_pos
			except StandardError,error:
				for kw in [surface,obj,axisToCheck,vector,maxDistance,maxIterations]:
					log.debug("%s"%kw)
				raise StandardError, "%s >> error: %s"%(self._str_funcName,error)										
							
							
		def findFurthestPointInRangeFromObject(surface,obj,axis = 'z+', pierceDepth = 4, vector = False, maxDistance = 1000):            	
			'''
			Find the furthest point in range on an axis. Useful for getting to the outershell of a surface
			'''
			try:
				self._str_funcName = 'findFurthestPointInRangeFromObject'
				log.debug(">>> %s >> "%self._str_funcName + "="*75)
				if len(mc.ls(surface))>1:
					raise StandardError,"findFurthestPointInRangeFromObject>>> More than one surface named: %s"%surface      							
				#>>>First cast to get our initial range
				self.d_firstcast = findSurfaceIntersectionFromObjectAxis(surface, obj, axis = axis, vector=vector, maxDistance = maxDistance)	
				if not self.d_firstcast.get('hit'):
					raise StandardError,"findFurthestPointInRangeFromObject>>> first cast failed to hit"	
				self.baseDistance = distance.returnDistanceBetweenPoints(distance.returnWorldSpacePosition(obj),self.d_firstcast['hit'])						
				log.debug("findFurthestPointInRangeFromObject>>>baseDistance: %s"%self.baseDistance)				
				self.castDistance = self.baseDistance + pierceDepth
				log.debug("findFurthestPointInRangeFromObject>>>castDistance: %s"%castDistance)
				self.l_positions = []
				self.d_castReturn = findSurfaceIntersectionFromObjectAxis(surface, obj, axis=axis, maxDistance = castDistance, singleReturn=False) or {}
				log.debug("2nd castReturn: %s"%self.d_castReturn)
				if self.d_castReturn.get('hits'):
					self.closestPoint = distance.returnFurthestPoint(distance.returnWorldSpacePosition(obj),self.d_castReturn.get('hits')) or False	
					self.d_castReturn['hit'] = self.closestPoint	
				return self.d_castReturn	
			except StandardError,error:
				for kw in [surface,obj,axis,pierceDepth,vector,maxDistance]:
					log.debug("%s"%kw)
				raise StandardError, "%s >> error: %s"%(self._str_funcName,error)							           	    
	return fncWrap(*args, **kws).go()

rayCasterSurfaceFuncCls(reportTimes = 1)
rayCasterSurfaceFuncCls(printHelp = 1)
rayCasterSurfaceFuncCls(reportShow = 1)
rayCasterSurfaceFuncCls(reportEnv = 1)