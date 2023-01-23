# 
#   -= ml_breakdownDragger.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 3, 2011-01-02
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_breakdownDragger.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_breakdownDragger
#     ml_breakdownDragger.drag()
# From MEL, this looks like:
#     python("import ml_breakdownDragger;ml_breakdownDragger.drag()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Blend a keyframe or pose with the next or previous keys, essentially
# creating a breakdown pose that is weighted one way or the other.
# The weight of the blend is controlled by dragging the mouse in the viewport.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# Run the tool, and the cursor will turn into a hand. Left-click and hold in
# the viewport, and then drag either left or right to weight the key to the
# next or previous key.
# Alternately, press and hold the middle mouse button to weight the key toward
# or away from the average of the surrounding keys.
# If you have no keys selectd, the tool will act only on curves
# that are visibile in the graph editor. If there are no keys at the 
# current frame, keys will be set.
#      ____________________
# - -/__ Video Tutorial __/- - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# http://www.youtube.com/watch?v=D8yD4zbHTP8
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 3

import maya.cmds as mc
import maya.mel as mm

def drag():
    '''The primary command to run the tool'''
    BreakdownDragger()

class Dragger(object):
    '''A base class for creating a draggerContext tool in Maya'''
    def __init__(self,
                name = 'mlDraggerContext',
                title = 'Dragger',
                defaultValue=0,
                minValue=None,
                maxValue=None,
                multiplier=0.01,
                cursor='hand'
                ):
        '''
        Args:
            name:           The name of the context tool in Maya
            title:          The nice name of the tool
            defaultValue:   The starting value of the dragger when the mouse button is pushed.
            minValue:       If specified, clamp the minimum output at this value
            maxValue:       If specified, clamp the maximum output at this value
            multiplier:     Scale the output of the dragger by this value.
            cursor:         What type of cursor to display, see Maya's draggerContext for options
        '''
        self.multiplier = multiplier
        self.defaultValue = defaultValue
        self.minValue = minValue
        self.maxValue = maxValue
        
        self.draggerContext = name
        if not mc.draggerContext(self.draggerContext, exists=True):
            self.draggerContext = mc.draggerContext(self.draggerContext)
                                                    
        mc.draggerContext(self.draggerContext, edit=True,
                        pressCommand=self.press, 
                        dragCommand=self.drag,
                        releaseCommand=self.release,
                        cursor=cursor,
                        drawString=title,
                        undoMode='all'
                        )
                                                    
    
    def press(self, *args):
        '''
        This method is called when the mouse is pressed, and initializes the mouse position.
        Be careful overwriting the press method in child classes, because of the undoInfo openChunk.
        '''
        
        self.anchorPoint = mc.draggerContext(self.draggerContext, query=True, anchorPoint=True)
        self.modifier = mc.draggerContext(self.draggerContext, query=True, modifier=True)
        self.button = mc.draggerContext(self.draggerContext, query=True, button=True)
        #dragString
        
        # This makes it so the script editor doesn't get spammed by a cycle in the puppet
        mc.cycleCheck(evaluation=False)
        
        # This turns off the undo queue until we're done dragging, so we can undo it.
        mc.undoInfo(openChunk=True)
        
        
    def drag(self, *args):
        '''Called continuously when holding the mouse button down, updates self.x and self.y with the mouse position,
        and runs the corresponding method for whichever button is being pressed.'''
        self.dragPoint = mc.draggerContext(self.draggerContext, query=True, dragPoint=True)
        
        self.x = ((self.dragPoint[0] - self.anchorPoint[0]) * self.multiplier) + self.defaultValue
        self.y = ((self.dragPoint[1] - self.anchorPoint[1]) * self.multiplier) + self.defaultValue
        
        if self.minValue is not None and self.x < self.minValue:
            self.x = self.minValue
        if self.maxValue is not None and self.x > self.maxValue:
            self.x = self.maxValue
        
        #dragString
        if self.modifier == 'control':
            if self.button == 1:
                self.dragControlLeft()
            elif self.button == 2:
                self.dragControlMiddle()
        elif self.modifier == 'shift':
            if self.button == 1:
                self.dragShiftLeft()
            elif self.button == 2:
                self.dragShiftMiddle()
        else:
            if self.button == 1:
                self.dragLeft()
            elif self.button == 2:
                self.dragMiddle()
        
        mc.refresh()
    
    def release(self, *args):
        '''
        Called when the mouse button is released, and cleans up after the tool.
        Be careful overwriting the release method in child classes. Not closing the undo chunk leaves maya in a sorry state.
        '''
        # close undo chunk and turn cycle check back on
        mc.undoInfo(closeChunk=True)
        mc.cycleCheck(evaluation=True)
        mm.eval('SelectTool')
    
    def drawString(self, message):
        '''Simply writes a message next to the cursor'''
        mc.draggerContext(self.draggerContext, edit=True, drawString=message)
        
    def dragLeft(self):
        '''Placeholder meant to be overridden in child classes'''
        pass
            
    def dragMiddle(self):
        '''Placeholder meant to be overridden in child classes'''
        pass
        
    def dragControlLeft(self):
        '''Placeholder meant to be overridden in child classes'''
        pass
            
    def dragControlMiddle(self):
        '''Placeholder meant to be overridden in child classes'''
        pass
        
    def dragShiftLeft(self):
        '''Placeholder meant to be overridden in child classes'''
        pass
            
    def dragShiftMiddle(self):
        '''Placeholder meant to be overridden in child classes'''
        pass
    
    #no drag right, because that is monopolized by the right click menu
    #no alt drag, because that is used for the camera
    
    def setTool(self):
        mc.setToolTo(self.draggerContext)


