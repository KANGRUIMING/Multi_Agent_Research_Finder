import streamlit as st
import warnings

from latest_ai_development.crew import LatestAiDevelopment


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def main():
    st.title("Latest AI Development Web App")

    # Ask for user inputs via Streamlit UI
    topic = st.text_input("Enter the topic")
    university = st.text_input("Enter your university")
    resume = st.text_area("Enter your resume")

    # When the user clicks the "Submit" button
    if st.button("Submit"):
        # Construct the inputs dictionary
        inputs = {
            'topic': topic,
            'university': university,
            'resume': resume,
        }

        # Kick off your AI dev crew
        try:
            # If your code returns a result, you can capture it here
            result = LatestAiDevelopment().crew().kickoff(inputs=inputs)

            # Display the success message to user
            st.success("Crew kicked off successfully!")
            
            # If you want to show some results from the crew
            st.write("## Output")
            st.write(result)

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
