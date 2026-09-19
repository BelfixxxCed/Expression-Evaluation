"""
Programming Exercise 01: Strings and DFA
Course: CMSC 129

This program recognizes strings based on a given deterministic finite automaton (DFA).
It provides a graphical user interface for loading .in (input strings) and .dfa
(transition table) files, processing strings against the DFA, and saving results.

Module Breakdown:
    1. DFA Parser & Validator             — parse_dfa(), load_input_strings()
    2. DFA Evaluator                      — process_dfa(), evaluate_strings()
    3. GUI & File I/O                     — DFAApp class
"""

import os
import csv
import io
import tkinter as tk
from tkinter import filedialog, ttk


# ==============================================================================
# SECTION 1: DFA PARSER & VALIDATOR
# ==============================================================================

def parse_dfa(file_path):
    """
    Parse and validate a .dfa CSV file.

    The .dfa format is:
        Line 1: Two comma-separated unique single-character alphabet symbols.
        Lines 2+: Four comma-separated values per row:
            type   — "-" (start), "+" (final), or "" (neither)
            state  — Uppercase letter A–Z
            dest1  — Next state for first alphabet symbol (uppercase A–Z)
            dest2  — Next state for second alphabet symbol (uppercase A–Z)

    Validation rules:
        - At least 2 lines (alphabet + one state).
        - Exactly 2 unique single-character symbols on line 1.
        - Each state row must have exactly 4 fields.
        - Type field must be "-", "+", or blank.
        - State labels must be uppercase A–Z.
        - Exactly one start state ("-") across all rows.
        - No duplicate state labels.
        - All destination states must reference defined states.

    Args:
        file_path: Path to the .dfa file.

    Returns:
        A tuple (is_valid, dfa_object, error_msg):
            is_valid  — True if the file is a valid DFA.
            dfa_object — Dict with keys "alphabet" and "states", or None if invalid.
            error_msg  — "" on success, or a description of the first error found.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except Exception as e:
        return (False, None, f"Could not read file: {e}")

    # Parse the CSV content
    reader = csv.reader(io.StringIO(raw_content))
    rows = []
    for row in reader:
        rows.append(row)

    if len(rows) < 2:
        return (False, None, "File must contain at least an alphabet line and one state row.")

    # ---- Validate alphabet line (line 1) ----
    alphabet_row = rows[0]
    # Strip whitespace from each symbol
    alphabet = [symbol.strip() for symbol in alphabet_row]
    # Remove any empty entries that may result from trailing commas
    alphabet = [s for s in alphabet if s != ""]

    if len(alphabet) != 2:
        return (False, None, "Alphabet line must define exactly 2 symbols.")

    if len(alphabet[0]) != 1 or len(alphabet[1]) != 1:
        return (False, None, "Each alphabet symbol must be exactly one character.")

    if alphabet[0] == alphabet[1]:
        return (False, None, "Alphabet symbols must be unique.")

    # ---- First pass: collect all defined states and validate row structure ----
    states = {}
    start_state_count = 0
    state_rows = rows[1:]

    if len(state_rows) == 0:
        return (False, None, "DFA must define at least one state.")

    for line_num, row in enumerate(state_rows, start=2):
        if len(row) != 4:
            return (False, None, f"Line {line_num}: Expected 4 comma-separated values, got {len(row)}.")

        raw_type = row[0].strip()
        raw_state = row[1].strip()
        raw_dest1 = row[2].strip()
        raw_dest2 = row[3].strip()

        # Validate type field
        if raw_type not in ("-", "+", ""):
            return (False, None, f"Line {line_num}: Type must be '-', '+', or blank. Got '{raw_type}'.")

        # Validate state label
        if len(raw_state) != 1 or not raw_state.isupper():
            return (False, None, f"Line {line_num}: State label must be a single uppercase letter A–Z. Got '{raw_state}'.")

        # Check for duplicate state labels
        if raw_state in states:
            return (False, None, f"Line {line_num}: Duplicate state label '{raw_state}'.")

        # Count start states
        if raw_type == "-":
            start_state_count += 1

        # Validate destination labels (must be single uppercase A–Z)
        if len(raw_dest1) != 1 or not raw_dest1.isupper():
            return (False, None, f"Line {line_num}: Destination for '{alphabet[0]}' must be a single uppercase letter A–Z. Got '{raw_dest1}'.")

        if len(raw_dest2) != 1 or not raw_dest2.isupper():
            return (False, None, f"Line {line_num}: Destination for '{alphabet[1]}' must be a single uppercase letter A–Z. Got '{raw_dest2}'.")

        states[raw_state] = {
            "type": raw_type,
            "transitions": {
                alphabet[0]: raw_dest1,
                alphabet[1]: raw_dest2,
            },
        }

    # ---- Validate exactly one start state ----
    if start_state_count == 0:
        return (False, None, "DFA must have exactly one start state ('-'). None found.")

    if start_state_count > 1:
        return (False, None, f"DFA must have exactly one start state ('-'). Found {start_state_count}.")

    # ---- Second pass: verify all destinations reference defined states ----
    defined_labels = set(states.keys())
    for label, data in states.items():
        for symbol, dest in data["transitions"].items():
            if dest not in defined_labels:
                return (
                    False,
                    None,
                    f"State '{label}': Transition on '{symbol}' goes to undefined state '{dest}'.",
                )

    # ---- Build and return the valid DFA object ----
    dfa_object = {
        "alphabet": alphabet,
        "states": states,
    }

    return (True, dfa_object, "")


def load_input_strings(file_path):
    """
    Read a .in file and return its lines as a list of strings.

    Each line is stripped of the trailing newline but otherwise preserved.
    Blank lines result in empty strings in the output list.

    Args:
        file_path: Path to the .in file.

    Returns:
        A list of strings, one per line in the file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return lines


