import os
import sys
import tempfile
import shutil
import subprocess

#NOTE: 'pip install nuitka' required.
#NOTE: your antivirus might interact with the build process of the executable.
#NOTE: CONS: Antivirus don't like nuitka.. A lot of viruses are made using nuitka..
#      PRO: Faster startup time.

#----------------- **CONFIG HERE** ----------------------
#--------------------------------------------------------

PYPATH = "D:\\Softs\\Python\\Python311\\python.exe"
HIDECONSOLE = True #hide the console (for final build)
INSTALLER_NAME = 'GeoScatter5.6.1_installer' #name of the installer, no '.' or os illegal characters

#----------------------- DIR UTILS ----------------------
#--------------------------------------------------------

#define common paths..
assert os.path.exists(PYPATH), f"[ERROR]: python.exe path does not exists '{PYPATH}'"
BUILDFILE = os.path.abspath(__file__) #../ParentFolder/pywiz/build_nuitka.py (this file)
MAINDIR = os.path.dirname(BUILDFILE) #../ParentFolder/pywiz/
MAINFILE = os.path.join(MAINDIR,'main.py')
assert os.path.exists(MAINFILE), "[ERROR]: 'main.py' file not found? '../ParentFolder/pywiz/main.py'"
PROJECTDIR = os.path.dirname(MAINDIR) #../ParentFolder/

#define assets
ASSETSDIR = os.path.join(MAINDIR,'assets') #../ParentFolder/pywiz/assets/
assert os.path.exists(ASSETSDIR), "[ERROR]: 'assets' directory not found? '../ParentFolder/pywiz/assets/'"
ICOPATH = os.path.join(ASSETSDIR,'app.ico')

#define result directory
RESULTDIR = os.path.join(PROJECTDIR,'dist_nuitka')  # D:\Work\ParentFolder\dist_nuitka\
INSTALLER = os.path.join(PROJECTDIR,f'{INSTALLER_NAME}.exe')  # Final executable in project root

#define fallback log file
TMPDIR = tempfile.gettempdir()
LOGFILE = os.path.join(TMPDIR, 'pywiz_errors.txt')

#--------------------- COMPILE --------------------------
#--------------------------------------------------------

def build_program():
    """build the program using Nuitka"""
    print("[---------------------- START -----------------------------]")

    # Clean up any existing files/directories first
    if os.path.exists(INSTALLER):
        print(f'[INFO]: `{INSTALLER_NAME}.exe` already exists.. Removing')
        os.remove(INSTALLER)

    if os.path.exists(RESULTDIR):
        print(f'[INFO]: Leftover `{RESULTDIR}` directory exists.. Removing')
        shutil.rmtree(RESULTDIR)

    # Create output directory
    os.makedirs(RESULTDIR, exist_ok=True)

    #tell python to build using Nuitka
    args = [
        "--onefile",  # Single executable file (required for installer)
        f"--output-dir={RESULTDIR}",
        "--enable-plugin=tk-inter",  # Enable tkinter support
        "--enable-plugin=no-qt",     # Disable Qt plugins (we don't use Qt)
        
    ]

    # Add assets directory
    args.extend([f"--include-data-dir={ASSETSDIR}=assets"])

    # Add icon if it exists
    if (os.path.exists(ICOPATH)):
        print('[INFO]: Adding icon to the installer')
        args.extend([f"--windows-icon-from-ico={ICOPATH}"])

    # Console mode
    if (HIDECONSOLE==True):
        print('[INFO]: Hiding the console')
        args.append("--windows-console-mode=disable")
    else:
        print('[INFO]: Console will be visible (development mode)')
        args.append("--windows-console-mode=attach")

    # Add version info (optional - may not be supported in all Nuitka versions)
    # args.extend([
    #     "--windows-product-name=Geo-Scatter Installer",
    #     "--windows-file-version=5.6.1.0",
    #     "--windows-product-version=5.6.1.0",
    # ])

    args.append("main.py")

    # Set environment variables to make Nuitka non-interactive
    env = os.environ.copy()
    env['NUITKA_ASSUME_YES'] = '1'
    env['NUITKA_ASSUME_YES_FOR_DOWNLOADS'] = '1'

    # Prefer running via current interpreter to avoid PATH issues
    cmd = [sys.executable, "-m", "nuitka"] + args
    print("[INFO]: Running Nuitka:", " ".join(cmd))

    # Run with environment variables and automatic "yes" responses
    result = subprocess.run(cmd, env=env, input="yes\nyes\nyes\n", text=True)
    code = result.returncode

    # build failed?
    if (code!=0):
        print(f"[ERROR] Nuitka failed with exit code {code}")
        sys.exit(code)

    # Nuitka creates main.exe, but we want the proper name
    nuitka_output = os.path.join(RESULTDIR, "main.exe")

    # Sanity check
    if (not os.path.exists(nuitka_output)):
        print(f"[ERROR] ERROR: build finished but 'main.exe' not found in {RESULTDIR}/")
        sys.exit(1)

    # Move and rename the executable
    print(f"[INFO] Moving executable from '{nuitka_output}' to '{INSTALLER}'")
    shutil.move(nuitka_output, INSTALLER)

    # Remove the entire dist_nuitka directory
    print(f"[INFO] Cleaning up build directory: {RESULTDIR}")
    shutil.rmtree(RESULTDIR)

    print("[---------------------- END -------------------------------]")
    print(f"[SUCCESS] Executable created: {INSTALLER}")
    print("[INFO] Double-click the .exe file to run your installer!")
    print("[INFO] Nuitka builds are typically 1-2 seconds startup vs PyInstaller's 10+ seconds!")
    print("[IMPORTANT] You might want to create an antivirus exception for the direcory of this project. Nuitka is often flagged as virus as it's often used to make them.")

    return None


if (__name__ == "__main__"):
    build_program()
