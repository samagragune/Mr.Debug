import os

AI_READY = all([
    os.getenv("AZURE_OPENAI_ENDPOINT"),
    os.getenv("AZURE_OPENAI_API_KEY"),
    os.getenv("AZURE_OPENAI_DEPLOYMENT")
])


def interpret_error(code: str, error: str) -> dict:
    """
    Explains Python errors in simple human language.
    Uses AI if available, otherwise falls back to offline logic.
    """

    if AI_READY:
        return _ai_placeholder_explain(code, error)
    else:
        return _fallback_explain(error)


def _ai_placeholder_explain(code: str, error: str) -> dict:
    return {
        "summary": "AI-based explanation will be generated here.",
        "why_it_happened": "Azure OpenAI integration is enabled in production.",
        "how_to_fix": [
            "Deploy with Azure OpenAI credentials to enable full explanations"
        ],
        "corrected_example": None,
        "confidence": 0.5
    }


def _fallback_explain(error: str) -> dict:
    error_lower = error.lower()

    if "nameerror" in error_lower:
        return {
            "summary": "You used a variable before defining it.",
            "why_it_happened": "Python could not find the variable name.",
            "how_to_fix": [
                "Define the variable before using it",
                "Check spelling"
            ],
            "corrected_example": "x = 10\nprint(x)",
            "confidence": 0.95
        }

    if "zerodivisionerror" in error_lower:
        return {
            "summary": "You divided a number by zero.",
            "why_it_happened": "Division by zero is undefined.",
            "how_to_fix": [
                "Ensure the denominator is not zero"
            ],
            "corrected_example": "if y != 0:\n    print(x / y)",
            "confidence": 0.95
        }

    if "syntaxerror" in error_lower:
        return {
            "summary": "There is a syntax mistake in your code.",
            "why_it_happened": "Python could not parse the code.",
            "how_to_fix": [
                "Check brackets, colons, indentation"
            ],
            "corrected_example": None,
            "confidence": 0.85
        }

    return {
        "summary": "Your code caused an error.",
        "why_it_happened": "Python encountered a runtime problem.",
        "how_to_fix": [
            "Read the error message",
            "Fix the issue and retry"
        ],
        "corrected_example": None,
        "confidence": 0.7
    }
