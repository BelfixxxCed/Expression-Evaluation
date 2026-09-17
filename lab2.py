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