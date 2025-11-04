
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

APP_TITLE = "PyWiz Installer"
APP_SIZE = "720x880"  # Increased height to accommodate 700px header images + content

# Get assets directory path (works for both development and bundled exe)
def get_assets_dir():
    """Get the assets directory, handling both development and bundled execution"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in development
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'assets')

ASSETS_DIR = get_assets_dir()
ICON_PATH = os.path.join(ASSETS_DIR, 'app.ico')

# Cache for loaded images to avoid reloading
image_cache = {}

def load_header_image(page_number):
    """Load header image for the specified page number"""
    image_key = f"page{page_number}"
    if image_key in image_cache:
        return image_cache[image_key]

    image_path = os.path.join(ASSETS_DIR, f'header_{image_key}.jpg')
    if os.path.exists(image_path):
        try:
            # Load and resize image to fit window width (720px) while maintaining aspect ratio
            image = Image.open(image_path)
            # Calculate new height to maintain aspect ratio for 720px width
            aspect_ratio = image.height / image.width
            new_height = int(720 * aspect_ratio)
            image = image.resize((720, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            image_cache[image_key] = photo
            return photo
        except Exception as e:
            print(f"Warning: Could not load header image for {image_key}: {e}")
            return None
    else:
        print(f"Warning: Header image not found: {image_path}")
        return None

class Wizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.resizable(False, False)

        # Set window icon if available
        print(f"Looking for icon at: {ICON_PATH}")
        print(f"Icon exists: {os.path.exists(ICON_PATH)}")
        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
                print("Icon set successfully")
            except Exception as e:
                print(f"Warning: Could not set window icon: {e}")
        else:
            print("Icon file not found")

        # Shared config state
        self.state = {
            "license1_scrolled_to_end": False,
            "license1_accepted": False,
            "ui_tests_toggle": False,
            "enum_choice": "Option A",
            "install_dir": "",
        }

        # Container for pages
        self.container = tk.Frame(self, bg="#f7f7f7")
        self.container.pack(fill="both", expand=True)

        # Nav bar
        self.nav = tk.Frame(self, height=52)
        self.nav.pack(fill="x", side="bottom")
        self.prev_btn = ttk.Button(self.nav, text="Previous", command=self.prev_page, takefocus=0)
        self.next_btn = ttk.Button(self.nav, text="Next", command=self.next_page, takefocus=0)

        self.prev_btn.pack(side="left", padx=10, pady=10)
        self.next_btn.pack(side="right", padx=10, pady=10)

        # Build pages
        self.pages = []
        self.current = 0
        self.pages.append(Page1(self.container, self.state, self._update_nav, 1))
        self.pages.append(Page2(self.container, self.state, self._update_nav, 2))
        self.pages.append(Page3(self.container, self.state, self._update_nav, 3))

        for p in self.pages:
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._show(0)

    # Navigation helpers
    def _show(self, idx: int):
        self.current = idx
        for i, p in enumerate(self.pages):
            p.tkraise() if i == idx else None
        self._update_nav()

    def _update_nav(self):
        # Previous disabled on first page
        self.prev_btn.config(state=("disabled" if self.current == 0 else "normal"))

        # Next label/enable rules per page
        if self.current == len(self.pages) - 1:
            self.next_btn.config(text="Finish")
        else:
            self.next_btn.config(text="Next")

        # Page-specific gating (enable/disable Next)
        if self.current == 0:
            can_next = self.state["license1_accepted"]
        else:
            can_next = True

        self.next_btn.config(state=("normal" if can_next else "disabled"))

    def prev_page(self):
        if self.current > 0:
            self._show(self.current - 1)

    def next_page(self):
        # Hook: print config when leaving Page 2 by pressing Next
        if self.current == 1:
            print("[CONFIG] ui_tests_toggle =", self.state["ui_tests_toggle"])
            print("[CONFIG] enum_choice     =", self.state["enum_choice"])

        # Finish on last page
        if self.current == len(self.pages) - 1:
            print("[DONE] Install directory =", self.state["install_dir"])
            self.destroy()
            return

        self._show(self.current + 1)

# ------------------ PAGES ------------------

class PageBase(tk.Frame):
    def __init__(self, parent, state, on_change, page_number):
        super().__init__(parent, bg="white")
        self.state = state
        self.on_change = on_change
        self.page_number = page_number

        # Load and display header image
        header_image = load_header_image(page_number)
        if header_image:
            self.header_label = tk.Label(self, image=header_image, bg="white", borderwidth=0, highlightthickness=0)
            self.header_label.image = header_image  # Keep reference to prevent garbage collection
            self.header_label.pack(anchor="nw", padx=0, pady=0, fill="x")

        # Title text (only if no image or as fallback)
        self.header = tk.Label(self, text=self.title_text(), font=("Segoe UI", 16, "bold"), bg="white")
        self.header.pack(anchor="w", padx=16, pady=(16, 8))

        self.body = tk.Frame(self, bg="white")
        self.body.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    def title_text(self):
        return f"Page {self.page_number}"

class Page1(PageBase):
    def title_text(self): return "Page 1 — License (must accept)"

    def __init__(self, parent, state, on_change, page_number):
        super().__init__(parent, state, on_change, page_number)

        # Scrollable long license text
        wrapper = tk.Frame(self.body, bg="white", height=200)
        wrapper.pack(fill="x")

        self.scroll = tk.Scrollbar(wrapper)
        self.scroll.pack(side="right", fill="y")

        self.text = tk.Text(wrapper, wrap="word", yscrollcommand=self.scroll.set, bg="#fafafa", height=22)
        self.text.pack(side="left", fill="both")
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

        self.accept_check = ttk.Checkbutton(self.body, text="I accept the license agreement",
                                           variable=self.accept_var, command=on_toggle, state="disabled", takefocus=0)
        self.accept_check.pack(anchor="w", pady=(8, 0))

        # Hint
        tk.Label(self.body, text="You must scroll to the end of the license text above to enable the acceptance checkbox.",
                 bg="white", fg="#555").pack(anchor="w", pady=(4, 0))

        # Track scroll position; enable checkbox only at end
        self._bind_scroll_checks()
        self._check_scroll()

    def _bind_scroll_checks(self):
        # Bind events to the text widget
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>", "<KeyRelease>", "<ButtonRelease-1>", "<Configure>"):
            self.text.bind(seq, lambda e: self.after(50, self._check_scroll))

        # Bind events to the scrollbar widget
        for seq in ("<ButtonRelease-1>", "<B1-Motion>", "<Button-1>", "<Button-2>", "<Button-3>"):
            self.scroll.bind(seq, lambda e: self.after(50, self._check_scroll))

    def _check_scroll(self):
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

class Page2(PageBase):
    def title_text(self): return "Page 2 — Options test"

    def __init__(self, parent, state, on_change, page_number):
        super().__init__(parent, state, on_change, page_number)

        # Toggle
        self.toggle_var = tk.BooleanVar(value=self.state["ui_tests_toggle"])
        def on_toggle():
            self.state["ui_tests_toggle"] = self.toggle_var.get()
        ttk.Checkbutton(self.body, text="Enable UI tests (optional)", variable=self.toggle_var,
                        command=on_toggle, takefocus=0).pack(anchor="w", pady=8)

        # Enum (combobox)
        ttk.Label(self.body, text="Choose an option:").pack(anchor="w", pady=(12, 4))
        self.combo = ttk.Combobox(self.body, values=["Option A", "Option B", "Option C"], state="readonly", takefocus=0)
        self.combo.set(self.state["enum_choice"])
        self.combo.pack(anchor="w", ipady=2)

        def on_combo_change(_evt=None):
            self.state["enum_choice"] = self.combo.get()
        self.combo.bind("<<ComboboxSelected>>", on_combo_change)

        # Note
        note = tk.Label(self.body, text="Click Next to print the current config to the console.",
                        fg="#555", bg="white")
        note.pack(anchor="w", pady=12)

class Page3(PageBase):
    def title_text(self): return "Page 3 — Choose install directory"

    def __init__(self, parent, state, on_change, page_number):
        super().__init__(parent, state, on_change, page_number)

        # Field + validation color
        path_row = tk.Frame(self.body, bg="white")
        path_row.pack(fill="x", pady=(6, 4))

        ttk.Label(path_row, text="Install directory:").pack(side="left", padx=(0, 8))
        self.path_var = tk.StringVar(value=self.state["install_dir"])

        self.entry = tk.Entry(path_row, textvariable=self.path_var, width=60, takefocus=0)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<KeyRelease>", lambda e: self._sync_and_validate())

        def pick_dir():
            d = filedialog.askdirectory(title="Select installation directory")
            if d:
                self.path_var.set(d)
                self._sync_and_validate()

        ttk.Button(path_row, text="Browse...", command=pick_dir, takefocus=0).pack(side="left", padx=8)

        # Operator button: append F:/Foo/Foo/Foo
        def append_magic():
            self.path_var.set(self.path_var.get() + (" " if self.path_var.get() else "") + "F:/Foo/Foo/Foo")
            self._sync_and_validate()

        ttk.Button(self.body, text="Append F:/Foo/Foo/Foo", command=append_magic, takefocus=0).pack(anchor="w", pady=8)

        # Hint
        tk.Label(self.body, text="Field turns red if the path does not exist.",
                 bg="white", fg="#555").pack(anchor="w", pady=(4, 0))

        # Initial validation
        self._sync_and_validate()
        on_change()

    def _sync_and_validate(self):
        val = self.path_var.get().strip()
        self.state["install_dir"] = val
        exists = os.path.isdir(val)
        self.entry.config(fg=("black" if exists else "red"))

if __name__ == "__main__":
    app = Wizard()
    app.mainloop()

