
![PyWiz](templates/pywiz.png)

A simple Python installer template for creating beautiful desktop application installers with wizard-style UI's.

---

## **Features**

*   **Multi-Page Wizard** - Step-by-step installation process
*   **Form Controls** - Basic UI with tkinter
*   **Easy Template** - Add custom icons, splash and headers from your branding
*   **Easy Configuration** - Simple class-based page system, just define & add pages in main.py following the examples
*   **Build Scripts** - Build the executable with the `build_nuikta.py` or `build_pyinstaller.py`. (NOTE: only tested on WinOS so far)
*   **One-File** - Will produce a single executable with compressed archives
*   **Cross-Platform** - Nuitka and PyInstaller supports creating apps for Windows, macOS, Linux support. (NOTE: You'll need to propose one app per OS. Only tested on WindowsOS so far)

---

## **Quick Start**

### 1\. Install Dependencies


for main.py
```
pip install sv_ttk
pip install pillow
```

for build_xx.py depending on your compiler choice
```
pip install pyinstaller
pip install nuitka
```

### 2\. Create Your Installer

```python

class MyInstallPage(PageBase):
    title_text = "Welcome"
    footer_text = "Page 1"

    def __init__(self, parent, refresh_ui):
        super().__init__(parent, refresh_ui)
        # Add your UI components here see existing examples in main.py

#NOTE: instead of building the .exe to test the app, you can run the script to test out the tkinter UI directly
if __name__ == "__main__":
    app = Wizard()
    app.mainloop()

#NOTE: store anything in the `/assets` folder, it will be packed in the .exe and unpacked in a temp directory during launch,  in main, use get_assets_dir() to find back the files you need at runtime.
```

### 3\. Build Executable

Build your own app.ico, header\_pageX.jpg, splash.jpg using the photoshop templates.  
Please keep the PyWiz logo on the splash lower corner.

### 4\. Build Executable

```
# Using PyInstaller (recommended for distribution)
python build_pyinstaller.py

# Using Nuitka (faster but heavily AV-flagged..)
python build_nuitka.py
```

---

## **License**

.py files:

*   **MIT License** - feel free to use in your projects!

images and logos:

*   **RoyaltyFree**, please replace the logos and images with your images. Except for pywiz.png, please include it in the splash.
