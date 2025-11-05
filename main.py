
import os
import sys
from PIL import Image as pillowImage
from PIL import ImageTk as pillowImageTk
import tkinter as tk
from tkinter import filedialog
import sv_ttk #tk theme: https://github.com/rdbende/Sun-Valley-ttk-theme/tree/main

APP_TITLE = "Geo-Scatter Installer"
APP_SIZE = "720x880"  # Increased height to accommodate 700px header images + content

def get_assets_dir():
    """Get the assets directory, handling both development and bundled execution"""
    try: base_path = sys._MEIPASS # PyInstaller creates a temp folder and stores path in _MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__)) # Running in development
    return os.path.join(base_path, 'assets')

ASSETS_DIR = get_assets_dir()
ICON_PATH = os.path.join(ASSETS_DIR, 'app.ico')

IMAGECACHE = {}

def load_header_image(page_number):
    """Load header image for the specified page number"""
    image_key = f"page{page_number}"
    if (image_key in IMAGECACHE):
        return IMAGECACHE[image_key]
    image_path = os.path.join(ASSETS_DIR, f'header_{image_key}.jpg')
    if os.path.exists(image_path):
        try: 
            image = pillowImage.open(image_path) # Load and resize image to fit window width (720px) while maintaining aspect ratio
            aspect_ratio = image.height / image.width # Calculate new height to maintain aspect ratio for 720px width
            new_height = int(720 * aspect_ratio)
            image = image.resize((720, new_height), pillowImage.LANCZOS)
            photo = pillowImageTk.PhotoImage(image)
            IMAGECACHE[image_key] = photo
            return photo
        except Exception as e:
            print(f"[WARNING]: Could not load header image for {image_key}: {e}")
            return None
    else:
        print(f"[WARNING]: Header image not found: {image_path}")
        return None

class Wizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.resizable(False, False)

        # Set window icon if available
        if os.path.exists(ICON_PATH):
            try: self.iconbitmap(ICON_PATH)
            except Exception as e:
                print(f"[ERROR]: Wizard(): Could not set window icon: {e}")
        else:   print(f"[ERROR]: Wizard(): Icon file not found '{ICON_PATH}'")

        # Set modern Sun Valley theme
        sv_ttk.set_theme("dark")

        # Set window close protocol
        self.protocol("WM_DELETE_WINDOW", self.premature_window_close_callback)

        # Shared config state
        self.state = {
            "license1_scrolled_to_end": False,
            "license1_accepted": False,
            "ui_tests_toggle": False,
            "enum_choice": "Option A",
            "install_dir": "",
            }

        # Container for pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Nav bar with darker background
        self.nav = tk.Frame(self, height=52, bg="#141414")
        self.nav.pack(fill="x", side="bottom")

        self.prev_btn = tk.ttk.Button(self.nav, text="Previous", command=self.prev_page, takefocus=0)
        self.prev_btn.pack(side="left", padx=10, pady=10)

        # Page indicator centered
        self.page_indicator = tk.Label(self.nav, text="Page 1", bg="#141414", fg="#888888",
                                      font=("Segoe UI", 9))
        self.page_indicator.place(relx=0.5, rely=0.5, anchor="center")

        self.next_btn = tk.ttk.Button(self.nav, text="Next", command=self.next_page, takefocus=0)
        self.next_btn.pack(side="right", padx=10, pady=10)

        # Build pages
        self.pages = []
        self.current = 0
        self.pages.append(Page1(self.container, self.state, self.update_page_state, 1))
        self.pages.append(Page2(self.container, self.state, self.update_page_state, 2))
        self.pages.append(Page3(self.container, self.state, self.update_page_state, 3))

        for p in self.pages:
            p.wizard = self  # Set wizard reference for callbacks
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.update_page(0)

    # Navigation helpers
    def update_page(self, idx: int):
        # Safety check - don't update if pages aren't initialized yet
        if not self.pages or idx >= len(self.pages):
            return None
        
        self.current = idx
        current_page = self.pages[idx]
        
        for i, p in enumerate(self.pages):
            p.tkraise() if i == idx else None
        
        # Update page indicator with custom text
        self.page_indicator.config(text=current_page.footer_text)
        
        # Update button labels
        self.prev_btn.config(text=current_page.prev_button_name)
        self.next_btn.config(text=current_page.next_button_name)
        
        # Update button commands to call page-specific callbacks
        self.prev_btn.config(command=current_page.prev_button_callback)
        self.next_btn.config(command=current_page.next_button_callback)
        
        # Update button states
        can_prev = current_page.prev_button_enabled() if hasattr(current_page, 'prev_button_enabled') else True
        self.prev_btn.config(state=("normal" if can_prev else "disabled"))

        can_next = current_page.next_button_enabled() if hasattr(current_page, 'next_button_enabled') else True
        self.next_btn.config(state=("normal" if can_next else "disabled"))
        
        return None

    def update_page_state(self):
        """Called by pages when their state changes - just refresh current page"""
        self.update_page(self.current)
        return None

    def prev_page(self):
        if (self.current > 0):
            self.update_page(self.current - 1)
        return None

    def next_page(self):
        if (self.current < len(self.pages) - 1):
            self.update_page(self.current + 1)
        return None

    def premature_window_close_callback(self):
        """Called when user closes the window (clicks X button)"""
        print("[INFO] User unexpectely closed the installer window")
        print("[INFO] Installation was cancelled")
        self.destroy()
        return None

