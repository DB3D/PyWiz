
import os
import tkinter as tk
from tkinter import ttk, filedialog

APP_TITLE = "PyWiz Installer"
APP_SIZE = "720x520"

class Wizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.resizable(False, False)

        # Shared config state
        self.state = {
            "license1_accepted": False,
            "ui_tests_toggle": False,
            "enum_choice": "Option A",
            "license3_scrolled_to_end": False,
            "license3_accepted": False,
            "install_dir": "",
        }

        # Container for pages
        self.container = tk.Frame(self, bg="#f7f7f7")
        self.container.pack(fill="both", expand=True)

        # Nav bar
        self.nav = tk.Frame(self, height=52)
        self.nav.pack(fill="x", side="bottom")
        self.prev_btn = ttk.Button(self.nav, text="Previous", command=self.prev_page)
        self.next_btn = ttk.Button(self.nav, text="Next", command=self.next_page)

        self.prev_btn.pack(side="left", padx=10, pady=10)
        self.next_btn.pack(side="right", padx=10, pady=10)

        # Build pages
        self.pages = []
        self.current = 0
        self.pages.append(Page1(self.container, self.state, self._update_nav))
        self.pages.append(Page2(self.container, self.state, self._update_nav))
        self.pages.append(Page3(self.container, self.state, self._update_nav))
        self.pages.append(Page4(self.container, self.state, self._update_nav))

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
        elif self.current == 2:
            can_next = self.state["license3_accepted"] and self.state["license3_scrolled_to_end"]
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
    def __init__(self, parent, state, on_change):
        super().__init__(parent, bg="white")
        self.state = state
        self.on_change = on_change

        self.header = tk.Label(self, text=self.title_text(), font=("Segoe UI", 16, "bold"), bg="white")
        self.header.pack(anchor="w", padx=16, pady=(16, 8))

        self.body = tk.Frame(self, bg="white")
        self.body.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    def title_text(self):
        return "Page"

class Page1(PageBase):
    def title_text(self): return "Page 1 — License (must accept)"

    def __init__(self, parent, state, on_change):
        super().__init__(parent, state, on_change)

        # Fake license text preview (short); acceptance is via button below
        preview = tk.Text(self.body, height=14, wrap="word", bg="#fafafa")
        preview.insert("1.0", "Short license intro...\n\n(Full license comes later on Page 3.)")
        preview.config(state="disabled")
        preview.pack(fill="both", expand=True)

        # Accept button
        def accept():
            self.state["license1_accepted"] = True
            self.accept_btn.config(state="disabled", text="Accepted")
            self.on_change()

        self.accept_btn = ttk.Button(self.body, text="Accept License", command=accept)
        self.accept_btn.pack(side="right", pady=8)

class Page2(PageBase):
    def title_text(self): return "Page 2 — Options test"

    def __init__(self, parent, state, on_change):
        super().__init__(parent, state, on_change)

        # Toggle
        self.toggle_var = tk.BooleanVar(value=self.state["ui_tests_toggle"])
        def on_toggle():
            self.state["ui_tests_toggle"] = self.toggle_var.get()
        ttk.Checkbutton(self.body, text="Enable UI tests (optional)", variable=self.toggle_var,
                        command=on_toggle).pack(anchor="w", pady=8)

        # Enum (combobox)
        ttk.Label(self.body, text="Choose an option:").pack(anchor="w", pady=(12, 4))
        self.combo = ttk.Combobox(self.body, values=["Option A", "Option B", "Option C"], state="readonly")
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
    def title_text(self): return "Page 3 — Read full text then accept"

    def __init__(self, parent, state, on_change):
        super().__init__(parent, state, on_change)

        # Scrollable long text
        wrapper = tk.Frame(self.body, bg="white")
        wrapper.pack(fill="both", expand=True)

        self.scroll = tk.Scrollbar(wrapper)
        self.scroll.pack(side="right", fill="y")

        self.text = tk.Text(wrapper, wrap="word", yscrollcommand=self.scroll.set, bg="#fafafa")
        self.text.pack(side="left", fill="both", expand=True)
        self.scroll.config(command=self.text.yview)

        # Populate ~300 lines
        lines = []
        for i in range(1, 301):
            lines.append(f"Line {i}: lorem ipsum dolor sit amet...\n")
        self.text.insert("1.0", "".join(lines))
        self.text.config(state="disabled")

        # Accept button (gated by scroll-to-end)
        self.accept = ttk.Button(self.body, text="Accept (after scrolling to end)", state="disabled",
                                 command=self._accept)
        self.accept.pack(side="right", pady=8)

        # Track scroll position; enable button only at end
        self._bind_scroll_checks()
        self._check_scroll()

    def _bind_scroll_checks(self):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>", "<KeyRelease>", "<ButtonRelease-1>", "<Configure>"):
            self.text.bind(seq, lambda e: self.after(50, self._check_scroll))

    def _check_scroll(self):
        # yview returns (first, last) fractions of the document visible
        first, last = self.text.yview()
        at_end = abs(last - 1.0) < 1e-3  # near bottom
        self.state["license3_scrolled_to_end"] = at_end
        if at_end and not self.state["license3_accepted"]:
            self.accept.config(state="normal")
        else:
            if not self.state["license3_accepted"]:
                self.accept.config(state="disabled")
        self.on_change()

    def _accept(self):
        self.state["license3_accepted"] = True
        self.accept.config(text="Accepted", state="disabled")
        self.on_change()

class Page4(PageBase):
    def title_text(self): return "Page 4 — Choose install directory"

    def __init__(self, parent, state, on_change):
        super().__init__(parent, state, on_change)

        # Field + validation color
        path_row = tk.Frame(self.body, bg="white")
        path_row.pack(fill="x", pady=(6, 4))

        ttk.Label(path_row, text="Install directory:").pack(side="left", padx=(0, 8))
        self.path_var = tk.StringVar(value=self.state["install_dir"])

        self.entry = tk.Entry(path_row, textvariable=self.path_var, width=60)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<KeyRelease>", lambda e: self._sync_and_validate())

        def pick_dir():
            d = filedialog.askdirectory(title="Select installation directory")
            if d:
                self.path_var.set(d)
                self._sync_and_validate()

        ttk.Button(path_row, text="Browse...", command=pick_dir).pack(side="left", padx=8)

        # Operator button: append F:/Foo/Foo/Foo
        def append_magic():
            self.path_var.set(self.path_var.get() + (" " if self.path_var.get() else "") + "F:/Foo/Foo/Foo")
            self._sync_and_validate()

        ttk.Button(self.body, text="Append F:/Foo/Foo/Foo", command=append_magic).pack(anchor="w", pady=8)

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

