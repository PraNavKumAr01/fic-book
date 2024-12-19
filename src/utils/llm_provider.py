from typing import List, Dict, Any
import groq

class LLMProvider:
    def __init__(self, api_key: str):
        self.client = groq.Groq(api_key=api_key)
    
    def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.9,
        max_tokens: int = 8000
    ) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            return ""