# ------------------ PAGES ------------------

class PageBase(tk.Frame):

    title_text = "*CHILDREN DEFINED*"
    footer_text = "*CHILDREN DEFINED*"

    prev_button_name = "Previous"
    next_button_name = "Next"

    # def prev_button_callback(self):
    #     """*CHILDREN DEFINED*: Called when Previous button is clicked on this page"""
    #     self.wizard.prev_page()
    #     return None

    # def next_button_callback(self):
    #     """*CHILDREN DEFINED*: Called when Next button is clicked on this page"""
    #     self.wizard.next_page()
    #     return None

    # def prev_button_enabled(self):
    #     """*CHILDREN DEFINED*: Override in subclasses to control Previous button state"""
    #     return True

    # def next_button_enabled(self):
    #     """*CHILDREN DEFINED*: Override in subclasses to control Next button state"""
    #     return True

    def __init__(self, parent, state, on_change, page_number):
        super().__init__(parent)  # Let Sun Valley theme handle background
        self.state = state
        self.on_change = on_change
        self.page_number = page_number
        self.wizard = None  # Will be set by Wizard class

        # Load and display header image
        header_image = load_header_image(page_number)
        if header_image:
            self.header_label = tk.Label(self, image=header_image, borderwidth=0, highlightthickness=0)
            self.header_label.image = header_image  # Keep reference to prevent garbage collection
            self.header_label.pack(anchor="nw", padx=0, pady=0, fill="x")

        # Title text (only if no image or as fallback)
        self.header = tk.Label(self, text=self.title_text, font=("Segoe UI", 16, "bold"))
        self.header.pack(anchor="w", padx=16, pady=(16, 8))

        # Separator line below title
        tk.ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16, pady=(0, 0))

        # Spacer below separator
        tk.Frame(self, height=16).pack()

        self.body = tk.Frame(self)
        self.body.pack(fill="both", expand=True, padx=16, pady=(0, 12))

class Page1(PageBase):

    title_text = "License Agreement"
    footer_text = "Page 1"

    prev_button_name = "Cancel"
    next_button_name = "Next"

    def prev_button_callback(self):
        self.wizard.destroy()
        return None

    def next_button_callback(self):
        self.wizard.next_page()
        return None

    def next_button_enabled(self):
        return self.state["license1_accepted"]

    def __init__(self, parent, state, on_change, page_number):
        super().__init__(parent, state, on_change, page_number)

        # Scrollable long license text
        wrapper = tk.Frame(self.body, height=200)
        wrapper.pack(fill="x")

        self.scroll = tk.ttk.Scrollbar(wrapper)
        self.scroll.pack(side="right", fill="y")

        self.text = tk.Text(wrapper, wrap="word", yscrollcommand=self.scroll.set, height=26, background="#141414", borderwidth=0, highlightthickness=0)
        self.text.pack(side="left", fill="both", expand=True, padx=(0, 8),)
        self.scroll.config(command=self.text.yview)

        # Populate large license text
        lines = []
        for i in range(1, 201):  # 200 lines of license text
            lines.append(f"License Agreement Line {i}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                        f"Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                        f"Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
                        f"Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\n")
        self.text.insert("1.0", "".join(lines))
        self.text.config(state="disabled")

        # Accept toggle (disabled until scrolled to end)
        self.accept_var = tk.BooleanVar(value=self.state["license1_accepted"])
        def on_toggle():
            self.state["license1_accepted"] = self.accept_var.get()
            self.on_change()

        self.accept_check = tk.ttk.Checkbutton(self.body, text="I accept the license agreement",
                                           variable=self.accept_var, command=on_toggle, state="disabled", takefocus=0)
        self.accept_check.pack(anchor="w", pady=(8, 0))

        # Hint
        tk.Label(self.body, text="You must scroll to the end of the license text above to enable the acceptance checkbox.").pack(anchor="w", pady=(4, 0))

        # Track scroll position; enable checkbox only at end
        self.bind_scroll_checks()
        self.check_scroll()

    def bind_scroll_checks(self):
        # Bind events to the text widget
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>", "<KeyRelease>", "<ButtonRelease-1>", "<Configure>"):
            self.text.bind(seq, lambda e: self.after(50, self.check_scroll))

        # Bind events to the scrollbar widget - check scroll state after interaction
        def on_scrollbar_release(event):
            self.after(50, self.check_scroll)
        
        self.scroll.bind("<ButtonRelease-1>", on_scrollbar_release)
        return None

    def check_scroll(self):
        # yview returns (first, last) fractions of the document visible
        first, last = self.text.yview()
        at_end = abs(last - 1.0) < 1e-3  # near bottom
        self.state["license1_scrolled_to_end"] = at_end
        if at_end:
            self.accept_check.config(state="normal")
        else:
            self.accept_check.config(state="disabled")
            self.accept_var.set(False)  # Reset acceptance if scrolled back up
            self.state["license1_accepted"] = False
        self.on_change()
        return None

