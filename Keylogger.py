import threading
import time
from pynput import keyboard

class TimedKeyListener:
    def __init__(self, timeout=60):
        self.timeout = timeout  # Inactivity timeout in seconds
        self.last_key_time = time.time()  # Track the last keypress time
        self.listener = None  # Keyboard listener instance
        self.timer_thread = None  # Thread for monitoring
        self.active = False  # Track listener activity state
        self.restart_event = threading.Event()  # Event to signal restart

    def on_press(self, key):
        self.last_key_time = time.time()
        print(f"Key pressed: {key}")

        # Restart listener if it's inactive
        # if not self.active:
        #     self.restart_event.set()  # Signal the event to restart the listener

    def start_listener(self):
        if  self.active==False:
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
            self.active = True
            print("Listener started")

    def stop_listener(self):
        if self.listener is not None:
            print("No key pressed for a minute, stopping listener...")
            self.listener.stop()
            self.listener = None
            self.active = False

    def monitor_activity(self):
        while True:
            # Check for inactivity
            if self.active == True and (time.time() - self.last_key_time) > self.timeout:
                self.stop_listener()

            # Wait for the restart event to be set, which happens on any key press
            if self.active == False:
                print("Waiting for key press to restart listener...")
                self.restart_event.wait()  # Block until the event is set
                self.restart_event.clear()  # Clear the event after restarting the listener
                print("here!!!")
                self.start_listener()

            time.sleep(1)  # Avoid busy waiting, check every second

    def monitor_keypress_for_restart(self):
        # This method will always run a lightweight listener to catch key presses
        def on_press_restart(key):
            if self.active == False:
                self.restart_event.set()  # Set the event to restart the main listener

        # This listener will always be active, independent of the main listener
        restart_listener = keyboard.Listener(on_press=on_press_restart)
        restart_listener.start()

    def start(self):
        # Start the listener and the monitoring thread
        self.start_listener()
        self.timer_thread = threading.Thread(target=self.monitor_activity)
        self.timer_thread.daemon = True  # Daemon thread will exit when the program exits
        self.timer_thread.start()

        # Start the restart monitoring thread
        restart_thread = threading.Thread(target=self.monitor_keypress_for_restart)
        restart_thread.daemon = True
        restart_thread.start()

if __name__ == "__main__":
    timed_listener = TimedKeyListener(timeout=60)
    timed_listener.start()

    # Keep the program running to allow the timer thread to work
    while True:
        time.sleep(10)
