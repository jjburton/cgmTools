#=================================================================================================================================================
#=================================================================================================================================================
#	objectFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for finding stuff
#
# ARGUMENTS:
# 	Maya
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru (and good friend) David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#   0.11 - 04/04/2011 - added cvListSimplifier
#
# FUNCTION KEY:
#   1) ????
#   2) ????
#   3) ????
#
#=================================================================================================================================================

import maya.cmds as mc
import maya.mel as mel

from cgm.lib.classes import NameFactory
from cgm.lib import (lists,
                     optionVars,
                     search,
                     attributes,
                     dictionary,
                     rigging,
                     settings,
                     guiFactory)

optionVarTypeDict = {'int':['int','i','integer',1,0],
                     'float':['f','float','fl',1.0,0.0],
                     'string':['string','str','s']}

class OptionVarFactory():
    """ 
    OptionVar Class handler
    
    """
    def __init__(self,varName,varType = 'int'):
        """ 
        Intializes an optionVar class handler
        
        Keyword arguments:
        varName(string) -- name for the optionVar
        varType(string) -- 'int','float','string' (default 'int')
        
        """
        #Default to creation of a var as an int value of 0
        ### input check   
        self.name = varName
        self.form = ''
        self.value = ''
        
        self.update(varType)

    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    def update(self,varType):
        """ 
        If it doesn't exist, makes it. If it does, fill out the data
        """
        
        if not mc.optionVar(exists = self.name):
            for option in optionVarTypeDict.keys():
                if varType in optionVarTypeDict.get(option):
                    self.form = option
                    self.create(self.form)
                    self.value = mc.optionVar(q=self.name)
                    return
            if not self.form:
                return guiFactory.warning("'%s' is not a valid variable type"%varType)  
        
        else:
            self.name = self.name
            dataBuffer = mc.optionVar(q=self.name)
            typeBuffer = search.returnDataType(dataBuffer)
            if typeBuffer == varType:
                self.form = typeBuffer
                self.value = dataBuffer
                return                
            else:
                for option in optionVarTypeDict.keys():
                    if varType in optionVarTypeDict.get(option):
                        self.form = option
                        self.create(self.form)
                        self.value = mc.optionVar(q=self.name)
                        return                        

    def create(self,doType):
        """ 
        If it doesn't exist, makes it. If it does, fill out the data.
        """
        print "Creating '%s' as '%s'"%(self.name,self.form)
            
        if doType == 'int':
            mc.optionVar(iv=(self.name,0))
        elif doType == 'float':
            mc.optionVar(fv=(self.name,0))
        elif doType == 'string':
            mc.optionVar(sv=(self.name,''))
            
  
    def purge(self):
        """ 
        Purge an optionVar from maya
        """
        try:
            mc.optionVar(remove = self.name)
            print mc.optionVar(q=self.name)
            self.name = ''
            self.form = ''
            self.value = ''
            
        except:
            guiFactory.warning("'%s' doesn't exist"%(self.name))
            
            
    def set(self,value):
        if self.form == 'int':
            try:
                mc.optionVar(iv = (self.name,value))
                self.value = value
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'float':
            try:
                mc.optionVar(fv = (self.name,value))
                self.value = value
                
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'string':
            try:
                mc.optionVar(sv = (self.name,str(value)))
                self.value = value
                
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
    def append(self,value):
        if self.form == 'int':
            try:
                mc.optionVar(iva = (self.name,int(value)))
                self.update(self.form)
                guiFactory.warning("'%s' added to '%s'"%(value,self.name))
                
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'float':
            try:
                mc.optionVar(fva = (self.name,value))
                self.update(self.form)
                guiFactory.warning("'%s' added to '%s'"%(value,self.name))
                
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'string':
            try:
                mc.optionVar(sva = (self.name,str(value)))
                self.update(self.form)
                guiFactory.warning("'%s' added to '%s'"%(value,self.name))
                
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))

    def remove(self,value):
        if value in self.value:
            try:         
                i = self.value.index(value)
                mc.optionVar(removeFromArray = (self.name,i))
                self.update(self.form)
                guiFactory.warning("'%s' removed from '%s'"%(value,self.name))
            except:
                guiFactory.warning("'%s' failed to remove '%s'"%(value,self.name))
        else:
            guiFactory.warning("'%s' wasn't found in '%s'"%(value,self.name))
            

                            
    def extend(self,valuesList):
        assert type(valuesList) is list,"'%s' not a list"%(valuesList)
        for v in valuesList:
            print v
            self.append(v)
    
    def toggle(self):
        """
        Toggles an int type variable
        """
        assert self.form == 'int',"'%s' not an int type var"%(self.name)
        
        mc.optionVar(iv = (self.name,not self.value))
        self.value = not self.value
        guiFactory.warning("'%s':%s"%(self.name,self.value))
        
        
        
    def select(self):
        """
        Attempts to select the items of a optionVar buffer
        """
        selectList = []
        if self.value:
            for item in self.value:
                if mc.objExists(item):
                    if '.' in item:
                        buffer = mc.ls(item,o=True)
                        if mc.objExists(buffer[0]):
                            selectList.append(buffer[0])
                    else:
                        selectList.append(item)
                
        if selectList:
            mc.select(selectList)
            
            
    def existCheck(self):
        """
        Attempts to select the items of a optionVar buffer
        """
        bufferList = self.value
        existsList = []
        if bufferList:
            for item in bufferList:
                if mc.objExists(item):
                        existsList.append(item)
                        
        mc.optionVar(clearArray = self.name)
        if existsList:
            existsList = lists.returnListNoDuplicates(existsList)
            self.extend(existsList)
                
                        
                        
        

    
