from pymel.core import *

def doIt():
    CurveSlider()

class CurveSlider(object):
    def __init__(self):
        self.create()
    
    def create(self):
        if window('slideWin', q=True, ex=True):
            deleteUI('slideWin')
        with window('slideWin', tlb=True, mxb=False, t='Slide Curves'):
            with formLayout(nd=100) as form:
                self.slider = intSliderGrp(field=True, v=1, min=1, max=20)
                btn1 = button(l='<', c=Callback(self.slideCurvesGUI, 1))
                btn2 = button(l='>', c=Callback(self.slideCurvesGUI, -1))
            formLayout(form, e=True, af=[(btn1, 'left', 2), (btn2, 'right', 2),
                                         (self.slider, 'left', 2), (self.slider, 'right', 2)],
                                     ap=[(btn1, 'right', 1, 50), (btn2, 'left', 1, 50)],
                                     ac=[(self.slider, 'top', 2, btn1)])
    
    def slideCurvesGUI(self, d=1):
        self.slideCurves(intSliderGrp(self.slider, q=True, v=True) * d)
    
    def slideCurves(self, d=1):
        selList = ls(sl=True)
        for obj in selList:
            nodes = keyframe(obj,query=True,name=True)
            for node in nodes:
               keyTimes = keyframe(node, q=True, tc=True)
               #query values at delta
               newValues = []
               for time in keyTimes:
                   newValues.append(keyframe(node, t=int(time+d), q=True, ev=True))
               #assign new values
               for i in range(0, len(keyTimes)):
                   keyframe(node, e=True, t=int(keyTimes[i]), vc=newValues[i][0])