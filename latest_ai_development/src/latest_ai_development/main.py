#!/usr/bin/env python
import sys
import warnings

from latest_ai_development.crew import LatestAiDevelopment

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'robotics, AI Agent',
        'university': 'UT Austin',
        'resume': 'Experience in Python, ML, Basic Robotics club, etc.',
    }
    LatestAiDevelopment().crew().kickoff(inputs=inputs)

