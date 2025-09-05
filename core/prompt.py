def summarize_prompt(chunk: str) -> str:
    prompt = f"""
    ### Instructions
    You are a text summarizer.
    Reduce the following text while preserving its main meaning, clarity, and tone.
    Remove redundancy, simplify phrasing, and keep only the most important details.
    ### Input
    {chunk}
    ### Summary
    """
    return prompt

