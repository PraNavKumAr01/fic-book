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

load_dotenv()

def generate_story_context(plot_planner, story_prompt, genre):
    return plot_planner.generate_story_structure(story_prompt, genre.lower())

def modify_story_context(plot_planner, prompt, genre, existing_structure, feedback):
    return plot_planner.modify_story_structure(prompt, genre, existing_structure, feedback)

def generate_chapter(story_context, chapter_num, total_chapters, previous_summary, 
                    scene_planner, chapter_writer, chapter_refiner):
    scene_layout = scene_planner.plan_chapter_scenes(
        story_context,
        [chapter_num, total_chapters],
        previous_summary
    )
    
    chapter_content = chapter_writer.generate_chapter(
        story_context,
        [chapter_num, total_chapters],
        scene_layout,
        previous_summary
    )
    
    refined_chapter = chapter_refiner.refine_chapter(
        story_context,
        [chapter_num, total_chapters],
        chapter_content,
        scene_layout
    )
    
    return refined_chapter, scene_layout

def modify_chapter_scenes(scene_planner, story_context, chapter_info, existing_scenes, feedback, previous_summary):
    return scene_planner.modify_chapter_scenes(
        story_context,
        chapter_info,
        existing_scenes,
        feedback,
        previous_summary
    )

def main():
    st.set_page_config(layout="wide")
    st.title("Infinite Fiction Generator")
    
    if "story_title" not in st.session_state:
        st.session_state.story_title = None
        st.session_state.story_theme = None
        st.session_state.generated_chapters = []
        st.session_state.story_context = None
        st.session_state.generation_mode = None
        st.session_state.current_chapter = 1
        st.session_state.previous_summary = None
        st.session_state.scene_layout = None
        st.session_state.initial_prompt = None
        st.session_state.genre = None
        st.session_state.context_modified = False

    llm_provider = LLMProvider(api_key=os.getenv('GROQ_API_KEY'))
    plot_planner = PlotPlannerAgent(llm_provider)
    summary_agent = ChapterSummaryAgent(llm_provider)
    chapter_writer = ChapterWritingAgent(llm_provider)
    chapter_refiner = ChapterRefinerAgent(llm_provider)
    narrative_tracker = NarrativeTrackingAgent(llm_provider)
    scene_planner = ScenePlanningAgent(llm_provider)
    
    if not st.session_state.generation_mode:
        story_prompt = st.text_input("Enter your story concept:")
        genre = st.selectbox("Select Genre", [
            "General Fiction", "Science Fiction", "Fantasy", "Mystery", "Romance"
        ])
        num_chapters = st.slider("Number of Chapters", 1, 10, 3)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Quick Generation"):
                st.session_state.generation_mode = "quick"
                st.session_state.num_chapters = num_chapters
                st.session_state.initial_prompt = story_prompt
                st.session_state.genre = genre
                story_context = generate_story_context(plot_planner, story_prompt, genre)
                st.session_state.story_context = story_context
                st.session_state.story_title = story_context.__dict__['title']
                st.session_state.story_theme = story_context.__dict__['central_theme']
                st.rerun()
                
        with col3:
            if st.button("Advanced Generation"):
                st.session_state.generation_mode = "advanced"
                st.session_state.num_chapters = num_chapters
                st.session_state.initial_prompt = story_prompt
                st.session_state.genre = genre
                story_context = generate_story_context(plot_planner, story_prompt, genre)
                st.session_state.story_context = story_context
                st.session_state.story_title = story_context.__dict__['title']
                st.session_state.story_theme = story_context.__dict__['central_theme']
                st.rerun()
    
    if st.session_state.generation_mode == "quick":
        story_overview(st.session_state.story_context.__dict__)

        st.divider()
        
        progress_placeholder = st.empty()
        chapters_container = st.container()
        
        if not st.session_state.generated_chapters:
            for i in range(st.session_state.num_chapters):
                progress_placeholder.write(f"Generating Chapter {i+1}...")
                
                chapter, scene_layout = generate_chapter(
                    st.session_state.story_context,
                    i + 1,
                    st.session_state.num_chapters,
                    st.session_state.previous_summary,
                    scene_planner,
                    chapter_writer,
                    chapter_refiner
                )
                
                st.session_state.generated_chapters.append(chapter)
                with chapters_container:
                    with st.expander(f"Chapter {i+1}", expanded=True):
                        st.write(chapter)
                
                chapter_summary = summary_agent.generate_chapter_summary(
                    chapter,
                    st.session_state.previous_summary
                )
                st.session_state.previous_summary = chapter_summary
                st.session_state.story_context = narrative_tracker.analyze_chapter_narrative(
                    st.session_state.story_context,
                    chapter,
                    st.session_state.previous_summary
                )
            
            progress_placeholder.empty()
        else:
            for i, chapter in enumerate(st.session_state.generated_chapters):
                with chapters_container:
                    with st.expander(f"Chapter {i+1}"):
                        st.write(chapter)
    
    elif st.session_state.generation_mode == "advanced":
        story_overview(st.session_state.story_context.__dict__)

        st.divider()
        
        if st.session_state.current_chapter <= st.session_state.num_chapters:
            st.subheader(f"Chapter {st.session_state.current_chapter} Generation")
            
            # Only show context modification before scene layout is generated
            if not st.session_state.scene_layout and not st.session_state.context_modified:
                context_feedback = st.text_area(
                    "Modify story context (optional):",
                    key=f"context_feedback_{st.session_state.current_chapter}"
                )
                
                if context_feedback:
                    if st.button("Update Context"):
                        st.session_state.story_context = modify_story_context(
                            plot_planner,
                            st.session_state.initial_prompt,
                            st.session_state.genre,
                            st.session_state.story_context,
                            context_feedback
                        )
                        st.session_state.context_modified = True
                        story_overview(st.session_state.story_context.__dict__)
            
            if not st.session_state.scene_layout:
                if st.button("Generate Scene Layout"):
                    chapter, scene_layout = generate_chapter(
                        st.session_state.story_context,
                        st.session_state.current_chapter,
                        st.session_state.num_chapters,
                        st.session_state.previous_summary,
                        scene_planner,
                        chapter_writer,
                        chapter_refiner
                    )
                    st.session_state.scene_layout = scene_layout
                    st.rerun()
            
            if st.session_state.scene_layout:
                st.write("### Scene Layout")
                st.write(st.session_state.scene_layout)
                
                scene_feedback = st.text_area(
                    "Modify scene layout (optional):",
                    key=f"scene_feedback_{st.session_state.current_chapter}"
                )
                
                if st.button("Generate Chapter"):
                    if scene_feedback:
                        modified_scenes = modify_chapter_scenes(
                            scene_planner,
                            st.session_state.story_context,
                            f"Chapter {st.session_state.current_chapter}/{st.session_state.num_chapters}",
                            st.session_state.scene_layout,
                            scene_feedback,
                            st.session_state.previous_summary
                        )
                        st.session_state.scene_layout = modified_scenes
                    
                    chapter_content = chapter_writer.generate_chapter(
                        st.session_state.story_context,
                        [st.session_state.current_chapter, st.session_state.num_chapters],
                        st.session_state.scene_layout,
                        st.session_state.previous_summary
                    )
                    
                    refined_chapter = chapter_refiner.refine_chapter(
                        st.session_state.story_context,
                        [st.session_state.current_chapter, st.session_state.num_chapters],
                        chapter_content,
                        st.session_state.scene_layout
                    )
                    
                    st.session_state.generated_chapters.append(refined_chapter)
                    chapter_summary = summary_agent.generate_chapter_summary(
                        refined_chapter,
                        st.session_state.previous_summary
                    )
                    st.session_state.previous_summary = chapter_summary
                    st.session_state.story_context = narrative_tracker.analyze_chapter_narrative(
                        st.session_state.story_context,
                        refined_chapter,
                        st.session_state.previous_summary
                    )
                    
                    st.session_state.current_chapter += 1
                    st.session_state.scene_layout = None
                    st.session_state.context_modified = False
                    st.rerun()
        
        for i, chapter in enumerate(st.session_state.generated_chapters):
            with st.expander(f"Chapter {i+1}"):
                st.write(chapter)
        
        if st.session_state.current_chapter > st.session_state.num_chapters:
            st.success("Story generation complete!")
    
    if st.session_state.generation_mode:
        if st.button("Start New Story"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()