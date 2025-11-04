
import os
import sys

#------------------- CONFIG HERE ------------------------
#--------------------------------------------------------

PYPATH = "D:\\Softs\\Python\\Python311\\python.exe"

#--------------------------------------------------------
#--------------------------------------------------------

def main():
    
    #define common paths..
    assert os.path.exists(PYPATH), f"[ERROR]: python.exe path does not exists '{PYPATH}'"
    BUILDFILE = os.path.abspath(__file__) #../PyWiz/source/build.py (this file)
    MAINDIR = os.path.dirname(BUILDFILE) #../PyWiz/source/
    MAINFILE = os.path.join(MAINDIR,'main.py'), "[ERROR]: 'main.py' file not found? '../PyWiz/source/main.py'"
    ASSETSDIR = os.path.join(MAINDIR,'assets') #../PyWiz/source/assets/
    assert os.path.exists(ASSETSDIR), "[ERROR]: 'assets' directory not found? '../PyWiz/source/assets/'"
    PROJECTDIR = os.path.dirname(MAINDIR) #../PyWiz/
    INSTALLER = os.path.join(PROJECTDIR,'installer.exe')

    #remove if already exists
    if os.path.exists(INSTALLER):
        print('[INFO]: installer.exe already exists.. Removing')
        os.remove(INSTALLER)

    #tell python to build using the 
    # NOTE: add --add-data entries if you bundle assets, e.g.:
    # "--add-data", "assets;assets",
    args = [
        "--onefile",
        "--name", "installer",
        "--noconfirm",
        "--distpath", ???,
        "--workpath", ???,
        "--specpath", ???,
        # "--icon", "assets/app.ico",  # optional
        "main.py",
        ]

    # Prefer running via current interpreter to avoid PATH issues
    cmd = [sys.executable, "-m", "PyInstaller"] + args
    print("[INFO] Running:", " ".join(cmd))
    code = os.spawnv(os.P_WAIT, sys.executable, cmd)

    # build failed?
    if (code!=0):
        print(f"[ERROR] PyInstaller failed with exit code {code}")
        sys.exit(code)

    # Sanity check
    if (not os.path.exists(INSTALLER)):
        print("[ERROR] ERROR: build finished but installer.exe not found.")
        sys.exit(1)

    return None


if (__name__ == "__main__"):
    main()