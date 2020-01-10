import maya.cmds as mc
#import pyunify.lib.node as node
import cgm.core.cgm_Meta as cgmMeta
import json
from functools import partial
import operator

class ShotUI(object):
    '''
Shot UI class.

Loads the Shot UI.

| outputs ShotUI

example:
.. python::

    import cgm.core.mrs.Shots as SHOTS
    x = SHOTS.ShotUI()
    '''
    def __init__(self):
        self.window                   = None

        self.cw    = 100
        self.width = self.cw * 7.5

        self.autoAdjustOptionVar = "shotUI_autoAdjustFrames"

        self.animDict           = {}
        self.animList           = []
        self.animUIDict         = {}
        self.animListNode       = None
        self.shotColumn         = None
        self.shotRCL            = None
        self.autoAdjustFramesMI = None

        self._defaultBGColor = [0,0,0]

        self.sortType = 1

        self.LoadAnimList()

        self.CreateWindow()

    def CreateWindow(self):
        if(mc.window("pyunify_ShotsUI", exists=True)):
            mc.deleteUI("pyunify_ShotsUI", window=True)

        #    Create a window with a some fields for entering text.
        #
        self.window = mc.window("pyunify_ShotsUI", title="Sub Animation List", menuBar=True)

        mc.menu( label='Options' )
        self.autoAdjustFramesMI = mc.menuItem( label='Auto Adjust Frames', checkBox=True, command = self.SaveOptions )

        mc.columnLayout(w=self.width)

        mc.rowColumnLayout( numberOfColumns=8, columnWidth=[(1, self.cw * 2.5), (2, self.cw*.25), (3, self.cw), (4, self.cw), (5, self.cw*.25), (6, self.cw), (7, self.cw * .75), (8, self.cw * .75)] )
        
        mc.button(label="Name", command=partial(self.Sort, 0))
        mc.button(label="")
        mc.button(label="Start", command=partial(self.Sort, 1))
        mc.button(label="End", command=partial(self.Sort, 2))
        mc.button(label="")
        mc.button(label="Frames", command=partial(self.Sort, 3))

        mc.setParent('..')

        self.shotRCL = mc.rowColumnLayout( numberOfColumns=8, columnWidth=[(1, self.cw * 2.5), (2, self.cw*.25), (3, self.cw), (4, self.cw), (5, self.cw*.25), (6, self.cw), (7, self.cw * .75), (8, self.cw * .75)] )

        self.animUIDict = {}

        mc.setParent('..')

        mc.button( label="Add Sub Animation", w=self.width, command=self.AddShotUI )
        mc.button( label="Refresh", w=self.width, command=self.RefreshShotList )

        mc.showWindow( self.window )

        self.Sort(self.sortType)

        if mc.optionVar( exists=self.autoAdjustOptionVar ):
            mc.menuItem( self.autoAdjustFramesMI, e=True, checkBox=mc.optionVar( q=self.autoAdjustOptionVar ))

    def SaveOptions(self, *args):
        mc.optionVar( iv=(self.autoAdjustOptionVar, mc.menuItem(self.autoAdjustFramesMI, q=True, checkBox=True) ) )

    def Sort(self, *args):
        self.sortType = args[0]

        if self.sortType == 0:
            self.animList = sorted(self.animDict.items(), key=operator.itemgetter(0))
        elif self.sortType == 1:
            self.animList = sorted(self.animDict.items(), key=lambda x: x[1][0])
        elif self.sortType == 2:
            self.animList = sorted(self.animDict.items(), key=lambda x: x[1][1]) 
        elif self.sortType == 3:
            self.animList = sorted(self.animDict.items(), key=lambda x: x[1][2])

        self.RefreshShotList()     

    def SetShotRange(self, *args, **kwargs):
        setMin = True
        setMax = True
        if 'min' in kwargs:
            setMin = kwargs['min']
        if 'max' in kwargs:
            setMax = kwargs['max']

        if setMin:
            mc.playbackOptions(e=True, min=self.animDict[args[0]][0])
        if setMax:
            mc.playbackOptions(e=True, max=self.animDict[args[0]][1])

        self.UpdateShotList()

    def RemoveShot(self, *args):
        self.animDict.pop(args[0], None)
        self.animListNode.subAnimList = self.animDict#json.dumps(self.animDict)

        self.Sort(self.sortType)

    def AddShotUI(self, *args):
        window = mc.window(title="Add Shot", iconName='Add Shot')
        mc.columnLayout()
        mc.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 80), (2, 200)], h=60  )
        mc.text( label='Shot Name')
        name = mc.textField()
        mc.text( label='Range' )
        shotRange = mc.intFieldGrp(numberOfFields=2, columnWidth=[(1, 96), (2, 99)])
        mc.setParent('..')
        mc.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 140), (2, 140)]  )
        mc.button(label="OK", w=140, h=30, command=partial(self.AddShotFromUI, window, name, shotRange))
        mc.button(label="Cancel", h=30, command=partial(self.DeleteAddShotUI, window) )
        mc.setParent('..')
        mc.setParent('..')

        minVal = mc.playbackOptions(q=True, min=True)
        maxVal = mc.playbackOptions(q=True, max=True)

        mc.intFieldGrp(shotRange, e=True, v1=minVal, v2=maxVal)

        mc.showWindow( window )

    def DeleteAddShotUI(self, *args):
        mc.deleteUI(args[0], window=True)

    def AddShotFromUI(self, *args):
        name = mc.textField(args[1], q=True, text=True)
        minVal = mc.intFieldGrp(args[2], q=True, v1=True)
        maxVal = mc.intFieldGrp(args[2], q=True, v2=True)
        mc.deleteUI(args[0], window=True)

        self.AddShot(name, minVal, maxVal)

    def AddShot(self, name, minVal, maxVal):
        # create if not found
        if not self.animListNode:
            self.animListNode = cgmMeta.cgmObject(name="AnimListNode")#node.Transform(name="AnimListNode")
            self.animListNode.addAttr("subAnimList", attrType = 'string')

        self.animDict[name] = [minVal, maxVal, maxVal - minVal]
        self.animListNode.subAnimList =  self.animDict#json.dumps(self.animDict)

        self.Sort(self.sortType)

    def RefreshUI(self, *args):
        mc.deleteUI( self.window, window=True )
        self.CreateWindow()

    def RefreshShotList(self, *args):
        children = mc.rowColumnLayout(self.shotRCL, q=True, childArray=True)
        for child in children if children else []:
            mc.deleteUI(child)

        self.animUIDict = {}

        mc.setParent(self.shotRCL)
        
        # subAnims
        for item in self.animList:
            key = item[0]

            self.animUIDict[key] = {}

            self.animUIDict[key]['nameField'] = mc.textField(text=key, changeCommand=partial(self.RenameShot, key))
            self.animUIDict[key]['minButton'] = mc.button( label="<", command=partial(self.SetShotRange, key, max=False) )
            self.animUIDict[key]['minField'] = mc.intField( v = item[1][0], changeCommand=partial(self.AdjustShotRange, key) )
            self.animUIDict[key]['maxField'] = mc.intField( v = item[1][1], changeCommand=partial(self.AdjustShotRange, key) )
            self.animUIDict[key]['maxButton'] = mc.button( label=">", command=partial(self.SetShotRange, key, min=False) )
            self.animUIDict[key]['lengthField'] = mc.intField( v = item[1][2], changeCommand=partial(self.AdjustShotLength, key) )
            self.animUIDict[key]['frameBtn'] = mc.button(label="Frame", command=partial(self.SetShotRange, key) )
            self.animUIDict[key]['removeBtn'] = mc.button(label="Remove", command=partial(self.RemoveShot, key))

            self._defaultBGColor = mc.textField(self.animUIDict[key]['nameField'], q=True, backgroundColor=True)

        self.UpdateShotList()
        
    def UpdateShotList(self):
        minV = mc.playbackOptions(q=True, min=True)
        maxV = mc.playbackOptions(q=True, max=True)

        for key in self.animDict:
            mc.textField(self.animUIDict[key]['nameField'], e=True, text=key )
            mc.intField(self.animUIDict[key]['minField'], e=True, v=self.animDict[key][0] )
            mc.intField(self.animUIDict[key]['maxField'], e=True, v=self.animDict[key][1] )
            mc.intField(self.animUIDict[key]['lengthField'], e=True, v=self.animDict[key][2] )
            mc.button(self.animUIDict[key]['minButton'], e=True, command=partial(self.SetShotRange, key, max=False) )
            mc.button(self.animUIDict[key]['maxButton'], e=True, command=partial(self.SetShotRange, key, min=False) )

            # Set Colors
            if minV == self.animDict[key][0]:
                mc.intField(self.animUIDict[key]['minField'], e=True, backgroundColor=[.2, .3, .3] )
            else:
                mc.intField(self.animUIDict[key]['minField'], e=True, backgroundColor = self._defaultBGColor )
            
            if maxV == self.animDict[key][1]:
                mc.intField(self.animUIDict[key]['maxField'], e=True, backgroundColor=[.2, .3, .3] )
            else:
                mc.intField(self.animUIDict[key]['maxField'], e=True, backgroundColor = self._defaultBGColor )

            if self.animDict[key][0] >= minV and self.animDict[key][1] <= maxV:
                mc.textField(self.animUIDict[key]['nameField'], e=True, backgroundColor=[.2, .3, .3] )
            else:
                mc.textField(self.animUIDict[key]['nameField'], e=True, backgroundColor = self._defaultBGColor )

    def AdjustShotRange(self, *args):
        shift = 0

        minVal = mc.intField( self.animUIDict[args[0]]['minField'], q=True, v=True )
        maxVal = mc.intField( self.animUIDict[args[0]]['maxField'], q=True, v=True )

        length = maxVal - minVal

        if self.animDict[args[0]][0] != minVal:
            shift = minVal - self.animDict[args[0]][0]
            maxVal = minVal + self.animDict[args[0]][2]
            length = maxVal - minVal
        elif self.animDict[args[0]][1] != maxVal:
            shift = maxVal - self.animDict[args[0]][1]
        elif self.animDict[args[0]][2] != length:
            shift = length - self.animDict[args[0]][2]

        self.animDict[args[0]][0] = minVal
        self.animDict[args[0]][1] = maxVal
        self.animDict[args[0]][2] = maxVal - minVal

        mc.intField( self.animUIDict[args[0]]['lengthField'], e=True, v=self.animDict[args[0]][2] )

        if mc.menuItem(self.autoAdjustFramesMI, q=True, checkBox=True ) and shift != 0:
            self.ShiftTimeRanges(minVal, shift, ignoreKeys = [args[0]])
        
        self.animListNode.subAnimList = self.animDict#json.dumps(self.animDict)
        
        self.UpdateShotList()

    def AdjustShotLength(self, *args):

        shotLength = mc.intField( self.animUIDict[args[0]]['lengthField'], q=True, v=True )

        shift = shotLength - self.animDict[args[0]][2]
        
        self.animDict[args[0]][1] = self.animDict[args[0]][0] + shotLength
        self.animDict[args[0]][2] = shotLength

        shotLength = mc.intField( self.animUIDict[args[0]]['maxField'], e=True, v=self.animDict[args[0]][1] )

        if mc.menuItem(self.autoAdjustFramesMI, q=True, checkBox=True ) and shift != 0:
            self.ShiftTimeRanges(self.animDict[args[0]][0], shift, ignoreKeys = [args[0]])
        
        self.animListNode.subAnimList = self.animDict#json.dumps(self.animDict)
        self.UpdateShotList()

    def ShiftTimeRanges(self, startTime, shift, ignoreKeys = []):
        for key in self.animDict:
            if key in ignoreKeys:
                continue

            if self.animDict[key][0] >= startTime:
                self.animDict[key][0] += shift
                self.animDict[key][1] += shift
            elif self.animDict[key][1] > startTime:
                self.animDict[key][1] += shift

            self.animDict[key][2] = self.animDict[key][1] - self.animDict[key][0]

        self.UpdateShotList()

    def RenameShot(self, *args):
        key = args[0]

        newName = str(mc.textField(self.animUIDict[key]['nameField'], q=True, text=True).strip())
        
        if newName == key:
            return

        if newName in self.animDict:
            mc.textField(self.animUIDict[key]['nameField'], e=True, text=key)
            mc.confirmDialog(title="Name Conflict", message='Sorry, new name conflicts with an existing name', button=['Bummer'])
            return
            
        self.animDict[newName] = self.animDict.pop(key)        
        self.animUIDict[newName] = self.animUIDict.pop(key)

        self.animListNode.subAnimList = self.animDict#json.dumps(self.animDict)

        # Adjust UI elements to reflect new name
        mc.textField(self.animUIDict[newName]['nameField'], e=True, changeCommand=partial(self.RenameShot, newName))
        mc.intField(self.animUIDict[newName]['minField'], e=True, changeCommand=partial(self.AdjustShotRange, newName) )
        mc.intField(self.animUIDict[newName]['maxField'], e=True, changeCommand=partial(self.AdjustShotRange, newName) )
        mc.intField(self.animUIDict[newName]['lengthField'], e=True, changeCommand=partial(self.AdjustShotLength, newName) )
        mc.button(self.animUIDict[newName]['frameBtn'], e=True, command=partial(self.SetShotRange, newName) )
        mc.button(self.animUIDict[newName]['removeBtn'], e=True, command=partial(self.RemoveShot, newName))
        mc.button(self.animUIDict[newName]['minButton'], e=True, command=partial(self.SetShotRange, newName, max=False) )
        mc.button(self.animUIDict[newName]['maxButton'], e=True, command=partial(self.SetShotRange, newName, min=False) )

    def LoadAnimList(self):
        # Find anim list node
        animListNodes = mc.ls("*.subAnimList")
        if len(animListNodes) > 0:
            self.animListNode = cgmMeta.asMeta(animListNodes)[0]
            animListString = self.animListNode.subAnimList
            if animListString:
                self.animDict = animListString#json.loads(animListString)

                for key in self.animDict:
                    if len(self.animDict[key]) == 2:
                        self.animDict[key].append(self.animDict[key][1] - self.animDict[key][0])
class AnimList(object):
    def __init__(self):
        self.shotDict = {}
        self.shotList = []
        
        animListNodes = mc.ls("*.subAnimList")
        if len(animListNodes) > 0:
            animListNode = cgmMeta.asMeta(animListNodes)[0]
            animListString = animListNode.subAnimList
            if animListString:
                #the try here is for the older version of the data object before moving to cgm methods
                try:self.shotDict = json.loads(animListString)
                except:
                    self.shotDict = animListString
                    #for k,v in animListString.iteritems():
                    #    self.shotDict.append([k,v])
                    #self.shotDict = animListString
                    

        self.SortedList(1)

    def SortedList(self, sortType = 1):
        if sortType == 0:
            self.shotList = sorted(self.shotDict.items(), key=operator.itemgetter(0))
        elif sortType == 1:
            self.shotList = sorted(self.shotDict.items(), key=lambda x: x[1][0])
        elif sortType == 2:
            self.shotList = sorted(self.shotDict.items(), key=lambda x: x[1][1]) 
        elif sortType == 3:
            self.shotList = sorted(self.shotDict.items(), key=lambda x: x[1][2])

        return self.shotList