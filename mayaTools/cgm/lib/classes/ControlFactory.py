#=================================================================================================================================================
#=================================================================================================================================================
#	ControlFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Child class to cgm.lib.classes.ObjectFactory for control specific wrapped functions
#
# Keyword arguments:
# 	Maya
#
# AUTHOR:
# 	Josh Burton - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 10.11.2012- created
#
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel
from cgm.lib.classes import ObjectFactory
reload(ObjectFactory)
from cgm.lib.classes import AttrFactory
reload(AttrFactory)

from cgm.lib.classes.ObjectFactory import *
from cgm.lib.classes.AttrFactory import *

from cgm.lib import (lists,
                     search,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)
reload(dictionary)

class ControlFactory(ObjectFactory):
    """ 
    Initialized a maya object as a class obj
    """
    def __init__(self,obj='',makeAimable = True, controlRO = False):
        """ 
        Asserts objects existance and that it has a transform. Then initializes. 

        Keyword arguments:
        obj(string)
	makeAimable(bool) -- whether to set up aim controls

        """
	self.aimable = False
	self.stateControlRO = False	
	
        ### input check
        ObjectFactory.__init__(self,obj=obj)


	if makeAimable or mc.objExists("%s.%s"%(self.nameLong,'axisAim')):
	    self.verifyAimControls()
	    
	if controlRO or mc.objExists("%s.%s"%(self.nameLong,'setRo')):
	    self.verifyRotateOrderControl()
		
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # ObjectAxis
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
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
