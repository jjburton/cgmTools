"""
Motion is a small toolset for visualizing objects in motion.

Specifically, motion provides some tools for motion pathing as well as
ghosting. The main priority of Motion is to provide a helpful view of
objects in motion to help in the refinement of animation.

"""

__version__ = '0.1'

from pymel.core import *

GHOST_GRP = 'ghosts_grp'
GHOST_GRP_ATTR = 'motionGhostGroup'
PATH_GRP = 'motionPaths_grp'
PATH_GRP_ATTR = 'motionPathGroup'

class GUI(object):
    def __init__(self):
        self.winName = 'boMotionWin'
        self.title = 'Motion {0}'.format(__version__)
        self.build()
    
    def deleteExisting(self):
        """Deletes the window if it already exists"""
        if window(self.winName, ex=True):
            deleteUI(self.winName, wnd=True)
    
    def setWindowPrefs(self, **prefs):
        """Sets preferences for the current window"""
        if not windowPref(self.winName, ex=True):
            windowPref(self.winName)
        windowPref(self.winName, e=True, **prefs)
    
    def build(self):
        self.deleteExisting()
        self.setWindowPrefs(w=250, h=400)
        
        with window(self.winName, t=self.title):
            with frameLayout(lv=False, bv=False, mw=6, mh=6):
                with formLayout() as tmpForm:
                    objLay = self.buildObjsUI()
                    actLay = self.buildActionsUI()
                    formLayout(tmpForm, e=True,
                        af = [(objLay, 'left', 0), (objLay, 'top', 0), (objLay, 'right', 0),
                              (actLay, 'left', 0), (actLay, 'bottom', 0), (actLay, 'right', 0),
                        ],
                        ac = [(objLay, 'bottom', 4, actLay)],
                    )
    
    def buildObjsUI(self):
        with frameLayout(l='Objects/Components', mw=4, mh=4, bs='out') as frame:
            with formLayout() as tmpForm:
                self.objsList = lst = textScrollList(ams=True)
                add = button(l='Add')
                rem = button(l='Remove')
                clr = button(l='Clear')
                formLayout(tmpForm, e=True,
                    af = [(lst, 'left', 0), (lst, 'top', 0), (lst, 'right', 0),
                          (add, 'left', 0), (add, 'bottom', 0),
                          (rem, 'bottom', 0),
                          (clr, 'bottom', 0), (clr, 'right', 0)],
                    ap = [(add, 'right', 2, 33), (rem, 'left', 2, 33),
                          (rem, 'right', 2, 66), (clr, 'left', 2, 66)],
                    ac = [(lst, 'bottom', 4, add)],
                )
        return frame
    
    def buildActionsUI(self):
        with frameLayout(lv=False, mw=4, mh=4, bs='out') as frame:
            button(l='Ghost')
            button(l='Motion Trail')
        return frame



def ghost(objs, times=None, removeExisting=True, **kwargs):
    """
    Ghost the selected objects at the given times. If not times are given,
    uses the frame range, selected frame range, or selected keys.
    """
    if not isinstance(objs, list):
        objs = [objs]
    # TODO: validate objects
    # save time/selection
    sel = selected()
    curTime = currentTime()
    # run ghosting
    cleanGhosts()
    ghosts = []
    for time in times:
        currentTime(time)
        ghosts.extend(createGhosts(objs, removeExisting))
    # restore time/selection
    select(sel)
    currentTime(curTime)
    # restore focus to main panel for hotkeys, etc
    try: setFocus(getPanel(wf=True))
    except: pass
    return ghosts


def createGhosts(objs, removeExisting=True):
    """
    Duplicates the given objects and adds attributes to reference original object 
    """
    time = currentTime()
    timeGrp = getGhostTimeGroup(time)
    ghosts = []
    for obj in objs:
        if removeExisting:
            removeExistingGhost(obj, time)
        ghost = obj.duplicate()[0]
        ghost.setParent(timeGrp)
        ghost.addAttr('ghostedObject', at='message')
        obj.message >> ghost.ghostedObject
        ghosts.append(ghost)
    return ghosts


def removeExistingGhost(obj, time):
    """Removes any existing ghosts of the given object at the given time"""
    timeGrp = getGhostTimeGroup(time, create=False)
    if timeGrp is None:
        return
    dead = []
    for ghost in timeGrp.getChildren():
        if ghost.ghostedObject.listConnections()[0] == obj:
            dead.append(ghost)
    delete(dead)


def cleanGhosts(removeAll=False):
    """Cleanup the ghosts group, removes empty transforms, leftover ghosts, etc"""
    grp = getGhostGroup()
    if removeAll:
        delete(grp)
        return
    # delete null ghosts (ghostedObject no longer exists)
    deadObjs = []
    for timeGrp in grp.getChildren():
        for ghost in timeGrp.getChildren():
            if len(ghost.ghostedObject.listConnections()) == 0:
                deadObjs.append(ghost)
    delete(deadObjs)
    # delete empty time groups
    dead = []
    for timeGrp in grp.getChildren():
        if len(timeGrp.getChildren()) == 0:
            dead.append(timeGrp)
    delete(dead)
    # delete main group if no time groups left
    if len(grp.getChildren()) == 0:
        delete(grp)



# Utils
# -----

def getGhostGroup():
    """Return the shared ghosts group"""
    return getGroup(GHOST_GRP, GHOST_GRP_ATTR)

def getGhostTimeGroup(time=None, create=True):
    """Return the ghosts group for the given time"""
    if time is None:
        time = currentTime()
    grp = getGhostGroup()
    for timeGrp in grp.getChildren():
        if timeGrp.ghostTime.get() == time:
            return timeGrp
    # does not exist
    if create:
        newGrp = group(em=True, n='ghosts_t{0}_grp'.format(currentTime()), p=grp)
        newGrp.addAttr('ghostTime', at='double')
        newGrp.ghostTime.set(time)
        return newGrp


def getPathGroup():
    """Return the shared motion paths group"""
    return getGroup(PATH_GRP, PATH_GRP_ATTR)

def getGroup(name, attr):
    """
    Return a group by searching for the given attribute.
    Create a group with the given name if no match is found.
    """
    trans = ls(tr=True)
    for obj in trans:
        if obj.hasAttr(attr):
            return obj
    # object not found
    newGrp = group(em=True, n=name)
    newGrp.addAttr(attr, at='message')
    return newGrp

