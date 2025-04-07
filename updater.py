import os
os.system("pip install requests -q")
import time
import requests

# Instellingen
url = "https://raw.githubusercontent.com/Virensahtiofficial/WorldOS/refs/heads/main/os.py"
doelmap = "worldos"
bestand_naam = "os.py"
bestand_pad = os.path.join(doelmap, bestand_naam)

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")  # Windows → cls, Andere OS'en → clear

clear_console()
print("Updating system...")
time.sleep(3)

# Vereiste libraries reinstalleren
os.system("pip uninstall requests tqdm bs4 sympy -q -y")
os.system("pip install requests tqdm bs4 sympy -q")

# Controleer of de map bestaat, anders aanmaken
if not os.path.exists(doelmap):
    os.makedirs(doelmap)

# Download nieuwste OS-versie
try:
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(bestand_pad, "wb") as bestand:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                bestand.write(chunk)

except requests.RequestException as e:
    clear_console()
    print(f"Update failed")
    time.sleep(2)
    os.system(f"python3 {bestand_pad}")

# Update voltooid
clear_console()
print("Restarting...")
time.sleep(8)

# Start OS opnieuw
os.system(f"python3 {bestand_pad}")
