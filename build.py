
import os
import sys
import tempfile
import shutil

#----------------- **CONFIG HERE** ----------------------
#--------------------------------------------------------

PYPATH = "D:\\Softs\\Python\\Python311\\python.exe"
HIDECONSOLE = False #hide the console (for final build)
INSTALLER_NAME = 'GeoScatter5.6.1_installer' #name of the installer, no '.' or os illegal characters

#----------------------- DIR UTILS ----------------------
#--------------------------------------------------------

#define common paths..
assert os.path.exists(PYPATH), f"[ERROR]: python.exe path does not exists '{PYPATH}'"
BUILDFILE = os.path.abspath(__file__) #../PyWiz/source/build.py (this file)
MAINDIR = os.path.dirname(BUILDFILE) #../PyWiz/source/
MAINFILE = os.path.join(MAINDIR,'main.py')
assert os.path.exists(MAINFILE), "[ERROR]: 'main.py' file not found? '../PyWiz/source/main.py'"
PROJECTDIR = os.path.dirname(MAINDIR) #../PyWiz/

#define assets
ASSETSDIR = os.path.join(MAINDIR,'assets') #../PyWiz/source/assets/
assert os.path.exists(ASSETSDIR), "[ERROR]: 'assets' directory not found? '../PyWiz/source/assets/'"
ICOPATH = os.path.join(ASSETSDIR,'app.ico')

#define result directory
RESULTDIR = PROJECTDIR  # D:\Work\PyWiz\
BUILDWORKDIR = os.path.join(PROJECTDIR,'buildfiles') #../PyWiz/build/
BUILDSPECDIR = os.path.join(PROJECTDIR,'buildfiles') #../PyWiz/build/
INSTALLER = os.path.join(RESULTDIR,f'{INSTALLER_NAME}.exe')

#define fallback log file
TMPDIR = tempfile.gettempdir()
LOGFILE = os.path.join(TMPDIR, 'pywiz_errors.txt')

#--------------------- COMPILE --------------------------
#--------------------------------------------------------

def build_program():
    """build the program using PyInstaller"""
    print("[---------------------- START -----------------------------]")

    #remove if already exists
    if os.path.exists(INSTALLER):
        print(f'[INFO]: `{INSTALLER_NAME}.exe` already exists.. Removing')
        os.remove(INSTALLER)

    #tell python to build using the
    # Bundle assets directory
    args = [
        "--onefile",
        "--name", INSTALLER_NAME,
        "--noconfirm",
        "--distpath", RESULTDIR,
        "--workpath", BUILDWORKDIR,
        "--specpath", BUILDSPECDIR,
        "--add-data", f"{ASSETSDIR};assets",
        ]

    if (os.path.exists(ICOPATH)):
        print('[INFO]: args: --icon: adding icon to the installer')
        args.append("--icon")
        args.append(ICOPATH)

    if (HIDECONSOLE==True):
        print('[INFO]: args: --noconsole: hiding the console')
        args.append("--noconsole")

    args.append("main.py")

    # Prefer running via current interpreter to avoid PATH issues
    cmd = [sys.executable, "-m", "PyInstaller"] + args
    print("[INFO]: Running PyInstaller:", " ".join(cmd))
    code = os.spawnv(os.P_WAIT, sys.executable, cmd)

    # build failed?
    if (code!=0):
        print(f"[ERROR] PyInstaller failed with exit code {code}")
        sys.exit(code)

    # Sanity check
    if (not os.path.exists(INSTALLER)):
        print(f"[ERROR] ERROR: build finished but '{INSTALLER_NAME}.exe' not found.")
        sys.exit(1)
    
    # Remove tmp build directory to ensure it's not infecting next build
    if os.path.exists(BUILDWORKDIR):
        print(f'[INFO]: buildfiles directory `{BUILDWORKDIR}` already exists.. Removing')
        shutil.rmtree(BUILDWORKDIR)
    if os.path.exists(BUILDSPECDIR):
        print(f'[INFO]: buildfiles directory `{BUILDSPECDIR}` already exists.. Removing')
        shutil.rmtree(BUILDSPECDIR)

    print("[---------------------- END -------------------------------]")
    return None


if (__name__ == "__main__"):
    build_program()