"""
Programming Exercise 00: Expression Evaluation
Course: CMSC 129

This program implements an expression evaluator with a graphical user interface (UI).
It evaluates mathematical expressions and assignment statements line-by-line:
1. Tokenizes expressions (supporting C-style variable names without underscores,
   integers/decimals, operators +, -, *, /, %, and parentheses).
2. Converts infix expressions to postfix notation using the Shunting-yard algorithm.
3. Evaluates postfix expressions using a stack while tracking variable assignments.
4. Identifies and reports errors (Invalid input code, Undefined variable, Division by zero).
5. Displays results, variables used with their final values, and all errors encountered.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from collections import OrderedDict


# ==============================================================================
# CUSTOM EXCEPTIONS FOR SPECIFIED ERROR TYPES
# ==============================================================================

class InvalidCodeException(Exception):
    """Raised when an input statement or expression is syntactically or lexically invalid."""
    pass


class UndefinedVariableException(Exception):
    """Raised when a variable is evaluated before being assigned any value."""
    def __init__(self, variable_name: str):
        self.variable_name = variable_name
        super().__init__(f"Undefined variable {variable_name}")


class DivisionByZeroException(Exception):
    """Raised when a division or modulo by zero is attempted."""
    def __init__(self):
        super().__init__("Division by zero")


# ==============================================================================
# TOKEN DEFINITIONS AND TOKENIZER
# ==============================================================================

class TokenType:
    NUMBER = "NUMBER"
    VARIABLE = "VARIABLE"
    OPERATOR = "OPERATOR"
    UNARY_MINUS = "UNARY_MINUS"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"


class Token:
    """Represents a lexical token with a type and text value."""
    __slots__ = ("type", "text")

    def __init__(self, token_type: str, text: str):
        self.type = token_type
        self.text = text

    def display_text(self) -> str:
        """Returns the text representation for display in postfix notation."""
        if self.type == TokenType.UNARY_MINUS:
            return "u-"
        return self.text

    def __repr__(self):
        return f"Token({self.type}, {self.text!r})"


def is_valid_variable_name(name: str) -> bool:
    """
    Validates variable names according to C language rules:
    - Excludes the underscore symbol.
    - Excludes the restriction on keywords (keywords are permitted as variable names).
    Therefore, the name must start with an alphabetic letter and contain only letters and digits.
    """
    if not name:
        return False
    if not name[0].isalpha():
        return False
    return name.isalnum()


def get_tokens(expression: str) -> list:
    """
    Scans and tokenizes an infix expression into a list of Token objects.
    Enforces lexical rules and checks for illegal characters.
    """
    tokens = []
    i = 0
    n = len(expression)

    while i < n:
        char = expression[i]

        # Ignore whitespace
        if char.isspace():
            i += 1
            continue

        # Opening parenthesis
        if char == "(":
            tokens.append(Token(TokenType.LPAREN, "("))
            i += 1
            continue

        # Closing parenthesis
        if char == ")":
            tokens.append(Token(TokenType.RPAREN, ")"))
            i += 1
            continue

        # Binary / arithmetic operators
        if char in "+-*/%":
            tokens.append(Token(TokenType.OPERATOR, char))
            i += 1
            continue

        # Numeric literal (integer or floating point)
        if char.isdigit() or char == ".":
            start = i
            saw_dot = False
            saw_digit = False

            while i < n and (expression[i].isdigit() or expression[i] == "."):
                if expression[i] == ".":
                    if saw_dot:
                        raise InvalidCodeException(f"Invalid decimal literal: {expression[start:i + 1]}")
                    saw_dot = True
                else:
                    saw_digit = True
                i += 1

            if not saw_digit:
                raise InvalidCodeException(f"Malformed number literal: {expression[start:i]}")

            # If letters immediately follow digits without an operator, it's invalid
            if i < n and expression[i].isalpha():
                raise InvalidCodeException(f"Invalid token: {expression[start:i + 1]}")

            tokens.append(Token(TokenType.NUMBER, expression[start:i]))
            continue

        # Variable identifier
        if char.isalpha():
            start = i
            i += 1
            while i < n and expression[i].isalnum():
                i += 1

            # Underscores are explicitly prohibited by specification
            if i < n and expression[i] == "_":
                raise InvalidCodeException("Underscore not allowed in variable name")

            var_name = expression[start:i]
            tokens.append(Token(TokenType.VARIABLE, var_name))
            continue

        # Any other character is rejected as invalid input code
        raise InvalidCodeException(f"Invalid character: {char}")

    return tokens


# ==============================================================================
# INFIX TO POSTFIX CONVERTER (SHUNTING-YARD ALGORITHM)
# ==============================================================================

def get_precedence(token: Token) -> int:
    """Returns the operator precedence for a given token."""
    if token.type == TokenType.UNARY_MINUS:
        return 4
    if token.text in ("*", "/", "%"):
        return 3
    if token.text in ("+", "-"):
        return 2
    return -1


def is_left_associative(token: Token) -> bool:
    """Returns whether the operator token is left-associative."""
    # Unary minus is right-associative; binary operators are left-associative
    return token.type != TokenType.UNARY_MINUS


def infix_to_postfix(tokens: list) -> list:
    """
    Converts a list of infix tokens to postfix notation using Shunting-yard.
    Properly differentiates between binary minus and unary minus.
    """
    output = []
    operator_stack = []

    # True when an operand (number, variable, or unary sign) is expected next
    expect_operand = True

    for token in tokens:
        if token.type in (TokenType.NUMBER, TokenType.VARIABLE):
            if not expect_operand:
                raise InvalidCodeException(f"Unexpected operand: {token.text}")
            output.append(token)
            expect_operand = False

        elif token.type == TokenType.LPAREN:
            if not expect_operand:
                raise InvalidCodeException("Unexpected '('")
            operator_stack.append(token)
            expect_operand = True

        elif token.type == TokenType.RPAREN:
            if expect_operand:
                raise InvalidCodeException("Unexpected ')'")

            found_matching_lparen = False
            while operator_stack:
                top = operator_stack.pop()
                if top.type == TokenType.LPAREN:
                    found_matching_lparen = True
                    break
                output.append(top)

            if not found_matching_lparen:
                raise InvalidCodeException("Mismatched parentheses")

            expect_operand = False

        elif token.type == TokenType.OPERATOR:
            if expect_operand:
                # Sign appearing where operand is expected -> unary operator
                if token.text == "-":
                    operator_stack.append(Token(TokenType.UNARY_MINUS, "-"))
                    expect_operand = True
                    continue
                elif token.text == "+":
                    # Unary plus: no-op, just keep expecting an operand
                    expect_operand = True
                    continue
                else:
                    raise InvalidCodeException(f"Unexpected operator '{token.text}'")

            # Binary operator precedence comparison
            while (
                operator_stack
                and operator_stack[-1].type != TokenType.LPAREN
                and (
                    get_precedence(operator_stack[-1]) > get_precedence(token)
                    or (
                        get_precedence(operator_stack[-1]) == get_precedence(token)
                        and is_left_associative(token)
                    )
                )
            ):
                output.append(operator_stack.pop())

            operator_stack.append(token)
            expect_operand = True

        else:
            raise InvalidCodeException(f"Unrecognized token: {token.text}")

    # Expression cannot end expecting an operand (e.g. "5 +")
    if expect_operand:
        raise InvalidCodeException("Expression ends unexpectedly")

    # Empty all remaining operators to the output
    while operator_stack:
        top = operator_stack.pop()
        if top.type in (TokenType.LPAREN, TokenType.RPAREN):
            raise InvalidCodeException("Mismatched parentheses")
        output.append(top)

    if not output:
        raise InvalidCodeException("Empty expression")

    return output


def postfix_to_string(postfix_tokens: list) -> str:
    """Formats a list of postfix tokens into a space-separated string."""
    return " ".join(tok.display_text() for tok in postfix_tokens)


# ==============================================================================
# POSTFIX EVALUATOR
# ==============================================================================

def format_number(value: float) -> str:
    """Formats a numeric value: whole numbers are displayed without trailing decimal point."""
    if value != value or value in (float("inf"), float("-inf")):
        return str(value)
    if value == int(value):
        return str(int(value))
    return str(value)


def evaluate_postfix(postfix_tokens: list, variables: dict) -> float:
    """
    Evaluates a postfix token list using an evaluation stack and the current variables map.
    Raises UndefinedVariableException, DivisionByZeroException, or InvalidCodeException.
    """
    eval_stack = []

    for token in postfix_tokens:
        if token.type == TokenType.NUMBER:
            eval_stack.append(float(token.text))

        elif token.type == TokenType.VARIABLE:
            var_name = token.text
            if var_name not in variables:
                raise UndefinedVariableException(var_name)
            eval_stack.append(variables[var_name])

        elif token.type == TokenType.UNARY_MINUS:
            if not eval_stack:
                raise InvalidCodeException("Malformed unary minus expression")
            operand = eval_stack.pop()
            eval_stack.append(-operand)

        elif token.type == TokenType.OPERATOR:
            if len(eval_stack) < 2:
                raise InvalidCodeException("Malformed operator expression")
            right = eval_stack.pop()
            left = eval_stack.pop()

            if token.text == "+":
                eval_stack.append(left + right)
            elif token.text == "-":
                eval_stack.append(left - right)
            elif token.text == "*":
                eval_stack.append(left * right)
            elif token.text == "/":
                if right == 0:
                    raise DivisionByZeroException()
                eval_stack.append(left / right)
            elif token.text == "%":
                if right == 0:
                    raise DivisionByZeroException()
                eval_stack.append(left % right)
            else:
                raise InvalidCodeException(f"Unknown operator: {token.text}")

        else:
            raise InvalidCodeException(f"Unexpected token in evaluation: {token.text}")

    if len(eval_stack) != 1:
        raise InvalidCodeException("Invalid expression structure")

    return eval_stack.pop()


# ==============================================================================
# INPUT PROCESSING AND OUTPUT BUILDER
# ==============================================================================

class LineRecord:
    """Holds information for each processed line of input."""
    def __init__(self, original_line: str, postfix_str: str, result_str: str):
        self.original_line = original_line
        self.postfix_str = postfix_str
        self.result_str = result_str


class ExpressionEngine:
    """
    Orchestrates the processing of the entire input text, maintains the variable symbol table,
    and formats the final output according to the program specifications.
    """
    def __init__(self):
        self.variables = OrderedDict()
        self.line_records = []
        self.errors = []

    def process_all(self, input_text: str):
        """Processes each non-empty line of the input text."""
        raw_lines = input_text.splitlines()
        for raw_line in raw_lines:
            stripped = raw_line.strip()
            if not stripped:
                continue
            self._process_single_line(raw_line, stripped)

    def _process_single_line(self, original_line: str, line: str):
        target_var = None

        # Check for assignment statement
        eq_index = line.find("=")
        if eq_index >= 0:
            left_part = line[:eq_index].strip()
            expr_part = line[eq_index + 1:].strip()

            if not is_valid_variable_name(left_part):
                self.errors.append("Invalid input code")
                self.line_records.append(
                    LineRecord(original_line, "N/A", "Error: Invalid input code")
                )
                return

            target_var = left_part
        else:
            expr_part = line

        if not expr_part:
            self.errors.append("Invalid input code")
            self.line_records.append(
                LineRecord(original_line, "N/A", "Error: Invalid input code")
            )
            return

        # Tokenize and convert to postfix
        try:
            tokens = get_tokens(expr_part)
            postfix_tokens = infix_to_postfix(tokens)
        except InvalidCodeException:
            self.errors.append("Invalid input code")
            self.line_records.append(
                LineRecord(original_line, "N/A", "Error: Invalid input code")
            )
            return

        postfix_str = postfix_to_string(postfix_tokens)

        # Evaluate the postfix expression
        try:
            val = evaluate_postfix(postfix_tokens, self.variables)
            formatted_val = format_number(val)

            if target_var is not None:
                self.variables[target_var] = val
                result_str = f"{target_var} = {formatted_val}"
            else:
                result_str = formatted_val

            self.line_records.append(LineRecord(original_line, postfix_str, result_str))

        except UndefinedVariableException as e:
            self.errors.append(str(e))
            if target_var is not None:
                result_str = f"{target_var} = Error: {e}"
            else:
                result_str = f"Error: {e}"
            self.line_records.append(LineRecord(original_line, postfix_str, result_str))

        except DivisionByZeroException as e:
            self.errors.append(str(e))
            if target_var is not None and target_var in self.variables:
                # If target variable already had a value prior to division by zero, it retains that value
                prev_val = format_number(self.variables[target_var])
                result_str = f"{target_var} = {prev_val} (retained previous value)"
            elif target_var is not None:
                result_str = f"{target_var} = Error: {e}"
            else:
                result_str = f"Error: {e}"
            self.line_records.append(LineRecord(original_line, postfix_str, result_str))

        except InvalidCodeException:
            self.errors.append("Invalid input code")
            self.line_records.append(
                LineRecord(original_line, postfix_str, "Error: Invalid input code")
            )

    def build_output(self) -> str:
        """
        Builds the formatted output text:
        - Line/Postfix/Result for each input code separated by empty lines.
        - Section for variables used with their final values.
        - Section for all errors found.
        """
        output_lines = []

        # Output per input line
        for rec in self.line_records:
            output_lines.append(f"Line: {rec.original_line.strip()}")
            output_lines.append(f"Postfix: {rec.postfix_str}")
            output_lines.append(f"Result: {rec.result_str}")
            output_lines.append("")

        # Variables used section
        output_lines.append("-------------------------------------------")
        output_lines.append("Variables used:")
        if not self.variables:
            output_lines.append("(none)")
        else:
            for var_name, var_val in self.variables.items():
                output_lines.append(f"{var_name} = {format_number(var_val)}")

        # Errors found section
        output_lines.append("-------------------------------------------")
        output_lines.append("Errors found:")
        if not self.errors:
            output_lines.append("(none)")
        else:
            for err in self.errors:
                output_lines.append(err)

        return "\n".join(output_lines) + "\n"


# ==============================================================================
# GRAPHICAL USER INTERFACE (TKINTER)
# ==============================================================================

class ExpressionEvaluatorApp(tk.Tk):
    """
    Main GUI application containing:
    - Input text area (editable)
    - Output text area (non-editable)
    - Load File button (.in files only)
    - Process button (triggers evaluation if input is not empty)
    """
    def __init__(self):
        super().__init__()
        self.title("PE00 - Expression Evaluation")
        self.geometry("900x620")
        self.minsize(700, 500)
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, padx=10, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        panes = tk.PanedWindow(container, orient=tk.HORIZONTAL, sashwidth=6)
        panes.pack(fill=tk.BOTH, expand=True)

        # Left Frame: Input lines
        input_frame = tk.LabelFrame(panes, text="Input lines:", font=("Arial", 10, "bold"))
        self.input_area = scrolledtext.ScrolledText(
            input_frame, wrap=tk.NONE, font=("Courier New", 11), undo=True
        )
        self.input_area.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        panes.add(input_frame, stretch="always")

        # Right Frame: Output
        output_frame = tk.LabelFrame(panes, text="Output:", font=("Arial", 10, "bold"))
        self.output_area = scrolledtext.ScrolledText(
            output_frame, wrap=tk.NONE, font=("Courier New", 11), state=tk.DISABLED
        )
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        panes.add(output_frame, stretch="always")

        # Bottom Frame: Action Buttons
        button_frame = tk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        load_button = tk.Button(
            button_frame,
            text="Load File",
            font=("Arial", 10, "bold"),
            command=self.on_load_file,
            height=2,
            cursor="hand2"
        )
        load_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        process_button = tk.Button(
            button_frame,
            text="Process",
            font=("Arial", 10, "bold"),
            command=self.on_process,
            height=2,
            cursor="hand2"
        )
        process_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

    def on_load_file(self):
        """
        Loads input code from an external .in file from any directory.
        Overwrites whatever is currently on the input text area.
        """
        file_path = filedialog.askopenfilename(
            title="Open Input File (.in)",
            filetypes=[("Input Files", "*.in"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        # Strictly enforce .in extension per specification
        if not file_path.lower().endswith(".in"):
            messagebox.showerror(
                "Invalid File Extension",
                "Only files with a .in extension can be loaded."
            )
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error Reading File", f"Could not read file:\n{e}")
            return

        # Overwrite input text area
        self.input_area.delete("1.0", tk.END)
        self.input_area.insert(tk.END, content)

    def on_process(self):
        """
        Processes the input code from the input text area.
        Only runs if the input text area is not empty.
        Overwrites whatever is currently on the output text area.
        """
        input_content = self.input_area.get("1.0", tk.END)

        # "The Process button should only work if the designated text area for the input is not empty."
        if not input_content.strip():
            return

        engine = ExpressionEngine()
        engine.process_all(input_content)
        output_result = engine.build_output()

        # Overwrite output text area
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert(tk.END, output_result)
        self.output_area.config(state=tk.DISABLED)


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """Starts the Expression Evaluation GUI application."""
    app = ExpressionEvaluatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()