# 
#   -= ml_toolbox.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 5, 2016-12-10
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_toolbox.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_toolbox
#     ml_toolbox.main()
# From MEL, this looks like:
#     python("import ml_toolbox;ml_toolbox.main()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Create custom menus in Maya's main menu bar for organizing scripts, just by putting them into directories.
# Insert tools into the existing maya menus, or add entirely new menus.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Make sure the ml_toolbox_menu folder is in your scripts directory or some other python path.
# Run the command mentioned above, or for best results, add the command to your scripts/userSetup.mel file, like so:
#     python('import ml_toolbox;ml_toolbox.main()');
# 
# To add a script to the menu, create folders and sub-folders in the ml_toolbox_menu directory. 
# If you add a folder that is named the same as a maya menu, the tools in that folder
# will be added to the maya menu, rather than a new menu.
# For MEL scripts to work, the main global proc needs to be the same name as the file.
# For python scripts, the main function needs to be "main" or "ui"
#      ______________
# - -/__ Advanced __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# If you have large menus and you don't like all the printing (if it's slowing startup), you can
# remove the verbose flag from Toolbox call in the main() function to suppress it.
# For python scripts, there's a few extra things you can do to get the most out of this tool.
# If you want any additional functions to be searched for besides main() etc, add them to the functionList
# variable below. They are sorted in search order.
# You can add an optional insertAfter variable to a script to have its menu item inserted after 
# an existing menuItem in a maya menu. See the bundled scripts for examples of this.
# If you'd like to automatically set up a hotkey for a tool, add a hotkey variable to script file
# with the value set to the modifier+hotkey button. (See the bundled create/snapLocator for an example of this.)
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -
__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__category__ = 'animationScripts'
__revision__ = 5

import maya.cmds as mc
import maya.mel as mm
import os, re, sys, imp, posixpath
from maya import OpenMaya

try:
    import ml_toolbox_menu
except:
    raise ImportError

ROOT_MODULE = ml_toolbox_menu.__name__
MENU_ITEM_PREFIX = '*' #change this if you want a different prefix for custom menu
MAIN_MENU_NAME_PREFIX = 'ml_mainWindowMenu_'

#These are the functions that this script will look for when building the menu, in this order.
#Add to this list if you want to support scripts with a different primary function.
functionList = ['main','ui','drag']


def main():

    Toolbox(ml_toolbox_menu, verbose=True)


def labelFromPath(path):
    '''
    generate a label based on a path
    '''
    pattern = re.compile('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))')

    label = os.path.basename(path)
    if '.' in label:
        label = os.path.splitext(label)[0]

    if label.startswith('ml_'):
        label = label[3:]

    label = pattern.sub(' ', label)
    label = label.replace('_', ' ')
    label = label.title()

    return label


def printMenu(menuLabel, depth=0):
    print((depth*'\t'+'  __'+len(menuLabel)*'_'))
    print((depth*'\t'+'_|',menuLabel,'|'+(20-len(menuLabel))*'_'))


