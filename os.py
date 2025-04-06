import os
import sys
import shutil
import socket
import platform
import subprocess
import random
import hashlib
from sympy import sympify
import json
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import zipfile
import signal

start_time = time.time()
BASE_DIR = os.path.abspath("data/0/")
PASSWORD_FILE = os.path.abspath("data/password.json")
current_dir = BASE_DIR
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BASE_DIR, exist_ok=True)


def zip_file(source, zip_name):
    source_path = os.path.join(current_dir, source)
    zip_path = os.path.join(current_dir, zip_name)

    if not os.path.exists(source_path):
        print("Error: Source file or folder not found.")
        return

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(source_path):
                for root, _, files in os.walk(source_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        zipf.write(full_path, os.path.relpath(full_path, current_dir))
            else:
                zipf.write(source_path, os.path.basename(source_path))
        print(f"Success: '{zip_name}' created.")
    except Exception as e:
        print(f"Error creating ZIP: {e}")
        
def unzip_file(zip_name):
    zip_path = os.path.join(current_dir, zip_name)

    if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
        print("Error: ZIP file not found or invalid.")
        return

    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(current_dir)
        print(f"Success: '{zip_name}' extracted.")
    except Exception as e:
        print(f"Error extracting ZIP: {e}")
def move_file_or_folder(src, dest, root_mode=False):
    src_path = os.path.abspath(os.path.join(current_dir, src))
    dest_path = os.path.abspath(os.path.join("flame" if root_mode else current_dir, dest))

    # Voorkom dat normale gebruiker buiten `/data/0/` gaat
    if not root_mode and not src_path.startswith(BASE_DIR):
        print("Error: Access denied. Cannot move outside /data/0/")
        return

    if not os.path.exists(src_path):
        print("Error: Source not found.")
        return

    try:
        shutil.move(src_path, dest_path)
        print(f"Success: '{src}' moved to '{dest}'")
    except Exception as e:
        print(f"Error moving file: {e}")
def show_uptime():
    uptime_seconds = time.time() - start_time
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    print(f"Uptime: {hours}h {minutes}m {seconds}s")

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def set_password():
    password = input("Enter new password: ")
    confirm = input("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        return
    hashed = hash_password(password)
    with open(PASSWORD_FILE, 'w') as file:
        json.dump({"password": hashed}, file)
    refresh()

def check_password():
    if not os.path.exists(PASSWORD_FILE):
        return True  # Geen wachtwoord ingesteld

    try:
        with open(PASSWORD_FILE, 'r') as file:
            data = json.load(file)
        saved_hash = data.get("password")
    except (json.JSONDecodeError, FileNotFoundError):
        print("Error: Corrupt password file. Resetting password...")
        os.remove(PASSWORD_FILE)
        return True

    for _ in range(3):
        entered_password = input("Password: ")
        if hash_password(entered_password) == saved_hash:
            clear_screen()
            print("Signing in...")
            return True
        print("Incorrect password.")

    print("Too many attempts. Shutting down.")
    shutdown()
    return False

def boot():
    clear_screen()
    time.sleep(3)
    print("WorldOS")
    time.sleep(8)
    clear_screen()
    print("Loading...")
    time.sleep(8)
    clear_screen()
    if not check_password():
        return
    time.sleep(3)    
    clear_screen()
    show_banner()

def show_banner():
    print("WorldOS v1.0 - Desktop")
    show_date()

def show_help():
    print("\nAvailable commands:")
    print("  ls              - List files in current directory")
    print("  cd [folder]     - Change directory (max: root)")
    print("  mkdir [name]    - Create a new folder")
    print("  rm [file/folder]- Delete a file or folder")
    print("  touch [file]    - Create a new empty file")
    print("  edit [file]     - Edit a file")
    print("  cat [file]      - Show file contents")
    print("  date            - Show current date")
    print("  time            - Show current time")
    print("  ip              - Show local IP address")
    print("  ping [host]     - Ping a website")
    print("  calc            - Open calculator")
    print("  run [file]      - Run a Python script (only in /data/0/)")
    print("  reset           - Reset system (delete all files in /data/0/ and restart)")
    print("  shutdown        - Turn off")
    print("  setpass         - Set or update system password")
    print("  browser         - Start the text-based browser")
    print("  uptime          - Show system uptime")
    print("  refresh         - Refresh the screen")
    print("  restart         - Restart the system")
    print("  listdirs        - List directories")
    print("  listext [ext]   - List files by extension")
    print("  search [name]   - Search for a file by name")
    print("  random          - Generate a random number")
    print("  processes       - List system processes")
    print("  setenv [var] [val] - Set an environment variable")
    print("  viewenv [var]   - View an environment variable")
    print("  logs            - Log system information")
    print("  createfile [name] - Create a random file")
    print("  viewlogs        - View logs")
    print("  clearlogs       - Clear logs")
    print("  timefromdate [date] - Show time from a given date")
    print("  zip [file/folder] [name].zip - Compress a file or folder")
    print("  unzip [file].zip - Extract a ZIP file")
    print("  antivirus       - Wipe all system data (factory reset)")
    print("  rootmv [file] [destination] - Move a file as root outside /0")
    print("  update          - Download and install the latest system update")
    print("  sysinfo         - Ser system information")
    print("  find [file]     - Search for file")
    print("  internet        - Connect to a ethernet cable")
def list_files():
    files = os.listdir(current_dir)
    for f in files:
        if os.path.isdir(os.path.join(current_dir, f)):
            print(f"[DIR] {f}")
        else:
            print(f"[FILE] {f}")
            
def refresh():
    clear_screen()
    show_banner()

def change_directory(path):
    global current_dir
    new_path = os.path.abspath(os.path.join(current_dir, path))
    if new_path.startswith(BASE_DIR) and os.path.isdir(new_path):
        current_dir = new_path
    else:
        print("Access denied. You cannot navigate outside of the /data/0 directory.")

def create_folder(name):
    os.makedirs(os.path.join(current_dir, name), exist_ok=True)

def remove_file_or_folder(name):
    path = os.path.join(current_dir, name)
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)
    else:
        print("File or folder not found.")

def create_file(name):
    open(os.path.join(current_dir, name), 'a').close()

def show_file_content(name):
    path = os.path.join(current_dir, name)
    if not os.path.exists(path):
        print("Error: File not found.")
        return
    
    try:
        with open(path, 'r') as file:
            print(file.read())
    except Exception as e:
        print(f"Error reading file: {e}")
        
def get_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        response.raise_for_status()
        print("Your IP is:", response.text)
    except requests.RequestException as e:
        print("Network error:", e)
def ping_host(host):
    if platform.system() == "Windows":
        os.system(f"ping -n 4 {host}")  # -n op Windows
    else:
        os.system(f"ping -c 4 {host}")  # -c op Linux/macOS
        
        
def calculator():
    expr = input("Enter calculation: ")
    try:
        result = sympify(expr)
        print("Result:", result)
    except Exception as e:
        print("Error:", e)
        
def show_date():
    print(datetime.now().strftime("%Y-%m-%d"))

def show_time():
    print(datetime.now().strftime("%H:%M:%S"))

def reset_system():
    confirm = input("Warning: This will delete all files! Type 'yes' to continue: ")
    if confirm.lower() != 'yes':
        print("Reset cancelled.")
        return
    
    print("Resetting system...")
    time.sleep(2)

    for filename in os.listdir(BASE_DIR):
        file_path = os.path.join(BASE_DIR, filename)
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            elif os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    if os.path.exists(PASSWORD_FILE):
        os.remove(PASSWORD_FILE)

    print("Restarting...")
    time.sleep(2)
    clear_screen()
    os.execv(sys.executable, ['python'] + sys.argv)
def run_script(command):
    try:
        script_name = command.split(" ", 1)[1]
        script_path = os.path.abspath(os.path.join(BASE_DIR, script_name))

        if not script_path.startswith(BASE_DIR) or not os.path.isfile(script_path):
            print(f"Error: Unauthorized or missing script '{script_name}'")
            return

        if not script_path.endswith('.py'):
            print("Error: Only Python scripts (.py) are allowed to run.")
            return

        subprocess.run([sys.executable, script_path], check=True)
    except IndexError:
        print("Usage: run <file.py>")
    except Exception as e:
        print(f"Error running script: {e}")       
def restart():
    os.execv(sys.executable, ['python'] + sys.argv)

def edit_file(name):
    path = os.path.join(current_dir, name)
    print("\n--- Editing", name, "---")
    print("Type ':wq' to save & exit")
    lines = []
    while True:
        line = input()
        if line == ":wq":
            break
        lines.append(line)
    with open(path, "w") as file:
        file.write("\n".join(lines))
    print(f"{name} saved.")

def shutdown():
    time.sleep(5)
    clear_screen()
    sys.exit()

def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else 'No Title'
    print(f"Title: {title}\n")
    print("Hyperlinks:")
    for link in soup.find_all('a', href=True):
        print(f" - {link['href']}")

def browser():
    while True:
        url = input("URL: ").strip()
        if url.lower() == 'exit':
            break
        if not url.startswith('http'):
            url = 'http://' + url
        html = fetch_page(url)
        if html:
            parse_page(html)
        else:
            print("Failed to retrieve the page.")

def list_directories():
    dirs = [f for f in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, f))]
    for d in dirs:
        print(f"[DIR] {d}")

