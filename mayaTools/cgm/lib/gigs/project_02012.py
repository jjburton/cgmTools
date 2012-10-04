#JTDarmRig($name, string $clavicle, string $shoulder, string $elbow, string $wrist, int $numRollJoints, int $leftRight, float $scale, string $world, string $primitive)
#JTDlegRig(string $name, string $hip, string $knee, string $ankle, string $heel,string $ball, int $numRollJoints, int $leftRight, float $scale, string $world, string $primitive, int $pivotOption)
#JTDneckRig(string $name, string $startJoint, string $endJoint, float $scale, string $world, string $primitive)

import maya.cmds as mc
import maya.mel as mel

from cgm.lib import (rigging,
                     lists,
                     joints,
                     curves,
                     search,
                     attributes)

from cgm.lib.classes import SetFactory

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Crowd stuff
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from cgm.lib import (guiFactory,locators)
from cgm.lib.classes import AttrFactory

def ObjectFacesToFolicles():
    try:
	import parentConstraintToSurface
    except:
	"Can't find parentConstraintToSurface"
	
    selection = mc.ls(sl=True) or []
    if not selection:
	return "Nothing selected"
    
    #If we're going, create a return set
    returnSet = SetFactory.SetFactory('folicledLocs','td',True)
    
    # Make some groups
    mLocGroup = mc.group(em=True,name = 'locators_grp')   
    
    number = len(selection)
    returnList = []
    for i,o in enumerate(selection):
	guiFactory.report("On %s. %s of %s"%(o,i,number))
	faceBuffer = "%s.f[4]"%o
	if not mc.objExists(faceBuffer):
	    print "'%s' has no face!"%o
	    
	loc = locators.locMeObject(faceBuffer)
	returnSet.store(loc)	
	mc.select(cl=True)
	mc.select(loc,o)
	parentConstraintToSurface.parentConstraintToSurface()
	
	rigging.doParentReturnName(loc,mLocGroup)
	
    
    follicles = mc.ls(type='follicle')
    mc.select(follicles)
    mc.group(name = 'folicles_grp')

from cgm.lib import search


def getSelectedCubeyRigNameSpaces():
    selection = mc.ls(sl=True) or []
    
    nameSpaces = []
    for o in selection:
	nameSpaces.append( search.returnReferencePrefix(o) )
	
    return lists.returnListNoDuplicates(nameSpaces)   

def randomizeSelectedCubies():
    finalSpaces = getSelectedCubeyRigNameSpaces()
    
    for s in finalSpaces:
	randomizeCubey(s)
    
def randomizeCubey(nameSpace):
    import random

    settingsObject = ('%s:Cubey_masterAnim_settings'%nameSpace)
    
    #reset stuff
    for a in 'Nose','Hair','Beard','BaseballHat','Belt','Buckle','Collar','Suit':
	attributes.doSetAttr(settingsObject,a, 0)
	
    #set it
    if not mc.objExists(settingsObject):
	print "'%s' doesn't exist!"%settingsObject
    attributes.doSetAttr(settingsObject,'Nose', random.randint(1,5))
    attributes.doSetAttr(settingsObject,'Hair', random.randint(0,6))
    beardOptions = [0,1,2,3,4,5,0,0,0,0,0]
    attributes.doSetAttr(settingsObject,'Beard', beardOptions[random.randint(0,9)])
    
    case = random.randint(0,10)

    if case in  [1,5,8]:
	attributes.doSetAttr(settingsObject,'BaseballHat', 1)
	attributes.doSetAttr(settingsObject,'Hair', 0)
    if case in [5,2,6]:
	attributes.doSetAttr(settingsObject,'Belt', 1)
	attributes.doSetAttr(settingsObject,'Buckle', 1)
    if case == 7:
	attributes.doSetAttr(settingsObject,'Suit', 1)
    if case in [9,3]:
	attributes.doSetAttr(settingsObject,'Collar', 1)
	
    #Nose and ears
    options = [.75,.8,.9,1,1]
    noseMult = options[random.randint(0,4)] 
    
    noseControl = ('%s:nose_jnt_anim'%nameSpace)
    attributes.doSetAttr(noseControl,'sx', noseMult)
    attributes.doSetAttr(noseControl,'sy', noseMult)
    attributes.doSetAttr(noseControl,'sz', noseMult)
    
    #eary = 0.513,1.02
    #earZ = 1, 1.857
    earOptionsY = [0.513,.62,.75,.8,1,1.02,1,1]
    earOptionsZ = [.75,1,1.25,1.5,1.8,1,1]
    
    earMultY = earOptionsY[random.randint(0,6)] 
    earMultZ = earOptionsZ[random.randint(0,6)]
    
    earLeftControl = ('%s:ear_l_jnt_anim'%nameSpace)
    earRightControl = ('%s:ear_r_jnt_anim'%nameSpace)
    
    
    attributes.doSetAttr(earLeftControl,'sy', earMultY)
    attributes.doSetAttr(earLeftControl,'sz', earMultZ) 
    
    attributes.doSetAttr(earRightControl,'sy', earMultY)
    attributes.doSetAttr(earRightControl,'sz', earMultZ)    
    
    #Eyes
    #l eye = -0.089,0.132  eye_l_mover_jnt_anim
    earLeftControl = ('%s:eye_l_mover_jnt_anim'%nameSpace)
    earRightControl = ('%s:eye_r_mover_jnt_anim'%nameSpace)
    
    eyeOptions = [-0.089,-.06,-.04,-.02,0,0,0,.025,.04,.06,.13]
    eyeMult = eyeOptions[random.randint(0,10)] 
    
    attributes.doSetAttr(earLeftControl,'tx', eyeMult)
    attributes.doSetAttr(earRightControl,'tx', -eyeMult)       

