"""
Programming Exercise 01: Strings and DFA
Course: CMSC 129

This program recognizes strings based on a given deterministic finite automaton (DFA).
It provides a graphical user interface for loading .in (input strings) and .dfa
(transition table) files, processing strings against the DFA, and saving results.

Module Breakdown:
    1. DFA Parser & Validator (Cedric)  — parse_dfa(), load_input_strings()
    2. DFA Evaluator (Jeycel)           — process_dfa(), evaluate_strings()
    3. GUI & File I/O (Dave)            — DFAApp class
"""

import os
import csv
import io
import tkinter as tk
from tkinter import filedialog, ttk


# ==============================================================================
# SECTION 1: DFA PARSER & VALIDATOR (Cedric)
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
# SECTION 2: DFA EVALUATOR (Jeycel)
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

    This is the modular API wrapper around Jeycel's process_dfa(),
    adapting the call signature to the agreed interface.

    Args:
        dfa_object: Dict with "alphabet" and "states" keys (from parse_dfa).
        input_strings: List of strings to evaluate.

    Returns:
        A list of "VALID"/"INVALID" results corresponding to each input string.
    """
    return process_dfa(input_strings, dfa_object["states"], dfa_object["alphabet"])


# ==============================================================================
# SECTION 3: GUI & FILE I/O (Dave)
# ==============================================================================

class DFAApp(tk.Tk):
    """
    Main GUI application for the DFA String Recognizer.

    Layout matches the specified UI mockup:
        - Top bar: Load File and Process buttons.
        - Middle: Transition Table (Treeview), Input (text area), Output (text area).
        - Bottom: Status bar.
    """

    def __init__(self):
        super().__init__()
        self.title("PE01 — Strings and DFA")
        self.geometry("960x540")
        self.minsize(800, 450)

        # Application state
        self.dfa_object = None           # Currently loaded valid DFA
        self.dfa_file_name = None        # Basename of loaded .dfa file
        self.input_strings = None        # Currently loaded input strings
        self.input_file_path = None      # Full path to loaded .in file
        self.input_file_name = None      # Basename of loaded .in file

        self._build_ui()

    def _build_ui(self):
        """Construct all UI widgets."""

        # ---- Top button bar ----
        button_frame = tk.Frame(self, padx=10, pady=8)
        button_frame.pack(fill=tk.X)

        self.load_button = tk.Button(
            button_frame,
            text="Load File",
            font=("Arial", 10, "bold"),
            command=self._on_load_file,
            height=2,
            cursor="hand2",
        )
        self.load_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.process_button = tk.Button(
            button_frame,
            text="Process",
            font=("Arial", 10, "bold"),
            command=self._on_process,
            height=2,
            cursor="hand2",
            state=tk.DISABLED,
        )
        self.process_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        # ---- Middle content area (three columns) ----
        content_frame = tk.Frame(self, padx=10)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Column 0: Transition Table
        table_frame = tk.LabelFrame(
            content_frame, text="Transition Table", font=("Arial", 10, "bold")
        )
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=4)

        self.table_tree = ttk.Treeview(table_frame, show="headings", height=12)
        self.table_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Column 1: Input
        input_frame = tk.LabelFrame(
            content_frame, text="Input", font=("Arial", 10, "bold")
        )
        input_frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        self.input_text = tk.Text(
            input_frame, wrap=tk.NONE, font=("Courier New", 11), state=tk.DISABLED
        )
        input_scroll = tk.Scrollbar(input_frame, command=self.input_text.yview)
        self.input_text.config(yscrollcommand=input_scroll.set)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Column 2: Output
        output_frame = tk.LabelFrame(
            content_frame, text="Output", font=("Arial", 10, "bold")
        )
        output_frame.grid(row=0, column=2, sticky="nsew", padx=(4, 0), pady=4)

        self.output_text = tk.Text(
            output_frame, wrap=tk.NONE, font=("Courier New", 11), state=tk.DISABLED
        )
        output_scroll = tk.Scrollbar(output_frame, command=self.output_text.yview)
        self.output_text.config(yscrollcommand=output_scroll.set)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Configure column weights for proportional resizing
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=2)
        content_frame.columnconfigure(2, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # ---- Bottom status bar ----
        status_frame = tk.Frame(self, padx=10, pady=6)
        status_frame.pack(fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text="STATUS: Ready. Load a .dfa and .in file to begin.",
            font=("Arial", 10),
            anchor=tk.W,
            relief=tk.SUNKEN,
            padx=6,
            pady=4,
        )
        self.status_label.pack(fill=tk.X)

    # ------------------------------------------------------------------
    # Load File handler
    # ------------------------------------------------------------------

    def _on_load_file(self):
        """
        Open a file dialog for .in and .dfa files.
        Dispatch to the appropriate loader based on the file extension.
        """
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("DFA and Input Files", "*.dfa *.in"),
                ("DFA Files", "*.dfa"),
                ("Input Files", "*.in"),
                ("All Files", "*.*"),
            ],
        )

        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".dfa":
            self._load_dfa_file(file_path)
        elif ext == ".in":
            self._load_input_file(file_path)
        else:
            self._set_status(
                f"Unable to load {os.path.basename(file_path)}: "
                f"unsupported file type '{ext}'. Use .dfa or .in files."
            )

        self._update_process_button()

    def _load_dfa_file(self, file_path):
        """Load and validate a .dfa file. On failure, retain the previous valid DFA."""
        basename = os.path.basename(file_path)
        is_valid, dfa_obj, error_msg = parse_dfa(file_path)

        if is_valid:
            self.dfa_object = dfa_obj
            self.dfa_file_name = basename
            self._render_transition_table()
            self._set_status(
                f"DFA table from {basename} has been successfully loaded."
            )
        else:
            # Invalid DFA — do NOT overwrite the previously loaded valid table
            if self.dfa_object is not None:
                self._set_status(
                    f"Unable to load content from {basename} due to invalid content. "
                    f"The program will be using the content from the most recently "
                    f"successfully loaded {self.dfa_file_name}."
                )
            else:
                self._set_status(
                    f"Unable to load content from {basename} due to invalid content."
                )

    def _load_input_file(self, file_path):
        """Load a .in file into the input display."""
        basename = os.path.basename(file_path)

        try:
            strings = load_input_strings(file_path)
        except Exception as e:
            self._set_status(f"Unable to load {basename}: {e}")
            return

        self.input_strings = strings
        self.input_file_path = file_path
        self.input_file_name = basename

        # Render into the input text area
        self.input_text.config(state=tk.NORMAL)
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, "\n".join(strings))
        self.input_text.config(state=tk.DISABLED)

        # Clear previous output when new input is loaded
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

        self._set_status(
            f"Input from file {basename} has been successfully loaded."
        )

    # ------------------------------------------------------------------
    # Transition Table rendering
    # ------------------------------------------------------------------

    def _render_transition_table(self):
        """Populate the Treeview with the current DFA's transition table."""
        tree = self.table_tree

        # Clear existing content
        tree.delete(*tree.get_children())
        tree["columns"] = ()

        if self.dfa_object is None:
            return

        alphabet = self.dfa_object["alphabet"]
        states = self.dfa_object["states"]

        # Define columns: Type | State | Symbol1 | Symbol2
        columns = ("type", "state", alphabet[0], alphabet[1])
        tree["columns"] = columns

        tree.heading("type", text="")
        tree.heading("state", text="State")
        tree.heading(alphabet[0], text=alphabet[0])
        tree.heading(alphabet[1], text=alphabet[1])

        tree.column("type", width=30, anchor=tk.CENTER, stretch=False)
        tree.column("state", width=60, anchor=tk.CENTER)
        tree.column(alphabet[0], width=60, anchor=tk.CENTER)
        tree.column(alphabet[1], width=60, anchor=tk.CENTER)

        # Insert rows in the original insertion order (dict preserves order in Python 3.7+)
        for label, data in states.items():
            tree.insert(
                "",
                tk.END,
                values=(
                    data["type"],
                    label,
                    data["transitions"][alphabet[0]],
                    data["transitions"][alphabet[1]],
                ),
            )

    # ------------------------------------------------------------------
    # Process handler
    # ------------------------------------------------------------------

    def _on_process(self):
        """
        Evaluate the loaded input strings against the loaded DFA.
        Display results in the output area and write the .out file.
        """
        if self.dfa_object is None or self.input_strings is None:
            return

        results = evaluate_strings(self.dfa_object, self.input_strings)

        # Display results in the output text area
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n".join(results))
        self.output_text.config(state=tk.DISABLED)

        # Write the .out file (same name and path as the .in file)
        out_path = os.path.splitext(self.input_file_path)[0] + ".out"
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                for result in results:
                    f.write(result + "\n")
        except Exception as e:
            self._set_status(f"Error writing output file: {e}")
            return

        out_basename = os.path.basename(out_path)
        self._set_status(
            f"Input from {self.input_file_name} successfully processed using "
            f"DFA table from {self.dfa_file_name}. Output saved to {out_basename}."
        )

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _update_process_button(self):
        """Enable the Process button only when both a valid DFA and input are loaded."""
        if self.dfa_object is not None and self.input_strings is not None:
            self.process_button.config(state=tk.NORMAL)
        else:
            self.process_button.config(state=tk.DISABLED)

    def _set_status(self, message):
        """Update the status bar text."""
        self.status_label.config(text=f"STATUS: {message}")


# ==============================================================================
# SECTION 4: MAIN ENTRY POINT
# ==============================================================================

def main():
    """Start the DFA String Recognizer GUI application."""
    app = DFAApp()
    app.mainloop()


if __name__ == "__main__":
    main()