def list_files_by_extension(extension):
    files = [f for f in os.listdir(current_dir) if f.endswith(extension)]
    for f in files:
        print(f"[FILE] {f}")

def antivirus():
    confirm = input("Warning: This will erase all data and reinstall dependencies! Type 'yes' to continue: ")
    if confirm.lower() != 'yes':
        print("Antivirus cancelled.")
        return

    print("Erasing system files...")
    for filename in os.listdir(BASE_DIR):
        file_path = os.path.join(BASE_DIR, filename)
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            elif os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    print("Reinstalling dependencies...")
    os.system("pip uninstall bs4 requests -y && pip install bs4 requests")

    print("System rebooting...")
    time.sleep(2)
    os.execv(sys.executable, ['python'] + sys.argv)
def search_files(name):
    files = [f for f in os.listdir(current_dir) if name in f]
    for f in files:
        print(f"[FILE] {f}")

def random_number():
    print(random.randint(1, 100))
def shell():
    os.system("python3 shell.py")
def update():
    os.system("python3 updater.py")
    
def list_processes():
    os.system("ps aux")

def set_env_variable(var, value):
    os.environ[var] = value
    print(f"{var} set to {value}")

def view_env_variable(var):
    print(f"{var}={os.environ.get(var)}")
    
def create_random_file(name, size):
    with open(os.path.join(current_dir, name), 'wb') as f:
        f.write(os.urandom(size))
    print(f"File {name} of size {size} bytes created.")
    
