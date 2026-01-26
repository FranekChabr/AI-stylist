from typing import List

class SecurityError(Exception):
    """Exception raised for security violations."""
    pass

class Guardrails:
    def __init__(self):
        self.blocked_phrases: List[str] = [
            "ignore previous instructions",
            "system prompt",
            "delete all"
        ]

    def validate_input(self, text: str) -> bool:
        """
        Validates the input text against known prompt injection patterns.
        Raises SecurityError if a pattern is found.
        """
        if not text:
            return True
            
        lower_text = text.lower()
        for phrase in self.blocked_phrases:
            if phrase in lower_text:
                raise SecurityError(f"Potential prompt injection detected: prohibited phrase '{phrase}' found.")
        return True

    def sanitize(self, text: str) -> str:
        """
        Basic sanitization of input text.
        Removes null bytes and other potentially dangerous control characters if necessary.
        """
        if not text:
            return ""
        # Removing null bytes as a basic safety measure
        return text.replace("\0", "")

guardrails = Guardrails()
