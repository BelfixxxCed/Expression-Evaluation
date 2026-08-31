import lab1

def process_code(lines: list[str]) -> str:
    """
    Processes the input lines by delegating to lab1 logic 
    and formats the evaluated output for the GUI.
    """
    variables = {}
    errors = []
    output = []
    
    for line in lines:
        if not line.strip():
            continue
            
        output.append(f"Line: {line}")
        
        try:
            postfix, result = lab1.process_line(line, variables)
            
            # Formating postfix tokens to string
            postfix_str = " ".join(postfix)
            output.append(f"Postfix: {postfix_str}")
            
            # Formatting the result
            if "=" in line:
                target = line.split("=")[0].strip()
                output.append(f"Result: {target} = {result}")
            else:
                output.append(f"Result: {result}")
                
        except (ValueError, ZeroDivisionError) as e:
            # According to standard assignment format, record the error
            errors.append(str(e))
            output.append("Postfix: ERROR")
            output.append("Result: ERROR")
            
        output.append("")
        
    output.append("-" * 43)
    output.append("Variables used:")
    if variables:
        for var, val in variables.items():
            output.append(f"{var}: {val}")
    else:
        output.append("None")
        
    output.append("-" * 43)
    output.append("Errors found:")
    if errors:
        for err in errors:
            output.append(err)
    else:
        output.append("None")
        
    return "\n".join(output)
