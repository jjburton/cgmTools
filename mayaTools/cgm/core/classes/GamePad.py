import threading 
import ctypes 
import time 
import cgm.core.lib.inputs as inputs

class GamePad(threading.Thread): 
    left_stick_x = 0.0
    left_stick_y = 0.0
    right_stick_x = 0.0
    right_stick_y = 0.0

    left_trigger = 0.0
    right_trigger = 0.0

    left_bumper = 0
    right_bumper = 0

    button_select = 0
    button_start = 0

    thumbpad_x = 0
    thumbpad_y = 0

    button_y = 0
    button_x = 0
    button_a = 0
    button_b = 0

    _on_press_subscribers = []
    _on_release_subscribers = []

    def __init__(self, name): 
        threading.Thread.__init__(self) 
        self.name = name
              
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
                    elif event.code == 'ABS_X':
                        self.left_stick_x = event.state / 32767.0
                    elif event.code == 'ABS_RX':
                        self.right_stick_x = event.state / 32767.0
                    elif event.code == 'ABS_RY':
                        self.right_stick_y = event.state / 32767.0
                    elif event.code == 'ABS_RZ':
                        self.right_trigger = event.state / 256.0
                    elif event.code == 'ABS_Z':
                        self.left_trigger = event.state / 256.0
                    elif event.code == 'BTN_TL':
                        self.left_bumper = event.state
                        if self.left_bumper:
                            self._on_press('LBumper')
                        else:
                            self._on_release('LBumper')
                    elif event.code == 'BTN_TR':
                        self.right_bumper = event.state
                        if self.right_bumper:
                            self._on_press('RBumper')
                        else:
                            self._on_release('RBumper')
                    elif event.code == 'ABS_HAT0X':
                        self.thumbpad_x = event.state
                    elif event.code == 'ABS_HAT0Y':
                        self.thumbpad_y = event.state
                    elif event.code == 'BTN_START':
                        self.button_start = event.state
                        if self.button_start:
                            self._on_press('Start')
                        else:
                            self._on_release('Start')
                    elif event.code == 'BTN_SELECT':
                        self.button_select = event.state
                        if self.button_select:
                            self._on_press('Select')
                        else:
                            self._on_release('Select')
                    elif event.code == 'BTN_WEST':
                        self.button_x = event.state
                        if self.button_x:
                            self._on_press('X')
                        else:
                            self._on_release('X')
                    elif event.code == 'BTN_NORTH':
                        self.button_y = event.state
                        if self.button_y:
                            self._on_press('Y')
                        else:
                            self._on_release('Y')
                    elif event.code == 'BTN_SOUTH':
                        self.button_a = event.state
                        if self.button_a:
                            self._on_press('A')
                        else:
                            self._on_release('A')
                    elif event.code == 'BTN_EAST':
                        self.button_b = event.state
                        if self.button_b:
                            self._on_press('B')
                        else:
                            self._on_release('B')

        finally: 
            print('ended') 
    
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

    def start_listening(self):
        self.start()

    def stop_listening(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
              ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure') 

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
