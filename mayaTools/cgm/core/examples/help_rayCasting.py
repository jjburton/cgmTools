"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for using the concept of rayCasting. We'll be looking at rayCaster,clickMesh,and control casting
================================================================
"""
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.lib import rayCaster as RayCast
from cgm.core.lib import shapeCaster as ShapeCast
from cgm.lib import curves,locators
#==============================================================================================
#>> rayCasting
#==============================================================================================
from cgm.core import cgm_Meta as cgmMeta
import maya.cmds as mc
import copy

#>>Setup ==================================================================================== 
'''
We need to create some objects to do our initial tests with 
'''
if not mc.objExists('nurbsSphere1'):mc.sphere(r=10)
if not mc.objExists('pSphere1'):mc.polySphere(r=10)
str_mesh = 'pSphere1'
str_surface = 'nurbsSphere1'

#Make a curve from our library so we can more sensibly see our cast direction.We'll be casting from z+
mi_aimObj = cgmMeta.cgmObject(curves.createControlCurve('arrowSingleFat3d',5,'y-'))

#Aim
#mc.delete(mc.aimConstraint('pSphere1', mi_loc.mNode))

#This is gonna be our dict reporter
def report_dict(d):
    for k in d.keys():
        print ("# {0} | {1}".format(k,d[k]))    
#===============================================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>RayCast Functions =============================================================================================
#Gonna start with some functions found in cgm.core.lib.rayCaster

#findMeshIntersectionFromObjectAxis ==============================================================
'''
This function is for basic casting from actual objects in maya. 
They call on the raw cast functions but it's easier to work with stuff you can 
see when starting out
'''
str_castTo = str_mesh #Link our mesh as our current object
#reload(RayCast)

#1) Do our first cast --------------------------------------------------------------------------------
mi_aimObj.tz = 20
RayCast.findMeshIntersectionFromObjectAxis(str_castTo,mi_aimObj.mNode)
# Result: {} # 
#This is gonna return us an empty result because our aim object is not in the sphere and not aiming at, let's aim it...

#2) Cast it again --------------------------------------------------------------------------------
mi_aimObj.ry = 180#Flip our aim object
RayCast.findMeshIntersectionFromObjectAxis(str_castTo,mi_aimObj.mNode)
# Result: {'source': [0.0, 0.0, 20.0], 'uv': [0.7000001072883606, 0.5], 'hit': [0.0, -9.4730781774936761e-17, 10.000000953674316]} # 
#Now, you'll see we're getting our return dict. We return to a dict because we want a more info

#3) Using that info to do something helpful. Let's cast one more time and store it to a holder --------------------------------------------------------------------------------
d_return = RayCast.findMeshIntersectionFromObjectAxis(str_castTo,mi_aimObj.mNode)

#4) Just for kicks, let's report that info to get used to that little function --------------------------------------------------------------------------------
report_dict(d_return)

#5) Let's do something useful with that info...
mc.spaceLocator(p = d_return.get('hit'),name = "hit_single")
#So, now we have a single loc positioned at our point, however, we have another option on the 
mc.spaceLocator(p = d_return.get('source'),name = "source_single")
#here we see our cast point of origin

#6) What if we wanna have more than one hit returned as the ray goes through the object...let's change a flag
d_return = RayCast.findMeshIntersectionFromObjectAxis(str_castTo,mi_aimObj.mNode,singleReturn = False)
#Then let's loc those
for i,hit_point in enumerate(d_return.get('hits')):
    mc.spaceLocator(p = hit_point,name = "hit_{0}".format(i))

#7) Does it work with nurbs?
str_castTo = str_surface#Link to the surface and let's go back and do the same 1-6 above
#It does, awesome

#7) Here's another sample to play with. Move the cast object around within the sphere and try some of these
for axis in ['x+','x-','z+','z-']:
    locators.doLocPos(RayCast.findMeshIntersectionFromObjectAxis(str_castTo,mi_aimObj.mNode,axis = axis)['hit'])
#===============================================================================================

#findMeshMidPointFromObject ==============================================================
'''
This function is for positioning objects in mesh iteratively 
'''

#1) Let's start by moving our caster object
mi_aimObj.translate = 6,2.5,1.5

#2) So let's start by playig with the caster
RayCast.findMeshMidPointFromObject(str_castTo,mi_aimObj.mNode, axisToCheck = ['x','z'],maxIterations=5)
# Result: [0.18749999999999992, 1.9396939318297912, -0.48360811199787312] # 
#So we get back a position in space..

#3) Let's feed that to our translate
mi_aimObj.translate = RayCast.findMeshMidPointFromObject(str_castTo,mi_aimObj.mNode, axisToCheck = ['x','z'],maxIterations=5)

#3) Play with moving the mi_aimObj around and reruning step 3. Play with the options as well

#=================================================================================================================
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>ShapeCast Functions =============================================================================================
#We're gonna look at some more functions which are one of the practical applications of rayCasting

#createMeshSliceCurve ==============================================================
'''
This is a curve lathing function. There are a lot of options so let's delve in. 
'''
mi_aimObj.translate = 0,0,0#...let's reset 
mi_aimObj.rotate = 0,0,0#...let's reset 
str_castTo = str_mesh #...Link our mesh as our current cast to object

reload(ShapeCast)
reload(cgmGeneral)

#We're gonna setup up some options here so we can easily change them 
latheAxis = 'z'
aimAxis = 'y+'
points = 12
curveDegree = 3
minRotate = None
maxRotate = None
rotateRange = None
posOffset = 0
markHits = False
rotateBank = None
closedCurve = True
maxDistance = 1000
initialRotate = 0
offsetMode = 'vector'
midMeshCast = False#...This mode will force the cast point to be centered in the axis to check. It uses the function we looked at in the previous function
l_specifiedRotates = None
closestInRange = True
returnDict = False
axisToCheck = ['x','y']

#We're gonna feed all these options in so we can play with stuff
ShapeCast.createMeshSliceCurve(str_castTo,mi_aimObj,latheAxis,aimAxis,points,curveDegree,minRotate,maxRotate,rotateRange,posOffset,markHits,rotateBank,closedCurve,maxDistance,initialRotate,offsetMode,midMeshCast,l_specifiedRotates,closestInRange,returnDict,axisToCheck)

#Let's start by changing the markHits
markHits = True#... then rerun our command

#You're gonna get all the hit points marked along with the step by step build curves of each cast
#Delete all that...

markHits = False
posOffset = [0,0,2]#...We're gonna set our vector offset and then rerun the caster
#Note, now our curve has off offset  from the surface, the default offsetmode is 'vector' which aims back to the cast point. Let's try the other mode
offsetMode = 'normal'#...then run again. The difference will probably not be much. This will be more apparent with more complicated surfaces. The normal mode uses the normal of the closes face as the offset vector

#Let's take a loot at specified rotates
l_specifiedRotates = [5,20,44]#...And recast...only those rotate settings will be used. It looks a little odd so...

closedCurve = False#And recast one more time. There that's a little better. We can use this for specific arcs to lathe

#What happens when we have holes in our mesh...select the faces from half the sphere, and let's reset the options using the kw section above
maxDistance = 50#...We're gonna set this so you don't have to zoom out so far in the next bit...
#Recast...
#You'll see that our function wants to make a whole curve so when holes are encountered, it picks the point at the maximum distance along that cast vector and uses that point

#There's lots of other options but that's enough for this first pass on learning these functions....I'll finish when I find another chunk of time

#===============================================================================================


#=================================================================================================================
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>