def randomizeSelectedCubbettes():
    finalSpaces = getSelectedCubeyRigNameSpaces()
    
    for s in finalSpaces:
	randomizeCubette(s)
	
def randomizeCubette(namespace):
    import random
    
    settingsObject = ('%s:Cubey_masterAnim_settings'%namespace)
    
    #reset stuff
    for a in 'Tops','Hair','Bottom','Noses','Belts','ShortSleeves':
	attributes.doSetAttr(settingsObject,a, 0)
	
    attributes.doSetAttr(settingsObject,'RegTop', 1)
	
    #set it
    if not mc.objExists(settingsObject):
	print "'%s' doesn't exist!"%settingsObject
    attributes.doSetAttr(settingsObject,'Tops', random.randint(0,3))
    attributes.doSetAttr(settingsObject,'Hair', random.randint(0,5))
    attributes.doSetAttr(settingsObject,'Bottom', random.randint(0,3))
    attributes.doSetAttr(settingsObject,'Noses', random.randint(1,5))
    
    case = random.randint(0,10)
    if case in [5,2,6]:
	attributes.doSetAttr(settingsObject,'ShortSleeves', 1)
	
	
    #Nose and ears
    options = [.75,.8,.9,1,1]
    noseMult = options[random.randint(0,4)] 
    
    noseControl = ('%s:nose_jnt_anim'%namespace)
    attributes.doSetAttr(noseControl,'sx', noseMult)
    attributes.doSetAttr(noseControl,'sy', noseMult)
    attributes.doSetAttr(noseControl,'sz', noseMult)
    
    #eary = 0.513,1.02
    #earZ = 1, 1.857
    earOptions = [.8,.9,1,1,1,1,1.1,1.2,1.3,1.364]
    
    earMult = earOptions[random.randint(0,9)] 
    
    earLeftControl = ('%s:ear_l_jnt_anim'%namespace)
    earRightControl = ('%s:ear_r_jnt_anim'%namespace)
    
    
    attributes.doSetAttr(earLeftControl,'sx', earMult)
    attributes.doSetAttr(earLeftControl,'sy', earMult) 
    attributes.doSetAttr(earLeftControl,'sz', earMult) 
    
    attributes.doSetAttr(earRightControl,'sx', earMult)    
    attributes.doSetAttr(earRightControl,'sy', earMult)
    attributes.doSetAttr(earRightControl,'sz', earMult)    
    
    #Eyes
    #l eye = -0.089,0.132  eye_l_mover_jnt_anim
    earLeftControl = ('%s:eye_l_mover_jnt_anim'%namespace)
    earRightControl = ('%s:eye_r_mover_jnt_anim'%namespace)
    
    eyeOptions = [-0.089,-.06,-.04,-.02,0,0,0,.025,.04,.06,.13]
    eyeMult = eyeOptions[random.randint(0,10)] 
    
    attributes.doSetAttr(earLeftControl,'tx', eyeMult)
    attributes.doSetAttr(earRightControl,'tx', -eyeMult)  
	
	