# ==============================================================================
# SECTION 2: DFA EVALUATOR
# ==============================================================================

def process_dfa(input_strings, states, alphabet):
    """
    Process all input strings using the given DFA.

    The DFA starts at the state marked with '-'.
    Each character causes a transition to another state.
    A string is VALID if it ends at a state marked with '+'.
    Otherwise, it is INVALID.

    Returns:
        A list of VALID/INVALID results corresponding
        to each input string.
    """

    # Find the DFA start state
    start_state = None

    for state, data in states.items():
        if data["type"] == "-":
            start_state = state
            break

    results = []

    # Process each input string
    for input_string in input_strings:

        current_state = start_state

        # If no start state exists, the string is invalid
        if current_state is None:
            results.append("INVALID")
            continue

        # Process the string character by character
        for symbol in input_string:

            # Reject the string if the symbol is not in the DFA alphabet
            if symbol not in alphabet:
                current_state = None
                break

            # Follow the DFA transition
            current_state = states[current_state]["transitions"][symbol]

        # Determine whether the final state is an accepting state
        if current_state is not None and states[current_state]["type"] == "+":
            results.append("VALID")
        else:
            results.append("INVALID")

    return results


def evaluate_strings(dfa_object, input_strings):
    """
    Evaluate a list of input strings against a DFA.

    This is the modular API wrapper around process_dfa(),
    adapting the call signature to the agreed interface.

    Args:
        dfa_object: Dict with "alphabet" and "states" keys (from parse_dfa).
        input_strings: List of strings to evaluate.

    Returns:
        A list of "VALID"/"INVALID" results corresponding to each input string.
    """
    return process_dfa(input_strings, dfa_object["states"], dfa_object["alphabet"])


# ==============================================================================
# SECTION 3: GUI & FILE I/O
# ==============================================================================

# ── Colour palette ─────────────────────────────────────────────────────────────
_BG          = "#1e1e2e"   # window background
_SURFACE     = "#2a2a3e"   # panel / frame background
_SURFACE2    = "#313145"   # slightly lighter surface (treeview rows)
_ACCENT      = "#7c6af7"   # primary accent (purple)
_ACCENT_HOV  = "#9b8dff"   # accent hover
_ACCENT_DIS  = "#4a4468"   # disabled accent
_TEXT        = "#cdd6f4"   # primary text
_TEXT_DIM    = "#888aaa"   # secondary / placeholder text
_GREEN       = "#a6e3a1"   # VALID highlight
_RED         = "#f38ba8"   # INVALID / error highlight
_BORDER      = "#414159"   # subtle border
_STATUS_BG   = "#252535"   # status bar background

