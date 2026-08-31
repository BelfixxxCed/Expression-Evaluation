import tkinter as tk
from tkinter import filedialog, messagebox
import processor

class ExpressionEvaluatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expression Evaluation")
        
        # Configure grid for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # --- UI Elements ---
        
        # Input Text Area with a subtle border
        self.input_frame = tk.Frame(self.root, bd=2, relief="groove")
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.input_frame.grid_rowconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_text = tk.Text(self.input_frame, font=("Consolas", 11), wrap="none")
        self.input_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Output Text Area with a subtle border
        self.output_frame = tk.Frame(self.root, bd=2, relief="groove")
        self.output_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=(10, 5))
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_text = tk.Text(self.output_frame, font=("Consolas", 11), wrap="none")
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.output_text.config(state=tk.DISABLED) # Make it read-only
        
        # Load File Button
        self.load_btn = tk.Button(self.root, text="Load File", command=self.load_file, font=("Segoe UI", 10, "bold"), bd=2)
        self.load_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        # Process Button
        self.process_btn = tk.Button(self.root, text="Process", command=self.process_input, font=("Segoe UI", 10, "bold"), bd=2)
        self.process_btn.grid(row=1, column=1, sticky="ew", padx=10, pady=(5, 10))

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Open Input File",
            filetypes=[("IN Files", "*.in"), ("All Files", "*.*")]
        )
        if not filepath:
            return
            
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
                
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")

    def process_input(self):
        content = self.input_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Input area is empty. Please enter some code or load a file.")
            return
            
        lines = content.split('\n')
        
        # Call processing module
        try:
            result = processor.process_code(lines)
            
            # Display output
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Processing Error", f"An error occurred during processing:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpressionEvaluatorApp(root)
    root.geometry("800x600")
    root.mainloop()
