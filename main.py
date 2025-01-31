import os
import glob

try:
    MY_SECRET_TOKEN = os.environ["MY_SECRET_TOKEN"]
except KeyError:
    MY_SECRET_TOKEN = "Token not available!"

SPECIFIC_SCRIPT = "links_cdiscount.py"  # Change ce nom selon ton besoin

def run_scripts():
    if os.path.exists(SPECIFIC_SCRIPT):
        print(f"Exécution de {SPECIFIC_SCRIPT} en premier...")
        os.system(f"python {SPECIFIC_SCRIPT}")

    script_files = glob.glob("*.py")  
    script_files.remove("main.py")  
    script_files.remove(SPECIFIC_SCRIPT)  # On évite de réexécuter le script spécifique

    for script in script_files:
        print(f"Exécution de {script}...")
        os.system(f"python {script}")

if __name__ == "__main__":
    run_scripts()