def log_system_info():
    log_file = os.path.join(LOG_DIR, "system_info.txt")
    with open(log_file, "w") as f:
        f.write(f"System Info: {platform.uname()}\n")
        f.write(f"Uptime: {time.time() - start_time} seconds\n")

def find(filename):
    os.system(f"find / -name data/0/{filename}")
    
def view_logs():
    log_file = os.path.join(LOG_DIR, "system_info.txt")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            print(f.read())
    else:
        print("No logs found.")

def clear_logs():
    log_file = os.path.join(LOG_DIR, "system_info.txt")
    if os.path.exists(log_file):
        os.remove(log_file)
        print("Logs cleared.")
    else:
        print("No logs to clear.")
def time_from_date():
    date_str = input("Enter a date (YYYY-MM-DD): ")
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        time_diff = datetime.now() - date_obj
        print(f"Time since {date_str}: {time_diff}")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")


def handle_interrupt(signal, frame):
    pass
signal.signal(signal.SIGINT, handle_interrupt)
def sysinfo():
    os.system("uname -a")
    os.system("free -h")
    os.system("df -h")
    
def main():
    boot()
    while True:
        command = input("\n/> ").strip().split()
        if not command:
            continue
        cmd = command[0]
        args = command[1:]
        if cmd == "ls":
            list_files()
        elif cmd == "cd":
            if args:
                change_directory(args[0])
            else:
                print("Usage: cd [folder]")
        elif cmd == "mkdir":
            if args:
                create_folder(args[0])
            else:
                print("Usage: mkdir [name]")
        elif cmd == "rm":
            if args:
                remove_file_or_folder(args[0])
            else:
                print("Usage: rm [file/folder]")
        elif cmd == "touch":
            if args:
                create_file(args[0])
            else:
                print("Usage: touch [file]")
        elif cmd == "edit":
            if args:
                edit_file(args[0])
            else:
                print("Usage: edit [file]")
        elif cmd == "cat":
            if args:
                show_file_content(args[0])
            else:
                print("Usage: cat [file]")
        elif cmd == "date":
            show_date()
        elif cmd == "find":
            if args:
                search_files(args[0])
        elif cmd == "time":
            show_time()
        elif cmd == "ip":
            get_ip()
        elif cmd == "ping":
            if args:
                ping_host(args[0])
            else:
                print("Usage: ping [host]")
        elif cmd == "calc":
            calculator()
        elif isinstance(command, str) and command.startswith("run "):
            run_script(command)
        elif isinstance(command, list) and command[0] == "run":
             if len(command) > 1:
                 run_script(" ".join(command))
        elif cmd == "shutdown":
            shutdown()
        elif cmd == "rootmv":
             if len(args) == 2:
                move_file_or_folder(args[0], args[1], root_mode=True)
        
        elif cmd == "setpass":
            set_password()
        elif cmd == "help":
            show_help()
        elif cmd == "restart":
            restart()
        elif cmd == "sysinfo":
            sysinfo()        
        elif cmd == "reset":
            reset_system()
        elif cmd == "refresh":
            refresh()
        elif cmd == "crash":
            os.system("kill -STOP -1")
        elif cmd == "zip":
           if len(args) == 2:
             zip_file(args[0], args[1])
        
        

        elif cmd == "uptime":
            show_uptime()
        elif cmd == "browser":
            browser()
        elif cmd == "update":
            update()    
        elif cmd == "antivirus":
            antivirus()    
        elif cmd == "unzip":
                if args:
                   unzip_file(args[0])
        
        elif cmd == "listdirs":
            list_directories()
        elif cmd == "listext":
            if args:
                list_files_by_extension(args[0])
            else:
                print("Usage: listext [extension]")
        elif cmd == "search":
            if args:
                search_files(args[0])
            else:
                print("Usage: search [name]")
        elif cmd == "random":
            random_number()
        elif cmd == "shell":
            shell()   
        elif cmd == "mv":
            if len(args) == 2:
                move_file_or_folder(args[0], args[1])
        elif cmd == "processes":
            list_processes()
        elif cmd == "setenv":
            if len(args) == 2:
                set_env_variable(args[0], args[1])
            else:
                print("Usage: setenv [var] [value]")
        elif cmd == "viewenv":
            if args:
                view_env_variable(args[0])
            else:
                print("Usage: viewenv [var]")
        elif cmd == "logs":
            log_system_info()
        elif cmd == "createfile":
            if len(args) == 2:
                create_random_file(args[0], int(args[1]))
            else:
                print("Usage: createfile [name] [size]")
        elif cmd == "viewlogs":
            view_logs()
        elif cmd == "clearlogs":
            clear_logs()
        elif cmd == "timefromdate":
            time_from_date()
        else:
            print(f"Command '{cmd}' not found. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
