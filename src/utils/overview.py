import streamlit as st

def story_overview(story_data):

    # Title and Genre
    st.title(story_data["title"])
    st.caption(str(story_data["genre"]).title())

    # Central Theme
    st.markdown("### ✨ Central Theme")
    st.write(story_data["central_theme"])

    # Characters and Plot Threads in Dropdowns
    with st.expander("👤 Protagonist Details"):
        st.markdown(f"**{story_data['protagonist']['name']}**")
        st.write(story_data["protagonist"]["background"])
        st.markdown("**Goal:**")
        st.write(story_data["protagonist"]["primary_goal"])
        st.markdown("**Internal Conflict:**")
        st.write(story_data["protagonist"]["internal_conflict"])

    with st.expander("🎯 Antagonist Details"):
        st.markdown(f"**{story_data['antagonist']['name']}**")
        st.markdown("**Motivation:**")
        st.write(story_data["antagonist"]["motivation"])
        st.markdown("**Power Source:**")
        st.write(story_data["antagonist"]["power_source"])

    with st.expander("🔄 Active Plot Threads"):
        for thread in story_data["active_plot_threads"]:
            st.markdown(f"- {thread}")

    with st.expander("⚠️ Unresolved Tensions"):
        for tension in story_data["unresolved_tensions"]:
            st.markdown(f"- {tension}")
