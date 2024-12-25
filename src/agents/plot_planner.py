from utils.llm_provider import LLMProvider
from models.story_context import StoryContext
import json

class PlotPlannerAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def generate_story_structure(
        self, 
        prompt: str, 
        genre: str = "general fiction"
    ) -> StoryContext:
        messages = [
            {
                "role": "system",
                "content": """
                You are a master storyteller and plot architect. 
                Generate a comprehensive story structure with:
                - Central theme
                - Key plot points
                - Character arcs
                - Potential narrative tensions
                
                Respond STRICTLY in the following JSON format:
                {
                    "title": "Story Title",
                    "genre": "Specified Genre",
                    "central_theme": "Core narrative theme or message (should be less than 10 words)",
                    "protagonist": {
                        "name": "Protagonist Name",
                        "background": "Brief character history",
                        "primary_goal": "What the protagonist wants to achieve",
                        "internal_conflict": "Character's inner struggle"
                    },
                    "antagonist": {
                        "name": "Antagonist Name",
                        "motivation": "Why they oppose the protagonist",
                        "power_source": "Their strength or advantage"
                    },
                    "plot_threads": [
                        "Initial primary plot thread",
                        "Secondary narrative line",
                        "Potential subplot"
                    ],
                    "tensions": [
                        "Initial conflict between protagonist and antagonist",
                        "Potential twist or unexpected obstacle"
                    ]
                }

                Respond with just the required JSON, no text before or after that.
                """
            },
            {
                "role": "user",
                "content": f"You need to keep the story about this specific prompt : {prompt} which fits this specific genre : {genre}"
            }
        ]
        
        response = self.llm.generate_completion(messages)
        
        try:
            story_data = json.loads(response)
            context = StoryContext(
                title=story_data.get('title', ''),
                genre=genre,
                central_theme=story_data.get('central_theme', ''),
                protagonist=story_data.get('protagonist', {}),
                antagonist=story_data.get('antagonist', {}),
                active_plot_threads=story_data.get('plot_threads', []),
                unresolved_tensions=story_data.get('tensions', [])
            )
            return context
        except json.JSONDecodeError:
            print("Failed to parse story structure")
            return StoryContext()

    def modify_story_structure(
        self, 
        prompt: str, 
        genre: str, 
        existing_structure: StoryContext, 
        additional_prompt: str
    ) -> StoryContext:
        messages = [
            {
                "role": "system",
                "content": """
                You are a master storyteller and plot architect. 
                Modify the provided story structure based on the additional instructions below. 
                Adhere to the new prompt strictly while maintaining coherence and narrative depth.
                
                Respond STRICTLY in the following JSON format:
                {
                    "title": "Story Title",
                    "genre": "Specified Genre",
                    "central_theme": "Core narrative theme or message (should be less than 10 words)",
                    "protagonist": {
                        "name": "Protagonist Name",
                        "background": "Brief character history",
                        "primary_goal": "What the protagonist wants to achieve",
                        "internal_conflict": "Character's inner struggle"
                    },
                    "antagonist": {
                        "name": "Antagonist Name",
                        "motivation": "Why they oppose the protagonist",
                        "power_source": "Their strength or advantage"
                    },
                    "plot_threads": [
                        "Initial primary plot thread",
                        "Secondary narrative line",
                        "Potential subplot"
                    ],
                    "tensions": [
                        "Initial conflict between protagonist and antagonist",
                        "Potential twist or unexpected obstacle"
                    ]
                }

                Respond with just the required JSON, no text before or after that.
                """
            },
            {
                "role": "user",
                "content": f"Here is the existing story structure: {json.dumps(existing_structure.__dict__)} which was created using this initial idea prompt {prompt}"
            },
            {
                "role": "user",
                "content": f"You need to modify the story to incorporate this additional prompt: {additional_prompt}"
            }
        ]

        response = self.llm.generate_completion(messages)

        try:
            modified_story_data = json.loads(response)
            modified_context = StoryContext(
                title=modified_story_data.get('title', ''),
                genre=genre,
                central_theme=modified_story_data.get('central_theme', ''),
                protagonist=modified_story_data.get('protagonist', {}),
                antagonist=modified_story_data.get('antagonist', {}),
                active_plot_threads=modified_story_data.get('plot_threads', []),
                unresolved_tensions=modified_story_data.get('tensions', [])
            )
            return modified_context
        except json.JSONDecodeError:
            print("Failed to parse modified story structure")
            return existing_structure