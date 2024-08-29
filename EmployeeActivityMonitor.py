# The main goal is to acess Windows API function. These Windows API function are defined in C with having libraries like for eg: Winuser.h, Windef.h, Windowsx.h, Winbase.h, Olectl.h.
# These functions are typically part of DLLs and is in the compiled form. Through Ctype library we can access this in python.
import psutil 
import ctypes #python module to interact with c libraries. 
from ctypes import wintypes #ctypes, a module to interact with c-compatible DLL
import time
import datetime
import win32api
import win32con
import win32process
import win32gui
from datetime import datetime
import pypyodbc as odbc
import pyodbc
import mysql.connector
from mysql.connector import pooling


# conn = mysql.connector.connect(
#     host="localhost",  # e.g., 'localhost' or your AWS RDS endpoint
#     user="root",  # MySQL username
#     password="aayush",  # MySQL password
#     database="Device_Data"  # The database you are connecting to
# )

connection_pool = pooling.MySQLConnectionPool(
   
    pool_name = "mypool",
    host="localhost",  # e.g., 'localhost' or your AWS RDS endpoint
    user="root",  # MySQL username
    password="aayush",  # MySQL password
    database="Device_Data"  # The database you are connecting to    
)

# cursor = conn.cursor()

def get_connection():
    return connection_pool.get_connection()


user32 = ctypes.windll.user32 #loads user32 DLL into python script.

def get_foreground_process_id():
        
    handle = user32.GetForegroundWindow() # retrieves handle (unique indentifier of a system resource) of the window with which user is currentlt working.
        
    pid = wintypes.DWORD() # create a DWORD data type created using python ctypes. Its a 32 bit unsigned integer
        
    user32.GetWindowThreadProcessId(handle, ctypes.byref(pid)) #GetWindowThreadProcessID(), returns the identifier of the thread that created the window. Eg: Process ID.

    #The above fun expects handle and LPDOWRD (long pointer to DWORD. So actually it contains mem. address of DWORD where process id is stored). ctypes.byref(pid) converts pid to a pointer. 

    return pid.value, handle

class Titlebarinfo(ctypes.Structure):
    _fields_ = [("cbSize",wintypes.DWORD),
                ("rcTitleBar",wintypes.RECT),
                ("rgstate",wintypes.DWORD*6)]

def get_title_bar_info(handle):
    titleBarInfo = Titlebarinfo()
    titleBarInfo.cbSize = ctypes.sizeof(Titlebarinfo)
    user32.GetTitleBarInfo(handle,ctypes.byref(titleBarInfo))    
    return titleBarInfo

def get_executable_path_from_Pid(pid):
    try:
        process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
        executable_path = win32process.GetModuleFileNameEx(process_handle, 0)
        win32api.CloseHandle(process_handle)
        return executable_path
    except Exception as e:
        return None
    
def get_uwp_app_name(pid):
    try:
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            return child.name()
    except Exception as e:
        return None
    
class TITLEBARINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD),
                ("rcTitleBar", wintypes.RECT),
                ("rgstate", wintypes.DWORD * 6)]    

def get_title_bar_info(hwnd):
    tbi = TITLEBARINFO()
    tbi.cbSize = ctypes.sizeof(TITLEBARINFO)
    ctypes.windll.user32.GetTitleBarInfo(hwnd, ctypes.byref(tbi))
    return tbi

def get_window_title(current_handle,pid):
    old_handle = None

    if current_handle != old_handle:
        return win32gui.GetWindowText(current_handle)

def calculateTimeForHandle(currentTime, currentHandle, pid):
    process = psutil.Process(pid)
    processStartTime = process.create_time()
    processStartTime = datetime.fromtimestamp(processStartTime)
    processStartTime = processStartTime.strftime('%H:%M:%S')
    
    duration = datetime.strptime(currentTime,'%H:%M:%S' ) - datetime.strptime(processStartTime,'%H:%M:%S')
    return duration

def get_process_create_time(pid):
    process = psutil.Process(pid)    
    process_create_time = datetime.fromtimestamp(process.create_time())
    process_create_time = process_create_time.strftime('%m-%d-%y %H:%M:%S %p')
    return process_create_time

def get_process_name(pid):
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        return process_name
    except psutil.NoSuchProcess:
        return "No Such Process"
    
def get_process_status(pid):
    process = psutil.Process(pid)
    process_status = process.status()
    return process_status

def print_foreground_details(foreground_details):
    
    print("-----------------------------------------") # Break section between two processes.    
    print("Window Title = ",foreground_details['window_title'])      
    print("Process Name = ",foreground_details['process_name'])    
    print("Process id = ",foreground_details['pid'])
    print("Process Status = ",foreground_details['process_status'])    
    print("Child Name = ",foreground_details['child_name'])    
    print("Executable Path = ",foreground_details['executable_path'])        
    print("Process Create Time = ",foreground_details['process_create_time'])    
    print("Handle = ",foreground_details['current_handle']) 
    # print("Title Bar Information = ",foreground_details['title_bar_info'])

    
def get_foreground_process_details(pid, current_handle):

    
    executable_path = get_executable_path_from_Pid(pid)
    child_name = get_uwp_app_name(pid)
    title_bar_info = get_title_bar_info(current_handle)
    window_title = get_window_title(current_handle,pid)
    process_create_time = get_process_create_time(pid)                
    process_name = get_process_name(pid)
    process_status = get_process_status(pid)
    
    # print_foreground_details(executable_path, child_name, title_bar_info, window_title, process_create_time, process_name, process_status,pid,current_handle)

    return {
        "executable_path": executable_path,
        "child_name": child_name,
        "title_bar_info": title_bar_info,
        "window_title": window_title,
        "process_create_time": process_create_time,
        "process_name": process_name,
        "process_status": process_status,
        "pid": pid,
        "current_handle": current_handle
    } 


