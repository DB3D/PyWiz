
![PyWiz](templates/pywiz.png)

A simple Python installer template for creating beautiful desktop application installers with wizard-style UI's.

---

## **Features**

*   **Multi-Page Wizard** - Step-by-step installation process
*   **Form Controls** - Basic UI with tkinter
*   **Easy Template** - Add custom icons, splash and headers from your branding
*   **Easy Configuration** - Simple class-based page system, just define your page in main.py
*   **Build Scripts** - Ready-to-use PyInstaller and Nuitka builds
*   **Error Handling** - Comprehensive error dialogs and logging
*   **One-Click Builds** - Automated standalone executable creation
*   **Cross-Platform** - Windows, macOS, Linux support. (NOTE: tested only on WinOS so far)

---

## **Quick Start**

### 1\. Install Dependencies

```
pip install tkinter sv_ttk pillow pyinstaller
```

### 2\. Create Your Installer

```python

class MyInstallPage(PageBase):
    title_text = "Welcome"
    footer_text = "Page 1"

    def __init__(self, parent, refresh_ui):
        super().__init__(parent, refresh_ui)
        # Add your UI components here see examples of existing pages

# Run the tk ui directly
if __name__ == "__main__":
    app = Wizard()
    app.mainloop()

#NOTE: store anything in the /assets folder, it will be packed in the .exe and unpacked in a temp directory, then use get_assets_dir() to find back the files you need.
```

### 3\. Build Executable

Build your own app.ico, header\_pageX.jpg, splash.jpg using the photoshop templates.  
Please keep the PyWiz logo on the splash lower corner.

### 4\. Build Executable

```
# Using PyInstaller (recommended for distribution)
python build_pyinstaller.py

# Using Nuitka (faster but AV-flagged)
python build_nuitka.py
```

---

## **License**

.py files:

*   **MIT License** - feel free to use in your projects!

images and logos:

*   **RoyaltyFree**, please replace the logos and images with your images. Except for pywiz.png, please include it in the splash.
