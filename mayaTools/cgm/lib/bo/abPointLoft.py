"""
    A tool for snapping points to a surface.
    Similar effect as using a live surface, except
    movement of the points is limited to a single axis.
"""


__version__ = '1.0'
__author__ = 'Ahdom and Bohdon Sayre'


import logging
from pymel.core import *


logger = logging.getLogger('Point Loft')
logger.setLevel(logging.DEBUG)

def doIt():
    selList = ls(sl=True, fl=True)
    myPointLoft = PointLoft()
    myPointLoft.surf = selList[-1] #get the last selected object (the surface)
    myPointLoft.pts = selList[:-1] #get all but the last selected objects (the verts)
    myPointLoft.run()


class Gui(object):
    """
    The GUI Class for Point Loft
    Contains three sections for collection points,
    the surface, and the axis to perform movement on
    
    >>> import abPointLoft
    >>> abPointLoft.Gui()
    """
    
    title = 'Point Loft %s' % __version__
    winName = 'abPointLoftWin'
    win = None
    ui = {}
    pts = []
    surf = None
    axis = 0
    useNormal = False
    
    def __init__(self):
        self.create()
    
    def create(self):
        if window(self.winName, exists=True):
            deleteUI(self.winName)
        
        with window(self.winName, t=self.title, mxb=False) as self.win:
            template = uiTemplate('abPointLoftTemplate', force=True)
            template.define(button, w=40, h=20, bgc=[1.4 * v for v in [.18, .21, .25]])
            template.define(columnLayout, rs=12, adj=True)
            template.define(formLayout, nd=100)
            template.define(frameLayout, mw=4, mh=4, bs='out', bgc=[.18, .21, .25])
            with template:
                with formLayout() as mainForm:
                    with columnLayout() as mainCol:
                        with frameLayout(l='Points (0)') as ptsFrame:
                            with formLayout() as form1:
                                ptsField = textField(ed=False)
                                ptsBtn = button(l='Get', c=Callback(self.getPts))
                                popupMenu(p=ptsBtn)
                                menuItem(l='Select Points', c=Callback(self.selectPts))
                        with frameLayout(l='Surface') as surfFrame:
                            with formLayout() as form2:
                                surfField = textField(ed=False)
                                surfBtn = button(l='Get', c=Callback(self.getSurf))
                        with frameLayout(l='Axis') as axisFrame:
                            with formLayout() as form3:
                                axisRadioGrp = radioButtonGrp(nrb=4, cc=Callback(self.axisChange), sl=2, l1='X', l2='Y', l3='Z', l4='N', cw4=[30, 30, 30, 30])
                    runBtn = button(l='Run', h=30, c=Callback(self.run))
                
                formLayout(form1, e=True,
                                af=[(ptsField, 'left', 0), (ptsBtn, 'right', 0)],
                                ac=[(ptsField, 'right', 4, ptsBtn)])
                formLayout(form2, e=True,
                                af=[(surfField, 'left', 0), (surfBtn, 'right', 0)],
                                ac=[(surfField, 'right', 4, surfBtn)])
                formLayout(form3, e=True,
                                ap=[(axisRadioGrp, 'left', -70, 50)])
                formLayout(mainForm, e=True,
                                af=[(mainCol, 'top', 6),
                                    (mainCol, 'left', 6),
                                    (mainCol, 'right', 6),
                                    (runBtn, 'left', 6),
                                    (runBtn, 'right', 6),
                                    (runBtn, 'bottom', 6)])
        #store ui elements
        self.ui['mainForm'] = mainForm
        self.ui['mainCol'] = mainCol
        self.ui['ptsFrame'] = ptsFrame
        self.ui['ptsField'] = ptsField
        self.ui['ptsBtn'] = ptsBtn
        self.ui['surfFrame'] = surfFrame
        self.ui['surfField'] = surfField
        self.ui['surfBtn'] = surfBtn
        self.ui['axisFrame'] = axisFrame
        self.ui['axisRadioGrp'] = axisRadioGrp
        self.ui['runBtn'] = runBtn
        self.axisChange()
    
    def getPts(self):
        self.pts = ls(sl=True, fl=True)
        ptsDisplayList = [str(vert.name()) for vert in self.pts]
        self.ui['ptsField'].setText(str(ptsDisplayList))
        self.ui['ptsFrame'].setLabel('Points (%d)' % len(self.pts))
    
    def selectPts(self):
        select(self.pts)
    
    def getSurf(self):
        self.surf = ls(sl=True)[0]
        self.ui['surfField'].setText(self.surf)
    
    def axisChange(self):
        self.axis = self.ui['axisRadioGrp'].getSelect() - 1
        if self.axis == 3:
            self.axis = 0
            self.useNormal = True
        else:
            self.useNormal = False
    
    def run(self):
        if self.pts == [] or self.surf == []:
            logger.error('Not enough information was provided')
            return
        
        print self.surf, self.axis, self.useNormal, self.pts
        
        pl = PointLoft()
        pl.pts = self.pts
        pl.surf = self.surf
        pl.axis = self.axis
        pl.useNormal = self.useNormal
        pl.run()


class PointLoft(object):
    """The Main Point Loft class
    Takes a list of points, a surface, and an axis and moves
    the points to the surface"""
    def __init__(self, surf=[], pts=[], axis=1, useNormal=False):
        """The runner class for Point Loft"""
        self.surf = surf
        self.pts = pts
        self.axis = axis
        self.useNormal = useNormal
        self.axisVectors = [[1, 0, 0], [0, 1, 0], [0, 0, 1], []]
        self.ptDeltas = [[0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 2, 3]]
    
    def run(self):
        if self.surf == [] or self.pts == []:
            logger.error('Not enough information was provided')
            return
        
        ptDelta = self.ptDeltas[self.axis]
        axis = self.axisVectors[self.axis]
        
        print 'axis %s' % axis
        print 'ptDelta %s' % ptDelta
        
        moveCount = 0
        failCount = 0
        for pt in self.pts:
            ptPos = pointPosition(pt)
            ptPos2 = ptPos - ptDelta
            c = curve(d=1, p=[ptPos2, ptPos], k=[0,1])
            if self.useNormal:
                proj = projectCurve(c, self.surf, un=True)
            else:
                proj = projectCurve(c, self.surf, d=axis)
            projC = proj[0].listConnections()[1]
            if objExists('%s.cv[0]' % projC):
                goalPt = pointPosition('%s.cv[0]' % projC)
                move(pt, goalPt, a=True, ws=True)
                moveCount += 1
            else:
                failCount += 1
            delete(c, proj)
        
        logger.info('%d point(s) were moved successfully' % moveCount)
        if failCount > 0:
            logger.warning('%d point(s) could not be moved' % failCount)





