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


def translate_prompt(chunk: str, source_lang: str, target_lang: str) -> str:
    prompt = f"""
    ### Instructions
    Translate the following text from {source_lang} to {target_lang}. 
    Output only the translated text with no explanations or extra phrases.

    ### Input
    {chunk}

    ### Translation
    """
    return prompt


def translate_prompt_with_context(
    chunk: str,
    summary: str,
    source_lang: str,
    target_lang: str,
) -> str:
    prompt = f"""
    ### Instructions
    Translate the provided text from {source_lang} to {target_lang}.
    Keep in mind the context provided, to help with translation.
    Don't translate names, dates, numbers, or formulas.
    Output only the translated text with no explanations or extra phrases.

    ### Context
    {summary}

    ### Text
    {chunk}

    ### Translation
    """
    return prompt