class Toolbox(object):

    def __init__(self, rootModule, verbose=False):

        self.menusPath = rootModule.__path__[0].replace('\\','/')
        
        self.tools = list()
        self.hasHotkeys = list()
        self.mayaMenus = list()
        self.customMenus = dict()
        self.verbose = verbose

        self.createMainMenus()

    
    def createMainMenus(self):
        
        #mayas main window menu:
        gMainWindow = mm.eval('$temp=$gMainWindow')
        #get all the menus that are children of the main menu
        mainWindowMenus = mc.window(gMainWindow, query=True, menuArray=True)
        #get the label for each of the menus
        #this will be matched against tool directories
        self.mainMenus = dict()
        for name in mainWindowMenus:
            label = mc.menu(name, query=True, label=True)
            #we need to make the label all lower case and no spaces, so we can match properly.
            formatLabel = label.replace(' ','').lower()
            self.mainMenus[formatLabel] = name

        mayaMenuDirectories = list()
        customMenuDirectories = list()
        
        for folder in os.listdir(self.menusPath):
            if folder.startswith('.'):
                continue

            toolDirectory = posixpath.join(self.menusPath,folder)

            #only directories for this first level
            if not os.path.isdir(toolDirectory):
                if not folder.startswith('__init__') and self.verbose:
                    print(('Root level file being ignored, move this to a sub-directory: ',toolDirectory))
                continue

            menuLabel = labelFromPath(toolDirectory)
            formatLabel = menuLabel.replace(' ','').lower()

            if formatLabel in self.mainMenus and not self.mainMenus[formatLabel].startswith(MAIN_MENU_NAME_PREFIX):
                #maya menus
                mayaMenuDirectories.append(toolDirectory)
            else:
                #custom menu
                customMenuDirectories.append(toolDirectory)

        if mayaMenuDirectories:
            for d in mayaMenuDirectories:
                self.appendMayaMenu(d)

        if customMenuDirectories:
            for d in customMenuDirectories:
                self.createCustomMenu(d, parent=gMainWindow, mainMenu=True)

        self.setHotkeys()


    def classifyTool(self, tool):

        #initialize tool
        self.tools.append(tool)
        if tool.isPython:
            #python only
            if hasattr(tool,'hotkey'):
                self.hasHotkeys.append(tool)


    def appendMayaMenu(self, path):
        '''
        Add tools to the maya menus
        '''
        menuLabel = labelFromPath(path)
        formatLabel = menuLabel.replace(' ','').lower()
        menuItemArray = mc.menu(self.mainMenus[formatLabel], query=True, itemArray=True)

        #if this menu hasn't been built yet, run the post menu command to build it
        #that took a long time to figure out.
        if not menuItemArray:
            if self.verbose:
                print(('pre-building menu: ',menuLabel))
            pmc = mc.menu(self.mainMenus[formatLabel], query=True, postMenuCommand=True)
            if pmc:
                mm.eval(pmc)
                menuItemArray = mc.menu(self.mainMenus[formatLabel], query=True, itemArray=True)

        #get all the menu items in the menu
        menuItems = dict()
        for each in menuItemArray:
            eachLabel = mc.menuItem(each, query=True, label=True)
            menuItems[eachLabel] = each

        subItems = [posixpath.join(path,x) for x in os.listdir(path) if (x.endswith('.py') or x.endswith('.mel')) and x != '__init__.py']

        if subItems:
            for path in subItems:
                tool = Tool(path)
                self.classifyTool(tool)
                if not tool.errors:
                    tool.createMenuItem(parent=self.mainMenus[formatLabel], labelPrefix=MENU_ITEM_PREFIX+' ', italicized=True)


    def createCustomMenu(self, path, parent=None, depth=0, mainMenu=False):
        '''
        Recurse through a tool directory, creating tools and menus
        '''

        if os.path.isdir(path):
            # recursive subMenu
            subItems = os.listdir(path)
            #if there's stuff in the folder, create a menu item
            if subItems:
                
                #if there are python files in this directory, but no __init__ file, create one.
                if not '__init__.py' in subItems and [x for x in subItems if x.endswith('.py')]:
                    print(('Creating required __init__.py file in {}'.format(path)))
                    with open(os.path.join(path,'__init__.py'), 'w') as f:
                        f.write('#Generated by ml_toolbox')
                    
                subItems = sorted(subItems)

                #do directories first, then files
                #generate menu name
                menuPrefix = 'mlSubMenu'
                if mainMenu:
                    menuPrefix = MAIN_MENU_NAME_PREFIX
                menuName = os.path.basename(path)
                menuName = menuPrefix+menuName
                if mc.menu(menuName, exists=True):
                    mc.deleteUI(menuName)        

                #generate menu label
                label = labelFromPath(path)
                if self.verbose:
                    printMenu(label,depth)

                #create the menu
                if mainMenu:
                    menuName = mc.menu(menuName, parent=parent, to=True, label=label, allowOptionBoxes=True)
                else:
                    menuName = mc.menuItem(menuName, label=label, subMenu=True, parent=parent, allowOptionBoxes=True)

                #and recurse!
                #do directories first
                filePaths = list()
                for each in subItems:
                    eachPath = posixpath.join(path,each)
                    if os.path.isdir(eachPath):
                        #if its a directory, recurse
                        self.createCustomMenu(eachPath, parent=menuName, depth=depth+1)
                    else:
                        filePaths.append(eachPath)

                #now go through the files
                for each in filePaths:
                    if not each.endswith('__init__.py') and ((each.endswith('.py') or each.endswith('.mel'))):
                        tool = Tool(each, depth=depth) 
                        self.classifyTool(tool)
                        if not tool.errors:
                            if self.verbose:
                                print(((depth+1)*'\t'+tool.label))
                            tool.createMenuItem(parent=menuName, italicized=False)
                        elif self.verbose:
                            print(((depth+1)*'\t',tool.label,' <-- has errors and was unable to be imported.'))

                mc.setParent('..', menu=True)


    def setHotkeys(self):
        '''
        Set hotkeys for all the tools
        '''
        if not self.hasHotkeys:
            return
        
        commands = list()
        keys = list()
        
        doPrint = True
        for each in self.hasHotkeys:
            if each.hotkey:
                if doPrint and self.verbose:
                    print() 
                    print('Set Hotkeys')
                    doPrint = False
                each.hotkey.create(self.verbose)


