from utils.llm_provider import LLMProvider
from models.story_context import StoryContext
import json

class ChapterRefinerAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def refine_chapter(
        self,
        story_context: StoryContext,
        chapter_info: str,
        chapter_content: str
    ) -> str:
        """
        Refines a chapter by removing redundant or repetitive lines and enhancing articulation.
        """
        context_injection = self._prepare_context_injection(
            story_context, 
            f"Chapter {chapter_info[0]}"
        )

        messages = [
            {
                "role": "system",
                "content": """
                You are a skilled editor specializing in refining narrative content.
                Your task is to:
                - Eliminate redundancy and repetition.
                - Improve articulation and flow.
                - Ensure consistency with the established story context.
                - Maintain the story's tone and voice.
                
                Refine the provided chapter without altering the plot or character arcs. Make the chapter:
                - Smooth and engaging to read.
                - Free of unnecessary details or overly verbose descriptions.
                - Polished in terms of grammar, structure, and language.
                """
            },
            {
                "role": "user",
                "content": f"""This is chapter {chapter_info[0]} of {chapter_info[1]} in the series.
                Refine it to maintain consistency with the story's tone and narrative arc.
                The story genre is: {story_context.genre}

                This is the raw chapter content:
                ---
                {chapter_content}
                ---

                The context of the story is:
                {context_injection}

                Start directly with the refined chapter, no details or text before or after that
                Provide the refined chapter content below as a continuous story format:
                """
            }
        ]

        return self.llm.generate_completion(messages)

    def _prepare_context_injection(self, story_context: StoryContext, chapter_title: str) -> str:
        """
        Prepare a detailed context injection for chapter refinement.
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

        return json.dumps(context_details, indent=2)