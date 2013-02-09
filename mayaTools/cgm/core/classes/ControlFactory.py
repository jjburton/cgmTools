"""
------------------------------------------
ControlFactory: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Class Factory for 
================================================================
"""
# From Python =============================================================
import copy
import re

#TEMP
import cgm.core
cgm.core._reload()
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General
from Red9.core import Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib import (lists,
                     search,
                     curves,#tmp
                     modules,#tmp
                     distance,#tmp
                     controlBuilder,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)

class cgmMasterControl(cgmMeta.cgmObject):
    """
    Make a master control curve
    """
    def __init__(self,*args,**kws):
        """Constructor"""				
        #>>>Keyword args
        super(cgmMasterControl, self).__init__(*args,**kws)
	
        log.debug(">>> cgmMasterControl.__init__")
	if kws:log.info("kws: %s"%str(kws))
	if args:log.debug("args: %s"%str(args)) 	
   
        if not self.isReferenced():   
            if not self.verify(*args,**kws):
                raise StandardError,"Failed!"	
	
    @r9General.Timer	
    def verify(self,*args,**kws):
	#Check for shapes, if not, build
	self.color =  modules.returnSettingsData('colorMaster',True)

	#>>> Attributes
	if kws and 'name' in kws.keys():
	    self.addAttr('cgmName', kws.get('name'), attrType = 'string')
	    
	self.addAttr('cgmType','controlMaster',attrType = 'string')
	self.addAttr('cgmType','controlMaster',attrType = 'string')
	self.addAttr('axisAim',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=2, keyable = False, hidden=True)
	self.addAttr('axisUp',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=1, keyable = False, hidden=True)
	self.addAttr('axisOut',attrType = 'enum', enumName= 'x+:y+:z+:x-:y-:z-',initialValue=0, keyable = False, hidden=True)
	self.addAttr('setRO',attrType = 'enum', enumName= 'xyz:yzx:zxy:xzy:yxz:zyx',initialValue=0, keyable = True, hidden=False)
	attributes.doConnectAttr('%s.setRO'%self.mNode,'%s.rotateOrder'%self.mNode,True)

	self.addAttr('controlVis', attrType = 'messageSimple',lock=True)
	self.addAttr('visControl', attrType = 'bool',keyable = False,initialValue= 1)
	
	self.addAttr('controlSettings', attrType = 'messageSimple',lock=True)
	self.addAttr('settingsControl', attrType = 'bool',keyable = False,initialValue= 1)
	
	#Connect and Lock the scale stuff
	attributes.doConnectAttr(('%s.scaleY'%self.mNode),('%s.scaleX'%self.mNode),True)
	attributes.doConnectAttr(('%s.scaleY'%self.mNode),('%s.scaleZ'%self.mNode),True)
	cgmMeta.cgmAttr(self,'scaleX',lock=True,hidden=True)
	cgmMeta.cgmAttr(self,'scaleZ',lock=True,hidden=True)
	yAttr = cgmMeta.cgmAttr(self,'scaleY')
	yAttr.p_nameAlias = 'masterScale'
	
	#=====================================================================
	#>>> Curves!
	#=====================================================================
	#>>> Master curves
	if not self.getShapes() or len(self.getShapes())<3:
	    log.info("Need to build shapes")
	    self.rebuildControlCurve(**kws)
	    
	#======================
	#>>> Sub controls
	visControl = attributes.returnMessageObject(self.mNode,'controlVis')
	if not mc.objExists( visControl ):
	    log.info('Creating visControl')
	    buffer = controlBuilder.childControlMaker(self.mNode, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 135, controls = ['controlVisibility'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
	    i_c = cgmMeta.cgmObject(buffer.get('controlVisibility'))
	    i_c.addAttr('mClass','cgmObject')
	    i_c.doName()	
	    curves.setCurveColorByName(i_c.mNode,self.color[0])#Set the color
	    self.controlVis = i_c.mNode #Link it
	    
	    attributes.doConnectAttr(('%s.visControl'%self.mNode),('%s.v'%i_c.mNode),True)
	
	#Vis control attrs
	self.controlVis.addAttr('controls', attrType = 'bool',keyable = False,initialValue= 1)
	self.controlVis.addAttr('subControls', attrType = 'bool',keyable = False,initialValue= 1)
	self.controlVis.addAttr('Rig', attrType = 'bool',keyable = False,initialValue= 1)
	
	#>>> Settings Control
	settingsControl = attributes.returnMessageObject(self.mNode,'controlSettings')
	if not mc.objExists( settingsControl ):
	    log.info('Creating settingsControl')
	    buffer = controlBuilder.childControlMaker(self.mNode, baseAim = [0,1,0], baseUp = [0,0,-1], offset = 225, controls = ['controlSettings'], mode = ['incremental',90],distanceMultiplier = .8, zeroGroups = True,lockHide = True)
	    i_c = cgmMeta.cgmObject(buffer.get('controlSettings'))
	    i_c.addAttr('mClass','cgmObject')
	    i_c.doName()	
	    curves.setCurveColorByName(i_c.mNode,self.color[0])#Set the color	    
	    self.controlSettings = i_c.mNode #Link it	
	    
	    attributes.doConnectAttr(('%s.settingsControl'%self.mNode),('%s.v'%i_c.mNode),True)
	

	self.doName()
	return True
    
    @r9General.Timer
    def rebuildControlCurve(self, size = None,font = None,**kws):
	"""
	Rebuild the master control curve
	"""
	log.debug('>>> rebuildControlCurve')
	shapes = self.getShapes()
	
	#>>> Figure out the control size 	
	if size == None:#
	    if shapes:
		absSize =  distance.returnAbsoluteSizeCurve(self.mNode)
		size = max(absSize)		
	    else:size = 125
	#>>> Figure out font	
	if font == None:#
	    if kws and 'font' in kws.keys():font = kws.get('font')		
	    else:font = 'arial'
	#>>> Delete shapes
	if shapes:
	    for s in shapes:mc.delete(s)	
		
	#>>> Build the new
	i_o = cgmMeta.cgmObject( curves.createControlCurve('masterAnim',size))#Create and initialize
	curves.setCurveColorByName( i_o.mNode,self.color[0] )
	curves.setCurveColorByName( i_o.getShapes()[1],self.color[1] )
	
	#>>> Build the text curve if cgmName exists
	if self.hasAttr('cgmName'):
	    rootShapes = i_o.getShapes()#Get the shapes
	    nameScaleBuffer = distance.returnAbsoluteSizeCurve(rootShapes[1])#Get the scale
	    nameScale = max(nameScaleBuffer) * .8#Get the new scale
	    masterText = curves.createTextCurveObject(self.cgmName,size=nameScale,font=font)
	    curves.setCurveColorByName(masterText,self.color[0])#Set the color
	    mc.setAttr((masterText+'.rx'), -90)#Rotate the curve
	    curves.parentShapeInPlace(self.mNode,masterText)#Shape parent it
	    mc.delete(masterText)
	    
	#>>>Shape parent it
	curves.parentShapeInPlace(self.mNode,i_o.mNode)
	mc.delete(i_o.mNode)
	
	self.doName()
	
    
    
class go(object):
    """ 
    Control Factory for 
    """
    def __init__(self,node = '',makeAimable = True, controlRO = False):
        """ 
        Asserts objects existance and that it has a transform. Then initializes. 

        Keyword arguments:
        obj(string)
	makeAimable(bool) -- whether to set up aim controls

        """
	self.i_object = cgmMeta.cgmObject(node)
	self.mirrorObject = False
	
	"""
	self.aimable = False
	self.stateControlRO = False	


	if makeAimable or mc.objExists("%s.%s"%(self.nameLong,'axisAim')):
	    self.verifyAimControls()
	    
	if controlRO or mc.objExists("%s.%s"%(self.nameLong,'setRo')):
	    self.verifyRotateOrderControl()
	"""	
    #======================================================================
    # Mirroring
    #======================================================================
    @r9General.Timer
    def isMirrorable(self):
	attrs = ['mirrorSide','mirrorIndex','mirrorAxis','cgmMirrorMatch']
	shortName = self.i_object.getShortName()
	for a in attrs:
	    if not self.i_object.hasAttr(a):
		log.warning("'%s' lacks attr: '%s'"%(shortName,a))
		return False
	if not self.i_object.getMessage('cgmMirrorMatch'):
	    log.warning("'%s' lacks mirrorTarget"%(shortName))	    
	    return False
	
	self.mirrorObject = self.i_object.getMessage('cgmMirrorMatch')[0]
	return True
    
    def doMirrorMe(self):
	if not self.isMirrorable():
	    return False
	
	i_mirror = r9Anim.MirrorHierarchy(self.i_object.mNode,)
	i_mirror.mirrorPairData(self.i_object.mNode,self.mirrorObject,'')
	
    def doPushToMirrorObject2(self,method='Anim'):
        if not self.isMirrorable():
            return False
        log.info(self.i_object.mNode)
        log.info(self.mirrorObject)
	
        i_mirrorSystem = r9Anim.MirrorHierarchy([self.i_object.mNode,self.mirrorObject])
	#i_mirrorSystem=r9Anim.MirrorHierarchy()
	i_mirrorSystem.makeSymmetrical(self.i_object.mNode,self.mirrorObject)
        

    def doPushToMirrorObject(self,method='Anim'):
        if not self.isMirrorable():
            return False
        
        i_mirrorSystem = r9Anim.MirrorHierarchy([self.i_object.mNode,self.mirrorObject])
        
        if method=='Anim':
            transferCall= r9Anim.AnimFunctions().copyKeys
            inverseCall = r9Anim.AnimFunctions.inverseAnimChannels
        else:
            transferCall= r9Anim.AnimFunctions().copyAttributes
            inverseCall = r9Anim.AnimFunctions.inverseAttributes
        
        transferCall([self.i_object.mNode,self.mirrorObject])
        #inverse the values
        inverseCall(self.mirrorObject,i_mirrorSystem.getMirrorAxis(self.mirrorObject))

        i_mirrorSystem.objs = [self.i_object.mNode,self.mirrorObject]#Overload as it was erroring out
   
    
class  OLDSTUFF():
    def verifyAimControls(self, keyable = False, hidden=True, locked = False):
	"""
	Adds necessary components for aiming
	
	"""
	self.optionAimAxis = AttrFactory(self,'axisAim','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=2, keyable = keyable, lock = locked, hidden = hidden) 
	self.optionUpAxis = AttrFactory(self,'axisUp','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=1, keyable = keyable, lock = locked, hidden = hidden) 
	self.optionOutAxis = AttrFactory(self,'axisOut','enum',enum = 'x+:y+:z+:x-:y-:z-',initialValue=0, keyable = keyable, lock = locked, hidden = hidden)         
	
	self.aimable = True
		    
    def doSetAimAxis(self,i):
        """
        Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
        Then Up, and Out is last.
        
        """
        assert i < 6,"%i isn't a viable aim axis integer"%i
	assert self.aimable,"'%s' lacks this attribute"%self.nameShort
        
        self.optionAimAxis.set(i)
        if self.optionUpAxis.get() == self.optionAimAxis.get():
            self.doSetUpAxis(i)
        if self.optionOutAxis.get() == self.optionAimAxis.get():
            self.doSetOutAxis(i)
            
        return True
        
    def doSetUpAxis(self,i):
        """
        Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
        Then Up, and Out is last.
        
        """        
        assert i < 6,"%i isn't a viable up axis integer"%i
	assert self.aimable,"'%s' lacks this attribute"%self.nameShort
	
        axisBuffer = range(6)
        axisBuffer.remove(self.optionAimAxis.get())
        
        if i != self.optionAimAxis.get():
            self.optionUpAxis.set(i)  
        else:
            self.optionUpAxis.set(axisBuffer[0]) 
            guiFactory.warning("Aim axis has '%s'. Changed up axis to '%s'. Change aim setting if you want this seeting"%(dictionary.axisDirectionsByString[self.optionAimAxis.get()],dictionary.axisDirectionsByString[self.optionUpAxis.get()]))                  
            axisBuffer.remove(axisBuffer[0])
            
        if self.optionOutAxis.get() in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
            for i in axisBuffer:
                if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
                    self.doSetOutAxis(i)
                    guiFactory.warning("Setting conflict. Changed out axis to '%s'"%dictionary.axisDirectionsByString[i])                    
                    break
        return True        

    def doSetOutAxis(self,i):
        assert i < 6,"%i isn't a viable aim axis integer"%i
	assert self.aimable,"'%s' lacks this attribute"%self.nameShort	
        
        if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
            self.optionOutAxis.set(i)
        else:
            axisBuffer = range(6)
            axisBuffer.remove(self.optionAimAxis.get())
            axisBuffer.remove(self.optionUpAxis.get())
            self.optionOutAxis.set(axisBuffer[0]) 
            guiFactory.warning("Setting conflict. Changed out axis to '%s'"%dictionary.axisDirectionsByString[ axisBuffer[0] ])                    

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # RotateOrder
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     
    def verifyRotateOrderControl(self):
	assert self.transform,"'%s' has no transform"%self.nameShort	
	initialValue = attributes.doGetAttr(self.nameLong,'rotateOrder')
	try:
	    self.RotateOrderControl = AttrFactory(self,'setRO','enum',enum = 'xyz:yzx:zxy:xzy:yxz:zyx',initialValue=initialValue) 
	except:
	    raise StandardError("Failed to add rotate order control")
	
	self.stateControlRO == True
	self.RotateOrderControl.doConnectOut(self.nameShort+'.rotateOrder')
