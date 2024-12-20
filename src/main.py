import streamlit as st
import os
from dotenv import load_dotenv

from utils.llm_provider import LLMProvider
from agents.plot_planner import PlotPlannerAgent
from agents.summary_agent import ChapterSummaryAgent
from agents.chapter_writer import ChapterWritingAgent
from agents.narrative_tracker import NarrativeTrackingAgent

# Load environment variables
load_dotenv()

def main():
    st.title("Infinite Fiction Generator")
    
    # Initialize LLM Provider
    llm_provider = LLMProvider(api_key=os.getenv('GROQ_API_KEY'))
    
    # Initialize Agents
    plot_planner = PlotPlannerAgent(llm_provider)
    summary_agent = ChapterSummaryAgent(llm_provider)
    chapter_writer = ChapterWritingAgent(llm_provider)
    narrative_tracker = NarrativeTrackingAgent(llm_provider)
    
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
        
        # Display Story Context
        st.write("### Story Overview")
        st.json(story_context.__dict__)
        
        # Generate Chapters
        generated_chapters = []
        previous_summary = None
        
        for i in range(num_chapters):
            st.write(f"### Generating Chapter {i+1}")
            
            # Generate Chapter
            chapter_content = chapter_writer.generate_chapter(
                story_context, 
                [i + 1, num_chapters], 
                previous_summary
            )
            generated_chapters.append(chapter_content)
            
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
        
        # Final Narrative Coherence Check
        # coherence_report = narrative_tracker.check_narrative_coherence(
        #     story_context, 
        #     generated_chapters
        # )
        
        # st.write("### Narrative Coherence Report")
        # st.json(coherence_report)

if __name__ == "__main__":
    main()