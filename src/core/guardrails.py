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

    def validate_output(self, text: str) -> str:
        """
        Validates the output text against known forbidden phrases.
        Returns a security alert message if a violation is found.
        Otherwise returns the original text.
        """
        if not text:
            return ""
            
        lower_text = text.lower()
        forbidden_phrases = [
            "pwned",
            "hacked",
            "root access",
            "system prompt"
        ]
        
        for phrase in forbidden_phrases:
            if phrase in lower_text:
                return "[Security Alert] Odpowiedź modelu została zablokowana ze względów bezpieczeństwa."
                
        return text

guardrails = Guardrails()
