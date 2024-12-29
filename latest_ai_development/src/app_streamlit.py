import streamlit as st
import warnings
import logging
import json

from latest_ai_development.crew import LatestAiDevelopment

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Suppress specific warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def parse_professors(raw_text):
    """
    Parses the raw text to extract professors' information.
    """
    import re
    professors_section = re.search(r"\*\*Professors in Mechanical Engineering at UTD:\*\*(.*?)\*\*Labs", raw_text, re.DOTALL)
    if professors_section:
        professors_text = professors_section.group(1).strip()
        professors = re.findall(
            r"\d+\.\s\*\*(.*?)\*\*\s+- Research Interests: (.*?)\s+- Email: (.*?)\s+- Phone: (.*?)\s+- URL: \[Profile\]\((.*?)\)",
            professors_text
        )
        return professors
    return []

def parse_labs(raw_text):
    """
    Parses the raw text to extract labs' information.
    """
    import re
    labs_section = re.search(r"\*\*Labs associated with Mechanical Engineering at UTD:\*\*(.*?)\*\*Additional Relevant Links", raw_text, re.DOTALL)
    if labs_section:
        labs_text = labs_section.group(1).strip()
        labs = re.findall(
            r"\d+\.\s\*\*(.*?)\*\*\s+- Focus: (.*?)\s+- URL: \[LAB\]\((.*?)\)",
            labs_text
        )
        return labs
    return []

def display_professors(professors):
    """
    Displays professors' information in a structured format.
    """
    if not professors:
        st.info("No professor information available.")
        return
    
    st.subheader("Professors in Mechanical Engineering at UTD")
    for prof in professors:
        name, research, email, phone, url = prof
        with st.expander(name):
            st.markdown(f"**Research Interests:** {research}")
            st.markdown(f"**Email:** [mailto:{email}](mailto:{email})")
            st.markdown(f"**Phone:** {phone}")
            st.markdown(f"**Profile:** [Link]({url})")

def display_labs(labs):
    """
    Displays labs' information in a structured format.
    """
    if not labs:
        st.info("No lab information available.")
        return
    
    st.subheader("Labs Associated with Mechanical Engineering at UTD")
    for lab in labs:
        name, focus, url = lab
        with st.expander(name):
            st.markdown(f"**Focus:** {focus}")
            st.markdown(f"**Lab URL:** [Link]({url})")

def display_tasks(tasks_output):
    """
    Displays tasks output in a structured manner.
    """
    if not tasks_output:
        st.info("No task outputs available.")
        return
    
    st.subheader("Task Outputs")
    for task in tasks_output:
        with st.expander(task.name):
            st.markdown(f"**Description:** {task.description}")
            st.markdown(f"**Expected Output:** {task.expected_output}")
            st.markdown(f"**Summary:** {task.summary}")
            st.markdown(f"**Agent:** {task.agent}")
            st.markdown("**Raw Output:**")
            st.write(task.raw)

def main():
    st.set_page_config(page_title="Latest AI Development Web App", layout="wide")
    st.title("Latest AI Development Web App")
    
    # User inputs
    topic = st.text_input("Enter the topic")
    university = st.text_input("Enter your university")
    resume = st.text_area("Enter your resume")
    
    # Submit button
    if st.button("Submit"):
        if not topic or not university or not resume:
            st.error("Please fill in all the fields before submitting.")
            return
        
        # Construct the inputs dictionary
        inputs = {
            'topic': topic,
            'university': university,
            'resume': resume,
        }
        
        # Kick off your AI dev crew with a spinner
        try:
            with st.spinner("Processing..."):
                logger.debug(f"Inputs received: {inputs}")
                crew_instance = LatestAiDevelopment()
                crew = crew_instance.crew()
                result = crew.kickoff(inputs=inputs)
                logger.debug(f"Result received: {result}")
            
            # Display success message and results
            st.success("Crew kicked off successfully!")
            
            # Display Raw Output
            with st.expander("Raw Output"):
                # Assuming 'raw' is a string
                st.text(result.raw)
            
            # Parse professors and labs
            professors = parse_professors(result.raw)
            labs = parse_labs(result.raw)
            
            # Display professors and labs
            display_professors(professors)
            display_labs(labs)
            
            # Display tasks output
            tasks_output = result.tasks_output
            display_tasks(tasks_output)
            
            # Display Token Usage
            if hasattr(result, 'token_usage') and result.token_usage:
                st.subheader("Token Usage")
                st.json({
                    "Total Tokens": result.token_usage.total_tokens,
                    "Prompt Tokens": result.token_usage.prompt_tokens,
                    "Completion Tokens": result.token_usage.completion_tokens,
                    "Cached Prompt Tokens": result.token_usage.cached_prompt_tokens,
                    "Successful Requests": result.token_usage.successful_requests
                })
        
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
