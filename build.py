import os
os.system("pip install requests -q")
import time
import requests
# Instellingen
url1 = "https://raw.githubusercontent.com/Virensahtiofficial/WorldOS/refs/heads/main/os.py"
url2 = "https://raw.githubusercontent.com/Virensahtiofficial/WorldOS/refs/heads/main/updater.py"
url3 = "https://raw.githubusercontent.com/Virensahtiofficial/WorldOS/refs/heads/main/shell.py"

pip_packages = ["requests", "tqdm", "beautifulsoup4", "sympy"]

doelmap = "worldos"
pip_download_dir = os.path.join(doelmap, "data", "0", "pip_packages")  # Pip-bestanden opslaan in flame/data/0

bestanden = {
    "os.py": url1,
    "updater.py": url2,
    "shell.py": url3   
}

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")  # Windows → cls, Andere OS'en → clear

clear_console()
print("Building WorldOS...")
time.sleep(5)

# Maak doelmappen aan als die niet bestaan
for pad in [doelmap, pip_download_dir]:
    if not os.path.exists(pad):
        os.makedirs(pad)

# Stap 1: Download pip-pakketten als bestanden in flame/data/0
for package in pip_packages:
    os.system(f"pip download {package} -d {pip_download_dir} -q")

# Stap 2: Installeer de gedownloade pakketten lokaal
os.system(f"pip install --no-index --find-links={pip_download_dir} {' '.join(pip_packages)} -q")

# Stap 3: Download FlameOS-bestanden
for bestand_naam, url in bestanden.items():
    bestand_pad = os.path.join(doelmap, bestand_naam)
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(bestand_pad, "wb") as bestand:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    bestand.write(chunk)

    except requests.RequestException as e:
        clear_console()
        print(f"Build failed")
        time.sleep(2)
        exit()

# Update voltooid
clear_console()
print("Starting...")
time.sleep(12)

# Start OS opnieuw
os.system(f"python3 {os.path.join(doelmap, 'os.py')}")
