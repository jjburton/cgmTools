import threading 
import ctypes 
import time 
import cgm.core.lib.inputs as inputs

class Keyboard(threading.Thread): 
    _on_press_subscribers = []
    _on_release_subscribers = []

    def __init__(self): 
        threading.Thread.__init__(self) 
              
    def run(self): 
        # target function of the thread class 
        try: 
            while True: 
                events = inputs.get_mouse()
                for event in events:
                    print(event.ev_type, event.code, event.state)

        finally: 
            print('ended') 

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