def placerLocsToCubey():
    import random
    from cgm.lib import position
    selection = mc.ls(sl=True) or []
    mStable = ['J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/male1.ma',
               'J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/male2.ma',
               'J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/male3.ma',
               'J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/male4.ma',
               'J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/male5.ma',
               'J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/male6.ma']
    fStable = ['J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/female1.ma',
               'J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/female2.ma',
               'J:/Dropbox/MasterCard/Sequences/mc/mc0010/Anim/maya/scenes/cycles/female3.ma']
    
    maleFileCnt = 0
    femaleFileCnt = 0
    maleCnt = 0
    femCnt = 0
    
    length = len(selection)
    for i,loc in enumerate(selection):
	guiFactory.report("On %s of %s"%(i,length))
	
	#Pick a sex
	sexInt = random.randint(0,10)
	sex = 'male'
	if sexInt in [2,3]:
	    sex = 'female'
	    
	guiFactory.report("sex is '%s'"%sex)
	
	#Pick a file
	if sex is 'male':
	    locFile = mStable[maleFileCnt]
	    maleFileCnt +=1
	    maleCnt +=1
	    if not maleFileCnt < len(mStable):
		maleFileCnt = 0
	    locNameSpace = 'male_%s'%maleCnt
	else:
	    locFile = fStable[femaleFileCnt]
	    femaleFileCnt +=1
	    femCnt +=1
	    if not femaleFileCnt < len(fStable):
		femaleFileCnt = 0
	    locNameSpace = 'female_%s'%femCnt
		
	guiFactory.report("File is '%s'"%locFile)
	
	#Import the file
	mc.file(locFile, i = True,namespace = locNameSpace,pr = True, force = True,prompt = False) # prompt means no error message
	buffer =  mc.ls('%s:*'%locNameSpace) 
	
	if not 'RN' in buffer[0]:
	    return guiFactory.warning('Failed to find name space')
	
	splitBuffer = buffer[0].split('RN')
	realLocNameSpace = splitBuffer[0]
	
	#Snap Master constraint group and constrain to loc
	nestedNameSpace = 'male'
	if sex == 'female':
	    nestedNameSpace = 'female'
	    
	snappingObject = ('%s:%s:Cubey_masterAnim_constraint_grp'%(locNameSpace,nestedNameSpace))
	if not mc.objExists(snappingObject):
	    return "Snapping object doesn't exist = '%s'"%snappingObject
	position.moveParentSnap(snappingObject,loc)
	
	masterObject = ('%s:%s:Cubey_masterAnim'%(locNameSpace,nestedNameSpace))
	if not mc.objExists(masterObject):
	    return "Master object doesn't exist = '%s'"%masterObject
	
	mc.parentConstraint(loc,snappingObject, maintainOffset=False)
	if sex == 'male':
	    attributes.doSetAttr(masterObject,'tz',.606)
	attributes.doSetAttr(masterObject,'rz',-90)
	
	#Randomize
	if sex == 'male':
	    randomizeCubey('%s:%s'%(locNameSpace,nestedNameSpace))
	if sex == 'female':
	    randomizeCubette('%s:%s'%(locNameSpace,nestedNameSpace))
		
	
    
	
	

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Vis Toggles
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from cgm.lib import (guiFactory,nodes)
from cgm.lib.classes import AttrFactory
reload(nodes)


def singleObjectVisToggle(obj,chooseAttr = 'switcher', controlObject = None, connectTo = 'visibility'):
    #Make our attr
    a = AttrFactory.AttrFactory(controlObject,chooseAttr,'enum')
    a.setEnum('off:on')


    condNodeTest = attributes.returnDriverObject('%s.%s'%(obj,connectTo))
    if condNodeTest:
	buffer = condNodeTest
    else:
	if mc.objExists('%s_condNode'%obj):
	    mc.delete('%s_condNode'%obj)
	buffer = nodes.createNamedNode('%s_picker'%obj,'condition') #Make our node
    print buffer
    attributes.doSetAttr(buffer,'secondTerm',1)
    attributes.doSetAttr(buffer,'colorIfTrueR',1)
    attributes.doSetAttr(buffer,'colorIfFalseR',0)
    
    a.doConnectOut('%s.firstTerm'%buffer)
    attributes.doConnectAttr('%s.outColorR'%buffer,'%s.%s'%(obj,connectTo))

def groupToConditionNodeSet(group,chooseAttr = 'switcher', controlObject = None, connectTo = 'visibility'):
    """
    Hack job for the gig to make a visibility switcher for all the first level of children of a group
    """
    children = search.returnChildrenObjects(group) #Check for children

    if not children: #If none, break out
	guiFactory("'%s' has no children! Aborted."%group)
	return False
    if controlObject is None:
	controlObject = group
    
    #Make our attr
    a = AttrFactory.AttrFactory(controlObject,chooseAttr,'enum')
    children.insert(0,'none')
    print children
    if len(children) == 2:
	a.setEnum('off:on')
    else:
	a.setEnum(':'.join(children))
    
    for i,c in enumerate(children[1:]):
	print i
	print c
	#see if the node exists
	condNodeTest = attributes.returnDriverObject('%s.%s'%(c,connectTo))
	if condNodeTest:
	    buffer = condNodeTest
	else:
	    if mc.objExists('%s_condNode'%c):
		mc.delete('%s_condNode'%c)
	    buffer = nodes.createNamedNode('%s_picker'%c,'condition') #Make our node
	print buffer
	attributes.doSetAttr(buffer,'secondTerm',i+1)
	attributes.doSetAttr(buffer,'colorIfTrueR',1)
	attributes.doSetAttr(buffer,'colorIfFalseR',0)
	
	a.doConnectOut('%s.firstTerm'%buffer)
	attributes.doConnectAttr('%s.outColorR'%buffer,'%s.%s'%(c,connectTo))
    