def insert_foreground_process_details_in_db(foreground_details):
    try:
        conn = get_connection()
        cursor = conn.cursor()    
        insert_query = """ 
        INSERT INTO applicationusagelogs(Title_Name, Child_Name, Executable_Path, Process_Name, Process_Status, Process_Create_Time ,Pid, Current_Handle, Duration, Window_Start_Time, Window_End_Time, Window_Active_Status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s , %s, %s ) """
        cursor.execute(insert_query,(foreground_details['window_title'],foreground_details['child_name'], foreground_details['executable_path'],
                                    foreground_details['process_name'],foreground_details['process_status'],foreground_details['process_create_time'],
                                    foreground_details['pid'], foreground_details['current_handle'], None, None, None, None ))
        conn.commit()
        print("record inserted into db successfully !")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

        
def calculate_window_end_time(old_pid):
    
    try:
        conn = get_connection()
        cursor = conn.cursor() 
        select_query = "SELECT * FROM applicationusagelogs WHERE Pid = %s and Window_Active_Status = %s"
        cursor.execute(select_query, (old_pid,'Active'))
        record_value = cursor.fetchone()
        # print("----->",record_value)
        if record_value:
            update_query = "Update applicationusagelogs set Window_End_Time = %s where Pid = %s and Window_Active_Status=%s"
            current_time = datetime.now()
            current_time = current_time.strftime('%m-%d-%y %H:%M:%S %p')
            cursor.execute(update_query, (current_time, old_pid,'Active'))
            conn.commit()
            # set_inactive_window_status(old_pid)
            print("Window End Time = ", current_time)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()        
    
def calculate_window_start_time(pid, window_title_name):

    try:
        conn = get_connection()
        cursor = conn.cursor() 
        set_active_window_status(pid)    
        update_query = "Update ApplicationUsageLogs set Window_Start_Time = %s where Pid = %s and Window_Active_Status = %s"
        current_time = datetime.now()
        current_time = current_time.strftime('%m-%d-%y %H:%M:%S %p')
        cursor.execute(update_query,(current_time, pid,'Active'))
        conn.commit()
        print('Window Start Time = ',current_time)
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()        



def set_active_window_status(pid):

    try:
        conn = get_connection()
        cursor = conn.cursor()     
        update_query = "Update ApplicationUsageLogs set Window_Active_Status = %s where Pid = %s and Window_Start_Time is Null"
        cursor.execute(update_query,('Active',pid))
        conn.commit()

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()        


def set_inactive_window_status(pid):

    try:
        conn = get_connection()
        cursor = conn.cursor()     
        update_query = "Update ApplicationUsageLogs set Window_Active_Status = %s where Pid = %s and Window_End_Time is Not Null"
        cursor.execute(update_query,('Inactive',pid))
        conn.commit()
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()        

def check_process_status(pid,handle):
    process_name = get_process_name(pid)
    # print("Last running process =",process_name)

    try:
        conn = get_connection()
        cursor = conn.cursor()     
        select_query = "SELECT * FROM applicationusagelogs WHERE Pid = %s"
        cursor.execute(select_query, (pid,))
        record_value = cursor.fetchall()
        
        if record_value and get_process_name(pid)=="No Such Process":   
            
            update_select_query = """UPDATE ApplicationUsageLogs AS t1
                                    JOIN (
                                        SELECT Pid, MAX(Window_End_Time) AS max_end_time
                                        FROM ApplicationUsageLogs
                                        WHERE Pid = %s
                                        GROUP BY Pid
                                    ) AS t2
                                    ON t1.Pid = t2.Pid AND t1.Window_End_Time = t2.max_end_time
                                    SET t1.Process_Status = %s;
                                    """   
            cursor.execute(update_select_query,(pid,"Stopped"))
            conn.commit()        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()        

    
def calculate_process_duration(old_pid):

    try:
        conn = get_connection()
        cursor = conn.cursor()     
        select_query = "Select Window_Start_Time, Window_End_Time from ApplicationUsageLogs where Pid = %s and Window_Active_Status = %s"
        cursor.execute(select_query, (old_pid,'Active'))
        rows = cursor.fetchall()
        duration = None
        if rows:
            for row in rows:
                window_start_time = datetime.strptime(row[0],'%m-%d-%y %H:%M:%S %p')             
                window_end_time = datetime.strptime(row[1], '%m-%d-%y %H:%M:%S %p')
                duration = window_end_time - window_start_time
                print("duration = ",duration)
    
            update_query = "Update ApplicationUsageLogs set duration = %s where Pid = %s and Window_Active_Status = %s"            
            cursor.execute(update_query,(duration,old_pid,'Active'))
            conn.commit()
        set_inactive_window_status(old_pid)

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()        

    
def keep_running_script(time_interval):

    old_pid = None
    old_handle = None
    while True:
        
        current_pid, current_handle = get_foreground_process_id()
     
        if old_pid != current_pid and old_handle != current_handle and current_pid!= 22824:
            foreground_details = get_foreground_process_details(current_pid, current_handle)
            print_foreground_details(foreground_details)
            insert_foreground_process_details_in_db(foreground_details)                                   
            calculate_window_start_time(current_pid, foreground_details['window_title'])
            calculate_window_end_time(old_pid)
            check_process_status(old_pid,old_handle)
            calculate_process_duration(old_pid)

            
            # calculateWindowEndTime(old_pid,old_handle)         
            
        old_pid = current_pid
        old_handle = current_handle   
        time.sleep(time_interval)


def main():

    time_interval = 1
    keep_running_script(time_interval)
    
if __name__ == "__main__":
  main()
