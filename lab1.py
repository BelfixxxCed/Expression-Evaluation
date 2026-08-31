# this program processes mathematical expressions and assignment statements.
# it separates an expression into tokens, converts the infix expression
# into postfix notation, evaluates the postfix expression, and stores
# the values of assigned variables for later use.
#
# supported operators:
# + for addition
# - for subtraction
# * for multiplication
# / for division
# % for modulo
#
# the program also handles parentheses, decimal values, variables,
# undefined variables, invalid expressions, mismatched parentheses,
# and division or modulo by zero.


# processes an expression character by character and groups
# numbers and variable names into tokens while separating
# operators and parentheses.
def get_tokens(expression):
    # this list stores all the tokens found in the expression.
    tokens = []

    # this temporary string is used to build a number
    # or variable name one character at a time.
    current = ""

    # read the expression one character at a time.
    for char in expression:

        # add letters, numbers, and decimal points to the
        # current token so multi-character values and variables
        # are treated as one token.
        if char.isalnum() or char == ".":
            current += char

        # check if the character is a supported operator
        # or a parenthesis.
        elif char in "+-*/%()":

            # save the current number or variable before
            # adding the operator or parenthesis.
            if current:
                tokens.append(current)
                current = ""

            # store the operator or parenthesis as a separate token.
            tokens.append(char)

        # ignore spaces and other whitespace characters.
        elif char.isspace():

            # save the current number or variable when whitespace
            # marks the end of the token.
            if current:
                tokens.append(current)
                current = ""

        # reject characters that are not supported by the program.
        else:
            raise ValueError(f"Invalid character: {char}")

    # save the last number or variable after the loop ends.
    if current:
        tokens.append(current)

    # return the complete list of tokens.
    return tokens


# converts the tokenized infix expression into postfix notation
# by arranging operands and operators according to precedence.
def infix_to_postfix(tokens):
    # this list stores the final postfix expression.
    output = []

    # this stack temporarily stores operators and parentheses.
    operators = []

    # process each token from left to right.
    for token in tokens:

        # numbers and variables are operands, so they can be
        # added directly to the postfix output.
        if token.replace(".", "", 1).isdigit() or token.isidentifier():
            output.append(token)

        # an opening parenthesis is placed on the operator stack
        # until its matching closing parenthesis is encountered.
        elif token == "(":
            operators.append(token)

        # a closing parenthesis means that operators inside
        # the matching parentheses must be moved to the output.
        elif token == ")":

            # move operators from the stack to the output
            # until the matching opening parenthesis is found.
            while operators and operators[-1] != "(":
                output.append(operators.pop())

            # if there is no opening parenthesis, the parentheses
            # in the expression do not match.
            if not operators:
                raise ValueError("Mismatched parentheses")

            # remove the opening parenthesis from the stack
            # because parentheses are not included in postfix notation.
            operators.pop()

        # process supported mathematical operators.
        elif token in "+-*/%":

            # addition and subtraction have lower precedence.
            if token in "+-":
                current_precedence = 1

            # multiplication, division, and modulo have higher precedence.
            else:
                current_precedence = 2

            # compare the current operator with the operator
            # currently at the top of the stack.
            while operators and operators[-1] != "(":

                # determine the precedence of the operator
                # at the top of the stack.
                if operators[-1] in "+-":
                    stack_precedence = 1
                else:
                    stack_precedence = 2

                # if the operator on the stack has higher or equal
                # precedence, move it to the postfix output first.
                if stack_precedence >= current_precedence:
                    output.append(operators.pop())

                # stop removing operators when the current operator
                # has higher precedence.
                else:
                    break

            # place the current operator on the operator stack.
            operators.append(token)

        # reject tokens that are not numbers, variables,
        # parentheses, or supported operators.
        else:
            raise ValueError(f"Invalid token: {token}")

    # move all remaining operators from the stack to the output.
    while operators:

        # an opening parenthesis still on the stack means
        # that it does not have a matching closing parenthesis.
        if operators[-1] == "(":
            raise ValueError("Mismatched parentheses")

        # move the remaining operator to the postfix output.
        output.append(operators.pop())

    # return the completed postfix expression.
    return output


