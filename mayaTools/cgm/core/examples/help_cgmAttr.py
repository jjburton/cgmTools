"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basis of cgmMeta.cgmAttr
================================================================
"""
#==============================================================================================
#>> cgmMeta.cgmAttr
#==============================================================================================
from cgm.core import cgm_Meta as cgmMeta
import maya.cmds as mc

#>>Intro =========================================================================
#First we're gonna make some objects 
try:mi_baseObj = cgmMeta.cgmObject('baseObj')#...if it exists, initialize, except, make...
except:mi_baseObj = cgmMeta.cgmObject(mc.spaceLocator(p = [5,0,0],name = 'baseObj')[0])
try:mi_catchObj = cgmMeta.cgmObject('catchObj')#...if it exists, initialize, except, make...
except:mi_catchObj = cgmMeta.cgmObject(mc.spaceLocator(p = [-5,0,0],name = 'catchObj')[0])

#>> Let's start with existing attributes
mi_baseObj.select()
mPlug_t = cgmMeta.cgmAttr(mi_baseObj,'translate')
mPlug_tx = cgmMeta.cgmAttr(mi_baseObj,'tx')

#Getting attribte names as we like
mPlug_tx.p_combinedName
mPlug_tx.p_combinedShortName
mPlug_tx.p_nameNice
mPlug_t.p_hidden = True #...Hide something
mPlug_tx.p_hidden = False #...Unhide 1
mPlug_t.p_hidden = False #...unHide all
mPlug_t.p_keyable = 1 #...unHide all
mPlug_t.p_locked = 1 #...lock all
mPlug_t.p_locked = False #...unlock all

#>> Name alias
mPlug_tx.p_nameAlias#...Nothing
mPlug_tx.p_nameAlias = 'sideways'#...Set it, look at the channel box
mPlug_tx.p_nameAlias#...Now returns
mPlug_tx.p_nameAlias = False #...Clear it

#Simple value setting
mPlug_tx.p_value = 'asdf'
mPlug_t.p_value = 3#...Works with attributes with children as well
#==============================================================================================




#>>Creating attributs and more =========================================================================
mPlug_tx = cgmMeta.cgmAttr(mi_baseObj,'tx')
mPlug_translate = cgmMeta.cgmAttr(mi_baseObj,'translate')

#>> Let's make a couple of attributes ---------------------------------------------------
mPlug_testNumericAttr = cgmMeta.cgmAttr(mi_baseObj,'test_valueAttr',attrType = 'float',keyable = 1)
mPlug_testStringAttr = cgmMeta.cgmAttr(mi_baseObj,'test_strAttr',attrType = 'string', value = 44.65)#...yup, we're storing a number as a string
mPlug_testMessageAttr = cgmMeta.cgmAttr(mi_baseObj,'test_msgAttr',value = mi_catchObj.mNode, lock = 0)
mPlug_testBoolAttr = cgmMeta.cgmAttr(mi_baseObj,'test_bool',attrType = 'bool',keyable = 1)
mPlug_testEnumAttr = cgmMeta.cgmAttr(mi_baseObj,'test_enum',attrType = 'enum',keyable = 1)

#Queries ---------------------------------------------------
mPlug_testNumericAttr.isNumeric()#...yup
mPlug_testStringAttr.isNumeric()#...nope

mPlug_testNumericAttr.isUserDefined()#yup
mPlug_tx.isUserDefined()#...nope

#Relations ---------------------------------------------------
mPlug_tx.getSiblings()
mPlug_tx.getSiblings(asMeta = True)
mPlug_tx.getParent()
mPlug_tx.getParent(asMeta = 1)[0].p_combinedShortName
mPlug_translate.getChildren()
mPlug_translate.getChildren(asMeta = 1)

#Min/max ---------------------------------------------------
mPlug_testNumericAttr.getRange()#...that didn't work. let's give it a min and max
mPlug_testNumericAttr.p_minValue = -1
mPlug_testNumericAttr.p_maxValue = 1
mPlug_testNumericAttr.getRange()#...thar she blows!

#Soft Min/max ---------------------------------------------------
mPlug_testNumericAttr.getSoftRange()#...that didn't work. let's give it a min and max
mPlug_testNumericAttr.p_softMinValue = -1

mPlug_testNumericAttr.p_softMaxValue = 1
mPlug_testNumericAttr.p_softMaxValue
mPlug_testNumericAttr.getSoftRange()#...thar she blows!

#Enum ---------------------------------------------------
mPlug_testEnumAttr.p_enum #...Query
mPlug_testEnumAttr.p_enum = "no:yes"#...set. you have to select the channel box to see the update for now
mPlug_testEnumAttr.setEnum("no:yes")
mPlug_testEnumAttr.setEnum("off:on")
mPlug_testBoolAttr.setEnum("off:on")
#==============================================================================================


#>>Connections/Transfers and more =========================================================================
mPlug_tx.obj.select()
mPlug_tx.doConnectOut("%s.ty"%mPlug_tx.obj.mNode)#...let's connect the x to the y via connect out
mPlug_tz = cgmMeta.cgmAttr(mPlug_tx.obj,'tz')
mPlug_tz.doConnectIn(mPlug_tx)#...let's connect the z to the x via connect in

#Queries -------------------------------------------------------------------------------------------
mPlug_testStringAttr.returnCompatibleFromTarget(mPlug_tx.obj.mNode)#...compatible attrs
mPlug_testNumericAttr.returnCompatibleFromTarget(mPlug_tx.obj.mNode)#...numeric have a lot more openings

#Driven -------------------------------------------------------------------------------------------
mPlug_tx.getDriven()#...returns the driven attrs, skipConversions nodes (False by default), can flag
mPlug_tx.getDriven(asMeta = 1)#...asMeta
mPlug_tx.getDriven(obj = 1)#...return the obj
mPlug_tx.getDriven(obj = 1,asMeta = 1)#...asMeta

#Driver -------------------------------------------------------------------------------------------
mPlug_tx.getDriver()#...no driver on tx
mPlug_tz.getDriver()#...returns the driver attr, skipConversions nodes (False by default), can flag
mPlug_tz.getDriver(asMeta = True)#...get driver as meta
mPlug_tz.getDriver(obj = 1)#...return the obj
mPlug_tx.getDriver(obj = 1,asMeta = 1)#...asMeta

#Coversion -------------------------------------------------------------------------------------------
mPlug_testEnumAttr.doConvert('string')#...now it's a string
mPlug_testEnumAttr.doConvert('enum')#...convert back

mPlug_testValueAttr.doConnectIn(mPlug_tx)#...connect in value
mPlug_testValueAttr.doConvert('int')#...convert, maintining connection
mPlug_testValueAttr.doConvert('bool')#...convert, maintining connection
mPlug_testValueAttr.doConvert('enum')#...convert, maintining connection
mPlug_testValueAttr.doConvert('string')#...convert...can't connect number to string...alas
mPlug_testValueAttr.doConvert('float')#...convert back to original

#Copy -------------------------------------------------------------------------------------------
mPlug_testEnumAttr.doCopyTo(mi_catchObj.mNode)#...copy an attr
mPlug_testEnumAttr.doCopyTo(mi_catchObj.mNode,'asNewAttrName')#...copy an attr

#Copy settings -------------------------------------------------------------------------------------------
#Let's setup up some settings to copy....
mPlug_testValueAttr.p_maxValue = 10
mPlug_testValueAttr.p_minValue = -1
mPlug_testValueAttr.getRange()
mPlug_testValueAttr.p_locked = True
mPlug_testValueAttr.p_keyable = False

mPlug_testValueAttr2 = cgmMeta.cgmAttr(mi_catchObj,'test_valueAttr',attrType = 'float')
mPlug_testValueAttr2.getRange()#...Can't even query
mPlug_testValueAttr.doCopySettingsTo(mPlug_testValueAttr2)#...let's copy settings over
mPlug_testValueAttr2.getRange()#...correct now
mPlug_testValueAttr.doCopySettingsTo(mPlug_testStringAttr)#...let's copy settings over

#Transfer-------------------------------------------------------------------------------------------
mPlug_testValueAttr.p_combinedName#...just checking in where it is
mPlug_catch = mPlug_testValueAttr.doTransferTo(mi_catchObj)
mPlug_catch.p_combinedName#...hope our attr likes its new home...:)
#==============================================================================================





