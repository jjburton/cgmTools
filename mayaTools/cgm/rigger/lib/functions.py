"""
cgmLimb
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
import maya.cmds as mc
from cgm.lib.classes import NameFactory
from cgm.lib.classes.AttrFactory import *
from cgm.lib.classes.ObjectFactory import *

from cgm.lib import (search,
                     distance,
                     names,
                     attributes,
                     names,
                     rigging,
                     constraints,
                     curves,
                     dictionary,
                     settings,
                     lists,
                     modules,
                     position,
                     cgmMath,
                     controlBuilder)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module and Puppet axis settings
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
def doSetAimAxis(self,i):
    """
    Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
    Then Up, and Out is last.
    
    """
    assert i < 6,"%i isn't a viable aim axis integer"%i
    
    self.optionAimAxis.set(i)
    if self.optionUpAxis.get() == self.optionAimAxis.get():
        doSetUpAxis(self,i)
    if self.optionOutAxis.get() == self.optionAimAxis.get():
        doSetOutAxis(self,i)
        
    return True
    
def doSetUpAxis(self,i):
    """
    Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
    Then Up, and Out is last.
    
    """        
    assert i < 6,"%i isn't a viable up axis integer"%i
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
                doSetOutAxis(self,i)
                guiFactory.warning("Setting conflict. Changed out axis to '%s'"%dictionary.axisDirectionsByString[i])                    
                break
    return True        
    
    
def doSetOutAxis(self,i):
    assert i < 6,"%i isn't a viable aim axis integer"%i
    
    if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
        self.optionOutAxis.set(i)
    else:
        axisBuffer = range(6)
        axisBuffer.remove(self.optionAimAxis.get())
        axisBuffer.remove(self.optionUpAxis.get())
        self.optionOutAxis.set(axisBuffer[0]) 
        guiFactory.warning("Setting conflict. Changed out axis to '%s'"%dictionary.axisDirectionsByString[ axisBuffer[0] ])                    



def copyAxisOptions(self,target):
    target.optionAimAxis
    target.optionUpAxis
    target.optionOutAxis
    self.optionAimAxis
    self.optionUpAxis
    self.optionOutAxis 
    
    doSetAimAxis(self,target.optionAimAxis.get())
    doSetUpAxis(self,target.optionUpAxis.get())
    doSetOutAxis(self,target.optionOutAxis.get())
    
    
    
