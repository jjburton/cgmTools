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
    def __init__(self,varName,varType = None,value = None, defaultValue = None):
        """ 
        Intializes an optionVar class handler
        
        Keyword arguments:
        varName(string) -- name for the optionVar
        varType(string) -- 'int','float','string' (default 'int')
        value() -- will attempt to set the optionVar with the value
        defaultValue() -- will ONLY use if the optionVar doesn't exist
        
        """
        #Default to creation of a var as an int value of 0
        ### input check   
        self.name = varName
        self.form = ''
        self.value = ''
        
        #>>> If it doesn't exist, create, else update
        if not mc.optionVar(exists = self.name):
            if varType is not None:
                requestVarType = self.returnVarTypeFromCall(varType)
            elif defaultValue is not None:
                requestVarType = search.returnDataType(defaultValue)                
            elif value is not None:
                requestVarType = search.returnDataType(value)
            else:
                requestVarType = 'int'
                
            if requestVarType:
                self.form = requestVarType
                self.create(self.form)
                if defaultValue is not None:
                    self.initialStore(defaultValue)
                elif value is not None:
                    self.initialStore(value)
                    
                self.value = mc.optionVar(q=self.name)
                
            else:
                guiFactory.warning("'%s' is not a valid variable type"%varType)
            
        else:               
            self.update(varType)
            
            #Attempt to set a value on call
            if value is not None:           
                self.initialStore(value)
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Base Functions
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  
    def initialStore(self,value):
        if type(value) is list:
            self.extend(value)
        else:
            if type(self.value) is list:
                self.append(value)                            
            else:
                if value != self.value:
                    self.set(value)
                        
    def returnVarTypeFromCall(self, varTypeCheck):    
        for option in optionVarTypeDict.keys():
            if varTypeCheck in optionVarTypeDict.get(option):
                return option
        return 'int'
    
    def update(self,varType = None):
        """ 
        Update the data in case some other process has changed on optionVar
        """
        dataBuffer = mc.optionVar(q=self.name)   
        
        requestVarType = self.returnVarTypeFromCall(varType)
        
        if not mc.optionVar(exists = self.name):
            if requestVarType:
                self.form = requestVarType
                self.create(self.form)
                self.value = mc.optionVar(q=self.name)
                return
            else:
                return guiFactory.warning("'%s' is not a valid variable type"%varType)  
        
        else:
            #If it exists, first check for data buffer
            typeBuffer = search.returnDataType(dataBuffer) or False
            if not typeBuffer:
                print'changing to int!'
                typeBuffer = 'int'
            
            if varType is not None:    
                if typeBuffer == requestVarType:
                    self.form = typeBuffer
                    self.value = dataBuffer
                    return                
                else:
                    self.form = requestVarType
                    self.create(self.form)
                    self.value = mc.optionVar(q=self.name)
                    return  
            else:
                self.form = typeBuffer
                self.value = mc.optionVar(q=self.name)
                return                  
            

    def create(self,doType):
        """ 
        Makes an optionVar.
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
            self.name = ''
            self.form = ''
            self.value = ''
            
        except:
            guiFactory.warning("'%s' doesn't exist"%(self.name))
            
    def clear(self):
        """
        Clear the data from an option var
        """
        doName = self.name
        doType = self.form
        self.purge()
        self.__init__(doName,doType)
            
            
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
                guiFactory.report("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'string':
            try:
                mc.optionVar(sv = (self.name,str(value)))
                self.value = value
                
            except:
                guiFactory.report("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
    def append(self,value): 
        if type(self.value) is list:
            if value in self.value:
                return guiFactory.warning("'%s' already added"%(value))

        if self.form == 'int':
            try:
                mc.optionVar(iva = (self.name,int(value)))
                self.update(self.form)
                guiFactory.report("'%s' added to '%s'"%(value,self.name))
                
            except:
                guiFactory.warning("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'float':
            try:
                mc.optionVar(fva = (self.name,value))
                self.update(self.form)
                guiFactory.report("'%s' added to '%s'"%(value,self.name))
                
            except:
                guiFactory.report("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))
            
        elif self.form == 'string':
            try:
                mc.optionVar(sva = (self.name,str(value)))
                for i in "",'':
                    if i in self.value:
                        self.remove(i)

                self.update(self.form)
                guiFactory.report("'%s' added to '%s'"%(value,self.name))
                             
                
            except:
                guiFactory.report("'%s' couldn't be added to '%s' of type '%s'"%(value,self.name,self.form))

            

    def remove(self,value):
        if value in self.value:
            try:         
                i = self.value.index(value)
                mc.optionVar(removeFromArray = (self.name,i))
                self.update(self.form)
                guiFactory.report("'%s' removed from '%s'"%(value,self.name))
            except:
                guiFactory.report("'%s' failed to remove '%s'"%(value,self.name))
        else:
            guiFactory.report("'%s' wasn't found in '%s'"%(value,self.name))
            

                            
    def extend(self,valuesList):
        assert type(valuesList) is list,"'%s' not a list"%(valuesList)
        
        for v in valuesList:
            if type(self.value) is list:
                if v not in self.value:
                    self.append(v)
            else:
                if v != self.value:
                    self.append(v)
    
    def toggle(self):
        """
        Toggles an int type variable
        """
        assert self.form == 'int',"'%s' not an int type var"%(self.name)
        
        mc.optionVar(iv = (self.name,not self.value))
        self.value = not self.value
        guiFactory.report("'%s':%s"%(self.name,self.value))
        
        
        
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
        else:
            guiFactory.warning("'%s' is empty!"%self.name)
            
            
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
                
                        
                        
        

    
