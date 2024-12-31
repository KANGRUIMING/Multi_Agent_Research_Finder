#!/usr/bin/env python
import sys
import warnings

from latest_ai_development.crew import LatestAiDevelopment

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew with user-provided input.
    """
    # Prompt the user for input at runtime
    topic = input("Enter the topic: ")
    university = input("Enter your university: ")
    resume = input("Enter your resume: ")

    # Create the inputs dictionary from user input
    inputs = {
        'topic': topic,
        'university': university,
        'resume': resume,
    }
    
    # Kick off your AI dev crew with these inputs
    LatestAiDevelopment().crew().kickoff(inputs=inputs)



if __name__ == '__main__':
    run()
