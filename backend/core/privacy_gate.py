import re

class PrivacyRedactor:
    def __init__(self):
        # A simple regular expression to match common email formats
        self.email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        
    def redact(self, text: str, user_name: str = None) -> str:
        """
        Redact Personally Identifiable Information (PII) from the given text.
        
        Args:
            text (str): The raw text potentially containing PII.
            user_name (str, optional): The name of the user to redact. Defaults to None.
            
        Returns:
            str: The redacted text safe for sending to external LLMs.
        """
        redacted_text = text
        
        # Redact emails
        redacted_text = self.email_pattern.sub("[EMAIL]", redacted_text)
        
        # Redact user name if provided
        if user_name:
            # simple string replacement
            redacted_text = redacted_text.replace(user_name, "[USER]")
            
        return redacted_text