# evaluates a postfix expression using a stack and the
# currently stored values of variables.
def evaluate_postfix(postfix, variables):
    # this stack stores operands and intermediate results
    # while the postfix expression is being evaluated.
    stack = []

    # process each token in the postfix expression from left to right.
    for token in postfix:

        # check if the token is a number, including decimal numbers.
        if token.replace(".", "", 1).isdigit():

            # convert the number from a string to a floating-point value
            # and place it on the evaluation stack.
            stack.append(float(token))

        # check if the token is a variable name.
        elif token.isidentifier():

            # a variable must have been assigned a value before
            # it can be used in an expression.
            if token not in variables:
                raise ValueError(
                    f"Undefined variable: {token}"
                )

            # get the most recently stored value of the variable
            # and place it on the evaluation stack.
            stack.append(variables[token])

        # process mathematical operators.
        elif token in "+-*/%":

            # every supported operator is binary, meaning it needs
            # two operands to perform an operation.
            if len(stack) < 2:
                raise ValueError("Invalid expression")

            # the first value removed from the stack is
            # the right operand.
            right = stack.pop()

            # the second value removed is the left operand.
            left = stack.pop()

            # perform addition.
            if token == "+":
                result = left + right

            # perform subtraction.
            elif token == "-":
                result = left - right

            # perform multiplication.
            elif token == "*":
                result = left * right

            # perform division.
            elif token == "/":

                # division by zero is not allowed.
                if right == 0:
                    raise ZeroDivisionError(
                        "Division by zero"
                    )

                # calculate the division result.
                result = left / right

            # perform modulo.
            elif token == "%":

                # modulo by zero is not allowed.
                if right == 0:
                    raise ZeroDivisionError(
                        "Modulo by zero"
                    )

                # calculate the modulo result.
                result = left % right

            # place the calculated result back onto the stack
            # so it can be used by the next operator.
            stack.append(result)

        # reject any token that is not recognized.
        else:
            raise ValueError(f"Invalid token: {token}")

    # a valid postfix expression must leave exactly one
    # final result on the stack.
    if len(stack) != 1:
        raise ValueError("Invalid expression")

    # return the final evaluated result.
    return stack.pop()


# processes one complete input line by determining whether
# it is an assignment or an expression, then tokenizing,
# converting, evaluating, and storing the result when needed.
def process_line(line, variables):

    # remove unnecessary whitespace from the beginning and end
    # of the input line.
    line = line.strip()

    # reject an input line that contains no code.
    if not line:
        raise ValueError("Empty input")

    # check whether the input line contains an assignment operator.
    if "=" in line:

        # an assignment must contain exactly one equals sign.
        if line.count("=") != 1:
            raise ValueError("Invalid assignment")

        # separate the target variable from the expression.
        target, expression = line.split("=", 1)

        # remove unnecessary spaces around the target variable.
        target = target.strip()

        # remove unnecessary spaces around the expression.
        expression = expression.strip()

        # make sure the target follows the required
        # variable naming format.
        if not target.isidentifier():
            raise ValueError(
                f"Invalid variable name: {target}"
            )

        # an assignment must contain an expression after the equals sign.
        if not expression:
            raise ValueError("Missing expression")

    else:

        # if there is no equals sign, the input is an expression only.
        # there is no target variable to store the result in.
        target = None

        # use the entire input line as the expression.
        expression = line

    # convert the expression into a list of tokens.
    tokens = get_tokens(expression)

    # reject an expression that produced no tokens.
    if not tokens:
        raise ValueError("Invalid expression")

    # convert the infix tokens into postfix notation.
    postfix = infix_to_postfix(tokens)

    # evaluate the postfix expression using the current
    # values stored in the variables dictionary.
    result = evaluate_postfix(postfix, variables)

    # store the result only after the expression has been
    # successfully evaluated.
    #
    # this ensures that an error such as division by zero
    # does not overwrite a variable's previous value.
    if target is not None:
        variables[target] = result

    # return both the postfix expression and evaluated result
    # so they can be displayed by the main program or GUI.
    return postfix, result


# contains the main program flow for receiving and processing
# expressions and assignment statements.
def main():

    # create a dictionary to store the current value
    # of every assigned variable.
    variables = {}

    # display the program title and basic instructions.
    print("Expression Processor")
    print("--------------------")
    print("Enter an expression or assignment.")
    print("Press ENTER on an empty line to stop.")
    print()

    # continuously ask the user for input until
    # an empty line is entered.
    while True:

        # read one complete input line from the user.
        line = input("Enter code: ")

        # stop the program when the user enters
        # an empty or whitespace-only line.
        if not line.strip():
            break

        try:

            # process the input line and receive
            # its postfix expression and result.
            postfix, result = process_line(
                line,
                variables
            )

            # display the postfix representation of the expression.
            print("Postfix:", " ".join(postfix))

            # display the evaluated result.
            print("Result:", result)

            # display the variables and their most recently
            # assigned values.
            print("Variables:", variables)

        # handle division-by-zero and modulo-by-zero errors.
        except ZeroDivisionError as error:

            # display the evaluation error without stopping
            # the entire program.
            print("Evaluation Error:", error)

        # handle invalid expressions, variables, tokens,
        # assignments, and parentheses.
        except ValueError as error:

            # display the expression-related error without
            # stopping the entire program.
            print("Expression Error:", error)

        # print an empty line to separate each input's output.
        print()

# start the main program.
main()