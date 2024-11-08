import threading
from pynput import mouse
import time

class TimedMouseListener:
    
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.active = False
        self.last_mouse_activity = time.time()
        self.mouse_listener = None
        self.restart_event = threading.Event()
        
        
    def start_mouse_listener(self):
        
        if self.active == False:
            self.mouse_listener = mouse.Listener(on_move = self.on_move, on_click = self.on_click)
            self.mouse_listener.start()
            self.active = True
            print("Mouse listener is active")
    
    def on_move(self, x, y):
        self.last_mouse_activity = time.time()
        print(f"Mouse moved from {x} to {y}")
        
    def on_click(self, x, y, button, pressed):
        self.last_mouse_activity = time.time()
        
        if pressed:
            print(f"Mouse clicked at ({x},{y}) with {button}")
    
    def stop_mouse_listener(self):
        
        if self.mouse_listener is not None:
            print("Mouse listener is stopped ! no mouse movement for a minute")
            self.mouse_listener.stop()
            self.active = False
            self.mouse_listener = None #Looks like not necessary
    
    def monitor_activity(self):
        
        while True:
        
            if (self.active == True) and (time.time() - self.last_mouse_activity > 60):
                self.stop_mouse_listener()
                
            if self.active == False:
                print("Waiting for a mouse movement to occur")
                self.restart_event.wait()
                self.restart_event.clear()
                self.start_mouse_listener()
            # print("monitor_activity method thread running")
            time.sleep(1)
    
    def monitor_keypress_for_restart(self):
        
        restart_listener = mouse.Listener(on_move=lambda x, y : self.on_activity_detected(), on_click=lambda x,y,pressed,button : self.on_activity_detected())         
        restart_listener.start()
    
    def on_activity_detected(self):
    
        if self.active == False:
            self.restart_event.set()
    
    
    def start(self):
        
        self.start_mouse_listener() # starts the listening thread
        
        self.monitor_activity_thread = threading.Thread(target=self.monitor_activity)
        self.monitor_activity_thread.daemon = True   
        self.monitor_activity_thread.start() # starts the monitory_activity thread
        
        self.monitor_keypress_for_restart_thread = threading.Thread(target=self.monitor_keypress_for_restart)
        self.monitor_keypress_for_restart_thread.daemon = True
        self.monitor_keypress_for_restart_thread.start()
    
if __name__ == "__main__":
        
    timed_mouse_listener = TimedMouseListener(timeout = 60)        
    timed_mouse_listener.start()
    
    while True:
        
        time.sleep(1)
        