spineScale = .25
armScale = .5
legScale = .6
fingerScale = .8

baseName = "cubey"
world = "Cubey_masterAnim"
connect = "cubey_spine_Prim_1"

   
    
    
def rigMasterCardCharater(doRig = True, doSkinIt = True):
    spineChain = []
    jointChains = []
    def skinIt():
	#Skin it
	geoGroupObjects = search.returnAllChildrenObjects('geo_grp',True)
	#Get our group objects
	
	jointChains = getSkinJointChains()

	for i,g in enumerate([u'torso_geoGrp', u'armLeft_geoGrp', u'armRight_geoGrp', u'legLeft_geoGrp', u'legRight_geoGrp']):
	    geoGroupObjects = search.returnAllChildrenObjects(g,True) or []
	
	    toSkin = []
	    for o in geoGroupObjects:
		if search.returnObjectType(o) in ['mesh','nurbsSurface']:
		    toSkin.append(o)
		
	    if toSkin:
		for o in toSkin:
		    toBind = jointChains[i] + [o]
		    mc.skinCluster(toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 10)
	    else:
		print ("'%s' has nothing to skin!"%g)   
		
	
    def orientSkeletonTemplate():
	#First unparent the parts so we can orient properly
	hip = rigging.doParentToWorld('hip_l')
	heel = rigging.doParentToWorld('heel_l')
	clav = rigging.doParentToWorld('clavicle_l')
	palm = rigging.doParentToWorld('palm_l')
	
	spineChain = ['root']
	spineChain.extend(search.returnChildrenJoints('root'))
	for j in spineChain:        
	    joints.orientJoint(j,'xzy','zup')    
	
	hipChain = [hip]
	hipChain.extend(search.returnChildrenJoints(hip))
	for j in hipChain:
	    #joints.orientJoint(j,'xzy','zup')
	    joints.orientJoint(j,'xzy','zup')
	    
	armChain = [clav]
	armChain.extend(search.returnChildrenJoints(clav))
	for j in armChain:
	    joints.orientJoint(j,'xyz','yup')  
	    
	footChain = [heel]
	footChain.extend(search.returnChildrenJoints(heel))
	for j in footChain:
	    #joints.orientJoint(j,'yzx','yup') 
	    #joints.orientJoint(j,'xyz','yup')
	    joints.orientJoint(j,'zyx','yup')
	
	handChain = [palm]
	handChain.extend(search.returnChildrenJoints(palm))
	for j in handChain:
	    joints.orientJoint(j,'xzy','zup') 
		
	#Fix the thumb
	thumbChain = ['thumb1_l']
	thumbChain.extend(search.returnChildrenJoints('thumb1_l'))
	for j in thumbChain:
	    #tweak - taken from Comet's orient 
	    mc.xform(j,r=True,os=True,ra= (-20,0,0))
	    mc.joint(j,e=True,zso = True)
	    mc.makeIdentity(j,apply=True)
	    
	#Fix the Head
	headChain = ['head1']
	headChain.extend(search.returnChildrenJoints('head1'))
	for j in headChain:
	    joints.orientJoint(j,'yzx','zup') 	
	    
	#Reconnect
	rigging.doParentReturnName(hip,'root')
	rigging.doParentReturnName(clav,'spine5')
	rigging.doParentReturnName(heel,'ankle_l')
	rigging.doParentReturnName(palm,'wrist_l')
	
	return spineChain
    
    def getSkinJointChains():
	leftArmChain = ['clavicle_l']
	leftArmChain.extend(search.returnChildrenJoints('clavicle_l'))
	
	rightArmChain = ['clavicle_r']
	rightArmChain.extend(search.returnChildrenJoints('clavicle_r'))	
	
	leftLegChain = ['hip_l']
	leftLegChain.extend(search.returnChildrenJoints('hip_l'))
	
	rightLegChain = ['hip_r']
	rightLegChain.extend(search.returnChildrenJoints('hip_r'))
	
	torsoChain.extend(['clavicle_l','clavicle_r'])
	
	returnList = [torsoChain,leftArmChain,rightArmChain,leftLegChain,rightLegChain]
	return returnList
    
    torsoChain = orientSkeletonTemplate()
    if not doRig:
	return ("Stopped after orientation")
    
    #Get ready for JTD stuff
    mel.eval('source JTDriggingUI;')
    mel.eval('source JTDarmRig;')
    mel.eval('source JTDspineRig;')
    mel.eval('source JTDneckRig;')
    mel.eval('source JTDdynParent;')
    mel.eval('source JTDfingerRig;')    
    
    mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior -searchReplace "_l" "_r" "hip_l";')
    mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior -searchReplace "_l" "_r" "clavicle_l";')
    
    mel.eval('JTDspineRig("%s", "spine1", "spine5", "root", %f, "%s", "");'%(baseName,spineScale,world))
    
    mel.eval('JTDneckRig("%s", "neck1", "head1", %f, "%s", "%s");'%(baseName,spineScale,world,connect))
    
    
    mel.eval('JTDarmRig("%s","clavicle_l","shoulder_l","elbow_l","wrist_l", 3, 1, %f, "%s", "%s");'%(baseName,armScale,world,connect))
    mel.eval('JTDarmRig("%s","clavicle_r","shoulder_r","elbow_r","wrist_r", 3, 2, %f, "%s", "%s");'%(baseName,armScale,world,connect))
    
    
    mel.eval('JTDlegRig("%s","hip_l","knee_l","ankle_l","heel_l","ball_l", 3, 1, %f, "%s", "%s", 2);'%(baseName,legScale,world,connect))
    mel.eval('JTDlegRig("%s","hip_r","knee_r","ankle_r","heel_r","ball_r", 3, 2, %f, "%s", "%s", 2);'%(baseName,legScale,world,connect))
    
    #Fingers Left
    mel.eval('JTDfingerRig("wrist_l","index1_l","index2_l","index3_l","index4_l", 1, 1, 1, 0, 1, "%s", %f);'%(baseName,fingerScale))
    mel.eval('JTDfingerRig("wrist_l","fingers1_l","fingers2_l","fingers3_l","fingers4_l", 1, 1, 4, 0, 1, "%s", %f);'%(baseName,fingerScale))
    
    mel.eval('JTDfingerRig("wrist_l","","thumb1_l","thumb2_l","thumb3_l", 1, 1, 0, 1, 1, "%s", %f);'%(baseName,fingerScale))
    
    #Fingers Right
    mel.eval('JTDfingerRig("wrist_r","index1_r","index2_r","index3_r","index4_r", 1, 1, 1, 0, 2, "%s", %f);'%(baseName,fingerScale))
    mel.eval('JTDfingerRig("wrist_r","fingers1_r","fingers2_r","fingers3_r","fingers4_r", 1, 1, 4, 0, 2, "%s", %f);'%(baseName,fingerScale))
    
    mel.eval('JTDfingerRig("wrist_r","","thumb1_r","thumb2_r","thumb3_r", 1, 1, 0, 1, 2, "%s", %f);'%(baseName,fingerScale))
    
    #new stuff
    #Head scale
    attributes.doSetLockHideKeyableAttr('cubey_neck_IK_Cntrl',lock = False,visible=True,keyable=True,channels = ['sx','sy','sz'])
    mc.setAttr('cubey_neck_IK_Cntrl.sx', keyable = True)
    mc.setAttr('cubey_neck_IK_Cntrl.sy', keyable = True)
    mc.setAttr('cubey_neck_IK_Cntrl.sz', keyable = True)
    
    mc.scaleConstraint('cubey_neck_IK_Cntrl','head1')
    
    #Sets and Coloring
    leftArmSetObjects = [u'rig_clavicle_l_IK_Cntrl', u'rig_shoulder_l_twist', u'rig_shoulder_l_Bendy', u'rig_elbow_l_Bendy', u'rig_clavicle_l_FK_Cntrl', u'cubey_finger_Cntrl0_l', u'rig_wrist_l_FK', u'rig_wrist_l_SW', u'rig_shoulder_l_FK', u'rig_elbow_l_FK', u'cubey_arm_IK_Cntrl_l', u'rig_wrist_l_GimbleCntrl_l', u'cubey_arm_PV_Cntrl_l'] # 
    rightArmSetObjects = [u'rig_clavicle_r_IK_Cntrl', u'rig_shoulder_r_twist', u'rig_shoulder_r_Bendy', u'rig_elbow_r_Bendy', u'rig_clavicle_r_FK_Cntrl', u'cubey_finger_Cntrl0_r', u'rig_wrist_r_FK', u'rig_wrist_r_SW', u'rig_shoulder_r_FK', u'rig_elbow_r_FK', u'cubey_arm_IK_Cntrl_r', u'rig_wrist_r_GimbleCntrl_r', u'cubey_arm_PV_Cntrl_r'] # 
    
    centerSetObjects = [u'rig_spine1_Shoulders', u'rig_spine1_Hips', u'cubey_spine_Root', u'rig_spine1FK3', u'rig_spine1FK2', u'rig_spine1FK1', u'cubey_neck_FK_Cntrl', u'cubey_neck_IK_Cntrl']
    
    leftLegSetObjects = [u'rig_ball_l_FK', u'rig_ankle_l_SW', u'rig_hip_l_Bendy', u'rig_knee_l_FK', u'rig_ankle_l_FK', u'rig_hip_l_FK', u'rig_knee_l_Bendy', u'rig_hip_l_twist', u'cubey_leg_GimbleCntrl_l', u'cubey_leg_IKleg_Cntrl_l', u'cubey_leg_PV_Cntrl_l']
    rightLegSetObjects = [u'rig_ball_r_FK', u'rig_ankle_r_SW', u'rig_hip_r_Bendy', u'rig_knee_r_FK', u'rig_ankle_r_FK', u'rig_hip_r_FK', u'rig_knee_r_Bendy', u'rig_hip_r_twist', u'cubey_leg_GimbleCntrl_r', u'cubey_leg_IKleg_Cntrl_r', u'cubey_leg_PV_Cntrl_r']
    
    lArmSet = SetFactory.SetFactory('armLeft','animation',True)
    for o in leftArmSetObjects:
	lArmSet.store(o)
	#color
	curves.setCurveColorByName(o,'blueBright')        
	
    rArmSet = SetFactory.SetFactory('armRight','animation',True)
    for o in rightArmSetObjects:
	rArmSet.store(o)
	#color
	curves.setCurveColorByName(o,'redBright')
	
    
    torsoSet = SetFactory.SetFactory('torso','animation',True)
    for o in centerSetObjects:
	torsoSet.store(o)  
	curves.setCurveColorByName(o,'yellow')
	
	
    lLegSet = SetFactory.SetFactory('legLeft','animation',True)
    for o in leftLegSetObjects:
	lLegSet.store(o)
	curves.setCurveColorByName(o,'blueBright')
	
    rLegSet = SetFactory.SetFactory('legRight','animation',True)
    for o in rightLegSetObjects:
	rLegSet.store(o)    
	curves.setCurveColorByName(o,'redBright')
    
    bindJoints = search.returnAllChildrenObjects('root')
    bindJoints.append('root')    
    skinJointsSet = SetFactory.SetFactory('skinJoints','td',True)
    for o in bindJoints:
	if mc.ls(o,type='joint'):
	    skinJointsSet.store(o)    

    #Set of all sets    
    allSet = SetFactory.SetFactory('all','animation',True)
    allSet.store(rLegSet.nameLong)
    allSet.store(lLegSet.nameLong)
    allSet.store(torsoSet.nameLong)
    allSet.store(lArmSet.nameLong)
    allSet.store(rArmSet.nameLong)
    
    
    #Skin!
    if not doSkinIt:
	return ("Stopped after riggning...no skinning")
    skinIt()
    

	

