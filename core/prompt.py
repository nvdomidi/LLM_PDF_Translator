def summarize_prompt(chunk: str) -> str:
    prompt = f"""
    ### Instructions
    Summarize the following text concisely. Keep the main meaning, clarity, and tone.
    Remove redundancy, simplify phrasing, and output only the summary text with no prefatory phrases or explanations.

    ### Input
    {chunk}

    ### Summary
    """
    return prompt


def rewrite_prompt(chunk: str, instruction: str) -> str:
    prompt = f"""
    ### Instructions
    You will rewrite the provided text according to this request: {instruction}
    Preserve the core meaning, keep facts accurate, and ensure the output is fluent and readable.
    Return only the rewritten text without commentary.

    ### Text
    {chunk}

    ### Rewritten Text
    """
    return prompt


def rewrite_prompt_with_context(
    chunk: str,
    summary: str,
    instruction: str,
) -> str:
    prompt = f"""
    ### Instructions
    Rewrite the provided text according to this request: {instruction}
    Use the context to stay consistent with the overall document meaning.
    Keep facts accurate and output only the rewritten text without commentary.

    ### Context
    {summary}

    ### Text
    {chunk}

    ### Rewritten Text
    """
    return prompt
