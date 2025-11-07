
import os
import sys
import time
from PIL import Image as pillowImage
from PIL import ImageTk as pillowImageTk
import tkinter as tk
from tkinter import ttk
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

def show_warning_near_mouse(parent, title="Warning", message="Warning"):
    """Show a custom warning dialog near the mouse cursor"""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.configure(bg="#1c1c1c")

    # Apply theme
    sv_ttk.set_theme("dark")

    # Set window icon if available
    if os.path.exists(ICON_PATH):
        try: dialog.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"[ERROR]: show_warning_near_mouse(): Could not set window icon: {e}")
        
    # Get mouse position
    x = parent.winfo_pointerx() 
    y = parent.winfo_pointery() 
    
    # Offset so OK button is at cursor    
    x-=150
    y-=150

    # Define window position
    dialog.geometry(f"+{x}+{y}")

    # Content frame
    content = tk.Frame(dialog, bg="#1c1c1c")
    content.pack(fill="both", expand=True, padx=10, pady=10)

    # Icon + Message
    tk.Label(content, text="⚠️", font=("Segoe UI", 20), bg="#1c1c1c", fg="orange").pack(pady=(0, 10))
    tk.Label(content, text=message, font=("Segoe UI", 10), bg="#1c1c1c", fg="white", 
            wraplength=300, justify="left").pack(pady=(0, 20))

    # OK button
    ttk.Button(content, text="OK", command=dialog.destroy, takefocus=0).pack()

    # Make modal
    dialog.transient(parent)
    dialog.grab_set()
    parent.wait_window(dialog)
    
    return None

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

# oooooooooo.                               
# `888'   `Y8b                              
#  888     888  .oooo.    .oooo.o  .ooooo.  
#  888oooo888' `P  )88b  d88(  "8 d88' `88b 
#  888    `88b  .oP"888  `"Y88b.  888ooo888 
#  888    .88P d8(  888  o.  )88b 888    .o 
# o888bood8P'  `Y888""8o 8""888P' `Y8bod8P' 


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

        self.prev_btn = ttk.Button(self.nav, text="Previous", command=self.prev_page, takefocus=0)
        self.prev_btn.pack(side="left", padx=10, pady=10)

        # Page indicator centered
        self.page_indicator = tk.Label(self.nav, text="Page 1", bg="#141414", fg="#888888",
                                      font=("Segoe UI", 9))
        self.page_indicator.place(relx=0.5, rely=0.5, anchor="center")

        self.next_btn = ttk.Button(self.nav, text="Next", command=self.next_page, takefocus=0)
        self.next_btn.pack(side="right", padx=10, pady=10)

        # Build pages
        self.pages = []
        self.current = 0
        self.pages.append(Page1(self.container, self.state, self.update_page_state,))
        self.pages.append(Page2(self.container, self.state, self.update_page_state,))
        self.pages.append(Page3(self.container, self.state, self.update_page_state,))
        self.pages.append(Page4(self.container, self.state, self.update_page_state,))

        for p in self.pages:
            p.wizard = self  # Set wizard reference for callbacks
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Define transparent button style
        style = ttk.Style()
        style.configure('Transparent.TButton', foreground='#666666')
            
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
        
        # Update button states enabled/disabled
        can_prev = current_page.prev_button_enabled() if hasattr(current_page, 'prev_button_enabled') else True
        self.prev_btn.config(state=("normal" if can_prev else "disabled"))
        can_next = current_page.next_button_enabled() if hasattr(current_page, 'next_button_enabled') else True
        self.next_btn.config(state=("normal" if can_next else "disabled"))
        
        # Apply greyed out style if page wants transparency effect
        is_prev_greyedout = current_page.prev_button_greyedout() if hasattr(current_page, 'prev_button_greyedout') else False
        self.prev_btn.configure(style='Transparent.TButton' if is_prev_greyedout else 'TButton')
        is_next_greyedout = current_page.next_button_greyedout() if hasattr(current_page, 'next_button_greyedout') else False
        self.next_btn.configure(style='Transparent.TButton' if is_next_greyedout else 'TButton')
        
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