class Page2(PageBase):

    title_text = "Install Options"
    footer_text = "Page 2"

    prev_button_name = "Previous"
    next_button_name = "Next"

    def prev_button_callback(self):
        self.wizard.prev_page()
        return None

    def next_button_callback(self):
        print("[CONFIG] ui_tests_toggle =", self.state["ui_tests_toggle"])
        print("[CONFIG] enum_choice     =", self.state["enum_choice"])
        self.wizard.next_page()
        return None

    def __init__(self, parent, state, on_change, page_number):
        super().__init__(parent, state, on_change, page_number)

        # Toggle
        self.toggle_var = tk.BooleanVar(value=self.state["ui_tests_toggle"])
        def on_toggle():
            self.state["ui_tests_toggle"] = self.toggle_var.get()
        tk.ttk.Checkbutton(self.body, text="Enable UI tests (optional)", variable=self.toggle_var,
                        command=on_toggle, takefocus=0).pack(anchor="w", pady=8)

        # Enum (using Radio buttons for cleaner look)
        tk.ttk.Label(self.body, text="Choose an option:").pack(anchor="w", pady=(12, 4))
        
        self.enum_var = tk.StringVar(value=self.state["enum_choice"])
        options_frame = tk.Frame(self.body)
        options_frame.pack(anchor="w", pady=(4, 0))
        
        for option in ["Option A", "Option B", "Option C"]:
            tk.ttk.Radiobutton(options_frame, text=option, variable=self.enum_var, 
                          value=option, takefocus=0,
                          command=lambda: self.update_enum_pick()).pack(anchor="w", pady=2)

        # Note
        tk.Label(self.body, text="Click Next to print the current config to the console.").pack(anchor="w", pady=12)
        
    def update_enum_pick(self):
        self.state["enum_choice"] = self.enum_var.get()

class Page3(PageBase):
    title_text = "Define Install Directory"
    footer_text = "Page 3"

    prev_button_name = "Previous"
    next_button_name = "Finish"

    def prev_button_callback(self):
        self.wizard.prev_page()
        return None

    def next_button_callback(self):
        print("[DONE] Install directory =", self.state["install_dir"])
        self.wizard.destroy()
        return None

    def __init__(self, parent, state, on_change, page_number):
        super().__init__(parent, state, on_change, page_number)

        # Field + validation color
        path_row = tk.Frame(self.body)
        path_row.pack(fill="x", pady=(6, 4))

        tk.ttk.Label(path_row, text="Install directory:").pack(side="left", padx=(0, 8))
        self.path_var = tk.StringVar(value=self.state["install_dir"])

        self.entry = tk.Entry(path_row, textvariable=self.path_var, width=60, takefocus=0)
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<KeyRelease>", lambda e: self.sync_and_validate())

        def pick_dir():
            d = filedialog.askdirectory(title="Select installation directory")
            if d:
                self.path_var.set(d)
                self.sync_and_validate()

        tk.ttk.Button(path_row, text="Browse...", command=pick_dir, takefocus=0).pack(side="left", padx=8)

        # Operator button: append F:/Foo/Foo/Foo
        def append_magic():
            self.path_var.set(self.path_var.get() + (" " if self.path_var.get() else "") + "F:/Foo/Foo/Foo")
            self.sync_and_validate()

        tk.ttk.Button(self.body, text="Append F:/Foo/Foo/Foo", command=append_magic, takefocus=0).pack(anchor="w", pady=8)

        # Hint
        tk.Label(self.body, text="Field turns red if the path does not exist.").pack(anchor="w", pady=(4, 0))

        # Initial validation
        self.sync_and_validate()
        on_change()

    def sync_and_validate(self):
        val = self.path_var.get().strip()
        self.state["install_dir"] = val
        exists = os.path.isdir(val)
        self.entry.config(fg=("black" if exists else "red"))
        return None

if __name__ == "__main__":
    app = Wizard()
    app.mainloop()

