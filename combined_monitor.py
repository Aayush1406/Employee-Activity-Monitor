from EmployeeActivityMonitor import ActivityMonitor
from Keylogger import TimedKeyListener
from MouseActivity import TimedMouseListener

import threading

def run_activity_monitor():
    employee_activity_monitor = ActivityMonitor()
    employee_activity_monitor.main()


def run_timed_key_listener():
    timed_key_listener = TimedKeyListener(timeout=60)
    timed_key_listener.start()
    
def run_timed_mouse_listener():
    timed_mouse_listener = TimedMouseListener(timeout=60)
    timed_mouse_listener.start()

if __name__=="__main__":
    
    employee_activity_thread = threading.Thread(target=run_activity_monitor)
    key_listener_thread = threading.Thread(target = run_timed_key_listener)
    mouse_listener_thread = threading.Thread(target = run_timed_mouse_listener)
    
    employee_activity_thread.start()
    key_listener_thread.start()
    mouse_listener_thread.start()
    
    employee_activity_thread.join()
    key_listener_thread.join()
    mouse_listener_thread.join()
