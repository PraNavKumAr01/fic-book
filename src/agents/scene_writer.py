from utils.llm_provider import LLMProvider
from models.story_context import StoryContext
import json

class ScenePlanningAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    def plan_chapter_scenes(
        self, 
        story_context: StoryContext,
        chapter_info: str,
        previous_chapter_summary: str = None
    ) -> str:
        context_injection = self._prepare_context_injection(
            story_context,
            f"Chapter {chapter_info[0]}",
            previous_chapter_summary
        )
        
        messages = [
            {
                "role": "system",
                "content": """
                You are a master story planner creating detailed scene outlines.
                Key guidelines:
                - Break chapter into 4-6 distinct scenes
                - Each scene should have clear dramatic purpose
                - Ensure smooth transitions between scenes
                - Balance action, dialogue, and description
                - Maintain narrative pacing and tension
                
                Create a scene-by-scene outline that includes:
                - Scene setting and atmosphere
                - Key character interactions
                - Major plot developments
                - Emotional beats and conflicts
                - Scene-specific tension points
                """
            },
            {
                "role": "user", 
                "content": f"""Plan the scenes for chapter {chapter_info[0]} of {chapter_info[1]}.
                
                Story phase considerations:
                - Early chapter (1-3): Establish world, characters, initial conflicts
                - Mid chapter (4-7): Escalate tensions, deepen relationships, reveal complications
                - Late chapter (8-10): Build toward resolution, heighten stakes, prepare for climax
                - Final chapter: Deliver satisfying conclusion with room for reflection
                
                Genre ({story_context.genre}) requirements:
                - Include genre-appropriate dramatic moments
                - Balance emotional intensity with plot progression
                - Maintain genre conventions while being original
                
                Context: {context_injection}
                
                Provide a scene-by-scene breakdown focusing on dramatic structure and narrative flow.
                Each scene should advance both plot and character development while building tension.

                Start directly with the layout, no text before or after it
                """
            }
        ]
        
        return self.llm.generate_completion(messages, model='llama-3.3-70b-versatile')
    
    def modify_chapter_scenes(
        self,
        story_context: StoryContext,
        chapter_info: str,
        existing_scenes: str,
        additional_prompt: str,
        previous_chapter_summary: str = None
    ) -> str:
        context_injection = self._prepare_context_injection(
            story_context,
            f"Chapter {chapter_info[0]}",
            previous_chapter_summary
        )
        
        messages = [
            {
                "role": "system",
                "content": """
                You are a master story planner tasked with modifying an existing chapter's scenes.
                Key guidelines:
                - Adhere to the additional prompt provided
                - Retain logical flow and coherence with the existing story
                - Balance action, dialogue, and description
                - Maintain narrative pacing and tension

                Modify the provided scene breakdown based on the additional prompt.
                Ensure the changes advance both plot and character development while enhancing tension.
                """
            },
            {
                "role": "user", 
                "content": f"""Modify the scenes for chapter {chapter_info[0]} of {chapter_info[1]}.
                
                Existing Scenes: {existing_scenes}
                
                Additional Prompt: {additional_prompt}
                
                Context: {context_injection}

                Provide the modified scene breakdown directly, no text before or after it.
                """
            }
        ]
        
        return self.llm.generate_completion(messages, model='llama-3.3-70b-versatile')

    def _prepare_context_injection(
        self,
        story_context: StoryContext,
        chapter_title: str,
        previous_chapter_summary: str = None
    ) -> str:
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