_FONT_SANS   = ("Segoe UI", 10)
_FONT_SANS_B = ("Segoe UI", 10, "bold")
_FONT_MONO   = ("Consolas", 11)
_FONT_LABEL  = ("Segoe UI", 9, "bold")


def _configure_styles():
    """Apply a consistent dark theme to ttk widgets."""
    style = ttk.Style()
    style.theme_use("clam")

    # ── Treeview ───────────────────────────────────────────────────────────────
    style.configure(
        "DFA.Treeview",
        background=_SURFACE2,
        foreground=_TEXT,
        fieldbackground=_SURFACE2,
        rowheight=24,
        font=_FONT_MONO,
        bordercolor=_BORDER,
        relief="flat",
    )
    style.configure(
        "DFA.Treeview.Heading",
        background=_ACCENT,
        foreground="#ffffff",
        font=_FONT_SANS_B,
        relief="flat",
    )
    style.map(
        "DFA.Treeview",
        background=[("selected", _ACCENT)],
        foreground=[("selected", "#ffffff")],
    )
    style.map(
        "DFA.Treeview.Heading",
        background=[("active", _ACCENT_HOV)],
    )

    # ── Scrollbar ──────────────────────────────────────────────────────────────
    style.configure(
        "Dark.Vertical.TScrollbar",
        background=_SURFACE2,
        troughcolor=_SURFACE,
        arrowcolor=_TEXT_DIM,
        bordercolor=_BORDER,
        relief="flat",
    )
    style.configure(
        "Dark.Horizontal.TScrollbar",
        background=_SURFACE2,
        troughcolor=_SURFACE,
        arrowcolor=_TEXT_DIM,
        bordercolor=_BORDER,
        relief="flat",
    )


