# Expression Evaluation

**CMSC 129 — Programming Exercise 00**

A Python-based expression evaluator with a Tkinter GUI that processes mathematical expressions and assignment statements line-by-line. It tokenizes input, converts infix notation to postfix using the Shunting-yard algorithm, evaluates the result, and reports errors — all displayed through a split-pane graphical interface.

## Features

- **Tokenizer (Lexer)** — Scans input into tokens: numbers (integers & decimals), variables (C-style names without underscores), operators (`+`, `-`, `*`, `/`, `%`), and parentheses.
- **Infix-to-Postfix Conversion** — Implements the Shunting-yard algorithm with correct operator precedence, associativity, and unary minus/plus handling.
- **Postfix Evaluator** — Evaluates postfix expressions using a stack, resolving variables from a symbol table.
- **Variable Assignment** — Supports statements like `x = 3 + 4 * 2`, storing results in an `OrderedDict` for ordered tracking.
- **Error Handling** — Detects and reports:
  - `Invalid input code` — malformed expressions, illegal characters, bad variable names
  - `Undefined variable` — using a variable before it has been assigned
  - `Division by zero` — division or modulo by zero
- **Tkinter GUI** — Split-pane interface with editable input, read-only output, a **Load File** button (`.in` files), and a **Process** button.

## Getting Started

### Prerequisites

- Python 3.x ([download here](https://www.python.org/downloads/))
- Git

### 1. Clone the Repository

```bash
git clone git@github.com:BelfixxxCed/Expression-Evaluation.git
cd Expression-Evaluation
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> If PowerShell blocks the activation script, run this once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Once activated, your terminal prompt will be prefixed with `(venv)`.

### 3. Run the Program

**From source:**
```bash
python lab1.py
```

**Or use the standalone executable (no Python required):**
```
dist\lab1.exe
```

This launches the GUI window. You can either type expressions directly into the input pane or click **Load File** to open a `.in` file.

### Deactivating the Environment

```bash
deactivate
```

## Usage

### Sample Input (`sample.in`)

```
x = 3 + 4 * 2
y = x - 1
z = y % 0
w = undefinedVar + 1
10 / (5 - 5)
5 +
a1 = 7
b = a1 * (2 + 3) - -2
```

### Expected Output

```
Line: x = 3 + 4 * 2
Postfix: 3 4 2 * +
Result: x = 11

Line: y = x - 1
Postfix: x 1 -
Result: y = 10

Line: z = y % 0
Postfix: y 0 %
Result: z = Error: Division by zero

Line: w = undefinedVar + 1
Postfix: undefinedVar 1 +
Result: w = Error: Undefined variable undefinedVar

Line: 10 / (5 - 5)
Postfix: 10 5 5 - /
Result: Error: Division by zero

Line: 5 +
Postfix: N/A
Result: Error: Invalid input code

Line: a1 = 7
Postfix: 7
Result: a1 = 7

Line: b = a1 * (2 + 3) - -2
Postfix: a1 2 3 + * 2 u- -
Result: b = 37

-------------------------------------------
Variables used:
x = 11
y = 10
a1 = 7
b = 37
-------------------------------------------
Errors found:
Division by zero
Undefined variable undefinedVar
Division by zero
Invalid input code
```

## Project Structure

```
Expression-Evaluation/
├── lab1.py            # Main source — tokenizer, parser, evaluator, and GUI
├── lab1.spec          # PyInstaller build specification
├── sample.in          # Sample input file for testing
├── dist/              # Contains the standalone executable (lab1.exe)
├── build/             # PyInstaller build cache (not committed)
├── .gitignore         # Excludes venv/ from version control
├── venv/              # Python virtual environment (not committed)
└── README.md
```

## How It Works

1. **Input** — The user types or loads expressions into the input pane.
2. **Tokenization** — Each line is scanned into tokens (numbers, variables, operators, parentheses).
3. **Parsing** — Tokens are converted from infix to postfix notation via the Shunting-yard algorithm. Unary `+`/`-` are handled contextually.
4. **Evaluation** — The postfix token list is evaluated using a stack. Variables are resolved from the symbol table; assignments update it.
5. **Output** — For each line, the original input, postfix form, and result (or error) are displayed. A summary of all variables and errors follows.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add some feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request
