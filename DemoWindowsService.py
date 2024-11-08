import time
import servicemanager
import win32serviceutil
import win32service
import win32event
import os

class MyPythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MyPythonService"
    _svc_display_name_ = "My Python Background Service"
    _svc_description_ = "This service runs a Python script in the background."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False

    def SvcStop(self):
        self.stop_requested = True
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))

        # Run your Python script here
        self.main()

    def main(self):
        while not self.stop_requested:
            # Add the code to run your Python script
            with open(r"C:/Users/aayus/OneDrive/Desktop/Python/CSC 502/ServiceLogFile.txt", "a") as f:
                f.write(f"Service is running at {time.ctime()}\n")
            time.sleep(10)  # Wait 10 seconds before writing again


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyPythonService)
