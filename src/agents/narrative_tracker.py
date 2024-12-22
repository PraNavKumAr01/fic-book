from utils.llm_provider import LLMProvider
from models.story_context import StoryContext
import json
from typing import List, Dict, Any

class NarrativeTrackingAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    def analyze_chapter_narrative(
        self, 
        story_context: StoryContext, 
        chapter_content: str,
        previous_summary: str,
    ) -> StoryContext:
        """
        Analyze the narrative progression and update story context
        """
        messages = [
            {
                "role": "system",
                "content": """
                You are a narrative analysis expert. 
                Carefully analyze the chapter and provide:
                - Character development insights
                - Plot thread progression
                - New narrative tensions
                - Thematic developments

                Respond STRICTLY in the following JSON format:
                {
                    "character_developments": {
                        "character_name": {
                            "arc_progression": "How the character has changed",
                            "emotional_state": "Current psychological condition",
                            "key_decision": "Significant choice made in this chapter"
                        }
                    },
                    "plot_thread_status": {
                        "plot_thread_name": "Current status or progression of the thread"
                    },
                    "new_tensions": [
                        "Newly introduced narrative conflicts or challenges"
                    ],
                    "thematic_progression": {
                        "theme_name": "How the theme has developed or been explored"
                    }
                }

                Respond with only the required JSON, no text before or after the JSON.
                """
            },
            {
                "role": "user",
                "content": f"This is the story plot context {story_context}, This is the summary of what has happened in the previous chapters : {previous_summary}, and this is the generated chapter : {chapter_content}"
            }
        ]
        
        response = self.llm.generate_completion(messages)

        try:
            narrative_analysis = json.loads(response)
            return self._update_story_context(story_context, narrative_analysis)
        except json.JSONDecodeError:
            print("Failed to parse narrative analysis")
            print(response)

            return story_context  # Return the original context if parsing fails

    
    def _update_story_context(
        self, 
        story_context: StoryContext, 
        narrative_analysis: Dict[str, Any]
    ) -> StoryContext:
        """
        Update the story context based on narrative analysis
        """
        # Update character arcs
        if 'character_developments' in narrative_analysis:
            for character, arc in narrative_analysis['character_developments'].items():
                if character not in story_context.character_arcs:
                    story_context.character_arcs[character] = []
                story_context.character_arcs[character].append(arc)
        
        # Update plot threads
        if 'plot_thread_status' in narrative_analysis:
            for thread, status in narrative_analysis['plot_thread_status'].items():
                if thread in story_context.active_plot_threads:
                    story_context.active_plot_threads.remove(thread)
                story_context.active_plot_threads.append(f"{thread} - {status}")
        
        # Add new tensions
        if 'new_tensions' in narrative_analysis:
            story_context.unresolved_tensions.extend(narrative_analysis['new_tensions'])
        
        return story_context

    
    def check_narrative_coherence(
        self, 
        story_context: StoryContext, 
        generated_chapters: List[str]
    ) -> Dict[str, Any]:
        """
        Perform a high-level coherence check across generated chapters
        """
        messages = [
            {
                "role": "system",
                "content": """
                Evaluate the narrative coherence of the generated chapters.
                Assess:
                - Consistency of character arcs
                - Plot thread progression
                - Thematic continuity
                - Potential narrative gaps or inconsistencies
                
                Provide recommendations for improvement if needed.
                """
            },
            {
                "role": "user",
                "content": f"""
                Story Context:
                {json.dumps(story_context.__dict__, indent=2)}
                
                Generated Chapters:
                {json.dumps(generated_chapters, indent=2)}
                """
            }
        ]
        
        coherence_analysis = self.llm.generate_completion(messages)
        
        return {
            "coherence_report": coherence_analysis,
            "needs_revision": len(generated_chapters) > 2  # Example condition
        }