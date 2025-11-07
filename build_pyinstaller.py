
import os
import sys
import tempfile
import shutil

#NOTE: 'pip install pyinstaller' required.
#NOTE: CONS: PyInstaller is slower than nuitka on paper.

#----------------- **CONFIG HERE** ----------------------
#--------------------------------------------------------

PYPATH = "D:\\Softs\\Python\\Python311\\python.exe"
HIDECONSOLE = True #hide the console (for final build)
INSTALLER_NAME = 'GeoScatter5.6.1_installer' #name of the installer, no '.' or os illegal characters

#----------------------- DIR UTILS ----------------------
#--------------------------------------------------------

#define common paths..
assert os.path.exists(PYPATH), f"[ERROR]: python.exe path does not exists '{PYPATH}'"
BUILDFILE = os.path.abspath(__file__) #../ParentFolder/pywiz/build.py (this file)
MAINDIR = os.path.dirname(BUILDFILE) #../ParentFolder/pywiz/
MAINFILE = os.path.join(MAINDIR,'main.py')
assert os.path.exists(MAINFILE), "[ERROR]: 'main.py' file not found? '../ParentFolder/pywiz/main.py'"
PROJECTDIR = os.path.dirname(MAINDIR) #../ParentFolder/

#define assets
ASSETSDIR = os.path.join(MAINDIR,'assets') #../ParentFolder/pywiz/assets/
assert os.path.exists(ASSETSDIR), "[ERROR]: 'assets' directory not found? '../ParentFolder/pywiz/assets/'"
ICOPATH = os.path.join(ASSETSDIR,'app.ico')

#define result directory
RESULTDIR = PROJECTDIR  # D:\Work\ParentFolder\
BUILDWORKDIR = os.path.join(PROJECTDIR,'buildfiles') #../ParentFolder/build/
BUILDSPECDIR = os.path.join(PROJECTDIR,'buildfiles') #../ParentFolder/build/
INSTALLER = os.path.join(RESULTDIR,f'{INSTALLER_NAME}.exe')  # Single file for --onefile

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
    # Optimized for faster startup with --onefile and splash screen
    args = [
        "--onefile",  # Single executable file
        "--name", INSTALLER_NAME,
        "--noconfirm",
        "--distpath", RESULTDIR,
        "--workpath", BUILDWORKDIR,
        "--specpath", BUILDSPECDIR,
        "--add-data", f"{ASSETSDIR};assets",
        "--optimize", "1",  # Basic Python optimization
        "--noupx",  # Skip UPX compression for faster startup
        ]

    # Add splash screen (requires tkinter and PIL)
    splash_image = os.path.join(ASSETSDIR, "splash.jpg")  # Create this image for splash screen
    if os.path.exists(splash_image):
        print(f'[INFO]: Adding splash screen: {splash_image}')
        args.extend(["--splash", splash_image])
    else:
        print(f'[WARNING]: Splash image not found: {splash_image}')
        print('[INFO]: Create assets/splash.jpg (400x200 recommended) for better UX')

    # Hidden imports for sv-ttk theme
    args.extend(["--hidden-import", "sv_ttk"])

    # Aggressive module exclusions to reduce startup time
    args.extend([
        # PIL/Pillow modules (keep JPEG and PNG support, exclude others)
        "--exclude-module", "PIL.BmpImagePlugin",
        "--exclude-module", "PIL.GifImagePlugin",
        "--exclude-module", "PIL.PpmImagePlugin",
        "--exclude-module", "PIL.TiffImagePlugin",
        "--exclude-module", "PIL.XbmImagePlugin",
        "--exclude-module", "PIL.XpmImagePlugin",
        "--exclude-module", "PIL.WmfImagePlugin",
        "--exclude-module", "PIL.WebPImagePlugin",
        "--exclude-module", "PIL.SpiderImagePlugin",
        # NumPy - exclude if not using advanced image processing
        "--exclude-module", "numpy",
        "--exclude-module", "numpy.libs",
        # Tkinter and test modules
        "--exclude-module", "tkinter.test",
        "--exclude-module", "tkinter.tix",  # Old tkinter extension
        # Keep tkinter.ttk - it's needed for ttk widgets
        "--exclude-module", "test",
        "--exclude-module", "unittest",
        "--exclude-module", "doctest",
        # Safe to exclude:
        "--exclude-module", "pdb",
        "--exclude-module", "pydoc",
        "--exclude-module", "distutils",
        # Essential modules - DO NOT exclude these:
        # urllib, ssl, multiprocessing, xml - needed by PyInstaller
    ])

    if (os.path.exists(ICOPATH)):
        print('[INFO]: args: --icon: adding icon to the installer')
        args.append("--icon")
        args.append(ICOPATH)

    if (HIDECONSOLE==True):
        print('[INFO]: args: --noconsole: hiding the console')
        args.append("--noconsole")
    else:
        print('[INFO]: args: console will be visible (development mode)')

    args.append("main.py")

    # Prefer running via current interpreter to avoid PATH issues
    cmd = [sys.executable, "-m", "PyInstaller"] + args
    print("[INFO]: Running PyInstaller:", " ".join(cmd))

    # Run PyInstaller (don't capture output so user can see progress)
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

    # Analyze the final executable size
    if os.path.exists(INSTALLER):
        size_mb = os.path.getsize(INSTALLER) / (1024 * 1024)
        print(f"[INFO] Final executable size: {size_mb:.1f} MB")
        # Warn if unusually large
        if size_mb > 20: print("[WARNING] Executable is quite large - consider more exclusions")
        elif size_mb > 50: print("[ERROR] Executable is very large - major optimization needed")

    print("[---------------------- END -------------------------------]")
    print(f"[SUCCESS] Executable created: {INSTALLER}")
    print("[INFO] Double-click the .exe file to run your installer!")
    return None


if (__name__ == "__main__"):
    build_program()