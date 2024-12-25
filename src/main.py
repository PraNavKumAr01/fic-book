import streamlit as st
import os
from dotenv import load_dotenv

from utils.llm_provider import LLMProvider
from utils.get_pdf import create_pdf
from utils.overview import story_overview
from agents.plot_planner import PlotPlannerAgent
from agents.summary_agent import ChapterSummaryAgent
from agents.chapter_writer import ChapterWritingAgent
from agents.narrative_tracker import NarrativeTrackingAgent
from agents.chapter_refiner import ChapterRefinerAgent
from agents.scene_writer import ScenePlanningAgent

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(layout="wide")
    st.title("Infinite Fiction Generator")
    
    # Initialize session state for persistence
    if "story_title" not in st.session_state:
        st.session_state["story_title"] = None
    if "story_theme" not in st.session_state:
        st.session_state["story_theme"] = None
    if "generated_chapters" not in st.session_state:
        st.session_state["generated_chapters"] = []

    # Initialize LLM Provider
    llm_provider = LLMProvider(api_key=os.getenv('GROQ_API_KEY'))
    
    # Initialize Agents
    plot_planner = PlotPlannerAgent(llm_provider)
    summary_agent = ChapterSummaryAgent(llm_provider)
    chapter_writer = ChapterWritingAgent(llm_provider)
    chapter_refiner = ChapterRefinerAgent(llm_provider)
    narrative_tracker = NarrativeTrackingAgent(llm_provider)
    scene_planner = ScenePlanningAgent(llm_provider)
    
    # User Input
    story_prompt = st.text_input("Enter your story concept:")
    genre = st.selectbox("Select Genre", [
        "General Fiction", 
        "Science Fiction", 
        "Fantasy", 
        "Mystery", 
        "Romance"
    ])
    
    # Number of chapters to generate
    num_chapters = st.slider("Number of Chapters", 1, 10, 3)

    if st.button("Generate Story"):
        # Generate Initial Story Context
        story_context = plot_planner.generate_story_structure(
            story_prompt, 
            genre.lower()
        )

        story_context_dict = story_context.__dict__
        st.session_state["story_title"] = story_context_dict['title']
        st.session_state["story_theme"] = story_context_dict['central_theme']

        story_overview(story_context_dict)
        
        # Generate Chapters
        st.session_state["generated_chapters"] = []
        previous_summary = None
        
        for i in range(num_chapters):
            st.write(f"### Generating Chapter {i+1}")

            scene_layout = scene_planner.plan_chapter_scenes(
                story_context,
                [i + 1, num_chapters], 
                previous_summary
            )

            # Generate Chapter
            chapter_content = chapter_writer.generate_chapter(
                story_context, 
                [i + 1, num_chapters],
                scene_layout,
                previous_summary
            )

            # Refine chapter
            refined_chapter_content = chapter_refiner.refine_chapter(
                story_context,
                [i + 1, num_chapters],
                chapter_content,
                scene_layout
            )

            st.session_state["generated_chapters"].append(refined_chapter_content)
            
            # Generate Chapter Summary
            chapter_summary = summary_agent.generate_chapter_summary(chapter_content, previous_summary)
            previous_summary = chapter_summary
            
            # Track Narrative Progression
            story_context = narrative_tracker.analyze_chapter_narrative(
                story_context, 
                chapter_content,
                previous_summary
            )
            
            # Display Chapter
            with st.expander(f"Chapter {i+1}"):
                st.write(chapter_content)
                st.write("### Chapter Summary")
                st.write(chapter_summary)

if __name__ == "__main__":
    main()