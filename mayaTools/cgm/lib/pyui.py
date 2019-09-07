import maya.cmds as mc
import maya.mel as mel
import subprocess
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

class TextFieldButtonGrp(object):
    def __init__(self, *args):
        self.name = mc.textFieldButtonGrp(label="",adj=2)

    @property
    def label(self):
        return mc.textFieldButtonGrp(self.name, q=True, label=True)

    @label.setter
    def label(self, value):
        mc.textFieldButtonGrp(self.name, e=True, label=value)

    @property
    def cw3(self):
        return mc.textFieldButtonGrp(self.name, q=True, cw3=True)

    @cw3.setter
    def cw3(self, value):
        mc.textFieldButtonGrp(self.name, e=True, cw3=value)

    @property
    def text(self):
        return mc.textFieldButtonGrp(self.name, q=True, text=True)

    @text.setter
    def text(self, value):
        mc.textFieldButtonGrp(self.name, e=True, text=value)

    @property
    def buttonLabel(self):
        return mc.textFieldButtonGrp(self.name, q=True, buttonLabel=True)

    @buttonLabel.setter
    def buttonLabel(self, value):
        mc.textFieldButtonGrp(self.name, e=True, buttonLabel=value)

    @property
    def buttonCommand(self):
        return mc.textFieldButtonGrp(self.name, q=True, buttonCommand=True)

    @buttonCommand.setter
    def buttonCommand(self, value):
        mc.textFieldButtonGrp(self.name, e=True, buttonCommand=value)

    @property
    def changeCommand(self):
        return mc.textFieldButtonGrp(self.name, q=True, changeCommand=True)

    @changeCommand.setter
    def changeCommand(self, value):
        mc.textFieldButtonGrp(self.name, e=True, changeCommand=value)

class UIList(object):
    def __init__(self):
        self.listItems = []
        self.textScrollList = None

    def CreateTSL(self):
        self.textScrollList = mUI.MelTextScrollList() #mc.textScrollList()

    @property
    def displayItems(self):
        return mc.textScrollList( self.textScrollList, q = True, allItems = True )

    @displayItems.setter
    def displayItems(self, items):
        selectedItem = mc.textScrollList( self.textScrollList, q=True, selectItem = True )
        if not selectedItem:
            selectedItem = []

        mc.textScrollList( self.textScrollList, e = True, ra = True )
        
        mc.textScrollList( self.textScrollList, e = True, append = items )

        if self.displayItems and selectedItem:
            for item in selectedItem:
                if item in self.displayItems:
                    self.selectedItem = item

    @property
    def selectedItem(self):
        items = mc.textScrollList( self.textScrollList, q=True, selectItem = True )
        if items:
            return items[0]
        else:
            return None

    @selectedItem.setter
    def selectedItem(self, item):
        mc.textScrollList( self.textScrollList, e = True, selectItem = item )

    @property
    def selectedItems(self):
        items = mc.textScrollList( self.textScrollList, q=True, selectItem = True )
        if items:
            return items
        else:
            return []

    @property
    def selectedIndex(self):
        items = mc.textScrollList( self.textScrollList, q=True, selectIndexedItem = True )
        if items:
            return items[0]
        else:
            return None

    @selectedIndex.setter
    def selectedIndex(self, item):
        mc.textScrollList( self.textScrollList, e = True, selectIndexedItem = item )

    @property
    def selectedIndexes(self):
        items = mc.textScrollList( self.textScrollList, q=True, selectIndexedItem = True )
        if items:
            return items
        else:
            return []

    def AddItem(self, item):
        self.listItems.append(item)
        self.UpdateList()

    def AddItems(self, items):
        self.listItems += items
        self.UpdateList()

    def SetItems(self, items):
        self.listItems = items
        self.UpdateList()

    def UpdateList(self, *args):
        self.displayItems = self.listItems

    def ClearList(self):
        self.listItems = []
        self.UpdateList()


class SearchableList(UIList):
    def __init__(self):
        super(SearchableList, self).__init__()

        self.searchField = None

    def CreateSearchField(self, width=150.0):
        self.searchField = mc.textFieldButtonGrp( textChangedCommand = self.UpdateList, buttonCommand=self.ClearSearchBar, buttonLabel="Clear", cw3=(0,width*.66,width*.33), adj=1 )

    def UpdateList(self, *args):
        if self.textScrollList == None:
            return
        
        super(SearchableList, self).UpdateList(args)
        
        searchTerm = ""
        if self.searchField != None:
            searchTerm = mc.textFieldButtonGrp(self.searchField, q=True, text=True)
        
        sorted_list = sorted(self.listItems, key=lambda s: s.lower())

        displayList = []
        if searchTerm != "":
            for item in sorted_list:
                if searchTerm.lower() in item.lower():
                    displayList.append(item)
        else:
            displayList = sorted_list
        
        self.displayItems = displayList

    def ClearSearchBar(self, *args):
        if self.searchField:
            mc.textFieldButtonGrp(self.searchField, e=True, text="")
