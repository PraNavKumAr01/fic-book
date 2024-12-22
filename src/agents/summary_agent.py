from utils.llm_provider import LLMProvider

class ChapterSummaryAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    def generate_chapter_summary(self, chapter_content: str, previous_summary: str) -> str:
        messages = [
            {
                "role": "system",
                "content": """
                Provide a concise, objective summary of the chapter. Also pay attention to the summary of the previous chapter provided
                Create a new summary of this chapter combined with the summary of the previous chapter. Keep the important details from this chapter and the previous summary as well
                Focus on:
                - Key events
                - Character developments
                - Plot progression
                - Emerging tensions
                
                Keep the summary to 6-8 sentences.
                Directly start with the summary, no text before or after that.
                """
            },
            {
                "role": "user",
                "content": f"Here is the current chapter content : {chapter_content}, and this is the previous chapter summary : {previous_summary} (If this is None then assume it is the first chapter), Start directly with the summary, no text before or after that"
            }
        ]
        
        return self.llm.generate_completion(messages)