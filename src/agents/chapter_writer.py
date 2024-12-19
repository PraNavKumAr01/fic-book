from utils.llm_provider import LLMProvider
from models.story_context import StoryContext
import json

class ChapterWritingAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    def generate_chapter(
        self, 
        story_context: StoryContext, 
        chapter_info: str, 
        previous_chapter_summary: str = None
    ) -> str:        
        """
        Generate a chapter with narrative continuity
        """
        context_injection = self._prepare_context_injection(
            story_context, 
            f"Chapter {chapter_info[0]}", 
            previous_chapter_summary
        )
        
        messages = [
            {
                "role": "system",
                "content": """
                You are a master storyteller creating a compelling chapter.
                Key guidelines:
                - Maintain narrative consistency
                - Advance character arcs
                - Develop ongoing plot threads
                - Create engaging narrative progression
                
                Write a comprehensive chapter that:
                - Is approximately 2000-3000 words
                - Follows the story's established themes
                - Introduces or resolves narrative tensions
                - Shows character growth
                """
            },
            {
                "role": "user",
                "content": f"""You are currently writing chapter number {chapter_info[0]} in a series of {chapter_info[1]} chapters
                            Write according to the chapter number you are currently on. Build the story if its an early chapter and start to write towards
                            Remeber, the story is going to end on chapter {chapter_info[1]}, and you are on chapter {chapter_info[0]}, so write accordingly so it can end on the last chapter
                            the climax and the end if the chapter is around the last part of the series.
                            The story should end on the last chapter so right accordingly, Make sure to not end it abruptly or too soon.
                            You have to end the storyline if it is the last chapter, make sure to give a reasonable conclusion to the story, but with hints that will leave the reader to ponder more and think about other scenarios
                            Make sure to add a lot of drama, fights, and emotions based on the genre of the story which is : {story_context.genre}
                            This is the entire context of the plot up untill now : {context_injection}
                            This context is only for you to understand and continue writing the story, dont include things like tension and charector details seperately in the chapter content.
                            The chapter content you provide has to be strictly like a story and not points. It should be how stories are written in books.
                            """
            }
        ]
        
        return self.llm.generate_completion(messages)
    
    def _prepare_context_injection(
        self, 
        story_context: StoryContext, 
        chapter_title: str, 
        previous_chapter_summary: str = None
    ) -> str:
        """
        Prepare a detailed context injection for chapter generation
        """
        if isinstance(story_context, dict):
            story_context = StoryContext(**story_context)

        context_details = {
            "Story Title": story_context.title,
            "Genre": story_context.genre,
            "Central Theme": story_context.central_theme,
            "Chapter Title": chapter_title,
            "Protagonist Details": story_context.protagonist,
            "Active Plot Threads": story_context.active_plot_threads,
            "Unresolved Tensions": story_context.unresolved_tensions
        }
        
        if previous_chapter_summary:
            context_details["Previous Chapter Summary"] = previous_chapter_summary
        
        return json.dumps(context_details, indent=2)