class Tool(object):

    def __init__(self, path, depth=0, verbose=False):

        self.path = os.path.normpath(path).replace('\\','/')

        #this doesn't allow period in name
        self.name = os.path.basename(self.path).split('.')[0]
        self.label = labelFromPath(self.path)
        self.depth = depth
        self.errors = False
        self.verbose = verbose

        self.hotkey = None
        self.markingMenu = None
        self.command = None
        self.isPython = False
        self.isMel = False

        if self.path.endswith('.py'):
            self.initPython()
        elif self.path.endswith('.mel'):
            self.initMel()
        else:
            self.errors = True


        if not self.errors and self.isPython:
            #initialize hotkeys and markingMenus, python only
            hotkey = self.Hotkey(self.module, self.command, self.name)
            if hotkey.keys:
                self.hotkey = hotkey


    def initPython(self):

        self.isPython = True

        #check for __init__ file, create one if there isn't any in this directory
        directory = os.path.dirname(self.path)
        initPath = posixpath.join(directory,'__init__.py')
        if not os.path.exists(initPath):
            print(('Creating required __init__.py file: '+initPath))
            with open(initPath, 'w') as f:
                f.write('#Generated by ml_toolbox')

        fromRoot = self.path.split(ROOT_MODULE)[1]
        noExt = fromRoot.split('.')[0]
        dotPath = noExt.replace('/','.')
        self.moduleName = ROOT_MODULE+dotPath
        
        #try to import the module, catch ones with errors
        try:
            __import__(self.moduleName)
            self.module = sys.modules[self.moduleName]

            #find the main command to use, otherwise skip
            for f in functionList:
                if f in self.module.__dict__:
                    self.command = 'import '+self.module.__name__+';reload('+self.module.__name__+');'+self.module.__name__+'.'+f+'()'
                    break
                else:
                    self.command = 'from maya import OpenMaya;OpenMaya.MGlobal.displayWarning("No command found, make sure this tool as a main() function or that its primary function is in the functionList variable in ml_toolbox.py")'

        except Exception:
            if self.verbose:
                print(('!!  '+((self.depth-1)*'\t')+self.label+' < -- Errors found. Skipping'))
            self.errors = True


    def initMel(self):
        self.isMel = True
        #escapePath = self.path.replace('\\','\\\\\\\\')
        self.command = 'import maya.mel;maya.mel.eval("source \\\"'+self.path+'\\\";'+self.name+'")'


    def createMenuItem(self, parent=None, labelPrefix='', italicized=False):

        if self.isPython:
            menuName = 'mlMenu_'+self.module.__name__.replace('.','_')
        else:
            menuName = 'mlMenu_'+self.name

        #Create the label and print the tool
        label = labelPrefix+self.label

        #keyword args for the menu command
        kwargs = {'italicized':italicized}

        if self.hotkey:
            if len(self.hotkey.keys) == 1:
                kwargs['altModifier'] = self.hotkey.altModifier[0]
                kwargs['ctrlModifier'] = self.hotkey.ctrlModifier[0]

                if self.hotkey.keys[0].isupper():
                    kwargs['shiftModifier'] = True
                kwargs['keyEquivalent'] = self.hotkey.keys[0]
        
        if self.verbose:
            print((self.depth*'\t'+label))

        if mc.menuItem(menuName, exists=True):
            mc.deleteUI(menuName)

        insertAfter = None
        if self.isPython and hasattr(self.module,'insertAfter'):
            menuItemArray = mc.menu(parent, query=True, itemArray=True)
            if menuItemArray:
                menuItems = dict()
                for each in menuItemArray:
                    eachLabel = mc.menuItem(each, query=True, label=True)
                    menuItems[eachLabel] = each
    
                if self.module.insertAfter in menuItems:
                    kwargs['insertAfter'] = menuItems[self.module.insertAfter]

        mc.setParent(parent, menu=True)

        menuName = mc.menuItem(menuName, label=label, command=self.command, **kwargs)


    class Hotkey(object):

        def __init__(self, module, command, name):

            self.keys = list()
            self.altModifier = list()
            self.ctrlModifier = list()
            self.commands = list()
            self.functions = list()
            self.name = name


            #check that the module has a hotkey attribute
            if not hasattr(module,'hotkey'):
                return

            hotkeys = list()
            commands = list()
            if isinstance(module.hotkey, str):
                hotkeys.append(module.hotkey)
                commands.append(command)
                self.functions.append('main')
            elif isinstance(module.hotkey, dict):
                hotkeys = list(module.hotkey.keys())
                for h in hotkeys:
                    func = module.hotkey[h].split('(')[0]
                    self.functions.append(func)
                    commands.append('import '+module.__name__+';'+module.__name__+'.'+module.hotkey[h])

            for i, (h,c) in enumerate(zip(hotkeys,commands)):

                self.keys.append(None)
                self.altModifier.append(False)
                self.ctrlModifier.append(False)
                self.commands.append(c)

                hotkeySplit = h.split('+')

                if len(hotkeySplit) == 1:
                    self.keys[i] = hotkeySplit[0]
                else:
                    for each in hotkeySplit:
                        low = each.lower()
                        if low == 'ctrl' or low == 'control' or low == 'cmd' or low == 'command':
                            self.ctrlModifier[i] = True
                        if low == 'alt' or low == 'alternate':
                            self.altModifier[i] = True

                    self.keys[i] = hotkeySplit[-1]


        def create(self, verbose=False):

            if not self.keys:
                return

            for i,k in enumerate(self.keys):

                name = self.name+'.'+self.functions[i]
                
                if verbose:
                    hotkeyPrint = '\t'
                    if self.altModifier[i]:
                        hotkeyPrint+='[Alt]+'
                    if self.ctrlModifier[i]:
                        hotkeyPrint+='[Ctrl]+'
                    hotkeyPrint = hotkeyPrint+'['+k+'] :\t'+name
                    print(hotkeyPrint)

                rtc = 'ml_hk_'+self.name+'_'+self.functions[i]

                nc = rtc+'_NC'

                if not mc.runTimeCommand(rtc, exists=True):
                    rtc = mc.runTimeCommand(rtc, default=True, annotation=name+' Hotkey generated by ml_toolbox', category='User', command=self.commands[i])

                nc = mc.nameCommand(nc, default=True, annotation=name+' nameCommand generated by ml_toolbox', command=rtc)

                mc.hotkey(keyShortcut=k, alt=self.altModifier[i], ctl=self.ctrlModifier[i], name=nc, releaseName='')


if __name__ == '__main__':
    main()

#      ______________________
# - -/__ Revision History __/- - - - - - - - - - - - - - - - - - - - - - - -
#
# Revision 1: 2016-01-31 : First publish.
#
# Revision 2: 2016-02-01 : Fixing Windows compatibility
#
# Revision 3: 2016-03-07 : more windows path support
#
# Revision 4: 2016-03-23 : Fixing slash bug in some windows cases.
#
# Revision 5: 2016-12-10 : Fixing print, and auto creation of __init__ files on windows.
