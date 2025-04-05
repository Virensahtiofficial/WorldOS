import os
import subprocess

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
        
def run_shell():
    while True:
        try:
            command = input("~ $ ") 

            if command.lower() in ["exit"]:
                break
            elif command.strip() == "":
                continue
            elif command.strip() == "bash":
                continue
            
            if command.startswith("cd "):
                try:
                    path = command[3:].strip()
                    os.chdir(path)
                except FileNotFoundError:
                    print(f"Cannot access '{path}': No such file or directory")
                except PermissionError:
                    print(f"Cannot open directory '{path}': Permission denied")
                continue
            else:
                process = subprocess.run(command, shell=True, text=True)

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
        except Exception as e:
            print(f"{e}")

if __name__ == "__main__":
    clear()
    run_shell()