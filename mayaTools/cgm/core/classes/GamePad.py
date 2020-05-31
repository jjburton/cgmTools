import threading 
import ctypes 
import time 
import cgm.core.lib.inputs as inputs
import os
import maya.cmds as mc


class GamePad(threading.Thread): 
    def __init__(self, name = "GamePad", updateVisual = True): 
        threading.Thread.__init__(self) 
        self.controller_model = None
        self.updateVisual = updateVisual

        #self.name = name

        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0

        self.left_trigger = 0.0
        self.right_trigger = 0.0

        self.left_bumper = 0
        self.right_bumper = 0

        self.button_select = 0
        self.button_start = 0

        self.thumbpad_x = 0
        self.thumbpad_y = 0

        self.button_y = 0
        self.button_x = 0
        self.button_a = 0
        self.button_b = 0

        self._on_press_subscribers = []
        self._on_release_subscribers = []

        self._parentCamera = None
              
    def run(self): 
        # target function of the thread class 
        try: 
            while True: 
                events = inputs.get_gamepad()
                for event in events:
                    has_pressed = False
                    has_released = False
                    #print(event.ev_type, event.code, event.state)
                    if event.code == 'ABS_Y':
                        self.left_stick_y = event.state / 32767.0
                    if event.code == 'ABS_X':
                        self.left_stick_x = event.state / 32767.0
                    if event.code == 'ABS_RX':
                        self.right_stick_x = event.state / 32767.0
                    if event.code == 'ABS_RY':
                        self.right_stick_y = event.state / 32767.0
                    if event.code == 'ABS_RZ':
                        self.right_trigger = event.state / 256.0
                    if event.code == 'ABS_Z':
                        self.left_trigger = event.state / 256.0
                    if event.code == 'BTN_TL':
                        self.left_bumper = event.state
                        if self.left_bumper:
                            self._on_press('LBumper')
                        else:
                            self._on_release('LBumper')
                    if event.code == 'BTN_TR':
                        self.right_bumper = event.state
                        if self.right_bumper:
                            self._on_press('RBumper')
                        else:
                            self._on_release('RBumper')
                    if event.code == 'ABS_HAT0X':
                        self.thumbpad_x = event.state
                    if event.code == 'ABS_HAT0Y':
                        self.thumbpad_y = event.state
                    if event.code == 'BTN_START':
                        self.button_start = event.state
                        if self.button_start:
                            self._on_press('Start')
                        else:
                            self._on_release('Start')
                    if event.code == 'BTN_SELECT':
                        self.button_select = event.state
                        if self.button_select:
                            self._on_press('Select')
                        else:
                            self._on_release('Select')
                    if event.code == 'BTN_WEST':
                        self.button_x = event.state
                        if self.button_x:
                            self._on_press('X')
                        else:
                            self._on_release('X')
                    if event.code == 'BTN_NORTH':
                        self.button_y = event.state
                        if self.button_y:
                            self._on_press('Y')
                        else:
                            self._on_release('Y')
                    if event.code == 'BTN_SOUTH':
                        self.button_a = event.state
                        if self.button_a:
                            self._on_press('A')
                        else:
                            self._on_release('A')
                    if event.code == 'BTN_EAST':
                        self.button_b = event.state
                        if self.button_b:
                            self._on_press('B')
                        else:
                            self._on_release('B')

                if self.updateVisual:
                    self.update_controller_model()

        finally: 
            print('\nended\n') 
    
    def get_state_dict(self):
        return {
            'left_stick_x':self.left_stick_x,
            'left_stick_y':self.left_stick_y,
            'right_stick_x':self.right_stick_x,
            'right_stick_y':self.right_stick_y,
            'left_trigger':self.left_trigger,
            'right_trigger':self.right_trigger,
            'left_bumper':self.left_bumper,
            'right_bumper':self.right_bumper,
            'button_select':self.button_select,
            'button_start':self.button_start,
            'thumbpad_x':self.thumbpad_x,
            'thumbpad_y':self.thumbpad_y,
            'button_y':self.button_y,
            'button_x':self.button_x,
            'button_a':self.button_a,
            'button_b':self.button_b
            }

    def get_id(self): 
  
        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id

    def update_controller_model(self):
        if not self.controller_model:
            return

        base = self.controller_model + '|PositionNode'

        # Right Stick
        mc.setAttr('{0}|RStick_Inner|RStick_Inner_On.v'.format(base), (abs(self.right_stick_y) + abs(self.right_stick_x)) > .1  )
        mc.setAttr('{0}|RStick_Inner.ty'.format(base), self.right_stick_y)
        mc.setAttr('{0}|RStick_Inner.tx'.format(base), self.right_stick_x)

        # Left Stick
        mc.setAttr('{0}|LStick_Inner|LStick_Inner_On.v'.format(base), (abs(self.left_stick_y) + abs(self.left_stick_x)) > .1  )
        mc.setAttr('{0}|LStick_Inner.ty'.format(base), self.left_stick_y)
        mc.setAttr('{0}|LStick_Inner.tx'.format(base), self.left_stick_x)

        # Bumpers/Triggers
        mc.setAttr('{0}|BumperOutline|LTrigger_On.v'.format(base), self.left_trigger > .1  )
        mc.setAttr('{0}|BumperOutline|LBumper_On.v'.format(base), self.left_bumper > .1  )
        
        mc.setAttr('{0}|BumperOutline|RTrigger_On.v'.format(base), self.right_trigger > .1  )
        mc.setAttr('{0}|BumperOutline|RBumper_On.v'.format(base), self.right_bumper > .1  )

        # Buttons
        mc.setAttr('{0}|AButton|AButton_On.v'.format(base), self.button_a > .1  )
        mc.setAttr('{0}|BButton|BButton_On.v'.format(base), self.button_b > .1  )
        mc.setAttr('{0}|XButton|XButton_On.v'.format(base), self.button_x > .1  )
        mc.setAttr('{0}|YButton|YButton_On.v'.format(base), self.button_y > .1  )

        mc.setAttr('{0}|Start|Start_On.v'.format(base), self.button_start > .1  )
        mc.setAttr('{0}|Select|Select_On.v'.format(base), self.button_select > .1  )

        # ThumbPad
        mc.setAttr('{0}|ThumbPad_Down|ThumbPad_Down_On.v'.format(base), self.thumbpad_y > .1  )
        mc.setAttr('{0}|ThumbPad_Up|ThumbPad_Up_On.v'.format(base), self.thumbpad_y < -.1  )
        mc.setAttr('{0}|ThumbPad_Left|ThumbPad_Left_On.v'.format(base), self.thumbpad_x < -.1  )
        mc.setAttr('{0}|ThumbPad_Right|ThumbPad_Right_On.v'.format(base), self.thumbpad_x > .1  )

        # currentCam = CAM.getCurrentCamera()
        # if self._parentCamera != currentCam:
        #     self._parentCamera = currentCam
        #     mc.delete(mc.listRelatives(self.controller_model, type='Constraint'))
        #     mc.parentConstraint(currentCam, self.controller_model, mo=False)

    def import_controller_model(self):
        controller_file = os.path.join( '/'.join(__file__.split('core')[:-1]), 'assets', 'cgmController.mb' )
        mc.file( controller_file, i=True, type="mayaBinary", ignoreVersion=True)
        self.controller_model = mc.ls('*.cgmController')[0].split('.')[0]
    
    def start_listening(self):
        self.import_controller_model()
        self.start()

    def stop_listening(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
              ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure') 

        if mc.objExists(self.controller_model):
            mc.delete(self.controller_model)
            self.controller_model = None
            self._parentCamera = None

    def on_press_subscribe(self, func):
        self._on_press_subscribers.append(func)

    def on_release_subscribe(self, func):
        self._on_release_subscribers.append(func)

    def _on_press(self, btn):
        for f in self._on_press_subscribers:
            f(btn)

    def _on_release(self, btn):
        for f in self._on_release_subscribers:
            f(btn)
