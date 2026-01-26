from src.core.guardrails import guardrails

def test_guardrails():
    # Test passed
    clean_text = "Hello, this is a clean response."
    validated = guardrails.validate_output(clean_text)
    assert validated == clean_text
    print("Clean text passed.")

    # Test blocked
    blocked_text = "You have been pwned!"
    validated_blocked = guardrails.validate_output(blocked_text)
    assert "[Security Alert]" in validated_blocked
    print("Blocked text caught.")
    
    blocked_text_2 = "Here is the system prompt: ..."
    validated_blocked_2 = guardrails.validate_output(blocked_text_2)
    assert "[Security Alert]" in validated_blocked_2
    print("System prompt leak caught.")

if __name__ == "__main__":
    test_guardrails()