class DFAApp(tk.Tk):
    """
    Main GUI application for the DFA String Recognizer.

    Layout matches the specified UI mockup:
        - Top bar   : Load File and Process buttons.
        - Middle    : Transition Table (Treeview), Input (text), Output (text).
        - Bottom    : Status bar.
        * Build and style all widgets to match the suggested design.
        * File dialog to open .in / .dfa from any directory.
        * Render file contents into the correct display panels.
        * Write results array to the .out file (same directory as .in).
        * Manage UI state: enable Process only when both files are loaded.
        * Display exact status messages as specified in the lab sheet.
    """

    def __init__(self):
        super().__init__()
        self.title("PE01 \u2014 Strings and DFA  |  CMSC 129")
        self.geometry("1060x580")
        self.minsize(860, 480)
        self.configure(bg=_BG)

        # ── Application state ──────────────────────────────────────────────────
        self.dfa_object      = None   # Currently loaded valid DFA dict
        self.dfa_file_name   = None   # Basename of loaded .dfa file
        self.input_strings   = None   # List[str] from loaded .in file
        self.input_file_path = None   # Full path to loaded .in file
        self.input_file_name = None   # Basename of loaded .in file

        _configure_styles()
        self._build_ui()

    # ==========================================================================
    # UI CONSTRUCTION
    # ==========================================================================

    def _build_ui(self):
        """Construct, arrange, and style all UI widgets."""

        # ── Title strip ───────────────────────────────────────────────────────
        title_frame = tk.Frame(self, bg=_ACCENT, pady=6)
        title_frame.pack(fill=tk.X)
        tk.Label(
            title_frame,
            text="  PE01 \u2014 Strings and DFA Recognizer",
            bg=_ACCENT,
            fg="#ffffff",
            font=("Segoe UI", 12, "bold"),
            anchor=tk.W,
        ).pack(side=tk.LEFT, padx=8)

        # ── Top button bar ────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=_BG, padx=12, pady=10)
        btn_frame.pack(fill=tk.X)

        self.load_btn = self._make_button(
            btn_frame,
            text="\u2b06  Load File",
            command=self._on_load_file,
            normal_bg=_ACCENT,
            hover_bg=_ACCENT_HOV,
            disabled_bg=_ACCENT_DIS,
        )
        self.load_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.process_btn = self._make_button(
            btn_frame,
            text="\u25b6  Process",
            command=self._on_process,
            normal_bg="#3d9970",
            hover_bg="#52c799",
            disabled_bg="#2a4a3a",
            state=tk.DISABLED,
        )
        self.process_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        # ── Content area  (three side-by-side panels) ─────────────────────────
        content = tk.Frame(self, bg=_BG, padx=12)
        content.pack(fill=tk.BOTH, expand=True)

        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=3)
        content.columnconfigure(2, weight=2)
        content.rowconfigure(0, weight=1)

        # ── Panel 0 : Transition Table ─────────────────────────────────────────
        tbl_panel = self._make_panel(content, "Transition Table")
        tbl_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 4))

        tbl_inner = tk.Frame(tbl_panel, bg=_SURFACE)
        tbl_inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self.table_tree = ttk.Treeview(
            tbl_inner,
            style="DFA.Treeview",
            show="headings",
            selectmode="none",
        )
        tbl_vscroll = ttk.Scrollbar(
            tbl_inner,
            orient=tk.VERTICAL,
            command=self.table_tree.yview,
            style="Dark.Vertical.TScrollbar",
        )
        tbl_hscroll = ttk.Scrollbar(
            tbl_inner,
            orient=tk.HORIZONTAL,
            command=self.table_tree.xview,
            style="Dark.Horizontal.TScrollbar",
        )
        self.table_tree.configure(
            yscrollcommand=tbl_vscroll.set,
            xscrollcommand=tbl_hscroll.set,
        )
        tbl_vscroll.pack(side=tk.RIGHT,  fill=tk.Y)
        tbl_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.table_tree.pack(fill=tk.BOTH, expand=True)

        # ── Panel 1 : Input ────────────────────────────────────────────────────
        inp_panel = self._make_panel(content, "Input")
        inp_panel.grid(row=0, column=1, sticky="nsew", padx=6, pady=(0, 4))

        inp_inner = tk.Frame(inp_panel, bg=_SURFACE)
        inp_inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self.input_text = self._make_textbox(inp_inner)
        inp_vscroll = ttk.Scrollbar(
            inp_inner, orient=tk.VERTICAL,
            command=self.input_text.yview,
            style="Dark.Vertical.TScrollbar",
        )
        self.input_text.configure(yscrollcommand=inp_vscroll.set)
        inp_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # ── Panel 2 : Output ───────────────────────────────────────────────────
        out_panel = self._make_panel(content, "Output")
        out_panel.grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=(0, 4))

        out_inner = tk.Frame(out_panel, bg=_SURFACE)
        out_inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self.output_text = self._make_textbox(out_inner)
        # Colour tags for VALID / INVALID
        self.output_text.tag_configure("valid",   foreground=_GREEN, font=("Consolas", 11, "bold"))
        self.output_text.tag_configure("invalid", foreground=_RED,   font=("Consolas", 11, "bold"))
        out_vscroll = ttk.Scrollbar(
            out_inner, orient=tk.VERTICAL,
            command=self.output_text.yview,
            style="Dark.Vertical.TScrollbar",
        )
        self.output_text.configure(yscrollcommand=out_vscroll.set)
        out_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # ── Status bar ─────────────────────────────────────────────────────────
        # Thin separator line
        tk.Frame(self, bg=_BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)

        status_frame = tk.Frame(self, bg=_STATUS_BG, padx=12, pady=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(
            value="STATUS: Ready. Load a .dfa and .in file to begin."
        )
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=_STATUS_BG,
            fg=_TEXT_DIM,
            anchor=tk.W,
            pady=5,
            wraplength=1000,
            justify=tk.LEFT,
        )
        self.status_label.pack(fill=tk.X)

    # ── Widget factory helpers ─────────────────────────────────────────────────

    def _make_panel(self, parent, title):
        """Return a styled LabelFrame used as a content panel."""
        return tk.LabelFrame(
            parent,
            text=f"  {title}  ",
            font=_FONT_LABEL,
            bg=_SURFACE,
            fg=_TEXT,
            bd=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground=_BORDER,
            labelanchor="n",
            pady=4,
        )

    def _make_button(self, parent, text, command, normal_bg, hover_bg,
                     disabled_bg, state=tk.NORMAL):
        """Return a styled, hover-animated tk.Button."""
        btn = tk.Button(
            parent,
            text=text,
            font=_FONT_SANS_B,
            bg=normal_bg if state == tk.NORMAL else disabled_bg,
            fg="#ffffff",
            activebackground=hover_bg,
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2" if state == tk.NORMAL else "arrow",
            bd=0,
            padx=18,
            pady=10,
            command=command,
            state=state,
            disabledforeground="#7a7a9a",
        )
        # Store colour info on the button for hover bindings
        btn._normal_bg   = normal_bg
        btn._hover_bg    = hover_bg
        btn._disabled_bg = disabled_bg

        btn.bind("<Enter>", lambda e, b=btn: self._btn_enter(b))
        btn.bind("<Leave>", lambda e, b=btn: self._btn_leave(b))
        return btn

    @staticmethod
    def _btn_enter(btn):
        if str(btn["state"]) != tk.DISABLED:
            btn.config(bg=btn._hover_bg)

    @staticmethod
    def _btn_leave(btn):
        if str(btn["state"]) != tk.DISABLED:
            btn.config(bg=btn._normal_bg)
        else:
            btn.config(bg=btn._disabled_bg)

    def _make_textbox(self, parent):
        """Return a styled, read-only tk.Text widget."""
        return tk.Text(
            parent,
            font=_FONT_MONO,
            bg=_SURFACE2,
            fg=_TEXT,
            insertbackground=_TEXT,
            selectbackground=_ACCENT,
            selectforeground="#ffffff",
            relief="flat",
            bd=0,
            wrap=tk.NONE,
            state=tk.DISABLED,
            padx=6,
            pady=4,
        )

    # ==========================================================================
    # LOAD FILE HANDLER
    # ==========================================================================

    def _on_load_file(self):
        """
        Open a file dialog accepting .in and .dfa files.
        Dispatch to the correct loader based on the file extension.
        """
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("DFA and Input Files", "*.dfa *.in"),
                ("DFA Transition Table", "*.dfa"),
                ("Input Strings File",   "*.in"),
                ("All Files",            "*.*"),
            ],
        )

        if not file_path:
            return  # User cancelled — do nothing

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".dfa":
            self._load_dfa_file(file_path)
        elif ext == ".in":
            self._load_input_file(file_path)
        else:
            self._set_status(
                f"Unable to load \"{os.path.basename(file_path)}\": "
                f"unsupported file type '{ext}'. Only .dfa and .in files are accepted.",
                error=True,
            )

        self._update_process_button()

    def _load_dfa_file(self, file_path):
        """
        Load and validate a .dfa file.
        On failure keep the previous valid DFA and report the appropriate
        status message as specified in the lab sheet.
        """
        basename = os.path.basename(file_path)
        is_valid, dfa_obj, error_msg = parse_dfa(file_path)

        if is_valid:
            self.dfa_object    = dfa_obj
            self.dfa_file_name = basename
            self._render_transition_table()
            self._set_status(
                f"DFA table from {basename} has been successfully loaded."
            )
        else:
            # Spec: invalid DFA must NOT overwrite the previously loaded table
            if self.dfa_object is not None:
                # Spec message variant 2: previous valid DFA still in use
                self._set_status(
                    f"Unable to load content from {basename} due to invalid content. "
                    f"The program will be using the content from the most recently "
                    f"successfully loaded {self.dfa_file_name}.",
                    error=True,
                )
            else:
                # Spec message variant 1: no valid DFA exists yet
                self._set_status(
                    f"Unable to load content from {basename} due to invalid content.",
                    error=True,
                )

    def _load_input_file(self, file_path):
        """Load a .in file; render its contents into the Input panel."""
        basename = os.path.basename(file_path)

        try:
            strings = load_input_strings(file_path)
        except Exception as exc:
            self._set_status(f"Unable to load {basename}: {exc}", error=True)
            return

        self.input_strings   = strings
        self.input_file_path = file_path
        self.input_file_name = basename

        # Render into Input text area (overwrites whatever was there)
        self._write_textbox(self.input_text, "\n".join(strings))

        # Clear any stale output when new input is loaded
        self._write_textbox(self.output_text, "")

        self._set_status(
            f"Input from file {basename} has been successfully loaded."
        )

    # ==========================================================================
    # TRANSITION TABLE RENDERING
    # ==========================================================================

    def _render_transition_table(self):
        """Populate the Treeview with the current DFA's transition table."""
        tree = self.table_tree

        # Wipe previous content
        tree.delete(*tree.get_children())
        tree["columns"] = ()

        if self.dfa_object is None:
            return

        alphabet = self.dfa_object["alphabet"]
        states   = self.dfa_object["states"]

        # Columns: blank type marker | State label | sym0 | sym1
        col_type  = "type"
        col_state = "state"
        col_s0    = alphabet[0]
        col_s1    = alphabet[1]
        columns   = (col_type, col_state, col_s0, col_s1)

        tree["columns"] = columns

        tree.heading(col_type,  text="")
        tree.heading(col_state, text="State")
        tree.heading(col_s0,    text=col_s0)
        tree.heading(col_s1,    text=col_s1)

        tree.column(col_type,  width=32,  minwidth=28,  anchor=tk.CENTER, stretch=False)
        tree.column(col_state, width=70,  minwidth=50,  anchor=tk.CENTER, stretch=True)
        tree.column(col_s0,    width=70,  minwidth=50,  anchor=tk.CENTER, stretch=True)
        tree.column(col_s1,    width=70,  minwidth=50,  anchor=tk.CENTER, stretch=True)

        # Alternating row colours and type-based text colours
        tree.tag_configure("odd",   background=_SURFACE2)
        tree.tag_configure("even",  background="#38384f")
        tree.tag_configure("start", foreground="#ffd700")   # gold  — start state (-)
        tree.tag_configure("final", foreground=_GREEN)       # green — final state (+)

        for idx, (label, data) in enumerate(states.items()):
            row_tag   = "odd" if idx % 2 == 0 else "even"
            extra_tag = []
            if data["type"] == "-":
                extra_tag.append("start")
            elif data["type"] == "+":
                extra_tag.append("final")

            tree.insert(
                "",
                tk.END,
                values=(
                    data["type"],
                    label,
                    data["transitions"][alphabet[0]],
                    data["transitions"][alphabet[1]],
                ),
                tags=(row_tag, *extra_tag),
            )

    # ==========================================================================
    # PROCESS HANDLER
    # ==========================================================================

    def _on_process(self):
        """
        Evaluate loaded input strings against the loaded DFA,
        display colour-coded results, and write the .out file.
        """
        if self.dfa_object is None or self.input_strings is None:
            return

        # Call evaluator via the agreed modular API
        results = evaluate_strings(self.dfa_object, self.input_strings)

        # Render results into Output panel with colour coding
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        for i, result in enumerate(results):
            tag = "valid" if result == "VALID" else "invalid"
            self.output_text.insert(tk.END, result, tag)
            if i < len(results) - 1:
                self.output_text.insert(tk.END, "\n")
        self.output_text.config(state=tk.DISABLED)

        # Write .out file — same directory and stem as the .in file
        out_path = os.path.splitext(self.input_file_path)[0] + ".out"
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(results) + "\n")
        except Exception as exc:
            self._set_status(f"Error writing output file: {exc}", error=True)
            return

        out_basename = os.path.basename(out_path)
        # Spec-mandated status message for successful processing
        self._set_status(
            f"Input from {self.input_file_name} successfully processed using "
            f"DFA table from {self.dfa_file_name}. "
            f"Output saved to {out_basename}."
        )

    # ==========================================================================
    # UI HELPER METHODS
    # ==========================================================================

    def _update_process_button(self):
        """Enable Process only when a valid DFA and input strings are both loaded."""
        ready = (self.dfa_object is not None) and (self.input_strings is not None)
        if ready:
            self.process_btn.config(
                state=tk.NORMAL,
                bg=self.process_btn._normal_bg,
                cursor="hand2",
            )
        else:
            self.process_btn.config(
                state=tk.DISABLED,
                bg=self.process_btn._disabled_bg,
                cursor="arrow",
            )

    def _set_status(self, message, error=False):
        """
        Update the status bar text.
        Error messages are shown in red; normal messages in the dim text colour.
        """
        self.status_var.set(f"STATUS: {message}")
        self.status_label.config(fg=_RED if error else _TEXT_DIM)

    @staticmethod
    def _write_textbox(widget, content):
        """Helper: enable, clear, write, and re-disable a read-only Text widget."""
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        if content:
            widget.insert(tk.END, content)
        widget.config(state=tk.DISABLED)


# ==============================================================================
# SECTION 4: MAIN ENTRY POINT
# ==============================================================================

def main():
    """Start the DFA String Recognizer GUI application."""
    app = DFAApp()
    app.mainloop()


if __name__ == "__main__":
    main()