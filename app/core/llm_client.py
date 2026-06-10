import os
from anthropic import Anthropic
from typing import Optional

class LLMClient:
    """Client for interacting with the LLM API to generate content."""

    def __init__(self, api_key: Optional[str] = None):
        # Priority: explicitly passed key -> environment variable
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            # We don't raise an error here so the app can start and show a config error in UI
            print("⚠️ WARNING: ANTHROPIC_API_KEY not found. LLM features will be unavailable.")
            self.client = None
        else:
            self.client = Anthropic(api_key=self.api_key)

    def generate_text(self, prompt: str, model: str = "claude-3-5-sonnet-20240620") -> Optional[str]:
        """Sends a prompt to the LLM and returns the generated text."""
        if not self.client:
            print("❌ LLMClient error: No API key configured.")
            return None

        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"❌ Error during LLM generation: {e}")
            return None