class PageBase(tk.Frame):
    page_number = -1
    title_text = "*CHILDREN DEFINED*"
    footer_text = "*CHILDREN DEFINED*"
    prev_button_name = "Previous"
    next_button_name = "Next"

    # def prev_button_callback/next_button_callback(self)->None:
    #     """*CHILDREN DEFINED*: Called when Previous button is clicked on this page"""
    #     self.wizard.prev_page/next_page()
    #     return None

    # def prev_button_enabled/next_button_enabled(self)->bool:
    #     """*CHILDREN DEFINED*: Override in subclasses to control Next button state"""
    #     return True

    # def prev_button_greyedout/next_button_greyedout(self)->bool:
    #     """*CHILDREN DEFINED*: Override to make Next button semi-transparent, like enabled==False but user can click it"""
    #     return False  # Return True to make button transparent when disabled

    def __init__(self, parent, state, on_change):
        super().__init__(parent)  # Let Sun Valley theme handle background
        self.state = state
        self.on_change = on_change
        self.wizard = None  # Will be set by Wizard class

        # Load and display header image
        header_image = load_header_image(self.page_number)
        if (header_image is not None):
            self.header_label = tk.Label(self, image=header_image, borderwidth=0, highlightthickness=0)
            self.header_label.image = header_image  # Keep reference to prevent garbage collection
            self.header_label.pack(anchor="nw", padx=0, pady=0, fill="x")

        # Title text (only if no image or as fallback)
        self.header = tk.Label(self, text=self.title_text, font=("Segoe UI", 16, "bold"))
        self.header.pack(anchor="w", padx=16, pady=(16, 8))

        # Separator line below title
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=16, pady=(0, 0))

        # Spacer below separator
        tk.Frame(self, height=16).pack()

        self.body = tk.Frame(self)
        self.body.pack(fill="both", expand=True, padx=16, pady=(0, 12))

# ooooooooo.                                    .o  
# `888   `Y88.                                o888  
#  888   .d88'  .oooo.    .oooooooo  .ooooo.   888  
#  888ooo88P'  `P  )88b  888' `88b  d88' `88b  888  
#  888          .oP"888  888   888  888ooo888  888  
#  888         d8(  888  `88bod8P'  888    .o  888  
# o888o        `Y888""8o `8oooooo.  `Y8bod8P' o888o 
#                        d"     YD                  
#                        "Y88888P'                  
                                                  
class Page1(PageBase):
    page_number = 1
    title_text = "License Agreement"
    footer_text = f"Page {page_number}"
    prev_button_name = "Cancel"

    def prev_button_callback(self) -> None:
        self.wizard.destroy()
        return None

    def next_button_callback(self) -> None:
        # Check if license accepted, otherwise show warning
        match self.state["license1_accepted"]:
            case False:
                show_warning_near_mouse(self.wizard,
                    title="Cannot continue",
                    message="To continue the installation, agreeing with the license is required. The accept button will be available once you scroll to the end of the license text.",
                    )
            case True:
                self.wizard.next_page()
        return None

    def next_button_greyedout(self) -> bool:
        return self.state["license1_accepted"]==False  # Make button semi-transparent when license not accepted, user can click it, will show warning

    def __init__(self, parent, state, on_change):
        super().__init__(parent, state, on_change)

        # Scrollable long license text
        wrapper = tk.Frame(self.body, height=200)
        wrapper.pack(fill="x")

        self.scroll = ttk.Scrollbar(wrapper)
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
            return None

        self.accept_check = ttk.Checkbutton(self.body, text="I accept the license agreement",
                                           variable=self.accept_var, command=on_toggle, state="disabled", takefocus=0)
        self.accept_check.pack(anchor="w", pady=(8, 0))

        # Hint
        tk.Label(self.body, text="*Read the license first before accepting it. This button will be available once you scroll to the end of the license text.").pack(anchor="w", pady=(4, 0))

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
            return None
        
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