def rigMasterCardCharaterOLD():
    spineChain = []
    jointChains = []
    def skinIt():
	#Skin it
	geoGroupObjects = search.returnAllChildrenObjects('geo_grp',True)
	#Get our group objects
	
	jointChains = getSkinJointChains()

	for i,g in enumerate([u'torso_geoGrp', u'armLeft_geoGrp', u'armRight_geoGrp', u'legLeft_geoGrp', u'legRight_geoGrp']):
	    geoGroupObjects = search.returnAllChildrenObjects(g,True)	
	
	    toSkin = []
	    for o in geoGroupObjects:
		if search.returnObjectType(o) in ['mesh','nurbsSurface']:
		    toSkin.append(o)
		
	    if toSkin:
		for o in toSkin:
		    toBind = jointChains[i] + [o]
		    mc.skinCluster(toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 10,polySmoothness = 3)
	    else:
		print ("'%s' has nothing to skin!"%g)   
		
	
    def orientSkeletonTemplate():
	#First unparent the parts so we can orient properly
	hip = rigging.doParentToWorld('hip_l')
	heel = rigging.doParentToWorld('heel_l')
	clav = rigging.doParentToWorld('clavicle_l')
	palm = rigging.doParentToWorld('palm_l')
	
	spineChain = ['root']
	spineChain.extend(search.returnChildrenJoints('root'))
	for j in spineChain:        
	    joints.orientJoint(j,'xzy','zup')    
	
	hipChain = [hip]
	hipChain.extend(search.returnChildrenJoints(hip))
	for j in hipChain:
	    joints.orientJoint(j,'xzy','zup')
	    
	armChain = [clav]
	armChain.extend(search.returnChildrenJoints(clav))
	for j in armChain:
	    joints.orientJoint(j,'xyz','yup')  
	    
	footChain = [heel]
	footChain.extend(search.returnChildrenJoints(heel))
	for j in footChain:
	    joints.orientJoint(j,'yzx','yup')    
	
	handChain = [palm]
	handChain.extend(search.returnChildrenJoints(palm))
	for j in handChain:
	    joints.orientJoint(j,'xzy','zup') 
		
	#Fix the thumb
	thumbChain = ['thumb1_l']
	thumbChain.extend(search.returnChildrenJoints('thumb1_l'))
	for j in thumbChain:
	    #tweak - taken from Comet's orient 
	    mc.xform(j,r=True,os=True,ra= (-20,0,0))
	    mc.joint(j,e=True,zso = True)
	    mc.makeIdentity(j,apply=True)
	    
	#Fix the Head
	headChain = ['head1']
	headChain.extend(search.returnChildrenJoints('head1'))
	for j in headChain:
	    joints.orientJoint(j,'yzx','zup') 	
	    
	#Reconnect
	rigging.doParentReturnName(hip,'root')
	rigging.doParentReturnName(clav,'spine5')
	rigging.doParentReturnName(heel,'ankle_l')
	rigging.doParentReturnName(palm,'wrist_l')
	
	return spineChain
    
    def getSkinJointChains():
	leftArmChain = ['clavicle_l']
	leftArmChain.extend(search.returnChildrenJoints('clavicle_l'))
	
	rightArmChain = ['clavicle_r']
	rightArmChain.extend(search.returnChildrenJoints('clavicle_r'))	
	
	leftLegChain = ['hip_l']
	leftLegChain.extend(search.returnChildrenJoints('hip_l'))
	
	rightLegChain = ['hip_r']
	rightLegChain.extend(search.returnChildrenJoints('hip_r'))
	
	torsoChain.extend(['clavicle_l','clavicle_r'])
	
	returnList = [torsoChain,leftArmChain,rightArmChain,leftLegChain,rightLegChain]
	return returnList
    
    torsoChain = orientSkeletonTemplate()
    
    #Get ready for JTD stuff
    mel.eval('source JTDriggingUI;')
    mel.eval('source JTDarmRig;')
    mel.eval('source JTDspineRig;')
    mel.eval('source JTDneckRig;')
    mel.eval('source JTDdynParent;')
    mel.eval('source JTDfingerRig;')    
    
    mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior -searchReplace "_l" "_r" "hip_l";')
    mel.eval('mirrorJoint -mirrorYZ -mirrorBehavior -searchReplace "_l" "_r" "clavicle_l";')
      
    mel.eval('JTDspineRig("%s", "spine1", "spine5", "root", %f, "%s", "");'%(baseName,spineScale,world))
    
    mel.eval('JTDneckRig("%s", "neck1", "head1", %f, "%s", "%s");'%(baseName,spineScale,world,connect))
    
    
    mel.eval('JTDarmRig("%s","clavicle_l","shoulder_l","elbow_l","wrist_l", 3, 1, %f, "%s", "%s");'%(baseName,armScale,world,connect))
    mel.eval('JTDarmRig("%s","clavicle_r","shoulder_r","elbow_r","wrist_r", 3, 2, %f, "%s", "%s");'%(baseName,armScale,world,connect))
    
    
    mel.eval('JTDlegRig("%s","hip_l","knee_l","ankle_l","heel_l","ball_l", 3, 1, %f, "%s", "%s", 2);'%(baseName,legScale,world,connect))
    mel.eval('JTDlegRig("%s","hip_r","knee_r","ankle_r","heel_r","ball_r", 3, 2, %f, "%s", "%s", 2);'%(baseName,legScale,world,connect))
    
    #Fingers Left
    mel.eval('JTDfingerRig("wrist_l","","index1_l","index2_l","index3_l", 1, 1, 1, 0, 1, "%s", %f);'%(baseName,fingerScale))
    mel.eval('JTDfingerRig("wrist_l","","fingers1_l","fingers2_l","fingers3_l", 1, 1, 4, 0, 1, "%s", %f);'%(baseName,fingerScale))
    
    mel.eval('JTDfingerRig("wrist_l","","thumb1_l","thumb2_l","thumb3_l", 1, 1, 0, 1, 1, "%s", %f);'%(baseName,fingerScale))
    
    #Fingers Right
    mel.eval('JTDfingerRig("wrist_r","","index1_r","index2_r","index3_r", 1, 1, 1, 0, 2, "%s", %f);'%(baseName,fingerScale))
    mel.eval('JTDfingerRig("wrist_r","","fingers1_r","fingers2_r","fingers3_r", 1, 1, 4, 0, 2, "%s", %f);'%(baseName,fingerScale))
    
    mel.eval('JTDfingerRig("wrist_r","","thumb1_r","thumb2_r","thumb3_r", 1, 1, 0, 1, 2, "%s", %f);'%(baseName,fingerScale))
    
    #new stuff
    #Head scale
    attributes.doSetLockHideKeyableAttr('cubey_neck_IK_Cntrl',lock = False,visible=True,keyable=True,channels = ['sx','sy','sz'])
    mc.setAttr('cubey_neck_IK_Cntrl.sx', keyable = True)
    mc.setAttr('cubey_neck_IK_Cntrl.sy', keyable = True)
    mc.setAttr('cubey_neck_IK_Cntrl.sz', keyable = True)
    
    mc.scaleConstraint('cubey_neck_IK_Cntrl','head1')
    
    #Sets and Coloring
    leftArmSetObjects = [u'rig_clavicle_l_IK_Cntrl', u'rig_shoulder_l_twist', u'rig_shoulder_l_Bendy', u'rig_elbow_l_Bendy', u'rig_clavicle_l_FK_Cntrl', u'cubey_finger_Cntrl0_l', u'rig_wrist_l_FK', u'rig_wrist_l_SW', u'rig_shoulder_l_FK', u'rig_elbow_l_FK', u'cubey_arm_IK_Cntrl_l', u'rig_wrist_l_GimbleCntrl_l', u'cubey_arm_PV_Cntrl_l'] # 
    rightArmSetObjects = [u'rig_clavicle_r_IK_Cntrl', u'rig_shoulder_r_twist', u'rig_shoulder_r_Bendy', u'rig_elbow_r_Bendy', u'rig_clavicle_r_FK_Cntrl', u'cubey_finger_Cntrl0_r', u'rig_wrist_r_FK', u'rig_wrist_r_SW', u'rig_shoulder_r_FK', u'rig_elbow_r_FK', u'cubey_arm_IK_Cntrl_r', u'rig_wrist_r_GimbleCntrl_r', u'cubey_arm_PV_Cntrl_r'] # 
    
    centerSetObjects = [u'rig_spine1_Shoulders', u'rig_spine1_Hips', u'cubey_spine_Root', u'rig_spine1FK3', u'rig_spine1FK2', u'rig_spine1FK1', u'cubey_neck_FK_Cntrl', u'cubey_neck_IK_Cntrl']
    
    leftLegSetObjects = [u'rig_ball_l_FK', u'rig_ankle_l_SW', u'rig_hip_l_Bendy', u'rig_knee_l_FK', u'rig_ankle_l_FK', u'rig_hip_l_FK', u'rig_knee_l_Bendy', u'rig_hip_l_twist', u'cubey_leg_GimbleCntrl_l', u'cubey_leg_IKleg_Cntrl_l', u'cubey_leg_PV_Cntrl_l']
    rightLegSetObjects = [u'rig_ball_r_FK', u'rig_ankle_r_SW', u'rig_hip_r_Bendy', u'rig_knee_r_FK', u'rig_ankle_r_FK', u'rig_hip_r_FK', u'rig_knee_r_Bendy', u'rig_hip_r_twist', u'cubey_leg_GimbleCntrl_r', u'cubey_leg_IKleg_Cntrl_r', u'cubey_leg_PV_Cntrl_r']
    
    lArmSet = SetFactory.SetFactory('armLeft','animation',True)
    for o in leftArmSetObjects:
	lArmSet.store(o)
	#color
	curves.setCurveColorByName(o,'blueBright')        
	
    rArmSet = SetFactory.SetFactory('armRight','animation',True)
    for o in rightArmSetObjects:
	rArmSet.store(o)
	#color
	curves.setCurveColorByName(o,'redBright')
	
    
    torsoSet = SetFactory.SetFactory('torso','animation',True)
    for o in centerSetObjects:
	torsoSet.store(o)  
	curves.setCurveColorByName(o,'yellow')
	
	
    lLegSet = SetFactory.SetFactory('legLeft','animation',True)
    for o in leftLegSetObjects:
	lLegSet.store(o)
	curves.setCurveColorByName(o,'blueBright')
	
    rLegSet = SetFactory.SetFactory('legRight','animation',True)
    for o in rightLegSetObjects:
	rLegSet.store(o)    
	curves.setCurveColorByName(o,'redBright')
    
    bindJoints = search.returnAllChildrenObjects('root')
    bindJoints.append('root')    
    skinJointsSet = SetFactory.SetFactory('skinJoints','td',True)
    for o in bindJoints:
	if mc.ls(o,type='joint'):
	    skinJointsSet.store(o)    

    #Set of all sets    
    allSet = SetFactory.SetFactory('all','animation',True)
    allSet.store(rLegSet.nameLong)
    allSet.store(lLegSet.nameLong)
    allSet.store(torsoSet.nameLong)
    allSet.store(lArmSet.nameLong)
    allSet.store(rArmSet.nameLong)
    
    
    #Skin!
    skinIt()
    