class BreakdownDragger(Dragger):
    '''Creates the tool and manages the data'''

    def __init__(self, 
                 name='mlBreakdownDraggerContext',
                 minValue=None,
                 maxValue=None,
                 defaultValue=0,
                 title = 'Breakdown'):
        
        sel = mc.ls(sl=True)
        if not sel:
            return
        
        Dragger.__init__(self, defaultValue=defaultValue, minValue=minValue, maxValue=maxValue, name=name, title=title)

        selected = False
        time = mc.currentTime(query=True)
        curves = mc.keyframe(query=True, name=True, selected=True)
        if curves:
            #try selected keys first
            selected = True
        else:
            #then visible in graph editor
            graphVis = mc.selectionConnection('graphEditor1FromOutliner', query=True, obj=True)
            if graphVis:
                curves = mc.keyframe(graphVis, query=True, name=True)
            else:
                #otherwise try keyed channels.
                curves = mc.listConnections(sel, s=True, d=False, type='animCurve')
                if not curves:
                    return
                    
        #cull unkeyable curves
        remove = list()
        for c in curves:
            if mc.referenceQuery(c, isNodeReferenced=True):
                remove.append(c)
            else:
                plug = mc.listConnections('.'.join((c,'output')), source=False, plugs=True)[0]
                if not mc.getAttr(plug, keyable=True) and not mc.getAttr(plug, settable=True):
                    remove.append(c)
        
        if remove:
            for r in remove:
                curves.remove(r)
        
        if not curves:
            return
        
        if not selected:
            mc.setKeyframe(curves)
        
        itt = 'plateau'
        ott = 'plateau'
        if mc.keyTangent(query=True, g=True, ott=True)[0]=='linear':
            itt='linear'
            ott='linear'
        elif mc.keyTangent(query=True, g=True, ott=True)[0]=='step':
            itt='linear'
            ott='step'

        self.curves = curves
        self.time = dict()
        self.value = dict()
        self.next = dict()
        self.prev = dict()
        self.average = dict()

        for curve in self.curves:
            if selected:
                self.time[curve] = mc.keyframe(curve, query=True, timeChange=True, sl=True)
                self.value[curve] = mc.keyframe(curve, query=True, valueChange=True, sl=True)
            else:
                self.time[curve] = [time]
                self.value[curve] = mc.keyframe(curve, time=(time,), query=True, valueChange=True)
                
            self.next[curve] = list()
            self.prev[curve] = list()
            self.average[curve] = list()
            
            for i in self.time[curve]:
                next = mc.findKeyframe(curve, time=(i,), which='next')
                prev = mc.findKeyframe(curve, time=(i,), which='previous')
                n = mc.keyframe(curve, time=(next,), query=True, valueChange=True)[0]
                p = mc.keyframe(curve, time=(prev,), query=True, valueChange=True)[0]
                
                self.next[curve].append(n)
                self.prev[curve].append(p)
                self.average[curve].append((n+p)/2)
                
                #set the tangents on this key, and the next and previous, so they flatten properly
                #if not mc.keyTangent(query=True, g=True, ott=True)[0]=='linear' and not mc.keyTangent(query=True, g=True, ott=True)[0]=='step':
                mc.keyTangent(curve, time=(i,), itt=itt, ott=ott)
                mc.keyTangent(curve, time=(next,), itt=itt)
                mc.keyTangent(curve, time=(prev,), ott=ott)
        
        self.setTool()
        self.drawString('Left: Weight Prev/Next, Middle: Weight Average')
        mm.eval('warning "Left: Weight Prev/Next, Middle: Weight Average"')
            
    def dragLeft(self):
        '''This is activated by the left mouse button, and weights to the next or previous keys.'''

        #clamp it
        if self.x < -1:
            self.x = -1
        if self.x > 1:
            self.x = 1
            
        if self.x > 0:
            self.drawString('>> '+str(int(self.x*100))+' %')
            for curve in self.curves:
                for i,v,n in zip(self.time[curve],self.value[curve],self.next[curve]):
                    mc.keyframe(curve, time=(i,), valueChange=v+((n-v)*self.x))
        elif self.x <0:
            self.drawString('<< '+str(int(self.x*-100))+' %')
            for curve in self.curves:
                for i,v,p in zip(self.time[curve],self.value[curve],self.prev[curve]):
                    mc.keyframe(curve, time=(i,), valueChange=v+((p-v)*(-1*self.x)))
                    
    def dragMiddle(self):
        '''This is activated by the middle mouse button, and weights to the average of the surrounding keys.'''
        
        #clamp it
        if self.x < -1:
            self.x = -1
        if self.x > 1:
            self.x = 1
            
        self.drawString('Average '+str(int(self.x*100))+' %')
        for curve in self.curves:
            for i,v,n in zip(self.time[curve],self.value[curve],self.average[curve]):
                mc.keyframe(curve, time=(i,), valueChange=v+((n-v)*self.x))

    def dragShiftLeft(self):
        '''This is activated by Shift and the left mouse button, and weights to the next or previous keys, without clamping.'''
        if self.x > 0:
            self.drawString('>> '+str(int(self.x*100))+' %')
            for curve in self.curves:
                for i,v,n in zip(self.time[curve],self.value[curve],self.next[curve]):
                    mc.keyframe(curve, time=(i,), valueChange=v+((n-v)*self.x))
        elif self.x <0:
            self.drawString('<< '+str(int(self.x*-100))+' %')
            for curve in self.curves:
                for i,v,p in zip(self.time[curve],self.value[curve],self.prev[curve]):
                    mc.keyframe(curve, time=(i,), valueChange=v+((p-v)*(-1*self.x)))