# ooooooooo.                                    .oooo.   
# `888   `Y88.                                .dP""Y88b  
#  888   .d88'  .oooo.    .oooooooo  .ooooo.        ]8P' 
#  888ooo88P'  `P  )88b  888' `88b  d88' `88b     .d8P'  
#  888          .oP"888  888   888  888ooo888   .dP'     
#  888         d8(  888  `88bod8P'  888    .o .oP     .o 
# o888o        `Y888""8o `8oooooo.  `Y8bod8P' 8888888888 
#                        d"     YD                       
#                        "Y88888P'                       
                                                       
class Page2(PageBase):
    page_number = 2
    title_text = "Install Options"
    footer_text = f"Page {page_number}"

    def prev_button_callback(self) -> None:
        self.wizard.prev_page()
        return None

    def next_button_callback(self) -> None:
        print("[CONFIG] Desktop shortcut:", self.state['bool_option1'])
        print(f"[CONFIG] Installation Type: {self.state['enum_choice']}")
        print(f"[CONFIG] Memory Allocation: {self.state['float_value']:.1f} GB")
        print(f"[CONFIG] Thread Count: {self.state['int_value']}")
        self.wizard.next_page()
        return None

    def __init__(self, parent, state, on_change):
        super().__init__(parent, state, on_change)

        # Initialize state if needed
        if "bool_option1" not in self.state:
            self.state.update({
                "bool_option1": True,
                "enum_choice": "Standard",
                "float_value": 50.0,
                "int_value": 10,
            })

        # Panel 1: Boolean Checkbox
        ttk.Label(self.body, text="Installation Options:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        bool_frame = tk.Frame(self.body)
        bool_frame.pack(anchor="w", fill="x", pady=(0, 16))
        
        self.bool1_var = tk.BooleanVar(value=self.state["bool_option1"])
        
        ttk.Checkbutton(bool_frame, text="Create desktop shortcut", variable=self.bool1_var,
                          command=lambda: self.update_bool("bool_option1", self.bool1_var), takefocus=0).pack(anchor="w", pady=1)

        ttk.Separator(self.body, orient="horizontal").pack(fill="x", pady=8)

        # Panel 2: Enum Radio Buttons
        ttk.Label(self.body, text="Installation Type:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        
        self.enum_var = tk.StringVar(value=self.state["enum_choice"])
        enum_frame = tk.Frame(self.body)
        enum_frame.pack(anchor="w", pady=(0, 16))
        
        for option in ["Standard", "Complete", "Custom"]:
            ttk.Radiobutton(enum_frame, text=option, variable=self.enum_var, 
                          value=option, takefocus=0,
                          command=lambda: self.update_enum()).pack(anchor="w", pady=1)

        ttk.Separator(self.body, orient="horizontal").pack(fill="x", pady=8)

        # Panel 3: Sliders
        ttk.Label(self.body, text="Advanced Settings:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        
        # Float slider
        float_frame = tk.Frame(self.body)
        float_frame.pack(anchor="w", fill="x", pady=(8, 0))

        ttk.Label(float_frame, text="Memory Allocation (GB):").pack(anchor="w")
        float_slider_frame = tk.Frame(float_frame)
        float_slider_frame.pack(anchor="w", fill="x", pady=(4, 0))

        self.float_var = tk.DoubleVar(value=self.state["float_value"])
        self.float_slider = ttk.Scale(float_slider_frame, from_=0, to=100, variable=self.float_var,
                                        orient="horizontal", command=lambda v: self.update_float())
        self.float_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.float_label = tk.Label(float_slider_frame, text=f"{self.state['float_value']:.1f} GB", width=8)
        self.float_label.pack(side="right")
        
        # Int slider
        int_frame = tk.Frame(self.body)
        int_frame.pack(anchor="w", fill="x", pady=(0, 0))
        
        ttk.Label(int_frame, text="Thread Count:").pack(anchor="w")
        int_slider_frame = tk.Frame(int_frame)
        int_slider_frame.pack(anchor="w", fill="x", pady=(0, 0))
        
        self.int_var = tk.IntVar(value=self.state["int_value"])
        self.int_slider = ttk.Scale(int_slider_frame, from_=1, to=32, variable=self.int_var,
                                      orient="horizontal", command=lambda v: self.update_int())
        self.int_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.int_label = tk.Label(int_slider_frame, text=f"{self.state['int_value']}", width=8)
        self.int_label.pack(side="right")

        # Note
        tk.Label(self.body, text="Click Next to save configuration and continue.").pack(anchor="w", pady=(12, 0))
        
    def update_bool(self, key, var):
        self.state[key] = var.get()
        return None
    
    def update_enum(self):
        self.state["enum_choice"] = self.enum_var.get()
        return None
    
    def update_float(self):
        val = self.float_var.get()
        self.state["float_value"] = val
        self.float_label.config(text=f"{val:.1f} GB")
        return None
    
    def update_int(self):
        val = int(self.int_var.get())
        self.state["int_value"] = val
        self.int_label.config(text=f"{val}")
        return None

# ooooooooo.                                    .oooo.
# `888   `Y88.                                .dP""Y88b
#  888   .d88'  .oooo.    .oooooooo  .ooooo.        ]8P'
#  888ooo88P'  `P  )88b  888' `88b  d88' `88b     <88b.
#  888          .oP"888  888   888  888ooo888      `88b.
#  888         d8(  888  `88bod8P'  888    .o o.   .88P
# o888o        `Y888""8o `8oooooo.  `Y8bod8P' `8bd88P'
#                        d"     YD
#                        "Y88888P'

class Page3(PageBase):
    page_number = 3
    title_text = "Loadbar Test"
    footer_text = f"Page {page_number}"

    def prev_button_callback(self) -> None:
        self.wizard.prev_page()
        return None

    def next_button_callback(self) -> None:
        match self.loadbar_complete:
            case False:
                show_warning_near_mouse(self.wizard,
                    title="Cannot continue",
                    message="Loadbar has to be completed before continuing.",
                    )
            case True:
                self.wizard.next_page()
        return None

    def next_button_greyedout(self) -> bool:
        return (self.loadbar_complete==False)

    def __init__(self, parent, state, on_change):
        super().__init__(parent, state, on_change)

        # Initialize loading state
        self.loadbar_complete = False
        self.loadbar_progress = 0
        self.loadbar_loading = False

        # Initialize state if needed
        if ("loadbar_progress" not in self.state):
            self.state.update({
                "loadbar_progress": 0,
                "loadbar_complete": False,
            })

        # Title and description
        ttk.Label(self.body, text="Loading Bar Test", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))
        tk.Label(self.body, text="This page demonstrates a fake loading process with a progress bar.\nClick the button below to start the loading simulation.").pack(anchor="w", pady=(0, 20))

        # Progress bar container
        progress_frame = tk.Frame(self.body)
        progress_frame.pack(fill="x", pady=(20, 0))

        # Progress bar
        self.progress_var = tk.DoubleVar(value=self.state["loadbar_progress"])
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress_bar.pack(fill="x", pady=(0, 5))

        # Status label
        self.status_label = tk.Label(progress_frame, text="Ready to start loading", font=("Segoe UI", 10), fg="#888888")
        self.status_label.pack(anchor="w")

        # Start button
        self.start_button = ttk.Button(self.body, text="Start Loading Stuff", command=self.start_loadbar, takefocus=0)
        self.start_button.pack(anchor="w", pady=(20, 0))

        # Instructions
        tk.Label(self.body, text="Once the loadbar reaches 100%, the Next button will be enabled.").pack(anchor="w", pady=(20, 0))

    def start_loadbar(self):
        if (self.loadbar_loading==True):
            return None
        self.loadbar_loading = True
        self.start_button.config(state="disabled", text="Loading...")
        self.loadbar_progress = 0
        self.progress_var.set(0)
        self.status_label.config(text="Initializing loading...", fg="#ffffff")
        self.loadbar_complete = False
        self.on_change()
        self.update_progress()
        return None

    def update_progress(self):
        if (self.loadbar_loading==False):
            return None

        self.loadbar_progress += 1
        self.progress_var.set(self.loadbar_progress)
        self.state["loadbar_progress"] = self.loadbar_progress

        # Update status messages based on progress
        match self.loadbar_progress:
            case v if (v >= 100):
                self.status_label.config(text="Loading complete!", fg="#00ff00")
                self.loadbar_complete = True
                self.loadbar_loading = False
                self.start_button.config(state="normal", text="Loading Complete")
                self.state["loadbar_complete"] = True
                self.on_change()
                return
            case 70:
                self.status_label.config(text="Finalizing installation...", fg="#ffffff")
            case 50:
                self.status_label.config(text="Configuring settings...", fg="#ffffff")
            case 30:
                self.status_label.config(text="Installing dependencies...", fg="#ffffff")
            case 20:
                self.status_label.config(text="Loading core files...", fg="#ffffff")

        # Schedule next update
        self.after(100, self.update_progress)
        return None

# ooooooooo.                                        .o   
# `888   `Y88.                                    .d88   
#  888   .d88'  .oooo.    .oooooooo  .ooooo.    .d'888   
#  888ooo88P'  `P  )88b  888' `88b  d88' `88b .d'  888   
#  888          .oP"888  888   888  888ooo888 88ooo888oo 
#  888         d8(  888  `88bod8P'  888    .o      888   
# o888o        `Y888""8o `8oooooo.  `Y8bod8P'     o888o  
#                        d"     YD                       
#                        "Y88888P'                       
                                                       
class Page4(PageBase):
    page_number = 4
    title_text = "Define Install Directory"
    footer_text = f"Page {page_number}"
    next_button_name = "Finish"

    def prev_button_callback(self) -> None:
        self.wizard.prev_page()
        return None

    def next_button_greyedout(self) -> bool:
        return (self.path_var_valid==False)

    def next_button_callback(self) -> None:
        match self.path_var_valid:
            case False:
                show_warning_near_mouse(self.wizard,
                    title="Cannot continue",
                    message="The install directory is not a directory. Please select a valid directory, and not a file.",
                    )
            case True:
                self.wizard.destroy()
        return None

    def __init__(self, parent, state, on_change):
        super().__init__(parent, state, on_change)

        # Field + validation color
        path_row = tk.Frame(self.body)
        path_row.pack(fill="x", pady=(6, 4))

        ttk.Label(path_row, text="Install directory:").pack(side="left", padx=(0, 8))
        self.path_var = tk.StringVar(value=self.state["install_dir"],)
        self.path_var_stripped = self.path_var.get().strip()
        self.path_var_valid = False

        self.entry = tk.Entry(path_row, textvariable=self.path_var, width=60, takefocus=0, background="#141414", borderwidth=0, highlightthickness=0)
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<KeyRelease>", lambda e: self.sync_and_validate())

        def pick_dir():
            d = filedialog.askdirectory(title="Select installation directory")
            self.path_var.set(d)
            self.sync_and_validate()
            return None

        ttk.Button(path_row, text="Browse...", command=pick_dir, takefocus=0).pack(side="left", padx=8)

        # Operator button: append F:/This/Path
        def append_magic():
            self.path_var.set(self.path_var.get() + (" " if self.path_var.get() else "") + "F:/This/Path")
            self.sync_and_validate()
            return None

        ttk.Button(self.body, text="Append F:/This/Path", command=append_magic, takefocus=0).pack(anchor="w", pady=8)
        tk.Label(self.body, text="Field turns red if the path does not exist.").pack(anchor="w", pady=(4, 0))

        on_change()

    def sync_and_validate(self):
        self.path_var_stripped = self.path_var.get().strip()
        self.path_var_valid = os.path.isdir(self.path_var_stripped)
        self.state["install_dir"] = self.path_var_stripped
        self.entry.config(fg=("white" if self.path_var_valid else "red"))
        self.on_change()
        return None

if __name__ == "__main__":
    app = Wizard()
    app.mainloop()

